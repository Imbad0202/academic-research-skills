#!/usr/bin/env python3
"""Lint: every top-level SKILL.md must declare metadata.data_access_level.

Legal values: raw | redacted | verified_only.

Beyond vocabulary, the per-skill VALUES are pinned (#756): the governing
rule (`shared/ground_truth_isolation_pattern.md` § DO: Declare
`data_access_level` truthfully) requires the annotation to reflect the
DIRTIEST input the skill may legitimately consume across all its modes.
`academic-pipeline` is `raw` — the orchestrator's Stage 1 accepts raw user
requests and mid-entry accepts raw existing papers; the upstream integrity
gates run INSIDE the pipeline, so nothing has verified its input before it
runs. Changing a pin here must be a deliberate, reviewed decision that
re-applies the dirtiest-input rule — not a drive-by edit. A new top-level
skill must be registered here before it passes.
"""
from __future__ import annotations

import sys
from pathlib import Path

from _skill_lint import (
    FrontmatterError,
    check_metadata_field,
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


def check_expected_levels(root: Path) -> list[str]:
    """Every skill's declared level equals its pin; every pin has a skill."""
    violations: list[str] = []
    seen: set[str] = set()
    for skill_md in iter_skill_files(root):
        name = skill_md.parent.name
        seen.add(name)
        try:
            meta = (parse_frontmatter(skill_md) or {}).get("metadata") or {}
        except FrontmatterError as exc:
            violations.append(f"{skill_md}: frontmatter parse error: {exc}")
            continue
        declared = meta.get("data_access_level")
        if name not in EXPECTED_LEVELS:
            violations.append(
                f"{skill_md}: skill '{name}' is not registered in "
                f"EXPECTED_LEVELS — apply the dirtiest-input rule and pin "
                f"its level here"
            )
            continue
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


def run_all_checks(root: Path) -> list[str]:
    violations = list(
        check_metadata_field(root, "data_access_level", LEGAL_VALUES)
    )
    violations.extend(check_expected_levels(root))
    return violations


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    violations = run_all_checks(root)
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
