#!/usr/bin/env python3
"""verification_gate — citation existence verification API (Delta 5).

Public functions:
  - verify_citation(entry, clients, *, ref_slug, anchor=None, cache=None)
        -> CitationVerificationOutcome
  - verify_passport(passport, clients, *, ref_slug_by_key, anchors=None,
        cache=None) -> list[outcome]

Composes the four resolvers (crossref / openalex / semantic_scholar / arxiv),
maps each resolver's execution to a {status, queried_by} outcome, derives the
3-class lookup_verified via the Delta 4 reducer (narrowed-false, C-V6(a)),
reads anchor_present from the v3.7.3 anchor marker, and stamps
verification_timestamp. Both ref_slug and anchor are prose-sourced inputs joined
upstream by citation_key — NEVER read off the corpus entry, whose schema forbids
them (#332). Does NOT duplicate the v3.8 audit pipeline — it composes
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
        resolve_arxiv_detailed,
        resolve_doi_then_title_detailed,
        resolve_s2_detailed,
    )
    from verification_cache import stale_advisory_days
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
        resolve_arxiv_detailed,
        resolve_doi_then_title_detailed,
        resolve_s2_detailed,
    )
    from scripts.verification_cache import stale_advisory_days

_ANCHOR_PRESENT_KINDS = frozenset({"quote", "page", "section", "paragraph"})

# #541 omitted-argument sentinel: omission = default cache-through (a
# VerificationCache at the default/env path) + revalidation derived from
# ARS_CACHE_REVALIDATE; an EXPLICIT cache=None is the live opt-out.
_UNSET = object()


def _default_cache():
    try:
        from verification_cache import VerificationCache
    except ImportError:  # pragma: no cover - dual-path import
        from scripts.verification_cache import VerificationCache
    return VerificationCache()


def _resolve_cache_args(cache, revalidate_stale):
    import os
    if cache is _UNSET:
        cache = _default_cache()
    if revalidate_stale is _UNSET:
        revalidate_stale = os.environ.get("ARS_CACHE_REVALIDATE") == "1"
    return cache, revalidate_stale


def _is_valid_ref_slug(ref_slug: Any) -> bool:
    """A ref_slug is valid iff it is a non-empty string: the summary schema
    requires ref_slug as a string, and an empty slug joins to no
    <!--ref:slug--> prose marker. Single definition so verify_citation (the
    emission point) and verify_passport (the join layer) agree on "bad slug"
    (#332)."""
    return isinstance(ref_slug, str) and bool(ref_slug)


def _outcome(status: str, queried_by: str | None,
             response_summary: str | None = None) -> dict[str, Any]:
    return {"status": status, "queried_by": queried_by,
            "response_summary": response_summary}


def _ran_outcome(unmatched: bool, queried_by: str | None) -> dict[str, Any]:
    """Map a ran-resolver result (matched/unmatched) to an outcome dict."""
    return _outcome(STATUS_UNMATCHED if unmatched else STATUS_MATCHED, queried_by)


def _run_doi_then_title(
    entry, client, unavailable_exc, *, resolver_name=None, cache=None,
    bypass_stale=False,
) -> tuple[dict[str, Any], bool]:
    """Run a doi-then-title resolver, mapping execution to a status outcome.
    Used by crossref / openalex (same flow + DOI key, different exception).
    The manual exemption is short-circuited upstream in verify_citation.
    Returns (outcome, served_from_cache) — #541 cache-through routes via the
    detailed contamination_signals wrapper (same cache keys, interoperable
    rows); cache=None is byte-equivalent to the historical live path."""
    try:
        if cache is not None:
            unmatched, _mb, queried_by, from_cache = (
                resolve_doi_then_title_detailed(
                    entry, client, resolver_name=resolver_name, cache=cache,
                    bypass_stale=bypass_stale))
        else:
            unmatched, _mb, queried_by = _resolve_doi_then_title(entry, client)
            from_cache = False
    except unavailable_exc:
        return _outcome(STATUS_UNREACHABLE, None), False
    return _ran_outcome(unmatched, queried_by), from_cache


def _run_semantic_scholar(
    entry, client, *, cache=None, bypass_stale=False,
) -> tuple[dict[str, Any], bool]:
    """S2's lookup(entry) is a single entry-keyed call (DOI-first then title
    internally). queried_by follows the has-an-id rule (C-V6(a)). The manual
    exemption is short-circuited upstream in verify_citation."""
    queried_by = queried_by_for(entry, id_field="doi")
    try:
        if cache is not None:
            unmatched, _mb, queried_by, from_cache = resolve_s2_detailed(
                entry, client, cache=cache, bypass_stale=bypass_stale)
            return _ran_outcome(unmatched, queried_by), from_cache
        matched = bool(client.lookup(entry).get("matched", False))
    except SemanticScholarUnavailable:
        return _outcome(STATUS_UNREACHABLE, None), False
    return _ran_outcome(not matched, queried_by), False


def _run_arxiv(
    entry, client, *, cache=None, bypass_stale=False,
) -> tuple[dict[str, Any], bool]:
    """arXiv resolver is applicable only when the citation has an arXiv ID;
    otherwise it is skipped (not unmatched) per Delta 1 / spec line 119. The
    manual exemption is short-circuited upstream in verify_citation."""
    if not entry.get("arxiv_id"):
        # non-arXiv citation → not applicable
        return _outcome(STATUS_SKIPPED, None), False
    try:
        if cache is not None:
            unmatched, _mb, queried_by, from_cache = resolve_arxiv_detailed(
                entry, client, cache=cache, bypass_stale=bypass_stale)
        else:
            unmatched, _mb, queried_by = _resolve_arxiv_id_then_title(
                entry, client)
            from_cache = False
    except ArxivUnavailable:
        return _outcome(STATUS_UNREACHABLE, None), False
    return _ran_outcome(unmatched, queried_by), from_cache


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
    ref_slug: str,
    anchor: Mapping[str, Any] | None = None,
    cache=_UNSET,
    revalidate_stale=_UNSET,
) -> dict[str, Any]:
    """Verify one citation's existence across the four resolvers.

    `entry` carries citation_key, title, authors, year, source_pointer, optional
    doi / arxiv_id, obtained_via. `clients` is a mapping {crossref, openalex,
    semantic_scholar, arxiv} of resolver clients (injected so callers control
    network / cache).

    `ref_slug` is the writer-prose `<!--ref:slug-->` marker this citation renders
    under, supplied by the caller — never read off the corpus entry (same
    provenance rule as `anchor`; the entry schema forbids the field, #332).

    `anchor` is the v3.7.3 anchor marker ({kind, value}) for this citation's
    ref_slug, already parsed from writer prose and joined upstream (None when no
    anchor marker exists for the ref_slug). It is a SEPARATE input, not an entry
    field — the anchor lives in prose, not in literature_corpus (spec Delta 4:
    the summary is a join across three sources).

    `cache` (#541, closes the Delta-2 follow-up): an optional VerificationCache
    threaded through the four resolvers (same cache keys as the
    contamination-signals layer — interoperable rows). OMITTING the argument gives the
    default cache-through (VerificationCache at the default/env path) with
    revalidation derived from ARS_CACHE_REVALIDATE; passing cache=None
    EXPLICITLY is the live opt-out, byte-equivalent to the historical path. When any resolver outcome was
    served from cache, the summary additionally carries `cache_age_days`
    (citation-level oldest-live-row age, rounded to 0.1) and
    `cache_stale_advisory` (that rounded value > ARS_CACHE_STALE_ADVISORY_DAYS,
    0 disables) — advisory metadata, never a gate input. `revalidate_stale`
    (#541 `ARS_CACHE_REVALIDATE`): a would-be hit whose own row age exceeds
    the threshold is recomputed live and re-cached instead of served.

    Returns a dict validating against citation_verification_summary.schema.json:
    {citation_key, ref_slug, lookup_verified, anchor_present,
     verification_timestamp, resolver_outcomes} (+ the two #541 fields when
    cache-served).
    """
    cache, revalidate_stale = _resolve_cache_args(cache, revalidate_stale)
    if not _is_valid_ref_slug(ref_slug):
        # ref_slug is the prose-join key stamped verbatim into the summary, which
        # the schema requires as a non-empty string. This is the single emission
        # point (verify_passport routes through here), so the contract is enforced
        # once: a non-string fails the schema's type:string, and an empty string
        # joins to no <!--ref:slug--> marker. Either is a caller (prose-join) error
        # — refuse rather than emit a contract-invalid / join-broken summary (#332).
        raise ValueError(
            f"ref_slug must be a non-empty string (the writer-prose join key), "
            f"got {ref_slug!r}; corpus entries do not carry ref_slug (#332)"
        )
    if entry.get("obtained_via") == "manual":
        # v3.7.3 manual exemption: no resolver runs — all four skipped (checked
        # once here rather than re-checked inside each resolver helper).
        resolver_outcomes = {
            r: _outcome(STATUS_SKIPPED, None)
            for r in ("crossref", "openalex", "semantic_scholar", "arxiv")
        }
        any_from_cache = False
    else:
        ran = {
            "crossref": _run_doi_then_title(
                entry, clients["crossref"], CrossrefUnavailable,
                resolver_name="crossref", cache=cache,
                bypass_stale=revalidate_stale),
            "openalex": _run_doi_then_title(
                entry, clients["openalex"], OpenAlexUnavailable,
                resolver_name="openalex", cache=cache,
                bypass_stale=revalidate_stale),
            "semantic_scholar": _run_semantic_scholar(
                entry, clients["semantic_scholar"], cache=cache,
                bypass_stale=revalidate_stale),
            "arxiv": _run_arxiv(
                entry, clients["arxiv"], cache=cache,
                bypass_stale=revalidate_stale),
        }
        resolver_outcomes = {name: oc for name, (oc, _fc) in ran.items()}
        any_from_cache = any(fc for _oc, fc in ran.values())
    summary = {
        "citation_key": entry.get("citation_key"),
        "ref_slug": ref_slug,
        "lookup_verified": reduce_lookup_verified(resolver_outcomes),
        "anchor_present": _anchor_present(anchor),
        "verification_timestamp": datetime.now(timezone.utc).isoformat(),
        "resolver_outcomes": resolver_outcomes,
    }
    if cache is not None and any_from_cache:
        age = cache.entry_age_days(entry.get("citation_key"))
        if age is not None:
            rounded = round(age, 1)
            threshold = stale_advisory_days()
            summary["cache_age_days"] = rounded
            summary["cache_stale_advisory"] = bool(
                threshold and rounded > threshold)
    return summary


def verify_passport(
    passport: Mapping[str, Any],
    clients: Mapping[str, Any],
    *,
    ref_slug_by_key: Mapping[str, str],
    anchors: Mapping[str, Mapping[str, Any]] | None = None,
    cache=_UNSET,
    revalidate_stale=_UNSET,
) -> list[dict[str, Any]]:
    """Batch helper: run verify_citation over every entry in the passport's
    literature_corpus[].

    `ref_slug_by_key` is the {citation_key: ref_slug} join map: corpus entries are
    keyed by citation_key, writer prose is keyed by ref_slug, and the join across
    them is the caller's (Stage 4→5 pipeline's) responsibility — the corpus entry
    never carries ref_slug itself (#332). An entry whose citation_key has no joined
    ref_slug raises ValueError rather than emitting a contract-invalid summary;
    the per-entry summary contract requires a non-null string ref_slug, so a
    missing join is a caller error, not a silently-defaulted field.

    `anchors` is the {ref_slug: anchor-marker} join map parsed from writer prose
    (the v3.7.3 <!--anchor:kind:value--> markers); each entry's anchor is looked
    up by its (joined) ref_slug (absent → anchor_present False). Threading both
    joins here keeps verify_citation a pure per-citation unit.

    ref_slug_by_key is 1:1 (one summary row per corpus entry); per-prose-occurrence
    verification (one entry under several ref slugs) is a different API shape, out
    of scope here.
    """
    cache, revalidate_stale = _resolve_cache_args(cache, revalidate_stale)
    corpus = passport.get("literature_corpus") or []
    anchors = anchors or {}
    outcomes: list[dict[str, Any]] = []
    for entry in corpus:
        citation_key = entry.get("citation_key")
        ref_slug = ref_slug_by_key.get(citation_key)
        if not _is_valid_ref_slug(ref_slug):
            # Missing join (None) OR a present-but-empty/non-string slug — both
            # fail the per-summary contract. Caught here (not just in
            # verify_citation) so the error names the offending citation_key,
            # which the per-citation layer doesn't have (#332).
            raise ValueError(
                f"no valid ref_slug joined for citation_key {citation_key!r} "
                f"(got {ref_slug!r}): the citation_key→ref_slug prose join must "
                "cover every corpus entry with a non-empty string "
                "(corpus entries do not carry ref_slug; #332)"
            )
        outcomes.append(verify_citation(
            entry, clients, ref_slug=ref_slug,
            anchor=anchors.get(ref_slug), cache=cache,
            revalidate_stale=revalidate_stale))
    return outcomes
