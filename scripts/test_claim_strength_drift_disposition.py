from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import claim_strength_drift_disposition as runtime


FINAL_DRAFT_RAW = b"# Exact revised draft\n\nBound manuscript bytes.\n"
REVISION_BUNDLE_RAW = b'{"schema_version":"revision-evidence-bundle/1.0"}\n'
HASH_A = hashlib.sha256(FINAL_DRAFT_RAW).hexdigest()
HASH_B = hashlib.sha256(REVISION_BUNDLE_RAW).hexdigest()
HASH_D = "d" * 64


def _finding(index: int, *, round_no: int = 1) -> dict:
    return {
        "finding_id": f"ADV-E6-{index}",
        "finding_type": "STRENGTH-DRIFTED",
        "revision_round": round_no,
        "block_id": f"B{index:04d}",
        "claim_location": f"Discussion paragraph {index}",
        "prior_rung": "association",
        "current_rung": "causal",
        "dropped_qualifier": None,
        "roadmap_item_ids": [f"REV-{index:03d}"],
        "direction": "up",
    }


def _finding_set(count: int = 2) -> dict:
    return {
        "schema_version": "claim-strength-drift-findings/1.0",
        "status": "completed",
        "final_draft_sha256": HASH_A,
        "revision_evidence_bundle_sha256": HASH_B,
        "detection_provenance": {
            "kind": "model_mediated_semantic_review",
            "detector_id": "session-model/exact-build-recorded-elsewhere",
            "protocol_sha256": HASH_D,
        },
        "findings": [_finding(index) for index in range(1, count + 1)],
    }


def _raw(value: dict) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def _event_raw(index: int) -> bytes:
    return f"synthetic raw session event {index}\n".encode()


def _event_raw_map(count: int) -> dict[str, bytes]:
    return {
        f"ASSERTED-EVENT-e6-{index}": _event_raw(index)
        for index in range(1, count + 1)
    }


def _author_input(
    actions: list[str], *, event_paths: list[Path] | None = None
) -> dict:
    events = []
    dispositions = []
    for index, action in enumerate(actions, start=1):
        event_id = f"ASSERTED-EVENT-e6-{index}"
        events.append(
            {
                "event_id": event_id,
                "source_assertion": "session_user_message",
                "actor_role_assertion": "author",
                "raw_session_event_path": str(
                    event_paths[index - 1]
                    if event_paths is not None
                    else Path(f"/synthetic/session-event-{index}.raw")
                ),
                "raw_session_event_sha256": hashlib.sha256(
                    _event_raw(index)
                ).hexdigest(),
            }
        )
        disposition = {
            "finding_id": f"ADV-E6-{index}",
            "session_event_id": event_id,
            "action": action,
        }
        if action == "authorize_with_reason":
            disposition["reason"] = "The stronger wording reflects an explicitly accepted interpretation."
        dispositions.append(disposition)
    return {
        "schema_version": "claim-strength-drift-disposition-input/1.0",
        "session_event_artifacts": events,
        "dispositions": dispositions,
    }


def _build(findings: dict, author_input: dict) -> dict:
    return runtime.build_sidecar(
        findings,
        _raw(findings),
        author_input,
        FINAL_DRAFT_RAW,
        REVISION_BUNDLE_RAW,
        _event_raw_map(len(author_input["dispositions"])),
    )


def _validate(
    findings: dict,
    raw: bytes,
    sidecar: dict,
    event_raw_by_id: dict[str, bytes] | None = None,
) -> None:
    if event_raw_by_id is None:
        event_raw_by_id = _event_raw_map(len(sidecar["dispositions"]))
    runtime.validate_sidecar(
        findings,
        raw,
        sidecar,
        FINAL_DRAFT_RAW,
        REVISION_BUNDLE_RAW,
        event_raw_by_id,
    )


def test_all_authorized_is_the_only_continue_projection() -> None:
    findings = _finding_set()
    raw = _raw(findings)
    sidecar = _build(
        findings, _author_input(["authorize_with_reason", "authorize_with_reason"])
    )

    assert sidecar["pipeline_action"] == "authorized_to_continue"
    assert sidecar["finding_set_sha256"] == hashlib.sha256(raw).hexdigest()
    assert [row["finding_id"] for row in sidecar["dispositions"]] == [
        "ADV-E6-1",
        "ADV-E6-2",
    ]
    _validate(findings, raw, sidecar)


def test_restore_prevents_continuation() -> None:
    findings = _finding_set()
    sidecar = _build(
        findings, _author_input(["authorize_with_reason", "restore"])
    )
    assert sidecar["pipeline_action"] == "restore_required"


def test_pause_dominates_mixed_dispositions() -> None:
    findings = _finding_set()
    sidecar = _build(findings, _author_input(["restore", "pause"]))
    assert sidecar["pipeline_action"] == "paused"


def test_authorization_requires_a_meaningful_reason() -> None:
    findings = _finding_set(1)
    author_input = _author_input(["authorize_with_reason"])
    del author_input["dispositions"][0]["reason"]
    with pytest.raises(runtime.ContractError, match="reason"):
        _build(findings, author_input)

    author_input = _author_input(["authorize_with_reason"])
    author_input["dispositions"][0]["reason"] = "   "
    with pytest.raises(runtime.ContractError, match="letter, number, or symbol"):
        _build(findings, author_input)


def test_proceed_open_and_implicit_acceptance_are_outside_the_contract() -> None:
    findings = _finding_set(1)
    author_input = _author_input(["restore"])
    author_input["dispositions"][0]["action"] = "proceed_open"
    with pytest.raises(runtime.ContractError, match="is not one of"):
        _build(findings, author_input)

    author_input = _author_input(["restore"])
    author_input["dispositions"][0]["reason"] = "An added note cannot turn restore into authorization."
    with pytest.raises(runtime.ContractError, match="should not be valid"):
        _build(findings, author_input)


def test_disposition_must_cover_every_finding_in_order() -> None:
    findings = _finding_set()
    author_input = _author_input(["restore", "restore"])
    author_input["dispositions"].pop()
    author_input["session_event_artifacts"].pop()
    with pytest.raises(runtime.ContractError, match="cover each finding exactly once"):
        _build(findings, author_input)

    author_input = _author_input(["restore", "restore"])
    author_input["dispositions"].reverse()
    with pytest.raises(runtime.ContractError, match="finding order"):
        _build(findings, author_input)


def test_session_event_references_are_closed_and_one_to_one() -> None:
    findings = _finding_set(1)
    author_input = _author_input(["restore"])
    author_input["dispositions"][0]["session_event_id"] = "ASSERTED-EVENT-unknown"
    with pytest.raises(runtime.ContractError, match="unknown session-event"):
        _build(findings, author_input)

    findings = _finding_set()
    author_input = _author_input(["restore", "restore"])
    author_input["dispositions"][1]["session_event_id"] = "ASSERTED-EVENT-e6-1"
    with pytest.raises(runtime.ContractError, match="only one disposition"):
        _build(findings, author_input)


def test_schema_keeps_paths_transient_and_provenance_honest() -> None:
    root = Path(__file__).resolve().parent.parent
    for name in (
        "claim_strength_drift_disposition_input.schema.json",
        "claim_strength_drift_disposition.schema.json",
    ):
        schema = json.loads(
            (root / "shared/contracts/revision" / name).read_text(encoding="utf-8")
        )
        serialized = json.dumps(schema, sort_keys=True)
        assert "raw_session_event_sha256" in serialized
        assert "session_event_id" in serialized
        assert "authenticate" in schema["description"]
    input_schema = json.loads(
        (root / "shared/contracts/revision/claim_strength_drift_disposition_input.schema.json").read_text(
            encoding="utf-8"
        )
    )
    sidecar_schema = json.loads(
        (root / "shared/contracts/revision/claim_strength_drift_disposition.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert "raw_session_event_path" in json.dumps(input_schema, sort_keys=True)
    assert "raw_session_event_path" not in json.dumps(sidecar_schema, sort_keys=True)
    assert "not_authenticated" in json.dumps(sidecar_schema, sort_keys=True)


def test_arbitrary_declared_digest_cannot_authorize_without_exact_raw_bytes() -> None:
    findings = _finding_set(1)
    author_input = _author_input(["authorize_with_reason"])
    author_input["session_event_artifacts"][0]["raw_session_event_sha256"] = "a" * 64
    with pytest.raises(runtime.ContractError, match="does not bind.*raw event bytes"):
        _build(findings, author_input)


def test_sidecar_omits_transient_path_and_raw_message() -> None:
    findings = _finding_set(1)
    author_input = _author_input(["authorize_with_reason"])
    sidecar = _build(findings, author_input)
    serialized = json.dumps(sidecar, sort_keys=True)
    assert author_input["session_event_artifacts"][0]["raw_session_event_path"] not in serialized
    assert _event_raw(1).decode().strip() not in serialized
    binding = sidecar["session_event_bindings"][0]
    assert binding["raw_session_event_sha256"] == hashlib.sha256(_event_raw(1)).hexdigest()
    assert binding["byte_binding"] == "runtime_recomputed_from_explicit_local_artifact"
    assert binding["authenticity_status"] == "not_authenticated"


def test_validate_reopens_exact_event_bytes_and_rejects_digest_only_replay() -> None:
    findings = _finding_set(1)
    raw = _raw(findings)
    sidecar = _build(findings, _author_input(["authorize_with_reason"]))
    with pytest.raises(runtime.ContractError, match="does not bind.*raw event bytes"):
        _validate(
            findings,
            raw,
            sidecar,
            {"ASSERTED-EVENT-e6-1": _event_raw(1) + b"tampered"},
        )
    with pytest.raises(runtime.ContractError, match="exact event-id mapping"):
        _validate(findings, raw, sidecar, {})
    with pytest.raises(runtime.ContractError, match="exact event-id mapping"):
        _validate(
            findings,
            raw,
            sidecar,
            {
                "ASSERTED-EVENT-e6-1": _event_raw(1),
                "ASSERTED-EVENT-extra": b"synthetic extra event\n",
            },
        )


def test_finding_sequence_and_round_order_are_closed() -> None:
    findings = _finding_set()
    findings["findings"][1]["finding_id"] = "ADV-E6-3"
    with pytest.raises(runtime.ContractError, match="complete ordered sequence"):
        _build(findings, _author_input(["restore", "restore"]))

    findings = _finding_set()
    findings["findings"][0]["revision_round"] = 2
    with pytest.raises(runtime.ContractError, match="nondecreasing"):
        _build(findings, _author_input(["restore", "restore"]))


def test_integrity_correction_ids_remain_valid_e6_attribution() -> None:
    findings = _finding_set(1)
    findings["findings"][0]["roadmap_item_ids"] = ["EA-003", "IL-SERIOUS-1"]
    sidecar = _build(findings, _author_input(["restore"]))
    assert sidecar["pipeline_action"] == "restore_required"


def test_sidecar_tampering_breaks_binding_and_projection() -> None:
    findings = _finding_set()
    raw = _raw(findings)
    sidecar = _build(
        findings, _author_input(["authorize_with_reason", "authorize_with_reason"])
    )

    tampered = copy.deepcopy(sidecar)
    tampered["dispositions"][0]["finding_sha256"] = "0" * 64
    with pytest.raises(runtime.ContractError, match="does not bind its finding"):
        _validate(findings, raw, tampered)

    tampered = copy.deepcopy(sidecar)
    tampered["pipeline_action"] = "restore_required"
    with pytest.raises(runtime.ContractError, match="mechanical projection"):
        _validate(findings, raw, tampered)

    tampered = copy.deepcopy(sidecar)
    tampered["session_event_bindings"][0]["raw_session_event_sha256"] = "a" * 64
    with pytest.raises(runtime.ContractError, match="does not bind.*raw event bytes"):
        _validate(findings, raw, tampered)

    with pytest.raises(runtime.ContractError, match="exact finding-set bytes"):
        _validate(findings, raw + b" ", sidecar)


def test_exact_draft_and_bundle_bytes_are_replayed() -> None:
    findings = _finding_set(1)
    author_input = _author_input(["restore"])
    with pytest.raises(runtime.ContractError, match="exact draft bytes"):
        runtime.build_sidecar(
            findings,
            _raw(findings),
            author_input,
            FINAL_DRAFT_RAW + b"changed",
            REVISION_BUNDLE_RAW,
            _event_raw_map(1),
        )
    with pytest.raises(runtime.ContractError, match="exact bundle bytes"):
        runtime.build_sidecar(
            findings,
            _raw(findings),
            author_input,
            FINAL_DRAFT_RAW,
            REVISION_BUNDLE_RAW + b"changed",
            _event_raw_map(1),
        )


def test_empty_or_skipped_finding_set_never_fabricates_author_work() -> None:
    findings = _finding_set(0)
    with pytest.raises(runtime.ContractError, match="no detected E6 finding"):
        _build(findings, _author_input(["restore"]))

    skipped = _finding_set(0)
    skipped["status"] = "skipped_no_revision_evidence"
    skipped["revision_evidence_bundle_sha256"] = None
    with pytest.raises(runtime.ContractError, match="completed E6 finding set"):
        _build(skipped, _author_input(["restore"]))


def test_cli_build_and_validate(tmp_path: Path) -> None:
    findings = _finding_set(1)
    finding_path = tmp_path / "findings.json"
    input_path = tmp_path / "input.json"
    draft_path = tmp_path / "draft.md"
    bundle_path = tmp_path / "revision-evidence-bundle.json"
    sidecar_path = tmp_path / "sidecar.json"
    event_path = tmp_path / "session-event-1.raw"
    finding_path.write_bytes(_raw(findings))
    event_path.write_bytes(_event_raw(1))
    input_path.write_bytes(
        _raw(_author_input(["authorize_with_reason"], event_paths=[event_path]))
    )
    draft_path.write_bytes(FINAL_DRAFT_RAW)
    bundle_path.write_bytes(REVISION_BUNDLE_RAW)

    script = Path(runtime.__file__)
    built = subprocess.run(
        [
            sys.executable,
            str(script),
            "build",
            "--finding-set",
            str(finding_path),
            "--author-input",
            str(input_path),
            "--final-draft",
            str(draft_path),
            "--revision-evidence-bundle",
            str(bundle_path),
            "--output",
            str(sidecar_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert built.returncode == 0, built.stderr
    assert json.loads(built.stdout)["pipeline_action"] == "authorized_to_continue"

    validated = subprocess.run(
        [
            sys.executable,
            str(script),
            "validate",
            "--finding-set",
            str(finding_path),
            "--sidecar",
            str(sidecar_path),
            "--final-draft",
            str(draft_path),
            "--revision-evidence-bundle",
            str(bundle_path),
            "--event-artifact",
            f"ASSERTED-EVENT-e6-1={event_path}",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert validated.returncode == 0, validated.stderr
    assert json.loads(validated.stdout)["status"] == "valid"


def test_cli_event_artifacts_fail_closed_for_missing_symlink_and_duplicate_mapping(
    tmp_path: Path,
) -> None:
    event_path = tmp_path / "event.raw"
    event_path.write_bytes(_event_raw(1))
    missing = tmp_path / "missing.raw"
    with pytest.raises(runtime.ContractError, match="cannot open regular non-symlink"):
        runtime._parse_validate_event_artifacts(
            [f"ASSERTED-EVENT-e6-1={missing}"]
        )

    symlink = tmp_path / "event-link.raw"
    symlink.symlink_to(event_path)
    with pytest.raises(runtime.ContractError, match="cannot open regular non-symlink"):
        runtime._parse_validate_event_artifacts(
            [f"ASSERTED-EVENT-e6-1={symlink}"]
        )

    with pytest.raises(runtime.ContractError, match="duplicates event id"):
        runtime._parse_validate_event_artifacts(
            [
                f"ASSERTED-EVENT-e6-1={event_path}",
                f"ASSERTED-EVENT-e6-1={tmp_path / 'other.raw'}",
            ]
        )


def test_build_loader_rejects_missing_symlink_and_duplicate_files(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing.raw"
    author_input = _author_input(["restore"], event_paths=[missing])
    with pytest.raises(runtime.ContractError, match="cannot open regular non-symlink"):
        runtime._load_build_event_artifacts(author_input)

    event_path = tmp_path / "event.raw"
    event_path.write_bytes(_event_raw(1))
    symlink = tmp_path / "event-link.raw"
    symlink.symlink_to(event_path)
    author_input = _author_input(["restore"], event_paths=[symlink])
    with pytest.raises(runtime.ContractError, match="cannot open regular non-symlink"):
        runtime._load_build_event_artifacts(author_input)

    hardlink = tmp_path / "event-hardlink-validate.raw"
    hardlink.hardlink_to(event_path)
    author_input = _author_input(
        ["restore", "restore"], event_paths=[event_path, hardlink]
    )
    with pytest.raises(runtime.ContractError, match="duplicate file mapping"):
        runtime._load_build_event_artifacts(author_input)

    hardlink = tmp_path / "event-hardlink.raw"
    hardlink.hardlink_to(event_path)
    with pytest.raises(runtime.ContractError, match="duplicate file mapping"):
        runtime._parse_validate_event_artifacts(
            [
                f"ASSERTED-EVENT-e6-1={event_path}",
                f"ASSERTED-EVENT-e6-2={hardlink}",
            ]
        )


def test_e6_authority_docs_do_not_offer_default_open() -> None:
    root = Path(__file__).resolve().parent.parent
    protocol = (root / "academic-pipeline/references/claim_verification_protocol.md").read_text()
    agent = (root / "academic-pipeline/agents/integrity_verification_agent.md").read_text()
    orchestrator = (root / "academic-pipeline/agents/pipeline_orchestrator_agent.md").read_text()

    protocol_e6 = protocol.split("## E6:", 1)[1].split("## Verdict Taxonomy", 1)[0]
    agent_e6 = agent.split("#### E6.", 1)[1].split("### Phase F", 1)[0]
    checkpoint = orchestrator.split("#### MANDATORY Checkpoint Template", 1)[1].split(
        "##### Phase E Evidence-Row Rendering", 1
    )[0]
    for surface in (protocol_e6, agent_e6, checkpoint):
        assert "proceed open (default)" not in surface
    assert "authorize_with_reason" in protocol_e6
    assert "restore_required" in checkpoint
    assert "generic `continue`" in checkpoint
    joined = "\n".join((protocol_e6, agent_e6, checkpoint))
    assert "recompute" in joined
    assert "raw session-event" in joined
    assert "does not authenticate" in joined
    assert "sidecar retains no path or raw message" in joined
