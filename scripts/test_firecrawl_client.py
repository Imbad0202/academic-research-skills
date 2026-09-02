#!/usr/bin/env python3
"""Tests for the Firecrawl research-index client.

Per `deep-research/references/firecrawl_api_protocol.md`. Structure mirrors
`test_openalex_client.py` / `test_arxiv_client.py` (per-client unit suite,
inline synthetic bodies, faked socket).

ZERO live network. The protocol doc's live examples are the record of a manual
verification; nothing here contacts `api.firecrawl.dev`.

The four behaviors that are NOT shared with the sibling resolvers, and that
carry the most weight, are pinned here: the exact-title gate over a ranked
semantic index, `web:` non-paper records being dropped, an unsupported id
raising instead of missing, and `Retry-After` being honored on 429.
"""
from __future__ import annotations

import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest


# The client sends an Authorization header, so it routes through a
# redirect-refusing opener rather than bare urllib.request.urlopen
# (see _RefuseRedirects). Patch the opener the client actually uses.
_OPEN_TARGET = "firecrawl_client._OPENER.open"


def _mock_resp(payload: dict) -> MagicMock:
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(payload).encode("utf-8")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)
    return mock_response


def _raw_resp(body: bytes) -> MagicMock:
    mock_response = MagicMock()
    mock_response.read.return_value = body
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)
    return mock_response


def _search(*records: dict) -> dict:
    return {"success": True, "partial": False, "results": list(records)}


def _paper(title: str, paper_id: str = "8319239866974784291",
           primary_id: str = "arxiv:1706.03762") -> dict:
    return {
        "paperId": paper_id,
        "primaryId": primary_id,
        "ids": {"arxiv": ["1706.03762"]},
        "title": title,
        "abstract": "Synthetic abstract for the hermetic fixture set.",
    }


def _http_error(code: int, msg: str, hdrs=None) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        url="https://api.firecrawl.dev/v2/search/research/papers",
        code=code,
        msg=msg,
        hdrs=hdrs if hdrs is not None else {},
        fp=None,
    )


# --------------------------------------------------------------------------
# ID-keyed lookup
# --------------------------------------------------------------------------

def test_paper_id_lookup_with_matching_title():
    """ID hit whose title clears the 0.70 cross-check returns the record."""
    from firecrawl_client import FirecrawlResearchClient

    body = {"success": True, "paper": _paper("Attention Is All You Need")}
    with patch(_OPEN_TARGET, return_value=_mock_resp(body)):
        client = FirecrawlResearchClient()
        result = client.paper_id_lookup(
            "arxiv:1706.03762", "Attention Is All You Need",
        )

    assert result is not None
    assert result["title"] == "Attention Is All You Need"
    assert result["primaryId"] == "arxiv:1706.03762"


def test_paper_id_lookup_id_mismatch_returns_none():
    """A resolvable id whose title is unrelated to the citation is
    ID_MISMATCH → None (the sibling resolvers' pattern)."""
    from firecrawl_client import FirecrawlResearchClient

    body = {"success": True, "paper": _paper("Tenure and the University Reward Structure")}
    with patch(_OPEN_TARGET, return_value=_mock_resp(body)):
        client = FirecrawlResearchClient()
        result = client.paper_id_lookup(
            "arxiv:1706.03762", "Attention Is All You Need",
        )

    assert result is None


def test_paper_id_lookup_404_is_miss_not_unavailable():
    """404 is the path-keyed endpoint's miss shape → None, never a
    degradation."""
    from firecrawl_client import FirecrawlResearchClient

    with patch(_OPEN_TARGET,
               side_effect=_http_error(404, "Not Found")):
        client = FirecrawlResearchClient()
        result = client.paper_id_lookup("arxiv:9999.99999", "Anything")

    assert result is None


def test_404_html_body_is_still_a_miss():
    """An id that leaves the route answers 404 with an HTML body. The body is
    never read, so a non-JSON 404 must not surface as a parse degradation."""
    from firecrawl_client import FirecrawlResearchClient

    err = _http_error(404, "Not Found")
    with patch(_OPEN_TARGET, side_effect=err):
        client = FirecrawlResearchClient()
        # A numeric id is in-grammar; the 404 path is what is under test.
        assert client.paper_id_lookup("123456789", "Anything") is None


@pytest.mark.parametrize("paper_id", [
    "doi:10.1038/nature14539",   # DOI: the `/` leaves the route
    "10.1038/nature14539",       # bare DOI
    "",                          # empty
    "arxiv:",                    # namespace with no id
    "openalex:W123",             # namespace this index does not key on
])
def test_unsupported_id_raises_never_misses(paper_id):
    """The load-bearing guard: an unsupported key must RAISE, so it can never
    be read as `the index does not hold this work` (absent != false, #331)."""
    from firecrawl_client import FirecrawlResearchClient, FirecrawlUnavailable

    client = FirecrawlResearchClient()
    # No urlopen patch: the guard must fire before any request is attempted.
    with patch(_OPEN_TARGET,
               side_effect=AssertionError("must not request")):
        with pytest.raises(FirecrawlUnavailable):
            client.paper_id_lookup(paper_id, "Deep learning")


@pytest.mark.parametrize("paper_id", [
    "8319239866974784291",   # canonical numeric paperId
    "arxiv:1706.03762",
    "arxiv:1706.03762v5",    # version suffix
    "pmid:25646877",
    "pmcid:PMC9243840",
])
def test_supported_id_forms_accepted(paper_id):
    """Every id form verified live against the endpoint stays in-grammar."""
    from firecrawl_client import FirecrawlResearchClient

    body = {"success": True, "paper": _paper("Attention Is All You Need")}
    with patch(_OPEN_TARGET, return_value=_mock_resp(body)):
        client = FirecrawlResearchClient()
        assert client.paper_id_lookup(paper_id, "Attention Is All You Need")


def test_paper_id_colon_is_not_percent_encoded():
    """The namespace separator must stay a literal `:` in the path, or the
    endpoint cannot route the id."""
    from firecrawl_client import FirecrawlResearchClient

    seen = []

    def capture(req, *args, **kwargs):
        seen.append(req.full_url)
        return _mock_resp({"success": True, "paper": _paper("X")})

    with patch(_OPEN_TARGET, side_effect=capture):
        client = FirecrawlResearchClient()
        client.paper_id_lookup("arxiv:1706.03762", "X")

    assert "papers/arxiv:1706.03762" in seen[0]
    assert "%3A" not in seen[0]


# --------------------------------------------------------------------------
# Ranked title search under the exact-title-or-bust gate
# --------------------------------------------------------------------------

def test_title_search_exact_match_accepted():
    """An exact normalized title clearing 0.70 is accepted."""
    from firecrawl_client import FirecrawlResearchClient

    body = _search(_paper("Attention Is All You Need"))
    with patch(_OPEN_TARGET, return_value=_mock_resp(body)):
        client = FirecrawlResearchClient()
        result = client.title_search("Attention is all you need")

    assert result is not None
    assert result["title"] == "Attention Is All You Need"


def test_title_search_rejects_near_miss_nearest_neighbour():
    """The behavior that makes this index safe to query: a ranked semantic
    endpoint answers a fabricated title with real nearest neighbours, and the
    #431 exact-title gate must reject every one of them."""
    from firecrawl_client import FirecrawlResearchClient

    # Shape of a real measured response to a fabricated query (protocol doc).
    body = _search(
        _paper("Tenure and the university reward structure.", primary_id="pmid:2928145"),
        _paper("Tenure and research trajectories.", primary_id="pmcid:PMC12318195"),
    )
    with patch(_OPEN_TARGET, return_value=_mock_resp(body)):
        client = FirecrawlResearchClient()
        result = client.title_search(
            "Quantum Entanglement Effects on Higher Education Faculty Tenure Decisions",
        )

    assert result is None


def test_title_search_rejects_high_ratio_non_exact_title():
    """A high ratio is not sufficient: a distinct related work (different
    subtitle) matches under no normalization and stays a non-match."""
    from firecrawl_client import FirecrawlResearchClient

    body = _search(_paper("Attention Is All You Need, Part II"))
    with patch(_OPEN_TARGET, return_value=_mock_resp(body)):
        client = FirecrawlResearchClient()
        result = client.title_search("Attention Is All You Need")

    assert result is None


def test_title_search_drops_web_records():
    """The index is not papers-only. A `web:` record shares the paper response
    shape and must never be offered as a bibliographic record — even when its
    title matches exactly."""
    from firecrawl_client import FirecrawlResearchClient

    body = _search({
        "paperId": "web:https://www.merriam-webster.com/dictionary/test",
        "primaryId": "web:https://www.merriam-webster.com/dictionary/test",
        "ids": {"web": ["https://www.merriam-webster.com/dictionary/test"]},
        "title": "Attention Is All You Need",
    })
    with patch(_OPEN_TARGET, return_value=_mock_resp(body)):
        client = FirecrawlResearchClient()
        result = client.title_search("Attention Is All You Need")

    assert result is None


def test_title_search_prefers_paper_over_web_record():
    """With both present, the paper record is the one returned."""
    from firecrawl_client import FirecrawlResearchClient

    body = _search(
        {
            "paperId": "web:https://example.org/page",
            "primaryId": "web:https://example.org/page",
            "title": "Attention Is All You Need",
        },
        _paper("Attention Is All You Need"),
    )
    with patch(_OPEN_TARGET, return_value=_mock_resp(body)):
        client = FirecrawlResearchClient()
        result = client.title_search("Attention Is All You Need")

    assert result is not None
    assert result["primaryId"] == "arxiv:1706.03762"


def test_title_search_drops_id_less_record():
    """Without an id there is nothing to key a bibliographic record on, so an
    id-less row is not promoted even on an exact title match."""
    from firecrawl_client import FirecrawlResearchClient

    body = _search({"title": "Attention Is All You Need"})
    with patch(_OPEN_TARGET, return_value=_mock_resp(body)):
        client = FirecrawlResearchClient()
        assert client.title_search("Attention Is All You Need") is None


def test_title_search_generic_title_not_promoted():
    """#431 §0.12.2: nothing on the title path can corroborate a bare generic
    title, so it is never promoted."""
    from firecrawl_client import FirecrawlResearchClient

    with patch(_OPEN_TARGET,
               side_effect=AssertionError("must not request")):
        client = FirecrawlResearchClient()
        assert client.title_search("Editorial") is None


def test_title_search_empty_results_returns_none():
    from firecrawl_client import FirecrawlResearchClient

    with patch(_OPEN_TARGET, return_value=_mock_resp(_search())):
        client = FirecrawlResearchClient()
        assert client.title_search("Attention Is All You Need") is None


def test_title_search_sends_bounded_k():
    """The 5-candidate window mirrors the siblings; the endpoint honors far
    larger `k`, which past the exact gate only adds nearest neighbours."""
    from firecrawl_client import FirecrawlResearchClient

    seen = []

    def capture(req, *args, **kwargs):
        seen.append(req.full_url)
        return _mock_resp(_search())

    with patch(_OPEN_TARGET, side_effect=capture):
        client = FirecrawlResearchClient()
        client.title_search("Attention Is All You Need")

    assert "k=5" in seen[0]


# --------------------------------------------------------------------------
# Passages (advisory)
# --------------------------------------------------------------------------

def test_paper_passages_returns_passages():
    from firecrawl_client import FirecrawlResearchClient

    body = {
        "success": True,
        "paperId": "8319239866974784291",
        "query": "multi-head attention",
        "passages": [
            {"score": 0.016, "text": "Multi-head attention allows the model ..."},
            {"score": 0.011, "text": "We employ a residual connection ..."},
        ],
    }
    with patch(_OPEN_TARGET, return_value=_mock_resp(body)):
        client = FirecrawlResearchClient()
        passages = client.paper_passages("arxiv:1706.03762", "multi-head attention", k=2)

    assert len(passages) == 2
    assert passages[0]["text"].startswith("Multi-head attention")


def test_paper_passages_missing_paper_returns_empty():
    """404 → [] (no passages), not a degradation."""
    from firecrawl_client import FirecrawlResearchClient

    with patch(_OPEN_TARGET,
               side_effect=_http_error(404, "Not Found")):
        client = FirecrawlResearchClient()
        assert client.paper_passages("arxiv:9999.99999", "anything") == []


def test_paper_passages_rejects_unsupported_id():
    from firecrawl_client import FirecrawlResearchClient, FirecrawlUnavailable

    client = FirecrawlResearchClient()
    with pytest.raises(FirecrawlUnavailable):
        client.paper_passages("doi:10.1038/nature14539", "anything")


# --------------------------------------------------------------------------
# Degradation handling
# --------------------------------------------------------------------------

def test_429_honors_retry_after_header(monkeypatch):
    """Firecrawl documents `Retry-After` (seconds) on 429 and asks callers to
    wait at least that long — it takes precedence over the shared backoff."""
    from firecrawl_client import FirecrawlResearchClient, FirecrawlUnavailable

    calls = [0]

    def mock_urlopen(*args, **kwargs):
        calls[0] += 1
        raise _http_error(429, "Too Many Requests", hdrs={"Retry-After": "7"})

    sleeps = []
    monkeypatch.setattr("firecrawl_client.time.sleep", lambda s: sleeps.append(s))

    with patch(_OPEN_TARGET, side_effect=mock_urlopen):
        client = FirecrawlResearchClient()
        with pytest.raises(FirecrawlUnavailable):
            client.title_search("Attention Is All You Need")

    assert calls[0] == 4  # initial + 3 retries
    assert sleeps == [7.0, 7.0, 7.0]


def test_429_without_retry_after_falls_back_to_exponential(monkeypatch):
    """No header → the shared exponential backoff (2s → 4s → 8s), the same
    shape openalex_client.py uses for a transient burst 429."""
    from firecrawl_client import FirecrawlResearchClient, FirecrawlUnavailable

    def mock_urlopen(*args, **kwargs):
        raise _http_error(429, "Too Many Requests", hdrs={})

    sleeps = []
    monkeypatch.setattr("firecrawl_client.time.sleep", lambda s: sleeps.append(s))

    with patch(_OPEN_TARGET, side_effect=mock_urlopen):
        client = FirecrawlResearchClient()
        with pytest.raises(FirecrawlUnavailable):
            client.title_search("Attention Is All You Need")

    assert sleeps == [2.0, 4.0, 8.0]


def test_429_unparseable_retry_after_falls_back(monkeypatch):
    """An HTTP-date `Retry-After` is legal but not what this API sends; it must
    degrade to the exponential fallback, not crash."""
    from firecrawl_client import FirecrawlResearchClient, FirecrawlUnavailable

    def mock_urlopen(*args, **kwargs):
        raise _http_error(
            429, "Too Many Requests",
            hdrs={"Retry-After": "Wed, 02 Sep 2026 09:00:00 GMT"},
        )

    sleeps = []
    monkeypatch.setattr("firecrawl_client.time.sleep", lambda s: sleeps.append(s))

    with patch(_OPEN_TARGET, side_effect=mock_urlopen):
        client = FirecrawlResearchClient()
        with pytest.raises(FirecrawlUnavailable):
            client.title_search("Attention Is All You Need")

    assert sleeps == [2.0, 4.0, 8.0]


def test_5xx_raises_immediately(monkeypatch):
    """5xx → raise, no retry (sibling contract)."""
    from firecrawl_client import FirecrawlResearchClient, FirecrawlUnavailable

    calls = [0]

    def mock_urlopen(*args, **kwargs):
        calls[0] += 1
        raise _http_error(503, "Service Unavailable")

    sleeps = []
    monkeypatch.setattr("firecrawl_client.time.sleep", lambda s: sleeps.append(s))

    with patch(_OPEN_TARGET, side_effect=mock_urlopen):
        client = FirecrawlResearchClient()
        with pytest.raises(FirecrawlUnavailable):
            client.title_search("Attention Is All You Need")

    assert calls[0] == 1
    assert sleeps == []


def test_network_error_raises_unavailable():
    from firecrawl_client import FirecrawlResearchClient, FirecrawlUnavailable

    with patch(_OPEN_TARGET,
               side_effect=urllib.error.URLError("timed out")):
        client = FirecrawlResearchClient()
        with pytest.raises(FirecrawlUnavailable):
            client.title_search("Attention Is All You Need")


def test_success_false_200_body_is_degradation_not_miss():
    """#331 non-expected-200-body guard: a parseable 200 body without
    `success: true` is a degradation. Reducing it to a miss would let an
    upstream outage persist as a false negative signal."""
    from firecrawl_client import FirecrawlResearchClient, FirecrawlUnavailable

    body = {"success": False, "code": "INTERNAL", "error": "boom"}
    with patch(_OPEN_TARGET, return_value=_mock_resp(body)):
        client = FirecrawlResearchClient()
        with pytest.raises(FirecrawlUnavailable):
            client.title_search("Attention Is All You Need")


def test_html_error_page_served_with_200_raises_unavailable():
    from firecrawl_client import FirecrawlResearchClient, FirecrawlUnavailable

    with patch(_OPEN_TARGET,
               return_value=_raw_resp(b"<html><body>Error</body></html>")):
        client = FirecrawlResearchClient()
        with pytest.raises(FirecrawlUnavailable):
            client.title_search("Attention Is All You Need")


def test_invalid_utf8_body_raises_unavailable():
    from firecrawl_client import FirecrawlResearchClient, FirecrawlUnavailable

    with patch(_OPEN_TARGET, return_value=_raw_resp(b"\xff\xfe\x00")):
        client = FirecrawlResearchClient()
        with pytest.raises(FirecrawlUnavailable):
            client.title_search("Attention Is All You Need")


def test_truncated_read_raises_unavailable():
    """IncompleteRead inherits HTTPException, not OSError — the canonical
    mid-stream socket drop."""
    import http.client

    from firecrawl_client import FirecrawlResearchClient, FirecrawlUnavailable

    mock_response = MagicMock()
    mock_response.read.side_effect = http.client.IncompleteRead(b"{\"succ")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)

    with patch(_OPEN_TARGET, return_value=mock_response):
        client = FirecrawlResearchClient()
        with pytest.raises(FirecrawlUnavailable):
            client.title_search("Attention Is All You Need")


# --------------------------------------------------------------------------
# Auth, pacing, URL discipline
# --------------------------------------------------------------------------

def test_api_key_rides_authorization_header_not_query(monkeypatch):
    """Header auth keeps the key out of the URL, so it cannot land in a log
    line or a raised-exception message."""
    from firecrawl_client import FirecrawlResearchClient

    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-synthetic-test-key")
    seen = []

    def capture(req, *args, **kwargs):
        seen.append(req)
        return _mock_resp(_search())

    with patch(_OPEN_TARGET, side_effect=capture):
        client = FirecrawlResearchClient()
        client.title_search("Attention Is All You Need")

    assert seen[0].get_header("Authorization") == "Bearer fc-synthetic-test-key"
    assert "fc-synthetic-test-key" not in seen[0].full_url


def test_keyless_is_supported(monkeypatch):
    """Both endpoints answer without an Authorization header; a key only
    raises the rate limit. This keeps the client on the same key-free footing
    as the four gate resolvers."""
    from firecrawl_client import FirecrawlResearchClient

    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    seen = []

    def capture(req, *args, **kwargs):
        seen.append(req)
        return _mock_resp({"success": True, "paper": _paper("Attention Is All You Need")})

    with patch(_OPEN_TARGET, side_effect=capture):
        client = FirecrawlResearchClient()
        result = client.paper_id_lookup("arxiv:1706.03762", "Attention Is All You Need")

    assert result is not None
    assert seen[0].get_header("Authorization") is None


def test_api_key_selects_authenticated_pacing_tier(monkeypatch):
    from firecrawl_client import FirecrawlResearchClient

    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    assert FirecrawlResearchClient()._min_interval == 1.0
    assert FirecrawlResearchClient(api_key="fc-synthetic")._min_interval == 0.2


def test_throttle_uses_monotonic_clock(monkeypatch):
    """NTP / manual clock adjustments can make time.time go backward (#128
    §6); pacing must measure elapsed on time.monotonic."""
    from firecrawl_client import FirecrawlResearchClient

    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-synthetic")
    # First _throttle() short-circuits on a None anchor without reading the
    # clock, so the ticks are: anchor set, elapsed read, anchor reset.
    ticks = iter([100.0, 100.05, 100.05])
    monkeypatch.setattr("firecrawl_client.time.monotonic", lambda: next(ticks))
    sleeps = []
    monkeypatch.setattr("firecrawl_client.time.sleep", lambda s: sleeps.append(s))

    with patch(_OPEN_TARGET, return_value=_mock_resp(_search())):
        client = FirecrawlResearchClient()
        client.title_search("Attention Is All You Need")
        client.title_search("Attention Is All You Need")

    # Second call was 0.05s after the first; authenticated interval is 0.2s.
    assert sleeps and abs(sleeps[0] - 0.15) < 1e-9


def test_redirect_is_refused_so_the_key_cannot_leave_the_host():
    """CPython's redirect handler copies `Authorization` to the redirect
    target (it strips only content-length/content-type), so a followed
    cross-origin hop would hand the API key to another host. The opener
    refuses redirects instead; `_require_api_url` cannot catch this because it
    only ever sees the URL this client builds."""
    import firecrawl_client
    from firecrawl_client import FirecrawlUnavailable

    handler = firecrawl_client._RefuseRedirects()
    with pytest.raises(FirecrawlUnavailable):
        handler.redirect_request(
            req=None, fp=None, code=302, msg="Found", headers={},
            newurl="https://evil.example.com/collect",
        )


def test_opener_is_built_with_the_redirect_refusing_handler():
    """Pins the wiring: a future refactor back to bare `urllib.request.urlopen`
    would silently restore the leak, so assert the handler is installed."""
    import firecrawl_client

    assert any(
        isinstance(h, firecrawl_client._RefuseRedirects)
        for h in firecrawl_client._OPENER.handlers
    )


@pytest.mark.parametrize("body", [
    {"success": True},                        # `paper` absent entirely
    {"success": True, "paper": None},
    {"success": True, "paper": "not-a-dict"},
    {"success": True, "paper": []},
])
def test_id_path_schema_drift_raises_instead_of_reading_as_a_miss(body):
    """A 200 answer without a well-formed `paper` is drift, NOT a miss.

    Collapsing it to None would manufacture ID-keyed non-existence evidence
    out of a malformed upstream response — the exact `absent != false`
    confusion this client refuses elsewhere.
    """
    from firecrawl_client import FirecrawlResearchClient, FirecrawlUnavailable

    with patch(_OPEN_TARGET, return_value=_mock_resp(body)):
        client = FirecrawlResearchClient()
        with pytest.raises(FirecrawlUnavailable):
            client.paper_id_lookup("arxiv:1706.03762", "Attention Is All You Need")


@pytest.mark.parametrize("body", [
    {"success": True, "partial": False},      # `results` absent entirely
    {"success": True, "results": None},
    {"success": True, "results": {}},
])
def test_search_schema_drift_raises(body):
    from firecrawl_client import FirecrawlResearchClient, FirecrawlUnavailable

    with patch(_OPEN_TARGET, return_value=_mock_resp(body)):
        client = FirecrawlResearchClient()
        with pytest.raises(FirecrawlUnavailable):
            client.title_search("Attention Is All You Need")


@pytest.mark.parametrize("body", [
    {"success": True, "paperId": "1"},        # `passages` absent entirely
    {"success": True, "passages": None},
    {"success": True, "passages": "text"},
])
def test_passages_schema_drift_raises(body):
    from firecrawl_client import FirecrawlResearchClient, FirecrawlUnavailable

    with patch(_OPEN_TARGET, return_value=_mock_resp(body)):
        client = FirecrawlResearchClient()
        with pytest.raises(FirecrawlUnavailable):
            client.paper_passages("arxiv:1706.03762", "anything")


def test_legitimately_empty_answers_are_not_drift():
    """The counterpart the drift guard must never fire on. Verified live: an
    empty answer is present-but-empty, not omitted — `results: []` for a query
    whose filters match nothing, `passages: []` for a paper with no indexed
    full text."""
    from firecrawl_client import FirecrawlResearchClient

    with patch(_OPEN_TARGET, return_value=_mock_resp(_search())):
        assert FirecrawlResearchClient().title_search("Attention Is All You Need") is None

    empty_passages = {"success": True, "paperId": "1", "passages": []}
    with patch(_OPEN_TARGET, return_value=_mock_resp(empty_passages)):
        assert FirecrawlResearchClient().paper_passages("pmid:25646877", "q") == []


def test_rejects_non_firecrawl_url_before_urlopen(monkeypatch):
    """Host guard mirrors openalex_client._require_api_url."""
    import firecrawl_client
    from firecrawl_client import FirecrawlResearchClient, FirecrawlUnavailable

    monkeypatch.setattr(firecrawl_client, "_API_BASE", "https://evil.example.com/v2")
    with patch(_OPEN_TARGET,
               side_effect=AssertionError("must not request")):
        client = FirecrawlResearchClient()
        with pytest.raises(FirecrawlUnavailable):
            client.title_search("Attention Is All You Need")
