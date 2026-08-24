#!/usr/bin/env python3
"""Contract, fallback, selection, and correction tests for issue #742."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from scripts.research_workflow_profile import (
    DEFAULT_FIELD_GENERAL_PROFILE,
    JCS_SAFE_INTEGER_MAX,
    PIPELINE_STAGE_IDS,
    PROFILE_HASH_PLACEHOLDER,
    RESEARCH_FAMILIES,
    RESEARCH_FAMILY_DISPLAY_NAMES,
    TASK_FAMILIES,
    ContractError,
    active_selection_summary,
    canonical_bytes,
    correct_selection,
    create_fallback_receipt,
    create_selection_receipt,
    effective_stage_map,
    load_profile,
    profile_digest,
    profile_binding,
    seal_profile,
    validate_profile,
    validate_profile_catalog,
    validate_selection_receipt,
    validate_shipped_field_general,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACTS = REPO_ROOT / "shared" / "contracts" / "research_workflow"
PROFILE_SCHEMA = CONTRACTS / "research_workflow_profile.schema.json"
RECEIPT_SCHEMA = CONTRACTS / "research_workflow_profile_selection_receipt.schema.json"
RUNTIME = REPO_ROOT / "scripts" / "research_workflow_profile.py"
MATRIX = REPO_ROOT / "shared" / "contracts" / "capability" / "stage_capability_matrix.json"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_validators() -> tuple[Draft202012Validator, Draft202012Validator]:
    profile_schema = _json(PROFILE_SCHEMA)
    receipt_schema = _json(RECEIPT_SCHEMA)
    Draft202012Validator.check_schema(profile_schema)
    Draft202012Validator.check_schema(receipt_schema)
    resource = Resource.from_contents(profile_schema)
    registry = Registry().with_resource(profile_schema["$id"], resource)
    registry = registry.with_resource("research_workflow_profile.schema.json", resource)
    return (
        Draft202012Validator(
            profile_schema, registry=registry, format_checker=FormatChecker()
        ),
        Draft202012Validator(
            receipt_schema, registry=registry, format_checker=FormatChecker()
        ),
    )


def _fallback() -> dict:
    return load_profile(DEFAULT_FIELD_GENERAL_PROFILE)


def _clinical_profile(*, version: str = "1.0.0") -> dict:
    profile = copy.deepcopy(_fallback())
    profile.update(
        {
            "profile_id": "clinical_human_subjects",
            "profile_version": version,
            "research_family": "clinical_human_subjects",
            "display_name": copy.deepcopy(
                RESEARCH_FAMILY_DISPLAY_NAMES["clinical_human_subjects"]
            ),
            "stage_map": {
                task_family: {"state": "applicable"}
                for task_family in TASK_FAMILIES
            },
            "alternative_categories": {
                "state": "declared",
                "categories": ["alternative_design", "boundary_condition"],
            },
            "branch_budget": 2,
            "authority_points": [
                {
                    "task_family": "methodology",
                    "authority": "institutional_review_board",
                    "requirement": "Obtain the applicable determination before authority-sensitive reuse.",
                }
            ],
            "known_exclusions": ["Non-human computational simulation only"],
            "unresolved_fit_note": "Local jurisdiction and review pathway remain user-confirmed inputs.",
            "provenance": {
                "source": "user_authored",
                "source_pointer": "user declaration: clinical profile",
                "last_reviewed_at": "2026-08-24",
                "freshness_state": "unverified",
            },
            "content_sha256": PROFILE_HASH_PLACEHOLDER,
        }
    )
    return seal_profile(profile)


def _write_canonical(path: Path, value: dict) -> Path:
    path.write_bytes(canonical_bytes(value))
    return path


def test_schemas_compile_and_validate_shipped_artifacts() -> None:
    profile_validator, receipt_validator = _schema_validators()
    profile = _fallback()
    receipt = create_selection_receipt(
        profile,
        selected_by="fallback_automatic",
        ars_suite_version="3.20.1",
        selected_at="2026-08-24T10:00:00+08:00",
    )
    assert list(profile_validator.iter_errors(profile)) == []
    assert list(receipt_validator.iter_errors(receipt)) == []


def test_shipped_field_general_exact_values_hash_and_canonical_storage() -> None:
    profile = _fallback()
    validate_shipped_field_general(profile)
    raw = DEFAULT_FIELD_GENERAL_PROFILE.read_bytes()
    assert raw == canonical_bytes(profile)
    assert not raw.endswith(b"\n")
    assert profile["content_sha256"] == profile_digest(profile)
    assert profile["authority_points"] == []
    assert profile["alternative_categories"] == {
        "state": "unresolved",
        "categories": [],
    }
    assert profile["branch_budget"] == 3
    assert profile["stage_map"]["integrity_check"] == {"state": "applicable"}
    assert all(
        profile["stage_map"][task_family] == {"state": "unresolved_fit"}
        for task_family in TASK_FAMILIES
        if task_family != "integrity_check"
    )


def test_all_research_families_have_explicit_en_and_zh_tw_names() -> None:
    assert set(RESEARCH_FAMILY_DISPLAY_NAMES) == set(RESEARCH_FAMILIES)
    for names in RESEARCH_FAMILY_DISPLAY_NAMES.values():
        assert set(names) == {"en", "zh_TW"}
        assert names["en"].strip()
        assert names["zh_TW"].strip()
        assert any(ord(character) > 127 for character in names["zh_TW"])


def test_task_vocabulary_and_pipeline_mapping_are_closed_and_matrix_aligned() -> None:
    matrix = _json(MATRIX)
    assert tuple(matrix["task_families"]) == TASK_FAMILIES
    assert tuple(PIPELINE_STAGE_IDS) == TASK_FAMILIES
    assert PIPELINE_STAGE_IDS["integrity_check"] == (
        "stage_2_5_gate",
        "stage_4_5_gate",
    )
    assert PIPELINE_STAGE_IDS["finalization"] == (
        "stage_5_final",
        "stage_6_record",
    )


def test_omitted_stage_is_effectively_unresolved_never_applicable() -> None:
    profile = _clinical_profile()
    profile["stage_map"] = {"integrity_check": {"state": "applicable"}}
    profile = seal_profile(profile)
    expanded = effective_stage_map(profile)
    assert expanded["integrity_check"] == {"state": "applicable"}
    assert expanded["drafting"] == {"state": "unresolved_fit"}
    assert set(expanded) == set(TASK_FAMILIES)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda p: p.update({"manuscript_quality": "high"}), "undeclared field"),
        (
            lambda p: p["stage_map"].update({"statistical_analysis": {"state": "applicable"}}),
            "unknown task-family",
        ),
        (
            lambda p: p.update(
                {"alternative_categories": {"state": "unresolved", "categories": ["rival_theory"]}}
            ),
            "must be empty",
        ),
        (lambda p: p.update({"overflow_behavior": "auto_prune"}), "ask_merge_park_archive"),
    ],
)
def test_profile_validator_refuses_closed_contract_violations(mutation, message) -> None:
    profile = _clinical_profile()
    mutation(profile)
    profile["content_sha256"] = profile_digest(profile)
    with pytest.raises(ContractError, match=message):
        validate_profile(profile)


def test_authority_empty_only_for_field_general_in_schema_and_runtime() -> None:
    profile = _clinical_profile()
    profile["authority_points"] = []
    profile["content_sha256"] = profile_digest(profile)
    with pytest.raises(ContractError, match="may be empty only"):
        validate_profile(profile)
    profile_validator, _ = _schema_validators()
    assert list(profile_validator.iter_errors(profile))

    fallback = _fallback()
    fallback["authority_points"] = [
        {
            "task_family": "methodology",
            "authority": "invented",
            "requirement": "must not be inferred",
        }
    ]
    fallback["content_sha256"] = profile_digest(fallback)
    with pytest.raises(ContractError, match="must be empty"):
        validate_profile(fallback)
    assert list(profile_validator.iter_errors(fallback))


def test_declared_family_label_is_display_only_and_user_authored_only() -> None:
    profile = _clinical_profile()
    profile["declared_family_label"] = "Community-led hybrid inquiry"
    profile = seal_profile(profile)
    validate_profile(profile)
    profile["provenance"]["source"] = "user_modified"
    profile["content_sha256"] = profile_digest(profile)
    with pytest.raises(ContractError, match="user_authored"):
        validate_profile(profile)


def test_user_authored_field_general_summary_is_not_mislabeled_as_fallback(
    tmp_path: Path,
) -> None:
    profile = copy.deepcopy(_fallback())
    profile.update(
        {
            "profile_id": "community_hybrid",
            "declared_family_label": "Community-led hybrid inquiry",
            "provenance": {
                "source": "user_authored",
                "source_pointer": "user declaration: community hybrid",
                "last_reviewed_at": "2026-08-24",
                "freshness_state": "unverified",
            },
        }
    )
    profile = seal_profile(profile)
    receipt = create_selection_receipt(
        profile,
        selected_by="user_explicit",
        ars_suite_version="3.20.1",
        selected_at="2026-08-24T10:00:00+08:00",
    )
    summary = active_selection_summary(receipt, profile)
    assert summary["fallback_active"] is False
    assert summary["fallback_notice"] is None
    assert summary["declared_family_label"] == "Community-led hybrid inquiry"

    receipt_path = _write_canonical(tmp_path / "receipt.json", receipt)
    profile_path = _write_canonical(tmp_path / "profile.json", profile)
    result = subprocess.run(
        [
            sys.executable,
            str(RUNTIME),
            "show-selection",
            "--receipt",
            str(receipt_path),
            "--profile",
            str(profile_path),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == summary


def test_digest_mismatch_noncanonical_storage_and_duplicate_keys_fail_closed(
    tmp_path: Path,
) -> None:
    profile = _fallback()
    drifted = copy.deepcopy(profile)
    drifted["branch_budget"] = 4
    canonical_path = _write_canonical(tmp_path / "drifted.json", drifted)
    with pytest.raises(ContractError, match="digest mismatch"):
        load_profile(canonical_path)

    pretty_path = tmp_path / "pretty.json"
    pretty_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    with pytest.raises(ContractError, match="exact JSON Canonical Form"):
        load_profile(pretty_path)

    duplicate_path = tmp_path / "duplicate.json"
    duplicate_path.write_text(
        '{"schema_version":"research-workflow-profile/1.0",'
        '"schema_version":"research-workflow-profile/1.0"}',
        encoding="utf-8",
    )
    with pytest.raises(ContractError, match="duplicate JSON key"):
        load_profile(duplicate_path)


def test_jcs_safe_integer_boundary_matches_cross_implementation_vector() -> None:
    profile_validator, _ = _schema_validators()
    profile = _clinical_profile()
    profile["branch_budget"] = JCS_SAFE_INTEGER_MAX
    profile = seal_profile(profile)
    assert list(profile_validator.iter_errors(profile)) == []
    assert canonical_bytes({"z": "領域", "a": JCS_SAFE_INTEGER_MAX}) == (
        b'{"a":9007199254740991,"z":"\xe9\xa0\x98\xe5\x9f\x9f"}'
    )

    profile["branch_budget"] = JCS_SAFE_INTEGER_MAX + 1
    assert list(profile_validator.iter_errors(profile))
    with pytest.raises(ContractError, match="JCS safe"):
        seal_profile(profile)


def test_profile_version_is_immutable_across_catalog() -> None:
    first = _clinical_profile()
    second = copy.deepcopy(first)
    second["branch_budget"] = 4
    second = seal_profile(second)
    with pytest.raises(ContractError, match="reuses immutable version"):
        validate_profile_catalog([first, second])
    validate_profile_catalog([first, copy.deepcopy(first)])


def test_no_selection_creates_visible_automatic_fallback_receipt() -> None:
    receipt = create_fallback_receipt(
        ars_suite_version="3.20.1",
        selected_at="2026-08-24T10:00:00+08:00",
    )
    summary = active_selection_summary(receipt, _fallback())
    assert receipt["selection_chain"][0]["selected_by"] == "fallback_automatic"
    assert summary["fallback_active"] is True
    assert summary["fallback_notice"] == (
        "Field-specific fit and authority points remain unresolved; ask the user."
    )
    assert summary["display_name"]["zh_TW"] == "領域通用後備設定"


def test_automatic_fallback_refuses_a_user_authored_field_general_profile() -> None:
    profile = copy.deepcopy(_fallback())
    profile["profile_id"] = "custom_general"
    profile["provenance"] = {
        "source": "user_authored",
        "source_pointer": "user declaration",
        "last_reviewed_at": "2026-08-24",
        "freshness_state": "unverified",
    }
    profile = seal_profile(profile)
    with pytest.raises(ContractError, match="shipped fallback"):
        create_selection_receipt(
            profile,
            selected_by="fallback_automatic",
            ars_suite_version="3.20.1",
            selected_at="2026-08-24T10:00:00+08:00",
        )


def test_automatic_fallback_refuses_forged_shipped_default_content() -> None:
    profile = copy.deepcopy(_fallback())
    profile["profile_version"] = "1.0.1"
    profile["branch_budget"] = 4
    profile = seal_profile(profile)
    with pytest.raises(ContractError, match="shipped fallback must equal 3"):
        create_selection_receipt(
            profile,
            selected_by="fallback_automatic",
            ars_suite_version="3.20.1",
            selected_at="2026-08-24T10:00:00+08:00",
        )

    profile["branch_budget"] = 3
    profile = seal_profile(profile)
    with pytest.raises(ContractError, match="exact currently shipped"):
        create_selection_receipt(
            profile,
            selected_by="fallback_automatic",
            ars_suite_version="3.20.1",
            selected_at="2026-08-24T10:00:00+08:00",
        )


def test_historical_automatic_fallback_remains_displayable_and_correctable() -> None:
    historical = copy.deepcopy(_fallback())
    historical["profile_version"] = "0.9.0"
    historical["provenance"]["last_reviewed_at"] = "2026-08-01"
    historical["provenance"]["freshness_state"] = "stale"
    historical = seal_profile(historical)
    receipt = {
        "schema_version": "research-workflow-profile-selection-receipt/1.0",
        "selection_chain": [
            {
                "sequence": 1,
                "profile_binding": profile_binding(historical),
                "selected_by": "fallback_automatic",
                "ars_suite_version": "3.20.0",
                "selected_at": "2026-08-01T10:00:00Z",
                "supersedes_sequence": None,
            }
        ],
        "artifact_stale_marks": [],
    }
    validate_selection_receipt(receipt)
    assert active_selection_summary(receipt, historical)["freshness_state"] == "stale"

    corrected = correct_selection(
        receipt,
        historical,
        _clinical_profile(),
        [],
        selected_by="user_explicit",
        ars_suite_version="3.20.1",
        selected_at="2026-08-24T10:00:00Z",
    )
    assert [row["sequence"] for row in corrected["selection_chain"]] == [1, 2]


def test_correction_appends_selection_and_marks_every_prior_output_stale() -> None:
    fallback = _fallback()
    clinical = _clinical_profile()
    receipt = create_selection_receipt(
        fallback,
        selected_by="user_explicit",
        ars_suite_version="3.20.1",
        selected_at="2026-08-24T10:00:00+08:00",
    )
    original_receipt = copy.deepcopy(receipt)
    stage_outputs = [
        {"artifact_ref": "rq-brief.md", "task_family": "rq_formation"},
        {"artifact_ref": "draft.md", "task_family": "drafting"},
    ]
    updated = correct_selection(
        receipt,
        fallback,
        clinical,
        stage_outputs,
        selected_by="user_confirmed_proposal",
        ars_suite_version="3.20.1",
        selected_at="2026-08-24T10:05:00+08:00",
    )
    assert receipt == original_receipt
    assert [item["sequence"] for item in updated["selection_chain"]] == [1, 2]
    assert updated["selection_chain"][1]["supersedes_sequence"] == 1
    assert [mark["artifact_ref"] for mark in updated["artifact_stale_marks"]] == [
        "rq-brief.md",
        "draft.md",
    ]
    for mark in updated["artifact_stale_marks"]:
        assert mark["state"] == "stale"
        assert mark["reason"] == "profile_context_changed"
        assert mark["produced_under_selection_sequence"] == 1
        assert mark["caused_by_selection_sequence"] == 2
        assert mark["authority_requirements_introduced"] == clinical["authority_points"]
        assert mark["authority_sensitive_reuse_gate"] == "unmet"
    validate_selection_receipt(updated)


def test_correction_without_new_authority_still_marks_outputs_stale() -> None:
    first = _clinical_profile(version="1.0.0")
    second = copy.deepcopy(first)
    second["profile_version"] = "1.0.1"
    second["branch_budget"] = 3
    second = seal_profile(second)
    receipt = create_selection_receipt(
        first,
        selected_by="user_explicit",
        ars_suite_version="3.20.1",
        selected_at="2026-08-24T10:00:00Z",
    )
    updated = correct_selection(
        receipt,
        first,
        second,
        [{"artifact_ref": "methods.md", "task_family": "methodology"}],
        selected_by="user_explicit",
        ars_suite_version="3.20.1",
        selected_at="2026-08-24T10:01:00Z",
    )
    mark = updated["artifact_stale_marks"][0]
    assert mark["state"] == "stale"
    assert mark["authority_requirements_introduced"] == []
    assert mark["authority_sensitive_reuse_gate"] == "not_introduced"


def test_correction_refuses_binding_mismatch_noop_duplicate_outputs_and_old_time() -> None:
    fallback = _fallback()
    clinical = _clinical_profile()
    receipt = create_selection_receipt(
        fallback,
        selected_by="user_explicit",
        ars_suite_version="3.20.1",
        selected_at="2026-08-24T10:00:00Z",
    )
    with pytest.raises(ContractError, match="current selection receipt"):
        correct_selection(
            receipt,
            clinical,
            fallback,
            [],
            selected_by="user_explicit",
            ars_suite_version="3.20.1",
            selected_at="2026-08-24T10:01:00Z",
        )
    with pytest.raises(ContractError, match="must change"):
        correct_selection(
            receipt,
            fallback,
            fallback,
            [],
            selected_by="user_explicit",
            ars_suite_version="3.20.1",
            selected_at="2026-08-24T10:01:00Z",
        )
    with pytest.raises(ContractError, match="duplicate artifact_ref"):
        correct_selection(
            receipt,
            fallback,
            clinical,
            [
                {"artifact_ref": "draft.md", "task_family": "drafting"},
                {"artifact_ref": "draft.md", "task_family": "revision"},
            ],
            selected_by="user_explicit",
            ars_suite_version="3.20.1",
            selected_at="2026-08-24T10:01:00Z",
        )
    with pytest.raises(ContractError, match="later than"):
        correct_selection(
            receipt,
            fallback,
            clinical,
            [],
            selected_by="user_explicit",
            ars_suite_version="3.20.1",
            selected_at="2026-08-24T09:59:00Z",
        )


def test_receipt_runtime_pins_dense_append_only_chain_and_stale_reason() -> None:
    receipt = create_fallback_receipt(
        ars_suite_version="3.20.1", selected_at="2026-08-24T10:00:00Z"
    )
    broken = copy.deepcopy(receipt)
    broken["selection_chain"][0]["sequence"] = 2
    with pytest.raises(ContractError, match="dense sequence"):
        validate_selection_receipt(broken)

    clinical = _clinical_profile()
    updated = correct_selection(
        receipt,
        _fallback(),
        clinical,
        [{"artifact_ref": "draft.md", "task_family": "drafting"}],
        selected_by="user_explicit",
        ars_suite_version="3.20.1",
        selected_at="2026-08-24T10:01:00Z",
    )
    updated["artifact_stale_marks"][0]["reason"] = "silently_rewrite"
    with pytest.raises(ContractError, match="profile_context_changed"):
        validate_selection_receipt(updated)


def test_receipt_schema_refuses_unknown_fields_and_wrong_stale_reason() -> None:
    _, receipt_validator = _schema_validators()
    receipt = create_fallback_receipt(
        ars_suite_version="3.20.1", selected_at="2026-08-24T10:00:00Z"
    )
    receipt["selection_chain"][0]["manuscript_score"] = 0
    assert list(receipt_validator.iter_errors(receipt))


@pytest.mark.parametrize(
    "timestamp",
    [
        "2026-08-24T10:00:00Z",
        "2026-08-24t10:00:00z",
        "2026-08-24T10:00:00.123456+08:00",
    ],
)
def test_timestamp_runtime_and_schema_accept_the_same_rfc3339_subset(
    timestamp: str,
) -> None:
    _, receipt_validator = _schema_validators()
    receipt = create_selection_receipt(
        _fallback(),
        selected_by="user_explicit",
        ars_suite_version="3.20.1",
        selected_at=timestamp,
    )
    assert list(receipt_validator.iter_errors(receipt)) == []


@pytest.mark.parametrize(
    "timestamp",
    [
        "2026-08-24T10:00:00+08",
        "2026-08-24T10:00:00+0800",
        "2026-08-24T10:00:00,5Z",
        "2026-08-24T10:00:00+08:00:30",
        "2026-08-24T10:00:00.1234567Z",
    ],
)
def test_timestamp_runtime_and_schema_reject_non_contract_variants(
    timestamp: str,
) -> None:
    _, receipt_validator = _schema_validators()
    receipt = create_fallback_receipt(
        ars_suite_version="3.20.1", selected_at="2026-08-24T10:00:00Z"
    )
    receipt["selection_chain"][0]["selected_at"] = timestamp
    assert list(receipt_validator.iter_errors(receipt))
    with pytest.raises(ContractError, match="ISO 8601 date-time"):
        validate_selection_receipt(receipt)


def test_stale_shipped_profile_remains_visible_never_silently_current() -> None:
    profile = copy.deepcopy(_fallback())
    profile["profile_version"] = "1.0.1"
    profile["provenance"]["freshness_state"] = "stale"
    profile["provenance"]["last_reviewed_at"] = "2026-08-25"
    profile = seal_profile(profile)
    validate_shipped_field_general(profile)
    receipt = create_selection_receipt(
        profile,
        selected_by="user_explicit",
        ars_suite_version="3.20.2",
        selected_at="2026-08-25T10:00:00+08:00",
    )
    summary = active_selection_summary(receipt, profile)
    assert summary["fallback_active"] is True
    assert summary["freshness_state"] == "stale"


def test_cli_omitted_profile_emits_explicit_fallback_and_validates_it(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(RUNTIME),
            "select",
            "--ars-suite-version",
            "3.20.1",
            "--selected-at",
            "2026-08-24T10:00:00+08:00",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    receipt = json.loads(result.stdout)
    validate_selection_receipt(receipt)
    assert receipt["selection_chain"][0]["selected_by"] == "fallback_automatic"
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(result.stdout, encoding="utf-8")
    validation = subprocess.run(
        [sys.executable, str(RUNTIME), "validate-receipt", str(receipt_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert validation.returncode == 0, validation.stderr


def test_cli_correction_requires_explicit_stage_output_inventory(tmp_path: Path) -> None:
    fallback = _fallback()
    clinical = _clinical_profile()
    receipt = create_selection_receipt(
        fallback,
        selected_by="user_explicit",
        ars_suite_version="3.20.1",
        selected_at="2026-08-24T10:00:00Z",
    )
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    clinical_path = _write_canonical(tmp_path / "clinical.json", clinical)
    result = subprocess.run(
        [
            sys.executable,
            str(RUNTIME),
            "correct",
            "--receipt",
            str(receipt_path),
            "--previous-profile",
            str(DEFAULT_FIELD_GENERAL_PROFILE),
            "--profile",
            str(clinical_path),
            "--selected-by",
            "user_explicit",
            "--ars-suite-version",
            "3.20.1",
            "--selected-at",
            "2026-08-24T10:01:00Z",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "--stage-outputs" in result.stderr


def test_capability_matrix_registers_implemented_profile_with_not_run_evidence() -> None:
    matrix = _json(MATRIX)
    row = next(
        item
        for item in matrix["rows"]
        if item["row_id"] == "rq_formation.research_workflow_profile"
    )
    assert row["task_family"] == "rq_formation"
    assert row["mechanism_status"] == "IMPLEMENTED"
    assert row["deterministic_conformance"] == "CI_GATED"
    assert row["behavioral_evidence"] == {"status": "NOT_RUN"}
    assert "scripts/test_research_workflow_profile.py" in row["conformance_pinned_by"]
    assert "every downstream stage" in " ".join(row["known_exclusions"])
    assert "outcome" in row["max_licensed_claim"]
