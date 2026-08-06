"""Mutation tests for scripts/check_heldout_measurement_report.py (#654).

Discipline mirrors the repo's other checker test suites: one valid fixture
must pass with zero errors, and every single-field mutation that violates a
contract invariant must fail with an error naming the invariant. Warnings are
asserted separately (they never gate).

Run: pytest scripts/test_check_heldout_measurement_report.py
"""
from __future__ import annotations

import copy
import json

import pytest

from check_heldout_measurement_report import validate_report

CONTRACT_MARKER = "heldout-measurement/1.0"


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
        "judge_plan": {
            "minimum_for_scored": 2,
            "actual": 2,
            "exception": "none",
        },
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


def errors_of(report: dict) -> list[str]:
    errors, _warnings = validate_report(report)
    return errors


def warnings_of(report: dict) -> list[str]:
    _errors, warnings = validate_report(report)
    return warnings


# ---------------------------------------------------------------- valid pass


def test_valid_report_passes():
    assert errors_of(make_valid_report()) == []


def test_valid_report_json_roundtrip_passes():
    report = json.loads(json.dumps(make_valid_report()))
    assert errors_of(report) == []


# ------------------------------------------------------------- opt-in marker


def test_wrong_contract_marker_fails():
    report = make_valid_report()
    report["measurement_contract"] = "heldout-measurement/9.9"
    assert errors_of(report)


def test_is_contract_report_detection():
    from check_heldout_measurement_report import is_contract_report

    assert is_contract_report(make_valid_report())
    assert not is_contract_report({"measurement_date": "2026-07-22"})


# ------------------------------------------------------------- schema layer


@pytest.mark.parametrize(
    "missing",
    [
        "suite",
        "suite_class",
        "measurement_date",
        "subject",
        "judge_plan",
        "judges",
        "aggregate",
        "replicates",
        "adjudication",
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


def test_subject_missing_suite_commit_fails():
    report = make_valid_report()
    del report["subject"]["config"]["suite_commit"]
    assert errors_of(report)


def test_judge_missing_budget_fails():
    report = make_valid_report()
    del report["judges"][0]["judging_budget"]
    assert errors_of(report)


def test_judge_missing_prompt_ref_fails():
    report = make_valid_report()
    del report["judges"][0]["prompt_ref"]
    assert errors_of(report)


def test_empty_caveats_fails():
    report = make_valid_report()
    report["caveats"] = []
    assert errors_of(report)


# --------------------------------------------------- multi-judge invariants


def test_judge_count_mismatch_fails():
    report = make_valid_report()
    report["judge_plan"]["actual"] = 3
    assert any("I1" in e for e in errors_of(report))


def test_single_judge_without_exception_fails():
    report = make_valid_report()
    report["judges"] = [report["judges"][0]]
    report["judge_plan"]["actual"] = 1
    assert any("I2" in e for e in errors_of(report))


def test_single_judge_with_legacy_exception_passes():
    report = make_valid_report()
    report["judges"] = [report["judges"][0]]
    report["judge_plan"]["actual"] = 1
    report["judge_plan"]["exception"] = "legacy_comparability"
    assert errors_of(report) == []


def test_zero_judges_fails_even_with_exception():
    report = make_valid_report()
    report["judges"] = []
    report["judge_plan"]["actual"] = 0
    report["judge_plan"]["exception"] = "mechanical_suite"
    assert errors_of(report)


def test_mechanical_suite_zero_judges_allowed():
    report = make_valid_report()
    report["suite_class"] = "mechanical_match"
    report["judges"] = []
    report["judge_plan"] = {
        "minimum_for_scored": 0,
        "actual": 0,
        "exception": "mechanical_suite",
    }
    report["adjudication"] = {"applies": False}
    report["aggregate"]["agreement"] = {
        "rate": None,
        "divergent_items": [],
        "note": "mechanical match; no judges",
    }
    assert errors_of(report) == []


# ---------------------------------------------------- aggregation invariants


def test_divergent_item_unknown_id_fails():
    report = make_valid_report()
    report["aggregate"]["agreement"]["divergent_items"] = ["rp-99"]
    assert any("I3" in e for e in errors_of(report))


def test_missing_divergent_items_field_fails():
    report = make_valid_report()
    del report["aggregate"]["agreement"]["divergent_items"]
    assert errors_of(report)


def test_actual_cross_judge_divergence_not_listed_fails():
    report = make_valid_report()
    report["aggregate"]["agreement"]["divergent_items"] = []
    assert any("I8" in e for e in errors_of(report))


# -------------------------------------------------- adjudication invariants


def test_raw_published_false_fails():
    report = make_valid_report()
    report["adjudication"]["raw_published"] = False
    assert any("I4" in e for e in errors_of(report))


def test_rubric_not_precommitted_fails():
    report = make_valid_report()
    report["adjudication"]["rubric_precommitted"] = False
    assert any("I4" in e for e in errors_of(report))


def test_bad_rubric_hash_fails():
    report = make_valid_report()
    report["adjudication"]["rubric_sha256"] = "nothex"
    assert errors_of(report)


def test_override_unknown_item_fails():
    report = make_valid_report()
    report["adjudication"]["overrides"][0]["item_id"] = "rp-99"
    assert any("I4" in e for e in errors_of(report))


def test_override_missing_criterion_fails():
    report = make_valid_report()
    del report["adjudication"]["overrides"][0]["criterion_ref"]
    assert errors_of(report)


def test_llm_judged_adjudication_applies_false_fails():
    report = make_valid_report()
    report["adjudication"] = {"applies": False}
    assert any("I5" in e for e in errors_of(report))


def test_bad_blinded_to_value_fails():
    report = make_valid_report()
    report["adjudication"]["blinded_to"] = ["vibes"]
    assert errors_of(report)


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
    assert any("I7" in e for e in errors_of(report))


def test_raw_retained_empty_paths_fails():
    report = make_valid_report()
    report["raw_outputs"]["paths"] = []
    assert any("I7" in e for e in errors_of(report))


# ------------------------------------------------------------- warnings


def test_judge_item_set_mismatch_warns_not_fails():
    report = make_valid_report()
    report["judges"][1]["per_item"] = [{"item_id": "rp-01", "claim_drift": False}]
    # rp-02 now judged by j1 only; j1's flag has no counterpart, so rp-02 is
    # no longer cross-judge divergent — keep the listed set consistent.
    report["aggregate"]["agreement"]["divergent_items"] = []
    assert errors_of(report) == []
    assert any("W1" in w for w in warnings_of(report))


def test_valid_report_has_no_warnings():
    assert warnings_of(make_valid_report()) == []


# ------------------------------------------------------------- deep-copy guard


def test_validate_does_not_mutate_input():
    report = make_valid_report()
    snapshot = copy.deepcopy(report)
    validate_report(report)
    assert report == snapshot
