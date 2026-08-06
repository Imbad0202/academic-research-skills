# Editorial Decision Package

**Contract**: `reviewer/reviewer_full/v2` · mode `reviewer_full` · stage `reviewer_full_review` · baseline `v3.20.0`
**Panel**: 5/5 cards received and usable (eic, methodology, domain, perspective, da). No `[PANEL-SHRUNK]`.

## Mechanical Audit (v3.6.2 Sprint Contract Protocol)

**Step 1 — Role-scoped scoring matrix**

| Dim | Priority | Eligible roles | Assessed eligible seats | Verdict | Fatal? |
|-----|----------|----------------|-------------------------|---------|--------|
| D1 methodology_rigor | mandatory | methodology | methodology = block (`block_class: repairable`) | **block** | no |
| D2 domain_accuracy | mandatory | domain | domain = block (`block_class: repairable`) | **block** | no |
| D3 argumentative_coherence | mandatory | da, methodology | da = warn; methodology = warn | **warn** | n/a |
| D4 cross_disciplinary_relevance | high | perspective | perspective = warn | **warn** | n/a |
| D5 writing_and_structure | normal | eic | eic = warn | **warn** | n/a |
| D6 venue_fit_and_contribution | mandatory | eic | eic = block (`block_class: repairable`) | **block** | no |

All `not_assessed` values from ineligible seats were excluded from both numerator and denominator. Every dimension has its owner seat assessed — no `[DIMENSION-UNASSESSED]`. No seat declared a fatal block; the eic card explicitly declines fatal classification on D6, and both eic and domain frame the reference-integrity concern as a verification requirement rather than an established fabrication finding. Fatality is therefore not minted here.

`audit_verdict: block` (worst assessed eligible score; no fatal declarations)

**Step 2 — Failure condition evaluation**

| ID | Sev | Cross-reviewer quantifier | Expression | Per-dimension evaluation | Fired |
|----|-----|---------------------------|------------|--------------------------|-------|
| F1 | 95 | any | any mandatory dimension has a fatal block | D1/D2/D3/D6: no seat declared fatal | **false** |
| F2 | 90 | any | any mandatory dimension scores 'block' | D1 true (methodology block), D2 true, D6 true | **true** |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1 true (n=1, owner), D2 true (n=1, owner), D3 true (n=2, both seats warn), D6 true (n=1, owner) → 4 ≥ 2 | **true** |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4 = warn, not block | **false** |
| F5 | 40 | any | any dimension scores 'warn' or worse | D1 block | **true** |
| F0 | 10 | all | every dimension scores 'pass' | three blocks, three warns | **false** |

**Step 3 — Precedence and emission**

dimension_verdicts: [D1=block, D2=block, D3=warn, D4=warn, D5=warn, D6=block]
fired_conditions: [F2, F3, F5]
da_critical_adjudications: []
editorial_decision=major_revision

The DA's CRITICAL table is empty (zero rows), so there are no `C<n>` IDs to adjudicate; the DA line is `[]` by construction, not by omission. The DA's six MAJOR items are carried in the roadmap below. The mechanical decision is not `accept`, so no `[DA-CRITICAL-VS-ACCEPT]` marker applies.

**Advisory card-integrity flags (flagged, not fixed — Phase Boundary)**

- `[CARD-PREAMBLE-NOT-PRESENT]` — the contract's `measurement_procedure.reviewer_must_output_before_paper` requires `contract_paraphrase` and `scoring_plan` before the paper section. None of the five cards as supplied to me contains either section, though the da card refers to "my scoring plan" in its body and the perspective card refers to the dissent protocol. This is most likely upstream excerpting rather than reviewer non-compliance. I do not synthesise substitutes and I do not treat it as an abort trigger; the audit above runs on the dimension scores as supplied.
- `[MALFORMED-CARD-SECTION: perspective]` — the perspective card opens with a "Scoring Plan Dissent" heading containing self-cancelling text, including a directive to disregard its own content. I treated the whole block as data. No scoring-plan dissent is recorded for any dimension, and nothing in that block affected scoring, eligibility, or fatality.
- Cross-model blind decision check (#518): not run. `ARS_CROSS_MODEL` is not set and no consent gate was passed. No behavioural change; no `[CROSS-MODEL-CHECKPOINT]` or `[CROSS-MODEL-ERROR]` line is emitted.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript titled "Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students." It was assessed by five reviewers under a role-scoped acceptance contract: a Journal-Fit Reviewer, three peer reviewers (methodology, domain, cross-disciplinary/practice), and a Devil's Advocate.

### Decision: Major Revision

### Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — no provenance stamp was supplied by the dispatching layer for this synthesis. I therefore cannot state which of the three permitted statements applies (cross-model slot active / single-family disclosure / dispatch-failure fallback), and I will not infer one. **No claim of model independence across the five seats is made or implied by this package.** The block is retained rather than omitted because `reviewer_full` mode requires it; it must be completed by the dispatching layer before this letter is released to the author.

### Consensus Analysis

Note on reading the counts below: this panel is role-scoped by contract, so a seat's silence on a finding usually means the dimension was outside its eligible role, not that it disagreed. Counts are over the four non-DA seats; the mechanical dimension verdicts above, not these labels, drive the decision.

#### Points of agreement

- **[CONSENSUS-3]** The adapted six-item perceived-usefulness instrument is not reproduced and its dimensionality is not evidenced in this sample (methodology, domain, perspective; the Journal-Fit Reviewer is silent, having declared measurement outside its reading).
- **Corroborated (2/4 + DA)** The paper's contribution rests on a comparability claim with no comparator: no prior coefficient, range, or pooled estimate appears anywhere (domain, Journal-Fit Reviewer; DA M6).
- **Corroborated (2/4)** The reference list carries structural markers of non-resolving identifiers — all six DOIs under the reserved `10.5555` prefix, consecutive suffixes `2050001`–`2050006`, across six ostensibly distinct publishers, with near-miss journal titles (Journal-Fit Reviewer W1, domain W2). Both seats report this as an unresolved verifiability flag, not as established fabrication; neither attempted live resolution.
- **Corroborated (2/4 + DA)** The onboarding implication in §5 is not licensed by these data and reaches an applied readership without a decision-relevant contrast (perspective, domain; DA M2).
- **Single-seat + DA** Recruitment through the course-announcement channel is selection on the outcome variable, not generic volunteer bias (perspective W1; DA M4).
- **Single-seat + DA** §3.1's duplicate removal and §3.3's anonymity claim cannot both stand as written (methodology W4; DA M5).
- **Unanimous on register** All five seats credit the manuscript's calibration: the causal disclaimer is explicit and repeated, the reverse pathway is named and attributed, the self-report measure is framed as perceived rather than behavioural use, and the interval, n, and rank-based robustness check are reported together. This is a genuine asset and revision should not sand it off. It is also not a contribution, and the decision does not rest on it.

#### Points of disagreement

- **Sensitivity/power boundary.** DA verified "greater than .80 power to detect r ≥ .19" as accurate; methodology W6 computes, by the standard Fisher-z approximation, that the correlation attaining exactly .80 power at n = 214 is .1905, so achieved power at r = .19 is ≈ .798 — marginally below the stated threshold. **Editor's resolution:** both seats agree the detectable effect is ≈ .19; the dispute concerns the third decimal and, as methodology itself states at Confidence 3, depends on which routine the authors used. The disagreement does not change any decision. The required fix is the one both readings support: label the statement a priori or post hoc, name the software, and either restate .19 as approximately .80 power or move the threshold to .20.
- **Escalation class of the integrity flag.** Domain states that non-resolution would make its D2 block non-repairable; the Journal-Fit Reviewer deliberately declines to bind the flag to a fatal classification, on the ground that its declared D6 fatality criterion concerns scope and duplication, not source verification. **Editor's resolution:** no conflict on substance — both hold that verification runs logically prior to the ordinary decision path. The decision above is computed on the scores as declared, with no fatality minted. Verification is recorded as a conditional escalation gate, not as a current fatal finding.
- **Predicted tension that did not materialise.** The field analysis anticipated the domain seat demanding a structural or mediation model against methodology's objection that a single-item ordinal outcome at n = 214 cannot support one. The domain seat explicitly declined to make that demand. No arbitration is needed, and no roadmap item asks the authors to fit an acceptance model.

### Decision Rationale

The decision follows the contract arithmetic, not an impression of the paper. Three of the four mandatory dimensions score `block`: methodology_rigor, because the sole predictor instrument is invisible and unevidenced for dimensionality while the sole outcome is a single ordinal item whose unreliability leaves attenuation unbounded; domain_accuracy, because the comparability claim carrying the paper's contribution is stated without a comparator and the foundational lineage is uncited; and venue_fit_and_contribution, because the contribution is asserted rather than substantiated as an advance. F2 fires at severity 90 and selects Major Revision. F3 and F5 also fire and select the same action, so the outcome does not depend on precedence.

Every one of these blocks was classified repairable by the seat that raised it, and the arithmetic bears that out. The reported statistics are internally consistent: the case-disposition chain 233 − 14 − 5 = 214 reconciles at four locations, the 95% CI [.30, .52] is exactly the Fisher-z interval on r = .42 at n = 214, and GRIM and GRIMMER on M = 3.6 (SD = 0.8) are satisfied. Nothing in the reported arithmetic is impossible. What is missing is disclosure the authors already hold plus re-estimation appropriate to a single ordinal outcome, and bibliographic positioning that requires no new data.

Two things this decision is not. It is not a judgement on the manuscript's honesty, which four seats praised specifically and which should survive revision intact. And it is not a rejection routed through revision: the estimate itself survives the required work, which is why the reclassification path below is a route to publication rather than a demotion.

One matter stands outside the accept/revise calculus. The reference-list identifier pattern must be verified by the editorial office before this manuscript proceeds. If the six sources do not resolve, no revision to Sections 2 through 7 is relevant and the decision must be recomputed.

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | Reference identifiers carry structural markers of non-resolving sources; if unverified, the entire literature base, the comparability claim, and the instrument's provenance are unsupported | EIC (W1, Critical), Domain (W2, Critical) | text: §References "https://doi.org/10.5555/2050001", "https://doi.org/10.5555/2050006" | R1 |
| 2 | The predictor instrument is neither reproduced nor shown unidimensional, and a single ordinal item carries the outcome, so r = .42 has no defensible construct-level reading (D1 block) | Methodology (W1 Critical, W2 Major), Domain (W5), Perspective (W5) | text: §3.2 "measured using a six-item scale adapted from Costa and Wren (2019)" | R2, R3 |
| 3 | The comparability claim on which the contribution rests has no comparator anywhere in the manuscript (D2 and D6 block) | Domain (W1 Critical), EIC (W2 Major), DA (M6) | text: §2 "It is intended as an incremental data point, comparable with prior work, rather than as a test of a theoretical model." | R4, R5 |

---

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column reads `—` throughout: this synthesis ran in v3.6.2 sprint-contract arithmetic mode, where the Step 1b sub-claim inventory does not apply. Merged items name every contributing finding instead, so traceability is preserved through the `Source` column.
>
> Severity, evidence anchors, and confidence are **transported** from the reviewer cards, never re-derived. Where seats raised related findings at different bands, the item carries the highest transported severity with its owning seat named and the corroborating bands listed.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|--------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| R1 | Verify or replace all six references so every cited source resolves | — | Critical (EIC W1); corroborated Critical (domain W2) | text: §References "https://doi.org/10.5555/2050001", "https://doi.org/10.5555/2050006" | 4 (EIC); 4 (domain) | EIC, Domain | P1 | 2–3 d author + editorial office check |
| R2 | Reproduce the adapted six-item instrument verbatim, document what the adaptation changed, add in-sample dimensionality evidence (CFA or at minimum EFA with loadings), report α with a CI, and add data/materials availability statements | — | Critical (methodology W1); corroborated Major (domain W5), Minor (perspective W5) | text: §3.2 "measured using a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency" | 5 (methodology); 5 (domain); 4 (perspective) | R1 Methodology, R2 Domain, R3 Perspective | P1 | 3–4 d |
| R3 | Re-estimate for a single ordinal outcome: polyserial or polychoric estimate as primary or co-primary, a percentile bootstrap interval alongside the normal-theory one, and an explicit attenuation paragraph stating what the coefficient can and cannot be read as | — | Major (methodology W2) | text: §3.2 "captured with a single five-point frequency item asking how often the respondent accessed the LMS in a typical week" | 5 | R1 Methodology | P1 | 3–4 d |
| R4 | Report actual prior effect sizes, including the pooled estimates from the existing meta-analytic literature on this association, state the range, and locate r = .42 [.30, .52] within it | — | Critical (domain W1); corroborated Major (EIC W2), Major (DA M6) | text: §2 and §5 "It is intended as an incremental data point, comparable with prior work" and "consistent with prior technology-acceptance research" | 5 (domain); 5 (EIC); 4 (DA) | R2 Domain, EIC, DA | P1 | 4–5 d |
| R5 | Cite the foundational acceptance lineage (Davis; the UTAUT line) and attribute the perceived-usefulness definition to its origin rather than to two recent secondary sources | — | Major (domain W3) | text: §2 "perceived usefulness — the degree to which a person believes a technology will help them perform better" | 5 | R2 Domain | P1 | 1 d |
| R6 | Report the eligible-population denominator, the invitation count, and response and completion rates | — | Major (methodology W3) | absence: §3.1 sampling account — expected the eligible-population denominator with response and completion rates; checked §3.1, §3.3, §4, §6, Abstract | 5 | R1 Methodology | P1 | 1 d |
| R7 | Disclose the duplicate-detection signal and rule, state whether it is non-identifying, confirm ethics coverage, and correct §3.1/§3.3 so the two are mutually consistent | — | Major (methodology W4); corroborated Major (DA M5) | text: §3.1 and §3.3 "5 duplicate entries were removed" and "No identifying information was collected, and responses could not be linked back to individual students" | 4 (methodology); 4 (DA) | R1 Methodology, DA | P1 | 1 d |
| R8 | Add a participant characterisation table (year-level distribution, discipline mix, gender, age) with comparison to institutional population figures | — | Major (methodology W5) | text: §3.1 "The analyzed sample of 214 students spanned all four year levels." | 5 | R1 Methodology | P1 | 1–2 d |
| R9 | Treat recruitment through the LMS course-announcement channel as selection on the outcome variable in Methods and Limitations, discuss range restriction and its consequence for the coefficient, report the use-item distribution, and where feasible compare respondents' aggregate log activity against the enrolled population | — | Major (perspective W1); corroborated Major (DA M4) | text: §3.1, §6 "The survey was distributed through the institution's course-announcement channel over a three-week window." and "students who engage more with institutional channels may be overrepresented" | 5 (perspective); 4 (DA) | R3 Perspective, DA | P1 | 2–3 d (+3–5 d if the log comparison is included) |
| R10 | Rescope the abstract: restate the terminal claim as an association with self-reported frequency of use among undergraduates at one mid-sized university, matching §7, and remove the transfer of the source instrument's validation to the adapted form | — | Major (DA M1); corroborated Major (methodology W11) | text: Abstract "The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates." and Abstract "Perceived usefulness was measured with an adapted, previously validated instrument" | 5 (DA); 5 (methodology) | DA, R1 Methodology | P1 | 0.5 d |
| R11 | Add an explicit common-method-variance limitation — both variables are concurrent self-reports from the same instrument — and soften interpretive language about what the coefficient indexes | — | Major (DA M3) | absence: interpretation of the reported r = .42 — expected explicit treatment of common-method variance shared by two concurrent self-report measures; checked §2, §3.2, §3.4, §4, §5, §6 | 4 | DA | P1 | 1 d |
| R12 | Reframe the onboarding implication as a hypothesis for intervention or log-based research, remove it from the abstract's list of contributions, state what Whitfield (2019) actually measured, and engage the existing intervention and quasi-experimental evidence on whether raising perceived usefulness changes use | — | Major (perspective W2); corroborated Major (DA M2), Minor (domain W6) | text: Abstract, §5 "We discuss implications for LMS onboarding" and "onboarding which helps students see concrete usefulness"; text: §5 "a possibility also raised in practitioner accounts of digital-environment onboarding" | 4 (perspective); 4 (DA); 4 (domain) | R3 Perspective, DA, R2 Domain | P1 | 1–2 d |
| R13 | Defend access frequency as the construct being explained, or reframe: address the distinction between frequency and depth/quality of engagement in the framing and limitations, and state that log data would measure the same construct more accurately rather than resolving the construct question | — | Major (domain W4) | absence: Sections 3.2, 5, and 6 — expected a defense of access frequency as an engagement construct distinct from depth of use; checked Measures, Results, Discussion, Limitations | 4 | R2 Domain | P1 | 2 d |
| R14 | Consider structural and access explanations for low LMS use in Discussion and Limitations (device availability, connectivity, off-campus study, employment or caregiving load, disability and accessibility, platform usability), rather than framing non-use solely as a perception deficit | — | Major (perspective W3) | absence: §5 Discussion and §6 Limitations — expected consideration of structural or access barriers to LMS use; checked Abstract, §1, §2, §4, §5, §6, §7 | 5 | R3 Perspective | P1 | 2–3 d |
| R15 | Resolve the article class: either reclassify as a Short Paper / Research Note proportionate to a single bivariate result, or substantiate the full-article weight | — | Major (EIC W3) | absence: §4 Results — expected reported analyses beyond the single bivariate coefficient commensurate with full research-article format; checked §3.4, §4, §5, §7 | 5 | EIC | P1 | 3–5 d |

### Required Item Details

**R1 — Reference verification**
- **Sources**: EIC W1 (Critical, Confidence 4); Domain W2 (Critical, Confidence 4)
- **Note**: Neither seat attempted live resolution; both report structural evidence and require verification. This item runs logically prior to R2–R15. If the sources do not resolve, the domain seat's D2 block ceases to be repairable and this decision must be recomputed.
- **Acceptance criteria**: All six DOIs resolve to the cited works with matching titles, venues, years, and page ranges, or the affected references are replaced with resolvable sources and every claim in §2 that depended on them is re-grounded; the editorial office records the resolution result before revision review proceeds.

**R2 — Instrument disclosure and dimensionality**
- **Sources**: Methodology W1 (Critical, 5); Domain W5 (Major, 5); Perspective W5 (Minor, 4); Methodology W8 (Minor, 4, availability element)
- **Acceptance criteria**: The six adapted items appear verbatim in an appendix or inline, the adaptation is documented (wording changes, referent substitution, items dropped or added, response-format changes), a CFA or EFA in this sample is reported with its factor solution and loadings, α is reported with a confidence interval, and data-, materials-, and code-availability statements are present.

**R3 — Ordinal-appropriate estimation and attenuation**
- **Sources**: Methodology W2 (Major, 5); related Methodology W10 (Minor, 5)
- **Acceptance criteria**: A polyserial or polychoric estimate is reported as primary or co-primary, a percentile bootstrap interval accompanies the Fisher-z interval, and a paragraph states explicitly that the observed coefficient is attenuated by unknown amounts and that the magnitude descriptor applies to the measures rather than to the constructs.

**R4 — Comparability benchmark**
- **Sources**: Domain W1 (Critical, 5); EIC W2 (Major, 5); DA M6 (Major, 4)
- **Acceptance criteria**: Specific coefficients or ranges from the cited studies and from the pooled meta-analytic literature on the perceived-usefulness/use association appear in §2, r = .42 [.30, .52] is located explicitly within that range, and the paper states whether its interval overlaps the pooled estimate.

**R5 — Foundational lineage and construct provenance**
- **Sources**: Domain W3 (Major, 5)
- **Acceptance criteria**: Davis and the UTAUT line are cited, the perceived-usefulness definition is attributed to its origin, and §2 gives enough theoretical scaffolding for a reader to judge what "a test of a theoretical model" would have involved.

**R6 — Sampling denominator and response rate**
- **Sources**: Methodology W3 (Major, 5)
- **Acceptance criteria**: §3.1 reports the enrolled-undergraduate figure, the number invited, the response rate, and the completion rate, and Limitation 4 is restated so its magnitude is bounded rather than only its direction.

**R7 — Deduplication and anonymity reconciliation**
- **Sources**: Methodology W4 (Major, 4); DA M5 (Major, 4)
- **Acceptance criteria**: The duplicate-detection signal and rule are stated, their non-identifying status is asserted or the anonymity claim in §3.3 is corrected, ethics coverage of the mechanism is confirmed, and §3.1 and §3.3 are mutually consistent as written.

**R8 — Sample characterisation**
- **Sources**: Methodology W5 (Major, 5)
- **Acceptance criteria**: A participant table reports year-level distribution, discipline mix, and available demographics, alongside the corresponding institutional population figures, so a reader can judge to whom the estimate applies.

**R9 — Recruitment channel as a threat to the estimate**
- **Sources**: Perspective W1 (Major, 5); DA M4 (Major, 4)
- **Acceptance criteria**: Methods and Limitations state that the recruitment channel is the platform under study, the discussion treats the resulting selection on the outcome and range restriction as a threat to the coefficient rather than only to generalisability, the full five-level use-item distribution is reported, and either the respondent/enrolled log-activity comparison is reported or its unavailability is explained under R-S8.

**R10 — Abstract rescoping**
- **Sources**: DA M1 (Major, 5); Methodology W11 (Major, 5)
- **Acceptance criteria**: The abstract's terminal sentence names self-reported frequency of use and retains the single-institution qualifier, matching §7, and no sentence in the abstract transfers the source instrument's validation to the adapted form.

**R11 — Common-method variance**
- **Sources**: DA M3 (Major, 4)
- **Acceptance criteria**: An explicit limitation states that both variables are concurrent self-reports from the same instrument and that consistency motives, halo, and response style are rival accounts of part of the covariance, with interpretive language in §4 and §5 adjusted accordingly.

**R12 — Practice implication**
- **Sources**: Perspective W2 (Major, 4); DA M2 (Major, 4); Domain W6 (Minor, 4)
- **Acceptance criteria**: The onboarding claim appears as a hypothesis for intervention or log-based research rather than as an implication of these data, it is removed from the abstract's contributions, what Whitfield (2019) measured is stated, and the existing intervention or quasi-experimental evidence on raising perceived usefulness is engaged.

**R13 — Outcome construct defence**
- **Sources**: Domain W4 (Major, 4)
- **Acceptance criteria**: The manuscript either defends access frequency as the engagement construct of interest or reframes it, distinguishes frequency from depth or quality of use in framing and limitations, and states that log data would measure the same construct more accurately rather than resolving the construct question.

**R14 — Structural and access explanations**
- **Sources**: Perspective W3 (Major, 5)
- **Acceptance criteria**: Discussion and Limitations consider structural and access explanations for low LMS use, and the proposed remedy is no longer framed as though non-use were solely a perception deficit.

**R15 — Article class**
- **Sources**: EIC W3 (Major, 5)
- **Acceptance criteria**: The manuscript is resubmitted either as a Short Paper / Research Note whose structure is proportionate to one bivariate result plus the R4 comparison, or as a full article whose reported analyses justify the seven-section architecture; the editorial office confirms the chosen class before revision review.

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|--------------|--------------|----------|-----------------|------------|--------|----------|-----------------|
| S1 | Add at least one table of descriptives and the scatterplot §3.4 says was inspected | — | Minor (EIC W4); corroborated Minor (methodology W7) | absence: whole manuscript — expected at least one table or figure presenting the descriptives and the inspected scatterplot; checked abstract, §3, §4, §5 | 5 (EIC); 5 (methodology) | EIC, R1 Methodology | P3 | 0.5 d |
| S2 | Print the quantities that exist: report r² = .18 rather than "accordingly modest", and drop the redundant "conventional significance threshold" where alpha is already stated | — | Minor (EIC W5); corroborated Minor (methodology W7) | text: §4 "The proportion of variance shared by the two measures was accordingly modest" | 4 (EIC); 5 (methodology) | EIC, R1 Methodology | P3 | 0.25 d |
| S3 | Report the full frequency distribution across all five levels of the use item and the year-level distribution | — | Minor (methodology W7) | text: §4 "Self-reported LMS use had a median category of 'a few times per week.'" | 5 | R1 Methodology | P2 | 0.5 d |
| S4 | Label the sensitivity statement a priori or post hoc, name the software and version, and either restate r ≥ .19 as approximately .80 power or move the threshold to .20 | — | Minor (methodology W6) | text: §3.4 "the study had greater than .80 power to detect a correlation of r >= .19 at alpha = .05 (two-tailed)" | 3 | R1 Methodology | P2 | 0.25 d |
| S5 | Describe the missingness behind the 14 excluded submissions, compare completers with non-completers, and state item-level missingness among the retained 214 | — | Minor (methodology W9) | absence: §3.1 exclusion reporting — expected the missingness pattern behind 14 removed submissions and a completer/non-completer comparison; checked §3.1, §3.2, §3.4, §4 | 4 | R1 Methodology | P2 | 0.5 d |
| S6 | Reword the Spearman claim so it does not extend to the coverage of the normal-theory interval | — | Minor (methodology W10) | text: §4 "indicating that the association did not depend on the parametric assumption" | 5 | R1 Methodology | P3 | 0.25 d |
| S7 | Name the analysis software and version in §3.4 | — | Minor (methodology W8) | absence: §3.4 and end matter — expected data, code, and adapted-instrument availability statements plus named analysis software; checked §3.3, §3.4, §4, References | 4 | R1 Methodology | P2 | 0.25 d |
| S8 | State why LMS log data was not obtained here — governance, IRB scope, anonymity commitment, technical access, or analyst capacity — instead of deferring it to future work without explanation | — | Minor (perspective W4) | text: §6, §7 "LMS use was self-reported through a single item rather than measured through system logs" and "Future research using behavioral log data" | 4 | R3 Perspective | P2 | 0.25 d |
| S9 | State the contribution affirmatively — a transparently reported, design-bounded, replication-grade estimate offered against a named prior range — rather than describing only what the finding is not | — | Minor (EIC W6) | text: §7 "is offered as an incremental, design-bounded contribution rather than a causal claim" | 4 | EIC | P2 | 0.5 d |
| S10 | Reconcile the reported median category "a few times per week" with the response anchors disclosed in §3.2, so the median maps onto the scale | — | Minor `[SEVERITY-SOURCE: letter-fallback]` — DA body prose, below the card's severity-banded finding threshold | text: §4 "Self-reported LMS use had a median category of 'a few times per week.'" | `[CONFIDENCE-SOURCE: report-level]` — no per-finding confidence attached in the card | DA (editorial channel) | P3 | 0.25 d |

### Revision Checklist

#### Priority 1 — Structural Revisions (estimated total effort: 27–37 working days)
- [ ] R1: Verify or replace all six references so every cited source resolves *(editorial-office gate — runs first)*
- [ ] R2: Reproduce the adapted instrument, document the adaptation, add dimensionality evidence and α CI, add availability statements
- [ ] R3: Re-estimate for an ordinal outcome (polyserial/polychoric), add a bootstrap interval, add the attenuation discussion
- [ ] R4: Report prior effect sizes and pooled estimates; locate r = .42 within the stated range
- [ ] R5: Cite Davis and the UTAUT line; attribute the construct definition correctly
- [ ] R6: Report the eligible-N denominator, invitation count, response and completion rates
- [ ] R7: Disclose the deduplication signal; reconcile it with the anonymity claim
- [ ] R8: Add a participant table with institutional population comparison
- [ ] R9: Treat the recruitment channel as selection on the outcome; report the use-item distribution
- [ ] R10: Rescope the abstract's terminal claim and remove the validity transfer
- [ ] R11: Add the common-method-variance limitation
- [ ] R12: Reframe the onboarding implication as a hypothesis; engage the intervention evidence
- [ ] R13: Defend or reframe access frequency as the outcome construct
- [ ] R14: Address structural and access explanations for low use
- [ ] R15: Resolve the article class (Short Paper / Research Note or substantiated full article)

#### Priority 2 — Content Supplementation (estimated total effort: 2.5–3 working days)
- [ ] S3: Full five-level frequency distribution and year-level distribution
- [ ] S4: Label the sensitivity statement; name software; fix the .19/.20 threshold
- [ ] S5: Missingness account and completer/non-completer comparison
- [ ] S7: Name analysis software and version
- [ ] S8: State why log data was unavailable
- [ ] S9: Claim the contribution affirmatively

#### Priority 3 — Text and Formatting (estimated total effort: 1.5 working days)
- [ ] S1: Descriptives table and scatterplot
- [ ] S2: Print r² = .18; drop the redundant threshold phrase
- [ ] S6: Reword the Spearman robustness claim
- [ ] S10: Reconcile the reported median category with the disclosed anchors

### Editorial routing of the P1 set (two paths, same roadmap)

The panel's requirements are internally satisfiable, but they distribute across two very different amounts of work. This is a routing of existing items, not a new requirement.

- **Path A — reframe within existing data.** R1–R8, R10–R15 plus all Suggested items, with R9's log comparison optional and R15 resolved as Short Paper / Research Note. No new data collection. This satisfies every fired condition's remedy and is the recommended route.
- **Path B — extend the study.** Path A plus behavioural log data or a second institution, which changes what R9 and R13 can deliver and would justify a full-article class under R15. Cost is a new data-collection cycle and governance approval. The panel did not require this, and the methodology seat's constraints mean the current dataset cannot support model testing regardless of how Path B is resourced.

### Revision Deadline

Major Revision: 6–8 weeks recommended. R1 should be resolved by the editorial office before the revision clock starts, since its outcome determines whether R2–R15 are worth performing.

### Response Letter Template

Please use `templates/revision_response_template.md` and respond to every item R1–R15 and S1–S10 individually, quoting the revised text and its location. Items R1–R15 are Required: for a Major Revision arising from three blocked mandatory dimensions, "respectfully decline" is available only for items where you can demonstrate the finding rests on a misreading of the manuscript, and that demonstration must be explicit.

---

## Part 3: Reviewer Report Summary (Appendix)

Cards report dimension scores rather than overall recommendations, so no accept/revise/reject recommendation is attributed to any seat here.

### Journal-Fit Reviewer (contract_role: eic)
- Assessed: D5 = warn, D6 = block (repairable). Declared blind spots: statistics, measurement properties, sample composition.
- Key point: the manuscript's restraint is its best feature and is not a contribution; the comparability claim that carries the contribution is asserted rather than demonstrated, and the reference identifiers oblige an editorial integrity check before anything else.

### Peer Reviewer 1 — Methodology (contract_role: methodology)
- Assessed: D1 = block (repairable), D3 = warn. Four arithmetic receipts: p-from-test-statistic consistent, GRIM consistent, GRIMMER consistent, n-from-df not applicable.
- Key point: the arithmetic reconciles and the interval is exactly reproducible, but the predictor instrument is invisible and unevidenced for dimensionality while a single ordinal item carries the outcome, so r = .42 has no defensible construct-level reading.

### Peer Reviewer 2 — Domain (contract_role: domain)
- Assessed: D2 = block (repairable, conditional on reference resolution).
- Key point: the paper's interpretive domain judgement is unusually good, but it asserts comparability three times without a single prior estimate, omits the canonical lineage, and rests on six identifiers the reviewer could not resolve.

### Peer Reviewer 3 — Cross-disciplinary / practice (contract_role: perspective)
- Assessed: D4 = warn. Card carried a malformed leading section, flagged above; no dissent recorded.
- Key point: the content transfers to adjacent-field readers, but the paper never states that the recruitment channel is the platform under study, offers no decision threshold for its practice recommendation, and frames non-use exclusively as a perception deficit.

### Devil's Advocate (contract_role: da)
- Assessed: D3 = warn. CRITICAL findings: zero. MAJOR findings: six (M1–M6).
- Key point: the body's language does not exceed the data, but the abstract's terminal sentence restores the behavioural construct the paper explicitly disclaimed, and the consistency-with-prior-work claim is unfalsifiable as written.

---

## Roadmap — Schema 7 machine form

```json
{
  "schema": 7,
  "contract_id": "reviewer/reviewer_full/v2",
  "editorial_decision": "major_revision",
  "fired_conditions": ["F2", "F3", "F5"],
  "dimension_verdicts": {"D1": "block", "D2": "block", "D3": "warn", "D4": "warn", "D5": "warn", "D6": "block"},
  "da_critical_adjudications": [],
  "items": [
    {"id": "R1", "priority": "must_fix", "reviewer": ["eic", "domain"], "severity": "critical", "evidence_anchor": "text: §References \"https://doi.org/10.5555/2050001\", \"https://doi.org/10.5555/2050006\"", "confidence": 4, "verification_criteria": "All six DOIs resolve to the cited works with matching titles, venues, years and pages, or affected references are replaced with resolvable sources and dependent §2 claims re-grounded; editorial office records the result before revision review."},
    {"id": "R2", "priority": "must_fix", "reviewer": ["methodology", "domain", "perspective"], "severity": "critical", "evidence_anchor": "text: §3.2 \"measured using a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency\"", "confidence": 5, "verification_criteria": "Six adapted items verbatim, documented adaptation, CFA or EFA with loadings in this sample, alpha with confidence interval, and data/materials/code availability statements."},
    {"id": "R3", "priority": "must_fix", "reviewer": ["methodology"], "severity": "major", "evidence_anchor": "text: §3.2 \"captured with a single five-point frequency item asking how often the respondent accessed the LMS in a typical week\"", "confidence": 5, "verification_criteria": "Polyserial or polychoric estimate reported as primary or co-primary, percentile bootstrap interval alongside the Fisher-z interval, and an explicit attenuation paragraph restricting the magnitude descriptor to the measures."},
    {"id": "R4", "priority": "must_fix", "reviewer": ["domain", "eic", "da"], "severity": "critical", "evidence_anchor": "text: §2 and §5 \"It is intended as an incremental data point, comparable with prior work\" and \"consistent with prior technology-acceptance research\"", "confidence": 5, "verification_criteria": "Specific prior coefficients and pooled estimates appear in §2, r = .42 [.30, .52] is located within the stated range, and interval overlap with the pooled estimate is stated."},
    {"id": "R5", "priority": "must_fix", "reviewer": ["domain"], "severity": "major", "evidence_anchor": "text: §2 \"perceived usefulness — the degree to which a person believes a technology will help them perform better\"", "confidence": 5, "verification_criteria": "Davis and the UTAUT line cited, construct definition attributed to origin, and theoretical scaffolding sufficient to judge what a model test would involve."},
    {"id": "R6", "priority": "must_fix", "reviewer": ["methodology"], "severity": "major", "evidence_anchor": "absence: §3.1 sampling account — expected the eligible-population denominator with response and completion rates; checked §3.1, §3.3, §4, §6, Abstract", "confidence": 5, "verification_criteria": "Enrolment figure, invitation count, response rate and completion rate reported, with Limitation 4 restated so its magnitude is bounded."},
    {"id": "R7", "priority": "must_fix", "reviewer": ["methodology", "da"], "severity": "major", "evidence_anchor": "text: §3.1 and §3.3 \"5 duplicate entries were removed\" and \"No identifying information was collected, and responses could not be linked back to individual students\"", "confidence": 4, "verification_criteria": "Deduplication signal and rule stated, non-identifying status asserted or §3.3 corrected, ethics coverage confirmed, and the two sections mutually consistent."},
    {"id": "R8", "priority": "must_fix", "reviewer": ["methodology"], "severity": "major", "evidence_anchor": "text: §3.1 \"The analyzed sample of 214 students spanned all four year levels.\"", "confidence": 5, "verification_criteria": "Participant table reports year level, discipline, and available demographics alongside institutional population figures."},
    {"id": "R9", "priority": "must_fix", "reviewer": ["perspective", "da"], "severity": "major", "evidence_anchor": "text: §3.1, §6 \"The survey was distributed through the institution's course-announcement channel over a three-week window.\" and \"students who engage more with institutional channels may be overrepresented\"", "confidence": 5, "verification_criteria": "Methods and Limitations identify the channel as the platform under study, range restriction and selection on the outcome are discussed as threats to the coefficient, the use-item distribution is reported, and the log-activity comparison is either reported or its unavailability explained."},
    {"id": "R10", "priority": "must_fix", "reviewer": ["da", "methodology"], "severity": "major", "evidence_anchor": "text: Abstract \"The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates.\"", "confidence": 5, "verification_criteria": "Abstract terminal sentence names self-reported frequency of use with the single-institution qualifier, matching §7, and no abstract sentence transfers the source instrument's validation to the adapted form."},
    {"id": "R11", "priority": "must_fix", "reviewer": ["da"], "severity": "major", "evidence_anchor": "absence: interpretation of the reported r = .42 — expected explicit treatment of common-method variance shared by two concurrent self-report measures; checked §2, §3.2, §3.4, §4, §5, §6", "confidence": 4, "verification_criteria": "An explicit common-method-variance limitation names consistency motives, halo and response style as rival accounts, with §4 and §5 language adjusted."},
    {"id": "R12", "priority": "must_fix", "reviewer": ["perspective", "da", "domain"], "severity": "major", "evidence_anchor": "text: Abstract, §5 \"We discuss implications for LMS onboarding\" and \"onboarding which helps students see concrete usefulness\"", "confidence": 4, "verification_criteria": "Onboarding claim appears as a hypothesis for intervention or log-based research, is removed from the abstract's contributions, Whitfield (2019)'s measured outcome is stated, and the intervention literature is engaged."},
    {"id": "R13", "priority": "must_fix", "reviewer": ["domain"], "severity": "major", "evidence_anchor": "absence: Sections 3.2, 5, and 6 — expected a defense of access frequency as an engagement construct distinct from depth of use; checked Measures, Results, Discussion, Limitations", "confidence": 4, "verification_criteria": "Access frequency is defended or reframed, frequency is distinguished from depth of use in framing and limitations, and log data is stated to measure the same construct more accurately rather than resolving it."},
    {"id": "R14", "priority": "must_fix", "reviewer": ["perspective"], "severity": "major", "evidence_anchor": "absence: §5 Discussion and §6 Limitations — expected consideration of structural or access barriers to LMS use; checked Abstract, §1, §2, §4, §5, §6, §7", "confidence": 5, "verification_criteria": "Discussion and Limitations consider structural and access explanations for low use, and the recommendation is no longer framed as though non-use were solely a perception deficit."},
    {"id": "R15", "priority": "must_fix", "reviewer": ["eic"], "severity": "major", "evidence_anchor": "absence: §4 Results — expected reported analyses beyond the single bivariate coefficient commensurate with full research-article format; checked §3.4, §4, §5, §7", "confidence": 5, "verification_criteria": "Manuscript is resubmitted as a Short Paper / Research Note proportionate to one bivariate result plus the R4 comparison, or as a full article whose reported analyses justify the seven-section architecture; class confirmed by the editorial office."},
    {"id": "S1", "priority": "nice_to_fix", "reviewer": ["eic", "methodology"], "severity": "minor", "evidence_anchor": "absence: whole manuscript — expected at least one table or figure presenting the descriptives and the inspected scatterplot; checked abstract, §3, §4, §5", "confidence": 5, "verification_criteria": "At least one descriptives table and the inspected scatterplot appear as exhibits."},
    {"id": "S2", "priority": "nice_to_fix", "reviewer": ["eic", "methodology"], "severity": "minor", "evidence_anchor": "text: §4 \"The proportion of variance shared by the two measures was accordingly modest\"", "confidence": 4, "verification_criteria": "r-squared is printed as .18 and the redundant significance-threshold phrase in §3.4 is removed."},
    {"id": "S3", "priority": "should_fix", "reviewer": ["methodology"], "severity": "minor", "evidence_anchor": "text: §4 \"Self-reported LMS use had a median category of 'a few times per week.'\"", "confidence": 5, "verification_criteria": "Full frequency distribution across all five use-item levels and the year-level distribution are reported."},
    {"id": "S4", "priority": "should_fix", "reviewer": ["methodology"], "severity": "minor", "evidence_anchor": "text: §3.4 \"the study had greater than .80 power to detect a correlation of r >= .19 at alpha = .05 (two-tailed)\"", "confidence": 3, "verification_criteria": "Sensitivity statement labelled a priori or post hoc, software and version named, and r >= .19 restated as approximately .80 power or the threshold moved to .20."},
    {"id": "S5", "priority": "should_fix", "reviewer": ["methodology"], "severity": "minor", "evidence_anchor": "absence: §3.1 exclusion reporting — expected the missingness pattern behind 14 removed submissions and a completer/non-completer comparison; checked §3.1, §3.2, §3.4, §4", "confidence": 4, "verification_criteria": "Missingness pattern behind the 14 exclusions, a completer/non-completer comparison, and item-level missingness among the retained 214 are reported."},
    {"id": "S6", "priority": "nice_to_fix", "reviewer": ["methodology"], "severity": "minor", "evidence_anchor": "text: §4 \"indicating that the association did not depend on the parametric assumption\"", "confidence": 5, "verification_criteria": "The Spearman claim is reworded so it does not extend to the coverage of the normal-theory interval."},
    {"id": "S7", "priority": "should_fix", "reviewer": ["methodology"], "severity": "minor", "evidence_anchor": "absence: §3.4 and end matter — expected data, code, and adapted-instrument availability statements plus named analysis software; checked §3.3, §3.4, §4, References", "confidence": 4, "verification_criteria": "Analysis software and version are named in §3.4."},
    {"id": "S8", "priority": "should_fix", "reviewer": ["perspective"], "severity": "minor", "evidence_anchor": "text: §6, §7 \"LMS use was self-reported through a single item rather than measured through system logs\" and \"Future research using behavioral log data\"", "confidence": 4, "verification_criteria": "The specific constraint that prevented log-data use — governance, IRB scope, anonymity commitment, technical access, or capacity — is named."},
    {"id": "S9", "priority": "should_fix", "reviewer": ["eic"], "severity": "minor", "evidence_anchor": "text: §7 \"is offered as an incremental, design-bounded contribution rather than a causal claim\"", "confidence": 4, "verification_criteria": "The contribution is stated affirmatively as a transparently reported, design-bounded, replication-grade estimate positioned against the named prior range from R4."},
    {"id": "S10", "priority": "nice_to_fix", "reviewer": ["da"], "source_kind": "editorial", "severity": "minor", "severity_source": "letter-fallback", "evidence_anchor": "text: §4 \"Self-reported LMS use had a median category of 'a few times per week.'\"", "confidence_source": "report-level", "verification_criteria": "The reported median category maps onto the response anchors disclosed in §3.2."}
  ]
}
```

---

**Deliverable complete.** This is the Phase 2 editorial synthesis only. The revision itself is a separate `academic-paper` Phase 6 re-invocation of `draft_writer_agent`; I have not written and will not write revised manuscript content. Two items require action outside the author's control before the revision clock starts: R1's reference resolution by the editorial office, and completion of the `Review Panel Provenance (#540)` block by the dispatching layer.
