#!/usr/bin/env python3
"""Firecrawl research-index client.

Implements the lookup contract documented at
`deep-research/references/firecrawl_api_protocol.md`.

WHY THIS EXISTS: the four gate resolvers (Semantic Scholar / OpenAlex /
Crossref / arXiv) are keyed on a DOI or an arXiv ID. A preprint or a
conference paper that carries neither — and a PubMed-only record whose DOI the
citation omits — reduces to `unresolvable`, the same state a fabricated
reference produces. Firecrawl's research index is keyed on its own canonical
`paperId` plus source-namespaced ids (`arxiv:`, `pmid:`, `pmcid:`), so it can
put an ID-keyed answer under a citation the DOI-keyed resolvers cannot reach.
It also exposes paper full-text passages, which no sibling resolver does: a
retrieved passage is what lets a human check whether a cited work actually
contains the method or result attributed to it.

Two upstream endpoints (both work without an account; a key only raises the
rate limit, so the gate's key-free reproducibility choice is preserved):

  1. GET /v2/search/research/papers/{id}          -> ID-keyed metadata
  2. GET /v2/search/research/papers?query=&k=     -> ranked paper search
     GET /v2/search/research/papers/{id}?query=   -> full-text passages

Differences from the Crossref / OpenAlex / S2 / arXiv siblings:

  - RANKED SEMANTIC SEARCH, NOT LOOKUP. The search endpoint always returns its
    nearest neighbours: a deliberately fabricated title still came back with
    three real papers attached (measured, see the protocol doc). "Search
    returned rows" is therefore NEVER existence evidence here, and this client
    exposes no `*_unmatched` boolean. `title_search` keeps the #431
    exact-title-or-bust gate for that reason, and it is the ONLY sibling
    matcher whose non-exact rejections are the common case rather than the
    edge.
  - THE INDEX IS NOT PAPERS-ONLY. Records under a `web:` namespace (a
    dictionary entry was observed for `query=test`) share the response shape
    with real paper records. `title_search` drops them: a web page is not a
    bibliographic record and must never be offered as one.
  - NO VENUE PUBLICATION YEAR. The index exposes `createdDate` / `updateDate`
    (index-side deposit dates), not a venue year, so the siblings' +0.05
    matching-year tiebreaker is deliberately NOT reimplemented — see
    `title_search`. Reading `createdDate` as a publication year would
    misdate every published-after-preprint work in the corpus.
  - UNSUPPORTED ID FORMS RAISE, THEY DO NOT MISS. A DOI contains `/`, which
    the path-keyed endpoint answers with a 404 HTML body. Returning None there
    would hand a DOI-keyed caller a miss that looks like non-existence
    evidence, so `_require_supported_id` raises instead (absent != false).
  - 429 HONORS `Retry-After`. Firecrawl documents the header and asks callers
    to wait at least that long; the shared exponential backoff is the fallback
    when it is absent.

STATUS: standalone client. It is NOT wired into `scripts/verification_gate/`,
the `resolver_outcomes` schema, the k=0..4 triangulation matrix, or
`shared/contracts/degradation_registry.json` — the same deliberate boundary
`chinese_literature_client.py` (#595) holds. The protocol doc's "Where this
stops" section enumerates what an integration would still have to decide,
starting with the fact that a ranked semantic index cannot supply a
`*_unmatched` signal on the shape the triangulation matrix consumes.
"""
from __future__ import annotations

import http.client
import json
import os
import re
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
        _similarity,
        exact_normalized_title,
        generic_title,
    )
except ImportError:
    from scripts._text_similarity import (
        _BACKOFF_SECONDS,
        _MAX_RETRIES,
        _TITLE_SIMILARITY_THRESHOLD,
        _similarity,
        exact_normalized_title,
        generic_title,
    )


_API_BASE = "https://api.firecrawl.dev/v2/search/research"
_API_HOST = "api.firecrawl.dev"
_API_KEY_ENV = "FIRECRAWL_API_KEY"

# The endpoints expose no rate-limit headers, and the per-minute ceiling is
# per-plan (https://docs.firecrawl.dev/rate-limits), so pacing is chosen
# conservatively rather than derived from a documented budget. The keyless
# tier is the slower one because it is the shared-quota path.
_AUTHENTICATED_MIN_INTERVAL = 0.2
_ANONYMOUS_MIN_INTERVAL = 1.0

# Mirrors the siblings' 5-candidate title-search window (S2/OpenAlex
# `per-page=5`, arXiv `max_results=5`). The endpoint honors much larger `k`
# (200 verified), which this client has no use for: past the exact-title gate
# a longer ranked tail only adds nearest neighbours that cannot match.
_SEARCH_K = 5

# Namespaces the path-keyed endpoint actually accepts: a bare canonical
# `paperId` (all digits) or one of the source-prefixed forms. Verified live —
# `arxiv:1706.03762`, a version suffix (`...v5`), `pmid:`, `pmcid:` and the
# bare numeric id all resolve; `doi:10.1038/nature14539` does not (the `/`
# leaves the route and answers 404 HTML).
_SUPPORTED_ID_RE = re.compile(r"^(?:[0-9]+|(?:arxiv|pmid|pmcid):[A-Za-z0-9._-]+)$")

# Records the index serves that are not bibliographic records. They carry the
# same fields as a paper, so the namespace is the only discriminator.
_NON_PAPER_ID_PREFIXES = ("web:",)


def _require_api_url(url: str) -> None:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != _API_HOST:
        raise FirecrawlUnavailable(f"Refusing non-Firecrawl URL: {url}")


class _RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """Refuse every redirect instead of following it.

    Not defensive boilerplate — it closes a credential leak. CPython's default
    `HTTPRedirectHandler.redirect_request` rebuilds the Request with
    `{k: v for k, v in req.headers.items() if k.lower() not in
    CONTENT_HEADERS}`, and `CONTENT_HEADERS` is only
    `("content-length", "content-type")`. `Authorization` is therefore copied
    verbatim to whatever host a `Location` names, cross-origin included
    (verified: a `Bearer` key sent to a redirecting local server arrived at a
    third-party listener). `_require_api_url` validates only the URL this
    client builds, so it cannot see a redirect target — the host check would
    pass and the key would still leave.

    Refusing outright (rather than validating each hop) is the right shape
    here: these endpoints do not redirect in normal operation, so a hop is
    already an anomaly, and the sibling `chinese_literature_client.py` refuses
    an off-allowlist hop for the same reason.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise FirecrawlUnavailable(
            f"Refusing HTTP {code} redirect to {newurl!r}: the research-index "
            f"endpoints do not redirect, and following a hop would forward the "
            f"Authorization header off-host."
        )


# Module-level opener so redirect refusal cannot be bypassed by a caller.
# This is the one deliberate divergence from the siblings' bare
# `urllib.request.urlopen`: they send no Authorization header, so a followed
# redirect cannot leak a credential for them.
_OPENER = urllib.request.build_opener(_RefuseRedirects)


def _require_supported_id(paper_id: str) -> None:
    """Guard the path-keyed endpoint's accepted id grammar.

    Deliberately raises rather than returning a miss. A DOI (or any other
    unsupported key) answers 404, and this client's callers read a `None` as
    "the index does not hold this work" — which, in a suite whose whole
    citation gate distinguishes `unresolvable` from `false`, is the one
    confusion that must not be possible. `absent != false` (#331).
    """
    if not _SUPPORTED_ID_RE.match(paper_id or ""):
        raise FirecrawlUnavailable(
            f"Unsupported research-index id {paper_id!r}: expected a canonical "
            f"numeric paperId or an arxiv:/pmid:/pmcid: id. DOIs are NOT a key "
            f"for this index — use the DOI-keyed sibling resolvers."
        )


def _retry_after_seconds(headers: Any) -> float | None:
    """Firecrawl documents a `Retry-After` (seconds) on 429 and asks callers to
    wait at least that long. Returns None when absent or unparseable, so the
    caller falls back to the shared exponential backoff."""
    if headers is None:
        return None
    value = headers.get("Retry-After")
    if value is None:
        return None
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        return None  # HTTP-date form is legal but not what this API sends
    return seconds if seconds >= 0 else None


def _require_shape(data: Mapping[str, Any], key: str, expected: type) -> Any:
    """Return `data[key]`, or raise if it is absent / the wrong type.

    A `success: true` answer that omits the field the endpoint is defined to
    return is schema drift or a mangled response, NOT a miss — and it must not
    be reducible to one, because a `None` from the ID path is read as
    ID-keyed non-existence evidence (`absent != false`, #331).

    Raising is verified safe against legitimately empty answers: both fields
    are present-but-empty rather than omitted when there is nothing to return
    (measured 2026-09-02 — `passages: []` for a paper with no indexed full
    text, `results: []` for a query whose author/date filters match nothing).
    So this can only fire on a genuinely malformed body.
    """
    value = data.get(key)
    if not isinstance(value, expected):
        raise FirecrawlUnavailable(
            f"Firecrawl 200 answer has no well-formed `{key}`: got "
            f"{type(value).__name__}, expected {expected.__name__}. Schema "
            f"drift is a degradation, never a miss."
        )
    return value


def _is_paper_record(record: Mapping[str, Any]) -> bool:
    """False for the index's non-bibliographic records (`web:` namespace).

    An id-less record is also False: without an id there is nothing to key a
    bibliographic record on, so it must not be offered as one. Requiring the
    id positively (rather than only excluding known-bad prefixes) also means a
    future non-paper namespace fails closed instead of passing as a paper.
    """
    primary = record.get("primaryId") or record.get("paperId") or ""
    if not isinstance(primary, str) or not primary:
        return False
    return not primary.startswith(_NON_PAPER_ID_PREFIXES)


def _record_to_dict(record: Mapping[str, Any]) -> dict[str, Any]:
    """Project an index record into the dict shape callers consume.

    `year` is deliberately absent — see the module docstring: the index has no
    venue publication year and `createdDate` is not one.

    `primaryId` is present on search results but NOT on the ID-path `paper`
    object, so it is None for a `paper_id_lookup` hit. Left as None rather than
    reconstructed from `ids`: which namespace the index considers preferred is
    the index's answer to give, not this client's to guess.
    """
    return {
        "paperId": record.get("paperId"),
        "primaryId": record.get("primaryId"),
        "title": record.get("title") or "",
        "ids": record.get("ids") or {},
    }


class FirecrawlUnavailable(Exception):
    """Firecrawl research index degraded, or asked for an unsupported key.

    Callers MUST NOT reduce this to a miss: no signal is emitted for the entry.
    """


class FirecrawlResearchClient:
    """Standalone research-index client: ID-keyed lookup, exact-title search,
    and full-text passage retrieval.

    Concurrency note: rate-limit pacing is per-instance. Share a single
    instance across a run (mirrors the sibling clients).
    """

    def __init__(self, api_key: str | None = None) -> None:
        # The key is OPTIONAL by design. Both endpoints answer without an
        # Authorization header (verified live); a key only raises the rate
        # limit. That keeps this client on the same key-free footing as the
        # four gate resolvers, whose key-optionality is a deliberate
        # reproducibility choice (docs/DATA_FLOWS.md).
        self._api_key = api_key or os.environ.get(_API_KEY_ENV)
        self._min_interval = (
            _AUTHENTICATED_MIN_INTERVAL
            if self._api_key
            else _ANONYMOUS_MIN_INTERVAL
        )
        self._last_request_at: float | None = None

    def _throttle(self) -> None:
        if self._last_request_at is None:
            return
        # time.monotonic for elapsed measurement: NTP / manual clock
        # adjustments can make time.time go backward (#128 §6). Aligns with
        # openalex_client.py / arxiv_client.py.
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)

    def _get(self, path: str, query: Mapping[str, str]) -> dict[str, Any] | None:
        """GET a research-index path.

        Returns **None** for a verified 404 (the index's miss shape) and a
        parsed `success: true` body otherwise. The None-vs-dict split matters:
        an empty dict would make "the index does not hold this id" and "the
        answer arrived without the field we need" indistinguishable, and only
        the first is a miss. Raises `FirecrawlUnavailable` on every
        degradation.
        """
        url = f"{_API_BASE}{path}"
        if query:
            url += "?" + urllib.parse.urlencode(query)
        _require_api_url(url)
        headers = {"User-Agent": "ARS-research-index-client"}
        if self._api_key:
            # Header auth, not a query param: the key never reaches the URL,
            # so it cannot land in a log line or a raised-exception message.
            headers["Authorization"] = f"Bearer {self._api_key}"
        req = urllib.request.Request(url, headers=headers)

        self._throttle()
        self._last_request_at = time.monotonic()

        for attempt in range(_MAX_RETRIES + 1):
            try:
                # URL is fixed-host HTTPS after _require_api_url(), and
                # _OPENER refuses redirects so it stays that way.
                with _OPENER.open(req, timeout=30) as resp:  # nosec B310
                    # Narrow except around read + decode + parse so a
                    # mid-stream socket drop, a truncated body, or an HTML
                    # error page served with 200 surfaces as a degradation
                    # rather than a miss. Mirrors openalex_client.py.
                    try:
                        body = resp.read()
                        data = json.loads(body.decode("utf-8"))
                    except (
                        OSError,
                        http.client.HTTPException,
                        UnicodeDecodeError,
                        json.JSONDecodeError,
                    ) as e:
                        # http.client.HTTPException covers IncompleteRead
                        # (truncated body), which inherits HTTPException,
                        # not OSError.
                        raise FirecrawlUnavailable(
                            f"Firecrawl response read/parse failed: {e}"
                        ) from e
                    # #331 non-expected-200-body guard: a complete JSON body
                    # that is not an index answer (a proxy's JSON error page,
                    # or `success: false` served with 200) parses cleanly but
                    # is NOT a result. A genuine miss is a 404, handled below,
                    # so a 200 without `success: true` is a degradation — not
                    # a miss that would persist as a false signal.
                    if not isinstance(data, dict) or data.get("success") is not True:
                        raise FirecrawlUnavailable(
                            "Firecrawl returned a 200 body that is not an index "
                            "answer (no `success: true`)"
                        )
                    return data
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    # The path-keyed endpoint's miss shape. Two body forms
                    # observed — JSON (`code: NOT_FOUND`) for an unknown id in
                    # a supported namespace, and HTML for an id that leaves
                    # the route — so the body is deliberately not read.
                    return None
                if e.code == 429 and attempt < _MAX_RETRIES:
                    # Honor the documented Retry-After when present; otherwise
                    # fall back to the shared exponential backoff
                    # (2s -> 4s -> 8s), the same shape openalex_client.py uses
                    # for a transient burst 429.
                    delay = _retry_after_seconds(e.headers)
                    if delay is None:
                        delay = _BACKOFF_SECONDS * (2 ** attempt)
                    time.sleep(delay)
                    # Refresh the anchor after backoff so the next _throttle()
                    # paces against actual wake time, not entry time.
                    self._last_request_at = time.monotonic()
                    continue
                raise FirecrawlUnavailable(
                    f"Firecrawl HTTP {e.code}: {e.reason}"
                ) from e
            except (urllib.error.URLError, TimeoutError) as e:
                raise FirecrawlUnavailable(f"Firecrawl network error: {e}") from e

        raise FirecrawlUnavailable("Firecrawl rate limit exhausted after retries")

    def paper_id_lookup(
        self, paper_id: str, expected_title: str,
    ) -> dict[str, Any] | None:
        """ID-keyed metadata lookup with mandatory 0.70 title cross-check.

        This is the only path here that can carry ID-keyed weight: the id is
        an exact key, so a 404 is the index genuinely not holding it. Returns
        the projected record when the id resolves AND the title cross-check
        passes; None on a 404 miss or an ID_MISMATCH (the sibling resolvers'
        pattern — a resolvable id whose title is unrelated to the citation).

        Raises `FirecrawlUnavailable` for an id outside the accepted grammar,
        so an unsupported key can never read as a miss.
        """
        _require_supported_id(paper_id)
        data = self._get(f"/papers/{urllib.parse.quote(paper_id, safe=':')}", {})
        if data is None:
            return None  # verified 404 — the index does not hold this id
        # A 200 without a well-formed `paper` is drift, not a miss: raises.
        paper = _require_shape(data, "paper", dict)
        title = paper.get("title") or ""
        if _similarity(title, expected_title) >= _TITLE_SIMILARITY_THRESHOLD:
            return _record_to_dict(paper)
        return None  # ID_MISMATCH

    def title_search(self, title: str) -> dict[str, Any] | None:
        """Ranked title search under the #431 exact-title-or-bust gate.

        The gate carries more weight here than in the siblings. This endpoint
        is a ranked semantic index: it answers every query with its nearest
        neighbours, so a returned row is not evidence the queried work exists.
        A candidate is accepted only when it clears the 0.70 ratio AND is an
        exact normalized title match; `web:` records are dropped before
        scoring, and an exact-but-generic title (#431 §0.12.2) is not promoted
        because nothing on this path can corroborate it.

        Returns the best exact candidate, or None. A None is a COVERAGE
        observation about this index, never fabrication evidence — the caller
        must not reduce it to a `*_unmatched` signal (see the protocol doc).

        No `year` parameter: the index exposes no venue publication year, so
        the siblings' matching-year tiebreaker has no input here. Ordering
        falls back to the ratio alone.
        """
        if generic_title(title):
            return None
        data = self._get("/papers", {"query": title, "k": str(_SEARCH_K)})
        if data is None:
            return None
        results = _require_shape(data, "results", list)
        scored = []
        for cand in results:
            if not isinstance(cand, dict) or not _is_paper_record(cand):
                continue
            cand_title = cand.get("title") or ""
            sim = _similarity(cand_title, title)
            if sim < _TITLE_SIMILARITY_THRESHOLD:
                continue
            if not exact_normalized_title(title, cand_title):
                continue
            scored.append((cand, sim))
        if not scored:
            return None
        scored.sort(key=lambda cand_score: -cand_score[1])
        return _record_to_dict(scored[0][0])

    def paper_passages(
        self, paper_id: str, query: str, k: int = 4,
    ) -> list[dict[str, Any]]:
        """Retrieve the top full-text passages of one paper for a question.

        The capability no sibling resolver has: it reads inside the work
        rather than confirming the record exists. Intended use is preparing a
        human check on whether a cited paper actually contains the method,
        dataset or result a draft attributes to it.

        ADVISORY ONLY, and the boundary is not stylistic. The passages are
        retrieved external content — data, not instructions
        (`shared/ground_truth_isolation_pattern.md` §2A) — and a retrieval
        score is a lexical/semantic match, not a judgement that the claim is
        supported. This method therefore returns passages and never a verdict;
        nothing derives a verification outcome from it.

        Returns the passage list ([] when the paper is missing or carries no
        retrievable full text). Raises `FirecrawlUnavailable` per `_get`.
        """
        _require_supported_id(paper_id)
        data = self._get(
            f"/papers/{urllib.parse.quote(paper_id, safe=':')}",
            {"query": query, "k": str(k)},
        )
        if data is None:
            return []  # verified 404 — no such paper
        passages = _require_shape(data, "passages", list)
        return [p for p in passages if isinstance(p, dict)]
