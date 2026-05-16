"""D4-c uncited-assertion token-rule detector.

Implements the three-condition rule pinned in
`academic-pipeline/agents/claim_ref_alignment_audit_agent.md`
§"Uncited-assertion detector (D4-c)" and exercised by
`scripts/test_uncited_assertion.py` (T-U1..T-U5).

A sentence becomes an `uncited_assertion` candidate iff ALL THREE hold:

  1. Quantifier-or-empirical-verb present
     (numeric/percent quantifiers `50%`, fuzzy quantifiers `most`/`several`/
     `two-thirds`, or empirical verbs `showed`/`demonstrated`/`observed`/
     `proved`/`confirmed`).
  2. No `<!--ref:slug-->` marker on the sentence.
  3. Not a definitional sentence (`refers to`/`is defined as`/`we define`/
     `for the purposes of`).

D4-c last paragraph: manifest membership does NOT exempt a sentence.
The wrapper `detect_uncited_assertions` preserves caller-supplied
`manifest_claim_id` / `scoped_manifest_id` on every finding so the
downstream pipeline can populate U-INV-4 cross-array integrity.

Cross-sentence ref-marker resolution (spec line 251: "no marker on the
immediately preceding or following clause that the slug could
legitimately attach to") is intentionally NOT handled here. This module
sees one sentence at a time; the surrounding-clause check belongs to
`scripts/claim_audit_pipeline.py::run_audit_pipeline`'s
`uncited_sentences` pre-processing path, which has access to the
adjacent-sentence window.

Detector outputs feed into the existing pipeline routing in
`scripts/claim_audit_pipeline.py::run_audit_pipeline`'s
`uncited_sentences` parameter — this module is the pre-processing
layer that turns raw draft sentences into the dicts the pipeline
expects.
"""
from __future__ import annotations

import re
from typing import Any, Iterable

from scripts._claim_audit_constants import (
    RE_NUMERIC_QUANTIFIER,
    RE_REF_MARKER,
    UNCITED_DEFINITION_PHRASES,
    UNCITED_EMPIRICAL_VERBS,
    UNCITED_FUZZY_QUANTIFIERS,
)

# Whole-word splitter for condition 1 fuzzy / verb matching. Strips
# punctuation so `"showed."` and `"showed,"` both match.
_RE_WORD = re.compile(r"[A-Za-z][A-Za-z-]*")


def _extract_word_tokens(sentence: str) -> list[str]:
    """Lower-cased alphabetic tokens (hyphens kept) for verb / fuzzy match."""
    return [m.group(0).lower() for m in _RE_WORD.finditer(sentence)]


def detect_uncited(sentence: str) -> tuple[bool, list[str]]:
    """Return `(is_candidate, trigger_tokens)` for one sentence.

    Mirrors the pseudocode in the agent prompt. Returns trigger_tokens in
    a deterministic order (numeric matches first in document order, then
    fuzzy quantifiers / verbs in document order) so passport diffs stay
    reproducible.
    """
    # Condition 3 fires first — if the sentence is definitional we never
    # need to inspect quantifier tokens.
    lowered = sentence.lower()
    if any(phrase in lowered for phrase in UNCITED_DEFINITION_PHRASES):
        return False, []

    # Condition 2 — ref marker present means the sentence is properly
    # cited under v3.7.3 Three-Layer Citation Emission.
    if RE_REF_MARKER.search(sentence):
        return False, []

    # Condition 1 — collect every quantifier / verb match in document order.
    # Order is preserved across the two passes (numeric first, then word
    # tokens left-to-right) and duplicates are dropped via order-preserving
    # dedup so passport diffs stay stable when the same token appears
    # twice in one sentence ("50% ... 50%", "showed ... showed").
    matches: list[str] = []
    # Numeric quantifiers preserve original-case substring so `50%` rides
    # through to the passport entry verbatim.
    matches.extend(m.group(0) for m in RE_NUMERIC_QUANTIFIER.finditer(sentence))
    # Fuzzy quantifiers + empirical verbs match on lower-cased whole words.
    triggers = UNCITED_FUZZY_QUANTIFIERS | UNCITED_EMPIRICAL_VERBS
    for token in _extract_word_tokens(sentence):
        if token in triggers:
            matches.append(token)

    trigger_tokens = list(dict.fromkeys(matches))
    return (bool(trigger_tokens), trigger_tokens)


def detect_uncited_assertions(
    sentences: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Filter raw draft sentences down to D4-c candidates.

    Each input dict must carry `sentence_text`; optional fields
    (`section_path`, `manifest_claim_id`, `scoped_manifest_id`,
    `upstream_owner_agent`) are passed through unchanged. The detector
    enriches the dict with `trigger_tokens` (non-empty per U-INV-2) and
    drops sentences that fail any of the three conditions.

    The wrapper does NOT mint `finding_id` / `detected_at` / `rule_version`
    — those are owned by `claim_audit_pipeline._uncited_assertion_entry`
    so the passport-write side stays the single point of authority over
    schema-required fields.
    """
    candidates: list[dict[str, Any]] = []
    for raw in sentences:
        sentence_text = raw.get("sentence_text", "")
        is_candidate, tokens = detect_uncited(sentence_text)
        if not is_candidate:
            continue
        enriched = dict(raw)
        enriched["trigger_tokens"] = tokens
        candidates.append(enriched)
    return candidates


__all__ = ["detect_uncited", "detect_uncited_assertions"]
