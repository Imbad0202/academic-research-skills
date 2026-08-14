#!/usr/bin/env python3
"""Closed first-round assignment-ledger gate for the #659 blind bundle.

The #659 no-call envelope freezes 48 arm-blind judge packets but explicitly
does not implement the assignment-ledger gate the design requires before any
first-round packet delivery. This tool is that gate, kept outside the no-call
runner so the envelope's own boundary statement stays true.

`verify` checks an operator-authored ledger against the exact finalized blind
bundle and, only when every closed check passes, writes a write-once pass
receipt. `deliver` publishes exactly one isolated packet per verified
first-round assignment. Both commands are offline and file-only; neither
creates, replaces, or stands in for a human judge or adjudicator.

Gate artifacts live in a sibling directory (`<run>-assignment-gate/`), never
inside the run directory, so the envelope's exact run-inventory validation is
unaffected.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, NoReturn

import run_ideation_diversity_no_call as envelope

SUITE = envelope.SUITE
SUITE_ROOT = envelope.SUITE_ROOT
LEDGER_SCHEMA = SUITE_ROOT / "judge_assignment_ledger.schema.json"
RECEIPT_SCHEMA = SUITE_ROOT / "assignment_gate_receipt.schema.json"
MARKER_SCHEMA = SUITE_ROOT / "first_round_delivery_marker.schema.json"
RECEIPT_REF = "assignment-gate-receipt.json"
DELIVERY_ROOT = "deliveries"
MIN_FIRST_ROUND_JUDGES = 2
BINDING_FIELDS = (
    "run_plan_sha256",
    "inventory_sha256",
    "blind_manifest_sha256",
    "private_map_sha256",
)


class GateError(RuntimeError):
    """Raised on any failed closed check; the gate then writes nothing new."""


def _fail(code: str, detail: str) -> NoReturn:
    raise GateError(f"[{code}] {detail}")


def _gate_dir(run_dir: Path) -> Path:
    return run_dir.parent / f"{run_dir.name}-assignment-gate"


def _binding_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "run_plan_sha256": run_dir / "run-plan.json",
        "inventory_sha256": run_dir / "blind" / "inventory.json",
        "blind_manifest_sha256": run_dir / "blind" / "manifest.json",
        "private_map_sha256": run_dir / "blind" / "private" / "arm-map.json",
    }


def _validate_against(
    schema_path: Path, value: dict[str, Any], code: str, label: str
) -> None:
    try:
        envelope._validate_schema(schema_path, value, label)
    except envelope.EnvelopeError as exc:
        _fail(code, str(exc))


def _load_json(
    path: Path, code: str, schema_path: Path, label: str
) -> tuple[dict[str, Any], bytes]:
    try:
        raw = envelope._read_file(path)
        value = envelope._strict_loads(raw)
    except envelope.EnvelopeError as exc:
        _fail(code, str(exc))
    _validate_against(schema_path, value, code, label)
    return value, raw


def _load_bundle(run_dir: Path, *, code: str = "LEDGER-BINDING") -> dict[str, Any]:
    try:
        plan, _, plan_sha, manifest = envelope._load_run(run_dir)
        if manifest["status"] != "blind_finalized":
            envelope._fail(
                "assignment gate requires a blind_finalized bundle, "
                f"not status {manifest['status']!r}"
            )
        blind_manifest_sha, inventory_sha = envelope._validate_blind_bundle(
            run_dir, plan, plan_sha, manifest
        )
        paths = _binding_paths(run_dir)
        inventory_raw = envelope._read_file(paths["inventory_sha256"])
        private_map_raw = envelope._read_file(paths["private_map_sha256"])
    except envelope.EnvelopeError as exc:
        _fail(code, str(exc))
    return {
        "run_plan_sha256": plan_sha,
        "inventory_sha256": inventory_sha,
        "blind_manifest_sha256": blind_manifest_sha,
        "private_map_sha256": envelope._sha(private_map_raw),
        "inventory": envelope._strict_loads(inventory_raw),
        "private_map": envelope._strict_loads(private_map_raw),
    }


def _check_bindings(
    ledger: dict[str, Any], bundle: dict[str, Any], *, code: str = "LEDGER-BINDING"
) -> None:
    for field in BINDING_FIELDS:
        if ledger[field] != bundle[field]:
            _fail(
                code,
                f"ledger {field} does not match the finalized blind bundle",
            )


def _check_roster(ledger: dict[str, Any]) -> None:
    roster = set(ledger["judges"])
    assigned = {row["judge_id"] for row in ledger["first_round_assignments"]}
    unknown = sorted(assigned - roster)
    if unknown:
        _fail("LEDGER-ROSTER", f"assignments name unlisted judges {unknown!r}")
    idle = sorted(roster - assigned)
    if idle:
        _fail("LEDGER-ROSTER", f"roster lists judges with no assignment {idle!r}")


def _check_coverage(ledger: dict[str, Any], bundle: dict[str, Any]) -> None:
    inventory_ids = {
        row["blind_session_id"] for row in bundle["inventory"]["packets"]
    }
    judges_by_packet: dict[str, set[str]] = {}
    for row in ledger["first_round_assignments"]:
        blind_id = row["blind_session_id"]
        if blind_id not in inventory_ids:
            _fail(
                "LEDGER-COVERAGE",
                f"assignment references a blind id outside the inventory: {blind_id}",
            )
        judges_by_packet.setdefault(blind_id, set()).add(row["judge_id"])
    for blind_id in sorted(inventory_ids):
        distinct = len(judges_by_packet.get(blind_id, set()))
        if distinct < MIN_FIRST_ROUND_JUDGES:
            _fail(
                "LEDGER-COVERAGE",
                f"packet {blind_id} has {distinct} distinct first-round "
                f"judges; at least {MIN_FIRST_ROUND_JUDGES} are required",
            )


def _check_exposure(ledger: dict[str, Any], bundle: dict[str, Any]) -> None:
    pair_by_blind = {
        row["blind_session_id"]: row["pair_id"]
        for row in bundle["private_map"]["mapping"]
    }
    packets_by_judge: dict[str, list[str]] = {}
    for row in ledger["first_round_assignments"]:
        packets_by_judge.setdefault(row["judge_id"], []).append(
            row["blind_session_id"]
        )
    for judge_id in sorted(packets_by_judge):
        blinds = packets_by_judge[judge_id]
        pairs = {pair_by_blind[blind_id] for blind_id in blinds}
        if len(pairs) != len(blinds):
            # The diagnostic carries no judge or blind identifiers: even
            # "judge X's set contains a shared pair" is private-map
            # information once combined with the ledger. The operator holds
            # the map and can locate the conflict directly.
            _fail(
                "LEDGER-EXPOSURE",
                "the ledger assigns at least one judge two packets that "
                "share an equivalent scholar context (pair/scenario/role "
                "card); consult the private arm map to locate the conflict",
            )


def verify(args: argparse.Namespace) -> dict[str, Any]:
    ledger, ledger_raw = _load_json(
        args.ledger, "LEDGER-SCHEMA", LEDGER_SCHEMA, "judge assignment ledger"
    )
    bundle = _load_bundle(args.run_dir)
    _check_bindings(ledger, bundle)
    _check_roster(ledger)
    _check_coverage(ledger, bundle)
    _check_exposure(ledger, bundle)

    ledger_sha = envelope._sha(ledger_raw)
    receipt = {
        "schema_version": "ideation-diversity-assignment-gate-receipt/1.0",
        "suite": SUITE,
        "verdict": "pass",
        "ledger_sha256": ledger_sha,
        "ledger": ledger,
        "delivery_rule": bundle["inventory"]["delivery_rule"],
    }
    _validate_against(RECEIPT_SCHEMA, receipt, "RECEIPT-SCHEMA", "gate receipt")
    receipt_raw = envelope._json_bytes(receipt)
    receipt_path = _gate_dir(args.run_dir) / RECEIPT_REF
    if receipt_path.exists() and envelope._read_file(receipt_path) != receipt_raw:
        _fail(
            "RECEIPT-CONFLICT",
            "a write-once pass receipt already exists for a different "
            "ledger or bundle state; it is never replaced",
        )
    envelope._ensure_exact_new(receipt_path, receipt_raw)
    return {
        "verdict": "pass",
        "ledger_sha256": ledger_sha,
        "receipt_ref": str(receipt_path),
        "judges": len(ledger["judges"]),
        "first_round_assignments": len(ledger["first_round_assignments"]),
    }


def _load_receipt(run_dir: Path) -> tuple[dict[str, Any], bytes]:
    receipt_path = _gate_dir(run_dir) / RECEIPT_REF
    if not receipt_path.exists():
        _fail(
            "DELIVERY-RECEIPT",
            "no pass receipt exists; run `verify` before any delivery",
        )
    receipt, receipt_raw = _load_json(
        receipt_path, "DELIVERY-RECEIPT", RECEIPT_SCHEMA, "gate receipt"
    )
    _validate_against(
        LEDGER_SCHEMA, receipt["ledger"], "DELIVERY-RECEIPT", "embedded ledger"
    )
    return receipt, receipt_raw


def _check_dest(
    run_dir: Path, dest: Path, packet_name: str, *, resume: bool
) -> Path:
    resolved = dest.resolve()
    for boundary in (run_dir.resolve(), _gate_dir(run_dir).resolve()):
        if resolved.is_relative_to(boundary):
            _fail(
                "DELIVERY-DEST",
                "destination must live outside the run and gate directories",
            )
    if resume:
        if resolved.exists():
            if not resolved.is_dir():
                _fail("DELIVERY-DEST", "destination must be a directory")
            occupants = [path.name for path in resolved.iterdir()]
            if occupants and occupants != [packet_name]:
                _fail(
                    "DELIVERY-DEST",
                    "destination must be empty: a judge desk holds exactly "
                    "one isolated packet",
                )
    elif resolved.exists():
        # A new delivery claims its desk by creating it: mkdir is the atomic
        # ownership acquisition, so two racing deliveries cannot both own one
        # desk. A pre-existing destination therefore always refuses.
        _fail(
            "DELIVERY-DEST",
            "destination must not exist; the gate creates the judge desk "
            "itself to claim it atomically",
        )
    return resolved


def deliver(args: argparse.Namespace) -> dict[str, Any]:
    receipt, receipt_raw = _load_receipt(args.run_dir)
    ledger = receipt["ledger"]
    # The sealed receipt is evidence, not authority: a receipt file is plain
    # bytes on disk, so delivery replays the complete bundle validation and
    # every semantic gate check against the embedded ledger — exactly what
    # `verify` runs — before anything is delivered.
    bundle = _load_bundle(args.run_dir, code="DELIVERY-DRIFT")
    _check_bindings(ledger, bundle, code="DELIVERY-DRIFT")
    _check_roster(ledger)
    _check_coverage(ledger, bundle)
    _check_exposure(ledger, bundle)
    packet_sha_by_blind = {
        row["blind_session_id"]: row["packet_sha256"]
        for row in bundle["inventory"]["packets"]
    }
    assignment = {
        "judge_id": args.judge,
        "blind_session_id": args.blind_session_id,
    }
    if assignment not in ledger["first_round_assignments"]:
        _fail(
            "DELIVERY-UNASSIGNED",
            f"{args.judge} has no verified first-round assignment for "
            f"{args.blind_session_id}",
        )
    packet_name = f"{args.blind_session_id}.json"
    packet_path = args.run_dir / "blind" / "sessions" / packet_name
    try:
        packet_raw = envelope._read_file(packet_path)
    except envelope.EnvelopeError as exc:
        _fail("DELIVERY-DRIFT", str(exc))
    packet_sha = envelope._sha(packet_raw)
    if packet_sha != packet_sha_by_blind[args.blind_session_id]:
        _fail(
            "DELIVERY-DRIFT",
            f"packet bytes for {args.blind_session_id} no longer match the "
            "sealed inventory hash",
        )

    marker_path = (
        _gate_dir(args.run_dir)
        / DELIVERY_ROOT
        / args.judge
        / f"{args.blind_session_id}.json"
    )
    marker_value = {
        "schema_version": "ideation-diversity-first-round-delivery-marker/1.0",
        "suite": SUITE,
        "judge_id": args.judge,
        "blind_session_id": args.blind_session_id,
        "packet_sha256": packet_sha,
        "dest": str(Path(args.dest).resolve()),
        "receipt_sha256": envelope._sha(receipt_raw),
    }
    _validate_against(MARKER_SCHEMA, marker_value, "DELIVERY-MARKER", "delivery marker")
    marker_raw = envelope._json_bytes(marker_value)
    completion_path = marker_path.with_name(f"{args.blind_session_id}.completed.json")
    if completion_path.exists():
        _fail(
            "DELIVERY-DUPLICATE",
            f"the assignment for {args.judge} and {args.blind_session_id} "
            "was already delivered to completion; it is never re-issued",
        )
    resume = marker_path.exists()
    if resume and envelope._read_file(marker_path) != marker_raw:
        _fail(
            "DELIVERY-DUPLICATE",
            f"{args.judge} already claimed a delivery for "
            f"{args.blind_session_id}; an assignment is delivered once",
        )

    # Destination is checked before the marker claim so a refused destination
    # never burns the write-once assignment.
    dest = _check_dest(args.run_dir, Path(args.dest), packet_name, resume=resume)
    if not resume:
        try:
            envelope._write_new(marker_path, marker_raw)
        except envelope.EnvelopeError:
            _fail(
                "DELIVERY-DUPLICATE",
                f"{args.judge} already claimed a delivery for "
                f"{args.blind_session_id}; an assignment is delivered once",
            )
    try:
        # Unconditional for a new delivery: this single mkdir IS the atomic
        # desk claim, so a racer that loses it never writes to the desk.
        dest.mkdir(mode=0o700)
    except FileExistsError:
        if not resume:
            _fail(
                "DELIVERY-DEST",
                "another delivery claimed this destination first",
            )
    except OSError as exc:
        _fail("DELIVERY-DEST", f"cannot create the judge desk: {exc}")
    delivered_path = dest / packet_name
    try:
        envelope._ensure_exact_new(delivered_path, packet_raw)
    except envelope.EnvelopeError as exc:
        _fail("DELIVERY-DEST", str(exc))
    # Post-publication isolation check: a concurrent delivery racing the
    # pre-publication emptiness check would leave more than one file here.
    # Both racers then fail before their completion markers, so a desk is
    # certified only by a successful exit over exactly one packet.
    occupants = sorted(path.name for path in dest.iterdir())
    if occupants != [packet_name]:
        _fail(
            "DELIVERY-DEST",
            "destination changed during delivery; a judge desk is certified "
            "only when it holds exactly the delivered packet",
        )
    # A write-once completion marker (the exact claim bytes) closes the
    # assignment: after this, even an identical command refuses, so a retired
    # packet cannot be silently re-issued. A crash before this line leaves the
    # claim marker resumable exactly once more.
    envelope._ensure_exact_new(completion_path, marker_raw)
    return {
        "delivered": 1,
        "judge_id": args.judge,
        "blind_session_id": args.blind_session_id,
        "dest": str(delivered_path),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    verify_parser = commands.add_parser(
        "verify",
        help="verify a first-round assignment ledger and seal a pass receipt",
    )
    verify_parser.add_argument("--run-dir", type=Path, required=True)
    verify_parser.add_argument("--ledger", type=Path, required=True)
    verify_parser.set_defaults(handler=verify)
    deliver_parser = commands.add_parser(
        "deliver",
        help="deliver exactly one isolated packet for one verified assignment",
    )
    deliver_parser.add_argument("--run-dir", type=Path, required=True)
    deliver_parser.add_argument("--judge", required=True)
    deliver_parser.add_argument("--blind-session-id", required=True)
    deliver_parser.add_argument("--dest", type=Path, required=True)
    deliver_parser.set_defaults(handler=deliver)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = args.handler(args)
    except (GateError, envelope.EnvelopeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
