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

#1148 pins the OpenAlex, Crossref, and arXiv protocols to that exact-title
search rule, and pins both S2 Tier 0 rows in ``docs/ARCHITECTURE.md``. Their
DOI and arXiv ID cross-checks still score titles with ``_similarity`` at 0.70.

Run:
    PYTHONPATH=. python -m pytest scripts/test_tier0_title_gate_prompt_sync.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest


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
    "The base and dotted-acronym forms also count a Unicode dash or quotation mark (`–`, `—`, `’`, `“`, `”`, `„`, `‚`) as the ASCII punctuation it stands for. "
    "An empty folded form never matches. "
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


EXACT_TITLE_SINCE_431 = (
    "Title search has required an exact normalized title since #431, "
    "and the helper now accepts the three forms."
)
COUNTEREXAMPLE = (
    'A similarity score alone does not pass the title check: '
    '"Attention Is All You Need" and "Attention Is Not All You Need" '
    "score 0.926 and are different works."
)
API_ORDER = "Equal scores retain API result order."
AUTHOR_CHECK = (
    "For every title-search result, check both the exact normalized title "
    "and the first author's family name"
)
TIER0_CONJUNCTION = (
    "exact normalized title + case-insensitive first-author family name"
)
ARCHITECTURE = REPO_ROOT / "docs" / "ARCHITECTURE.md"
S2_FAILURE_ROW = (
    "| S2 API verification | 🤖 | 1 | "
    "No candidate passes Tier 0 (exact normalized title + case-insensitive first-author family name). "
    "If either side has no author, the check fails. "
    "A DOI title score below 0.70 triggers `DOI_MISMATCH`. "
    "| References that FAIL Tier 0 MUST proceed through Tier 1 + Tier 2. |"
)
SIBLING_PROTOCOLS = (
    {
        "name": "openalex",
        "relative": "deep-research/references/openalex_api_protocol.md",
        "client": "openalex_client.py",
        "year_source": "The client reads the year from `publication_year`.",
        "generic": (
            "A generic query title such as `Editorial`, `Introduction`, or `Book Review` "
            "cannot pass by title search and requires a DOI lookup."
        ),
        "label": "**Matching rule (mirrors S2 `DOI_MISMATCH` pattern):**",
        "cross_check": "Cross-check the returned `title` against the reference title.",
        "below": (
            "If the title score is below 0.70, the DOI cross-check fails (`DOI_MISMATCH`) "
            "and the caller falls through to title search."
        ),
        "at_or_above": "At or above 0.70, the client returns the DOI record.",
        "pattern1_extra": (),
        "unmatched_start": "## `openalex_unmatched` derivation",
        "unmatched_end": "## `retraction_status`",
        "unmatched": (
            "DOI present: the DOI lookup misses or fails the title cross-check, and the title search yields no exact normalized title match.",
            "DOI absent: the title search yields no exact normalized title match.",
        ),
    },
    {
        "name": "crossref",
        "relative": "deep-research/references/crossref_api_protocol.md",
        "client": "crossref_client.py",
        "year_source": (
            "The client reads `date-parts[0][0]` from `issued`, then `published-print`, "
            "then `published-online`, taking the first available value."
        ),
        "generic": (
            "A generic query title such as `Editorial`, `Introduction`, or `Book Review` "
            "cannot pass by title search and requires a DOI lookup."
        ),
        "label": "**Matching rule (mirrors S2 `DOI_MISMATCH` pattern):**",
        "cross_check": "Cross-check the first entry in Crossref's `title` list against the reference title.",
        "below": (
            "If the title score is below 0.70, the DOI cross-check fails (`DOI_MISMATCH`) "
            "and the caller falls through to title search."
        ),
        "at_or_above": "At or above 0.70, the client returns the DOI record.",
        "pattern1_extra": (),
        "unmatched_start": "## `crossref_unmatched` derivation",
        "unmatched_end": "## `retraction_status`",
        "unmatched": (
            "DOI present: the DOI lookup misses or fails the title cross-check, and the title search yields no exact normalized title match.",
            "DOI absent: the title search yields no exact normalized title match.",
        ),
    },
    {
        "name": "arxiv",
        "relative": "deep-research/references/arxiv_api_protocol.md",
        "client": "arxiv_client.py",
        "year_source": "The client reads the year from the leading four digits of `<published>`.",
        "generic": (
            "A generic query title such as `Editorial`, `Introduction`, or `Book Review` "
            "cannot pass by title search and requires an arXiv ID lookup."
        ),
        "label": "**Matching rule (mirrors the Crossref/S2 `DOI_MISMATCH` pattern):**",
        "cross_check": "Cross-check the resolved entry's title against the reference title.",
        "below": (
            "If the title score is below 0.70, the ID cross-check fails (`ID_MISMATCH`) "
            "and the caller falls through to title search."
        ),
        "at_or_above": "At or above 0.70, the client returns the entry.",
        "pattern1_extra": (
            "An empty feed is an ID miss and also falls through to title search.",
        ),
        "unmatched_start": "## `arxiv_unmatched` derivation",
        "unmatched_end": "## Degradation handling",
        "unmatched": (
            "`true` if and only if the citation **has an arXiv ID**, the ID lookup returns an empty feed or fails the title cross-check, and the title-search fallback yields no exact normalized title match.",
        ),
    },
)


def _resolver_year(client: str) -> str:
    scored = RESOLVER_YEAR.replace("semantic_scholar_client.py", client)
    if "semantic_scholar_client.py" in scored or client not in scored:
        raise AssertionError(client)
    return scored


@pytest.mark.parametrize("protocol", SIBLING_PROTOCOLS, ids=[item["name"] for item in SIBLING_PROTOCOLS])
def test_sibling_title_search_requires_exact_normalized_title(protocol: dict) -> None:
    """Pattern 2 accepts a title only as an exact normalized match. A matching
    year adds 0.05 among those candidates, and a tie keeps API order."""
    text = (REPO_ROOT / protocol["relative"]).read_text(encoding="utf-8")
    pattern2 = _between(text, "### Pattern 2:", protocol["unmatched_start"])
    assert TITLE_FORMS in pattern2
    assert EXACT_TITLE_SINCE_431 in pattern2
    assert COUNTEREXAMPLE in pattern2
    assert protocol["generic"] in pattern2
    assert _resolver_year(protocol["client"]) in pattern2
    assert protocol["year_source"] in pattern2
    assert "Year is not a pass condition." in pattern2
    assert API_ORDER in pattern2
    assert ">= 0.70" not in pattern2
    assert "Accept if similarity" not in pattern2
    assert "populated DOI" not in pattern2
    assert "meeting threshold" not in pattern2
    assert "Levenshtein" not in pattern2
    assert AUTHOR_CHECK not in pattern2
    if protocol["name"] == "arxiv":
        assert "DOI lookup" not in pattern2
    else:
        assert "arXiv ID lookup" not in pattern2


@pytest.mark.parametrize("protocol", SIBLING_PROTOCOLS, ids=[item["name"] for item in SIBLING_PROTOCOLS])
def test_sibling_identifier_cross_check_uses_similarity_threshold(protocol: dict) -> None:
    """Pattern 1 scores the title with ``_similarity``. Below 0.70 the
    cross-check fails and title search runs; at or above 0.70 the client
    returns the record."""
    text = (REPO_ROOT / protocol["relative"]).read_text(encoding="utf-8")
    pattern1 = _between(text, "### Pattern 1:", "### Pattern 2:")
    assert protocol["label"] in pattern1
    assert protocol["cross_check"] in pattern1
    assert SIMILARITY in pattern1
    assert protocol["below"] in pattern1
    assert protocol["at_or_above"] in pattern1
    for extra in protocol["pattern1_extra"]:
        assert extra in pattern1
    if protocol["name"] == "arxiv":
        assert "fails (`DOI_MISMATCH`)" not in pattern1
        assert "returns the DOI record" not in pattern1
    else:
        assert "fails (`ID_MISMATCH`)" not in pattern1
        assert "empty feed" not in pattern1


@pytest.mark.parametrize("protocol", SIBLING_PROTOCOLS, ids=[item["name"] for item in SIBLING_PROTOCOLS])
def test_sibling_unmatched_requires_exact_normalized_title(protocol: dict) -> None:
    """Unmatched follows the exact-title search. ``meeting threshold`` is not
    an accept condition."""
    text = (REPO_ROOT / protocol["relative"]).read_text(encoding="utf-8")
    section = _between(text, protocol["unmatched_start"], protocol["unmatched_end"])
    for clause in protocol["unmatched"]:
        assert clause in section
    assert "exact normalized title" in section
    assert "meeting threshold" not in section


@pytest.mark.parametrize(
    ("prefix", "required", "forbidden", "exact"),
    [
        (
            "| **1. RESEARCH** |",
            (
                "S2 API Tier-0 verification (exact normalized title + case-insensitive first-author family name)",
            ),
            ("0.70", "Levenshtein", "DOI_MISMATCH", "Tier 1 + Tier 2"),
            None,
        ),
        (
            "| S2 API verification |",
            (
                TIER0_CONJUNCTION,
                "If either side has no author, the check fails.",
                "A DOI title score below 0.70 triggers `DOI_MISMATCH`.",
                "References that FAIL Tier 0 MUST proceed through Tier 1 + Tier 2.",
            ),
            ("Levenshtein",),
            S2_FAILURE_ROW,
        ),
    ],
    ids=["research-stage", "s2-failure"],
)
def test_architecture_tier0_row_names_title_and_first_author(
    prefix: str,
    required: tuple[str, ...],
    forbidden: tuple[str, ...],
    exact: str | None,
) -> None:
    """Each architecture row is read by its own prefix. The DOI 0.70 threshold
    and the Tier 1 + Tier 2 route belong to the failure row."""
    text = ARCHITECTURE.read_text(encoding="utf-8")
    row = _line_starting(text, prefix)
    for clause in required:
        assert clause in row
    for clause in forbidden:
        assert clause not in row
    if exact is not None:
        assert row == exact


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
