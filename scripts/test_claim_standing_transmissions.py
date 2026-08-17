"""#655 PR-C: transmission-ledger contract and gate-14 allowlist tests.

Design authority: docs/design/2026-08-13-655-search-bounded-claim-standing-probe-design.md
§6 (separate transmission ledgers, per-event accounting) and §9 gate 14
(transmission logs obey the consented content allowlist). Hermetic: synthetic
fixtures and the injected fake transport only.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from scripts import build_claim_standing_candidate_ledger as substrate
from scripts import check_claim_standing_transmissions as transmissions
from scripts import claim_standing_stance_runner as runner
from scripts.test_build_claim_standing_candidate_ledger import (
    _rehash_input,
    _rehash_plan,
    _retained,
)
from scripts.test_claim_standing_stance_contracts import _plan_v1_0, _plan_v1_1
from scripts.test_claim_standing_stance_runner import FakeTransport

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "shared/contracts/claim_standing/transmission_ledger.schema.json"


def _stance_setup() -> tuple[dict, dict, dict]:
    plan = _plan_v1_1(stance=True)
    plan["stance_plan"]["prompt_contract_version"] = runner.PROMPT_CONTRACT_VERSION
    _rehash_plan(plan)
    retained = _retained()
    _rehash_input(retained, plan)
    ledger_value = substrate.build_ledger(plan, retained)
    return plan, retained, ledger_value


def _stance_transmissions(plan: dict, ledger_value: dict) -> list[dict]:
    _, _, events = runner.run_stance(plan, ledger_value, transport=FakeTransport())
    return events


def _retrieval_only_setup() -> tuple[dict, dict]:
    plan = _plan_v1_0()
    retained = _retained()
    _rehash_input(retained, plan)
    return plan, retained


def _build_full() -> tuple[dict, dict, list[dict], dict]:
    plan, retained, ledger_value = _stance_setup()
    stance_events = _stance_transmissions(plan, ledger_value)
    doc = transmissions.build_transmission_ledger(
        plan, retained, stance_transmissions=stance_events
    )
    return plan, retained, stance_events, doc


# --- schema -----------------------------------------------------------------


def test_schema_is_closed_draft_2020_12_and_accepts_built_ledger() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert schema["additionalProperties"] is False
    _, _, _, doc = _build_full()
    Draft202012Validator(schema).validate(doc)
    mutated = copy.deepcopy(doc)
    mutated["undeclared"] = True
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(mutated)


def test_schema_version_and_event_kinds_are_closed() -> None:
    _, _, _, doc = _build_full()
    assert doc["schema_version"] == "claim-standing-transmission-ledger/1.0"
    kinds = {event["event_kind"] for event in doc["events"]}
    assert kinds == {"retrieval_query", "stance_classification"}
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    mutated = copy.deepcopy(doc)
    mutated["events"][0]["event_kind"] = "ambient_telemetry"
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(mutated)


def test_schema_rejects_undeclared_event_field() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    _, _, _, doc = _build_full()
    mutated = copy.deepcopy(doc)
    mutated["events"][0]["session_cookie"] = "secret"
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(mutated)


# --- retrieval events -------------------------------------------------------


def test_one_retrieval_event_per_attempt_in_attempt_order() -> None:
    plan, retained, _, doc = _build_full()
    retrieval_events = [
        event for event in doc["events"] if event["event_kind"] == "retrieval_query"
    ]
    assert [event["attempt_id"] for event in retrieval_events] == [
        attempt["attempt_id"] for attempt in retained["attempts"]
    ]
    by_index = {p["index_id"]: p for p in plan["provider_roster"]}
    queries = {q["query_id"]: q for q in plan["queries"]}
    for event, attempt in zip(retrieval_events, retained["attempts"]):
        provider = by_index[attempt["index_id"]]
        query = queries[attempt["query_id"]]
        assert event["recipient_index_id"] == attempt["index_id"]
        assert event["recipient_product_identity"] == provider["product_identity"]
        assert event["purpose"] == "scholarly_discovery"
        assert event["content_classes"] == ["accepted_search_query"]
        assert event["query_sha256"] == query["query_sha256"]
        assert event["query_utf8_bytes"] == len(
            query["accepted_query_text"].encode("utf-8")
        )
        assert event["consent_receipt_id"] == plan["consent"]["consent_receipt_id"]
        assert event["retention_state"] == provider["retention_state"]
        assert event["retention_reference"] == provider["retention_reference"]
        assert event["sent_at"] == attempt["started_at"]
        assert event["result_state"] == attempt["outcome"]


def test_failed_attempt_remains_a_visible_event() -> None:
    _, retained, _, doc = _build_full()
    failed = [
        event
        for event in doc["events"]
        if event["event_kind"] == "retrieval_query"
        and event["result_state"] == "service_unavailable"
    ]
    assert len(failed) == 1


# --- stance events ----------------------------------------------------------


def test_stance_events_mirror_runner_transmissions_verbatim() -> None:
    _, _, stance_events, doc = _build_full()
    ledger_stance = [
        event
        for event in doc["events"]
        if event["event_kind"] == "stance_classification"
    ]
    assert len(ledger_stance) == len(stance_events)
    for event, source in zip(ledger_stance, stance_events):
        expected = dict(source)
        expected["event_kind"] = "stance_classification"
        assert event == expected


def test_ledger_digest_replays() -> None:
    _, _, _, doc = _build_full()
    assert doc["transmission_ledger_sha256"] == substrate.bound_digest(
        doc, "transmission_ledger_sha256"
    )


def test_ledger_binds_plan_and_receipt_identity() -> None:
    plan, _, _, doc = _build_full()
    assert doc["probe_id"] == plan["probe_id"]
    assert doc["query_plan_sha256"] == plan["plan_sha256"]
    assert doc["consent_receipt_id"] == plan["consent"]["consent_receipt_id"]
    assert doc["consent_receipt_sha256"] == plan["consent"]["receipt_sha256"]
    assert doc["authorized_content_classes"] == plan["authorized_content_classes"]


# --- gate 14: consented content allowlist -----------------------------------


def test_dropped_attempts_without_rehash_are_refused() -> None:
    plan, retained = _retrieval_only_setup()
    tampered = copy.deepcopy(retained)
    del tampered["attempts"][2]  # digest left stale: silent omission attempt
    with pytest.raises(transmissions.TransmissionError, match="digest"):
        transmissions.build_transmission_ledger(plan, tampered)


def test_cleared_attempt_array_is_refused_by_the_input_contract() -> None:
    plan, retained = _retrieval_only_setup()
    tampered = copy.deepcopy(retained)
    tampered["attempts"] = []
    tampered["retrieval_input_sha256"] = substrate.bound_digest(
        tampered, "retrieval_input_sha256"
    )
    with pytest.raises(transmissions.TransmissionError, match="invalid"):
        transmissions.build_transmission_ledger(plan, tampered)


def test_duplicate_attempt_ids_are_refused() -> None:
    plan, retained = _retrieval_only_setup()
    tampered = copy.deepcopy(retained)
    tampered["attempts"].append(copy.deepcopy(tampered["attempts"][0]))
    tampered["retrieval_input_sha256"] = substrate.bound_digest(
        tampered, "retrieval_input_sha256"
    )
    with pytest.raises(transmissions.TransmissionError, match="unique"):
        transmissions.build_transmission_ledger(plan, tampered)


def test_attempt_index_outside_query_targets_is_refused() -> None:
    plan, retained, _ = _stance_setup()
    tampered_plan = copy.deepcopy(plan)
    tampered_plan["queries"][0]["index_targets"] = ["index-a", "index-b"]
    _rehash_plan(tampered_plan)
    tampered = copy.deepcopy(retained)
    _rehash_input(tampered, tampered_plan)
    with pytest.raises(transmissions.TransmissionError, match="target"):
        transmissions.build_transmission_ledger(tampered_plan, tampered)


def test_stance_plan_requires_explicit_stance_transmissions() -> None:
    plan, retained, _ = _stance_setup()
    with pytest.raises(transmissions.TransmissionError, match="explicit"):
        transmissions.build_transmission_ledger(plan, retained)


def test_explicit_empty_stance_transmissions_build_zero_stance_events() -> None:
    plan, retained, _ = _stance_setup()
    doc = transmissions.build_transmission_ledger(
        plan, retained, stance_transmissions=[]
    )
    assert all(event["event_kind"] == "retrieval_query" for event in doc["events"])


def test_stance_event_with_unexpected_key_is_refused() -> None:
    plan, retained, ledger_value = _stance_setup()
    stance_events = _stance_transmissions(plan, ledger_value)
    stance_events[0] = dict(stance_events[0])
    stance_events[0]["event_kind"] = "retrieval_query"
    with pytest.raises(transmissions.TransmissionError, match="unexpected"):
        transmissions.build_transmission_ledger(
            plan, retained, stance_transmissions=stance_events
        )


def test_stance_record_cross_check_accepts_complete_events() -> None:
    plan, retained, ledger_value = _stance_setup()
    record, _, events = runner.run_stance(
        plan, ledger_value, transport=FakeTransport()
    )
    doc = transmissions.build_transmission_ledger(
        plan, retained, stance_transmissions=events, stance_record=record
    )
    assert doc["transmission_ledger_sha256"]


def test_resealed_omission_of_a_planned_attempt_is_refused() -> None:
    # Even a schema-valid, re-sealed retrieval input cannot drop a planned
    # query/index attempt: the canonical intake's one-initial-attempt-per-
    # planned-pair rule is enforced here too (gate 14 completeness).
    plan, retained = _retrieval_only_setup()
    tampered = copy.deepcopy(retained)
    del tampered["attempts"][2]
    tampered["retrieval_input_sha256"] = substrate.bound_digest(
        tampered, "retrieval_input_sha256"
    )
    with pytest.raises(transmissions.TransmissionError, match="initial attempt"):
        transmissions.build_transmission_ledger(plan, tampered)


def test_stance_record_cross_check_compares_prompt_and_result_fields() -> None:
    plan, retained, ledger_value = _stance_setup()
    record, _, events = runner.run_stance(
        plan, ledger_value, transport=FakeTransport()
    )
    tampered = [dict(events[0])]
    tampered[0]["prompt_sha256"] = "0" * 64
    with pytest.raises(transmissions.TransmissionError, match="prompt"):
        transmissions.build_transmission_ledger(
            plan, retained, stance_transmissions=tampered, stance_record=record
        )
    downgraded = [dict(events[0])]
    downgraded[0]["result_state"] = "judge_error"
    with pytest.raises(transmissions.TransmissionError, match="result"):
        transmissions.build_transmission_ledger(
            plan,
            retained,
            stance_transmissions=downgraded,
            stance_record=record,
        )


def test_failed_call_events_still_bind_their_prompt_hash() -> None:
    # A judge_timeout row must retain the prompt hash it sent, so a tampered
    # timeout event cannot seal a false hash (codex R3 P2).
    plan, retained, ledger_value = _stance_setup()
    record, _, events = runner.run_stance(
        plan, ledger_value, transport=FakeTransport(TimeoutError())
    )
    assert record["rows"][0]["failure_state"] == "judge_timeout"
    assert record["rows"][0]["prompt_sha256"] == events[0]["prompt_sha256"]
    tampered = [dict(events[0])]
    tampered[0]["prompt_sha256"] = "0" * 64
    with pytest.raises(transmissions.TransmissionError, match="prompt"):
        transmissions.build_transmission_ledger(
            plan, retained, stance_transmissions=tampered, stance_record=record
        )


def test_stance_record_cross_check_replays_the_record_digest() -> None:
    # An edited record (row dropped, digest left stale) must not be able to
    # vouch for a ledger missing that row's event.
    plan, retained, ledger_value = _stance_setup()
    record, _, _ = runner.run_stance(
        plan, ledger_value, transport=FakeTransport()
    )
    edited = copy.deepcopy(record)
    edited["rows"] = []
    with pytest.raises(transmissions.TransmissionError, match="digest"):
        transmissions.build_transmission_ledger(
            plan, retained, stance_transmissions=[], stance_record=edited
        )


def test_stance_record_cross_check_refuses_omitted_events() -> None:
    plan, retained, ledger_value = _stance_setup()
    record, _, _ = runner.run_stance(
        plan, ledger_value, transport=FakeTransport()
    )
    with pytest.raises(transmissions.TransmissionError, match="unaccounted"):
        transmissions.build_transmission_ledger(
            plan, retained, stance_transmissions=[], stance_record=record
        )


def test_stance_event_fields_match_the_schema_required_list() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    required = set(schema["$defs"]["stance_event"]["required"])
    assert set(transmissions.STANCE_EVENT_FIELDS) == required - {"event_kind"}


def test_stance_events_refused_under_retrieval_only_plan() -> None:
    plan, retained, ledger_value = _stance_setup()
    stance_events = _stance_transmissions(plan, ledger_value)
    retrieval_only_plan, retrieval_only_retained = _retrieval_only_setup()
    with pytest.raises(transmissions.TransmissionError, match="retrieval_plus_stance"):
        transmissions.build_transmission_ledger(
            retrieval_only_plan,
            retrieval_only_retained,
            stance_transmissions=stance_events,
        )


def test_retrieval_only_plan_builds_without_stance_events() -> None:
    plan, retained = _retrieval_only_setup()
    doc = transmissions.build_transmission_ledger(plan, retained)
    assert doc["authorized_content_classes"] == ["accepted_search_query"]
    assert all(event["event_kind"] == "retrieval_query" for event in doc["events"])


@pytest.mark.parametrize(
    "overrides, match",
    [
        (
            {
                "content_classes": [
                    "claim_and_selected_evidence_to_stance_provider",
                    "session_held_full_text_passage",
                ]
            },
            "content class",
        ),
        ({"recipient_provider_identity": "Unconsented Provider"}, "provider"),
        (
            {
                "retention_state": "known",
                "retention_reference": "https://example.org/terms",
            },
            "retention",
        ),
        ({"consent_receipt_id": "consent-other"}, "receipt"),
        ({"result_state": None}, "result_state"),
    ],
)
def test_tampered_stance_event_is_refused(overrides: dict, match: str) -> None:
    plan, retained, ledger_value = _stance_setup()
    stance_events = _stance_transmissions(plan, ledger_value)
    stance_events[0] = {**stance_events[0], **overrides}
    with pytest.raises(transmissions.TransmissionError, match=match):
        transmissions.build_transmission_ledger(
            plan, retained, stance_transmissions=stance_events
        )


def test_unconsented_recipient_index_refused() -> None:
    plan, retained, ledger_value = _stance_setup()
    stance_events = _stance_transmissions(plan, ledger_value)
    tampered = copy.deepcopy(retained)
    tampered["attempts"][0]["index_id"] = "index-unconsented"
    tampered["retrieval_input_sha256"] = substrate.bound_digest(
        tampered, "retrieval_input_sha256"
    )
    with pytest.raises(transmissions.TransmissionError, match="index"):
        transmissions.build_transmission_ledger(
            plan, tampered, stance_transmissions=stance_events
        )


def test_unknown_query_id_refused() -> None:
    plan, retained = _retrieval_only_setup()
    tampered = copy.deepcopy(retained)
    tampered["attempts"][0]["query_id"] = "q-unplanned"
    tampered["retrieval_input_sha256"] = substrate.bound_digest(
        tampered, "retrieval_input_sha256"
    )
    with pytest.raises(transmissions.TransmissionError, match="query"):
        transmissions.build_transmission_ledger(plan, tampered)


def test_attempt_receipt_id_mismatch_refused() -> None:
    plan, retained = _retrieval_only_setup()
    tampered = copy.deepcopy(retained)
    tampered["attempts"][0]["consent_receipt_id"] = "consent-other"
    tampered["retrieval_input_sha256"] = substrate.bound_digest(
        tampered, "retrieval_input_sha256"
    )
    with pytest.raises(transmissions.TransmissionError, match="receipt"):
        transmissions.build_transmission_ledger(plan, tampered)


def test_retained_input_not_bound_to_plan_refused() -> None:
    plan, _, ledger_value = _stance_setup()
    stance_events = _stance_transmissions(plan, ledger_value)
    unbound = _retained()  # still hashed against the 1.0 fixture plan
    with pytest.raises(transmissions.TransmissionError, match="plan"):
        transmissions.build_transmission_ledger(
            plan, unbound, stance_transmissions=stance_events
        )


# --- exact replay validation ------------------------------------------------


def test_validate_accepts_exact_replay() -> None:
    plan, retained, stance_events, doc = _build_full()
    transmissions.validate_transmission_ledger(plan, retained, stance_events, doc)


def test_validate_rejects_tampered_byte_count() -> None:
    plan, retained, stance_events, doc = _build_full()
    tampered = copy.deepcopy(doc)
    for event in tampered["events"]:
        if event["event_kind"] == "stance_classification":
            event["prompt_utf8_bytes"] += 1
            break
    tampered["transmission_ledger_sha256"] = substrate.bound_digest(
        tampered, "transmission_ledger_sha256"
    )
    with pytest.raises(transmissions.TransmissionError):
        transmissions.validate_transmission_ledger(
            plan, retained, stance_events, tampered
        )


def test_validate_rejects_dropped_event() -> None:
    plan, retained, stance_events, doc = _build_full()
    tampered = copy.deepcopy(doc)
    tampered["events"] = tampered["events"][1:]
    tampered["transmission_ledger_sha256"] = substrate.bound_digest(
        tampered, "transmission_ledger_sha256"
    )
    with pytest.raises(transmissions.TransmissionError):
        transmissions.validate_transmission_ledger(
            plan, retained, stance_events, tampered
        )


# --- CLI --------------------------------------------------------------------


def _write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def test_cli_build_prints_ledger_without_output(tmp_path, capsys) -> None:
    plan, retained, stance_events, doc = _build_full()
    rc = transmissions.main(
        [
            "build",
            "--query-plan", str(_write_json(tmp_path / "plan.json", plan)),
            "--retrieval-input", str(_write_json(tmp_path / "input.json", retained)),
            "--stance-transmissions",
            str(_write_json(tmp_path / "events.json", stance_events)),
        ]
    )
    assert rc == 0
    assert json.loads(capsys.readouterr().out) == doc


def test_cli_build_refuses_output_path_under_session_only(tmp_path, capsys) -> None:
    plan, retained = _retrieval_only_setup()
    assert plan["consent"]["local_persistence"] == "session_only"
    output = tmp_path / "out" / "anything.transmission-ledger.json"
    rc = transmissions.main(
        [
            "build",
            "--query-plan", str(_write_json(tmp_path / "plan.json", plan)),
            "--retrieval-input", str(_write_json(tmp_path / "input.json", retained)),
            "--output", str(output),
        ]
    )
    assert rc == 1
    assert "explicit_local_export" in capsys.readouterr().err
    assert not output.exists()
    assert not output.parent.exists()


def test_cli_export_writes_only_the_consent_derived_path(tmp_path, capsys) -> None:
    from scripts.test_build_claim_standing_candidate_ledger import (
        _authorize_local_export,
    )

    plan = _plan_v1_0()
    authorized_base = tmp_path / "authorized" / "probe"
    (tmp_path / "authorized").mkdir()
    _authorize_local_export(plan, str(authorized_base))
    retained = _retained()
    _rehash_input(retained, plan)
    plan_path = _write_json(tmp_path / "plan.json", plan)
    input_path = _write_json(tmp_path / "input.json", retained)

    somewhere_else = tmp_path / "elsewhere.json"
    rc = transmissions.main(
        [
            "build",
            "--query-plan", str(plan_path),
            "--retrieval-input", str(input_path),
            "--output", str(somewhere_else),
        ]
    )
    assert rc == 1
    assert not somewhere_else.exists()
    capsys.readouterr()

    derived = transmissions.authorized_transmission_ledger_path(plan)
    assert str(derived) == str(authorized_base) + ".transmission-ledger.json"
    rc = transmissions.main(
        [
            "build",
            "--query-plan", str(plan_path),
            "--retrieval-input", str(input_path),
            "--output", str(derived),
        ]
    )
    assert rc == 0
    capsys.readouterr()
    written = json.loads(derived.read_text(encoding="utf-8"))
    assert written == transmissions.build_transmission_ledger(plan, retained)


def test_cli_validate_replays_from_files(tmp_path, capsys) -> None:
    plan, retained, stance_events, doc = _build_full()
    rc = transmissions.main(
        [
            "validate",
            "--query-plan", str(_write_json(tmp_path / "plan.json", plan)),
            "--retrieval-input", str(_write_json(tmp_path / "input.json", retained)),
            "--stance-transmissions",
            str(_write_json(tmp_path / "events.json", stance_events)),
            "--transmission-ledger", str(_write_json(tmp_path / "doc.json", doc)),
        ]
    )
    assert rc == 0
    tampered = copy.deepcopy(doc)
    tampered["events"][0]["query_utf8_bytes"] += 1
    tampered["transmission_ledger_sha256"] = substrate.bound_digest(
        tampered, "transmission_ledger_sha256"
    )
    rc = transmissions.main(
        [
            "validate",
            "--query-plan", str(tmp_path / "plan.json"),
            "--retrieval-input", str(tmp_path / "input.json"),
            "--stance-transmissions", str(tmp_path / "events.json"),
            "--transmission-ledger",
            str(_write_json(tmp_path / "tampered.json", tampered)),
        ]
    )
    assert rc == 1
    assert "replay" in capsys.readouterr().err


# --- inputs stay unmutated (gate 12 support) --------------------------------


def test_build_does_not_mutate_inputs() -> None:
    plan, retained, ledger_value = _stance_setup()
    stance_events = _stance_transmissions(plan, ledger_value)
    plan_before = copy.deepcopy(plan)
    retained_before = copy.deepcopy(retained)
    events_before = copy.deepcopy(stance_events)
    transmissions.build_transmission_ledger(
        plan, retained, stance_transmissions=stance_events
    )
    assert plan == plan_before
    assert retained == retained_before
    assert stance_events == events_before
