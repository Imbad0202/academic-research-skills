#!/usr/bin/env python3
"""Contract and replay tests for typed review-panel provenance."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import review_panel_provenance as provenance  # noqa: E402


def _seat(
    seat_id: str,
    *,
    role_id: str,
    context_id: str,
    model_family: str = "family-a",
    provider: str = "provider-a",
) -> dict:
    return {
        "seat_id": seat_id,
        "role_id": role_id,
        "context_id": context_id,
        "peer_outputs_visible": False,
        "actor_type": "model",
        "model_family": model_family,
        "provider": provider,
        "human_reviewer_id": None,
    }


def _same_family_manifest() -> dict:
    return {
        "schema_version": provenance.INPUT_VERSION,
        "panel_id": "panel-001",
        "mode": provenance.REVIEW_MODE,
        "contract_id": provenance.CONTRACT_ID,
        "contract_sha256": provenance.CONTRACT_SHA256,
        "seats": [
            _seat("EIC", role_id="eic", context_id="ctx-eic"),
            _seat("R1", role_id="methodology", context_id="ctx-r1"),
            _seat("R2", role_id="domain", context_id="ctx-r2"),
            _seat("R3", role_id="perspective", context_id="ctx-r3"),
            _seat("DA", role_id="da", context_id="ctx-da"),
        ],
    }


@pytest.mark.parametrize(
    "path",
    [
        provenance.INPUT_SCHEMA_PATH,
        provenance.ARTIFACT_SCHEMA_PATH,
        provenance.CARRIER_SCHEMA_PATH,
    ],
)
def test_schemas_are_valid_and_closed(path: Path) -> None:
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    if "additionalProperties" in schema:
        assert schema["additionalProperties"] is False
    else:
        assert schema["oneOf"]


def test_same_family_artifact_keeps_axes_separate_and_discloses_risk() -> None:
    artifact = provenance.build_artifact(_same_family_manifest())

    assert artifact["axes"] == {
        "role_separated": True,
        "fresh_context": True,
        "blind_to_peer_outputs": True,
        "model_family_distinct": False,
        "provider_distinct": False,
        "human_distinct": False,
    }
    assert artifact["independence_claim"] == "not_computed_from_personas"
    assert "independent" not in artifact
    assert artifact["mode"] == provenance.REVIEW_MODE
    assert artifact["contract_id"] == provenance.CONTRACT_ID
    assert artifact["contract_sha256"] == provenance.CONTRACT_SHA256
    assert artifact["fresh_context_scope"] == provenance.FRESH_CONTEXT_SCOPE
    assert artifact["correlated_error_disclosure"] == {
        "required": True,
        "reason": "same_model_family",
        "text": provenance.SAME_FAMILY_TEXT,
    }
    assert provenance.validate_artifact(artifact) == []


def test_cross_family_and_provider_are_independent_typed_axes() -> None:
    manifest = _same_family_manifest()
    manifest["seats"][1]["model_family"] = "family-b"
    artifact = provenance.build_artifact(manifest)

    assert artifact["axes"]["model_family_distinct"] is True
    assert artifact["axes"]["provider_distinct"] is False
    assert artifact["correlated_error_disclosure"] == {
        "required": False,
        "reason": "multiple_model_families",
        "text": None,
    }


def test_execution_topology_is_stable_across_fresh_context_ids_only() -> None:
    first = provenance.build_artifact(_same_family_manifest())
    second_manifest = _same_family_manifest()
    for index, seat in enumerate(second_manifest["seats"], start=1):
        seat["context_id"] = f"fresh-context-{index}"
    second = provenance.build_artifact(second_manifest)
    assert first["normalized_manifest_sha256"] != second["normalized_manifest_sha256"]
    assert first["execution_topology_sha256"] == second["execution_topology_sha256"]

    second_manifest["seats"][1]["model_family"] = "family-b"
    changed = provenance.build_artifact(second_manifest)
    assert changed["execution_topology_sha256"] != first["execution_topology_sha256"]


def test_missing_observations_normalize_to_unknown_without_inference() -> None:
    manifest = {
        "schema_version": provenance.INPUT_VERSION,
        "panel_id": "panel-missing",
        "mode": provenance.REVIEW_MODE,
        "contract_id": provenance.CONTRACT_ID,
        "contract_sha256": provenance.CONTRACT_SHA256,
        "seats": [
            {"seat_id": "EIC", "actor_type": "model"},
            {"seat_id": "R1"},
            {"seat_id": "R2"},
            {"seat_id": "R3"},
            {"seat_id": "DA"},
        ],
    }
    artifact = provenance.build_artifact(manifest)

    assert artifact["seats"][0]["role_id"] is None
    assert artifact["seats"][1]["actor_type"] == "unknown"
    for axis in (
        "role_separated",
        "fresh_context",
        "blind_to_peer_outputs",
        "model_family_distinct",
        "provider_distinct",
        "human_distinct",
    ):
        assert artifact["axes"][axis] == "unknown", axis
    assert artifact["correlated_error_disclosure"] == {
        "required": True,
        "reason": "model_family_unknown",
        "text": provenance.UNKNOWN_FAMILY_TEXT,
    }


def test_one_observed_peer_output_proves_panel_was_not_blind() -> None:
    manifest = _same_family_manifest()
    manifest["seats"][1]["peer_outputs_visible"] = True
    manifest["seats"][2].pop("peer_outputs_visible")
    artifact = provenance.build_artifact(manifest)
    assert artifact["axes"]["blind_to_peer_outputs"] is False


def test_reused_role_or_context_proves_separation_axis_false() -> None:
    manifest = _same_family_manifest()
    manifest["seats"][2]["role_id"] = manifest["seats"][1]["role_id"]
    manifest["seats"][2]["context_id"] = manifest["seats"][1]["context_id"]
    axes = provenance.build_artifact(manifest)["axes"]
    assert axes["role_separated"] is False
    assert axes["fresh_context"] is False


def test_two_distinct_humans_can_be_proven_without_model_diversity() -> None:
    manifest = {
        "schema_version": provenance.INPUT_VERSION,
        "panel_id": "panel-human",
        "mode": provenance.REVIEW_MODE,
        "contract_id": provenance.CONTRACT_ID,
        "contract_sha256": provenance.CONTRACT_SHA256,
        "seats": [
            {
                "seat_id": "EIC",
                "role_id": "eic",
                "context_id": "ctx-eic",
                "peer_outputs_visible": False,
                "actor_type": "human",
                "human_reviewer_id": "human-a",
            },
            {
                "seat_id": "R1",
                "role_id": "methodology",
                "context_id": "ctx-r1",
                "peer_outputs_visible": False,
                "actor_type": "human",
                "human_reviewer_id": "human-b",
            },
            {
                "seat_id": "R2",
                "role_id": "domain",
                "context_id": "ctx-r2",
                "peer_outputs_visible": False,
                "actor_type": "human",
                "human_reviewer_id": "human-c",
            },
            {
                "seat_id": "R3",
                "role_id": "perspective",
                "context_id": "ctx-r3",
                "peer_outputs_visible": False,
                "actor_type": "human",
                "human_reviewer_id": "human-d",
            },
            {
                "seat_id": "DA",
                "role_id": "da",
                "context_id": "ctx-da",
                "peer_outputs_visible": False,
                "actor_type": "human",
                "human_reviewer_id": "human-e",
            },
        ],
    }
    axes = provenance.build_artifact(manifest)["axes"]
    assert axes["human_distinct"] is True
    assert axes["model_family_distinct"] == "unknown"
    assert axes["provider_distinct"] == "unknown"


def test_persona_labels_never_create_binary_independence() -> None:
    artifact = provenance.build_artifact(_same_family_manifest())
    assert artifact["axes"]["role_separated"] is True
    assert artifact["independence_claim"] == "not_computed_from_personas"

    schema = provenance._load_schema(provenance.ARTIFACT_SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    mutated = copy.deepcopy(artifact)
    mutated["independent"] = True
    assert list(validator.iter_errors(mutated))


def test_seat_level_independence_field_is_rejected() -> None:
    manifest = _same_family_manifest()
    manifest["seats"][0]["independent"] = True
    with pytest.raises(provenance.ProvenanceError, match="Additional properties"):
        provenance.build_artifact(manifest)


def test_replay_validator_rejects_tampered_axis() -> None:
    artifact = provenance.build_artifact(_same_family_manifest())
    artifact["axes"]["fresh_context"] = False
    errors = provenance.validate_artifact(artifact)
    assert any("axes" in error and "deterministic replay" in error for error in errors)


def test_replay_validator_rejects_tampered_topology_digest() -> None:
    artifact = provenance.build_artifact(_same_family_manifest())
    artifact["execution_topology_sha256"] = "0" * 64
    errors = provenance.validate_artifact(artifact)
    assert any("execution_topology_sha256" in error for error in errors)


def test_schema_rejects_suppressed_same_family_disclosure() -> None:
    artifact = provenance.build_artifact(_same_family_manifest())
    artifact["correlated_error_disclosure"] = {
        "required": False,
        "reason": "multiple_model_families",
        "text": None,
    }
    errors = provenance.validate_artifact(artifact)
    assert errors
    assert any("correlated_error_disclosure" in error for error in errors)


def test_omitted_and_explicit_unknown_observations_have_same_digest() -> None:
    omitted = {
        "schema_version": provenance.INPUT_VERSION,
        "panel_id": "panel-canonical",
        "mode": provenance.REVIEW_MODE,
        "contract_id": provenance.CONTRACT_ID,
        "contract_sha256": provenance.CONTRACT_SHA256,
        "seats": [{"seat_id": seat_id} for seat_id in provenance.EXPECTED_ROSTER],
    }
    explicit = copy.deepcopy(omitted)
    for seat in explicit["seats"]:
        seat.update(
            {
                "role_id": None,
                "context_id": None,
                "peer_outputs_visible": None,
                "actor_type": "unknown",
                "model_family": None,
                "provider": None,
                "human_reviewer_id": None,
            }
        )
    assert (
        provenance.build_artifact(omitted)["normalized_manifest_sha256"]
        == provenance.build_artifact(explicit)["normalized_manifest_sha256"]
    )


def test_duplicate_seat_id_is_rejected() -> None:
    manifest = _same_family_manifest()
    manifest["seats"][1]["seat_id"] = "EIC"
    with pytest.raises(provenance.ProvenanceError, match="EIC|R1"):
        provenance.build_artifact(manifest)


def test_actor_identity_contradiction_is_rejected_without_guessing() -> None:
    manifest = _same_family_manifest()
    manifest["seats"][0]["human_reviewer_id"] = "human-a"
    with pytest.raises(provenance.ProvenanceError, match="use 'hybrid'"):
        provenance.build_artifact(manifest)


def test_model_identity_requires_canonical_lower_case_dispatch_id() -> None:
    manifest = _same_family_manifest()
    manifest["seats"][0]["model_family"] = "Family A"
    with pytest.raises(provenance.ProvenanceError, match="not valid"):
        provenance.build_artifact(manifest)


def test_manifest_binds_exact_mode_contract_and_raw_contract_bytes() -> None:
    assert (
        provenance._raw_sha256(provenance.FULL_CONTRACT_PATH.read_bytes())
        == provenance.CONTRACT_SHA256
    )
    for field, value in (
        ("mode", "reviewer_methodology_focus"),
        ("contract_id", "reviewer/reviewer_methodology_focus/v2"),
        ("contract_sha256", "0" * 64),
    ):
        manifest = _same_family_manifest()
        manifest[field] = value
        with pytest.raises(provenance.ProvenanceError):
            provenance.build_artifact(manifest)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda seats: seats.pop(),
        lambda seats: seats.append(copy.deepcopy(seats[-1])),
        lambda seats: seats.__setitem__(1, copy.deepcopy(seats[2])),
        lambda seats: seats.reverse(),
    ],
)
def test_manifest_rejects_any_noncanonical_five_seat_roster(mutate) -> None:
    manifest = _same_family_manifest()
    mutate(manifest["seats"])
    with pytest.raises(provenance.ProvenanceError):
        provenance.build_artifact(manifest)


def test_fresh_context_is_scoped_to_one_panel_attempt_not_history() -> None:
    first = provenance.build_artifact(_same_family_manifest())
    repeated_contexts = _same_family_manifest()
    repeated_contexts["panel_id"] = "panel-002"
    second = provenance.build_artifact(repeated_contexts)

    assert first["axes"]["fresh_context"] is True
    assert second["axes"]["fresh_context"] is True
    assert first["fresh_context_scope"] == "within_panel_attempt_only"
    assert second["fresh_context_scope"] == "within_panel_attempt_only"
    assert first["normalized_manifest_sha256"] != second["normalized_manifest_sha256"]


def _write_artifact(tmp_path: Path) -> tuple[Path, dict, dict]:
    artifact = provenance.build_artifact(_same_family_manifest())
    artifact_path = tmp_path / "panel.json"
    artifact_path.write_text(
        json.dumps(artifact, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    carrier = provenance.build_carrier(artifact_path, artifact_ref="panel.json")
    return artifact_path, artifact, carrier


def test_schema6_valid_carrier_verifies_raw_bytes_and_replay(tmp_path: Path) -> None:
    artifact_path, artifact, carrier = _write_artifact(tmp_path)
    assert carrier == {
        "schema_version": provenance.CARRIER_VERSION,
        "status": "valid",
        "review_mode": provenance.REVIEW_MODE,
        "artifact_path": "panel.json",
        "artifact_sha256": provenance._raw_sha256(artifact_path.read_bytes()),
        "normalized_manifest_sha256": artifact["normalized_manifest_sha256"],
        "execution_topology_sha256": artifact["execution_topology_sha256"],
        "fresh_context_scope": provenance.FRESH_CONTEXT_SCOPE,
        "axes": artifact["axes"],
    }
    assert provenance.verify_carrier(carrier, tmp_path) == (None, [])


def test_carrier_detects_raw_byte_digest_drift_even_when_json_is_same(
    tmp_path: Path,
) -> None:
    artifact_path, _artifact, carrier = _write_artifact(tmp_path)
    artifact_path.write_bytes(artifact_path.read_bytes() + b"\n")
    state, errors = provenance.verify_carrier(carrier, tmp_path)
    assert state == "digest_mismatch"
    assert errors


def test_carrier_detects_artifact_replay_drift_after_digest_is_updated(
    tmp_path: Path,
) -> None:
    artifact_path, artifact, carrier = _write_artifact(tmp_path)
    artifact["axes"]["fresh_context"] = False
    artifact_path.write_text(
        json.dumps(artifact, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    carrier["artifact_sha256"] = provenance._raw_sha256(artifact_path.read_bytes())
    state, errors = provenance.verify_carrier(carrier, tmp_path)
    assert state == "replay_invalid"
    assert errors


@pytest.mark.parametrize(
    "field",
    ["normalized_manifest_sha256", "execution_topology_sha256", "axes"],
)
def test_carrier_rejects_metadata_that_differs_from_replayed_artifact(
    tmp_path: Path, field: str
) -> None:
    _artifact_path, _artifact, carrier = _write_artifact(tmp_path)
    if field == "axes":
        carrier[field] = copy.deepcopy(carrier[field])
        carrier[field]["blind_to_peer_outputs"] = False
    else:
        carrier[field] = "0" * 64
    state, errors = provenance.verify_carrier(carrier, tmp_path)
    assert state == "replay_invalid"
    assert any(field in error for error in errors)


@pytest.mark.parametrize(
    "reason",
    [
        "absent",
        "unreachable",
        "digest_mismatch",
        "schema_invalid",
        "replay_invalid",
    ],
)
def test_invalid_carrier_is_closed_unknown_only_and_fail_visible(reason: str) -> None:
    carrier = provenance.invalid_carrier(reason)
    assert carrier["status"] == "invalid"
    assert carrier["axes"] == {axis: "unknown" for axis in provenance.AXIS_NAMES}
    assert "artifact_path" not in carrier
    assert "artifact_sha256" not in carrier
    assert provenance.verify_carrier(carrier, Path(".")) == (reason, [])

    mutated = copy.deepcopy(carrier)
    mutated["artifact_sha256"] = "0" * 64
    state, errors = provenance.verify_carrier(mutated, Path("."))
    assert state == "schema_invalid"
    assert errors


def test_build_carrier_turns_absent_unreachable_and_invalid_into_typed_states(
    tmp_path: Path,
) -> None:
    assert provenance.build_carrier(None)["reason"] == "absent"
    assert provenance.build_carrier(tmp_path / "missing.json")["reason"] == "unreachable"
    malformed = tmp_path / "malformed.json"
    malformed.write_text("{", encoding="utf-8")
    assert provenance.build_carrier(malformed)["reason"] == "schema_invalid"


def test_schema6_mode_binding_is_closed_and_requires_full_carrier(
    tmp_path: Path,
) -> None:
    _artifact_path, _artifact, carrier = _write_artifact(tmp_path)
    schema6 = {"review_panel_provenance": carrier}
    assert provenance.validate_schema6_binding(
        schema6, provenance.REVIEW_MODE, tmp_path
    ) == (None, [])

    state, errors = provenance.validate_schema6_binding(
        {}, provenance.REVIEW_MODE, tmp_path
    )
    assert state == "absent"
    assert errors

    for mode in provenance.SCHEMA6_MODES - {provenance.REVIEW_MODE}:
        assert provenance.validate_schema6_binding({}, mode, tmp_path) == (None, [])
        state, errors = provenance.validate_schema6_binding(schema6, mode, tmp_path)
        assert state == "schema_invalid"
        assert errors

    state, errors = provenance.validate_schema6_binding({}, "reviewer_other", tmp_path)
    assert state == "schema_invalid"
    assert errors


def test_carrier_rejects_unsafe_or_escaping_artifact_reference(tmp_path: Path) -> None:
    _artifact_path, _artifact, carrier = _write_artifact(tmp_path)
    for unsafe in ("../panel.json", "/panel.json", "nested//panel.json"):
        mutated = copy.deepcopy(carrier)
        mutated["artifact_path"] = unsafe
        state, errors = provenance.verify_carrier(mutated, tmp_path)
        assert state == "schema_invalid"
        assert errors


def test_cli_build_then_validate(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    artifact_path = tmp_path / "artifact.json"
    manifest_path.write_text(json.dumps(_same_family_manifest()), encoding="utf-8")
    script = SCRIPTS / "review_panel_provenance.py"

    built = subprocess.run(
        [sys.executable, str(script), "build", str(manifest_path), "--output", str(artifact_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert built.returncode == 0, built.stderr
    validated = subprocess.run(
        [sys.executable, str(script), "validate", str(artifact_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert validated.returncode == 0, validated.stderr
    assert "PASS" in validated.stdout


def test_documented_surfaces_bind_the_typed_contract() -> None:
    template = (
        REPO_ROOT / "academic-paper-reviewer/templates/editorial_decision_template.md"
    ).read_text(encoding="utf-8")
    protocol = (
        REPO_ROOT
        / "academic-paper-reviewer/references/review_panel_provenance_protocol.md"
    ).read_text(encoding="utf-8")
    cross_model = (REPO_ROOT / "shared/cross_model_verification.md").read_text(
        encoding="utf-8"
    )

    for axis in (
        "role_separated",
        "fresh_context",
        "blind_to_peer_outputs",
        "model_family_distinct",
        "provider_distinct",
        "human_distinct",
    ):
        assert axis in template
        assert axis in protocol
        assert axis in cross_model
    assert "not_computed_from_personas" in protocol
    assert "Exactly one of:" not in template
    assert "scripts/review_panel_provenance.py" in cross_model
