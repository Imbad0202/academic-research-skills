#!/usr/bin/env python3
"""Transmission-ledger builder/validator for the #655 claim-standing probe.

Implements the design §6 transmission accounting and the §9 gate-14 check:
every authorized transmission attempt is recorded (recipient, purpose, exact
content classes, byte count, local hash, time, consent receipt, retention
disclosure, result state) and every event must stay inside the consented
content-class allowlist and recipient roster. Retrieval events derive from
the retained `claim-standing-retrieval-input/1.0` attempts (one transport
call per attempt); stance events are the runner's transmission records,
copied field-for-field. Accounting is conservative: an attempt an adapter
refused before transport (e.g. an unsupported query) still appears with its
failure result state, so the ledger may overstate, never understate, what
could have left the session; byte counts are of the consented content class
(the accepted query text / the exact prompt), not transport framing.

The builder is pure and deterministic: it adds no timestamp, performs no
network or model call, and fails closed on any unconsented recipient,
content class, receipt mismatch, off-plan query/index pair, duplicate
attempt, or stale input digest. A `retrieval_plus_stance` plan must supply
its stance transmissions explicitly (an empty list is an explicit assertion
that no stance call ran); passing the stance record cross-checks that every
row that reached the transport has its event. Partial pre-finalization
transmissions remain accountable through the same entry points.
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


def _require_allowlisted(
    event_label: str, content_classes: Any, allowed: set[str]
) -> None:
    if (
        not isinstance(content_classes, list)
        or not content_classes
        or not all(isinstance(item, str) for item in content_classes)
    ):
        _fail(f"{event_label}: content classes must be a non-empty string list")
    outside = [item for item in content_classes if item not in allowed]
    if outside:
        _fail(
            f"{event_label}: content class {outside[0]!r} is outside the "
            "consented allowlist"
        )


def _validated_inputs(
    plan: dict[str, Any], retrieval_input: dict[str, Any]
) -> None:
    try:
        substrate.validate_schema(
            plan, substrate.plan_schema_filename(plan), "query plan"
        )
        substrate.validate_plan(plan)
        substrate.validate_schema(
            retrieval_input, "retrieval_input.schema.json", "retrieval input"
        )
    except substrate.LedgerError as exc:
        raise TransmissionError(f"input is invalid: {exc}") from exc
    if retrieval_input["retrieval_input_sha256"] != substrate.bound_digest(
        retrieval_input, "retrieval_input_sha256"
    ):
        _fail(
            "retrieval input self-digest does not replay; a silently edited "
            "attempt list cannot be accounted"
        )
    if retrieval_input["query_plan_sha256"] != plan["plan_sha256"]:
        _fail("retrieval input is not bound to this query plan")


def _retrieval_events(
    plan: dict[str, Any], retrieval_input: dict[str, Any]
) -> list[dict[str, Any]]:
    queries = {query["query_id"]: query for query in plan["queries"]}
    roster = {provider["index_id"]: provider for provider in plan["provider_roster"]}
    receipt_id = plan["consent"]["consent_receipt_id"]
    seen_attempts: set[str] = set()
    events: list[dict[str, Any]] = []
    for attempt in retrieval_input["attempts"]:
        label = f"attempt {attempt.get('attempt_id')!r}"
        if attempt["attempt_id"] in seen_attempts:
            _fail(f"{label}: attempt ids must be unique (double-counted event)")
        seen_attempts.add(attempt["attempt_id"])
        query = queries.get(attempt.get("query_id"))
        if query is None:
            _fail(f"{label}: names a query outside the consented plan")
        provider = roster.get(attempt.get("index_id"))
        if provider is None:
            _fail(f"{label}: names an index outside the consented roster")
        if attempt["index_id"] not in query["index_targets"]:
            _fail(
                f"{label}: index {attempt['index_id']!r} is not a consented "
                f"target of query {query['query_id']!r}"
            )
        if attempt.get("consent_receipt_id") != receipt_id:
            _fail(f"{label}: consent receipt does not match the plan receipt")
        events.append(
            {
                "event_kind": "retrieval_query",
                "attempt_id": attempt["attempt_id"],
                "query_id": attempt["query_id"],
                "recipient_index_id": attempt["index_id"],
                "recipient_product_identity": provider["product_identity"],
                "purpose": "scholarly_discovery",
                "content_classes": list(
                    substrate.RETRIEVAL_ONLY_CONTENT_CLASSES
                ),
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
    plan: dict[str, Any],
    stance_transmissions: list[dict[str, Any]],
    allowed: set[str],
) -> list[dict[str, Any]]:
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
        unexpected = sorted(set(source) - set(STANCE_EVENT_FIELDS))
        if unexpected:
            _fail(f"{label}: unexpected field {unexpected[0]!r}")
        _require_allowlisted(label, source["content_classes"], allowed)
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
        event = {"event_kind": "stance_classification"}
        for field in STANCE_EVENT_FIELDS:
            event[field] = source[field]
        events.append(event)
    return events


# Which event result states can honestly account for a stance-record row.
_ROW_EVENT_RESULT_STATES = {
    None: {"performed"},  # performed row (failure_state is null)
    "judge_timeout": {"judge_timeout"},
    "judge_error": {"judge_error"},
    # An oversized judge return is recorded as the row's parse_error with
    # its own event result state.
    "parse_error": {"parse_error", "oversized_output"},
}


def _cross_check_stance_record(
    stance_record: dict[str, Any],
    plan: dict[str, Any],
    stance_events: list[dict[str, Any]],
) -> None:
    try:
        substrate.validate_schema(
            stance_record, "stance_record.schema.json", "stance record"
        )
    except substrate.LedgerError as exc:
        raise TransmissionError(str(exc)) from exc
    if stance_record["stance_record_sha256"] != substrate.bound_digest(
        stance_record, "stance_record_sha256"
    ):
        _fail(
            "stance record self-digest does not replay; an edited record "
            "cannot vouch for the transmission ledger"
        )
    identity = stance_record["identity"]
    if identity["query_plan_sha256"] != plan["plan_sha256"]:
        _fail("stance record is not bound to this query plan")
    if identity["consent_receipt_sha256"] != plan["consent"]["receipt_sha256"]:
        _fail("stance record is not bound to this consent receipt")
    # Every row that reached the transport (everything except an
    # abstract-missing row, which never builds a prompt) must have its
    # event, and the event's prompt hash and result state must agree with
    # the row's retained evidence.
    events_by_family = {
        event["work_family_id"]: event for event in stance_events
    }
    if len(events_by_family) != len(stance_events):
        _fail("stance events must be unique per work family")
    expected_rows = [
        row
        for row in stance_record["rows"]
        if row.get("failure_state") != "abstract_missing"
    ]
    expected_ids = sorted(row["work_family_id"] for row in expected_rows)
    accounted_ids = sorted(events_by_family)
    if expected_ids != accounted_ids:
        _fail(
            "stance record leaves transmissions unaccounted: expected events "
            f"for {expected_ids}, got {accounted_ids}"
        )
    for row in expected_rows:
        event = events_by_family[row["work_family_id"]]
        label = f"stance event for {row['work_family_id']!r}"
        if row.get("prompt_sha256") is None:
            _fail(
                f"{label}: the record row retains no prompt hash for a "
                "transport-reaching call"
            )
        if event["prompt_sha256"] != row["prompt_sha256"]:
            _fail(f"{label}: prompt hash does not match the record row")
        allowed_states = _ROW_EVENT_RESULT_STATES.get(row.get("failure_state"))
        if allowed_states is None:
            _fail(
                f"{label}: record row failure state "
                f"{row.get('failure_state')!r} has no transmission mapping"
            )
        if event["result_state"] not in allowed_states:
            _fail(
                f"{label}: result state {event['result_state']!r} does not "
                f"match the record row (expected one of {sorted(allowed_states)})"
            )


def build_transmission_ledger(
    plan: dict[str, Any],
    retrieval_input: dict[str, Any],
    *,
    stance_transmissions: list[dict[str, Any]] | None = None,
    stance_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(retrieval_input, dict) or not isinstance(
        retrieval_input.get("attempts"), list
    ):
        _fail("retrieval input must carry an attempts array")
    _validated_inputs(plan, retrieval_input)
    allowed = set(plan["authorized_content_classes"])
    events = _retrieval_events(plan, retrieval_input)
    try:
        # The canonical intake's semantic invariants (one initial attempt per
        # planned query/index pair, retry authorization chains, monotonic
        # times): a re-sealed input that silently omits a planned attempt is
        # refused here.
        substrate.validate_input(plan, retrieval_input)
    except substrate.LedgerError as exc:
        raise TransmissionError(f"input is invalid: {exc}") from exc
    stance_authorized = (
        plan["consent"].get("decision") == "retrieval_plus_stance"
    )
    if stance_transmissions is None:
        if stance_authorized:
            _fail(
                "a retrieval_plus_stance consent requires its stance "
                "transmissions to be supplied explicitly; pass an empty list "
                "to assert that no stance call occurred"
            )
    elif stance_transmissions:
        if not stance_authorized:
            _fail(
                "stance transmissions require a retrieval_plus_stance consent "
                "decision; this plan does not authorize a stance call"
            )
        events.extend(_stance_events(plan, stance_transmissions, allowed))
    if stance_record is not None:
        _cross_check_stance_record(
            stance_record, plan, stance_transmissions or []
        )
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
    *,
    stance_record: dict[str, Any] | None = None,
) -> None:
    """Exact deterministic replay: the ledger must equal a fresh build."""
    rebuilt = build_transmission_ledger(
        plan,
        retrieval_input,
        stance_transmissions=stance_transmissions,
        stance_record=stance_record,
    )
    if rebuilt != ledger:
        _fail("transmission ledger does not replay from its inputs")


def authorized_transmission_ledger_path(plan: dict[str, Any]) -> Path:
    """The only writable output path: derived from the hash-bound consent."""
    try:
        return substrate.authorized_export_path(
            plan, TRANSMISSION_LEDGER_SUFFIX
        )
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
        sub.add_argument("--stance-record", type=Path, default=None)
        if name == "build":
            sub.add_argument("--output", type=Path, default=None)
        else:
            sub.add_argument("--transmission-ledger", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        plan = substrate.load_json(args.query_plan)
        retrieval_input = substrate.load_json(args.retrieval_input)
        stance_transmissions = None
        if args.stance_transmissions is not None:
            stance_transmissions = substrate.load_json(args.stance_transmissions)
            if not isinstance(stance_transmissions, list):
                _fail("stance transmissions file must contain a JSON array")
        stance_record = (
            substrate.load_json(args.stance_record)
            if args.stance_record is not None
            else None
        )
        if args.command == "build":
            ledger = build_transmission_ledger(
                plan,
                retrieval_input,
                stance_transmissions=stance_transmissions,
                stance_record=stance_record,
            )
            if args.output is None:
                print(json.dumps(ledger, ensure_ascii=False, indent=2))
            else:
                authorized = substrate.require_export_consent(
                    plan, args.output, TRANSMISSION_LEDGER_SUFFIX
                )
                substrate.write_new_ledger(authorized, ledger)
                print(f"transmission ledger written: {authorized}")
        else:
            ledger = substrate.load_json(args.transmission_ledger)
            validate_transmission_ledger(
                plan,
                retrieval_input,
                stance_transmissions,
                ledger,
                stance_record=stance_record,
            )
            print("transmission ledger replays exactly")
    except (
        TransmissionError,
        substrate.LedgerError,
        OSError,
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
    ) as exc:
        print(f"TRANSMISSION-LEDGER ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
