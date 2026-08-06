# Editorial Decision Package

**Manuscript:** *Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students*
**Contract:** `reviewer/reviewer_full/v2` · stage `reviewer_full_review` · baseline `v3.20.0` · `panel_size: 5`
**Synthesis mode:** v3.6.2 Sprint Contract Synthesizer Protocol (arithmetic) for the decision; general Synthesis Protocol for the consensus analysis and roadmap. The consensus analysis below does **not** modify the mechanical decision.

---

## Sprint Contract Audit (mechanical — Steps 1–3)

### Step 1 — Role-scoped scoring matrix

| Dim | Priority | Eligible roles | Assessed eligible seats (score) | Ineligible / not_assessed | Dimension verdict |
|-----|----------|----------------|----------------------------------|---------------------------|-------------------|
| D1 methodology_rigor | mandatory | methodology | methodology = `warn` | eic, domain, perspective, da → excluded | `warn` |
| D2 domain_accuracy | mandatory | domain | domain = `block`, `block_class: fatal` | eic, methodology, perspective, da → excluded | `block(fatal)` |
| D3 argumentative_coherence | mandatory | da, methodology | da = `warn`; methodology = `warn` | eic, domain, perspective → excluded | `warn` |
| D4 cross_disciplinary_relevance | high | perspective | perspective = `warn` | all others → excluded | `warn` |
| D5 writing_and_structure | normal | eic | eic = `warn` | all others → excluded | `warn` |
| D6 venue_fit_and_contribution | mandatory | eic | eic = `block`, `block_class: repairable` | all others → excluded | `block` |

No dimension is unassessed by its eligible seats; no `[DIMENSION-UNASSESSED]` marker applies. **Audit verdict: `block(fatal)`** (worst assessed eligible score is `block`; one assessed eligible seat — domain on D2 — declared a fatal block).

Two exclusions are load-bearing and stated for the record:
- The Journal-Fit Reviewer classified the reference defect as **repairable** and the domain reviewer classified it as **fatal**. The Journal-Fit Reviewer is **not eligible** on D2; its `repairable` classification sits on D6 (a different dimension). An ineligible seat does not vote, so it cannot offset D2's fatal declaration.
- The devil's advocate is eligible on D3 only. Its six MAJOR findings inform the roadmap; they do not enter any other dimension's score.

### Step 2 — Failure-condition evaluation

| ID | Sev | Cross-reviewer quantifier | Expression | Evaluation | Fired |
|----|-----|---------------------------|------------|------------|-------|
| F1 | 95 | any | any mandatory dimension has a fatal block | Mandatory = D1,D2,D3,D6. `any` seat: D2 → domain declared `block_class: fatal` → true. Dimension quantifier `any`: ≥1 → true. Fatal scope valid (D2 is mandatory). | **true** |
| F2 | 90 | any | any mandatory dimension scores 'block' | D2 = block (true), D6 = block (true) under `any`. Dimension `any` → true. | **true** |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1: n=1 → owner seat (methodology) = warn → true. D2: n=1 → block → true. D3: n=2 → majority = both seats; da=warn, methodology=warn → true. D6: n=1 → block → true. Four ≥ two. | **true** |
| F4 | 60 | any | any high-priority dimension scores 'block' | High = D4 only. perspective = warn, not block → false. | false |
| F5 | 40 | any | any dimension scores 'warn' or worse | D1 = warn under `any` → true. | **true** |
| F0 | 10 | all | every dimension scores 'pass' | D1 = warn → false. | false |

All six expressions parsed inside the closed vocabulary; no `[EXPRESSION-UNRECOGNISED]` marker applies.

### Step 3 — Precedence and emission

Fired conditions ranked by severity: F1 (95) > F2 (90) > F3 (70) > F5 (40). Highest severity selects **F1 → `editorial_decision=reject`**.

```
dimension_verdicts: [D1=warn, D2=block(fatal), D3=warn, D4=warn, D5=warn, D6=block]
fired_conditions: [F1, F2, F3, F5]
da_critical_adjudications: []
editorial_decision=reject
```

`da_critical_adjudications: []` is correct, not an omission: the devil's advocate emitted a CRITICAL table containing a header and **zero rows**. Its six findings are all banded MAJOR and therefore carry no `C<n>` identifiers requiring adjudication. No `[DA-CRITICAL-VS-ACCEPT]` marker applies (the mechanical decision is `reject`, not `accept`).

### Card-integrity flags (advisory — flagged, not fixed)

- `[CARD-ARTIFACT: domain]` — the domain card's "Scoring Plan Dissent" section opens with a placeholder line followed by the reviewer's own self-correction ("*Wait — that placeholder is itself a protocol violation. Corrected output follows.*"). The `contract_role`, all six dimension scores, block class, trigger, and every finding are present and parseable, so the card is usable and was scored as submitted. I am flagging the artifact, not editing the card.
- `[CARD-INPUT-NOTE]` — the contract's `measurement_procedure.reviewer_must_output_before_paper` requires `contract_paraphrase` and `scoring_plan` from each seat. Neither artifact appears in the material forwarded to me; each card does quote its own dimension-level `trigger` text, which is consistent with a scoring plan having existed upstream. This may be forwarding truncation rather than reviewer non-compliance. I cannot distinguish the two from what I hold, and I did not assume compliance either way — no seat was dropped, and no `[PANEL-SHRUNK]` condition arose.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript to *Education and Information Technologies*. It was assessed by five independent reviewers: a Journal-Fit Reviewer, a quantitative survey methodologist, a domain specialist in technology acceptance in higher education, a learning-analytics/institutional-research reviewer, and an adversarial reviewer charged with attacking the argument's coherence.

### Decision: Reject

The decision follows the acceptance contract mechanically. Domain accuracy — a mandatory dimension — carries a fatal block on the ground that the entire reference apparatus is unverifiable. That fires the contract's highest-severity condition (F1), whose action is rejection. Three further conditions also fired (F2, F3, F5) and would independently have produced a major-revision outcome; they are recorded above for completeness but do not compete with F1 on precedence.

I want to be equally clear about what this decision is **not**. It is not a judgement that the study was incompetently executed, and it is not a finding of misconduct. Four of five reviewers volunteered, unprompted, that the manuscript's epistemic restraint is genuine and unusual: the correlational language holds from abstract to conclusion, the reverse-causation pathway is named in the Discussion rather than buried in Limitations, and the self-report measure is treated as an indicator of perceived use in the body of the paper. Three reviewers independently recomputed the Fisher-z interval and confirmed that the reported 95% CI [.30, .52] is exactly what the standard procedure returns for *r* = .42 at *n* = 214 — correcting a hint in the reviewer brief that had suggested an upper limit near .53. The sample accounting (233 − 14 − 5 = 214) reconciles across the abstract, §3.1, and §7. If the reference base can be authenticated, most of this manuscript's substance survives, and the roadmap below is the path.

### Points of Agreement (Consensus)

Consensus is counted over the four non-devil's-advocate seats, per sub-claim, with `not-mentioned` treated as silence rather than agreement.

- **[CONSENSUS-4]** The six adapted perceived-usefulness item stems are never reproduced and the nature of the adaptation is never documented. *(SC-6 — all four seats; corroborated independently for four different reasons: instrument-disclosure convention, α interpretability, the "validated instrument" warrant, and replication.)*
- **[CONSENSUS-3]** No prior coefficient, range, or pooled estimate appears anywhere in the manuscript, so "consistent with prior technology-acceptance research" is unfalsifiable as written. *(SC-3 — Journal-Fit Reviewer, R1, R2 agree; **R3 silent**; also raised by the devil's advocate as M4 at confidence 5.)*
- **[CONSENSUS-3]** The shared-variance quantity is characterised adjectivally ("modest") where *r*² = .18 would state it in one number. *(SC-5 — Journal-Fit Reviewer, R1, R2 agree; **R3 silent**.)*
- **[CONSENSUS-3]** Only the endpoint anchors of the five-point use item are reported, so the reported median category cannot be located on the scale or compared externally. *(SC-29 — R1, R2, R3 agree; **Journal-Fit Reviewer silent**.)*

Below the consensus bar but action-bearing, and the most consequential finding in the package: **SC-1**, the unverifiable reference apparatus, is a **2/4 corroborated finding** — raised by the Journal-Fit Reviewer and the domain reviewer at Critical severity and confidence 5 each. It is a 2/4 finding because R1 and R3 never addressed the reference list at all, not because either dissented. Both seats that corroborated it are the two the field analysis assigned the verification task, and both are the eligible owners of the dimensions the finding blocks. Under the confidence-weighting rule (quality of expertise over quantity of opinion), this drives the decision despite the count.

### Points of Disagreement

Five genuine conflicts were identified. Each is arbitrated below; the arbitration governs the roadmap's priority assignment, and none of it alters the mechanical decision.

**D-1. Is the reference defect repairable or fatal? (SC-22)**
- R2 (domain): fatal — "not repairable by revising text: it requires rebuilding the literature base from scratch and re-establishing what instrument was actually administered."
- Journal-Fit Reviewer: a synthesized placeholder set requiring an authenticity query, suspension of substantive review, and referral only if records cannot be produced; scored its own dimension `repairable`.
- **Editor's Resolution:** Both seats agree the defect is acceptance-blocking as submitted; they differ on process stage, and the two paths converge. The arbitrated position is conditional: **if** resolvable records for all six works are produced, the defect reduces to a correction plus the literature-base rebuild in item R2; **if** they cannot be produced, R2's reading holds and the prior-work account, the instrument provenance, and the contribution framing must all be rebuilt, which is a different study. Rationale: the Journal-Fit Reviewer's evidence rules out the two benign explanations (random transcription error cannot produce suffixes that run strictly sequentially in citation order; de-identification has no reason to alter third-party journal titles while preserving plausible volume/issue/page ranges), which leaves authenticity genuinely open rather than settled in either direction. **This arbitration does not soften F1.** The decision is `reject` because the eligible owner of D2 declared a fatal block; the conditional path above describes what a resubmission would require, not a downgrade of the present decision.

**D-2. Does the §5 hedge cure the onboarding recommendation? (SC-26)**
- R3 and the devil's advocate (M1, confidence 5 each): no. §5 states the reverse pathway is "equally consistent with the data," then two sentences later recommends onboarding designed to raise perceived usefulness — a lever indicated under only one of the two pathways. Under the reverse pathway the indicated lever is assessment placement and course design. The hedge makes the sentence unfalsifiable rather than defensible.
- Journal-Fit Reviewer (S1) and R2 (S3): the paper's claim strength is calibrated throughout; "no sentence in §5 or §7 exceeds what a correlation licenses," and the implication is explicitly marked as unproven.
- **Editor's Resolution: upheld in favour of R3 and the devil's advocate, with the dissenting credit preserved.** The two sides are testing different things and both are partly right. The Journal-Fit Reviewer and R2 are correct that no sentence in §5 asserts causation — that credit stands and is not overturned. But the defect is not in the phrasing; it is that the *content* of the recommendation is derivable only under one horn of a disjunction the authors themselves declared undetermined, and the manuscript never tells the reader that. Expertise tiebreak: translating correlational LMS findings into allocation decisions is R3's owned area at confidence 5, and internal claim–evidence consistency is the devil's advocate's remit. The abstract also advertises "implications for LMS onboarding," so the paper claims this ground rather than having it imputed. Repair: derive the implication under both directions, or withdraw it and amend the abstract.

**D-3. How heavily does the abstract's "engagement" slip weigh? (SC-21)**
- R1: Minor — "arguably stylistic rather than substantive here."
- R3: Major — the abstract is the highest-traffic sentence in the paper, it circulates independently, and the manuscript's own Vasquez citation forbids the equivalence.
- **Editor's Resolution: Major.** R3's argument is evidence-backed and R1 concedes the drift exists while marking its own band with a hedge. The corrected sentence narrows the paper's advertised contribution to what it actually measured, which is a substantive change, not a copy-edit. Also corroborated by the devil's advocate (M5). Routed to Priority 1 as item R12.

**D-4. Deduplication versus anonymity — Major or Minor? (SC-9)**
- R1: Major (analytic-sample definition — the five exclusions cannot be justified without the detection rule).
- R3: Minor (disclosure and governance — readers cannot assess whether their own governance regime would have approved the protocol).
- **Editor's Resolution: Major, as a single merged item.** Both consequences hold, and the band difference reflects each seat's remit rather than a disagreement about the facts; three seats independently identified the same irreconcilability (R1 W3, R3 W5, DA M6). Per the review strategy, R1 owns the procedural framing and R3 the governance framing, and they are merged into one request (item S2) rather than issued as duplicate comments. No reviewer alleged a protocol violation and neither do I; the finding is that the two paragraphs cannot both be read at face value as written.

**D-5. Does Pearson–Spearman convergence license the robustness claim? (SC-17)**
- R1 and the devil's advocate: "indicating that the association did not depend on the parametric assumption" overstates what convergence of two point estimates shows, and ρ = .40 arrives with no interval, *p*, or *n*.
- R2 (S4): the ordinal item is handled as ordinal and the check is "reported without overclaiming what the check establishes."
- **Editor's Resolution: upheld in favour of R1 and the devil's advocate.** Adequacy of inferential reporting is R1's owned dimension; R2's remit is domain accuracy. On substance, Spearman shares the same data and monotonicity, so convergence bears on distributional shape rather than on independence from the parametric assumption generally. Low decision impact — Priority 3, one clause plus reporting ρ's interval (item S14).

**Anticipated conflict that did not materialise.** The review strategy predicted an irreconcilable split between R1 (improve measurement inside the survey paradigm) and R3 (the survey was the wrong instrument where logs were available), and warned the synthesizer not to average them. There is nothing to average: R1's own feasibility paragraph lands on "the honest revision is to state the constraint and drop the comparability claim, not to collect anything," which is R3's request in W3. Both seats converge on disclosure. Recorded as a non-split so that the absence of a conflict is not mistaken for a suppressed one.

### Surface-form parity check (#216)

One down-weighting decision in this synthesis turned on wording: R1's confidence hedge on SC-21 ("arguably stylistic"). Ran the opposite-style counterfactual — if R3's Major-banded argument had arrived in informal phrasing, and R1's Minor band in technical phrasing, would the arbitration flip? No: the arbitration rests on the paper's own text (the abstract drops a qualifier the title, §3.2, §4, and §6 all maintain) and on the §2 commitment the manuscript makes to itself. No sub-claim in this package was re-weighted on the basis of phrasing polish, and none was marked unevaluable for vagueness. Authorship was not a weighting input.

*Epistemic status: this is a prompt-surface check, not a proof that no surface-form prior operated at runtime.*

### Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — this run is `reviewer_full`, so a provenance statement is mandatory and is not omitted. The dispatching layer supplied no provenance stamp with the five reviewer cards. I therefore cannot attest a cross-model slot, and I must not infer one: **no claim of model-family independence across the five seats is made or implied here.** Readers should treat cross-seat agreement in this package as agreement between five prompted reviewer roles of unattested model provenance, not as independent multi-family corroboration. Cross-family splits, had a stamp been supplied, would be visible by inspection in the panel matrix above; no cross-family aggregate was computed, as that is outside this role's permitted operations.

### Cross-model blind decision check (#518)

`ARS_CROSS_MODEL` is not set and no consent gate has been passed. No cross-model check was run; no behavioural change.

### Decision Rationale

The mandatory domain-accuracy dimension carries a fatal block, which under F1 is rejection. The substance behind that score is narrow and severe: every domain claim in the manuscript — the definition of the focal construct, the instrument's provenance and validation, the self-report/log caution, the multi-campus distributional claim that licenses the paper's whole "one point in a distribution" framing, and the consistency verdict — is sourced only to six references that all carry DOIs under the 10.5555 reserved test prefix, numbered 2050001–2050006 in exact citation order, in venues that are near-variants of real journals. Two seats verified this independently at confidence 5. The paper's prior-work account currently cannot be checked at all.

The second, independent block sits on venue fit. One bivariate coefficient, from one site, between two self-reports, one of them a single item, on the field's most replicated association, with no comparator estimate, no moderator, no pooling, no behavioural measure, and no theoretical test. The Journal-Fit Reviewer's judgement is that "it is intended as an incremental data point" is not a contribution statement but a concession that none is being advanced — and the one virtue the manuscript does claim, comparability, is the thing it never demonstrates, since no prior coefficient appears anywhere. Three seats and the devil's advocate agree on that last point.

The three mandatory warns compound rather than compete. The magnitude of *r* = .42 cannot currently be interpreted as a quantity in either direction: a single-item outcome with no reliability estimate bounds the observed correlation from below by an unknown amount, while shared-method covariance between two self-reports collected in one sitting inflates it by an unquantified amount. Neither mechanism is acknowledged. The domain reviewer adds that supplying the missing benchmark may reverse the paper's reading rather than confirm it — .42 against a self-reported access measure plausibly sits at or above log-based pooled estimates, which is a common-method story, not a corroboration story. That would be a more interesting finding than the one the paper reports, and it is available on the existing data.

Reject here means the manuscript cannot proceed in its present form, not that the work is unsalvageable. The roadmap below is ordered so that authenticating the reference base comes first, because whether the remaining fourteen required items describe a substantial revision or a new study depends entirely on its outcome.

### Top Blocking Issues (3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | All six references are unverifiable — reserved 10.5555 test DOI prefix, suffixes sequential in citation order, four near-variant venue titles — so no cited work can be checked and no prior-work claim can be audited. Drives the fatal block on D2. | EIC (W1), R2 (W1) | text: §References, "https://doi.org/10.5555/2050001" … "https://doi.org/10.5555/2050006" | R1 |
| 2 | Contribution falls below the full-article threshold, and the sole claimed virtue — comparability — is never substantiated, since no prior coefficient, range, or pooled estimate appears in the manuscript. Drives the block on D6. | EIC (W2, W3), R1 (W12), R2 (W4), DA (M4) | text: §2, "It is intended as an incremental data point, comparable with prior work, rather than as a test of a theoretical model." · absence: §2 and §5 — expected ≥1 numeric prior correlation or pooled estimate against which r = .42 is compared | R14, R4 |
| 3 | No canonical acceptance-model source, no synthesis or meta-analysis, and nothing post-2021 is engaged in a saturated literature — the omitted sources are precisely the ones that would establish whether the paper adds anything, so item R4's benchmark cannot be built until this is fixed. | R2 (W2) | absence: §2 Literature Review and §References — expected ≥1 foundational acceptance-model source and ≥1 meta-analytic/systematic-review source, plus any work post-2021; checked §1, §2, §5, §7, §References | R2 |

---

## Part 1b: Reviewer Summary Matrix (Step 1a) and Sub-Claim Inventory (Step 1b)

### Step 1a — Reviewer summary matrix

| Dimension | Journal-Fit Reviewer | R1 (Methodology) | R2 (Domain) | R3 (Cross-disciplinary) | DA (Adversarial) |
|---|---|---|---|---|---|
| Overall recommendation | *not emitted under sprint contract* | *not emitted* | *not emitted* | *not emitted* | *not emitted* |
| Report-level confidence | *not emitted (per-finding confidence only)* | *not emitted* | *not emitted* | *not emitted* | *not emitted* |
| Dimensions assessed | D5 `warn`, D6 `block` (repairable) | D1 `warn`, D3 `warn` | D2 `block` (**fatal**) | D4 `warn` | D3 `warn` |
| Key strengths | 4 (S1–S4) | 5 (S1–S5) | 4 (S1–S4) | 3 (S1–S3) | credited inline (arithmetic consistency, CI, causal restraint) |
| Key weaknesses | 5 (W1–W5) → Step 1b | 13 (W1–W13) → Step 1b | 8 (W1–W8) → Step 1b | 6 (W1–W6) → Step 1b | 6 MAJOR (M1–M6), **0 CRITICAL** → Step 1b |
| Minor-band items | 2 | 7 | 2 | 3 | 0 (all MAJOR) |
| Other artifacts | reference-verification determination | 4 arithmetic receipts (AR1 consistent, AR2 consistent, AR3 not_computable, AR4 not_applicable) | independent CI + power verification | governance/consent analysis | — |

No seat emitted a report-level recommendation or confidence score; the contract requires dimension scores, and I have not manufactured either field.

### Step 1b — Weakness sub-claim inventory

**Compaction declared:** the specified shape is one row per `(sub_claim, reviewer)` position, which would produce ~145 rows dominated by `not-mentioned`. I have compacted to one row per sub-claim with a positions column, which is information-equivalent and auditable against the cards. Positions: `R` raised, `C` corroborated, `D` disputed, `–` not-mentioned. Order of seats: **EIC / R1 / R2 / R3 / DA**. Severity and confidence are transported from each raising seat's finding entry, never re-derived.

| SC | Parent weakness(es) | EIC | R1 | R2 | R3 | DA | Count (non-DA) | Disposition | Transported severity | Transported confidence | Evidence anchor |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SC-1 | Reference apparatus unverifiable | R | – | C | – | – | 2 agree / 0 conflict | corroborated finding | Critical (EIC), Critical (R2) | 5, 5 | text: §References, "…10.5555/2050001" … "…10.5555/2050006" |
| SC-22 | Remediability of SC-1 | D | – | R | – | – | 1 agree / 1 conflict | **[SPLIT] → D-1** | Critical (both) | 5, 5 | as SC-1 |
| SC-2 | Contribution below full-article threshold | R | – | – | – | – | 1 / 0 | single-reviewer (D6 owner) | Major | 5 | text: §2, "It is intended as an incremental data point…" |
| SC-3 | No numeric benchmark → consistency claim unfalsifiable | R | C | C | – | C | 3 / 0 | **[CONSENSUS-3]** (silent: R3) | Major, Major, Major | 4, 4, 4 (DA 5) | absence: §2 and §5 — expected ≥1 numeric prior estimate; checked Abstract, §2, §4, §5, §7 |
| SC-19 | Comparison not like-for-like (attenuation; intention vs use; self-report vs log) | – | R | R | – | – | 2 / 0 | corroborated finding | Major, Major | 4, 4 | text: Abstract, "The association was consistent with prior technology-acceptance research"; §5 ¶1 |
| SC-20 | "Use" construct not commensurable with compared studies | – | – | R | – | – | 1 / 0 | single-reviewer (D2 owner) | Major | 5 | text: §3.2, "how often the respondent accessed the LMS in a typical week" |
| SC-23 | No canonical / meta-analytic / post-2021 source | – | – | R | – | – | 1 / 0 | single-reviewer (D2 owner) | Major | 5 | absence: §2 and §References — see Top Blocking rank 3 |
| SC-24 | Canonical PU definition attributed to recent secondary sources; "has long proposed" unsupported | – | – | R | – | – | 1 / 0 | single-reviewer (D2 owner) | Major | 5 | text: §2 ¶1, "the degree to which a person believes a technology will help them perform better" |
| SC-25 | "Technology acceptance" label claimed without naming any model | – | – | R | – | – | 1 / 0 | single-reviewer | Minor | 5 | text: §1 ¶2, "nor do we test a full acceptance model" |
| SC-7 | Single-item ordinal DV, no reliability → magnitude unbounded | – | R | – | – | – | 1 / 0 | single-reviewer (D1 owner) | Major | 5 | text: §3.2, "captured with a single five-point frequency item…" |
| SC-13 | Shared-method covariance never named as rival for the magnitude | – | R | C | – | C | 2 / 0 | corroborated finding | Major, Major | 4, 4 (DA 4) | absence: §3.4 and §5 — expected acknowledgement of one-instrument, one-occasion self-report covariance; checked §2, §3.2, §3.4, §5, §6 |
| SC-8 | No frame size, response rate, or demographics | – | R | – | – | – | 1 / 0 | single-reviewer (D1 owner) | Major | 5 | absence: §3.1 — expected eligible population size, response rate, demographics; checked §3.1, §3.4, §4, §6, Abstract |
| SC-30 | Recruitment plausibly ran through the outcome variable (LMS announcement channel) → selection on the DV | – | – | – | – | R | 0 / 0 non-DA | DA-only finding | Major | 4 | text: §3.1, "All enrolled undergraduates were eligible" + "distributed through the institution's course-announcement channel" |
| SC-9 | Deduplication irreconcilable with anonymity protocol | – | R | – | R | C | 2 / severity conflict | **[SPLIT] → D-4** | Major (R1), Minor (R3) | 4, 4 (DA 4) | text: §3.1 "5 duplicate entries were removed" + §3.3 "No identifying information was collected…" |
| SC-10 | DV five-category distribution never reported → range restriction & symmetry unverifiable | – | R | – | – | C | 1 / 0 | single-reviewer (D1 owner) | Major | 5 | absence: §4 results for the use variable — expected the five-category distribution or a figure; checked §3.4, §4, §5, §6 |
| SC-6 | Item stems not reproduced; adaptation undocumented | R | R | R | R | – | 4 / 0 | **[CONSENSUS-4]** | Minor (EIC), Major (R1), Major (R2), Minor (R3) — band divergence inherited from differing parent scope; remedy identical | 4, 5, 4, 5 | text: §3.2, "a six-item scale adapted from Costa and Wren (2019)" |
| SC-11 | α = .88 without dimensionality evidence | – | R | C | – | – | 2 / 0 | corroborated finding | Major, Major | 5, 4 | text: §3.2, "adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency" |
| SC-12 | "Previously validated instrument" inherits validation across adaptation; reliability ≠ validity | – | C | R | – | C | 2 / 0 | corroborated finding | Major, Major | 5, 4 | text: Abstract, "Perceived usefulness was measured with an adapted, previously validated instrument" |
| SC-21 | Abstract converts self-reported use into "LMS engagement" | – | R | – | R | C | 2 / severity conflict | **[SPLIT] → D-3** | Minor (R1), Major (R3) | 4, 5 (DA 4) | text: Abstract, "perceived usefulness tracks with LMS engagement among undergraduates" |
| SC-26 | Onboarding implication presupposes an undetermined direction; hedge does not cure it | D | – | D | R | C | 1 / 2 conflict | **[SPLIT] → D-2** | Major (R3) | 5 (DA 5) | text: §5, "the reverse pathway… is equally consistent with the data" + "may be worth institutional attention" |
| SC-27 | Reason log data was not used is never stated | – | C `[SEVERITY-SOURCE: letter-fallback]` (unbanded body prose) | – | R | – | 2 / 0 | corroborated finding | Major (R3); unbanded (R1) | 5 (R3) | absence: §3.3 and §6 — expected explicit statement of governance restriction, IRB scope, or non-pursuit; checked Abstract, §1, §3.1–§3.4, §6, §7 |
| SC-28 | Consent architecture forecloses the log-linked follow-up §7 recommends | – | – | – | R | – | 1 / 0 | single-reviewer | Minor | 4 | text: §3.3, "No identifying information was collected, and responses could not be linked back to individual students." |
| SC-29 | Interior anchors of the use item unlabelled → median category uninterpretable | – | C (inside Major parent) | C `[SEVERITY-SOURCE: letter-fallback]` (forwarded, unbanded) | R | – | 3 / 0 | **[CONSENSUS-3]** (silent: EIC) | Minor (R3); band divergence inherited from parent scope | 5 (R3) | text: §3.2, "1 = rarely or never to 5 = several times daily" |
| SC-4 | No tables or figures; the cited scatterplot is never shown | R | C (inside Major parent) | – | – | C | 2 / 0 | corroborated finding | Minor (EIC); inherited band divergence | 4 | text: §3.4, "Scatterplot inspection showed an approximately linear, monotonic association…" |
| SC-5 | Shared variance adjectival, not r² = .18 | R | R | R | – | C | 3 / 0 | **[CONSENSUS-3]** (silent: R3) | Minor, Minor, Minor | 4, 5, 5 | text: §4, "The proportion of variance shared by the two measures was accordingly modest" |
| SC-14 | Power statement is post hoc sensitivity presented as design justification | – | R | – | – | – | 1 / 0 | single-reviewer | Minor | 4 | text: §3.4, "the study had greater than .80 power to detect a correlation of r >= .19" |
| SC-15 | Exclusion rule for 14 incomplete submissions undocumented | – | R | – | – | – | 1 / 0 | single-reviewer | Minor | 4 | absence: §3.1 exclusion accounting — expected the operational rule and removed-vs-retained comparison; checked §3.1, §3.4, §6 |
| SC-16 | ρ = .40 reported without interval, p, or n | – | R | – | – | C | 1 / 0 | single-reviewer | Minor | 5 | text: §4, "The Spearman robustness check yielded a comparable coefficient (ρ = .40)" |
| SC-17 | "did not depend on the parametric assumption" overstates convergence | – | R | D | – | C | 1 / 1 conflict | **[SPLIT] → D-5** | Minor (R1) | 5 | text: §4, "indicating that the association did not depend on the parametric assumption" |
| SC-18 | No data / code / instrument availability statement | – | R | – | – | – | 1 / 0 | single-reviewer | Minor | 5 | absence: back matter after §7 — expected a data, code, or instrument availability statement; checked §3.2, §3.4, §7, §References |

**Band-divergence handling, stated rather than silent.** Four sub-claims (SC-4, SC-6, SC-29, and the R1 side of SC-9) show a Minor/Major divergence. I routed to arbitration only those where the divergence is substantive — a genuine disagreement about weight between parents scoped to the *same* atomic claim (SC-9, SC-21). Where the divergence is inherited from parents of *different* scope and the requested remedy is identical (SC-4, SC-6, SC-29), I recorded it as corroboration with the band inheritance noted and did not manufacture a dispute. All transported bands remain visible above.

---

## Part 2: Revision Roadmap

> **Framing.** The decision is `reject`, so this roadmap defines what a resubmission would have to satisfy rather than a revision timetable for the present submission. Item **R1 is a precondition for the rest**: its outcome determines whether items R2–R14 describe substantial rewriting on the existing data or a different study.

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`. Priority is assigned by a stated rule, not by raw agreement count: **P1** = any item whose unrepaired state makes a claim the paper actually makes unsupportable; **P2** = items that constrain or qualify a claim without making it unsupportable; **P3** = presentation and reporting completeness. Where this promoted a 2/4 or 1/4 finding above the naive count-to-priority mapping (SC-1, SC-2, SC-7, SC-20, SC-23, SC-24), the promotion rests on the confidence-weighting rule and on the finding coming from the eligible owner of the dimension it blocks, at confidence 5. Every promotion is visible in the table.

### Required Revisions (Must Fix)

> **Ordinal contract (#576 §5.1):** the `### Required Item Details` blocks below are numbered `R<n>` in this table's order, contiguous R1..R14.

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| R1 | Produce resolvable bibliographic records for all six cited works, or withdraw and replace them and re-derive every claim currently sourced to them | SC-1, SC-22 | Critical (transported, both seats) | text: §References, "…10.5555/2050001" … "…10.5555/2050006" | 5 — reference resolvability verified independently by two seats | EIC (W1), R2 (W1) | P1 | 1–2 days if records exist; 4–6 weeks if not |
| R2 | Rebuild the literature base: ≥1 foundational acceptance-model source, ≥1 meta-analytic or systematic-review source, and post-2021 work | SC-23 | Major | absence: §2 and §References — expected ≥1 foundational and ≥1 synthesis source plus post-2021 work; checked §1, §2, §5, §7, §References | 5 — R2 synthesizes this literature professionally | R2 (W2) | P1 | 2–3 weeks |
| R3 | Reattribute the perceived-usefulness definition to its actual provenance and repair the "has long proposed" diachronic claim | SC-24 | Major | text: §2 ¶1, "the degree to which a person believes a technology will help them perform better" | 5 | R2 (W3) | P1 | 2–3 days (after R2) |
| R4 | State the benchmark numerically and perform the comparison, or delete every "consistent with prior technology-acceptance research" claim in the Abstract, §5, and §7 | SC-3 | Major (all three seats) | absence: §2 and §5 — expected ≥1 numeric prior estimate; checked Abstract, §2, §4, §5, §7 | 4 (EIC), 4 (R1), 4 (R2); DA 5 | **CONSENSUS-3** — EIC (W3), R1 (W12), R2 (W4); DA (M4) | P1 | 1 week (after R2) |
| R5 | Make the comparison like-for-like: distinguish PU→intention from PU→use and self-reported from log-measured use, and address the attenuation difference of a single-item outcome. Report the result even if it reverses the paper's reading | SC-19 | Major, Major | text: Abstract, "The association was consistent with prior technology-acceptance research"; §5 ¶1 | 4, 4 | R1 (W12), R2 (W4) | P1 | 1 week (after R4) |
| R6 | Narrow the construct claim to weekly access frequency and restrict comparisons to studies using that operationalisation, or measure a richer use construct | SC-20 | Major | text: §3.2, "how often the respondent accessed the LMS in a typical week" | 5 | R2 (W5) | P1 | 3–5 days (narrowing) or new data collection |
| R7 | State an explicit reliability assumption for the single-item outcome and report the attenuation-bounded range for r, or replace it with a multi-item / behavioural measure. Until then, present r = .42 as a sign, not a magnitude | SC-7 | Major | text: §3.2, "captured with a single five-point frequency item…" | 5 — R1's primary research area | R1 (W1) | P1 | 3–5 days (bounding) or new data collection |
| R8 | Name shared-method covariance as a rival explanation for the magnitude and bound it, noting that it runs opposite to attenuation and that neither is currently constrained | SC-13 | Major, Major | absence: §3.4 and §5 — expected acknowledgement of one-instrument, one-occasion covariance; checked §2, §3.2, §3.4, §5, §6 | 4, 4; DA 4 | R1 (W6), R2 (W4); DA (M2) | P1 | 2–3 days |
| R9 | Reproduce all six adapted item stems and document exactly what the adaptation changed from the source instrument | SC-6 | Minor / Major / Major / Minor (transported, four seats) | text: §3.2, "a six-item scale adapted from Costa and Wren (2019)" | 4, 5, 4, 5 | **CONSENSUS-4** — EIC (W5), R1 (W5, W10), R2 (W6), R3 (W6) | P1 | 1 day |
| R10 | Supply dimensionality / factorial evidence and item-total correlations for the six-item scale, or withdraw the α-based measurement warrant | SC-11 | Major, Major | text: §3.2, "…whose original instrument reported strong internal consistency" | 5, 4 | R1 (W5), R2 (W6) | P1 | 3–5 days (re-analysis of existing data) |
| R11 | Withdraw the Abstract's "previously validated instrument" or substantiate the transfer of validation across the adaptation; do not offer α as validity evidence | SC-12 | Major, Major | text: Abstract, "Perceived usefulness was measured with an adapted, previously validated instrument" | 5, 4 | R2 (W6), R1 (W5); DA | P1 | 1 day (after R9, R10) |
| R12 | Correct the Abstract's closing sentence to name the measured construct — self-reported frequency of use, not "LMS engagement" — and align every surface with §2's own commitment | SC-21 | **Arbitrated Major** (D-3); transported Minor (R1), Major (R3) | text: Abstract, "perceived usefulness tracks with LMS engagement among undergraduates" | 4 (R1), 5 (R3); DA 4 | R1 (W13), R3 (W1); DA (M5) | P1 | 1 day |
| R13 | Derive the practical implication under both causal directions, or withdraw it and amend the Abstract's promise of "implications for LMS onboarding". Do not rely on the "suggested by, not proven by" hedge to carry it | SC-26 | **Arbitrated Major** (D-2) | text: §5, "the reverse pathway… is equally consistent with the data" + "may be worth institutional attention" | 5 (R3); DA 5 | R3 (W2); DA (M1). EIC (S1) and R2 (S3) dissent — recorded in D-2 | P1 | 3–5 days |
| R14 | Reframe as a short / brief report, or build an explicit contribution claim that survives the numeric positioning in R4. "An incremental data point" is not a contribution statement | SC-2 | Major | text: §2, "It is intended as an incremental data point, comparable with prior work, rather than as a test of a theoretical model." | 5 — the D6 owner's daily judgement on this stream | EIC (W2) | P1 | 1–2 weeks |

### Required Item Details

**R1**
- **Acceptance criteria**: Each of the six references either resolves to a verifiable published record (DOI, publisher, or archival copy supplied to the editor) or is removed, with every claim previously sourced to it re-derived from a verifiable source or deleted.

**R2**
- **Acceptance criteria**: The reference list contains at least one foundational acceptance-model source, at least one meta-analytic or systematic review of perceived-usefulness–use associations, and at least one source published after 2021, each engaged in §2 rather than cited in passing.

**R3**
- **Acceptance criteria**: The perceived-usefulness definition is attributed to the source that originated it, and no diachronic claim ("has long proposed") remains unsupported by a source of appropriate vintage in the list.

**R4**
- **Acceptance criteria**: At least one numeric prior coefficient, range, or pooled estimate appears in the manuscript alongside a stated comparison rule, or every assertion of consistency with prior research is removed from the Abstract, §5, and §7.

**R5**
- **Acceptance criteria**: The comparison explicitly distinguishes perceived-usefulness→intention from perceived-usefulness→use and self-reported from log-measured outcomes, states the attenuation difference for a single-item outcome, and reports the resulting position of r = .42 even where that position is at or above the pooled estimate.

**R6**
- **Acceptance criteria**: Either the construct is named as weekly access frequency throughout with comparisons restricted to studies using that operationalisation, or a use measure covering depth or duration of engagement is administered.

**R7**
- **Acceptance criteria**: An explicit reliability assumption for the single-item outcome is stated with the disattenuated bound reported, or a multi-item or behavioural use measure replaces it; absent either, magnitude language ("moderately") is replaced by directional language.

**R8**
- **Acceptance criteria**: §5 or §6 names shared-method covariance as a rival explanation for the observed magnitude, states that it runs opposite in sign to attenuation, and states that neither is currently bounded.

**R9**
- **Acceptance criteria**: All six item stems appear in the manuscript or an appendix, together with an itemised statement of what the adaptation changed (wording, item count, scaling) relative to the source instrument.

**R10**
- **Acceptance criteria**: Factor-analytic or item-total evidence for essential unidimensionality of the six-item scale is reported, or the α = .88 figure is retained only as a descriptive statistic with no inferential warrant attached.

**R11**
- **Acceptance criteria**: The word "validated" no longer appears in the Abstract in reference to the adapted instrument, unless item-level equivalence with the validated original is demonstrated in §3.2.

**R12**
- **Acceptance criteria**: The Abstract's closing sentence names self-reported frequency of use, and no surface in the manuscript substitutes "engagement" for the measured construct.

**R13**
- **Acceptance criteria**: §5 either states the indicated lever under each of the two causal directions and flags the recommendation as conditional on an unidentified direction, or contains no onboarding recommendation and the Abstract no longer advertises onboarding implications.

**R14**
- **Acceptance criteria**: The manuscript is submitted to a short-report track at its present scale, or §2 contains a contribution statement that specifies what a reader can do after reading it that they could not do before, consistent with the positioning delivered in R4.

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| S1 | Report the eligible undergraduate population size, the response/completion rate, and respondent demographics beyond year level; bound nonresponse or state that it cannot be bounded | SC-8 | Major | absence: §3.1 — expected population size, response rate, demographics; checked §3.1, §3.4, §4, §6, Abstract | 5 | R1 (W2) | P2 | 1–2 days (institution holds the data) |
| S2 | Reconcile deduplication with the anonymity protocol in **one** merged disclosure: the detection mechanism, its compatibility with §3.3, and the rule distinguishing a duplicate from two identical response vectors | SC-9 | **Arbitrated Major** (D-4); transported Major (R1), Minor (R3) | text: §3.1 "5 duplicate entries were removed" + §3.3 "No identifying information was collected…" | 4 (R1), 4 (R3); DA 4 | R1 (W3) + R3 (W5) merged per review strategy; DA (M6) | P2 | 1 day |
| S3 | Report the outcome item's full five-category frequency distribution and the evidence for the §3.4 symmetry and linearity claims; address ceiling-driven range restriction | SC-10 | Major | absence: §4 — expected the five-category distribution or a supporting figure; checked §3.4, §4, §5, §6 | 5 | R1 (W4) | P2 | 1 day |
| S4 | State why LMS log data was not used — governance restriction, IRB scope, or non-pursuit — and defend the choice if it was non-pursuit | SC-27 | Major (R3); unbanded body prose (R1) `[SEVERITY-SOURCE: letter-fallback]` | absence: §3.3 and §6 — expected an explicit statement; checked Abstract, §1, §3.1–§3.4, §6, §7 | 5 (R3) | R3 (W3), R1 (body, converging) | P2 | 1 day |
| S5 | Disclose whether the course-announcement channel is the LMS itself; if so, address selection on the outcome variable and restate the population claim | SC-30 | Major | text: §3.1, "All enrolled undergraduates were eligible" + "distributed through the institution's course-announcement channel" | 4 | DA (M3) | P2 | 1 day |
| S6 | Relabel the power statement as a post hoc sensitivity analysis, or supply the genuine a priori target with its provenance, software, and method | SC-14 | Minor | text: §3.4, "the study had greater than .80 power to detect a correlation of r >= .19" | 4 | R1 (W7) | P2 | Half a day |
| S7 | Name the acceptance framework the perceived-usefulness construct is drawn from and state which of its paths this study does and does not address | SC-25 | Minor | text: §1 ¶2, "nor do we test a full acceptance model" | 5 | R2 (W7) | P2 | Half a day (after R2) |
| S8 | State the consent and linkage architecture a log-linked follow-up would require, given that §3.3's design forecloses it for this cohort | SC-28 | Minor | text: §3.3, "No identifying information was collected, and responses could not be linked back to individual students." | 4 | R3 (W4) | P2 | Half a day |
| S9 | Print all five anchor labels of the use item so the reported median category can be located on the scale and compared externally | SC-29 | Minor (R3); band inheritance noted (R1, R2) | text: §3.2, "1 = rarely or never to 5 = several times daily" | 5 (R3) | **CONSENSUS-3** — R1, R2, R3 (silent: EIC) | P2 | Half a day |
| S10 | Add a descriptive table for both measures and the scatterplot on which the reported linearity and outlier screening rests | SC-4 | Minor (EIC); band inheritance noted (R1) | text: §3.4, "Scatterplot inspection showed an approximately linear, monotonic association…" | 4 | EIC (W4), R1 (W4) | P3 | Half a day |
| S11 | State r² = .18 numerically instead of characterising shared variance as "modest" | SC-5 | Minor, Minor, Minor | text: §4, "The proportion of variance shared by the two measures was accordingly modest" | 4, 5, 5 | **CONSENSUS-3** — EIC, R1, R2 (silent: R3) | P3 | 10 minutes |
| S12 | State the operational rule defining an incomplete submission and compare removed with retained cases on the observed variables | SC-15 | Minor | absence: §3.1 — expected the operational rule and a removed-vs-retained comparison; checked §3.1, §3.4, §6 | 4 | R1 (W8) | P3 | Half a day |
| S13 | Report the Spearman coefficient with its interval, p, and n | SC-16 | Minor | text: §4, "The Spearman robustness check yielded a comparable coefficient (ρ = .40)" | 5 | R1 (W9) | P3 | 10 minutes |
| S14 | Replace "did not depend on the parametric assumption" with a claim convergence actually licenses | SC-17 | **Arbitrated Minor** (D-5) | text: §4, "indicating that the association did not depend on the parametric assumption" | 5 (R1) | R1 (W9), DA. R2 (S4) dissent — recorded in D-5 | P3 | 10 minutes |
| S15 | Add a data, analysis-code, and instrument availability statement | SC-18 | Minor | absence: back matter after §7 — expected an availability statement; checked §3.2, §3.4, §7, §References | 5 | R1 (W10) | P3 | Half a day |

Transported severity, evidence anchor, and per-finding confidence appear on **every** row above, not only on the Top Blocking rows; fallback tags travel with the values they qualify.

### Revision Checklist

#### Priority 1 — Claim-supporting revisions (estimated total: 6–9 weeks if reference records exist; 3–4 months if they do not)
- [ ] R1: Authenticate or replace all six references (**gates every item below**)
- [ ] R2: Rebuild the literature base (foundational + synthesis + post-2021)
- [ ] R3: Reattribute the perceived-usefulness definition; fix "has long proposed"
- [ ] R4: Supply the numeric benchmark or delete the consistency claim
- [ ] R5: Make the comparison like-for-like; report a reversed reading if that is what emerges
- [ ] R6: Narrow the "use" construct or measure a richer one
- [ ] R7: Bound the single-item outcome's attenuation or replace the measure
- [ ] R8: Name and bound shared-method covariance
- [ ] R9: Reproduce the six item stems; document the adaptation
- [ ] R10: Supply dimensionality evidence or withdraw the α warrant
- [ ] R11: Withdraw or substantiate "previously validated instrument"
- [ ] R12: Correct the Abstract's construct claim
- [ ] R13: Repair or withdraw the onboarding implication
- [ ] R14: Reframe as a short report or build a contribution claim

#### Priority 2 — Constraining and qualifying disclosures (estimated total: 5–7 days)
- [ ] S1: Frame size, response rate, demographics
- [ ] S2: Merged deduplication / anonymity disclosure
- [ ] S3: Outcome distribution and assumption evidence
- [ ] S4: Why log data was not used
- [ ] S5: Recruitment channel identity and its selection consequence
- [ ] S6: Relabel the power statement
- [ ] S7: Name the acceptance framework
- [ ] S8: Consent architecture for the recommended follow-up
- [ ] S9: Print all five anchor labels

#### Priority 3 — Presentation and reporting completeness (estimated total: 2 days)
- [ ] S10: Descriptive table and scatterplot
- [ ] S11: State r² = .18
- [ ] S12: Incompleteness exclusion rule
- [ ] S13: Spearman interval, p, n
- [ ] S14: Correct the robustness-check claim
- [ ] S15: Data, code, and instrument availability statement

### Deadline

Not applicable — this is a rejection, not a revision invitation. If item R1 resolves favourably and the authors work through this roadmap, the work would be welcome as a **new submission**, most plausibly to a short-report track (the field analysis identified *Research in Learning Technology* and *Contemporary Educational Technology* as realistic homes at this scale). Please do not submit a revision under the present manuscript number.

### Response Letter

Should the authors resubmit, please respond to every roadmap item using the `templates/revision_response_template.md` format, item by item, including items the authors decline — with reasons. Items R1, R4, R9, and R12 admit no "respectfully decline" option: R1 because nothing can be assessed without it, R4 and R9 because they carry consensus at CONSENSUS-3 and CONSENSUS-4, and R12 because the Abstract currently states a finding the study did not produce.

---

## Part 2b: Roadmap — Schema 7 machine form

```json
{
  "schema": 7,
  "contract_id": "reviewer/reviewer_full/v2",
  "editorial_decision": "reject",
  "items": [
    {"id": "R1", "priority": "must_fix", "verification_criteria": "Each of the six references resolves to a verifiable published record supplied to the editor, or is removed with every dependent claim re-derived or deleted.", "reviewer": "eic,domain", "severity": "critical", "evidence_anchor": "text: §References, \"https://doi.org/10.5555/2050001\" … \"https://doi.org/10.5555/2050006\"", "confidence": 5, "sub_claims": ["SC-1", "SC-22"]},
    {"id": "R2", "priority": "must_fix", "verification_criteria": "Reference list contains >=1 foundational acceptance-model source, >=1 meta-analytic/systematic review, and >=1 post-2021 source, each engaged in §2.", "reviewer": "domain", "severity": "major", "evidence_anchor": "absence: §2 Literature Review and §References — expected >=1 foundational acceptance-model source and >=1 synthesis source plus post-2021 work; checked §1, §2, §5, §7, §References", "confidence": 5, "sub_claims": ["SC-23"]},
    {"id": "R3", "priority": "must_fix", "verification_criteria": "Perceived-usefulness definition attributed to its originating source; no unsupported diachronic claim remains.", "reviewer": "domain", "severity": "major", "evidence_anchor": "text: §2 ¶1, \"the degree to which a person believes a technology will help them perform better\"", "confidence": 5, "sub_claims": ["SC-24"]},
    {"id": "R4", "priority": "must_fix", "verification_criteria": ">=1 numeric prior coefficient/range/pooled estimate appears with a stated comparison rule, or all consistency claims are deleted from Abstract, §5, §7.", "reviewer": "eic,methodology,domain", "severity": "major", "evidence_anchor": "absence: §2 and §5 — expected at least one numeric prior correlation or pooled estimate against which r = .42 is compared; checked Abstract, §2, §4, §5, §7", "confidence": 4, "consensus": "CONSENSUS-3", "sub_claims": ["SC-3"]},
    {"id": "R5", "priority": "must_fix", "verification_criteria": "Comparison distinguishes PU->intention from PU->use and self-report from log-measured use, states the single-item attenuation difference, and reports the resulting position of r = .42 even if adverse.", "reviewer": "methodology,domain", "severity": "major", "evidence_anchor": "text: Abstract \"The association was consistent with prior technology-acceptance research\"; §5 ¶1", "confidence": 4, "sub_claims": ["SC-19"]},
    {"id": "R6", "priority": "must_fix", "verification_criteria": "Construct named as weekly access frequency with comparisons restricted accordingly, or a depth/duration use measure administered.", "reviewer": "domain", "severity": "major", "evidence_anchor": "text: §3.2, \"how often the respondent accessed the LMS in a typical week\"", "confidence": 5, "sub_claims": ["SC-20"]},
    {"id": "R7", "priority": "must_fix", "verification_criteria": "Explicit reliability assumption for the single-item outcome with disattenuated bound reported, or a multi-item/behavioural measure substituted; otherwise magnitude language replaced by directional language.", "reviewer": "methodology", "severity": "major", "evidence_anchor": "text: §3.2, \"captured with a single five-point frequency item asking how often the respondent accessed the LMS\"", "confidence": 5, "sub_claims": ["SC-7"]},
    {"id": "R8", "priority": "must_fix", "verification_criteria": "§5 or §6 names shared-method covariance as a rival for the magnitude, notes its opposite sign to attenuation, and states neither is bounded.", "reviewer": "methodology,domain,da", "severity": "major", "evidence_anchor": "absence: §3.4 and §5 treatment of measurement threats — expected acknowledgement that predictor and outcome come from one self-report instrument administered at one time; checked §2, §3.2, §3.4, §5, §6", "confidence": 4, "sub_claims": ["SC-13"]},
    {"id": "R9", "priority": "must_fix", "verification_criteria": "All six item stems present in manuscript or appendix, with an itemised statement of what the adaptation changed.", "reviewer": "eic,methodology,domain,perspective", "severity": "major", "evidence_anchor": "text: §3.2, \"measured using a six-item scale adapted from Costa and Wren (2019)\"", "confidence": 5, "consensus": "CONSENSUS-4", "sub_claims": ["SC-6"]},
    {"id": "R10", "priority": "must_fix", "verification_criteria": "Factor-analytic or item-total evidence for essential unidimensionality reported, or alpha retained as descriptive only with no inferential warrant.", "reviewer": "methodology,domain", "severity": "major", "evidence_anchor": "text: §3.2, \"adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency\"", "confidence": 5, "sub_claims": ["SC-11"]},
    {"id": "R11", "priority": "must_fix", "verification_criteria": "\"Validated\" removed from the Abstract's description of the adapted instrument unless item-level equivalence with the original is demonstrated in §3.2.", "reviewer": "domain,methodology", "severity": "major", "evidence_anchor": "text: Abstract, \"Perceived usefulness was measured with an adapted, previously validated instrument\"", "confidence": 4, "sub_claims": ["SC-12"]},
    {"id": "R12", "priority": "must_fix", "verification_criteria": "Abstract's closing sentence names self-reported frequency of use; no surface substitutes \"engagement\" for the measured construct.", "reviewer": "methodology,perspective,da", "severity": "major", "evidence_anchor": "text: Abstract, \"perceived usefulness tracks with LMS engagement among undergraduates\"", "confidence": 5, "arbitration": "D-3", "sub_claims": ["SC-21"]},
    {"id": "R13", "priority": "must_fix", "verification_criteria": "§5 states the indicated lever under both causal directions and flags the recommendation as conditional, or contains no onboarding recommendation and the Abstract drops onboarding implications.", "reviewer": "perspective,da", "severity": "major", "evidence_anchor": "text: §5, \"the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data\" and \"may be worth institutional attention\"", "confidence": 5, "arbitration": "D-2", "sub_claims": ["SC-26"]},
    {"id": "R14", "priority": "must_fix", "verification_criteria": "Submitted to a short-report track at present scale, or §2 contains a contribution statement specifying what a reader can do afterwards that they could not before, consistent with R4.", "reviewer": "eic", "severity": "major", "evidence_anchor": "text: §2, \"It is intended as an incremental data point, comparable with prior work, rather than as a test of a theoretical model.\"", "confidence": 5, "sub_claims": ["SC-2"]},

    {"id": "S1", "priority": "should_fix", "verification_criteria": "Eligible population size, response/completion rate, and demographics beyond year level reported; nonresponse bounded or explicitly declared unboundable.", "reviewer": "methodology", "severity": "major", "evidence_anchor": "absence: §3.1 participants reporting — expected the eligible undergraduate population size, a response or completion rate, and respondent demographics beyond year level; checked §3.1, §3.4, §4, §6, and the abstract", "confidence": 5, "sub_claims": ["SC-8"]},
    {"id": "S2", "priority": "should_fix", "verification_criteria": "One merged disclosure stating the duplicate-detection mechanism, its compatibility with §3.3, and the rule separating duplicates from identical response vectors.", "reviewer": "methodology,perspective,da", "severity": "major", "evidence_anchor": "text: §3.1, §3.3 \"5 duplicate entries were removed\", \"No identifying information was collected\"", "confidence": 4, "arbitration": "D-4", "sub_claims": ["SC-9"]},
    {"id": "S3", "priority": "should_fix", "verification_criteria": "Full five-category outcome distribution reported plus evidence for the §3.4 symmetry and linearity claims; range restriction addressed.", "reviewer": "methodology", "severity": "major", "evidence_anchor": "absence: §4 results for the single-item use variable — expected the full five-category frequency distribution or a figure evidencing the stated linearity and symmetry; checked §3.4, §4, §5, and §6", "confidence": 5, "sub_claims": ["SC-10"]},
    {"id": "S4", "priority": "should_fix", "verification_criteria": "Manuscript states whether log data was governance-restricted, outside IRB scope, or not pursued, and defends the choice if the last.", "reviewer": "perspective,methodology", "severity": "major", "evidence_anchor": "absence: Methods §3.3 and Limitations §6 — expected an explicit statement of whether LMS log data was governance-restricted, outside IRB scope, or simply not pursued; checked Abstract, §1, §3.1, §3.2, §3.3, §3.4, §6, §7", "confidence": 5, "severity_source": "letter-fallback-for-methodology-position", "sub_claims": ["SC-27"]},
    {"id": "S5", "priority": "should_fix", "verification_criteria": "Recruitment channel identity disclosed; if the LMS, selection on the outcome variable is addressed and the population claim restated.", "reviewer": "da", "severity": "major", "evidence_anchor": "text: §3.1 \"All enrolled undergraduates were eligible\" and \"The survey was distributed through the institution's course-announcement channel\"", "confidence": 4, "sub_claims": ["SC-30"]},
    {"id": "S6", "priority": "should_fix", "verification_criteria": "Power statement relabelled as post hoc sensitivity, or a priori target supplied with provenance, software, and method.", "reviewer": "methodology", "severity": "minor", "evidence_anchor": "text: §3.4 \"the study had greater than .80 power to detect a correlation of r >= .19\"", "confidence": 4, "sub_claims": ["SC-14"]},
    {"id": "S7", "priority": "should_fix", "verification_criteria": "Acceptance framework named, with the paths this study addresses and omits stated explicitly.", "reviewer": "domain", "severity": "minor", "evidence_anchor": "text: §1 ¶2 \"nor do we test a full acceptance model\"", "confidence": 5, "sub_claims": ["SC-25"]},
    {"id": "S8", "priority": "should_fix", "verification_criteria": "§7 states the consent and linkage architecture a log-linked follow-up requires.", "reviewer": "perspective", "severity": "minor", "evidence_anchor": "text: §3.3 \"No identifying information was collected, and responses could not be linked back to individual students.\"", "confidence": 4, "sub_claims": ["SC-28"]},
    {"id": "S9", "priority": "should_fix", "verification_criteria": "All five anchor labels of the use item printed in §3.2.", "reviewer": "methodology,domain,perspective", "severity": "minor", "evidence_anchor": "text: §3.2 \"1 = rarely or never to 5 = several times daily\"", "confidence": 5, "consensus": "CONSENSUS-3", "sub_claims": ["SC-29"]},
    {"id": "S10", "priority": "nice_to_fix", "verification_criteria": "A descriptive table for both measures and the scatterplot underlying the linearity/outlier screening appear in the manuscript.", "reviewer": "eic,methodology", "severity": "minor", "evidence_anchor": "text: §3.4 \"Scatterplot inspection showed an approximately linear, monotonic association with no extreme bivariate outliers\"", "confidence": 4, "sub_claims": ["SC-4"]},
    {"id": "S11", "priority": "nice_to_fix", "verification_criteria": "r-squared = .18 stated numerically in §4 in place of the adjectival characterisation.", "reviewer": "eic,methodology,domain", "severity": "minor", "evidence_anchor": "text: §4 \"The proportion of variance shared by the two measures was accordingly modest\"", "confidence": 5, "consensus": "CONSENSUS-3", "sub_claims": ["SC-5"]},
    {"id": "S12", "priority": "nice_to_fix", "verification_criteria": "Operational rule for incomplete submissions stated, with a removed-vs-retained comparison on observed variables.", "reviewer": "methodology", "severity": "minor", "evidence_anchor": "absence: §3.1 exclusion accounting — expected the operational rule defining an incomplete submission and any comparison of removed with retained cases; checked §3.1, §3.4, and §6", "confidence": 4, "sub_claims": ["SC-15"]},
    {"id": "S13", "priority": "nice_to_fix", "verification_criteria": "Spearman coefficient reported with interval, p, and n.", "reviewer": "methodology", "severity": "minor", "evidence_anchor": "text: §4 \"The Spearman robustness check yielded a comparable coefficient (rho = .40)\"", "confidence": 5, "sub_claims": ["SC-16"]},
    {"id": "S14", "priority": "nice_to_fix", "verification_criteria": "The robustness sentence claims only what Pearson-Spearman convergence licenses.", "reviewer": "methodology,da", "severity": "minor", "evidence_anchor": "text: §4 \"indicating that the association did not depend on the parametric assumption\"", "confidence": 5, "arbitration": "D-5", "sub_claims": ["SC-17"]},
    {"id": "S15", "priority": "nice_to_fix", "verification_criteria": "A data, analysis-code, and instrument availability statement appears in the back matter.", "reviewer": "methodology", "severity": "minor", "evidence_anchor": "absence: manuscript back matter following §7 — expected a data, analysis-code, or instrument availability statement and the six adapted item stems; checked §3.2, §3.4, §7, and the references", "confidence": 5, "sub_claims": ["SC-18"]}
  ]
}
```

---

## Part 3: Reviewer Report Summary (Appendix)

No seat emitted a report-level recommendation or confidence score under this contract; dimension scores and per-finding confidence are reported instead, and neither field has been synthesized.

### Journal-Fit Reviewer (role: `eic`)
- Assessed: D5 `warn` (no exhibits; adapted instrument not reproduced), D6 `block` / `repairable` (contribution below full-article threshold).
- Key point: the manuscript's restraint is a genuine editorial credit, but somewhere between §2 and §7 modesty stops qualifying a contribution claim and starts substituting for one — and the entire reference apparatus is unverifiable, which is acceptance-blocking independent of everything else.

### Peer Reviewer 1 — Methodology (role: `methodology`)
- Assessed: D1 `warn`, D3 `warn`. 13 findings (6 Major, 7 Minor); 4 arithmetic receipts (2 consistent, 1 `not_computable`, 1 `not_applicable`).
- Key point: the inferential register is better than the measurement layer — a coefficient reported to two decimals with a CI sits on a single-item outcome whose unreliability attenuates it by an unknown amount while shared-method covariance inflates it by another, so the magnitude has no defensible interval of interpretation even though its sign is secure.

### Peer Reviewer 2 — Domain (role: `domain`)
- Assessed: D2 `block` / **`fatal`**. 8 findings (1 Critical, 5 Major, 2 Minor).
- Key point: modest is fine, unverifiable is not — every domain claim rests on six references bearing the reserved 10.5555 test prefix, and when the missing benchmark is supplied from the omitted literature the comparison turns adverse rather than neutral.

### Peer Reviewer 3 — Cross-disciplinary (role: `perspective`)
- Assessed: D4 `warn`. 6 findings (3 Major, 3 Minor).
- Key point: an adjacent-field reader can restate the finding correctly from §1–§7 but not from the Abstract, and the paper's sole actionable recommendation survives under only one of two causal directions the authors declare equally consistent.

### Devil's Advocate (role: `da`)
- Assessed: D3 `warn`. **0 CRITICAL**, 6 MAJOR.
- Key point: came to break the spine and could not — the arithmetic holds and the central correlational claim survives; the load-bearing weakness is that the paper names the objections it has answers to and passes over the one it does not, namely common-method variance bearing on the magnitude itself.

---

*Editorial decision determined mechanically per the v3.6.2 Sprint Contract Synthesizer Protocol: `editorial_decision=reject` (F1, severity 95). No fired condition's action was softened; no substitute scores were synthesized; no aggregation rule outside `cross_reviewer_quantifier` + `severity` was applied; no new review comment was authored by this role.*
