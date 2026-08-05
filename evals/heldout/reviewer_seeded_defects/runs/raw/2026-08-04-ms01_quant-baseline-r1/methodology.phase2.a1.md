contract_role: methodology

## Dimension Scores

### D1: methodology_rigor
score: block
block_class: fatal
trigger: "an outcome measured before or contemporaneously with the exposure it is claimed to follow"

Two independent grounds converge here. First, the reported inferential and descriptive statistics cannot have been computed from the sample the manuscript describes: one *t*-test implies *n* = 158 against a stated analytic sample of 142 and an item-level *n* of 87; a second *t*-test reconciles arithmetically with Table 2's *n* = 127 while being reported with df = 140 and a *p*-value off by a factor of roughly 24; and two descriptive statistics are arithmetically unobtainable from integer response scales at the stated sample sizes. Second, and the reason this is fatal rather than repairable, the exposure (cumulative dashboard sessions across the term) accrues only while a student remains enrolled, while the outcome (completing the final assessment) is what terminates accrual — the exposure window is truncated by the outcome event, so part of the reported engagement-retention association is definitional. This is compounded by a mid-term voluntary recruitment window that structurally excludes students who had already withdrawn. No re-analysis of this sample can separate the empirical from the mechanical component; recovering the stated estimand would require a full-cohort log extraction, a time-anchored exposure window closed before any withdrawal, and baseline covariates — a different study, not a revision.

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: block
block_class: repairable
trigger: "causal, effectiveness, or policy-prescriptive language resting on associational evidence without the required identification argument"

The Introduction promises to "distinguish the pattern in the data from the causal story," and the Discussion's opening sentence abandons that promise, asserting that engagement "improved course retention" and "raises the probability that a student completes the course." The Conclusion escalates further to unconditional institutional prescription across "programs and disciplines" worldwide from a single lecture section of one introductory statistics course, with no covariates and no identification argument. Separately, the Abstract's headline *r* = .42 contradicts the Results' *r* = .24. I score this repairable because the claim-to-evidence link can be restored by rewriting the Discussion and Conclusion in associational terms and reconciling the Abstract — a rewriting task. That repairability is conditional on the reported quantities being real, which is the D1 question and is not settled.

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I recomputed every reported statistic in this manuscript before assessing any substantive claim. The results of that reconciliation determine my review, so I state them first.

Three reported quantities reconcile. The primary correlation is one of them: *r* = .24 at *n* = 142 gives *t* = 2.93 on 140 df and *p* = .004, exactly as reported. The perceived-control *t* and *p* are mutually consistent with each other (*t* = 3.02 at df = 156 gives *p* = .003), and the exam-comparison *t* is exactly reproducible from Table 2's cell means and SDs (pooled *s* = 12.05, SE = 2.14, *t* = 1.308).

Everything else fails. The perceived-control comparison's df = 156 implies *n* = 158 for an independent-samples test, but only 87 respondents answered that item (df should be 85) and the entire analytic sample is 142. The exam comparison's *t* = 1.31 is reproducible from Table 2 — but Table 2's groups sum to 127, giving df = 125, not the reported 140, and the text's assertion that "All 142 students in the primary analytic sample were classified into engagement groups" is contradicted by the analysis the authors evidently ran. At *t* = 1.31 on either 125 or 140 df, two-tailed *p* ≈ .19, not the reported .008; the sentence simultaneously reports a *p*-value well below the stated alpha of .05 and describes the difference as not reaching significance, so the number and its own interpretation contradict each other. The perceived-control mean of 3.847 cannot be produced by 87 integer responses (87 × 3.847 = 334.69, and the attainable neighbours are 3.839 and 3.851); no other sample size in the manuscript — 142, 127, or the 158 implied by df = 156 — yields an integer sum either. The secondary clarity item reports *N* = 10, *M* = 3.00, sample *SD* = 0.10 on a 1-5 integer scale; if the ten integers average exactly 3.00, the deviations are integers summing to zero, so either all responses equal 3 and *SD* = 0, or at least two deviate and the sum of squared deviations is at least 2, giving *SD* ≥ 0.471. A value of 0.10 is unobtainable from any integer dataset satisfying the stated *N* and *M*. And the Abstract's *r* = .42 is not the *r* = .24 reported in §4.2; these differ in both digits, so a transcription slip is not the obvious explanation.

Individually, any one of these could be a typographical error. Collectively the pattern is diagnostic rather than clerical: the reported statistics correspond to at least three mutually incompatible sample sizes (127, 142, 158), and two of them correspond to no possible dataset on the described scales. This is why I cannot evaluate a single substantive finding in the paper. The editorial request that follows from it is the raw analysis output and variable-level data dictionary, not a corrected proof.

The design problem is independent of the arithmetic and is the more serious of the two. Section 3.2 makes two incompatible statements about the sampling frame in adjacent paragraphs: participants were "drawn from the course enrollment using a random sample," and participants were volunteers who responded to a mid-term LMS announcement. These cannot both be true, and the recruitment paragraph is the operative one. Because recruitment occurred mid-term and logs were pulled only "for the same set of respondents," students who withdrew before the announcement cannot be in the sample at all, so the denominator for retention is a survivorship-filtered subset of the enrolled cohort. Worse, the exposure measure is a cumulative count over "the term," but a student who leaves in week 9 accumulates sessions for nine weeks while a completer accumulates for fifteen. The non-retained students are, by construction, students with a shorter observation window and therefore a mechanically lower session count. Some unknown share of *r* = .24 is exposure-window length, not engagement. The manuscript never reports the retention base rate, which compounds the problem: the maximum attainable point-biserial correlation is bounded by the marginal split of the dichotomous outcome, so a reader cannot even judge whether .24 is small or near-ceiling.

Reverse causality is untreated and plausible in both directions — students who are already on track to complete may check a progress dashboard more often precisely because the news is good — and there is no covariate of any kind (prior attainment, credit load, major, concurrent course load) anywhere in the analysis, in a course explicitly described as serving "a range of majors." The Limitations section is silent on all three of selection, survivorship, and reverse causation, while listing the narrowness of the session-count proxy, self-report bias, and single-course generalisability.

On analytic adequacy: a dichotomous outcome is correlated with a continuous predictor using Pearson's *r* without being named point-biserial and without a logistic model that could have carried covariates; a right-skewed predictor is median-split with the skew acknowledged and not remedied; no effect size, confidence interval, or power analysis appears anywhere; and the exposure definition rests entirely on the platform's default 30-minute inactivity rule with no sensitivity check, even though the session count is the paper's independent variable and that threshold is an artefact of vendor configuration. Both headline constructs are single-item measures with no reliability or validity evidence, justified by appeal to convention.

Finally, two provenance matters that fall inside methodological rigor rather than presentation. The manuscript states that "Students were not informed that their dashboard activity data would be analyzed for this study," and there is no ethics-approval or IRB statement anywhere in the submission. Whether the consent obtained for the survey extends to secondary analysis of behavioural logs is an editorial and ethics-board determination, but it must be made before publication. And nothing in the submission supports independent verification: the software is described only as "standard statistical software," there is no code, no data availability statement, and no accounting of the item non-response that took the perceived-control analysis from 142 respondents down to 87.

I have not assessed the adequacy of the self-regulated learning framing, the accuracy of the cited literature, or venue fit; those belong to other seats. My verdict is confined to whether the numbers are internally consistent and whether the design can bear the reported estimand, and on both counts it cannot.

### S1: Design type and temporal scope stated without hedging
The manuscript labels itself observational and cross-sectional in its first Methods sentence and draws the correct consequence in the same paragraph. This is the disclosure that makes the Discussion's causal language diagnosable as overreach rather than ambiguity.
**Evidence Anchor**: text: §3.1 "Because the design is cross-sectional, all measures reflect a single term and no student was observed across multiple courses or terms."
**Confidence**: 5 — direct reading of an explicit design statement.

### S2: Outcome operationalisation covers the non-obvious case
Retention is defined dichotomously and, unusually, explicitly handles students who remained enrolled but did not sit the final. Most trace-data retention studies leave this case implicit, and the explicit rule is what allowed me to identify the exposure-window truncation problem.
**Evidence Anchor**: text: §3.3 "Students who withdrew before the final assessment, or who were enrolled but did not sit the final, were coded as not retained."
**Confidence**: 5 — the definition is stated verbatim.

### S3: Recruitment mechanism reported honestly enough to be audited
Despite the contradictory "random sample" sentence, the recruitment paragraph describes voluntary response accurately and names the recruitment window. Authors frequently omit this; here the disclosure is what makes the selection mechanism assessable at all.
**Evidence Anchor**: text: §3.2 "Because participation depended on students electing to answer the announcement, the resulting sample reflects those who volunteered during the recruitment window."
**Confidence**: 4 — clear text, though it contradicts the sampling sentence above it.

### S4: The primary correlation reconciles with its stated sample size
Of the reported inferential results, the headline correlation is the one that survives recomputation: *r* = .24 with *n* = 142 yields *t* = 2.93 on 140 df, *p* = .004, matching the reported value. This is worth stating explicitly because it isolates the failures to the group comparisons and descriptives.
**Evidence Anchor**: text: §4.2 "(r = .24, p = .004)"
**Confidence**: 5 — recomputed directly.

### S5: Introduction commits to the correct inferential register
The Introduction states the correlational scope of the design and names the literature's causal-language problem, which is the right frame for this evidence. The commitment is not kept later, but it is correctly made.
**Evidence Anchor**: text: §1 "We are careful throughout to distinguish the pattern in the data from the causal story that might explain it"
**Confidence**: 5 — explicit statement.

### W1: Perceived-control t-test has degrees of freedom exceeding every stated sample size
The reported *t*(156) = 3.02 is internally consistent with its own *p* = .003, which means it was computed on a sample of 158 for an independent-samples test. Only 87 respondents answered the perceived-control item, implying df = 85, and the entire primary analytic sample is 142. There is no sample of 158 anywhere in the manuscript. This is not a plausible transcription of 85, and the result is one of the two findings advertised in the Abstract.
**Severity**: Critical
**Evidence Anchor**: text: §4.3 "t(156) = 3.02, p = .003"
**Confidence**: 5 — arithmetic recomputation against sample sizes stated in the same manuscript.

### W2: Exam-comparison p-value is incompatible with its own t and df, and with its own verbal interpretation
At *t* = 1.31 on 140 df, two-tailed *p* ≈ .19; the reported *p* = .008 is off by roughly a factor of 24. The sentence simultaneously reports a value below the stated alpha of .05 and characterises the comparison as not reaching significance, so the number contradicts the interpretation attached to it. The *t* itself is exactly reproducible from Table 2 (pooled *s* = 12.05, SE = 2.14, *t* = 1.308), which means the test statistic is real and the df and *p* reported alongside it are not.
**Severity**: Critical
**Evidence Anchor**: text: §4.3 "the difference was small, t(140) = 1.31, p = .008"
**Confidence**: 5 — recomputed from the manuscript's own Table 2 cell statistics.

### W3: Analytic sample for the exam comparison is unreconciled across text, table, and degrees of freedom
Table 2's groups sum to 127 (66 + 61), the text states that all 142 students were classified into engagement groups, and the reported df = 140 implies 142. Fifteen students are unaccounted for, with no exclusion or missingness statement. The same gap appears upstream: 142 provided complete data but only 87 answered a single-item measure, a 39% item non-response that is never reported as such or characterised in any way. Without an exclusion flow, the analysed population for each reported test is unknown.
**Severity**: Major
**Evidence Anchor**: table: Table 2 (Final exam comparison by engagement group), n column
**Confidence**: 5 — direct arithmetic on the table against the text.

### W4: Secondary-item standard deviation is arithmetically unobtainable
With *N* = 10 integer responses on a 1-5 scale averaging exactly 3.00, the deviations from the mean are integers summing to zero. Either all ten responses are 3 and *SD* = 0, or at least two deviate, forcing the sum of squared deviations to at least 2 and the sample *SD* to at least 0.471. No integer dataset satisfying the stated *N* and *M* can produce *SD* = 0.10. Either the scale is not integer as described, the mean is not 3.00, or the statistic was not computed from these data.
**Severity**: Major
**Evidence Anchor**: text: §4.1 "the reported secondary-item values were N=10; M=3.00; sample SD=0.10; integer scale=1-5"
**Confidence**: 5 — closed-form arithmetic bound on integer data.

### W5: Perceived-control mean is unattainable at the stated sample size and is reported to spurious precision
A mean of 87 integer responses must equal an integer divided by 87; 87 × 3.847 = 334.69, and the attainable neighbouring means are 3.839 and 3.851. Substituting any other sample size in the manuscript does not rescue it (142 → 546.27; 127 → 488.57; 158 → 607.83). Separately, three-decimal reporting of a single-item integer measure implies a precision the instrument cannot deliver, and the combination of *SD* = 0.62 with observed values at both 1 and 5 in Table 1 is tight enough to warrant checking against the raw distribution.
**Severity**: Major
**Evidence Anchor**: text: §4.1 "The mean perceived-control score across the 87 survey respondents who answered the item was 3.847"
**Confidence**: 5 — divisibility check on integer-scale data.

### W6: Abstract reports an effect size that does not appear in the Results
The Abstract's *r* = .42 is roughly 75% larger than the *r* = .24 reported in §4.2, and the two values do not share digits in a way that suggests transposition. The Abstract is the number that will be cited and the number the Conclusion's policy claim rests on. Until it is reconciled, readers cannot know which analysis, if either, was run.
**Severity**: Major
**Evidence Anchor**: text: Abstract "Dashboard engagement correlated positively with retention (r = .42)"
**Confidence**: 5 — direct comparison of two stated values.

### W7: Exposure window is truncated by the outcome, making part of the association definitional
Dashboard sessions are counted cumulatively across the term, but a student coded as not retained stopped accruing sessions when they left. Non-retained students therefore have shorter observation windows by construction, and their lower session counts are partly an artefact of that truncation rather than evidence of differential engagement. The mid-term recruitment window compounds this: students who withdrew before the announcement could not respond and are structurally absent, so the retention outcome's variance is already survivorship-filtered before analysis begins. Neither problem is remediable within this sample; a fixed pre-recruitment exposure window applied to full-cohort logs would be required, and those logs were pulled only for respondents.
**Severity**: Critical
**Evidence Anchor**: text: §3.3 "the number of distinct sessions in which a student opened the dashboard view during the term"; §3.2 "Midway through the term, an announcement was posted to the course LMS inviting students"
**Confidence**: 5 — follows directly from the stated exposure and outcome definitions and the recruitment timing.

### W8: Sampling frame is described in two mutually exclusive ways
Section 3.2 states that participants were drawn "using a random sample of students enrolled in the course section" and, in the next paragraph, that the sample consists of students who chose to respond to an LMS announcement. These are different sampling designs with different inferential warrants, and only the second is consistent with the exclusion rule that follows it. As written, the sampling frame is unknown, so no reported quantity can be referred to any defined population.
**Severity**: Major
**Evidence Anchor**: text: §3.2 "using a random sample of students enrolled in the course section"
**Confidence**: 5 — two statements in the same subsection cannot both hold.

### W9: Discussion and Conclusion assert causation and institutional policy from a cross-sectional correlation
The Discussion's opening sentence states that engagement "improved course retention" and that increasing it "raises the probability that a student completes the course." The Conclusion generalises to institutions "worldwide" and calls dashboards "a dependable strategy for improving retention across programs and disciplines." Nothing in the design supports a counterfactual claim: there is no manipulation, no covariate adjustment, no instrument, and no temporal separation between exposure and outcome. The paper's own Introduction and its cited critique of causal overreach in this literature make the gap self-inflicted rather than inadvertent.
**Severity**: Critical
**Evidence Anchor**: text: §5 "dashboard engagement improved course retention"; §6 "is a dependable strategy for improving retention across programs and disciplines"
**Confidence**: 5 — direct comparison of claim language against the stated design.

### W10: Dichotomous outcome analysed as a Pearson correlation with no model and no reported base rate
Retention is binary, so the reported *r* is a point-biserial coefficient; it is neither named as such nor accompanied by the marginal split that bounds its maximum attainable value. The retention base rate is never reported anywhere in the manuscript, so a reader cannot tell whether .24 is modest or near its ceiling given the outcome distribution. A logistic regression would have been the appropriate model and would also have provided the vehicle for covariate adjustment; none is fitted.
**Severity**: Major
**Evidence Anchor**: text: §3.4 "Associations between continuous measures were assessed with Pearson correlations."
**Confidence**: 5 — standard property of point-biserial correlation with a dichotomous variable.

### W11: No covariate of any kind enters the engagement-retention analysis
The course explicitly serves multiple majors, yet no prior attainment measure, credit load, major, concurrent enrolment, or demographic variable is measured or adjusted for. Students with stronger prior preparation plausibly both check progress displays more and complete at higher rates, which is a straightforward confounding path the design leaves entirely open. Reverse causality is equally unaddressed: on-track students may consult a dashboard more because the feedback is favourable. The Limitations section names none of these.
**Severity**: Major
**Evidence Anchor**: absence: Sections 3.3 to 4.2 — expected baseline covariates such as prior attainment, credit load, and major entering the engagement-retention analysis; checked Measures, Analysis, Results, Table 1, Table 2, Limitations
**Confidence**: 5 — exhaustive read of the Measures and Analysis subsections.

### W12: No effect sizes, confidence intervals, or power justification anywhere
Every inferential result is reported as a test statistic and a *p*-value against a fixed alpha. No standardised mean difference accompanies either group comparison, no interval accompanies the correlation, and there is no a priori power analysis for a design whose secondary comparison rests on *n* = 10. This is below the reporting standard for quantitative educational research and, more practically, it prevents any reader from assessing whether the "modest" association the Discussion invokes is practically meaningful.
**Severity**: Major
**Evidence Anchor**: absence: Section 4 — expected effect sizes with confidence intervals and an a priori power justification; checked Analysis, Results, Table 1, Table 2, Abstract
**Confidence**: 5 — no such statistics appear in the manuscript.

### W13: The independent variable is defined by an untested vendor default
The entire exposure measure depends on a 30-minute inactivity threshold adopted because it is the platform's default. Session counts are highly sensitive to this parameter: a 10-minute or 60-minute rule would produce materially different counts, a different median, and therefore different group membership in every reported comparison. No sensitivity analysis across plausible thresholds is presented, so the reported association is conditional on a configuration choice made by the LMS vendor rather than by the researchers.
**Severity**: Major
**Evidence Anchor**: text: §3.3 "A session was defined as a dashboard view preceded by at least thirty minutes of inactivity"
**Confidence**: 5 — well-established sensitivity of sessionisation counts to the inactivity threshold.

### W14: Right-skewed continuous predictor is median-split, acknowledged but not remedied
The manuscript states that dashboard sessions are right-skewed and then dichotomises them at the median for the group comparisons that supply the paper's second headline finding. Median splitting discards variance, imposes an arbitrary and sample-dependent cut point, and with a skewed distribution places students with very different session counts on the same side of the threshold. Acknowledging the coarseness does not remedy it: the continuous analysis is available in the same data and is not reported.
**Severity**: Major
**Evidence Anchor**: text: §3.3 "students were split at the median number of dashboard sessions into high-engagement and low-engagement groups"
**Confidence**: 5 — standard psychometric result on dichotomisation of continuous predictors.

### W15: Both survey constructs are single items with no reliability or validity evidence
Perceived control over learning is a multidimensional construct measured here by one global item, justified on grounds of convention and survey burden rather than evidence. No test-retest reliability, no convergent validity against an established SRL instrument, and no pilot data are reported. The clarity item is likewise single-item and additionally has *n* = 10. Since perceived control carries one of the two claims in the Abstract and the whole SRL interpretation in the Discussion, the measurement basis for that claim is unestablished.
**Severity**: Major
**Evidence Anchor**: text: §3.3 "single-item overall ratings are common in dashboard studies to limit survey burden"
**Confidence**: 4 — clear from the Measures text; the strength of the objection depends on venue norms for single-item global ratings.

### W16: Behavioural log analysis conducted without notice to participants and with no ethics statement
The manuscript states plainly that students were not informed their dashboard activity would be analysed for this study, and no ethics approval, IRB reference, or consent-scope statement appears anywhere in the submission. Consent was obtained for a survey; whether it extends to secondary analysis of individually linked behavioural traces is precisely the question an ethics committee exists to answer, and the manuscript provides no evidence that it was asked. If approval exists, it must be documented; if it does not, this escalates beyond a reporting gap.
**Severity**: Major
**Evidence Anchor**: text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study."
**Confidence**: 4 — the text is unambiguous; the severity ceiling depends on an editorial and ethics-board determination outside my seat.

### W17: No reproducibility affordances
The analysis software is identified only as "standard statistical software" with no name or version, no analysis code or scripts are provided, there is no data availability statement, and no supplementary output is referenced. In an ordinary submission this would be a routine reporting gap. Here it is the only route by which the discrepancies in W1 through W6 could be resolved, and its absence means an editor cannot distinguish typesetting error from analytic error without requesting materials directly.
**Severity**: Minor
**Evidence Anchor**: absence: Section 3.4 and end matter — expected named software with version, analysis code, and a data availability statement; checked Methods, Analysis, Results, References
**Confidence**: 5 — no such materials appear in the submission.

### W18: Final exam score is analysed and tabulated but never operationalised in Measures
Section 3.3 defines dashboard engagement, retention, perceived control, and the clarity item, but not the final exam score, which nonetheless appears in Table 1 as a primary measure and supplies the dependent variable for the §4.3 comparison. Its scoring basis, weighting, and relationship to the retention coding (a student who does not sit the final is coded not retained, so exam score and retention are not independent variables) are all unstated.
**Severity**: Minor
**Evidence Anchor**: table: Table 1, row "Final exam score (0-100)"
**Confidence**: 5 — the variable is absent from the Measures subsection.
