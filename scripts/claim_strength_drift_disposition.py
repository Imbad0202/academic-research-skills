#!/usr/bin/env python3
"""Build and validate explicit author dispositions for detected E6 drift.

The runtime is hermetic: it opens only explicitly named local artifacts, never
calls a model or network service, never reads an ambient clock, and never
supplies an author choice. Build and replay validation both bind every choice to
the raw bytes of one explicitly named session-event artifact. The durable
sidecar retains the event id, recomputed digest, and honest provenance, but not
the transient path or raw message. Byte binding does not authenticate that the
bytes came from a user, identify their author, or establish scientific warrant.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import stat
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any

import jsonschema


REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_ROOT = REPO_ROOT / "shared" / "contracts" / "revision"
FINDING_SCHEMA_PATH = CONTRACT_ROOT / "claim_strength_drift_findings.schema.json"
INPUT_SCHEMA_PATH = (
    CONTRACT_ROOT / "claim_strength_drift_disposition_input.schema.json"
)
SIDECAR_SCHEMA_PATH = CONTRACT_ROOT / "claim_strength_drift_disposition.schema.json"
MAX_ARTIFACT_BYTES = 8 * 1024 * 1024


class ContractError(ValueError):
    """Closed validation failure collection."""

    def __init__(self, failures: list[str]):
        self.failures = failures
        super().__init__("; ".join(failures))


def bytes_hash(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _reject_noncanonical_numbers(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ContractError([f"{path}: non-finite number is forbidden"])
        raise ContractError([f"{path}: floating-point values are outside this contract"])
    if isinstance(value, dict):
        for key, child in value.items():
            _reject_noncanonical_numbers(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_noncanonical_numbers(child, f"{path}[{index}]")


def canonical_bytes(value: Any) -> bytes:
    _reject_noncanonical_numbers(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return bytes_hash(canonical_bytes(value))


def _read_path_once(path: Path, label: str) -> bytes:
    raw, _ = _read_path_once_with_identity(path, label)
    return raw


def _read_path_once_with_identity(
    path: Path, label: str
) -> tuple[bytes, tuple[int, int]]:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise ContractError(
            [f"{label}: cannot open regular non-symlink file {path}: {exc}"]
        ) from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise ContractError([f"{label}: artifact is not a regular file"])
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, min(1024 * 1024, MAX_ARTIFACT_BYTES + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > MAX_ARTIFACT_BYTES:
                raise ContractError(
                    [f"{label}: artifact exceeds {MAX_ARTIFACT_BYTES} bytes"]
                )
        after = os.fstat(fd)
        before_key = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        after_key = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        if before_key != after_key or total != after.st_size:
            raise ContractError([f"{label}: artifact changed while being read"])
        return b"".join(chunks), (after.st_dev, after.st_ino)
    finally:
        os.close(fd)


def _json_from_raw(raw: bytes, label: str) -> dict[str, Any]:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, child in pairs:
            if key in value:
                raise ValueError(f"duplicate object key {key!r}")
            value[key] = child
        return value

    def reject_constant(token: str) -> None:
        raise ValueError(f"non-finite JSON constant {token!r}")

    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ContractError([f"{label}: invalid strict UTF-8 JSON: {exc}"]) from exc
    if not isinstance(value, dict):
        raise ContractError([f"{label}: top level must be an object"])
    return value


def load_json_path(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    raw = _read_path_once(path, label)
    return _json_from_raw(raw, label), raw


def _load_schema(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(value)
    return value


def _schema_failures(
    value: dict[str, Any], schema_path: Path, label: str
) -> list[str]:
    validator = jsonschema.Draft202012Validator(_load_schema(schema_path))
    errors = sorted(
        validator.iter_errors(value),
        key=lambda error: [str(part) for part in error.absolute_path],
    )
    failures: list[str] = []
    for error in errors:
        path = "/".join(str(part) for part in error.absolute_path) or "(root)"
        failures.append(f"{label} schema {path}: {error.message}")
    return failures


def _meaningful(value: str) -> bool:
    normalized = unicodedata.normalize("NFKC", value)
    return any(unicodedata.category(char)[0] in {"L", "N", "S"} for char in normalized)


def _validate_findings(findings: dict[str, Any]) -> None:
    failures = _schema_failures(findings, FINDING_SCHEMA_PATH, "finding set")
    rows = findings.get("findings", [])
    if isinstance(rows, list):
        expected_ids = [f"ADV-E6-{index}" for index in range(1, len(rows) + 1)]
        actual_ids = [row.get("finding_id") for row in rows if isinstance(row, dict)]
        if actual_ids != expected_ids:
            failures.append(
                "finding set: findings must use the complete ordered sequence "
                f"{expected_ids!r}, got {actual_ids!r}"
            )
        rounds = [row.get("revision_round") for row in rows if isinstance(row, dict)]
        if all(isinstance(round_no, int) for round_no in rounds) and rounds != sorted(rounds):
            failures.append("finding set: revision_round values must be nondecreasing")
    if failures:
        raise ContractError(failures)


def _validate_author_input(
    findings: dict[str, Any], author_input: dict[str, Any]
) -> None:
    failures = _schema_failures(author_input, INPUT_SCHEMA_PATH, "author input")
    rows = findings.get("findings", [])
    if findings.get("status") != "completed":
        failures.append("author input: dispositions require a completed E6 finding set")
    if not rows:
        failures.append("author input: no detected E6 finding requires disposition")

    expected_ids = [row.get("finding_id") for row in rows if isinstance(row, dict)]
    decisions = author_input.get("dispositions", [])
    actual_ids = [row.get("finding_id") for row in decisions if isinstance(row, dict)]
    if actual_ids != expected_ids:
        failures.append(
            "author input: dispositions must cover each finding exactly once in finding order; "
            f"expected {expected_ids!r}, got {actual_ids!r}"
        )

    events = author_input.get("session_event_artifacts", [])
    event_ids = [row.get("event_id") for row in events if isinstance(row, dict)]
    if len(event_ids) != len(set(event_ids)):
        failures.append("author input: session-event ids must be unique")
    paths = [
        row.get("raw_session_event_path") for row in events if isinstance(row, dict)
    ]
    if all(isinstance(path, str) for path in paths):
        normalized_paths = [os.path.normpath(path) for path in paths]
        if len(normalized_paths) != len(set(normalized_paths)):
            failures.append(
                "author input: raw session-event artifact paths must be unique"
            )
        for index, path in enumerate(paths):
            if not Path(path).is_absolute():
                failures.append(
                    "author input: session_event_artifacts"
                    f"[{index}].raw_session_event_path must be absolute"
                )
    referenced = [
        row.get("session_event_id") for row in decisions if isinstance(row, dict)
    ]
    if len(referenced) != len(set(referenced)):
        failures.append(
            "author input: each session-event artifact may map to only one disposition"
        )
    unknown = sorted(set(referenced) - set(event_ids))
    unused = sorted(set(event_ids) - set(referenced))
    if unknown:
        failures.append(f"author input: unknown session-event references {unknown!r}")
    if unused:
        failures.append(f"author input: unreferenced session-event artifacts {unused!r}")
    if event_ids != referenced:
        failures.append(
            "author input: session-event artifacts must be in one-to-one "
            "disposition order"
        )

    for index, decision in enumerate(decisions):
        if not isinstance(decision, dict):
            continue
        if decision.get("action") == "authorize_with_reason":
            reason = decision.get("reason")
            if isinstance(reason, str) and not _meaningful(reason):
                failures.append(
                    f"author input: dispositions[{index}].reason must contain a letter, number, or symbol"
                )
    if failures:
        raise ContractError(failures)


def _validate_event_bytes(
    declared_events: list[dict[str, Any]], event_raw_by_id: dict[str, bytes], label: str
) -> None:
    failures: list[str] = []
    expected_ids = [
        row.get("event_id") for row in declared_events if isinstance(row, dict)
    ]
    actual_ids = list(event_raw_by_id)
    if actual_ids != expected_ids:
        failures.append(
            f"{label}: exact event-id mapping required in declared order; "
            f"expected {expected_ids!r}, got {actual_ids!r}"
        )
    for index, event in enumerate(declared_events):
        if not isinstance(event, dict):
            continue
        event_id = event.get("event_id")
        raw = event_raw_by_id.get(event_id)
        if raw is None:
            continue
        if not raw:
            failures.append(f"{label}: event {event_id!r} has empty raw bytes")
        declared = event.get("raw_session_event_sha256")
        recomputed = bytes_hash(raw)
        if declared != recomputed:
            failures.append(
                f"{label}: event binding [{index}].raw_session_event_sha256 "
                "does not bind the explicitly named raw event bytes"
            )
    if failures:
        raise ContractError(failures)


def _load_build_event_artifacts(
    author_input: dict[str, Any],
) -> dict[str, bytes]:
    failures = _schema_failures(author_input, INPUT_SCHEMA_PATH, "author input")
    if failures:
        raise ContractError(failures)
    result: dict[str, bytes] = {}
    identities: dict[tuple[int, int], str] = {}
    for event in author_input["session_event_artifacts"]:
        event_id = event["event_id"]
        path = Path(event["raw_session_event_path"])
        if not path.is_absolute():
            raise ContractError(
                [f"event artifact {event_id}: path must be absolute: {path}"]
            )
        raw, identity = _read_path_once_with_identity(path, f"event artifact {event_id}")
        prior = identities.get(identity)
        if prior is not None:
            raise ContractError(
                [
                    "event artifacts: duplicate file mapping for "
                    f"{prior!r} and {event_id!r}"
                ]
            )
        identities[identity] = event_id
        result[event_id] = raw
    return result


def _parse_validate_event_artifacts(specs: list[str]) -> dict[str, bytes]:
    parsed: list[tuple[str, Path]] = []
    failures: list[str] = []
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for spec in specs:
        if "=" not in spec:
            failures.append(
                "event artifact mapping must have the exact form EVENT_ID=/absolute/path"
            )
            continue
        event_id, path_text = spec.split("=", 1)
        path = Path(path_text)
        normalized_path = os.path.normpath(path_text)
        if not event_id or not path_text:
            failures.append(
                "event artifact mapping must have the exact form EVENT_ID=/absolute/path"
            )
            continue
        if event_id in seen_ids:
            failures.append(f"event artifact mapping duplicates event id {event_id!r}")
        if normalized_path in seen_paths:
            failures.append(f"event artifact mapping duplicates path {path_text!r}")
        if not path.is_absolute():
            failures.append(f"event artifact {event_id}: path must be absolute: {path}")
        seen_ids.add(event_id)
        seen_paths.add(normalized_path)
        parsed.append((event_id, path))
    if failures:
        raise ContractError(failures)

    result: dict[str, bytes] = {}
    identities: dict[tuple[int, int], str] = {}
    for event_id, path in parsed:
        raw, identity = _read_path_once_with_identity(path, f"event artifact {event_id}")
        prior = identities.get(identity)
        if prior is not None:
            raise ContractError(
                [
                    "event artifacts: duplicate file mapping for "
                    f"{prior!r} and {event_id!r}"
                ]
            )
        identities[identity] = event_id
        result[event_id] = raw
    return result


def _validate_evidence_bindings(
    findings: dict[str, Any], final_draft_raw: bytes, revision_bundle_raw: bytes
) -> None:
    failures: list[str] = []
    if findings.get("final_draft_sha256") != bytes_hash(final_draft_raw):
        failures.append("finding set: final_draft_sha256 does not bind exact draft bytes")
    if findings.get("revision_evidence_bundle_sha256") != bytes_hash(
        revision_bundle_raw
    ):
        failures.append(
            "finding set: revision_evidence_bundle_sha256 does not bind exact bundle bytes"
        )
    if failures:
        raise ContractError(failures)


def _derive_pipeline_action(dispositions: list[dict[str, Any]]) -> str:
    actions = {row["action"] for row in dispositions}
    if "pause" in actions:
        return "paused"
    if "restore" in actions:
        return "restore_required"
    return "authorized_to_continue"


def build_sidecar(
    findings: dict[str, Any],
    finding_raw: bytes,
    author_input: dict[str, Any],
    final_draft_raw: bytes,
    revision_bundle_raw: bytes,
    event_raw_by_id: dict[str, bytes],
) -> dict[str, Any]:
    _validate_findings(findings)
    _validate_author_input(findings, author_input)
    _validate_evidence_bindings(findings, final_draft_raw, revision_bundle_raw)
    _validate_event_bytes(
        author_input["session_event_artifacts"], event_raw_by_id, "author input"
    )

    input_by_id = {row["finding_id"]: row for row in author_input["dispositions"]}
    dispositions: list[dict[str, Any]] = []
    for finding in findings["findings"]:
        chosen = input_by_id[finding["finding_id"]]
        row = {
            "finding_id": finding["finding_id"],
            "finding_sha256": canonical_hash(finding),
            "session_event_id": chosen["session_event_id"],
            "action": chosen["action"],
        }
        if chosen["action"] == "authorize_with_reason":
            row["reason"] = chosen["reason"]
        dispositions.append(row)

    session_event_bindings = []
    for event in author_input["session_event_artifacts"]:
        event_id = event["event_id"]
        session_event_bindings.append(
            {
                "event_id": event_id,
                "raw_session_event_sha256": bytes_hash(event_raw_by_id[event_id]),
                "source_assertion": event["source_assertion"],
                "actor_role_assertion": event["actor_role_assertion"],
                "byte_binding": "runtime_recomputed_from_explicit_local_artifact",
                "authenticity_status": "not_authenticated",
            }
        )

    sidecar = {
        "schema_version": "claim-strength-drift-disposition/1.0",
        "finding_set_sha256": bytes_hash(finding_raw),
        "final_draft_sha256": findings["final_draft_sha256"],
        "revision_evidence_bundle_sha256": findings[
            "revision_evidence_bundle_sha256"
        ],
        "disposition_status": "complete",
        "session_event_bindings": session_event_bindings,
        "dispositions": dispositions,
        "pipeline_action": _derive_pipeline_action(dispositions),
    }
    validate_sidecar(
        findings,
        finding_raw,
        sidecar,
        final_draft_raw,
        revision_bundle_raw,
        event_raw_by_id,
    )
    return sidecar


def validate_sidecar(
    findings: dict[str, Any],
    finding_raw: bytes,
    sidecar: dict[str, Any],
    final_draft_raw: bytes,
    revision_bundle_raw: bytes,
    event_raw_by_id: dict[str, bytes],
) -> None:
    _validate_findings(findings)
    _validate_evidence_bindings(findings, final_draft_raw, revision_bundle_raw)
    failures = _schema_failures(sidecar, SIDECAR_SCHEMA_PATH, "sidecar")
    if not findings.get("findings"):
        failures.append("sidecar: no detected E6 finding requires a disposition sidecar")
    if findings.get("status") != "completed":
        failures.append("sidecar: finding set status must be completed")

    for field in (
        "final_draft_sha256",
        "revision_evidence_bundle_sha256",
    ):
        if sidecar.get(field) != findings.get(field):
            failures.append(f"sidecar: {field} does not match finding set")
    if sidecar.get("finding_set_sha256") != bytes_hash(finding_raw):
        failures.append("sidecar: finding_set_sha256 does not bind exact finding-set bytes")

    finding_rows = findings.get("findings", [])
    sidecar_rows = sidecar.get("dispositions", [])
    expected_ids = [row.get("finding_id") for row in finding_rows if isinstance(row, dict)]
    actual_ids = [row.get("finding_id") for row in sidecar_rows if isinstance(row, dict)]
    if actual_ids != expected_ids:
        failures.append(
            "sidecar: dispositions must cover each finding exactly once in finding order; "
            f"expected {expected_ids!r}, got {actual_ids!r}"
        )
    if len(sidecar_rows) == len(finding_rows):
        for index, (finding, disposition) in enumerate(zip(finding_rows, sidecar_rows)):
            if not isinstance(finding, dict) or not isinstance(disposition, dict):
                continue
            if disposition.get("finding_sha256") != canonical_hash(finding):
                failures.append(
                    f"sidecar: dispositions[{index}].finding_sha256 does not bind its finding"
                )
            if disposition.get("action") == "authorize_with_reason":
                reason = disposition.get("reason")
                if isinstance(reason, str) and not _meaningful(reason):
                    failures.append(
                        f"sidecar: dispositions[{index}].reason must contain a letter, number, or symbol"
                    )

    events = sidecar.get("session_event_bindings", [])
    event_ids = [row.get("event_id") for row in events if isinstance(row, dict)]
    if len(event_ids) != len(set(event_ids)):
        failures.append("sidecar: session-event ids must be unique")
    references = [
        row.get("session_event_id") for row in sidecar_rows if isinstance(row, dict)
    ]
    if len(references) != len(set(references)):
        failures.append(
            "sidecar: each session-event artifact may map to only one disposition"
        )
    unknown = sorted(set(references) - set(event_ids))
    unused = sorted(set(event_ids) - set(references))
    if unknown:
        failures.append(f"sidecar: unknown session-event references {unknown!r}")
    if unused:
        failures.append(f"sidecar: unreferenced session-event bindings {unused!r}")
    if event_ids != references:
        failures.append(
            "sidecar: session-event bindings must be in one-to-one disposition order"
        )

    if not failures:
        try:
            _validate_event_bytes(events, event_raw_by_id, "sidecar replay")
        except ContractError as exc:
            failures.extend(exc.failures)

    if all(isinstance(row, dict) and "action" in row for row in sidecar_rows):
        expected_action = _derive_pipeline_action(sidecar_rows)
        if sidecar.get("pipeline_action") != expected_action:
            failures.append(
                "sidecar: pipeline_action is not the mechanical projection of dispositions; "
                f"expected {expected_action!r}"
            )
    if failures:
        raise ContractError(failures)


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    if not path.parent.is_dir():
        raise ContractError([f"output: parent directory does not exist: {path.parent}"])
    payload = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False).encode(
        "utf-8"
    ) + b"\n"
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f".{path.name}.", dir=path.parent, delete=False
        ) as handle:
            temporary = handle.name
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="build a disposition sidecar")
    build.add_argument("--finding-set", type=Path, required=True)
    build.add_argument("--author-input", type=Path, required=True)
    build.add_argument("--final-draft", type=Path, required=True)
    build.add_argument("--revision-evidence-bundle", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)

    validate = subparsers.add_parser("validate", help="validate an existing sidecar")
    validate.add_argument("--finding-set", type=Path, required=True)
    validate.add_argument("--sidecar", type=Path, required=True)
    validate.add_argument("--final-draft", type=Path, required=True)
    validate.add_argument("--revision-evidence-bundle", type=Path, required=True)
    validate.add_argument(
        "--event-artifact",
        action="append",
        required=True,
        metavar="EVENT_ID=/ABSOLUTE/PATH",
        help=(
            "repeat once per disposition to replay-bind the event id to exact "
            "local raw session-event bytes"
        ),
    )

    args = parser.parse_args(argv)
    try:
        findings, finding_raw = load_json_path(args.finding_set, "finding set")
        final_draft_raw = _read_path_once(args.final_draft, "final draft")
        revision_bundle_raw = _read_path_once(
            args.revision_evidence_bundle, "revision evidence bundle"
        )
        if args.command == "build":
            author_input, _ = load_json_path(args.author_input, "author input")
            event_raw_by_id = _load_build_event_artifacts(author_input)
            sidecar = build_sidecar(
                findings,
                finding_raw,
                author_input,
                final_draft_raw,
                revision_bundle_raw,
                event_raw_by_id,
            )
            _atomic_write_json(args.output, sidecar)
            print(
                json.dumps(
                    {
                        "status": "built",
                        "pipeline_action": sidecar["pipeline_action"],
                        "findings": len(sidecar["dispositions"]),
                        "output": str(args.output),
                    },
                    sort_keys=True,
                )
            )
        else:
            sidecar, _ = load_json_path(args.sidecar, "sidecar")
            event_raw_by_id = _parse_validate_event_artifacts(args.event_artifact)
            validate_sidecar(
                findings,
                finding_raw,
                sidecar,
                final_draft_raw,
                revision_bundle_raw,
                event_raw_by_id,
            )
            print(
                json.dumps(
                    {
                        "status": "valid",
                        "pipeline_action": sidecar["pipeline_action"],
                        "findings": len(sidecar["dispositions"]),
                    },
                    sort_keys=True,
                )
            )
    except ContractError as exc:
        for failure in exc.failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
