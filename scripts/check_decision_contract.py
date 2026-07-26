#!/usr/bin/env python3
"""Pin the four-value decision enum and its per-mode authority.

Threat model: accidental drift. Historical records and design documents are
excluded deliberately; they may truthfully mention retired grammar.

Exit 0 pass / 1 drift / 2 missing input.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _skill_lint import heading_section, norm_ws, read_or_exit2

REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIONS = (
    "editorial_decision=accept",
    "editorial_decision=minor_revision",
    "editorial_decision=major_revision",
    "editorial_decision=reject",
)
VALUES = ("Accept", "Minor Revision", "Major Revision", "Reject")
QUALITY = "academic-paper-reviewer/references/quality_rubrics.md"
STANDARDS = "academic-paper-reviewer/references/editorial_decision_standards.md"
SKILL = "academic-paper-reviewer/SKILL.md"
HANDOFF = "shared/handoff_schemas.md"
SCHEMA = "shared/sprint_contract.schema.json"
PANEL = "scripts/check_panel_synthesis.py"
CONTRACTS = (
    "shared/contracts/reviewer/full.json",
    "shared/contracts/reviewer/methodology_focus.json",
)
LIVE_ROOTS = (
    "academic-paper-reviewer",
    "shared/contracts/reviewer",
)
LIVE_FILES = (
    SCHEMA, HANDOFF, PANEL, "scripts/check_sprint_contract.py",
)


def _read(root: Path, rel: str) -> str:
    return read_or_exit2(root, rel)


def check(root: Path) -> list[str]:
    errors: list[str] = []
    schema = json.loads(_read(root, SCHEMA))
    branch4 = schema["allOf"][3]["then"]["properties"]["failure_conditions"][
        "items"]["properties"]["action"]["enum"]
    if tuple(branch4) != ACTIONS:
        errors.append(f"{SCHEMA}: branch 4 enum drift: {branch4}")

    panel = _read(root, PANEL)
    for action in ACTIONS:
        if panel.count(f'"{action}"') < 1:
            errors.append(f"{PANEL}: ACTION_ENUM missing {action}")

    for rel in CONTRACTS:
        actions = {
            condition["action"]
            for condition in json.loads(_read(root, rel))["failure_conditions"]
        }
        if not actions <= set(ACTIONS) or not set(ACTIONS) <= actions:
            errors.append(f"{rel}: four-action coverage drift: {sorted(actions)}")

    handoff = heading_section(
        _read(root, HANDOFF),
        "## Schema 6: Review Report (academic-paper-reviewer -> pipeline)",
    )
    if handoff is None:
        errors.append(f"{HANDOFF}: Schema 6 section missing")
    else:
        for value in VALUES:
            if value not in handoff:
                errors.append(f"{HANDOFF}: Schema 6 decision enum missing {value}")

    authority = heading_section(_read(root, STANDARDS), "## 0. Decision Authority by Mode")
    if authority is None:
        errors.append(f"{STANDARDS}: §0 authority table missing")
    else:
        for mode in (
            "`full` (sprint contract)", "`methodology-focus` (sprint contract)",
            "`re-review`", "`quick`", "`guided`", "`calibration`",
        ):
            if mode not in authority:
                errors.append(f"{STANDARDS}: authority row missing {mode}")
        if norm_ws("Under a sprint contract, the mechanical synthesizer governs") \
                not in norm_ws(authority):
            errors.append(f"{STANDARDS}: mechanical governor sentence missing")
    if "canonical per-mode decision authority table" not in _read(root, SKILL):
        errors.append(f"{SKILL}: §0 authority pointer missing")

    for rel in LIVE_FILES:
        if "reject_or_major_revision" in _read(root, rel):
            errors.append(f"{rel}: retired hybrid decision token present")
    for live_root in LIVE_ROOTS:
        base = root / live_root
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".json", ".py"}:
                if "reject_or_major_revision" in path.read_text(encoding="utf-8"):
                    errors.append(
                        f"{path.relative_to(root)}: retired hybrid decision token present"
                    )

    thresholds = (">= 80", "65-79", "50-64", "< 50")
    quality = _read(root, QUALITY)
    for threshold in thresholds:
        if quality.count(threshold) != 1:
            errors.append(f"{QUALITY}: threshold residency drift for {threshold}")
    live_paths: set[Path] = set()
    for live_root in LIVE_ROOTS:
        base = root / live_root
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".json", ".py"}:
                live_paths.add(path)
    live_paths.update(root / rel for rel in LIVE_FILES)
    for path in sorted(live_paths):
        rel = str(path.relative_to(root))
        if rel == QUALITY:
            continue
        text = path.read_text(encoding="utf-8")
        for threshold in thresholds:
            if threshold in text:
                errors.append(
                    f"{rel}: decision threshold {threshold} must reside only "
                    f"in {QUALITY}"
                )
    standards = _read(root, STANDARDS)
    for retired in ("4.0", "3.5", "2.5-3.4", "< 2.5", "score = 1", "score = 2"):
        if retired in standards:
            errors.append(f"{STANDARDS}: retired 1-5 threshold residue {retired}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    errors = check(args.root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("check_decision_contract: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
