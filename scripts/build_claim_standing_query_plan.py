#!/usr/bin/env python3
"""Consent-surface builder for the #655 claim-standing probe (design §3.1/§3.2).

Turns one Phase E Claim Registry row plus explicit researcher decisions into
a schema-valid `claim-standing-query-plan/1.0` (retrieval_only) or `/1.1`
(retrieval_plus_stance) plan, or into an explicit local `not_checked`
declination record when the researcher cancels. The builder enforces the
§3.1 trigger exactly: only a `HIGH-IMPACT` registry row at Stage 2.5, or a
Stage 4.5 `ALL` row whose five-part high-impact classification is recorded,
is eligible; `RANDOM`, `TOP-UP`, `NOT-SELECTED`, and a bare `ALL` without a
recorded basis never expand the trigger, and an ambiguous row stays
ineligible until the researcher confirms the classification (the
confirmation is recorded here and never written back to the registry).

Consent is bound before any dispatchable plan exists: `bind` refuses unless
the decisions carry the SHA-256 of the exact consent surface produced by
`propose` for the same row and choices, so a claim edit or option change
after proposal invalidates the acceptance. The builder performs no network,
index, or model call and never mutates its inputs; eligibility, hashing,
and final validation replay through the Track A substrate
(`build_claim_standing_candidate_ledger`).
"""
from __future__ import annotations

import argparse
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
HIGH_IMPACT_BASIS_VALUES = (
    "headline_conclusion",
    "numerical",
    "causal",
    "methods_critical",
    "disputed",
)
CHECKPOINT_REQUIRED_TIER = {"stage_2_5": "HIGH-IMPACT", "stage_4_5": "ALL"}
DECISION_VALUES = ("retrieval_only", "retrieval_plus_stance", "cancel")
SESSION_ONLY_EXPORT_BOUNDARY = (
    "No local export is authorized under session_only persistence."
)
ADVISORY_STATEMENT = (
    "The probe result is advisory, search-bounded, and fallible; it is not a "
    "gate, it never changes a Phase E verdict, checkpoint result, manuscript "
    "byte, citation, or read ledger, and absent results never prove absence."
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
        and values
        and all(isinstance(item, str) for item in values),
        f"{source}: high_impact_basis must be a non-empty string list",
    )
    unknown = [item for item in values if item not in HIGH_IMPACT_BASIS_VALUES]
    _require(
        not unknown,
        f"{source}: unknown high_impact_basis token {unknown[0]!r}"
        if unknown
        else "",
    )
    _require(
        len(set(values)) == len(values),
        f"{source}: high_impact_basis tokens must be unique",
    )
    return list(values)


def assess_eligibility(
    registry_row: dict[str, Any], confirmation: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Apply the §3.1 trigger to one Claim Registry row.

    The verdict never mutates the row. A valid researcher confirmation makes
    an ambiguous (basis-less) row eligible and supplies the recorded basis;
    it cannot override a wrong selection tier.
    """
    checkpoint = registry_row.get("checkpoint")
    _require(
        checkpoint in CHECKPOINT_REQUIRED_TIER,
        f"checkpoint must be stage_2_5 or stage_4_5, got {checkpoint!r}",
    )
    tier = registry_row.get("registry_selection_tier")
    reasons: list[str] = []
    required_tier = CHECKPOINT_REQUIRED_TIER[checkpoint]
    if tier != required_tier:
        reasons.append(
            f"registry_selection_tier {tier!r} is not probe-eligible at "
            f"{checkpoint} (requires {required_tier!r}; RANDOM, TOP-UP, and "
            "NOT-SELECTED rows are never eligible, and ALL is not permission "
            "to probe every claim)"
        )
    recorded = registry_row.get("high_impact_basis") or []
    basis: list[str] = []
    requires_confirmation = False
    if not reasons:
        if recorded:
            basis = _valid_basis(recorded, "registry row")
        elif confirmation is not None:
            _require(
                confirmation.get("confirmed_high_impact") is True,
                "eligibility confirmation must set confirmed_high_impact true",
            )
            _require(
                isinstance(confirmation.get("recorded_at"), str)
                and bool(confirmation["recorded_at"]),
                "eligibility confirmation must record recorded_at",
            )
            basis = _valid_basis(
                confirmation.get("high_impact_basis"), "eligibility confirmation"
            )
        else:
            requires_confirmation = True
            reasons.append(
                "the registry row records no five-part high-impact basis; the "
                "row is ambiguous and stays ineligible until the researcher "
                "confirms the classification"
            )
    return {
        "eligible": not reasons,
        "high_impact_basis": basis,
        "reasons": reasons,
        "requires_confirmation": requires_confirmation,
    }


def _require_eligible(
    registry_row: dict[str, Any], decisions: dict[str, Any]
) -> list[str]:
    verdict = assess_eligibility(
        registry_row, confirmation=decisions.get("eligibility_confirmation")
    )
    if not verdict["eligible"]:
        _fail("; ".join(verdict["reasons"]))
    return verdict["high_impact_basis"]


def _roster(decisions: dict[str, Any]) -> list[dict[str, Any]]:
    indexes = decisions.get("indexes")
    _require(
        isinstance(indexes, list) and 1 <= len(indexes) <= 4,
        "decisions.indexes must name 1..4 discovery indexes",
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
    if not supplied:
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
                    "index_targets", sorted(decisions.get("indexes", []))
                ),
            }
        ]
    _require(
        isinstance(supplied, list) and 1 <= len(supplied) <= 3,
        "a plan carries at most 3 queries and at least 1",
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
                "index_targets": list(entry.get("index_targets", [])),
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
    return json.loads(json.dumps(stance_plan))


def build_consent_surface(
    registry_row: dict[str, Any], decisions: dict[str, Any]
) -> dict[str, Any]:
    """The closed §3.2 consent receipt content, shown before any acceptance."""
    basis = _require_eligible(registry_row, decisions)
    roster = _roster(decisions)
    queries = _queries(registry_row, decisions)
    stance_plan = _stance_plan(decisions)
    claim_text = _claim_text(registry_row)
    local_persistence = decisions.get("local_persistence")
    _require(
        local_persistence in ("session_only", "explicit_local_export"),
        "local_persistence must be session_only or explicit_local_export",
    )
    constructions = {query["construction"] for query in queries}
    return {
        "surface_kind": SURFACE_KIND,
        "probe_id": decisions.get("probe_id"),
        "checkpoint": registry_row.get("checkpoint"),
        "claim": {
            "claim_id": registry_row.get("claim_id"),
            "claim_text": claim_text,
            "claim_sha256": substrate.text_digest(claim_text),
            "registry_selection_tier": registry_row.get(
                "registry_selection_tier"
            ),
            "high_impact_basis": basis,
        },
        "queries": queries,
        "providers": roster,
        "query_transmission": {
            "exact_claim_text": "exact_claim" in constructions,
            "researcher_edited_query": "researcher_authored" in constructions,
        },
        "caps": dict(substrate.CAPS),
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
        "authorized_output_path": decisions.get("authorized_output_path"),
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
    registry_row: dict[str, Any], decisions: dict[str, Any]
) -> dict[str, Any]:
    recorded_at = decisions.get("recorded_at")
    _require(
        isinstance(recorded_at, str) and bool(recorded_at),
        "a cancellation must record recorded_at",
    )
    claim_text = _claim_text(registry_row)
    return {
        "record_kind": DECLINATION_KIND,
        "probe_id": decisions.get("probe_id"),
        "checkpoint": registry_row.get("checkpoint"),
        "claim_id": registry_row.get("claim_id"),
        "claim_sha256": substrate.text_digest(claim_text),
        "status": "not_checked",
        "reason": "consent_cancelled",
        "recorded_at": recorded_at,
        "network_calls": "none",
        "model_calls": "none",
    }


def bind_plan(
    registry_row: dict[str, Any], decisions: dict[str, Any]
) -> dict[str, Any]:
    """Bind researcher acceptance to the exact proposed consent surface.

    Returns the schema-valid plan, or the explicit `not_checked` declination
    record when the decision is `cancel`. Never mutates its inputs.
    """
    surface = build_consent_surface(registry_row, decisions)
    supplied_hash = decisions.get("consent_surface_sha256")
    _require(
        supplied_hash == consent_surface_sha256(surface),
        "the consent surface hash is missing or stale: the researcher must "
        "see and accept the exact current surface (re-run propose after any "
        "claim, query, provider, cap, or persistence change)",
    )
    if decisions.get("decision") == "cancel":
        return _declination(registry_row, decisions)

    stance_plan = _stance_plan(decisions)
    version = (
        substrate.PLAN_VERSION_1_1 if stance_plan else substrate.PLAN_VERSION
    )
    claim = {
        "checkpoint": registry_row["checkpoint"],
        "claim_id": registry_row["claim_id"],
        "claim_text": surface["claim"]["claim_text"],
        "claim_sha256": surface["claim"]["claim_sha256"],
        "registry_selection_tier": registry_row["registry_selection_tier"],
        "high_impact_basis": surface["claim"]["high_impact_basis"],
        "eligibility_confirmed_by_researcher": True,
    }
    authorized_classes = (
        [
            "accepted_search_query",
            "claim_and_selected_evidence_to_stance_provider",
        ]
        if stance_plan
        else ["accepted_search_query"]
    )
    consent: dict[str, Any] = {
        "consent_receipt_id": decisions.get("consent_receipt_id"),
        "decision": decisions["decision"],
        "accepted_at": decisions.get("accepted_at"),
        "claim_sha256": claim["claim_sha256"],
        "provider_roster_sha256": substrate.digest(surface["providers"]),
        "caps_sha256": substrate.digest(surface["caps"]),
        "queries_sha256": substrate.digest(surface["queries"]),
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
    plan: dict[str, Any] = {
        "schema_version": version,
        "probe_id": decisions.get("probe_id"),
        "claim": claim,
        "queries": surface["queries"],
        "provider_roster": surface["providers"],
        "allowed_languages": list(decisions.get("allowed_languages", [])),
        "allowed_document_types": list(
            decisions.get("allowed_document_types", [])
        ),
        "authorized_content_classes": authorized_classes,
        "caps": surface["caps"],
        "consent": consent,
        "created_at": decisions.get("created_at"),
    }
    if version == substrate.PLAN_VERSION_1_1:
        plan["stance_plan"] = stance_plan
    consent["consentable_plan_sha256"] = substrate.digest(
        substrate.consentable_plan_projection(plan)
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


def _load(path: Path) -> Any:
    try:
        return substrate.load_json(path)
    except substrate.LedgerError as exc:
        raise PlanBuilderError(str(exc)) from exc


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
            sub.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        registry_row = _load(args.registry_claim)
        decisions = _load(args.decisions)
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
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                try:
                    substrate.write_new_ledger(args.output, result)
                except substrate.LedgerError as exc:
                    raise PlanBuilderError(str(exc)) from exc
                print(f"query plan written: {args.output}")
    except PlanBuilderError as exc:
        print(f"QUERY-PLAN ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
