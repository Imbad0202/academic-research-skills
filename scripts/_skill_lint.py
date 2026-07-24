"""Shared helpers for SKILL.md frontmatter linting + cross-lint H2-section
literal checks.

Frontmatter helpers (check_data_access_level.py, check_task_type.py)
validate that every top-level SKILL.md declares a required metadata field
drawn from a closed vocabulary.

`h2_section_body` / `check_section_literals` are the H2 line-walk variant
shared by the block-scoped string-check lints (check_394, check_390): the
"named H2 must exist and carry every load-bearing literal" pattern. This is
ONE of several section extractors in scripts/ — the heading-level / regex /
fence-aware variants (check_392, check_216, check_firm_rules_sync) are
deliberately not interchangeable with this plain line-walk and are not
consolidated here.

`norm_ws` / `read_or_exit2` are the verbatim-witness-lint pair
(check_reviewer_data_fences, check_reviewer_finding_contract): whitespace
folding is load-bearing for "verbatim match modulo wrapping" pins, so it must
be single-sourced rather than re-implemented per lint. (Older lints with
private `_norm` copies — check_instruction_data_boundary,
check_firm_rules_sync — predate this helper; migrating them is a follow-up.)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

SKIP_DIRS = frozenset(
    {"shared", "scripts", "docs", ".git", ".github", "examples", ".local-plans", ".claude"}
)


class FrontmatterError(Exception):
    """Raised when SKILL.md frontmatter cannot be parsed.

    Distinct from a missing fence (returns None) and an empty fence
    (returns {}). Callers should catch this and surface the path +
    parser detail on stdout, not stderr — CI logs commonly capture
    only stdout.
    """


def iter_skill_files(root: Path) -> list[Path]:
    """Top-level SKILL.md files only. Skips SKIP_DIRS."""
    results: list[Path] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name in SKIP_DIRS:
            continue
        skill_md = child / "SKILL.md"
        if skill_md.is_file():
            results.append(skill_md)
    return results


def parse_frontmatter(path: Path) -> dict | None:
    """Parse the YAML frontmatter of a SKILL.md.

    Three outcomes:
      - dict (possibly empty) — fence present and parseable
      - None                  — no opening '---' fence
      - raises FrontmatterError — fence present but YAML invalid
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    match = re.match(r"\A---\r?\n(?P<fm>.*?)(?:\r?\n)---(?:\r?\n|$)", text, re.DOTALL)
    if not match:
        raise FrontmatterError(f"{path}: missing closing YAML frontmatter fence")
    fm = match.group("fm")
    try:
        data = yaml.safe_load(fm) or {}
    except yaml.YAMLError as exc:
        raise FrontmatterError(f"{path}: malformed YAML frontmatter: {exc}") from exc
    if not isinstance(data, dict):
        raise FrontmatterError(
            f"{path}: YAML frontmatter must be a mapping/object, got {type(data).__name__}"
        )
    return data


def split_frontmatter(text: str) -> tuple[dict | None, str]:
    """Split YAML frontmatter from body. Lenient variant of parse_frontmatter.

    Unlike parse_frontmatter, callers here need access to the body and
    prefer "no frontmatter" to an exception when YAML is malformed (the
    caller's surrounding check will surface the structural error). Both
    invalid-fence and invalid-YAML return (None, text) rather than raising.
    """
    if not text.startswith("---"):
        return None, text
    match = re.match(r"\A---\r?\n(?P<fm>.*?)(?:\r?\n)---(?:\r?\n|$)", text, re.DOTALL)
    if not match:
        return None, text
    try:
        data = yaml.safe_load(match.group("fm")) or {}
    except yaml.YAMLError:
        return None, text
    if not isinstance(data, dict):
        return None, text
    return data, text[match.end():]


def check_metadata_field(
    root: Path,
    field: str,
    legal_values: set[str] | frozenset[str],
) -> list[str]:
    """Return a list of human-readable violation messages, empty if all pass."""
    violations: list[str] = []
    skills = iter_skill_files(root)
    if not skills:
        violations.append(f"no SKILL.md files found under {root}")
        return violations
    for path in skills:
        try:
            fm = parse_frontmatter(path)
        except FrontmatterError as exc:
            violations.append(str(exc))
            continue
        if fm is None:
            violations.append(f"{path}: missing YAML frontmatter")
            continue
        metadata = fm.get("metadata") or {}
        if field not in metadata:
            violations.append(f"{path}: metadata.{field} is missing")
            continue
        value = metadata[field]
        if value not in legal_values:
            violations.append(
                f"{path}: metadata.{field} = {value!r}, "
                f"must be one of {sorted(legal_values)}"
            )
    return violations


def h2_section_body(text: str, heading: str) -> str | None:
    """Return the BODY of the H2 starting with `heading` (heading line
    excluded) up to the next H2, or None when the heading is absent. The
    section boundary is explicit: a line is a boundary iff it starts a new
    H2 (`## `); internal H3s and code fences are part of the body."""
    body: list[str] = []
    in_section = False
    for line in text.splitlines():
        if line.startswith(heading):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            body.append(line)
    return "\n".join(body) if in_section else None


def check_section_literals(invariant: int, text: str, heading: str,
                           label: str,
                           literals: dict[str, str]) -> list[str]:
    """The named H2 section must exist and carry every load-bearing literal.
    Shared by the block-scoped string-check lints (check_394, check_390)."""
    section = h2_section_body(text, heading)
    if section is None:
        return [f"invariant {invariant}: {label} section '{heading}' missing"]
    return [
        f"invariant {invariant}: {label} section lost the "
        f"{name} literal ({literal!r})"
        for name, literal in literals.items()
        if literal not in section
    ]


def heading_section(text: str, heading: str) -> str | None:
    """Return the body of the section opened by the exact heading line
    (column 0, outside ``` fences), up to the next heading of the SAME or
    HIGHER level outside fences — deeper child headings stay inside the body.
    None if absent. Nestable: pass a parent section's body back in to bind a
    child heading to that parent (delivery-block scoping — a heading matched
    anywhere in the file is NOT the delivered block)."""
    open_level = len(heading) - len(heading.lstrip("#"))
    stop = re.compile(rf"#{{1,{open_level}}} ")
    # Both Markdown fence forms count — a heading "hidden" in a ~~~ block must
    # not read as a real section boundary (CommonMark close: same fence char,
    # run length >= the opening run, at most 3 spaces of indentation).
    fence_re = re.compile(r"[ ]{0,3}(`{3,}|~{3,})")
    # A CLOSING fence is the run alone on its line (CommonMark: no info string
    # on a closer — "~~~not-a-close" does NOT close a ~~~ block — and a
    # 4-space-indented run is content, not a closer).
    fence_close_re = re.compile(r"[ ]{0,3}(`{3,}|~{3,})\s*$")
    fence: str | None = None  # the opening fence run while inside a fenced block
    started = False
    body: list[str] = []
    for line in text.splitlines(keepends=True):
        m = fence_re.match(line)
        if fence is not None:
            mc = fence_close_re.match(line)
            if mc and mc.group(1)[0] == fence[0] and len(mc.group(1)) >= len(fence):
                fence = None
            if started:
                body.append(line)
            continue
        if m:
            fence = m.group(1)
            if started:
                body.append(line)
            continue
        if not started:
            if line.rstrip("\n") == heading:
                started = True
            continue
        if stop.match(line):
            break
        body.append(line)
    return "".join(body) if started else None


def norm_ws(text: str) -> str:
    """Collapse all whitespace runs so line-wrapping does not defeat a
    verbatim-witness compare. Load-bearing for the fence/finding-contract
    pins — hardening added here reaches every importing lint at once."""
    return re.sub(r"\s+", " ", text).strip()


def read_or_exit2(root: Path, rel: str) -> str:
    """Read a required lint surface; a missing file is an invocation error
    (exit 2), never a lint failure (exit 1)."""
    p = root / rel
    if not p.is_file():
        print(f"ERROR: required file missing: {rel}", file=sys.stderr)
        raise SystemExit(2)
    return p.read_text(encoding="utf-8")


def run_lint(field: str, legal_values: set[str] | frozenset[str], ok_message: str) -> int:
    """argparse + check + print + exit-code wrapper used by both check scripts."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    args = parser.parse_args()

    violations = check_metadata_field(args.path, field, legal_values)
    if violations:
        for v in violations:
            print(f"ERROR: {v}")
        print(f"\n{len(violations)} violation(s) found.", file=sys.stderr)
        return 1
    print(ok_message)
    return 0
