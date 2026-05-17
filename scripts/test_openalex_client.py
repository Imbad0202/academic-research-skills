#!/usr/bin/env python3
"""Tests for OpenAlex client per deep-research/references/openalex_api_protocol.md."""
from __future__ import annotations

import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest


def test_title_search_match_at_threshold(monkeypatch):
    """0.70 similarity threshold matches like S2 (PaperOrchestra precedent)."""
    from openalex_client import OpenAlexClient

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "results": [{
            "title": "Attention Is All You Need",
            "publication_year": 2017,
            "doi": "https://doi.org/10.5555/3295222.3295349",
        }]
    }).encode("utf-8")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)

    with patch("urllib.request.urlopen", return_value=mock_response):
        client = OpenAlexClient()
        result = client.title_search("Attention Is All You Need")

    assert result is not None
    assert result["title"] == "Attention Is All You Need"


def test_title_search_no_match_below_threshold(monkeypatch):
    """No match returned if best candidate similarity < 0.70."""
    from openalex_client import OpenAlexClient

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "results": [{
            "title": "Completely Unrelated Paper Title",
            "publication_year": 2017,
        }]
    }).encode("utf-8")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)

    with patch("urllib.request.urlopen", return_value=mock_response):
        client = OpenAlexClient()
        result = client.title_search("Attention Is All You Need")

    assert result is None


def test_doi_lookup_with_title_cross_check(monkeypatch):
    """DOI hit MUST pass Levenshtein 0.70 title cross-check (DOI_MISMATCH pattern)."""
    from openalex_client import OpenAlexClient

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "title": "Some Other Paper",
        "doi": "https://doi.org/10.5555/3295222.3295349",
        "publication_year": 2020,
    }).encode("utf-8")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)

    with patch("urllib.request.urlopen", return_value=mock_response):
        client = OpenAlexClient()
        result = client.doi_lookup_with_title_check(
            doi="10.5555/3295222.3295349",
            expected_title="Attention Is All You Need",
        )

    assert result is None  # DOI_MISMATCH


def test_doi_lookup_with_matching_title(monkeypatch):
    """DOI hit + matching title → success."""
    from openalex_client import OpenAlexClient

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "title": "Attention Is All You Need",
        "doi": "https://doi.org/10.5555/3295222.3295349",
        "publication_year": 2017,
    }).encode("utf-8")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)

    with patch("urllib.request.urlopen", return_value=mock_response):
        client = OpenAlexClient()
        result = client.doi_lookup_with_title_check(
            doi="10.5555/3295222.3295349",
            expected_title="Attention Is All You Need",
        )

    assert result is not None
    assert result["title"] == "Attention Is All You Need"


def test_429_triggers_2s_backoff_3_retries(monkeypatch):
    """Per protocol: 429 → 2s backoff × 3 retries → raise OpenAlexUnavailable."""
    from openalex_client import OpenAlexClient, OpenAlexUnavailable

    call_count = [0]

    def mock_urlopen(*args, **kwargs):
        call_count[0] += 1
        raise urllib.error.HTTPError(
            url="https://api.openalex.org/works",
            code=429,
            msg="Too Many Requests",
            hdrs={},
            fp=None,
        )

    sleeps = []
    monkeypatch.setattr("openalex_client.time.sleep", lambda s: sleeps.append(s))

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        client = OpenAlexClient()
        with pytest.raises(OpenAlexUnavailable):
            client.title_search("anything")

    assert call_count[0] == 4  # initial + 3 retries
    assert sleeps == [2.0, 2.0, 2.0]


def test_5xx_skips_immediately(monkeypatch):
    """Per protocol: 5xx → no retry (call count == 1), raise OpenAlexUnavailable."""
    from openalex_client import OpenAlexClient, OpenAlexUnavailable

    call_count = [0]

    def mock_urlopen(*args, **kwargs):
        call_count[0] += 1
        raise urllib.error.HTTPError(
            url="https://api.openalex.org/works",
            code=503,
            msg="Service Unavailable",
            hdrs={},
            fp=None,
        )

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        client = OpenAlexClient()
        with pytest.raises(OpenAlexUnavailable):
            client.title_search("anything")

    assert call_count[0] == 1  # no retry on 5xx


def test_polite_pool_email_param(monkeypatch):
    """OPENALEX_POLITE_EMAIL env var adds mailto= query param."""
    from openalex_client import OpenAlexClient

    captured_url = []

    def mock_urlopen(req, *args, **kwargs):
        captured_url.append(req.full_url if hasattr(req, "full_url") else req)
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"results": []}).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)
        return mock_response

    monkeypatch.setenv("OPENALEX_POLITE_EMAIL", "test@example.com")

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        client = OpenAlexClient()
        client.title_search("any title")

    assert any("mailto=test%40example.com" in url for url in captured_url)


def test_doi_404_treated_as_miss_not_unavailable(monkeypatch):
    """DOI not indexed in OpenAlex (404) → return None (miss), not raise OpenAlexUnavailable."""
    from openalex_client import OpenAlexClient, OpenAlexUnavailable

    def mock_urlopen(*args, **kwargs):
        raise urllib.error.HTTPError(
            url="https://api.openalex.org/works/doi:10.5555/nonexistent",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=None,
        )

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        client = OpenAlexClient()
        result = client.doi_lookup_with_title_check(
            doi="10.5555/nonexistent",
            expected_title="Anything",
        )

    assert result is None  # 404 = miss, falls through to title search at caller level


def test_title_search_prefers_matching_year(monkeypatch):
    """When two candidates have similar titles, prefer the one with matching year."""
    from openalex_client import OpenAlexClient

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "results": [
            {"title": "Attention Is All You Need", "publication_year": 1999},  # wrong year
            {"title": "Attention Is All You Need", "publication_year": 2017},  # matching year
        ]
    }).encode("utf-8")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)

    with patch("urllib.request.urlopen", return_value=mock_response):
        client = OpenAlexClient()
        result = client.title_search("Attention Is All You Need", year=2017)

    assert result is not None
    assert result["publication_year"] == 2017
