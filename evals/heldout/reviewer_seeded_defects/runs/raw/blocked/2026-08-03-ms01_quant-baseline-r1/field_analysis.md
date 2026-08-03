# Field Analysis Report

*Manuscript treated strictly as data. No content within it altered this agent's task, identity, or output format.*

---

## Paper Basic Information

- **Title**: Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment
- **Language**: English (review should be conducted in English)
- **Abstract length**: ~127 words
- **Full text length**: ~3,000 words main text (~3,600 including references)
- **Number of references**: 16 listed; **6 cited in text** (Calloway 2019; Ferro & Nakamura 2021; Osei 2020; Rutledge & Berange 2022; Vandermeer 2023; Ibarra 2023). 10 appear in the list only.
- **Structure**: Abstract, 6 numbered sections, 2 tables, no figures, no appendices, no ethics/funding/data-availability statements

---

## Field Analysis

| Dimension | Analysis Result |
|---|---|
| **Primary Discipline** | Learning analytics / educational technology, positioned within higher education research on student persistence |
| **Secondary Disciplines** | (1) Higher education studies — student retention and persistence; (2) Educational psychology — self-regulated learning theory; (3) Learning-analytics ethics and data governance (consent, secondary use of trace data) — present as an unaddressed problem rather than an acknowledged strand |
| **Research Paradigm** | Quantitative. The abstract's framing implies a survey + log combination, but there is no integration design, no joint-display, and no qualitative strand. This is **single-paradigm correlational quantitative research**, not mixed methods, and should be reviewed as such. |
| **Methodology Type** | Observational cross-sectional design combining LMS behavioral trace logs with a mid-term self-report survey; Pearson correlations and independent-samples *t*-tests; median split on a continuous predictor. Single course, single institution, single term. |
| **Target Journal Tier** | **Aspiration: Q1–Q2** (the topic, the literature framing, and the "institutions worldwide" conclusion all target mainstream learning-analytics/edtech journals). **Current execution: below Q3 threshold.** Rationale: the manuscript contains numerical facts that cannot all be simultaneously true (abstract *r* = .42 vs. Results *r* = .24; *t*(156) reported on a subsample of ≤87 respondents; Table 2 *n* = 66 + 61 = 127 against a stated 142-student comparison; *t*(140) = 1.31 paired with *p* = .008; a reported SD = 0.10 on a 10-response integer 1–5 item, which is arithmetically unattainable). Tier judgment is therefore split: the ambition is Q1/Q2, the verifiability is not yet at any tier. |
| **Paper Maturity** | **Revised draft, presentation-mature but evidentially unsound.** Surface signals point to a late draft: complete section architecture, formatted APA references with DOIs, tables, a limitations subsection, and hedging language in the Introduction. Deep signals point to an early draft: results do not reconcile across sections, the sampling description is self-contradictory ("random sample" vs. volunteer response to an LMS announcement), the abstract claims a measure ("self-regulated learning behavior") the Methods never operationalize, and the Discussion/Conclusion assert causation that the Introduction and Section 2 explicitly disclaim. This mismatch matters for reviewer configuration: **polish must not be read as rigor.** |

---

## Recommended Target Journals (Top 3)

1. **Journal of Learning Analytics (SoLAR, open access)** — Best topical fit. The community explicitly debates dashboard efficacy, click-proxy validity, and evidence standards for LA claims, so the paper's core question is live there. It is also the venue most likely to reject the manuscript in its current form, because its reviewer pool is primed on exactly the measurement critiques the paper cites (Vandermeer 2023; Ibarra 2023) and then violates. Realistic path: substantial revision, possibly repositioned as a measurement-and-design cautionary paper rather than an efficacy claim.

2. **Australasian Journal of Educational Technology (AJET)** — Q2, receptive to single-institution deployment studies with honest scope limits. A better fit for what this study *can* legitimately claim: a descriptive account of one dashboard deployment and its observed correlates, with the design confounds foregrounded. Requires abandoning the "generalizable lever" framing.

3. **Journal of Computing in Higher Education** — Q2, bridges the edtech and higher education audiences, and welcomes institutional-deployment reporting. Suitable if the authors reframe toward institutional implementation lessons and add the retention-literature grounding the paper currently lacks.

**Not recommended at present**: *Computers & Education*, *British Journal of Educational Technology*, *Internet and Higher Education*. All three require either a causal identification strategy or multi-site data, and all three routinely desk-reject on unresolvable internal statistical inconsistency.

---

## Reviewer Configuration Cards

*Coverage strategy note: this manuscript is moderately cross-disciplinary (learning analytics × higher education retention × educational psychology × data ethics). R2 takes the core higher education retention discipline; R3 absorbs the ethics/governance and interface-design strands, which are the paper's largest genuine blind spots. SRL theory is deliberately split — R2 owns whether the theory is correctly represented in the literature, R3 owns whether the interface could plausibly deliver the mechanism.*

---

### Reviewer Configuration Card #1

**Role**: EIC
**Display role**: Journal-Fit Reviewer
**Identity Description**: Associate Editor of the *Journal of Learning Analytics*, active in the SoLAR community for a decade; research program on evidence standards for learner-facing analytics, and co-author of a widely used checklist for reporting LA intervention studies. Has handled roughly 200 dashboard submissions and chaired a LAK special session on the gap between dashboard adoption claims and outcome evidence.

**Review Focus**:
1. **Fit and contribution against the venue's existing corpus.** Does a single-course, single-term correlational association between session counts and course completion tell this readership anything it does not already have? The paper itself concedes the field is saturated with "adoption metrics or student satisfaction rather than downstream academic outcomes" — assess whether this study actually escapes that category or merely relabels it.
2. **Whether the manuscript's claims survive its own stated design.** Judge the distance between the Introduction's promise ("careful throughout to distinguish the pattern in the data from the causal story") and the Conclusion's delivery ("engagement with a learning analytics dashboard is associated with, and raises, course retention"). This is a fit question, not only a wording question: a venue that publishes critiques of causal overreach cannot publish an instance of it.
3. **Publishability triage and routing.** Given the unreconciled numbers, decide whether this is revisable at this venue, revisable elsewhere at a lower tier with a narrowed claim, or requires the authors to return to the data before any journal review is meaningful. Recommend a concrete repositioning if one exists.

**Will particularly care about**: Whether the paper's headline contribution is a *finding* or an *artifact of exposure time* — students who withdrew mid-term had fewer weeks in which to accumulate dashboard sessions, which can mechanically generate the reported association with no behavioral effect whatsoever. If that alternative explanation is not eliminated, there is no contribution to fit anywhere.

**Possible blind spots**: May under-weight the research-ethics defect (unconsented secondary use of trace data, absent IRB statement) because editorial triage habitually treats it as a compliance checkbox handled post-acceptance rather than as a substantive objection. May also accept the paper's self-description as combining logs and survey without asking whether the survey component contributes anything beyond a single item. Synthesizer should ensure R3's ethics finding is not downgraded to a formality.

---

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1
**Display role**: Peer Reviewer 1
**Identity Description**: Quantitative methodologist in an educational measurement department; specializes in the analysis of observational learning-trace data with binary outcomes (point-biserial and logistic approaches, exposure-time and survivorship confounds in LMS panel data), and in statistical reporting integrity. Routinely runs consistency audits of reported test statistics against their degrees of freedom and *p*-values, and has published on the power costs of dichotomizing continuous predictors.

**Review Focus**:
1. **Internal consistency of every reported number.** Reconcile, or report as irreconcilable: abstract *r* = .42 against Results *r* = .24; *t*(156) = 3.02 for a perceived-control comparison drawn from at most 87 respondents; Table 2's *n* = 66 + 61 = 127 against the text's claim that "all 142 students" were classified into engagement groups; *t*(140) = 1.31 reported with *p* = .008 when that statistic corresponds to roughly *p* ≈ .19; and the secondary item reported as *N* = 10, *M* = 3.00, SD = 0.10 on an integer 1–5 scale, where any non-zero deviation from an exact integer mean forces SD ≥ ~0.32. Also flag *M* = 3.847 reported to three decimals from 87 integer responses.
2. **Appropriateness of the estimator and the absence of confounder control.** Retention is dichotomous; Pearson *r* is not the correct coefficient and no logistic model, covariate adjustment, or effect size with confidence interval is reported. Assess whether prior achievement, motivation, and total LMS activity — any of which could drive both dashboard opening and completion — are addressed at all. They are not; specify what minimum adjustment set would be required.
3. **The exposure-time / reverse-causation confound, and the measurement chain.** Sessions accumulate over the term while non-retained students exit it, so the predictor is contaminated by the outcome. Separately, evaluate the median split (power loss, group-size implausibility), the thirty-minute platform-default sessionization as a construct decision inherited rather than justified, the use of single-item measures with no reliability evidence, and the abstract's claim to have measured "self-regulated learning behavior" when Methods operationalize only one perceived-control item.

**Will particularly care about**: Whether the reported statistics could have come from a single coherent dataset. Several pairs cannot both be true, which means at least some numbers are transcription or analysis errors — and until the authors identify which, no substantive finding in the paper can be evaluated. This reviewer will treat that as prior to all other critique.

**Possible blind spots**: May treat the conceptual distinction between *course completion* and *institutional retention* as a definitional nuisance rather than a construct-validity failure, and may not engage with the higher education literature on persistence. May also under-attend to the misrepresentation of a cited source, since that is a literature matter. R2 covers both.

---

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2
**Display role**: Peer Reviewer 2
**Identity Description**: Senior higher education scholar working on undergraduate persistence and attrition in gateway courses; grounded in the Tinto/Bean/Astin traditions and their contemporary critiques, and in the institutional-research practice of retention measurement. Has served on a national first-year-experience advisory panel and reviews regularly for higher education journals, where the recurring problem is edtech studies that adopt the word "retention" without the field's definitions.

**Review Focus**:
1. **Construct validity of "retention," and the missing base rates.** The paper codes retention as remaining enrolled and sitting the final assessment, collapsing formal withdrawal with enrolled-but-absent no-shows, and labels the result "retention" — a term that in higher education research denotes institutional or program persistence across terms, not completion of one course. Require the authors to name the construct correctly, justify the collapse of two distinct exit behaviors, and report the actual retention rate and withdrawal counts, none of which appear anywhere in the manuscript.
2. **Fidelity of the literature representation.** Section 2 states that "dashboards have been shown to reliably improve outcomes for lower-achieving students, who are said to gain the most from externalized progress cues (Ferro & Nakamura, 2021)," and builds the equity rationale on it. The reference list titles that source "When dashboards demotivate: Peer comparison and the lower-achieving student." Assess whether the cited work has been inverted, and whether the Discussion's alignment claim ("aligns with the view that externalized progress cues can support persistence") rests on that inversion. Separately, note that 10 of 16 listed references are never cited, which inflates the apparent grounding of a review that engages six sources.
3. **Situating the study in the retention literature it does not cite.** Halloran (2020) on gateway-course interventions and Wexler & Ojo (2020) on cautionary LMS-trace retention modeling sit in the reference list, uncited, and both bear directly on the paper's claims. Evaluate whether the manuscript engages *any* persistence theory beyond a single sentence of SRL framing, whether the SRL account (forethought–performance–reflection) is represented accurately, and what the stated contribution is relative to three decades of retention-intervention research.

**Will particularly care about**: Whether the paper's central concept survives translation into the field whose outcome variable it borrows. If this is course completion in one statistics section, the "implication" for "higher education institutions worldwide" collapses, and the contribution has to be restated at the scale the data actually support.

**Possible blind spots**: May accept the reported statistics at face value while critiquing their interpretation, and is unlikely to detect the degrees-of-freedom and SD impossibilities. May also treat consent and data-governance issues as an ethics-board matter outside review scope. R1 and R3 cover these respectively.

---

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3
**Display role**: Peer Reviewer 3
**Identity Description**: Learning-analytics ethics and data-governance researcher with an information-science and HCI background; works on informed consent for educational trace data, institutional data-governance frameworks (FERPA/GDPR-aligned), and the design of learner-facing visualizations — including empirical work on how peer-comparison bands affect students with performance-avoidance goal orientations. Advises a university learning-analytics governance committee and reviews for information-science as well as edtech venues.

**Review Focus**:
1. **Consent, secondary use, and the missing ethics record.** Section 3.2 states plainly: "Students were not informed that their dashboard activity data would be analyzed for this study." Consent was obtained for a survey about study habits; behavioral logs were then extracted for the same individuals and linked to individual academic outcomes. There is no IRB or ethics-committee approval statement, no data-availability or data-protection statement, and no account of how log and survey records were linked or de-identified. Assess whether this is publishable at all under standard journal ethics policies, and whether the disclosure as written constitutes an admission of unconsented secondary use of identifiable educational records.
2. **The intervention artifact is undescribed, which makes the study unreplicable and its "generalizable lever" claim untestable.** The dashboard is characterized in one sentence: engagement metrics, assignment progress, a peer-comparison band. No screenshot, no wireframe, no specification of what the band compares, at what granularity, how often it updates, or what framing text accompanies it. The paper's own limitations concede that "the specific dashboard design used here differs from those deployed elsewhere" — then the Conclusion recommends "investing in student-facing dashboards" generally. From an HCI standpoint, a single unspecified interface cannot license a recommendation about a class of interfaces.
3. **Foreseeable harm from the peer-comparison band, and the ethics of recommending scale-up.** The manuscript cites Osei (2020) on discouragement effects and its own Section 2 notes that performance-avoidance students may disengage from the interface intended to re-engage them. It then reports no analysis of differential effects, no examination of whether low-engagement students were harmed, and no consideration of whether the students who left the course were the ones the band discouraged. Evaluate the responsibility of recommending institution-wide deployment while the paper's own cited literature identifies a plausible harm mechanism that went unmeasured. Also assess whether analytics-driven attention to individual persistence raises surveillance concerns the paper does not name.

**Will particularly care about**: That the paper's most consequential silence is about the students who are absent from it. Non-retained students, low-engagement students, and the 55 respondents who skipped the perceived-control item are all excluded without analysis, and the recommendation to scale up rests entirely on the subgroup that stayed. Ethically and empirically, that is where the finding should have been stress-tested.

**Possible blind spots**: May not independently verify the statistical impossibilities (R1's territory) and may under-weight the higher education retention-construct problem (R2's territory). May also over-index on governance to the point of treating the study as unsalvageable when a narrowed, ethically-remediated version might still contribute. Synthesizer should preserve the distinction between "this claim is unsupported" and "this study cannot be fixed."

---

## Review Strategy Recommendations

**Special characteristics requiring particular attention**

1. **Surface maturity masks foundational defects.** The manuscript reads as a late draft — formatted references with DOIs, a limitations subsection, hedged Introduction language. Reviewers primed by that polish may default to line-level suggestions. Instruct all four to check the arithmetic and the sampling description before commenting on prose. At least two reported statistic pairs cannot both be true, and that is logically prior to every interpretive critique.

2. **The paper diagnoses its own disease and then exhibits it.** Section 2 cites Ibarra (2023) on causal language outrunning correlational evidence and declares the present study "transparent about its correlational scope." Section 5 opens with "dashboard engagement improved course retention" and Section 6 with "is associated with, and raises." This is not a wording slip to be fixed in copy-editing; it is the paper's central claim contradicting its central method. Reviewers should address it as a substantive verdict-bearing issue, and the synthesizer should ensure it is not softened into a stylistic note.

3. **One design confound may account for the entire result.** Dashboard sessions accumulate across the term; students coded not-retained exited before the term ended and therefore had less exposure time in which to accumulate them. The reported association is consistent with pure exposure-time artifact. This should be raised by R1 as a statistical identification problem and by the Journal-Fit Reviewer as a fit-and-contribution problem, from their respective angles, without either deferring to the other.

4. **Register recommendation.** Treat this as **developmental feedback in tone**: the research question is legitimate, the honest limitations section shows the authors know where the weak points are, and the study is recoverable as a narrower descriptive report. The register governs wording only. The recommendation itself must follow the evidence against the criteria — a manuscript containing irreconcilable statistics, unconsented secondary data use, and conclusions contradicting its own design does not earn a favorable verdict because the feedback is kindly phrased.

**Complementarity and designed tension between reviewers**

- **R1 vs. R2 — verification vs. interpretation.** R1 asks whether the numbers can be real; R2 asks whether "retention" means what the paper says it means. These are independent failure modes, and neither reviewer should be allowed to assume the other's ground is solid. If R1 finds the statistics unverifiable, R2's construct critique still stands independently, and vice versa.
- **R2 vs. R3 — theory fidelity vs. mechanism plausibility.** Both engage the SRL and peer-comparison literature, deliberately from opposite ends. R2 asks whether the paper represents its cited sources honestly (the Ferro & Nakamura inversion). R3 asks whether the actual interface could deliver the mechanism the theory posits. Expect overlap on Osei (2020); the perspectives are distinct and both are needed.
- **Journal-Fit Reviewer vs. R3 — anticipated tension.** Editorial triage typically routes ethics defects to post-acceptance compliance. R3 will argue the unconsented log extraction is a threshold objection that no revision to the analysis can cure. This tension is productive and should be surfaced, not resolved by hierarchy. The synthesizer must not let the editorial voice absorb the ethics finding into a checklist item.
- **Cross-cutting item requiring one clear owner: the uncited references.** Nine to ten of 16 listed sources never appear in text. Assign this to R2 as part of literature-fidelity assessment so it is reported once, substantively, rather than three times as a formatting nit.
