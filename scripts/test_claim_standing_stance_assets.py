from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
SUITE_ROOT = ROOT / "evals" / "heldout" / "claim_standing_probe"


def _load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = _load_module(
    "claim_standing_assets_validator", "validate_claim_standing_stance_assets.py"
)
scorer = _load_module("claim_standing_stance_scorer", "claim_standing_stance_scorer.py")


@pytest.fixture(scope="module")
def shipped_set() -> dict:
    return json.loads((SUITE_ROOT / "heldout_stance_set.json").read_bytes())


def _adjudicated_from_design(set_value: dict) -> dict:
    """Stand-in gold for scorer tests ONLY (real gold requires human experts)."""
    rows = []
    for item in set_value["items"]:
        target = item["design_target"]
        rows.append(
            {
                "item_id": item["item_id"],
                "relevance": item["relevance_design"],
                "check_state": target["check_state"],
                "stance": target["stance"],
                "failure_state": target["failure_state"],
                "evidence_scope": item["candidate"]["coverage"],
                "disagreement": False,
                "adjudication_rationale": None,
            }
        )
    return {
        "schema_version": "claim-standing-adjudicated-labels/0.1",
        "suite": "claim_standing_probe",
        "adjudicator_id": "adjudicator-test",
        "expert_label_files": [
            {"expert_id": "expert-a", "sha256": "a" * 64},
            {"expert_id": "expert-b", "sha256": "b" * 64},
        ],
        "rows": rows,
    }


def _subject_from_adjudicated(adjudicated: dict, replicates: int = 2) -> dict:
    rows = []
    for gold in adjudicated["rows"]:
        for replicate in range(1, replicates + 1):
            rows.append(
                {
                    "item_id": gold["item_id"],
                    "replicate": replicate,
                    "row_state": "scored",
                    "relevance": gold["relevance"],
                    "check_state": gold["check_state"],
                    "stance": gold["stance"],
                    "failure_state": gold["failure_state"],
                    "evidence_scope": gold["evidence_scope"],
                    "rationale": (
                        "test rationale row" if gold["check_state"] == "performed" else None
                    ),
                }
            )
    return {
        "schema_version": "claim-standing-subject-output/0.1",
        "suite": "claim_standing_probe",
        "subject_run_id": "test-run-1",
        "rows": rows,
    }


# --- validator ---


def test_shipped_seed_set_passes_all_invariants(shipped_set):
    validator.validate_set(shipped_set)


def test_registration_is_deferred_until_implementation(shipped_set):
    registry = json.loads((SUITE_ROOT.parent / "suite_registry.json").read_bytes())
    assert "claim_standing_probe" not in registry


@pytest.mark.parametrize(
    "mutate, message",
    [
        (
            lambda v: v["items"][1].__setitem__("item_id", v["items"][0]["item_id"]),
            "unique",
        ),
        (
            lambda v: v["items"][0]["candidate"].__setitem__(
                "doi", "10.99999/csp-en-support-2"
            ),
            "doi",
        ),
        (
            lambda v: next(
                item for item in v["items"] if item["language"] == "zh-TW"
            ).update(claim_text="这项研究显示效果显著提升并可推广应用"),
            "[Ss]implified",
        ),
        (
            lambda v: next(
                item for item in v["items"] if item["item_id"].endswith("absmiss-1")
            )["design_target"].update(failure_state=None),
            "failure",
        ),
        (
            lambda v: next(
                item for item in v["items"] if item["item_id"].endswith("support-1")
            )["design_target"].update(stance="contradict"),
            "design slot",
        ),
        (
            lambda v: next(
                item for item in v["items"] if item["item_id"].endswith("irrel-1")
            ).update(relevance_design="relevant"),
            "not_relevant",
        ),
    ],
)
def test_validator_fails_closed_on_mutations(shipped_set, mutate, message):
    mutated = copy.deepcopy(shipped_set)
    mutate(mutated)
    with pytest.raises(validator.AssetError, match=message):
        validator.validate_set(mutated)


# --- scorer ---


def test_perfect_subject_scores_clean(shipped_set):
    adjudicated = _adjudicated_from_design(shipped_set)
    subject = _subject_from_adjudicated(adjudicated)
    report = scorer.score(shipped_set, adjudicated, subject)
    assert report["schema_version"] == "claim-standing-stance-score-report/0.1"
    assert report["not_a_measurement_contract_row"] is True
    assert report["rows"] == {"scored": 64, "blocked": 0, "partial": 0}
    assert report["replicates"]["decision_relevant_two_replicates"] is True
    for language in ("en", "zh-TW"):
        block = report["by_language"][language]
        assert block["micro_full_row_accuracy"] == 1.0
        assert block["stance_macro_recall"] == 1.0
        confusion = block["stance_confusion"]
        for gold_stance, row in confusion.items():
            assert set(row) == {gold_stance}
    assert report["overall"]["micro_full_row_accuracy"] == 1.0


def test_single_stance_swap_lands_in_the_right_cell(shipped_set):
    adjudicated = _adjudicated_from_design(shipped_set)
    subject = _subject_from_adjudicated(adjudicated)
    row = next(
        r
        for r in subject["rows"]
        if r["item_id"] == "csp-en-support-1" and r["replicate"] == 1
    )
    row["stance"] = "contradict"
    report = scorer.score(shipped_set, adjudicated, subject)
    en = report["by_language"]["en"]
    assert en["stance_confusion"]["support"]["contradict"] == 1
    assert en["micro_full_row_accuracy"] < 1.0
    assert report["by_language"]["zh-TW"]["micro_full_row_accuracy"] == 1.0


def test_not_checked_where_gold_performed_counts_as_check_state_miss(shipped_set):
    adjudicated = _adjudicated_from_design(shipped_set)
    subject = _subject_from_adjudicated(adjudicated)
    row = next(
        r
        for r in subject["rows"]
        if r["item_id"] == "csp-zh-mixed-1" and r["replicate"] == 2
    )
    row.update(check_state="not_checked", stance=None, failure_state="judge_error")
    report = scorer.score(shipped_set, adjudicated, subject)
    zh = report["by_language"]["zh-TW"]
    assert zh["check_state_confusion"]["performed"]["not_checked"] == 1
    assert zh["failure_state_distribution"]["judge_error"] == 1
    assert zh["stance_confusion"]["mixed"][scorer.ABSTAINED] == 1
    assert sum(zh["stance_confusion"]["mixed"].values()) == 4
    assert zh["stance_macro_recall"] < 1.0


def test_blocked_rows_break_decision_relevance_without_imputation(shipped_set):
    adjudicated = _adjudicated_from_design(shipped_set)
    subject = _subject_from_adjudicated(adjudicated)
    row = next(
        r
        for r in subject["rows"]
        if r["item_id"] == "csp-en-ambig-2" and r["replicate"] == 2
    )
    row.update(
        row_state="blocked",
        relevance=None,
        check_state=None,
        stance=None,
        failure_state="judge_timeout",
        evidence_scope=None,
        rationale=None,
    )
    report = scorer.score(shipped_set, adjudicated, subject)
    assert report["rows"]["blocked"] == 1
    assert report["by_language"]["en"]["failure_state_distribution"]["judge_timeout"] == 1
    assert report["replicates"]["decision_relevant_two_replicates"] is False


def test_scorer_fails_closed_on_bad_inputs(shipped_set):
    adjudicated = _adjudicated_from_design(shipped_set)
    subject = _subject_from_adjudicated(adjudicated)
    duplicated = copy.deepcopy(subject)
    duplicated["rows"].append(copy.deepcopy(duplicated["rows"][0]))
    with pytest.raises(scorer.ScoreError, match="schema"):
        scorer.score(shipped_set, adjudicated, duplicated)
    varied = copy.deepcopy(subject)
    extra = copy.deepcopy(varied["rows"][0])
    extra["rationale"] = "same item and replicate, different bytes"
    varied["rows"].append(extra)
    with pytest.raises(scorer.ScoreError, match="duplicate"):
        scorer.score(shipped_set, adjudicated, varied)

    missing = copy.deepcopy(adjudicated)
    missing["rows"] = missing["rows"][:-1]
    with pytest.raises(scorer.ScoreError, match="cover"):
        scorer.score(shipped_set, missing, subject)

    scalar = copy.deepcopy(subject)
    scalar["rows"][0]["confidence"] = 0.93
    with pytest.raises(scorer.ScoreError, match="schema|confidence|additional"):
        scorer.score(shipped_set, adjudicated, scalar)


def test_evidence_scope_mismatch_breaks_full_row_accuracy(shipped_set):
    adjudicated = _adjudicated_from_design(shipped_set)
    subject = _subject_from_adjudicated(adjudicated)
    row = next(
        r
        for r in subject["rows"]
        if r["item_id"] == "csp-en-fulltext-1" and r["replicate"] == 1
    )
    row["evidence_scope"] = "abstract"
    report = scorer.score(shipped_set, adjudicated, subject)
    en = report["by_language"]["en"]
    assert en["micro_full_row_accuracy"] < 1.0
    assert en["evidence_scope_agreement"]["disagree"] == 1
    assert en["stance_confusion"]["support"]["support"] == sum(
        en["stance_confusion"]["support"].values()
    )


def test_adjudication_requires_two_distinct_experts(shipped_set):
    adjudicated = _adjudicated_from_design(shipped_set)
    subject = _subject_from_adjudicated(adjudicated)
    adjudicated["expert_label_files"] = [
        {"expert_id": "expert-a", "sha256": "a" * 64},
        {"expert_id": "expert-a", "sha256": "c" * 64},
    ]
    with pytest.raises(scorer.ScoreError, match="two distinct"):
        scorer.score(shipped_set, adjudicated, subject)


def test_blocked_row_must_carry_a_failure_state(shipped_set):
    adjudicated = _adjudicated_from_design(shipped_set)
    subject = _subject_from_adjudicated(adjudicated)
    row = subject["rows"][0]
    row.update(
        row_state="blocked",
        relevance=None,
        check_state=None,
        stance=None,
        failure_state=None,
        evidence_scope=None,
        rationale=None,
    )
    with pytest.raises(scorer.ScoreError, match="schema"):
        scorer.score(shipped_set, adjudicated, subject)


def test_expert_files_with_identical_hashes_are_rejected(shipped_set):
    adjudicated = _adjudicated_from_design(shipped_set)
    subject = _subject_from_adjudicated(adjudicated)
    adjudicated["expert_label_files"] = [
        {"expert_id": "expert-a", "sha256": "a" * 64},
        {"expert_id": "expert-b", "sha256": "a" * 64},
    ]
    with pytest.raises(scorer.ScoreError, match="distinct file hashes"):
        scorer.score(shipped_set, adjudicated, subject)


def _expert_file_from_design(set_value: dict) -> dict:
    labels = []
    for item in set_value["items"]:
        target = item["design_target"]
        labels.append(
            {
                "item_id": item["item_id"],
                "relevance": item["relevance_design"],
                "check_state": target["check_state"],
                "stance": target["stance"],
                "failure_state": target["failure_state"],
                "evidence_scope": item["candidate"]["coverage"],
                "rationale": "synthetic test rationale for coverage checking",
                "label_guide_criterion": "REL",
            }
        )
    return {
        "schema_version": "claim-standing-expert-label/0.1",
        "suite": "claim_standing_probe",
        "expert_id": "expert-test",
        "blinded_to": [
            "design_target",
            "subject_output",
            "other_expert_labels",
            "model_or_provider",
            "expected_baseline_performance",
        ],
        "labels": labels,
    }


def test_expert_file_validator_requires_complete_distinct_coverage(shipped_set):
    expert_file = _expert_file_from_design(shipped_set)
    validator.validate_expert_file(expert_file, shipped_set)
    incomplete = copy.deepcopy(expert_file)
    incomplete["labels"][1]["item_id"] = incomplete["labels"][0]["item_id"]
    with pytest.raises(
        validator.AssetError, match="more than once|32 distinct|non-unique"
    ):
        validator.validate_expert_file(incomplete, shipped_set)
    reduced = copy.deepcopy(expert_file)
    reduced["labels"] = reduced["labels"][:-1]
    with pytest.raises(validator.AssetError, match="schema|32 distinct"):
        validator.validate_expert_file(reduced, shipped_set)


def test_closed_enums_stay_synchronized_across_schemas():
    def enum_of(schema_file, pointer):
        value = json.loads((SUITE_ROOT / schema_file).read_bytes())
        for key in pointer:
            value = value[key]
        return value

    stance_enums = [
        enum_of(
            "heldout_stance_set.schema.json",
            ["$defs", "design_target", "properties", "stance", "anyOf", 0, "enum"],
        ),
        enum_of(
            "subject_output.schema.json",
            ["$defs", "row", "properties", "stance", "anyOf", 0, "enum"],
        ),
        enum_of(
            "expert_label.schema.json",
            ["$defs", "label", "properties", "stance", "anyOf", 0, "enum"],
        ),
        enum_of(
            "adjudicated_labels.schema.json",
            ["$defs", "row", "properties", "stance", "anyOf", 0, "enum"],
        ),
    ]
    assert all(e == stance_enums[0] for e in stance_enums)
    expert_failures = enum_of(
        "expert_label.schema.json",
        ["$defs", "label", "properties", "failure_state", "anyOf", 0, "enum"],
    )
    subject_failures = enum_of(
        "subject_output.schema.json",
        ["$defs", "row", "properties", "failure_state", "anyOf", 0, "enum"],
    )
    assert set(expert_failures) <= set(subject_failures)


def test_report_validates_against_its_schema(shipped_set):
    # Sole job: fail if the scorer's internal report validation is removed.
    from jsonschema import Draft202012Validator

    adjudicated = _adjudicated_from_design(shipped_set)
    subject = _subject_from_adjudicated(adjudicated)
    report = scorer.score(shipped_set, adjudicated, subject)
    schema = json.loads((SUITE_ROOT / "stance_score_report.schema.json").read_bytes())
    Draft202012Validator(schema).validate(report)
