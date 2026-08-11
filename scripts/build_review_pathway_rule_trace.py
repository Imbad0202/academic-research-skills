#!/usr/bin/env python3
"""Build, replay-validate, and render a deterministic #669 pathway rule trace.

The runtime opens only caller-named JSON artifacts.  It never chooses or ranks a
pathway, determines approval/exemption/clearance, calls a model or network, uses
the clock, scans a directory, or changes a workflow decision.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any, NoReturn

if __package__:
    from scripts.resolve_human_subjects_authority import (
        ContractError,
        digest,
        load_json,
        validate_resolved_context,
    )
else:
    from resolve_human_subjects_authority import (  # type: ignore[no-redef]
        ContractError,
        digest,
        load_json,
        validate_resolved_context,
    )


REQUEST_VERSION = "review-pathway-trace-request/1.0"
TRACE_VERSION = "review-pathway-rule-trace/1.0"
RESULT = "institutional determination required"
BOUNDARY_FOOTER = (
    "Human-subjects boundary: This output does not authorize recruitment, "
    "consent, access to identifiable data, intervention, or data collection."
)
ORDERING = "display_only_sequence_no_decision_meaning"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
HTTPS_RE = re.compile(r"^https://[^\s\x00-\x1f\x7f]+$")
REQUIREMENT_POINTER_RE = re.compile(r"^/profiles/[0-9]+/requirements/[0-9]+$")
MAX_CANDIDATES = 128
MAX_REQUIREMENTS = 4096
MAX_ALTERNATIVE_ROWS = 4096
MAX_TRACE_BYTES = 8 * 1024 * 1024
MAX_RENDERED_BYTES = 8 * 1024 * 1024
INERT_FORBIDDEN = set("\r\n\t#*[]()<>|\\`")
HALT_CODES = {
    "JURISDICTION_UNRESOLVED",
    "APPLICABILITY_UNRESOLVED",
    "PROFILE_SCOPE_CONFLICT",
    "AUTHORITY_SOURCE_NOT_CURRENT",
    "OVERLAY_BASE_UNRESOLVED",
}
REQUEST_FIELDS = {
    "schema_version",
    "trace_request_id",
    "context_pointer",
    "registry_pointer",
    "resolved_digest",
    "ordering_semantics",
    "candidate_pathways",
}
TRACE_FIELDS = {
    "schema_version",
    "trace_request_id",
    "request_digest",
    "context_pointer",
    "registry_pointer",
    "resolved_digest",
    "trace_state",
    "halt_reasons",
    "ordering_semantics",
    "candidate_pathways",
    "result",
    "boundary_footer",
    "trace_digest",
}


def _fail(path: str, message: str) -> NoReturn:
    raise ContractError(f"{path}: {message}")


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


def _array(value: Any, path: str, *, maximum: int = MAX_REQUIREMENTS) -> list[Any]:
    if not isinstance(value, list):
        _fail(path, "must be an array")
    if len(value) > maximum:
        _fail(path, f"exceeds {maximum} items")
    return value


def _text(value: Any, path: str, *, maximum: int) -> str:
    if not isinstance(value, str) or not value:
        _fail(path, "must be a non-empty string")
    if len(value) > maximum:
        _fail(path, f"must not exceed {maximum} characters")
    if any(
        unicodedata.category(char) in {"Cc", "Cf", "Cs"}
        or "\U00013430" <= char <= "\U0001345f"
        for char in value
    ):
        _fail(path, "must not contain control, format, surrogate, or format-control characters")
    return value


def _inert_text(value: Any, path: str, *, maximum: int) -> str:
    text = _text(value, path, maximum=maximum)
    if text != text.strip():
        _fail(path, "must not contain leading or trailing whitespace")
    if unicodedata.normalize("NFKC", text) != text:
        _fail(path, "must already be Unicode NFKC normalized")
    bad = sorted(set(text) & INERT_FORBIDDEN)
    if bad:
        _fail(path, f"must not contain Markdown/control delimiter(s): {''.join(bad)!r}")
    return text


def _identifier(value: Any, path: str) -> str:
    text = _text(value, path, maximum=200)
    if ID_RE.fullmatch(text) is None:
        _fail(path, "must use lowercase letters, digits, dot, underscore, or hyphen")
    return text


def _version(value: Any, path: str) -> str:
    text = _text(value, path, maximum=200)
    if VERSION_RE.fullmatch(text) is None:
        _fail(path, "has an invalid version token")
    return text


def _sha(value: Any, path: str) -> str:
    text = _text(value, path, maximum=64)
    if SHA_RE.fullmatch(text) is None:
        _fail(path, "must be a lowercase SHA-256 digest")
    return text


def _https(value: Any, path: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    text = _text(value, path, maximum=2048)
    if HTTPS_RE.fullmatch(text) is None:
        _fail(path, "must be an https URL without whitespace or controls")
    return text


def _date(value: Any, path: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    text = _text(value, path, maximum=10)
    try:
        parsed = date.fromisoformat(text)
    except ValueError as exc:
        _fail(path, f"must be an ISO date: {exc}")
    if parsed.isoformat() != text:
        _fail(path, "must be a canonical ISO date")
    return text


def _validate_context_pointer(value: Any, path: str) -> dict[str, Any]:
    row = _closed(value, path, {"context_record_id", "schema_version", "context_digest"})
    _identifier(row["context_record_id"], f"{path}.context_record_id")
    if row["schema_version"] != "irb-context-record/1.0":
        _fail(f"{path}.schema_version", "must equal irb-context-record/1.0")
    _sha(row["context_digest"], f"{path}.context_digest")
    return row


def _validate_registry_pointer(value: Any, path: str) -> dict[str, Any]:
    row = _closed(value, path, {"registry_id", "registry_version", "as_of", "registry_digest"})
    _identifier(row["registry_id"], f"{path}.registry_id")
    _version(row["registry_version"], f"{path}.registry_version")
    _date(row["as_of"], f"{path}.as_of")
    _sha(row["registry_digest"], f"{path}.registry_digest")
    return row


def _validate_profile_ref(value: Any, path: str) -> tuple[str, str, str, str]:
    row = _closed(value, path, {"axis", "profile_id", "profile_version", "profile_digest"})
    if row["axis"] not in {"review_ethics", "data_protection"}:
        _fail(f"{path}.axis", "must be review_ethics or data_protection")
    return (
        row["axis"],
        _identifier(row["profile_id"], f"{path}.profile_id"),
        _version(row["profile_version"], f"{path}.profile_version"),
        _sha(row["profile_digest"], f"{path}.profile_digest"),
    )


def _validate_candidate_source(value: Any, path: str) -> None:
    row = _closed(value, path, {"source_kind", "source_locator", "source_url", "effective_date"})
    if row["source_kind"] not in {"institutional_material", "author_declared_question"}:
        _fail(f"{path}.source_kind", "must be institutional_material or author_declared_question")
    _inert_text(row["source_locator"], f"{path}.source_locator", maximum=500)
    _https(row["source_url"], f"{path}.source_url", nullable=True)
    _date(row["effective_date"], f"{path}.effective_date", nullable=True)


def _profile_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (row["axis"], row["profile_id"], row["profile_version"], row["profile_digest"])


def _trace_state(resolved: dict[str, Any]) -> str:
    reasons = resolved["unresolved_reasons"]
    if any(row["code"] == "JURISDICTION_UNRESOLVED" for row in reasons):
        return "jurisdiction_unresolved"
    profiles_safe = all(
        row["applicability"] == "true" and row["source_state"] == "current"
        for row in resolved["selected_profiles"]
    )
    selected_profile_requirements = {
        (row["authority_id"], row["requirement_id"])
        for row in resolved["requirement_results"]
        if row["authority_kind"] == "profile"
    }
    only_requirement_unknown = all(
        row["code"] == "APPLICABILITY_UNRESOLVED"
        and row["requirement_id"] is not None
        and (row["authority_id"], row["requirement_id"])
        in selected_profile_requirements
        for row in reasons
    )
    if (
        resolved["downstream_gate"]["both_axes_selected"] is True
        and profiles_safe
        and only_requirement_unknown
    ):
        return "completed"
    return "authority_context_unresolved"


def _eligible_requirements(resolved: dict[str, Any]) -> dict[tuple[str, str, str, str], dict[str, dict[str, Any]]]:
    result: dict[tuple[str, str, str, str], dict[str, dict[str, Any]]] = {}
    selected = {
        _profile_key(row)
        for row in resolved["selected_profiles"]
    }
    for row in resolved["requirement_results"]:
        if (
            row["authority_kind"] != "profile"
            or "pathway_trace" not in row["consumer_scopes"]
        ):
            continue
        key = (
            row["axis"],
            row["authority_id"],
            row["authority_version"],
            row["authority_digest"],
        )
        if key not in selected:
            _fail("resolved.requirement_results", "eligible requirement is not owned by an exact selected profile")
        bucket = result.setdefault(key, {})
        requirement_id = row["requirement_id"]
        if requirement_id in bucket:
            _fail("resolved.requirement_results", f"duplicate eligible requirement id: {requirement_id}")
        bucket[requirement_id] = row
    return result


def _validate_alternative_volume(
    candidate_sizes: dict[tuple[str, str, str, str], list[int]],
) -> None:
    projected = sum(
        sum(sizes) * (len(sizes) - 1) for sizes in candidate_sizes.values()
    )
    if projected > MAX_ALTERNATIVE_ROWS:
        _fail(
            "request.candidate_pathways",
            f"projects {projected} alternative rows; limit is {MAX_ALTERNATIVE_ROWS}",
        )


def validate_review_pathway_trace_request(
    request: dict[str, Any],
    resolved: dict[str, Any],
) -> None:
    """Validate exact bindings and complete selected-profile requirement coverage."""
    root = _closed(request, "request", REQUEST_FIELDS)
    if root["schema_version"] != REQUEST_VERSION:
        _fail("request.schema_version", f"must equal {REQUEST_VERSION}")
    _identifier(root["trace_request_id"], "request.trace_request_id")
    _validate_context_pointer(root["context_pointer"], "request.context_pointer")
    _validate_registry_pointer(root["registry_pointer"], "request.registry_pointer")
    _sha(root["resolved_digest"], "request.resolved_digest")
    if root["ordering_semantics"] != ORDERING:
        _fail("request.ordering_semantics", f"must equal {ORDERING}")
    if root["context_pointer"] != resolved["context_pointer"]:
        _fail("request.context_pointer", "does not equal replay-bound resolved context pointer")
    if root["registry_pointer"] != resolved["registry_pointer"]:
        _fail("request.registry_pointer", "does not equal replay-bound registry pointer")
    if root["resolved_digest"] != resolved["resolved_digest"]:
        _fail("request.resolved_digest", "does not equal replay-bound resolved digest")

    state = _trace_state(resolved)
    candidates = _array(root["candidate_pathways"], "request.candidate_pathways", maximum=MAX_CANDIDATES)
    if state != "completed":
        if candidates:
            _fail("request.candidate_pathways", f"must be empty when trace state is {state}")
        return
    if not candidates:
        _fail("request.candidate_pathways", "must contain a candidate for every selected profile")

    selected_profile_keys = {
        _profile_key(row)
        for row in resolved["selected_profiles"]
    }
    eligible = _eligible_requirements(resolved)
    if set(eligible) != selected_profile_keys:
        _fail("resolved.requirement_results", "every selected profile must supply pathway_trace requirements")

    seen_candidate_ids: set[str] = set()
    assigned: dict[tuple[str, str, str, str], set[str]] = {key: set() for key in selected_profile_keys}
    candidate_sizes: dict[tuple[str, str, str, str], list[int]] = {}
    candidate_ids_in_order: list[str] = []
    for index, value in enumerate(candidates):
        path = f"request.candidate_pathways[{index}]"
        row = _closed(
            value,
            path,
            {
                "candidate_id",
                "profile_ref",
                "candidate_pathway_name",
                "candidate_name_source",
                "predicate_requirement_ids",
            },
        )
        candidate_id = _identifier(row["candidate_id"], f"{path}.candidate_id")
        if candidate_id in seen_candidate_ids:
            _fail(f"{path}.candidate_id", "duplicates another candidate")
        seen_candidate_ids.add(candidate_id)
        candidate_ids_in_order.append(candidate_id)
        profile_key = _validate_profile_ref(row["profile_ref"], f"{path}.profile_ref")
        if profile_key not in selected_profile_keys:
            _fail(f"{path}.profile_ref", "is not an exact selected profile")
        _inert_text(row["candidate_pathway_name"], f"{path}.candidate_pathway_name", maximum=200)
        _validate_candidate_source(row["candidate_name_source"], f"{path}.candidate_name_source")
        requirement_values = _array(
            row["predicate_requirement_ids"],
            f"{path}.predicate_requirement_ids",
            maximum=512,
        )
        if not requirement_values:
            _fail(f"{path}.predicate_requirement_ids", "must not be empty")
        requirement_ids = [
            _identifier(value, f"{path}.predicate_requirement_ids[{req_index}]")
            for req_index, value in enumerate(requirement_values)
        ]
        if requirement_ids != sorted(requirement_ids):
            _fail(f"{path}.predicate_requirement_ids", "must be in ascending requirement-id order")
        if len(requirement_ids) != len(set(requirement_ids)):
            _fail(f"{path}.predicate_requirement_ids", "must not contain duplicates")
        foreign = set(requirement_ids) - set(eligible[profile_key])
        if foreign:
            _fail(f"{path}.predicate_requirement_ids", f"contains foreign or ineligible id(s): {', '.join(sorted(foreign))}")
        overlap = assigned[profile_key] & set(requirement_ids)
        if overlap:
            _fail(f"{path}.predicate_requirement_ids", f"duplicates assignment(s): {', '.join(sorted(overlap))}")
        assigned[profile_key].update(requirement_ids)
        candidate_sizes.setdefault(profile_key, []).append(len(requirement_ids))

    if candidate_ids_in_order != sorted(candidate_ids_in_order):
        _fail("request.candidate_pathways", "must be in ascending candidate-id order")
    for key in sorted(selected_profile_keys):
        expected = set(eligible[key])
        if assigned[key] != expected:
            missing = sorted(expected - assigned[key])
            _fail("request.candidate_pathways", f"does not cover profile {key[1]} requirement(s): {', '.join(missing)}")
    _validate_alternative_volume(candidate_sizes)


def _pointer_get(root: dict[str, Any], pointer: str, path: str) -> dict[str, Any]:
    if REQUIREMENT_POINTER_RE.fullmatch(pointer) is None:
        _fail(path, "is not an exact profile requirement pointer")
    value: Any = root
    for token in pointer[1:].split("/"):
        if isinstance(value, dict):
            if token not in value:
                _fail(path, "does not resolve in replay-bound registry")
            value = value[token]
        elif isinstance(value, list):
            index = int(token)
            if index >= len(value):
                _fail(path, "array index is outside replay-bound registry")
            value = value[index]
        else:
            _fail(path, "traverses a non-container")
    if not isinstance(value, dict):
        _fail(path, "must resolve to an object")
    return value


def _predicate_row(
    result: dict[str, Any],
    context: dict[str, Any],
    registry: dict[str, Any],
) -> dict[str, Any]:
    requirement = _pointer_get(
        registry,
        result["requirement_pointer"],
        f"resolved.requirement_results[{result['requirement_id']}].requirement_pointer",
    )
    if requirement.get("requirement_id") != result["requirement_id"]:
        _fail(result["requirement_pointer"], "requirement id does not match resolved row")
    if digest(requirement) != result["requirement_digest"]:
        _fail(result["requirement_pointer"], "requirement digest does not match resolved row")
    if result["authority_anchor_pointer"] != f"{result['requirement_pointer']}/authority_anchor":
        _fail("resolved.authority_anchor_pointer", "does not extend exact requirement pointer")
    anchor = requirement.get("authority_anchor")
    if not isinstance(anchor, dict):
        _fail(result["authority_anchor_pointer"], "does not resolve to an authority anchor")
    decision_maker = requirement.get("authoritative_decision_maker")
    if not isinstance(decision_maker, dict):
        _fail(result["requirement_pointer"], "missing authoritative decision maker")
    role_id = _identifier(decision_maker.get("role_id"), f"{result['requirement_pointer']}.authoritative_decision_maker.role_id")
    facts = {row["fact_id"]: row for row in context["declared_facts"]}
    bindings: list[dict[str, Any]] = []
    unresolved_ids: set[str] = set()
    for trace_index, leaf in enumerate(result["predicate_trace"]):
        fact_id = leaf["fact_id"]
        if fact_id is None:
            continue
        path = f"resolved.requirement_results[{result['requirement_id']}].predicate_trace[{trace_index}]"
        _identifier(fact_id, f"{path}.fact_id")
        if leaf["operator"] not in {"fact_equals", "fact_in", "fact_contains"}:
            _fail(f"{path}.operator", "fact leaf has an unsupported operator")
        declaration = facts.get(fact_id)
        state = leaf["declared_state"]
        if declaration is None:
            value = None
            if state != "missing":
                _fail(f"{path}.declared_state", "does not match missing context fact")
        else:
            value = copy.deepcopy(declaration["value"])
            if state != declaration["state"]:
                _fail(f"{path}.declared_state", "does not match context declaration")
        if state in {"missing", "unknown"} or leaf["result"] == "unknown":
            unresolved_ids.add(fact_id)
        bindings.append(
            {
                "expression_path": leaf["expression_path"],
                "operator": leaf["operator"],
                "predicate_result": leaf["result"],
                "fact_id": fact_id,
                "declared_state": state,
                "declared_value": value,
            }
        )
    if not bindings:
        _fail(result["requirement_pointer"], "must expose at least one fact predicate")
    bindings.sort(key=lambda row: (row["expression_path"], row["fact_id"], row["operator"]))
    return {
        "requirement_id": result["requirement_id"],
        "requirement_digest": result["requirement_digest"],
        "requirement_pointer": result["requirement_pointer"],
        "authority_anchor_pointer": result["authority_anchor_pointer"],
        "applicability": result["applicability"],
        "fact_bindings": bindings,
        "unresolved_fact_ids": sorted(unresolved_ids),
        "responsible_authority_role_id": role_id,
        "authority_anchor": {
            "source_id": _identifier(anchor.get("source_id"), f"{result['authority_anchor_pointer']}.source_id"),
            "authority_url": _https(anchor.get("authority_url"), f"{result['authority_anchor_pointer']}.authority_url"),
            "provision": _text(
                anchor.get("provision"),
                f"{result['authority_anchor_pointer']}.provision",
                maximum=300,
            ),
            "effective_date": _date(anchor.get("effective_date"), f"{result['authority_anchor_pointer']}.effective_date"),
        },
    }


def _halt_reasons(resolved: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, reason in enumerate(resolved["unresolved_reasons"]):
        row = _closed(reason, f"resolved.unresolved_reasons[{index}]", {"code", "axis", "authority_id", "requirement_id"})
        if row["code"] not in HALT_CODES:
            _fail(f"resolved.unresolved_reasons[{index}].code", "is not a closed #669 halt code")
        rows.append(copy.deepcopy(row))
    rows.sort(key=lambda row: (row["code"], row["axis"], row["authority_id"] or "", row["requirement_id"] or ""))
    return rows


def build_review_pathway_rule_trace(
    request: dict[str, Any],
    context: dict[str, Any],
    registry: dict[str, Any],
    resolved: dict[str, Any],
) -> dict[str, Any]:
    """Build a candidate-only trace after exact #666 replay."""
    validate_resolved_context(resolved, context, registry)
    validate_review_pathway_trace_request(request, resolved)
    state = _trace_state(resolved)
    output: dict[str, Any] = {
        "schema_version": TRACE_VERSION,
        "trace_request_id": request["trace_request_id"],
        "request_digest": digest(request),
        "context_pointer": copy.deepcopy(resolved["context_pointer"]),
        "registry_pointer": copy.deepcopy(resolved["registry_pointer"]),
        "resolved_digest": resolved["resolved_digest"],
        "trace_state": state,
        "halt_reasons": _halt_reasons(resolved) if state != "completed" else [],
        "ordering_semantics": ORDERING,
        "candidate_pathways": [],
        "result": RESULT,
        "boundary_footer": BOUNDARY_FOOTER,
    }
    if state == "completed":
        eligible = _eligible_requirements(resolved)
        predicate_by_candidate: dict[str, list[dict[str, Any]]] = {}
        candidates_by_profile: dict[tuple[str, str, str, str], list[str]] = {}
        for candidate in request["candidate_pathways"]:
            key = _profile_key(candidate["profile_ref"])
            rows = [
                _predicate_row(eligible[key][requirement_id], context, registry)
                for requirement_id in candidate["predicate_requirement_ids"]
            ]
            rows.sort(key=lambda row: row["requirement_id"])
            predicate_by_candidate[candidate["candidate_id"]] = rows
            candidates_by_profile.setdefault(key, []).append(candidate["candidate_id"])

        for candidate in request["candidate_pathways"]:
            candidate_id = candidate["candidate_id"]
            key = _profile_key(candidate["profile_ref"])
            matched: list[dict[str, Any]] = []
            unmatched: list[dict[str, Any]] = []
            unresolved: list[dict[str, Any]] = []
            for row in predicate_by_candidate[candidate_id]:
                if row["unresolved_fact_ids"] or row["applicability"] == "unknown":
                    unresolved.append(copy.deepcopy(row))
                elif row["applicability"] == "true":
                    matched.append(copy.deepcopy(row))
                else:
                    unmatched.append(copy.deepcopy(row))
            alternatives: list[dict[str, Any]] = []
            for other_id in sorted(candidates_by_profile[key]):
                if other_id == candidate_id:
                    continue
                for row in predicate_by_candidate[other_id]:
                    alternatives.append(
                        {"target_candidate_id": other_id, "predicate": copy.deepcopy(row)}
                    )
            output["candidate_pathways"].append(
                {
                    "candidate_id": candidate_id,
                    "profile_ref": copy.deepcopy(candidate["profile_ref"]),
                    "candidate_pathway_name": candidate["candidate_pathway_name"],
                    "candidate_name_source": copy.deepcopy(candidate["candidate_name_source"]),
                    "matched_predicates": matched,
                    "unmatched_predicates": unmatched,
                    "unresolved_predicates": unresolved,
                    "alternative_pathway_triggers": alternatives,
                    "result": RESULT,
                }
            )
        output["candidate_pathways"].sort(key=lambda row: row["candidate_id"])

    output["trace_digest"] = digest(output)
    if len(_canonical_bytes(output)) > MAX_TRACE_BYTES:
        _fail("trace", f"canonical artifact exceeds {MAX_TRACE_BYTES} bytes")
    try:
        if __package__:
            from scripts.check_review_pathway_output import lint_trace_surface
        else:
            from check_review_pathway_output import lint_trace_surface  # type: ignore[no-redef]
        lint_errors = lint_trace_surface(output)
    except (TypeError, ValueError) as exc:
        _fail("trace", f"banned-output lint failed: {exc}")
    if lint_errors:
        _fail("trace", lint_errors[0])
    return output


def validate_review_pathway_rule_trace(
    trace: dict[str, Any],
    request: dict[str, Any],
    context: dict[str, Any],
    registry: dict[str, Any],
    resolved: dict[str, Any],
) -> None:
    """Replay the complete serialized trace against all exact named inputs."""
    root = _closed(trace, "trace", TRACE_FIELDS)
    if root["schema_version"] != TRACE_VERSION:
        _fail("trace.schema_version", f"must equal {TRACE_VERSION}")
    claimed = _sha(root["trace_digest"], "trace.trace_digest")
    unsigned = copy.deepcopy(root)
    unsigned.pop("trace_digest")
    if digest(unsigned) != claimed:
        _fail("trace.trace_digest", "does not match canonical trace bytes")
    expected = build_review_pathway_rule_trace(request, context, registry, resolved)
    if _canonical_bytes(root) != _canonical_bytes(expected):
        _fail("trace", "does not exactly match deterministic replay from named inputs")


def _canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise ContractError(f"value is not canonical JSON: {exc}") from exc


def _fact_text(bindings: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for row in bindings:
        value = json.dumps(row["declared_value"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        parts.append(
            f"{row['expression_path']} {row['fact_id']}={value} "
            f"[{row['declared_state']}; {row['predicate_result']}]"
        )
    return "; ".join(parts)


def _predicate_line(row: dict[str, Any]) -> str:
    anchor = row["authority_anchor"]
    unresolved = ",".join(row["unresolved_fact_ids"]) or "none"
    return (
        f"- {row['requirement_id']} | applicability {row['applicability']} | facts: "
        f"{_fact_text(row['fact_bindings'])} | unresolved facts: {unresolved} | "
        f"holder: {row['responsible_authority_role_id']} | authority: "
        f"{anchor['provision']} | {anchor['authority_url']} | effective {anchor['effective_date']}"
    )


def _render_predicate_section(lines: list[str], label: str, rows: list[dict[str, Any]]) -> None:
    lines.append(label)
    if not rows:
        lines.append("- none")
    else:
        lines.extend(_predicate_line(row) for row in rows)


def render_review_pathway_rule_trace(trace: dict[str, Any]) -> str:
    """Render the fixed #669 Markdown grammar from a validated-shape trace."""
    _closed(trace, "trace", TRACE_FIELDS)
    lines = [
        "# Review-pathway rule trace",
        "",
        f"Trace state: {trace['trace_state']}",
        "Ordering: display only — sequence has no decision meaning",
        "",
    ]
    if trace["trace_state"] != "completed":
        lines.append("Halt reasons:")
        for row in trace["halt_reasons"]:
            lines.append(
                f"- {row['code']} | axis {row['axis']} | authority "
                f"{row['authority_id'] or 'none'} | requirement {row['requirement_id'] or 'none'}"
            )
        lines.extend([f"Result: {trace['result']}", ""])
    else:
        for index, candidate in enumerate(trace["candidate_pathways"]):
            if index:
                lines.append("")
            lines.extend(
                [
                    f"## Candidate {candidate['candidate_id']}",
                    f"Candidate pathway examined: {candidate['profile_ref']['profile_id']} {candidate['candidate_pathway_name']}",
                    (
                        "Candidate name source: "
                        f"{candidate['candidate_name_source']['source_kind']} | "
                        f"{candidate['candidate_name_source']['source_locator']}"
                    ),
                ]
            )
            _render_predicate_section(lines, "Matched predicates:", candidate["matched_predicates"])
            _render_predicate_section(lines, "Unmatched predicates:", candidate["unmatched_predicates"])
            _render_predicate_section(lines, "Unresolved predicates:", candidate["unresolved_predicates"])
            lines.append("Alternative pathway triggers:")
            alternatives = candidate["alternative_pathway_triggers"]
            if not alternatives:
                lines.append("- none")
            else:
                for alternative in alternatives:
                    lines.append(
                        f"- target {alternative['target_candidate_id']} | "
                        + _predicate_line(alternative["predicate"])[2:]
                    )
            lines.append(f"Result: {candidate['result']}")
            own_rows = (
                candidate["matched_predicates"]
                + candidate["unmatched_predicates"]
                + candidate["unresolved_predicates"]
            )
            for row in sorted(own_rows, key=lambda item: item["requirement_id"]):
                anchor = row["authority_anchor"]
                lines.append(
                    f"Authority: {row['requirement_id']} | {anchor['provision']} | "
                    f"{anchor['authority_url']} | effective {anchor['effective_date']}"
                )
            lines.append("")
    lines.append(f"> **{trace['boundary_footer']}**")
    rendered = "\n".join(lines) + "\n"
    if len(rendered.encode("utf-8")) > MAX_RENDERED_BYTES:
        _fail("rendered", f"artifact exceeds {MAX_RENDERED_BYTES} bytes")
    return rendered


def _write_all(fd: int, raw: bytes) -> None:
    view = memoryview(raw)
    while view:
        written = os.write(fd, view)
        if written <= 0:
            raise OSError("zero-progress write")
        view = view[written:]


def _atomic_create(path: Path, raw: bytes) -> None:
    parent = path.parent
    if not parent.is_dir():
        raise ContractError(f"output parent is not a directory: {parent}")
    if path.exists() or path.is_symlink():
        raise ContractError(f"refusing to overwrite output: {path}")
    temporary = parent / f".{path.name}.tmp-{os.getpid()}"
    fd: int | None = None
    try:
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
        _write_all(fd, raw)
        os.fsync(fd)
        if os.fstat(fd).st_size != len(raw):
            raise OSError("output size mismatch after write")
        os.fchmod(fd, 0o644)
        os.close(fd)
        fd = None
        os.link(temporary, path, follow_symlinks=False)
        try:
            directory_fd = os.open(parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except OSError:
            pass
    finally:
        if fd is not None:
            os.close(fd)
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _load_inputs(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        load_json(args.request),
        load_json(args.context),
        load_json(args.registry),
        load_json(args.resolved),
    )


def _add_bound_inputs(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--resolved", type=Path, required=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build", help="build one canonical trace JSON artifact")
    _add_bound_inputs(build_parser)
    build_parser.add_argument("--output", type=Path)
    validate_parser = commands.add_parser("validate", help="replay-validate a serialized trace")
    _add_bound_inputs(validate_parser)
    validate_parser.add_argument("--trace", type=Path, required=True)
    render_parser = commands.add_parser("render", help="replay-validate and render fixed Markdown")
    _add_bound_inputs(render_parser)
    render_parser.add_argument("--trace", type=Path, required=True)
    render_parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        request, context, registry, resolved = _load_inputs(args)
        if args.command == "build":
            trace = build_review_pathway_rule_trace(request, context, registry, resolved)
            raw = json.dumps(trace, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False).encode("utf-8") + b"\n"
            if len(raw) > MAX_TRACE_BYTES:
                _fail("trace", f"pretty-printed artifact exceeds {MAX_TRACE_BYTES} bytes")
            if args.output is None:
                sys.stdout.buffer.write(raw)
            else:
                _atomic_create(args.output, raw)
        else:
            trace = load_json(args.trace)
            validate_review_pathway_rule_trace(trace, request, context, registry, resolved)
            if args.command == "validate":
                print("Review-pathway rule trace replay validation passed (#669).")
            else:
                raw = render_review_pathway_rule_trace(trace).encode("utf-8")
                if args.output is None:
                    sys.stdout.buffer.write(raw)
                else:
                    _atomic_create(args.output, raw)
        return 0
    except (ContractError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
