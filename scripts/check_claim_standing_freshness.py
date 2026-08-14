#!/usr/bin/env python3
"""§7 freshness checker for the #655 claim-standing probe (gate 13).

The probe identity binds the exact claim text, consent receipt, query plan,
adapter registry, candidate ledger, and stance configuration. This checker
compares a probe's persisted artifacts against the current registry claim
text (and, opt-in, the currently declared discovery adapters) and reports a
closed stale-reason list. A stale result remains inspectable but must not
be presented as current; re-running after new consent creates a new probe
id and never overwrites the prior ledger. The checker is read-only and
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


def _runtime_adapter_reasons(plan: dict[str, Any]) -> list[str]:
    declared = discovery.provider_roster_defaults()
    for provider in plan.get("provider_roster", []):
        index_id = provider.get("index_id")
        if index_id not in declared or provider != declared[index_id]:
            return ["adapter_registry_changed"]
    return []


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

    reasons: set[str] = set()
    claim_sha = plan["claim"]["claim_sha256"]
    if substrate.text_digest(current_claim_text) != claim_sha:
        reasons.add("claim_text_changed")

    if candidate_ledger is not None:
        _require_self_digest(
            candidate_ledger, "candidate_ledger_sha256", "candidate ledger"
        )
        if candidate_ledger.get("query_plan_sha256") != plan["plan_sha256"]:
            reasons.add("query_plan_changed")
        if candidate_ledger.get("claim_sha256") != claim_sha:
            reasons.add("claim_text_changed")
        if candidate_ledger.get("adapter_registry_sha256") != substrate.digest(
            plan["provider_roster"]
        ):
            reasons.add("adapter_registry_changed")

    if stance_record is not None:
        _require_self_digest(
            stance_record, "stance_record_sha256", "stance record"
        )
        identity = stance_record.get("identity")
        _require(
            isinstance(identity, dict), "stance record is missing its identity"
        )
        if identity.get("claim_sha256") != claim_sha:
            reasons.add("claim_text_changed")
        if identity.get("query_plan_sha256") != plan["plan_sha256"]:
            reasons.add("query_plan_changed")
        if (
            identity.get("consent_receipt_sha256")
            != plan["consent"]["receipt_sha256"]
        ):
            reasons.add("consent_receipt_changed")
        if identity.get("adapter_registry_sha256") != substrate.digest(
            plan["provider_roster"]
        ):
            reasons.add("adapter_registry_changed")
        if candidate_ledger is not None and identity.get(
            "candidate_ledger_sha256"
        ) != candidate_ledger.get("candidate_ledger_sha256"):
            reasons.add("candidate_ledger_changed")
        expected_stance_sha = (
            substrate.digest(plan["stance_plan"])
            if plan.get("stance_plan") is not None
            else None
        )
        if identity.get("stance_plan_sha256") != expected_stance_sha:
            reasons.add("stance_configuration_changed")
        stance_runtime = stance_record.get("stance_runtime", {})
        if (
            stance_runtime.get("prompt_contract_version")
            != runner.PROMPT_CONTRACT_VERSION
        ):
            reasons.add("stance_configuration_changed")

    if runtime_check:
        reasons.update(_runtime_adapter_reasons(plan))

    stale_reasons = [token for token in STALE_REASONS if token in reasons]
    verdict: dict[str, Any] = {
        "probe_id": plan["probe_id"],
        "status": "stale" if stale_reasons else "current",
        "stale_reasons": stale_reasons,
    }
    if stale_reasons:
        verdict["presentation_rule"] = PRESENTATION_RULE
    return verdict


def _load(path: Path) -> Any:
    try:
        return substrate.load_json(path)
    except substrate.LedgerError as exc:
        raise FreshnessError(str(exc)) from exc


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
            plan=_load(args.query_plan),
            candidate_ledger=(
                _load(args.candidate_ledger)
                if args.candidate_ledger is not None
                else None
            ),
            stance_record=(
                _load(args.stance_record)
                if args.stance_record is not None
                else None
            ),
            runtime_check=args.runtime_check,
        )
    except FreshnessError as exc:
        print(f"FRESHNESS ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(verdict, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
