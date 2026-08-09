#!/usr/bin/env python3
"""Resolve explicit human-subjects authority profiles without inferring jurisdiction.

The runtime is standard-library-only.  It reads only the paths named on the
command line, performs closed-contract and cross-row validation, and emits a
pointer-only applicability trace.  It is not a legal, compliance, pathway,
readiness, exemption, or authorization engine.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, NoReturn


AXES = ("review_ethics", "data_protection")
TRI = ("true", "false", "unknown")
OPS = ("fact_equals", "fact_in", "fact_contains", "all", "any", "not")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
HTTPS_RE = re.compile(r"^https://[^\s\x00-\x1f\x7f]+$")
MAX_JSON_BYTES = 8 * 1024 * 1024
MAX_ITEMS = 4096
MAX_AST_DEPTH = 16
MAX_AST_NODES = 512


class ContractError(ValueError):
    """An input violates the closed V1 contract."""


def _fail(path: str, message: str) -> NoReturn:
    raise ContractError(f"{path}: {message}")


def _reject_constant(value: str) -> NoReturn:
    raise ContractError(f"non-finite JSON number is not allowed: {value}")


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON key is not allowed: {key}")
        result[key] = value
    return result


def load_json(path: Path | str) -> dict[str, Any]:
    source = Path(path)
    try:
        if source.stat().st_size > MAX_JSON_BYTES:
            raise ContractError(f"JSON input exceeds {MAX_JSON_BYTES} bytes: {source}")
        with source.open("r", encoding="utf-8") as handle:
            value = json.load(
                handle,
                object_pairs_hook=_reject_duplicate_pairs,
                parse_constant=_reject_constant,
            )
    except ContractError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON input {source}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"top-level JSON value must be an object: {source}")
    return value


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _closed(value: Any, path: str, fields: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(path, "must be an object")
    missing = fields - set(value)
    extra = set(value) - fields
    if missing:
        _fail(path, f"missing field(s): {', '.join(sorted(missing))}")
    if extra:
        _fail(path, f"undeclared field(s): {', '.join(sorted(extra))}")
    return value


def _array(value: Any, path: str, *, maximum: int = MAX_ITEMS) -> list[Any]:
    if not isinstance(value, list):
        _fail(path, "must be an array")
    if len(value) > maximum:
        _fail(path, f"exceeds {maximum} items")
    return value


def _text(
    value: Any,
    path: str,
    *,
    nullable: bool = False,
    maximum: int | None = None,
) -> str | None:
    if nullable and value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        _fail(path, "must be a non-empty string" + (" or null" if nullable else ""))
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        _fail(path, "must not contain control characters")
    if maximum is not None and len(value) > maximum:
        _fail(path, f"must not exceed {maximum} characters")
    return value


def _identifier(value: Any, path: str) -> str:
    text = _text(value, path)
    assert text is not None
    if ID_RE.fullmatch(text) is None:
        _fail(path, "must use lowercase letters, digits, dot, underscore, or hyphen")
    return text


def _version(value: Any, path: str) -> str:
    text = _text(value, path)
    assert text is not None
    if VERSION_RE.fullmatch(text) is None:
        _fail(path, "has an invalid version token")
    return text


def _sha(value: Any, path: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    text = _text(value, path)
    assert text is not None
    if SHA_RE.fullmatch(text) is None:
        _fail(path, "must be 64 lowercase hexadecimal characters")
    return text


def _date(value: Any, path: str, *, nullable: bool = False) -> date | None:
    if nullable and value is None:
        return None
    text = _text(value, path)
    assert text is not None
    try:
        if len(text) != 10:
            raise ValueError
        return date.fromisoformat(text)
    except ValueError as exc:
        raise ContractError(f"{path}: must be a real ISO 8601 date") from exc


def _datetime(value: Any, path: str) -> datetime:
    text = _text(value, path)
    assert text is not None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if "T" not in text or parsed.tzinfo is None:
            raise ValueError
        return parsed
    except ValueError as exc:
        raise ContractError(f"{path}: must be an ISO 8601 date-time with offset") from exc


def _https(value: Any, path: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    text = _text(value, path)
    assert text is not None
    if HTTPS_RE.fullmatch(text) is None:
        _fail(path, "must be a control-free HTTPS URL")
    return text


def _enum(value: Any, path: str, choices: tuple[str, ...] | set[str]) -> str:
    if value not in choices:
        _fail(path, f"must be one of: {', '.join(sorted(choices))}")
    return value


def _unique_texts(
    value: Any,
    path: str,
    *,
    identifiers: bool = False,
    minimum: int = 0,
    maximum: int = MAX_ITEMS,
) -> list[str]:
    rows = _array(value, path, maximum=maximum)
    if len(rows) < minimum:
        _fail(path, f"must contain at least {minimum} item(s)")
    result: list[str] = []
    for index, item in enumerate(rows):
        result.append(
            _identifier(item, f"{path}[{index}]")
            if identifiers
            else (_text(item, f"{path}[{index}]") or "")
        )
    if len(result) != len(set(result)):
        _fail(path, "must not contain duplicate values")
    return result


def _unique(values: list[Any], path: str) -> None:
    seen: set[Any] = set()
    for value in values:
        if value in seen:
            _fail(path, f"duplicate value: {value}")
        seen.add(value)


def _validate_fact_value(value_type: str, value: Any, path: str) -> None:
    if value_type == "boolean":
        if not isinstance(value, bool):
            _fail(path, "must be a boolean")
        return
    if value_type in {"string", "string_enum"}:
        _text(value, path, maximum=512)
        return
    if value_type == "date":
        _date(value, path)
        return
    if value_type == "string_set":
        rows = _array(value, path, maximum=128)
        normalized = [
            _text(item, f"{path}[{index}]", maximum=256)
            for index, item in enumerate(rows)
        ]
        if len(normalized) != len(set(normalized)):
            _fail(path, "must not contain duplicate values")
        return
    _fail(path, f"unknown fact value type: {value_type}")


def _validate_predicate(
    value: Any,
    definitions: dict[str, dict[str, Any]],
    path: str,
    *,
    depth: int = 0,
    counter: list[int] | None = None,
) -> None:
    if counter is None:
        counter = [0]
    counter[0] += 1
    if counter[0] > MAX_AST_NODES:
        _fail(path, f"predicate exceeds {MAX_AST_NODES} nodes")
    if depth > MAX_AST_DEPTH:
        _fail(path, f"predicate exceeds depth {MAX_AST_DEPTH}")
    if not isinstance(value, dict):
        _fail(path, "predicate must be an object")
    op = _enum(value.get("op"), f"{path}.op", set(OPS))
    if op in {"fact_equals", "fact_contains"}:
        row = _closed(value, path, {"op", "fact_id", "value"})
        fact_id = _identifier(row["fact_id"], f"{path}.fact_id")
        if fact_id not in definitions:
            _fail(f"{path}.fact_id", f"unknown fact definition: {fact_id}")
        fact_type = definitions[fact_id]["value_type"]
        if op == "fact_contains":
            if fact_type != "string_set":
                _fail(path, "fact_contains requires a string_set fact")
            _text(row["value"], f"{path}.value", maximum=256)
        else:
            if fact_type == "string_set":
                _fail(path, "fact_equals is for scalar facts; use fact_contains for string_set")
            _validate_fact_value(fact_type, row["value"], f"{path}.value")
        allowed = definitions[fact_id]["allowed_values"]
        if allowed is not None and row["value"] not in allowed:
            _fail(f"{path}.value", "is outside the fact allowlist")
        return
    if op == "fact_in":
        row = _closed(value, path, {"op", "fact_id", "values"})
        fact_id = _identifier(row["fact_id"], f"{path}.fact_id")
        if fact_id not in definitions:
            _fail(f"{path}.fact_id", f"unknown fact definition: {fact_id}")
        fact_type = definitions[fact_id]["value_type"]
        if fact_type == "string_set":
            _fail(path, "fact_in is for scalar facts; use fact_contains for string_set")
        values = _array(row["values"], f"{path}.values", maximum=64)
        if not values:
            _fail(f"{path}.values", "must not be empty")
        for index, item in enumerate(values):
            _validate_fact_value(fact_type, item, f"{path}.values[{index}]")
        if len({_canonical_bytes(item) for item in values}) != len(values):
            _fail(f"{path}.values", "must not contain duplicate values")
        allowed = definitions[fact_id]["allowed_values"]
        if allowed is not None and any(item not in allowed for item in values):
            _fail(f"{path}.values", "contains a value outside the fact allowlist")
        return
    if op in {"all", "any"}:
        row = _closed(value, path, {"op", "operands"})
        operands = _array(row["operands"], f"{path}.operands", maximum=64)
        if not operands:
            _fail(f"{path}.operands", "must not be empty")
        for index, operand in enumerate(operands):
            _validate_predicate(
                operand,
                definitions,
                f"{path}.operands[{index}]",
                depth=depth + 1,
                counter=counter,
            )
        return
    row = _closed(value, path, {"op", "operand"})
    _validate_predicate(
        row["operand"], definitions, f"{path}.operand", depth=depth + 1, counter=counter
    )


def _fact_map(facts: Any) -> dict[str, Any]:
    if isinstance(facts, list):
        return {row["fact_id"]: row for row in facts}
    if isinstance(facts, dict):
        return facts
    raise ContractError("facts: must be an object or declared-fact array")


def evaluate_predicate(
    predicate: dict[str, Any],
    facts: Any,
    definitions: dict[str, dict[str, Any]] | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Evaluate one closed predicate under Strong Kleene three-valued logic."""
    fact_rows = _fact_map(facts)
    if definitions is not None:
        _validate_predicate(predicate, definitions, "predicate")
    trace: list[dict[str, Any]] = []
    visited = 0

    def walk(node: dict[str, Any], pointer: str, depth: int) -> str:
        nonlocal visited
        visited += 1
        if visited > MAX_AST_NODES:
            _fail(pointer or "/", f"predicate exceeds {MAX_AST_NODES} nodes")
        display_pointer = pointer or "/"
        if not isinstance(node, dict):
            _fail(display_pointer, "predicate node must be an object")
        if depth > MAX_AST_DEPTH:
            _fail(display_pointer, f"predicate exceeds depth {MAX_AST_DEPTH}")
        op = node.get("op")
        if op not in OPS:
            _fail(f"{pointer}/op", "unknown predicate operator")
        fact_id: str | None = None
        declared_state = "compound"
        if op in {"fact_equals", "fact_in", "fact_contains"}:
            fact_id = node.get("fact_id")
            row = fact_rows.get(fact_id)
            if row is None:
                result, declared_state = "unknown", "missing"
            elif isinstance(row, dict) and "state" in row:
                declared_state = row.get("state")
                if declared_state != "declared" or row.get("value") is None:
                    result, declared_state = "unknown", "unknown"
                else:
                    actual = row["value"]
                    if op == "fact_equals":
                        if isinstance(actual, list):
                            _fail(display_pointer, "fact_equals cannot compare a string_set")
                        result = "true" if type(actual) is type(node.get("value")) and actual == node.get("value") else "false"
                    elif op == "fact_in":
                        if isinstance(actual, list):
                            _fail(display_pointer, "fact_in cannot inspect a string_set")
                        result = "true" if any(type(actual) is type(v) and actual == v for v in node.get("values", [])) else "false"
                    elif isinstance(actual, list):
                        result = "true" if node.get("value") in actual else "false"
                    else:
                        _fail(display_pointer, "fact_contains requires a string_set value")
            else:
                declared_state = "declared"
                actual = row
                if op == "fact_equals":
                    if isinstance(actual, list):
                        _fail(display_pointer, "fact_equals cannot compare a string_set")
                    result = "true" if type(actual) is type(node.get("value")) and actual == node.get("value") else "false"
                elif op == "fact_in":
                    if isinstance(actual, list):
                        _fail(display_pointer, "fact_in cannot inspect a string_set")
                    result = "true" if any(type(actual) is type(v) and actual == v for v in node.get("values", [])) else "false"
                elif isinstance(actual, list):
                    result = "true" if node.get("value") in actual else "false"
                else:
                    _fail(display_pointer, "fact_contains requires a string_set value")
        elif op in {"all", "any"}:
            children = [
                walk(child, f"{pointer}/operands/{index}", depth + 1)
                for index, child in enumerate(node.get("operands", []))
            ]
            if op == "all":
                result = "false" if "false" in children else ("unknown" if "unknown" in children else "true")
            else:
                result = "true" if "true" in children else ("unknown" if "unknown" in children else "false")
        else:
            child = walk(node.get("operand"), f"{pointer}/operand", depth + 1)
            result = {"true": "false", "false": "true", "unknown": "unknown"}[child]
        trace.append(
            {
                "expression_path": display_pointer,
                "operator": op,
                "result": result,
                "fact_id": fact_id,
                "declared_state": declared_state,
            }
        )
        return result

    result = walk(predicate, "", 0)
    if len(trace) > MAX_AST_NODES:
        _fail("predicate", f"exceeds {MAX_AST_NODES} nodes")
    return result, trace


SOURCE_FIELDS = {
    "source_id", "title", "publisher", "canonical_url", "snapshot_url",
    "provision_locator", "allowed_provisions", "effective_from", "effective_until",
    "source_amended_or_published_date", "retrieved_at", "verified_at",
    "source_language", "controlling_language", "authenticity_status",
    "content_digest", "digest_scope", "rights_status", "freshness",
}
ANCHOR_FIELDS = {
    "source_id", "authority_url", "snapshot_url", "provision", "effective_date",
    "effective_until", "source_amended_or_published_date", "retrieved_at",
    "verified_at", "source_language", "controlling_language",
    "authenticity_status", "content_digest", "digest_scope", "rights_status",
}


def _validate_source(row: Any, path: str, registry_as_of: date) -> None:
    obj = _closed(row, path, SOURCE_FIELDS)
    _identifier(obj["source_id"], f"{path}.source_id")
    _text(obj["title"], f"{path}.title")
    _text(obj["publisher"], f"{path}.publisher")
    _https(obj["canonical_url"], f"{path}.canonical_url")
    _https(obj["snapshot_url"], f"{path}.snapshot_url", nullable=True)
    _text(obj["provision_locator"], f"{path}.provision_locator")
    _unique_texts(obj["allowed_provisions"], f"{path}.allowed_provisions", minimum=1, maximum=128)
    start = _date(obj["effective_from"], f"{path}.effective_from")
    end = _date(obj["effective_until"], f"{path}.effective_until", nullable=True)
    _date(obj["source_amended_or_published_date"], f"{path}.source_amended_or_published_date", nullable=True)
    retrieved = _date(obj["retrieved_at"], f"{path}.retrieved_at")
    verified = _date(obj["verified_at"], f"{path}.verified_at")
    assert start is not None and retrieved is not None and verified is not None
    if end is not None and end < start:
        _fail(path, "effective_until precedes effective_from")
    if retrieved > registry_as_of or verified > registry_as_of:
        _fail(path, "retrieved_at/verified_at cannot be later than registry.as_of")
    _text(obj["source_language"], f"{path}.source_language")
    if not isinstance(obj["controlling_language"], bool):
        _fail(f"{path}.controlling_language", "must be boolean")
    authenticity = _enum(
        obj["authenticity_status"],
        f"{path}.authenticity_status",
        {
            "authentic_official", "official_controlling_language",
            "authoritative_unofficial", "official_consolidated",
            "official_reference_translation",
        },
    )
    if authenticity == "official_reference_translation" and obj["controlling_language"]:
        _fail(path, "a reference translation cannot be controlling")
    _sha(obj["content_digest"], f"{path}.content_digest", nullable=True)
    digest_scope = _enum(obj["digest_scope"], f"{path}.digest_scope", {"official_representation", "metadata_only", "not_recorded"})
    if (obj["content_digest"] is None) != (digest_scope == "not_recorded"):
        _fail(path, "content_digest and digest_scope are inconsistent")
    _enum(obj["rights_status"], f"{path}.rights_status", {"link_only", "curator_summary_only", "redistribution_recorded"})
    _enum(obj["freshness"], f"{path}.freshness", {"current", "stale", "unverified", "superseded"})


def _validate_anchor(anchor: Any, source: dict[str, Any], path: str) -> None:
    obj = _closed(anchor, path, ANCHOR_FIELDS)
    _identifier(obj["source_id"], f"{path}.source_id")
    _https(obj["authority_url"], f"{path}.authority_url")
    _https(obj["snapshot_url"], f"{path}.snapshot_url", nullable=True)
    _text(obj["provision"], f"{path}.provision")
    effective = _date(obj["effective_date"], f"{path}.effective_date")
    end = _date(obj["effective_until"], f"{path}.effective_until", nullable=True)
    _date(obj["source_amended_or_published_date"], f"{path}.source_amended_or_published_date", nullable=True)
    _date(obj["retrieved_at"], f"{path}.retrieved_at")
    _date(obj["verified_at"], f"{path}.verified_at")
    _text(obj["source_language"], f"{path}.source_language")
    if not isinstance(obj["controlling_language"], bool):
        _fail(f"{path}.controlling_language", "must be boolean")
    _text(obj["authenticity_status"], f"{path}.authenticity_status")
    _sha(obj["content_digest"], f"{path}.content_digest", nullable=True)
    _enum(obj["digest_scope"], f"{path}.digest_scope", {"official_representation", "metadata_only", "not_recorded"})
    _enum(obj["rights_status"], f"{path}.rights_status", {"link_only", "curator_summary_only", "redistribution_recorded"})
    joins = {
        "source_id": "source_id", "authority_url": "canonical_url",
        "snapshot_url": "snapshot_url", "effective_until": "effective_until",
        "source_amended_or_published_date": "source_amended_or_published_date",
        "retrieved_at": "retrieved_at", "verified_at": "verified_at",
        "source_language": "source_language", "controlling_language": "controlling_language",
        "authenticity_status": "authenticity_status", "content_digest": "content_digest",
        "digest_scope": "digest_scope", "rights_status": "rights_status",
    }
    for anchor_key, source_key in joins.items():
        if obj[anchor_key] != source[source_key]:
            _fail(f"{path}.{anchor_key}", f"does not match source {source['source_id']}")
    start = date.fromisoformat(source["effective_from"])
    source_end = date.fromisoformat(source["effective_until"]) if source["effective_until"] else None
    assert effective is not None
    if effective != start:
        _fail(f"{path}.effective_date", "must equal the provision source's verified effective_from date")
    if obj["provision"] not in source["allowed_provisions"]:
        _fail(f"{path}.provision", "is not an allowed provision locator for the selected source")
    if end is not None and end < effective:
        _fail(f"{path}.effective_until", "precedes effective_date")


def _validate_requirement(
    row: Any,
    path: str,
    axis: str,
    definitions: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
    authority_source_ids: set[str],
) -> str:
    fields = {
        "requirement_id", "axis", "title", "summary", "obligation_kind",
        "obligated_actor", "consumer_scopes", "applies_if",
        "structured_expectations", "evidence_expected", "waiver_or_exception_route",
        "authoritative_decision_maker", "interaction", "authority_anchor",
    }
    obj = _closed(row, path, fields)
    requirement_id = _identifier(obj["requirement_id"], f"{path}.requirement_id")
    if obj["axis"] != axis:
        _fail(f"{path}.axis", "must match its profile or overlay axis")
    _text(obj["title"], f"{path}.title")
    _text(obj["summary"], f"{path}.summary")
    _enum(obj["obligation_kind"], f"{path}.obligation_kind", {"require", "prohibit", "condition", "information", "safeguard", "route"})
    _identifier(obj["obligated_actor"], f"{path}.obligated_actor")
    _unique_texts(obj["consumer_scopes"], f"{path}.consumer_scopes", identifiers=True, minimum=1)
    _validate_predicate(obj["applies_if"], definitions, f"{path}.applies_if")
    for index, expectation in enumerate(_array(obj["structured_expectations"], f"{path}.structured_expectations")):
        exp = _closed(expectation, f"{path}.structured_expectations[{index}]", {"field_id", "operator", "value"})
        _identifier(exp["field_id"], f"{path}.structured_expectations[{index}].field_id")
        _enum(exp["operator"], f"{path}.structured_expectations[{index}].operator", {"equals", "includes", "gte", "lte", "present"})
        value = exp["value"]
        if isinstance(value, float) and not math.isfinite(value):
            _fail(f"{path}.structured_expectations[{index}].value", "must be finite")
        if isinstance(value, dict):
            frac = _closed(value, f"{path}.structured_expectations[{index}].value", {"numerator", "denominator"})
            if isinstance(frac["numerator"], bool) or not isinstance(frac["numerator"], int) or frac["numerator"] < 0:
                _fail(path, "fraction numerator must be a non-negative integer")
            if isinstance(frac["denominator"], bool) or not isinstance(frac["denominator"], int) or frac["denominator"] < 1:
                _fail(path, "fraction denominator must be a positive integer")
        elif not isinstance(value, (bool, int, float, str)):
            _fail(path, "structured expectation has an unsupported value")
    evidence_ids: list[str] = []
    evidence = _array(obj["evidence_expected"], f"{path}.evidence_expected")
    if not evidence:
        _fail(f"{path}.evidence_expected", "must not be empty")
    for index, item in enumerate(evidence):
        ev = _closed(item, f"{path}.evidence_expected[{index}]", {"evidence_id", "held_by", "artifact_type", "description"})
        evidence_ids.append(_identifier(ev["evidence_id"], f"{path}.evidence_expected[{index}].evidence_id"))
        _identifier(ev["held_by"], f"{path}.evidence_expected[{index}].held_by")
        _identifier(ev["artifact_type"], f"{path}.evidence_expected[{index}].artifact_type")
        _text(ev["description"], f"{path}.evidence_expected[{index}].description")
    _unique(evidence_ids, f"{path}.evidence_expected")
    route = _closed(obj["waiver_or_exception_route"], f"{path}.waiver_or_exception_route", {"state", "requirement_ids", "decision_maker_role"})
    state = _enum(route["state"], f"{path}.waiver_or_exception_route.state", {"profiled", "external_authority_required", "not_profiled_in_bounded_profile", "not_applicable"})
    route_ids = _unique_texts(route["requirement_ids"], f"{path}.waiver_or_exception_route.requirement_ids", identifiers=True)
    if state == "profiled" and not route_ids:
        _fail(f"{path}.waiver_or_exception_route", "profiled routes require requirement_ids")
    if state != "profiled" and route_ids:
        _fail(f"{path}.waiver_or_exception_route", "only profiled routes may carry requirement_ids")
    if route["decision_maker_role"] is not None:
        _identifier(route["decision_maker_role"], f"{path}.waiver_or_exception_route.decision_maker_role")
    decision = _closed(obj["authoritative_decision_maker"], f"{path}.authoritative_decision_maker", {"role_id", "description"})
    _identifier(decision["role_id"], f"{path}.authoritative_decision_maker.role_id")
    if decision["role_id"] in {"ars", "model", "user"}:
        _fail(f"{path}.authoritative_decision_maker.role_id", "cannot assign authority to ARS, a model, or the user")
    _text(decision["description"], f"{path}.authoritative_decision_maker.description")
    interaction = _closed(obj["interaction"], f"{path}.interaction", {"collision_key", "policy"})
    if interaction["collision_key"] is not None:
        _identifier(interaction["collision_key"], f"{path}.interaction.collision_key")
    if interaction["policy"] != "parallel_authorities":
        _fail(f"{path}.interaction.policy", "must equal parallel_authorities")
    anchor = obj["authority_anchor"]
    if not isinstance(anchor, dict) or anchor.get("source_id") not in sources:
        _fail(f"{path}.authority_anchor.source_id", "must resolve to a registry source")
    if anchor["source_id"] not in authority_source_ids:
        _fail(f"{path}.authority_anchor.source_id", "must be declared by its profile or overlay source_ids")
    _validate_anchor(anchor, sources[anchor["source_id"]], f"{path}.authority_anchor")
    return requirement_id


def validate_registry(registry: dict[str, Any]) -> None:
    top = _closed(registry, "registry", {"schema_version", "registry_id", "registry_version", "as_of", "fact_definitions", "sources", "profiles", "overlays"})
    if top["schema_version"] != "human-subjects-authority-registry/1.0":
        _fail("registry.schema_version", "must equal human-subjects-authority-registry/1.0")
    _identifier(top["registry_id"], "registry.registry_id")
    _version(top["registry_version"], "registry.registry_version")
    registry_as_of = _date(top["as_of"], "registry.as_of")
    assert registry_as_of is not None
    definitions: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(_array(top["fact_definitions"], "registry.fact_definitions", maximum=512)):
        path = f"registry.fact_definitions[{index}]"
        obj = _closed(row, path, {"fact_id", "value_type", "allowed_values", "description"})
        fact_id = _identifier(obj["fact_id"], f"{path}.fact_id")
        if fact_id in definitions:
            _fail(f"{path}.fact_id", "duplicate fact id")
        value_type = _enum(obj["value_type"], f"{path}.value_type", {"boolean", "string", "string_enum", "string_set", "date"})
        allowed = obj["allowed_values"]
        if allowed is not None:
            allowed = _unique_texts(allowed, f"{path}.allowed_values", minimum=1, maximum=128)
        if value_type == "string_enum" and allowed is None:
            _fail(path, "string_enum requires allowed_values")
        if value_type != "string_enum" and allowed is not None:
            _fail(path, "allowed_values are only valid for string_enum")
        _text(obj["description"], f"{path}.description")
        definitions[fact_id] = obj
    sources: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(_array(top["sources"], "registry.sources", maximum=256)):
        _validate_source(row, f"registry.sources[{index}]", registry_as_of)
        source_id = row["source_id"]
        if source_id in sources:
            _fail(f"registry.sources[{index}].source_id", "duplicate source id")
        sources[source_id] = row
    profile_index: dict[tuple[str, str], dict[str, Any]] = {}
    profile_ids: set[str] = set()
    requirement_ids: list[str] = []
    profiles = _array(top["profiles"], "registry.profiles", maximum=128)
    for index, row in enumerate(profiles):
        path = f"registry.profiles[{index}]"
        fields = {"profile_id", "profile_version", "profile_digest", "axis", "authority_scope_ids", "title", "authority_level", "coverage_status", "covered_provisions", "known_exclusions", "known_gaps", "no_completeness_claim", "source_ids", "applies_if", "requirements"}
        obj = _closed(row, path, fields)
        profile_id = _identifier(obj["profile_id"], f"{path}.profile_id")
        profile_version = _version(obj["profile_version"], f"{path}.profile_version")
        if profile_id in profile_ids or (profile_id, profile_version) in profile_index:
            _fail(f"{path}.profile_id", "duplicate profile id/version")
        profile_ids.add(profile_id)
        axis = _enum(obj["axis"], f"{path}.axis", set(AXES))
        _sha(obj["profile_digest"], f"{path}.profile_digest")
        unsigned = copy.deepcopy(obj)
        declared_digest = unsigned.pop("profile_digest")
        if declared_digest != digest(unsigned):
            _fail(f"{path}.profile_digest", "does not match the canonical profile digest")
        _unique_texts(obj["authority_scope_ids"], f"{path}.authority_scope_ids", identifiers=True, minimum=1)
        _text(obj["title"], f"{path}.title")
        _enum(obj["authority_level"], f"{path}.authority_level", {"supranational", "national", "subnational", "tribal", "institutional"})
        if obj["coverage_status"] != "bounded_subset" or obj["no_completeness_claim"] is not True:
            _fail(path, "profiles must be bounded subsets with no_completeness_claim=true")
        for name in ("covered_provisions", "known_exclusions", "known_gaps"):
            _unique_texts(obj[name], f"{path}.{name}", minimum=1)
        for source_id in _unique_texts(obj["source_ids"], f"{path}.source_ids", identifiers=True, minimum=1):
            if source_id not in sources:
                _fail(f"{path}.source_ids", f"unknown source id: {source_id}")
        _validate_predicate(obj["applies_if"], definitions, f"{path}.applies_if")
        requirements = _array(obj["requirements"], f"{path}.requirements", maximum=512)
        if not requirements:
            _fail(f"{path}.requirements", "must not be empty")
        for req_index, requirement in enumerate(requirements):
            requirement_ids.append(
                _validate_requirement(
                    requirement,
                    f"{path}.requirements[{req_index}]",
                    axis,
                    definitions,
                    sources,
                    set(obj["source_ids"]),
                )
            )
        profile_index[(profile_id, profile_version)] = obj
    if {row["axis"] for row in profiles} != set(AXES):
        _fail("registry.profiles", "must ship at least one profile on both V1 axes")
    overlays = _array(top["overlays"], "registry.overlays", maximum=128)
    overlay_ids: set[str] = set()
    for index, row in enumerate(overlays):
        path = f"registry.overlays[{index}]"
        fields = {"overlay_id", "overlay_version", "overlay_digest", "overlay_kind", "axis", "issuer", "title", "authority_scope_ids", "target_profiles", "source_ids", "operation", "requirements_removed", "requirements"}
        obj = _closed(row, path, fields)
        overlay_id = _identifier(obj["overlay_id"], f"{path}.overlay_id")
        if overlay_id in overlay_ids:
            _fail(f"{path}.overlay_id", "duplicate overlay id")
        overlay_ids.add(overlay_id)
        _version(obj["overlay_version"], f"{path}.overlay_version")
        _sha(obj["overlay_digest"], f"{path}.overlay_digest")
        unsigned = copy.deepcopy(obj)
        declared_digest = unsigned.pop("overlay_digest")
        if declared_digest != digest(unsigned):
            _fail(f"{path}.overlay_digest", "does not match the canonical overlay digest")
        _enum(obj["overlay_kind"], f"{path}.overlay_kind", {"institutional", "funder"})
        axis = _enum(obj["axis"], f"{path}.axis", set(AXES))
        _text(obj["issuer"], f"{path}.issuer")
        _text(obj["title"], f"{path}.title")
        _unique_texts(obj["authority_scope_ids"], f"{path}.authority_scope_ids", identifiers=True, minimum=1)
        targets = _array(obj["target_profiles"], f"{path}.target_profiles")
        if not targets:
            _fail(f"{path}.target_profiles", "must not be empty")
        target_keys: list[tuple[str, str]] = []
        for target_index, target in enumerate(targets):
            target_path = f"{path}.target_profiles[{target_index}]"
            target_obj = _closed(target, target_path, {"axis", "profile_id", "profile_version", "profile_digest"})
            if target_obj["axis"] != axis:
                _fail(f"{target_path}.axis", "must match overlay axis")
            key = (_identifier(target_obj["profile_id"], f"{target_path}.profile_id"), _version(target_obj["profile_version"], f"{target_path}.profile_version"))
            if key not in profile_index:
                _fail(target_path, "target profile does not exist")
            profile = profile_index[key]
            if target_obj["profile_digest"] != profile["profile_digest"] or target_obj["axis"] != profile["axis"]:
                _fail(target_path, "target profile pin does not match exactly")
            target_keys.append(key)
        _unique(target_keys, f"{path}.target_profiles")
        for source_id in _unique_texts(obj["source_ids"], f"{path}.source_ids", identifiers=True, minimum=1):
            if source_id not in sources:
                _fail(f"{path}.source_ids", f"unknown source id: {source_id}")
        _enum(obj["operation"], f"{path}.operation", {"add", "supplement", "conflict"})
        if obj["requirements_removed"] is not False:
            _fail(f"{path}.requirements_removed", "overlays may never remove requirements")
        requirements = _array(obj["requirements"], f"{path}.requirements", maximum=512)
        if not requirements:
            _fail(f"{path}.requirements", "must not be empty")
        for req_index, requirement in enumerate(requirements):
            requirement_ids.append(
                _validate_requirement(
                    requirement,
                    f"{path}.requirements[{req_index}]",
                    axis,
                    definitions,
                    sources,
                    set(obj["source_ids"]),
                )
            )
    _unique(requirement_ids, "registry requirement ids")
    known_requirements = set(requirement_ids)
    for row in [*profiles, *overlays]:
        for requirement in row["requirements"]:
            route = requirement["waiver_or_exception_route"]
            for target_id in route["requirement_ids"]:
                if target_id not in known_requirements:
                    _fail(f"requirement {requirement['requirement_id']}", f"unknown profiled route requirement: {target_id}")


CONTEXT_FIELDS = {"schema_version", "context_record_id", "confirmed_by", "confirmed_at", "applicability_as_of", "scope_dimensions", "declared_facts", "profile_selection_state", "selected_profiles", "overlay_selection_state", "selected_overlays", "display_precedence"}


def validate_context(context: dict[str, Any], registry: dict[str, Any] | None = None) -> None:
    obj = _closed(context, "context", CONTEXT_FIELDS)
    if obj["schema_version"] != "irb-context-record/1.0":
        _fail("context.schema_version", "must equal irb-context-record/1.0")
    _identifier(obj["context_record_id"], "context.context_record_id")
    if obj["confirmed_by"] != "author":
        _fail("context.confirmed_by", "must equal author")
    _datetime(obj["confirmed_at"], "context.confirmed_at")
    _date(obj["applicability_as_of"], "context.applicability_as_of")
    scope_names = {"review_jurisdictions", "institutions", "data_protection_regimes", "funders", "study_types", "populations", "data_locations", "cross_border_transfers"}
    scopes = _closed(obj["scope_dimensions"], "context.scope_dimensions", scope_names)
    scoped_fact_ids: set[str] = set()
    for name in sorted(scope_names):
        scoped_fact_ids.update(_unique_texts(scopes[name], f"context.scope_dimensions.{name}", identifiers=True, maximum=256))
    definition_index = {row["fact_id"]: row for row in registry["fact_definitions"]} if registry is not None else None
    declared_ids: list[str] = []
    for index, row in enumerate(_array(obj["declared_facts"], "context.declared_facts", maximum=512)):
        path = f"context.declared_facts[{index}]"
        fact = _closed(row, path, {"fact_id", "value_type", "state", "value", "provenance"})
        fact_id = _identifier(fact["fact_id"], f"{path}.fact_id")
        declared_ids.append(fact_id)
        value_type = _enum(fact["value_type"], f"{path}.value_type", {"boolean", "string", "string_enum", "string_set", "date"})
        state = _enum(fact["state"], f"{path}.state", {"declared", "unknown"})
        if fact["provenance"] != "author_declared":
            _fail(f"{path}.provenance", "must equal author_declared")
        if state == "unknown" and fact["value"] is not None:
            _fail(f"{path}.value", "must be null when state is unknown")
        if state == "declared":
            if fact["value"] is None:
                _fail(f"{path}.value", f"does not match declared value_type {value_type}")
            _validate_fact_value(value_type, fact["value"], f"{path}.value")
        if definition_index is not None:
            if fact_id not in definition_index:
                _fail(f"{path}.fact_id", "is not in the registry fact catalog")
            definition = definition_index[fact_id]
            if value_type != definition["value_type"]:
                _fail(f"{path}.value_type", "does not match registry fact definition")
            allowed = definition["allowed_values"]
            if state == "declared" and allowed is not None and fact["value"] not in allowed:
                _fail(f"{path}.value", "is outside the registry fact allowlist")
    _unique(declared_ids, "context.declared_facts")
    if registry is not None:
        unknown_scoped = scoped_fact_ids - set(declared_ids)
        if unknown_scoped:
            _fail("context.scope_dimensions", f"references undeclared fact(s): {', '.join(sorted(unknown_scoped))}")
    states = _closed(obj["profile_selection_state"], "context.profile_selection_state", set(AXES))
    for axis in AXES:
        _enum(states[axis], f"context.profile_selection_state.{axis}", {"selected", "unresolved"})
    profile_keys: list[tuple[str, str, str]] = []
    selections = _array(obj["selected_profiles"], "context.selected_profiles", maximum=64)
    for index, row in enumerate(selections):
        path = f"context.selected_profiles[{index}]"
        selection = _closed(row, path, {"axis", "profile_id", "profile_version", "profile_digest", "authority_scope_ids"})
        axis = _enum(selection["axis"], f"{path}.axis", set(AXES))
        profile_id = _identifier(selection["profile_id"], f"{path}.profile_id")
        version = _version(selection["profile_version"], f"{path}.profile_version")
        _sha(selection["profile_digest"], f"{path}.profile_digest")
        _unique_texts(selection["authority_scope_ids"], f"{path}.authority_scope_ids", identifiers=True, minimum=1)
        profile_keys.append((axis, profile_id, version))
    _unique(profile_keys, "context.selected_profiles")
    for axis in AXES:
        count = sum(row["axis"] == axis for row in selections)
        if states[axis] == "selected" and count == 0:
            _fail("context.profile_selection_state", f"{axis}=selected requires a selected profile")
        if states[axis] == "unresolved" and count != 0:
            _fail("context.profile_selection_state", f"{axis}=unresolved forbids selected profiles")
    overlay_states = _closed(obj["overlay_selection_state"], "context.overlay_selection_state", {"institutional", "funder"})
    for kind in ("institutional", "funder"):
        _enum(overlay_states[kind], f"context.overlay_selection_state.{kind}", {"selected", "not_provided", "none_declared_by_author"})
    overlay_keys: list[tuple[str, str, str]] = []
    overlay_selections = _array(obj["selected_overlays"], "context.selected_overlays", maximum=64)
    for index, row in enumerate(overlay_selections):
        path = f"context.selected_overlays[{index}]"
        selection = _closed(row, path, {"overlay_kind", "axis", "overlay_id", "overlay_version", "overlay_digest"})
        kind = _enum(selection["overlay_kind"], f"{path}.overlay_kind", {"institutional", "funder"})
        axis = _enum(selection["axis"], f"{path}.axis", set(AXES))
        overlay_id = _identifier(selection["overlay_id"], f"{path}.overlay_id")
        version = _version(selection["overlay_version"], f"{path}.overlay_version")
        _sha(selection["overlay_digest"], f"{path}.overlay_digest")
        overlay_keys.append((kind, overlay_id, version))
    _unique(overlay_keys, "context.selected_overlays")
    for kind in ("institutional", "funder"):
        count = sum(row["overlay_kind"] == kind for row in overlay_selections)
        if overlay_states[kind] == "selected" and count == 0:
            _fail("context.overlay_selection_state", f"{kind}=selected requires an overlay")
        if overlay_states[kind] != "selected" and count != 0:
            _fail("context.overlay_selection_state", f"{kind} overlays require state=selected")
    precedence = _array(obj["display_precedence"], "context.display_precedence", maximum=2)
    if len(precedence) != 2:
        _fail("context.display_precedence", "must contain both axes exactly once")
    expected: dict[str, set[tuple[str, str, str, str, str]]] = {axis: set() for axis in AXES}
    for row in selections:
        expected[row["axis"]].add(("profile", row["axis"], row["profile_id"], row["profile_version"], row["profile_digest"]))
    for row in overlay_selections:
        expected[row["axis"]].add((f"{row['overlay_kind']}_overlay", row["axis"], row["overlay_id"], row["overlay_version"], row["overlay_digest"]))
    seen_axes: set[str] = set()
    for index, row in enumerate(precedence):
        path = f"context.display_precedence[{index}]"
        entry = _closed(row, path, {"axis", "purpose", "ordered_authorities"})
        axis = _enum(entry["axis"], f"{path}.axis", set(AXES))
        if axis in seen_axes:
            _fail(f"{path}.axis", "duplicate axis")
        seen_axes.add(axis)
        if entry["purpose"] != "display_only_no_suppression":
            _fail(f"{path}.purpose", "must equal display_only_no_suppression")
        actual: list[tuple[str, str, str, str, str]] = []
        for auth_index, authority in enumerate(_array(entry["ordered_authorities"], f"{path}.ordered_authorities", maximum=128)):
            auth_path = f"{path}.ordered_authorities[{auth_index}]"
            ref = _closed(authority, auth_path, {"authority_kind", "axis", "authority_id", "authority_version", "authority_digest"})
            kind = _enum(ref["authority_kind"], f"{auth_path}.authority_kind", {"profile", "institutional_overlay", "funder_overlay"})
            if ref["axis"] != axis:
                _fail(f"{auth_path}.axis", "must match display axis")
            _identifier(ref["authority_id"], f"{auth_path}.authority_id")
            _version(ref["authority_version"], f"{auth_path}.authority_version")
            _sha(ref["authority_digest"], f"{auth_path}.authority_digest")
            actual.append((kind, axis, ref["authority_id"], ref["authority_version"], ref["authority_digest"]))
        if len(actual) != len(set(actual)) or set(actual) != expected[axis]:
            _fail(f"{path}.ordered_authorities", "must list every selected authority on this axis exactly once")


def _semantic_context(context: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(context)
    value.pop("confirmed_at", None)
    for row in value["declared_facts"]:
        if row["value_type"] == "string_set" and isinstance(row["value"], list):
            row["value"].sort()
    value["declared_facts"] = sorted(value["declared_facts"], key=lambda row: row["fact_id"])
    for rows in value["scope_dimensions"].values():
        rows.sort()
    for row in value["selected_profiles"]:
        row["authority_scope_ids"].sort()
    value["selected_profiles"].sort(key=lambda row: (row["axis"], row["profile_id"], row["profile_version"], row["profile_digest"]))
    value["selected_overlays"].sort(key=lambda row: (row["axis"], row["overlay_kind"], row["overlay_id"], row["overlay_version"], row["overlay_digest"]))
    return value


def _source_current(source: dict[str, Any], as_of: date) -> bool:
    start = date.fromisoformat(source["effective_from"])
    end = date.fromisoformat(source["effective_until"]) if source["effective_until"] else None
    return (
        start <= as_of
        and (end is None or as_of <= end)
        and source["freshness"] == "current"
        and source["controlling_language"] is True
        and source["authenticity_status"] != "official_reference_translation"
    )


def _combine_all(left: str, right: str) -> str:
    if "false" in {left, right}:
        return "false"
    if "unknown" in {left, right}:
        return "unknown"
    return "true"


def resolve(context: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    validate_registry(registry)
    validate_context(context, registry)
    context_as_of = _date(context["applicability_as_of"], "context.applicability_as_of")
    registry_as_of = _date(registry["as_of"], "registry.as_of")
    assert context_as_of is not None and registry_as_of is not None
    if context_as_of > registry_as_of:
        _fail("context.applicability_as_of", "cannot be later than registry.as_of")
    facts = {row["fact_id"]: row for row in context["declared_facts"]}
    definitions = {row["fact_id"]: row for row in registry["fact_definitions"]}
    sources = {row["source_id"]: row for row in registry["sources"]}
    profile_index = {(row["profile_id"], row["profile_version"]): (index, row) for index, row in enumerate(registry["profiles"])}
    overlay_index = {(row["overlay_id"], row["overlay_version"]): (index, row) for index, row in enumerate(registry["overlays"])}
    unresolved: list[dict[str, Any]] = []
    selected_profiles: list[dict[str, Any]] = []
    selected_profile_rows: list[tuple[int, dict[str, Any], str, list[dict[str, Any]], str]] = []
    selected_profile_applicability: dict[tuple[str, str, str, str], str] = {}
    for selection in sorted(context["selected_profiles"], key=lambda row: (row["axis"], row["profile_id"], row["profile_version"])):
        key = (selection["profile_id"], selection["profile_version"])
        if key not in profile_index:
            _fail("context.selected_profiles", f"unknown exact profile pin: {key[0]}@{key[1]}")
        index, profile = profile_index[key]
        if selection["axis"] != profile["axis"] or selection["profile_digest"] != profile["profile_digest"] or set(selection["authority_scope_ids"]) != set(profile["authority_scope_ids"]):
            _fail("context.selected_profiles", f"exact profile pin mismatch: {key[0]}@{key[1]}")
        applicability, trace = evaluate_predicate(profile["applies_if"], facts, definitions)
        anchored_sources = [sources[req["authority_anchor"]["source_id"]] for req in profile["requirements"]]
        source_state = "current" if anchored_sources and all(_source_current(source, context_as_of) for source in anchored_sources) else "unresolved"
        result = {
            "axis": profile["axis"], "profile_id": profile["profile_id"],
            "profile_version": profile["profile_version"], "profile_digest": profile["profile_digest"],
            "authority_scope_ids": sorted(profile["authority_scope_ids"]),
            "profile_pointer": f"/profiles/{index}", "applicability": applicability,
            "predicate_trace": trace, "source_state": source_state,
        }
        selected_profiles.append(result)
        selected_profile_rows.append((index, profile, applicability, trace, source_state))
        selected_profile_applicability[
            (
                profile["profile_id"],
                profile["profile_version"],
                profile["profile_digest"],
                profile["axis"],
            )
        ] = applicability
        if applicability == "unknown":
            unresolved.append({"code": "APPLICABILITY_UNRESOLVED", "axis": profile["axis"], "authority_id": profile["profile_id"], "requirement_id": None})
        elif applicability == "false":
            unresolved.append({"code": "PROFILE_SCOPE_CONFLICT", "axis": profile["axis"], "authority_id": profile["profile_id"], "requirement_id": None})
        if source_state != "current":
            unresolved.append({"code": "AUTHORITY_SOURCE_NOT_CURRENT", "axis": profile["axis"], "authority_id": profile["profile_id"], "requirement_id": None})
    both_axes = all(context["profile_selection_state"][axis] == "selected" and any(row["axis"] == axis for row in context["selected_profiles"]) for axis in AXES)
    if not both_axes:
        for axis in AXES:
            if not any(row["axis"] == axis for row in context["selected_profiles"]):
                unresolved.append({"code": "JURISDICTION_UNRESOLVED", "axis": axis, "authority_id": None, "requirement_id": None})
    selected_profile_pins = {(row["profile_id"], row["profile_version"], row["profile_digest"], row["axis"]) for row in context["selected_profiles"]}
    selected_overlays: list[dict[str, Any]] = []
    selected_overlay_rows: list[tuple[int, dict[str, Any], str]] = []
    for selection in sorted(context["selected_overlays"], key=lambda row: (row["axis"], row["overlay_kind"], row["overlay_id"], row["overlay_version"])):
        key = (selection["overlay_id"], selection["overlay_version"])
        if key not in overlay_index:
            _fail("context.selected_overlays", f"unknown exact overlay pin: {key[0]}@{key[1]}")
        index, overlay = overlay_index[key]
        if selection["overlay_kind"] != overlay["overlay_kind"] or selection["axis"] != overlay["axis"] or selection["overlay_digest"] != overlay["overlay_digest"]:
            _fail("context.selected_overlays", f"exact overlay pin mismatch: {key[0]}@{key[1]}")
        targets = {(row["profile_id"], row["profile_version"], row["profile_digest"], row["axis"]) for row in overlay["target_profiles"]}
        matched = targets & selected_profile_pins
        if matched != targets:
            _fail("context.selected_overlays", f"overlay does not have every exact base target selected: {overlay['overlay_id']}")
        base_applicability = "true"
        for target in sorted(targets):
            base_applicability = _combine_all(
                base_applicability, selected_profile_applicability[target]
            )
        if base_applicability != "true":
            unresolved.append({"code": "OVERLAY_BASE_UNRESOLVED", "axis": overlay["axis"], "authority_id": overlay["overlay_id"], "requirement_id": None})
        selected_overlays.append({
            "overlay_kind": overlay["overlay_kind"], "axis": overlay["axis"],
            "overlay_id": overlay["overlay_id"], "overlay_version": overlay["overlay_version"],
            "overlay_digest": overlay["overlay_digest"], "overlay_pointer": f"/overlays/{index}",
            "target_profile_ids": sorted({row[0] for row in matched}), "requirements_removed": False,
        })
        selected_overlay_rows.append((index, overlay, base_applicability))
    requirement_results: list[dict[str, Any]] = []
    collision_members: dict[str, list[str]] = {}
    authority_requirements: dict[tuple[str, str], list[str]] = {}

    def add_requirements(authority_kind: str, index: int, authority: dict[str, Any], parent_applicability: str = "true") -> None:
        identity_key = "profile_id" if authority_kind == "profile" else "overlay_id"
        version_key = "profile_version" if authority_kind == "profile" else "overlay_version"
        digest_key = "profile_digest" if authority_kind == "profile" else "overlay_digest"
        base_pointer = "profiles" if authority_kind == "profile" else "overlays"
        public_kind = authority_kind if authority_kind == "profile" else f"{authority['overlay_kind']}_overlay"
        authority_id = authority[identity_key]
        authority_requirements[(public_kind, authority_id)] = []
        for req_index, requirement in enumerate(authority["requirements"]):
            req_result, trace = evaluate_predicate(requirement["applies_if"], facts, definitions)
            applicability = _combine_all(parent_applicability, req_result)
            pointer = f"/{base_pointer}/{index}/requirements/{req_index}"
            result = {
                "requirement_id": requirement["requirement_id"], "authority_kind": public_kind,
                "authority_id": authority_id, "authority_version": authority[version_key],
                "authority_digest": authority[digest_key], "axis": authority["axis"],
                "obligated_actor": requirement["obligated_actor"],
                "consumer_scopes": sorted(requirement["consumer_scopes"]),
                "applicability": applicability, "predicate_trace": trace,
                "requirement_digest": digest(requirement), "requirement_pointer": pointer,
                "authority_anchor_pointer": f"{pointer}/authority_anchor",
            }
            requirement_results.append(result)
            authority_requirements[(public_kind, authority_id)].append(requirement["requirement_id"])
            collision_key = requirement["interaction"]["collision_key"]
            if collision_key is not None:
                collision_members.setdefault(collision_key, []).append(requirement["requirement_id"])
            if applicability == "unknown":
                unresolved.append({"code": "APPLICABILITY_UNRESOLVED", "axis": authority["axis"], "authority_id": authority_id, "requirement_id": requirement["requirement_id"]})
            anchor_source = sources[requirement["authority_anchor"]["source_id"]]
            if not _source_current(anchor_source, context_as_of):
                reason = {"code": "AUTHORITY_SOURCE_NOT_CURRENT", "axis": authority["axis"], "authority_id": authority_id, "requirement_id": requirement["requirement_id"]}
                if reason not in unresolved:
                    unresolved.append(reason)

    for index, profile, applicability, _trace, _state in selected_profile_rows:
        add_requirements("profile", index, profile, applicability)
    for index, overlay, base_applicability in selected_overlay_rows:
        add_requirements("overlay", index, overlay, base_applicability)
    requirement_results.sort(key=lambda row: (row["axis"], row["authority_kind"], row["authority_id"], row["requirement_id"]))
    collisions = [
        {"collision_key": key, "requirement_ids": sorted(ids), "resolution": "parallel_authorities_require_human_resolution", "requirements_removed": False}
        for key, ids in sorted(collision_members.items()) if len(set(ids)) >= 2
    ]
    precedence_keys: list[tuple[str, str]] = []
    for axis_entry in context["display_precedence"]:
        for ref in axis_entry["ordered_authorities"]:
            precedence_keys.append((ref["authority_kind"], ref["authority_id"]))
    trace_ids: list[tuple[str, str]] = []
    for key in precedence_keys:
        trace_ids.extend((key[1], req_id) for req_id in authority_requirements.get(key, []))
    if {req_id for _, req_id in trace_ids} != {row["requirement_id"] for row in requirement_results} or len(trace_ids) != len(requirement_results):
        _fail("context.display_precedence", "did not preserve every requirement exactly once")
    trace_order = [
        {"position": index + 1, "requirement_id": req_id, "authority_id": authority_id, "purpose": "display_only_no_suppression"}
        for index, (authority_id, req_id) in enumerate(trace_ids)
    ]
    unique_unresolved = {(row["code"], row["axis"], row["authority_id"], row["requirement_id"]): row for row in unresolved}
    unresolved_rows = [unique_unresolved[key] for key in sorted(unique_unresolved, key=lambda item: tuple("" if part is None else part for part in item))]
    applicability_resolved = both_axes and not any(row["code"] in {"APPLICABILITY_UNRESOLVED", "PROFILE_SCOPE_CONFLICT", "AUTHORITY_SOURCE_NOT_CURRENT", "OVERLAY_BASE_UNRESOLVED"} for row in unresolved_rows)
    allowed = both_axes and applicability_resolved
    resolution_state = "resolved" if allowed else ("jurisdiction_unresolved" if not both_axes else "applicability_unresolved")
    output: dict[str, Any] = {
        "schema_version": "resolved-human-subjects-authority-context/1.0",
        "context_pointer": {"context_record_id": context["context_record_id"], "schema_version": context["schema_version"], "context_digest": digest(_semantic_context(context))},
        "registry_pointer": {"registry_id": registry["registry_id"], "registry_version": registry["registry_version"], "as_of": registry["as_of"], "registry_digest": digest(registry)},
        "selected_profiles": selected_profiles,
        "selected_overlays": selected_overlays,
        "requirement_results": requirement_results,
        "collisions": collisions,
        "trace_order": trace_order,
        "resolution_state": resolution_state,
        "unresolved_reasons": unresolved_rows,
        "downstream_gate": {"both_axes_selected": both_axes, "exact_selection_resolved": True, "all_applicability_resolved": applicability_resolved, "profile_dependent_result_allowed": allowed},
    }
    output["resolved_digest"] = digest(output)
    return output


def validate_resolved_context(
    output: dict[str, Any],
    context: dict[str, Any],
    registry: dict[str, Any],
) -> None:
    """Validate a serialized result by deterministic replay against named inputs."""
    if not isinstance(output, dict):
        _fail("resolved", "must be an object")
    if set(output) != {
        "schema_version",
        "context_pointer",
        "registry_pointer",
        "selected_profiles",
        "selected_overlays",
        "requirement_results",
        "collisions",
        "trace_order",
        "resolution_state",
        "unresolved_reasons",
        "downstream_gate",
        "resolved_digest",
    }:
        _fail("resolved", "does not have the closed resolved-context field set")
    claimed_digest = _sha(output["resolved_digest"], "resolved.resolved_digest")
    unsigned = copy.deepcopy(output)
    unsigned.pop("resolved_digest")
    if digest(unsigned) != claimed_digest:
        _fail("resolved.resolved_digest", "does not match the canonical artifact digest")
    expected = resolve(context, registry)
    if _canonical_bytes(output) != _canonical_bytes(expected):
        _fail(
            "resolved",
            "does not exactly match deterministic replay from the named context and registry",
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", type=Path)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check-registry", action="store_true")
    parser.add_argument(
        "--check-resolved",
        type=Path,
        help="validate a serialized resolved artifact by replaying --context and --registry",
    )
    args = parser.parse_args(argv)
    try:
        registry = load_json(args.registry)
        validate_registry(registry)
        if args.check_registry:
            if (
                args.context is not None
                or args.output is not None
                or args.check_resolved is not None
            ):
                raise ContractError(
                    "--check-registry cannot be combined with --context, --output, or --check-resolved"
                )
            print("Human-subjects authority registry validation passed (#666).")
            return 0
        if args.context is None:
            raise ContractError("--context is required unless --check-registry is used")
        context = load_json(args.context)
        if args.check_resolved is not None:
            if args.output is not None:
                raise ContractError("--check-resolved cannot be combined with --output")
            validate_resolved_context(load_json(args.check_resolved), context, registry)
            print("Resolved human-subjects authority context validation passed (#666).")
            return 0
        result = resolve(context, registry)
        rendered = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        if args.output is None:
            sys.stdout.write(rendered)
        else:
            args.output.write_text(rendered, encoding="utf-8")
        return 0
    except (ContractError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
