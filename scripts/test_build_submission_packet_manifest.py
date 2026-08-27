#!/usr/bin/env python3
"""Hermetic contract, replay, and adversarial tests for issue #667."""
from __future__ import annotations

import ast
import copy
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

import pytest
from jsonschema import Draft202012Validator, FormatChecker

import build_submission_packet_manifest as packet_runtime
from build_submission_packet_manifest import (
    ContractError,
    build_submission_packet_manifest,
    observe_submission_packet,
    render_submission_packet_manifest,
    validate_submission_packet_inventory,
    validate_submission_packet_manifest,
)
from resolve_human_subjects_authority import digest, resolve


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "scripts" / "fixtures" / "submission_packet_manifest"
PACKET_ROOT = FIXTURES / "packet"
BASE_INVENTORY = FIXTURES / "base_inventory.json"
AUTHORITY_FIXTURES = REPO_ROOT / "scripts" / "fixtures" / "human_subjects_authority"
REGISTRY_PATH = REPO_ROOT / "shared" / "human_subjects_authority_registry.json"
CONTRACTS = REPO_ROOT / "shared" / "contracts" / "human_subjects"
RUNTIME = REPO_ROOT / "scripts" / "build_submission_packet_manifest.py"

INVENTORY_SCHEMA = "submission_packet_inventory.schema.json"
MANIFEST_SCHEMA = "submission_packet_manifest.schema.json"
BOUNDARY_FOOTER = (
    "Human-subjects boundary: This output does not authorize recruitment, "
    "consent, access to identifiable data, intervention, or data collection."
)
RENDERED_BOUNDARY = (
    "> **Human-subjects boundary:** This output does not authorize recruitment, "
    "consent, access to identifiable data, intervention, or data collection."
)
ENVELOPE_EXPECTED = {
    "packet_v1.non_clinical": True,
    "packet_v1.single_institution": True,
    "packet_v1.competent_adults_only": True,
    "packet_v1.biospecimens_involved": False,
    "packet_v1.regulated_clinical_trial": False,
    "packet_v1.cross_border_material_transfer": False,
    "packet_v1.multisite_reliance": False,
}


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _inventory() -> dict[str, Any]:
    return _json(BASE_INVENTORY)


def _registry() -> dict[str, Any]:
    return _json(REGISTRY_PATH)


def _context(name: str = "us-gdpr-two-axis.json") -> dict[str, Any]:
    context = _json(AUTHORITY_FIXTURES / name)
    known = {row["fact_id"] for row in context["declared_facts"]}
    for fact_id, value in ENVELOPE_EXPECTED.items():
        if fact_id not in known:
            context["declared_facts"].append(
                {
                    "fact_id": fact_id,
                    "value_type": "boolean",
                    "state": "declared",
                    "value": value,
                    "provenance": "author_declared",
                }
            )
    return context


def _authority(
    name: str = "us-gdpr-two-axis.json",
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    context = _context(name)
    registry = _registry()
    return context, registry, resolve(context, registry)


def _build(
    inventory: dict[str, Any] | None = None,
    packet_root: Path = PACKET_ROOT,
    context: dict[str, Any] | None = None,
    registry: dict[str, Any] | None = None,
    resolved: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if context is None and registry is None and resolved is None:
        context, registry, resolved = _authority()
    return build_submission_packet_manifest(
        _inventory() if inventory is None else inventory,
        packet_root,
        context=context,
        registry=registry,
        resolved=resolved,
    )


def _validator(name: str) -> Draft202012Validator:
    schema = _json(CONTRACTS / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _artifact(inventory: dict[str, Any], artifact_id: str) -> dict[str, Any]:
    return next(row for row in inventory["artifacts"] if row["artifact_id"] == artifact_id)


def _entry(
    manifest: dict[str, Any], requirement_id: str, evidence_id: str | None = None
) -> dict[str, Any]:
    matches = [
        row
        for row in manifest["entries"]
        if row["requirement_ref"]["requirement_id"] == requirement_id
        and (
            evidence_id is None
            or row["evidence_ref"]["evidence_id"] == evidence_id
        )
    ]
    assert len(matches) == 1, (requirement_id, evidence_id, matches)
    return matches[0]


def _all_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        return set(value) | set().union(*(_all_keys(item) for item in value.values()), set())
    if isinstance(value, list):
        return set().union(*(_all_keys(item) for item in value), set())
    return set()


def _repin_manifest(manifest: dict[str, Any]) -> None:
    manifest.pop("manifest_digest", None)
    manifest["manifest_digest"] = digest(manifest)


def _repin_overlay(context: dict[str, Any], overlay: dict[str, Any]) -> None:
    unsigned = copy.deepcopy(overlay)
    unsigned.pop("overlay_digest", None)
    overlay["overlay_digest"] = digest(unsigned)
    selected = next(
        row
        for row in context["selected_overlays"]
        if row["overlay_id"] == overlay["overlay_id"]
    )
    selected["overlay_digest"] = overlay["overlay_digest"]
    display = next(
        row
        for axis in context["display_precedence"]
        for row in axis["ordered_authorities"]
        if row["authority_id"] == overlay["overlay_id"]
    )
    display["authority_digest"] = overlay["overlay_digest"]


def _repin_profile(context: dict[str, Any], profile: dict[str, Any]) -> None:
    unsigned = copy.deepcopy(profile)
    unsigned.pop("profile_digest", None)
    profile["profile_digest"] = digest(unsigned)
    selected = next(
        row
        for row in context["selected_profiles"]
        if row["profile_id"] == profile["profile_id"]
    )
    selected["profile_digest"] = profile["profile_digest"]
    display = next(
        row
        for axis in context["display_precedence"]
        for row in axis["ordered_authorities"]
        if row["authority_kind"] == "profile"
        and row["authority_id"] == profile["profile_id"]
    )
    display["authority_digest"] = profile["profile_digest"]


def _packet_copy(tmp_path: Path) -> Path:
    target = tmp_path / "packet"
    shutil.copytree(PACKET_ROOT, target)
    return target


def _reason_codes(manifest: dict[str, Any]) -> set[str]:
    return {row["code"] for row in manifest["unresolved_reasons"]}


def _synthetic_overlay_authority() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]
]:
    """Add test-only certificate and exactly profiled waiver rows."""
    context = _context()
    registry = _registry()
    us_profile = next(
        row
        for row in registry["profiles"]
        if row["profile_id"] == "us.hhs.45-cfr-46.subpart-a"
    )
    template = next(
        row
        for row in us_profile["requirements"]
        if row["requirement_id"] == "us.45cfr46.116.informed-consent"
    )
    base = copy.deepcopy(template)
    base.update(
        {
            "requirement_id": "synthetic.packet.base-consent",
            "title": "Synthetic packet base attachment",
            "summary": "Test-only structural attachment row.",
            "obligated_actor": "investigator",
            "consumer_scopes": ["submission_packet"],
            "applies_if": {
                "op": "fact_equals",
                "fact_id": "activity.human_subjects",
                "value": True,
            },
            "structured_expectations": [
                {
                    "field_id": "synthetic.prose-meaning-must-never-be-read",
                    "operator": "present",
                    "value": True,
                }
            ],
            "evidence_expected": [
                {
                    "evidence_id": "synthetic.base-consent",
                    "held_by": "investigator",
                    "artifact_type": "consent_materials",
                    "description": "Test-only base attachment.",
                }
            ],
            "waiver_or_exception_route": {
                "state": "profiled",
                "requirement_ids": ["synthetic.packet.waiver-route"],
                "decision_maker_role": "institutional_review_office",
            },
            "interaction": {
                "collision_key": "synthetic.packet.base",
                "policy": "parallel_authorities",
            },
        }
    )
    route = copy.deepcopy(template)
    route.update(
        {
            "requirement_id": "synthetic.packet.waiver-route",
            "title": "Synthetic profiled route record",
            "summary": "Test-only route evidence row.",
            "obligated_actor": "investigator",
            "consumer_scopes": ["submission_packet"],
            "applies_if": {
                "op": "fact_equals",
                "fact_id": "activity.human_subjects",
                "value": True,
            },
            "structured_expectations": [],
            "evidence_expected": [
                {
                    "evidence_id": "synthetic.waiver-decision",
                    "held_by": "investigator",
                    "artifact_type": "training_certificate",
                    "description": "Test-only located decision artifact.",
                }
            ],
            "waiver_or_exception_route": {
                "state": "not_applicable",
                "requirement_ids": [],
                "decision_maker_role": None,
            },
            "interaction": {
                "collision_key": "synthetic.packet.route",
                "policy": "parallel_authorities",
            },
        }
    )
    overlay = {
        "overlay_id": "synthetic.institution.packet-routes",
        "overlay_version": "1.0",
        "overlay_digest": "0" * 64,
        "overlay_kind": "institutional",
        "axis": "review_ethics",
        "issuer": "Synthetic Institution",
        "title": "Synthetic packet route overlay",
        "authority_scope_ids": list(us_profile["authority_scope_ids"]),
        "target_profiles": [
            {
                "axis": us_profile["axis"],
                "profile_id": us_profile["profile_id"],
                "profile_version": us_profile["profile_version"],
                "profile_digest": us_profile["profile_digest"],
            }
        ],
        "source_ids": list(us_profile["source_ids"]),
        "operation": "add",
        "requirements_removed": False,
        "requirements": [base, route],
    }
    unsigned = copy.deepcopy(overlay)
    unsigned.pop("overlay_digest")
    overlay["overlay_digest"] = digest(unsigned)
    registry["overlays"].append(overlay)
    context["overlay_selection_state"]["institutional"] = "selected"
    context["selected_overlays"].append(
        {
            "overlay_kind": "institutional",
            "axis": "review_ethics",
            "overlay_id": overlay["overlay_id"],
            "overlay_version": overlay["overlay_version"],
            "overlay_digest": overlay["overlay_digest"],
        }
    )
    review = next(
        row for row in context["display_precedence"] if row["axis"] == "review_ethics"
    )
    review["ordered_authorities"].append(
        {
            "authority_kind": "institutional_overlay",
            "axis": "review_ethics",
            "authority_id": overlay["overlay_id"],
            "authority_version": overlay["overlay_version"],
            "authority_digest": overlay["overlay_digest"],
        }
    )
    return context, registry, resolve(context, registry), overlay


def _waiver_inventory() -> dict[str, Any]:
    inventory = _inventory()
    inventory["waiver_or_exception_claims"] = [
        {
            "requirement_id": "synthetic.packet.base-consent",
            "route_requirement_ids": ["synthetic.packet.waiver-route"],
            "decision_artifact_id": "fixture.training-certificate",
            "declared_by": "author",
        }
    ]
    return inventory


def test_schemas_and_base_inventory_are_closed_and_valid() -> None:
    for name in (INVENTORY_SCHEMA, MANIFEST_SCHEMA):
        Draft202012Validator.check_schema(_json(CONTRACTS / name))
    inventory = _inventory()
    _validator(INVENTORY_SCHEMA).validate(inventory)
    validate_submission_packet_inventory(inventory)


def test_all_seven_capability_facts_are_registry_catalogued_booleans() -> None:
    definitions = {row["fact_id"]: row for row in _registry()["fact_definitions"]}
    assert set(ENVELOPE_EXPECTED) <= set(definitions)
    for fact_id in ENVELOPE_EXPECTED:
        assert definitions[fact_id]["value_type"] == "boolean"
        assert definitions[fact_id]["allowed_values"] is None


def test_base_fixture_observation_is_explicit_and_scan_free() -> None:
    observed = observe_submission_packet(_inventory(), PACKET_ROOT)
    assert {row["artifact_id"] for row in observed} == {
        "fixture.us-consent",
        "fixture.tw-consent",
        "fixture.training-certificate",
    }


def test_manifest_schema_and_deterministic_replay_pass() -> None:
    inventory = _inventory()
    context, registry, resolved = _authority()
    manifest = _build(inventory, PACKET_ROOT, context, registry, resolved)
    _validator(MANIFEST_SCHEMA).validate(manifest)
    validate_submission_packet_manifest(
        manifest,
        inventory,
        PACKET_ROOT,
        context=context,
        registry=registry,
        resolved=resolved,
    )


@pytest.mark.parametrize(
    "mutate",
    [
        lambda value: value.__setitem__("unknown", True),
        lambda value: value["artifacts"].append(copy.deepcopy(value["artifacts"][0])),
        lambda value: value["artifacts"][1].__setitem__(
            "relative_path", value["artifacts"][0]["relative_path"]
        ),
        lambda value: value["artifacts"][0]["evidence_bindings"].append(
            copy.deepcopy(value["artifacts"][0]["evidence_bindings"][0])
        ),
        lambda value: value["packet_responsibility_role_ids"].append(
            value["packet_responsibility_role_ids"][0]
        ),
        lambda value: value["authorization_status_input"].update(
            {"value": "not_provided", "source_reference": "invented.source"}
        ),
        lambda value: value["artifacts"][0]["declared_structure"].update(
            {"document_date": "2026-02-30"}
        ),
        lambda value: value["artifacts"][0].update({"declared_size_bytes": True}),
    ],
)
def test_inventory_closed_shape_and_semantic_duplicates_fail(
    mutate: Callable[[dict[str, Any]], None]
) -> None:
    inventory = _inventory()
    mutate(inventory)
    with pytest.raises(ContractError):
        validate_submission_packet_inventory(inventory)


@pytest.mark.parametrize(
    "relative_path",
    [
        "/absolute.txt",
        "../escape.txt",
        "a/../escape.txt",
        "a/./file.txt",
        "a//file.txt",
        "a\\file.txt",
        "C:/drive.txt",
        ".",
        "folder/",
        "\u202efile.txt",
    ],
)
def test_inventory_paths_must_be_normalized_relative_posix(
    relative_path: str,
) -> None:
    inventory = _inventory()
    inventory["artifacts"][0]["relative_path"] = relative_path
    with pytest.raises(ContractError):
        validate_submission_packet_inventory(inventory)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda value: value.__setitem__("inventory_id", "valid.id\n"),
        lambda value: value["artifacts"][0]["declared_structure"].__setitem__(
            "version_id", "v1\n"
        ),
        lambda value: value["artifacts"][0].__setitem__(
            "declared_sha256", "0" * 64 + "\n"
        ),
        lambda value: value["artifacts"][0].__setitem__(
            "relative_path", "consent-materials.txt\n"
        ),
        lambda value: value["artifacts"][0].__setitem__(
            "media_type", "text/plain\n"
        ),
        lambda value: value["artifacts"][0]["declared_structure"].__setitem__(
            "document_date", "2026-W01-1"
        ),
    ],
)
def test_inventory_schema_runtime_absolute_end_parity(
    mutate: Callable[[dict[str, Any]], None]
) -> None:
    inventory = _inventory()
    mutate(inventory)
    assert list(_validator(INVENTORY_SCHEMA).iter_errors(inventory))
    with pytest.raises(ContractError):
        validate_submission_packet_inventory(inventory)


def test_lone_surrogate_path_fails_schema_public_validation_and_context_free_build() -> None:
    inventory = _inventory()
    inventory["artifacts"][0]["relative_path"] = "surrogate-\ud800.txt"
    assert list(_validator(INVENTORY_SCHEMA).iter_errors(inventory))
    with pytest.raises(ContractError, match="surrogate"):
        validate_submission_packet_inventory(inventory)
    with pytest.raises(ContractError, match="surrogate"):
        build_submission_packet_manifest(inventory, PACKET_ROOT)
    manifest = _build()
    manifest["packet_observations"][0]["relative_path"] = "surrogate-\ud800.txt"
    assert list(_validator(MANIFEST_SCHEMA).iter_errors(manifest))
    with pytest.raises(ContractError, match="canonical JSON"):
        render_submission_packet_manifest(manifest)


def test_reserved_format_control_fails_schema_and_runtime_on_both_contracts() -> None:
    reserved_format_control = "\U00013439"
    inventory = _inventory()
    inventory["artifacts"][0]["relative_path"] = (
        f"reserved-{reserved_format_control}.txt"
    )
    assert list(_validator(INVENTORY_SCHEMA).iter_errors(inventory))
    with pytest.raises(ContractError, match="format"):
        validate_submission_packet_inventory(inventory)
    with pytest.raises(ContractError, match="format"):
        build_submission_packet_manifest(inventory, PACKET_ROOT)

    manifest = _build()
    manifest["packet_observations"][0]["relative_path"] = (
        f"reserved-{reserved_format_control}.txt"
    )
    _repin_manifest(manifest)
    assert list(_validator(MANIFEST_SCHEMA).iter_errors(manifest))
    with pytest.raises(ContractError, match="format"):
        render_submission_packet_manifest(manifest)


def test_missing_explicit_attachment_is_observed_not_located(tmp_path: Path) -> None:
    packet = _packet_copy(tmp_path)
    (packet / "consent-materials.txt").unlink()
    rows = observe_submission_packet(_inventory(), packet)
    row = next(item for item in rows if item["artifact_id"] == "fixture.us-consent")
    assert row == {
        "artifact_id": "fixture.us-consent",
        "relative_path": "consent-materials.txt",
        "state": "not_located",
        "observed_sha256": None,
        "observed_size_bytes": None,
        "status": "CONFLICTING",
        "reason_codes": ["DECLARED_ATTACHMENT_NOT_LOCATED"],
    }


@pytest.mark.parametrize(
    ("mutation", "expected_reasons"),
    [
        ("missing", ["DECLARED_ATTACHMENT_NOT_LOCATED"]),
        ("digest", ["ARTIFACT_DIGEST_MISMATCH"]),
        ("certificate_holder", ["CERTIFICATE_HOLDER_MISMATCH"]),
    ],
)
def test_unbound_declared_conflict_stays_visible_without_changing_readiness(
    tmp_path: Path, mutation: str, expected_reasons: list[str]
) -> None:
    packet = _packet_copy(tmp_path)
    inventory = _inventory()
    artifact = _artifact(inventory, "fixture.training-certificate")
    path = packet / artifact["relative_path"]
    if mutation == "missing":
        path.unlink()
    elif mutation == "digest":
        original = path.read_bytes()
        replacement = bytes([original[0] ^ 1]) + original[1:]
        assert len(replacement) == len(original)
        path.write_bytes(replacement)
    else:
        certificate = artifact["declared_structure"]["certificate"]
        assert certificate is not None
        certificate["holder_role_id"] = "principal_investigator"
    manifest = _build(inventory, packet)
    observation = next(
        row
        for row in manifest["packet_observations"]
        if row["artifact_id"] == artifact["artifact_id"]
    )
    assert observation["status"] == "CONFLICTING"
    assert observation["reason_codes"] == expected_reasons
    assert not any(
        artifact["artifact_id"] in row["matched_artifact_ids"]
        for row in manifest["entries"]
    )
    assert manifest["administrative_status"]["submission_readiness"] == (
        "no_listed_gaps_located"
    )


def test_packet_root_symlink_is_rejected(tmp_path: Path) -> None:
    packet = _packet_copy(tmp_path)
    redirected = tmp_path / "redirected"
    packet.rename(redirected)
    packet.symlink_to(redirected, target_is_directory=True)
    with pytest.raises(ContractError, match="symlink"):
        observe_submission_packet(_inventory(), packet)


def test_packet_root_with_symlinked_ancestor_is_rejected(tmp_path: Path) -> None:
    real_parent = tmp_path / "real-parent"
    real_parent.mkdir()
    _packet_copy(real_parent)
    linked_parent = tmp_path / "linked-parent"
    linked_parent.symlink_to(real_parent, target_is_directory=True)
    with pytest.raises(ContractError, match="symlink"):
        observe_submission_packet(_inventory(), linked_parent / "packet")


@pytest.mark.parametrize("link_parent", [False, True])
def test_packet_member_or_parent_symlink_is_rejected(
    tmp_path: Path, link_parent: bool
) -> None:
    inventory = _inventory()
    packet = _packet_copy(tmp_path)
    if link_parent:
        real = tmp_path / "real-subdir"
        real.mkdir()
        shutil.copy2(packet / "consent-materials.txt", real / "consent-materials.txt")
        (packet / "linked").symlink_to(real, target_is_directory=True)
        _artifact(inventory, "fixture.us-consent")["relative_path"] = (
            "linked/consent-materials.txt"
        )
    else:
        original = packet / "consent-materials.txt"
        real = packet / "consent-real.txt"
        original.rename(real)
        original.symlink_to(real.name)
    with pytest.raises(ContractError, match="symlink"):
        observe_submission_packet(inventory, packet)


def test_broken_symlink_is_rejected_not_folded_into_absence(tmp_path: Path) -> None:
    packet = _packet_copy(tmp_path)
    path = packet / "consent-materials.txt"
    path.unlink()
    path.symlink_to("missing-target.txt")
    with pytest.raises(ContractError, match="symlink"):
        observe_submission_packet(_inventory(), packet)


def test_final_member_swap_to_symlink_cannot_escape_anchored_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inventory = _inventory()
    packet = _packet_copy(tmp_path)
    artifact = _artifact(inventory, "fixture.us-consent")
    target = packet / artifact["relative_path"]
    outside = tmp_path / "outside-secret.txt"
    outside.write_bytes(b"OUTSIDE-SYMLINK-TARGET-667\n")
    original_open = os.open
    swapped = False

    def racing_open(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        nonlocal swapped
        if (
            not swapped
            and dir_fd is not None
            and not flags & os.O_DIRECTORY
            and os.fsdecode(path) == target.name
        ):
            swapped = True
            target.unlink()
            target.symlink_to(outside)
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(os, "open", racing_open)
    with pytest.raises(ContractError, match="symlink"):
        observe_submission_packet(inventory, packet)
    assert swapped is True
    assert target.is_symlink()


def test_member_parent_swap_after_open_stays_on_anchored_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inventory = _inventory()
    packet = _packet_copy(tmp_path)
    artifact = _artifact(inventory, "fixture.us-consent")
    original_path = packet / artifact["relative_path"]
    expected = original_path.read_bytes()
    member_parent = packet / "nested"
    member_parent.mkdir()
    original_path.rename(member_parent / original_path.name)
    artifact["relative_path"] = f"nested/{original_path.name}"

    outside_parent = tmp_path / "outside-parent"
    outside_parent.mkdir()
    (outside_parent / original_path.name).write_bytes(b"OUTSIDE-PARENT-TARGET-667\n")
    moved_parent = packet / "opened-parent"
    original_open_directory = packet_runtime._open_directory_at
    swapped = False

    def swap_after_open(
        parent_fd: int,
        component: str,
        contract_path: str,
        *,
        missing_ok: bool,
    ) -> int | None:
        nonlocal swapped
        opened = original_open_directory(
            parent_fd,
            component,
            contract_path,
            missing_ok=missing_ok,
        )
        if component == "nested" and opened is not None and not swapped:
            swapped = True
            member_parent.rename(moved_parent)
            member_parent.symlink_to(outside_parent, target_is_directory=True)
        return opened

    monkeypatch.setattr(packet_runtime, "_open_directory_at", swap_after_open)
    observations = observe_submission_packet(inventory, packet)
    row = next(
        item for item in observations if item["artifact_id"] == artifact["artifact_id"]
    )
    assert swapped is True
    assert member_parent.is_symlink()
    assert row["observed_sha256"] == hashlib.sha256(expected).hexdigest()
    assert row["observed_sha256"] != hashlib.sha256(
        (outside_parent / original_path.name).read_bytes()
    ).hexdigest()


def test_descriptor_safe_open_has_no_unsafe_platform_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delattr(packet_runtime.os, "O_NOFOLLOW")
    with pytest.raises(ContractError, match="descriptor-relative O_NOFOLLOW"):
        observe_submission_packet(_inventory(), PACKET_ROOT)


@pytest.mark.parametrize("kind", ["directory", "fifo"])
def test_non_regular_explicit_attachment_is_rejected(tmp_path: Path, kind: str) -> None:
    packet = _packet_copy(tmp_path)
    path = packet / "consent-materials.txt"
    path.unlink()
    if kind == "directory":
        path.mkdir()
    else:
        if not hasattr(os, "mkfifo"):
            pytest.skip("FIFO creation is unavailable")
        os.mkfifo(path)
    with pytest.raises(ContractError, match="regular file"):
        observe_submission_packet(_inventory(), packet)


def test_observer_opens_only_inventory_paths_and_ignores_sibling_sentinel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    packet = _packet_copy(tmp_path)
    sentinel = packet / "consent-final-approved-secret.txt"
    sentinel.write_text("UNLISTED-SENTINEL-667", encoding="utf-8")
    inventory = _inventory()
    opened: list[str] = []
    original_open = os.open

    def tracked_open(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if dir_fd is not None and not flags & os.O_DIRECTORY:
            opened.append(os.fsdecode(path))
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(os, "open", tracked_open)
    rows = observe_submission_packet(inventory, packet)
    expected = {row["relative_path"] for row in inventory["artifacts"]}
    assert set(opened) == expected
    assert sentinel.name not in opened
    assert "UNLISTED-SENTINEL-667" not in json.dumps(rows)


def test_observer_limits_are_enforced_without_large_fixture(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inventory = _inventory()
    for artifact in inventory["artifacts"]:
        artifact["declared_size_bytes"] = 0
    monkeypatch.setattr(packet_runtime, "MAX_ARTIFACT_BYTES", 32)
    with pytest.raises(ContractError, match="observation limit"):
        observe_submission_packet(inventory, PACKET_ROOT)


def test_total_observer_limit_is_enforced_without_large_fixture(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inventory = _inventory()
    declared_total = sum(
        artifact["declared_size_bytes"] for artifact in inventory["artifacts"]
    )
    monkeypatch.setattr(packet_runtime, "MAX_TOTAL_BYTES", declared_total - 1)
    with pytest.raises(ContractError, match="total limit"):
        observe_submission_packet(inventory, PACKET_ROOT)


def test_runtime_has_no_directory_scan_network_or_model_client() -> None:
    tree = ast.parse(RUNTIME.read_text(encoding="utf-8"))
    imported: set[str] = set()
    forbidden_calls = {
        "glob",
        "iglob",
        "rglob",
        "iterdir",
        "listdir",
        "scandir",
        "walk",
        "fwalk",
    }
    calls: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            calls.add(node.func.attr)
    assert imported.isdisjoint(
        {
            "socket",
            "urllib",
            "http",
            "requests",
            "httpx",
            "openai",
            "anthropic",
            "subprocess",
        }
    )
    assert calls.isdisjoint(forbidden_calls)


def test_in_process_builder_never_opens_a_socket(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_connect(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("packet manifest attempted network access")

    monkeypatch.setattr(socket.socket, "connect", fail_connect)
    _build()


def test_no_authority_triplet_returns_explicit_unresolved_manifest() -> None:
    manifest = build_submission_packet_manifest(_inventory(), PACKET_ROOT)
    assert manifest["authority_binding"]["state"] == "not_provided"
    assert manifest["entries"] == []
    assert manifest["excluded_requirements"] == []
    assert manifest["administrative_status"]["submission_readiness"] == "unresolved"
    assert "AUTHORITY_INPUT_NOT_PROVIDED" in _reason_codes(manifest)
    assert "V1_ENVELOPE_FACT_MISSING" in _reason_codes(manifest)


@pytest.mark.parametrize("provided", [(True, False, False), (False, True, False), (False, False, True), (True, True, False), (True, False, True), (False, True, True)])
def test_partial_authority_triplet_fails_closed(
    provided: tuple[bool, bool, bool]
) -> None:
    context, registry, resolved = _authority()
    values = (context, registry, resolved)
    args = [value if use else None for value, use in zip(values, provided)]
    with pytest.raises(ContractError, match="all-or-none"):
        build_submission_packet_manifest(
            _inventory(),
            PACKET_ROOT,
            context=args[0],
            registry=args[1],
            resolved=args[2],
        )


def test_schema_shaped_resolved_tamper_is_rejected_with_or_without_resigning() -> None:
    context, registry, resolved = _authority()
    for resign in (False, True):
        tampered = copy.deepcopy(resolved)
        tampered["requirement_results"][0]["consumer_scopes"].append(
            "submission_packet"
        )
        if resign:
            tampered.pop("resolved_digest")
            tampered["resolved_digest"] = digest(tampered)
        with pytest.raises(ContractError):
            _build(_inventory(), PACKET_ROOT, context, registry, tampered)


def test_upstream_week_date_residue_cannot_escape_the_667_date_contract() -> None:
    context = _context()
    registry = _registry()
    registry["as_of"] = "2026-W52-7"
    resolved = resolve(context, registry)
    with pytest.raises(ContractError, match="real ISO 8601 date"):
        _build(_inventory(), PACKET_ROOT, context, registry, resolved)


def test_replayed_closed_authority_gate_stays_unresolved_without_default_profile() -> None:
    context = _context("no-profile.json")
    registry = _registry()
    resolved = resolve(context, registry)
    manifest = _build(_inventory(), PACKET_ROOT, context, registry, resolved)
    assert manifest["authority_binding"]["state"] == "replay_validated"
    assert manifest["authority_binding"]["resolution_state"] == "jurisdiction_unresolved"
    assert manifest["entries"] == []
    assert manifest["administrative_status"]["submission_readiness"] == "unresolved"
    assert "AUTHORITY_RESOLUTION_NOT_PERMITTED" in _reason_codes(manifest)


@pytest.mark.parametrize("fact_id", tuple(ENVELOPE_EXPECTED))
@pytest.mark.parametrize("case", ["missing", "unknown", "outside"])
def test_each_v1_envelope_fact_is_load_bearing(
    fact_id: str, case: str
) -> None:
    context = _context()
    rows = context["declared_facts"]
    row = next(item for item in rows if item["fact_id"] == fact_id)
    if case == "missing":
        rows.remove(row)
        expected_code = "V1_ENVELOPE_FACT_MISSING"
    elif case == "unknown":
        row["state"] = "unknown"
        row["value"] = None
        expected_code = "V1_ENVELOPE_FACT_UNKNOWN"
    else:
        row["value"] = not ENVELOPE_EXPECTED[fact_id]
        expected_code = "V1_ENVELOPE_OUTSIDE"
    registry = _registry()
    resolved = resolve(context, registry)
    manifest = _build(_inventory(), PACKET_ROOT, context, registry, resolved)
    assert manifest["capability_envelope"]["state"] == "unresolved"
    assert manifest["entries"] == []
    assert manifest["administrative_status"]["submission_readiness"] == "unresolved"
    assert any(
        reason["code"] == expected_code and reason["fact_id"] == fact_id
        for reason in manifest["unresolved_reasons"]
    )


def test_all_seven_v1_envelope_facts_pass_together() -> None:
    manifest = _build()
    assert manifest["capability_envelope"]["state"] == "within_v1"
    assert manifest["capability_envelope"]["reason_codes"] == []
    assert {
        row["fact_id"]: (row["required_value"], row["declared_value"])
        for row in manifest["capability_envelope"]["facts"]
    } == {key: (value, value) for key, value in ENVELOPE_EXPECTED.items()}


@pytest.mark.parametrize("overlay_kind", ["institutional", "funder"])
def test_not_provided_overlay_remains_visible_and_readiness_unresolved(
    overlay_kind: str,
) -> None:
    context = _context()
    context["overlay_selection_state"][overlay_kind] = "not_provided"
    registry = _registry()
    resolved = resolve(context, registry)
    manifest = _build(_inventory(), PACKET_ROOT, context, registry, resolved)
    assert manifest["overlay_selection_state"][overlay_kind] == "not_provided"
    assert manifest["administrative_status"]["submission_readiness"] == "unresolved"
    assert any(
        reason["code"] == "OVERLAY_SELECTION_NOT_PROVIDED"
        and reason["overlay_kind"] == overlay_kind
        for reason in manifest["unresolved_reasons"]
    )


def test_us_packet_rows_respect_actor_scope_and_evidence_holder_boundaries() -> None:
    manifest = _build()
    participant = _entry(
        manifest,
        "us.45cfr46.116.informed-consent",
        "consent.participant-materials",
    )
    determination = _entry(
        manifest,
        "us.45cfr46.116.informed-consent",
        "consent.irb-determination",
    )
    assert participant["responsibility"] == "packet_owned"
    assert participant["status"] == "DOCUMENTED"
    assert participant["reason_codes"] == ["STRUCTURE_DOCUMENTED"]
    assert participant["matched_artifact_ids"] == ["fixture.us-consent"]
    assert determination["responsibility"] == "external_dependency"
    assert determination["status"] == "ACCEPTANCE_UNVERIFIED"
    assert determination["readiness_effect"] == "none"
    assert determination["matched_artifact_ids"] == []
    requirement_ids = {
        row["requirement_ref"]["requirement_id"] for row in manifest["entries"]
    }
    assert "us.45cfr46.107.irb-composition" not in requirement_ids
    assert not any(item.startswith("eu.gdpr") for item in requirement_ids)
    assert manifest["administrative_status"]["submission_readiness"] == (
        "no_listed_gaps_located"
    )


def test_exact_obligated_actor_match_is_required_before_packet_ownership() -> None:
    inventory = _inventory()
    inventory["packet_responsibility_role_ids"].remove("investigator_and_irb")
    manifest = _build(inventory)
    participant = _entry(
        manifest,
        "us.45cfr46.116.informed-consent",
        "consent.participant-materials",
    )
    assert participant["responsibility"] == "external_dependency"
    assert participant["status"] == "ACCEPTANCE_UNVERIFIED"
    assert participant["readiness_effect"] == "none"


def test_same_packet_inventory_produces_distinct_exact_us_and_tw_manifests() -> None:
    inventory = _inventory()
    us_context, registry, us_resolved = _authority("us-gdpr-two-axis.json")
    tw_context = _context("tw-gdpr-two-axis.json")
    tw_resolved = resolve(tw_context, registry)
    us = _build(inventory, PACKET_ROOT, us_context, registry, us_resolved)
    tw = _build(inventory, PACKET_ROOT, tw_context, registry, tw_resolved)
    us_row = _entry(
        us,
        "us.45cfr46.116.informed-consent",
        "consent.participant-materials",
    )
    tw_row = _entry(
        tw,
        "tw.hsra.article-14.consent-information",
        "consent.article-14-materials",
    )
    assert us_row["status"] == tw_row["status"] == "DOCUMENTED"
    assert us_row["matched_artifact_ids"] == ["fixture.us-consent"]
    assert tw_row["matched_artifact_ids"] == ["fixture.tw-consent"]
    assert us["manifest_digest"] != tw["manifest_digest"]
    assert not any(
        row["requirement_ref"]["requirement_id"].startswith("tw.")
        for row in us["entries"]
    )
    assert not any(
        row["requirement_ref"]["requirement_id"].startswith("us.")
        for row in tw["entries"]
    )


def test_same_packet_conditional_fact_true_false_unknown_is_not_inferred() -> None:
    context, registry, _resolved, overlay = _synthetic_overlay_authority()
    base = next(
        row
        for row in overlay["requirements"]
        if row["requirement_id"] == "synthetic.packet.base-consent"
    )
    base["applies_if"] = {
        "op": "fact_equals",
        "fact_id": "data.special_category",
        "value": True,
    }
    _repin_overlay(context, overlay)
    special = next(
        row
        for row in context["declared_facts"]
        if row["fact_id"] == "data.special_category"
    )

    special["state"], special["value"] = "declared", False
    false_manifest = _build(
        _inventory(), PACKET_ROOT, context, registry, resolve(context, registry)
    )
    assert any(
        row["requirement_ref"]["requirement_id"]
        == "synthetic.packet.base-consent"
        for row in false_manifest["excluded_requirements"]
    )

    special["value"] = True
    true_manifest = _build(
        _inventory(), PACKET_ROOT, context, registry, resolve(context, registry)
    )
    assert _entry(
        true_manifest,
        "synthetic.packet.base-consent",
        "synthetic.base-consent",
    )["status"] == "NOT_LOCATED"

    special["state"], special["value"] = "unknown", None
    unknown_manifest = _build(
        _inventory(), PACKET_ROOT, context, registry, resolve(context, registry)
    )
    assert unknown_manifest["entries"] == []
    assert unknown_manifest["excluded_requirements"] == []
    assert "AUTHORITY_RESOLUTION_NOT_PERMITTED" in _reason_codes(unknown_manifest)
    assert len(
        {
            false_manifest["manifest_digest"],
            true_manifest["manifest_digest"],
            unknown_manifest["manifest_digest"],
        }
    ) == 3


def test_parallel_collision_entries_survive_display_precedence_changes() -> None:
    context, registry, _resolved, overlay = _synthetic_overlay_authority()
    base = next(
        row
        for row in overlay["requirements"]
        if row["requirement_id"] == "synthetic.packet.base-consent"
    )
    base["interaction"]["collision_key"] = "participant.information"
    _repin_overlay(context, overlay)
    first_resolved = resolve(context, registry)
    collision = next(
        row
        for row in first_resolved["collisions"]
        if row["collision_key"] == "participant.information"
    )
    assert {
        "us.45cfr46.116.informed-consent",
        "synthetic.packet.base-consent",
    } <= set(collision["requirement_ids"])
    first = _build(_inventory(), PACKET_ROOT, context, registry, first_resolved)
    live = _entry(
        first,
        "us.45cfr46.116.informed-consent",
        "consent.participant-materials",
    )
    parallel = _entry(
        first,
        "synthetic.packet.base-consent",
        "synthetic.base-consent",
    )
    assert live["requirement_ref"]["authority_kind"] == "profile"
    assert live["requirement_ref"]["requirement_pointer"].startswith("/profiles/")
    assert parallel["requirement_ref"]["authority_kind"] == "institutional_overlay"
    assert parallel["requirement_ref"]["requirement_pointer"].startswith("/overlays/")
    assert live["requirement_ref"]["authority_digest"] != parallel[
        "requirement_ref"
    ]["authority_digest"]

    review = next(
        row
        for row in context["display_precedence"]
        if row["axis"] == "review_ethics"
    )
    review["ordered_authorities"].reverse()
    second_resolved = resolve(context, registry)
    assert second_resolved["trace_order"] != first_resolved["trace_order"]
    second = _build(_inventory(), PACKET_ROOT, context, registry, second_resolved)
    assert second["entries"] == first["entries"]
    assert second["excluded_requirements"] == first["excluded_requirements"]
    assert second["authority_binding"] != first["authority_binding"]


def _bounded_requirement_result(requirement_id: str, applicability: str) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "authority_kind": "profile",
        "authority_id": "synthetic.profile",
        "authority_version": "1.0",
        "authority_digest": "0" * 64,
        "axis": "review_ethics",
        "obligated_actor": "investigator",
        "consumer_scopes": ["submission_packet"],
        "applicability": applicability,
        "predicate_trace": [],
        "requirement_digest": "0" * 64,
        "requirement_pointer": "/profiles/0/requirements/0",
        "authority_anchor_pointer": "/profiles/0/requirements/0/authority_anchor",
    }


def test_manifest_entry_bound_accepts_4096_and_rejects_4097(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evidence_rows = [
        {
            "evidence_id": f"synthetic.evidence.{index:04d}",
            "held_by": "external_holder",
            "artifact_type": "synthetic_artifact",
            "description": "Digest-only synthetic row.",
        }
        for index in range(packet_runtime.MAX_MANIFEST_ENTRIES)
    ]

    def fake_requirement(
        _result: dict[str, Any], _registry: dict[str, Any]
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        return {"waiver_or_exception_route": None}, evidence_rows

    monkeypatch.setattr(packet_runtime, "_resolved_requirement", fake_requirement)
    inventory = {
        "packet_responsibility_role_ids": ["investigator"],
        "waiver_or_exception_claims": [],
        "artifacts": [],
    }
    resolved = {
        "requirement_results": [
            _bounded_requirement_result("synthetic.requirement", "true")
        ]
    }
    entries, excluded = packet_runtime._evidence_entries(
        inventory, {}, {}, resolved, []
    )
    assert len(entries) == packet_runtime.MAX_MANIFEST_ENTRIES
    assert excluded == []

    evidence_rows.append(
        {
            "evidence_id": "synthetic.evidence.overflow",
            "held_by": "external_holder",
            "artifact_type": "synthetic_artifact",
            "description": "Overflow row.",
        }
    )
    with pytest.raises(ContractError, match="4096 submission-packet evidence entries"):
        packet_runtime._evidence_entries(inventory, {}, {}, resolved, [])


def test_manifest_canonical_byte_bound_is_inclusive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert packet_runtime.MAX_MANIFEST_BYTES == 8 * 1024 * 1024
    inventory = _inventory()
    context, registry, resolved = _authority()
    baseline = _build(inventory, PACKET_ROOT, context, registry, resolved)
    exact_size = len(packet_runtime._canonical_bytes(baseline))

    monkeypatch.setattr(packet_runtime, "MAX_MANIFEST_BYTES", exact_size)
    assert _build(inventory, PACKET_ROOT, context, registry, resolved) == baseline
    validate_submission_packet_manifest(
        baseline,
        inventory,
        PACKET_ROOT,
        context=context,
        registry=registry,
        resolved=resolved,
    )
    assert render_submission_packet_manifest(baseline).startswith(
        "# Human-Subjects Submission-Packet Manifest"
    )

    monkeypatch.setattr(packet_runtime, "MAX_MANIFEST_BYTES", exact_size - 1)
    with pytest.raises(ContractError, match="canonical JSON exceeds"):
        _build(inventory, PACKET_ROOT, context, registry, resolved)
    with pytest.raises(ContractError, match="canonical JSON exceeds"):
        validate_submission_packet_manifest(
            baseline,
            inventory,
            PACKET_ROOT,
            context=context,
            registry=registry,
            resolved=resolved,
        )
    with pytest.raises(ContractError, match="canonical JSON exceeds"):
        render_submission_packet_manifest(baseline)


def test_consumer_scope_bound_accepts_512_and_rejects_513(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evidence_rows = [
        {
            "evidence_id": "synthetic.evidence",
            "held_by": "external_holder",
            "artifact_type": "synthetic_artifact",
            "description": "Bounded scope row.",
        }
    ]
    monkeypatch.setattr(
        packet_runtime,
        "_resolved_requirement",
        lambda _result, _registry: ({"waiver_or_exception_route": None}, evidence_rows),
    )
    inventory = {
        "packet_responsibility_role_ids": ["investigator"],
        "waiver_or_exception_claims": [],
        "artifacts": [],
    }
    result = _bounded_requirement_result("synthetic.requirement", "true")
    result["consumer_scopes"] = sorted(
        ["submission_packet"]
        + [
            f"synthetic.scope.{index:04d}"
            for index in range(packet_runtime.MAX_CONSUMER_SCOPES - 1)
        ]
    )
    entries, _excluded = packet_runtime._evidence_entries(
        inventory, {}, {}, {"requirement_results": [result]}, []
    )
    assert len(entries[0]["requirement_ref"]["consumer_scopes"]) == (
        packet_runtime.MAX_CONSUMER_SCOPES
    )

    result["consumer_scopes"].append("synthetic.scope.overflow")
    with pytest.raises(ContractError, match="consumer scopes exceed 512"):
        packet_runtime._evidence_entries(
            inventory, {}, {}, {"requirement_results": [result]}, []
        )


def test_evidence_expansion_indexes_inventory_bindings_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class CountingBindings(list[dict[str, str]]):
        iterations = 0

        def __iter__(self):  # type: ignore[no-untyped-def]
            type(self).iterations += 1
            return super().__iter__()

    bindings = CountingBindings(
        [
            {
                "requirement_id": "synthetic.requirement",
                "evidence_id": "synthetic.evidence.0000",
            }
        ]
    )
    artifact = {
        "artifact_id": "synthetic.artifact",
        "evidence_bindings": bindings,
    }
    inventory = {
        "packet_responsibility_role_ids": ["investigator"],
        "waiver_or_exception_claims": [],
        "artifacts": [artifact],
    }
    evidence_rows = [
        {
            "evidence_id": f"synthetic.evidence.{index:04d}",
            "held_by": "external_holder",
            "artifact_type": "synthetic_artifact",
            "description": "Indexed synthetic row.",
        }
        for index in range(128)
    ]
    monkeypatch.setattr(
        packet_runtime,
        "_resolved_requirement",
        lambda _result, _registry: ({"waiver_or_exception_route": None}, evidence_rows),
    )
    result = _bounded_requirement_result("synthetic.requirement", "true")
    entries, _excluded = packet_runtime._evidence_entries(
        inventory, {}, {}, {"requirement_results": [result]}, []
    )
    assert len(entries) == len(evidence_rows)
    assert CountingBindings.iterations == 1


def test_profiled_route_result_is_cached_per_requirement(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inventory = {
        "packet_responsibility_role_ids": ["investigator"],
        "waiver_or_exception_claims": [],
        "artifacts": [],
    }
    evidence_rows = [
        {
            "evidence_id": f"synthetic.evidence.{index:04d}",
            "held_by": "investigator",
            "artifact_type": "synthetic_artifact",
            "description": "Missing synthetic row.",
        }
        for index in range(128)
    ]
    monkeypatch.setattr(
        packet_runtime,
        "_resolved_requirement",
        lambda _result, _registry: (
            {
                "waiver_or_exception_route": {
                    "state": "profiled",
                    "requirement_ids": ["synthetic.route"],
                }
            },
            evidence_rows,
        ),
    )
    calls = 0

    def counted_route(*_args: Any, **_kwargs: Any) -> bool:
        nonlocal calls
        calls += 1
        return False

    monkeypatch.setattr(
        packet_runtime, "_located_profiled_route_claim", counted_route
    )
    result = _bounded_requirement_result("synthetic.requirement", "true")
    entries, _excluded = packet_runtime._evidence_entries(
        inventory, {}, {}, {"requirement_results": [result]}, []
    )
    assert len(entries) == len(evidence_rows)
    assert calls == 1


def test_excluded_requirement_bound_accepts_4096_and_rejects_4097() -> None:
    inventory = {
        "packet_responsibility_role_ids": ["investigator"],
        "waiver_or_exception_claims": [],
        "artifacts": [],
    }
    results = [
        _bounded_requirement_result(f"synthetic.requirement.{index:04d}", "false")
        for index in range(packet_runtime.MAX_EXCLUDED_REQUIREMENTS)
    ]
    _entries, excluded = packet_runtime._evidence_entries(
        inventory, {}, {}, {"requirement_results": results}, []
    )
    assert len(excluded) == packet_runtime.MAX_EXCLUDED_REQUIREMENTS

    results.append(
        _bounded_requirement_result("synthetic.requirement.overflow", "false")
    )
    with pytest.raises(
        ContractError, match="4096 excluded submission-packet requirements"
    ):
        packet_runtime._evidence_entries(
            inventory, {}, {}, {"requirement_results": results}, []
        )


def test_absent_binding_is_not_located_but_external_evidence_is_not_a_false_gap() -> None:
    inventory = _inventory()
    _artifact(inventory, "fixture.us-consent")["evidence_bindings"] = []
    manifest = _build(inventory)
    participant = _entry(
        manifest,
        "us.45cfr46.116.informed-consent",
        "consent.participant-materials",
    )
    determination = _entry(
        manifest,
        "us.45cfr46.116.informed-consent",
        "consent.irb-determination",
    )
    assert participant["status"] == "NOT_LOCATED"
    assert participant["readiness_effect"] == "gap"
    assert participant["reason_codes"] == ["EXPECTED_PACKET_ARTIFACT_NOT_LOCATED"]
    assert determination["status"] == "ACCEPTANCE_UNVERIFIED"
    assert determination["readiness_effect"] == "none"
    assert manifest["administrative_status"]["submission_readiness"] == "gaps_located"


def test_two_artifacts_claiming_one_evidence_binding_conflict(tmp_path: Path) -> None:
    packet = _packet_copy(tmp_path)
    inventory = _inventory()
    duplicate = copy.deepcopy(_artifact(inventory, "fixture.us-consent"))
    duplicate["artifact_id"] = "fixture.us-consent-copy"
    duplicate["relative_path"] = "us-consent-copy.txt"
    shutil.copy2(packet / "consent-materials.txt", packet / duplicate["relative_path"])
    inventory["artifacts"].append(duplicate)
    manifest = _build(inventory, packet)
    row = _entry(
        manifest,
        "us.45cfr46.116.informed-consent",
        "consent.participant-materials",
    )
    assert row["status"] == "CONFLICTING"
    assert row["readiness_effect"] == "gap"
    assert "DUPLICATE_EVIDENCE_BINDING" in row["reason_codes"]
    assert row["matched_artifact_ids"] == [
        "fixture.us-consent",
        "fixture.us-consent-copy",
    ]


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        ("missing_file", "DECLARED_ATTACHMENT_NOT_LOCATED"),
        ("digest", "ARTIFACT_DIGEST_MISMATCH"),
        ("size", "ARTIFACT_SIZE_MISMATCH"),
        ("type", "ARTIFACT_TYPE_MISMATCH"),
        ("holder", "ARTIFACT_HOLDER_MISMATCH"),
    ],
)
def test_declared_attachment_internal_conflicts_are_deterministic(
    tmp_path: Path, mutation: str, reason: str
) -> None:
    packet = _packet_copy(tmp_path)
    inventory = _inventory()
    artifact = _artifact(inventory, "fixture.us-consent")
    if mutation == "missing_file":
        (packet / artifact["relative_path"]).unlink()
    elif mutation == "digest":
        artifact["declared_sha256"] = "0" * 64
    elif mutation == "size":
        artifact["declared_size_bytes"] += 1
    elif mutation == "type":
        artifact["artifact_type"] = "protocol"
    elif mutation == "holder":
        artifact["declared_holder_role_id"] = "principal_investigator"
    manifest = _build(inventory, packet)
    row = _entry(
        manifest,
        "us.45cfr46.116.informed-consent",
        "consent.participant-materials",
    )
    assert row["status"] == "CONFLICTING"
    assert row["readiness_effect"] == "gap"
    assert reason in row["reason_codes"]
    assert manifest["administrative_status"]["submission_readiness"] == "gaps_located"


@pytest.mark.parametrize("signature_state", ["not_located", "unknown"])
def test_declared_signature_state_does_not_invent_a_requirement(
    signature_state: str,
) -> None:
    inventory = _inventory()
    artifact = _artifact(inventory, "fixture.us-consent")
    artifact["declared_structure"]["signature_blocks"][0]["state"] = signature_state
    artifact["declared_structure"]["certificate"] = None
    row = _entry(
        _build(inventory),
        "us.45cfr46.116.informed-consent",
        "consent.participant-materials",
    )
    assert row["status"] == "DOCUMENTED"
    assert row["reason_codes"] == ["STRUCTURE_DOCUMENTED"]


@pytest.mark.parametrize(
    ("issued_on", "expires_on"),
    [("2000-01-01", "2001-01-01"), ("2099-01-01", "2100-01-01")],
)
def test_certificate_dates_do_not_invent_freshness_requirements(
    issued_on: str, expires_on: str
) -> None:
    context, registry, resolved, _overlay = _synthetic_overlay_authority()
    inventory = _waiver_inventory()
    certificate = _artifact(inventory, "fixture.training-certificate")[
        "declared_structure"
    ]["certificate"]
    assert certificate is not None
    certificate["issued_on"] = issued_on
    certificate["expires_on"] = expires_on
    row = _entry(
        _build(inventory, PACKET_ROOT, context, registry, resolved),
        "synthetic.packet.waiver-route",
        "synthetic.waiver-decision",
    )
    assert row["status"] == "DOCUMENTED"
    assert row["reason_codes"] == ["STRUCTURE_DOCUMENTED"]


def test_schema_valid_reversed_certificate_interval_is_a_manifest_conflict() -> None:
    context, registry, resolved, _overlay = _synthetic_overlay_authority()
    inventory = _waiver_inventory()
    certificate = _artifact(inventory, "fixture.training-certificate")[
        "declared_structure"
    ]["certificate"]
    assert certificate is not None
    certificate["issued_on"] = "2026-01-02"
    certificate["expires_on"] = "2026-01-01"
    _validator(INVENTORY_SCHEMA).validate(inventory)
    validate_submission_packet_inventory(inventory)

    row = _entry(
        _build(inventory, PACKET_ROOT, context, registry, resolved),
        "synthetic.packet.waiver-route",
        "synthetic.waiver-decision",
    )
    assert row["status"] == "CONFLICTING"
    assert row["readiness_effect"] == "gap"
    assert row["reason_codes"] == ["DECLARED_STRUCTURE_CONFLICT"]


def test_certificate_internal_holder_conflict_uses_only_synthetic_overlay() -> None:
    context, registry, resolved, _overlay = _synthetic_overlay_authority()
    inventory = _waiver_inventory()
    certificate = _artifact(inventory, "fixture.training-certificate")[
        "declared_structure"
    ]["certificate"]
    assert certificate is not None
    certificate["holder_role_id"] = "principal_investigator"
    manifest = _build(inventory, PACKET_ROOT, context, registry, resolved)
    row = _entry(
        manifest,
        "synthetic.packet.waiver-route",
        "synthetic.waiver-decision",
    )
    assert row["status"] == "CONFLICTING"
    assert "CERTIFICATE_HOLDER_MISMATCH" in row["reason_codes"]


def test_status_vocabulary_is_covered_without_inventing_a_verdict() -> None:
    documented = _build()
    missing_inventory = _inventory()
    _artifact(missing_inventory, "fixture.us-consent")["evidence_bindings"] = []
    not_located = _build(missing_inventory)
    conflict_inventory = _inventory()
    _artifact(conflict_inventory, "fixture.us-consent")["declared_sha256"] = "0" * 64
    conflicting = _build(conflict_inventory)
    unresolved_context = _context()
    unresolved_context["declared_facts"] = [
        row
        for row in unresolved_context["declared_facts"]
        if row["fact_id"] != "packet_v1.non_clinical"
    ]
    registry = _registry()
    applicability = _build(
        _inventory(),
        PACKET_ROOT,
        unresolved_context,
        registry,
        resolve(unresolved_context, registry),
    )
    observed_statuses = {
        row["status"]
        for manifest in (documented, not_located, conflicting, applicability)
        for key in ("entries", "unresolved_reasons")
        for row in manifest[key]
    }
    assert observed_statuses == {
        "DOCUMENTED",
        "NOT_LOCATED",
        "CONFLICTING",
        "APPLICABILITY_UNRESOLVED",
        "ACCEPTANCE_UNVERIFIED",
    }


def test_exact_profiled_waiver_route_avoids_false_gap_but_never_claims_grant() -> None:
    context, registry, resolved, _overlay = _synthetic_overlay_authority()
    inventory = _waiver_inventory()
    manifest = _build(inventory, PACKET_ROOT, context, registry, resolved)
    route = _entry(
        manifest,
        "synthetic.packet.waiver-route",
        "synthetic.waiver-decision",
    )
    base = _entry(
        manifest,
        "synthetic.packet.base-consent",
        "synthetic.base-consent",
    )
    assert route["status"] == "DOCUMENTED"
    assert route["matched_artifact_ids"] == ["fixture.training-certificate"]
    assert base["responsibility"] == "packet_owned"
    assert base["status"] == "ACCEPTANCE_UNVERIFIED"
    assert base["readiness_effect"] == "unresolved"
    assert base["reason_codes"] == ["WAIVER_OR_EXCEPTION_CLAIM_UNVERIFIED"]
    assert "NOT_LOCATED" not in base["status"]
    assert manifest["administrative_status"]["submission_readiness"] == "unresolved"
    encoded = json.dumps(manifest, sort_keys=True).casefold()
    assert "waiver_granted" not in encoded
    assert '"approved"' not in encoded


def test_profiled_route_without_author_claim_does_not_suppress_base_gap() -> None:
    context, registry, resolved, _overlay = _synthetic_overlay_authority()
    manifest = _build(_inventory(), PACKET_ROOT, context, registry, resolved)
    base = _entry(
        manifest,
        "synthetic.packet.base-consent",
        "synthetic.base-consent",
    )
    assert base["status"] == "NOT_LOCATED"
    assert base["reason_codes"] == ["EXPECTED_PACKET_ARTIFACT_NOT_LOCATED"]
    assert manifest["administrative_status"]["submission_readiness"] == "gaps_located"


@pytest.mark.parametrize(
    "mutation",
    ["wrong_route", "wrong_decision_artifact", "unbound_decision", "holder_conflict"],
)
def test_inexact_or_conflicting_profiled_route_cannot_suppress_missing_base(
    mutation: str,
) -> None:
    context, registry, resolved, _overlay = _synthetic_overlay_authority()
    inventory = _waiver_inventory()
    claim = inventory["waiver_or_exception_claims"][0]
    certificate = _artifact(inventory, "fixture.training-certificate")
    if mutation == "wrong_route":
        claim["route_requirement_ids"] = ["us.45cfr46.116.informed-consent"]
    elif mutation == "wrong_decision_artifact":
        claim["decision_artifact_id"] = "fixture.us-consent"
    elif mutation == "unbound_decision":
        certificate["evidence_bindings"] = []
    else:
        certificate["declared_holder_role_id"] = "principal_investigator"
    manifest = _build(inventory, PACKET_ROOT, context, registry, resolved)
    base = _entry(
        manifest,
        "synthetic.packet.base-consent",
        "synthetic.base-consent",
    )
    assert base["status"] == "NOT_LOCATED"
    assert base["readiness_effect"] == "gap"


def test_unprofiled_or_external_route_state_cannot_suppress_missing_base() -> None:
    for state in (
        "external_authority_required",
        "not_profiled_in_bounded_profile",
        "not_applicable",
    ):
        context, registry, _resolved, overlay = _synthetic_overlay_authority()
        base = next(
            row
            for row in overlay["requirements"]
            if row["requirement_id"] == "synthetic.packet.base-consent"
        )
        base["waiver_or_exception_route"] = {
            "state": state,
            "requirement_ids": [],
            "decision_maker_role": (
                "institutional_review_office"
                if state == "external_authority_required"
                else None
            ),
        }
        _repin_overlay(context, overlay)
        resolved = resolve(context, registry)
        manifest = _build(
            _waiver_inventory(), PACKET_ROOT, context, registry, resolved
        )
        row = _entry(
            manifest,
            "synthetic.packet.base-consent",
            "synthetic.base-consent",
        )
        assert row["status"] == "NOT_LOCATED", state


@pytest.mark.parametrize("mutation", ["scope", "actor"])
def test_route_scope_or_actor_mismatch_cannot_suppress_missing_base(
    mutation: str,
) -> None:
    context, registry, _resolved, overlay = _synthetic_overlay_authority()
    route = next(
        row
        for row in overlay["requirements"]
        if row["requirement_id"] == "synthetic.packet.waiver-route"
    )
    if mutation == "scope":
        route["consumer_scopes"] = ["participant_information"]
    else:
        route["obligated_actor"] = "institutional_review_office"
    _repin_overlay(context, overlay)
    resolved = resolve(context, registry)
    manifest = _build(
        _waiver_inventory(), PACKET_ROOT, context, registry, resolved
    )
    base = _entry(
        manifest,
        "synthetic.packet.base-consent",
        "synthetic.base-consent",
    )
    assert base["status"] == "NOT_LOCATED"


def test_profiled_route_does_not_recursively_self_satisfy() -> None:
    context, registry, _resolved, overlay = _synthetic_overlay_authority()
    route = next(
        row
        for row in overlay["requirements"]
        if row["requirement_id"] == "synthetic.packet.waiver-route"
    )
    route["waiver_or_exception_route"] = {
        "state": "profiled",
        "requirement_ids": ["synthetic.packet.waiver-route"],
        "decision_maker_role": "institutional_review_office",
    }
    _repin_overlay(context, overlay)
    resolved = resolve(context, registry)
    inventory = _waiver_inventory()
    _artifact(inventory, "fixture.training-certificate")["evidence_bindings"] = []
    manifest = _build(inventory, PACKET_ROOT, context, registry, resolved)
    route_entry = _entry(
        manifest,
        "synthetic.packet.waiver-route",
        "synthetic.waiver-decision",
    )
    base_entry = _entry(
        manifest,
        "synthetic.packet.base-consent",
        "synthetic.base-consent",
    )
    assert route_entry["status"] == "NOT_LOCATED"
    assert base_entry["status"] == "NOT_LOCATED"


@pytest.mark.parametrize(
    ("value", "source_reference"),
    [
        ("documented", "caller.authorization-record"),
        ("not_provided", None),
        ("cannot_verify", None),
    ],
)
def test_authorization_status_is_exact_copy_through_only(
    value: str, source_reference: str | None
) -> None:
    inventory = _inventory()
    inventory["authorization_status_input"] = {
        "value": value,
        "source_reference": source_reference,
        "provenance": "caller_supplied_no_derivation",
    }
    manifest = _build(inventory)
    assert manifest["administrative_status"]["authorization_status"] == inventory[
        "authorization_status_input"
    ]


def test_documented_packet_structure_never_promotes_authorization() -> None:
    inventory = _inventory()
    inventory["authorization_status_input"] = {
        "value": "not_provided",
        "source_reference": None,
        "provenance": "caller_supplied_no_derivation",
    }
    manifest = _build(inventory)
    assert any(row["status"] == "DOCUMENTED" for row in manifest["entries"])
    assert manifest["administrative_status"]["submission_readiness"] == (
        "no_listed_gaps_located"
    )
    assert manifest["administrative_status"]["authorization_status"]["value"] == (
        "not_provided"
    )


def test_readiness_changes_do_not_change_authorization_input() -> None:
    inventory = _inventory()
    complete = _build(inventory)
    missing = copy.deepcopy(inventory)
    _artifact(missing, "fixture.us-consent")["evidence_bindings"] = []
    gaps = _build(missing)
    unresolved_context = _context()
    unresolved_context["overlay_selection_state"]["institutional"] = "not_provided"
    registry = _registry()
    unresolved = _build(
        inventory,
        PACKET_ROOT,
        unresolved_context,
        registry,
        resolve(unresolved_context, registry),
    )
    assert {
        complete["administrative_status"]["submission_readiness"],
        gaps["administrative_status"]["submission_readiness"],
        unresolved["administrative_status"]["submission_readiness"],
    } == {"no_listed_gaps_located", "gaps_located", "unresolved"}
    assert complete["administrative_status"]["authorization_status"] == gaps[
        "administrative_status"
    ]["authorization_status"] == unresolved["administrative_status"][
        "authorization_status"
    ]


def test_fixed_administrative_and_acceptance_boundaries_are_exact() -> None:
    manifest = _build()
    assert manifest["administrative_status"]["review_pathway"] == (
        "institutional determination required"
    )
    assert manifest["administrative_status"]["review_timeline"] == (
        "unknown — obtain current institutional estimate"
    )
    assert manifest["acceptance_boundary"] == {
        "status": "ACCEPTANCE_UNVERIFIED",
        "reason_code": "INSTITUTIONAL_DETERMINATION_REQUIRED",
        "affects_submission_readiness": False,
    }
    assert manifest["boundary_footer"] == BOUNDARY_FOOTER


def test_recursive_output_has_no_verdict_adequacy_prose_or_excerpt() -> None:
    manifest = _build()
    forbidden_keys = {
        "verdict",
        "review_level",
        "approval",
        "approval_status",
        "clearance",
        "compliance",
        "conformance",
        "adequacy",
        "content_coverage",
        "quality_score",
        "language_quality",
        "authorization_decision",
        "excerpt",
        "quote",
        "description",
        "summary",
        "structured_expectations",
    }
    assert _all_keys(manifest).isdisjoint(forbidden_keys)
    encoded = json.dumps(manifest, ensure_ascii=False, sort_keys=True)
    for path in PACKET_ROOT.iterdir():
        if path.is_file():
            assert path.read_text(encoding="utf-8").strip() not in encoded
    assert "Test-only structural attachment row" not in encoded
    assert "Participant-facing consent materials" not in encoded


def test_681_handoff_is_json_round_trip_pointer_only_without_parallel_verdict() -> None:
    manifest = _build()
    transported = json.loads(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
    assert transported == manifest
    _validator(MANIFEST_SCHEMA).validate(transported)
    assert all(
        row["requirement_ref"]["requirement_pointer"].startswith(
            ("/profiles/", "/overlays/")
        )
        and row["evidence_ref"]["evidence_pointer"].startswith(
            ("/profiles/", "/overlays/")
        )
        for row in transported["entries"]
    )
    assert "verdict" not in _all_keys(transported)


def test_live_structured_expectations_and_descriptions_do_not_affect_status() -> None:
    context, registry, _resolved = _authority()
    baseline = _build(
        _inventory(), PACKET_ROOT, context, registry, resolve(context, registry)
    )
    profile = next(
        row
        for row in registry["profiles"]
        if row["profile_id"] == "us.hhs.45-cfr-46.subpart-a"
    )
    requirement = next(
        row
        for row in profile["requirements"]
        if row["requirement_id"] == "us.45cfr46.116.informed-consent"
    )
    requirement["structured_expectations"] = [
        {
            "field_id": "synthetic.impossible-prose-test",
            "operator": "equals",
            "value": False,
        }
    ]
    for evidence in requirement["evidence_expected"]:
        evidence["description"] = "This prose must never influence #667."
    _repin_profile(context, profile)
    changed = _build(
        _inventory(), PACKET_ROOT, context, registry, resolve(context, registry)
    )
    for evidence_id in ("consent.participant-materials", "consent.irb-determination"):
        before = _entry(baseline, requirement["requirement_id"], evidence_id)
        after = _entry(changed, requirement["requirement_id"], evidence_id)
        assert (
            after["status"],
            after["responsibility"],
            after["reason_codes"],
            after["matched_artifact_ids"],
        ) == (
            before["status"],
            before["responsibility"],
            before["reason_codes"],
            before["matched_artifact_ids"],
        )


def test_packet_prose_polarity_is_not_interpreted_when_mechanical_binding_matches(
    tmp_path: Path,
) -> None:
    packet = _packet_copy(tmp_path)
    inventory = _inventory()
    before = _build(inventory, packet)
    artifact = _artifact(inventory, "fixture.us-consent")
    path = packet / artifact["relative_path"]
    path.write_text(
        "I refuse every substantive proposition; this is adversarial prose.\n",
        encoding="utf-8",
    )
    raw = path.read_bytes()
    artifact["declared_sha256"] = hashlib.sha256(raw).hexdigest()
    artifact["declared_size_bytes"] = len(raw)
    after = _build(inventory, packet)
    before_row = _entry(
        before,
        "us.45cfr46.116.informed-consent",
        "consent.participant-materials",
    )
    after_row = _entry(
        after,
        "us.45cfr46.116.informed-consent",
        "consent.participant-materials",
    )
    assert before_row["status"] == after_row["status"] == "DOCUMENTED"
    assert before_row["reason_codes"] == after_row["reason_codes"]
    assert before["manifest_digest"] != after["manifest_digest"]


def test_manifest_self_digest_is_exact() -> None:
    manifest = _build()
    unsigned = copy.deepcopy(manifest)
    claimed = unsigned.pop("manifest_digest")
    assert claimed == digest(unsigned)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda value: value["entries"][0]["requirement_ref"].__setitem__(
            "requirement_pointer", "/profiles/999/requirements/0"
        ),
        lambda value: value["entries"][0]["evidence_ref"].__setitem__(
            "evidence_digest", "0" * 64
        ),
        lambda value: value["packet_observations"][0].__setitem__(
            "observed_sha256", "0" * 64
        ),
        lambda value: value["administrative_status"].__setitem__(
            "submission_readiness", "gaps_located"
        ),
        lambda value: value["administrative_status"]["authorization_status"].update(
            {
                "value": "documented",
                "source_reference": "forged.authorization",
            }
        ),
        lambda value: value["entries"][0].update(
            {
                "status": "ACCEPTANCE_UNVERIFIED",
                "readiness_effect": "unresolved",
                "reason_codes": ["WAIVER_OR_EXCEPTION_CLAIM_UNVERIFIED"],
            }
        ),
    ],
)
def test_resigned_manifest_mutations_fail_exact_replay(
    mutate: Callable[[dict[str, Any]], None]
) -> None:
    inventory = _inventory()
    context, registry, resolved = _authority()
    manifest = _build(inventory, PACKET_ROOT, context, registry, resolved)
    mutate(manifest)
    _repin_manifest(manifest)
    with pytest.raises(ContractError):
        validate_submission_packet_manifest(
            manifest,
            inventory,
            PACKET_ROOT,
            context=context,
            registry=registry,
            resolved=resolved,
        )


def test_resigned_context_free_overlay_state_fails_shape_and_direct_render() -> None:
    manifest = build_submission_packet_manifest(_inventory(), PACKET_ROOT)
    manifest["overlay_selection_state"] = {
        "institutional": "selected",
        "funder": "none_declared_by_author",
    }
    _repin_manifest(manifest)
    assert list(_validator(MANIFEST_SCHEMA).iter_errors(manifest))
    with pytest.raises(ContractError, match="overlay_selection_state"):
        render_submission_packet_manifest(manifest)


def test_resigned_replay_validated_manifest_requires_overlay_state() -> None:
    manifest = _build()
    manifest["overlay_selection_state"] = None
    _repin_manifest(manifest)
    assert list(_validator(MANIFEST_SCHEMA).iter_errors(manifest))
    with pytest.raises(ContractError, match="overlay_selection_state"):
        render_submission_packet_manifest(manifest)


def test_resigned_resolved_authority_with_partly_closed_gate_fails_shape() -> None:
    manifest = _build()
    manifest["authority_binding"]["downstream_gate"][
        "all_applicability_resolved"
    ] = False
    _repin_manifest(manifest)
    assert list(_validator(MANIFEST_SCHEMA).iter_errors(manifest))
    with pytest.raises(ContractError, match="fully open"):
        render_submission_packet_manifest(manifest)


def test_resigned_unresolved_authority_with_open_profile_gate_fails_shape() -> None:
    context = _context("no-profile.json")
    registry = _registry()
    resolved = resolve(context, registry)
    manifest = _build(_inventory(), PACKET_ROOT, context, registry, resolved)
    manifest["authority_binding"]["downstream_gate"][
        "profile_dependent_result_allowed"
    ] = True
    _repin_manifest(manifest)
    assert list(_validator(MANIFEST_SCHEMA).iter_errors(manifest))
    with pytest.raises(ContractError, match="must be false"):
        render_submission_packet_manifest(manifest)


def test_resigned_closed_gate_with_entries_fails_shape_and_direct_render() -> None:
    unresolved = build_submission_packet_manifest(_inventory(), PACKET_ROOT)
    unresolved["entries"] = [copy.deepcopy(_build()["entries"][0])]
    _repin_manifest(unresolved)
    assert list(_validator(MANIFEST_SCHEMA).iter_errors(unresolved))
    with pytest.raises(ContractError, match="closed authority or capability gate"):
        render_submission_packet_manifest(unresolved)


def test_resigned_closed_gate_with_packet_observation_fails_shape() -> None:
    unresolved = build_submission_packet_manifest(_inventory(), PACKET_ROOT)
    unresolved["packet_observations"] = [
        copy.deepcopy(_build()["packet_observations"][0])
    ]
    unresolved["packet_pointer"]["observation_digest"] = digest(
        unresolved["packet_observations"]
    )
    _repin_manifest(unresolved)
    assert list(_validator(MANIFEST_SCHEMA).iter_errors(unresolved))
    with pytest.raises(ContractError, match="closed authority or capability gate"):
        render_submission_packet_manifest(unresolved)


def test_resigned_located_observation_cannot_claim_attachment_absence() -> None:
    manifest = _build()
    observation = manifest["packet_observations"][0]
    assert observation["state"] == "located"
    observation["status"] = "CONFLICTING"
    observation["reason_codes"] = ["DECLARED_ATTACHMENT_NOT_LOCATED"]
    manifest["packet_pointer"]["observation_digest"] = digest(
        manifest["packet_observations"]
    )
    _repin_manifest(manifest)
    assert list(_validator(MANIFEST_SCHEMA).iter_errors(manifest))
    with pytest.raises(ContractError, match="located conflict"):
        render_submission_packet_manifest(manifest)


def test_resigned_overlay_not_provided_without_reason_fails_shape() -> None:
    manifest = _build()
    manifest["overlay_selection_state"]["institutional"] = "not_provided"
    manifest["administrative_status"]["submission_readiness"] = "unresolved"
    _repin_manifest(manifest)
    assert list(_validator(MANIFEST_SCHEMA).iter_errors(manifest))
    with pytest.raises(ContractError, match="unresolved_reasons"):
        render_submission_packet_manifest(manifest)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda value: value["inventory_pointer"].__setitem__(
            "inventory_id", value["inventory_pointer"]["inventory_id"] + "\n"
        ),
        lambda value: value["authority_binding"]["registry_pointer"].__setitem__(
            "registry_version",
            value["authority_binding"]["registry_pointer"]["registry_version"]
            + "\n",
        ),
        lambda value: value["entries"][0]["evidence_ref"].__setitem__(
            "evidence_digest",
            value["entries"][0]["evidence_ref"]["evidence_digest"] + "\n",
        ),
        lambda value: value["packet_observations"][0].__setitem__(
            "relative_path",
            value["packet_observations"][0]["relative_path"] + "\n",
        ),
        lambda value: value["entries"][0]["requirement_ref"].__setitem__(
            "requirement_pointer",
            value["entries"][0]["requirement_ref"]["requirement_pointer"] + "\n",
        ),
        lambda value: value["entries"][0]["requirement_ref"].__setitem__(
            "authority_anchor_pointer",
            value["entries"][0]["requirement_ref"]["authority_anchor_pointer"]
            + "\n",
        ),
        lambda value: value["entries"][0]["evidence_ref"].__setitem__(
            "evidence_pointer",
            value["entries"][0]["evidence_ref"]["evidence_pointer"] + "\n",
        ),
        lambda value: value["authority_binding"]["registry_pointer"].__setitem__(
            "as_of", "2026-W01-1"
        ),
    ],
)
def test_manifest_schema_runtime_absolute_end_parity(
    mutate: Callable[[dict[str, Any]], None]
) -> None:
    inventory = _inventory()
    context, registry, resolved = _authority()
    manifest = _build(inventory, PACKET_ROOT, context, registry, resolved)
    mutate(manifest)
    _repin_manifest(manifest)
    assert list(_validator(MANIFEST_SCHEMA).iter_errors(manifest))
    with pytest.raises(ContractError):
        validate_submission_packet_manifest(
            manifest,
            inventory,
            PACKET_ROOT,
            context=context,
            registry=registry,
            resolved=resolved,
        )


def test_inventory_key_and_unordered_list_order_do_not_change_manifest() -> None:
    inventory = _inventory()
    us_artifact = _artifact(inventory, "fixture.us-consent")
    us_artifact["evidence_bindings"].append(
        {"requirement_id": "unused.requirement", "evidence_id": "unused.evidence"}
    )
    us_artifact["declared_structure"]["signature_blocks"].append(
        {"role_id": "sponsor", "state": "present"}
    )
    inventory["waiver_or_exception_claims"] = [
        {
            "requirement_id": "unused.base-a",
            "route_requirement_ids": ["unused.route-b", "unused.route-a"],
            "decision_artifact_id": None,
            "declared_by": "author",
        },
        {
            "requirement_id": "unused.base-b",
            "route_requirement_ids": [],
            "decision_artifact_id": None,
            "declared_by": "author",
        },
    ]
    baseline = _build(inventory)
    reordered = json.loads(json.dumps(inventory, ensure_ascii=False, sort_keys=True))
    reordered["artifacts"].reverse()
    reordered["packet_responsibility_role_ids"].reverse()
    reordered["waiver_or_exception_claims"].reverse()
    for claim in reordered["waiver_or_exception_claims"]:
        claim["route_requirement_ids"].reverse()
    for artifact in reordered["artifacts"]:
        artifact["evidence_bindings"].reverse()
        artifact["declared_structure"]["signature_blocks"].reverse()
    after = _build(reordered)
    assert after == baseline


def test_context_fact_order_and_reconfirmation_do_not_change_manifest() -> None:
    inventory = _inventory()
    context, registry, resolved = _authority()
    baseline = _build(inventory, PACKET_ROOT, context, registry, resolved)
    reordered = json.loads(json.dumps(context, ensure_ascii=False, sort_keys=True))
    reordered["declared_facts"].reverse()
    reordered["confirmed_at"] = "2026-08-09T15:00:00+08:00"
    replayed = resolve(reordered, registry)
    after = _build(inventory, PACKET_ROOT, reordered, registry, replayed)
    assert after == baseline


def test_output_order_is_canonical() -> None:
    manifest = _build()
    observations = [row["artifact_id"] for row in manifest["packet_observations"]]
    assert observations == sorted(observations)
    entry_keys = [
        (
            row["requirement_ref"]["axis"],
            row["requirement_ref"]["authority_kind"],
            row["requirement_ref"]["authority_id"],
            row["requirement_ref"]["requirement_id"],
            row["evidence_ref"]["evidence_pointer"],
        )
        for row in manifest["entries"]
    ]
    assert entry_keys == sorted(entry_keys)
    assert all(row["reason_codes"] == sorted(row["reason_codes"]) for row in manifest["entries"])


def test_identical_packet_re_root_does_not_change_manifest(tmp_path: Path) -> None:
    copied = _packet_copy(tmp_path)
    assert _build(packet_root=copied) == _build(packet_root=PACKET_ROOT)


def test_locale_timezone_and_cwd_do_not_change_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    baseline = _build()
    monkeypatch.setenv("LANG", "tr_TR.UTF-8")
    monkeypatch.setenv("LC_ALL", "C")
    monkeypatch.setenv("TZ", "Pacific/Honolulu")
    monkeypatch.chdir(tmp_path)
    assert _build() == baseline


def test_authorization_copy_through_is_digest_load_bearing_but_row_statuses_are_not() -> None:
    original_inventory = _inventory()
    original = _build(original_inventory)
    documented_inventory = copy.deepcopy(original_inventory)
    documented_inventory["authorization_status_input"] = {
        "value": "documented",
        "source_reference": "caller.authorization-record",
        "provenance": "caller_supplied_no_derivation",
    }
    documented = _build(documented_inventory)
    assert documented["manifest_digest"] != original["manifest_digest"]
    assert [
        (row["status"], row["reason_codes"], row["matched_artifact_ids"])
        for row in documented["entries"]
    ] == [
        (row["status"], row["reason_codes"], row["matched_artifact_ids"])
        for row in original["entries"]
    ]


def test_renderer_is_deterministic_and_never_includes_packet_prose() -> None:
    manifest = _build()
    first = render_submission_packet_manifest(manifest)
    second = render_submission_packet_manifest(
        json.loads(json.dumps(manifest, sort_keys=True))
    )
    assert first == second
    assert "Review pathway: institutional determination required" in first
    assert "Submission readiness: no_listed_gaps_located" in first
    assert "Authorization status: not_provided" in first
    assert "Review timeline: unknown — obtain current institutional estimate" in first
    assert "## Packet Observations" in first
    assert RENDERED_BOUNDARY in first
    assert "STRUCTURAL-FIXTURE-667" not in first
    assert "Test-only structural attachment row" not in first


def test_resolved_empty_renderer_does_not_invent_unresolved_entry_status() -> None:
    context, registry, _resolved = _authority()
    profile = next(
        row
        for row in registry["profiles"]
        if row["profile_id"] == "us.hhs.45-cfr-46.subpart-a"
    )
    for requirement in profile["requirements"]:
        requirement["consumer_scopes"] = [
            scope
            for scope in requirement["consumer_scopes"]
            if scope != "submission_packet"
        ]
    _repin_profile(context, profile)
    resolved = resolve(context, registry)
    manifest = _build(_inventory(), PACKET_ROOT, context, registry, resolved)
    assert manifest["entries"] == []
    assert manifest["excluded_requirements"] == []
    assert manifest["unresolved_reasons"] == []
    assert manifest["administrative_status"]["submission_readiness"] == (
        "no_listed_gaps_located"
    )
    rendered = render_submission_packet_manifest(manifest)
    assert "| none | none | none | none | none | none | none |" in rendered
    assert packet_runtime._md("APPLICABILITY_UNRESOLVED") not in rendered


def test_context_free_empty_renderer_carries_unresolved_only_in_reason_table() -> None:
    manifest = build_submission_packet_manifest(_inventory(), PACKET_ROOT)
    rendered = render_submission_packet_manifest(manifest)
    assert "| none | none | none | none | none | none | none |" in rendered
    assert (
        f"| {packet_runtime._md('APPLICABILITY_UNRESOLVED')} | "
        f"{packet_runtime._md('AUTHORITY_INPUT_NOT_PROVIDED')} | "
        "not provided | not provided |"
    ) in rendered


def test_renderer_preserves_false_applicability_accounting() -> None:
    context, registry, _resolved, overlay = _synthetic_overlay_authority()
    base = next(
        row
        for row in overlay["requirements"]
        if row["requirement_id"] == "synthetic.packet.base-consent"
    )
    base["applies_if"] = {
        "op": "fact_equals",
        "fact_id": "data.special_category",
        "value": True,
    }
    _repin_overlay(context, overlay)
    special = next(
        row
        for row in context["declared_facts"]
        if row["fact_id"] == "data.special_category"
    )
    special["state"], special["value"] = "declared", False
    resolved = resolve(context, registry)
    manifest = _build(_inventory(), PACKET_ROOT, context, registry, resolved)
    excluded = next(
        row
        for row in manifest["excluded_requirements"]
        if row["requirement_ref"]["requirement_id"]
        == "synthetic.packet.base-consent"
    )
    rendered = render_submission_packet_manifest(manifest)
    assert "## Excluded Requirements" in rendered
    assert (
        f"| {packet_runtime._md('synthetic.packet.base-consent')} | "
        f"{packet_runtime._md(excluded['requirement_ref']['requirement_pointer'])} | "
        f"{packet_runtime._md('resolved_predicate_false')} |"
    ) in rendered


def test_renderer_neutralizes_markdown_active_inventory_path(
    tmp_path: Path,
) -> None:
    packet = _packet_copy(tmp_path)
    inventory = _inventory()
    artifact = _artifact(inventory, "fixture.us-consent")
    original = packet / artifact["relative_path"]
    malicious = (
        "<img src=x>-![x](javascript:alert(1))-`code`-pipe|cell-"
        "line\u2028# heading.txt"
    )
    original.rename(packet / malicious)
    artifact["relative_path"] = malicious
    manifest = _build(inventory, packet)
    rendered = render_submission_packet_manifest(manifest)
    assert malicious not in rendered
    assert "javascript:" not in rendered
    assert "<img" not in rendered
    assert "\u2028" not in rendered
    observation_lines = rendered.split("## Packet Observations", 1)[1].split(
        "## Mechanical Evidence Entries", 1
    )[0]
    assert sum(
        line.startswith(f"| {packet_runtime._md(artifact['artifact_id'])} |")
        for line in observation_lines.splitlines()
    ) == 1

    markdown_it = pytest.importorskip("markdown_it")
    tokens = markdown_it.MarkdownIt().parse(rendered)
    # link_open / image / html_inline nest under inline tokens' children;
    # only html_block appears at the top level.
    flattened = [child for token in tokens for child in (token.children or [])]
    assert not any(
        token.type in {"link_open", "image", "html_inline", "html_block"}
        for token in [*tokens, *flattened]
    )


def _cli_inputs(tmp_path: Path) -> dict[str, Path]:
    context, registry, resolved = _authority()
    paths = {
        "inventory": tmp_path / "inventory.json",
        "context": tmp_path / "context.json",
        "registry": tmp_path / "registry.json",
        "resolved": tmp_path / "resolved.json",
        "manifest": tmp_path / "manifest.json",
        "rendered": tmp_path / "manifest.md",
    }
    _write_json(paths["inventory"], _inventory())
    _write_json(paths["context"], context)
    _write_json(paths["registry"], registry)
    _write_json(paths["resolved"], resolved)
    return paths


def _authority_cli_args(paths: dict[str, Path]) -> list[str]:
    return [
        "--context",
        str(paths["context"]),
        "--registry",
        str(paths["registry"]),
        "--resolved",
        str(paths["resolved"]),
    ]


def test_cli_build_validate_and_render_all_use_exact_replay(tmp_path: Path) -> None:
    paths = _cli_inputs(tmp_path)
    common = [
        "--inventory",
        str(paths["inventory"]),
        "--packet-root",
        str(PACKET_ROOT),
        *_authority_cli_args(paths),
    ]
    built = subprocess.run(
        [
            sys.executable,
            str(RUNTIME),
            "build",
            *common,
            "--output",
            str(paths["manifest"]),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert built.returncode == 0, built.stderr
    built_manifest = _json(paths["manifest"])
    _validator(MANIFEST_SCHEMA).validate(built_manifest)
    manifest_bytes = paths["manifest"].read_bytes()
    assert manifest_bytes == packet_runtime._canonical_bytes(built_manifest)
    assert len(manifest_bytes) <= packet_runtime.MAX_MANIFEST_BYTES

    validated = subprocess.run(
        [
            sys.executable,
            str(RUNTIME),
            "validate",
            "--manifest",
            str(paths["manifest"]),
            *common,
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert validated.returncode == 0, validated.stderr

    rendered = subprocess.run(
        [
            sys.executable,
            str(RUNTIME),
            "render",
            "--manifest",
            str(paths["manifest"]),
            *common,
            "--output",
            str(paths["rendered"]),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert rendered.returncode == 0, rendered.stderr
    assert RENDERED_BOUNDARY in paths["rendered"].read_text(encoding="utf-8")

    forged = _json(paths["manifest"])
    forged["entries"][0]["matched_artifact_ids"] = []
    _repin_manifest(forged)
    _write_json(paths["manifest"], forged)
    rejected = subprocess.run(
        [
            sys.executable,
            str(RUNTIME),
            "render",
            "--manifest",
            str(paths["manifest"]),
            *common,
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert rejected.returncode == 2
    assert "exactly match deterministic replay" in rejected.stderr


@pytest.mark.parametrize(
    ("target", "raw"),
    [
        ("inventory", '{"schema_version":"a","schema_version":"b"}'),
        ("inventory", '{"value":NaN}'),
        ("context", '{"schema_version":"a","schema_version":"b"}'),
        ("context", '{"value":Infinity}'),
        ("registry", '{"schema_version":"a","schema_version":"b"}'),
        ("registry", '{"value":-Infinity}'),
        ("resolved", '{"schema_version":"a","schema_version":"b"}'),
        ("resolved", '{"value":NaN}'),
        ("manifest", '{"schema_version":"a","schema_version":"b"}'),
        ("manifest", '{"value":Infinity}'),
    ],
)
def test_cli_rejects_duplicate_keys_and_nonfinite_json(
    tmp_path: Path, target: str, raw: str
) -> None:
    paths = _cli_inputs(tmp_path)
    manifest = _build()
    _write_json(paths["manifest"], manifest)
    paths[target].write_text(raw, encoding="utf-8")
    common = [
        "--inventory",
        str(paths["inventory"]),
        "--packet-root",
        str(PACKET_ROOT),
        *_authority_cli_args(paths),
    ]
    command = "validate" if target == "manifest" else "build"
    argv = [sys.executable, str(RUNTIME), command]
    if command == "validate":
        argv.extend(["--manifest", str(paths["manifest"])])
    argv.extend(common)
    completed = subprocess.run(
        argv,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 2
    assert "duplicate JSON key" in completed.stderr or "non-finite" in completed.stderr


@pytest.mark.parametrize(
    "raw",
    [
        '{"oversized_integer":' + "9" * 5000 + "}",
        '{"deep":' + "[" * 2000 + "0" + "]" * 2000 + "}",
    ],
)
def test_cli_rejects_parser_resource_edges_with_rc2_and_no_traceback(
    tmp_path: Path, raw: str
) -> None:
    paths = _cli_inputs(tmp_path)
    paths["inventory"].write_text(raw, encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME),
            "build",
            "--inventory",
            str(paths["inventory"]),
            "--packet-root",
            str(PACKET_ROOT),
            *_authority_cli_args(paths),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 2
    assert completed.stderr.startswith("ERROR:")
    assert "Traceback" not in completed.stderr


def test_cli_rejects_escaped_lone_surrogate_with_rc2_and_no_traceback(
    tmp_path: Path,
) -> None:
    paths = _cli_inputs(tmp_path)
    inventory = _inventory()
    inventory["artifacts"][0]["relative_path"] = "surrogate-\ud800.txt"
    paths["inventory"].write_text(
        json.dumps(inventory, ensure_ascii=True), encoding="utf-8"
    )
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME),
            "build",
            "--inventory",
            str(paths["inventory"]),
            "--packet-root",
            str(PACKET_ROOT),
            *_authority_cli_args(paths),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 2
    assert completed.stderr.startswith("ERROR:")
    assert "surrogate" in completed.stderr
    assert "Traceback" not in completed.stderr
