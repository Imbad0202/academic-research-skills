#!/usr/bin/env python3
"""Persistent verification cache for the bibliographic resolvers (Delta 2).

A local SQLite-backed cache so the same paper cited across multiple drafts
does not re-hit Crossref / OpenAlex / Semantic Scholar / arXiv every run.

Cache key: (citation_key, resolver_name, query_form).
  - resolver_name ∈ {crossref, openalex, semantic_scholar, arxiv}
  - query_form is the canonical-form DOI / arXiv ID / title-query string the
    resolver was keyed on (the caller passes whichever it used).
Cache value: the resolver's structured response (any JSON-serializable dict)
plus a verification_timestamp.

TTL: entries older than 90 days are treated as a miss. The 90-day window is a
guess pending empirical tuning (spec OQ-1, deferred).

Concurrency: SQLite WAL mode (single-writer-many-readers). The audit pipeline
is single-process; multi-user shared cache is out of scope (spec Delta 2).

Spec: docs/design/2026-05-21-v3.10-182-promote-citation-gate-spec.md §2 Delta 2.
"""
from __future__ import annotations

import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# Spec OQ-1: 90-day window is a guess, deferred for empirical tuning.
_TTL_DAYS = 90

# #541 staleness advisory (Ren et al. arXiv:2607.13104 §6.2.3 "scheduled review
# and attenuation"): entries older than this many days are still HITS (the TTL
# above is the only miss boundary) but carry an advisory flag so stale evidence
# is visible exactly where it is used. 0 disables the advisory. Advisory-only —
# never a gate input.
_STALE_ADVISORY_ENV = "ARS_CACHE_STALE_ADVISORY_DAYS"
_STALE_ADVISORY_DEFAULT_DAYS = 30


def stale_advisory_days() -> int:
    """The #541 advisory threshold in days (env-overridable; 0 disables).

    A malformed or negative override falls back to the default rather than
    erroring: the advisory is a convenience layer and must never break a run.
    """
    raw = os.environ.get(_STALE_ADVISORY_ENV)
    if raw is None:
        return _STALE_ADVISORY_DEFAULT_DAYS
    try:
        value = int(raw)
    except ValueError:
        return _STALE_ADVISORY_DEFAULT_DAYS
    if value < 0:
        return _STALE_ADVISORY_DEFAULT_DAYS
    return value

_DEFAULT_PATH = Path.home() / ".cache" / "ars" / "verification.db"
_ENV_PATH = "ARS_VERIFICATION_CACHE_PATH"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS verification_cache (
    citation_key           TEXT NOT NULL,
    resolver_name          TEXT NOT NULL,
    query_form             TEXT NOT NULL,
    response_json          TEXT NOT NULL,
    verification_timestamp TEXT NOT NULL,
    PRIMARY KEY (citation_key, resolver_name, query_form)
)
"""


def _parse_ts(verification_timestamp: str) -> datetime | None:
    """Parse a stored ISO timestamp defensively (#541): naive timestamps
    (written by older/other tools) are read as UTC; malformed strings return
    None (callers treat the row as a miss / skip it — never abort)."""
    try:
        stored = datetime.fromisoformat(verification_timestamp)
    except (ValueError, TypeError):
        return None
    if stored.tzinfo is None:
        stored = stored.replace(tzinfo=timezone.utc)
    return stored


def _resolve_path(path: str | None) -> Path:
    """Explicit arg wins over the env override, which wins over the default."""
    if path is not None:
        return Path(path)
    env = os.environ.get(_ENV_PATH)
    if env:
        return Path(env)
    return _DEFAULT_PATH


class VerificationCache:
    """SQLite-backed (citation_key, resolver_name, query_form) → response cache.

    Single-process use. Each method opens a short-lived connection so the
    cache holds no long-lived file handle across pipeline stages.
    """

    def __init__(self, path: str | None = None) -> None:
        self.path = str(_resolve_path(path))
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        # `closing(...) as conn, conn` — the outer ctx closes the handle, the
        # inner (the connection itself) commits/rolls back. Honors the
        # short-lived-connection contract (no leaked handle across stages).
        with closing(self._connect()) as conn, conn:
            conn.execute(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        # WAL: single-writer-many-readers safety (spec Delta 2). Persistent
        # journal-mode pragma — set on every connection (cheap; no-op when
        # already WAL).
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def get(
        self, citation_key: str, resolver_name: str, query_form: str,
    ) -> dict[str, Any] | None:
        """Return the cached response, or None on miss / expired entry.

        An entry whose verification_timestamp is older than the TTL is a
        miss (the caller then makes the live call and re-populates).
        """
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT response_json, verification_timestamp "
                "FROM verification_cache "
                "WHERE citation_key = ? AND resolver_name = ? AND query_form = ?",
                (citation_key, resolver_name, query_form),
            ).fetchone()
        if row is None:
            return None
        response_json, ts = row
        if self._is_expired(ts):
            return None
        # #331: a corrupted payload (not decodable) or a non-dict value (e.g.
        # written by an older/other tool) is a miss, not a hard error — the
        # documented contract is "malformed cache payload = miss". Returning None
        # forces a clean live recompute instead of aborting verification with a
        # JSONDecodeError or handing the caller a shape it cannot read.
        try:
            value = json.loads(response_json)
        except (json.JSONDecodeError, TypeError):
            return None
        if not isinstance(value, dict):
            return None
        return value

    def put(
        self,
        citation_key: str,
        resolver_name: str,
        query_form: str,
        response: dict[str, Any],
    ) -> None:
        """Store (or overwrite) the resolver response, stamping it now (UTC)."""
        now = datetime.now(timezone.utc).isoformat()
        with closing(self._connect()) as conn, conn:
            conn.execute(
                "INSERT OR REPLACE INTO verification_cache "
                "(citation_key, resolver_name, query_form, response_json, "
                " verification_timestamp) VALUES (?, ?, ?, ?, ?)",
                (
                    citation_key,
                    resolver_name,
                    query_form,
                    json.dumps(response),
                    now,
                ),
            )

    def invalidate(self, citation_key: str) -> None:
        """Drop every cached entry (all resolvers, all query forms) for a
        citation. Backs the /ars-cache-invalidate command. No-op when the
        citation has no cached rows."""
        with closing(self._connect()) as conn, conn:
            conn.execute(
                "DELETE FROM verification_cache WHERE citation_key = ?",
                (citation_key,),
            )

    def entry_age_days(self, citation_key: str) -> float | None:
        """Age in days of the OLDEST live (non-expired) cached row for a
        citation, across resolvers and query forms — deliberately the most
        conservative citation-level signal (#541): an unexpired row for an
        obsolete query form can flag a citation whose latest verification is
        fresh. That false-positive direction is accepted (advisory-only; a
        stale warning that prompts one unnecessary look is cheaper than a
        missed stale source). None when the citation has no live rows.
        Malformed timestamps are skipped; naive timestamps are read as UTC;
        clock-skewed future timestamps clamp to age 0.
        """
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT verification_timestamp FROM verification_cache "
                "WHERE citation_key = ?",
                (citation_key,),
            ).fetchall()
        ages = []
        now = datetime.now(timezone.utc)
        for (ts,) in rows:
            if self._is_expired(ts):
                continue
            stored = _parse_ts(ts)
            if stored is None:
                continue
            ages.append(max(0.0, (now - stored).total_seconds() / 86400.0))
        return max(ages) if ages else None

    def row_age_days(
        self, citation_key: str, resolver_name: str, query_form: str,
    ) -> float | None:
        """Age in days of ONE live cached row (#541 per-row form — backs the
        stale-revalidate bypass, which must judge exactly the row it would
        serve). None on miss / expired / malformed timestamp. Future
        timestamps clamp to 0."""
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT verification_timestamp FROM verification_cache "
                "WHERE citation_key = ? AND resolver_name = ? AND query_form = ?",
                (citation_key, resolver_name, query_form),
            ).fetchone()
        if row is None or self._is_expired(row[0]):
            return None
        stored = _parse_ts(row[0])
        if stored is None:
            return None
        return max(
            0.0, (datetime.now(timezone.utc) - stored).total_seconds() / 86400.0
        )

    def stale_report(
        self, citation_keys: list[str],
    ) -> dict[str, dict[str, Any]]:
        """Per-citation #541 staleness report for the integrity gate.

        Returns {citation_key: {"cache_age_days": float,
        "cache_stale_advisory": bool}} for keys that have at least one live
        cached row; keys with no live rows are omitted (nothing cache-served =
        nothing to warn about). `cache_stale_advisory` is True iff the
        threshold is enabled (>0) and the oldest live row exceeds it.
        Advisory-only: callers MUST NOT gate on this report.
        """
        threshold = stale_advisory_days()
        report: dict[str, dict[str, Any]] = {}
        for key in citation_keys:
            age = self.entry_age_days(key)
            if age is None:
                continue
            rounded = round(age, 1)
            # The flag is computed from the SAME rounded value the report
            # emits, so the emitted pair is always self-consistent (a raw age
            # of threshold+epsilon that rounds down to the threshold does not
            # flag).
            report[key] = {
                "cache_age_days": rounded,
                "cache_stale_advisory": bool(threshold and rounded > threshold),
            }
        return report

    @staticmethod
    def _is_expired(verification_timestamp: str) -> bool:
        stored = _parse_ts(verification_timestamp)
        if stored is None:
            return True  # malformed timestamp = expired = miss, never an abort
        return datetime.now(timezone.utc) - stored > timedelta(days=_TTL_DAYS)
