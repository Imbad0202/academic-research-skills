"""Tests for the citation_extraction self-reducer + full 50-tuple gold-set run.

Pins the #182 Delta 4 reducer branches and the end-to-end accuracy against the
shipped gold set (which was authored by the same rule -> ~1.0 accuracy).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import run_evals

REPO_ROOT = Path(__file__).resolve().parents[1]
CITATION_DIR = REPO_ROOT / "evals" / "gold" / "citation_extraction"


def _ro(crossref="skipped", openalex="skipped", semantic_scholar="skipped", arxiv="skipped"):
    return {
        "crossref": {"status": crossref, "response_summary": None},
        "openalex": {"status": openalex, "response_summary": None},
        "semantic_scholar": {"status": semantic_scholar, "response_summary": None},
        "arxiv": {"status": arxiv, "response_summary": None},
    }


# ---------------------------------------------------------------------------
# Reducer branch pins (#182 Delta 4)
# ---------------------------------------------------------------------------
def test_reducer_matched_wins_true():
    assert run_evals.reduce_lookup_verified(_ro(crossref="matched")) == "true"


def test_reducer_matched_plus_unmatched_still_true():
    # matched WINS even if another applicable resolver returned unmatched.
    assert run_evals.reduce_lookup_verified(
        _ro(crossref="matched", openalex="unmatched")
    ) == "true"


def test_reducer_arxiv_matched_crossref_unmatched_true():
    # valid_arxiv shape: crossref unmatched, arxiv matched -> true (matched wins).
    assert run_evals.reduce_lookup_verified(
        _ro(crossref="unmatched", openalex="matched", semantic_scholar="matched", arxiv="matched")
    ) == "true"


def test_reducer_unmatched_no_matched_false():
    assert run_evals.reduce_lookup_verified(
        _ro(crossref="unmatched", openalex="unmatched", semantic_scholar="unmatched")
    ) == "false"


def test_reducer_partial_outage_unmatched_plus_unreachable_false():
    # Anti-fabrication bias: >=1 unmatched & 0 matched -> false even with outage.
    assert run_evals.reduce_lookup_verified(
        _ro(crossref="unmatched", openalex="unmatched",
            semantic_scholar="unmatched", arxiv="unreachable")
    ) == "false"


def test_reducer_all_skipped_unresolvable():
    # Manual-entry exempt: empty adjudicating set -> unresolvable.
    assert run_evals.reduce_lookup_verified(_ro()) == "unresolvable"


def test_reducer_all_unreachable_unresolvable():
    # Total outage -> unresolvable (NOT false).
    assert run_evals.reduce_lookup_verified(
        _ro(crossref="unreachable", openalex="unreachable",
            semantic_scholar="unreachable", arxiv="unreachable")
    ) == "unresolvable"


def test_reducer_unresolvable_never_collapsed_into_false():
    # Explicit anti-collapse pin: total outage stays unresolvable.
    assert run_evals.reduce_lookup_verified(
        _ro(crossref="unreachable", openalex="unreachable",
            semantic_scholar="unreachable")
    ) != "false"


# ---------------------------------------------------------------------------
# Full 50-tuple gold-set run
# ---------------------------------------------------------------------------
def test_full_gold_set_runs_at_high_accuracy():
    result = run_evals.run_task("citation_extraction")
    assert result["status"] == "measured"
    assert result["sample_n"] == 50
    # Authored by the same reducer rule -> expect ~1.0 accuracy.
    assert result["aggregate_metric"]["value"] == pytest.approx(1.0)
    assert result["aggregate_metric"]["passed"] is True


def test_full_gold_set_per_class_all_pass():
    result = run_evals.run_task("citation_extraction")
    by_class = {pc["class_name"]: pc for pc in result["per_class"]}
    for cls in ("true", "false", "unresolvable"):
        assert by_class[cls]["passed"] is True, cls
    # Distribution: 30 true (20 doi + 10 arxiv), 15 false, 5 unresolvable.
    assert by_class["true"]["support"] == 30
    assert by_class["false"]["support"] == 15
    assert by_class["unresolvable"]["support"] == 5


def test_full_gold_set_reducer_matches_every_expected_label():
    # Independent recompute: the reducer over each tuple's resolver_outcomes
    # must reproduce expected_outcomes' lookup_verified for all 50 tuples.
    expected = json.loads((CITATION_DIR / "expected_outcomes.json").read_text(encoding="utf-8"))
    for tid, outcome in expected.items():
        predicted = run_evals.reduce_lookup_verified(outcome["resolver_outcomes"])
        assert predicted == outcome["lookup_verified"], tid


def test_expert_concordance_present_for_labeled_subset():
    # 10 of 50 tuples carry human_expert_verdict; concordance is advisory.
    result = run_evals.run_task("citation_extraction")
    conc = result.get("expert_concordance", [])
    total_labeled = sum(c["labeled_count"] for c in conc)
    assert total_labeled == 10
