contract_role: methodology

## Dimension Scores

### D1: methodology_rigor
score: warn
trigger: "rigor is degraded by recoverable omissions that a revision could supply: incomplete reliability evidence, thin justification for a modelling or scoring choice, missing data-availability or ethics statement, absent response-rate reporting, single-source or common-method measurement acknowledged only in passing"

The design, sample, measures, and analysis are reconstructible and the reported inferential statistics are internally verifiable, which keeps this dimension short of `block`. What degrades it is a cluster of recoverable omissions concentrated on measurement quality and data provenance: no treatment of same-instrument method variance, no latent-scale estimate for a coarse single-item outcome, no participation rate against the stated eligible population, an undisclosed duplicate-detection mechanism that sits in tension with the anonymity claim, and no factor evidence or item wording for an instrument described as adapted rather than used intact.

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: warn
trigger: "a plausible confound or alternative explanation left unaddressed"

The inferential chain from research question to conclusion is unusually disciplined: the outcome is consistently framed as perceived use, causality is refused in four places, and the abstract, results, discussion, and conclusion all report the same estimate under the same restriction. The argument is nonetheless under-defended at one load-bearing point — the single most obvious rival account of part of the observed magnitude (shared instrument, respondent, and occasion producing correlated response-style variance) never enters the set of alternatives the paper considers, even though reverse causation and third factors do. A second, smaller overreach claims robustness that the reported check does not deliver.

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

This is a deliberately narrow correlational report, and it should be reviewed against the claim it actually makes rather than a claim it declines to make. The authors do not assert behavioural measurement; they state in the literature review, the measures section, the results, and the limitations that the outcome is *perceived* use, and they cite the self-report/log divergence literature pre-emptively rather than defensively. That narrowing is legitimate and it changes what a methodologist may demand: I have not scored the absence of log data as a defect, because the paper never trades on behaviour. Reporting hygiene is also above the norm for this genre — the correlation arrives with a 95% confidence interval, an exact n, a rank-based check, a stated detectable-effect calculation, and a complete ethics and consent paragraph. I reproduced both numeric claims: the interval [.30, .52] is what a Fisher-z transform of r = .42 at n = 214 returns, and r ≈ .19 is indeed the effect detectable at .80 power, α = .05 two-tailed, at that sample size. Nothing in the reported arithmetic is wrong.

The rigor problem is not in what is computed but in what is left undiscussed about the two variables being correlated. Both the predictor and the outcome were elicited from the same respondent, in the same instrument, at the same sitting, on the same five-point response format. Some portion of r = .42 is therefore attributable to shared method rather than to shared construct, and the manuscript nowhere says so: there is no marker variable, no Harman-type single-factor diagnostic, no temporal or procedural separation between the blocks, and — most tellingly — no mention of the issue among the four limitations, which cover generalisability, self-report accuracy relative to logs, causality, and voluntary response. Limitation two is close but not the same point: it concerns whether the self-report tracks behaviour, not whether the two self-reports contaminate each other. This matters because the paper's contribution is explicitly a *magnitude* offered as comparable with prior estimates, and a method-inflated magnitude is not comparable to a multi-method one.

The same coefficient is simultaneously under a downward pressure the paper also does not discuss. A one-item outcome has no estimable reliability, so attenuation cannot be quantified; five coarse ordinal categories truncate the observable association further, independently of unreliability. The Spearman check does not address this. Rank-order agreement speaks to monotonicity, not to categorisation coarseness, and a rank coefficient computed on the same five categories inherits the same coarseness. A polyserial or polychoric estimate would have spoken directly to the latent association and would very likely have exceeded .42. The honest description is a two-sided distortion — .42 as a lower bound on the latent relationship and a plausible upper bound on the method-free substantive one — and that framing is what the discussion needs, not one additional coefficient. The remedy costs the authors almost nothing: the polyserial estimate is computable from existing data, and the design acknowledgement is a paragraph.

On provenance, three items need closing. First, "all enrolled undergraduates were eligible" establishes a frame but supplies no denominator, so 233 received responses cannot be converted into a participation rate; combined with distribution through a course-announcement channel of unknown reach, the relation of the analysed 214 to the eligible population is unbounded. Second, §3.1 removes five duplicates while §3.3 states that no identifying information was collected and that responses could not be linked to individuals; these cannot both be true without a stated mechanism, and the two plausible mechanisms (quasi-identifiers such as IP or session token, versus pattern-based inference) have different implications — one qualifies the anonymity claim, the other risks deleting genuinely distinct respondents. Third, α = .88 licenses a statement about internal consistency, not about unidimensionality, and the composite is a simple item mean; since the instrument was adapted rather than used intact, this sample's factor structure and the adapted item wording both belong in the paper, and the abstract's "previously validated" should be attributed to the parent instrument rather than to the version administered here.

I stopped short of `block` on D1 deliberately. Every defect above is either a reporting addition the authors can supply from data in hand or an interpretive qualification they can write, and none of them makes the reported result non-verifiable or the sign of the association doubtful. On D3, the warn rests on the unaddressed method-variance rival plus the robustness over-claim; the central thesis survives both.

### S1: Uncertainty reporting is complete and independently verifiable
The headline estimate is reported with an interval, an exact p threshold, and n in the same sentence, and the interval is exactly what the standard normalising transform returns for that r and n. This is the reporting standard the genre usually misses.
**Evidence Anchor**: `text: §4 "r = .42, 95% CI [.30, .52], p < .001, n = 214"`
**Confidence**: 5 — recomputed the interval directly.

### S2: Sensitivity stated as a detectable effect size, not as a bare power assertion
The paper names the smallest correlation detectable at conventional power and alpha rather than claiming "adequate power," and the figure is arithmetically correct for n = 214.
**Evidence Anchor**: `text: §3.4 "the study had greater than .80 power to detect a correlation of r >= .19 at alpha = .05"`
**Confidence**: 5 — verified against the Fisher-z power expression.

### S3: Human-participants reporting is complete
Committee review, voluntariness, absence of incentive, and consent placement are each stated explicitly rather than gestured at.
**Evidence Anchor**: `text: §3.3 "The study protocol was reviewed and approved by the university's research ethics committee."`
**Confidence**: 4 — standard checklist reading of the ethics paragraph.

### S4: Construct narrowing is declared in advance and held consistently
The outcome is defined as an indicator of perceived use before results appear, the divergence literature is cited in support of that narrowing, and no later section quietly upgrades it to behaviour.
**Evidence Anchor**: `text: §2 "treat our self-report measure as an indicator of perceived use rather than a behavioral count"`
**Confidence**: 5 — traced the construct label across abstract, methods, results, discussion, limitations.

### S5: The reverse pathway is named, not merely hedged against
Rather than asserting non-causality generically, the discussion states the specific competing direction and attributes it to a cited source, which is the correct standard for a cross-sectional association.
**Evidence Anchor**: `text: §5 "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"`
**Confidence**: 5 — direct reading.

### W1: Common-method variance is the dominant threat to the reported magnitude and is nowhere disclosed
Predictor and outcome share instrument, respondent, occasion, and response format, so an unknown share of r = .42 is method rather than construct covariance. No marker variable, no single-factor diagnostic, and no procedural separation were used, and the threat is absent from all four limitations — limitation two addresses self-report-versus-log accuracy, which is a different problem. Because the paper's stated contribution is a magnitude positioned as comparable with prior estimates, an undisclosed method-variance component bears directly on the claim. The repair is partly costless: the design acknowledgement and an explicit statement that .42 is an upper-bound-inclusive estimate require no new data, and a single-factor diagnostic on the seven items is computable now.
**Severity**: Major
**Evidence Anchor**: `absence: §6 Limitations — expected an acknowledgement of common-method variance from same-instrument, same-respondent, same-occasion measurement, plus a marker variable or Harman-type check; checked §3.2, §3.3, §3.4, §4, §5, §6`
**Confidence**: 5 — common-method variance in single-instrument technology-use surveys is my primary research area.

### W2: One coarse ordinal outcome, with no latent-scale estimate and no attenuation discussion
Reliability is unknown and unknowable for a single item, so attenuation cannot be quantified; five categories truncate the observable association further, independently of unreliability. The Spearman check addresses monotonicity, not coarseness, and inherits the same five categories. A polyserial or polychoric estimate would speak to the latent association and would plausibly exceed .42. The paper needs to state the two-sided distortion — attenuation pushing the estimate down, shared method pushing it up — rather than treating one rank coefficient as settling the measurement question.
**Severity**: Major
**Evidence Anchor**: `absence: §3.4 Analysis — expected a polyserial or polychoric estimate of the latent association, or an explicit attenuation bound for the one-item five-category outcome; checked §3.2, §3.4, §4, §6`
**Confidence**: 5 — psychometric attenuation and coarse-categorisation effects are core to my teaching.

### W3: No eligible-population denominator and therefore no participation rate
The frame is stated ("all enrolled undergraduates were eligible") but its size is not, and the announcement channel's reach is unknown, so 233 received responses cannot be expressed as a participation rate. The authors acknowledge voluntary-response bias qualitatively but leave its magnitude unbounded. This is decision-relevant beyond checklist compliance: the manuscript positions its estimate as one comparable point against multi-campus work, and a very low effective participation rate would require that positioning to be rewritten. Enrolment figures are almost certainly retrievable.
**Severity**: Major
**Evidence Anchor**: `absence: §3.1 Design and participants — expected an eligible-population denominator and a participation or response rate; checked §3.1, §3.4, §4, §6, §7`
**Confidence**: 5 — standard survey-reporting requirement.

### W4: Duplicate removal is logically incompatible with the stated anonymity procedure as written
Five duplicates were identified and removed, yet the procedure states that no identifying information was collected and that responses could not be linked to individual students. One of these descriptions is incomplete. If quasi-identifiers such as IP address, session token, or device fingerprint were captured, the anonymity statement and the consent disclosure both need amending; if duplication was inferred from identical response patterns, the criterion needs stating and carries a real risk of deleting distinct respondents who answered identically on a six-item Likert block and one frequency item. Either way the exclusion rule is currently unauditable. The affected fraction is small, so I do not treat this as invalidating the estimate.
**Severity**: Major
**Evidence Anchor**: `text: §3.1 and §3.3 "5 duplicate entries were removed" and "responses could not be linked back to individual students"`
**Confidence**: 4 — inference from the stated procedure; a mechanism the authors can supply may reconcile it.

### W5: The adapted instrument's structure and item content are not established for this sample
α = .88 evidences internal consistency, not the unidimensionality that a simple item mean presupposes, and no factor structure is reported for this sample even though the scale was adapted rather than administered intact. Neither the adapted item wording nor a description of what was changed appears anywhere, so the main predictor cannot be reproduced by another team. Relatedly, the abstract's "previously validated instrument" attaches validation evidence to the parent instrument, not to the version actually fielded; that attribution should be split.
**Severity**: Major
**Evidence Anchor**: `text: Abstract "Perceived usefulness was measured with an adapted, previously validated instrument"`
**Confidence**: 5 — routine instrument-adaptation reporting standard.

### W6: The assumption checks are asserted but not shown, and the outcome's marginal distribution is missing
Linearity, monotonicity, absence of bivariate outliers, and approximate symmetry are all reported as conclusions of a scatterplot inspection that is not displayed, and the outcome is summarised by a median category with no frequency distribution or dispersion. A reader therefore cannot assess floor or ceiling piling on the five-category item or verify the symmetry claim. A category-frequency table would close this. I keep this Minor because no plausible marginal distribution would reverse the sign or the qualitative reading of the association, and the rank check corroborates it.
**Severity**: Minor
**Evidence Anchor**: `text: §3.4 "Scatterplot inspection showed an approximately linear, monotonic association with no extreme bivariate outliers"`
**Confidence**: 5 — direct reading against the results section.

### W7: The power statement's status (a priori versus post hoc sensitivity) is unspecified
Because the calculation is conditioned on the realised n = 214, it is a sensitivity statement unless it was performed before data collection, and the phrasing attributes sensitivity to "the design" rather than to the achieved sample. State which it is; if a target n was set in advance, say so and give the assumed effect size.
**Severity**: Minor
**Evidence Anchor**: `text: §3.4 "so the design was sensitive to small-to-moderate associations"`
**Confidence**: 4 — reporting-convention judgement.

### W8: No data-, code-, or materials-availability statement
Neither the dataset, the analysis script, nor the fielded item set is made available or addressed by an availability statement anywhere in the manuscript. Given that the analysis is a two-variable correlation, providing the anonymised pair of columns and the item list would make the entire result independently reproducible at negligible cost.
**Severity**: Minor
**Evidence Anchor**: `absence: §3.3 and §7 — expected a data-availability, code-availability, or materials-availability statement; checked §3.2, §3.3, §3.4, §5, §6, §7, References`
**Confidence**: 5 — presence or absence is directly checkable.

### W9: The robustness claim over-reads what the rank check establishes
A comparable Spearman coefficient shows that the association survives rank transformation; it does not show independence from "the parametric assumption" in general, since the contested assumption here is interval scoring of five coarse categories, which the rank coefficient shares. Rewrite the sentence to claim monotonic robustness specifically, and let the polyserial estimate requested in W2 carry the scale-level argument.
**Severity**: Minor
**Evidence Anchor**: `text: §4 "indicating that the association did not depend on the parametric assumption"`
**Confidence**: 5 — the distinction between rank-order and scale-level robustness is unambiguous.
