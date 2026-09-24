#!/usr/bin/env python3
"""Routing-core sync lint (#892).

`shared/references/routing_core.md` holds the cross-skill routing core and
says which files carry it and why. This lint keeps the verbatim copies in
`.claude/CLAUDE.md` and in every top-level `SKILL.md` byte-identical to it.
The SessionStart announce reads the canonical file at runtime;
`test_check_routing_core_sync.py` runs the announce to check the block arrives.

Checks:
  RC-1  The canonical file holds exactly one begin marker and one end marker,
        each alone on its line, begin before end, around a non-empty block.
  RC-2  Every copy holds exactly one such marker pair, and its block is
        byte-identical to the canonical block, line endings included.

Usage:
    python scripts/check_routing_core_sync.py [--root PATH]

Exit codes: 0 all checks pass; 1 a check failed; 2 a required file is missing.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _skill_lint import iter_skill_files, read_or_exit2  # noqa: E402

CANONICAL = Path("shared/references/routing_core.md")
CLAUDE_MD = Path(".claude/CLAUDE.md")
BEGIN = "<!-- routing-core:begin -->"
END = "<!-- routing-core:end -->"


def extract_block(text: str, label: str) -> tuple[str | None, list[str]]:
    """Return the text between the one marker pair, or None with the errors.
    A marker line may end in CR; the block keeps its CRs for the comparison."""
    lines = text.split("\n")
    begins = [i for i, line in enumerate(lines) if line.rstrip("\r") == BEGIN]
    ends = [i for i, line in enumerate(lines) if line.rstrip("\r") == END]
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
            if got.rstrip("\r") == want.rstrip("\r"):
                return f"block line {number} differs only in its line ending"
            return f"block line {number} differs"
    return (f"block has {len(copy_lines)} lines, canonical has {len(canon_lines)}")


def copies(root: Path) -> list[Path]:
    """`.claude/CLAUDE.md` and every top-level SKILL.md, relative to `root`."""
    return [CLAUDE_MD, *(path.relative_to(root) for path in iter_skill_files(root))]


def check(root: Path) -> list[str]:
    """Run RC-1 and RC-2 under `root`; a missing file exits 2."""
    canonical, errors = extract_block(read_or_exit2(root, str(CANONICAL), exact=True),
                                      f"RC-1 {CANONICAL}")
    for rel in copies(root):
        block, copy_errors = extract_block(read_or_exit2(root, str(rel), exact=True), f"RC-2 {rel}")
        errors += copy_errors
        if block is not None and canonical is not None and block != canonical:
            errors.append(f"RC-2 {rel}: routing-core block differs from {CANONICAL} "
                          f"({first_difference(block, canonical)})")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    errors = check(args.root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"check_routing_core_sync: OK ({len(copies(args.root))} copies match {CANONICAL})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
