# Field Analysis Report

## Paper Basic Information

| Item | Value |
|---|---|
| **Title** | Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment |
| **Language** | English (review should be conducted in English) |
| **Abstract length** | ~120 words |
| **Full text length** | ~2,500 words excluding references (estimated from section word counts) |
| **Number of references** | 15 entries; 6 cited in text, 9 appear in the list only |
| **Reported sample** | N = 142 (primary analytic sample); N = 87 (perceived-control item); N = 10 (secondary clarity item) |
| **Setting** | Single 15-week introductory statistics course, one institution, one term |

---

## Field Analysis

| Dimension | Analysis Result |
|---|---|
| **Primary Discipline** | Learning analytics / educational technology in higher education — specifically the student-facing dashboard (SFD) subfield |
| **Secondary Disciplines** | (1) Higher education student retention and persistence research; (2) Educational psychology — self-regulated learning and achievement goal theory; (3) Learning analytics ethics and educational data governance |
| **Research Paradigm** | Quantitative, observational. **Not** mixed methods, despite the paper's framing of "combining" log data with self-report — both strands are quantitative and there is no qualitative component. This distinction drives the R1 configuration below. |
| **Methodology Type** | Cross-sectional correlational study using LMS trace/log data plus a single-item survey; analysis limited to Pearson correlation, median-split grouping, and independent-samples *t*-tests |
| **Target Journal Tier** | **Aspirational: Q1–Q2.** The framing, keyword set, and institutional-implication register are pitched at field-leading venues. **Current evidentiary state: below Q2 threshold.** Triage detected a headline statistic that does not match the Results section (abstract r = .42 vs. Results r = .24), test statistics whose reported degrees of freedom cannot be reconciled with the stated sample sizes, and no ethics/IRB statement alongside an explicit note that students were not informed their activity data would be analyzed. Any Q1–Q2 editor would treat these as desk-screen items rather than revision items. Realistic near-term ceiling after major revision: Q2–Q3. |
| **Paper Maturity** | **Revised draft, not submission-ready — with a maturity mismatch that reviewers must be warned about.** Structure, sectioning, prose quality, and reference formatting all present as pre-submission (the limitations section is genuinely self-aware; the literature review is well-organised). The *numerical layer* is at first-draft integrity. Polished prose over unreconciled numbers is the specific risk profile here: it invites leniency. |

**Cross-disciplinary note:** this paper is moderately cross-disciplinary. Coverage strategy: R2 owns the core higher education / SRL literature, R3 owns the ethics-and-governance and practitioner-deployment perspectives that the paper itself opens (peer-comparison bands, undisclosed secondary use of trace data, institution-wide recommendations) but never examines.

---

## Recommended Target Journals (Top 3)

1. **Journal of Learning Analytics** (SoLAR, open access, Q1-equivalent in field) — Closest topical fit; dashboards, trace data, and SRL are core scope. SoLAR-affiliated venues also apply explicit expectations around learner data ethics, which makes this simultaneously the best fit and the venue most likely to hard-gate on the consent issue. Best choice *if* the paper is repaired.
2. **British Journal of Educational Technology (BJET)** — Q1, strong track record on LMS-based dashboard studies and on cautious framing of correlational technology-effect claims. Requires effect sizes, confidence intervals, and covariate adjustment as a baseline; single-course scope is publishable there only with sharply narrowed claims.
3. **Australasian Journal of Educational Technology (AJET)** — Q2, realistic fallback. Accepts single-institution deployment studies with descriptive-to-correlational designs, provided claims stay proportionate to the design and ethics approval is documented.

*Not recommended in current form:* Computers & Education, Internet and Higher Education, Studies in Higher Education. The first two demand causal identification or multi-context data; the third would reject on construct grounds, since "completed the final assessment in one course" is not retention as that literature defines it.

---

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC
**Display role**: Journal-Fit Reviewer
**Identity Description**: Associate Editor of the *Journal of Learning Analytics*, with a decade of handling student-facing dashboard submissions and prior service on a SoLAR working group on learner data expectations. Has personally desk-rejected upwards of forty single-course dashboard correlational studies and can recite what the existing systematic reviews of dashboards and SRL already establish.
**Review Focus**:
1. **Marginal contribution against the existing review literature.** The dashboard-engagement-correlates-with-outcomes finding is close to settled descriptive territory. Determine whether this manuscript adds anything beyond what published syntheses of student-facing dashboards already report, and whether the paper's failure to engage any systematic review or meta-analysis is itself disqualifying for a field-leading venue.
2. **Claim-to-evidence alignment at the title, abstract, and conclusion layer.** The abstract reports r = .42; Section 4.2 reports r = .24. The Discussion opens with "dashboard engagement improved course retention" and the Conclusion asserts a "dependable" and "generalizable" lever "for higher education institutions worldwide." Assess whether the manuscript's public-facing claims can be reconciled with its own Results section, and what that discrepancy implies about readiness.
3. **Desk-level research-integrity screen and journal fit.** Absence of any ethics approval, consent, or data-governance statement; the sentence "Students were not informed that their dashboard activity data would be analyzed for this study"; and a reference list in which every DOI shares a single non-resolving `10.5555` prefix. Decide whether these are revision items or gate items for the recommended venue, and whether readership interest survives once claims are cut to what the design supports.

**Will particularly care about**: Whether the paper's headline number is the same number the analysis produced — because if the abstract and Results disagree, no amount of downstream methodological repair tells the editor which finding the authors actually have.
**Possible blind spots**: Will judge at the level of claims and venue fit and may not verify individual test statistics, recompute degrees of freedom, or scrutinise measurement operationalisation. May also under-weight the domain-literature fidelity problems (see R2) because the literature review *reads* competently. Synthesizer must not let a fit-based "major revision" absorb or dilute R1's arithmetic findings or R3's ethics finding.

---

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1
**Display role**: Peer Reviewer 1
**Identity Description**: Quantitative methodologist in educational measurement, specialising in observational designs with behavioural trace data — selection and survivorship bias, point-biserial and dichotomous-outcome analysis, and the reconstruction of reported test statistics. Routinely recomputes every *t*, *df*, and *p* in a submission before writing a word, and has published on how sessionisation rules manufacture spurious engagement-outcome associations.
**Review Focus**:
1. **Recomputation and reconciliation of every reported statistic.** Section 4.3 reports *t*(156) = 3.02 for a perceived-control comparison, but only 87 respondents answered that item (implying df ≈ 85). It reports *t*(140) = 1.31 with *p* = .008 while describing the result as not reaching significance — *t* = 1.31 at df = 140 corresponds to *p* ≈ .19, and the stated df implies N = 142 while Table 2 sums to n = 127. The secondary item reports N = 10, M = 3.00, SD = 0.10 on a 1–5 integer scale, which is arithmetically unobtainable (integer responses averaging exactly 3.00 at n = 10 yield either SD = 0 or SD ≥ 0.47). Also assess M = 3.847 reported to three decimals against a 1–5 integer item. Determine for each figure whether it is a typographical error or evidence that the reported analyses were not run on the described data.
2. **Design-level threats that the association cannot survive.** Sampling is described as "a random sample of students enrolled in the course section" while the recruitment paragraph describes volunteers self-selecting into a mid-term LMS announcement — these are incompatible. Because recruitment occurred mid-term and retention is coded as completing the final assessment, students who withdrew early may be structurally absent from the sample (survivorship bias), and cumulative session counts are mechanically lower for anyone who left the course, making part of the engagement-retention correlation definitional rather than empirical. Evaluate reverse causality and the absence of any covariate (prior attainment, credit load, major).
3. **Analytic adequacy and reporting standards.** Median split of a right-skewed continuous predictor (acknowledged but not remedied); Pearson correlation with a dichotomous outcome without identifying it as point-biserial; no effect sizes, no confidence intervals, no power analysis; unexamined dependence of the association on the platform's default 30-minute sessionisation rule; single-item measures with no reliability or validity evidence.

**Will particularly care about**: Whether the numbers in the manuscript are internally consistent with each other and with the stated sample sizes. Until that is resolved, no substantive finding in the paper can be evaluated at all.
**Possible blind spots**: May stay inside the statistics and neglect the theoretical adequacy of the SRL framing, the field-literature citation problems, and the ethics dimension. May also treat "the data cannot support this" as a purely technical verdict without registering that the conclusions have already been written as institutional policy advice.

---

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2
**Display role**: Peer Reviewer 2
**Identity Description**: Senior higher education scholar working at the intersection of student persistence research (Tinto/Bean lineage and its contemporary critics) and self-regulated learning theory. Has served on retention-intervention review panels, reads dashboard studies primarily to check whether they know the persistence literature they invoke, and habitually reads every in-text citation back against the source it points to.
**Review Focus**:
1. **Construct validity of "retention."** The paper measures whether a student remained enrolled and sat the final assessment in one course, but titles, frames, and concludes in the vocabulary of institutional retention ("undergraduate attrition," "improving retention across programs and disciplines"). Assess whether course completion is a defensible operationalisation of retention as the higher education literature uses the term, and whether the mismatch between measure and claim is repairable by rewording or requires reframing the paper as a course-completion study.
2. **Citation fidelity and literature integrity.** Section 2 attributes to Ferro & Nakamura (2021) the claim that dashboards "have been shown to reliably improve outcomes for lower-achieving students," yet that source is titled "When dashboards demotivate: Peer comparison and the lower-achieving student" — an apparent reversal of the cited finding, and one on which the paper says it will build in the Discussion. Separately, the paper cites Ibarra (2023) on causal language outrunning correlational evidence and states "we designed the present study to be transparent about its correlational scope," then writes causal claims into the Discussion and Conclusion. Nine of fifteen listed references are never cited in text. Evaluate all three patterns.
3. **Theoretical adequacy of the SRL framework.** SRL is invoked as the explanatory mechanism (forethought, monitoring, reflection), but the only regulatory measure is a single global perceived-control item, which indexes neither strategy use nor monitoring behaviour. Assess whether the theory is doing genuine explanatory work or is decorative, and whether the achievement-goal literature the paper itself cites (performance-avoidance students disengaging) has been reconciled with the paper's uniformly positive interpretation.

**Will particularly care about**: Whether the manuscript is faithful to the sources it cites. A paper that reverses a cited finding and then commits the exact error the critique it cites warns against has a scholarship problem, not a writing problem.
**Possible blind spots**: May accept the reported statistics at face value while critiquing their interpretation, and may not independently detect the df/p inconsistencies. Likely to under-weight consent and data-governance questions as "compliance matters" outside the scholarly critique.

---

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3
**Display role**: Peer Reviewer 3
**Identity Description**: Learning analytics ethics and educational data governance researcher with an information science background, now advising a university system on institutional analytics deployment. Sits on an institutional review board, has drafted student-facing transparency notices for LMS trace-data research, and evaluates dashboard studies by asking what would happen if the recommendation were actually implemented at scale.
**Review Focus**:
1. **Consent, transparency, and secondary use of trace data.** The manuscript states plainly that "Students were not informed that their dashboard activity data would be analyzed for this study," while reporting that survey participants consented only to the survey. There is no ethics approval statement, no data-protection framing, and no waiver rationale. Assess whether analysing behavioural logs beyond the disclosed consent scope is defensible, what documentation would be required for any journal to publish this, and whether this is a fixable-by-disclosure item or a conduct-of-research item.
2. **Equity and harm profile of the intervention being recommended.** The dashboard includes a peer-comparison band. The paper's own literature review documents demotivation and discouragement effects of relative-standing feedback for lower-achieving and performance-avoidance-oriented students, then recommends institution-wide encouragement of dashboard engagement without any subgroup analysis, differential-effect testing, or discussion of who might be harmed. Evaluate the gap between the acknowledged risk and the unconditional recommendation.
3. **Deployment feasibility and generalisability of the institutional claim.** The Conclusion advises institutions "worldwide" to invest in dashboards and calls this "dependable" and "generalizable" based on one course, one term, one dashboard design, one institution. Assess what a practitioner could actually act on: no cost analysis, no comparison against alternative retention interventions, no account of the advising and staffing infrastructure dashboards require, no consideration that "encouraging engagement" with a metric turns that metric into a target.

**Will particularly care about**: Whether a real institution acting on this paper's recommendation would harm the students the paper says it wants to help — and whether the research itself was conducted within the bounds students were told about.
**Possible blind spots**: Will not verify statistical computations and may not weigh the novelty-against-existing-reviews question. Risk of anchoring the whole review on the consent sentence and giving thin treatment to the substantive design and theory problems, which R1 and R2 must cover independently.

---

## Review Strategy Recommendations

**1. The maturity profile is inverted, and reviewers must be primed for it.** Prose, structure, and self-aware limitations section all signal a competent pre-submission manuscript; the numerical layer does not survive first contact with a calculator. Fluent writing produces measurable leniency in reviewers. R1 should be instructed explicitly to recompute rather than read, and no reviewer should be allowed to infer analytic quality from writing quality.

**2. Instruct R1 to distinguish typos from data-integrity signals, and to say which.** Several inconsistencies are individually explainable as transcription errors (r = .42 vs .24; df 156 vs 85). Their *density* is the finding: three test statistics, one impossible SD, one unreconcilable table total, and one abstract-Results mismatch. R1's recommendation should turn on whether the pattern is consistent with sloppy transcription or with reported analyses that were never run on the described dataset. That distinction changes the verdict, so it must be argued rather than assumed.

**3. Anticipated tension: R3's ethics finding versus everyone else's revision framing.** R1, R2, and the Journal-Fit Reviewer are all likely to converge on major revision. R3 may reasonably land on a hard gate, since undisclosed secondary use of student trace data is not remediable by rewriting. The synthesizer must not average these into a single moderate verdict. If R3's reading holds, it constrains the others regardless of how the statistics are repaired, and the synthesis should present it as a precondition rather than as one vote among four.

**4. Anticipated overlap to police.** Three reviewers will independently notice the causal-language problem: EIC at the abstract/conclusion level, R2 as a citation-fidelity failure against Ibarra (2023), R1 as an inferential-validity failure. This convergence is genuine signal, not redundancy, but the synthesis should report it once with three grounds rather than three times. Similarly, the single-item perceived-control measure will attract R1 (psychometrics) and R2 (theoretical adequacy); keep the measurement critique with R1 and the theory critique with R2.

**5. Register guidance.** The manuscript shows real self-awareness — the limitations section names the session-count and single-course problems unprompted, and the literature review engages the field's methodological critics. A developmental register is warranted and will be usable by these authors. Register affects wording only. The recommendation itself must stay tied to the evidence against the criteria: the abstract does not match the results, the test statistics do not reconcile, the sampling description is self-contradictory, and the data were analysed beyond the disclosed consent scope. Constructive tone does not move any of those findings.

**6. One item no configured reviewer owns, flagged for the synthesizer.** The setting details (Meridian State University, a uniform `10.5555` DOI prefix across all fifteen references, placeholder-style journal titles) are consistent with a synthetic or de-identified manuscript. Reviewers should evaluate the submission on its stated content as written. The synthesizer should note that reference verifiability could not be established, without treating that as a substantive scholarly judgment about the authors.
