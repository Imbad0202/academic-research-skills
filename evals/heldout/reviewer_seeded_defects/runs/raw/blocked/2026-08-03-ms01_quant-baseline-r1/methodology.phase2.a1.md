contract_role: methodology

## Dimension Scores

### D1: methodology_rigor
score: block
block_class: fatal
trigger: "internally contradictory reported numbers indicating the analysis as described could not have produced the stated results"

At least five independent pairs of reported quantities are mutually exclusive, and two of them are arithmetic impossibilities rather than ambiguities (a mean unattainable from the stated number of integer responses; a *t* whose degrees of freedom exceed the largest possible sample). The reported numbers therefore cannot all be a record of one analysis of one dataset, and no reader can determine which subset is authentic. A second, independent defect points the same way: the predictor accumulates over the same window in which the outcome removes students from the course, so exposure is partly a function of the outcome.

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: block
block_class: repairable
trigger: "an observational association presented as a causal or effect-producing relationship"

The Discussion and Conclusion convert a cross-sectional association into an effect ("improved", "raises", "dependable strategy") and widen the target from one statistics course to institutions worldwide. I classify this as repairable rather than fatal deliberately: a correlational restatement of whichever association is real, with the single-course scope carried into the implications, is a coherent paper. The unrepairable problem lives in D1, not here.

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

My review proceeds in an order dictated by the manuscript itself. Before any substantive finding can be assessed, the reported statistics have to be capable of coming from a single dataset. Here they are not. I reconstructed each reported test against its degrees of freedom, its stated sample, and the response scales described in Methods, and several pairs cannot both be true. The headline correlation appears as *r* = .42 in the Abstract and *r* = .24 in §4.2. The perceived-control comparison is reported as *t*(156) = 3.02 although the item was answered by at most 87 respondents, whose maximum two-group *df* is 85. The exam comparison is reported as *t*(140) = 1.31 with *p* = .008, when *t*(140) = 1.31 corresponds to *p* ≈ .19 two-tailed, and its subgroup table sums to 127 rather than the 142 the text says were classified. The perceived-control mean of 3.847 cannot be produced by 87 integer responses at all: 87 × 3.847 = 334.689, and the two attainable neighbours are 334/87 = 3.839 and 335/87 = 3.851. The secondary item reported as *N* = 10, *M* = 3.00, SD = 0.10 on an integer 1–5 scale is likewise unattainable: if the mean is exactly 3.00 every value must be 3 and SD = 0; the smallest non-zero SD available even if 3.00 is a rounded figure is ≈ 0.32. Some of this is diagnosable. The value *t* = 1.31 reconstructs almost exactly from Table 2's own cells (Δ = 2.8, SE = √(11.1²/66 + 13.0²/61) = 2.15, *t* = 1.30, *df* ≈ 125), and *r* = .24 with *n* = 142 does yield *p* ≈ .004, so the internally consistent subset appears to be Table 2's group statistics and the §4.2 correlation, with the *df*, the *p*, the Abstract's *r*, and both descriptive means being the corrupted entries. But diagnosing which numbers hang together is the authors' job, not the reviewer's, and until they do it no substantive claim in the paper can be evaluated. This is why I score D1 a fatal block: the defect is not that the analysis is weak but that the analysis as described could not have produced the reported output.

Even if every number were corrected, two design problems would remain. First, the estimator does not match the data. Retention is dichotomous, so the reported Pearson coefficient is a point-biserial correlation; that is not arithmetically illegitimate, but its attainable maximum depends on the marginal split of the outcome, and the retention base rate is never reported anywhere in the manuscript. Without it the coefficient cannot be interpreted, compared to other studies, or bounded. No logistic model, no odds ratio or risk difference, and no confidence interval appears for the headline association; a bare *p*-value is doing all the inferential work. Second, and more seriously, the predictor is contaminated by the outcome. Dashboard sessions accumulate across a 15-week term while students who are not retained stop generating sessions when they leave it, so a student who withdraws in week 6 has roughly a third of the exposure window of a completer. A positive association between session count and completion is the mechanical expectation under this design even if the dashboard has no effect whatsoever. Nothing in Methods restricts the exposure window to a period preceding the outcome, and the mid-term recruitment compounds it: students who withdrew before the announcement could never enter the sample at all, so the non-retained group consists only of late leavers.

Confounder control is absent rather than inadequate. The minimum adjustment set I would require for any claim about dashboard engagement and completion is prior achievement (institutional GPA or a placement/prerequisite score), baseline motivation or conscientiousness measured before the dashboard was used, and total non-dashboard LMS activity as a proxy for general course engagement. The third is indispensable: a diligent student clicks everything, including the dashboard, and completes the course. Without it the reported association is as compatible with "conscientious students click dashboards" as with any dashboard mechanism. None of the three is measured, modelled, or named as a threat in §5.1.

The measurement chain is thin in ways that a revision could address. Perceived control rests on a single item with no reliability or validity evidence and no defence beyond survey burden; the 30-minute session threshold is inherited from a platform default and never justified or varied, although it determines every value of the paper's key predictor; the median split discards variance in that predictor for interpretive convenience the authors themselves describe as inefficient; and the reproducibility affordances a quantitative analytics paper needs — named software, a data or code statement, a missing-data rule, the selection rule for the ten-student subsample — are all missing. There is also an ethics gap I flag as methodology reporting rather than editorial judgement: log data were analysed without informing students, and no approval or waiver statement appears.

On coherence, my angle is narrow: whether the inferential scope the design supports is honoured in the framing. It is not. The Introduction promises care in distinguishing pattern from cause, and the Discussion opens by asserting that engagement "improved" retention and that increasing it "raises the probability" of completion; the Conclusion escalates to a "dependable strategy" for "higher education institutions worldwide". Nothing in a single-course cross-sectional design licenses either the causal verb or the generalisation, and the single-course limitation acknowledged in §5.1 does not survive into §6. The Abstract also claims to have measured "self-regulated learning behavior" when Methods operationalise one perceived-control item and no behavioural regulation measure at all, and the Discussion invokes perceived control as a "mediating construct" with no mediation analysis reported.

Two matters I am not scoring but should flag for the seats that own them: the characterisation of Ferro & Nakamura (2021) in §2 as showing that dashboards "reliably improve outcomes for lower-achieving students" appears to invert a source whose title concerns demotivation, which is a literature-accuracy question; and whether "completed the final assessment" can stand in for institutional retention is a construct question I treat here only as an operational-definition issue.

### S1: Outcome coding rule is stated with enough precision to be audited
The retention variable's edge cases are handled explicitly — withdrawals and enrolled non-sitters are both coded as not retained — which is more than many trace-data studies offer and is what allowed me to identify the exposure-window problem.
**Evidence Anchor**: text: §3.3 Measures — "was coded dichotomously as whether the student remained enrolled and completed the final assessment"

### S2: Table 2 reports subgroup n, M, and SD, enabling independent reconstruction
Because both group sizes and dispersions are given, the test statistic can be recomputed by a reader. This transparency is the reason the *df* and *p* errors in the same paragraph are detectable at all, and it should be retained in any revision.
**Evidence Anchor**: table: Table 2, n and M final exam and SD columns, both engagement-group rows

### S3: Design status is declared rather than left implicit
§3.1 states the observational, cross-sectional status and explicitly notes that no student was observed across terms or courses. The design is therefore classifiable without inference, which is the precondition for any rigour assessment.
**Evidence Anchor**: text: §3.1 Design and Setting — "Because the design is cross-sectional, all measures reflect a single term and no student was observed across multiple courses or terms."

### S4: The engagement-proxy limitation is named accurately
§5.1 concedes that session counts do not capture depth or quality of engagement, in terms that match the measurement literature the paper cites. This is a correctly scoped limitation, not a ritual one.
**Evidence Anchor**: text: §5.1 Limitations — "dashboard engagement was operationalized narrowly as session counts, which does not capture the depth or quality of engagement"

### W1: Headline effect size reported at two incompatible values
The Abstract reports *r* = .42; §4.2 reports *r* = .24 for what is described as the same association. These imply roughly 18% versus 6% of shared variance and support materially different conclusions. The §4.2 pairing is internally consistent (*r* = .24, *n* = 142 → *p* ≈ .004), which suggests .42 is the error, but the authors must adjudicate. Until they do, the paper's central quantitative claim has no determinate magnitude.
**Severity**: Critical
**Evidence Anchor**: text: Abstract and §4.2 — "Dashboard engagement correlated positively with retention (r = .42)"; "Dashboard engagement was positively associated with course retention (r = .24, p = .004)"
**Confidence**: 5 — direct arithmetic comparison of two reported coefficients

### W2: Reported t(156) exceeds the maximum degrees of freedom the perceived-control sample allows
The perceived-control item was answered by 87 respondents (§4.1), giving a maximum two-independent-groups *df* of 85. A *df* of 156 implies 158 observations. The reported test cannot be the test described in Methods, so one of the two results the Abstract advertises is unverifiable in principle.
**Severity**: Critical
**Evidence Anchor**: text: §4.3 Group Comparisons — "Students in the high-engagement group reported significantly greater perceived control than students in the low-engagement group, t(156) = 3.02, p = .003."
**Confidence**: 5 — routine df-to-sample consistency audit

### W3: The predictor is contaminated by the outcome through differential exposure time
Sessions accumulate across the term; students coded not retained stop accumulating them at withdrawal. Exposure is therefore a function of the outcome, and a positive association is the null-model expectation. No pre-outcome exposure window, no offset or rate denominator, and no survival framing is used. This defect alone would justify blocking, independently of the numerical problems.
**Severity**: Critical
**Evidence Anchor**: text: §3.3 Measures — "the number of distinct sessions in which a student opened the dashboard view during the term"; "Students who withdrew before the final assessment, or who were enrolled but did not sit the final, were coded as not retained."
**Confidence**: 5 — standard survivorship and immortal-time reasoning in LMS panel data

### W4: Analytic denominators are mutually inconsistent across text, table, and test statistic
§4.3 states all 142 students were classified into engagement groups; Table 2 sums to 127 (66 + 61); the reported *df* of 140 implies 142. A further check fails to close: Table 2's weighted exam mean is 70.65 against Table 1's 71.3. The analytic sample for the exam comparison is therefore not determinable, and neither is the disposition of the 15 missing cases.
**Severity**: Major
**Evidence Anchor**: text: §4.3 Group Comparisons — "All 142 students in the primary analytic sample were classified into engagement groups for this comparison."
**Confidence**: 5 — arithmetic reconciliation of stated n against table cells

### W5: Reported p-value contradicts its own test statistic and the surrounding verbal claim
*t*(140) = 1.31 corresponds to *p* ≈ .19, not *p* = .008. The paragraph simultaneously describes the difference as small and not reaching a comparable level, which is consistent with .19 and not with .008. As printed, the exam result reads as significant at α = .05, inverting the paper's own interpretation.
**Severity**: Major
**Evidence Anchor**: text: §4.3 Group Comparisons — "the difference was small, t(140) = 1.31, p = .008"
**Confidence**: 5 — direct t-to-p verification against the reported df

### W6: Perceived-control mean is unattainable from the stated number of integer responses
87 × 3.847 = 334.689, which is not an integer; the nearest attainable means from 87 integer scores are 3.839 and 3.851. Three-decimal reporting is in any case spurious precision at 1/87 ≈ 0.012 granularity. The descriptive table thus cannot be a faithful summary of the described responses.
**Severity**: Major
**Evidence Anchor**: table: Table 1, Perceived control (1-5) row, M and SD columns
**Confidence**: 5 — closed-form check on the attainable means of integer data

### W7: Secondary-item descriptives are impossible on the stated integer scale
With ten integer responses on 1–5 and a mean of exactly 3.00, every value must be 3 and SD = 0. If 3.00 is rounded, the smallest non-zero sample SD available is ≈ 0.32 (nine 3s and one 4). SD = 0.10 is unattainable under either reading. The item is descriptive only, but the impossibility is further evidence that reported values were not computed from the data described.
**Severity**: Major
**Evidence Anchor**: text: §4.1 Descriptive Statistics — "the reported secondary-item values were N=10; M=3.00; sample SD=0.10; integer scale=1-5"
**Confidence**: 5 — enumeration of attainable integer configurations

### W8: Binary outcome analysed with a correlation coefficient, with no base rate and no interval estimate
Pearson *r* against a 0/1 outcome is a point-biserial coefficient whose ceiling depends on the outcome's marginal split, and the retention base rate is never reported. No logistic model, odds ratio, risk difference, or confidence interval accompanies the headline association. Re-analysis with an appropriate link function, a reported base rate, and an interval estimate is required before the association's magnitude can be judged.
**Severity**: Major
**Evidence Anchor**: absence: §3.4 Analysis and §4.2 Results — expected the retention base rate, a model specification appropriate to a binary outcome, and an interval estimate for the headline association; checked §3.3 Measures, §3.4 Analysis, §4.1, §4.2, Table 1, Table 2
**Confidence**: 5 — specialty in binary-outcome estimation for trace data

### W9: No confounder adjustment of any kind
The minimum adjustment set for this question is prior achievement, pre-exposure motivation, and total non-dashboard LMS activity; any of the three could drive both dashboard opening and completion. None is measured or modelled, and §5.1 does not name confounding as a limitation. The reported association is observationally equivalent to a general-diligence explanation.
**Severity**: Major
**Evidence Anchor**: absence: §3.4 Analysis — expected an adjusted model or a stated minimum adjustment set covering prior achievement, baseline motivation, and total non-dashboard LMS activity; checked §3.1 Design, §3.3 Measures, §3.4 Analysis, §4.2, §5.1 Limitations
**Confidence**: 5 — routine identification analysis for observational learning-trace studies

### W10: Sampling frame description is self-contradictory and the sample is conditioned on survival
§3.2 claims a random sample, then describes recruitment by voluntary response to an LMS announcement with non-responders excluded — these are different frames with different bias profiles. Recruitment midway through the term also excludes early withdrawers by construction. Enrollment is given only as "several hundred", so no response rate, participation rate, or attrition account can be computed.
**Severity**: Major
**Evidence Anchor**: text: §3.2 Participants and Sampling — "Participants were drawn from the course enrollment using a random sample of students enrolled in the course section"; "Students who chose to respond, and who consented to the survey, formed the study sample; those who did not respond were excluded."
**Confidence**: 5 — standard sampling-frame and non-response assessment

### W11: Single-item measures carry no reliability or validity evidence
Both self-report constructs rest on one item each, defended only by convention and survey burden. No test-retest, no convergent evidence, and no acknowledgement that a single item cannot be assessed for internal consistency. Since perceived control carries one of the paper's two headline claims, this needs either a validated multi-item scale or an explicit measurement-error argument.
**Severity**: Major
**Evidence Anchor**: text: §3.3 Measures — "single-item overall ratings are common in dashboard studies to limit survey burden"
**Confidence**: 4 — measurement-theory grounds; venue norms on single items vary

### W12: Causal claims in Discussion and Conclusion are not licensed by the design
A cross-sectional observational association is restated as an effect that "improved" retention and "raises" completion probability. No design feature — no randomisation, no instrument, no pre-post structure, no adjustment set — supports the shift. The thesis asserted is therefore not the thesis demonstrated, and the mediation language for perceived control is likewise unaccompanied by any mediation model.
**Severity**: Major
**Evidence Anchor**: text: §5 Discussion and §6 Conclusion — "The central finding of this study is that dashboard engagement improved course retention"; "This study provides evidence that engagement with a learning analytics dashboard is associated with, and raises, course retention among undergraduates."
**Confidence**: 5 — inferential-scope assessment against the stated design

### W13: Implications generalise far beyond the studied setting, and the acknowledged limitation is not carried through
§5.1 correctly limits the study to one introductory statistics course with one dashboard design; §6 then addresses institutions worldwide and claims generalisability across programs and disciplines. The word "dependable" also overstates a modest association whose magnitude is currently indeterminate.
**Severity**: Major
**Evidence Anchor**: text: §6 Conclusion — "For higher education institutions worldwide, the implication is clear: investing in student-facing dashboards and encouraging students to engage with them is a dependable strategy"
**Confidence**: 5 — comparison of stated generalisation target against the sampling frame

### W14: Abstract claims measurement of a construct that Methods never operationalise
Self-regulated learning behaviour is listed among the measured variables, but §3.3 instruments only dashboard sessions, dichotomous retention, and one perceived-control rating. A perception item is not a behavioural regulation measure. Either the construct claim is withdrawn or an SRL instrument must be reported.
**Severity**: Major
**Evidence Anchor**: text: Abstract — "we measured dashboard engagement, self-regulated learning behavior, and course persistence"
**Confidence**: 5 — direct comparison of abstract claims against the measures section

### W15: Log data analysed without notification and with no ethics statement
§3.2 states plainly that students were not told their dashboard activity would be analysed, and no approval, waiver, or consent-scope statement appears anywhere in the manuscript. Survey consent does not extend to behavioural log analysis. I checked the Methods, the article end matter, and the reference list for an approval statement and found none.
**Severity**: Major
**Evidence Anchor**: text: §3.2 Participants and Sampling — "Students were not informed that their dashboard activity data would be analyzed for this study."
**Confidence**: 4 — reporting-standard grounds; specific institutional requirements unknown to me

### W16: Median split discards information from the key predictor
Dichotomising a right-skewed count at its median costs power, attenuates the association, and makes the resulting groups sample-dependent and non-comparable across studies. The authors concede the choice is inefficient. Retaining sessions as a continuous predictor in a regression would answer the same question without the loss.
**Severity**: Minor
**Evidence Anchor**: text: §3.3 Measures — "This median split is a coarse simplification of a continuous measure and was adopted for interpretability rather than statistical efficiency."
**Confidence**: 5 — published work on the costs of dichotomising continuous predictors

### W17: Sessionization threshold is inherited from a platform default without justification or sensitivity analysis
The 30-minute inactivity rule defines every value of the paper's principal predictor, yet it is adopted because the platform supplies it. A construct decision of this weight needs either a substantive rationale or a demonstration that the association is stable across plausible thresholds.
**Severity**: Minor
**Evidence Anchor**: absence: §3.3 Measures — expected a substantive justification for the thirty-minute session threshold and a sensitivity analysis across alternative thresholds; checked §3.3 Measures, §3.4 Analysis, §4.1 Results, §5.1 Limitations
**Confidence**: 4 — trace-data operationalisation practice

### W18: Reproducibility affordances are absent
Software is described only as "standard statistical software" with no name or version; there is no data or code availability statement; missing-data handling is unstated although 55 of 142 respondents lack the perceived-control item; and the ten-student subsample is described as "selected from the survey respondents" with no selection rule. An independent analyst could not reproduce the reported figures even with the raw logs.
**Severity**: Minor
**Evidence Anchor**: absence: §3.4 Analysis and the article end matter — expected named software with version, a data and code availability statement, a missing-data rule, and the selection rule for the ten-student subsample; checked §3.2, §3.3, §3.4, §4.1, §5.1, References
**Confidence**: 5 — reproducibility checklist applied to the manuscript as submitted

### W19: The manuscript's self-description of its own inferential care is contradicted by its later sections
§1 states that the paper is careful throughout to separate pattern from cause, and §2 credits the study with transparency about its correlational scope. The Discussion and Conclusion do the opposite. This is a distinct defect from the causal overreach itself: a claim about the paper's own conduct that the paper falsifies, which misleads a skimming reader about how the results were framed.
**Severity**: Minor
**Evidence Anchor**: text: §1 Introduction — "We are careful throughout to distinguish the pattern in the data from the causal story that might explain it"
**Confidence**: 4 — internal cross-section consistency check
