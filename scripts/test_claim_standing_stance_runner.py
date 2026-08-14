from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import build_claim_standing_candidate_ledger as ledger
from scripts import claim_standing_stance_runner as runner
from scripts.test_build_claim_standing_candidate_ledger import (
    _plan,
    _rehash_plan,
    _retained,
    _rehash_input,
)
from scripts.test_claim_standing_stance_contracts import STANCE_PLAN, _plan_v1_1

ROOT = Path(__file__).resolve().parent.parent
CONTRACTS = ROOT / "shared/contracts"

WELL_FORMED = (
    "STANCE: support\n"
    "EVIDENCE: A bounded synthetic abstract.\n"
    "CONDITIONS: none\n"
    "RATIONALE: The inspected text reports the same direction as the claim.\n"
)


class FakeTransport:
    provider_identity = STANCE_PLAN["provider_identity"]
    model_identity = STANCE_PLAN["model_identity"]
    runtime_identity = "offline-fake-transport"

    def __init__(self, output: str | Exception = WELL_FORMED):
        self.output = output
        self.prompts: list[str] = []

    def __call__(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if isinstance(self.output, Exception):
            raise self.output
        return self.output


def _stance_setup() -> tuple[dict, dict]:
    plan = _plan_v1_1(stance=True)
    plan["stance_plan"]["prompt_contract_version"] = runner.PROMPT_CONTRACT_VERSION
    _rehash_plan(plan)
    retained = _retained()
    _rehash_input(retained, plan)
    ledger_value = ledger.build_ledger(plan, retained)
    return plan, ledger_value


def test_happy_path_produces_valid_record_and_evidence_rows():
    plan, ledger_value = _stance_setup()
    transport = FakeTransport()
    record, evidence_rows, _ = runner.run_stance(plan, ledger_value, transport=transport)

    record_schema = json.loads(
        (CONTRACTS / "claim_standing/stance_record.schema.json").read_bytes()
    )
    Draft202012Validator(record_schema).validate(record)
    row_schema = json.loads(
        (CONTRACTS / "evidence/evidence_row_v1_3.schema.json").read_bytes()
    )
    for row in evidence_rows:
        Draft202012Validator(row_schema).validate(row)

    assert record["unmeasured_banner"] == "STANCE CLASSIFICATION UNMEASURED"
    assert record["identity"]["query_plan_sha256"] == plan["plan_sha256"]
    assert record["identity"]["candidate_ledger_sha256"] == ledger_value[
        "candidate_ledger_sha256"
    ]
    assert record["identity"]["stance_plan_sha256"] == ledger.digest(
        plan["stance_plan"]
    )
    assert len(record["rows"]) == 1
    row = record["rows"][0]
    assert row["check_state"] == "performed"
    assert row["stance"] == "support"
    assert len(row["evidence_row_refs"]) == 1
    evidence = evidence_rows[0]
    assert evidence["row_id"] == row["evidence_row_refs"][0]["row_id"]
    assert (
        ledger.bound_digest(evidence, "row_sha256")
        == row["evidence_row_refs"][0]["row_sha256"]
        == evidence["row_sha256"]
    )
    assert evidence["excerpt"]["state"] == "verified_exact_match"
    assert evidence["excerpt"]["text"] == "A bounded synthetic abstract."
    span = evidence["excerpt"]["source_span_utf8"]
    abstract = "A bounded synthetic abstract."
    assert abstract.encode("utf-8")[span["start"] : span["end"]].decode(
        "utf-8"
    ) == evidence["excerpt"]["text"]
    distribution = record["distribution"]
    assert distribution["selected_total"] == 1
    assert distribution["support"] == 1
    assert sum(
        distribution[key]
        for key in (
            "support",
            "contradict",
            "mixed",
            "not_addressed",
            "INSUFFICIENT_EVIDENCE",
            "AMBIGUOUS",
            "not_checked",
        )
    ) == distribution["selected_total"]
    assert len(transport.prompts) == 1
    prompt = transport.prompts[0]
    assert plan["claim"]["claim_text"] in prompt
    assert abstract in prompt
    runner.validate_stance_record(plan, ledger_value, record, evidence_rows)


def test_consent_gate_refuses_plans_without_stance_authorization():
    plan_1_0 = _plan()
    retained = _retained()
    ledger_value = ledger.build_ledger(plan_1_0, retained)
    with pytest.raises(runner.StanceError, match="retrieval_plus_stance"):
        runner.run_stance(plan_1_0, ledger_value, transport=FakeTransport())

    plan_retrieval_only = _plan_v1_1(stance=False)
    retained = _retained()
    _rehash_input(retained, plan_retrieval_only)
    ledger_value = ledger.build_ledger(plan_retrieval_only, retained)
    with pytest.raises(runner.StanceError, match="retrieval_plus_stance"):
        runner.run_stance(
            plan_retrieval_only, ledger_value, transport=FakeTransport()
        )


def test_transport_identity_must_match_the_consented_stance_plan():
    plan, ledger_value = _stance_setup()
    transport = FakeTransport()
    transport.model_identity = "some-other-model"
    with pytest.raises(runner.StanceError, match="model_identity"):
        runner.run_stance(plan, ledger_value, transport=transport)


def test_prompt_contract_version_binds_the_runner():
    plan, ledger_value = _stance_setup()
    plan["stance_plan"]["prompt_contract_version"] = "some-other-prompt-2.0"
    _rehash_plan(plan)
    retained = _retained()
    _rehash_input(retained, plan)
    ledger_value = ledger.build_ledger(plan, retained)
    with pytest.raises(runner.StanceError, match="prompt_contract_version"):
        runner.run_stance(plan, ledger_value, transport=FakeTransport())


@pytest.mark.parametrize(
    "output",
    [
        "STANCE: maybe\nEVIDENCE: A bounded synthetic abstract.\nCONDITIONS: none\nRATIONALE: x.\n",
        "EVIDENCE: A bounded synthetic abstract.\nRATIONALE: missing stance line.\n",
        "STANCE: support\nEVIDENCE: text that is not in the abstract\nCONDITIONS: none\nRATIONALE: x.\n",
        "STANCE: support\nEVIDENCE: "
        + "word " * 26
        + "\nCONDITIONS: none\nRATIONALE: x.\n",
    ],
)
def test_malformed_judge_output_becomes_parse_error(output):
    plan, ledger_value = _stance_setup()
    record, evidence_rows, _ = runner.run_stance(
        plan, ledger_value, transport=FakeTransport(output)
    )
    row = record["rows"][0]
    assert row["check_state"] == "not_checked"
    assert row["failure_state"] == "parse_error"
    assert row["stance"] is None
    assert row["raw_output"] == output
    assert record["distribution"]["not_checked"] == 1
    assert evidence_rows == []
    runner.validate_stance_record(plan, ledger_value, record, evidence_rows)


@pytest.mark.parametrize(
    "raised, failure",
    [(TimeoutError("slow judge"), "judge_timeout"), (RuntimeError("boom"), "judge_error")],
)
def test_transport_failures_map_to_the_closed_vocabulary(raised, failure):
    plan, ledger_value = _stance_setup()
    record, evidence_rows, _ = runner.run_stance(
        plan, ledger_value, transport=FakeTransport(raised)
    )
    row = record["rows"][0]
    assert row["check_state"] == "not_checked"
    assert row["failure_state"] == failure
    assert row["raw_output"] is None
    runner.validate_stance_record(plan, ledger_value, record, evidence_rows)


def test_nonstring_transport_return_is_judge_error():
    plan, ledger_value = _stance_setup()

    class NoneTransport(FakeTransport):
        def __call__(self, prompt: str):
            return None

    record, evidence_rows, transmissions = runner.run_stance(
        plan, ledger_value, transport=NoneTransport()
    )
    row = record["rows"][0]
    assert row["check_state"] == "not_checked"
    assert row["failure_state"] == "judge_error"
    assert transmissions[0]["result_state"] == "judge_error"


def test_every_transport_call_records_a_transmission_event():
    plan, ledger_value = _stance_setup()
    record, evidence_rows, transmissions = runner.run_stance(
        plan, ledger_value, transport=FakeTransport()
    )
    assert len(transmissions) == 1
    event = transmissions[0]
    assert event["recipient_provider_identity"] == STANCE_PLAN["provider_identity"]
    assert event["content_classes"] == [
        "claim_and_selected_evidence_to_stance_provider"
    ]
    assert event["consent_receipt_id"] == plan["consent"]["consent_receipt_id"]
    assert event["retention_state"] == "unknown"
    assert event["result_state"] == "performed"
    assert event["prompt_sha256"] == record["rows"][0]["prompt_sha256"]


def test_forged_cross_candidate_evidence_is_rejected():
    plan, ledger_value = _stance_setup()
    record, evidence_rows, _ = runner.run_stance(
        plan, ledger_value, transport=FakeTransport()
    )
    forged = copy.deepcopy(evidence_rows)
    forged[0]["candidate"]["canonical_raw_hit_id"] = "hit-2"
    forged[0]["row_sha256"] = ledger.bound_digest(forged[0], "row_sha256")
    resealed = copy.deepcopy(record)
    resealed["rows"][0]["evidence_row_refs"][0]["row_sha256"] = forged[0][
        "row_sha256"
    ]
    resealed["stance_record_sha256"] = ledger.bound_digest(
        resealed, "stance_record_sha256"
    )
    with pytest.raises(runner.StanceError, match="different\s+candidate|candidate"):
        runner.validate_stance_record(plan, ledger_value, resealed, forged)


def test_fabricated_excerpt_fails_span_replay():
    plan, ledger_value = _stance_setup()
    record, evidence_rows, _ = runner.run_stance(
        plan, ledger_value, transport=FakeTransport()
    )
    forged = copy.deepcopy(evidence_rows)
    forged[0]["excerpt"]["text"] = "totally fabricated excerpt"
    forged[0]["excerpt"]["excerpt_sha256"] = ledger.text_digest(
        "totally fabricated excerpt"
    )
    forged[0]["row_sha256"] = ledger.bound_digest(forged[0], "row_sha256")
    resealed = copy.deepcopy(record)
    resealed["rows"][0]["evidence_row_refs"][0]["row_sha256"] = forged[0][
        "row_sha256"
    ]
    resealed["stance_record_sha256"] = ledger.bound_digest(
        resealed, "stance_record_sha256"
    )
    with pytest.raises(runner.StanceError, match="replay"):
        runner.validate_stance_record(plan, ledger_value, resealed, forged)


def test_forged_stance_value_fails_raw_output_replay():
    plan, ledger_value = _stance_setup()
    record, evidence_rows, _ = runner.run_stance(
        plan, ledger_value, transport=FakeTransport()
    )
    forged = copy.deepcopy(record)
    forged["rows"][0]["stance"] = "contradict"
    forged["distribution"].update(support=0, contradict=1)
    forged["stance_record_sha256"] = ledger.bound_digest(
        forged, "stance_record_sha256"
    )
    with pytest.raises(runner.StanceError, match="replay"):
        runner.validate_stance_record(plan, ledger_value, forged, evidence_rows)


def test_blank_lines_in_judge_output_are_parse_errors():
    plan, ledger_value = _stance_setup()
    output = (
        "STANCE: support\n\nEVIDENCE: A bounded synthetic abstract.\n"
        "CONDITIONS: none\nRATIONALE: x.\n"
    )
    record, _, _ = runner.run_stance(
        plan, ledger_value, transport=FakeTransport(output)
    )
    assert record["rows"][0]["failure_state"] == "parse_error"


def test_semantic_validator_fails_closed_on_tampering():
    plan, ledger_value = _stance_setup()
    record, evidence_rows, _ = runner.run_stance(
        plan, ledger_value, transport=FakeTransport()
    )
    # Re-seal after tampering so the semantic layer, not the record hash,
    # must catch each violation independently.
    bad_sum = copy.deepcopy(record)
    bad_sum["distribution"]["support"] = 0
    bad_sum["stance_record_sha256"] = ledger.bound_digest(
        bad_sum, "stance_record_sha256"
    )
    with pytest.raises(runner.StanceError, match="distribution"):
        runner.validate_stance_record(plan, ledger_value, bad_sum, evidence_rows)

    missing_row = copy.deepcopy(record)
    missing_row["rows"] = []
    missing_row["distribution"].update(selected_total=0, support=0)
    missing_row["stance_record_sha256"] = ledger.bound_digest(
        missing_row, "stance_record_sha256"
    )
    with pytest.raises(runner.StanceError, match="selected"):
        runner.validate_stance_record(plan, ledger_value, missing_row, evidence_rows)

    tampered_evidence = copy.deepcopy(evidence_rows)
    tampered_evidence[0]["excerpt"]["text"] = "A bounded synthetic abstract!"
    with pytest.raises(runner.StanceError, match="row_sha256|does not bind"):
        runner.validate_stance_record(plan, ledger_value, record, tampered_evidence)

    stale = copy.deepcopy(record)
    stale["identity"]["candidate_ledger_sha256"] = "0" * 64
    stale["stance_record_sha256"] = ledger.bound_digest(
        stale, "stance_record_sha256"
    )
    with pytest.raises(runner.StanceError, match="candidate_ledger"):
        runner.validate_stance_record(plan, ledger_value, stale, evidence_rows)


def test_record_hash_binds_the_whole_record():
    plan, ledger_value = _stance_setup()
    record, evidence_rows, _ = runner.run_stance(
        plan, ledger_value, transport=FakeTransport()
    )
    assert record["stance_record_sha256"] == ledger.bound_digest(
        record, "stance_record_sha256"
    )
    mutated = copy.deepcopy(record)
    mutated["rows"][0]["rationale"] = "changed"
    with pytest.raises(runner.StanceError, match="stance_record_sha256"):
        runner.validate_stance_record(plan, ledger_value, mutated, evidence_rows)
