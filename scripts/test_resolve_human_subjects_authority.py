#!/usr/bin/env python3
"""Hermetic contract, resolver, and mutation tests for issue #666."""
from __future__ import annotations

import ast
import copy
import hashlib
import json
import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from resolve_human_subjects_authority import (
    ContractError,
    digest,
    evaluate_predicate,
    load_json,
    resolve,
    validate_context,
    validate_registry,
    validate_resolved_context,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "scripts" / "fixtures" / "human_subjects_authority"
CONTRACTS = REPO_ROOT / "shared" / "contracts" / "human_subjects"
REGISTRY_PATH = REPO_ROOT / "shared" / "human_subjects_authority_registry.json"
RESOLVER = REPO_ROOT / "scripts" / "resolve_human_subjects_authority.py"

FIXTURE_NAMES = (
    "us-gdpr-two-axis.json",
    "tw-gdpr-two-axis.json",
    "cross-border-us-tw-gdpr.json",
    "no-profile.json",
    "missing-data-axis.json",
    "gdpr-member-state-unresolved.json",
)


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _fixture(name: str) -> dict[str, Any]:
    return _json(FIXTURES / name)


def _registry() -> dict[str, Any]:
    return _json(REGISTRY_PATH)


def _validator(name: str) -> Draft202012Validator:
    schema = _json(CONTRACTS / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _profile(registry: dict[str, Any], profile_id: str) -> dict[str, Any]:
    return next(row for row in registry["profiles"] if row["profile_id"] == profile_id)


def _requirement(result: dict[str, Any], requirement_id: str) -> dict[str, Any]:
    return next(row for row in result["requirement_results"] if row["requirement_id"] == requirement_id)


def _selection(context: dict[str, Any], profile_id: str) -> dict[str, Any]:
    return next(row for row in context["selected_profiles"] if row["profile_id"] == profile_id)


def _profile_display_ref(context: dict[str, Any], profile_id: str) -> dict[str, Any]:
    return next(
        ref
        for axis in context["display_precedence"]
        for ref in axis["ordered_authorities"]
        if ref["authority_kind"] == "profile" and ref["authority_id"] == profile_id
    )


def _repin_profile(context: dict[str, Any], profile: dict[str, Any]) -> None:
    payload = copy.deepcopy(profile)
    payload.pop("profile_digest")
    profile["profile_digest"] = digest(payload)
    selection = _selection(context, profile["profile_id"])
    selection["profile_digest"] = profile["profile_digest"]
    _profile_display_ref(context, profile["profile_id"])["authority_digest"] = profile[
        "profile_digest"
    ]


def _all_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        return set(value) | set().union(*(_all_keys(item) for item in value.values()), set())
    if isinstance(value, list):
        return set().union(*(_all_keys(item) for item in value), set())
    return set()


def _predicate_facts() -> dict[str, dict[str, Any]]:
    return {
        "flag.true": {
            "fact_id": "flag.true",
            "value_type": "boolean",
            "state": "declared",
            "value": True,
            "provenance": "author_declared",
        },
        "flag.false": {
            "fact_id": "flag.false",
            "value_type": "boolean",
            "state": "declared",
            "value": False,
            "provenance": "author_declared",
        },
        "flag.unknown": {
            "fact_id": "flag.unknown",
            "value_type": "boolean",
            "state": "unknown",
            "value": None,
            "provenance": "author_declared",
        },
        "choice.region": {
            "fact_id": "choice.region",
            "value_type": "string_enum",
            "state": "declared",
            "value": "tw",
            "provenance": "author_declared",
        },
        "set.locations": {
            "fact_id": "set.locations",
            "value_type": "string_set",
            "state": "declared",
            "value": ["de", "tw"],
            "provenance": "author_declared",
        },
    }


def _with_institutional_overlay(
    context: dict[str, Any], registry: dict[str, Any]
) -> dict[str, Any]:
    us = _profile(registry, "us.hhs.45-cfr-46.subpart-a")
    source = {
        "source_id": "synthetic.institution.policy",
        "title": "Synthetic institution participant-information policy",
        "publisher": "Example Institution",
        "canonical_url": "https://example.invalid/institution-policy",
        "snapshot_url": None,
        "provision_locator": "Section 1",
        "allowed_provisions": ["Section 1"],
        "effective_from": "2026-01-01",
        "effective_until": None,
        "source_amended_or_published_date": "2026-01-01",
        "retrieved_at": "2026-08-09",
        "verified_at": "2026-08-09",
        "source_language": "en",
        "controlling_language": True,
        "authenticity_status": "authentic_official",
        "content_digest": None,
        "digest_scope": "not_recorded",
        "rights_status": "curator_summary_only",
        "freshness": "current",
    }
    anchor = {
        "source_id": source["source_id"],
        "authority_url": source["canonical_url"],
        "snapshot_url": source["snapshot_url"],
        "provision": source["provision_locator"],
        "effective_date": source["effective_from"],
        "effective_until": source["effective_until"],
        "source_amended_or_published_date": source["source_amended_or_published_date"],
        "retrieved_at": source["retrieved_at"],
        "verified_at": source["verified_at"],
        "source_language": source["source_language"],
        "controlling_language": source["controlling_language"],
        "authenticity_status": source["authenticity_status"],
        "content_digest": source["content_digest"],
        "digest_scope": source["digest_scope"],
        "rights_status": source["rights_status"],
    }
    overlay = {
        "overlay_id": "synthetic.institution.participant-information",
        "overlay_version": "1.0",
        "overlay_digest": "0" * 64,
        "overlay_kind": "institutional",
        "axis": "review_ethics",
        "issuer": "Example Institution",
        "title": "Synthetic additive participant-information overlay",
        "authority_scope_ids": ["us.common-rule"],
        "target_profiles": [
            {
                "axis": us["axis"],
                "profile_id": us["profile_id"],
                "profile_version": us["profile_version"],
                "profile_digest": us["profile_digest"],
            }
        ],
        "source_ids": [source["source_id"]],
        "operation": "add",
        "requirements_removed": False,
        "requirements": [
            {
                "requirement_id": "synthetic.institution.participant-information",
                "axis": "review_ethics",
                "title": "Additional participant-information item",
                "summary": "Synthetic curator summary for additive-overlay testing.",
                "obligation_kind": "information",
                "obligated_actor": "investigator",
                "consumer_scopes": ["participant_information", "submission_packet"],
                "applies_if": {
                    "op": "fact_equals",
                    "fact_id": "activity.human_subjects",
                    "value": True,
                },
                "structured_expectations": [
                    {"field_id": "participant.notice.synthetic", "operator": "present", "value": True}
                ],
                "evidence_expected": [
                    {
                        "evidence_id": "synthetic.notice",
                        "held_by": "investigator",
                        "artifact_type": "participant_information_sheet",
                        "description": "Synthetic participant-information artifact.",
                    }
                ],
                "waiver_or_exception_route": {
                    "state": "external_authority_required",
                    "requirement_ids": [],
                    "decision_maker_role": "institutional_review_office",
                },
                "authoritative_decision_maker": {
                    "role_id": "institutional_review_office",
                    "description": "The institutionally authorized review office.",
                },
                "interaction": {
                    "collision_key": "participant.information",
                    "policy": "parallel_authorities",
                },
                "authority_anchor": anchor,
            }
        ],
    }
    unsigned = copy.deepcopy(overlay)
    unsigned.pop("overlay_digest")
    overlay["overlay_digest"] = digest(unsigned)
    registry["sources"].append(source)
    registry["overlays"].append(overlay)
    context["overlay_selection_state"]["institutional"] = "selected"
    context["selected_overlays"].append(
        {
            "overlay_kind": overlay["overlay_kind"],
            "axis": overlay["axis"],
            "overlay_id": overlay["overlay_id"],
            "overlay_version": overlay["overlay_version"],
            "overlay_digest": overlay["overlay_digest"],
        }
    )
    review_order = next(
        row for row in context["display_precedence"] if row["axis"] == "review_ethics"
    )["ordered_authorities"]
    review_order.append(
        {
            "authority_kind": "institutional_overlay",
            "axis": overlay["axis"],
            "authority_id": overlay["overlay_id"],
            "authority_version": overlay["overlay_version"],
            "authority_digest": overlay["overlay_digest"],
        }
    )
    return overlay


def _repin_overlay(context: dict[str, Any], overlay: dict[str, Any]) -> None:
    unsigned = copy.deepcopy(overlay)
    unsigned.pop("overlay_digest")
    overlay["overlay_digest"] = digest(unsigned)
    selection = next(
        row for row in context["selected_overlays"] if row["overlay_id"] == overlay["overlay_id"]
    )
    selection["overlay_digest"] = overlay["overlay_digest"]
    display = next(
        ref
        for axis in context["display_precedence"]
        for ref in axis["ordered_authorities"]
        if ref["authority_kind"] == "institutional_overlay"
        and ref["authority_id"] == overlay["overlay_id"]
    )
    display["authority_digest"] = overlay["overlay_digest"]


def _repin_resolved(result: dict[str, Any]) -> None:
    result.pop("resolved_digest", None)
    result["resolved_digest"] = digest(result)


@pytest.fixture
def us_context() -> dict[str, Any]:
    return _fixture("us-gdpr-two-axis.json")


@pytest.fixture
def live_registry() -> dict[str, Any]:
    return _registry()


def test_all_three_schemas_are_valid_draft_2020_12() -> None:
    for name in (
        "irb_context_record.schema.json",
        "authority_profile_registry.schema.json",
        "resolved_authority_context.schema.json",
    ):
        Draft202012Validator.check_schema(_json(CONTRACTS / name))


def test_all_context_fixtures_validate_against_closed_schema() -> None:
    for name in FIXTURE_NAMES:
        context = _fixture(name)
        _validator("irb_context_record.schema.json").validate(context)
        validate_context(context, _registry())


def test_live_registry_validates_and_profile_digests_are_exact() -> None:
    registry = _registry()
    _validator("authority_profile_registry.schema.json").validate(registry)
    validate_registry(registry)
    for profile in registry["profiles"]:
        payload = copy.deepcopy(profile)
        expected = payload.pop("profile_digest")
        assert digest(payload) == expected


def test_live_authority_dates_and_taiwan_controlling_fields_are_pinned() -> None:
    registry = _registry()
    sources = {row["source_id"]: row for row in registry["sources"]}
    for source_id in ("us.ecfr.45-cfr-46.107", "us.ecfr.45-cfr-46.116"):
        assert sources[source_id]["effective_from"] == "2018-07-19"
        assert sources[source_id]["source_amended_or_published_date"] == "2017-01-19"
    for source_id in ("tw.moj.hsra.article-7.zh-hant", "tw.moj.hsra.article-14.zh-hant"):
        assert sources[source_id]["effective_from"] == "2011-12-28"
        assert sources[source_id]["source_amended_or_published_date"] == "2019-01-02"
        assert sources[source_id]["controlling_language"] is True

    profile = _profile(registry, "tw.mohw.human-subjects-research-act")
    expectations = {
        row["requirement_id"]: {
            item["field_id"] for item in row["structured_expectations"]
        }
        for row in profile["requirements"]
    }
    committee = expectations["tw.hsra.article-7.committee-composition"]
    assert "committee.includes_legal_expert" in committee
    assert "committee.includes_other_socially_impartial_member" in committee
    assert "committee.includes_legal_expert_or_community_representative" not in committee
    consent = expectations["tw.hsra.article-14.consent-information"]
    assert "consent.research_contact_name_and_contact_information" in consent
    assert "consent.other_required_research_information" not in consent


@pytest.mark.parametrize(
    ("fixture_name", "review_profile_id"),
    [
        ("us-gdpr-two-axis.json", "us.hhs.45-cfr-46.subpart-a"),
        ("tw-gdpr-two-axis.json", "tw.mohw.human-subjects-research-act"),
    ],
)
def test_structurally_distinct_review_profiles_resolve_through_same_schema(
    fixture_name: str, review_profile_id: str
) -> None:
    result = resolve(_fixture(fixture_name), _registry())
    _validator("resolved_authority_context.schema.json").validate(result)
    assert result["resolution_state"] == "resolved"
    assert {row["axis"] for row in result["selected_profiles"]} == {
        "review_ethics",
        "data_protection",
    }
    assert review_profile_id in {row["profile_id"] for row in result["selected_profiles"]}
    assert result["downstream_gate"]["profile_dependent_result_allowed"] is True


def test_data_protection_operates_simultaneously_with_review_ethics() -> None:
    result = resolve(_fixture("us-gdpr-two-axis.json"), _registry())
    by_axis = {
        axis: {row["requirement_id"] for row in result["requirement_results"] if row["axis"] == axis}
        for axis in ("review_ethics", "data_protection")
    }
    assert by_axis["review_ethics"]
    assert by_axis["data_protection"] >= {
        "eu.gdpr.article-6.lawful-basis",
        "eu.gdpr.article-89.1.research-safeguards",
    }


def test_cross_border_profiles_remain_parallel_and_preserve_collisions() -> None:
    result = resolve(_fixture("cross-border-us-tw-gdpr.json"), _registry())
    assert len(result["selected_profiles"]) == 3
    collisions = {row["collision_key"]: row for row in result["collisions"]}
    assert set(collisions["committee.composition"]["requirement_ids"]) == {
        "us.45cfr46.107.irb-composition",
        "tw.hsra.article-7.committee-composition",
    }
    assert {
        "us.45cfr46.116.informed-consent",
        "tw.hsra.article-14.consent-information",
        "eu.gdpr.article-13.direct-collection-information",
        "eu.gdpr.article-14.indirect-collection-information",
    } <= set(collisions["participant.information"]["requirement_ids"])
    assert all(row["requirements_removed"] is False for row in result["collisions"])


@pytest.mark.parametrize("name", ["no-profile.json", "missing-data-axis.json"])
def test_missing_profile_axis_cannot_enable_downstream_results(name: str) -> None:
    result = resolve(_fixture(name), _registry())
    assert result["resolution_state"] == "jurisdiction_unresolved"
    assert result["downstream_gate"]["both_axes_selected"] is False
    assert result["downstream_gate"]["profile_dependent_result_allowed"] is False
    assert any(row["code"] == "JURISDICTION_UNRESOLVED" for row in result["unresolved_reasons"])


def test_unknown_member_state_fact_remains_unresolved() -> None:
    result = resolve(_fixture("gdpr-member-state-unresolved.json"), _registry())
    row = _requirement(result, "eu.gdpr.article-89.2.member-state-derogation")
    assert row["applicability"] == "unknown"
    assert result["resolution_state"] == "applicability_unresolved"
    assert result["downstream_gate"]["all_applicability_resolved"] is False
    assert result["downstream_gate"]["profile_dependent_result_allowed"] is False


def test_every_exact_profile_pin_is_load_bearing() -> None:
    mutations = [
        ("axis", "data_protection"),
        ("profile_id", "unknown.profile"),
        ("profile_version", "2099-01-01"),
        ("profile_digest", "0" * 64),
        ("authority_scope_ids", ["unknown.scope"]),
    ]
    for field, value in mutations:
        context = _fixture("us-gdpr-two-axis.json")
        context["selected_profiles"][0][field] = value
        with pytest.raises(ContractError):
            resolve(context, _registry())


def test_selected_state_without_axis_row_is_rejected_by_schema(
    us_context: dict[str, Any],
) -> None:
    us_context["selected_profiles"] = [us_context["selected_profiles"][0]]
    assert list(_validator("irb_context_record.schema.json").iter_errors(us_context))


def test_funder_is_not_a_third_axis(us_context: dict[str, Any]) -> None:
    us_context["selected_profiles"][0]["axis"] = "funder"
    assert list(_validator("irb_context_record.schema.json").iter_errors(us_context))


@pytest.mark.parametrize("kind", ["duplicate_fact", "duplicate_profile"])
def test_semantic_duplicate_identifiers_are_rejected(
    kind: str, us_context: dict[str, Any], live_registry: dict[str, Any]
) -> None:
    if kind == "duplicate_fact":
        duplicate = copy.deepcopy(us_context["declared_facts"][0])
        duplicate["value"] = False
        us_context["declared_facts"].append(duplicate)
    else:
        duplicate = copy.deepcopy(us_context["selected_profiles"][0])
        duplicate["authority_scope_ids"] = ["us.common-rule", "extra.scope"]
        us_context["selected_profiles"].append(duplicate)
    with pytest.raises(ContractError):
        validate_context(us_context, live_registry)


def test_jurisdiction_hints_never_trigger_default_selection() -> None:
    context = _fixture("no-profile.json")
    result = resolve(context, _registry())
    assert context["scope_dimensions"]["review_jurisdictions"]
    assert context["scope_dimensions"]["data_protection_regimes"]
    assert result["selected_profiles"] == []
    assert result["requirement_results"] == []


@pytest.mark.parametrize(
    ("predicate", "expected"),
    [
        ({"op": "fact_equals", "fact_id": "flag.true", "value": True}, "true"),
        ({"op": "fact_equals", "fact_id": "flag.true", "value": False}, "false"),
        ({"op": "fact_equals", "fact_id": "flag.missing", "value": True}, "unknown"),
        ({"op": "fact_in", "fact_id": "choice.region", "values": ["tw", "us"]}, "true"),
        ({"op": "fact_contains", "fact_id": "set.locations", "value": "de"}, "true"),
        (
            {"op": "not", "operand": {"op": "fact_equals", "fact_id": "flag.unknown", "value": True}},
            "unknown",
        ),
        (
            {
                "op": "all",
                "operands": [
                    {"op": "fact_equals", "fact_id": "flag.false", "value": True},
                    {"op": "fact_equals", "fact_id": "flag.unknown", "value": True},
                ],
            },
            "false",
        ),
        (
            {
                "op": "all",
                "operands": [
                    {"op": "fact_equals", "fact_id": "flag.true", "value": True},
                    {"op": "fact_equals", "fact_id": "flag.unknown", "value": True},
                ],
            },
            "unknown",
        ),
        (
            {
                "op": "any",
                "operands": [
                    {"op": "fact_equals", "fact_id": "flag.true", "value": True},
                    {"op": "fact_equals", "fact_id": "flag.unknown", "value": True},
                ],
            },
            "true",
        ),
        (
            {
                "op": "any",
                "operands": [
                    {"op": "fact_equals", "fact_id": "flag.false", "value": True},
                    {"op": "fact_equals", "fact_id": "flag.unknown", "value": True},
                ],
            },
            "unknown",
        ),
    ],
)
def test_closed_predicate_ast_uses_strong_kleene_three_valued_logic(
    predicate: dict[str, Any], expected: str
) -> None:
    result, trace = evaluate_predicate(predicate, _predicate_facts())
    assert result == expected
    assert trace
    assert trace[0]["expression_path"].startswith("/")
    assert {row["result"] for row in trace} <= {"true", "false", "unknown"}


def test_unselected_overlay_is_never_applied_implicitly(
    us_context: dict[str, Any], live_registry: dict[str, Any]
) -> None:
    overlay_context = copy.deepcopy(us_context)
    overlay = _with_institutional_overlay(overlay_context, live_registry)
    result = resolve(us_context, live_registry)
    assert result["selected_overlays"] == []
    assert overlay["requirements"][0]["requirement_id"] not in {
        row["requirement_id"] for row in result["requirement_results"]
    }


def test_overlay_is_additive_and_collision_rows_are_preserved(
    us_context: dict[str, Any], live_registry: dict[str, Any]
) -> None:
    overlay = _with_institutional_overlay(us_context, live_registry)
    validate_registry(live_registry)
    result = resolve(us_context, live_registry)
    assert result["selected_overlays"] == [
        {
            "overlay_kind": "institutional",
            "axis": "review_ethics",
            "overlay_id": overlay["overlay_id"],
            "overlay_version": overlay["overlay_version"],
            "overlay_digest": overlay["overlay_digest"],
            "overlay_pointer": "/overlays/0",
            "target_profile_ids": ["us.hhs.45-cfr-46.subpart-a"],
            "requirements_removed": False,
        }
    ]
    requirement_ids = {row["requirement_id"] for row in result["requirement_results"]}
    assert {row["requirement_id"] for row in _profile(live_registry, "us.hhs.45-cfr-46.subpart-a")["requirements"]} <= requirement_ids
    assert overlay["requirements"][0]["requirement_id"] in requirement_ids
    collision = next(row for row in result["collisions"] if row["collision_key"] == "participant.information")
    assert overlay["requirements"][0]["requirement_id"] in collision["requirement_ids"]
    assert collision["requirements_removed"] is False


def test_wrong_target_overlay_fails_closed(
    us_context: dict[str, Any], live_registry: dict[str, Any]
) -> None:
    overlay = _with_institutional_overlay(us_context, live_registry)
    tw = _profile(live_registry, "tw.mohw.human-subjects-research-act")
    overlay["target_profiles"] = [
        {
            "axis": tw["axis"],
            "profile_id": tw["profile_id"],
            "profile_version": tw["profile_version"],
            "profile_digest": tw["profile_digest"],
        }
    ]
    _repin_overlay(us_context, overlay)
    with pytest.raises(ContractError):
        resolve(us_context, live_registry)


def test_multi_target_overlay_requires_every_exact_base_target(
    us_context: dict[str, Any], live_registry: dict[str, Any]
) -> None:
    overlay = _with_institutional_overlay(us_context, live_registry)
    tw = _profile(live_registry, "tw.mohw.human-subjects-research-act")
    overlay["target_profiles"].append(
        {
            "axis": tw["axis"],
            "profile_id": tw["profile_id"],
            "profile_version": tw["profile_version"],
            "profile_digest": tw["profile_digest"],
        }
    )
    _repin_overlay(us_context, overlay)
    _validator("authority_profile_registry.schema.json").validate(live_registry)
    validate_registry(live_registry)
    with pytest.raises(ContractError, match="every exact base target selected"):
        resolve(us_context, live_registry)


def test_overlay_cannot_fill_a_missing_base_axis(live_registry: dict[str, Any]) -> None:
    context = _fixture("missing-data-axis.json")
    _with_institutional_overlay(context, live_registry)
    result = resolve(context, live_registry)
    assert result["downstream_gate"]["both_axes_selected"] is False
    assert result["downstream_gate"]["profile_dependent_result_allowed"] is False


def test_overlay_requirement_inherits_unknown_or_false_base_applicability() -> None:
    cases = (("unknown", None, "unknown"), ("declared", False, "false"))
    for state, value, expected in cases:
        context = _fixture("us-gdpr-two-axis.json")
        registry = _registry()
        overlay = _with_institutional_overlay(context, registry)
        support = next(
            row
            for row in context["declared_facts"]
            if row["fact_id"] == "support.us_hhs_or_common_rule"
        )
        support["state"] = state
        support["value"] = value
        result = resolve(context, registry)
        overlay_requirement = _requirement(
            result, "synthetic.institution.participant-information"
        )
        assert overlay_requirement["applicability"] == expected
        assert any(
            row["code"] == "OVERLAY_BASE_UNRESOLVED"
            and row["authority_id"] == overlay["overlay_id"]
            for row in result["unresolved_reasons"]
        )


def test_display_precedence_changes_only_trace_order_and_digest(
    us_context: dict[str, Any], live_registry: dict[str, Any]
) -> None:
    _with_institutional_overlay(us_context, live_registry)
    first = resolve(us_context, live_registry)
    reordered = copy.deepcopy(us_context)
    review = next(row for row in reordered["display_precedence"] if row["axis"] == "review_ethics")
    review["ordered_authorities"].reverse()
    second = resolve(reordered, live_registry)
    assert {row["requirement_id"] for row in first["requirement_results"]} == {
        row["requirement_id"] for row in second["requirement_results"]
    }
    assert first["collisions"] == second["collisions"]
    assert first["downstream_gate"] == second["downstream_gate"]
    assert first["trace_order"] != second["trace_order"]
    assert first["resolved_digest"] != second["resolved_digest"]


def test_noncurrent_or_noncontrolling_authority_source_blocks_gate() -> None:
    mutations = [
        ("freshness", "stale"),
        ("freshness", "unverified"),
        ("freshness", "superseded"),
        ("future", "2027-01-01"),
        ("expired", "2026-01-01"),
        ("noncontrolling", False),
    ]
    for mutation, value in mutations:
        context = _fixture("us-gdpr-two-axis.json")
        registry = _registry()
        source_id = "us.ecfr.45-cfr-46.107"
        source = next(row for row in registry["sources"] if row["source_id"] == source_id)
        profile = _profile(registry, "us.hhs.45-cfr-46.subpart-a")
        anchors = [
            row["authority_anchor"]
            for row in profile["requirements"]
            if row["authority_anchor"]["source_id"] == source_id
        ]
        if mutation == "freshness":
            source["freshness"] = value
        elif mutation == "future":
            source["effective_from"] = value
            for anchor in anchors:
                anchor["effective_date"] = value
            _repin_profile(context, profile)
        elif mutation == "expired":
            source["effective_until"] = value
            for anchor in anchors:
                anchor["effective_until"] = value
            _repin_profile(context, profile)
        else:
            source["controlling_language"] = False
            source["authenticity_status"] = "official_reference_translation"
            for anchor in anchors:
                anchor["controlling_language"] = False
                anchor["authenticity_status"] = "official_reference_translation"
            _repin_profile(context, profile)
        result = resolve(context, registry)
        selected = next(
            row
            for row in result["selected_profiles"]
            if row["profile_id"] == profile["profile_id"]
        )
        assert selected["source_state"] == "unresolved", mutation
        assert result["resolution_state"] == "applicability_unresolved", mutation
        assert result["downstream_gate"]["profile_dependent_result_allowed"] is False
        assert any(
            row["code"] == "AUTHORITY_SOURCE_NOT_CURRENT"
            and row["authority_id"] == profile["profile_id"]
            for row in result["unresolved_reasons"]
        ), mutation


def test_requirement_authority_anchor_fields_are_mandatory() -> None:
    for field in ("authority_url", "provision", "effective_date"):
        registry = _registry()
        profile = _profile(registry, "us.hhs.45-cfr-46.subpart-a")
        profile["requirements"][0]["authority_anchor"].pop(field)
        assert list(_validator("authority_profile_registry.schema.json").iter_errors(registry)), field


def test_anchor_effective_date_cannot_be_replaced_by_amendment_date() -> None:
    context = _fixture("tw-gdpr-two-axis.json")
    registry = _registry()
    profile = _profile(registry, "tw.mohw.human-subjects-research-act")
    requirement = next(
        row
        for row in profile["requirements"]
        if row["requirement_id"] == "tw.hsra.article-14.consent-information"
    )
    requirement["authority_anchor"]["effective_date"] = "2019-01-02"
    _repin_profile(context, profile)
    _validator("authority_profile_registry.schema.json").validate(registry)
    with pytest.raises(ContractError, match="verified effective_from"):
        resolve(context, registry)


def test_anchor_provision_must_be_in_source_allowed_provisions() -> None:
    context = _fixture("tw-gdpr-two-axis.json")
    registry = _registry()
    profile = _profile(registry, "tw.mohw.human-subjects-research-act")
    profile["requirements"][0]["authority_anchor"]["provision"] = "人體研究法第 999 條"
    _repin_profile(context, profile)
    _validator("authority_profile_registry.schema.json").validate(registry)
    with pytest.raises(ContractError, match="allowed provision"):
        resolve(context, registry)


def test_profile_must_declare_every_requirement_anchor_source() -> None:
    context = _fixture("us-gdpr-two-axis.json")
    registry = _registry()
    profile = _profile(registry, "us.hhs.45-cfr-46.subpart-a")
    anchor_source = profile["requirements"][0]["authority_anchor"]["source_id"]
    profile["source_ids"].remove(anchor_source)
    _repin_profile(context, profile)
    _validator("authority_profile_registry.schema.json").validate(registry)
    with pytest.raises(ContractError, match="declared by its profile or overlay source_ids"):
        resolve(context, registry)


def test_resolver_contains_no_jurisdiction_specific_profile_branch() -> None:
    source = RESOLVER.read_text(encoding="utf-8")
    for profile_id in (
        "us.hhs.45-cfr-46.subpart-a",
        "tw.mohw.human-subjects-research-act",
        "eu.gdpr.research-core-bounded",
    ):
        assert profile_id not in source


def test_resolved_artifact_is_pointer_only_and_complete() -> None:
    registry = _registry()
    context = _fixture("us-gdpr-two-axis.json")
    result = resolve(context, registry)
    encoded = json.dumps(result, ensure_ascii=False, sort_keys=True)
    for profile_id in {row["profile_id"] for row in context["selected_profiles"]}:
        profile = _profile(registry, profile_id)
        assert profile["title"] not in encoded
        for requirement in profile["requirements"]:
            assert requirement["summary"] not in encoded
    expected = {
        row["requirement_id"]
        for profile in registry["profiles"]
        if profile["profile_id"] in {row["profile_id"] for row in context["selected_profiles"]}
        for row in profile["requirements"]
    }
    assert {row["requirement_id"] for row in result["requirement_results"]} == expected
    assert len(result["trace_order"]) == len(expected)


def test_resolved_output_round_trips_and_self_digest_is_exact() -> None:
    context = _fixture("us-gdpr-two-axis.json")
    registry = _registry()
    output = resolve(context, registry)
    validate_resolved_context(output, context, registry)
    unsigned = copy.deepcopy(output)
    claimed = unsigned.pop("resolved_digest")
    assert claimed == digest(unsigned)


def test_resolved_validator_rejects_rebound_structural_and_semantic_mutations() -> None:
    mutations = (
        lambda output: output["selected_profiles"][0].pop("axis"),
        lambda output: output["requirement_results"][0].__setitem__("applicability", "unknown"),
        lambda output: output["requirement_results"][0].__setitem__(
            "requirement_pointer", "/profiles/999/requirements/0"
        ),
        lambda output: output["requirement_results"][0].__setitem__(
            "requirement_digest", "0" * 64
        ),
        lambda output: output["requirement_results"][0].__setitem__(
            "detail", "injected legal conclusion"
        ),
        lambda output: output["requirement_results"][0].__setitem__(
            "summary", "injected profile prose"
        ),
    )
    context = _fixture("us-gdpr-two-axis.json")
    registry = _registry()
    for mutate in mutations:
        output = resolve(context, registry)
        mutate(output)
        _repin_resolved(output)
        with pytest.raises(ContractError):
            validate_resolved_context(output, context, registry)


def test_resolved_artifact_has_no_verdict_or_authorization_fields() -> None:
    keys = _all_keys(resolve(_fixture("us-gdpr-two-axis.json"), _registry()))
    forbidden = {
        "verdict",
        "review_pathway",
        "submission_readiness",
        "authorization_status",
        "conformance",
    }
    assert forbidden.isdisjoint(keys)


def test_committee_governance_is_not_promoted_to_submission_packet_scope() -> None:
    result = resolve(_fixture("cross-border-us-tw-gdpr.json"), _registry())
    for requirement_id in (
        "us.45cfr46.107.irb-composition",
        "tw.hsra.article-7.committee-composition",
    ):
        row = _requirement(result, requirement_id)
        assert "committee_governance" in row["consumer_scopes"]
        assert "submission_packet" not in row["consumer_scopes"]


def test_key_order_selection_order_and_reconfirmation_do_not_change_digest() -> None:
    context = _fixture("cross-border-us-tw-gdpr.json")
    registry = _registry()
    first = resolve(context, registry)["resolved_digest"]
    reordered = json.loads(json.dumps(context, ensure_ascii=False, sort_keys=True))
    reordered["selected_profiles"].reverse()
    reordered["confirmed_at"] = "2026-08-09T12:34:56+08:00"
    assert resolve(reordered, json.loads(json.dumps(registry, sort_keys=True)))["resolved_digest"] == first


def test_string_set_value_order_does_not_change_context_or_resolved_digest() -> None:
    context = _fixture("us-gdpr-two-axis.json")
    registry = _registry()
    registry["fact_definitions"].append(
            {
                "fact_id": "synthetic.processing_locations",
                "value_type": "string_set",
                "allowed_values": None,
                "description": "Synthetic unordered processing-location set for digest testing.",
            }
    )
    context["declared_facts"].append(
        {
            "fact_id": "synthetic.processing_locations",
            "value_type": "string_set",
            "state": "declared",
            "value": ["de", "tw"],
            "provenance": "author_declared",
        }
    )
    first = resolve(context, registry)
    reordered = copy.deepcopy(context)
    next(
        row
        for row in reordered["declared_facts"]
        if row["fact_id"] == "synthetic.processing_locations"
    )["value"].reverse()
    second = resolve(reordered, registry)
    assert second["context_pointer"]["context_digest"] == first["context_pointer"]["context_digest"]
    assert second["resolved_digest"] == first["resolved_digest"]


def test_substantive_mutations_change_resolved_digest() -> None:
    for mutation in ("fact", "profile_version", "source_state"):
        context = _fixture("us-gdpr-two-axis.json")
        registry = _registry()
        first = resolve(context, registry)["resolved_digest"]
        if mutation == "fact":
            fact = next(
                row
                for row in context["declared_facts"]
                if row["fact_id"] == "data.special_category"
            )
            fact["value"] = True
        elif mutation == "profile_version":
            profile = _profile(registry, "us.hhs.45-cfr-46.subpart-a")
            profile["profile_version"] = "2019-01-21-repack"
            _selection(context, profile["profile_id"])["profile_version"] = profile[
                "profile_version"
            ]
            _profile_display_ref(context, profile["profile_id"])["authority_version"] = profile[
                "profile_version"
            ]
            _repin_profile(context, profile)
        else:
            source = next(
                row
                for row in registry["sources"]
                if row["source_id"] == "us.ecfr.45-cfr-46.107"
            )
            source["freshness"] = "stale"
        assert resolve(context, registry)["resolved_digest"] != first, mutation


def test_strict_json_loader_rejects_duplicate_keys_and_nonfinite_numbers(tmp_path: Path) -> None:
    path = tmp_path / "invalid.json"
    for raw in (
        '{"schema_version":"a","schema_version":"b"}',
        '{"outer":{"fact_id":"a","fact_id":"b"}}',
        '{"value":NaN}',
        '{"value":Infinity}',
    ):
        path.write_text(raw, encoding="utf-8")
        with pytest.raises(ContractError):
            load_json(path)


def test_registry_semantic_ids_are_unique() -> None:
    for kind in ("fact", "source", "profile", "requirement"):
        registry = _registry()
        if kind == "fact":
            registry["fact_definitions"].append(copy.deepcopy(registry["fact_definitions"][0]))
        elif kind == "source":
            registry["sources"].append(copy.deepcopy(registry["sources"][0]))
        elif kind == "profile":
            registry["profiles"].append(copy.deepcopy(registry["profiles"][0]))
        else:
            duplicate = copy.deepcopy(registry["profiles"][0]["requirements"][0])
            registry["profiles"][1]["requirements"].append(duplicate)
            _repin_profile(_fixture("tw-gdpr-two-axis.json"), registry["profiles"][1])
        with pytest.raises(ContractError):
            validate_registry(registry)


def test_registry_rejects_executable_or_unknown_predicate_shape() -> None:
    registry = _registry()
    registry["profiles"][0]["applies_if"] = {"op": "eval", "code": "open('/etc/passwd')"}
    assert list(_validator("authority_profile_registry.schema.json").iter_errors(registry))


def test_registry_rejects_predicate_fact_type_mismatch() -> None:
    registry = _registry()
    registry["profiles"][0]["applies_if"] = {
        "op": "fact_contains",
        "fact_id": "activity.human_subjects",
        "value": "true",
    }
    payload = copy.deepcopy(registry["profiles"][0])
    payload.pop("profile_digest")
    registry["profiles"][0]["profile_digest"] = digest(payload)
    with pytest.raises(ContractError):
        validate_registry(registry)


def test_predicate_operator_types_and_real_iso_dates_fail_closed() -> None:
    cases = (
        (
            {
                "fact_id": "synthetic.set",
                "value_type": "string_set",
                "allowed_values": ["russia", "us"],
                "description": "Synthetic set-valued fact.",
            },
            {"op": "fact_equals", "fact_id": "synthetic.set", "value": "us"},
            ["russia"],
        ),
        (
            {
                "fact_id": "synthetic.text",
                "value_type": "string",
                "allowed_values": None,
                "description": "Synthetic scalar text fact.",
            },
            {"op": "fact_contains", "fact_id": "synthetic.text", "value": "us"},
            "russia",
        ),
        (
            {
                "fact_id": "synthetic.date",
                "value_type": "date",
                "allowed_values": None,
                "description": "Synthetic date fact.",
            },
            {"op": "fact_equals", "fact_id": "synthetic.date", "value": "2026-02-30"},
            "2026-02-28",
        ),
    )
    for definition, predicate, actual in cases:
        fact = {
            "fact_id": definition["fact_id"],
            "value_type": definition["value_type"],
            "state": "declared",
            "value": actual,
            "provenance": "author_declared",
        }
        with pytest.raises(ContractError):
            evaluate_predicate(
                predicate,
                {definition["fact_id"]: fact},
                {definition["fact_id"]: definition},
            )
        context = _fixture("us-gdpr-two-axis.json")
        registry = _registry()
        registry["fact_definitions"].append(definition)
        profile = _profile(registry, "us.hhs.45-cfr-46.subpart-a")
        profile["applies_if"] = predicate
        _repin_profile(context, profile)
        _validator("authority_profile_registry.schema.json").validate(registry)
        with pytest.raises(ContractError):
            resolve(context, registry)


def test_resolver_imports_no_network_or_model_client() -> None:
    tree = ast.parse(RESOLVER.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported.isdisjoint(
        {"socket", "urllib", "http", "requests", "httpx", "openai", "anthropic", "subprocess"}
    )


def test_resolver_has_no_eval_exec_or_directory_scan() -> None:
    tree = ast.parse(RESOLVER.read_text(encoding="utf-8"))
    forbidden_names = {"eval", "exec"}
    forbidden_attributes = {"glob", "rglob", "iterdir", "walk"}
    assert not any(
        isinstance(node, ast.Call)
        and (
            isinstance(node.func, ast.Name)
            and node.func.id in forbidden_names
            or isinstance(node.func, ast.Attribute)
            and node.func.attr in forbidden_attributes
        )
        for node in ast.walk(tree)
    )


def test_in_process_resolution_does_not_open_a_socket(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_connect(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("resolver attempted network access")

    monkeypatch.setattr(socket.socket, "connect", fail_connect)
    assert resolve(_fixture("us-gdpr-two-axis.json"), _registry())["resolution_state"] == "resolved"


def test_cli_lints_registry_and_resolves_context(tmp_path: Path) -> None:
    linted = subprocess.run(
        [sys.executable, str(RESOLVER), "--registry", str(REGISTRY_PATH), "--check-registry"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert linted.returncode == 0, linted.stderr
    output = tmp_path / "resolved.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RESOLVER),
            "--context",
            str(FIXTURES / "us-gdpr-two-axis.json"),
            "--registry",
            str(REGISTRY_PATH),
            "--output",
            str(output),
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    _validator("resolved_authority_context.schema.json").validate(_json(output))
    checked = subprocess.run(
        [
            sys.executable,
            str(RESOLVER),
            "--context",
            str(FIXTURES / "us-gdpr-two-axis.json"),
            "--registry",
            str(REGISTRY_PATH),
            "--check-resolved",
            str(output),
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert checked.returncode == 0, checked.stderr


def test_cli_fails_closed_on_duplicate_keys_and_nonfinite_json(tmp_path: Path) -> None:
    context_path = tmp_path / "context.json"
    registry_path = tmp_path / "registry.json"
    mutations = (
        ("context", '{"schema_version":"a","schema_version":"b"}'),
        ("context", '{"schema_version":"irb-context-record/1.0","x":NaN}'),
        ("registry", '{"schema_version":"a","schema_version":"b"}'),
        ("registry", '{"schema_version":"human-subjects-authority-registry/1.0","x":Infinity}'),
    )
    for target, raw in mutations:
        context_path.write_text(
            (FIXTURES / "us-gdpr-two-axis.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        registry_path.write_text(REGISTRY_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        (context_path if target == "context" else registry_path).write_text(raw, encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                str(RESOLVER),
                "--context",
                str(context_path),
                "--registry",
                str(registry_path),
            ],
            cwd=tmp_path,
            text=True,
            capture_output=True,
            check=False,
        )
        assert completed.returncode == 2, target
        assert "duplicate JSON key" in completed.stderr or "non-finite" in completed.stderr


def test_cli_reads_only_named_inputs_not_sibling_manuscript(tmp_path: Path) -> None:
    sentinel = "MANUSCRIPT-SENTINEL-666-DO-NOT-READ"
    context_path = tmp_path / "context-us-jurisdiction.json"
    registry_path = tmp_path / "registry.json"
    output_path = tmp_path / "resolved.json"
    manuscript_path = tmp_path / "manuscript.md"
    context_path.write_text(
        (FIXTURES / "no-profile.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    registry_path.write_text(REGISTRY_PATH.read_text(encoding="utf-8"), encoding="utf-8")
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
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "LANG": "en_US.UTF-8", "TZ": "America/New_York"},
    )
    assert completed.returncode == 0, completed.stderr
    encoded = output_path.read_text(encoding="utf-8")
    assert sentinel not in encoded
    assert manuscript_path.read_text(encoding="utf-8") == sentinel
    result = json.loads(encoded)
    assert result["selected_profiles"] == []
    assert result["downstream_gate"]["profile_dependent_result_allowed"] is False


def test_665_and_668_adjacent_contract_bytes_remain_pinned() -> None:
    expected = {
        "scripts/check_human_subjects_output_contract.py":
            "f14afef8571915c5e66897b06ff5166add4f72f23d9c06fcbcf602fd73050c13",
        "shared/contracts/human_subjects/committee_correspondence.schema.json":
            "302ffff93ca62445afa5f2979540aa24cea7875dc81f2ba2b770208e174b2931",
        "scripts/fixtures/committee_correspondence/16fd83f6aec7/concern_tracker.json":
            "efc76a930e8f42e1135258ca6dc80aabe3637fd0b6c535a1429b560d38764630",
    }
    for relative, expected_digest in expected.items():
        path = REPO_ROOT / relative
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_digest
