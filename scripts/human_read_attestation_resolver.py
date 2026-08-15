"""Deterministically resolve USER_ATTESTED_READ coverage for one citation.

The ledger is a user declaration. This resolver never infers that reading or
comprehension occurred; it only determines whether the latest declaration's
explicit scope covers the supplied citation anchor. Unknown, missing, invalid,
or ambiguous coverage is never eligible for an ``ok`` marker (#738).

The JSON result is a transient routing decision, not a persisted audit receipt:
it deliberately carries no ledger or anchor digest. Consumers MUST recompute it
from the current ledger and exact current anchor on every finalizer pass.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


SIGNAL_TYPE = "USER_ATTESTED_READ"
SCHEMA_VERSION = "user-attested-read-resolution/1.0"
ARTIFACT_ROLE = "transient_routing_decision"
MAX_REASON_CHARS = 1000
ANCHOR_KINDS = frozenset({"quote", "page", "section", "paragraph", "none"})
READ_SCOPE_LEVELS = frozenset(
    {"full_text", "sections", "abstract_only", "toc_only", "unknown"}
)
_RFC3339_UTC = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$"
)
_PAGE_RANGE = re.compile(
    r"(?:pages?|p\.|pp\.)\s*:?\s*(\d+)\s*(?:-\s*(\d+))?\s*",
    re.IGNORECASE,
)
_FINALIZER_DISPOSITION = {
    "covered": "eligible_for_ok",
    "partial_coverage": "acknowledged_partial",
    "coverage_unknown": "acknowledged_partial",
    "not_attested": "unacknowledged_low_warn",
    "rescinded": "unacknowledged_low_warn",
    "anchor_unresolved": "anchor_precedence",
    "ledger_invalid": "block_invalid_ledger",
}


class LedgerValidationError(ValueError):
    """The current ledger does not satisfy the closed #738 contract."""


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: _UniqueKeySafeLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable mapping key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def _result(
    citation_key: str,
    state: str,
    reason: str,
    *,
    marked_at: str | None = None,
) -> dict[str, Any]:
    bounded_reason = (
        reason
        if len(reason) <= MAX_REASON_CHARS
        else reason[: MAX_REASON_CHARS - 3] + "..."
    )
    out: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_role": ARTIFACT_ROLE,
        "citation_key": citation_key,
        "signal_type": SIGNAL_TYPE,
        "state": state,
        "ok_eligible": state == "covered",
        "finalizer_disposition": _FINALIZER_DISPOSITION[state],
        "reason": bounded_reason,
    }
    if marked_at is not None:
        out["governing_marked_at"] = marked_at
    return out


def _timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or _RFC3339_UTC.fullmatch(value) is None:
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        return None
    return parsed


def _closed_object(
    value: Any,
    *,
    label: str,
    required: set[str],
    allowed: set[str],
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LedgerValidationError(f"{label} must be an object")
    missing = sorted(required - set(value))
    extra = sorted(set(value) - allowed, key=repr)
    if missing:
        raise LedgerValidationError(f"{label} missing required keys: {missing!r}")
    if extra:
        raise LedgerValidationError(f"{label} has unexpected keys: {extra!r}")
    return value


def _bounded_string(
    value: Any, *, label: str, minimum: int = 1, maximum: int | None = None
) -> str:
    if not isinstance(value, str) or len(value) < minimum:
        raise LedgerValidationError(f"{label} must be a non-empty string")
    if maximum is not None and len(value) > maximum:
        raise LedgerValidationError(f"{label} exceeds {maximum} characters")
    return value


def _validate_scope(value: Any, *, label: str) -> dict[str, Any]:
    scope = _closed_object(
        value,
        label=label,
        required={"level"},
        allowed={"level", "locators", "note"},
    )
    level = scope["level"]
    if not isinstance(level, str) or level not in READ_SCOPE_LEVELS:
        raise LedgerValidationError(f"{label}.level is outside the closed enum")
    if "locators" in scope:
        if level != "sections":
            raise LedgerValidationError(
                f"{label}.locators are legal only when level=sections"
            )
        locators = scope["locators"]
        if not isinstance(locators, list) or not locators:
            raise LedgerValidationError(f"{label}.locators must be a non-empty array")
        for index, locator in enumerate(locators):
            _bounded_string(
                locator,
                label=f"{label}.locators[{index}]",
                maximum=200,
            )
    if "note" in scope:
        _bounded_string(scope["note"], label=f"{label}.note", maximum=1000)
    return scope


def _validated_rows(
    ledger: Any,
) -> list[tuple[dict[str, Any], datetime, datetime | None]]:
    root = _closed_object(
        ledger,
        label="ledger",
        required={"session_id", "created_at", "human_read"},
        allowed={"session_id", "created_at", "human_read"},
    )
    _bounded_string(root["session_id"], label="ledger.session_id")
    if _timestamp(root["created_at"]) is None:
        raise LedgerValidationError(
            "ledger.created_at must be an RFC3339 UTC timestamp ending in Z"
        )
    rows = root["human_read"]
    if not isinstance(rows, list):
        raise LedgerValidationError("ledger.human_read must be an array")

    validated: list[tuple[dict[str, Any], datetime, datetime | None]] = []
    for index, raw in enumerate(rows):
        label = f"ledger.human_read[{index}]"
        row = _closed_object(
            raw,
            label=label,
            required={"citation_key", "marked_at"},
            allowed={
                "citation_key",
                "marked_at",
                "rescinded_at",
                "attestation_type",
                "read_scope",
            },
        )
        _bounded_string(row["citation_key"], label=f"{label}.citation_key")
        marked = _timestamp(row["marked_at"])
        if marked is None:
            raise LedgerValidationError(
                f"{label}.marked_at must be an RFC3339 UTC timestamp ending in Z"
            )
        rescinded: datetime | None = None
        if "rescinded_at" in row:
            rescinded = _timestamp(row["rescinded_at"])
            if rescinded is None:
                raise LedgerValidationError(
                    f"{label}.rescinded_at must be an RFC3339 UTC timestamp ending in Z"
                )
            if rescinded < marked:
                raise LedgerValidationError(
                    f"{label}.rescinded_at precedes marked_at"
                )

        has_type = "attestation_type" in row
        has_scope = "read_scope" in row
        if has_type != has_scope:
            raise LedgerValidationError(
                f"{label} current attestation_type and read_scope must appear together; "
                "legacy rows omit both"
            )
        if has_type:
            if row["attestation_type"] != SIGNAL_TYPE:
                raise LedgerValidationError(
                    f"{label}.attestation_type must equal {SIGNAL_TYPE}"
                )
            _validate_scope(row["read_scope"], label=f"{label}.read_scope")
        validated.append((row, marked, rescinded))
    return validated


def _normalize(value: str) -> str:
    return " ".join(
        value.casefold().replace("–", "-").replace("—", "-").split()
    )


def _page_locator_covers(locator: str, anchor_value: str) -> bool:
    try:
        page = int(anchor_value.strip())
    except ValueError:
        return False
    if page < 1:
        return False
    match = _PAGE_RANGE.fullmatch(_normalize(locator))
    if match is None:
        return False
    start = int(match.group(1))
    end = int(match.group(2) or start)
    if start < 1 or end < 1 or end < start:
        return False
    return start <= page <= end


def _locator_covers(anchor_kind: str, anchor_value: str, locator: str) -> bool:
    kind = anchor_kind
    value = _normalize(anchor_value)
    candidate = _normalize(locator)
    if kind == "page":
        return _page_locator_covers(candidate, value)
    if kind not in {"section", "paragraph"}:
        return False
    return candidate in {value, f"{kind}:{value}", f"{kind} {value}"}


def _anchor_precedence_result(
    citation_key: str, anchor_kind: Any, anchor_value: Any
) -> dict[str, Any] | None:
    """Resolve precedence-zero anchor failures before opening the ledger."""
    if not isinstance(anchor_kind, str) or anchor_kind not in ANCHOR_KINDS:
        return _result(
            citation_key,
            "anchor_unresolved",
            f"anchor kind {anchor_kind!r} is outside the closed enum",
        )
    if (
        anchor_kind == "none"
        or not isinstance(anchor_value, str)
        or not anchor_value.strip()
    ):
        return _result(
            citation_key,
            "anchor_unresolved",
            "citation anchor is absent or unresolved",
        )
    return None


def resolve_user_attested_read(
    ledger: dict[str, Any] | None,
    *,
    citation_key: str,
    anchor_kind: str,
    anchor_value: str,
) -> dict[str, Any]:
    """Return a closed resolution object; only ``covered`` is ok-eligible."""
    anchor_failure = _anchor_precedence_result(
        citation_key, anchor_kind, anchor_value
    )
    if anchor_failure is not None:
        return anchor_failure
    if ledger is None:
        return _result(
            citation_key, "not_attested", "no read ledger exists for this passport"
        )

    try:
        rows = _validated_rows(ledger)
    except LedgerValidationError as exc:
        return _result(citation_key, "ledger_invalid", str(exc))

    events: list[tuple[datetime, int, int, str, dict[str, Any]]] = []
    for index, (row, marked, rescinded) in enumerate(rows):
        if row["citation_key"] != citation_key:
            continue
        events.append((marked, index, 0, "mark", row))
        if rescinded is not None:
            events.append((rescinded, index, 1, "rescind", row))

    if not events:
        return _result(
            citation_key, "not_attested", "no matching user attestation"
        )

    _, _, _, event_kind, row = max(
        events, key=lambda item: (item[0], item[1], item[2])
    )
    marked_at = row["marked_at"]
    if event_kind == "rescind":
        return _result(
            citation_key,
            "rescinded",
            "latest matching event rescinds the attestation",
            marked_at=marked_at,
        )

    scope = row.get("read_scope")
    if scope is None or scope["level"] == "unknown":
        return _result(
            citation_key,
            "coverage_unknown",
            "legacy or explicit unknown scope cannot establish anchor coverage",
            marked_at=marked_at,
        )

    level = scope.get("level")
    if level == "full_text":
        return _result(
            citation_key,
            "covered",
            "explicit full_text scope covers the resolved anchor",
            marked_at=marked_at,
        )
    if level in {"abstract_only", "toc_only"}:
        return _result(
            citation_key,
            "partial_coverage",
            f"{level} scope does not establish coverage of the citation anchor",
            marked_at=marked_at,
        )
    locators = scope.get("locators")
    if not locators:
        return _result(
            citation_key,
            "coverage_unknown",
            "sections scope has no deterministic locator",
            marked_at=marked_at,
        )
    if anchor_kind == "quote":
        return _result(
            citation_key,
            "partial_coverage",
            "quote anchors require full_text scope",
            marked_at=marked_at,
        )
    if any(
        _locator_covers(anchor_kind, anchor_value, locator)
        for locator in locators
    ):
        return _result(
            citation_key,
            "covered",
            "a declared locator deterministically covers the anchor",
            marked_at=marked_at,
        )
    return _result(
        citation_key,
        "partial_coverage",
        "no declared locator deterministically covers the anchor",
        marked_at=marked_at,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Resolve USER_ATTESTED_READ coverage for one citation anchor."
    )
    parser.add_argument("--read-log", type=Path, required=True)
    parser.add_argument("--citation-key", required=True)
    parser.add_argument("--anchor-kind", required=True)
    parser.add_argument("--anchor-value", default="")
    args = parser.parse_args(argv)

    # Anchor presence is the finalizer's precedence-zero check.  Do not even
    # open the read ledger when that structural prerequisite is unresolved;
    # otherwise a malformed irrelevant ledger could mask NO-LOCATOR routing.
    anchor_failure = _anchor_precedence_result(
        args.citation_key, args.anchor_kind, args.anchor_value
    )
    if anchor_failure is not None:
        print(json.dumps(anchor_failure, sort_keys=True))
        return 0

    if args.read_log.exists():
        try:
            ledger = yaml.load(
                args.read_log.read_text(encoding="utf-8"),
                Loader=_UniqueKeySafeLoader,
            )
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
            print(
                json.dumps(
                    _result(
                        args.citation_key,
                        "ledger_invalid",
                        f"cannot parse read ledger: {exc}",
                    ),
                    sort_keys=True,
                )
            )
            return 2
    else:
        ledger = None
    result = resolve_user_attested_read(
        ledger,
        citation_key=args.citation_key,
        anchor_kind=args.anchor_kind,
        anchor_value=args.anchor_value,
    )
    print(json.dumps(result, sort_keys=True))
    return 2 if result["state"] == "ledger_invalid" else 0


if __name__ == "__main__":
    sys.exit(main())
