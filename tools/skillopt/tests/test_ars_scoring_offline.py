"""Offline plumbing test for the ARS x SkillOpt harness — ZERO API calls.

Validates the only logic the harness must get right independent of any optimizer:
parsing a model answer into ``trigger_advisory`` and scoring/aggregating against
the gold labels. Imports only ``tools.skillopt.ars_scoring`` (pure — no SkillOpt,
no network, no ``ANTHROPIC_API_KEY``), and drives it over the real
``evals/gold/rq_framing_patterns/gold_set.json`` with stubbed model outputs.

Run from the repo root:

    python -m pytest tools/skillopt/tests/test_ars_scoring_offline.py -q
"""
from __future__ import annotations

import json
from pathlib import Path

from tools.skillopt.ars_scoring import (
    BALANCED_ACCURACY_FLOOR,
    NEGATIVE_LABEL,
    POSITIVE_LABEL,
    compute_metrics,
    expected_trigger,
    parse_trigger,
    score_prediction,
)

GOLD_PATH = Path(__file__).resolve().parents[3] / "evals/gold/rq_framing_patterns/gold_set.json"


# ── parse_trigger ──────────────────────────────────────────────────────────
def test_parse_marker_yes_no():
    assert parse_trigger("Reasoning...\nADVISORY: YES") is True
    assert parse_trigger("Reasoning...\nADVISORY: NO") is False
    assert parse_trigger("advisory : true") is True
    assert parse_trigger("ADVISORY=false") is False


def test_parse_json_field():
    assert parse_trigger('{"trigger_advisory": true}') is True
    assert parse_trigger('prose {"trigger_advisory": false} more') is False
    assert parse_trigger('{"trigger_advisory": "yes"}') is True


def test_parse_last_marker_wins():
    # A model that reconsiders mid-answer: the concluding verdict is authoritative.
    assert parse_trigger("ADVISORY: NO ... on reflection ADVISORY: YES") is True


def test_parse_unparseable_returns_none():
    assert parse_trigger("I think this is fine.") is None
    assert parse_trigger("") is None


# ── expected_trigger ───────────────────────────────────────────────────────
def test_expected_trigger_mapping():
    assert expected_trigger(POSITIVE_LABEL) is True
    assert expected_trigger(NEGATIVE_LABEL) is False


# ── score_prediction ───────────────────────────────────────────────────────
def test_score_correct_and_wrong():
    # Correct positive.
    s = score_prediction("ADVISORY: YES", POSITIVE_LABEL)
    assert s["hard"] == 1.0 and s["parsed_ok"] and s["fail_reason"] == ""
    # False negative.
    s = score_prediction("ADVISORY: NO", POSITIVE_LABEL)
    assert s["hard"] == 0.0 and "false_negative" in s["fail_reason"]
    # False positive.
    s = score_prediction("ADVISORY: YES", NEGATIVE_LABEL)
    assert s["hard"] == 0.0 and "false_positive" in s["fail_reason"]


def test_unparseable_scores_as_miss():
    # Unparseable on a positive -> counted as the wrong (negative) prediction.
    s = score_prediction("no verdict here", POSITIVE_LABEL)
    assert s["hard"] == 0.0 and s["parsed_ok"] is False
    assert s["predicted_trigger"] is False


# ── compute_metrics over the real gold set ─────────────────────────────────
def _load_gold():
    items = json.loads(GOLD_PATH.read_text(encoding="utf-8"))["items"]
    assert len(items) == 40, "gold set should hold 40 items"
    return items


def test_perfect_oracle_passes_gate():
    """An oracle that always emits the gold-correct verdict scores 1.0 / passes."""
    records = []
    for it in _load_gold():
        correct = "ADVISORY: YES" if it["label"] == POSITIVE_LABEL else "ADVISORY: NO"
        records.append(score_prediction(correct, it["label"]))
    m = compute_metrics(records)
    assert m["counts"] == {"tp": 20, "tn": 20, "fp": 0, "fn": 0,
                           "positives": 20, "negatives": 20}
    assert m["metrics"]["balanced_accuracy"] == 1.0
    assert m["metrics"]["fnr"] == 0.0 and m["metrics"]["fpr"] == 0.0
    assert m["passes_gate"] is True


def test_borderline_model_fails_gate():
    """A model that over-warns on every domain-native RQ blows the FPR ceiling."""
    records = []
    for it in _load_gold():
        # Always says YES -> all positives caught (FNR 0) but every negative is a FP.
        records.append(score_prediction("ADVISORY: YES", it["label"]))
    m = compute_metrics(records)
    assert m["counts"]["fp"] == 20 and m["counts"]["fn"] == 0
    assert m["metrics"]["fpr"] == 1.0
    assert m["metrics"]["balanced_accuracy"] == 0.5
    assert m["metrics"]["balanced_accuracy"] < BALANCED_ACCURACY_FLOOR
    assert m["passes_gate"] is False
