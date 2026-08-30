#!/usr/bin/env python3
"""Lint: the skill inventory is identical on every surface that lists it (#809).

Triage of an external PR that added a fifth top-level skill directory showed
that the existing inventory lints are anchored to the skills they already
know about: `check_spec_consistency.py` hardcodes four SKILL.md paths,
`check_version_consistency.py` iterates the `.claude/CLAUDE.md` table, and
nothing cross-checks the `skills/` symlink directory or the marketplace
manifest. A skill could therefore exist on disk without being packaged,
listed, or versioned, with every lint green.

This lint takes the set of top-level `<name>/SKILL.md` directories as the
authority (it is what exists) and requires set-equality against the three
surfaces that advertise or package the inventory:

  B. `skills/<name>` — one symlink per skill, resolving to `<root>/<name>`
     (plugin auto-discovery packages from here);
  C. `.claude/CLAUDE.md` § "Skills Overview" table rows (the canonical
     inventory other lints iterate);
  D. `.claude-plugin/marketplace.json` `plugins[].skills[]` as `./<name>`
     (what symlink-blind importers read).

It also checks that any "<N> skills" count claim in the plugin / marketplace
descriptions equals the number of skills on disk. A description that carries
no count makes no claim and is not checked.

Every asymmetric difference is reported in both directions, so a stale row
and an unpackaged directory are both single, named violations.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from _skill_lint import iter_skill_files

SKILLS_DIR = "skills"
CLAUDE_MD = Path(".claude") / "CLAUDE.md"
MARKETPLACE_JSON = Path(".claude-plugin") / "marketplace.json"
PLUGIN_JSON = Path(".claude-plugin") / "plugin.json"

SKILLS_OVERVIEW_HEADING = "## Skills Overview"
# A table row whose first cell is a backticked skill name. Anchored per line.
TABLE_ROW_RE = re.compile(r"^\|\s*`([a-z0-9-]+)`", re.MULTILINE)
# Marketplace skill paths are relative, `./<name>`, one segment.
MANIFEST_SKILL_RE = re.compile(r"^\./([a-z0-9-]+)$")
# A count claim such as "4 skills" (word-bounded so "40 skillsets" is not one).
COUNT_CLAIM_RE = re.compile(r"\b(\d+) skills\b")


def _skills_on_disk(root: Path) -> set[str]:
    return {p.parent.name for p in iter_skill_files(root)}


def _skills_dir_entries(root: Path, violations: list[str]) -> set[str]:
    skills_dir = root / SKILLS_DIR
    if not skills_dir.is_dir():
        violations.append(f"{skills_dir}: directory is missing")
        return set()
    names: set[str] = set()
    for entry in sorted(skills_dir.iterdir(), key=lambda p: p.name):
        names.add(entry.name)
        expected = root / entry.name
        if not entry.is_symlink():
            violations.append(
                f"{entry}: must be a symlink to ../{entry.name}, "
                f"found a real {'directory' if entry.is_dir() else 'file'}"
            )
            continue
        try:
            target = entry.resolve(strict=True)
        except (FileNotFoundError, RuntimeError):
            violations.append(f"{entry}: dangling symlink")
            continue
        if target != expected.resolve():
            violations.append(
                f"{entry}: symlink resolves to {target}, expected {expected}"
            )
    return names


def _claude_table_rows(root: Path, violations: list[str]) -> set[str]:
    claude_md = root / CLAUDE_MD
    if not claude_md.is_file():
        violations.append(f"{claude_md}: file is missing")
        return set()
    text = claude_md.read_text(encoding="utf-8")
    start = text.find(SKILLS_OVERVIEW_HEADING)
    if start < 0:
        violations.append(
            f"{claude_md}: '{SKILLS_OVERVIEW_HEADING}' section is missing"
        )
        return set()
    body = text[start + len(SKILLS_OVERVIEW_HEADING):]
    next_heading = re.search(r"^## ", body, re.MULTILINE)
    section = body[: next_heading.start()] if next_heading else body
    rows = set(TABLE_ROW_RE.findall(section))
    if not rows:
        violations.append(
            f"{claude_md}: '{SKILLS_OVERVIEW_HEADING}' table has no "
            f"backticked skill rows"
        )
    return rows


def _load_json(path: Path, violations: list[str]) -> dict | None:
    if not path.is_file():
        violations.append(f"{path}: file is missing")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        violations.append(f"{path}: invalid JSON ({exc.msg} at line {exc.lineno})")
        return None
    if not isinstance(data, dict):
        violations.append(f"{path}: top level must be an object")
        return None
    return data


def _marketplace_skills(
    root: Path, violations: list[str]
) -> tuple[set[str], list[str]]:
    """Return (skill names across all plugins, plugin descriptions)."""
    path = root / MARKETPLACE_JSON
    data = _load_json(path, violations)
    if data is None:
        return set(), []
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        violations.append(f"{path}: 'plugins' must be a non-empty list")
        return set(), []
    names: set[str] = set()
    descriptions: list[str] = []
    for index, plugin in enumerate(plugins):
        if not isinstance(plugin, dict):
            violations.append(f"{path}: plugins[{index}] must be an object")
            continue
        description = plugin.get("description")
        if isinstance(description, str):
            descriptions.append(description)
        skills = plugin.get("skills")
        if not isinstance(skills, list):
            violations.append(
                f"{path}: plugins[{index}].skills must be a list of './<name>' "
                f"paths (symlink-blind importers read this list)"
            )
            continue
        for raw in skills:
            match = MANIFEST_SKILL_RE.match(raw) if isinstance(raw, str) else None
            if match is None:
                violations.append(
                    f"{path}: plugins[{index}].skills entry {raw!r} must be "
                    f"'./<name>' with a single lowercase path segment"
                )
                continue
            names.add(match.group(1))
    return names, descriptions


def _check_count_claims(
    label: str, descriptions: list[str], expected: int, violations: list[str]
) -> None:
    for description in descriptions:
        for claimed in COUNT_CLAIM_RE.findall(description):
            if int(claimed) != expected:
                violations.append(
                    f"{label}: description claims '{claimed} skills' but "
                    f"{expected} top-level skill directories exist"
                )


def _report_set_diff(
    on_disk: set[str], other: set[str], surface: str, violations: list[str]
) -> None:
    for name in sorted(on_disk - other):
        violations.append(
            f"skill '{name}' exists on disk (top-level {name}/SKILL.md) but "
            f"is not listed in {surface}"
        )
    for name in sorted(other - on_disk):
        violations.append(
            f"{surface} lists skill '{name}' but no top-level {name}/SKILL.md "
            f"exists"
        )


def run_all_checks(root: Path) -> list[str]:
    violations: list[str] = []
    on_disk = _skills_on_disk(root)
    if not on_disk:
        violations.append(
            f"{root}: no top-level <name>/SKILL.md found (wrong --path?)"
        )
        return violations

    symlinked = _skills_dir_entries(root, violations)
    _report_set_diff(on_disk, symlinked, f"{SKILLS_DIR}/ symlinks", violations)

    table = _claude_table_rows(root, violations)
    _report_set_diff(
        on_disk, table, f"{CLAUDE_MD} Skills Overview table", violations
    )

    manifest, market_descriptions = _marketplace_skills(root, violations)
    _report_set_diff(
        on_disk, manifest, f"{MARKETPLACE_JSON} plugins[].skills", violations
    )
    _check_count_claims(
        str(MARKETPLACE_JSON), market_descriptions, len(on_disk), violations
    )

    plugin = _load_json(root / PLUGIN_JSON, violations)
    if plugin is not None:
        description = plugin.get("description")
        if isinstance(description, str):
            _check_count_claims(
                str(PLUGIN_JSON), [description], len(on_disk), violations
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
        "OK: skill inventory is identical across top-level directories, "
        "skills/ symlinks, the CLAUDE.md table, and the marketplace manifest."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
