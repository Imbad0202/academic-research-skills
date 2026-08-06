contract_role: methodology

## Dimension Scores

### D1: methodology_rigor

score: block
block_class: fatal
trigger: "internally contradictory sample sizes or degrees of freedom that no reading reconciles"

### D2: domain_accuracy

score: not_assessed

### D3: argumentative_coherence

score: block
block_class: repairable
trigger: "a headline causal or policy recommendation resting on an unadjusted association"

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: not_assessed

### D6: venue_fit_and_contribution

score: not_assessed

## Review Body

I read this manuscript the way I read any submission built on LMS trace data: first I try to reproduce every reported inferential and descriptive quantity from the samples the paper itself specifies, then I ask whether the design could support the reported interpretation even if the arithmetic were clean. Both checks fail here, and they fail independently of each other, which is why my recommendation rests on the arithmetic rather than only on the design.

The consistency audit is itemised in `## Arithmetic Receipts` below. Eight bounded recomputations were attempted; five returned mismatches. The most serious is the perceived-control comparison in §4.3, where the printed degrees of freedom require 158 cases contributing a perceived-control score. The item was answered by 87 respondents (§4.1) and the entire analytic sample is 142 (§3.2). Under the pooled-variance identity for an independent-samples *t*-test this is unattainable by 71 cases against the scored responses and by 16 against the whole sample, and a Welch correction cannot rescue it because Welch degrees of freedom are bounded above by *N*₁ + *N*₂ − 2, never below it. No prose revision fixes a degree of freedom that the described data cannot generate. The final-exam comparison fails in a second, independent way: *t*(140) = 1.31 corresponds to a two-tailed *p* ≈ .19 or a one-tailed *p* ≈ .096, so the printed *p* = .008 is wrong under either tail convention, and the surrounding prose ("did not reach a comparable level," "the difference was small") describes a null result while the printed *p* is significant at the stated α. The two errors point in opposite directions, which rules out a single transcription slip as the explanation. Table 2's group sizes (66 + 61 = 127) then contradict both the stated 142 and the *df* of 140, and §4.3 explicitly asserts that "All 142 students in the primary analytic sample were classified into engagement groups for this comparison," so the 15-case gap is not merely undocumented but affirmatively denied by the text. The descriptive statistics fail their own reachability checks: *M* = 3.847 cannot arise as a mean of 87 integers on a 1–5 scale, and the secondary clarity item's sample *SD* = 0.10 cannot arise from ten integers summing to 30, where the attainable sample SDs begin 0, 0.471, 0.667.

I want to be explicit that this audit is targeted rather than blanket. The headline retention correlation is the one statistic in the manuscript that reproduces: *r* = .24 on *N* = 142 yields *t* ≈ 2.93 on *df* = 140, whose two-tailed *p* rounds to the printed .004. I could not certify it outright only because §3.4 never states a tail convention and the one-tailed value (.002) would not match — a reporting gap, not an impossibility. That contrast matters diagnostically: whatever produced the perceived-control and exam statistics was not the analysis described in §3.4 applied to the samples described in §3.2.

Even with corrected arithmetic, the central claim would not be interpretable as reported. Retention is coded as remaining enrolled and sitting the final assessment, while dashboard engagement is the count of sessions accumulated "during the term." A student who withdrew in week five had ten fewer weeks in which to open the dashboard, so the outcome mechanically constrains the exposure window. The observed association is therefore partly an artefact of time at risk, and the paper offers no exposure-window normalisation (sessions per enrolled week, or sessions accumulated before a fixed common cut-point) and no temporal separation between measurement of the predictor and determination of the outcome. Until the predictor is measured over a window that every student shares, no directional reading — including the deliberately hedged "engagement and retention move together" — is available.

The sampling description cannot be true as written. §3.2 says participants were "drawn from the course enrollment using a random sample of students enrolled in the course section," and then describes an open LMS announcement, voluntary response, and exclusion of non-responders. Probability sampling and self-selected volunteer response are mutually exclusive recruitment mechanisms. The course enrolled "several hundred" students, yet no response or coverage rate is reported for the 142, and §5.1 does not list self-selection among the limitations, so the reader cannot bound the selection bias in either direction.

The modelling choices compound this. A dichotomous outcome is analysed with a Pearson correlation under a sentence that describes correlations "between continuous measures"; the resulting coefficient is a point-biserial and should be labelled as such, and its magnitude is constrained by the marginal retention split. For a binary outcome with any covariate adjustment at all, logistic regression is the appropriate model — and there are no covariates whatsoever, so nothing distinguishes dashboard engagement from prior achievement, enrolment intent, or general course activity. A median split on a right-skewed count discards information and leaves tie handling unstated. No confidence interval or standardised effect size appears anywhere. Item nonresponse of roughly 39% on the perceived-control measure receives no missing-data treatment and no responder-versus-nonresponder comparison. Final exam score appears in Table 1 and §4.3 but is never operationally defined in §3.3. The analysis software is "standard statistical software," unnamed and unversioned, with no data or code availability statement — which is precisely the material an editor would need to adjudicate the five mismatches above.

On argumentative coherence, my concern is narrowly evidentiary. §1 promises to "distinguish the pattern in the data from the causal story that might explain it" and §2 says the study was designed "to be transparent about its correlational scope." §5 then opens with "dashboard engagement improved course retention" and asserts that "increasing dashboard engagement therefore raises the probability that a student completes the course," and §6 recommends dashboard investment to "higher education institutions worldwide" as a "dependable strategy" that is "generalizable" across programmes and disciplines. That is a policy recommendation resting on one unadjusted bivariate association in one course, and it also generalises well past the sampled population. The abstract compounds the problem by printing *r* = .42 where §4.2 prints *r* = .24. I score this dimension repairable rather than fatal because a consistent correlational thesis is recoverable from the existing material if the causal and policy language is withdrawn; I leave the rhetorical and framing analysis to the owner role.

Two matters I note but do not score, as they sit outside my remit and are better judged by the domain and ethics-competent reviewers: §3.2 states that "Students were not informed that their dashboard activity data would be analyzed for this study" and the manuscript contains no ethics approval statement; and §2 attributes to Ferro and Nakamura (2021) the claim that dashboards "reliably improve outcomes for lower-achieving students," which is difficult to reconcile with the title carried in the reference list.

What would change my assessment is not a revised manuscript but the underlying material: the raw response-level data, the analytic file with case-level inclusion flags, and the analysis script. Five arithmetically unreachable values cannot be repaired by rewriting, and until they are traced to their source the reported inferential results cannot be treated as findings.

### S1: The headline retention correlation reproduces from the stated sample

The correlation between dashboard sessions and retention is internally coherent: on *N* = 142 the reported *r* = .24 implies *t* ≈ 2.93 on *df* = 140, whose two-tailed *p* rounds to the printed .004. This is worth saying explicitly, because it establishes that the failures elsewhere are localised rather than a global rounding or reporting-format artefact, and it gives the authors a verified anchor from which to reconstruct the remaining analyses.

**Evidence Anchor**: text: §4.2 "Dashboard engagement was positively associated with course retention (r = .24, p = .004)"

### S2: The sessionisation rule is stated precisely enough to be replicated

Trace-data papers routinely report "sessions" without defining the inactivity threshold or naming the sessionisation source. Here the 30-minute threshold and its provenance in the platform default are both given, which makes the exposure variable reconstructible from a comparable log export and lets a reader judge how the proxy would behave under a different threshold.

**Evidence Anchor**: text: §3.3 "A session was defined as a dashboard view preceded by at least thirty minutes of inactivity"

### S3: Analytic simplifications are disclosed rather than concealed

The median split is labelled as a coarse simplification adopted for interpretability rather than efficiency, and §2 concedes that click-based proxies conflate distinct kinds of engagement. I criticise the choice itself below, but the disclosure is the right practice: it makes the analytic decision auditable instead of leaving the reader to infer it from the results.

**Evidence Anchor**: text: §3.3 "This median split is a coarse simplification of a continuous measure"

### W1: Perceived-control t-test degrees of freedom are unattainable from any sample the paper reports

*t*(156) requires 158 cases contributing a perceived-control score under the pooled-variance identity, and Welch cannot raise the degrees of freedom above *N*₁ + *N*₂ − 2. The item was answered by 87 respondents; the full analytic sample is 142. No reading of §3.2, §3.3, or §4.1 reconciles the printed *df* with the available data, and this statistic carries one of the manuscript's two headline results. Because the defect is in the reported number rather than in its description, no revision of the prose can repair it; only the case-level data and analysis script can establish what was actually computed.

**Severity**: Critical
**Evidence Anchor**: text: §4.3 "t(156) = 3.02, p = .003"
**Arithmetic Receipt**: AR5
**Confidence**: 5 — direct application of the degrees-of-freedom identity for the test the paper names

### W2: The final-exam p-value cannot follow from the reported test statistic under either tail convention

At *df* = 140, *t* = 1.31 gives a two-tailed *p* ≈ .19 and a one-tailed *p* ≈ .096; the printed .008 would require *t* ≈ 2.67 two-tailed or *t* ≈ 2.44 one-tailed. The mismatch is stable across tail conventions, so it does not depend on the unstated tail. The prose surrounding the statistic compounds the problem by describing the result as not reaching a comparable level and as small, which contradicts the printed *p* in the opposite direction from the recomputed value. The exam comparison is secondary to the retention claim, so the core survives, but the reported result must be recomputed from data rather than reconciled by editing.

**Severity**: Major
**Evidence Anchor**: text: §4.3 "the difference was small, t(140) = 1.31, p = .008"
**Arithmetic Receipt**: AR7
**Confidence**: 5 — recomputation from a fully specified statistic and degrees of freedom

### W3: Table 2 group sizes contradict both the stated analytic sample and the reported degrees of freedom

The reported *df* = 140 implies 142 analysed cases, matching the stated analytic sample and matching §4.3's explicit assertion that all 142 students were classified into engagement groups. Table 2 sums to 127, which implies *df* = 125. Fifteen cases are unaccounted for, and because the same 142 is the denominator of the retention correlation, the discrepancy propagates to the paper's core estimate: a reader cannot determine which cases entered which analysis. A plausible mechanism is tie-dropping at the median, but the text forecloses that reading, so the accounting must be redone and reported.

**Severity**: Major
**Evidence Anchor**: table: Table 2, n column, 66 high-engagement and 61 low-engagement cases
**Arithmetic Receipt**: AR8
**Confidence**: 5 — arithmetic comparison of a reported sum against a reported degrees-of-freedom identity

### W4: The perceived-control mean is unattainable from 87 integer responses

A mean of 87 single-item integer scores has the form *S*/87 for integer *S*. The reported 3.847 requires *S* ≈ 334.689; the adjacent attainable means are 3.83908 and 3.85057, and no integer sum rounds to 3.847 at three decimals. Either the denominator is not 87, or the responses are not the integers §3.3 describes, or the mean is misreported. The same value is repeated in Table 1, so this is not a single-instance typographical artefact. The perceived-control descriptive claim in §4.1 and its use in §5 both depend on this quantity.

**Severity**: Major
**Evidence Anchor**: text: §4.1 "was 3.847 (SD = 0.62) on the 1-5 scale"
**Arithmetic Receipt**: AR1
**Confidence**: 5 — granularity check on an explicitly stated N, precision, and integer scale

### W5: The clarity item's sample SD is unattainable on the stated scale and sample size

With *N* = 10, *M* = 3.00 and integer responses on 1–5, the responses must sum to 30 and the sum of squared deviations must be a non-negative integer, so attainable sample SDs are √(SS)/3: 0, then 0.4714, then 0.6667. A reported 0.10 requires SS between 0.081 and 0.100, which contains no integer, and SS = 1 is in any case unreachable because integer deviations from an integer mean cannot sum to zero with a single unit deviation. The item is descriptive only and no core claim rests on it, but an unattainable value means the printed statistic is not a summary of the described responses; that requires the underlying ten responses, not rewording.

**Severity**: Major
**Evidence Anchor**: text: §4.1 "the reported secondary-item values were N=10; M=3.00; sample SD=0.10; integer scale=1-5"
**Arithmetic Receipt**: AR3
**Confidence**: 5 — reachability enumeration on a fully specified integer scale and sample size

### W6: The abstract and Results report mutually exclusive values for the study's central estimate

The abstract prints *r* = .42 for the engagement-retention association; §4.2 prints *r* = .24. These cannot both be the estimate, and the difference is not cosmetic: .42 would be a moderate association supporting the abstract's "promising lever" framing, whereas .24 is the "modest" effect §5 concedes. Readers, meta-analysts, and anyone screening the abstract alone would extract the wrong magnitude. The recomputation in AR4 is consistent only with .24, so the abstract appears to be the erroneous surface, but the authors must state which estimate the analysis produced and correct the other.

**Severity**: Major
**Evidence Anchor**: text: Abstract "Dashboard engagement correlated positively with retention (r = .42)"
**Confidence**: 5 — direct comparison of two reported values for the same parameter

### W7: The outcome definition mechanically constrains the exposure window

Retention is coded as remaining enrolled and completing the final assessment, while dashboard engagement counts sessions accumulated across the term. Students who withdrew early therefore had a shorter window in which any session could occur, so the outcome partially determines the maximum attainable value of the predictor. The association is thus confounded with time at risk by construction, and this is not a bias whose direction can be argued away: it inflates the observed relationship regardless of whether dashboards do anything. No exposure-window normalisation (for example sessions per enrolled week, or sessions counted only up to a common early cut-point) and no temporal separation between predictor measurement and outcome determination is offered, so the headline association supports no directional reading at all, including the hedged one. This defect survives any correction to the arithmetic and would alone require a redesigned exposure measure.

**Severity**: Critical
**Evidence Anchor**: text: §3.3 "the number of distinct sessions in which a student opened the dashboard view during the term" and "was coded dichotomously as whether the student remained enrolled and completed the final assessment"
**Confidence**: 5 — standard exposure-window confounding in observational trace-data designs

### W8: Causal and policy conclusions rest on a single unadjusted bivariate association

§5 states that engagement "improved" retention and that increasing engagement "raises the probability" of completion; §6 recommends dashboard investment to institutions "worldwide" as a "dependable strategy" that is "generalizable" across programmes and disciplines. The evidentiary basis is one unadjusted correlation in one self-selected sample from one course, with no covariates, no comparison condition, and no temporal identification. The design cannot distinguish a dashboard effect from prior achievement, enrolment intent, or general course activity, and the paper's own §1 and §2 promise correlational restraint, so the conclusions contradict the manuscript's stated scope as well as its evidence. The generalisation target also exceeds the sampled population by several orders of magnitude. A correlational thesis is recoverable, but only by withdrawing the causal and policy claims outright.

**Severity**: Critical
**Evidence Anchor**: text: §5 and §6 "dashboard engagement improved course retention" and "increasing dashboard engagement therefore raises the probability that a student completes the course"
**Confidence**: 5 — inference-to-design matching in observational educational research

### W9: The sampling description is internally contradictory and the coverage rate is never reported

§3.2 asserts probability sampling from the course enrolment and then describes a mid-term LMS announcement, voluntary response, and exclusion of non-responders. These are incompatible mechanisms, and the reader cannot tell which one generated the 142. Because the course enrolled "several hundred," the response and coverage rates are essential for bounding selection bias, and neither is given; §5.1 omits self-selection from the limitations entirely. Students who volunteer to answer a survey about their dashboard use are plausibly the students most engaged with the dashboard, which is the exposure variable, so the selection mechanism is not orthogonal to the analysis.

**Severity**: Major
**Evidence Anchor**: text: §3.2 "Participants were drawn from the course enrollment using a random sample of students enrolled in the course section" and "Students who chose to respond, and who consented to the survey, formed the study sample; those who did not respond were excluded"
**Confidence**: 5 — routine assessment of sampling frames in survey-plus-log designs

### W10: A dichotomous outcome is analysed with Pearson correlation and unadjusted t-tests, with no covariates

§3.4 describes correlations "between continuous measures," yet retention is explicitly dichotomous in §3.3. The coefficient reported in §4.2 is therefore a point-biserial and should be labelled as such, with the marginal retention split reported so readers can judge the ceiling on its magnitude. More substantively, a binary outcome with any adjustment requires logistic regression or an equivalent model, and no covariate of any kind is entered anywhere in the manuscript, so no confounder can be addressed even in principle. The engagement contrast is likewise tested by unadjusted *t*-tests with no equality-of-variance justification. Repairing this requires re-analysis on an appropriate model, not relabelling.

**Severity**: Major
**Evidence Anchor**: text: §3.4 "Associations between continuous measures were assessed with Pearson correlations"
**Confidence**: 5 — model-selection standards for binary outcomes in educational measurement

### W11: Item nonresponse of roughly 39% receives no missing-data treatment

Eighty-seven of 142 students answered the perceived-control item, and respondents who skipped it were simply excluded. No item response rate is computed, no missing-data mechanism is named, no responder-versus-nonresponder comparison is offered, and no sensitivity analysis is reported. Complete-case analysis on a self-report item about perceived control is precisely the situation in which nonresponse is likely to correlate with the construct, so the perceived-control result may be a selection artefact within an already self-selected sample. Fixing this requires new analysis of the retained data plus explicit reporting, not an added caveat.

**Severity**: Major
**Evidence Anchor**: absence: Methods and Results treatment of item nonresponse — expected a stated missing-data mechanism, an item response rate, and a comparison of responders with nonresponders; checked §3.2 participants and sampling, §3.3 measures, §3.4 analysis, §4.1 descriptives, Table 1, and §5.1 limitations

**Confidence**: 5 — standard missing-data reporting expectations for survey-linked trace data

### W12: No reproducibility affordances are provided at any level

The analysis software is described only as "standard statistical software," with no name, version, or procedure specified; there is no data availability statement, no analysis code, no codebook, and no full instrument text beyond two item stems. For an observational study whose entire empirical contribution is a set of statistics computed from proprietary LMS logs, this makes independent verification impossible. It also has a concrete consequence here: the five arithmetic mismatches documented above cannot be adjudicated by any reader or editor without the case-level data and script, so the absence of these affordances converts correctable errors into unresolvable ones.

**Severity**: Major
**Evidence Anchor**: absence: Analysis and end matter reproducibility affordances — expected named software with version, a data availability statement, and analysis code; checked §3.4 analysis, §3.3 measures, §5.1 limitations, §6 conclusion, and the reference list

**Confidence**: 5 — reproducibility reporting standards for LMS trace-data studies

### W13: No confidence intervals, standardised effect sizes, or precision statement accompany any inferential result

The manuscript reports point estimates and *p*-values only. There is no interval estimate for the correlation, no Cohen's *d* or mean-difference interval for either group comparison, and no power or precision statement anywhere, even though §5 turns on the claim that the effect is "reliable but not large." Group means and SDs in Table 2 make a standardised effect computable, so this is an omission in reporting rather than in the data. It does not alter the core claims, but it prevents a reader from judging how precisely the "modest" effect is pinned down.

**Severity**: Minor
**Evidence Anchor**: absence: Inferential reporting in Results — expected confidence intervals and standardised effect sizes for the correlation and both t-tests, plus a power or precision statement; checked §3.4 analysis, §4.2, §4.3, Table 1, and Table 2

**Confidence**: 5 — routine application of effect-size and interval reporting standards

### W14: Median split on a right-skewed count with unstated tie handling

§4.1 states that dashboard engagement was right-skewed with a small number of very active students, which is exactly the distribution in which a median split is least defensible: it discards magnitude information, treats students immediately either side of the cut as maximally different, and on a discrete count will produce ties at the median whose disposition determines group sizes. The tie rule is never stated, and the unequal 66/61 split in Table 2 suggests it mattered. The continuous predictor is available, so the appropriate remedy is to analyse it as such and reserve the dichotomisation for illustration.

**Severity**: Minor
**Evidence Anchor**: text: §3.3 "students were split at the median number of dashboard sessions into high-engagement and low-engagement groups"
**Confidence**: 5 — standard critique of dichotomising skewed continuous predictors

### W15: Final exam score is analysed but never operationally defined

Final exam score appears in Table 1 with a 0-100 range and is the outcome of the §4.3 comparison, yet §3.3 defines only dashboard engagement, retention, perceived control, and the clarity item. Nothing states what the exam comprised, how it was scored, whether the score is a raw percentage or a curved mark, or how students who did not sit it were handled — which matters because non-sitting is simultaneously the operationalisation of non-retention. The measure is straightforward to describe, so the omission is a documentation gap rather than a design flaw.

**Severity**: Minor
**Evidence Anchor**: absence: Measures section definition of the final exam outcome — expected an operational definition, scoring range, and administration details for the final exam score; checked §3.1 design and setting, §3.3 measures, §3.4 analysis, §4.3 group comparisons, and Table 1

**Confidence**: 5 — measurement documentation requirements for analysed variables

### W16: False precision in reported descriptive statistics

A mean of single-item integer responses is reported to three decimal places in both §4.1 and Table 1. Even setting aside its unattainability, three decimals imply a resolution the instrument cannot deliver: on a five-point integer scale with 87 respondents, the finest meaningful gradation is roughly 0.01. The clarity item's SD carries the mirror-image problem, being reported at a precision finer than the attainable spacing of values on that scale. Two decimals throughout, with precision matched to the measure, would present the same information honestly.

**Severity**: Minor
**Evidence Anchor**: table: Table 1, Perceived control (1-5) row, M column
**Confidence**: 5 — reporting-precision conventions for single-item ordinal measures

## Arithmetic Receipts

### AR1

procedure_id: grim
evidence_anchor: text: §4.1 "The mean perceived-control score across the 87 survey respondents who answered the item was 3.847"
reported_inputs: N = 87 respondents who answered the perceived-control item (§4.1); M = 3.847 reported to three decimals in §4.1 and repeated in Table 1; single-item integer 1-5 response scale (§3.3)
assumptions: only what §3.3 and §4.1 license, namely that each of the 87 respondents contributed exactly one integer score in {1,2,3,4,5}, that 3.847 is the unweighted arithmetic mean of those 87 integers, and that it is rounded to three decimals; no imputation, weighting, or non-integer scoring is assumed because none is described
derivation: an unweighted mean of 87 integers has the form S/87 with S a non-negative integer; 3.847 x 87 = 334.689, so the reported mean requires a non-integer sum; the two candidate integer sums give 334/87 = 3.839080 and 335/87 = 3.850575, and neither rounds to 3.847 at three decimals
derived_value_or_range: attainable means straddling the reported value are 3.839080 and 3.850575; the sum required by the reported value lies in [334.6455, 334.7325), which contains no integer
comparison_rule: half-up rounding at three decimals, so a printed 3.847 requires a true mean in [3.8465, 3.8475), equivalently an integer sum in [334.6455, 334.7325)
rounding_interval: [3.8465, 3.8475) for the mean, equivalently an integer response sum in [334.6455, 334.7325)
nearest_achievable: 334/87 = 3.839080 and 335/87 = 3.850575
status: mismatch
finding_ref: W4

### AR2

procedure_id: grimmer
evidence_anchor: text: §4.1 "3.847 (SD = 0.62)"
reported_inputs: N = 87 item respondents; M = 3.847; SD = 0.62 at two decimals; single-item integer 1-5 scale (§3.3)
assumptions: only what the paper states; §4.1 does not say whether 0.62 is a sample or population standard deviation, unlike the clarity item where "sample SD" is printed, so no denominator convention is assumed here
derivation: GRIMMER is conditional on a GRIM-consistent mean because the feasible set of sums of squared deviations depends on the integer response sum implied by that mean; AR1 establishes that no integer sum of 87 integers reproduces M = 3.847, so there is no candidate response vector against which SD = 0.62 can be tested, and completing the check would require assuming a mean the paper does not report
derived_value_or_range: not derived, because the feasible set of sums of squared deviations is undefined while the reported mean is GRIM-inconsistent
comparison_rule: would have been half-up rounding at two decimals against the standard deviations attainable from 87 integers summing to the GRIM-consistent total; not reached
status: not_computable
not_computable_reason: mean_grim_inconsistent

### AR3

procedure_id: grimmer
evidence_anchor: text: §4.1 "N=10; M=3.00; sample SD=0.10; integer scale=1-5"
reported_inputs: N = 10; M = 3.00 at two decimals; sample SD = 0.10 at two decimals; integer 1-5 response scale, all printed in §4.1 and consistent with §3.3
assumptions: only what the paper states, namely ten single-item integer responses in {1,2,3,4,5}, "sample SD" read as the n-1 denominator exactly as printed, and both statistics rounded half-up at two decimals
derivation: GRIM passes first because M = 3.00 requires an integer sum of 30, which ten integers in 1-5 can produce, so GRIMMER applies; with the mean exactly 3 and all responses integers, every deviation is an integer and the sum of squared deviations SS is a non-negative integer with sample variance SS/9, so attainable sample SDs are sqrt(SS)/3; deviations must sum to zero, so SS = 1 is unreachable and the smallest non-zero SS is 2; a printed SD of 0.10 requires SS = 9 x SD^2 in [0.081225, 0.099225), an interval containing no integer at all
derived_value_or_range: attainable sample SDs begin 0 at SS = 0, sqrt(2)/3 = 0.4714 at SS = 2, and 2/3 = 0.6667 at SS = 4; the required SS interval [0.081225, 0.099225) contains no attainable value
comparison_rule: half-up rounding at two decimals, so a printed 0.10 requires a true sample SD in [0.095, 0.105), equivalently SS in [0.081225, 0.099225)
rounding_interval: [0.095, 0.105) for the sample SD, equivalently a sum of squared deviations in [0.081225, 0.099225)
nearest_achievable: 0 at SS = 0 and sqrt(2)/3 = 0.4714 at SS = 2; SS = 1 is unattainable because integer deviations from an integer mean cannot sum to zero with a single unit deviation
status: mismatch
finding_ref: W5

### AR4

procedure_id: p_from_test_statistic
evidence_anchor: text: §4.2 "r = .24, p = .004"
reported_inputs: Pearson r = .24 between dashboard sessions and dichotomous retention; p = .004; primary analytic N = 142 (§3.2); alpha = .05 (§3.4)
assumptions: only that the printed p is the significance test of this r computed on the stated 142 cases via the standard t transformation with df = N - 2 = 140; §3.4 states an alpha but names no tail and declares no directional hypothesis, so no tail is assumed
derivation: t = r x sqrt(N-2) / sqrt(1 - r^2) = .24 x sqrt(140) / sqrt(1 - .0576) = 2.8397 / .97077 = 2.925 on df = 140; the corresponding two-tailed p is approximately .0039 and the one-tailed p is approximately .0019, so the printed .004 agrees under a two-tailed reading and disagrees under a one-tailed reading, which means the verdict is determined entirely by an unstated choice
derived_value_or_range: two-tailed p is approximately .0039 and one-tailed p is approximately .0019, against a printed .004
comparison_rule: agreement at the printed three-decimal precision, so the derived p must round to .004
tail_convention: unstated
status: not_computable
not_computable_reason: tail_ambiguous

### AR5

procedure_id: n_from_df
evidence_anchor: text: §4.3 "t(156) = 3.02"
reported_inputs: independent-samples t-test of perceived control between high- and low-engagement groups (§3.4, §4.3); df = 156; 87 respondents answered the perceived-control item (§4.1); primary analytic sample N = 142 (§3.2)
assumptions: only what §3.4 states, an independent-samples t-test on two groups with the conventional pooled-variance identity; no Welch or other correction is described anywhere in the manuscript
derivation: solving the pooled identity for the total gives N1 + N2 = df + 2 = 158 cases contributing a perceived-control score, but only 87 respondents answered that item and the entire analytic sample is 142, so the implied total exceeds the scored responses by 71 and the whole sample by 16; a Welch correction cannot resolve this because Welch degrees of freedom are bounded above by N1 + N2 - 2, so any correction would require even more than 158 cases
derived_value_or_range: implied analysed total of 158 cases, against 87 available scored responses and a maximum of 142 cases in the analytic sample
comparison_rule: the total implied by the reported degrees of freedom must not exceed the largest number of cases the paper reports as contributing the analysed variable
df_identity: df = N1 + N2 - 2 for a pooled-variance independent-samples t-test, with Welch degrees of freedom bounded above by the same quantity
status: mismatch
finding_ref: W1

### AR6

procedure_id: p_from_test_statistic
evidence_anchor: text: §4.3 "reported significantly greater perceived control than students in the low-engagement group, t(156) = 3.02, p = .003"
reported_inputs: t = 3.02; df = 156 as printed; p = .003; alpha = .05 (§3.4)
assumptions: the printed df = 156 is taken at face value for this computation alone, even though AR5 shows it is unattainable, in order to test whether the printed p is at least internally consistent with the printed statistic; §3.4 names no tail
derivation: at df = 156, t = 3.02 corresponds to a two-tailed p of approximately .0029 and a one-tailed p of approximately .0015; the printed .003 matches the two-tailed value at the stated precision and does not match the one-tailed value, so the verdict flips with the unstated tail choice and cannot be settled from the manuscript
derived_value_or_range: two-tailed p is approximately .0029 and one-tailed p is approximately .0015, against a printed .003
comparison_rule: agreement at the printed three-decimal precision, so the derived p must round to .003
tail_convention: unstated
status: not_computable
not_computable_reason: tail_ambiguous

### AR7

procedure_id: p_from_test_statistic
evidence_anchor: text: §4.3 "t(140) = 1.31, p = .008"
reported_inputs: t = 1.31; df = 140; p = .008; independent-samples comparison of final exam scores between engagement groups (§4.3); alpha = .05 (§3.4)
assumptions: only that the printed p corresponds to the printed t on the printed df from the independent-samples t-test named in §3.4; no tail is stated anywhere in the manuscript, so both conventions are evaluated
derivation: at df = 140, t = 1.31 yields a two-tailed p of approximately .192 and a one-tailed p of approximately .096, each exceeding the printed .008 by more than an order of magnitude, so the mismatch is stable across tail conventions and requires no tail assumption; inverting the comparison, a two-tailed p of .008 at df = 140 requires t of approximately 2.67 and a one-tailed p of .008 requires t of approximately 2.43, neither close to 1.31
derived_value_or_range: two-tailed p is approximately .192 and one-tailed p is approximately .096, and the printed .008 lies outside both
comparison_rule: agreement at the printed three-decimal precision, with the verdict required to hold under both tail conventions before a mismatch is declared
tail_convention: unstated
status: mismatch
finding_ref: W2

### AR8

procedure_id: n_from_df
evidence_anchor: table: Table 2 (Final exam comparison by engagement group), n and M final exam columns
reported_inputs: df = 140 from t(140) = 1.31 in §4.3; the §4.3 statement that all 142 students in the primary analytic sample were classified into engagement groups for this comparison; Table 2 group sizes of 66 and 61
assumptions: only what §3.4 and §4.3 state, an independent-samples t-test on the two engagement groups with the pooled-variance identity; no case weighting, pooling, or model-based correction is described
derivation: the pooled identity gives N1 + N2 = df + 2 = 142, which matches the stated analytic sample and the explicit §4.3 assertion, whereas the group sizes printed in Table 2 sum to 66 + 61 = 127 and would imply df = 125; the same comparison cannot simultaneously have analysed 142 and 127 cases, and the 15-case difference is not reconciled anywhere in §3 or §4
derived_value_or_range: total implied by the reported df is 142, total reported in Table 2 is 127, a discrepancy of 15 cases corresponding to an implied table df of 125
comparison_rule: the total implied by the reported degrees of freedom must equal the sum of the reported group sizes for the same comparison
df_identity: df = N1 + N2 - 2 for a pooled-variance independent-samples t-test
status: mismatch
finding_ref: W3
