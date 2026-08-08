#!/usr/bin/env python3
"""Deterministic #651 retraction-status resolver and policy helper.

The module consumes already-returned OpenAlex/Crossref metadata.  It performs
no network I/O and never judges whether citing a retracted work is legitimate.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from bibliographic_integrity_signals import _signal_id, validation_errors
except ImportError:  # pragma: no cover - namespace import
    from scripts.bibliographic_integrity_signals import _signal_id, validation_errors


SCHEMA_VERSION = "bibliographic-integrity-signal/1.1"
CACHE_SCHEMA_VERSION = "retraction-status-cache/1.0"
CACHE_REVALIDATE_DAYS = 30
_DOI_PREFIX = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.I)
_EVENT_TYPES = {
    "retraction": "retraction",
    "retracted": "retraction",
    "reinstatement": "reinstatement",
    "reinstated": "reinstatement",
    "expression of concern": "expression_of_concern",
    "expression-of-concern": "expression_of_concern",
    "correction": "correction",
}


def _parse_datetime(value: str | None) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def normalize_doi(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = _DOI_PREFIX.sub("", value.strip()).rstrip(".").lower()
    return normalized if normalized.startswith("10.") and "/" in normalized else None


def _canonical_sha(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _event_date(event: Mapping[str, Any]) -> str | None:
    updated = event.get("updated")
    if isinstance(updated, Mapping):
        value = updated.get("date-time")
        if isinstance(value, str) and _parse_datetime(value):
            return value
        parts = updated.get("date-parts")
        if isinstance(parts, list) and parts and isinstance(parts[0], list):
            try:
                year, month, day = (parts[0] + [1, 1])[:3]
                return datetime(year, month, day, tzinfo=timezone.utc).isoformat().replace(
                    "+00:00", "Z"
                )
            except (TypeError, ValueError):
                return None
    return None


def _event_kind(event: Mapping[str, Any]) -> str | None:
    for raw in (event.get("type"), event.get("label"), event.get("update-nature")):
        if isinstance(raw, str):
            key = raw.strip().lower().replace("_", " ")
            if key in _EVENT_TYPES:
                return _EVENT_TYPES[key]
    return None


def _crossref_events(records: Sequence[Mapping[str, Any]], cited_doi: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in records:
        record_doi = normalize_doi(record.get("DOI"))
        containers: list[Mapping[str, Any]] = [record]
        relation = record.get("relation")
        if isinstance(relation, Mapping):
            containers.append(relation)
        for container in containers:
            for direction in ("updated-by", "update-to"):
                raw_events = container.get(direction)
                if not isinstance(raw_events, list):
                    continue
                for raw in raw_events:
                    if not isinstance(raw, Mapping):
                        continue
                    target = normalize_doi(raw.get("DOI") or raw.get("id"))
                    relevant = (
                        direction == "updated-by" and record_doi == cited_doi
                    ) or (direction == "update-to" and target == cited_doi)
                    kind = _event_kind(raw)
                    if not relevant or kind not in {"retraction", "reinstatement"}:
                        continue
                    event = {
                        "kind": kind,
                        "direction": direction,
                        "date": _event_date(raw),
                        "notice_doi": target if direction == "updated-by" else record_doi,
                        "source": raw.get("source") if isinstance(raw.get("source"), str) else None,
                        "record_id": str(raw["record-id"]) if raw.get("record-id") is not None else None,
                    }
                    key = _canonical_sha(event)
                    if key not in seen:
                        seen.add(key)
                        events.append(event)
    return events


def _reduce_crossref(records: Sequence[Mapping[str, Any]], cited_doi: str) -> dict[str, Any]:
    events = _crossref_events(records, cited_doi)
    has_cited_record = any(normalize_doi(record.get("DOI")) == cited_doi for record in records)
    if not events:
        return {
            "verdict": "not_retracted" if has_cited_record else "unknown",
            "event_date": None,
            "events": [],
        }
    status_events = [event for event in events if event["kind"] in {"retraction", "reinstatement"}]
    dated = [(event, _parse_datetime(event["date"])) for event in status_events]
    if any(parsed is None for _, parsed in dated) and len({event["kind"] for event in status_events}) > 1:
        return {"verdict": "disputed", "event_date": None, "events": events}
    latest = max(dated, key=lambda item: item[1] or datetime.min.replace(tzinfo=timezone.utc))[0]
    return {
        "verdict": "reinstated" if latest["kind"] == "reinstatement" else "retracted",
        "event_date": latest["date"],
        "events": events,
    }


def _resolver_observations(
    *,
    cited_doi: str,
    openalex: Mapping[str, Any],
    crossref: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    observations: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []

    oa_status = openalex.get("status")
    oa_record = openalex.get("record")
    if oa_status == "checked" and isinstance(oa_record, Mapping):
        raw = oa_record.get("is_retracted")
        verdict = "retracted" if raw is True else "not_retracted" if raw is False else "unknown"
        locator = oa_record.get("id") if isinstance(oa_record.get("id"), str) else None
        observations.append({"resolver": "OpenAlex", "status": "checked", "verdict": verdict})
        evidence.append({
            "evidence_type": "resolver_response",
            "source_name": "OpenAlex",
            "record_locator": locator,
            "observed_value": verdict,
            "evidence_sha256": _canonical_sha(oa_record),
        })
    else:
        status = oa_status if oa_status in {"degraded", "not_checked"} else "unknown"
        observations.append({"resolver": "OpenAlex", "status": status, "verdict": "unknown"})
        evidence.append({
            "evidence_type": "degradation_record" if status == "degraded" else "metadata_rule",
            "source_name": "OpenAlex",
            "record_locator": None,
            "observed_value": status,
            "evidence_sha256": None,
        })

    cr_status = crossref.get("status")
    cr_records = crossref.get("records")
    if cr_status == "checked" and isinstance(cr_records, list):
        records = [record for record in cr_records if isinstance(record, Mapping)]
        reduced = _reduce_crossref(records, cited_doi)
        observations.append({
            "resolver": "Crossref",
            "status": "checked",
            "verdict": reduced["verdict"],
            "event_date": reduced["event_date"],
            "events": reduced["events"],
        })
        evidence.append({
            "evidence_type": "resolver_response",
            "source_name": "Crossref",
            "record_locator": f"https://api.crossref.org/works/{cited_doi}",
            "observed_value": reduced["verdict"],
            "evidence_sha256": _canonical_sha(records),
        })
    else:
        status = cr_status if cr_status in {"degraded", "not_checked"} else "unknown"
        observations.append({"resolver": "Crossref", "status": status, "verdict": "unknown"})
        evidence.append({
            "evidence_type": "degradation_record" if status == "degraded" else "metadata_rule",
            "source_name": "Crossref",
            "record_locator": None,
            "observed_value": status,
            "evidence_sha256": None,
        })
    return observations, evidence


def _reconcile(observations: Sequence[Mapping[str, Any]]) -> tuple[str, str, str | None]:
    known = [item for item in observations if item.get("verdict") != "unknown"]
    verdicts = {item["verdict"] for item in known}
    event_dates = [item.get("event_date") for item in known if item.get("event_date")]
    event_date = max(event_dates, key=lambda value: _parse_datetime(value) or datetime.min.replace(tzinfo=timezone.utc)) if event_dates else None
    if "disputed" in verdicts or ("retracted" in verdicts and verdicts & {"not_retracted", "reinstated"}):
        return "disputed", "disagree", event_date
    if not known:
        return "unknown", "unknown", event_date
    effective = "reinstated" if "reinstated" in verdicts else next(iter(verdicts))
    agreement = "agree" if len(known) == len(observations) and len(verdicts) == 1 else "partial"
    return effective, agreement, event_date


def _load_bearing(affected_claims: Sequence[str], claim_impacts: Mapping[str, str]) -> str:
    values = [claim_impacts.get(claim) for claim in affected_claims]
    if "HIGH-IMPACT" in values:
        return "high_impact"
    if values and all(value == "OTHER" for value in values):
        return "other"
    return "not_decidable"


def _timing(source_acquisition_date: Any, event_date: str | None) -> str:
    acquired = _parse_datetime(source_acquisition_date if isinstance(source_acquisition_date, str) else None)
    event = _parse_datetime(event_date)
    if acquired is None or event is None:
        return "not_decidable"
    if event.date() == acquired.date():
        return "same_day"
    return "after_acquisition" if event > acquired else "before_acquisition"


def resolve_retraction_signal(
    entry: Mapping[str, Any],
    *,
    openalex: Mapping[str, Any],
    crossref: Mapping[str, Any],
    checked_at: str,
    recorded_at: str,
    stale_after: str,
    affected_claims: Sequence[str] = (),
    claim_impacts: Mapping[str, str] | None = None,
    declaration: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve one v1.1 canonical retraction signal from normalized envelopes."""
    citation_key = entry.get("citation_key")
    if not isinstance(citation_key, str) or not citation_key:
        raise ValueError("entry requires citation_key")
    doi = normalize_doi(entry.get("doi"))
    declaration = declaration or {}
    declared = declaration.get("declared") is True
    notice_cited = declaration.get("retraction_notice_cited") is True
    declaration_id = declaration.get("declaration_id")
    notice_citation_key = declaration.get("notice_citation_key")
    legitimate_exception = (
        declared
        and notice_cited
        and isinstance(declaration_id, str)
        and bool(declaration_id.strip())
        and isinstance(notice_citation_key, str)
        and bool(notice_citation_key.strip())
    )

    if doi is None:
        observations = [
            {"resolver": "OpenAlex", "status": "not_checked", "verdict": "unknown"},
            {"resolver": "Crossref", "status": "not_checked", "verdict": "unknown"},
        ]
        evidence = [{
            "evidence_type": "metadata_rule",
            "source_name": "DOI applicability rule",
            "record_locator": entry.get("source_pointer"),
            "observed_value": "doi_absent",
            "evidence_sha256": None,
        }]
        effective, agreement, event_date = "unknown", "unknown", None
        check_status = "not_checked"
    else:
        observations, evidence = _resolver_observations(
            cited_doi=doi, openalex=openalex, crossref=crossref
        )
        effective, agreement, event_date = _reconcile(observations)
        statuses = {item["status"] for item in observations}
        check_status = "checked" if "checked" in statuses else "degraded" if "degraded" in statuses else "not_checked"

    served_reasons = crossref.get("retraction_reasons")
    reasons = sorted(
        {
            reason.strip()
            for reason in served_reasons
            if isinstance(reason, str) and reason.strip()
        }
    ) if isinstance(served_reasons, list) and effective == "retracted" else []

    freshness = "stale" if (_parse_datetime(recorded_at) or datetime.max.replace(tzinfo=timezone.utc)) > (_parse_datetime(stale_after) or datetime.min.replace(tzinfo=timezone.utc)) else "current"
    strict_eligible = (
        effective == "retracted"
        and agreement != "disagree"
        and freshness == "current"
        and not legitimate_exception
    )
    finding = "detected" if effective == "retracted" else "not_detected" if effective in {"not_retracted", "reinstated"} else "unresolved"
    if finding == "unresolved" and check_status == "checked":
        check_status = "unknown"
    any_resolver_checked = any(
        observation.get("status") == "checked" for observation in observations
    )

    signal = {
        "schema_version": SCHEMA_VERSION,
        "signal_id": _signal_id(citation_key, "retraction_status"),
        "signal_type": "retraction_status",
        "epistemic_class": "deterministic_fact",
        "epistemic_label": "RESOLVER-OR-LIST-OBSERVATION",
        "check_status": check_status,
        "finding": finding,
        "evidence": evidence,
        "provenance": {
            "source_name": "OpenAlex + Crossref",
            "source_version": "works-api/retraction-v1",
            "source_sha256": _canonical_sha(observations),
            "checked_at": checked_at if any_resolver_checked else None,
            "recorded_at": recorded_at,
            "stale_after": stale_after,
            "freshness": freshness,
        },
        "subject": {
            "citation_key": citation_key,
            "source_pointer": entry.get("source_pointer") if isinstance(entry.get("source_pointer"), str) else None,
            "affected_claims": list(affected_claims),
        },
        "terminal_policy": {
            "eligible": strict_eligible,
            "owner": "citation_finalizer" if strict_eligible else "none",
            "policy_key": "retraction" if strict_eligible else None,
            "current_effect": "policy_gated" if strict_eligible else "advisory_only",
        },
        "display": {
            "carrier": "provenance_summary",
            "section": "Bibliographic Integrity Advisories",
            "summary_label": "Retraction-list status",
            "marker_token": None,
        },
        "retraction_context": {
            "doi": doi,
            "effective_status": effective,
            "resolver_agreement": agreement,
            "resolver_observations": observations,
            "retraction_event_date": event_date,
            "retraction_reasons": reasons,
            "reason_availability": "served" if reasons else "not_served",
            "load_bearing": _load_bearing(affected_claims, claim_impacts or {}),
            "claim_join_rule": "worst_tier_wins",
            "source_acquisition_date": entry.get("source_acquisition_date") if isinstance(entry.get("source_acquisition_date"), str) else None,
            "timing_vs_acquisition": _timing(entry.get("source_acquisition_date"), event_date),
            "declared_legitimate_citation": {
                "declared": declared,
                "declaration_id": declaration_id if isinstance(declaration_id, str) else None,
                "retraction_notice_cited": notice_cited,
                "notice_citation_key": notice_citation_key if isinstance(notice_citation_key, str) else None,
                "deterministic_exception": legitimate_exception,
                "contextual_judgment": "not_performed",
            },
        },
    }
    problems = validation_errors(signal)
    if problems:
        raise ValueError("invalid retraction signal: " + "; ".join(problems))
    return signal


def evaluate_retraction_policy(signal: Mapping[str, Any], policy: str | None) -> str | None:
    """Return the finalizer token for an eligible strict row, else None."""
    resolved = policy or "advisory"
    if resolved not in {"advisory", "strict"}:
        raise ValueError("retraction policy must be advisory or strict")
    terminal = signal.get("terminal_policy")
    if resolved == "strict" and isinstance(terminal, Mapping) and terminal.get("eligible") is True:
        return "TERMINAL-BLOCK severity=HIGH-BLOCK policy=retraction reason=retracted_reference mode=strict"
    return None


def citation_policy_slug(policies: Mapping[str, Any]) -> str | None:
    keys = ("citation_existence", "contamination_triangulation", "retraction", "temporal_integrity")
    parts = [f"{key}.{policies[key]}" for key in keys if policies.get(key) not in {None, "advisory"}]
    return "+".join(sorted(parts)) or None


class RetractionStatusCache:
    """Separate, versioned cache namespace for mutable retraction status."""

    _SCHEMA = """
    CREATE TABLE IF NOT EXISTS retraction_status_cache_v1 (
        doi TEXT NOT NULL,
        resolver_name TEXT NOT NULL,
        observation_json TEXT NOT NULL,
        checked_at TEXT NOT NULL,
        schema_version TEXT NOT NULL,
        PRIMARY KEY (doi, resolver_name)
    )
    """

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute(self._SCHEMA)

    def put(self, doi: str, resolver_name: str, observation: Mapping[str, Any], *, checked_at: str) -> None:
        normalized = normalize_doi(doi)
        if normalized is None:
            raise ValueError("cache key requires a DOI")
        if observation.get("status") not in {"checked", "unknown", "degraded"}:
            raise ValueError("cache observation needs typed status")
        if _parse_datetime(checked_at) is None:
            raise ValueError("checked_at must be an ISO-8601 datetime")
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute(
                "INSERT OR REPLACE INTO retraction_status_cache_v1 VALUES (?, ?, ?, ?, ?)",
                (normalized, resolver_name, json.dumps(dict(observation), sort_keys=True), checked_at, CACHE_SCHEMA_VERSION),
            )

    def lookup(self, doi: str, resolver_name: str, *, now: str) -> dict[str, Any] | None:
        normalized = normalize_doi(doi)
        current = _parse_datetime(now)
        if normalized is None or current is None:
            raise ValueError("lookup requires DOI and ISO-8601 now")
        with closing(sqlite3.connect(self.path)) as conn:
            row = conn.execute(
                "SELECT observation_json, checked_at, schema_version FROM retraction_status_cache_v1 WHERE doi = ? AND resolver_name = ?",
                (normalized, resolver_name),
            ).fetchone()
        if row is None or row[2] != CACHE_SCHEMA_VERSION:
            return None
        checked = _parse_datetime(row[1])
        if checked is None:
            return None
        try:
            observation = json.loads(row[0])
        except json.JSONDecodeError:
            return None
        if not isinstance(observation, dict):
            return None
        state = "stale" if current - checked > timedelta(days=CACHE_REVALIDATE_DAYS) else "current"
        return {"cache_state": state, "checked_at": row[1], "observation": observation}


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Resolve a hermetic #651 retraction fixture")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    signal = resolve_retraction_signal(**payload)
    rendered = json.dumps(signal, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
