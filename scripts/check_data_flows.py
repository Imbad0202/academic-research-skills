#!/usr/bin/env python3
"""Defrift lint for docs/DATA_FLOWS.md (#758).

The data-flow map claims to be the exhaustive user-facing inventory of the
network touchpoints and local stores the suite's own scripts create. A claim
of exhaustiveness is exactly the kind that silently rots, so the lint pins
the coverage direction mechanically and deliberately nothing else — row
semantics (payload class, TTL, off switch) stay owned by code review:

  DF-1  Every non-test Python file under scripts/ that IMPORTS a network
        module (AST import scan, so a no-call guard merely naming
        "urllib.request" in a forbidden-list string does not count) must be
        named in docs/DATA_FLOWS.md. A new resolver cannot land without a
        row on the map.
  DF-2  Every shell script under scripts/ or hooks/ that invokes `curl`
        (outside comments) must be named in docs/DATA_FLOWS.md.
  DF-3  README.md, SECURITY.md, and THIRD_PARTY.md each carry a RENDERED
        markdown link whose destination resolves to docs/DATA_FLOWS.md
        (the #758 acceptance criterion, pinned so a refactor cannot orphan
        the map). Non-rendering markdown counts for nothing: fenced code
        (CommonMark fence-length closing rule) and HTML comments (inline
        spans + line/blockquote-level type-2 blocks) are stripped first.

Rendered-link / non-rendering grammar: scripts/_markdown_lint_util.py
(#771 consolidation).

Exit 0 when all invariants hold; exit 1 with one line per violation.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

from _markdown_lint_util import links_to

DOC_RELPATH = Path("docs/DATA_FLOWS.md")
INBOUND_LINK_SURFACES = (
    Path("README.md"),
    Path("SECURITY.md"),
    Path("THIRD_PARTY.md"),
    Path("docs/SETUP.md"),
)

# Direct network capability at the Python level. The vocabulary is the
# network subset of check_indirect_prompt_injection_no_call.py's
# FORBIDDEN_IMPORTS (that lint's full set also bans process/loader modules
# like subprocess/asyncio/importlib, which many scripts here use
# legitimately — importing it wholesale would false-fire). Deliberate
# deviations from the sibling set: bare `urllib` / `http` are replaced by
# the dotted forms below (urllib.parse and http.HTTPStatus are not network
# calls), and `ssl` is excluded (building a TLS context is not a data
# flow).
NETWORK_TOP_LEVEL = {
    "aiohttp",
    "anthropic",
    "boto3",
    "ftplib",
    "grpc",
    "httpx",
    "openai",
    "paramiko",
    "requests",
    "smtplib",
    "socket",
    "telnetlib",
    "urllib3",
    "websocket",
    "websockets",
}
NETWORK_DOTTED = {
    "urllib.request",
    "http.client",
}

_SHELL_QUOTED_RE = re.compile(r"'[^']*'|\"[^\"]*\"")
_ENV_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z_0-9]*=")
# Shell control words that precede a command without consuming its command
# position: `if curl …; then`, `while ! curl …; do`, `exec curl …`.
_SHELL_CONTROL_TOKENS = {
    "if",
    "elif",
    "while",
    "until",
    "then",
    "else",
    "do",
    "!",
    "time",
    "exec",
}


def _invokes_curl(code: str) -> bool:
    """True when curl appears in COMMAND POSITION: the first token of a
    segment (split on pipes/separators/substitution openers) after skipping
    VAR=value assignment prefixes and shell control words, with any path
    prefix allowed (`/usr/bin/curl`). `command -v curl`, `echo curl`, and
    other argument-position mentions do not count. Accepted edges:
    wrapper-prefixed invocations (`sudo curl`, `timeout 3 curl`,
    `xargs curl`) are missed — the surfaces don't write them."""
    for segment in re.split(r"[|;&(`]|\$\(", code):
        head = None
        for token in segment.split():
            if _ENV_ASSIGN_RE.match(token):
                continue  # VAR=value prefix before the command word
            if token in _SHELL_CONTROL_TOKENS:
                continue  # control word — the command follows
            if token.startswith("-"):
                continue  # an option to a control word (`time -p curl …`)
            head = token
            break
        if head is not None and head.rsplit("/", 1)[-1] == "curl":
            return True
    return False


def _imported_modules(py_source: str) -> set[str]:
    """Top-level dotted module names imported anywhere in the file."""
    try:
        tree = ast.parse(py_source)
    except SyntaxError:
        return set()
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module is None or node.level:
                continue  # relative import — repo-internal, not a network module
            modules.add(node.module)
            # `from urllib import request` imports urllib.request without the
            # dotted name appearing as node.module.
            for alias in node.names:
                modules.add(f"{node.module}.{alias.name}")
    return modules


def _is_network_module(module: str) -> bool:
    if module.split(".", 1)[0] in NETWORK_TOP_LEVEL:
        return True
    return any(
        module == net or module.startswith(net + ".")
        for net in NETWORK_DOTTED
    )


def _python_network_scripts(root: Path) -> list[Path]:
    hits: list[Path] = []
    # Recursive on purpose: scripts/verification_gate/,
    # scripts/cross_model_verification/, scripts/adapters/ are exactly where
    # a future resolver call would plausibly land.
    for py in sorted((root / "scripts").rglob("*.py")):
        if py.name.startswith("test_") or "tests" in py.parts:
            continue
        modules = _imported_modules(py.read_text(encoding="utf-8"))
        if any(_is_network_module(m) for m in modules):
            hits.append(py)
    return hits


def _curl_shell_scripts(root: Path) -> list[Path]:
    hits: list[Path] = []
    for base in ("scripts", "hooks"):
        for sh in sorted((root / base).rglob("*.sh")):
            for line in sh.read_text(encoding="utf-8").split("\n"):
                if line.lstrip().startswith("#"):
                    continue  # a full comment line executes nothing
                # Command substitutions execute even inside double quotes:
                # `resp="$(curl ...)"` is a real network call, so scan their
                # bodies FIRST, before quote masking can hide them. (Known
                # accepted edge: a $(curl) inside a trailing inline comment
                # would false-fire; the surfaces don't write that.)
                subs = re.findall(r"\$\(([^)]*)\)", line)
                if any(_invokes_curl(sub) for sub in subs):
                    hits.append(sh)
                    break
                # Then mask quoted spans so `echo "run curl ..."` (quoted
                # instructional text, no curl process) cannot fire, and drop
                # the comment tail.
                code = _SHELL_QUOTED_RE.sub("", line).split("#", 1)[0]
                if _invokes_curl(code):
                    hits.append(sh)
                    break
    return hits


def check_network_coverage(root: Path) -> list[str]:
    """DF-1 + DF-2: every network-capable script is named on the map.

    Naming means the FULL repo-relative path appears in the doc — basename
    matching would let a new `scripts/client.py` ride on the substring
    inside `scripts/semantic_scholar_client.py`.
    """
    errors: list[str] = []
    doc_text = (root / DOC_RELPATH).read_text(encoding="utf-8")
    for path in _python_network_scripts(root):
        if path.relative_to(root).as_posix() not in doc_text:
            errors.append(
                f"DF-1: {path.relative_to(root)} imports a network module "
                f"but is not named in {DOC_RELPATH} — new or renamed "
                f"network touchpoint missing from the map"
            )
    for path in _curl_shell_scripts(root):
        if path.relative_to(root).as_posix() not in doc_text:
            errors.append(
                f"DF-2: {path.relative_to(root)} invokes curl but is not "
                f"named in {DOC_RELPATH}"
            )
    return errors


def check_inbound_links(root: Path) -> list[str]:
    """DF-3: the three surfaces carry a rendered link resolving to the map."""
    errors: list[str] = []
    doc_abs = (root / DOC_RELPATH).resolve()
    for rel in INBOUND_LINK_SURFACES:
        surface = root / rel
        text = surface.read_text(encoding="utf-8")
        if not links_to(text, surface.parent, doc_abs):
            errors.append(
                f"DF-3: {rel} no longer links to {DOC_RELPATH.name} "
                f"(#758 acceptance criterion)"
            )
    return errors


def run_all_checks(root: Path) -> list[str]:
    if not (root / DOC_RELPATH).exists():
        return [f"DF-1: {DOC_RELPATH} is missing"]
    errors: list[str] = []
    errors.extend(check_network_coverage(root))
    errors.extend(check_inbound_links(root))
    return errors


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    errors = run_all_checks(root)
    if errors:
        for line in errors:
            print(f"ERROR: {line}", file=sys.stderr)
        print(f"check_data_flows: {len(errors)} violation(s)", file=sys.stderr)
        return 1
    print("check_data_flows: OK (DF-1..DF-3)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
