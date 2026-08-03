# Editorial Decision Package

## Contract Audit (v3.6.2 Sprint Contract Synthesizer Protocol)

**Contract**: `reviewer/reviewer_full/v2` · mode `reviewer_full` · stage `reviewer_full_review` · baseline `v3.20.0` · panel_size 5

### Step 1 — Role-scoped scoring matrix

| Dim | Priority | Eligible roles | Assessed eligible seats | Scores | Dimension verdict |
|-----|----------|----------------|-------------------------|--------|-------------------|
| D1 methodology_rigor | mandatory | methodology | methodology (owner) | block (`repairable`) | **block** |
| D2 domain_accuracy | mandatory | domain | domain (owner) | block (`fatal`) | **block(fatal)** |
| D3 argumentative_coherence | mandatory | da, methodology | da (owner), methodology | warn, warn | **warn** |
| D4 cross_disciplinary_relevance | high | perspective | perspective (owner) | warn | **warn** |
| D5 writing_and_structure | normal | eic | eic (owner) | warn | **warn** |
| D6 venue_fit_and_contribution | mandatory | eic | eic (owner) | block (`repairable`) | **block** |

All six dimensions have ≥1 assessed eligible seat; no `[DIMENSION-UNASSESSED]`. Ineligible `not_assessed` values were excluded from every numerator and denominator. Audit verdict: **block(fatal)**.

### Step 2 — Failure-condition evaluation

| ID | Sev | Quantifier | Expression | Per-dimension result | Fired |
|----|-----|-----------|------------|----------------------|-------|
| F1 | 95 | any | any mandatory dimension has a fatal block | D1 F, **D2 T**, D3 F, D6 F | **true** |
| F2 | 90 | any | any mandatory dimension scores 'block' | **D1 T, D2 T**, D3 F, **D6 T** | **true** |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | **D1 T, D2 T, D3 T, D6 T** (4 ≥ 2) | **true** |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4 F (warn, not block) | false |
| F5 | 40 | any | any dimension scores 'warn' or worse | **D1 T** | **true** |
| F0 | 10 | all | every dimension scores 'pass' | F | false |

F3 note: for D1/D2/D6 the eligible-seat count is n=1, so `majority` resolves to the owner seat itself; for D3 (n=2) `majority` requires both seats — da and methodology both scored `warn`. Fatal scope was tested only on mandatory dimensions.

### Step 3 — Precedence and emission

```
dimension_verdicts: [D1=block, D2=block(fatal), D3=warn, D4=warn, D5=warn, D6=block]
fired_conditions: [F1, F2, F3, F5]
da_critical_adjudications: []
editorial_decision=reject
```

Highest severity among fired conditions is F1 (95) → `action: editorial_decision=reject`. Ties: none. The Devil's Advocate CRITICAL band is empty by the DA's own statement ("the CRITICAL band below is empty by finding, not by courtesy"), so no `C<n>` IDs exist and no `[DA-CRITICAL-VS-ACCEPT]` marker applies.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript, "Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students." It was assessed by five reviewers: a Journal-Fit Reviewer, three peer reviewers (methodology, domain, cross-disciplinary/practitioner), and a Devil's Advocate.

### Decision: **Reject**

### Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — this run is `reviewer_full`, in which a panel-provenance statement is mandatory, but no provenance stamp was supplied by the dispatching layer. I am not permitted to infer which model family ran which seat, so no statement about cross-model slot activity, single-family composition, or dispatch fallback can be made here. **The dispatching layer must supply the stamp before this letter ships.** Nothing in this package should be read as implying model independence across the five seats.

### Consensus Analysis

#### A structural note before the counts

This panel was configured for **deliberate non-overlap** — the field analysis partitioned coverage so that "no two cards claim the same finding," and each card names the territory it does not enter. The consequence is arithmetic, not substantive: with a partitioned panel, **no weakness reaches CONSENSUS-4 or CONSENSUS-3**, and most findings sit at 1/4 or 2/4 by design. Readers should not infer from the absence of consensus labels that the panel was scattered or that the findings are weakly supported. The decision is driven by the contract arithmetic over dimension verdicts, not by consensus counts.

#### Points of Agreement

- **[CONSENSUS-4] Inferential and causal restraint is genuine and correctly targeted.** All four non-DA reviewers independently credited the same passage (§5, "the reverse pathway... is equally consistent with the data"), and the Devil's Advocate confirmed the causal disclaimer is in the abstract rather than buried. This is unanimous and it is the manuscript's strongest property.
- **Corroborated (2/4) — instrument documentation is absent** (methodology + domain): what was adapted, the administered wording, and dimensionality evidence for the six items are all missing, and α = .88 does not substitute for any of them.
- **Corroborated (2/4) — the comparability claim is never operationalised** (Journal-Fit + domain, plus DA M2): no prior or pooled estimate appears anywhere, so r = .42 is unlocatable and "consistent with prior research" is unfalsifiable as written.
- **Corroborated (2/4) — the six-source reference base is below the floor for the article type** (Journal-Fit + domain).
- **Corroborated (2/4) — no tables or figures at all**, including the scatterplot §3.4 relies on (Journal-Fit + methodology, plus DA).
- **Corroborated (2/4) — descriptive capacity of the sample is unused**: no year-level breakdown, no use-item frequency distribution, no full anchor labels (methodology + Journal-Fit).

#### Points of Disagreement (arbitrated)

**SPLIT-1 — SC-4: Is the §3.3 anonymity/non-linkability statement accurate as written?**
Methodology (Major, conf 5) and DA M4 hold that §3.1's removal of "5 duplicate entries" and §3.3's "responses could not be linked back to individual students" cannot both be true. The Journal-Fit Reviewer's S3 credits the ethics reporting as "crisp and complete" and clearing venue requirements without editorial query — an implicit dispute, since a statement that may be inaccurate does not clear a venue check.
- **Editor's Resolution: uphold methodology.** Evidence-first: the contradiction is visible on the manuscript's face and admits no reading in which both statements hold. Expertise-first: human-subjects reporting sits in the methodology seat; the Journal-Fit credit is a *completeness* check (are the required elements present?), not an *internal-consistency* check, and the Journal-Fit Reviewer expressly limited its own scope. Confidence weighting favours methodology (5, with DA at 4 corroborating) over an untagged strength claim. **S3's credit is narrowed to "all required ethics elements are present"; the accuracy of the non-linkability statement is unresolved and Required (R4).**

**SPLIT-2 — SC-5: Is the analytic-sample derivation (233 − 14 − 5 = 214) verifiable?**
Methodology (Major, conf 5) and DA M4 say no, because the duplicate-identification rule is undisclosed. The Journal-Fit Reviewer's S4 ("lets a reader reconstruct the analytic sample") and the perspective seat's S3 ("lets a practitioner reconstruct the denominator instead of trusting it") both assert the opposite property.
- **Editor's Resolution: uphold methodology, and narrow — not withdraw — the credits.** Decomposition dissolves most of the conflict: the exclusion *counts* are itemised by reason (true, and creditable), while the *rule* behind one of those counts is undisclosed (also true). Neither disputing seat engaged §3.3 or claimed the duplicate rule was documented. **The strengths stand as "exclusion counts itemised by reason"; the reconstructability implication in both is withdrawn; the weakness stands and is Required (R4).**

**SPLIT-3 — SC-8: What severity attaches to the Abstract's "previously validated instrument" claim?**
Methodology tags it Minor (conf 5, "will likely resolve alongside" the instrument-documentation finding); domain tags the same claim Major (conf 4), on the ground that validation warrant for acceptance instruments rests on factor structure and convergent–discriminant evidence, and that adaptation suspends whatever validation the source carried.
- **Editor's Resolution: Major.** Expertise-first: construct-validity standards for this instrument lineage are the domain seat's core area, and it supplied the specific warrant; the methodology seat's own W3 states that validation "does not transfer automatically across adaptation," which supports the higher severity — its Minor tag reflects that the *edit* is small, not that the *claim* is small. **Transported pair recorded as (Minor / Major); arbitrated to Major; item Required (R6), contingent on R5.**

#### Apparent conflicts examined and cleared

- **Reference base: "fixable in revision" (Journal-Fit) vs. fatal integrity block (domain).** Not a conflict. These are different sub-claims: *coverage adequacy* (SC-10, both seats agree, both say fixable) and *verifiability of the entries that exist* (SC-1, domain only). The correct ordering is that verifiability is antecedent — a base whose existing entries cannot be located cannot be expanded or benchmarked against.
- **The predicted three-way expansion conflict did not materialise.** Each seat pre-emptively self-limited: methodology ("I do not think this manuscript is obliged to fit a latent-variable model"), domain ("I am not asking for theoretical elaboration that would break the paper's deliberately narrow frame"), perspective ("a bounded descriptive note is not obliged to model variance"). No arbitration required.
- **Sensitivity statement.** The Journal-Fit Reviewer's S2 credits its presence while explicitly disclaiming endorsement of the computation; methodology W7 and DA item (d) contest the framing and the threshold. No dispute — the credit and the critique address different properties.

#### Devil's Advocate handling

The DA CRITICAL band is empty by the DA's own finding, which the DA states directly rather than by omission. Its four MAJOR items were adjudicated as: **M1 validated** (DA-only, no non-DA seat raised it — Required as R3); **M2 validated** (corroborates Journal-Fit W1 and domain W3 — R7); **M3 validated** (corroborated in substance by the perspective seat's W3 — R12); **M4 validated** (drives SPLIT-1 and SPLIT-2 above — R4). No DA finding was rejected, so no rejection rationale is required.

### Decision Rationale

The decision follows the contract arithmetic: F1 fired on a fatal block declared by the domain seat against D2, and F1 carries the highest severity among the four fired conditions. I record explicitly that this is not a close call reached by aggregating dissatisfaction — three of four mandatory dimensions scored `block`, and F2, F3 and F5 fired independently of F1. Even with the fatal block set aside, F2 would have fired and returned major revision.

The substance behind the fatal block is that all six references carry DOIs on the `10.5555` prefix — a registration-agency test prefix, not a publisher prefix — with suffixes running sequentially 2050001–2050006 in reference-list order, across six differently-named journals. A DOI prefix is assigned per registrant, so six independently published articles cannot legitimately share one. Every substantive domain claim in the manuscript routes through those six entries, including the instrument's prior validation and the comparability claim on which the stated contribution rests.

**A procedural note that does not change the decision.** The panel's own field analysis raised an alternative reading the domain card did not consider: this pattern may be an artifact of manuscript anonymisation or placeholder drafting rather than of fabrication. I cannot re-score a seat's assessed dimension and I may not soften a fired condition's action, so the decision stands as emitted. But the editor should establish which explanation holds before this letter is sent, because the two lead to very different next steps for the author — a resubmission with a real reference base, versus a research-integrity process. I flag this as an unresolved factual question, not as a finding of misconduct.

I want to be direct with the authors about the rest. The manuscript's inferential discipline is real, unanimously credited, and better than most submissions in this area. That discipline does not carry the paper. Three separate load-bearing Methods elements are undocumented or self-contradictory, the contribution is asserted rather than located, and the practical implication survives every possible value of the coefficient. These are repairable, and the roadmap below is written on the assumption that the authors will want to repair them.

### Top Blocking Issues (ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | Entire citation base is unverifiable — six DOIs on the `10.5555` test prefix with sequential suffixes across six distinct journals; every domain claim routes through them (fatal block, D2) | R2 (domain) | `text: §References, first and last entries, "10.5555/2050001" and "10.5555/2050006"` | R1 |
| 2 | Three load-bearing Methods elements are absent or self-contradictory — no enrolment denominator, undocumented instrument adaptation, deduplication basis that §3.3 appears to preclude (block, D1) | R1 (methodology), DA | `absence: §3.1 Design and participants — expected total eligible enrollment and a computed response rate; checked §3.1, §3.4, §6, and the abstract` | R2, R4, R5 |
| 3 | Contribution is never located against the literature it claims comparability with, and the reference base cannot support the claim (block, D6) | Journal-Fit, R2 (domain), DA | `absence: §2 Literature Review and §5 Discussion — expected quantitative benchmarking of r = .42 against pooled acceptance-model meta-analytic estimates; checked Abstract, §2, §4, §5, §7, References` | R7, R8 |

---

## Part 2: Revision Roadmap

> This roadmap accompanies a **Reject**. It is provided because the panel judged the underlying study competently executed and the defects repairable in a redeveloped manuscript — not as a revise-and-resubmit instruction. Item R1 is antecedent to everything else: until the citation base is established, R7–R10 cannot be attempted and no other work is worth doing.

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. Severity, evidence anchor, and confidence are transported from the reviewer cards, not re-derived; arbitrated severities are marked.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---------------|--------------|----------|-----------------|------------|--------|----------|------------------|
| R1 | Establish that every cited source exists as described, or replace the citation base | SC-1 | Critical | `text: §References, first and last entries, "10.5555/2050001" and "10.5555/2050006"` | 5 — reference verification and DOI-prefix administration are routine first-pass work | R2 (domain) | P1 | 1–2 days if anonymisation artifact; weeks if not |
| R2 | Report total eligible enrolment for the survey window and compute a response rate | SC-2 | Major | `absence: §3.1 Design and participants — expected total eligible enrollment and a computed response rate; checked §3.1, §3.4, §6, and the abstract` | 5 — teaches survey sampling; baseline expectation | R1 (methodology) | P1 | 0.5 day |
| R3 | Disclose the recruitment channel's relationship to the LMS and assess selection on the outcome | SC-3 | Major | `text: §3.1 "distributed through the institution's course-announcement channel" and §6 "students who engage more with institutional channels may be overrepresented"` | 4 — survey sampling and selection-bias reasoning | DA (M1) | P1 | 1 day |
| R4 | Resolve the anonymity/deduplication contradiction on both branches: correct §3.3 **or** document the duplicate-identification rule | SC-4, SC-5 | Major | `text: §3.1 and §3.3 "5 duplicate entries were removed" versus "No identifying information was collected, and responses could not be linked back to individual students"` | 5 — routine survey data-handling and human-subjects reporting review | R1 (methodology), DA (M4) | P1 | 0.5–1 day (SPLIT-1, SPLIT-2 arbitrated) |
| R5 | Document the instrument adaptation: state what changed and why, reproduce the administered items, report a dimensionality check | SC-6, SC-7 | Major | `text: §3.2 Measures "a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"` | 5 — psychometrics background; standard requirement for a borrowed scale | R1 (methodology), R2 (domain) | P1 | 2–3 days |
| R6 | Correct or earn the Abstract's "previously validated instrument" claim | SC-8 | Major (arbitrated; transported pair Minor/Major) | `text: Abstract "Perceived usefulness was measured with an adapted, previously validated instrument"` | 5 / 4 — direct reading of abstract against §3.2; construct-validity standards | R1 (methodology), R2 (domain) | P1 | 0.5 day (SPLIT-3 arbitrated) |
| R7 | Benchmark r = .42 against stated prior estimates and make the comparability claim falsifiable | SC-9 | Major | `absence: §2 Literature Review and §5 Discussion — expected quantitative benchmarking of r = .42 against pooled acceptance-model meta-analytic estimates; checked Abstract, §2, §4, §5, §7, References` | 5 — editorial familiarity with the acceptance-model literature stock | Journal-Fit, R2 (domain), DA (M2) | P1 | 4–6 days |
| R8 | Expand the reference base substantively: foundational acceptance work, UTAUT family, post-2021 LMS-use studies, learning-analytics on behavioural measures | SC-10, SC-11, SC-12, SC-13 | Major | `absence: §References and §2 Literature Review — expected foundational acceptance-model sources, UTAUT-family work, post-2021 LMS-use studies, and learning-analytics work on behavioral LMS measures; checked all six reference entries, §1, §2, §6` | 5 / 4 — weekly desk screening; literature-currency tracking | Journal-Fit, R2 (domain) | P1 | 5–8 days |
| R9 | Declare the target article type and argue for it; replace modesty framing with a stated increment | SC-14, SC-15 | Major | `text: Abstract "The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates"` | 4 — sufficiency and article-type calls are venue-relative | Journal-Fit | P1 | 1–2 days |
| R10 | Correct the estimand: name and justify the dropped behavioural-intention step; restore construct provenance | SC-16 | Major | `text: §2 Literature Review, "perceived usefulness — the degree to which a person believes a technology will help them perform better", "is among the factors associated with adoption and continued use"` | 5 — canonical instrument lineage and its mediation structure | R2 (domain) | P1 | 2–3 days |
| R11 | Acknowledge attenuation from the coarse single-item outcome and carry it into the comparability claim; correct the Spearman framing | SC-17, SC-18 | Major | `text: §4 Results "indicating that the association did not depend on the parametric assumption"` | 4 — direct specialisation in single-item self-report measurement | R1 (methodology) | P1 | 1 day |
| R12 | Add common-cause confounding to the stated inferential limits; relocate or withdraw the untested §4 attribution | SC-19, SC-20 | Major | `text: §2 "in shaping both perception and use" and §5 "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"` | 4 — causal-inference reasoning about observational associations | DA (M3), R3 (perspective) | P1 | 1 day |
| R13 | State why behavioural log data was not obtained or a consented validation subsample was infeasible | SC-21 | Major | `absence: §6 Limitations and §3.3 Procedure and ethics — expected a stated reason log data was unavailable or subsample validation infeasible; checked Abstract, §1, §3.1, §3.2, §3.3, §3.4, §4, §5, §6, §7` | 5 — operates the LMS, owns its clickstream, processes the approvals | R3 (perspective) | P1 | 0.5 day |
| R14 | Substantiate the onboarding implication or remove it from the Abstract and demote it to a research hypothesis | SC-22 | Major | `text: §5 "modest support for the intuition that LMS onboarding which helps students see concrete usefulness"` | 4 — designs, budgets, and evaluates the targeted programmes | R3 (perspective) | P1 | 0.5 day |
| R15 | Either measure the site's contextual determinants or narrow the cross-site comparability framing to match what was observed | SC-23 | Major | `text: §4 "including course requirements and assessment schedules"` | 5 — daily operational knowledge of LMS access drivers | R3 (perspective) | P1 | 1 day (narrow) or new collection (measure) |

### Required Item Details

#### R1 — Establish the citation base
All six DOIs sit on `10.5555`, a registration-agency test prefix, with suffixes incrementing sequentially in reference-list order across six differently-named journals. A DOI prefix is assigned per registrant, so this pattern is not consistent with six independent publications. If the pattern is an anonymisation artifact, say so and supply the real records; if not, the reference base must be rebuilt.
- **Acceptance criteria**: Every reference resolves to a locatable published record with a live DOI on a genuine registrant prefix, and each claim currently attributed to a placeholder entry is either re-attributed to a verified source or withdrawn.

#### R2 — Report the sampling denominator
Eligibility is stated as universal but total enrolment is never given, so the response rate is uncomputable and §6's acknowledged volunteer bias cannot be bounded even approximately.
- **Acceptance criteria**: §3.1 reports total eligible undergraduate enrolment for the survey window and a computed response rate, and where available compares respondent year-level distribution against enrolment composition.

#### R3 — Disclose the recruitment channel
If the "institution's course-announcement channel" is the LMS or is driven by it, invitation visibility was proportional to the dependent variable and students in the lowest use category are close to unsamplable — a different and sharper concern than the generic volunteer bias §6 concedes.
- **Acceptance criteria**: §3.1 states whether the recruitment channel is the LMS or independent of it, and §6 addresses truncation of the outcome's range as a distinct threat where the channel is LMS-linked.

#### R4 — Resolve the anonymity/deduplication contradiction
§3.1 removes five duplicates; §3.3 states no identifying information was collected and responses could not be linked to individuals. One statement is inaccurate. Either an identifier or quasi-identifier was retained — in which case the ethics and anonymity statement requires correction — or the duplicate rule was heuristic and undisclosed, in which case an undocumented exclusion criterion altered the analysed n. Both branches must be answered, not one.
- **Acceptance criteria**: §3.1 states the mechanism by which duplicates were identified and §3.3 accurately describes what data were retained, with the two statements mutually consistent on the manuscript's face.

#### R5 — Document the instrument adaptation
The perceived-usefulness scale is the only multi-item measure and its provenance is given only as "adapted from," with no statement of what changed, no administered wording, and no structural evidence. Cronbach's α = .88 establishes covariation, not dimensionality — a six-item set can return .88 while being two correlated factors.
- **Acceptance criteria**: The administered items are reproduced in an appendix or supplement, changes relative to the source instrument are itemised with rationale, and a dimensionality check on the six items is reported.

#### R6 — Correct the "previously validated" claim
The abstract attaches the source instrument's validation to an adapted version whose differences are never disclosed. The domain seat's higher severity was upheld in arbitration because validation warrant in this lineage rests on factor structure and convergent–discriminant evidence, not on internal consistency, and adaptation suspends that warrant until re-established.
- **Acceptance criteria**: The abstract either describes the measure as an adaptation of a previously validated instrument with adaptation documented in Methods, or the validation claim is supported by the evidence supplied under R5.

#### R7 — Benchmark the coefficient
"Consistent with prior technology-acceptance research" is asserted in the Abstract, §5, and §7 without a single prior estimate, range, or interval appearing anywhere. As written the claim is unfalsifiable — any positive coefficient of any magnitude would satisfy it — and the paper's declared contribution is precisely comparability.
- **Acceptance criteria**: At least one prior or pooled effect-size estimate is stated with its estimand, r = .42 is located relative to it, and the paper says plainly whether .42 sits inside, above, or below that range.

#### R8 — Expand the reference base
Six sources, all 2018–2021, carry a thirty-year literature: no foundational acceptance work, nothing from the UTAUT family, nothing after 2021, and no learning-analytics work on behavioural LMS measures despite §6 depending on that literature's central finding. The post-2021 gap is substantive — baseline LMS use shifted sharply across 2020–2021, which bears on the variance available in a five-point weekly-frequency item.
- **Acceptance criteria**: §2 engages foundational acceptance-model sources, UTAUT-family work, post-2021 LMS-use studies, and learning-analytics work on behavioural measures, with each addition used to carry a specific claim rather than added as padding.

#### R9 — Declare the article type and the increment
The manuscript carries full research-article apparatus around one correlation and one robustness check, never states which article type it targets, and lets "modest," "incremental," and "one point in a distribution" perform the work a contribution statement should perform.
- **Acceptance criteria**: The manuscript states its target article type and justifies it, and states in specific terms what a reader knows after the study that they did not know before.

#### R10 — Correct the estimand
In the canonical formulation perceived usefulness predicts behavioural intention, with use downstream; the prior estimates a reader would benchmark against are largely perception-to-intention. The paper estimates a direct perception-to-use association without naming or defending the collapse, while claiming consistency with the tradition whose estimand it changed.
- **Acceptance criteria**: §2 names the omitted intention step, defends the direct path as a design choice or restates the comparison target on matching terms, and attributes the perceived-usefulness construct to its actual origin.

#### R11 — Acknowledge attenuation
A five-point ordinal outcome attenuates the observable coefficient through coarse categorisation and unmodelled item unreliability, so r = .42 is a lower bound. The Spearman check addresses monotonicity and normality but not coarseness — ρ = .40 is attenuated by the same mechanism, so it cannot be presented as retiring the measurement concern.
- **Acceptance criteria**: §3.2 or §4 states that the coefficient is attenuated by the outcome's coarseness and unreliability, §4 no longer presents ρ as addressing the measurement-level worry, and §5 qualifies the comparability claim accordingly.

#### R12 — Add confounding to the inferential limits
§2 cites context as shaping both perception and use and declares those cautions are taken seriously; §5 then frames the inferential limit as a two-way directional choice and §6's four limitations omit confounding entirely. For a two-variable correlation with no covariates, a common cause such as assessment structure is the leading rival account and the one the design cannot address at all. The §4 attribution to "course requirements and assessment schedules" is untested, uncited, and sits in Results.
- **Acceptance criteria**: §5 or §6 states confounding by a common cause as a distinct and unaddressable limitation of the two-variable design, and the §4 attribution is either supported, relocated to Discussion, or withdrawn.

#### R13 — Account for the unused log data
The study surveyed self-reported use of a system that logs every access, at the authors' institution, on the same population, in the same three-week window, cites divergence between self-report and logs, lists it as Limitation 2, and never says why logs were not obtained. Whether this was an ethics constraint, a governance refusal, an anonymity trade-off protecting the §3.3 guarantee, or a scope decision changes how much weight the coefficient can bear.
- **Acceptance criteria**: §3.3 or §6 states the specific reason log data was not obtained and why a consented validation subsample was infeasible.

#### R14 — Substantiate or withdraw the onboarding implication
The recommendation is a reasonable practitioner intuition that no value of the coefficient would change: the design cannot distinguish perception causing access, access causing perception, or assessment design driving both. Hedging it in §5 while advertising it in the Abstract is not substantiation.
- **Acceptance criteria**: The onboarding implication is removed from the Abstract, and §5 states plainly that the correlation neither supports nor tests it and reframes it as a hypothesis requiring a design study.

#### R15 — Fix the cross-site framing
Whether submission is gated through the LMS, whether instructors mandate use, whether assessment deadlines cluster, whether a mobile app exists, and course modality determine access frequency far more than perception does. None was measured, yet two are invoked interpretively in Results, and the paper positions itself as one comparable point in a cross-institutional distribution.
- **Acceptance criteria**: Either the contextual determinants are measured and reported, or the comparability and cross-site positioning in §2, §5, and §7 is narrowed to what a single uncharacterised site can support.

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---------------|--------------|----------|-----------------|------------|--------|----------|------------------|
| S1 | Report r² numerically instead of describing shared variance as "modest" | SC-25 | Minor | `text: §4 Results "The proportion of variance shared by the two measures was accordingly modest"` | 4 — reporting-convention check | Journal-Fit, DA | P2 | 0.25 day |
| S2 | Supply at least one table and the scatterplot §3.4 relies on for its assumption check | SC-26 | Minor | `absence: §4 Results and §3.4 Analysis — expected at least one table or figure, including the scatterplot cited for the linearity and outlier check; checked Abstract through §7` | 5 — direct inspection for exhibits and callouts | Journal-Fit, R1 (methodology), DA | P2 | 1 day |
| S3 | Report year-level breakdown, the use-item frequency distribution, and the full set of anchor labels | SC-27 | Minor | `text: §3.1 Design and participants "The analyzed sample of 214 students spanned all four year levels"` | 4 — standard descriptive-reporting expectation | R1 (methodology), Journal-Fit | P2 | 0.5 day |
| S4 | Reframe the power statement as post hoc sensitivity; state α once and consistently; correct the marginal .80 threshold | SC-28 | Minor | `text: §3.4 Analysis "the study had greater than .80 power to detect a correlation of r >= .19"` | 4 — routine power/sensitivity reporting | R1 (methodology), DA | P2 | 0.5 day |
| S5 | Add data and code availability statements and name the analysis software | SC-29 | Minor | `absence: §3.4 Analysis and §7 Conclusion — expected a data/code availability statement and named analysis software or package versions; checked §3.2, §3.3, §3.4, §7, References` | 4 — routine venue-reporting expectation | R1 (methodology) | P2 | 0.25 day |
| S6 | Correct the recasting of self-report divergence into a construct claim, and the Abstract's drift to "LMS engagement" | SC-30 | Minor | `text: §2 Literature Review, "studies relying on self-report capture perceived rather than actual engagement"` | 4 — familiar with how the log-comparison literature states its findings | R2 (domain), DA | P2 | 0.5 day |
| S7 | Report the LMS platform identity and where the three-week window fell in the term | SC-24 | Minor | `absence: §3.1 Design and participants — expected the LMS platform identity and the position of the three-week window in the academic term; checked Abstract, §1, §3.1–§3.4, §4, §6` | 4 — routinely assesses transfer of others' learning-analytics findings | R3 (perspective) | P2 | 0.25 day |
| S8 | Merge §6 into §5 and reduce the fourfold restatement of r = .42 | SC-31 | Minor | `text: §6 Limitations "Third, the cross-sectional design precludes any causal or temporal inference."` | 4 — structural read of section functions and overlap | Journal-Fit | P3 | 0.5 day |

### Revision Checklist

#### Priority 1 — Structural Revisions (estimated total effort: 22–33 days, excluding R1 contingency and any new data collection under R15)
- [ ] R1: Establish or replace the citation base — **blocking prerequisite for R7, R8, R10**
- [ ] R2: Report enrolment denominator and response rate
- [ ] R3: Disclose recruitment channel; assess selection on the outcome
- [ ] R4: Resolve the anonymity/deduplication contradiction on both branches
- [ ] R5: Document the instrument adaptation and report dimensionality
- [ ] R6: Correct or earn the "previously validated" claim
- [ ] R7: Benchmark r = .42 against stated prior estimates
- [ ] R8: Expand the reference base substantively
- [ ] R9: Declare the article type; state the increment
- [ ] R10: Correct the estimand and construct provenance
- [ ] R11: Acknowledge attenuation; correct the Spearman framing
- [ ] R12: Add common-cause confounding; fix the §4 attribution
- [ ] R13: Account for the unused log data
- [ ] R14: Substantiate or withdraw the onboarding implication
- [ ] R15: Measure site determinants or narrow the cross-site framing

#### Priority 2 — Content Supplementation (estimated total effort: 3–4 days)
- [ ] S1: Report r² numerically
- [ ] S2: Supply tables and the scatterplot
- [ ] S3: Report year-level breakdown, use-item distribution, full anchor labels
- [ ] S4: Reframe the power statement; fix α consistency and the .80 threshold
- [ ] S5: Add data/code availability and named software
- [ ] S6: Fix the self-report recasting and the "engagement" drift
- [ ] S7: Report platform identity and term position

#### Priority 3 — Text and Formatting (estimated total effort: 0.5 day)
- [ ] S8: Merge §6 into §5; reduce restatement of the headline coefficient

### Revision Deadline

Not applicable — this is a **Reject**, not a revise-and-resubmit. Any future submission would be handled as a new manuscript with a fresh panel. The panel's own advice on next steps, drawn from the field analysis and the Journal-Fit Reviewer's article-type judgment: R1 must be settled first, because nothing downstream is worth doing until it is; and even a fully repaired version is a **research note or short report**, not a full research article. *Research in Learning Technology* and *Journal of Information Technology Education: Research* were identified as structurally appropriate venues for that article type; the Q1 edtech venues were explicitly not recommended at this scope.

### Response Letter Template

If the authors resubmit, use `templates/revision_response_template.md` and respond to every item R1–R15 and S1–S8 individually, including items the authors decline — R4, R6, and R11 in particular are unresolved factual or claim-language questions where a stated answer is itself the deliverable.

---

### Roadmap — machine form (Schema 7)

```json
{
  "schema": 7,
  "decision": "reject",
  "items": [
    {"id": "R1", "priority": "must_fix", "reviewer": "domain", "severity": "critical", "confidence": 5, "source_kind": "finding", "evidence_anchor": "text: §References, first and last entries, \"10.5555/2050001\" and \"10.5555/2050006\"", "verification_criteria": "Every reference resolves to a locatable published record with a live DOI on a genuine registrant prefix; claims attributed to placeholder entries are re-attributed or withdrawn."},
    {"id": "R2", "priority": "must_fix", "reviewer": "methodology", "severity": "major", "confidence": 5, "source_kind": "finding", "evidence_anchor": "absence: §3.1 Design and participants — expected total eligible enrollment and a computed response rate; checked §3.1, §3.4, §6, and the abstract", "verification_criteria": "§3.1 reports total eligible undergraduate enrolment for the survey window and a computed response rate."},
    {"id": "R3", "priority": "must_fix", "reviewer": "da", "severity": "major", "confidence": 4, "source_kind": "finding", "evidence_anchor": "text: §3.1 \"distributed through the institution's course-announcement channel\" and §6 \"students who engage more with institutional channels may be overrepresented\"", "verification_criteria": "§3.1 states whether the recruitment channel is LMS-linked; §6 addresses outcome-range truncation where it is."},
    {"id": "R4", "priority": "must_fix", "reviewer": "methodology", "severity": "major", "confidence": 5, "source_kind": "finding", "evidence_anchor": "text: §3.1 and §3.3 \"5 duplicate entries were removed\" versus \"No identifying information was collected, and responses could not be linked back to individual students\"", "verification_criteria": "§3.1 states the duplicate-identification mechanism and §3.3 accurately describes retained data, with the two statements mutually consistent."},
    {"id": "R5", "priority": "must_fix", "reviewer": "methodology", "severity": "major", "confidence": 5, "source_kind": "finding", "evidence_anchor": "text: §3.2 Measures \"a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency\"", "verification_criteria": "Administered items reproduced; changes from source itemised with rationale; dimensionality check on the six items reported."},
    {"id": "R6", "priority": "must_fix", "reviewer": "domain", "severity": "major", "confidence": 4, "source_kind": "finding", "evidence_anchor": "text: Abstract \"Perceived usefulness was measured with an adapted, previously validated instrument\"", "verification_criteria": "Abstract describes the measure as an adaptation with adaptation documented in Methods, or the validation claim is supported by R5 evidence."},
    {"id": "R7", "priority": "must_fix", "reviewer": "eic", "severity": "major", "confidence": 5, "source_kind": "finding", "evidence_anchor": "absence: §2 Literature Review and §5 Discussion — expected quantitative benchmarking of r = .42 against pooled acceptance-model meta-analytic estimates; checked Abstract, §2, §4, §5, §7, References", "verification_criteria": "At least one prior or pooled estimate is stated with its estimand and r = .42 is located relative to it."},
    {"id": "R8", "priority": "must_fix", "reviewer": "eic", "severity": "major", "confidence": 5, "source_kind": "finding", "evidence_anchor": "absence: §References and §2 Literature Review — expected foundational acceptance-model sources, UTAUT-family work, post-2021 LMS-use studies, and learning-analytics work on behavioral LMS measures; checked all six reference entries, §1, §2, §6", "verification_criteria": "§2 engages foundational, UTAUT-family, post-2021, and learning-analytics literature, each carrying a specific claim."},
    {"id": "R9", "priority": "must_fix", "reviewer": "eic", "severity": "major", "confidence": 4, "source_kind": "finding", "evidence_anchor": "text: Abstract \"The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates\"", "verification_criteria": "Target article type is stated and justified, and the increment over prior knowledge is stated specifically."},
    {"id": "R10", "priority": "must_fix", "reviewer": "domain", "severity": "major", "confidence": 5, "source_kind": "finding", "evidence_anchor": "text: §2 Literature Review, \"perceived usefulness — the degree to which a person believes a technology will help them perform better\", \"is among the factors associated with adoption and continued use\"", "verification_criteria": "§2 names the omitted intention step, defends the direct path or restates the comparison target, and attributes the construct to its origin."},
    {"id": "R11", "priority": "must_fix", "reviewer": "methodology", "severity": "major", "confidence": 4, "source_kind": "finding", "evidence_anchor": "text: §4 Results \"indicating that the association did not depend on the parametric assumption\"", "verification_criteria": "Attenuation is stated in §3.2 or §4, ρ is no longer presented as addressing measurement coarseness, and §5 qualifies comparability."},
    {"id": "R12", "priority": "must_fix", "reviewer": "da", "severity": "major", "confidence": 4, "source_kind": "finding", "evidence_anchor": "text: §2 \"in shaping both perception and use\" and §5 \"the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data\"", "verification_criteria": "§5 or §6 states common-cause confounding as a distinct unaddressable limitation; the §4 attribution is supported, relocated, or withdrawn."},
    {"id": "R13", "priority": "must_fix", "reviewer": "perspective", "severity": "major", "confidence": 5, "source_kind": "finding", "evidence_anchor": "absence: §6 Limitations and §3.3 Procedure and ethics — expected a stated reason log data was unavailable or subsample validation infeasible; checked Abstract, §1, §3.1, §3.2, §3.3, §3.4, §4, §5, §6, §7", "verification_criteria": "§3.3 or §6 states the specific reason log data was not obtained and why a consented validation subsample was infeasible."},
    {"id": "R14", "priority": "must_fix", "reviewer": "perspective", "severity": "major", "confidence": 4, "source_kind": "finding", "evidence_anchor": "text: §5 \"modest support for the intuition that LMS onboarding which helps students see concrete usefulness\"", "verification_criteria": "Onboarding implication removed from the Abstract; §5 states the correlation neither supports nor tests it and reframes it as a hypothesis."},
    {"id": "R15", "priority": "must_fix", "reviewer": "perspective", "severity": "major", "confidence": 5, "source_kind": "finding", "evidence_anchor": "text: §4 \"including course requirements and assessment schedules\"", "verification_criteria": "Contextual determinants are measured and reported, or comparability and cross-site framing in §2, §5, §7 is narrowed to a single uncharacterised site."},
    {"id": "S1", "priority": "should_fix", "reviewer": "eic", "severity": "minor", "confidence": 4, "source_kind": "finding", "evidence_anchor": "text: §4 Results \"The proportion of variance shared by the two measures was accordingly modest\"", "verification_criteria": "r-squared is reported numerically in §4."},
    {"id": "S2", "priority": "should_fix", "reviewer": "eic", "severity": "minor", "confidence": 5, "source_kind": "finding", "evidence_anchor": "absence: §4 Results and §3.4 Analysis — expected at least one table or figure, including the scatterplot cited for the linearity and outlier check; checked Abstract through §7 and all section bodies", "verification_criteria": "At least one descriptive table and the scatterplot referenced in §3.4 are supplied and called out in text."},
    {"id": "S3", "priority": "should_fix", "reviewer": "methodology", "severity": "minor", "confidence": 4, "source_kind": "finding", "evidence_anchor": "text: §3.1 Design and participants \"The analyzed sample of 214 students spanned all four year levels\"", "verification_criteria": "Year-level breakdown, use-item frequency distribution, and the full set of response-option labels are reported."},
    {"id": "S4", "priority": "should_fix", "reviewer": "methodology", "severity": "minor", "confidence": 4, "source_kind": "finding", "evidence_anchor": "text: §3.4 Analysis \"the study had greater than .80 power to detect a correlation of r >= .19\"", "verification_criteria": "The statement is reframed as post hoc sensitivity, alpha is stated once consistently, and the .80 threshold is corrected."},
    {"id": "S5", "priority": "should_fix", "reviewer": "methodology", "severity": "minor", "confidence": 4, "source_kind": "finding", "evidence_anchor": "absence: §3.4 Analysis and §7 Conclusion — expected a data/code availability statement and named analysis software or package versions; checked §3.2, §3.3, §3.4, §7, and the reference list", "verification_criteria": "Data and code availability statements are present and analysis software is named with version."},
    {"id": "S6", "priority": "should_fix", "reviewer": "domain", "severity": "minor", "confidence": 4, "source_kind": "finding", "evidence_anchor": "text: §2 Literature Review, \"studies relying on self-report capture perceived rather than actual engagement\"", "verification_criteria": "§2 states self-report divergence as measurement error rather than a separate construct, and the Abstract no longer uses \"LMS engagement\" for the measured variable."},
    {"id": "S7", "priority": "should_fix", "reviewer": "perspective", "severity": "minor", "confidence": 4, "source_kind": "finding", "evidence_anchor": "absence: §3.1 Design and participants — expected the LMS platform identity and the position of the three-week window in the academic term; checked Abstract, §1, §3.1, §3.2, §3.3, §3.4, §4, §6", "verification_criteria": "§3.1 names the LMS platform and states where the three-week window fell in the academic term."},
    {"id": "S8", "priority": "nice_to_fix", "reviewer": "eic", "severity": "minor", "confidence": 4, "source_kind": "finding", "evidence_anchor": "text: §6 Limitations \"Third, the cross-sectional design precludes any causal or temporal inference.\"", "verification_criteria": "§6 is merged into §5 or the duplicated cautions are removed, and r = .42 appears in no more than two sections."}
  ]
}
```

---

## Part 3: Reviewer Report Summary (Appendix)

> These cards were produced in contract mode and emit dimension scores, not verdict recommendations. Per-report confidence is reported as the range of per-finding confidence values on that card.

### Journal-Fit Review Report Summary
- Dimensions owned: D5 = **warn**, D6 = **block** (`repairable`) | Per-finding confidence: 4–5
- Key point: fit is not in question, sufficiency is — the paper never states what r = .42 adds to a literature that already holds pooled estimates, and its modesty language performs the work a contribution statement should perform. This is a research note submitted in full-article dress.

### Reviewer 1 (Methodology) Summary
- Dimensions owned: D1 = **block** (`repairable`), D3 (co-eligible) = **warn** | Per-finding confidence: 4–5
- Key point: the analysis is the right analysis and the problems are reporting problems — but three load-bearing elements (sampling denominator, instrument adaptation, deduplication basis) are absent or self-contradictory, so a reader cannot reconstruct who was sampled, what was measured, or how n = 214 was reached.

### Reviewer 2 (Domain) Summary
- Dimensions owned: D2 = **block** (`fatal`) | Per-finding confidence: 4–5
- Key point: all six DOIs sit on a registration-agency test prefix with sequential suffixes across six distinct journals, and every substantive domain claim routes through them; separately, the paper collapses the intention step without acknowledgement and asserts consistency with a literature it never quantifies.

### Reviewer 3 (Perspective / Practitioner) Summary
- Dimensions owned: D4 = **warn** | Per-finding confidence: 4–5
- Key point: the paper is legible and honestly hedged, but its only claim on practice — the onboarding implication — survives every possible value of the coefficient, and the two facts needed for transfer (platform identity, term position) are absent while behavioural log data sat on the same server for the same population and window.

### Devil's Advocate Summary
- Dimensions owned: D3 = **warn** | CRITICAL band **empty by finding** | Per-finding confidence: 4–5
- Key point: the P3→C1 link holds and the numbers reconcile (Fisher-z reproduces the reported interval), so no singleton defect invalidates the central claim; the defects are in the paper's framing of its own warrant — possible selection on the dependent variable, an unfalsifiable consistency claim, omitted common-cause confounding, and a Methods pair that cannot both be true.
