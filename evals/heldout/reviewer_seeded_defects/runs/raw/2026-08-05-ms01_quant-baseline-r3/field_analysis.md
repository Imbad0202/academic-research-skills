# Field Analysis Report

## Paper Basic Information

- **Title**: Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment
- **Abstract length**: ~115 words
- **Full text length**: ~2,600 words (body, Sections 1–6); ~3,300 words including references
- **Number of references**: 15 listed; 6 cited in text (Calloway 2019; Ferro & Nakamura 2021; Osei 2020; Rutledge & Berange 2022; Vandermeer 2023; Ibarra 2023). 9 listed references are never cited.
- **Language**: English (review should be conducted in English)

---

## Field Analysis

| Dimension | Analysis Result |
|---|---|
| **Primary Discipline** | Learning analytics / educational technology, situated within higher education research. The object of study is a student-facing LMS dashboard; the outcome of interest is course-level persistence. |
| **Secondary Disciplines** | (1) Higher education student retention & persistence studies; (2) Educational psychology — self-regulated learning and achievement-goal theory; (3) Learning analytics ethics, data governance, and institutional research practice. |
| **Research Paradigm** | Quantitative. Observational and correlational. Not genuinely mixed methods despite the two data sources — the survey component is a single-item quantitative rating, not a qualitative strand, so no integration logic is required or claimed. |
| **Methodology Type** | Single-site, single-course, cross-sectional observational study combining LMS trace/log data with a voluntary self-report survey. Analysis is Pearson correlation, median-split group formation, and independent-samples *t*-tests. No regression, no covariate adjustment, no causal identification strategy. |
| **Target Journal Tier** | **Aspiration: Q1–Q2.** The framing (SRL theory, retention outcomes, institutional implications) and the "implications for institutional deployment" pitch are aimed at mainstream field journals such as *Journal of Learning Analytics* or *BJET*. **Current execution: Q3 at best.** Rationale: (a) a single-course *n* = 142 correlational study with no comparison condition is thin for Q1 field journals that now expect quasi-experimental or multi-site designs; (b) the reported statistics contain internal contradictions that any Q1–Q2 statistical reviewer will catch on first pass; (c) the reference base is narrow (15 items, 6 used) and omits the canonical dashboard reviews and SRL sources the argument depends on. The gap between aspiration and execution is the single most important fact for the review team to hold. |
| **Paper Maturity** | **Revised draft** (surface) / **first draft** (substance). Structure is complete, headings are conventional, prose is polished, APA-style referencing is consistent, tables are present. But the numerical record is unstable across sections — the abstract, the Results, and the tables do not agree with one another, and section-to-section *N* values do not reconcile. Polished prose over an unreconciled analysis is characteristic of a manuscript written before the analysis was finalized. Treat as **not submission-ready**. |

### Triage signals that shaped the reviewer configuration

These are targeting cues for the review team, not the review itself. They are listed so that focus areas can be allocated without overlap:

- **Numerical inconsistency cluster**: abstract *r* = .42 vs. Results *r* = .24; *t*(156) reported on a perceived-control analysis whose stated *n* is 87; *t*(140) = 1.31 paired with *p* = .008; Table 2 subgroup *n*s (66 + 61 = 127) contradicting the stated 142 classified students; a secondary item reported as integer-scale *M* = 3.00 with *SD* = 0.10 at *N* = 10.
- **Claim–design mismatch cluster**: the Introduction explicitly promises to "distinguish the pattern in the data from the causal story," and the Literature Review cites Ibarra (2023) on causal overreach — then the Discussion and Conclusion state that engagement "improved" retention and "raises the probability" of completion, and the Conclusion generalizes to "institutions worldwide."
- **Sampling contradiction**: Section 3.2 states a "random sample" and then describes voluntary response to a mid-term LMS announcement. These are incompatible. The mid-term recruitment window also mechanically excludes early withdrawers from the retention outcome.
- **Ethics disclosure**: "Students were not informed that their dashboard activity data would be analyzed for this study." No IRB/ethics approval statement anywhere in the manuscript.
- **Source-fidelity issue**: Ferro & Nakamura (2021), whose listed title is *"When dashboards demotivate: Peer comparison and the lower-achieving student,"* is cited in text as evidence that dashboards "reliably improve outcomes for lower-achieving students."

---

## Recommended Target Journals (Top 3)

1. **Journal of Learning Analytics** (SoLAR, open access) — The closest topical match; the journal's readership is precisely the dashboard-evaluation community, and it has published both dashboard efficacy work and the methodological critiques this paper gestures at. It is also the venue least likely to tolerate causal phrasing over a cross-sectional design, which makes it the right diagnostic fit for a Journal-Fit Reviewer.
2. **Australasian Journal of Educational Technology** or **Technology, Knowledge and Learning** — Realistic Q2 landing zone for a single-site descriptive deployment study, provided claims are scaled back to the correlational scope and the statistical record is reconciled. These venues accept single-institution work when reporting is transparent.
3. **British Journal of Educational Technology** — Stretch target. BJET publishes dashboard work but expects either a stronger design (quasi-experimental, multi-cohort) or a substantially larger and better-characterized sample. Viable only after a design or scope revision, not after cosmetic edits.

*Not recommended in current form*: *Computers & Education* and *The Internet and Higher Education* — both now effectively require causal or multi-site designs for retention outcomes; desk rejection is the likely outcome.

---

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC
**Display role**: Journal-Fit Reviewer
**Identity Description**: Associate Editor of the *Journal of Learning Analytics*, active in the SoLAR/LAK community for a decade, who has handled roughly forty dashboard-evaluation submissions and co-authored an editorial on the gap between dashboard adoption claims and outcome evidence. Reads first for whether a manuscript earns space in a field that already has multiple systematic reviews of student-facing dashboards.

**Review Focus**:
1. **Contribution above the existing review literature** — the field already has synthesis-level statements that dashboard–outcome associations are small, heterogeneous, and design-dependent. Determine what a single-course *r* ≈ .24 adds beyond that baseline, and whether the paper positions itself against those syntheses at all (it currently does not cite any).
2. **Title–abstract–results–conclusion coherence as an editorial screen** — the abstract advertises *r* = .42 while the Results report *r* = .24, and the abstract concludes engagement is "a promising lever." Judge whether the manuscript's headline claim survives contact with its own results section, since this is what an editor screens before assigning reviewers.
3. **Journal fit and readership interest** — whether the framing ("implications for institutional deployment") matches what this evidence base can support, and whether the paper would be better placed in a practitioner-facing venue than a research journal.

**Will particularly care about**: Whether the manuscript's stated scope (Introduction: "careful throughout to distinguish the pattern in the data from the causal story") is honored by its own Conclusion, because a journal cannot publish a paper that refutes its own methodological self-description four pages later.

**Possible blind spots**: Will likely treat the statistical inconsistencies as "authors need to check their numbers" rather than diagnosing which specific values are arithmetically impossible; may under-weight the research-ethics disclosure, since consent handling is usually delegated to an ethics statement checklist rather than editorial judgment.

---

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1
**Display role**: Peer Reviewer 1
**Identity Description**: Quantitative methodologist in educational measurement with an applied-statistics appointment, specializing in observational designs built on platform trace data — selection mechanisms in log-based samples, binary-outcome modeling, and reporting standards (effect sizes, intervals, degrees of freedom reconciliation). Regularly serves as a statistical reviewer and has published on why click-count exposure measures produce inflated associations with completion outcomes.

**Review Focus**:
1. **Internal arithmetic and reporting integrity** — reconcile every reported statistic against its stated sample: the *df* = 156 perceived-control test against *n* = 87 respondents; the *t*(140) = 1.31 / *p* = .008 pairing; Table 2's 66 + 61 = 127 against the claim that all 142 students were classified; the *r* = .42 / *r* = .24 discrepancy; and whether an integer 1–5 item at *N* = 10 can yield *M* = 3.00 with *SD* = 0.10. Also the three-decimal *M* = 3.847 against a one-decimal *SD*.
2. **Design and estimator appropriateness** — Pearson correlation between a continuous count and a dichotomous retention outcome (point-biserial labeling; logistic regression as the appropriate model), the median split's cost in power and its arbitrariness, the absence of any effect size or confidence interval for the group comparisons, the absence of covariate adjustment for prior attainment or baseline LMS activity, and the right-skewed session distribution's implications for Pearson *r*.
3. **Selection and survivorship mechanics** — mid-term recruitment means students who withdrew before the announcement cannot enter the sample, which mechanically constrains the retention outcome; the "random sample" claim in §3.2 is contradicted by the voluntary-response recruitment described in the same subsection; no response rate is reportable because the course denominator is given only as "several hundred."

**Will particularly care about**: Whether the retention association is an artifact of the sampling window rather than a property of dashboard use — that is, whether the estimand is even identified given who could have entered the sample.

**Possible blind spots**: May stop at "the design cannot support the claim" without engaging the substantive higher-education literature on what retention means, and is unlikely to raise the consent/ethics issue or the misattributed citation.

---

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2
**Display role**: Peer Reviewer 2
**Identity Description**: Senior higher education researcher studying undergraduate persistence and gateway-course attrition, with a decade of work bridging the classical persistence literature (departure/integration models, institutional retention metrics) and the newer learning-analytics evidence base. Has served on national retention-initiative advisory panels and reviews regularly for higher education journals where "retention" is a technical term with an institutional definition.

**Review Focus**:
1. **Construct integrity of "retention"** — the paper operationalizes retention as sitting the final assessment in one course, then discusses and concludes in the vocabulary of institutional retention ("improving retention across programs and disciplines"). Assess whether course completion is being silently substituted for student persistence, and what that substitution does to the paper's stated contribution.
2. **Literature coverage and source fidelity** — Ferro & Nakamura (2021), titled *"When dashboards demotivate,"* is cited as showing dashboards "reliably improve outcomes for lower-achieving students," and this misreading is load-bearing for the equity argument the Discussion returns to. Separately: 9 of 15 listed references are never cited; the SRL framework is invoked repeatedly (forethought / performance / reflection phases) without citing its canonical sources; no systematic review of student-facing dashboards appears anywhere.
3. **Theoretical framing and contribution to the field** — whether the SRL account is genuinely tested or merely narrated around the results, given that "perceived control" is measured with one item and is never modeled as a mediator despite the Discussion calling it "a mediating construct."

**Will particularly care about**: Whether the paper's claimed positioning in the "who benefits from dashboards" debate is earned, when the study reports no subgroup analysis by prior achievement and its own key citation for that debate has been reversed in meaning.

**Possible blind spots**: May accept the reported statistics at face value while critiquing their interpretation; less likely to interrogate the sessionization rule or the technical feasibility of the log measures.

---

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3
**Display role**: Peer Reviewer 3
**Identity Description**: Learning-analytics ethics and data-governance specialist who also holds an institutional research/registrar-adjacent appointment — the person who actually has to sign off on whether a campus may analyze student trace data, and who is then asked whether the evidence justifies procurement. Works at the intersection of research ethics review, student data privacy regimes (FERPA/GDPR-style consent and legitimate-interest tests), and algorithmic equity in student-success systems.

**Review Focus**:
1. **Consent, disclosure, and ethics governance** — §3.2 states that "students were not informed that their dashboard activity data would be analyzed for this study," while survey consent was obtained separately. There is no ethics approval statement, no data-protection basis, no retention or de-identification protocol, and no explanation of how log data were linked to survey responses. Assess whether the disclosed procedure is publishable as described and what remediation (ethics statement, retrospective approval documentation, debriefing) is required.
2. **Equity and differential harm in deployment** — the paper's own Literature Review acknowledges that peer-comparison bands can demotivate performance-avoidance-oriented and lower-achieving students, yet the deployed dashboard includes a peer-comparison band and the Conclusion recommends institution-wide encouragement of engagement with no equity safeguard, no subgroup analysis, and no discussion of who might be harmed at scale.
3. **Practitioner decision-usefulness of the recommendation** — the Conclusion tells institutions worldwide that dashboard investment is "a dependable strategy." Evaluate what an institutional decision-maker could actually do with an *r* ≈ .24 from one statistics course: no cost data, no comparison against alternative retention interventions, no implementation conditions, and an unexamined assumption that engagement is a manipulable lever rather than a marker of students who were already going to persist.

**Will particularly care about**: The gap between "we observed an association among volunteers in one course" and "institutions worldwide should invest" — specifically, that the recommendation asks institutions to act on covertly collected behavioral data using an interface the paper's own cited literature says may harm the students it is meant to help.

**Possible blind spots**: Will not adjudicate the *df* and *p*-value arithmetic; may over-index on governance at the expense of acknowledging what the study does contribute descriptively.

---

## Review Strategy Recommendations

**Coverage map — no two reviewers hold the same territory.**

| Territory | Owner |
|---|---|
| Fit, originality against existing reviews, abstract–results coherence | Journal-Fit Reviewer |
| Statistical arithmetic, estimator choice, selection mechanics | Peer Reviewer 1 |
| Construct definition of retention, literature fidelity, theory | Peer Reviewer 2 |
| Consent/ethics, equity harm, practitioner decision-usefulness | Peer Reviewer 3 |

**Special characteristics requiring attention.**

1. **The paper argues against itself.** It cites Ibarra (2023) on causal overreach in correlational learning analytics, states in the Introduction that it will keep pattern and cause separate, and then writes "dashboard engagement improved course retention" and "raises the probability" in the Discussion. This is not a wording slip to be smoothed over — it is the manuscript's central defect, and every reviewer will land on some facet of it. **Deconfliction rule**: the Journal-Fit Reviewer owns it as an editorial-screen problem (does the headline survive the results?); Peer Reviewer 1 owns it as an identification problem (what estimand does this design support?); Peer Reviewer 3 owns it as a deployment-recommendation problem (what are institutions being told to do?). Peer Reviewer 2 should route around it and stay on construct and literature.

2. **Numbers before narrative.** Several reported statistics appear arithmetically impossible, not merely questionable. Peer Reviewer 1 must verify each one explicitly and state which values cannot coexist, because the synthesizer needs a hard finding here rather than a hedge. If the numbers are wrong, some of the substantive critiques may target results that will not survive correction — the synthesizer should sequence the report so that the reporting-integrity finding is resolved before interpretive critiques are weighted.

3. **A source appears to be cited against its own title.** Peer Reviewer 2 owns this exclusively. It matters disproportionately because the misread claim carries the paper's equity argument, and Peer Reviewer 3 independently relies on the opposite reading of the same evidence. Flag for the synthesizer: if R2 and R3 converge on the demotivation literature from different directions, that convergence is signal, not redundancy.

4. **Ethics is a gate, not a comment.** The undisclosed analysis of student trace data plus the missing ethics statement is potentially a publication blocker independent of every methodological issue. Peer Reviewer 3 owns it alone; no other reviewer should raise it, so that its weight in the synthesis is not diluted by triplication.

**Predicted tensions between reviewers.**

- **R1 vs. R3 on what to do with the paper.** R1's logic points toward "the design cannot answer the question — redesign or reframe." R3's logic points toward "the ethics disclosure may bar publication regardless of design." These are different verdicts arriving from different premises; the synthesizer should not average them but present both conditions as sequential gates.
- **Journal-Fit Reviewer vs. Peer Reviewer 2 on novelty.** The Journal-Fit Reviewer may find the contribution too thin against existing reviews; Peer Reviewer 2 may find a salvageable descriptive contribution if "retention" is redefined honestly as course completion. This is a productive tension and should be preserved in the synthesis rather than resolved.
- **Risk of pile-on.** All four reviewers can plausibly write "the causal claims are unsupported." Without the deconfliction rule above, the report will read as one criticism repeated four times, which weakens rather than strengthens it.

**Register.** Given the maturity assessment (polished surface, unreconciled substance), reviewers should adopt a **developmental register** — the author has a real dataset and a defensible descriptive study buried under overclaiming. Tone should be constructive and specific about remediation paths. **The register does not soften the verdict**: the recommendation must remain evidence-based against journal criteria, and the arithmetic and ethics findings are stated as findings, not as suggestions.

**Language.** Manuscript is in English; all four reviews should be written in English.
