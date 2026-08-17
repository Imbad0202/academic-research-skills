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

The markdown-stripping semantics intentionally match
scripts/check_control_availability.py (#757); consolidating the shared
helpers into one module is follow-up work once both lints are on main.

Exit 0 when all invariants hold; exit 1 with one line per violation.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

DOC_RELPATH = Path("docs/DATA_FLOWS.md")
INBOUND_LINK_SURFACES = (
    Path("README.md"),
    Path("SECURITY.md"),
    Path("THIRD_PARTY.md"),
)

# Direct network capability at the Python level. urllib.parse is NOT here on
# purpose: URL string manipulation is not a network call.
NETWORK_MODULES = {
    "urllib.request",
    "http.client",
    "socket",
    "ssl",
    "ftplib",
    "smtplib",
    "requests",
    "httpx",
    "aiohttp",
}

_LINK_RE = re.compile(r"\[[^\]]*\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_QUOTE_PREFIX_RE = re.compile(r"^(\s{0,3}>\s?)+")
_CURL_RE = re.compile(r"(?:^|[|&;(\s])curl\s")


def _strip_fenced_code(md_text: str) -> str:
    """Fenced code renders literally. CommonMark closing rule: a closer is a
    same-character run at least as long as the opener with only trailing
    whitespace."""
    kept: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    for line in md_text.split("\n"):
        content = _QUOTE_PREFIX_RE.sub("", line).lstrip(" ")
        if not in_fence:
            opener = re.match(r"(`{3,}|~{3,})", content)
            if opener:
                in_fence = True
                fence_char = opener.group(1)[0]
                fence_len = len(opener.group(1))
                continue
        else:
            closer = re.match(
                rf"({re.escape(fence_char)}{{{fence_len},}})\s*$", content
            )
            if closer:
                in_fence = False
            continue
        kept.append(line)
    return "\n".join(kept)


def _strip_html_comments(md_text: str) -> str:
    """A line beginning with `<!--` (looking through block-quote markers)
    opens a GFM type-2 HTML block through the `-->` line or to EOF; inline
    `<!-- -->` spans elsewhere are raw HTML."""
    kept: list[str] = []
    lines = md_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        content = _QUOTE_PREFIX_RE.sub("", line)
        stripped = content.lstrip(" ")
        indent = len(content) - len(stripped)
        if indent <= 3 and stripped.startswith("<!--"):
            while i < len(lines) and "-->" not in lines[i]:
                i += 1
            i += 1
            continue
        kept.append(line)
        i += 1
    return _HTML_COMMENT_RE.sub("", "\n".join(kept))


def _strip_non_rendering(md_text: str) -> str:
    return _strip_html_comments(_strip_fenced_code(md_text))


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


def _python_network_scripts(root: Path) -> list[Path]:
    hits: list[Path] = []
    for py in sorted((root / "scripts").glob("*.py")):
        if py.name.startswith("test_"):
            continue
        modules = _imported_modules(py.read_text(encoding="utf-8"))
        if any(
            m == net or m.startswith(net + ".")
            for m in modules
            for net in NETWORK_MODULES
        ):
            hits.append(py)
    return hits


def _curl_shell_scripts(root: Path) -> list[Path]:
    hits: list[Path] = []
    for pattern in ("scripts/*.sh", "hooks/*.sh"):
        for sh in sorted(root.glob(pattern)):
            for line in sh.read_text(encoding="utf-8").split("\n"):
                code = line.split("#", 1)[0]
                if _CURL_RE.search(code):
                    hits.append(sh)
                    break
    return hits


def check_network_coverage(root: Path) -> list[str]:
    """DF-1 + DF-2: every network-capable script is named on the map."""
    errors: list[str] = []
    doc_text = (root / DOC_RELPATH).read_text(encoding="utf-8")
    for path in _python_network_scripts(root):
        if path.name not in doc_text:
            errors.append(
                f"DF-1: {path.relative_to(root)} imports a network module "
                f"but is not named in {DOC_RELPATH} — new or renamed "
                f"network touchpoint missing from the map"
            )
    for path in _curl_shell_scripts(root):
        if path.name not in doc_text:
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
        found = False
        text = _strip_non_rendering(surface.read_text(encoding="utf-8"))
        for match in _LINK_RE.finditer(text):
            target = match.group(1)
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = target.partition("#")[0]
            if path_part and (surface.parent / path_part).resolve() == doc_abs:
                found = True
                break
        if not found:
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
