#!/usr/bin/env python3
"""Build, validate, page, and inertly render ARS shared evidence rows.

The module is deliberately standard-library-only and hermetic.  Builders may
inspect only the ``session_source_or_none`` string explicitly supplied by their
caller.  Validators optionally replay against that same explicit string.
Renderers require an explicit source map (in memory, a JSON file, or the
named files of a ``--source-dir`` folder, #933) to replay source-bound rows;
they never retrieve, re-extract, invoke a model, consult a cache, follow a row
pointer, or read/write the human-read ledger.  Integrity validation checks that
the persisted encoded and decoded anchors agree but never alters provenance.

CLI exit codes: 0 success, 1 contract/data failure, 2 named-input or argparse
usage failure. The CLI handles ``evidence-row/1.0`` rows only and refuses
``evidence-row/1.1`` advisory rows with exit 2 (#947).
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import html
import json
import re
import stat
import sys
import unicodedata
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import unquote


SCHEMA_VERSION = "evidence-row/1.0"
SURFACE = "phase_e_claim_verification"
ADVISORY_SCHEMA_VERSION = "evidence-row/1.1"
ADVISORY_SURFACE = "authority_profile_content_coverage"
EXTRACTOR_VERSION = "evidence-rows/1.0"
QUOTE_WORD_CAP = 25
TEXT_CHAR_CAP = 1000
DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 25
LEGACY_UNAVAILABLE_LABEL = "LEGACY — EVIDENCE ROWS UNAVAILABLE"

ANCHOR_KINDS = frozenset({"quote", "page", "section", "paragraph", "none"})
EXCERPT_STATES = frozenset(
    {
        "verified_exact_match",
        "agent_extracted",
        "unconfirmed_anchor",
        "not_checked",
        "source_missing",
        "access_failed",
        "retrieval_failed",
        "anchorless",
    }
)
STATE_LABELS = {
    "verified_exact_match": "VERIFIED EXACT MATCH",
    "agent_extracted": "AGENT-EXTRACTED — NOT AUTHORITATIVE",
    "unconfirmed_anchor": "UNCONFIRMED ANCHOR",
    "not_checked": "NOT CHECKED",
    "source_missing": "SOURCE NOT HELD",
    "access_failed": "ACCESS FAILED",
    "retrieval_failed": "RETRIEVAL FAILED",
    "anchorless": "ANCHORLESS — NO EXCERPT",
}
EMPTY_STATES = frozenset(
    {"not_checked", "source_missing", "access_failed", "retrieval_failed", "anchorless"}
)
SOURCE_BOUND_STATES = frozenset(
    {"verified_exact_match", "agent_extracted", "unconfirmed_anchor"}
)
EXCERPT_TEXT_STATES = frozenset({"verified_exact_match", "agent_extracted"})
FAILURE_STATES = frozenset({"not_checked", "source_missing", "access_failed", "retrieval_failed", "anchorless"})
SELECTION_TIERS = frozenset({"HIGH-IMPACT", "RANDOM", "TOP-UP", "ALL"})
VERDICTS = frozenset(
    {
        "VERIFIED",
        "MINOR_DISTORTION",
        "MAJOR_DISTORTION",
        "UNVERIFIABLE",
        "UNVERIFIABLE_ACCESS",
    }
)
CACHE_STATUSES = frozenset({"not_used", "miss", "hit"})
SHARING_SCOPES = frozenset({"session_only", "user_confirmed_shareable"})
RIGHTS_BASES = frozenset({"not_assessed", "user_declared_authorized"})
ADVISORY_ANCHOR_KINDS = frozenset({"quote", "none"})
ADVISORY_EXCERPT_STATES = frozenset(
    {
        "agent_extracted",
        "checked_no_match",
        "not_checked",
        "source_missing",
        "access_failed",
        "retrieval_failed",
    }
)
ADVISORY_SOURCE_BOUND_STATES = frozenset({"agent_extracted", "checked_no_match"})
ADVISORY_EMPTY_STATES = frozenset(
    {"checked_no_match", "not_checked", "source_missing", "access_failed", "retrieval_failed"}
)
ADVISORY_FAILURE_STATES = frozenset(
    {"not_checked", "source_missing", "access_failed", "retrieval_failed"}
)
DOCUMENT_LOCATOR_KINDS = frozenset(
    {"document", "page", "section", "paragraph", "other"}
)
DOCUMENT_LOCATOR_PROVENANCE = "agent_supplied_not_independently_authenticated"
MAX_JSON_NESTING = 100

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_REF_SLUG_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_:-]*$")
_ROW_ID_RE = re.compile(r"^EVR-[A-Za-z0-9._:-]+$")
_AUTHORITY_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_POINTER_RE = re.compile(r"^/(?:profiles|overlays)/[0-9]+/requirements/[0-9]+(?:/.*)?$")
_RFC3339_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt]"
    r"(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
    r"(?:\.[0-9]+)?(?:[Zz]|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])$"
)
_HEX = frozenset("0123456789abcdefABCDEF")


class EvidenceRowError(ValueError):
    """A shared evidence row violates the closed #656 contract."""


class EvidenceRowInputError(EvidenceRowError):
    """A named CLI input could not be read or parsed as strict JSON."""


def _fail(path: str, message: str) -> None:
    raise EvidenceRowError(f"{path}: {message}")


def _input_fail(path: str, message: str) -> None:
    raise EvidenceRowInputError(f"{path}: {message}")


def _closed(value: Any, path: str, required: set[str], allowed: set[str] | None = None) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(path, "must be an object")
    allowed = required if allowed is None else allowed
    missing = sorted(required - set(value))
    extra = sorted(set(value) - allowed)
    if missing:
        _fail(path, f"missing required key(s): {', '.join(missing)}")
    if extra:
        _fail(path, f"unexpected key(s): {', '.join(extra)}")
    return value


def _string(value: Any, path: str, *, minimum: int = 0, maximum: int | None = None) -> str:
    if not isinstance(value, str):
        _fail(path, "must be a string")
    if len(value) < minimum:
        _fail(path, f"must contain at least {minimum} character(s)")
    if maximum is not None and len(value) > maximum:
        _fail(path, f"exceeds {maximum} Unicode code points")
    _reject_unsafe_controls(value, path)
    return value


def _nullable_string(value: Any, path: str, *, minimum: int = 0, maximum: int | None = None) -> str | None:
    if value is None:
        return None
    return _string(value, path, minimum=minimum, maximum=maximum)


def _sha(value: Any, path: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        _fail(path, "must be a lowercase 64-hex SHA-256 digest" + (" or null" if nullable else ""))
    return value


def _integer(value: Any, path: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        _fail(path, "must be an integer")
    if value < minimum:
        _fail(path, f"must be >= {minimum}")
    return value


def _enum(value: Any, path: str, allowed: frozenset[str] | set[str]) -> str:
    if not isinstance(value, str) or value not in allowed:
        _fail(path, f"must be one of {sorted(allowed)}")
    return value


def _authority_identifier(value: Any, path: str) -> str:
    text = _string(value, path, minimum=1, maximum=200)
    if _AUTHORITY_ID_RE.fullmatch(text) is None:
        _fail(path, "must use lowercase letters, digits, dot, underscore, or hyphen")
    return text


def _json_pointer(value: Any, path: str) -> str:
    text = _string(value, path, minimum=1, maximum=2000)
    if _POINTER_RE.fullmatch(text) is None or any(char.isspace() for char in text):
        _fail(path, "must be a normalized profile/overlay requirement JSON Pointer")
    return text


def _single_line(value: Any, path: str, *, maximum: int) -> str:
    text = _string(value, path, minimum=1, maximum=maximum)
    if any(char in text for char in "\r\n") or any(
        unicodedata.category(char) in {"Cc", "Zl", "Zp"} for char in text
    ):
        _fail(path, "must be a single line without control characters")
    return text


def _advisory_relative_path(value: Any, path: str) -> str:
    text = _single_line(value, path, maximum=1024)
    if "\\" in text or text.startswith("/") or text.endswith("/"):
        _fail(path, "must be a normalized relative POSIX path")
    parts = text.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        _fail(path, "must not contain empty, dot, or parent-traversal components")
    return text


def _reject_unsafe_controls(value: str, path: str) -> None:
    for char in value:
        code = ord(char)
        if (code < 0x20 and char not in "\t\n\r") or code == 0x7F:
            _fail(path, f"contains forbidden control U+{code:04X}")
        if 0xD800 <= code <= 0xDFFF:
            _fail(path, "contains an unpaired UTF-16 surrogate")


def _utf8(value: str, path: str) -> bytes:
    try:
        return value.encode("utf-8", errors="strict")
    except UnicodeError as exc:
        _fail(path, f"is not strict UTF-8 encodable: {exc}")


def _hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _hash_text(value: str, path: str = "text") -> str:
    return _hash_bytes(_utf8(value, path))


def strict_percent_decode(value: str) -> str:
    """Decode RFC-3986 percent escapes exactly once using strict UTF-8.

    ``+`` remains a literal plus.  A decoded ``%HH`` sequence is deliberately
    left as text, so ``%2520`` becomes ``%20`` rather than a space.
    """

    _string(value, "value", maximum=12000)
    index = 0
    while index < len(value):
        if value[index] == "%":
            if index + 2 >= len(value) or value[index + 1] not in _HEX or value[index + 2] not in _HEX:
                _fail("value", f"malformed percent escape at character {index}")
            index += 3
        else:
            index += 1
    try:
        decoded = unquote(value, encoding="utf-8", errors="strict")
    except UnicodeError as exc:
        _fail("value", f"percent escapes are not valid UTF-8: {exc}")
    _string(decoded, "decoded value", maximum=TEXT_CHAR_CAP)
    return decoded


def _bounded_external_text(value: str, path: str) -> str:
    value = _string(value, path, minimum=1, maximum=TEXT_CHAR_CAP)
    words = len(value.split())
    if words > QUOTE_WORD_CAP:
        _fail(path, f"exceeds {QUOTE_WORD_CAP} words by whitespace split (got {words})")
    return value


def _canonical_json(value: Mapping[str, Any]) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError, UnicodeError) as exc:
        _fail("row", f"cannot be canonically serialized: {exc}")


def _row_sha256(row: Mapping[str, Any]) -> str:
    payload = copy.deepcopy(dict(row))
    payload.pop("row_sha256", None)
    return _hash_text(_canonical_json(payload), "canonical row")


def _cache_key(
    source_content_sha256: str,
    anchor_kind: str,
    anchor_decoded: str,
    *,
    claim_id: str,
    ref_slug: str,
    state: str,
    excerpt_candidate_sha256: str | None,
) -> str:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "surface": SURFACE,
        "claim_id": claim_id,
        "ref_slug": ref_slug,
        "source_content_sha256": source_content_sha256,
        "anchor_kind": anchor_kind,
        "anchor_decoded_sha256": _hash_text(anchor_decoded, "anchor.value_decoded"),
        "state": state,
        "excerpt_candidate_sha256": excerpt_candidate_sha256,
        "extractor_version": EXTRACTOR_VERSION,
        "quote_word_cap": QUOTE_WORD_CAP,
        "text_char_cap": TEXT_CHAR_CAP,
    }
    return _hash_text(_canonical_json(payload), "cache key payload")


def _timestamp_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _timestamp(value: Any, path: str) -> str:
    value = _string(value, path, minimum=1, maximum=100)
    if _RFC3339_RE.fullmatch(value) is None:
        _fail(path, "must be an RFC 3339 date-time")
    candidate = value[:-1] + "+00:00" if value[-1] in {"Z", "z"} else value
    try:
        dt.datetime.fromisoformat(candidate)
    except ValueError as exc:
        _fail(path, f"must be an RFC 3339 date-time: {exc}")
    return value


def _span(source: str, excerpt: str) -> dict[str, int]:
    char_start = source.find(excerpt)
    if char_start < 0:
        _fail("excerpt.text", "must be an exact contiguous substring of session_source_or_none")
    start = len(_utf8(source[:char_start], "session_source_or_none prefix"))
    return {"start": start, "end": start + len(_utf8(excerpt, "excerpt.text"))}


def _empty_excerpt(state: str) -> dict[str, Any]:
    return {
        "state": state,
        "text": None,
        "excerpt_sha256": None,
        "source_span_utf8": None,
        "captured_at": None,
    }


def _text_excerpt(
    state: str,
    text: str,
    source: str,
    *,
    captured_at: str | None = None,
) -> dict[str, Any]:
    text = _bounded_external_text(text, "excerpt.text")
    return {
        "state": state,
        "text": text,
        "excerpt_sha256": _hash_text(text, "excerpt.text"),
        "source_span_utf8": _span(source, text),
        "captured_at": (
            _timestamp_now()
            if captured_at is None
            else _timestamp(captured_at, "captured_at")
        ),
    }


def _template(row: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(row, Mapping):
        _fail("row", "must be a mapping")
    raw = copy.deepcopy(dict(row))
    required = {"surface", "row_id", "claim", "source", "anchor", "verdict", "detail"}
    allowed = required | {"schema_version", "excerpt", "cache", "content_handling", "row_sha256"}
    _closed(raw, "row template", required, allowed)
    if raw.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
        _fail("schema_version", f"must equal {SCHEMA_VERSION}")
    if raw["surface"] != SURFACE:
        _fail("surface", f"must equal {SURFACE}")
    row_id = _string(raw["row_id"], "row_id", minimum=1, maximum=200)
    if _ROW_ID_RE.fullmatch(row_id) is None:
        _fail("row_id", "must match ^EVR-[A-Za-z0-9._:-]+$")

    claim = _closed(raw["claim"], "claim", {"claim_id", "text", "paper_locator", "selection_tier"})
    normalized_claim = {
        "claim_id": _string(claim["claim_id"], "claim.claim_id", minimum=1, maximum=200),
        "text": _string(claim["text"], "claim.text", minimum=1, maximum=2000),
        "paper_locator": _string(claim["paper_locator"], "claim.paper_locator", minimum=1, maximum=500),
        "selection_tier": _enum(claim["selection_tier"], "claim.selection_tier", SELECTION_TIERS),
    }

    source = _closed(
        raw["source"],
        "source",
        {"ref_slug", "display_label"},
        {
            "ref_slug",
            "display_label",
            "source_content_sha256",
            "source_content_utf8_bytes",
            "source_artifact_sha256",
        },
    )
    ref_slug = _nullable_string(source["ref_slug"], "source.ref_slug", minimum=1, maximum=300)
    if ref_slug is not None and _REF_SLUG_RE.fullmatch(ref_slug) is None:
        _fail("source.ref_slug", "does not match the citation slug grammar")
    display_label = _nullable_string(source["display_label"], "source.display_label", minimum=1, maximum=500)
    artifact_sha = _sha(source.get("source_artifact_sha256"), "source.source_artifact_sha256", nullable=True)

    anchor = _closed(
        raw["anchor"],
        "anchor",
        {"kind", "value_encoded"},
        {"kind", "value_encoded", "value_decoded"},
    )
    kind = _enum(anchor["kind"], "anchor.kind", ANCHOR_KINDS)
    encoded = _string(anchor["value_encoded"], "anchor.value_encoded", maximum=12000)
    decoded = strict_percent_decode(encoded)
    if "value_decoded" in anchor and anchor["value_decoded"] != decoded:
        _fail("anchor.value_decoded", "must equal one strict percent decode of anchor.value_encoded")
    if kind == "none":
        if encoded or decoded:
            _fail("anchor", "kind=none requires empty encoded and decoded values")
    elif not decoded.strip():
        _fail("anchor.value_decoded", "non-none anchors require a non-empty decoded value")
    if kind == "quote":
        _bounded_external_text(decoded, "anchor.value_decoded")

    handling = raw.get("content_handling", {})
    if not isinstance(handling, dict):
        _fail("content_handling", "must be an object")
    allowed_handling = {"contains_external_text", "sharing_scope", "rights_basis"}
    extra_handling = sorted(set(handling) - allowed_handling)
    if extra_handling:
        _fail("content_handling", f"unexpected key(s): {', '.join(extra_handling)}")
    sharing_scope = _enum(handling.get("sharing_scope", "session_only"), "content_handling.sharing_scope", SHARING_SCOPES)
    rights_basis = _enum(handling.get("rights_basis", "not_assessed"), "content_handling.rights_basis", RIGHTS_BASES)
    if (sharing_scope == "user_confirmed_shareable") != (rights_basis == "user_declared_authorized"):
        _fail("content_handling", "user_confirmed_shareable and user_declared_authorized must appear together")

    return {
        "schema_version": SCHEMA_VERSION,
        "surface": SURFACE,
        "row_id": row_id,
        "claim": normalized_claim,
        "source": {
            "ref_slug": ref_slug,
            "display_label": display_label,
            "source_content_sha256": None,
            "source_content_utf8_bytes": None,
            "source_artifact_sha256": artifact_sha,
        },
        "anchor": {"kind": kind, "value_encoded": encoded, "value_decoded": decoded},
        "verdict": _enum(raw["verdict"], "verdict", VERDICTS),
        "detail": _string(raw["detail"], "detail", maximum=2000),
        "content_handling": {
            "contains_external_text": False,
            "sharing_scope": sharing_scope,
            "rights_basis": rights_basis,
        },
    }


def _advisory_template(row: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize caller-supplied metadata for one #681 evidence row."""

    if not isinstance(row, Mapping):
        _fail("row", "must be a mapping")
    raw = copy.deepcopy(dict(row))
    required = {"surface", "row_id", "coverage_subject", "source", "anchor"}
    allowed = required | {
        "schema_version",
        "excerpt",
        "cache",
        "content_handling",
        "row_sha256",
    }
    _closed(raw, "row template", required, allowed)
    if raw.get("schema_version", ADVISORY_SCHEMA_VERSION) != ADVISORY_SCHEMA_VERSION:
        _fail("schema_version", f"must equal {ADVISORY_SCHEMA_VERSION}")
    if raw["surface"] != ADVISORY_SURFACE:
        _fail("surface", f"must equal {ADVISORY_SURFACE}")
    row_id = _string(raw["row_id"], "row_id", minimum=1, maximum=200)
    if _ROW_ID_RE.fullmatch(row_id) is None:
        _fail("row_id", "must match ^EVR-[A-Za-z0-9._:-]+$")

    subject = _closed(
        raw["coverage_subject"],
        "coverage_subject",
        {
            "requirement_id",
            "requirement_pointer",
            "authority_anchor_pointer",
            "expectation_field_id",
            "expectation_pointer",
            "expectation_digest",
            "document_locator",
        },
    )
    requirement_pointer = _json_pointer(
        subject["requirement_pointer"], "coverage_subject.requirement_pointer"
    )
    if not re.fullmatch(r"/(?:profiles|overlays)/[0-9]+/requirements/[0-9]+", requirement_pointer):
        _fail("coverage_subject.requirement_pointer", "must point to one exact requirement")
    authority_anchor_pointer = _json_pointer(
        subject["authority_anchor_pointer"],
        "coverage_subject.authority_anchor_pointer",
    )
    if authority_anchor_pointer != requirement_pointer + "/authority_anchor":
        _fail(
            "coverage_subject.authority_anchor_pointer",
            "must be the requirement's exact authority_anchor pointer",
        )
    expectation_pointer = _json_pointer(
        subject["expectation_pointer"], "coverage_subject.expectation_pointer"
    )
    if re.fullmatch(
        re.escape(requirement_pointer) + r"/structured_expectations/[0-9]+",
        expectation_pointer,
    ) is None:
        _fail(
            "coverage_subject.expectation_pointer",
            "must point to one structured expectation under the requirement",
        )
    locator = _closed(
        subject["document_locator"],
        "coverage_subject.document_locator",
        {"kind", "value", "provenance"},
    )
    if locator["provenance"] != DOCUMENT_LOCATOR_PROVENANCE:
        _fail(
            "coverage_subject.document_locator.provenance",
            f"must equal {DOCUMENT_LOCATOR_PROVENANCE}",
        )

    source = _closed(
        raw["source"],
        "source",
        {"artifact_id", "relative_path", "source_artifact_sha256", "source_artifact_size_bytes"},
        {
            "artifact_id",
            "relative_path",
            "source_artifact_sha256",
            "source_artifact_size_bytes",
            "source_content_sha256",
            "source_content_utf8_bytes",
        },
    )
    anchor = _closed(
        raw["anchor"],
        "anchor",
        {"kind", "value_encoded"},
        {"kind", "value_encoded", "value_decoded"},
    )
    kind = _enum(anchor["kind"], "anchor.kind", ADVISORY_ANCHOR_KINDS)
    encoded = _string(anchor["value_encoded"], "anchor.value_encoded", maximum=12000)
    decoded = strict_percent_decode(encoded)
    if "value_decoded" in anchor and anchor["value_decoded"] != decoded:
        _fail(
            "anchor.value_decoded",
            "must equal one strict percent decode of anchor.value_encoded",
        )
    if kind == "none":
        if encoded or decoded:
            _fail("anchor", "kind=none requires empty encoded and decoded values")
    else:
        if not decoded.strip():
            _fail("anchor.value_decoded", "quote anchors require non-empty text")
        _bounded_external_text(decoded, "anchor.value_decoded")

    handling = raw.get("content_handling", {})
    if not isinstance(handling, dict):
        _fail("content_handling", "must be an object")
    extra_handling = sorted(
        set(handling) - {"contains_external_text", "sharing_scope", "rights_basis"}
    )
    if extra_handling:
        _fail("content_handling", f"unexpected key(s): {', '.join(extra_handling)}")
    sharing_scope = _enum(
        handling.get("sharing_scope", "session_only"),
        "content_handling.sharing_scope",
        SHARING_SCOPES,
    )
    rights_basis = _enum(
        handling.get("rights_basis", "not_assessed"),
        "content_handling.rights_basis",
        RIGHTS_BASES,
    )
    if (sharing_scope == "user_confirmed_shareable") != (
        rights_basis == "user_declared_authorized"
    ):
        _fail(
            "content_handling",
            "user_confirmed_shareable and user_declared_authorized must appear together",
        )

    return {
        "schema_version": ADVISORY_SCHEMA_VERSION,
        "surface": ADVISORY_SURFACE,
        "row_id": row_id,
        "coverage_subject": {
            "requirement_id": _authority_identifier(
                subject["requirement_id"], "coverage_subject.requirement_id"
            ),
            "requirement_pointer": requirement_pointer,
            "authority_anchor_pointer": authority_anchor_pointer,
            "expectation_field_id": _authority_identifier(
                subject["expectation_field_id"],
                "coverage_subject.expectation_field_id",
            ),
            "expectation_pointer": expectation_pointer,
            "expectation_digest": _sha(
                subject["expectation_digest"], "coverage_subject.expectation_digest"
            ),
            "document_locator": {
                "kind": _enum(
                    locator["kind"],
                    "coverage_subject.document_locator.kind",
                    DOCUMENT_LOCATOR_KINDS,
                ),
                "value": _single_line(
                    locator["value"],
                    "coverage_subject.document_locator.value",
                    maximum=500,
                ),
                "provenance": DOCUMENT_LOCATOR_PROVENANCE,
            },
        },
        "source": {
            "artifact_id": _authority_identifier(source["artifact_id"], "source.artifact_id"),
            "relative_path": _advisory_relative_path(
                source["relative_path"], "source.relative_path"
            ),
            "source_artifact_sha256": _sha(
                source["source_artifact_sha256"], "source.source_artifact_sha256"
            ),
            "source_artifact_size_bytes": _integer(
                source["source_artifact_size_bytes"],
                "source.source_artifact_size_bytes",
            ),
            "source_content_sha256": None,
            "source_content_utf8_bytes": None,
        },
        "anchor": {"kind": kind, "value_encoded": encoded, "value_decoded": decoded},
        "content_handling": {
            "contains_external_text": False,
            "sharing_scope": sharing_scope,
            "rights_basis": rights_basis,
        },
    }


def build_advisory(
    row: Mapping[str, Any],
    session_source_or_none: str | None,
    *,
    extracted_text: str | None = None,
    failure_state: str | None = None,
    cached_row: Mapping[str, Any] | None = None,
    captured_at: str | None = None,
) -> dict[str, Any]:
    """Build one closed #681 row from explicit evaluator metadata and source text.

    This function verifies provenance only.  It never infers a coverage status,
    invokes an evaluator, opens a source path, or performs retrieval.
    """

    output = _advisory_template(row)
    if output["source"]["source_artifact_size_bytes"] > 64 * 1024 * 1024:
        _fail("source.source_artifact_size_bytes", "must be <= 67108864")
    if cached_row is not None:
        _fail("cached_row", "evidence-row/1.1 forbids cache reuse")
    if session_source_or_none is not None and not isinstance(session_source_or_none, str):
        _fail("session_source_or_none", "must be a string or null")
    kind = output["anchor"]["kind"]
    decoded = output["anchor"]["value_decoded"]
    if extracted_text is not None:
        extracted_text = _bounded_external_text(extracted_text, "extracted_text")
        if kind != "quote" or extracted_text != decoded:
            _fail("extracted_text", "must exactly equal the decoded quote anchor")

    if failure_state is not None:
        if captured_at is not None:
            _fail("captured_at", "failure states require null captured_at")
        state = _enum(failure_state, "failure_state", ADVISORY_FAILURE_STATES)
        if kind != "none":
            _fail("anchor.kind", f"state={state} requires anchor.kind=none")
        excerpt = _empty_excerpt(state)
    elif kind == "quote":
        if captured_at is None:
            _fail(
                "captured_at",
                "agent_extracted requires an explicit evaluator-supplied timestamp",
            )
        if session_source_or_none is None:
            _fail("failure_state", "a missing source requires an explicit failure state")
        if decoded not in session_source_or_none:
            _fail(
                "anchor.value_decoded",
                "must be an exact contiguous substring of session_source_or_none",
            )
        source_bytes = _utf8(session_source_or_none, "session_source_or_none")
        if len(source_bytes) > 64 * 1024 * 1024:
            _fail("session_source_or_none", "exceeds 67108864 UTF-8 bytes")
        output["source"]["source_content_sha256"] = _hash_bytes(source_bytes)
        output["source"]["source_content_utf8_bytes"] = len(source_bytes)
        state = "agent_extracted"
        excerpt = _text_excerpt(
            state,
            decoded,
            session_source_or_none,
            captured_at=captured_at,
        )
    else:
        if captured_at is not None:
            _fail("captured_at", "checked_no_match requires null captured_at")
        if session_source_or_none is None:
            _fail("failure_state", "a missing source requires an explicit failure state")
        source_bytes = _utf8(session_source_or_none, "session_source_or_none")
        if len(source_bytes) > 64 * 1024 * 1024:
            _fail("session_source_or_none", "exceeds 67108864 UTF-8 bytes")
        output["source"]["source_content_sha256"] = _hash_bytes(source_bytes)
        output["source"]["source_content_utf8_bytes"] = len(source_bytes)
        state = "checked_no_match"
        excerpt = _empty_excerpt(state)

    output["excerpt"] = excerpt
    output["cache"] = {"status": "not_used", "key_sha256": None}
    output["content_handling"]["contains_external_text"] = bool(
        excerpt["text"] is not None or (kind == "quote" and decoded)
    )
    output["row_sha256"] = _row_sha256(output)
    replay_source = (
        session_source_or_none if state in ADVISORY_SOURCE_BOUND_STATES else None
    )
    return _validate_v1_1(output, replay_source)


def build(
    row: Mapping[str, Any],
    session_source_or_none: str | None,
    *,
    extracted_text: str | None = None,
    failure_state: str | None = None,
    cached_row: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one closed evidence row from metadata and explicit session text.

    ``failure_state`` accepts only an explicit empty state.  Positive states and
    ``unconfirmed_anchor`` are derived, never caller-asserted.  ``cached_row`` is
    an optional previously built whole row; a matching source-bound cache key
    replays its excerpt block and original timestamp.
    """

    output = _template(row)
    kind = output["anchor"]["kind"]
    decoded = output["anchor"]["value_decoded"]
    if session_source_or_none is not None and not isinstance(session_source_or_none, str):
        _fail("session_source_or_none", "must be a string or null")
    if session_source_or_none is not None:
        source_bytes = _utf8(session_source_or_none, "session_source_or_none")
        source_sha = _hash_bytes(source_bytes)
    else:
        source_bytes = b""
        source_sha = None

    if failure_state is not None:
        failure_state = _enum(failure_state, "failure_state", FAILURE_STATES)
        # A current explicit failure always wins.  Do not even inspect a cached
        # success: stale evidence must not overwrite access/retrieval reality.
        if extracted_text is not None:
            _fail("extracted_text", "cannot be combined with failure_state")
        if failure_state == "anchorless" and kind != "none":
            _fail("failure_state", "anchorless requires anchor.kind=none")
        if failure_state != "anchorless" and kind == "none":
            _fail("failure_state", "anchor.kind=none can only produce anchorless")
        if failure_state in {"source_missing", "access_failed", "retrieval_failed"} and session_source_or_none is not None:
            _fail("session_source_or_none", f"must be null for {failure_state}")
        state = failure_state
        excerpt = _empty_excerpt(state)
    elif kind == "none":
        if extracted_text is not None:
            _fail("extracted_text", "anchor.kind=none cannot carry an excerpt")
        state = "anchorless"
        excerpt = _empty_excerpt(state)
    elif kind == "paragraph":
        if extracted_text is not None:
            _fail("extracted_text", "paragraph anchors are an explicit not_checked empty state in V1")
        state = "not_checked"
        excerpt = _empty_excerpt(state)
    elif session_source_or_none is None:
        if extracted_text is not None:
            _fail("extracted_text", "cannot be accepted without session-held source text")
        state = "source_missing"
        excerpt = _empty_excerpt(state)
    else:
        if output["source"]["ref_slug"] is None:
            _fail("source.ref_slug", "source-bound quote/page/section processing requires a citation slug")
        output["source"]["source_content_sha256"] = source_sha
        output["source"]["source_content_utf8_bytes"] = len(source_bytes)

        candidate_text: str | None = None
        if kind == "quote":
            if extracted_text is not None:
                _fail("extracted_text", "quote evidence is fixed by the decoded writer anchor")
            prospective_state = "verified_exact_match" if decoded in session_source_or_none else "unconfirmed_anchor"
        elif kind in {"page", "section"}:
            if extracted_text is not None:
                candidate_text = _bounded_external_text(extracted_text, "extracted_text")
                _span(session_source_or_none, candidate_text)
                prospective_state = "agent_extracted"
            else:
                prospective_state = "not_checked"
        else:  # Defensive totality; paragraph/none returned above.
            _fail("anchor.kind", f"unsupported builder state for {kind}")

        cached: dict[str, Any] | None = None
        if cached_row is not None:
            try:
                cached = validate(cached_row)
            except EvidenceRowError:
                cached = None
            if cached is not None and cached["excerpt"]["state"] not in SOURCE_BOUND_STATES:
                cached = None
            if cached is not None and kind in {"page", "section"} and extracted_text is None:
                cached_text = cached["excerpt"]["text"]
                if cached["excerpt"]["state"] == "agent_extracted" and isinstance(cached_text, str):
                    candidate_text = cached_text
                    prospective_state = "agent_extracted"
            if cached is not None:
                expected_key = _cache_key(
                    source_sha,  # type: ignore[arg-type]
                    kind,
                    decoded,
                    claim_id=output["claim"]["claim_id"],
                    ref_slug=output["source"]["ref_slug"],
                    state=prospective_state,
                    excerpt_candidate_sha256=(
                        _hash_text(candidate_text, "extracted_text")
                        if prospective_state == "agent_extracted" and candidate_text is not None
                        else None
                    ),
                )
                if cached["cache"]["key_sha256"] != expected_key:
                    cached = None
        if cached is not None:
            # Match first, then replay against the exact current source.  This
            # catches a forged span/excerpt even if an attacker recomputed the
            # row digest and cache key around it.
            try:
                cached = validate(cached, session_source_or_none)
            except EvidenceRowError:
                cached = None
            if cached is not None:
                output["excerpt"] = copy.deepcopy(cached["excerpt"])
                output["cache"] = {"status": "hit", "key_sha256": expected_key}
                output["content_handling"]["contains_external_text"] = bool(
                    output["excerpt"]["text"] is not None or (kind == "quote" and decoded)
                )
                output["row_sha256"] = _row_sha256(output)
                return validate(output, session_source_or_none)

        if kind == "quote":
            if decoded in session_source_or_none:
                state = "verified_exact_match"
                excerpt = _text_excerpt(state, decoded, session_source_or_none)
            else:
                state = "unconfirmed_anchor"
                excerpt = _empty_excerpt(state)
        elif kind in {"page", "section"}:
            if extracted_text is None:
                state = "not_checked"
                excerpt = _empty_excerpt(state)
                output["source"]["source_content_sha256"] = None
                output["source"]["source_content_utf8_bytes"] = None
            else:
                state = "agent_extracted"
                excerpt = _text_excerpt(state, candidate_text, session_source_or_none)  # type: ignore[arg-type]

        if state in SOURCE_BOUND_STATES:
            expected_key = _cache_key(
                source_sha,  # type: ignore[arg-type]
                kind,
                decoded,
                claim_id=output["claim"]["claim_id"],
                ref_slug=output["source"]["ref_slug"],
                state=state,
                excerpt_candidate_sha256=(
                    excerpt["excerpt_sha256"] if state == "agent_extracted" else None
                ),
            )
            output["cache"] = {"status": "miss", "key_sha256": expected_key}
        else:
            output["cache"] = {"status": "not_used", "key_sha256": None}
        output["excerpt"] = excerpt

    if state in EMPTY_STATES:
        output["source"]["source_content_sha256"] = None
        output["source"]["source_content_utf8_bytes"] = None
        output["cache"] = {"status": "not_used", "key_sha256": None}
    output["excerpt"] = excerpt
    output["content_handling"]["contains_external_text"] = bool(
        excerpt["text"] is not None or (kind == "quote" and decoded)
    )
    output["row_sha256"] = _row_sha256(output)
    return validate(output, session_source_or_none if state in SOURCE_BOUND_STATES else None)


def _validate_v1_0(row: Mapping[str, Any], session_source_or_none: str | None = None) -> dict[str, Any]:
    """Return a deep-copied validated row; optionally replay source binding."""

    if not isinstance(row, Mapping):
        _fail("row", "must be a mapping")
    value = copy.deepcopy(dict(row))
    root_keys = {
        "schema_version", "surface", "row_id", "claim", "source", "anchor",
        "verdict", "detail", "excerpt", "cache", "content_handling", "row_sha256",
    }
    _closed(value, "row", root_keys)
    if value["schema_version"] != SCHEMA_VERSION:
        _fail("schema_version", f"must equal {SCHEMA_VERSION}")
    if value["surface"] != SURFACE:
        _fail("surface", f"must equal {SURFACE}")
    row_id = _string(value["row_id"], "row_id", minimum=1, maximum=200)
    if _ROW_ID_RE.fullmatch(row_id) is None:
        _fail("row_id", "does not match the EVR identifier grammar")

    claim = _closed(value["claim"], "claim", {"claim_id", "text", "paper_locator", "selection_tier"})
    _string(claim["claim_id"], "claim.claim_id", minimum=1, maximum=200)
    _string(claim["text"], "claim.text", minimum=1, maximum=2000)
    _string(claim["paper_locator"], "claim.paper_locator", minimum=1, maximum=500)
    _enum(claim["selection_tier"], "claim.selection_tier", SELECTION_TIERS)

    source = _closed(
        value["source"], "source",
        {"ref_slug", "display_label", "source_content_sha256", "source_content_utf8_bytes", "source_artifact_sha256"},
    )
    ref_slug = _nullable_string(source["ref_slug"], "source.ref_slug", minimum=1, maximum=300)
    if ref_slug is not None and _REF_SLUG_RE.fullmatch(ref_slug) is None:
        _fail("source.ref_slug", "does not match the citation slug grammar")
    _nullable_string(source["display_label"], "source.display_label", minimum=1, maximum=500)
    content_sha = _sha(source["source_content_sha256"], "source.source_content_sha256", nullable=True)
    content_length = source["source_content_utf8_bytes"]
    if content_length is not None:
        content_length = _integer(content_length, "source.source_content_utf8_bytes")
    _sha(source["source_artifact_sha256"], "source.source_artifact_sha256", nullable=True)

    anchor = _closed(value["anchor"], "anchor", {"kind", "value_encoded", "value_decoded"})
    kind = _enum(anchor["kind"], "anchor.kind", ANCHOR_KINDS)
    encoded = _string(anchor["value_encoded"], "anchor.value_encoded", maximum=12000)
    decoded = _string(anchor["value_decoded"], "anchor.value_decoded", maximum=TEXT_CHAR_CAP)
    if strict_percent_decode(encoded) != decoded:
        _fail("anchor.value_decoded", "must equal one strict percent decode of anchor.value_encoded")
    if kind == "none":
        if encoded or decoded:
            _fail("anchor", "kind=none requires empty encoded and decoded values")
    elif not decoded.strip():
        _fail("anchor.value_decoded", "non-none anchors require a non-empty decoded value")
    if kind == "quote":
        _bounded_external_text(decoded, "anchor.value_decoded")

    _enum(value["verdict"], "verdict", VERDICTS)
    _string(value["detail"], "detail", maximum=2000)

    excerpt = _closed(value["excerpt"], "excerpt", {"state", "text", "excerpt_sha256", "source_span_utf8", "captured_at"})
    state = _enum(excerpt["state"], "excerpt.state", EXCERPT_STATES)
    text_value = excerpt["text"]
    if text_value is not None:
        text_value = _bounded_external_text(text_value, "excerpt.text")
    excerpt_sha = _sha(excerpt["excerpt_sha256"], "excerpt.excerpt_sha256", nullable=True)
    span = excerpt["source_span_utf8"]
    if span is not None:
        span = _closed(span, "excerpt.source_span_utf8", {"start", "end"})
        start = _integer(span["start"], "excerpt.source_span_utf8.start")
        end = _integer(span["end"], "excerpt.source_span_utf8.end", minimum=1)
        if end <= start:
            _fail("excerpt.source_span_utf8", "end must be greater than start")
        if content_length is not None and end > content_length:
            _fail("excerpt.source_span_utf8.end", "exceeds source_content_utf8_bytes")
    captured = excerpt["captured_at"]
    if captured is not None:
        _timestamp(captured, "excerpt.captured_at")

    cache = _closed(value["cache"], "cache", {"status", "key_sha256"})
    cache_status = _enum(cache["status"], "cache.status", CACHE_STATUSES)
    cache_key = _sha(cache["key_sha256"], "cache.key_sha256", nullable=True)

    handling = _closed(value["content_handling"], "content_handling", {"contains_external_text", "sharing_scope", "rights_basis"})
    if not isinstance(handling["contains_external_text"], bool):
        _fail("content_handling.contains_external_text", "must be a boolean")
    sharing = _enum(handling["sharing_scope"], "content_handling.sharing_scope", SHARING_SCOPES)
    rights = _enum(handling["rights_basis"], "content_handling.rights_basis", RIGHTS_BASES)
    if (sharing == "user_confirmed_shareable") != (rights == "user_declared_authorized"):
        _fail("content_handling", "user-confirmed sharing and user-declared authorization must appear together")
    expected_external = bool(text_value is not None or (kind == "quote" and decoded))
    if handling["contains_external_text"] != expected_external:
        _fail("content_handling.contains_external_text", f"must equal derived value {expected_external}")

    if state == "verified_exact_match" and kind != "quote":
        _fail("excerpt.state", "verified_exact_match requires anchor.kind=quote")
    if state == "agent_extracted" and kind not in {"page", "section"}:
        _fail("excerpt.state", "agent_extracted requires page or section anchor")
    if state == "unconfirmed_anchor" and kind != "quote":
        _fail("excerpt.state", "unconfirmed_anchor requires anchor.kind=quote")
    if kind == "paragraph" and state != "not_checked":
        _fail("excerpt.state", "paragraph anchors are not_checked in V1")
    if kind == "none" and state != "anchorless":
        _fail("excerpt.state", "anchor.kind=none requires anchorless")
    if state == "anchorless" and kind != "none":
        _fail("excerpt.state", "anchorless requires anchor.kind=none")
    if kind in {"page", "section"} and state not in {"agent_extracted", "not_checked", "source_missing", "access_failed", "retrieval_failed"}:
        _fail("excerpt.state", f"is not permitted with anchor.kind={kind}")

    if state in EXCERPT_TEXT_STATES:
        if ref_slug is None:
            _fail("source.ref_slug", "positive excerpt states require a citation slug")
        if text_value is None or excerpt_sha is None or span is None or captured is None:
            _fail("excerpt", "positive excerpt states require text, digest, span, and captured_at")
        if content_sha is None or content_length is None:
            _fail("source", "positive excerpt states require source content digest and byte length")
        if excerpt_sha != _hash_text(text_value, "excerpt.text"):
            _fail("excerpt.excerpt_sha256", "does not match excerpt.text")
    else:
        if any(item is not None for item in (text_value, excerpt_sha, span, captured)):
            _fail("excerpt", f"state={state} requires explicit null text/hash/span/captured_at")

    if state == "verified_exact_match" and text_value != decoded:
        _fail("excerpt.text", "verified_exact_match must equal the once-decoded quote anchor byte-for-byte")
    if state == "unconfirmed_anchor":
        if ref_slug is None or content_sha is None or content_length is None:
            _fail("source", "unconfirmed_anchor requires ref_slug and source content binding")

    if state in SOURCE_BOUND_STATES:
        if cache_status not in {"miss", "hit"} or cache_key is None:
            _fail("cache", "source-bound states require miss/hit plus key_sha256")
        expected_key = _cache_key(
            content_sha,  # type: ignore[arg-type]
            kind,
            decoded,
            claim_id=claim["claim_id"],
            ref_slug=ref_slug,  # type: ignore[arg-type]
            state=state,
            excerpt_candidate_sha256=(excerpt_sha if state == "agent_extracted" else None),
        )
        if cache_key != expected_key:
            _fail("cache.key_sha256", "does not match the canonical source/anchor cache key")
    else:
        if content_sha is not None or content_length is not None:
            _fail("source", f"state={state} must not claim inspected source content")
        if cache_status != "not_used" or cache_key is not None:
            _fail("cache", f"state={state} requires not_used and null key")

    if session_source_or_none is not None:
        if not isinstance(session_source_or_none, str):
            _fail("session_source_or_none", "must be a string or null")
        if state in SOURCE_BOUND_STATES:
            source_bytes = _utf8(session_source_or_none, "session_source_or_none")
            if content_sha != _hash_bytes(source_bytes) or content_length != len(source_bytes):
                _fail("source", "content digest/length does not match the supplied session source")
            if state in EXCERPT_TEXT_STATES:
                assert isinstance(span, dict) and isinstance(text_value, str)
                text_bytes = _utf8(text_value, "excerpt.text")
                if source_bytes[span["start"] : span["end"]] != text_bytes:
                    _fail("excerpt.source_span_utf8", "does not select excerpt.text from the supplied source")
            elif decoded in session_source_or_none:
                _fail("excerpt.state", "unconfirmed_anchor is invalid because the decoded quote exactly matches the supplied source")

    digest = _sha(value["row_sha256"], "row_sha256")
    if digest != _row_sha256(value):
        _fail("row_sha256", "does not match canonical row content")
    return value


def _validate_v1_1(
    row: Mapping[str, Any], session_source_or_none: str | None = None
) -> dict[str, Any]:
    """Validate an evidence-row/1.1 carrier and optionally replay held content."""

    if not isinstance(row, Mapping):
        _fail("row", "must be a mapping")
    value = copy.deepcopy(dict(row))
    root_keys = {
        "schema_version",
        "surface",
        "row_id",
        "coverage_subject",
        "source",
        "anchor",
        "excerpt",
        "cache",
        "content_handling",
        "row_sha256",
    }
    _closed(value, "row", root_keys)
    if value["schema_version"] != ADVISORY_SCHEMA_VERSION:
        _fail("schema_version", f"must equal {ADVISORY_SCHEMA_VERSION}")
    if value["surface"] != ADVISORY_SURFACE:
        _fail("surface", f"must equal {ADVISORY_SURFACE}")
    row_id = _string(value["row_id"], "row_id", minimum=1, maximum=200)
    if _ROW_ID_RE.fullmatch(row_id) is None:
        _fail("row_id", "does not match the EVR identifier grammar")

    subject = _closed(
        value["coverage_subject"],
        "coverage_subject",
        {
            "requirement_id",
            "requirement_pointer",
            "authority_anchor_pointer",
            "expectation_field_id",
            "expectation_pointer",
            "expectation_digest",
            "document_locator",
        },
    )
    _authority_identifier(subject["requirement_id"], "coverage_subject.requirement_id")
    requirement_pointer = _json_pointer(
        subject["requirement_pointer"], "coverage_subject.requirement_pointer"
    )
    if re.fullmatch(r"/(?:profiles|overlays)/[0-9]+/requirements/[0-9]+", requirement_pointer) is None:
        _fail("coverage_subject.requirement_pointer", "must point to one exact requirement")
    authority_pointer = _json_pointer(
        subject["authority_anchor_pointer"], "coverage_subject.authority_anchor_pointer"
    )
    if authority_pointer != requirement_pointer + "/authority_anchor":
        _fail("coverage_subject.authority_anchor_pointer", "does not match requirement_pointer")
    _authority_identifier(
        subject["expectation_field_id"], "coverage_subject.expectation_field_id"
    )
    expectation_pointer = _json_pointer(
        subject["expectation_pointer"], "coverage_subject.expectation_pointer"
    )
    if re.fullmatch(
        re.escape(requirement_pointer) + r"/structured_expectations/[0-9]+",
        expectation_pointer,
    ) is None:
        _fail("coverage_subject.expectation_pointer", "does not belong to requirement_pointer")
    _sha(subject["expectation_digest"], "coverage_subject.expectation_digest")
    locator = _closed(
        subject["document_locator"],
        "coverage_subject.document_locator",
        {"kind", "value", "provenance"},
    )
    _enum(
        locator["kind"], "coverage_subject.document_locator.kind", DOCUMENT_LOCATOR_KINDS
    )
    _single_line(locator["value"], "coverage_subject.document_locator.value", maximum=500)
    if locator["provenance"] != DOCUMENT_LOCATOR_PROVENANCE:
        _fail(
            "coverage_subject.document_locator.provenance",
            f"must equal {DOCUMENT_LOCATOR_PROVENANCE}",
        )

    source = _closed(
        value["source"],
        "source",
        {
            "artifact_id",
            "relative_path",
            "source_artifact_sha256",
            "source_artifact_size_bytes",
            "source_content_sha256",
            "source_content_utf8_bytes",
        },
    )
    _authority_identifier(source["artifact_id"], "source.artifact_id")
    _advisory_relative_path(source["relative_path"], "source.relative_path")
    _sha(source["source_artifact_sha256"], "source.source_artifact_sha256")
    artifact_size = _integer(
        source["source_artifact_size_bytes"], "source.source_artifact_size_bytes"
    )
    if artifact_size > 64 * 1024 * 1024:
        _fail("source.source_artifact_size_bytes", "must be <= 67108864")
    content_sha = _sha(
        source["source_content_sha256"], "source.source_content_sha256", nullable=True
    )
    content_length = source["source_content_utf8_bytes"]
    if content_length is not None:
        content_length = _integer(content_length, "source.source_content_utf8_bytes")
        if content_length > 64 * 1024 * 1024:
            _fail("source.source_content_utf8_bytes", "must be <= 67108864")

    anchor = _closed(value["anchor"], "anchor", {"kind", "value_encoded", "value_decoded"})
    kind = _enum(anchor["kind"], "anchor.kind", ADVISORY_ANCHOR_KINDS)
    encoded = _string(anchor["value_encoded"], "anchor.value_encoded", maximum=12000)
    decoded = _string(anchor["value_decoded"], "anchor.value_decoded", maximum=TEXT_CHAR_CAP)
    if strict_percent_decode(encoded) != decoded:
        _fail("anchor.value_decoded", "must equal one strict percent decode of anchor.value_encoded")
    if kind == "none":
        if encoded or decoded:
            _fail("anchor", "kind=none requires empty encoded and decoded values")
    else:
        _bounded_external_text(decoded, "anchor.value_decoded")

    excerpt = _closed(
        value["excerpt"],
        "excerpt",
        {"state", "text", "excerpt_sha256", "source_span_utf8", "captured_at"},
    )
    state = _enum(excerpt["state"], "excerpt.state", ADVISORY_EXCERPT_STATES)
    text_value = excerpt["text"]
    if text_value is not None:
        text_value = _bounded_external_text(text_value, "excerpt.text")
    excerpt_sha = _sha(excerpt["excerpt_sha256"], "excerpt.excerpt_sha256", nullable=True)
    span = excerpt["source_span_utf8"]
    if span is not None:
        span = _closed(span, "excerpt.source_span_utf8", {"start", "end"})
        start = _integer(span["start"], "excerpt.source_span_utf8.start")
        end = _integer(span["end"], "excerpt.source_span_utf8.end", minimum=1)
        if end <= start:
            _fail("excerpt.source_span_utf8", "end must be greater than start")
        if content_length is not None and end > content_length:
            _fail("excerpt.source_span_utf8.end", "exceeds source_content_utf8_bytes")
    captured = excerpt["captured_at"]
    if captured is not None:
        _timestamp(captured, "excerpt.captured_at")

    cache = _closed(value["cache"], "cache", {"status", "key_sha256"})
    if cache != {"status": "not_used", "key_sha256": None}:
        _fail("cache", "evidence-row/1.1 requires not_used and null key_sha256")
    handling = _closed(
        value["content_handling"],
        "content_handling",
        {"contains_external_text", "sharing_scope", "rights_basis"},
    )
    if not isinstance(handling["contains_external_text"], bool):
        _fail("content_handling.contains_external_text", "must be a boolean")
    sharing = _enum(
        handling["sharing_scope"], "content_handling.sharing_scope", SHARING_SCOPES
    )
    rights = _enum(handling["rights_basis"], "content_handling.rights_basis", RIGHTS_BASES)
    if (sharing == "user_confirmed_shareable") != (
        rights == "user_declared_authorized"
    ):
        _fail(
            "content_handling",
            "user-confirmed sharing and user-declared authorization must appear together",
        )

    if state == "agent_extracted":
        if kind != "quote" or not decoded:
            _fail("anchor", "agent_extracted requires a non-empty quote anchor")
        if text_value != decoded:
            _fail("excerpt.text", "agent_extracted must equal the decoded quote anchor")
        if any(item is None for item in (content_sha, content_length, excerpt_sha, span, captured)):
            _fail(
                "excerpt",
                "agent_extracted requires source binding, text hash, span, and captured_at",
            )
        if excerpt_sha != _hash_text(text_value, "excerpt.text"):
            _fail("excerpt.excerpt_sha256", "does not match excerpt.text")
    elif state == "checked_no_match":
        if kind != "none" or content_sha is None or content_length is None:
            _fail("excerpt", "checked_no_match requires an empty anchor and source binding")
        if any(item is not None for item in (text_value, excerpt_sha, span, captured)):
            _fail("excerpt", "checked_no_match requires a null excerpt payload")
    else:
        if kind != "none":
            _fail("anchor.kind", f"state={state} requires anchor.kind=none")
        if content_sha is not None or content_length is not None:
            _fail("source", f"state={state} requires null source-content binding")
        if any(item is not None for item in (text_value, excerpt_sha, span, captured)):
            _fail("excerpt", f"state={state} requires a null excerpt payload")

    expected_external = state == "agent_extracted"
    if handling["contains_external_text"] != expected_external:
        _fail(
            "content_handling.contains_external_text",
            f"must equal derived value {expected_external}",
        )

    if session_source_or_none is not None:
        if not isinstance(session_source_or_none, str):
            _fail("session_source_or_none", "must be a string or null")
        if state in ADVISORY_SOURCE_BOUND_STATES:
            source_bytes = _utf8(session_source_or_none, "session_source_or_none")
            if len(source_bytes) > 64 * 1024 * 1024:
                _fail("session_source_or_none", "exceeds 67108864 UTF-8 bytes")
            if content_sha != _hash_bytes(source_bytes) or content_length != len(source_bytes):
                _fail("source", "content digest/length does not match the supplied session source")
            if state == "agent_extracted":
                assert isinstance(span, dict) and isinstance(text_value, str)
                if source_bytes[span["start"] : span["end"]] != _utf8(
                    text_value, "excerpt.text"
                ):
                    _fail(
                        "excerpt.source_span_utf8",
                        "does not select excerpt.text from the supplied source",
                    )
                if decoded not in session_source_or_none:
                    _fail("anchor.value_decoded", "does not occur in supplied source")
    digest = _sha(value["row_sha256"], "row_sha256")
    if digest != _row_sha256(value):
        _fail("row_sha256", "does not match canonical row content")
    return value


def validate(
    row: Mapping[str, Any], session_source_or_none: str | None = None
) -> dict[str, Any]:
    """Validate evidence-row/1.0 or evidence-row/1.1 without version coercion."""

    if not isinstance(row, Mapping):
        _fail("row", "must be a mapping")
    version = row.get("schema_version")
    if version == SCHEMA_VERSION:
        return _validate_v1_0(row, session_source_or_none)
    if version == ADVISORY_SCHEMA_VERSION:
        return _validate_v1_1(row, session_source_or_none)
    _fail(
        "schema_version",
        f"must equal {SCHEMA_VERSION} or {ADVISORY_SCHEMA_VERSION}",
    )


def paginate(
    rows: Sequence[Mapping[str, Any]],
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> dict[str, Any]:
    """Validate and return one deterministic, document-order page.

    Persistence is never capped or truncated.  A render call can expose at most
    25 rows, so even a 1001-row report remains accessible page by page without a
    resource-unbounded ``--all`` path.
    """

    if isinstance(rows, (str, bytes, bytearray)) or not isinstance(rows, Sequence):
        _fail("rows", "must be a sequence of evidence-row mappings")
    page = _integer(page, "page", minimum=1)
    page_size = _integer(page_size, "page_size", minimum=1)
    if page_size > MAX_PAGE_SIZE:
        _fail("page_size", f"must be <= {MAX_PAGE_SIZE}")

    validated: list[dict[str, Any]] = []
    row_ids: set[str] = set()
    anchors: set[tuple[Any, ...]] = set()
    claim_views: dict[str, tuple[dict[str, Any], str]] = {}
    row_version: str | None = None
    for index, raw in enumerate(rows):
        try:
            current = validate(raw)
        except EvidenceRowError as exc:
            _fail(f"rows[{index}]", str(exc))
        row_id = current["row_id"]
        if row_id in row_ids:
            _fail(f"rows[{index}].row_id", f"duplicate row_id {row_id!r}")
        row_ids.add(row_id)
        if row_version is None:
            row_version = current["schema_version"]
        elif current["schema_version"] != row_version:
            _fail("rows", "cannot mix evidence-row schema versions on one page")
        if current["schema_version"] == SCHEMA_VERSION:
            anchor_key = (
                current["claim"]["claim_id"],
                current["source"]["ref_slug"],
                current["anchor"]["kind"],
                current["anchor"]["value_decoded"],
            )
            duplicate_message = "duplicates an earlier (claim_id, ref_slug, anchor) row"
        else:
            anchor_key = (
                current["coverage_subject"]["requirement_id"],
                current["coverage_subject"]["expectation_pointer"],
                current["source"]["artifact_id"],
                current["anchor"]["kind"],
                current["anchor"]["value_decoded"],
            )
            duplicate_message = (
                "duplicates an earlier (requirement, expectation, artifact, anchor) row"
            )
        if anchor_key in anchors:
            _fail(f"rows[{index}]", duplicate_message)
        anchors.add(anchor_key)
        if current["schema_version"] == SCHEMA_VERSION:
            claim_id = current["claim"]["claim_id"]
            claim_view = (current["claim"], current["verdict"])
            previous_claim_view = claim_views.get(claim_id)
            if previous_claim_view is not None and previous_claim_view != claim_view:
                _fail(
                    f"rows[{index}].claim",
                    "rows sharing claim_id must carry the same closed claim object and claim-level verdict",
                )
            claim_views[claim_id] = claim_view
        validated.append(current)

    total_rows = len(validated)
    total_pages = max(1, (total_rows + page_size - 1) // page_size)
    if page > total_pages:
        _fail("page", f"{page} exceeds total_pages={total_pages}")
    start_index = (page - 1) * page_size
    end_index = min(start_index + page_size, total_rows)
    if total_rows == 0:
        row_start = 0
        row_end = 0
    else:
        row_start = start_index + 1
        row_end = end_index
    return {
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "total_rows": total_rows,
        "row_start": row_start,
        "row_end": row_end,
        "has_previous": page > 1,
        "has_next": page < total_pages,
        "truncated": False,
        "rows": validated[start_index:end_index],
    }


_BIDI_CONTROL_CODES = frozenset(
    {
        0x061C,
        0x200E,
        0x200F,
        0x202A,
        0x202B,
        0x202C,
        0x202D,
        0x202E,
        0x2066,
        0x2067,
        0x2068,
        0x2069,
    }
)


def _visible_single_line(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    parts: list[str] = []
    for char in text:
        code = ord(char)
        if char == "\n":
            parts.append(" ␤ ")
        elif char == "\t":
            parts.append(" ⇥ ")
        elif (
            code in _BIDI_CONTROL_CODES
            or code in {0x2028, 0x2029}
            or unicodedata.category(char) in {"Cc", "Cf"}
        ):
            escape = f"\\u{code:04X}" if code <= 0xFFFF else f"\\U{code:08X}"
            parts.append(escape)
        else:
            parts.append(char)
    return "".join(parts)


def _markdown_escape(value: Any) -> str:
    # HTML escaping first prevents raw tags/autolinks.  Backslash escaping then
    # neutralizes CommonMark table, link/image, emphasis, code, heading, and list
    # syntax.  Newlines were already rendered as a visible data glyph.
    text = html.escape(_visible_single_line(value), quote=True)
    text = text.replace("\\", "\\\\")
    # Colon, slash, and at-sign are included to disable GFM bare URL/email
    # autolinking as well as explicit CommonMark link syntax.
    for char in "`*{}_[]()#+-.!|>~:/@":
        text = text.replace(char, "\\" + char)
    return text


def _html_escape(value: Any) -> str:
    return html.escape(_visible_single_line(value), quote=True)


def _source_display(row: Mapping[str, Any]) -> str:
    source = row["source"]
    label = source["display_label"] or "(source label unavailable)"
    slug = source["ref_slug"] or "(no ref slug)"
    digest = source["source_content_sha256"]
    suffix = f"; content sha256 {digest}" if digest else ""
    return f"{label} [{slug}]{suffix}"


def _anchor_display(row: Mapping[str, Any]) -> str:
    anchor = row["anchor"]
    if anchor["kind"] == "none":
        return "none"
    return f"{anchor['kind']}:{anchor['value_decoded']}"


def _evidence_display(row: Mapping[str, Any]) -> str:
    state = row["excerpt"]["state"]
    label = STATE_LABELS[state]
    excerpt = row["excerpt"]["text"]
    if excerpt is not None:
        return f'{label} — "{excerpt}"'
    if row["anchor"]["kind"] == "quote" and row["anchor"]["value_decoded"]:
        return (
            f'{label} — NO EXCERPT; writer-emitted anchor remains unconfirmed: '
            f'"{row["anchor"]["value_decoded"]}"'
        )
    return f"{label} — NO EXCERPT"


_HANDLING_CAVEAT = (
    "External quote anchors and excerpts are limited to 25 words and 1000 Unicode code points each, "
    "and remain session-only unless the user explicitly confirmed sharing rights. "
    "Those limits are data minimization, not a rights determination. Viewing an "
    "evidence row is not a human-read attestation. Evidence labels describe excerpt "
    "provenance only, never whether the claim is supported."
)


def _rows_replayed_for_render(
    rows: Sequence[Mapping[str, Any]],
    session_sources: Mapping[str, str] | None,
) -> list[dict[str, Any]]:
    if isinstance(rows, (str, bytes, bytearray)) or not isinstance(rows, Sequence):
        _fail("rows", "must be a sequence of evidence-row mappings")
    if session_sources is not None and not isinstance(session_sources, Mapping):
        _fail("session_sources", "must be a mapping from ref_slug to exact source text")

    replayed: list[dict[str, Any]] = []
    for index, raw in enumerate(rows):
        try:
            current = validate(raw)
        except EvidenceRowError as exc:
            _fail(f"rows[{index}]", str(exc))
        advisory = current["schema_version"] == ADVISORY_SCHEMA_VERSION
        source_bound = current["excerpt"]["state"] in (
            ADVISORY_SOURCE_BOUND_STATES if advisory else SOURCE_BOUND_STATES
        )
        if source_bound:
            source_key = (
                current["source"]["artifact_id"]
                if advisory
                else current["source"]["ref_slug"]
            )
            if session_sources is None or source_key not in session_sources:
                _fail(
                    (
                        f"rows[{index}].source.artifact_id"
                        if advisory
                        else f"rows[{index}].source.ref_slug"
                    ),
                    f"source-bound row requires {source_key!r} in session_sources",
                )
            source_text = session_sources[source_key]
            if not isinstance(source_text, str):
                _fail(
                    f"session_sources.{source_key}",
                    "must be an exact source-text string",
                )
            try:
                current = validate(current, source_text)
            except EvidenceRowError as exc:
                _fail(f"rows[{index}] source replay", str(exc))
        replayed.append(current)
    return replayed


def _navigation_text(paged: Mapping[str, Any]) -> str:
    previous = str(paged["page"] - 1) if paged["has_previous"] else "none"
    following = str(paged["page"] + 1) if paged["has_next"] else "none"
    return (
        f"Navigation: Previous page {previous}; Next page {following}; "
        f"Explicit page range 1–{paged['total_pages']} (current {paged['page']})."
    )


def _render_advisory_markdown_page(paged: Mapping[str, Any]) -> str:
    lines = [
        f"### LLM-ADVISORY content-coverage evidence rows — Page {paged['page']}/{paged['total_pages']}",
        "",
        f"Rows {paged['row_start']}–{paged['row_end']} of {paged['total_rows']}.",
        "",
        _navigation_text(paged),
        "",
        _markdown_escape(
            "LLM-ADVISORY: passages are bounded evaluator-supplied observations, not adequacy, authorization, institutional acceptance, or an efficacy measurement."
        ),
        "",
        "| Row | Requirement | Expectation | Artifact | Document locator | Evidence state | Evidence | Handling |",
        "|---|---|---|---|---|---|---|---|",
    ]
    if not paged["rows"]:
        lines.append("| — | No evidence rows on this page. | — | — | — | — | — | — |")
    else:
        for row in paged["rows"]:
            subject = row["coverage_subject"]
            locator = subject["document_locator"]
            excerpt = row["excerpt"]
            evidence = excerpt["text"] if excerpt["text"] is not None else "NO EXCERPT"
            cells = [
                row["row_id"],
                subject["requirement_id"],
                f"{subject['expectation_field_id']} [{subject['expectation_pointer']}]",
                f"{row['source']['artifact_id']} [{row['source']['relative_path']}]",
                f"{locator['kind']}:{locator['value']} ({locator['provenance']})",
                excerpt["state"],
                evidence,
                (
                    f"{row['content_handling']['sharing_scope']} / "
                    f"{row['content_handling']['rights_basis']}"
                ),
            ]
            lines.append("| " + " | ".join(_markdown_escape(cell) for cell in cells) + " |")
    return "\n".join(lines) + "\n"


def _render_advisory_html_page(paged: Mapping[str, Any]) -> str:
    parts = [
        (
            f'<section class="ars-evidence-rows ars-content-coverage-advisory" '
            f'data-layer="LLM-ADVISORY" data-page="{paged["page"]}" '
            f'data-total-pages="{paged["total_pages"]}">'
        ),
        f"<h3>LLM-ADVISORY content-coverage evidence rows — Page {paged['page']}/{paged['total_pages']}</h3>",
        f"<p>Rows {paged['row_start']}–{paged['row_end']} of {paged['total_rows']}.</p>",
        (
            '<nav class="ars-evidence-navigation" aria-label="Evidence row page navigation">'
            f"{_html_escape(_navigation_text(paged))}</nav>"
        ),
        (
            '<p class="ars-evidence-caveat">'
            + _html_escape(
                "LLM-ADVISORY: passages are bounded evaluator-supplied observations, not adequacy, authorization, institutional acceptance, or an efficacy measurement."
            )
            + "</p>"
        ),
        "<table>",
        (
            "<thead><tr><th>Row</th><th>Requirement</th><th>Expectation</th>"
            "<th>Artifact</th><th>Document locator</th><th>Evidence state</th>"
            "<th>Evidence</th><th>Handling</th></tr></thead>"
        ),
        "<tbody>",
    ]
    if not paged["rows"]:
        parts.append('<tr><td colspan="8">No evidence rows on this page.</td></tr>')
    else:
        for row in paged["rows"]:
            subject = row["coverage_subject"]
            locator = subject["document_locator"]
            excerpt = row["excerpt"]
            evidence = excerpt["text"] if excerpt["text"] is not None else "NO EXCERPT"
            cells = [
                row["row_id"],
                subject["requirement_id"],
                f"{subject['expectation_field_id']} [{subject['expectation_pointer']}]",
                f"{row['source']['artifact_id']} [{row['source']['relative_path']}]",
                f"{locator['kind']}:{locator['value']} ({locator['provenance']})",
                excerpt["state"],
                evidence,
                (
                    f"{row['content_handling']['sharing_scope']} / "
                    f"{row['content_handling']['rights_basis']}"
                ),
            ]
            parts.append(f'<tr data-evidence-state="{_html_escape(excerpt["state"])}">')
            parts.extend(f"<td>{_html_escape(cell)}</td>" for cell in cells)
            parts.append("</tr>")
    parts.extend(["</tbody>", "</table>", "</section>"])
    return "\n".join(parts) + "\n"


def render_markdown(
    rows: Sequence[Mapping[str, Any]],
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    *,
    session_sources: Mapping[str, str] | None = None,
) -> str:
    """Render one replay-validated page as inert Markdown without retrieval."""

    replayed = _rows_replayed_for_render(rows, session_sources)
    paged = paginate(replayed, page=page, page_size=page_size)
    if replayed and replayed[0]["schema_version"] == ADVISORY_SCHEMA_VERSION:
        return _render_advisory_markdown_page(paged)
    lines = [
        f"### Phase E evidence rows — Page {paged['page']}/{paged['total_pages']}",
        "",
        f"Rows {paged['row_start']}–{paged['row_end']} of {paged['total_rows']}.",
        "",
        _navigation_text(paged),
        "",
        _markdown_escape(_HANDLING_CAVEAT),
        "",
        "| Row | Claim | Paper locator | Source | Anchor | Tier | Phase E claim verdict (unchanged) | Detail | Evidence | Handling |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    if not paged["rows"]:
        lines.append("| — | No evidence rows on this page. | — | — | — | — | — | — | — | — |")
    else:
        for row in paged["rows"]:
            cells = [
                row["row_id"],
                f"{row['claim']['claim_id']}: {row['claim']['text']}",
                row["claim"]["paper_locator"],
                _source_display(row),
                _anchor_display(row),
                row["claim"]["selection_tier"],
                row["verdict"],
                row["detail"],
                _evidence_display(row),
                (
                    f"{row['content_handling']['sharing_scope']} / "
                    f"{row['content_handling']['rights_basis']}"
                ),
            ]
            lines.append("| " + " | ".join(_markdown_escape(cell) for cell in cells) + " |")
    return "\n".join(lines) + "\n"


def render_html(
    rows: Sequence[Mapping[str, Any]],
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    *,
    session_sources: Mapping[str, str] | None = None,
) -> str:
    """Render one replay-validated page as escaped HTML without retrieval."""

    replayed = _rows_replayed_for_render(rows, session_sources)
    paged = paginate(replayed, page=page, page_size=page_size)
    if replayed and replayed[0]["schema_version"] == ADVISORY_SCHEMA_VERSION:
        return _render_advisory_html_page(paged)
    parts = [
        (
            f'<section class="ars-evidence-rows" data-page="{paged["page"]}" '
            f'data-total-pages="{paged["total_pages"]}">'
        ),
        f"<h3>Phase E evidence rows — Page {paged['page']}/{paged['total_pages']}</h3>",
        f"<p>Rows {paged['row_start']}–{paged['row_end']} of {paged['total_rows']}.</p>",
        (
            '<nav class="ars-evidence-navigation" aria-label="Evidence row page navigation" '
            f'data-has-previous="{str(paged["has_previous"]).lower()}" '
            f'data-has-next="{str(paged["has_next"]).lower()}">'
            f"{_html_escape(_navigation_text(paged))}</nav>"
        ),
        f'<p class="ars-evidence-caveat">{_html_escape(_HANDLING_CAVEAT)}</p>',
        "<table>",
        (
            "<thead><tr><th>Row</th><th>Claim</th><th>Paper locator</th>"
            "<th>Source</th><th>Anchor</th><th>Tier</th><th>Phase E claim verdict (unchanged)</th>"
            "<th>Detail</th><th>Evidence</th><th>Handling</th></tr></thead>"
        ),
        "<tbody>",
    ]
    if not paged["rows"]:
        parts.append('<tr><td colspan="10">No evidence rows on this page.</td></tr>')
    else:
        for row in paged["rows"]:
            cells = [
                row["row_id"],
                f"{row['claim']['claim_id']}: {row['claim']['text']}",
                row["claim"]["paper_locator"],
                _source_display(row),
                _anchor_display(row),
                row["claim"]["selection_tier"],
                row["verdict"],
                row["detail"],
                _evidence_display(row),
                (
                    f"{row['content_handling']['sharing_scope']} / "
                    f"{row['content_handling']['rights_basis']}"
                ),
            ]
            state = _html_escape(row["excerpt"]["state"])
            parts.append(f'<tr data-evidence-state="{state}">')
            parts.extend(f"<td>{_html_escape(cell)}</td>" for cell in cells)
            parts.append("</tr>")
    parts.extend(["</tbody>", "</table>", "</section>"])
    return "\n".join(parts) + "\n"


def _no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _input_fail("JSON", f"duplicate key {key!r}")
        result[key] = value
    return result


def _reject_excessive_json_nesting(text: str, path: Path) -> None:
    """Apply one parser-independent nesting limit before strict JSON decoding."""
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
            if depth > MAX_JSON_NESTING:
                _input_fail(
                    str(path),
                    (
                        "cannot read strict JSON: nesting depth exceeds "
                        f"{MAX_JSON_NESTING}"
                    ),
                )
        elif character in "]}" and depth:
            depth -= 1


def _load_json(path: Path) -> Any:
    try:
        text = path.read_text(encoding="utf-8")
        _reject_excessive_json_nesting(text, path)
        return json.loads(
            text,
            object_pairs_hook=_no_duplicate_object,
            parse_constant=lambda token: _input_fail("JSON", f"non-finite number {token!r} is forbidden"),
        )
    except EvidenceRowError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, RecursionError) as exc:
        _input_fail(str(path), f"cannot read strict JSON: {exc}")


def _validate_report_claim_summary(
    e_claims: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
) -> None:
    has_checked = "checked" in e_claims
    has_verified = "verified" in e_claims
    if not has_checked or not has_verified:
        _fail(
            "phases.E_claims",
            "a current report with evidence_rows requires integer checked and verified counters",
        )

    checked = _integer(e_claims["checked"], "phases.E_claims.checked")
    verified = _integer(e_claims["verified"], "phases.E_claims.verified")
    # This validates every row and enforces row/semantic-anchor uniqueness plus
    # a single claim object and verdict for each repeated claim_id.
    paginate(rows)
    claim_verdicts: dict[str, str] = {}
    for row in rows:
        claim_id = row["claim"]["claim_id"]
        claim_verdicts[claim_id] = row["verdict"]
    if len(claim_verdicts) != checked:
        _fail(
            "phases.E_claims.checked",
            f"is {checked}, but evidence_rows contains {len(claim_verdicts)} unique selected claim_id(s)",
        )
    verified_count = sum(verdict == "VERIFIED" for verdict in claim_verdicts.values())
    if verified_count != verified:
        _fail(
            "phases.E_claims.verified",
            f"is {verified}, but evidence_rows contains {verified_count} unique VERIFIED claim_id(s)",
        )


def _refuse_advisory_rows(rows: Sequence[Any], path: str) -> None:
    """The CLI handles V1 rows only; name the advisory entry point (#947)."""
    for index, row in enumerate(rows):
        if isinstance(row, Mapping) and row.get("schema_version") == ADVISORY_SCHEMA_VERSION:
            _input_fail(
                f"{path}[{index}]",
                f"is an {ADVISORY_SCHEMA_VERSION} advisory row, which this CLI does not "
                "handle; use scripts/build_content_coverage_advisory.py "
                "(shared/references/authority_content_coverage_advisory_protocol.md)",
            )


def _rows_from_document(
    document: Any,
    *,
    allow_legacy_absence: bool = False,
) -> list[Mapping[str, Any]] | None:
    if isinstance(document, list):
        _refuse_advisory_rows(document, "rows")
        return document
    if isinstance(document, dict) and document.get("schema_version") == ADVISORY_SCHEMA_VERSION:
        _refuse_advisory_rows([document], "rows")
    if isinstance(document, dict) and document.get("schema_version") == SCHEMA_VERSION:
        return [document]
    if isinstance(document, dict):
        try:
            e_claims = document["phases"]["E_claims"]
        except (KeyError, TypeError):
            _fail("input", "must be an evidence-row object, row array, or Integrity Report with phases.E_claims.evidence_rows")
        if not isinstance(e_claims, dict):
            _fail("phases.E_claims", "must be an object")
        if "evidence_rows" not in e_claims:
            if allow_legacy_absence:
                return None
            _fail(
                "phases.E_claims.evidence_rows",
                "is absent; current evidence-row contract validation is unavailable",
            )
        rows = e_claims["evidence_rows"]
        if not isinstance(rows, list):
            _fail("phases.E_claims.evidence_rows", "must be an array")
        _refuse_advisory_rows(rows, "phases.E_claims.evidence_rows")
        _validate_report_claim_summary(e_claims, rows)
        return rows
    _fail("input", "must be a JSON object or array")


def _source_map(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    document = _load_json(path)
    if not isinstance(document, dict):
        _fail("source map", "must be an object mapping ref_slug to exact source text")
    result: dict[str, str] = {}
    for key, value in document.items():
        if not isinstance(key, str) or _REF_SLUG_RE.fullmatch(key) is None:
            _fail("source map", f"invalid ref_slug key {key!r}")
        if not isinstance(value, str):
            _fail(f"source map.{key}", "must be a string")
        result[key] = value
    return result


_WINDOWS_RESERVED_NAMES = frozenset(
    {"con", "prn", "aux", "nul"}
    | {f"{device}{digit}" for device in ("com", "lpt") for digit in "123456789"}
)


def source_file_name(source_key: str) -> str:
    """File name of one source's text inside a ``--source-dir`` folder (#933).

    The ref_slug with ``:`` written ``%3A`` (invalid in Windows names), each
    capital letter written ``^`` plus its lowercase form (so ``Smith2024`` and
    ``smith2024`` stay apart on case-insensitive file systems), and ``~``
    after a name Windows reserves (``con``, ``nul``, ``com1``, ...), then
    ``.txt``. ``%``, ``^``, and ``~`` cannot occur in a ref_slug, so distinct
    slugs always get distinct names.
    """
    if not isinstance(source_key, str) or _REF_SLUG_RE.fullmatch(source_key) is None:
        _input_fail("source dir", f"invalid ref_slug {source_key!r}")
    name = "".join(
        "%3A" if char == ":" else f"^{char.lower()}" if "A" <= char <= "Z" else char
        for char in source_key
    )
    if name in _WINDOWS_RESERVED_NAMES:
        name += "~"
    return name + ".txt"


def _source_dir(path: Path, rows: Sequence[Any]) -> dict[str, str]:
    """Read the source texts that the rows' source-bound entries name (#933).

    Covers V1 Phase E rows, keyed by ``ref_slug``; advisory rows keep their
    own in-memory API. Only ``<folder>/<source_file_name(slug)>`` is read for
    each slug a source-bound V1 row names; no other file in the folder is
    opened. Each file is read as exact bytes and decoded as strict UTF-8,
    with no newline translation, because replay hashes the exact text. A slug
    with no file is left out, so replay fails for it as for a missing
    source-map entry.
    """
    try:
        if path.is_symlink() or not path.is_dir():
            _input_fail(str(path), "is not a folder")
    except OSError as exc:
        _input_fail(str(path), f"cannot inspect folder: {exc}")
    slugs: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping) or row.get("schema_version") != SCHEMA_VERSION:
            continue
        source = row.get("source")
        excerpt = row.get("excerpt")
        if not isinstance(source, Mapping) or not isinstance(excerpt, Mapping):
            continue
        slug, state = source.get("ref_slug"), excerpt.get("state")
        if (isinstance(state, str) and state in SOURCE_BOUND_STATES
                and isinstance(slug, str) and _REF_SLUG_RE.fullmatch(slug)):
            slugs.add(slug)
    result: dict[str, str] = {}
    for slug in sorted(slugs):
        target = path / source_file_name(slug)
        try:
            # One lstat: it does not follow a link, and it raises the same
            # error for an over-long name on every platform (exists() hides it).
            mode = target.lstat().st_mode
        except FileNotFoundError:
            continue
        except OSError as exc:
            _input_fail(str(target), f"cannot inspect source file: {exc}")
        if not stat.S_ISREG(mode):
            _input_fail(str(target), "must be a regular file, not a link or folder")
        try:
            result[slug] = target.read_bytes().decode("utf-8")
        except (OSError, UnicodeError) as exc:
            _input_fail(str(target), f"cannot read exact UTF-8 source text: {exc}")
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    sub = parser.add_subparsers(dest="command", required=True)
    validate_parser = sub.add_parser(
        "validate",
        help="validate persisted evidence rows",
        allow_abbrev=False,
    )
    validate_parser.add_argument("rows", type=Path)
    validate_sources = validate_parser.add_mutually_exclusive_group()
    validate_sources.add_argument("--source-map", type=Path)
    validate_sources.add_argument("--source-dir", type=Path)
    render_parser = sub.add_parser(
        "render",
        help="render one persisted evidence-row page",
        allow_abbrev=False,
    )
    render_parser.add_argument("rows", type=Path)
    render_parser.add_argument("--format", choices=("markdown", "html"), required=True)
    render_sources = render_parser.add_mutually_exclusive_group()
    render_sources.add_argument(
        "--source-map",
        type=Path,
        help="explicit ref_slug-to-source-text JSON used only for source replay",
    )
    render_sources.add_argument(
        "--source-dir",
        type=Path,
        help=(
            "folder of source texts named by source_file_name(ref_slug), used only "
            "for source replay; only the files the source-bound rows name are read"
        ),
    )
    render_parser.add_argument(
        "--allow-legacy-absence",
        action="store_true",
        help=(
            "explicitly treat an Integrity Report with no evidence_rows field as "
            "a pre-#656 legacy artifact and render the fixed unavailable marker"
        ),
    )
    render_parser.add_argument("--page", type=int, default=1)
    render_parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        rows = _rows_from_document(
            _load_json(args.rows),
            allow_legacy_absence=(
                args.command == "render"
                and bool(getattr(args, "allow_legacy_absence", False))
            ),
        )
        if rows is None:
            if args.format == "markdown":
                sys.stdout.write(LEGACY_UNAVAILABLE_LABEL + "\n")
            else:
                sys.stdout.write(
                    '<p class="ars-evidence-rows-legacy">'
                    + _html_escape(LEGACY_UNAVAILABLE_LABEL)
                    + "</p>\n"
                )
            return 0
        sources = (
            _source_dir(args.source_dir, rows)
            if args.source_dir is not None
            else _source_map(args.source_map)
        )
        if args.command == "validate":
            seen: list[dict[str, Any]] = []
            for index, row in enumerate(rows):
                if not isinstance(row, Mapping):
                    _fail(f"rows[{index}]", "must be an object")
                slug = row.get("source", {}).get("ref_slug") if isinstance(row.get("source"), dict) else None
                state = row.get("excerpt", {}).get("state") if isinstance(row.get("excerpt"), dict) else None
                slug = slug if isinstance(slug, str) else None
                if isinstance(state, str) and state in SOURCE_BOUND_STATES and slug not in sources:
                    _fail(
                        f"rows[{index}].source.ref_slug",
                        f"source-bound row requires {slug!r} in --source-map or --source-dir "
                        "for CLI trust establishment",
                    )
                seen.append(validate(row, sources.get(slug)))
            paginate(seen)
            print(f"PASS: {len(seen)} evidence row(s)")
            return 0
        if args.format == "markdown":
            sys.stdout.write(
                render_markdown(
                    rows,
                    page=args.page,
                    page_size=args.page_size,
                    session_sources=sources,
                )
            )
        else:
            sys.stdout.write(
                render_html(
                    rows,
                    page=args.page,
                    page_size=args.page_size,
                    session_sources=sources,
                )
            )
        return 0
    except EvidenceRowInputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except EvidenceRowError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


__all__ = [
    "ADVISORY_EXCERPT_STATES",
    "ADVISORY_SCHEMA_VERSION",
    "ADVISORY_SURFACE",
    "ANCHOR_KINDS",
    "DEFAULT_PAGE_SIZE",
    "EvidenceRowError",
    "EvidenceRowInputError",
    "EXCERPT_STATES",
    "LEGACY_UNAVAILABLE_LABEL",
    "MAX_PAGE_SIZE",
    "QUOTE_WORD_CAP",
    "SCHEMA_VERSION",
    "STATE_LABELS",
    "SURFACE",
    "TEXT_CHAR_CAP",
    "build",
    "build_advisory",
    "main",
    "paginate",
    "render_html",
    "render_markdown",
    "source_file_name",
    "strict_percent_decode",
    "validate",
]


if __name__ == "__main__":
    raise SystemExit(main())
