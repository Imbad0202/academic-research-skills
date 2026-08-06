# Field Analysis Report

## Paper Basic Information

- **Title**: Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment
- **Abstract length**: ~130 words
- **Full text length**: ~3,000 words (main text, Sections 1–6), ~3,600 words including references
- **Number of references**: 15
- **Language**: English (review should be conducted in English)
- **Structure**: IMRaD, complete (Abstract → Intro → Lit Review → Methods → Results → Discussion → Limitations → Conclusion → References); 2 tables, no figures

---

## Field Analysis

| Dimension | Analysis Result |
|---|---|
| **Primary Discipline** | Learning analytics / educational technology, situated within higher education research. The unit of analysis is a student-facing LMS dashboard and its relation to course-level outcomes. |
| **Secondary Disciplines** | (1) Higher education student retention & persistence studies; (2) Educational psychology — self-regulated learning (SRL) theory; (3) Learning analytics ethics & educational data governance (consent, peer-comparison harms). A fourth adjacent field, HCI / information visualisation, is implicated by the "dashboard design differs from those deployed elsewhere" limitation but is not developed by the authors. |
| **Research Paradigm** | Quantitative. Observational, cross-sectional. The paper is *not* mixed methods despite combining two data sources — the survey component is a single-item quantitative rating, not qualitative data. Authors do not claim mixed methods; a reviewer should not mis-frame it as such. |
| **Methodology Type** | Correlational secondary analysis of LMS trace/log data, combined with a cross-sectional self-report survey. Analytic techniques: Pearson correlation (with a dichotomous outcome), median-split group formation, independent-samples t-tests. No multivariable modelling, no covariates, no effect sizes, no confidence intervals. |
| **Target Journal Tier** | **Author ambition: Q1.** The framing ("Evidence from…", scale-up language in the Conclusion, engagement with a named methodological critique literature) targets top learning analytics venues. **Current execution: Q3–Q4.** Single-course convenience sample, no causal identification strategy, no adjustment for confounders, and multiple internal reporting discrepancies place the manuscript well below the threshold of the journals it is written for. This gap between ambition and execution is the defining feature of the submission. |
| **Paper Maturity** | **Revised draft** (not pre-submission). Rationale: prose is polished, citation formatting is consistent, structure is complete, and the Limitations section shows genuine self-awareness — all markers of a manuscript past first draft. But the numbers reported in the Abstract, Results, and Tables do not reconcile with one another, and the Discussion/Conclusion assert a causal claim the Introduction explicitly disclaims. A manuscript at pre-submission maturity would have survived an internal consistency pass. The polish is a hazard: it can produce a halo effect that suppresses arithmetic scrutiny. |

---

## Recommended Target Journals (Top 3)

1. **Journal of Learning Analytics (SoLAR)** — The natural home venue. Publishes dashboard and feedback-loop research, and has an active editorial line on overclaiming in correlational analytics work (the very critique the paper cites via Ibarra). Open access, field-central readership. *Realistic outcome at present quality: reject or major revision.*

2. **British Journal of Educational Technology (BJET)** — Q1, broad edtech readership, receptive to LMS trace-data studies with institutional-deployment framing. Demands stronger statistical reporting and effect-size conventions than the manuscript currently meets.

3. **Journal of Computing in Higher Education** *or* **Australasian Journal of Educational Technology** — Q2 venues where a rigorously re-analysed, honestly scoped single-site study is publishable. **This is the realistic fit for the paper as written, once the reporting and claim-calibration problems are fixed.**

*Not recommended:* *Computers & Education* or *The Internet and Higher Education* — both would likely desk-reject a single-course cross-sectional correlational study without a causal identification strategy.

---

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC
**Display role**: Journal-Fit Reviewer
**Identity Description**: Associate Editor of the *Journal of Learning Analytics*, long-standing member of the SoLAR community, whose own work concerns feedback literacy and the evidentiary standards of the dashboard literature. Has co-authored editorials arguing that the field's credibility problem is not a shortage of studies but a surplus of studies whose conclusions outrun their designs. Handles roughly 60 submissions a year and desk-rejects about a third.

**Review Focus**:
1. **Claim–evidence calibration as a fit criterion.** Whether the manuscript's stated contribution ("a promising lever," "a dependable strategy," "generalizable") is one this journal's readership would accept from a single-course, single-term, self-selected sample of 142. Specifically, whether the Introduction's stated care ("careful throughout to distinguish the pattern in the data from the causal story") holds through Section 5 and Section 6, or collapses.
2. **Novelty and contribution to the field.** Whether "dashboard use correlates with retention" is a finding the journal's readers already regard as established, and what — if anything — the perceived-control component adds beyond a re-statement of the SRL premise the paper begins from.
3. **Reportability and integrity signals.** Whether the manuscript meets the journal's submission requirements: ethics/IRB statement, data availability, funding and conflict-of-interest declarations, and whether the reported statistics are internally reconcilable to the standard a copy-editor would not catch but a reader would.

**Will particularly care about**: Whether this paper, if published, would be cited by others as evidence that dashboards *cause* retention — i.e. whether the journal would be lending its imprimatur to precisely the inferential slippage its own published critiques (Ibarra 2023, cited here) warn against.

**Possible blind spots**: May reason at the level of framing and venue fit and delegate the arithmetic entirely to R1; may under-weight the research-ethics defect in §3.2 (students not informed their activity data would be analysed) if reading it as a fixable disclosure omission rather than a substantive consent problem.

---

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1
**Display role**: Peer Reviewer 1
**Identity Description**: Quantitative methodologist in an educational measurement department, applied statistician by training, specialising in observational designs using digital trace data. Teaches a graduate seminar on selection bias in learning analytics and routinely serves as a statistical reviewer who recomputes reported test statistics from the reported descriptives before writing a word.

**Review Focus**:
1. **Internal arithmetic reconciliation.** Recompute and cross-check every reported quantity against every other: the correlation coefficient stated in the Abstract versus the one in §4.2; the degrees of freedom of each t-test against the stated sample sizes and against the number of respondents to each item; the reported p-value against the reported t and df; the group *n*s in Table 2 against the analytic N and against a median split; the reported SD of the ten-student secondary item against the constraint that responses are integers on a 1–5 scale with a stated mean. Report each discrepancy with the specific numbers involved.
2. **Estimator–measurement fit and inferential adequacy.** Pearson correlation applied to a dichotomous retention outcome; median dichotomisation of a right-skewed continuous predictor (with its known cost in power and its capacity to manufacture spurious group differences); complete absence of covariate adjustment, effect sizes, and confidence intervals; absence of any account of the direction of the relationship (students who are failing withdraw, and withdrawn students cannot open a dashboard — the outcome mechanically truncates the exposure).
3. **Sampling and missingness.** The direct contradiction between "a random sample of students enrolled in the course section" (§3.2, sentence 1) and the volunteer-response recruitment described three sentences later; the undefined denominator ("several hundred students" enrolled, 142 analysed); the shifting analytic samples (142 / 87 / 127 / 10) and the absence of any missing-data accounting or comparison of respondents to non-respondents.

**Will particularly care about**: Whether any reported inferential statistic in Section 4 can be reproduced from the information the manuscript itself provides. A statistic that cannot be reconciled is not a rounding matter — it means the reader cannot tell what analysis was actually run.

**Possible blind spots**: May treat the citation-accuracy and literature-coverage problems as out of scope; may under-attend to the research-ethics question; may frame the recommendation purely as "re-analyse and resubmit" without asking whether the design can support *any* version of the paper's headline claim.

---

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2
**Display role**: Peer Reviewer 2
**Identity Description**: Higher education scholar working in the student persistence tradition (Tinto, Bean, and their contemporary critics), with a decade of empirical work on gateway-course attrition and institutional early-alert systems. Reads the learning analytics literature as an outsider-adjacent expert and is chronically unimpressed by studies that treat "retention" as a variable rather than as a construct with thirty years of contested definition behind it.

**Review Focus**:
1. **Construct validity of "retention."** The paper operationalises retention as completing the final assessment of one course in one term, then generalises in the Conclusion to "retention across programs and disciplines" for "higher education institutions worldwide." Whether course completion is a defensible proxy for institutional persistence, and whether the paper acknowledges — anywhere — that these are different constructs with different determinants. Also whether coding "enrolled but did not sit the final" as *not retained* conflates withdrawal with a single missed assessment.
2. **Citation accuracy and source–claim correspondence.** Verify that each in-text attribution matches what the cited source is titled and appears to argue. Pay specific attention to the §2 claim that "Dashboards have been shown to reliably improve outcomes for lower-achieving students… (Ferro & Nakamura, 2021)" against that entry in the reference list ("*When dashboards demotivate: Peer comparison and the lower-achieving student*"). Also flag the nine reference-list entries that appear nowhere in the body text (Ainsworth & Devi; Berange 2021; Delacroix & Ohno; Halloran; Kessler & Amadou; Montez; Prakash & Tolliver; Solberg & Whitfield; Wexler & Ojo) — 9 of 15.
3. **Literature coverage and theoretical framing.** Whether the SRL framing is doing real analytic work or is decorative: the paper invokes forethought/performance/reflection phases but measures none of them, substituting a single-item "perceived control" rating. Whether the retention literature the paper *should* engage (gateway-course intervention studies, early-alert evaluation, the persistence-modelling tradition) is represented — the reference list contains a review titled exactly that (Halloran 2020) and never cites it.

**Will particularly care about**: Whether the paper has read the sources it cites. A study whose Literature Review inverts the argument of a named source, and whose reference list is 60% uncited, has a scholarship problem that is independent of, and more serious than, its statistics problem.

**Possible blind spots**: May accept the reported numbers at face value and duplicate R1's territory only superficially; unlikely to interrogate the dashboard interface itself or the data-governance dimension; may over-index on the retention literature the paper omits at the expense of the analytics literature it engages competently.

---

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3
**Display role**: Peer Reviewer 3
**Identity Description**: Learning analytics ethics and educational data governance researcher, cross-appointed between an information school and a university research-ethics advisory board, with prior practitioner experience leading a campus-wide analytics deployment that was paused after a student-consent complaint. Publishes on algorithmic harm in student-facing systems and on the gap between what dashboard vendors promise institutions and what deployments deliver.

**Review Focus**:
1. **Consent, IRB, and secondary use of trace data.** §3.2 states plainly that "Students were not informed that their dashboard activity data would be analyzed for this study," while describing a consent process covering only the survey. There is no ethics approval statement anywhere in the manuscript. Assess whether the behavioural-log component was covered by any consent instrument, whether the study would clear a contemporary IRB, and whether the manuscript can be published at all without an ethics statement.
2. **Harms designed into the intervention, not just measured around it.** The dashboard includes a "peer-comparison band" (§3.1). The paper's own Literature Review documents that relative-standing feedback demotivates performance-avoidance-oriented students (Osei 2020) and cites a source titled *When dashboards demotivate*. Whether the study examines heterogeneous effects at all, or whether it aggregates over exactly the subgroup its cited literature predicts is harmed — and whether the collision-with-survivorship (harmed students disengage, then withdraw, then leave the analytic sample) means the design is structurally incapable of detecting the harm.
3. **Deployment realism and the generalisation claim.** The Conclusion advises institutions worldwide that dashboard investment is "a dependable strategy." Interrogate this from a practitioner's chair: one dashboard design, one interface, one LMS, one introductory statistics course, one term, one institution, no cost data, no implementation-fidelity data, no comparison condition. Also whether "encouraging students to engage" is even an actionable lever, or whether it mistakes an engagement *indicator* for an engagement *cause* — the sorting problem that R1 will name statistically and that a practitioner names operationally: telling students to click more does not manufacture the disposition that produced the clicking.

**Will particularly care about**: That the paper recommends scaling to institutions worldwide a system whose peer-comparison feature its own cited literature identifies as harmful to the students the equity rationale claims to serve — and does so without ethics approval on record.

**Possible blind spots**: May not engage the statistical reporting problems at all; may under-value what is genuinely competent in the manuscript (the Literature Review's measurement critique in ¶4 is honest and self-implicating); risks a review that reads as a governance objection rather than a scholarly assessment if not anchored to specific manuscript text.

---

## Coverage Check

| | Journal-Fit | R1 | R2 | R3 |
|---|---|---|---|---|
| Venue fit & contribution | ● | | | |
| Statistical reporting & inference | | ● | | |
| Construct validity of outcome | | ○ | ● | |
| Citation accuracy & lit coverage | | | ● | |
| Ethics / consent / governance | ○ | | | ● |
| Intervention design & harm | | | | ● |
| Claim calibration | ● | ○ | ○ | ○ |

● primary owner ○ secondary touch. No two reviewers own the same cell. The one deliberate overlap is *claim calibration*, which each reviewer reaches from a different route (venue norms / inferential logic / construct scope / deployment reality) — this is a convergence signal for the synthesiser, not redundancy.

---

## Review Strategy Recommendations

**1. This manuscript's distinguishing feature is the gap between surface quality and substrate quality.** The prose is genuinely good, the Limitations section is unusually candid, and the Literature Review contains a self-implicating methodological critique ("Most dashboard studies, including the present one, infer engagement from coarse behavioral proxies"). That candour is real and should be credited. It is also precisely what makes the manuscript risky to review quickly: a reviewer who reads for tone will conclude the authors are careful people, and will not check the arithmetic. **Instruct R1 to recompute before reading Section 5.**

**2. There is a coherence defect that is invisible section-by-section and obvious end-to-end.** The Introduction promises to "distinguish the pattern in the data from the causal story"; §2 ¶5 endorses Ibarra's critique that "causal language frequently outruns the evidence"; §3.1 states the design is cross-sectional; §5.1 lists appropriate limitations. Then §5 ¶1 opens "dashboard engagement *improved* course retention… increasing dashboard engagement therefore *raises* the probability," and §6 escalates to "*raises* course retention" and "a *dependable* strategy." A reviewer assigned only the Discussion will read this as ordinary overclaiming; a reviewer reading the whole manuscript will see the paper contradicting its own stated epistemic commitment. **Ensure at least two reviewers read the Introduction and Conclusion adjacently.**

**3. Verification targets — assign explicitly, do not leave to chance.** The following are checkable from the manuscript alone and each should have a named owner: (a) Abstract *r* vs. §4.2 *r*; (b) every reported *df* against every reported *N*; (c) each reported *p* against its reported *t* and *df*; (d) Table 2 group *n*s against the stated analytic sample and against a median split; (e) the ten-student secondary item's stated mean and SD against the constraint of integer responses; (f) §3.2 sentence 1 against §3.2 ¶2; (g) the §2 Ferro & Nakamura attribution against the reference-list title; (h) every reference-list entry against the body text. Findings on all eight should be reported with the specific figures quoted from the manuscript — no reviewer assertion without the receipt.

**4. Anticipated tension between reviewers, and how to hold it.** R1 and R3 will likely converge on reject; R2 may see a salvageable paper behind fixable scholarship errors; the Journal-Fit Reviewer must adjudicate whether the defects are *reporting* problems (fixable in revision) or *design and ethics* problems (not fixable without new data collection and retrospective ethics review). The synthesiser should force this distinction rather than averaging the recommendations. Note the asymmetry: the reporting inconsistencies could in principle be corrected; the absence of documented consent for the behavioural-log component cannot be corrected after the fact.

**5. Register: developmental, verdict: evidence-based.** Maturity is *revised draft*, so reviewers should write to help the authors rebuild rather than to dismiss — concrete, actionable, specific about what a defensible version of this study would look like. That governs *wording only*. It does not soften the recommendation, and it does not permit any reviewer to record an unreconciled statistic as a "minor point."

**6. Provenance note for the Journal-Fit Reviewer.** All 15 references carry DOIs under the 10.5555 prefix (a reserved test/example prefix), and the institution is named "Meridian State University." This may indicate a de-identified or synthetic manuscript prepared for evaluation purposes. Flag it as an observation; it does not change the review task, and every substantive defect identified above is present in the text on its own terms.
