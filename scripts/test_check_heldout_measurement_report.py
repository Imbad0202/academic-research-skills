"""Mutation tests for scripts/check_heldout_measurement_report.py (#654).

Discipline mirrors the repo's other checker test suites: one valid fixture
must pass with zero errors, and every single-field mutation that violates a
contract invariant must fail. Checker-layer invariants assert their I/R/L
number; schema-layer violations assert non-empty errors. Warnings never gate
and are asserted separately.

Run: pytest scripts/test_check_heldout_measurement_report.py
"""
from __future__ import annotations

import copy
import hashlib
import subprocess
from pathlib import Path

import pytest

from check_heldout_measurement_report import (
    HELDOUT_ROOT,
    REPO_ROOT,
    contract_version,
    is_contract_report,
    location_errors,
    marker_status,
    validate_report,
)

CONTRACT_MARKER = contract_version()


def make_valid_report() -> dict:
    """A minimal but complete llm_judged report satisfying every invariant."""
    return {
        "measurement_contract": CONTRACT_MARKER,
        "suite": "revision_claim_drift",
        "suite_class": "llm_judged",
        "measurement_date": "2026-08-10",
        "decision_relevant": True,
        "subject": {
            "model_id": "claude-fable-5",
            "config": {
                "suite_commit": "0123456789abcdef0123456789abcdef01234567",
                "prompts_ref": "evals/heldout/revision_claim_drift/README.md#re-run-protocol",
                "settings": "one revision per item, fresh subagent context",
                "sampling": "provider default",
            },
        },
        "judge_plan": {"exception": "none"},
        "judges": [
            {
                "judge_id": "j1",
                "model_id": "gpt-5.6-sol",
                "model_family": "openai",
                "prompt_ref": "evals/heldout/revision_claim_drift/judge_prompt_v2.md",
                "evidence_provided": "original passage + revised passage + roadmap",
                "judging_budget": "xhigh, single pass",
                "per_item": [
                    {"item_id": "rp-01", "claim_drift": False},
                    {"item_id": "rp-02", "claim_drift": True},
                ],
            },
            {
                "judge_id": "j2",
                "model_id": "gemini-3.1-pro",
                "model_family": "google",
                "prompt_ref": "evals/heldout/revision_claim_drift/judge_prompt_v2.md",
                "evidence_provided": "original passage + revised passage + roadmap",
                "judging_budget": "provider default, single pass",
                "per_item": [
                    {"item_id": "rp-01", "claim_drift": False},
                    {"item_id": "rp-02", "claim_drift": False},
                ],
            },
        ],
        "aggregate": {
            "headline": {
                "metric_name": "claim_strength_hedge_drift_rate",
                "value": "1/2",
                "construction_rule": "post-adjudication confirmed drift over items; divergent items resolved by adjudication, never averaged",
            },
            "agreement": {
                "rate": 0.5,
                "divergent_items": ["rp-02"],
                "note": "j1 flagged rp-02, j2 did not; adjudicated below",
            },
        },
        "replicates": {
            "per_item": 2,
            "rule_ref": "evals/heldout/revision_claim_drift/README.md#re-run-protocol",
            "spread": None,
            "exception": None,
        },
        "adjudication": {
            "applies": True,
            "rubric_ref": "evals/heldout/revision_claim_drift/adjudication_rubric_v1.md",
            "rubric_sha256": "a" * 64,
            "rubric_precommitted": True,
            "blinded_to": ["expected_label", "raw_aggregate"],
            "overrides": [
                {
                    "item_id": "rp-02",
                    "judge_id": "j1",
                    "raw": "claim_drift=true",
                    "adjudicated": "claim_drift=true (upheld)",
                    "criterion_ref": "rubric_v1 C-2",
                    "note": "hedge drop confirmed on logic read",
                }
            ],
            "raw_published": True,
        },
        "attempts": {
            "atomicity": "one judge call per item per judge; failed call retried once then item marked blocked",
            "partial_published": True,
            "blocked_runs": [],
        },
        "raw_outputs": {
            "retained": True,
            "paths": ["evals/heldout/revision_claim_drift/runs/raw/2026-08-10/"],
        },
        "results": {"suite_specific": "free-form payload"},
        "verdict": "example",
        "caveats": ["n=2 excerpt fixture; not a real measurement"],
    }


def make_valid_mechanical_report() -> dict:
    report = make_valid_report()
    report["suite"] = "pipeline_behavior_robustness"
    report["suite_class"] = "mechanical_match"
    report["judges"] = []
    report["judge_plan"] = {"exception": "mechanical_suite"}
    report["adjudication"] = {"applies": False}
    report["aggregate"]["agreement"] = {
        "rate": None,
        "divergent_items": [],
        "note": "mechanical match; no judges",
    }
    return report


def make_valid_legacy_row() -> dict:
    report = make_valid_report()
    report["judges"] = [report["judges"][0]]
    report["judge_plan"] = {
        "exception": "legacy_comparability",
        "legacy_baseline_ref": "evals/heldout/revision_claim_drift/measurement-2026-07-22.json",
    }
    report["aggregate"]["agreement"] = {
        "rate": None,
        "divergent_items": [],
        "note": "legacy-comparability row keeps the original judge",
    }
    return report


def errors_of(report: dict) -> list[str]:
    errors, _warnings = validate_report(report)
    return errors


def warnings_of(report: dict) -> list[str]:
    _errors, warnings = validate_report(report)
    return warnings


# ---------------------------------------------------------------- valid pass


def test_valid_report_passes():
    assert errors_of(make_valid_report()) == []


def test_valid_mechanical_report_passes():
    assert errors_of(make_valid_mechanical_report()) == []


def test_valid_legacy_row_passes():
    assert errors_of(make_valid_legacy_row()) == []


# ------------------------------------------------------------- opt-in marker


def test_wrong_contract_marker_fails():
    report = make_valid_report()
    report["measurement_contract"] = "heldout-measurement/9.9"
    assert errors_of(report)


def test_is_contract_report_detection():
    assert is_contract_report(make_valid_report())
    assert is_contract_report({"measurement_contract": "heldout-measurement/9.9"})
    assert not is_contract_report({"measurement_date": "2026-07-22"})


def test_marker_status_classification():
    assert marker_status(make_valid_report()) == "contract"
    assert marker_status({"measurement_date": "x"}) == "absent"
    # leading space, homoglyph hyphen (U+2011), case games: all near-miss
    assert marker_status({"measurement_contract": " heldout-measurement/1.0"}) == "near_miss"
    assert (
        marker_status({"measurement_contract": "heldout‑measurement/1.0"})
        == "near_miss"
    )
    assert marker_status({"measurement_contract": "Heldout-Measurement/1.0"}) == "near_miss"
    assert marker_status({"measurement_contract": "internal-notes/0.1"}) == "near_miss"


def test_contract_version_single_sourced_from_schema():
    assert CONTRACT_MARKER.startswith("heldout-measurement/")
    assert make_valid_report()["measurement_contract"] == CONTRACT_MARKER


# ------------------------------------------------------------- schema layer


@pytest.mark.parametrize(
    "missing",
    [
        "suite",
        "suite_class",
        "measurement_date",
        "decision_relevant",
        "subject",
        "judge_plan",
        "judges",
        "aggregate",
        "replicates",
        "adjudication",
        "attempts",
        "raw_outputs",
        "verdict",
        "caveats",
    ],
)
def test_missing_required_top_level_field_fails(missing):
    report = make_valid_report()
    del report[missing]
    assert errors_of(report)


def test_bad_suite_class_fails():
    report = make_valid_report()
    report["suite_class"] = "vibes"
    assert errors_of(report)


def test_bad_date_fails():
    report = make_valid_report()
    report["measurement_date"] = "Aug 10, 2026"
    assert errors_of(report)


def test_impossible_date_fails():
    report = make_valid_report()
    report["measurement_date"] = "9999-99-99"
    assert any("I12" in e for e in errors_of(report))


def test_subject_missing_suite_commit_fails():
    report = make_valid_report()
    del report["subject"]["config"]["suite_commit"]
    assert errors_of(report)


def test_judge_missing_budget_fails():
    report = make_valid_report()
    del report["judges"][0]["judging_budget"]
    assert errors_of(report)


def test_empty_caveats_fails():
    report = make_valid_report()
    report["caveats"] = []
    assert errors_of(report)


def test_blank_caveat_fails():
    report = make_valid_report()
    report["caveats"] = [""]
    assert errors_of(report)


def test_blank_raw_output_path_fails():
    report = make_valid_report()
    report["raw_outputs"]["paths"] = [""]
    assert errors_of(report)


def test_evidence_free_per_item_row_fails():
    report = make_valid_report()
    for judge in report["judges"]:
        judge["per_item"] = [{"item_id": "rp-01"}, {"item_id": "rp-02"}]
    report["aggregate"]["agreement"] = {"rate": 1.0, "divergent_items": [], "note": ""}
    assert errors_of(report)


def test_empty_per_item_on_judged_suite_fails():
    report = make_valid_report()
    for judge in report["judges"]:
        judge["per_item"] = []
    report["aggregate"]["agreement"] = {"rate": None, "divergent_items": [], "note": ""}
    assert errors_of(report)


def test_declared_judge_plan_minimum_rejected():
    """The derived-minimum design: author-declared minimums are not a field."""
    report = make_valid_report()
    report["judge_plan"]["minimum_for_scored"] = 1
    assert errors_of(report)


def test_dash_replicate_exception_rejected():
    report = make_valid_report()
    report["replicates"]["per_item"] = 1
    report["replicates"]["exception"] = "-"
    assert errors_of(report)


def test_legacy_exception_requires_baseline_ref():
    report = make_valid_legacy_row()
    del report["judge_plan"]["legacy_baseline_ref"]
    assert errors_of(report)


def test_schema_invalid_short_circuits_invariants():
    report = make_valid_report()
    del report["judges"]
    errors = errors_of(report)
    assert errors
    assert all(e.startswith("schema ") for e in errors)


# ------------------------------------------- suite-class branches (schema)


def test_zero_judges_non_mechanical_fails():
    report = make_valid_report()
    report["judges"] = []
    report["judge_plan"] = {"exception": "none"}
    assert errors_of(report)


def test_llm_judged_adjudication_applies_false_fails():
    report = make_valid_report()
    report["adjudication"] = {"applies": False}
    assert errors_of(report)


def test_mechanical_exception_on_llm_judged_fails():
    report = make_valid_report()
    report["judge_plan"] = {"exception": "mechanical_suite"}
    assert errors_of(report)


def test_applies_false_with_rubric_fails():
    report = make_valid_mechanical_report()
    report["adjudication"] = {"applies": False, "rubric_ref": "sneaky.md"}
    assert errors_of(report)


# --------------------------------------------------- multi-judge invariants


def test_single_judge_without_exception_fails():
    report = make_valid_report()
    report["judges"] = [report["judges"][0]]
    report["aggregate"]["agreement"] = {
        "rate": None,
        "divergent_items": [],
        "note": "single judge",
    }
    assert any("I2" in e for e in errors_of(report))


def test_single_family_judges_fail():
    report = make_valid_report()
    report["judges"][1]["model_family"] = "openai"
    assert any("I2" in e for e in errors_of(report))


def test_case_variant_family_is_same_family():
    report = make_valid_report()
    report["judges"][1]["model_family"] = "OpenAI"
    report["judges"][1]["model_id"] = "gpt-5.5"
    assert any("I2" in e for e in errors_of(report))


def test_duplicate_judge_id_fails():
    report = make_valid_report()
    report["judges"][1]["judge_id"] = "j1"
    assert any("I9" in e for e in errors_of(report))


def test_same_model_two_families_fails():
    report = make_valid_report()
    report["judges"][1]["model_id"] = "gpt-5.6-sol"
    assert any("I9" in e for e in errors_of(report))


def test_same_model_and_prompt_twice_fails():
    report = make_valid_report()
    j2 = report["judges"][1]
    j2["model_id"] = "gpt-5.6-sol"
    j2["model_family"] = "openai"
    assert any("I9" in e for e in errors_of(report))


def test_non_decision_relevant_single_judge_passes():
    report = make_valid_report()
    report["decision_relevant"] = False
    report["judges"] = [report["judges"][0]]
    report["aggregate"]["agreement"] = {
        "rate": None,
        "divergent_items": [],
        "note": "seed run, single judge",
    }
    assert errors_of(report) == []


# --------------------------------------------------- item-identity hygiene


def test_duplicate_item_in_one_judge_fails():
    report = make_valid_report()
    report["judges"][0]["per_item"].append({"item_id": "rp-01", "claim_drift": False})
    assert any("I9" in e for e in errors_of(report))


def test_zero_width_item_id_spoof_fails():
    report = make_valid_report()
    report["judges"][1]["per_item"][1]["item_id"] = "rp-02​"
    assert any("I9" in e for e in errors_of(report))


def test_mismatched_verdict_keysets_fail():
    report = make_valid_report()
    report["judges"][1]["per_item"][1] = {"item_id": "rp-02", "drifted": False}
    assert any("I9" in e for e in errors_of(report))


# ------------------------------------------------- agreement-rate invariant


def test_wrong_agreement_rate_fails():
    report = make_valid_report()
    report["aggregate"]["agreement"]["rate"] = 0.9
    assert any("I1" in e for e in errors_of(report))


def test_null_rate_with_comparable_items_fails():
    report = make_valid_report()
    report["aggregate"]["agreement"]["rate"] = None
    assert any("I1" in e for e in errors_of(report))


def test_nonnull_rate_without_comparable_items_fails():
    report = make_valid_mechanical_report()
    report["aggregate"]["agreement"]["rate"] = 1.0
    assert any("I1" in e for e in errors_of(report))


def test_intra_judge_duplicate_cannot_mint_comparability():
    """One judge listing an item twice is I9, never a >=2-judge comparison."""
    report = make_valid_legacy_row()
    report["judges"][0]["per_item"] = [
        {"item_id": "rp-01", "claim_drift": False},
        {"item_id": "rp-01", "claim_drift": False},
    ]
    report["aggregate"]["agreement"]["rate"] = 1.0
    errors = errors_of(report)
    assert any("I9" in e for e in errors)
    # and the duplicate row is not counted as cross-judge comparability:
    assert any("I1" in e for e in errors)


def test_bool_int_payloads_diverge():
    """JSON true and 1 are different verdicts, not agreement."""
    report = make_valid_report()
    report["judges"][0]["per_item"][1]["claim_drift"] = True
    report["judges"][1]["per_item"][1]["claim_drift"] = 1
    # undeclared: the type-aware comparison must flag rp-02 as divergent
    hidden = copy.deepcopy(report)
    hidden["aggregate"]["agreement"]["divergent_items"] = []
    hidden["aggregate"]["agreement"]["rate"] = 1.0
    assert any("I8" in e for e in errors_of(hidden))
    # declared: the same report validates cleanly
    report["aggregate"]["agreement"]["divergent_items"] = ["rp-02"]
    report["aggregate"]["agreement"]["rate"] = 0.5
    assert errors_of(report) == []


# ---------------------------------------------------- divergence invariants


def test_divergent_item_unknown_id_fails():
    report = make_valid_report()
    report["aggregate"]["agreement"]["divergent_items"] = ["rp-02", "rp-99"]
    assert any("I3" in e for e in errors_of(report))


def test_agreeing_item_declared_divergent_fails():
    report = make_valid_report()
    report["aggregate"]["agreement"]["divergent_items"] = ["rp-02", "rp-01"]
    assert any("I3" in e for e in errors_of(report))


def test_missing_divergent_items_field_fails():
    report = make_valid_report()
    del report["aggregate"]["agreement"]["divergent_items"]
    assert errors_of(report)


def test_actual_cross_judge_divergence_not_listed_fails():
    report = make_valid_report()
    report["aggregate"]["agreement"]["divergent_items"] = []
    report["aggregate"]["agreement"]["rate"] = 0.5
    assert any("I8" in e for e in errors_of(report))


def test_divergence_without_override_fails():
    report = make_valid_report()
    report["adjudication"]["overrides"] = []
    assert any("I10" in e for e in errors_of(report))


# -------------------------------------------------- adjudication invariants


def test_raw_published_false_fails():
    report = make_valid_report()
    report["adjudication"]["raw_published"] = False
    assert errors_of(report)


def test_rubric_not_precommitted_fails():
    report = make_valid_report()
    report["adjudication"]["rubric_precommitted"] = False
    assert errors_of(report)


def test_bad_rubric_hash_fails():
    report = make_valid_report()
    report["adjudication"]["rubric_sha256"] = "nothex"
    assert errors_of(report)


def test_override_unknown_item_fails():
    report = make_valid_report()
    report["adjudication"]["overrides"][0]["item_id"] = "rp-99"
    assert any("I4" in e for e in errors_of(report))


def test_override_unknown_judge_fails():
    report = make_valid_report()
    report["adjudication"]["overrides"][0]["judge_id"] = "judge-that-never-ran"
    assert any("I4" in e for e in errors_of(report))


def test_override_missing_criterion_fails():
    report = make_valid_report()
    del report["adjudication"]["overrides"][0]["criterion_ref"]
    assert errors_of(report)


def test_bad_blinded_to_value_fails():
    report = make_valid_report()
    report["adjudication"]["blinded_to"] = ["vibes"]
    assert errors_of(report)


# ------------------------------------------------- suite-registry invariant


def test_unregistered_suite_fails():
    report = make_valid_report()
    report["suite"] = "not_a_registered_suite"
    assert any("I5" in e for e in errors_of(report))


def test_suite_class_registry_mismatch_fails():
    report = make_valid_report()
    report["suite"] = "pipeline_behavior_robustness"
    assert any("I5" in e for e in errors_of(report))


# ---------------------------------------------------- replicate invariants


def test_decision_relevant_single_replicate_fails():
    report = make_valid_report()
    report["replicates"]["per_item"] = 1
    assert any("I6" in e for e in errors_of(report))


def test_decision_relevant_single_replicate_with_exception_passes():
    report = make_valid_report()
    report["replicates"]["per_item"] = 1
    report["replicates"]["exception"] = (
        "seed run; explicitly labeled not decision-relevant for mechanism claims"
    )
    assert errors_of(report) == []


def test_non_decision_relevant_single_replicate_passes():
    report = make_valid_report()
    report["decision_relevant"] = False
    report["replicates"]["per_item"] = 1
    assert errors_of(report) == []


# ---------------------------------------------------- raw-output invariants


def test_raw_not_retained_fails():
    report = make_valid_report()
    report["raw_outputs"]["retained"] = False
    assert errors_of(report)


def test_raw_retained_empty_paths_fails():
    report = make_valid_report()
    report["raw_outputs"]["paths"] = []
    assert any("I7" in e for e in errors_of(report))


# ---------------------------------------------- partial coverage (I11 / W1)


def test_decision_relevant_item_gap_uncovered_fails():
    report = make_valid_report()
    report["judges"][1]["per_item"] = [{"item_id": "rp-01", "claim_drift": False}]
    report["aggregate"]["agreement"]["divergent_items"] = []
    report["aggregate"]["agreement"]["rate"] = 1.0
    report["adjudication"]["overrides"] = []
    assert any("I11" in e for e in errors_of(report))


def test_decision_relevant_item_gap_covered_by_blocked_runs_passes():
    report = make_valid_report()
    report["judges"][1]["per_item"] = [{"item_id": "rp-01", "claim_drift": False}]
    report["aggregate"]["agreement"]["divergent_items"] = []
    report["aggregate"]["agreement"]["rate"] = 1.0
    report["adjudication"]["overrides"] = []
    report["attempts"]["blocked_runs"] = [
        "j2 rp-02: judge call failed after retry; see runs/raw/2026-08-10/j2-rp-02.log"
    ]
    assert errors_of(report) == []


def test_item_gap_with_partial_unpublished_fails():
    report = make_valid_report()
    report["judges"][1]["per_item"] = [{"item_id": "rp-01", "claim_drift": False}]
    report["aggregate"]["agreement"]["divergent_items"] = []
    report["aggregate"]["agreement"]["rate"] = 1.0
    report["adjudication"]["overrides"] = []
    report["attempts"]["blocked_runs"] = ["j2 rp-02 blocked"]
    report["attempts"]["partial_published"] = False
    assert any("I11" in e for e in errors_of(report))


def test_non_decision_item_gap_warns_not_fails():
    report = make_valid_report()
    report["decision_relevant"] = False
    report["judges"][1]["per_item"] = [{"item_id": "rp-01", "claim_drift": False}]
    report["aggregate"]["agreement"]["divergent_items"] = []
    report["aggregate"]["agreement"]["rate"] = 1.0
    report["adjudication"]["overrides"] = []
    assert errors_of(report) == []
    assert any("W1" in w for w in warnings_of(report))


def test_valid_report_has_no_warnings():
    assert warnings_of(make_valid_report()) == []


# ---------------------------------------------------------- strict loading


def test_duplicate_keys_rejected():
    from check_heldout_measurement_report import _loads_strict

    with pytest.raises(ValueError):
        _loads_strict('{"raw_published": false, "raw_published": true}')


def test_nan_rejected():
    from check_heldout_measurement_report import _loads_strict

    with pytest.raises(ValueError):
        _loads_strict('{"rate": NaN}')


# ------------------------------------------------- reference resolution (R)


def _repo_file_sha256(rel: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest()


def make_resolvable_report() -> dict:
    report = make_valid_report()
    report["adjudication"]["rubric_ref"] = "README.md"
    report["adjudication"]["rubric_sha256"] = _repo_file_sha256("README.md")
    report["raw_outputs"]["paths"] = ["evals/heldout/revision_claim_drift/README.md"]
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True
    ).stdout.strip()
    report["subject"]["config"]["suite_commit"] = head
    return report


def test_resolvable_report_passes_with_refs():
    errors, _ = validate_report(make_resolvable_report(), resolve_refs=True)
    assert errors == []


def test_rubric_hash_mismatch_fails_with_refs():
    report = make_resolvable_report()
    report["adjudication"]["rubric_sha256"] = "b" * 64
    errors, _ = validate_report(report, resolve_refs=True)
    assert any("R1" in e for e in errors)


def test_missing_rubric_file_fails_with_refs():
    report = make_resolvable_report()
    report["adjudication"]["rubric_ref"] = "does/not/exist.md"
    errors, _ = validate_report(report, resolve_refs=True)
    assert any("R1" in e for e in errors)


def test_traversal_rubric_ref_fails_with_refs():
    report = make_resolvable_report()
    report["adjudication"]["rubric_ref"] = "../outside.md"
    errors, _ = validate_report(report, resolve_refs=True)
    assert any("R1" in e for e in errors)


def test_missing_raw_output_path_fails_with_refs():
    report = make_resolvable_report()
    report["raw_outputs"]["paths"] = ["evals/heldout/nonexistent-raw-dir/"]
    errors, _ = validate_report(report, resolve_refs=True)
    assert any("R2" in e for e in errors)


def test_unknown_suite_commit_fails_with_refs():
    report = make_resolvable_report()
    report["subject"]["config"]["suite_commit"] = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    errors, _ = validate_report(report, resolve_refs=True)
    assert any("R3" in e for e in errors)


def test_unresolved_refs_ignored_without_flag():
    """resolve_refs=False (library/test mode) skips R1-R3 by design."""
    assert errors_of(make_valid_report()) == []


# ------------------------------------------------------- location binding


def test_location_mismatch_fails():
    report = make_valid_report()
    path = HELDOUT_ROOT / "pipeline_behavior_robustness" / "measurement-2026-08-10.json"
    assert any("L1" in e for e in location_errors(path, report))


def test_location_match_passes():
    report = make_valid_report()
    path = HELDOUT_ROOT / "revision_claim_drift" / "measurement-2026-08-10.json"
    assert location_errors(path, report) == []


def test_location_outside_heldout_unchecked():
    report = make_valid_report()
    assert location_errors(Path("/tmp/draft.json"), report) == []


def test_location_heldout_root_depth1_fails():
    report = make_valid_report()
    path = HELDOUT_ROOT / "measurement-2026-08-10.json"
    assert any("L1" in e for e in location_errors(path, report))


def test_marker_status_null_value_is_near_miss():
    assert marker_status({"measurement_contract": None}) == "near_miss"


def test_fullwidth_model_alias_rejected():
    """NFKC-folded identity: a full-width respelling is the same judge."""
    report = make_valid_report()
    j2 = report["judges"][1]
    j2["model_id"] = "ｇｐｔ-5.6-sol"
    j2["model_family"] = "openai-mirror"
    assert any("I9" in e for e in errors_of(report))


def test_blocked_run_embedded_id_does_not_cover():
    """rp-02 embedded in rp-020 is not naming the gap (token boundaries)."""
    report = make_valid_report()
    report["judges"][1]["per_item"] = [{"item_id": "rp-01", "claim_drift": False}]
    report["aggregate"]["agreement"]["divergent_items"] = []
    report["aggregate"]["agreement"]["rate"] = 1.0
    report["adjudication"]["overrides"] = []
    report["attempts"]["blocked_runs"] = ["j9 rp-020 unrelated failure"]
    assert any("I11" in e for e in errors_of(report))


def test_raw_output_path_outside_suite_fails_with_refs():
    report = make_resolvable_report()
    report["raw_outputs"]["paths"] = ["README.md"]
    errors, _ = validate_report(report, resolve_refs=True)
    assert any("R2" in e for e in errors)


def test_bogus_legacy_baseline_ref_fails_with_refs():
    report = make_resolvable_report()
    report["judges"] = [report["judges"][0]]
    report["judge_plan"] = {
        "exception": "legacy_comparability",
        "legacy_baseline_ref": "does/not/exist.json",
    }
    report["aggregate"]["agreement"] = {
        "rate": None,
        "divergent_items": [],
        "note": "legacy row",
    }
    errors, _ = validate_report(report, resolve_refs=True)
    assert any("R1" in e for e in errors)


def test_commitish_suite_commit_rejected_by_schema():
    report = make_valid_report()
    report["subject"]["config"]["suite_commit"] = "HEAD~000"
    assert errors_of(report)


# ------------------------------------------------------------- purity guard


def test_validate_does_not_mutate_input():
    report = make_valid_report()
    snapshot = copy.deepcopy(report)
    validate_report(report)
    assert report == snapshot


# ------------------------------------------------------- --all scan (CLI)


def _scan_with_root(monkeypatch, root: Path) -> int:
    import check_heldout_measurement_report as mod

    monkeypatch.setattr(mod, "HELDOUT_ROOT", root)
    return mod._scan_all()


def test_scan_ignores_unmarked_legacy_json(monkeypatch, tmp_path, capsys):
    (tmp_path / "suite").mkdir()
    (tmp_path / "suite" / "legacy.json").write_text('{"anything": [1, 2, {"x": ')
    (tmp_path / "suite" / "other.json").write_text('{"measurement_date": "2026-01-01"}')
    assert _scan_with_root(monkeypatch, tmp_path) == 0
    assert "no contract-marked reports" in capsys.readouterr().out


def test_scan_duplicate_key_marked_file_fails(monkeypatch, tmp_path, capsys):
    (tmp_path / "s").mkdir()
    (tmp_path / "s" / "m.json").write_text(
        '{"measurement_contract": "heldout-measurement/1.0", '
        '"raw_published": true, "raw_published": false}'
    )
    assert _scan_with_root(monkeypatch, tmp_path) == 1
    assert "strict JSON parse" in capsys.readouterr().out


def test_scan_near_miss_marker_fails(monkeypatch, tmp_path, capsys):
    (tmp_path / "s").mkdir()
    (tmp_path / "s" / "m.json").write_text(
        '{"measurement_contract": " heldout-measurement/1.0"}'
    )
    assert _scan_with_root(monkeypatch, tmp_path) == 1
    assert "near-miss" in capsys.readouterr().out


def test_scan_follows_directory_symlinks(monkeypatch, tmp_path, capsys):
    scan_root = tmp_path / "root"
    scan_root.mkdir()
    real = scan_root / "real_dir"
    real.mkdir()
    (real / "m.json").write_text('{"measurement_contract": "heldout-measurement/1.0"}')
    (scan_root / "linked").symlink_to(real, target_is_directory=True)
    # marked but schema-invalid: must be DISCOVERED through the symlink and fail
    assert _scan_with_root(monkeypatch, scan_root) == 1


def test_scan_external_symlink_is_walk_error(monkeypatch, tmp_path, capsys):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "m.json").write_text('{"measurement_contract": "heldout-measurement/1.0"}')
    scan_root = tmp_path / "root"
    scan_root.mkdir()
    (scan_root / "linked").symlink_to(outside, target_is_directory=True)
    # the external target is not scanned, and the walk says so loudly
    assert _scan_with_root(monkeypatch, scan_root) == 1
    assert "resolves outside" in capsys.readouterr().out


def test_scan_escaped_marker_key_detected(monkeypatch, tmp_path, capsys):
    """A backslash-u-escaped spelling of the marker key cannot hide a report."""
    (tmp_path / "s").mkdir()
    (tmp_path / "s" / "m.json").write_text(
        '{"\\u006deasurement_contract": "heldout-measurement/1.0"}'
    )
    assert _scan_with_root(monkeypatch, tmp_path) == 1


def test_scan_null_marker_value_fails(monkeypatch, tmp_path, capsys):
    (tmp_path / "s").mkdir()
    (tmp_path / "s" / "m.json").write_text('{"measurement_contract": null}')
    assert _scan_with_root(monkeypatch, tmp_path) == 1
    assert "near-miss" in capsys.readouterr().out


def test_scan_non_utf8_json_fails(monkeypatch, tmp_path, capsys):
    (tmp_path / "s").mkdir()
    (tmp_path / "s" / "m.json").write_bytes(b'{"x": "\xff\xfe"}')
    assert _scan_with_root(monkeypatch, tmp_path) == 1
    assert "UTF-8" in capsys.readouterr().out


def test_scan_uppercase_extension_discovered(monkeypatch, tmp_path):
    (tmp_path / "s").mkdir()
    (tmp_path / "s" / "M.JSON").write_text(
        '{"measurement_contract": "heldout-measurement/1.0"}'
    )
    assert _scan_with_root(monkeypatch, tmp_path) == 1


def test_scan_unreadable_json_fails(monkeypatch, tmp_path):
    (tmp_path / "s").mkdir()
    dangling = tmp_path / "s" / "measurement-x.json"
    dangling.symlink_to(tmp_path / "s" / "does-not-exist.json")
    assert _scan_with_root(monkeypatch, tmp_path) == 1


def test_scan_external_file_symlink_is_walk_error(monkeypatch, tmp_path, capsys):
    """A .json FILE symlink resolving outside scan root and repo is loud."""
    scan_root = tmp_path / "root"
    (scan_root / "s").mkdir(parents=True)
    (scan_root / "s" / "external.json").symlink_to("/dev/null")
    assert _scan_with_root(monkeypatch, scan_root) == 1
    assert "resolves outside" in capsys.readouterr().out
