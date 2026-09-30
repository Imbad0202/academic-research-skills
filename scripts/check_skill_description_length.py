"""Enforce the Agent Skills description limit on parsed Unicode text (#864).

Count Python len(description), not source bytes, and never trim or normalize
before counting. Preserve the newline before the closing frontmatter fence:
it participates in YAML block-scalar chomping.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

SKILLS = ("deep-research", "academic-paper", "academic-paper-reviewer", "academic-pipeline")
MAX_LENGTH = 1024


def check(root: Path) -> tuple[dict[str, int], list[str]]:
    counts = {}
    errors = []
    for skill in SKILLS:
        path = root / skill / "SKILL.md"
        try:
            lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
            if not lines or lines[0].strip() != "---":
                raise ValueError("missing opening frontmatter fence")
            end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
            if end is None:
                raise ValueError("missing closing frontmatter fence")
            frontmatter = yaml.safe_load("".join(lines[1:end]))
            if not isinstance(frontmatter, dict):
                raise ValueError("frontmatter must be a mapping")
        except (OSError, ValueError, yaml.YAMLError) as exc:
            errors.append(f"{skill}/SKILL.md: {exc}")
            continue
        description = (frontmatter or {}).get("description")
        if not isinstance(description, str):
            errors.append(f"{skill}/SKILL.md: description must be a string")
            continue
        counts[skill] = len(description)
        if not description.strip():
            errors.append(f"{skill}/SKILL.md: description must not be blank")
        if len(description) > MAX_LENGTH:
            errors.append(f"{skill}/SKILL.md: description exceeds {MAX_LENGTH} code points")
    return counts, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    counts, errors = check(args.repo_root)
    for skill in SKILLS:
        length = counts.get(skill)
        print(f"{skill}: {length if length is not None else 'INVALID'}/{MAX_LENGTH} code points")
    for error in errors:
        print(f"ERROR: {error}")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
