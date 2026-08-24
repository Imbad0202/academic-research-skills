#!/usr/bin/env python3
"""Validate, replay, and durably publish inquiry-branch-ledger/1.0 (#743).

The ledger is an opt-in, event-sourced user-project artifact.  This module is
deliberately manuscript-blind and model-free: callers supply exact profile
documents, timestamps, event payloads, workspace paths, and project identity.
It never infers a research family, branch, condition, or author decision.

Runtime interpretations needed to make the frozen design executable:

* profile bindings are resolved only through an explicit catalog of fully
  validated research-workflow-profile/1.0 documents.  A digest is not a
  branch budget, and the current shipped fallback is never substituted for an
  unresolved historical binding;
* a non-null parent_id must already exist when a branch is introduced;
* downstream_refs are identifier lists, so duplicates are rejected.  This
  makes "one stale event per identifier" and merge/supersession order unique;
* a newly emitted reopen-condition signal must name a condition still present
  on a non-terminal branch.  Removed condition ids remain retired and can be
  resolved in historical events, but cannot motivate a new event;
* a branch_reopened event is followed immediately, in current downstream-ref
  order, by exactly one system artifact_marked_stale event per identifier.
  A missing, delayed, reordered, or orphan system event fails replay;
* repeated supersession resolutions for distinct stale causes of the same
  artifact must name the same replacement.  Replacing an identifier with
  itself is not a replacement;
* persisted publication requires at least two introduced branches, matching
  the frozen rule that the ledger/pointer do not materialize on the simple
  zero-or-one-branch path.  In-memory replay remains available before that;
* ledger_path is an explicitly workspace-relative POSIX path and the ledger
  must be beside the passport.  No path is resolved relative to the process
  working directory;
* two stable filesystem paths cannot be renamed atomically together.  A
  shared passport-domain sidecar lock, full-byte compare-and-swap checks, and
  a durable recovery journal make the two-file update atomic for cooperating
  ARS readers.  Without a valid recoverable journal, an unreadable/mismatched
  pointer is surfaced as
  LEDGER-BINDING-BROKEN and is never silently continued.

The hash chain is tamper-evident relative to the separately trusted passport
pointer.  It is not authentication: a party able to rewrite both artifacts
can recompute both hashes, just as the design's within-session author labels
do not authenticate a human identity.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import math
import os
import re
import stat
import sys
import time
import unicodedata
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Iterator, Mapping, NoReturn, Sequence

try:  # POSIX is the supported durable-publication platform for this alpha.
    import fcntl
except ImportError:  # pragma: no cover - exercised only on non-POSIX hosts
    fcntl = None  # type: ignore[assignment]

try:  # Dual-path import: script invocation vs package import under pytest.
    from research_workflow_profile import (
        JCS_SAFE_INTEGER_MAX,
        ContractError as ProfileContractError,
        canonical_bytes as _profile_canonical_bytes,
        load_profile,
        profile_binding,
        validate_profile,
    )
except ImportError:  # pragma: no cover - package-import path
    from scripts.research_workflow_profile import (
        JCS_SAFE_INTEGER_MAX,
        ContractError as ProfileContractError,
        canonical_bytes as _profile_canonical_bytes,
        load_profile,
        profile_binding,
        validate_profile,
    )


LEDGER_SCHEMA_VERSION = "inquiry-branch-ledger/1.0"
POINTER_LEDGER_VERSION = LEDGER_SCHEMA_VERSION
TRANSACTION_SCHEMA_VERSION = "inquiry-ledger-transaction/1.0"
ZERO_SHA256 = "0" * 64
ENV_FLAG = "ARS_INQUIRY_LEDGER"

EVENT_KINDS = (
    "branch_created",
    "facet_surfaced",
    "branch_adopted",
    "branch_annotated",
    "branch_parked",
    "branch_rejected",
    "branch_reopened",
    "branch_merged",
    "branch_archived",
    "reopen_condition_signal",
    "profile_rebound",
    "artifact_marked_stale",
    "artifact_reconfirmed",
    "artifact_superseded",
)
AI_EVENT_KINDS = frozenset({"facet_surfaced", "reopen_condition_signal"})
SYSTEM_EVENT_KINDS = frozenset({"artifact_marked_stale"})
ARTIFACT_EVENT_KINDS = frozenset(
    {"artifact_marked_stale", "artifact_reconfirmed", "artifact_superseded"}
)
NULL_BRANCH_EVENT_KINDS = ARTIFACT_EVENT_KINDS | {"profile_rebound"}
LIVE_STATUSES = frozenset({"active", "reopened"})
TERMINAL_STATUSES = frozenset({"merged", "archived"})
BRANCH_STATUSES = (
    "active",
    "parked",
    "rejected",
    "reopened",
    "merged",
    "archived",
)
AUTHOR_OWNED_PROVENANCE = frozenset({"author_originated", "author_adopted"})
AUTHOR_REOPENABLE_STATUSES = frozenset({"parked", "rejected"})
PROVENANCE_VALUES = (
    "author_originated",
    "ai_surfaced_facet",
    "author_adopted",
)
ANNOTATION_FIELDS = (
    "assumptions",
    "evidence_sought",
    "reopen_conditions",
    "downstream_refs",
)
SUMMARY_MOMENTS = (
    "design_freeze",
    "stage_2_5",
    "stage_4_5",
    "reopen_condition_signal",
)
_SUMMARY_TEXT_LIMIT = 160
_MARKDOWN_META = frozenset("\\`*_[]<>|")

_LEDGER_FIELDS = {
    "schema_version",
    "project_ref",
    "initial_profile_binding",
    "events",
}
_EVENT_FIELDS = {
    "event_id",
    "recorded_at",
    "actor",
    "kind",
    "branch_id",
    "payload",
    "prev_event_sha256",
}
_EVENT_INPUT_FIELDS = {
    "recorded_at",
    "actor",
    "kind",
    "branch_id",
    "payload",
}
_BINDING_FIELDS = {"profile_id", "profile_version", "content_sha256"}
_POINTER_FIELDS = {"ledger_path", "ledger_version", "content_sha256"}

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_SEMVER_RE = re.compile(
    r"^(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)"
    r"(?:-((?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_RFC3339_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt]"
    r"(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
    r"(?:\.[0-9]+)?(?:[Zz]|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])$"
)
_FORBIDDEN_PATH_CHARS_RE = re.compile(
    "[\\x00-\\x1f\\x7f-\\x9f"
    "\u00ad\u0600-\u0605\u061c\u06dd\u070f\u0890-\u0891\u08e2"
    "\u180e\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u206f"
    "\ufeff\ufff9-\ufffb]"
)


class ContractError(ValueError):
    """Raised when ledger input or replay violates the frozen contract."""


class LedgerBindingError(ContractError):
    """Raised for the design's visible LEDGER-BINDING-BROKEN load state."""

    def __init__(self, message: str):
        super().__init__(f"LEDGER-BINDING-BROKEN: {message}")


class TransactionRecoveryError(ContractError):
    """Raised when a durable journal exists but cannot be safely recovered."""

    def __init__(self, message: str):
        super().__init__(f"LEDGER-TRANSACTION-RECOVERY-REQUIRED: {message}")


def _fail(path: str, message: str) -> NoReturn:
    raise ContractError(f"{path}: {message}")


def canonical_bytes(value: Any) -> bytes:
    """Restricted JCS bytes shared byte-for-byte with the #742 runtime."""

    try:
        return _profile_canonical_bytes(value)
    except ProfileContractError as exc:
        raise ContractError(str(exc)) from exc


def _reject_constant(value: str) -> NoReturn:
    raise ContractError(f"non-finite JSON number is not allowed: {value}")


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON key is not allowed: {key}")
        result[key] = value
    return result


def _parse_json_bytes(raw: bytes, *, source: str) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractError(f"JSON input is not UTF-8: {source}") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, ContractError) as exc:
        raise ContractError(f"cannot parse JSON input {source}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"top-level JSON value must be an object: {source}")
    return value


def load_ledger(path: Path | str, *, require_canonical: bool = True) -> dict[str, Any]:
    """Load a ledger with duplicate-key rejection and exact canonical storage."""

    ledger_path = Path(path)
    try:
        raw = ledger_path.read_bytes()
    except OSError as exc:
        raise ContractError(f"cannot read ledger {ledger_path}: {exc}") from exc
    value = _parse_json_bytes(raw, source=str(ledger_path))
    if require_canonical and raw != canonical_bytes(value):
        raise ContractError(
            f"ledger file must be stored as exact JSON Canonical Form bytes: {ledger_path}"
        )
    return value


def _object(
    value: Any,
    path: str,
    required: set[str],
    optional: set[str] | None = None,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail(path, "must be an object")
    optional = optional or set()
    keys = set(value)
    missing = required - keys
    extra = keys - required - optional
    if missing:
        _fail(path, f"missing field(s): {', '.join(sorted(missing))}")
    if extra:
        _fail(path, f"undeclared field(s): {', '.join(sorted(extra))}")
    return value


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(path, "must be a non-empty string")
    return value


def _slug(value: Any, path: str) -> str:
    text = _text(value, path)
    if _SLUG_RE.fullmatch(text) is None:
        _fail(path, "must be a lowercase slug using letters, digits, '_' or '-'")
    return text


def _semver(value: Any, path: str) -> str:
    text = _text(value, path)
    if _SEMVER_RE.fullmatch(text) is None:
        _fail(path, "must be a SemVer 2.0.0 version")
    return text


def _sha256(value: Any, path: str) -> str:
    text = _text(value, path)
    if _SHA256_RE.fullmatch(text) is None:
        _fail(path, "must be a lowercase 64-hex SHA-256 digest")
    return text


def _positive_int(value: Any, path: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
        or value > JCS_SAFE_INTEGER_MAX
    ):
        _fail(path, f"must be an integer from 1 through {JCS_SAFE_INTEGER_MAX}")
    return value


def _nonnegative_int(value: Any, path: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
        or value > JCS_SAFE_INTEGER_MAX
    ):
        _fail(path, f"must be an integer from 0 through {JCS_SAFE_INTEGER_MAX}")
    return value


def _rfc3339(value: Any, path: str) -> str:
    text = _text(value, path)
    if _RFC3339_RE.fullmatch(text) is None:
        _fail(path, "must be an ISO 8601 date-time with offset")
    normalized = text[:10] + "T" + text[11:]
    if normalized.endswith(("Z", "z")):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ContractError(f"{path}: must be an ISO 8601 date-time with offset") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(path, "must be an ISO 8601 date-time with offset")
    return text


def _enum(value: Any, path: str, choices: Sequence[str]) -> str:
    if value not in choices:
        _fail(path, f"must be one of: {', '.join(choices)}")
    return value


def _nullable_slug(value: Any, path: str) -> str | None:
    if value is None:
        return None
    return _slug(value, path)


def _text_list(
    value: Any, path: str, *, unique: bool = False
) -> list[str]:
    if not isinstance(value, list):
        _fail(path, "must be an array")
    result = [_text(item, f"{path}[{index}]") for index, item in enumerate(value)]
    if unique and len(set(result)) != len(result):
        _fail(path, "must not contain duplicate identifiers")
    return result


def _validate_binding(value: Any, path: str) -> dict[str, str]:
    binding = _object(value, path, _BINDING_FIELDS)
    return {
        "profile_id": _slug(binding["profile_id"], f"{path}.profile_id"),
        "profile_version": _semver(
            binding["profile_version"], f"{path}.profile_version"
        ),
        "content_sha256": _sha256(
            binding["content_sha256"], f"{path}.content_sha256"
        ),
    }


def _validate_conditions(value: Any, path: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        _fail(path, "must be an array")
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, raw in enumerate(value):
        item_path = f"{path}[{index}]"
        condition = _object(
            raw,
            item_path,
            {"condition_id", "statement"},
            {"evidence_pointer"},
        )
        condition_id = _text(condition["condition_id"], f"{item_path}.condition_id")
        if condition_id in seen:
            _fail(path, f"duplicate condition_id: {condition_id}")
        seen.add(condition_id)
        normalized = {
            "condition_id": condition_id,
            "statement": _text(condition["statement"], f"{item_path}.statement"),
        }
        if "evidence_pointer" in condition:
            normalized["evidence_pointer"] = _text(
                condition["evidence_pointer"], f"{item_path}.evidence_pointer"
            )
        result.append(normalized)
    return result


def _validate_event_shape(raw_event: Any, path: str) -> None:
    event = _object(raw_event, path, _EVENT_FIELDS)
    _positive_int(event["event_id"], f"{path}.event_id")
    _rfc3339(event["recorded_at"], f"{path}.recorded_at")
    actor = _enum(event["actor"], f"{path}.actor", ("author", "ai", "system"))
    kind = _enum(event["kind"], f"{path}.kind", EVENT_KINDS)
    _sha256(event["prev_event_sha256"], f"{path}.prev_event_sha256")

    expected_actor = "ai" if kind in AI_EVENT_KINDS else (
        "system" if kind in SYSTEM_EVENT_KINDS else "author"
    )
    if actor != expected_actor:
        _fail(f"{path}.actor", f"must equal {expected_actor} for {kind}")

    if kind in NULL_BRANCH_EVENT_KINDS:
        if event["branch_id"] is not None:
            _fail(f"{path}.branch_id", f"must be null for {kind}")
    else:
        _slug(event["branch_id"], f"{path}.branch_id")

    payload_path = f"{path}.payload"
    payload = event["payload"]
    if kind == "branch_created":
        value = _object(
            payload,
            payload_path,
            {
                "parent_id",
                "statement",
                "assumptions",
                "evidence_sought",
                "reopen_conditions",
                "downstream_refs",
            },
        )
        _nullable_slug(value["parent_id"], f"{payload_path}.parent_id")
        _text(value["statement"], f"{payload_path}.statement")
        _text_list(value["assumptions"], f"{payload_path}.assumptions")
        _text_list(value["evidence_sought"], f"{payload_path}.evidence_sought")
        _validate_conditions(
            value["reopen_conditions"], f"{payload_path}.reopen_conditions"
        )
        _text_list(
            value["downstream_refs"],
            f"{payload_path}.downstream_refs",
            unique=True,
        )
    elif kind == "facet_surfaced":
        value = _object(payload, payload_path, {"parent_id", "surfaced_text"})
        _nullable_slug(value["parent_id"], f"{payload_path}.parent_id")
        _text(value["surfaced_text"], f"{payload_path}.surfaced_text")
    elif kind == "branch_adopted":
        value = _object(
            payload,
            payload_path,
            {"source_event_id", "surfaced_text", "author_formulation"},
        )
        _positive_int(value["source_event_id"], f"{payload_path}.source_event_id")
        surfaced = _text(value["surfaced_text"], f"{payload_path}.surfaced_text")
        formulation = _text(
            value["author_formulation"], f"{payload_path}.author_formulation"
        )
        if formulation == surfaced:
            _fail(
                f"{payload_path}.author_formulation",
                "must not be byte-identical to surfaced_text",
            )
        if formulation.strip().casefold() == "ok":
            _fail(
                f"{payload_path}.author_formulation",
                "a bare 'ok' is not an adoption formulation",
            )
    elif kind == "branch_annotated":
        value = _object(payload, payload_path, {"field", "value"})
        field = _enum(value["field"], f"{payload_path}.field", ANNOTATION_FIELDS)
        if field == "reopen_conditions":
            _validate_conditions(value["value"], f"{payload_path}.value")
        else:
            _text_list(
                value["value"],
                f"{payload_path}.value",
                unique=field == "downstream_refs",
            )
    elif kind in {"branch_parked", "branch_rejected", "branch_archived"}:
        value = _object(payload, payload_path, {"reason"})
        _text(value["reason"], f"{payload_path}.reason")
    elif kind == "branch_reopened":
        value = _object(
            payload,
            payload_path,
            {"reason"},
            {"condition_id", "evidence_pointer"},
        )
        _text(value["reason"], f"{payload_path}.reason")
        if "condition_id" in value:
            _text(value["condition_id"], f"{payload_path}.condition_id")
        if "evidence_pointer" in value:
            _text(value["evidence_pointer"], f"{payload_path}.evidence_pointer")
    elif kind == "branch_merged":
        value = _object(payload, payload_path, {"merged_into", "reason"})
        _slug(value["merged_into"], f"{payload_path}.merged_into")
        _text(value["reason"], f"{payload_path}.reason")
    elif kind == "reopen_condition_signal":
        value = _object(
            payload,
            payload_path,
            {"branch_id_ref", "condition_id", "evidence_pointer"},
        )
        _slug(value["branch_id_ref"], f"{payload_path}.branch_id_ref")
        _text(value["condition_id"], f"{payload_path}.condition_id")
        _text(value["evidence_pointer"], f"{payload_path}.evidence_pointer")
        if value["branch_id_ref"] != event["branch_id"]:
            _fail(
                f"{payload_path}.branch_id_ref",
                "must equal the event-level branch_id",
            )
    elif kind == "profile_rebound":
        value = _object(
            payload,
            payload_path,
            _BINDING_FIELDS | {"selection_receipt_ref"},
        )
        _validate_binding(
            {key: value[key] for key in _BINDING_FIELDS},
            payload_path,
        )
        _text(value["selection_receipt_ref"], f"{payload_path}.selection_receipt_ref")
    elif kind == "artifact_marked_stale":
        value = _object(
            payload, payload_path, {"artifact_ref", "reopening_event_id"}
        )
        _text(value["artifact_ref"], f"{payload_path}.artifact_ref")
        _positive_int(
            value["reopening_event_id"], f"{payload_path}.reopening_event_id"
        )
    elif kind == "artifact_reconfirmed":
        value = _object(
            payload,
            payload_path,
            {"artifact_ref", "resolves_stale_event_id", "note"},
        )
        _text(value["artifact_ref"], f"{payload_path}.artifact_ref")
        _positive_int(
            value["resolves_stale_event_id"],
            f"{payload_path}.resolves_stale_event_id",
        )
        _text(value["note"], f"{payload_path}.note")
    elif kind == "artifact_superseded":
        value = _object(
            payload,
            payload_path,
            {"artifact_ref", "resolves_stale_event_id", "note", "replaced_by"},
        )
        artifact_ref = _text(value["artifact_ref"], f"{payload_path}.artifact_ref")
        _positive_int(
            value["resolves_stale_event_id"],
            f"{payload_path}.resolves_stale_event_id",
        )
        _text(value["note"], f"{payload_path}.note")
        replaced_by = _text(value["replaced_by"], f"{payload_path}.replaced_by")
        if replaced_by == artifact_ref:
            _fail(f"{payload_path}.replaced_by", "must differ from artifact_ref")


def validate_ledger_shape(ledger: Mapping[str, Any]) -> None:
    """Validate only the closed document/event shapes (not replay semantics)."""

    value = _object(ledger, "ledger", _LEDGER_FIELDS)
    if value["schema_version"] != LEDGER_SCHEMA_VERSION:
        _fail("ledger.schema_version", f"must equal {LEDGER_SCHEMA_VERSION}")
    _text(value["project_ref"], "ledger.project_ref")
    _validate_binding(value["initial_profile_binding"], "ledger.initial_profile_binding")
    events = value["events"]
    if not isinstance(events, list):
        _fail("ledger.events", "must be an array")
    for index, event in enumerate(events):
        _validate_event_shape(event, f"ledger.events[{index}]")


def _binding_key(binding: Mapping[str, Any]) -> tuple[str, str, str]:
    return (
        str(binding["profile_id"]),
        str(binding["profile_version"]),
        str(binding["content_sha256"]),
    )


def build_profile_catalog(
    profiles: Iterable[Mapping[str, Any]] | Mapping[Any, Mapping[str, Any]],
) -> dict[tuple[str, str, str], Mapping[str, Any]]:
    """Build an exact-binding catalog; never supplies an implicit fallback."""

    if isinstance(profiles, Mapping) and "schema_version" in profiles:
        candidates: Iterable[Mapping[str, Any]] = [profiles]
    elif isinstance(profiles, Mapping):
        candidates = profiles.values()
    else:
        candidates = profiles
    catalog: dict[tuple[str, str, str], Mapping[str, Any]] = {}
    for index, profile in enumerate(candidates):
        try:
            validate_profile(profile)
            binding = profile_binding(profile)
        except (ProfileContractError, TypeError, ValueError) as exc:
            raise ContractError(f"profiles[{index}]: invalid profile: {exc}") from exc
        key = _binding_key(binding)
        if key in catalog and canonical_bytes(catalog[key]) != canonical_bytes(profile):
            _fail(f"profiles[{index}]", "duplicate binding has different content")
        catalog[key] = profile
    if not catalog:
        _fail("profiles", "must explicitly supply at least one exact profile document")
    return catalog


def load_profile_catalog(
    paths: Sequence[Path | str],
) -> dict[tuple[str, str, str], Mapping[str, Any]]:
    if not paths:
        _fail("profiles", "at least one --profile path is required")
    loaded: list[Mapping[str, Any]] = []
    for raw_path in paths:
        try:
            loaded.append(load_profile(Path(raw_path)))
        except (ProfileContractError, OSError) as exc:
            raise ContractError(f"cannot load profile {raw_path}: {exc}") from exc
    return build_profile_catalog(loaded)


def _resolve_profile(
    binding: Mapping[str, Any],
    catalog: Mapping[tuple[str, str, str], Mapping[str, Any]],
    path: str,
) -> Mapping[str, Any]:
    key = _binding_key(binding)
    profile = catalog.get(key)
    if profile is None:
        _fail(
            path,
            "binding is unresolved in the explicit profile catalog "
            f"({key[0]}@{key[1]} {key[2]})",
        )
    return profile


def _is_terminal(branch: Mapping[str, Any]) -> bool:
    if branch["status"] in TERMINAL_STATUSES:
        return True
    return (
        branch["status"] == "rejected"
        and branch["provenance"] == "ai_surfaced_facet"
    )


def _require_branch(
    branches: Mapping[str, dict[str, Any]], branch_id: Any, path: str
) -> dict[str, Any]:
    branch = branches.get(str(branch_id))
    if branch is None:
        _fail(path, f"unknown branch_id: {branch_id}")
    return branch


def _condition_map(branch: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        condition["condition_id"]: condition
        for condition in branch["reopen_conditions"]
    }


def _dedupe_ordered(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _public_branch(branch: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: copy.deepcopy(value)
        for key, value in branch.items()
        if not key.startswith("_")
    }


def replay_ledger(
    ledger: Mapping[str, Any],
    profiles: Iterable[Mapping[str, Any]] | Mapping[Any, Mapping[str, Any]],
    *,
    expected_project_ref: str | None = None,
    require_materialized: bool = False,
) -> dict[str, Any]:
    """Purely replay a ledger and return its deterministic projection.

    No file, environment, clock, model, or network state is consulted.
    """

    validate_ledger_shape(ledger)
    if expected_project_ref is not None:
        _text(expected_project_ref, "expected_project_ref")
        if ledger["project_ref"] != expected_project_ref:
            _fail(
                "ledger.project_ref",
                f"does not equal expected project_ref {expected_project_ref!r}",
            )
    catalog = build_profile_catalog(profiles)
    initial_binding = _validate_binding(
        ledger["initial_profile_binding"], "ledger.initial_profile_binding"
    )
    current_profile = _resolve_profile(
        initial_binding, catalog, "ledger.initial_profile_binding"
    )
    effective_binding = copy.deepcopy(initial_binding)

    branches: dict[str, dict[str, Any]] = {}
    artifacts: dict[str, dict[str, Any]] = {}
    stale_causes: dict[int, dict[str, Any]] = {}
    signals: list[dict[str, Any]] = []
    supersession_targets: dict[str, str] = {}
    expected_stale: list[tuple[str, int]] = []
    introduced_count = 0

    events = ledger["events"]
    for index, raw_event in enumerate(events):
        event = raw_event
        path = f"ledger.events[{index}]"
        expected_id = index + 1
        if event["event_id"] != expected_id:
            _fail(f"{path}.event_id", f"must equal dense event id {expected_id}")
        expected_prev = (
            ZERO_SHA256
            if index == 0
            else hashlib.sha256(canonical_bytes(events[index - 1])).hexdigest()
        )
        if event["prev_event_sha256"] != expected_prev:
            _fail(
                f"{path}.prev_event_sha256",
                "does not equal the canonical SHA-256 of the previous event",
            )

        kind = event["kind"]
        branch_id = event["branch_id"]
        payload = event["payload"]

        if expected_stale:
            expected_artifact, reopening_id = expected_stale.pop(0)
            if kind != "artifact_marked_stale":
                _fail(
                    path,
                    "must be the contiguous artifact_marked_stale event "
                    f"for {expected_artifact!r} after reopening event {reopening_id}",
                )
            if payload["artifact_ref"] != expected_artifact:
                _fail(
                    f"{path}.payload.artifact_ref",
                    f"must equal {expected_artifact!r} in downstream_refs order",
                )
            if payload["reopening_event_id"] != reopening_id:
                _fail(
                    f"{path}.payload.reopening_event_id",
                    f"must equal reopening event {reopening_id}",
                )
            artifact = artifacts.setdefault(
                expected_artifact,
                {
                    "artifact_ref": expected_artifact,
                    "outstanding_stale_causes": [],
                    "resolution_history": [],
                },
            )
            artifact["outstanding_stale_causes"].append(event["event_id"])
            stale_causes[event["event_id"]] = {
                "artifact_ref": expected_artifact,
                "reopening_event_id": reopening_id,
            }
        elif kind == "artifact_marked_stale":
            _fail(path, "orphan artifact_marked_stale event")
        elif kind in {"branch_created", "facet_surfaced"}:
            assert isinstance(branch_id, str)
            if branch_id in branches:
                _fail(f"{path}.branch_id", "branch ids are stable and cannot be reused")
            parent_id = payload["parent_id"]
            if parent_id is not None and parent_id not in branches:
                _fail(
                    f"{path}.payload.parent_id",
                    "must name a branch introduced by an earlier event",
                )
            introduced_count += 1
            if kind == "branch_created":
                conditions = copy.deepcopy(payload["reopen_conditions"])
                branches[branch_id] = {
                    "branch_id": branch_id,
                    "parent_id": parent_id,
                    "provenance": "author_originated",
                    "statement": payload["statement"],
                    "surfaced_text": None,
                    "adoption_receipt": None,
                    "assumptions": copy.deepcopy(payload["assumptions"]),
                    "evidence_sought": copy.deepcopy(payload["evidence_sought"]),
                    "status": "active",
                    "disposition_reason": None,
                    "reopen_conditions": conditions,
                    "downstream_refs": copy.deepcopy(payload["downstream_refs"]),
                    "merged_into": None,
                    "_origin_event_id": event["event_id"],
                    "_condition_history": {
                        item["condition_id"]: item["statement"] for item in conditions
                    },
                    "_retired_condition_ids": set(),
                }
            else:
                branches[branch_id] = {
                    "branch_id": branch_id,
                    "parent_id": parent_id,
                    "provenance": "ai_surfaced_facet",
                    "statement": None,
                    "surfaced_text": payload["surfaced_text"],
                    "adoption_receipt": None,
                    "assumptions": [],
                    "evidence_sought": [],
                    "status": "parked",
                    "disposition_reason": None,
                    "reopen_conditions": [],
                    "downstream_refs": [],
                    "merged_into": None,
                    "_origin_event_id": event["event_id"],
                    "_condition_history": {},
                    "_retired_condition_ids": set(),
                }
        elif kind == "branch_adopted":
            branch = _require_branch(branches, branch_id, f"{path}.branch_id")
            if branch["provenance"] != "ai_surfaced_facet" or branch["status"] != "parked":
                _fail(path, "branch_adopted is lawful only on a parked unadopted facet")
            if payload["source_event_id"] != branch["_origin_event_id"]:
                _fail(
                    f"{path}.payload.source_event_id",
                    "must name the facet_surfaced event that introduced this branch",
                )
            if payload["surfaced_text"] != branch["surfaced_text"]:
                _fail(
                    f"{path}.payload.surfaced_text",
                    "must retain the originating surfaced_text verbatim",
                )
            branch["provenance"] = "author_adopted"
            branch["statement"] = payload["author_formulation"]
            branch["adoption_receipt"] = copy.deepcopy(payload)
            branch["status"] = "active"
        elif kind == "branch_annotated":
            branch = _require_branch(branches, branch_id, f"{path}.branch_id")
            if _is_terminal(branch):
                _fail(path, "terminal branches cannot be annotated")
            field = payload["field"]
            replacement = copy.deepcopy(payload["value"])
            if field == "reopen_conditions":
                old = _condition_map(branch)
                new = {item["condition_id"]: item for item in replacement}
                history: dict[str, str] = branch["_condition_history"]
                retired: set[str] = branch["_retired_condition_ids"]
                for condition_id, condition in new.items():
                    if condition_id in retired:
                        _fail(
                            f"{path}.payload.value",
                            f"retired condition_id cannot be reused: {condition_id}",
                        )
                    historical = history.get(condition_id)
                    if historical is not None and historical != condition["statement"]:
                        _fail(
                            f"{path}.payload.value",
                            f"condition_id {condition_id!r} cannot be rebound to new text",
                        )
                    history.setdefault(condition_id, condition["statement"])
                retired.update(set(old) - set(new))
            branch[field] = replacement
        elif kind == "branch_parked":
            branch = _require_branch(branches, branch_id, f"{path}.branch_id")
            if branch["status"] not in {"active", "reopened"}:
                _fail(path, "branch_parked requires active or reopened status")
            branch["status"] = "parked"
            branch["disposition_reason"] = payload["reason"]
        elif kind == "branch_rejected":
            branch = _require_branch(branches, branch_id, f"{path}.branch_id")
            if branch["status"] not in {"active", "reopened", "parked"}:
                _fail(path, "branch_rejected requires active, reopened, or parked status")
            branch["status"] = "rejected"
            branch["disposition_reason"] = payload["reason"]
        elif kind == "branch_reopened":
            branch = _require_branch(branches, branch_id, f"{path}.branch_id")
            if branch["status"] not in {"parked", "rejected"}:
                _fail(path, "branch_reopened requires parked or rejected status")
            if branch["provenance"] not in {"author_originated", "author_adopted"}:
                _fail(path, "an unadopted AI facet cannot be reopened")
            condition_id = payload.get("condition_id")
            if condition_id is not None and condition_id not in _condition_map(branch):
                _fail(
                    f"{path}.payload.condition_id",
                    "must name a currently stored reopen condition",
                )
            branch["status"] = "reopened"
            branch["disposition_reason"] = payload["reason"]
            expected_stale = [
                (artifact_ref, event["event_id"])
                for artifact_ref in branch["downstream_refs"]
            ]
        elif kind == "branch_merged":
            branch = _require_branch(branches, branch_id, f"{path}.branch_id")
            if branch["status"] not in {"active", "reopened"}:
                _fail(path, "branch_merged requires active or reopened source status")
            target_id = payload["merged_into"]
            if target_id == branch_id:
                _fail(f"{path}.payload.merged_into", "a branch cannot merge into itself")
            target = _require_branch(branches, target_id, f"{path}.payload.merged_into")
            if target["status"] not in LIVE_STATUSES:
                _fail(f"{path}.payload.merged_into", "must name a currently-live branch")
            target["downstream_refs"] = _dedupe_ordered(
                [*target["downstream_refs"], *branch["downstream_refs"]]
            )
            branch["status"] = "merged"
            branch["disposition_reason"] = payload["reason"]
            branch["merged_into"] = target_id
        elif kind == "branch_archived":
            branch = _require_branch(branches, branch_id, f"{path}.branch_id")
            if _is_terminal(branch):
                _fail(path, "branch_archived requires a non-terminal branch")
            branch["status"] = "archived"
            branch["disposition_reason"] = payload["reason"]
        elif kind == "reopen_condition_signal":
            branch = _require_branch(branches, branch_id, f"{path}.branch_id")
            if _is_terminal(branch):
                _fail(path, "a terminal branch cannot receive a new reopen signal")
            conditions = _condition_map(branch)
            condition = conditions.get(payload["condition_id"])
            if condition is None:
                _fail(
                    f"{path}.payload.condition_id",
                    "must name a currently stored reopen condition",
                )
            signals.append(
                {
                    "event_id": event["event_id"],
                    "branch_id": branch_id,
                    "condition_id": payload["condition_id"],
                    "condition_statement": condition["statement"],
                    "evidence_pointer": payload["evidence_pointer"],
                }
            )
        elif kind == "profile_rebound":
            rebound = _validate_binding(
                {key: payload[key] for key in _BINDING_FIELDS},
                f"{path}.payload",
            )
            if rebound == effective_binding:
                _fail(path, "profile_rebound must change the effective profile binding")
            replacement = _resolve_profile(rebound, catalog, f"{path}.payload")
            live_count = sum(
                branch["status"] in LIVE_STATUSES for branch in branches.values()
            )
            if live_count > replacement["branch_budget"]:
                _fail(
                    path,
                    "profile_rebound would exceed the replacement profile's "
                    "branch_budget; dispose live branches first",
                )
            effective_binding = copy.deepcopy(rebound)
            current_profile = replacement
        elif kind in {"artifact_reconfirmed", "artifact_superseded"}:
            cause_id = payload["resolves_stale_event_id"]
            cause = stale_causes.get(cause_id)
            if cause is None:
                _fail(
                    f"{path}.payload.resolves_stale_event_id",
                    "does not name an earlier artifact_marked_stale event",
                )
            if cause["artifact_ref"] != payload["artifact_ref"]:
                _fail(
                    f"{path}.payload.artifact_ref",
                    "does not match the named stale cause's artifact_ref",
                )
            artifact = artifacts[payload["artifact_ref"]]
            if cause_id not in artifact["outstanding_stale_causes"]:
                _fail(path, "the named stale cause has already been resolved")
            artifact["outstanding_stale_causes"].remove(cause_id)
            resolution = {
                "event_id": event["event_id"],
                "kind": kind,
                "resolves_stale_event_id": cause_id,
                "note": payload["note"],
            }
            if kind == "artifact_superseded":
                old_ref = payload["artifact_ref"]
                replacement_ref = payload["replaced_by"]
                prior_target = supersession_targets.get(old_ref)
                if prior_target is not None and prior_target != replacement_ref:
                    _fail(
                        f"{path}.payload.replaced_by",
                        f"must equal prior replacement {prior_target!r} for {old_ref!r}",
                    )
                supersession_targets[old_ref] = replacement_ref
                resolution["replaced_by"] = replacement_ref
                for branch in branches.values():
                    if old_ref in branch["downstream_refs"]:
                        branch["downstream_refs"] = _dedupe_ordered(
                            replacement_ref if item == old_ref else item
                            for item in branch["downstream_refs"]
                        )
            artifact["resolution_history"].append(resolution)
        else:  # pragma: no cover - shape validation closes the enum
            _fail(path, f"unhandled event kind: {kind}")

        live_count = sum(
            branch["status"] in LIVE_STATUSES for branch in branches.values()
        )
        if live_count > current_profile["branch_budget"]:
            _fail(
                path,
                f"post-event live branch count {live_count} exceeds effective "
                f"branch_budget {current_profile['branch_budget']}",
            )

    if expected_stale:
        artifact_ref, reopening_id = expected_stale[0]
        _fail(
            "ledger.events",
            "ends before the required artifact_marked_stale event "
            f"for {artifact_ref!r} after reopening event {reopening_id}",
        )
    if require_materialized and introduced_count < 2:
        _fail(
            "ledger.events",
            "persisted ledger publication requires at least two introduced branches",
        )

    public_artifacts: list[dict[str, Any]] = []
    for artifact in artifacts.values():
        public_artifacts.append(
            {
                "artifact_ref": artifact["artifact_ref"],
                "stale": bool(artifact["outstanding_stale_causes"]),
                "outstanding_stale_causes": copy.deepcopy(
                    artifact["outstanding_stale_causes"]
                ),
                "resolution_history": copy.deepcopy(artifact["resolution_history"]),
            }
        )
    live_count = sum(
        branch["status"] in LIVE_STATUSES for branch in branches.values()
    )
    head = ZERO_SHA256 if not events else hashlib.sha256(
        canonical_bytes(events[-1])
    ).hexdigest()
    return {
        "project_ref": ledger["project_ref"],
        "effective_profile_binding": copy.deepcopy(effective_binding),
        "branch_budget": current_profile["branch_budget"],
        "live_count": live_count,
        "introduced_branch_count": introduced_count,
        "branches": [_public_branch(branch) for branch in branches.values()],
        "artifacts": public_artifacts,
        "reopen_condition_signals": copy.deepcopy(signals),
        "event_count": len(events),
        "head_event_sha256": head,
    }


def new_ledger(
    project_ref: str, initial_profile: Mapping[str, Any]
) -> dict[str, Any]:
    """Create an in-memory empty ledger; publication waits for branch two."""

    _text(project_ref, "project_ref")
    try:
        validate_profile(initial_profile)
        binding = profile_binding(initial_profile)
    except ProfileContractError as exc:
        raise ContractError(f"initial_profile: {exc}") from exc
    return {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "project_ref": project_ref,
        "initial_profile_binding": binding,
        "events": [],
    }


def _complete_event(
    events: list[Mapping[str, Any]], event_input: Mapping[str, Any]
) -> dict[str, Any]:
    _object(event_input, "event", _EVENT_INPUT_FIELDS)
    completed = copy.deepcopy(dict(event_input))
    completed["event_id"] = len(events) + 1
    completed["prev_event_sha256"] = (
        ZERO_SHA256
        if not events
        else hashlib.sha256(canonical_bytes(events[-1])).hexdigest()
    )
    # Put fields into one stable human-readable order. Canonical serialization
    # itself sorts keys, but stable insertion order keeps replay output tidy.
    result = {
        "event_id": completed["event_id"],
        "recorded_at": completed["recorded_at"],
        "actor": completed["actor"],
        "kind": completed["kind"],
        "branch_id": completed["branch_id"],
        "payload": completed["payload"],
        "prev_event_sha256": completed["prev_event_sha256"],
    }
    _validate_event_shape(result, "event")
    return result


def append_event(
    ledger: Mapping[str, Any],
    event: Mapping[str, Any],
    profiles: Iterable[Mapping[str, Any]] | Mapping[Any, Mapping[str, Any]],
    *,
    expected_project_ref: str | None = None,
) -> dict[str, Any]:
    """Append one author/AI event and mechanically append reopen stale marks.

    ``event`` is the five-field pre-chain shape: recorded_at, actor, kind,
    branch_id, payload.  Direct system stale-mark appends are refused because
    those events are emitted only as part of a branch_reopened operation.
    """

    _object(event, "event", _EVENT_INPUT_FIELDS)
    catalog = build_profile_catalog(profiles)
    before = replay_ledger(
        ledger, catalog, expected_project_ref=expected_project_ref
    )
    if event.get("kind") == "artifact_marked_stale":
        _fail("event.kind", "artifact_marked_stale is emitted mechanically")
    updated = copy.deepcopy(dict(ledger))
    updated["events"] = copy.deepcopy(list(ledger["events"]))
    completed = _complete_event(updated["events"], event)
    updated["events"].append(completed)

    if completed["kind"] == "branch_reopened":
        branch = next(
            (
                item
                for item in before["branches"]
                if item["branch_id"] == completed["branch_id"]
            ),
            None,
        )
        if branch is None:
            # Final replay would fail too; this gives a local, comprehensible
            # error before trying to derive system events from unknown state.
            _fail("event.branch_id", "unknown branch_id")
        for artifact_ref in branch["downstream_refs"]:
            stale_input = {
                "recorded_at": completed["recorded_at"],
                "actor": "system",
                "kind": "artifact_marked_stale",
                "branch_id": None,
                "payload": {
                    "artifact_ref": artifact_ref,
                    "reopening_event_id": completed["event_id"],
                },
            }
            stale_event = _complete_event(updated["events"], stale_input)
            updated["events"].append(stale_event)

    replay_ledger(updated, catalog, expected_project_ref=expected_project_ref)
    return updated


def inquiry_ledger_enabled(env: Mapping[str, str] | None = None) -> bool:
    """The alpha is enabled only by the exact value ``ARS_INQUIRY_LEDGER=1``."""

    source = os.environ if env is None else env
    return source.get(ENV_FLAG) == "1"


def _summary_text(value: Any, path: str) -> str:
    """Return one bounded line of inert Markdown-safe display text."""

    text = _text(value, path)
    collapsed = " ".join(text.split())
    escaped: list[str] = []
    escaped_length = 0
    for character in collapsed:
        if unicodedata.category(character).startswith("C"):
            width = 4 if ord(character) <= 0xFFFF else 8
            token = f"\\{'u' if width == 4 else 'U'}{ord(character):0{width}x}"
        elif character in _MARKDOWN_META:
            token = "\\" + character
        else:
            token = character
        if escaped_length + len(token) > _SUMMARY_TEXT_LIMIT:
            while escaped and escaped_length >= _SUMMARY_TEXT_LIMIT:
                escaped_length -= len(escaped.pop())
            return "".join(escaped).rstrip() + "…"
        escaped.append(token)
        escaped_length += len(token)
    return "".join(escaped)


def render_summary(
    projection: Mapping[str, Any], *, signal_event_id: int | None = None
) -> str:
    """Render the compact, provenance-labelled branch summary."""

    branches = projection.get("branches")
    if not isinstance(branches, list):
        _fail("projection.branches", "must be an array")
    live_count = _nonnegative_int(projection.get("live_count"), "projection.live_count")
    branch_budget = _positive_int(
        projection.get("branch_budget"), "projection.branch_budget"
    )
    branch_by_id: dict[str, Mapping[str, Any]] = {}
    for index, branch in enumerate(branches):
        if not isinstance(branch, Mapping):
            _fail(f"projection.branches[{index}]", "must be an object")
        branch_id = _slug(
            branch.get("branch_id"), f"projection.branches[{index}].branch_id"
        )
        if branch_id in branch_by_id:
            _fail("projection.branches", f"duplicate branch_id: {branch_id}")
        branch_by_id[branch_id] = branch

    lines = [f"Inquiry branches (live {live_count}/{branch_budget}):"]
    if signal_event_id is not None:
        _positive_int(signal_event_id, "signal_event_id")
        signals = projection.get("reopen_condition_signals")
        if not isinstance(signals, list):
            _fail("projection.reopen_condition_signals", "must be an array")
        signal = None
        for index, item in enumerate(signals):
            signal_path = f"projection.reopen_condition_signals[{index}]"
            value = _object(
                item,
                signal_path,
                {
                    "event_id",
                    "branch_id",
                    "condition_id",
                    "condition_statement",
                    "evidence_pointer",
                },
            )
            _positive_int(value["event_id"], f"{signal_path}.event_id")
            if value["event_id"] == signal_event_id:
                if signal is not None:
                    _fail("signal_event_id", "matches more than one replayed signal")
                signal = value
        if signal is None:
            _fail("signal_event_id", "does not name a replayed reopen-condition signal")

        signal_branch_id = _slug(signal["branch_id"], "signal.branch_id")
        signal_branch = branch_by_id.get(signal_branch_id)
        if signal_branch is None:
            _fail("signal_event_id", "names a branch absent from the current projection")
        status = _enum(signal_branch.get("status"), "signal.branch.status", BRANCH_STATUSES)
        provenance = _enum(
            signal_branch.get("provenance"),
            "signal.branch.provenance",
            PROVENANCE_VALUES,
        )
        if (
            status not in AUTHOR_REOPENABLE_STATUSES
            or provenance not in AUTHOR_OWNED_PROVENANCE
        ):
            _fail(
                "signal_event_id",
                "branch is not currently eligible for an author-owned reopen",
            )
        conditions = _validate_conditions(
            signal_branch.get("reopen_conditions"),
            "signal.branch.reopen_conditions",
        )
        condition_id = _text(signal["condition_id"], "signal.condition_id")
        current_condition = next(
            (item for item in conditions if item["condition_id"] == condition_id),
            None,
        )
        if current_condition is None:
            _fail("signal_event_id", "condition_id is no longer current on the branch")
        historical_statement = _text(
            signal["condition_statement"], "signal.condition_statement"
        )
        if historical_statement != current_condition["statement"]:
            _fail(
                "signal_event_id",
                "historical condition text does not equal the current condition text",
            )
        lines.append(
            f"- {signal_branch_id} [{status}; {provenance}] — "
            "AUTHOR JUDGMENT REQUIRED: "
            f"{_summary_text(condition_id, 'signal.condition_id')} — "
            f"{_summary_text(current_condition['statement'], 'signal.condition_statement')} "
            f"(evidence: {_summary_text(signal['evidence_pointer'], 'signal.evidence_pointer')})"
        )

    live = [branch for branch in branches if branch.get("status") in LIVE_STATUSES]
    if not live:
        lines.append("- No live branches.")
    for branch in live:
        statement = branch.get("statement") or branch.get("surfaced_text") or "(unstated)"
        branch_id = _slug(branch["branch_id"], "branch.branch_id")
        status = _enum(branch["status"], "branch.status", ("active", "reopened"))
        provenance = _enum(
            branch["provenance"], "branch.provenance", PROVENANCE_VALUES
        )
        lines.append(
            f"- {branch_id} [{status}; {provenance}]: "
            f"{_summary_text(statement, 'branch.statement')}"
        )
    artifacts = projection.get("artifacts", [])
    if not isinstance(artifacts, list):
        _fail("projection.artifacts", "must be an array")
    stale_items: list[tuple[str, list[int]]] = []
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, Mapping):
            _fail(f"projection.artifacts[{index}]", "must be an object")
        if not artifact.get("stale"):
            continue
        cause_ids = artifact.get("outstanding_stale_causes")
        if not isinstance(cause_ids, list):
            _fail(
                f"projection.artifacts[{index}].outstanding_stale_causes",
                "must be an array",
            )
        for cause_index, cause_id in enumerate(cause_ids):
            _positive_int(
                cause_id,
                f"projection.artifacts[{index}].outstanding_stale_causes[{cause_index}]",
            )
        if not cause_ids:
            _fail(
                f"projection.artifacts[{index}].outstanding_stale_causes",
                "a stale artifact must retain at least one outstanding cause",
            )
        stale_items.append(
            (
                _summary_text(
                    artifact.get("artifact_ref"),
                    f"projection.artifacts[{index}].artifact_ref",
                ),
                cause_ids,
            )
        )
    if stale_items:
        lines.append(f"- Stale artifacts ({len(stale_items)}):")
        for artifact_ref, cause_ids in stale_items:
            lines.append(f"  - {artifact_ref} [outstanding={len(cause_ids)}]")
            lines.extend(f"    - cause_event_id={cause_id}" for cause_id in cause_ids)
    parked = sum(branch.get("status") == "parked" for branch in branches)
    rejected = sum(branch.get("status") == "rejected" for branch in branches)
    if parked or rejected:
        lines.append(f"- Other dispositions: parked={parked}; rejected={rejected}.")
    lines.append("Controls: skip | off | reset-to-simple-path (ledger is preserved).")
    return "\n".join(lines)


def checkpoint_summary(
    projection: Mapping[str, Any],
    *,
    moment: str,
    env: Mapping[str, str] | None = None,
    signal_event_id: int | None = None,
) -> str | None:
    """Return a summary only at the frozen moments and only when opt-in is on."""

    _enum(moment, "moment", SUMMARY_MOMENTS)
    if not inquiry_ledger_enabled(env):
        return None
    if int(projection.get("introduced_branch_count", 0)) <= 1:
        return None
    if moment == "reopen_condition_signal":
        if signal_event_id is None:
            _fail("signal_event_id", "is required at reopen_condition_signal moment")
    elif signal_event_id is not None:
        _fail("signal_event_id", "is lawful only at reopen_condition_signal moment")
    return render_summary(projection, signal_event_id=signal_event_id)


def validate_pointer(pointer: Mapping[str, Any]) -> dict[str, str]:
    value = _object(pointer, "inquiry_ledger_ref", _POINTER_FIELDS)
    ledger_path = _workspace_relative_path(
        value["ledger_path"], "inquiry_ledger_ref.ledger_path"
    )
    if value["ledger_version"] != POINTER_LEDGER_VERSION:
        _fail(
            "inquiry_ledger_ref.ledger_version",
            f"must equal {POINTER_LEDGER_VERSION}",
        )
    return {
        "ledger_path": ledger_path,
        "ledger_version": POINTER_LEDGER_VERSION,
        "content_sha256": _sha256(
            value["content_sha256"], "inquiry_ledger_ref.content_sha256"
        ),
    }


def _workspace_relative_path(value: Any, path: str) -> str:
    text = _text(value, path)
    if "\\" in text or _FORBIDDEN_PATH_CHARS_RE.search(text):
        _fail(path, "must be a normalized relative POSIX path without unsafe characters")
    pure = PurePosixPath(text)
    if pure.is_absolute() or text.startswith("/"):
        _fail(path, "must be workspace-relative")
    if any(part in {"", ".", ".."} for part in pure.parts):
        _fail(path, "must not contain empty, '.' or '..' path segments")
    normalized = pure.as_posix()
    if normalized != text or "//" in text or text.endswith("/"):
        _fail(path, "must be a normalized relative POSIX path")
    # PurePosixPath treats ``C:/x`` as relative; it is absolute on Windows and
    # remains forbidden even though durable publication is POSIX-only.
    if re.match(r"^[A-Za-z]:", text):
        _fail(path, "must not be a platform-absolute path")
    return text


def _workspace_root(path: Path | str) -> Path:
    root = Path(path)
    if not root.is_absolute():
        _fail("workspace_root", "must be an explicit absolute path")
    try:
        resolved = root.resolve(strict=True)
    except OSError as exc:
        raise ContractError(f"workspace_root is not readable: {root}: {exc}") from exc
    if not resolved.is_dir():
        _fail("workspace_root", "must be a directory")
    return resolved


def _authoritative_passport_path(
    path: Path | str, root: Path
) -> tuple[str, Path]:
    """Resolve a passport without erasing evidence of a symlinked parent."""

    raw = Path(path)
    if raw.is_absolute():
        try:
            relative = raw.relative_to(root).as_posix()
        except ValueError:
            _fail("passport_path", "is outside workspace_root")
    else:
        relative = raw.as_posix()
    normalized = _workspace_relative_path(relative, "passport_path")
    passport = root.joinpath(*PurePosixPath(normalized).parts)
    try:
        resolved_parent = passport.parent.resolve(strict=True)
    except OSError as exc:
        raise ContractError(
            f"passport_path: parent directory is not readable: {exc}"
        ) from exc
    if resolved_parent != passport.parent:
        _fail(
            "passport_path",
            "parent directory must not resolve through a symlink",
        )
    _require_regular_nonsymlink(passport, "passport_path")
    return normalized, passport


def _contained_path(root: Path, relative: str, path: str) -> Path:
    normalized = _workspace_relative_path(relative, path)
    candidate = root.joinpath(*PurePosixPath(normalized).parts)
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError:
        _fail(path, "resolves outside workspace_root")
    return candidate


def _relative_to_workspace(path: Path | str, root: Path, field: str) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        try:
            # Preserve the caller's lexical target. Resolving here would erase
            # a final-component or parent symlink before the non-symlink and
            # beside-passport checks have a chance to reject it.
            relative = candidate.relative_to(root).as_posix()
        except ValueError:
            _fail(field, "is outside workspace_root")
    else:
        relative = candidate.as_posix()
    return _workspace_relative_path(relative, field)


def default_ledger_relative_path(
    passport_path: Path | str, workspace_root: Path | str
) -> str:
    """Return the deterministic beside-passport orphan-discovery candidate."""

    root = _workspace_root(workspace_root)
    passport_relative = _relative_to_workspace(passport_path, root, "passport_path")
    passport = PurePosixPath(passport_relative)
    filename = f"{passport.stem}.inquiry-branch-ledger.json"
    return (passport.parent / filename).as_posix()


def _require_regular_nonsymlink(path: Path, field: str, *, may_absent: bool = False) -> None:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        if may_absent:
            return
        _fail(field, f"file does not exist: {path}")
    except OSError as exc:
        raise ContractError(f"{field}: cannot inspect {path}: {exc}") from exc
    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
        _fail(field, "must be a regular non-symlink file")


def _yaml_runtime():
    try:
        from ruamel.yaml import YAML
    except ImportError as exc:  # pragma: no cover - dependency is CI-pinned
        raise ContractError("ruamel.yaml is required for passport transactions") from exc
    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True
    yaml.allow_duplicate_keys = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    return yaml


def _parse_passport_bytes(path: Path, raw: bytes) -> Any:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractError(f"passport YAML is not UTF-8: {path}") from exc
    yaml = _yaml_runtime()
    try:
        document = yaml.load(text)
    except Exception as exc:
        raise ContractError(f"cannot parse passport YAML {path}: {exc}") from exc
    if not isinstance(document, Mapping):
        _fail("passport", "top-level YAML value must be an object")
    return document


def _load_passport_snapshot(path: Path) -> tuple[bytes, Any]:
    _require_regular_nonsymlink(path, "passport_path")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ContractError(f"cannot read passport YAML {path}: {exc}") from exc
    return raw, _parse_passport_bytes(path, raw)


def _load_passport_doc(path: Path) -> Any:
    return _load_passport_snapshot(path)[1]


def _passport_bytes(document: Any) -> bytes:
    yaml = _yaml_runtime()
    stream = io.StringIO()
    try:
        yaml.dump(document, stream)
        return stream.getvalue().encode("utf-8")
    except Exception as exc:
        raise ContractError(f"cannot serialize passport YAML: {exc}") from exc


def _passport_pointer(document: Mapping[str, Any]) -> dict[str, str] | None:
    if "inquiry_ledger_ref" not in document:
        return None
    raw = document["inquiry_ledger_ref"]
    if raw is None:
        raise LedgerBindingError(
            "inquiry_ledger_ref is present but null; omit the field for no ledger"
        )
    try:
        return validate_pointer(raw)
    except ContractError as exc:
        raise LedgerBindingError(f"invalid inquiry_ledger_ref: {exc}") from exc


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    fd = os.open(path, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write_exclusive_durable(path: Path, data: bytes, *, mode: int = 0o600) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(path, flags, mode)
    try:
        offset = 0
        while offset < len(data):
            written = os.write(fd, data[offset:])
            if written <= 0:  # pragma: no cover - defensive kernel/I/O guard
                raise OSError(f"short write while staging transaction file: {path}")
            offset += written
        os.fsync(fd)
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise
    finally:
        os.close(fd)


def _sidecars(passport: Path) -> dict[str, Path]:
    feature_base = f".{passport.name}.inquiry-ledger"
    return {
        # The lock is deliberately feature-neutral: every passport writer,
        # including future companion transactions, shares this domain.
        "lock": passport.parent / f".{passport.name}.lock",
        "journal": passport.parent / f"{feature_base}.transaction.json",
        "journal_temp": passport.parent / f"{feature_base}.transaction.tmp",
        "passport_temp": passport.parent / f"{feature_base}.passport.tmp",
        "ledger_temp": passport.parent / f"{feature_base}.ledger.tmp",
        # Reserved now so a pre-#744 ledger can never occupy the companion
        # register transaction's deterministic staged pathname.
        "register_temp": passport.parent / f"{feature_base}.register.tmp",
    }


def _ledger_temp(ledger: Path, passport: Path) -> Path:
    if ledger.parent != passport.parent:
        _fail("ledger_path", "must be in the same directory as the Material Passport")
    return _sidecars(passport)["ledger_temp"]


def _assert_safe_ledger_target(passport: Path, ledger: Path) -> None:
    def name_key(path: Path) -> str:
        # APFS and HFS+ commonly compare names case-insensitively and with
        # canonical-equivalence folding. Reject those aliases conservatively
        # even when the current test filesystem happens to be case-sensitive.
        return unicodedata.normalize("NFD", path.name).casefold()

    ledger_key = name_key(ledger)
    if ledger == passport or ledger_key == name_key(passport):
        _fail("ledger_path", "must not equal passport_path")
    if ledger.parent != passport.parent:
        _fail("ledger_path", "must be beside the Material Passport")
    collisions = [
        name
        for name, path in _sidecars(passport).items()
        if ledger == path or ledger_key == name_key(path)
    ]
    if collisions:
        _fail(
            "ledger_path",
            "collides with reserved passport transaction path(s): "
            + ", ".join(sorted(collisions)),
        )


@contextmanager
def _transaction_lock(passport: Path, *, timeout_seconds: float = 30.0) -> Iterator[None]:
    if fcntl is None:
        raise ContractError(
            "concurrency protection unavailable on this platform; refusing ledger access"
        )
    if isinstance(timeout_seconds, bool) or not isinstance(
        timeout_seconds, (int, float)
    ):
        _fail("lock_timeout", "must be a finite number between 0 and 60 seconds")
    try:
        normalized_timeout = float(timeout_seconds)
    except (OverflowError, ValueError):
        _fail("lock_timeout", "must be a finite number between 0 and 60 seconds")
    if not math.isfinite(normalized_timeout) or not 0 <= normalized_timeout <= 60:
        _fail("lock_timeout", "must be a finite number between 0 and 60 seconds")
    lock_path = _sidecars(passport)["lock"]
    if lock_path.exists() or lock_path.is_symlink():
        _require_regular_nonsymlink(lock_path, "transaction_lock")
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(lock_path, flags, 0o600)
    deadline = time.monotonic() + normalized_timeout
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ContractError(f"transaction_lock: must be a regular file: {lock_path}")
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise ContractError(
                        f"passport locked by another session: {passport}"
                    )
                time.sleep(0.05)
        yield
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def _plain_pointer(pointer: Mapping[str, Any] | None) -> dict[str, str] | None:
    if pointer is None:
        return None
    return {key: str(pointer[key]) for key in sorted(_POINTER_FIELDS)}


def _journal_shape(value: Mapping[str, Any]) -> Mapping[str, Any]:
    fields = {
        "schema_version",
        "transaction_id",
        "passport_path",
        "ledger_path",
        "passport_temp_path",
        "ledger_temp_path",
        "old_pointer",
        "new_pointer",
        "old_ledger_sha256",
        "new_ledger_sha256",
        "old_passport_sha256",
        "new_passport_sha256",
    }
    journal = _object(value, "transaction", fields)
    if journal["schema_version"] != TRANSACTION_SCHEMA_VERSION:
        _fail("transaction.schema_version", f"must equal {TRANSACTION_SCHEMA_VERSION}")
    _text(journal["transaction_id"], "transaction.transaction_id")
    for field in (
        "passport_path",
        "ledger_path",
        "passport_temp_path",
        "ledger_temp_path",
    ):
        _workspace_relative_path(journal[field], f"transaction.{field}")
    old_pointer = (
        None
        if journal["old_pointer"] is None
        else validate_pointer(journal["old_pointer"])
    )
    new_pointer = validate_pointer(journal["new_pointer"])
    if journal["old_ledger_sha256"] is not None:
        _sha256(journal["old_ledger_sha256"], "transaction.old_ledger_sha256")
    _sha256(journal["new_ledger_sha256"], "transaction.new_ledger_sha256")
    _sha256(journal["old_passport_sha256"], "transaction.old_passport_sha256")
    _sha256(journal["new_passport_sha256"], "transaction.new_passport_sha256")
    if new_pointer["ledger_path"] != journal["ledger_path"]:
        _fail("transaction.new_pointer", "ledger_path does not equal transaction ledger_path")
    if new_pointer["content_sha256"] != journal["new_ledger_sha256"]:
        _fail("transaction.new_pointer", "digest does not equal new_ledger_sha256")
    if old_pointer is None:
        if journal["old_ledger_sha256"] is not None:
            _fail(
                "transaction.old_ledger_sha256",
                "must be null when old_pointer is null",
            )
    else:
        if old_pointer["ledger_path"] != journal["ledger_path"]:
            _fail(
                "transaction.old_pointer",
                "ledger_path does not equal transaction ledger_path",
            )
        if journal["old_ledger_sha256"] != old_pointer["content_sha256"]:
            _fail(
                "transaction.old_ledger_sha256",
                "must equal old_pointer.content_sha256",
            )
    return journal


def _path_digest(path: Path, *, field: str = "transaction_target") -> str | None:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise TransactionRecoveryError(
            f"cannot inspect {field} {path}: {exc}"
        ) from exc
    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
        raise TransactionRecoveryError(
            f"{field} must be a regular non-symlink file: {path}"
        )
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise TransactionRecoveryError(f"cannot read {field} {path}: {exc}") from exc
    return hashlib.sha256(raw).hexdigest()


def _cleanup_unjournaled_temps(passport: Path, ledger: Path | None = None) -> None:
    paths = [_sidecars(passport)["journal_temp"], _sidecars(passport)["passport_temp"]]
    if ledger is not None:
        paths.append(_ledger_temp(ledger, passport))
    for path in paths:
        if not path.exists() and not path.is_symlink():
            continue
        _require_regular_nonsymlink(path, "transaction_temp")
        try:
            path.unlink()
        except OSError as exc:
            raise TransactionRecoveryError(f"cannot clear unjournaled temp {path}: {exc}") from exc
        _fsync_directory(path.parent)


def _write_journal(path: Path, temp: Path, journal: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise TransactionRecoveryError(f"existing transaction journal: {path}")
    if temp.exists() or temp.is_symlink():
        raise TransactionRecoveryError(f"stale transaction journal temp: {temp}")
    journal_bytes = canonical_bytes(journal)
    _write_exclusive_durable(temp, journal_bytes)
    _require_regular_nonsymlink(temp, "transaction_journal_temp")
    try:
        if temp.read_bytes() != journal_bytes:
            raise TransactionRecoveryError(
                "transaction journal temp changed before publication"
            )
    except OSError as exc:
        raise TransactionRecoveryError(
            f"cannot verify transaction journal temp {temp}: {exc}"
        ) from exc
    if path.exists() or path.is_symlink():
        raise TransactionRecoveryError(f"transaction journal appeared concurrently: {path}")
    os.replace(temp, path)
    _fsync_directory(path.parent)


def _recovery_passport_snapshot(
    path: Path, field: str
) -> tuple[bytes, Mapping[str, Any]]:
    try:
        raw, document = _load_passport_snapshot(path)
    except ContractError as exc:
        raise TransactionRecoveryError(f"invalid {field} {path}: {exc}") from exc
    return raw, document


def _recovery_passport_pointer(
    document: Mapping[str, Any], field: str
) -> dict[str, str] | None:
    try:
        return _passport_pointer(document)
    except ContractError as exc:
        raise TransactionRecoveryError(f"invalid {field} pointer: {exc}") from exc


def _recover_transaction_locked(passport: Path, root: Path) -> bool:
    sidecars = _sidecars(passport)
    journal_path = sidecars["journal"]
    if not journal_path.exists():
        if journal_path.is_symlink():
            raise TransactionRecoveryError("journal path is a symlink")
        return False
    try:
        _require_regular_nonsymlink(journal_path, "transaction_journal")
    except ContractError as exc:
        raise TransactionRecoveryError(f"invalid journal {journal_path}: {exc}") from exc
    try:
        raw = journal_path.read_bytes()
        value = _parse_json_bytes(raw, source=str(journal_path))
        if raw != canonical_bytes(value):
            raise ContractError("journal is not exact canonical JSON")
        journal = _journal_shape(value)
    except (OSError, ContractError) as exc:
        raise TransactionRecoveryError(f"invalid journal {journal_path}: {exc}") from exc

    expected_passport_rel = _relative_to_workspace(passport, root, "passport_path")
    if journal["passport_path"] != expected_passport_rel:
        raise TransactionRecoveryError("journal passport_path does not match lock owner")
    ledger = _contained_path(root, journal["ledger_path"], "transaction.ledger_path")
    passport_temp = _contained_path(
        root, journal["passport_temp_path"], "transaction.passport_temp_path"
    )
    ledger_temp = _contained_path(
        root, journal["ledger_temp_path"], "transaction.ledger_temp_path"
    )
    try:
        _assert_safe_ledger_target(passport, ledger)
    except ContractError as exc:
        raise TransactionRecoveryError(f"invalid journal ledger target: {exc}") from exc
    expected_passport_temp = sidecars["passport_temp"]
    expected_ledger_temp = _ledger_temp(ledger, passport)
    if passport_temp != expected_passport_temp:
        raise TransactionRecoveryError(
            "journal passport_temp_path is not the deterministic reserved path"
        )
    if ledger_temp != expected_ledger_temp:
        raise TransactionRecoveryError(
            "journal ledger_temp_path is not the deterministic reserved path"
        )

    new_digest = journal["new_ledger_sha256"]
    old_digest = journal["old_ledger_sha256"]
    ledger_digest = _path_digest(ledger, field="ledger target")
    ledger_temp_present = ledger_temp.exists() or ledger_temp.is_symlink()
    if ledger_temp_present:
        temp_digest = _path_digest(ledger_temp, field="staged ledger")
        if temp_digest != new_digest:
            raise TransactionRecoveryError(
                "staged ledger is not the journal's complete new byte image"
            )
    if ledger_digest == new_digest:
        publish_ledger = False
    elif ledger_digest == old_digest:
        if not ledger_temp_present:
            raise TransactionRecoveryError("new ledger temp is absent")
        publish_ledger = True
    else:
        raise TransactionRecoveryError(
            "ledger target is neither the recorded old nor new generation"
        )

    old_pointer = (
        None if journal["old_pointer"] is None else validate_pointer(journal["old_pointer"])
    )
    new_pointer = validate_pointer(journal["new_pointer"])
    old_passport_digest = journal["old_passport_sha256"]
    new_passport_digest = journal["new_passport_sha256"]

    staged_passport_present = passport_temp.exists() or passport_temp.is_symlink()
    if staged_passport_present:
        staged_raw, staged_document = _recovery_passport_snapshot(
            passport_temp, "staged passport"
        )
        if hashlib.sha256(staged_raw).hexdigest() != new_passport_digest:
            raise TransactionRecoveryError(
                "staged passport is not the journal's complete new byte image"
            )
        if _recovery_passport_pointer(staged_document, "staged passport") != new_pointer:
            raise TransactionRecoveryError("staged passport does not carry new pointer")

    live_raw, live_document = _recovery_passport_snapshot(passport, "live passport")
    live_passport_digest = hashlib.sha256(live_raw).hexdigest()
    current_pointer = _recovery_passport_pointer(live_document, "live passport")
    if live_passport_digest == new_passport_digest:
        publish_passport = False
        if current_pointer != new_pointer:
            raise TransactionRecoveryError(
                "new passport byte image does not carry the recorded new pointer"
            )
    elif live_passport_digest == old_passport_digest:
        publish_passport = True
        if current_pointer != old_pointer:
            raise TransactionRecoveryError(
                "old passport byte image does not carry the recorded old pointer"
            )
        if not staged_passport_present:
            raise TransactionRecoveryError("new passport temp is absent")
    else:
        raise TransactionRecoveryError(
            "live passport is neither the recorded old nor new byte generation"
        )

    # All journal relations, sources, and live generations are valid before
    # recovery advances either member of the pair.
    if publish_ledger:
        if _path_digest(ledger, field="ledger target CAS") != old_digest:
            raise TransactionRecoveryError("ledger target changed during recovery")
        if _path_digest(ledger_temp, field="staged ledger CAS") != new_digest:
            raise TransactionRecoveryError("staged ledger changed during recovery")
        os.replace(ledger_temp, ledger)
        _fsync_directory(ledger.parent)
    if publish_passport:
        check_raw, check_document = _recovery_passport_snapshot(
            passport, "live passport CAS"
        )
        if hashlib.sha256(check_raw).hexdigest() != old_passport_digest:
            raise TransactionRecoveryError("live passport changed during recovery")
        if _recovery_passport_pointer(check_document, "live passport CAS") != old_pointer:
            raise TransactionRecoveryError("live passport pointer changed during recovery")
        check_staged_raw, check_staged_document = _recovery_passport_snapshot(
            passport_temp, "staged passport CAS"
        )
        if hashlib.sha256(check_staged_raw).hexdigest() != new_passport_digest:
            raise TransactionRecoveryError("staged passport changed during recovery")
        if (
            _recovery_passport_pointer(
                check_staged_document, "staged passport CAS"
            )
            != new_pointer
        ):
            raise TransactionRecoveryError("staged passport pointer changed during recovery")
        os.replace(passport_temp, passport)
        _fsync_directory(passport.parent)

    final_raw, final_document = _recovery_passport_snapshot(
        passport, "recovered passport"
    )
    if hashlib.sha256(final_raw).hexdigest() != new_passport_digest:
        raise TransactionRecoveryError(
            "recovered passport digest is not the new passport digest"
        )
    if _recovery_passport_pointer(final_document, "recovered passport") != new_pointer:
        raise TransactionRecoveryError("recovered passport pointer is not the new pointer")
    if _path_digest(ledger, field="recovered ledger") != new_digest:
        raise TransactionRecoveryError("recovered ledger digest is not the new digest")

    for temp in (passport_temp, ledger_temp):
        if temp.exists() or temp.is_symlink():
            try:
                _require_regular_nonsymlink(temp, "transaction_temp")
            except ContractError as exc:
                raise TransactionRecoveryError(
                    f"invalid transaction temp during cleanup: {exc}"
                ) from exc
            temp.unlink()
    try:
        _require_regular_nonsymlink(journal_path, "transaction_journal")
    except ContractError as exc:
        raise TransactionRecoveryError(
            f"transaction journal changed during recovery: {exc}"
        ) from exc
    journal_path.unlink()
    _fsync_directory(passport.parent)
    return True


def recover_ledger_transaction(
    passport_path: Path | str,
    workspace_root: Path | str,
    *,
    lock_timeout: float = 30.0,
) -> bool:
    """Recover one interrupted two-file transaction, if a journal exists."""

    root = _workspace_root(workspace_root)
    _, passport = _authoritative_passport_path(passport_path, root)
    with _transaction_lock(passport, timeout_seconds=lock_timeout):
        return _recover_transaction_locked(passport, root)


def _load_bound_locked(
    passport: Path,
    root: Path,
    catalog: Mapping[tuple[str, str, str], Mapping[str, Any]],
    *,
    expected_project_ref: str,
    orphan_relative: str,
) -> dict[str, Any]:
    document = _load_passport_doc(passport)
    pointer = _passport_pointer(document)
    if pointer is None:
        orphan = _contained_path(root, orphan_relative, "orphan_candidate")
        if orphan.exists() or orphan.is_symlink():
            return {
                "state": "orphan_ignored",
                "notice": (
                    "ledger file exists without inquiry_ledger_ref; passport is "
                    "authoritative, so the file is ignored"
                ),
                "ledger": None,
                "projection": None,
                "pointer": None,
                "ledger_path": str(orphan),
            }
        return {
            "state": "absent",
            "notice": None,
            "ledger": None,
            "projection": None,
            "pointer": None,
            "ledger_path": None,
        }

    ledger_path = _contained_path(
        root, pointer["ledger_path"], "inquiry_ledger_ref.ledger_path"
    )
    try:
        _assert_safe_ledger_target(passport, ledger_path)
    except ContractError as exc:
        raise LedgerBindingError(str(exc)) from exc
    try:
        _require_regular_nonsymlink(ledger_path, "ledger_path")
        raw = ledger_path.read_bytes()
        ledger = _parse_json_bytes(raw, source=str(ledger_path))
        if raw != canonical_bytes(ledger):
            raise ContractError("ledger storage is not exact canonical JSON")
        digest = hashlib.sha256(raw).hexdigest()
        if digest != pointer["content_sha256"]:
            raise ContractError(
                f"pointer digest {pointer['content_sha256']} does not match ledger {digest}"
            )
        if ledger.get("schema_version") != pointer["ledger_version"]:
            raise ContractError("pointer ledger_version does not match ledger schema_version")
        projection = replay_ledger(
            ledger,
            catalog,
            expected_project_ref=expected_project_ref,
            require_materialized=True,
        )
    except (OSError, ContractError) as exc:
        if isinstance(exc, LedgerBindingError):
            raise
        raise LedgerBindingError(str(exc)) from exc
    return {
        "state": "bound",
        "notice": None,
        "ledger": ledger,
        "projection": projection,
        "pointer": pointer,
        "ledger_path": str(ledger_path),
    }


def load_bound_ledger(
    passport_path: Path | str,
    workspace_root: Path | str,
    profiles: Iterable[Mapping[str, Any]] | Mapping[Any, Mapping[str, Any]],
    *,
    expected_project_ref: str | None = None,
    orphan_candidate: Path | str | None = None,
    recover: bool = True,
    lock_timeout: float = 30.0,
) -> dict[str, Any]:
    """Load the passport-authoritative ledger binding under the stable lock."""

    root = _workspace_root(workspace_root)
    expected = _text(expected_project_ref, "expected_project_ref")
    _, passport = _authoritative_passport_path(passport_path, root)
    catalog = build_profile_catalog(profiles)
    orphan_relative = (
        default_ledger_relative_path(passport, root)
        if orphan_candidate is None
        else _relative_to_workspace(orphan_candidate, root, "orphan_candidate")
    )
    with _transaction_lock(passport, timeout_seconds=lock_timeout):
        journal = _sidecars(passport)["journal"]
        if journal.exists() or journal.is_symlink():
            if not recover:
                raise TransactionRecoveryError("pending journal; recovery disabled")
            _recover_transaction_locked(passport, root)
        return _load_bound_locked(
            passport,
            root,
            catalog,
            expected_project_ref=expected,
            orphan_relative=orphan_relative,
        )


def _assert_append_only(old: Mapping[str, Any], new: Mapping[str, Any]) -> None:
    for field in ("schema_version", "project_ref", "initial_profile_binding"):
        if new[field] != old[field]:
            _fail(f"ledger.{field}", "is immutable after materialization")
    old_events = old["events"]
    new_events = new["events"]
    if len(new_events) <= len(old_events):
        _fail("ledger.events", "publication must append at least one new event")
    if new_events[: len(old_events)] != old_events:
        _fail("ledger.events", "prior event history was rewritten or reordered")


def commit_ledger_transaction(
    passport_path: Path | str,
    ledger_path: Path | str,
    workspace_root: Path | str,
    ledger: Mapping[str, Any],
    profiles: Iterable[Mapping[str, Any]] | Mapping[Any, Mapping[str, Any]],
    project_ref: str | None = None,
    *,
    lock_timeout: float = 30.0,
    crash_hook: Callable[[str], None] | None = None,
) -> dict[str, str]:
    """Durably publish ledger bytes and their passport pointer as one transaction.

    ``crash_hook`` is a deterministic test seam called after these durable
    boundaries: ``temps_durable``, ``journal_durable``, ``ledger_published``,
    ``passport_published``, and ``journal_cleared``.  Raising at or after
    ``journal_durable`` deliberately leaves recovery state intact.
    """

    root = _workspace_root(workspace_root)
    expected_project_ref = _text(project_ref, "expected_project_ref")
    passport_relative, passport = _authoritative_passport_path(passport_path, root)
    ledger_relative = _relative_to_workspace(ledger_path, root, "ledger_path")
    ledger_target = _contained_path(root, ledger_relative, "ledger_path")
    _assert_safe_ledger_target(passport, ledger_target)
    _require_regular_nonsymlink(ledger_target, "ledger_path", may_absent=True)
    catalog = build_profile_catalog(profiles)
    replay_ledger(
        ledger,
        catalog,
        expected_project_ref=expected_project_ref,
        require_materialized=True,
    )
    ledger_bytes = canonical_bytes(ledger)
    new_digest = hashlib.sha256(ledger_bytes).hexdigest()
    new_pointer = {
        "ledger_path": ledger_relative,
        "ledger_version": POINTER_LEDGER_VERSION,
        "content_sha256": new_digest,
    }
    validate_pointer(new_pointer)

    hook = crash_hook or (lambda _phase: None)
    sidecars = _sidecars(passport)
    ledger_temp = _ledger_temp(ledger_target, passport)
    journal_durable = False
    with _transaction_lock(passport, timeout_seconds=lock_timeout):
        if sidecars["journal"].exists() or sidecars["journal"].is_symlink():
            _recover_transaction_locked(passport, root)
        _cleanup_unjournaled_temps(passport, ledger_target)

        old_passport_raw, document = _load_passport_snapshot(passport)
        old_passport_digest = hashlib.sha256(old_passport_raw).hexdigest()
        old_pointer = _passport_pointer(document)
        old_digest: str | None = None
        if old_pointer is None:
            if ledger_target.exists() or ledger_target.is_symlink():
                raise ContractError(
                    "ledger file exists without a passport pointer; it is an ignored "
                    "orphan and will not be overwritten or silently adopted"
                )
        else:
            if old_pointer["ledger_path"] != ledger_relative:
                _fail(
                    "ledger_path",
                    "must equal the existing passport pointer's stable ledger_path",
                )
            try:
                _require_regular_nonsymlink(ledger_target, "ledger_path")
                old_raw = ledger_target.read_bytes()
                old_ledger = _parse_json_bytes(old_raw, source=str(ledger_target))
                if old_raw != canonical_bytes(old_ledger):
                    raise ContractError("existing ledger is not exact canonical JSON")
                old_digest = hashlib.sha256(old_raw).hexdigest()
                if old_digest != old_pointer["content_sha256"]:
                    raise ContractError("existing pointer digest does not match ledger")
                replay_ledger(
                    old_ledger,
                    catalog,
                    expected_project_ref=expected_project_ref,
                    require_materialized=True,
                )
                _assert_append_only(old_ledger, ledger)
            except (OSError, ContractError) as exc:
                raise LedgerBindingError(str(exc)) from exc

        document["inquiry_ledger_ref"] = copy.deepcopy(new_pointer)
        passport_bytes = _passport_bytes(document)
        new_passport_digest = hashlib.sha256(passport_bytes).hexdigest()
        _write_exclusive_durable(ledger_temp, ledger_bytes)
        try:
            passport_mode = stat.S_IMODE(passport.stat().st_mode)
            _write_exclusive_durable(
                sidecars["passport_temp"], passport_bytes, mode=passport_mode
            )
        except BaseException:
            ledger_temp.unlink(missing_ok=True)
            raise
        hook("temps_durable")

        journal = {
            "schema_version": TRANSACTION_SCHEMA_VERSION,
            "transaction_id": uuid.uuid4().hex,
            "passport_path": passport_relative,
            "ledger_path": ledger_relative,
            "passport_temp_path": _relative_to_workspace(
                sidecars["passport_temp"], root, "passport_temp_path"
            ),
            "ledger_temp_path": _relative_to_workspace(
                ledger_temp, root, "ledger_temp_path"
            ),
            "old_pointer": _plain_pointer(old_pointer),
            "new_pointer": _plain_pointer(new_pointer),
            "old_ledger_sha256": old_digest,
            "new_ledger_sha256": new_digest,
            "old_passport_sha256": old_passport_digest,
            "new_passport_sha256": new_passport_digest,
        }
        _journal_shape(journal)
        try:
            _write_journal(sidecars["journal"], sidecars["journal_temp"], journal)
            journal_durable = True
            hook("journal_durable")

            if _path_digest(ledger_temp, field="staged ledger") != new_digest:
                raise TransactionRecoveryError("staged ledger changed before publication")
            if _path_digest(ledger_target, field="live ledger") != old_digest:
                raise TransactionRecoveryError("live ledger changed before publication")
            preflight_passport_raw, preflight_passport = _recovery_passport_snapshot(
                sidecars["passport_temp"], "staged passport preflight"
            )
            if (
                hashlib.sha256(preflight_passport_raw).hexdigest()
                != new_passport_digest
            ):
                raise TransactionRecoveryError(
                    "staged passport changed before publication"
                )
            if (
                _recovery_passport_pointer(
                    preflight_passport, "staged passport preflight"
                )
                != new_pointer
            ):
                raise TransactionRecoveryError(
                    "staged passport pointer changed before publication"
                )
            preflight_live_raw, preflight_live = _recovery_passport_snapshot(
                passport, "live passport preflight"
            )
            if (
                hashlib.sha256(preflight_live_raw).hexdigest()
                != old_passport_digest
            ):
                raise TransactionRecoveryError("live passport changed before publication")
            if (
                _recovery_passport_pointer(preflight_live, "live passport preflight")
                != old_pointer
            ):
                raise TransactionRecoveryError(
                    "live passport pointer changed before publication"
                )
            os.replace(ledger_temp, ledger_target)
            _fsync_directory(ledger_target.parent)
            hook("ledger_published")

            staged_passport_raw, staged_passport = _recovery_passport_snapshot(
                sidecars["passport_temp"], "staged passport"
            )
            if hashlib.sha256(staged_passport_raw).hexdigest() != new_passport_digest:
                raise TransactionRecoveryError(
                    "staged passport changed before publication"
                )
            if (
                _recovery_passport_pointer(staged_passport, "staged passport")
                != new_pointer
            ):
                raise TransactionRecoveryError(
                    "staged passport pointer changed before publication"
                )
            live_passport_raw, live_passport = _recovery_passport_snapshot(
                passport, "live passport CAS"
            )
            if hashlib.sha256(live_passport_raw).hexdigest() != old_passport_digest:
                raise TransactionRecoveryError("live passport changed before publication")
            if (
                _recovery_passport_pointer(live_passport, "live passport CAS")
                != old_pointer
            ):
                raise TransactionRecoveryError(
                    "live passport pointer changed before publication"
                )
            os.replace(sidecars["passport_temp"], passport)
            _fsync_directory(passport.parent)
            hook("passport_published")

            # Verify the committed pair before deleting its recovery witness.
            committed_raw, committed_document = _recovery_passport_snapshot(
                passport, "committed passport"
            )
            if hashlib.sha256(committed_raw).hexdigest() != new_passport_digest:
                raise TransactionRecoveryError("committed passport digest mismatch")
            if (
                _recovery_passport_pointer(committed_document, "committed passport")
                != new_pointer
            ):
                raise TransactionRecoveryError("committed passport pointer mismatch")
            if _path_digest(ledger_target, field="committed ledger") != new_digest:
                raise TransactionRecoveryError("committed ledger digest mismatch")
            _require_regular_nonsymlink(sidecars["journal"], "transaction_journal")
            sidecars["journal"].unlink()
            _fsync_directory(passport.parent)
            hook("journal_cleared")
        except BaseException:
            # os.replace(journal_temp, journal) may have succeeded before a
            # directory-fsync error was reported.  If the journal name is
            # visible, preserve both staged generations for recovery instead
            # of converting a recoverable transaction into a broken one.
            journal_durable = journal_durable or sidecars["journal"].exists()
            if not journal_durable:
                for temp in (
                    ledger_temp,
                    sidecars["passport_temp"],
                    sidecars["journal_temp"],
                ):
                    try:
                        temp.unlink(missing_ok=True)
                    except OSError:
                        pass
            raise
    return new_pointer


def _emit_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _event_input(path: Path) -> Mapping[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ContractError(f"cannot read event input {path}: {exc}") from exc
    value = _parse_json_bytes(raw, source=str(path))
    _object(value, "event", _EVENT_INPUT_FIELDS)
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_ledger_inputs(
        command_parser: argparse.ArgumentParser, *, authoritative: bool = False
    ) -> None:
        command_parser.add_argument("ledger", type=Path)
        command_parser.add_argument(
            "--profile", action="append", required=True, type=Path
        )
        command_parser.add_argument(
            "--project-ref",
            required=authoritative,
            help=(
                "required project identity for authoritative mutation/display; "
                "optional only for diagnostic validate/replay"
            ),
        )

    validate_parser = subparsers.add_parser("validate")
    add_ledger_inputs(validate_parser)
    validate_parser.add_argument("--allow-in-memory", action="store_true")

    replay_parser = subparsers.add_parser("replay")
    add_ledger_inputs(replay_parser)
    replay_parser.add_argument("--allow-in-memory", action="store_true")

    append_parser = subparsers.add_parser("append")
    add_ledger_inputs(append_parser, authoritative=True)
    append_parser.add_argument("--event", required=True, type=Path)

    summary_parser = subparsers.add_parser("summary")
    add_ledger_inputs(summary_parser, authoritative=True)
    summary_parser.add_argument("--moment", choices=SUMMARY_MOMENTS, required=True)
    summary_parser.add_argument("--signal-event-id", type=int)
    summary_parser.add_argument(
        "--force",
        action="store_true",
        help="render for diagnostics even when ARS_INQUIRY_LEDGER is not 1",
    )

    load_parser = subparsers.add_parser("load-bound")
    load_parser.add_argument("--passport", required=True, type=Path)
    load_parser.add_argument("--workspace-root", required=True, type=Path)
    load_parser.add_argument("--profile", action="append", required=True, type=Path)
    load_parser.add_argument("--project-ref", required=True)
    load_parser.add_argument("--orphan-candidate", type=Path)
    load_parser.add_argument("--no-recover", action="store_true")

    commit_parser = subparsers.add_parser("commit")
    commit_parser.add_argument("--passport", required=True, type=Path)
    commit_parser.add_argument("--workspace-root", required=True, type=Path)
    commit_parser.add_argument("--ledger-path", required=True, type=Path)
    commit_parser.add_argument("--ledger", required=True, type=Path)
    commit_parser.add_argument("--profile", action="append", required=True, type=Path)
    commit_parser.add_argument("--project-ref", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command in {"validate", "replay", "append", "summary"}:
            catalog = load_profile_catalog(args.profile)
            ledger = load_ledger(args.ledger)
        if args.command == "validate":
            replay_ledger(
                ledger,
                catalog,
                expected_project_ref=args.project_ref,
                require_materialized=not args.allow_in_memory,
            )
            _emit_json({"status": "valid", "schema_version": LEDGER_SCHEMA_VERSION})
        elif args.command == "replay":
            _emit_json(
                replay_ledger(
                    ledger,
                    catalog,
                    expected_project_ref=args.project_ref,
                    require_materialized=not args.allow_in_memory,
                )
            )
        elif args.command == "append":
            updated = append_event(
                ledger,
                _event_input(args.event),
                catalog,
                expected_project_ref=args.project_ref,
            )
            sys.stdout.buffer.write(canonical_bytes(updated))
        elif args.command == "summary":
            projection = replay_ledger(
                ledger, catalog, expected_project_ref=args.project_ref
            )
            env = {ENV_FLAG: "1"} if args.force else None
            rendered = checkpoint_summary(
                projection,
                moment=args.moment,
                env=env,
                signal_event_id=args.signal_event_id,
            )
            if rendered is not None:
                print(rendered)
        elif args.command == "load-bound":
            catalog = load_profile_catalog(args.profile)
            result = load_bound_ledger(
                args.passport,
                args.workspace_root,
                catalog,
                expected_project_ref=args.project_ref,
                orphan_candidate=args.orphan_candidate,
                recover=not args.no_recover,
            )
            _emit_json(result)
        elif args.command == "commit":
            catalog = load_profile_catalog(args.profile)
            ledger = load_ledger(args.ledger)
            pointer = commit_ledger_transaction(
                args.passport,
                args.ledger_path,
                args.workspace_root,
                ledger,
                catalog,
                args.project_ref,
            )
            _emit_json(pointer)
        return 0
    except (ContractError, ProfileContractError) as exc:
        print(f"[inquiry_branch_ledger ERROR] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
