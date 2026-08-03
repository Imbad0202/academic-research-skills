contract_role: methodology

## Dimension Scores

### D1: methodology_rigor

score: block
trigger: "a load-bearing methodological element is absent or internally inconsistent"
block_class: repairable

The analysis itself is defensible and the inferential reporting is above average for this literature. What fails the bar is documentation of three load-bearing elements: the sampling denominator (no enrollment total, hence no response rate), the instrument actually administered (an undocumented adaptation, no item wording, no dimensionality evidence for the adapted six items), and the data-cleaning mechanism (duplicate removal that the stated anonymity procedure appears to preclude). None of these requires new data collection to repair, which is why the block is classed repairable rather than fatal: a reader currently cannot reconstruct who was sampled, what was measured, or how the analytic sample of 214 was arrived at.

### D2: domain_accuracy

score: not_assessed

### D3: argumentative_coherence

score: warn
trigger: "individual inferential steps overreach or are loosely joined"

The central thesis — a positive, moderate, non-causal association within one bounded sample — is genuinely underwritten by the reported evidence, and the causal disclaimer is carried consistently from abstract to conclusion. Two inferential steps nonetheless overreach: the abstract's assertion that the predictor was measured with a "previously validated instrument" transfers validation from an original instrument to an undocumented adaptation, and the Spearman check is positioned as retiring a robustness concern that it only partially addresses, while the self-report limitation conceded in §6 is never carried back into how the point estimate is interpreted or compared to prior effect sizes.

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: not_assessed

### D6: venue_fit_and_contribution

score: not_assessed

## Review Body

This is a modest, honestly framed correlational study, and I want to be clear at the outset that its problems are reporting problems rather than analytic ones. The research question is narrow by declared intent; the analysis chosen (a bivariate correlation with a rank-order robustness check, effect size with a confidence interval, an explicit sensitivity statement) is the right analysis for that question. I found no evidence of selective reporting, no unreconciled numbers between text and prose, and no causal language smuggled into the conclusions. The paper's claim discipline is better than most manuscripts I see in this area.

The block on D1 rests on the fact that three separate elements a reader needs in order to use the reported coefficient are either absent or self-contradictory in the manuscript as submitted. First, the recruitment frame is stated as universal ("all enrolled undergraduates were eligible") but the denominator that would make that statement informative is never given, so the response rate is uncomputable and the acknowledged voluntary-response bias remains entirely unquantified — the reader cannot tell whether 233 responses represent 5% or 40% of the eligible population, and those two scenarios support very different generalization claims. Second, the predictor variable — the paper's only substantive measurement instrument — is described as an adaptation with no report of what was adapted, no item wording, and no structural-validity evidence for the adapted form. Cronbach's α = .88 establishes that the six items covary in this sample; it does not establish that they measure the same single construct the original instrument measured, and it cannot substitute for a dimensionality check that the existing data would readily support. Third, the deduplication statement and the anonymity statement cannot both be true as written. I raise this last point not as a technicality but because its resolution has consequences in either direction: if some identifier (email, IP, session token, institutional login) was in fact captured to detect the five duplicates, then the ethics statement in §3.3 misdescribes the data collection and requires correction; if no such identifier existed, then the basis for classifying five submissions as duplicates is unexplained and the analytic sample definition is unverifiable. This is a concrete and answerable question, and the authors are best placed to answer it.

On the outcome measure, I will flag my own predisposition explicitly so the panel can discount it appropriately. My seat is inclined to ask for measurement machinery that a deliberately narrow paper may not warrant, and I do not think this manuscript is obliged to fit a latent-variable model to two variables. What it is obliged to do is tell the reader that a single five-point frequency item, treated as the dependent variable, places a ceiling on the observable coefficient through coarse categorization and unmodeled item unreliability, so that r = .42 is an attenuated estimate of whatever the underlying association is. The paper never says this. It instead presents the coefficient as a clean point estimate, compares it favorably to "prior technology-acceptance research" whose outcome measures may have been multi-item or log-based, and offers the Spearman check as though it had addressed the measurement-level worry. Spearman's ρ addresses monotonicity and the normality assumption; it does nothing about coarseness or unreliability, and ρ = .40 with five outcome categories is subject to essentially the same attenuation as r. The minimum acceptable repair here is textual — a caveat plus a comparability qualification — not a re-analysis. A polyserial or polychoric estimate would be informative but is optional.

The sample is also under-exploited relative to what was collected. The paper notes that all four year levels are represented and then reports no breakdown by year, no covariate adjustment, and no subgroup comparison, while the outcome item is summarized only by a median category with no frequency distribution and no full set of response-option labels. Given that Ibarra and Poll (2021) are cited precisely for the contextual determination of both perception and use, and that course requirements and assessment schedules are invoked in the Results as unmeasured influences, a year-level descriptive table would cost nothing and would let a reader judge whether the pooled coefficient masks heterogeneity. I am not asking for a model the design cannot carry; I am asking for descriptives the data already contain.

Finally, reproducibility affordances are thin in the conventional sense as well: no data or code availability statement, no named analysis software, and the significance threshold stated once as "a conventional significance threshold" and once numerically inside the power sentence. For a two-variable correlation these are low-cost additions, and I weight them accordingly.

### S1: Claim strength is calibrated to design throughout

The paper states the reverse-causation pathway explicitly rather than gesturing at it, and the correlational framing survives intact from abstract through conclusion without a single directional slip in the substantive claims. This is unusual and worth preserving in revision.

**Evidence Anchor**: text: §5 Discussion "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"

### S2: Uncertainty reporting is pre-specified and complete

The analysis plan commits to reporting the coefficient with an interval estimate, p value, and n together, and §4 delivers exactly that set. Interval estimation is present where much of this literature reports significance verdicts alone.

**Evidence Anchor**: text: §3.4 Analysis "we report the correlation coefficient alongside its 95% confidence interval, p value, and sample size"

### S3: Assumption checks are reported rather than assumed

Linearity, monotonicity, bivariate outliers, and marginal symmetry are each explicitly inspected, and the rank-order estimate is reported as a check rather than swapped in silently. The checks reported are the correct ones for a Pearson estimate.

**Evidence Anchor**: text: §3.4 Analysis "Scatterplot inspection showed an approximately linear, monotonic association with no extreme bivariate outliers"

### S4: Reliability is estimated in the present sample, not borrowed

The composite's internal consistency is computed on these data rather than cited from the source instrument, and the scoring rule (mean of six items) is stated. This is the correct practice even though it does not, by itself, establish structural validity.

**Evidence Anchor**: text: §3.2 Measures "In the present sample, the scale showed good internal consistency (Cronbach's α = .88)"

### W1: Deduplication procedure is incompatible with the stated anonymity conditions

Five submissions were classified as duplicates and removed, yet the procedure section states that no identifying information was collected and that responses could not be linked to individuals. Under those conditions no stated mechanism exists for identifying a duplicate. Either an identifier was captured — in which case the ethics and anonymity statement requires correction — or the duplicate classification rests on an undisclosed heuristic, in which case the analytic sample definition (233 − 14 − 5 = 214) cannot be verified. The numerical consequence is small; the reporting consequence is not, because one of two load-bearing methods statements is inaccurate as written.

**Severity**: Major
**Evidence Anchor**: text: §3.1 and §3.3 "5 duplicate entries were removed" versus "No identifying information was collected, and responses could not be linked back to individual students"
**Confidence**: 5 — routine survey data-handling and human-subjects reporting review; the contradiction is on the manuscript's face.

### W2: No enrollment denominator, therefore no response rate and no bound on nonresponse bias

Eligibility is described as universal but total enrollment is never reported, so the response rate cannot be computed from any figure in the paper. §6 concedes that voluntary response may overrepresent students who engage with institutional channels, but leaves that concession entirely qualitative. Since the correlation is being offered as a descriptive estimate for a defined undergraduate population, the reader needs the denominator to judge whether the estimate describes that population at all or a small self-selected fraction of it. Reporting institutional enrollment for the survey window, plus any available comparison of respondent year-level distribution against enrollment composition, would resolve this without new data collection.

**Severity**: Major
**Evidence Anchor**: absence: §3.1 Design and participants — expected total eligible enrollment and a computed response rate; checked §3.1, §3.4, §6, and the abstract
**Confidence**: 5 — teach survey sampling; response-rate reporting is a baseline expectation for any eligibility-defined survey.

### W3: Instrument adaptation is undocumented and validity is borrowed rather than demonstrated

The perceived-usefulness scale is the paper's only multi-item measure and its provenance is given as an adaptation of a prior instrument, with no statement of which items were changed, how, or why, and no reproduction of the administered wording. Validation properties do not transfer automatically across adaptation, and α does not speak to dimensionality: a six-item set can return α = .88 while being two correlated factors. The repair is bounded and uses data already in hand — report the administered items (appendix or supplement), state the changes made relative to the source, and report a dimensionality check on the six items.

**Severity**: Major
**Evidence Anchor**: text: §3.2 Measures "a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"
**Confidence**: 5 — psychometrics background; adaptation documentation and structural evidence are standard requirements for a borrowed scale.

### W4: Attenuation from the coarse single-item outcome is neither acknowledged nor carried into interpretation

The dependent variable is one five-point frequency item. Categorization at five levels plus unmodeled item unreliability both attenuate the observable coefficient, so r = .42 is a lower bound on the underlying association, not a neutral point estimate. The paper presents the Spearman check as showing that the association "did not depend on the parametric assumption," which is true of linearity and normality but is silent on coarseness and reliability — ρ = .40 is attenuated by the same mechanism. This matters for a core claim, because the paper's comparison of its coefficient to prior technology-acceptance findings presumes metric comparability across studies whose outcome measures may have been multi-item or behavioral. A caveat in §3.2/§4 and a qualification of the comparability claim in §5 are the minimum; re-estimation with an attenuation-aware coefficient is welcome but not required by the paper's declared scope.

**Severity**: Major
**Evidence Anchor**: text: §4 Results "indicating that the association did not depend on the parametric assumption"
**Confidence**: 4 — direct specialization in single-item self-report measurement; the magnitude of attenuation here is unknown without the item distribution.

### W5: No reproducibility affordances beyond the prose description

There is no data availability statement, no code or analysis-script availability statement, no named software, and the decision threshold is given verbally in one place and numerically only inside the power sentence. For a two-variable correlation the analytic burden is trivial, which is precisely why the omission is easy to fix; it does not change the reported result.

**Severity**: Minor
**Evidence Anchor**: absence: §3.4 Analysis and §7 Conclusion — expected a data/code availability statement and named analysis software or package versions; checked §3.2, §3.3, §3.4, §7, and the reference list
**Confidence**: 4 — routine venue-reporting expectation; the appropriate level of disclosure depends partly on the target journal's policy.

### W6: Descriptive capacity of the sample is left unused

All four year levels are reported as represented, yet no breakdown by year appears anywhere, and no covariate or subgroup analysis is attempted. The outcome item is summarized by a median category only, with no frequency distribution and no full set of response-option labels (endpoints plus one interior label appear, the remaining anchors do not). Given that the paper itself attributes unexplained variance to course requirements and assessment schedules, and cites prior work on contextual moderation, a simple descriptive table by year level would let readers judge whether the pooled coefficient conceals heterogeneity. This does not change the headline finding; it strengthens what the reader can do with it.

**Severity**: Minor
**Evidence Anchor**: text: §3.1 Design and participants "The analyzed sample of 214 students spanned all four year levels"
**Confidence**: 4 — standard descriptive-reporting expectation for a single-site survey.

### W7: Power statement is framed as a design property and inherits the outcome-metric problem

The sensitivity computation itself is credible at n = 214, but it is written as though the study had been powered prospectively rather than as a post hoc sensitivity bound, and it is computed under Pearson assumptions on a coarse ordinal outcome, so nominal sensitivity to r ≥ .19 in the observed metric is not sensitivity to a latent association of that size. Reframing this explicitly as a post hoc sensitivity analysis, and stating α once and consistently, would fix it.

**Severity**: Minor
**Evidence Anchor**: text: §3.4 Analysis "the study had greater than .80 power to detect a correlation of r >= .19"
**Confidence**: 4 — routine power/sensitivity reporting; the attenuation adjustment is unquantified without item-level data.

### W8: Abstract asserts a validation property the paper does not establish for its own instrument

The abstract states that the predictor was measured with an adapted, previously validated instrument. As written, this attaches the source instrument's validation to a version whose differences from the source are never disclosed. The wording should either be hedged (an adaptation of a previously validated instrument, with adaptation documented in Methods) or earned by supplying the documentation requested in W1's companion finding on the instrument. This is the claim-language counterpart of the documentation gap and will likely resolve alongside it.

**Severity**: Minor
**Evidence Anchor**: text: Abstract "Perceived usefulness was measured with an adapted, previously validated instrument"
**Confidence**: 5 — direct reading of the abstract against §3.2.
