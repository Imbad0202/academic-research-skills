#!/usr/bin/env python3
"""Hermetic tortured-phrase risk-marker screening for issue #660.

The runtime consumes only explicitly named local inputs.  It never downloads a
phrase list, dereferences a corpus pointer, invokes a model, judges authorship,
or rewrites manuscript text.  A deterministic match is carried as a heuristic
advisory because a curated-list hit is only a risk marker.

CLI exit codes: 0 success, 1 fail-closed contract/replay error, 2 invocation
error.  A snapshot failure still writes an explicit degraded/not-checked
artifact when an output path was supplied; it never becomes a clean result.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import html
import json
import math
import os
import re
import sys
import tempfile
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from io import StringIO
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator
from ruamel.yaml import YAML

if __package__:
    from .bibliographic_integrity_signals import (
        _validate_tortured_phrase_projection as _validate_existing_phrase_projection,
    )
else:
    from bibliographic_integrity_signals import (
        _validate_tortured_phrase_projection as _validate_existing_phrase_projection,
    )


REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_SCHEMA_PATH = (
    REPO_ROOT / "shared/contracts/audit/tortured_phrase_snapshot.schema.json"
)
MANIFEST_SCHEMA_PATH = (
    REPO_ROOT
    / "shared/contracts/audit/tortured_phrase_snapshot_manifest.schema.json"
)
ADVISORY_SCHEMA_PATH = (
    REPO_ROOT / "shared/contracts/audit/tortured_phrase_advisory.schema.json"
)
SIGNAL_SCHEMA_PATH = (
    REPO_ROOT
    / "shared/contracts/passport/bibliographic_integrity_signal.schema.json"
)
CORPUS_ENTRY_SCHEMA_PATH = (
    REPO_ROOT / "shared/contracts/passport/literature_corpus_entry.schema.json"
)

SNAPSHOT_VERSION = "tortured-phrase-snapshot/1.0"
MANIFEST_VERSION = "tortured-phrase-snapshot-manifest/1.0"
ADVISORY_VERSION = "tortured-phrase-advisory/1.0"
SIGNAL_VERSION = "bibliographic-integrity-signal/1.2"
GRAMMAR_PROFILE = "ars-tortured-phrase-canonical-ast/1.0"
NORMALIZER_PROFILE = "ars-nfkc-casefold-token/1.0"
LAYER = "HEURISTIC-ADVISORY"
EVALUATION_STATUS = "UNMEASURED"
SUMMARY_LABEL = "Phrase-list match requiring review"
ADVISORY_LABEL = "Phrase-list screening advisory"

MAX_SNAPSHOT_BYTES = 2 * 1024 * 1024
MAX_MANIFEST_BYTES = 512 * 1024
MAX_DOCUMENT_BYTES = 8 * 1024 * 1024
MAX_PASSPORT_BYTES = 16 * 1024 * 1024
MAX_ADVISORY_BYTES = 32 * 1024 * 1024
MAX_RULES = 512
MAX_AST_DEPTH = 12
MAX_AST_NODES = 64
MAX_LITERAL_TOKENS = 8
MAX_NODE_WITNESSES = 512
MAX_NODE_COMBINATIONS = 100_000
MAX_RULE_SEGMENT_EVALUATIONS = 100_000
MAX_MATCH_WORK_UNITS = 5_000_000
MAX_REPORT_MATCHES = 4096
MAX_CORPUS_OUTPUT_MATCHES = 4096
MAX_CORPUS_ENTRIES = 512
MAX_CORPUS_EXISTING_SIGNALS = 8192
MAX_STRUCTURE_DEPTH = 64
MAX_STRUCTURE_NODES = 200_000
MAX_SEGMENTS = 4096
MAX_PARSE_INTERVALS = 4096
MAX_PARSE_WORK_UNITS = 100_000
MAX_TOKENS = 500_000
MAX_RAW_TOKEN_CODEPOINTS = 4096
MAX_EVIDENCE_WORDS = 25
MAX_EVIDENCE_CODEPOINTS = 1000
MAX_RENDER_PAGE_SIZE = 25

CONTEXTS = (
    "author_prose",
    "quote",
    "cited_title",
    "reference_entry",
    "code_or_verbatim",
    "unknown",
    "cited_abstract",
)
PROTECTED_CONTEXTS = frozenset(
    {"quote", "cited_title", "reference_entry", "code_or_verbatim"}
)

_RFC3339_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt]"
    r"(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
    r"(?:\.[0-9]{1,6})?(?:[Zz]|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])$"
)
_SHA_RE = re.compile(r"^[0-9a-f]{64}$")
_SAFE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_DASHES = frozenset(
    {
        "-",
        "\u058a",
        "\u05be",
        "\u1400",
        "\u1806",
        "\u2010",
        "\u2011",
        "\u2012",
        "\u2013",
        "\u2014",
        "\u2015",
        "\u2e17",
        "\u2e1a",
        "\u2e3a",
        "\u2e3b",
        "\u2e40",
        "\u301c",
        "\u3030",
        "\u30a0",
        "\ufe31",
        "\ufe32",
        "\ufe58",
        "\ufe63",
        "\uff0d",
    }
)


class ScreeningError(ValueError):
    """A named input or derived artifact violates the #660 contract."""


class SnapshotLoadError(ScreeningError):
    """The supplied snapshot cannot authorize a checked result."""

    def __init__(
        self,
        reason_code: str,
        message: str,
        *,
        snapshot_sha256: str | None = None,
        manifest_sha256: str | None = None,
    ) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.snapshot_sha256 = snapshot_sha256
        self.manifest_sha256 = manifest_sha256


class MatchLimitError(ScreeningError):
    """A bounded matcher resource ceiling was exceeded."""


@dataclass
class MatchWorkBudget:
    """One shared operation budget for a complete surface scan."""

    remaining: int = field(default_factory=lambda: MAX_MATCH_WORK_UNITS)

    def spend(self, units: int) -> None:
        if units < 0 or units > self.remaining:
            raise MatchLimitError(
                f"matcher work exceeds {MAX_MATCH_WORK_UNITS} units"
            )
        self.remaining -= units


@dataclass
class ParseWorkBudget:
    """One shared delimiter/context-candidate budget for a complete document."""

    remaining: int = field(default_factory=lambda: MAX_PARSE_WORK_UNITS)

    def spend(self, units: int = 1) -> None:
        if units < 0 or units > self.remaining:
            raise MatchLimitError(
                f"parser work exceeds {MAX_PARSE_WORK_UNITS} units"
            )
        self.remaining -= units


@dataclass(frozen=True)
class Token:
    normalized: str
    start: int
    end: int


@dataclass(frozen=True, order=True)
class Witness:
    token_start: int
    token_end: int
    codepoint_start: int
    codepoint_end: int


@dataclass(frozen=True)
class Segment:
    segment_id: str
    kind: str
    start: int
    end: int


@dataclass(frozen=True, order=True)
class OpaqueOpener:
    """One lexical opener used by the source-order opaque parser."""

    start: int
    priority: int
    opener_end: int
    syntax: str
    payload: tuple[Any, ...] = ()


@dataclass(frozen=True)
class CompiledRule:
    rule_id: str
    expression: dict[str, Any]
    exclude_if: tuple[dict[str, Any], ...]
    rule_sha256: str
    semantic_key: str


@dataclass(frozen=True)
class SnapshotBundle:
    snapshot: dict[str, Any]
    manifest: dict[str, Any]
    snapshot_sha256: str
    manifest_sha256: str
    rules: tuple[CompiledRule, ...]
    unicode_data_version: str


@dataclass(frozen=True)
class SnapshotState:
    status: str
    reason_code: str
    bundle: SnapshotBundle | None
    snapshot_sha256: str | None
    manifest_sha256: str | None
    detail: str | None


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8", errors="strict"))


def _canonical_json(value: Any) -> str:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise ScreeningError(f"value cannot be serialized canonically: {exc}") from exc


def _pretty_json_bytes(value: Any) -> bytes:
    try:
        return (
            json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        ).encode("utf-8", errors="strict")
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise ScreeningError(f"value cannot be serialized as strict JSON: {exc}") from exc


def _timestamp(value: Any, field: str) -> str:
    if not isinstance(value, str) or _RFC3339_RE.fullmatch(value) is None:
        raise ScreeningError(f"{field} must be an explicit RFC 3339 date-time")
    candidate = value[:-1] + "+00:00" if value[-1] in {"Z", "z"} else value
    try:
        parsed = dt.datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ScreeningError(f"{field} is not a valid RFC 3339 date-time: {exc}") from exc
    if parsed.tzinfo is None:
        raise ScreeningError(f"{field} must carry a UTC offset")
    return value


def _timestamp_instant(value: str) -> dt.datetime:
    candidate = value[:-1] + "+00:00" if value[-1] in {"Z", "z"} else value
    return dt.datetime.fromisoformat(candidate)


def _ordered_timestamps(checked_at: str, recorded_at: str) -> None:
    if _timestamp_instant(recorded_at) < _timestamp_instant(checked_at):
        raise ScreeningError("recorded_at must not precede checked_at")


def _reject_unsafe_text(value: str, field: str) -> str:
    for char in value:
        code = ord(char)
        category = unicodedata.category(char)
        if (code < 0x20 and char not in "\t\n\r") or code == 0x7F:
            raise ScreeningError(f"{field} contains forbidden control U+{code:04X}")
        if 0xD800 <= code <= 0xDFFF:
            raise ScreeningError(f"{field} contains an unpaired surrogate")
        if category in {"Cs"}:
            raise ScreeningError(f"{field} contains unsafe Unicode category {category}")
    return value


def _reject_isolated_carriage_returns(value: str, field: str) -> str:
    """Allow CRLF input while rejecting ambiguous bare carriage returns."""

    if re.search(r"\r(?!\n)", value):
        raise ScreeningError(f"{field} contains an isolated carriage return")
    return value


def _preflight_json_structure(text: str, *, label: str) -> None:
    """Bound JSON depth/nodes before the decoder allocates container objects."""

    depth = -1
    nodes = 0
    index = 0
    while index < len(text):
        char = text[index]
        if char in " \t\r\n,:":
            index += 1
            continue
        if char in "{[":
            depth += 1
            nodes += 1
            index += 1
        elif char in "}]":
            depth -= 1
            index += 1
        elif char == '"':
            nodes += 1
            index += 1
            while index < len(text):
                if text[index] == "\\":
                    index += 2
                    continue
                if text[index] == '"':
                    index += 1
                    break
                index += 1
        else:
            nodes += 1
            index += 1
            while index < len(text) and text[index] not in " \t\r\n,]}:":
                index += 1
        if depth > MAX_STRUCTURE_DEPTH:
            raise MatchLimitError(
                f"{label} structure exceeds depth {MAX_STRUCTURE_DEPTH}"
            )
        if nodes > MAX_STRUCTURE_NODES:
            raise MatchLimitError(
                f"{label} structure exceeds {MAX_STRUCTURE_NODES} nodes"
            )


def _preflight_yaml_structure(text: str, *, label: str) -> None:
    """Bound YAML event structure before constructing the round-trip document."""

    parser = YAML(typ="safe")
    depth = -1
    nodes = 0
    try:
        for event in parser.parse(text):
            name = type(event).__name__
            if name in {"MappingStartEvent", "SequenceStartEvent"}:
                depth += 1
                nodes += 1
            elif name in {"MappingEndEvent", "SequenceEndEvent"}:
                depth -= 1
            elif name == "ScalarEvent":
                nodes += 1
            elif name == "AliasEvent":
                raise ScreeningError("shared or recursive YAML aliases are forbidden")
            if depth > MAX_STRUCTURE_DEPTH:
                raise MatchLimitError(
                    f"{label} structure exceeds depth {MAX_STRUCTURE_DEPTH}"
                )
            if nodes > MAX_STRUCTURE_NODES:
                raise MatchLimitError(
                    f"{label} structure exceeds {MAX_STRUCTURE_NODES} nodes"
                )
    except ScreeningError:
        raise
    except Exception as exc:
        raise ScreeningError(f"{label} structure cannot be parsed safely: {exc}") from exc


def _strict_json_bytes(raw: bytes, *, label: str, maximum: int) -> Any:
    if len(raw) > maximum:
        raise ScreeningError(f"{label} exceeds {maximum} bytes")
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ScreeningError(f"{label} must not carry a UTF-8 BOM")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ScreeningError(f"{label} is not strict UTF-8: {exc}") from exc
    _preflight_json_structure(text, label=label)

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        folded: dict[str, str] = {}
        for key, item in pairs:
            if key in result:
                raise ScreeningError(f"{label} has duplicate JSON key {key!r}")
            fold = unicodedata.normalize("NFKC", key).casefold()
            if fold in folded:
                raise ScreeningError(
                    f"{label} has fold-colliding JSON keys {folded[fold]!r} and {key!r}"
                )
            folded[fold] = key
            result[key] = item
        return result

    def reject_constant(token: str) -> None:
        raise ScreeningError(f"{label} contains forbidden non-finite number {token}")

    try:
        value = json.loads(
            text,
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except ScreeningError:
        raise
    except (json.JSONDecodeError, UnicodeError, RecursionError) as exc:
        raise ScreeningError(f"{label} is not strict JSON: {exc}") from exc
    _reject_nonfinite_recursive(value, path=label)
    return value


def _read_bounded_bytes(path: Path, *, maximum: int) -> bytes:
    with path.open("rb") as handle:
        raw = handle.read(maximum + 1)
    if len(raw) > maximum:
        raise MatchLimitError(f"input exceeds {maximum} bytes")
    return raw


def _strict_json_path(path: Path, *, label: str, maximum: int) -> tuple[Any, bytes]:
    try:
        raw = _read_bounded_bytes(path, maximum=maximum)
    except OSError as exc:
        raise ScreeningError(f"cannot read {label} {path}: {exc}") from exc
    return _strict_json_bytes(raw, label=label, maximum=maximum), raw


def _load_schema(path: Path) -> dict[str, Any]:
    value, _ = _strict_json_path(path, label=str(path), maximum=2 * 1024 * 1024)
    if not isinstance(value, dict):
        raise ScreeningError(f"schema {path} must be a JSON object")
    Draft202012Validator.check_schema(value)
    return value


def _schema_errors(instance: Any, schema_path: Path) -> list[str]:
    validator = _schema_validator(schema_path)
    return sorted(
        (
            f"/{'/'.join(str(item) for item in error.absolute_path)}: {error.message}"
        )
        for error in validator.iter_errors(instance)
    )


@lru_cache(maxsize=None)
def _schema_validator(schema_path: Path) -> Draft202012Validator:
    return Draft202012Validator(
        _load_schema(schema_path),
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )


def _require_schema(instance: Any, schema_path: Path, label: str) -> None:
    errors = _schema_errors(instance, schema_path)
    if errors:
        raise ScreeningError(f"{label} schema failure: {'; '.join(errors)}")


def _is_word_char(char: str) -> bool:
    return unicodedata.category(char)[:1] in {"L", "N", "M"}


def _is_token_start(char: str) -> bool:
    return unicodedata.category(char)[:1] in {"L", "N"}


def _normalized_token_parts(value: str) -> Iterable[str]:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    current: list[str] = []
    for char in normalized:
        if current and _is_word_char(char):
            current.append(char)
        elif not current and _is_token_start(char):
            current.append(char)
        elif current:
            yield "".join(current)
            current = []
    if current:
        yield "".join(current)


def tokenize(value: str) -> list[Token]:
    """Tokenize with reversible source spans and frozen hyphen handling.

    Unicode L/N/M code points form tokens. NFKC+casefold is applied to each
    raw token on both rule and document paths. U+00AD and a dash immediately
    followed by a physical line break are treated as discretionary hyphenation
    and join the surrounding token; a same-line dash is a token boundary. Other
    format characters are boundaries. No accent stripping, stemming, or
    lemmatization occurs.
    """

    tokens: list[Token] = []
    buffer: list[str] = []
    start: int | None = None
    last_word_end: int | None = None

    def flush() -> None:
        nonlocal buffer, start, last_word_end
        if start is None or last_word_end is None:
            buffer = []
            start = None
            last_word_end = None
            return
        for part in _normalized_token_parts("".join(buffer)):
            if part:
                tokens.append(Token(part, start, last_word_end))
                if len(tokens) > MAX_TOKENS:
                    raise MatchLimitError(f"token count exceeds {MAX_TOKENS}")
        buffer = []
        start = None
        last_word_end = None

    index = 0
    while index < len(value):
        char = value[index]
        if (start is None and _is_token_start(char)) or (
            start is not None and _is_word_char(char)
        ):
            if start is None:
                start = index
            buffer.append(char)
            if len(buffer) > MAX_RAW_TOKEN_CODEPOINTS:
                raise MatchLimitError(
                    "raw token exceeds "
                    f"{MAX_RAW_TOKEN_CODEPOINTS} code points before normalization"
                )
            last_word_end = index + 1
            index += 1
            continue
        if char == "\u00ad" and start is not None:
            if index + 1 < len(value) and _is_word_char(value[index + 1]):
                index += 1
                continue
        if char == "-" and start is not None:
            cursor = index + 1
            previous_is_letter = (
                index > 0 and unicodedata.category(value[index - 1]).startswith("L")
            )
            if previous_is_letter and cursor < len(value) and value[cursor] in "\r\n":
                if (
                    value[cursor] == "\r"
                    and cursor + 1 < len(value)
                    and value[cursor + 1] == "\n"
                ):
                    cursor += 2
                else:
                    cursor += 1
                if (
                    cursor < len(value)
                    and unicodedata.category(value[cursor]).startswith("L")
                ):
                    index = cursor
                    continue
        flush()
        index += 1
    flush()
    return tokens


def _literal_tokens(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, str):
        raise ScreeningError(f"{field} must be a string")
    _reject_unsafe_text(value, field)
    tokens = tuple(token.normalized for token in tokenize(value))
    if not tokens:
        raise ScreeningError(f"{field} must contain at least one token")
    if len(tokens) > MAX_LITERAL_TOKENS:
        raise ScreeningError(
            f"{field} exceeds {MAX_LITERAL_TOKENS} normalized tokens"
        )
    return tokens


def _semantic_expression(expression: Any, *, depth: int = 1) -> Any:
    if depth > MAX_AST_DEPTH:
        raise ScreeningError(f"AST depth exceeds {MAX_AST_DEPTH}")
    if not isinstance(expression, dict):
        raise ScreeningError("expression node must be an object")
    op = expression.get("op")
    if op == "literal":
        return {"op": "literal", "tokens": _literal_tokens(expression.get("value"), "literal.value")}
    if op in {"all", "any"}:
        key = "terms" if op == "all" else "alternatives"
        children = expression.get(key)
        if not isinstance(children, list) or not 2 <= len(children) <= 8:
            raise ScreeningError(f"{op}.{key} must contain 2..8 expressions")
        semantic_children = [
            _semantic_expression(child, depth=depth + 1) for child in children
        ]
        encoded = [_canonical_json(child) for child in semantic_children]
        if len(set(encoded)) != len(encoded):
            raise ScreeningError(f"{op} contains a duplicate semantic child")
        semantic_children = [
            json.loads(item) for item in sorted(encoded)
        ]
        result: dict[str, Any] = {"op": op, key: semantic_children}
        if op == "all":
            max_span = expression.get("max_span_tokens")
            if isinstance(max_span, bool) or not isinstance(max_span, int):
                raise ScreeningError("all.max_span_tokens must be an integer")
            result["max_span_tokens"] = max_span
        return result
    if op == "near":
        left = _semantic_expression(expression.get("left"), depth=depth + 1)
        right = _semantic_expression(expression.get("right"), depth=depth + 1)
        gap = expression.get("max_gap_tokens")
        ordered = expression.get("ordered")
        if isinstance(gap, bool) or not isinstance(gap, int):
            raise ScreeningError("near.max_gap_tokens must be an integer")
        if not isinstance(ordered, bool):
            raise ScreeningError("near.ordered must be a boolean")
        if not ordered and _canonical_json(left) > _canonical_json(right):
            left, right = right, left
        return {
            "op": "near",
            "left": left,
            "right": right,
            "max_gap_tokens": gap,
            "ordered": ordered,
        }
    raise ScreeningError(f"unsupported expression operator {op!r}")


def _count_nodes(expression: Any) -> int:
    if not isinstance(expression, dict):
        return 1
    op = expression.get("op")
    if op == "literal":
        return 1
    if op == "all":
        return 1 + sum(_count_nodes(item) for item in expression.get("terms", []))
    if op == "any":
        return 1 + sum(
            _count_nodes(item) for item in expression.get("alternatives", [])
        )
    if op == "near":
        return 1 + _count_nodes(expression.get("left")) + _count_nodes(
            expression.get("right")
        )
    return 1


def _compile_rules(snapshot: dict[str, Any]) -> tuple[CompiledRule, ...]:
    rules = snapshot.get("rules")
    if not isinstance(rules, list) or not 1 <= len(rules) <= MAX_RULES:
        raise ScreeningError(f"snapshot rules must contain 1..{MAX_RULES} items")
    seen_ids: dict[str, str] = {}
    seen_semantics: dict[str, str] = {}
    compiled: list[CompiledRule] = []
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            raise ScreeningError(f"rules[{index}] must be an object")
        rule_id = rule.get("rule_id")
        if not isinstance(rule_id, str) or _SAFE_ID_RE.fullmatch(rule_id) is None:
            raise ScreeningError(f"rules[{index}].rule_id is not a safe identifier")
        folded = unicodedata.normalize("NFKC", rule_id).casefold()
        if folded in seen_ids:
            raise ScreeningError(
                f"rules[{index}].rule_id collides with {seen_ids[folded]!r}"
            )
        seen_ids[folded] = rule_id
        expression = rule.get("expression")
        node_count = _count_nodes(expression)
        excludes = rule.get("exclude_if", [])
        if not isinstance(excludes, list):
            raise ScreeningError(f"rules[{index}].exclude_if must be an array")
        node_count += sum(_count_nodes(item.get("expression")) if isinstance(item, dict) else 1 for item in excludes)
        if node_count > MAX_AST_NODES:
            raise ScreeningError(
                f"rules[{index}] AST contains {node_count} nodes; maximum is {MAX_AST_NODES}"
            )
        semantic_expression = _semantic_expression(expression)
        semantic_excludes: list[dict[str, Any]] = []
        for exclusion_index, exclusion in enumerate(excludes):
            if not isinstance(exclusion, dict):
                raise ScreeningError(
                    f"rules[{index}].exclude_if[{exclusion_index}] must be an object"
                )
            within = exclusion.get("within_tokens")
            if isinstance(within, bool) or not isinstance(within, int):
                raise ScreeningError("exclude_if.within_tokens must be an integer")
            semantic_excludes.append(
                {
                    "expression": _semantic_expression(exclusion.get("expression")),
                    "within_tokens": within,
                }
            )
        semantic_excludes.sort(key=_canonical_json)
        semantic = _canonical_json(
            {
                "expression": semantic_expression,
                "exclude_if": semantic_excludes,
            }
        )
        if semantic in seen_semantics:
            raise ScreeningError(
                f"rules[{index}] duplicates semantic rule {seen_semantics[semantic]!r}"
            )
        seen_semantics[semantic] = rule_id
        raw_rule = copy.deepcopy(rule)
        compiled.append(
            CompiledRule(
                rule_id=rule_id,
                expression=raw_rule["expression"],
                exclude_if=tuple(copy.deepcopy(excludes)),
                rule_sha256=_sha256_text(_canonical_json(raw_rule)),
                semantic_key=semantic,
            )
        )
    return tuple(sorted(compiled, key=lambda item: item.rule_id))


def load_snapshot(snapshot_path: Path, manifest_path: Path) -> SnapshotBundle:
    snapshot_raw: bytes | None = None
    manifest_raw: bytes | None = None
    snapshot_sha: str | None = None
    manifest_sha: str | None = None
    try:
        try:
            snapshot_raw = _read_bounded_bytes(
                snapshot_path, maximum=MAX_SNAPSHOT_BYTES
            )
            snapshot_sha = _sha256_bytes(snapshot_raw)
        except MatchLimitError as exc:
            raise SnapshotLoadError(
                "SNAPSHOT_RESOURCE_LIMIT", str(exc)
            ) from exc
        except OSError as exc:
            raise SnapshotLoadError(
                "SNAPSHOT_BYTES_INVALID", f"cannot read supplied snapshot: {exc}"
            ) from exc
        try:
            manifest_raw = _read_bounded_bytes(
                manifest_path, maximum=MAX_MANIFEST_BYTES
            )
            manifest_sha = _sha256_bytes(manifest_raw)
        except MatchLimitError as exc:
            raise SnapshotLoadError(
                "SNAPSHOT_RESOURCE_LIMIT",
                str(exc),
                snapshot_sha256=snapshot_sha,
            ) from exc
        except OSError as exc:
            raise SnapshotLoadError(
                "SNAPSHOT_MANIFEST_INVALID",
                f"cannot read snapshot manifest: {exc}",
                snapshot_sha256=snapshot_sha,
            ) from exc
        try:
            manifest = _strict_json_bytes(
                manifest_raw,
                label="snapshot manifest",
                maximum=MAX_MANIFEST_BYTES,
            )
        except ScreeningError as exc:
            raise SnapshotLoadError(
                "SNAPSHOT_MANIFEST_INVALID",
                str(exc),
                snapshot_sha256=snapshot_sha,
                manifest_sha256=manifest_sha,
            ) from exc
        if not isinstance(manifest, dict):
            raise SnapshotLoadError(
                "SNAPSHOT_MANIFEST_INVALID",
                "snapshot manifest must be a JSON object",
                snapshot_sha256=snapshot_sha,
                manifest_sha256=manifest_sha,
            )
        if (
            manifest.get("schema_version") != MANIFEST_VERSION
            or manifest.get("snapshot_schema_version") != SNAPSHOT_VERSION
            or manifest.get("grammar_profile") != GRAMMAR_PROFILE
            or manifest.get("normalizer_profile") != NORMALIZER_PROFILE
        ):
            raise SnapshotLoadError(
                "SNAPSHOT_PROFILE_UNSUPPORTED",
                "snapshot manifest declares an unsupported contract profile",
                snapshot_sha256=snapshot_sha,
                manifest_sha256=manifest_sha,
            )
        try:
            _require_schema(manifest, MANIFEST_SCHEMA_PATH, "snapshot manifest")
        except ScreeningError as exc:
            raise SnapshotLoadError(
                "SNAPSHOT_MANIFEST_INVALID",
                str(exc),
                snapshot_sha256=snapshot_sha,
                manifest_sha256=manifest_sha,
            ) from exc
        if manifest.get("schema_version") != MANIFEST_VERSION:
            raise SnapshotLoadError(
                "SNAPSHOT_PROFILE_UNSUPPORTED",
                "unsupported snapshot manifest version",
                snapshot_sha256=snapshot_sha,
                manifest_sha256=manifest_sha,
            )
        if manifest.get("snapshot_sha256") != snapshot_sha:
            raise SnapshotLoadError(
                "SNAPSHOT_HASH_MISMATCH",
                "snapshot bytes do not match manifest.snapshot_sha256",
                snapshot_sha256=snapshot_sha,
                manifest_sha256=manifest_sha,
            )
        # The detached manifest authorizes these exact raw bytes.  Do not
        # decode or inspect snapshot content until that byte hash has passed.
        try:
            snapshot = _strict_json_bytes(
                snapshot_raw, label="snapshot", maximum=MAX_SNAPSHOT_BYTES
            )
        except ScreeningError as exc:
            raise SnapshotLoadError(
                "SNAPSHOT_BYTES_INVALID",
                str(exc),
                snapshot_sha256=snapshot_sha,
                manifest_sha256=manifest_sha,
            ) from exc
        if not isinstance(snapshot, dict):
            raise SnapshotLoadError(
                "SNAPSHOT_BYTES_INVALID",
                "snapshot must be a JSON object",
                snapshot_sha256=snapshot_sha,
                manifest_sha256=manifest_sha,
            )
        if (
            snapshot.get("schema_version") != SNAPSHOT_VERSION
            or snapshot.get("grammar_profile") != GRAMMAR_PROFILE
            or snapshot.get("normalizer_profile") != NORMALIZER_PROFILE
        ):
            raise SnapshotLoadError(
                "SNAPSHOT_PROFILE_UNSUPPORTED",
                "snapshot declares an unsupported contract profile",
                snapshot_sha256=snapshot_sha,
                manifest_sha256=manifest_sha,
            )
        try:
            _require_schema(snapshot, SNAPSHOT_SCHEMA_PATH, "snapshot")
        except ScreeningError as exc:
            raise SnapshotLoadError(
                "SNAPSHOT_RULES_UNSUPPORTED",
                str(exc),
                snapshot_sha256=snapshot_sha,
                manifest_sha256=manifest_sha,
            ) from exc
        if snapshot.get("schema_version") != SNAPSHOT_VERSION:
            raise SnapshotLoadError(
                "SNAPSHOT_PROFILE_UNSUPPORTED",
                "unsupported snapshot schema version",
                snapshot_sha256=snapshot_sha,
                manifest_sha256=manifest_sha,
            )
        if manifest.get("snapshot_id") != snapshot.get("snapshot_id"):
            raise SnapshotLoadError(
                "SNAPSHOT_HASH_MISMATCH",
                "manifest.snapshot_id does not match the exact snapshot",
                snapshot_sha256=snapshot_sha,
                manifest_sha256=manifest_sha,
            )
        for field, expected in (
            ("grammar_profile", GRAMMAR_PROFILE),
            ("normalizer_profile", NORMALIZER_PROFILE),
        ):
            if snapshot.get(field) != expected or manifest.get(field) != expected:
                raise SnapshotLoadError(
                    "SNAPSHOT_PROFILE_UNSUPPORTED",
                    f"{field} is unsupported or differs between snapshot and manifest",
                    snapshot_sha256=snapshot_sha,
                    manifest_sha256=manifest_sha,
                )
        if manifest.get("unsupported_rule_count") != 0:
            raise SnapshotLoadError(
                "SNAPSHOT_RULES_UNSUPPORTED",
                "manifest reports unsupported rules; partial-list clean output is forbidden",
                snapshot_sha256=snapshot_sha,
                manifest_sha256=manifest_sha,
            )
        if manifest.get("rule_count") != len(snapshot.get("rules", [])):
            raise SnapshotLoadError(
                "SNAPSHOT_HASH_MISMATCH",
                "manifest.rule_count does not match exact snapshot rules",
                snapshot_sha256=snapshot_sha,
                manifest_sha256=manifest_sha,
            )
        try:
            rules = _compile_rules(snapshot)
        except (ScreeningError, RecursionError) as exc:
            reason = (
                "SNAPSHOT_RESOURCE_LIMIT"
                if "exceeds" in str(exc) or "maximum" in str(exc)
                else "SNAPSHOT_RULES_UNSUPPORTED"
            )
            raise SnapshotLoadError(
                reason,
                str(exc),
                snapshot_sha256=snapshot_sha,
                manifest_sha256=manifest_sha,
            ) from exc
        return SnapshotBundle(
            snapshot=snapshot,
            manifest=manifest,
            snapshot_sha256=snapshot_sha,
            manifest_sha256=manifest_sha,
            rules=rules,
            unicode_data_version=unicodedata.unidata_version,
        )
    except SnapshotLoadError:
        raise
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise SnapshotLoadError(
            "SNAPSHOT_RESOURCE_LIMIT",
            str(exc),
            snapshot_sha256=snapshot_sha,
            manifest_sha256=manifest_sha,
        ) from exc


def snapshot_state(
    snapshot_path: Path | None,
    manifest_path: Path | None,
) -> SnapshotState:
    if snapshot_path is None and manifest_path is None:
        return SnapshotState(
            status="not_checked",
            reason_code="SNAPSHOT_NOT_PROVIDED",
            bundle=None,
            snapshot_sha256=None,
            manifest_sha256=None,
            detail="No snapshot and manifest were explicitly supplied.",
        )
    if snapshot_path is None or manifest_path is None:
        return SnapshotState(
            status="degraded",
            reason_code="SNAPSHOT_MANIFEST_INVALID",
            bundle=None,
            snapshot_sha256=None,
            manifest_sha256=None,
            detail="Snapshot and manifest must be supplied together.",
        )
    try:
        bundle = load_snapshot(snapshot_path, manifest_path)
    except SnapshotLoadError as exc:
        return SnapshotState(
            status="degraded",
            reason_code=exc.reason_code,
            bundle=None,
            snapshot_sha256=exc.snapshot_sha256,
            manifest_sha256=exc.manifest_sha256,
            detail=str(exc),
        )
    return SnapshotState(
        status="loaded",
        reason_code="CHECK_COMPLETED",
        bundle=bundle,
        snapshot_sha256=bundle.snapshot_sha256,
        manifest_sha256=bundle.manifest_sha256,
        detail=None,
    )


def _minimal_witnesses(values: Iterable[Witness]) -> list[Witness]:
    """Return the bounded, exact witness union in canonical order.

    Only byte-identical witness spans collapse here.  A proper containing span
    remains a distinct rule witness and is later joined with overlaps only for
    ``unique_instance_count``; dropping it would silently change rule-match
    cardinality for ``any`` and ``all`` expressions.
    """

    unique = sorted(set(values))
    if len(unique) > MAX_NODE_WITNESSES:
        raise MatchLimitError(
            f"expression produced more than {MAX_NODE_WITNESSES} witnesses"
        )
    return unique


def _literal_witnesses(
    tokens: list[Token],
    literal: tuple[str, ...],
    *,
    budget: MatchWorkBudget,
) -> list[Witness]:
    width = len(literal)
    result: list[Witness] = []
    normalized = [token.normalized for token in tokens]
    budget.spend(max(0, len(tokens) - width + 1))
    for index in range(0, len(tokens) - width + 1):
        if tuple(normalized[index : index + width]) == literal:
            result.append(
                Witness(
                    index,
                    index + width,
                    tokens[index].start,
                    tokens[index + width - 1].end,
                )
            )
            if len(result) > MAX_NODE_WITNESSES:
                raise MatchLimitError(
                    f"literal produced more than {MAX_NODE_WITNESSES} witnesses"
                )
    return result


def _token_gap(left: Witness, right: Witness) -> int:
    if left.token_end <= right.token_start:
        return right.token_start - left.token_end
    if right.token_end <= left.token_start:
        return left.token_start - right.token_end
    return 0


def _combine(left: Witness, right: Witness) -> Witness:
    return Witness(
        min(left.token_start, right.token_start),
        max(left.token_end, right.token_end),
        min(left.codepoint_start, right.codepoint_start),
        max(left.codepoint_end, right.codepoint_end),
    )


def evaluate_expression(
    expression: dict[str, Any],
    tokens: list[Token],
    *,
    depth: int = 1,
    budget: MatchWorkBudget | None = None,
) -> list[Witness]:
    if budget is None:
        budget = MatchWorkBudget()
    if depth > MAX_AST_DEPTH:
        raise MatchLimitError(f"AST depth exceeds {MAX_AST_DEPTH}")
    op = expression.get("op")
    if op == "literal":
        return _literal_witnesses(
            tokens,
            _literal_tokens(expression.get("value"), "literal.value"),
            budget=budget,
        )
    if op == "any":
        alternatives = expression.get("alternatives", [])
        return _minimal_witnesses(
            witness
            for child in alternatives
            for witness in evaluate_expression(
                child, tokens, depth=depth + 1, budget=budget
            )
        )
    if op == "near":
        left_values = evaluate_expression(
            expression["left"], tokens, depth=depth + 1, budget=budget
        )
        right_values = evaluate_expression(
            expression["right"], tokens, depth=depth + 1, budget=budget
        )
        maximum = expression["max_gap_tokens"]
        ordered = expression["ordered"]
        combined: list[Witness] = []
        attempts = 0
        for left in left_values:
            for right in right_values:
                attempts += 1
                budget.spend(1)
                if attempts > MAX_NODE_COMBINATIONS:
                    raise MatchLimitError("near witness evaluation exceeded the cap")
                if ordered and left.token_end > right.token_start:
                    continue
                if _token_gap(left, right) <= maximum:
                    combined.append(_combine(left, right))
                    if len(combined) > MAX_NODE_WITNESSES:
                        raise MatchLimitError("near witness enumeration exceeded the cap")
        return _minimal_witnesses(combined)
    if op == "all":
        child_values = [
            evaluate_expression(child, tokens, depth=depth + 1, budget=budget)
            for child in expression.get("terms", [])
        ]
        if any(not values for values in child_values):
            return []
        maximum = expression["max_span_tokens"]
        combinations: list[Witness] = []
        attempts = 0

        def visit(child_index: int, current: Witness | None) -> None:
            nonlocal attempts
            if len(combinations) > MAX_NODE_WITNESSES:
                raise MatchLimitError("all witness enumeration exceeded the cap")
            if child_index == len(child_values):
                if current is not None:
                    combinations.append(current)
                return
            for witness in child_values[child_index]:
                attempts += 1
                budget.spend(1)
                if attempts > MAX_NODE_COMBINATIONS:
                    raise MatchLimitError("all witness evaluation exceeded the cap")
                candidate = witness if current is None else _combine(current, witness)
                if candidate.token_end - candidate.token_start <= maximum:
                    visit(child_index + 1, candidate)

        visit(0, None)
        return _minimal_witnesses(combinations)
    raise ScreeningError(f"unsupported expression operator {op!r}")


def evaluate_rule(
    rule: CompiledRule,
    tokens: list[Token],
    *,
    budget: MatchWorkBudget | None = None,
) -> list[Witness]:
    if budget is None:
        budget = MatchWorkBudget()
    included = evaluate_expression(rule.expression, tokens, budget=budget)
    for exclusion in rule.exclude_if:
        excluded = evaluate_expression(
            exclusion["expression"], tokens, budget=budget
        )
        within = exclusion["within_tokens"]
        retained: list[Witness] = []
        for witness in included:
            is_excluded = False
            for other in excluded:
                budget.spend(1)
                if _token_gap(witness, other) <= within:
                    is_excluded = True
                    break
            if not is_excluded:
                retained.append(witness)
        included = retained
    return _minimal_witnesses(included)


_CONTEXT_PRIORITY = {
    "author_prose": 0,
    "quote": 20,
    "cited_title": 30,
    "reference_entry": 40,
    "code_or_verbatim": 50,
    "unknown": 60,
}


def _append_parse_interval(
    intervals: list[tuple[int, int, str]], value: tuple[int, int, str]
) -> None:
    intervals.append(value)
    if len(intervals) > MAX_PARSE_INTERVALS:
        raise MatchLimitError(f"parse interval count exceeds {MAX_PARSE_INTERVALS}")


def _intervals_from_fences(text: str) -> list[tuple[int, int, str]]:
    intervals: list[tuple[int, int, str]] = []
    open_fence: tuple[str, int, int] | None = None
    for line_match in re.finditer(r"[^\n]*(?:\n|$)", text):
        line = line_match.group(0)
        if not line:
            continue
        offset = line_match.start()
        stripped = line.lstrip(" \t")
        match = re.match(r"(`{3,}|~{3,})", stripped)
        if match:
            marker = match.group(1)
            family = marker[0]
            if open_fence is None:
                open_fence = (family, len(marker), offset)
            elif family == open_fence[0] and len(marker) >= open_fence[1]:
                _append_parse_interval(
                    intervals,
                    (open_fence[2], offset + len(line), "code_or_verbatim"),
                )
                open_fence = None
    if open_fence is not None:
        _append_parse_interval(intervals, (open_fence[2], len(text), "unknown"))
    return intervals


def _paired_environment_intervals(
    text: str,
    names: tuple[str, ...],
    kind: str,
    *,
    excluded: tuple[tuple[int, int], ...] = (),
) -> list[tuple[int, int, str]]:
    def search_unexcluded(pattern: re.Pattern[str], cursor: int) -> re.Match[str] | None:
        while True:
            match = pattern.search(text, cursor)
            if match is None or (
                not _position_excluded(match.start(), excluded)
                and not _is_backslash_escaped(text, match.start())
            ):
                return match
            cursor = match.end()

    intervals: list[tuple[int, int, str]] = []
    for name in names:
        begin_re = re.compile(r"\\begin\{" + re.escape(name) + r"\}")
        end_re = re.compile(r"\\end\{" + re.escape(name) + r"\}")
        cursor = 0
        while True:
            begin = search_unexcluded(begin_re, cursor)
            if begin is None:
                break
            end = search_unexcluded(end_re, begin.end())
            if end is None:
                _append_parse_interval(
                    intervals, (begin.start(), len(text), "unknown")
                )
                break
            _append_parse_interval(intervals, (begin.start(), end.end(), kind))
            cursor = end.end()
    return intervals


def _is_backslash_escaped(text: str, index: int) -> bool:
    """Return true when the code point at index has an odd backslash prefix."""

    count = 0
    cursor = index - 1
    while cursor >= 0 and text[cursor] == "\\":
        count += 1
        cursor -= 1
    return count % 2 == 1


def _position_excluded(
    index: int,
    excluded: tuple[tuple[int, int], ...],
) -> bool:
    """Test sorted, non-overlapping intervals in logarithmic time."""

    lower = 0
    upper = len(excluded)
    while lower < upper:
        middle = (lower + upper) // 2
        start, end = excluded[middle]
        if index < start:
            upper = middle
        elif index >= end:
            lower = middle + 1
        else:
            return True
    return False


def _find_unescaped(
    text: str,
    needle: str,
    start: int,
    end: int | None = None,
    *,
    excluded: tuple[tuple[int, int], ...] = (),
    budget: ParseWorkBudget | None = None,
) -> int:
    """Find a delimiter whose first code point is not backslash-escaped."""

    limit = len(text) if end is None else end
    cursor = start
    while cursor <= limit - len(needle):
        found = text.find(needle, cursor, limit)
        if found < 0:
            return -1
        if budget is not None:
            budget.spend()
        if not _is_backslash_escaped(text, found) and not _position_excluded(
            found, excluded
        ):
            return found
        cursor = found + len(needle)
    return -1


def _paired_delimiter_intervals(
    text: str,
    opener: str,
    closer: str,
    kind: str,
    *,
    same_line: bool = False,
    excluded: tuple[tuple[int, int], ...] = (),
) -> list[tuple[int, int, str]]:
    intervals: list[tuple[int, int, str]] = []
    cursor = 0
    while True:
        start = _find_unescaped(text, opener, cursor, excluded=excluded)
        if start < 0:
            break
        search_start = start + len(opener)
        line_end = text.find("\n", search_start) if same_line else -1
        search_end = line_end if same_line and line_end >= 0 else None
        end = _find_unescaped(
            text,
            closer,
            search_start,
            search_end,
            excluded=excluded,
        )
        if end < 0 or (same_line and line_end >= 0 and end > line_end):
            failure_end = line_end if line_end >= 0 else len(text)
            _append_parse_interval(intervals, (start, failure_end, "unknown"))
            cursor = max(failure_end, start + len(opener))
            continue
        _append_parse_interval(intervals, (start, end + len(closer), kind))
        cursor = end + len(closer)
    return intervals


def _inline_code_intervals(
    text: str,
    *,
    excluded: tuple[tuple[int, int], ...] = (),
) -> list[tuple[int, int, str]]:
    intervals: list[tuple[int, int, str]] = []
    for line_match in re.finditer(r"[^\n]*(?:\n|$)", text):
        line = line_match.group(0)
        base = line_match.start()
        cursor = 0
        while cursor < len(line):
            match = re.search(r"`+", line[cursor:])
            if match is None:
                break
            start = cursor + match.start()
            fence = match.group(0)
            absolute_start = base + start
            if len(fence) >= 3 or any(
                interval_start <= absolute_start < interval_end
                for interval_start, interval_end in excluded
            ):
                cursor += match.end()
                continue
            if _is_backslash_escaped(line, start):
                cursor += match.end()
                continue
            end = _find_unescaped(line, fence, cursor + match.end())
            if end < 0:
                _append_parse_interval(
                    intervals,
                    (base + start, base + len(line.rstrip("\n")), "unknown"),
                )
                break
            _append_parse_interval(
                intervals,
                (base + start, base + end + len(fence), "code_or_verbatim"),
            )
            cursor = end + len(fence)
    return intervals


def _select_source_order_opaque_intervals(
    *groups: Iterable[tuple[int, int, str]],
) -> list[tuple[int, int, str]]:
    """Keep the first opaque construct and ignore openers inside its bytes."""

    indexed = [
        (start, sequence, end, kind)
        for sequence, (start, end, kind) in enumerate(
            item for group in groups for item in group
        )
    ]
    if len(indexed) > MAX_PARSE_INTERVALS:
        raise MatchLimitError(
            f"opaque parse candidates exceed {MAX_PARSE_INTERVALS} intervals"
        )
    selected: list[tuple[int, int, str]] = []
    covered_until = -1
    for start, _sequence, end, kind in sorted(indexed):
        if start < covered_until:
            continue
        _append_parse_interval(selected, (start, end, kind))
        covered_until = end
    return selected


def _append_opaque_opener(
    openers: list[OpaqueOpener], opener: OpaqueOpener
) -> None:
    openers.append(opener)
    if len(openers) > MAX_PARSE_INTERVALS:
        raise MatchLimitError(
            f"opaque parse candidates exceed {MAX_PARSE_INTERVALS} intervals"
        )


def _markdown_opaque_openers(
    text: str, *, budget: ParseWorkBudget
) -> list[OpaqueOpener]:
    """Collect only fixed-cost Markdown opener tokens.

    Pairing happens later, after the earliest opener has won.  This prevents an
    opener inside an earlier comment/code span from consuming the closer that
    belongs to a later real construct.
    """

    openers: list[OpaqueOpener] = []
    for line_match in re.finditer(r"[^\n]*(?:\n|$)", text):
        line = line_match.group(0)
        if not line:
            continue
        stripped = line.lstrip(" \t")
        match = re.match(r"(`{3,}|~{3,})", stripped)
        if match:
            budget.spend()
            marker = match.group(1)
            start = line_match.start() + len(line) - len(stripped)
            _append_opaque_opener(
                openers,
                OpaqueOpener(
                    start,
                    0,
                    line_match.end(),
                    "markdown_fence",
                    (marker[0], len(marker)),
                ),
            )
    for match in re.finditer(re.escape("<!--"), text):
        budget.spend()
        _append_opaque_opener(
            openers,
            OpaqueOpener(match.start(), 1, match.end(), "markdown_comment"),
        )
    for match in re.finditer(r"`+", text):
        budget.spend()
        marker = match.group(0)
        if len(marker) >= 3 or _is_backslash_escaped(text, match.start()):
            continue
        _append_opaque_opener(
            openers,
            OpaqueOpener(
                match.start(),
                2,
                match.end(),
                "markdown_inline_code",
                (marker,),
            ),
        )
    for match in re.finditer(r"\$+", text):
        budget.spend()
        marker = match.group(0)
        if _is_backslash_escaped(text, match.start()) or len(marker) not in {1, 2}:
            continue
        _append_opaque_opener(
            openers,
            OpaqueOpener(
                match.start(),
                3 if len(marker) == 2 else 4,
                match.end(),
                "display_math" if len(marker) == 2 else "inline_math",
                (marker,),
            ),
        )
    return openers


def _latex_opaque_openers(
    text: str, *, budget: ParseWorkBudget
) -> list[OpaqueOpener]:
    """Collect bounded LaTeX opaque openers without backreference searches."""

    openers: list[OpaqueOpener] = []
    for match in re.finditer("%", text):
        budget.spend()
        if not _is_backslash_escaped(text, match.start()):
            _append_opaque_opener(
                openers,
                OpaqueOpener(match.start(), 0, match.end(), "latex_comment"),
            )
    environment_re = re.compile(
        r"\\begin\{(verbatim|lstlisting|minted)\}"
    )
    for match in environment_re.finditer(text):
        budget.spend()
        if not _is_backslash_escaped(text, match.start()):
            _append_opaque_opener(
                openers,
                OpaqueOpener(
                    match.start(),
                    1,
                    match.end(),
                    "latex_environment",
                    (match.group(1),),
                ),
            )
    # A TeX control word continues through ASCII letters.  Therefore
    # ``\verbose``/``\verbatim`` are not ``\verb``.  The starred form is an
    # explicit variant and both forms require a non-space delimiter.
    verb_res = (
        re.compile(r"\\verb\*([^\s\n])"),
        re.compile(r"\\verb(?![A-Za-z*])([^\s\n])"),
    )
    for verb_re in verb_res:
        for match in verb_re.finditer(text):
            budget.spend()
            if not _is_backslash_escaped(text, match.start()):
                _append_opaque_opener(
                    openers,
                    OpaqueOpener(
                        match.start(),
                        2,
                        match.end(),
                        "latex_verb",
                        (match.group(1),),
                    ),
                )
    malformed_verb_re = re.compile(
        r"\\verb\*(?=\s|$)|\\verb(?![A-Za-z*])(?=\s|$)"
    )
    for match in malformed_verb_re.finditer(text):
        budget.spend()
        if not _is_backslash_escaped(text, match.start()):
            _append_opaque_opener(
                openers,
                OpaqueOpener(
                    match.start(),
                    2,
                    match.end(),
                    "latex_verb_missing_delimiter",
                ),
            )
    for opener, syntax, priority in (
        (r"\(", "paren_math", 3),
        (r"\[", "bracket_math", 3),
    ):
        for match in re.finditer(re.escape(opener), text):
            budget.spend()
            if not _is_backslash_escaped(text, match.start()):
                _append_opaque_opener(
                    openers,
                    OpaqueOpener(match.start(), priority, match.end(), syntax),
                )
    for match in re.finditer(r"\$+", text):
        budget.spend()
        marker = match.group(0)
        if _is_backslash_escaped(text, match.start()) or len(marker) not in {1, 2}:
            continue
        _append_opaque_opener(
            openers,
            OpaqueOpener(
                match.start(),
                4 if len(marker) == 2 else 5,
                match.end(),
                "display_math" if len(marker) == 2 else "inline_math",
                (marker,),
            ),
        )
    return openers


def _line_end(text: str, start: int, *, include_newline: bool) -> int:
    newline = text.find("\n", start)
    if newline < 0:
        return len(text)
    return newline + 1 if include_newline else newline


def _close_opaque_opener(
    text: str, opener: OpaqueOpener, *, budget: ParseWorkBudget
) -> tuple[int, str]:
    """Return the selected opaque interval end and its fail-safe kind."""

    syntax = opener.syntax
    if syntax == "markdown_fence":
        family, minimum = opener.payload
        for line_match in re.finditer(r"[^\n]*(?:\n|$)", text[opener.opener_end :]):
            line = line_match.group(0)
            if not line:
                continue
            stripped = line.lstrip(" \t")
            match = re.match(r"(`{3,}|~{3,})", stripped)
            if match:
                budget.spend()
                if match.group(1)[0] == family and len(match.group(1)) >= minimum:
                    return opener.opener_end + line_match.end(), "code_or_verbatim"
        return len(text), "unknown"
    if syntax == "markdown_comment":
        end = text.find("-->", opener.opener_end)
        if end >= 0:
            budget.spend()
        return (
            (end + 3, "code_or_verbatim")
            if end >= 0
            else (len(text), "unknown")
        )
    if syntax == "markdown_inline_code":
        marker = opener.payload[0]
        line_end = _line_end(text, opener.opener_end, include_newline=False)
        end = _find_unescaped(
            text, marker, opener.opener_end, line_end, budget=budget
        )
        return (
            (end + len(marker), "code_or_verbatim")
            if end >= 0
            else (line_end, "unknown")
        )
    if syntax == "latex_comment":
        return _line_end(text, opener.opener_end, include_newline=True), "code_or_verbatim"
    if syntax == "latex_environment":
        closer = rf"\end{{{opener.payload[0]}}}"
        end = _find_unescaped(
            text, closer, opener.opener_end, budget=budget
        )
        return (
            (end + len(closer), "code_or_verbatim")
            if end >= 0
            else (len(text), "unknown")
        )
    if syntax == "latex_verb":
        delimiter = opener.payload[0]
        line_end = _line_end(text, opener.opener_end, include_newline=False)
        end = text.find(delimiter, opener.opener_end, line_end)
        if end >= 0:
            budget.spend()
        return (
            (end + len(delimiter), "code_or_verbatim")
            if end >= 0
            else (line_end, "unknown")
        )
    if syntax == "latex_verb_missing_delimiter":
        return _line_end(text, opener.opener_end, include_newline=False), "unknown"
    closer = {
        "paren_math": r"\)",
        "bracket_math": r"\]",
        "display_math": "$$",
        "inline_math": "$",
    }[syntax]
    line_end = (
        _line_end(text, opener.opener_end, include_newline=False)
        if syntax == "inline_math"
        else None
    )
    end = _find_unescaped(
        text, closer, opener.opener_end, line_end, budget=budget
    )
    return (
        (end + len(closer), "code_or_verbatim")
        if end >= 0
        else (line_end if line_end is not None else len(text), "unknown")
    )


def _source_order_opaque_intervals(
    text: str, artifact_format: str, *, budget: ParseWorkBudget
) -> list[tuple[int, int, str]]:
    openers = (
        _markdown_opaque_openers(text, budget=budget)
        if artifact_format == "markdown"
        else _latex_opaque_openers(text, budget=budget)
    )
    intervals: list[tuple[int, int, str]] = []
    cursor = 0
    for opener in sorted(
        openers,
        key=lambda item: (item.start, item.priority, item.opener_end, item.syntax),
    ):
        if opener.start < cursor:
            continue
        end, kind = _close_opaque_opener(text, opener, budget=budget)
        end = max(end, opener.opener_end)
        _append_parse_interval(intervals, (opener.start, end, kind))
        cursor = end
    return intervals


def _unexcluded_ranges(
    length: int, excluded: tuple[tuple[int, int], ...]
) -> Iterable[tuple[int, int]]:
    cursor = 0
    for start, end in sorted(excluded):
        start = max(cursor, min(length, start))
        end = max(start, min(length, end))
        if cursor < start:
            yield cursor, start
        cursor = max(cursor, end)
    if cursor < length:
        yield cursor, length


def _quote_intervals(
    text: str,
    *,
    excluded: tuple[tuple[int, int], ...],
    budget: ParseWorkBudget,
) -> list[tuple[int, int, str]]:
    """Pair prose quote marks linearly without crossing opaque intervals."""

    intervals: list[tuple[int, int, str]] = []
    for range_start, range_end in _unexcluded_ranges(len(text), excluded):
        cursor = range_start
        while cursor < range_end:
            line_end = text.find("\n", cursor, range_end)
            if line_end < 0:
                line_end = range_end
            opener = next(
                (
                    index
                    for index in range(cursor, line_end)
                    if text[index] in {'"', "“"}
                    and not _is_backslash_escaped(text, index)
                ),
                -1,
            )
            if opener < 0:
                cursor = line_end + (line_end < range_end)
                continue
            budget.spend()
            closer = next(
                (
                    index
                    for index in range(opener + 1, line_end)
                    if text[index] in {'"', "”"}
                    and not _is_backslash_escaped(text, index)
                ),
                -1,
            )
            if closer < 0:
                break
            budget.spend()
            if closer > opener + 1:
                _append_parse_interval(
                    intervals, (opener, closer + 1, "quote")
                )
            cursor = closer + 1
    return intervals


def _doi_title_intervals(
    text: str,
    *,
    excluded: tuple[tuple[int, int], ...],
    budget: ParseWorkBudget,
) -> list[tuple[int, int, str]]:
    """Find DOI-link titles with monotonic cursors and no regex retry blow-up."""

    prefixes = (
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi:",
    )
    intervals: list[tuple[int, int, str]] = []
    for range_start, range_end in _unexcluded_ranges(len(text), excluded):
        cursor = range_start
        while cursor < range_end:
            line_end = text.find("\n", cursor, range_end)
            if line_end < 0:
                line_end = range_end
            opener = text.find("[", cursor, line_end)
            if opener < 0:
                cursor = line_end + (line_end < range_end)
                continue
            budget.spend()
            close = text.find("](", opener + 1, line_end)
            if close < 0:
                break
            budget.spend()
            target_start = close + 2
            prefix = next(
                (
                    value
                    for value in prefixes
                    if text[target_start : target_start + len(value)].lower()
                    == value
                ),
                None,
            )
            if prefix is None:
                cursor = target_start
                continue
            target_end = text.find(")", target_start + len(prefix), line_end)
            if target_end < 0:
                break
            budget.spend()
            if close > opener + 1:
                _append_parse_interval(
                    intervals, (opener + 1, close, "cited_title")
                )
            cursor = target_end + 1
    return intervals


def _nested_environment_intervals(
    text: str,
    names: tuple[str, ...],
    kind: str,
    *,
    excluded: tuple[tuple[int, int], ...],
    budget: ParseWorkBudget,
) -> list[tuple[int, int, str]]:
    """Recognize nested non-opaque LaTeX environments in source order."""

    name_pattern = "|".join(re.escape(name) for name in names)
    token_re = re.compile(r"\\(begin|end)\{(" + name_pattern + r")\}")
    stack: list[tuple[str, int]] = []
    intervals: list[tuple[int, int, str]] = []
    for match in token_re.finditer(text):
        budget.spend()
        if _position_excluded(match.start(), excluded) or _is_backslash_escaped(
            text, match.start()
        ):
            continue
        action, name = match.groups()
        if action == "begin":
            stack.append((name, match.start()))
            if len(stack) > MAX_PARSE_INTERVALS:
                raise MatchLimitError(
                    f"environment nesting exceeds {MAX_PARSE_INTERVALS}"
                )
        elif stack and stack[-1][0] == name:
            _name, start = stack.pop()
            if not stack:
                _append_parse_interval(intervals, (start, match.end(), kind))
    if stack:
        _append_parse_interval(intervals, (stack[0][1], len(text), "unknown"))
    return intervals


def segment_document(text: str, artifact_format: str) -> list[Segment]:
    if artifact_format not in {"markdown", "latex"}:
        raise ScreeningError("artifact_format must be markdown or latex")
    if not text:
        return []
    intervals: list[tuple[int, int, str]] = []
    paragraph_boundaries: set[int] = set()
    reference_entry_boundaries: set[int] = set()
    partition_boundaries = {0, len(text)}
    parse_budget = ParseWorkBudget()

    def add_partition_boundary(target: set[int], value: int) -> None:
        target.add(value)
        partition_boundaries.add(value)
        if len(partition_boundaries) > MAX_SEGMENTS + 1:
            raise MatchLimitError(
                f"document partition exceeds {MAX_SEGMENTS} output segments"
            )

    for match in re.finditer(r"\r?\n[ \t]*\r?\n", text):
        parse_budget.spend()
        add_partition_boundary(paragraph_boundaries, match.end())

    def extend_bounded(values: Iterable[tuple[int, int, str]]) -> None:
        for value in values:
            intervals.append(value)
            if len(intervals) > MAX_PARSE_INTERVALS:
                raise MatchLimitError(
                    f"parse interval count exceeds {MAX_PARSE_INTERVALS}"
                )

    if artifact_format == "markdown":
        opaque_intervals = _source_order_opaque_intervals(
            text, artifact_format, budget=parse_budget
        )
        extend_bounded(opaque_intervals)
        delimiter_exclusions = tuple(
            (start, end) for start, end, _ in opaque_intervals
        )
        for match in re.finditer(r"(?m)^[ \t]*>[^\n]*(?:\n|$)", text):
            parse_budget.spend()
            marker = match.start() + match.group(0).find(">")
            if not _position_excluded(marker, delimiter_exclusions):
                extend_bounded(((match.start(), match.end(), "quote"),))
        reference = None
        for match in re.finditer(
            r"(?im)^#{1,6}[ \t]+(?:references|bibliography|works[ \t]+cited)[ \t]*$",
            text,
        ):
            parse_budget.spend()
            if not _position_excluded(match.start(), delimiter_exclusions):
                reference = match
                break
        if reference is not None:
            extend_bounded(((reference.start(), len(text), "reference_entry"),))
            reference_body_start = reference.end()
            for line in re.finditer(
                r"(?m)^[ \t]*(?=\S)", text[reference_body_start:]
            ):
                parse_budget.spend()
                add_partition_boundary(
                    reference_entry_boundaries,
                    reference_body_start + line.start(),
                )
        extend_bounded(
            _doi_title_intervals(
                text,
                excluded=delimiter_exclusions,
                budget=parse_budget,
            )
        )
    else:
        opaque_intervals = _source_order_opaque_intervals(
            text, artifact_format, budget=parse_budget
        )
        extend_bounded(opaque_intervals)
        delimiter_exclusions = tuple(
            (start, end) for start, end, _ in opaque_intervals
        )
        extend_bounded(
            _nested_environment_intervals(
                text,
                ("quote", "quotation"),
                "quote",
                excluded=delimiter_exclusions,
                budget=parse_budget,
            )
        )
        bibliography_intervals = _nested_environment_intervals(
            text,
            ("thebibliography",),
            "reference_entry",
            excluded=delimiter_exclusions,
            budget=parse_budget,
        )
        extend_bounded(bibliography_intervals)
        for match in re.finditer(r"(?m)^[ \t]*\\bibitem\b", text):
            parse_budget.spend()
            if not _position_excluded(
                match.start(), delimiter_exclusions
            ) and not _is_backslash_escaped(
                text,
                match.start() + match.group(0).rfind("\\"),
            ):
                add_partition_boundary(reference_entry_boundaries, match.start())

    extend_bounded(
        _quote_intervals(
            text,
            excluded=delimiter_exclusions,
            budget=parse_budget,
        )
    )

    cleaned: list[tuple[int, int, str]] = []
    boundaries = set(partition_boundaries)
    for start, end, kind in intervals:
        start = max(0, min(start, len(text)))
        end = max(start, min(end, len(text)))
        if start == end:
            continue
        cleaned.append((start, end, kind))
        boundaries.add(start)
        boundaries.add(end)
        if len(boundaries) > MAX_SEGMENTS + 1:
            raise MatchLimitError(
                f"document partition exceeds {MAX_SEGMENTS} output segments"
            )
    ordered = sorted(boundaries)
    starts: dict[int, list[str]] = {}
    ends: dict[int, list[str]] = {}
    for start, end, kind in cleaned:
        starts.setdefault(start, []).append(kind)
        ends.setdefault(end, []).append(kind)
    active: dict[str, int] = {}
    raw_segments: list[tuple[str, int, int]] = []
    for start, end in zip(ordered, ordered[1:]):
        for kind in ends.get(start, ()):
            remaining = active.get(kind, 0) - 1
            if remaining > 0:
                active[kind] = remaining
            else:
                active.pop(kind, None)
        for kind in starts.get(start, ()):
            active[kind] = active.get(kind, 0) + 1
        kind = (
            max(active, key=lambda item: _CONTEXT_PRIORITY[item])
            if active
            else "author_prose"
        )
        if (
            raw_segments
            and raw_segments[-1][0] == kind
            and raw_segments[-1][2] == start
            and not (
                (kind == "author_prose" and start in paragraph_boundaries)
                or (
                    kind == "reference_entry"
                    and start in reference_entry_boundaries
                )
            )
        ):
            previous = raw_segments.pop()
            raw_segments.append((kind, previous[1], end))
        else:
            raw_segments.append((kind, start, end))
    return [
        Segment(f"SEG-{index + 1:06d}", kind, start, end)
        for index, (kind, start, end) in enumerate(raw_segments)
    ]


def _disposition(context: str) -> str:
    if context == "author_prose":
        return "review_author_prose_no_automatic_rewrite"
    if context in PROTECTED_CONTEXTS:
        return "preserve_verbatim_review_context"
    if context == "cited_abstract":
        return "review_cited_source_no_automatic_rewrite"
    return "review_unknown_no_automatic_rewrite"


def _selected_byte_offsets(text: str, indices: Iterable[int]) -> dict[int, int]:
    """Compute UTF-8 offsets only for bounded persisted witness endpoints."""

    wanted = set(indices)
    if not wanted:
        return {}
    if min(wanted) < 0 or max(wanted) > len(text):
        raise ScreeningError("requested UTF-8 offset is outside the source text")
    offsets: dict[int, int] = {}
    total = 0
    for index, char in enumerate(text):
        if index in wanted:
            offsets[index] = total
        total += len(char.encode("utf-8", errors="strict"))
    if len(text) in wanted:
        offsets[len(text)] = total
    if set(offsets) != wanted:
        raise ScreeningError("requested UTF-8 offsets could not be replayed")
    return offsets


def _unique_instance_count(matches: list[dict[str, Any]]) -> int:
    by_segment: dict[str, list[tuple[int, int]]] = {}
    for match in matches:
        by_segment.setdefault(match["segment_id"], []).append(
            (
                match["source_span"]["codepoint_start"],
                match["source_span"]["codepoint_end"],
            )
        )
    count = 0
    for intervals in by_segment.values():
        current_end: int | None = None
        for start, end in sorted(set(intervals)):
            if current_end is None or start >= current_end:
                count += 1
                current_end = end
            else:
                current_end = max(current_end, end)
    return count


def scan_segments(
    text: str,
    segments: list[Segment],
    bundle: SnapshotBundle,
    *,
    artifact_sha256: str,
    surface: str,
    work_budget: MatchWorkBudget | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    encoded = text.encode("utf-8", errors="strict")
    if len(encoded) > MAX_DOCUMENT_BYTES:
        raise MatchLimitError(f"document exceeds {MAX_DOCUMENT_BYTES} bytes")
    if len(segments) * len(bundle.rules) > MAX_RULE_SEGMENT_EVALUATIONS:
        raise MatchLimitError(
            "rule-by-segment evaluations exceed "
            f"{MAX_RULE_SEGMENT_EVALUATIONS}"
        )
    matches: list[dict[str, Any]] = []
    by_context = {context: 0 for context in CONTEXTS}
    matched_rule_ids: set[str] = set()
    if work_budget is None:
        work_budget = MatchWorkBudget()
    for segment in segments:
        segment_text = text[segment.start : segment.end]
        segment_tokens = tokenize(segment_text)
        for rule in bundle.rules:
            for witness in evaluate_rule(
                rule, segment_tokens, budget=work_budget
            ):
                cp_start = segment.start + witness.codepoint_start
                cp_end = segment.start + witness.codepoint_end
                matched_text = text[cp_start:cp_end]
                if len(matched_text) > MAX_EVIDENCE_CODEPOINTS:
                    raise MatchLimitError(
                        f"match evidence exceeds {MAX_EVIDENCE_CODEPOINTS} code points"
                    )
                if len(matched_text.split()) > MAX_EVIDENCE_WORDS:
                    raise MatchLimitError(
                        f"match evidence exceeds {MAX_EVIDENCE_WORDS} whitespace words"
                    )
                match_key = {
                    "artifact_sha256": artifact_sha256,
                    "snapshot_sha256": bundle.snapshot_sha256,
                    "surface": surface,
                    "segment_id": segment.segment_id,
                    "context": segment.kind,
                    "rule_id": rule.rule_id,
                    "codepoint_start": cp_start,
                    "codepoint_end": cp_end,
                }
                match = {
                    "match_id": "tpm-" + _sha256_text(_canonical_json(match_key))[:24],
                    "pattern_id": rule.rule_id,
                    "pattern_sha256": rule.rule_sha256,
                    "segment_id": segment.segment_id,
                    "context": segment.kind,
                    "disposition": _disposition(segment.kind),
                    "source_span": {
                        "codepoint_start": cp_start,
                        "codepoint_end": cp_end,
                    },
                    "matched_text": matched_text,
                    "matched_text_sha256": _sha256_text(matched_text),
                }
                matches.append(match)
                by_context[segment.kind] += 1
                matched_rule_ids.add(rule.rule_id)
                if len(matches) > MAX_REPORT_MATCHES:
                    raise MatchLimitError(
                        f"match count exceeds {MAX_REPORT_MATCHES}; partial output is forbidden"
                    )
    deduplicated: dict[tuple[Any, ...], dict[str, Any]] = {}
    for match in matches:
        key = (
            match["pattern_id"],
            match["segment_id"],
            match["source_span"]["codepoint_start"],
            match["source_span"]["codepoint_end"],
        )
        deduplicated[key] = match
    matches = sorted(
        deduplicated.values(),
        key=lambda item: (
            item["source_span"]["codepoint_start"],
            item["source_span"]["codepoint_end"],
            item["pattern_id"],
            item["segment_id"],
        ),
    )
    offsets = _selected_byte_offsets(
        text,
        (
            endpoint
            for match in matches
            for endpoint in (
                match["source_span"]["codepoint_start"],
                match["source_span"]["codepoint_end"],
            )
        ),
    )
    for match in matches:
        span = match["source_span"]
        span["utf8_start"] = offsets[span["codepoint_start"]]
        span["utf8_end"] = offsets[span["codepoint_end"]]
    # Recompute after de-duplication so the two declared counts cannot drift.
    by_context = {context: 0 for context in CONTEXTS}
    for match in matches:
        by_context[match["context"]] += 1
    counts = {
        "rules_evaluated": len(bundle.rules),
        "matched_rule_count": len({item["pattern_id"] for item in matches}),
        "rule_match_count": len(matches),
        "unique_instance_count": _unique_instance_count(matches),
        "segments_total": len(segments),
        "unknown_segments": sum(1 for item in segments if item.kind == "unknown"),
        "matches_by_context": by_context,
    }
    return matches, counts


def _empty_counts(*, rules_evaluated: int = 0) -> dict[str, Any]:
    return {
        "rules_evaluated": rules_evaluated,
        "matched_rule_count": 0,
        "rule_match_count": 0,
        "unique_instance_count": 0,
        "segments_total": 0,
        "unknown_segments": 0,
        "matches_by_context": {context: 0 for context in CONTEXTS},
    }


def _snapshot_binding(state: SnapshotState) -> dict[str, Any]:
    bundle = state.bundle
    if bundle is None:
        return {
            "status": state.status,
            "reason_code": state.reason_code,
            "snapshot_sha256": state.snapshot_sha256,
            "manifest_sha256": state.manifest_sha256,
            "snapshot_id": None,
            "source": None,
            "supply_mode": None,
            "snapshot_schema_version": None,
            "grammar_profile": None,
            "normalizer_profile": None,
            "unicode_data_version": unicodedata.unidata_version,
            "rule_count": None,
            "unsupported_rule_count": None,
            "rights": None,
        }
    manifest = bundle.manifest
    return {
        "status": "loaded",
        "reason_code": "CHECK_COMPLETED",
        "snapshot_sha256": bundle.snapshot_sha256,
        "manifest_sha256": bundle.manifest_sha256,
        "snapshot_id": manifest["snapshot_id"],
        "source": copy.deepcopy(manifest["source"]),
        "supply_mode": manifest["supply_mode"],
        "snapshot_schema_version": manifest["snapshot_schema_version"],
        "grammar_profile": manifest["grammar_profile"],
        "normalizer_profile": manifest["normalizer_profile"],
        "unicode_data_version": bundle.unicode_data_version,
        "rule_count": manifest["rule_count"],
        "unsupported_rule_count": manifest["unsupported_rule_count"],
        "rights": copy.deepcopy(manifest["rights"]),
    }


def _boundary() -> dict[str, Any]:
    return {
        "list_match_only": True,
        "origin_inference": "not_performed",
        "contextual_judgment": "not_performed",
        "automatic_rewrite": False,
        "absence_is_clean_certificate": False,
        "native_pps_compatibility": "not_claimed",
        "sharing_scope": "local_only",
    }


def _report_digest(report: dict[str, Any]) -> str:
    payload = copy.deepcopy(report)
    payload.pop("report_sha256", None)
    return _sha256_text(_canonical_json(payload))


def build_own_draft_report(
    text: str,
    *,
    artifact_id: str,
    artifact_format: str,
    state: SnapshotState,
    checked_at: str,
    recorded_at: str,
) -> dict[str, Any]:
    if not isinstance(text, str):
        raise ScreeningError("draft text must be a string")
    _reject_unsafe_text(text, "draft text")
    _reject_isolated_carriage_returns(text, "draft text")
    encoded = text.encode("utf-8", errors="strict")
    if len(encoded) > MAX_DOCUMENT_BYTES:
        raise ScreeningError(f"draft exceeds {MAX_DOCUMENT_BYTES} bytes")
    if not isinstance(artifact_id, str) or not artifact_id or len(artifact_id) > 256:
        raise ScreeningError("artifact_id must contain 1..256 characters")
    if any(char in artifact_id for char in "\r\n"):
        raise ScreeningError("artifact_id must be a single line")
    if artifact_format not in {"markdown", "latex"}:
        raise ScreeningError("artifact_format must be markdown or latex")
    checked_at = _timestamp(checked_at, "checked_at")
    recorded_at = _timestamp(recorded_at, "recorded_at")
    _ordered_timestamps(checked_at, recorded_at)
    artifact_sha = _sha256_bytes(encoded)
    matches: list[dict[str, Any]] = []
    counts = _empty_counts(
        rules_evaluated=len(state.bundle.rules) if state.bundle is not None else 0
    )
    reason_code = state.reason_code
    check_status = "not_checked" if state.status == "not_checked" else "degraded"
    finding = "unresolved"
    if not text.strip() and state.bundle is not None:
        counts = _empty_counts()
        check_status = "degraded"
        finding = "unresolved"
        reason_code = "DOCUMENT_EMPTY"
    elif state.bundle is not None:
        try:
            segments = segment_document(text, artifact_format)
            if len(segments) > MAX_SEGMENTS:
                raise MatchLimitError(
                    f"segment count exceeds {MAX_SEGMENTS}; partial parsing is forbidden"
                )
            matches, counts = scan_segments(
                text,
                segments,
                state.bundle,
                artifact_sha256=artifact_sha,
                surface="own_draft",
            )
            if counts["unknown_segments"]:
                check_status = "degraded"
                finding = "unresolved"
                reason_code = "DOCUMENT_PARSE_DEGRADED"
            else:
                check_status = "checked"
                finding = "detected" if matches else "not_detected"
                reason_code = "CHECK_COMPLETED"
        except MatchLimitError:
            matches = []
            counts = _empty_counts()
            check_status = "degraded"
            finding = "unresolved"
            reason_code = "MATCH_RESOURCE_LIMIT"
    report: dict[str, Any] = {
        "schema_version": ADVISORY_VERSION,
        "layer": LAYER,
        "evaluation_status": EVALUATION_STATUS,
        "surface": "own_draft",
        "input_binding": {
            "artifact": {
                "artifact_id": artifact_id,
                "artifact_format": artifact_format,
                "artifact_sha256": artifact_sha,
                "artifact_utf8_bytes": len(encoded),
            },
            "snapshot": _snapshot_binding(state),
            "checked_at": checked_at,
            "recorded_at": recorded_at,
        },
        "check_status": check_status,
        "finding": finding,
        "reason_code": reason_code,
        "counts": counts,
        "matches": matches,
        "boundary": _boundary(),
        "report_sha256": "0" * 64,
    }
    report["report_sha256"] = _report_digest(report)
    if len(_pretty_json_bytes(report)) > MAX_ADVISORY_BYTES:
        report["check_status"] = "degraded"
        report["finding"] = "unresolved"
        report["reason_code"] = "MATCH_RESOURCE_LIMIT"
        report["counts"] = _empty_counts()
        report["matches"] = []
        report["report_sha256"] = _report_digest(report)
    _require_schema(report, ADVISORY_SCHEMA_PATH, "own-draft advisory")
    return report


def validate_own_draft_report(
    report: dict[str, Any],
    text: str,
    *,
    state: SnapshotState,
) -> None:
    _require_schema(report, ADVISORY_SCHEMA_PATH, "own-draft advisory")
    if report.get("report_sha256") != _report_digest(report):
        raise ScreeningError("own-draft advisory report_sha256 mismatch")
    binding = report["input_binding"]
    artifact = binding["artifact"]
    rebuilt = build_own_draft_report(
        text,
        artifact_id=artifact["artifact_id"],
        artifact_format=artifact["artifact_format"],
        state=state,
        checked_at=binding["checked_at"],
        recorded_at=binding["recorded_at"],
    )
    if _canonical_json(rebuilt) != _canonical_json(report):
        raise ScreeningError(
            "own-draft advisory does not replay from the exact draft/snapshot inputs"
        )


def _markdown_cell(value: Any, *, maximum: int = 1000) -> str:
    if value is None or value == "":
        return "—"
    rendered = str(value).replace("\r", " ").replace("\n", " ")
    rendered = "".join(
        char
        if unicodedata.category(char) not in {"Cc", "Cf", "Zl", "Zp"}
        else f"U+{ord(char):04X}"
        for char in rendered
    )
    if len(rendered) > maximum:
        rendered = rendered[: maximum - 1] + "…"
    rendered = html.escape(rendered, quote=False)
    for char in ("\\", "|", "`", "[", "]", "!", "*"):
        rendered = rendered.replace(char, "\\" + char)
    return rendered


def render_own_draft_report(
    report: dict[str, Any],
    text: str,
    *,
    state: SnapshotState,
) -> str:
    validate_own_draft_report(report, text, state=state)
    matches = report["matches"]
    selected = matches[:MAX_RENDER_PAGE_SIZE]
    omitted = len(matches) - len(selected)
    counts = report["counts"]
    if report["finding"] == "detected":
        outcome = (
            f"**{SUMMARY_LABEL}.** A match does not establish papermill, AI, or author origin."
        )
    elif report["finding"] == "not_detected":
        outcome = (
            "**No phrase-list match observed on the checked surface.** "
            "Absence is not a clean-text certificate."
        )
    else:
        outcome = (
            "**Phrase-list screening is unresolved.** No clean or origin conclusion "
            "may be drawn from this result."
        )
    lines = [
        "# Tortured-phrase screening advisory",
        "",
        f"Layer: `{LAYER}`  ",
        f"Evaluation status: `{EVALUATION_STATUS}`  ",
        f"Check status: `{_markdown_cell(report['check_status'])}`  ",
        f"Finding: `{_markdown_cell(report['finding'])}`  ",
        f"Reason: `{_markdown_cell(report['reason_code'])}`",
        "",
        outcome,
        (
            "Zero matches means only that no configured pattern matched a fully checked "
            "surface; absence is not a clean-text certificate."
        ),
        "",
        (
            f"Rules evaluated: {counts['rules_evaluated']}; matched rules: "
            f"{counts['matched_rule_count']}; rule matches: {counts['rule_match_count']}; "
            f"unique overlap-components: {counts['unique_instance_count']}."
        ),
        "",
        "| match | pattern | context | disposition | UTF-8 span | matched text |",
        "|---|---|---|---|---|---|",
    ]
    for match in selected:
        span = match["source_span"]
        lines.append(
            "| {match_id} | {pattern_id} | {context} | {disposition} | {start}:{end} | {text} |".format(
                match_id=_markdown_cell(match["match_id"]),
                pattern_id=_markdown_cell(match["pattern_id"]),
                context=_markdown_cell(match["context"]),
                disposition=_markdown_cell(match["disposition"]),
                start=span["utf8_start"],
                end=span["utf8_end"],
                text=_markdown_cell(match["matched_text"]),
            )
        )
    if not selected:
        lines.append("| — | — | — | — | — | No match rows on this page. |")
    lines.extend(
        [
            "",
            (
                f"Showing {len(selected)} of {len(matches)} match rows; omitted "
                f"{omitted}; the renderer has one fixed page capped at "
                f"{MAX_RENDER_PAGE_SIZE}."
            ),
        ]
    )
    if omitted:
        lines.append(
            "Complete machine JSON replay key: artifact_id={artifact_id}; "
            "report_sha256={report_sha256}.".format(
                artifact_id=_markdown_cell(
                    report["input_binding"]["artifact"]["artifact_id"], maximum=256
                ),
                report_sha256=report["report_sha256"],
            )
        )
    return "\n".join(lines) + "\n"


def _signal_id(
    citation_key: str,
    surface: str,
    snapshot_sha256: str | None,
    content_sha256: str | None,
) -> str:
    payload = {
        "citation_key": citation_key,
        "surface": surface,
        "snapshot_sha256": snapshot_sha256,
        "content_sha256": content_sha256,
    }
    suffix = _sha256_text(_canonical_json(payload))[:20]
    surface_slug = "title" if surface == "cited_title" else "abstract"
    return f"bis:{citation_key}:tpm_{surface_slug}_{suffix}"


def _cited_surface_result(
    text: str | None,
    *,
    surface: str,
    state: SnapshotState,
    citation_key: str,
    work_budget: MatchWorkBudget | None = None,
) -> tuple[str, str, str, list[dict[str, Any]], dict[str, Any], str | None, int | None]:
    if text is None:
        return (
            "not_checked",
            "unresolved",
            "ABSTRACT_MISSING",
            [],
            _empty_counts(),
            None,
            None,
        )
    if text.strip() == "":
        return (
            "not_checked",
            "unresolved",
            "ABSTRACT_EMPTY",
            [],
            _empty_counts(),
            None,
            None,
        )
    encoded = text.encode("utf-8", errors="strict")
    content_sha = _sha256_bytes(encoded)
    if state.bundle is None:
        return (
            "not_checked" if state.status == "not_checked" else "degraded",
            "unresolved",
            state.reason_code,
            [],
            _empty_counts(),
            content_sha,
            len(encoded),
        )
    context = "cited_title" if surface == "cited_title" else "cited_abstract"
    try:
        matches, counts = scan_segments(
            text,
            [Segment("SEG-000001", context, 0, len(text))],
            state.bundle,
            artifact_sha256=content_sha,
            surface=surface,
            work_budget=work_budget,
        )
    except MatchLimitError:
        return (
            "degraded",
            "unresolved",
            "MATCH_RESOURCE_LIMIT",
            [],
            _empty_counts(),
            content_sha,
            len(encoded),
        )
    return (
        "checked",
        "detected" if matches else "not_detected",
        "CHECK_COMPLETED",
        matches,
        counts,
        content_sha,
        len(encoded),
    )


def build_cited_signal(
    entry: dict[str, Any],
    *,
    surface: str,
    state: SnapshotState,
    checked_at: str,
    recorded_at: str,
    work_budget: MatchWorkBudget | None = None,
) -> dict[str, Any]:
    checked_at = _timestamp(checked_at, "checked_at")
    recorded_at = _timestamp(recorded_at, "recorded_at")
    _ordered_timestamps(checked_at, recorded_at)
    citation_key = entry.get("citation_key")
    source_pointer = entry.get("source_pointer")
    if not isinstance(citation_key, str) or not citation_key:
        raise ScreeningError("corpus entry requires citation_key")
    if not isinstance(source_pointer, str) or not source_pointer:
        raise ScreeningError("corpus entry requires source_pointer")
    if surface == "cited_title":
        text = entry.get("title")
        if not isinstance(text, str) or not text.strip():
            raise ScreeningError(f"{citation_key}: title must be a non-empty string")
    elif surface == "cited_abstract":
        value = entry.get("abstract")
        if value is not None and not isinstance(value, str):
            raise ScreeningError(f"{citation_key}: abstract must be a string when present")
        text = value
    else:
        raise ScreeningError("cited surface must be cited_title or cited_abstract")
    if text is not None:
        _reject_unsafe_text(text, f"{citation_key}.{surface}")
        _reject_isolated_carriage_returns(text, f"{citation_key}.{surface}")
    (
        status,
        finding,
        reason_code,
        matches,
        counts,
        content_sha,
        content_bytes,
    ) = _cited_surface_result(
        text,
        surface=surface,
        state=state,
        citation_key=citation_key,
        work_budget=work_budget,
    )
    binding = _snapshot_binding(state)
    source = binding.get("source") or {}
    source_name = source.get("name") or "tortured-phrase snapshot unavailable"
    source_version = source.get("version")
    evidence_type = (
        "phrase_match"
        if status == "checked" and finding == "detected"
        else "list_record"
        if status == "checked"
        else "degradation_record"
    )
    evidence_value: Any = counts["rule_match_count"] if status == "checked" else reason_code
    signal = {
        "schema_version": SIGNAL_VERSION,
        "signal_id": _signal_id(
            citation_key, surface, state.snapshot_sha256, content_sha
        ),
        "signal_type": "tortured_phrase_match",
        "epistemic_class": "heuristic_advisory",
        "epistemic_label": "HEURISTIC-INDICATOR",
        "check_status": status,
        "finding": finding,
        "evidence": [
            {
                "evidence_type": evidence_type,
                "source_name": source_name,
                "record_locator": "title" if surface == "cited_title" else "abstract",
                "observed_value": evidence_value,
                "evidence_sha256": content_sha,
            }
        ],
        "provenance": {
            "source_name": source_name,
            "source_version": source_version,
            "source_sha256": state.snapshot_sha256,
            "checked_at": checked_at if status != "not_checked" else None,
            "recorded_at": recorded_at,
            "stale_after": None,
            "freshness": "unknown",
        },
        "subject": {
            "citation_key": citation_key,
            "source_pointer": source_pointer,
            "affected_claims": [],
        },
        "terminal_policy": {
            "eligible": False,
            "owner": "none",
            "policy_key": None,
            "current_effect": "advisory_only",
        },
        "display": {
            "carrier": "provenance_summary",
            "section": "Bibliographic Integrity Advisories",
            "summary_label": ADVISORY_LABEL,
            "marker_token": None,
        },
        "tortured_phrase_context": {
            "layer": LAYER,
            "evaluation_status": EVALUATION_STATUS,
            "surface": surface,
            "surface_binding": {
                "content_sha256": content_sha,
                "content_utf8_bytes": content_bytes,
            },
            "snapshot": binding,
            "reason_code": reason_code,
            "counts": counts,
            "matches": matches,
            "boundary": _boundary(),
        },
    }
    _require_schema(signal, SIGNAL_SCHEMA_PATH, "tortured-phrase cited signal")
    return signal


def validate_cited_signal_binding(signal: dict[str, Any], entry: dict[str, Any]) -> None:
    """Replay source/hash/id invariants that do not require the local ruleset."""

    if signal.get("signal_type") != "tortured_phrase_match":
        return
    context = signal.get("tortured_phrase_context")
    if not isinstance(context, dict):
        # Legacy v1.0 compatibility rows are intentionally not upgraded here.
        return
    _require_schema(signal, SIGNAL_SCHEMA_PATH, "tortured-phrase cited signal")
    subject = signal.get("subject")
    if not isinstance(subject, dict):
        raise ScreeningError("tortured-phrase signal subject must be an object")
    if subject.get("citation_key") != entry.get("citation_key"):
        raise ScreeningError("tortured-phrase signal citation_key join mismatch")
    if subject.get("source_pointer") != entry.get("source_pointer"):
        raise ScreeningError("tortured-phrase signal source_pointer join mismatch")
    surface = context.get("surface")
    if surface == "cited_title":
        value = entry.get("title")
    elif surface == "cited_abstract":
        value = entry.get("abstract")
    else:
        raise ScreeningError("tortured-phrase signal has unsupported surface")
    surface_binding = context.get("surface_binding", {})
    if value is None or (isinstance(value, str) and not value.strip()):
        expected_sha = None
        expected_bytes = None
    elif isinstance(value, str):
        raw = value.encode("utf-8", errors="strict")
        expected_sha = _sha256_bytes(raw)
        expected_bytes = len(raw)
    else:
        raise ScreeningError("bound corpus surface must be a string")
    if surface_binding.get("content_sha256") != expected_sha:
        raise ScreeningError("tortured-phrase signal content_sha256 is stale")
    if surface_binding.get("content_utf8_bytes") != expected_bytes:
        raise ScreeningError("tortured-phrase signal content byte length is stale")
    snapshot_sha = context.get("snapshot", {}).get("snapshot_sha256")
    expected_id = _signal_id(
        entry["citation_key"], surface, snapshot_sha, expected_sha
    )
    if signal.get("signal_id") != expected_id:
        raise ScreeningError("tortured-phrase signal_id binding mismatch")
    matches = context.get("matches", [])
    if not isinstance(matches, list):
        raise ScreeningError("tortured-phrase matches must be an array")
    replay_text = value or ""
    endpoints = {
        endpoint
        for match in matches
        if isinstance(match, dict)
        and isinstance(match.get("source_span"), dict)
        for endpoint in (
            match["source_span"].get("codepoint_start"),
            match["source_span"].get("codepoint_end"),
        )
        if isinstance(endpoint, int) and not isinstance(endpoint, bool)
    }
    offsets = _selected_byte_offsets(replay_text, endpoints)
    seen_match_ids: set[str] = set()
    artifact_sha = expected_sha or _sha256_bytes(b"")
    snapshot_sha_for_match = context.get("snapshot", {}).get("snapshot_sha256")
    expected_context = surface
    expected_disposition = (
        "preserve_verbatim_review_context"
        if surface == "cited_title"
        else "review_cited_source_no_automatic_rewrite"
    )
    for index, match in enumerate(matches):
        if match.get("segment_id") != "SEG-000001":
            raise ScreeningError(
                f"tortured-phrase matches[{index}] segment_id must be SEG-000001"
            )
        if match.get("context") != expected_context:
            raise ScreeningError(
                f"tortured-phrase matches[{index}] context does not match surface"
            )
        if match.get("disposition") != expected_disposition:
            raise ScreeningError(
                f"tortured-phrase matches[{index}] disposition does not match surface"
            )
        span = match.get("source_span", {}) if isinstance(match, dict) else {}
        cp_start = span.get("codepoint_start")
        cp_end = span.get("codepoint_end")
        if (
            isinstance(cp_start, bool)
            or isinstance(cp_end, bool)
            or not isinstance(cp_start, int)
            or not isinstance(cp_end, int)
            or not 0 <= cp_start < cp_end <= len(value or "")
        ):
            raise ScreeningError(f"tortured-phrase matches[{index}] has invalid codepoint span")
        matched = (value or "")[cp_start:cp_end]
        if len(matched) > MAX_EVIDENCE_CODEPOINTS or len(matched.split()) > MAX_EVIDENCE_WORDS:
            raise ScreeningError(
                f"tortured-phrase matches[{index}] exceeds the evidence bound"
            )
        if span.get("utf8_start") != offsets[cp_start] or span.get("utf8_end") != offsets[cp_end]:
            raise ScreeningError(f"tortured-phrase matches[{index}] UTF-8 span mismatch")
        if match.get("matched_text") != matched:
            raise ScreeningError(f"tortured-phrase matches[{index}] text replay mismatch")
        if match.get("matched_text_sha256") != _sha256_text(matched):
            raise ScreeningError(f"tortured-phrase matches[{index}] text hash mismatch")
        match_id = match.get("match_id")
        expected_match_id = "tpm-" + _sha256_text(
            _canonical_json(
                {
                    "artifact_sha256": artifact_sha,
                    "snapshot_sha256": snapshot_sha_for_match,
                    "surface": surface,
                    "segment_id": match.get("segment_id"),
                    "context": match.get("context"),
                    "rule_id": match.get("pattern_id"),
                    "codepoint_start": cp_start,
                    "codepoint_end": cp_end,
                }
            )
        )[:24]
        if match_id != expected_match_id:
            raise ScreeningError(f"tortured-phrase matches[{index}] match_id mismatch")
        if match_id in seen_match_ids:
            raise ScreeningError(f"tortured-phrase matches[{index}] duplicates match_id")
        seen_match_ids.add(match_id)
    counts = context.get("counts", {})
    if counts.get("rule_match_count") != len(matches):
        raise ScreeningError("tortured-phrase rule_match_count mismatch")
    if counts.get("matched_rule_count") != len(
        {item.get("pattern_id") for item in matches if isinstance(item, dict)}
    ):
        raise ScreeningError("tortured-phrase matched_rule_count mismatch")
    if counts.get("matched_rule_count", 0) > counts.get("rules_evaluated", 0):
        raise ScreeningError(
            "tortured-phrase matched_rule_count exceeds rules_evaluated"
        )
    if counts.get("unique_instance_count") != _unique_instance_count(matches):
        raise ScreeningError("tortured-phrase unique_instance_count mismatch")
    matches_by_context = counts.get("matches_by_context")
    if not isinstance(matches_by_context, dict) or any(
        matches_by_context.get(name) != (len(matches) if name == expected_context else 0)
        for name in CONTEXTS
    ):
        raise ScreeningError("tortured-phrase matches_by_context mismatch")
    status = signal.get("check_status")
    reason_code = context.get("reason_code")
    snapshot = context.get("snapshot")
    if not isinstance(snapshot, dict):
        raise ScreeningError("tortured-phrase snapshot binding must be an object")
    if expected_sha is None:
        expected_reason = (
            "ABSTRACT_MISSING" if value is None else "ABSTRACT_EMPTY"
        )
        if (
            surface != "cited_abstract"
            or status != "not_checked"
            or signal.get("finding") != "unresolved"
            or reason_code != expected_reason
            or matches
            or counts != _empty_counts()
        ):
            raise ScreeningError(
                "absent/empty cited abstract must remain explicit not_checked/unresolved"
            )
    elif status == "checked":
        if (
            reason_code != "CHECK_COMPLETED"
            or snapshot.get("status") != "loaded"
            or snapshot.get("reason_code") != "CHECK_COMPLETED"
            or counts.get("rules_evaluated") != snapshot.get("rule_count")
            or counts.get("segments_total") != 1
            or counts.get("unknown_segments") != 0
        ):
            raise ScreeningError(
                "checked cited surface does not prove one complete loaded-snapshot scan"
            )
    else:
        if matches or counts != _empty_counts():
            raise ScreeningError(
                "not-checked/degraded cited surface must discard partial match state"
            )
        if reason_code == "MATCH_RESOURCE_LIMIT":
            if (
                status != "degraded"
                or signal.get("finding") != "unresolved"
                or snapshot.get("status") != "loaded"
                or snapshot.get("reason_code") != "CHECK_COMPLETED"
            ):
                raise ScreeningError(
                    "match resource failure requires a loaded snapshot and degraded output"
                )
        elif (
            reason_code != snapshot.get("reason_code")
            or status != snapshot.get("status")
            or signal.get("finding") != "unresolved"
        ):
            raise ScreeningError(
                "cited surface status/reason does not replay snapshot availability"
            )
    evidence = signal.get("evidence")
    if not isinstance(evidence, list) or len(evidence) != 1 or not isinstance(evidence[0], dict):
        raise ScreeningError("tortured-phrase signal requires exactly one evidence row")
    expected_evidence_type = (
        "phrase_match"
        if signal.get("check_status") == "checked" and signal.get("finding") == "detected"
        else "list_record"
        if signal.get("check_status") == "checked"
        else "degradation_record"
    )
    expected_observed = (
        counts.get("rule_match_count")
        if signal.get("check_status") == "checked"
        else context.get("reason_code")
    )
    row = evidence[0]
    if row.get("evidence_type") != expected_evidence_type:
        raise ScreeningError("tortured-phrase evidence_type mismatch")
    if row.get("record_locator") != (
        "title" if surface == "cited_title" else "abstract"
    ):
        raise ScreeningError("tortured-phrase evidence locator mismatch")
    if signal.get("check_status") == "checked" and (
        isinstance(row.get("observed_value"), bool)
        or not isinstance(row.get("observed_value"), int)
    ):
        raise ScreeningError("checked tortured-phrase evidence count must be an integer")
    if row.get("observed_value") != expected_observed:
        raise ScreeningError("tortured-phrase evidence observed_value mismatch")
    if row.get("evidence_sha256") != expected_sha:
        raise ScreeningError("tortured-phrase evidence hash mismatch")
    provenance = signal.get("provenance")
    if not isinstance(provenance, dict):
        raise ScreeningError("tortured-phrase provenance must be an object")
    if provenance.get("source_sha256") != snapshot_sha:
        raise ScreeningError("tortured-phrase provenance snapshot hash mismatch")
    snapshot_source = context.get("snapshot", {}).get("source")
    expected_source_name = (
        snapshot_source.get("name")
        if isinstance(snapshot_source, dict)
        else "tortured-phrase snapshot unavailable"
    )
    expected_source_version = (
        snapshot_source.get("version") if isinstance(snapshot_source, dict) else None
    )
    if provenance.get("source_name") != expected_source_name:
        raise ScreeningError("tortured-phrase provenance source_name mismatch")
    if provenance.get("source_version") != expected_source_version:
        raise ScreeningError("tortured-phrase provenance source_version mismatch")
    if row.get("source_name") != expected_source_name:
        raise ScreeningError("tortured-phrase evidence source_name mismatch")
    recorded_at = _timestamp(provenance.get("recorded_at"), "provenance.recorded_at")
    checked_value = provenance.get("checked_at")
    if signal.get("check_status") == "not_checked":
        if checked_value is not None:
            raise ScreeningError("not-checked tortured-phrase row must have null checked_at")
    else:
        checked_at = _timestamp(checked_value, "provenance.checked_at")
        _ordered_timestamps(checked_at, recorded_at)


def enrich_passport(
    document: dict[str, Any],
    *,
    state: SnapshotState,
    checked_at: str,
    recorded_at: str,
) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise ScreeningError("passport must be a mapping")
    _reject_nonfinite_recursive(document, path="passport")
    corpus = document.get("literature_corpus")
    if not isinstance(corpus, list):
        raise ScreeningError("passport must contain literature_corpus[]")
    if len(corpus) > MAX_CORPUS_ENTRIES:
        raise MatchLimitError(
            f"literature_corpus contains more than {MAX_CORPUS_ENTRIES} entries"
        )
    existing_signal_count = sum(
        len(entry.get("bibliographic_integrity_signals", []))
        for entry in corpus
        if isinstance(entry, dict)
        and isinstance(entry.get("bibliographic_integrity_signals", []), list)
    )
    if existing_signal_count > MAX_CORPUS_EXISTING_SIGNALS:
        raise MatchLimitError(
            "existing bibliographic-integrity signals exceed "
            f"{MAX_CORPUS_EXISTING_SIGNALS} rows"
        )
    output = copy.deepcopy(document)
    generated_match_count = 0
    work_budget = MatchWorkBudget()
    for index, entry in enumerate(output["literature_corpus"]):
        if not isinstance(entry, dict):
            raise ScreeningError(f"literature_corpus[{index}] must be a mapping")
        _require_schema(
            entry,
            CORPUS_ENTRY_SCHEMA_PATH,
            f"literature_corpus[{index}] input entry",
        )
        citation_key = entry.get("citation_key")
        generated = [
            build_cited_signal(
                entry,
                surface=surface,
                state=state,
                checked_at=checked_at,
                recorded_at=recorded_at,
                work_budget=work_budget,
            )
            for surface in ("cited_title", "cited_abstract")
        ]
        generated_match_count += sum(
            len(signal["tortured_phrase_context"]["matches"])
            for signal in generated
        )
        if generated_match_count > MAX_CORPUS_OUTPUT_MATCHES:
            raise MatchLimitError(
                "corpus output match count exceeds "
                f"{MAX_CORPUS_OUTPUT_MATCHES}"
            )
        existing = entry.get("bibliographic_integrity_signals", [])
        if not isinstance(existing, list):
            raise ScreeningError(
                f"literature_corpus[{index}].bibliographic_integrity_signals must be an array"
            )
        by_id: dict[str, dict[str, Any]] = {}
        current_by_surface: dict[str, list[dict[str, Any]]] = {
            "cited_title": [],
            "cited_abstract": [],
        }
        for signal_index, signal in enumerate(existing):
            if not isinstance(signal, dict) or not isinstance(signal.get("signal_id"), str):
                raise ScreeningError(
                    f"literature_corpus[{index}].bibliographic_integrity_signals[{signal_index}] is invalid"
                )
            _require_schema(
                signal,
                SIGNAL_SCHEMA_PATH,
                f"literature_corpus[{index}].bibliographic_integrity_signals[{signal_index}]",
            )
            signal_id = signal["signal_id"]
            if signal_id in by_id:
                raise ScreeningError(f"duplicate existing signal_id {signal_id!r}")
            by_id[signal_id] = signal
            context = signal.get("tortured_phrase_context")
            if (
                signal.get("schema_version") == SIGNAL_VERSION
                and signal.get("signal_type") == "tortured_phrase_match"
                and isinstance(context, dict)
                and context.get("surface") in current_by_surface
            ):
                subject = signal.get("subject")
                if not isinstance(subject, dict) or subject.get(
                    "citation_key"
                ) != citation_key:
                    raise ScreeningError(
                        "current v1.2 tortured-phrase row citation_key does not "
                        f"belong to corpus entry {citation_key!r}"
                    )
                if subject.get("source_pointer") != entry.get("source_pointer"):
                    raise ScreeningError(
                        "current v1.2 tortured-phrase row source_pointer does not "
                        f"belong to corpus entry {citation_key!r}"
                    )
                try:
                    _validate_existing_phrase_projection(signal)
                except ValueError as exc:
                    raise ScreeningError(
                        "existing current v1.2 tortured-phrase row is internally "
                        f"inconsistent: {exc}"
                    ) from exc
                current_by_surface[context["surface"]].append(signal)
        for surface, current in current_by_surface.items():
            if len(current) > 1:
                raise ScreeningError(
                    f"multiple current v1.2 tortured-phrase rows for {citation_key!r}/{surface}"
                )
        # The explicit enricher is a current-state projection, not a history
        # ledger.  It supersedes at most one prior v1.2 row per surface in the
        # NEW output while preserving every legacy and unrelated signal.
        preserved = [
            signal
            for signal in existing
            if not (
                signal.get("schema_version") == SIGNAL_VERSION
                and signal.get("signal_type") == "tortured_phrase_match"
                and isinstance(signal.get("tortured_phrase_context"), dict)
                and signal["tortured_phrase_context"].get("surface")
                in current_by_surface
            )
        ]
        preserved_ids = {signal["signal_id"] for signal in preserved}
        generated_ids = {signal["signal_id"] for signal in generated}
        collisions = preserved_ids & generated_ids
        if collisions:
            raise ScreeningError(
                f"generated tortured-phrase signal_id collides with preserved row(s): "
                f"{sorted(collisions)}"
            )
        entry["bibliographic_integrity_signals"] = preserved + sorted(
            generated, key=lambda item: item["signal_id"]
        )
        _require_schema(
            entry,
            CORPUS_ENTRY_SCHEMA_PATH,
            f"literature_corpus[{index}] enriched entry",
        )
        for signal in generated:
            validate_cited_signal_binding(signal, entry)
    return output


def _degraded_corpus_reasons(document: dict[str, Any]) -> list[str]:
    """Return reasons from current v1.2 rows degraded by this projection."""

    reasons: set[str] = set()
    for entry in document.get("literature_corpus", []):
        if not isinstance(entry, dict):
            continue
        for signal in entry.get("bibliographic_integrity_signals", []):
            if not isinstance(signal, dict):
                continue
            context = signal.get("tortured_phrase_context")
            if (
                signal.get("schema_version") == SIGNAL_VERSION
                and signal.get("signal_type") == "tortured_phrase_match"
                and signal.get("check_status") == "degraded"
                and isinstance(context, dict)
            ):
                reason = context.get("reason_code")
                reasons.add(reason if isinstance(reason, str) else "UNKNOWN")
    return sorted(reasons)


def _read_strict_text(path: Path, *, maximum: int, label: str) -> str:
    try:
        raw = _read_bounded_bytes(path, maximum=maximum)
    except OSError as exc:
        raise ScreeningError(f"cannot read {label} {path}: {exc}") from exc
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ScreeningError(f"{label} must not carry a UTF-8 BOM")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ScreeningError(f"{label} is not strict UTF-8: {exc}") from exc
    _reject_unsafe_text(text, label)
    _reject_isolated_carriage_returns(text, label)
    return text


def _reject_nonfinite_recursive(
    value: Any,
    *,
    path: str = "passport",
    seen_containers: set[int] | None = None,
) -> None:
    """Reject unsafe scalar/container states with bounded iterative traversal."""

    if seen_containers is None:
        seen_containers = set()
    stack: list[tuple[Any, str, int]] = [(value, path, 0)]
    nodes_seen = 0
    while stack:
        item, item_path, depth = stack.pop()
        nodes_seen += 1
        if nodes_seen > MAX_STRUCTURE_NODES:
            raise MatchLimitError(
                f"{path} structure exceeds {MAX_STRUCTURE_NODES} nodes"
            )
        if depth > MAX_STRUCTURE_DEPTH:
            raise MatchLimitError(
                f"{path} structure exceeds depth {MAX_STRUCTURE_DEPTH}"
            )
        if isinstance(item, float) and not math.isfinite(item):
            raise ScreeningError(f"{item_path} contains a non-finite number")
        if isinstance(item, dict):
            identity = id(item)
            if identity in seen_containers:
                raise ScreeningError("shared or recursive YAML aliases are forbidden")
            seen_containers.add(identity)
            if nodes_seen + len(stack) + 2 * len(item) > MAX_STRUCTURE_NODES:
                raise MatchLimitError(
                    f"{path} structure exceeds {MAX_STRUCTURE_NODES} nodes"
                )
            folded: dict[str, str] = {}
            children: list[tuple[Any, str, int]] = []
            for key, child in item.items():
                if not isinstance(key, str):
                    raise ScreeningError(
                        f"{item_path} contains a non-string mapping key"
                    )
                _reject_unsafe_text(key, f"{item_path} key")
                nodes_seen += 1
                normalized = unicodedata.normalize("NFKC", key).casefold()
                if normalized in folded:
                    raise ScreeningError(
                        f"{item_path} has fold-colliding keys "
                        f"{folded[normalized]!r} and {key!r}"
                    )
                folded[normalized] = key
                children.append((child, f"{item_path}.{key}", depth + 1))
            stack.extend(reversed(children))
        elif isinstance(item, list):
            identity = id(item)
            if identity in seen_containers:
                raise ScreeningError("shared or recursive YAML aliases are forbidden")
            seen_containers.add(identity)
            if nodes_seen + len(stack) + len(item) > MAX_STRUCTURE_NODES:
                raise MatchLimitError(
                    f"{path} structure exceeds {MAX_STRUCTURE_NODES} nodes"
                )
            for index in range(len(item) - 1, -1, -1):
                stack.append((item[index], f"{item_path}[{index}]", depth + 1))
        elif isinstance(item, str):
            _reject_unsafe_text(item, item_path)


def _load_passport(path: Path) -> tuple[dict[str, Any], str]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        value, _ = _strict_json_path(
            path, label="passport", maximum=MAX_PASSPORT_BYTES
        )
        kind = "json"
    else:
        text = _read_strict_text(
            path, maximum=MAX_PASSPORT_BYTES, label="passport"
        )
        _preflight_yaml_structure(text, label="passport")
        loader = YAML(typ="rt")
        loader.allow_duplicate_keys = False
        loader.preserve_quotes = True
        try:
            value = loader.load(text)
        except Exception as exc:
            raise ScreeningError(f"passport is not strict YAML: {exc}") from exc
        kind = "yaml"
    if not isinstance(value, dict):
        raise ScreeningError("passport must be a top-level mapping")
    _reject_nonfinite_recursive(value)
    return value, kind


def _atomic_write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            temporary.unlink()
        except OSError:
            pass
        raise


def _atomic_write_json(
    path: Path,
    value: Any,
    *,
    maximum: int | None = None,
) -> None:
    payload = _pretty_json_bytes(value)
    if maximum is not None and len(payload) > maximum:
        raise ScreeningError(f"serialized output exceeds {maximum} bytes")
    _atomic_write_bytes(path, payload)


def _atomic_write_passport(path: Path, value: dict[str, Any], kind: str) -> None:
    _reject_nonfinite_recursive(value, path="passport output")
    if kind == "json" or path.suffix.lower() == ".json":
        _atomic_write_json(path, value, maximum=MAX_PASSPORT_BYTES)
        return
    emitter = YAML(typ="rt")
    emitter.preserve_quotes = True
    emitter.indent(mapping=2, sequence=4, offset=2)
    buffer = StringIO()
    emitter.dump(value, buffer)
    payload = buffer.getvalue().encode("utf-8")
    if len(payload) > MAX_PASSPORT_BYTES:
        raise ScreeningError(
            f"serialized passport exceeds {MAX_PASSPORT_BYTES} bytes"
        )
    _atomic_write_bytes(path, payload)


def _state_from_args(args: argparse.Namespace) -> SnapshotState:
    return snapshot_state(args.snapshot, args.snapshot_manifest)


def _add_snapshot_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--snapshot",
        type=Path,
        help="Exact local canonical snapshot JSON; omit only for explicit not-checked output.",
    )
    parser.add_argument(
        "--snapshot-manifest",
        type=Path,
        help="Detached manifest that hash-binds --snapshot; must travel with it.",
    )


def _add_draft_replay_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--format", choices=("markdown", "latex"), required=True)
    _add_snapshot_args(parser)


def _load_report(path: Path) -> dict[str, Any]:
    value, _ = _strict_json_path(
        path, label="own-draft advisory", maximum=MAX_ADVISORY_BYTES
    )
    if not isinstance(value, dict):
        raise ScreeningError("own-draft advisory must be a JSON object")
    return value


def _same_path(left: Path, right: Path) -> bool:
    try:
        if left.exists() and right.exists() and os.path.samefile(left, right):
            return True
        return left.resolve(strict=False) == right.resolve(strict=False)
    except OSError:
        return os.path.abspath(left) == os.path.abspath(right)


def _reject_output_alias(output: Path, named_inputs: Iterable[Path | None]) -> None:
    for candidate in named_inputs:
        if candidate is not None and _same_path(output, candidate):
            raise ScreeningError(
                "output refuses in-place or named-input alias: "
                f"{output} is also an input artifact"
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_snapshot_parser = subparsers.add_parser(
        "validate-snapshot", help="Validate and hash-bind one local snapshot."
    )
    validate_snapshot_parser.add_argument("--snapshot", type=Path, required=True)
    validate_snapshot_parser.add_argument(
        "--snapshot-manifest", type=Path, required=True
    )

    scan_parser = subparsers.add_parser(
        "scan-draft", help="Build a closed own-draft advisory report."
    )
    _add_draft_replay_args(scan_parser)
    scan_parser.add_argument("--checked-at", required=True)
    scan_parser.add_argument("--recorded-at", required=True)
    scan_parser.add_argument("--output", type=Path, required=True)

    validate_parser = subparsers.add_parser(
        "validate-draft", help="Replay a draft advisory against exact inputs."
    )
    _add_draft_replay_args(validate_parser)
    validate_parser.add_argument("--report", type=Path, required=True)

    render_parser = subparsers.add_parser(
        "render-draft", help="Replay then render the one bounded advisory page."
    )
    _add_draft_replay_args(render_parser)
    render_parser.add_argument("--report", type=Path, required=True)

    enrich_parser = subparsers.add_parser(
        "enrich-passport",
        help="Write a new passport with title/abstract advisory rows; never in place.",
    )
    enrich_parser.add_argument("--input", type=Path, required=True)
    enrich_parser.add_argument("--output", type=Path, required=True)
    _add_snapshot_args(enrich_parser)
    enrich_parser.add_argument("--checked-at", required=True)
    enrich_parser.add_argument("--recorded-at", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "validate-snapshot":
            bundle = load_snapshot(args.snapshot, args.snapshot_manifest)
            print(
                "Tortured-phrase snapshot: ok "
                f"rules={len(bundle.rules)} sha256={bundle.snapshot_sha256}"
            )
            return 0

        if args.command == "scan-draft":
            _reject_output_alias(
                args.output,
                (args.input, args.snapshot, args.snapshot_manifest),
            )
        elif args.command == "enrich-passport":
            _reject_output_alias(
                args.output,
                (args.input, args.snapshot, args.snapshot_manifest),
            )

        state = _state_from_args(args)
        if args.command in {"scan-draft", "validate-draft", "render-draft"}:
            text = _read_strict_text(
                args.input, maximum=MAX_DOCUMENT_BYTES, label="draft"
            )
            if args.command == "scan-draft":
                report = build_own_draft_report(
                    text,
                    artifact_id=args.artifact_id,
                    artifact_format=args.format,
                    state=state,
                    checked_at=args.checked_at,
                    recorded_at=args.recorded_at,
                )
                _atomic_write_json(
                    args.output, report, maximum=MAX_ADVISORY_BYTES
                )
                if report.get("check_status") == "degraded":
                    print(
                        "ERROR: wrote degraded advisory: "
                        f"{report.get('reason_code', 'UNKNOWN')}",
                        file=sys.stderr,
                    )
                    return 1
                return 0
            report = _load_report(args.report)
            validate_own_draft_report(report, text, state=state)
            if args.command == "render-draft":
                print(
                    render_own_draft_report(
                        report,
                        text,
                        state=state,
                    ),
                    end="",
                )
            return 0

        if args.command == "enrich-passport":
            document, kind = _load_passport(args.input)
            output = enrich_passport(
                document,
                state=state,
                checked_at=args.checked_at,
                recorded_at=args.recorded_at,
            )
            _atomic_write_passport(args.output, output, kind)
            degraded_reasons = _degraded_corpus_reasons(output)
            if degraded_reasons:
                print(
                    "ERROR: wrote degraded corpus advisories: "
                    + ", ".join(degraded_reasons),
                    file=sys.stderr,
                )
                return 1
            return 0
        raise ScreeningError(f"unsupported command {args.command!r}")
    except ScreeningError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except RecursionError:
        print(
            "ERROR: input structure exceeds the supported nesting limit",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
