#!/usr/bin/env python3
"""Per-source method-weaknesses sync lint (#916).

`shared/references/per_source_method_weaknesses.md` holds the canonical
method-weakness rules for reading outputs and lists the surfaces that carry
them. This lint keeps each surface's verbatim copy byte-identical to it.

Checks:
  MW-1  The canonical file holds exactly one begin marker and one end marker,
        each alone on its line, begin before end, around a non-empty block.
  MW-2  Every surface holds exactly one such marker pair, and its block is
        byte-identical to the canonical block, line endings included.

Usage:
    python scripts/check_method_weaknesses_sync.py [--root PATH]

Exit codes: 0 all checks pass; 1 a check failed; 2 a required file is missing.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _skill_lint import read_or_exit2  # noqa: E402
from check_routing_core_sync import first_difference  # noqa: E402

CANONICAL = Path("shared/references/per_source_method_weaknesses.md")
SURFACES = (
    Path("deep-research/templates/evidence_assessment_template.md"),
    Path("deep-research/SKILL.md"),
    Path("deep-research/agents/bibliography_agent.md"),
    Path("academic-paper/agents/literature_strategist_agent.md"),
)
BEGIN = "<!-- method-weaknesses:begin -->"
END = "<!-- method-weaknesses:end -->"


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
        return None, [f"{label}: the method-weaknesses block is empty"]
    return block, []


def check(root: Path) -> list[str]:
    """Run MW-1 and MW-2 under `root`; a missing file exits 2."""
    canonical, errors = extract_block(read_or_exit2(root, str(CANONICAL), exact=True),
                                      f"MW-1 {CANONICAL}")
    for rel in SURFACES:
        block, copy_errors = extract_block(read_or_exit2(root, str(rel), exact=True), f"MW-2 {rel}")
        errors += copy_errors
        if block is not None and canonical is not None and block != canonical:
            errors.append(f"MW-2 {rel}: method-weaknesses block differs from {CANONICAL} "
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
    print(f"check_method_weaknesses_sync: OK ({len(SURFACES)} surfaces match {CANONICAL})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
