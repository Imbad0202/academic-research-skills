#!/usr/bin/env python3
"""#511 Part B — hermetic transport-fixture integration test for the citation gate.

The four per-client unit suites mock at the transport boundary one client at a
time, and the citation eval replays already-reduced ``resolver_outcomes``
(scripts/run_evals.py) whose expected values were authored from the same
reducer rule — so no CI test fed realistic RAW API bodies through all four
ACTUAL client implementations into ``verify_citation``. This suite closes that
gap: checked-in redacted success/miss/error bodies per resolver
(scripts/fixtures/transport_bodies/) + a URL-dispatch fake at
``urllib.request.urlopen`` + real ``CrossrefClient`` / ``OpenAlexClient`` /
``SemanticScholarClient`` / ``ArxivClient`` instances, asserting the gate's
3-class verdict end-to-end (URL construction → dispatch → body parse → title
cross-check → C-V6(a) reduction).

Deliberately NOT a product ``--offline`` mode and NOT a replication of the
51-case citation gold set (#511 scopes both out as inflation). Three scenarios
only — one per checked-in body class:

  1. all resolvers hit by DOI/arXiv-ID   → lookup_verified "true"
  2. fabricated IDs: 404 + empty results → "false" (ID-keyed unmatched)
  3. total outage: 5xx everywhere        → "unresolvable" (all unreachable)
"""
from __future__ import annotations

import email.message
import io
import sys
import urllib.error
import urllib.parse
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

FIXTURES = REPO_ROOT / "scripts" / "fixtures" / "transport_bodies"

# Synthetic citation pinned to the fixture bodies (see transport_bodies/README.md):
# 10.5555 is the example/test DOI prefix; the arXiv ID is structurally
# impossible (month 13), so it can never collide with a real submission.
DOI = "10.5555/ars.tfx.2026.42"
ARXIV_ID = "2613.04567"
TITLE = "Hermetic Transport Fixtures for Deterministic Citation Gate Verification"
REF_SLUG = "fixture-2026-hermetic-transport"

_QUOTED_DOI = urllib.parse.quote(DOI, safe="")
_RESOLVERS = ("crossref", "openalex", "semantic_scholar", "arxiv")

# The documented select/fields values each client sends — pinned here
# INDEPENDENTLY of the clients' private _FIELDS constants, so an accidental
# field-list edit in a client fails this suite instead of auto-following.
_OPENALEX_SELECT = "id,title,authorships,publication_year,doi,primary_location"
_S2_FIELDS = "title,authors,year,externalIds,venue,publicationDate"


def _entry():
    # Production-shaped corpus entry (all five required fields, no ref_slug /
    # anchor — those live in writer prose; mirrors test_verification_gate.py).
    return {
        "citation_key": "fixture2026",
        "title": TITLE,
        "authors": [{"family": "Fixture", "given": "Ada"}],
        "year": 2026,
        "source_pointer": "kb://refs/fixture2026",
        "doi": DOI,
        "arxiv_id": ARXIV_ID,
        "obtained_via": "folder-scan",
    }


def _real_clients():
    """The four ACTUAL client implementations — the whole point of this suite.
    S2's throttle interval is zeroed through its documented injection point;
    the other three clients' pacing sleeps are neutered by the hermetic_env
    time.sleep patch."""
    from arxiv_client import ArxivClient
    from crossref_client import CrossrefClient
    from openalex_client import OpenAlexClient
    from semantic_scholar_client import SemanticScholarClient

    return {
        "crossref": CrossrefClient(),
        "openalex": OpenAlexClient(),
        "semantic_scholar": SemanticScholarClient(min_interval_seconds=0.0),
        "arxiv": ArxivClient(),
    }


@pytest.fixture
def hermetic_env(monkeypatch):
    """Deterministic URLs (no credential env leaking into query/User-Agent)
    and no real pacing sleeps."""
    for var in (
        "CROSSREF_POLITE_EMAIL",
        "OPENALEX_API_KEY",
        "OPENALEX_POLITE_EMAIL",
        "S2_API_KEY",
    ):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr("time.sleep", lambda seconds: None)


# ---------- URL-dispatch fake transport ----------


class FakeTransport:
    """urlopen stand-in dispatching on the REAL URL each client built.

    ``routes`` is an ordered list of ``(predicate, action)``; predicates get
    ``(urlsplit_result, parse_qs_dict)``. Any URL no route claims is an
    immediate test failure — the dispatch table doubles as an assertion that
    the clients contacted exactly the documented endpoints (AssertionError is
    not in any client's degradation except-list, so it propagates)."""

    def __init__(self, routes):
        self.routes = routes
        self.requests: list[str] = []

    def __call__(self, req, timeout=None):
        url = req.full_url
        self.requests.append(url)
        parsed = urllib.parse.urlsplit(url)
        # keep_blank_values + strict_parsing so a malformed addition
        # (?junk=, &extra=, a stray separator) fails routing instead of
        # being silently dropped by parse_qs and matching the exact dict.
        # An absent query string parses to {} (strict_parsing rejects "").
        query = (
            urllib.parse.parse_qs(
                parsed.query, keep_blank_values=True, strict_parsing=True)
            if parsed.query else {}
        )
        for predicate, action in self.routes:
            if predicate(parsed, query):
                return action(url)
        raise AssertionError(f"client contacted an unrouted URL: {url}")


def _serve(fixture_relpath: str):
    # io.BytesIO already satisfies everything the clients touch on the
    # response (context manager + read()); no custom response class needed.
    body = (FIXTURES / fixture_relpath).read_bytes()
    return lambda url: io.BytesIO(body)


def _http_error(code: int, reason: str, fixture_relpath: str | None = None):
    def action(url):
        body = (
            (FIXTURES / fixture_relpath).read_bytes()
            if fixture_relpath
            else b"Resource not found."
        )
        raise urllib.error.HTTPError(
            url, code, reason, email.message.Message(), io.BytesIO(body)
        )

    return action


# Endpoint predicates — one per documented request shape. Each compares
# scheme + host + path + the EXACT decoded query dict (parse_qs is
# order-insensitive), so a malformed production URL — wrong title, dropped
# rows/per-page/limit, missing select/fields — cannot silently receive the
# expected fixture and pass (codex review P2).
def _crossref_doi(p, q):
    return (
        p.scheme == "https"
        and p.netloc == "api.crossref.org"
        and p.path == f"/works/{_QUOTED_DOI}"
        and q == {}
    )


def _crossref_title_search(p, q):
    return (
        p.scheme == "https"
        and p.netloc == "api.crossref.org"
        and p.path == "/works"
        and q == {"query.title": [TITLE], "rows": ["5"]}
    )


def _openalex_doi(p, q):
    return (
        p.scheme == "https"
        and p.netloc == "api.openalex.org"
        and p.path == f"/works/doi:{_QUOTED_DOI}"
        and q == {"select": [_OPENALEX_SELECT]}
    )


def _openalex_title_search(p, q):
    return (
        p.scheme == "https"
        and p.netloc == "api.openalex.org"
        and p.path == "/works"
        and q == {"search": [TITLE], "per-page": ["5"], "select": [_OPENALEX_SELECT]}
    )


def _s2_doi(p, q):
    return (
        p.scheme == "https"
        and p.netloc == "api.semanticscholar.org"
        and p.path == f"/graph/v1/paper/DOI:{_QUOTED_DOI}"
        and q == {"fields": [_S2_FIELDS]}
    )


def _s2_title_search(p, q):
    return (
        p.scheme == "https"
        and p.netloc == "api.semanticscholar.org"
        and p.path == "/graph/v1/paper/search"
        and q == {"query": [TITLE], "limit": ["5"], "fields": [_S2_FIELDS]}
    )


def _arxiv_id(p, q):
    return (
        p.scheme == "http"  # arXiv's documented query API base is http
        and p.netloc == "export.arxiv.org"
        and p.path == "/api/query"
        and q == {"id_list": [ARXIV_ID]}
    )


def _arxiv_title_search(p, q):
    return (
        p.scheme == "http"
        and p.netloc == "export.arxiv.org"
        and p.path == "/api/query"
        and q == {"search_query": [f'ti:"{TITLE}"'], "max_results": ["5"]}
    )


# ---------- scenarios ----------


def test_hit_bodies_reduce_to_true_through_real_clients(hermetic_env, monkeypatch):
    """All four raw success bodies parse through the real clients → matched by
    ID everywhere → 'true'. One request per resolver pins the ID fast path (no
    title fallback fired)."""
    from verification_gate import verify_citation

    transport = FakeTransport([
        (_crossref_doi, _serve("crossref/doi_hit.json")),
        (_openalex_doi, _serve("openalex/doi_hit.json")),
        (_s2_doi, _serve("semantic_scholar/doi_hit.json")),
        (_arxiv_id, _serve("arxiv/id_hit.xml")),
    ])
    monkeypatch.setattr("urllib.request.urlopen", transport)

    outcome = verify_citation(
        _entry(), _real_clients(), ref_slug=REF_SLUG,
        anchor={"kind": "page", "value": "3"},
    )

    assert outcome["lookup_verified"] == "true"
    for resolver in _RESOLVERS:
        assert outcome["resolver_outcomes"][resolver] == {
            "status": "matched", "queried_by": "id", "response_summary": None,
        }, resolver
    assert outcome["citation_key"] == "fixture2026"
    assert outcome["ref_slug"] == REF_SLUG
    assert outcome["anchor_present"] is True
    assert len(transport.requests) == 4


def test_fabricated_ids_reduce_to_false_through_real_clients(hermetic_env, monkeypatch):
    """Fabricated DOI/arXiv ID: ID lookups 404 / return an empty feed, title
    fallbacks parse the real empty-result bodies → ID-keyed unmatched on every
    resolver → 'false' (C-V6(a) fabrication evidence). Two requests per
    resolver pin that the title fallback actually ran."""
    from verification_gate import verify_citation

    transport = FakeTransport([
        (_crossref_doi, _http_error(404, "Not Found")),
        (_crossref_title_search, _serve("crossref/title_search_miss.json")),
        (_openalex_doi, _http_error(404, "Not Found")),
        (_openalex_title_search, _serve("openalex/title_search_miss.json")),
        (_s2_doi, _http_error(404, "Not Found")),
        (_s2_title_search, _serve("semantic_scholar/title_search_miss.json")),
        (_arxiv_id, _serve("arxiv/empty_feed.xml")),
        (_arxiv_title_search, _serve("arxiv/empty_feed.xml")),
    ])
    monkeypatch.setattr("urllib.request.urlopen", transport)

    outcome = verify_citation(_entry(), _real_clients(), ref_slug=REF_SLUG)

    assert outcome["lookup_verified"] == "false"
    for resolver in _RESOLVERS:
        assert outcome["resolver_outcomes"][resolver] == {
            "status": "unmatched", "queried_by": "id", "response_summary": None,
        }, resolver
    assert outcome["anchor_present"] is False
    assert len(transport.requests) == 8


def test_total_outage_reduces_to_unresolvable_through_real_clients(
    hermetic_env, monkeypatch,
):
    """5xx from every API: each real client raises its *Unavailable → every
    resolver 'unreachable' → 'unresolvable', never 'verified' (the degradation
    row #511 Part A indexes for this gate). One request per resolver pins that
    5xx fails fast (no retry loop — only 429 retries)."""
    from verification_gate import verify_citation

    transport = FakeTransport([
        (_crossref_doi, _http_error(502, "Bad Gateway", "crossref/error_5xx.html")),
        (_openalex_doi, _http_error(
            500, "Internal Server Error", "openalex/error_5xx.json")),
        (_s2_doi, _http_error(
            500, "Internal Server Error", "semantic_scholar/error_5xx.json")),
        (_arxiv_id, _http_error(
            503, "Service Temporarily Unavailable", "arxiv/error_5xx.html")),
    ])
    monkeypatch.setattr("urllib.request.urlopen", transport)

    outcome = verify_citation(_entry(), _real_clients(), ref_slug=REF_SLUG)

    assert outcome["lookup_verified"] == "unresolvable"
    for resolver in _RESOLVERS:
        assert outcome["resolver_outcomes"][resolver] == {
            "status": "unreachable", "queried_by": None, "response_summary": None,
        }, resolver
    assert len(transport.requests) == 4
