#!/usr/bin/env python3
"""Prompt pin for #1146 — Tier 0 wording matches the resolver script gate.

The title check passes when the two titles are equal under any of the three
forms in ``exact_normalized_title`` (base, dotted-acronym, or Chinese-aware
when both titles contain a Han ideograph). Tier 0 (``S2_VERIFIED``) also
requires a case-insensitive first-author family name, and fails if either
side has no author. Both that author comparison and exact-title verification
on a DOI candidate are prompt-only: the scripts do not compare authors, and
``_lookup_by_doi`` returns ``matched`` once the DOI title score clears its
threshold. ``_similarity`` returns 1.0 for a Chinese-aware exact match and
otherwise the higher of the base and dotted-acronym
``difflib.SequenceMatcher.ratio()`` scores. ``DOI_MISMATCH`` fires only below
0.70. Year only breaks ties after both checks.

Run:
    PYTHONPATH=. python -m pytest scripts/test_tier0_title_gate_prompt_sync.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AGENT = REPO_ROOT / "deep-research" / "agents" / "source_verification_agent.md"
PROTOCOL = (
    REPO_ROOT / "deep-research" / "references" / "semantic_scholar_api_protocol.md"
)

TITLE_FORMS = (
    "The title check passes if the two titles are equal under any of the three forms "
    "used by `exact_normalized_title` in `scripts/_text_similarity.py`. "
    "The base form lowercases, replaces ASCII punctuation with spaces, and collapses and trims whitespace. "
    "The dotted-acronym form first removes the dots in a run that starts at a word boundary and consists of two or more contiguous dotted ASCII letters, "
    "then applies the base form (`R.A.G.` equals `RAG`). "
    "When both titles contain a Han ideograph in U+4E00-U+9FFF, `_cjk_titles_match` also accepts equal, nonempty Chinese-aware forms. "
    "This form folds fullwidth ASCII (`甲Ａ` equals `甲A`), strips one of the wrapper pairs `《》`, `「」`, `『』`, `【】`, `“”`, or `‘’` only when that pair encloses the whole title, "
    "strips the terminal marks `。` and `.`, normalizes whitespace, removes spaces touching Han characters, and preserves letter case."
)
DECISION = (
    "A generic query title such as `Editorial`, `Introduction`, or `Book Review` cannot pass by title search and requires a DOI lookup. "
    "For every title-search result, check both the exact normalized title and the first author's family name against the reference. "
    "Compare family names case-insensitively. If either side has no author, the author check fails. "
    "Only after checking every result, use matching year as a tie-break among those that pass both checks. "
    "Year is not a pass condition."
)
RESOLVER_YEAR = (
    "The resolver's title-search scoring in `scripts/semantic_scholar_client.py` adds 0.05 when the year is equal "
    "among candidates that already have an exact normalized title, and it never rejects a candidate for the year; "
    "that scoring does not compare authors."
)
CONJUNCTION = (
    "A candidate passes Tier 0 (`S2_VERIFIED`) only when its returned title is an exact normalized match "
    "for the reference title and its first author's family name matches the reference's first author's family name "
    "case-insensitively. If either side has no author, the check fails."
)
PROMPT_LEVEL = (
    "Both the first-author comparison on either path and exact-title verification on a DOI candidate "
    "are prompt-level requirements. The scripts do not compare authors. "
    "`_lookup_by_doi` returns `matched: True` once the DOI title cross-check clears its threshold "
    "(`scripts/semantic_scholar_client.py`)."
)
DOI_SENTENCE = (
    "A DOI candidate at or above 0.70 whose title is not an exact normalized match "
    "does not trigger `DOI_MISMATCH` and does not pass Tier 0."
)
SIMILARITY = (
    "The title score is `_similarity` in `scripts/_text_similarity.py`. "
    "It returns `1.0` for a Chinese-aware exact match and otherwise takes the higher of the base and "
    "dotted-acronym `difflib.SequenceMatcher.ratio()` scores, not a Levenshtein distance. "
    "The helper now accepts the three forms; only the threshold stayed at 0.70."
)
NO_MATCH = (
    "If the reference has a DOI, classify it as `S2_NOT_FOUND` when the DOI lookup returns no candidate. "
    "If the reference has no DOI, classify it as `S2_NOT_FOUND` when its title is generic, or when title search returns no candidate with an exact normalized title."
)
FAIL_BULLET = "- References that FAIL Tier 0 MUST proceed through Tier 1 + Tier 2."
ID_SENTENCE = (
    "Record `semantic_scholar_id` in the verification audit trail for deduplication "
    "only when the reference passes Tier 0."
)
MATCH_SCORE = (
    "`match_score`: title similarity returned by `_similarity` in `scripts/_text_similarity.py` "
    "(see Pattern 2). It is the title score, before any year preference."
)


def _between(text: str, start: str, end: str) -> str:
    start_at = text.index(start)
    end_at = text.index(end, start_at + len(start))
    return text[start_at:end_at]


def _line_starting(text: str, prefix: str) -> str:
    for line in text.splitlines():
        if line.startswith(prefix):
            return line
    raise AssertionError(f"no line starts with {prefix!r}")


def test_tier0_section_requires_exact_title_and_first_author() -> None:
    """The acceptance bullet states the three forms, the author check, and the
    year tie-break. The failure bullet keeps MUST. The id is recorded only on
    a Tier 0 pass. ``>= 0.70`` is not an accept rule."""
    section = _between(
        AGENT.read_text(encoding="utf-8"),
        "#### Tier 0",
        "#### Tier 1",
    )
    acceptance = _line_starting(section, "- The title check passes if")
    for clause in (TITLE_FORMS, DECISION, RESOLVER_YEAR, CONJUNCTION, PROMPT_LEVEL):
        assert clause in acceptance
    assert "Attention Is All You Need" in acceptance
    assert "0.70" not in acceptance
    assert ">= 0.70" not in section
    assert "Levenshtein title similarity" not in section

    assert _line_starting(section, "- References that FAIL Tier 0") == FAIL_BULLET
    assert _line_starting(section, "- Record `semantic_scholar_id`") == "- " + ID_SENTENCE
    skip = _line_starting(section, "- References that PASS Tier 0")
    assert "may skip the Tier 2 WebSearch spot-check" in skip


def test_s2_verified_row_names_exact_title_not_a_threshold() -> None:
    """The outcome row, read only up to any arrow, does not cite 0.70."""
    row = ""
    for line in AGENT.read_text(encoding="utf-8").splitlines():
        if line.startswith("- `S2_VERIFIED`:"):
            row = line.split("→", 1)[0]
            break
    assert row, "S2_VERIFIED row missing"
    assert "0.70" not in row
    assert (
        "exact normalized title + case-insensitive first-author family name"
    ) in row
    assert "Levenshtein" not in row
    assert "year match" not in row


def test_pattern1_names_exact_normalized_title_and_not_a_threshold() -> None:
    protocol = PROTOCOL.read_text(encoding="utf-8")
    pattern1 = _between(protocol, "### Pattern 1:", "### Pattern 2:")
    for clause in (TITLE_FORMS, DECISION, RESOLVER_YEAR):
        assert clause in pattern1
    assert (
        "Title search has required an exact normalized title since #431, "
        "and the helper now accepts the three forms."
    ) in pattern1
    assert "applied this title check to title-search results since #431" not in pattern1
    assert "exact_normalized_title" in pattern1
    assert ">= 0.70" not in pattern1
    assert "Accept if similarity >= 0.70" not in pattern1
    assert "Attention Is All You Need" in pattern1
    assert "0.926" in pattern1
    assert "not a Levenshtein distance" in pattern1
    author_at = pattern1.index(
        "check both the exact normalized title and the first author's family name"
    )
    year_at = pattern1.index("use matching year as a tie-break")
    assert author_at < year_at

    no_match = _between(protocol, "### On no match", "### On API failure")
    assert NO_MATCH in no_match
    assert "Levenshtein" not in no_match
    assert "0.70" not in no_match


def test_doi_mismatch_sentence_keeps_the_script_threshold() -> None:
    """DOI_MISMATCH still fires below 0.70. A non-exact title at or above
    0.70 is neither that flag nor a Tier 0 pass. The pass block has no
    threshold."""
    protocol = PROTOCOL.read_text(encoding="utf-8")
    pattern2 = _between(protocol, "### Pattern 2:", "### Pattern 3:")
    assert "If the title score is below 0.70, flag as `DOI_MISMATCH`" in pattern2
    assert SIMILARITY in pattern2
    assert DOI_SENTENCE in pattern2
    assert "#431 did not change" not in pattern2
    assert "is a match" not in pattern2

    agent = AGENT.read_text(encoding="utf-8")
    doi_line = _line_starting(agent, "**DOI mismatch")
    assert (
        "If a DOI resolves in S2 but the returned title's score is below 0.70 "
        "against the reference title, flag as `DOI_MISMATCH`"
    ) in doi_line
    assert "Compound Deception Pattern #5" in doi_line
    assert SIMILARITY in doi_line
    assert DOI_SENTENCE in doi_line
    assert "#431 did not change" not in doi_line

    tier0_pass = _between(protocol, "**Tier 0 pass", "\n---")
    assert CONJUNCTION in tier0_pass
    assert PROMPT_LEVEL in tier0_pass
    assert "do not compare authors" in tier0_pass
    assert "exact-title verification on a DOI candidate" in tier0_pass
    assert (
        "A candidate that fails only the prompt-level title or author requirement is rejected "
        "without being classified as `S2_NOT_FOUND` or `DOI_MISMATCH`. "
        "If no candidate passes Tier 0, the reference proceeds to Tier 1 + Tier 2. "
        "A failed candidate does not by itself send on a reference that another candidate passes."
    ) in tier0_pass
    assert "not a pass condition" in tier0_pass
    assert "0.70" not in tier0_pass

    on_pass = _between(protocol, "### On Tier 0 pass", "### On no match")
    assert ID_SENTENCE in on_pass
    assert "649def34f8be52c8b66281af98ae884c09aef38b" in on_pass
    assert MATCH_SCORE in on_pass
    assert "SequenceMatcher.ratio()" not in on_pass

    dedup = _between(protocol, "## Deduplication via S2 ID", "## Cost and Performance")
    assert (
        "When two references that pass Tier 0 have the same recorded "
        "`semantic_scholar_id`, flag as duplicate."
    ) in dedup


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
