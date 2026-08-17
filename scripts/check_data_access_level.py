#!/usr/bin/env python3
"""Lint: every top-level SKILL.md declares the PINNED data_access_level.

Single pass per skill, one violation per problem: frontmatter must parse,
the skill must be registered in EXPECTED_LEVELS, and the declared value
must equal its pin. The governing rule (`ground_truth_isolation_pattern.md`
§ "Declare `data_access_level` truthfully") requires the annotation to
reflect the DIRTIEST input the skill may legitimately consume across all
its modes.

Pin provenance is not uniform (honest-claim discipline): the
`academic-pipeline: raw` pin is #756-derived (Stage 1 accepts raw user
requests, mid-entry accepts raw papers; the gates run inside the pipeline).
The other three pins freeze the pre-existing declarations against silent
drift — they have not been re-derived under the dirtiest-input rule.
Changing any pin must be a deliberate, reviewed re-application of the rule,
and a new top-level skill must be registered here before it passes.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _skill_lint import (
    FrontmatterError,
    iter_skill_files,
    parse_frontmatter,
)

LEGAL_VALUES = frozenset({"raw", "redacted", "verified_only"})

# Dirtiest-input pins (#756). Keyed by skill directory name.
EXPECTED_LEVELS = {
    "academic-paper": "redacted",
    "academic-paper-reviewer": "verified_only",
    "academic-pipeline": "raw",
    "deep-research": "raw",
}

# The pins themselves must stay inside the closed vocabulary.
assert set(EXPECTED_LEVELS.values()) <= LEGAL_VALUES


def run_all_checks(root: Path) -> list[str]:
    violations: list[str] = []
    seen: set[str] = set()
    for skill_md in iter_skill_files(root):
        name = skill_md.parent.name
        seen.add(name)
        try:
            fm = parse_frontmatter(skill_md)
        except FrontmatterError as exc:
            violations.append(str(exc))  # message already carries the path
            continue
        if fm is None:
            violations.append(f"{skill_md}: missing YAML frontmatter")
            continue
        if name not in EXPECTED_LEVELS:
            violations.append(
                f"{skill_md}: skill '{name}' is not registered in "
                f"EXPECTED_LEVELS — apply the dirtiest-input rule and pin "
                f"its level here"
            )
            continue
        metadata = fm.get("metadata")
        if not isinstance(metadata, dict):
            violations.append(
                f"{skill_md}: metadata must be a mapping/object, got "
                f"{type(metadata).__name__}"
            )
            continue
        declared = metadata.get("data_access_level")
        if declared != EXPECTED_LEVELS[name]:
            violations.append(
                f"{skill_md}: data_access_level is {declared!r}, pinned "
                f"value is {EXPECTED_LEVELS[name]!r} (change the pin "
                f"deliberately or fix the declaration)"
            )
    for name in sorted(set(EXPECTED_LEVELS) - seen):
        violations.append(
            f"EXPECTED_LEVELS pins '{name}' but no top-level "
            f"{name}/SKILL.md exists"
        )
    return violations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    args = parser.parse_args()
    violations = run_all_checks(args.path)
    if violations:
        for v in violations:
            print(f"ERROR: {v}")
        print(f"\n{len(violations)} violation(s) found.", file=sys.stderr)
        return 1
    print(
        "OK: all SKILL.md files declare a valid, pinned data_access_level."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
