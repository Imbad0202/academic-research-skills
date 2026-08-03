# Academic Integrity Verification Report — Final Check

## Verification mode and input

- Mode: **Mode 2 — Stage 4.5 final verification**.
- Manuscript: `stage-04p-rerevision/03-re-revised-course-paper-for-inspection.md`.
- Bound SHA-256: `513004b245efe8a557e92144faa8c06eb6bd95e16095d35a624d3d7d4870e40f`.
- Literature corpus: frozen; no source was added, removed, or promoted.
- Live activity: exact-identity, DOI, direct-page, retraction/correction, and text-overlap verification only; these lookups did not reopen literature discovery.
- Cross-model verification: not enabled.
- Cache: no cached citation row was used; no `ADV-CACHE` row.
- Execution: sequential in the same recovered `openai-codex/gpt-5.6-sol` Pi context; fresh artifact/source checks were performed, but cognitive independence is not claimed.

## Verdict

# PASS

Zero SERIOUS issues, zero MEDIUM issues, zero MAJOR_DISTORTION, zero UNVERIFIABLE claims, zero citation-context errors, and zero data inconsistencies were found. No manuscript correction round is required.

Non-gating notes and advisories remain visible: Semantic Scholar HTTP 429 degradation, one live-host retrieval timeout backed by the preserved official file, heuristic originality limits, unavailable identity-based self-plagiarism screening, two standalone-table trace notes, nonblocking PRISMA-trAIce/RAISE adaptation warnings, and token-conservation advisories.

## Verification summary

| Category | Total | Passed | Issues |
|---|---:|---:|---:|
| Reference existence and identity | 21 | 21 VERIFIED | 0 |
| Bibliographic accuracy | 21 | 21 | 0 |
| Ghost citations | 21 body/reference slugs | 21 | 0 orphan; 0 dangling |
| Citation-context occurrences | 58 | 58 VERIFIED | 0 |
| Statistical/data verification | 10 table rows + endpoint calculations | All | 0 |
| Internal consistency | Complete manuscript | PASS | 0 |
| Originality D1 | 24/46 eligible long body paragraphs (52.17%) | 24 | 0 CLOSE_MATCH; 0 VERBATIM |
| Revised-paragraph originality | 24/24 | 24 | 0 |
| Self-plagiarism D2 | — | Not executable | Author name remains a placeholder |
| Claim verification E1–E3 | 41/41 (Mode 2: ALL) | 41 VERIFIED | 0 distortion; 0 unverifiable |
| Scope E4 | 41 claim clusters | 41 conformant | 0 `ADV-E4` |
| Novelty/absence E5 | 1 bounded corpus-absence formulation | Supported within search | 0 `ADV-E5` |
| Strength drift E6 | 4 rounds / 27 patch operations | All | 0 `ADV-E6` |
| AI failure modes | 7 | 7 CLEAR | 0 suspected/insufficient |
| Figure/table fidelity C3 | 2 standalone tables | 2 PASS WITH NOTES | 0 blocking failure |
| Experiment declaration C4 | 1 passport declaration | PASS | 0 |
| Temporal audit | Complete body | PASS | 0 findings |

## Phase A — Reference verification

### A0 structured API layer

All nine DOI-bearing articles were freshly queried.

- Semantic Scholar: 9/9 returned HTTP 429 (`API_UNAVAILABLE`). This was recorded as degradation, never as a positive or negative verdict.
- Crossref: 9/9 exact DOI records returned matching titles and containers.
- OpenAlex: 9/9 exact DOI records returned matching titles; `is_retracted: false` for all nine.
- DOI/direct publisher resolution: 9/9 returned HTTP 200.
- A5 author metadata and A4 page metadata absent from Crossref were confirmed in the retrieved full texts.
- A6's 2012 online deposit date and 2013 issue year were distinguished; the manuscript's 2013 issue citation matches the retrieved article.

### A1/A2 existence and bibliographic accuracy

Every reference received an exact title/author or cited-domain query and a direct canonical resolution. SearXNG returned few indexed hits during this run, so positive determinations rest on DOI/Crossref/OpenAlex records, fresh official/issuer pages, and preserved original files—not on search-result counts.

- Official/institutional sources: 12/12 VERIFIED.
- Academic articles: 9/9 VERIFIED.
- NOT_FOUND: 0.
- MISMATCH: 0.
- DOI misdirection: 0.

For U02, U03, U05, O7, and O8, the standard-library client encountered certificate-chain errors; `curl -k` reached the cited HTTPS pages with HTTP 200 and matching issuer/title content. O1's live host timed out, but the preserved official workbook/PDF text carries the exact cited title and 93–114 table content. This is an access note, not an identity uncertainty.

Field-level audit trail: `01-reference-adjudication.tsv` and `reference-verification/raw/`.

### A3 ghost citations and retraction/correction

- Body citation markers: 58.
- Anchor markers: 58.
- Unique body source slugs: 21.
- Reference entries: 21.
- Orphans/dangling entries: 0/0.

For all nine DOI articles, Crossref relation metadata was empty, OpenAlex returned `is_retracted: false`, and exact-title retraction/correction/expression-of-concern queries returned no notice. This is a dated, coverage-bounded result, not a permanent guarantee.

## Phase B — 100% citation-context verification

All 58 citation occurrences were checked against the cited source's assigned evidentiary role.

- A1 remains Taiwan TVET, 2020–2024, association-only.
- A2–A9 remain governance, mechanism, context, or safeguard sources; none is promoted to a Taiwan private-university strategy effect.
- O3/O8 support official definitions and descriptive recomputation, not effects.
- O4 supports AY113 sampling context only.
- O6 supports policy existence/purpose only.
- U01–U06 support issuer-authored visibility only.

The compound safety language near A3/A7/A8 is explicitly treated as normative synthesis: the sources support student experience, stratification, and stakeholder-governance components, while legal/privacy/financial safeguards are not misattributed as empirical findings from those articles.

Complete occurrence audit: `03-citation-context-audit.tsv`.

## Phase C — data, tables, and experiments

### C1/C2 statistical and internal consistency

The frozen derivation was rerun from the official input:

- Input CSV SHA-256: `8d11b6647f693b27e70f5289980a9710972c17db46fcdb2313d35b7ce7c30c6b`.
- Derived CSV SHA-256 before/after rerun: `ae1802065413b8cd0ff11686382eb6202e671cc18836243156536ebe75251fff`.
- Exit: 0; stderr: empty.
- Ten Table 1 stratum-year rows: exact match.
- Private-general decline: 9,737; 14.2% after rounding.
- Private-Tvet decline: 16,704; 17.4% after rounding.
- TVET approved quota A: 123,366 → 92,294.
- Chinese abstract, English abstract, Results, Discussion, and Conclusion endpoints agree.

Search accounting also passed mechanically: 382 raw records → 316 clusters → 96 retained/220 removed → 16 initial DOI-core works + 2 citation-chased works = 18 identity-verified works → 9 full text + 2 abstract-only + 7 metadata-only. `core-dois.txt` contains 16 unique entries. The Stage 4' record transparently states that no new per-record decision ledger was created; the exact list and frozen rule surfaces are the available witnesses.

### C3 figure/table caption fidelity

No figures exist. Both standalone tables pass their support and interpretation checks. Because no Figure Package or `figure_table_trace[]` exists, each carries a trace-unavailable note under the standalone-table rule; neither note is a blocking issue.

### C4 experiment provenance

The passport's `no_experiments_declared` declaration is present and consistent with an empty `experiment_provenance[]`. No own-experiment claim or `planned_experiment_ids[]` pointer exists.

> This check verifies disclosure and claim-to-provenance fidelity. It does not judge whether the experiment was correctly designed, run, statistically adequate, or reproducible by ARS.

## Phase D — originality

- Eligible long body paragraphs: 46.
- Sampled: 24 (52.17%).
- Substantially revised eligible paragraphs: 24; checked: 24 (100%).
- Every major numbered section and Appendix A is represented.
- Quoted and unquoted exact-fragment searches returned no related match for the 24 sampled blocks.
- Grades: 24 ORIGINAL; 0 CLOSE_MATCH; 0 VERBATIM.

Identity-based self-plagiarism checking could not run because the title-page author name is still a placeholder. D3 produced one structural-parallelism observation, below the two-indicator alert threshold; it is not an authorship determination.

> This originality check is heuristic WebSearch screening, not Turnitin or iThenticate. It covers publicly searchable material only, has cross-language and paywall limitations, and can miss overlap despite the 52.17% sample. Professional plagiarism screening remains recommended before formal submission.

## Phase E — 100% claim verification

All 41 quantitative/factual claim clusters were checked.

| Verdict | Count |
|---|---:|
| VERIFIED | 41 |
| MINOR_DISTORTION | 0 |
| MAJOR_DISTORTION | 0 |
| UNVERIFIABLE | 0 |
| UNVERIFIABLE_ACCESS | 0 |

The funding, conflict, author-contribution, and AI-use statements are verified as project/scholar declarations consistent with the recorded pipeline, not as externally audited personal circumstances.

### E4 scope

No population, timeframe, geography, or domain broadening was found. International studies remain mechanism-only; A1 remains TVET-only; private-general, region, stable-size, and Taiwan-domain gaps remain open limitations. `ADV-E4`: none.

### E5 novelty/absence

The manuscript makes no global novelty claim. Its “only” formulation is bounded to the dated, named, retrieved-full-text corpus and explicitly preserves unknown unsearched/unretrieved areas. Classification: `SUPPORTED_WITHIN_SEARCH`. `ADV-E5`: none.

### E6 claim-strength drift

All four patch rounds and 27 operations since Stage 2.5 PASS were audited. No causal/evidential rung moved without roadmap authorization, and no load-bearing scope, null, validation, or non-causality qualifier was silently dropped. `ADV-E6`: none.

## AI Research Failure Mode Checklist

All seven modes are CLEAR: implementation bug, citation hallucination, result hallucination, shortcut reliance, bug-as-insight, methodology fabrication, and frame-lock. No user override is needed. Full evidence: `08-ai-research-failure-mode-checklist.md`.

## Stage 3' traceability and previous integrity issues

The Stage 3' traceability sidecar was consumed:

- previously-missed new issues: 0;
- indeterminate new issues: 0;
- regressions: 0.

Stage 2.5 corrections remain resolved: O7 uses `pid=217372`, current integrity-process wording matches completed checks, and no stale incorrect locator or claim remains.

## Advisory register

### Token conservation

Twelve patch-level token advisories are preserved across Stage 4 and Stage 4'. E6 found no unauthorized strength drift in any associated operation. `ADV-REV-S4P-R1-1` was explicitly accepted by the scholar. Eleven earlier Stage 4 rows remain open/nonblocking because their prior stage confirmation did not record row-specific dispositions; they are listed in `12-token-conservation-advisory-register.tsv`.

### Compliance

Schema 12 validation passed. Because the manuscript is `other_evidence_synthesis`, PRISMA-trAIce is adaptation-only and cannot block. RAISE returns WARN: the paper discloses AI tasks and author responsibility but does not provide model/provider/version, full prompts/parameters, per-tool validation, AI screening-performance metrics, or a dedicated Discussion-level AI limitations paragraph. These are transparent reporting gaps, not citation/data integrity failures.

PRISMA-trAIce is a foundational, pre-Delphi proposal and has not been empirically validated across diverse contexts; this report does not present it as a consensus standard.

## Execution recovery notes

- The first reference-verification command reached 12/21 records before the harness timeout; the script was resumed at record 13 and the final adjudication contains all 21.
- Follow-up exact-identity searches reached the harness timeout twice; completed query files were retained and the remaining records were resumed until all planned queries were present.
- The first temporal lint invocation used a nonconforming audit-run ID and was rejected by schema lint; the audit was rerun with a valid ID and returned zero findings.
- No incomplete partial output was used for a PASS determination. Final mechanical, schema, citation, hash, and state checks all passed.

## Issue list

### SERIOUS

None.

### MEDIUM

None.

### MINOR

None requiring a correction round.

## Release status

The manuscript is released from Stage 4.5 with a **PASS and zero blocking issues**. Stage 5 has not started. The final verified draft remains byte-identical to the inspected input at SHA-256 `513004b245efe8a557e92144faa8c06eb6bd95e16095d35a624d3d7d4870e40f`.
