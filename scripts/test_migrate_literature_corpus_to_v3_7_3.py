#!/usr/bin/env python3
"""#105 v3.7.3 contamination_signals backfill migration tool tests.

Tests scripts/migrate_literature_corpus_to_v3_7_3.py — the CLI that
backfills `contamination_signals` on pre-v3.7.3 literature_corpus[]
entries per v3.7.3 spec §3.2 R-L3-2-B.

Design: docs/design/2026-05-15-issue-105-contamination-signals-backfill-design.md
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import migrate_literature_corpus_to_v3_7_3 as mig  # noqa: E402


SAMPLE_PASSPORT_YAML = """\
# Material Passport for the SLR run
origin_skill: deep-research
origin_mode: systematic-review
origin_date: '2026-05-01T10:00:00Z'
verification_status: VERIFIED
version_label: research_v1
literature_corpus:
  - citation_key: chen2024ai
    title: AI in education
    authors:
      - family: Chen
        given: A
    year: 2024
    venue: arXiv
    doi: 10.1234/abc
    obtained_via: folder-scan
    source_pointer: file:///refs/chen2024.pdf
  - citation_key: smith2020old
    title: Old paper
    authors:
      - family: Smith
        given: B
    year: 2020
    venue: Nature
    doi: 10.5678/def
    obtained_via: folder-scan
    source_pointer: file:///refs/smith2020.pdf
  - citation_key: lopez2024manual
    title: Manual entry
    authors:
      - family: Lopez
        given: C
    year: 2024
    venue: bioRxiv
    obtained_via: manual
    source_pointer: file:///refs/lopez2024.pdf
"""


def _make_ss_client(unmatched_for_keys=()):
    """Build a mock SS client that returns no-match for the listed citation
    keys (so the entry gets semantic_scholar_unmatched: true) and match
    otherwise."""
    client = MagicMock()
    def lookup(entry):
        return {"matched": entry.get("citation_key") not in set(unmatched_for_keys)}
    client.lookup.side_effect = lookup
    return client


# ============================================================================
# Single-passport migration
# ============================================================================
class SinglePassportMigrationTest(unittest.TestCase):
    def test_dry_run_writes_no_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "passport.yaml"
            p.write_text(SAMPLE_PASSPORT_YAML)
            before = p.read_text()
            report = mig.migrate_passport(
                p, ss_client=_make_ss_client(), dry_run=True
            )
            after = p.read_text()
            self.assertEqual(before, after, "dry-run must not write")
            self.assertEqual(report["patched"], 3)
            self.assertEqual(report["manual_unmatched_omitted"], 1)

    def test_patches_three_entries_per_emission_rules(self) -> None:
        """Per spec §3.2: emit object on every non-skipped entry, even
        when both signals are False (computed-and-clean is distinct from
        not-computed). All 3 sample entries get the object; manual entry
        omits the unmatched field."""
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "passport.yaml"
            p.write_text(SAMPLE_PASSPORT_YAML)
            report = mig.migrate_passport(
                p,
                ss_client=_make_ss_client(unmatched_for_keys=["chen2024ai"]),
                dry_run=False,
            )
            self.assertEqual(report["patched"], 3)
            doc = mig.load_passport(p)
            entries = doc["literature_corpus"]
            # chen2024ai: arXiv 2024 → preprint=true; SS no-match → unmatched=true
            chen = entries[0]
            self.assertEqual(
                chen["contamination_signals"],
                {"preprint_post_llm_inflection": True, "semantic_scholar_unmatched": True},
            )
            self.assertIn("contamination_signals_backfilled_at", chen)
            # smith2020old: Nature 2020 → preprint=false; SS match → unmatched=false
            smith = entries[1]
            self.assertEqual(
                smith["contamination_signals"],
                {"preprint_post_llm_inflection": False, "semantic_scholar_unmatched": False},
            )
            # lopez2024manual: bioRxiv 2024 manual → preprint=true; unmatched OMITTED
            lopez = entries[2]
            self.assertEqual(
                lopez["contamination_signals"],
                {"preprint_post_llm_inflection": True},
            )
            self.assertNotIn("semantic_scholar_unmatched", lopez["contamination_signals"])

    def test_idempotency_already_migrated_entry_skipped(self) -> None:
        """Re-running on an already-migrated entry must not re-compute,
        re-write, or update the backfilled_at timestamp."""
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "passport.yaml"
            p.write_text(SAMPLE_PASSPORT_YAML)
            mig.migrate_passport(p, ss_client=_make_ss_client(), dry_run=False)
            after_first = p.read_text()
            report = mig.migrate_passport(
                p, ss_client=_make_ss_client(), dry_run=False
            )
            after_second = p.read_text()
            self.assertEqual(report["patched"], 0)
            self.assertEqual(report["skipped_already_migrated"], 3)
            self.assertEqual(
                after_first, after_second,
                "re-run on migrated passport must be byte-identical",
            )

    def test_insufficient_data_missing_venue_skipped(self) -> None:
        """An entry missing venue cannot have Signal 1 reliably emitted
        as False — that would be a half-truth (we don't know if the
        venue is a preprint server). Per spec §3.2 emission rules,
        'computed and clean' must be distinguished from 'not computed'.
        v3.7.3 codex F3 closure (simplify round)."""
        yaml_no_venue = """\
origin_skill: deep-research
literature_corpus:
  - citation_key: novenue2024
    title: No venue
    authors:
      - family: X
        given: Y
    year: 2024
    obtained_via: folder-scan
    source_pointer: file:///refs/novenue.pdf
"""
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "passport.yaml"
            p.write_text(yaml_no_venue)
            report = mig.migrate_passport(
                p, ss_client=_make_ss_client(), dry_run=False
            )
            self.assertEqual(report["patched"], 0)
            self.assertEqual(report["skipped_insufficient_data"], 1)

    def test_insufficient_data_entry_skipped(self) -> None:
        """An entry missing year cannot have Signal 1 computed reliably
        (year is in the AND); migration tool skips and logs the reason
        rather than emitting half-truth."""
        yaml_no_year = """\
origin_skill: deep-research
literature_corpus:
  - citation_key: noyear2024
    title: No year
    authors:
      - family: X
        given: Y
    venue: arXiv
    obtained_via: folder-scan
    source_pointer: file:///refs/noyear.pdf
"""
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "passport.yaml"
            p.write_text(yaml_no_year)
            # Note: schema-invalid passport — `year` is required. This test
            # exercises the migration tool's defensive behavior, not the
            # schema validator. Real corpora won't reach here, but if they
            # do (e.g., user hand-edited their YAML), we degrade gracefully.
            report = mig.migrate_passport(
                p, ss_client=_make_ss_client(), dry_run=False
            )
            self.assertEqual(report["patched"], 0)
            self.assertEqual(report["skipped_insufficient_data"], 1)

    def test_passport_without_literature_corpus_returns_zero_report(self) -> None:
        yaml_no_corpus = """\
origin_skill: deep-research
verification_status: VERIFIED
"""
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "passport.yaml"
            p.write_text(yaml_no_corpus)
            report = mig.migrate_passport(
                p, ss_client=_make_ss_client(), dry_run=False
            )
            self.assertEqual(report["processed"], 0)
            self.assertEqual(report["patched"], 0)


# ============================================================================
# Directory-scan mode
# ============================================================================
class DirectoryScanTest(unittest.TestCase):
    def test_scan_dir_finds_yaml_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "passport_a.yaml").write_text(SAMPLE_PASSPORT_YAML)
            (d / "passport_b.yaml").write_text(SAMPLE_PASSPORT_YAML)
            (d / "notes.txt").write_text("ignore me")
            paths = sorted(mig.discover_passports(d))
            self.assertEqual(
                [p.name for p in paths],
                ["passport_a.yaml", "passport_b.yaml"],
            )

    def test_scan_dir_is_non_recursive(self) -> None:
        """Per design §4.2: directory scan finds *.yaml non-recursively.
        A passport in a subdir is intentionally NOT discovered."""
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "passport.yaml").write_text(SAMPLE_PASSPORT_YAML)
            sub = d / "subdir"
            sub.mkdir()
            (sub / "nested.yaml").write_text(SAMPLE_PASSPORT_YAML)
            paths = sorted(mig.discover_passports(d))
            self.assertEqual([p.name for p in paths], ["passport.yaml"])

    def test_migrate_dir_runs_each_passport(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            for name in ("a.yaml", "b.yaml"):
                (d / name).write_text(SAMPLE_PASSPORT_YAML)
            client = _make_ss_client(unmatched_for_keys=["chen2024ai"])
            agg = mig.migrate_directory(d, ss_client=client, dry_run=False)
            self.assertEqual(agg["files_processed"], 2)
            self.assertEqual(agg["entries_patched"], 6)  # 3 per passport × 2


# ============================================================================
# Comment + key-order preservation (ruamel.yaml round-trip)
# ============================================================================
class RoundTripPreservationTest(unittest.TestCase):
    def test_comments_preserved_after_migration(self) -> None:
        yaml_with_comments = """\
# Top-level comment about this passport
origin_skill: deep-research
literature_corpus:
  - citation_key: chen2024ai  # inline note about chen
    title: AI in education
    authors:
      - family: Chen
        given: A
    year: 2024
    venue: arXiv
    obtained_via: folder-scan
    source_pointer: file:///refs/chen2024.pdf
"""
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "passport.yaml"
            p.write_text(yaml_with_comments)
            mig.migrate_passport(p, ss_client=_make_ss_client(), dry_run=False)
            after = p.read_text()
            self.assertIn("# Top-level comment", after)
            self.assertIn("# inline note about chen", after)


if __name__ == "__main__":
    unittest.main()
