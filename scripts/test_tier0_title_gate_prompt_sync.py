#!/usr/bin/env python3
"""Prompt pin for #1146 — Tier 0 wording matches the resolver script gate.

Title search accepts a candidate only when ``exact_normalized_title`` is true.
A DOI lookup still cross-checks at similarity 0.70 and flags ``DOI_MISMATCH``
only below that. The first-author check is prompt-only: the scripts do not
compare authors. Year only breaks ties (+0.05, never a rejection). The score
is ``difflib.SequenceMatcher.ratio()``, not a Levenshtein distance.

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


def _between(text: str, start: str, end: str) -> str:
    start_at = text.index(start)
    end_at = text.index(end, start_at + len(start))
    return text[start_at:end_at]


def test_tier0_section_requires_exact_title_and_first_author() -> None:
    """Between the Tier 0 and Tier 1 headings, acceptance is exact title plus
    a prompt-only first-author check. ``>= 0.70`` is not an accept rule."""
    section = _between(
        AGENT.read_text(encoding="utf-8"),
        "#### Tier 0",
        "#### Tier 1",
    )
    assert ">= 0.70" not in section
    assert "exact normalized" in section
    assert "first author" in section
    assert "prompt-level rule" in section
    assert "do not compare authors" in section
    assert "tie-break" in section
    assert "SequenceMatcher" in section
    assert "not a Levenshtein distance" in section
    assert "Levenshtein title similarity" not in section
    assert "< 0.70" in section


def test_s2_verified_row_names_exact_title_not_a_threshold() -> None:
    """The outcome row, read only up to any arrow, does not cite 0.70."""
    row = ""
    for line in AGENT.read_text(encoding="utf-8").splitlines():
        if line.startswith("- `S2_VERIFIED`:"):
            row = line.split("→", 1)[0]
            break
    assert row, "S2_VERIFIED row missing"
    assert "0.70" not in row
    assert "exact normalized" in row
    assert "first-author" in row
    assert "Levenshtein" not in row
    assert "year match" not in row


def test_pattern1_names_exact_normalized_title_and_not_a_threshold() -> None:
    pattern1 = _between(
        PROTOCOL.read_text(encoding="utf-8"),
        "### Pattern 1:",
        "### Pattern 2:",
    )
    assert "exact_normalized_title" in pattern1
    assert ">= 0.70" not in pattern1
    assert "Accept if similarity >= 0.70" not in pattern1
    assert "SequenceMatcher" in pattern1
    assert "not a Levenshtein distance" in pattern1
    assert "tie-break" in pattern1
    assert "Editorial" in pattern1


def test_doi_mismatch_sentence_keeps_the_script_threshold() -> None:
    """Option A: DOI_MISMATCH still fires below 0.70, the scripts' cross-check."""
    protocol = PROTOCOL.read_text(encoding="utf-8")
    pattern2 = _between(protocol, "### Pattern 2:", "### Pattern 3:")
    assert "DOI_MISMATCH" in pattern2
    assert "0.70" in pattern2
    assert "below 0.70" in pattern2
    assert "SequenceMatcher" in pattern2
    assert "exact normalized" in pattern2

    agent = AGENT.read_text(encoding="utf-8")
    doi_line = next(
        line for line in agent.splitlines() if line.startswith("**DOI mismatch")
    )
    assert "DOI_MISMATCH" in doi_line
    assert "0.70" in doi_line
    assert "< 0.70" in doi_line
    assert "SequenceMatcher" in doi_line

    tier0_pass = _between(protocol, "**Tier 0 pass", "\n---")
    assert "prompt-run path only" in tier0_pass
    assert "do not compare authors" in tier0_pass
    assert "tie-break" in tier0_pass
    assert "not a pass condition" in tier0_pass


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
