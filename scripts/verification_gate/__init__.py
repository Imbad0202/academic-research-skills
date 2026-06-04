#!/usr/bin/env python3
"""verification_gate — citation existence verification API (Delta 5).

Public functions:
  - verify_citation(entry, clients, cache=None) -> CitationVerificationOutcome
  - verify_passport(passport, clients, cache=None) -> list[outcome]

Composes the four resolvers (crossref / openalex / semantic_scholar / arxiv),
maps each resolver's execution to a {status, queried_by} outcome, derives the
3-class lookup_verified via the Delta 4 reducer (narrowed-false, C-V6(a)),
reads anchor_present from the v3.7.3 anchor marker, and stamps
verification_timestamp. Does NOT duplicate the v3.8 audit pipeline — it composes
the same lower-layer resolvers and writes the unified summary schema (Delta 4).

The returned dict validates against
shared/contracts/passport/citation_verification_summary.schema.json.

Spec: docs/design/2026-05-21-v3.10-182-promote-citation-gate-spec.md §2 Delta 5.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

try:
    from citation_verification_summary import (
        STATUS_MATCHED,
        STATUS_SKIPPED,
        STATUS_UNMATCHED,
        STATUS_UNREACHABLE,
        reduce_lookup_verified,
    )
    from crossref_client import CrossrefUnavailable
    from openalex_client import OpenAlexUnavailable
    from arxiv_client import ArxivUnavailable
    from contamination_signals import (
        SemanticScholarUnavailable,
        _resolve_arxiv_id_then_title,
        _resolve_doi_then_title,
        queried_by_for,
    )
except ImportError:  # pragma: no cover - dual-path import
    from scripts.citation_verification_summary import (
        STATUS_MATCHED,
        STATUS_SKIPPED,
        STATUS_UNMATCHED,
        STATUS_UNREACHABLE,
        reduce_lookup_verified,
    )
    from scripts.crossref_client import CrossrefUnavailable
    from scripts.openalex_client import OpenAlexUnavailable
    from scripts.arxiv_client import ArxivUnavailable
    from scripts.contamination_signals import (
        SemanticScholarUnavailable,
        _resolve_arxiv_id_then_title,
        _resolve_doi_then_title,
        queried_by_for,
    )

_ANCHOR_PRESENT_KINDS = frozenset({"quote", "page", "section", "paragraph"})


def _outcome(status: str, queried_by: str | None,
             response_summary: str | None = None) -> dict[str, Any]:
    return {"status": status, "queried_by": queried_by,
            "response_summary": response_summary}


def _ran_outcome(unmatched: bool, queried_by: str | None) -> dict[str, Any]:
    """Map a ran-resolver result (matched/unmatched) to an outcome dict."""
    return _outcome(STATUS_UNMATCHED if unmatched else STATUS_MATCHED, queried_by)


def _run_doi_then_title(entry, client, unavailable_exc) -> dict[str, Any]:
    """Run a doi-then-title resolver, mapping execution to a status outcome.
    Used by crossref / openalex (same flow + DOI key, different exception).
    The manual exemption is short-circuited upstream in verify_citation."""
    try:
        unmatched, _matched_by, queried_by = _resolve_doi_then_title(entry, client)
    except unavailable_exc:
        return _outcome(STATUS_UNREACHABLE, None)
    return _ran_outcome(unmatched, queried_by)


def _run_semantic_scholar(entry, client) -> dict[str, Any]:
    """S2's lookup(entry) is a single entry-keyed call (DOI-first then title
    internally). queried_by follows the has-an-id rule (C-V6(a)). The manual
    exemption is short-circuited upstream in verify_citation."""
    queried_by = queried_by_for(entry, id_field="doi")
    try:
        matched = bool(client.lookup(entry).get("matched", False))
    except SemanticScholarUnavailable:
        return _outcome(STATUS_UNREACHABLE, None)
    return _ran_outcome(not matched, queried_by)


def _run_arxiv(entry, client) -> dict[str, Any]:
    """arXiv resolver is applicable only when the citation has an arXiv ID;
    otherwise it is skipped (not unmatched) per Delta 1 / spec line 119. The
    manual exemption is short-circuited upstream in verify_citation."""
    if not entry.get("arxiv_id"):
        return _outcome(STATUS_SKIPPED, None)  # non-arXiv citation → not applicable
    try:
        unmatched, _matched_by, queried_by = _resolve_arxiv_id_then_title(entry, client)
    except ArxivUnavailable:
        return _outcome(STATUS_UNREACHABLE, None)
    return _ran_outcome(unmatched, queried_by)


def _anchor_present(anchor: Any) -> bool:
    """True iff the v3.7.3 anchor marker has kind ∈ {quote,page,section,paragraph}
    (not none). `anchor` is the already-parsed {kind, value} marker sourced from
    writer prose and joined by ref_slug upstream — NEVER read off the corpus
    entry (the literature_corpus_entry schema has no anchor field; reading it
    there would be a permanent silent False)."""
    if not isinstance(anchor, Mapping):
        return False
    return anchor.get("kind") in _ANCHOR_PRESENT_KINDS


def verify_citation(
    entry: Mapping[str, Any],
    clients: Mapping[str, Any],
    *,
    anchor: Mapping[str, Any] | None = None,
    cache=None,
) -> dict[str, Any]:
    """Verify one citation's existence across the four resolvers.

    `entry` carries citation_key, ref_slug, title, optional doi / arxiv_id,
    obtained_via. `clients` is a mapping {crossref, openalex, semantic_scholar,
    arxiv} of resolver clients (injected so callers control network / cache).
    `anchor` is the v3.7.3 anchor marker ({kind, value}) for this citation's
    ref_slug, already parsed from writer prose and joined upstream (None when no
    anchor marker exists for the ref_slug). It is a SEPARATE input, not an entry
    field — the anchor lives in prose, not in literature_corpus (spec Delta 4:
    the summary is a join across three sources). `cache` is reserved for future
    cache-through wiring at this layer (the resolver-level cache lands in
    contamination_signals; threading it here is a Delta-2 follow-up).

    Returns a dict validating against citation_verification_summary.schema.json:
    {citation_key, ref_slug, lookup_verified, anchor_present,
     verification_timestamp, resolver_outcomes}.
    """
    if cache is not None:
        # Honest forward-decl: the resolver-level cache lands in
        # contamination_signals, but it is not yet threaded through this layer
        # (a Delta-2 follow-up). Refuse rather than silently drop a cache the
        # caller passed expecting it to take effect.
        raise NotImplementedError(
            "cache-through at the verification_gate layer is not yet wired "
            "(#182 Delta-2 follow-up); pass cache=None"
        )
    if entry.get("obtained_via") == "manual":
        # v3.7.3 manual exemption: no resolver runs — all four skipped (checked
        # once here rather than re-checked inside each resolver helper).
        resolver_outcomes = {
            r: _outcome(STATUS_SKIPPED, None)
            for r in ("crossref", "openalex", "semantic_scholar", "arxiv")
        }
    else:
        resolver_outcomes = {
            "crossref": _run_doi_then_title(
                entry, clients["crossref"], CrossrefUnavailable),
            "openalex": _run_doi_then_title(
                entry, clients["openalex"], OpenAlexUnavailable),
            "semantic_scholar": _run_semantic_scholar(
                entry, clients["semantic_scholar"]),
            "arxiv": _run_arxiv(entry, clients["arxiv"]),
        }
    return {
        "citation_key": entry.get("citation_key"),
        "ref_slug": entry.get("ref_slug"),
        "lookup_verified": reduce_lookup_verified(resolver_outcomes),
        "anchor_present": _anchor_present(anchor),
        "verification_timestamp": datetime.now(timezone.utc).isoformat(),
        "resolver_outcomes": resolver_outcomes,
    }


def verify_passport(
    passport: Mapping[str, Any],
    clients: Mapping[str, Any],
    *,
    anchors: Mapping[str, Mapping[str, Any]] | None = None,
    cache=None,
) -> list[dict[str, Any]]:
    """Batch helper: run verify_citation over every entry in the passport's
    literature_corpus[]. `anchors` is the {ref_slug: anchor-marker} join map
    parsed from writer prose (the v3.7.3 <!--anchor:kind:value--> markers); each
    entry's anchor is looked up by its ref_slug (absent → anchor_present False).
    Threading the join here keeps verify_citation a pure per-citation unit."""
    corpus = passport.get("literature_corpus") or []
    anchors = anchors or {}
    return [
        verify_citation(
            entry, clients, anchor=anchors.get(entry.get("ref_slug")),
            cache=cache)
        for entry in corpus
    ]
