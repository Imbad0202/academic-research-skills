from __future__ import annotations

import copy

import pytest

from scripts import build_claim_standing_candidate_ledger as ledger
from scripts import claim_standing_stance_runner as runner
from scripts import render_claim_standing_view as view
from scripts.test_build_claim_standing_candidate_ledger import (
    _rehash_input,
    _retained,
)
from scripts.test_claim_standing_stance_runner import FakeTransport, _stance_setup

FORBIDDEN_PHRASES = (
    "scientific consensus",
    "field-level standing",
    "verified true",
    "verified false",
    "credibility score",
    "trust score",
    "confidence score",
    "complete search",
    "none exist",
    "the field agrees",
    "the literature establishes",
)
EMPTY_CATEGORIES = (
    "contradict",
    "mixed",
    "not_addressed",
    "INSUFFICIENT_EVIDENCE",
    "AMBIGUOUS",
    "not_checked",
)


def _full_setup():
    plan, ledger_value = _stance_setup()
    record, evidence_rows = runner.run_stance(
        plan, ledger_value, transport=FakeTransport()
    )
    return plan, ledger_value, record, evidence_rows


def test_full_view_carries_banner_three_parts_and_fixed_wording():
    plan, ledger_value, record, evidence_rows = _full_setup()
    text = view.render_view(plan, ledger_value, record, evidence_rows)
    lines = text.splitlines()
    assert lines[0] == "STANCE CLASSIFICATION UNMEASURED"
    for heading in (
        "## Consent and recorded search",
        "## Candidate ledger",
        "## Claim standing (advisory)",
    ):
        assert heading in text
    assert (
        "Within the recorded search of arxiv, crossref, index-a using q1, "
        "1/1 selected candidates were classified support." in text
        or "1/1 selected candidates were classified support." in text
    )
    for category in EMPTY_CATEGORIES:
        assert (
            f"No {category} sources were found among the selected candidates "
            "within this recorded search." in text
        )
    assert "0/1 selected candidates were not checked or failed" in text
    assert "ABSTRACT" in text
    assert "duplicate_version" in text
    assert "not_relevant" in text
    assert "service_unavailable" in text
    assert "secondary" in text.lower()


def test_view_never_uses_forbidden_vocabulary():
    plan, ledger_value, record, evidence_rows = _full_setup()
    text = view.render_view(plan, ledger_value, record, evidence_rows).lower()
    for phrase in FORBIDDEN_PHRASES:
        assert phrase not in text


def test_provider_text_renders_inert():
    plan, ledger_value, record, evidence_rows = _full_setup()
    tampered = copy.deepcopy(ledger_value)
    for hit in tampered["raw_hits"]:
        if hit["raw_hit_id"] == record["rows"][0]["canonical_raw_hit_id"]:
            hit["title"] = 'Reminder <script>alert("x")</script> Effects'
    tampered["candidate_ledger_sha256"] = ledger.bound_digest(
        tampered, "candidate_ledger_sha256"
    )
    text = view.render_view(plan, tampered, None, [])
    assert "<script>" not in text
    assert "&lt;script&gt;" in text


def test_stale_stance_record_refuses_to_render():
    plan, ledger_value, record, evidence_rows = _full_setup()
    tampered = copy.deepcopy(ledger_value)
    tampered["raw_hits"][0]["title"] = "Silently swapped title"
    tampered["candidate_ledger_sha256"] = ledger.bound_digest(
        tampered, "candidate_ledger_sha256"
    )
    with pytest.raises(runner.StanceError, match="stale|candidate_ledger"):
        view.render_view(plan, tampered, record, evidence_rows)


def test_retrieval_only_view_renders_without_a_stance_record():
    plan, ledger_value, _, _ = _full_setup()
    text = view.render_view(plan, ledger_value, None, [])
    assert text.splitlines()[0] == "STANCE CLASSIFICATION UNMEASURED"
    assert "## Consent and recorded search" in text
    assert "## Candidate ledger" in text
    assert "Stance classification was not run under this consent." in text
