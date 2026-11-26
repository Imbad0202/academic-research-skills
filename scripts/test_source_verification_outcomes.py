#!/usr/bin/env python3
"""Wording pin for the publisher-confirmed DOI-elsewhere outcome (#1159).

Reads only the Verification Outcome section of
deep-research/agents/source_verification_agent.md. The assertions stay inside
the paragraph that states the rule, so a file-wide PLAUSIBLE or DOI_MISMATCH
hit — both already present on main — cannot satisfy them.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AGENT_PATH = REPO_ROOT / "deep-research" / "agents" / "source_verification_agent.md"

_SECTION_START = "#### Verification Outcome"
_SECTION_END = "### 5. Currency Assessment"
_PARAGRAPH_START = "If Semantic Scholar has no matching record"


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _verification_outcome_section(agent_text: str) -> str:
    start = agent_text.find(_SECTION_START)
    assert start != -1, f"missing {_SECTION_START!r}"
    body_start = start + len(_SECTION_START)
    end = agent_text.find(_SECTION_END, body_start)
    assert end != -1, f"missing {_SECTION_END!r} after {_SECTION_START!r}"
    return agent_text[body_start:end]


def _paragraph_beginning(section: str, prefix: str) -> str:
    for block in re.split(r"\n\s*\n", section):
        normalized = _normalize_whitespace(block)
        if normalized.startswith(prefix):
            return normalized
    raise AssertionError(
        f"no Verification Outcome paragraph begins with {prefix!r}"
    )


def test_publisher_confirmed_work_with_doi_resolving_elsewhere() -> None:
    section = _verification_outcome_section(AGENT_PATH.read_text(encoding="utf-8"))
    paragraph = _paragraph_beginning(section, _PARAGRAPH_START)

    assert "publisher record confirms the cited work and its printed DOI" in paragraph
    assert "resolves to a different record, assign `PLAUSIBLE`" in paragraph
    assert (
        "Flagged Sources (Detail), identify the publisher record, "
        "the printed DOI, and the record it resolves to"
    ) in paragraph
    assert "`DOI_MISMATCH` flag raised in Tier 0" in paragraph
