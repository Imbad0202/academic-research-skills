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
from _skill_lint import check_marker_copies  # noqa: E402

CANONICAL = Path("shared/references/per_source_method_weaknesses.md")
SURFACES = (
    Path("deep-research/templates/evidence_assessment_template.md"),
    Path("deep-research/SKILL.md"),
    Path("deep-research/agents/bibliography_agent.md"),
    Path("academic-paper/agents/literature_strategist_agent.md"),
)
BEGIN = "<!-- method-weaknesses:begin -->"
END = "<!-- method-weaknesses:end -->"


def check(root: Path) -> list[str]:
    """Run MW-1 and MW-2 under `root`; a missing file exits 2."""
    _, errors = check_marker_copies(root, CANONICAL, SURFACES, BEGIN, END,
                                    "method-weaknesses", "MW-1", "MW-2")
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
