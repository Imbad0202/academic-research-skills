# arXiv API Verification Protocol

**Status**: v3.11 (#182 Delta 1)
**Used by**: `bibliography_agent`, `scripts/contamination_signals.py` (`resolve_arxiv_unmatched`)
**API base**: `http://export.arxiv.org/api/query`
**Rate limit**: arXiv asks callers to pace requests ~3s apart (https://info.arxiv.org/help/api/tou.html). No polite-pool / higher-tier mechanism.
**Polite email env var**: none (arXiv has no such convention)

---

## Purpose

Adds a fourth bibliographic-index lookup to the cross-index triangulation surface (S2 + OpenAlex + Crossref + arXiv) per spec v3.11 #182 Delta 1. arXiv is the preprint registry of record — strongest coverage for CS / physics / math preprints carrying an arXiv ID. It complements the three published-literature indexes: a citation with a bogus arXiv ID that fails to resolve is positive non-existence evidence, while a published paper without an arXiv ID is legitimately `skipped` by this resolver (arXiv applicability is ID-gated, not a coverage gap).

Mirrors the structure of `crossref_api_protocol.md` and `openalex_api_protocol.md`.

## Response format

Unlike the JSON siblings, the arXiv query API returns an **Atom 1.0 XML feed**. The client parses it with `xml.etree.ElementTree`; the Atom namespace is `{http://www.w3.org/2005/Atom}`. A match yields one or more `<entry>` elements; a miss yields a feed with **zero** `<entry>` elements (not a 404). Per-entry fields the client reads:

- `<entry><title>` — paper title (arXiv inserts internal whitespace/newlines, which the client collapses to single spaces before similarity comparison).
- `<entry><published>` — ISO-8601 timestamp; the leading 4 digits are the year (matching-year tiebreaker).

## Query Patterns

### Pattern 1: arXiv ID Lookup with Title Cross-Check (primary when an arXiv ID is available)

```
GET ?id_list={arxiv_id}
```

**Matching rule (mirrors the Crossref/S2 `DOI_MISMATCH` pattern):** ID lookup hits are gated by a 0.70 title cross-check (same SequenceMatcher threshold as the sibling clients). If the resolved entry's title is below threshold → ID_MISMATCH, return None, fall through to title search. An empty feed (non-existent ID) is a miss → None.

### Pattern 2: Title Search (fallback when no arXiv ID or ID_MISMATCH)

```
GET ?search_query=ti:"{title}"&max_results=5
```

**Matching rule:** similarity >= 0.70. When multiple candidates pass, prefer the matching-year tiebreaker via a +0.05 score bonus (year read from `<published>`).

## `arxiv_unmatched` derivation

`true` if and only if:
- arXiv ID present: ID lookup either returns an empty feed (miss), misses the title cross-check, AND title search returns no match meeting threshold; OR
- arXiv ID absent: title search alone returns no match meeting threshold.

The check fires only when `obtained_via != 'manual'`.

Note: the unified `lookup_verified` summary (#182 Delta 4, a later batch) narrows the existence-gate `false` to **ID-keyed** unmatched — a title-only `arxiv_unmatched` with no resolvable ID is a coverage-gap signal, not fabrication evidence (C-V6(a)). This protocol's `arxiv_unmatched` boolean is the raw triangulation signal; the narrowing happens at the Delta 4 reducer, not here.

## Degradation handling

| Condition | Action |
|---|---|
| Empty feed (zero `<entry>`) | Treat as miss — caller falls through to title search / reports unmatched. NOT a degradation. |
| HTTP 429 (rate limit) | Back off 2 seconds, retry up to 3 times. After exhaustion, raise `ArxivUnavailable`. Throttle anchor refreshed after each backoff. |
| HTTP 5xx | Raise `ArxivUnavailable` immediately (no retry). |
| Network timeout (30s default) / URLError | Raise `ArxivUnavailable`. |
| Malformed XML body (truncated / unclosed mid-stream) | Raise `ArxivUnavailable` (the read/parse narrow-except translates `ET.ParseError`, `OSError`, `http.client.IncompleteRead`). A *complete* HTML error page is well-formed XML and parses to zero entries — a miss, not a degradation. |
| `ArxivUnavailable` raised | Caller MUST omit `arxiv_unmatched` from the entry (absent != false). Other indexes proceed independently. |

## arXiv-specific notes

- **Applicability is ID-gated.** A citation with no arXiv ID is only checked by title search; the unified Delta 4 summary treats arXiv as `skipped` (not `unmatched`) for non-arXiv published work, so a journal article never picks up a spurious arXiv signal.
- **No polite pool.** arXiv has no `mailto:`-in-User-Agent tier; pacing is the fixed ~3s min-interval, longer than the Crossref/OpenAlex sub-second intervals.
- **XML, not JSON.** This is the one structural divergence from the sibling clients — the only place the response shape differs.

## Client implementation

See `scripts/arxiv_client.py`. Class `ArxivClient` exposes `arxiv_id_lookup(arxiv_id, expected_title)` and `title_search(title, year=None)`. Both return `dict | None` (the dict being a projected `{title, year}` view of one Atom `<entry>`). Both raise `ArxivUnavailable` on degradation per the table above.

## Cross-references

- Spec: `docs/design/2026-05-21-v3.10-182-promote-citation-gate-spec.md` §2 Delta 1
- Mirror template: `deep-research/references/crossref_api_protocol.md`
- Sibling protocols: `deep-research/references/openalex_api_protocol.md`, `deep-research/references/semantic_scholar_api_protocol.md`
