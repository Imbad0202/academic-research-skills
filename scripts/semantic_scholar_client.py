#!/usr/bin/env python3
"""Minimal Semantic Scholar API client wrapper.

Implements the lookup contract documented at
`deep-research/references/semantic_scholar_api_protocol.md` for the
v3.7.3 contamination-signals migration tool (#105). DOI-first, title-
similarity fallback, 429 backoff per the protocol's retry budget.

Not a general-purpose S2 client — this is the migration tool's narrow
need (single-paper existence check). When ARS later adds a broader S2
helper, this module's `SemanticScholarClient` class should satisfy the
contamination_signals.SemanticScholarClient Protocol so the migration
tool can switch over without code changes.
"""
from __future__ import annotations

import os
import string
import time
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from typing import Any, Mapping

from contamination_signals import SemanticScholarUnavailable


_PUNCT_TRANSLATION = str.maketrans({c: " " for c in string.punctuation})


# Per protocol: api.semanticscholar.org/graph/v1, 1 req/s unauthenticated.
_API_BASE = "https://api.semanticscholar.org/graph/v1"
_API_KEY_ENV = "S2_API_KEY"
_FIELDS = "title,authors,year,externalIds,venue,publicationDate"

# Per protocol: 429 → 2s backoff × 3 retries.
_BACKOFF_SECONDS = 2.0
_MAX_RETRIES = 3

# Per PaperOrchestra (Song et al. 2026 Appx D.3) + protocol §"Query
# Patterns" Pattern 1: title-similarity threshold for "matched" verdict.
_TITLE_SIMILARITY_THRESHOLD = 0.70


def _normalize_title(s: str) -> str:
    """Per protocol §"Query Patterns" Pattern 1: 'case-insensitive,
    stripped of punctuation' before computing similarity. Punctuation
    becomes whitespace so token boundaries are preserved, then collapse
    runs of whitespace. Codex R4-1 closure: raw lowercased comparison
    falsely scored 'R.A.G.' vs 'RAG' below the 0.70 threshold."""
    cleaned = s.lower().translate(_PUNCT_TRANSLATION)
    return " ".join(cleaned.split())


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _normalize_title(a), _normalize_title(b)).ratio()


class SemanticScholarClient:
    """Production lookup-by-(doi-then-title) client for v3.7.3 backfill.

    Satisfies `contamination_signals.SemanticScholarClient` Protocol.
    Tests inject MagicMocks; production callers use this concrete class.
    """

    def __init__(self, api_key: str | None = None, sleep: Any = time.sleep) -> None:
        self._api_key = api_key or os.environ.get(_API_KEY_ENV)
        self._sleep = sleep

    def lookup(self, entry: Mapping[str, Any]) -> Mapping[str, Any]:
        """Return {"matched": bool, "paperId": str | None}.

        Per protocol §"Query Patterns" + §"Response Handling":
        `semantic_scholar_unmatched` is True only when NEITHER DOI nor
        title lookup yields a hit. So:

        1. If `doi` present → GET /paper/DOI:{doi}; on hit, cross-check
           returned title (Levenshtein ≥ 0.70). DOI_MISMATCH (title
           differs despite DOI hit) AND DOI-404 BOTH fall through to (2)
           rather than returning no-match immediately — the v3.7.3
           Vector 2 contract requires both DOI AND title to miss before
           setting the signal. Codex R2-2 closure.
        2. Title search: GET /paper/search?query={url-encoded-title};
           pick the top result with title similarity ≥ 0.70, prefer
           matching year.

        Raises SemanticScholarUnavailable on:
        - HTTP 429 after exhausting `_MAX_RETRIES` retries
        - HTTP 5xx
        - Network error (URLError)
        """
        doi = entry.get("doi")
        title = entry.get("title") or ""
        if doi:
            doi_result = self._lookup_by_doi(doi, title)
            if doi_result["matched"]:
                return doi_result
            # DOI miss or DOI_MISMATCH: fall through to title search
            # per protocol §Vector 2 "neither DOI nor title" rule.
        if title:
            return self._lookup_by_title(title, entry.get("year"))
        return {"matched": False, "paperId": None}

    def _request(self, path: str) -> dict[str, Any]:
        url = f"{_API_BASE}{path}"
        headers = {"User-Agent": "ARS-migration/1.0"}
        if self._api_key:
            headers["x-api-key"] = self._api_key
        req = urllib.request.Request(url, headers=headers)

        for attempt in range(_MAX_RETRIES + 1):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    import json
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return {}
                if e.code == 429 and attempt < _MAX_RETRIES:
                    self._sleep(_BACKOFF_SECONDS)
                    continue
                if 500 <= e.code < 600:
                    raise SemanticScholarUnavailable(
                        f"S2 API HTTP {e.code}"
                    ) from e
                raise SemanticScholarUnavailable(
                    f"S2 API HTTP {e.code} after {_MAX_RETRIES} retries"
                ) from e
            except urllib.error.URLError as e:
                raise SemanticScholarUnavailable(f"S2 API network error: {e}") from e
            except (OSError, TimeoutError) as e:
                # Response-body read timeouts (socket.timeout subclasses
                # OSError; TimeoutError is the 3.10+ alias) and other
                # transient I/O failures during resp.read() must be
                # treated as API degradation per spec — never let them
                # abort the migration. Codex R4-2 closure.
                raise SemanticScholarUnavailable(
                    f"S2 API I/O failure during response read: {e}"
                ) from e
        raise SemanticScholarUnavailable(f"S2 API exhausted {_MAX_RETRIES} retries")

    def _lookup_by_doi(self, doi: str, expected_title: str) -> dict[str, Any]:
        data = self._request(f"/paper/DOI:{urllib.parse.quote(doi)}?fields={_FIELDS}")
        if not data or not data.get("paperId"):
            return {"matched": False, "paperId": None}
        # Per protocol: cross-check title; DOI_MISMATCH counts as no-match
        # for this binary signal.
        returned_title = data.get("title") or ""
        if _similarity(expected_title, returned_title) < _TITLE_SIMILARITY_THRESHOLD:
            return {"matched": False, "paperId": None}
        return {"matched": True, "paperId": data["paperId"]}

    def _lookup_by_title(self, title: str, year: int | None) -> dict[str, Any]:
        path = (
            f"/paper/search?query={urllib.parse.quote(title)}"
            f"&limit=5&fields={_FIELDS}"
        )
        data = self._request(path)
        candidates = data.get("data") or []
        best: tuple[float, dict[str, Any]] | None = None
        for cand in candidates:
            sim = _similarity(title, cand.get("title") or "")
            if sim < _TITLE_SIMILARITY_THRESHOLD:
                continue
            # Per protocol: prefer matching year when multiple ≥0.70 results.
            year_match = year is not None and cand.get("year") == year
            score = sim + (0.05 if year_match else 0.0)
            if best is None or score > best[0]:
                best = (score, cand)
        if best is None:
            return {"matched": False, "paperId": None}
        return {"matched": True, "paperId": best[1].get("paperId")}
