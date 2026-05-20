#!/usr/bin/env python3
"""Lint: version labels stay aligned across .claude/CLAUDE.md, SKILL.md frontmatter, and CHANGELOG.md.

Invariants enforced:
  1. Every skill listed in .claude/CLAUDE.md Skills Overview table has a version
     equal to its own SKILL.md metadata.version.
  2. .claude/CLAUDE.md "**Suite version**: X.Y.Z" equals the most recent
     "## [X.Y.Z]" entry in CHANGELOG.md.
  3. academic-pipeline version in the table equals the suite version (pipeline
     = orchestrator, by convention tracks the suite release).

Runs from repo root by default; `--path` lets tests point at a fake tree.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from _skill_lint import parse_frontmatter, FrontmatterError


SEMVER = r"\d+\.\d+\.\d+(?:\.\d+)?"
TABLE_ROW_RE = re.compile(
    rf"^\|\s*`([a-z0-9-]+)`\s+v({SEMVER})(?!\.\d)\s*\|", re.MULTILINE
)
SUITE_VERSION_RE = re.compile(
    rf"^\s*-\s*\*\*Suite version\*\*:\s*({SEMVER})(?!\.\d)", re.MULTILINE
)
CHANGELOG_ENTRY_RE = re.compile(rf"^##\s*\[({SEMVER})\]", re.MULTILINE)  # `]` delimiter blocks 5-segment prefix match without a lookahead

PIPELINE_SKILL_NAME = "academic-pipeline"


def _parse_table_versions(claude_md_text: str) -> dict[str, str]:
    """Return mapping skill_name -> version from the Skills Overview table."""
    return dict(TABLE_ROW_RE.findall(claude_md_text))


def _parse_suite_version(claude_md_text: str) -> str | None:
    m = SUITE_VERSION_RE.search(claude_md_text)
    return m.group(1) if m else None


def _parse_changelog_latest(changelog_text: str) -> str | None:
    m = CHANGELOG_ENTRY_RE.search(changelog_text)
    return m.group(1) if m else None


def check(root: Path) -> list[str]:
    errors: list[str] = []

    claude_md = root / ".claude" / "CLAUDE.md"
    if not claude_md.is_file():
        errors.append(f"{claude_md}: not found")
        return errors
    claude_text = claude_md.read_text(encoding="utf-8")

    table_versions = _parse_table_versions(claude_text)
    if not table_versions:
        errors.append(
            f"{claude_md}: Skills Overview table has no parseable "
            "`<skill>` vX.Y.Z rows"
        )

    suite_version = _parse_suite_version(claude_text)
    if suite_version is None:
        errors.append(
            f"{claude_md}: missing '**Suite version**: X.Y.Z' line"
        )

    changelog = root / "CHANGELOG.md"
    if not changelog.is_file():
        errors.append(f"{changelog}: not found")
    else:
        latest = _parse_changelog_latest(changelog.read_text(encoding="utf-8"))
        if latest is None:
            errors.append(f"{changelog}: no '## [X.Y.Z]' entry found")
        elif suite_version is not None and latest != suite_version:
            errors.append(
                f"{claude_md}: Suite version {suite_version!r} does not match "
                f"CHANGELOG latest entry {latest!r}"
            )

    for skill_name, table_version in sorted(table_versions.items()):
        skill_md = root / skill_name / "SKILL.md"
        if not skill_md.is_file():
            errors.append(
                f"{claude_md}: table lists {skill_name!r} v{table_version} "
                f"but {skill_md} does not exist"
            )
            continue
        try:
            fm = parse_frontmatter(skill_md)
        except FrontmatterError as exc:
            errors.append(str(exc))
            continue
        if fm is None:
            errors.append(f"{skill_md}: missing YAML frontmatter")
            continue
        metadata = fm.get("metadata") or {}
        declared = metadata.get("version")
        if declared is None:
            errors.append(f"{skill_md}: metadata.version is missing")
            continue
        declared_str = str(declared)
        if declared_str != table_version:
            errors.append(
                f"{claude_md}: {skill_name!r} listed as v{table_version} but "
                f"{skill_md} metadata.version is {declared_str!r}"
            )

    if suite_version is not None:
        pipeline_in_table = table_versions.get(PIPELINE_SKILL_NAME)
        if pipeline_in_table is not None and pipeline_in_table != suite_version:
            errors.append(
                f"{claude_md}: {PIPELINE_SKILL_NAME} listed as "
                f"v{pipeline_in_table} but suite version is {suite_version!r} "
                "(pipeline tracks the suite release)"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    args = parser.parse_args()

    errors = check(args.path)
    if errors:
        print("Version consistency check failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Version consistency check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
