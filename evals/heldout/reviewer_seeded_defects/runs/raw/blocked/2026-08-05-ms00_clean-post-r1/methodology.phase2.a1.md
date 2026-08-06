## Scoring Plan Dissent

*(omitted — my Phase 1 scoring plan holds for both eligible dimensions)*

contract_role: methodology

## Dimension Scores

### D1: methodology_rigor

score: warn
trigger: "specific rigor elements are thin or absent — for example missing response rate"

The reported inference is fully reconstructable: the manuscript gives the test family, coefficient, a 95% interval, a p value, the analytic n, a distributional robustness check, and a sensitivity statement. Case accounting is internally consistent (233 − 14 − 5 = 214), and the reported interval is the Fisher-z interval implied by r = .42 with n = 214, so nothing in the headline result is arithmetically unsupported. My Phase 1 block condition — a headline association asserted without a test statistic, effect size, uncertainty estimate, or analytic denominator, or an analysis invalid for the data structure with no correction offered — therefore does not fire. What does fire is the warn condition, and it fires on multiple independent elements: no sampling-frame size and hence no derivable response rate, no sample-composition benchmark, no stated completeness rule behind the 14 exclusions, no mechanism for the 5 duplicate removals, no structural-validity evidence for the adapted predictor scale, no reliability information for the outcome item, and no data, code, or instrument availability. Two design-level threats compound this: common method variance is never named, and the recruitment channel may be endogenous to the outcome. I record honestly that a reviewer weighting the joint interpretive damage rather than reconstructability could read this as block; I hold warn because every defect is repairable within the study as conducted (added denominator and composition data, deduplication disclosure, a factor analysis of existing item-level data, and reframing of what the coefficient estimates), and because I refuse to convert the paper's explicit scoping decision against log linkage, longitudinal waves, and multi-site sampling into a rejection ground.

### D2: domain_accuracy

score: not_assessed

Not eligible for the methodology seat under the contract.

### D3: argumentative_coherence

score: warn
trigger: "one construct substituted for a related but non-equivalent construct"

The inferential spine is unusually disciplined for this literature. The correlational-only commitment survives from abstract to conclusion, the reverse pathway is named and attributed, the practical implication is explicitly marked as suggested rather than proven, and the magnitude is not inflated in restatement. What triggers warn is localised construct drift in exactly the place the paper had already committed itself not to drift. Section 2 promises to "treat our self-report measure as an indicator of perceived use rather than a behavioral count," yet the abstract's closing sentence and the discussion both speak of "LMS engagement" and "engagement" without the self-report qualifier, silently widening a single-item perception measure into a behavioural construct that Vasquez (2020) is cited to distinguish from it. A second, smaller slippage transfers validation from Costa and Wren's original instrument to a six-item adaptation whose in-sample evidence is one alpha coefficient. Neither defeats the central claim, which is why this is warn and not block: the sentence-level repairs are small, but they are the difference between a claim the design licenses and one it does not.

### D4: cross_disciplinary_relevance

score: not_assessed

Not eligible for the methodology seat under the contract.

### D5: writing_and_structure

score: not_assessed

Not eligible for the methodology seat under the contract.

### D6: venue_fit_and_contribution

score: not_assessed

Not eligible for the methodology seat under the contract.

## Review Body

This is a modest, honestly framed cross-sectional survey whose reporting quality is above the median for its genre and whose interpretive discipline is genuinely good. My assessment is not that the authors have overclaimed in language; they have not. It is that the paper's single deliverable is the magnitude of one coefficient, and the manuscript does not establish what that coefficient estimates. Three mechanisms bear on the number in opposite directions and none is addressed: shared method inflates it, the unreliability of a single-item outcome attenuates it, and a recruitment channel that may sit inside the platform being measured truncates the low end of the outcome distribution. The net direction of bias is indeterminate on the information given, which means "positively and moderately associated" is currently a statement about a sample and an instrument pair rather than about perceived usefulness and LMS use. That is repairable, and none of the repairs requires the redesign the paper explicitly disclaims.

On sampling, the frame is stated in principle ("All enrolled undergraduates were eligible") but never in cardinality, so no response rate exists and the paper's own fourth limitation cannot be sized. Nothing in Section 3.1 lets a reader compare the 214 respondents with the enrolled population — year level is asserted to span all four but no counts are given — so the voluntary-response threat the authors correctly identify remains entirely unquantified. Separately, the deduplication claim and the anonymity claim sit in tension: identifying 5 duplicates in a survey where "no identifying information was collected, and responses could not be linked back to individual students" requires either some linkage artefact the paper does not disclose, in which case Section 3.3 is inaccurate as written, or a pattern-based judgement rule, in which case the exclusion criterion is unauditable. Either resolution is publishable; the current silence is not.

On measurement, an alpha of .88 is evidence of internal consistency and nothing more. It does not establish that six adapted items are unidimensional, and a mean composite presupposes exactly that. The manuscript never states what the adaptation changed from Costa and Wren's original, never reproduces the items, and never reports a factor structure, though the item-level data plainly exist and a confirmatory or exploratory analysis is a re-analysis rather than new data collection. On the outcome side, a single ordinal item carries unknown reliability; the Spearman check is a correct and welcome response to distributional form, but the authors should not be read — and, to their credit, do not claim — as having addressed reliability with it.

On analysis, the reporting is complete and the assumption checks are stated rather than implied, which I credit. Two residual points: the Fisher-z interval presumes a bivariate normal that a five-category outcome cannot instantiate, so the stated coverage is approximate and a bootstrap interval would cost nothing; and the Spearman coefficient is reported bare, so the robustness claim itself is unquantified. I also checked the sensitivity statement: with n = 214 the power at r = .19 sits essentially on the .80 boundary and whether it clears it depends on which standard-error convention the authors used. The substantive claim that the design is sensitive to small-to-moderate associations is correct, so I do not record this as a defect.

I have not scored the adequacy of the literature coverage or the value of the contribution; those belong to other seats. Where a presentation gap made a methodological claim unverifiable — absent item wording, absent composition data — I have logged it as an evidence gap rather than a writing complaint.

### S1: Inferential discipline is maintained across every section

The causal disclaimer is not confined to the limitations section; it is stated in the abstract, restated with attribution in the discussion, and preserved in the conclusion, and the reverse pathway is named rather than gestured at. This is the correct handling for a cross-sectional association and it is done without hedging so heavy that the claim becomes vacuous.

**Evidence Anchor**: text: Abstract "should not be read as causal, given the cross-sectional design"

### S2: Effect reporting is complete and internally consistent

The coefficient is reported with an interval, a p value, and the analytic n together in one place. The interval is exactly the one implied by the reported coefficient and sample size, so the three numbers are mutually consistent rather than independently asserted — a check that fails more often than reviewers assume.

**Evidence Anchor**: text: §4 "r = .42, 95% CI [.30, .52], p < .001, n = 214"

### S3: Assumption checks and design sensitivity are stated rather than assumed

Linearity, monotonicity, outlier presence, and distributional symmetry are each explicitly inspected before a Pearson coefficient is reported, and a sensitivity floor is given for the achieved sample. Both are ordinary good practice and both are ordinarily omitted.

**Evidence Anchor**: text: §3.4 "Scatterplot inspection showed an approximately linear, monotonic association with no extreme bivariate outliers" and "the study had greater than .80 power to detect a correlation of r >= .19 at alpha = .05 (two-tailed)"

### S4: Reliability is reported for the present sample, not imported

The alpha is estimated in this sample rather than cited from the source instrument. This is the minimum defensible practice for an adapted scale and it is frequently skipped in favour of citing the original validation.

**Evidence Anchor**: text: §3.2 "In the present sample, the scale showed good internal consistency (Cronbach's α = .88)"

### W1: Common method variance is neither identified nor remedied

Predictor and outcome share source, instrument, and administration occasion, which is the textbook configuration for method-variance inflation of a reported correlation. The manuscript never names the threat, considers no procedural remedy (item separation, differing response formats, temporal separation), and reports no statistical diagnostic. A post hoc statistical remedy is in fact foreclosed here because the outcome is a single item, so the honest repair is to state the threat, present r = .42 as an upper bound on the construct-level association from shared-method data, and stop describing the magnitude as if it estimated a construct relationship. The core claim of a positive association survives; the magnitude claim, which is the paper's actual payload, does not survive unqualified.

**Severity**: Major
**Evidence Anchor**: absence: Sections 3.2 through 3.4, 5, and 6 — expected explicit identification of common method variance as a threat to the reported correlation with at least one procedural or statistical remedy; checked Measures, Analysis, Results, Discussion, Limitations, and Abstract
**Confidence**: 5 — I have published on common method variance in acceptance research

### W2: The recruitment channel may be endogenous to the outcome measure

The survey was distributed through "the institution's course-announcement channel," and the manuscript never states whether that channel is internal to the LMS. If it is, students who rarely or never access the LMS could not have seen the invitation, so the sample is selected on the dependent variable and the low end of the outcome distribution is structurally truncated. That is a different and sharper problem than the voluntary-response bias acknowledged in Limitation 4: range restriction on the outcome biases the coefficient itself, not merely its generalisability. The fix is one sentence of disclosure plus, if the channel is LMS-internal, an explicit statement that the estimate is conditional on some baseline platform access. I flag the ambiguity rather than asserting the worse reading.

**Severity**: Major
**Evidence Anchor**: text: §3.1 "The survey was distributed through the institution's course-announcement channel over a three-week window"
**Confidence**: 4 — nonresponse and coverage error in web-administered institutional surveys is my primary area

### W3: No frame size, no response rate, and no composition benchmark

A population is defined but never counted, so no response or cooperation rate is derivable from any number in the manuscript. The consequence is not cosmetic: the authors themselves raise overrepresentation of institutionally engaged students as a limitation, and without a denominator that limitation cannot be assigned any magnitude, from negligible to disqualifying. The absence of any composition breakdown compounds this — the sample is said to span all four year levels, but with no counts there is no comparison against enrolment data and therefore no empirical purchase on nonresponse bias at all. Institutional registry figures make this a reporting repair, not new data collection.

**Severity**: Major
**Evidence Anchor**: text: §3.1 "All enrolled undergraduates were eligible" and "The analyzed sample of 214 students spanned all four year levels"
**Confidence**: 5 — reporting standards for response rates in institutional surveys are directly my field

### W4: Duplicate detection is unexplained and sits in tension with the anonymity claim

Five entries were removed as duplicates from a survey the paper describes as collecting no identifying information and producing responses that could not be linked to individual students. Detecting duplicates requires some persistent artefact — a device or session token, an IP address, a single-use link, an authenticated session — and if one existed, the Section 3.3 characterisation is inaccurate and the ethics statement needs correcting. If instead duplicates were inferred from response patterns, the exclusion rule is a discretionary judgement and is currently unstated, unreproducible, and capable of removing valid cases. The numerical impact on the coefficient is negligible at 5 of 233 responses; I band this Major on its own impact because it concerns an internal inconsistency between two methods claims, one of them about human-subjects protection, that an editor must resolve before acceptance rather than after.

**Severity**: Major
**Evidence Anchor**: text: §3.1 and §3.3 "14 incomplete submissions and 5 duplicate entries were removed" and "No identifying information was collected, and responses could not be linked back to individual students"
**Confidence**: 4 — anonymous web-survey administration and deduplication practice is within my routine work

### W5: The predictor scale's validity evidence is limited to a single reliability coefficient

The instrument is described as adapted, but nothing states what the adaptation changed, and the items are not reproduced anywhere. Validity evidence for the six-item version in this sample consists solely of alpha, which speaks to internal consistency and is compatible with a multidimensional item set; the mean composite used in the analysis nevertheless assumes unidimensionality. No exploratory or confirmatory factor analysis is reported, and no argument is offered that Costa and Wren's validation population resembles this one. Because the item-level responses already exist, a structural analysis is a re-analysis, and reproducing the six items is a short appendix. Until then the reader cannot know whether the composite score means what the construct label says.

**Severity**: Major
**Evidence Anchor**: text: §3.2 "measured using a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"
**Confidence**: 5 — validity limits of adapted self-report scales is my specialisation

### W6: The single-item outcome has unknown reliability and attenuation is never considered

A one-item frequency measure carries no estimable reliability in a single administration, so its unreliability attenuates the observed correlation by an unknown factor. The paper's second limitation correctly raises the self-report-versus-log validity gap, which is a different issue, and the Spearman check addresses distributional form, also a different issue. Neither touches attenuation. The repair is interpretive rather than analytic: the reported magnitude should be presented as jointly subject to shared-method inflation and measurement attenuation, with the net direction unresolved.

**Severity**: Minor
**Evidence Anchor**: text: §3.2 "captured with a single five-point frequency item asking how often the respondent accessed the LMS in a typical week"
**Confidence**: 5 — the validity limits of single-item measures is a stated specialisation

### W7: The interval estimate and the robustness check are each under-specified

The 95% interval is the normal-theory Fisher-z interval, whose bivariate-normality premise a five-category ordinal variable cannot satisfy; with n = 214 the interval is probably serviceable, but its coverage is approximate and the manuscript does not say so. A percentile bootstrap interval would settle this at no cost. Relatedly, the Spearman coefficient is reported as a bare point value with no interval and no p, so the sentence claiming the association "did not depend on the parametric assumption" is asserted rather than quantified.

**Severity**: Minor
**Evidence Anchor**: text: §3.4 and §4 "we report the correlation coefficient alongside its 95% confidence interval, p value, and sample size" and "The Spearman robustness check yielded a comparable coefficient"
**Confidence**: 4 — standard interval estimation for correlations with ordinal indicators

### W8: Exclusions and missing data are reported as counts without a policy

Fourteen submissions were removed as incomplete, but the manuscript never defines completeness, never reports item-level missingness among retained cases, and never compares removed with retained respondents on any observed variable. Partial responders are a substantively informative group in engagement research, and a two-line comparison would either dispel or confirm the concern that they differ systematically from completers.

**Severity**: Minor
**Evidence Anchor**: absence: §3.1 and §3.4 — expected a stated completeness criterion for the 14 removed submissions plus item-level missingness and any comparison of removed with retained cases; checked Design and participants, Measures, Analysis, and Results
**Confidence**: 4 — routine missing-data reporting practice in survey research

### W9: No data, code, or instrument availability

There is no availability statement for the response data, no analysis specification beyond prose, and no appendix reproducing the six adapted items. The analysis is simple enough that a reader could re-run it given the data, which makes the omission easy to fix and correspondingly hard to justify; the instrument omission additionally prevents any future study from replicating the adapted measure.

**Severity**: Minor
**Evidence Anchor**: absence: whole manuscript including §3 and the reference list — expected a data, analysis-code, or instrument availability statement or an appendix reproducing the six adapted items; checked Methods subsections, Results, Discussion, Limitations, Conclusion, and References
**Confidence**: 4 — reproducibility affordances expected of survey reports in this literature

### W10: Construct drift from self-reported use to "engagement"

Having committed in Section 2 to treating the measure as an indicator of perceived use rather than a behavioural count, the manuscript then states its finding in terms of "LMS engagement" in the abstract and "engagement" in the discussion. That is a broader construct than a single self-reported weekly frequency item, and it is precisely the construct the cited measurement caution says self-report does not deliver. The Results paragraph gets this right with "reported engagement," which shows the authors know the distinction; the fix is to apply the same qualifier in the two sections readers weight most.

**Severity**: Minor
**Evidence Anchor**: text: Abstract and §5 "The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates" and "perceived usefulness is at best one of several factors bearing on engagement"
**Confidence**: 4 — construct-to-measure correspondence is core measurement territory

### W11: The abstract transfers validation from the original instrument to the adaptation

Describing the measure as "an adapted, previously validated instrument" lets one clause carry both the fact of adaptation and the authority of the original validation, when validation does not transfer across adaptation without evidence. This is the presentational face of W5 and is independently repairable: even with a factor analysis added, the abstract should say what was adapted and what validity evidence applies to the adapted version; and rewording alone would not close the evidence gap.

**Severity**: Minor
**Evidence Anchor**: text: Abstract "Perceived usefulness was measured with an adapted, previously validated instrument"
**Confidence**: 5 — instrument adaptation and validity transfer is my specialisation

## Arithmetic Receipts

### AR1

procedure_id: p_from_test_statistic
evidence_anchor: text: §4 "Perceived usefulness was positively and moderately associated with self-reported LMS use, r = .42, 95% CI [.30, .52], p < .001, n = 214"
reported_inputs: Pearson product-moment correlation r = .42; analytic n = 214; reported significance claim p < .001; alpha = .05 two-tailed stated in §3.4; no t or df reported by the authors.
assumptions: paper-licensed only — the coefficient is the Pearson correlation stated in §3.4 estimated on all 214 analysed cases (§4), and the null distribution is the standard zero-correlation reference for a Pearson r with df = n - 2; no re-specification of the test family is imposed.
derivation: t = r*sqrt(n-2)/sqrt(1-r^2) = 0.42*sqrt(212)/sqrt(1-0.1764) = 6.1153/0.90752 = 6.738 on df = 212; Wallace normal approximation z = sqrt(212*ln(1+6.738^2/212))*(1697/1699) = sqrt(41.150)*0.998823 = 6.407, giving upper-tail probability about 7.4e-11, doubled for the two-sided test.
tail_convention: two-tailed
derived_value_or_range: two-tailed p approximately 1.5e-10; one-tailed p approximately 7.4e-11
comparison_rule: the reported value is an inequality claim, so consistency requires the derived p to be strictly below .001; the verdict is checked under both tails and is identical either way, so no boundary sensitivity exists.
status: consistent

### AR2

procedure_id: grim
evidence_anchor: text: §4 "mean perceived-usefulness score of 3.6 (SD = 0.8) on the five-point scale"
reported_inputs: composite mean M = 3.6 reported to one decimal; n = 214 analysed respondents; six items per respondent; five-point Likert response scale from 1 to 5; composite defined as the unweighted mean of the six items.
assumptions: paper-licensed only — item responses are integers 1 to 5 per the §3.2 scale definition, the composite is the unweighted six-item mean per §3.2, and all 214 retained cases have all six items present because §3.1 states incomplete submissions were removed; standard rounding to one decimal.
derivation: the sample mean equals the sum of 1284 integer item responses divided by 1284, so attainable values are k/1284 for integer k; 3.6*1284 = 4622.4, which is not an integer, so the reported value is not exactly attainable, but k = 4622 yields 3.599688 and k = 4623 yields 3.600467, both of which round to 3.6 at one decimal; granularity 1/1284 = 0.00078 is far finer than the reporting precision, so roughly 128 attainable values lie inside the rounding target.
rounding_interval: 3.55 up to but excluding 3.65 rounds to 3.6 at one decimal
nearest_achievable: 4622/1284 = 3.599688 and 4623/1284 = 3.600467
derived_value_or_range: attainable means straddling the reported value are 3.599688 and 3.600467, both inside the rounding target
comparison_rule: consistent if at least one attainable k/1284 falls inside the rounding target; at this granularity the test is non-diagnostic, so a consistent verdict is weak evidence and not corroboration of the mean.
status: consistent

### AR3

procedure_id: grimmer
evidence_anchor: text: §4 "The 214 respondents reported a mean perceived-usefulness score of 3.6 (SD = 0.8)"
reported_inputs: composite SD = 0.8 reported to one decimal alongside M = 3.6; n = 214; six integer items per case; case-level composite values restricted to multiples of 1/6 between 1 and 5.
assumptions: paper-licensed only — integer item responses and an unweighted six-item mean per §3.2 with complete cases per §3.1; no standard-deviation denominator convention is assumed, because neither §3.4 nor §4 states whether the reported SD uses n-1 or n.
derivation: completing this procedure requires enumerating attainable sums of squared deviations for 214 case scores drawn from the 25-value lattice of sixths that simultaneously reproduce an attainable mean inside the AR2 rounding target, then testing whether any such configuration yields an SD rounding to 0.8; I did not complete that enumeration, and at this granularity and sample size the feasible set is dense enough that the test is expected to be non-diagnostic in any case, so I decline to state a verdict rather than assert one.
derived_value_or_range: not derived; no feasible standard-deviation set enumerated for the target of 0.75 up to but excluding 0.85
comparison_rule: would require at least one attainable sum of squared deviations whose standard deviation falls inside the stated target under a named n-1 or n convention; the rule was not applied.
status: not_computable
not_computable_reason: reachability_not_completed

### AR4

procedure_id: n_from_df
evidence_anchor: absence: §3.4 and §4 — expected a reported test statistic with its degrees of freedom from which the analytic N could be back-derived; checked the Analysis subsection, both Results paragraphs, the Abstract, and the Conclusion
reported_inputs: n = 214 is stated directly for the correlation in the Abstract, §3.4, §4, §6, and §7; no t, F, chi-square, or model degrees-of-freedom term appears anywhere in the manuscript.
assumptions: none beyond the manuscript's own statement that the correlation was estimated on 214 analysed cases.
derivation: this procedure inverts a named test-specific degrees-of-freedom identity to recover N and then compares it with the reported N; with no degrees-of-freedom term reported anywhere in the manuscript there is no quantity to invert, so the procedure has no input surface here and extending it to a df I supplied myself would exceed its boundary.
derived_value_or_range: none derivable; no degrees of freedom reported
comparison_rule: not applied; the procedure requires a manuscript-reported degrees-of-freedom value to compare against the reported sample size.
status: not_applicable
