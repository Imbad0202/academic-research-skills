contract_role: methodology

## Dimension Scores

### D1: methodology_rigor

score: block
trigger: "A quantitative conclusion rests on a procedure that is not recoverable or not defensible as reported"
block_class: repairable

Two of the example clauses under this trigger fire, each in a modified form that I state precisely rather than overclaim. The exposure instrument's items are nowhere given and the adaptation from the validated original is undocumented, so its scores cannot be interpreted or compared with the prior estimates the paper positions itself against — the response *format* is disclosed, the item *content* is not. And the analytic sample is reconciled against its exclusions (233 − 14 − 5 = 214) but never against those invited, because the eligible denominator is never stated. Both are repairable by disclosure and re-estimation rather than by new data collection, which is why this is `repairable` and not `fatal`: the reported arithmetic reconciles, ethics approval is reported, and I see no sign of undisclosed outcome redefinition.

### D2: domain_accuracy

score: not_assessed

### D3: argumentative_coherence

score: warn
trigger: "a plausible rival explanation left unaddressed"

The paper's inferential discipline is genuinely above average for this literature — reverse causation is named and attributed, causal language is refused throughout. But the rival explanation that bears most directly on the magnitude of *this* estimate, common-method variance from two self-reports collected in one instrument from one respondent at one moment, is never raised. The paper's citation of Vasquez (2020) addresses the accuracy of the use measure, not the shared-method inflation of the correlation between the two measures. There is also local hardening of the qualifier in the abstract. Neither defect collapses the argument, so this is warn and not block.

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: not_assessed

### D6: venue_fit_and_contribution

score: not_assessed

## Review Body

This is a carefully hedged paper reporting a single bivariate association, and its rhetorical restraint is real: it does not claim causation, it names the reverse pathway, and it declines to generalize in the discussion and conclusion. My concern is not that the paper overclaims in language. It is that the visible apparatus of precision — a two-decimal confidence interval, a robustness check, a power statement — is doing less inferential work than its presence implies, and that the two measures on which every number depends are documented at a level that does not permit an independent analyst to know what was correlated with what.

Start with what checks out, because it constrains what I can fairly criticize. I recomputed the interval: Fisher's z-transform of r = .42 with n = 214 gives z = .448, SE = 1/√211 = .0689, back-transformed bounds of .303 and .525. The reported CI [.30, .52] is exactly what the standard procedure yields, so there is no arithmetic discrepancy between the coefficient, the sample size, and the interval. The exclusion accounting also reconciles. The power figure is close to correct as well: at r = .19 with n = 214 the achieved power is approximately .798, so "greater than .80" is marginally generous at the stated boundary but accurate for any effect above it. I note these because a reviewer who alleges false precision should first establish that the numbers are at least internally consistent. They are. The problem lies elsewhere.

The problem is what the interval is an interval *of*. It propagates sampling error only, on the assumption of bivariate normality, when one of the two variables is a five-category ordinal item and the other is a mean of six items whose content is not disclosed. Two distinct sources of uncertainty are therefore excluded from the reported precision: the attenuation induced by a dependent variable whose reliability cannot be estimated at all, and the downward bias of Pearson's r applied to a coarsely categorized ordinal variable. Both biases point toward zero, which is why I am *not* arguing that the direction of the finding is unsafe — it is the most robust thing in the paper. What is unsafe is the reported magnitude and its stated precision. A polychoric estimate would very plausibly land above .42, and a disattenuated estimate higher still; the paper's characterization of the association as "moderate," and its comparison against prior effect sizes, are both anchored to a number that is systematically low by an amount the manuscript never attempts to bound. The correct response is not to abandon the estimate but to make the ordinal-appropriate coefficient primary, report an interval for it, and state plainly that no correction for measurement error in the dependent variable is possible because a single item admits none.

The instrument documentation is the defect I regard as decisive. The exposure measure is the whole paper, and it is described in three sentences: six items, adapted from Costa and Wren (2019), five-point agreement scale, α = .88. Nothing tells the reader what was adapted, why, or in which direction. "Previously validated" is a property of the original instrument, and validation does not survive undocumented modification. α = .88 across six items implies a mean inter-item correlation of about .55, which is consistent with a coherent unidimensional scale and equally consistent with a set of near-paraphrases; internal consistency alone cannot distinguish those cases and carries no information about whether the items measure perceived usefulness rather than satisfaction, ease of use, or general favorability toward the platform. Since the manuscript's stated contribution is comparability — "an incremental data point, comparable with prior work" — comparability is precisely what an undocumented adaptation with no factor-structure evidence in the present sample destroys.

The sampling reporting has the same shape: everything that could bound the finding is absent. "All enrolled undergraduates were eligible" without the number enrolled means there is no response rate, and without a response rate the voluntary-response bias the paper honestly names in §6 cannot be characterized even qualitatively. If the university enrolls 3,000 undergraduates, 233 responses is a 7.8% self-selected slice recruited through the very institutional channel whose usage is the outcome variable — that is not an incidental worry, it is a mechanism that plausibly restricts and shifts the distribution of the dependent variable. "Spanned all four year levels" is a presence claim, not a distribution, and cannot substitute for one.

Finally, §3.1 and §3.3 cannot both be read literally. Five duplicates were identified and removed, yet no identifying information was collected and responses could not be linked to individuals. Every mechanism that would support deduplication — session tokens, cookies, IP addresses, one-time links — is either a quasi-identifier at collection time or a linkage mechanism, and identification by response-pattern matching would be a substantive analytic decision requiring its own justification. One of these two statements requires correction. I did not treat this as fatal, because it is a contradiction between two methods statements rather than between methods and results, it does not touch the estimate materially, and it is repairable in one disclosed sentence. But it sits inside the ethics and consent statement, which is where accuracy matters most.

### S1: Confidence interval reconciles exactly with the reported coefficient and sample size

The interval is not decorative arithmetic: it is the correct Fisher z-transformed interval for the stated r and n, to both reported decimals. Whatever else is wrong here, the authors did not fabricate or mis-transcribe the primary inferential quantity, and the reporting convention (coefficient, interval, p, n together) is the right one.

**Evidence Anchor**: equation: Fisher z inversion of r = .42 at n = 214 checked against the §4 reported 95% CI [.30, .52]

### S2: Case-flow accounting is complete and internally consistent

The path from responses received to analyzed cases is stated with counts and reasons at each step and sums correctly. This is a low bar that a large fraction of survey manuscripts still fail, and it is the reason I could locate the deduplication problem at all.

**Evidence Anchor**: text: §3.1 "14 incomplete submissions and 5 duplicate entries were removed, leaving 214 valid responses"

### S3: Directionality is treated as genuinely open rather than nominally acknowledged

The reverse pathway is not relegated to a limitations list; it is stated in the discussion as equally consistent with the data and attributed to a cited source. This is the correct handling of an ambiguity that cross-sectional acceptance studies routinely acknowledge in one sentence and then ignore in their recommendations.

**Evidence Anchor**: text: §5 "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"

### S4: An ordinal-appropriate coefficient was computed and reported, not suppressed

Reporting ρ = .40 alongside r = .42 shows the authors recognized the measurement-level problem and checked it rather than hoping no reviewer would notice. My criticism below concerns which coefficient is primary and what accompanies it, not the absence of the check.

**Evidence Anchor**: text: §4 "The Spearman robustness check yielded a comparable coefficient"

### W1: Exposure instrument is unrecoverable — items not reproduced, adaptation undocumented, no validity evidence in-sample

The six items are nowhere printed, the modifications to Costa and Wren (2019) are nowhere described, and no factor analysis or other structural evidence is offered for the present sample. Cronbach's α is the sole psychometric warrant and cannot establish that the adapted scale measures the construct named. Because the paper's contribution is explicitly the comparability of its estimate with prior estimates, and comparability requires knowing what was measured, this single defect leaves the core claim uninterpretable as stated: a reader cannot determine whether "perceived usefulness" here denotes the same construct as in the studies against which the finding is benchmarked. Remedy: an appendix with verbatim item wording, an explicit change log against the source instrument, and either a confirmatory factor model or, at minimum, the item-level inter-correlation matrix.

**Severity**: Critical
**Evidence Anchor**: absence: §3.2 Measures and manuscript back matter — expected verbatim wording of the six items, an explicit statement of what was changed from Costa and Wren (2019), and factor-structure evidence in the present sample; checked §3.2, §3.4, §4, §7, References, and the absence of any appendix or supplementary-materials statement
**Confidence**: 5 — routine instrument-documentation audit against reporting standards for adapted scales in survey psychometrics

### W2: Single-item ordinal dependent variable makes reliability unestimable and attenuation unquantifiable

The §3.2 hedge describes the problem accurately but does nothing about it. A single item admits no internal-consistency estimate, no test-retest estimate is reported, and therefore the attenuation of r = .42 is of unknown magnitude and cannot be corrected or bounded. The reported CI reflects sampling variability alone and is silent about this second, potentially larger source of uncertainty, which makes the two-decimal precision misleading about how well the association is actually pinned down. The item's own documentation compounds this: only the endpoint labels are given (1 = rarely or never, 5 = several times daily), while the reported median category "a few times per week" corresponds to a label the reader never sees, so the response distribution cannot be reconstructed even qualitatively. Remedy: state explicitly that no reliability estimate exists for the outcome and that the interval therefore understates total uncertainty; report the full category labels and the frequency distribution; and frame the coefficient as a lower bound rather than a point estimate for comparison.

**Severity**: Major
**Evidence Anchor**: text: §3.2 "We treat this as an ordinal indicator of self-reported use and interpret it accordingly."
**Confidence**: 5 — direct application of classical attenuation theory to a single-indicator outcome

### W3: Pearson r is primary on a five-category ordinal variable, and its interval assumes a distribution the data cannot have

The estimate carrying the paper's conclusion is a product-moment coefficient computed on a variable with five discrete levels, with an interval derived under bivariate normality. Coarse categorization biases Pearson downward relative to the underlying association, and the Spearman check — which is the ordinal-appropriate gesture — is reported as a bare coefficient with no interval, so it cannot serve as an inferential alternative, only as reassurance that the sign is stable. A polychoric correlation, which estimates the association on the latent metric the Likert responses discretize, is the appropriate primary estimate and is not attempted. Reporting is also incomplete around the primary test: no t statistic and degrees of freedom accompany "p < .001" (t(212) ≈ 6.74 from the reported values), the shared-variance statement is made verbally rather than numerically (R² = .18), and the descriptives are given to one decimal while the coefficient is given to two. Remedy: make a polychoric or ordinal-appropriate estimate primary with a bootstrap interval, retain Pearson and Spearman as sensitivity analyses with intervals, and report the full test statistic.

**Severity**: Major
**Evidence Anchor**: text: §3.4 "Because the use item is ordinal, we also computed a Spearman correlation as a robustness check."
**Confidence**: 5 — standard ordinal-data estimation practice in educational measurement

### W4: No denominator, no response rate, no nonresponse evidence, no sample composition

Eligibility is stated as all enrolled undergraduates, but the size of that population is never given, so no response rate can be computed and the sample's relationship to any population is entirely unknown. Recruitment ran through the institution's course-announcement channel, meaning selection into the sample is plausibly correlated with the outcome variable itself; the §6 acknowledgment of voluntary-response bias therefore names a mechanism it cannot bound. "Spanned all four year levels" asserts presence without distribution, so even a minimal check for skew toward, say, first-year students is impossible. This does not invalidate the within-sample association, but it means the "bounded, single-sample descriptive finding" framing lacks the information needed to say what it is bounded to. Remedy: report the eligible enrollment, the number of invitations delivered, the computed response rate, the year-level and any available demographic distribution against institutional benchmarks, and, if available, an early-versus-late responder comparison as a nonresponse proxy.

**Severity**: Major
**Evidence Anchor**: absence: §3.1 Design and participants — expected the enrolled undergraduate population size, a computed response rate, and the year-level distribution of the 214 analyzed cases against institutional benchmarks; checked §3.1, §3.3, §4, §6, and the Abstract
**Confidence**: 5 — standard survey-reporting requirements for any sample-to-population inference

### W5: Anonymity statement and duplicate removal are mutually inconsistent as written

The manuscript states that no identifying information was collected and that responses could not be linked to individuals, and separately that five duplicate entries were identified and removed. Under the stated collection conditions, duplicate identification requires some persistent marker (session token, cookie, IP address, single-use link) or a response-pattern matching rule — the first class contradicts the anonymity statement as literally written, and the second is a substantive analytic decision with a nonzero false-positive rate that would require its own justification and disclosure. One of the two statements must be corrected. The estimate is not materially affected by five cases, but the affected sentence sits in the ethics and consent section, where imprecision is least acceptable, and readers cannot currently evaluate whether five legitimate responses were discarded. Remedy: disclose the deduplication mechanism and its retention status, and revise §3.3 to describe the anonymity condition accurately.

**Severity**: Major
**Evidence Anchor**: text: §3.3 "No identifying information was collected, and responses could not be linked back to individual students."
**Confidence**: 4 — survey-operations auditing; a token-based mechanism could resolve the contradiction, but it is not disclosed

### W6: Power statement is a sensitivity computation on the achieved sample, presented as design sensitivity

The statement is conditioned on n = 214 and concludes "so the design was sensitive to small-to-moderate associations," which reads as a design-stage justification. Nothing in the manuscript indicates that a target sample size was determined before data collection, and the survey ran for a fixed three-week window rather than to a recruitment target. This is a post-hoc sensitivity analysis and should be labelled as one. To be fair to the authors, it is the defensible form of post-hoc computation — it is conditioned on a specified effect size rather than on the observed effect, so it is not the observed-power fallacy, and the arithmetic is essentially right (power at r = .19 is approximately .798, so "greater than .80" holds for any effect above the stated threshold and is marginally generous at it). The defect is labelling and the absence of any planned-N rationale, not invalid computation. Remedy: relabel as a sensitivity analysis, state whether any a priori target existed, and correct the boundary wording to "approximately .80."

**Severity**: Minor
**Evidence Anchor**: text: §3.4 "With n = 214, the study had greater than .80 power to detect a correlation of r >= .19"
**Confidence**: 5 — direct recomputation of the stated power quantity

### W7: No reproducibility affordances beyond the narrative description

No statistical software or version is named, no data availability statement appears, no analysis script or fully specified computational procedure is provided, and no item-level or category-level descriptives are reported that would allow the primary coefficient to be recomputed or an alternative estimator applied. For an analysis this simple, full reproducibility is achievable at near-zero cost: the bivariate contingency table of the six-item mean against the five-category use item, or the deposited response-level data, would let any reader verify the coefficient and compute the ordinal alternative themselves. Remedy: name the software, add a data availability statement, and deposit either the data or the cross-tabulation.

**Severity**: Minor
**Evidence Anchor**: absence: §3.4 Analysis and manuscript back matter — expected named statistical software with version, a data availability statement, and analysis code or a cross-tabulation sufficient to recompute the reported coefficient; checked §3.4, §4, §7, References, and the absence of any declarations section
**Confidence**: 5 — standard reproducibility checklist for quantitative survey submissions

### W8: Common-method variance is never raised as a competing explanation for the association's magnitude

Both variables were collected in the same instrument, from the same respondent, at the same sitting, using adjacent self-report formats. Shared method variance is a well-established inflationary mechanism for exactly this configuration, and it works in the opposite direction from the attenuation discussed above, so the two do not conveniently cancel to a known net. The literature review's treatment of self-report addresses whether the use measure tracks behavior, which is a different question from whether the *correlation between* two self-reports is inflated by their shared source; the manuscript's careful engagement with the first caution may obscure that the second was never raised. Because the paper's substantive interpretation rests entirely on the magnitude of r, an unaddressed mechanism that plausibly moves that magnitude is material. Remedy: name common-method variance explicitly in the discussion, and if any procedural remedies were used (item separation, differing response formats, counterbalancing), report them.

**Severity**: Major
**Evidence Anchor**: text: §2 "studies relying on self-report capture perceived rather than actual engagement"
**Confidence**: 5 — standard survey-methods concern for single-source cross-sectional correlations

### W9: Qualifiers loosen between the body and the abstract

The literature review commits to treating the outcome as perceived rather than behavioral engagement, and §6 restricts generalization to a single mid-sized university. The abstract's closing sentence then reports evidence about "LMS engagement" — a behavioral term the paper elsewhere disowns — "among undergraduates," without the institutional restriction that appears two sentences earlier in the same abstract. The drift is local and self-corrected in the conclusion, which is properly scoped, so this is a wording repair rather than a structural overreach. Remedy: replace "LMS engagement" with "self-reported LMS use" and add the single-institution qualifier to the closing sentence.

**Severity**: Minor
**Evidence Anchor**: text: Abstract "The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates."
**Confidence**: 4 — reading of qualifier propagation across sections; reasonable reviewers may treat this as stylistic
