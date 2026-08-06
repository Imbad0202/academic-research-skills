contract_role: methodology

## Dimension Scores

### D1: methodology_rigor
score: block
trigger: "internally contradictory sample sizes, degrees of freedom, or subgroup totals that cannot be reconciled"
block_class: fatal

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: block
trigger: "conclusions or recommended actions stated in causal, mechanistic, or policy-directive terms while the evidence base is purely associational"
block_class: repairable

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I recomputed every quantity in Section 4 that the manuscript supplies enough information to check before forming any judgement about the study's substance. The result is that not one inferential statistic in Section 4 reconciles with the sample the manuscript describes. The perceived-control t-test carries 156 degrees of freedom, which under any two-group identity requires at least 158 cases, against the 87 respondents who answered the item and the 142-student primary sample. The exam comparison's degrees of freedom imply 142 cases while its own Table 2 reports 127. The exam comparison's p-value is off by more than an order of magnitude from the printed t and df under either tail convention. The perceived-control mean of 3.847 is not attainable as the mean of 87 integer responses on a 1–5 scale. The secondary item's standard deviation of 0.10 is not attainable at all for ten integer responses with a mean of exactly 3.00 — the nearest reachable values are 0.000 and 0.471. And the headline correlation is .42 in the Abstract and .24 in §4.2.

Any one of these could be a transcription slip. Five independent checks failing in five different ways is a different kind of finding: it means the reader cannot determine which analysis was actually run on which cases. That is the condition my fatal criterion names, and it is not repairable from the manuscript, because the paper supplies no data, no code, no software identification, and no reconciliation of its four shifting subsamples (142, 127, 87, 10). A revision could not resolve this by rewriting; it would have to re-derive every number from the source data and show the reconciliation.

There is one forensic detail worth putting in front of the authors, and I flag it as my own hand calculation lying outside the bounded recompute procedures I use in the receipts below, so it requires the authors' verification rather than my assertion. Pooling Table 2's reported means and SDs (72.0/11.1 at n = 66 and 69.2/13.0 at n = 61) yields a pooled SD near 12.05, a standard error near 2.14, and t ≈ 1.31 on 125 degrees of freedom. The reported t is therefore consistent with Table 2's 127 cases and inconsistent with the stated df of 140 and with the claim that all 142 students were classified. The most parsimonious reading is that the analysis ran on 127 cases and that 15 students are unaccounted for. That reading, if correct, is exactly the missing-data accounting the manuscript omits.

Separately from the arithmetic, the design cannot support the paper's headline claim in any version. Dashboard sessions are counted across the whole term; students coded as not retained left the term early and could not accumulate sessions after leaving. The outcome therefore mechanically truncates the exposure, and a positive association between session count and retention is guaranteed by the measurement window irrespective of any dashboard effect. The manuscript nowhere acknowledges this direction problem, and neither the Limitations section nor the Discussion raises it. Fixing it requires a fixed early exposure window measured before any withdrawal occurs, plus adjustment for baseline attainment and baseline LMS activity — that is, a new analysis on data the manuscript does not report having.

On D3 I score narrowly and within my remit. The introduction promises care in separating pattern from cause; the Discussion opens by asserting that "dashboard engagement improved course retention" and that increasing engagement "raises the probability" of completion, and the Conclusion escalates to a "dependable strategy" that is "generalizable" for "institutions worldwide" on the basis of one lecture section of one introductory statistics course sampled by volunteer response. The §4.3 narrative also describes a result printed as p = .008 as failing to reach the level of an earlier finding, which contradicts the paper's own stated alpha of .05. I read these as block-level rather than fatal because the argument's associational core survives an honest rewrite, whereas the arithmetic problems do not survive anything short of re-derivation.

Finally, the sampling description contradicts itself within four sentences — a random sample in the first sentence, volunteer response to an LMS announcement with non-respondents excluded thereafter — with no enrolment denominator ("several hundred"), no response rate, and no comparison of respondents to non-respondents. This is not a hedging problem. It is a factual misstatement of the sampling mechanism at the point where a reader decides what the sample represents.

### S1: Design type and temporal scope stated explicitly and honestly
The paper names its design as observational and cross-sectional in §3.1 and states plainly that no student was observed across terms or courses. This is the correct starting posture and made the rest of my assessment tractable; the failure is that later sections argue as if the design were something else.
**Evidence Anchor**: text: §3.1 "Because the design is cross-sectional, all measures reflect a single term and no student was observed across multiple courses or terms"
**Confidence**: 5 — direct reading of an explicit design statement.

### S2: Exposure measure is operationally reproducible
The sessionisation rule is specified precisely enough that another analyst could re-implement the exposure variable from raw logs, including the inactivity threshold and its provenance in the platform default. Most dashboard studies I review do not supply this.
**Evidence Anchor**: text: §3.3 "A session was defined as a dashboard view preceded by at least thirty minutes of inactivity"
**Confidence**: 5 — routine assessment of trace-data operationalisation.

### S3: Outcome coding rule is stated at case level
The retention coding rule states not only the withdrawal case but also the enrolled-but-absent case, so a reader knows how each student was classified. The composite nature of that coding is a separate problem (W12), but the rule itself is explicit rather than implied.
**Evidence Anchor**: text: §3.3 "Students who withdrew before the final assessment, or who were enrolled but did not sit the final, were coded as not retained"
**Confidence**: 5 — explicit coding statement.

### S4: Median split is disclosed as a concession rather than defended as a method
The paper names the dichotomisation as a coarse simplification adopted for interpretability, not efficiency. This kind of disclosure is what lets a reviewer locate the cost rather than hunt for it, and it should be preserved in any revision even as the analysis moves to the continuous measure.
**Evidence Anchor**: text: §3.3 "This median split is a coarse simplification of a continuous measure and was adopted for interpretability rather than statistical efficiency"
**Confidence**: 4 — judgement about reporting transparency in this literature.

### W1: The outcome mechanically truncates the exposure, so the headline association is guaranteed by the measurement window
Dashboard sessions are accumulated over the full 15-week term, while students coded as not retained exited the term early and were structurally unable to accumulate further sessions. Students who are failing withdraw, and withdrawn students cannot open a dashboard. Under this design a positive engagement–retention correlation is produced by the exposure window alone, with or without any dashboard effect, and the manuscript reports no fixed pre-withdrawal exposure window, no survival framing, and no adjustment for baseline attainment or baseline LMS activity. This defect alone invalidates the central claim and cannot be repaired by rewriting; it requires re-measuring exposure over a window that closes before any outcome can occur.
**Severity**: Critical
**Evidence Anchor**: text: §3.3 "the number of distinct sessions in which a student opened the dashboard view during the term"
**Confidence**: 5 — this is the standard exposure-truncation failure mode in observational learning-analytics designs, which I teach.

### W2: The perceived-control t-test's degrees of freedom cannot be reconciled with any sample the paper describes
The comparison reports 156 degrees of freedom. Under the pooled independent-samples identity this implies 158 analysed cases; under Welch the df is bounded above by N − 2 as well, so no two-group identity yields 156 from either the 87 respondents who answered the item or the 142-student primary sample. The perceived-control item was answered by 87 students, which caps df at 85. This is one of the two results named in the Abstract, and as printed it cannot be the analysis described in §3.4 on the sample described in §3.2. A reader cannot tell what was tested or on whom.
**Severity**: Critical
**Evidence Anchor**: text: §4.3 "t(156) = 3.02, p = .003"; §3.2 "A subset of these students additionally answered the perceived-control item"
**Arithmetic Receipt**: AR7
**Confidence**: 5 — arithmetic recomputed from the printed df and the stated item response count.

### W3: Table 2's group sizes contradict both the stated classification and the reported degrees of freedom
The text states that all 142 students were classified into engagement groups for the exam comparison, and the reported df of 140 is consistent with 142 cases. Table 2 reports n = 66 and n = 61, totalling 127. Fifteen cases are unexplained. My own unreceipted pooled recomputation from Table 2's means and SDs returns t ≈ 1.31 on 125 df, which matches the printed t and points to 127 as the true analytic N — but this must be verified by the authors against the source data rather than accepted from me. Either the table or the df is wrong, and in either case the exam comparison's sample is unknown.
**Severity**: Major
**Evidence Anchor**: table: Table 2, engagement-group n column (66 and 61)
**Arithmetic Receipt**: AR9
**Confidence**: 5 — direct subtraction plus a standard pooled-variance check.

### W4: The exam comparison's p-value is impossible given its own t and df
For t = 1.31 on 140 df the two-tailed p is approximately .19 and the one-tailed p approximately .096. The reported .008 is unreachable under either convention, and .008 would require a t near 2.7 two-tailed. The direction of the error also matters: .008 falls below the paper's stated alpha of .05, so as printed the result is significant while the surrounding narrative treats it as null. A reader cannot determine whether the intended value was .08, .19, or something else, and the choice changes what the section reports.
**Severity**: Major
**Evidence Anchor**: text: §4.3 "the difference was small, t(140) = 1.31, p = .008"
**Arithmetic Receipt**: AR10
**Confidence**: 5 — t-distribution tail area recomputed from the printed statistic and df.

### W5: The perceived-control mean is not attainable from 87 integer responses
A single item on a 1–5 integer scale answered by 87 students yields a mean equal to an integer total divided by 87. For a reported 3.847 the total would have to lie in [334.65, 334.73), which contains no integer; the adjacent attainable means are 3.83908 and 3.85057. Either the N, the scale, the item structure, or the mean differs from what §3.3 and §4.1 state. Because this descriptive underlies the Abstract's perceived-control claim, the claim cannot be checked as printed.
**Severity**: Major
**Evidence Anchor**: text: §4.1 "The mean perceived-control score across the 87 survey respondents who answered the item was 3.847 (SD = 0.62)"
**Arithmetic Receipt**: AR1
**Confidence**: 5 — GRIM reachability check on stated N, precision, and scale.

### W6: The secondary item's standard deviation is arithmetically impossible
For ten integer responses on a 1–5 scale with a mean of exactly 3.00, the sum of squared deviations must be a non-negative even integer, so the attainable sample SDs are 0.000, 0.471, 0.667, and so on. A reported 0.10 would require a squared-deviation sum of 0.09. No configuration of ten integer responses produces it, and the population-SD reading fails equally. The item is descriptive only, so no inference rests on it — but an impossible SD is direct evidence that at least one reported summary does not come from the data as described, which is what makes the Section 4 pattern a reporting-integrity problem rather than a rounding problem.
**Severity**: Major
**Evidence Anchor**: text: §4.1 "the reported secondary-item values were N=10; M=3.00; sample SD=0.10; integer scale=1-5"
**Arithmetic Receipt**: AR3
**Confidence**: 5 — GRIMMER variance-reachability check on an integer-bounded scale.

### W7: The headline correlation differs between the Abstract and the Results
The Abstract reports r = .42; §4.2 reports r = .24. The Abstract value overstates the shared variance by roughly a factor of three (.18 versus .06) and is the number most readers and citation chains will carry forward. The Discussion's hedged "modest" characterisation matches .24, not .42, which suggests .42 is the error — but the manuscript nowhere reconciles them, and no confidence interval is given for either value that would let a reader judge their compatibility.
**Severity**: Major
**Evidence Anchor**: text: Abstract "Dashboard engagement correlated positively with retention (r = .42)"; §4.2 "Dashboard engagement was positively associated with course retention (r = .24, p = .004)"
**Confidence**: 5 — direct comparison of two printed values for the same quantity.

### W8: The sampling description contradicts itself and supplies no denominator
The first sentence of §3.2 states a random sample of enrolled students. Three sentences later the recruitment is an LMS announcement to which students elected to respond, with non-respondents excluded. These are different sampling mechanisms with different inferential warrants, and only the second is compatible with the described procedure. The enrolment denominator is given only as "several hundred", so no response rate is computable, and nothing establishes how the 142 respondents differ from the non-responding remainder. Volunteer response to a survey about dashboard use is precisely the mechanism that would over-recruit engaged students, which bears directly on the exposure distribution in Table 1.
**Severity**: Major
**Evidence Anchor**: text: §3.2 "Participants were drawn from the course enrollment using a random sample of students enrolled in the course section"; §3.2 "Students who chose to respond, and who consented to the survey, formed the study sample"
**Confidence**: 5 — the two statements are mutually exclusive on their face.

### W9: Four different analytic samples appear with no missing-data accounting
The manuscript analyses 142, 127, 87, and 10 cases at different points without stating how each subsample was formed, whether attrition or item non-response drove the differences, or whether the excluded cases differ systematically from the retained ones. Item skippers are described as excluded, which is listwise deletion by default and unstated as such. With retention as the outcome and volunteer recruitment as the sampling mechanism, missingness is plausibly related to both exposure and outcome, so complete-case analysis is the assumption most likely to be wrong here and the one least defensible without evidence.
**Severity**: Major
**Evidence Anchor**: absence: §3.2–§4.3 — expected reconciliation of the 142, 127, 87, and 10 analytic subsamples with an explicit missing-data mechanism and a respondent versus non-respondent comparison; checked §3.2 Participants and Sampling, §3.3 Measures, §3.4 Analysis, §4.1–§4.3 Results, Tables 1–2
**Confidence**: 5 — verified by reading every N reported in the manuscript.

### W10: No effect sizes, no confidence intervals, and no covariate adjustment anywhere
Inference rests entirely on p-values against a fixed alpha. No standardised mean difference accompanies either t-test, no interval accompanies the correlation, and no model adjusts for prior attainment, baseline LMS activity, major, or any other determinant of both engagement and persistence. In an observational design with a self-selected sample, an unadjusted bivariate association is not an estimate of anything the paper wants to claim, and without intervals a reader cannot even judge whether the reported difference in exam performance is compatible with zero or with a substantively important effect.
**Severity**: Major
**Evidence Anchor**: absence: §3.4 and §4.2–§4.3 — expected effect sizes with confidence intervals for each reported comparison and a covariate-adjusted model specification; checked §3.4 Analysis, §4.2, §4.3, Tables 1–2, §5.1 Limitations
**Confidence**: 5 — confirmed absent across the analysis and results sections.

### W11: Median dichotomisation of an explicitly right-skewed predictor, with the tie rule and resulting group sizes unexplained
The paper reports that dashboard engagement is right-skewed with a small number of very active students, then splits at the median. Dichotomising a skewed continuous predictor discards variance, loses power relative to the continuous analysis, and can manufacture group differences that reflect the cut point rather than the construct — the high-engagement group here spans a range from the median to 48 sessions. The tie-handling rule is unstated, and the reported group sizes (66/61) are unequal in a way a median split does not explain without a tie rule. Every group comparison in the paper, including the perceived-control result in the Abstract, depends on this construction.
**Severity**: Major
**Evidence Anchor**: text: §3.3 "students were split at the median number of dashboard sessions into high-engagement and low-engagement groups"
**Confidence**: 5 — standard cost of dichotomisation, plus the paper's own skew statement.

### W12: The retention outcome conflates two different processes, and the correlation is not identified as point-biserial
"Not retained" covers both withdrawal before the final assessment and remaining enrolled but not sitting the final. These are different behaviours with different relationships to dashboard exposure: the first truncates exposure, the second does not. Collapsing them makes the outcome uninterpretable as retention and makes the direction problem in W1 impossible to bound. Relatedly, §3.4 describes Pearson correlations "between continuous measures", but the reported r pairs a count with a dichotomous outcome, so it is a point-biserial coefficient whose magnitude is bounded by the marginal split of the outcome — a constraint the paper never states and the reader needs in order to interpret .24.
**Severity**: Major
**Evidence Anchor**: text: §3.3 "Course retention was coded dichotomously as whether the student remained enrolled and completed the final assessment"; §3.4 "Associations between continuous measures were assessed with Pearson correlations"
**Confidence**: 5 — measurement-validity and estimator-fit judgement within my specialism.

### W13: Causal and interventional claims are asserted from a cross-sectional association
The Discussion states as the central finding that engagement "improved" retention and that increasing engagement "raises the probability" of completion. Both are causal claims about an intervention that was never manipulated, on a self-selected sample, with no adjustment, and with an exposure measured over a window closed by the outcome. The Introduction's stated commitment to distinguishing pattern from cause is abandoned without acknowledgement, and §2 cites a critique of exactly this practice.
**Severity**: Major
**Evidence Anchor**: text: §5 "The central finding of this study is that dashboard engagement improved course retention"; §5 "increasing dashboard engagement therefore raises the probability that a student completes the course"
**Confidence**: 5 — comparison of claim strength against the stated design.

### W14: Generalisation extends far beyond one volunteer sample in one course section
The Conclusion recommends institutional investment as a "dependable strategy" for retention "across programs and disciplines" and a "generalizable lever" for institutions worldwide. The evidence is one lecture section of one introductory statistics course at one university, sampled by volunteer response, in one term, with one dashboard design that §5.1 itself concedes differs from those deployed elsewhere. The Limitations section names the single-course constraint and the Conclusion then argues as if it had been resolved.
**Severity**: Major
**Evidence Anchor**: text: §6 "investing in student-facing dashboards and encouraging students to engage with them is a dependable strategy for improving retention across programs and disciplines"
**Confidence**: 5 — sampled population versus target population comparison.

### W15: The narrative describes a significant printed result as non-significant
Section 4.3 introduces the exam comparison as not reaching a comparable level and the Discussion calls it "weaker still", while the printed p of .008 falls well below the paper's stated alpha of .05 and below the p reported for the correlation. Whichever number is wrong, the results narrative and the results numbers are describing different findings, and the reader has no way to tell which one the authors believe.
**Severity**: Major
**Evidence Anchor**: text: §4.3 "A parallel comparison on final exam performance did not reach a comparable level"; §5 "the exam-performance comparison was weaker still"
**Confidence**: 5 — comparison of narrative characterisation against the printed p and stated alpha.

### W16: Trace data were analysed without informing the students, and no ethics approval is reported
The manuscript states that students were not informed their dashboard activity data would be analysed for the study, while survey consent was obtained. Secondary analysis of individually identifiable behavioural logs linked to consented survey responses and to a withdrawal outcome is human-subjects research, and the manuscript reports no ethics board review, no approval identifier, no waiver of consent, and no data-protection provision anywhere in §3 or the end matter. This is a data-provenance defect, not only a compliance one: without a documented approval and consent basis, the legitimacy of the linked dataset that every analysis depends on is unestablished.
**Severity**: Major
**Evidence Anchor**: text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study"
**Confidence**: 4 — confident on the reporting gap; specific institutional requirements vary by jurisdiction.

### W17: No reproducibility affordances at all
The analysis software is described only as "standard statistical software", with no name, version, or procedure identified; no data, synthetic data, code, codebook, or analysis plan is offered or referenced. Ordinarily I would treat this as a routine reporting gap. Here it is the reason the arithmetic problems above are unrepairable from the manuscript: with no artefact to consult, no reader can determine which of the conflicting numbers reflects the analysis actually performed.
**Severity**: Minor
**Evidence Anchor**: absence: §3.4 and end matter — expected named software with version, a data and analysis-code availability statement, and any pre-specification of the analysis plan; checked §3.4 Analysis, §4 Results, §5.1 Limitations, §6 Conclusion, References
**Confidence**: 5 — verified absent across all reporting surfaces.

## Arithmetic Receipts

### AR1
procedure_id: grim
evidence_anchor: table: Table 1, Perceived control row (M = 3.847, SD = 0.62), with N = 87 from §4.1
reported_inputs: single-item integer response scale 1-5 (§3.3); N = 87 respondents who answered the item (§4.1); reported mean 3.847 at three-decimal precision (§4.1 and Table 1)
assumptions: the paper states the item is one integer 1-5 rating and that 87 respondents answered it, so the reported mean is a sum of 87 integers divided by 87; no weighting, imputation, or aggregation is described
derivation: an attainable mean is T/87 for integer T in [87, 435]; for 3.847 the rounding interval [3.8465, 3.8475) requires T in [334.6455, 334.7325), which contains no integer, and the adjacent totals give 334/87 = 3.83908 and 335/87 = 3.85057
derived_value_or_range: attainable means nearest the reported value are 3.83908 and 3.85057; no attainable mean rounds to 3.847
comparison_rule: half-up rounding to three decimals; consistent only if some attainable mean falls in [3.8465, 3.8475)
rounding_interval: [3.8465, 3.8475) at three-decimal precision, equivalently response total T in [334.6455, 334.7325)
nearest_achievable: 334/87 = 3.83908 and 335/87 = 3.85057
status: mismatch
finding_ref: W5

### AR2
procedure_id: grimmer
evidence_anchor: table: Table 1, Perceived control row SD = 0.62, with N = 87 from §4.1
reported_inputs: N = 87; reported mean 3.847; reported SD 0.62 at two-decimal precision; single-item integer scale 1-5
assumptions: the paper states an integer 1-5 single item and N = 87; GRIMMER presupposes a GRIM-consistent mean from which the attainable variance set is built
derivation: the reported mean is not attainable from 87 integer responses (see AR1), so no valid response total exists from which to enumerate attainable sums of squared deviations, and the variance reachability check cannot be started
derived_value_or_range: not derivable while the reported mean is GRIM-inconsistent
comparison_rule: none applied; the procedure requires a GRIM-consistent mean before variance reachability is evaluated
status: not_computable
not_computable_reason: mean_grim_inconsistent

### AR3
procedure_id: grimmer
evidence_anchor: text: §4.1 "N=10; M=3.00; sample SD=0.10; integer scale=1-5"
reported_inputs: N = 10; M = 3.00 at two decimals; sample SD = 0.10 at two decimals; responses are integers on a 1-5 scale (§3.3 and §4.1)
assumptions: the paper explicitly labels the dispersion a sample SD and the scale an integer 1-5 scale, so no SD-convention or granularity assumption is imposed
derivation: M = 3.00 is GRIM-consistent with response total 30, giving a mean of exactly 3; with integer responses summing to 30 the deviations from 3 are integers summing to zero, so their squared sum SS is a non-negative even integer and the sample SD equals sqrt(SS/9); SD = 0.10 requires SS = 0.09, and under a population-SD reading it would require SS = 0.1, neither of which is an even integer
derived_value_or_range: attainable sample SDs are sqrt(0/9) = 0.0000, sqrt(2/9) = 0.4714, sqrt(4/9) = 0.6667 and upward; nothing lies strictly between 0.0000 and 0.4714
comparison_rule: half-up rounding to two decimals; consistent only if an attainable SD falls in [0.095, 0.105), equivalently SS in [0.0812, 0.0992)
rounding_interval: [0.095, 0.105) at two-decimal precision, equivalently SS in [0.0812, 0.0992)
nearest_achievable: 0.0000 at SS = 0 and 0.4714 at SS = 2 straddle the reported 0.10
status: mismatch
finding_ref: W6

### AR4
procedure_id: grim
evidence_anchor: table: Table 1, Dashboard sessions row (M = 14.6, SD = 9.1, Min = 0, Max = 48), with N = 142 from §3.2
reported_inputs: N = 142 primary analytic sample; reported mean 14.6 at one decimal; measure defined as a count of distinct dashboard sessions
assumptions: §3.3 defines the measure as a session count, so values are non-negative integers, and §3.2 states that 142 students provided complete behavioral log data
derivation: an attainable mean is T/142 for integer T; the rounding interval [14.55, 14.65) requires T in [2066.1, 2080.3), which contains the integers 2067 through 2080
derived_value_or_range: attainable means from T = 2067 to T = 2080 run from 14.5563 to 14.6479, and several fall inside the rounding interval
comparison_rule: half-up rounding to one decimal; consistent if any attainable mean falls in [14.55, 14.65)
rounding_interval: [14.55, 14.65) at one-decimal precision, equivalently total T in [2066.1, 2080.3)
nearest_achievable: 2073/142 = 14.59859 and 2074/142 = 14.60563, both rounding to 14.6
status: consistent

### AR5
procedure_id: grim
evidence_anchor: table: Table 1, Final exam score row (M = 71.3, SD = 12.4, Min = 32, Max = 98)
reported_inputs: reported mean 71.3 at one decimal; scale labelled 0-100; candidate Ns are 142 (§3.2) and 127 (Table 2 group totals)
assumptions: none beyond the printed values; the paper does not state whether exam scores are integer-valued or can take fractional values, and does not state which N produced Table 1
derivation: GRIM requires a known integer granularity together with a known N in order to enumerate attainable means; the manuscript supplies neither for exam score, so no attainable set can be constructed and no reachability claim is available
derived_value_or_range: not derivable; the attainable set depends on unstated score granularity
comparison_rule: none applied; the documented boundary of the procedure requires integer-valued data at a known N
status: not_computable
not_computable_reason: scale_granularity_unknown

### AR6
procedure_id: p_from_test_statistic
evidence_anchor: text: §4.2 "(r = .24, p = .004)"
tail_convention: unstated
reported_inputs: r = .24; reported p = .004; N = 142 (§3.2); retention coded dichotomously (§3.3); alpha = .05 (§3.4)
assumptions: N = 142 taken from §3.2 as the sample with complete log and retention data; the null is zero association; the identity t = r*sqrt(N-2)/sqrt(1-r^2) on df = N-2 is used, which for a dichotomous outcome is the point-biserial equivalent of the two-group t-test; the paper states no tail and no directional hypothesis
derivation: t = .24*sqrt(140)/sqrt(1-.0576) = 2.840/0.9709 = 2.925 on df = 140, whose upper-tail area is about .0020
derived_value_or_range: two-tailed: p is about .0040; one-tailed: p is about .0020
comparison_rule: reported p = .004 at three decimals; the two-tailed derivation rounds to .004 while the one-tailed derivation rounds to .002, so the verdict depends on which tail the paper intended
status: not_computable
not_computable_reason: tail_ambiguous

### AR7
procedure_id: n_from_df
evidence_anchor: text: §4.3 "Students in the high-engagement group reported significantly greater perceived control than students in the low-engagement group, t(156) = 3.02"
reported_inputs: independent-samples t-test (§3.4); reported df = 156; perceived-control item answered by 87 respondents (§4.1); primary analytic sample 142 (§3.2)
assumptions: §3.4 states independent-samples t-tests, so the pooled two-sample identity applies; no imputation, pooling across items, or repeated-measures structure is described; the Welch alternative is also bounded above by N-2, so the conclusion does not depend on which two-group variant was used
derivation: df = N1 + N2 - 2 = 156 implies a total analysed N of 158, while the item respondents number 87 (maximum df 85) and the full primary sample numbers 142 (maximum df 140), so 158 exceeds every sample the manuscript reports
derived_value_or_range: derived N = 158; reported candidate totals are 87 item respondents and 142 primary-sample students
comparison_rule: the derived total N must equal the number of cases contributing to the two compared groups
df_identity: df = N1 + N2 - 2 for a pooled independent-samples t-test
status: mismatch
finding_ref: W2

### AR8
procedure_id: p_from_test_statistic
evidence_anchor: text: §4.3 "t(156) = 3.02, p = .003"
tail_convention: unstated
reported_inputs: t = 3.02; df = 156; reported p = .003; alpha = .05 (§3.4)
assumptions: the printed t and df are used exactly as given; the paper states no tail convention and no directional hypothesis for the perceived-control comparison
derivation: for t = 3.02 on df = 156 the upper-tail area is approximately .00146, so doubling gives approximately .0029
derived_value_or_range: two-tailed: p is about .0029; one-tailed: p is about .0015
comparison_rule: reported p = .003 at three decimals; the two-tailed derivation rounds to .003 and would be consistent, while the one-tailed derivation rounds to .001 or .002 and would be a mismatch, so the tail choice flips the verdict
status: not_computable
not_computable_reason: tail_ambiguous

### AR9
procedure_id: n_from_df
evidence_anchor: text: §4.3 "All 142 students in the primary analytic sample were classified into engagement groups for this comparison"
reported_inputs: reported df = 140; stated classification of all 142 primary-sample students; Table 2 group sizes 66 and 61
assumptions: §3.4 states independent-samples t-tests, so the pooled two-sample identity applies; §3.3 defines the two engagement groups as an exhaustive median split, so the group sizes should sum to the analysed total
derivation: df = 140 implies N1 + N2 = 142, which matches the stated 142 but exceeds the Table 2 total of 66 + 61 = 127 by 15 cases, so the df and the table cannot both describe the same comparison
derived_value_or_range: derived N = 142; the reported group total for the same comparison is 127
comparison_rule: the derived total N must equal the sum of the reported group ns for the same comparison
df_identity: df = N1 + N2 - 2 for a pooled independent-samples t-test
status: mismatch
finding_ref: W3

### AR10
procedure_id: p_from_test_statistic
evidence_anchor: text: §4.3 "t(140) = 1.31, p = .008"
tail_convention: unstated
reported_inputs: t = 1.31; df = 140; reported p = .008; alpha = .05 (§3.4)
assumptions: the printed t and df are used exactly as given; the paper states no tail convention and no directional hypothesis for the exam comparison
derivation: for t = 1.31 on df = 140 the upper-tail area is approximately .096, so doubling gives approximately .192; recovering p = .008 would require a t of about 2.7 two-tailed or about 2.4 one-tailed
derived_value_or_range: two-tailed: p is about .192; one-tailed: p is about .096
comparison_rule: reported p = .008 at three decimals; consistent only if a derived value rounds to .008, which neither tail approaches, so the verdict does not depend on the tail choice
status: mismatch
finding_ref: W4
