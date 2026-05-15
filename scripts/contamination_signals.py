#!/usr/bin/env python3
"""#105 v3.7.3 contamination_signals resolvers.

Pure functions implementing v3.7.3 spec §3.2 Vector 1 + Vector 2 for use
by the migration tool. bibliography_agent computes these at ingest time;
this module gives the migration tool the equivalent computation for
post-hoc backfill on pre-v3.7.3 entries.

Design: docs/design/2026-05-15-issue-105-contamination-signals-backfill-design.md
Spec: docs/design/2026-05-12-ars-v3.7.3-claim-faithfulness-and-contaminated-source-spec.md §3.2
"""
from __future__ import annotations

from typing import Any, Mapping, Protocol


# 10-server closed list per v3.7.3 spec §3.2 + schema description.
# Expanded from 6 to 10 venues per gemini review F6 / codex round-4 F13.
# This list is intentionally redundant with the bibliography_agent's
# in-prose list — adapters and migration tools both need the literal set.
PREPRINT_VENUES = frozenset({
    "arXiv",
    "bioRxiv",
    "medRxiv",
    "SSRN",
    "Research Square",
    "Preprints.org",
    "ChemRxiv",
    "EarthArXiv",
    "OSF Preprints",
    "TechRxiv",
})


class SemanticScholarUnavailable(Exception):
    """SS API degraded (network failure / rate limit exhausted / 5xx).

    Per spec §3.2 emission rules, this triggers OMIT of the
    `semantic_scholar_unmatched` field rather than setting it to False.
    Absence ≠ negative confirmation."""


class SemanticScholarClient(Protocol):
    """Minimal contract for the SS API client passed into Signal 2.

    Production callers pass a real client implementing the protocol at
    `deep-research/references/semantic_scholar_api_protocol.md`
    (429 → 2s backoff × 3, DOI-first then title-similarity fallback).
    Tests pass a MagicMock returning whatever shape the test specifies."""

    def lookup(self, entry: Mapping[str, Any]) -> Mapping[str, Any]:
        """Return {"matched": bool, ...}. Raise SemanticScholarUnavailable
        on transient API failures (after the protocol's retry budget is
        exhausted)."""
        ...


def compute_preprint_signal(entry: Mapping[str, Any]) -> bool:
    """Signal 1 per v3.7.3 spec §3.2 Vector 1.

    True iff `year >= 2024 AND venue in PREPRINT_VENUES`. Missing year
    or missing venue resolves to False — both are required for the
    spec's AND.
    """
    year = entry.get("year")
    venue = entry.get("venue")
    if not isinstance(year, int):
        return False
    if venue not in PREPRINT_VENUES:
        return False
    return year >= 2024


def compute_ss_unmatched_signal(
    entry: Mapping[str, Any],
    client: SemanticScholarClient,
) -> bool | None:
    """Signal 2 per v3.7.3 spec §3.2 Vector 2.

    Returns:
      - None if `obtained_via='manual'` (spec exemption) OR API degradation
      - True if SS lookup returns no match
      - False if SS lookup returns a match

    Per spec emission rules, None means OMIT the field from the
    contamination_signals object (NOT set to False — that would imply
    "checked and found", which is not what happened).
    """
    if entry.get("obtained_via") == "manual":
        return None
    try:
        result = client.lookup(entry)
    except SemanticScholarUnavailable:
        return None
    return not result.get("matched", False)


def build_signals_object(
    entry: Mapping[str, Any],
    client: SemanticScholarClient,
) -> dict[str, bool]:
    """Construct the `contamination_signals` object for `entry`.

    Per v3.7.3 spec §3.2 emission rules:
      - Both signals computed → emit both fields (even when both False:
        "computed and found clean" is distinct from "not computed")
      - Manual entry → omit `semantic_scholar_unmatched` field
      - API degradation → omit `semantic_scholar_unmatched` field
    """
    obj: dict[str, bool] = {
        "preprint_post_llm_inflection": compute_preprint_signal(entry),
    }
    ss = compute_ss_unmatched_signal(entry, client)
    if ss is not None:
        obj["semantic_scholar_unmatched"] = ss
    return obj
