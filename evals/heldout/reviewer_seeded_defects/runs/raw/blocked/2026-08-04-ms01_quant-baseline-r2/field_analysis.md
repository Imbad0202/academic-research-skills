# Field Analysis Report

## Paper Basic Information

- **Title**: Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment
- **Abstract length**: ~115 words
- **Full text length**: ~2,450 words (body) / ~3,000 words including references
- **Number of references**: 15 listed; **6 cited in text** (Calloway 2019; Ferro & Nakamura 2021; Osei 2020; Rutledge & Berange 2022; Vandermeer 2023; Ibarra 2023). 9 appear in the list only.
- **Language**: English (review should be conducted in English)

---

## Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| **Primary Discipline** | Learning analytics / educational technology, applied to undergraduate teaching and learning |
| **Secondary Disciplines** | (1) Higher education student persistence & retention studies; (2) Educational measurement / psychometrics (self-regulated learning constructs, single-item measures); (3) Research ethics & student-data governance |
| **Research Paradigm** | **Quantitative** — not mixed methods. The paper pairs behavioral logs with a self-report survey, but both strands are quantitative and there is no qualitative data collection, coding, or integration logic. Reviewer 1 should therefore be a quantitative methodologist, not a mixed-methods design specialist. |
| **Methodology Type** | Observational, cross-sectional correlational study; LMS trace-log extraction + single-item survey; Pearson correlation, median-split independent-samples *t*-tests. Single course, single term, single institution. |
| **Target Journal Tier** | **Aspiration: Q1/Q2** (topic, framing, and citation of the field's methodological critiques all signal a mainstream learning-analytics venue). **Current state: below Q2 threshold.** The manuscript contains numerical contradictions between abstract, Results, and tables (r = .42 vs. r = .24; *t*(156) reported against an N of 142; Table 2 n = 127 against a stated N = 142; *t*(140) = 1.31 paired with p = .008), which at most Q1 venues are desk-reject-class rather than revision-class findings. Tier judgment should be stated as *conditional on data-integrity resolution*. |
| **Paper Maturity** | **Revised draft** (not pre-submission). Structure is complete, prose is competent and unpadded, references are consistently formatted in APA, and the Limitations section volunteers two real weaknesses. But results reporting is internally inconsistent, the causal register in Abstract/Discussion/Conclusion contradicts the stated cross-sectional design, sampling is described two incompatible ways (§3.2 "random sample" vs. volunteer response to an LMS announcement), and there is no ethics-approval statement. This is a manuscript that reads finished and is not. |

---

## Recommended Target Journals (Top 3)

1. **Journal of Learning Analytics** (SoLAR) — Closest scope match: student-facing dashboards, trace-data measurement, and the field's own debate about causal overreach are core JLA territory. It is also the venue most likely to hold the paper to its own cited standard (Ibarra 2023). Realistic only after the reporting inconsistencies and the correlational-claim discipline are fixed.
2. **British Journal of Educational Technology** — Q1, broad international edtech readership, receptive to single-site deployment studies when framed modestly and when institutional implications are drawn carefully. Would require the "worldwide / dependable strategy" language in the Conclusion to be withdrawn.
3. **Australasian Journal of Educational Technology** *or* **Journal of Computing in Higher Education** — Realistic Q2 fallbacks for a single-course correlational study with honest scope limits. Named as the tier the current evidence base actually supports, so that reviewers can calibrate their recommendation to an achievable venue rather than an aspirational one.

*Deliberately excluded*: retention-specialist journals in the Tinto/Bean tradition. The paper measures course completion, not institutional persistence, and would be under-theorized for that readership.

---

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC
**Display role**: Journal-Fit Reviewer
**Identity Description**: Associate Editor of the *Journal of Learning Analytics*, researcher on student-facing feedback systems who has run multi-institutional dashboard trials and contributed to SoLAR-affiliated work on reporting standards for trace-data studies. Handles roughly 60 submissions a year and desk-rejects about a third.
**Review Focus**:
  1. **Scope and advance**: Does the paper move beyond the "adoption metrics and satisfaction" literature it criticizes in the Introduction, or does it reproduce that pattern with a retention variable attached? Is a single-course, single-term correlation a contribution an international learning-analytics readership needs?
  2. **Claim architecture at manuscript level**: Whether the Abstract, Discussion, and Conclusion make claims the Methods section cannot license. Specifically: the Abstract reports r = .42 while §4.2 reports r = .24, and the Conclusion asserts dashboards "raise" retention and constitute a "dependable" and "generalizable" strategy. At editorial level this is a question about whether the manuscript can be trusted, not only about wording.
  3. **Self-consistency of the paper's own critique**: §2 cites Ibarra (2023) on causal language outrunning correlational evidence, and §1 promises to "distinguish the pattern in the data from the causal story." The Discussion opens by saying engagement "improved" retention. Whether the paper meets the standard it sets for others.
**Will particularly care about**: Whether the discrepancy between the abstract's r = .42 and the results' r = .24 is a typographical slip or a reporting-integrity problem — because that determination decides between "major revision" and "reject."
**Possible blind spots**: Unlikely to recompute degrees of freedom or check whether a reported SD is arithmetically possible on an integer scale; tends to treat consent and data-governance issues as an ethics-office matter rather than a review criterion.

---

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1
**Display role**: Peer Reviewer 1
**Identity Description**: Quantitative methodologist in educational measurement, specializing in inference from observational LMS trace data — selection and survivorship bias, sessionization artifacts, and identification strategies for behavior–outcome associations. Routinely runs consistency checks (recomputing *df*, test statistics, and dispersion feasibility) as a first pass on any submission.
**Review Focus**:
  1. **Reporting consistency, recomputed from the stated N**: *t*(156) = 3.02 for the perceived-control comparison when the analytic sample is 142 and only 87 answered the item (implied *df* = 85); Table 2 group sizes summing to 127 against a text claim that all 142 students were classified and *t*(140); *t*(140) = 1.31 reported with p = .008 when that statistic corresponds to p ≈ .19, and the surrounding text simultaneously calls the difference non-significant; a mean of 3.847 on a 1–5 integer item; and the secondary clarity item (N = 10, M = 3.00, SD = 0.10) whose dispersion is not attainable from ten integer responses with that mean.
  2. **Design validity and who is missing**: §3.2 describes a "random sample" and then describes self-selected volunteers responding to a mid-term LMS announcement — incompatible descriptions. Because recruitment occurred mid-term and the outcome is retention, students who withdrew earliest cannot appear in the sample, biasing the association in the direction the paper reports. No response rate is given against an enrollment of "several hundred."
  3. **Analytic choices**: median split imposed on a right-skewed count variable (acknowledged but not remedied); Pearson correlation with a dichotomous outcome (point-biserial, not named); no effect sizes, confidence intervals, or covariate adjustment; multiple comparisons at α = .05 without correction; sessionization inherited from a platform default without sensitivity analysis.
**Will particularly care about**: Whether **any** inferential result in the paper survives recomputation from the reported sample sizes. This reviewer's recommendation hinges on that, not on interpretation.
**Possible blind spots**: Likely to bracket the literature-misattribution problem and the undisclosed-data-use issue as "not my section"; may under-weight whether the construct being measured is the right one in the first place.

---

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2
**Display role**: Peer Reviewer 2
**Identity Description**: Senior higher education scholar in student persistence, working in the Tinto/Bean/Braxton lineage on gateway-course attrition and on institutional research use of early-alert systems. Editorial board member of a retention-focused journal; has published on why course-level completion and institutional persistence must not be treated as the same outcome.
**Review Focus**:
  1. **Construct validity of "retention"**: The paper measures whether a student sat one final assessment in one introductory statistics course, and then concludes for "higher education institutions worldwide" that dashboards improve retention "across programs and disciplines." It also collapses two distinct non-retention pathways — formal withdrawal and enrolled-but-absent from the final — into one dichotomy, though these have different causes and different institutional remedies. The title's "course retention" and the Conclusion's institutional claim are not the same variable.
  2. **Literature accuracy and coverage**: §2 states that dashboards "have been shown to reliably improve outcomes for lower-achieving students" and attributes this to Ferro & Nakamura (2021) — a source whose listed title is "When dashboards demotivate: Peer comparison and the lower-achieving student." The cited claim appears to invert the source. Separately, 9 of 15 listed references are never cited, and the paper engages no retention theory at all (no integration, institutional commitment, or early-alert literature), despite retention being the dependent variable.
  3. **Rival explanation and genuine contribution**: The leading alternative account — that already-persisting, conscientious, higher-prior-attainment students both click more and complete more — is never named, tested, or adjusted for. Without it, the Discussion's mediation-flavored reading of perceived control has no support. What does the field learn here that Wexler & Ojo's cautionary trace-data work (listed, uncited) did not already establish?
**Will particularly care about**: Whether there is a contribution to the persistence literature that survives once the dashboard framing is set aside.
**Possible blind spots**: Less attentive to log instrumentation detail (sessionization thresholds, dashboard interface features) and to the psychometrics of single-item measures; may frame everything as a theory deficit when part of the problem is arithmetic.

---

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3
**Display role**: Peer Reviewer 3
**Identity Description**: Learning analytics ethics and student-data governance specialist with an institutional research / IT operations background — advises campuses on secondary use of trace data under GDPR-aligned and DELICATE-style frameworks, and has been on the receiving end of "encourage students to use the dashboard" mandates. Reviews from the position of the person who would have to implement the paper's recommendation.
**Review Focus**:
  1. **Consent and disclosure**: §3.2 states plainly that "students were not informed that their dashboard activity data would be analyzed for this study," while survey participants gave consent for the survey only. There is no ethics-approval or IRB statement anywhere in the manuscript, no data-minimization or retention statement, and no mention of whether students could opt out of the peer-comparison band that was displayed to all of them by default. For most target venues this is a submission requirement, not a discretionary detail.
  2. **Deployment realism of the recommendation**: The Conclusion advises institutions to invest in dashboards and "encourage students to engage with them." Operationally, the only thing measured is session count — so the recommendation reduces to increasing a click metric. This reviewer will ask what happens when an institution incentivizes that metric: whether the paper has produced an implementation lever or a gaming target, and whether §2's own caution (Vandermeer 2023: clicks are not cognitive engagement) is compatible with the advice given.
  3. **Equity and potential for harm**: The literature review reports that peer comparison can demotivate struggling students and that effects depend on goal orientation, yet the study runs no subgroup analysis by prior attainment or engagement trajectory and then recommends universal encouragement. The students the equity rationale is aimed at — early withdrawers, non-respondents, the disengaged — are precisely those the sampling design excludes. Scaling this recommendation could concentrate its risks on the population it claims to serve.
**Will particularly care about**: Whether adopting this paper's recommendation at institutional scale could harm students, and whether the manuscript gives a practitioner enough information to avoid that.
**Possible blind spots**: Will not audit the inferential statistics and may accept the reported numbers at face value; risks drifting into general policy commentary about learning analytics rather than staying anchored to what this manuscript claims.

---

## Review Strategy Recommendations

**Paper characteristics requiring particular attention**

- **Numerical contradictions must be adjudicated before interpretation.** At least five reported quantities conflict with each other or with the stated sample sizes. If reviewers debate what r = .42 means while the Results say .24, the review will be about a finding that may not exist. Sequence this first.
- **Ownership assignment to prevent quadruple-counting.** The causal-overreach problem is visible to every reviewer and will otherwise generate four near-identical paragraphs. Suggested split: the Journal-Fit Reviewer owns it at the manuscript-claims level (Abstract/Conclusion vs. Methods); Reviewer 1 owns the design-level identification argument (why cross-sectional volunteer data cannot support "raises"); Reviewer 2 owns the generalization step specifically (one course's final-exam attendance → worldwide institutional retention). Reviewer 3 does not need to restate it; their version is downstream harm.
- **Same treatment for the reference problems.** Reviewer 2 owns the Ferro & Nakamura inversion and the 9 uncited entries. Reviewer 1 should not duplicate it.
- **The paper cites the critique it commits.** Ibarra (2023) on causal language in correlational learning analytics is cited approvingly in §2. Name this once — it is the single most efficient framing for the whole revision — and do not repeat it in four voices.

**Complementarity and expected tension**

- **Tension to protect, not resolve**: Reviewers 1 and 2 will likely regard Reviewer 3's consent objection as outside the scope of scientific review. It is not — no other configured reviewer covers undisclosed secondary use of student data, and most target venues will require an ethics statement before considering the manuscript. The synthesizer should preserve this as an independent axis rather than letting the methodological majority absorb it.
- **Coverage gap in the current configuration**: no reviewer owns reporting-craft issues that are not substantive errors — excessive decimal precision, missing response rate, reference-list padding, the mismatch between the title's "course retention" and the Conclusion's institutional claim. Assign precision and response rate as secondary to Reviewer 1, reference padding and title/claim scope to Reviewer 2.
- **Cross-disciplinary load is manageable.** This paper is bi-disciplinary (learning analytics + higher education) with an ethics dimension, not the 3+ discipline case, so Reviewer 2 can hold the core field and Reviewer 3 can take the governance/practice angle without overlap.

**Register calibration**

- The volume of problems here is high, but the writing is disciplined, the Limitations section honestly names two of the three central weaknesses, and the underlying question is legitimate and publishable. Reviewers should use a **developmental register** — concrete, prioritized, and specific about what a resubmission would need. The register governs wording only; the recommendation itself must follow from the evidence against the criteria. If the numerical inconsistencies turn out to be irreconcilable rather than typographical, a constructive tone does not convert that into a revise verdict.
