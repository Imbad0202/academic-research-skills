#!/usr/bin/env python3
"""Shared title-similarity + retry-budget helpers for the v3.9.0 cross-index
triangulation clients.

Previously triple-implemented byte-equivalently in
`semantic_scholar_client.py`, `openalex_client.py`, and `crossref_client.py`.
Extracted in #128 (v3.9.1 housekeeping) to prevent sibling drift — any
threshold tuning or normalization rule change now happens in one place.

Behavior must remain byte-equivalent with the v3.7.3 / v3.9.0 client
implementations. See `test_text_similarity.py` for the contract tests.
"""
from __future__ import annotations

import string
from difflib import SequenceMatcher


_PUNCT_TRANSLATION = str.maketrans({c: " " for c in string.punctuation})


# Per protocol: 429 → 2s backoff × 3 retries. Shared budget across S2 /
# OpenAlex / Crossref clients.
_BACKOFF_SECONDS = 2.0
_MAX_RETRIES = 3


# Per PaperOrchestra (Song et al. 2026 Appx D.3) + protocol §"Query Patterns"
# Pattern 1: title-similarity threshold for "matched" verdict.
_TITLE_SIMILARITY_THRESHOLD = 0.70


def _normalize_title(s: str) -> str:
    """Per protocol §"Query Patterns" Pattern 1: 'case-insensitive, stripped
    of punctuation' before computing similarity. Punctuation becomes
    whitespace so token boundaries are preserved, then collapse runs of
    whitespace. Codex R4-1 closure: raw lowercased comparison falsely scored
    'R.A.G.' vs 'RAG' below the 0.70 threshold."""
    cleaned = s.lower().translate(_PUNCT_TRANSLATION)
    return " ".join(cleaned.split())


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _normalize_title(a), _normalize_title(b)).ratio()
