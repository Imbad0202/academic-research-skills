"""Hermetic conformance and mutation tests for #655 Track A."""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from scripts import build_claim_standing_candidate_ledger as ledger


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "scripts/fixtures/claim_standing_candidate_ledger"
SCHEMAS = ROOT / "shared/contracts/claim_standing"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _plan() -> dict:
    return _load("query_plan.json")


def _retained() -> dict:
    return _load("retrieval_input.json")


def _rehash_plan(plan: dict) -> None:
    claim = plan["claim"]
    claim["claim_sha256"] = ledger.text_digest(claim["claim_text"])
    for query in plan["queries"]:
        query["source_claim_sha256"] = claim["claim_sha256"]
        query["query_sha256"] = ledger.text_digest(query["accepted_query_text"])
    consent = plan["consent"]
    consent["claim_sha256"] = claim["claim_sha256"]
    consent["provider_roster_sha256"] = ledger.digest(plan["provider_roster"])
    consent["caps_sha256"] = ledger.digest(plan["caps"])
    consent["queries_sha256"] = ledger.digest(plan["queries"])
    if plan["schema_version"] == ledger.PLAN_VERSION_1_1:
        consent["stance_plan_sha256"] = (
            ledger.digest(plan["stance_plan"])
            if plan["stance_plan"] is not None
            else None
        )
    consent["consentable_plan_sha256"] = ledger.digest(
        ledger.consentable_plan_projection(plan)
    )
    consent["receipt_sha256"] = ledger.bound_digest(consent, "receipt_sha256")
    plan["plan_sha256"] = ledger.bound_digest(plan, "plan_sha256")


def _authorize_local_export(
    plan: dict, output_path: str = "/operator-named/candidate-ledger.json"
) -> None:
    plan["consent"]["local_persistence"] = "explicit_local_export"
    plan["consent"]["export_boundary"] = ledger.EXPLICIT_LOCAL_EXPORT_BOUNDARY
    plan["consent"]["authorized_output_path"] = output_path
    _rehash_plan(plan)


def _rehash_input(retained: dict, plan: dict | None = None) -> None:
    active_plan = plan if plan is not None else _plan()
    if plan is not None:
        retained["query_plan_sha256"] = active_plan["plan_sha256"]
    hits = {row["raw_hit_id"]: row for row in retained["raw_hits"]}
    for assessment in retained["relevance_assessments"]:
        hit = hits.get(assessment["canonical_raw_hit_id"])
        if hit is None:
            continue
        projection = ledger.relevance_assessment_input_projection(
            active_plan, hit, assessment
        )
        prompt = ledger.render_relevance_prompt(projection)
        assessment["assessment_input_sha256"] = ledger.digest(projection)
        assessment["prompt_utf8"] = prompt
        assessment["prompt_sha256"] = ledger.text_digest(prompt)
    retained["retrieval_input_sha256"] = ledger.bound_digest(
        retained, "retrieval_input_sha256"
    )


def test_all_contracts_are_valid_closed_draft_2020_12_instances() -> None:
    plan, retained = _plan(), _retained()
    result = ledger.build_ledger(plan, retained)
    instances = {
        "query_plan": plan,
        "retrieval_input": retained,
        "candidate_ledger": result,
    }
    for name, instance in instances.items():
        schema = json.loads((SCHEMAS / f"{name}.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(instance)
        assert schema["additionalProperties"] is False
        mutated = copy.deepcopy(instance)
        mutated["undeclared"] = True
        with pytest.raises(ValidationError):
            Draft202012Validator(schema).validate(mutated)


def test_fixture_replays_dedup_selection_failure_and_hash() -> None:
    result = ledger.build_ledger(_plan(), _retained())
    assert result["candidate_ledger_sha256"] == (
        "a68d62a08a508a8a9f8aac62fdf2d7aef978f75ba941ea5e38ab52e9d5102843"
    )
    assert result["counts"]["selected_work_families"] == 1
    assert result["counts"]["attempt_failure_counts"]["service_unavailable"] == 1
    rows = {row["raw_hit_id"]: row for row in result["raw_hits"]}
    assert rows["hit-1"]["terminal_state"] == "selected"
    assert rows["hit-2"]["terminal_state"] == "duplicate_version"
    assert rows["hit-2"]["retained_raw_hit_id"] == "hit-1"
    assert rows["hit-3"]["terminal_state"] == "not_relevant"


def test_build_is_deterministic_and_does_not_mutate_inputs() -> None:
    plan, retained = _plan(), _retained()
    frozen = copy.deepcopy((plan, retained))
    assert ledger.build_ledger(plan, retained) == ledger.build_ledger(plan, retained)
    assert (plan, retained) == frozen


@pytest.mark.parametrize(
    "persistence", ["session_only", "explicit_local_export"]
)
def test_finalized_ledger_truthfully_carries_consent_persistence(
    persistence: str,
) -> None:
    plan = _plan()
    if persistence == "explicit_local_export":
        _authorize_local_export(plan)
    else:
        _rehash_plan(plan)
    retained = _retained()
    _rehash_input(retained, plan)
    result = ledger.build_ledger(plan, retained)
    assert result["local_persistence"] == persistence
    assert result["export_boundary"] == plan["consent"]["export_boundary"]
    assert result["authorized_output_path"] == plan["consent"].get(
        "authorized_output_path"
    )
    assert {row["sharing_scope"] for row in result["work_families"]} == {
        persistence
    }
    assert {row["rights_basis"] for row in result["work_families"]} == {
        "not_assessed"
    }


def test_explicit_local_export_requires_exact_bound_consent_language() -> None:
    plan = _plan()
    plan["consent"]["local_persistence"] = "explicit_local_export"
    plan["consent"]["export_boundary"] = "No export is authorized."
    plan["consent"]["authorized_output_path"] = "/tmp/ledger.json"
    _rehash_plan(plan)
    with pytest.raises(ledger.LedgerError, match="export_boundary"):
        ledger.validate_plan(plan)
    retained = _retained()
    _rehash_input(retained, plan)
    with pytest.raises(ledger.LedgerError, match="query plan schema violation"):
        ledger.build_ledger(plan, retained)


def test_explicit_local_export_rejects_relative_authorized_path() -> None:
    plan = _plan()
    _authorize_local_export(plan, "ledger.json")
    with pytest.raises(ledger.LedgerError, match="absolute path"):
        ledger.validate_plan(plan)


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({"year": 2019, "language": "fr", "document_type": "thesis"}, "outside_date_range"),
        ({"year": 2024, "language": "fr", "document_type": "thesis"}, "outside_language_set"),
        ({"year": 2024, "language": "en", "document_type": "thesis"}, "outside_document_type"),
        ({"title": None, "provider_record_id": None, "doi": None}, "missing_title_and_stable_id"),
    ],
)
def test_filter_order_is_explicit(changes: dict, expected: str) -> None:
    retained = _retained()
    retained["raw_hits"][2].update(changes)
    retained["relevance_assessments"] = retained["relevance_assessments"][:1]
    _rehash_input(retained)
    result = ledger.build_ledger(_plan(), retained)
    row = next(row for row in result["raw_hits"] if row["raw_hit_id"] == "hit-3")
    assert row["terminal_state"] == expected


def test_published_record_wins_canonical_selection_over_preprint() -> None:
    result = ledger.build_ledger(_plan(), _retained())
    family = next(row for row in result["work_families"] if "hit-2" in row["member_raw_hit_ids"])
    assert family["canonical_raw_hit_id"] == "hit-1"
    assert ledger.normalize_doi("HTTPS://DOI.ORG/10.1000/EXAMPLE") == "10.1000/example"


def test_normalizers_collapse_semantically_empty_identity_values_to_null() -> None:
    assert ledger.normalize_doi("doi:   ") is None
    assert ledger.normalize_title("---") is None
    assert ledger.normalize_provider_record_id("   ") is None
    assert ledger.normalize_author_family("   ") is None


@pytest.mark.parametrize("value", ["\u200b", "\u0301", "\u2028", "\x00", "\ud800"])
def test_visible_semantic_text_rejects_nonsemantic_unicode(value: str) -> None:
    assert not ledger.has_visible_semantic_text(value, allow_symbols=True)
    assert not ledger.has_visible_semantic_text(value, allow_symbols=False)


def test_visible_semantic_text_nfkc_base_and_field_symbol_policy() -> None:
    assert ledger.has_visible_semantic_text("Ａ", allow_symbols=False)
    assert ledger.has_visible_semantic_text("a\u0301", allow_symbols=False)
    assert ledger.has_visible_semantic_text("✓", allow_symbols=True)
    assert not ledger.has_visible_semantic_text("✓", allow_symbols=False)
    assert not ledger.has_visible_semantic_text("---", allow_symbols=True)


def test_semantically_empty_title_fails_closed_at_the_runtime_boundary() -> None:
    plan = _plan()
    retained = _retained()
    hit = retained["raw_hits"][2]
    hit.update(provider_record_id=None, doi="doi:   ", title="---")
    with pytest.raises(ledger.LedgerError, match="raw_hits.hit-3.title"):
        ledger.validate_input(plan, retained)


@pytest.mark.parametrize(
    "invalid_doi",
    ["-", "x", "10.1/", "10.1234/---", "10.1234/x\u200b"],
)
def test_invalid_doi_does_not_satisfy_minimum_identity(invalid_doi: str) -> None:
    plan = _plan()
    retained = _retained()
    hit = retained["raw_hits"][2]
    hit.update(provider_record_id=None, doi=invalid_doi, title=None)
    retained["relevance_assessments"] = retained["relevance_assessments"][:1]
    _rehash_input(retained, plan)
    result = ledger.build_ledger(plan, retained)
    row = next(row for row in result["raw_hits"] if row["raw_hit_id"] == "hit-3")
    assert row["terminal_state"] == "missing_title_and_stable_id"


@pytest.mark.parametrize(
    "invalid_doi",
    [
        "-",
        "x",
        "10.1/",
        "10.1234/---",
        "10.1234/x\u200b",
        "10.1234/x\ud800",
    ],
)
def test_doi_normalizer_rejects_invalid_or_invisible_suffixes(
    invalid_doi: str,
) -> None:
    assert ledger.normalize_doi(invalid_doi) is None


def test_doi_normalizer_accepts_only_a_valid_prefixed_body() -> None:
    assert ledger.normalize_doi(" doi: 10.1234/X ") == "10.1234/x"
    assert ledger.normalize_doi("https://doi.org/10.123456789/Ab-1") == (
        "10.123456789/ab-1"
    )


def test_normalization_empty_dois_never_create_a_strong_union() -> None:
    plan = _plan()
    retained = _retained()
    retained["raw_hits"][0]["doi"] = "doi:   "
    retained["raw_hits"][1].update(
        doi="https://doi.org/",
        title="A distinct candidate",
        explicit_version_of_raw_hit_id=None,
    )
    assessment = copy.deepcopy(retained["relevance_assessments"][0])
    assessment["canonical_raw_hit_id"] = "hit-2"
    assessment["raw_output"] = "assessment-hit-2"
    assessment["raw_output_sha256"] = ledger.text_digest(assessment["raw_output"])
    retained["relevance_assessments"].append(assessment)
    _rehash_input(retained, plan)
    result = ledger.build_ledger(plan, retained)
    rows = {row["raw_hit_id"]: row for row in result["raw_hits"]}
    assert rows["hit-1"]["work_family_id"] != rows["hit-2"]["work_family_id"]


def test_distinct_dois_defeat_weaker_title_fallback() -> None:
    retained = _retained()
    retained["raw_hits"][1]["doi"] = "10.1000/distinct"
    retained["raw_hits"][1]["explicit_version_of_raw_hit_id"] = None
    assessment = copy.deepcopy(retained["relevance_assessments"][0])
    assessment["canonical_raw_hit_id"] = "hit-2"
    assessment["raw_output"] = "assessment-hit-2"
    assessment["raw_output_sha256"] = ledger.text_digest(assessment["raw_output"])
    retained["relevance_assessments"].append(assessment)
    _rehash_input(retained)
    result = ledger.build_ledger(_plan(), retained)
    rows = {row["raw_hit_id"]: row for row in result["raw_hits"]}
    assert rows["hit-1"]["work_family_id"] != rows["hit-2"]["work_family_id"]
    assert rows["hit-2"]["terminal_state"] == "selected"


def test_exact_claim_construction_allows_only_marker_stripping_and_ascii_space() -> None:
    plan = _plan()
    plan["claim"]["claim_text"] = "A structured <!--ref:x--> reminder\n improves artifact completeness by 12%."
    _rehash_plan(plan)
    retained = _retained()
    _rehash_input(retained, plan)
    ledger.build_ledger(plan, retained)
    plan["queries"][0]["accepted_query_text"] += " extra"
    _rehash_plan(plan)
    with pytest.raises(ledger.LedgerError, match="exact_claim"):
        ledger.build_ledger(plan, retained)


@pytest.mark.parametrize(
    ("field", "construction"),
    [
        ("original_query_text", "researcher_authored"),
        ("accepted_query_text", "researcher_authored"),
        ("accepted_query_text", "assisted_then_researcher_approved"),
    ],
)
def test_all_query_constructions_reject_whitespace_only_text(
    field: str, construction: str
) -> None:
    plan = _plan()
    query = plan["queries"][0]
    query["construction"] = construction
    query[field] = "   "
    _rehash_plan(plan)
    with pytest.raises(ledger.LedgerError, match=field):
        ledger.validate_plan(plan)
    retained = _retained()
    _rehash_input(retained, plan)
    with pytest.raises(ledger.LedgerError, match="query plan schema violation"):
        ledger.build_ledger(plan, retained)


def test_claim_text_rejects_whitespace_only_content() -> None:
    plan = _plan()
    plan["claim"]["claim_text"] = "   "
    _rehash_plan(plan)
    with pytest.raises(ledger.LedgerError, match="claim_text"):
        ledger.validate_plan(plan)
    retained = _retained()
    _rehash_input(retained, plan)
    with pytest.raises(ledger.LedgerError, match="query plan schema violation"):
        ledger.build_ledger(plan, retained)


def test_stage_tier_rule_is_closed() -> None:
    plan = _plan()
    plan["claim"]["registry_selection_tier"] = "ALL"
    _rehash_plan(plan)
    with pytest.raises(ledger.LedgerError, match="HIGH-IMPACT"):
        ledger.build_ledger(plan, _retained())
    plan["claim"]["checkpoint"] = "stage_4_5"
    _rehash_plan(plan)
    retained = _retained()
    _rehash_input(retained, plan)
    ledger.build_ledger(plan, retained)


def test_consent_and_input_digest_drift_fail_closed() -> None:
    plan = _plan()
    plan["consent"]["queries_sha256"] = "0" * 64
    with pytest.raises(ledger.LedgerError, match="consent binding"):
        ledger.build_ledger(plan, _retained())
    retained = _retained()
    retained["completed_at"] = "2026-08-13T01:02:00Z"
    with pytest.raises(ledger.LedgerError, match="does not bind input"):
        ledger.build_ledger(_plan(), retained)


@pytest.mark.parametrize(
    ("path", "mutation"),
    [
        (("probe_id",), "probe-mutated"),
        (("allowed_languages",), ["en", "fr"]),
        (("allowed_document_types",), ["journal-article"]),
        (("authorized_content_classes",), ["accepted_search_query", "claim_text"]),
    ],
)
def test_consent_receipt_binds_complete_authorization_surface(
    path: tuple[str, ...], mutation: object
) -> None:
    plan = _plan()
    plan[path[0]] = mutation
    plan["plan_sha256"] = ledger.bound_digest(plan, "plan_sha256")
    retained = _retained()
    _rehash_input(retained, plan)
    with pytest.raises(ledger.LedgerError, match="consentable plan|query plan schema"):
        ledger.build_ledger(plan, retained)


@pytest.mark.parametrize(
    ("state", "reference"),
    [
        ("known", None),
        ("known", "   "),
        ("unknown", "https://example.invalid/terms"),
    ],
)
def test_retention_disclosure_state_and_reference_are_consistent(
    state: str, reference: str | None
) -> None:
    plan = _plan()
    plan["provider_roster"][0]["retention_state"] = state
    plan["provider_roster"][0]["retention_reference"] = reference
    _rehash_plan(plan)
    with pytest.raises(ledger.LedgerError, match="retention_reference"):
        ledger.validate_plan(plan)
    retained = _retained()
    _rehash_input(retained, plan)
    with pytest.raises(ledger.LedgerError, match="query plan schema violation"):
        ledger.build_ledger(plan, retained)


@pytest.mark.parametrize("field", ["deletion_boundary", "export_boundary"])
def test_consent_boundary_disclosures_cannot_be_whitespace(field: str) -> None:
    plan = _plan()
    plan["consent"][field] = "   "
    plan["consent"]["receipt_sha256"] = ledger.bound_digest(
        plan["consent"], "receipt_sha256"
    )
    plan["plan_sha256"] = ledger.bound_digest(plan, "plan_sha256")
    with pytest.raises(ledger.LedgerError, match=field):
        ledger.validate_plan(plan)
    retained = _retained()
    _rehash_input(retained, plan)
    with pytest.raises(ledger.LedgerError, match="query plan schema violation"):
        ledger.build_ledger(plan, retained)


def test_relevance_rows_bind_exact_claim_candidate_and_prompt_bytes() -> None:
    plan = _plan()
    plan["claim"]["claim_text"] = "A wholly different reconsented claim."
    plan["queries"][0]["accepted_query_text"] = plan["claim"]["claim_text"]
    plan["queries"][0]["original_query_text"] = plan["claim"]["claim_text"]
    _rehash_plan(plan)
    retained = _retained()
    retained["query_plan_sha256"] = plan["plan_sha256"]
    retained["retrieval_input_sha256"] = ledger.bound_digest(
        retained, "retrieval_input_sha256"
    )
    with pytest.raises(ledger.LedgerError, match="exact claim, candidate"):
        ledger.build_ledger(plan, retained)

    plan = _plan()
    retained = _retained()
    retained["relevance_assessments"][0]["prompt_utf8"] += " stale"
    retained["retrieval_input_sha256"] = ledger.bound_digest(
        retained, "retrieval_input_sha256"
    )
    with pytest.raises(ledger.LedgerError, match="canonical relevance prompt"):
        ledger.build_ledger(plan, retained)


def test_every_planned_query_index_pair_requires_visible_root_attempt() -> None:
    retained = _retained()
    retained["attempts"] = [
        attempt
        for attempt in retained["attempts"]
        if attempt["attempt_id"] != "attempt-c"
    ]
    _rehash_input(retained)
    with pytest.raises(ledger.LedgerError, match="every planned query/index"):
        ledger.build_ledger(_plan(), retained)


def test_runtime_enforces_closed_input_contracts() -> None:
    plan = _plan()
    plan["undeclared"] = True
    with pytest.raises(ledger.LedgerError, match="query plan schema violation"):
        ledger.build_ledger(plan, _retained())
    retained = _retained()
    retained["raw_hits"][0]["undeclared"] = True
    with pytest.raises(ledger.LedgerError, match="retrieval input schema violation"):
        ledger.build_ledger(_plan(), retained)


@pytest.mark.parametrize("field", ["provider_record_id", "title"])
def test_raw_hit_identity_fields_reject_whitespace_only_values(field: str) -> None:
    plan = _plan()
    retained = _retained()
    hit = retained["raw_hits"][2]
    hit["title"] = None
    hit["provider_record_id"] = None
    hit["doi"] = None
    hit[field] = "   "
    _rehash_input(retained, plan)
    with pytest.raises(ledger.LedgerError, match=field):
        ledger.validate_input(plan, retained)
    with pytest.raises(ledger.LedgerError, match="retrieval input schema violation"):
        ledger.build_ledger(plan, retained)


def test_whitespace_only_doi_is_structurally_rejected_and_never_identity() -> None:
    plan = _plan()
    retained = _retained()
    hit = retained["raw_hits"][2]
    hit.update(title=None, provider_record_id=None, doi="   ")
    assert ledger.normalize_doi(hit["doi"]) is None
    with pytest.raises(ledger.LedgerError, match="retrieval input schema violation"):
        ledger.build_ledger(plan, retained)


@pytest.mark.parametrize("field", ["family", "given"])
def test_author_names_reject_whitespace_in_schema_and_runtime(field: str) -> None:
    plan = _plan()
    retained = _retained()
    retained["raw_hits"][0]["authors"][0][field] = "   "
    _rehash_input(retained, plan)
    with pytest.raises(ledger.LedgerError, match=field):
        ledger.validate_input(plan, retained)
    with pytest.raises(ledger.LedgerError, match="retrieval input schema violation"):
        ledger.build_ledger(plan, retained)


@pytest.mark.parametrize(
    "field", ["product_identity", "query_capability", "pagination_behavior"]
)
def test_provider_disclosures_reject_whitespace_in_schema_and_runtime(field: str) -> None:
    plan = _plan()
    plan["provider_roster"][0][field] = "   "
    _rehash_plan(plan)
    with pytest.raises(ledger.LedgerError, match=field):
        ledger.validate_plan(plan)
    retained = _retained()
    _rehash_input(retained, plan)
    with pytest.raises(ledger.LedgerError, match="query plan schema violation"):
        ledger.build_ledger(plan, retained)


@pytest.mark.parametrize(
    ("surface", "value"),
    [
        ("claim", "\u200b"),
        ("query_original", "\u0301"),
        ("query_accepted", "\u2060"),
        ("provider_disclosure", "\u200b"),
        ("retention_reference", "\u0301"),
        ("deletion_boundary", "\u2060"),
        ("export_boundary", "\ud800"),
    ],
)
def test_plan_semantic_text_surfaces_reject_invisible_unicode(
    surface: str, value: str
) -> None:
    plan = _plan()
    if surface == "claim":
        plan["claim"]["claim_text"] = value
    elif surface == "query_original":
        plan["queries"][0]["original_query_text"] = value
    elif surface == "query_accepted":
        plan["queries"][0]["accepted_query_text"] = value
    elif surface == "provider_disclosure":
        plan["provider_roster"][0]["product_identity"] = value
    elif surface == "retention_reference":
        provider = plan["provider_roster"][0]
        provider["retention_state"] = "known"
        provider["retention_reference"] = value
    else:
        plan["consent"][surface] = value
    with pytest.raises(ledger.LedgerError, match="semantic|visible"):
        ledger.validate_plan(plan)


@pytest.mark.parametrize(
    ("surface", "value"),
    [
        ("provider_record_id", "\u200b"),
        ("title", "\u0301"),
        ("author_family", "\u2060"),
        ("author_given", "\ud800"),
        ("abstract", "\x00"),
        ("success_rationale", "\u200b"),
        ("success_raw_output", "\u0301"),
        ("failure_detail", "\u2060"),
    ],
)
def test_retained_semantic_text_surfaces_reject_invisible_unicode(
    surface: str, value: str
) -> None:
    plan = _plan()
    retained = _retained()
    hit = retained["raw_hits"][0]
    assessment = retained["relevance_assessments"][0]
    if surface == "provider_record_id":
        hit["provider_record_id"] = value
    elif surface == "title":
        hit["title"] = value
    elif surface == "author_family":
        hit["authors"][0]["family"] = value
    elif surface == "author_given":
        hit["authors"][0]["given"] = value
    elif surface == "abstract":
        hit["abstract_text"] = value
    elif surface == "success_rationale":
        assessment["rationale"] = value
    elif surface == "success_raw_output":
        assessment["raw_output"] = value
        assessment["raw_output_sha256"] = ledger.text_digest(value)
    else:
        assessment.update(
            outcome="failed",
            state="not_checked",
            reason_code=None,
            rationale=None,
            raw_output=None,
            raw_output_sha256=None,
            failure_code="timeout",
            failure_detail=value,
        )
    with pytest.raises(ledger.LedgerError, match="semantic|visible"):
        ledger.validate_input(plan, retained)


def test_attempt_counts_caps_and_failed_ownership_fail_closed() -> None:
    retained = _retained()
    retained["attempts"][0]["retained_hit_count"] = 1
    _rehash_input(retained)
    with pytest.raises(ledger.LedgerError, match="retained source rows"):
        ledger.build_ledger(_plan(), retained)


def test_second_initial_attempt_for_same_pair_is_rejected() -> None:
    retained = _retained()
    retained["attempts"][1]["index_id"] = "index-a"
    retained["raw_hits"][1]["index_id"] = "index-a"
    _rehash_input(retained)
    with pytest.raises(ledger.LedgerError, match="only one initial attempt"):
        ledger.build_ledger(_plan(), retained)
    retained = _retained()
    retained["raw_hits"][0]["attempt_id"] = "attempt-c"
    retained["raw_hits"][0]["index_id"] = "index-c"
    _rehash_input(retained)
    with pytest.raises(ledger.LedgerError, match="failed attempts cannot own"):
        ledger.build_ledger(_plan(), retained)


def test_retry_requires_a_fresh_named_authorization() -> None:
    retained = _retained()
    retained["attempts"][1]["retry_of_attempt_id"] = "attempt-c"
    _rehash_input(retained)
    with pytest.raises(ledger.LedgerError, match="fresh authorization"):
        ledger.build_ledger(_plan(), retained)
    retained["attempts"][1]["retry_authorization_receipt_id"] = "consent-retry-002"
    retained["attempts"].append(
        {
            "attempt_id": "attempt-b-root",
            "query_id": "q1",
            "index_id": "index-b",
            "started_at": "2026-08-13T01:00:00Z",
            "completed_at": "2026-08-13T01:01:00Z",
            "outcome": "service_unavailable",
            "provider_reported_count": None,
            "returned_count": 0,
            "retained_hit_count": 0,
            "truncated_count": 0,
            "retry_of_attempt_id": None,
            "retry_authorization_receipt_id": None,
            "consent_receipt_id": "consent-001",
        }
    )
    retained["attempts"][1]["retry_of_attempt_id"] = "attempt-b-root"
    retained["attempts"][1]["started_at"] = "2026-08-13T01:03:00Z"
    retained["attempts"][1]["completed_at"] = "2026-08-13T01:04:00Z"
    retained["raw_hits"][1]["returned_at"] = "2026-08-13T01:04:00Z"
    retained["completed_at"] = "2026-08-13T01:04:00Z"
    _rehash_input(retained)
    with pytest.raises(ledger.LedgerError, match="retained receipt"):
        ledger.build_ledger(_plan(), retained)
    receipt = {
        "retry_authorization_receipt_id": "consent-retry-002",
        "query_plan_sha256": _plan()["plan_sha256"],
        "probe_id": _plan()["probe_id"],
        "consent_receipt_id": _plan()["consent"]["consent_receipt_id"],
        "failed_attempt_id": "attempt-b-root",
        "query_id": "q1",
        "index_id": "index-b",
        "accepted_at": "2026-08-13T01:02:00Z",
        "receipt_sha256": "",
    }
    receipt["receipt_sha256"] = ledger.bound_digest(receipt, "receipt_sha256")
    retained["retry_authorizations"] = [receipt]
    _rehash_input(retained)
    ledger.build_ledger(_plan(), retained)

    stale = copy.deepcopy(retained)
    stale["retry_authorizations"][0]["accepted_at"] = "2026-08-13T01:01:00Z"
    stale["retry_authorizations"][0]["receipt_sha256"] = ledger.bound_digest(
        stale["retry_authorizations"][0], "receipt_sha256"
    )
    _rehash_input(stale)
    with pytest.raises(ledger.LedgerError, match="later than the failed attempt"):
        ledger.build_ledger(_plan(), stale)

    retained["retry_authorizations"][0]["failed_attempt_id"] = "attempt-a"
    retained["retry_authorizations"][0]["receipt_sha256"] = ledger.bound_digest(
        retained["retry_authorizations"][0], "receipt_sha256"
    )
    _rehash_input(retained)
    with pytest.raises(ledger.LedgerError, match="failed attempt"):
        ledger.build_ledger(_plan(), retained)


def test_retry_must_target_a_failed_attempt_on_the_same_pair() -> None:
    retained = _retained()
    retained["attempts"][1]["retry_of_attempt_id"] = "attempt-a"
    retained["attempts"][1]["retry_authorization_receipt_id"] = "consent-retry-002"
    _rehash_input(retained)
    with pytest.raises(ledger.LedgerError, match="must name a failed attempt"):
        ledger.build_ledger(_plan(), retained)
    retained = _retained()
    retained["attempts"][1]["retry_of_attempt_id"] = "attempt-c"
    retained["attempts"][1]["retry_authorization_receipt_id"] = "consent-retry-002"
    _rehash_input(retained)
    with pytest.raises(ledger.LedgerError, match="preserve the failed query/index"):
        ledger.build_ledger(_plan(), retained)


def test_20_hit_cap_is_aggregate_per_query_index_across_attempts() -> None:
    retained = _retained()
    for attempt_id, count, authorization in (
        ("attempt-d", 20, "consent-retry-002"),
        ("attempt-e", 1, "consent-retry-003"),
    ):
        retry = copy.deepcopy(retained["attempts"][0])
        retry.update(
            attempt_id=attempt_id,
            index_id="index-c",
            retained_hit_count=count,
            returned_count=count,
            provider_reported_count=count,
            retry_of_attempt_id="attempt-c",
            retry_authorization_receipt_id=authorization,
            started_at="2026-08-13T01:03:00Z",
            completed_at="2026-08-13T01:04:00Z",
        )
        retained["attempts"].append(retry)
        receipt = {
            "retry_authorization_receipt_id": authorization,
            "query_plan_sha256": _plan()["plan_sha256"],
            "probe_id": _plan()["probe_id"],
            "consent_receipt_id": "consent-001",
            "failed_attempt_id": "attempt-c",
            "query_id": "q1",
            "index_id": "index-c",
            "accepted_at": "2026-08-13T01:02:00Z",
            "receipt_sha256": "",
        }
        receipt["receipt_sha256"] = ledger.bound_digest(receipt, "receipt_sha256")
        retained["retry_authorizations"].append(receipt)
    template = retained["raw_hits"][2]
    n = 3
    for attempt_id, count in (("attempt-d", 20), ("attempt-e", 1)):
        for rank in range(1, count + 1):
            n += 1
            raw = copy.deepcopy(template)
            raw.update(
                raw_hit_id=f"retry-hit-{n}",
                attempt_id=attempt_id,
                index_id="index-c",
                provider_rank=rank,
                provider_record_id=f"retry-record-{n}",
                doi=f"10.1000/retry-{n}",
                title=f"Retry candidate {n}",
                returned_at="2026-08-13T01:04:00Z",
            )
            retained["raw_hits"].append(raw)
    retained["completed_at"] = "2026-08-13T01:04:00Z"
    _rehash_input(retained)
    with pytest.raises(ledger.LedgerError, match="aggregate 20-hit"):
        ledger.build_ledger(_plan(), retained)


def test_attempt_hit_and_input_timestamps_are_monotonic() -> None:
    retained = _retained()
    retained["attempts"][0]["started_at"] = "2026-08-13T01:02:00Z"
    _rehash_input(retained)
    with pytest.raises(ledger.LedgerError, match="input completion"):
        ledger.build_ledger(_plan(), retained)

    retained = _retained()
    retained["raw_hits"][0]["returned_at"] = "2026-08-13T00:59:59Z"
    _rehash_input(retained)
    with pytest.raises(ledger.LedgerError, match="owning attempt"):
        ledger.build_ledger(_plan(), retained)

    retained = _retained()
    retained["relevance_assessments"][0]["assessed_at"] = "2026-08-13T00:59:59Z"
    _rehash_input(retained)
    with pytest.raises(ledger.LedgerError, match="candidate return"):
        ledger.build_ledger(_plan(), retained)


@pytest.mark.parametrize(
    ("state", "reason", "message"),
    [
        ("not_checked", None, "schema violation|successful assessment"),
        ("not_relevant", None, "schema violation|mismatch reason"),
        ("relevant", "outcome_mismatch", "schema violation|must be null"),
    ],
)
def test_relevance_states_fail_closed(state: str, reason: str | None, message: str) -> None:
    retained = _retained()
    retained["relevance_assessments"][0]["state"] = state
    retained["relevance_assessments"][0]["reason_code"] = reason
    _rehash_input(retained)
    with pytest.raises(ledger.LedgerError, match=message):
        ledger.build_ledger(_plan(), retained)


def test_failed_relevance_assessment_remains_truthfully_visible() -> None:
    retained = _retained()
    assessment = retained["relevance_assessments"][0]
    assessment.update(
        outcome="failed",
        state="not_checked",
        reason_code=None,
        rationale=None,
        raw_output=None,
        raw_output_sha256=None,
        failure_code="timeout",
        failure_detail="Synthetic assessor timeout.",
    )
    _rehash_input(retained)
    result = ledger.build_ledger(_plan(), retained)
    family = next(
        row for row in result["work_families"] if row["canonical_raw_hit_id"] == "hit-1"
    )
    assert family["selection_state"] == "not_checked"
    assert family["relevance"]["failure_code"] == "timeout"
    row = next(row for row in result["raw_hits"] if row["raw_hit_id"] == "hit-1")
    assert row["terminal_state"] == "not_checked"
    assert result["counts"]["raw_hit_state_counts"]["not_checked"] == 1


def test_failed_malformed_relevance_preserves_whitespace_raw_output_exactly() -> None:
    retained = _retained()
    assessment = retained["relevance_assessments"][0]
    assessment.update(
        outcome="failed",
        state="not_checked",
        reason_code=None,
        rationale=None,
        raw_output="   ",
        raw_output_sha256=ledger.text_digest("   "),
        failure_code="malformed_output",
        failure_detail="Assessor returned only whitespace.",
    )
    _rehash_input(retained)
    result = ledger.build_ledger(_plan(), retained)
    family = next(
        row for row in result["work_families"] if row["canonical_raw_hit_id"] == "hit-1"
    )
    assert family["relevance"]["raw_output"] == "   "
    assert family["relevance"]["raw_output_sha256"] == ledger.text_digest("   ")


def test_failed_malformed_relevance_preserves_format_only_raw_output_exactly() -> None:
    retained = _retained()
    assessment = retained["relevance_assessments"][0]
    assessment.update(
        outcome="failed",
        state="not_checked",
        reason_code=None,
        rationale=None,
        raw_output="\u200b\u2060",
        raw_output_sha256=ledger.text_digest("\u200b\u2060"),
        failure_code="malformed_output",
        failure_detail="Assessor returned format-only output.",
    )
    _rehash_input(retained)
    result = ledger.build_ledger(_plan(), retained)
    family = next(
        row
        for row in result["work_families"]
        if row["canonical_raw_hit_id"] == "hit-1"
    )
    assert family["relevance"]["raw_output"] == "\u200b\u2060"
    assert family["relevance"]["raw_output_sha256"] == ledger.text_digest(
        "\u200b\u2060"
    )


def test_available_abstract_rejects_whitespace_in_schema_and_runtime() -> None:
    plan = _plan()
    retained = _retained()
    hit = retained["raw_hits"][0]
    hit["abstract_text"] = "   "
    hit["abstract_sha256"] = ledger.text_digest(hit["abstract_text"])
    _rehash_input(retained, plan)
    with pytest.raises(ledger.LedgerError, match="abstract_text"):
        ledger.validate_input(plan, retained)
    with pytest.raises(ledger.LedgerError, match="retrieval input schema violation"):
        ledger.build_ledger(plan, retained)


@pytest.mark.parametrize("field", ["rationale", "raw_output"])
def test_successful_relevance_text_rejects_whitespace_in_schema_and_runtime(
    field: str,
) -> None:
    plan = _plan()
    retained = _retained()
    assessment = retained["relevance_assessments"][0]
    assessment[field] = "   "
    if field == "raw_output":
        assessment["raw_output_sha256"] = ledger.text_digest(assessment[field])
    _rehash_input(retained, plan)
    with pytest.raises(ledger.LedgerError, match=field):
        ledger.validate_input(plan, retained)
    with pytest.raises(ledger.LedgerError, match="retrieval input schema violation"):
        ledger.build_ledger(plan, retained)


def test_failed_relevance_detail_rejects_whitespace_in_schema_and_runtime() -> None:
    plan = _plan()
    retained = _retained()
    assessment = retained["relevance_assessments"][0]
    assessment.update(
        outcome="failed",
        state="not_checked",
        reason_code=None,
        rationale=None,
        raw_output=None,
        raw_output_sha256=None,
        failure_code="timeout",
        failure_detail="   ",
    )
    _rehash_input(retained, plan)
    with pytest.raises(ledger.LedgerError, match="failure"):
        ledger.validate_input(plan, retained)
    with pytest.raises(ledger.LedgerError, match="retrieval input schema violation"):
        ledger.build_ledger(plan, retained)


def test_relevance_raw_output_hash_is_verified() -> None:
    retained = _retained()
    retained["relevance_assessments"][0]["raw_output"] = "drifted output"
    _rehash_input(retained)
    with pytest.raises(ledger.LedgerError, match="retained raw output"):
        ledger.build_ledger(_plan(), retained)


def test_weak_title_match_cannot_bridge_distinct_doi_components() -> None:
    retained = _retained()
    retained["raw_hits"][1]["doi"] = None
    retained["raw_hits"][1]["explicit_version_of_raw_hit_id"] = None
    retained["raw_hits"][2]["doi"] = "10.1000/distinct"
    retained["raw_hits"][2]["title"] = "Reminder Effects"
    retained["relevance_assessments"][1]["canonical_raw_hit_id"] = "hit-2"
    extra = copy.deepcopy(retained["relevance_assessments"][0])
    extra["canonical_raw_hit_id"] = "hit-3"
    extra["raw_output"] = "assessment-hit-3-distinct"
    extra["raw_output_sha256"] = ledger.text_digest(extra["raw_output"])
    retained["relevance_assessments"].append(extra)
    _rehash_input(retained)
    result = ledger.build_ledger(_plan(), retained)
    rows = {row["raw_hit_id"]: row for row in result["raw_hits"]}
    assert len({rows[name]["work_family_id"] for name in ("hit-1", "hit-2", "hit-3")}) == 3


def test_top_40_is_deterministic_and_overflow_remains_visible() -> None:
    retained = _retained()
    retained["attempts"] = []
    retained["raw_hits"] = []
    retained["relevance_assessments"] = []
    for index_no, (index_id, count) in enumerate(
        (("index-a", 20), ("index-b", 20), ("index-c", 1))
    ):
        attempt_id = f"attempt-{index_no}"
        retained["attempts"].append(
            {
                "attempt_id": attempt_id,
                "query_id": "q1",
                "index_id": index_id,
                "started_at": "2026-08-13T01:00:00Z",
                "completed_at": "2026-08-13T01:01:00Z",
                "outcome": "success",
                "provider_reported_count": count,
                "returned_count": count,
                "retained_hit_count": count,
                "truncated_count": 0,
                "retry_of_attempt_id": None,
                "retry_authorization_receipt_id": None,
                "consent_receipt_id": "consent-001",
            }
        )
        for rank in range(1, count + 1):
            n = len(retained["raw_hits"]) + 1
            raw_id = f"cap-hit-{n:02d}"
            text = f"Synthetic abstract {n}."
            retained["raw_hits"].append(
                {
                    "raw_hit_id": raw_id,
                    "probe_id": "probe-655-fixture",
                    "query_id": "q1",
                    "index_id": index_id,
                    "attempt_id": attempt_id,
                    "provider_rank": rank,
                    "provider_record_id": f"record-{n:02d}",
                    "doi": f"10.1000/cap-{n:02d}",
                    "title": f"Unique candidate {n:02d}",
                    "authors": [{"family": f"Author{n:02d}", "given": None}],
                    "year": 2024,
                    "language": "en",
                    "document_type": "journal-article",
                    "publication_status": "published",
                    "abstract_state": "available",
                    "abstract_text": text,
                    "abstract_sha256": ledger.text_digest(text),
                    "landing_url": None,
                    "returned_at": "2026-08-13T01:01:00Z",
                    "raw_metadata_sha256": ledger.text_digest(f"metadata-{n}"),
                    "explicit_version_of_raw_hit_id": None,
                }
            )
            retained["relevance_assessments"].append(
                {
                    "canonical_raw_hit_id": raw_id,
                    "state": "relevant",
                    "reason_code": None,
                    "rationale": "Synthetic relevant candidate.",
                    "assessor_kind": "synthetic_fixture",
                    "assessor_id": "fixture-assessor",
                    "prompt_version": "fixture-v1",
                    "outcome": "success",
                    "raw_output": f"assessment-{n}",
                    "raw_output_sha256": ledger.text_digest(f"assessment-{n}"),
                    "failure_code": None,
                    "failure_detail": None,
                    "assessed_at": "2026-08-13T01:01:00Z",
                }
            )
    _rehash_input(retained)
    result = ledger.build_ledger(_plan(), retained)
    assert result["counts"]["selected_work_families"] == 40
    assert result["counts"]["raw_hit_state_counts"]["candidate_cap_exceeded"] == 1


def _umask_022() -> None:
    os.umask(0o022)


def _cli_build_command(plan_path: Path, retained_path: Path, output: Path) -> list[str]:
    return [
        sys.executable,
        str(ROOT / "scripts/build_claim_standing_candidate_ledger.py"),
        "build",
        "--query-plan",
        str(plan_path),
        "--retrieval-input",
        str(retained_path),
        "--output",
        str(output),
    ]


def test_cli_session_only_build_refuses_before_creating_0644_output(
    tmp_path: Path,
) -> None:
    output = tmp_path / "would-be-0644" / "ledger.json"
    command = _cli_build_command(
        FIXTURES / "query_plan.json",
        FIXTURES / "retrieval_input.json",
        output,
    )
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        preexec_fn=_umask_022,
    )
    assert completed.returncode == 1
    assert "explicit_local_export" in completed.stderr
    assert not output.exists()
    assert not output.parent.exists()


def test_cli_explicit_local_export_is_write_once_and_validate_replays(
    tmp_path: Path,
) -> None:
    plan = _plan()
    output = tmp_path / "ledger.json"
    _authorize_local_export(plan, str(output))
    retained = _retained()
    _rehash_input(retained, plan)
    plan_path = tmp_path / "query-plan.json"
    retained_path = tmp_path / "retrieval-input.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    retained_path.write_text(json.dumps(retained), encoding="utf-8")
    command = _cli_build_command(plan_path, retained_path, output)
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        preexec_fn=_umask_022,
    )
    assert completed.returncode == 0
    assert output.stat().st_mode & 0o777 == 0o600
    written = json.loads(output.read_text(encoding="utf-8"))
    assert written["local_persistence"] == "explicit_local_export"
    assert written["export_boundary"] == plan["consent"]["export_boundary"]
    assert {row["sharing_scope"] for row in written["work_families"]} == {
        "explicit_local_export"
    }
    assert {row["rights_basis"] for row in written["work_families"]} == {
        "not_assessed"
    }
    assert subprocess.run(command, capture_output=True, text=True).returncode == 1
    validate = command[:2] + [
        "validate",
        "--query-plan",
        str(plan_path),
        "--retrieval-input",
        str(retained_path),
        "--candidate-ledger",
        str(output),
    ]
    assert subprocess.run(validate, capture_output=True, text=True).returncode == 0


def test_cli_invalid_unicode_fails_without_traceback_or_output(tmp_path: Path) -> None:
    plan = _plan()
    output = tmp_path / "ledger.json"
    _authorize_local_export(plan, str(output))
    plan["claim"]["claim_text"] = "\ud800"
    plan_path = tmp_path / "query-plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    retained_path = FIXTURES / "retrieval_input.json"
    completed = subprocess.run(
        _cli_build_command(plan_path, retained_path, output),
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 1
    assert "ERROR:" in completed.stderr
    assert "Traceback" not in completed.stderr
    assert not output.exists()


@pytest.mark.skipif(os.name == "nt", reason="POSIX symlink/no-follow regression")
def test_cli_explicit_local_export_refuses_a_symlink_output(tmp_path: Path) -> None:
    plan = _plan()
    output = tmp_path / "ledger.json"
    _authorize_local_export(plan, str(output))
    retained = _retained()
    _rehash_input(retained, plan)
    plan_path = tmp_path / "query-plan.json"
    retained_path = tmp_path / "retrieval-input.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    retained_path.write_text(json.dumps(retained), encoding="utf-8")
    target = tmp_path / "target.json"
    output.symlink_to(target)
    completed = subprocess.run(
        _cli_build_command(plan_path, retained_path, output),
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 1
    assert "refuses to overwrite" in completed.stderr
    assert output.is_symlink()
    assert not target.exists()


def test_cli_explicit_local_export_rejects_any_other_output_path(
    tmp_path: Path,
) -> None:
    authorized = tmp_path / "authorized.json"
    unauthorized = tmp_path / "unauthorized.json"
    plan = _plan()
    _authorize_local_export(plan, str(authorized))
    retained = _retained()
    _rehash_input(retained, plan)
    plan_path = tmp_path / "query-plan.json"
    retained_path = tmp_path / "retrieval-input.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    retained_path.write_text(json.dumps(retained), encoding="utf-8")

    rejected = subprocess.run(
        _cli_build_command(plan_path, retained_path, unauthorized),
        capture_output=True,
        text=True,
    )
    assert rejected.returncode == 1
    assert "authorized_output_path" in rejected.stderr
    assert not unauthorized.exists()

    accepted = subprocess.run(
        _cli_build_command(plan_path, retained_path, authorized),
        capture_output=True,
        text=True,
    )
    assert accepted.returncode == 0
    assert authorized.stat().st_mode & 0o777 == 0o600
