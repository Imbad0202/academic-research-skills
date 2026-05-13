# AI Disclosure Schema — Discovery Document

**Status:** DRAFT — Phase 1 scaffold only (cell-filling deferred to Phase 2/3)
**Date:** 2026-05-13
**Issue:** [#106](https://github.com/Imbad0202/academic-research-skills/issues/106)
**Author:** Cheng-I Wu
**Scope:** Discovery — NO schema commitment, NO implementation
**Discovery output is a PR adding this document; PR merge closes #106. Implementation issue (deferred) blocked-by #106.**

---

## 0. Phase tracking

This discovery is split into three execution phases. Each phase ships as a PR commit.

| Phase | Deliverable | Status |
|---|---|---|
| Phase 1 | Doc scaffold + 4 anchor snapshots locked (Wayback + SHA-256) + manifest | **In progress** (this commit) |
| Phase 2 | Fill cells for PRISMA-trAIce + ICMJE (32 of 64 cells minimum) | pending |
| Phase 3 | Fill cells for Nature + IEEE (remaining 32) + Deliverable 2 design space + Deliverable 3 open questions | pending |

**Phase 1 explicitly does NOT fill any cells.** Cells carry `phase: 1-scaffold` placeholder until Phase 2/3. This is intentional — Phase 1 builds the provenance infrastructure so Phase 2/3 cell-filling can cite verbatim with byte-level integrity.

---

## 1. Background

ARS currently has a minimal `ai_disclosure` field (boolean / narrative). Three downstream pressures suggest this **may** need structural expansion:

1. **v3.7.x trust-chain infrastructure** (`docs/design/2026-05-12-ars-v3.7.3-claim-faithfulness-and-contaminated-source-spec.md`) records source provenance + citation anchors. Per-stage AI disclosure has been **hypothesized** as a complement on the production side, but should be tested rather than assumed.
2. **Zhao et al. arXiv:2605.07723 (2026-05)** corpus-scale evidence suggests AI-usage stage **may** correlate with hallucination risk profile. Disclosure granularity has analytical value worth investigating.
3. **External normative anchors** (PRISMA-trAIce / ICMJE / Nature / IEEE, plus expansion candidates) **may** require disclosure beyond ARS's current boolean/narrative form. The actual requirement-vs-recommendation strength varies and must be classified per-item, not aggregated.

**Honest about uncertainty:** discovery output may conclude that the right answer is to align ARS to a single anchor verbatim, construct a hybrid, defer policy mapping to a renderer layer, OR retain the current minimal `ai_disclosure` field. All four outcomes are valid discovery results.

A prior draft attempted to propose a concrete schema directly. Codex pre-open review flagged 5 P1 structural problems. These were symptoms of skipping discovery. This document is the discovery reset.

---

## 2. Scope

### 2.1 In scope

- Source-by-field disclosure matrix across a minimum required set of normative anchors with auditable provenance
- Design space documentation (enumeration of design choices, NOT a chosen solution)
- Open questions for community feedback

### 2.2 Out of scope (per #106)

- Schema file
- Renderer skill
- Migration tooling
- Lint
- Tests

These are reserved for the follow-up implementation issue, which is blocked-by this discovery's completion.

---

## 3. Provenance infrastructure (Phase 1)

All `explicit-mandate` / `explicit-recommend` / `conditional-mandate` cells filled in Phase 2/3 MUST cite a snapshot from this provenance bundle. Snapshot manifest is canonical; live URLs may drift after capture.

**Manifest:** `docs/design/snapshots/2026-05-13-ai-disclosure-discovery/manifest.yaml`

| Anchor | Wayback ID | Local SHA-256 (truncated) | Scope |
|---|---|---|---|
| PRISMA-trAIce | `20260513075443` | `f95fc59f…` | SLR-specific living guideline |
| ICMJE | `20260513075516` | `52f9e6bc…` | Medical journals, broad |
| Nature Portfolio | `20260513075542` | `cf691cba…` | Nature Portfolio (publisher-level guidance) |
| IEEE | `20260513075605` | `3ab8db50…` | IEEE author guidelines |

Verification protocol (per manifest): re-compute SHA-256 of local mirror before writing a mandate/recommend cell; mismatch → re-fetch from `wayback_url` + re-hash before continuing.

---

## 4. Deliverable 1: Source-by-field disclosure matrix

### 4.1 Classification scheme

Each cell carries:

| Field | Required? | Rule |
|---|---|---|
| `source_strength` | yes | `explicit-mandate` / `explicit-recommend` / `conditional-mandate` / `implicit` / `not-addressed` / `unknown` |
| `verbatim_quote` | yes for mandate/recommend/conditional cells | Paraphrase forbidden; ≤ 50 words verbatim from primary source |
| `inference_passage` | yes for `implicit` cells | The passage(s) used for inference, verbatim |
| `locator` | yes for non-`unknown` cells | Section / item / heading within source (e.g., "PRISMA-trAIce Table 1 M6.a") |
| `expected_value_type` | yes | boolean / structured / narrative |
| `conditional_trigger` | required for `conditional-mandate` | Plain-text trigger description |
| `snapshot_ref` | required for non-`unknown` cells | `{anchor_slug}:wayback={wayback_id}` |

**`not-addressed` rule:** a cell may be `not-addressed` only when the matrix author has read the **entire** primary source AND can affirmatively state the field is absent. Cells where the source has not been fully read must be `unknown`.

**`unknown` ceiling:** matrix may close with up to **10 of 64** cells marked `unknown` (subjective ceiling, adjustable upward per #106 acceptance criteria if author finds source genuinely hard to fully read — document why).

### 4.2 Candidate disclosure fields (16-field core list)

These 16 fields anchor the 4×16 = 64-cell minimum matrix. Additional fields may be added during Phase 2/3 if material to ARS's design decision; subtractions require rationale.

1. **AI tool name**
2. **AI tool version**
3. **AI tool developer / manufacturer**
4. **Stage / phase of use**
5. **Specific task within stage**
6. **Affected manuscript sections / content locator**
7. **Date(s) of use**
8. **Prompts** (full text or summary, depending on source)
9. **Human oversight method** (reviewer count, qualifications)
10. **Human responsibility statement**
11. **Performance evaluation method**
12. **Performance evaluation results** (quantitative)
13. **Limitations / known failure modes**
14. **Disclosure location** (acknowledgments / Methods / cover letter)
15. **Copyediting exemption predicate**
16. **AI-generated image / figure / content rights**

### 4.3 Per-anchor matrix — PRISMA-trAIce

**Snapshot:** [`prisma-trAIce` @ wayback 20260513075443](https://web.archive.org/web/20260513075443/https://ai.jmir.org/2025/1/e80247/)

| # | Field | Source strength | Verbatim quote / inference passage | Locator | Value type | Conditional trigger |
|---|---|---|---|---|---|---|
| 1 | AI tool name | _phase-2_ | — | — | — | — |
| 2 | AI tool version | _phase-2_ | — | — | — | — |
| 3 | AI tool developer / manufacturer | _phase-2_ | — | — | — | — |
| 4 | Stage / phase of use | _phase-2_ | — | — | — | — |
| 5 | Specific task within stage | _phase-2_ | — | — | — | — |
| 6 | Affected manuscript sections / content locator | _phase-2_ | — | — | — | — |
| 7 | Date(s) of use | _phase-2_ | — | — | — | — |
| 8 | Prompts | _phase-2_ | — | — | — | — |
| 9 | Human oversight method | _phase-2_ | — | — | — | — |
| 10 | Human responsibility statement | _phase-2_ | — | — | — | — |
| 11 | Performance evaluation method | _phase-2_ | — | — | — | — |
| 12 | Performance evaluation results | _phase-2_ | — | — | — | — |
| 13 | Limitations / known failure modes | _phase-2_ | — | — | — | — |
| 14 | Disclosure location | _phase-2_ | — | — | — | — |
| 15 | Copyediting exemption predicate | _phase-2_ | — | — | — | — |
| 16 | AI-generated image / figure / content rights | _phase-2_ | — | — | — | — |

### 4.4 Per-anchor matrix — ICMJE

**Snapshot:** [`icmje` @ wayback 20260513075516](https://web.archive.org/web/20260513075516/https://www.icmje.org/recommendations/browse/artificial-intelligence/ai-use-by-authors.html)

| # | Field | Source strength | Verbatim quote / inference passage | Locator | Value type | Conditional trigger |
|---|---|---|---|---|---|---|
| 1 | AI tool name | _phase-2_ | — | — | — | — |
| 2 | AI tool version | _phase-2_ | — | — | — | — |
| 3 | AI tool developer / manufacturer | _phase-2_ | — | — | — | — |
| 4 | Stage / phase of use | _phase-2_ | — | — | — | — |
| 5 | Specific task within stage | _phase-2_ | — | — | — | — |
| 6 | Affected manuscript sections / content locator | _phase-2_ | — | — | — | — |
| 7 | Date(s) of use | _phase-2_ | — | — | — | — |
| 8 | Prompts | _phase-2_ | — | — | — | — |
| 9 | Human oversight method | _phase-2_ | — | — | — | — |
| 10 | Human responsibility statement | _phase-2_ | — | — | — | — |
| 11 | Performance evaluation method | _phase-2_ | — | — | — | — |
| 12 | Performance evaluation results | _phase-2_ | — | — | — | — |
| 13 | Limitations / known failure modes | _phase-2_ | — | — | — | — |
| 14 | Disclosure location | _phase-2_ | — | — | — | — |
| 15 | Copyediting exemption predicate | _phase-2_ | — | — | — | — |
| 16 | AI-generated image / figure / content rights | _phase-2_ | — | — | — | — |

### 4.5 Per-anchor matrix — Nature Portfolio

**Snapshot:** [`nature` @ wayback 20260513075542](https://web.archive.org/web/20260513075542/https://www.nature.com/nature-portfolio/editorial-policies/ai)

| # | Field | Source strength | Verbatim quote / inference passage | Locator | Value type | Conditional trigger |
|---|---|---|---|---|---|---|
| 1 | AI tool name | _phase-3_ | — | — | — | — |
| 2 | AI tool version | _phase-3_ | — | — | — | — |
| 3 | AI tool developer / manufacturer | _phase-3_ | — | — | — | — |
| 4 | Stage / phase of use | _phase-3_ | — | — | — | — |
| 5 | Specific task within stage | _phase-3_ | — | — | — | — |
| 6 | Affected manuscript sections / content locator | _phase-3_ | — | — | — | — |
| 7 | Date(s) of use | _phase-3_ | — | — | — | — |
| 8 | Prompts | _phase-3_ | — | — | — | — |
| 9 | Human oversight method | _phase-3_ | — | — | — | — |
| 10 | Human responsibility statement | _phase-3_ | — | — | — | — |
| 11 | Performance evaluation method | _phase-3_ | — | — | — | — |
| 12 | Performance evaluation results | _phase-3_ | — | — | — | — |
| 13 | Limitations / known failure modes | _phase-3_ | — | — | — | — |
| 14 | Disclosure location | _phase-3_ | — | — | — | — |
| 15 | Copyediting exemption predicate | _phase-3_ | — | — | — | — |
| 16 | AI-generated image / figure / content rights | _phase-3_ | — | — | — | — |

### 4.6 Per-anchor matrix — IEEE

**Snapshot:** [`ieee` @ wayback 20260513075605](https://web.archive.org/web/20260513075605/https://open.ieee.org/author-guidelines-for-artificial-intelligence-ai-generated-text/)

| # | Field | Source strength | Verbatim quote / inference passage | Locator | Value type | Conditional trigger |
|---|---|---|---|---|---|---|
| 1 | AI tool name | _phase-3_ | — | — | — | — |
| 2 | AI tool version | _phase-3_ | — | — | — | — |
| 3 | AI tool developer / manufacturer | _phase-3_ | — | — | — | — |
| 4 | Stage / phase of use | _phase-3_ | — | — | — | — |
| 5 | Specific task within stage | _phase-3_ | — | — | — | — |
| 6 | Affected manuscript sections / content locator | _phase-3_ | — | — | — | — |
| 7 | Date(s) of use | _phase-3_ | — | — | — | — |
| 8 | Prompts | _phase-3_ | — | — | — | — |
| 9 | Human oversight method | _phase-3_ | — | — | — | — |
| 10 | Human responsibility statement | _phase-3_ | — | — | — | — |
| 11 | Performance evaluation method | _phase-3_ | — | — | — | — |
| 12 | Performance evaluation results | _phase-3_ | — | — | — | — |
| 13 | Limitations / known failure modes | _phase-3_ | — | — | — | — |
| 14 | Disclosure location | _phase-3_ | — | — | — | — |
| 15 | Copyediting exemption predicate | _phase-3_ | — | — | — | — |
| 16 | AI-generated image / figure / content rights | _phase-3_ | — | — | — | — |

### 4.7 Expansion anchors (Phase 3, optional)

COPE / CSE / WAME / JAMA / PLOS — partial expansion allowed; each cell column added must follow the same provenance rules. Snapshot capture deferred until Phase 3 author elects to include.

---

## 5. Deliverable 2: Design space document _(Phase 3)_

Enumeration of design choices across 5 dimensions (A–E), with trade-off matrix per option across at least 4 axes (alignment depth / schema simplicity / backward-compat burden / integration cost). Per #106, options are credible alternatives — not a quota — and choosing among them is OUT of scope for this discovery.

Dimension placeholders:

- **Dimension A: Value-type / event model** (A1–A5 from #106) — _phase-3_
- **Dimension B: Stage taxonomy** (B1–B5) — _phase-3_
- **Dimension C: Disclosure policy expression** (C1–C5) — _phase-3_
- **Dimension D: Legacy disclosure handling** (D1–D4) — _phase-3_
- **Dimension E: Renderer target** (E1–E4) — _phase-3_

---

## 6. Deliverable 3: Open questions for community feedback _(Phase 3)_

To be surfaced after Deliverables 1+2 close. Six baseline questions from #106:

1. Should ARS schema force a single declaration policy, or be policy-agnostic?
2. Should stage taxonomy be SLR-centric, general, or hierarchical?
3. Is per-stage prompt disclosure mandatory or conditional on policy choice?
4. What's the failure mode if disclosure is incomplete? (Pipeline halt / warning / silent log)
5. Backward compatibility horizon: how long do we accept legacy boolean entries?
6. Is a hybrid schema warranted? This is itself a hypothesis to test.

A GitHub Discussions thread will be linked from #106 when Phase 3 ships.

---

## 7. Phase 1 closure note

Phase 1 is **scaffold + provenance** only. It deliberately fills zero cells. The infrastructure it locks:

- 4 anchor URLs Wayback-archived (capture timestamps recorded in §3)
- 4 local HTML mirrors with SHA-256 hashes (in `snapshots/manifest.yaml`)
- Document structure for Deliverable 1 (4 × 16 = 64 cell placeholders) + Deliverable 2 (5 dimensions) + Deliverable 3 (6 open questions)
- Verification protocol for downstream cell-fillers

**Acceptance for Phase 1** (this commit): the four snapshots verify against their manifest SHAs, the document parses as valid Markdown, and no cell carries a non-placeholder value yet. Cell-filling acceptance criteria (per #106) apply at Phase 2/3 closure.

---

## 8. Related

- v3.7.3 spec: `docs/design/2026-05-12-ars-v3.7.3-claim-faithfulness-and-contaminated-source-spec.md` (locator infrastructure prior art)
- #102 (v3.7.4 triangulation) — orthogonal advisory-signal pattern reference
- #103 (v3.8 L3 audit agent) — disclosure granularity may feed audit signal; RubricEM integration section in #103 references stage-aware disclosure (Borrow 2 mention)
- #104 (README Zhao et al. motivation) — corpus-scale evidence backing for why disclosure granularity matters
- #105 (v3.7.3 migration tool) — orthogonal pattern reference if AI disclosure schema migration is later needed
