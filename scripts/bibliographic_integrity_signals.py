#!/usr/bin/env python3
"""Canonical #678 bibliographic-integrity signal helpers and migration CLI.

The migration is deliberately additive. It writes
``bibliographic_integrity_signals`` while preserving every legacy field that
currently drives marker projection or terminal policy.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import html
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = (
    REPO_ROOT
    / "shared/contracts/passport/bibliographic_integrity_signal.schema.json"
)
SCHEMA_VERSION = "bibliographic-integrity-signal/1.0"

_RESOLVERS = {
    "semantic_scholar_unmatched": "Semantic Scholar",
    "openalex_unmatched": "OpenAlex",
    "crossref_unmatched": "Crossref",
    "arxiv_unmatched": "arXiv",
}

_SUMMARY_LABELS = {
    "preprint_post_llm_inflection": "Post-LLM-inflection preprint heuristic",
    "semantic_scholar_unmatched": "Semantic Scholar unmatched observation",
    "openalex_unmatched": "OpenAlex unmatched observation",
    "crossref_unmatched": "Crossref unmatched observation",
    "arxiv_unmatched": "arXiv unmatched observation",
    "retraction_status": "Retraction-list status",
    "tortured_phrase_match": "Tortured-phrase heuristic match",
}

_TORTURED_PHRASE_CONTEXTS = (
    "author_prose",
    "quote",
    "cited_title",
    "reference_entry",
    "code_or_verbatim",
    "unknown",
    "cited_abstract",
)
_TORTURED_PHRASE_RFC3339_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt]"
    r"(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
    r"(?:\.[0-9]{1,6})?(?:[Zz]|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])$"
)


def _empty_tortured_phrase_counts() -> dict[str, Any]:
    return {
        "rules_evaluated": 0,
        "matched_rule_count": 0,
        "rule_match_count": 0,
        "unique_instance_count": 0,
        "segments_total": 0,
        "unknown_segments": 0,
        "matches_by_context": {
            context: 0 for context in _TORTURED_PHRASE_CONTEXTS
        },
    }


def _signal_id(citation_key: str, signal_type: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_:-]+", citation_key):
        key_part = citation_key
    else:
        digest = hashlib.sha256(citation_key.encode("utf-8")).hexdigest()[:16]
        key_part = f"source-{digest}"
    return f"bis:{key_part}:{signal_type}"


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validation_errors(signal: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(
        load_schema(), format_checker=Draft202012Validator.FORMAT_CHECKER
    )
    return sorted(error.message for error in validator.iter_errors(signal))


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _validate_tortured_phrase_projection(signal: dict[str, Any]) -> None:
    """Validate v1.2 invariants that do not require the source corpus entry."""

    if signal.get("schema_version") != "bibliographic-integrity-signal/1.2":
        return
    context = signal["tortured_phrase_context"]
    surface = context["surface"]
    binding = context["surface_binding"]
    snapshot = context["snapshot"]
    content_utf8_bytes = binding["content_utf8_bytes"]
    if binding["content_sha256"] is not None and (
        isinstance(content_utf8_bytes, bool)
        or not isinstance(content_utf8_bytes, int)
        or content_utf8_bytes < 1
    ):
        raise ValueError(
            "present tortured-phrase surface requires positive content_utf8_bytes"
        )
    citation_key = signal["subject"]["citation_key"]
    payload = {
        "citation_key": citation_key,
        "surface": surface,
        "snapshot_sha256": snapshot["snapshot_sha256"],
        "content_sha256": binding["content_sha256"],
    }
    suffix = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()[:20]
    surface_slug = "title" if surface == "cited_title" else "abstract"
    expected_signal_id = f"bis:{citation_key}:tpm_{surface_slug}_{suffix}"
    if signal["signal_id"] != expected_signal_id:
        raise ValueError("tortured-phrase signal_id binding mismatch")

    matches = context["matches"]
    counts = context["counts"]
    if counts["rule_match_count"] != len(matches):
        raise ValueError("tortured-phrase rule_match_count mismatch")
    if counts["matched_rule_count"] != len({item["pattern_id"] for item in matches}):
        raise ValueError("tortured-phrase matched_rule_count mismatch")
    intervals: dict[str, list[tuple[int, int]]] = {}
    seen_match_ids: set[str] = set()
    artifact_sha = binding["content_sha256"] or hashlib.sha256(b"").hexdigest()
    expected_context = surface
    expected_disposition = (
        "preserve_verbatim_review_context"
        if surface == "cited_title"
        else "review_cited_source_no_automatic_rewrite"
    )
    for index, match in enumerate(matches):
        if match["segment_id"] != "SEG-000001":
            raise ValueError(
                f"tortured-phrase matches[{index}] segment_id mismatch"
            )
        if match["context"] != expected_context:
            raise ValueError(f"tortured-phrase matches[{index}] context mismatch")
        if match["disposition"] != expected_disposition:
            raise ValueError(
                f"tortured-phrase matches[{index}] disposition mismatch"
            )
        if hashlib.sha256(match["matched_text"].encode("utf-8")).hexdigest() != match[
            "matched_text_sha256"
        ]:
            raise ValueError(f"tortured-phrase matches[{index}] text hash mismatch")
        span = match["source_span"]
        codepoint_start = span["codepoint_start"]
        codepoint_end = span["codepoint_end"]
        utf8_start = span["utf8_start"]
        utf8_end = span["utf8_end"]
        matched_text = match["matched_text"]
        if not codepoint_start < codepoint_end or not utf8_start < utf8_end:
            raise ValueError(f"tortured-phrase matches[{index}] has an empty/reversed span")
        if codepoint_end - codepoint_start != len(matched_text):
            raise ValueError(
                f"tortured-phrase matches[{index}] codepoint span length mismatch"
            )
        if utf8_end - utf8_start != len(matched_text.encode("utf-8")):
            raise ValueError(
                f"tortured-phrase matches[{index}] UTF-8 span length mismatch"
            )
        if not (
            codepoint_start <= utf8_start <= 4 * codepoint_start
            and codepoint_end <= utf8_end <= 4 * codepoint_end
        ):
            raise ValueError(
                f"tortured-phrase matches[{index}] has an impossible UTF-8 prefix offset"
            )
        if (
            not isinstance(content_utf8_bytes, int)
            or codepoint_end > content_utf8_bytes
            or utf8_end > content_utf8_bytes
        ):
            raise ValueError(
                f"tortured-phrase matches[{index}] exceeds the bound surface bytes"
            )
        if len(matched_text) > 1000 or len(matched_text.split()) > 25:
            raise ValueError(f"tortured-phrase matches[{index}] exceeds evidence bounds")
        match_payload = {
            "artifact_sha256": artifact_sha,
            "snapshot_sha256": snapshot["snapshot_sha256"],
            "surface": surface,
            "segment_id": match["segment_id"],
            "context": match["context"],
            "rule_id": match["pattern_id"],
            "codepoint_start": span["codepoint_start"],
            "codepoint_end": span["codepoint_end"],
        }
        expected_match_id = "tpm-" + hashlib.sha256(
            _canonical_json(match_payload).encode("utf-8")
        ).hexdigest()[:24]
        if match["match_id"] != expected_match_id:
            raise ValueError(f"tortured-phrase matches[{index}] match_id mismatch")
        if match["match_id"] in seen_match_ids:
            raise ValueError(f"tortured-phrase matches[{index}] duplicates match_id")
        seen_match_ids.add(match["match_id"])
        intervals.setdefault(match["segment_id"], []).append(
            (span["codepoint_start"], span["codepoint_end"])
        )
    unique_instances = 0
    for values in intervals.values():
        current_end: int | None = None
        for start, end in sorted(set(values)):
            if current_end is None or start >= current_end:
                unique_instances += 1
                current_end = end
            else:
                current_end = max(current_end, end)
    if counts["unique_instance_count"] != unique_instances:
        raise ValueError("tortured-phrase unique_instance_count mismatch")
    if counts["matched_rule_count"] > counts["rules_evaluated"]:
        raise ValueError("tortured-phrase matched_rule_count exceeds rules_evaluated")
    matches_by_context = counts["matches_by_context"]
    if any(
        matches_by_context[name]
        != (len(matches) if name == expected_context else 0)
        for name in _TORTURED_PHRASE_CONTEXTS
    ):
        raise ValueError("tortured-phrase matches_by_context mismatch")

    status = signal["check_status"]
    reason_code = context["reason_code"]
    if binding["content_sha256"] is None:
        if (
            surface != "cited_abstract"
            or reason_code not in {"ABSTRACT_MISSING", "ABSTRACT_EMPTY"}
            or status != "not_checked"
            or signal["finding"] != "unresolved"
            or matches
            or counts != _empty_tortured_phrase_counts()
        ):
            raise ValueError(
                "unbound cited surface must be an explicit missing/empty abstract"
            )
    elif status == "checked":
        if (
            reason_code != "CHECK_COMPLETED"
            or snapshot["status"] != "loaded"
            or snapshot["reason_code"] != "CHECK_COMPLETED"
            or counts["rules_evaluated"] != snapshot["rule_count"]
            or counts["segments_total"] != 1
            or counts["unknown_segments"] != 0
        ):
            raise ValueError(
                "checked cited surface lacks complete loaded-snapshot coverage"
            )
    else:
        if matches or counts != _empty_tortured_phrase_counts():
            raise ValueError(
                "not-checked/degraded cited surface must discard partial match state"
            )
        if reason_code == "MATCH_RESOURCE_LIMIT":
            if (
                status != "degraded"
                or signal["finding"] != "unresolved"
                or snapshot["status"] != "loaded"
                or snapshot["reason_code"] != "CHECK_COMPLETED"
            ):
                raise ValueError(
                    "match resource failure requires a loaded snapshot and degraded output"
                )
        elif (
            reason_code != snapshot["reason_code"]
            or status != snapshot["status"]
            or signal["finding"] != "unresolved"
        ):
            raise ValueError(
                "cited surface status/reason does not replay snapshot availability"
            )

    evidence = signal["evidence"]
    if len(evidence) != 1:
        raise ValueError("tortured-phrase signal requires exactly one evidence row")
    expected_type = (
        "phrase_match"
        if signal["check_status"] == "checked" and signal["finding"] == "detected"
        else "list_record"
        if signal["check_status"] == "checked"
        else "degradation_record"
    )
    expected_value: Any = (
        counts["rule_match_count"]
        if signal["check_status"] == "checked"
        else context["reason_code"]
    )
    evidence_row = evidence[0]
    if evidence_row["evidence_type"] != expected_type:
        raise ValueError("tortured-phrase evidence_type mismatch")
    if evidence_row.get("record_locator") != (
        "title" if surface == "cited_title" else "abstract"
    ):
        raise ValueError("tortured-phrase evidence locator mismatch")
    if signal["check_status"] == "checked" and (
        isinstance(evidence_row["observed_value"], bool)
        or not isinstance(evidence_row["observed_value"], int)
    ):
        raise ValueError("checked tortured-phrase evidence count must be an integer")
    if evidence_row["observed_value"] != expected_value:
        raise ValueError("tortured-phrase evidence observed_value mismatch")
    if evidence_row.get("evidence_sha256") != binding["content_sha256"]:
        raise ValueError("tortured-phrase evidence hash mismatch")
    provenance = signal["provenance"]
    if provenance["source_sha256"] != snapshot["snapshot_sha256"]:
        raise ValueError("tortured-phrase provenance snapshot hash mismatch")
    snapshot_source = snapshot["source"]
    expected_source_name = (
        snapshot_source["name"]
        if isinstance(snapshot_source, dict)
        else "tortured-phrase snapshot unavailable"
    )
    expected_source_version = (
        snapshot_source["version"] if isinstance(snapshot_source, dict) else None
    )
    if provenance["source_name"] != expected_source_name:
        raise ValueError("tortured-phrase provenance source_name mismatch")
    if provenance["source_version"] != expected_source_version:
        raise ValueError("tortured-phrase provenance source_version mismatch")
    if evidence_row["source_name"] != expected_source_name:
        raise ValueError("tortured-phrase evidence source_name mismatch")
    checked_at = provenance["checked_at"]
    recorded_at = provenance["recorded_at"]
    if signal["check_status"] == "not_checked":
        if checked_at is not None:
            raise ValueError("not-checked tortured-phrase row must have null checked_at")
    else:
        if not isinstance(checked_at, str) or not isinstance(recorded_at, str):
            raise ValueError("checked/degraded tortured-phrase row requires checked_at")
        if (
            _TORTURED_PHRASE_RFC3339_RE.fullmatch(checked_at) is None
            or _TORTURED_PHRASE_RFC3339_RE.fullmatch(recorded_at) is None
        ):
            raise ValueError(
                "tortured-phrase timestamps require RFC 3339 with at most 6 fraction digits"
            )
        checked_value = (
            checked_at[:-1] + "+00:00"
            if checked_at[-1] in {"Z", "z"}
            else checked_at
        )
        recorded_value = (
            recorded_at[:-1] + "+00:00"
            if recorded_at[-1] in {"Z", "z"}
            else recorded_at
        )
        checked = dt.datetime.fromisoformat(checked_value)
        recorded = dt.datetime.fromisoformat(recorded_value)
        if recorded < checked:
            raise ValueError("tortured-phrase recorded_at precedes checked_at")


def _signal(
    *,
    citation_key: str,
    source_pointer: str | None,
    signal_type: str,
    epistemic_class: str,
    epistemic_label: str,
    check_status: str,
    finding: str,
    evidence: list[dict[str, Any]],
    source_name: str,
    source_version: str | None,
    source_sha256: str | None,
    checked_at: str | None,
    recorded_at: str,
    stale_after: str | None = None,
    freshness: str = "unknown",
    affected_claims: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "signal_id": _signal_id(citation_key, signal_type),
        "signal_type": signal_type,
        "epistemic_class": epistemic_class,
        "epistemic_label": epistemic_label,
        "check_status": check_status,
        "finding": finding,
        "evidence": evidence,
        "provenance": {
            "source_name": source_name,
            "source_version": source_version,
            "source_sha256": source_sha256,
            "checked_at": checked_at,
            "recorded_at": recorded_at,
            "stale_after": stale_after,
            "freshness": freshness,
        },
        "subject": {
            "citation_key": citation_key,
            "source_pointer": source_pointer,
            "affected_claims": affected_claims or [],
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
            "summary_label": _SUMMARY_LABELS[signal_type],
            "marker_token": None,
        },
    }


def migrate_legacy_entry(
    entry: dict[str, Any], *, recorded_at: str
) -> list[dict[str, Any]]:
    """Project declared legacy fields into canonical v1 records.

    No missing value is synthesized as ``not_detected``. Existing canonical
    records win by ``signal_id`` so the operation is idempotent.
    """
    citation_key = entry.get("citation_key") or entry.get("id")
    if not isinstance(citation_key, str) or not citation_key:
        raise ValueError("legacy entry requires citation_key or id")
    source_pointer = entry.get("source_pointer")
    if not isinstance(source_pointer, str):
        source_pointer = None
    checked_at = entry.get("contamination_signals_backfilled_at") or entry.get(
        "obtained_at"
    )
    if not isinstance(checked_at, str):
        checked_at = None

    projected: list[dict[str, Any]] = []
    legacy = entry.get("contamination_signals")
    if isinstance(legacy, dict):
        for signal_type in (
            "preprint_post_llm_inflection",
            "semantic_scholar_unmatched",
            "openalex_unmatched",
            "crossref_unmatched",
            "arxiv_unmatched",
        ):
            observed = legacy.get(signal_type)
            if not isinstance(observed, bool):
                continue
            heuristic = signal_type == "preprint_post_llm_inflection"
            source_name = (
                "publication-year and preprint-venue rule"
                if heuristic
                else _RESOLVERS[signal_type]
            )
            projected.append(
                _signal(
                    citation_key=citation_key,
                    source_pointer=source_pointer,
                    signal_type=signal_type,
                    epistemic_class=(
                        "heuristic_advisory" if heuristic else "deterministic_fact"
                    ),
                    epistemic_label=(
                        "HEURISTIC-INDICATOR"
                        if heuristic
                        else "RESOLVER-OR-LIST-OBSERVATION"
                    ),
                    check_status="checked",
                    finding="detected" if observed else "not_detected",
                    evidence=[
                        {
                            "evidence_type": (
                                "metadata_rule" if heuristic else "resolver_response"
                            ),
                            "source_name": source_name,
                            "record_locator": source_pointer,
                            "observed_value": observed,
                            "evidence_sha256": None,
                        }
                    ],
                    source_name=source_name,
                    source_version="legacy-carrier",
                    source_sha256=None,
                    checked_at=checked_at,
                    recorded_at=recorded_at,
                )
            )

    omissions = entry.get("contamination_signal_omissions")
    if isinstance(omissions, dict):
        for signal_type, reason in omissions.items():
            if signal_type not in _RESOLVERS or reason != "api_degraded":
                continue
            projected.append(
                _signal(
                    citation_key=citation_key,
                    source_pointer=source_pointer,
                    signal_type=signal_type,
                    epistemic_class="deterministic_fact",
                    epistemic_label="RESOLVER-OR-LIST-OBSERVATION",
                    check_status="degraded",
                    finding="unresolved",
                    evidence=[
                        {
                            "evidence_type": "degradation_record",
                            "source_name": _RESOLVERS[signal_type],
                            "record_locator": source_pointer,
                            "observed_value": reason,
                            "evidence_sha256": None,
                        }
                    ],
                    source_name=_RESOLVERS[signal_type],
                    source_version="legacy-carrier",
                    source_sha256=None,
                    checked_at=None,
                    recorded_at=recorded_at,
                )
            )

    if isinstance(entry.get("retraction_check"), bool):
        ran = entry["retraction_check"]
        projected.append(
            _signal(
                citation_key=citation_key,
                source_pointer=source_pointer,
                signal_type="retraction_status",
                epistemic_class="process_attestation",
                epistemic_label="CHECK-EXECUTION-ATTESTATION",
                check_status="checked" if ran else "not_checked",
                finding="unresolved",
                evidence=[
                    {
                        "evidence_type": "legacy_attestation",
                        "source_name": "Retraction Watch",
                        "record_locator": None,
                        "observed_value": ran,
                        "evidence_sha256": None,
                    }
                ],
                source_name="Retraction Watch",
                source_version=None,
                source_sha256=None,
                checked_at=checked_at if ran else None,
                recorded_at=recorded_at,
            )
        )

    existing = entry.get("bibliographic_integrity_signals")
    by_id: dict[str, dict[str, Any]] = {}
    if existing is not None and not isinstance(existing, list):
        raise ValueError("bibliographic_integrity_signals must be an array")
    if isinstance(existing, list):
        for index, signal in enumerate(existing):
            if not isinstance(signal, dict):
                raise ValueError(
                    "bibliographic_integrity_signals"
                    f"[{index}] must be an object"
                )
            signal_id = signal.get("signal_id")
            if not isinstance(signal_id, str) or not signal_id.strip():
                raise ValueError(
                    "bibliographic_integrity_signals"
                    f"[{index}] is missing a non-empty signal_id"
                )
            if signal_id in by_id:
                raise ValueError(
                    "duplicate bibliographic-integrity signal_id "
                    f"{signal_id!r}; refusing a lossy migration"
                )
            by_id[signal_id] = copy.deepcopy(signal)
    for signal in projected:
        by_id.setdefault(signal["signal_id"], signal)
    return [by_id[key] for key in sorted(by_id)]


def render_advisory_section(signals: list[dict[str, Any]]) -> str:
    """Compose one complete, injection-safe canonical provenance summary."""
    if not signals:
        return ""

    def cell(value: Any) -> str:
        if value is None or value == "":
            return "—"
        rendered = str(value).replace("\r", " ").replace("\n", " ")
        rendered = "".join(
            char
            if unicodedata.category(char) not in {"Cc", "Cf", "Zl", "Zp"}
            else f"U+{ord(char):04X}"
            for char in rendered
        )
        if len(rendered) > 1000:
            rendered = rendered[:999] + "…"
        rendered = html.escape(rendered, quote=False)
        for char in ("\\", "|", "`", "[", "]", "!", "*"):
            rendered = rendered.replace(char, "\\" + char)
        return rendered

    ordered = sorted(signals, key=lambda item: item["signal_id"])
    for signal in ordered:
        problems = validation_errors(signal)
        if problems:
            raise ValueError(
                f"invalid bibliographic-integrity signal {signal.get('signal_id')!r}: "
                + "; ".join(problems)
            )
        _validate_tortured_phrase_projection(signal)

    lines = [
        "## Bibliographic Integrity Advisories",
        "",
        "| signal_id | signal type | citation | label | summary label | layer | evaluation status | status | finding | reason code | surface | rule matches | unique instances | evidence | source | source version | snapshot as of | source sha256 | manifest sha256 | checked at | recorded at | stale after | freshness | source pointer | claims | context |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for signal in ordered:
        status = signal["check_status"]
        finding = signal["finding"]
        if finding == "unresolved" or status in {"not_checked", "unknown", "degraded"}:
            finding = "NOT CLEAN — UNRESOLVED"
        claims = ", ".join(signal["subject"]["affected_claims"]) or "—"
        provenance = signal["provenance"]
        context = "—"
        summary_label = "—"
        layer = "—"
        evaluation_status = "—"
        reason_code = "—"
        surface = "—"
        rule_matches: Any = "—"
        unique_instances: Any = "—"
        evidence_projection = "—"
        snapshot_as_of = "—"
        manifest_sha256 = "—"
        retraction = signal.get("retraction_context")
        if isinstance(retraction, dict):
            reasons = ", ".join(retraction.get("retraction_reasons", [])) or "not served"
            legitimate = retraction.get("declared_legitimate_citation", {}).get(
                "deterministic_exception", False
            )
            context = (
                f"effective={retraction.get('effective_status', 'unknown')}; "
                f"agreement={retraction.get('resolver_agreement', 'unknown')}; "
                f"event={retraction.get('retraction_event_date') or 'not decidable'}; "
                f"reasons={reasons}; load_bearing={retraction.get('load_bearing', 'not_decidable')}; "
                f"timing={retraction.get('timing_vs_acquisition', 'not_decidable')}; "
                f"legitimate_exception={str(bool(legitimate)).lower()}"
            )
        phrase = signal.get("tortured_phrase_context")
        if isinstance(phrase, dict):
            summary_label = signal["display"]["summary_label"]
            layer = phrase["layer"]
            evaluation_status = phrase["evaluation_status"]
            reason_code = phrase["reason_code"]
            surface = phrase.get("surface", "—")
            snapshot = phrase["snapshot"]
            snapshot_source = snapshot["source"]
            if isinstance(snapshot_source, dict):
                snapshot_as_of = snapshot_source["as_of"]
            manifest_sha256 = snapshot["manifest_sha256"] or "—"
            counts = phrase.get("counts", {})
            rule_matches = counts.get("rule_match_count", "—")
            unique_instances = counts.get("unique_instance_count", "—")
            projected: list[str] = []
            for match in phrase.get("matches", [])[:3]:
                span = match.get("source_span", {})
                projected.append(
                    "{pattern}@{start}:{end}={text} [{disposition}]".format(
                        pattern=match.get("pattern_id", "?"),
                        start=span.get("utf8_start", "?"),
                        end=span.get("utf8_end", "?"),
                        text=match.get("matched_text", "?"),
                        disposition=match.get("disposition", "?"),
                    )
                )
            omitted = len(phrase.get("matches", [])) - len(projected)
            if omitted > 0:
                projected.append(f"+{omitted} more machine rows")
            evidence_projection = "; ".join(projected) or phrase.get(
                "reason_code", "—"
            )
            if finding == "detected":
                outcome = "phrase-list match requiring review"
            elif finding == "not_detected":
                outcome = (
                    "no phrase-list match observed on the checked surface; "
                    "absence is not a clean certificate"
                )
            else:
                outcome = "phrase-list screening unresolved; no clean conclusion"
            context = (
                f"{outcome}; list-match only; origin not inferred; contextual judgment "
                "not performed; no automatic rewrite"
            )
        lines.append(
            "| {signal_id} | {signal_type} | {citation} | {label} | {summary_label} | "
            "{layer} | {evaluation_status} | {status} | {finding} | {reason_code} | "
            "{surface} | {rule_matches} | {unique_instances} | {evidence} | "
            "{source} | {source_version} | {snapshot_as_of} | {source_sha256} | "
            "{manifest_sha256} | {checked_at} | "
            "{recorded_at} | {stale_after} | {freshness} | {source_pointer} | "
            "{claims} | {context} |".format(
                signal_id=cell(signal["signal_id"]),
                signal_type=cell(signal["signal_type"]),
                citation=cell(signal["subject"]["citation_key"]),
                label=cell(signal["epistemic_label"]),
                summary_label=cell(summary_label),
                layer=cell(layer),
                evaluation_status=cell(evaluation_status),
                status=cell(status),
                finding=cell(finding),
                reason_code=cell(reason_code),
                surface=cell(surface),
                rule_matches=cell(rule_matches),
                unique_instances=cell(unique_instances),
                evidence=cell(evidence_projection),
                source=cell(provenance["source_name"]),
                source_version=cell(provenance["source_version"]),
                snapshot_as_of=cell(snapshot_as_of),
                source_sha256=cell(provenance["source_sha256"]),
                manifest_sha256=cell(manifest_sha256),
                checked_at=cell(provenance["checked_at"]),
                recorded_at=cell(provenance["recorded_at"]),
                stale_after=cell(provenance["stale_after"]),
                freshness=cell(provenance["freshness"]),
                source_pointer=cell(signal["subject"]["source_pointer"]),
                claims=cell(claims),
                context=cell(context),
            )
        )
    return "\n".join(lines) + "\n"


def _load_document(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        if path.suffix.lower() == ".json":
            data = json.load(handle)
        else:
            data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON/YAML mapping")
    return data


def _dump_document(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        if path.suffix.lower() == ".json":
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        else:
            yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add canonical bibliographic-integrity records without deleting legacy fields."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--recorded-at", required=True, help="ISO-8601 migration timestamp")
    args = parser.parse_args()

    try:
        document = _load_document(args.input)
        corpus = document.get("literature_corpus")
        if not isinstance(corpus, list):
            raise ValueError("input must contain literature_corpus[]")
        for entry in corpus:
            if not isinstance(entry, dict):
                raise ValueError("every literature_corpus item must be a mapping")
            signals = migrate_legacy_entry(entry, recorded_at=args.recorded_at)
            if signals:
                entry["bibliographic_integrity_signals"] = signals
                for signal in signals:
                    problems = validation_errors(signal)
                    if problems:
                        raise ValueError("; ".join(problems))
        _dump_document(args.output, document)
    except (OSError, ValueError, yaml.YAMLError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
