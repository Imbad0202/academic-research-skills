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


# Broad token captures: anything that looks like an identifier inside the
# expected position. The strict validator below then decides whether the raw
# token is a canonical semver. Using the regex as a filter (the pre-#169
# pattern) silently dropped invalid tokens and hid the very drift this lint
# is meant to surface; see dual-track review on PR for that class of bug.
TABLE_TOKEN_RE = re.compile(
    r"^\|\s*`([a-z0-9-]+)`\s+v([A-Za-z0-9.\-_+]+)\s*\|", re.MULTILINE
)
SUITE_TOKEN_RE = re.compile(
    r"^\s*-\s*\*\*Suite version\*\*:\s*([A-Za-z0-9.\-_+]+)", re.MULTILINE
)
CHANGELOG_TOKEN_RE = re.compile(r"^##\s*\[([A-Za-z0-9.\-_+]+)\]", re.MULTILINE)
SEMVER_STRICT_RE = re.compile(r"^\d+(?:\.\d+){2,}$")  # 3 or more segments

NON_VERSION_CHANGELOG_TOKENS = frozenset({"Unreleased"})

PIPELINE_SKILL_NAME = "academic-pipeline"


def _is_strict_semver(token: str) -> bool:
    return bool(SEMVER_STRICT_RE.match(token))


def _parse_table_versions(
    claude_md_text: str,
) -> tuple[dict[str, str], list[tuple[str, str]]]:
    """Return (valid_versions, invalid_rows) from the Skills Overview table.

    `valid_versions` maps skill_name -> version for rows whose v-token is a
    canonical N.N.N(.N)+ string. `invalid_rows` collects (skill_name, raw_token)
    for rows where the v-token is present but not a canonical version; the
    caller surfaces these as errors so a malformed table row does not silently
    drop out of downstream invariants.
    """
    valid: dict[str, str] = {}
    invalid: list[tuple[str, str]] = []
    for skill, raw in TABLE_TOKEN_RE.findall(claude_md_text):
        if _is_strict_semver(raw):
            valid[skill] = raw
        else:
            invalid.append((skill, raw))
    return valid, invalid


def _parse_suite_version(claude_md_text: str) -> tuple[str | None, str | None]:
    """Return (valid_version, invalid_raw_token).

    Exactly one of the two is non-None when a Suite version line is present.
    Both are None when the line is missing entirely.
    """
    m = SUITE_TOKEN_RE.search(claude_md_text)
    if m is None:
        return None, None
    raw = m.group(1)
    if _is_strict_semver(raw):
        return raw, None
    return None, raw


def _parse_changelog_latest(
    changelog_text: str,
) -> tuple[str | None, str | None]:
    """Return (valid_latest, invalid_raw_token).

    Walks `## [TOKEN]` headings in document order, skipping pseudo-entries
    like `[Unreleased]`. The first remaining heading is the latest release.
    If that heading's token is not a canonical version, it is returned as
    `invalid_raw_token` so the caller flags it instead of silently falling
    through to a predecessor and hiding the malformed release entry.
    """
    for m in CHANGELOG_TOKEN_RE.finditer(changelog_text):
        raw = m.group(1)
        if raw in NON_VERSION_CHANGELOG_TOKENS:
            continue
        if _is_strict_semver(raw):
            return raw, None
        return None, raw
    return None, None


def check(root: Path) -> list[str]:
    errors: list[str] = []

    claude_md = root / ".claude" / "CLAUDE.md"
    if not claude_md.is_file():
        errors.append(f"{claude_md}: not found")
        return errors
    claude_text = claude_md.read_text(encoding="utf-8")

    table_versions, invalid_table_rows = _parse_table_versions(claude_text)
    if not table_versions and not invalid_table_rows:
        errors.append(
            f"{claude_md}: Skills Overview table has no parseable "
            "`<skill>` vX.Y.Z rows"
        )
    for skill, raw in invalid_table_rows:
        errors.append(
            f"{claude_md}: table row {skill!r} has invalid version "
            f"token v{raw!r} (expected canonical N.N.N or N.N.N.N)"
        )

    suite_version, invalid_suite_token = _parse_suite_version(claude_text)
    if suite_version is None and invalid_suite_token is None:
        errors.append(
            f"{claude_md}: missing '**Suite version**: X.Y.Z' line"
        )
    elif invalid_suite_token is not None:
        errors.append(
            f"{claude_md}: Suite version token {invalid_suite_token!r} is "
            "not a canonical N.N.N or N.N.N.N version"
        )

    changelog = root / "CHANGELOG.md"
    if not changelog.is_file():
        errors.append(f"{changelog}: not found")
    else:
        latest, invalid_latest = _parse_changelog_latest(
            changelog.read_text(encoding="utf-8")
        )
        if latest is None and invalid_latest is None:
            errors.append(f"{changelog}: no '## [X.Y.Z]' entry found")
        elif invalid_latest is not None:
            errors.append(
                f"{changelog}: latest entry token {invalid_latest!r} is "
                "not a canonical N.N.N or N.N.N.N version"
            )
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
