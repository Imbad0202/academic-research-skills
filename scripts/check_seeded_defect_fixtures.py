#!/usr/bin/env python3
"""Integrity lint for evals/heldout/reviewer_seeded_defects/ (#574/#610 v0.2).

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
  7. Every statistical defect carries one closed `statistical_kind`; the
     exact v0.2 kind/defect projection is pinned so reporting-only defects do
     not silently enter the #610 recomputation denominator.
  8. Every GRIMMER defect carries a small, structured integer-scale oracle
     whose expected inconsistency is recomputed by this checker.

Run: python3 scripts/check_seeded_defect_fixtures.py
Exit 0 on pass; 1 with per-invariant messages on failure.
"""
from __future__ import annotations

import json
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ROOT = REPO / "evals" / "heldout" / "reviewer_seeded_defects"
MANIFESTS = ROOT / "manifests"
CLEAN_CONTROL = ROOT / "manuscripts" / "ms00_clean_control.md"

# Expected inventory — update deliberately when fixtures/defects are
# added/retired. Values are the EXACT defect-ID sets: a coordinated
# row-deletion + defect_count decrement (or an SD-* rename that would orphan
# per_defect run records) must fail CI, not shrink the denominator silently.
EXPECTED_FIXTURE_VERSION = "0.2"
EXPECTED_DEFECT_IDS = {
    "ms01_quant": {f"SD-{i:02d}" for i in range(1, 12)},
    "ms02_qual": {f"SD-{i:02d}" for i in range(1, 10)},
}
EXPECTED_FIXTURES = set(EXPECTED_DEFECT_IDS)
EXPECTED_STATISTICAL_KINDS = {
    "ms01_quant": {
        "SD-01": "grim",
        "SD-02": "n_from_df",
        "SD-03": "p_from_test_statistic",
        "SD-11": "grimmer",
    },
    "ms02_qual": {"SD-07": "reporting_only"},
}

REQUIRED_TOP = {
    "fixture_id",
    "fixture_version",
    "manuscript",
    "defect_count",
    "defects",
}
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
STATISTICAL_KINDS = {
    "grim",
    "grimmer",
    "n_from_df",
    "p_from_test_statistic",
    "reporting_only",
}
RECOMPUTE_ORACLE_FIELDS = {
    "type",
    "n",
    "scale_min",
    "scale_max",
    "reported_mean",
    "reported_sd",
    "sd_convention",
    "rounding",
    "expected_consistent",
}


def _reported_quantum(value: str) -> tuple[Decimal, Decimal]:
    """Return a finite reported decimal and its explicit precision quantum."""
    if not isinstance(value, str):
        raise ValueError("reported values must be strings that preserve precision")
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"invalid decimal {value!r}") from exc
    if not parsed.is_finite():
        raise ValueError(f"reported decimal must be finite, got {value!r}")
    exponent = parsed.as_tuple().exponent
    quantum = Decimal(1).scaleb(exponent if exponent < 0 else 0)
    return parsed, quantum


def integer_scale_mean_sd_reachability(oracle: dict) -> tuple[bool, bool]:
    """Return rounded-mean and joint mean/SD reachability.

    This is a fixture oracle, not the future production GRIMMER engine. Its
    deliberately small bounds keep CI deterministic while independently
    proving that a planted prospective defect is arithmetically impossible.
    """
    if not isinstance(oracle, dict):
        raise ValueError("recompute_oracle must be an object")
    if set(oracle) != RECOMPUTE_ORACLE_FIELDS:
        missing = sorted(RECOMPUTE_ORACLE_FIELDS - set(oracle))
        extra = sorted(set(oracle) - RECOMPUTE_ORACLE_FIELDS)
        raise ValueError(f"oracle fields differ (missing={missing}, extra={extra})")
    if oracle["type"] != "integer_scale_mean_sd":
        raise ValueError(f"unsupported oracle type {oracle['type']!r}")
    n = oracle["n"]
    scale_min = oracle["scale_min"]
    scale_max = oracle["scale_max"]
    if (
        isinstance(n, bool)
        or not isinstance(n, int)
        or not 2 <= n <= 30
    ):
        raise ValueError("oracle n must be an integer between 2 and 30")
    if any(
        isinstance(value, bool) or not isinstance(value, int)
        for value in (scale_min, scale_max)
    ):
        raise ValueError("oracle scale bounds must be integers")
    if scale_min >= scale_max or scale_max - scale_min > 10:
        raise ValueError("oracle scale must be increasing with width at most 10")
    if oracle["sd_convention"] not in {"sample", "population"}:
        raise ValueError("sd_convention must be sample or population")
    if oracle["rounding"] != "half_up":
        raise ValueError("only half_up rounding is supported by the v0.2 oracle")
    if not isinstance(oracle["expected_consistent"], bool):
        raise ValueError("expected_consistent must be Boolean")

    reported_mean, mean_quantum = _reported_quantum(oracle["reported_mean"])
    reported_sd, sd_quantum = _reported_quantum(oracle["reported_sd"])
    if reported_sd < 0:
        raise ValueError("reported_sd cannot be negative")

    states = {(0, 0)}
    for _ in range(n):
        states = {
            (total + value, total_sq + value * value)
            for total, total_sq in states
            for value in range(scale_min, scale_max + 1)
        }

    mean_reachable = False
    with localcontext() as context:
        context.prec = 50
        decimal_n = Decimal(n)
        for total, total_sq in states:
            mean = Decimal(total) / decimal_n
            if mean.quantize(mean_quantum, rounding=ROUND_HALF_UP) != reported_mean:
                continue
            mean_reachable = True
            variance_numerator = n * total_sq - total * total
            variance_denominator = (
                n * (n - 1)
                if oracle["sd_convention"] == "sample"
                else n * n
            )
            sd = (
                Decimal(variance_numerator) / Decimal(variance_denominator)
            ).sqrt()
            if sd.quantize(sd_quantum, rounding=ROUND_HALF_UP) == reported_sd:
                return True, True
    return mean_reachable, False


def integer_scale_mean_sd_consistent(oracle: dict) -> bool:
    """Compatibility wrapper returning joint mean/SD reachability only."""
    return integer_scale_mean_sd_reachability(oracle)[1]


def canonical_recompute_oracle_anchor(oracle: dict) -> str:
    """Bind every oracle input to one unambiguous manuscript anchor."""
    return (
        "the reported secondary-item values were "
        f"N={oracle['n']}; M={oracle['reported_mean']}; "
        f"{oracle['sd_convention']} SD={oracle['reported_sd']}; "
        f"integer scale={oracle['scale_min']}-{oracle['scale_max']}"
    )


def check_recompute_oracle(path: Path, row: dict, errors: list[str]) -> None:
    rid = row.get("defect_id", "<missing id>")
    oracle = row.get("recompute_oracle")
    try:
        mean_reachable, joint_reachable = integer_scale_mean_sd_reachability(
            oracle
        )
    except (ValueError, ArithmeticError) as exc:
        errors.append(f"inv8 {path.name} {rid}: invalid recompute_oracle ({exc})")
        return
    # A defect cannot make a reachable replacement self-validating by changing
    # the expectation beside it. GRIMMER rows in this held-out manifest are,
    # by definition, planted inconsistencies.
    if oracle["expected_consistent"] is not False:
        errors.append(
            f"inv8 {path.name} {rid}: a grimmer defect must set "
            "expected_consistent=false"
        )
    if not mean_reachable:
        errors.append(
            f"inv8 {path.name} {rid}: GRIMMER prerequisite mean is unreachable"
        )
    if joint_reachable:
        errors.append(
            f"inv8 {path.name} {rid}: planted grimmer values are reachable"
        )
    expected_anchor = canonical_recompute_oracle_anchor(oracle)
    if row.get("anchor_quote") != expected_anchor:
        errors.append(
            f"inv8 {path.name} {rid}: oracle anchor must exactly equal "
            f"{expected_anchor!r}"
        )


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
    if data["fixture_version"] != EXPECTED_FIXTURE_VERSION:
        errors.append(
            f"inv1 {path.name}: fixture_version={data['fixture_version']!r}, "
            f"expected {EXPECTED_FIXTURE_VERSION!r}"
        )

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
        kind = row.get("statistical_kind")
        if row["class"] == "statistical":
            if kind not in STATISTICAL_KINDS:
                errors.append(
                    f"inv7 {path.name} {rid}: statistical_kind must be one of "
                    f"{sorted(STATISTICAL_KINDS)}, got {kind!r}"
                )
            if kind == "grimmer":
                check_recompute_oracle(path, row, errors)
            elif "recompute_oracle" in row:
                errors.append(
                    f"inv8 {path.name} {rid}: only grimmer rows may carry "
                    "recompute_oracle"
                )
        elif "statistical_kind" in row:
            errors.append(
                f"inv7 {path.name} {rid}: non-statistical row must not carry "
                "statistical_kind"
            )
        elif "recompute_oracle" in row:
            errors.append(
                f"inv8 {path.name} {rid}: non-GRIMMER row must not carry "
                "recompute_oracle"
            )
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
        actual_kinds = {
            row.get("defect_id", ""): row.get("statistical_kind")
            for row in data.get("defects", [])
            if row.get("class") == "statistical"
        }
        expected_kinds = EXPECTED_STATISTICAL_KINDS.get(fid, {})
        if actual_kinds != expected_kinds:
            errors.append(
                f"inv7 {path.name}: statistical projection {actual_kinds} != "
                f"expected {expected_kinds} — recompute and reporting-only "
                "denominators are versioned inventory"
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
