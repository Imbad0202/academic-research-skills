#!/usr/bin/env python3
"""Build and replay-validate typed reviewer_full panel provenance.

The artifact deliberately has no binary ``independent`` field.  Role/persona
separation, context freshness, output blinding, model-family diversity,
provider diversity, and human-reviewer diversity are separate observations.
Unknown input observations remain ``"unknown"`` instead of being guessed.

``fresh_context`` is deliberately limited to context-id separation among the
five seats in one panel attempt.  This runtime receives no prior-attempt
history and therefore never claims cross-attempt freshness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_SCHEMA_PATH = (
    REPO_ROOT
    / "shared"
    / "contracts"
    / "reviewer"
    / "review_panel_provenance_input.schema.json"
)
ARTIFACT_SCHEMA_PATH = (
    REPO_ROOT
    / "shared"
    / "contracts"
    / "reviewer"
    / "review_panel_provenance.schema.json"
)
CARRIER_SCHEMA_PATH = (
    REPO_ROOT
    / "shared"
    / "contracts"
    / "reviewer"
    / "review_panel_provenance_carrier.schema.json"
)
FULL_CONTRACT_PATH = (
    REPO_ROOT / "shared" / "contracts" / "reviewer" / "full.json"
)

INPUT_VERSION = "review-panel-provenance-input/1.0"
ARTIFACT_VERSION = "review-panel-provenance/1.0"
CARRIER_VERSION = "review-panel-provenance-carrier/1.0"
REVIEW_MODE = "reviewer_full"
CONTRACT_ID = "reviewer/reviewer_full/v2"
CONTRACT_SHA256 = "e9712090d2469fea15a37b8e22d4e137afbcb2bf38d5789939c5df56738ef7af"
FRESH_CONTEXT_SCOPE = "within_panel_attempt_only"
UNKNOWN = "unknown"

EXPECTED_ROSTER = ("EIC", "R1", "R2", "R3", "DA")
AXIS_NAMES = (
    "role_separated",
    "fresh_context",
    "blind_to_peer_outputs",
    "model_family_distinct",
    "provider_distinct",
    "human_distinct",
)
SCHEMA6_MODES = frozenset(
    {
        REVIEW_MODE,
        "reviewer_methodology_focus",
        "reviewer_re_review",
        "reviewer_quick",
        "reviewer_guided",
        "reviewer_calibration",
    }
)

SEAT_FIELDS = (
    "seat_id",
    "role_id",
    "context_id",
    "peer_outputs_visible",
    "actor_type",
    "model_family",
    "provider",
    "human_reviewer_id",
)

SAME_FAMILY_TEXT = (
    "All model-executed review seats used one model family; role separation "
    "does not remove correlated-error risk."
)
UNKNOWN_FAMILY_TEXT = (
    "Model-family provenance is incomplete; cross-family separation is "
    "unknown, so correlated-error risk cannot be ruled out."
)


class ProvenanceError(ValueError):
    """Raised when a provenance manifest is structurally or semantically invalid."""


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8", errors="strict")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _raw_sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _load_schema(path: Path) -> dict[str, Any]:
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


def _json_path(parts: Iterable[Any]) -> str:
    rendered = "$"
    for part in parts:
        rendered += f"[{part}]" if isinstance(part, int) else f".{part}"
    return rendered


def _schema_errors(value: Any, path: Path) -> list[str]:
    validator = Draft202012Validator(_load_schema(path))
    errors = sorted(validator.iter_errors(value), key=lambda err: list(err.absolute_path))
    return [f"{_json_path(err.absolute_path)}: {err.message}" for err in errors]


def _duplicate_rejecting_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProvenanceError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _parse_json_bytes(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=_duplicate_rejecting_object,
        )
    except UnicodeDecodeError as exc:
        raise ProvenanceError(f"invalid UTF-8 in {label}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ProvenanceError(f"invalid JSON in {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProvenanceError(f"{label}: expected a JSON object")
    return value


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object and reject duplicate keys."""

    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ProvenanceError(f"cannot read {path}: {exc}") from exc
    return _parse_json_bytes(raw, str(path))


def _assert_canonical_contract_binding() -> None:
    """Fail if the pinned reviewer_full contract no longer matches raw bytes."""

    try:
        actual = _raw_sha256(FULL_CONTRACT_PATH.read_bytes())
    except OSError as exc:
        raise ProvenanceError(
            f"cannot read canonical reviewer_full contract: {exc}"
        ) from exc
    if actual != CONTRACT_SHA256:
        raise ProvenanceError(
            "canonical reviewer_full contract raw-byte digest drifted from the "
            "pinned provenance contract"
        )


def _normalise_seat(raw: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "seat_id": raw["seat_id"],
        "role_id": raw.get("role_id"),
        "context_id": raw.get("context_id"),
        "peer_outputs_visible": raw.get("peer_outputs_visible"),
        "actor_type": raw.get("actor_type", UNKNOWN),
        "model_family": raw.get("model_family"),
        "provider": raw.get("provider"),
        "human_reviewer_id": raw.get("human_reviewer_id"),
    }


def _semantic_manifest_errors(seats: Sequence[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, seat in enumerate(seats):
        seat_id = seat["seat_id"]
        if seat_id in seen:
            errors.append(f"$.seats[{index}].seat_id: duplicate seat_id {seat_id!r}")
        seen.add(seat_id)

        actor_type = seat["actor_type"]
        if actor_type == "human" and (
            seat["model_family"] is not None or seat["provider"] is not None
        ):
            errors.append(
                f"$.seats[{index}]: actor_type 'human' cannot carry model-family "
                "or provider identity; use 'hybrid' when both participated"
            )
        if actor_type == "model" and seat["human_reviewer_id"] is not None:
            errors.append(
                f"$.seats[{index}]: actor_type 'model' cannot carry a human "
                "reviewer identity; use 'hybrid' when both participated"
            )

    actual_roster = tuple(seat["seat_id"] for seat in seats)
    if actual_roster != EXPECTED_ROSTER:
        errors.append(
            "$.seats: reviewer_full roster must be ordered exactly as "
            "EIC, R1, R2, R3, DA"
        )
    return errors


def normalize_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and fully populate omitted observations with unknown/null values."""

    schema_errors = _schema_errors(manifest, INPUT_SCHEMA_PATH)
    if schema_errors:
        raise ProvenanceError("; ".join(schema_errors))
    _assert_canonical_contract_binding()
    seats = [_normalise_seat(seat) for seat in manifest["seats"]]
    semantic_errors = _semantic_manifest_errors(seats)
    if semantic_errors:
        raise ProvenanceError("; ".join(semantic_errors))
    return {
        "schema_version": INPUT_VERSION,
        "panel_id": manifest["panel_id"],
        "mode": REVIEW_MODE,
        "contract_id": CONTRACT_ID,
        "contract_sha256": CONTRACT_SHA256,
        "seats": seats,
    }


def _all_seats_unique(seats: Sequence[Mapping[str, Any]], field: str) -> bool | str:
    """Compare observations only within this one panel attempt.

    In particular, unique ``context_id`` values do not establish that those
    identifiers were unused in a previous attempt; no history is accepted by
    this contract.
    """

    values = [seat[field] for seat in seats]
    known = [value for value in values if value is not None]
    if len(set(known)) != len(known):
        return False
    if len(known) != len(values):
        return UNKNOWN
    return True


def _blind_axis(seats: Sequence[Mapping[str, Any]]) -> bool | str:
    observations = [seat["peer_outputs_visible"] for seat in seats]
    if any(value is True for value in observations):
        return False
    if any(value is None for value in observations):
        return UNKNOWN
    return True


def _model_distinct_axis(
    seats: Sequence[Mapping[str, Any]], field: str
) -> bool | str:
    """Return whether at least two model identities are proven distinct.

    Two known values prove diversity even when another seat is unknown.  A
    false value requires at least one model-involved seat, complete observations
    for all possibly model-involved seats, and only one distinct value.
    """

    model_involved = [
        seat
        for seat in seats
        if seat["actor_type"] in {"model", "hybrid"}
        or seat["model_family"] is not None
        or seat["provider"] is not None
    ]
    known = {seat[field] for seat in model_involved if seat[field] is not None}
    if len(known) >= 2:
        return True
    actor_unknown = any(seat["actor_type"] == UNKNOWN for seat in seats)
    missing_identity = any(seat[field] is None for seat in model_involved)
    if not model_involved or actor_unknown or missing_identity:
        return UNKNOWN
    return False


def _human_distinct_axis(seats: Sequence[Mapping[str, Any]]) -> bool | str:
    """Return whether at least two distinct human reviewers are proven present."""

    known_ids = {
        seat["human_reviewer_id"]
        for seat in seats
        if seat["human_reviewer_id"] is not None
    }
    if len(known_ids) >= 2:
        return True

    possibly_human = [
        seat for seat in seats if seat["actor_type"] in {"human", "hybrid", UNKNOWN}
    ]
    missing_identity = any(
        seat["human_reviewer_id"] is None for seat in possibly_human
    )
    if missing_identity:
        return UNKNOWN
    return False


def derive_axes(seats: Sequence[Mapping[str, Any]]) -> dict[str, bool | str]:
    """Derive the six closed provenance axes from normalized seat evidence."""

    return {
        "role_separated": _all_seats_unique(seats, "role_id"),
        "fresh_context": _all_seats_unique(seats, "context_id"),
        "blind_to_peer_outputs": _blind_axis(seats),
        "model_family_distinct": _model_distinct_axis(seats, "model_family"),
        "provider_distinct": _model_distinct_axis(seats, "provider"),
        "human_distinct": _human_distinct_axis(seats),
    }


def _execution_topology_projection(
    normalized: Mapping[str, Any], axes: Mapping[str, bool | str]
) -> dict[str, Any]:
    """Return the stable configuration projection used for profile matching.

    Invocation context identifiers are intentionally excluded so the key can
    match the same configuration across attempts. Their within-panel
    ``fresh_context`` status and fixed scope are retained. This projection does
    not compare attempts or attest that context ids are new across history.
    """

    seats = normalized["seats"]
    return {
        "schema_version": "review-panel-execution-topology/1.0",
        "mode": normalized["mode"],
        "contract_id": normalized["contract_id"],
        "contract_sha256": normalized["contract_sha256"],
        "seats": [
            {
                field: seat[field]
                for field in (
                    "seat_id",
                    "role_id",
                    "peer_outputs_visible",
                    "actor_type",
                    "model_family",
                    "provider",
                    "human_reviewer_id",
                )
            }
            for seat in seats
        ],
        "axes": dict(axes),
        "fresh_context_scope": FRESH_CONTEXT_SCOPE,
    }


def _correlated_error_disclosure(
    model_family_distinct: bool | str,
) -> dict[str, Any]:
    if model_family_distinct is False:
        return {
            "required": True,
            "reason": "same_model_family",
            "text": SAME_FAMILY_TEXT,
        }
    if model_family_distinct == UNKNOWN:
        return {
            "required": True,
            "reason": "model_family_unknown",
            "text": UNKNOWN_FAMILY_TEXT,
        }
    return {
        "required": False,
        "reason": "multiple_model_families",
        "text": None,
    }


def build_artifact(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Build the canonical typed provenance artifact from one input manifest."""

    normalized = normalize_manifest(manifest)
    seats = normalized["seats"]
    axes = derive_axes(seats)
    artifact = {
        "schema_version": ARTIFACT_VERSION,
        "panel_id": normalized["panel_id"],
        "mode": normalized["mode"],
        "contract_id": normalized["contract_id"],
        "contract_sha256": normalized["contract_sha256"],
        "normalized_manifest_sha256": _sha256(normalized),
        "execution_topology_sha256": _sha256(
            _execution_topology_projection(normalized, axes)
        ),
        "seats": seats,
        "axes": axes,
        "fresh_context_scope": FRESH_CONTEXT_SCOPE,
        "independence_claim": "not_computed_from_personas",
        "correlated_error_disclosure": _correlated_error_disclosure(
            axes["model_family_distinct"]
        ),
    }
    errors = _schema_errors(artifact, ARTIFACT_SCHEMA_PATH)
    if errors:  # Defensive: a builder/schema drift is a hard failure.
        raise ProvenanceError("builder emitted invalid artifact: " + "; ".join(errors))
    return artifact


def validate_artifact(artifact: Mapping[str, Any]) -> list[str]:
    """Schema-check and replay every derived field; return deterministic errors."""

    errors = _schema_errors(artifact, ARTIFACT_SCHEMA_PATH)
    if errors:
        return errors

    projected_manifest = {
        "schema_version": INPUT_VERSION,
        "panel_id": artifact["panel_id"],
        "mode": artifact["mode"],
        "contract_id": artifact["contract_id"],
        "contract_sha256": artifact["contract_sha256"],
        "seats": artifact["seats"],
    }
    try:
        expected = build_artifact(projected_manifest)
    except ProvenanceError as exc:
        return [f"artifact seats cannot be replayed: {exc}"]
    if artifact != expected:
        for field in (
            "normalized_manifest_sha256",
            "execution_topology_sha256",
            "axes",
            "fresh_context_scope",
            "independence_claim",
            "correlated_error_disclosure",
        ):
            if artifact.get(field) != expected.get(field):
                errors.append(f"$.{field}: value does not match deterministic replay")
    return errors


def _unknown_axes() -> dict[str, str]:
    return {axis: UNKNOWN for axis in AXIS_NAMES}


def invalid_carrier(reason: str) -> dict[str, Any]:
    """Return one closed, fail-visible Schema 6 invalid carrier."""

    carrier = {
        "schema_version": CARRIER_VERSION,
        "status": "invalid",
        "review_mode": REVIEW_MODE,
        "reason": reason,
        "fresh_context_scope": FRESH_CONTEXT_SCOPE,
        "axes": _unknown_axes(),
    }
    errors = _schema_errors(carrier, CARRIER_SCHEMA_PATH)
    if errors:
        raise ProvenanceError("invalid carrier reason: " + "; ".join(errors))
    return carrier


def _validate_artifact_ref(artifact_ref: str) -> None:
    if not artifact_ref:
        raise ProvenanceError("artifact_path must not be empty")
    if "\\" in artifact_ref or "//" in artifact_ref:
        raise ProvenanceError(
            "artifact_path must use canonical single forward-slash separators"
        )
    path = Path(artifact_ref)
    if path.is_absolute() or any(part in {".", "..", ""} for part in path.parts):
        raise ProvenanceError(
            "artifact_path must be a canonical relative path without traversal"
        )


def _resolve_artifact_ref(artifact_root: Path, artifact_ref: str) -> Path:
    _validate_artifact_ref(artifact_ref)
    root = artifact_root.resolve()
    candidate = (root / artifact_ref).resolve(strict=False)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ProvenanceError("artifact_path resolves outside artifact root") from exc
    return candidate


def build_carrier(
    artifact_path: Path | None, *, artifact_ref: str | None = None
) -> dict[str, Any]:
    """Build a valid carrier or one explicit invalid execution state.

    This helper computes ``artifact_sha256`` from exact raw bytes. It never
    accepts a caller-asserted digest and never repairs an invalid artifact.
    """

    if artifact_path is None:
        return invalid_carrier("absent")
    try:
        raw = artifact_path.read_bytes()
    except OSError:
        return invalid_carrier("unreachable")
    try:
        artifact = _parse_json_bytes(raw, str(artifact_path))
    except ProvenanceError:
        return invalid_carrier("schema_invalid")

    if _schema_errors(artifact, ARTIFACT_SCHEMA_PATH):
        return invalid_carrier("schema_invalid")
    if validate_artifact(artifact):
        return invalid_carrier("replay_invalid")

    ref = artifact_ref if artifact_ref is not None else artifact_path.name
    _validate_artifact_ref(ref)
    carrier = {
        "schema_version": CARRIER_VERSION,
        "status": "valid",
        "review_mode": REVIEW_MODE,
        "artifact_path": ref,
        "artifact_sha256": _raw_sha256(raw),
        "normalized_manifest_sha256": artifact["normalized_manifest_sha256"],
        "execution_topology_sha256": artifact["execution_topology_sha256"],
        "fresh_context_scope": artifact["fresh_context_scope"],
        "axes": artifact["axes"],
    }
    errors = _schema_errors(carrier, CARRIER_SCHEMA_PATH)
    if errors:
        raise ProvenanceError("builder emitted invalid carrier: " + "; ".join(errors))
    return carrier


def verify_carrier(
    carrier: Any, artifact_root: Path
) -> tuple[str | None, list[str]]:
    """Verify a Schema 6 carrier and classify any fail-visible state.

    ``None`` means the valid branch passed raw-byte, schema, deterministic
    replay, normalized-manifest, topology, scope, and six-axis comparison.
    Otherwise the first tuple item is one invalid-union reason.
    """

    schema_errors = _schema_errors(carrier, CARRIER_SCHEMA_PATH)
    if schema_errors:
        return "schema_invalid", schema_errors
    if carrier["status"] == "invalid":
        return carrier["reason"], []

    try:
        artifact_path = _resolve_artifact_ref(
            artifact_root, carrier["artifact_path"]
        )
    except ProvenanceError as exc:
        return "schema_invalid", [str(exc)]
    try:
        raw = artifact_path.read_bytes()
    except OSError as exc:
        return "unreachable", [f"cannot read artifact_path: {exc}"]
    if _raw_sha256(raw) != carrier["artifact_sha256"]:
        return "digest_mismatch", [
            "artifact_sha256 does not match exact artifact bytes"
        ]
    try:
        artifact = _parse_json_bytes(raw, carrier["artifact_path"])
    except ProvenanceError as exc:
        return "schema_invalid", [str(exc)]

    artifact_schema_errors = _schema_errors(artifact, ARTIFACT_SCHEMA_PATH)
    if artifact_schema_errors:
        return "schema_invalid", artifact_schema_errors
    replay_errors = validate_artifact(artifact)
    if replay_errors:
        return "replay_invalid", replay_errors

    comparison_errors: list[str] = []
    for field in (
        "normalized_manifest_sha256",
        "execution_topology_sha256",
        "fresh_context_scope",
        "axes",
    ):
        if carrier[field] != artifact[field]:
            comparison_errors.append(
                f"$.{field}: carrier value does not match replay-valid artifact"
            )
    if comparison_errors:
        return "replay_invalid", comparison_errors
    return None, []


def validate_schema6_binding(
    schema6: Mapping[str, Any], review_mode: str, artifact_root: Path
) -> tuple[str | None, list[str]]:
    """Enforce mode-scoped presence and validate the Schema 6 carrier.

    ``reviewer_full`` requires the field. Every other closed current mode must
    omit it because this provenance family has no contract for those modes.
    """

    if review_mode not in SCHEMA6_MODES:
        return "schema_invalid", [
            f"unsupported review mode {review_mode!r}; closed mode handling applies"
        ]
    present = "review_panel_provenance" in schema6
    if review_mode != REVIEW_MODE:
        if present:
            return "schema_invalid", [
                "$.review_panel_provenance: must be omitted outside reviewer_full"
            ]
        return None, []
    if not present:
        return "absent", [
            "$.review_panel_provenance: reviewer_full requires an explicit "
            "valid or invalid carrier"
        ]
    return verify_carrier(schema6["review_panel_provenance"], artifact_root)


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build", help="build a typed artifact")
    build.add_argument("manifest", type=Path)
    build.add_argument("--output", type=Path)
    validate = subparsers.add_parser("validate", help="replay-validate an artifact")
    validate.add_argument("artifact", type=Path)
    carrier = subparsers.add_parser(
        "build-carrier", help="build a fail-visible Schema 6 carrier"
    )
    carrier.add_argument("artifact", type=Path, nargs="?")
    carrier.add_argument(
        "--artifact-ref",
        help="canonical relative reference persisted in the carrier",
    )
    carrier.add_argument("--output", type=Path)
    verify = subparsers.add_parser(
        "validate-carrier",
        help="verify carrier raw digest, artifact schema, replay, and bindings",
    )
    verify.add_argument("carrier", type=Path)
    verify.add_argument("--artifact-root", type=Path, required=True)
    schema6 = subparsers.add_parser(
        "validate-schema6",
        help="enforce closed mode presence and verify Schema 6 provenance",
    )
    schema6.add_argument("schema6", type=Path)
    schema6.add_argument("--mode", choices=sorted(SCHEMA6_MODES), required=True)
    schema6.add_argument("--artifact-root", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "build":
            artifact = build_artifact(load_json(args.manifest))
            if args.output is None:
                print(json.dumps(artifact, ensure_ascii=False, sort_keys=True, indent=2))
            else:
                _write_json(args.output, artifact)
            return 0

        if args.command == "validate":
            artifact = load_json(args.artifact)
            errors = validate_artifact(artifact)
            if errors:
                for error in errors:
                    print(error, file=sys.stderr)
                return 1
            print("review-panel provenance: PASS")
            return 0

        if args.command == "build-carrier":
            carrier = build_carrier(args.artifact, artifact_ref=args.artifact_ref)
            if args.output is None:
                print(json.dumps(carrier, ensure_ascii=False, sort_keys=True, indent=2))
            else:
                _write_json(args.output, carrier)
            if carrier["status"] == "invalid":
                print(
                    f"review-panel provenance carrier: INVALID ({carrier['reason']})",
                    file=sys.stderr,
                )
                return 2
            return 0

        if args.command == "validate-carrier":
            carrier = load_json(args.carrier)
            state, errors = verify_carrier(carrier, args.artifact_root)
        else:
            schema6 = load_json(args.schema6)
            state, errors = validate_schema6_binding(
                schema6, args.mode, args.artifact_root
            )
        if state is not None:
            for error in errors:
                print(error, file=sys.stderr)
            print(
                f"review-panel provenance carrier: INVALID ({state})",
                file=sys.stderr,
            )
            return 2
        print("review-panel provenance carrier: PASS")
        return 0
    except ProvenanceError as exc:
        print(f"review-panel provenance: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
