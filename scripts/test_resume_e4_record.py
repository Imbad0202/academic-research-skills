#!/usr/bin/env python3
"""Fail-closed recovery tests for #616 resume-from-bundle."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from scripts import dispatch_e4_panel as harness
from scripts import resume_e4_record as recovery
from scripts import test_dispatch_e4_panel as fixtures


DATE = "2026-08-01"
STEM = f"{DATE}-ms00_clean-post-r1"


def _panel(tmp_path: Path):
    work = tmp_path / "work"
    result, bundle = harness.dispatch_panel(
        fixture="ms00_clean", condition="post", replicate=1,
        work_dir=work, transport=fixtures.scripted(),
        manuscript=fixtures.MANUSCRIPT, metadata=fixtures.METADATA,
        contract_json=fixtures.CONTRACT_JSON,
    )
    assert result.abort is None
    return work, result, bundle


def _failed_emission(tmp_path: Path, monkeypatch):
    work, result, bundle = _panel(tmp_path)
    _force_emission_failure(work, result, bundle, monkeypatch)
    return work, bundle


def _force_emission_failure(work, result, bundle, monkeypatch):
    real_replace = os.replace

    def fail_record_install(source, destination, *args, **kwargs):
        if str(destination).endswith(".json"):
            raise OSError(28, "forced record install failure")
        return real_replace(source, destination, *args, **kwargs)

    monkeypatch.setattr(harness.os, "replace", fail_record_install)
    with pytest.raises(OSError, match="forced"):
        harness.emit(
            result, bundle, work, model_id="test-model",
            suite_commit="deadbeef", date=DATE,
            dispatch_note="scripted", working_tree_dirty=False,
        )
    monkeypatch.setattr(harness.os, "replace", real_replace)
    assert bundle.root.exists()
    assert (bundle.root / harness.RECOVERY_STATE_FILE).is_file()


def test_a_forced_post_bundle_failure_resumes_without_a_model_call(
    tmp_path, monkeypatch,
):
    work, bundle = _failed_emission(tmp_path, monkeypatch)

    def forbidden(*args, **kwargs):
        raise AssertionError("resume must not construct a model transport")

    monkeypatch.setattr(harness, "ClaudeCliTransport", forbidden)
    exit_code = recovery.main([
        "--bundle", str(bundle.root), "--work-dir", str(work),
    ])
    assert exit_code == harness.EXIT_OK
    path = work / "runs" / f"{STEM}.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["score_eligible"] is True
    assert record["measurement_status"] == "completed"
    assert record["suite_commit"] == "deadbeef"
    assert record["dispatch"] == "scripted"


def test_resume_refuses_to_overwrite_an_existing_identity(tmp_path):
    work, result, bundle = _panel(tmp_path)
    path, record = harness.emit(
        result, bundle, work, model_id="test-model",
        suite_commit="deadbeef", date=DATE, dispatch_note="scripted")
    installed = path.parent / record["raw_bundle"]
    with pytest.raises(recovery.RecoveryError, match="already recorded"):
        recovery.resume(installed, work)


def test_resume_refuses_an_existing_blocked_identity(tmp_path, monkeypatch):
    work, bundle = _failed_emission(tmp_path, monkeypatch)
    blocked = work / "runs" / "blocked" / f"{STEM}.json"
    blocked.parent.mkdir(parents=True, exist_ok=True)
    blocked.write_text("{}\n", encoding="utf-8")

    with pytest.raises(recovery.RecoveryError, match="already recorded"):
        recovery.resume(bundle.root, work)

    assert blocked.read_text(encoding="utf-8") == "{}\n"


def test_resume_refuses_a_dangling_record_identity_redirect(tmp_path, monkeypatch):
    work, bundle = _failed_emission(tmp_path, monkeypatch)
    record_path = work / "runs" / f"{STEM}.json"
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.symlink_to(tmp_path / "missing-record-target.json")

    with pytest.raises(recovery.RecoveryError, match="already recorded"):
        recovery.resume(bundle.root, work)

    assert record_path.is_symlink()


def test_resume_refuses_a_dangling_raw_identity_redirect(tmp_path, monkeypatch):
    work, bundle = _failed_emission(tmp_path, monkeypatch)
    raw_path = work / "runs" / "raw" / STEM
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.symlink_to(tmp_path / "missing-raw-target")

    with pytest.raises(recovery.RecoveryError, match="already holds a bundle"):
        recovery.resume(bundle.root, work)

    assert raw_path.is_symlink()


def test_emission_refuses_a_redirected_existing_recovery_state(tmp_path):
    work, result, bundle = _panel(tmp_path)
    external = tmp_path / "external-state.json"
    external.write_text("operator-owned\n", encoding="utf-8")
    (bundle.root / harness.RECOVERY_STATE_FILE).symlink_to(external)

    with pytest.raises(harness.PreconditionFailure, match="symlink"):
        harness.ensure_recovery_state(
            result, bundle, model_id="test-model",
            suite_commit="deadbeef", date=DATE,
            dispatch_note="scripted",
        )

    assert external.read_text(encoding="utf-8") == "operator-owned\n"


def test_resume_refuses_a_changed_preserved_artifact(tmp_path, monkeypatch):
    work, bundle = _failed_emission(tmp_path, monkeypatch)
    (bundle.root / "synthesis.a1.md").write_text(
        "changed after dispatch\n", encoding="utf-8")
    with pytest.raises(recovery.RecoveryError, match="manifest"):
        recovery.resume(bundle.root, work)


def test_resume_refuses_an_inserted_artifact(tmp_path, monkeypatch):
    work, bundle = _failed_emission(tmp_path, monkeypatch)
    (bundle.root / "operator-note.txt").write_text(
        "not part of the retained bundle\n", encoding="utf-8")
    with pytest.raises(recovery.RecoveryError, match="manifest"):
        recovery.resume(bundle.root, work)


def test_resume_refuses_an_inconsistent_completed_stage_ledger(
    tmp_path, monkeypatch,
):
    work, bundle = _failed_emission(tmp_path, monkeypatch)
    state_path = bundle.root / harness.RECOVERY_STATE_FILE
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["result"]["completed_stages"].remove("synthesis")
    state_path.write_text(json.dumps(state, indent=1) + "\n", encoding="utf-8")
    with pytest.raises(recovery.RecoveryError, match="completed stages"):
        recovery.resume(bundle.root, work)


def test_resume_refuses_an_omitted_retry_event(tmp_path, monkeypatch):
    work = tmp_path / "work"
    malformed = fixtures.phase_fixtures.phase1_text("methodology").replace(
        "what_triggers_fatal: fatal evidence pattern for D3", "", 1)
    result, bundle = harness.dispatch_panel(
        fixture="ms00_clean", condition="post", replicate=1,
        work_dir=work,
        transport=fixtures.scripted({"methodology.phase1": [
            malformed, fixtures.phase_fixtures.phase1_text("methodology"),
        ]}),
        manuscript=fixtures.MANUSCRIPT, metadata=fixtures.METADATA,
        contract_json=fixtures.CONTRACT_JSON,
    )
    assert len(result.retries) == 1
    _force_emission_failure(work, result, bundle, monkeypatch)

    state_path = bundle.root / harness.RECOVERY_STATE_FILE
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["result"]["retries"] = []
    state_path.write_text(json.dumps(state, indent=1) + "\n", encoding="utf-8")

    with pytest.raises(recovery.RecoveryError, match="retry ledger"):
        recovery.resume(bundle.root, work)


def test_resume_cannot_turn_a_terminal_synthesis_failure_into_completion(
    tmp_path, monkeypatch,
):
    work = tmp_path / "work"
    broken = fixtures.synthesis_response().replace("D1=pass", "D1=warn")
    result, bundle = harness.dispatch_panel(
        fixture="ms00_clean", condition="post", replicate=1,
        work_dir=work,
        transport=fixtures.scripted({"synthesis": [broken, broken]}),
        manuscript=fixtures.MANUSCRIPT, metadata=fixtures.METADATA,
        contract_json=fixtures.CONTRACT_JSON,
    )
    assert result.abort is not None
    assert "synthesis" not in result.completed_stages
    _force_emission_failure(work, result, bundle, monkeypatch)

    state_path = bundle.root / harness.RECOVERY_STATE_FILE
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["result"]["abort"] = None
    state["result"]["completed_stages"].append("synthesis")
    state_path.write_text(json.dumps(state, indent=1) + "\n", encoding="utf-8")

    with pytest.raises(recovery.RecoveryError, match="dispatch journal"):
        recovery.resume(bundle.root, work)


def test_resume_accepts_the_documented_installed_raw_state(
    tmp_path, monkeypatch,
):
    work, bundle = _failed_emission(tmp_path, monkeypatch)
    installed = work / "runs" / "raw" / STEM
    installed.parent.mkdir(parents=True, exist_ok=True)
    bundle.root.rename(installed)
    path, record = recovery.resume(installed, work)
    assert path.is_file()
    assert record["raw_bundle"] == f"raw/{STEM}/"


def test_resume_refuses_a_bundle_at_an_undeclared_location(
    tmp_path, monkeypatch,
):
    work, bundle = _failed_emission(tmp_path, monkeypatch)
    elsewhere = work / "operator-moved" / "bundle"
    elsewhere.parent.mkdir(parents=True)
    bundle.root.rename(elsewhere)
    with pytest.raises(recovery.RecoveryError, match="supported retained"):
        recovery.resume(elsewhere, work)


def test_resume_accepts_an_extraction_retry_ledger(tmp_path, monkeypatch):
    # #610 step 5: the extraction retry class round-trips through recovery
    # like the phase1 class, with its own record list.
    work = tmp_path / "work"
    malformed = "Let me extract first.\n\n" + fixtures.EXTRACTION_TEXT
    result, bundle = harness.dispatch_panel(
        fixture="ms00_clean", condition="post", replicate=1,
        work_dir=work,
        transport=fixtures.scripted({
            "methodology.extraction": [malformed,
                                       fixtures.EXTRACTION_TEXT],
        }),
        manuscript=fixtures.MANUSCRIPT, metadata=fixtures.METADATA,
        contract_json=fixtures.CONTRACT_JSON,
    )
    assert result.abort is None
    _force_emission_failure(work, result, bundle, monkeypatch)
    assert recovery.main([
        "--bundle", str(bundle.root), "--work-dir", str(work),
    ]) == harness.EXIT_OK
    record = json.loads(
        (work / "runs" / f"{STEM}.json").read_text(encoding="utf-8"))
    assert record["score_eligible"] is True
    events = record["extraction_retries"]
    assert len(events) == 1
    assert events[0]["rejected_response_preserved"] is True


def test_resume_refuses_a_tampered_receipts_artifact(tmp_path, monkeypatch):
    # security round 1, P2-5: the calculator is deterministic, so recovery
    # re-derives the receipts from the gate-passed extraction and refuses
    # a receipts artifact that disagrees.
    work, bundle = _failed_emission(tmp_path, monkeypatch)
    receipts = bundle.root / harness.RECEIPTS_ARTIFACT
    tampered = receipts.read_text(encoding="utf-8").replace(
        "no_recomputable_statistics:", "no_recomputable_statistics: edited"
    )
    receipts.write_text(tampered, encoding="utf-8")
    # The sha256 tree manifest catches a naive tamper first; refresh it in
    # the recovery state so THIS test proves the deeper layer — content
    # tied to the extraction, not to a rewritable manifest.
    state_path = bundle.root / harness.RECOVERY_STATE_FILE
    state = json.loads(state_path.read_text(encoding="utf-8"))
    from scripts import _e4_evidence as e4_evidence
    state["bundle_manifest"] = e4_evidence.tree_manifest(
        bundle.root, exclude={harness.RECOVERY_STATE_FILE})
    state_path.write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(recovery.RecoveryError,
                       match="deterministic re-derivation"):
        recovery.resume(bundle.root, work)


def test_resume_requires_the_identity_gate_witness(tmp_path, monkeypatch):
    # security round 1, P2-5: with the calculator stage in the ledger, a
    # methodology Phase 2 gate log without the RECEIPT-IDENTITY witness is
    # not evidence the contract's identity gate ran.
    work, bundle = _failed_emission(tmp_path, monkeypatch)
    gate = bundle.root / "methodology.phase2.a1.gate.log"
    text = gate.read_text(encoding="utf-8")
    assert "RECEIPT-IDENTITY: PASS" in text
    gate.write_text(
        text.replace("RECEIPT-IDENTITY: PASS\n", ""), encoding="utf-8")
    state_path = bundle.root / harness.RECOVERY_STATE_FILE
    state = json.loads(state_path.read_text(encoding="utf-8"))
    from scripts import _e4_evidence as e4_evidence
    state["bundle_manifest"] = e4_evidence.tree_manifest(
        bundle.root, exclude={harness.RECOVERY_STATE_FILE})
    state_path.write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(recovery.RecoveryError,
                       match="lack response/checker evidence"):
        recovery.resume(bundle.root, work)
