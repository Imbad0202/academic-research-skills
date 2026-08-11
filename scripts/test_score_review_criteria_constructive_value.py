from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

import score_review_criteria_constructive_value as scorer


REPO = Path(__file__).resolve().parents[1]
SCHEMA = (
    REPO
    / "evals"
    / "heldout"
    / "review_criteria_constructive_value"
    / "paired_adjudication.schema.json"
)
SCRIPT = REPO / "scripts" / "score_review_criteria_constructive_value.py"
SHA_A = "a" * 64
SHA_B = "b" * 64


def _finding(
    finding_id: str,
    *,
    support: str,
    predicted_severity: str,
    expert_severity: str,
    predicted_venue: str,
    expert_venue: str,
    usefulness: int,
) -> dict[str, object]:
    return {
        "finding_id": finding_id,
        "expert_labels": [
            {
                "expert_id": "expert-a",
                "support_label": support,
                "severity": expert_severity,
                "venue_alignment": expert_venue,
                "usefulness": usefulness,
            },
            {
                "expert_id": "expert-b",
                "support_label": support,
                "severity": expert_severity,
                "venue_alignment": expert_venue,
                "usefulness": usefulness,
            },
        ],
        "support_label": support,
        "predicted_severity": predicted_severity,
        "expert_severity": expert_severity,
        "predicted_venue_alignment": predicted_venue,
        "expert_venue_alignment": expert_venue,
        "usefulness": usefulness,
    }


def _replicate(arm: str, ordinal: int) -> dict[str, object]:
    treatment = arm == "treatment"
    findings = [
        _finding(
            f"{arm}-{ordinal}-F1",
            support="supported" if treatment else "unsupported",
            predicted_severity="major" if treatment else "critical",
            expert_severity="major",
            predicted_venue="aligned" if treatment else "not_aligned",
            expert_venue="aligned",
            usefulness=5 if treatment else 2,
        ),
        _finding(
            f"{arm}-{ordinal}-F2",
            support="supported",
            predicted_severity="critical" if treatment else "major",
            expert_severity="critical",
            predicted_venue="not_claimed",
            expert_venue="not_claimed",
            usefulness=4 if treatment else 3,
        ),
    ]
    return {
        "replicate_id": f"{arm}-{ordinal}",
        "profile": {
            "resolved_digest": SHA_B if treatment or ordinal == 1 else SHA_A,
            "selected_criterion_ids": ["c1", "c2"],
        },
        "applicability": [
            {
                "criterion_id": "c1",
                "predicted": "applicable",
                "expert_labels": [
                    {"expert_id": "expert-a", "label": "applicable"},
                    {"expert_id": "expert-b", "label": "applicable"},
                ],
                "expert_label": "applicable",
            },
            {
                "criterion_id": "c2",
                "predicted": "unresolved" if treatment else "not_applicable",
                "expert_labels": [
                    {"expert_id": "expert-a", "label": "unresolved"},
                    {"expert_id": "expert-b", "label": "unresolved"},
                ],
                "expert_label": "unresolved",
            },
        ],
        "findings": findings,
    }


def _record() -> dict[str, object]:
    budget = {
        "model_id": "synthetic/model",
        "model_family": "synthetic-family",
        "tools": [],
        "sampling": "temperature=0",
        "input_token_cap": 4000,
        "output_token_cap": 2000,
    }
    context = {
        "context_ref": "sealed/context.json",
        "context_sha256": SHA_A,
        "resolved_digest": SHA_B,
        "selected_criterion_ids": ["c1", "c2"],
    }
    return {
        "schema_version": "review-criteria-paired-adjudication/1.0",
        "suite": "review_criteria_constructive_value",
        "subject": {
            "suite_commit": "c" * 40,
            **budget,
            "replicates_per_item": 2,
        },
        "experts": [
            {
                "expert_id": "expert-a",
                "expert_type": "human",
                "expertise": "synthetic domain expert",
                "independent": True,
                "blinded_to": [
                    "arm_identity",
                    "mechanism_state",
                    "other_experts",
                    "raw_aggregate",
                    "expected_direction",
                ],
            },
            {
                "expert_id": "expert-b",
                "expert_type": "human",
                "expertise": "synthetic methodology expert",
                "independent": True,
                "blinded_to": [
                    "arm_identity",
                    "mechanism_state",
                    "other_experts",
                    "raw_aggregate",
                    "expected_direction",
                ],
            },
        ],
        "adjudication": {
            "adjudicator_id": "expert-c",
            "adjudicator_type": "human",
            "method": "independent labels followed by arm-blind resolution",
            "arm_blind": True,
            "disagreements_retained": True,
        },
        "items": [
            {
                "item_id": "RCV-01",
                "target_context": context,
                "arms": [
                    {
                        "arm_id": "baseline",
                        "mechanism": "pre_684",
                        "target_context": copy.deepcopy(context),
                        "budget": copy.deepcopy(budget),
                        "replicates": [
                            _replicate("baseline", 1),
                            _replicate("baseline", 2),
                        ],
                    },
                    {
                        "arm_id": "treatment",
                        "mechanism": "criteria_binding_v1",
                        "target_context": copy.deepcopy(context),
                        "budget": copy.deepcopy(budget),
                        "replicates": [
                            _replicate("treatment", 1),
                            _replicate("treatment", 2),
                        ],
                    },
                ],
            }
        ],
    }


def _raw(record: dict[str, object]) -> bytes:
    return json.dumps(record, sort_keys=True, separators=(",", ":")).encode()


def test_schema_is_draft_2020_12_and_positive_record_validates() -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(_record())


def test_score_reports_separate_metrics_and_no_composite() -> None:
    record = _record()
    result = scorer.score(record, _raw(record))
    assert result["composite_score"] is None
    assert result["per_arm"]["baseline"]["profile_resolution_rate"]["rate"] == 0.5
    assert result["per_arm"]["treatment"]["profile_resolution_rate"]["rate"] == 1.0
    assert result["per_arm"]["baseline"]["applicability_accuracy"]["rate"] == 0.5
    assert result["per_arm"]["treatment"]["applicability_accuracy"]["rate"] == 1.0
    assert result["per_arm"]["baseline"]["unsupported_finding_rate"]["rate"] == 0.5
    assert result["per_arm"]["treatment"]["unsupported_finding_rate"]["rate"] == 0.0
    assert result["per_arm"]["baseline"]["severity_agreement_rate"]["rate"] == 0.0
    assert result["per_arm"]["treatment"]["severity_agreement_rate"]["rate"] == 1.0
    assert result["per_arm"]["treatment"]["raw_expert_unanimity"]["support"] == {
        "numerator": 4,
        "denominator": 4,
        "rate": 1.0,
    }


@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        (lambda value: value["items"][0]["arms"][1]["target_context"].update({"resolved_digest": SHA_A}), "sealed item context"),
        (lambda value: value["items"][0]["arms"][1]["budget"].update({"output_token_cap": 1999}), "frozen subject budget"),
        (lambda value: value["items"][0]["arms"][1].update({"mechanism": "pre_684"}), "criteria_binding_v1"),
        (lambda value: value["items"][0]["arms"][0]["replicates"].pop(), "at least 2"),
        (lambda value: value["experts"].pop(), "at least 2"),
    ],
)
def test_incomparable_or_underlabelled_records_fail(mutation, match: str) -> None:
    value = _record()
    mutation(value)
    with pytest.raises(scorer.ScoreError, match=match):
        scorer.score(value, _raw(value))


def test_applicability_requires_authority_order() -> None:
    value = _record()
    rows = value["items"][0]["arms"][0]["replicates"][0]["applicability"]
    rows.reverse()
    with pytest.raises(scorer.ScoreError, match="authority order"):
        scorer.score(value, _raw(value))


def test_duplicate_replicate_identity_fails() -> None:
    value = _record()
    reps = value["items"][0]["arms"][0]["replicates"]
    reps[1]["replicate_id"] = reps[0]["replicate_id"]
    with pytest.raises(scorer.ScoreError, match="duplicate replicate_id"):
        scorer.score(value, _raw(value))


def test_every_label_row_must_cover_every_declared_expert() -> None:
    value = _record()
    labels = value["items"][0]["arms"][0]["replicates"][0]["applicability"][0]["expert_labels"]
    labels.pop()
    with pytest.raises(scorer.ScoreError, match="every declared expert"):
        scorer.score(value, _raw(value))


def test_unanimous_expert_label_cannot_be_overturned() -> None:
    value = _record()
    row = value["items"][0]["arms"][0]["replicates"][0]["findings"][0]
    row["support_label"] = "supported"
    with pytest.raises(scorer.ScoreError, match="unanimous expert label"):
        scorer.score(value, _raw(value))


def test_cli_is_deterministic_and_writes_explicit_output(tmp_path: Path) -> None:
    source = tmp_path / "adjudication.json"
    output = tmp_path / "score.json"
    source.write_bytes(_raw(_record()))
    first = subprocess.run(
        [sys.executable, str(SCRIPT), "--adjudication", str(source)],
        check=True,
        capture_output=True,
    ).stdout
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--adjudication",
            str(source),
            "--output",
            str(output),
        ],
        check=True,
    )
    assert output.read_bytes() == first
    assert json.loads(first)["source_sha256"] == scorer.hashlib.sha256(source.read_bytes()).hexdigest()


def test_duplicate_json_key_and_symlink_are_rejected(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"schema_version":"a","schema_version":"b"}')
    assert subprocess.run(
        [sys.executable, str(SCRIPT), "--adjudication", str(duplicate)],
        capture_output=True,
    ).returncode == 2
    source = tmp_path / "record.json"
    source.write_bytes(_raw(_record()))
    link = tmp_path / "link.json"
    link.symlink_to(source)
    assert subprocess.run(
        [sys.executable, str(SCRIPT), "--adjudication", str(link)],
        capture_output=True,
    ).returncode == 2


def test_parent_symlink_and_unbounded_id_are_rejected(tmp_path: Path) -> None:
    real_parent = tmp_path / "real"
    real_parent.mkdir()
    source = real_parent / "record.json"
    source.write_bytes(_raw(_record()))
    linked_parent = tmp_path / "linked"
    linked_parent.symlink_to(real_parent, target_is_directory=True)
    assert subprocess.run(
        [sys.executable, str(SCRIPT), "--adjudication", str(linked_parent / "record.json")],
        capture_output=True,
    ).returncode == 2

    invalid = _record()
    invalid["items"][0]["item_id"] = "x" * 129
    with pytest.raises(scorer.ScoreError, match="ASCII identifier"):
        scorer.score(invalid, _raw(invalid))
