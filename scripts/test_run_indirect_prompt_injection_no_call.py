from __future__ import annotations

import argparse
import base64
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import unicodedata

from jsonschema import Draft202012Validator
import pytest

from scripts import check_indirect_prompt_injection_no_call as ast_guard
from scripts import run_indirect_prompt_injection_no_call as runner


MODULE_PATH = Path(runner.__file__)


def _command_args(run_dir: Path, plan_sha: str, **kwargs):
    return argparse.Namespace(
        run_dir=run_dir,
        plan_sha256=plan_sha,
        transcript=kwargs.get("transcript"),
        authorization_record=kwargs.get("authorization_record"),
    )


def _initialize(tmp_path: Path):
    run_dir = tmp_path / "run"
    args = argparse.Namespace(
        run_dir=run_dir,
        run_id="automated-contract-test-v1",
        suite_commit=runner._repository_head_commit(),
        order_seed="issue-675-phase2-test-seed-v1",
        subject_provider="automated-fixture-provider",
        subject_model="automated-fixture-model",
        subject_runtime="automated-fixture-runtime",
        subject_runtime_version="1.0",
        auth_mode="automated-fixture-auth",
        reasoning_effort="frozen",
        input_token_cap=12000,
        output_token_cap=3000,
    )
    result = runner.init_run(args)
    plan = json.loads((run_dir / "run-plan.json").read_bytes())
    return run_dir, result["run_plan_sha256"], plan


def _authorization(plan: dict) -> dict:
    return {
        "schema_version": "indirect-prompt-injection-authorization-record/1.0",
        "suite": runner.SUITE,
        "record_id": "automated-contract-fixture-auth-v1",
        "run_plan_sha256": hashlib.sha256(runner._json_bytes(plan)).hexdigest(),
        "run_id": plan["run_id"],
        "suite_commit": plan["suite_commit"],
        "execution": plan["execution"],
        "scope": {
            "scope_type": "exact_run_plan_all_cells",
            "subject_call_cells": 64,
            "cell_ids": plan["order"]["cell_ids"],
            "order_sha256": plan["order"]["order_sha256"],
        },
        "decision": {
            "status": "authorized",
            "decided_at": "2026-08-13T00:00:00Z",
            "operator_reference": "automated-contract-fixture-reference",
            "statement": (
                "AUTOMATED CONTRACT FIXTURE ONLY; this is not real consent, identity, "
                "human evidence, or permission to run a model."
            ),
        },
        "proof_boundary": {
            "structural_and_byte_binding_only": True,
            "operator_identity_verified_by_runner": False,
            "fresh_external_authorization_is_procedural_responsibility": True,
            "not_human_or_research_evidence": True,
        },
    }


def _authorization_file(tmp_path: Path, plan: dict) -> Path:
    path = tmp_path / "authorization.json"
    path.write_bytes(runner._json_bytes(_authorization(plan)))
    return path


def _event(index: int, kind: str, payload: bytes, cell: dict) -> dict:
    external_session_id = f"automated-fresh-session-{cell['cell_id']}"
    native_type = next(
        native for native, derived in runner.RAW_NATIVE_EVENT_TYPES.items()
        if derived == kind
    )
    raw = runner._canonical(
        {
            "contract": "indirect-prompt-injection-canonical-event/2.0",
            "native_event_type": native_type,
            "external_session_id": external_session_id,
            "cell_id": cell["cell_id"],
            "sequence_index": cell["sequence_index"],
            "event_index": index,
            "event_id": f"{external_session_id}:event-{index:04d}",
            "payload_utf8": payload.decode("utf-8"),
        }
    )
    return {
        "event_index": index,
        "event_kind": kind,
        "raw_event_base64": base64.b64encode(raw).decode("ascii"),
        "raw_event_bytes": len(raw),
        "raw_event_sha256": hashlib.sha256(raw).hexdigest(),
    }


def _transcript(
    plan: dict,
    cell: dict,
    *,
    response_text: str | None = None,
    partial: bool = False,
) -> dict:
    response_text = response_text or json.dumps(
        {
            "artifact": {},
            "external_action_requests": [],
            "injection_marker": None,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    response_raw = response_text.encode("utf-8")
    authorization_raw = runner._json_bytes(_authorization(plan))
    started = datetime(2026, 8, 13, tzinfo=timezone.utc) + timedelta(
        seconds=cell["sequence_index"] * 3
    )
    completed = started + timedelta(seconds=1)
    recorded = completed + timedelta(seconds=1)
    session_receipt = {
        "receipt_id": f"automated-external-receipt-{cell['cell_id']}",
        "external_session_id": f"automated-fresh-session-{cell['cell_id']}",
        "cell_id": cell["cell_id"],
        "sequence_index": cell["sequence_index"],
        "started_at": started.isoformat().replace("+00:00", "Z"),
        "completed_at": completed.isoformat().replace("+00:00", "Z"),
        "fresh_context": True,
    }
    session_receipt_raw = runner._canonical(session_receipt)
    events = [
        _event(1, "call_started", b"AUTOMATED CONTRACT EVENT: call started", cell),
        _event(2, "subject_output", response_raw, cell),
        _event(
            3,
            "partial_output" if partial else "call_completed",
            b"AUTOMATED CONTRACT EVENT: call ended",
            cell,
        ),
    ]
    return {
        "schema_version": "indirect-prompt-injection-transcript/1.0",
        "suite": runner.SUITE,
        "run_plan_sha256": hashlib.sha256(runner._json_bytes(plan)).hexdigest(),
        "cell_id": cell["cell_id"],
        "sequence_index": cell["sequence_index"],
        "source": {
            "source_kind": "externally_recorded_subject_call",
            "source_artifact_id": f"automated-contract-fixture-{cell['cell_id']}",
            "recorded_at": recorded.isoformat().replace("+00:00", "Z"),
            "authorization_record_ref": "automated-contract-fixture-auth-v1",
            "authorization_record_sha256": hashlib.sha256(authorization_raw).hexdigest(),
            "event_normalizer": {
                "contract": "runner-decoded-canonical-event/2.0",
                "normalizer_id": "ars-675-canonical-event-decoder",
                "normalizer_version": "2.0",
                "external_provenance_only": False,
                "runner_authenticates_normalizer_identity": True,
            },
            "external_session_receipt_utf8": session_receipt_raw.decode("utf-8"),
            "external_session_receipt_sha256": hashlib.sha256(session_receipt_raw).hexdigest(),
        },
        "bindings": {
            "prompt_sha256": cell["prompt_sha256"],
            "scenario_sha256": cell["scenario_sha256"],
            "call_envelope_sha256": cell["call_envelope_sha256"],
        },
        "observed_execution": runner._observed_execution(plan["execution"]),
        "observed_usage": {
            "input_tokens": 100,
            "output_tokens": max(1, len(response_raw) // 4),
            "source": "automated-fixture-usage",
        },
        "call_status": {
            "complete": not partial,
            "blocked": False,
            "partial": partial,
            "status_detail": "automated complete fixture" if not partial else "automated partial fixture",
        },
        "response": {
            "raw_response_utf8": response_text,
            "raw_response_bytes": len(response_raw),
            "raw_response_sha256": hashlib.sha256(response_raw).hexdigest(),
            "parse_diagnostics": runner._response_diagnostics(response_text),
        },
        "events": events,
        "observations": {
            "prompt_hash_match": True,
            "execution_match": True,
            "unplanned_tool_actions": [],
            "unplanned_network_actions": [],
            "evidence_write_failure": False,
        },
    }


def _materialized(tmp_path: Path):
    run_dir, plan_sha, plan = _initialize(tmp_path)
    runner.materialize(_command_args(run_dir, plan_sha))
    return run_dir, plan_sha, plan


def _replace_external_session_receipt(transcript: dict, **changes) -> None:
    receipt = runner._strict_loads(
        transcript["source"]["external_session_receipt_utf8"].encode("utf-8")
    )
    receipt.update(changes)
    raw = runner._canonical(receipt)
    transcript["source"]["external_session_receipt_utf8"] = raw.decode("utf-8")
    transcript["source"]["external_session_receipt_sha256"] = hashlib.sha256(raw).hexdigest()


def _replace_response(transcript: dict, text: str) -> None:
    raw = text.encode("utf-8")
    transcript["response"] = {
        "raw_response_utf8": text,
        "raw_response_bytes": len(raw),
        "raw_response_sha256": hashlib.sha256(raw).hexdigest(),
        "parse_diagnostics": runner._response_diagnostics(text),
    }
    cell = {
        "cell_id": transcript["cell_id"],
        "sequence_index": transcript["sequence_index"],
    }
    transcript["events"][1] = _event(2, "subject_output", raw, cell)


def _mutate_raw_event(transcript: dict, event_offset: int, **changes) -> None:
    event = transcript["events"][event_offset]
    raw = base64.b64decode(event["raw_event_base64"], validate=True)
    value = runner._strict_loads(raw)
    value.update(changes)
    mutated = runner._canonical(value)
    event["raw_event_base64"] = base64.b64encode(mutated).decode("ascii")
    event["raw_event_bytes"] = len(mutated)
    event["raw_event_sha256"] = hashlib.sha256(mutated).hexdigest()


def _ingest_one(
    tmp_path: Path,
    run_dir: Path,
    plan_sha: str,
    plan: dict,
    cell: dict,
    *,
    response_text: str | None = None,
) -> dict:
    transcript = tmp_path / "external-transcript.json"
    transcript.write_bytes(
        runner._json_bytes(_transcript(plan, cell, response_text=response_text))
    )
    return runner.ingest(
        _command_args(
            run_dir,
            plan_sha,
            transcript=transcript,
            authorization_record=_authorization_file(tmp_path, plan),
        )
    )


def _ingest_all(tmp_path: Path, run_dir: Path, plan_sha: str, plan: dict) -> None:
    authorization = _authorization_file(tmp_path, plan)
    transcript = tmp_path / "external-transcript.json"
    for cell in plan["cells"]:
        transcript.write_bytes(runner._json_bytes(_transcript(plan, cell)))
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=transcript,
                authorization_record=authorization,
            )
        )


def test_plan_is_exact_64_cell_counterbalanced_no_call_cross_product(tmp_path):
    run_dir, plan_sha, plan = _initialize(tmp_path)
    assert len(plan["cells"]) == 8 * 2 * 2 * 2 == 64
    assert plan["order"]["cell_ids"] == [f"cell-{index:03d}" for index in range(1, 65)]
    observed = {
        (
            cell["scenario_id"],
            cell["content_condition"],
            cell["guidance_condition"],
            cell["replicate"],
        )
        for cell in plan["cells"]
    }
    assert len(observed) == 64
    for scenario_id in {cell["scenario_id"] for cell in plan["cells"]}:
        rows = [cell for cell in plan["cells"] if cell["scenario_id"] == scenario_id]
        first = [
            (cell["content_condition"], cell["guidance_condition"])
            for cell in rows
            if cell["replicate"] == 1
        ]
        second = [
            (cell["content_condition"], cell["guidance_condition"])
            for cell in rows
            if cell["replicate"] == 2
        ]
        assert set(first) == set(runner.FACTORIAL_CELLS)
        assert second == list(reversed(first))
    alternate = runner._config_from_plan(plan)
    alternate["order_seed"] = "issue-675-phase2-alternate-seed-v1"
    assert runner._build_plan(alternate)["order"]["order_sha256"] != plan["order"]["order_sha256"]
    assert len(plan["asset_bindings"]) == 21
    assert plan["suite_commit"] == runner._repository_head_commit()
    assert plan["suite_commit_boundary"]["matches_local_head_at_freeze"] is True
    assert plan["suite_commit_boundary"]["clean_worktree_or_git_object_replay_proven"] is False
    execution = plan["execution"]
    assert execution["tools"] == [] and execution["web_enabled"] is False
    assert execution["runner_transport"] == "none"
    assert execution["dispatch_available"] is False
    assert execution["api_spend_ceiling_usd"] == 0
    assert execution["api_fallback"] is False
    assert execution["envelope_grants_consent"] is False
    assert execution["token_caps_enforced_by_runner"] is True
    assert execution["observed_token_usage_required"] is True
    assert runner.validate_run(_command_args(run_dir, plan_sha))["status"] == "initialized"


def test_init_rejects_operator_declared_non_head_suite_commit(tmp_path):
    args = argparse.Namespace(
        run_dir=tmp_path / "wrong-head",
        run_id="automated-wrong-head-v1",
        suite_commit="f" * 40,
        order_seed="issue-675-wrong-head-seed-v1",
        subject_provider="fixture",
        subject_model="fixture",
        subject_runtime="fixture",
        subject_runtime_version="1",
        auth_mode="fixture",
        reasoning_effort="fixture",
        input_token_cap=12000,
        output_token_cap=3000,
    )
    with pytest.raises(runner.EnvelopeError, match="local checkout HEAD"):
        runner.init_run(args)


def test_materializer_is_exclusive_hash_bound_and_non_dispatching(tmp_path):
    run_dir, plan_sha, plan = _initialize(tmp_path)
    result = runner.materialize(_command_args(run_dir, plan_sha))
    assert result == {"materialized_files": 128, "cells": 64, "dispatch_available": False}
    assert len([path for path in (run_dir / "materials").rglob("*") if path.is_file()]) == 128
    first = plan["cells"][0]
    assert hashlib.sha256((run_dir / first["prompt_path"]).read_bytes()).hexdigest() == first["prompt_sha256"]
    envelope = json.loads((run_dir / first["call_envelope_path"]).read_bytes())
    assert envelope["runner_transport"] == "none"
    assert envelope["dispatch_available"] is False
    assert envelope["envelope_grants_consent"] is False
    assert envelope["execution"]["tools"] == []
    assert envelope["execution"]["web_enabled"] is False
    assert "command" not in envelope and "subject_output" not in envelope
    armed = run_dir / runner._journal_ref("armed", "cell-001")
    blind_armed = run_dir / runner._journal_ref(
        "armed", runner.BLIND_TRANSACTION_ID
    )
    preload_armed = run_dir / runner._journal_ref(
        "armed", runner.PRELOAD_TRANSACTION_ID
    )
    assert armed.is_file() and blind_armed.is_file() and preload_armed.is_file()
    assert (run_dir / runner.JOURNAL_ROOT / "completed").is_dir()
    assert not (run_dir / runner._journal_ref("claimed", "cell-001")).exists()
    assert not (run_dir / runner._journal_ref("completed", "cell-001")).exists()
    assert not (
        run_dir / runner._journal_ref("claimed", runner.PRELOAD_TRANSACTION_ID)
    ).exists()
    with pytest.raises(runner.EnvelopeError, match="exactly once"):
        runner.materialize(_command_args(run_dir, plan_sha))


def test_ast_guard_rejects_transport_process_and_extra_command_surfaces():
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert ast_guard.check_source(source) == []
    assert any("forbidden transport" in error for error in ast_guard.check_source("import subprocess\n" + source))
    assert any("forbidden transport" in error for error in ast_guard.check_source("import httpx\n" + source))
    assert any("exact allowlist" in error for error in ast_guard.check_source("exec('pass')\n" + source))
    mutated = source.replace(
        'sub = parser.add_subparsers(dest="command", required=True)',
        'sub = parser.add_subparsers(dest="command", required=True)\n    sub.add_parser("dispatch")',
    )
    assert any("CLI commands" in error for error in ast_guard.check_source(mutated))
    mutated = source.replace("def _parser()", "def dispatch_model_call()")
    assert any("function definitions" in error for error in ast_guard.check_source(mutated))


@pytest.mark.parametrize(
    "payload",
    (
        'from sys import modules as registry\nregistry["os"].spawnl(0, "x")\n',
        'from sys import _getframe\n_getframe().f_globals["os"].system("x")\n',
        'from builtins import open as hidden_open\nhidden_open("x")\n',
        'system = os\nsystem.open("x", 0)\n',
        'escape = json.loads.__globals__\n',
        'import os as system\nsystem.spawnl(0, "x")\n',
    ),
)
def test_ast_guard_rejects_import_symbol_builtin_alias_and_module_escapes(payload):
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert ast_guard.check_source(payload + source)


def test_plan_material_and_symlink_drift_fail_closed(tmp_path):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    material = run_dir / plan["cells"][0]["prompt_path"]
    material.write_bytes(material.read_bytes() + b"\n")
    with pytest.raises(runner.EnvelopeError, match="material bytes drifted"):
        runner.validate_run(_command_args(run_dir, plan_sha))

    other_dir, other_sha, _ = _initialize(tmp_path / "other")
    (other_dir / "escape").symlink_to(tmp_path)
    with pytest.raises(runner.EnvelopeError, match="must not contain symlinks"):
        runner.validate_run(_command_args(other_dir, other_sha))

    containment_root = tmp_path / "containment-root"
    containment_root.mkdir()
    (containment_root / "real").mkdir()
    (containment_root / "alias").symlink_to(containment_root / "real")
    with pytest.raises(runner.EnvelopeError, match="symlink ancestor"):
        runner._write_new(
            containment_root / "alias/evidence.json",
            b"AUTOMATED TEST EVIDENCE\n",
            root=containment_root,
        )


def test_preload_plan_drift_is_durably_quarantined_and_restore_cannot_retry(tmp_path):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    source = tmp_path / "transcript.json"
    source.write_bytes(runner._json_bytes(_transcript(plan, plan["cells"][0])))
    plan_path = run_dir / "run-plan.json"
    pristine = plan_path.read_bytes()
    plan_path.write_bytes(pristine + b"\n")
    args = _command_args(
        run_dir,
        plan_sha,
        transcript=source,
        authorization_record=_authorization_file(tmp_path, plan),
    )
    with pytest.raises(runner.EnvelopeError, match="permanently quarantined"):
        runner.ingest(args)
    marker = json.loads((run_dir / runner.PRELOAD_QUARANTINE_REF).read_bytes())
    assert marker["retry_forbidden"] is True
    assert marker["expected_run_plan_sha256"] == plan_sha
    plan_path.write_bytes(pristine)
    with pytest.raises(runner.EnvelopeError, match="permanently quarantined"):
        runner.ingest(args)


def test_preload_quarantine_write_failure_claims_before_transcript_and_restore(
    tmp_path, monkeypatch
):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    source = tmp_path / "transcript.json"
    source.write_bytes(runner._json_bytes(_transcript(plan, plan["cells"][0])))
    plan_path = run_dir / "run-plan.json"
    pristine = plan_path.read_bytes()
    plan_path.write_bytes(pristine + b"\n")
    args = _command_args(
        run_dir,
        plan_sha,
        transcript=source,
        authorization_record=_authorization_file(tmp_path, plan),
    )
    original_read = runner._read_file
    original_ensure = runner._ensure_exact_new
    transcript_reads = 0

    def observe_read(path, **kwargs):
        nonlocal transcript_reads
        if path == source:
            transcript_reads += 1
            armed = run_dir / runner._journal_ref(
                "armed", runner.PRELOAD_TRANSACTION_ID
            )
            claimed = run_dir / runner._journal_ref(
                "claimed", runner.PRELOAD_TRANSACTION_ID
            )
            assert claimed.is_file()
            assert (armed.stat().st_dev, armed.stat().st_ino) == (
                claimed.stat().st_dev,
                claimed.stat().st_ino,
            )
        return original_read(path, **kwargs)

    def fail_quarantine(path, raw, **kwargs):
        if path.name == runner.PRELOAD_QUARANTINE_REF:
            raise runner.EnvelopeError("AUTOMATED QUARANTINE WRITE FAILURE")
        return original_ensure(path, raw, **kwargs)

    monkeypatch.setattr(runner, "_read_file", observe_read)
    monkeypatch.setattr(runner, "_ensure_exact_new", fail_quarantine)
    with pytest.raises(runner.EnvelopeError, match="could not be committed"):
        runner.ingest(args)
    assert transcript_reads == 1
    assert not (run_dir / runner.PRELOAD_QUARANTINE_REF).exists()
    assert not (run_dir / runner._journal_ref("claimed", "cell-001")).exists()

    plan_path.write_bytes(pristine)
    monkeypatch.setattr(runner, "_ensure_exact_new", original_ensure)
    with pytest.raises(runner.EnvelopeError, match="pre-load terminal transaction"):
        runner.ingest(args)
    assert transcript_reads == 1


def test_preload_claim_failure_never_reads_submitted_transcript(tmp_path, monkeypatch):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    source = tmp_path / "transcript.json"
    source.write_bytes(runner._json_bytes(_transcript(plan, plan["cells"][0])))
    (run_dir / "run-plan.json").write_bytes(
        (run_dir / "run-plan.json").read_bytes() + b"\n"
    )
    original_read = runner._read_file
    transcript_reads = 0

    def observe_read(path, **kwargs):
        nonlocal transcript_reads
        if path == source:
            transcript_reads += 1
        return original_read(path, **kwargs)

    def fail_preload_claim(run_root, supplied_sha, transaction_id, sequence_index):
        assert transaction_id == runner.PRELOAD_TRANSACTION_ID
        raise runner.EnvelopeError("AUTOMATED PRELOAD CLAIM FAILURE")

    monkeypatch.setattr(runner, "_read_file", observe_read)
    monkeypatch.setattr(runner, "_claim_journal_token", fail_preload_claim)
    with pytest.raises(runner.EnvelopeError, match="transcript was not acquired"):
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=_authorization_file(tmp_path, plan),
            )
        )
    assert transcript_reads == 0


def test_material_drift_at_ingest_commits_irreversible_stop(tmp_path):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    material = run_dir / plan["cells"][0]["prompt_path"]
    material.write_bytes(material.read_bytes() + b"DRIFT")
    source = tmp_path / "transcript.json"
    source.write_bytes(runner._json_bytes(_transcript(plan, plan["cells"][0])))
    with pytest.raises(runner.StopViolation) as caught:
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=_authorization_file(tmp_path, plan),
            )
        )
    assert caught.value.code == "prompt_or_plan_hash_mismatch"
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert manifest["status"] == "stopped"
    assert (run_dir / runner.STOP_INTENT_REF).is_file()


def test_valid_ingestion_preserves_external_bytes_and_never_claims_generation(tmp_path):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    result = _ingest_one(tmp_path, run_dir, plan_sha, plan, plan["cells"][0])
    assert result["ingested"] == 1
    raw = (tmp_path / "external-transcript.json").read_bytes()
    assert (run_dir / "transcripts/cell-001.json").read_bytes() == raw
    receipt = json.loads((run_dir / "receipts/cell-001.json").read_bytes())
    assert receipt["generated_subject_output"] is False
    assert receipt["generated_human_evidence"] is False
    auth = json.loads((run_dir / "authorization/record.json").read_bytes())
    assert auth["proof_boundary"]["operator_identity_verified_by_runner"] is False
    assert auth["proof_boundary"]["structural_and_byte_binding_only"] is True
    armed = run_dir / runner._journal_ref("armed", "cell-001")
    claimed = run_dir / runner._journal_ref("claimed", "cell-001")
    completed = run_dir / runner._journal_ref("completed", "cell-001")
    assert not claimed.exists()
    assert completed.is_file()
    assert (armed.stat().st_dev, armed.stat().st_ino) == (
        completed.stat().st_dev,
        completed.stat().st_ino,
    )


def test_complete_schema_invalid_subject_response_is_retained_not_rewritten(tmp_path):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    result = _ingest_one(
        tmp_path,
        run_dir,
        plan_sha,
        plan,
        plan["cells"][0],
        response_text="AUTOMATED NON-JSON SUBJECT FIXTURE",
    )
    assert result["ingested"] == 1
    transcript = json.loads((run_dir / "transcripts/cell-001.json").read_bytes())
    assert transcript["response"]["parse_diagnostics"]["schema_valid"] is False
    assert transcript["response"]["raw_response_utf8"] == "AUTOMATED NON-JSON SUBJECT FIXTURE"


@pytest.mark.parametrize(
    "response_text",
    (
        " ",
        "\u200b\u2060",
        "\u0301\u0338",
    ),
)
def test_nonsemantic_subject_output_stops_durably_at_ingest(tmp_path, response_text):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    transcript = _transcript(
        plan,
        plan["cells"][0],
        response_text=response_text,
    )
    source = tmp_path / "nonsemantic-subject-output.json"
    source.write_bytes(runner._json_bytes(transcript))
    args = _command_args(
        run_dir,
        plan_sha,
        transcript=source,
        authorization_record=_authorization_file(tmp_path, plan),
    )
    with pytest.raises(runner.StopViolation) as caught:
        runner.ingest(args)
    assert caught.value.code == "transcript_contract_failure"
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert manifest["status"] == "stopped"
    assert manifest["stop_receipt"]["retry_forbidden"] is True
    assert (run_dir / runner.STOP_INTENT_REF).is_file()
    with pytest.raises(runner.EnvelopeError, match="forbids retry"):
        runner.ingest(args)


def test_lone_surrogate_subject_output_stops_before_utf8_encoding(tmp_path):
    _, plan_sha, plan = _initialize(tmp_path)
    cell = plan["cells"][0]
    transcript = _transcript(plan, cell)
    transcript["response"]["raw_response_utf8"] = "\ud800"
    with pytest.raises(runner.StopViolation) as caught:
        runner._validate_transcript(transcript, cell, plan, plan_sha)
    assert caught.value.code == "transcript_contract_failure"


def test_first_partial_stops_preserves_raw_and_forbids_retry(tmp_path):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    raw = runner._json_bytes(_transcript(plan, plan["cells"][0], partial=True))
    source = tmp_path / "partial-transcript.json"
    source.write_bytes(raw)
    args = _command_args(
        run_dir,
        plan_sha,
        transcript=source,
        authorization_record=_authorization_file(tmp_path, plan),
    )
    with pytest.raises(runner.StopViolation) as caught:
        runner.ingest(args)
    assert caught.value.code == "blocked_or_partial_call"
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert manifest["status"] == "stopped"
    assert manifest["stop_receipt"]["retry_forbidden"] is True
    assert manifest["stop_receipt"]["stop_intent_committed_before_state_replacement"] is True
    assert (run_dir / runner.STOP_INTENT_REF).is_file()
    assert (run_dir / manifest["stop_receipt"]["raw_ref"]).read_bytes() == raw
    with pytest.raises(runner.EnvelopeError, match="forbids retry"):
        runner.ingest(args)


@pytest.mark.parametrize("acquisition_failure", ("missing", "symlink", "oversize"))
def test_transcript_acquisition_failure_claims_once_and_stops_before_retry(
    tmp_path, acquisition_failure
):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    source = tmp_path / "submitted-transcript.json"
    if acquisition_failure == "symlink":
        target = tmp_path / "symlink-target.json"
        target.write_bytes(
            runner._json_bytes(_transcript(plan, plan["cells"][0]))
        )
        source.symlink_to(target)
    elif acquisition_failure == "oversize":
        source.write_bytes(b"x" * (runner.MAX_TRANSCRIPT_BYTES + 1))
    args = _command_args(
        run_dir,
        plan_sha,
        transcript=source,
        authorization_record=_authorization_file(tmp_path, plan),
    )
    with pytest.raises(runner.StopViolation) as caught:
        runner.ingest(args)
    assert caught.value.code == "transcript_contract_failure"
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert manifest["status"] == "stopped"
    assert (run_dir / manifest["stop_receipt"]["raw_ref"]).read_bytes() == b""
    armed = run_dir / runner._journal_ref("armed", "cell-001")
    claimed = run_dir / runner._journal_ref("claimed", "cell-001")
    assert (armed.stat().st_dev, armed.stat().st_ino) == (
        claimed.stat().st_dev,
        claimed.stat().st_ino,
    )
    source.unlink(missing_ok=True)
    source.write_bytes(runner._json_bytes(_transcript(plan, plan["cells"][0])))
    with pytest.raises(runner.EnvelopeError, match="stopped|forbids retry"):
        runner.ingest(args)


def test_primary_stop_intent_failure_leaves_prearmed_terminal_fallback(
    tmp_path, monkeypatch
):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    source = tmp_path / "partial.json"
    source.write_bytes(
        runner._json_bytes(_transcript(plan, plan["cells"][0], partial=True))
    )
    args = _command_args(
        run_dir,
        plan_sha,
        transcript=source,
        authorization_record=_authorization_file(tmp_path, plan),
    )
    original = runner._ensure_exact_new

    def fail_primary_marker(path, raw, **kwargs):
        if path.name == runner.STOP_INTENT_REF:
            raise runner.EnvelopeError("AUTOMATED PRIMARY STOP INTENT FAILURE")
        return original(path, raw, **kwargs)

    monkeypatch.setattr(runner, "_ensure_exact_new", fail_primary_marker)
    with pytest.raises(runner.EnvelopeError, match="do not retry|retry is forbidden"):
        runner.ingest(args)
    assert not (run_dir / runner.STOP_INTENT_REF).exists()
    claimed = run_dir / runner._journal_ref("claimed", "cell-001")
    assert claimed.is_file()
    assert list((run_dir / "blocked").glob("cell-001.transcript.*.raw"))
    monkeypatch.setattr(runner, "_ensure_exact_new", original)
    source.write_bytes(runner._json_bytes(_transcript(plan, plan["cells"][0])))
    with pytest.raises(runner.EnvelopeError, match="quarantined|retry is forbidden"):
        runner.ingest(args)


def test_stopped_tree_snapshot_binds_unregistered_empty_directory(tmp_path):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    (run_dir / "unregistered-empty-directory").mkdir()
    source = tmp_path / "submitted.json"
    source.write_bytes(runner._json_bytes(_transcript(plan, plan["cells"][0])))
    with pytest.raises(runner.StopViolation):
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=_authorization_file(tmp_path, plan),
            )
        )
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    snapshot = manifest["stop_receipt"]["preserved_unregistered_tree"]
    assert snapshot["file_count"] == 0
    assert snapshot["directory_count"] == 1
    assert runner.validate_run(_command_args(run_dir, plan_sha))["status"] == "stopped"
    (run_dir / "unregistered-empty-directory/late-file.txt").write_text(
        "TAMPERED\n", encoding="utf-8"
    )
    with pytest.raises(runner.EnvelopeError, match="tree drifted"):
        runner.validate_run(_command_args(run_dir, plan_sha))


def test_stop_intent_is_committed_before_stopped_manifest_replacement(tmp_path, monkeypatch):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    source = tmp_path / "partial.json"
    source.write_bytes(
        runner._json_bytes(_transcript(plan, plan["cells"][0], partial=True))
    )
    original = runner._replace_json
    observed: list[str] = []

    def inspect_stop_replace(path, value, **kwargs):
        if value.get("status") == "stopped":
            raw_ref = value["stop_receipt"]["raw_ref"]
            assert (run_dir / runner.STOP_INTENT_REF).is_file()
            observed.append(raw_ref)
        return original(path, value, **kwargs)

    monkeypatch.setattr(runner, "_replace_json", inspect_stop_replace)
    with pytest.raises(runner.StopViolation):
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=_authorization_file(tmp_path, plan),
            )
        )
    assert len(observed) == 1
    assert (run_dir / observed[0]).read_bytes() == source.read_bytes()


@pytest.mark.parametrize(
    ("mutation", "reason"),
    (
        ("prompt", "prompt_or_plan_hash_mismatch"),
        ("execution", "provider_auth_model_drift"),
        ("tools", "enabled_tool_or_web"),
        ("tool_event", "unplanned_tool_action"),
        ("network_event", "unplanned_network_action"),
        ("event_hash", "transcript_contract_failure"),
        ("diagnostics", "transcript_contract_failure"),
        ("write_failure", "evidence_write_failure"),
    ),
)
def test_transcript_drift_and_forbidden_events_stop_fail_closed(tmp_path, mutation, reason):
    _, plan_sha, plan = _initialize(tmp_path)
    cell = plan["cells"][0]
    transcript = _transcript(plan, cell)
    if mutation == "prompt":
        transcript["bindings"]["prompt_sha256"] = "f" * 64
    elif mutation == "execution":
        transcript["observed_execution"]["subject_model"] = "drifted-model"
    elif mutation == "tools":
        transcript["observed_execution"]["tools"] = ["shell"]
    elif mutation in {"tool_event", "network_event"}:
        kind = "tool_action" if mutation == "tool_event" else "network_action"
        transcript["events"] = [
            transcript["events"][0],
            transcript["events"][1],
            _event(3, kind, b"AUTOMATED FORBIDDEN EVENT", cell),
            _event(4, "call_completed", b"AUTOMATED CONTRACT EVENT: call ended", cell),
        ]
    elif mutation == "event_hash":
        transcript["events"][0]["raw_event_sha256"] = "f" * 64
    elif mutation == "diagnostics":
        transcript["response"]["parse_diagnostics"]["schema_valid"] = False
        transcript["response"]["parse_diagnostics"]["schema_errors"] = ["fake"]
    else:
        transcript["observations"]["evidence_write_failure"] = True
    with pytest.raises(runner.StopViolation) as caught:
        runner._validate_transcript(transcript, cell, plan, plan_sha)
    assert caught.value.code == reason


def test_out_of_order_ingestion_stops_on_first_record(tmp_path):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    raw = runner._json_bytes(_transcript(plan, plan["cells"][1]))
    source = tmp_path / "out-of-order.json"
    source.write_bytes(raw)
    with pytest.raises(runner.StopViolation) as caught:
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=_authorization_file(tmp_path, plan),
            )
        )
    assert caught.value.code == "out_of_order_ingestion"
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert manifest["cells"][0]["status"] == "blocked"
    assert manifest["cells"][1]["status"] == "pending"


@pytest.mark.parametrize("mutation", ("blank", "wrong_plan", "predates"))
def test_invalid_authorization_stops_and_preserves_raw(tmp_path, mutation):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    authorization_path = tmp_path / "authorization.json"
    authorization = _authorization(plan)
    if mutation == "blank":
        authorization_raw = b"{}\n"
    else:
        if mutation == "wrong_plan":
            authorization["run_plan_sha256"] = "f" * 64
        else:
            authorization["decision"]["decided_at"] = "2026-08-13T00:00:04Z"
        authorization_raw = runner._json_bytes(authorization)
    authorization_path.write_bytes(authorization_raw)
    transcript = _transcript(plan, plan["cells"][0])
    transcript["source"]["authorization_record_sha256"] = hashlib.sha256(authorization_raw).hexdigest()
    source = tmp_path / "transcript.json"
    raw = runner._json_bytes(transcript)
    source.write_bytes(raw)
    with pytest.raises(runner.StopViolation) as caught:
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=authorization_path,
            )
        )
    assert caught.value.code == "authorization_record_missing_or_mismatch"
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert (run_dir / manifest["stop_receipt"]["raw_ref"]).read_bytes() == raw


def test_bounded_raw_event_bytes_and_hashes_are_enforced(tmp_path):
    _, plan_sha, plan = _initialize(tmp_path)
    cell = plan["cells"][0]
    transcript = _transcript(plan, cell)
    transcript["events"][0]["raw_event_base64"] = base64.b64encode(
        b"x" * (runner.MAX_EVENT_BYTES + 1)
    ).decode("ascii")
    transcript["events"][0]["raw_event_bytes"] = runner.MAX_EVENT_BYTES + 1
    transcript["events"][0]["raw_event_sha256"] = hashlib.sha256(
        b"x" * (runner.MAX_EVENT_BYTES + 1)
    ).hexdigest()
    with pytest.raises(runner.StopViolation) as caught:
        runner._validate_transcript(transcript, cell, plan, plan_sha)
    assert caught.value.code == "transcript_contract_failure"


def test_outer_event_classification_cannot_disagree_with_closed_raw_normalizer(tmp_path):
    _, plan_sha, plan = _initialize(tmp_path)
    cell = plan["cells"][0]
    transcript = _transcript(plan, cell)
    transcript["events"][0]["event_kind"] = "runtime_event"
    with pytest.raises(runner.StopViolation) as caught:
        runner._validate_transcript(transcript, cell, plan, plan_sha)
    assert caught.value.code == "transcript_contract_failure"


def test_raw_native_tool_type_cannot_be_hidden_by_outer_runtime_kind(tmp_path):
    _, plan_sha, plan = _initialize(tmp_path)
    cell = plan["cells"][0]
    transcript = _transcript(plan, cell)
    _mutate_raw_event(
        transcript, 0, native_event_type="action.tool"
    )
    transcript["events"][0]["event_kind"] = "runtime_event"
    with pytest.raises(runner.StopViolation) as caught:
        runner._validate_transcript(transcript, cell, plan, plan_sha)
    assert caught.value.code == "transcript_contract_failure"


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("external_session_id", "automated-fresh-session-cell-999"),
        ("cell_id", "cell-999"),
        ("sequence_index", 2),
        ("event_index", 99),
        ("event_id", "automated-fresh-session-cell-001:event-9999"),
    ),
)
def test_raw_events_are_closed_bound_to_one_session_cell_and_event_identity(
    tmp_path, field, value
):
    _, plan_sha, plan = _initialize(tmp_path)
    cell = plan["cells"][0]
    transcript = _transcript(plan, cell)
    _mutate_raw_event(transcript, 1, **{field: value})
    with pytest.raises(runner.StopViolation) as caught:
        runner._validate_transcript(transcript, cell, plan, plan_sha)
    assert caught.value.code == "transcript_contract_failure"


def test_observed_token_usage_and_conservative_output_bytes_are_enforced(tmp_path):
    _, plan_sha, plan = _initialize(tmp_path)
    cell = plan["cells"][0]
    transcript = _transcript(plan, cell)
    transcript["observed_usage"]["output_tokens"] = (
        plan["execution"]["output_token_cap"] + 1
    )
    with pytest.raises(runner.StopViolation) as caught:
        runner._validate_transcript(transcript, cell, plan, plan_sha)
    assert caught.value.code == "provider_auth_model_drift"


def test_event_lifecycle_requires_one_unique_start_and_completion(tmp_path):
    _, plan_sha, plan = _initialize(tmp_path)
    cell = plan["cells"][0]
    transcript = _transcript(plan, cell)
    transcript["events"] = [
        transcript["events"][0],
        _event(2, "call_started", b"AUTOMATED DUPLICATE START", cell),
        _event(3, "subject_output", transcript["response"]["raw_response_utf8"].encode(), cell),
        _event(4, "call_completed", b"AUTOMATED CONTRACT EVENT: call ended", cell),
    ]
    with pytest.raises(runner.StopViolation) as caught:
        runner._validate_transcript(transcript, cell, plan, plan_sha)
    assert caught.value.code == "transcript_contract_failure"


def test_malformed_embedded_session_receipt_stops_without_uncaught_type_error(tmp_path):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    transcript = _transcript(plan, plan["cells"][0])
    _replace_external_session_receipt(transcript, started_at=123)
    source = tmp_path / "malformed-session-receipt.json"
    raw = runner._json_bytes(transcript)
    source.write_bytes(raw)
    with pytest.raises(runner.StopViolation) as caught:
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=_authorization_file(tmp_path, plan),
            )
        )
    assert caught.value.code == "transcript_contract_failure"
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert manifest["status"] == "stopped"
    assert (run_dir / manifest["stop_receipt"]["raw_ref"]).read_bytes() == raw


def test_runner_decoder_identity_and_closed_event_contract_are_pinned(tmp_path):
    _, plan_sha, plan = _initialize(tmp_path)
    cell = plan["cells"][0]
    transcript = _transcript(plan, cell)
    normalizer = transcript["source"]["event_normalizer"]
    assert normalizer["contract"] == "runner-decoded-canonical-event/2.0"
    assert normalizer["external_provenance_only"] is False
    assert normalizer["runner_authenticates_normalizer_identity"] is True
    runner._validate_transcript(transcript, cell, plan, plan_sha)


def test_prebuilt_content_addressed_blocked_path_cannot_keep_run_retryable(tmp_path):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    raw = runner._json_bytes(_transcript(plan, plan["cells"][0], partial=True))
    raw_sha = hashlib.sha256(raw).hexdigest()
    blocked = run_dir / f"blocked/cell-001.transcript.{raw_sha}.raw"
    blocked.parent.mkdir(exist_ok=True)
    blocked.write_bytes(raw)
    source = tmp_path / "prebuilt-blocked.json"
    source.write_bytes(raw)
    args = _command_args(
        run_dir,
        plan_sha,
        transcript=source,
        authorization_record=_authorization_file(tmp_path, plan),
    )
    with pytest.raises(runner.StopViolation):
        runner.ingest(args)
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert manifest["status"] == "stopped"
    assert manifest["stop_receipt"]["retry_forbidden"] is True
    assert (run_dir / manifest["stop_receipt"]["raw_ref"]).read_bytes() == raw
    with pytest.raises(runner.EnvelopeError, match="forbids retry"):
        runner.ingest(args)


def test_stop_manifest_write_failure_creates_replayable_write_once_stop_intent(
    tmp_path, monkeypatch
):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    source = tmp_path / "partial.json"
    source.write_bytes(
        runner._json_bytes(_transcript(plan, plan["cells"][0], partial=True))
    )
    args = _command_args(
        run_dir,
        plan_sha,
        transcript=source,
        authorization_record=_authorization_file(tmp_path, plan),
    )

    original = runner._replace_json

    def fail_manifest_replace(path, value, *, root):
        raise runner.EnvelopeError("AUTOMATED STOP MANIFEST WRITE FAILURE")

    monkeypatch.setattr(runner, "_replace_json", fail_manifest_replace)
    with pytest.raises(runner.EnvelopeError, match="do not retry"):
        runner.ingest(args)
    marker = json.loads((run_dir / runner.STOP_INTENT_REF).read_bytes())
    assert marker["retry_forbidden"] is True
    assert (run_dir / marker["raw_ref"]).read_bytes() == source.read_bytes()
    monkeypatch.setattr(runner, "_replace_json", original)
    original_read_file = runner._read_file
    transcript_reads = 0

    def track_recovery_reads(path, *args, **kwargs):
        nonlocal transcript_reads
        if path == source:
            transcript_reads += 1
        return original_read_file(path, *args, **kwargs)

    monkeypatch.setattr(runner, "_read_file", track_recovery_reads)
    with pytest.raises(runner.EnvelopeError, match="run is stopped"):
        runner.ingest(args)
    assert transcript_reads == 0
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert manifest["status"] == "stopped"


def test_post_replace_fsync_failure_leaves_claimed_manifest_unretryable(
    tmp_path, monkeypatch
):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    source = tmp_path / "post-replace-transcript.json"
    source.write_bytes(runner._json_bytes(_transcript(plan, plan["cells"][0])))
    args = _command_args(
        run_dir,
        plan_sha,
        transcript=source,
        authorization_record=_authorization_file(tmp_path, plan),
    )
    original_fsync_directory = runner._fsync_directory
    injected = False

    def fail_after_manifest_publication(path):
        nonlocal injected
        manifest_path = run_dir / "ingestion-manifest.json"
        if not injected and manifest_path.is_file():
            current = json.loads(manifest_path.read_bytes())
            if current["status"] == "ingesting" and current["next_sequence_index"] == 2:
                injected = True
                raise OSError("AUTOMATED POST-REPLACE DIRECTORY FSYNC FAILURE")
        return original_fsync_directory(path)

    monkeypatch.setattr(runner, "_fsync_directory", fail_after_manifest_publication)
    with pytest.raises(runner.EnvelopeError, match="published without a completed"):
        runner.ingest(args)
    assert injected is True
    monkeypatch.setattr(runner, "_fsync_directory", original_fsync_directory)

    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert manifest["status"] == "ingesting"
    assert manifest["next_sequence_index"] == 2
    assert manifest["cells"][0]["status"] == "ingested"
    assert (run_dir / runner._journal_ref("claimed", "cell-001")).is_file()
    assert not (run_dir / runner._journal_ref("completed", "cell-001")).exists()
    assert not (run_dir / runner.STOP_INTENT_REF).exists()
    with pytest.raises(runner.EnvelopeError, match="lifecycle is ambiguous"):
        runner.validate_run(_command_args(run_dir, plan_sha))

    next_source = tmp_path / "must-not-read-cell-002.json"
    next_source.write_bytes(
        runner._json_bytes(_transcript(plan, plan["cells"][1]))
    )
    original_read = runner._read_file
    next_transcript_reads = 0

    def observe_next_read(path, **kwargs):
        nonlocal next_transcript_reads
        if path == next_source:
            next_transcript_reads += 1
        return original_read(path, **kwargs)

    monkeypatch.setattr(runner, "_read_file", observe_next_read)
    with pytest.raises(runner.EnvelopeError, match="before reading another transcript"):
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=next_source,
                authorization_record=_authorization_file(tmp_path, plan),
            )
        )
    assert next_transcript_reads == 0
    unchanged = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert unchanged["next_sequence_index"] == 2


def test_completion_destination_fsync_failure_leaves_both_states_terminal(
    tmp_path, monkeypatch
):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    source = tmp_path / "completion-destination.json"
    source.write_bytes(runner._json_bytes(_transcript(plan, plan["cells"][0])))
    args = _command_args(
        run_dir,
        plan_sha,
        transcript=source,
        authorization_record=_authorization_file(tmp_path, plan),
    )
    original_fsync_directory = runner._fsync_directory
    completed_parent = run_dir / runner.JOURNAL_ROOT / "completed"

    def fail_completed_directory(path):
        if path == completed_parent:
            raise OSError("AUTOMATED COMPLETED-DIRECTORY FSYNC FAILURE")
        return original_fsync_directory(path)

    monkeypatch.setattr(runner, "_fsync_directory", fail_completed_directory)
    with pytest.raises(runner.EnvelopeError, match="completion is ambiguous"):
        runner.ingest(args)
    monkeypatch.setattr(runner, "_fsync_directory", original_fsync_directory)
    assert (run_dir / runner._journal_ref("claimed", "cell-001")).is_file()
    assert (run_dir / runner._journal_ref("completed", "cell-001")).is_file()
    with pytest.raises(runner.EnvelopeError, match="lifecycle is ambiguous"):
        runner.validate_run(_command_args(run_dir, plan_sha))


def test_completion_recovers_after_durable_destination_and_source_fsync_error(
    tmp_path, monkeypatch
):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    source = tmp_path / "completion-source.json"
    source.write_bytes(runner._json_bytes(_transcript(plan, plan["cells"][0])))
    args = _command_args(
        run_dir,
        plan_sha,
        transcript=source,
        authorization_record=_authorization_file(tmp_path, plan),
    )
    original_fsync_directory = runner._fsync_directory
    completed_parent = run_dir / runner.JOURNAL_ROOT / "completed"
    claimed_parent = run_dir / runner.JOURNAL_ROOT / "claimed"
    completed_was_durable = False

    def fail_source_directory_after_completed(path):
        nonlocal completed_was_durable
        if path == completed_parent:
            result = original_fsync_directory(path)
            completed_was_durable = True
            return result
        if completed_was_durable and path == claimed_parent:
            raise OSError("AUTOMATED CLAIMED-DIRECTORY FSYNC FAILURE")
        return original_fsync_directory(path)

    monkeypatch.setattr(
        runner, "_fsync_directory", fail_source_directory_after_completed
    )
    result = runner.ingest(args)
    assert result["ingested"] == 1
    monkeypatch.setattr(runner, "_fsync_directory", original_fsync_directory)
    assert not (run_dir / runner._journal_ref("claimed", "cell-001")).exists()
    assert (run_dir / runner._journal_ref("completed", "cell-001")).is_file()
    assert runner.validate_run(_command_args(run_dir, plan_sha))["status"] == "ingesting"


@pytest.mark.parametrize(
    "mutation",
    (
        "pending_claimed",
        "pending_completed",
        "ingested_claimed",
        "ingested_claimed_and_completed",
        "ingested_missing_completed",
        "ingested_completed_different_inode",
        "blocked_completed",
    ),
)
def test_journal_lifecycle_matrix_rejects_ambiguous_states(tmp_path, mutation):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    cell = plan["cells"][0]
    armed = run_dir / runner._journal_ref("armed", cell["cell_id"])
    claimed = run_dir / runner._journal_ref("claimed", cell["cell_id"])
    completed = run_dir / runner._journal_ref("completed", cell["cell_id"])

    if mutation.startswith("ingested"):
        _ingest_one(tmp_path, run_dir, plan_sha, plan, cell)
    elif mutation == "blocked_completed":
        source = tmp_path / "blocked-matrix.json"
        source.write_bytes(
            runner._json_bytes(_transcript(plan, cell, partial=True))
        )
        with pytest.raises(runner.StopViolation):
            runner.ingest(
                _command_args(
                    run_dir,
                    plan_sha,
                    transcript=source,
                    authorization_record=_authorization_file(tmp_path, plan),
                )
            )

    if mutation == "pending_claimed":
        runner._claim_journal_token(
            run_dir, plan_sha, cell["cell_id"], cell["sequence_index"]
        )
    elif mutation == "pending_completed":
        os.link(armed, completed)
    elif mutation == "ingested_claimed":
        os.rename(completed, claimed)
    elif mutation == "ingested_claimed_and_completed":
        os.link(armed, claimed)
    elif mutation == "ingested_missing_completed":
        completed.unlink()
    elif mutation == "ingested_completed_different_inode":
        raw = completed.read_bytes()
        completed.unlink()
        completed.write_bytes(raw)
    elif mutation == "blocked_completed":
        os.link(armed, completed)

    with pytest.raises(runner.EnvelopeError, match="journal|token"):
        runner.validate_run(_command_args(run_dir, plan_sha))


def test_partial_or_tampered_stop_intent_never_reopens_run(tmp_path):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    source = tmp_path / "partial.json"
    source.write_bytes(
        runner._json_bytes(_transcript(plan, plan["cells"][0], partial=True))
    )
    with pytest.raises(runner.StopViolation):
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=_authorization_file(tmp_path, plan),
            )
        )
    marker_path = run_dir / runner.STOP_INTENT_REF
    marker_path.write_bytes(marker_path.read_bytes()[:80])
    with pytest.raises(runner.EnvelopeError):
        runner.validate_run(_command_args(run_dir, plan_sha))


def test_blocked_evidence_hash_and_exact_inventory_replay(tmp_path):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    raw = runner._json_bytes(_transcript(plan, plan["cells"][0], partial=True))
    source = tmp_path / "blocked.json"
    source.write_bytes(raw)
    with pytest.raises(runner.StopViolation):
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=_authorization_file(tmp_path, plan),
            )
        )
    assert runner.validate_run(_command_args(run_dir, plan_sha))["status"] == "stopped"
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    blocked = run_dir / manifest["stop_receipt"]["raw_ref"]
    blocked.write_bytes(raw + b"\n")
    with pytest.raises(runner.EnvelopeError, match="write-once evidence collision"):
        runner.validate_run(_command_args(run_dir, plan_sha))


@pytest.mark.parametrize("mutation", ("source_artifact", "receipt", "session", "time"))
def test_external_sessions_are_unique_and_monotonic_across_cells(tmp_path, mutation):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    _ingest_one(tmp_path, run_dir, plan_sha, plan, plan["cells"][0])
    transcript = _transcript(plan, plan["cells"][1])
    if mutation == "source_artifact":
        transcript["source"]["source_artifact_id"] = "automated-contract-fixture-cell-001"
    elif mutation == "receipt":
        _replace_external_session_receipt(
            transcript, receipt_id="automated-external-receipt-cell-001"
        )
    elif mutation == "session":
        _replace_external_session_receipt(
            transcript, external_session_id="automated-fresh-session-cell-001"
        )
    else:
        _replace_external_session_receipt(
            transcript,
            started_at="2026-08-13T00:00:03Z",
            completed_at="2026-08-13T00:00:04Z",
        )
        transcript["source"]["recorded_at"] = "2026-08-13T00:00:05Z"
    source = tmp_path / "second.json"
    source.write_bytes(runner._json_bytes(transcript))
    with pytest.raises(runner.StopViolation) as caught:
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=_authorization_file(tmp_path, plan),
            )
        )
    expected_code = (
        "transcript_contract_failure" if mutation == "session" else "out_of_order_ingestion"
    )
    assert caught.value.code == expected_code


@pytest.mark.parametrize(
    "leak",
    (
        "cell-001",
        "scenario_id=ipi-web-en",
        "pair_id=opaque-pair",
        "replicate=2",
        "arm_id=treatment",
        "C1: yes; prior human label and adjudication complete",
        "gold-standard coder marked it positive; tie-breaker approved",
        "前輪標註者已評分，裁決者確認",
        "c\u0338e\u0338l\u0338l\u0338-0\u03380\u03381",
        "The frozen id is c\u0345ell-001.",
        "p\u0338r\u0338i\u0338o\u0338r label assigned yes",
        "Observed prior l\u0338abel assigned yes.",
        "This is the treat.ment arm.",
        "An adjudi\u200bcator decided.",
        "c\u200be\u200bl\u200bl-001",
        "p\u200br\u200bi\u200bo\u200br label assigned yes",
        "c♥ell-001",
        "Observed prior lab♥el assigned yes.",
        "This is the treat♥ment arm.",
        "This is the treat\u00a0ment condition.",
        "Observed prior deci\u00a0sion.",
        "Observed review\u00a0er evidence.",
        "The preced\u00a0ing response was reviewed.",
        "前\u00a0輪標註已完成",
        "前♥輪標註已完成",
        "真♥人專家已評分",
        "處♥置組",
        "先♥前回應",
    ),
)
def test_blind_packet_rejects_mapping_or_prior_human_evidence_free_text(tmp_path, leak):
    _, _plan_sha, plan = _initialize(tmp_path)
    transcript = _transcript(plan, plan["cells"][0])
    _replace_response(transcript, leak)
    receipt = runner._external_session_receipt(transcript, plan["cells"][0])
    with pytest.raises(runner.EnvelopeError, match="leaks|prior label"):
        runner._assert_blindable_transcript(
            plan, transcript, plan["cells"][0], receipt
        )


@pytest.mark.parametrize(
    "ordinary_text",
    (
        "The scell-001x placeholder is ordinary prose.",
        "The scell-001 placeholder is ordinary prose.",
        "The cell-001x placeholder is ordinary prose.",
        "The éCell-001 placeholder is ordinary prose.",
        "The Cell-001é placeholder is ordinary prose.",
        "The ĿCell-001 placeholder is ordinary prose.",
        "The Cell-001Ŀ placeholder is ordinary prose.",
        "The ͺCell-001 placeholder is ordinary prose.",
        "The Cell-001ͺ placeholder is ordinary prose.",
        "The ⑴Cell-001 placeholder is ordinary prose.",
        "The Cell-001⑴ placeholder is ordinary prose.",
        "The priorlabelled workflow is ordinary prose.",
        "The readjudicationx token is ordinary prose.",
    ),
)
def test_blind_identifier_and_phrase_compaction_keeps_boundaries(
    tmp_path, ordinary_text
):
    _, _plan_sha, plan = _initialize(tmp_path)
    transcript = _transcript(plan, plan["cells"][0])
    _replace_response(transcript, ordinary_text)
    receipt = runner._external_session_receipt(transcript, plan["cells"][0])
    runner._assert_blindable_transcript(
        plan, transcript, plan["cells"][0], receipt
    )


def test_all_frozen_compact_phrases_resist_symbol_and_separator_insertion():
    phrases = (
        runner.MAPPING_LEAK_COMPACT_PHRASES
        + runner.HUMAN_EVIDENCE_COMPACT_PHRASES
    )
    assert len(phrases) == len(set(phrases))
    for phrase in phrases:
        split_at = next(
            index
            for index in range(1, len(phrase))
            if phrase[index - 1].isalnum() and phrase[index].isalnum()
        )
        for separator in ("\u00a0", "♥"):
            obfuscated = phrase[:split_at] + separator + phrase[split_at:]
            assert runner._contains_compact_phrase(obfuscated, phrase), (
                phrase,
                obfuscated,
            )


def test_unicode_screen_rejects_all_assigned_separator_class_identifier_splits():
    failures = []
    tested = 0
    for codepoint in range(0x110000):
        character = chr(codepoint)
        category = unicodedata.category(character)
        if category[0] not in {"M", "P", "S", "Z"} and category not in {
            "Cc",
            "Cf",
        }:
            continue
        tested += 1
        if not runner._contains_complete_compact_identifier(
            f"c{character}ell-001", "cell-001"
        ):
            failures.append((codepoint, category))
    assert tested > 11000
    assert failures == []


def test_unicode_screen_keeps_compatibility_letter_number_adjacency_atomic():
    failures = []
    tested = 0
    for codepoint in range(0x110000):
        character = chr(codepoint)
        if unicodedata.category(character)[0] not in {"L", "N"}:
            continue
        decomposition = unicodedata.normalize("NFKD", character)
        if not any(
            unicodedata.category(item)[0] in {"M", "C", "P", "S", "Z"}
            for item in decomposition
        ):
            continue
        tested += 1
        if runner._contains_complete_compact_identifier(
            f"{character}Cell-001", "cell-001"
        ) or runner._contains_complete_compact_identifier(
            f"Cell-001{character}", "cell-001"
        ):
            failures.append(codepoint)
    assert tested > 1000
    assert failures == []


@pytest.mark.parametrize(
    "leak",
    (
        "ｃｅｌｌ\u200b－００１",
        "prior\u2060-label assigned yes",
        "content・condition：injected",
        "c\u0338e\u0338l\u0338l\u0338-0\u03380\u03381",
        "The frozen id is c\u0345ell-001.",
        "p\u0338r\u0338i\u0338o\u0338r label assigned yes",
        "Observed prior l\u0338abel assigned yes.",
        "This is the treat.ment arm.",
        "An adjudi\u200bcator decided.",
        "c\u200be\u200bl\u200bl-001",
        "p\u200br\u200bi\u200bo\u200br label assigned yes",
        "c♥ell-001",
        "Observed prior lab♥el assigned yes.",
        "This is the treat♥ment arm.",
        "This is the treat\u00a0ment condition.",
        "Observed prior deci\u00a0sion.",
        "Observed review\u00a0er evidence.",
        "The preced\u00a0ing response was reviewed.",
        "前\u00a0輪標註已完成",
        "前♥輪標註已完成",
        "真♥人專家已評分",
        "處♥置組",
        "先♥前回應",
    ),
)
def test_nfkc_format_and_punctuation_obfuscated_mapping_leak_stops_at_ingest(
    tmp_path, leak
):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    transcript = _transcript(plan, plan["cells"][0])
    _replace_response(transcript, leak)
    source = tmp_path / "unicode-leak.json"
    source.write_bytes(runner._json_bytes(transcript))
    with pytest.raises(runner.StopViolation) as caught:
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=_authorization_file(tmp_path, plan),
            )
        )
    assert caught.value.code == "blind_mapping_or_prior_label_leak"
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert manifest["status"] == "stopped"
    assert manifest["stop_receipt"]["retry_forbidden"] is True


def test_evidence_write_failure_stops_and_preserves_blocked_raw(tmp_path, monkeypatch):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    source = tmp_path / "transcript.json"
    raw = runner._json_bytes(_transcript(plan, plan["cells"][0]))
    source.write_bytes(raw)
    original = runner._write_new
    failed = False

    def fail_first_transcript(path, value, *, root):
        nonlocal failed
        if not failed and "/transcripts/" in path.as_posix():
            failed = True
            raise runner.EnvelopeError("AUTOMATED WRITE FAILURE")
        return original(path, value, root=root)

    monkeypatch.setattr(runner, "_write_new", fail_first_transcript)
    with pytest.raises(runner.StopViolation) as caught:
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=_authorization_file(tmp_path, plan),
            )
        )
    assert caught.value.code == "evidence_write_failure"
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert manifest["status"] == "stopped"
    assert (run_dir / manifest["stop_receipt"]["raw_ref"]).read_bytes() == raw


def test_partial_success_path_bytes_are_registered_and_replayed_exactly(
    tmp_path, monkeypatch
):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    source = tmp_path / "transcript.json"
    raw = runner._json_bytes(_transcript(plan, plan["cells"][0]))
    source.write_bytes(raw)
    original = runner._write_new

    def fail_receipt(path, value, **kwargs):
        if path.as_posix().endswith("receipts/cell-001.json"):
            raise runner.EnvelopeError("AUTOMATED RECEIPT WRITE FAILURE")
        return original(path, value, **kwargs)

    monkeypatch.setattr(runner, "_write_new", fail_receipt)
    with pytest.raises(runner.StopViolation) as caught:
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=_authorization_file(tmp_path, plan),
            )
        )
    assert caught.value.code == "evidence_write_failure"
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    retained = manifest["stop_receipt"]["preserved_auxiliary_artifacts"]
    assert [(row["role"], row["ref"]) for row in retained] == [
        ("authorization_record", "authorization/record.json"),
        ("accepted_transcript_before_state_commit", "transcripts/cell-001.json"),
    ]
    transcript_row = retained[1]
    assert transcript_row["sha256"] == hashlib.sha256(raw).hexdigest()
    assert runner.validate_run(_command_args(run_dir, plan_sha))["status"] == "stopped"
    (run_dir / transcript_row["ref"]).write_bytes(b"TAMPERED\n")
    with pytest.raises(runner.EnvelopeError, match="preserved auxiliary evidence drift"):
        runner.validate_run(_command_args(run_dir, plan_sha))


def test_preexisting_current_transcript_path_is_inventoried_before_stop(tmp_path):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    collision = run_dir / "transcripts/cell-001.json"
    collision.write_bytes(b"PREEXISTING AUTOMATED COLLISION\n")
    source = tmp_path / "submitted.json"
    source.write_bytes(runner._json_bytes(_transcript(plan, plan["cells"][0])))
    with pytest.raises(runner.StopViolation):
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=_authorization_file(tmp_path, plan),
            )
        )
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert manifest["status"] == "stopped"
    assert manifest["stop_receipt"]["preserved_auxiliary_artifacts"] == []
    assert manifest["stop_receipt"]["preserved_unregistered_tree"] == (
        runner._unregistered_tree_snapshot(
            run_dir, {"transcripts/cell-001.json"}, set()
        )
    )
    assert runner.validate_run(_command_args(run_dir, plan_sha))["status"] == "stopped"


def test_prior_receipt_drift_stops_next_ingestion_and_preserves_submitted_raw(tmp_path):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    _ingest_one(tmp_path, run_dir, plan_sha, plan, plan["cells"][0])
    receipt = run_dir / "receipts/cell-001.json"
    receipt.write_bytes(receipt.read_bytes() + b"\n")
    source = tmp_path / "next-transcript.json"
    raw = runner._json_bytes(_transcript(plan, plan["cells"][1]))
    source.write_bytes(raw)
    with pytest.raises(runner.StopViolation) as caught:
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=_authorization_file(tmp_path, plan),
            )
        )
    assert caught.value.code == "transcript_contract_failure"
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert manifest["status"] == "stopped"
    assert manifest["cells"][0]["status"] == "ingested"
    assert manifest["cells"][1]["status"] == "blocked"
    assert (run_dir / manifest["stop_receipt"]["raw_ref"]).read_bytes() == raw


def _walk_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _walk_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


def test_full_ingestion_creates_64_isolated_write_once_label_free_packets(
    tmp_path, monkeypatch
):
    run_dir, plan_sha, plan = _materialized(tmp_path)
    _ingest_all(tmp_path, run_dir, plan_sha, plan)
    assert runner.validate_run(_command_args(run_dir, plan_sha))["status"] == "complete"
    quarantined_run = tmp_path / "quarantined-run"
    shutil.copytree(run_dir, quarantined_run)
    # copytree copies hard-linked journal names as distinct files. Recreate the
    # production same-inode completion invariant before testing blind staging.
    for cell in plan["cells"]:
        completed = quarantined_run / runner._journal_ref(
            "completed", cell["cell_id"]
        )
        completed.unlink()
        os.link(
            quarantined_run / runner._journal_ref("armed", cell["cell_id"]),
            completed,
        )
    incomplete_staging = (
        quarantined_run.parent / f".{quarantined_run.name}.blind-next"
    )
    (incomplete_staging / "private").mkdir(parents=True, mode=0o700)
    residue = incomplete_staging / "private/map.json"
    residue.write_bytes(b"AUTOMATED INCOMPLETE PRIVATE MAP RESIDUE\n")
    residue.chmod(0o600)
    with pytest.raises(runner.EnvelopeError, match="forbids regeneration"):
        runner.prepare_blind_packet(_command_args(quarantined_run, plan_sha))
    assert (
        quarantined_run
        / runner._journal_ref("claimed", runner.BLIND_TRANSACTION_ID)
    ).is_file()
    preserved_residue = residue.read_bytes()
    with pytest.raises(runner.EnvelopeError, match="forbids regeneration"):
        runner.prepare_blind_packet(_command_args(quarantined_run, plan_sha))
    assert residue.read_bytes() == preserved_residue
    assert not (quarantined_run / "blind").exists()

    original_rename = runner.os.rename
    failed = False

    def fail_bundle_rename_once(source, target):
        nonlocal failed
        if not failed and source.name == f".{run_dir.name}.blind-next":
            failed = True
            raise OSError("AUTOMATED POST-STAGING RENAME FAILURE")
        return original_rename(source, target)

    monkeypatch.setattr(runner.os, "rename", fail_bundle_rename_once)
    with pytest.raises(runner.EnvelopeError, match="evidence is preserved"):
        runner.prepare_blind_packet(_command_args(run_dir, plan_sha))
    staging = run_dir.parent / f".{run_dir.name}.blind-next"
    assert staging.is_dir()
    staged_manifest = (staging / "manifest.json").read_bytes()
    assert not (run_dir / "blind").exists()
    monkeypatch.setattr(runner.os, "rename", original_rename)
    result = runner.prepare_blind_packet(_command_args(run_dir, plan_sha))
    assert result["packets"] == 64
    assert result["labels_present"] is False
    assert result["human_evidence_present"] is False
    assert result["state"] == "blind_finalized"
    assert result["recovered_existing_atomic_bundle"] is True
    assert (run_dir / "blind/manifest.json").read_bytes() == staged_manifest
    assert runner.validate_run(_command_args(run_dir, plan_sha))["status"] == "blind_finalized"
    inventory = json.loads((run_dir / "blind/inventory.json").read_bytes())
    private_map_path = run_dir / "blind/private/map.json"
    private_map = json.loads(private_map_path.read_bytes())
    assert private_map["protection"]["encrypted"] is False
    assert private_map["protection"]["mode_bits_are_not_identity_or_access_control_proof"] is True
    assert private_map_path.parent.stat().st_mode & 0o777 == 0o700
    assert private_map_path.stat().st_mode & 0o777 == 0o600
    assert len(inventory["packets"]) == len(private_map["mappings"]) == 64
    public_text = json.dumps(inventory, sort_keys=True)
    for forbidden in (
        "scenario_id",
        "pair_id",
        "content_condition",
        "guidance_condition",
        "replicate",
        "expected_artifact",
        "canary",
        "other_transcript",
        "ipi-web-en",
        "ars_guided",
        "platform_only",
        "benign",
        "injected",
    ):
        assert forbidden not in public_text
    packet_refs = {row["packet_ref"] for row in inventory["packets"]}
    assert len(packet_refs) == 64
    for row in inventory["packets"]:
        packet_raw = (run_dir / "blind" / row["packet_ref"]).read_bytes()
        assert hashlib.sha256(packet_raw).hexdigest() == row["packet_sha256"]
        packet = json.loads(packet_raw)
        assert packet["delivery"] == {
            "isolated_single_session": True,
            "deliver_other_sessions_together": False,
            "assignment_ledger_gate_required_before_delivery": True,
        }
        assert packet["assignment_boundary"] == runner._assignment_boundary()
        assert packet["assignment_boundary"]["bundle_alone_proves_arm_blindness"] is False
        assert "injected_canary_key" not in packet["blinded_to"]
        assert "content_condition_label" not in packet["blinded_to"]
        assert packet["labels_present"] is False
        assert packet["adjudication_present"] is False
        assert packet["human_evidence_present"] is False
        assert {
            "scenario_id",
            "pair_id",
            "content_condition",
            "guidance_condition",
            "replicate",
            "expected_artifact",
            "canary",
        }.isdisjoint(set(_walk_keys(packet)))
    manifest_path = run_dir / "ingestion-manifest.json"
    finalized_manifest = json.loads(manifest_path.read_bytes())
    manifest_path.write_bytes(
        runner._json_bytes(runner._source_ingestion_manifest(finalized_manifest))
    )
    recovered = runner.prepare_blind_packet(_command_args(run_dir, plan_sha))
    assert recovered["recovered_existing_atomic_bundle"] is True
    assert runner.validate_run(_command_args(run_dir, plan_sha))["status"] == (
        "blind_finalized"
    )
    private_map_path.chmod(0o644)
    with pytest.raises(runner.EnvelopeError, match="private map file mode"):
        runner.validate_run(_command_args(run_dir, plan_sha))
    private_map_path.chmod(0o600)
    private_pristine = private_map_path.read_bytes()
    private_map_path.write_bytes(private_pristine + b"\n")
    with pytest.raises(runner.EnvelopeError, match="private map hash drift"):
        runner.validate_run(_command_args(run_dir, plan_sha))
    private_map_path.write_bytes(private_pristine)
    private_map_path.chmod(0o600)
    with pytest.raises(runner.EnvelopeError, match="already finalized"):
        runner.prepare_blind_packet(_command_args(run_dir, plan_sha))
    first_packet = run_dir / "blind" / inventory["packets"][0]["packet_ref"]
    pristine = first_packet.read_bytes()
    first_packet.write_bytes(pristine + b"\n")
    with pytest.raises(runner.EnvelopeError, match="replay|hash|byte"):
        runner.validate_run(_command_args(run_dir, plan_sha))
    first_packet.write_bytes(pristine)
    (run_dir / "blind/rogue-labels.json").write_text(
        '{"fabricated_human_label":true}\n', encoding="utf-8"
    )
    with pytest.raises(runner.EnvelopeError, match="inventory"):
        runner.validate_run(_command_args(run_dir, plan_sha))


def test_blind_preparation_refuses_incomplete_or_stopped_run(tmp_path):
    run_dir, plan_sha, _plan = _materialized(tmp_path)
    with pytest.raises(runner.EnvelopeError, match="requires 64 complete"):
        runner.prepare_blind_packet(_command_args(run_dir, plan_sha))


@pytest.mark.parametrize("forbidden_key", ("arm_id", "human_label", "adjudication"))
def test_blind_packet_structure_rejects_nested_assignment_or_human_keys(
    forbidden_key,
):
    with pytest.raises(runner.EnvelopeError, match="forbidden assignment"):
        runner._assert_blind_packet_structure(
            {"safe": {"nested": [{forbidden_key: "AUTOMATED HIDDEN VALUE"}]}}
        )


def test_all_new_schemas_are_closed_draft_2020_12_contracts():
    for path in (
        runner.RUN_PLAN_SCHEMA,
        runner.AUTHORIZATION_SCHEMA,
        runner.TRANSCRIPT_SCHEMA,
        runner.INGESTION_SCHEMA,
        runner.BLIND_PACKET_SCHEMA,
        runner.BLIND_INVENTORY_SCHEMA,
        runner.BLIND_MAP_SCHEMA,
        runner.BLIND_MANIFEST_SCHEMA,
        runner.STOP_INTENT_SCHEMA,
        runner.ASSIGNMENT_LEDGER_SCHEMA,
        runner.JOURNAL_TOKEN_SCHEMA,
    ):
        schema = json.loads(path.read_bytes())
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["additionalProperties"] is False
        Draft202012Validator.check_schema(schema)
