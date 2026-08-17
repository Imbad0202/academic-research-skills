#!/usr/bin/env python3
"""Consent-surface builder for the #655 claim-standing probe (design §3.1/§3.2).

Turns one Phase E Claim Registry row plus explicit researcher decisions into
a schema-valid `claim-standing-query-plan/1.0` (retrieval_only) or `/1.1`
(retrieval_plus_stance) plan, or into an explicit local `not_checked`
declination record. The §3.1 trigger is exact: at Stage 2.5 the recorded
`HIGH-IMPACT` tier is the registry witness (`RANDOM`, `TOP-UP`, and
`NOT-SELECTED` are never eligible); at Stage 4.5 the `ALL` registry is not
permission — a row is eligible only with the recorded five-part high-impact
basis, and a basis-less row stays ineligible until the researcher confirms
the classification. A Stage 2.5 row whose registry recorded no basis stays
eligible by tier, but binding a plan still needs the basis, supplied through
the same recorded researcher confirmation; the basis provenance (registry
vs researcher confirmation) is displayed on the consent surface and never
written back to the registry.

Consent is bound before any dispatchable plan exists. `propose` renders the
closed §3.2 consent surface, which embeds the complete consentable-plan
projection (claim, queries, roster, filters, content classes, caps, stance
plan, creation time) — what is shown IS what the receipt later binds.
`bind` compares the decisions' surface hash against the exact current
surface: absence produces a `consent_absent` declination, any drift a
`consent_invalidated` declination, and an explicit cancel a
`consent_cancelled` declination — each an explicit local `not_checked`
record with no plan and no network or model call anywhere in the builder.
Eligibility, hashing, and final validation replay through the Track A
substrate (`build_claim_standing_candidate_ledger`). The builder never
mutates its inputs.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

try:
    from scripts import build_claim_standing_candidate_ledger as substrate
    from scripts import claim_standing_discovery as discovery
except ImportError:  # direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_claim_standing_candidate_ledger as substrate  # noqa: E402
    import claim_standing_discovery as discovery  # noqa: E402

SURFACE_KIND = "claim-standing-consent-surface/1.0"
DECLINATION_KIND = "claim-standing-probe-declination/1.0"
QUERY_PLAN_SUFFIX = ".query-plan.json"
DECISION_VALUES = ("retrieval_only", "retrieval_plus_stance", "cancel")
SESSION_ONLY_EXPORT_BOUNDARY = (
    "No local export is authorized under session_only persistence."
)
ADVISORY_STATEMENT = (
    "The probe result is advisory, search-bounded, and fallible; it is not a "
    "gate, it never changes a Phase E verdict, checkpoint result, manuscript "
    "byte, citation, or read ledger, and absent results never prove absence. "
    "Every probe surface remains STANCE CLASSIFICATION UNMEASURED until the "
    "#655 baseline measurement row exists."
)
CONSENT_CHOICES = [
    "edit_or_redact_claim",
    "approve_retrieval_only",
    "approve_retrieval_plus_stance",
    "cancel",
]


class PlanBuilderError(Exception):
    """Fail-closed refusal: no plan may be constructed from these inputs."""


def _fail(message: str) -> None:
    raise PlanBuilderError(message)


def _require(condition: bool, message: str) -> None:
    if not condition:
        _fail(message)


def _valid_basis(values: Any, source: str) -> list[str]:
    _require(
        isinstance(values, list)
        and bool(values)
        and all(isinstance(item, str) for item in values),
        f"{source}: high_impact_basis must be a non-empty string list",
    )
    unknown = [
        item
        for item in values
        if item not in substrate.HIGH_IMPACT_BASIS_VALUES
    ]
    if unknown:
        _fail(f"{source}: unknown high_impact_basis token {unknown[0]!r}")
    _require(
        len(set(values)) == len(values),
        f"{source}: high_impact_basis tokens must be unique",
    )
    return list(values)


def _confirmed_basis(confirmation: dict[str, Any]) -> list[str]:
    _require(
        confirmation.get("confirmed_high_impact") is True,
        "eligibility confirmation must set confirmed_high_impact true",
    )
    _require(
        isinstance(confirmation.get("recorded_at"), str)
        and bool(confirmation["recorded_at"]),
        "eligibility confirmation must record recorded_at",
    )
    return _valid_basis(
        confirmation.get("high_impact_basis"), "eligibility confirmation"
    )


def assess_eligibility(
    registry_row: dict[str, Any], confirmation: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Apply the §3.1 trigger to one Claim Registry row.

    The verdict never mutates the row. At Stage 2.5 the recorded HIGH-IMPACT
    tier alone is the eligibility witness; the plan's five-part basis then
    comes from the registry when recorded, otherwise from a recorded
    researcher confirmation. At Stage 4.5 a basis-less ALL row is ambiguous
    and stays ineligible until the researcher confirms the classification.
    A confirmation can supply a missing basis; it cannot override a wrong
    selection tier.
    """
    checkpoint = registry_row.get("checkpoint")
    _require(
        checkpoint in substrate.CHECKPOINT_REQUIRED_TIER,
        f"checkpoint must be stage_2_5 or stage_4_5, got {checkpoint!r}",
    )
    tier = registry_row.get("registry_selection_tier")
    reasons: list[str] = []
    required_tier = substrate.CHECKPOINT_REQUIRED_TIER[checkpoint]
    if tier != required_tier:
        reasons.append(
            f"registry_selection_tier {tier!r} is not probe-eligible at "
            f"{checkpoint} (requires {required_tier!r}; RANDOM, TOP-UP, and "
            "NOT-SELECTED rows are never eligible, and ALL is not permission "
            "to probe every claim)"
        )
    recorded = registry_row.get("high_impact_basis")
    _require(
        recorded is None or isinstance(recorded, (list, tuple)),
        "registry row: high_impact_basis must be a list when present",
    )
    basis: list[str] = []
    basis_source: str | None = None
    requires_confirmation = False
    if not reasons:
        if recorded:
            basis = _valid_basis(list(recorded), "registry row")
            basis_source = "registry"
        elif confirmation is not None:
            basis = _confirmed_basis(confirmation)
            basis_source = "researcher_confirmation"
        else:
            requires_confirmation = True
            if checkpoint == "stage_4_5":
                reasons.append(
                    "the registry row records no five-part high-impact basis; "
                    "at Stage 4.5 the row is ambiguous and stays ineligible "
                    "until the researcher confirms the classification"
                )
    return {
        "eligible": not reasons,
        "high_impact_basis": basis,
        "basis_source": basis_source,
        "reasons": reasons,
        "requires_confirmation": requires_confirmation,
        # A row is dispatchable only when nothing further is owed by the
        # researcher — consumers must never branch on `eligible` alone.
        "dispatchable": not reasons and not requires_confirmation,
    }


def _resolved_basis(
    registry_row: dict[str, Any], decisions: dict[str, Any]
) -> tuple[list[str], str, dict[str, Any] | None]:
    confirmation = decisions.get("eligibility_confirmation")
    verdict = assess_eligibility(registry_row, confirmation=confirmation)
    if not verdict["eligible"]:
        _fail("; ".join(verdict["reasons"]))
    if not verdict["high_impact_basis"]:
        _fail(
            "the registry row records no five-part high-impact basis; the "
            "researcher must confirm the classification "
            "(decisions.eligibility_confirmation) before a consent surface "
            "can bind one"
        )
    return (
        verdict["high_impact_basis"],
        verdict["basis_source"],
        confirmation if verdict["basis_source"] == "researcher_confirmation" else None,
    )


def _roster(decisions: dict[str, Any]) -> list[dict[str, Any]]:
    indexes = decisions.get("indexes")
    _require(
        isinstance(indexes, list) and 1 <= len(indexes) <= 4,
        "decisions.indexes must be a list naming 1..4 discovery indexes",
    )
    _require(
        len(set(indexes)) == len(indexes),
        "decisions.indexes must be unique",
    )
    defaults = discovery.provider_roster_defaults()
    unknown = [index_id for index_id in indexes if index_id not in defaults]
    if unknown:
        _fail(f"index {unknown[0]!r} is not a declared discovery adapter")
    return [defaults[index_id] for index_id in sorted(indexes)]


def _claim_text(registry_row: dict[str, Any]) -> str:
    claim_text = registry_row.get("claim_text")
    _require(
        isinstance(claim_text, str) and bool(claim_text.strip()),
        "registry row must carry non-empty claim_text",
    )
    return claim_text


def _queries(
    registry_row: dict[str, Any], decisions: dict[str, Any]
) -> list[dict[str, Any]]:
    claim_text = _claim_text(registry_row)
    derived = substrate.exact_claim_query(claim_text)
    claim_sha = substrate.text_digest(claim_text)
    supplied = decisions.get("queries")
    if supplied is None:
        default = decisions.get("default_query")
        _require(
            isinstance(default, dict),
            "decisions.default_query is required when no queries are supplied",
        )
        supplied = [
            {
                "query_id": default.get("query_id", "q1"),
                "accepted_query_text": derived,
                "construction": "exact_claim",
                "language": default.get("language"),
                "date_filter": default.get("date_filter"),
                "index_targets": default.get(
                    "index_targets", sorted(decisions.get("indexes") or [])
                ),
            }
        ]
    _require(
        isinstance(supplied, list) and 1 <= len(supplied) <= 3,
        "decisions.queries must be a list of 1..3 queries when present "
        "(an explicit empty or non-list value is refused, never defaulted)",
    )
    queries: list[dict[str, Any]] = []
    for entry in supplied:
        _require(isinstance(entry, dict), "each query must be an object")
        construction = entry.get("construction")
        if construction == "assisted_then_researcher_approved":
            _fail(
                "assisted_then_researcher_approved is a future optional "
                "planner mode; this builder does not authorize it (design "
                "§4.1)"
            )
        _require(
            construction in ("exact_claim", "researcher_authored"),
            f"unknown query construction {construction!r}",
        )
        accepted = entry.get("accepted_query_text")
        _require(
            isinstance(accepted, str) and bool(accepted.strip()),
            "accepted_query_text must be non-empty",
        )
        if construction == "exact_claim":
            _require(
                accepted == derived,
                "an exact_claim query may only strip ARS citation markers and "
                "collapse ASCII whitespace; edited text must be declared "
                "researcher_authored",
            )
            original = derived
        else:
            original = entry.get("original_query_text", accepted)
        queries.append(
            {
                "query_id": entry.get("query_id"),
                "original_query_text": original,
                "accepted_query_text": accepted,
                "construction": construction,
                "source_claim_sha256": claim_sha,
                "language": entry.get("language"),
                "date_filter": entry.get("date_filter"),
                "index_targets": list(entry.get("index_targets") or []),
                "query_sha256": substrate.text_digest(accepted),
            }
        )
    return queries


def _stance_plan(decisions: dict[str, Any]) -> dict[str, Any] | None:
    decision = decisions.get("decision")
    _require(
        decision in DECISION_VALUES,
        f"decision must be one of {DECISION_VALUES}, got {decision!r}",
    )
    if decision != "retrieval_plus_stance":
        return None
    stance_plan = decisions.get("stance_plan")
    _require(
        isinstance(stance_plan, dict),
        "retrieval_plus_stance requires an explicit stance_plan naming the "
        "exact provider and model",
    )
    return copy.deepcopy(stance_plan)


def _explicit_string_list(decisions: dict[str, Any], field: str) -> list[str]:
    values = decisions.get(field)
    _require(
        isinstance(values, list)
        and bool(values)
        and all(isinstance(item, str) for item in values),
        f"decisions.{field} must be a non-empty string list (an explicit "
        "falsey or wrong-type value is refused, never defaulted)",
    )
    return list(values)


def _draft_plan(
    registry_row: dict[str, Any], decisions: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any] | None, str, dict[str, Any] | None]:
    """Everything of the future plan except the consent block and plan hash."""
    basis, basis_source, confirmation = _resolved_basis(registry_row, decisions)
    stance_plan = _stance_plan(decisions)
    version = (
        substrate.PLAN_VERSION_1_1 if stance_plan else substrate.PLAN_VERSION
    )
    draft: dict[str, Any] = {
        "schema_version": version,
        "probe_id": decisions.get("probe_id"),
        "claim": {
            "checkpoint": registry_row.get("checkpoint"),
            "claim_id": registry_row.get("claim_id"),
            "claim_text": _claim_text(registry_row),
            "claim_sha256": substrate.text_digest(_claim_text(registry_row)),
            "registry_selection_tier": registry_row.get(
                "registry_selection_tier"
            ),
            "high_impact_basis": basis,
            "eligibility_confirmed_by_researcher": True,
        },
        "queries": _queries(registry_row, decisions),
        "provider_roster": _roster(decisions),
        "allowed_languages": _explicit_string_list(
            decisions, "allowed_languages"
        ),
        "allowed_document_types": _explicit_string_list(
            decisions, "allowed_document_types"
        ),
        "authorized_content_classes": list(
            substrate.STANCE_CONTENT_CLASSES
            if stance_plan
            else substrate.RETRIEVAL_ONLY_CONTENT_CLASSES
        ),
        "caps": dict(substrate.CAPS),
        "created_at": decisions.get("created_at"),
    }
    if version == substrate.PLAN_VERSION_1_1:
        draft["stance_plan"] = stance_plan
    return draft, stance_plan, basis_source, confirmation


def build_consent_surface(
    registry_row: dict[str, Any], decisions: dict[str, Any]
) -> dict[str, Any]:
    """The closed §3.2 consent receipt content, shown before any acceptance.

    Embeds the complete consentable-plan projection of the plan `bind` would
    construct from the same inputs, so the surface digest covers every field
    the consent receipt later binds.
    """
    return _surface_from_draft(
        *_draft_plan(registry_row, decisions), decisions
    )


def _surface_from_draft(
    draft: dict[str, Any],
    stance_plan: dict[str, Any] | None,
    basis_source: str,
    confirmation: dict[str, Any] | None,
    decisions: dict[str, Any],
) -> dict[str, Any]:
    local_persistence = decisions.get("local_persistence")
    _require(
        local_persistence in ("session_only", "explicit_local_export"),
        "local_persistence must be session_only or explicit_local_export",
    )
    authorized_output_path = decisions.get("authorized_output_path")
    if local_persistence == "explicit_local_export":
        _require(
            isinstance(authorized_output_path, str)
            and not authorized_output_path.endswith(("/", "\\")),
            "authorized_output_path must not end with a path separator: "
            "derived artifact names would become hidden dotfiles",
        )
    constructions = {
        query["construction"] for query in draft["queries"]
    }
    claim_display = dict(draft["claim"])
    claim_display["high_impact_basis_source"] = basis_source
    if confirmation is not None:
        claim_display["basis_confirmation_recorded_at"] = confirmation[
            "recorded_at"
        ]
    return {
        "surface_kind": SURFACE_KIND,
        "probe_id": draft["probe_id"],
        "checkpoint": draft["claim"]["checkpoint"],
        "claim": claim_display,
        "queries": draft["queries"],
        "providers": draft["provider_roster"],
        "consentable_plan": substrate.consentable_plan_projection(draft),
        "query_transmission": {
            "exact_claim_text": "exact_claim" in constructions,
            "researcher_edited_query": "researcher_authored" in constructions,
        },
        "caps": draft["caps"],
        "llm_transmission": {
            "abstracts_to_llm": bool(
                stance_plan and stance_plan.get("abstracts_to_llm_authorized")
            ),
            "session_held_full_text_to_llm": bool(
                stance_plan
                and stance_plan.get("session_held_full_text_to_llm_authorized")
            ),
        },
        "stance_provider": (
            {
                "provider_identity": stance_plan["provider_identity"],
                "model_identity": stance_plan["model_identity"],
            }
            if stance_plan
            else None
        ),
        "stance_retention": (
            {
                "retention_state": stance_plan["retention_state"],
                "retention_reference": stance_plan["retention_reference"],
            }
            if stance_plan
            else None
        ),
        "local_persistence": local_persistence,
        "authorized_output_path": authorized_output_path,
        "derived_artifact_suffixes": dict(substrate.ARTIFACT_SUFFIXES),
        "deletion_boundary": decisions.get("deletion_boundary"),
        "export_boundary": (
            substrate.EXPLICIT_LOCAL_EXPORT_BOUNDARY
            if local_persistence == "explicit_local_export"
            else SESSION_ONLY_EXPORT_BOUNDARY
        ),
        "advisory_statement": ADVISORY_STATEMENT,
        "choices": list(CONSENT_CHOICES),
    }


def consent_surface_sha256(surface: dict[str, Any]) -> str:
    return substrate.digest(surface)


def _declination(
    registry_row: dict[str, Any], decisions: dict[str, Any], reason: str
) -> dict[str, Any]:
    recorded_at = decisions.get("recorded_at") or decisions.get("accepted_at")
    _require(
        isinstance(recorded_at, str) and bool(recorded_at),
        "a declination must record recorded_at (or carry accepted_at)",
    )
    claim_text = _claim_text(registry_row)
    return {
        "record_kind": DECLINATION_KIND,
        "probe_id": decisions.get("probe_id"),
        "checkpoint": registry_row.get("checkpoint"),
        "claim_id": registry_row.get("claim_id"),
        "claim_sha256": substrate.text_digest(claim_text),
        "status": "not_checked",
        "reason": reason,
        "recorded_at": recorded_at,
        "network_calls": "none",
        "model_calls": "none",
    }


def bind_plan(
    registry_row: dict[str, Any], decisions: dict[str, Any]
) -> dict[str, Any]:
    """Bind researcher acceptance to the exact proposed consent surface.

    Returns the schema-valid plan, or an explicit `not_checked` declination
    record: `consent_absent` when no surface hash was supplied,
    `consent_invalidated` when the supplied hash does not match the exact
    current surface (claim edit, filter change, provider change, cap change,
    persistence change), and `consent_cancelled` on an explicit cancel.
    Never mutates its inputs; performs no network or model call.
    """
    # An explicit cancel is a refusal of consent, not an acceptance to
    # verify: it needs no surface hash and is recorded before any binding
    # comparison (a proposed retrieval_plus_stance surface followed by a
    # cancel must record consent_cancelled, never consent_invalidated).
    if decisions.get("decision") == "cancel":
        return _declination(registry_row, decisions, "consent_cancelled")
    draft, stance_plan, basis_source, confirmation = _draft_plan(
        registry_row, decisions
    )
    surface = _surface_from_draft(
        draft, stance_plan, basis_source, confirmation, decisions
    )
    supplied_hash = decisions.get("consent_surface_sha256")
    if supplied_hash is None:
        return _declination(registry_row, decisions, "consent_absent")
    if supplied_hash != consent_surface_sha256(surface):
        return _declination(registry_row, decisions, "consent_invalidated")

    version = draft["schema_version"]
    consent: dict[str, Any] = {
        "consent_receipt_id": decisions.get("consent_receipt_id"),
        "decision": decisions["decision"],
        "accepted_at": decisions.get("accepted_at"),
        "claim_sha256": draft["claim"]["claim_sha256"],
        "provider_roster_sha256": substrate.digest(draft["provider_roster"]),
        "caps_sha256": substrate.digest(draft["caps"]),
        "queries_sha256": substrate.digest(draft["queries"]),
        "stance_classification_authorized": bool(stance_plan),
        "advisory_acknowledged": True,
        "search_bounded_acknowledged": True,
        "local_persistence": surface["local_persistence"],
        "provider_retention_disclosed": True,
        "deletion_boundary": surface["deletion_boundary"],
        "export_boundary": surface["export_boundary"],
        "authorized_output_path": surface["authorized_output_path"],
    }
    if version == substrate.PLAN_VERSION_1_1:
        consent["stance_plan_sha256"] = (
            substrate.digest(stance_plan) if stance_plan else None
        )
    plan = dict(draft)
    plan["consent"] = consent
    consent["consentable_plan_sha256"] = substrate.digest(
        substrate.consentable_plan_projection(plan)
    )
    _require(
        consent["consentable_plan_sha256"]
        == substrate.digest(surface["consentable_plan"]),
        "internal consistency failure: the bound consentable-plan projection "
        "does not equal the projection the accepted surface displayed",
    )
    consent["receipt_sha256"] = substrate.bound_digest(consent, "receipt_sha256")
    plan["plan_sha256"] = substrate.bound_digest(plan, "plan_sha256")
    try:
        substrate.validate_schema(
            plan, substrate.plan_schema_filename(plan), "query plan"
        )
        substrate.validate_plan(plan)
    except substrate.LedgerError as exc:
        raise PlanBuilderError(f"bound plan failed validation: {exc}") from exc
    return plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("propose", "print the consent surface and its binding digest"),
        ("bind", "bind an accepted consent surface into a query plan"),
    ):
        sub = commands.add_parser(name, help=help_text)
        sub.add_argument("--registry-claim", type=Path, required=True)
        sub.add_argument("--decisions", type=Path, required=True)
        if name == "bind":
            sub.add_argument(
                "--output",
                type=Path,
                default=None,
                help=(
                    "write the bound plan to the consent-derived path; "
                    "requires the receipt to say explicit_local_export. "
                    "Omit to print the plan for session-only use."
                ),
            )
    args = parser.parse_args(argv)
    try:
        registry_row = substrate.load_json(args.registry_claim)
        decisions = substrate.load_json(args.decisions)
        if args.command == "propose":
            surface = build_consent_surface(registry_row, decisions)
            print(
                json.dumps(
                    {
                        "consent_surface": surface,
                        "consent_surface_sha256": consent_surface_sha256(
                            surface
                        ),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            result = bind_plan(registry_row, decisions)
            if result.get("record_kind") == DECLINATION_KIND:
                # Distinct status: a declination is neither a bound plan
                # (0) nor an assessment error (1).
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 3
            elif args.output is None:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                authorized = substrate.require_export_consent(
                    result, args.output, QUERY_PLAN_SUFFIX
                )
                substrate.write_new_ledger(authorized, result)
                print(f"query plan written: {authorized}")
    except (
        PlanBuilderError,
        substrate.LedgerError,
        OSError,
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
    ) as exc:
        print(f"QUERY-PLAN ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
