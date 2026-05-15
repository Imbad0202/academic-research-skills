#!/usr/bin/env python3
"""#105 v3.7.3 contamination_signals resolver tests.

Tests the two pure-function signals defined in v3.7.3 spec §3.2 that
the migration tool uses to backfill pre-v3.7.3 literature_corpus entries.

Signal 1 (preprint_post_llm_inflection): year >= 2024 AND venue in 10-server
closed list (per spec §3.2 Vector 1 + schema description).

Signal 2 (semantic_scholar_unmatched): SS API lookup with manual exemption
+ API degradation handling (per spec §3.2 Vector 2 + R-L3-2-B).

Design: docs/design/2026-05-15-issue-105-contamination-signals-backfill-design.md
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import contamination_signals as cs  # noqa: E402


# ============================================================================
# Signal 1 — preprint_post_llm_inflection
# ============================================================================
class PreprintSignalTest(unittest.TestCase):
    """Signal 1 per v3.7.3 spec §3.2 Vector 1: True iff year >= 2024 AND
    venue ∈ 10-server closed list."""

    def test_arxiv_2024_returns_true(self) -> None:
        self.assertTrue(cs.compute_preprint_signal({"year": 2024, "venue": "arXiv"}))

    def test_arxiv_2023_returns_false(self) -> None:
        # Year boundary: 2023 is below threshold
        self.assertFalse(cs.compute_preprint_signal({"year": 2023, "venue": "arXiv"}))

    def test_arxiv_2025_returns_true(self) -> None:
        self.assertTrue(cs.compute_preprint_signal({"year": 2025, "venue": "arXiv"}))

    def test_biorxiv_2024_returns_true(self) -> None:
        self.assertTrue(cs.compute_preprint_signal({"year": 2024, "venue": "bioRxiv"}))

    def test_medrxiv_2024_returns_true(self) -> None:
        self.assertTrue(cs.compute_preprint_signal({"year": 2024, "venue": "medRxiv"}))

    def test_ssrn_2024_returns_true(self) -> None:
        self.assertTrue(cs.compute_preprint_signal({"year": 2024, "venue": "SSRN"}))

    def test_research_square_2024_returns_true(self) -> None:
        self.assertTrue(
            cs.compute_preprint_signal({"year": 2024, "venue": "Research Square"})
        )

    def test_preprints_org_2024_returns_true(self) -> None:
        self.assertTrue(
            cs.compute_preprint_signal({"year": 2024, "venue": "Preprints.org"})
        )

    def test_chemrxiv_2024_returns_true(self) -> None:
        """v3.7.3 codex F6 / gemini review F6 expansion."""
        self.assertTrue(cs.compute_preprint_signal({"year": 2024, "venue": "ChemRxiv"}))

    def test_eartharxiv_2024_returns_true(self) -> None:
        self.assertTrue(
            cs.compute_preprint_signal({"year": 2024, "venue": "EarthArXiv"})
        )

    def test_osf_preprints_2024_returns_true(self) -> None:
        self.assertTrue(
            cs.compute_preprint_signal({"year": 2024, "venue": "OSF Preprints"})
        )

    def test_techrxiv_2024_returns_true(self) -> None:
        self.assertTrue(cs.compute_preprint_signal({"year": 2024, "venue": "TechRxiv"}))

    def test_non_preprint_venue_2024_returns_false(self) -> None:
        # Year passes threshold but venue is not in the closed list
        self.assertFalse(
            cs.compute_preprint_signal({"year": 2024, "venue": "Nature"})
        )

    def test_missing_venue_returns_false(self) -> None:
        # Defensive: entries lacking venue cannot satisfy the AND
        self.assertFalse(cs.compute_preprint_signal({"year": 2024}))

    def test_missing_year_returns_false(self) -> None:
        # Defensive: entries lacking year cannot satisfy the AND
        self.assertFalse(cs.compute_preprint_signal({"venue": "arXiv"}))

    def test_source_pointer_infers_arxiv(self) -> None:
        """Codex R2-1 closure: when venue is missing, source_pointer
        URLs to preprint servers must satisfy Signal 1."""
        self.assertTrue(
            cs.compute_preprint_signal(
                {"year": 2024, "source_pointer": "https://arxiv.org/abs/2401.12345"}
            )
        )

    def test_source_pointer_infers_biorxiv(self) -> None:
        self.assertTrue(
            cs.compute_preprint_signal(
                {"year": 2025, "source_pointer": "https://www.biorxiv.org/content/10.1101/2025.01.01.000000v1"}
            )
        )

    def test_source_pointer_infers_osf_preprints(self) -> None:
        self.assertTrue(
            cs.compute_preprint_signal(
                {"year": 2024, "source_pointer": "https://osf.io/preprints/socarxiv/xyz123"}
            )
        )

    def test_source_pointer_non_preprint_returns_false(self) -> None:
        """An arbitrary URL with no preprint-server hint stays False."""
        self.assertFalse(
            cs.compute_preprint_signal(
                {"year": 2024, "source_pointer": "https://nature.com/articles/x"}
            )
        )

    def test_source_pointer_ignored_when_venue_present(self) -> None:
        """Explicit `venue` field takes precedence — Nature 2024 with an
        arxiv source_pointer is still venue=Nature (Signal 1 false)."""
        self.assertFalse(
            cs.compute_preprint_signal(
                {
                    "year": 2024,
                    "venue": "Nature",
                    "source_pointer": "https://arxiv.org/abs/2401.x",
                }
            )
        )

    def test_source_pointer_pre_2024_returns_false(self) -> None:
        """Year < 2024 short-circuits before pointer inference fires."""
        self.assertFalse(
            cs.compute_preprint_signal(
                {"year": 2023, "source_pointer": "https://arxiv.org/abs/2301.x"}
            )
        )


# ============================================================================
# Signal 2 — semantic_scholar_unmatched
# ============================================================================
class SemanticScholarSignalTest(unittest.TestCase):
    """Signal 2 per v3.7.3 spec §3.2 Vector 2: SS API lookup. Returns None
    on (a) manual exemption (b) API degradation; True/False otherwise.

    The SS client is dependency-injected — tests use a MagicMock that
    returns whatever match shape the test specifies."""

    def _entry(self, **overrides):
        base = {
            "citation_key": "chen2024ai",
            "title": "Test paper",
            "authors": [{"family": "Chen", "given": "A"}],
            "year": 2024,
            "doi": "10.1234/xyz",
            "obtained_via": "folder-scan",
        }
        return base | overrides

    def test_manual_entry_returns_none(self) -> None:
        """v3.7.3 spec §3.2 + schema allOf rule #4: obtained_via='manual'
        triggers SKIP — the field MUST be omitted from the emission."""
        client = MagicMock()
        result = cs.compute_ss_unmatched_signal(
            self._entry(obtained_via="manual"), client
        )
        self.assertIsNone(result)
        # The exemption is a skip, not an API call
        client.lookup.assert_not_called()

    def test_ss_match_returns_false(self) -> None:
        client = MagicMock()
        client.lookup.return_value = {"matched": True, "paperId": "abc123"}
        self.assertFalse(cs.compute_ss_unmatched_signal(self._entry(), client))

    def test_ss_no_match_returns_true(self) -> None:
        client = MagicMock()
        client.lookup.return_value = {"matched": False, "paperId": None}
        self.assertTrue(cs.compute_ss_unmatched_signal(self._entry(), client))

    def test_ss_api_degradation_returns_none(self) -> None:
        """Per spec §3.2: API unreachable (network failure / rate-limit-
        exhausted / 5xx) returns None. Absence ≠ negative confirmation;
        setting False would imply 'checked and found'."""
        client = MagicMock()
        client.lookup.side_effect = cs.SemanticScholarUnavailable("rate limit exhausted")
        self.assertIsNone(cs.compute_ss_unmatched_signal(self._entry(), client))

    def test_ss_network_failure_returns_none(self) -> None:
        client = MagicMock()
        client.lookup.side_effect = cs.SemanticScholarUnavailable("connection refused")
        self.assertIsNone(cs.compute_ss_unmatched_signal(self._entry(), client))

    def test_unexpected_exception_propagates(self) -> None:
        """Distinguish 'API degradation' (a known-handled signal) from
        unknown bugs. ValueError isn't SS-API-degradation; let it surface
        so the migration tool can fail loudly rather than silently OMIT."""
        client = MagicMock()
        client.lookup.side_effect = ValueError("bug in client")
        with self.assertRaises(ValueError):
            cs.compute_ss_unmatched_signal(self._entry(), client)


# ============================================================================
# Emission rules — building the contamination_signals object
# ============================================================================
class EmissionRulesTest(unittest.TestCase):
    """Per spec §3.2 emission rules: emit object with both fields false
    when computed-and-clean; emit partial object when one signal can't
    be computed; omit semantic_scholar_unmatched on manual exemption."""

    def _entry(self, **overrides):
        base = {
            "year": 2024,
            "venue": "arXiv",
            "obtained_via": "folder-scan",
        }
        return base | overrides

    def test_both_signals_computed_emits_full_object(self) -> None:
        client = MagicMock()
        client.lookup.return_value = {"matched": False}
        result = cs.build_signals_object(self._entry(), client)
        self.assertEqual(
            result,
            {"preprint_post_llm_inflection": True, "semantic_scholar_unmatched": True},
        )

    def test_clean_entry_emits_both_false(self) -> None:
        client = MagicMock()
        client.lookup.return_value = {"matched": True}
        result = cs.build_signals_object(self._entry(year=2023, venue="Nature"), client)
        self.assertEqual(
            result,
            {"preprint_post_llm_inflection": False, "semantic_scholar_unmatched": False},
        )

    def test_manual_entry_omits_unmatched_field(self) -> None:
        client = MagicMock()
        result = cs.build_signals_object(
            self._entry(obtained_via="manual"), client
        )
        self.assertEqual(result, {"preprint_post_llm_inflection": True})
        self.assertNotIn("semantic_scholar_unmatched", result)

    def test_api_degradation_omits_unmatched_field(self) -> None:
        """Partial computation: Signal 1 still emits (trivial from
        year+venue), Signal 2 omitted (API down). Per spec §3.2."""
        client = MagicMock()
        client.lookup.side_effect = cs.SemanticScholarUnavailable("5xx")
        result = cs.build_signals_object(self._entry(), client)
        self.assertEqual(result, {"preprint_post_llm_inflection": True})
        self.assertNotIn("semantic_scholar_unmatched", result)


class ResetClientOutageLatchHelperTest(unittest.TestCase):
    """#115 R5-3 helper: production clients implementing the outage-latch
    pattern expose `reset_outage_latch()`; minimal mocks may not. The
    helper invokes when present, no-ops when absent. Avoids
    AttributeError for callers that swap in test mocks."""

    def test_helper_invokes_reset_when_present(self) -> None:
        client = MagicMock()
        cs.reset_client_outage_latch(client)
        client.reset_outage_latch.assert_called_once()

    def test_helper_no_ops_when_method_absent(self) -> None:
        client = MagicMock(spec=["lookup"])  # only the Protocol's lookup
        # Should NOT raise AttributeError
        cs.reset_client_outage_latch(client)


if __name__ == "__main__":
    unittest.main()
