# Semantic Scholar API Verification Protocol

**Status**: v3.3
**Used by**: `source_verification_agent`, `bibliography_agent`, `integrity_verification_agent`
**API base**: `https://api.semanticscholar.org/graph/v1`
**Rate limit**: 1 request/second (unauthenticated), 10 requests/second (with API key)
**API key env var**: `S2_API_KEY` (optional; graceful degradation if unset)

---

## Purpose

Provides programmatic verification of reference existence and bibliographic accuracy using the Semantic Scholar Academic Graph API. This supplements (not replaces) WebSearch-based verification by adding a structured, API-grounded check that returns machine-readable metadata.

PaperOrchestra (Song et al., 2026) demonstrated that a two-phase citation pipeline — (1) broad discovery via web search, (2) sequential verification via Semantic Scholar API — achieves significantly higher citation coverage (P0 Recall +2-6%, P1 Recall +12-14% over baselines). ARS adopts the verification phase as an additional tier in the existing multi-tier verification strategy.

---

## Query Patterns

### Pattern 1: Title Search (primary)

```
GET /paper/search?query={url_encoded_title}&limit=5&fields=title,authors,year,externalIds,venue,publicationDate
```

**Matching rule**: Accept a result only when its title is an exact normalized match for the query title: the two titles are identical after lowercasing, replacing ASCII punctuation with spaces, and collapsing whitespace, and a dotted acronym counts as its undotted form (`R.A.G.` = `RAG`). This is `exact_normalized_title` in `scripts/_text_similarity.py`, the check the resolver scripts have applied to title-search results since #431. A similarity score alone does not accept a result: "Attention Is All You Need" and "Attention Is Not All You Need" score 0.926 and are different works. That score is `difflib.SequenceMatcher.ratio()` (`_similarity` in the same module), not a Levenshtein distance. A query title that is only a generic label (`Editorial`, `Introduction`, `Book Review`) is not accepted from title search and needs a DOI match. If more than one result passes, prefer the one with matching year. Year is only that tie-break: the scripts add 0.05 to the score when the year is equal and never reject a result for the year.

### Pattern 2: DOI Lookup (when DOI is available)

```
GET /paper/DOI:{doi}?fields=title,authors,year,externalIds,venue,publicationDate,citationCount
```

**Matching rule**: DOI match is exact. Cross-check the returned title against the reference title. If the title similarity is below 0.70 (`_similarity` in `scripts/_text_similarity.py`, `difflib.SequenceMatcher.ratio()` over normalized titles, not a Levenshtein distance; the scripts' DOI cross-check, which #431 did not change), flag as `DOI_MISMATCH` — a known hallucination pattern where a fabricated DOI resolves to an unrelated paper. A DOI match at or above 0.70 is a match, but it passes Tier 0 only if the returned title is also an exact normalized match (Pattern 1 rule); see Tier 0 pass below.

### Pattern 3: Semantic Scholar ID Lookup (for re-verification)

```
GET /paper/{paperId}?fields=title,authors,year,externalIds,venue,publicationDate,citationCount
```

Used when re-verifying a reference that was previously resolved to a Semantic Scholar ID (stored in the bibliography's `semantic_scholar_id` field).

---

## Verification Tiers (Updated with S2 API)

| Tier | Method | Coverage | Purpose |
|------|--------|----------|---------|
| **Tier 0 (NEW)** | Semantic Scholar API | 100% of references | Programmatic existence check + metadata extraction |
| Tier 1 | DOI resolution | 100% of DOI-bearing refs | URL-level existence check |
| Tier 2 | WebSearch spot-check | 50% of sources | Human-readable verification |

**Execution order**: Tier 0 first (batch, 1 req/sec). References that PASS Tier 0 skip Tier 2 unless flagged for other reasons. References that FAIL Tier 0 proceed to Tier 1 + Tier 2 for manual investigation.

**Tier 0 pass (`S2_VERIFIED`)**: A match passes Tier 0 only when (1) the returned title is an exact normalized match for the reference title (Pattern 1 rule; a DOI match needs this too) and (2) the first author Semantic Scholar returns has the same family name as the reference's first author, compared case-insensitively; if either side has no author, the check fails. A match that does not pass is not `S2_NOT_FOUND` and not `DOI_MISMATCH`; it proceeds to Tier 1 + Tier 2. Check (2) is made in the prompt-run path only: the resolver scripts compare titles and do not compare authors. Year is not a pass condition. In the scripts it is only a tie-break among title-search candidates that already pass (an equal year adds 0.05 to the score and never rejects a candidate).

---

## Response Handling

### On successful match

Record the following in the reference's verification audit trail:
- `semantic_scholar_id`: the S2 paper ID (e.g., `"649def34f8be52c8b66281af98ae884c09aef38b"`)
- `s2_title`: returned title
- `s2_authors`: returned author list
- `s2_year`: returned year
- `s2_venue`: returned venue
- `s2_citation_count`: citation count (informational)
- `match_score`: title similarity score (`difflib.SequenceMatcher.ratio()` in `scripts/_text_similarity.py`; not a Levenshtein distance)
- `verification_method`: `"s2_title_search"` or `"s2_doi_lookup"`

### On no match

- If no DOI match is found and no title-search result passes the Pattern 1 matching rule: classify as `S2_NOT_FOUND`
- `S2_NOT_FOUND` does NOT automatically mean fabrication — the paper may exist but not be indexed in Semantic Scholar (e.g., very recent, non-English, grey literature)
- Proceed to Tier 1 (DOI) and Tier 2 (WebSearch) for further investigation
- If ALL tiers fail: classify as `NOT_FOUND` per existing protocol

### On API failure

- HTTP 429 (rate limit): back off 2 seconds, retry up to 3 times
- HTTP 5xx: skip S2 for this reference, proceed to Tier 1
- Network error: skip S2 entirely for remaining batch, log `[S2-API-UNAVAILABLE]`
- **Never block the pipeline on S2 API failure** — graceful degradation to existing WebSearch-only verification

---

## Deduplication via S2 ID

When two references resolve to the same `semantic_scholar_id`, flag as duplicate. The `bibliography_agent` uses this for deduplication during search (matching PaperOrchestra's approach of deduplicating via Semantic Scholar IDs).

---

## Cost and Performance

- **API calls per paper**: ~30-80 (one per reference, typical paper has 30-80 references)
- **Time**: At 1 req/sec (unauthenticated), 30-80 seconds for a full paper. With API key (10 req/sec): 3-8 seconds
- **Cost**: Free (Semantic Scholar API is free for academic use)
- **Recommendation**: Set `S2_API_KEY` for faster verification. Obtain from https://www.semanticscholar.org/product/api#api-key

---

## References

- Song, Y., Song, Y., Pfister, T., & Yoon, J. (2026). PaperOrchestra: A Multi-Agent Framework for Automated AI Research Paper Writing. *arXiv preprint arXiv:2604.05018*. — Section 4 Step 3 (Literature Review Agent), Appendix D.3 (Citation Verification).
- Semantic Scholar API documentation: https://api.semanticscholar.org/
