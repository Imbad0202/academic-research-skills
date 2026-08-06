contract_role: methodology

## Dimension Scores

### D1: methodology_rigor
score: block
trigger: "A load-bearing methodological component is absent or unverifiable"
block_class: repairable

The analysis itself is competently executed and internally reconcilable — the disposition chain (233 − 14 − 5 = 214) holds across Abstract, §3.1, §4 and §7, the reported 95% CI [.30, .52] is exactly what a Fisher-z interval on r = .42 with n = 214 returns, and GRIM/GRIMMER checks on M = 3.6 (SD = 0.8) are satisfied. What fails is verifiability of the measurement and of the sample. The sole predictor is a six-item instrument whose items are never reproduced, whose adaptation from Costa and Wren (2019) is never described, and whose dimensionality is never tested in this sample — α = .88 presumes essential unidimensionality rather than demonstrating it, and is reported without an interval. The sole outcome is a single ordinal item for which no reliability coefficient is estimable in principle, yet the headline estimate and its normal-theory interval are interpreted as a construct-level "moderate" association with no attenuation accounting. The sampling account has no denominator, so 233 responses and 214 analyzed cases cannot be converted into any response rate; the sample is described only as having "spanned all four year levels." And §3.1's removal of five duplicates cannot be reconciled as written with §3.3's claim that no identifying information was collected and responses could not be linked to individuals. Each of these is load-bearing: an independent analyst cannot reconstruct the instrument, the eligible frame, or the exclusion rule from the text. I record this as repairable rather than fatal because nothing in the reported arithmetic is impossible, ethics approval and consent are stated, the rank-based check corroborates that a positive association exists, and every gap can be closed by disclosure the authors hold plus re-estimation with methods appropriate to a single ordinal outcome.

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: warn
trigger: "The overall argument holds but is locally miscalibrated"

The argumentative spine is unusually disciplined for this literature: the causal disclaimer is explicit and repeated, the reverse pathway is named and attributed, the self-report measure is framed as capturing perceived rather than behavioral engagement, and the limitations genuinely bound the claims that precede them. The miscalibration is local and lexical rather than structural. Three instances: the Abstract's "adapted, previously validated instrument" transfers the source instrument's validation to an adapted form for which no validity evidence in this sample exists; the magnitude descriptor "moderately" is asserted at the construct level in Abstract, §4, §5 and §7 while the outcome's reliability is unknowable, so the descriptor is a property of the observed pair of measures rather than of the constructs; and §4's claim that the Spearman check shows the association "did not depend on the parametric assumption" overstates what a rank correlation establishes, since the reported interval remains normal-theory. None of this is a causal claim, and the tested conclusion (a positive association exists) is the conclusion drawn, so the overreach does not reach my block threshold. Each instance is correctable by rewording plus the attenuation discussion requested under D1, without altering the substantive finding.

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

This is a carefully written, deliberately modest correlational report, and I want to be clear at the outset that my block on D1 is not a judgement about ambition or honesty. The manuscript's rhetoric is better calibrated than most technology-acceptance submissions I review: it declines causal language, names the reverse pathway, cites the self-report/log-data divergence literature against its own measure, and reports uncertainty rather than a bare p-value. Where it fails is upstream of the rhetoric. A correlation between two measures is only interpretable to the extent that both measures are documented and their reliability is characterisable, and here one instrument is invisible and the other is a single item.

Take the predictor first. Six items, adapted, no items shown, no statement of what the adaptation changed, no appendix, and no in-sample structural evidence. Cronbach's α = .88 is offered as the whole psychometric case, but α is a lower bound on reliability under essential unidimensionality — it does not test that condition, and a two-factor six-item set with correlated factors will routinely return α in the high .80s. Since the analysis uses an unweighted mean of the six items, unidimensionality is not an optional nicety; it is the assumption that licenses the composite. What I need in revision is the adapted items verbatim, a description of the adaptation (wording changes, referent substitution, items dropped or added, and whether the response format was altered), a CFA or at minimum an EFA with the factor solution and loadings in this sample, and α with a confidence interval.

Now the outcome. One five-point frequency item carries the entire dependent variable. No reliability coefficient can be computed for it, so the amount of attenuation in r = .42 is not merely unestimated but unbounded by anything in the manuscript. This has a direct consequence the paper never draws: the construct-level association is necessarily at least as large as .42 and could be materially larger, so "moderate" is a statement about the instruments, not about perceived usefulness and LMS use. The 95% CI compounds this. As I verify below, the interval is exactly the Fisher-z interval, which is the right computation given the inputs — but its nominal coverage rests on approximate bivariate normality, and one arm of the pair is a five-category ordinal item whose full frequency distribution is never shown. The Spearman check addresses monotonicity and rank robustness; it says nothing about the interval's coverage. In revision I would want a polyserial or polychoric estimate as the primary or a co-primary estimate, a percentile bootstrap interval alongside the normal-theory one, and an explicit paragraph on attenuation that states what the observed coefficient can and cannot be read as.

The sampling accounting is the third front. "All enrolled undergraduates were eligible" defines a frame without ever giving its size, so no response rate exists and 214 cannot be located anywhere on a participation scale — the manuscript's own fourth limitation, about volunteer overrepresentation, is therefore unbounded in magnitude as well as in direction. Independently, the duplicate-removal and anonymity statements are in tension as written. I can imagine non-identifying duplicate-detection signals (session tokens, identical response vectors with adjacent timestamps, hashed link parameters), and I do not assume misconduct; but exactly which signal was used, and whether it is compatible with the anonymity assertion that underwrites §3.3, has to be stated rather than left to a reviewer's imagination. The sample description is thinner still: no year-level distribution, no discipline mix, no gender or age breakdown, no comparison with the institutional population. A single-site estimate whose site is uncharacterised gives the reader nothing to reason with about transportability.

Two smaller reporting matters deserve fixing because the information plainly exists. The sensitivity statement is welcome and rare, but it is unlabelled as to whether it was computed before or after data collection, and no software is named. On my own check — and I flag that power computation is outside the bounded recompute procedures I report receipts for, so this is my arithmetic, not an audited receipt — the standard Fisher-z approximation with n = 214 gives SE = 1/sqrt(211) = .0688, so the correlation attaining exactly .80 power at two-tailed alpha = .05 is tanh((1.960 + 0.842) × .0688) = .1905; achieved power at r = .19 is therefore about .798. That is marginally below, not "greater than", .80. Separately, §4 describes the shared variance in prose ("accordingly modest") but never prints it; r² = .1764, i.e. about 18%, and the sentence would be stronger with the number in it.

Reproducibility affordances are absent as a class: no data availability statement, no analysis code, no instrument in an appendix, no software or version named, and no account of the missingness behind the 14 removed submissions or of item-level missingness among the retained 214. None of this is exotic to supply.

### S1: Correlational discipline is maintained, not merely announced
The anti-causal commitment is stated in the Abstract, argued in §5 with the reverse pathway named and attributed to Delgado (2020), and honoured in the wording of §7. The practical implication about onboarding is explicitly marked as suggested rather than proven. This is the standard I wish more acceptance-model submissions met.
**Evidence Anchor**: text: §5 "the correlation cannot establish that perceived usefulness causes use"
**Confidence**: 5 — direct reading of claim language against the design.

### S2: The estimate is reported with uncertainty, and the interval is internally reproducible
The results sentence carries the coefficient, a 95% interval, the p value and n together. Recomputing from r = .42 and n = 214 by Fisher z (z = .4477, SE = 1/sqrt(211) = .0688) returns limits of .3029 and .5246, which round to exactly the reported [.30, .52]. This is not one of the four bounded procedures I emit receipts for, so I record it as reviewer verification rather than an audited receipt, but it is a real internal-consistency success.
**Evidence Anchor**: text: §4 "95% CI [.30, .52]"
**Confidence**: 4 — routine Fisher-z arithmetic, hand-checked once.

### S3: A sensitivity statement is offered at all
Reporting the detectable effect size at n = 214 rather than asserting adequacy is good practice, and the framing correctly points at small-to-moderate detectability rather than claiming power for a specific alternative.
**Evidence Anchor**: text: §3.4 "so the design was sensitive to small-to-moderate associations"
**Confidence**: 4 — standard sensitivity-reporting norm.

### S4: The self-report measure is framed as what it is
§2 anticipates the log-data critique, cites Vasquez (2020) against the manuscript's own instrument, and commits to reading the item as perceived use. §6 repeats the constraint. A measurement critique the authors raise themselves is worth more than one a reviewer has to supply.
**Evidence Anchor**: text: §2 "treat our self-report measure as an indicator of perceived use rather than a behavioral count"
**Confidence**: 5 — direct textual reading.

### S5: The case-disposition arithmetic reconciles across the manuscript
233 received, 14 incomplete and 5 duplicates removed, 214 analyzed; the 214 figure is then used consistently in the Abstract, §3.1, §4, §6 and §7 with no drift.
**Evidence Anchor**: text: §3.1 "A total of 233 responses were received"
**Confidence**: 5 — single-step arithmetic, cross-checked at four locations.

### S6: Limitations constrain rather than decorate
Each of the four limitations names a specific inferential restriction, and §7 repeats the bounding rather than reverting to a broader claim, which is where papers of this type usually leak.
**Evidence Anchor**: text: §6 "response was voluntary, so students who engage more with institutional channels may be overrepresented"
**Confidence**: 4 — comparison of limitation text with conclusion text.

### W1: The predictor instrument is neither reproduced nor shown to be unidimensional
No items, no adaptation record, no appendix, and α = .88 as the sole psychometric evidence for a mean composite whose validity depends on essential unidimensionality that α cannot establish. As written, no reader can determine what construct r = .42 involves, and no independent team can administer the same measure. Required: items verbatim, documented adaptation, CFA or EFA with loadings in this sample, and α with an interval.
**Severity**: Critical
**Evidence Anchor**: text: §3.2 "measured using a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"
**Confidence**: 5 — core psychometric reporting requirement; α/dimensionality distinction is standard.

### W2: A single ordinal item carries the outcome, so attenuation is unbounded and the parametric interval is unlicensed
No reliability is estimable for one item, so the distance between r = .42 and the construct-level association is unknown; the normal-theory interval additionally presumes approximate bivariate normality on a five-category variable. The magnitude descriptor "moderate" is consequently a property of the instruments. Required: polyserial or polychoric estimation, a bootstrap interval, and an explicit attenuation discussion.
**Severity**: Major
**Evidence Anchor**: text: §3.2 "captured with a single five-point frequency item asking how often the respondent accessed the LMS in a typical week"
**Confidence**: 5 — attenuation and ordinal-treatment consequences are my primary area.

### W3: No eligible-population denominator, therefore no response rate
The frame is asserted to be all enrolled undergraduates but its size is never given, so neither 233 nor 214 can be interpreted as participation, and the manuscript's own volunteer-bias limitation cannot be sized. Required: enrolment figure, invitation count, response and completion rates.
**Severity**: Major
**Evidence Anchor**: absence: §3.1 sampling account — expected the eligible-population denominator with response and completion rates; checked §3.1, §3.3, §4, §6, Abstract
**Confidence**: 5 — survey-reporting minimum.

### W4: Duplicate removal and the anonymity claim cannot both stand as written
Five duplicates were identified and removed, yet no identifying information was collected and responses could not be linked to individuals. A non-identifying detection signal could reconcile these, but the mechanism is undisclosed, so the exclusion rule is unreproducible and the anonymity assertion underwriting §3.3 is unverified. Required: the detection signal, its non-identifying status, and whether the ethics approval covered it.
**Severity**: Major
**Evidence Anchor**: text: §3.1 and §3.3 "5 duplicate entries were removed" and "No identifying information was collected, and responses could not be linked back to individual students"
**Confidence**: 4 — the tension is textual and clear; benign reconciliations exist but are not stated.

### W5: The analyzed sample is essentially undescribed
"Spanned all four year levels" is the only compositional information given: no year distribution, no discipline mix, no gender or age, no comparison with institutional figures. Nothing supports judging to whom the estimate applies, which is the load the single-site framing places on the sample description. Required: a participant table with a population comparison.
**Severity**: Major
**Evidence Anchor**: text: §3.1 "The analyzed sample of 214 students spanned all four year levels."
**Confidence**: 5 — standard participant-reporting requirement.

### W6: The sensitivity claim is unlabelled and sits marginally outside the stated threshold
Neither a priori nor post hoc is declared, and no software is named. On the standard Fisher-z approximation the r delivering exactly .80 power at n = 214 and two-tailed alpha = .05 is .1905, so achieved power at r = .19 is about .798 — just under "greater than .80". Required: the label, the software, and either .19 restated as approximately .80 power or the threshold moved to .20.
**Severity**: Minor
**Evidence Anchor**: text: §3.4 "the study had greater than .80 power to detect a correlation of r >= .19 at alpha = .05 (two-tailed)"
**Confidence**: 3 — the labelling gap is certain; the boundary arithmetic depends on their method, since exact noncentral routines may differ in the third decimal.

### W7: Descriptives are incomplete on both variables
A median category is given for the ordinal outcome with no frequency distribution across the five levels, so neither floor and ceiling behaviour nor the plausibility of the linearity claim can be assessed; and the shared variance is described in prose but never printed, though r² = .1764 (about 18%).
**Severity**: Minor
**Evidence Anchor**: text: §4 "The proportion of variance shared by the two measures was accordingly modest"
**Confidence**: 5 — a full ordinal frequency table is a routine expectation.

### W8: No reproducibility affordances of any kind
No data, code, or instrument availability statement, and no analysis software or version identified, so nothing about the pipeline from responses to r = .42 can be independently re-executed.
**Severity**: Minor
**Evidence Anchor**: absence: §3.4 and end matter — expected data, code, and adapted-instrument availability statements plus named analysis software; checked §3.3, §3.4, §4, References
**Confidence**: 4 — availability statements are now venue-standard in this literature.

### W9: Complete-case exclusion is reported without any missingness account
Fourteen incomplete submissions were dropped with no description of how much or where data were missing, no comparison of completers with non-completers, and no statement about item-level missingness or imputation among the retained 214 — the last also bearing on the granularity assumption in my GRIM and GRIMMER receipts.
**Severity**: Minor
**Evidence Anchor**: absence: §3.1 exclusion reporting — expected the missingness pattern behind 14 removed submissions and a completer/non-completer comparison; checked §3.1, §3.2, §3.4, §4
**Confidence**: 4 — the pattern is probably benign at this volume, but it is unreported.

### W10: The robustness check is credited with more than a rank correlation can establish
Spearman ρ = .40 supports monotonicity and rank stability; it does not address the normal-theory basis of the reported interval, which remains the only uncertainty statement in the paper. Required: reword the claim and add a bootstrap or rank-based interval.
**Severity**: Minor
**Evidence Anchor**: text: §4 "indicating that the association did not depend on the parametric assumption"
**Confidence**: 5 — the distinction between coefficient robustness and interval coverage is unambiguous.

### W11: The Abstract transfers the source instrument's validation to the adapted form
Validity evidence does not travel across adaptation, and the manuscript supplies none for the adapted version in this sample. The Abstract is where editors and most readers form their view of the measurement warrant, so the phrasing materially overstates it. This finding is scored under D3 and is deliberately not counted again in the D1 severity attaching to W1.
**Severity**: Major
**Evidence Anchor**: text: Abstract "Perceived usefulness was measured with an adapted, previously validated instrument"
**Confidence**: 5 — standard measurement-validity principle.

## Arithmetic Receipts

### AR1
procedure_id: p_from_test_statistic
evidence_anchor: text: §4 "r = .42" and "p < .001, n = 214"
reported_inputs: Pearson product-moment r = .42; n = 214; reported p as the inequality p < .001; alpha = .05 with a two-tailed convention stated in §3.4; no test statistic and no degrees of freedom reported anywhere.
assumptions: The paper's own two-tailed alpha statement in §3.4 is taken as its inferential convention for the same correlation analysis, not imposed as a default; the standard t-transform of a Pearson r on df = n - 2 = 212 is used because §3.4 declares Pearson estimation; no interval-level measurement claim is needed for the transform's arithmetic, and its substantive appropriateness is challenged separately in W2.
derivation: t = r * sqrt(n - 2) / sqrt(1 - r^2) = .42 * sqrt(212) / sqrt(1 - .1764) = .42 * 14.5602 / 0.90752 = 6.7385 on df = 212; the two-tailed .001 critical value at df = 212 is about 3.34, and 6.74 far exceeds it, so p is bounded well below .001 under either tail.
tail_convention: two-tailed
derived_value_or_range: two-tailed p < 1e-8; one-tailed p < 5e-9 (both from t = 6.74 on df = 212), so the reported inequality holds under either tail choice and the verdict does not turn on the tail.
comparison_rule: The reported inequality p < .001 is satisfied if the derived p is strictly less than .001, equivalently if |t| exceeds the two-tailed .001 critical value for df = 212 (about 3.34).
status: consistent

### AR2
procedure_id: grim
evidence_anchor: text: §4 "mean perceived-usefulness score of 3.6 (SD = 0.8)"
reported_inputs: M = 3.6 at one-decimal precision; n = 214 analyzed cases; composite defined in §3.2 as the unweighted mean of six items each rated on an integer five-point scale from 1 to 5, giving per-case granularity 1/6 and grand-mean granularity 1/(6 * 214) = 1/1284.
assumptions: Integer 1-to-5 item scoring and a six-item unweighted mean are stated in §3.2, so the integer-scale premise is licensed by the text rather than assumed; all 214 analyzed cases are taken to be complete on all six items, which §3.1's removal of incomplete submissions supports but does not state item by item (see W9).
derivation: A one-decimal mean of 3.6 requires an integer total item-sum S = 1284 * mean with 3.55 <= S/1284 < 3.65, i.e. 4558.2 <= S < 4686.6, so S is any of the 128 integers 4559 through 4686; the two attainable means bracketing 3.6 are 4622/1284 = 3.599688 and 4623/1284 = 3.600467, both of which round to 3.6, so the reported mean is reachable.
derived_value_or_range: The rounding interval [3.55, 3.65) contains 128 attainable composite means spaced 1/1284 = 0.000779 apart, so the reported mean is attainable; at this n and granularity GRIM is satisfied but non-diagnostic.
rounding_interval: [3.55, 3.65) — the interval a value must fall in to round to 3.6 at one decimal under half-up rounding.
nearest_achievable: 4622/1284 = 3.599688 and 4623/1284 = 3.600467, the adjacent attainable composite means straddling the reported 3.6.
comparison_rule: Half-up rounding to one decimal; consistency requires at least one attainable value of the form S/1284 with S an integer to fall inside the rounding interval.
status: consistent

### AR3
procedure_id: grimmer
evidence_anchor: text: §4 "(SD = 0.8)" with §3.2 "computed as the mean of the six items"
reported_inputs: SD = 0.8 at one-decimal precision; M = 3.6; n = 214; composite is the mean of six integer 1-to-5 items, so each case value is a multiple of 1/6 within [1, 5].
assumptions: The SD divisor is not stated in the manuscript, so the check is run under both the n - 1 and the n convention rather than defaulting to a sample SD; integer item scoring per §3.2; complete item data for all 214 cases; rescaling y = 6x maps composites onto integers 6 through 30, so the sum S and the sum of squares Q are integers with matching parity.
derivation: With y = 6x, S is one of 4559 through 4686 from AR2 and the target SD_y = 6 * 0.8 = 4.8 with interval [4.5, 5.1), i.e. variance_y in [20.25, 26.01); for the representative S = 4622, S^2/n = 21362884/214 = 99826.5607, so under the n - 1 convention Q must satisfy 104139.81 <= Q < 105366.69 with Q even to match the parity of S, which admits about 613 attainable values, and the n convention shifts the window by roughly 0.5% without emptying it.
derived_value_or_range: Under the n - 1 convention Q ranges over the even integers from 104140 to 105366 (about 613 values) and the reported SD is attainable, for example Q = 104734 giving SD_x = 0.799993 and Q = 104736 giving SD_x = 0.800156; the n convention yields an equally non-empty set, so GRIMMER is satisfied but non-diagnostic at one-decimal precision.
rounding_interval: [0.75, 0.85) for SD_x at one decimal, equivalently SD_y in [4.5, 5.1) and variance_y in [20.25, 26.01).
nearest_achievable: With S = 4622 under the n - 1 convention, Q = 104734 gives SD_x = 0.799993 and Q = 104736 gives SD_x = 0.800156, the adjacent attainable values straddling the reported 0.8.
comparison_rule: Half-up rounding to one decimal; consistency requires at least one integer Q of the parity of S yielding an SD inside the rounding interval under at least one divisor convention the paper leaves open, and here both conventions qualify.
status: consistent

### AR4
procedure_id: n_from_df
evidence_anchor: absence: §3.4 and §4 inferential reporting — expected a test statistic with its degrees of freedom for the reported correlation test; checked §3.4, §4, Abstract, §7
reported_inputs: No degrees-of-freedom value appears anywhere in the manuscript; §4 reports only r = .42, the 95% interval, p as an inequality, and n = 214.
assumptions: None beyond the text as written; df is not imputed from n, because this procedure recovers an analytic N from a reported df rather than the reverse.
derivation: The procedure requires a reported df together with a named test identity to invert; with no df reported there is nothing to invert, and reconstructing df = n - 2 = 212 from the reported n would audit my own arithmetic rather than the manuscript's.
derived_value_or_range: Not derived; no reported df exists to invert against N = 214.
comparison_rule: Not applied; the procedure has no reported df input to compare with the analyzed N of 214.
status: not_applicable
