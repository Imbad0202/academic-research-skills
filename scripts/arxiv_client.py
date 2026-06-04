#!/usr/bin/env python3
"""Minimal arXiv API client wrapper.

Implements the lookup contract documented at
`deep-research/references/arxiv_api_protocol.md`. arXiv-ID-first with
title cross-check (ID_MISMATCH pattern), title-similarity fallback,
429 -> 2s backoff x 3 retries, network/5xx -> ArxivUnavailable. Mirrors
`crossref_client.py` / `openalex_client.py` structure.

arXiv-specific differences from the Crossref/OpenAlex siblings:
  - The query API returns Atom 1.0 XML, NOT JSON. `_get` parses with
    `xml.etree.ElementTree`; the Atom namespace is
    `{http://www.w3.org/2005/Atom}`.
  - The exact-key endpoint is keyed by arXiv ID, not DOI:
    `?id_list={id}` for ID lookup, `?search_query=ti:"{title}"` for the
    title fallback. The base is `http://export.arxiv.org/api/query`.
  - There is no polite-pool email convention. Rate-limit pacing is a
    fixed min-interval; arXiv asks callers to wait ~3s between requests
    (https://info.arxiv.org/help/api/tou.html), so `_ARXIV_MIN_INTERVAL`
    is 3.0s.

Delta 1 of docs/design/2026-05-21-v3.10-182-promote-citation-gate-spec.md.
"""
from __future__ import annotations

import http.client
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any

# Dual-path import: see openalex_client.py comment.
try:
    from _text_similarity import (
        _BACKOFF_SECONDS,
        _MAX_RETRIES,
        _TITLE_SIMILARITY_THRESHOLD,
        _similarity,
    )
except ImportError:
    from scripts._text_similarity import (
        _BACKOFF_SECONDS,
        _MAX_RETRIES,
        _TITLE_SIMILARITY_THRESHOLD,
        _similarity,
    )


_API_BASE = "http://export.arxiv.org/api/query"
_ATOM_NS = "{http://www.w3.org/2005/Atom}"

# arXiv API Terms of Use ask callers to pace requests ~3s apart.
_ARXIV_MIN_INTERVAL = 3.0


def _extract_title(entry: ET.Element) -> str:
    """Atom <entry><title> text; arXiv collapses internal whitespace/newlines
    in the title, so normalize runs of whitespace to single spaces."""
    node = entry.find(f"{_ATOM_NS}title")
    if node is None or node.text is None:
        return ""
    return " ".join(node.text.split())


def _extract_year(entry: ET.Element) -> int | None:
    """Atom <entry><published> is ISO-8601 (e.g. 2017-06-12T...); year is the
    leading 4 digits. Returns None when absent or unparseable."""
    node = entry.find(f"{_ATOM_NS}published")
    if node is None or not node.text:
        return None
    head = node.text[:4]
    return int(head) if head.isdigit() else None


def _entry_to_dict(entry: ET.Element) -> dict[str, Any]:
    """Project an Atom <entry> into the dict shape callers consume."""
    return {"title": _extract_title(entry), "year": _extract_year(entry)}


class ArxivUnavailable(Exception):
    """arXiv API degraded -- caller MUST omit `arxiv_unmatched`."""


class ArxivClient:
    """Production lookup-by-(arxiv-id-with-cross-check-then-title) client.

    Concurrency note: rate-limit pacing is per-instance.
    """

    def __init__(self) -> None:
        self._min_interval = _ARXIV_MIN_INTERVAL
        self._last_request_at: float | None = None
        self._user_agent = "ARS-v3.11"

    def _throttle(self) -> None:
        if self._last_request_at is None:
            return
        # time.monotonic for elapsed measurement: NTP / manual clock
        # adjustments can make time.time go backward (#128 §6). Aligns
        # with crossref_client.py / semantic_scholar_client.py.
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)

    def _get(self, query: dict[str, str]) -> list[ET.Element]:
        """GET the query endpoint and return the list of Atom <entry> elements
        (empty list when the feed has none -- arXiv's miss shape)."""
        url = _API_BASE
        if query:
            url += "?" + urllib.parse.urlencode(query)
        req = urllib.request.Request(url, headers={"User-Agent": self._user_agent})

        self._throttle()
        self._last_request_at = time.monotonic()

        for attempt in range(_MAX_RETRIES + 1):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    # Wrap read + parse in a narrow except so transient socket
                    # drops mid-stream and truncated / malformed bodies surface
                    # as ArxivUnavailable -- honoring the per-API degradation
                    # contract (one transient failure drops only arxiv_unmatched,
                    # never aborts the backfill). Note: a *complete* non-Atom
                    # body (e.g. a well-formed HTML error page served with 200)
                    # parses fine and yields zero Atom entries -- that is a miss,
                    # not a degradation; only genuinely malformed XML raises
                    # ParseError here. Mirrors crossref_client.py's read/parse
                    # except (ET.ParseError replaces JSONDecodeError).
                    try:
                        body = resp.read()
                        root = ET.fromstring(body)
                    except (
                        OSError,
                        http.client.HTTPException,
                        ET.ParseError,
                    ) as e:
                        # http.client.HTTPException covers IncompleteRead
                        # (truncated body) which inherits HTTPException, not
                        # OSError. ET.ParseError replaces crossref's
                        # JSONDecodeError for the XML payload.
                        raise ArxivUnavailable(
                            f"arXiv response read/parse failed: {e}"
                        ) from e
                    return root.findall(f"{_ATOM_NS}entry")
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < _MAX_RETRIES:
                    time.sleep(_BACKOFF_SECONDS)
                    # Refresh throttle anchor after backoff so the next outer
                    # _get call paces against actual wake time (mirrors
                    # crossref_client.py).
                    self._last_request_at = time.monotonic()
                    continue
                raise ArxivUnavailable(f"arXiv HTTP {e.code}: {e.reason}") from e
            except (urllib.error.URLError, TimeoutError) as e:
                raise ArxivUnavailable(f"arXiv network error: {e}") from e

        raise ArxivUnavailable("arXiv rate limit exhausted after retries")

    def arxiv_id_lookup(
        self, arxiv_id: str, expected_title: str,
    ) -> dict[str, Any] | None:
        """arXiv ID lookup with mandatory 0.70 title cross-check.

        Returns the projected entry dict if the ID resolves AND the title
        cross-check passes; None on empty feed (miss) or ID_MISMATCH.
        """
        entries = self._get({"id_list": arxiv_id})
        if not entries:  # non-existent ID -> empty feed
            return None
        entry = entries[0]
        title = _extract_title(entry)
        if _similarity(title, expected_title) >= _TITLE_SIMILARITY_THRESHOLD:
            return _entry_to_dict(entry)
        return None  # ID_MISMATCH

    def title_search(
        self, title: str, year: int | None = None,
    ) -> dict[str, Any] | None:
        """Title search with 0.70 similarity threshold + matching-year tiebreaker.

        Returns the best matching projected entry dict, or None if no
        candidate meets the threshold.
        """
        entries = self._get({"search_query": f'ti:"{title}"', "max_results": "5"})
        scored = []
        for cand in entries:
            cand_title = _extract_title(cand)
            sim = _similarity(cand_title, title)
            if sim < _TITLE_SIMILARITY_THRESHOLD:
                continue
            year_match = year is not None and _extract_year(cand) == year
            score = sim + (0.05 if year_match else 0.0)
            scored.append((cand, score))
        if not scored:
            return None
        scored.sort(key=lambda cand_score: -cand_score[1])
        return _entry_to_dict(scored[0][0])
