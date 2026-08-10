#!/usr/bin/env python3
"""Build, replay-validate, and render the hermetic #672 advisory.

The semantic observations are explicit untrusted inputs.  This module performs
only closed-contract validation, exact-byte hashing/replay, deterministic
serialization, and bounded rendering.  It never calls a model, network, clock,
subprocess, cache, or directory discovery surface.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
import unicodedata
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, NoReturn
from urllib.parse import unquote


SIDECAR_SCHEMA_VERSION = "preregistration-artifact/1.0"
MANIFEST_SCHEMA_VERSION = "cross-document-source-manifest/1.0"
DRAFT_SCHEMA_VERSION = "cross-document-consistency-advisory-draft/1.0"
REPORT_SCHEMA_VERSION = "cross-document-consistency-advisory/1.0"
EVIDENCE_SCHEMA_VERSION = "evidence-row/1.2"
SURFACE = "cross_document_consistency"
LAYER = "LLM-ADVISORY"
EVALUATION_STATUS = "UNMEASURED"

MAX_DRAFT_BYTES = 16 * 1024 * 1024
MAX_MANIFEST_BYTES = 1 * 1024 * 1024
MAX_SIDECAR_BYTES = 1 * 1024 * 1024
MAX_FINAL_BYTES = 32 * 1024 * 1024
MAX_ACCEPTED_DRAFT_BYTES = 8 * 1024 * 1024
MAX_PREREGISTRATION_BYTES = 64 * 1024 * 1024
MAX_TOTAL_SOURCE_BYTES = 72 * 1024 * 1024
MAX_OBSERVATIONS = 4096
MAX_JSON_DEPTH = 100
MAX_JSON_NODES = 1_000_000
MAX_PAGE_SIZE = 25
MAX_IDENTIFIER = 200
MAX_PATH_CODEPOINTS = 1024
MAX_EXTERNAL_CODEPOINTS = 1000
MAX_EXTERNAL_WORDS = 25
MAX_ENCODED_ANCHOR = 12000

TEMPLATE_SHA256 = "40054e26c527ff3dd237a5eef3fee60b821cf8549e210d48a057005333c8e0d2"
LOCATOR_PROVENANCE = "agent_supplied_not_independently_authenticated"
SCOPE_COMPLETENESS = (
    "caller_declared_complete_named_scope_not_independently_authenticated"
)
SEMANTIC_PROVENANCE = "caller_supplied_not_deterministically_verified"

PAIR_ORDER = (
    "abstract_results",
    "discussion_results",
    "methods_reported_analyses",
    "manuscript_preregistration",
)
PAIR_ROLES = {
    "abstract_results": ("abstract", "results"),
    "discussion_results": ("discussion", "results"),
    "methods_reported_analyses": ("methods", "reported_analyses"),
    "manuscript_preregistration": (
        "manuscript_report",
        "preregistration",
        "disclosure_scope",
    ),
}
FINDING_TYPES = {
    "abstract_results": frozenset(
        {
            "numeric_mismatch",
            "direction_mismatch",
            "significance_mismatch",
            "claim_strength_rung_mismatch",
        }
    ),
    "discussion_results": frozenset(
        {
            "direction_mismatch",
            "claim_strength_rung_mismatch",
            "scope_or_population_overreach",
        }
    ),
    "methods_reported_analyses": frozenset(
        {
            "declared_analysis_no_reported_counterpart",
            "reported_analysis_no_declared_counterpart",
            "analysis_specification_conflict",
        }
    ),
    "manuscript_preregistration": frozenset({"undisclosed_preregistration_deviation"}),
}
NEGATIVE_BASES = frozenset(
    {
        "legitimate_compression",
        "same_rung_rewording",
        "disclosed_deviation",
        "other_no_listed_observation",
    }
)
DEVIATION_DOMAINS = frozenset(
    {
        "hypothesis",
        "primary_outcome",
        "sample_size_or_stopping",
        "analysis_model",
        "transformation",
        "exclusion",
        "inference_criterion",
        "confirmatory_exploratory_designation",
    }
)
EVIDENCE_STATES = frozenset(
    {
        "agent_extracted",
        "checked_no_match",
        "not_checked",
        "source_missing",
        "access_failed",
        "retrieval_failed",
    }
)
FAILURE_STATES = frozenset(
    {"not_checked", "source_missing", "access_failed", "retrieval_failed"}
)
MANIFEST_STATES = frozenset(
    {"present", "source_missing", "access_failed", "retrieval_failed"}
)
SIDECAR_STATES = frozenset(
    {"provided", "not_provided", "access_failed", "retrieval_failed"}
)
NOT_CHECKED_REASONS = frozenset(
    {
        "PAIR_CHECK_NOT_PERFORMED",
        "COUNTERPART_DOCUMENT_MISSING",
        "COUNTERPART_SCOPE_NOT_PROVIDED",
        "SOURCE_ACCESS_FAILED",
        "SOURCE_RETRIEVAL_FAILED",
    }
)
OUTCOMES = frozenset(
    {"POTENTIAL_INCONSISTENCY_LOCATED", "NO_LISTED_INCONSISTENCY_LOCATED"}
)
DIAGNOSTIC_CODES = frozenset(
    {
        "NAMED_INPUT_UNREADABLE",
        "DRAFT_CONTRACT_INVALID",
        "SOURCE_MANIFEST_INVALID",
        "SOURCE_BINDING_INVALID",
        "EVIDENCE_REPLAY_INVALID",
        "FINAL_ARTIFACT_INVALID",
        "RESOURCE_LIMIT",
    }
)
BOUNDARY = {
    "semantic_observation_not_recomputed": True,
    "stage_4_5_verdict_unchanged": True,
    "stage_5_routing_unchanged": True,
    "integrity_issue_counts_unchanged": True,
    "formatter_gate_unchanged": True,
    "terminal_policy_unchanged": True,
    "score_not_produced": True,
    "automatic_rewrite_not_performed": True,
    "agreement_not_certified": True,
}

_RFC3339_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt]"
    r"(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
    r"(?:\.[0-9]+)?(?:[Zz]|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])$"
)
_HEX = frozenset("0123456789abcdefABCDEF")


class AdvisoryError(ValueError):
    """A closed #672 contract or replay invariant failed."""

    def __init__(self, code: str, message: str) -> None:
        if code not in DIAGNOSTIC_CODES:
            raise ValueError(f"unknown diagnostic code: {code}")
        super().__init__(message)
        self.code = code


class _ClosedArgumentParser(argparse.ArgumentParser):
    """Convert malformed CLI syntax into the same bounded diagnostic channel."""

    def error(self, message: str) -> NoReturn:
        del message
        raise AdvisoryError(
            "FINAL_ARTIFACT_INVALID",
            "command line: arguments do not match the closed CLI",
        )


def _fail(code: str, path: str, message: str) -> NoReturn:
    raise AdvisoryError(code, f"{path}: {message}")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8", errors="strict")
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        _fail("FINAL_ARTIFACT_INVALID", "value", f"cannot serialize canonically: {exc}")


def _digest_without(value: Mapping[str, Any], field: str) -> str:
    payload = {key: copy.deepcopy(item) for key, item in value.items() if key != field}
    return _sha256(_canonical_bytes(payload))


def _closed(
    value: Any,
    path: str,
    fields: set[str] | frozenset[str],
    *,
    code: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(code, path, "must be an object")
    missing = fields - set(value)
    extra = set(value) - fields
    if missing:
        _fail(code, path, f"missing field(s): {', '.join(sorted(missing))}")
    if extra:
        _fail(code, path, f"undeclared field(s): {', '.join(sorted(extra))}")
    return value


def _array(
    value: Any,
    path: str,
    *,
    code: str,
    minimum: int = 0,
    maximum: int = MAX_OBSERVATIONS,
) -> list[Any]:
    if not isinstance(value, list):
        _fail(code, path, "must be an array")
    if len(value) < minimum or len(value) > maximum:
        _fail(code, path, f"must contain {minimum}..{maximum} items")
    return value


def _safe_text(
    value: Any,
    path: str,
    *,
    code: str,
    minimum: int = 1,
    maximum: int = 1000,
) -> str:
    if not isinstance(value, str):
        _fail(code, path, "must be a string")
    if len(value) < minimum or len(value) > maximum:
        _fail(code, path, f"must contain {minimum}..{maximum} code points")
    for character in value:
        number = ord(character)
        category = unicodedata.category(character)
        if (
            number == 127
            or (number < 32 and character not in {"\t", "\n", "\r"})
            or 0xD800 <= number <= 0xDFFF
            or category in {"Cf", "Zl", "Zp"}
        ):
            _fail(code, path, f"contains forbidden character U+{number:04X}")
    return value


def _identifier(value: Any, path: str, *, code: str) -> str:
    text = _safe_text(value, path, code=code, maximum=MAX_IDENTIFIER)
    if re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,199}", text) is None:
        _fail(code, path, "must be a lowercase ASCII identifier")
    return text


def _sha(value: Any, path: str, *, code: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        _fail(code, path, "must be a lowercase SHA-256 hex digest")
    return value


def _integer(
    value: Any,
    path: str,
    *,
    code: str,
    minimum: int = 0,
    maximum: int,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        _fail(code, path, "must be an integer")
    if value < minimum or value > maximum:
        _fail(code, path, f"must be within {minimum}..{maximum}")
    return value


def _enum(value: Any, path: str, choices: frozenset[str], *, code: str) -> str:
    if not isinstance(value, str) or value not in choices:
        _fail(code, path, f"must be one of {sorted(choices)}")
    return value


def _timestamp(value: Any, path: str, *, code: str) -> str:
    text = _safe_text(value, path, code=code, maximum=100)
    if _RFC3339_RE.fullmatch(text) is None:
        _fail(code, path, "must be an RFC 3339 timestamp with an offset")
    normalized = text[:-1] + "+00:00" if text[-1] in {"Z", "z"} else text
    try:
        dt.datetime.fromisoformat(normalized)
    except ValueError as exc:
        _fail(code, path, f"is not a real RFC 3339 timestamp: {exc}")
    return text


def _relative_path(value: Any, path: str, *, code: str) -> str:
    text = _safe_text(value, path, code=code, maximum=MAX_PATH_CODEPOINTS)
    if (
        text.startswith("/")
        or "\\" in text
        or any(
            unicodedata.category(character) in {"Cc", "Cf", "Zl", "Zp"}
            for character in text
        )
    ):
        _fail(code, path, "must be a normalized relative POSIX path")
    components = text.split("/")
    if any(component in {"", ".", ".."} for component in components):
        _fail(code, path, "contains an empty, dot, or parent component")
    return text


def _span(value: Any, path: str, *, code: str) -> dict[str, int]:
    block = _closed(value, path, {"start", "end"}, code=code)
    start = _integer(
        block["start"], f"{path}.start", code=code, maximum=MAX_TOTAL_SOURCE_BYTES
    )
    end = _integer(
        block["end"],
        f"{path}.end",
        code=code,
        minimum=1,
        maximum=MAX_TOTAL_SOURCE_BYTES,
    )
    if end <= start:
        _fail(code, path, "must be a non-empty half-open UTF-8 span")
    return {"start": start, "end": end}


def strict_percent_decode(value: str) -> str:
    """Decode RFC 3986 percent escapes once; a plus remains a literal plus."""

    _safe_text(
        value,
        "anchor_value_encoded",
        code="EVIDENCE_REPLAY_INVALID",
        maximum=MAX_ENCODED_ANCHOR,
    )
    index = 0
    while index < len(value):
        if value[index] == "%":
            if (
                index + 2 >= len(value)
                or value[index + 1] not in _HEX
                or value[index + 2] not in _HEX
            ):
                _fail(
                    "EVIDENCE_REPLAY_INVALID",
                    "anchor_value_encoded",
                    f"malformed percent escape at character {index}",
                )
            index += 3
        else:
            index += 1
    try:
        return unquote(value, encoding="utf-8", errors="strict")
    except UnicodeError as exc:
        _fail(
            "EVIDENCE_REPLAY_INVALID",
            "anchor_value_encoded",
            f"percent escapes are not strict UTF-8: {exc}",
        )


def _precheck_depth(text: str, *, code: str, path: str) -> None:
    depth = 0
    in_string = False
    escaped = False
    for character in text:
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue
        if character == '"':
            in_string = True
        elif character in "[{":
            depth += 1
            if depth > MAX_JSON_DEPTH:
                _fail(code, path, f"JSON nesting exceeds {MAX_JSON_DEPTH}")
        elif character in "]}":
            depth -= 1


def _count_nodes(value: Any, *, code: str, path: str) -> None:
    count = 0
    stack = [value]
    while stack:
        current = stack.pop()
        count += 1
        if count > MAX_JSON_NODES:
            _fail(code, path, f"JSON aggregate nodes exceed {MAX_JSON_NODES}")
        if isinstance(current, dict):
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)


def _reject_unsafe_json_strings(value: Any, *, code: str, path: str) -> None:
    stack: list[tuple[str, Any]] = [(path, value)]
    while stack:
        current_path, current = stack.pop()
        if isinstance(current, dict):
            for key, item in current.items():
                _safe_text(
                    key, f"{current_path} key", code=code, minimum=0, maximum=1024
                )
                stack.append((f"{current_path}.{key}", item))
        elif isinstance(current, list):
            for index, item in enumerate(current):
                stack.append((f"{current_path}[{index}]", item))
        elif isinstance(current, str):
            _safe_text(
                current,
                current_path,
                code=code,
                minimum=0,
                maximum=max(len(current), 1),
            )


def _read_named_bytes(
    path: Path,
    maximum: int,
    *,
    label: str,
    unreadable_code: str = "NAMED_INPUT_UNREADABLE",
) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    # A read-only open of a FIFO can otherwise wait forever before fstat has a
    # chance to reject it.  O_NONBLOCK is inert for ordinary regular files.
    if hasattr(os, "O_NONBLOCK"):
        flags |= os.O_NONBLOCK
    try:
        descriptor = os.open(path, flags)
        try:
            metadata = os.fstat(descriptor)
            if not stat.S_ISREG(metadata.st_mode):
                _fail(unreadable_code, label, "must be a regular file")
            chunks: list[bytes] = []
            remaining = maximum + 1
            while remaining:
                chunk = os.read(descriptor, min(1024 * 1024, remaining))
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            payload = b"".join(chunks)
        finally:
            os.close(descriptor)
    except AdvisoryError:
        raise
    except (OSError, ValueError) as exc:
        _fail(
            unreadable_code,
            label,
            f"could not be read: {exc.__class__.__name__}",
        )
    if len(payload) > maximum:
        _fail("RESOURCE_LIMIT", label, f"exceeds {maximum} bytes")
    return payload


def _strict_json_bytes(
    raw: bytes,
    *,
    code: str,
    path: str,
) -> Any:
    if raw.startswith(b"\xef\xbb\xbf"):
        _fail(code, path, "must not contain a UTF-8 BOM")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeError as exc:
        _fail(code, path, f"is not strict UTF-8: {exc}")
    _precheck_depth(text, code=code, path=path)

    def object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in pairs:
            if key in result:
                _fail(code, path, f"contains duplicate decoded key {key!r}")
            result[key] = item
        return result

    def reject_constant(value: str) -> NoReturn:
        _fail(code, path, f"contains non-finite number {value}")

    def reject_float(value: str) -> NoReturn:
        _fail(code, path, f"contains unsupported non-integer number {value}")

    try:
        value = json.loads(
            text,
            object_pairs_hook=object_pairs,
            parse_constant=reject_constant,
            parse_float=reject_float,
        )
    except AdvisoryError:
        raise
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        _fail(code, path, f"is not strict JSON: {exc}")
    _count_nodes(value, code=code, path=path)
    _reject_unsafe_json_strings(value, code=code, path=path)
    return value


def _load_json(
    path: Path,
    maximum: int,
    *,
    code: str,
    label: str,
) -> tuple[Any, bytes]:
    raw = _read_named_bytes(path, maximum, label=label)
    return _strict_json_bytes(raw, code=code, path=label), raw


def _binding_bytes(
    value: Any,
    raw: bytes | None,
    maximum: int,
    *,
    code: str,
    path: str,
) -> bytes:
    """Bind a parsed carrier to the exact raw bytes named by its caller."""

    if raw is None:
        candidate = _canonical_bytes(value)
    elif isinstance(raw, bytes):
        candidate = raw
    else:
        _fail(code, path, "raw binding must be bytes")
    if len(candidate) > maximum:
        _fail("RESOURCE_LIMIT", path, f"exceeds {maximum} bytes")
    parsed = _strict_json_bytes(candidate, code=code, path=path)
    if _canonical_bytes(parsed) != _canonical_bytes(value):
        _fail(code, path, "raw bytes decode to a different object")
    return candidate


def _strict_source(raw: bytes, *, label: str, maximum: int) -> str:
    if not isinstance(raw, bytes):
        _fail("SOURCE_BINDING_INVALID", label, "must be bytes")
    if len(raw) > maximum:
        _fail("RESOURCE_LIMIT", label, f"exceeds {maximum} bytes")
    if raw.startswith(b"\xef\xbb\xbf"):
        _fail("SOURCE_BINDING_INVALID", label, "must not contain a UTF-8 BOM")
    try:
        text = raw.decode("utf-8", errors="strict")
        if text.encode("utf-8", errors="strict") != raw:
            _fail(
                "SOURCE_BINDING_INVALID", label, "does not round-trip as strict UTF-8"
            )
    except UnicodeError as exc:
        _fail("SOURCE_BINDING_INVALID", label, f"is not strict UTF-8: {exc}")
    return text


def _strict_accepted_draft(raw: bytes) -> str:
    text = _strict_source(
        raw,
        label="accepted draft",
        maximum=MAX_ACCEPTED_DRAFT_BYTES,
    )
    if not text.strip():
        _fail("SOURCE_BINDING_INVALID", "accepted draft", "must not be blank")
    return text


def _atomic_write(path: Path, payload: bytes) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
        )
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        except BaseException:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
            raise
    except AdvisoryError:
        raise
    except OSError as exc:
        _fail(
            "NAMED_INPUT_UNREADABLE",
            "output",
            f"atomic write failed: {exc.__class__.__name__}",
        )


def _reject_output_alias(output: Path, inputs: Sequence[Path | None]) -> None:
    output_absolute = os.path.abspath(output)
    for candidate in inputs:
        if candidate is None:
            continue
        if output_absolute == os.path.abspath(candidate):
            _fail("NAMED_INPUT_UNREADABLE", "output", "must not alias a named input")
        try:
            if (
                output.exists()
                and candidate.exists()
                and os.path.samefile(output, candidate)
            ):
                _fail(
                    "NAMED_INPUT_UNREADABLE", "output", "must not alias a named input"
                )
        except OSError:
            continue


def build_preregistration_artifact(
    *,
    status: str,
    artifact_id: str,
    declared_at: str,
    companion_bytes: bytes | None = None,
    relative_path: str | None = None,
    artifact_provenance: str | None = None,
) -> dict[str, Any]:
    """Derive one canonical, hash-bound preregistration handoff sidecar."""

    state = _enum(status, "status", SIDECAR_STATES, code="SOURCE_BINDING_INVALID")
    identity = _identifier(artifact_id, "artifact_id", code="SOURCE_BINDING_INVALID")
    timestamp = _timestamp(declared_at, "declared_at", code="SOURCE_BINDING_INVALID")
    if state == "provided":
        if companion_bytes is None:
            _fail(
                "SOURCE_BINDING_INVALID", "companion", "is required for provided status"
            )
        text = _strict_source(
            companion_bytes,
            label="preregistration companion",
            maximum=MAX_PREREGISTRATION_BYTES,
        )
        if not text.strip():
            _fail("SOURCE_BINDING_INVALID", "companion", "must not be blank")
        digest = _sha256(companion_bytes)
        if digest == TEMPLATE_SHA256:
            _fail(
                "SOURCE_BINDING_INVALID",
                "companion",
                "blank guidance template is not evidence",
            )
        if relative_path is None:
            _fail(
                "SOURCE_BINDING_INVALID",
                "relative_path",
                "is required for provided status",
            )
        normalized_path = _relative_path(
            relative_path,
            "relative_path",
            code="SOURCE_BINDING_INVALID",
        )
        provenance = artifact_provenance or "author_provided_completed_preregistration"
        if not isinstance(provenance, str) or provenance not in {
            "author_provided_completed_preregistration",
            "synthetic_fixture",
        }:
            _fail(
                "SOURCE_BINDING_INVALID",
                "artifact_provenance",
                "is invalid for provided status",
            )
        size = len(companion_bytes)
        record: dict[str, Any] = {
            "schema_version": SIDECAR_SCHEMA_VERSION,
            "status": state,
            "artifact_id": identity,
            "relative_path": normalized_path,
            "artifact_provenance": provenance,
            "source_artifact_sha256": digest,
            "source_artifact_size_bytes": size,
            "source_content_sha256": digest,
            "source_content_utf8_bytes": size,
            "declared_at": timestamp,
            "record_digest": "",
        }
    else:
        if companion_bytes is not None or relative_path is not None:
            _fail(
                "SOURCE_BINDING_INVALID",
                "sidecar",
                "unavailable status forbids companion/path",
            )
        if artifact_provenance is not None and artifact_provenance != "not_provided":
            _fail(
                "SOURCE_BINDING_INVALID", "artifact_provenance", "must be not_provided"
            )
        record = {
            "schema_version": SIDECAR_SCHEMA_VERSION,
            "status": state,
            "artifact_id": identity,
            "relative_path": None,
            "artifact_provenance": "not_provided",
            "source_artifact_sha256": None,
            "source_artifact_size_bytes": None,
            "source_content_sha256": None,
            "source_content_utf8_bytes": None,
            "declared_at": timestamp,
            "record_digest": "",
        }
    record["record_digest"] = _digest_without(record, "record_digest")
    if len(_canonical_bytes(record)) > MAX_SIDECAR_BYTES:
        _fail("RESOURCE_LIMIT", "sidecar", "canonical output exceeds 1 MiB")
    return record


def validate_preregistration_artifact(
    value: Any,
    *,
    companion_bytes: bytes | None,
) -> dict[str, Any]:
    fields = {
        "schema_version",
        "status",
        "artifact_id",
        "relative_path",
        "artifact_provenance",
        "source_artifact_sha256",
        "source_artifact_size_bytes",
        "source_content_sha256",
        "source_content_utf8_bytes",
        "declared_at",
        "record_digest",
    }
    record = _closed(value, "sidecar", fields, code="SOURCE_BINDING_INVALID")
    if record["schema_version"] != SIDECAR_SCHEMA_VERSION:
        _fail(
            "SOURCE_BINDING_INVALID", "sidecar.schema_version", "has the wrong version"
        )
    _sha(
        record["record_digest"], "sidecar.record_digest", code="SOURCE_BINDING_INVALID"
    )
    expected = build_preregistration_artifact(
        status=record["status"],
        artifact_id=record["artifact_id"],
        declared_at=record["declared_at"],
        companion_bytes=companion_bytes,
        relative_path=record["relative_path"],
        artifact_provenance=record["artifact_provenance"],
    )
    if _canonical_bytes(record) != _canonical_bytes(expected):
        _fail(
            "SOURCE_BINDING_INVALID", "sidecar", "does not match deterministic replay"
        )
    return copy.deepcopy(record)


def _manifest_artifact(value: Any, path: str) -> dict[str, Any]:
    fields = {
        "artifact_id",
        "document_kind",
        "relative_path",
        "artifact_state",
        "artifact_provenance",
        "source_artifact_sha256",
        "source_artifact_size_bytes",
        "source_content_sha256",
        "source_content_utf8_bytes",
    }
    artifact = _closed(value, path, fields, code="SOURCE_MANIFEST_INVALID")
    _identifier(
        artifact["artifact_id"], f"{path}.artifact_id", code="SOURCE_MANIFEST_INVALID"
    )
    if not isinstance(artifact["document_kind"], str) or artifact[
        "document_kind"
    ] not in {
        "manuscript",
        "preregistration",
    }:
        _fail("SOURCE_MANIFEST_INVALID", f"{path}.document_kind", "is invalid")
    state = _enum(
        artifact["artifact_state"],
        f"{path}.artifact_state",
        MANIFEST_STATES,
        code="SOURCE_MANIFEST_INVALID",
    )
    if state == "present":
        _relative_path(
            artifact["relative_path"],
            f"{path}.relative_path",
            code="SOURCE_MANIFEST_INVALID",
        )
        raw_sha = _sha(
            artifact["source_artifact_sha256"],
            f"{path}.source_artifact_sha256",
            code="SOURCE_MANIFEST_INVALID",
        )
        content_sha = _sha(
            artifact["source_content_sha256"],
            f"{path}.source_content_sha256",
            code="SOURCE_MANIFEST_INVALID",
        )
        maximum_size = (
            MAX_ACCEPTED_DRAFT_BYTES
            if artifact["document_kind"] == "manuscript"
            else MAX_PREREGISTRATION_BYTES
        )
        raw_size = _integer(
            artifact["source_artifact_size_bytes"],
            f"{path}.source_artifact_size_bytes",
            code="SOURCE_MANIFEST_INVALID",
            minimum=1,
            maximum=maximum_size,
        )
        content_size = _integer(
            artifact["source_content_utf8_bytes"],
            f"{path}.source_content_utf8_bytes",
            code="SOURCE_MANIFEST_INVALID",
            minimum=1,
            maximum=maximum_size,
        )
        if raw_sha != content_sha or raw_size != content_size:
            _fail(
                "SOURCE_MANIFEST_INVALID", path, "UTF-8 V1 raw/content bindings differ"
            )
        allowed_provenance = (
            {"author_provided_manuscript", "synthetic_fixture"}
            if artifact["document_kind"] == "manuscript"
            else {"author_provided_completed_preregistration", "synthetic_fixture"}
        )
        if (
            not isinstance(artifact["artifact_provenance"], str)
            or artifact["artifact_provenance"] not in allowed_provenance
        ):
            _fail(
                "SOURCE_MANIFEST_INVALID", f"{path}.artifact_provenance", "is invalid"
            )
    else:
        if artifact["document_kind"] != "preregistration":
            _fail(
                "SOURCE_MANIFEST_INVALID", path, "accepted manuscript must be present"
            )
        if artifact["relative_path"] is not None:
            _fail("SOURCE_MANIFEST_INVALID", f"{path}.relative_path", "must be null")
        for field in (
            "source_artifact_sha256",
            "source_artifact_size_bytes",
            "source_content_sha256",
            "source_content_utf8_bytes",
        ):
            if artifact[field] is not None:
                _fail("SOURCE_MANIFEST_INVALID", f"{path}.{field}", "must be null")
        if artifact["artifact_provenance"] != "not_provided":
            _fail(
                "SOURCE_MANIFEST_INVALID",
                f"{path}.artifact_provenance",
                "must be not_provided",
            )
    return artifact


def _project_sidecar(record: Mapping[str, Any]) -> dict[str, Any]:
    state = {
        "provided": "present",
        "not_provided": "source_missing",
        "access_failed": "access_failed",
        "retrieval_failed": "retrieval_failed",
    }[record["status"]]
    return {
        "artifact_id": record["artifact_id"],
        "document_kind": "preregistration",
        "relative_path": record["relative_path"],
        "artifact_state": state,
        "artifact_provenance": record["artifact_provenance"],
        "source_artifact_sha256": record["source_artifact_sha256"],
        "source_artifact_size_bytes": record["source_artifact_size_bytes"],
        "source_content_sha256": record["source_content_sha256"],
        "source_content_utf8_bytes": record["source_content_utf8_bytes"],
    }


def validate_source_manifest(
    value: Any,
    *,
    sidecar: Mapping[str, Any],
    accepted_draft_bytes: bytes,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    fields = {
        "schema_version",
        "manifest_id",
        "accepted_draft_artifact_id",
        "accepted_draft_sha256",
        "artifacts",
        "manifest_digest",
    }
    manifest = _closed(value, "manifest", fields, code="SOURCE_MANIFEST_INVALID")
    if manifest["schema_version"] != MANIFEST_SCHEMA_VERSION:
        _fail(
            "SOURCE_MANIFEST_INVALID",
            "manifest.schema_version",
            "has the wrong version",
        )
    _identifier(
        manifest["manifest_id"], "manifest.manifest_id", code="SOURCE_MANIFEST_INVALID"
    )
    accepted_id = _identifier(
        manifest["accepted_draft_artifact_id"],
        "manifest.accepted_draft_artifact_id",
        code="SOURCE_MANIFEST_INVALID",
    )
    accepted_sha = _sha(
        manifest["accepted_draft_sha256"],
        "manifest.accepted_draft_sha256",
        code="SOURCE_MANIFEST_INVALID",
    )
    _sha(
        manifest["manifest_digest"],
        "manifest.manifest_digest",
        code="SOURCE_MANIFEST_INVALID",
    )
    artifacts = _array(
        manifest["artifacts"],
        "manifest.artifacts",
        code="SOURCE_MANIFEST_INVALID",
        minimum=2,
        maximum=2,
    )
    parsed = [
        _manifest_artifact(item, f"manifest.artifacts[{index}]")
        for index, item in enumerate(artifacts)
    ]
    ids = [item["artifact_id"] for item in parsed]
    if ids != sorted(ids) or len(set(ids)) != 2:
        _fail(
            "SOURCE_MANIFEST_INVALID",
            "manifest.artifacts",
            "must have unique ASCII-sorted IDs",
        )
    by_id = {item["artifact_id"]: item for item in parsed}
    if accepted_id not in by_id:
        _fail(
            "SOURCE_MANIFEST_INVALID",
            "manifest.accepted_draft_artifact_id",
            "does not resolve",
        )
    accepted = by_id[accepted_id]
    if (
        accepted["document_kind"] != "manuscript"
        or accepted["artifact_state"] != "present"
    ):
        _fail(
            "SOURCE_MANIFEST_INVALID",
            "manifest",
            "designated accepted draft is not present manuscript",
        )
    if sidecar["artifact_id"] == accepted_id:
        _fail(
            "SOURCE_MANIFEST_INVALID",
            "manifest",
            "preregistration/manuscript IDs must differ",
        )
    if set(by_id) != {accepted_id, sidecar["artifact_id"]}:
        _fail(
            "SOURCE_MANIFEST_INVALID",
            "manifest.artifacts",
            "must contain exactly accepted draft and sidecar projection",
        )
    if by_id[sidecar["artifact_id"]] != _project_sidecar(sidecar):
        _fail(
            "SOURCE_MANIFEST_INVALID",
            "manifest",
            "preregistration projection differs from sidecar",
        )
    actual_sha = _sha256(accepted_draft_bytes)
    actual_size = len(accepted_draft_bytes)
    if accepted_sha != actual_sha:
        _fail(
            "SOURCE_BINDING_INVALID",
            "accepted draft",
            "manifest SHA does not match named bytes",
        )
    for field in ("source_artifact_sha256", "source_content_sha256"):
        if accepted[field] != actual_sha:
            _fail(
                "SOURCE_BINDING_INVALID",
                f"accepted draft {field}",
                "does not match named bytes",
            )
    for field in ("source_artifact_size_bytes", "source_content_utf8_bytes"):
        if accepted[field] != actual_size:
            _fail(
                "SOURCE_BINDING_INVALID",
                f"accepted draft {field}",
                "does not match named bytes",
            )
    if _digest_without(manifest, "manifest_digest") != manifest["manifest_digest"]:
        _fail("SOURCE_MANIFEST_INVALID", "manifest.manifest_digest", "does not replay")
    return copy.deepcopy(manifest), copy.deepcopy(by_id)


def _locator(value: Any, path: str) -> dict[str, str]:
    locator = _closed(
        value,
        path,
        {"kind", "value", "provenance"},
        code="DRAFT_CONTRACT_INVALID",
    )
    if not isinstance(locator["kind"], str) or locator["kind"] not in {
        "document",
        "page",
        "section",
        "paragraph",
        "other",
    }:
        _fail("DRAFT_CONTRACT_INVALID", f"{path}.kind", "is invalid")
    _safe_text(
        locator["value"],
        f"{path}.value",
        code="DRAFT_CONTRACT_INVALID",
        maximum=500,
    )
    if any(
        unicodedata.category(character) in {"Cc", "Cf", "Zl", "Zp"}
        for character in locator["value"]
    ):
        _fail(
            "DRAFT_CONTRACT_INVALID",
            f"{path}.value",
            "must be a control-free single line",
        )
    if locator["provenance"] != LOCATOR_PROVENANCE:
        _fail("DRAFT_CONTRACT_INVALID", f"{path}.provenance", "is invalid")
    return copy.deepcopy(locator)


def _rights_pair(sharing_scope: Any, rights_basis: Any, path: str) -> tuple[str, str]:
    if not isinstance(sharing_scope, str) or not isinstance(rights_basis, str):
        _fail(
            "DRAFT_CONTRACT_INVALID",
            path,
            "sharing_scope/rights_basis must both be strings",
        )
    pair = (sharing_scope, rights_basis)
    allowed = {
        ("session_only", "not_assessed"),
        ("user_confirmed_shareable", "user_declared_authorized"),
    }
    if pair not in allowed:
        _fail(
            "DRAFT_CONTRACT_INVALID",
            path,
            "sharing_scope/rights_basis pairing is invalid",
        )
    return pair  # type: ignore[return-value]


def _draft_slot(
    value: Any,
    path: str,
    *,
    expected_role: str,
    accepted_id: str,
    preregistration_id: str,
) -> dict[str, Any]:
    fields = {
        "logical_role",
        "artifact_id",
        "document_locator",
        "evidence_state",
        "anchor_value_encoded",
        "quote_source_span_utf8",
        "checked_scope_input",
        "captured_at",
        "sharing_scope",
        "rights_basis",
    }
    slot = _closed(value, path, fields, code="DRAFT_CONTRACT_INVALID")
    if slot["logical_role"] != expected_role:
        _fail(
            "DRAFT_CONTRACT_INVALID",
            f"{path}.logical_role",
            f"must equal {expected_role}",
        )
    expected_id = (
        preregistration_id if expected_role == "preregistration" else accepted_id
    )
    artifact_id = _identifier(
        slot["artifact_id"], f"{path}.artifact_id", code="DRAFT_CONTRACT_INVALID"
    )
    if artifact_id != expected_id:
        _fail(
            "DRAFT_CONTRACT_INVALID",
            f"{path}.artifact_id",
            "does not bind the required artifact",
        )
    _locator(slot["document_locator"], f"{path}.document_locator")
    state = _enum(
        slot["evidence_state"],
        f"{path}.evidence_state",
        EVIDENCE_STATES,
        code="DRAFT_CONTRACT_INVALID",
    )
    encoded = slot["anchor_value_encoded"]
    span = slot["quote_source_span_utf8"]
    scope = slot["checked_scope_input"]
    captured = slot["captured_at"]
    if state == "agent_extracted":
        _safe_text(
            encoded,
            f"{path}.anchor_value_encoded",
            code="DRAFT_CONTRACT_INVALID",
            maximum=MAX_ENCODED_ANCHOR,
        )
        _span(span, f"{path}.quote_source_span_utf8", code="DRAFT_CONTRACT_INVALID")
        _timestamp(captured, f"{path}.captured_at", code="DRAFT_CONTRACT_INVALID")
        if scope is not None:
            _fail(
                "DRAFT_CONTRACT_INVALID", f"{path}.checked_scope_input", "must be null"
            )
    elif state == "checked_no_match":
        if encoded is not None or span is not None or captured is not None:
            _fail(
                "DRAFT_CONTRACT_INVALID",
                path,
                "checked_no_match carries no quote payload",
            )
        block = _closed(
            scope,
            f"{path}.checked_scope_input",
            {"source_span_utf8", "checked_at", "scope_completeness"},
            code="DRAFT_CONTRACT_INVALID",
        )
        _span(
            block["source_span_utf8"],
            f"{path}.checked_scope_input.source_span_utf8",
            code="DRAFT_CONTRACT_INVALID",
        )
        _timestamp(
            block["checked_at"],
            f"{path}.checked_scope_input.checked_at",
            code="DRAFT_CONTRACT_INVALID",
        )
        if block["scope_completeness"] != SCOPE_COMPLETENESS:
            _fail(
                "DRAFT_CONTRACT_INVALID",
                f"{path}.checked_scope_input.scope_completeness",
                "is invalid",
            )
    else:
        if (
            encoded is not None
            or span is not None
            or scope is not None
            or captured is not None
        ):
            _fail(
                "DRAFT_CONTRACT_INVALID",
                path,
                "failure state carries quote/scope payload",
            )
    sharing, rights = _rights_pair(slot["sharing_scope"], slot["rights_basis"], path)
    if state != "agent_extracted" and (sharing, rights) != (
        "session_only",
        "not_assessed",
    ):
        _fail(
            "DRAFT_CONTRACT_INVALID",
            path,
            "non-quote state must use session_only/not_assessed",
        )
    return copy.deepcopy(slot)


def _expected_not_checked_reason(pair_kind: str, slots: list[dict[str, Any]]) -> str:
    states = [slot["evidence_state"] for slot in slots]
    if "source_missing" in states:
        return "COUNTERPART_DOCUMENT_MISSING"
    if "access_failed" in states:
        return "SOURCE_ACCESS_FAILED"
    if "retrieval_failed" in states:
        return "SOURCE_RETRIEVAL_FAILED"
    if pair_kind == "methods_reported_analyses" and sorted(states) == [
        "agent_extracted",
        "not_checked",
    ]:
        return "COUNTERPART_SCOPE_NOT_PROVIDED"
    if pair_kind == "manuscript_preregistration" and states == [
        "agent_extracted",
        "agent_extracted",
        "not_checked",
    ]:
        return "COUNTERPART_SCOPE_NOT_PROVIDED"
    return "PAIR_CHECK_NOT_PERFORMED"


def _performed_combination(
    observation: Mapping[str, Any], states: tuple[str, ...], path: str
) -> None:
    pair = observation["pair_kind"]
    outcome = observation["outcome"]
    finding = observation["finding_type"]
    negative = observation["negative_basis"]
    expected: tuple[str, ...]
    if outcome == "POTENTIAL_INCONSISTENCY_LOCATED":
        if pair in {"abstract_results", "discussion_results"}:
            expected = ("agent_extracted", "agent_extracted")
        elif pair == "methods_reported_analyses":
            expected = {
                "declared_analysis_no_reported_counterpart": (
                    "agent_extracted",
                    "checked_no_match",
                ),
                "reported_analysis_no_declared_counterpart": (
                    "checked_no_match",
                    "agent_extracted",
                ),
                "analysis_specification_conflict": (
                    "agent_extracted",
                    "agent_extracted",
                ),
            }[finding]
        else:
            expected = (
                "agent_extracted",
                "agent_extracted",
                "checked_no_match",
            )
    elif negative == "disclosed_deviation":
        expected = ("agent_extracted", "agent_extracted", "agent_extracted")
    else:
        expected = ("agent_extracted", "agent_extracted")
    if states != expected:
        _fail(
            "DRAFT_CONTRACT_INVALID",
            f"{path}.evidence_slots",
            f"must use states {expected}",
        )


def _preflight_draft_role_matrix(
    observations: Sequence[Any],
    *,
    manifest: Mapping[str, Any],
    artifacts: Mapping[str, Mapping[str, Any]],
    sidecar: Mapping[str, Any],
    fields: set[str],
) -> None:
    """Validate every identity/role/source slot before reading any outcome."""

    keys: set[str] = set()
    pair_counts = {pair: 0 for pair in PAIR_ORDER}
    accepted_id = manifest["accepted_draft_artifact_id"]
    for index, item in enumerate(observations):
        path = f"draft.observations[{index}]"
        observation = _closed(item, path, fields, code="DRAFT_CONTRACT_INVALID")
        key = _identifier(
            observation["observation_key"],
            f"{path}.observation_key",
            code="DRAFT_CONTRACT_INVALID",
        )
        if key in keys:
            _fail(
                "DRAFT_CONTRACT_INVALID",
                f"{path}.observation_key",
                "duplicates an earlier key",
            )
        keys.add(key)
        pair = _enum(
            observation["pair_kind"],
            f"{path}.pair_kind",
            frozenset(PAIR_ORDER),
            code="DRAFT_CONTRACT_INVALID",
        )
        pair_counts[pair] += 1
        roles = PAIR_ROLES[pair]
        raw_slots = _array(
            observation["evidence_slots"],
            f"{path}.evidence_slots",
            code="DRAFT_CONTRACT_INVALID",
            minimum=len(roles),
            maximum=len(roles),
        )
        slots = [
            _draft_slot(
                slot,
                f"{path}.evidence_slots[{slot_index}]",
                expected_role=role,
                accepted_id=accepted_id,
                preregistration_id=sidecar["artifact_id"],
            )
            for slot_index, (slot, role) in enumerate(
                zip(raw_slots, roles, strict=True)
            )
        ]
        for slot_index, slot in enumerate(slots):
            artifact = artifacts[slot["artifact_id"]]
            state = slot["evidence_state"]
            if state in {"agent_extracted", "checked_no_match", "not_checked"}:
                if artifact["artifact_state"] != "present":
                    _fail(
                        "DRAFT_CONTRACT_INVALID",
                        f"{path}.evidence_slots[{slot_index}]",
                        "requires a present artifact",
                    )
            elif artifact["artifact_state"] != state:
                _fail(
                    "DRAFT_CONTRACT_INVALID",
                    f"{path}.evidence_slots[{slot_index}]",
                    "state differs from manifest",
                )
    if any(count == 0 for count in pair_counts.values()):
        _fail(
            "DRAFT_CONTRACT_INVALID",
            "draft.observations",
            "must contain all four pair kinds",
        )


def validate_draft(
    value: Any,
    *,
    manifest: Mapping[str, Any],
    artifacts: Mapping[str, Mapping[str, Any]],
    sidecar: Mapping[str, Any],
) -> list[dict[str, Any]]:
    root = _closed(
        value,
        "draft",
        {"schema_version", "layer", "recorded_at", "observations"},
        code="DRAFT_CONTRACT_INVALID",
    )
    if root["schema_version"] != DRAFT_SCHEMA_VERSION or root["layer"] != LAYER:
        _fail("DRAFT_CONTRACT_INVALID", "draft", "has wrong schema version or layer")
    _timestamp(root["recorded_at"], "draft.recorded_at", code="DRAFT_CONTRACT_INVALID")
    observations = _array(
        root["observations"],
        "draft.observations",
        code="DRAFT_CONTRACT_INVALID",
        minimum=4,
        maximum=MAX_OBSERVATIONS,
    )
    fields = {
        "observation_key",
        "pair_kind",
        "check_state",
        "outcome",
        "finding_type",
        "negative_basis",
        "not_checked_reason",
        "deviation_id",
        "deviation_domain",
        "evidence_slots",
    }
    _preflight_draft_role_matrix(
        observations,
        manifest=manifest,
        artifacts=artifacts,
        sidecar=sidecar,
        fields=fields,
    )
    result: list[dict[str, Any]] = []
    keys: set[str] = set()
    deviation_ids: set[str] = set()
    pair_counts = {pair: 0 for pair in PAIR_ORDER}
    accepted_id = manifest["accepted_draft_artifact_id"]
    for index, item in enumerate(observations):
        path = f"draft.observations[{index}]"
        observation = _closed(item, path, fields, code="DRAFT_CONTRACT_INVALID")
        key = _identifier(
            observation["observation_key"],
            f"{path}.observation_key",
            code="DRAFT_CONTRACT_INVALID",
        )
        if key in keys:
            _fail(
                "DRAFT_CONTRACT_INVALID",
                f"{path}.observation_key",
                "duplicates an earlier key",
            )
        keys.add(key)
        pair = _enum(
            observation["pair_kind"],
            f"{path}.pair_kind",
            frozenset(PAIR_ORDER),
            code="DRAFT_CONTRACT_INVALID",
        )
        pair_counts[pair] += 1
        roles = PAIR_ROLES[pair]
        raw_slots = _array(
            observation["evidence_slots"],
            f"{path}.evidence_slots",
            code="DRAFT_CONTRACT_INVALID",
            minimum=len(roles),
            maximum=len(roles),
        )
        slots = [
            _draft_slot(
                slot,
                f"{path}.evidence_slots[{slot_index}]",
                expected_role=role,
                accepted_id=accepted_id,
                preregistration_id=sidecar["artifact_id"],
            )
            for slot_index, (slot, role) in enumerate(
                zip(raw_slots, roles, strict=True)
            )
        ]
        for slot_index, slot in enumerate(slots):
            artifact = artifacts[slot["artifact_id"]]
            state = slot["evidence_state"]
            if state in {"agent_extracted", "checked_no_match", "not_checked"}:
                if artifact["artifact_state"] != "present":
                    _fail(
                        "DRAFT_CONTRACT_INVALID",
                        f"{path}.evidence_slots[{slot_index}]",
                        "requires a present artifact",
                    )
            elif artifact["artifact_state"] != state:
                _fail(
                    "DRAFT_CONTRACT_INVALID",
                    f"{path}.evidence_slots[{slot_index}]",
                    "state differs from manifest",
                )
        check_state = observation["check_state"]
        if not isinstance(check_state, str) or check_state not in {
            "performed",
            "not_checked",
        }:
            _fail("DRAFT_CONTRACT_INVALID", f"{path}.check_state", "is invalid")
        states = tuple(slot["evidence_state"] for slot in slots)
        if check_state == "performed":
            if (
                not isinstance(observation["outcome"], str)
                or observation["outcome"] not in OUTCOMES
            ):
                _fail("DRAFT_CONTRACT_INVALID", f"{path}.outcome", "is invalid")
            if observation["not_checked_reason"] is not None:
                _fail(
                    "DRAFT_CONTRACT_INVALID",
                    f"{path}.not_checked_reason",
                    "must be null",
                )
            if observation["outcome"] == "POTENTIAL_INCONSISTENCY_LOCATED":
                if (
                    not isinstance(observation["finding_type"], str)
                    or observation["finding_type"] not in FINDING_TYPES[pair]
                    or observation["negative_basis"] is not None
                ):
                    _fail(
                        "DRAFT_CONTRACT_INVALID",
                        path,
                        "positive outcome fields are invalid",
                    )
            else:
                if (
                    observation["finding_type"] is not None
                    or not isinstance(observation["negative_basis"], str)
                    or observation["negative_basis"] not in NEGATIVE_BASES
                ):
                    _fail(
                        "DRAFT_CONTRACT_INVALID",
                        path,
                        "no-listed outcome fields are invalid",
                    )
                negative = observation["negative_basis"]
                allowed = (
                    (
                        negative == "legitimate_compression"
                        and pair == "abstract_results"
                    )
                    or (
                        negative == "same_rung_rewording"
                        and pair in {"abstract_results", "discussion_results"}
                    )
                    or (
                        negative == "disclosed_deviation"
                        and pair == "manuscript_preregistration"
                    )
                    or (
                        negative == "other_no_listed_observation"
                        and pair != "manuscript_preregistration"
                    )
                )
                if not allowed:
                    _fail(
                        "DRAFT_CONTRACT_INVALID",
                        f"{path}.negative_basis",
                        "is invalid for pair",
                    )
            _performed_combination(observation, states, path)
        else:
            if any(
                observation[field] is not None
                for field in ("outcome", "finding_type", "negative_basis")
            ):
                _fail(
                    "DRAFT_CONTRACT_INVALID",
                    path,
                    "not_checked carries no semantic outcome",
                )
            reason = _enum(
                observation["not_checked_reason"],
                f"{path}.not_checked_reason",
                NOT_CHECKED_REASONS,
                code="DRAFT_CONTRACT_INVALID",
            )
            if not any(state in FAILURE_STATES for state in states):
                _fail(
                    "DRAFT_CONTRACT_INVALID",
                    path,
                    "not_checked requires a failure slot",
                )
            if reason != _expected_not_checked_reason(pair, slots):
                _fail(
                    "DRAFT_CONTRACT_INVALID",
                    f"{path}.not_checked_reason",
                    "contradicts slot-state precedence",
                )
        if pair == "manuscript_preregistration" and check_state == "performed":
            deviation_id = _identifier(
                observation["deviation_id"],
                f"{path}.deviation_id",
                code="DRAFT_CONTRACT_INVALID",
            )
            if deviation_id in deviation_ids:
                _fail(
                    "DRAFT_CONTRACT_INVALID",
                    f"{path}.deviation_id",
                    "must be globally unique",
                )
            deviation_ids.add(deviation_id)
            _enum(
                observation["deviation_domain"],
                f"{path}.deviation_domain",
                DEVIATION_DOMAINS,
                code="DRAFT_CONTRACT_INVALID",
            )
        elif (
            observation["deviation_id"] is not None
            or observation["deviation_domain"] is not None
        ):
            _fail("DRAFT_CONTRACT_INVALID", path, "deviation fields must be null")
        normalized = copy.deepcopy(observation)
        normalized["evidence_slots"] = slots
        result.append(normalized)
    if any(count == 0 for count in pair_counts.values()):
        _fail(
            "DRAFT_CONTRACT_INVALID",
            "draft.observations",
            "must contain all four pair kinds",
        )
    return result


def _source_block(artifact: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": artifact["artifact_id"],
        "document_kind": artifact["document_kind"],
        "relative_path": artifact["relative_path"],
        "source_artifact_sha256": artifact["source_artifact_sha256"],
        "source_artifact_size_bytes": artifact["source_artifact_size_bytes"],
        "source_content_sha256": artifact["source_content_sha256"],
        "source_content_utf8_bytes": artifact["source_content_utf8_bytes"],
    }


def _slice_utf8(raw: bytes, span: Mapping[str, int], path: str) -> tuple[bytes, str]:
    start = span["start"]
    end = span["end"]
    if end > len(raw):
        _fail("EVIDENCE_REPLAY_INVALID", path, "extends beyond bound source bytes")
    payload = raw[start:end]
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeError as exc:
        _fail("EVIDENCE_REPLAY_INVALID", path, f"splits a UTF-8 sequence: {exc}")
    return payload, text


def _derive_slot(
    slot: Mapping[str, Any],
    *,
    artifact: Mapping[str, Any],
    source_bytes: bytes | None,
    path: str,
) -> dict[str, Any]:
    state = slot["evidence_state"]
    anchor: dict[str, Any]
    excerpt: dict[str, Any]
    checked_scope: dict[str, Any] | None = None
    if state == "agent_extracted":
        if source_bytes is None:
            _fail("EVIDENCE_REPLAY_INVALID", path, "quote source is unavailable")
        span = _span(
            slot["quote_source_span_utf8"],
            f"{path}.quote_source_span_utf8",
            code="EVIDENCE_REPLAY_INVALID",
        )
        payload, replayed = _slice_utf8(
            source_bytes, span, f"{path}.quote_source_span_utf8"
        )
        decoded = strict_percent_decode(slot["anchor_value_encoded"])
        _safe_text(
            decoded,
            f"{path}.anchor_value_encoded decoded",
            code="EVIDENCE_REPLAY_INVALID",
            maximum=MAX_EXTERNAL_CODEPOINTS,
        )
        word_count = len(decoded.split())
        if word_count > MAX_EXTERNAL_WORDS:
            _fail(
                "EVIDENCE_REPLAY_INVALID",
                f"{path}.anchor_value_encoded",
                f"exceeds {MAX_EXTERNAL_WORDS} words by whitespace split",
            )
        if decoded != replayed:
            _fail(
                "EVIDENCE_REPLAY_INVALID",
                path,
                "decoded quote does not equal exact source span",
            )
        anchor = {
            "kind": "quote",
            "value_encoded": slot["anchor_value_encoded"],
            "value_decoded": decoded,
        }
        excerpt = {
            "text": decoded,
            "excerpt_sha256": _sha256(payload),
            "source_span_utf8": span,
            "captured_at": slot["captured_at"],
        }
    else:
        anchor = {"kind": "none", "value_encoded": "", "value_decoded": ""}
        excerpt = {
            "text": None,
            "excerpt_sha256": None,
            "source_span_utf8": None,
            "captured_at": None,
        }
        if state == "checked_no_match":
            if source_bytes is None:
                _fail(
                    "EVIDENCE_REPLAY_INVALID",
                    path,
                    "checked scope source is unavailable",
                )
            block = slot["checked_scope_input"]
            span = _span(
                block["source_span_utf8"],
                f"{path}.checked_scope_input.source_span_utf8",
                code="EVIDENCE_REPLAY_INVALID",
            )
            payload, scope_text = _slice_utf8(
                source_bytes,
                span,
                f"{path}.checked_scope_input.source_span_utf8",
            )
            if not scope_text.strip():
                _fail(
                    "EVIDENCE_REPLAY_INVALID", path, "checked scope must not be blank"
                )
            checked_scope = {
                "source_span_utf8": span,
                "scope_sha256": _sha256(payload),
                "scope_utf8_bytes": len(payload),
                "checked_at": block["checked_at"],
                "completeness_provenance": block["scope_completeness"],
            }
    sharing_scope, rights_basis = _rights_pair(
        slot["sharing_scope"],
        slot["rights_basis"],
        path,
    )
    return {
        "logical_role": slot["logical_role"],
        "source": _source_block(artifact),
        "document_locator": copy.deepcopy(slot["document_locator"]),
        "evidence_state": state,
        "anchor": anchor,
        "excerpt": excerpt,
        "checked_scope": checked_scope,
        "cache": {"status": "not_used", "key_sha256": None},
        "content_handling": {
            "contains_external_text": state == "agent_extracted",
            "sharing_scope": sharing_scope,
            "rights_basis": rights_basis,
        },
    }


def _derive_evidence_row(
    observation: Mapping[str, Any],
    *,
    row_id: str,
    artifacts: Mapping[str, Mapping[str, Any]],
    sources: Mapping[str, bytes],
) -> dict[str, Any]:
    evidence_slots = [
        _derive_slot(
            slot,
            artifact=artifacts[slot["artifact_id"]],
            source_bytes=sources.get(slot["artifact_id"]),
            path=f"observation.{observation['observation_key']}.evidence_slots[{index}]",
        )
        for index, slot in enumerate(observation["evidence_slots"])
    ]
    row: dict[str, Any] = {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "surface": SURFACE,
        "row_id": row_id,
        "pair_kind": observation["pair_kind"],
        "observation_key": observation["observation_key"],
        "deviation_id": observation["deviation_id"],
        "deviation_domain": observation["deviation_domain"],
        "evidence_slots": evidence_slots,
        "row_sha256": "",
    }
    row["row_sha256"] = _digest_without(row, "row_sha256")
    return row


def _source_bundle_digest(
    *,
    manifest_sha256: str,
    sidecar_sha256: str,
    sidecar: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> str:
    framing = {
        "source_manifest_sha256": manifest_sha256,
        "preregistration_record_sha256": sidecar_sha256,
        "preregistration_record_digest": sidecar["record_digest"],
        "accepted_draft_artifact_id": manifest["accepted_draft_artifact_id"],
        "accepted_draft_sha256": manifest["accepted_draft_sha256"],
        "artifacts": [copy.deepcopy(item) for item in manifest["artifacts"]],
    }
    return _sha256(_canonical_bytes(framing))


def _prepare_inputs(
    draft: Any,
    manifest: Any,
    sidecar: Any,
    *,
    accepted_draft_bytes: bytes,
    preregistration_bytes: bytes | None,
) -> tuple[
    list[dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
    dict[str, dict[str, Any]],
    dict[str, bytes],
]:
    accepted_text = _strict_accepted_draft(accepted_draft_bytes)
    del accepted_text
    if preregistration_bytes is not None:
        _strict_source(
            preregistration_bytes,
            label="preregistration companion",
            maximum=MAX_PREREGISTRATION_BYTES,
        )
    total = len(accepted_draft_bytes) + len(preregistration_bytes or b"")
    if total > MAX_TOTAL_SOURCE_BYTES:
        _fail("RESOURCE_LIMIT", "sources", "exceed 72 MiB aggregate")
    normalized_sidecar = validate_preregistration_artifact(
        sidecar,
        companion_bytes=preregistration_bytes,
    )
    normalized_manifest, artifacts = validate_source_manifest(
        manifest,
        sidecar=normalized_sidecar,
        accepted_draft_bytes=accepted_draft_bytes,
    )
    observations = validate_draft(
        draft,
        manifest=normalized_manifest,
        artifacts=artifacts,
        sidecar=normalized_sidecar,
    )
    sources = {normalized_manifest["accepted_draft_artifact_id"]: accepted_draft_bytes}
    if preregistration_bytes is not None:
        sources[normalized_sidecar["artifact_id"]] = preregistration_bytes
    return observations, normalized_manifest, normalized_sidecar, artifacts, sources


def finalize_advisory(
    draft: Any,
    manifest: Any,
    sidecar: Any,
    *,
    accepted_draft_bytes: bytes,
    preregistration_bytes: bytes | None,
    draft_raw: bytes | None = None,
    manifest_raw: bytes | None = None,
    sidecar_raw: bytes | None = None,
) -> dict[str, Any]:
    """Build the canonical final carrier from all exact named inputs."""

    draft_bytes = _binding_bytes(
        draft,
        draft_raw,
        MAX_DRAFT_BYTES,
        code="DRAFT_CONTRACT_INVALID",
        path="advisory draft",
    )
    manifest_bytes = _binding_bytes(
        manifest,
        manifest_raw,
        MAX_MANIFEST_BYTES,
        code="SOURCE_MANIFEST_INVALID",
        path="source manifest",
    )
    sidecar_bytes = _binding_bytes(
        sidecar,
        sidecar_raw,
        MAX_SIDECAR_BYTES,
        code="SOURCE_BINDING_INVALID",
        path="preregistration record",
    )
    observations, normalized_manifest, normalized_sidecar, artifacts, sources = (
        _prepare_inputs(
            draft,
            manifest,
            sidecar,
            accepted_draft_bytes=accepted_draft_bytes,
            preregistration_bytes=preregistration_bytes,
        )
    )
    draft_sha = _sha256(draft_bytes)
    manifest_sha = _sha256(manifest_bytes)
    sidecar_sha = _sha256(sidecar_bytes)
    source_bundle_sha = _source_bundle_digest(
        manifest_sha256=manifest_sha,
        sidecar_sha256=sidecar_sha,
        sidecar=normalized_sidecar,
        manifest=normalized_manifest,
    )
    report_identity_payload = {
        "draft_sha256": draft_sha,
        "source_manifest_sha256": manifest_sha,
        "preregistration_record_sha256": sidecar_sha,
        "preregistration_record_digest": normalized_sidecar["record_digest"],
        "accepted_draft_artifact_id": normalized_manifest["accepted_draft_artifact_id"],
        "accepted_draft_sha256": normalized_manifest["accepted_draft_sha256"],
        "source_bundle_sha256": source_bundle_sha,
    }
    report_id = "XDOC-" + _sha256(_canonical_bytes(report_identity_payload))[:24]
    ordered = sorted(
        observations,
        key=lambda item: (PAIR_ORDER.index(item["pair_kind"]), item["observation_key"]),
    )
    grouped: dict[str, list[dict[str, Any]]] = {pair: [] for pair in PAIR_ORDER}
    for ordinal, observation in enumerate(ordered, start=1):
        advisory_id = f"ADV-XDOC-{ordinal:06d}"
        row_id = f"EVR-XDOC-{ordinal:06d}"
        row = _derive_evidence_row(
            observation,
            row_id=row_id,
            artifacts=artifacts,
            sources=sources,
        )
        grouped[observation["pair_kind"]].append(
            {
                "advisory_id": advisory_id,
                "observation_key": observation["observation_key"],
                "pair_kind": observation["pair_kind"],
                "check_state": observation["check_state"],
                "outcome": observation["outcome"],
                "finding_type": observation["finding_type"],
                "negative_basis": observation["negative_basis"],
                "not_checked_reason": observation["not_checked_reason"],
                "deviation_id": observation["deviation_id"],
                "deviation_domain": observation["deviation_domain"],
                "semantic_provenance": SEMANTIC_PROVENANCE,
                "evidence_row": row,
            }
        )
    report: dict[str, Any] = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "layer": LAYER,
        "evaluation_status": EVALUATION_STATUS,
        "report_id": report_id,
        "input_binding": {
            "draft_schema_version": DRAFT_SCHEMA_VERSION,
            "draft_sha256": draft_sha,
            "source_manifest_schema_version": MANIFEST_SCHEMA_VERSION,
            "source_manifest_sha256": manifest_sha,
            "preregistration_record_schema_version": SIDECAR_SCHEMA_VERSION,
            "preregistration_record_sha256": sidecar_sha,
            "preregistration_record_digest": normalized_sidecar["record_digest"],
            "accepted_draft_artifact_id": normalized_manifest[
                "accepted_draft_artifact_id"
            ],
            "accepted_draft_sha256": normalized_manifest["accepted_draft_sha256"],
            "source_bundle_sha256": source_bundle_sha,
        },
        "pair_results": [
            {"pair_kind": pair, "observations": grouped[pair]} for pair in PAIR_ORDER
        ],
        "boundary": copy.deepcopy(BOUNDARY),
        "report_digest": "",
    }
    report["report_digest"] = _digest_without(report, "report_digest")
    if len(_canonical_bytes(report)) > MAX_FINAL_BYTES:
        _fail("RESOURCE_LIMIT", "final advisory", "canonical output exceeds 32 MiB")
    return report


def validate_advisory(
    advisory: Any,
    draft: Any,
    manifest: Any,
    sidecar: Any,
    *,
    advisory_raw: bytes,
    accepted_draft_bytes: bytes,
    preregistration_bytes: bytes | None,
    draft_raw: bytes | None = None,
    manifest_raw: bytes | None = None,
    sidecar_raw: bytes | None = None,
) -> None:
    expected = finalize_advisory(
        draft,
        manifest,
        sidecar,
        accepted_draft_bytes=accepted_draft_bytes,
        preregistration_bytes=preregistration_bytes,
        draft_raw=draft_raw,
        manifest_raw=manifest_raw,
        sidecar_raw=sidecar_raw,
    )
    _require_exact_final(advisory, advisory_raw, expected)


def _require_exact_final(advisory: Any, advisory_raw: bytes, expected: Any) -> None:
    if not isinstance(advisory_raw, bytes):
        _fail("FINAL_ARTIFACT_INVALID", "advisory", "raw binding must be bytes")
    if len(advisory_raw) > MAX_FINAL_BYTES:
        _fail("RESOURCE_LIMIT", "final advisory", "exceeds 32 MiB")
    parsed = _strict_json_bytes(
        advisory_raw,
        code="FINAL_ARTIFACT_INVALID",
        path="final advisory",
    )
    expected_bytes = _canonical_bytes(expected)
    if (
        advisory_raw != expected_bytes
        or _canonical_bytes(parsed) != expected_bytes
        or _canonical_bytes(advisory) != expected_bytes
    ):
        _fail(
            "FINAL_ARTIFACT_INVALID",
            "advisory",
            "is not the exact canonical deterministic replay",
        )


def _markdown_inert(value: Any) -> str:
    if value is None:
        return "NOT CHECKED"
    result: list[str] = []
    for character in str(value):
        if character.isascii() and (character.isalnum() or character == " "):
            result.append(character)
        else:
            result.append(f"&#{ord(character)};")
    return "".join(result)


def paginate(
    items: Sequence[Any], *, page: int, page_size: int
) -> tuple[list[Any], int]:
    if isinstance(page, bool) or not isinstance(page, int) or page < 1:
        _fail("FINAL_ARTIFACT_INVALID", "page", "must be a positive integer")
    if (
        isinstance(page_size, bool)
        or not isinstance(page_size, int)
        or page_size < 1
        or page_size > MAX_PAGE_SIZE
    ):
        _fail("FINAL_ARTIFACT_INVALID", "page_size", "must be within 1..25")
    total_pages = max(1, (len(items) + page_size - 1) // page_size)
    if page > total_pages:
        _fail("FINAL_ARTIFACT_INVALID", "page", f"must not exceed {total_pages}")
    start = (page - 1) * page_size
    return list(items[start : start + page_size]), total_pages


def render_advisory(
    advisory: Mapping[str, Any], *, page: int = 1, page_size: int = 25
) -> str:
    observations = [
        observation
        for pair_result in advisory["pair_results"]
        for observation in pair_result["observations"]
    ]
    visible, total_pages = paginate(observations, page=page, page_size=page_size)
    report_sha = _sha256(_canonical_bytes(advisory))
    lines = [
        f"# Cross-document consistency advisory — Page {page}/{total_pages}",
        "",
        "Layer: LLM-ADVISORY",
        "Evaluation status: UNMEASURED",
        f"Report ID: {_markdown_inert(advisory['report_id'])}",
        f"Report SHA-256: {report_sha}",
        f"Rows: {len(observations)} total; {len(visible)} on this page",
        "",
        "NO LISTED INCONSISTENCY LOCATED — not proof of agreement, completeness, or a clean document.",
        "",
        "| Advisory | Pair | State | Observation | Left | Right | Disclosure | Result | Evidence |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for observation in visible:
        row = observation["evidence_row"]
        slots = row["evidence_slots"]
        display_slots: list[str] = []
        for slot in slots:
            locator = slot["document_locator"]
            if slot["evidence_state"] == "agent_extracted":
                evidence = slot["anchor"]["value_decoded"]
            elif slot["evidence_state"] == "checked_no_match":
                evidence = "CHECKED NO MATCH"
            else:
                evidence = "NOT CHECKED"
            display_slots.append(
                f"{slot['logical_role']} @ {locator['kind']}: {locator['value']} — "
                f"{slot['evidence_state']} — {evidence}"
            )
        while len(display_slots) < 3:
            display_slots.append("not applicable")
        if observation["outcome"] == "NO_LISTED_INCONSISTENCY_LOCATED":
            result = f"{observation['outcome']} — {observation['negative_basis']}"
        else:
            result = (
                observation["finding_type"]
                or observation["not_checked_reason"]
                or observation["outcome"]
            )
        evidence_ref = f"{row['row_id']} / {row['row_sha256']}"
        values = (
            observation["advisory_id"],
            observation["pair_kind"],
            observation["check_state"],
            observation["observation_key"],
            display_slots[0],
            display_slots[1],
            display_slots[2],
            result,
            evidence_ref,
        )
        lines.append(
            "| " + " | ".join(_markdown_inert(value) for value in values) + " |"
        )
    lines.append("")
    if page > 1:
        lines.append(f"Previous: `--page {page - 1} --page-size {page_size}`")
    if page < total_pages:
        lines.append(f"Next: `--page {page + 1} --page-size {page_size}`")
    lines.append("")
    return "\n".join(lines)


def _load_runtime_inputs(args: argparse.Namespace) -> dict[str, Any]:
    sidecar, sidecar_raw = _load_json(
        args.preregistration_record,
        MAX_SIDECAR_BYTES,
        code="SOURCE_BINDING_INVALID",
        label="preregistration record",
    )
    companion_bytes = (
        _read_named_bytes(
            args.preregistration_companion,
            MAX_PREREGISTRATION_BYTES,
            label="preregistration companion",
            unreadable_code="SOURCE_BINDING_INVALID",
        )
        if args.preregistration_companion is not None
        else None
    )
    accepted_bytes = _read_named_bytes(
        args.accepted_draft,
        MAX_ACCEPTED_DRAFT_BYTES,
        label="accepted draft",
    )
    manifest, manifest_raw = _load_json(
        args.manifest,
        MAX_MANIFEST_BYTES,
        code="SOURCE_MANIFEST_INVALID",
        label="source manifest",
    )
    # Establish all source/sidecar/manifest bindings before parsing semantic outcomes.
    _strict_accepted_draft(accepted_bytes)
    if companion_bytes is not None:
        _strict_source(
            companion_bytes,
            label="preregistration companion",
            maximum=MAX_PREREGISTRATION_BYTES,
        )
    if len(accepted_bytes) + len(companion_bytes or b"") > MAX_TOTAL_SOURCE_BYTES:
        _fail("RESOURCE_LIMIT", "sources", "exceed 72 MiB aggregate")
    normalized_sidecar = validate_preregistration_artifact(
        sidecar,
        companion_bytes=companion_bytes,
    )
    validate_source_manifest(
        manifest,
        sidecar=normalized_sidecar,
        accepted_draft_bytes=accepted_bytes,
    )
    draft, draft_raw = _load_json(
        args.draft,
        MAX_DRAFT_BYTES,
        code="DRAFT_CONTRACT_INVALID",
        label="advisory draft",
    )
    return {
        "sidecar": sidecar,
        "sidecar_raw": sidecar_raw,
        "companion_bytes": companion_bytes,
        "accepted_bytes": accepted_bytes,
        "manifest": manifest,
        "manifest_raw": manifest_raw,
        "draft": draft,
        "draft_raw": draft_raw,
    }


def _expected_from_loaded(loaded: Mapping[str, Any]) -> dict[str, Any]:
    return finalize_advisory(
        loaded["draft"],
        loaded["manifest"],
        loaded["sidecar"],
        accepted_draft_bytes=loaded["accepted_bytes"],
        preregistration_bytes=loaded["companion_bytes"],
        draft_raw=loaded["draft_raw"],
        manifest_raw=loaded["manifest_raw"],
        sidecar_raw=loaded["sidecar_raw"],
    )


def _parser() -> argparse.ArgumentParser:
    parser = _ClosedArgumentParser(description=__doc__, allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True)

    sidecar = commands.add_parser("build-preregistration-artifact", allow_abbrev=False)
    sidecar.add_argument("--status", required=True, choices=sorted(SIDECAR_STATES))
    sidecar.add_argument("--artifact-id", required=True)
    sidecar.add_argument("--declared-at", required=True)
    sidecar.add_argument("--relative-path")
    sidecar.add_argument("--artifact-provenance")
    sidecar.add_argument("--companion", type=Path)
    sidecar.add_argument("--output", type=Path, required=True)

    for name in ("finalize", "validate", "render"):
        command = commands.add_parser(name, allow_abbrev=False)
        command.add_argument("--draft", type=Path, required=True)
        command.add_argument("--manifest", type=Path, required=True)
        command.add_argument("--preregistration-record", type=Path, required=True)
        command.add_argument("--preregistration-companion", type=Path)
        command.add_argument("--accepted-draft", type=Path, required=True)
        if name in {"validate", "render"}:
            command.add_argument("--advisory", type=Path, required=True)
        if name in {"finalize", "render"}:
            command.add_argument("--output", type=Path)
        if name == "render":
            command.add_argument("--page", type=int, default=1)
            command.add_argument("--page-size", type=int, default=25)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        if args.command == "build-preregistration-artifact":
            companion = (
                _read_named_bytes(
                    args.companion,
                    MAX_PREREGISTRATION_BYTES,
                    label="preregistration companion",
                )
                if args.companion is not None
                else None
            )
            _reject_output_alias(args.output, (args.companion,))
            record = build_preregistration_artifact(
                status=args.status,
                artifact_id=args.artifact_id,
                declared_at=args.declared_at,
                companion_bytes=companion,
                relative_path=args.relative_path,
                artifact_provenance=args.artifact_provenance,
            )
            _atomic_write(args.output, _canonical_bytes(record))
            return 0

        loaded = _load_runtime_inputs(args)
        expected = _expected_from_loaded(loaded)
        if args.command == "finalize":
            payload = _canonical_bytes(expected)
            if args.output is None:
                sys.stdout.buffer.write(payload)
            else:
                _reject_output_alias(
                    args.output,
                    (
                        args.draft,
                        args.manifest,
                        args.preregistration_record,
                        args.preregistration_companion,
                        args.accepted_draft,
                    ),
                )
                _atomic_write(args.output, payload)
            return 0

        advisory, advisory_raw = _load_json(
            args.advisory,
            MAX_FINAL_BYTES,
            code="FINAL_ARTIFACT_INVALID",
            label="final advisory",
        )
        _require_exact_final(advisory, advisory_raw, expected)
        if args.command == "validate":
            print("Cross-document consistency advisory validation passed (#672).")
            return 0
        rendered = render_advisory(expected, page=args.page, page_size=args.page_size)
        if args.output is None:
            sys.stdout.write(rendered)
        else:
            _reject_output_alias(
                args.output,
                (
                    args.draft,
                    args.manifest,
                    args.preregistration_record,
                    args.preregistration_companion,
                    args.accepted_draft,
                    args.advisory,
                ),
            )
            _atomic_write(args.output, rendered.encode("utf-8"))
        return 0
    except AdvisoryError as exc:
        print(f"ADVISORY_UNAVAILABLE:{exc.code}", file=sys.stderr)
        return 2
    except (
        IndexError,
        KeyError,
        OSError,
        RecursionError,
        TypeError,
        UnicodeError,
        ValueError,
    ):
        print("ADVISORY_UNAVAILABLE:FINAL_ARTIFACT_INVALID", file=sys.stderr)
        return 2


__all__ = [
    "AdvisoryError",
    "DRAFT_SCHEMA_VERSION",
    "EVIDENCE_SCHEMA_VERSION",
    "EVALUATION_STATUS",
    "LAYER",
    "MANIFEST_SCHEMA_VERSION",
    "MAX_PAGE_SIZE",
    "REPORT_SCHEMA_VERSION",
    "SIDECAR_SCHEMA_VERSION",
    "SURFACE",
    "build_preregistration_artifact",
    "finalize_advisory",
    "main",
    "paginate",
    "render_advisory",
    "strict_percent_decode",
    "validate_advisory",
    "validate_preregistration_artifact",
    "validate_source_manifest",
]


if __name__ == "__main__":
    raise SystemExit(main())
