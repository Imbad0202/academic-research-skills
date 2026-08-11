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
import json
import subprocess
from pathlib import Path

import pytest

import check_heldout_measurement_report as measurement_mod
from check_heldout_measurement_report import (
    HELDOUT_ROOT,
    REPO_ROOT,
    TEMPLATE_PATH,
    _execution_claim_errors,
    _execution_validator,
    _resolution_findings,
    _validate_obj,
    contract_version,
    is_contract_report,
    location_errors,
    marker_status,
    supported_contract_versions,
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
                "blinded_to": ["condition", "control_status"],
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
                "blinded_to": ["condition", "control_status"],
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
                "estimand_status": "point_estimate",
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
            "resolution_direction": "bidirectional",
            "resolution_rule_ref": "rubric_v1 direction",
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
        "preregistration": {
            "plan_ref": "evals/heldout/revision_claim_drift/RUN_PLAN.md",
            "plan_sha256": "b" * 64,
            "rubric_ref": "evals/heldout/revision_claim_drift/adjudication_rubric_v1.md",
            "rubric_sha256": "a" * 64,
            "frozen_commit": "0123456789abcdef0123456789abcdef01234567",
            "frozen_before_dispatch": True,
            "rubric_and_plan_frozen_together": True,
            "judge_template_version": "revision-claim-drift-judge/2.0",
            "amendments_append_only": True,
            "amendments": [],
        },
        "execution_manifest": {
            "ref": "evals/heldout/revision_claim_drift/runs/2026-08-10/execution-manifest.json",
            "sha256": "c" * 64,
            "write_once": True,
            "claims": [],
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
        "results": {
            "design": "matched two-condition evaluation",
            "arm_roles": {
                "treatment_or_cohort_arms": ["baseline", "treatment"],
                "variant_packet_arms": [],
            },
            "suite_specific": "free-form payload",
        },
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
    report["preregistration"].pop("judge_template_version")
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


def make_valid_human_expert_report() -> dict:
    """A paired-controls row whose judgments come only from a human panel."""
    report = make_valid_report()
    report["suite"] = "review_criteria_constructive_value"
    report["suite_class"] = "paired_controls"
    report["judge_plan"] = {
        "exception": "human_expert_panel",
        "expert_panel_ref": (
            "evals/heldout/review_criteria_constructive_value/runs/"
            "2026-08-11/paired-adjudication.json"
        ),
        "expert_panel_sha256": "d" * 64,
    }
    report["judges"] = []
    report["aggregate"]["agreement"] = {
        "rate": None,
        "divergent_items": [],
        "note": "model-judge agreement does not apply; human labels are in the panel record",
    }
    report["adjudication"]["overrides"] = []
    report["preregistration"]["judge_template_version"] = (
        "review-criteria-human-expert-label/1.0"
    )
    return report


def make_valid_v1_0_report() -> dict:
    """The pre-#664 shape remains valid without any v1.1 retrofit fields."""
    report = make_valid_report()
    report["measurement_contract"] = "heldout-measurement/1.0"
    report.pop("preregistration")
    report.pop("execution_manifest")
    for judge in report["judges"]:
        judge.pop("blinded_to")
    report["aggregate"]["headline"].pop("estimand_status")
    report["adjudication"].pop("resolution_direction")
    report["adjudication"].pop("resolution_rule_ref")
    report["results"] = {"suite_specific": "legacy free-form payload"}
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


def test_valid_human_expert_report_passes_without_model_judges():
    assert errors_of(make_valid_human_expert_report()) == []


def test_new_v1_0_report_is_rejected_even_if_schema_valid():
    assert any("I15" in error for error in errors_of(make_valid_v1_0_report()))


def test_frozen_2026_08_07_row_is_byte_unchanged_and_valid(monkeypatch):
    path = HELDOUT_ROOT / "revision_claim_drift/measurement-2026-08-07.json"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == (
        "1af137c798e6cf3a5d0a742e379a8af78fe802cb924b4ece22cdf57cb881f573"
    )
    import json

    report = json.loads(path.read_text(encoding="utf-8"))
    assert report["measurement_contract"] == "heldout-measurement/1.0"

    def unexpected_git_probe(*_args, **_kwargs):
        raise AssertionError("frozen v1.0 must not require full git history")

    monkeypatch.setattr(subprocess, "run", unexpected_git_probe)
    assert _validate_obj(path, report) == 0


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
    assert supported_contract_versions() == (
        "heldout-measurement/1.0",
        "heldout-measurement/1.1",
    )


def test_v1_1_template_stays_schema_and_invariant_valid():
    import json

    template = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    assert errors_of(template) == []


def test_v1_1_contract_schema_and_template_vocabulary_stay_synced():
    contract_doc = (HELDOUT_ROOT / "MEASUREMENT_CONTRACT.md").read_text(encoding="utf-8")
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    for token in (
        "heldout-measurement/1.1",
        "resolution_direction",
        "estimand_status",
        "blinded_to",
        "preregistration",
        "execution_manifest",
        "treatment_or_cohort_arms",
        "variant_packet_arms",
    ):
        assert token in contract_doc
        assert token in template_text


@pytest.mark.parametrize("field", ["preregistration", "execution_manifest", "results"])
def test_v1_1_requires_new_top_level_contract_fields(field):
    report = make_valid_report()
    del report[field]
    assert errors_of(report)


def test_v1_1_requires_judge_side_blinding_separately():
    report = make_valid_report()
    del report["judges"][0]["blinded_to"]
    assert errors_of(report)


def test_judge_and_adjudicator_blinding_are_independent():
    report = make_valid_report()
    report["judges"][0]["blinded_to"] = ["condition"]
    report["adjudication"]["blinded_to"] = ["judge_identity"]
    assert errors_of(report) == []


def test_v1_1_requires_design_and_arm_roles():
    report = make_valid_report()
    del report["results"]["arm_roles"]
    assert errors_of(report)


def test_flags_only_requires_lower_bound_estimand_status():
    report = make_valid_report()
    report["adjudication"]["resolution_direction"] = "flags_only"
    assert any("I13" in error for error in errors_of(report))


def test_flags_only_lower_bound_requires_headline_and_caveat_wording():
    report = make_valid_report()
    report["adjudication"]["resolution_direction"] = "flags_only"
    report["aggregate"]["headline"]["estimand_status"] = "lower_bound"
    report["aggregate"]["headline"]["construction_rule"] += "; lower bound"
    report["caveats"].append("The flags-only headline is a lower bound.")
    assert errors_of(report) == []


def test_other_frozen_requires_explicit_note_and_lower_bound_honesty():
    report = make_valid_report()
    report["adjudication"]["resolution_direction"] = "other_frozen"
    assert errors_of(report)
    report["adjudication"]["resolution_direction_note"] = (
        "The frozen rule may remove flags but cannot add missed flags."
    )
    assert any("I13" in error for error in errors_of(report))
    report["aggregate"]["headline"]["estimand_status"] = "lower_bound"
    report["aggregate"]["headline"]["construction_rule"] += "; lower bound"
    report["caveats"].append("The other-frozen headline is a lower bound.")
    assert errors_of(report) == []


def test_judge_template_version_required_only_for_judge_bearing_rows():
    report = make_valid_report()
    del report["preregistration"]["judge_template_version"]
    assert errors_of(report)
    assert errors_of(make_valid_mechanical_report()) == []


def test_preregistration_rubric_must_match_adjudication():
    report = make_valid_report()
    report["preregistration"]["rubric_sha256"] = "f" * 64
    assert any("I14" in error for error in errors_of(report))


def test_amendments_are_unique_and_append_ordered():
    report = make_valid_report()
    report["preregistration"]["amendments"] = [
        {
            "amendment_id": "A1",
            "recorded_at": "2026-08-08T01:00:00Z",
            "description": "first",
        },
        {
            "amendment_id": "a1",
            "recorded_at": "2026-08-08T00:00:00Z",
            "description": "duplicate and out of order",
        },
    ]
    errors = errors_of(report)
    assert sum("I14" in error for error in errors) >= 2


def test_arm_vocabularies_cannot_overlap():
    report = make_valid_report()
    report["results"]["arm_roles"]["variant_packet_arms"] = ["BASELINE"]
    assert any("I14" in error for error in errors_of(report))


def test_design_label_cannot_be_an_arm_label():
    report = make_valid_report()
    report["results"]["design"] = "treatment"
    assert any("I14" in error for error in errors_of(report))


@pytest.mark.parametrize(
    ("text", "claim"),
    [
        ("same-window execution", "same_window"),
        ("ordered execution", "ordering"),
        ("concurrent execution", "concurrency"),
    ],
)
def test_timing_claim_requires_execution_manifest_declaration(text, claim):
    report = make_valid_report()
    report["caveats"].append(text)
    assert any("I14" in error for error in errors_of(report))
    report["execution_manifest"]["claims"].append(claim)
    assert errors_of(report) == []


@pytest.mark.parametrize(
    "text",
    [
        "The calls were not run concurrently.",
        "No same-window execution was attempted.",
        "Execution never used ordering guarantees.",
    ],
)
def test_negated_timing_language_does_not_create_a_claim(text):
    report = make_valid_report()
    report["caveats"].append(text)
    assert errors_of(report) == []


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
    assert errors_of(report)


def test_invalid_amendment_timestamp_fails_schema_format_check():
    report = make_valid_report()
    report["preregistration"]["amendments"] = [
        {
            "amendment_id": "A1",
            "recorded_at": "not-a-timestamp",
            "description": "invalid fixture",
        }
    ]
    assert errors_of(report)


def test_naive_amendment_timestamp_fails_without_crashing_comparison():
    report = make_valid_report()
    report["preregistration"]["amendments"] = [
        {
            "amendment_id": "A1",
            "recorded_at": "2026-08-08T00:00:00Z",
            "description": "aware",
        },
        {
            "amendment_id": "A2",
            "recorded_at": "2026-08-08T01:00:00",
            "description": "missing timezone",
        },
    ]
    assert errors_of(report)


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


def test_human_expert_exception_on_llm_judged_fails():
    report = make_valid_report()
    report["judge_plan"] = {
        "exception": "human_expert_panel",
        "expert_panel_ref": "evals/heldout/revision_claim_drift/panel.json",
        "expert_panel_sha256": "d" * 64,
    }
    assert errors_of(report)


@pytest.mark.parametrize("field", ["expert_panel_ref", "expert_panel_sha256"])
def test_human_expert_exception_requires_both_bindings(field: str):
    report = make_valid_human_expert_report()
    del report["judge_plan"][field]
    assert errors_of(report)


def test_human_expert_exception_rejects_model_judges():
    report = make_valid_human_expert_report()
    report["judges"] = [make_valid_report()["judges"][0]]
    assert errors_of(report)


def test_human_expert_exception_requires_applied_adjudication():
    report = make_valid_human_expert_report()
    report["adjudication"] = {"applies": False}
    assert errors_of(report)


@pytest.mark.parametrize("exception", ["none", "legacy_comparability", "mechanical_suite"])
def test_other_exceptions_reject_expert_panel_fields(exception: str):
    report = make_valid_human_expert_report()
    report["judge_plan"]["exception"] = exception
    if exception == "legacy_comparability":
        report["judge_plan"]["legacy_baseline_ref"] = "legacy.json"
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


def _execution_manifest_fixture() -> dict:
    return {
        "schema_version": "heldout-execution-manifest/1.0",
        "suite": "revision_claim_drift",
        "created_at": "2026-08-08T00:00:00Z",
        "write_once": True,
        "calls": [
            {
                "call_id": "c1",
                "sequence_index": 1,
                "started_at": "2026-08-08T00:00:00Z",
                "completed_at": "2026-08-08T00:00:10Z",
                "prompt_sha256": "1" * 64,
                "output_sha256": "2" * 64,
                "concurrency_group": "g1",
            },
            {
                "call_id": "c2",
                "sequence_index": 2,
                "started_at": "2026-08-08T00:00:05Z",
                "completed_at": "2026-08-08T00:00:15Z",
                "prompt_sha256": "3" * 64,
                "output_sha256": "4" * 64,
                "concurrency_group": "g1",
            },
        ],
    }


def test_execution_manifest_timestamp_format_is_enforced():
    manifest = _execution_manifest_fixture()
    manifest["calls"][0]["started_at"] = "not-a-timestamp"
    assert list(_execution_validator().iter_errors(manifest))


def test_single_call_cannot_support_any_multi_call_execution_claim():
    manifest = _execution_manifest_fixture()
    manifest["calls"] = manifest["calls"][:1]
    errors = _execution_claim_errors(
        manifest, {"ordering", "concurrency", "same_window"}
    )
    assert len(errors) == 3


def test_concurrency_requires_grouped_overlapping_calls():
    manifest = _execution_manifest_fixture()
    assert _execution_claim_errors(manifest, {"concurrency"}) == []
    manifest["calls"][1]["started_at"] = "2026-08-08T00:00:10Z"
    assert any(
        "concurrency" in error
        for error in _execution_claim_errors(manifest, {"concurrency"})
    )


def test_ordering_requires_contiguous_indexes_and_nondecreasing_starts():
    manifest = _execution_manifest_fixture()
    assert _execution_claim_errors(manifest, {"ordering"}) == []
    manifest["calls"][1]["sequence_index"] = 3
    assert any(
        "ordering" in error
        for error in _execution_claim_errors(manifest, {"ordering"})
    )


def test_same_window_requires_declared_window_containing_all_calls():
    manifest = _execution_manifest_fixture()
    assert any(
        "same_window" in error
        for error in _execution_claim_errors(manifest, {"same_window"})
    )
    manifest["execution_window"] = {
        "window_id": "dispatch-1",
        "started_at": "2026-08-08T00:00:00Z",
        "completed_at": "2026-08-08T00:00:15Z",
    }
    assert _execution_claim_errors(manifest, {"same_window"}) == []


# ------------------------------------------------- reference resolution (R)


def _repo_file_sha256(rel: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest()


def make_resolvable_report() -> dict:
    report = make_valid_report()
    report["adjudication"]["rubric_ref"] = "README.md"
    report["adjudication"]["rubric_sha256"] = _repo_file_sha256("README.md")
    report["preregistration"]["rubric_ref"] = "README.md"
    report["preregistration"]["rubric_sha256"] = _repo_file_sha256("README.md")
    report["preregistration"]["plan_ref"] = "POSITIONING.md"
    report["preregistration"]["plan_sha256"] = _repo_file_sha256("POSITIONING.md")
    execution_ref = (
        "evals/heldout/revision_claim_drift/runs/fixtures/"
        "execution-manifest-v1.1.json"
    )
    report["execution_manifest"]["ref"] = execution_ref
    report["execution_manifest"]["sha256"] = _repo_file_sha256(execution_ref)
    report["raw_outputs"]["paths"] = ["evals/heldout/revision_claim_drift/README.md"]
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True
    ).stdout.strip()
    report["subject"]["config"]["suite_commit"] = head
    report["preregistration"]["frozen_commit"] = head
    return report


def test_resolvable_report_passes_with_refs():
    errors, _ = validate_report(make_resolvable_report(), resolve_refs=True)
    assert errors == []


def test_rubric_hash_mismatch_fails_with_refs():
    report = make_resolvable_report()
    report["adjudication"]["rubric_sha256"] = "b" * 64
    report["preregistration"]["rubric_sha256"] = "b" * 64
    errors, _ = validate_report(report, resolve_refs=True)
    assert any("R1" in e for e in errors)


def test_missing_rubric_file_fails_with_refs():
    report = make_resolvable_report()
    report["adjudication"]["rubric_ref"] = "does/not/exist.md"
    report["preregistration"]["rubric_ref"] = "does/not/exist.md"
    errors, _ = validate_report(report, resolve_refs=True)
    assert any("R1" in e for e in errors)


def test_traversal_rubric_ref_fails_with_refs():
    report = make_resolvable_report()
    report["adjudication"]["rubric_ref"] = "../outside.md"
    report["preregistration"]["rubric_ref"] = "../outside.md"
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


def test_preregistration_plan_hash_mismatch_fails_with_refs():
    report = make_resolvable_report()
    report["preregistration"]["plan_sha256"] = "d" * 64
    errors, _ = validate_report(report, resolve_refs=True)
    assert any("R4" in error for error in errors)


def test_unknown_preregistration_commit_fails_with_refs():
    report = make_resolvable_report()
    report["preregistration"]["frozen_commit"] = "deadbeef" * 5
    errors, _ = validate_report(report, resolve_refs=True)
    assert any("R4" in error for error in errors)


def test_execution_manifest_hash_mismatch_fails_with_refs():
    report = make_resolvable_report()
    report["execution_manifest"]["sha256"] = "e" * 64
    errors, _ = validate_report(report, resolve_refs=True)
    assert any("R5" in error for error in errors)


def test_unresolved_refs_ignored_without_flag():
    """resolve_refs=False (library/test mode) skips R1-R5 by design."""
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


def _valid_expert_panel() -> dict:
    return {
        "schema_version": "test-human-expert-panel/1.0",
        "suite": "review_criteria_constructive_value",
        "experts": [
            {
                "expert_id": "expert-a",
                "expert_type": "human",
                "expertise": "methods",
                "independent": True,
                "blinded_to": ["arm_identity", "mechanism_state"],
            },
            {
                "expert_id": "expert-b",
                "expert_type": "human",
                "expertise": "venue",
                "independent": True,
                "blinded_to": ["arm_identity", "mechanism_state"],
            },
        ],
        "adjudication": {
            "adjudicator_type": "human",
            "arm_blind": True,
            "disagreements_retained": True,
        },
    }


def _r6_errors(
    monkeypatch, tmp_path: Path, panel: dict, *, outside: bool = False
) -> list[str]:
    root = tmp_path / "repo"
    suite_root = root / "evals" / "heldout" / "review_criteria_constructive_value"
    panel_path = (root / "outside-panel.json") if outside else (suite_root / "panel.json")
    panel_path.parent.mkdir(parents=True)
    raw = json.dumps(panel, sort_keys=True).encode()
    panel_path.write_bytes(raw)

    report = make_valid_human_expert_report()
    report["judge_plan"]["expert_panel_ref"] = str(panel_path.relative_to(root))
    report["judge_plan"]["expert_panel_sha256"] = hashlib.sha256(raw).hexdigest()
    monkeypatch.setattr(measurement_mod, "REPO_ROOT", root)
    monkeypatch.setattr(measurement_mod, "HELDOUT_ROOT", root / "evals" / "heldout")
    return [error for error in _resolution_findings(report) if error.startswith("R6")]


def test_human_expert_panel_ref_resolves(monkeypatch, tmp_path):
    assert _r6_errors(monkeypatch, tmp_path, _valid_expert_panel()) == []


def test_human_expert_panel_must_live_under_suite(monkeypatch, tmp_path):
    errors = _r6_errors(monkeypatch, tmp_path, _valid_expert_panel(), outside=True)
    assert any("not under" in error for error in errors)


def test_human_expert_panel_hash_mismatch_fails(monkeypatch, tmp_path):
    panel = _valid_expert_panel()
    root = tmp_path / "repo"
    panel_path = root / "evals/heldout/review_criteria_constructive_value/panel.json"
    panel_path.parent.mkdir(parents=True)
    panel_path.write_text(json.dumps(panel))
    report = make_valid_human_expert_report()
    report["judge_plan"]["expert_panel_ref"] = str(panel_path.relative_to(root))
    report["judge_plan"]["expert_panel_sha256"] = "0" * 64
    monkeypatch.setattr(measurement_mod, "REPO_ROOT", root)
    monkeypatch.setattr(measurement_mod, "HELDOUT_ROOT", root / "evals" / "heldout")
    assert any("hash mismatch" in error for error in _resolution_findings(report))


def test_human_expert_panel_requires_two_experts(monkeypatch, tmp_path):
    panel = _valid_expert_panel()
    panel["experts"] = panel["experts"][:1]
    assert _r6_errors(monkeypatch, tmp_path, panel)


def test_human_expert_panel_requires_independence(monkeypatch, tmp_path):
    panel = _valid_expert_panel()
    panel["experts"][1]["independent"] = False
    assert _r6_errors(monkeypatch, tmp_path, panel)


def test_human_expert_panel_rejects_model_as_expert(monkeypatch, tmp_path):
    panel = _valid_expert_panel()
    panel["experts"][1]["expert_type"] = "model"
    assert _r6_errors(monkeypatch, tmp_path, panel)


def test_human_expert_panel_requires_human_adjudicator(monkeypatch, tmp_path):
    panel = _valid_expert_panel()
    panel["adjudication"]["adjudicator_type"] = "model"
    assert _r6_errors(monkeypatch, tmp_path, panel)


def test_human_expert_panel_rejects_fold_duplicate_ids(monkeypatch, tmp_path):
    panel = _valid_expert_panel()
    panel["experts"][1]["expert_id"] = "EXPERT-A"
    assert _r6_errors(monkeypatch, tmp_path, panel)


def test_human_expert_panel_requires_subject_blinding(monkeypatch, tmp_path):
    panel = _valid_expert_panel()
    panel["experts"][1]["blinded_to"] = ["arm_identity"]
    assert _r6_errors(monkeypatch, tmp_path, panel)


@pytest.mark.parametrize("field", ["arm_blind", "disagreements_retained"])
def test_human_expert_panel_requires_blind_retained_adjudication(
    monkeypatch, tmp_path, field: str
):
    panel = _valid_expert_panel()
    panel["adjudication"][field] = False
    assert _r6_errors(monkeypatch, tmp_path, panel)


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
