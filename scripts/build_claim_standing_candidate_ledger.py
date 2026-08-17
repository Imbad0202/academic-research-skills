#!/usr/bin/env python3
"""Build or replay-validate the offline #655 Track A candidate ledger.

The runtime consumes only explicitly named local JSON files containing a frozen
query plan and already-returned synthetic or externally supplied retrieval
records.  It has no discovery adapter, transport, model, stance classifier,
renderer, ambient clock, retry, or overwrite path.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime
from itertools import combinations
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError


PLAN_VERSION = "claim-standing-query-plan/1.0"
PLAN_VERSION_1_1 = "claim-standing-query-plan/1.1"
PLAN_SCHEMA_FILENAMES = {
    PLAN_VERSION: "query_plan.schema.json",
    PLAN_VERSION_1_1: "query_plan_v1_1.schema.json",
}
RETRIEVAL_ONLY_CONTENT_CLASSES = ["accepted_search_query"]
STANCE_CONTENT_CLASSES = [
    "accepted_search_query",
    "claim_and_selected_evidence_to_stance_provider",
]
CHECKPOINT_REQUIRED_TIER = {"stage_2_5": "HIGH-IMPACT", "stage_4_5": "ALL"}
HIGH_IMPACT_BASIS_VALUES = (
    "headline_conclusion",
    "numerical",
    "causal",
    "methods_critical",
    "disputed",
)
INPUT_VERSION = "claim-standing-retrieval-input/1.0"
LEDGER_VERSION = "claim-standing-candidate-ledger/1.0"
RELEVANCE_INPUT_VERSION = "claim-standing-relevance-assessment-input/1.0"
MAX_QUERIES = 3
MAX_INDEXES = 4
MAX_HITS_PER_QUERY_INDEX = 20
MAX_RAW_HITS = 240
MAX_SELECTED = 40
EXPLICIT_LOCAL_EXPORT_BOUNDARY = (
    "One local candidate-ledger export to the operator-named output path is authorized."
)
# Complete family of artifacts derivable from one consented
# authorized_output_path ("" = the candidate ledger at the path itself).
# Consumed by the consent surface disclosure and pinned to each owning
# module's suffix constant by test.
ARTIFACT_SUFFIXES = {
    "candidate_ledger": "",
    "query_plan": ".query-plan.json",
    "retrieval_input": ".retrieval-input.json",
    "transmission_ledger": ".transmission-ledger.json",
    "stance_record": ".stance-record.json",
    "evidence_rows": ".evidence-rows.json",
    "rendered_view": ".view.md",
}
CAPS = {
    "max_queries": MAX_QUERIES,
    "max_indexes": MAX_INDEXES,
    "max_hits_per_query_index": MAX_HITS_PER_QUERY_INDEX,
    "max_raw_hits": MAX_RAW_HITS,
    "max_selected_work_families": MAX_SELECTED,
}
FAILURE_OUTCOMES = {
    "timeout",
    "authentication_failed",
    "rate_limited",
    "malformed_response",
    "service_unavailable",
    "unsupported_query",
}
RAW_TERMINAL_STATES = (
    "selected",
    "missing_title_and_stable_id",
    "outside_date_range",
    "outside_language_set",
    "outside_document_type",
    "duplicate_version",
    "not_relevant",
    "not_checked",
    "candidate_cap_exceeded",
)
SCHEMA_DIR = Path(__file__).resolve().parents[1] / "shared/contracts/claim_standing"

_CITATION_MARKER_RE = re.compile(r"<!--(?:ref|anchor):[^>]*-->")
_ASCII_WS_RE = re.compile(r"[\t\n\r\f\v ]+")
_DOI_PREFIX_RE = re.compile(r"(?i)^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)")
_DOI_BODY_RE = re.compile(r"^10\.[0-9]{4,9}/(.+)$")


class LedgerError(ValueError):
    """A closed #655 Track A invariant failed."""


class DuplicateKeyError(ValueError):
    pass


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite number {token!r}")
            ),
        )
    except (OSError, UnicodeError, JSONDecodeError, ValueError) as exc:
        raise LedgerError(f"{path}: cannot read strict UTF-8 JSON: {exc}") from exc


_VALIDATOR_CACHE: dict[str, Draft202012Validator] = {}


def validate_schema(value: Any, filename: str, label: str) -> None:
    try:
        validator = _VALIDATOR_CACHE.get(filename)
        if validator is None:
            # Schema files are read-only within a process; meta-validate once.
            schema = load_json(SCHEMA_DIR / filename)
            Draft202012Validator.check_schema(schema)
            validator = Draft202012Validator(schema)
            _VALIDATOR_CACHE[filename] = validator
        validator.validate(value)
    except (SchemaError, ValidationError) as exc:
        location = ".".join(str(part) for part in exc.absolute_path) or "<root>"
        raise LedgerError(f"{label} schema violation at {location}: {exc.message}") from exc


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except UnicodeError as exc:
        raise LedgerError("canonical JSON contains invalid Unicode text") from exc


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def text_digest(value: str) -> str:
    try:
        encoded = value.encode("utf-8")
    except UnicodeError as exc:
        raise LedgerError("text digest input contains invalid Unicode text") from exc
    return hashlib.sha256(encoded).hexdigest()


def bound_digest(value: dict[str, Any], field: str) -> str:
    payload = copy.deepcopy(value)
    payload.pop(field, None)
    return digest(payload)


def plan_schema_filename(plan: dict[str, Any]) -> str:
    version = plan.get("schema_version")
    filename = PLAN_SCHEMA_FILENAMES.get(version)
    if filename is None:
        raise LedgerError(
            f"schema_version: unknown query-plan version {version!r}"
        )
    return filename


def consentable_plan_projection(plan: dict[str, Any]) -> dict[str, Any]:
    """Return every plan field whose use requires the named consent receipt."""

    projection = {
        "schema_version": plan["schema_version"],
        "probe_id": plan["probe_id"],
        "claim": copy.deepcopy(plan["claim"]),
        "queries": copy.deepcopy(plan["queries"]),
        "provider_roster": copy.deepcopy(plan["provider_roster"]),
        "allowed_languages": copy.deepcopy(plan["allowed_languages"]),
        "allowed_document_types": copy.deepcopy(plan["allowed_document_types"]),
        "authorized_content_classes": copy.deepcopy(
            plan["authorized_content_classes"]
        ),
        "caps": copy.deepcopy(plan["caps"]),
        "created_at": plan["created_at"],
    }
    if plan.get("schema_version") == PLAN_VERSION_1_1:
        projection["stance_plan"] = copy.deepcopy(plan["stance_plan"])
    return projection


def relevance_assessment_input_projection(
    plan: dict[str, Any], hit: dict[str, Any], assessment: dict[str, Any]
) -> dict[str, Any]:
    """Return the exact claim, candidate, and assessor contract seen at relevance."""

    claim = plan["claim"]
    return {
        "schema_version": RELEVANCE_INPUT_VERSION,
        "claim": {
            "claim_id": claim["claim_id"],
            "claim_text": claim["claim_text"],
            "claim_sha256": claim["claim_sha256"],
        },
        "candidate": {
            "canonical_raw_hit_id": hit["raw_hit_id"],
            "title": hit["title"],
            "abstract_state": hit["abstract_state"],
            "abstract_text": hit["abstract_text"],
            "abstract_sha256": hit["abstract_sha256"],
        },
        "assessor_contract": {
            "assessor_kind": assessment["assessor_kind"],
            "assessor_id": assessment["assessor_id"],
            "prompt_version": assessment["prompt_version"],
            "task": "topical_relevance_only_no_stance_or_credibility",
        },
    }


def render_relevance_prompt(projection: dict[str, Any]) -> str:
    """Render the only prompt bytes bound by a Track A relevance row."""

    return (
        "Assess topical relevance only. Do not infer stance, credibility, consensus, "
        "or claim truth. Use exactly this canonical assessment input:\n"
        + canonical_bytes(projection).decode("utf-8")
    )


def parse_rfc3339(value: str, path: str) -> datetime:
    try:
        return datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except (TypeError, ValueError) as exc:
        raise LedgerError(f"{path}: must be a real RFC 3339 UTC timestamp") from exc


def exact_claim_query(claim_text: str) -> str:
    return _ASCII_WS_RE.sub(" ", _CITATION_MARKER_RE.sub("", claim_text)).strip()


def has_visible_semantic_text(value: Any, *, allow_symbols: bool) -> bool:
    """Return whether NFKC text has a visible semantic base character.

    Surrogates are rejected anywhere. Unicode control/format/separator-only,
    combining-mark-only, whitespace-only, and punctuation-only strings are not
    semantic text. Narrative fields may opt into a symbol as the visible base;
    provider identifiers and author names require a letter or number.
    """

    if not isinstance(value, str):
        return False
    try:
        normalized = unicodedata.normalize("NFKC", value)
        categories = [unicodedata.category(char) for char in normalized]
    except UnicodeError as exc:
        raise LedgerError("semantic text contains invalid Unicode") from exc
    if any(category == "Cs" for category in categories):
        return False
    allowed_groups = {"L", "N", "S"} if allow_symbols else {"L", "N"}
    return any(category[0] in allowed_groups for category in categories)


def _expect(condition: bool, path: str, message: str) -> None:
    if not condition:
        raise LedgerError(f"{path}: {message}")


def _unique(rows: list[dict[str, Any]], field: str, path: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        value = row.get(field)
        _expect(isinstance(value, str) and value, f"{path}[{index}].{field}", "must be non-empty")
        _expect(value not in result, f"{path}[{index}].{field}", f"duplicate {value!r}")
        result[value] = row
    return result


def _validate_stance_authorization(
    plan: dict[str, Any], consent: dict[str, Any]
) -> None:
    stance_plan = plan.get("stance_plan")
    if consent["decision"] == "retrieval_plus_stance":
        _expect(
            consent["stance_classification_authorized"] is True,
            "consent.stance_classification_authorized",
            "retrieval_plus_stance requires an explicit true",
        )
        _expect(
            isinstance(stance_plan, dict),
            "stance_plan",
            "retrieval_plus_stance requires a stance_plan",
        )
        _expect(
            consent.get("stance_plan_sha256") == digest(stance_plan),
            "consent.stance_plan_sha256",
            "does not bind the stance_plan",
        )
        _expect(
            plan["authorized_content_classes"] == STANCE_CONTENT_CLASSES,
            "authorized_content_classes",
            "retrieval_plus_stance authorizes exactly the stance content classes",
        )
        for field in ("provider_identity", "model_identity"):
            _expect(
                has_visible_semantic_text(stance_plan[field], allow_symbols=True),
                f"stance_plan.{field}",
                "must contain visible semantic text after NFKC normalization",
            )
        if stance_plan["retention_state"] == "known":
            _expect(
                has_visible_semantic_text(
                    stance_plan["retention_reference"], allow_symbols=True
                ),
                "stance_plan.retention_reference",
                "known retention requires a semantically visible reference",
            )
        else:
            _expect(
                stance_plan["retention_reference"] is None,
                "stance_plan.retention_reference",
                "unknown retention requires a null reference",
            )
    else:
        _expect(
            consent["stance_classification_authorized"] is False,
            "consent.stance_classification_authorized",
            "retrieval_only must be false",
        )
        _expect(stance_plan is None, "stance_plan", "retrieval_only requires null")
        _expect(
            consent.get("stance_plan_sha256") is None,
            "consent.stance_plan_sha256",
            "retrieval_only requires null",
        )
        _expect(
            plan["authorized_content_classes"] == RETRIEVAL_ONLY_CONTENT_CLASSES,
            "authorized_content_classes",
            "retrieval_only authorizes exactly the accepted search queries",
        )


def validate_plan(plan: dict[str, Any]) -> None:
    _expect(
        plan.get("schema_version") in PLAN_SCHEMA_FILENAMES,
        "schema_version",
        f"must be one of {sorted(PLAN_SCHEMA_FILENAMES)}",
    )
    _expect(plan.get("caps") == CAPS, "caps", "must equal the frozen v1 ceilings")
    claim = plan["claim"]
    _expect(
        has_visible_semantic_text(claim["claim_text"], allow_symbols=True),
        "claim.claim_text",
        "must contain visible semantic text after NFKC normalization",
    )
    _expect(text_digest(claim["claim_text"]) == claim["claim_sha256"], "claim.claim_sha256", "does not bind exact claim text")
    checkpoint = claim["checkpoint"]
    tier = claim["registry_selection_tier"]
    _expect(
        CHECKPOINT_REQUIRED_TIER.get(checkpoint) == tier,
        "claim.registry_selection_tier",
        "must be HIGH-IMPACT at Stage 2.5 or ALL with explicit high-impact basis at Stage 4.5",
    )
    _expect(bool(claim["high_impact_basis"]), "claim.high_impact_basis", "must be explicit")
    queries = plan["queries"]
    roster = plan["provider_roster"]
    _expect(1 <= len(queries) <= MAX_QUERIES, "queries", "must contain 1..3 rows")
    _expect(1 <= len(roster) <= MAX_INDEXES, "provider_roster", "must contain 1..4 rows")
    _expect(
        plan.get("schema_version") == PLAN_VERSION_1_1
        or plan["authorized_content_classes"] == RETRIEVAL_ONLY_CONTENT_CLASSES,
        "authorized_content_classes",
        "Track A retrieval authorizes only accepted search-query text",
    )
    query_map = _unique(queries, "query_id", "queries")
    provider_map = _unique(roster, "index_id", "provider_roster")
    for index_id, provider in provider_map.items():
        for disclosure_field in (
            "product_identity",
            "query_capability",
            "pagination_behavior",
        ):
            disclosure = provider[disclosure_field]
            _expect(
                has_visible_semantic_text(disclosure, allow_symbols=True),
                f"provider_roster.{index_id}.{disclosure_field}",
                "must contain visible semantic provider disclosure text after NFKC normalization",
            )
        retention_state = provider["retention_state"]
        retention_reference = provider["retention_reference"]
        _expect(
            (
                retention_state == "known"
                and has_visible_semantic_text(
                    retention_reference, allow_symbols=True
                )
            )
            or (retention_state == "unknown" and retention_reference is None),
            f"provider_roster.{index_id}.retention_reference",
            "known retention requires visible semantic reference text after NFKC normalization; unknown requires null",
        )
    for query_id, query in query_map.items():
        for query_text_field in ("original_query_text", "accepted_query_text"):
            _expect(
                has_visible_semantic_text(
                    query[query_text_field], allow_symbols=True
                ),
                f"queries.{query_id}.{query_text_field}",
                "must contain visible semantic text after NFKC normalization",
            )
        _expect(query["source_claim_sha256"] == claim["claim_sha256"], f"queries.{query_id}.source_claim_sha256", "claim binding drifted")
        _expect(text_digest(query["accepted_query_text"]) == query["query_sha256"], f"queries.{query_id}.query_sha256", "does not bind accepted query text")
        if query["construction"] == "exact_claim":
            expected = exact_claim_query(claim["claim_text"])
            _expect(query["accepted_query_text"] == expected, f"queries.{query_id}.accepted_query_text", "exact_claim may only strip ARS markers and collapse ASCII whitespace")
        _expect(set(query["index_targets"]) <= set(provider_map), f"queries.{query_id}.index_targets", "names an index outside provider roster")
        dates = query["date_filter"]
        if dates["from_year"] is not None and dates["through_year"] is not None:
            _expect(dates["from_year"] <= dates["through_year"], f"queries.{query_id}.date_filter", "from_year exceeds through_year")
    consent = plan["consent"]
    if plan.get("schema_version") == PLAN_VERSION_1_1:
        _validate_stance_authorization(plan, consent)
    else:
        _expect(consent["decision"] == "retrieval_only", "consent.decision", "Track A accepts retrieval_only")
        _expect(consent["stance_classification_authorized"] is False, "consent.stance_classification_authorized", "must be false")
    for disclosure_field in ("deletion_boundary", "export_boundary"):
        _expect(
            has_visible_semantic_text(
                consent[disclosure_field], allow_symbols=True
            ),
            f"consent.{disclosure_field}",
            "must contain visible semantic disclosure text after NFKC normalization",
        )
    if consent["local_persistence"] == "explicit_local_export":
        _expect(
            consent["export_boundary"] == EXPLICIT_LOCAL_EXPORT_BOUNDARY,
            "consent.export_boundary",
            "explicit_local_export requires the exact closed local-export authorization boundary",
        )
        _expect(
            has_visible_semantic_text(
                consent.get("authorized_output_path"), allow_symbols=True
            ),
            "consent.authorized_output_path",
            "explicit_local_export requires one hash-bound operator-named output path",
        )
        _expect(
            Path(consent["authorized_output_path"]).is_absolute(),
            "consent.authorized_output_path",
            "must be an absolute path so its target cannot vary by working directory",
        )
        _expect(
            not consent["authorized_output_path"].endswith(("/", "\\")),
            "consent.authorized_output_path",
            "must not end with a path separator: derived artifact names would become hidden dotfiles",
        )
    else:
        _expect(
            consent.get("authorized_output_path") is None,
            "consent.authorized_output_path",
            "session_only must not authorize an output path",
        )
    bindings = {
        "claim_sha256": claim["claim_sha256"],
        "provider_roster_sha256": digest(roster),
        "caps_sha256": digest(plan["caps"]),
        "queries_sha256": digest(queries),
    }
    for field, expected in bindings.items():
        _expect(consent[field] == expected, f"consent.{field}", "consent binding drifted")
    _expect(
        consent["consentable_plan_sha256"]
        == digest(consentable_plan_projection(plan)),
        "consent.consentable_plan_sha256",
        "does not bind the complete consentable plan projection",
    )
    _expect(consent["receipt_sha256"] == bound_digest(consent, "receipt_sha256"), "consent.receipt_sha256", "does not bind receipt")
    _expect(plan["plan_sha256"] == bound_digest(plan, "plan_sha256"), "plan_sha256", "does not bind plan")
    _expect(
        parse_rfc3339(plan["created_at"], "created_at")
        <= parse_rfc3339(consent["accepted_at"], "consent.accepted_at"),
        "consent.accepted_at",
        "must not precede plan creation",
    )


def validate_input(plan: dict[str, Any], retained: dict[str, Any]) -> None:
    _expect(retained.get("schema_version") == INPUT_VERSION, "retrieval_input.schema_version", f"must equal {INPUT_VERSION}")
    _expect(retained["query_plan_sha256"] == plan["plan_sha256"], "retrieval_input.query_plan_sha256", "plan binding drifted")
    _expect(len(retained["raw_hits"]) <= MAX_RAW_HITS, "raw_hits", "exceeds 240")
    query_map = {row["query_id"]: row for row in plan["queries"]}
    provider_ids = {row["index_id"] for row in plan["provider_roster"]}
    attempts = _unique(retained["attempts"], "attempt_id", "attempts")
    hits = _unique(retained["raw_hits"], "raw_hit_id", "raw_hits")
    retry_receipts = _unique(
        retained["retry_authorizations"],
        "retry_authorization_receipt_id",
        "retry_authorizations",
    )
    consent_id = plan["consent"]["consent_receipt_id"]
    plan_completed = parse_rfc3339(retained["completed_at"], "completed_at")
    consent_accepted = parse_rfc3339(
        plan["consent"]["accepted_at"], "consent.accepted_at"
    )
    root_attempts: Counter[tuple[str, str]] = Counter()
    retry_authorizations: set[str] = set()
    hits_by_attempt: Counter[str] = Counter()
    ranks_by_attempt: dict[str, set[int]] = {}
    attempt_times: dict[str, tuple[datetime, datetime]] = {}
    hit_returned_times: dict[str, datetime] = {}
    for attempt_id, attempt in attempts.items():
        _expect(attempt["query_id"] in query_map, f"attempts.{attempt_id}.query_id", "unknown query")
        _expect(attempt["index_id"] in query_map[attempt["query_id"]]["index_targets"], f"attempts.{attempt_id}.index_id", "not targeted by query")
        _expect(attempt["index_id"] in provider_ids, f"attempts.{attempt_id}.index_id", "outside roster")
        _expect(attempt["consent_receipt_id"] == consent_id, f"attempts.{attempt_id}.consent_receipt_id", "consent drifted")
        started = parse_rfc3339(
            attempt["started_at"], f"attempts.{attempt_id}.started_at"
        )
        completed = parse_rfc3339(
            attempt["completed_at"], f"attempts.{attempt_id}.completed_at"
        )
        _expect(
            consent_accepted <= started <= completed <= plan_completed,
            f"attempts.{attempt_id}",
            "must satisfy consent accepted <= start <= completion <= input completion",
        )
        attempt_times[attempt_id] = (started, completed)
        retry = attempt["retry_of_attempt_id"]
        authorization = attempt["retry_authorization_receipt_id"]
        if retry is None:
            pair = (attempt["query_id"], attempt["index_id"])
            root_attempts[pair] += 1
            _expect(
                root_attempts[pair] == 1,
                f"attempts.{attempt_id}",
                "a query/index pair may have only one initial attempt; later attempts must name a retry",
            )
        _expect((retry is None) == (authorization is None), f"attempts.{attempt_id}", "retry and its fresh authorization must appear together")
        if retry is not None:
            _expect(retry in attempts and retry != attempt_id, f"attempts.{attempt_id}.retry_of_attempt_id", "must name another retained attempt")
            previous = attempts[retry]
            _expect(previous["outcome"] != "success", f"attempts.{attempt_id}.retry_of_attempt_id", "must name a failed attempt")
            _expect(
                (attempt["query_id"], attempt["index_id"])
                == (previous["query_id"], previous["index_id"]),
                f"attempts.{attempt_id}.retry_of_attempt_id",
                "retry must preserve the failed query/index pair",
            )
            _expect(
                authorization != consent_id,
                f"attempts.{attempt_id}.retry_authorization_receipt_id",
                "initial retrieval consent is not a fresh retry authorization",
            )
            _expect(
                authorization not in retry_authorizations,
                f"attempts.{attempt_id}.retry_authorization_receipt_id",
                "fresh retry authorization identifiers cannot be reused",
            )
            retry_authorizations.add(authorization)
        if attempt["outcome"] != "success":
            _expect(attempt["outcome"] in FAILURE_OUTCOMES, f"attempts.{attempt_id}.outcome", "unknown failure")
            _expect(attempt["returned_count"] == attempt["retained_hit_count"] == attempt["truncated_count"] == 0, f"attempts.{attempt_id}", "failed attempts carry zero hits and no fabricated source row")
    expected_root_pairs = {
        (query["query_id"], index_id)
        for query in plan["queries"]
        for index_id in query["index_targets"]
    }
    _expect(
        set(root_attempts) == expected_root_pairs,
        "attempts",
        "must contain exactly one initial attempt for every planned query/index target pair",
    )
    _expect(
        retry_authorizations == set(retry_receipts),
        "retry_authorizations",
        "must contain exactly one retained receipt for every retry and no unused receipts",
    )
    for receipt_id, receipt in retry_receipts.items():
        _expect(
            receipt["query_plan_sha256"] == plan["plan_sha256"],
            f"retry_authorizations.{receipt_id}.query_plan_sha256",
            "plan binding drifted",
        )
        _expect(
            receipt["probe_id"] == plan["probe_id"],
            f"retry_authorizations.{receipt_id}.probe_id",
            "probe binding drifted",
        )
        _expect(
            receipt["consent_receipt_id"] == consent_id,
            f"retry_authorizations.{receipt_id}.consent_receipt_id",
            "initial consent binding drifted",
        )
        failed_id = receipt["failed_attempt_id"]
        _expect(
            failed_id in attempts and attempts[failed_id]["outcome"] != "success",
            f"retry_authorizations.{receipt_id}.failed_attempt_id",
            "must bind a retained failed attempt",
        )
        failed = attempts[failed_id]
        _expect(
            (receipt["query_id"], receipt["index_id"])
            == (failed["query_id"], failed["index_id"]),
            f"retry_authorizations.{receipt_id}",
            "query/index pair differs from failed attempt",
        )
        _expect(
            receipt["receipt_sha256"] == bound_digest(receipt, "receipt_sha256"),
            f"retry_authorizations.{receipt_id}.receipt_sha256",
            "does not bind retry authorization receipt",
        )
    for attempt_id in attempts:
        seen = {attempt_id}
        cursor = attempts[attempt_id]["retry_of_attempt_id"]
        while cursor is not None:
            _expect(cursor not in seen, f"attempts.{attempt_id}.retry_of_attempt_id", "retry graph contains a cycle")
            seen.add(cursor)
            cursor = attempts[cursor]["retry_of_attempt_id"]
    for hit_id, hit in hits.items():
        provider_record_id = hit["provider_record_id"]
        _expect(
            provider_record_id is None
            or has_visible_semantic_text(
                provider_record_id, allow_symbols=False
            ),
            f"raw_hits.{hit_id}.provider_record_id",
            "must be null or contain a visible letter or number after NFKC normalization",
        )
        doi = hit["doi"]
        _expect(
            doi is None or isinstance(doi, str),
            f"raw_hits.{hit_id}.doi",
            "must be null or a retained provider DOI string",
        )
        title = hit["title"]
        _expect(
            title is None
            or has_visible_semantic_text(title, allow_symbols=True),
            f"raw_hits.{hit_id}.title",
            "must be null or contain visible semantic text after NFKC normalization",
        )
        for author_index, author in enumerate(hit["authors"]):
            for author_field in ("family", "given"):
                author_value = author[author_field]
                _expect(
                    author_value is None
                    or has_visible_semantic_text(
                        author_value, allow_symbols=False
                    ),
                    f"raw_hits.{hit_id}.authors[{author_index}].{author_field}",
                    "must be null or contain a visible letter or number after NFKC normalization",
                )
        _expect(hit["probe_id"] == plan["probe_id"], f"raw_hits.{hit_id}.probe_id", "probe drifted")
        _expect(hit["attempt_id"] in attempts, f"raw_hits.{hit_id}.attempt_id", "unknown attempt")
        attempt = attempts[hit["attempt_id"]]
        _expect(attempt["outcome"] == "success", f"raw_hits.{hit_id}.attempt_id", "failed attempts cannot own source rows")
        _expect((hit["query_id"], hit["index_id"]) == (attempt["query_id"], attempt["index_id"]), f"raw_hits.{hit_id}", "query/index differ from attempt")
        ranks = ranks_by_attempt.setdefault(hit["attempt_id"], set())
        _expect(hit["provider_rank"] not in ranks, f"raw_hits.{hit_id}.provider_rank", "duplicate within attempt")
        ranks.add(hit["provider_rank"])
        hits_by_attempt[hit["attempt_id"]] += 1
        if hit["abstract_state"] == "available":
            _expect(
                has_visible_semantic_text(
                    hit["abstract_text"], allow_symbols=True
                ),
                f"raw_hits.{hit_id}.abstract_text",
                "available abstract must contain visible semantic text after NFKC normalization",
            )
            _expect(hit["abstract_sha256"] == text_digest(hit["abstract_text"]), f"raw_hits.{hit_id}.abstract_sha256", "does not bind abstract")
        else:
            _expect(hit["abstract_text"] is None and hit["abstract_sha256"] is None, f"raw_hits.{hit_id}.abstract", "missing/not-returned abstract must be null")
        relation = hit["explicit_version_of_raw_hit_id"]
        if relation is not None:
            _expect(relation in hits and relation != hit_id, f"raw_hits.{hit_id}.explicit_version_of_raw_hit_id", "must name another hit")
        returned = parse_rfc3339(
            hit["returned_at"], f"raw_hits.{hit_id}.returned_at"
        )
        hit_returned_times[hit_id] = returned
        started, completed = attempt_times[hit["attempt_id"]]
        _expect(
            started <= returned <= completed,
            f"raw_hits.{hit_id}.returned_at",
            "must fall within its owning attempt",
        )
    for attempt_id, attempt in attempts.items():
        _expect(hits_by_attempt[attempt_id] == attempt["retained_hit_count"], f"attempts.{attempt_id}.retained_hit_count", "does not equal retained source rows")
        _expect(attempt["retained_hit_count"] <= MAX_HITS_PER_QUERY_INDEX, f"attempts.{attempt_id}.retained_hit_count", "exceeds 20")
        _expect(attempt["returned_count"] == attempt["retained_hit_count"] + attempt["truncated_count"], f"attempts.{attempt_id}", "returned count must partition retained and truncated")
        if attempt["provider_reported_count"] is not None:
            _expect(attempt["provider_reported_count"] >= attempt["returned_count"], f"attempts.{attempt_id}.provider_reported_count", "cannot be below returned count")
    pair_counts = Counter((hit["query_id"], hit["index_id"]) for hit in hits.values())
    for (query_id, index_id), count in pair_counts.items():
        _expect(
            count <= MAX_HITS_PER_QUERY_INDEX,
            f"raw_hits.{query_id}.{index_id}",
            "exceeds the aggregate 20-hit query/index ceiling across attempts",
        )
    for index, relation in enumerate(retained["researcher_confirmed_version_relations"]):
        left, right = relation["left_raw_hit_id"], relation["right_raw_hit_id"]
        _expect(left in hits and right in hits and left != right, f"researcher_confirmed_version_relations[{index}]", "must name two distinct retained hits")
    for attempt_id, attempt in attempts.items():
        receipt_id = attempt["retry_authorization_receipt_id"]
        if receipt_id is None:
            continue
        receipt = retry_receipts[receipt_id]
        _expect(
            receipt["failed_attempt_id"] == attempt["retry_of_attempt_id"],
            f"attempts.{attempt_id}.retry_authorization_receipt_id",
            "receipt must bind this retry's failed attempt",
        )
        _expect(
            (receipt["query_id"], receipt["index_id"])
            == (attempt["query_id"], attempt["index_id"]),
            f"attempts.{attempt_id}.retry_authorization_receipt_id",
            "receipt must bind this retry's query/index pair",
        )
        authorized = parse_rfc3339(
            receipt["accepted_at"],
            f"retry_authorizations.{receipt_id}.accepted_at",
        )
        failed_completed = attempt_times[attempt["retry_of_attempt_id"]][1]
        retry_started = attempt_times[attempt_id][0]
        _expect(
            failed_completed < authorized < retry_started,
            f"retry_authorizations.{receipt_id}.accepted_at",
            "must be later than the failed attempt and earlier than the retry",
        )
    for index, assessment in enumerate(retained["relevance_assessments"]):
        assessed_raw_hit_id = assessment["canonical_raw_hit_id"]
        _expect(
            assessed_raw_hit_id in hits,
            f"relevance_assessments[{index}].canonical_raw_hit_id",
            "must name a retained raw hit",
        )
        assessed = parse_rfc3339(
            assessment["assessed_at"], f"relevance_assessments[{index}].assessed_at"
        )
        _expect(
            hit_returned_times[assessed_raw_hit_id] <= assessed <= plan_completed,
            f"relevance_assessments[{index}].assessed_at",
            "must not precede its candidate return or exceed input completion",
        )
        raw_output = assessment["raw_output"]
        raw_output_sha256 = assessment["raw_output_sha256"]
        assessment_projection = relevance_assessment_input_projection(
            plan, hits[assessed_raw_hit_id], assessment
        )
        _expect(
            assessment["assessment_input_sha256"] == digest(assessment_projection),
            f"relevance_assessments[{index}].assessment_input_sha256",
            "does not bind exact claim, candidate, and assessor contract",
        )
        expected_prompt = render_relevance_prompt(assessment_projection)
        _expect(
            assessment["prompt_utf8"] == expected_prompt,
            f"relevance_assessments[{index}].prompt_utf8",
            "does not equal the canonical relevance prompt",
        )
        _expect(
            assessment["prompt_sha256"] == text_digest(expected_prompt),
            f"relevance_assessments[{index}].prompt_sha256",
            "does not bind exact prompt UTF-8 bytes",
        )
        if raw_output is None:
            _expect(
                raw_output_sha256 is None,
                f"relevance_assessments[{index}].raw_output_sha256",
                "must be null when raw_output is null",
            )
        else:
            _expect(
                raw_output_sha256 == text_digest(raw_output),
                f"relevance_assessments[{index}].raw_output_sha256",
                "does not bind retained raw output",
            )
        if assessment["outcome"] == "success":
            _expect(
                assessment["state"] != "not_checked",
                f"relevance_assessments[{index}].state",
                "successful assessment must have a checked relevance state",
            )
            _expect(
                has_visible_semantic_text(raw_output, allow_symbols=True),
                f"relevance_assessments[{index}].raw_output",
                "successful assessment must retain visible semantic raw output after NFKC normalization",
            )
            _expect(
                has_visible_semantic_text(
                    assessment["rationale"], allow_symbols=True
                ),
                f"relevance_assessments[{index}].rationale",
                "successful assessment must retain visible semantic rationale text after NFKC normalization",
            )
            _expect(
                assessment["failure_code"] is None
                and assessment["failure_detail"] is None,
                f"relevance_assessments[{index}].failure",
                "successful assessment cannot carry failure fields",
            )
        else:
            _expect(
                assessment["state"] == "not_checked",
                f"relevance_assessments[{index}].state",
                "failed assessment must finalize as not_checked",
            )
            _expect(
                assessment["reason_code"] is None
                and assessment["rationale"] is None,
                f"relevance_assessments[{index}]",
                "failed assessment cannot invent relevance rationale",
            )
            _expect(
                assessment["failure_code"] is not None
                and has_visible_semantic_text(
                    assessment["failure_detail"], allow_symbols=True
                ),
                f"relevance_assessments[{index}].failure",
                "failed assessment must retain a failure code and visible semantic detail after NFKC normalization",
            )
    _expect(retained["retrieval_input_sha256"] == bound_digest(retained, "retrieval_input_sha256"), "retrieval_input_sha256", "does not bind input")


def normalize_doi(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        normalized = unicodedata.normalize("NFKC", value).strip()
        normalized = _DOI_PREFIX_RE.sub("", normalized).strip().casefold()
        match = _DOI_BODY_RE.fullmatch(normalized)
        if match is None:
            return None
        suffix = match.group(1)
        categories = [unicodedata.category(char) for char in suffix]
    except (TypeError, UnicodeError):
        return None
    if any(
        category[0] in {"C", "Z"} or char.isspace()
        for char, category in zip(suffix, categories)
    ):
        return None
    if not any(category[0] in {"L", "N"} for category in categories):
        return None
    return normalized


def normalize_provider_record_id(value: str | None) -> str | None:
    if value is None or not has_visible_semantic_text(value, allow_symbols=False):
        return None
    return unicodedata.normalize("NFKC", value).strip() or None


def normalize_author_family(value: str | None) -> str | None:
    if value is None or not has_visible_semantic_text(value, allow_symbols=False):
        return None
    normalized = unicodedata.normalize("NFKC", value).casefold().strip()
    return normalized or None


def normalize_title(value: str | None) -> str | None:
    if value is None or not has_visible_semantic_text(value, allow_symbols=True):
        return None
    text = unicodedata.normalize("NFKC", value).casefold()
    text = "".join(
        " " if unicodedata.category(char)[0] in {"C", "P", "Z"} else char
        for char in text
    )
    return _ASCII_WS_RE.sub(" ", text).strip() or None


def _canonical_key(hit: dict[str, Any]) -> tuple[Any, ...]:
    status = {"published": 0, "preprint": 1, "other": 2, "unknown": 3}[hit["publication_status"]]
    return (
        status,
        0 if normalize_doi(hit["doi"]) else 1,
        0 if hit["abstract_state"] == "available" else 1,
        hit["provider_rank"],
        hit["index_id"],
        normalize_provider_record_id(hit["provider_record_id"]) or "",
        hit["raw_hit_id"],
    )


def _union_find(ids: list[str]) -> tuple[dict[str, str], Any]:
    parent = {value: value for value in ids}

    def find(value: str) -> str:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: str, right: str) -> None:
        a, b = find(left), find(right)
        if a != b:
            parent[max(a, b)] = min(a, b)

    return parent, (find, union)


def build_ledger(plan: dict[str, Any], retained: dict[str, Any]) -> dict[str, Any]:
    validate_schema(plan, plan_schema_filename(plan), "query plan")
    validate_schema(retained, "retrieval_input.schema.json", "retrieval input")
    validate_plan(plan)
    validate_input(plan, retained)
    query_order = {row["query_id"]: index for index, row in enumerate(plan["queries"])}
    query_map = {row["query_id"]: row for row in plan["queries"]}
    final_rows = [copy.deepcopy(row) for row in retained["raw_hits"]]
    by_id = {row["raw_hit_id"]: row for row in final_rows}
    eligible: list[dict[str, Any]] = []
    for row in final_rows:
        row.update(terminal_state=None, work_family_id=None, retained_raw_hit_id=None)
        stable = bool(
            normalize_provider_record_id(row["provider_record_id"])
            or normalize_doi(row["doi"])
        )
        if normalize_title(row["title"]) is None and not stable:
            row["terminal_state"] = "missing_title_and_stable_id"
            continue
        dates = query_map[row["query_id"]]["date_filter"]
        if row["year"] is not None and (
            (dates["from_year"] is not None and row["year"] < dates["from_year"])
            or (dates["through_year"] is not None and row["year"] > dates["through_year"])
        ):
            row["terminal_state"] = "outside_date_range"
            continue
        if row["language"] not in set(plan["allowed_languages"]):
            row["terminal_state"] = "outside_language_set"
            continue
        if row["document_type"] not in set(plan["allowed_document_types"]):
            row["terminal_state"] = "outside_document_type"
            continue
        eligible.append(row)
    eligible.sort(key=lambda row: row["raw_hit_id"])
    ids = [row["raw_hit_id"] for row in eligible]
    _, (find, union) = _union_find(ids)
    # Strong relations are applied first. They may intentionally preserve an
    # explicit provider relation even when provider DOI metadata disagrees.
    for left, right in combinations(eligible, 2):
        left_id, right_id = left["raw_hit_id"], right["raw_hit_id"]
        left_doi, right_doi = normalize_doi(left["doi"]), normalize_doi(right["doi"])
        if left_doi and left_doi == right_doi:
            union(left_id, right_id)
            continue
        explicitly_related = (
            left["explicit_version_of_raw_hit_id"] == right_id
            or right["explicit_version_of_raw_hit_id"] == left_id
        )
        if explicitly_related:
            union(left_id, right_id)

    def weak_key(row: dict[str, Any]) -> tuple[str, int, str] | None:
        title = normalize_title(row["title"])
        first_family = (
            normalize_author_family(row["authors"][0]["family"])
            if row["authors"]
            else None
        )
        if title is None or row["year"] is None or first_family is None:
            return None
        return (title, row["year"], first_family)

    weak_groups: dict[tuple[str, int, str], list[str]] = {}
    for row in eligible:
        key = weak_key(row)
        if key is not None:
            weak_groups.setdefault(key, []).append(row["raw_hit_id"])
    for member_ids in weak_groups.values():
        roots = sorted({find(member_id) for member_id in member_ids})
        root_dois: dict[str, set[str]] = {root: set() for root in roots}
        for row in eligible:
            root = find(row["raw_hit_id"])
            if root not in root_dois:
                continue
            doi = normalize_doi(row["doi"])
            if doi:
                root_dois[root].add(doi)
        distinct_dois = set().union(*(root_dois[root] for root in roots))
        if len(distinct_dois) <= 1:
            for root in roots[1:]:
                union(roots[0], root)
        else:
            # A metadata-only record that weakly matches two distinct DOI
            # components is ambiguous. Keep it separate rather than allowing
            # transitive union to bridge the DOI families.
            no_doi_roots = [root for root in roots if not root_dois[root]]
            for root in no_doi_roots[1:]:
                union(no_doi_roots[0], root)
    for relation in retained["researcher_confirmed_version_relations"]:
        left, right = relation["left_raw_hit_id"], relation["right_raw_hit_id"]
        if left in ids and right in ids:
            left_title = normalize_title(by_id[left]["title"])
            right_title = normalize_title(by_id[right]["title"])
            _expect(
                left_title is not None and left_title == right_title,
                "researcher_confirmed_version_relations",
                "confirmation requires equal non-empty normalized titles",
            )
            union(left, right)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in eligible:
        grouped.setdefault(find(row["raw_hit_id"]), []).append(row)
    assessments = _unique(retained["relevance_assessments"], "canonical_raw_hit_id", "relevance_assessments")
    families: list[dict[str, Any]] = []
    for members in grouped.values():
        members.sort(key=_canonical_key)
        canonical = members[0]
        assessment = assessments.get(canonical["raw_hit_id"])
        _expect(assessment is not None, f"relevance_assessments.{canonical['raw_hit_id']}", "one explicit assessment is required per canonical family")
        if assessment["state"] == "not_relevant":
            _expect(assessment["reason_code"] is not None, f"relevance_assessments.{canonical['raw_hit_id']}.reason_code", "not_relevant requires a mismatch reason")
        else:
            _expect(assessment["reason_code"] is None, f"relevance_assessments.{canonical['raw_hit_id']}.reason_code", "relevant/ambiguous reason_code must be null")
        member_ids = sorted(row["raw_hit_id"] for row in members)
        family_id = "CSF-" + digest(member_ids)[:16]
        for row in members:
            row["work_family_id"] = family_id
            if row is not canonical:
                row["terminal_state"] = "duplicate_version"
                row["retained_raw_hit_id"] = canonical["raw_hit_id"]
        coverage = "abstract" if canonical["abstract_state"] == "available" else "metadata_only"
        state = "available" if coverage == "abstract" else "abstract_missing"
        families.append(
            {
                "work_family_id": family_id,
                "member_raw_hit_ids": member_ids,
                "canonical_raw_hit_id": canonical["raw_hit_id"],
                "query_ids": sorted({row["query_id"] for row in members}, key=query_order.__getitem__),
                "index_ids": sorted({row["index_id"] for row in members}),
                "relevance": copy.deepcopy(assessment),
                "selection_state": None,
                "coverage": coverage,
                "content_state": state,
                "content_sha256": canonical["abstract_sha256"] if coverage == "abstract" else None,
                "sharing_scope": plan["consent"]["local_persistence"],
                "rights_basis": "not_assessed",
            }
        )
    _expect(set(assessments) == {row["canonical_raw_hit_id"] for row in families}, "relevance_assessments", "must contain exactly one row per computed canonical family")
    candidates = [row for row in families if row["relevance"]["state"] in {"relevant", "ambiguous"}]
    candidates.sort(
        key=lambda family: (
            0 if family["relevance"]["state"] == "relevant" else 1,
            min(by_id[row_id]["provider_rank"] for row_id in family["member_raw_hit_ids"]),
            min(query_order[by_id[row_id]["query_id"]] for row_id in family["member_raw_hit_ids"]),
            by_id[family["canonical_raw_hit_id"]]["index_id"],
            by_id[family["canonical_raw_hit_id"]]["provider_record_id"] or "",
            family["work_family_id"],
        )
    )
    selected_ids = {row["work_family_id"] for row in candidates[:MAX_SELECTED]}
    for family in families:
        canonical = by_id[family["canonical_raw_hit_id"]]
        if family["relevance"]["state"] == "not_relevant":
            family["selection_state"] = canonical["terminal_state"] = "not_relevant"
        elif family["relevance"]["state"] == "not_checked":
            family["selection_state"] = canonical["terminal_state"] = "not_checked"
        elif family["work_family_id"] in selected_ids:
            family["selection_state"] = canonical["terminal_state"] = "selected"
        else:
            family["selection_state"] = canonical["terminal_state"] = "candidate_cap_exceeded"
    families.sort(key=lambda row: row["work_family_id"])
    state_counts = Counter(row["terminal_state"] for row in final_rows)
    failure_counts = Counter(row["outcome"] for row in retained["attempts"] if row["outcome"] != "success")
    ledger = {
        "schema_version": LEDGER_VERSION,
        "probe_id": plan["probe_id"],
        "query_plan_sha256": plan["plan_sha256"],
        "claim_sha256": plan["claim"]["claim_sha256"],
        "adapter_registry_sha256": digest(plan["provider_roster"]),
        "local_persistence": plan["consent"]["local_persistence"],
        "export_boundary": plan["consent"]["export_boundary"],
        "authorized_output_path": plan["consent"].get("authorized_output_path"),
        "retrieval_input_sha256": retained["retrieval_input_sha256"],
        "attempts": copy.deepcopy(retained["attempts"]),
        "retry_authorizations": copy.deepcopy(retained["retry_authorizations"]),
        "raw_hits": final_rows,
        "researcher_confirmed_version_relations": copy.deepcopy(retained["researcher_confirmed_version_relations"]),
        "work_families": families,
        "counts": {
            "attempts": len(retained["attempts"]),
            "successful_attempts": sum(row["outcome"] == "success" for row in retained["attempts"]),
            "failed_attempts": sum(row["outcome"] != "success" for row in retained["attempts"]),
            "raw_hits": len(final_rows),
            "work_families": len(families),
            "selected_work_families": len(selected_ids),
            "raw_hit_state_counts": {state: state_counts[state] for state in RAW_TERMINAL_STATES},
            "attempt_failure_counts": {state: failure_counts[state] for state in sorted(FAILURE_OUTCOMES)},
        },
        "completed_at": retained["completed_at"],
        "candidate_ledger_sha256": "",
    }
    ledger["candidate_ledger_sha256"] = bound_digest(ledger, "candidate_ledger_sha256")
    validate_schema(ledger, "candidate_ledger.schema.json", "candidate ledger")
    return ledger


def validate_ledger(plan: dict[str, Any], retained: dict[str, Any], ledger: dict[str, Any]) -> None:
    expected = build_ledger(plan, retained)
    _expect(ledger == expected, "candidate_ledger", "does not exactly replay from named plan and retrieval input")


def write_new_ledger(path: Path, value: dict[str, Any]) -> None:
    descriptor: int | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if os.name != "nt":
            flags |= os.O_NOFOLLOW
        descriptor = os.open(path, flags, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            descriptor = None
            handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        if os.name != "nt":
            directory_descriptor = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_descriptor)
            finally:
                os.close(directory_descriptor)
    except FileExistsError as exc:
        raise LedgerError("output: refuses to overwrite an existing path") from exc
    except (OSError, UnicodeError) as exc:
        raise LedgerError(f"output: cannot write new ledger: {exc}") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)


def authorized_export_path(plan: dict[str, Any], suffix: str) -> Path:
    """The only writable path for a consent-derived artifact of this probe."""
    authorized = plan["consent"]["authorized_output_path"]
    if not isinstance(authorized, str) or not authorized:
        raise LedgerError(
            "consent.authorized_output_path: no operator-named output path is "
            "bound by this receipt"
        )
    if authorized.endswith(("/", "\\")):
        raise LedgerError(
            "consent.authorized_output_path: a trailing path separator would "
            "derive a hidden artifact name; name a file base, not a directory"
        )
    return Path(authorized + suffix)


def require_export_consent(
    plan: dict[str, Any], output: Path, suffix: str
) -> Path:
    """Fail closed unless the hash-bound consent authorizes exactly `output`."""
    if plan["consent"]["local_persistence"] != "explicit_local_export":
        raise LedgerError(
            "consent does not say explicit_local_export: refusing to create "
            "any output path"
        )
    authorized = authorized_export_path(plan, suffix)
    if str(output) != str(authorized):
        raise LedgerError(
            "output path must exactly match the consent-derived path "
            f"{str(authorized)!r}"
        )
    return authorized


def _parser() -> Any:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="write one new replayable ledger; never retrieve")
    build.add_argument("--query-plan", type=Path, required=True)
    build.add_argument("--retrieval-input", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    validate = sub.add_parser("validate", help="rebuild and compare one retained ledger")
    validate.add_argument("--query-plan", type=Path, required=True)
    validate.add_argument("--retrieval-input", type=Path, required=True)
    validate.add_argument("--candidate-ledger", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        plan = load_json(args.query_plan)
        retained = load_json(args.retrieval_input)
        if args.command == "build":
            _expect(
                plan.get("consent", {}).get("local_persistence")
                == "explicit_local_export",
                "output",
                "local_persistence=session_only forbids writing a ledger; "
                "a separately consented explicit_local_export plan is required",
            )
            _expect(
                plan.get("consent", {}).get("authorized_output_path")
                == str(args.output),
                "output",
                "does not exactly match the hash-bound authorized_output_path",
            )
            ledger = build_ledger(plan, retained)
            write_new_ledger(args.output, ledger)
            print(f"PASS: wrote {args.output}")
        else:
            validate_ledger(plan, retained, load_json(args.candidate_ledger))
            print("PASS: candidate ledger exactly replays")
    except (LedgerError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
