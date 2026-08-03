# Editorial Decision Package

**Contract:** `reviewer/reviewer_full/v2` · mode `reviewer_full` · stage `reviewer_full_review` · baseline `v3.20.0` · `panel_size: 5` (all 5 cards usable; no `[PANEL-SHRUNK]`)
**Synthesis mode:** v3.6.2 Sprint Contract Synthesizer Protocol (arithmetic). The decision below is produced by the contract's `failure_conditions[]` precedence, not by consensus counting.

---

## Sprint Contract Audit (v3.6.2)

**Step 1 — role-scoped scoring matrix.** Only seats whose `contract_role` appears in a dimension's `eligible_roles` are counted; `not_assessed` values from ineligible seats are excluded from numerator and denominator. No dimension lacks an assessed eligible seat, so no `[DIMENSION-UNASSESSED]` marker applies.

| Dim | Priority | Eligible roles | Assessed eligible seats | Verdict |
|-----|----------|----------------|-------------------------|---------|
| D1 methodology_rigor | mandatory | methodology | methodology = `block` (`fatal`) | `block(fatal)` |
| D2 domain_accuracy | mandatory | domain | domain = `block` (`fatal`) | `block(fatal)` |
| D3 argumentative_coherence | mandatory | da, methodology | da = `block` (repairable); methodology = `block` (repairable) | `block` |
| D4 cross_disciplinary_relevance | high | perspective | perspective = `block` (no `block_class` declared) | `block` |
| D5 writing_and_structure | normal | eic | eic = `warn` | `warn` |
| D6 venue_fit_and_contribution | mandatory | eic | eic = `block` (repairable) | `block` |

**Audit verdict:** `block(fatal)` — worst assessed eligible score is `block`, and two mandatory dimensions (D1, D2) carry declared fatal blocks. Both fatal declarations are in scope, because fatality is valid only on mandatory dimensions and both D1 and D2 are mandatory. D4's missing `block_class` is immaterial: F4 keys on `block`, and a fatal declaration on D4 would have been out of scope in any case.

**Step 2 — failure-condition evaluation.** Every `expression` parsed against the closed vocabulary; no `[EXPRESSION-UNRECOGNISED]` applies. Two-stage evaluation: `cross_reviewer_quantifier` applied to each selected dimension's assessed eligible seats, then the expression's dimension quantifier applied to those per-dimension booleans.

| ID | Sev | Quantifier | Expression | Per-dimension booleans | Fired |
|----|-----|-----------|------------|------------------------|-------|
| F1 | 95 | any | any mandatory dimension has a fatal block | D1=T, D2=T, D3=F, D6=F | **true** |
| F2 | 90 | any | any mandatory dimension scores 'block' | D1=T, D2=T, D3=T, D6=T | **true** |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1=T (n=1→owner), D2=T (n=1→owner), D3=T (n=2→both), D6=T (n=1→owner) | **true** |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4=T | **true** |
| F5 | 40 | any | any dimension scores 'warn' or worse | D1–D6 all T | **true** |
| F0 | 10 | all | every dimension scores 'pass' | — | false |

**Step 3 — precedence and emission.** Highest severity among fired conditions is F1 (95); its action governs. Reviewer cards containing inline routing remarks (the perspective seat writes that its D4 block "routes to major revision") are advisory only — precedence governs, and no fired condition's action is softened on any post-hoc ground.

dimension_verdicts: [D1=block(fatal), D2=block(fatal), D3=block, D4=block, D5=warn, D6=block]
fired_conditions: [F1, F2, F3, F4, F5]
da_critical_adjudications: [C1=VALIDATED, C2=VALIDATED, C3=VALIDATED, C4=VALIDATED]
editorial_decision=reject

*Checker note (`[SYNTHESIS-PARSE: synthesis.a1.md: expected exactly one fired_conditions line, found 0]`): the prior emission omitted the fired-conditions line. This package emits exactly one line of each of the four required audit forms, above. No `[DA-CRITICAL-VS-ACCEPT]` marker applies, since the mechanical decision is not `accept`.*

**Card-hygiene flags (raised, not repaired — Phase 1 territory):**
- The `perspective` card opens with a `## Scoring Plan Dissent` heading containing a self-retracted placeholder ("Wait — that placeholder is not permitted"). I have read it as emitting no dissent, per the card's own retraction, and I have not rewritten the card.
- The `perspective` card's D4 `block` declares no `block_class`.
- The `domain` card places `contract_role` after the `## Dimension Scores` heading rather than before it.
None of these changes the arithmetic.

---

## Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — no dispatching-layer provenance stamp accompanied this invocation. The protocol forbids inferring which of the three permitted statements applies, so none is asserted here. **Nothing in this package should be read as claiming model independence across the five seats.** No cross-family aggregate and no "same-model majority" is computed; the per-seat verdicts in the matrix above are visible by inspection.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript "Building Institutional Quality Culture: Administrator Perspectives on Quality Assurance Implementation in Universities." It was assessed by five reviewers — a Journal-Fit Reviewer and four peer reviewers, one serving in an adversarial capacity — against the venue's six acceptance dimensions.

### Decision: **Reject**

The decision follows from the contract's highest-severity fired condition (F1: a fatal block on a mandatory dimension). Two mandatory dimensions carry fatal blocks, and four of six dimensions are blocked. The paper's underlying observation — that administrators occupy a structurally uncomfortable hinge and manufacture meaning to survive it — is worth reporting, and three seats independently identified §4.3's "held it open" passage as a genuine contribution in waiting. That is not enough to carry the manuscript as written.

Two reviewers stated conditions under which their fatal blocks would be overturned, and I record them because they define the shortest path forward: the domain seat's fatal block would be overturned by resolvable DOIs and verifiable bibliographic records for all twelve sources; the methodology seat's fatal block binds specifically on §4.3 and would require re-analysis of the transcripts with the excluded dissenting participants restored, not additional description of the existing analysis.

### Consensus Analysis

Consensus is computed per sub-claim across the four non-DA reviewers (denominator always 4; silence is neither agreement nor opposition). The Devil's Advocate is adjudicated separately and does not participate in the count. Full sub-claim inventory is in Part 2's preamble.

#### Points of Agreement

**[CONSENSUS-4] — all four non-DA reviewers**

- **SC-1/SC-2 — Delacroix (2018) is reversed in §5, and the paper's only design recommendation rests on the reversed reading.** §2 and the reference-list annotation both state Delacroix argues *against* treating consultation as evidence of quality culture; §5 credits him with recommending it as "the engine of internalization."
- **SC-4 — the interview sample size is stated two ways** (Abstract "Fourteen"; §3.2 "Twelve senior administrators (n=12)").
- **SC-6/SC-8 — dissenting participants were excluded because they fell outside the three-theme structure, while §4.3 claims "the full range of administrator views."** The dependent claims (§4.1 pervasiveness, §4.2 "recurred across every interview," §3.4 "stable structure") inherit the defect.
- **SC-9 — the §3.5 anonymisation guarantee is falsified by §4.1's identifying descriptors** ("the quality director of the largest private university in the region"), in a three-site sample containing one private and one research university.
- **SC-10 — sector-wide and global generalisation** from three institutions in one unnamed system ("universities across the sector," "administrators everywhere"), which §6 then treats as untested.
- **SC-16 — the survey instrument is wholly unreported**, so M=3.9 (SD=0.6) is uninterpretable.
- **SC-17 — the p<.05 subgroup claim is unsupportable as reported** (no named test, no group means, no effect size, no correction, institution perfectly confounded with group, third site dropped).
- **SC-19 — §4.1 attributes the themes to a "structured protocol,"** contradicting the semi-structured design declared in §3.1.

**[CONSENSUS-3] — three agree, fourth silent (silent seat named)**

- **SC-11 — the §6 "first comprehensive account" claim is unsupported** (EIC, methodology, domain; **perspective silent**).
- **SC-14 — "quality culture" is never defined or operationalised, and "QA" attaches to three different objects across the three themes** (EIC, domain, perspective; **methodology silent**).
- **SC-20 — the confidence warrant built on protocol structure in §4.1 is a non-sequitur** (methodology, EIC, perspective; **domain silent**).

**Corroborated findings (2/4, no conflict — action-bearing, not a consensus label)**

- SC-13 — the national system, regulatory model, and review cycle are never identified (EIC, perspective; both confidence 5, both the owner seats of the dimensions they block).
- SC-24 — gatekeeper recruitment through the QA offices under study is never named as a selection pressure (methodology, perspective).
- SC-28 — no theoretical framework, though §1 diagnoses a *theorizing* gap (domain, perspective).
- SC-31 — a multidimensional construct is measured as a unidimensional mean (domain, perspective).

**Single-reviewer findings (1/4 — weighted by confidence, no consensus label)**

SC-3 reference verifiability (domain, conf 5); SC-21 §4.4 divergence labelled corroboration (methodology, conf 5); SC-22 no mixed-methods typology or integration point (methodology, conf 5); SC-23 thematic procedure non-reconstructable, no reflexivity (methodology, conf 5); SC-26 pre-2018 canon absent (domain, conf 5); SC-27 borrowed adjacent-field vocabulary without its source literatures (perspective, conf 5); SC-29 non-operational implications, burden unquantified (perspective, conf 5); SC-30 no academic or student data yet §6 prescribes for them (perspective, conf 5); SC-32 no reproducibility affordances (methodology, conf 5, Minor); SC-33 editorial annotation in a reference entry (EIC, conf 5, Minor); SC-35 no tables or figures anywhere (EIC, conf 4).

Each of these is a Score-4/5 finding from the seat that owns the relevant dimension. Under the confidence-weighting rule, quality of expertise outweighs quantity of opinions: none is discounted for arriving alone.

#### Points of Disagreement

**Surface-form parity applied (#216):** no sub-claim below was re-weighted on the polish, formality, or technical specificity of its phrasing. I ran the opposite-style counterfactual on the two severity splits (SC-5, SC-12): in both cases the divergence is a severity *tag* difference between seats, not a difference traceable to wording, so re-weighting on substance produced the same result. No sub-claim was found unevaluable on wording grounds.

- **SC-5 — how consequential is the 14-vs-12 discrepancy?** Methodology, EIC, and domain tag it Major; perspective tags it Minor and adds "I may be over-reading a drafting error."
  - **Editor's Resolution: Major.** Evidence-first, and the resolution comes from the disputing seat's own text: perspective itself notes the discrepancy "leaves open whether the two excluded dissenting participants account for the difference, which would materially change how the exclusion in §4.3 should be read." Methodology reaches the identical entanglement independently. A discrepancy whose resolution may determine whether the two missing interviews *are* the excluded dissenters is not a drafting slip.

- **SC-7 — what remedy does the §4.3 exclusion require?** Methodology requires re-analysis with the dissenting cases restored (and binds its fatal block to this); domain and perspective concur ("restored and analysed"; "reintegrating... is the minimum remedy"). EIC offers an alternative: reincorporate the accounts *or* drop the representativeness claim and report the exclusion as a limitation.
  - **Editor's Resolution: re-analysis is required; withdrawing the coverage claim alone is insufficient.** Expertise-first — D1 is the methodology seat's dimension, and EIC explicitly defers the analytic consequences to it. Evidence-first — the exclusion contaminates more than §4.3's coverage sentence: §4.1's pervasiveness claim and §4.2's "recurred across every interview" are universal quantifiers over a corpus from which non-conforming members were removed. Striking one sentence in §4.3 leaves those standing.

- **SC-12 — what does fixing the priority claim cost?** EIC (D6 owner) treats it as Major requiring substantive repositioning; domain concurs ("substantial rewriting" of §1, §2, §5, §6); methodology tags it Minor — "Deleting the claim costs the paper nothing."
  - **Editor's Resolution: both are correct about different objects, and the roadmap separates them.** Deleting the sentence is trivial (methodology is right on that narrow point) and appears as the first clause of R7. But EIC's D6 block is driven by the *un-argued increment* — the three themes map one-to-one onto Okonkwo (2018), Pettersen (2022), and Rahman (2020), and the manuscript nowhere states what it adds — which deletion does not touch. Expertise-first on D6 ownership: the repositioning is separately required.

- **Apparent conflict resolved as no conflict — is §5's divergence reporting a strength or a defect?** Domain (S3) and perspective (S3) both credit the manuscript for reporting the administrator/staff divergence rather than smoothing it. Methodology (W5) and the DA (M2) both charge that divergence is *labelled corroboration*.
  - **Editor's Resolution: not a disagreement.** The praise is anchored at §5 ¶5 ("a divergence worth pursuing in future work"); the charge is anchored at §4.4's opening sentence ("The survey corroborated the qualitative picture"). The manuscript does both, in two places. Both positions stand as recorded, and R14 asks only that §4.4 be brought into line with §5.

- **No unresolved dissent remains.** All three genuine splits resolved on evidence or expertise; the unresolved-dissent provision was not invoked.

#### Devil's Advocate Adjudication

| ID | DA argument | Corroborated by | Journal-Fit assessment | Verdict |
|----|-------------|-----------------|------------------------|---------|
| C1 | §5's design recommendation is warranted by Delacroix with the source's thesis reversed | All 4 non-DA (EIC W2, methodology W12, domain W2, perspective W4) | The manuscript's own reference annotation records the correct reading, so the inversion is internal and requires no external verification. The claim it carries is the paper's sole design prescription. | **VALIDATED** |
| C2 | Generalisation from 12 administrators / 3 sites / 1 system to the whole sector, while §6 treats generality as untested | All 4 non-DA (EIC W8, methodology W11, domain W7, perspective W1) | Quantifier scope compared against the stated sampling frame; the domain seat adds that cross-system universality is contradicted by comparative evidence, not merely unsupported by this study's. | **VALIDATED** |
| C3 | Disconfirming cases removed for non-fit, then full-range coverage claimed on the reduced corpus | All 4 non-DA (EIC W6, methodology W1, domain W9, perspective W5) | Both statements appear in adjacent sentences. This is the binding of the methodology seat's fatal block on D1. | **VALIDATED** |
| C4 | Role-plus-institution descriptors identify individuals, breaching the §3.5 consent-backed guarantee | All 4 non-DA (EIC W7, methodology W8, domain W10, perspective W9) | With one private and one research university in the sample, the descriptors resolve to single post-holders; the quotations attributed to them are unflattering about their employers. | **VALIDATED** |

The DA's MAJOR findings are not adjudicated as CRITICALs but are carried into the roadmap where no non-DA seat raised them: M6 → R16, M8 (reactivity half) → S6, M9 → folded into R3.

### Decision Rationale

Four of six dimensions are blocked, and two mandatory dimensions carry fatal blocks — which is what produces Reject rather than Major Revision. The two fatalities are independent. The domain seat cannot assess whether prior work is correctly represented, because all twelve DOIs sit in the `10.5555` reserved test range with sequential suffixes and, for the entries naming real journals, cannot belong to the articles named; a contribution that is entirely literature-relative cannot be evaluated on a bibliography that cannot be checked. The methodology seat's fatality is narrower and, in a sense, worse: the described procedure could not have produced the reported result, because the disconfirming cases were excised from the analysis the Findings report. That is not underspecification that documentation repairs — the evidence itself would have to be regenerated.

Layered on top are three repairable blocks that would each independently have forced Major Revision: sector-wide conclusions from three sites (D3), claim scope exceeding evidence scope plus an undescribed construct (D4), and a novelty claim contradicted by the manuscript's own reference list (D6). D5 sits at `warn`: readable prose, but a manuscript that was never assembled into one consistent draft.

Against that, the panel is unanimous that there is real material here. The §4.3 observation that administrators locate professional identity in an unresolved gap was independently marked as a strength by three seats. A study rebuilt around that observation, honestly scoped to three institutions in a named system, with verifiable sources and the dissenting accounts restored, could be competitive. That is a different manuscript, and the route to it is a new submission rather than a revision of this one. Two further items — the anonymisation breach and the identifying quotations — must be corrected before this text circulates anywhere, irrespective of venue.

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | Entire reference set unverifiable: all 12 DOIs in the `10.5555` reserved test range with sequential suffixes; for entries naming real journals the registered publisher prefix differs; 3 journal titles unidentifiable in the field. D2 assessment on substance is impossible. | R2 (domain) — D2 `block(fatal)` | text: References, Ferreira & Lund (2022) and Okonkwo (2018) entries "https://doi.org/10.5555/1042004" "https://doi.org/10.5555/1042009" | R1 |
| 2 | Disconfirming cases excised from the analysis while full-range coverage is claimed, so the three-theme structure is preserved by construction and every dependent completeness/universal claim is unsupported. | R1 (methodology) — D1 `block(fatal)`; corroborated by EIC, R2, R3; DA C3 | text: §4.3 "balanced representation of perspectives, capturing the full range of administrator views"; "these were excluded for space, as they fell outside the three-theme structure" | R3 |
| 3 | The paper's sole design recommendation is warranted by Delacroix (2018) with the source's thesis reversed against the manuscript's own §2 and reference annotation. | All 4 non-DA seats; DA C1 | text: §5 "our findings align with Delacroix (2018), who recommends that institutions treat broad stakeholder consultation as the central mechanism for building a healthy quality culture" | R2 |

---

## Part 2: Revision Roadmap

> **Scope of "Required" under a Reject.** This is not a revise-and-resubmit invitation; F1's action is not softened. The roadmap is the rebuild path — the work required before this material could be submitted anywhere with claims of this kind, whether to this venue or to one of the alternatives in the field analysis. R5 (anonymity) and R2 (the reversed citation) apply before the text circulates at all.
>
> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. Items sourced from the DA's MAJOR table with no non-DA raiser carry `DA` as source and `—` where no sub-claim id applies.

### Sub-Claim Inventory (Step 1b, matrix form)

*Compression note: sprint-contract arithmetic mode governs the decision and does not consume this inventory, so it is presented one row per sub-claim with per-reviewer position columns rather than one row per `(sub_claim, reviewer)`. Information content is identical. Positions: `R` raised, `C` corroborated, `N` not-mentioned, `D` disputed. Severity and confidence are **transported** from the cards' per-finding tags, never re-derived; where seats differ, both are shown. No sub-claim was invented — every row decomposes a claim a reviewer actually made.*

| ID | Parent weakness | EIC | R1 meth | R2 dom | R3 persp | DA | Disposition | Severity (transported) | Conf |
|----|-----------------|-----|---------|--------|----------|-----|-------------|------------------------|------|
| SC-1 | Delacroix reversal (internal contradiction) | R | R | R | R | C1 | CONSENSUS-4 | Critical (R2) / Major (EIC, R1, R3) | 4–5 |
| SC-2 | §5 third implication rests on the reversed reading | R | C | R | C | C1 | CONSENSUS-4 | Critical (R2) / Major (EIC, R3) | 4–5 |
| SC-3 | Reference set unverifiable (`10.5555`) | N | N | R | N | — | single-reviewer | Critical | 5 |
| SC-4 | Interview N = 14 vs 12 (existence) | R | R | R | R | M1 | CONSENSUS-4 | Major (EIC, R1, R2) / Minor (R3) | 4–5 |
| SC-5 | Consequence of the N discrepancy | R | R | R | **D** | M1 | **SPLIT** → Major | Major / Minor (R3) | 4–5 |
| SC-6 | Dissenters excluded; coverage claimed | R | R | R | R | C3 | CONSENSUS-4 | Critical (R1, R3) / Major (EIC, R2) | 5 |
| SC-7 | Remedy: re-analysis vs withdraw claim | **D** | R | C | C | C3 | **SPLIT** → re-analysis | Critical (R1) | 5 |
| SC-8 | Dependent claims contaminated (§4.1, §4.2, §3.4) | C | R | C | C | C3, M9 | CONSENSUS-4 | Critical (R1) / Major | 5 |
| SC-9 | Anonymity guarantee falsified | R | R | R | R | C4 | CONSENSUS-4 | Major | 4–5 |
| SC-10 | Sector-wide / "everywhere" generalisation | R | R | R | R | C2 | CONSENSUS-4 | Major | 5 |
| SC-11 | "First comprehensive account" unsupported | R | R | R | N | M5 | CONSENSUS-3 (R3 silent) | Major (EIC, R2) / Minor (R1) | 5 |
| SC-12 | Fix scope: delete vs reposition contribution | R | **D** | C | N | M5 | **SPLIT** → both | Major (EIC, R2) / Minor (R1) | 5 |
| SC-13 | National system never named/characterised | R | N | N | R | — | corroborated (2/4) | Major | 5 |
| SC-14 | "Quality culture" undefined; QA referents slide | R | N | R | C | — | CONSENSUS-3 (R1 silent) | Major | 4–5 |
| SC-15 | "Not a management output" partly definitional | N | N | R | N | — | single-reviewer | Major | 5 |
| SC-16 | Survey instrument wholly unreported | R | R | R | R | M4 | CONSENSUS-4 | Major | 4–5 |
| SC-17 | p<.05 subgroup claim unsupportable | C | R | C | C | M3 | CONSENSUS-4 | Major | 4–5 |
| SC-18 | 28 of 48 respondents unaccounted; no private-site subgroup | C | C | C | R | M3, M4 | CONSENSUS-4 | Major (EIC, R1) / Minor (R3) | 4–5 |
| SC-19 | "Structured protocol" contradicts §3.1 | R | R | R | R | M7 | CONSENSUS-4 | Major (R1) / Minor (EIC, R2, R3) | 4–5 |
| SC-20 | §4.1 confidence warrant is a non-sequitur | C | R | N | C | M7 | CONSENSUS-3 (R2 silent) | Major (R1) / Minor (EIC, R3) | 4–5 |
| SC-21 | §4.4 labels divergence "corroborated" | N | R | N | N | M2 | single-reviewer | Major | 5 |
| SC-22 | No MM typology, sequence, or integration point | N | R | N | N | — | single-reviewer | Major | 5 |
| SC-23 | Thematic procedure non-reconstructable; no reflexivity | N | R | N | N | — | single-reviewer | Major | 5 |
| SC-24 | Gatekeeper recruitment / no sampling logic | N | R | N | C | M8 | corroborated (2/4) | Major | 5 |
| SC-25 | Interview reactivity rival explanation unaddressed | N | N | N | N | M8 | DA-only | Major (DA band) | 4 |
| SC-26 | Pre-2018 canon absent; known findings as emergent | N | N | R | N | — | single-reviewer | Major | 5 |
| SC-27 | Borrowed adjacent-field vocabulary without sources | N | N | N | R | — | single-reviewer | Major | 5 |
| SC-28 | No theoretical framework despite theorizing gap | N | N | R | C | — | corroborated (2/4) | Major | 4–5 |
| SC-29 | Implications non-operational; burden unquantified | N | N | N | R | — | single-reviewer | Major | 5 |
| SC-30 | No academic/student data yet §6 prescribes for them | N | N | N | R | — | single-reviewer | Major | 5 |
| SC-31 | Multidimensional construct measured as one mean | N | N | R | C | — | corroborated (2/4) | Major | 4 |
| SC-32 | No reproducibility affordances | N | R | N | N | — | single-reviewer | Minor | 5 |
| SC-33 | Editorial annotation in reference entry | R | N | N | N | — | single-reviewer | Minor | 5 |
| SC-34 | §6 forward-looking causal claim, no outcome measure | N | N | N | N | M6 | DA-only | Major (DA band) | 5 |
| SC-35 | No tables/figures; quantitative strand in prose | R | N | N | N | — | single-reviewer | Major | 4 |

**Decomposition note on SC-19/SC-20:** the Major-vs-Minor tag divergence on the "structured protocol" bundle dissolves once decomposed — the three Minor tags attach to the *terminology inconsistency* (SC-19), the methodology seat's Major attaches to the *warrant built on it* (SC-20). No arbitration was needed; this is the case the sub-claim protocol exists for.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| R1 | Supply resolvable DOIs and verifiable bibliographic records for all 12 sources, or withdraw the unverifiable ones and rebuild the argument on sources of record | SC-3 | Critical | text: References, Ferreira & Lund (2022) and Okonkwo (2018) entries "https://doi.org/10.5555/1042004" "https://doi.org/10.5555/1042009" | 5 — DOI prefix registration is public record | R2 (domain) | P1 | 3–5 days if records exist; indefinite if they do not |
| R2 | Resolve the Delacroix (2018) contradiction and rebuild §5's third implication on sources that support it, or reframe it as a disagreement with Delacroix | SC-1, SC-2 | Critical (R2) / Major (EIC, R1, R3) | text: §5 "our findings align with Delacroix (2018), who recommends that institutions treat broad stakeholder consultation as the central mechanism" | 5 — contradiction internal to the manuscript | All 4 non-DA; DA C1 | P1 | 2–4 days |
| R3 | Restore the excluded dissenting participants and re-analyse; withdraw or re-derive every dependent claim (§4.3 coverage, §4.1 pervasiveness, §4.2 "every interview", §3.4 "stable structure") | SC-6, SC-7, SC-8 | Critical (R1, R3) / Major (EIC, R2) | text: §4.3 "capturing the full range of administrator views"; "these were excluded for space, as they fell outside the three-theme structure" | 5 — negative-case handling is core to reflexive TA | R1 (methodology), arbitrated; DA C3, M9 | P1 | 3–5 weeks (re-analysis may change the theme structure) |
| R4 | Reconcile the interview N (14 vs 12), state the governing figure, and re-verify every count in the manuscript against it | SC-4, SC-5 | Major (arbitrated; Minor per R3) | text: Abstract and §3.2 "Fourteen administrators were interviewed in depth"; "Twelve senior administrators (n=12)" | 5 — direct arithmetic inconsistency | All 4 non-DA; DA M1 | P1 | 1 day, plus dependency on R3 |
| R5 | Replace all identifying participant descriptors with generic role labels and correct §3.5 to describe what was actually done | SC-9 | Major | text: §3.5 and §4.1 "no individual could be identified"; "the quality director of the largest private university in the region" | 5 — sample composition makes descriptors uniquely identifying | All 4 non-DA; DA C4 | P1 | 1 day |
| R6 | Rescope §5 and §6 to three institutions in one national system; delete "demonstrate", "the sector as a whole", and "administrators everywhere" | SC-10 | Major | text: §5 "administrators everywhere face the same fundamental tension between external requirement and internal meaning" | 5 — quantifier scope vs stated sampling frame | All 4 non-DA; DA C2 | P1 | 3–5 days |
| R7 | Delete the "first comprehensive account" claim, and separately argue the differentiating increment against Okonkwo (2018), Pettersen (2022), Rahman (2020), and Silva & Tan (2021) | SC-11, SC-12 | Major (EIC, R2) / Minor (R1) | text: §6 "This paper has offered the first comprehensive account of how university administrators experience and enact QA implementation" | 5 — compared against the paper's own cited work | EIC (D6 owner), arbitrated; DA M5 | P1 | Deletion 1 hour; repositioning 1–2 weeks |
| R8 | Name and characterise the national QA system: regulator, regulatory model (accreditation / audit / standards-based), funding or licensure linkage, documentation language, review-cycle stage during fieldwork | SC-13 | Major | absence: Methods §3.2 and Introduction — expected identification of the national QA system and its regulatory model; checked Abstract, §1, §3.2, §3.3, §4, §5 | 5 — standard expectation for comparative QA scholarship | EIC (D6), R3 (D4) | P1 | 2–3 days |
| R9 | Define and operationalise "quality culture" against the field's two-component canonical definition; disaggregate the referents of "QA" across the three themes; re-examine whether "not a management output" survives as a finding rather than a definitional consequence | SC-14, SC-15 | Major | absence: §1 Introduction and §3.4 Analysis — expected an operational definition distinguishing quality culture from external accreditation compliance, external review, and internal QA; checked Abstract, §1, §2, §3.3, §3.4, §4.4, §5 | 5 — conceptual distinctions are foundational here | EIC, R2, R3 | P1 | 1–2 weeks |
| R10 | Report the survey instrument in full: item wording, response-scale range and anchors, provenance or validation, sampling frame, invitation base, response rate, and handling of respondents nested in three institutions | SC-16 | Major | absence: §3.3 and §4.4 survey reporting — expected item wording, scale range and anchors, reliability or validity evidence, sampling frame, response rate; checked §3.1–§3.5, §4.4, Abstract, References | 5 — minimum survey-methods standard | All 4 non-DA; DA M4 | P1 | 3–5 days if instrument exists |
| R11 | Withdraw the p<.05 subgroup claim and the institutional-type moderator suggestion, or re-express the contrast descriptively; account for all 48 respondents including the private site; present the quantitative strand in a table | SC-17, SC-18, SC-35 | Major (Minor per R3 on the respondent accounting) | text: §4.4 "we found a statistically significant difference (p<.05) in perceived quality culture, with the teaching-focused institution scoring higher" | 5 — elementary inferential reporting requirements | R1 (D1 owner), EIC, R2, R3; DA M3 | P1 | 2–3 days |
| R12 | Report the thematic analysis procedure: named analytic tradition, stated criterion for thematic stability, coder or team process, reflexivity/positionality statement, and at least one trustworthiness check | SC-23 | Major | absence: §3.4 analysis reporting — expected named analytic approach, reflexivity or positionality statement, stability criterion, coder process, and a trustworthiness check; checked §3.1–§3.5, §4.1–§4.3, Abstract | 5 — reflexive TA reporting standards | R1 (methodology) | P1 | 4–6 days, concurrent with R3 |
| R13 | Strike the "structured protocol" warrant and the "confidence that the pattern was not an artifact" clause in §4.1; make design terminology consistent with §3.1 and §3.4 | SC-19, SC-20 | Major (R1) / Minor (EIC, R2, R3) | text: §3.1 and §4.1 "semi-structured interviews"; "These themes emerged systematically from the structured protocol, giving us confidence that the pattern was not an artifact" | 5 — internal inconsistency between declared design and findings warrant | R1, EIC, R3 (R2 on terminology); DA M7 | P1 | 1 day |
| R14 | Relabel §4.4's result as divergence rather than corroboration and bring it into line with §5; declare the mixed-methods typology, priority sequence, and point of interface, and provide a joint display | SC-21, SC-22 | Major | text: §4.4 "The survey corroborated the qualitative picture"; "the interview accounts had led us to anticipate a more skeptical picture" | 5 — standard MM integration and inference-quality criteria | R1 (methodology); DA M2 | P1 | 3–4 days |
| R15 | Name gatekeeper recruitment through the QA offices under study as a selection pressure and discuss its consequences; report how many were approached, how many declined, and the sufficiency logic governing n | SC-24 | Major | text: §3.2 "were recruited through institutional QA offices" | 5 — routine appraisal of gatekeeper-mediated access | R1, R3 | P1 | 2 days |
| R16 | Withdraw the §6 claim that meaning-making process design "are more likely to foster the internalized commitment" — the study has no outcome measure, intervention, or longitudinal component | SC-34 | Major (DA band) | text: §6 "are more likely to foster the internalized commitment that the language of quality culture promises" | 5 — no outcome variable appears in Methods or Findings | DA (M6) | P1 | 1 hour |
| R17 | Reconstruct §2 back to the field's foundational literature (institutional decoupling, audit society and audit cultures, performativity, quality-culture typologies, qualitative work on ritualism among quality staff) and reposition the three themes as confirmation and refinement within it | SC-26 | Major | absence: §2 and reference list — expected the field's foundational quality-culture and audit-culture sources predating 2018; checked all 12 references, §1 framing, §2, §5, §6 | 5 — the domain seat's own field of publication | R2 (domain, D2 owner) | P1 | 2–3 weeks |

### Required Item Details

**R1 — Reference verifiability**
All twelve DOIs sit in the `10.5555` reserved test/example range with sequential suffixes `1042001`–`1042012`; for the entries naming real journals, the registered publisher prefixes (Wiley `10.1111`, SAGE `10.1177`, Taylor & Francis `10.1080`, Emerald `10.1108`) differ, so the supplied DOIs cannot belong to the articles named. Three journal titles are not identifiable in the field. The domain seat named this as the condition it would need reversed to lift its fatal block.
- **Acceptance criteria**: every cited source resolves to a verifiable record of publication with a registered DOI or equivalent locator, and any source that cannot be verified is removed together with every claim that depended on it.

**R2 — Delacroix reversal and the dependent recommendation**
§2 and the reference-list annotation state Delacroix argues *against* consultation-as-evidence; §5 credits him with recommending consultation as the central mechanism and concludes "Consultation... is the engine of internalization." The reversed version is the one carrying the paper's sole design prescription.
- **Acceptance criteria**: the manuscript states one consistent reading of Delacroix (2018), and §5's third implication is either rebuilt on sources that support it or reframed explicitly as a disagreement with Delacroix.

**R3 — Restore the excluded cases and re-analyse**
The stated exclusion criterion is non-fit with the finding, which makes the three-theme structure unfalsifiable by the study's own data. The dissenting participants are precisely the disconfirming cases for the paper's central thesis that administrators recover meaning from ritual. Arbitrated against the EIC's alternative remedy: withdrawing §4.3's coverage sentence leaves §4.1's pervasiveness claim and §4.2's universal quantifier standing on the same reduced corpus.
- **Acceptance criteria**: the dissenting accounts are included in the analysed corpus and reported, the theme structure is re-derived against the full corpus with any change disclosed, and no completeness or universal claim rests on a corpus from which non-conforming cases were removed.

**R4 — Reconcile the sample size**
The Abstract reports fourteen, §3.2 reports twelve twice. Arbitrated to Major: the resolution may determine whether the two missing interviews are the excluded dissenters, which changes how §4.3 must be read.
- **Acceptance criteria**: one interview N governs throughout the manuscript, its relationship to any excluded participants is stated, and every count in the Abstract, Methods, and Findings reconciles with it.

**R5 — Anonymity**
§3.5 guarantees no individual could be identified; §4.1 attributes quotations to "the quality director of the largest private university in the region" and "the associate dean for quality at the public research university." With one private and one research university in the sample these are identifiers, and the quotations are unflattering about the participants' employers.
- **Acceptance criteria**: no participant attribution permits identification of an institution or post-holder, and §3.5 describes the de-identification actually performed.

**R6 — Rescope the inferential reach**
§5 asserts the findings "demonstrate that universities across the sector treat QA as a negotiated accomplishment," offers the study as "a general account of how the higher education sector as a whole constructs quality culture," and claims "administrators everywhere" face the same tension — while §6 asks future research to test the dynamics across systems.
- **Acceptance criteria**: every claim in §5 and §6 is scoped to the administrators interviewed at the three studied institutions within one national system, and no sector-level or cross-national generalisation remains.

**R7 — Priority claim and contribution**
Two separable tasks, per the SC-12 arbitration. The sentence deletion is free. The contribution deficit is not: the three themes map one-to-one onto three works the paper itself cites, and the manuscript nowhere states what it adds.
- **Acceptance criteria**: the priority claim is removed, and the manuscript states in the Introduction and Conclusion what its account adds to Okonkwo (2018), Pettersen (2022), Rahman (2020), and Silva & Tan (2021) specifically.

**R8 — Name the system**
"Three universities in a single national system" gives an international readership nothing usable; a reader cannot determine what the described ritual compliance is compliance *with*, and cannot judge transfer to their own setting.
- **Acceptance criteria**: the national system, its regulatory model, any funding or licensure linkage, the documentation language, and the review-cycle stage during fieldwork are all stated in the Methods.

**R9 — Define and disaggregate the construct**
The title construct is carried by a single gloss and by a survey score whose instrument is undescribed. The three themes attach "QA" to three different objects — externally driven documentation, internal governance, professional self-understanding — which is what makes the tripartite finding look more unified than it is. The domain seat adds that dropping the managerial component of the canonical definition makes the "not a management output" conclusion partly true by definition.
- **Acceptance criteria**: quality culture is operationally defined and distinguished from external accreditation compliance, external review, and internal QA; each theme names the object its "QA" refers to; and the "not a management output" conclusion is re-derived against a definition that does not presuppose it.

**R10 — Report the instrument**
Without scale range, M=3.9 is uninterpretable: 3.9 on a five-point and 3.9 on a seven-point scale are different findings, and one would not support "moderately positive."
- **Acceptance criteria**: the survey instrument, its response scale and anchors, its provenance or validation evidence, the sampling frame, the response rate, and the treatment of respondents nested within three institutions are all reported, or every survey-derived claim is removed.

**R11 — Quantitative reporting**
The p<.05 claim names no test, reports no group means, degrees of freedom, or effect size, applies no correction, perfectly confounds institution with group, and drops the third site. Twenty-eight of forty-eight respondents are never allocated. The manuscript contains no tables or figures at all.
- **Acceptance criteria**: no inferential claim or moderator suggestion is made from the subgroup comparison unless a named test with effect size, dispersion, and clustering treatment supports it; all 48 respondents are accounted for by site; and the quantitative results appear in a table.

**R12 — Thematic analysis procedure**
§3.4 gives two sentences: no named tradition, no stability criterion, no coder process, no reflexivity or positionality despite an interpretive design, no trustworthiness check.
- **Acceptance criteria**: a reader can reconstruct how the themes were produced and by whom, including the analytic tradition, the stability criterion, the coder or team process, a positionality statement, and at least one trustworthiness procedure.

**R13 — Design description and warrant**
Semi-structured interviews do not have a "structured protocol," themes cannot both emerge inductively and be produced systematically by a protocol, and protocol uniformity cannot establish that a cross-site pattern is not an artifact.
- **Acceptance criteria**: the design is described identically in §3.1, §3.4, and §4.1, and no validity or non-artifact claim is warranted by protocol structure.

**R14 — Divergence and integration**
§4.4 opens by calling the survey corroboration and two sentences later concedes the interviews had led the authors to expect the opposite. §5 already reads this correctly as divergence; §4.4 must match. Separately, "mixed methods" is asserted without typology, sequence, interface, or joint display.
- **Acceptance criteria**: §4.4 describes the survey result as divergent from the interview-based expectation and explains the divergence, and the Methods name the mixed-methods design typology, priority sequence, and point of integration with a joint display.

**R15 — Recruitment and sampling logic**
Participants were recruited through the QA offices whose work is the object of study — a selection pressure toward administrators invested in QA, which plausibly explains why dissent appeared only as a residual minority. The manuscript neither names it nor reports any sufficiency logic.
- **Acceptance criteria**: the gatekeeper recruitment route is named as a selection pressure with its consequences discussed, and the Methods report the approach/decline counts and the logic governing sample sufficiency.

**R16 — Forward-looking causal claim**
§6 predicts what QA process design produces, from a study with no outcome measure, no intervention, and no longitudinal component.
- **Acceptance criteria**: no claim about what QA process design causes or is likely to produce appears anywhere in the manuscript.

**R17 — Reconstruct the literature base**
No source predates 2018 in a field whose defining works are older. Theme 1 restates institutional decoupling under a new label; Theme 3 restates a documented finding about how quality staff hold the compliance/meaning tension open. This is also the mechanism by which R7's repositioning becomes possible.
- **Acceptance criteria**: §2 engages the field's foundational literature and the three themes are positioned as confirmation and refinement within a cumulative literature rather than as emergent discoveries.

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| S1 | Declare and apply a theoretical framework, or restate the §1 gap claim as descriptive rather than a theorizing gap | SC-28 | Major | absence: §1 and §3.4 — expected a declared theoretical or conceptual framework connecting the three themes to cumulative scholarship; checked §1, §2 strand three, §3.4, §5 | 4 — judgement about what counts as theory here | R2, R3 | P2 | 1–2 weeks |
| S2 | Cite the adjacent-field literatures whose vocabulary the paper already uses: street-level bureaucracy on discretion under conflicting mandates, institutional work and decoupling on legitimacy maintenance, professional-identity work on coping resources | SC-27 | Major | text: §4.3 "This vocational framing appeared to function as a coping resource" | 5 — the perspective seat's own publishing area | R3 (perspective) | P2 | 4–6 days |
| S3 | Address the construct/measure mismatch: justify a unidimensional mean for a construct the field treats as multidimensional and typological, or narrow the survey claims accordingly | SC-31 | Major | absence: §3.3 and §4.4 — expected named instrument, item wording, or scale provenance for the measure reported as M=3.9; checked §3.3, §3.4, §4.4, References | 4 — familiar with the instruments, less with their psychometrics | R2, R3 | P2 | 2–3 days, concurrent with R10 |
| S4 | Make the practical implications operational and quantify the documentation burden the paper diagnoses: what to stop doing, the staff-time substitution cost, what a regulator would have to relax, and how a panel distinguishes a meaningful process from a well-documented one | SC-29 | Major | text: §5 and §6 "processes that maximize genuine participation should be favored"; "create room for meaning-making rather than merely demanding documentation" | 5 — the seat is the audience the recommendations address | R3 (perspective) | P2 | 1 week |
| S5 | Either acknowledge that the prescriptions rest on administrator self-report alone, or confine the claims to administrative experience — academics and students appear nowhere in the data yet §6 pronounces on processes for them | SC-30 | Major | absence: §3.2 and §4 — expected accounts from academics or students on whom QA acts, given the institution-wide prescriptions in §6; checked §3.2–§3.3, §4.1–§4.4, §5, §6 | 5 — the population claimed about must appear in the evidence base | R3 (perspective) | P2 | 2 days |
| S6 | Confront interview reactivity as a rival explanation: the paper's own third theme is that administrators construct identity through moral framing of QA work, and an interview with an external researcher is exactly the setting in which such framing would be performed | SC-25 | Major (DA band) | text: §3.2 "were recruited through institutional QA offices" | 4 — reactivity risk evident from the stated design | DA (M8) | P2 | 2 days, concurrent with R12 |
| S7 | Supply reproducibility affordances: interview protocol or topic guide, coding frame or codebook, survey instrument as an appendix, and a data-availability or materials statement | SC-32 | Minor | absence: Methods and back matter — expected interview protocol, coding frame or codebook, and a data-availability or materials statement; checked §3.1–§3.5, §4, §6, References | 5 — direct check of the manuscript's surfaces | R1 (methodology) | P3 | 2 days |
| S8 | Remove the italicised editorial annotation from the Delacroix reference entry or move its content into the body | SC-33 | Minor | text: References "Delacroix argues against relying on stakeholder consultation as evidence of quality culture" | 5 — venue reference conventions | EIC | P3 | 15 minutes |
| S9 | Copyedit and rebalance: §4.4 is a single paragraph carrying the entire quantitative contribution; section proportions are uneven; the central construct is undefined on first use | — (editorial channel; `source_kind: editorial`) | — (below finding threshold) | — | — | EIC (D5 `warn`) | P3 | 2–3 days |

> Transported metadata appears on every row above, not only on the three Top Blocking rows: each item carries the driving sub-claim's transported Severity (with per-seat divergence shown where seats differ), the finding's typed Evidence Anchor, and its per-finding Confidence. No `[SEVERITY-SOURCE: letter-fallback]` or `[CONFIDENCE-SOURCE: report-level]` tags were needed — all five cards carry per-finding severity and confidence tags, except the DA's tables where severity is the section band (noted as "DA band") and S9, which derives from the EIC's D5 dimension narrative rather than from a tagged finding.

### Revision Checklist

#### Priority 1 — Structural (estimated total: 10–14 weeks, R1 and R3 on the critical path)
- [ ] R1: Verify or withdraw all 12 references
- [ ] R2: Resolve Delacroix; rebuild or reframe §5's third implication
- [ ] R3: Restore dissenting cases; re-analyse; re-derive dependent claims
- [ ] R4: Reconcile the interview N and re-verify every count
- [ ] R5: De-identify participant attributions; correct §3.5
- [ ] R6: Rescope §5 and §6 to three institutions in one system
- [ ] R7: Delete the priority claim; argue the differentiating increment
- [ ] R8: Name and characterise the national QA system
- [ ] R9: Define and operationalise quality culture; disaggregate QA referents
- [ ] R10: Report the survey instrument in full
- [ ] R11: Withdraw or redescribe the subgroup claim; account for all 48; add a table
- [ ] R12: Report the thematic analysis procedure and positionality
- [ ] R13: Strike the §4.1 warrant; make design terminology consistent
- [ ] R14: Relabel divergence; declare MM typology and integration
- [ ] R15: Name gatekeeper selection; report sampling logic
- [ ] R16: Withdraw the §6 forward-looking causal claim
- [ ] R17: Reconstruct §2 to the field's foundational literature

#### Priority 2 — Content supplementation (estimated total: 3–4 weeks, partly concurrent)
- [ ] S1: Declare and apply a theoretical framework
- [ ] S2: Cite the adjacent-field literatures already being borrowed from
- [ ] S3: Justify or narrow the unidimensional quality-culture measure
- [ ] S4: Operationalise the implications; quantify the documentation burden
- [ ] S5: Acknowledge or confine the administrator-only evidence base
- [ ] S6: Confront interview reactivity as a rival explanation

#### Priority 3 — Text and formatting (estimated total: 3–4 days)
- [ ] S7: Supply protocol, codebook, instrument, and data-availability statement
- [ ] S8: Remove the annotation from the Delacroix reference entry
- [ ] S9: Copyedit; rebalance sections; expand §4.4 beyond a single paragraph

### Revision Deadline

**Not applicable — this is a Reject, not a revise-and-resubmit.** No resubmission window is held open at this venue for this manuscript. For planning a future submission, the P1 critical path is 10–14 weeks, dominated by R3 (re-analysis with the dissenting cases restored, whose outcome may change the theme structure) and R17/R7 (literature reconstruction and contribution repositioning). R1 gates everything: if the twelve sources cannot be verified, the remaining items are moot.

Two items are not deferrable to any future submission cycle. R5 (identifying attributions against a consent-backed anonymity guarantee) and R2 (a cited author credited with the reverse of his argument) should be corrected before this text circulates further in any form.

On venue: the field analysis identifies *Quality in Higher Education*, *Higher Education Quarterly*, and *Journal of Higher Education Policy and Management* as the closest fits, with a reframed exploratory three-institution study — survey removed or demoted to descriptive context — as the fallback. That choice interacts with R6, R8, and R9 and is worth settling before the rewrite rather than after.

### Response Letter Template

For any future submission, use `templates/revision_response_template.md` and respond to every numbered item above (R1–R17, S1–S9) individually, stating what changed and where. Items R3, R7, and R11 carry arbitrated resolutions that differ from at least one reviewer's stated preference; the arbitration rationale is in the Points of Disagreement section, and a response that addresses only the minority position will read as unresponsive.

### Machine-Form Roadmap (Schema 7)

```json
{
  "schema": "roadmap/7",
  "contract_id": "reviewer/reviewer_full/v2",
  "editorial_decision": "reject",
  "items": [
    {"id": "R1", "priority": "must_fix", "reviewer": "domain", "severity": "critical", "confidence": 5, "sub_claims": ["SC-3"], "source_kind": "finding", "evidence_anchor": "text: References, Ferreira & Lund (2022) and Okonkwo (2018) entries \"https://doi.org/10.5555/1042004\" \"https://doi.org/10.5555/1042009\"", "verification_criteria": "Every cited source resolves to a verifiable record of publication with a registered DOI or equivalent locator; unverifiable sources removed together with every dependent claim."},
    {"id": "R2", "priority": "must_fix", "reviewer": "eic,methodology,domain,perspective,da", "severity": "critical", "confidence": 5, "sub_claims": ["SC-1", "SC-2"], "source_kind": "finding", "evidence_anchor": "text: §5 \"our findings align with Delacroix (2018), who recommends that institutions treat broad stakeholder consultation as the central mechanism\"", "verification_criteria": "One consistent reading of Delacroix (2018) throughout; §5's third implication rebuilt on supporting sources or reframed as disagreement with Delacroix."},
    {"id": "R3", "priority": "must_fix", "reviewer": "methodology", "severity": "critical", "confidence": 5, "sub_claims": ["SC-6", "SC-7", "SC-8"], "source_kind": "finding", "evidence_anchor": "text: §4.3 \"capturing the full range of administrator views\"; \"these were excluded for space, as they fell outside the three-theme structure\"", "verification_criteria": "Dissenting accounts included in the analysed corpus and reported; theme structure re-derived against the full corpus with any change disclosed; no completeness or universal claim rests on the reduced corpus."},
    {"id": "R4", "priority": "must_fix", "reviewer": "eic,methodology,domain,perspective,da", "severity": "major", "confidence": 5, "sub_claims": ["SC-4", "SC-5"], "source_kind": "finding", "evidence_anchor": "text: Abstract and §3.2 \"Fourteen administrators were interviewed in depth\"; \"Twelve senior administrators (n=12)\"", "verification_criteria": "One governing interview N throughout; its relation to any excluded participants stated; all counts reconcile."},
    {"id": "R5", "priority": "must_fix", "reviewer": "eic,methodology,domain,perspective,da", "severity": "major", "confidence": 5, "sub_claims": ["SC-9"], "source_kind": "finding", "evidence_anchor": "text: §3.5 and §4.1 \"no individual could be identified\"; \"the quality director of the largest private university in the region\"", "verification_criteria": "No attribution permits identification of an institution or post-holder; §3.5 describes the de-identification actually performed."},
    {"id": "R6", "priority": "must_fix", "reviewer": "eic,methodology,domain,perspective,da", "severity": "major", "confidence": 5, "sub_claims": ["SC-10"], "source_kind": "finding", "evidence_anchor": "text: §5 \"administrators everywhere face the same fundamental tension between external requirement and internal meaning\"", "verification_criteria": "All §5 and §6 claims scoped to the administrators at the three studied institutions in one national system; no sector-level or cross-national generalisation remains."},
    {"id": "R7", "priority": "must_fix", "reviewer": "eic", "severity": "major", "confidence": 5, "sub_claims": ["SC-11", "SC-12"], "source_kind": "finding", "evidence_anchor": "text: §6 \"This paper has offered the first comprehensive account of how university administrators experience and enact QA implementation\"", "verification_criteria": "Priority claim removed; Introduction and Conclusion state what the account adds to Okonkwo (2018), Pettersen (2022), Rahman (2020), and Silva & Tan (2021) specifically."},
    {"id": "R8", "priority": "must_fix", "reviewer": "eic,perspective", "severity": "major", "confidence": 5, "sub_claims": ["SC-13"], "source_kind": "finding", "evidence_anchor": "absence: Methods §3.2 and Introduction — expected identification of the national QA system and its regulatory model; checked Abstract, §1, §3.2, §3.3, §4, §5", "verification_criteria": "Methods state the national system, regulatory model, funding or licensure linkage, documentation language, and review-cycle stage during fieldwork."},
    {"id": "R9", "priority": "must_fix", "reviewer": "eic,domain,perspective", "severity": "major", "confidence": 5, "sub_claims": ["SC-14", "SC-15"], "source_kind": "finding", "evidence_anchor": "absence: §1 Introduction and §3.4 Analysis — expected an operational definition distinguishing quality culture from external accreditation compliance, external review, and internal QA; checked Abstract, §1, §2, §3.3, §3.4, §4.4, §5", "verification_criteria": "Quality culture operationally defined and distinguished from adjacent constructs; each theme names its QA referent; the 'not a management output' conclusion re-derived against a non-presupposing definition."},
    {"id": "R10", "priority": "must_fix", "reviewer": "eic,methodology,domain,perspective,da", "severity": "major", "confidence": 5, "sub_claims": ["SC-16"], "source_kind": "finding", "evidence_anchor": "absence: §3.3 and §4.4 survey reporting — expected item wording, scale range and anchors, reliability or validity evidence, sampling frame, response rate; checked §3.1–§3.5, §4.4, Abstract, References", "verification_criteria": "Instrument, scale anchors, provenance or validation, sampling frame, response rate, and clustering treatment reported; otherwise all survey-derived claims removed."},
    {"id": "R11", "priority": "must_fix", "reviewer": "methodology,eic,domain,perspective,da", "severity": "major", "confidence": 5, "sub_claims": ["SC-17", "SC-18", "SC-35"], "source_kind": "finding", "evidence_anchor": "text: §4.4 \"we found a statistically significant difference (p<.05) in perceived quality culture, with the teaching-focused institution scoring higher\"", "verification_criteria": "No inferential or moderator claim without a named test, effect size, dispersion, and clustering treatment; all 48 respondents accounted for by site; quantitative results presented in a table."},
    {"id": "R12", "priority": "must_fix", "reviewer": "methodology", "severity": "major", "confidence": 5, "sub_claims": ["SC-23"], "source_kind": "finding", "evidence_anchor": "absence: §3.4 analysis reporting — expected named analytic approach, reflexivity or positionality statement, stability criterion, coder process, and a trustworthiness check; checked §3.1–§3.5, §4.1–§4.3, Abstract", "verification_criteria": "A reader can reconstruct how the themes were produced and by whom: analytic tradition, stability criterion, coder or team process, positionality statement, and at least one trustworthiness procedure."},
    {"id": "R13", "priority": "must_fix", "reviewer": "methodology,eic,perspective,domain,da", "severity": "major", "confidence": 5, "sub_claims": ["SC-19", "SC-20"], "source_kind": "finding", "evidence_anchor": "text: §3.1 and §4.1 \"semi-structured interviews\"; \"These themes emerged systematically from the structured protocol, giving us confidence that the pattern was not an artifact\"", "verification_criteria": "Design described identically in §3.1, §3.4, and §4.1; no validity or non-artifact claim warranted by protocol structure."},
    {"id": "R14", "priority": "must_fix", "reviewer": "methodology,da", "severity": "major", "confidence": 5, "sub_claims": ["SC-21", "SC-22"], "source_kind": "finding", "evidence_anchor": "text: §4.4 \"The survey corroborated the qualitative picture\"; \"the interview accounts had led us to anticipate a more skeptical picture\"", "verification_criteria": "§4.4 describes the survey result as divergent and explains the divergence; Methods name the mixed-methods typology, priority sequence, and integration point, with a joint display."},
    {"id": "R15", "priority": "must_fix", "reviewer": "methodology,perspective,da", "severity": "major", "confidence": 5, "sub_claims": ["SC-24"], "source_kind": "finding", "evidence_anchor": "text: §3.2 \"were recruited through institutional QA offices\"", "verification_criteria": "Gatekeeper recruitment named as a selection pressure with consequences discussed; approach and decline counts and the sample-sufficiency logic reported."},
    {"id": "R16", "priority": "must_fix", "reviewer": "da", "severity": "major", "confidence": 5, "sub_claims": ["SC-34"], "source_kind": "finding", "evidence_anchor": "text: §6 \"are more likely to foster the internalized commitment that the language of quality culture promises\"", "verification_criteria": "No claim about what QA process design causes or is likely to produce appears anywhere in the manuscript."},
    {"id": "R17", "priority": "must_fix", "reviewer": "domain", "severity": "major", "confidence": 5, "sub_claims": ["SC-26"], "source_kind": "finding", "evidence_anchor": "absence: §2 and reference list — expected the field's foundational quality-culture and audit-culture sources predating 2018; checked all 12 references, §1 framing, §2, §5, §6", "verification_criteria": "§2 engages the field's foundational literature and the three themes are positioned as confirmation and refinement within it rather than as emergent discoveries."},
    {"id": "S1", "priority": "should_fix", "reviewer": "domain,perspective", "severity": "major", "confidence": 4, "sub_claims": ["SC-28"], "source_kind": "finding", "evidence_anchor": "absence: §1 and §3.4 — expected a declared theoretical or conceptual framework connecting the three themes to cumulative scholarship; checked §1, §2 strand three, §3.4, §5", "verification_criteria": "A framework is declared and applied to the themes, or the §1 gap claim is restated as descriptive rather than theorizing."},
    {"id": "S2", "priority": "should_fix", "reviewer": "perspective", "severity": "major", "confidence": 5, "sub_claims": ["SC-27"], "source_kind": "finding", "evidence_anchor": "text: §4.3 \"This vocational framing appeared to function as a coping resource\"", "verification_criteria": "Each borrowed construct is either cited to the literature that defines it or replaced with the paper's own terminology."},
    {"id": "S3", "priority": "should_fix", "reviewer": "domain,perspective", "severity": "major", "confidence": 4, "sub_claims": ["SC-31"], "source_kind": "finding", "evidence_anchor": "absence: §3.3 and §4.4 — expected named instrument, item wording, or scale provenance for the measure reported as M=3.9; checked §3.3, §3.4, §4.4, References", "verification_criteria": "A unidimensional mean is justified for the construct, or the survey claims are narrowed to what a single composite supports."},
    {"id": "S4", "priority": "should_fix", "reviewer": "perspective", "severity": "major", "confidence": 5, "sub_claims": ["SC-29"], "source_kind": "finding", "evidence_anchor": "text: §5 and §6 \"processes that maximize genuine participation should be favored\"; \"create room for meaning-making rather than merely demanding documentation\"", "verification_criteria": "Each recommendation states what to stop doing, its staff-time cost, what a regulator would have to change, and how a panel would distinguish a meaningful from a well-documented process; the documentation burden is quantified."},
    {"id": "S5", "priority": "should_fix", "reviewer": "perspective", "severity": "major", "confidence": 5, "sub_claims": ["SC-30"], "source_kind": "finding", "evidence_anchor": "absence: §3.2 and §4 — expected accounts from academics or students on whom QA acts, given the institution-wide prescriptions in §6; checked §3.2–§3.3, §4.1–§4.4, §5, §6", "verification_criteria": "Prescriptions are confined to administrative experience, or the reliance on administrator self-report alone is stated as a limitation on their reach."},
    {"id": "S6", "priority": "should_fix", "reviewer": "da", "severity": "major", "confidence": 4, "sub_claims": ["SC-25"], "source_kind": "finding", "evidence_anchor": "text: §3.2 \"were recruited through institutional QA offices\"", "verification_criteria": "Interview reactivity and self-presentation are addressed as rival explanations for the identity and leadership themes."},
    {"id": "S7", "priority": "should_fix", "reviewer": "methodology", "severity": "minor", "confidence": 5, "sub_claims": ["SC-32"], "source_kind": "finding", "evidence_anchor": "absence: Methods and back matter — expected interview protocol, coding frame or codebook, and a data-availability or materials statement; checked §3.1–§3.5, §4, §6, References", "verification_criteria": "Protocol, codebook, survey instrument, and a data-availability or materials statement are supplied."},
    {"id": "S8", "priority": "should_fix", "reviewer": "eic", "severity": "minor", "confidence": 5, "sub_claims": ["SC-33"], "source_kind": "finding", "evidence_anchor": "text: References \"Delacroix argues against relying on stakeholder consultation as evidence of quality culture\"", "verification_criteria": "No reference entry carries an editorial annotation; any needed characterisation of a source appears in the body."},
    {"id": "S9", "priority": "should_fix", "reviewer": "eic", "sub_claims": [], "source_kind": "editorial", "verification_criteria": "Section proportions rebalanced, §4.4 developed beyond a single paragraph, and the central construct defined at first use."}
  ]
}
```

---

## Part 3: Reviewer Report Summary (Appendix)

*Under this contract the reviewer cards emit per-dimension scores rather than an overall Accept/Revise/Reject recommendation, and confidence is per-finding rather than report-level. Both are reported as such below; neither is inferred.*

### Journal-Fit Reviewer (EIC)
- Owned dimensions: D5 `warn`; D6 `block` (repairable). Confidence range across findings: 4–5 (mode 5).
- Key point: the manuscript belongs in this journal on topic and method, but its three themes map one-to-one onto three works it cites without ever stating what it adds — so the "first comprehensive account" claim is contradicted by its own bibliography, and the unnamed national system makes the finding uninterpretable for a comparative readership.

### Peer Reviewer 1 (Methodology)
- Owned dimensions: D1 `block` (**fatal**, bound on §4.3 alone); D3 `block` (repairable). Confidence range: 4–5 (mode 5).
- Key point: the described procedure could not have produced the reported results — the disconfirming cases were excised from the analysis the Findings report, so the evidence would have to be regenerated rather than documented; the survey strand is unevaluable as reported.

### Peer Reviewer 2 (Domain)
- Owned dimensions: D2 `block` (**fatal**). Confidence range: 4–5 (mode 5).
- Key point: all twelve DOIs use the reserved `10.5555` test prefix and contradict the named publishers, so no claim about prior work can be checked; and the manuscript rediscovers institutional decoupling and documented ritualism findings as emergent themes because no source predates 2018.

### Peer Reviewer 3 (Cross-disciplinary / Perspective)
- Owned dimensions: D4 `block` (no `block_class` declared). Confidence range: 4–5 (mode 5).
- Key point: claim scope exceeds evidence scope and the operative constructs are undescribed, so no outside reader can judge transfer; the paper reproduces a managerial account of quality from inside the quality office while presenting itself as a critique of managerialism, with academics, students, the regulator, and the dissenting administrators all absent.

### Devil's Advocate
- Owned dimensions: D3 `block` (repairable). Four CRITICAL findings, nine MAJOR. Confidence range: 4–5.
- Key point: the shortest hostile route runs entirely through the manuscript's own text — the sole design recommendation is warranted by a source the paper elsewhere describes as arguing the opposite, and the theme structure that carries the analysis is preserved by the acknowledged removal of the participants who dissented from it.

Sincerely,
Managing Editor
