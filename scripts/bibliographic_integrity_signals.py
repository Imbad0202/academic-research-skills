#!/usr/bin/env python3
"""Canonical #678 bibliographic-integrity signal helpers and migration CLI.

The migration is deliberately additive. It writes
``bibliographic_integrity_signals`` while preserving every legacy field that
currently drives marker projection or terminal policy.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
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
    """Compose any number of signals in one provenance-summary section."""
    if not signals:
        return ""

    def cell(value: Any) -> str:
        if value is None or value == "":
            return "—"
        return str(value).replace("|", "\\|").replace("\n", " ")

    lines = [
        "## Bibliographic Integrity Advisories",
        "",
        "| signal_id | signal type | citation | label | status | finding | source | source version | source sha256 | checked at | recorded at | stale after | freshness | source pointer | claims | context |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for signal in sorted(signals, key=lambda item: item["signal_id"]):
        status = signal["check_status"]
        finding = signal["finding"]
        if finding == "unresolved" or status in {"not_checked", "unknown", "degraded"}:
            finding = "NOT CLEAN — UNRESOLVED"
        claims = ", ".join(signal["subject"]["affected_claims"]) or "—"
        provenance = signal["provenance"]
        context = "—"
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
        lines.append(
            "| {signal_id} | {signal_type} | {citation} | {label} | {status} | {finding} | "
            "{source} | {source_version} | {source_sha256} | {checked_at} | "
            "{recorded_at} | {stale_after} | {freshness} | {source_pointer} | "
            "{claims} | {context} |".format(
                signal_id=cell(signal["signal_id"]),
                signal_type=cell(signal["signal_type"]),
                citation=cell(signal["subject"]["citation_key"]),
                label=cell(signal["epistemic_label"]),
                status=cell(status),
                finding=cell(finding),
                source=cell(provenance["source_name"]),
                source_version=cell(provenance["source_version"]),
                source_sha256=cell(provenance["source_sha256"]),
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
