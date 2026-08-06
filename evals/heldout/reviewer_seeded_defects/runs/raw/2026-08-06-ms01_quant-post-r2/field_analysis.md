# Field Analysis Report

## Paper Basic Information

- **Title**: Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment
- **Abstract length**: ~145 words
- **Full text length**: ~2,750 words excluding references (Introduction ~470; Literature Review ~490; Methods ~700; Results ~400; Discussion ~330; Conclusion ~95). Figures are estimates from the supplied text.
- **Number of references**: 16 (of which 8 appear never to be cited in the body text)
- **Language**: English
- **Setting**: Single introductory statistics course, "Meridian State University" (apparently pseudonymised), one 15-week term, N = 142 analytic sample

---

## Field Analysis

| Dimension | Analysis Result |
|---|---|
| **Primary Discipline** | Learning analytics / educational technology, specifically student-facing dashboard effectiveness research |
| **Secondary Disciplines** | (1) Higher education studies — student retention and persistence; (2) Educational psychology — self-regulated learning and achievement goal orientation; (3) Information science / student data governance — consent, privacy, secondary use of trace data |
| **Research Paradigm** | Quantitative. Presented as combining behavioural logs with self-report, but the survey component is a single-item rating, so this is not a mixed-methods design in any recognised sense; the paper never claims to be, yet the abstract's "self-report survey" framing invites that misreading |
| **Methodology Type** | Observational cross-sectional correlational study using LMS trace data plus a cross-sectional survey. Analysis limited to bivariate Pearson correlation, independent-samples *t*-tests, and a median-split group comparison. No covariates, no multivariable model, no design element supporting temporal ordering |
| **Target Journal Tier** | **Aspiration Q1; current execution below Q3.** Aspiration is signalled by the framing ("For higher education institutions worldwide"), the SRL theoretical hook, and the scale-up language in the Conclusion. Execution is constrained by: single-course single-term design, bivariate-only analysis, two single-item measures, and — decisively — internal numerical contradictions between the abstract, Results, and Table 2 that make the reported findings currently non-evaluable. Tier judgement should be revisited only after the authors reconcile the statistics |
| **Paper Maturity** | **Revised draft.** Structure is complete, prose is fluent and well organised, references are consistently formatted with DOIs, and the Introduction and §5.1 show genuine methodological self-awareness. But the manuscript is not pre-submission: the abstract reports a different correlation than the Results (r = .42 vs r = .24), two reported *t*-tests carry degrees of freedom that no stated sample can produce, Table 2's subgroup *n*s sum to 127 against a claimed 142, one reported SD is arithmetically impossible for the stated response scale, and there is no ethics approval or data availability statement |

### Two flags that should be resolved before reviewer effort is spent

These are factual observations about the manuscript's apparatus, not review verdicts, and they condition how much of the review is worth writing:

1. **Reference verifiability.** All 16 references carry DOIs under the `10.5555` prefix, which is a reserved test/dummy prefix rather than a registered publisher prefix, and all five journal titles in the list (*Journal of Educational Data Practice*, *Learning Sciences Review*, *Journal of Learning Analytics Practice*, *International Journal of Educational Technology Studies*, *Higher Education Persistence Quarterly*) do not correspond to journals I can identify. This pattern is consistent with placeholder or fabricated references. If confirmed, it outranks every substantive comment. Verification is assigned below to the Journal-Fit Reviewer, corroborated by Peer Reviewer 2. Until verified, treat this as **unverified**, not established.

2. **Statistical reconcilability.** The inconsistencies are not uniform, which matters for how the audit should be written. The retention result is internally coherent (r = .24 with df = 140 yields t = 2.93, p ≈ .004 — matches). The failures are localised: the abstract's r = .42, the df = 156 perceived-control test, the t(140) = 1.31 / p = .008 pair, Table 2's *n*s, and the secondary-item SD. A blanket "the statistics are unreliable" comment would be less useful and less defensible than the itemised audit specified for Peer Reviewer 1.

---

## Recommended Target Journals (Top 3)

1. **Journal of Learning Analytics (JLA, SoLAR)** — The natural disciplinary home for student-facing dashboard research; publishes both effectiveness studies and methodological critique, and its readership already contains the audit literature this paper cites. It is also the venue most likely to demand that the correlational scope in the Introduction be honoured in the Conclusion. Best fit *after* the numbers are reconciled.
2. **British Journal of Educational Technology (BJET)** — Q1, receptive to LMS trace-data studies with an SRL framing and to single-institution deployments, but expects multivariable analysis and explicit ethics governance. Would likely require covariates and a logistic model for the dichotomous retention outcome.
3. **Australasian Journal of Educational Technology (AJET)** — A realistic Q1/Q2 destination for a well-executed single-course study with appropriately bounded claims. Lower novelty bar than JLA, same rigour expectations on reporting.

**Alternatives worth naming to the authors**: *Internet and Higher Education* (if the retention framing is strengthened theoretically); *Journal of College Student Retention* (if retention, not dashboards, becomes the centre of gravity — though the paper's outcome is course completion, not institutional persistence, which is the mismatch Peer Reviewer 2 is configured to press). *Computers & Education* is a poor current fit; its design-rigour screen would likely stop this at desk stage.

---

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC
**Display role**: Journal-Fit Reviewer
**Identity Description**: Associate Editor of the *Journal of Learning Analytics*, specialising in student-facing feedback and dashboard design; has served on LAK programme committees and handled the journal's stream of single-institution dashboard-effectiveness submissions, including several desk rejections for claim–evidence mismatch.
**Review Focus**:
1. **Scope and originality against a saturated sub-literature.** Dashboard-engagement-correlates-with-outcomes findings from one course are numerous. Determine whether this manuscript offers anything beyond a local audit — a new measure, a new mechanism test, a disconfirming result — and say plainly if it does not.
2. **Claim–evidence calibration at the level the journal screens on.** The abstract reports r = .42; §4.2 reports r = .24. The Conclusion asserts dashboards "raise" retention and are a "dependable" and "generalizable" lever. Assess whether the manuscript's headline claims survive contact with its own Results section, and whether the gap is a correction or a positioning problem.
3. **Apparatus integrity.** Verify the reference list (the `10.5555` DOI prefix and the unidentifiable journal titles noted above), the presence of an ethics approval statement, and a data availability statement. Report findings as verified or unverified; do not assert fabrication without a check.

**Will particularly care about**: Whether the Introduction's explicit promise to "distinguish the pattern in the data from the causal story" is kept by the Discussion and Conclusion — the manuscript indicts itself using its own stated standard and its own citation of Ibarra (2023).
**Possible blind spots**: Unlikely to recompute individual test statistics or check whether a reported SD is attainable on an integer scale; may treat the consent gap as a compliance checkbox rather than a substantive harm question. Peer Reviewers 1 and 3 cover these.

---

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1
**Display role**: Peer Reviewer 1
**Identity Description**: Quantitative methodologist in educational measurement, specialising in observational designs built on LMS trace data; publishes on statistical reporting standards and routinely runs consistency audits (statcheck-style recomputation of test statistics against reported *p*-values) as a referee.
**Review Focus**:
1. **Itemised consistency audit, with recomputation shown.** Specifically: (a) abstract r = .42 vs §4.2 r = .24 — which is the estimate? (b) t(156) = 3.02 for perceived control implies 158 cases, but only 87 respondents answered the item and the analytic sample is 142 — the df is unattainable. (c) t(140) = 1.31 is reported with p = .008; at df = 140, t = 1.31 gives two-tailed p ≈ .19, and p = .008 would require t ≈ 2.68 — and the surrounding prose ("did not reach a comparable level," "the difference was small") contradicts the printed *p* in the other direction. (d) Table 2's *n*s (66 + 61 = 127) contradict both the stated 142 and the df of 140. (e) The secondary clarity item reports N = 10, M = 3.00, SD = 0.10 on an integer 1–5 scale; with integer responses summing to 30, the attainable sample SDs are 0, 0.471, 0.667, … — 0.10 cannot occur. (f) M = 3.847 reported to three decimals from a single integer item is false precision. Note explicitly that the retention correlation *is* internally coherent, so the audit is targeted rather than blanket.
2. **Design validity and the exposure-time confound.** Retention is coded as sitting the final assessment; dashboard sessions are counted "during the term." Students who withdrew early had fewer weeks in which to accumulate sessions, so the outcome mechanically constrains the predictor. Assess whether any directional interpretation is available without exposure-window normalisation or a design with temporal separation. Also: dichotomous outcome analysed by Pearson (point-biserial should be labelled as such; logistic regression is the appropriate model), no covariates whatsoever, median split on a right-skewed count with likely ties, no effect sizes or confidence intervals, no power analysis, no missing-data handling, final exam score used in Table 1 and §4.3 but never operationally defined in §3.3, and "standard statistical software" un-named (non-reproducible).
3. **Sampling description internally contradictory.** §3.2 states participants were drawn by "a random sample of students enrolled," then describes an open LMS announcement with voluntary self-selected response and exclusion of non-responders. These cannot both be true. The course enrolled "several hundred"; the response/coverage rate for the 142 is never reported, and self-selection is absent from §5.1.

**Will particularly care about**: Whether a single reported inferential statistic can be reproduced from the stated samples — and if not, whether the authors can supply the raw data and analysis script, since no revision to the prose fixes an unattainable degree of freedom.
**Possible blind spots**: Likely to treat the consent gap, the citation misrepresentation, and field-level novelty as outside methodological remit. Covered by Reviewers 2 and 3 and the Journal-Fit Reviewer.

---

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2
**Display role**: Peer Reviewer 2
**Identity Description**: Senior higher education researcher on student persistence and gateway-course attrition, working in the Tinto/Bean integration-and-departure tradition and its critics; has published on SRL-based dashboard interventions and knows the dashboard-effectiveness synthesis literature closely enough to notice when a source is cited against its own findings.
**Review Focus**:
1. **Citation–claim fidelity.** §2 states "Dashboards have been shown to reliably improve outcomes for lower-achieving students, who are said to gain the most from externalized progress cues (Ferro & Nakamura, 2021)" — but that reference is titled "When dashboards demotivate: Peer comparison and the lower-achieving student." The claim appears to invert the source, and the Discussion then builds on this inverted premise ("aligns with the view that externalized progress cues can support persistence"). Separately, 8 of 16 references appear uncited in the text (Ainsworth & Devi; Berange; Delacroix & Ohno; Halloran; Kessler & Amadou; Montez; Prakash & Tolliver; Solberg & Whitfield; Wexler & Ojo), including Halloran (2020) on gateway-course retention interventions and Wexler & Ojo (2020) on LMS trace-data retention modelling — the two sources most directly relevant to the paper's own question. Corroborate the Journal-Fit Reviewer's reference-verifiability check.
2. **Construct validity of "retention" and the generalisation it licenses.** The outcome is completing one course's final assessment. The field reserves "retention" for institutional or programme persistence. The Conclusion nonetheless generalises to "retention across programs and disciplines" and to institutions "worldwide." Assess whether the measured construct can carry that scope, and whether §5.1's limitation ("single introductory statistics course") is adequate when the Conclusion contradicts it two paragraphs later.
3. **Theory invoked but not measured.** The abstract states "we measured dashboard engagement, self-regulated learning behavior, and course persistence." No SRL measure exists in §3.3; the closest proxy is a single perceived-control item, which is not an SRL instrument and is not validated here. SRL is used as a framing device and then as an interpretive warrant in §5 ("consistent with a self-regulated learning account in which dashboards scaffold monitoring and adjustment") without any measurement standing behind it. Also assess the absence of established retention theory: the paper offers no theoretical account of departure at all, only a mechanism story about visibility.

**Will particularly care about**: Whether, once the overclaiming is stripped out, a contribution to the retention literature remains that is distinguishable from what Wexler & Ojo (2020) and Halloran (2020) — sat uncited in this paper's own bibliography — already established.
**Possible blind spots**: Likely to accept the reported statistics at face value rather than recompute them, and less attentive to data-protection and deployment-harm questions. Covered by Reviewers 1 and 3.

---

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3
**Display role**: Peer Reviewer 3
**Identity Description**: Learning analytics ethics and student data governance specialist, information-science trained, now institutional lead advising campus LA deployments on consent architecture, data protection, algorithmic fairness, and rollout feasibility; has halted dashboard pilots over peer-comparison harm and reviews for both LA venues and institutional research ethics panels.

*Angle note*: This is a genuinely different disciplinary lens, not a broader version of Reviewers 1 and 2. Reviewer 1 asks whether the numbers hold; Reviewer 2 asks whether the field learns anything; Reviewer 3 asks whether the data should have been collected this way and whether an institution acting on this paper would harm the students it aims to help.

**Review Focus**:
1. **Consent and lawful basis for secondary use of trace data.** §3.2 states plainly: "Students were not informed that their dashboard activity data would be analyzed for this study." There is no ethics/IRB approval statement, no data-protection basis (FERPA or GDPR as applicable), no anonymisation or retention description, and no data availability statement. The survey obtained consent; the behavioural logs — the paper's primary predictor — did not. Assess whether this is remediable by disclosure and retrospective approval, or whether it is publication-blocking at any reputable venue.
2. **Peer comparison as an unmonitored intervention with documented harm potential.** The dashboard included "a peer-comparison band," delivered to all enrolled students from week 1 with no opt-in. The paper's own cited sources (Osei, 2020 on discouragement from relative-standing feedback; Ferro & Nakamura, 2021 on demotivation among lower achievers) predict differential harm to precisely the students retention work targets. No harm monitoring, no subgroup analysis by prior achievement, and no discussion of differential effects appear anywhere. Note also that students who disengaged or withdrew are the group least represented in a self-selected mid-term survey — the harmed population is structurally invisible to this design.
3. **Deployment realism and gaming risk.** The Conclusion recommends institution-wide investment and "encouraging students to engage" as a "dependable strategy," on the basis of r = .24 in one statistics course. Assess: the dashboard's design is never specified (undocumented interface makes the "deployment" non-replicable and the recommendation non-transferable, which §5.1 half-concedes); no cost, staffing, or infrastructure estimate supports "at scale"; and an engagement-count target is directly gameable — if institutions nudge toward session counts, they optimise the proxy Vandermeer (2023) is cited as warning against, while raising legitimate student perceptions of surveillance.

**Will particularly care about**: Whether following this paper's recommendation could measurably harm lower-achieving students, and whether the manuscript gives an institution enough to act on responsibly even if every number were correct.
**Possible blind spots**: Will not adjudicate statistical detail or field-level novelty, and may under-weight whether the paper is publishable-if-fixed. Covered by Reviewer 1 and the Journal-Fit Reviewer.

---

## Review Strategy Recommendations

**Overlap check**: Journal-Fit Reviewer = fit, positioning, apparatus integrity. R1 = numbers and inference. R2 = literature, constructs, theory. R3 = ethics, harm, deployment. No focus area is duplicated. Reference verifiability is deliberately double-assigned (Journal-Fit primary, R2 corroborating) because a single unconfirmed check on a potential integrity issue is not enough to act on.

**1. Sequencing: verify the apparatus before weighting the substance.** If the reference list is confirmed to be placeholder or fabricated, that finding outranks all substantive commentary and changes the nature of the required action. Run the Journal-Fit Reviewer's verification check early and report it as verified or unverified. Do not let a verification failure be folded in as one comment among twenty.

**2. Treat the statistical-consistency findings as gating, not as line items.** Three reported inferential results cannot be reproduced from any sample the manuscript describes, and one reported SD is arithmetically impossible. This is not a "revise the analysis" comment — no rewriting reconciles a df of 156 with 87 respondents. The synthesiser should note that the manuscript's findings are currently non-evaluable pending author-supplied raw data and analysis code, and should let the recommendation follow from that fact rather than from tone.

**3. Assign causal overreach to prevent triple-counting.** All three peer reviewers will independently reach the Conclusion's causal language. Split ownership: **R1** owns causal inference (why the design cannot support "raises," including the exposure-time confound); **R2** owns generalisation and construct scope (why one course's final-exam attendance is not "retention across programs and disciplines"); **R3** owns action-recommendation risk (why "dependable strategy" is unsafe advice to institutions). The synthesiser should merge these into one finding with three distinct warrants, not three findings.

**4. Productive tension to preserve, not resolve.** R1 will conclude the study is unsalvageable with the data in hand; R3 will conclude the data should not have been collected as they were; R2 will conclude that even a clean version may not add to the field. These are not contradictory verdicts but three independent routes to the same conclusion — which strengthens rather than muddies the synthesis. Where they genuinely diverge is remediability: R1's problems are partly fixable with the raw data, R3's consent gap may not be fixable at all retrospectively. Surface that divergence explicitly.

**5. Register: developmental. Verdict: evidence-based.** The prose is competent, the Introduction states the correct epistemic standard, §5.1 names four real limitations unprompted, and §2 engages the critical literature (Ibarra, Vandermeer, Osei) rather than ignoring it. The author demonstrably knows what a careful correlational study looks like; the failure is in numerical control, in claim calibration between Introduction and Conclusion, and in ethics disclosure. Reviewers should write in a way that makes the fixes actionable and names what is genuinely working. This changes wording only — it does not soften the recommendation, and the recommendation must follow from the criteria and the evidence, not from the tone.

**6. The single most tractable framing for the authors.** The manuscript already contains its own indictment: the Introduction promises to "distinguish the pattern in the data from the causal story," §2 cites an audit of exactly this failure mode, and then §5 and §6 commit it. Leading with that internal contradiction is more useful than an external lecture on correlation and causation, because it shows the author already holds the standard they broke.
