#!/usr/bin/env python3
"""Hermetic black-box and library tests for #673 adjudication activity."""
from __future__ import annotations

import copy
import fcntl
import hashlib
import json
from pathlib import Path
from collections.abc import Callable
from typing import Any

import jsonschema
import pytest

from scripts import adjudication_activity as activity
from scripts import check_re_review_synthesis as re_review
from scripts.test_check_re_review_synthesis import emit, scenario_g2d


REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "scripts/fixtures/adjudication_activity"
INPUT_SCHEMA = REPO / "shared/contracts/activity/adjudication_activity_input.schema.json"
STORE_SCHEMA = REPO / "shared/contracts/activity/adjudication_activity_store.schema.json"
STORE_ID = "ADJ-ACTIVITY-STORE-focused-tests"
LIMITATION = (
    "This records explicit adjudication activity only. It cannot determine correctness, "
    "attentiveness, engagement, or whether human ownership is real; genuine agreement and "
    "non-review can produce the same history."
)
ADVISORY = "This series is advisory only; it never gates, blocks, scores, or changes any verdict."
COVERAGE = (
    "Coverage: only successfully retained records in this explicitly selected store are "
    "shown; runs without this store selection or whose append failed are not represented."
)
STAGES = (
    "pipeline_stage_1",
    "pipeline_stage_2",
    "pipeline_stage_2_5",
    "pipeline_stage_3",
    "pipeline_stage_3_prime",
    "pipeline_stage_4",
    "pipeline_stage_4_prime",
    "pipeline_stage_4_5",
    "pipeline_stage_5",
    "pipeline_stage_6",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(activity.canonical_bytes(value) + b"\n")


def _independent_digest(domain: bytes, value: Any) -> str:
    canonical = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(domain + canonical).hexdigest()


def _independent_interaction(run_id: str, interaction_id: str) -> str:
    return _independent_digest(
        b"ars.adjudication-activity.interaction/1.0\0",
        {"run_id": run_id, "interaction_id": interaction_id},
    )


def _copy_fixture(root: Path, name: str) -> str:
    destination = root / "sources" / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes((FIXTURES / name).read_bytes())
    return destination.relative_to(root).as_posix()


def _artifact(
    artifact_id: str,
    role: str,
    group_id: str,
    relative_path: str,
    stage: str | None = None,
) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "artifact_role": role,
        "artifact_group_id": group_id,
        "artifact_group_stage": stage,
        "relative_path": relative_path,
    }


def _empty_rows(capture_state: str = "not_applicable") -> list[dict[str, Any]]:
    reason = (
        "not_applicable_for_run"
        if capture_state == "not_applicable"
        else "source_not_provided"
    )
    return [
        {
            "source_family": family,
            "capture_state": capture_state,
            "reason_code": reason,
            "artifacts": [],
        }
        for family in activity.SOURCE_FAMILIES
    ]


def _terminal_state(
    root: Path,
    run_id: str,
    *,
    pipeline_state: str = "completed",
    current_stage: str = "6",
    status: str = "completed",
    extra_completed: tuple[str, ...] = (),
) -> Path:
    stages = {current_stage: {"status": status}}
    stages.update({stage: {"status": "completed"} for stage in extra_completed})
    state = {
        "run_id": run_id,
        "pipeline_state": pipeline_state,
        "current_stage": current_stage,
        "stages": stages,
    }
    path = root / "state" / f"{run_id}.json"
    _write(path, state)
    return path


def _call(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str, str]:
    code = activity.main(list(argv))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def _seal_and_build(
    capsys: pytest.CaptureFixture[str],
    root: Path,
    state: Path,
    rows: list[dict[str, Any]],
    *,
    output_name: str = "input.json",
) -> Path:
    activity.seal_terminal_inventory(state, root, rows)
    output = root / output_name
    code, stdout, stderr = _call(
        capsys,
        "build-input",
        "--state",
        str(state),
        "--artifact-root",
        str(root),
        "--store-id",
        STORE_ID,
        "--output",
        str(output),
    )
    assert code == 0, stderr
    assert stdout.startswith("[ARS-ADJUDICATION-ACTIVITY] built_input run_id=")
    return output


def _append(
    capsys: pytest.CaptureFixture[str], root: Path, store: Path, manifest: Path
) -> tuple[int, str, str]:
    return _call(
        capsys,
        "append-run",
        "--store",
        str(store),
        "--artifact-root",
        str(root),
        "--input",
        str(manifest),
    )


def _make_re_review_chain(root: Path) -> tuple[str, str, str, str]:
    generated = root / "generated_re_review"
    generated.mkdir()
    emit(generated, scenario_g2d(False))
    manifest = _load(generated / "manifest.json")
    precommitment = _load(generated / "precommitment.json")
    verdict = _load(generated / "verdict_record.json")
    traceability = _load(generated / "traceability.json")

    traceability["dissent_adjudications"][0]["adjudicator"] = "user"
    reapplication = traceability["reapplications"][0]
    reapplication["reapplied_verdict"] = "NOT_ADDRESSED"
    reapplication.pop("cannot_verify_reason")
    anchor = {
        "anchor": 'text: §6 "procedure evidence"',
        "anchor_artifact": "manuscript",
    }
    reapplication["evidence_anchor"] = [anchor]
    traceability["adjustments"] = [
        {
            "adjustment_id": "ADJ-1",
            "item_id": "REV-001",
            "from_verdict": "FULLY_ADDRESSED",
            "to_verdict": "NOT_ADDRESSED",
            "basis": "cross_model_adjudication",
            "evidence_anchor": [anchor],
            "rationale": reapplication["rationale"],
            "source_ref": "reapplication:RAP-1",
        }
    ]
    first_row = traceability["rows"][0]
    first_row.update(
        {
            "verified": "NO",
            "status": "NOT_ADDRESSED",
            "final_verdict": "NOT_ADDRESSED",
            "adjustment_id": "ADJ-1",
        }
    )
    traceability["decision_inputs"]["per_item"][0]["final_verdict"] = "NOT_ADDRESSED"

    precommitment["input_manifest_hash"] = re_review.canonical_hash(manifest)
    verdict["precommitment_hash"] = re_review.canonical_hash(precommitment)
    traceability["verdict_record_hash"] = re_review.canonical_hash(verdict)
    _write(generated / "manifest.json", manifest)
    _write(generated / "precommitment.json", precommitment)
    _write(generated / "verdict_record.json", verdict)
    _write(generated / "traceability.json", traceability)

    for name in ("input_manifest", "precommitment", "verdict_record", "traceability"):
        schema = REPO / "shared/contracts/re_review" / f"{name}.schema.json"
        artifact_name = "manifest" if name == "input_manifest" else name
        jsonschema.Draft202012Validator(_load(schema)).validate(
            _load(generated / f"{artifact_name}.json")
        )
    return tuple(
        (generated / name).relative_to(root).as_posix()
        for name in (
            "manifest.json",
            "precommitment.json",
            "verdict_record.json",
            "traceability.json",
        )
    )  # type: ignore[return-value]


def _all_event_rows(root: Path) -> list[dict[str, Any]]:
    author_paths = [
        _copy_fixture(root, "author_stage3_input.json"),
        _copy_fixture(root, "author_stage3.json"),
        _copy_fixture(root, "author_stage3_prime_input.json"),
        _copy_fixture(root, "author_stage3_prime.json"),
    ]
    override_report = _copy_fixture(root, "compliance_override.json")
    override_action = _copy_fixture(root, "compliance_override_action.json")
    pass_report = _copy_fixture(root, "compliance_pass.json")
    explicit_log = _copy_fixture(root, "explicit_user_request_log.json")
    mandatory_log = _copy_fixture(root, "mandatory_checkpoint_log.json")
    manifest, precommitment, verdict, traceability = _make_re_review_chain(root)
    return [
        {
            "source_family": "revision_author_adjudication",
            "capture_state": "captured",
            "reason_code": None,
            "artifacts": [
                _artifact("author-input-3", "author_adjudication_input", "SOURCE-GROUP-author-3", author_paths[0], "pipeline_stage_3"),
                _artifact("author-output-3", "author_adjudication", "SOURCE-GROUP-author-3", author_paths[1], "pipeline_stage_3"),
                _artifact("author-input-3p", "author_adjudication_input", "SOURCE-GROUP-author-3p", author_paths[2], "pipeline_stage_3_prime"),
                _artifact("author-output-3p", "author_adjudication", "SOURCE-GROUP-author-3p", author_paths[3], "pipeline_stage_3_prime"),
            ],
        },
        {
            "source_family": "compliance_report",
            "capture_state": "captured",
            "reason_code": None,
            "artifacts": [
                _artifact("compliance-override-report", "compliance_report", "SOURCE-GROUP-compliance-1", override_report),
                _artifact("compliance-override-action", "compliance_override_action_receipt", "SOURCE-GROUP-compliance-1", override_action),
                _artifact("compliance-pass-a", "compliance_report", "SOURCE-GROUP-compliance-2", pass_report),
                _artifact("compliance-pass-b", "compliance_report", "SOURCE-GROUP-compliance-3", pass_report),
            ],
        },
        {
            "source_family": "re_review_traceability",
            "capture_state": "captured",
            "reason_code": None,
            "artifacts": [
                _artifact("rereview-manifest", "input_manifest", "SOURCE-GROUP-rereview", manifest),
                _artifact("rereview-precommitment", "precommitment", "SOURCE-GROUP-rereview", precommitment),
                _artifact("rereview-verdict", "verdict_record", "SOURCE-GROUP-rereview", verdict),
                _artifact("rereview-traceability", "traceability", "SOURCE-GROUP-rereview", traceability),
            ],
        },
        {
            "source_family": "explicit_user_request",
            "capture_state": "captured",
            "reason_code": None,
            "artifacts": [
                _artifact("explicit-log", "explicit_user_request_log", "SOURCE-GROUP-explicit", explicit_log)
            ],
        },
        {
            "source_family": "mandatory_checkpoint_response",
            "capture_state": "captured",
            "reason_code": None,
            "artifacts": [
                _artifact("mandatory-log", "mandatory_checkpoint_response_log", "SOURCE-GROUP-mandatory", mandatory_log)
            ],
        },
    ]


def _compliance_rows(
    root: Path,
    run_id: str,
    mutate_action: Callable[[dict[str, Any]], None] | None = None,
) -> list[dict[str, Any]]:
    report_path = _copy_fixture(root, "compliance_override.json")
    action = _load(FIXTURES / "compliance_override_action.json")
    action["run_id"] = run_id
    action["interaction_sha256"] = _independent_interaction(
        run_id, action["interaction_id"]
    )
    action["report_sha256"] = hashlib.sha256((root / report_path).read_bytes()).hexdigest()
    if mutate_action is not None:
        mutate_action(action)
    action_path = root / "sources" / "compliance-action-dynamic.json"
    _write(action_path, action)
    rows = _empty_rows()
    rows[1] = {
        "source_family": "compliance_report",
        "capture_state": "captured",
        "reason_code": None,
        "artifacts": [
            _artifact(
                "compliance-report",
                "compliance_report",
                "SOURCE-GROUP-compliance",
                report_path,
            ),
            _artifact(
                "compliance-action",
                "compliance_override_action_receipt",
                "SOURCE-GROUP-compliance",
                action_path.relative_to(root).as_posix(),
            ),
        ],
    }
    return rows


def _single_log_rows(
    root: Path,
    run_id: str,
    *,
    mandatory: bool,
    mutate_record: Callable[[dict[str, Any]], None] | None = None,
) -> list[dict[str, Any]]:
    interaction_id = "USER-LOG-1"
    common = {
        "actor_role": "user",
        "source": "explicit_session_user_action",
        "stage": "pipeline_stage_3",
        "interaction_id": interaction_id,
        "interaction_sha256": _independent_interaction(run_id, interaction_id),
    }
    if mandatory:
        record = {
            **common,
            "response_id": "RESPONSE-1",
            "checkpoint_id": "checkpoint-1",
            "checkpoint_type": "MANDATORY",
            "disposition": "pause",
        }
        version = "adjudication-mandatory-checkpoint-log/1.0"
        family_index = 4
        family = "mandatory_checkpoint_response"
        role = "mandatory_checkpoint_response_log"
    else:
        record = {
            **common,
            "request_id": "REQUEST-1",
            "action": "justify_finding",
            "finding_id": "REV-001",
        }
        version = "adjudication-explicit-user-request-log/1.0"
        family_index = 3
        family = "explicit_user_request"
        role = "explicit_user_request_log"
    if mutate_record is not None:
        mutate_record(record)
    log_path = root / "sources" / f"{family}-dynamic.json"
    _write(
        log_path,
        {"schema_version": version, "run_id": run_id, "records": [record]},
    )
    rows = _empty_rows()
    rows[family_index] = {
        "source_family": family,
        "capture_state": "captured",
        "reason_code": None,
        "artifacts": [
            _artifact(
                "action-log",
                role,
                f"SOURCE-GROUP-{'mandatory' if mandatory else 'explicit'}",
                log_path.relative_to(root).as_posix(),
            )
        ],
    }
    return rows


def _re_review_rows(
    root: Path,
    mutate: Callable[[dict[str, Any], dict[str, Any]], None],
) -> list[dict[str, Any]]:
    paths = _make_re_review_chain(root)
    verdict_path = root / paths[2]
    trace_path = root / paths[3]
    verdict = _load(verdict_path)
    trace = _load(trace_path)
    mutate(verdict, trace)
    trace["verdict_record_hash"] = re_review.canonical_hash(verdict)
    _write(verdict_path, verdict)
    _write(trace_path, trace)
    rows = _empty_rows()
    rows[2] = {
        "source_family": "re_review_traceability",
        "capture_state": "captured",
        "reason_code": None,
        "artifacts": [
            _artifact("rereview-manifest", "input_manifest", "SOURCE-GROUP-rereview", paths[0]),
            _artifact("rereview-precommitment", "precommitment", "SOURCE-GROUP-rereview", paths[1]),
            _artifact("rereview-verdict", "verdict_record", "SOURCE-GROUP-rereview", paths[2]),
            _artifact("rereview-trace", "traceability", "SOURCE-GROUP-rereview", paths[3]),
        ],
    }
    return rows


def _recompute_record(run: dict[str, Any]) -> None:
    preimage = {key: value for key, value in run.items() if key != "record_sha256"}
    run["record_sha256"] = _independent_digest(
        b"ars.adjudication-activity.run/1.0\0", preimage
    )


def test_contract_schemas_and_closed_positive_negative_payloads() -> None:
    input_schema = _load(INPUT_SCHEMA)
    store_schema = _load(STORE_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(input_schema)
    jsonschema.Draft202012Validator.check_schema(store_schema)

    input_payload = {
        "schema_version": "adjudication-activity-input/1.0",
        "store_id": STORE_ID,
        "run_id": "run-schema",
        "terminal_state": "completed",
        "terminal_stage": "pipeline_stage_6",
        "terminal_receipt": {
            "artifact_id": "pipeline-state-terminal-receipt",
            "relative_path": "state/run-schema.json",
            "sha256": "0" * 64,
            "run_id": "run-schema",
            "pipeline_state": "completed",
            "current_stage": "pipeline_stage_6",
            "current_stage_status": "completed",
        },
        "sources": _empty_rows(),
        "data_minimization": copy.deepcopy(activity.DATA_MINIMIZATION),
    }
    jsonschema.Draft202012Validator(input_schema).validate(input_payload)
    poisoned = copy.deepcopy(input_payload)
    poisoned["events"] = []
    assert list(jsonschema.Draft202012Validator(input_schema).iter_errors(poisoned))

    empty_store = {
        "schema_version": "adjudication-activity-store/1.0",
        "store_id": STORE_ID,
        "revision": 0,
        "next_sequence": 1,
        "runs": [],
        "data_minimization": copy.deepcopy(activity.DATA_MINIMIZATION),
    }
    jsonschema.Draft202012Validator(store_schema).validate(empty_store)
    poisoned_store = copy.deepcopy(empty_store)
    poisoned_store["score"] = 100
    assert list(jsonschema.Draft202012Validator(store_schema).iter_errors(poisoned_store))


def test_init_build_append_validate_render_and_exact_retry_no_write(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "artifacts"
    state = _terminal_state(root, "run-zero")
    manifest = _seal_and_build(capsys, root, state, _empty_rows("unavailable"))
    store = tmp_path / "activity.json"

    code, stdout, stderr = _call(capsys, "init-store", "--store", str(store), "--store-id", STORE_ID)
    assert (code, stderr) == (0, "")
    assert stdout == f'[ARS-ADJUDICATION-ACTIVITY] initialized store_id="{STORE_ID}"; revision=0; next_sequence=1\n'
    code, stdout, stderr = _append(capsys, root, store, manifest)
    assert (code, stderr) == (0, "")
    assert "append_sequence=1; revision=1" in stdout
    before = store.read_bytes()
    code, stdout, stderr = _append(capsys, root, store, manifest)
    assert (code, stderr) == (0, "")
    assert "already_appended" in stdout
    assert store.read_bytes() == before

    code, stdout, stderr = _call(capsys, "validate", "--store", str(store))
    assert (code, stderr) == (0, "")
    assert "retained_runs=1; revision=1; next_sequence=2" in stdout
    code, stdout, stderr = _call(capsys, "render", "--store", str(store))
    assert (code, stderr) == (0, "")
    lines = stdout.splitlines()
    assert lines[0] == (
        "[ARS-ADJUDICATION-ACTIVITY INSUFFICIENT_HISTORY] "
        "selected_retained_eligible_run_count=1; minimum_required=2; requested_window=10."
    )
    assert lines[-3:] == [COVERAGE, LIMITATION, ADVISORY]
    assert "unavailable_source_count=5 (denominator: 5 source families)" in stdout


def test_all_seven_event_types_occurrence_digest_dedup_and_repeated_hashes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "artifacts"
    state = _terminal_state(root, "run-all-events", extra_completed=("3", "3p"))
    manifest = _seal_and_build(capsys, root, state, _all_event_rows(root))
    store = tmp_path / "activity.json"
    code, _stdout, stderr = _append(capsys, root, store, manifest)
    assert code == 0, stderr
    payload = _load(store)
    run = payload["runs"][0]
    events = [event for source in run["sources"] for event in source["events"]]
    assert {event["event_type"] for event in events} == {
        "author_triage_wont_address",
        "author_triage_not_on_point",
        "compliance_block_override",
        "re_review_verdict_changed",
        "finding_justification_requested",
        "finding_redo_requested",
        "mandatory_checkpoint_non_proceed",
    }
    author_events = run["sources"][0]["events"]
    assert author_events[0]["interaction_sha256"] == _independent_interaction(
        "run-all-events", "AUTHOR-EVENT-ONE"
    )
    assert author_events[1]["interaction_sha256"] == _independent_interaction(
        "run-all-events", "AUTHOR-EVENT-TWO"
    )
    assert author_events[0]["interaction_sha256"] != author_events[1]["interaction_sha256"]
    assert run["sources"][1]["artifact_sha256s"][2] == run["sources"][1]["artifact_sha256s"][3]
    shared = _independent_interaction("run-all-events", "USER-REQUEST-SHARED")
    assert sum(event["interaction_sha256"] == shared for event in events) == 1
    assert any(
        event["event_type"] == "finding_justification_requested"
        and event["interaction_sha256"] == shared
        for event in events
    )
    assert not any(
        event["event_type"] == "mandatory_checkpoint_non_proceed"
        and event["stage"] == "pipeline_stage_3"
        for event in events
    )
    assert {event["stage"] for event in run["sources"][4]["events"]} == set(STAGES) - {
        "pipeline_stage_1",
        "pipeline_stage_3",
        "pipeline_stage_4_5",
    }

    expected_input_digest = _independent_digest(
        b"ars.adjudication-activity.input/1.0\0", _load(manifest)
    )
    assert run["input_receipt_sha256"] == expected_input_digest
    record_without_digest = {
        key: value for key, value in run.items() if key != "record_sha256"
    }
    assert run["record_sha256"] == _independent_digest(
        b"ars.adjudication-activity.run/1.0\0", record_without_digest
    )
    first_author_source_record = {
        "item_id": "REV-001",
        "author_event_id": "AUTHOR-EVENT-ONE",
        "author_triage": "wont_address",
        "input_sha256": "a" * 64,
        "interaction_sha256": author_events[0]["interaction_sha256"],
    }
    assert author_events[0]["source_event_sha256"] == _independent_digest(
        b"ars.adjudication-activity.source-event/1.0\0",
        {
            "source_family": "revision_author_adjudication",
            "source_record": first_author_source_record,
        },
    )
    expected_event_digest = _independent_digest(
        b"ars.adjudication-activity.event-id/1.0\0",
        {
            "run_id": "run-all-events",
            "source_family": "revision_author_adjudication",
            "event_type": author_events[0]["event_type"],
            "stage": author_events[0]["stage"],
            "disposition": author_events[0]["disposition"],
            "interaction_sha256": author_events[0]["interaction_sha256"],
            "source_event_sha256": author_events[0]["source_event_sha256"],
        },
    )
    assert author_events[0]["event_id"] == f"ACTIVITY-EVENT-{expected_event_digest}"


def test_terminal_inventory_is_exact_authority_and_conflicting_retry_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "artifacts"
    state = _terminal_state(root, "run-authority")
    manifest = _seal_and_build(capsys, root, state, _empty_rows())
    store = tmp_path / "activity.json"
    assert _append(capsys, root, store, manifest)[0] == 0

    forged_root = tmp_path / "forged-root"
    forged_state = _terminal_state(forged_root, "run-forged-authority")
    valid_forged_base = _seal_and_build(
        capsys, forged_root, forged_state, _empty_rows()
    )
    forged = _load(valid_forged_base)
    forged["sources"][0] = {
        "source_family": "revision_author_adjudication",
        "capture_state": "unavailable",
        "reason_code": "source_not_provided",
        "artifacts": [],
    }
    forged_path = forged_root / "forged-input.json"
    _write(forged_path, forged)
    before = store.read_bytes()
    code, stdout, stderr = _append(capsys, forged_root, store, forged_path)
    assert code == 3
    assert stdout == ""
    assert "ERROR:INPUT" in stderr
    assert store.read_bytes() == before

    second_root = tmp_path / "second-root"
    second_state = _terminal_state(second_root, "run-authority")
    conflicting = _seal_and_build(
        capsys,
        second_root,
        second_state,
        _empty_rows("unavailable"),
        output_name="different-input.json",
    )
    code, stdout, stderr = _append(capsys, second_root, store, conflicting)
    assert code == 5
    assert stdout == ""
    assert "ERROR:CONFLICT" in stderr
    assert store.read_bytes() == before


def test_delete_gap_range_delete_and_delete_store_recovery(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = tmp_path / "activity.json"
    roots: list[Path] = []
    for ordinal in range(1, 4):
        root = tmp_path / f"root-{ordinal}"
        roots.append(root)
        state = _terminal_state(
            root,
            f"run-{ordinal}",
            pipeline_state="aborted" if ordinal == 2 else "completed",
            current_stage="4p" if ordinal == 2 else "6",
            status="blocked" if ordinal == 2 else "completed",
        )
        manifest = _seal_and_build(capsys, root, state, _empty_rows())
        assert _append(capsys, root, store, manifest)[0] == 0

    raw_hash = hashlib.sha256(store.read_bytes()).hexdigest()
    before = store.read_bytes()
    code, stdout, stderr = _call(
        capsys,
        "delete-runs",
        "--store",
        str(store),
        "--store-id",
        STORE_ID,
        "--expect-store-sha256",
        "0" * 64,
        "--run-id",
        "run-2",
    )
    assert code == 6
    assert stdout == ""
    assert "ERROR:DELETE_CONFIRMATION" in stderr
    assert store.read_bytes() == before
    code, stdout, stderr = _call(
        capsys,
        "delete-runs",
        "--store",
        str(store),
        "--store-id",
        STORE_ID,
        "--expect-store-sha256",
        raw_hash,
        "--run-id",
        "run-2",
    )
    assert (code, stderr) == (0, "")
    assert "deleted_runs=1; revision=4; next_sequence=4" in stdout
    assert [run["append_sequence"] for run in _load(store)["runs"]] == [1, 3]

    raw_hash = hashlib.sha256(store.read_bytes()).hexdigest()
    code, _stdout, stderr = _call(
        capsys,
        "delete-runs",
        "--store",
        str(store),
        "--store-id",
        STORE_ID,
        "--expect-store-sha256",
        raw_hash,
        "--sequence-range",
        "1:3",
    )
    assert code == 0, stderr
    assert _load(store)["next_sequence"] == 4
    store.write_bytes(b'{"corrupt":true}\n')
    corrupt_hash = hashlib.sha256(store.read_bytes()).hexdigest()
    code, stdout, stderr = _call(
        capsys,
        "delete-store",
        "--store",
        str(store),
        "--store-id",
        STORE_ID,
        "--expect-store-sha256",
        corrupt_hash,
        "--confirm",
        "WRONG-TOKEN",
    )
    assert code == 6
    assert stdout == ""
    assert "ERROR:DELETE_CONFIRMATION" in stderr
    assert store.exists()
    code, stdout, stderr = _call(
        capsys,
        "delete-store",
        "--store",
        str(store),
        "--store-id",
        STORE_ID,
        "--expect-store-sha256",
        corrupt_hash,
        "--confirm",
        "DELETE-ADJUDICATION-ACTIVITY-STORE",
    )
    assert (code, stderr) == (0, "")
    assert stdout == "[ARS-ADJUDICATION-ACTIVITY] deleted_store=true\n"
    assert not store.exists()


@pytest.mark.parametrize("window", ["1", "51"])
def test_renderer_rejects_out_of_range_window(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], window: str
) -> None:
    store = tmp_path / "activity.json"
    code, _stdout, _stderr = _call(
        capsys, "init-store", "--store", str(store), "--store-id", STORE_ID
    )
    assert code == 0
    code, stdout, stderr = _call(
        capsys, "render", "--store", str(store), "--window", window
    )
    assert code == 2
    assert stdout == ""
    assert "ERROR:USAGE" in stderr


def test_build_input_rejects_caller_sources_and_input_cap_is_fail_closed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "artifacts"
    state = _terminal_state(root, "run-no-caller-authority")
    output = root / "input.json"
    code, stdout, stderr = _call(
        capsys,
        "build-input",
        "--state",
        str(state),
        "--artifact-root",
        str(root),
        "--store-id",
        STORE_ID,
        "--output",
        str(output),
        "--source-sha256",
        "0" * 64,
    )
    assert code == 2
    assert stdout == ""
    assert "ERROR:USAGE" in stderr
    assert not output.exists()

    oversized = root / "oversized-input.json"
    oversized.write_bytes(b" " * ((1 << 20) + 1))
    store = tmp_path / "activity.json"
    code, stdout, stderr = _append(capsys, root, store, oversized)
    assert code == 5
    assert stdout == ""
    assert "ERROR:CAP" in stderr
    assert not store.exists()


@pytest.mark.parametrize(
    "corrupt",
    [
        b'{"schema_version":"adjudication-activity-store/1.0","schema_version":"duplicate"}\n',
        b"\xef\xbb\xbf{}\n",
        b"{} trailing\n",
        b'{"float":1.5}\n',
    ],
)
def test_store_corruption_fails_closed(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    corrupt: bytes,
) -> None:
    store = tmp_path / "activity.json"
    store.write_bytes(corrupt)
    code, stdout, stderr = _call(capsys, "validate", "--store", str(store))
    assert code == 4
    assert stdout == ""
    assert "ERROR:STORE" in stderr


def test_symlink_artifact_and_lock_contention_fail_without_mutation(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "artifacts"
    target = root / "target.json"
    _write(target, {"fixture": True})
    link = root / "link.json"
    link.symlink_to(target)
    rows = _empty_rows()
    rows[3] = {
        "source_family": "explicit_user_request",
        "capture_state": "captured",
        "reason_code": None,
        "artifacts": [
            _artifact("explicit-log", "explicit_user_request_log", "SOURCE-GROUP-explicit", "link.json")
        ],
    }
    state = _terminal_state(root, "run-path")
    state_before = state.read_bytes()
    with pytest.raises(activity.ActivityError, match="symlink"):
        activity.seal_terminal_inventory(state, root, rows)
    assert state.read_bytes() == state_before

    store = tmp_path / "activity.json"
    assert _call(capsys, "init-store", "--store", str(store), "--store-id", STORE_ID)[0] == 0
    before = store.read_bytes()
    lock_path = store.with_name(store.name + ".lock")
    with lock_path.open("r+b") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        code, stdout, stderr = _call(capsys, "validate", "--store", str(store))
    assert code == 7
    assert stdout == ""
    assert "ERROR:LOCK" in stderr
    assert store.read_bytes() == before


def test_captured_zero_compliance_report_only_is_valid(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "artifacts"
    pass_report = _copy_fixture(root, "compliance_pass.json")
    rows = _empty_rows()
    rows[1] = {
        "source_family": "compliance_report",
        "capture_state": "captured",
        "reason_code": None,
        "artifacts": [
            _artifact("report-only", "compliance_report", "SOURCE-GROUP-pass", pass_report)
        ],
    }
    state = _terminal_state(root, "run-captured-zero")
    manifest = _seal_and_build(capsys, root, state, rows)
    store = tmp_path / "activity.json"
    code, _stdout, stderr = _append(capsys, root, store, manifest)
    assert code == 0, stderr
    compliance = _load(store)["runs"][0]["sources"][1]
    assert compliance["capture_state"] == "captured"
    assert compliance["events"] == []


def test_nonqualifying_compliance_receipt_pair_is_rejected(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "artifacts"
    pass_report = _copy_fixture(root, "compliance_pass.json")
    action = _load(FIXTURES / "compliance_override_action.json")
    action["report_sha256"] = hashlib.sha256((root / pass_report).read_bytes()).hexdigest()
    action_path = root / "sources" / "bad-paired-action.json"
    _write(action_path, action)
    rows = _empty_rows()
    rows[1] = {
        "source_family": "compliance_report",
        "capture_state": "captured",
        "reason_code": None,
        "artifacts": [
            _artifact("plain-report", "compliance_report", "SOURCE-GROUP-bad-pair", pass_report),
            _artifact(
                "forbidden-action",
                "compliance_override_action_receipt",
                "SOURCE-GROUP-bad-pair",
                action_path.relative_to(root).as_posix(),
            ),
        ],
    }
    state = _terminal_state(root, "run-bad-pair")
    activity.seal_terminal_inventory(state, root, rows)
    manifest = root / "input.json"
    store = tmp_path / "activity.json"
    code, stdout, stderr = _call(
        capsys,
        "build-input",
        "--state",
        str(state),
        "--artifact-root",
        str(root),
        "--store-id",
        STORE_ID,
        "--output",
        str(manifest),
    )
    assert code == 3
    assert stdout == ""
    assert "ERROR:SOURCE" in stderr
    assert not store.exists()


def test_exact_retry_ignores_deleted_source_and_terminal_bytes_without_write(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "artifacts"
    pass_report = _copy_fixture(root, "compliance_pass.json")
    rows = _empty_rows()
    rows[1] = {
        "source_family": "compliance_report",
        "capture_state": "captured",
        "reason_code": None,
        "artifacts": [
            _artifact(
                "report-only",
                "compliance_report",
                "SOURCE-GROUP-pass",
                pass_report,
            )
        ],
    }
    state = _terminal_state(root, "run-retry-deleted")
    manifest = _seal_and_build(capsys, root, state, rows)
    store = tmp_path / "activity.json"
    assert _append(capsys, root, store, manifest)[0] == 0
    before_bytes = store.read_bytes()
    before_mtime = store.stat().st_mtime_ns

    (root / pass_report).unlink()
    state.unlink()
    code, stdout, stderr = _append(capsys, root, store, manifest)
    assert (code, stderr) == (0, "")
    assert "already_appended" in stdout
    assert store.read_bytes() == before_bytes
    assert store.stat().st_mtime_ns == before_mtime


def test_short_write_is_completed_and_zero_write_fails_cleanly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = b"short-write-fixture" * 64
    short_path = tmp_path / "short.bin"
    original_write = activity.os.write

    def short_write(fd: int, data: bytes | memoryview) -> int:
        return original_write(fd, data[: max(1, len(data) // 2)])

    monkeypatch.setattr(activity.os, "write", short_write)
    activity._atomic_create(short_path, payload)
    assert short_path.read_bytes() == payload

    zero_path = tmp_path / "zero.bin"
    monkeypatch.setattr(activity.os, "write", lambda _fd, _data: 0)
    with pytest.raises(activity.ActivityError) as caught:
        activity._atomic_create(zero_path, payload)
    assert caught.value.code == "WRITE"
    assert not zero_path.exists()


def test_short_read_is_reassembled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = b"short-read-fixture" * 64
    path = tmp_path / "read.bin"
    path.write_bytes(payload)
    original_read = activity.os.read

    def short_read(fd: int, count: int) -> bytes:
        return original_read(fd, max(1, count // 2))

    monkeypatch.setattr(activity.os, "read", short_read)
    assert activity._read_limited(path, len(payload), code="INPUT") == payload


def test_noncanonical_valid_object_delete_store_recovery(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = tmp_path / "activity.json"
    store.write_bytes(b'{ "z": 1, "a": 2 }\n')
    raw_hash = hashlib.sha256(store.read_bytes()).hexdigest()
    code, stdout, stderr = _call(
        capsys,
        "delete-store",
        "--store",
        str(store),
        "--store-id",
        STORE_ID,
        "--expect-store-sha256",
        raw_hash,
        "--confirm",
        "DELETE-ADJUDICATION-ACTIVITY-STORE",
    )
    assert (code, stderr) == (0, "")
    assert stdout == "[ARS-ADJUDICATION-ACTIVITY] deleted_store=true\n"
    assert not store.exists()


@pytest.mark.parametrize(
    "mutation",
    [
        lambda action: action.__setitem__("override_ordinal", True),
        lambda action: action.__setitem__("scope", [["M4"]]),
    ],
    ids=("boolean-ordinal", "unhashable-scope"),
)
def test_compliance_bad_ordinal_or_scope_is_bounded_source_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    mutation: Callable[[dict[str, Any]], None],
) -> None:
    root = tmp_path / "artifacts"
    run_id = "run-compliance-edge"
    state = _terminal_state(root, run_id)
    activity.seal_terminal_inventory(
        state, root, _compliance_rows(root, run_id, mutation)
    )
    output = root / "input.json"
    code, stdout, stderr = _call(
        capsys,
        "build-input",
        "--state",
        str(state),
        "--artifact-root",
        str(root),
        "--store-id",
        STORE_ID,
        "--output",
        str(output),
    )
    assert code == 3
    assert stdout == ""
    assert "ERROR:SOURCE" in stderr
    assert "Traceback" not in stderr
    assert len(stderr.rstrip("\n").splitlines()) == 1
    assert len(stderr.rstrip("\n")) <= 560
    assert not output.exists()


@pytest.mark.parametrize("mandatory", [False, True], ids=("finding-id", "checkpoint-id"))
def test_129_character_finding_or_checkpoint_id_is_rejected(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    mandatory: bool,
) -> None:
    root = tmp_path / "artifacts"
    run_id = f"run-long-{'checkpoint' if mandatory else 'finding'}"

    def mutate(record: dict[str, Any]) -> None:
        record["checkpoint_id" if mandatory else "finding_id"] = "X" * 129

    state = _terminal_state(root, run_id)
    activity.seal_terminal_inventory(
        state,
        root,
        _single_log_rows(root, run_id, mandatory=mandatory, mutate_record=mutate),
    )
    output = root / "input.json"
    code, stdout, stderr = _call(
        capsys,
        "build-input",
        "--state",
        str(state),
        "--artifact-root",
        str(root),
        "--store-id",
        STORE_ID,
        "--output",
        str(output),
    )
    assert code == 3
    assert stdout == ""
    assert "ERROR:SOURCE" in stderr
    assert not output.exists()


def test_explicit_and_mandatory_raw_record_aggregate_4097_is_rejected(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "artifacts"
    run_id = "run-aggregate-4097"
    explicit_id = "EXPLICIT-1"
    explicit = {
        "schema_version": "adjudication-explicit-user-request-log/1.0",
        "run_id": run_id,
        "records": [
            {
                "request_id": "REQUEST-1",
                "actor_role": "user",
                "source": "explicit_session_user_action",
                "action": "justify_finding",
                "stage": "pipeline_stage_3",
                "finding_id": "REV-001",
                "interaction_id": explicit_id,
                "interaction_sha256": _independent_interaction(run_id, explicit_id),
            }
        ],
    }
    mandatory_records = []
    for ordinal in range(4096):
        interaction_id = f"MANDATORY-{ordinal}"
        mandatory_records.append(
            {
                "response_id": f"RESPONSE-{ordinal}",
                "checkpoint_id": f"CHECKPOINT-{ordinal}",
                "checkpoint_type": "MANDATORY",
                "actor_role": "user",
                "source": "explicit_session_user_action",
                "stage": "pipeline_stage_4_5",
                "disposition": "proceed",
                "interaction_id": interaction_id,
                "interaction_sha256": _independent_interaction(run_id, interaction_id),
            }
        )
    mandatory = {
        "schema_version": "adjudication-mandatory-checkpoint-log/1.0",
        "run_id": run_id,
        "records": mandatory_records,
    }
    explicit_path = root / "sources" / "explicit-4097.json"
    mandatory_path = root / "sources" / "mandatory-4097.json"
    _write(explicit_path, explicit)
    _write(mandatory_path, mandatory)
    rows = _empty_rows()
    rows[3] = {
        "source_family": "explicit_user_request",
        "capture_state": "captured",
        "reason_code": None,
        "artifacts": [
            _artifact(
                "explicit-log",
                "explicit_user_request_log",
                "SOURCE-GROUP-explicit",
                explicit_path.relative_to(root).as_posix(),
            )
        ],
    }
    rows[4] = {
        "source_family": "mandatory_checkpoint_response",
        "capture_state": "captured",
        "reason_code": None,
        "artifacts": [
            _artifact(
                "mandatory-log",
                "mandatory_checkpoint_response_log",
                "SOURCE-GROUP-mandatory",
                mandatory_path.relative_to(root).as_posix(),
            )
        ],
    }
    state = _terminal_state(root, run_id)
    activity.seal_terminal_inventory(state, root, rows)
    output = root / "input.json"
    code, stdout, stderr = _call(
        capsys,
        "build-input",
        "--state",
        str(state),
        "--artifact-root",
        str(root),
        "--store-id",
        STORE_ID,
        "--output",
        str(output),
    )
    assert code == 5
    assert stdout == ""
    assert "ERROR:CAP" in stderr
    assert not output.exists()


def test_lone_surrogate_is_bounded_store_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = tmp_path / "activity.json"
    store.write_bytes(b'{"surrogate":"\\ud800"}\n')
    code, stdout, stderr = _call(capsys, "validate", "--store", str(store))
    assert code == 4
    assert stdout == ""
    assert "ERROR:STORE" in stderr
    assert "Traceback" not in stderr
    assert len(stderr.rstrip("\n").splitlines()) == 1
    assert len(stderr.rstrip("\n")) <= 560


def test_author_store_three_hashes_is_rejected(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "artifacts"
    paths = [
        _copy_fixture(root, "author_stage3_input.json"),
        _copy_fixture(root, "author_stage3.json"),
    ]
    rows = _empty_rows()
    rows[0] = {
        "source_family": "revision_author_adjudication",
        "capture_state": "captured",
        "reason_code": None,
        "artifacts": [
            _artifact("author-input", "author_adjudication_input", "SOURCE-GROUP-author", paths[0], "pipeline_stage_3"),
            _artifact("author-output", "author_adjudication", "SOURCE-GROUP-author", paths[1], "pipeline_stage_3"),
        ],
    }
    state = _terminal_state(root, "run-author-three-hashes", extra_completed=("3",))
    manifest = _seal_and_build(capsys, root, state, rows)
    store = tmp_path / "activity.json"
    assert _append(capsys, root, store, manifest)[0] == 0
    payload = _load(store)
    hashes = payload["runs"][0]["sources"][0]["artifact_sha256s"]
    hashes.append(hashes[-1])
    _recompute_record(payload["runs"][0])
    _write(store, payload)
    code, stdout, stderr = _call(capsys, "validate", "--store", str(store))
    assert code == 4
    assert stdout == ""
    assert "ERROR:STORE" in stderr


def test_store_next_sequence_cannot_exceed_revision_plus_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "artifacts"
    state = _terminal_state(root, "run-next-sequence")
    manifest = _seal_and_build(capsys, root, state, _empty_rows())
    store = tmp_path / "activity.json"
    assert _append(capsys, root, store, manifest)[0] == 0
    payload = _load(store)
    assert payload["revision"] == 1
    payload["next_sequence"] = 3
    _write(store, payload)
    code, stdout, stderr = _call(capsys, "validate", "--store", str(store))
    assert code == 4
    assert stdout == ""
    assert "ERROR:STORE" in stderr


def _assert_re_review_mutation_rejected(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    mutation: Callable[[dict[str, Any], dict[str, Any]], None],
) -> None:
    root = tmp_path / "artifacts"
    state = _terminal_state(root, "run-rereview-negative")
    rows = _re_review_rows(root, mutation)
    activity.seal_terminal_inventory(state, root, rows)
    output = root / "input.json"
    code, stdout, stderr = _call(
        capsys,
        "build-input",
        "--state",
        str(state),
        "--artifact-root",
        str(root),
        "--store-id",
        STORE_ID,
        "--output",
        str(output),
    )
    assert code == 3
    assert stdout == ""
    assert "ERROR:SOURCE" in stderr
    assert not output.exists()


def test_re_review_no_change_adjustment_is_rejected(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    def mutate(_verdict: dict[str, Any], trace: dict[str, Any]) -> None:
        reapplication = trace["reapplications"][0]
        reapplication["reapplied_verdict"] = "FULLY_ADDRESSED"
        adjustment = trace["adjustments"][0]
        adjustment["from_verdict"] = "FULLY_ADDRESSED"
        adjustment["to_verdict"] = "FULLY_ADDRESSED"
        trace["rows"][0].update(
            {"verified": "YES", "status": "FULLY_ADDRESSED", "final_verdict": "FULLY_ADDRESSED"}
        )

    _assert_re_review_mutation_rejected(tmp_path, capsys, mutate)


def test_re_review_adjustment_endpoints_must_mirror_reapplication(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    def mutate(_verdict: dict[str, Any], trace: dict[str, Any]) -> None:
        trace["adjustments"][0]["from_verdict"] = "PARTIALLY_ADDRESSED"

    _assert_re_review_mutation_rejected(tmp_path, capsys, mutate)


def test_re_review_reapplication_and_adjustment_are_single_use(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    def mutate(verdict: dict[str, Any], trace: dict[str, Any]) -> None:
        second_dissent = copy.deepcopy(verdict["dissents"][0])
        second_dissent["dissent_id"] = "DIS-2"
        verdict["dissents"].append(second_dissent)
        second_adjudication = copy.deepcopy(trace["dissent_adjudications"][0])
        second_adjudication["dissent_id"] = "DIS-2"
        trace["dissent_adjudications"].append(second_adjudication)
        trace["reapplications"][0]["answer_refs"].append("adjudication:DIS-2")

    _assert_re_review_mutation_rejected(tmp_path, capsys, mutate)


def test_seal_rejects_invalid_artifact_id_without_state_write(tmp_path: Path) -> None:
    root = tmp_path / "artifacts"
    report = _copy_fixture(root, "compliance_pass.json")
    rows = _empty_rows()
    rows[1] = {
        "source_family": "compliance_report",
        "capture_state": "captured",
        "reason_code": None,
        "artifacts": [
            _artifact(
                "invalid artifact id",
                "compliance_report",
                "SOURCE-GROUP-invalid-id",
                report,
            )
        ],
    }
    state = _terminal_state(root, "run-invalid-artifact-id")
    before = state.read_bytes()
    with pytest.raises(activity.ActivityError) as caught:
        activity.seal_terminal_inventory(state, root, rows)
    assert caught.value.code == "SOURCE"
    assert state.read_bytes() == before


def test_renderer_empty_one_two_full_golden_and_mixed_denominators(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = tmp_path / "activity.json"
    assert _call(
        capsys, "init-store", "--store", str(store), "--store-id", STORE_ID
    )[0] == 0
    code, stdout, stderr = _call(capsys, "render", "--store", str(store))
    assert (code, stderr) == (0, "")
    assert stdout == "\n".join(
        [
            "[ARS-ADJUDICATION-ACTIVITY INSUFFICIENT_HISTORY] selected_retained_eligible_run_count=0; minimum_required=2; requested_window=10.",
            "[ARS-ADJUDICATION-ACTIVITY COUNTS] adjudication_count=0 (denominator: 0 retained eligible terminal run records); overturn_count=0 (denominator: 0 recorded adjudications); unavailable_run_count=0 (denominator: 0 retained eligible terminal run records).",
            COVERAGE,
            LIMITATION,
            ADVISORY,
            "",
        ]
    )

    root_one = tmp_path / "root-one"
    pass_report = _copy_fixture(root_one, "compliance_pass.json")
    mixed_rows = _empty_rows()
    mixed_rows[0] = {
        "source_family": "revision_author_adjudication",
        "capture_state": "unavailable",
        "reason_code": "source_not_provided",
        "artifacts": [],
    }
    mixed_rows[1] = {
        "source_family": "compliance_report",
        "capture_state": "captured",
        "reason_code": None,
        "artifacts": [
            _artifact("report-only", "compliance_report", "SOURCE-GROUP-pass", pass_report)
        ],
    }
    state_one = _terminal_state(root_one, "run-mixed-zero")
    manifest_one = _seal_and_build(capsys, root_one, state_one, mixed_rows)
    assert _append(capsys, root_one, store, manifest_one)[0] == 0
    code, stdout, stderr = _call(capsys, "render", "--store", str(store))
    assert (code, stderr) == (0, "")
    assert stdout == "\n".join(
        [
            "[ARS-ADJUDICATION-ACTIVITY INSUFFICIENT_HISTORY] selected_retained_eligible_run_count=1; minimum_required=2; requested_window=10.",
            "[ARS-ADJUDICATION-ACTIVITY COUNTS] adjudication_count=0 (denominator: 1 retained eligible terminal run records); overturn_count=0 (denominator: 0 recorded adjudications); unavailable_run_count=1 (denominator: 1 retained eligible terminal run records).",
            'sequence=1; run_id="run-mixed-zero"; terminal_state=completed; adjudication_count=0 (denominator: 1 retained eligible terminal run record); overturn_count=0 (denominator: 0 recorded adjudications); unavailable_source_count=1 (denominator: 5 source families).',
            COVERAGE,
            LIMITATION,
            ADVISORY,
            "",
        ]
    )

    root_two = tmp_path / "root-two"
    state_two = _terminal_state(root_two, "run-not-applicable")
    manifest_two = _seal_and_build(capsys, root_two, state_two, _empty_rows())
    assert _append(capsys, root_two, store, manifest_two)[0] == 0
    code, stdout, stderr = _call(capsys, "render", "--store", str(store))
    assert (code, stderr) == (0, "")
    assert stdout == "\n".join(
        [
            "[ARS-ADJUDICATION-ACTIVITY] selected_retained_eligible_run_count=2; requested_window=10; adjudication_count=0 (denominator: 2 retained eligible terminal run records); overturn_count=0 (denominator: 0 recorded adjudications); unavailable_run_count=1 (denominator: 2 retained eligible terminal run records).",
            'sequence=1; run_id="run-mixed-zero"; terminal_state=completed; adjudication_count=0 (denominator: 1 retained eligible terminal run record); overturn_count=0 (denominator: 0 recorded adjudications); unavailable_source_count=1 (denominator: 5 source families).',
            'sequence=2; run_id="run-not-applicable"; terminal_state=completed; adjudication_count=0 (denominator: 1 retained eligible terminal run record); overturn_count=0 (denominator: 0 recorded adjudications); unavailable_source_count=0 (denominator: 5 source families).',
            COVERAGE,
            LIMITATION,
            ADVISORY,
            "",
        ]
    )


@pytest.mark.parametrize(
    ("pipeline_state", "raw_stage", "status"),
    [("completed", "6", "skipped")]
    + [("aborted", raw_stage, "blocked") for raw_stage in activity.RAW_TO_STAGE],
)
def test_completed_stage6_skipped_and_every_aborted_stage_replay(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    pipeline_state: str,
    raw_stage: str,
    status: str,
) -> None:
    safe_stage = raw_stage.replace(".", "_")
    root = tmp_path / "artifacts"
    run_id = f"run-{pipeline_state}-{safe_stage}"
    state = _terminal_state(
        root,
        run_id,
        pipeline_state=pipeline_state,
        current_stage=raw_stage,
        status=status,
    )
    manifest = _seal_and_build(capsys, root, state, _empty_rows())
    store = tmp_path / "activity.json"
    code, _stdout, stderr = _append(capsys, root, store, manifest)
    assert code == 0, stderr
    run = _load(store)["runs"][0]
    assert run["terminal_state"] == pipeline_state
    assert run["terminal_stage"] == activity.RAW_TO_STAGE[raw_stage]


def test_delete_store_identity_swap_is_detected_before_unlink(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = tmp_path / "activity.json"
    assert _call(
        capsys, "init-store", "--store", str(store), "--store-id", STORE_ID
    )[0] == 0
    original_hash = hashlib.sha256(store.read_bytes()).hexdigest()
    replacement = tmp_path / "replacement.json"
    replacement_bytes = b'{"replacement":true}\n'
    replacement.write_bytes(replacement_bytes)
    displaced = tmp_path / "displaced-original.json"
    original_assert = activity._assert_identity
    swapped = False

    def swap_then_assert(path: Path, expected: tuple[int, int, int]) -> None:
        nonlocal swapped
        if not swapped:
            path.replace(displaced)
            replacement.replace(path)
            swapped = True
        original_assert(path, expected)

    monkeypatch.setattr(activity, "_assert_identity", swap_then_assert)
    code, stdout, stderr = _call(
        capsys,
        "delete-store",
        "--store",
        str(store),
        "--store-id",
        STORE_ID,
        "--expect-store-sha256",
        original_hash,
        "--confirm",
        "DELETE-ADJUDICATION-ACTIVITY-STORE",
    )
    assert code == 5
    assert stdout == ""
    assert "ERROR:CONFLICT" in stderr
    assert store.read_bytes() == replacement_bytes
    assert displaced.exists()
