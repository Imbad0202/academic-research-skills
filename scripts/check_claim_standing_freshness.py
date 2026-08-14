#!/usr/bin/env python3
"""§7 freshness checker for the #655 claim-standing probe (gate 13).

The probe identity binds the exact claim text, consent receipt, query plan,
adapter registry, candidate ledger, and stance configuration. This checker
compares a probe's persisted artifacts against the current registry claim
text (and, opt-in, the currently declared discovery adapters) and reports a
closed stale-reason list plus an explicit statement of which bindings were
and were not assessed — a claim-text-only comparison never presents itself
as a complete freshness assessment. A stale result remains inspectable but
must not be presented as current; re-running after new consent creates a
new probe id and never overwrites the prior ledger.

The record-side comparison consumes the runner's single identity authority
(`claim_standing_stance_runner.expected_identity`), so a new §7 binding
added there extends this checker automatically. A stance record can only be
assessed together with its candidate ledger. Artifact semantics (schema and
deep replay) belong to `validate_stance_record` and the ledger validator
and are reported as unassessed here. The checker is read-only and
deterministic: no network, no model call, no input mutation, no file
output. Corruption (a self-digest that does not replay) is an assessment
error, never a silent verdict.
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
    from scripts import claim_standing_stance_runner as runner
except ImportError:  # direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_claim_standing_candidate_ledger as substrate  # noqa: E402
    import claim_standing_discovery as discovery  # noqa: E402
    import claim_standing_stance_runner as runner  # noqa: E402

STALE_REASONS = (
    "claim_text_changed",
    "consent_receipt_changed",
    "query_plan_changed",
    "adapter_registry_changed",
    "candidate_ledger_changed",
    "stance_configuration_changed",
)
IDENTITY_FIELD_REASONS = {
    "claim_sha256": "claim_text_changed",
    "consent_receipt_sha256": "consent_receipt_changed",
    "query_plan_sha256": "query_plan_changed",
    "adapter_registry_sha256": "adapter_registry_changed",
    "candidate_ledger_sha256": "candidate_ledger_changed",
    "stance_plan_sha256": "stance_configuration_changed",
}
ASSESSMENT_TOKENS = (
    "claim_text",
    "consent_receipt",
    "query_plan",
    "adapter_registry_binding",
    "current_adapter_registry",
    "candidate_ledger",
    "stance_configuration",
    "artifact_semantic_validation",
)
PRESENTATION_RULE = (
    "A stale result remains inspectable but cannot be presented as current; "
    "re-running requires new consent and a new probe id."
)


class FreshnessError(Exception):
    """The probe artifacts cannot be assessed (malformed or corrupt)."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FreshnessError(message)


def _require_self_digest(value: dict[str, Any], field: str, label: str) -> None:
    _require(isinstance(value, dict), f"{label} must be an object")
    _require(field in value, f"{label} is missing its {field}")
    if value[field] != substrate.bound_digest(value, field):
        raise FreshnessError(
            f"{label} self-digest does not replay; the artifact is corrupt "
            "and cannot be assessed for freshness"
        )


def _runtime_adapter_reasons(plan: dict[str, Any]) -> set[str]:
    declared = discovery.provider_roster_defaults()
    for provider in plan.get("provider_roster", []):
        index_id = provider.get("index_id")
        if index_id not in declared or provider != declared[index_id]:
            return {"adapter_registry_changed"}
    return set()


def assess_freshness(
    *,
    current_claim_text: str,
    plan: dict[str, Any],
    candidate_ledger: dict[str, Any] | None = None,
    stance_record: dict[str, Any] | None = None,
    runtime_check: bool = False,
) -> dict[str, Any]:
    """Compare probe artifacts against the current claim text and each other."""
    _require(isinstance(plan, dict), "query plan must be an object")
    _require(isinstance(current_claim_text, str), "current claim text required")
    try:
        substrate.validate_plan(plan)
    except substrate.LedgerError as exc:
        raise FreshnessError(f"query plan is invalid: {exc}") from exc
    _require(
        stance_record is None or candidate_ledger is not None,
        "a stance record can only be assessed together with its candidate "
        "ledger (identity.candidate_ledger_sha256 is unverifiable without it)",
    )

    reasons: set[str] = set()
    assessed: set[str] = {"claim_text"}
    claim_sha = plan["claim"]["claim_sha256"]
    roster_sha = substrate.digest(plan["provider_roster"])
    if substrate.text_digest(current_claim_text) != claim_sha:
        reasons.add("claim_text_changed")

    if candidate_ledger is not None:
        _require_self_digest(
            candidate_ledger, "candidate_ledger_sha256", "candidate ledger"
        )
        assessed.update({"query_plan", "adapter_registry_binding"})
        if candidate_ledger.get("query_plan_sha256") != plan["plan_sha256"]:
            reasons.add("query_plan_changed")
        if candidate_ledger.get("claim_sha256") != claim_sha:
            reasons.add("claim_text_changed")
        if candidate_ledger.get("adapter_registry_sha256") != roster_sha:
            reasons.add("adapter_registry_changed")

    if stance_record is not None:
        _require_self_digest(
            stance_record, "stance_record_sha256", "stance record"
        )
        identity = stance_record.get("identity")
        _require(
            isinstance(identity, dict), "stance record is missing its identity"
        )
        assessed.update(
            {"consent_receipt", "candidate_ledger", "stance_configuration"}
        )
        expected = runner.expected_identity(plan, candidate_ledger)
        unmapped = set(expected) - set(IDENTITY_FIELD_REASONS)
        _require(
            not unmapped,
            "identity binding without a stale-reason mapping: "
            f"{sorted(unmapped)}; extend IDENTITY_FIELD_REASONS before "
            "assessing (fail-closed parity with the runner's authority)",
        )
        for field, expected_value in expected.items():
            if identity.get(field) != expected_value:
                reasons.add(IDENTITY_FIELD_REASONS[field])
        if identity.get("claim_sha256") != substrate.text_digest(
            current_claim_text
        ):
            reasons.add("claim_text_changed")
        stance_runtime = stance_record.get("stance_runtime", {})
        stance_plan = plan.get("stance_plan") or {}
        for field in ("provider_identity", "model_identity"):
            if stance_runtime.get(field) != stance_plan.get(field):
                reasons.add("stance_configuration_changed")
        if (
            stance_runtime.get("prompt_contract_version")
            != runner.PROMPT_CONTRACT_VERSION
        ):
            reasons.add("stance_configuration_changed")

    if runtime_check:
        assessed.add("current_adapter_registry")
        reasons.update(_runtime_adapter_reasons(plan))

    stale_reasons = [token for token in STALE_REASONS if token in reasons]
    verdict: dict[str, Any] = {
        "probe_id": plan["probe_id"],
        "status": "stale" if stale_reasons else "current",
        "stale_reasons": stale_reasons,
        "assessed": [
            token for token in ASSESSMENT_TOKENS if token in assessed
        ],
        "unassessed": [
            token for token in ASSESSMENT_TOKENS if token not in assessed
        ],
    }
    if stale_reasons:
        verdict["presentation_rule"] = PRESENTATION_RULE
    return verdict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current-claim-file", type=Path, required=True)
    parser.add_argument("--query-plan", type=Path, required=True)
    parser.add_argument("--candidate-ledger", type=Path, default=None)
    parser.add_argument("--stance-record", type=Path, default=None)
    parser.add_argument(
        "--runtime-check",
        action="store_true",
        help="also compare the consented roster against the currently "
        "declared discovery adapters",
    )
    args = parser.parse_args(argv)
    try:
        try:
            current_claim_text = args.current_claim_file.read_text(
                encoding="utf-8"
            )
        except (OSError, UnicodeError) as exc:
            raise FreshnessError(
                f"{args.current_claim_file}: cannot read claim text: {exc}"
            ) from exc
        verdict = assess_freshness(
            current_claim_text=current_claim_text,
            plan=substrate.load_json(args.query_plan),
            candidate_ledger=(
                substrate.load_json(args.candidate_ledger)
                if args.candidate_ledger is not None
                else None
            ),
            stance_record=(
                substrate.load_json(args.stance_record)
                if args.stance_record is not None
                else None
            ),
            runtime_check=args.runtime_check,
        )
    except (
        FreshnessError,
        substrate.LedgerError,
        OSError,
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
    ) as exc:
        print(f"FRESHNESS ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(verdict, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
