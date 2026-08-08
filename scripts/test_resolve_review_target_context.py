#!/usr/bin/env python3
"""Contract, resolver, digest, and blind-boundary tests for issue #683."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from resolve_review_target_context import (
    ContractError,
    render_brief,
    resolve,
    validate_declaration,
    validate_registry,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "scripts" / "fixtures" / "review_target_context"
CONTRACTS = REPO_ROOT / "shared" / "contracts" / "review_target"
RESOLVER = REPO_ROOT / "scripts" / "resolve_review_target_context.py"
LIVE_REGISTRY = REPO_ROOT / "shared" / "review_criteria_registry.json"
SOURCE_PATH = REPO_ROOT / "academic-paper-reviewer" / "references" / "review_criteria_framework.md"


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def declaration() -> dict[str, object]:
    return _json(FIXTURES / "exact-declaration.json")


@pytest.fixture
def field_general_declaration() -> dict[str, object]:
    return _json(FIXTURES / "field-general-declaration.json")


@pytest.fixture
def registry() -> dict[str, object]:
    return _json(FIXTURES / "synthetic-registry.json")


def _validator(schema_name: str) -> Draft202012Validator:
    schema = _json(CONTRACTS / schema_name)
    declaration_schema = _json(CONTRACTS / "review_target_declaration.schema.json")
    resource = Resource.from_contents(declaration_schema)
    store = Registry().with_resource(declaration_schema["$id"], resource)
    store = store.with_resource("review_target_declaration.schema.json", resource)
    return Draft202012Validator(schema, registry=store, format_checker=FormatChecker())


def _row(registry: dict[str, object], criterion_id: str) -> dict[str, object]:
    return next(
        item for item in registry["criteria"] if item["criterion_id"] == criterion_id  # type: ignore[index,union-attr]
    )


def test_schemas_and_live_registry_are_valid(field_general_declaration: dict[str, object]) -> None:
    live = _json(LIVE_REGISTRY)
    _validator("review_target_declaration.schema.json").validate(field_general_declaration)
    _validator("criteria_registry.schema.json").validate(live)
    validate_registry(live)
    context = resolve(field_general_declaration, live)
    _validator("review_target_context.schema.json").validate(context)
    assert context["fallback_state"] == "field_general"
    assert context["outcomes"]["venue_fit"] == []  # type: ignore[index]
    assert SOURCE_PATH.is_file()
    assert all(
        item["source"]["uri"]  # type: ignore[index]
        == "repository://academic-paper-reviewer/references/review_criteria_framework.md"
        for item in live["criteria"]  # type: ignore[union-attr]
    )


def test_exact_target_selects_all_authority_classes_and_distinct_outcomes(
    declaration: dict[str, object], registry: dict[str, object]
) -> None:
    context = resolve(declaration, registry)
    assert context["fallback_state"] == "venue_exact"
    assert context["resolution_state"] == "resolved"
    assert {item["authority_class"] for item in context["selected_criteria"]} == {  # type: ignore[union-attr]
        "official_venue_type",
        "field_society_standard",
        "reporting_design_overlay",
        "broad_field_fallback",
    }
    outcomes = context["outcomes"]
    assert set(outcomes) == {"scientific_validity", "venue_fit", "submission_readiness"}  # type: ignore[arg-type]
    assert set().union(*map(set, outcomes.values())) == set(context["selected_criterion_ids"])  # type: ignore[union-attr]


def test_declaration_is_preserved_and_target_is_not_inferred(
    field_general_declaration: dict[str, object], registry: dict[str, object]
) -> None:
    context = resolve(field_general_declaration, registry)
    assert context["declaration"] == field_general_declaration
    assert context["declaration"]["target"]["venue"] is None  # type: ignore[index]
    assert not any(
        item["authority_class"] == "official_venue_type"  # type: ignore[index]
        for item in context["selected_criteria"]  # type: ignore[union-attr]
    )


def test_declared_unknown_venue_is_partial_not_impersonated(
    declaration: dict[str, object], registry: dict[str, object]
) -> None:
    declaration["target"]["venue"] = "Unregistered Journal"  # type: ignore[index]
    context = resolve(declaration, registry)
    assert context["fallback_state"] == "declared_target_unresolved"
    assert context["resolution_state"] == "partial"
    assert context["outcomes"]["venue_fit"] == []  # type: ignore[index]
    assert context["unresolved"][0]["dimension"] == "venue_fit"  # type: ignore[index]


def test_exact_match_requires_contribution_type(
    declaration: dict[str, object], registry: dict[str, object]
) -> None:
    declaration["target"]["contribution_type"] = "Registered Report"  # type: ignore[index]
    context = resolve(declaration, registry)
    assert context["fallback_state"] == "declared_target_unresolved"
    assert not any(
        item["authority_class"] == "official_venue_type"  # type: ignore[index]
        for item in context["selected_criteria"]  # type: ignore[union-attr]
    )


def test_stale_and_unverified_sources_cannot_block(
    declaration: dict[str, object], registry: dict[str, object]
) -> None:
    context = resolve(declaration, registry)
    pointers = {item["criterion_id"]: item for item in context["selected_criteria"]}  # type: ignore[union-attr]
    assert pointers["official.example.format"]["blocking_eligible"] is False
    assert pointers["official.example.format"]["advisory_reasons"] == ["source_stale"]
    assert pointers["overlay.prisma.flow"]["blocking_eligible"] is False
    assert pointers["overlay.prisma.flow"]["advisory_reasons"] == ["source_unverified"]


def test_exact_profile_with_only_noncurrent_sources_is_advisory(
    declaration: dict[str, object], registry: dict[str, object]
) -> None:
    source = _row(registry, "official.example.scope")["source"]
    source["freshness"] = "stale"  # type: ignore[index]
    context = resolve(declaration, registry)
    assert context["fallback_state"] == "venue_exact_advisory"
    assert context["resolution_state"] == "advisory_only"
    assert not any(
        item["blocking_eligible"]  # type: ignore[index]
        for item in context["selected_criteria"]  # type: ignore[union-attr]
        if item["authority_class"] == "official_venue_type"  # type: ignore[index]
    )


def test_interdisciplinary_conflicts_remain_parallel(
    declaration: dict[str, object], registry: dict[str, object]
) -> None:
    context = resolve(declaration, registry)
    assert context["parallel_conflicts"] == [
        {
            "conflict_group": "synthetic.reporting-emphasis",
            "criterion_ids": ["field.computing.transparency", "field.education.context"],
            "reason": "parallel_interdisciplinary_criteria_require_human_resolution",
        }
    ]
    brief = render_brief(context, registry)
    assert "Keep these criteria parallel" in brief
    assert "average" in brief


def test_overlay_is_selected_only_when_author_declares_it(
    declaration: dict[str, object], registry: dict[str, object]
) -> None:
    declaration["reporting_design_overlays"] = []
    context = resolve(declaration, registry)
    assert "overlay.prisma.flow" not in context["selected_criterion_ids"]


def test_future_effective_criterion_is_not_applicable(
    declaration: dict[str, object], registry: dict[str, object]
) -> None:
    _row(registry, "field.computing.transparency")["source"]["effective_date"] = "2027-01-01"  # type: ignore[index]
    context = resolve(declaration, registry)
    assert "field.computing.transparency" not in context["selected_criterion_ids"]


def test_explicit_selection_rejects_unknown_and_inapplicable_ids(
    declaration: dict[str, object], registry: dict[str, object]
) -> None:
    declaration["criterion_selection"] = {"mode": "explicit", "ids": ["does.not.exist"]}
    with pytest.raises(ContractError, match="unknown criterion"):
        resolve(declaration, registry)
    declaration["criterion_selection"] = {"mode": "explicit", "ids": ["overlay.prisma.flow"]}
    declaration["reporting_design_overlays"] = []
    with pytest.raises(ContractError, match="inapplicable criterion"):
        resolve(declaration, registry)


def test_numeric_weights_and_manuscript_fields_are_rejected(
    declaration: dict[str, object], registry: dict[str, object]
) -> None:
    declaration["weights"] = {"venue_fit": 0.5}
    with pytest.raises(ContractError, match="undeclared field.*weights"):
        validate_declaration(declaration)
    declaration.pop("weights")
    declaration["manuscript"] = "draft text"
    with pytest.raises(ContractError, match="undeclared field.*manuscript"):
        validate_declaration(declaration)
    registry["criteria"][0]["weight"] = 10  # type: ignore[index]
    with pytest.raises(ContractError, match="undeclared field.*weight"):
        validate_registry(registry)


def test_resolver_enforces_schema_identifier_and_datetime_lexemes(
    declaration: dict[str, object], registry: dict[str, object]
) -> None:
    registry["criteria"][0]["criterion_id"] = "Official/Bad"  # type: ignore[index]
    with pytest.raises(ContractError, match="lowercase letters"):
        validate_registry(registry)
    declaration["confirmed_at"] = "2026-08-08"
    with pytest.raises(ContractError, match="date-time"):
        validate_declaration(declaration)


def test_declaration_schema_rejects_duplicate_precedence_authority(
    declaration: dict[str, object]
) -> None:
    declaration["precedence"][1]["authority_class"] = "official_venue_type"  # type: ignore[index]
    assert list(_validator("review_target_declaration.schema.json").iter_errors(declaration))


def test_requested_as_of_cannot_exceed_registry_as_of(
    declaration: dict[str, object], registry: dict[str, object]
) -> None:
    declaration["criteria_as_of"] = "2026-08-09"
    with pytest.raises(ContractError, match="later than registry.as_of"):
        resolve(declaration, registry)


def test_partition_drift_and_official_nonexact_axes_are_rejected(
    registry: dict[str, object]
) -> None:
    registry["authority_classes"]["official_venue_type"].remove("official.example.scope")  # type: ignore[index]
    with pytest.raises(ContractError, match="absent from partition"):
        validate_registry(registry)
    registry = _json(FIXTURES / "synthetic-registry.json")
    _row(registry, "official.example.scope")["applicability"]["venues"].append("Second Journal")  # type: ignore[index]
    with pytest.raises(ContractError, match="require exactly one value"):
        validate_registry(registry)


def test_digest_is_stable_across_key_order_and_reconfirmation(
    declaration: dict[str, object], registry: dict[str, object]
) -> None:
    first = resolve(declaration, registry)["resolved_digest"]
    reordered = json.loads(json.dumps(declaration, sort_keys=True))
    reordered["confirmed_at"] = "2026-08-09T09:00:00+08:00"
    second = resolve(reordered, json.loads(json.dumps(registry, sort_keys=True)))["resolved_digest"]
    assert first == second


@pytest.mark.parametrize(
    "mutation",
    [
        "target",
        "criterion_version",
        "registry_version",
        "precedence",
    ],
)
def test_substantive_changes_change_resolved_digest(
    mutation: str, declaration: dict[str, object], registry: dict[str, object]
) -> None:
    first = resolve(declaration, registry)["resolved_digest"]
    if mutation == "target":
        declaration["target"]["contribution_type"] = "Registered Report"  # type: ignore[index]
    elif mutation == "criterion_version":
        _row(registry, "field.computing.transparency")["version"] = "1.1"
    elif mutation == "registry_version":
        registry["registry_version"] = "1.1-test"
    else:
        declaration["precedence"][1]["rank"] = 3  # type: ignore[index]
        declaration["precedence"][2]["rank"] = 2  # type: ignore[index]
    assert resolve(declaration, registry)["resolved_digest"] != first


def test_unrelated_registry_addition_changes_registry_digest_not_resolved_digest(
    declaration: dict[str, object], registry: dict[str, object]
) -> None:
    first = resolve(declaration, registry)
    extra = copy.deepcopy(_row(registry, "official.example.scope"))
    extra["criterion_id"] = "official.other.scope"
    extra["applicability"]["venues"] = ["Other Journal"]  # type: ignore[index]
    registry["criteria"].append(extra)  # type: ignore[union-attr]
    registry["authority_classes"]["official_venue_type"].append("official.other.scope")  # type: ignore[index]
    second = resolve(declaration, registry)
    assert second["resolved_digest"] == first["resolved_digest"]
    assert second["registry"]["registry_digest"] != first["registry"]["registry_digest"]  # type: ignore[index]


def test_resolved_artifact_is_pointer_only(
    declaration: dict[str, object], registry: dict[str, object]
) -> None:
    context = resolve(declaration, registry)
    encoded = json.dumps(context)
    for row in registry["criteria"]:  # type: ignore[union-attr]
        assert row["statement"] not in encoded  # type: ignore[index]
    assert context["phase1_safe"] is True
    assert context["numeric_weights_applied"] is False
    _validator("review_target_context.schema.json").validate(context)


def test_cli_does_not_read_sibling_manuscript(tmp_path: Path) -> None:
    sentinel = "MANUSCRIPT-SENTINEL-683-DO-NOT-READ"
    context_path = tmp_path / "context.json"
    registry_path = tmp_path / "registry.json"
    manuscript_path = tmp_path / "manuscript.md"
    output_path = tmp_path / "resolved.json"
    brief_path = tmp_path / "brief.md"
    context_path.write_text((FIXTURES / "exact-declaration.json").read_text(), encoding="utf-8")
    registry_path.write_text((FIXTURES / "synthetic-registry.json").read_text(), encoding="utf-8")
    manuscript_path.write_text(sentinel, encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            str(RESOLVER),
            "--context",
            str(context_path),
            "--registry",
            str(registry_path),
            "--output",
            str(output_path),
            "--brief",
            str(brief_path),
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert sentinel not in output_path.read_text(encoding="utf-8")
    assert sentinel not in brief_path.read_text(encoding="utf-8")
    assert manuscript_path.read_text(encoding="utf-8") == sentinel


def test_cli_rejects_duplicate_json_keys(tmp_path: Path, registry: dict[str, object]) -> None:
    declaration_path = tmp_path / "duplicate.json"
    registry_path = tmp_path / "registry.json"
    declaration_path.write_text('{"schema_version":"a","schema_version":"b"}', encoding="utf-8")
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(RESOLVER), "--context", str(declaration_path), "--registry", str(registry_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 2
    assert "duplicate JSON key" in completed.stderr
