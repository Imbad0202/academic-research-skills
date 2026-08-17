#!/usr/bin/env python3
"""Build and replay-validate a bounded E1 Claim Registry coverage report.

The detector enumerates citation-bearing and quantitative sentence candidates,
records their bounded lexical trigger spans, and joins them only to exact,
byte-bound Claim Registry spans. A sentence is clean only when one registered
span equals the full sentence and every trigger is inside a registered span;
partial same-sentence registration remains an unresolved candidate. It does
not extract semantic claims and always reports semantic completeness as unknown.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml
from jsonschema import Draft202012Validator
from yaml.constructor import ConstructorError


REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_SCHEMA_PATH = REPO_ROOT / "shared/contracts/evidence/claim_registry.schema.json"
REPORT_SCHEMA_PATH = (
    REPO_ROOT / "shared/contracts/evidence/claim_registry_coverage_report.schema.json"
)
REGISTRY_VERSION = "claim-registry/1.0"
REPORT_VERSION = "claim-registry-coverage/1.0"

_SENTENCE_BREAK = re.compile(r"(?<=[.!?。！？])\s+")
_MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\([^)]+\)")
_NUMERIC_CITATION = re.compile(r"\[(?:\s*\d+\s*[,;–—-]?)+\]")
_AUTHOR_YEAR = re.compile(r"\([^)]*[A-Z][^)]*,\s*(?:19|20)\d{2}[a-z]?[^)]*\)")
_NARRATIVE_AUTHOR_YEAR = re.compile(
    r"(?<![@\w])[A-Z][\w'’-]+"
    r"(?:\s+(?:and|&)\s+[A-Z][\w'’-]+|\s+et\s+al\.)?"
    r"\s*\((?:19|20)\d{2}[a-z]?\)"
)
_PANDOC_CITATION = re.compile(r"\[[^\]\n]*@[-\w:.]+[^\]\n]*\]")
_INLINE_REF = re.compile(r"<!--ref:[^>]+-->")
_QUANTITATIVE = re.compile(
    r"(?:\b\d+(?:[.,]\d+)?\s*(?:%|percent|percentage|participants?|cases?|observations?|items?|points?|times?|fold)\b|\bp\s*[<=>]\s*0?\.\d+\b)",
    re.IGNORECASE,
)
_SAMPLE_SIZE = re.compile(r"(?<!\w)[Nn]\s*=\s*\d+(?:[,_]\d+)*\b")
_EFFECT_SIZE = re.compile(
    r"(?<!\w)(?:Cohen['’]?s\s+d|Hedges['’]?\s+g|odds\s+ratio|"
    r"risk\s+ratio|hazard\s+ratio|OR|RR|HR|R(?:\^?2|²)|[dgr]|β|beta|"
    r"eta(?:[- ]?squared)?|η[2²])\s*(?:=|of|was)?\s*"
    r"-?(?:\d+(?:\.\d+)?|\.\d+)\b",
    re.IGNORECASE,
)


class CoverageError(ValueError):
    """Raised when an input or replay artifact is invalid."""


class _UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: _UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_path(parts: Iterable[Any]) -> str:
    rendered = "$"
    for part in parts:
        rendered += f"[{part}]" if isinstance(part, int) else f".{part}"
    return rendered


def _load_schema(path: Path) -> dict[str, Any]:
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


def _schema_errors(value: Any, path: Path) -> list[str]:
    validator = Draft202012Validator(_load_schema(path))
    errors = sorted(
        validator.iter_errors(value), key=lambda error: list(error.absolute_path)
    )
    return [f"{_json_path(error.absolute_path)}: {error.message}" for error in errors]


def _decode_utf8(raw: bytes, label: str) -> str:
    try:
        return raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise CoverageError(f"{label} is not strict UTF-8: {exc}") from exc


def _load_registry(raw: bytes) -> dict[str, Any]:
    text = _decode_utf8(raw, "registry")
    try:
        value = yaml.load(text, Loader=_UniqueKeyLoader)
    except (yaml.YAMLError, ConstructorError) as exc:
        raise CoverageError(f"cannot parse registry: {exc}") from exc
    if not isinstance(value, dict):
        raise CoverageError("registry root must be an object")
    errors = _schema_errors(value, REGISTRY_SCHEMA_PATH)
    if errors:
        raise CoverageError("registry schema invalid: " + "; ".join(errors))
    return value


def _candidate_kinds(sentence: str) -> list[str]:
    kinds: list[str] = []
    if any(
        pattern.search(sentence)
        for pattern in (
            _MARKDOWN_LINK,
            _NUMERIC_CITATION,
            _AUTHOR_YEAR,
            _NARRATIVE_AUTHOR_YEAR,
            _PANDOC_CITATION,
            _INLINE_REF,
        )
    ):
        kinds.append("citation_bearing_sentence")
    if any(
        pattern.search(sentence)
        for pattern in (_QUANTITATIVE, _SAMPLE_SIZE, _EFFECT_SIZE)
    ):
        kinds.append("quantitative_sentence")
    return kinds


def _candidate_triggers(sentence: str) -> list[dict[str, Any]]:
    """Return finite lexical witnesses, not semantic subclaim boundaries."""

    patterns = (
        (
            "citation_bearing_sentence",
            (
                _MARKDOWN_LINK,
                _NUMERIC_CITATION,
                _AUTHOR_YEAR,
                _NARRATIVE_AUTHOR_YEAR,
                _PANDOC_CITATION,
                _INLINE_REF,
            ),
        ),
        (
            "quantitative_sentence",
            (_QUANTITATIVE, _SAMPLE_SIZE, _EFFECT_SIZE),
        ),
    )
    found: dict[tuple[str, int, int], dict[str, Any]] = {}
    for kind, kind_patterns in patterns:
        for pattern in kind_patterns:
            for match in pattern.finditer(sentence):
                key = (kind, match.start(), match.end())
                found[key] = {
                    "kind": kind,
                    "start_char": match.start(),
                    "end_char": match.end(),
                    "text": match.group(0),
                }
    return [
        found[key] for key in sorted(found, key=lambda row: (row[1], row[2], row[0]))
    ]


def _char_to_byte_offsets(text: str) -> list[int]:
    offsets = [0]
    total = 0
    for character in text:
        total += len(character.encode("utf-8"))
        offsets.append(total)
    return offsets


def _trimmed_segment(
    body: str, start: int, end: int
) -> tuple[int, int, str] | None:
    segment = body[start:end]
    left = len(segment) - len(segment.lstrip())
    right = len(segment.rstrip())
    if right <= left:
        return None
    return start + left, start + right, segment[left:right]


def _sentences(draft: str) -> list[dict[str, Any]]:
    """Return prose sentences with exact character positions in the draft."""

    output: list[dict[str, Any]] = []
    in_fence = False
    absolute = 0
    for line_number, raw_line in enumerate(draft.splitlines(keepends=True), start=1):
        content = raw_line.rstrip("\r\n")
        stripped = content.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            absolute += len(raw_line)
            continue
        if in_fence or not stripped or stripped.startswith("#"):
            absolute += len(raw_line)
            continue

        body_start = len(content) - len(content.lstrip())
        body_end = len(content.rstrip())
        body = content[body_start:body_end]
        boundaries = list(_SENTENCE_BREAK.finditer(body))
        segment_start = 0
        sentence_index = 0
        for boundary in boundaries + [None]:
            segment_end = boundary.start() if boundary is not None else len(body)
            trimmed = _trimmed_segment(body, segment_start, segment_end)
            if trimmed is not None:
                local_start, local_end, sentence = trimmed
                sentence_index += 1
                output.append(
                    {
                        "line": line_number,
                        "sentence_index": sentence_index,
                        "text": sentence,
                        "start_char": absolute + body_start + local_start,
                        "end_char": absolute + body_start + local_end,
                    }
                )
            if boundary is None:
                break
            segment_start = boundary.end()
        absolute += len(raw_line)
    return output


def _validated_claims(
    draft_raw: bytes, registry: Mapping[str, Any]
) -> list[dict[str, Any]]:
    expected_hash = _sha256(draft_raw)
    if registry["draft_raw_sha256"] != expected_hash:
        raise CoverageError(
            "registry draft_raw_sha256 does not match the exact draft bytes"
        )

    claims: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_spans: set[tuple[int, int]] = set()
    for claim in registry["claims"]:
        claim_id = claim["claim_id"]
        if claim_id in seen_ids:
            raise CoverageError(f"duplicate claim_id: {claim_id}")
        seen_ids.add(claim_id)
        start = claim["draft_span"]["start_byte"]
        end = claim["draft_span"]["end_byte"]
        if start >= end:
            raise CoverageError(f"claim {claim_id} draft span is empty or reversed")
        if (start, end) in seen_spans:
            raise CoverageError(
                f"claim {claim_id} duplicates another claim's exact draft span"
            )
        seen_spans.add((start, end))
        if end > len(draft_raw):
            raise CoverageError(f"claim {claim_id} draft span exceeds draft bytes")
        fragment = _decode_utf8(draft_raw[start:end], f"claim {claim_id} draft span")
        if fragment != claim["claim_text"]:
            raise CoverageError(
                f"claim {claim_id} claim_text does not equal its exact draft span"
            )
        claims.append(dict(claim))
    return claims


def build_report(draft_raw: bytes, registry_raw: bytes) -> dict[str, Any]:
    """Build a report bound to exact raw draft and registry bytes."""

    draft = _decode_utf8(draft_raw, "draft")
    registry = _load_registry(registry_raw)
    claims = _validated_claims(draft_raw, registry)
    char_to_byte = _char_to_byte_offsets(draft)

    matched_claim_ids: set[str] = set()
    candidates: list[dict[str, Any]] = []
    for sentence in _sentences(draft):
        triggers = _candidate_triggers(sentence["text"])
        kinds = _candidate_kinds(sentence["text"])
        if not kinds:
            continue
        start_byte = char_to_byte[sentence["start_char"]]
        end_byte = char_to_byte[sentence["end_char"]]
        matches = sorted(
            claim["claim_id"]
            for claim in claims
            if claim["draft_span"]["start_byte"] >= start_byte
            and claim["draft_span"]["end_byte"] <= end_byte
        )
        matched_claim_ids.update(matches)
        sentence_raw = draft_raw[start_byte:end_byte]
        trigger_rows: list[dict[str, Any]] = []
        for trigger in triggers:
            trigger_start_char = sentence["start_char"] + trigger["start_char"]
            trigger_end_char = sentence["start_char"] + trigger["end_char"]
            trigger_start_byte = char_to_byte[trigger_start_char]
            trigger_end_byte = char_to_byte[trigger_end_char]
            trigger_matches = sorted(
                claim["claim_id"]
                for claim in claims
                if claim["draft_span"]["start_byte"] <= trigger_start_byte
                and claim["draft_span"]["end_byte"] >= trigger_end_byte
                and claim["draft_span"]["start_byte"] >= start_byte
                and claim["draft_span"]["end_byte"] <= end_byte
            )
            trigger_raw = draft_raw[trigger_start_byte:trigger_end_byte]
            trigger_digest = _sha256(
                trigger["kind"].encode("utf-8") + bytes([0]) + trigger_raw
            )[:12]
            trigger_rows.append(
                {
                    "trigger_id": (
                        f"TRIG-B{trigger_start_byte}-{trigger_end_byte}-"
                        f"{trigger_digest}"
                    ),
                    "kind": trigger["kind"],
                    "start_byte": trigger_start_byte,
                    "end_byte": trigger_end_byte,
                    "text": trigger["text"],
                    "coverage_state": (
                        "registry_span_matched"
                        if trigger_matches
                        else "trigger_unregistered"
                    ),
                    "matched_claim_ids": trigger_matches,
                }
            )
        uncovered_trigger_count = sum(
            row["coverage_state"] == "trigger_unregistered" for row in trigger_rows
        )
        full_sentence_match = any(
            claim["draft_span"]["start_byte"] == start_byte
            and claim["draft_span"]["end_byte"] == end_byte
            for claim in claims
        )
        if not matches:
            coverage_state = "candidate_unregistered"
        elif uncovered_trigger_count or not full_sentence_match:
            coverage_state = "mixed_or_partial_registry_coverage"
        else:
            coverage_state = "registry_span_matched"
        candidates.append(
            {
                "candidate_id": (
                    f"CAND-B{start_byte}-{end_byte}-{_sha256(sentence_raw)[:12]}"
                ),
                "line": sentence["line"],
                "sentence_index": sentence["sentence_index"],
                "start_byte": start_byte,
                "end_byte": end_byte,
                "text": sentence["text"],
                "candidate_kinds": kinds,
                "coverage_state": coverage_state,
                "matched_claim_ids": matches,
                "uncovered_trigger_count": uncovered_trigger_count,
                "triggers": trigger_rows,
            }
        )

    report = {
        "schema_version": REPORT_VERSION,
        "draft_raw_sha256": _sha256(draft_raw),
        "registry_raw_sha256": _sha256(registry_raw),
        "registry_schema_version": registry["schema_version"],
        "mechanical_candidate_scope": [
            "citation_bearing_sentence",
            "quantitative_sentence",
        ],
        "semantic_extraction_coverage": "not_machine_detectable",
        "registry_claim_count": len(claims),
        "candidate_unregistered_count": sum(
            row["coverage_state"] != "registry_span_matched" for row in candidates
        ),
        "candidates": candidates,
        "registered_claims_outside_candidate_classes": sorted(
            {claim["claim_id"] for claim in claims} - matched_claim_ids
        ),
    }
    errors = _schema_errors(report, REPORT_SCHEMA_PATH)
    if errors:
        raise CoverageError("builder emitted invalid report: " + "; ".join(errors))
    return report


def _reject_duplicate_json_keys(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CoverageError(f"duplicate report JSON key: {key!r}")
        result[key] = value
    return result


def _load_report(raw: bytes) -> dict[str, Any]:
    text = _decode_utf8(raw, "report")
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicate_json_keys)
    except json.JSONDecodeError as exc:
        raise CoverageError(f"cannot parse report JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise CoverageError("report root must be an object")
    return value


def validate_report(
    report: Mapping[str, Any], draft_raw: bytes, registry_raw: bytes
) -> list[str]:
    """Validate shape and replay the complete report from exact inputs."""

    errors = _schema_errors(report, REPORT_SCHEMA_PATH)
    if errors:
        return errors
    try:
        expected = build_report(draft_raw, registry_raw)
    except CoverageError as exc:
        return [f"inputs cannot be replayed: {exc}"]
    if dict(report) != expected:
        return ["$: report does not equal deterministic replay from exact inputs"]
    return []


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--validate-report",
        type=Path,
        help="replay-validate an existing report instead of building one",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        draft_raw = args.draft.read_bytes()
        registry_raw = args.registry.read_bytes()
        if args.validate_report is not None:
            if args.output is not None:
                raise CoverageError("--output cannot be used with --validate-report")
            report = _load_report(args.validate_report.read_bytes())
            errors = validate_report(report, draft_raw, registry_raw)
            if errors:
                for error in errors:
                    print(error, file=sys.stderr)
                return 1
            print("claim-registry coverage replay: PASS")
            return 0

        report = build_report(draft_raw, registry_raw)
        rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.output is None:
            sys.stdout.write(rendered)
        else:
            args.output.write_text(rendered, encoding="utf-8")
        return 0
    except (OSError, CoverageError) as exc:
        print(f"[CLAIM-REGISTRY-COVERAGE ERROR: {exc}]", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
