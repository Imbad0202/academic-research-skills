from __future__ import annotations

import argparse
import ast
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

import pytest

from scripts import check_spec_consistency as spec_consistency


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
MODULE_PATH = SCRIPTS / "run_ideation_diversity_no_call.py"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("ideation_no_call", MODULE_PATH)
assert SPEC and SPEC.loader
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)
def _args(run_dir: Path) -> argparse.Namespace:
    return argparse.Namespace(
        run_dir=run_dir,
        run_id="phase2-test-no-call",
        suite_commit="a" * 40,
        order_seed="phase2-test-seed-v1",
        subject_provider="external-placeholder",
        subject_model="no-model-called",
        subject_runtime="external-only",
        subject_runtime_version="none",
        auth_mode="fresh-external-authorization-required",
        reasoning_effort="high",
        input_token_cap=12000,
        output_token_cap=3000,
    )


def _initialize(tmp_path: Path) -> tuple[Path, str, dict]:
    run_dir = tmp_path / "run"
    result = runner.init_run(_args(run_dir))
    plan_raw = (run_dir / "run-plan.json").read_bytes()
    plan = json.loads(plan_raw)
    assert result["run_plan_sha256"] == hashlib.sha256(plan_raw).hexdigest()
    return run_dir, result["run_plan_sha256"], plan


def _command_args(run_dir: Path, plan_sha: str, **values) -> argparse.Namespace:
    return argparse.Namespace(
        run_dir=run_dir,
        plan_sha256=plan_sha,
        **values,
    )


def _authorization(plan: dict) -> dict:
    plan_sha = hashlib.sha256(runner._json_bytes(plan)).hexdigest()
    return {
        "schema_version": "ideation-diversity-authorization-record/1.0",
        "suite": runner.SUITE,
        "record_id": "automated-contract-fixture-auth-v1",
        "run_plan_sha256": plan_sha,
        "run_id": plan["run_id"],
        "suite_commit": plan["suite_commit"],
        "execution": plan["execution"],
        "scope": {
            "scope_type": "exact_run_plan_all_cells",
            "subject_session_cells": 48,
            "cell_ids": plan["order"]["cell_ids"],
            "order_sha256": plan["order"]["order_sha256"],
        },
        "decision": {
            "status": "authorized",
            "decided_at": "2026-08-13T00:00:00Z",
            "operator_reference": "automated-contract-fixture-operator-not-a-human-claim",
            "statement": (
                "AUTOMATED CONTRACT FIXTURE ONLY; not real consent, human evidence, "
                "or research evidence."
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
    path = tmp_path / "automated-authorization-fixture.json"
    path.write_bytes(runner._json_bytes(_authorization(plan)))
    return path


def _transcript(plan: dict, cell: dict, *, partial: bool = False) -> dict:
    heldout, _ = runner.phase1.load_assets()
    scenario = next(
        row for row in heldout["scenarios"] if row["scenario_id"] == cell["scenario_id"]
    )
    turns = []
    for turn_index in range(1, 12):
        is_actor = turn_index % 2 == 1
        if turn_index == 1:
            text = scenario["initial_message"]
        else:
            role = "actor" if is_actor else "subject"
            text = (
                f"AUTOMATED CONTRACT TEST FIXTURE {role} turn {turn_index}; "
                "repository-owned synthetic content only."
            )
        turns.append(
            {
                "turn_index": turn_index,
                "role": "actor" if is_actor else "subject",
                "text": text,
            }
        )
    def raw_event(
        event_kind: str, turn_index: int | None, text: str | None = None
    ) -> dict[str, str]:
        value = {"event_kind": event_kind, "turn_index": turn_index}
        if text is not None:
            value["text"] = text
        raw = runner._canonical(value).decode("utf-8")
        return {
            "raw_event_utf8": raw,
            "raw_event_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        }

    events = [
        {
            "event_index": 1,
            "event_kind": "session_started",
            "turn_index": None,
            **raw_event("session_started", None),
        }
    ]
    for turn in turns:
        events.append(
            {
                "event_index": len(events) + 1,
                "event_kind": f"{turn['role']}_message",
                "turn_index": turn["turn_index"],
                **raw_event(
                    f"{turn['role']}_message", turn["turn_index"], turn["text"]
                ),
            }
        )
    events.append(
        {
            "event_index": len(events) + 1,
            "event_kind": "session_partial" if partial else "session_completed",
            "turn_index": None,
            **raw_event("session_partial" if partial else "session_completed", None),
        }
    )
    started_at = datetime(2026, 8, 13, tzinfo=timezone.utc) + timedelta(
        seconds=cell["sequence_index"] * 2 - 1
    )
    completed_at = started_at + timedelta(seconds=1)
    external_receipt = {
        "receipt_id": f"automated-external-receipt-{cell['cell_id']}",
        "external_session_id": f"automated-fresh-session-{cell['cell_id']}",
        "cell_id": cell["cell_id"],
        "sequence_index": cell["sequence_index"],
        "started_at": started_at.isoformat().replace("+00:00", "Z"),
        "completed_at": completed_at.isoformat().replace("+00:00", "Z"),
        "fresh_context": True,
    }
    external_receipt_utf8 = runner._canonical(external_receipt).decode("utf-8")
    return {
        "schema_version": "ideation-diversity-transcript/1.0",
        "suite": runner.SUITE,
        "run_plan_sha256": hashlib.sha256(
            runner._json_bytes(plan)
        ).hexdigest(),
        "cell_id": cell["cell_id"],
        "sequence_index": cell["sequence_index"],
        "source": {
            "source_kind": "externally_recorded_session",
            "source_artifact_id": f"automated-contract-fixture-{cell['cell_id']}",
            "external_session_receipt_utf8": external_receipt_utf8,
            "external_session_receipt_sha256": hashlib.sha256(
                external_receipt_utf8.encode("utf-8")
            ).hexdigest(),
            "authorization_record_ref": "automated-contract-fixture-auth-v1",
            "authorization_record_sha256": hashlib.sha256(
                runner._json_bytes(_authorization(plan))
            ).hexdigest(),
        },
        "bindings": {
            "prompt_sha256": cell["prompt"]["sha256"],
            "scenario_sha256": cell["scenario_sha256"],
            "initial_message_sha256": cell["initial_message_sha256"],
            "actor_packet_sha256": cell["actor_packet_sha256"],
            "session_envelope_sha256": cell["session_envelope_sha256"],
        },
        "session": {
            "fresh_context": True,
            "complete": not partial,
            "blocked": False,
            "partial": partial,
            "stop_reason": "partial" if partial else "freeze_point_reached",
            "actor_turns": 6,
            "subject_turns": 5,
            "freeze_after_actor_turn": 6,
        },
        "turns": turns,
        "events": events,
        "observations": {
            "prompt_hash_match": True,
            "role_card_hash_match": True,
            "arm_leakage": False,
            "eligible": True,
            "unplanned_tool_actions": [],
            "unplanned_network_actions": [],
            "evidence_write_failure": False,
            "partial_subject_output": partial,
            "actor_protocol_deviation": False,
        },
    }


def _set_raw_event(event: dict, normalized: dict) -> None:
    raw = runner._canonical(normalized).decode("utf-8")
    event["raw_event_utf8"] = raw
    event["raw_event_sha256"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _set_external_receipt(transcript: dict, receipt: dict) -> None:
    raw = runner._canonical(receipt).decode("utf-8")
    transcript["source"]["external_session_receipt_utf8"] = raw
    transcript["source"]["external_session_receipt_sha256"] = hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


def _get_external_receipt(transcript: dict) -> dict:
    return json.loads(transcript["source"]["external_session_receipt_utf8"])


def test_plan_is_exact_48_cell_counterbalanced_no_call_cross_product(tmp_path):
    run_dir, plan_sha, plan = _initialize(tmp_path)
    assert len(plan["cells"]) == 2 * 6 * 2 * 2 == 48
    assert plan["order"]["cell_ids"] == [
        f"cell-{index:03d}" for index in range(1, 49)
    ]
    order_projection = [
        {
            key: cell[key]
            for key in (
                "cell_id",
                "sequence_index",
                "experiment_id",
                "scenario_id",
                "arm_id",
                "replicate",
                "actor_block_id",
            )
        }
        for cell in plan["cells"]
    ]
    assert plan["order"]["order_sha256"] == hashlib.sha256(
        runner._canonical(order_projection)
    ).hexdigest()
    alternate_config = runner._config_from_plan(plan)
    alternate_config["order_seed"] = "phase2-alternate-seed-v1"
    alternate = runner._build_plan(alternate_config)
    assert alternate["order"]["order_sha256"] != plan["order"]["order_sha256"]
    observed = {
        (
            cell["experiment_id"],
            cell["scenario_id"],
            cell["arm_id"],
            cell["replicate"],
        )
        for cell in plan["cells"]
    }
    assert len(observed) == 48
    for experiment, arms in runner.EXPERIMENTS:
        scenario_ids = {
            cell["scenario_id"]
            for cell in plan["cells"]
            if cell["experiment_id"] == experiment
        }
        assert len(scenario_ids) == 6
        for scenario_id in scenario_ids:
            rows = [
                cell
                for cell in plan["cells"]
                if cell["experiment_id"] == experiment
                and cell["scenario_id"] == scenario_id
            ]
            first = [cell["arm_id"] for cell in rows if cell["replicate"] == 1]
            second = [cell["arm_id"] for cell in rows if cell["replicate"] == 2]
            assert set(first) == set(arms)
            assert second == list(reversed(first))
    assert plan["execution"] | {
        "runner_transport": "none",
        "dispatch_available": False,
        "api_spend_ceiling_usd": 0,
        "api_fallback": False,
        "envelope_grants_consent": False,
    } == plan["execution"]
    assert plan["created_without_dispatch"] is True
    assert len(plan["asset_bindings"]) == 16
    assert runner.validate_run(_command_args(run_dir, plan_sha))["status"] == "initialized"


def test_materializer_writes_only_frozen_inputs_and_never_changes_production(tmp_path):
    production_before = runner.PRODUCTION_PROMPT.read_bytes()
    run_dir, plan_sha, plan = _initialize(tmp_path)
    result = runner.materialize(_command_args(run_dir, plan_sha))
    assert result == {
        "materialized_files": 98,
        "cells": 48,
        "dispatch_available": False,
    }
    inventory = [path for path in (run_dir / "materials").rglob("*") if path.is_file()]
    assert len(inventory) == 98
    assert (
        run_dir / "materials/prompts/production-socratic-mentor.md"
    ).read_bytes() == production_before
    assert (
        run_dir / "materials/prompts/exploratory-guardrails-ablated.md"
    ).read_bytes() != production_before
    assert runner.PRODUCTION_PROMPT.read_bytes() == production_before
    actor = json.loads((run_dir / plan["cells"][0]["actor_packet_path"]).read_bytes())
    assert actor["model_generated_actor"] is False
    assert "arm_id" not in actor and "experiment_id" not in actor
    envelope = json.loads(
        (run_dir / plan["cells"][0]["session_envelope_path"]).read_bytes()
    )
    assert envelope["runner_transport"] == "none"
    assert envelope["dispatch_available"] is False
    assert envelope["tools"] == [] and envelope["web_enabled"] is False
    assert envelope["api_spend_ceiling_usd"] == 0
    assert envelope["api_fallback"] is False
    assert envelope["envelope_grants_consent"] is False
    assert envelope["fresh_external_authorization_required"] is True
    assert "command" not in envelope and "subject_output" not in envelope
    assert runner.validate_run(_command_args(run_dir, plan_sha))["status"] == "materialized"


def test_runner_exposes_no_transport_dispatch_probe_or_model_surface():
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    forbidden_imports = {
        "subprocess",
        "socket",
        "requests",
        "httpx",
        "aiohttp",
        "urllib",
        "http",
        "openai",
        "anthropic",
        "cohere",
        "litellm",
        "mistralai",
        "importlib",
        "ctypes",
    }
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".", 1)[0])
    assert imported.isdisjoint(forbidden_imports)
    forbidden_os_calls = {
        "system",
        "popen",
        "spawnl",
        "spawnle",
        "spawnlp",
        "spawnlpe",
        "spawnv",
        "spawnve",
        "spawnvp",
        "spawnvpe",
        "posix_spawn",
        "posix_spawnp",
        "fork",
        "forkpty",
        "execl",
        "execle",
        "execlp",
        "execlpe",
        "execv",
        "execve",
        "execvp",
        "execvpe",
    }
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "os"
        and node.func.attr in forbidden_os_calls
        for node in ast.walk(tree)
    )
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"__import__", "eval", "exec", "compile"}
        for node in ast.walk(tree)
    )
    parser = runner._parser()
    subparsers = parser._subparsers._group_actions[0]
    assert set(subparsers.choices) == {
        "init-run",
        "materialize",
        "validate",
        "ingest",
        "prepare-blind-packet",
    }
    assert {"dispatch", "probe", "detect", "run"}.isdisjoint(subparsers.choices)


def test_plan_or_material_hash_drift_fails_closed(tmp_path):
    run_dir, plan_sha, plan = _initialize(tmp_path)
    runner.materialize(_command_args(run_dir, plan_sha))
    material = run_dir / plan["cells"][0]["actor_packet_path"]
    material.write_bytes(material.read_bytes() + b"\n")
    with pytest.raises(runner.EnvelopeError, match="material bytes drifted"):
        runner.validate_run(_command_args(run_dir, plan_sha))

    other_dir, _, other_plan = _initialize(tmp_path / "other")
    mutated = copy.deepcopy(other_plan)
    mutated["cells"][0]["arm_id"] = "adjacent_probe_on"
    raw = runner._json_bytes(mutated)
    (other_dir / "run-plan.json").write_bytes(raw)
    with pytest.raises(runner.EnvelopeError, match="exact current asset/order/hash"):
        runner.validate_run(
            _command_args(other_dir, hashlib.sha256(raw).hexdigest())
        )


def test_first_partial_output_stops_preserves_raw_and_forbids_retry(tmp_path):
    run_dir, plan_sha, plan = _initialize(tmp_path)
    runner.materialize(_command_args(run_dir, plan_sha))
    raw = runner._json_bytes(_transcript(plan, plan["cells"][0], partial=True))
    source = tmp_path / "external-transcript.json"
    source.write_bytes(raw)
    ingest_args = _command_args(
        run_dir,
        plan_sha,
        transcript=source,
        authorization_record=_authorization_file(tmp_path, plan),
    )
    with pytest.raises(runner.StopViolation) as caught:
        runner.ingest(ingest_args)
    assert caught.value.code == "partial_subject_output"
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert manifest["status"] == "stopped"
    assert manifest["next_sequence_index"] == 1
    assert manifest["stop_receipt"]["retry_forbidden"] is True
    blocked = run_dir / manifest["stop_receipt"]["raw_ref"]
    assert blocked.read_bytes() == raw
    with pytest.raises(runner.EnvelopeError, match="forbids retry"):
        runner.ingest(ingest_args)


def test_out_of_order_ingestion_stops_on_first_event(tmp_path):
    run_dir, plan_sha, plan = _initialize(tmp_path)
    runner.materialize(_command_args(run_dir, plan_sha))
    raw = runner._json_bytes(_transcript(plan, plan["cells"][1]))
    source = tmp_path / "external-transcript.json"
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
    assert [row["status"] for row in manifest["cells"][:2]] == [
        "blocked",
        "pending",
    ]


@pytest.mark.parametrize(
    ("mutation", "reason_code"),
    (
        ("prompt", "prompt_or_role_card_hash_mismatch"),
        ("reported_arm_leak", "arm_leakage"),
        ("ineligible", "ineligible_session"),
        ("reported_tool", "unplanned_tool_action"),
        ("reported_network", "unplanned_network_action"),
        ("write_failure", "evidence_write_failure"),
        ("actor_deviation", "actor_protocol_deviation"),
    ),
)
def test_each_reported_stop_rule_fails_closed(tmp_path, mutation, reason_code):
    _, plan_sha, plan = _initialize(tmp_path)
    cell = plan["cells"][0]
    transcript = _transcript(plan, cell)
    observations = transcript["observations"]
    if mutation == "prompt":
        observations["prompt_hash_match"] = False
    elif mutation == "reported_arm_leak":
        observations["arm_leakage"] = True
    elif mutation == "ineligible":
        observations["eligible"] = False
    elif mutation == "reported_tool":
        observations["unplanned_tool_actions"] = ["automated test fixture"]
    elif mutation == "reported_network":
        observations["unplanned_network_actions"] = ["automated test fixture"]
    elif mutation == "write_failure":
        observations["evidence_write_failure"] = True
    elif mutation == "actor_deviation":
        observations["actor_protocol_deviation"] = True
    heldout, _ = runner.phase1.load_assets()
    scenario = next(
        row for row in heldout["scenarios"] if row["scenario_id"] == cell["scenario_id"]
    )
    with pytest.raises(runner.StopViolation) as caught:
        runner._validate_transcript(transcript, cell, plan_sha, scenario)
    assert caught.value.code == reason_code


@pytest.mark.parametrize(
    ("event_kind", "reason_code"),
    (
        ("tool_action", "unplanned_tool_action"),
        ("network_action", "unplanned_network_action"),
        ("evidence_write_failure", "evidence_write_failure"),
    ),
)
def test_normalized_event_stream_cannot_hide_forbidden_actions(
    tmp_path, event_kind, reason_code
):
    _, plan_sha, plan = _initialize(tmp_path)
    cell = plan["cells"][0]
    transcript = _transcript(plan, cell)
    normalized = {"event_kind": event_kind, "turn_index": None}
    raw_event = runner._canonical(normalized).decode("utf-8")
    transcript["events"].insert(
        -1,
        {
            "event_index": len(transcript["events"]),
            "event_kind": event_kind,
            "turn_index": None,
            "raw_event_utf8": raw_event,
            "raw_event_sha256": hashlib.sha256(raw_event.encode()).hexdigest(),
        },
    )
    transcript["events"][-1]["event_index"] += 1
    heldout, _ = runner.phase1.load_assets()
    scenario = next(
        row for row in heldout["scenarios"] if row["scenario_id"] == cell["scenario_id"]
    )
    with pytest.raises(runner.StopViolation) as caught:
        runner._validate_transcript(transcript, cell, plan_sha, scenario)
    assert caught.value.code == reason_code


def test_exact_arm_identifiers_in_turn_text_cannot_bypass_false_observation(tmp_path):
    _, plan_sha, plan = _initialize(tmp_path)
    cell = plan["cells"][0]
    transcript = _transcript(plan, cell)
    transcript["turns"][1]["text"] += " adjacent_probe_on"
    heldout, _ = runner.phase1.load_assets()
    scenario = next(
        row for row in heldout["scenarios"] if row["scenario_id"] == cell["scenario_id"]
    )
    with pytest.raises(runner.StopViolation) as caught:
        runner._validate_transcript(transcript, cell, plan_sha, scenario)
    assert caught.value.code == "arm_leakage"


def test_raw_event_hash_mutation_fails_closed(tmp_path):
    _, plan_sha, plan = _initialize(tmp_path)
    cell = plan["cells"][0]
    transcript = _transcript(plan, cell)
    transcript["events"][0]["raw_event_utf8"] += " mutated"
    heldout, _ = runner.phase1.load_assets()
    scenario = next(
        row for row in heldout["scenarios"] if row["scenario_id"] == cell["scenario_id"]
    )
    with pytest.raises(runner.StopViolation, match=r"raw event (?:[0-9]+ )?hash mismatch"):
        runner._validate_transcript(transcript, cell, plan_sha, scenario)


def test_raw_network_action_cannot_hide_behind_normalized_message_fields(tmp_path):
    _, plan_sha, plan = _initialize(tmp_path)
    cell = plan["cells"][0]
    transcript = _transcript(plan, cell)
    _set_raw_event(
        transcript["events"][1],
        {"event_kind": "network_action", "turn_index": None},
    )
    heldout, _ = runner.phase1.load_assets()
    scenario = next(
        row for row in heldout["scenarios"] if row["scenario_id"] == cell["scenario_id"]
    )
    with pytest.raises(runner.StopViolation) as caught:
        runner._validate_transcript(transcript, cell, plan_sha, scenario)
    assert caught.value.code == "unplanned_network_action"


def test_turn_text_must_be_derived_exactly_from_raw_message_bytes(tmp_path):
    _, plan_sha, plan = _initialize(tmp_path)
    cell = plan["cells"][0]
    transcript = _transcript(plan, cell)
    transcript["turns"][1]["text"] += " externally mutated"
    heldout, _ = runner.phase1.load_assets()
    scenario = next(
        row for row in heldout["scenarios"] if row["scenario_id"] == cell["scenario_id"]
    )
    with pytest.raises(runner.StopViolation, match="derived byte-exactly"):
        runner._validate_transcript(transcript, cell, plan_sha, scenario)


def test_raw_event_unknown_fields_fail_closed_instead_of_self_classifying(tmp_path):
    _, plan_sha, plan = _initialize(tmp_path)
    cell = plan["cells"][0]
    transcript = _transcript(plan, cell)
    _set_raw_event(
        transcript["events"][0],
        {
            "event_kind": "session_started",
            "turn_index": None,
            "network_action": "https://example.invalid",
        },
    )
    heldout, _ = runner.phase1.load_assets()
    scenario = next(
        row for row in heldout["scenarios"] if row["scenario_id"] == cell["scenario_id"]
    )
    with pytest.raises(runner.StopViolation, match="closed normalized event"):
        runner._validate_transcript(transcript, cell, plan_sha, scenario)


def test_event_lifecycle_rejects_stitched_sessions(tmp_path):
    _, plan_sha, plan = _initialize(tmp_path)
    cell = plan["cells"][0]
    transcript = _transcript(plan, cell)
    inserted = []
    for event_kind in ("session_completed", "session_started"):
        normalized = {"event_kind": event_kind, "turn_index": None}
        raw = runner._canonical(normalized).decode("utf-8")
        inserted.append(
            {
                "event_index": 0,
                "event_kind": event_kind,
                "turn_index": None,
                "raw_event_utf8": raw,
                "raw_event_sha256": hashlib.sha256(raw.encode()).hexdigest(),
            }
        )
    transcript["events"][3:3] = inserted
    for index, event in enumerate(transcript["events"], 1):
        event["event_index"] = index
    heldout, _ = runner.phase1.load_assets()
    scenario = next(
        row for row in heldout["scenarios"] if row["scenario_id"] == cell["scenario_id"]
    )
    with pytest.raises(runner.StopViolation, match="exactly one first start"):
        runner._validate_transcript(transcript, cell, plan_sha, scenario)


def test_authorization_record_hash_mismatch_stops_and_preserves_transcript(tmp_path):
    run_dir, plan_sha, plan = _initialize(tmp_path)
    runner.materialize(_command_args(run_dir, plan_sha))
    source = tmp_path / "external-transcript.json"
    raw = runner._json_bytes(_transcript(plan, plan["cells"][0]))
    source.write_bytes(raw)
    wrong_authorization = tmp_path / "wrong-authorization.txt"
    wrong_authorization.write_bytes(b"AUTOMATED WRONG HASH TEST FIXTURE\n")
    with pytest.raises(runner.StopViolation) as caught:
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=wrong_authorization,
            )
        )
    assert caught.value.code == "authorization_record_missing_or_mismatch"
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert (run_dir / manifest["stop_receipt"]["raw_ref"]).read_bytes() == raw


@pytest.mark.parametrize("mutation", ("blank", "wrong_plan", "predates"))
def test_invalid_authorization_structure_plan_or_time_stops(tmp_path, mutation):
    run_dir, plan_sha, plan = _initialize(tmp_path)
    runner.materialize(_command_args(run_dir, plan_sha))
    transcript = _transcript(plan, plan["cells"][0])
    authorization_path = tmp_path / "authorization.json"
    if mutation == "blank":
        authorization_raw = b"{}\n"
    else:
        authorization = _authorization(plan)
        if mutation == "wrong_plan":
            authorization["run_plan_sha256"] = "f" * 64
        else:
            authorization["decision"]["decided_at"] = "2026-08-13T00:00:02Z"
        authorization_raw = runner._json_bytes(authorization)
    authorization_path.write_bytes(authorization_raw)
    transcript["source"]["authorization_record_sha256"] = hashlib.sha256(
        authorization_raw
    ).hexdigest()
    source = tmp_path / "transcript.json"
    source.write_bytes(runner._json_bytes(transcript))
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


def test_prior_transcript_and_receipt_drift_blocks_further_ingestion(tmp_path):
    run_dir, plan_sha, plan = _initialize(tmp_path)
    runner.materialize(_command_args(run_dir, plan_sha))
    source = tmp_path / "external-transcript.json"
    source.write_bytes(runner._json_bytes(_transcript(plan, plan["cells"][0])))
    authorization = _authorization_file(tmp_path, plan)
    runner.ingest(
        _command_args(
            run_dir,
            plan_sha,
            transcript=source,
            authorization_record=authorization,
        )
    )
    receipt = run_dir / "receipts/cell-001.json"
    receipt.write_bytes(receipt.read_bytes() + b"\n")
    with pytest.raises(runner.EnvelopeError, match="ingestion receipt drift"):
        runner.validate_run(_command_args(run_dir, plan_sha))
    source.write_bytes(runner._json_bytes(_transcript(plan, plan["cells"][1])))
    with pytest.raises(runner.EnvelopeError, match="ingestion receipt drift"):
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=authorization,
            )
        )


def test_local_evidence_write_failure_stops_without_overwrite(tmp_path):
    run_dir, plan_sha, plan = _initialize(tmp_path)
    runner.materialize(_command_args(run_dir, plan_sha))
    existing = run_dir / "transcripts/cell-001.json"
    existing.parent.mkdir()
    existing.write_bytes(b"PREEXISTING AUTOMATED TEST SENTINEL\n")
    source = tmp_path / "external-transcript.json"
    raw = runner._json_bytes(_transcript(plan, plan["cells"][0]))
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
    assert caught.value.code == "evidence_write_failure"
    assert existing.read_bytes() == b"PREEXISTING AUTOMATED TEST SENTINEL\n"
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert manifest["status"] == "stopped"
    assert manifest["stop_receipt"]["retry_forbidden"] is True
    assert (run_dir / manifest["stop_receipt"]["raw_ref"]).read_bytes() == raw


def test_preexisting_blocked_path_cannot_prevent_irreversible_first_stop(tmp_path):
    run_dir, plan_sha, plan = _initialize(tmp_path)
    runner.materialize(_command_args(run_dir, plan_sha))
    sentinel = run_dir / "blocked/cell-001.transcript.raw"
    sentinel.parent.mkdir()
    sentinel.write_bytes(b"PREEXISTING BLOCKED-PATH SENTINEL\n")
    source = tmp_path / "external-transcript.json"
    raw = runner._json_bytes(_transcript(plan, plan["cells"][0]))
    source.write_bytes(raw)
    ingest_args = _command_args(
        run_dir,
        plan_sha,
        transcript=source,
        authorization_record=_authorization_file(tmp_path, plan),
    )
    with pytest.raises(runner.StopViolation) as caught:
        runner.ingest(ingest_args)
    assert caught.value.code == "evidence_write_failure"
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert manifest["status"] == "stopped"
    assert manifest["stop_receipt"]["state_committed_before_evidence_write"] is True
    assert sentinel.read_bytes() == b"PREEXISTING BLOCKED-PATH SENTINEL\n"
    assert (run_dir / manifest["stop_receipt"]["raw_ref"]).read_bytes() == raw
    with pytest.raises(runner.EnvelopeError, match="forbids retry"):
        runner.ingest(ingest_args)


def test_blocked_raw_evidence_tamper_is_detected_on_replay(tmp_path):
    run_dir, plan_sha, plan = _initialize(tmp_path)
    runner.materialize(_command_args(run_dir, plan_sha))
    source = tmp_path / "partial-transcript.json"
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
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    blocked = run_dir / manifest["stop_receipt"]["raw_ref"]
    blocked.write_bytes(b"TAMPERED BLOCKED EVIDENCE\n")
    with pytest.raises(runner.EnvelopeError, match="blocked transcript hash drift"):
        runner.validate_run(_command_args(run_dir, plan_sha))


@pytest.mark.parametrize("mutation", ("duplicate_session", "time_regression"))
def test_external_session_receipts_are_unique_and_monotonic(tmp_path, mutation):
    run_dir, plan_sha, plan = _initialize(tmp_path)
    runner.materialize(_command_args(run_dir, plan_sha))
    source = tmp_path / "external-transcript.json"
    authorization = _authorization_file(tmp_path, plan)
    first = _transcript(plan, plan["cells"][0])
    source.write_bytes(runner._json_bytes(first))
    runner.ingest(
        _command_args(
            run_dir,
            plan_sha,
            transcript=source,
            authorization_record=authorization,
        )
    )
    second = _transcript(plan, plan["cells"][1])
    receipt = _get_external_receipt(second)
    if mutation == "duplicate_session":
        receipt["external_session_id"] = _get_external_receipt(first)[
            "external_session_id"
        ]
    else:
        receipt["started_at"] = "2026-08-13T00:00:01.500000Z"
        receipt["completed_at"] = "2026-08-13T00:00:01.750000Z"
    _set_external_receipt(second, receipt)
    source.write_bytes(runner._json_bytes(second))
    with pytest.raises(runner.StopViolation) as caught:
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=authorization,
            )
        )
    assert caught.value.code == "out_of_order_ingestion"


@pytest.mark.parametrize(
    "leak_text",
    (
        "cell=cell-001 pair=idi-public-health replicate=1",
        "prior human judge label=M1 yes; adjudicator approved",
        "other transcript mapping replicate 2",
        (
            "first repeat in the treatment where adjacent probe is enabled. "
            "The preceding session answered differently. Gold-standard coder "
            "marked it positive; tie-breaker approved"
        ),
    ),
)
def test_blind_packet_free_text_gate_rejects_mapping_or_human_evidence(
    tmp_path, leak_text
):
    _, _, plan = _initialize(tmp_path)
    transcript = _transcript(plan, plan["cells"][0])
    transcript["turns"][1]["text"] += f" {leak_text}"
    _set_raw_event(
        transcript["events"][2],
        {
            "event_kind": "subject_message",
            "turn_index": 2,
            "text": transcript["turns"][1]["text"],
        },
    )
    with pytest.raises(runner.EnvelopeError, match="leak|label|mapping"):
        runner._assert_blindable_transcript(plan, transcript)


def test_partial_success_writes_are_registered_in_stopped_replay(tmp_path, monkeypatch):
    run_dir, plan_sha, plan = _initialize(tmp_path)
    runner.materialize(_command_args(run_dir, plan_sha))
    source = tmp_path / "external-transcript.json"
    raw = runner._json_bytes(_transcript(plan, plan["cells"][0]))
    source.write_bytes(raw)
    authorization = _authorization_file(tmp_path, plan)
    original_write = runner._write_new

    def fail_receipt(path, raw_bytes, **kwargs):
        if str(path).endswith("receipts/cell-001.json"):
            raise runner.EnvelopeError("AUTOMATED RECEIPT WRITE FAILURE")
        return original_write(path, raw_bytes, **kwargs)

    monkeypatch.setattr(runner, "_write_new", fail_receipt)
    with pytest.raises(runner.StopViolation) as caught:
        runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=authorization,
            )
        )
    assert caught.value.code == "evidence_write_failure"
    manifest = json.loads((run_dir / "ingestion-manifest.json").read_bytes())
    assert manifest["status"] == "stopped"
    preserved = manifest["stop_receipt"]["preserved_auxiliary_artifacts"]
    assert [(row["role"], row["ref"]) for row in preserved] == [
        ("authorization_record", "authorization/record.json"),
        (
            "accepted_transcript_before_state_commit",
            "transcripts/cell-001.json",
        ),
    ]
    monkeypatch.setattr(runner, "_write_new", original_write)
    assert runner.validate_run(_command_args(run_dir, plan_sha))["status"] == "stopped"
    (run_dir / "transcripts/cell-001.json").write_bytes(b"TAMPERED\n")
    with pytest.raises(runner.EnvelopeError, match="pre-stop artifact hash drift"):
        runner.validate_run(_command_args(run_dir, plan_sha))


def test_48_external_ingestions_prepare_unlabeled_arm_blind_packet(tmp_path):
    run_dir, plan_sha, plan = _initialize(tmp_path)
    runner.materialize(_command_args(run_dir, plan_sha))
    source = tmp_path / "external-transcript.json"
    authorization = _authorization_file(tmp_path, plan)
    for index, cell in enumerate(plan["cells"], 1):
        source.write_bytes(runner._json_bytes(_transcript(plan, cell)))
        result = runner.ingest(
            _command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=authorization,
            )
        )
        assert result["ingested"] == index
    assert runner.validate_run(_command_args(run_dir, plan_sha))["status"] == "complete"
    result = runner.prepare_blind_packet(_command_args(run_dir, plan_sha))
    assert result["sessions"] == 48
    assert result["artifact_presence"] == runner._artifact_presence()
    assert result["state"] == "blind_finalized"
    assert result["recovered_existing_atomic_bundle"] is False
    inventory = json.loads((run_dir / "blind/inventory.json").read_bytes())
    assert inventory["artifact_presence"] == runner._artifact_presence()
    assert len(inventory["packets"]) == 48
    assert all(
        set(row) == {"blind_session_id", "packet_sha256"}
        for row in inventory["packets"]
    )
    public_inventory_text = json.dumps(inventory, sort_keys=True)
    for forbidden in (
        "arm_id",
        "experiment_id",
        "pair_id",
        "replicate",
        "scenario_id",
        "role_card",
        "transcript",
    ):
        assert forbidden not in public_inventory_text
    isolated_paths = sorted((run_dir / "blind/sessions").glob("*.json"))
    assert len(isolated_paths) == 48
    for packet_path in isolated_paths:
        isolated = json.loads(packet_path.read_bytes())
        assert isolated["delivery"] == {
            "isolated_single_session": True,
            "deliver_other_sessions_together": False,
        }
        assert isolated["artifact_presence"] == runner._artifact_presence()
        assert "sessions" not in isolated
        assert len(isolated["transcript"]["turns"]) <= 11
        for forbidden in (
            "arm_id",
            "experiment_id",
            "pair_id",
            "replicate",
            "scenario_id",
        ):
            assert forbidden not in isolated
            assert forbidden not in isolated["role_card"]
            assert forbidden not in isolated["transcript"]
    arm_map_path = run_dir / "blind/private/arm-map.json"
    arm_map = json.loads(arm_map_path.read_bytes())
    assert arm_map["private"] is True
    assert arm_map["protection"] == {
        "kind": "procedural_nondisclosure_only",
        "encrypted": False,
        "directory_mode": "0700",
        "file_mode": "0600",
        "unblind_only_after_raw_labels_and_adjudication_sealed": True,
    }
    assert stat.S_IMODE(arm_map_path.parent.stat().st_mode) == 0o700
    assert stat.S_IMODE(arm_map_path.stat().st_mode) == 0o600
    assert len(arm_map["mapping"]) == 48
    assert arm_map["inventory_sha256"] == hashlib.sha256(
        (run_dir / "blind/inventory.json").read_bytes()
    ).hexdigest()
    final = runner.validate_run(_command_args(run_dir, plan_sha))
    assert final["status"] == "blind_finalized"
    # Replay the crash boundary after the atomic bundle rename but before the
    # ingestion manifest's final state replacement.
    final_manifest_path = run_dir / "ingestion-manifest.json"
    final_manifest = json.loads(final_manifest_path.read_bytes())
    final_manifest_path.write_bytes(
        runner._json_bytes(runner._source_ingestion_manifest(final_manifest))
    )
    recovered = runner.prepare_blind_packet(_command_args(run_dir, plan_sha))
    assert recovered["recovered_existing_atomic_bundle"] is True
    assert runner.validate_run(_command_args(run_dir, plan_sha))["status"] == (
        "blind_finalized"
    )
    isolated_paths[0].write_bytes(b"TAMPERED BLIND PACKET\n")
    with pytest.raises(runner.EnvelopeError, match="blind packet replay|hash drift"):
        runner.validate_run(_command_args(run_dir, plan_sha))


def test_manifest_tampering_cannot_reorder_append_only_state(tmp_path):
    run_dir, plan_sha, _ = _initialize(tmp_path)
    manifest_path = run_dir / "ingestion-manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["status"] = "ingesting"
    manifest["next_sequence_index"] = 2
    manifest["cells"][-1].update(
        status="ingested",
        transcript_ref="transcripts/cell-048.json",
        transcript_sha256="c" * 64,
        ingestion_receipt_ref="receipts/cell-048.json",
    )
    manifest_path.write_bytes(runner._json_bytes(manifest))
    with pytest.raises(
        runner.EnvelopeError,
        match="authorization record|append-only prefix",
    ):
        runner.validate_run(_command_args(run_dir, plan_sha))


def test_run_tree_symlink_is_rejected_before_ingestion_write(tmp_path):
    run_dir, plan_sha, _ = _initialize(tmp_path)
    runner.materialize(_command_args(run_dir, plan_sha))
    outside = tmp_path / "outside"
    outside.mkdir()
    os.symlink(outside, run_dir / "transcripts")
    with pytest.raises(runner.EnvelopeError, match="must not contain symlinks"):
        runner.validate_run(_command_args(run_dir, plan_sha))
    assert list(outside.iterdir()) == []


def test_spec_consistency_integration_accepts_current_no_call_contract():
    previous = list(spec_consistency.ERRORS)
    spec_consistency.ERRORS.clear()
    try:
        spec_consistency.check_ideation_diversity_no_call_contract()
        assert spec_consistency.ERRORS == []
    finally:
        spec_consistency.ERRORS.clear()
        spec_consistency.ERRORS.extend(previous)


def test_spec_consistency_integration_rejects_48_cell_drift(monkeypatch):
    original_read = spec_consistency.read

    def mutated_read(rel_path: str) -> str:
        text = original_read(rel_path)
        if rel_path.endswith("run_plan.schema.json"):
            value = json.loads(text)
            value["properties"]["design"]["properties"][
                "subject_session_cells"
            ]["const"] = 47
            return json.dumps(value)
        return text

    previous = list(spec_consistency.ERRORS)
    spec_consistency.ERRORS.clear()
    monkeypatch.setattr(spec_consistency, "read", mutated_read)
    try:
        spec_consistency.check_ideation_diversity_no_call_contract()
        assert any(
            "subject_session_cells must remain const 48" in error
            for error in spec_consistency.ERRORS
        )
    finally:
        spec_consistency.ERRORS.clear()
        spec_consistency.ERRORS.extend(previous)


@pytest.mark.parametrize(
    "runner_mutation",
    (
        "import requests\n",
        "import http.client\n",
        "import os\nos.system('forbidden')\n",
        "import os as operating\noperating.popen('forbidden')\n",
        "from os import system as launch\nlaunch('forbidden')\n",
        "import subprocess\nsubprocess.run(['forbidden'])\n",
        "import httpx\nhttpx.get('https://example.invalid')\n",
        "__import__('subprocess').run(['forbidden'])\n",
    ),
)
def test_spec_consistency_ast_rejects_transport_or_process_surface(
    monkeypatch, runner_mutation
):
    original_read = spec_consistency.read

    def mutated_read(rel_path: str) -> str:
        text = original_read(rel_path)
        if rel_path == "scripts/run_ideation_diversity_no_call.py":
            return runner_mutation + text
        return text

    previous = list(spec_consistency.ERRORS)
    spec_consistency.ERRORS.clear()
    monkeypatch.setattr(spec_consistency, "read", mutated_read)
    try:
        spec_consistency.check_ideation_diversity_no_call_contract()
        assert any(
            "forbidden import" in error
            or "forbidden process call" in error
            or "forbidden dynamic execution call" in error
            for error in spec_consistency.ERRORS
        )
    finally:
        spec_consistency.ERRORS.clear()
        spec_consistency.ERRORS.extend(previous)
