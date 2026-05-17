#!/usr/bin/env python3
"""#102 v3.9.0 cross-index triangulation backfill migration tool tests.

Tests scripts/migrate_literature_corpus_to_v3_9_0.py — the CLI that
backfills `openalex_unmatched` and `crossref_unmatched` on v3.7.3-onward
literature_corpus[] entries per v3.9.0 spec §3.7.

Design: docs/design/2026-05-17-ars-v3.9.0-cross-index-triangulation-measurement-spec.md
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import migrate_literature_corpus_to_v3_9_0 as mig  # noqa: E402

from openalex_client import OpenAlexUnavailable  # noqa: E402
from crossref_client import CrossrefUnavailable  # noqa: E402


# ---------------------------------------------------------------------------
# Mock client helpers
# ---------------------------------------------------------------------------

def _make_oa_client(matched_dois: frozenset[str] | None = None, matched_titles: frozenset[str] | None = None):
    """Mock OpenAlexClient.

    `matched_dois`: set of DOI strings that return a hit on doi_lookup_with_title_check.
    `matched_titles`: set of title strings that return a hit on title_search.
    Both default to empty (everything unmatched).
    """
    matched_dois = matched_dois or frozenset()
    matched_titles = matched_titles or frozenset()
    client = MagicMock()

    def doi_lookup(doi, expected_title):
        if doi in matched_dois:
            return {"title": expected_title}
        return None

    def title_search(title, year=None):
        if title in matched_titles:
            return {"title": title}
        return None

    client.doi_lookup_with_title_check.side_effect = doi_lookup
    client.title_search.side_effect = title_search
    return client


def _make_cr_client(matched_dois: frozenset[str] | None = None, matched_titles: frozenset[str] | None = None):
    """Mirror of _make_oa_client for CrossrefClient."""
    matched_dois = matched_dois or frozenset()
    matched_titles = matched_titles or frozenset()
    client = MagicMock()

    def doi_lookup(doi, expected_title):
        if doi in matched_dois:
            return {"title": expected_title}
        return None

    def title_search(title, year=None):
        if title in matched_titles:
            return {"title": title}
        return None

    client.doi_lookup_with_title_check.side_effect = doi_lookup
    client.title_search.side_effect = title_search
    return client


def _make_passport(tmp_path, entries):
    """Write a minimal passport YAML and return its Path."""
    from ruamel.yaml import YAML
    p = tmp_path / "passport.yaml"
    y = YAML()
    y.preserve_quotes = True
    y.indent(mapping=2, sequence=4, offset=2)
    with p.open("w") as f:
        y.dump({"version": 9, "literature_corpus": entries}, f)
    return p


# ============================================================================
# 1. Dry-run: no file write
# ============================================================================
class DryRunTest(unittest.TestCase):
    def test_dry_run_does_not_modify_file(self) -> None:
        """--dry-run prints diff but leaves file untouched."""
        with tempfile.TemporaryDirectory() as td:
            p = _make_passport(Path(td), [{
                "citation_key": "smith2024",
                "title": "Some Paper",
                "authors": [{"family": "Smith"}],
                "year": 2024,
                "source_pointer": "doi:10.5555/abc",
                "doi": "10.5555/abc",
                "obtained_via": "folder-scan",
                "contamination_signals": {
                    "preprint_post_llm_inflection": False,
                    "semantic_scholar_unmatched": True,
                },
            }])
            before = p.read_bytes()
            # OpenAlex/Crossref return no match — would set True on real run.
            report = mig.migrate_passport(
                p,
                oa_client=_make_oa_client(),
                cr_client=_make_cr_client(),
                dry_run=True,
            )
            after = p.read_bytes()
            self.assertEqual(before, after, "dry-run must not write")
            # Would-add should be 1 (both fields to be added to 1 entry)
            self.assertEqual(report["would_add"] if "would_add" in report else report["patched"], 1)


# ============================================================================
# 2. Full backfill: both new fields populated correctly
# ============================================================================
class BackfillTest(unittest.TestCase):
    def test_backfill_populates_two_new_fields(self) -> None:
        """openalex_unmatched + crossref_unmatched are added to eligible entry."""
        with tempfile.TemporaryDirectory() as td:
            p = _make_passport(Path(td), [{
                "citation_key": "smith2024",
                "title": "Real Paper",
                "authors": [{"family": "Smith"}],
                "year": 2024,
                "source_pointer": "doi:10.5555/abc",
                "doi": "10.5555/abc",
                "obtained_via": "folder-scan",
                "contamination_signals": {
                    "preprint_post_llm_inflection": False,
                    "semantic_scholar_unmatched": False,
                },
            }])
            # OpenAlex: DOI matches → openalex_unmatched=False
            # Crossref: DOI miss, title miss → crossref_unmatched=True
            oa = _make_oa_client(matched_dois=frozenset(["10.5555/abc"]))
            cr = _make_cr_client()

            report = mig.migrate_passport(
                p, oa_client=oa, cr_client=cr, dry_run=False
            )
            self.assertEqual(report["patched"], 1)
            doc = mig.load_passport(p)
            sig = doc["literature_corpus"][0]["contamination_signals"]
            self.assertIs(sig["openalex_unmatched"], False)
            self.assertIs(sig["crossref_unmatched"], True)


# ============================================================================
# 3. Manual entry: untouched entirely
# ============================================================================
class ManualSkipTest(unittest.TestCase):
    def test_manual_entry_skipped_entirely(self) -> None:
        """obtained_via='manual' entries are not modified."""
        with tempfile.TemporaryDirectory() as td:
            p = _make_passport(Path(td), [{
                "citation_key": "manual1",
                "title": "User curated",
                "authors": [{"family": "User"}],
                "year": 2024,
                "source_pointer": "manual:1",
                "obtained_via": "manual",
                "contamination_signals": {
                    "preprint_post_llm_inflection": True,
                },
            }])
            before = p.read_bytes()
            report = mig.migrate_passport(
                p,
                oa_client=_make_oa_client(),
                cr_client=_make_cr_client(),
                dry_run=False,
            )
            after = p.read_bytes()
            self.assertEqual(before, after, "Manual entry was modified")
            self.assertEqual(report["patched"], 0)
            self.assertEqual(report["skipped_manual"], 1)


# ============================================================================
# 4. Pre-v3.7.3 entry: no semantic_scholar_unmatched → out of scope
# ============================================================================
class PreV373SkipTest(unittest.TestCase):
    def test_pre_v3_7_3_entry_skipped(self) -> None:
        """Entry without semantic_scholar_unmatched is out of v3.9.0 scope."""
        with tempfile.TemporaryDirectory() as td:
            p = _make_passport(Path(td), [{
                "citation_key": "legacy1",
                "title": "Old entry",
                "authors": [{"family": "Old"}],
                "year": 2020,
                "source_pointer": "doi:10.5555/old",
                "obtained_via": "folder-scan",
                # No contamination_signals at all.
            }])
            before = p.read_bytes()
            report = mig.migrate_passport(
                p,
                oa_client=_make_oa_client(),
                cr_client=_make_cr_client(),
                dry_run=False,
            )
            after = p.read_bytes()
            self.assertEqual(before, after, "Pre-v3.7.3 entry was modified")
            self.assertEqual(report["patched"], 0)
            self.assertEqual(report["skipped_pre_v3_7_3"], 1)


# ============================================================================
# 5. Idempotency: already-complete entry untouched
# ============================================================================
class IdempotencyTest(unittest.TestCase):
    def test_idempotent_stable_fields(self) -> None:
        """Re-running on a fully-populated entry produces no change."""
        with tempfile.TemporaryDirectory() as td:
            p = _make_passport(Path(td), [{
                "citation_key": "complete",
                "title": "Fully indexed",
                "authors": [{"family": "Yes"}],
                "year": 2024,
                "source_pointer": "doi:10.5555/yes",
                "doi": "10.5555/yes",
                "obtained_via": "folder-scan",
                "contamination_signals": {
                    "preprint_post_llm_inflection": False,
                    "semantic_scholar_unmatched": False,
                    "openalex_unmatched": False,
                    "crossref_unmatched": False,
                },
            }])
            before = p.read_bytes()
            report = mig.migrate_passport(
                p,
                oa_client=_make_oa_client(),
                cr_client=_make_cr_client(),
                dry_run=False,
            )
            after = p.read_bytes()
            self.assertEqual(before, after, "Already-complete entry was modified")
            self.assertEqual(report["patched"], 0)
            self.assertEqual(report["skipped_complete"], 1)


# ============================================================================
# 6. Partial degradation: one field absent, one populated — only fills missing
# ============================================================================
class PartialDegradationTest(unittest.TestCase):
    def test_partial_degradation_fills_only_missing_field(self) -> None:
        """crossref_unmatched already set from prior run, openalex absent.

        OpenAlex now up → openalex_unmatched filled; crossref_unmatched preserved.
        Tests both stable-fields idempotency AND partial-fill eligibility.
        """
        with tempfile.TemporaryDirectory() as td:
            p = _make_passport(Path(td), [{
                "citation_key": "partial",
                "title": "Partial backfill",
                "authors": [{"family": "X"}],
                "year": 2024,
                "source_pointer": "doi:10.5555/p",
                "doi": "10.5555/p",
                "obtained_via": "folder-scan",
                "contamination_signals": {
                    "preprint_post_llm_inflection": False,
                    "semantic_scholar_unmatched": False,
                    "crossref_unmatched": False,  # populated from a prior run
                    # openalex_unmatched absent — to be filled
                },
            }])
            # OpenAlex: DOI match → False
            oa = _make_oa_client(matched_dois=frozenset(["10.5555/p"]))
            cr = _make_cr_client()  # not called (crossref already set)

            report = mig.migrate_passport(
                p, oa_client=oa, cr_client=cr, dry_run=False
            )
            self.assertEqual(report["patched"], 1)

            doc = mig.load_passport(p)
            sig = doc["literature_corpus"][0]["contamination_signals"]
            self.assertIs(sig["openalex_unmatched"], False)   # added
            self.assertIs(sig["crossref_unmatched"], False)   # preserved (not overwritten)

            # Crossref client must NOT have been consulted (field was already set)
            cr.doi_lookup_with_title_check.assert_not_called()
            cr.title_search.assert_not_called()


if __name__ == "__main__":
    unittest.main()
