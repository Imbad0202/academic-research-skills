#!/usr/bin/env python3
"""Tests for the minimal Semantic Scholar client backing #105 CLI.

Mocks urllib at the transport layer (no real network). Verifies the
client honors the protocol's DOI-first + title-similarity + 429-backoff
contract and surfaces SemanticScholarUnavailable on the documented
failure modes.
"""
from __future__ import annotations

import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch, MagicMock

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import semantic_scholar_client as ssc  # noqa: E402
from contamination_signals import SemanticScholarUnavailable  # noqa: E402


def _mock_urlopen_returning(payload: dict) -> MagicMock:
    """Build a urlopen mock that returns `payload` JSON as the response body."""
    body = json.dumps(payload).encode("utf-8")
    resp = MagicMock()
    resp.read.return_value = body
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=False)
    return MagicMock(return_value=resp)


class DoiLookupTest(unittest.TestCase):
    def test_doi_match_with_matching_title(self) -> None:
        client = ssc.SemanticScholarClient()
        payload = {"paperId": "abc123", "title": "AI in education"}
        with patch(
            "urllib.request.urlopen", _mock_urlopen_returning(payload)
        ):
            result = client.lookup(
                {"title": "AI in education", "doi": "10.1234/xyz", "year": 2024}
            )
        self.assertEqual(result, {"matched": True, "paperId": "abc123"})

    def test_doi_match_with_title_mismatch_counts_as_no_match(self) -> None:
        """Per protocol §"Query Patterns": DOI_MISMATCH (title differs
        despite DOI hit) is a known hallucination pattern. For the binary
        contamination signal we map it to no-match."""
        client = ssc.SemanticScholarClient()
        payload = {"paperId": "abc123", "title": "Totally unrelated paper"}
        with patch(
            "urllib.request.urlopen", _mock_urlopen_returning(payload)
        ):
            result = client.lookup(
                {"title": "AI in education", "doi": "10.1234/xyz", "year": 2024}
            )
        self.assertEqual(result, {"matched": False, "paperId": None})


class TitleSearchTest(unittest.TestCase):
    def test_title_search_above_threshold_matches(self) -> None:
        client = ssc.SemanticScholarClient()
        payload = {
            "data": [
                {"paperId": "abc123", "title": "AI in education", "year": 2024}
            ]
        }
        with patch(
            "urllib.request.urlopen", _mock_urlopen_returning(payload)
        ):
            result = client.lookup({"title": "AI in education", "year": 2024})
        self.assertEqual(result, {"matched": True, "paperId": "abc123"})

    def test_title_search_below_threshold_no_match(self) -> None:
        client = ssc.SemanticScholarClient()
        payload = {
            "data": [
                {"paperId": "xyz", "title": "Totally different", "year": 2024}
            ]
        }
        with patch(
            "urllib.request.urlopen", _mock_urlopen_returning(payload)
        ):
            result = client.lookup({"title": "AI in education", "year": 2024})
        self.assertEqual(result, {"matched": False, "paperId": None})

    def test_empty_results_no_match(self) -> None:
        client = ssc.SemanticScholarClient()
        with patch(
            "urllib.request.urlopen", _mock_urlopen_returning({"data": []})
        ):
            result = client.lookup({"title": "Unknown paper"})
        self.assertEqual(result, {"matched": False, "paperId": None})


class FailureHandlingTest(unittest.TestCase):
    def _raise_http(self, code: int):
        return urllib.error.HTTPError("u", code, "msg", {}, io.BytesIO(b""))

    def test_429_backoff_then_recover(self) -> None:
        """Per protocol: HTTP 429 → 2s backoff × 3 retries before
        giving up. The retry is transparent — successful retry returns
        a normal result without raising."""
        client = ssc.SemanticScholarClient(sleep=MagicMock())
        payload = {"paperId": "abc", "title": "AI in education"}
        body = json.dumps(payload).encode("utf-8")
        resp = MagicMock()
        resp.read.return_value = body
        resp.__enter__ = MagicMock(return_value=resp)
        resp.__exit__ = MagicMock(return_value=False)

        # First two calls 429, third succeeds
        urlopen = MagicMock(side_effect=[
            self._raise_http(429),
            self._raise_http(429),
            resp,
        ])
        with patch("urllib.request.urlopen", urlopen):
            result = client.lookup(
                {"title": "AI in education", "doi": "10.1234/xyz"}
            )
        self.assertEqual(result, {"matched": True, "paperId": "abc"})

    def test_429_after_max_retries_raises_unavailable(self) -> None:
        client = ssc.SemanticScholarClient(sleep=MagicMock())
        # All 4 attempts (initial + 3 retries) raise 429
        urlopen = MagicMock(side_effect=[self._raise_http(429)] * 4)
        with patch("urllib.request.urlopen", urlopen):
            with self.assertRaises(SemanticScholarUnavailable):
                client.lookup({"title": "X", "doi": "10.1/y"})

    def test_5xx_raises_unavailable(self) -> None:
        client = ssc.SemanticScholarClient(sleep=MagicMock())
        urlopen = MagicMock(side_effect=self._raise_http(503))
        with patch("urllib.request.urlopen", urlopen):
            with self.assertRaises(SemanticScholarUnavailable):
                client.lookup({"title": "X", "doi": "10.1/y"})

    def test_404_means_no_match_not_unavailable(self) -> None:
        client = ssc.SemanticScholarClient(sleep=MagicMock())
        urlopen = MagicMock(side_effect=self._raise_http(404))
        with patch("urllib.request.urlopen", urlopen):
            result = client.lookup({"title": "X", "doi": "10.1/y"})
        self.assertEqual(result, {"matched": False, "paperId": None})

    def test_network_error_raises_unavailable(self) -> None:
        client = ssc.SemanticScholarClient(sleep=MagicMock())
        urlopen = MagicMock(side_effect=urllib.error.URLError("connection refused"))
        with patch("urllib.request.urlopen", urlopen):
            with self.assertRaises(SemanticScholarUnavailable):
                client.lookup({"title": "X", "doi": "10.1/y"})


class CLIWiringTest(unittest.TestCase):
    """Codex R1-1 closure: CLI was unrunnable because NotImplementedError
    fired before reading the passport. Verify the production wiring path
    now actually constructs a SemanticScholarClient instance."""

    def test_build_default_ss_client_returns_real_client(self) -> None:
        import migrate_literature_corpus_to_v3_7_3 as mig
        client = mig._build_default_ss_client()
        self.assertIsInstance(client, ssc.SemanticScholarClient)


if __name__ == "__main__":
    unittest.main()
