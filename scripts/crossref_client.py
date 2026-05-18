#!/usr/bin/env python3
"""Minimal Crossref API client wrapper.

Implements the lookup contract documented at
`deep-research/references/crossref_api_protocol.md`. DOI-first with
title cross-check (DOI_MISMATCH pattern), title-similarity fallback,
429 -> 2s backoff x 3 retries, 404/5xx -> miss vs. skip. Mirrors
`semantic_scholar_client.py` / `openalex_client.py` structure.

Crossref-specific: DOI endpoint is /works/{doi} (no doi: prefix);
title search is /works?query.title=...&rows=5; polite-pool email
goes in User-Agent header (not query param); response shape is
nested under `message`; title is a list (multi-language variants).
"""
from __future__ import annotations

import http.client
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Mapping

# Dual-path import: see openalex_client.py comment.
try:
    from _text_similarity import (
        _BACKOFF_SECONDS,
        _MAX_RETRIES,
        _TITLE_SIMILARITY_THRESHOLD,
        _normalize_title,
        _similarity,
    )
except ImportError:
    from scripts._text_similarity import (
        _BACKOFF_SECONDS,
        _MAX_RETRIES,
        _TITLE_SIMILARITY_THRESHOLD,
        _normalize_title,
        _similarity,
    )


_API_BASE = "https://api.crossref.org"
_POLITE_EMAIL_ENV = "CROSSREF_POLITE_EMAIL"

# Crossref polite pool: 10 req/s with mailto, ~5 req/s anonymous (per
# Crossref live response headers: x-rate-limit-limit=10, interval=1s).
_POLITE_MIN_INTERVAL = 0.1
_ANONYMOUS_MIN_INTERVAL = 0.2


def _extract_title(message_or_item: Mapping[str, Any]) -> str:
    """Crossref returns `title` as a list of language variants. Take first or empty."""
    titles = message_or_item.get("title") or []
    return titles[0] if titles else ""


def _extract_year(item: Mapping[str, Any]) -> int | None:
    """Crossref year lives in `issued.date-parts[0][0]` (or `published-print` / `published-online`).
    Prefer `issued` as canonical; fall through to alternatives."""
    for key in ("issued", "published-print", "published-online"):
        val = item.get(key)
        if not isinstance(val, dict):
            continue
        date_parts = val.get("date-parts")
        if date_parts and date_parts[0]:
            return date_parts[0][0]
    return None


class CrossrefUnavailable(Exception):
    """Crossref API degraded -- caller MUST omit `crossref_unmatched`."""


class CrossrefClient:
    """Production lookup-by-(doi-with-cross-check-then-title) client for Crossref.

    Concurrency note: rate-limit pacing is per-instance.
    """

    def __init__(self, polite_email: str | None = None):
        self._polite_email = polite_email or os.environ.get(_POLITE_EMAIL_ENV)
        self._min_interval = (
            _POLITE_MIN_INTERVAL if self._polite_email else _ANONYMOUS_MIN_INTERVAL
        )
        self._last_request_at: float | None = None
        # Polite-pool email goes in User-Agent, not query param.
        ua = "ARS-v3.9.0"
        if self._polite_email:
            ua += f" (mailto:{self._polite_email})"
        self._user_agent = ua

    def _throttle(self) -> None:
        if self._last_request_at is None:
            return
        # time.monotonic for elapsed measurement: NTP / manual clock
        # adjustments can make time.time go backward, producing negative
        # elapsed and either huge sleep or zero sleep (#128 §6). Aligns
        # with semantic_scholar_client.py.
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)

    def _get(self, path: str, query: Mapping[str, str]) -> dict[str, Any]:
        url = f"{_API_BASE}{path}"
        if query:
            url += "?" + urllib.parse.urlencode(query)
        req = urllib.request.Request(url, headers={"User-Agent": self._user_agent})

        self._throttle()
        self._last_request_at = time.monotonic()

        for attempt in range(_MAX_RETRIES + 1):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    # Wrap response body read + decode + parse in a narrow
                    # except so transient socket drops mid-stream, garbled
                    # bodies, or HTML error pages slipped through with 200
                    # status surface as CrossrefUnavailable — honoring the
                    # v3.9.0 spec §3.7 per-API degradation contract (one
                    # transient failure must drop only crossref_unmatched,
                    # not abort the whole backfill). Mirrors openalex_client.
                    try:
                        body = resp.read()
                        return json.loads(body.decode("utf-8"))
                    except (
                        OSError,
                        http.client.HTTPException,
                        UnicodeDecodeError,
                        json.JSONDecodeError,
                    ) as e:
                        # http.client.HTTPException covers IncompleteRead
                        # (truncated body — canonical mid-stream socket drop)
                        # which inherits HTTPException, not OSError. Codex
                        # review v3.9.1 R1 P2.
                        raise CrossrefUnavailable(
                            f"Crossref response read/parse failed: {e}"
                        ) from e
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return {}
                if e.code == 429 and attempt < _MAX_RETRIES:
                    time.sleep(_BACKOFF_SECONDS)
                    # Refresh throttle anchor after backoff so the next outer
                    # _get call's _throttle() paces against actual wake time,
                    # not the original entry time (mirrors openalex_client.py).
                    self._last_request_at = time.monotonic()
                    continue
                raise CrossrefUnavailable(f"Crossref HTTP {e.code}: {e.reason}") from e
            except (urllib.error.URLError, TimeoutError) as e:
                raise CrossrefUnavailable(f"Crossref network error: {e}") from e

        raise CrossrefUnavailable("Crossref rate limit exhausted after retries")

    def doi_lookup_with_title_check(
        self, doi: str, expected_title: str,
    ) -> dict[str, Any] | None:
        """DOI lookup with mandatory Levenshtein 0.70 title cross-check.

        Returns the `message` dict if DOI hit AND title cross-check passes;
        None on 404 (miss), DOI_MISMATCH, or network success but no match.
        """
        data = self._get(f"/works/{doi}", {})
        if not data:  # 404 -> empty dict from _get
            return None
        message = data.get("message", {})
        title = _extract_title(message)
        if _similarity(title, expected_title) >= _TITLE_SIMILARITY_THRESHOLD:
            return message
        return None  # DOI_MISMATCH

    def title_search(
        self, title: str, year: int | None = None,
    ) -> dict[str, Any] | None:
        """Title search with 0.70 similarity threshold + matching-year tiebreaker.

        Returns the best matching candidate dict from `message.items`,
        or None if no candidate meets the threshold.
        """
        data = self._get("/works", {"query.title": title, "rows": "5"})
        candidates = data.get("message", {}).get("items", [])
        scored = []
        for cand in candidates:
            cand_title = _extract_title(cand)
            sim = _similarity(cand_title, title)
            if sim < _TITLE_SIMILARITY_THRESHOLD:
                continue
            year_match = year is not None and _extract_year(cand) == year
            score = sim + (0.05 if year_match else 0.0)
            scored.append((cand, score))
        if not scored:
            return None
        scored.sort(key=lambda cand_score: (-cand_score[1],))
        return scored[0][0]
