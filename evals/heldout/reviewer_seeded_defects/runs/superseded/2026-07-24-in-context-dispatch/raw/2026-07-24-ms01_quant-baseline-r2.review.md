# Editorial Peer Review — Full Mode

**Manuscript**: "Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment"
**Skill**: `academic-paper-reviewer` v1.10.0, `full` mode (5-seat panel + v3.6.2 sprint-contract two-phase protocol)
**Review Round**: 1
**Cross-model track**: not active for this session (`ARS_CROSS_MODEL` unset) — single model family; correlated-error caveat applies (disclosed in the Review Panel Provenance block of the Editorial Decision Letter).

---

# Part A — Field Analyst Reviewer Configuration

# Field Analysis Report

## Paper Basic Information
- **Title**: Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment
- **Abstract length**: ~150 words
- **Full text length**: ~2,400 words (excluding references)
- **Number of references**: 18 (reference list); ~9 cited in text

## Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| Primary Discipline | Higher education — learning analytics / educational technology |
| Secondary Disciplines | Educational psychology (self-regulated learning); educational measurement / applied statistics; research ethics (student-data governance) |
| Research Paradigm | Quantitative Research |
| Methodology Type | Observational, cross-sectional; LMS behavioral-log analysis + single-item self-report survey; correlation + independent-samples *t*-tests |
| Target Journal Tier | Q2–Q3. Ambition (single-course, cross-sectional, N=142, single-item DV) is modest; cited venues are plausible field-level journals. The topic is timely (Q1 venues exist), but the design and reporting cap realistic placement at a mid-tier ed-tech / higher-education outlet. |
| Paper Maturity | Revised draft. Structure is complete (IMRaD present, two tables, reference list), language is publication-grade, but the empirical core carries internal contradictions that a pre-submission draft should not — so it sits below "pre-submission." |

## Recommended Target Journals (Top 3)
1. *The Internet and Higher Education* (Elsevier) — online-learning / dashboard focus; expects an outcome measure, not adoption metrics. The paper aims here but currently under-delivers on causal-claim discipline.
2. *British Journal of Educational Technology* (Wiley) — balances theory and practice; would accept a correlational learning-analytics study **if** the claims match the design.
3. *International Journal of Educational Technology in Higher Education* ([publisher], OA, Q1) — strong ed-tech-in-HE fit; the SRL framing is on-topic, but this venue's methods bar is higher than the current statistics can clear.

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC
**Identity Description**: Editor-in-Chief of a mid-to-upper-tier learning-analytics / educational-technology journal (calibrated to *The Internet and Higher Education* / *British Journal of Educational Technology*), whose readership is instructional designers, LA researchers, and institutional-effectiveness staff. Has handled many "dashboard-and-outcomes" submissions and is acutely alert to the field's documented gap between enthusiasm and evidence.
**Review Focus**:
  1. Journal fit and whether the paper delivers an *outcome* result (retention) rather than adoption/satisfaction metrics.
  2. Whether the abstract, results, discussion, and conclusion tell one internally consistent story — especially whether headline numbers match the body.
  3. Whether the contribution justifies a slot, given a single-course cross-sectional design.
**Will particularly care about**: Over-promising. Whether "association" in the design silently becomes "lever / raises / dependable strategy" by the conclusion — a pattern this editor has rejected repeatedly.
**Possible blind spots**: Will not re-derive the statistics line-by-line (that is R1); may under-weight the literature-representation error (that is R2).

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1 — Methodology
**Identity Description**: Quantitative educational-measurement researcher with an applied-statistics background, specializing in observational LMS-trace-data studies and the reproducibility of learning-analytics findings. Routinely reviews for APA 7.0 statistical-reporting compliance and teaches research design.
**Review Focus**:
  1. Internal numerical consistency: do the reported statistics (*r*, *t*, *df*, *p*, *N*) agree across abstract, methods, results, and tables?
  2. Statistical-reporting adequacy: effect sizes, CIs, power, assumption testing, correct test choice for a dichotomous outcome.
  3. Design validity: selection bias, confounding, and whether the analysis supports any causal reading.
**Will particularly care about**: Whether the *t* / *df* / *p* triples are arithmetically possible, and whether "Pearson correlation" is the right tool for a dichotomous retention variable.
**Possible blind spots**: May treat the causal-language problem as purely a statistics issue and under-state its argument-level and domain-level reach (covered by DA and EIC).

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2 — Domain
**Identity Description**: Senior learning-analytics scholar working in the self-regulated-learning (SRL) tradition, familiar with the dashboard-effectiveness literature, the equity/demotivation debate, and the measurement critique of click-based engagement proxies. Knows the primary sources on peer-comparison feedback.
**Review Focus**:
  1. Whether cited works are represented accurately (does a citation support what the text claims it supports?).
  2. Literature-coverage integrity: are in-text claims sourced, and are listed references actually used?
  3. Whether the SRL framework is genuinely applied or merely named.
**Will particularly care about**: Citation–claim fidelity — specifically whether a source titled around *demotivation* is cited to support *reliable improvement*. Terminology precision around "engagement."
**Possible blind spots**: Will not audit the *t*-test arithmetic (R1) or the cross-disciplinary/ethics angle (R3).

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3 — Cross-disciplinary / Practical
**Identity Description**: Research-ethics and student-data-governance scholar with a secondary footing in institutional policy and program evaluation — the "outsider" who reads a learning-analytics paper for consent, equity, and deployment feasibility rather than for its *p*-values.
**Review Focus**:
  1. Consent / data-governance: the undisclosed secondary use of behavioral-log data (§3.2).
  2. Deployment realism: whether "encourage students to engage with dashboards → retention at scale" survives contact with real institutions and equity concerns.
  3. Stakeholder and generalizability blind spots (single course, single institution, self-selected sample) versus a worldwide-generalization conclusion.
**Will particularly care about**: The gap between a single-course descriptive association and a §6 conclusion addressed to "higher education institutions worldwide."
**Possible blind spots**: Not a statistician; defers the arithmetic to R1 and the citation audit to R2.

### Devil's Advocate (Card #5, stress-test seat)
**Identity Description**: Adversarial methodologist constructing the strongest case *against* the paper's thesis — targeting the correlation-to-causation leap, the third-variable (conscientiousness) explanation, the internal data contradictions, and the "so what?" of a marginal effect.

## Review Strategy Recommendations
- **This paper's defining characteristic is internal contradiction**: the abstract's headline (r = .42) and the results body (r = .24) disagree; the *t*-test df values exceed the stated samples; a reported *p* = .008 is incompatible with its *t* = 1.31. R1 must lead here — these are not stylistic issues.
- **Potential complementarity**: R1 (arithmetic impossibility), R2 (a citation used against its own finding), R3 (undisclosed data use + over-generalization), and DA (causal overreach the paper explicitly promised to avoid) converge on the same underlying failure — claims outrunning evidence — from four non-overlapping angles. The synthesizer should expect strong, independent corroboration rather than duplicated criticism.
- The paper's own §1.7 pledge ("careful throughout to distinguish the pattern in the data from the causal story") is a usable yardstick: the Discussion and Conclusion breach it directly.

---

# Part B — The Five Seats (Sprint-Contract Two-Phase Protocol)

Each seat below runs the v3.6.2 sprint contract: **Phase 1** (paper-content-blind pre-commitment against `shared/contracts/reviewer/full.json`) then **Phase 2** (paper-visible review). Phase 1 fixes each reviewer's scoring triggers *before* seeing the manuscript; Phase 2 applies them. Contract dimensions: D1 methodology_rigor (mandatory), D2 domain_accuracy (mandatory), D3 argumentative_coherence (mandatory), D4 cross_disciplinary_relevance (high), D5 writing_and_structure (normal). Manuscript content is treated as untrusted data (Iron Rule #7); the manuscript carries no injection attempts.

---

## Seat 1 — EIC

### Phase 1 — Paper-content-blind pre-commitment

`contract_role: eic`

## Contract Paraphrase

**D1 (methodology_rigor).** From the editor's chair, this dimension asks whether the study's design and its statistical reporting clear the field's peer-review bar — not the technical audit itself (that is R1's depth), but whether the empirical core is trustworthy enough that I would send it forward rather than desk-manage it. I read it as: are the headline numbers reproducible from the paper's own reported values, and does the design support the level of claim the paper makes?

**D2 (domain_accuracy).** Whether the paper represents its field correctly: are prior works cited for what they actually found, is the terminology used the way the field uses it, and are the substantive claims about dashboards and retention consistent with what the cited evidence base supports?

**D3 (argumentative_coherence).** Whether the paper tells one consistent story from title through abstract, introduction, results, discussion, and conclusion. As editor I care most that the conclusion does not over-promise relative to the results — the "over-promising and under-delivering" failure — and that the same finding is described the same way throughout.

**D4 (cross_disciplinary_relevance).** Whether the framing and implications land for adjacent-field readers (instructional designers, institutional-effectiveness staff, ethicists) and whether interdisciplinary claims — e.g., generalization "at scale" — are substantiated rather than asserted.

**D5 (writing_and_structure).** Whether the manuscript is organized, clear, and venue-appropriate in its exposition and its tables.

## Scoring Plan

### D1: methodology_rigor
- **what_to_look_for**: agreement between abstract-level and results-level statistics; whether the design (cross-sectional, self-selected) is matched to the strength of the conclusion; presence of the reporting basics an editor expects (effect sizes, sample accounting).
- **what_triggers_block**: a headline statistic that contradicts the body, OR a design that cannot support the paper's central claim as stated.
- **what_triggers_warn**: reporting gaps (missing effect sizes/CIs/power) that are fixable but currently below bar, with the core numbers internally consistent.

### D2: domain_accuracy
- **what_to_look_for**: whether cited sources are used to support claims consistent with those sources; correct use of field terms.
- **what_triggers_block**: a citation deployed to support the opposite of what that source found, OR a substantive factual misrepresentation of the evidence base.
- **what_triggers_warn**: thin or imprecise sourcing that does not rise to misrepresentation.

### D3: argumentative_coherence
- **what_to_look_for**: consistency of the central claim across sections; whether the conclusion's strength matches the results' strength.
- **what_triggers_block**: the conclusion asserts a categorically stronger claim (causal / "lever" / "dependable strategy") than the correlational results license, especially if the paper elsewhere disclaims that very move.
- **what_triggers_warn**: local coherence slips that do not overturn the main claim.

### D4: cross_disciplinary_relevance
- **what_to_look_for**: whether adjacent-field implications (policy, ethics, equity) are substantiated; whether generalization claims are bounded to the study's scope.
- **what_triggers_block**: an interdisciplinary/scale claim wholly unsupported by the single-site design.
- **what_triggers_warn**: implications gestured at but under-substantiated.

### D5: writing_and_structure
- **what_to_look_for**: IMRaD completeness, table quality, clarity.
- **what_triggers_block**: exposition so disorganized the paper is unreviewable.
- **what_triggers_warn**: prose fine but tables/results under-specified.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 — Paper-visible review

`contract_role: eic`

## Dimension Scores

### D1: methodology_rigor
score: block

### D2: domain_accuracy
score: warn

### D3: argumentative_coherence
score: block

### D4: cross_disciplinary_relevance
score: warn

### D5: writing_and_structure
score: pass

## Failure Condition Checks

### F1
fired: true

### F2
fired: true

### F3
fired: false

### F0
fired: false

## Review Body

This is a topical study on a question the field genuinely needs answered — whether dashboard engagement translates into a downstream outcome (retention) rather than adoption or satisfaction. The writing is clean and the structure is complete. But two editor-level problems make the manuscript unpublishable in its current form.

First, the paper does not tell one story. The abstract reports the central association as *r* = .42; the Results (§4.2) report it as *r* = .24, *p* = .004. These cannot both be the headline finding, and the discrepancy is not a typo I can wave through — it is the paper's primary result. An editor cannot forward a manuscript whose main number changes between the abstract and the results.

Second, the conclusion over-promises far beyond the design. §1.7 explicitly commits the authors to "distinguish the pattern in the data from the causal story," yet §5 states dashboard engagement "improved course retention" and "raises the probability that a student completes the course," and §6 calls dashboards "a dependable strategy" and "a practical and generalizable lever ... at scale" for "higher education institutions worldwide." From a single-course, cross-sectional, self-selected sample with a modest correlation, that is precisely the over-claiming the field is trying to leave behind — and the paper indicts itself by promising not to do it.

D1 scores `block` (headline statistic contradicts the body). D3 scores `block` (conclusion asserts a causal/at-scale claim the correlational design cannot license, against the paper's own stated discipline). D2 scores `warn` (the Ferro & Nakamura representation looks wrong to me, but I defer the citation audit to R2). D4 `warn` (scale/worldwide claims unsubstantiated). D5 `pass`.

## Editorial Decision
editorial_decision=reject_or_major_revision

---

### EIC Review Report (full narrative)

#### Reviewer Identity
Editor-in-Chief, mid-to-upper-tier learning-analytics / educational-technology journal (calibrated to *The Internet and Higher Education* / *British Journal of Educational Technology*).

#### Overall Recommendation
Major Revision (the contract's `reject_or_major_revision` action, resolved toward Major Revision because the flaws are fixable — see Editorial Decision Letter).

#### Confidence Score
4 — High confidence. Journal-fit, coherence, and over-claiming are squarely within an editor's remit; I defer the statistical arithmetic to R1 and the citation audit to R2.

#### Summary Assessment
The paper asks a worthwhile, timely question — does dashboard *engagement* predict *retention*, an outcome the dashboard literature too often skips in favor of adoption metrics — and it pairs behavioral logs with a self-report of perceived control, which is a sensible design in outline. The writing is publication-grade and the structure is complete. However, the manuscript fails at the editor's level on two counts. The central association is reported as *r* = .42 in the abstract but *r* = .24 in the results, so the paper's headline number is not stable. And the conclusion escalates a modest correlation into causal, prescriptive, worldwide-scale claims that the cross-sectional single-course design cannot support — directly contradicting the authors' own §1.7 promise to keep pattern and cause separate. Either failure alone would warrant Major Revision; together they require re-analysis and a wholesale re-scoping of the claims. The contribution is salvageable, but not in this draft.

#### Strengths
1. **Outcome-focused question**: The paper targets retention, a real downstream outcome, rather than the adoption/satisfaction proxies §1 rightly criticizes ("Much of the published work reports adoption metrics or student satisfaction rather than downstream academic outcomes"). That framing is the paper's best asset.
2. **Mixed behavioral + self-report design**: Combining LMS logs with a perceived-control item to connect behavior to the SRL mechanism (§1) is a reasonable way to ask not just *whether* engagement and retention co-move but *whether* the regulatory experience the theory predicts is present.
3. **Self-aware literature framing**: §2 and §1.7 correctly identify the field's causal-overreach problem and the weakness of click-based proxies (Vandermeer, 2023), showing the authors know where the landmines are — which makes the Discussion's missteps more surprising than excusable.

#### Weaknesses
1. **Headline statistic is unstable across the manuscript**
   - **Problem**: Abstract: "Dashboard engagement correlated positively with retention (r = .42)"; §4.2: "positively associated with course retention (r = .24, p = .004)." The primary result differs between the two most-read sections.
   - **Why it matters**: The abstract is the paper's public claim; a reader cannot tell which number is real. This is a `block`-level coherence and integrity failure, not a formatting nit.
   - **Suggestion**: Report one verified value everywhere, recomputed from the data, with its effect-size interpretation and CI. Reconcile every downstream sentence to it.
2. **Conclusion over-promises relative to the design**
   - **Problem**: §5/§6 move from "associated" to "improved," "raises the probability," "dependable strategy," "generalizable lever ... at scale," "institutions worldwide" — all from one cross-sectional course.
   - **Why it matters**: This is the exact over-claiming the paper criticizes in others (Ibarra, 2023, is cited approvingly in §2) and pledges to avoid (§1.7). It is a credibility-ending move at review.
   - **Suggestion**: Re-scope all causal/prescriptive language to associational, single-site, exploratory claims; delete "worldwide / at scale / dependable."
3. **Contribution is thin for the strength of the claims made**
   - **Problem**: A single course, N=142, one institution, single-item DV — yet the framing implies a general institutional lever.
   - **Why it matters**: Even fully corrected, the study is a modest local association; the paper must position it as such.
   - **Suggestion**: Frame as preliminary/hypothesis-generating; state the effect size honestly and let it be small.

#### Detailed Comments

**Journal Fit**: On topic for a learning-analytics / ed-tech-in-HE venue *if* the claims are brought back in line with the design. As written, no reputable venue in this space would accept the causal framing.

**Originality**: Incremental. The engagement→retention association is plausible and worth reporting, but it is not novel enough to carry over-stated conclusions; its value is in careful, bounded reporting.

**Significance**: Potentially useful to practitioners *if* correctly scoped. At the current claim strength the significance is illusory — it rests on a causal inference the data cannot support.

**Structural Coherence**: The Title→Abstract→Introduction→Conclusion chain breaks in two places: the abstract's *r* = .42 vs. the results' *r* = .24, and the §1.7 "we distinguish pattern from cause" promise vs. the §5/§6 causal conclusion. Fix both and the spine holds.

**Title & Abstract**: The title ("Dashboard Engagement and Course Retention") is appropriately associational; the abstract undoes that discipline with "increasing dashboard engagement is a promising lever." Align the abstract to the title's restraint.

**Conclusion**: §6 is the weakest section. It asserts causation ("raises course retention"), dependability, and worldwide generalizability in three sentences. It must be rewritten from scratch around the actual (corrected, modest) association.

#### Questions for Authors
1. Which is the correct primary association — *r* = .42 or *r* = .24 — and can you show it recomputed from the raw data with its effect size and 95% CI?
2. Given a cross-sectional design and a self-selected sample, on what basis does §5 claim engagement "improved"/"raises" retention rather than merely co-varies with it?
3. What is the retention base rate in the analytic sample, and how does that shape the interpretation of the association?

#### Minor Issues
- Perceived-control mean reported to three decimals ("3.847") while its SD is two ("0.62") — inconsistent precision.
- "Several hundred students" (§3.1) vs. "142 students" (analytic sample) — clarify the enrolment-to-analysis funnel.

---

## Seat 2 — Peer Reviewer 1 (Methodology)

### Phase 1 — Paper-content-blind pre-commitment

`contract_role: methodology`

## Contract Paraphrase

**D1 (methodology_rigor).** This is my core dimension. It asks whether the design answers the question, whether the statistics are correctly chosen and correctly reported (APA 7.0: effect sizes, CIs, power, assumption tests), and — most basically — whether the reported numbers are arithmetically self-consistent. A study whose *t*/*df*/*p* triples are internally impossible has failed this dimension regardless of anything else.

**D2 (domain_accuracy).** From a methods seat, I read this as whether the statistical and measurement claims match domain evidence — e.g., whether a click-count "engagement" measure is treated with the caution the field's own measurement critique demands, and whether the analysis of a dichotomous outcome uses the right tool.

**D3 (argumentative_coherence).** Whether the inferential chain holds: does a correlation get reported as a correlation, or does it silently become a causal claim? Coherence, for me, is whether the conclusions stay inside the envelope the analysis defines.

**D4 (cross_disciplinary_relevance).** Whether generalization claims are statistically warranted by the sampling frame — a methods reviewer's version of external validity.

**D5 (writing_and_structure).** Whether results are reported precisely enough (tables, exact statistics) to be checkable and reproducible.

## Scoring Plan

### D1: methodology_rigor
- **what_to_look_for**: internal consistency of every reported *N*, *df*, *t*, *r*, *p*; correct test for the outcome's measurement level; effect sizes, CIs, power analysis, assumption tests; sample-accounting (who is in each analysis).
- **what_triggers_block**: any arithmetically impossible or mutually contradictory statistic (e.g., *df* implying a sample larger than exists; a *p*-value incompatible with its test statistic; a headline *r* that differs between sections), OR a test fundamentally mismatched to the data.
- **what_triggers_warn**: complete-but-substandard reporting — missing effect sizes/CIs/power/assumption tests — where the reported numbers are at least internally consistent.

### D2: domain_accuracy
- **what_to_look_for**: whether the engagement proxy is caveated per the field's measurement critique; correct outcome-variable treatment.
- **what_triggers_block**: a measurement or analytic claim that contradicts an established methodological fact of the subfield.
- **what_triggers_warn**: proxy used with insufficient caveat but not misrepresented.

### D3: argumentative_coherence
- **what_to_look_for**: correlation reported as correlation; conclusions bounded by design.
- **what_triggers_block**: causal conclusions drawn from cross-sectional correlational data without identification strategy.
- **what_triggers_warn**: occasional loose inferential wording not central to the conclusion.

### D4: cross_disciplinary_relevance
- **what_to_look_for**: generalization bounded to the sampling frame.
- **what_triggers_block**: population-scale generalization from a single self-selected course sample stated as fact.
- **what_triggers_warn**: under-bounded but non-load-bearing generalization.

### D5: writing_and_structure
- **what_to_look_for**: exact statistics, table–text agreement, reproducible reporting.
- **what_triggers_block**: results unreportable/uncheckable.
- **what_triggers_warn**: table–text mismatches or under-specified reporting.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 — Paper-visible review

`contract_role: methodology`

## Dimension Scores

### D1: methodology_rigor
score: block

### D2: domain_accuracy
score: warn

### D3: argumentative_coherence
score: block

### D4: cross_disciplinary_relevance
score: warn

### D5: writing_and_structure
score: warn

## Failure Condition Checks

### F1
fired: true

### F2
fired: true

### F3
fired: false

### F0
fired: false

## Review Body

The statistics in this manuscript do not survive an internal-consistency check, and several reported values are arithmetically impossible. This is a `block` on D1 before any question of effect sizes or power even arises.

1. **Headline correlation contradicts itself.** Abstract: *r* = .42. §4.2: *r* = .24, *p* = .004. Same association, two different values.

2. **Perceived-control group comparison has an impossible df.** §4.3 reports *t*(156) = 3.02 for high- vs. low-engagement perceived control. *df* = 156 implies *n* ≈ 158 in that comparison. But only 87 respondents answered the perceived-control item (§4.1), and the entire analytic sample is 142 (§3.2). The comparison cannot have more cases than the sample it is drawn from. The number is not reproducible.

3. **Exam-comparison *p*-value is incompatible with its *t*.** §4.3: *t*(140) = 1.31, *p* = .008, and the text calls the difference "small." For *df* = 140, *t* = 1.31 gives a two-tailed *p* ≈ .19 — non-significant. A *p* of .008 would require *t* ≈ 2.6. The reported *t*, *p*, and verbal description are mutually inconsistent. Separately, §4.3 says "All 142 students ... were classified into engagement groups," but Table 2 sums to 66 + 61 = 127. Both the *N* and the significance are wrong somewhere.

4. **Wrong test for a dichotomous outcome.** §3.3 codes retention dichotomously (retained / not). §4.2 then reports a "Pearson correlation" between engagement and retention. A Pearson *r* with a dichotomous variable is a point-biserial correlation and should be labeled and computed as such; more importantly, the retention base rate is never reported, so the association is uninterpretable.

5. **APA 7.0 reporting is inadequate throughout.** No effect sizes for either *t*-test (Cohen's *d* is mandatory under APA 7.0); no confidence intervals anywhere; no a-priori power analysis; no assumption testing (normality, homogeneity of variance — §4.1 states engagement is right-skewed, which bears directly on the *t*-test but is never addressed); missing-data handling for the perceived-control item is "excluded" with no MCAR/MAR discussion. The median-split (§3.3) discards information and is acknowledged as "coarse" but retained.

6. **Causal inference from cross-sectional data (Reverse Causation / confounding).** §5 states engagement "improved" and "raises" retention; the design is cross-sectional and correlational with no identification strategy. This is the textbook reverse-causation / omitted-variable fallacy — a `block` on D3.

Methodological fallacies detected: **Reverse Causation** (cross-sectional data → causal claim), **Survivorship / Selection Bias** (voluntary respondents; withdrawn students under-represented in a retention study), **Endogeneity** (conscientiousness/motivation as an omitted common cause of both engagement and retention), and internal-inconsistency red flags (df > N; *p* incompatible with *t*; *N* mismatch text vs. table).

D1 `block` (multiple impossible/contradictory statistics). D3 `block` (causal claim from cross-sectional data). D2 `warn` (engagement proxy under-caveated; wrong-test issue). D4 `warn` (generalization not bounded to the frame). D5 `warn` (table–text *N* mismatch; false-precision mean).

## Editorial Decision
editorial_decision=reject_or_major_revision

---

### Methodology Review Report (Peer Reviewer 1) (full narrative)

#### Reviewer Identity
Quantitative educational-measurement researcher, applied-statistics background; specializes in observational LMS-trace-data studies and reproducibility in learning analytics.

#### Overall Recommendation
Major Revision (contract action `reject_or_major_revision`; the errors are fixable in principle via re-analysis, so not an outright Reject — but re-analysis is mandatory, and if the corrected numbers dissolve the association, Reject follows).

#### Confidence Score
5 — The findings here are arithmetic and definitional; they are fully within my expertise and do not depend on domain judgment.

#### Summary Assessment
This is an observational, cross-sectional study relating a click-based dashboard-engagement proxy to dichotomous course retention (N = 142) plus a single-item perceived-control survey. Methodologically it cannot be accepted, for reasons that are independent of taste: the reported statistics are internally contradictory and in places arithmetically impossible. The headline correlation is *r* = .42 in the abstract and *r* = .24 in the results; a *t*-test reports *df* = 156 in a sample of at most 142 (and only 87 answered the relevant item); another *t*-test reports *t*(140) = 1.31 with *p* = .008, which is incompatible (*p* ≈ .19). Beyond consistency, the study omits every modern reporting requirement — effect sizes, CIs, power, assumption tests — and draws causal conclusions from correlational data. The core association may or may not survive a correct re-analysis; as reported, none of the numbers can be trusted. Major Revision contingent on a complete, reproducible re-analysis.

#### Strengths
1. **Sessionization defined**: §3.3 defines a dashboard session operationally (a view preceded by ≥30 min inactivity, per the platform default). Explicit, reproducible operationalization is good practice and rare in this literature.
2. **Skew acknowledged**: §4.1 reports engagement is right-skewed with a heavy tail — the correct observation to make; it simply must then flow into the analysis (it does not).
3. **Median-split honestly flagged**: §3.3 concedes the median split is "a coarse simplification ... adopted for interpretability rather than statistical efficiency." Naming the weakness is the right instinct; the fix is to model engagement continuously.

#### Weaknesses
1. **Arithmetically impossible / contradictory statistics** (Severity: Critical)
   - **Problem**: (a) *r* = .42 (abstract) vs. *r* = .24 (§4.2); (b) *t*(156) with *n*≤142 and item-*n*=87 (§4.3); (c) *t*(140) = 1.31 with *p* = .008 when *p* ≈ .19 (§4.3); (d) "all 142 ... classified" vs. Table 2 summing to 127.
   - **Why it matters**: These are not reporting-style issues; they mean the results as printed cannot be reproduced from any single dataset. The paper's evidentiary core is unverifiable.
   - **Suggestion**: Re-run every analysis from the raw data; report each statistic once, consistently, with *N* stated per analysis; reconcile text, abstract, and tables.
2. **Missing effect sizes, CIs, power, and assumption tests** (Severity: Major)
   - **Problem**: No Cohen's *d* for either *t*-test; no CIs; no power analysis; no normality/variance-homogeneity tests despite acknowledged skew (§4.1).
   - **Why it matters**: APA 7.0 mandates effect sizes; without them (and CIs) the "modest but reliable" framing is unsupported, and the skew directly threatens the *t*-test's validity.
   - **Suggestion**: Report *d* with 95% CI for each comparison; conduct and report assumption tests or use rank-based / robust alternatives; add a sensitivity/power statement.
3. **Wrong correlation type; missing base rate** (Severity: Major)
   - **Problem**: "Pearson correlation" between engagement and a dichotomous retention variable (§4.2) is a point-biserial correlation; the retention base rate is never reported.
   - **Why it matters**: Mislabeling aside, without the base rate the association cannot be interpreted (an *r* with a rare or near-universal outcome behaves very differently). A logistic regression is the appropriate model.
   - **Suggestion**: Report retention base rate; model retention with logistic regression (OR, 95% CI); if keeping the correlation, label it point-biserial.
4. **Causal inference from cross-sectional data** (Severity: Critical)
   - **Problem**: §5: engagement "improved" retention and "raises the probability" of completion; the design is cross-sectional and correlational.
   - **Why it matters**: No temporal ordering, no identification strategy, obvious confounders (conscientiousness) — the causal claim is unsupported and reverses the paper's own §1.7 commitment.
   - **Suggestion**: Restrict all wording to association; if a causal claim is wanted, it needs a different design (longitudinal, quasi-experimental with a plausible instrument or matching).

#### Detailed Comments

**Research Questions & Hypotheses**: RQ (§1.3, does engagement predict persistence) is clear and answerable in associational form; no formal hypotheses stated, acceptable for an exploratory design.

**Research Design**: Cross-sectional observational; appropriate for description, not for the causal conclusion drawn. The internal/external-validity trade-off is never discussed.

**Sampling Strategy**: §3.2 is internally contradictory — it claims a "random sample of students enrolled" but then describes a *voluntary* mid-term survey ("students who chose to respond ... formed the study sample"). Volunteer response is not random sampling. Selection bias is unaddressed and, in a retention study, is severe: students who withdraw are least likely to answer a mid-term survey, biasing the sample toward the retained.

**Data Collection**: Log-based engagement and a single-item survey; sessionization is well-specified. The single-item DV for perceived control limits reliability.

**Analysis Methods**: Pearson correlation (should be point-biserial/logistic for a dichotomous outcome); independent *t*-tests without effect sizes, CIs, assumption tests, or multiple-comparison awareness. Median split discards information.

**Results Presentation**: The central defects live here — see Weakness 1. Table 2's *N* (127) contradicts the text (142). Table 1 reports a final-exam mean (71.3) but the exam is not part of the stated design until §4.3.

**Reproducibility**: No data/code availability statement; no ethics-review record (see R3). Given the internal contradictions, the results are currently non-reproducible on their face.

**Methodological Fallacies Detected**: Reverse Causation; Selection/Survivorship Bias; Endogeneity (omitted common cause); plus internal-inconsistency red flags (df > N; *p*≠*t*; text–table *N* mismatch).

#### Questions for Authors
1. Provide the raw *N* per analysis and recompute *r*, both *t*-tests, all *df*, and all *p*-values; explain each current discrepancy (r=.42/.24; df=156; p=.008 with t=1.31; 142 vs. 127).
2. Was the sample randomly drawn or self-selected via a voluntary survey? These are described inconsistently in §3.2 and imply very different bias profiles.
3. What is the retention base rate, and will you re-model retention with logistic regression?
4. How were the skewed engagement distribution and the *t*-test normality/variance assumptions handled?

#### Minor Issues
- **Language/Numbers**: "3.847" (3 dp) vs. "SD = 0.62" (2 dp) — standardize to 2 dp; report *p* exactly and in APA form.
- **Tables**: Table 2 header/rows should state the group *n*s that reconcile to the analytic sample; Table 1 should note which sample each row is computed on.
- **APA format**: statistics should be italicized (*r*, *t*, *p*, *M*, *SD*, *N*); *p* = .008 not "p = .008".

---

## Seat 3 — Peer Reviewer 2 (Domain)

### Phase 1 — Paper-content-blind pre-commitment

`contract_role: domain`

## Contract Paraphrase

**D1 (methodology_rigor).** From the domain seat I read this as whether the study's design and measures reflect the field's accepted practice for dashboard-effectiveness research — in particular whether a click-based engagement proxy is handled with the caution the subfield's own measurement literature requires. The statistical audit itself I leave to R1.

**D2 (domain_accuracy).** My core dimension. Whether cited works are represented for what they actually found, whether the SRL theoretical framework is applied rather than name-dropped, whether the field's key debates (equity/demotivation) are engaged accurately, and whether every in-text claim is sourced and every listed reference is used.

**D3 (argumentative_coherence).** Whether the paper's argument about *who benefits from dashboards* coheres with the evidence it cites — e.g., whether it cites a demotivation finding as if it were an improvement finding.

**D4 (cross_disciplinary_relevance).** Whether the SRL framing translates for adjacent-field readers and whether interdisciplinary claims about mechanism (perceived control as mediator) are substantiated in the domain literature.

**D5 (writing_and_structure).** Whether the literature review is organized as critical synthesis rather than an enumerated list.

## Scoring Plan

### D1: methodology_rigor
- **what_to_look_for**: engagement proxy caveated per the field's measurement critique; design consistent with dashboard-effectiveness norms.
- **what_triggers_block**: a design/measurement claim that contradicts a settled methodological fact of the subfield.
- **what_triggers_warn**: proxy or design under-caveated but not contradicting the field.

### D2: domain_accuracy
- **what_to_look_for**: citation–claim fidelity (does the source support the sentence it is attached to?); framework applied vs. named; accurate engagement with the equity/demotivation debate; in-text claims sourced; listed references actually cited.
- **what_triggers_block**: a citation used to support the *opposite* of what that source found (a misrepresentation of the evidence base), OR a substantive factual error about the field.
- **what_triggers_warn**: thin sourcing, uncited listed references, or framework named-but-shallow, short of misrepresentation.

### D3: argumentative_coherence
- **what_to_look_for**: the "who benefits" argument consistent with the cited evidence.
- **what_triggers_block**: the central domain argument built on a mis-cited source such that it collapses if the citation is read correctly.
- **what_triggers_warn**: local incoherence not fatal to the domain argument.

### D4: cross_disciplinary_relevance
- **what_to_look_for**: SRL mechanism claims substantiated.
- **what_triggers_block**: a mechanism claim contradicted by the domain literature.
- **what_triggers_warn**: mechanism asserted with thin support.

### D5: writing_and_structure
- **what_to_look_for**: critical synthesis vs. enumeration in §2.
- **what_triggers_block**: no discernible literature organization.
- **what_triggers_warn**: mostly synthesis with some enumeration / padding.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 — Paper-visible review

`contract_role: domain`

## Dimension Scores

### D1: methodology_rigor
score: warn

### D2: domain_accuracy
score: block

### D3: argumentative_coherence
score: warn

### D4: cross_disciplinary_relevance
score: warn

### D5: writing_and_structure
score: warn

## Failure Condition Checks

### F1
fired: true

### F2
fired: true

### F3
fired: false

### F0
fired: false

## Review Body

The paper's domain problem is a citation used against its own source. §2 states: "Dashboards have been shown to reliably improve outcomes for lower-achieving students, who are said to gain the most from externalized progress cues (Ferro & Nakamura, 2021)." But the reference list gives Ferro & Nakamura (2021) as *"When dashboards demotivate: Peer comparison and the lower-achieving student."* A paper with that title is, on its face, about dashboards *harming* — not "reliably improving" — outcomes for lower-achieving students. The manuscript cites a demotivation finding as if it were a reliable-improvement finding, and then builds the "equity-oriented rationale for institutional dashboard deployment" on it and promises to "return to it in the Discussion." This is a misrepresentation of the evidence base, and because a load-bearing domain claim rests on it, D2 scores `block`.

This is compounded by a second-order problem: §5's Discussion claims the results "align with the view that externalized progress cues can support persistence" — an alignment asserted against the very (mis-read) source. If Ferro & Nakamura in fact document demotivation, the paper's finding would *complicate*, not confirm, that literature, and the whole "who benefits" argument (§2, §5) needs re-writing.

Field-norm grounding for the severity (Domain Step 5 / #215): the norm I am invoking is citation–claim fidelity — a source must be represented for what it reports. This is not a discipline-specific "best practice" I am asserting from model knowledge; it is a universal scholarly-integrity standard (COPE guidance on citation integrity; APA 7.0 §8 on accurate source representation), so the severity is grounded, not `[FIELD-NORM UNVERIFIED]`.

Separately, reference-list integrity is weak: of 18 listed references, roughly nine are never cited in the text (Ainsworth & Devi 2018; Berange 2021; Delacroix & Ohno 2022; Halloran 2020; Kessler & Amadou 2019; Montez 2022; Prakash & Tolliver 2021; Solberg & Whitfield 2018; Wexler & Ojo 2020). A padded reference list is a `warn`-level integrity signal, not a `block`, but it compounds the citation-fidelity problem.

On the positive side, the SRL framework is genuinely (if lightly) applied — the forethought/performance/reflection cycle in §1 and the Rutledge & Berange (2022) "regulatory strategies to act on what they see" caveat in §2 are used to interpret, not merely named. The measurement critique (Vandermeer 2023 on click-count proxies) is correctly engaged. So D1 and D3 are `warn`, not `block`, from the domain seat.

D2 `block` (citation used against its source). D1/D3/D4/D5 `warn`.

## Editorial Decision
editorial_decision=reject_or_major_revision

---

### Domain Review Report (Peer Reviewer 2) (full narrative)

#### Reviewer Identity
Senior learning-analytics scholar in the self-regulated-learning tradition; familiar with the dashboard-effectiveness literature, the peer-comparison/demotivation debate, and the measurement critique of click-based engagement proxies.

#### Overall Recommendation
Major Revision.

#### Confidence Score
4 — Citation fidelity and the dashboard/SRL literature are within my competence; the specific empirical claims of the (fictional) cited works I judge from their titles and the manuscript's own use of them.

#### Summary Assessment
The manuscript engages the right literature — the SRL cycle, the demotivation/equity debate, and the measurement critique of click-based engagement — and applies the SRL frame with reasonable depth rather than as ornament. Its central domain flaw is a misused citation: §2 cites Ferro & Nakamura (2021) for the claim that dashboards "reliably improve outcomes for lower-achieving students," but that reference is titled *"When dashboards demotivate,"* i.e., it documents the opposite. Because the paper's equity rationale and part of its Discussion rest on this reading, the domain argument does not currently hold. The reference list is also padded — about half of the listed works are never cited. The theoretical framing is salvageable and even a strength; the citation integrity is not, as written. Major Revision, conditional on correcting the source representation and rebuilding the "who benefits" argument on what the literature actually says.

#### Strengths
1. **SRL framework genuinely applied**: §1 uses the forethought/performance/reflection cycle to motivate the dashboard-as-feedback mechanism, and §2 (Rutledge & Berange, 2022) adds the correct caveat that dashboards help "only when learners possess the regulatory strategies to act on what they see." This is application, not name-dropping.
2. **Measurement critique engaged**: §2 cites Vandermeer (2023) to concede that click-based engagement "should be treated as rough indicators rather than as faithful measures of the cognitive engagement the theory implicates" — the field's central measurement worry, correctly surfaced.
3. **Methodological-critique awareness**: §2 cites Ibarra (2023) that "causal language frequently outruns the evidence" and positions the study as correlational — showing the authors know the field's causal-overreach problem (which makes the Discussion's breach a coherence failure, not ignorance).

#### Weaknesses
1. **Citation used against its own source (Ferro & Nakamura, 2021)** (Severity: Critical)
   - **Problem**: §2 claims dashboards "reliably improve outcomes for lower-achieving students (Ferro & Nakamura, 2021)," but the reference is titled *"When dashboards demotivate: Peer comparison and the lower-achieving student."* The citation supports the opposite of the claim.
   - **Why it matters**: The equity rationale for dashboard deployment (§2) and the alignment claim in §5 both rest on this. A load-bearing argument built on a mis-read source collapses when the source is read correctly. Field-norm basis: citation–claim fidelity (COPE citation-integrity guidance; APA 7.0 §8) — a grounded, universal standard, not an asserted subfield preference.
   - **Suggestion**: Read the source correctly and rewrite §2's "who benefits" paragraph; if the literature is genuinely split (some improvement, some demotivation, framing-dependent per Osei 2020), present it as a genuine tension your data speaks to — which is a *stronger* paper.
   - **Recommended references**: The manuscript's own Osei (2020) and Rutledge & Berange (2022) already support the demotivation/conditional-benefit reading; use them. (I recommend only sources already in the manuscript; I will not invent metadata — #574 A5.)
2. **Reference-list padding / uncited works** (Severity: Major)
   - **Problem**: ~9 of 18 references never appear in the text (Ainsworth & Devi 2018; Berange 2021; Delacroix & Ohno 2022; Halloran 2020; Kessler & Amadou 2019; Montez 2022; Prakash & Tolliver 2021; Solberg & Whitfield 2018; Wexler & Ojo 2020).
   - **Why it matters**: Uncited references inflate the apparent evidence base and are a recognized integrity red flag; they also mean genuinely relevant retention literature (e.g., a "gateway course retention review," Halloran 2020) is listed but not integrated.
   - **Suggestion**: Cite each listed work at its relevant point or remove it. Integrate Halloran (2020) and Wexler & Ojo (2020) into the retention framing, where they are directly on-topic.
3. **"Engagement" terminology under-specified** (Severity: Minor)
   - **Problem**: The paper uses "engagement" for a session count while §2 concedes (via Vandermeer) that this conflates cognitive and behavioral engagement.
   - **Why it matters**: The mismatch between the theoretical construct (cognitive/regulatory engagement) and the operational measure (clicks) weakens every inference to the SRL mechanism.
   - **Suggestion**: Consistently call the measure "dashboard access frequency" or "behavioral engagement," and reserve "engagement" for the construct.

#### Detailed Comments

**Literature Review**:
- **Coverage**: The core debate (benefit vs. demotivation, measurement critique, causal-overreach critique) is covered. But the retention literature specifically — the paper's outcome — is thin in-text despite being present in the reference list (Halloran 2020; Wexler & Ojo 2020 uncited).
- **Integration quality**: §2 is mostly critical synthesis (thematic: benefit → demotivation → measurement → methodology), which is good — but the synthesis is undermined by the Ferro & Nakamura misreading, which points the "benefit" theme in the wrong direction.
- **Research-gap argument**: The gap ("more enthusiasm than evidence," "downstream outcomes rather than adoption") is well-argued and genuine.

**Theoretical Framework**:
- **Appropriateness**: SRL is the right frame for a dashboard-feedback mechanism.
- **Application depth**: Applied, not merely named — a strength.
- **Alternative frameworks**: A feedback-intervention or goal-orientation frame (Osei 2020 already gestures at goal orientation) could sharpen the "who benefits" analysis.

**Academic Argument Quality**:
- **Factual accuracy**: The Ferro & Nakamura representation is the central inaccuracy.
- **Argument logic**: The "who benefits" thread (§2 → §5) is internally undercut by the misread source.
- **Terminology precision**: "Engagement" construct-vs-measure slippage (Weakness 3).

**Contribution to the Field**:
- **Incremental contribution**: A correctly-scoped correlational engagement→retention result is a modest but publishable increment *if* the citation integrity is repaired.
- **Positioning**: Currently over-positioned (see EIC/DA); domain-wise it should be positioned as speaking into an unresolved benefit-vs-demotivation tension.
- **Overclaiming**: High (shared finding with EIC/R1/DA).

#### Missing Key References
- No fabricated recommendations. Within the manuscript's own reference list, Halloran (2020) and Wexler & Ojo (2020) are directly relevant to the retention outcome and should be cited; Osei (2020) and Rutledge & Berange (2022) should carry the corrected "who benefits" argument. Any external additions the authors seek should be treated as `[UNVERIFIED]` search leads (e.g., literature on the "productivity paradox" of dashboard feedback and on point-biserial/logistic modeling of retention) rather than confident citations (#574 A5).

#### Questions for Authors
1. Does Ferro & Nakamura (2021) find that dashboards *improve* or *demotivate* outcomes for lower-achieving students? The title and your §2 claim point in opposite directions.
2. Roughly half your references are never cited. Which are load-bearing, and will you integrate or remove the rest?
3. Given Vandermeer's (2023) caveat that click counts are not cognitive engagement, how do you justify inferring an SRL (perceived-control) mechanism from a session-count measure?

#### Minor Issues
- **Terminology**: "engagement" (construct) vs. "dashboard sessions" (measure) — disambiguate.
- **Citation format**: Rutledge & Berange (2022) and a standalone Berange (2021) both appear in the list; confirm both are intended and cited.
- Confirm every in-text citation resolves to a list entry and vice versa.

---

## Seat 4 — Peer Reviewer 3 (Cross-disciplinary / Practical)

### Phase 1 — Paper-content-blind pre-commitment

`contract_role: perspective`

## Contract Paraphrase

**D1 (methodology_rigor).** From an outsider (research-ethics / data-governance) seat, I read this dimension for whether the study's conduct — how the data were obtained and consented — meets accepted-practice standards, not for the statistical internals (R1's job).

**D2 (domain_accuracy).** Whether the paper's substantive claims are stated with the accuracy a non-specialist reader would need to act on them responsibly — especially whether deployment implications are drawn accurately from what was measured.

**D3 (argumentative_coherence).** Whether the leap from a single-course finding to institution-wide and worldwide prescription holds together, and whether the paper's stated caution matches its stated conclusions.

**D4 (cross_disciplinary_relevance).** My core dimension. Whether adjacent-field concerns — consent, equity, data governance, deployment feasibility, and cross-context generalizability — are engaged, and whether the practical recommendations are implementable without harm.

**D5 (writing_and_structure).** Whether the paper is accessible and its limitations honestly located for a mixed readership.

## Scoring Plan

### D1: methodology_rigor
- **what_to_look_for**: consent and ethics-review record for secondary use of behavioral data; whether participants knew their log data would be analyzed.
- **what_triggers_block**: analysis of identifiable behavioral data with no consent/ethics disclosure AND an explicit statement that subjects were not informed.
- **what_triggers_warn**: ethics review plausibly present but under-reported.

### D2: domain_accuracy
- **what_to_look_for**: deployment claims that match what was measured.
- **what_triggers_block**: a practice recommendation that the evidence cannot bear at all.
- **what_triggers_warn**: recommendation over-reaching but with a kernel of support.

### D3: argumentative_coherence
- **what_to_look_for**: scope discipline from sample to conclusion; stated caution matching stated conclusion.
- **what_triggers_block**: conclusion generalized to "worldwide / at scale" from one self-selected course, stated as fact.
- **what_triggers_warn**: generalization loose but hedged.

### D4: cross_disciplinary_relevance
- **what_to_look_for**: consent/equity/governance/feasibility engaged; stakeholder voices (withdrawn students; low-digital-literacy students) present; cross-context validity flagged.
- **what_triggers_block**: a deployment prescription that ignores a first-order ethics/equity problem the study itself raises.
- **what_triggers_warn**: adjacent concerns gestured at but under-developed.

### D5: writing_and_structure
- **what_to_look_for**: honest, located limitations section.
- **what_triggers_block**: limitations absent or actively misleading.
- **what_triggers_warn**: limitations present but omitting the biggest threats.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 — Paper-visible review

`contract_role: perspective`

## Dimension Scores

### D1: methodology_rigor
score: warn

### D2: domain_accuracy
score: warn

### D3: argumentative_coherence
score: block

### D4: cross_disciplinary_relevance
score: block

### D5: writing_and_structure
score: warn

## Failure Condition Checks

### F1
fired: true

### F2
fired: true

### F3
fired: true

### F0
fired: false

## Review Body

As the outsider on this panel — I work on research ethics and student-data governance — I see two problems the disciplinary reviewers may under-weight, and one is a first-order ethics issue.

**Undisclosed secondary use of behavioral data (consent).** §3.2 states plainly: "Students were not informed that their dashboard activity data would be analyzed for this study." The paper then analyzes exactly that data. There is no IRB/ethics-review statement anywhere. Analyzing identifiable behavioral logs that subjects were explicitly not told would be used for research is a consent problem, not a footnote — and in a paper that recommends institution-wide deployment, it undermines the ethical standing of the recommendation. From my seat this scores `warn` on D1 (I cannot see the ethics record and will not assert a specific jurisdiction's rule as a fired `block` without it — Role-boundary honesty), but it is a `block`-worthy concern on D4 because the paper's *deployment* argument ignores the governance problem its own method raises.

**Scale claim detached from the study (D3/D4 block).** §6 addresses "higher education institutions worldwide" and calls dashboards "a practical and generalizable lever for supporting student success at scale," from one 15-week introductory-statistics course at one institution with a self-selected sample. That is not a hedge that needs tightening; it is a category error — a single-site descriptive association presented as a worldwide institutional strategy. D3 `block` (the sample-to-conclusion leap breaks coherence) and D4 `block` (the interdisciplinary/scale claim is wholly unsupported by the design), which fires F3 (any high-priority dimension `block`).

**Equity and stakeholder blind spots.** The §2 literature itself says peer-comparison feedback can *demotivate* struggling students (Osei 2020), yet §6 recommends "encouraging students to engage" with the peer-comparison dashboard as a "dependable strategy" — with no equity analysis for the students the literature says it may harm, and no consideration of students with lower digital literacy for whom "engage more" is not costless. The most affected stakeholders — students who withdrew (the retention study's whole point) and lower-achieving students — are structurally absent from both the sample and the recommendation.

D3 `block`, D4 `block`; D1/D2/D5 `warn`.

## Editorial Decision
editorial_decision=reject_or_major_revision

*(Note: from my own dimension scores, F3 fires on D4=block; F1 also fires because mandatory D3=block. Per the contract's severity precedence the synthesizer will resolve to the F1 action; I emit the highest-severity fired action here, `reject_or_major_revision`.)*

---

### Perspective Review Report (Peer Reviewer 3) (full narrative)

#### Reviewer Identity
Research-ethics and student-data-governance scholar, secondary footing in institutional policy and program evaluation — the "outsider" reading this learning-analytics paper for consent, equity, and deployment realism rather than for its statistics.

#### Overall Recommendation
Major Revision (bordering on Reject on ethics grounds until the consent/IRB question is answered).

#### Confidence Score
4 on the ethics/governance and scope-generalization points (my expertise); 2 on the statistical internals (outside my competence — I defer to R1).

#### Summary Assessment
Read from outside the learning-analytics guild, this paper has an ethics problem and a scope problem that its disciplinary framing obscures. Ethically, §3.2 states that students were not informed their dashboard-activity data would be analyzed, and no IRB/ethics-review record appears — yet the paper analyzes that data and recommends institution-wide deployment. On scope, a single introductory course at one institution, with a self-selected sample, becomes in §6 a "generalizable lever ... at scale" for "institutions worldwide." Meanwhile the paper's own cited literature warns that the peer-comparison feature can demotivate the very students a retention intervention should protect, and the recommendation never engages that equity risk. The core association may be worth reporting once corrected, but the deployment prescription must be withdrawn and the ethics of the data use must be addressed before this is publishable. I acknowledge I am not a statistician and defer the numerical audit to Reviewer 1.

#### Strengths
1. **Honest single-item and median-split disclosures**: §3.3 and §5.1 concede the single-item DV and the coarse median split — the kind of methodological candor an ethics reviewer values, because it does not hide the study's soft spots.
2. **Right outcome for the field's stated need**: Choosing retention (a consequential student outcome) over adoption metrics means the research at least aims at something that matters to students, not just to vendors.
3. **Limitations section exists and names real issues**: §5.1 names the engagement-proxy narrowness, self-report bias, and single-course scope — a genuine (if incomplete) attempt at honesty.

#### Weaknesses
1. **Undisclosed secondary use of behavioral data; no ethics record** (Severity: Critical)
   - **Problem**: §3.2: "Students were not informed that their dashboard activity data would be analyzed for this study." No IRB/REC statement anywhere.
   - **Why it matters**: Analyzing identifiable behavioral logs subjects were told nothing about is a consent and data-governance failure; it also weakens the moral authority of an institution-wide deployment recommendation. As an outsider I cannot adjudicate the specific jurisdiction's rule, but the study cannot be evaluated without an ethics-approval and consent statement.
   - **Suggestion**: Add the IRB/ethics-approval reference and consent basis (or waiver rationale). If no approval was obtained, that is a fundamental problem, not a revision item.
2. **Worldwide/at-scale generalization from one course** (Severity: Critical)
   - **Problem**: §6 addresses "higher education institutions worldwide" and calls dashboards "a dependable strategy" and "a practical and generalizable lever ... at scale" — from one introductory-statistics course, one institution, self-selected respondents.
   - **Why it matters**: This is not a fixable hedge; it is a scope category error that will mislead the practitioners the paper addresses (institutional-effectiveness staff who might spend real budget on it).
   - **Suggestion**: Confine all claims to "in this course / at this institution, we observed an association." Delete "worldwide," "at scale," "dependable," "generalizable lever."
3. **Equity blind spot: the recommendation ignores the demotivation risk the paper itself cites** (Severity: Major)
   - **Problem**: §6 recommends encouraging engagement with a peer-comparison dashboard; §2 (Osei 2020) says peer comparison can demotivate struggling students. No equity analysis; no consideration of low-digital-literacy students for whom "engage more" is a real cost.
   - **Why it matters**: A retention intervention that may harm the lowest-achieving students while being recommended universally has an equity failure mode the paper does not consider.
   - **Suggestion**: Add an equity/differential-effects analysis (does the association hold, or reverse, for lower-achieving students?) and temper the recommendation accordingly.

#### Detailed Comments

**Assumption Audit**:
- **Explicit assumptions**: that dashboard visibility supports self-regulation (§1) — reasonable as a hypothesis, over-read as a result.
- **Implicit assumptions**: that "more engagement is better for everyone" — contradicted by the paper's own cited demotivation literature; that behavioral-log research on students needs no separate consent — an unexamined data-governance premise.
- **Paradigmatic assumptions**: a positivist "measure clicks → infer regulation" chain that the field's own measurement critique (Vandermeer 2023) has already questioned.

**Cross-Disciplinary Connections**:
- **Parallel research**: the research-ethics literature on learning-analytics consent and the "datafication of students" is directly relevant and absent. (Offered as an `[UNVERIFIED]` search lead, not a specific citation — #574 A5.)
- **Borrowing opportunities**: program-evaluation logic (theory of change; who is helped/harmed) would discipline the deployment claim.
- **Methodological borrowing**: differential-effects / subgroup analysis from program evaluation would directly test the equity concern.

**Practical Impact**:
- **Real-world application**: as written, the paper invites institutions to invest in dashboards on evidence that cannot bear the recommendation — "academically meaningful but practically misleading."
- **Implementation feasibility**: "encourage students to engage" is not a costless intervention; it competes for student attention and may disadvantage those with less time or digital access.
- **Stakeholders**: withdrawn students (absent from a voluntary mid-term survey) and lower-achieving students (the ones the cited literature flags) are the missing voices.

**Broader Implications**:
- **Ethical dimensions**: consent and surveillance of student behavior (Weakness 1).
- **Social impact**: an equity risk of widening gaps if the intervention helps the already-engaged (Weakness 3).
- **Future directions**: a longitudinal, consented, equity-stratified design.

#### Cross-Disciplinary Reading Recommendations
- Research-ethics / data-governance literature on learning-analytics consent, and program-evaluation differential-effects methods — offered as `[UNVERIFIED]` search leads (I will not fabricate author/year/venue; #574 A5), phrased as directions rather than citations.

#### Questions for Authors
1. What was the ethics-review status and consent basis for analyzing students' dashboard-activity logs, given §3.2 says students were not informed?
2. On what evidence does §6 generalize from one course to "institutions worldwide"?
3. Did you test whether the engagement–retention association differs for lower-achieving students, given your cited literature warns of demotivation for exactly that group?

#### Minor Issues
- §6's "dependable" and "generalizable" are the specific words to cut.
- The limitations section (§5.1) should add selection bias and the consent issue.

---

## Seat 5 — Devil's Advocate (Stress-Test Seat)

### Phase 1 — Paper-content-blind pre-commitment

`contract_role: da`

## Contract Paraphrase

**D1 (methodology_rigor).** Adversarially, this is where I attack the reproducibility and internal consistency of the numbers and the design's ability to license the claim — if the statistics do not cohere or the design cannot bear the conclusion, the paper's foundation is exposed.

**D2 (domain_accuracy).** The angle of attack is whether any load-bearing factual/citation claim is false or misrepresented — a single mis-cited source that props up the argument is a foundation-collapse target.

**D3 (argumentative_coherence).** My primary hunting ground: does the main conclusion follow from the evidence, or is there a logic-chain break — correlation asserted as causation, a conclusion the data actively fails to support, or an internal contradiction between sections?

**D4 (cross_disciplinary_relevance).** Attack surface: unsupported generalization presented as established fact.

**D5 (writing_and_structure).** Least adversarial for me; only relevant if disorganization hides an inconsistency.

## Scoring Plan

### D1: methodology_rigor
- **what_to_look_for**: statistics that contradict each other or are impossible; a design that structurally cannot support the thesis.
- **what_triggers_block**: any internally impossible statistic, OR a cross-sectional design carrying a causal thesis.
- **what_triggers_warn**: reporting gaps short of impossibility.

### D2: domain_accuracy
- **what_to_look_for**: a load-bearing citation or fact that is false.
- **what_triggers_block**: a core-argument claim resting on a misrepresented source.
- **what_triggers_warn**: peripheral inaccuracy.

### D3: argumentative_coherence
- **what_to_look_for**: causation-from-correlation; conclusion contradicting the data or an earlier stated commitment; a more parsimonious rival explanation.
- **what_triggers_block**: the main conclusion does not follow (logic-chain break) OR the data/commitment contradicts the conclusion.
- **what_triggers_warn**: local slips not fatal to the thesis.

### D4: cross_disciplinary_relevance
- **what_to_look_for**: scale/interdisciplinary claims asserted as fact.
- **what_triggers_block**: worldwide/at-scale claim from a single site stated as established.
- **what_triggers_warn**: over-reach that is at least hedged.

### D5: writing_and_structure
- **what_to_look_for**: structure concealing an inconsistency.
- **what_triggers_block**: unreviewable.
- **what_triggers_warn**: table–text mismatch.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 — Paper-visible review

`contract_role: da`

## Dimension Scores

### D1: methodology_rigor
score: block

### D2: domain_accuracy
score: block

### D3: argumentative_coherence
score: block

### D4: cross_disciplinary_relevance
score: block

### D5: writing_and_structure
score: warn

## Failure Condition Checks

### F1
fired: true

### F2
fired: true

### F3
fired: true

### F0
fired: false

## Review Body

I only challenge; here is the strongest case against the paper. The thesis — "increasing dashboard engagement is a promising lever for improving retention" (Abstract) — fails on three independent grounds, any one of which is fatal as stated.

First, **the numbers do not cohere**, so there is no stable finding to defend (D1 `block`): *r* = .42 vs. .24; *t*(156) in a sample of ≤142 (item-*n* = 87); *t*(140) = 1.31 reported at *p* = .008 when it is *p* ≈ .19; "all 142" vs. Table 2's 127.

Second, **the causal conclusion does not follow from the design** (D3 `block`): the data are cross-sectional and correlational, so "engagement improved retention" and "raises the probability [of] completion" (§5) are a straight correlation-to-causation leap — and the paper promised in §1.7 not to make it. This is an internal self-contradiction, not merely an overreach.

Third, **the load-bearing equity citation is misused** (D2 `block`): §2 cites Ferro & Nakamura (2021) — titled *"When dashboards demotivate"* — for the claim that dashboards *reliably improve* outcomes for lower-achieving students. A core supporting pillar says the opposite of what the paper claims.

The surface-form parity self-check (#216) applies: I am not crediting these as strong because they are phrased technically, nor discounting them for wording — each is checkable against the paper's own printed values and reference list, and each holds on substance. The field-norm severity gate (#215) applies to my causal-inference and citation CRITICALs: the norms invoked (cross-sectional data cannot license causal claims; citations must represent their sources) are universal, externally grounded standards (research-design consensus; COPE/APA citation-integrity), not norms I assert from model knowledge — so the CRITICAL severities are grounded, not `[FIELD-NORM UNVERIFIED]`.

D4 `block` (worldwide/at-scale claim from one course). D5 `warn` (Table 2 *N* mismatch). Since I do not assign the panel's dimension scores in the editorial sense, I emit these to satisfy the contract grammar; my substantive product is the issue list below.

## Editorial Decision
editorial_decision=reject_or_major_revision

---

### Devil's Advocate Review (full narrative)

Before the counter-argument, in fairness: the paper targets the right outcome (retention, not adoption), defines its engagement measure operationally, and openly flags its median-split and single-item weaknesses. Those are real strengths.

#### Strongest Counter-Argument

If I held the opposite view, I would argue that this paper demonstrates nothing beyond a well-known selection artifact dressed as an intervention finding. The entire result is consistent with a single omitted variable — conscientiousness (or academic motivation) — that independently causes both more dashboard use and higher completion. Under that rival explanation, the dashboard does no causal work at all: diligent students click more *and* finish more, and the dashboard is a bystander correlate. This explanation is more parsimonious than the SRL-mediation story, and it fits the data at least as well, because the study has no temporal ordering, no manipulation, and a self-selected sample that over-represents exactly the students (survey-responders) most likely to persist. The paper cannot rule it out — and never tries.

Worse, the paper's evidentiary base is not stable enough to adjudicate anything: its headline correlation is reported at two different values (.42 vs. .24), one *t*-test has more degrees of freedom (156) than the study has participants (142, or 87 on that item), and another reports a significant *p* (.008) for a *t* (1.31) that is not significant. When the numbers contradict each other this way, no counter-argument is even needed — there is nothing reproducible to attack. Finally, the one piece of "equity" support the paper leans on (Ferro & Nakamura, "When dashboards demotivate") in fact argues the reverse of the paper's use of it. So the strongest case against the paper is simply: the finding is unstable, the causal claim is unlicensed, the mechanism is unidentified against an obvious confound, and a key citation is inverted. The paper should claim, at most, "diligent students used the dashboard more and completed more often, in one course" — which is a very different and much smaller paper.

#### Issue List

##### CRITICAL

| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|----------|---------------------|-----------------------------|
| C1 | 4 (Logic Chain) / 3 | Causal conclusion from cross-sectional correlational data ("engagement improved course retention... raises the probability that a student completes the course"), contradicting the paper's own §1.7 pledge to distinguish pattern from cause | §5 ¶1; §6; Abstract; vs. §1.7 | Cross-sectional correlational designs cannot identify causal effects — research-design consensus (Shadish/Cook/Campbell tradition; the paper's own cited Ibarra 2023 audit) | The design has no temporal ordering, no manipulation, no identification strategy; the conclusion asserts causation regardless — an unrescuable logic-chain break unless the claim is downgraded to association |
| C2 | 4 (Logic Chain) / 1 (Data–Conclusion Mismatch) | Internally impossible / contradictory statistics: *r*=.42 vs .24; *t*(156) with N≤142 (item-n=87); *t*(140)=1.31 reported p=.008 (actually p≈.19); "all 142" vs Table 2 = 127 | Abstract vs §4.2; §4.3; Table 2 | Reported statistics must be reproducible and mutually consistent — universal quantitative-reporting standard (APA 7.0) | The printed values contradict each other on the paper's face; a single dataset cannot produce them, so the evidentiary core is unverifiable — foundation collapse |
| C3 | 2 (Cherry-Picking / Confirmation) | Load-bearing equity citation inverted: Ferro & Nakamura (2021), titled "When dashboards demotivate," cited for dashboards "reliably improve outcomes for lower-achieving students" | §2 ¶2; reused §5 | Citations must represent their sources (COPE citation-integrity; APA 7.0 §8) | The manuscript's own reference list gives a title that contradicts the claim it supports; a core "who benefits" pillar rests on the inversion |

##### MAJOR

| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|----------|---------------------|-----------------------------|
| M1 | 1 (Alternative Explanation) | Uncontrolled third-variable (conscientiousness/motivation) offers a more parsimonious non-causal account of the engagement–retention link; never addressed | §5 (mechanism claim) | Plausible confounds in observational designs must be acknowledged/addressed — observational-inference norm | The rival explanation fits the same data with fewer assumptions than SRL mediation and is not ruled out; the paper's causal reading over-rates its mechanism |
| M2 | 5 (Overgeneralization) | Selection bias: voluntary mid-term survey sample over-represents persisters; withdrawn students (the retention outcome's core) are structurally under-sampled; "random sample" (§3.2) contradicts the voluntary recruitment described in the same section | §3.2 | Sampling frame must support the inference population — sampling-inference norm | A retention study drawing on volunteers who are still enrolled mid-term biases the outcome distribution; the inference to "students" generally is unsupported |
| M3 | 8 ("So What?") / 5 | Worldwide/at-scale prescription from one introductory course at one institution presented as established fact | §6 | Generalization must be bounded by design scope — external-validity norm | A single-site descriptive association cannot license a worldwide institutional strategy; the scope leap is categorical |

##### MINOR

| # | Dimension | Issue Description | Location |
|---|-----------|-------------------|----------|
| m1 | 4 | False precision: perceived-control mean "3.847" (3 dp) with SD "0.62" (2 dp) | §4.1; Table 1 |
| m2 | 4 | Final-exam variable and Table 1 exam row appear without being part of the stated design/measures | §3.3 vs §4.1/§4.3 |
| m3 | 2 | ~9 of 18 references never cited in text (list padding) | References |

#### Ignored Alternative Explanations/Paths
1. **Conscientiousness / motivation as common cause** (M1): diligent students both click dashboards more and complete courses more; the dashboard is a correlate, not a cause. More parsimonious than SRL mediation and unaddressed.
2. **Reverse causation**: students who are on track (and thus likely to be retained) may check a progress dashboard more *because* they are doing well — the arrow could run outcome → engagement.
3. **Survivorship in the sample**: because the survey was voluntary and mid-term, the students least likely to be retained are least likely to be in the sample at all, inflating the apparent engagement–retention link.

#### Missing Stakeholder Perspectives
- Students who withdrew before the final (the "not retained" group the study is ostensibly about) — largely absent from a voluntary mid-term survey.
- Lower-achieving / performance-avoidance-oriented students whom the cited literature (Osei 2020) says the peer-comparison feature may demotivate.
- (Scope note per DA Dimension 7: identifying the absent voices only; the practical elaboration is R3's.)

#### Unexamined Premise (Frame-Lock Detection)
The entire paper presumes that a dashboard *access count* is a valid stand-in for the *cognitive/regulatory engagement* the SRL theory implicates — the paper cites Vandermeer (2023) conceding this proxy is unfaithful, then proceeds to infer an SRL mechanism from it anyway. The unexamined premise is that clicking equals regulating; if it does not, the perceived-control result and the SRL story both lose their footing regardless of the statistics.

#### Observations (Non-Defects)
- The paper's §1.7 self-commitment to separating pattern from cause is exactly the right instinct; the paper would be publishable (if modest) had it kept that promise. The gap between the stated intent and the executed conclusion is the single most fixable thing here.
- If the corrected association survives and is honestly scoped, "diligent students engage more and persist more, in one course" is a legitimate small contribution — the paper is over-claimed, not worthless.

---

# Part C — Editorial Decision Package

## Panel arithmetic (v3.6.2 synthesizer three-step protocol, N = 5)

**Step 1 — Scoring matrix** (rows = contract dimensions; columns = the five seats' Phase-2 `## Dimension Scores`):

| Dimension (priority) | EIC | R1 (meth) | R2 (domain) | R3 (persp) | DA | block count |
|----------------------|-----|-----------|-------------|------------|-----|-------------|
| D1 methodology_rigor (mandatory) | block | block | warn | warn | block | 3 |
| D2 domain_accuracy (mandatory) | warn | warn | block | warn | block | 2 |
| D3 argumentative_coherence (mandatory) | block | block | warn | block | block | 4 |
| D4 cross_disciplinary_relevance (high) | warn | warn | warn | block | block | 2 |
| D5 writing_and_structure (normal) | pass | warn | warn | warn | warn | 0 |

**Step 2 — Evaluate `failure_conditions[]`:**
- **F1** (sev 90, `any`, "any mandatory dimension scores 'block'"): D1, D2, D3 are mandatory and each is scored `block` by ≥1 reviewer → predicate holds for ≥1 of 5. **fired: true.**
- **F2** (sev 70, `majority`, "two or more mandatory dimensions score 'warn' or worse"): per reviewer, count reviewers for whom ≥2 mandatory dims (D1/D2/D3) are `warn`-or-worse. EIC: D1 block, D3 block (2) → yes. R1: D1 block, D3 block (2) → yes. R2: D2 block, D1 warn, D3 warn (3) → yes. R3: D1 warn, D2 warn, D3 block (3) → yes. DA: D1/D2/D3 block (3) → yes. 5/5 ≥ majority (⌊5/2⌋+1 = 3). **fired: true.**
- **F3** (sev 60, `any`, "any high-priority dimension scores 'block'"): D4 is the high-priority dim; R3 and DA score it `block` → ≥1 of 5. **fired: true.**
- **F0** (sev 10, `all`, "every mandatory dimension scores 'pass'"): not remotely — mandatory dims carry blocks. **fired: false.**

**Step 3 — Precedence and decision:** fired = {F1, F2, F3}. Highest severity = **F1 (90)** → `action = editorial_decision=reject_or_major_revision`.

`fired_conditions: [F1, F2, F3]`
`editorial_decision=reject_or_major_revision`

**Resolving the disjunctive action.** F1's action is `reject_or_major_revision`. Per `editorial_decision_standards.md`, the deciding question is whether the flaws are *fundamental and unfixable* (→ Reject) or *serious but fixable via re-analysis and re-scoping* (→ Major Revision). Here: (a) the statistical contradictions are correctable by re-running the analyses on the raw data; (b) the causal overreach is correctable by re-scoping the claims; (c) the citation inversion is correctable by reading the source and rebuilding one paragraph; (d) the ethics/consent question is answerable if an IRB record exists. None is intrinsically unfixable *provided the underlying data exist and an ethics approval exists*. Therefore the panel resolves F1 to **Major Revision**, with an explicit contingency: if re-analysis dissolves the association, or if no ethics approval was obtained, the decision converts to Reject at the next round. Iron Rule #4 (DA CRITICAL ⇒ cannot Accept) is satisfied — the decision is not Accept.

**Self-consistency note (§8.1):** the recomputed decision from the emitted per-reviewer scores matches the stated `editorial_decision=reject_or_major_revision`; no `[PANEL-SYNTHESIS-MISMATCH]`. All five seats returned usable Phase-2 outputs (`len(usable)=5=panel_size`); no `[PANEL-SHRUNK]`.

---

# Editorial Decision

## Manuscript Information
- **Title**: Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment
- **Manuscript ID**: (not supplied)
- **Submission Date**: (not supplied)
- **Decision Date**: Round 1
- **Review Round**: 1

## Review Panel Provenance (#540)

All five reviewer personas ran on a single model family. Persona diversity is not model diversity — blind spots may be correlated across reviewers (Ren et al. 2026, arXiv:2607.13104 §5.2). `ARS_CROSS_MODEL` was not configured for this session, so the cross-model Reviewer-2 track and the blind editorial-decision cross-check did not run.

---

## Decision

### Major Revision

*(Contract action `reject_or_major_revision`, resolved to Major Revision because the flaws are fixable in principle. Contingent conversion to **Reject** if (a) re-analysis on the raw data does not reproduce a genuine association, or (b) no ethics/IRB approval exists for the behavioral-log analysis.)*

---

## Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | Internally impossible / contradictory statistics — the evidentiary core is unverifiable as printed | R1, DA, EIC | *r*=.42 (Abstract) vs *r*=.24 (§4.2); *t*(156) with N≤142 / item-n=87 (§4.3); *t*(140)=1.31 reported *p*=.008 [actually ≈.19] (§4.3); "all 142" vs Table 2 = 127 | R1 |
| 2 | Causal / worldwide-scale conclusion from a cross-sectional single-course correlation, breaching the paper's own §1.7 promise | DA, EIC, R1, R3 | §5 "engagement improved... raises the probability"; §6 "dependable strategy... generalizable lever... at scale... worldwide" vs §1.7 | R2 (re-scope) |
| 3 | Load-bearing equity citation inverted (source titled "When dashboards demotivate" cited for "reliably improve") | R2, DA | §2 ¶2 "reliably improve outcomes for lower-achieving students (Ferro & Nakamura, 2021)" vs reference list title | R3 |

---

## Reviewer Summary

| Reviewer | Role | Recommendation | Confidence |
|----------|------|---------------|------------|
| EIC | LA/ed-tech journal Editor-in-Chief | Major Revision | 4 |
| Reviewer 1 | Quantitative measurement / applied statistics | Major Revision | 5 |
| Reviewer 2 | SRL / learning-analytics domain scholar | Major Revision | 4 |
| Reviewer 3 | Research-ethics / data-governance (cross-disciplinary) | Major Revision (Reject-leaning on ethics) | 4 |
| Devil's Advocate | Adversarial methodologist | (challenge seat — 3 CRITICAL findings) | — |

---

## Consensus Analysis

Consensus is computed per sub-claim over the 4 non-DA reviewers (EIC, R1, R2, R3), following the Step 1b decomposition. DA findings are tracked separately.

### Step 1b — Weakness Sub-Claim Inventory (abridged to the decision-driving sub-claims)

| sub_claim_id | parent_weakness | reviewers raised/corroborated | position summary | confidence (max) |
|--------------|-----------------|-------------------------------|------------------|------------------|
| SC-1 | Contradictory/impossible statistics (r .42/.24; df=156; p=.008/t=1.31; N 142/127) | R1 (raised), EIC (corroborated), DA (corroborated) | 3 agree, 0 disputed, R2 silent | 5 |
| SC-2 | Causal claim from cross-sectional data; §1.7 self-contradiction | EIC (raised), R1 (corroborated), R3 (corroborated), DA (corroborated) | 4 agree, 0 disputed | 5 |
| SC-3 | Worldwide/at-scale over-generalization | EIC (raised), R3 (corroborated), DA (corroborated) | 3 agree, 0 disputed, R1 partial/silent-as-D4-warn | 4 |
| SC-4 | Ferro & Nakamura citation inverted | R2 (raised), DA (corroborated) | 2 agree, 0 disputed, EIC/R3 silent | 4 |
| SC-5 | Missing effect sizes / CIs / power / assumption tests | R1 (raised) | 1 agree | 5 |
| SC-6 | Wrong test (Pearson on dichotomous outcome); base rate missing | R1 (raised) | 1 agree | 5 |
| SC-7 | Undisclosed secondary data use / no IRB record | R3 (raised) | 1 agree | 4 |
| SC-8 | Selection/volunteer bias; "random sample" mislabel | R1 (raised), R3 (corroborated), DA (corroborated) | 3 agree, 0 disputed, EIC silent | 4 |
| SC-9 | Third-variable (conscientiousness) confound unaddressed | DA (raised) | DA-only (tracked separately) | — |
| SC-10 | Reference-list padding (~9 uncited) | R2 (raised), DA (corroborated) | 2 agree | 4 |
| SC-11 | Equity blind spot (recommendation ignores demotivation risk) | R3 (raised), DA (corroborated) | 2 agree | 4 |

No sub-claim carries a `disputed` position — the panel does not conflict on any finding; the reviewers corroborate independently from non-overlapping angles. There are therefore **no SPLITs to arbitrate.**

### Points of Agreement (Consensus)

**[CONSENSUS-4]** (all 4 non-DA reviewers agree):
1. **SC-2 — Causal / prescriptive conclusion is unlicensed by the correlational cross-sectional design, and contradicts the paper's own §1.7 commitment.** EIC (D3 block), R1 (D3 block; "reverse-causation fallacy"), R3 (D3 block; scope), and DA (CRITICAL C1) each reach this independently. Author MUST address (no decline option).

**[CONSENSUS-3]** (3/4 agree, 4th silent):
1. **SC-1 — The reported statistics are internally contradictory / arithmetically impossible.** R1 (raised, confidence 5), EIC (corroborated), DA (corroborated); **R2 is silent** (out of the domain seat's remit — R2 deferred the arithmetic to R1). A Confidence-5 methodology finding; author MUST address.
2. **SC-3 — Worldwide/at-scale over-generalization from one course.** EIC (raised), R3 (corroborated), DA (corroborated); **R1 silent** (scored the related D4 `warn`, did not raise the scale claim as a separate finding). Author should address.
3. **SC-8 — Selection/volunteer bias and the "random sample" mislabel.** R1 (raised), R3 (corroborated), DA (corroborated); **EIC silent.** Author should address.

**Corroborated findings (2/4, below the consensus bar):**
- **SC-4 — Ferro & Nakamura citation inverted** (R2 raised @confidence 4, DA corroborated). Action-bearing; drives roadmap R3. Surface-form parity check (#216) applied at arbitration: the sub-claim's weight rests on the reference-list title contradicting the in-text claim — checkable substance, not phrasing — so it is not down-weighted for arriving from a single domain reviewer.
- **SC-10 — reference-list padding** (R2, DA). Content-supplementation priority.
- **SC-11 — equity blind spot** (R3, DA). Content priority.

**Single-reviewer findings (1/4, weighted by confidence, not consensus):**
- **SC-5** (missing effect sizes/CIs/power/assumption tests), **SC-6** (wrong test / base rate) — both R1 @confidence 5, full weight; roadmap R1/S1.
- **SC-7** (undisclosed data use / no IRB) — R3 @confidence 4; escalated in priority despite single-reviewer status because it is a research-integrity gate, not a quality preference.

### Points of Disagreement

None. The panel does not conflict on any sub-claim; every finding is either agreed or raised-and-unopposed. This is corroboration from four non-overlapping seats (statistics / domain / ethics / adversarial), not manufactured consensus. (Per Iron Rule #2 the reviewers could not see each other's reports; the convergence is independent.)

### DA-CRITICAL Handling

The Devil's Advocate raised three CRITICAL findings; per Iron Rule #4 the decision cannot be Accept (it is not), and each must appear in the decision with the EIC's validity assessment:

- **DA-C1 (causal claim from cross-sectional data)** — Corroborated by EIC, R1, R3 (= SC-2, CONSENSUS-4). EIC assessment: **valid.** Author must re-scope. Field-norm grounded (research-design consensus; the paper's own cited Ibarra 2023).
- **DA-C2 (impossible/contradictory statistics)** — Corroborated by R1, EIC (= SC-1). EIC assessment: **valid**, and the single most serious blocker. Author must re-analyze from raw data.
- **DA-C3 (inverted equity citation)** — Corroborated by R2 (= SC-4). EIC assessment: **valid**; the citation title contradicts its use on the paper's face. Author must correct.

All three DA CRITICALs survive the #215 field-norm gate (norms are universal, externally grounded) and the #216 surface-form parity gate (each holds on checkable substance).

---

## Decision Rationale

Three independent, mutually reinforcing failures put this manuscript at Major Revision rather than Accept or Minor Revision, and place it one step from Reject. First and most decisively, R1 (confidence 5) and the DA show the reported statistics are internally contradictory and in places arithmetically impossible — the headline correlation appears as both .42 and .24, one *t*-test carries a *df* (156) larger than the sample (≤142), and another reports a significant *p* (.008) for a non-significant *t* (1.31). Until the analyses are recomputed from raw data, there is no verifiable finding to publish. Second, all four non-DA reviewers plus the DA independently reach the same coherence failure: the paper draws causal, prescriptive, worldwide-scale conclusions ("improved," "raises," "dependable strategy," "generalizable lever ... at scale") from a single-course cross-sectional correlation — and does so after explicitly promising in §1.7 to keep pattern and cause separate. Third, R2 and the DA show a load-bearing equity citation (Ferro & Nakamura, 2021) is used to support the opposite of what its title reports.

The decision is not Reject because each defect is, in principle, fixable: re-analysis repairs the statistics, re-scoping repairs the claims, and one corrected paragraph repairs the citation — *provided* the raw data reproduce a genuine association and an ethics approval exists for the log analysis (R3's undisclosed-secondary-use concern, §3.2). It is not Minor Revision because the required work is substantive re-analysis and wholesale claim re-scoping, not clarification. Per `editorial_decision_standards.md`, mandatory-dimension `block` scores from multiple reviewers with a Confidence-5 methodology finding map to Major Revision with re-review required. The paper's core idea — a bounded, honestly-scoped engagement–retention association in one course — remains publishable if the authors let the evidence be as modest as it is.

---

## Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Source Reviewer | Severity | Section | Estimated Effort |
|---|--------------|--------------|----------------|----------|---------|-----------------|
| R1 | Re-run every analysis from raw data; report each statistic once, consistently, with per-analysis *N*; reconcile abstract, results, and both tables. Resolve r=.42/.24, df=156, p=.008/t=1.31, and 142-vs-127. | SC-1 | R1, EIC, DA | Critical | §4, Abstract, Tables 1–2 | 5–8 days |
| R2 | Re-scope all causal/prescriptive/scale language to associational, single-site, exploratory claims. Delete "improved," "raises the probability," "dependable strategy," "generalizable lever," "at scale," "worldwide." Reconcile with the §1.7 commitment. | SC-2, SC-3 | EIC, R1, R3, DA | Critical | §5, §6, Abstract | 3–5 days |
| R3 | Correct the Ferro & Nakamura (2021) representation to what the source reports ("demotivate"); rebuild the §2 "who benefits" paragraph and the §5 alignment claim on the corrected reading. | SC-4 | R2, DA | Critical | §2, §5 | 1–2 days |
| R4 | Add effect sizes (Cohen's *d*) with 95% CIs for both *t*-tests; add a power/sensitivity statement; conduct and report assumption tests (normality, variance homogeneity), addressing the acknowledged skew, or use robust/rank alternatives. | SC-5 | R1 | Major | §3.4, §4 | 3–4 days |
| R5 | Report the retention base rate; re-model retention with logistic regression (OR, 95% CI); if retaining a correlation, label it point-biserial. | SC-6 | R1 | Major | §3.4, §4.2 | 2–3 days |
| R6 | Add the IRB/ethics-approval reference and consent basis (or documented waiver) for analyzing dashboard-activity logs, given §3.2 states students were not informed. If no approval exists, disclose and address. | SC-7 | R3 | Critical | §3.1–3.2 | 1 day (if record exists) |
| R7 | Address selection/volunteer bias: reconcile the "random sample" wording (§3.2) with the voluntary recruitment described in the same section; add selection bias to limitations; discuss the retention-specific survivorship risk. | SC-8 | R1, R3, DA | Major | §3.2, §5.1 | 1–2 days |
| R8 | Add and address the third-variable (conscientiousness/motivation) confound as a rival explanation for the association. | SC-9 (DA-CRITICAL-adjacent) | DA | Major | §5 | 1 day |

### Required Item Details

**R1: Reconcile and re-analyze all statistics**
- **Problem**: Headline *r* differs by section; a *t*-test df exceeds the sample; a reported *p* is incompatible with its *t*; text *N* contradicts Table 2.
- **Source**: R1 Weakness 1 (confidence 5); EIC Weakness 1; DA C2.
- **Requirement**: Recompute from raw data; single consistent value per statistic; state *N* per analysis; APA 7.0 formatting.
- **Acceptance criteria**: Every statistic in abstract, results, and tables reconciles to one dataset; a reader can reproduce each *df* and *p* from the reported *N*.

**R2: Re-scope claims to the design**
- **Problem**: Causal/worldwide conclusions from a cross-sectional single-course correlation, against §1.7.
- **Source**: EIC W2; R1 W4; R3 W2; DA C1/M3.
- **Requirement**: Associational language only; explicit scope limits; conclusion rewritten around the corrected, modest effect.
- **Acceptance criteria**: No causal or scale verb survives; §1.7 promise and §6 conclusion are consistent.

**R3: Correct the inverted citation**
- **Problem**: Demotivation source cited for reliable improvement.
- **Source**: R2 W1; DA C3.
- **Requirement**: Represent the source correctly; rebuild the dependent argument.
- **Acceptance criteria**: The §2 claim matches the cited source's finding; the "who benefits" argument reflects the genuine benefit-vs-demotivation tension.

**R6: Ethics/consent statement**
- **Problem**: §3.2 states students were not informed their log data would be analyzed; no IRB record.
- **Source**: R3 W1.
- **Requirement**: Provide approval reference and consent/waiver basis.
- **Acceptance criteria**: An ethics-review statement is present and consistent with the data used; if none exists, the issue is escalated to the editor (potential Reject).

---

## Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Source Reviewer | Priority | Section | Expected Improvement |
|---|--------------|--------------|----------------|----------|---------|---------------------|
| S1 | Cite each listed reference at its relevant point or remove it; integrate the on-topic retention works (Halloran 2020; Wexler & Ojo 2020) into the framing. | SC-10 | R2, DA | P2 | §2, References | Restores reference-list integrity; strengthens retention framing |
| S2 | Add a differential-effects / equity analysis: does the engagement–retention association hold or reverse for lower-achieving students? Temper the recommendation accordingly. | SC-11 | R3, DA | P2 | §4, §5, §6 | Addresses the equity failure mode the cited literature predicts |
| S3 | Disambiguate "engagement" (construct) from "dashboard sessions / access frequency" (measure) throughout; justify the SRL-mechanism inference given the click-proxy caveat (Vandermeer 2023). | SC-4-adjacent | R2, DA (frame-lock) | P2 | throughout | Aligns construct and measure; strengthens mechanism claim |
| S4 | Model engagement continuously rather than via median split (or justify the split with a robustness check). | — | R1 | P2/P3 | §3.3, §4.3 | Recovers discarded information; increases power |

---

## Revision Roadmap

### Priority 1 — Structural Revisions (Estimated total effort: ~12–18 days)
- [ ] R1 (SC-1): Re-run and reconcile all statistics from raw data.
- [ ] R2 (SC-2, SC-3): Re-scope all causal/scale claims to associational single-site language; reconcile with §1.7.
- [ ] R3 (SC-4): Correct the Ferro & Nakamura representation and rebuild the dependent argument.
- [ ] R6 (SC-7): Add IRB/ethics-approval and consent statement (or disclose absence).
- [ ] R4 (SC-5): Add effect sizes, CIs, power, and assumption tests.
- [ ] R5 (SC-6): Report base rate; re-model retention with logistic regression.
- [ ] R7 (SC-8): Address selection/volunteer bias and the "random sample" mislabel.
- [ ] R8 (SC-9): Add and address the conscientiousness confound.

### Priority 2 — Content Supplementation (Estimated total effort: ~4–6 days)
- [ ] S1 (SC-10): Fix reference-list integrity; integrate uncited retention works.
- [ ] S2 (SC-11): Add equity / differential-effects analysis; temper recommendation.
- [ ] S3: Disambiguate engagement construct vs. measure; justify SRL-mechanism inference.

### Priority 3 — Text and Formatting (Estimated total effort: ~1 day)
- [ ] Standardize numeric precision (perceived-control mean to 2 dp to match SD).
- [ ] APA 7.0 statistical formatting (italicize *r*, *t*, *p*, *M*, *SD*, *N*; exact *p*; no *p* = .000).
- [ ] Reconcile Table 1/Table 2 sample labels with the text; note which sample each row uses.
- [ ] Model engagement continuously or add a median-split robustness check (S4).

### Total Estimated Effort
- **Major Revision**: ~4–5 weeks.

---

## Revision Deadline
- **Recommended deadline**: 6–8 weeks (Major Revision).
- **Basis**: Substantive re-analysis + claim re-scoping + ethics documentation; re-review required.
- **Extension policy**: Notify the editor at least 1 week before the deadline if an extension is needed.

---

## Response Letter Instructions

Please use `templates/revision_response_template.md` (R→A→C format) to respond point-by-point.

**Must include**:
1. A response and revision description for each Required Revision (R1–R8), including the reconciled statistics table.
2. A response for each Suggested Revision (S1–S4) — adopted, or reason for not adopting.
3. Change markup (track changes / color) in the revised manuscript.
4. A cross-reference table of new section/paragraph locations.
5. Explicitly: which single value is the correct primary association, shown recomputed from the data; and the ethics-approval reference.

---

## Closing

We encourage you to carefully consider the reviewers' comments and submit a substantially revised manuscript. The research question is worthwhile and the study is salvageable, but the revised manuscript will undergo another round of review, and acceptance is contingent on the re-analysis reproducing a genuine (and honestly-scoped) association and on a documented ethics basis for the behavioral-log analysis. Please note that if the recomputed statistics do not support an association, or if no ethics approval exists, the decision at the next round would convert to Reject.

---

## Part 3: Reviewer Report Summary (Appendix)

### EIC Report Summary
- Recommendation: Major Revision | Confidence: 4
- Key Point: Topical and well-written, but the headline statistic is unstable (r=.42 vs .24) and the conclusion over-promises causally/at-scale against the paper's own §1.7 pledge.

### Reviewer 1 (Methodology) Summary
- Recommendation: Major Revision | Confidence: 5
- Key Point: The reported statistics are internally contradictory and in places arithmetically impossible (df=156 with N≤142; p=.008 with t=1.31); no effect sizes/CIs/power; wrong test for a dichotomous outcome; causal claim from cross-sectional data.

### Reviewer 2 (Domain) Summary
- Recommendation: Major Revision | Confidence: 4
- Key Point: A load-bearing equity citation (Ferro & Nakamura, "When dashboards demotivate") is used to support the opposite of what it reports; the reference list is padded (~9 uncited); the SRL framing is otherwise genuinely applied.

### Reviewer 3 (Perspective) Summary
- Recommendation: Major Revision (Reject-leaning on ethics) | Confidence: 4
- Key Point: Undisclosed secondary use of behavioral-log data with no IRB record (§3.2), and a worldwide/at-scale deployment prescription from one course that ignores the equity/demotivation risk the paper itself cites.

### Devil's Advocate Summary
- Findings: 3 CRITICAL (causal-from-correlational; impossible statistics; inverted citation), 3 MAJOR (conscientiousness confound; selection bias; worldwide over-generalization), 3 MINOR. Strongest counter-argument: the whole result is consistent with a conscientiousness confound and a self-selected sample — "diligent students click more and finish more, in one course" — with no stable, reproducible number to defend.
