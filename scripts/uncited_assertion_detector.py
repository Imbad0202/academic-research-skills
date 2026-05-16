"""D4-c uncited-assertion token-rule detector.

Implements the three-condition rule pinned in
`academic-pipeline/agents/claim_ref_alignment_audit_agent.md`
§"Uncited-assertion detector (D4-c)" and exercised by
`scripts/test_uncited_assertion.py` (T-U1..T-U5).

A sentence becomes an `uncited_assertion` candidate iff ALL THREE hold:

  1. Quantifier-or-empirical-verb present
     (numbers `42 participants`, percentages `50%`, explicit quantifiers
     `most`/`several`/`two-thirds`, empirical verbs `showed`/`demonstrated`/
     `observed`/`proved`/`confirmed`). Bare-number matches are filtered by
     a guard pass that rejects years, version triples, and section numbers.
  2. No `<!--ref:slug-->` marker on the sentence.
  3. Not a definitional sentence (`refers to`/`is defined as`/`we define`/
     `for the purposes of`).

D4-c last paragraph: manifest membership does NOT exempt a sentence.
The wrapper `detect_uncited_assertions` preserves caller-supplied
`manifest_claim_id` / `scoped_manifest_id` on every finding so the
downstream pipeline can populate U-INV-4 cross-array integrity.

DEFERRED-CROSS-SENTENCE: Spec line 251 also says "no marker on the
immediately preceding or following clause that the slug could
legitimately attach to". The adjacent-clause check is intentionally
NOT implemented in v3.8 Step 6 — this module sees one sentence at a
time, the pipeline's `uncited_sentences` parameter is caller-injected,
and the Step 9 e2e wiring is where the surrounding-clause window
becomes available. Until Step 9 lands, callers MUST pre-filter
ref-marker-adjacent sentences themselves; otherwise the detector may
produce false positives for sentences whose ref marker sits on the
previous clause. Tracked by spec §"Step 9 — wire detector into e2e".

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
    RE_BARE_NUMERIC_YEAR,
    RE_DOTTED_PAIR,
    RE_DOTTED_TRIPLE_OR_MORE,
    RE_NUMERIC_LEFT_ATTACHED,
    RE_NUMERIC_QUANTIFIER,
    RE_REF_MARKER,
    RE_SECTION_CUE,
    RE_VERSION_PREFIX,
    UNCITED_DEFINITION_PHRASES,
    UNCITED_EMPIRICAL_VERBS,
    UNCITED_FUZZY_QUANTIFIERS,
)

# Whole-word splitter for condition 1 fuzzy / verb matching. Strips
# punctuation so `"showed."` and `"showed,"` both match.
_RE_WORD = re.compile(r"[A-Za-z][A-Za-z-]*")

# Left-context window length for guard pass cue detection. 24 chars covers
# `cf. Section ` and `as shown in Figure ` while avoiding catching cue
# words from a previous clause separated by punctuation.
_GUARD_LEFT_WINDOW = 24


def _is_year_or_version_or_section(
    sentence: str, match_text: str, match_start: int
) -> bool:
    """Guard pass: return True when a bare-number match is NOT a quantifier.

    Four disqualifying shapes:
      1. 4-digit year in plausible academic range (1900-2099).
      2. Dotted X.Y.Z[.W...] form — version triple OR deep section number.
      3. Dotted X.Y form preceded by a section cue (`section`, `figure`,
         `chapter`, `table`, `fig.`, `tbl.`, `step`, `appendix`, `§`) OR
         by `v` (version literal).
      4. Any match (bare or dotted) whose immediate left neighbour is a
         dotted-number suffix like `3.` — handles the case where Python's
         `\\b` does not fire between a letter and a digit (e.g. `v3.7.3`
         has no \\b between `v` and `3`, so RE_NUMERIC_QUANTIFIER starts
         from the SECOND segment `7.3`; this branch reattaches the prefix
         and classifies the full token as a version/section reference).

    Percent (`50%`) and `N of M` matches never reach this guard — the
    caller is responsible for routing only bare-number matches through.
    """
    if RE_BARE_NUMERIC_YEAR.match(match_text):
        return True
    if RE_DOTTED_TRIPLE_OR_MORE.match(match_text):
        # Three-or-more-segment dotted forms are unambiguously version
        # triples or deep section numbers; no quantitative claim ever
        # writes "50.3.1 of participants".
        return True
    if RE_DOTTED_PAIR.match(match_text):
        # Two-segment X.Y is ambiguous — `21.4 years` is a quantifier,
        # `section 3.1` is a section reference. Disambiguate by left
        # context (window of 24 chars before the match).
        left = sentence[max(0, match_start - _GUARD_LEFT_WINDOW) : match_start]
        if RE_SECTION_CUE.search(left) or RE_VERSION_PREFIX.search(left):
            return True
    # Branch 4: reattach a left-side dotted-number prefix that Python's \b
    # failed to separate. RE_NUMERIC_QUANTIFIER consumed every dotted
    # segment to the right of the prefix already, so the only token that
    # can sit immediately before match_start and still belong to the same
    # logical version/section literal is `\d+\.`.
    #
    # Two reattachment shapes:
    #   (i)  Immediate (no whitespace between prefix and match): the
    #        canonical `v3.7.3` shape where the regex starts at `7.3`
    #        because Python's \b cannot separate `v` and `3`.
    #   (ii) Line-wrapped (whitespace between prefix and match): the
    #        codex R2 P1-NEW shape `v3.\n7.3`.
    #
    # Shape (ii) is restricted to dotted matches only — a bare integer
    # after whitespace after a period belongs to the NEXT sentence, not
    # the version triple. `"v3. 7 participants withdrew."` is two
    # statements: a version reference (the `v3.` is a section end) and
    # a quantitative claim about 7 participants. Without this restriction
    # branch 4 swallowed the legitimate 7-participant count (codex R3
    # P2-NEW-B).
    if match_start > 0:
        # Shape (i) — immediate left `.` always reattaches.
        if sentence[match_start - 1] == ".":
            left_search_start = max(0, match_start - _GUARD_LEFT_WINDOW)
            left = sentence[left_search_start:match_start]
            if RE_NUMERIC_LEFT_ATTACHED.search(left):
                return True
        # Shape (ii) — whitespace-separated only for dotted right tails.
        elif "." in match_text and sentence[match_start - 1].isspace():
            scan_idx = match_start - 1
            while scan_idx > 0 and sentence[scan_idx].isspace():
                scan_idx -= 1
            if sentence[scan_idx] == ".":
                left_search_start = max(0, scan_idx + 1 - _GUARD_LEFT_WINDOW)
                left = sentence[left_search_start : scan_idx + 1]
                if RE_NUMERIC_LEFT_ATTACHED.search(left):
                    return True
    return False


def detect_uncited(sentence: str) -> tuple[bool, list[str]]:
    """Return `(is_candidate, trigger_tokens)` for one sentence.

    Trigger tokens are returned in document order (left-to-right in the
    source sentence) so passport diffs and human review stay aligned with
    reader expectations. Duplicates are dropped via order-preserving
    dedup so `"showed ... showed ... showed"` produces one token.
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

    # Condition 1 — collect every quantifier / verb match with its byte
    # offset so the final token list reflects document order regardless
    # of which regex / pass produced it.
    matches: list[tuple[int, str]] = []
    for m in RE_NUMERIC_QUANTIFIER.finditer(sentence):
        text = m.group(0)
        # Percent and `N of M` matches always pass through; only bare-
        # number matches need the year/version/section guard. The two
        # qualified shapes are distinguishable by character content:
        # percent ends with `%`, `N of M` contains ` of `.
        if "%" not in text and " of " not in text:
            if _is_year_or_version_or_section(sentence, text, m.start()):
                continue
        matches.append((m.start(), text))

    # Fuzzy quantifiers + empirical verbs match on lower-cased whole words.
    triggers = UNCITED_FUZZY_QUANTIFIERS | UNCITED_EMPIRICAL_VERBS
    for m in _RE_WORD.finditer(sentence):
        token = m.group(0).lower()
        if token in triggers:
            matches.append((m.start(), token))

    # Sort by source offset, then dedup preserving first occurrence.
    matches.sort(key=lambda pair: pair[0])
    trigger_tokens = list(dict.fromkeys(token for _, token in matches))
    return (bool(trigger_tokens), trigger_tokens)


def detect_uncited_assertions(
    sentences: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Filter raw draft sentences down to D4-c candidates.

    Each input dict MUST carry a non-empty string `sentence_text`. Missing
    or non-string `sentence_text` raises `ValueError` — silently treating
    bad input as empty would let upstream bugs masquerade as
    "no findings", which is the worst possible failure mode for an audit
    pipeline.

    Optional fields (`section_path`, `manifest_claim_id`,
    `scoped_manifest_id`, `upstream_owner_agent`) pass through unchanged.
    The detector enriches the candidate dict with `trigger_tokens`
    (non-empty per U-INV-2) and drops sentences that fail any of the
    three D4-c conditions.

    The wrapper does NOT mint `finding_id` / `detected_at` / `rule_version`
    — those are owned by `claim_audit_pipeline._uncited_assertion_entry`
    so the passport-write side stays the single point of authority over
    schema-required fields.
    """
    candidates: list[dict[str, Any]] = []
    for index, raw in enumerate(sentences):
        if "sentence_text" not in raw:
            raise ValueError(
                f"detect_uncited_assertions: sentences[{index}] missing "
                "required 'sentence_text' key"
            )
        sentence_text = raw["sentence_text"]
        if not isinstance(sentence_text, str):
            raise ValueError(
                f"detect_uncited_assertions: sentences[{index}]['sentence_text'] "
                f"must be str, got {type(sentence_text).__name__}"
            )
        is_candidate, tokens = detect_uncited(sentence_text)
        if not is_candidate:
            continue
        enriched = dict(raw)
        enriched["trigger_tokens"] = tokens
        candidates.append(enriched)
    return candidates


__all__ = ["detect_uncited", "detect_uncited_assertions"]
