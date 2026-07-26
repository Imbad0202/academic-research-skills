# Chinese-Literature Verification Protocol

**Status**: standalone client (#595) — NOT wired into the citation verification gate
**Used by**: `scripts/chinese_literature_client.py`
**API bases**: `https://doi.org`, `https://hdl.handle.net`, `https://eutils.ncbi.nlm.nih.gov/entrez/eutils`
**API keys**: none required. An optional NCBI key may be passed to the client constructor; it does NOT relax pacing.
**Live examples in this document were re-verified on 2026-07-27.**

---

## Purpose

`api.crossref.org` is **one DOI registration agency (RA), not the DOI system**. Chinese-language literature DOIs are predominantly registered with **ISTIC** or **CNKI**, both of which are invisible to the Crossref API while resolving normally through `doi.org`. The existing four ARS resolvers (Semantic Scholar / OpenAlex / Crossref / arXiv) therefore reduce almost every Chinese reference to `unresolvable` — the same state a fabricated reference produces. OpenAlex indexes roughly 37% of Chinese core-list journals and 24% of their articles (arXiv:2512.16339), and stores English bracketed shadow titles, so it does not close the gap either.

This protocol documents four open, key-free endpoints that do close a usable part of it, and — equally important — documents exactly where they stop.

## Endpoints

### 1. Registration-agency triage — `GET https://doi.org/ra/<prefix>`

Zero-cost routing. Supports comma-batched prefixes. Response is a JSON array of `{"DOI": <prefix>, "RA": <agency>}`.

Verified 2026-07-27:

```
$ curl -s 'https://doi.org/ra/10.3760,10.3969,10.13209,10.1360'
[{"DOI":"10.3760","RA":"ISTIC"},{"DOI":"10.3969","RA":"ISTIC"},
 {"DOI":"10.13209","RA":"CNKI"},{"DOI":"10.1360","RA":"Crossref"}]
```

| prefix | RA | note |
|---|---|---|
| `10.3760` | ISTIC | Chinese Medical Association journals (yiigle.com) |
| `10.3969` | ISTIC | a large block of Chinese journals |
| `10.13209` | CNKI | e.g. *Acta Scientiarum Naturalium Universitatis Pekinensis* |
| `10.1360` | Crossref | *Science China* series |

An unknown prefix does not return an error: the endpoint answers 200 with a `status` field in place of `RA` (verified 2026-07-27: `GET /ra/10.99999` → `[{"DOI": "10.99999", "status": "DOI does not exist"}]`). The client treats a row with no usable `RA` value as "no agency" and additionally rejects any `RA` value containing a space, defending against the endpoint's occasional human-sentence answers. Routing metadata never produces a verdict on its own.

**Crossref-registered Chinese DOIs are deliberately NOT claimed by this resolver** — the existing `crossref_client.py` already covers them, and re-querying would burn quota while amplifying the Chinese fuzzy-match false positives measured below.

### 2. Content negotiation — `GET https://doi.org/<doi>` with `Accept: application/vnd.citationstyles.csl+json`

For an **ISTIC**-registered DOI this returns CSL-JSON carrying the **original Chinese title and Chinese journal name**, which is what makes an ID + title cross-check possible at all.

Verified 2026-07-27 (`10.3760/cma.j.cn112137-20231008-00670`):

```json
{
  "DOI": "10.3760/cma.j.cn112137-20231008-00670",
  "title": "宫颈腺癌中ProEXC和PRMT5的表达及其临床意义",
  "container-title": "中华医学杂志",
  "volume": "103", "issue": "48", "page": "3967",
  "type": "article-journal",
  "author": [{"given": "Cui Hongxia"}]
}
```

The same DOI returns **HTTP 404** from `https://api.crossref.org/works/<doi>` — this one pair of requests is the entire motivation for the resolver.

Known metadata defects, defended against in `_csl_to_dict`:

- `author` often collapses an entire name into `given` with no family/given split, and mixes pinyin with Han characters. **Authors are display-only and are never a match criterion.**
- `page` frequently carries the first page only (no `page-last`).
- `issued` may be absent → year is `None` and the year check is *skipped*, not failed. Absence is not mismatch.
- `title` is occasionally a single-element list rather than a string.

### 3. Existence probe — `GET https://hdl.handle.net/api/handles/<doi>`

Returns `{"responseCode": 1, ...}` when the handle exists and `{"responseCode": 100, ...}` when it does not. Any other code is treated as an unknown state and degrades.

Verified 2026-07-27:

| identifier | `responseCode` | content negotiation |
|---|---|---|
| `10.3760/cma.j.cn112137-20231008-00670` (real, ISTIC) | `1` | `200` + CSL-JSON |
| `10.3760/cma.j.cn112137-20239999-99999` (fabricated) | `100` | `404` |
| `10.13209/j.0479-8023.2019.001` (real, CNKI) | `1` | `200` + **HTML**, not CSL-JSON |

**There is no wildcard catch-all on these prefixes**, so a `responseCode: 100` is a trustworthy negative — this is what licenses a `false` verdict contribution for a refuted identifier under C-V6(a) (ID-keyed unmatched).

### 4. PubMed E-utilities — coordinate lookup for DOI-less Chinese medical citations

Three steps, in order, none skippable:

**4a. ISSN → NLM title abbreviation.** PubMed does not accept Chinese journal names (`term=中华医学杂志` in NLM Catalog returns 0). GB/T 7714 references do not carry ISSNs either, so the client keeps an offline 中文刊名 → ISSN → NLM TA bridge table.

```
GET esearch.fcgi?db=nlmcatalog&retmode=json&term=0376-2491[issn]   -> NLM 7511141
GET esummary.fcgi?db=nlmcatalog&retmode=json&id=7511141            -> medlineta "Zhonghua Yi Xue Za Zhi"
```

**4b. Coverage confirmation — "the journal has ≥ 1 PubMed record", not "the journal is in the NLM Catalog".** These differ in practice, and conflating them manufactures meaningless misses:

| journal | ISSN | NLM ID | MEDLINE TA | PubMed records |
|---|---|---|---|---|
| 中华医学杂志 | 0376-2491 | 7511141 | `Zhonghua Yi Xue Za Zhi` | 19 347 |
| 中华内科杂志 | 0578-1426 | 161387 | `Zhonghua Nei Ke Za Zhi` | 7 726 |
| 中华外科杂志 | 0529-5815 | 153611 | `Zhonghua Wai Ke Za Zhi` | 11 216 |
| 中华儿科杂志 | 0578-1310 | 417427 | `Zhonghua Er Ke Za Zhi` | 6 167 |
| 中华流行病学杂志 | 0254-6450 | 8208604 | `Zhonghua Liu Xing Bing Xue Za Zhi` | 8 924 |
| 中国全科医学 | 1007-9572 | 101299195 | *(none)* | **0** |

All rows verified 2026-07-27. The last row is the counterexample that forces the rule: the journal is catalogued but carries no MEDLINE abbreviation and no articles, so a coordinate miss against it would say nothing at all.

**4c. Coordinate query.** `[ta] AND [vi] AND [pg]`, falling back to `[ta] AND [au] AND [dp]`.

```
"Zhonghua Yi Xue Za Zhi"[ta] AND 103[vi] AND 3967[pg]  -> count=1, PMID 38129175
"Zhonghua Yi Xue Za Zhi"[ta] AND 103[vi] AND 9999[pg]  -> count=0   (fabricated page)
```

The coordinate tuple is a near-deterministic key, not a fuzzy title match. A multi-record result is reported as `ambiguous` with no record attached — the client never picks one of several.

**Critical limitation, measured 2026-07-27.** For a Chinese-language article, `esummary` returns the **English bracketed shadow title**, never the Chinese original:

```json
{"title": "[Expression of ProEXC and PRMT5 in cervical adenocarcinoma ...].",
 "source": "Zhonghua Yi Xue Za Zhi", "volume": "103", "pages": "3967-3971",
 "lang": ["chi"], "issn": "0376-2491",
 "articleids": [{"idtype": "doi", "value": "10.3760/cma.j.cn112137-20231008-00670"}]}
```

A Chinese-to-English title cross-check is therefore **structurally impossible** on this branch. Corroboration is structural instead: a unique coordinate hit whose echoed journal ISSN matches the ISSN we bridged through and whose year agrees with the cited year (each checked only where both sides carry a value), and the English shadow title is carried into the result's `evidence` for the human to eyeball. A *disagreement* on either demotes the outcome; an *absent* value on either side does not.

## Rate-limit etiquette

| host | client interval | basis |
|---|---|---|
| `doi.org`, `hdl.handle.net` | 0.2 s min interval | neither publishes a floor; mirrors the anonymous pacing of the sibling index clients |
| `eutils.ncbi.nlm.nih.gov` | 0.34 s min interval | NCBI asks for ≤ 3 req/s without an API key |

Pacing is per-instance and uses `time.monotonic` (NTP/manual clock adjustments can run `time.time` backwards, #128 §6). An NCBI API key, when supplied, is passed through but does **not** relax the interval — staying polite is cheaper than defending a ban. Two independent throttle anchors are kept, since sharing one would either over-throttle DOI lookups or under-throttle NCBI.

## Degradation handling

| condition | action |
|---|---|
| DOI/Handle `404`, Handle `responseCode: 100` | **meaningful negative** — reported as data, never as degradation. Treating it as an outage would discard the resolver's strongest signal. |
| HTTP 429 | backoff (≥ 2 s, growing per attempt) then retry, up to `_MAX_RETRIES`; anchor refreshed after the sleep; raise on exhaustion |
| HTTP 5xx | **no retry** — raise immediately (fail fast; the tests pin the request count at 1) |
| network error / timeout (30 s) | raise |
| truncated body (`IncompleteRead`, inherits `HTTPException` not `OSError`) | raise |
| 200 with an unparseable body | raise — a proxy/CDN HTML error page served with 200 must never be recorded as an empty result (#331) |
| 200 CSL request that returns non-CSL (the CNKI HTML shape) | *not* a degradation and *not* a miss: `title unverifiable` → `unresolvable` + a P2 checklist row |
| any of the above | `ChineseLiteratureUnavailable` is raised; the caller MUST map it to `unreachable` and MUST NOT read it as evidence about existence |

`resolve()` has no `unreachable` return value by design: degradation raises, so a network outage can never be silently rendered as a lookup result.

## Chinese title matching

The shared `_text_similarity.exact_normalized_title` (#431 exact-title-or-bust) is ASCII-centric. Measured 2026-07-27 against the real ISTIC title above, it **rejects three legitimate spellings of the identical title**:

| variant | shared `_similarity` | shared `exact_normalized_title` |
|---|---|---|
| identical string | 1.000 | ✅ true |
| fullwidth latin/digits (ＰｒｏＥＸＣ) | 0.577 | ❌ false |
| trailing CJK punctuation (`。`) | 0.981 | ❌ false |
| interior spaces around latin runs | 0.929 | ❌ false |
| a genuinely **different** paper on a related topic | **0.510** | ❌ false |

Two conclusions drive `normalize_cn_title` / `_cn_titles_match`:

1. **Normalization must be Chinese-aware**: NFKC (fullwidth folding), removal of all Unicode punctuation/symbol categories (which covers CJK punctuation `。、，；：《》「」（）【】—` without a hand-maintained list that could drift), and removal of *all* whitespace — Chinese carries no word breaks, so an interior space is typesetting noise, unlike English where it is a token boundary the shared normalizer must preserve.
2. **The shared fuzzy ratio is excluded from the rule entirely**, in both directions. It is not *sufficient*: an unrelated paper already scores 0.510 on Han-character overlap alone, and a Crossref bibliographic query for this exact Chinese title returned a completely different paper as its top hit. And — the non-obvious half, caught by a live smoke run rather than by reasoning — it is not safe as an extra *necessary* condition either: the fullwidth spelling of the identical title scores **0.577, below the 0.70 floor**, so ANDing the ratio in would veto a match that exact normalization had correctly established and file a real paper at **P0, next to the word "fabricated"**. Read the table again: 0.510 for an unrelated paper against 0.577 for an identical one. On CJK titles the threshold separates almost nothing, so it earns no place in the decision.

The operative rule is therefore: **exact equality after Chinese-aware normalization**, plus the `generic_title` veto. Nothing else.

Simplified/Traditional folding is deliberately **not** performed: it is lossy for proper nouns, and a wrong fold would manufacture a false match. The variant pair is surfaced to the human instead.

## Resolution waterfall

```
Stage 0  applicability gate — LOCAL SIGNALS ONLY, zero requests
         CJK in title or journal name, or language ∈ {zh, chi}
         └─ otherwise ─────────────────────────────► skipped (queried_by=None)

Stage 1  DOI present?
   yes ──► ra_lookup(prefix)
           ├─ ISTIC ─► content negotiation (CSL-JSON)
           │           ├─ 200 + Chinese title matches ────► matched   (queried_by=id)
           │           ├─ 200 + title differs ──► handle probe
           │           │        ├─ exists ─────────────► unmatched (id)  DOI_TITLE_MISMATCH
           │           │        └─ absent ─────────────► unmatched (id)  DOI_REFUTED
           │           ├─ 404 ──► handle probe ─────────► unmatched (id)  DOI_REFUTED
           │           └─ 200 non-CSL / no title ──────► unmatched (title) P2
           └─ CNKI ──► handle existence ONLY
                       ├─ responseCode 100 ────────────► unmatched (id)  DOI_REFUTED
                       └─ responseCode 1 ──────────────► unmatched (title) P2
                                                          (never matched — no title obtainable)
   no ───► journal name → ISSN → NLM TA (offline bridge)
           ├─ unmapped ────────────────────────────────► skipped + P3 row
           └─ mapped ──► PubMed coverage (≥1 record?)
                         ├─ not indexed ────────────────► skipped + P3 row
                         └─ indexed ──► coordinate query [ta]+[vi]+[pg]
                                        ├─ 1 hit + ISSN/year agree ► matched (queried_by=title)
                                        ├─ >1 hit ───────────────► unmatched (title) P1 ambiguous
                                        └─ 0 hits ───────────────► unmatched (title) P1
                                                                    (NEVER false — see below)

Every non-matched outcome emits one human-confirmation checklist item.
```

## Three-state semantics — why a miss is never "fabricated"

The resolver's outcomes use the `citation_verification_summary.py` vocabulary verbatim (`matched` / `unmatched` / `skipped`, `queried_by ∈ {id, title, None}`) — but that claim is deliberately scoped to the **status/queried_by semantic layer only**. Under the existing reducer, `false` requires **ID-keyed** unmatched; a title-keyed unmatched reduces to `unresolvable`, and every mapping in the table below reduces correctly through the unmodified reducer.

A gate wiring would still be a real schema-side change, not a mechanical one. Recorded here so the #593 issue-first integration starts from an honest delta list:

1. **`resolver_outcomes` is locked to exactly four keys.** The passport schema pins `additionalProperties: false` with `required: [crossref, openalex, semantic_scholar, arxiv]` ("Exactly four fields, one per resolver — ALL required"). A fifth resolver means editing the schema, the k=0..4 triangulation matrix and its set-equality lints, and the degradation registry — none of which this standalone PR touches.
2. **The coordinate query borrows `queried_by: "title"`.** The schema describes `title` as "only a title search was possible"; a `[ta]+[vi]+[pg]` coordinate query is not a title search. The borrowing is directionally safe — the point is that a non-identifier key must never produce `false`, exactly C-V6(a) — but at wiring time the schema's `queried_by` description needs revising (or a third enum value) rather than silently stretching.
3. **`skipped` here can follow real requests.** The schema describes `skipped` as "resolver did not run", while the `NO_ISSN_MAPPING` / `JOURNAL_NOT_INDEXED` outcomes return `skipped` after the RA lookup or coverage probe has already executed. Reducer-compatible (skipped is excluded from the verdict set, which is precisely what "our table's gap is not evidence" needs), but the schema's `skipped` description needs an "or ran and found no applicable automated source" clause at wiring time.

The design is **deliberately asymmetric — negatives strong, positives conservative**:

| outcome | `status` | `queried_by` | reduces to | why |
|---|---|---|---|---|
| ISTIC DOI resolves, Chinese title matches | `matched` | `id` | `true` | identifier + title, double evidence |
| ISTIC DOI resolves, title differs | `unmatched` | `id` | `false` | chimeric-citation evidence |
| DOI refuted (Handle 100 + 404) | `unmatched` | `id` | `false` | no wildcard catch-all — a fabricated identifier is cleanly refuted |
| DOI exists, title unverifiable (CNKI RA, or an ISTIC record carrying no title) | `unmatched` | `title` | `unresolvable` | ⭐ deliberate demotion (below) |
| PubMed coordinate hit, ISSN + year agree | `matched` | `title` | `true` | near-deterministic coordinate key |
| PubMed coordinate hit, ISSN or year differs | `unmatched` | `title` | `unresolvable` | ⭐ never `false` |
| PubMed indexed, coordinates return 0 | `unmatched` | `title` | `unresolvable` | ⭐ never `false` |
| coordinates ambiguous (>1 record) | `unmatched` | `title` | `unresolvable` | we never pick one of several |
| journal unmapped / not PubMed-indexed | `skipped` | `None` | excluded | not applicable ≠ negative |
| non-Chinese citation | `skipped` | `None` | excluded | English corpora untouched |

Three ⭐ demotions carry the weight of the design:

- **CNKI existence never becomes `matched`.** A real DOI carrying a fabricated title would otherwise be waved through. Because the CNKI RA serves HTML rather than CSL-JSON and we refuse to parse it, "exists" is all we honestly have.
- **A coordinate miss never becomes `false`**, for three independent reasons: the journal-name → NLM TA bridge is heuristic and a wrong row would condemn a real paper; PubMed indexes Chinese journals selectively, so "the journal is indexed" does not imply "this volume is indexed"; and C-V6(a) defines `false` as ID-keyed unmatched, which a coordinate tuple is not. The strength of the signal goes into the **checklist priority (P1)**, not into the verdict. That is where precision-over-recall belongs.
- **An unmapped journal is `skipped`, not `unmatched`.** A gap in our table is a fact about our table.

### Human-confirmation checklist

Every non-matched outcome produces one checklist item with a priority that is **workload ordering, not a suspicion score**:

| priority | reason codes | meaning |
|---|---|---|
| **P0** | `DOI_REFUTED`, `DOI_TITLE_MISMATCH` | the identifier is refuted — the only tier where fabrication vocabulary is permitted at all |
| **P1** | `PUBMED_INDEXED_BUT_COORDINATE_MISS`, `PUBMED_COORDINATE_AMBIGUOUS` | the journal is indexed but the cited coordinates return nothing/too much |
| **P2** | `DOI_EXISTS_TITLE_UNVERIFIABLE` | resolves, but the title cannot be machine-compared — one click closes it |
| **P3** | `JOURNAL_NOT_INDEXED`, `NO_ISSN_MAPPING` | no automated source applies. **This is the normal case** for social-science, non-core-journal, and pre-digital Chinese literature, and is not suspicious |

`human_result` is initialized to `None` and the tool **never** fills it: the judgement is the human's. Wording discipline is enforced in the item text — P1/P2/P3 read "pending human check", because mislabeling a real paper by a real author as suspected fabrication costs far more than missing one bad citation.

## Legal and compliance boundary

**Zero scraping.** CNKI, Wanfang, and VIP search and full-text pages are never fetched or parsed. The four endpoints above are the DOI Foundation's, the Handle System's, and NCBI's official machine-facing services, all open and key-free, all documented for programmatic access.

The concrete cost of this line: a CNKI-registered DOI's resolution page **does** display its title to a human eye, and parsing that HTML would let the resolver auto-verify those citations. We do not do it. Structured extraction from CNKI's pages is a terms-of-service and legal exposure we decline to take on behalf of users, so the CNKI branch stops at existence and asks a person to click one link. That is the boundary of "semi-automatic" in this design.

Also excluded, and why:

- **CSTR (cstr.cn)** — the published API is registration-only (OAuth2 with an institutional registrant identity). No open query/resolution endpoint exists.
- **chinadoi.cn** — a JavaScript SPA with no documented interface. No documentation means no authorization. (Its DOIs resolve fine through `doi.org`, which is what we use.)
- **NSTL** — metadata access requires an institutional service agreement, which an open-source skill cannot require of every user.
- **CQVIP** — no public literature-search API, and its terms prohibit crawling.

## What this does and does not catch

**Catches:**

1. **Fabricated Chinese DOIs**, at high confidence — no wildcard catch-all exists on the ISTIC/CNKI prefixes, so a hallucinated identifier is cleanly refuted.
2. **Chimeric citations** (real DOI, wrong title) within ISTIC coverage — impossible for the existing four resolvers, which 404 on these DOIs entirely.
3. **Fabricated volume/page coordinates** in PubMed-indexed Chinese medical journals, as a high-priority human item.
4. **Systematic visibility of "no source could check this"** — arguably the largest practical gain. Today a Chinese reference silently lands in `unresolvable` and nobody knows it was never actually checked; here every one lands in a checklist row stating which sources were tried and why nothing concluded.

**Does not catch:**

1. Real literature that no open index covers — social-science works, non-core journals, pre-2000 publications, internal reports, theses, conference proceedings, standards. These land in P3 by design, and are expected to remain a large share of any Chinese bibliography.
2. DOI-less non-medical Chinese citations — PubMed covers medicine only, and the ISTIC/CNKI branches require a DOI.
3. Fabricated citations with no identifier at all — technically indistinguishable from real-but-unindexed work. This is the pre-existing OQ-5 recall limit; this resolver makes it visible rather than solving it.
4. Chinese titles for CNKI-registered DOIs — the zero-scraping tradeoff above.
5. Journals outside the seed bridge table (five verified rows at first release, user-extensible via the constructor's `journal_map` argument). The table is built only from publicly redistributable sources (NLM Catalog, ISSN Portal); importing a journal list out of CNKI/Wanfang/VIP is out of bounds.
6. Whether a claim is actually *supported* by the cited source. This resolver answers "does it exist", never "does it support the claim" — the latter is the separate anchor layer, whose gold standard remains a human reading the source.
7. A Chinese work cited with a fully romanized title, no CJK anywhere in the entry, and no `language` field — the Stage 0 gate reads local signals only and skips it. Deciding applicability from the registration agency instead would cost one `doi.org` round-trip for **every English reference in every bibliography**; the applicability gate exists precisely to avoid that, so this narrow case is left to the human rather than billed to English corpora. A caller that has already established the RA can pass it to `is_applicable(entry, ra=...)`.
8. Anything at all when `doi.org` / NCBI are unreachable from the user's network (a live concern inside mainland China). That path raises `ChineseLiteratureUnavailable` so the caller must degrade explicitly; it must never be presented as "everything checked out".

## Client implementation

`scripts/chinese_literature_client.py`. `ChineseLiteratureClient` exposes `ra_for(doi)`, `doi_lookup_with_title_check(doi, expected_title)`, `handle_exists(doi)`, `journal_bridge(container_title)`, `journal_is_indexed(nlm_ta)`, `pubmed_coordinate_lookup(...)`, `is_applicable(entry)`, and the orchestrating `resolve(entry)`. All raise `ChineseLiteratureUnavailable` on degradation per the table above.

Tests: `scripts/test_chinese_literature_client.py`, driven entirely by synthetic checked-in bodies under `scripts/fixtures/transport_bodies/chinese_literature/`. **No CI test performs live network access.**

## Cross-references

- Client spec mirror: `deep-research/references/arxiv_api_protocol.md`
- Sibling protocols: `crossref_api_protocol.md`, `openalex_api_protocol.md`, `semantic_scholar_api_protocol.md`
- Reducer semantics: `scripts/citation_verification_summary.py` (`reduce_lookup_verified`), spec INVARIANT C-V6(a)
- Transport-fixture discipline: `scripts/fixtures/transport_bodies/README.md`
