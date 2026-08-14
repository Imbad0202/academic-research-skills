#!/usr/bin/env python3
"""Transmission-ledger builder/validator for the #655 claim-standing probe.

Implements the design §6 transmission accounting and the §9 gate-14 check:
every event that left the session is recorded (recipient, purpose, exact
content classes, byte count, local hash, time, consent receipt, retention
disclosure, result state) and every event must stay inside the consented
content-class allowlist and recipient roster. Retrieval events derive from
the retained `claim-standing-retrieval-input/1.0` attempts (one transport
call per attempt); stance events are the runner's transmission records,
copied verbatim. The builder is pure and deterministic: it adds no
timestamp, performs no network or model call, and fails closed on any
unconsented recipient, content class, or receipt mismatch — including for
a probe that failed before finalization, whose partial transmissions must
still be accountable.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from scripts import build_claim_standing_candidate_ledger as substrate
except ImportError:  # direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_claim_standing_candidate_ledger as substrate  # noqa: E402

LEDGER_VERSION = "claim-standing-transmission-ledger/1.0"
SCHEMA_FILENAME = "transmission_ledger.schema.json"
TRANSMISSION_LEDGER_SUFFIX = ".transmission-ledger.json"
RETRIEVAL_CONTENT_CLASSES = ["accepted_search_query"]
STANCE_CONTENT_CLASSES = ["claim_and_selected_evidence_to_stance_provider"]
STANCE_EVENT_FIELDS = (
    "work_family_id",
    "recipient_provider_identity",
    "recipient_model_identity",
    "purpose",
    "content_classes",
    "prompt_sha256",
    "prompt_utf8_bytes",
    "consent_receipt_id",
    "retention_state",
    "retention_reference",
    "sent_at",
    "result_state",
)


class TransmissionError(Exception):
    """Fail-closed refusal: the transmissions cannot be honestly accounted."""


def _fail(message: str) -> None:
    raise TransmissionError(message)


def _authorized_classes(plan: dict[str, Any]) -> set[str]:
    return set(plan["authorized_content_classes"])


def _require_allowlisted(
    event_label: str, content_classes: Any, plan: dict[str, Any]
) -> None:
    if (
        not isinstance(content_classes, list)
        or not content_classes
        or not all(isinstance(item, str) for item in content_classes)
    ):
        _fail(f"{event_label}: content classes must be a non-empty string list")
    outside = [
        item for item in content_classes if item not in _authorized_classes(plan)
    ]
    if outside:
        _fail(
            f"{event_label}: content class {outside[0]!r} is outside the "
            "consented allowlist"
        )


def _retrieval_events(
    plan: dict[str, Any], retrieval_input: dict[str, Any]
) -> list[dict[str, Any]]:
    queries = {query["query_id"]: query for query in plan["queries"]}
    roster = {provider["index_id"]: provider for provider in plan["provider_roster"]}
    receipt_id = plan["consent"]["consent_receipt_id"]
    events: list[dict[str, Any]] = []
    for attempt in retrieval_input["attempts"]:
        label = f"attempt {attempt.get('attempt_id')!r}"
        query = queries.get(attempt.get("query_id"))
        if query is None:
            _fail(f"{label}: names a query outside the consented plan")
        provider = roster.get(attempt.get("index_id"))
        if provider is None:
            _fail(f"{label}: names an index outside the consented roster")
        if attempt.get("consent_receipt_id") != receipt_id:
            _fail(f"{label}: consent receipt does not match the plan receipt")
        _require_allowlisted(label, list(RETRIEVAL_CONTENT_CLASSES), plan)
        events.append(
            {
                "event_kind": "retrieval_query",
                "attempt_id": attempt["attempt_id"],
                "query_id": attempt["query_id"],
                "recipient_index_id": attempt["index_id"],
                "recipient_product_identity": provider["product_identity"],
                "purpose": "scholarly_discovery",
                "content_classes": list(RETRIEVAL_CONTENT_CLASSES),
                "query_sha256": query["query_sha256"],
                "query_utf8_bytes": len(
                    query["accepted_query_text"].encode("utf-8")
                ),
                "consent_receipt_id": receipt_id,
                "retention_state": provider["retention_state"],
                "retention_reference": provider["retention_reference"],
                "sent_at": attempt["started_at"],
                "result_state": attempt["outcome"],
            }
        )
    return events


def _stance_events(
    plan: dict[str, Any], stance_transmissions: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    if plan.get("consent", {}).get("decision") != "retrieval_plus_stance":
        _fail(
            "stance transmissions require a retrieval_plus_stance consent "
            "decision; this plan does not authorize a stance call"
        )
    stance_plan = plan["stance_plan"]
    receipt_id = plan["consent"]["consent_receipt_id"]
    events: list[dict[str, Any]] = []
    for index, source in enumerate(stance_transmissions):
        label = f"stance transmission [{index}]"
        if not isinstance(source, dict):
            _fail(f"{label}: must be an object")
        missing = [field for field in STANCE_EVENT_FIELDS if field not in source]
        if missing:
            _fail(f"{label}: missing recorded field {missing[0]!r}")
        _require_allowlisted(label, source["content_classes"], plan)
        if source["recipient_provider_identity"] != stance_plan["provider_identity"]:
            _fail(
                f"{label}: recipient provider identity does not match the "
                "consented stance_plan"
            )
        if source["recipient_model_identity"] != stance_plan["model_identity"]:
            _fail(
                f"{label}: recipient model identity does not match the "
                "consented stance_plan"
            )
        if source["consent_receipt_id"] != receipt_id:
            _fail(f"{label}: consent receipt does not match the plan receipt")
        if (
            source["retention_state"] != stance_plan["retention_state"]
            or source["retention_reference"] != stance_plan["retention_reference"]
        ):
            _fail(
                f"{label}: retention disclosure does not match the consented "
                "stance_plan verbatim"
            )
        if not isinstance(source["result_state"], str):
            _fail(
                f"{label}: result_state must be recorded before the event can "
                "be accounted"
            )
        events.append({"event_kind": "stance_classification", **source})
    return events


def build_transmission_ledger(
    plan: dict[str, Any],
    retrieval_input: dict[str, Any],
    *,
    stance_transmissions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    try:
        substrate.validate_plan(plan)
    except substrate.LedgerError as exc:
        raise TransmissionError(f"query plan is invalid: {exc}") from exc
    if not isinstance(retrieval_input, dict) or not isinstance(
        retrieval_input.get("attempts"), list
    ):
        _fail("retrieval input must carry an attempts array")
    if retrieval_input.get("query_plan_sha256") != plan["plan_sha256"]:
        _fail("retrieval input is not bound to this query plan")
    events = _retrieval_events(plan, retrieval_input)
    if stance_transmissions:
        events.extend(_stance_events(plan, stance_transmissions))
    ledger = {
        "schema_version": LEDGER_VERSION,
        "probe_id": plan["probe_id"],
        "query_plan_sha256": plan["plan_sha256"],
        "consent_receipt_id": plan["consent"]["consent_receipt_id"],
        "consent_receipt_sha256": plan["consent"]["receipt_sha256"],
        "authorized_content_classes": list(plan["authorized_content_classes"]),
        "events": events,
    }
    ledger["transmission_ledger_sha256"] = substrate.bound_digest(
        ledger, "transmission_ledger_sha256"
    )
    try:
        substrate.validate_schema(ledger, SCHEMA_FILENAME, "transmission ledger")
    except substrate.LedgerError as exc:
        raise TransmissionError(str(exc)) from exc
    return ledger


def validate_transmission_ledger(
    plan: dict[str, Any],
    retrieval_input: dict[str, Any],
    stance_transmissions: list[dict[str, Any]] | None,
    ledger: dict[str, Any],
) -> None:
    """Exact deterministic replay: the ledger must equal a fresh build."""
    rebuilt = build_transmission_ledger(
        plan, retrieval_input, stance_transmissions=stance_transmissions
    )
    if rebuilt != ledger:
        _fail("transmission ledger does not replay from its inputs")


def authorized_transmission_ledger_path(plan: dict[str, Any]) -> Path:
    """The only writable output path: derived from the hash-bound consent."""
    return Path(
        plan["consent"]["authorized_output_path"] + TRANSMISSION_LEDGER_SUFFIX
    )


def _load(path: Path) -> Any:
    try:
        return substrate.load_json(path)
    except substrate.LedgerError as exc:
        raise TransmissionError(str(exc)) from exc


def _export(plan: dict[str, Any], output: Path, ledger: dict[str, Any]) -> None:
    if plan["consent"]["local_persistence"] != "explicit_local_export":
        _fail(
            "consent does not say explicit_local_export: refusing to create "
            "any output path"
        )
    authorized = authorized_transmission_ledger_path(plan)
    if str(output) != str(authorized):
        _fail(
            "output path must exactly match the consent-derived path "
            f"{str(authorized)!r}"
        )
    try:
        substrate.write_new_ledger(authorized, ledger)
    except substrate.LedgerError as exc:
        raise TransmissionError(str(exc)) from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("build", "assemble and print or export the transmission ledger"),
        ("validate", "replay an existing transmission ledger exactly"),
    ):
        sub = commands.add_parser(name, help=help_text)
        sub.add_argument("--query-plan", type=Path, required=True)
        sub.add_argument("--retrieval-input", type=Path, required=True)
        sub.add_argument("--stance-transmissions", type=Path, default=None)
        if name == "build":
            sub.add_argument("--output", type=Path, default=None)
        else:
            sub.add_argument("--transmission-ledger", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        plan = _load(args.query_plan)
        retrieval_input = _load(args.retrieval_input)
        stance_transmissions = None
        if args.stance_transmissions is not None:
            stance_transmissions = _load(args.stance_transmissions)
            if not isinstance(stance_transmissions, list):
                _fail("stance transmissions file must contain a JSON array")
        if args.command == "build":
            ledger = build_transmission_ledger(
                plan, retrieval_input, stance_transmissions=stance_transmissions
            )
            if args.output is None:
                print(json.dumps(ledger, ensure_ascii=False, indent=2))
            else:
                _export(plan, args.output, ledger)
                print(f"transmission ledger written: {args.output}")
        else:
            ledger = _load(args.transmission_ledger)
            validate_transmission_ledger(
                plan, retrieval_input, stance_transmissions, ledger
            )
            print("transmission ledger replays exactly")
    except TransmissionError as exc:
        print(f"TRANSMISSION-LEDGER ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
