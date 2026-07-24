#!/usr/bin/env python3
"""Integrity lint for evals/heldout/reviewer_seeded_defects/ (#574 E4 v0.1).

Structure-only fixture gate (the field_norm_severity precedent): it validates
that the ground-truth manifests and manuscripts agree, so a drifted fixture
cannot silently corrupt a baseline/acceptance run. It measures nothing about
reviewer behavior.

Invariants:
  1. Every manifest parses, carries the required top-level keys, and its
     `manuscript` path exists.
  2. `defect_count == len(defects)`.
  3. Every defect row carries all required fields; `class`, `expected_severity`,
     and `expected_detector` come from the closed enums; `defect_id` values are
     unique within a manifest.
  4. Every `anchor_quote` (8-25 words) appears VERBATIM exactly once in its
     manuscript.
  5. The clean control manuscript exists and no manifest points at it.
  6. The manifest set is exactly the expected fixture inventory (a deleted
     manifest cannot silently shrink the acceptance set), and every
     `*_defective.md` manuscript is covered by a manifest.

Run: python3 scripts/check_seeded_defect_fixtures.py
Exit 0 on pass; 1 with per-invariant messages on failure.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ROOT = REPO / "evals" / "heldout" / "reviewer_seeded_defects"
MANIFESTS = ROOT / "manifests"
CLEAN_CONTROL = ROOT / "manuscripts" / "ms00_clean_control.md"

# Expected inventory — update deliberately when fixtures/defects are
# added/retired. Values are the EXACT defect-ID sets: a coordinated
# row-deletion + defect_count decrement (or an SD-* rename that would orphan
# per_defect run records) must fail CI, not shrink the denominator silently.
EXPECTED_DEFECT_IDS = {
    "ms01_quant": {f"SD-{i:02d}" for i in range(1, 11)},
    "ms02_qual": {f"SD-{i:02d}" for i in range(1, 10)},
}
EXPECTED_FIXTURES = set(EXPECTED_DEFECT_IDS)

REQUIRED_TOP = {"fixture_id", "manuscript", "defect_count", "defects"}
REQUIRED_DEFECT = {
    "defect_id",
    "class",
    "expected_severity",
    "section",
    "anchor_quote",
    "description",
    "expected_detector",
}
CLASSES = {
    "statistical",
    "inference",
    "citation_claim_mismatch",
    "methods",
    "ethics",
    "internal_consistency",
    "overclaim",
    "qual_rigor",
}
SEVERITIES = {"critical", "major", "minor"}
DETECTORS = {
    "methodology",
    "statistics",
    "domain",
    "ethics",
    "internal_consistency",
    "any",
}


def check_manifest(path: Path, errors: list[str]) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"inv1 {path.name}: unreadable/invalid JSON ({exc})")
        return

    missing = REQUIRED_TOP - data.keys()
    if missing:
        errors.append(f"inv1 {path.name}: missing top-level keys {sorted(missing)}")
        return

    ms_path = ROOT / data["manuscript"]
    if not ms_path.is_file():
        errors.append(f"inv1 {path.name}: manuscript not found: {data['manuscript']}")
        return
    if ms_path.resolve() == CLEAN_CONTROL.resolve():
        errors.append(f"inv5 {path.name}: manifest points at the clean control")
        return
    text = ms_path.read_text(encoding="utf-8")

    defects = data["defects"]
    if data["defect_count"] != len(defects):
        errors.append(
            f"inv2 {path.name}: defect_count={data['defect_count']} but "
            f"{len(defects)} defect rows"
        )

    seen_ids: set[str] = set()
    for row in defects:
        rid = row.get("defect_id", "<missing id>")
        missing_fields = REQUIRED_DEFECT - row.keys()
        if missing_fields:
            errors.append(f"inv3 {path.name} {rid}: missing {sorted(missing_fields)}")
            continue
        if rid in seen_ids:
            errors.append(f"inv3 {path.name} {rid}: duplicate defect_id")
        seen_ids.add(rid)
        if row["class"] not in CLASSES:
            errors.append(f"inv3 {path.name} {rid}: unknown class {row['class']!r}")
        if row["expected_severity"] not in SEVERITIES:
            errors.append(
                f"inv3 {path.name} {rid}: unknown severity "
                f"{row['expected_severity']!r}"
            )
        if row["expected_detector"] not in DETECTORS:
            errors.append(
                f"inv3 {path.name} {rid}: unknown detector "
                f"{row['expected_detector']!r}"
            )
        anchor = row["anchor_quote"]
        n_words = len(anchor.split())
        if not 8 <= n_words <= 25:
            errors.append(
                f"inv4 {path.name} {rid}: anchor_quote is {n_words} words "
                f"(bound: 8-25)"
            )
        occurrences = text.count(anchor)
        if occurrences != 1:
            errors.append(
                f"inv4 {path.name} {rid}: anchor_quote occurs {occurrences}x "
                f"in {data['manuscript']} (must be exactly 1)"
            )


def main() -> int:
    errors: list[str] = []
    manifest_paths = sorted(MANIFESTS.glob("*.defects.json"))
    if not manifest_paths:
        errors.append(f"inv1: no manifests found under {MANIFESTS}")
    seen_fixture_ids: list[str] = []
    manifested_manuscripts: set[str] = set()
    for path in manifest_paths:
        check_manifest(path, errors)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            seen_fixture_ids.append(data.get("fixture_id", ""))
            manifested_manuscripts.add(data.get("manuscript", ""))
        except (OSError, json.JSONDecodeError):
            pass  # already reported by check_manifest
    for path in manifest_paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue  # already reported
        fid = data.get("fixture_id", "")
        expected_ids = EXPECTED_DEFECT_IDS.get(fid)
        if expected_ids is None:
            continue  # unknown fixture_id handled by the set-equality check
        actual_ids = {
            row.get("defect_id", "") for row in data.get("defects", [])
        }
        if actual_ids != expected_ids:
            errors.append(
                f"inv6 {path.name}: defect ids {sorted(actual_ids)} != expected "
                f"{sorted(expected_ids)} — deleting/renaming a defect must be a "
                f"deliberate EXPECTED_DEFECT_IDS update, never a silent shrink"
            )
    if len(seen_fixture_ids) != len(set(seen_fixture_ids)):
        errors.append(
            "inv6: duplicate fixture_id across manifests — an extra manifest "
            "reusing an expected id would corrupt or double-count the inventory"
        )
    if set(seen_fixture_ids) != EXPECTED_FIXTURES:
        errors.append(
            f"inv6: manifest fixture_ids {sorted(set(seen_fixture_ids))} != expected "
            f"{sorted(EXPECTED_FIXTURES)} — a missing manifest silently shrinks "
            f"the acceptance set; update EXPECTED_FIXTURES deliberately instead"
        )
    for ms in sorted((ROOT / "manuscripts").glob("*_defective.md")):
        rel = f"manuscripts/{ms.name}"
        if rel not in manifested_manuscripts:
            errors.append(f"inv6: defective manuscript {rel} has no manifest")
    if not CLEAN_CONTROL.is_file():
        errors.append(f"inv5: clean control missing: {CLEAN_CONTROL}")

    if errors:
        for e in errors:
            print(f"FAIL {e}", file=sys.stderr)
        return 1
    print(
        f"PASSED: check_seeded_defect_fixtures — {len(manifest_paths)} manifests, "
        f"clean control present"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
