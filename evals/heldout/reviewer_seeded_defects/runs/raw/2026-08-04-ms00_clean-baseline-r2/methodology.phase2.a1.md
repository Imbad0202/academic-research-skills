contract_role: methodology

## Dimension Scores

### D1: methodology_rigor

score: warn
trigger: "The core design and analysis are recoverable but rigour is incomplete in ways that weaken confidence without voiding it"

The design, cleaning chain, and inferential reporting are all recoverable, and the headline estimate is reported with an interval, a robustness check, and a sample size — so my Phase 1 block criterion ("cannot be reconstructed or evaluated **at all**") is not met. But the warn is dense rather than nominal: it is carried by five Major findings, and the paper is missing almost the full exemplar list I committed to in Phase 1 (outcome reliability, characterized missing-data treatment, instrument availability, data availability), plus two items I did not anticipate (no sampling-frame denominator, no common-method-variance treatment). This sits at the top of the warn band, not the bottom.

### D2: domain_accuracy

score: not_assessed

### D3: argumentative_coherence

score: warn
trigger: "The main argument holds but contains local slippage"

The evidential chain from measurement to conclusion holds, numbers are internally consistent across all four sections, and causal language is refused explicitly. Two local slippages prevent a pass: the abstract's take-home sentence upgrades "self-reported frequency of access" to "LMS engagement," which contradicts the standard the authors themselves import from Vasquez (2020) two pages earlier; and the onboarding implication is directional in a paper that has just conceded the reverse pathway is equally consistent. Neither defeats the thesis; both are exactly the local slippage my warn trigger describes.

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: not_assessed

### D6: venue_fit_and_contribution

score: not_assessed

## Review Body

This is a modest, competently executed, deliberately narrow correlational study, and I want to say at the outset that its restraint is genuine rather than performative: the authors set a bounded question, kept correlational language throughout, and reported the coefficient with an interval and a robustness check rather than a bare asterisk. My objections are not to what the paper claims. They are to whether a reader has been given enough surrounding information to appraise the number the paper is built on.

The central problem is that r = .42 is presented as a portable quantity while the two ingredients that determine its meaning are undisclosed. On the outcome side, the study rests on a single five-point frequency item of unknown reliability. Two biases act on the observed coefficient in opposite directions and neither is named: measurement error in a single item attenuates r downward, while treating a five-category ordinal variable with plainly unequal psychological spacing ("rarely or never" to "several times daily") as an interval variable can push in the other direction. The Spearman check is a good instinct, but ρ = .40 speaks to monotonicity, not to reliability; it cannot repair attenuation, and the paper reads it as though it can ("indicating that the association did not depend on the parametric assumption"). On the predictor side, both constructs were collected in one instrument, at one moment, from one respondent, with no marker variable and no procedural separation. Some non-trivial share of .42 is plausibly method-shared. That is a standard and well-known feature of this design; what is not standard is that the Limitations section, which is otherwise conscientious, does not mention it.

The sampling account has a hole of the same kind. "All enrolled undergraduates were eligible" establishes a census frame but never gives its size, so no response rate exists anywhere in the paper. Limitation 4 then asserts voluntary-response bias without any magnitude attached to it — the reader cannot tell whether 214 represents 3% or 30% of the eligible population, and those imply very different exposures to self-selection. Relatedly, "spanned all four year levels" is a range statement, not a distribution, and it does nothing to establish correspondence with the institutional population.

I want to be explicit about executability, because a revision list that cannot be run on already-collected anonymous data is not a review, it is a wish. Almost everything I am asking for is executable now: the verbatim wording of both instruments and a statement of what "adapted" changed (the authors have these); the full category frequency distribution of the use item plus its SD (in the dataset); r² stated numerically rather than as "modest" (arithmetic); the frame size (registrar data, no re-contact needed); the year-level distribution against institutional figures (year level was evidently collected); a dimensionality check on the six perceived-usefulness items (item-level data exists); an explicit statement of the attenuation direction and a common-method-variance limitation (framing); and relabelling the power statement as sensitivity. The one thing I am *not* requesting is a second use item or log data — those are new data collection, and I flag them only as design guidance for the successor study the Conclusion already gestures at.

On coherence, my concern is narrow and mechanical. The paper's own literature review sets the standard — self-report "capture[s] perceived rather than actual engagement" — and then the abstract's final sentence spends it, reporting that perceived usefulness "tracks with LMS engagement." The same substitution recurs in the Discussion. This is one word, but it is one word in the most-read sentence of the manuscript, and it is the exact substitution the authors elsewhere warn against. Similarly, the onboarding implication is hedged twice but remains directional in a paragraph that has just granted the reverse pathway equal standing; if the direction is genuinely undetermined, then no perception-targeting intervention follows from the correlation at all, hedged or not.

### S1: Numerical integrity is exact across every section

The cleaning chain reconciles (233 − 14 − 5 = 214), the coefficient is reported identically in abstract, results, discussion, and conclusion, and the interval is not decorative: Fisher's z transformation at r = .42 with n = 214 returns approximately [.30, .53], matching the reported bound to rounding. This is more internal arithmetic discipline than I usually find at this scale of paper.

**Evidence Anchor**: text: §4 "r = .42, 95% CI [.30, .52], p < .001, n = 214"

### S2: The sensitivity computation is arithmetically correct

The claimed detectable effect is right: at n = 214, α = .05 two-tailed, 80% power, the minimum detectable r is approximately .19. My objection below concerns how this quantity is framed, not whether it was computed correctly.

**Evidence Anchor**: text: §3.4 "the study had greater than .80 power to detect a correlation of r >= .19 at alpha = .05"

### S3: Ethics and consent reporting is complete for this design

Committee approval, voluntary participation, absence of incentive, landing-page informed consent, and non-linkability are each stated. For an anonymous student survey this is the full set, and it is reported without padding.

**Evidence Anchor**: text: §3.3 "The study protocol was reviewed and approved by the university's research ethics committee"

### S4: The ordinal nature of the outcome is acknowledged and probed

The authors identify the measurement level of the use item themselves and run the appropriate rank-based check rather than leaving the Pearson coefficient unexamined. The check is incomplete for reasons I give in W1, but the instinct and the disclosure are correct.

**Evidence Anchor**: text: §3.4 "Because the use item is ordinal, we also computed a Spearman correlation as a robustness check"

### S5: Causal restraint is stated in the abstract, not buried in limitations

Most manuscripts of this type put the non-causal caveat where only a reviewer will read it. Placing it in the abstract, and repeating the bidirectionality argument in the discussion with a citation, is the correct handling of a cross-sectional association.

**Evidence Anchor**: text: Abstract "should not be read as causal, given the cross-sectional design"

### W1: Single-item ordinal outcome of unknown reliability, with the direction of bias never stated

The entire outcome variable is one item. No reliability evidence exists for it (none is obtainable from a single administration of a single item), yet the coefficient is interpreted as though it estimated an association between constructs. Two distortions operate simultaneously and neither is disclosed: measurement error attenuates r toward zero, while Pearson treatment of five ordered categories with unequal psychological spacing distorts in a less predictable direction. The Spearman check does not address reliability. At minimum the manuscript must state that .42 is a coefficient between *measures*, not constructs, and name the attenuation direction explicitly; reporting the full category distribution would also let a reader judge floor/ceiling compression, which materially affects the achievable correlation.

**Severity**: Major
**Evidence Anchor**: text: §3.2 "Self-reported use was captured with a single five-point frequency item asking how often the respondent accessed the LMS in a typical week"
**Confidence**: 5 — measurement error in single-item self-report measures is my primary research area

### W2: No sampling frame size, therefore no response rate and no representativeness evidence

A census frame is asserted but never sized, so the manuscript contains no response rate at any point. Limitation 4 then names voluntary-response bias without magnitude, which converts a quantifiable exposure into a rhetorical gesture. "Spanned all four year levels" is a range, not a distribution, and cannot support any inference about correspondence with the institutional population. The frame size is administrative data the authors can obtain without re-contacting anyone, and the year-level distribution is already in the dataset; both should appear, with a comparison against institutional figures and, if discipline was collected, a discipline breakdown as well.

**Severity**: Major
**Evidence Anchor**: text: §3.1 "All enrolled undergraduates were eligible"; "spanned all four year levels"
**Confidence**: 5 — nonresponse bias in institutional student surveys is my second research line

### W3: Common method variance is neither remedied nor named

Both constructs were captured in the same instrument, in the same sitting, from the same respondent, with no temporal separation, no marker variable, and no procedural remedy. This design guarantees that some portion of the observed covariance is method-attributable, and the direction is upward. The paper's Limitations section is otherwise thoughtful, which makes the omission conspicuous rather than routine: as written, a reader is told about self-report divergence from logs (a validity issue) but not about shared-method inflation (a covariance issue), and the two are distinct. This can be addressed in revision by naming it and, if a plausible marker exists in the instrument, running a partial-correlation check.

**Severity**: Major
**Evidence Anchor**: absence: Section 6 Limitations — expected an explicit common-method-variance limitation with marker-variable or procedural-separation remedy; checked Abstract, §3.2 Measures, §3.3 Procedure, §3.4 Analysis, §5 Discussion, §6 Limitations
**Confidence**: 5 — standard single-source design diagnostic

### W4: The adapted instrument is not reproducible and its factor structure is unverified

"Adapted" is doing unexamined work here. No item wording is given, no appendix is provided, and no description of what was changed from the Costa and Wren original appears anywhere. Coefficient alpha of .88 is then offered as the sole psychometric evidence, but alpha is a function of item count and inter-item covariance and is entirely compatible with a multidimensional set; it is not evidence that the adaptation preserved the original factor structure. Without the items, no reader can replicate the measure and no reader can judge whether the six items still measure what the validated original measured. A dimensionality check on the existing item-level data, plus the items themselves in an appendix, resolves this without new collection.

**Severity**: Major
**Evidence Anchor**: text: §3.2 "measured using a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"
**Confidence**: 5 — routine scale-adaptation reporting standard in psychometrics

### W5: A post hoc sensitivity computation is framed as design sensitivity

The power statement is calculated *from* the realized n of an availability sample. That is a legitimate and useful sensitivity analysis, but the sentence "so the design was sensitive to small-to-moderate associations" attributes to design a property that was determined by whoever happened to respond. No sample-size target preceded data collection, and none is claimed. Relabel it as a sensitivity analysis on the achieved sample. While revising this paragraph, "Analyses were conducted at a conventional significance threshold" should also be replaced with the actual α, which is stated two sentences earlier anyway.

**Severity**: Minor
**Evidence Anchor**: text: §3.4 "so the design was sensitive to small-to-moderate associations"
**Confidence**: 4 — standard distinction between a priori and sensitivity power analysis

### W6: Shared variance is described verbally rather than reported numerically

The Results paragraph makes a quantitative claim about shared variance and then declines to give the quantity. r² = .18 is one keystroke and lets the reader calibrate "modest" for themselves rather than accepting the authors' adjective. The outcome descriptives are similarly thin: a median category with no standard deviation and no frequency table, which prevents any assessment of distributional compression in the variable that carries the whole outcome side of the correlation. The scatterplot is asserted to have been inspected but is not shown, so the linearity and outlier claims are unverifiable.

**Severity**: Minor
**Evidence Anchor**: text: §4 "The proportion of variance shared by the two measures was accordingly modest"
**Confidence**: 5 — basic effect-size reporting convention

### W7: Deduplication criterion is unstated and sits in tension with the anonymity claim

Five submissions were classified as duplicates, but the manuscript states that no identifying information was collected and that responses cannot be linked to individuals. Duplicate detection under those conditions is possible — response-vector matching, session cookies, timestamp adjacency — but each carries a different false-positive risk, and none is described. As written, the reader cannot tell whether five genuine respondents were discarded. One sentence naming the criterion resolves it.

**Severity**: Minor
**Evidence Anchor**: text: §3.3 "No identifying information was collected, and responses could not be linked back to individual students"
**Confidence**: 4 — survey data-cleaning transparency; the tension is real but likely benign

### W8: Complete-case deletion is applied without characterizing the excluded cases

Fourteen incomplete submissions were removed and never mentioned again. Whether they dropped out before or after the perceived-usefulness block, and whether they differ on any observed variable, is not reported — and if they had answered the perceived-usefulness items but not the use item, those responses are informative about the missingness mechanism. Nor does the paper state whether any item-level missingness survived among the retained 214, or how it was handled in the correlation. Both are answerable from the existing file.

**Severity**: Minor
**Evidence Anchor**: text: §3.1 "14 incomplete submissions and 5 duplicate entries were removed, leaving 214 valid responses"
**Confidence**: 4 — standard missing-data reporting expectation

### W9: The abstract's concluding sentence substitutes "engagement" for the measured construct

The literature review commits the paper to a specific position: self-report captures perceived rather than actual engagement. The Methods honor it. The abstract's final sentence then abandons it, reporting that perceived usefulness "tracks with LMS engagement" — a behavioral construct the study did not measure. The same substitution recurs in the Discussion ("one of several factors bearing on engagement"). This is the sentence most readers will carry away, and it asserts more than the design produced. The fix is lexical, but it is not cosmetic: the paper's whole claim to restraint depends on this distinction holding everywhere.

**Severity**: Major
**Evidence Anchor**: text: Abstract "The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates"
**Confidence**: 5 — the contradiction is internal to the manuscript and does not require outside knowledge

### W10: The practical implication is directional in a paragraph that concedes bidirectionality

Two sentences after granting that the reverse pathway is "equally consistent with the data," the Discussion recommends attention to onboarding that raises perceived usefulness. If direction is genuinely undetermined, this recommendation has no correlational support: the same coefficient is equally compatible with usage driving perception, in which case onboarding aimed at perception is the wrong lever. The double hedge ("may be," "suggested by, not proven by") softens the register but does not repair the logic. Either state the additional premise the recommendation requires, or present it as a hypothesis for the longitudinal work the Conclusion proposes.

**Severity**: Minor
**Evidence Anchor**: text: §5 "LMS onboarding which helps students see concrete usefulness"; "may be worth institutional attention"
**Confidence**: 4 — inference-to-practice chain; the authors' hedging is partial mitigation
