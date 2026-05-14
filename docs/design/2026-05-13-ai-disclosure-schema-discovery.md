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
| Phase 1 | Doc scaffold + 4 anchor snapshots locked (Wayback + SHA-256) + manifest | shipped (PR #107 c1) |
| Phase 2 | Fill cells for PRISMA-trAIce + ICMJE (32 of 64 cells) | shipped (PR #107 c2) |
| Phase 3a | Fill cells for Nature Portfolio (16 of remaining 32 cells; 48 of 64 total) | **In progress** (this commit) |
| Phase 3b | Fill cells for IEEE (remaining 16 cells; 64 of 64 total) + Deliverable 2 design space + Deliverable 3 open questions | pending |

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
**Source-strength caveat:** PRISMA-trAIce is a **pre-Delphi proposal** (Holst et al. 2025, §Methods: *"this work is explicitly intended as a well-founded proposal that provides an immediate solution and can serve as the foundation for a subsequent, community-driven formal consensus process"*). It has not undergone formal consensus. **No item carries `explicit-mandate` strength** — the framework explicitly invites community refinement. Items within the framework use reporting-guideline directive verbs ("describe", "report", "include") classified here as `explicit-recommend` *within the proposed framework*. The framework itself is `conditional-mandate` on "AI tool used as methodological tool in an SLR" — outside that condition the framework does not apply. Cells below distinguish item-level recommend from framework-level conditional via the `conditional_trigger` column.

| # | Field | Source strength | Verbatim quote (or inference passage) | Locator | Value type | Conditional trigger |
|---|---|---|---|---|---|---|
| 1 | AI tool name | explicit-recommend | "For each AI tool or system used: a. Specify the name, version number (if applicable), and developer/provider." | Table 1, M2.a | narrative | AI tool used in SLR |
| 2 | AI tool version | explicit-recommend | "Specify the name, version number (if applicable), and developer/provider." | Table 1, M2.a | narrative | AI tool used in SLR; "if applicable" softens to recommend-when-versioned |
| 3 | AI tool developer / manufacturer | explicit-recommend | "Specify the name, version number (if applicable), and developer/provider." | Table 1, M2.a | narrative | AI tool used in SLR |
| 4 | Stage / phase of use | explicit-recommend | "For each AI tool, clearly describe: a. The specific SLR stage(s) where it was applied (e.g., search, screening, data extraction, Risk of Bias assessment, synthesis, drafting)." | Table 1, M3.a | structured (SLR stage enum) + narrative | AI tool used in SLR |
| 5 | Specific task within stage | explicit-recommend | "b. The precise task(s) the AI was intended to perform at each stage." | Table 1, M3.b | narrative | AI tool used in SLR |
| 6 | Affected manuscript sections / content locator | implicit | (inference passage) Items T1, A1, I1, R1, D1, D2 each prescribe a *manuscript section* for disclosure but the framework does not require an explicit per-task content-locator field. | Table 1 row headings (Title / Abstract / Introduction / Results / Discussion) | narrative | — |
| 7 | Date(s) of use | not-addressed | (Read entire checklist Table 1 + Methods §; no item requests date-of-use disclosure. Confirmed against M1–M10, R1–R2, D1–D2, T1, A1, I1.) | — | — | — |
| 8 | Prompts | explicit-recommend | "For each LLM/GenAI tool used, report: a. The full prompt(s) employed for each specific task. If prompts are extensive, provide a detailed description of their structure, key instructions, context provided..." | Table 1, M6.a | narrative (or repository link) | LLM/GenAI tool used (M6 header: "Prompt Engineering (if any)") |
| 9 | Human oversight method | explicit-recommend | "Describe the process of human interaction with and oversight of the AI tool(s) at each stage: a. How many reviewers interacted with/validated the AI outputs for each task? b. Did reviewers work independently when validating AI outputs? c. What were the qualifications or training of reviewers..." | Table 1, M8.a–g | narrative | AI tool used in SLR |
| 10 | Human responsibility statement | not-addressed | (Read entire Methods §; M8 covers oversight process but no item assigns explicit author-responsibility statement for AI output correctness. Distinct from ICMJE which mandates this separately.) | — | — | — |
| 11 | Performance evaluation method | explicit-recommend | "Describe methods used to evaluate the AI tool(s) performance for the specific tasks within the review (if applicable and feasible). This may include: a. The reference standard used for evaluation... b. The metrics used..." | Table 1, M9 | narrative | AI tool used in SLR; "if applicable and feasible" softens further |
| 12 | Performance evaluation results | explicit-recommend | "Report the results of any performance evaluations of the AI tool(s) for the specific tasks within the review (as described in P-trAIce M9). Include quantitative results (see M9) and measures of agreement between AI and human reviewers if assessed." | Table 1, R2 | structured (quantitative metrics) + narrative | M9 performance evaluation was conducted |
| 13 | Limitations / known failure modes | explicit-recommend | "Discuss any limitations encountered in using the AI tool(s) (eg, technical issues, biases identified, challenges in prompt engineering, unexpected outputs, limitations in AI performance for specific sub-tasks)." | Table 1, D1 | narrative | AI tool used in SLR |
| 14 | Disclosure location | implicit | (inference passage) Each Table 1 item is row-categorized by manuscript section (Title / Abstract / Introduction / Methods / Results / Discussion), implying section-of-record per item. No single "disclosure_location" field; location is structural property of the checklist itself. | Table 1 row groupings | structured (manuscript section enum) | — |
| 15 | Copyediting exemption predicate | not-addressed | (Read entire checklist; PRISMA-trAIce scope is "AI as methodological tool in an SLR"; copyediting exemption is not in scope — distinct concern handled by venue-level policies, not this framework.) | — | — | — |
| 16 | AI-generated image / figure / content rights | implicit | (inference passage) "Describe how data handled by AI tools (input, output, intermediate data) was managed and stored, and any measures taken to ensure data privacy, security, and compliance with copyright or terms of service, especially when using third-party cloud-based AI tools." M10 covers copyright/terms-of-service compliance for *data handled by AI tools* — touches AI-generated content rights indirectly without dedicated field. | Table 1, M10 | narrative | AI tool used in SLR |

**Snapshot ref:** all explicit-recommend / implicit cells above cite `prisma-trAIce:wayback=20260513075443` (`sha256: f95fc59f…`).
**Cell count:** 16 cells filled; source-strength distribution: 0 explicit-mandate / 10 explicit-recommend / 0 conditional-mandate / 3 implicit / 3 not-addressed / 0 unknown.

### 4.4 Per-anchor matrix — ICMJE

**Snapshot:** [`icmje` @ wayback 20260513075516](https://web.archive.org/web/20260513075516/https://www.icmje.org/recommendations/browse/artificial-intelligence/ai-use-by-authors.html)
**Source-strength caveat:** ICMJE Recommendations are **adopted** (not draft) and used by 1000+ journals as baseline. Strength language is consistent: "should require", "should describe", "must ensure", "is not acceptable". The page on AI Use by Authors (§V.A) is short — just two paragraphs — and is deliberately framework-level, not field-by-field. Many disclosure fields ARS tracks (tool version, prompts, performance metrics, date of use) are **not addressed** by ICMJE because ICMJE delegates section-level detail to individual journals. Where ICMJE uses "should require" addressed at *journals*, the effective strength to *authors* (post journal adoption) is `explicit-mandate`; where it addresses authors directly with "should describe" / "must ensure" / "is not acceptable", strength is recorded as written.

| # | Field | Source strength | Verbatim quote (or inference passage) | Locator | Value type | Conditional trigger |
|---|---|---|---|---|---|---|
| 1 | AI tool name | implicit | (inference passage) "the journal should require authors to disclose at submission whether they used AI-assisted technologies (such as LLMs, chatbots, or image creators)". Tool identity is implied by "such technology... how they used it" but no field-level requirement to name the specific tool. | §V.A, paragraph 1 | narrative | AI-assisted technology used |
| 2 | AI tool version | not-addressed | (Read entire §V.A; no mention of version-level granularity. ICMJE delegates this detail to individual journal instructions.) | — | — | — |
| 3 | AI tool developer / manufacturer | not-addressed | (Read entire §V.A; no mention of developer/manufacturer disclosure.) | — | — | — |
| 4 | Stage / phase of use | implicit | (inference passage) "Authors who use such technology should describe... how they used it". "How they used it" implies stage but no enumerated stage taxonomy. | §V.A, paragraph 1 | narrative | AI-assisted technology used |
| 5 | Specific task within stage | implicit | (inference passage — same source as #4) "how they used it" implies task-level description without explicit field. | §V.A, paragraph 1 | narrative | AI-assisted technology used |
| 6 | Affected manuscript sections / content locator | not-addressed | (Read entire §V.A; "the submitted work in the appropriate section if applicable" prescribes a disclosure section but not per-content-affected-location.) | — | — | — |
| 7 | Date(s) of use | not-addressed | (Read entire §V.A; no date-of-use disclosure required.) | — | — | — |
| 8 | Prompts | not-addressed | (Read entire §V.A; no prompt-disclosure requirement. ICMJE delegates this to journal-level policy.) | — | — | — |
| 9 | Human oversight method | explicit-recommend | "Authors should carefully review and edit the AI-generated content as the output can be incorrect, incomplete, or biased." | §V.A, paragraph 1 | narrative | AI-assisted technology used |
| 10 | Human responsibility statement | explicit-mandate | "Therefore, humans are responsible for any submitted material that included the use of AI-assisted technologies." | §V.A, paragraph 1 | narrative or boolean | AI-assisted technology used |
| 11 | Performance evaluation method | not-addressed | (Read entire §V.A; no performance-evaluation method disclosure required.) | — | — | — |
| 12 | Performance evaluation results | not-addressed | (Read entire §V.A; no performance-evaluation results disclosure required.) | — | — | — |
| 13 | Limitations / known failure modes | not-addressed | (Read entire §V.A; output limitations *mentioned* in oversight context — "output can be incorrect, incomplete, or biased" — but no requirement to disclose specific limitations encountered.) | — | — | — |
| 14 | Disclosure location | explicit-recommend | "Authors who use such technology should describe, in both the cover letter and the submitted work in the appropriate section if applicable, how they used it" | §V.A, paragraph 1 | structured (closed enum: cover-letter + manuscript-section) | AI-assisted technology used. Note: ICMJE's "should describe" reads as recommend at the language layer; adopting journals may upgrade to mandate via their own instructions. |
| 15 | Copyediting exemption predicate | not-addressed | (Read entire §V.A; no copyediting carve-out. ICMJE treats all AI-assisted technologies uniformly within §V.A — distinct from Nature/IEEE which may carve out basic copyediting. To be verified against those anchors in Phase 3.) | — | — | — |
| 16 | AI-generated image / figure / content rights | explicit-mandate | "Humans must ensure there is appropriate attribution of all quoted material, including full citations." + "Referencing AI-generated material as the primary source is not acceptable." | §V.A, paragraph 1 | narrative + negative-constraint flag | AI-assisted technology used (text or image). Both clauses are mandate strength ("must ensure" + "is not acceptable"). |

**Snapshot ref:** all explicit-mandate / explicit-recommend / implicit cells above cite `icmje:wayback=20260513075516` (`sha256: 52f9e6bc…`).
**Cell count:** 16 cells filled; source-strength distribution: 2 explicit-mandate / 2 explicit-recommend / 3 implicit / 9 not-addressed / 0 unknown.

**Cross-anchor observation:** ICMJE's distribution skews toward `not-addressed` (9/16) by design — it's deliberately framework-level, delegating field-level granularity to adopting journals. This contrasts with PRISMA-trAIce (9 explicit-recommend) which provides item-level granularity within its SLR-only scope. The two anchors are complementary, not competitive: ICMJE sets the *policy floor* (must disclose, must take responsibility); PRISMA-trAIce sets the *content ceiling* (these are the specific things to report when AI is used).

### 4.5 Per-anchor matrix — Nature Portfolio

**Snapshot:** [`nature` @ wayback 20260513075542](https://web.archive.org/web/20260513075542/https://www.nature.com/nature-portfolio/editorial-policies/ai)
**Source-strength caveat:** The Nature Portfolio AI editorial policy is **adopted** (not draft) and applies across all Nature Portfolio journals. The author-facing surface is structured as four short sections: AI authorship, Generative AI images, AI use by peer reviewers, Editorial use. ARS's matrix covers author-side obligations only (sections §AI authorship + §Generative AI images); peer-reviewer-side use and Springer Nature's own editorial use are out of scope per §2.2. Strength language is mixed: "do not currently satisfy our authorship criteria" + "unable to permit" + "must be labelled" carry mandate strength; "should be properly documented" + "should be disclosed" + "does not need to be declared" carry recommend strength. The policy is **framework-level for text** (Methods-section documentation is called for via should-language, with no field-level granularity — no version / no developer / no prompt / no performance metric requirement) and **prohibition-level for images** (generative AI images banned by default with three carve-outs; non-generative ML manipulations carry a recommend-strength caption-disclosure rule). Many text-side disclosure fields ARS tracks are therefore `not-addressed`; image-side rights field carries a hard `explicit-mandate` carrying a negative-constraint + labelling-mandate composite.

| # | Field | Source strength | Verbatim quote (or inference passage) | Locator | Value type | Conditional trigger |
|---|---|---|---|---|---|---|
| 1 | AI tool name | implicit | (inference passage) "Use of an LLM should be properly documented in the Methods section (and if a Methods section is not available, in a suitable alternative part) of the manuscript." Documentation requirement implies tool identity disclosure but no field-level name requirement. | §AI authorship | narrative | LLM used (non-copyediting) |
| 2 | AI tool version | not-addressed | (Read entire §AI authorship + §Generative AI images; no version-level granularity required. Nature delegates Methods-section detail to author and journal-level instructions.) | — | — | — |
| 3 | AI tool developer / manufacturer | not-addressed | (Read entire §AI authorship + §Generative AI images; no developer/manufacturer disclosure required.) | — | — | — |
| 4 | Stage / phase of use | implicit | (inference passage) "Use of an LLM should be properly documented in the Methods section". "Use" implies stage/task description in Methods but no explicit stage taxonomy. | §AI authorship | narrative | LLM used (non-copyediting) |
| 5 | Specific task within stage | implicit | (inference passage — same source as #4) "properly documented in the Methods section" implies task-level description without dedicated field. | §AI authorship | narrative | LLM used (non-copyediting) |
| 6 | Affected manuscript sections / content locator | implicit | (inference passage) "in the relevant caption upon submission" for non-generative ML image tools; for LLM text use, Methods-section documentation implies which sections used AI but no per-content-affected-location requirement. | §Generative AI images (caption rule); §AI authorship (Methods rule) | narrative | AI tool used |
| 7 | Date(s) of use | not-addressed | (Read entire §AI authorship + §Generative AI images; no date-of-use disclosure required.) | — | — | — |
| 8 | Prompts | not-addressed | (Read entire §AI authorship + §Generative AI images; no prompt disclosure required. Methods-section documentation requirement does not enumerate prompts as a required element.) | — | — | — |
| 9 | Human oversight method | explicit-mandate | "In all cases, there must be human accountability for the final version of the text and agreement from the authors that the edits reflect their original work." | §AI authorship | narrative | LLM / AI-tool used in manuscript text ("In all cases" generalizes the rule beyond the copyediting carve-out) |
| 10 | Human responsibility statement | explicit-mandate | "an attribution of authorship carries with it accountability for the work, which cannot be effectively applied to LLMs" + "there must be human accountability for the final version of the text" | §AI authorship | narrative or boolean | LLM used in manuscript |
| 11 | Performance evaluation method | not-addressed | (Read entire §AI authorship + §Generative AI images; no performance-evaluation method disclosure required.) | — | — | — |
| 12 | Performance evaluation results | not-addressed | (Read entire §AI authorship + §Generative AI images; no performance-evaluation results disclosure required.) | — | — | — |
| 13 | Limitations / known failure modes | not-addressed | (Read entire §AI authorship + §Generative AI images; §Generative AI images mentions general legal-copyright and research-integrity risks but does not require authors to disclose tool-specific limitations or failure modes. AI-tool limitations are characterized in §AI use by peer reviewers — out of scope for author-side matrix.) | — | — | — |
| 14 | Disclosure location | explicit-recommend | "Use of an LLM should be properly documented in the Methods section (and if a Methods section is not available, in a suitable alternative part) of the manuscript." + (for non-generative ML on images) "should be disclosed in the relevant caption upon submission" | §AI authorship + §Generative AI images | structured (closed enum: Methods + image-caption + suitable-alternative) | AI tool used; location varies by use type |
| 15 | Copyediting exemption predicate | explicit-recommend | (carve-out) "The use of an LLM (or other AI-tool) for "AI assisted copy editing" purposes does not need to be declared." (predicate, partial verbatim) "AI-assisted improvements to human-generated texts for readability and style... [but] do not include generative editorial work and autonomous content creation." | §AI authorship | structured (boolean carve-out + predicate definition) | AI use limited to copyediting-as-defined |
| 16 | AI-generated image / figure / content rights | explicit-mandate | "Springer Nature journals are unable to permit its use for publication." + "All exceptions must be labelled clearly as generated by AI within the image field." | §Generative AI images | structured (default-prohibit + 3-carve-out enum + labelling-required flag) | Generative AI image/video proposed for publication (default-deny); non-generative ML caption rule handled at #14 as recommend-strength |

**Snapshot ref:** all explicit-mandate / explicit-recommend / implicit cells above cite `nature:wayback=20260513075542` (`sha256: cf691cba…`).
**Cell count:** 16 cells filled; source-strength distribution: 3 explicit-mandate / 2 explicit-recommend / 0 conditional-mandate / 4 implicit / 7 not-addressed / 0 unknown.

**Cross-anchor observation:** Nature Portfolio's distribution skews to `not-addressed` (7/16) for the same structural reason as ICMJE — it is a framework-level policy that delegates field-level granularity to Methods-section author practice and journal instructions, not a reporting-guideline with item-level disclosure schema. Nature's distinctive contribution to the 4-anchor set is the **image-rights mandate package** (#16: default-deny + 3 carve-outs + labelling-required), which is more prescriptive than ICMJE's text-only attribution rule (ICMJE #16 forbids citing AI as primary source; Nature #16 forbids publishing the image at all unless a carve-out applies). The **copyediting exemption predicate (#15)** is the second distinctive contribution: Nature is the first anchor in the matrix to define an explicit carve-out boundary ("AI assisted copy editing" with prose definition) — PRISMA-trAIce and ICMJE both leave this `not-addressed`. Three-anchor hybrid emerging: ICMJE = policy floor (must disclose + must take responsibility), PRISMA-trAIce = SLR content ceiling (item-level granularity), Nature = section-of-record + carve-out shape (Methods location + copyediting predicate + image-rights regime).

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

## 7. Phase closure notes

### 7.1 Phase 1 (shipped)

Phase 1 was **scaffold + provenance** only. It deliberately filled zero cells. The infrastructure it locked:

- 4 anchor URLs Wayback-archived (capture timestamps recorded in §3)
- 4 local HTML mirrors with SHA-256 hashes (in `snapshots/manifest.yaml`)
- Document structure for Deliverable 1 (4 × 16 = 64 cell placeholders) + Deliverable 2 (5 dimensions) + Deliverable 3 (6 open questions)
- Verification protocol for downstream cell-fillers

### 7.2 Phase 2 (this commit)

Phase 2 fills **32 of 64 cells**: PRISMA-trAIce (§4.3) and ICMJE (§4.4). Both anchors fully read end-to-end before any `not-addressed` cell was emitted.

**Cell distribution summary** (32 cells total across two anchors):

| Anchor | explicit-mandate | explicit-recommend | conditional-mandate | implicit | not-addressed | unknown |
|---|---|---|---|---|---|---|
| PRISMA-trAIce | 0 | 10 | 0 | 3 | 3 | 0 |
| ICMJE | 2 | 2 | 0 | 3 | 9 | 0 |
| **Phase 2 total** | **2** | **12** | **0** | **6** | **12** | **0** |

**Key observations** (advisory; Deliverable 2/3 will weigh these):

1. **Anchor complementarity**: ICMJE sets the *policy floor* (must-disclose, human-responsibility, no-plagiarism); PRISMA-trAIce sets the *content ceiling* (tool name, version, prompts, performance metrics — SLR-specific granularity). Neither anchor alone covers ARS's 16-field aspiration.
2. **Zero `unknown` cells**: both anchors were fully readable in single sessions (PRISMA-trAIce 14 checklist items + Methods §; ICMJE §V.A two paragraphs). The 10-cell `unknown` ceiling from §4.1 stays available for Nature + IEEE in Phase 3 if needed.
3. **`not-addressed` skew on ICMJE** (9/16): expected given ICMJE's deliberate framework-level scope. This is a discovery signal, not a flaw in ICMJE — it means a schema chasing ICMJE-only alignment would have a small core (mandate-only) and large optional space.
4. **No `explicit-mandate` in PRISMA-trAIce**: by design, the proposal is pre-Delphi. Any schema that treats PRISMA-trAIce items as hard requirements would be over-reading the source.
5. **Tool-type-conditioned recommendation** in PRISMA-trAIce M6 (Prompts): "if any" / "LLM/GenAI tool used" → this is the only cell where applicability shifts based on tool *type*, not just AI-use binary. Strength stays explicit-recommend (consistent with the pre-Delphi no-mandate rule); the conditioning is on whether the field *applies*, not on whether it is mandatory. Suggests stage-taxonomy Dimension B (Phase 3) may need to handle tool-type-conditioned fields independent of mandate strength.

**Acceptance for Phase 2** (this commit): 32 cells filled with source-strength classification + verbatim quote (or inference passage) + locator; SHA-256 of 4 snapshot HTML files unchanged from Phase 1; document parses as valid Markdown.

### 7.3 Phase 3 (pending)

Phase 3 fills remaining 32 cells (Nature + IEEE) and completes Deliverables 2 (design space) + 3 (open questions). Phase 2 observations above will inform Dimension B (stage taxonomy) and Dimension C (policy expression) options.

---

## 8. Related

- v3.7.3 spec: `docs/design/2026-05-12-ars-v3.7.3-claim-faithfulness-and-contaminated-source-spec.md` (locator infrastructure prior art)
- #102 (v3.7.4 triangulation) — orthogonal advisory-signal pattern reference
- #103 (v3.8 L3 audit agent) — disclosure granularity may feed audit signal; RubricEM integration section in #103 references stage-aware disclosure (Borrow 2 mention)
- #104 (README Zhao et al. motivation) — corpus-scale evidence backing for why disclosure granularity matters
- #105 (v3.7.3 migration tool) — orthogonal pattern reference if AI disclosure schema migration is later needed
