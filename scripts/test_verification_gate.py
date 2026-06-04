#!/usr/bin/env python3
"""Tests for the verification_gate API (Delta 5).

Spec: docs/design/2026-05-21-v3.10-182-promote-citation-gate-spec.md §2 Delta 5.

verify_citation composes the four resolvers, maps each resolver's execution to a
{status, queried_by} outcome, derives lookup_verified via the Delta 4 reducer
(narrowed-false, C-V6(a)), reads anchor_present, and stamps verification_timestamp.
Clients are dependency-injected so tests run without network.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))


def _entry(**overrides):
    # Production-shaped corpus entry: NO anchor field (the v3.7.3 anchor lives in
    # writer prose, joined by ref_slug — passed to verify_citation as an explicit
    # `anchor` param, never read off the corpus entry).
    base = {
        "citation_key": "vaswani2017",
        "ref_slug": "vaswani-2017-attention",
        "title": "Attention Is All You Need",
        "doi": "10.5555/abc",
        "obtained_via": "folder-scan",
    }
    base.update(overrides)
    return base


_PAGE_ANCHOR = {"kind": "page", "value": "1"}


def _clients(*, crossref=None, openalex=None, semantic_scholar=None, arxiv=None):
    """Build a clients dict of MagicMocks. Pass a configured mock per resolver,
    or None to get a default (all lookups miss)."""
    def default():
        m = MagicMock()
        m.doi_lookup_with_title_check.return_value = None
        m.title_search.return_value = None
        m.arxiv_id_lookup.return_value = None
        m.lookup.return_value = {"matched": False}
        return m
    return {
        "crossref": crossref or default(),
        "openalex": openalex or default(),
        "semantic_scholar": semantic_scholar or default(),
        "arxiv": arxiv or default(),
    }


# ---------- verify_citation ----------


def test_matched_yields_true_and_id_queried():
    from verification_gate import verify_citation

    cr = MagicMock()
    cr.doi_lookup_with_title_check.return_value = {"title": ["X"]}  # match
    outcome = verify_citation(_entry(), _clients(crossref=cr))

    assert outcome["lookup_verified"] == "true"
    assert outcome["resolver_outcomes"]["crossref"]["status"] == "matched"
    assert outcome["resolver_outcomes"]["crossref"]["queried_by"] == "id"


def test_id_keyed_unmatched_yields_false():
    from verification_gate import verify_citation
    # All resolvers miss; entry has a DOI → ID-keyed unmatched → false.
    outcome = verify_citation(_entry(), _clients())
    assert outcome["lookup_verified"] == "false"
    assert outcome["resolver_outcomes"]["crossref"]["queried_by"] == "id"


def test_title_only_unmatched_yields_unresolvable():
    from verification_gate import verify_citation
    # No DOI → title-only unmatched everywhere → unresolvable (C-V6(a)).
    outcome = verify_citation(_entry(doi=None), _clients())
    assert outcome["lookup_verified"] == "unresolvable"
    assert outcome["resolver_outcomes"]["crossref"]["queried_by"] == "title"


def test_resolver_outage_is_unreachable():
    from verification_gate import verify_citation
    from crossref_client import CrossrefUnavailable

    cr = MagicMock()
    cr.doi_lookup_with_title_check.side_effect = CrossrefUnavailable("down")
    # other three also miss (id-keyed) → false stands (anti-fabrication bias).
    outcome = verify_citation(_entry(), _clients(crossref=cr))
    assert outcome["resolver_outcomes"]["crossref"]["status"] == "unreachable"
    assert outcome["resolver_outcomes"]["crossref"]["queried_by"] is None
    assert outcome["lookup_verified"] == "false"


def test_all_unreachable_is_unresolvable():
    from verification_gate import verify_citation
    from crossref_client import CrossrefUnavailable
    from openalex_client import OpenAlexUnavailable
    from arxiv_client import ArxivUnavailable
    from contamination_signals import SemanticScholarUnavailable

    cr = MagicMock(); cr.doi_lookup_with_title_check.side_effect = CrossrefUnavailable("x")
    oa = MagicMock(); oa.doi_lookup_with_title_check.side_effect = OpenAlexUnavailable("x")
    s2 = MagicMock(); s2.lookup.side_effect = SemanticScholarUnavailable("x")
    ax = MagicMock(); ax.arxiv_id_lookup.side_effect = ArxivUnavailable("x")
    outcome = verify_citation(
        _entry(arxiv_id="1706.03762"),
        _clients(crossref=cr, openalex=oa, semantic_scholar=s2, arxiv=ax),
    )
    assert outcome["lookup_verified"] == "unresolvable"
    for r in ("crossref", "openalex", "semantic_scholar", "arxiv"):
        assert outcome["resolver_outcomes"][r]["status"] == "unreachable"


def test_manual_entry_all_skipped_unresolvable():
    from verification_gate import verify_citation
    outcome = verify_citation(_entry(obtained_via="manual"), _clients())
    assert outcome["lookup_verified"] == "unresolvable"
    for r in ("crossref", "openalex", "semantic_scholar", "arxiv"):
        assert outcome["resolver_outcomes"][r]["status"] == "skipped"


def test_arxiv_skipped_on_non_arxiv_citation():
    from verification_gate import verify_citation
    cr = MagicMock(); cr.doi_lookup_with_title_check.return_value = {"title": ["X"]}
    outcome = verify_citation(_entry(), _clients(crossref=cr))  # no arxiv_id
    assert outcome["resolver_outcomes"]["arxiv"]["status"] == "skipped"


def test_anchor_present_true_for_page_kind():
    from verification_gate import verify_citation
    # anchor is an EXPLICIT param (prose-sourced, joined by ref_slug upstream).
    outcome = verify_citation(_entry(), _clients(), anchor=_PAGE_ANCHOR)
    assert outcome["anchor_present"] is True


def test_anchor_present_false_for_none_kind():
    from verification_gate import verify_citation
    outcome = verify_citation(
        _entry(), _clients(), anchor={"kind": "none", "value": None})
    assert outcome["anchor_present"] is False


def test_anchor_present_false_when_anchor_omitted():
    from verification_gate import verify_citation
    # No anchor param (the prose join found no anchor for this ref_slug) → False.
    outcome = verify_citation(_entry(), _clients())
    assert outcome["anchor_present"] is False


def test_anchor_is_not_read_off_the_corpus_entry():
    """Anti-regression for the latent shape mismatch: even if a corpus entry
    erroneously carries an 'anchor' key, it MUST be ignored — anchor_present
    derives ONLY from the explicit param. This pins that we don't silently
    resurrect the entry.get('anchor') path (the anchor lives in writer prose,
    not in literature_corpus)."""
    from verification_gate import verify_citation
    e = _entry(anchor={"kind": "page", "value": "99"})  # decoy on the entry
    outcome = verify_citation(e, _clients())  # no anchor param
    assert outcome["anchor_present"] is False


def test_outcome_carries_keys_and_timestamp():
    from verification_gate import verify_citation
    outcome = verify_citation(_entry(), _clients())
    assert outcome["citation_key"] == "vaswani2017"
    assert outcome["ref_slug"] == "vaswani-2017-attention"
    assert outcome["verification_timestamp"]  # never null/empty


def test_outcome_validates_against_summary_schema():
    """The outcome must validate against citation_verification_summary.schema."""
    import json
    from jsonschema import Draft202012Validator
    from verification_gate import verify_citation

    schema = json.loads((
        REPO_ROOT / "shared" / "contracts" / "passport"
        / "citation_verification_summary.schema.json"
    ).read_text(encoding="utf-8"))
    outcome = verify_citation(_entry(), _clients())
    errors = list(Draft202012Validator(schema).iter_errors(outcome))
    assert errors == [], f"outcome must validate: {errors}"


# ---------- verify_passport ----------


def test_verify_passport_runs_each_entry():
    from verification_gate import verify_passport

    cr = MagicMock(); cr.doi_lookup_with_title_check.return_value = {"title": ["X"]}
    passport = {
        "literature_corpus": [
            _entry(citation_key="a", ref_slug="slug-a"),
            _entry(citation_key="b", ref_slug="slug-b", doi=None),
        ]
    }
    outcomes = verify_passport(passport, clients=_clients(crossref=cr))
    assert len(outcomes) == 2
    assert {o["citation_key"] for o in outcomes} == {"a", "b"}


def test_verify_passport_joins_anchors_by_ref_slug():
    """verify_passport performs the prose-marker join: a {ref_slug: anchor} map
    is threaded so each entry's anchor_present reflects ITS ref_slug's anchor.
    Entry 'a' has a page anchor; entry 'b' has none → False."""
    from verification_gate import verify_passport
    passport = {
        "literature_corpus": [
            _entry(citation_key="a", ref_slug="slug-a"),
            _entry(citation_key="b", ref_slug="slug-b"),
        ]
    }
    anchors = {"slug-a": _PAGE_ANCHOR}  # slug-b absent → anchor_present False
    outcomes = verify_passport(passport, clients=_clients(), anchors=anchors)
    by_key = {o["citation_key"]: o for o in outcomes}
    assert by_key["a"]["anchor_present"] is True
    assert by_key["b"]["anchor_present"] is False


def test_verify_passport_empty_corpus():
    from verification_gate import verify_passport
    assert verify_passport({"literature_corpus": []}, clients=_clients()) == []
    assert verify_passport({}, clients=_clients()) == []


def test_cache_argument_is_honest_not_silent_noop():
    """cache wiring at this layer is a forward-decl; passing a non-None cache
    must raise (not silently drop it), so a caller is never misled into
    thinking caching took effect."""
    from verification_gate import verify_citation
    with pytest.raises(NotImplementedError):
        verify_citation(_entry(), _clients(), cache=object())
