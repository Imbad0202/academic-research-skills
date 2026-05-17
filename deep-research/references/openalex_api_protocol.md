# OpenAlex API Verification Protocol

**Status**: v3.9.0
**Used by**: `bibliography_agent`, `migrate_literature_corpus_to_v3_9_0.py`
**API base**: `https://api.openalex.org`
**Rate limit**: 10 req/s (polite pool, with `mailto`), 1 req/s (anonymous)
**Polite email env var**: `OPENALEX_POLITE_EMAIL` (optional)

---

## Purpose

Provides a second bibliographic-index lookup for v3.9.0 cross-index triangulation per spec v3.9.0 §3.4. Mirrors the structure of `semantic_scholar_api_protocol.md` so adapters and migration tools can swap clients with minimal contract divergence. Used by `bibliography_agent` at ingest time and by the v3.9.0 migration tool for legacy backfill.

OpenAlex coverage complements Semantic Scholar for OA venues, monographs, and works without DOIs. Per Zhao et al. arXiv:2605.07723 §3, cross-index triangulation reduces false-positive rate vs. single-index detection (e.g., a paper unmatched in S2 but matched in OpenAlex is high-coverage-gap evidence, not fabrication evidence).

## Query Patterns

### Pattern 1: DOI Lookup with Title Cross-Check (primary when DOI is available)

```
GET /works/doi:{doi}?select=id,title,authorships,publication_year,doi,primary_location
```

**Matching rule (mirrors S2 `DOI_MISMATCH` pattern):** DOI lookup hits are gated by a Levenshtein 0.70 title cross-check. If the returned `title` field fails the threshold against the entry's canonical title, the DOI hit is rejected (DOI_MISMATCH — a known hallucination pattern where a fabricated DOI resolves to an unrelated paper). The caller falls through to title search.

### Pattern 2: Title Search (fallback when DOI absent or DOI_MISMATCH)

```
GET /works?search={url_encoded_title}&per-page=5&select=id,title,authorships,publication_year,doi,primary_location
```

**Matching rule:** Compute Levenshtein similarity between query title and each result title (case-insensitive, punctuation stripped) per `_normalize_title` in the client. Accept if similarity >= 0.70 (matching PaperOrchestra threshold). If multiple candidates pass, prefer matching-year tiebreaker, then highest similarity, then candidate with populated DOI.

## `openalex_unmatched` derivation

`true` if and only if:
- DOI present: DOI lookup either misses or fails the title cross-check, AND title search returns no match meeting threshold; OR
- DOI absent: title search alone returns no match meeting threshold.

The check fires only when `obtained_via != 'manual'` (manual entries are user-vouched per spec v3.9.0 §3.1).

## Degradation handling

| Condition | Action |
|---|---|
| HTTP 429 (rate limit) | Back off 2 seconds, retry up to 3 times. After exhaustion, raise `OpenAlexUnavailable`. |
| HTTP 5xx | Skip — raise `OpenAlexUnavailable` immediately. |
| Network timeout (30s default) | Skip — raise `OpenAlexUnavailable`. |
| `OpenAlexUnavailable` raised | Caller MUST omit `openalex_unmatched` from the entry (per spec v3.9.0 R-L3-2-C: absent ≠ false). Other indexes proceed independently. |

## v3.9.0 R-L3-2-D constraint

OpenAlex returns `primary_location.source.type` and other classification fields. **v3.9.0 ignores these.** They are not stored on the entry, not surfaced to the finalizer, and not used in any derivation. v3.10 will introduce `venue_type` as an explicit adapter-declared field; the OpenAlex-inferred classification is NOT a v3.10 acceptance provenance value because the k=3 case (where OpenAlex itself is unmatched) makes the classification untrusted.

## Client implementation

See `scripts/openalex_client.py`. The client class `OpenAlexClient` exposes `doi_lookup_with_title_check(doi, expected_title)` and `title_search(title, year=None)` methods. Both return `dict | None`. Both raise `OpenAlexUnavailable` on degradation per the table above. The optional `year` parameter in `title_search` enables a matching-year tiebreaker (+0.05 score bonus) mirroring the S2 client `_lookup_by_title` pattern.

## Cross-references

- Spec: `docs/design/2026-05-17-ars-v3.9.0-cross-index-triangulation-measurement-spec.md` §3.4
- Mirror template: `deep-research/references/semantic_scholar_api_protocol.md`
- Sibling protocol: `deep-research/references/crossref_api_protocol.md`
