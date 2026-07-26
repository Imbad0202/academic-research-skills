#!/usr/bin/env python3
"""Chinese-language literature resolver client.

Implements the lookup contract documented at
`deep-research/references/chinese_literature_api_protocol.md`.

WHY THIS EXISTS (#595): `api.crossref.org` is ONE DOI registration agency (RA),
not the DOI system. Real, resolvable Chinese-literature DOIs are registered with
ISTIC or CNKI and return 404 from the Crossref API while resolving fine through
`doi.org`. So for a Chinese citation, "not found in Crossref / OpenAlex / S2" is
weak evidence in BOTH directions, and the existing four resolvers reduce almost
every Chinese reference to `unresolvable` — indistinguishable from a fabrication.

Four legally-open, key-free upstreams. NO scraping of CNKI / Wanfang / VIP:

  1. doi.org RA lookup    -> https://doi.org/ra/<prefix>       (zero-cost routing)
  2. doi.org content-neg  -> Accept: application/vnd.citationstyles.csl+json
                             (ISTIC-registered DOIs return the CHINESE title,
                              Chinese journal name, volume/issue/page)
  3. Handle System REST   -> https://hdl.handle.net/api/handles/<doi>
                             (binary existence, incl. CNKI-registered DOIs)
  4. NCBI E-utilities     -> ISSN -> NLM TA bridge, PubMed coverage confirmation,
                             then the coordinate query `[ta]+[vi]+[pg]` for
                             DOI-less Chinese medical citations

Differences from the Crossref / OpenAlex / S2 / arXiv siblings:

  - APPLICABILITY GATE (mirrors arxiv's "not applicable != unmatched"): a
    non-Chinese citation is `skipped`, never `unmatched`, so English corpora are
    untouched by this resolver.
  - PRECISION ASYMMETRY: a refuted identifier is strong evidence (`unmatched`
    keyed by `id`), but a resolved-yet-unverifiable identifier is NEVER promoted
    to `matched`. The CNKI RA serves an HTML disambiguation page rather than
    CSL-JSON and we deliberately refuse to parse it (see `handle_exists`), so
    "the DOI exists but its title cannot be machine-checked" degrades to
    `unmatched` keyed by `title` — which the ARS reducer folds into
    `unresolvable`, never `false`.
  - CHINESE-AWARE EXACT-TITLE-OR-BUST: the shared `exact_normalized_title`
    (#431) is ASCII-centric and measurably breaks on legitimate Chinese title
    variants (fullwidth forms, CJK terminal punctuation, interior spaces —
    measured 2026-07-27, see the protocol doc). `_cn_titles_match` normalizes
    those away and then requires EXACT equality. The shared fuzzy `_similarity`
    is excluded from the rule entirely: on CJK titles it separates almost
    nothing (0.510 for an unrelated paper vs 0.577 for a fullwidth spelling of
    the identical one), so it is neither sufficient nor safe as an extra
    necessary condition.
  - Every terminal non-decision produces a human-confirmation checklist item
    (P0-P3 priority) rather than a fabrication verdict.

STATUS: standalone client (#595). It is NOT wired into
`scripts/verification_gate/`, the `resolver_outcomes` schema, the k=0..4
triangulation matrix, or `shared/contracts/degradation_registry.json`. The
status vocabulary below deliberately mirrors `citation_verification_summary.py`
so a future integration carries no SEMANTIC change — the schema-side deltas it
would still need (the four-key `resolver_outcomes` lock, the `queried_by`
description text, the `skipped` "did not run" wording) are enumerated in the
protocol doc's "Three-state semantics" section for the #593 issue-first
integration.
"""
from __future__ import annotations

import http.client
import json
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

# Dual-path import: see openalex_client.py comment.
try:
    from _text_similarity import _MAX_RETRIES, generic_title
except ImportError:  # pragma: no cover - exercised by the package-import path
    from scripts._text_similarity import _MAX_RETRIES, generic_title


_DOI_RA_BASE = "https://doi.org/ra/"
_DOI_RESOLVE_BASE = "https://doi.org/"
_HANDLE_API_BASE = "https://hdl.handle.net/api/handles/"
_EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

# Every host this client is permitted to contact. The zero-scraping red line
# (no CNKI / Wanfang / VIP) is enforced here as code, not only as prose.
_ALLOWED_API_HOSTS = frozenset({
    "doi.org",
    "hdl.handle.net",
    "eutils.ncbi.nlm.nih.gov",
})

_CSL_ACCEPT = "application/vnd.citationstyles.csl+json"

# NCBI asks for <= 3 req/s without an API key (10 with one). We pace at the
# no-key floor unconditionally; an api_key, when supplied, is passed through but
# does NOT relax the interval — staying polite is cheaper than defending a ban.
_EUTILS_MIN_INTERVAL = 0.34
# Neither doi.org nor the Handle proxy publishes a rate floor; 0.2s mirrors the
# anonymous pacing the sibling index clients use.
_DOI_MIN_INTERVAL = 0.2

# CJK Unified Ideographs (U+4E00-U+9FFF). Extension blocks are deliberately not
# scanned: the base block is sufficient for the applicability gate, and a
# narrower gate errs toward `skipped`, which is the safe direction.
_CJK_LO = "一"
_CJK_HI = "鿿"

# Registration agencies whose DOIs this resolver claims. A Crossref-registered
# Chinese DOI is left to the existing crossref resolver: re-querying it here
# would burn quota and amplify the Chinese fuzzy-match false positives the
# protocol doc measures.
_RA_ISTIC = "ISTIC"
_RA_CNKI = "CNKI"
_CHINESE_RAS = frozenset({_RA_ISTIC, _RA_CNKI})

# Status vocabulary, byte-identical to citation_verification_summary.py — the
# verbatim claim is scoped to this status/queried_by layer only; the schema-side
# deltas a gate wiring would still need are listed in the protocol doc's
# "Three-state semantics" section. Values are duplicated (not imported) to keep
# this client standalone and dependency-free at #595 scope.
STATUS_MATCHED = "matched"
STATUS_UNMATCHED = "unmatched"
STATUS_SKIPPED = "skipped"

# Closed reason-code set. Adding a member is a protocol-doc change.
REASON_CODES = frozenset({
    "DOI_REFUTED",
    "DOI_TITLE_MISMATCH",
    "DOI_TITLE_VERIFIED",
    "DOI_EXISTS_TITLE_UNVERIFIABLE",
    "PUBMED_COORDINATE_VERIFIED",
    "PUBMED_INDEXED_BUT_COORDINATE_MISS",
    "PUBMED_COORDINATE_AMBIGUOUS",
    "JOURNAL_NOT_INDEXED",
    "NO_ISSN_MAPPING",
    "NOT_CHINESE_LITERATURE",
})

# Priority is workload ordering for the human, NOT a suspicion score.
#   P0 = the identifier is refuted (the only tier where fabrication language is
#        permitted at all)
#   P1 = the journal IS indexed but the cited coordinates return nothing
#   P2 = the identifier resolves but the title cannot be machine-compared
#   P3 = no applicable automated source — the normal case for social-science,
#        non-core-journal, and pre-digital Chinese literature; NOT suspicious
_PRIORITY_BY_REASON = {
    "DOI_REFUTED": "P0",
    "DOI_TITLE_MISMATCH": "P0",
    "PUBMED_INDEXED_BUT_COORDINATE_MISS": "P1",
    "PUBMED_COORDINATE_AMBIGUOUS": "P1",
    "DOI_EXISTS_TITLE_UNVERIFIABLE": "P2",
    "JOURNAL_NOT_INDEXED": "P3",
    "NO_ISSN_MAPPING": "P3",
}

# --------------------------------------------------------------------------
# Seed journal map: 中文刊名 -> ISSN -> NLM title abbreviation.
#
# EVERY row below was verified live on 2026-07-27 against NCBI E-utilities
# (`db=nlmcatalog` by `[issn]` -> `esummary.medlineta`, then a `"<ta>"[ta]`
# PubMed search for the record count). Nothing here is guessed: an unverified
# row would silently mis-route a real citation into a P1 "indexed but not
# found" checklist row, which is exactly the false-accusation failure mode this
# resolver is built to avoid.
#
# This is a SEED, not a catalogue. The map is a documented user extension
# point: pass `journal_map=` to the constructor to merge in your own rows. An
# unmapped journal yields `NO_ISSN_MAPPING` -> `skipped` — a coverage gap in
# OUR table is never evidence about the citation. Rows must be built only from
# publicly redistributable sources (NLM Catalog, ISSN Portal); importing a
# journal list out of CNKI / Wanfang / VIP is out of bounds.
#
# Keys are `normalize_cn_title` outputs so 《中华医学杂志》 and 中华医学杂志
# hit the same row.
# --------------------------------------------------------------------------
_SEED_JOURNAL_ROWS: tuple[tuple[str, str, str, int], ...] = (
    # (Chinese journal name, ISSN, NLM title abbreviation, NLM unique ID)
    ("中华医学杂志", "0376-2491", "Zhonghua Yi Xue Za Zhi", 7511141),
    ("中华内科杂志", "0578-1426", "Zhonghua Nei Ke Za Zhi", 161387),
    ("中华外科杂志", "0529-5815", "Zhonghua Wai Ke Za Zhi", 153611),
    ("中华儿科杂志", "0578-1310", "Zhonghua Er Ke Za Zhi", 417427),
    ("中华流行病学杂志", "0254-6450", "Zhonghua Liu Xing Bing Xue Za Zhi", 8208604),
)


class ChineseLiteratureUnavailable(Exception):
    """Chinese-literature upstream degraded.

    The caller MUST map this to an `unreachable` outcome and MUST NOT interpret
    the absence of a hit as evidence about existence. fail-closed: this is
    raised, never swallowed into a miss. Distinct from a 404 / Handle
    `responseCode: 100`, which are MEANINGFUL NEGATIVES the resolver reports as
    data (see `_fetch(allow_404=True)`).
    """


def _redact_url(url: str) -> str:
    """scheme + host + path only. Error/refusal text must never carry the
    query string: it can carry api_key, which must never land in logs /
    raised-exception text. Mirrors openalex_client.py / crossref_client.py
    (#495)."""
    parsed = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))


def _require_api_url(url: str) -> None:
    """Multi-host variant of the siblings' `_require_api_url`: this client
    legitimately talks to three hosts, so the guard is an allowlist rather
    than a single-host equality check."""
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc not in _ALLOWED_API_HOSTS:
        raise ChineseLiteratureUnavailable(
            f"Refusing non-allowlisted URL: {_redact_url(url)}"
        )


class _TitleUnverifiable(Exception):
    """Internal: the identifier resolved but no machine-readable title exists.

    The CNKI RA serves an HTML disambiguation page instead of CSL-JSON, and we
    refuse to parse it (zero-scraping red line). Maps to `unmatched` keyed by
    `title` -> `unresolvable` under the ARS reducer, plus a P2 checklist row.
    NEVER `matched` (a real DOI carrying a fabricated title would slip through),
    NEVER `false` (we did not actually check anything).
    """


def has_cjk(text: str | None) -> bool:
    """True iff the string contains a CJK Unified Ideograph."""
    return any(_CJK_LO <= ch <= _CJK_HI for ch in text or "")


def normalize_cn_title(title: str | None) -> str:
    """Chinese-aware title normalization.

    The shared `_text_similarity.exact_normalized_title` (#431) is ASCII-centric
    and, measured on real ISTIC metadata 2026-07-27, rejects three legitimate
    variants of one identical Chinese title:

      - fullwidth latin/digits (ＰｒｏＥＸＣ vs ProEXC): NFKC folds these; the
        shared normalizer does not (measured similarity 0.577, exact=False)
      - CJK terminal/interior punctuation (。、，《》): not in
        `string.punctuation`, so the shared normalizer keeps it (0.981, False)
      - interior spaces: Chinese carries no word breaks, so an interior space is
        pure typesetting noise — unlike English, where it is a token boundary
        the shared normalizer must preserve (0.929, False)

    Simplified/Traditional folding is deliberately NOT done: it is lossy for
    proper nouns, and a wrong fold would manufacture a false match. The pair is
    surfaced to the human instead.
    """
    text = unicodedata.normalize("NFKC", title or "")
    stripped = []
    for ch in text:
        if ch.isspace():
            continue
        category = unicodedata.category(ch)
        # Unicode punctuation (P*) and symbols (S*) cover CJK punctuation
        # (。、，；：《》「」（）【】—) and ASCII punctuation in one rule, so the
        # normalizer cannot drift out of sync with a hand-maintained char list.
        if category.startswith(("P", "S")):
            continue
        stripped.append(ch)
    return "".join(stripped).lower()


def _cn_titles_match(candidate: str | None, expected: str | None) -> bool:
    """Chinese-aware exact-title-or-bust (#431 discipline).

    The rule is EXACT equality after `normalize_cn_title`, plus the #431
    §0.12.2 `generic_title` veto. The shared fuzzy `_similarity` is
    deliberately NOT part of it, in either direction:

      - It is not sufficient. Han characters give unrelated papers a high
        baseline overlap — two genuinely different cervical-cancer papers score
        0.510 (measured 2026-07-27), and a Crossref bibliographic query for an
        exact Chinese title returned a completely different paper as its top
        hit. Fuzzy title matching is MORE dangerous in Chinese than in English.

      - It is not usable as an extra necessary condition either, which is the
        non-obvious half. A legitimate fullwidth spelling of the identical
        title scores 0.577 — BELOW the 0.70 floor — so ANDing the ratio in
        would veto matches that exact normalization correctly established, and
        a real paper would land in the checklist at P0 next to the word
        "fabricated". That miscall costs far more than a missed bad citation,
        so the ratio is excluded. This was caught by a live smoke run against
        real ISTIC metadata, not by reasoning.

    In short: on CJK titles the 0.70 ratio separates almost nothing (0.510 for
    an unrelated paper vs 0.577 for an identical one), so it earns no place in
    the decision.
    """
    if generic_title(expected or ""):
        return False
    left, right = normalize_cn_title(candidate), normalize_cn_title(expected)
    if not left or not right:
        return False
    return left == right


def _csl_to_dict(csl: dict[str, Any]) -> dict[str, Any]:
    """Project CSL-JSON into the shape callers consume.

    Chinese-DOI metadata quirks defended against here (all observed live on
    ISTIC records, 2026-07-27):
      - `author` frequently collapses a whole name into `given` with no
        family/given split, and mixes pinyin with Han characters -> authors are
        DISPLAY-ONLY and are never a match criterion.
      - `page` frequently carries the first page only.
      - `issued` may be absent -> `year` is None and the year check is SKIPPED
        rather than failed (absence is not mismatch).
    """
    title = csl.get("title")
    if isinstance(title, list):  # some RAs emit title as a single-element list
        title = title[0] if title else None
    container = csl.get("container-title")
    if isinstance(container, list):
        container = container[0] if container else None
    year = None
    issued = csl.get("issued")
    if isinstance(issued, dict):
        parts = issued.get("date-parts")
        if isinstance(parts, list) and parts and isinstance(parts[0], list) and parts[0]:
            head = parts[0][0]
            if isinstance(head, int):
                year = head
            elif isinstance(head, str) and head.isdigit():
                year = int(head)
    authors = []
    for entry in csl.get("author") or []:
        if not isinstance(entry, dict):
            continue
        name = " ".join(
            part for part in (entry.get("given"), entry.get("family")) if part
        ).strip()
        if name:
            authors.append(name)
    return {
        "title": title if isinstance(title, str) else None,
        "year": year,
        "container_title": container if isinstance(container, str) else None,
        "volume": csl.get("volume"),
        "issue": csl.get("issue"),
        "page": csl.get("page"),
        "doi": csl.get("DOI"),
        "authors": authors,
    }


def _checklist_item(
    *,
    reason_code: str,
    verdict_contribution: str,
    entry: dict[str, Any],
    attempts: list[dict[str, Any]],
    human_action: str,
    verification_urls: list[str] | None = None,
) -> dict[str, Any]:
    """Build one human-confirmation row.

    `human_result` is initialized to None and the tool NEVER fills it: the
    judgement is the human's. Wording discipline: fabrication vocabulary is
    permitted only at P0 (a refuted identifier); every other tier reads
    "pending human check", because mislabeling a real paper by a real author as
    suspected fabrication costs far more than missing one bad citation.
    """
    if reason_code not in REASON_CODES:
        raise ValueError(f"unknown reason_code {reason_code!r}")
    return {
        "citation_key": entry.get("citation_key"),
        "priority": _PRIORITY_BY_REASON.get(reason_code, "P3"),
        "reason_code": reason_code,
        "verdict_contribution": verdict_contribution,
        "cited_as": {
            "title": entry.get("title"),
            "container_title": entry.get("container_title"),
            "year": entry.get("year"),
            "volume": entry.get("volume"),
            "issue": entry.get("issue"),
            "pages": entry.get("pages"),
            "doi": entry.get("doi"),
        },
        "attempts": attempts,
        "human_action": human_action,
        "verification_urls": verification_urls or [],
        "human_result": None,
    }


class ChineseLiteratureClient:
    """Waterfall resolver for Chinese-language citations.

    Concurrency note: rate-limit pacing is per-instance (matches the siblings).
    Two independent throttle anchors are kept because the DOI/Handle hosts and
    the NCBI host publish different pacing expectations; sharing one anchor
    would either over-throttle DOI lookups or under-throttle NCBI.
    """

    def __init__(
        self,
        journal_map: dict[str, dict[str, Any]] | None = None,
        ncbi_api_key: str | None = None,
    ) -> None:
        self._journal_map = dict(seed_journal_map())
        if journal_map:
            # User extension point: caller rows override / extend the seed.
            for key, value in journal_map.items():
                self._journal_map[normalize_cn_title(key)] = value
        self._ncbi_api_key = ncbi_api_key
        self._last_doi_at: float | None = None
        self._last_eutils_at: float | None = None
        self._user_agent = "ARS-v3.19"

    # ---------- transport ----------

    def _throttle(self, attr: str, interval: float) -> None:
        last = getattr(self, attr)
        if last is None:
            return
        # time.monotonic for elapsed measurement: NTP / manual clock adjustments
        # can make time.time run backwards (#128 §6). Aligns with
        # arxiv_client.py / crossref_client.py.
        elapsed = time.monotonic() - last
        if elapsed < interval:
            time.sleep(interval - elapsed)

    def _fetch(
        self,
        url: str,
        *,
        accept: str,
        throttle_attr: str,
        interval: float,
        allow_404: bool = False,
    ) -> tuple[int, bytes]:
        """One paced HTTP GET returning `(status, body)`.

        A 404 is returned as data ONLY when `allow_404`: on the DOI/Handle paths
        a 404 is a MEANINGFUL NEGATIVE (this identifier does not exist), not a
        degradation — treating it as one would throw away the single strongest
        signal this resolver has. Everything else degrades:

          - 429: backoff and retry up to `_MAX_RETRIES` (shared budget), then
            raise. The backoff respects the endpoint's own pacing floor so a
            retry cannot itself violate the limit the 429 is enforcing —
            same rule as arxiv_client.py.
          - 5xx: NO retry, raise immediately (fail fast; the sibling clients do
            the same and the tests pin the request count).
          - transport / timeout / truncated body / unparseable body: raise.
        """
        _require_api_url(url)
        # Every error message below uses the query-stripped URL: the query can
        # carry api_key, which must never land in logs / raised-exception
        # text (#495 discipline, mirrors crossref/openalex).
        redacted = _redact_url(url)
        headers = {"User-Agent": self._user_agent, "Accept": accept}
        req = urllib.request.Request(url, headers=headers)

        # Pace once before the first attempt; the 429 branch below re-anchors
        # after its own backoff, so a retry never double-sleeps (mirrors
        # arxiv_client.py, whose throttle also sits outside the retry loop).
        self._throttle(throttle_attr, interval)
        setattr(self, throttle_attr, time.monotonic())

        for attempt in range(_MAX_RETRIES + 1):
            try:
                # URL is allowlisted-host HTTPS after _require_api_url().
                with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310
                    try:
                        return getattr(resp, "status", 200) or 200, resp.read()
                    except (OSError, http.client.HTTPException) as exc:
                        # IncompleteRead inherits HTTPException, not OSError: a
                        # truncated body must degrade, never become a miss.
                        raise ChineseLiteratureUnavailable(
                            f"read failed for {redacted}: {exc}"
                        ) from exc
            except urllib.error.HTTPError as exc:
                if exc.code == 404 and allow_404:
                    return 404, b""
                if exc.code == 429 and attempt < _MAX_RETRIES:
                    # Sleep the endpoint's pacing floor (>= 2s), then refresh the
                    # throttle anchor so the next call paces from actual wake
                    # time rather than from before the sleep.
                    time.sleep(max(interval, 2.0) * (attempt + 1))
                    setattr(self, throttle_attr, time.monotonic())
                    continue
                raise ChineseLiteratureUnavailable(
                    f"HTTP {exc.code} for {redacted}: {exc.reason}"
                ) from exc
            except (urllib.error.URLError, TimeoutError) as exc:
                raise ChineseLiteratureUnavailable(
                    f"network error for {redacted}: {exc}"
                ) from exc
            except (http.client.HTTPException, ValueError) as exc:
                # http.client.InvalidURL (an HTTPException raised when a
                # control character survives into the request line) and any
                # ValueError-shaped malformed-request rejection must degrade
                # cleanly, never crash resolve() outside its contract.
                # Identifiers are percent-encoded before reaching here, so this
                # is defense in depth, not the primary sanitizer.
                raise ChineseLiteratureUnavailable(
                    f"invalid request for {redacted}: {exc}"
                ) from exc

        raise ChineseLiteratureUnavailable(f"rate limit exhausted for {redacted}")

    def _fetch_json(self, url: str, **kwargs: Any) -> tuple[int, Any]:
        """`_fetch` + JSON decode. An unparseable 200 body is a degradation, not
        an empty result (#331: a proxy/CDN HTML error page served with 200 must
        never be cached as a false negative)."""
        status, body = self._fetch(url, **kwargs)
        if status == 404:
            return 404, None
        try:
            return status, json.loads(body)
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError) as exc:
            raise ChineseLiteratureUnavailable(
                f"unparseable JSON body from {_redact_url(url)}: {exc}"
            ) from exc

    # ---------- stage 1a: registration-agency routing ----------

    def ra_for(self, doi: str) -> str | None:
        """`https://doi.org/ra/<prefix>` -> RA name ("ISTIC" / "CNKI" /
        "Crossref" / ...), or None when the prefix is unknown to the DOI
        Foundation.

        This is pure routing metadata and NEVER produces a verdict by itself:
        an unknown prefix could equally be a typo or a very new registrant.
        """
        prefix = (doi or "").split("/", 1)[0].strip()
        if not prefix.startswith("10.") or len(prefix) <= 3:
            return None
        status, rows = self._fetch_json(
            _DOI_RA_BASE + urllib.parse.quote(prefix, safe=""),
            accept="application/json",
            throttle_attr="_last_doi_at",
            interval=_DOI_MIN_INTERVAL,
            allow_404=True,
        )
        if status == 404 or not rows:
            return None
        if not isinstance(rows, list) or not isinstance(rows[0], dict):
            raise ChineseLiteratureUnavailable(
                f"unexpected RA lookup shape for {prefix}"
            )
        ra = rows[0].get("RA")
        # For an unknown prefix the endpoint answers 200 with a `status` field
        # in place of `RA` (verified 2026-07-27: /ra/10.99999 ->
        # [{"DOI": "10.99999", "status": "DOI does not exist"}]), so a missing
        # RA key means "no agency". Defensively also reject any RA value
        # carrying a space -- a human sentence is not an agency name.
        if not isinstance(ra, str) or not ra or " " in ra:
            return None
        return ra

    # ---------- stage 1b: ISTIC content negotiation ----------

    def doi_lookup_with_title_check(
        self, doi: str, expected_title: str,
    ) -> dict[str, Any] | None:
        """ISTIC path: DOI content negotiation + mandatory title cross-check.

        Returns the projected record when the DOI resolves AND the Chinese title
        cross-check passes. Returns None in BOTH negative cases — a 404 (the DOI
        does not exist) and an ID_MISMATCH (a real DOI carrying someone else's
        title, i.e. a chimeric citation). Both are ID-keyed unmatched, which is
        exactly the C-V6(a) shape that licenses a `false`; `resolve()`
        distinguishes them only for the checklist wording.

        Raises `_TitleUnverifiable` when the RA served a 200 that is not
        CSL-JSON (the CNKI HTML shape) or a record with no title — signalling
        "unverifiable", which must never collapse into either a match or a miss.
        """
        # Percent-encode the DOI (sibling discipline). safe="/" rather than
        # crossref's safe="": doi.org / Handle resolve on the path, where the
        # prefix/suffix slash must survive; crossref's API demands the fully
        # encoded form because the DOI sits in a different position there.
        status, body = self._fetch(
            _DOI_RESOLVE_BASE + urllib.parse.quote(doi, safe="/"),
            accept=_CSL_ACCEPT,
            throttle_attr="_last_doi_at",
            interval=_DOI_MIN_INTERVAL,
            allow_404=True,
        )
        if status == 404:
            return None  # refuted identifier
        try:
            csl = json.loads(body)
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError) as exc:
            # A well-formed 200 that is NOT CSL-JSON means the RA served an HTML
            # landing page. Not a miss, not a match — unverifiable.
            raise _TitleUnverifiable(doi) from exc
        if not isinstance(csl, dict):
            raise _TitleUnverifiable(doi)
        record = _csl_to_dict(csl)
        if not record.get("title"):
            raise _TitleUnverifiable(doi)
        if _cn_titles_match(record["title"], expected_title):
            return record
        return None  # ID_MISMATCH

    # ---------- stage 2a: Handle existence (CNKI etc.) ----------

    def handle_exists(self, doi: str) -> bool:
        """Handle System REST: `responseCode` 1 = exists, 100 = not found.

        Verified 2026-07-27: the CNKI prefixes carry NO wildcard handler, so a
        100 is a trustworthy negative — three fabricated DOIs across both ISTIC
        and CNKI prefixes all returned 100.

        This is existence ONLY. A True must NOT be promoted to `matched`: no
        title is obtainable for a CNKI-registered DOI without parsing
        chndoi.org's resolution page, and this project does not scrape. That is
        a deliberate compliance tradeoff — one extra human click beats a legal
        risk — and it is why the CNKI branch tops out at `unresolvable`.
        """
        # Percent-encode (safe="/") — see doi_lookup_with_title_check.
        status, payload = self._fetch_json(
            _HANDLE_API_BASE + urllib.parse.quote(doi, safe="/"),
            accept="application/json",
            throttle_attr="_last_doi_at",
            interval=_DOI_MIN_INTERVAL,
            allow_404=True,
        )
        if status == 404:
            return False
        code = payload.get("responseCode") if isinstance(payload, dict) else None
        if code == 1:
            return True
        if code == 100:
            return False
        # 2 (internal error), 200 (values not found), anything else: unknown
        # state, degrade rather than guess.
        raise ChineseLiteratureUnavailable(
            f"handle responseCode {code!r} for {doi}"
        )

    # ---------- stage 3: ISSN bridge + PubMed coordinate lookup ----------

    def journal_bridge(self, container_title: str | None) -> dict[str, Any] | None:
        """中文刊名 -> {issn, nlm_ta, nlm_id}. OFFLINE map only.

        Returns None when unmapped, and the caller then emits `skipped` — never
        `unmatched`. An unmapped journal is a coverage gap in OUR table, not
        evidence about the citation. Runtime expansion of the map by fetching a
        journal list from any site is forbidden: the map changes by PR review.
        """
        return self._journal_map.get(normalize_cn_title(container_title))

    def journal_is_indexed(self, nlm_ta: str) -> bool:
        """Coverage confirmation: does the journal have >= 1 PubMed record?

        NOT "is it in the NLM Catalog" — those differ in practice. 中国全科医学
        (ISSN 1007-9572) is catalogued as NLM 101299195 yet carries no MEDLINE
        abbreviation and no PubMed articles (verified 2026-07-27), so a catalog
        hit would license a meaningless coordinate miss against a journal
        PubMed never indexed.
        """
        return bool(self._esearch(f'"{nlm_ta}"[ta]', retmax=1))

    def pubmed_coordinate_lookup(
        self,
        *,
        nlm_ta: str,
        volume: str | None = None,
        pages: str | None = None,
        first_author: str | None = None,
        year: int | None = None,
    ) -> tuple[str, dict[str, Any] | None]:
        """Coordinate query `[ta]+[vi]+[pg]`, then `[ta]+[au]+[dp]` fallback.

        The coordinate tuple is a near-deterministic key rather than a fuzzy
        title match: a real journal/volume/first-page triple returns exactly one
        record and a fabricated page returns zero (verified 2026-07-27).

        Returns `(outcome, record)` where outcome is one of `"hit"` /
        `"zero_hit"` / `"ambiguous"`. A multi-hit is `ambiguous` with no record:
        we never pick one of several.
        """
        terms: list[str] = []
        if volume and pages:
            first_page = str(pages).split("-")[0].strip()
            if first_page:
                terms.append(f'"{nlm_ta}"[ta] AND {volume}[vi] AND {first_page}[pg]')
        if first_author and year:
            terms.append(f'"{nlm_ta}"[ta] AND {first_author}[au] AND {year}[dp]')
        if not terms:
            return "zero_hit", None
        outcome = "zero_hit"
        for term in terms:
            ids = self._esearch(term)
            if len(ids) == 1:
                return "hit", self._esummary(ids[0])
            if len(ids) > 1:
                outcome = "ambiguous"
        return outcome, None

    def _eutils_url(self, endpoint: str, params: dict[str, str]) -> str:
        query = dict(params)
        if self._ncbi_api_key:
            query["api_key"] = self._ncbi_api_key
        return _EUTILS_BASE + endpoint + "?" + urllib.parse.urlencode(query)

    def _esearch(self, term: str, retmax: int = 5) -> list[str]:
        url = self._eutils_url(
            "esearch.fcgi",
            {"db": "pubmed", "retmode": "json", "retmax": str(retmax), "term": term},
        )
        _status, payload = self._fetch_json(
            url,
            accept="application/json",
            throttle_attr="_last_eutils_at",
            interval=_EUTILS_MIN_INTERVAL,
        )
        try:
            ids = payload["esearchresult"]["idlist"]
        except (KeyError, TypeError) as exc:
            raise ChineseLiteratureUnavailable(
                f"unexpected esearch shape for term {term!r}"
            ) from exc
        if not isinstance(ids, list):
            raise ChineseLiteratureUnavailable(
                f"unexpected esearch idlist shape for term {term!r}"
            )
        return [str(pmid) for pmid in ids]

    def _esummary(self, pmid: str) -> dict[str, Any]:
        """Project one esummary record.

        NOTE (measured 2026-07-27): for a Chinese-language article PubMed's
        `title` is the ENGLISH bracketed shadow title, never the Chinese
        original. A Chinese-to-English title cross-check is therefore
        structurally impossible on this branch — see `resolve()` for what is
        checked instead.
        """
        url = self._eutils_url(
            "esummary.fcgi", {"db": "pubmed", "retmode": "json", "id": pmid},
        )
        _status, payload = self._fetch_json(
            url,
            accept="application/json",
            throttle_attr="_last_eutils_at",
            interval=_EUTILS_MIN_INTERVAL,
        )
        try:
            record = payload["result"][pmid]
        except (KeyError, TypeError) as exc:
            raise ChineseLiteratureUnavailable(
                f"unexpected esummary shape for pmid {pmid}"
            ) from exc
        pubdate = str(record.get("pubdate") or "")
        year = int(pubdate[:4]) if pubdate[:4].isdigit() else None
        doi = None
        for article_id in record.get("articleids") or []:
            if isinstance(article_id, dict) and article_id.get("idtype") == "doi":
                doi = article_id.get("value")
        return {
            "pmid": pmid,
            # English shadow title — display/human-confirmation only.
            "english_title": record.get("title"),
            "year": year,
            "container_title": record.get("source"),
            "volume": record.get("volume"),
            "issue": record.get("issue"),
            "pages": record.get("pages"),
            "issn": record.get("issn"),
            "languages": record.get("lang") or [],
            "doi": doi,
        }

    # ---------- stage 0 + orchestration ----------

    def is_applicable(self, entry: dict[str, Any], ra: str | None = None) -> bool:
        """Applicability gate (mirrors `_run_arxiv`'s skip semantics).

        A citation is in scope when any of its title / journal name / language
        field is Chinese, or when a caller has ALREADY established that its DOI
        belongs to a Chinese RA and passes that in. Everything else is `skipped`
        with `queried_by=None`, so an English corpus's verdicts are byte-
        unchanged by this resolver's existence.

        `resolve()` deliberately calls this WITHOUT `ra`: see the comment there
        for why establishing the RA first would cost one request per English
        reference.
        """
        if ra in _CHINESE_RAS:
            return True
        language = str(entry.get("language") or "").lower()
        if language in {"zh", "zh-cn", "zh-tw", "chi", "chinese"}:
            return True
        return has_cjk(entry.get("title")) or has_cjk(entry.get("container_title"))

    def resolve(self, entry: dict[str, Any]) -> dict[str, Any]:
        """Run the waterfall for one citation and return a structured result.

        Return shape::

            {"status": "matched"|"unmatched"|"skipped",
             "queried_by": "id"|"title"|None,
             "reason_code": <closed set>,
             "evidence": {...} | None,
             "checklist_item": {...} | None}

        `status`/`queried_by` use the `citation_verification_summary.py`
        vocabulary verbatim — at the semantic layer; the schema-side deltas a
        gate wiring would still need are in the protocol doc. There is no
        `unreachable` return value BY DESIGN: degradation raises
        `ChineseLiteratureUnavailable` and the CALLER decides, so a network
        outage can never be silently rendered as a lookup result.

        Asymmetry, restated because it is the whole point: only a refuted or
        title-mismatched IDENTIFIER returns `queried_by="id"` (the shape the ARS
        reducer turns into `false`). Every PubMed and CNKI outcome returns
        `queried_by="title"` at most, which reduces to `unresolvable`.
        """
        # Stage 0 FIRST, on local signals only: an English citation must cost
        # ZERO requests. Deciding applicability from the RA would mean one
        # doi.org round-trip per English reference in every bibliography — the
        # exact waste the applicability gate exists to prevent. The price is
        # that a Chinese work cited with a fully romanized title, no CJK
        # anywhere and no language field is `skipped`; that is recorded as a
        # known non-catch in the protocol doc rather than paid for by every
        # English corpus.
        if not self.is_applicable(entry):
            return {
                "status": STATUS_SKIPPED,
                "queried_by": None,
                "reason_code": "NOT_CHINESE_LITERATURE",
                "evidence": None,
                "checklist_item": None,
            }

        doi = (entry.get("doi") or "").strip()
        attempts: list[dict[str, Any]] = []

        ra = None
        if doi:
            ra = self.ra_for(doi)
            attempts.append({"stage": "ra_lookup", "outcome": ra or "unknown_prefix"})

        if doi and ra in _CHINESE_RAS:
            return self._resolve_by_doi(entry, doi, ra, attempts)
        return self._resolve_by_coordinates(entry, attempts)

    def _resolve_by_doi(
        self,
        entry: dict[str, Any],
        doi: str,
        ra: str,
        attempts: list[dict[str, Any]],
    ) -> dict[str, Any]:
        expected_title = entry.get("title") or ""
        # Display-only (checklist verification_urls): kept human-readable
        # unencoded on purpose; the network call sites do their own encoding.
        resolve_url = _DOI_RESOLVE_BASE + doi

        if ra == _RA_CNKI:
            # CNKI RA: existence only. Content negotiation would return an HTML
            # disambiguation page and parsing it is out of bounds.
            exists = self.handle_exists(doi)
            attempts.append(
                {"stage": "handle_existence", "outcome": "exists" if exists else "absent"}
            )
            if not exists:
                return self._refuted(entry, attempts, resolve_url)
            return {
                "status": STATUS_UNMATCHED,
                "queried_by": "title",
                "reason_code": "DOI_EXISTS_TITLE_UNVERIFIABLE",
                "evidence": {"doi": doi, "registration_agency": ra},
                "checklist_item": _checklist_item(
                    reason_code="DOI_EXISTS_TITLE_UNVERIFIABLE",
                    verdict_contribution="unresolvable",
                    entry=entry,
                    attempts=attempts,
                    human_action=(
                        "This DOI resolves, but its registration agency serves no "
                        "machine-readable title. Open the link and confirm the "
                        "title matches the citation. Pending human check — this "
                        "is not a finding about the citation's validity."
                    ),
                    verification_urls=[resolve_url],
                ),
            }

        # ISTIC RA: content negotiation returns CSL-JSON with the Chinese title.
        try:
            record = self.doi_lookup_with_title_check(doi, expected_title)
        except _TitleUnverifiable:
            attempts.append({"stage": "content_negotiation", "outcome": "no_title"})
            return {
                "status": STATUS_UNMATCHED,
                "queried_by": "title",
                "reason_code": "DOI_EXISTS_TITLE_UNVERIFIABLE",
                "evidence": {"doi": doi, "registration_agency": ra},
                "checklist_item": _checklist_item(
                    reason_code="DOI_EXISTS_TITLE_UNVERIFIABLE",
                    verdict_contribution="unresolvable",
                    entry=entry,
                    attempts=attempts,
                    human_action=(
                        "This DOI resolved but returned no machine-readable "
                        "title. Open the link and confirm the title matches. "
                        "Pending human check."
                    ),
                    verification_urls=[resolve_url],
                ),
            }

        if record is not None:
            attempts.append({"stage": "content_negotiation", "outcome": "title_verified"})
            return {
                "status": STATUS_MATCHED,
                "queried_by": "id",
                "reason_code": "DOI_TITLE_VERIFIED",
                "evidence": {"registration_agency": ra, **record},
                "checklist_item": None,
            }

        # None means either "the DOI does not exist" or "it exists with a
        # different title". Both are ID-keyed unmatched; the Handle probe only
        # decides which sentence the human reads.
        exists = self.handle_exists(doi)
        attempts.append(
            {"stage": "handle_existence", "outcome": "exists" if exists else "absent"}
        )
        if not exists:
            return self._refuted(entry, attempts, resolve_url)
        return {
            "status": STATUS_UNMATCHED,
            "queried_by": "id",
            "reason_code": "DOI_TITLE_MISMATCH",
            "evidence": {"doi": doi, "registration_agency": ra},
            "checklist_item": _checklist_item(
                reason_code="DOI_TITLE_MISMATCH",
                verdict_contribution="false",
                entry=entry,
                attempts=attempts,
                human_action=(
                    "This DOI resolves to a DIFFERENT title than the one cited "
                    "(a chimeric citation pattern). Verify the identifier "
                    "against the source and correct or remove the reference."
                ),
                verification_urls=[resolve_url],
            ),
        }

    def _refuted(
        self,
        entry: dict[str, Any],
        attempts: list[dict[str, Any]],
        resolve_url: str,
    ) -> dict[str, Any]:
        """The identifier does not exist anywhere in the global DOI system."""
        return {
            "status": STATUS_UNMATCHED,
            "queried_by": "id",
            "reason_code": "DOI_REFUTED",
            "evidence": {"doi": entry.get("doi")},
            "checklist_item": _checklist_item(
                reason_code="DOI_REFUTED",
                verdict_contribution="false",
                entry=entry,
                attempts=attempts,
                human_action=(
                    "This DOI does not exist in the global DOI system (Handle "
                    "responseCode 100 and no content negotiation). There is no "
                    "wildcard catch-all on these prefixes, so this is positive "
                    "evidence the identifier was fabricated or mistyped. "
                    "Verify against the original journal, correct, or remove."
                ),
                verification_urls=[resolve_url],
            ),
        }

    def _resolve_by_coordinates(
        self, entry: dict[str, Any], attempts: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """No Chinese DOI: journal -> ISSN -> NLM TA -> PubMed coordinates."""
        container = entry.get("container_title")
        bridged = self.journal_bridge(container)
        if bridged is None:
            attempts.append({"stage": "issn_bridge", "outcome": "unmapped"})
            return self._skipped_with_checklist(
                entry, attempts, "NO_ISSN_MAPPING",
                human_action=(
                    "This journal is not in the ISSN/NLM bridge table, so no "
                    "automated source applies. Verify the reference by hand. "
                    "Pending human check — an unmapped journal says nothing "
                    "about the citation."
                ),
            )
        nlm_ta = bridged["nlm_ta"]
        attempts.append({
            "stage": "issn_bridge",
            "outcome": "mapped",
            "detail": f"{bridged['issn']} -> {nlm_ta} (NLM {bridged['nlm_id']})",
        })

        if not self.journal_is_indexed(nlm_ta):
            attempts.append({"stage": "pubmed_coverage", "outcome": "not_indexed"})
            return self._skipped_with_checklist(
                entry, attempts, "JOURNAL_NOT_INDEXED",
                human_action=(
                    "This journal has no PubMed records, so a coordinate miss "
                    "would carry no information. Verify by hand. Pending human "
                    "check."
                ),
            )
        attempts.append({"stage": "pubmed_coverage", "outcome": "indexed"})

        outcome, record = self.pubmed_coordinate_lookup(
            nlm_ta=nlm_ta,
            volume=entry.get("volume"),
            pages=entry.get("pages"),
            first_author=entry.get("first_author_pinyin"),
            year=entry.get("year"),
        )
        attempts.append({"stage": "pubmed_coordinate", "outcome": outcome})

        if outcome == "hit" and record is not None:
            cited_year = entry.get("year")
            # The Chinese title CANNOT be compared here: PubMed stores the
            # English bracketed shadow title for Chinese-language articles
            # (measured 2026-07-27). So the corroboration is structural —
            # the ISSN the record echoes must be the ISSN we bridged through,
            # and the year must agree — and the English shadow title is carried
            # into the evidence for the human to eyeball. A DISAGREEMENT on
            # either demotes; an ABSENT value on either side does not, because
            # absence is not mismatch.
            record_issn = (record.get("issn") or "").strip()
            issn_conflict = bool(record_issn) and record_issn != bridged["issn"]
            year_conflict = bool(
                cited_year and record.get("year")
                and int(cited_year) != record["year"]
            )
            if issn_conflict or year_conflict:
                return {
                    "status": STATUS_UNMATCHED,
                    "queried_by": "title",
                    "reason_code": "PUBMED_INDEXED_BUT_COORDINATE_MISS",
                    "evidence": record,
                    "checklist_item": _checklist_item(
                        reason_code="PUBMED_INDEXED_BUT_COORDINATE_MISS",
                        verdict_contribution="unresolvable",
                        entry=entry,
                        attempts=attempts,
                        human_action=(
                            "A record exists at these journal/volume/page "
                            "coordinates, but its "
                            + ("journal ISSN" if issn_conflict else "year")
                            + " disagrees with the citation. Check whether the "
                            "citation details or the journal mapping are wrong. "
                            "Pending human check."
                        ),
                        verification_urls=[
                            f"https://pubmed.ncbi.nlm.nih.gov/{record['pmid']}/"
                        ],
                    ),
                }
            return {
                "status": STATUS_MATCHED,
                "queried_by": "title",
                "reason_code": "PUBMED_COORDINATE_VERIFIED",
                "evidence": record,
                "checklist_item": None,
            }

        if outcome == "ambiguous":
            return {
                "status": STATUS_UNMATCHED,
                "queried_by": "title",
                "reason_code": "PUBMED_COORDINATE_AMBIGUOUS",
                "evidence": None,
                "checklist_item": _checklist_item(
                    reason_code="PUBMED_COORDINATE_AMBIGUOUS",
                    verdict_contribution="unresolvable",
                    entry=entry,
                    attempts=attempts,
                    human_action=(
                        "Several PubMed records share these coordinates, so no "
                        "single record can be attributed. Pending human check."
                    ),
                ),
            }

        # Coverage confirmed, coordinates return nothing. This deliberately does
        # NOT escalate to `false`: (1) the journal-name -> NLM TA bridge is
        # heuristic and a wrong row would condemn a real paper; (2) PubMed
        # indexes Chinese journals selectively, so "the journal is indexed" does
        # not mean "this volume is indexed"; (3) C-V6(a) defines `false` as
        # ID-keyed unmatched and a coordinate tuple is not an identifier.
        # The strength goes into the P1 priority, not into the verdict.
        return {
            "status": STATUS_UNMATCHED,
            "queried_by": "title",
            "reason_code": "PUBMED_INDEXED_BUT_COORDINATE_MISS",
            "evidence": None,
            "checklist_item": _checklist_item(
                reason_code="PUBMED_INDEXED_BUT_COORDINATE_MISS",
                verdict_contribution="unresolvable",
                entry=entry,
                attempts=attempts,
                human_action=(
                    "This journal IS indexed in PubMed, but no record exists at "
                    "the cited volume/page. PubMed indexes Chinese journals "
                    "selectively, so this may simply be an unindexed issue — "
                    "check the journal's own site by volume and page. Pending "
                    "human check."
                ),
                verification_urls=[
                    "https://pubmed.ncbi.nlm.nih.gov/?term="
                    + urllib.parse.quote(f'"{nlm_ta}"[ta] AND {entry.get("volume")}[vi]')
                ],
            ),
        }

    def _skipped_with_checklist(
        self,
        entry: dict[str, Any],
        attempts: list[dict[str, Any]],
        reason_code: str,
        *,
        human_action: str,
    ) -> dict[str, Any]:
        """`skipped` + a P3 checklist row.

        `skipped` is not silence: the row is the whole point of this resolver —
        it turns "nobody ever actually checked this reference" from an invisible
        default into a visible item somebody has to sign off on.
        """
        return {
            "status": STATUS_SKIPPED,
            "queried_by": None,
            "reason_code": reason_code,
            "evidence": None,
            "checklist_item": _checklist_item(
                reason_code=reason_code,
                verdict_contribution="unresolvable",
                entry=entry,
                attempts=attempts,
                human_action=human_action,
            ),
        }


def seed_journal_map() -> dict[str, dict[str, Any]]:
    """The verified seed 中文刊名 -> ISSN/NLM-TA rows, keyed by normalized name.

    Every row was confirmed live against NCBI on 2026-07-27 (see
    `_SEED_JOURNAL_ROWS`). Extend it by passing `journal_map=` to the client
    rather than by editing this function in a fork, and only from publicly
    redistributable sources.
    """
    return {
        normalize_cn_title(name): {
            "issn": issn,
            "nlm_ta": nlm_ta,
            "nlm_id": str(nlm_id),
            "display_name": name,
        }
        for name, issn, nlm_ta, nlm_id in _SEED_JOURNAL_ROWS
    }
