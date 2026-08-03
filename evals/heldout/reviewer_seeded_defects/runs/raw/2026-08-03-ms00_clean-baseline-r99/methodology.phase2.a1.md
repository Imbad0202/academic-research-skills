contract_role: methodology

## Dimension Scores

### D1: methodology_rigor

score: block
trigger: "A core reported inference cannot be reconstructed or evaluated because a load-bearing methodological element is absent or internally inconsistent"
block_class: repairable

The paper's entire contribution is one coefficient, so the coefficient's measurement foundation is load-bearing in the strictest sense. That foundation is not documented. The sole predictor is a six-item scale described only as "adapted" from a prior instrument, with no items reproduced, no statement of what the adaptation changed, and no dimensionality evidence in this sample — α = .88 licenses none of that. The data-handling account is internally inconsistent: five duplicate submissions were identified in a survey that reports collecting no identifying information and no linkage to individuals. The population denominator is absent even though "all enrolled undergraduates were eligible," so no response rate exists and the conceded volunteer skew cannot be bounded. Descriptive reporting is limited to two numbers, so the symmetry and linearity claims that license a Pearson estimate on a five-category ordinal outcome cannot be checked, and r² is characterised verbally rather than stated. Every one of these is repairable from material the authors plainly hold, which is why this is a repairable block rather than a fatal one; but as submitted, a reader cannot reconstruct what was measured or on whom.

### D2: domain_accuracy

score: not_assessed

### D3: argumentative_coherence

score: warn
trigger: "coherence is locally strained — for example over-strong verbs in the abstract relative to a hedged results section"

The central inference is proportionate: the paper claims a positive moderate association with self-reported use in one sample, declines causal language throughout, and concedes the reverse pathway explicitly. That core survives. The strain is local and appears at three seams. The abstract's closing sentence widens the outcome from "self-reported frequency of use" to "LMS engagement" and the referent from a volunteer subset at one institution to "undergraduates." The practical onboarding implication is licensed only under the perception-to-use direction that Section 5 declares unidentifiable; hedging it as "suggested by, not proven by" names the gap without closing it. And the intro's description of "one clearly bounded sample" is not honoured by Section 6's limitation that volunteers are overrepresented in an unquantified way. These are rewriting problems, not a broken thesis, so warn rather than block.

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: not_assessed

### D6: venue_fit_and_contribution

score: not_assessed

## Review Body

This is a disciplined, deliberately modest correlational report, and I want to be clear at the outset that its restraint about causality is genuine and well executed. My concerns lie almost entirely upstream of causality, in a place the manuscript never visits: whether the reported coefficient is defensible as an *estimate* at all. The paper concedes the direction problem four separate times and treats that concession as discharging its measurement obligations. It does not. Direction and magnitude are independent problems, and the manuscript addresses only the first.

The magnitude problem has two components pushing in opposite directions, neither bounded in the text. Downward: the outcome is a single five-point item whose categories are vague quantifiers of unequal width ("rarely or never" through "several times daily"), so the observed correlation is attenuated relative to the latent association by an unknown amount, and no reliability evidence for that item exists or can exist from these data. Upward: both variables come from the same instrument, the same respondent, and the same sitting, so shared method and consistency motif inflate the observed covariance by an unknown amount. The paper reports r = .42 with a 95% CI and treats sampling error as the only source of uncertainty. It is not; it is arguably the smallest of the three. That is why the interval as printed conveys more precision than the design can deliver.

On estimator ordering, I would reverse the paper's own hierarchy. Section 3.2 explicitly declares the outcome ordinal and says it will be interpreted accordingly. Section 3.4 then makes Pearson primary and demotes Spearman to a "robustness check." That is internally backwards: the measurement model stated in the Measures section implies the rank-based estimate is the primary one, or better, that a polychoric estimate be reported if the authors wish to speak about the latent association at all. The practical difference here is small (ρ = .40 versus r = .42), which is reassuring, but the reasoning should follow the declared measurement model rather than the larger coefficient.

On sampling, the paper is transparent about arithmetic and opaque about population. Removing 14 incomplete and 5 duplicate submissions from 233 is clean accounting, but complete-case exclusion is never characterised — we learn nothing about whether the 14 partial responders differed on the perceived-usefulness items they did complete — and the deduplication procedure is both undisclosed and in tension with the anonymity statement. A public university knows its undergraduate enrolment; reporting it costs one sentence and converts "voluntary response may skew this" from an acknowledgment into a quantity a reader can reason about.

Finally, the sensitivity statement. It is computed on the realised post-exclusion n and then described as a property of "the design," which reads as a priori planning. If the .19 detectable-effect figure was reconstructed after data collection, it is a post hoc observation about the analysis, not evidence that the study was designed to be sensitive, and it should be worded as such. The arithmetic is approximately right; the framing is not.

What follows below is what I would need to see to change my score on D1: item wording and a specific account of the adaptation, a dimensionality check in this sample, the enrolment denominator and response rate, a full frequency distribution for the use item, r² stated numerically, the deduplication method, and an explicit treatment of same-source measurement as a threat to the magnitude rather than only to the direction.

### S1: Ethics and consent reporting is complete and specific rather than boilerplate

Approval body, voluntariness, absence of incentive, anonymity, and the placement of the consent step are all stated. This is more than most survey manuscripts of this length provide, and it makes the one inconsistency I raise below (deduplication) conspicuous precisely because the rest of the account is careful.

**Evidence Anchor**: text: §3.3 — "The study protocol was reviewed and approved by the university's research ethics committee"

### S2: The primary estimate is reported with interval, exact n, and a non-parametric corroboration rather than a significance verdict

The manuscript avoids the common failure of reporting p alone. The interval, the exact n at the point of estimate, and the Spearman coefficient together give a reader materially more to work with than a starred coefficient would.

**Evidence Anchor**: text: §4 — "r = .42, 95% CI [.30, .52], p < .001, n = 214"

### S3: Directional restraint is consistent across abstract, results, discussion, and conclusion

The reverse pathway is stated affirmatively rather than buried, and attributed to a source that argues it. Sections 4, 5, 6, and 7 do not drift into causal verbs. This is the paper's strongest methodological virtue.

**Evidence Anchor**: text: §5 — "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"

### S4: The limitations section names the threats that actually bear on this design

Single site, single-item self-report, cross-sectional structure, and volunteer response are the four correct threats to name. The section is not padded with generic caveats, and each item corresponds to a real feature of the study.

**Evidence Anchor**: text: §6 — "Fourth, response was voluntary, so students who engage more with institutional channels may be overrepresented"

### S5: The literature review engages methodological cautions, not only supportive findings

Citing between-institution variability in association strength, and self-report versus log divergence, shows the authors understand the measurement literature they are operating inside. That makes the omissions below more surprising rather than less, but the awareness is real and worth crediting.

**Evidence Anchor**: text: §2 — "Song (2018), reporting across multiple campuses, likewise found that association strengths varied by institution"

### W1: The sole predictor's measurement content is undocumented and the adaptation is unspecified

The perceived-usefulness scale is described only as six items "adapted" from a prior instrument. No item is reproduced, the nature and extent of the adaptation are never stated, and no factor structure is examined in this sample. Two consequences follow. First, the source instrument's validation evidence does not transfer to an undescribed modification — an adapted scale is a new scale until shown otherwise. Second, α = .88 is evidence of inter-item homogeneity only; it is compatible with a unidimensional measure of perceived usefulness, with a narrower facet of it, and with a bloated-specific set of near-duplicate items, and it cannot distinguish among them. Because this manuscript's declared contribution is a single "transparently reported" coefficient, the content of the measure on one side of that coefficient is not a detail; it is the contribution's foundation. As submitted, neither replication nor construct interpretation is possible.

**Severity**: Critical
**Evidence Anchor**: text: §3.2 — "six-item scale adapted from Costa and Wren (2019)" and "the scale showed good internal consistency (Cronbach's α = .88)"
**Confidence**: 5 — instrument documentation and the α-versus-dimensionality distinction are the core of my review specialty.

### W2: The outcome is a coarse single ordinal item with no reliability evidence, yet the parametric estimate is made primary

A single five-point frequency item cannot yield any internal-consistency or test-retest evidence, so the outcome's measurement error is entirely unquantified, and coarse categorisation attenuates the observed coefficient by an unknown amount. Compounding this, the response options are vague quantifiers whose spacing is not interval and whose interpretation varies across respondents: the distance from "a few times per week" to "several times daily" is not psychologically equivalent to the distance between adjacent low categories. The manuscript declares the item ordinal in Section 3.2 and then contradicts that declaration in Section 3.4 by treating Pearson as primary and the rank-based estimate as a check. The ordering should be reversed, or a polychoric estimate reported if a latent-association claim is intended. The close agreement of the two coefficients limits the practical damage, but the magnitude claim — "moderately" — remains uninterpretable without a stated attenuation argument.

**Severity**: Major
**Evidence Anchor**: text: §3.2 and §3.4 — "captured with a single five-point frequency item asking how often the respondent accessed the LMS" and "Because the use item is ordinal, we also computed a Spearman correlation as a robustness check"
**Confidence**: 5 — single-item versus multi-item measurement and ordinal estimator choice are my primary research programme.

### W3: Common-method variance is never assessed; the paper's restraint addresses direction only

Both variables were elicited from the same respondent, on the same instrument, in the same sitting, using the same Likert-type response format. This threatens the coefficient's magnitude independently of the direction problem, through consistency motif and shared response style. The manuscript's careful hedging is directed exclusively at causal ordering and at self-report-versus-log validity of the outcome; neither addresses shared-method inflation of the covariance between the two measures. No procedural remedy (temporal or format separation of measures, marker variable) and no statistical diagnostic is reported. This also undercuts the comparability claim: describing r = .42 as "consistent with prior technology-acceptance research" needs qualification when some of that prior work used behavioural traces on one side of the association and this study did not.

**Severity**: Major
**Evidence Anchor**: absence: Methods §3.2 and Discussion §5 — expected any assessment of common-method variance arising from same-instrument, same-respondent, same-sitting measurement of both variables; checked §3.2 Measures, §3.3 Procedure and ethics, §3.4 Analysis, §5 Discussion, §6 Limitations
**Confidence**: 5 — common-method variance in self-report designs is a named component of my research programme.

### W4: No population denominator, therefore no response rate and no bounded nonresponse bias

Eligibility is defined as the full undergraduate population, which means the denominator was available to the authors, yet enrolment is never reported and no response rate is computed. The consequence is that the conceded volunteer skew cannot be quantified at all: 214 respondents could represent 3% or 30% of the eligible population, and the plausible magnitude of selection bias differs enormously across that range. Sample composition is described only as spanning all four year levels, which establishes non-emptiness of each stratum and nothing else — no year-level distribution, no discipline mix, no age or enrolment-status breakdown, nothing that would let a reader judge similarity to the institutional profile or to any other site. This also undermines the intro's characterisation of the sample as "clearly bounded": the boundary is defined by who chose to answer an announcement, and that set is never described.

**Severity**: Major
**Evidence Anchor**: text: §3.1 — "All enrolled undergraduates were eligible" and "The analyzed sample of 214 students spanned all four year levels"
**Confidence**: 5 — reporting completeness and sampling transparency in correlational education research is my standing review focus.

### W5: Duplicate detection is inconsistent with the stated anonymity protections, and incomplete-case exclusion is uncharacterised

Five submissions were identified as duplicates, which requires some cross-response identifier — IP address, session token, device fingerprint, or a matching pattern rule. The manuscript states that no identifying information was collected and that responses could not be linked to individuals. These two statements cannot both be complete as written; either an identifier was collected and the ethics statement understates the data held, or the deduplication rule was heuristic and its false-positive behaviour matters for the analysed n. Separately, 14 incomplete submissions were dropped with no comparison of their available responses to retained cases, so complete-case analysis is adopted without any evidence that missingness is benign. Neither issue is likely to move the coefficient much, but both are disclosure defects in exactly the region where readers must take the authors on trust.

**Severity**: Major
**Evidence Anchor**: text: §3.1 and §3.3 — "5 duplicate entries were removed" and "No identifying information was collected"
**Confidence**: 4 — routine survey-operations reasoning; I cannot rule out an innocuous explanation the authors simply omitted.

### W6: Distributional reporting is too thin to verify the assumption checks that license the primary estimator

Section 3.4 asserts approximate linearity, monotonicity, absence of extreme bivariate outliers, and approximate symmetry of both distributions. For a five-category ordinal outcome, "approximately symmetric" is a claim about a frequency table that is never shown; only a median category appears. No descriptives table, no full item-level statistics, no correlation matrix, and no scatterplot or cross-tabulation are provided. A reader therefore cannot check whether the use item clusters at the upper categories, whether any category is nearly empty, or whether the bivariate pattern is monotone across all five levels rather than driven by contrast between the extremes. These are precisely the checks that decide whether a product-moment coefficient is the right summary, so the assertion carries the argumentative weight while the evidence for it is withheld.

**Severity**: Major
**Evidence Anchor**: text: §3.4 — "Scatterplot inspection showed an approximately linear, monotonic association with no extreme bivariate outliers" and "and both distributions were approximately symmetric"
**Confidence**: 5 — assumption verification for correlational reporting is a routine part of my statistical-review work.

### W7: Shared variance is characterised verbally instead of stated

The Results section describes the proportion of shared variance as "accordingly modest" without ever reporting it. The quantity is approximately .18, it takes four characters to print, and the verbal substitute invites the reader to accept an interpretation of magnitude rather than to evaluate one. This is a one-sentence fix and does not change any claim, but withholding a derived quantity while arguing from it is the wrong instinct in a paper whose stated virtue is transparent reporting.

**Severity**: Minor
**Evidence Anchor**: text: §4 — "The proportion of variance shared by the two measures was accordingly modest"
**Confidence**: 5 — direct arithmetic from the reported coefficient.

### W8: The sensitivity statement is computed on the realised sample yet framed as a property of the design

The power figure is derived from n = 214, which is the post-exclusion analysed sample, and is then used to conclude that "the design was sensitive" to small-to-moderate associations. A calculation performed on the sample that survived exclusions is a post hoc sensitivity statement, not evidence of design-stage planning. No target sample size, no a priori power analysis, and no pre-specified analysis plan is reported, and it is likewise unstated whether the Pearson-primary/Spearman-check ordering was fixed in advance or chosen after both coefficients were seen. The arithmetic is approximately correct, and the confidence interval already conveys the achieved precision honestly, so the substantive cost is small — but the planning status should be stated plainly rather than implied.

**Severity**: Minor
**Evidence Anchor**: text: §3.4 — "the study had greater than .80 power to detect a correlation of r >= .19" and "so the design was sensitive to small-to-moderate associations"
**Confidence**: 4 — power-statement provenance is inferable from the text but the authors' actual sequence is not observable to me.

### W9: No availability statement for instrument, data, or analysis code

Nothing in the manuscript tells a reader where to obtain the six item stems, the response distributions, the de-identified dataset, or the analysis specification. For an anonymous survey with two variables and n = 214, the barrier to sharing is close to zero, and sharing would resolve part of W1 and all of W6 at a stroke. The absence is a reproducibility gap rather than an error, but it sits awkwardly beside the paper's self-description as a transparently reported contribution.

**Severity**: Minor
**Evidence Anchor**: absence: end matter and Methods §3.4 — expected an availability statement for the survey instrument, item wording, data, or analysis code; checked §3.2 Measures, §3.3 Procedure and ethics, §3.4 Analysis, §7 Conclusion, References
**Confidence**: 5 — a full read of the manuscript's method and end matter.

### W10: The abstract widens both the construct and the population beyond what was measured

The abstract's closing sentence reports that perceived usefulness "tracks with LMS engagement among undergraduates." What was measured is a single self-reported frequency item, which the literature review itself distinguishes from behavioural engagement, among a self-selected subset of one institution's students. Both nouns are broader than the evidence: "engagement" upgrades the outcome the paper elsewhere carefully restricts to perceived use, and the unqualified "undergraduates" drops the single-site and volunteer boundaries that Sections 6 and 7 honour. The rest of the manuscript is disciplined about this, which makes the abstract the least accurate surface in the paper — and the one most readers will see alone.

**Severity**: Minor
**Evidence Anchor**: text: Abstract — "perceived usefulness tracks with LMS engagement among undergraduates"
**Confidence**: 5 — direct comparison of abstract wording to the Measures and Limitations sections.

### W11: The practical implication is licensed only by the direction the paper declares unidentifiable

The onboarding recommendation presupposes that raising perceived usefulness would raise use. Section 5 states two paragraphs earlier that the reverse pathway is equally consistent with the data. Under the reverse pathway the recommendation receives no support whatsoever, so the implication is not weakly supported by this correlation — it is conditional on an unresolved identification question. The added hedge that the implication is "suggested by, not proven by" the correlation names the gap without repairing it, since the issue is not strength of support but whether any support exists under one of two equally admissible readings. Reframing the passage as a hypothesis for a design that could distinguish the directions would resolve this without losing anything the authors need.

**Severity**: Minor
**Evidence Anchor**: text: §5 — "offers modest support for the intuition that LMS onboarding which helps students see concrete usefulness"
**Confidence**: 4 — an inferential-warrant judgement within my remit, though the boundary between hedged implication and unlicensed claim admits some reasonable disagreement.
