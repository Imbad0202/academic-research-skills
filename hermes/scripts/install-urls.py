#!/usr/bin/env python
"""List direct raw GitHub install URLs for Hermes skills."""
from __future__ import annotations

from pathlib import Path

REPO = "https://raw.githubusercontent.com/maximosovsky/academic-research-skills/hermes-adaptation"
ROOT = Path(__file__).resolve().parents[1]
for skill in sorted((ROOT / "skills").glob("*/SKILL.md")):
    rel = skill.relative_to(ROOT).as_posix()
    name = skill.parent.name
    print(f"hermes skills install {REPO}/hermes/{rel} --name {name}")
