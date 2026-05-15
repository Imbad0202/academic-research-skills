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


# source_pointer → venue inference table. Per v3.7.3 spec §3.2 + schema
# rule, when `venue` is absent the resolver must check `source_pointer`
# for a preprint-server URL/identifier. Substring match against
# lower-cased pointer; keys must be lower-cased and unambiguous.
_POINTER_VENUE_HINTS: tuple[tuple[str, str], ...] = (
    ("arxiv.org", "arXiv"),
    ("biorxiv.org", "bioRxiv"),
    ("medrxiv.org", "medRxiv"),
    ("ssrn.com", "SSRN"),
    ("papers.ssrn.com", "SSRN"),
    ("researchsquare.com", "Research Square"),
    ("preprints.org", "Preprints.org"),
    ("chemrxiv.org", "ChemRxiv"),
    ("eartharxiv.org", "EarthArXiv"),
    ("osf.io/preprints", "OSF Preprints"),
    ("techrxiv.org", "TechRxiv"),
)


def _infer_venue_from_pointer(source_pointer: str) -> str | None:
    """Return the preprint venue inferred from the source_pointer URL,
    or None if no preprint-server hint is present. Per v3.7.3 spec §3.2
    Vector 1: 'venue field (or, when venue is absent, inference from
    source_pointer)'."""
    pointer = source_pointer.lower()
    for hint, venue in _POINTER_VENUE_HINTS:
        if hint in pointer:
            return venue
    return None


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

    True iff `year >= 2024 AND venue resolves to a preprint server`.
    Venue resolution per spec: prefer the explicit `venue` field; when
    absent, infer from `source_pointer` (e.g., 'https://arxiv.org/abs/...'
    → arXiv). Missing year, or venue that resolves to neither a preprint
    server nor an inferable pointer, returns False.

    Source-pointer inference is the codex R2-1 closure: legacy entries
    that schema-validly omit `venue` but carry a preprint URL must still
    surface CONTAMINATED-PREPRINT.
    """
    year = entry.get("year")
    if not isinstance(year, int) or year < 2024:
        return False
    venue = entry.get("venue")
    if venue in PREPRINT_VENUES:
        return True
    if not isinstance(venue, str):
        pointer = entry.get("source_pointer")
        if isinstance(pointer, str):
            return _infer_venue_from_pointer(pointer) in PREPRINT_VENUES
    return False


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
