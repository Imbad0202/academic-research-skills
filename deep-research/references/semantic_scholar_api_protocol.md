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

**Matching rule**: The title check passes if the two titles are equal under any of the three forms used by `exact_normalized_title` in `scripts/_text_similarity.py`. The base form lowercases, replaces ASCII punctuation with spaces, and collapses and trims whitespace. The dotted-acronym form first removes the dots in a run that starts at a word boundary and consists of two or more contiguous dotted ASCII letters, then applies the base form (`R.A.G.` equals `RAG`). The base and dotted-acronym forms also count a Unicode dash or quotation mark (`–`, `—`, `’`, `“`, `”`, `„`, `‚`) as the ASCII punctuation it stands for. An empty folded form never matches. When both titles contain a Han ideograph in U+4E00-U+9FFF, `_cjk_titles_match` also accepts equal, nonempty Chinese-aware forms. This form folds fullwidth ASCII (`甲Ａ` equals `甲A`), strips one of the wrapper pairs `《》`, `「」`, `『』`, `【】`, `“”`, or `‘’` only when that pair encloses the whole title, strips the terminal marks `。` and `.`, normalizes whitespace, removes spaces touching Han characters, and preserves letter case. Passing the title check is not a Tier 0 pass, which also requires the first-author check. Title search has required an exact normalized title since #431, and the helper now accepts the three forms. A similarity score alone does not pass the title check: "Attention Is All You Need" and "Attention Is Not All You Need" score 0.926 and are different works. That score is `_similarity` in the same module (see Pattern 2), not a Levenshtein distance. A generic query title such as `Editorial`, `Introduction`, or `Book Review` cannot pass by title search and requires a DOI lookup. For every title-search result, check both the exact normalized title and the first author's family name against the reference. Compare family names case-insensitively. If either side has no author, the author check fails. Only after checking every result, use matching year as a tie-break among those that pass both checks. Year is not a pass condition. The resolver's title-search scoring in `scripts/semantic_scholar_client.py` adds 0.05 when the year is equal among candidates that already have an exact normalized title, and it never rejects a candidate for the year; that scoring does not compare authors.

### Pattern 2: DOI Lookup (when DOI is available)

```
GET /paper/DOI:{doi}?fields=title,authors,year,externalIds,venue,publicationDate,citationCount
```

**Matching rule**: The DOI itself must match exactly. Cross-check the returned title against the reference title. The title score is `_similarity` in `scripts/_text_similarity.py`. It returns `1.0` for a Chinese-aware exact match and otherwise takes the higher of the base and dotted-acronym `difflib.SequenceMatcher.ratio()` scores, not a Levenshtein distance. The helper now accepts the three forms; only the threshold stayed at 0.70. If the title score is below 0.70, flag as `DOI_MISMATCH` — a known hallucination pattern where a fabricated DOI resolves to an unrelated paper. A DOI candidate at or above 0.70 whose title is not an exact normalized match does not trigger `DOI_MISMATCH` and does not pass Tier 0.

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

**Tier 0 pass (`S2_VERIFIED`)**: A candidate passes Tier 0 (`S2_VERIFIED`) only when its returned title is an exact normalized match for the reference title and its first author's family name matches the reference's first author's family name case-insensitively. If either side has no author, the check fails. This applies to both a DOI lookup and a title search, subject to the generic-title exclusion on title search. A candidate that fails only the prompt-level title or author requirement is rejected without being classified as `S2_NOT_FOUND` or `DOI_MISMATCH`. If no candidate passes Tier 0, the reference proceeds to Tier 1 + Tier 2. A failed candidate does not by itself send on a reference that another candidate passes. Both the first-author comparison on either path and exact-title verification on a DOI candidate are prompt-level requirements. The scripts do not compare authors. `_lookup_by_doi` returns `matched: True` once the DOI title cross-check clears its threshold (`scripts/semantic_scholar_client.py`). Year is not a pass condition. Matching year is only a tie-break among title-search candidates that pass both checks.

---

## Response Handling

### On Tier 0 pass (`S2_VERIFIED`)

Record the following in the verification audit trail of a reference that passes Tier 0. Record `semantic_scholar_id` in the verification audit trail for deduplication only when the reference passes Tier 0.
- `semantic_scholar_id`: the S2 paper ID (e.g., `"649def34f8be52c8b66281af98ae884c09aef38b"`)
- `s2_title`: returned title
- `s2_authors`: returned author list
- `s2_year`: returned year
- `s2_venue`: returned venue
- `s2_citation_count`: citation count (informational)
- `match_score`: title similarity returned by `_similarity` in `scripts/_text_similarity.py` (see Pattern 2). It is the title score, before any year preference.
- `verification_method`: `"s2_title_search"` or `"s2_doi_lookup"`

### On no match

- If the reference has a DOI, classify it as `S2_NOT_FOUND` when the DOI lookup returns no candidate. If the reference has no DOI, classify it as `S2_NOT_FOUND` when its title is generic, or when title search returns no candidate with an exact normalized title.
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

When two references that pass Tier 0 have the same recorded `semantic_scholar_id`, flag as duplicate. The `bibliography_agent` uses this for deduplication during search (matching PaperOrchestra's approach of deduplicating via Semantic Scholar IDs).

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
