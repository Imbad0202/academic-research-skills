#!/usr/bin/env python3
"""Tests for Crossref client per deep-research/references/crossref_api_protocol.md."""
from __future__ import annotations

import http.client
import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest


def test_title_search_match_at_threshold(monkeypatch):
    """0.70 similarity threshold matches like S2/OpenAlex."""
    from crossref_client import CrossrefClient

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "message": {
            "items": [{
                "title": ["Attention Is All You Need"],
                "DOI": "10.5555/3295222.3295349",
            }]
        }
    }).encode("utf-8")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)

    with patch("urllib.request.urlopen", return_value=mock_response):
        client = CrossrefClient()
        result = client.title_search("Attention Is All You Need")

    assert result is not None
    # Result should be the candidate dict from items list.
    assert result["title"] == ["Attention Is All You Need"]


def test_title_search_no_match_below_threshold(monkeypatch):
    """No match if best candidate similarity < 0.70."""
    from crossref_client import CrossrefClient

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "message": {
            "items": [{"title": ["Completely Unrelated Paper Title"]}]
        }
    }).encode("utf-8")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)

    with patch("urllib.request.urlopen", return_value=mock_response):
        client = CrossrefClient()
        result = client.title_search("Attention Is All You Need")

    assert result is None


@pytest.mark.parametrize(
    "title",
    [
        pytest.param(None, id="none"),
        pytest.param("", id="empty"),
        pytest.param("   ", id="whitespace"),
        pytest.param("---", id="punctuation"),
    ],
)
def test_title_search_blank_title_does_not_query(title):
    """#1177: a null or empty-normalized title is a miss and sends no request.

    The configured hit has a punctuation-only title, which normalizes to the
    same empty string and would otherwise match.
    """
    from crossref_client import CrossrefClient

    client = CrossrefClient()
    client._get = MagicMock(return_value={
        "message": {"items": [{"title": ["---"], "DOI": "10.0000/punct"}]}
    })

    assert client.title_search(title) is None
    client._get.assert_not_called()


def test_doi_lookup_with_title_cross_check(monkeypatch):
    """DOI hit MUST pass Levenshtein 0.70 title cross-check (DOI_MISMATCH)."""
    from crossref_client import CrossrefClient

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "message": {
            "title": ["Some Other Paper"],
            "DOI": "10.5555/3295222.3295349",
        }
    }).encode("utf-8")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)

    with patch("urllib.request.urlopen", return_value=mock_response):
        client = CrossrefClient()
        result = client.doi_lookup_with_title_check(
            doi="10.5555/3295222.3295349",
            expected_title="Attention Is All You Need",
        )

    assert result is None  # DOI_MISMATCH


@pytest.mark.parametrize(
    ("expected_title", "titles"),
    [
        pytest.param("", [], id="both-empty"),
        pytest.param("   ", [], id="whitespace-expected-missing-returned"),
        pytest.param("Attention Is All You Need", [], id="populated-expected-missing-returned"),
        pytest.param("", ["Attention Is All You Need"], id="empty-expected-populated-returned"),
        pytest.param("   ", ["Attention Is All You Need"], id="whitespace-expected-populated-returned"),
        pytest.param("Attention Is All You Need", ["   "], id="populated-expected-whitespace-returned"),
        pytest.param("", ["   "], id="empty-expected-whitespace-returned"),
        pytest.param("   ", ["   "], id="both-whitespace"),
        pytest.param(None, ["Attention Is All You Need"], id="null-expected-populated-returned"),
    ],
)
def test_doi_lookup_blank_title_is_not_a_match(expected_title, titles):
    """#1163: a DOI hit requires text on both titles. An empty title list is missing."""
    from crossref_client import CrossrefClient

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "message": {
            "title": titles,
            "DOI": "10.5555/3295222.3295349",
        }
    }).encode("utf-8")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)

    with patch("urllib.request.urlopen", return_value=mock_response):
        client = CrossrefClient()
        result = client.doi_lookup_with_title_check(
            doi="10.5555/3295222.3295349",
            expected_title=expected_title,
        )

    assert result is None


def test_doi_lookup_null_first_title_variant_is_miss():
    """#1171: a null first Crossref title variant is a missing title.

    A later language variant is not consulted. The first-variant rule still
    applies when that first element is null.
    """
    from crossref_client import CrossrefClient

    for titles in ([None], [None, "Attention Is All You Need"]):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "message": {
                "title": titles,
                "DOI": "10.5555/3295222.3295349",
            }
        }).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)

        with patch("urllib.request.urlopen", return_value=mock_response):
            client = CrossrefClient()
            result = client.doi_lookup_with_title_check(
                doi="10.5555/3295222.3295349",
                expected_title="Attention Is All You Need",
            )

        assert result is None


def test_title_search_null_first_variant_reaches_later_exact_candidate():
    """#1171: a null title on the first candidate must not hide a later exact hit."""
    from crossref_client import CrossrefClient

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "message": {
            "items": [
                {"title": [None], "DOI": "10.0000/null-title"},
                {
                    "title": ["Attention Is All You Need"],
                    "DOI": "10.5555/3295222.3295349",
                },
            ]
        }
    }).encode("utf-8")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)

    with patch("urllib.request.urlopen", return_value=mock_response):
        client = CrossrefClient()
        result = client.title_search("Attention Is All You Need")

    assert result is not None
    assert result["DOI"] == "10.5555/3295222.3295349"


def test_doi_lookup_with_matching_title(monkeypatch):
    """DOI hit + matching title -> success."""
    from crossref_client import CrossrefClient

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "message": {
            "title": ["Attention Is All You Need"],
            "DOI": "10.5555/3295222.3295349",
        }
    }).encode("utf-8")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)

    with patch("urllib.request.urlopen", return_value=mock_response):
        client = CrossrefClient()
        result = client.doi_lookup_with_title_check(
            doi="10.5555/3295222.3295349",
            expected_title="Attention Is All You Need",
        )

    assert result is not None
    assert result["title"] == ["Attention Is All You Need"]


def test_429_triggers_2s_backoff_3_retries(monkeypatch):
    """Per protocol: 429 -> 2s backoff x 3 retries -> raise CrossrefUnavailable."""
    from crossref_client import CrossrefClient, CrossrefUnavailable

    call_count = [0]

    def mock_urlopen(*args, **kwargs):
        call_count[0] += 1
        raise urllib.error.HTTPError(
            url="https://api.crossref.org/works",
            code=429, msg="Too Many Requests", hdrs={}, fp=None,
        )

    sleeps = []
    monkeypatch.setattr("crossref_client.time.sleep", lambda s: sleeps.append(s))

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        client = CrossrefClient()
        with pytest.raises(CrossrefUnavailable):
            client.title_search("anything")

    assert call_count[0] == 4
    assert sleeps == [2.0, 2.0, 2.0]


def test_5xx_skips_immediately(monkeypatch):
    """Per protocol: 5xx -> no retry, raise CrossrefUnavailable. Assert call_count == 1."""
    from crossref_client import CrossrefClient, CrossrefUnavailable

    call_count = [0]

    def mock_urlopen(*args, **kwargs):
        call_count[0] += 1
        raise urllib.error.HTTPError(
            url="https://api.crossref.org/works", code=503, msg="SU", hdrs={}, fp=None,
        )

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        client = CrossrefClient()
        with pytest.raises(CrossrefUnavailable):
            client.title_search("anything")

    assert call_count[0] == 1


def test_doi_404_treated_as_miss_not_unavailable(monkeypatch):
    """DOI not indexed in Crossref (404) -> return None (miss), not raise CrossrefUnavailable."""
    from crossref_client import CrossrefClient, CrossrefUnavailable

    def mock_urlopen(*args, **kwargs):
        raise urllib.error.HTTPError(
            url="https://api.crossref.org/works/10.5555/nope",
            code=404, msg="Not Found", hdrs={}, fp=None,
        )

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        client = CrossrefClient()
        result = client.doi_lookup_with_title_check(
            doi="10.5555/nope",
            expected_title="Anything",
        )

    assert result is None


def test_title_search_prefers_matching_year(monkeypatch):
    """Two candidates same title - year-match wins via 0.05 score bonus."""
    from crossref_client import CrossrefClient

    mock_response = MagicMock()
    # Crossref year is nested: typically under `published-print` or `issued`.
    # Use `issued.date-parts[0][0]` for the year value (standard Crossref shape).
    mock_response.read.return_value = json.dumps({
        "message": {
            "items": [
                {
                    "title": ["Attention Is All You Need"],
                    "issued": {"date-parts": [[1999]]},
                },
                {
                    "title": ["Attention Is All You Need"],
                    "issued": {"date-parts": [[2017]]},
                },
            ]
        }
    }).encode("utf-8")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)

    with patch("urllib.request.urlopen", return_value=mock_response):
        client = CrossrefClient()
        result = client.title_search("Attention Is All You Need", year=2017)

    assert result is not None
    assert result["issued"]["date-parts"][0][0] == 2017


def test_polite_pool_email_in_user_agent(monkeypatch):
    """CROSSREF_POLITE_EMAIL adds 'mailto:...' to User-Agent header (NOT query param)."""
    from crossref_client import CrossrefClient

    captured_headers = []

    def mock_urlopen(req, *args, **kwargs):
        # urllib.request.Request stores headers; access via get_header (case-insensitive)
        ua = req.get_header("User-agent") or ""
        captured_headers.append(ua)
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"message": {"items": []}}).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)
        return mock_response

    monkeypatch.setenv("CROSSREF_POLITE_EMAIL", "test@example.com")

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        client = CrossrefClient()
        client.title_search("any title")

    assert any("mailto:test@example.com" in ua for ua in captured_headers)


# ---------- v3.9.1: #129 response-read failure wrapping (Crossref) ----------


@pytest.mark.parametrize(
    "exc",
    [
        http.client.RemoteDisconnected("closed before status"),
        http.client.BadStatusLine("garbled status"),
        OSError("connection failed"),
    ],
    ids=["RemoteDisconnected", "BadStatusLine", "OSError"],
)
def test_urlopen_transport_failure_raises_unavailable(exc):
    """urlopen itself raises before a response arrives. A drop before the
    status line, a garbled status line, or a bare OSError must become
    CrossrefUnavailable, with the injected instance as the cause."""
    from crossref_client import CrossrefClient, CrossrefUnavailable

    with patch("urllib.request.urlopen", side_effect=exc) as urlopen:
        client = CrossrefClient()
        with pytest.raises(CrossrefUnavailable) as raised:
            client.title_search("any title")

    assert raised.value.__cause__ is exc
    assert urlopen.call_count == 1


def test_oserror_during_read_raises_unavailable(monkeypatch):
    """urlopen succeeds, but resp.read() raises OSError (socket drop / timeout
    mid-stream). Per v3.9.0 spec §3.7 degradation contract, this MUST be
    translated to CrossrefUnavailable so migrate_literature_corpus_to_v3_9_0
    omits crossref_unmatched instead of aborting the whole backfill."""
    from crossref_client import CrossrefClient, CrossrefUnavailable

    mock_response = MagicMock()
    mock_response.read.side_effect = OSError("socket dropped mid-read")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)

    with patch("urllib.request.urlopen", return_value=mock_response):
        client = CrossrefClient()
        with pytest.raises(CrossrefUnavailable):
            client.title_search("any title")


def test_invalid_utf8_body_raises_unavailable(monkeypatch):
    """resp.read() returns bytes that aren't valid UTF-8. Per v3.9.0 spec §3.7,
    translate to CrossrefUnavailable not bubble UnicodeDecodeError."""
    from crossref_client import CrossrefClient, CrossrefUnavailable

    mock_response = MagicMock()
    mock_response.read.return_value = b"\xff\xfe\xff garbage"
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)

    with patch("urllib.request.urlopen", return_value=mock_response):
        client = CrossrefClient()
        with pytest.raises(CrossrefUnavailable):
            client.title_search("any title")


def test_invalid_json_body_raises_unavailable(monkeypatch):
    """resp.read() returns valid utf-8 but not valid JSON (truncated body /
    HTML error page). Per v3.9.0 spec §3.7, translate to CrossrefUnavailable
    not bubble JSONDecodeError."""
    from crossref_client import CrossrefClient, CrossrefUnavailable

    mock_response = MagicMock()
    mock_response.read.return_value = b"<html>503 backend unavailable</html>"
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)

    with patch("urllib.request.urlopen", return_value=mock_response):
        client = CrossrefClient()
        with pytest.raises(CrossrefUnavailable):
            client.title_search("any title")


def test_truncated_read_raises_unavailable(monkeypatch):
    """http.client.IncompleteRead = mid-stream socket drop (200 + truncated
    body). Inherits HTTPException not OSError. v3.9.1 codex R1 P2 — symmetric
    to OpenAlex client."""
    import http.client

    from crossref_client import CrossrefClient, CrossrefUnavailable

    mock_response = MagicMock()
    mock_response.read.side_effect = http.client.IncompleteRead(
        partial=b'{"message":', expected=200
    )
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)

    with patch("urllib.request.urlopen", return_value=mock_response):
        client = CrossrefClient()
        with pytest.raises(CrossrefUnavailable):
            client.title_search("any title")


def test_throttle_uses_monotonic_clock(monkeypatch):
    """time.monotonic for elapsed measurement (NTP-safe). time.time can
    go backward on NTP adjustments, breaking elapsed calculation.
    Aligns OA/CR with semantic_scholar_client.py (#128 §6)."""
    from crossref_client import CrossrefClient

    monotonic_calls = []
    time_calls = []

    def fake_monotonic():
        monotonic_calls.append(1)
        return 100.0

    def fake_time():
        time_calls.append(1)
        return 100.0

    monkeypatch.setattr("crossref_client.time.monotonic", fake_monotonic)
    monkeypatch.setattr("crossref_client.time.time", fake_time)

    client = CrossrefClient()
    # Initial state: no prior request — _throttle short-circuits.
    client._throttle()
    # Set anchor, then check throttle uses monotonic, not time.time.
    client._last_request_at = 90.0
    client._throttle()

    assert len(monotonic_calls) >= 1, "throttle must read time.monotonic"
    assert len(time_calls) == 0, "throttle must NOT read time.time (NTP-unsafe)"


def test_doi_lookup_quotes_doi_path_segment(monkeypatch):
    """DOI lookup must encode path separators/query markers before urlopen."""
    from crossref_client import CrossrefClient

    captured_urls = []

    def mock_urlopen(req, *args, **kwargs):
        captured_urls.append(req.full_url)
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "message": {
                "title": ["Attention Is All You Need"],
                "DOI": "10.1000/foo?bar=baz",
            }
        }).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)
        return mock_response

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        client = CrossrefClient()
        result = client.doi_lookup_with_title_check(
            doi="10.1000/foo?bar=baz",
            expected_title="Attention Is All You Need",
        )

    assert result is not None
    assert captured_urls == [
        "https://api.crossref.org/works/10.1000%2Ffoo%3Fbar%3Dbaz"
    ]


def test_rejects_non_crossref_api_url_before_urlopen(monkeypatch):
    import crossref_client
    from crossref_client import CrossrefClient, CrossrefUnavailable

    monkeypatch.setattr(crossref_client, "_API_BASE", "http://evil.example")
    urlopen = MagicMock()
    with patch("urllib.request.urlopen", urlopen):
        client = CrossrefClient()
        with pytest.raises(CrossrefUnavailable):
            client.title_search("anything")

    assert urlopen.call_count == 0


def test_refusal_message_never_carries_mailto(monkeypatch):
    """The non-Crossref-URL refusal strips the query string so the polite-pool
    mailto (an email address) never lands in raised-exception text / logs
    (#495; mirrors openalex_client.py)."""
    import crossref_client
    from crossref_client import CrossrefClient, CrossrefUnavailable

    monkeypatch.setattr(crossref_client, "_API_BASE", "http://evil.example")
    with patch("urllib.request.urlopen", MagicMock()):
        client = CrossrefClient(polite_email="secret@example.com")
        with pytest.raises(CrossrefUnavailable) as excinfo:
            client.title_search("anything")

    assert "secret@example.com" not in str(excinfo.value)


# ---------------------------------------------------------------------------
# CJK title matching (#431 repair) — integration through the real client.
#
# The shared helpers were ASCII-centric, so a Chinese title that an index serves
# in a different-but-legitimate typesetting reduced to DOI_MISMATCH (DOI path)
# or unresolvable (title path) — the same state a fabricated citation produces.
# ---------------------------------------------------------------------------

_CN_CITED = "基于ProEXC的宫颈癌筛查研究"
_CN_AS_INDEXED = "基于ＰｒｏＥＸＣ的宫颈癌筛查研究。"  # fullwidth latin + terminal 。
_CN_UNRELATED = "基于液基细胞学的宫颈癌筛查研究"


def _crossref_response(payload):
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(payload).encode("utf-8")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)
    return mock_response


def test_doi_lookup_accepts_legitimate_cjk_typesetting_variant():
    """A correct DOI whose indexed title uses fullwidth Latin must NOT reduce to
    DOI_MISMATCH. This path gates on the ratio alone, which measured 0.625 for
    this pair before the repair."""
    from crossref_client import CrossrefClient

    response = _crossref_response({"message": {"title": [_CN_AS_INDEXED], "DOI": "10.1000/cn.1"}})
    with patch("urllib.request.urlopen", return_value=response):
        result = CrossrefClient().doi_lookup_with_title_check("10.1000/cn.1", _CN_CITED)

    assert result is not None, "correct DOI for a real Chinese paper reported as DOI_MISMATCH"
    assert result["DOI"] == "10.1000/cn.1"


def test_doi_lookup_still_rejects_a_different_cjk_paper():
    """The guard: Han overlap alone (0.510 measured) must never promote a
    genuinely different paper."""
    from crossref_client import CrossrefClient

    response = _crossref_response({"message": {"title": [_CN_UNRELATED], "DOI": "10.1000/cn.2"}})
    with patch("urllib.request.urlopen", return_value=response):
        result = CrossrefClient().doi_lookup_with_title_check("10.1000/cn.2", _CN_CITED)

    assert result is None


def test_title_search_matches_legitimate_cjk_typesetting_variant():
    """The title-fallback path requires ratio AND exact-normalized equality;
    before the repair a legitimate variant failed both and fell to
    `unresolvable`."""
    from crossref_client import CrossrefClient

    response = _crossref_response(
        {"message": {"items": [{"title": [_CN_AS_INDEXED], "DOI": "10.1000/cn.1"}]}}
    )
    with patch("urllib.request.urlopen", return_value=response):
        result = CrossrefClient().title_search(_CN_CITED)

    assert result is not None, "legitimate CJK variant fell through to unresolvable"
    assert result["DOI"] == "10.1000/cn.1"


def test_title_search_still_rejects_a_different_cjk_paper():
    from crossref_client import CrossrefClient

    response = _crossref_response(
        {"message": {"items": [{"title": [_CN_UNRELATED], "DOI": "10.1000/cn.2"}]}}
    )
    with patch("urllib.request.urlopen", return_value=response):
        result = CrossrefClient().title_search(_CN_CITED)

    assert result is None


def test_title_search_does_not_match_a_cross_script_shadow_title():
    """An English shadow title is not chimeric-citation evidence and is not a
    match either: there is no translation oracle in this client."""
    from crossref_client import CrossrefClient

    response = _crossref_response(
        {"message": {"items": [{
            "title": ["ProEXC-based cervical cancer screening"],
            "DOI": "10.1000/cn.3",
        }]}}
    )
    with patch("urllib.request.urlopen", return_value=response):
        result = CrossrefClient().title_search(_CN_CITED)

    assert result is None


def test_title_search_matches_an_en_dash_title_typed_with_a_hyphen():
    """Crossref serves this 1961 Nature title with an en dash
    (10.1038/189151a0); a reference typed with an ASCII hyphen is the same
    title and must not fall through to `unresolvable`."""
    from crossref_client import CrossrefClient

    response = _crossref_response(
        {"message": {"items": [{
            "title": ["Dose\u2013Response Relationship in Radiation Carcinogenesis"],
            "DOI": "10.1038/189151a0",
        }]}}
    )
    with patch("urllib.request.urlopen", return_value=response):
        result = CrossrefClient().title_search(
            "Dose-Response Relationship in Radiation Carcinogenesis")

    assert result is not None, "hyphen spelling of an en-dash title fell through to unresolvable"
    assert result["DOI"] == "10.1038/189151a0"


def _crossref_200(body: bytes) -> MagicMock:
    resp = MagicMock()
    resp.read.return_value = body
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=None)
    return resp


# ---------- #1184 items 3-4: 200 bodies the client cannot use ----------


@pytest.mark.parametrize("body", [b"null", b"[]", b'"maintenance"'])
def test_non_object_json_body_raises_unavailable(body):
    """A null or [] DOI body used to read as a miss, and title search raised
    AttributeError."""
    from crossref_client import CrossrefClient, CrossrefUnavailable

    with patch("urllib.request.urlopen", return_value=_crossref_200(body)):
        client = CrossrefClient()
        with pytest.raises(CrossrefUnavailable):
            client.title_search("Attention Is All You Need")
        with pytest.raises(CrossrefUnavailable):
            client.doi_lookup_with_title_check("10.1/x", "Attention Is All You Need")


@pytest.mark.parametrize("payload", [
    {"status": "error", "message": "maintenance"},
    {"status": "ok", "message": {"total-results": 0}},
    {"status": "ok", "message": {"items": None}},
    {},
])
def test_title_search_without_items_raises_unavailable(payload):
    from crossref_client import CrossrefClient, CrossrefUnavailable

    body = json.dumps(payload).encode("utf-8")
    with patch("urllib.request.urlopen", return_value=_crossref_200(body)):
        with pytest.raises(CrossrefUnavailable):
            CrossrefClient().title_search("Attention Is All You Need")


def test_title_search_empty_items_and_404_stay_a_miss():
    from crossref_client import CrossrefClient

    body = json.dumps({"status": "ok", "message": {"items": []}}).encode("utf-8")
    with patch("urllib.request.urlopen", return_value=_crossref_200(body)):
        assert CrossrefClient().title_search("Attention Is All You Need") is None
    not_found = urllib.error.HTTPError("u", 404, "Not Found", {}, None)
    with patch("urllib.request.urlopen", side_effect=not_found):
        assert CrossrefClient().title_search("Attention Is All You Need") is None
