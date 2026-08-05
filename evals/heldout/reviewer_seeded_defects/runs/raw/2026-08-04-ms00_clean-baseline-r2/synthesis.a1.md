# Editorial Decision Package

## Contract Audit (v3.6.2 sprint contract — `reviewer/reviewer_full/v2`)

**Step 1 — role-scoped scoring matrix** (only assessed scores from seats whose `contract_role` appears in the dimension's `eligible_roles`)

| Dim | Priority | Eligible roles | Assessed eligible seats | Dimension score |
|-----|----------|----------------|-------------------------|-----------------|
| D1 methodology_rigor | mandatory | methodology | methodology = warn | warn |
| D2 domain_accuracy | mandatory | domain | domain = block (`block_class: repairable`) | block |
| D3 argumentative_coherence | mandatory | da, methodology | da = warn; methodology = warn | warn |
| D4 cross_disciplinary_relevance | high | perspective | perspective = warn | warn |
| D5 writing_and_structure | normal | eic | eic = warn | warn |
| D6 venue_fit_and_contribution | mandatory | eic | eic = block (`block_class: repairable`) | block |

All `not_assessed` entries were from ineligible seats and are excluded from both numerator and denominator. No eligible seat abstained. No dimension is unassessed. No seat declared a fatal block — both block-scoring seats explicitly typed their block as repairable, and the EIC card states on the record that it did not stretch its fatal condition to cover an integrity finding.

`audit_verdict: block` (non-fatal)

**Step 2 — failure-condition evaluation**

| ID | Sev | Quantifier | Expression | Per-dimension result | Fired |
|----|-----|-----------|------------|----------------------|-------|
| F1 | 95 | any | any mandatory dimension has a fatal block | D1 no, D2 no, D3 no, D6 no | false |
| F2 | 90 | any | any mandatory dimension scores 'block' | D2 yes, D6 yes | **true** |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1 yes (n=1, owner), D2 yes, D3 yes (n=2, both seats), D6 yes → 4 ≥ 2 | **true** |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4 = warn, not block | false |
| F5 | 40 | any | any dimension scores 'warn' or worse | all six yes | **true** |
| F0 | 10 | all | every dimension scores 'pass' | no | false |

**Step 3 — precedence and emission**

```
dimension_verdicts: [D1=warn, D2=block, D3=warn, D4=warn, D5=warn, D6=block]
fired_conditions: [F2, F3, F5]
da_critical_adjudications: []
editorial_decision=major_revision
```

The Devil's Advocate card's CRITICAL table contains headers and no rows, so there are no DA CRITICAL IDs to adjudicate; the DA's six MAJOR-band findings and four in-body findings are carried through the consensus analysis and roadmap below. `[DA-CRITICAL-VS-ACCEPT]` does not apply (mechanical decision is not `accept`, and no CRITICAL IDs exist).

**Card-completeness flags** (raised, not fixed — Phase 1 is not mine to rewrite): the contract's `measurement_procedure` requires each reviewer to emit `contract_paraphrase` and `scoring_plan` before reading the paper; those Phase 1 artefacts were not supplied to me, so I cannot verify that precondition. The DA card places four of its ten findings in body prose with inline anchors rather than in its severity tables; they are legible and were inventoried, but the card deviates from the tabular format.

---

## Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — this run is `mode: reviewer_full`, so this block is mandatory, but the dispatching layer supplied no provenance stamp. I will not infer which model family ran which seat. **Readers must not infer model independence across the five seats from the absence of a statement here.** The stamp must be supplied and this block filled before the decision letter is treated as complete.

---

# Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript, *Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students*. It was assessed by five reviewers: a Journal-Fit Reviewer, three peer reviewers (methodology, domain, cross-disciplinary), and an adversarial reviewer.

### Decision: Major Revision

### Consensus Analysis

Consensus is computed per sub-claim across the four non-DA seats (Journal-Fit/EIC, R1 Methodology, R2 Domain, R3 Perspective); silence is recorded as silence and is never promoted to agreement. The DA is tracked separately. Thirty-three card-level weaknesses decomposed into 35 sub-claims.

**No sub-claim reached [CONSENSUS-4].** Stating this plainly matters, because the surface impression of this panel is convergence: everyone found something wrong with the same three or four passages. The convergence is real but it is not unanimity, and the roadmap is priced accordingly.

#### Points of agreement

- **[CONSENSUS-3]** (silent: Journal-Fit Reviewer) — The manuscript substitutes "LMS engagement" for what it measured. §2 commits to treating the item as "an indicator of perceived use rather than a behavioral count"; the Abstract's closing sentence then reports that perceived usefulness "tracks with LMS engagement among undergraduates," and the substitution recurs in §4 and §5. R1, R2 and R3 each raised this independently at Major severity and confidence 5, from three different professional angles (internal contradiction, construct precision, adjacent-field readability). The DA corroborates and adds that the same sentence escalates the population from one university to undergraduates as such. → **R4**
- **[CONSENSUS-3]** (silent: R2 Domain) — The six adapted perceived-usefulness items are not reproduced anywhere, so the operational content of the paper's predictor is invisible and the measure cannot be replicated. → **R9**
- **Corroborated (2/4, no conflict)** — The evidence base cannot be verified: all six DOIs sit on the CrossRef `10.5555` reserved test prefix in the consecutive block 2050001–2050006, and none of the six outlet titles is recognisable. The Journal-Fit Reviewer (confidence 5, reference-verification checklist) and R2 (confidence 4, familiarity with the technology-acceptance record) both report verification failure; both explicitly decline to allege fabrication. R1 and R3 scoped it out of their remits. → **R1**
- **Corroborated (2/4, no conflict)** — The paper's only stated contribution is positional ("an incremental data point, comparable with prior work"), and the distribution it claims membership in is never specified. R2 raised it at confidence 5; the Journal-Fit Reviewer's D6 block rests on the same relation being unestablishable; the DA adds that under the paper's own premise that effect sizes vary, no observed coefficient could have been reported as inconsistent. → **R2**
- **Corroborated (2/4, no conflict)** — No eligible-population denominator and therefore no response rate exists anywhere in the manuscript, which leaves the voluntary-response bias the authors correctly concede unsizeable. → **R5**
- **Corroborated (2/4, no conflict)** — Common method variance is neither remedied nor named: both constructs came from one respondent, one instrument, one occasion, with no marker and no procedural separation. → **R6**
- **Corroborated (2/4, no conflict)** — Shared variance is characterised as "modest" while every other statistic is reported exactly; r² ≈ .18 should be stated. → **S3**
- **Corroborated (2/4, no conflict)** — The scatterplot the analysis relies on is not shown and no descriptive exhibit of either measure appears. → **S11**

#### Points of disagreement

**D-1 [SPLIT] — Is the practical implication adequately handled?** (3 agree / 1 disputed; sub-claims SC-27, SC-28)
R2 lists the onboarding recommendation as a *strength*: it is "presented as a possibility and expressly flagged as not established by the correlation... the standard failure point in applied LMS papers and the authors avoided it." R1 (Minor, confidence 4) holds that the double hedge "softens the register but does not repair the logic," because two sentences earlier the Discussion granted the reverse pathway equal standing. R3 (Minor, confidence 5) and the Journal-Fit Reviewer (Minor, confidence 4) hold that the passage is unactionable at the resolution an institution costs interventions at, and that its supporting practitioner source (Whitfield, 2019) enters only in the Discussion and is never appraised.
**Editor's resolution:** R2 is right and keeps the credit — this is not an overclaim, and the panel should not be read as saying it is. R1 is right that hedging does not license a directional recommendation drawn from an avowedly bidirectional correlation; R3 and the Journal-Fit Reviewer are right that what remains is not specifiable. These are compatible, not competing, once separated: the passage is simultaneously well-hedged, a non-sequitur, and non-specific. The author must either state the additional premise the recommendation requires *and* specify facet, segment and timing, or recast it as a research question — and must appraise or remove the late-entering source. Rationale: the three positions address different properties of the same sentence, and R2's dissent turns out to concern only the property the other three did not contest.

**D-2 [SPLIT] — Is the power statement prospective or post hoc?** (1 agree / 1 disputed; sub-claim SC-21)
R1 (Minor, confidence 4) reads "With n = 214, the study had greater than .80 power to detect r ≥ .19... so the design was sensitive to small-to-moderate associations" as a sensitivity analysis computed *from* a realised availability sample, and asks for it to be relabelled. R3 credits it in S3 and in its body as "a prospective power statement rather than a post-hoc one."
**Editor's resolution:** R1 prevails. Both evidence and expertise point the same way — the sentence conditions on `n = 214`, no sample-size target is claimed anywhere in the manuscript, and the a-priori/sensitivity distinction sits inside the methodology seat's remit and outside the analytics seat's. R3's substantive credit stands: the statement is useful and legible to an adjacent-field reader, which is what R3 was assessing. Only its label is wrong. → **S2**

**D-3 Cross-panel dispute — Which way does measurement artefact bound r = .42?** (sub-claim SC-12b; R2 vs DA, the DA sitting outside the four-seat count)
R2 (Major, confidence 4) argues that with two perceptions measured together, .42 is "more defensibly read as an upper bound on the perceived-usefulness–actual-use relationship." The DA (confidence 4) argues the opposite for the Discussion's ceiling claim: an ordinal single-item outcome of unreported reliability attenuates the estimate, so ".42 is better read as a floor than a ceiling," and "at best one of several factors" asserts a bound the design does not deliver. R1 names both forces — attenuation downward from single-item error, inflation upward from shared method — and asks only that the direction be stated.
**Editor's resolution: unresolved dissent, recorded as such.** Both mechanisms are real and act in opposite directions, and neither seat quantified the net; on the evidence before the panel there is no basis to pick a side, and I will not manufacture one. The consequence for the author is nonetheless determinate: name both forces and state that their net is indeterminate under this design, and **delete the "at best one of several factors" ceiling claim**, which is unlicensed under either account — it is supported only if R2's net holds, and R2's net is exactly what the panel could not establish. → **R7**

#### Devil's Advocate findings

No CRITICAL findings were filed. Six MAJOR-band findings and four in-body findings were inventoried. Three (construct/population escalation, common-method rival explanation, comparator unfalsifiability) corroborate positions the non-DA seats already hold and are folded into **R4**, **R6** and **R2**. Two are DA-only and are carried into the roadmap on their own merits: the Discussion's causal inventory asserts symmetry ("equally consistent") while omitting the common-cause structure the paper's own §2 endorses via Ibarra and Poll (**R10**), and the ceiling claim discussed above (**R7**). Three lower-confidence DA findings sit in the Suggested tier with their confidence visible: recruitment-channel range restriction (confidence 3, contingent on a fact the paper does not state), the Spearman check not validating the Fisher-z interval (confidence 4), and the residual-variance attribution (confidence 4).

### Decision Rationale

The decision is `major_revision`, fired by F2: two mandatory dimensions score `block`. Both blocks were typed repairable by the seats that raised them, which is why this is not a rejection — nothing here is categorically outside the venue's remit and nothing requires a different study to fix.

The two blocks are the same wound seen from two seats. This manuscript disclaims causal inference and disclaims model testing, which leaves it exactly one contribution: that r = .42 is a locatable point in an existing distribution. The domain seat blocks because the distribution is never specified — no pooled estimate, no interval, not even the spread from Song (2018), whose multi-campus framing the paper borrows. The venue seat blocks because the comparison set cannot be verified at all: six sequential DOIs on CrossRef's reserved test prefix, no recognisable outlets. Neither seat alleges fabrication and neither has standing to; both report that verification failed, which is the finding an editor must act on. Remove the verified distribution and the paper's sole claim to contribution has nothing to stand on.

What is not in dispute is the reporting craft. Four seats independently credited the same things: a point estimate with a confidence interval that reconciles under Fisher's z, exact-form p, n, an appropriate rank-based robustness check, arithmetic that reconciles across every section (233 − 14 − 5 = 214), complete ethics reporting, and a causal disclaimer placed in the Abstract rather than buried. The reverse pathway is stated as *equally* consistent, which is the correct characterisation and rarer than it should be. This is above the median for the genre, and the panel says so on the record.

Calibration, however, is not contribution. A manuscript that truthfully reports showing very little has told the truth about a manuscript that shows very little. The panel was instructed not to reward hedging as though it were contribution and not to penalise candour — both halves held.

### Scope of this revision request

The three peer reviewers' requests, summed naively, would constitute a different study. They do not sum that way, because each seat drew the line itself: R1 explicitly excludes a second use item and log data as new collection; R2 explicitly declines to demand a TAM/UTAUT specification, a mediator, or additional constructs on two measures and 214 responses; R3 explicitly flags its own professional bias toward trace-data linkage and asks only that the tradeoff be stated. I am holding that line.

**In scope (executable on data already held):** every item in Parts 2's Required and Suggested tables.
**Not in scope, and not conditions of this revision:** log-data validation or linkage, multi-institution sampling, longitudinal waves, a multi-item use measure, a behavioural-intention mediator, any structural model. These belong in the future-work paragraph the Conclusion already begins.

### Surface-form parity check (#216)

Applied before any sub-claim was weighted. No sub-claim was down-weighted for informal or vague phrasing, and none was credited for technical specificity absent paper evidence; the opposite-style counterfactual was run on the DA's body-prose findings and on R3's informally phrased actionability objection, and neither changed weight. SC-33 was placed in the Suggested tier on its stated confidence of 3 and its explicit contingency on a fact the manuscript does not state, not on its wording.

### Top Blocking Issues (2, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | The entire evidence base fails verification — six DOIs on CrossRef's reserved test prefix in a consecutive block, no recognisable outlets — so no cited claim, and therefore no positioning claim, has a confirmable referent. | EIC (W1), R2 (W4) | text: References — "https://doi.org/10.5555/2050001" and "https://doi.org/10.5555/2050006" | R1 |
| 2 | The manuscript's sole stated contribution is positional, and the position is never established: no pooled estimate, interval or range is given anywhere, and the estimand being compared is unnamed. | R2 (W1), EIC (W2 / D6 block) | absence: §2 Literature Review and §5 Discussion — expected a pooled or interval estimate for the perceived-usefulness/use association against which r = .42 is positioned; checked Abstract, §1, §2, §4, §5, §7, References | R2, R3 |

Exactly two issues currently block acceptance. I declined to pad the table to three: the construct-drift finding (R4) is the panel's strongest consensus item and its most-read defect, but it is a Major coherence failure that contributes to a `warn`, not a block, and presenting it as a blocker would misstate what stands between this manuscript and acceptance.

---

# Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`s each item traces to. Source labels use the reviewer tokens EIC / R1 / R2 / R3 / DA; item IDs use the same `R<n>` syntax by template convention — **item R1 is not reviewer R1.** Severity, evidence anchor and confidence are transported from the reviewer cards, never re-derived.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---------------|--------------|----------|-----------------|------------|--------|----------|------------------|
| R1 | Supply verifiable, resolving references for all six cited sources | SC-1 | Critical (EIC) / Major (R2) | text: References — "https://doi.org/10.5555/2050001" and "https://doi.org/10.5555/2050006" | 5 — EIC (maintains venue reference-verification checklist); 4 — R2 (high on observation, deliberately low on cause) | EIC, R2 | P1 | 1–2 days if placeholders; otherwise submission cannot proceed in this form |
| R2 | Specify the comparator distribution and position r = .42 inside it; name the estimand being compared | SC-2, SC-4 | Major (R2, EIC) | absence: §2 and §5 — expected a pooled or interval estimate for the PU/use association; checked Abstract, §1, §2, §4, §5, §7, References | 5 — R2 (author of a TAM-derived e-learning synthesis); 5 — EIC | R2, EIC, DA | P1 | 5–8 days |
| R3 | Reset the article category to a short empirical report / Research Note and rewrite framing, length and claim structure to match — or redirect to an outlet whose research-article bar matches the contribution | SC-3 | Major (EIC) | text: §2 — "It is intended as an incremental data point, comparable with prior work, rather than as a test of a theoretical model." | 5 — EIC (first-pass category triage is this seat's standing function) | EIC | P1 | 2–3 days |
| R4 | Stabilise the outcome construct and the claimed population across Abstract, §2, §4, §5 and §7; remove "engagement"; state which of adoption, continuance or habitual access the outcome operationalises | SC-5 [CONSENSUS-3], SC-6 (DA-only), SC-7 | Major (R1, R2, R3, DA) | text: Abstract — "The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates" vs §2 — "an indicator of perceived use rather than a behavioral count" | 5 — R1, R2, R3 (textual, not interpretive); 5 — DA | R1, R2, R3, DA | P1 | 1 day |
| R5 | Report the eligible-population denominator and the response rate; report the year-level distribution (and discipline, if collected) against institutional figures; revise how much weight the site estimate is said to bear | SC-8, SC-9 | Major (EIC, R1) | text: §3.1 — "All enrolled undergraduates were eligible"; "spanned all four year levels" | 5 — R1 (nonresponse bias in institutional student surveys is a primary research line); 4 — EIC | R1, EIC, DA | P1 | 1–2 days |
| R6 | Name common method variance as a rival account of r = .42 in §6 and, if a plausible marker exists in the instrument, report a marker-based partial-correlation check | SC-10 | Major (R1, R2) | absence: §6 Limitations — expected an explicit common-method-variance limitation with marker-variable or procedural-separation remedy; checked Abstract, §3.2, §3.3, §3.4, §5, §6 | 5 — R1 (single-source design diagnostic); 4 — R2 | R1, R2, DA | P1 | 1 day (+1 if marker check runs) |
| R7 | Disclose the outcome item verbatim with its full category frequency distribution and SD; state that r is an association between measures, not constructs; name both artefact directions and state that their net is indeterminate; delete the "at best one of several factors" ceiling claim | SC-11, SC-12, SC-12b (arbitrated, unresolved dissent), SC-13 (DA-only) | Major (R1); Major (R2 on the bound); Major-band (DA on the ceiling) | text: §3.2 — "Self-reported use was captured with a single five-point frequency item asking how often the respondent accessed the LMS in a typical week"; text: §5 — "perceived usefulness is at best one of several factors bearing on engagement" | 5 — R1 (measurement error in single-item self-report is this seat's primary area); 4 — R2; 4 — DA | R1, R2, DA | P1 | 1–2 days |
| R8 | Add a study-context paragraph: name the platform, state which LMS functions are compulsory for undergraduates, locate the three-week window in the academic calendar, and acknowledge the non-stationarity assumption in the "typical week" item | SC-15, SC-16 | Major (R3) | absence: §3.1 and §3.2 — expected identification of the LMS platform and a statement of which functions are compulsory; checked Abstract, §1, §3.1, §3.2, §5, §6 | 5 — R3 (has run a campus-wide LMS onboarding redesign); 4 — R3 on the calendar/burstiness point | R3 | P1 | 1 day |
| R9 | Make the adapted instrument inspectable: reproduce the six items, describe what the adaptation changed from the source, run a dimensionality check on existing item-level data, and narrow the "previously validated" claim | SC-17 [CONSENSUS-3], SC-18, SC-19, SC-20 | Major (R1) / Minor (EIC, R3, R2) | text: §3.2 — "a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency" | 5 — R1 (scale-adaptation reporting standard); 5 — EIC; 4 — R3; 4 — R2 | R1, EIC, R3, R2 | P1 | 2–3 days |
| R10 | Add the common-cause pathway to the Discussion's inventory of what the correlation is compatible with, and drop "equally" — the paper's own §2 endorses context shaping both perception and use | SC-14 (DA-only) | Major-band (DA) | text: §5 — "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data" | 4 — DA (causal-structure analysis of stated alternatives) | DA | P1 | 0.5 day |

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---------------|--------------|----------|-----------------|------------|--------|----------|------------------|
| S1 | Rebuild the practical implication per arbitration D-1: state the premise it requires or recast as a research question; specify facet, segment and timing or drop; appraise or remove Whitfield (2019) | SC-27 [SPLIT], SC-28 [SPLIT], SC-29 | Minor (R1, R3, EIC) | text: §5 — "LMS onboarding which helps students see concrete usefulness"; "may be worth institutional attention" | 5 — R3 (institutional costing resolution); 4 — R1; 4 — EIC | R3, R1, EIC (R2 dissenting) | P2 | 1 day |
| S2 | Relabel the power statement as a sensitivity analysis on the achieved sample per arbitration D-2; state α numerically in place of "a conventional significance threshold" | SC-21 [SPLIT], SC-22 | Minor (R1) | text: §3.4 — "so the design was sensitive to small-to-moderate associations" | 4 — R1 (a priori vs sensitivity power analysis) | R1 (R3 dissenting) | P2 | 0.5 day |
| S3 | Report r² numerically (≈ .18) rather than as "modest" | SC-23 | Minor (EIC, R1) | text: §4 — "The proportion of variance shared by the two measures was accordingly modest" | 5 — EIC; 5 — R1; 5 — DA | EIC, R1, DA | P2 | 0.25 day |
| S4 | Add the foundational technology-acceptance lineage (Davis 1989; Venkatesh & Davis 2000; Venkatesh et al. 2003; Bhattacherjee 2001) and the e-learning meta-analytic record; stop attributing the field's core proposition to 2019–2020 secondary citations | SC-30 | Minor (R2) | text: §1 and §2 — "a substantial body of work suggests"; "Research on technology acceptance has long proposed that perceived usefulness" | 5 — R2 (lineage and definitional origin are unambiguous) | R2 | P2 | 2 days |
| S5 | State the deduplication criterion for the 5 removed entries and reconcile it with the no-identifiers claim | SC-25 | Minor (R1) | text: §3.3 — "No identifying information was collected, and responses could not be linked back to individual students" | 4 — R1 (tension is real but likely benign) | R1 | P2 | 0.25 day |
| S6 | Characterise the 14 excluded incomplete cases (where they dropped out, whether they differ on observed variables) and report any surviving item-level missingness and its handling | SC-26 | Minor (R1) | text: §3.1 — "14 incomplete submissions and 5 duplicate entries were removed, leaving 214 valid responses" | 4 — R1 (missing-data reporting expectation) | R1 | P2 | 0.5 day |
| S7 | Name the recruitment channel; if it is LMS-delivered or adjacent, discuss range restriction's bearing on the estimate rather than confining voluntary-response bias to generalisability | SC-33 (DA-only) | Major-band (DA) | text: §3.1 — "The survey was distributed through the institution's course-announcement channel over a three-week window." | 3 — DA (selection-mechanism reading, contingent on unstated channel identity) | DA | P2 | 0.5 day |
| S8 | Report a bootstrap interval alongside the Fisher-z interval, or drop the claim that the Spearman check shows the association "did not depend on the parametric assumption" | SC-34 (DA-only) | Major-band (DA) | text: §4 — "indicating that the association did not depend on the parametric assumption" | 4 — DA (statistical-inference reading) | DA | P2 | 0.5 day |
| S9 | Restate the residual-variance attribution as one of several available accounts, single-item measurement error included, since neither named cause was measured | SC-35 (DA-only) | Major-band (DA) | text: §4 — "including course requirements and assessment schedules" | 4 — DA (inference-to-unmeasured-variables reading) | DA | P2 | 0.25 day |
| S10 | State the no-linkage decision as a tradeoff with its measurement cost, and sketch the consent pathway that would have permitted log linkage, so readers elsewhere can weigh it differently | SC-32 | Minor (R3) | text: §3.3 — "No identifying information was collected, and responses could not be linked back to individual students" | 4 — R3 (co-chairs an institutional data-ethics working group; own disciplinary bias flagged) | R3 | P2 | 0.5 day |
| S11 | Supply the inspected scatterplot and a descriptive table for both measures | SC-24 | Minor (EIC, R1) | absence: §4 Results — expected the inspected scatterplot and a descriptive table of both measures; checked §4, §3.4, and all section bodies for figure or table captions | 5 — EIC; 5 — R1 | EIC, R1 | P3 | 0.5 day |
| S12 | Add a data availability statement | SC-31 | Minor (EIC) | absence: back matter — expected a data availability statement and the six adapted scale items; checked §3.2, §3.3, §3.4, References, all post-reference content | 5 — EIC (venue-convention completeness check) | EIC | P3 | 0.25 day |

No funding or conflict-of-interest item appears in this roadmap: no reviewer card raised one, and I am not authorised to add findings the panel did not make.

### Required Item Details

**R1 — Verifiable references**
- **Acceptance criteria**: All six references resolve to registered DOIs at indexed outlets, no DOI sits on the `10.5555` reserved prefix, and every characterisation of prior work in §1, §2 and §5 is traceable to a resolvable source; if a cited source cannot be produced, the claim it supports is removed.

**R2 — Comparator distribution and estimand**
- **Acceptance criteria**: §2 or §5 reports at least one pooled or interval estimate for the perceived-usefulness/use association from the published record, states whether r = .42 falls inside, above or below it, and names which quantity the comparison is against (unmediated bivariate association versus a mediated path coefficient).

**R3 — Article category**
- **Acceptance criteria**: The manuscript is submitted under a short-report or Research Note category with framing, length and claim structure aligned to it, or the authors state on the record which alternative outlet they are targeting and why its article bar matches.

**R4 — Construct and population stability**
- **Acceptance criteria**: "Engagement" no longer appears as a label for the measured outcome in the Abstract, §4 or §5; the outcome is named identically in all five sections; the claimed population is the sampled institution throughout; and §2 states whether the outcome operationalises adoption, continuance or habitual access.

**R5 — Denominator and representativeness**
- **Acceptance criteria**: §3.1 reports the eligible-undergraduate population size and the resulting response rate, reports the analysed sample's year-level distribution (and discipline, if collected) against institutional figures, and §6 revises the voluntary-response limitation to reference that magnitude.

**R6 — Common method variance**
- **Acceptance criteria**: §6 names shared-method variance from same-instrument, same-occasion, single-respondent measurement as a distinct threat from self-report/log divergence, states its expected direction, and either reports a marker-based partial-correlation check or states that no usable marker exists in the instrument.

**R7 — Outcome measure disclosure and bounded interpretation**
- **Acceptance criteria**: §3.2 gives the use item verbatim with all five category labels, §4 reports its full category frequency distribution and SD, the text states that r = .42 is an association between measures rather than constructs, both attenuation and method-inflation are named with their net stated as indeterminate under this design, and the "at best one of several factors" ceiling claim is removed.

**R8 — Study context**
- **Acceptance criteria**: The manuscript names the LMS platform, states which platform functions are compulsory for undergraduates, locates the three-week collection window in the academic calendar relative to assessment clusters, and acknowledges that a "typical week" estimate presumes stationarity that LMS access does not have.

**R9 — Instrument transparency**
- **Acceptance criteria**: The six perceived-usefulness items appear in full with a description of what the adaptation changed from the source instrument, a dimensionality check on the existing item-level data is reported, and the validity claim is narrowed to adaptation-from-a-validated-instrument with internal consistency re-established in this sample.

**R10 — Causal inventory**
- **Acceptance criteria**: §5 lists the common-cause pathway (course design, instructor expectations, assessment structure) alongside the forward and reverse pathways as an account the correlation is compatible with, and the word "equally" no longer characterises a two-item inventory.

### Machine-form Roadmap (Schema 7)

```json
{
  "roadmap_version": "schema7",
  "editorial_decision": "major_revision",
  "items": [
    {"id": "R1", "priority": "must_fix", "reviewer": ["eic", "domain"], "severity": "critical", "confidence": 5, "evidence_anchor": "text: References — \"https://doi.org/10.5555/2050001\" and \"https://doi.org/10.5555/2050006\"", "sub_claims": ["SC-1"], "verification_criteria": "All six references resolve to registered DOIs at indexed outlets; no 10.5555 prefix; unresolvable claims removed."},
    {"id": "R2", "priority": "must_fix", "reviewer": ["domain", "eic", "da"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §2 and §5 — expected pooled or interval estimate for the PU/use association", "sub_claims": ["SC-2", "SC-4"], "verification_criteria": "A pooled or interval prior estimate is reported, r = .42 is located relative to it, and the compared estimand is named."},
    {"id": "R3", "priority": "must_fix", "reviewer": ["eic"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §2 — \"It is intended as an incremental data point, comparable with prior work\"", "sub_claims": ["SC-3"], "verification_criteria": "Submitted as short report/Research Note with framing aligned, or an alternative outlet is named with justification."},
    {"id": "R4", "priority": "must_fix", "reviewer": ["methodology", "domain", "perspective", "da"], "severity": "major", "confidence": 5, "evidence_anchor": "text: Abstract — \"perceived usefulness tracks with LMS engagement among undergraduates\"", "sub_claims": ["SC-5", "SC-6", "SC-7"], "consensus": "CONSENSUS-3", "verification_criteria": "No \"engagement\" label for the measured outcome; one construct name across all sections; population scoped to the sampled site; adoption/continuance/habitual access declared."},
    {"id": "R5", "priority": "must_fix", "reviewer": ["methodology", "eic", "da"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.1 — \"All enrolled undergraduates were eligible\"; \"spanned all four year levels\"", "sub_claims": ["SC-8", "SC-9"], "verification_criteria": "Frame size, response rate, and year-level (and discipline if collected) distribution against institutional figures are reported; §6 references the magnitude."},
    {"id": "R6", "priority": "must_fix", "reviewer": ["methodology", "domain", "da"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §6 Limitations — expected explicit common-method-variance limitation", "sub_claims": ["SC-10"], "verification_criteria": "CMV named as distinct from self-report/log divergence, direction stated, marker check reported or its absence stated."},
    {"id": "R7", "priority": "must_fix", "reviewer": ["methodology", "domain", "da"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.2 single five-point frequency item; text: §5 \"at best one of several factors\"", "sub_claims": ["SC-11", "SC-12", "SC-12b", "SC-13"], "arbitration": "unresolved_dissent", "verification_criteria": "Item verbatim, full category distribution and SD reported; r framed as between measures; both artefact directions named with net indeterminate; ceiling claim deleted."},
    {"id": "R8", "priority": "must_fix", "reviewer": ["perspective"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §3.1 and §3.2 — expected platform identification and compulsory-function statement", "sub_claims": ["SC-15", "SC-16"], "verification_criteria": "Platform named, compulsory functions stated, collection window located in the calendar, non-stationarity of \"typical week\" acknowledged."},
    {"id": "R9", "priority": "must_fix", "reviewer": ["methodology", "eic", "perspective", "domain"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.2 — \"a six-item scale adapted from Costa and Wren (2019)\"", "sub_claims": ["SC-17", "SC-18", "SC-19", "SC-20"], "consensus": "CONSENSUS-3", "verification_criteria": "Six items reproduced, adaptation described, dimensionality check reported, validity claim narrowed to the adapted form."},
    {"id": "R10", "priority": "must_fix", "reviewer": ["da"], "severity": "major", "confidence": 4, "evidence_anchor": "text: §5 — \"the reverse pathway ... is equally consistent with the data\"", "sub_claims": ["SC-14"], "verification_criteria": "Common-cause pathway listed alongside forward and reverse pathways; \"equally\" removed from a two-item inventory."},
    {"id": "S1", "priority": "should_fix", "reviewer": ["perspective", "methodology", "eic"], "severity": "minor", "confidence": 5, "evidence_anchor": "text: §5 — \"LMS onboarding which helps students see concrete usefulness\"", "sub_claims": ["SC-27", "SC-28", "SC-29"], "arbitration": "split_resolved", "verification_criteria": "Premise stated and facet/segment/timing specified, or recast as a research question; Whitfield appraised or removed."},
    {"id": "S2", "priority": "should_fix", "reviewer": ["methodology"], "severity": "minor", "confidence": 4, "evidence_anchor": "text: §3.4 — \"so the design was sensitive to small-to-moderate associations\"", "sub_claims": ["SC-21", "SC-22"], "arbitration": "split_resolved", "verification_criteria": "Statement labelled a sensitivity analysis on the achieved sample; alpha stated numerically."},
    {"id": "S3", "priority": "should_fix", "reviewer": ["eic", "methodology", "da"], "severity": "minor", "confidence": 5, "evidence_anchor": "text: §4 — \"The proportion of variance shared by the two measures was accordingly modest\"", "sub_claims": ["SC-23"], "verification_criteria": "r squared reported numerically in §4."},
    {"id": "S4", "priority": "should_fix", "reviewer": ["domain"], "severity": "minor", "confidence": 5, "evidence_anchor": "text: §1 and §2 — \"a substantial body of work suggests\"", "sub_claims": ["SC-30"], "verification_criteria": "Foundational lineage and e-learning meta-analytic record cited; field-level claims no longer rest on 2019-2020 secondary citations."},
    {"id": "S5", "priority": "should_fix", "reviewer": ["methodology"], "severity": "minor", "confidence": 4, "evidence_anchor": "text: §3.3 — \"No identifying information was collected\"", "sub_claims": ["SC-25"], "verification_criteria": "Deduplication criterion stated and reconciled with the anonymity claim."},
    {"id": "S6", "priority": "should_fix", "reviewer": ["methodology"], "severity": "minor", "confidence": 4, "evidence_anchor": "text: §3.1 — \"14 incomplete submissions and 5 duplicate entries were removed\"", "sub_claims": ["SC-26"], "verification_criteria": "Excluded cases characterised; surviving item-level missingness and its handling reported."},
    {"id": "S7", "priority": "should_fix", "reviewer": ["da"], "severity": "major", "confidence": 3, "evidence_anchor": "text: §3.1 — \"distributed through the institution's course-announcement channel\"", "sub_claims": ["SC-33"], "verification_criteria": "Channel named; if LMS-delivered, range restriction discussed as bearing on the estimate."},
    {"id": "S8", "priority": "should_fix", "reviewer": ["da"], "severity": "major", "confidence": 4, "evidence_anchor": "text: §4 — \"indicating that the association did not depend on the parametric assumption\"", "sub_claims": ["SC-34"], "verification_criteria": "Bootstrap interval reported, or the interval-validation claim withdrawn."},
    {"id": "S9", "priority": "should_fix", "reviewer": ["da"], "severity": "major", "confidence": 4, "evidence_anchor": "text: §4 — \"including course requirements and assessment schedules\"", "sub_claims": ["SC-35"], "verification_criteria": "Residual-variance attribution presented as one of several accounts, measurement error included."},
    {"id": "S10", "priority": "should_fix", "reviewer": ["perspective"], "severity": "minor", "confidence": 4, "evidence_anchor": "text: §3.3 — \"responses could not be linked back to individual students\"", "sub_claims": ["SC-32"], "verification_criteria": "No-linkage decision stated as a tradeoff with its measurement cost and the consent pathway sketched."},
    {"id": "S11", "priority": "nice_to_fix", "reviewer": ["eic", "methodology"], "severity": "minor", "confidence": 5, "evidence_anchor": "absence: §4 Results — expected the inspected scatterplot and a descriptive table", "sub_claims": ["SC-24"], "verification_criteria": "Scatterplot and descriptive table for both measures supplied."},
    {"id": "S12", "priority": "nice_to_fix", "reviewer": ["eic"], "severity": "minor", "confidence": 5, "evidence_anchor": "absence: back matter — expected a data availability statement", "sub_claims": ["SC-31"], "verification_criteria": "Data availability statement present in back matter."}
  ]
}
```

### Revision Checklist

#### Priority 1 — Structural Revisions (estimated total: 15–19 days)
- [ ] R1: Supply verifiable, resolving references for all six sources
- [ ] R2: Specify the comparator distribution and position r = .42 within it; name the estimand
- [ ] R3: Reset the article category (or name the alternative outlet) and rewrite framing to match
- [ ] R4: Stabilise the outcome construct and population across all five sections
- [ ] R5: Report the denominator, response rate and sample-composition comparison
- [ ] R6: Name common method variance; run the marker check if a marker exists
- [ ] R7: Disclose the outcome item and its distribution; bound r honestly; delete the ceiling claim
- [ ] R8: Add the study-context paragraph (platform, compulsory functions, calendar position)
- [ ] R9: Make the adapted instrument inspectable and check its dimensionality
- [ ] R10: Add the common-cause pathway; drop "equally"

#### Priority 2 — Content Supplementation (estimated total: 6–7 days)
- [ ] S1: Rebuild the practical implication per arbitration D-1
- [ ] S2: Relabel the power statement per arbitration D-2; state α numerically
- [ ] S3: Report r² numerically
- [ ] S4: Add the foundational lineage and meta-analytic record
- [ ] S5: State the deduplication criterion
- [ ] S6: Characterise excluded cases and item-level missingness
- [ ] S7: Name the recruitment channel; address range restriction if applicable
- [ ] S8: Report a bootstrap interval or withdraw the interval-validation claim
- [ ] S9: Soften the residual-variance attribution to one of several accounts
- [ ] S10: State the no-linkage decision as a tradeoff

#### Priority 3 — Text and Formatting (estimated total: 1 day)
- [ ] S11: Supply the scatterplot and a descriptives table
- [ ] S12: Add a data availability statement

### Revision Deadline

Recommended 6–8 weeks. The estimate assumes the six citations exist and the DOIs were placeholders. If sources must be located from scratch, or if any cited finding cannot be produced, the timeline is not the binding constraint and the authors should contact the editorial office before resubmitting.

### Response Letter Template

Please respond to every numbered item (R1–R10, S1–S12) using `templates/revision_response_template.md`. Items R1–R10 require a substantive response; a respectful decline is not available for them. Items S1–S12 may be declined with reasoning. Where an item records a split or unresolved dissent (S1, S2, R7), the arbitrated instruction in Part 1 is what the response should address, not the raw reviewer positions.

---

# Part 3: Reviewer Report Summary (Appendix)

Under this contract seats emit per-dimension scores rather than an overall Accept/Revise/Reject recommendation, and per-finding rather than report-level confidence. No overall recommendation or single confidence score is available for any seat, and none has been imputed.

### Journal-Fit Reviewer (EIC)
- Dimension verdicts: D5 = warn, D6 = block (repairable) | 7 weaknesses (1 Critical, 2 Major, 4 Minor), 4 strengths | per-finding confidence 4–5
- Key point: the contribution claim is entirely relational and the relation cannot be established, because the comparison set fails verification on all six references — with the reporting craft credited on the record as above the genre median.

### Reviewer 1 — Methodology
- Dimension verdicts: D1 = warn (top of band), D3 = warn | 10 weaknesses (5 Major, 5 Minor), 5 strengths | per-finding confidence 4–5
- Key point: r = .42 is presented as a portable quantity while both ingredients that fix its meaning — outcome reliability and the sampling denominator — are undisclosed, and every request made is executable on data already held.

### Reviewer 2 — Domain
- Dimension verdicts: D2 = block (repairable) | 6 weaknesses (4 Major, 2 Minor), 4 strengths | per-finding confidence 4–5
- Key point: the paper invokes Song's "one point in a distribution" framing as a commitment and then never specifies the distribution, so "consistent with prior research" is unfalsifiable and the sole contribution cannot stand as written.

### Reviewer 3 — Cross-disciplinary / Perspective
- Dimension verdicts: D4 = warn | 6 weaknesses (3 Major, 3 Minor), 4 strengths | per-finding confidence 4–5
- Key point: the object of measurement is never described — no platform, no compulsory-function statement, no calendar position — so an adjacent-field or operator reader cannot interpret r = .42 or situate it against their own environment.

### Devil's Advocate
- Dimension verdicts: D3 = warn | 0 CRITICAL, 6 MAJOR-band table findings, 4 in-body findings | per-finding confidence 3–5
- Key point: the hedging is decorative at three seams — the consistency claim admits no disconfirming result, the causal inventory omits the confound the paper's own §2 endorses, and the "at best" ceiling asserts a bound the measurement does not deliver.

---

## Appendix: Sub-Claim Inventory (Step 1b, condensed)

Encoding note: one row per sub-claim with reviewer positions as columns, which preserves every `(sub_claim, reviewer)` position in denser form. Positions: `R` raised, `C` corroborated, `D` disputed, `–` not-mentioned (silence, not opposition). Consensus counts use the four non-DA seats only. Every sub-claim decomposes a claim a reviewer actually made; none was authored here.

| SC | Sub-claim (parent weakness) | EIC | R1 | R2 | R3 | DA | agree/conflict | Disposition | Item |
|----|------|-----|----|----|----|----|----------------|-------------|------|
| SC-1 | Reference base unverifiable (EIC W1 / R2 W4) | R | – | C | – | – | 2/0 | corroborated | R1 |
| SC-2 | Positional claim has no specified comparator (R2 W1 / EIC D6 / DA M1) | C | – | R | – | C | 2/0 | corroborated | R2 |
| SC-3 | Below research-article bar; recategorise (EIC W2) | R | – | – | – | – | 1/0 | single-reviewer | R3 |
| SC-4 | Estimand compared is unnamed (R2 W1) | – | – | R | – | – | 1/0 | single-reviewer | R2 |
| SC-5 | "Engagement" substituted for measured outcome (R1 W9 / R2 W2 / R3 W1 / DA M3) | – | R | C | C | C | 3/0 | **CONSENSUS-3** (silent: EIC) | R4 |
| SC-6 | Population escalated to "undergraduates" (DA M3) | – | – | – | – | R | DA-only | DA-tracked | R4 |
| SC-7 | Adoption/continuance/habitual access conflated (R2 W2) | – | – | R | – | – | 1/0 | single-reviewer | R4 |
| SC-8 | No denominator / response rate (EIC W3 / R1 W2 / DA) | R | C | – | – | C | 2/0 | corroborated | R5 |
| SC-9 | Sample composition vs institution unreported (R1 W2) | – | R | – | – | – | 1/0 | single-reviewer | R5 |
| SC-10 | CMV not named or remedied (R1 W3 / R2 W3 / DA M4) | – | R | C | – | C | 2/0 | corroborated | R6 |
| SC-11 | Single-item outcome: wording, distribution, SD undisclosed (R1 W1) | – | R | – | – | – | 1/0 | single-reviewer | R7 |
| SC-12 | Direction of artefact bound must be stated (R1 W1 / R2 W3) | – | R | C | – | – | 2/0 | corroborated | R7 |
| SC-12b | Net bound is upward (.42 an upper bound) (R2 W3 vs DA M6) | – | – | R | – | D | cross-panel | **unresolved dissent** | R7 |
| SC-13 | "At best one of several factors" ceiling unlicensed (DA M6) | – | – | – | – | R | DA-only | DA-tracked | R7 |
| SC-14 | Causal inventory omits common cause; "equally" misstates (DA M2) | – | – | – | – | R | DA-only | DA-tracked | R10 |
| SC-15 | Platform / compulsory functions unstated (R3 W2) | – | – | – | R | – | 1/0 | single-reviewer | R8 |
| SC-16 | Window unlocated; "typical week" non-stationarity (R3 W3) | – | – | – | R | – | 1/0 | single-reviewer | R8 |
| SC-17 | Six PU items not reproduced (R1 W4 / EIC W7 / R3 W4) | C | R | – | C | – | 3/0 | **CONSENSUS-3** (silent: R2) | R9 |
| SC-18 | What "adapted" changed unreported (R1 W4 / R3 W4) | – | R | – | C | – | 2/0 | corroborated | R9 |
| SC-19 | α is not evidence of preserved factor structure (R1 W4 / R2 W6) | – | R | C | – | – | 2/0 | corroborated | R9 |
| SC-20 | "Previously validated" over-transfers (R2 W6) | – | – | R | – | – | 1/0 | single-reviewer | R9 |
| SC-21 | Power statement is post-hoc sensitivity (R1 W5 vs R3 S3) | – | R | – | D | – | 1/1 | **[SPLIT]** resolved D-2 | S2 |
| SC-22 | α not stated numerically (R1 W5) | – | R | – | – | – | 1/0 | single-reviewer | S2 |
| SC-23 | r² not reported numerically (EIC W5 / R1 W6 / DA) | R | C | – | – | C | 2/0 | corroborated | S3 |
| SC-24 | Scatterplot and descriptives absent (EIC W6 / R1 W6) | R | C | – | – | – | 2/0 | corroborated | S11 |
| SC-25 | Deduplication criterion unstated (R1 W7) | – | R | – | – | – | 1/0 | single-reviewer | S5 |
| SC-26 | Excluded cases uncharacterised (R1 W8) | – | R | – | – | – | 1/0 | single-reviewer | S6 |
| SC-27 | Implication directional despite bidirectionality (R1 W10 vs R2 S4) | – | R | D | – | – | 1/1 | **[SPLIT]** resolved D-1 | S1 |
| SC-28 | Implication unspecifiable (R3 W5 / EIC W4 vs R2 S4) | C | – | D | R | – | 2/1 | **[SPLIT]** resolved D-1 | S1 |
| SC-29 | Whitfield enters late, unappraised (EIC W4) | R | – | – | – | – | 1/0 | single-reviewer | S1 |
| SC-30 | Foundational lineage absent (R2 W5) | – | – | R | – | – | 1/0 | single-reviewer | S4 |
| SC-31 | No data availability statement (EIC W7) | R | – | – | – | – | 1/0 | single-reviewer | S12 |
| SC-32 | Anonymity tradeoff not connected (R3 W6) | – | – | – | R | – | 1/0 | single-reviewer | S10 |
| SC-33 | Recruitment channel may condition frame on outcome (DA M5) | – | – | – | – | R | DA-only | DA-tracked | S7 |
| SC-34 | Spearman does not validate the Fisher-z interval (DA body) | – | – | – | – | R | DA-only | DA-tracked | S8 |
| SC-35 | Residual variance attributed to specific unmeasured causes (DA body) | – | – | – | – | R | DA-only | DA-tracked | S9 |

Severity and confidence for every sub-claim are transported from the source card as recorded in Part 2; no `[SEVERITY-SOURCE: letter-fallback]` or `[CONFIDENCE-SOURCE: report-level]` fallbacks were needed, as all five cards carry per-finding severity and confidence.

---

*Revision-side work (drafting the revised manuscript, preparing the response letter) is outside this phase. Control returns to the caller.*
