#!/usr/bin/env python
"""Validate Hermes SKILL.md files in this repo's hermes/skills tree."""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except Exception as exc:  # pragma: no cover
    print(f"ERROR: PyYAML is required: {exc}", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

errors: list[str] = []

for skill in sorted(SKILLS.glob("*/SKILL.md")):
    text = skill.read_text(encoding="utf-8")
    if not text.startswith("---"):
        errors.append(f"{skill}: must start with YAML frontmatter")
        continue
    end = text.find("\n---\n", 3)
    if end == -1:
        errors.append(f"{skill}: missing closing frontmatter delimiter")
        continue
    try:
        fm = yaml.safe_load(text[3:end])
    except Exception as exc:
        errors.append(f"{skill}: YAML parse error: {exc}")
        continue
    if not isinstance(fm, dict):
        errors.append(f"{skill}: frontmatter is not a mapping")
        continue
    for key in ("name", "description"):
        if not fm.get(key):
            errors.append(f"{skill}: missing {key}")
    name = str(fm.get("name", ""))
    if len(name) > 64 or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
        errors.append(f"{skill}: invalid skill name {name!r}")
    desc = str(fm.get("description", ""))
    if len(desc) > 1024:
        errors.append(f"{skill}: description exceeds 1024 chars")
    if not text[end + 5 :].strip():
        errors.append(f"{skill}: body is empty")
    print(f"OK {name} ({len(desc)} chars description)")

if errors:
    print("\nValidation failed:", file=sys.stderr)
    for err in errors:
        print(f"- {err}", file=sys.stderr)
    sys.exit(1)

print("All Hermes skills valid.")
