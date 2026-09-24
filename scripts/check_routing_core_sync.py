#!/usr/bin/env python3
"""Routing-core sync lint (#892).

The cross-skill routing core (Routing Discipline v3.9.2: Step 0, Steps 1-3,
and the #133 anti-pattern) has to reach a session on every install path.
Claude Code loads the repository's `.claude/CLAUDE.md` only when the session's
working directory is inside the checkout, so the block has one canonical home,
`shared/references/routing_core.md`, and three carriers:

- `.claude/CLAUDE.md` (sessions started inside a clone): a verbatim copy;
- the four `SKILL.md` files (every install path, once a skill loads):
  verbatim copies;
- `scripts/announce-ars-loaded.sh` (plugin SessionStart): reads the canonical
  file at runtime and holds no copy.

Checks:
  RC-1  The canonical file holds exactly one begin marker and one end marker,
        each alone on its line, begin before end, around a non-empty block.
  RC-2  Every copy carrier holds exactly one such marker pair, and its block
        is byte-identical to the canonical block.
  RC-3  The announce script names the canonical path and both markers, which
        is how it finds the block at runtime.

The companion `test_check_routing_core_sync.py` runs the announce script for
every SessionStart source and checks the block reaches the emitted context.

Usage:
    python scripts/check_routing_core_sync.py [--root PATH]

Exit codes: 0 all checks pass; 1 a check failed; 2 a required file is missing.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

CANONICAL = Path("shared/references/routing_core.md")
COPIES = (
    Path(".claude/CLAUDE.md"),
    Path("academic-paper/SKILL.md"),
    Path("academic-paper-reviewer/SKILL.md"),
    Path("deep-research/SKILL.md"),
    Path("academic-pipeline/SKILL.md"),
)
ANNOUNCE = Path("scripts/announce-ars-loaded.sh")
BEGIN = "<!-- routing-core:begin -->"
END = "<!-- routing-core:end -->"


def extract_block(text: str, label: str) -> tuple[str | None, list[str]]:
    """Return the text between the one marker pair, or None with the errors."""
    lines = text.split("\n")
    begins = [i for i, line in enumerate(lines) if line == BEGIN]
    ends = [i for i, line in enumerate(lines) if line == END]
    errors: list[str] = []
    for marker, whole in ((BEGIN, begins), (END, ends)):
        total = text.count(marker)
        if total != 1 or len(whole) != 1:
            errors.append(f"{label}: expected one {marker} alone on its line, "
                          f"found {total} occurrence(s), {len(whole)} on their own line")
    if errors:
        return None, errors
    if begins[0] > ends[0]:
        return None, [f"{label}: {END} comes before {BEGIN}"]
    block = "\n".join(lines[begins[0] + 1:ends[0]])
    if not block.strip():
        return None, [f"{label}: the routing-core block is empty"]
    return block, []


def first_difference(copy: str, canonical: str) -> str:
    copy_lines, canon_lines = copy.split("\n"), canonical.split("\n")
    for number, (got, want) in enumerate(zip(copy_lines, canon_lines), start=1):
        if got != want:
            return f"block line {number} differs"
    return (f"block has {len(copy_lines)} lines, canonical has {len(canon_lines)}")


def check(root: Path) -> list[str]:
    """Run RC-1..RC-3 under `root`; raise FileNotFoundError for a missing file."""
    canonical, errors = extract_block(
        (root / CANONICAL).read_text(encoding="utf-8"), f"RC-1 {CANONICAL}")
    for rel in COPIES:
        block, copy_errors = extract_block(
            (root / rel).read_text(encoding="utf-8"), f"RC-2 {rel}")
        errors += copy_errors
        if block is not None and canonical is not None and block != canonical:
            errors.append(f"RC-2 {rel}: routing-core block differs from {CANONICAL} "
                          f"({first_difference(block, canonical)})")
    script = (root / ANNOUNCE).read_text(encoding="utf-8")
    for needle in (str(CANONICAL), BEGIN, END):
        if needle not in script:
            errors.append(f"RC-3 {ANNOUNCE}: does not name {needle}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    try:
        errors = check(args.root)
    except FileNotFoundError as exc:
        print(f"check_routing_core_sync: missing file: {exc.filename}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"check_routing_core_sync: OK ({len(COPIES)} copies match {CANONICAL}; "
          f"{ANNOUNCE} reads it at runtime)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
