contract_role: methodology

## Dimension Scores

### D1: methodology_rigor
score: warn
trigger: "reliability evidence reported for only some scales, uncertainty given without assumption checks, missing-data handling mentioned only in passing, no instrument appendix, or a single-source self-report design whose common-method vulnerability is not discussed"

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: warn
trigger: "effect sizes characterised as strong or meaningful without a comparison benchmark, or a discussion claim that outruns its result yet is elsewhere correctly hedged"

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

This is a disciplined small study that mostly declines to overclaim, and the honest thing to say first is that its inferential register is better than its measurement layer. The design is stated, the analysis is the right analysis for the question as posed, the causal disclaimer is repeated rather than buried, and the reverse pathway is named explicitly. Those are not decorative virtues; they are the reason I score D1 `warn` rather than `block`. Every gap I found is repairable either by disclosure of information the authors already possess or by re-analysis of the dataset they already have — none of them requires abandoning the study, and none of them can plausibly reverse the direction or the statistical significance of the headline coefficient.

What the manuscript does not survive is the claim that r = .42 is a *quantity comparable to prior estimates*. The outcome is one five-point frequency item. A single item has no internal-consistency estimate by construction, and the manuscript supplies no test-retest, no parallel indicator, and no attenuation bound. Under the classical model the observed correlation is bounded above by the square root of the outcome's reliability, so the reported .42 is a floor of unknown height. Simultaneously, both variables come from the same instrument, the same respondent, and the same sitting, which pushes the observed covariance the other way by an unquantified amount. The manuscript acknowledges neither mechanism. The result is a coefficient reported to two decimals with a 95% CI, sitting on a measurement structure that cannot pin its magnitude at all. That is the specific way in which reported precision here outruns what the measurement supports, and it is why I flag the comparability claim (W12) as Major rather than treating the CI's presence as sufficient rigor.

I verified the uncertainty reporting rather than assuming it. Fisher-z on r = .42 with n = 214 gives z = .4477, SE = 1/√211 = .0688, so the 95% z-limits are .3128 and .5826, back-transforming to .3029 and .5246, which at two decimals is [.30, .52]. The reported interval is exactly what the standard procedure yields; the reviewer-brief estimate of an upper limit near .53 is off at the third decimal. This calculation is not one of the four bounded recompute procedures, so it carries no receipt below, and I flag it as model-generated arithmetic that a human should re-run rather than accept. The same applies to the exclusion arithmetic: 233 − 14 − 5 = 214 is coherent across §3.1, the abstract, and §7, so the paper has no unit-count contradiction.

The sampling account is where the paper is thinnest and where its limitations section functions as a shield rather than a fix. "All enrolled undergraduates were eligible" without a count means there is no denominator, so no response rate exists and nonresponse bias cannot be bounded even in direction. §6's fourth limitation — "response was voluntary, so students who engage more with institutional channels may be overrepresented" — names precisely the mechanism that would inflate the observed association if perceived usefulness and channel engagement covary, and then leaves it unbounded. Conceding a threat is not the same as constraining it. With no demographics beyond "spanned all four year levels," a reader cannot even benchmark the respondents against the registry. That is a Major gap (W2), and the fix is cheap: the institution knows its enrolment.

On the internal-consistency question in the methods account, I considered and rejected a fatal finding. §3.3 asserts that no identifying information was collected and that responses could not be linked to individual students, while §3.1 reports removing five duplicate entries. Duplicate detection is not strictly impossible under anonymity — identical response vectors, platform-level single-submission enforcement, or a one-time link token would all do it — but two of the plausible mechanisms (IP address, device fingerprint) would falsify the §3.3 sentence, and the manuscript states none of them. My Phase 1 fatal criterion required a procedure that is impossible or self-contradictory at its foundation, and this is instead an unresolved procedural disclosure whose repair is a sentence plus, if the mechanism was response-vector matching, a defensible rule for distinguishing a duplicate from two students who happened to answer identically on six 1–5 items and one 1–5 item. That is Major (W3), not fatal. I am not alleging a protocol violation; I am saying the account as written cannot be reconciled by a reader, and in an ethics-approved anonymous survey that reconciliation is exactly what has to be on the page.

The α = .88 report is doing more work than it can. Alpha presupposes essential unidimensionality, and there is no factor analysis, no item-total correlations, no interval on α, and — critically — no description of what "adapted" changed in the Costa and Wren instrument. If items were reworded, dropped, or rescaled, the original validation does not transfer, and the manuscript's own framing ("previously validated instrument") depends on that transfer. The six item stems are not reproduced anywhere, so the reader cannot judge the adaptation at all (W5, W10).

The power statement (W7) is a sensitivity calculation on the analyzed n dressed as design justification. n = 214 was not known at design time; it is the post-exclusion analytic sample. The provenance of the r ≥ .19 target is unstated, no software or computational method is named, and by the standard Fisher-z approximation the power at n = 214 for ρ = .19, α = .05 two-tailed lands essentially at .80 rather than comfortably above it, so "greater than .80" is not robust to the unstated method. Because power computation is outside the four bounded recompute procedures, I do not file this as an arithmetic mismatch and I do not assert a numeric contradiction — it is a framing and reporting defect, Minor in decision impact.

On D3, my angle is narrower than the discourse owner's: I look only for slippage between what the design licenses and what the prose asserts. The causal discipline is genuinely good. The two slippages I do find are the unbenchmarked comparability claim (W12, Major) and the construct-label drift from "self-reported frequency of use" to "LMS engagement" in the abstract (W13, Minor), which contradicts the paper's own §2 commitment to treat the measure "as an indicator of perceived use rather than a behavioral count." Neither reverses the thesis; both are local overreach on top of an otherwise correctly hedged argument, which is a `warn` under my Phase 1 criterion, not a `block`.

Feasibility, since it is fair to weigh it: enrolment size, response rate, the deduplication rule, the incompleteness rule, the DV's five-category frequency distribution, r² = .18, and a CI or p for ρ = .40 are all zero-cost disclosures. Dimensionality evidence for the six-item scale, a reliability-corrected upper bound on the association, and a range-restriction check on the DV are re-analyses of the existing dataset. Only two requests need new data — a multi-item or log-based use measure, and demographics if they were never collected — and for those the honest revision is to state the constraint and drop the comparability claim, not to collect anything.

### S1: Complete and internally consistent uncertainty reporting for the headline coefficient

The estimate is reported with its interval, exact-form p bound, and n together, and the interval reproduces the standard Fisher-z computation at the reported precision. Many papers at this size report r and p alone.

**Evidence Anchor**: text: §4 "r = .42, 95% CI [.30, .52], p < .001, n = 214"

### S2: Causal restraint is structural, not cosmetic

The reverse pathway is stated as equally consistent with the data in the discussion itself, not quarantined in a limitations list, which is the correct treatment of a cross-sectional association and matches the design's actual licensing.

**Evidence Anchor**: text: §5 "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"

### S3: Measurement-level-appropriate robustness check is pre-specified

The ordinal nature of the outcome is recognised in the analysis plan and the Spearman check is declared there rather than introduced post hoc in results, which is the right order of operations.

**Evidence Anchor**: text: §3.4 "Because the use item is ordinal, we also computed a Spearman correlation as a robustness check"

### S4: The self-report/behavioural-trace distinction is named as a validity limit

The limitation is stated in the authors' own voice and anticipated in the literature review via Vasquez (2020), which is more than a formulaic caveat and partially earns the narrow framing of the contribution.

**Evidence Anchor**: text: §6 "LMS use was self-reported through a single item rather than measured through system logs"

### S5: The composite construction rule is stated explicitly

Because the scoring rule and item count are given, the descriptive statistics are auditable at all — this is what makes the GRIM-style reachability check in AR2 possible, and it passes.

**Evidence Anchor**: text: §3.2 "A perceived-usefulness score was computed as the mean of the six items"

### W1: Single-item ordinal outcome with no reliability evidence leaves the coefficient's magnitude unbounded

The outcome is one item, so no internal-consistency coefficient exists by construction, and no test-retest, parallel-indicator, or attenuation estimate is offered. Under the classical measurement model the observed r is bounded above by √(ρ_xx·ρ_yy), so .42 is a floor of unknown height. Until either a multi-item use measure is used or an explicit reliability assumption is stated and the disattenuated bound reported, the coefficient's magnitude cannot be interpreted as a quantity, only as a sign.

**Severity**: Major
**Evidence Anchor**: text: §3.2 "captured with a single five-point frequency item asking how often the respondent accessed the LMS"
**Confidence**: 5 — measurement error in single-item self-report instruments is my primary research area.

### W2: No sampling frame size, response rate, or demographics, so nonresponse bias cannot be bounded

233 responses arrived from an eligible population whose size is never stated, so no response rate can be computed and the achieved sample cannot be benchmarked against the registry on any characteristic except year-level coverage, itself reported only as an unquantified assertion. §6's voluntary-response sentence identifies the mechanism that would bias the association upward without constraining its direction or size.

**Severity**: Major
**Evidence Anchor**: absence: §3.1 participants reporting — expected the eligible undergraduate population size, a response or completion rate, and respondent demographics beyond year level; checked §3.1, §3.4, §4, §6, and the abstract
**Confidence**: 5 — survey nonresponse reporting standards are routine review territory for me.

### W3: Deduplication procedure is not reconcilable with the stated anonymity protocol as written

Five duplicate entries were removed, yet the ethics statement asserts that no identifying information was collected and that responses could not be linked to individual students. No detection mechanism is given. Response-vector matching is possible but would need a stated rule, since with six 1–5 items plus one 1–5 item genuine coincidences are not negligible; IP or device-based detection would contradict §3.3 outright. The methods and ethics accounts must be made mutually consistent, and the five exclusions re-justified under whichever mechanism was actually used.

**Severity**: Major
**Evidence Anchor**: text: §3.1, §3.3 "5 duplicate entries were removed", "No identifying information was collected"
**Confidence**: 4 — confident about the inconsistency on the page, less so about the survey platform's capabilities, which are undisclosed.

### W4: Outcome distribution is never reported, so range restriction and the assumption claims are unverifiable

The only statistic given for the five-category outcome is a median category, and its intermediate category labels never appear in §3.2, which names only anchors 1 and 5. §3.4 asserts that "both distributions were approximately symmetric" and that scatterplot inspection showed linearity and monotonicity, but no figure and no distributional numbers are provided. If the use item is ceiling-bounded — plausible for LMS access in a course-required system — the attainable maximum correlation is further compressed, which bears directly on the "moderate" characterization.

**Severity**: Major
**Evidence Anchor**: absence: §4 results for the single-item use variable — expected the full five-category frequency distribution or a figure evidencing the stated linearity and symmetry; checked §3.4, §4, §5, and §6 with no tables or figures present in the manuscript
**Confidence**: 5 — range restriction in coarse ordinal outcomes is directly within my teaching and review area.

### W5: α = .88 is reported without dimensionality evidence for an undescribed adaptation

Alpha presupposes essential unidimensionality and is not evidence of it. No factor structure, item-total correlations, or interval estimate for α is given, and the manuscript does not say what the adaptation of the Costa and Wren instrument changed. The claim that the measure is "previously validated" depends on an item-level equivalence that is neither shown nor described, and the six stems are not reproduced.

**Severity**: Major
**Evidence Anchor**: text: §3.2 "adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"
**Confidence**: 5 — reliability and dimensionality evidence for adapted scales is my core competence.

### W6: Shared-method covariance between predictor and outcome is never acknowledged

Both variables are self-reports collected from the same respondent in the same administration, which can inflate the observed association independently of any substantive relation. The manuscript applies the Vasquez (2020) caution only to the outcome's construct validity, never to the covariance between the two measures. Combined with W1, the two biases run in opposite directions and neither is bounded, so the reported magnitude has no defensible interval of interpretation even though its sign is secure.

**Severity**: Major
**Evidence Anchor**: absence: §3.4 and §5 treatment of measurement threats — expected acknowledgement that predictor and outcome come from one self-report instrument administered at one time, and any bound on shared-method covariance; checked §2, §3.2, §3.4, §5, and §6
**Confidence**: 4 — the mechanism is standard, though the magnitude of method inflation is contested in the literature.

### W7: Power statement is a post hoc sensitivity calculation presented as design justification

The calculation uses n = 214, which is the post-exclusion analytic sample and was unknowable at design time, and it concludes that "so the design was sensitive to small-to-moderate associations." The r ≥ .19 target has no stated provenance, no software or method is named, and under the standard Fisher-z approximation the achieved power at that n sits at approximately .80 rather than above it, so the ">.80" assertion is method-dependent. This should be relabelled as a sensitivity analysis or replaced with the actual a priori target and its source. I file no arithmetic receipt for this because power computation lies outside the four bounded recompute procedures.

**Severity**: Minor
**Evidence Anchor**: text: §3.4 "the study had greater than .80 power to detect a correlation of r >= .19", "so the design was sensitive to small-to-moderate associations"
**Confidence**: 4 — power conventions are familiar, but the borderline value depends on the unstated computational method.

### W8: Exclusion rule for incomplete submissions is undocumented and unexamined

Fourteen submissions were removed as incomplete with no operational definition (item-level missingness threshold, partial-progress cutoff, or straightlining screen) and no comparison of removed with retained cases on the observed variables. At 6% of receipts this cannot plausibly reverse the finding, but the rule should be stated and, ideally, the sensitivity of r to it reported.

**Severity**: Minor
**Evidence Anchor**: absence: §3.1 exclusion accounting — expected the operational rule defining an incomplete submission and any comparison of removed with retained cases; checked §3.1, §3.4, and §6
**Confidence**: 4 — standard missing-data documentation expectation, with modest decision impact at this exclusion rate.

### W9: Spearman robustness check is reported as a bare point estimate

ρ = .40 arrives with no interval, no p, and no n, and the robustness conclusion that the association "did not depend on the parametric assumption" is inferred from point-estimate proximity alone. Since no p or test statistic accompanies ρ, there is no recompute target for it either. Report the interval so the reader can judge overlap rather than take proximity on trust.

**Severity**: Minor
**Evidence Anchor**: text: §4 "The Spearman robustness check yielded a comparable coefficient (ρ = .40)"
**Confidence**: 5 — completeness of inferential reporting is a routine journal requirement.

### W10: No availability statement for data, analysis code, or the instrument

Neither the six adapted item stems nor the outcome item's full response labels are reproduced, and there is no data or code statement. The analysis is simple enough to be reproduced from the dataset, but the instrument cannot be re-administered or evaluated from the manuscript, which blocks the replication the paper itself calls for.

**Severity**: Minor
**Evidence Anchor**: absence: manuscript back matter following §7 — expected a data, analysis-code, or instrument availability statement and the six adapted item stems; checked §3.2, §3.4, §7, and the references
**Confidence**: 5 — reproducibility affordances are an explicit, checkable reporting standard.

### W11: Shared variance is characterised adjectivally rather than quantified

The variance-overlap discussion is entirely verbal where r² = .18 would state it in one number, and the same adjectival treatment ("moderately") carries the magnitude claim in the abstract, results, discussion, and conclusion. Give the number and a stated benchmark.

**Severity**: Minor
**Evidence Anchor**: text: §4 "The proportion of variance shared by the two measures was accordingly modest"
**Confidence**: 5 — effect-size reporting convention, straightforward to check.

### W12: The comparability claim to prior research is asserted with no benchmark and no attenuation adjustment

"Consistent with prior technology-acceptance research" appears in the abstract, discussion, and conclusion without a single prior estimate, interval, or stated comparison rule, so it is unfalsifiable as written. The paper's own literature review undercuts it twice: Song (2018) is cited for the finding that association strengths vary by institution, and Vasquez (2020) for the divergence of self-report from log measures. Prior estimates using multi-item or behavioural outcomes carry different attenuation, so comparing a single-item-outcome r to them without adjustment is not a like-for-like comparison. Either supply the benchmark estimates with an attenuation-aware comparison, or drop the claim.

**Severity**: Major
**Evidence Anchor**: text: Abstract "The association was consistent with prior technology-acceptance research"
**Confidence**: 4 — the methodological defect in the comparison is clear to me; the substantive benchmark values belong to the domain reviewer's dimension.

### W13: Construct label drifts from self-reported frequency to "engagement" in the abstract

The abstract's summative sentence converts a single self-reported frequency item into "LMS engagement," which is a broader construct that the design does not measure and which §2 explicitly disclaims by committing to treat the measure as an indicator of perceived use rather than a behavioural count. The discussion repeats the drift in describing perceived usefulness as one factor "bearing on engagement." The measured construct should be named consistently on every surface, especially the abstract.

**Severity**: Minor
**Evidence Anchor**: text: Abstract "perceived usefulness tracks with LMS engagement among undergraduates"
**Confidence**: 4 — construct-label consistency is checkable, though the drift is arguably stylistic rather than substantive here.

## Arithmetic Receipts

### AR1
procedure_id: p_from_test_statistic
evidence_anchor: text: §4 "r = .42, 95% CI [.30, .52], p < .001"
reported_inputs: Pearson product-moment r = .42; n = 214; reported bound p < .001; test of H0 rho = 0; stated analysis convention alpha = .05 two-tailed (§3.4)
assumptions: only what the paper licenses in §3.4 — approximate linearity, monotonicity, approximate symmetry of both distributions, and no extreme bivariate outliers, which license the standard t transform; df = n − 2 = 212 follows from the paper's own reported n; no one-tailed default and no equal-variance assumption imposed
tail_convention: two-tailed
derivation: t = r*sqrt(n−2)/sqrt(1−r^2) = .42*sqrt(212)/sqrt(1−.1764) = .42*14.5602/0.90752 = 6.1153/0.90752 = 6.739 on df = 212; the upper-tail area of the t distribution with df = 212 at t = 6.739 is of order 5e-11, doubled for the two-tailed convention the paper states
derived_value_or_range: two-tailed p of order 1e-10 and one-tailed p of order 5e-11, both many orders of magnitude below the reported .001 bound, so the verdict is invariant to tail choice
comparison_rule: the reported inequality holds if the derived p under the paper's stated tail convention is strictly less than .001
status: consistent

### AR2
procedure_id: grim
evidence_anchor: text: §4 "The 214 respondents reported a mean perceived-usefulness score of 3.6"
reported_inputs: reported composite mean M = 3.6 at one-decimal precision; N = 214 analyzed cases; six items each scored in integer steps 1 to 5 (§3.2); composite defined as the unweighted mean of the six items (§3.2)
assumptions: only what §3.1 and §3.2 license — six integer item scores per respondent, unweighted item mean, and complete item data for all 214 analyzed cases given that incomplete submissions were removed; no SD convention is needed for this check
derivation: the total of all item responses is an integer S over 6*214 = 1284 item scores, so attainable composite means are exactly S/1284; the reported 3.6 at one decimal requires 3.55 <= S/1284 < 3.65, i.e. 4558.2 <= S < 4686.6, giving the 128 integers S = 4559 through 4686, all inside the feasible range 1284 to 6420
derived_value_or_range: the attainable set {S/1284} intersected with [3.55, 3.65) is non-empty, corresponding to S = 4559 through 4686
rounding_interval: [3.55, 3.65) at one-decimal precision under round-half-up
nearest_achievable: 4622/1284 = 3.599688 and 4623/1284 = 3.600467, the adjacent attainable values straddling 3.6
comparison_rule: consistent if at least one attainable composite mean falls inside the rounding interval for the reported value; note this test has almost no discriminating power at 1284 item responses
status: consistent

### AR3
procedure_id: grimmer
evidence_anchor: text: §4 "(SD = 0.8) on the five-point scale"
reported_inputs: reported composite SD = 0.8 at one-decimal precision; M = 3.6; N = 214; six items scored 1 to 5; composite is the unweighted item mean
assumptions: the paper states no SD convention, so neither the n−1 sample divisor nor the n population divisor is assumed, and no distributional shape beyond the paper's approximate-symmetry statement is used
derivation: the documented GRIMMER procedure tests a reported SD against variances attainable from integer-scored responses, but here each respondent's composite is 1/6-granular rather than integer, so the attainable-variance set at N = 214 is the set of sums of squared deviations over 1284 integer item scores, which I did not enumerate; the unstated sample-versus-population divisor additionally shifts the attainable set at one-decimal precision, so extending the procedure here would exceed its documented boundary
derived_value_or_range: none derived, since no attainable-variance set was enumerated
comparison_rule: would test whether any attainable variance yields an SD inside [0.75, 0.85) under the divisor the paper actually used, once both the attainable set and the divisor are established
status: not_computable
not_computable_reason: reachability_not_completed

### AR4
procedure_id: n_from_df
evidence_anchor: absence: §3.4 and §4 inferential reporting — expected a test statistic with degrees of freedom for the correlation test or the Spearman check; checked §3.4, §4, §5, §7, and the abstract
reported_inputs: no degrees of freedom and no t, F, or chi-square value appear anywhere in the manuscript; the only reported quantities are r = .42, rho = .40, p < .001, and n = 214
assumptions: none beyond the paper's own reporting; the analytic n = 214 is read as reported rather than inferred
derivation: this procedure recovers an analytic N by inverting a test-specific df identity, and with no df reported at any point there is no input to invert, which makes the procedure inapplicable rather than blocked by ambiguity
derived_value_or_range: none, as no reported df exists to invert
comparison_rule: not exercised, since there is no reported df to compare against the reported n = 214
status: not_applicable
