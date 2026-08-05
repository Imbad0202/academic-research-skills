contract_role: methodology

## Dimension Scores

### D1: methodology_rigor

score: block
trigger: "internally contradictory numbers (Ns, degrees of freedom, subgroup totals) that cannot be reconciled and would change the reported conclusion"
block_class: fatal

### D2: domain_accuracy

score: not_assessed

### D3: argumentative_coherence

score: block
trigger: "The central conclusion is stated in causal or prescriptive terms that the reported design cannot support, and the manuscript does not qualify it"
block_class: repairable

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: not_assessed

### D6: venue_fit_and_contribution

score: not_assessed

## Review Body

I read this manuscript as a statistical reviewer, and my assessment separates into three layers: whether the reported numbers are internally consistent, whether the estimators match the data types, and whether the sample can identify the quantity the authors claim to have estimated. The manuscript fails at all three layers, and the first failure is severe enough that I cannot treat the results section as a reliable record of any analysis.

**Layer one: arithmetic reconciliation.** I attempted to reconcile every reported statistic against its stated sample and found five independent impossibilities. The headline correlation appears as *r* = .42 in the abstract and *r* = .24 in §4.2. These are not roundings of each other; at *n* = 142 they imply *t* values of 5.48 and 2.93 respectively. The reported *p* = .004 is consistent with .24, which suggests .24 is the analysis and .42 is either a stale draft value or a different analysis that is never described. A reader cannot know which number the study found. The perceived-control comparison is reported as *t*(156) = 3.02 with only 87 respondents having answered the item; an independent-samples test on 87 cases has at most 85 degrees of freedom, and even the full analytic sample of 142 caps *df* at 140. No subsetting of this dataset produces 156. The exam comparison reports *t*(140) = 1.31 with *p* = .008; for 140 degrees of freedom, *t* = 1.31 corresponds to *p* ≈ .19 two-tailed, and the narrative around it ("did not reach a comparable level", "the difference was small") is written as though the result were null, which is incompatible with the *p* value printed beside it. Table 2's group sizes sum to 127 while the same paragraph states that all 142 students were classified, and the *df* = 140 implies *n* = 142 rather than 127; a median split of 142 should also yield groups near 71/71, not 66/61. Finally, both survey means are numerically unattainable: 3.847 × 87 = 334.689, and an integer 1–5 item summed over 87 respondents must yield an integer total, so *M* = 3.847 cannot arise at *N* = 87; and an integer 1–5 item with *N* = 10 and *M* = 3.00 requires a total of exactly 30, so the sample *SD* is either 0 (all tens are 3) or at least √(2/9) ≈ 0.47, never 0.10. The three-decimal mean beside a two-decimal *SD* is a further sign that these values were not produced by a single analysis pipeline.

These are not stylistic slips. Each one indicates that a printed number does not correspond to any computation on the described sample. Individually, the *r* discrepancy and the *df* = 156 test each invalidate one of the paper's two core claims; collectively they establish that the results section cannot be audited from the text. This is what my scoring plan named as fatal for D1, and I have applied it.

**Layer two: estimator choice.** Even if the arithmetic were repaired, the analytic strategy does not match the data. Retention is a binary outcome; §3.4 reports Pearson correlation between it and a session count, so the reported *r* is a point-biserial coefficient and should be labelled as such, with logistic regression the appropriate model if the authors want an interpretable association (an odds ratio or risk difference per session, with an interval). The significance test for *r* rests on bivariate normality, which the authors themselves undercut by reporting in §4.1 that the session distribution is right-skewed with a heavy upper tail; with 0–48 sessions and a mean of 14.6, a handful of high-activity students exert substantial leverage. Neither *t*-test carries an effect size or a confidence interval, so the reader cannot judge magnitude or precision on either comparison. There is no adjustment for prior attainment or baseline LMS activity, which is the obvious confounding structure here: students who are already on track use the LMS more and complete more, and dashboard sessions are a proxy for that general activity. The median split discards the continuous predictor the authors already possess, costs power, and makes the group boundary an artifact of this sample's distribution.

**Layer three: identification.** This is the defect that would survive even a fully corrected analysis. Recruitment occurred midway through the term via an LMS announcement, and the sample consists of students who saw and answered it. A student who withdrew in week 3 cannot appear in the sample, so the retention outcome is truncated by construction: the sampling window mechanically removes early non-retention from the denominator, and it removes it non-randomly with respect to prior engagement. Whatever the association between sessions and completion is in this sample, it is conditioned on survival to the recruitment date, and the estimand the authors interpret — the association between dashboard use and course retention among enrolled students — is not identified by this design. Compounding this, §3.2 opens by describing "a random sample of students enrolled in the course section" and then, two paragraphs later, describes voluntary response to an open announcement. These are incompatible descriptions of the same recruitment, and the voluntary-response account is the operative one. Because the denominator is given only as "several hundred", no response rate can be computed, so the extent of the selection cannot even be bounded.

On argumentative coherence, my contribution is confined to inferential warrant. §1 promises that the authors "are careful throughout to distinguish the pattern in the data from the causal story that might explain it", and §2 approvingly cites a critical audit of causal language in correlational learning analytics. The Discussion then opens by asserting that dashboard engagement "improved" retention and that increasing engagement "raises the probability" of completion, and the Conclusion advises institutions worldwide that dashboard investment is "a dependable strategy". A cross-sectional observational design with a self-selected exposure, no covariate adjustment, and a survivorship-truncated outcome licenses none of this. The limitations section lists measurement coarseness, self-report bias, and single-course specificity, but omits the two threats that actually determine whether the finding means anything: the recruitment window and unmeasured confounding. This overclaim is repairable by rewriting rather than by a new study, so I have scored the block on D3 as repairable, while the D1 block is not.

I want to record what the manuscript does well, because these features made the audit above possible. The sessionization rule is stated explicitly rather than left to the reader's imagination; the retention coding names the awkward case of the enrolled-but-absent student; the authors flag their own median split as a coarse simplification; and the literature review engages the click-count critique that applies directly to their own exposure measure. That candour is real, and it is why the gap between the stated methodological self-awareness and the executed analysis is so striking.

### Strengths

**S1: Sessionization rule is operationally explicit**
**Evidence Anchor**: text: §3.3 "A session was defined as a dashboard view preceded by at least thirty minutes of inactivity"

**S2: Retention outcome definition covers the ambiguous non-sitter case**
**Evidence Anchor**: text: §3.3 "Students who withdrew before the final assessment, or who were enrolled but did not sit the final, were coded as not retained."

**S3: Discretionary dichotomization is disclosed rather than buried**
**Evidence Anchor**: text: §3.3 "This median split is a coarse simplification of a continuous measure"

**S4: Literature review names the measurement critique that applies to the authors' own exposure variable**
**Evidence Anchor**: text: §2 "click-based engagement metrics should be treated as rough indicators rather than as faithful measures"

### W1: Headline correlation is reported at two irreconcilable values

**Severity**: Critical
**Evidence Anchor**: text: §Abstract and §4.2 "Dashboard engagement correlated positively with retention (r = .42)" against "Dashboard engagement was positively associated with course retention (r = .24, p = .004)"
**Confidence**: 5 — direct arithmetic reconciliation of *r*, *n*, and *p*; the reported *p* = .004 matches .24 and not .42 at *n* = 142.

### W2: Degrees of freedom for the perceived-control test exceed any possible sample

**Severity**: Critical
**Evidence Anchor**: text: §4.3 "t(156) = 3.02, p = .003"
**Confidence**: 5 — an independent-samples test on 87 item-responders admits at most *df* = 85, and the full analytic sample of 142 caps *df* at 140.

### W3: Mid-term recruitment truncates the retention outcome, so the estimand is not identified

**Severity**: Critical
**Evidence Anchor**: text: §3.2 "Midway through the term, an announcement was posted to the course LMS inviting students to complete a short survey"
**Confidence**: 5 — standard survivorship reasoning for observational log-based samples; students withdrawing before the announcement cannot enter the denominator.

### W4: Reported *t* and *p* for the exam comparison cannot co-occur

**Severity**: Major
**Evidence Anchor**: text: §4.3 "the difference was small, t(140) = 1.31, p = .008"
**Confidence**: 5 — *t* = 1.31 at *df* = 140 gives *p* ≈ .19 two-tailed; the surrounding narrative also treats the result as non-significant.

### W5: Table 2 group sizes contradict the stated classification of all 142 students

**Severity**: Major
**Evidence Anchor**: table: Table 2, n column (66 high-engagement plus 61 low-engagement, total 127)
**Confidence**: 5 — addition against the text's classification claim; the *df* = 140 implies *n* = 142, and a median split of 142 should yield groups near 71/71.

### W6: Perceived-control mean is unattainable on an integer scale at *N* = 87

**Severity**: Major
**Evidence Anchor**: text: §4.1 "the mean perceived-control score across the 87 survey respondents who answered the item was 3.847 (SD = 0.62)"
**Confidence**: 5 — granularity check: 3.847 × 87 = 334.689, and an integer-item total must be a whole number.

### W7: Secondary-item mean and *SD* are jointly impossible

**Severity**: Major
**Evidence Anchor**: text: §4.1 "the reported secondary-item values were N=10; M=3.00; sample SD=0.10; integer scale=1-5"
**Confidence**: 5 — *M* = 3.00 at *N* = 10 forces a total of 30; the sample *SD* is then either 0 or at least √(2/9) ≈ 0.47.

### W8: Sampling is described as random and as voluntary response in the same subsection, with no computable response rate

**Severity**: Major
**Evidence Anchor**: text: §3.2 "Participants were drawn from the course enrollment using a random sample of students enrolled in the course section"
**Confidence**: 5 — the two recruitment descriptions are mutually exclusive; the enrollment denominator is given only as "several hundred".

### W9: Pearson correlation is the wrong estimator for a count-by-binary association

**Severity**: Major
**Evidence Anchor**: text: §3.4 "Associations between continuous measures were assessed with Pearson correlations."
**Confidence**: 5 — retention is dichotomous, so the coefficient is point-biserial; logistic regression with an interval is the appropriate model, and the self-reported right skew undermines the normality basis of the significance test.

### W10: No effect size or confidence interval accompanies either group comparison

**Severity**: Major
**Evidence Anchor**: absence: §4.3 group comparisons — expected a standardized mean difference with a confidence interval for each t-test; checked §3.4 Analysis, §4.2, §4.3, Table 1, Table 2, and §5.1
**Confidence**: 5 — reporting-standards check across all results surfaces.

### W11: No adjustment for prior attainment or baseline LMS activity

**Severity**: Major
**Evidence Anchor**: absence: §3.4 Analysis — expected covariate adjustment for prior attainment and baseline LMS activity; checked §3.1, §3.3, §3.4, §4.2, §4.3, and §5.1
**Confidence**: 5 — general platform activity is the obvious common cause of both dashboard sessions and completion in trace-data designs.

### W12: Median split discards the continuous predictor and creates arbitrary groups

**Severity**: Major
**Evidence Anchor**: text: §3.3 "students were split at the median number of dashboard sessions into high-engagement and low-engagement groups"
**Confidence**: 5 — dichotomizing a continuous predictor forfeits power and makes the cut point sample-dependent; a regression on the continuous measure is available.

### W13: Item nonresponse of roughly 39% on the perceived-control measure is never characterized

**Severity**: Major
**Evidence Anchor**: absence: §3.2 and §4.1 perceived-control subsample — expected a missing-data analysis comparing the 87 item-responders with the 142-student analytic sample; checked §3.2, §3.3, §3.4, §4.1, and §5.1
**Confidence**: 4 — the 87-of-142 gap is stated but its mechanism and consequences are unexamined.

### W14: No ethics approval statement, and log data were analyzed without informing students

**Severity**: Major
**Evidence Anchor**: text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study."
**Confidence**: 3 — data-governance reporting from a statistical-review standpoint; consent appears to cover only the survey, and no review-board approval is stated anywhere.

### W15: Reproducibility affordances are absent

**Severity**: Minor
**Evidence Anchor**: absence: §3.4 and end matter — expected named software with version, data and code availability, and preregistration status; checked §3.4, §4, §5.1, §6, and the reference list
**Confidence**: 5 — "standard statistical software" identifies nothing auditable.

### W16: Single-item construct measure carries no validity or reliability evidence

**Severity**: Minor
**Evidence Anchor**: text: §3.3 "Perceived control over learning was measured with a single-item overall rating"
**Confidence**: 4 — burden-reduction is a reasonable rationale, but no psychometric support or correlation with an established scale is offered.

### W17: Discussion asserts causation from a cross-sectional self-selected design

**Severity**: Major
**Evidence Anchor**: text: §5 "dashboard engagement improved course retention" and "increasing dashboard engagement therefore raises the probability that a student completes the course"
**Confidence**: 5 — inferential-warrant check against the stated design; §1 promises the opposite discipline.

### W18: Conclusion generalizes worldwide from one course section

**Severity**: Major
**Evidence Anchor**: text: §6 "investing in student-facing dashboards and encouraging students to engage with them is a dependable strategy for improving retention"
**Confidence**: 5 — directly contradicts the single-course limitation the authors themselves record.

### W19: Limitations omit the sampling window and confounding

**Severity**: Major
**Evidence Anchor**: absence: §5.1 Limitations — expected acknowledgment of mid-term recruitment truncating the retention outcome and of unmeasured confounding by prior attainment; checked §5, §5.1, and §6
**Confidence**: 5 — the listed limitations are the mild ones; the two threats that govern interpretation are unlisted.
