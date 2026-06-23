"""Pure scoring helpers for the ARS x SkillOpt rq_framing_patterns harness.

This module has **no SkillOpt dependency and makes no model calls**. It holds the
two things the harness must get right regardless of which optimizer runs on top:

  1. turning a target model's free-text answer into a ``trigger_advisory`` boolean
     (:func:`parse_trigger`), and
  2. scoring + aggregating those predictions against the gold labels with the
     *same* metric definition ARS's own checker uses
     (:func:`score_prediction`, :func:`compute_metrics`).

Keeping this layer pure means it is unit-testable offline (see
``tests/test_ars_scoring_offline.py``) — no ``ANTHROPIC_API_KEY``, no network, no
SkillOpt install. The SkillOpt-facing glue (``ars_adapter.py`` / ``ars_gold_loader.py``)
imports these functions; it never re-implements them.

The metric mirrors ``scripts/check_rq_framing_patterns.py`` exactly: a
``wording_cliche`` item is a positive (the advisory *should* fire), a
``domain_native`` item is a negative (it should *not*), and the acceptance gate is
FNR < 0.30, FPR < 0.20, balanced accuracy >= 0.75.
"""
from __future__ import annotations

import json
import re
from typing import Any, Iterable

# Label vocabulary — must match evals/gold/rq_framing_patterns/gold_set.json.
POSITIVE_LABEL = "wording_cliche"
NEGATIVE_LABEL = "domain_native"

# Acceptance thresholds — must match scripts/check_rq_framing_patterns.py and the
# task manifest (evals/gold/rq_framing_patterns/manifest.yaml).
FNR_CEILING = 0.30
FPR_CEILING = 0.20
BALANCED_ACCURACY_FLOOR = 0.75

# Final-line marker the seed skill instructs the model to emit, e.g. "ADVISORY: YES".
_MARKER_RE = re.compile(r"ADVISORY\s*[:=]\s*(YES|NO|TRUE|FALSE|TRIGGER|PASS)\b", re.IGNORECASE)
_TRUEY = {"yes", "true", "trigger"}
_FALSEY = {"no", "false", "pass"}


def expected_trigger(label: str) -> bool:
    """Ground-truth ``trigger_advisory`` for a gold label.

    ``wording_cliche`` -> the advisory should fire (positive);
    ``domain_native`` -> it should not (negative).
    """
    if label == POSITIVE_LABEL:
        return True
    if label == NEGATIVE_LABEL:
        return False
    raise ValueError(f"unknown label {label!r}; expected one of "
                     f"{POSITIVE_LABEL!r} / {NEGATIVE_LABEL!r}")


def parse_trigger(model_output: str) -> bool | None:
    """Extract ``trigger_advisory`` from a target model's free-text answer.

    Two formats are accepted, tried in order:

      1. A JSON object anywhere in the text carrying a ``trigger_advisory``
         boolean (or "yes"/"no"/"true"/"false" string), e.g.
         ``{"trigger_advisory": true, "pattern": "impact/effect frame"}``.
      2. A final-line marker, e.g. ``ADVISORY: YES`` / ``ADVISORY: NO``.

    Returns ``None`` when neither is present, so the caller can record an
    unparseable rollout rather than silently scoring it as a negative.
    """
    if not model_output:
        return None

    # 1) JSON object with a trigger_advisory field (scan all {...} candidates).
    for candidate in re.findall(r"\{[^{}]*\}", model_output, re.DOTALL):
        try:
            obj = json.loads(candidate)
        except (ValueError, TypeError):
            continue
        if isinstance(obj, dict) and "trigger_advisory" in obj:
            val = obj["trigger_advisory"]
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                low = val.strip().lower()
                if low in _TRUEY:
                    return True
                if low in _FALSEY:
                    return False

    # 2) Final-line marker — last marker wins (the model's concluding verdict).
    markers = _MARKER_RE.findall(model_output)
    if markers:
        return markers[-1].lower() in _TRUEY

    return None


def score_prediction(model_output: str, label: str) -> dict[str, Any]:
    """Score one rollout output against its gold label.

    Returns a dict shaped for SkillOpt's rollout contract: ``hard`` (0/1) and
    ``soft`` (float in [0, 1]) plus diagnostic fields used by reflection and by
    :func:`compute_metrics`. An unparseable answer counts as a wrong prediction
    on the side opposite the truth, so the optimizer is pressured to fix format
    drift too.
    """
    exp = expected_trigger(label)
    parsed = parse_trigger(model_output)
    if parsed is None:
        predicted = not exp  # unparseable == wrong, whichever way truth points
        parsed_ok = False
        fail_reason = "unparseable: no trigger_advisory JSON field or ADVISORY marker"
    else:
        predicted = parsed
        parsed_ok = True
        fail_reason = "" if predicted == exp else (
            "false_negative (missed wording cliche)" if exp else
            "false_positive (over-warned on domain-native RQ)")

    hard = 1.0 if predicted == exp else 0.0
    return {
        "hard": hard,
        "soft": hard,  # binary task: soft == hard
        "predicted_trigger": predicted,
        "expected_trigger": exp,
        "parsed_ok": parsed_ok,
        "fail_reason": fail_reason,
    }


def compute_metrics(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate scored records into the ARS rq_framing_patterns metric block.

    Each record must carry ``predicted_trigger`` (bool) and ``expected_trigger``
    (bool) — exactly what :func:`score_prediction` returns. The output mirrors
    ``scripts/check_rq_framing_patterns.py``: tp/tn/fp/fn counts, FNR, FPR,
    balanced accuracy, and a ``passes_gate`` flag against the binding thresholds.
    """
    tp = tn = fp = fn = 0
    for rec in records:
        predicted = bool(rec["predicted_trigger"])
        actual = bool(rec["expected_trigger"])
        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and actual:
            fn += 1
        else:
            tn += 1

    positives = tp + fn
    negatives = tn + fp
    fnr = fn / positives if positives else 0.0
    fpr = fp / negatives if negatives else 0.0
    tpr = tp / positives if positives else 0.0
    tnr = tn / negatives if negatives else 0.0
    balanced_accuracy = (tpr + tnr) / 2 if positives and negatives else 0.0

    passes_gate = (
        positives > 0
        and negatives > 0
        and fnr < FNR_CEILING
        and fpr < FPR_CEILING
        and balanced_accuracy >= BALANCED_ACCURACY_FLOOR
    )

    return {
        "counts": {"tp": tp, "tn": tn, "fp": fp, "fn": fn,
                   "positives": positives, "negatives": negatives},
        "metrics": {"fnr": fnr, "fpr": fpr, "balanced_accuracy": balanced_accuracy},
        "passes_gate": passes_gate,
    }
