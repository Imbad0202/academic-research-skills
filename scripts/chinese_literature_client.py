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

  1. doi.org RA lookup    -> https://doi.org/doiRA/<prefix>    (zero-cost routing)
  2. doi.org content-neg  -> Accept: application/vnd.citationstyles.csl+json
                             (when safely exposed, ISTIC metadata can carry the
                              Chinese title, journal, volume/issue/page)
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
  - Every applicable terminal non-decision produces a human-confirmation
    checklist item (P0-P3 priority) rather than a fabrication verdict.

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
import re
import string
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from enum import Enum
from typing import Any

# Dual-path import: see openalex_client.py comment.
try:
    from _text_similarity import _MAX_RETRIES
except ImportError:  # pragma: no cover - exercised by the package-import path
    from scripts._text_similarity import _MAX_RETRIES


_DOI_RA_BASE = "https://doi.org/doiRA/"
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
_NCBI_TOOL = "academic-research-skills"
# Bound every response before parsing it. The largest payload this standalone
# client requests is an E-utilities JSON response with retmax=5; 2 MiB leaves a
# generous margin without allowing a redirect target or broken upstream to
# stream an unbounded body into the process.
MAX_BODY_BYTES = 2 * 1024 * 1024

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
    "PUBMED_COORDINATE_CANDIDATE_UNVERIFIED",
    "PUBMED_INDEXED_BUT_COORDINATE_MISS",
    "PUBMED_COORDINATE_AMBIGUOUS",
    "INSUFFICIENT_PUBMED_COORDINATES",
    "JOURNAL_NOT_INDEXED",
    "NO_ISSN_MAPPING",
    "DOI_RA_OUT_OF_SCOPE",
    "DOI_RA_UNRESOLVED",
    "NOT_CHINESE_LITERATURE",
})

# Priority is workload ordering for the human, NOT a suspicion score.
#   P0 = the identifier is absent, or it resolves to a different title (the
#        only tier where fabrication language is permitted at all)
#   P1 = the journal IS indexed but the cited coordinates return nothing
#   P2 = the identifier resolves but the title cannot be machine-compared
#   P3 = no applicable automated source — the normal case for social-science,
#        non-core-journal, and pre-digital Chinese literature; NOT suspicious
_PRIORITY_BY_REASON = {
    "DOI_REFUTED": "P0",
    "DOI_TITLE_MISMATCH": "P0",
    "PUBMED_INDEXED_BUT_COORDINATE_MISS": "P1",
    "PUBMED_COORDINATE_AMBIGUOUS": "P1",
    "PUBMED_COORDINATE_CANDIDATE_UNVERIFIED": "P2",
    "DOI_EXISTS_TITLE_UNVERIFIABLE": "P2",
    "INSUFFICIENT_PUBMED_COORDINATES": "P3",
    "JOURNAL_NOT_INDEXED": "P3",
    "NO_ISSN_MAPPING": "P3",
    "DOI_RA_OUT_OF_SCOPE": "P3",
    "DOI_RA_UNRESOLVED": "P2",
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
    raised, never swallowed into a miss. Distinct from a 404 or Handle
    `responseCode: 100`, which are meaningful typed observations the resolver
    reports as data; only their validated combination refutes a DOI (see
    `_fetch(allow_404=True)`).
    """


def _redact_url(url: str) -> str:
    """scheme + host + path only. Error/refusal text must never carry the
    query string: it can carry api_key, which must never land in logs /
    raised-exception text. Mirrors openalex_client.py / crossref_client.py
    (#495)."""
    parsed = urllib.parse.urlsplit(url)
    # Rebuild from hostname rather than netloc so rejected userinfo is not
    # reflected into logs either. An explicit port is retained for diagnosis.
    host = parsed.hostname or ""
    try:
        port = parsed.port
    except ValueError:
        port = None
    netloc = f"{host}:{port}" if port is not None else host
    return urllib.parse.urlunsplit((parsed.scheme, netloc, parsed.path, "", ""))


def _quote_url_component(value: str, *, safe: str = "") -> str:
    """Percent-encode one URL component inside the typed failure boundary.

    JSON Schema strings can contain lone UTF-16 surrogates even though UTF-8
    cannot encode them. Treat that malformed scalar as unavailable input
    rather than leaking a raw ``UnicodeEncodeError`` from ``urllib.parse``.
    """
    try:
        return urllib.parse.quote(value, safe=safe)
    except (TypeError, UnicodeError, ValueError):
        raise ChineseLiteratureUnavailable(
            "URL component contains invalid Unicode"
        ) from None


def _require_api_url(url: str) -> None:
    """Multi-host variant of the siblings' `_require_api_url`: this client
    legitimately talks to three hosts, so the guard is an allowlist rather
    than a single-host equality check."""
    try:
        parsed = urllib.parse.urlsplit(url)
        port = parsed.port
    except ValueError:
        # `parsed.port` includes the rejected port token in its ValueError;
        # never retain that untrusted text as an exception cause.
        raise ChineseLiteratureUnavailable("Refusing malformed API URL") from None
    if (
        parsed.scheme != "https"
        or parsed.hostname not in _ALLOWED_API_HOSTS
        or parsed.netloc != parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or port is not None
    ):
        raise ChineseLiteratureUnavailable(
            f"Refusing non-allowlisted URL: {_redact_url(url)}"
        )


class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Validate the resolved destination before following every redirect.

    urllib's default handler follows Location automatically. Validating only
    the initial request would let an allowlisted DOI endpoint downgrade to
    HTTP or escape to an arbitrary host. `newurl` is the absolute URL resolved
    by urllib for this hop; the final response URL is checked independently in
    `_fetch` as defense in depth.
    """

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> urllib.request.Request | None:
        _require_api_url(newurl)
        method = req.get_method()
        if not (
            code in (301, 302, 303, 307, 308) and method in ("GET", "HEAD")
            or code in (301, 302, 303) and method == "POST"
        ):
            raise ChineseLiteratureUnavailable(
                "redirect response is not permitted for this request method"
            )
        content_headers = {"content-length", "content-type"}
        new_headers = {
            key: value for key, value in req.headers.items()
            if key.lower() not in content_headers
        }
        return urllib.request.Request(
            newurl,
            headers=new_headers,
            origin_req_host=req.origin_req_host,
            unverifiable=True,
        )

    def http_error_302(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
    ) -> Any:
        """Follow one validated redirect without stdlib's unbounded `fp.read()`.

        CPython's default handler drains every redirect body with an unbounded
        read before following it. Redirect bodies are not evidence this client
        consumes, so close the response without reading after the destination
        and loop budget have been checked.
        """
        try:
            location = headers.get("location") or headers.get("uri")
            if location is None:
                raise ChineseLiteratureUnavailable(
                    "redirect response is missing a Location header"
                )
            if not isinstance(location, str):
                raise ChineseLiteratureUnavailable(
                    "redirect response has a malformed Location header"
                )
            try:
                quoted = urllib.parse.quote(
                    location, encoding="iso-8859-1", safe=string.punctuation,
                )
                newurl = urllib.parse.urljoin(req.full_url, quoted)
            except (TypeError, UnicodeError, ValueError):
                raise ChineseLiteratureUnavailable(
                    "redirect response has a malformed Location header"
                ) from None

            _require_api_url(newurl)
            new = self.redirect_request(req, fp, code, msg, headers, newurl)
            if new is None:
                return None

            if hasattr(req, "redirect_dict"):
                visited = new.redirect_dict = req.redirect_dict
                if (
                    visited.get(newurl, 0) >= self.max_repeats
                    or len(visited) >= self.max_redirections
                ):
                    raise ChineseLiteratureUnavailable(
                        "redirect loop or budget exhausted"
                    )
            else:
                visited = new.redirect_dict = req.redirect_dict = {}
            visited[newurl] = visited.get(newurl, 0) + 1
        except ChineseLiteratureUnavailable:
            try:
                fp.close()
            except (OSError, http.client.HTTPException):
                raise ChineseLiteratureUnavailable(
                    "redirect response could not be closed"
                ) from None
            raise
        except (TypeError, UnicodeError, ValueError):
            try:
                fp.close()
            except (OSError, http.client.HTTPException):
                pass
            raise ChineseLiteratureUnavailable(
                "redirect response has a malformed Location header"
            ) from None

        try:
            fp.close()
        except (OSError, http.client.HTTPException):
            raise ChineseLiteratureUnavailable(
                "redirect response could not be closed"
            ) from None
        return self.parent.open(new, timeout=req.timeout)

    http_error_301 = http_error_303 = http_error_307 = http_error_308 = http_error_302


def _safe_urlopen(req: urllib.request.Request, timeout: float = 30) -> Any:
    """Production transport and the single hermetic-test injection point."""
    opener = urllib.request.build_opener(_SafeRedirectHandler())
    return opener.open(req, timeout=timeout)


def _entrez_quoted(value: Any, field: str) -> str:
    """Return one quoted Entrez literal or fail closed.

    URL encoding protects HTTP syntax, not Entrez's own query grammar. Quotes,
    brackets, backslashes and control characters could terminate a literal or
    introduce a new field tag, so untrusted citation fields carrying any of
    them are rejected before a request is built.
    """
    text = str(value or "").strip()
    if not text or any(
        ord(ch) < 32 or ch in {'"', "[", "]", "\\"} for ch in text
    ):
        raise ChineseLiteratureUnavailable(
            f"unsafe Entrez {field} literal"
        )
    return f'"{text}"'


def _entrez_atom(value: Any, field: str) -> str:
    """Return an unquoted volume/page atom with no Entrez grammar surface."""
    text = str(value or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+/-]*", text):
        raise ChineseLiteratureUnavailable(f"unsafe Entrez {field} atom")
    return text


def _entrez_year(value: Any) -> str:
    text = str(value or "").strip()
    if not re.fullmatch(r"[12][0-9]{3}", text):
        raise ChineseLiteratureUnavailable("unsafe Entrez publication year")
    return text


def _valid_ncbi_email(value: Any) -> bool:
    """Minimal deterministic identity check; NCBI requires a valid email."""
    return isinstance(value, str) and bool(
        re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value)
    )


def _first_page(value: Any) -> str:
    """Return the first page/e-location atom from common range separators."""
    return re.split(r"[-–—]", str(value or ""), maxsplit=1)[0].strip()


class DoiTitleState(str, Enum):
    """Closed outcome set for one DOI-keyed machine-title lookup."""

    MATCH = "match"
    MISMATCH = "mismatch"
    NOT_FOUND = "not_found"
    UNVERIFIABLE = "unverifiable"


@dataclass(frozen=True)
class DoiTitleLookupOutcome:
    """Keep evidence states distinct until orchestration assigns semantics."""

    state: DoiTitleState
    record: dict[str, Any] | None = None


def has_cjk(text: str | None) -> bool:
    """True iff the string contains a CJK Unified Ideograph."""
    return any(_CJK_LO <= ch <= _CJK_HI for ch in text or "")


def normalize_cn_title(title: str | None) -> str:
    """Chinese-aware title normalization.

    The shared `_text_similarity.exact_normalized_title` (#431) is ASCII-centric
    and, measured on real ISTIC metadata 2026-07-27, rejects three legitimate
    variants of one identical Chinese title:

      - fullwidth latin/digits (ＰｒｏＥＸＣ vs ProEXC): an explicit fullwidth-
        ASCII fold handles these; the shared normalizer does not (measured
        similarity 0.577, exact=False)
      - a trailing CJK full stop (。) and outer title wrappers (《》): not in
        `string.punctuation`, so the shared normalizer keeps them (0.981, False)
      - spaces touching Han characters: Chinese carries no word breaks, so
        these are typesetting noise; whitespace between non-CJK tokens remains
        significant (the measured Chinese/Latin variant scored 0.929, False)

    Simplified/Traditional folding is deliberately NOT done: it is lossy for
    proper nouns, and a wrong fold would manufacture a false match. The pair is
    surfaced to the human instead.
    """
    # Fold only the fullwidth ASCII compatibility block that was observed in
    # the motivating metadata. Whole-string NFKC/casefold is too broad for an
    # exact scientific-title key: it collapses e.g. 2² with 22 and Straße with
    # Strasse. U+3000 is the fullwidth/ideographic space and is removed below.
    text = "".join(
        chr(ord(ch) - 0xFEE0) if "！" <= ch <= "～" else " " if ch == "　" else ch
        for ch in (title or "")
    ).strip()

    # Only remove wrappers and terminal marks that are demonstrated typesetting
    # noise. Scientific operators and measurements remain byte-significant:
    # ER+ != ER-, CD4+ != CD4−, and 4.5% != 45%. In particular, do not return to
    # a Unicode-category-wide P*/S* deletion rule.
    wrappers = {
        ("《", "》"), ("「", "」"), ("『", "』"), ("【", "】"),
        ("“", "”"), ("‘", "’"),
    }
    # The fullwidth-ASCII fold above has already mapped `．` to `.`. A final
    # full stop is ordinary title punctuation; keep `?`/`？` because it can
    # distinguish an interrogative title from an otherwise identical one.
    terminal_marks = "。."
    while text:
        previous = text
        text = text.rstrip(terminal_marks).strip()
        if len(text) >= 2 and (text[0], text[-1]) in wrappers:
            text = text[1:-1].strip()
        if text == previous:
            break

    # Whitespace touching a Han character is ordinary Chinese typesetting
    # noise, including spaces around an embedded Latin abbreviation. Preserve
    # whitespace *between* non-CJK tokens, where deleting it can collapse
    # scientifically distinct names (for example `PD L1` versus `PDL 1`).
    # Case is likewise retained: gene/protein symbols can be case-sensitive,
    # and the measured fullwidth variant already folds to the same case without
    # requiring a broad lowercase transform.
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(
        rf"(?<=[{_CJK_LO}-{_CJK_HI}]) +| +(?=[{_CJK_LO}-{_CJK_HI}])",
        "",
        text,
    )
    return text


def _cn_titles_match(candidate: str | None, expected: str | None) -> bool:
    """Chinese-aware exact-title-or-bust (#431 discipline).

    The rule is EXACT equality after `normalize_cn_title`. This helper is used
    only after a DOI-keyed lookup, so the #431 `generic_title` veto for
    identifier-free title searches does not apply: a real DOI can legitimately
    resolve to a paper titled "Editorial". The shared fuzzy `_similarity` is
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
        if len(title) != 1 or not isinstance(title[0], str):
            raise ChineseLiteratureUnavailable("unexpected CSL title shape")
        title = title[0]
    elif title is not None and not isinstance(title, str):
        raise ChineseLiteratureUnavailable("unexpected CSL title shape")
    container = csl.get("container-title")
    if isinstance(container, list):
        if len(container) != 1 or not isinstance(container[0], str):
            raise ChineseLiteratureUnavailable("unexpected CSL container-title shape")
        container = container[0]
    elif container is not None and not isinstance(container, str):
        raise ChineseLiteratureUnavailable("unexpected CSL container-title shape")
    year = None
    issued = csl.get("issued")
    if issued is not None and not isinstance(issued, dict):
        raise ChineseLiteratureUnavailable("unexpected CSL issued shape")
    if isinstance(issued, dict):
        parts = issued.get("date-parts")
        if parts is not None and not isinstance(parts, list):
            raise ChineseLiteratureUnavailable("unexpected CSL date-parts shape")
        if isinstance(parts, list) and parts:
            if not isinstance(parts[0], list):
                raise ChineseLiteratureUnavailable("unexpected CSL date-parts shape")
            if not parts[0]:
                parts = []
        if isinstance(parts, list) and parts:
            head = parts[0][0]
            if type(head) is int and 1000 <= head <= 2999:
                year = head
            elif isinstance(head, str) and re.fullmatch(r"[12][0-9]{3}", head):
                year = int(head)
            else:
                raise ChineseLiteratureUnavailable("unexpected CSL year shape")
    author_rows = csl.get("author")
    if author_rows is None:
        author_rows = []
    elif not isinstance(author_rows, list):
        raise ChineseLiteratureUnavailable("unexpected CSL author shape")
    authors = []
    for entry in author_rows:
        if not isinstance(entry, dict):
            raise ChineseLiteratureUnavailable("unexpected CSL author entry shape")
        for key in ("given", "family"):
            if entry.get(key) is not None and not isinstance(entry.get(key), str):
                raise ChineseLiteratureUnavailable(
                    f"unexpected CSL author {key} shape"
                )
        name = " ".join(
            part for part in (entry.get("given"), entry.get("family"))
            if isinstance(part, str) and part
        ).strip()
        if name:
            authors.append(name)
    scalar_values: dict[str, str | None] = {}
    for source_key, output_key in (
        ("volume", "volume"),
        ("issue", "issue"),
        ("page", "page"),
    ):
        value = csl.get(source_key)
        if value is not None and type(value) not in (str, int):
            raise ChineseLiteratureUnavailable(
                f"unexpected CSL {source_key} shape"
            )
        scalar_values[output_key] = str(value) if value is not None else None

    metadata_doi = csl.get("DOI")
    if metadata_doi is not None and not isinstance(metadata_doi, str):
        raise ChineseLiteratureUnavailable("unexpected CSL DOI shape")
    scalar_values["doi"] = metadata_doi

    return {
        "title": title if isinstance(title, str) else None,
        "year": year,
        "container_title": container if isinstance(container, str) else None,
        **scalar_values,
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
    permitted only at P0 (an absent identifier or a DOI-title association that
    resolves to a different title); every other tier reads "pending human
    check", because mislabeling a real paper by a real author as suspected
    fabrication costs far more than missing one bad citation.
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
        ncbi_email: str | None = None,
    ) -> None:
        self._journal_map = dict(seed_journal_map())
        if journal_map:
            # User extension point: caller rows override / extend the seed.
            for key, value in journal_map.items():
                self._journal_map[normalize_cn_title(key)] = value
        self._ncbi_api_key = ncbi_api_key
        self._ncbi_email = ncbi_email
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
        it is a meaningful NOT_FOUND observation, not a degradation. A DOI CSL
        404 alone does not refute an identifier; orchestration requires an
        independent Handle absence before assigning `DOI_REFUTED`. Everything
        else degrades:

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
                # `_safe_urlopen` installs the per-hop redirect guard. The
                # response URL is checked again because injected transports,
                # alternate handlers, and future refactors must not bypass the
                # same trust boundary.
                with _safe_urlopen(req, timeout=30) as resp:
                    try:
                        final_url = resp.geturl()
                        if not isinstance(final_url, str) or not final_url:
                            raise ChineseLiteratureUnavailable(
                                f"response has no final URL for {redacted}"
                            )
                        _require_api_url(final_url)

                        response_status = getattr(resp, "status", None)
                        if type(response_status) is not int:
                            raise ChineseLiteratureUnavailable(
                                f"response has invalid status for {redacted}"
                            )
                        if response_status == 404 and allow_404:
                            return 404, b""
                        if not 200 <= response_status < 300:
                            raise ChineseLiteratureUnavailable(
                                f"HTTP {response_status} for {redacted}"
                            )

                        response_headers = getattr(resp, "headers", None)
                        if response_headers is None:
                            raise ChineseLiteratureUnavailable(
                                f"response has no headers for {redacted}"
                            )
                        content_length = response_headers.get("Content-Length")
                        if content_length is not None:
                            normalized_length = (
                                content_length.strip(" \t")
                                if isinstance(content_length, str)
                                else ""
                            )
                            if (
                                not isinstance(content_length, str)
                                or len(normalized_length) > 20
                                or not re.fullmatch(r"[0-9]+", normalized_length)
                            ):
                                raise ChineseLiteratureUnavailable(
                                    f"invalid Content-Length for {redacted}"
                                )
                            declared_length = int(normalized_length)
                            if declared_length < 0 or declared_length > MAX_BODY_BYTES:
                                raise ChineseLiteratureUnavailable(
                                    f"response body exceeds {MAX_BODY_BYTES} bytes "
                                    f"for {redacted}"
                                )

                        body = resp.read(MAX_BODY_BYTES + 1)
                        if not isinstance(body, bytes):
                            raise ChineseLiteratureUnavailable(
                                f"non-bytes response body for {redacted}"
                            )
                        if len(body) > MAX_BODY_BYTES:
                            raise ChineseLiteratureUnavailable(
                                f"response body exceeds {MAX_BODY_BYTES} bytes "
                                f"for {redacted}"
                            )
                        if (
                            content_length is not None
                            and declared_length != len(body)
                        ):
                            raise ChineseLiteratureUnavailable(
                                f"truncated response body for {redacted}"
                            )
                        return response_status, body
                    except (OSError, http.client.HTTPException):
                        # IncompleteRead inherits HTTPException, not OSError: a
                        # truncated body must degrade, never become a miss.
                        raise ChineseLiteratureUnavailable(
                            f"read failed for {redacted}"
                        ) from None
            except urllib.error.HTTPError as exc:
                try:
                    error_url = exc.geturl()
                    if not isinstance(error_url, str) or not error_url:
                        raise ChineseLiteratureUnavailable(
                            f"HTTP error has no final URL for {redacted}"
                        ) from None
                    try:
                        _require_api_url(error_url)
                    except ChineseLiteratureUnavailable:
                        raise ChineseLiteratureUnavailable(
                            f"HTTP error final URL refused for {redacted}"
                        ) from None
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
                        f"HTTP {exc.code} for {redacted}"
                    ) from None
                finally:
                    try:
                        exc.close()
                    except (OSError, http.client.HTTPException):
                        raise ChineseLiteratureUnavailable(
                            f"HTTP error response could not be closed for {redacted}"
                        ) from None
            except (urllib.error.URLError, TimeoutError):
                raise ChineseLiteratureUnavailable(
                    f"network error for {redacted}"
                ) from None
            except OSError:
                # Some alternate transports and response context managers can
                # surface a raw OSError rather than wrapping it in URLError.
                # Keep that close/transport failure inside the same typed
                # degradation boundary.
                raise ChineseLiteratureUnavailable(
                    f"network error for {redacted}"
                ) from None
            except (http.client.HTTPException, ValueError):
                # http.client.InvalidURL (an HTTPException raised when a
                # control character survives into the request line) and any
                # ValueError-shaped malformed-request rejection must degrade
                # cleanly, never crash resolve() outside its contract.
                # Identifiers are percent-encoded before reaching here, so this
                # is defense in depth, not the primary sanitizer.
                raise ChineseLiteratureUnavailable(
                    f"invalid request for {redacted}"
                ) from None

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
        except (
            json.JSONDecodeError,
            ValueError,
            UnicodeDecodeError,
            RecursionError,
        ) as exc:
            raise ChineseLiteratureUnavailable(
                f"unparseable JSON body from {_redact_url(url)}: {exc}"
            ) from exc

    # ---------- stage 1a: registration-agency routing ----------

    def ra_for(self, doi: str) -> str | None:
        """`https://doi.org/doiRA/<prefix>` -> RA name ("ISTIC" / "CNKI" /
        "Crossref" / ...), or None when the prefix is unknown to the DOI
        Foundation.

        This is pure routing metadata and NEVER produces a verdict by itself:
        an unknown prefix could equally be a typo or a very new registrant.
        """
        prefix = (doi or "").split("/", 1)[0].strip()
        if not prefix.startswith("10.") or len(prefix) <= 3:
            return None
        status, rows = self._fetch_json(
            _DOI_RA_BASE + _quote_url_component(prefix),
            accept="application/json",
            throttle_attr="_last_doi_at",
            interval=_DOI_MIN_INTERVAL,
            allow_404=True,
        )
        if status == 404:
            return None
        if (
            not isinstance(rows, list)
            or len(rows) != 1
            or not isinstance(rows[0], dict)
        ):
            raise ChineseLiteratureUnavailable(
                f"unexpected RA lookup shape for {prefix}"
            )
        row = rows[0]
        echoed_prefix = row.get("DOI")
        if not isinstance(echoed_prefix, str) or echoed_prefix != prefix:
            raise ChineseLiteratureUnavailable(
                f"RA lookup returned a mismatched DOI prefix for {prefix}"
            )
        ra = row.get("RA")
        # For an unknown prefix the endpoint answers 200 with a `status` field
        # in place of `RA` (verified 2026-07-27: /doiRA/10.99999 ->
        # [{"DOI": "10.99999", "status": "DOI does not exist"}]), so a missing
        # RA key means "no agency", but only for the endpoint's documented
        # not-found row. Any other missing/malformed RA is degradation rather
        # than an invented unknown-prefix observation.
        if ra is None and row.get("status") == "DOI does not exist":
            return None
        if (
            not isinstance(ra, str)
            or not ra
            or ra != ra.strip()
            or any(ord(ch) < 32 for ch in ra)
        ):
            raise ChineseLiteratureUnavailable(
                f"unexpected RA value for {prefix}"
            )
        return ra

    # ---------- stage 1b: ISTIC content negotiation ----------

    def doi_lookup_with_title_check(
        self, doi: str, expected_title: str,
    ) -> DoiTitleLookupOutcome:
        """ISTIC path: DOI content negotiation + mandatory title cross-check.

        The closed result distinguishes a 404, a verified mismatch, and a
        record whose title cannot be compared. Keeping those states separate is
        what prevents a 404 followed by Handle existence, or an empty cited
        title, from becoming a false mismatch verdict.

        A 200 response that is non-JSON or malformed is upstream degradation
        and raises `ChineseLiteratureUnavailable`; it is not an UNVERIFIABLE
        metadata result and cannot drive a citation verdict.
        """
        # Percent-encode the DOI (sibling discipline). safe="/" rather than
        # crossref's safe="": doi.org / Handle resolve on the path, where the
        # prefix/suffix slash must survive; crossref's API demands the fully
        # encoded form because the DOI sits in a different position there.
        status, body = self._fetch(
            _DOI_RESOLVE_BASE + _quote_url_component(doi, safe="/"),
            accept=_CSL_ACCEPT,
            throttle_attr="_last_doi_at",
            interval=_DOI_MIN_INTERVAL,
            allow_404=True,
        )
        if status == 404:
            return DoiTitleLookupOutcome(DoiTitleState.NOT_FOUND)
        try:
            csl = json.loads(body)
        except (
            json.JSONDecodeError,
            ValueError,
            UnicodeDecodeError,
            RecursionError,
        ) as exc:
            # A 200 non-JSON body can be a proxy/CDN error page. It is an
            # upstream degradation, never ordinary evidence for a human-check
            # verdict.
            raise ChineseLiteratureUnavailable(
                f"unparseable CSL body from {_redact_url(_DOI_RESOLVE_BASE + doi)}"
            ) from exc
        if not isinstance(csl, dict):
            raise ChineseLiteratureUnavailable("unexpected CSL root shape")
        record = _csl_to_dict(csl)
        metadata_doi = record.get("doi")
        if metadata_doi is None:
            # Some ISTIC CSL responses omit the redundant DOI field. The
            # request path is still DOI-keyed, so retain that key in evidence.
            record["doi"] = doi
        elif (
            not metadata_doi.strip()
            or metadata_doi.strip().lower() != doi.strip().lower()
        ):
            raise ChineseLiteratureUnavailable(
                "CSL DOI does not match the requested DOI"
            )
        else:
            record["doi"] = metadata_doi.strip()
        if (
            not normalize_cn_title(record.get("title"))
            or not normalize_cn_title(expected_title)
        ):
            return DoiTitleLookupOutcome(DoiTitleState.UNVERIFIABLE, record)
        if _cn_titles_match(record["title"], expected_title):
            return DoiTitleLookupOutcome(DoiTitleState.MATCH, record)

        # A different script is not evidence of a different work. Chinese
        # indexing services can expose an English translation/shadow title for
        # the same article, and this client has no translation oracle. Only two
        # non-empty Chinese titles are comparable strongly enough for a
        # mismatch to contribute `false`; every cross-language or romanized
        # pair remains human-verifiable evidence.
        if not has_cjk(record["title"]) or not has_cjk(expected_title):
            return DoiTitleLookupOutcome(DoiTitleState.UNVERIFIABLE, record)
        return DoiTitleLookupOutcome(DoiTitleState.MISMATCH, record)

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
            _HANDLE_API_BASE + _quote_url_component(doi, safe="/"),
            accept="application/json",
            throttle_attr="_last_doi_at",
            interval=_DOI_MIN_INTERVAL,
            allow_404=True,
        )
        if status == 404:
            return False
        code = payload.get("responseCode") if isinstance(payload, dict) else None
        if type(code) is int and code == 1:
            return True
        if type(code) is int and code == 100:
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
        return bool(self._esearch(f'{_entrez_quoted(nlm_ta, "journal")}[ta]', retmax=1))

    def pubmed_coordinate_lookup(
        self,
        *,
        nlm_ta: str,
        volume: str | None = None,
        pages: str | None = None,
        first_author: str | None = None,
        year: int | None = None,
    ) -> tuple[str, dict[str, Any] | None]:
        """Coordinate query `[ta]+[vi]+[pg]`, then `[ta]+[1au]+[dp]` fallback.

        The coordinate tuple is a deterministic candidate query rather than a
        fuzzy title match: a real journal/volume/first-page triple can return one
        record and a fabricated page can return zero (verified 2026-07-27), but
        a hit is not promoted until its DOI binds an exact Chinese title.

        Returns `(outcome, record)` where outcome is one of `"hit"` /
        `"zero_hit"` / `"ambiguous"` / `"insufficient_input"`. A multi-hit is
        `ambiguous` with no record; a missing tuple is not mislabeled as a
        search miss. We never pick one of several.
        """
        terms: list[str] = []
        journal_term = _entrez_quoted(nlm_ta, "journal")
        if volume and pages:
            first_page = _first_page(pages)
            if first_page:
                volume_term = _entrez_atom(volume, "volume")
                page_term = _entrez_atom(first_page, "first page")
                terms.append(
                    f"{journal_term}[ta] AND {volume_term}[vi] AND {page_term}[pg]"
                )
        # Volume + first page is the stronger coordinate. Author/year is used
        # only when that tuple is unavailable; it must never wash a zero-hit or
        # ambiguous page citation into a positive match.
        if not terms and first_author and year:
            author_term = _entrez_quoted(first_author, "first author")
            year_term = _entrez_year(year)
            terms.append(
                f"{journal_term}[ta] AND {author_term}[1au] AND {year_term}[dp]"
            )
        if not terms:
            return "insufficient_input", None
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
        if not self._ncbi_email or not _valid_ncbi_email(self._ncbi_email):
            raise ChineseLiteratureUnavailable(
                "NCBI E-utilities requires a valid ncbi_email"
            )
        query["tool"] = _NCBI_TOOL
        query["email"] = self._ncbi_email
        if self._ncbi_api_key:
            query["api_key"] = self._ncbi_api_key
        try:
            encoded_query = urllib.parse.urlencode(query)
        except (TypeError, UnicodeError, ValueError):
            raise ChineseLiteratureUnavailable(
                "E-utilities parameters contain invalid Unicode"
            ) from None
        return _EUTILS_BASE + endpoint + "?" + encoded_query

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
            result = payload["esearchresult"]
            ids = result["idlist"]
            count = result["count"]
        except (KeyError, TypeError) as exc:
            raise ChineseLiteratureUnavailable(
                f"unexpected esearch shape for term {term!r}"
            ) from exc
        if (
            not isinstance(result, dict)
            or not isinstance(count, str)
            or len(count) > 20
            or not re.fullmatch(r"[0-9]+", count)
            or not isinstance(ids, list)
            or any(
                not isinstance(pmid, str)
                or not re.fullmatch(r"[1-9][0-9]*", pmid)
                for pmid in ids
            )
        ):
            raise ChineseLiteratureUnavailable(
                f"unexpected esearch idlist shape for term {term!r}"
            )
        count_value = int(count)
        if (
            len(ids) != min(count_value, retmax)
            or len(set(ids)) != len(ids)
        ):
            raise ChineseLiteratureUnavailable(
                f"inconsistent esearch count/idlist for term {term!r}"
            )
        return ids

    def _esummary(self, pmid: str) -> dict[str, Any]:
        """Project one esummary record.

        NOTE (measured 2026-07-27): for a Chinese-language article PubMed's
        `title` is the ENGLISH bracketed shadow title, never the Chinese
        original. A Chinese-to-English title cross-check is therefore
        structurally impossible within PubMed; `resolve()` treats this record
        only as a candidate and follows its DOI to Chinese metadata.
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
            result = payload["result"]
            record = result[pmid]
        except (KeyError, TypeError) as exc:
            raise ChineseLiteratureUnavailable(
                f"unexpected esummary shape for pmid {pmid}"
            ) from exc
        if not isinstance(record, dict):
            raise ChineseLiteratureUnavailable(
                f"unexpected esummary record shape for pmid {pmid}"
            )
        echoed_uids = result.get("uids")
        if echoed_uids is not None and echoed_uids != [pmid]:
            raise ChineseLiteratureUnavailable(
                f"unexpected esummary uids for pmid {pmid}"
            )
        echoed_uid = record.get("uid")
        if echoed_uid is not None and (
            not isinstance(echoed_uid, str) or echoed_uid != pmid
        ):
            raise ChineseLiteratureUnavailable(
                f"unexpected esummary uid for pmid {pmid}"
            )
        scalar_fields: dict[str, str | None] = {}
        for field in ("pubdate", "title", "source", "volume", "issue", "pages", "issn"):
            value = record.get(field)
            if value is not None and not isinstance(value, str):
                raise ChineseLiteratureUnavailable(
                    f"unexpected esummary {field} shape for pmid {pmid}"
                )
            scalar_fields[field] = value

        languages = record.get("lang")
        if languages is None:
            languages = []
        elif not isinstance(languages, list) or any(
            not isinstance(language, str) for language in languages
        ):
            raise ChineseLiteratureUnavailable(
                f"unexpected esummary lang shape for pmid {pmid}"
            )

        pubdate = scalar_fields["pubdate"] or ""
        if pubdate:
            pubdate_match = re.fullmatch(
                r"([12][0-9]{3})(?:[ \t./-][\x20-\x7e]*)?",
                pubdate,
            )
            if pubdate_match is None:
                raise ChineseLiteratureUnavailable(
                    f"unexpected esummary pubdate value for pmid {pmid}"
                )
            year = int(pubdate_match.group(1))
        else:
            year = None
        doi = None
        article_ids = record.get("articleids")
        if article_ids is None:
            article_ids = []
        elif not isinstance(article_ids, list):
            raise ChineseLiteratureUnavailable(
                f"unexpected esummary articleids shape for pmid {pmid}"
            )
        for article_id in article_ids:
            if not isinstance(article_id, dict):
                raise ChineseLiteratureUnavailable(
                    f"unexpected esummary articleid entry shape for pmid {pmid}"
                )
            id_type = article_id.get("idtype")
            value = article_id.get("value")
            if not isinstance(id_type, str) or not isinstance(value, str):
                raise ChineseLiteratureUnavailable(
                    f"unexpected esummary articleid fields for pmid {pmid}"
                )
            if id_type == "doi":
                candidate = value.strip() or None
                if doi is not None and candidate is not None and candidate != doi:
                    raise ChineseLiteratureUnavailable(
                        f"conflicting esummary DOI values for pmid {pmid}"
                    )
                doi = candidate
        return {
            "pmid": pmid,
            # English shadow title — display/human-confirmation only.
            "english_title": scalar_fields["title"],
            "year": year,
            "container_title": scalar_fields["source"],
            "volume": scalar_fields["volume"],
            "issue": scalar_fields["issue"],
            "pages": scalar_fields["pages"],
            "issn": scalar_fields["issn"],
            "languages": languages,
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

        if doi:
            if ra in _CHINESE_RAS:
                return self._resolve_by_doi(entry, doi, ra, attempts)
            if ra is None:
                return self._skipped_with_checklist(
                    entry, attempts, "DOI_RA_UNRESOLVED",
                    human_action=(
                        "The DOI registration agency could not be established. "
                        "This resolver will not ignore the supplied DOI and fall "
                        "back to coordinates. Verify the DOI manually. Pending "
                        "human check."
                    ),
                )
            return self._skipped_with_checklist(
                entry, attempts, "DOI_RA_OUT_OF_SCOPE",
                human_action=(
                    f"This DOI is registered with {ra}, outside this resolver's "
                    "ISTIC/CNKI scope. Route it to the appropriate DOI resolver; "
                    "the supplied DOI was not replaced by a coordinate lookup. "
                    "Pending human check."
                ),
            )
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

        # ISTIC RA: attempt CSL-JSON within the allowlisted HTTPS boundary.
        lookup = self.doi_lookup_with_title_check(doi, expected_title)
        attempts.append({
            "stage": "content_negotiation",
            "outcome": lookup.state.value,
        })

        if lookup.state is DoiTitleState.MATCH:
            assert lookup.record is not None  # closed-state construction invariant
            return {
                "status": STATUS_MATCHED,
                "queried_by": "id",
                "reason_code": "DOI_TITLE_VERIFIED",
                "evidence": {"registration_agency": ra, **lookup.record},
                "checklist_item": None,
            }

        if lookup.state is DoiTitleState.MISMATCH:
            return {
                "status": STATUS_UNMATCHED,
                "queried_by": "id",
                "reason_code": "DOI_TITLE_MISMATCH",
                "evidence": {
                    "doi": doi,
                    "registration_agency": ra,
                    "resolved_title": (lookup.record or {}).get("title"),
                },
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

        if lookup.state is DoiTitleState.NOT_FOUND:
            # A content-negotiation 404 is only refutation evidence when the
            # independent Handle API also says absent. Some existing handles do
            # not expose a CSL representation at doi.org.
            exists = self.handle_exists(doi)
            attempts.append({
                "stage": "handle_existence",
                "outcome": "exists" if exists else "absent",
            })
            if not exists:
                return self._refuted(entry, attempts, resolve_url)

        # Either the 200 record lacks a comparable title (including an empty
        # cited title), or content negotiation returned 404 while Handle proves
        # the DOI exists. Neither state permits a mismatch/false verdict.
        return self._doi_title_unverifiable(
            entry, attempts, doi, ra, resolve_url,
            resolved_title=(lookup.record or {}).get("title"),
        )

    def _doi_title_unverifiable(
        self,
        entry: dict[str, Any],
        attempts: list[dict[str, Any]],
        doi: str,
        ra: str,
        resolve_url: str,
        *,
        resolved_title: Any = None,
    ) -> dict[str, Any]:
        evidence = {"doi": doi, "registration_agency": ra}
        if isinstance(resolved_title, str) and resolved_title:
            evidence["resolved_title"] = resolved_title
        return {
            "status": STATUS_UNMATCHED,
            "queried_by": "title",
            "reason_code": "DOI_EXISTS_TITLE_UNVERIFIABLE",
            "evidence": evidence,
            "checklist_item": _checklist_item(
                reason_code="DOI_EXISTS_TITLE_UNVERIFIABLE",
                verdict_contribution="unresolvable",
                entry=entry,
                attempts=attempts,
                human_action=(
                    "This DOI exists, but the cited and resolved titles were "
                    "not both comparable Chinese originals. Open the link and "
                    "confirm the title manually. Pending human check — this is "
                    "not a finding about the citation's validity."
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

        volume = entry.get("volume")
        pages = entry.get("pages")
        first_author = entry.get("first_author_pinyin")
        cited_year = entry.get("year")
        cited_year_number = (
            int(_entrez_year(cited_year)) if cited_year is not None else None
        )
        has_volume_page = bool(volume and pages and _first_page(pages))
        has_author_year = bool(first_author and cited_year_number)
        if not has_volume_page and not has_author_year:
            attempts.append({
                "stage": "pubmed_coordinate_input",
                "outcome": "insufficient",
            })
            return self._skipped_with_checklist(
                entry,
                attempts,
                "INSUFFICIENT_PUBMED_COORDINATES",
                human_action=(
                    "PubMed coordinate lookup needs either volume plus first "
                    "page, or first-author pinyin plus publication year. These "
                    "fields are incomplete, so no coordinate search was run. "
                    "Verify the reference by hand. Pending human check."
                ),
            )

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
            volume=volume,
            pages=pages,
            first_author=first_author,
            year=cited_year_number,
        )
        attempts.append({
            "stage": "pubmed_coordinate",
            "outcome": outcome,
            "detail": "volume_page" if has_volume_page else "author_year",
        })

        if outcome == "hit" and record is not None:
            # PubMed's title is only an English shadow title, so a coordinate
            # hit is a candidate, never a match. Structural disagreement rejects
            # even candidacy; otherwise the candidate DOI must route back to an
            # allowed Chinese RA and return a Chinese machine title that exactly
            # matches the cited title.
            record_issn = (record.get("issn") or "").strip()
            issn_conflict = bool(record_issn) and record_issn != bridged["issn"]
            cited_volume = str(volume).strip() if volume is not None else ""
            record_volume = (record.get("volume") or "").strip()
            volume_conflict = bool(cited_volume and record_volume) and (
                cited_volume != record_volume
            )
            cited_first_page = _first_page(pages)
            record_first_page = _first_page(record.get("pages"))
            page_conflict = bool(cited_first_page and record_first_page) and (
                cited_first_page != record_first_page
            )
            year_conflict = bool(
                cited_year_number and record.get("year")
                and cited_year_number != record["year"]
            )
            structural_conflicts = [
                label for label, conflict in (
                    ("journal ISSN", issn_conflict),
                    ("volume", volume_conflict),
                    ("first page", page_conflict),
                    ("year", year_conflict),
                ) if conflict
            ]
            if structural_conflicts:
                attempts.append({
                    "stage": "pubmed_candidate_verification",
                    "outcome": "structural_conflict",
                    "detail": ", ".join(structural_conflicts),
                })
                return self._pubmed_candidate_unverified(
                    entry,
                    attempts,
                    record,
                    "The PubMed coordinate candidate's "
                    + ", ".join(structural_conflicts)
                    + " disagrees with the citation.",
                )

            candidate_doi = record.get("doi")
            if not isinstance(candidate_doi, str) or not candidate_doi.strip():
                attempts.append({
                    "stage": "pubmed_candidate_verification",
                    "outcome": "no_doi",
                })
                return self._pubmed_candidate_unverified(
                    entry,
                    attempts,
                    record,
                    "The unique PubMed coordinate candidate has no DOI, so its "
                    "English shadow title cannot be bound to the cited Chinese title.",
                )
            candidate_doi = candidate_doi.strip()

            candidate_ra = self.ra_for(candidate_doi)
            attempts.append({
                "stage": "pubmed_candidate_ra",
                "outcome": candidate_ra or "unknown_prefix",
            })
            if candidate_ra == _RA_ISTIC:
                title_lookup = self.doi_lookup_with_title_check(
                    candidate_doi, entry.get("title") or "",
                )
                attempts.append({
                    "stage": "pubmed_candidate_title",
                    "outcome": title_lookup.state.value,
                })
                machine_title = (title_lookup.record or {}).get("title")
                if (
                    title_lookup.state is DoiTitleState.MATCH
                    and has_cjk(machine_title)
                    and has_cjk(entry.get("title"))
                ):
                    return {
                        "status": STATUS_MATCHED,
                        "queried_by": "title",
                        "reason_code": "PUBMED_COORDINATE_VERIFIED",
                        "evidence": {
                            **record,
                            "registration_agency": candidate_ra,
                            "doi_metadata": title_lookup.record,
                        },
                        "checklist_item": None,
                    }
                return self._pubmed_candidate_unverified(
                    entry,
                    attempts,
                    record,
                    "The PubMed candidate DOI did not yield an exactly matching "
                    "machine-readable Chinese title.",
                )

            if candidate_ra == _RA_CNKI:
                exists = self.handle_exists(candidate_doi)
                attempts.append({
                    "stage": "pubmed_candidate_handle",
                    "outcome": "exists" if exists else "absent",
                })
                detail = (
                    "The PubMed candidate DOI exists, but CNKI supplies no "
                    "key-free machine-readable Chinese title."
                    if exists else
                    "The PubMed candidate DOI could not be confirmed by Handle."
                )
                return self._pubmed_candidate_unverified(
                    entry, attempts, record, detail,
                )

            return self._pubmed_candidate_unverified(
                entry,
                attempts,
                record,
                "The PubMed candidate DOI belongs to an out-of-scope or unknown "
                "registration agency, so this client cannot bind it to a Chinese title.",
            )

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
        if has_volume_page:
            miss_description = "the cited volume/page"
            verification_term = (
                f'"{nlm_ta}"[ta] AND {volume}[vi] AND {_first_page(pages)}[pg]'
            )
        else:
            miss_description = "the cited first-author/year coordinates"
            verification_term = (
                f'"{nlm_ta}"[ta] AND "{first_author}"[1au] '
                f"AND {cited_year_number}[dp]"
            )
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
                    f"{miss_description}. PubMed indexes Chinese journals "
                    "selectively, so this may simply be an unindexed issue — "
                    "check the journal's own site. Pending human check."
                ),
                verification_urls=[
                    "https://pubmed.ncbi.nlm.nih.gov/?term="
                    + _quote_url_component(verification_term)
                ],
            ),
        }

    def _pubmed_candidate_unverified(
        self,
        entry: dict[str, Any],
        attempts: list[dict[str, Any]],
        record: dict[str, Any],
        detail: str,
    ) -> dict[str, Any]:
        """A coordinate candidate is never negative evidence about a citation."""
        verification_urls = [
            f"https://pubmed.ncbi.nlm.nih.gov/{record['pmid']}/"
        ]
        if isinstance(record.get("doi"), str) and record["doi"]:
            verification_urls.append(_DOI_RESOLVE_BASE + record["doi"])
        return {
            "status": STATUS_UNMATCHED,
            "queried_by": "title",
            "reason_code": "PUBMED_COORDINATE_CANDIDATE_UNVERIFIED",
            "evidence": record,
            "checklist_item": _checklist_item(
                reason_code="PUBMED_COORDINATE_CANDIDATE_UNVERIFIED",
                verdict_contribution="unresolvable",
                entry=entry,
                attempts=attempts,
                human_action=(
                    f"{detail} The coordinate hit remains a candidate only; "
                    "verify the original Chinese title manually. Pending human "
                    "check — this is never a false verdict."
                ),
                verification_urls=verification_urls,
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
        """`skipped` + a checklist row at the reason code's priority.

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
