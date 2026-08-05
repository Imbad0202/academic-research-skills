## Dimension Scores

contract_role: methodology

### D1: methodology_rigor

score: block
block_class: repairable
trigger: "an undocumented or unvalidated instrument carrying the paper's primary measures"

Both of the study's two measures lack validity evidence in the form actually used. The predictor is an undescribed adaptation of Costa and Wren (2019) whose items are reproduced nowhere and whose structural equivalence to the source instrument is never tested; α = .88 establishes internal consistency only. The outcome is a single five-category self-report item with no reliability estimate of any kind and no reported category distribution. Layered on this are an uncomputable response rate, a robustness check that cannot detect the problem it is offered against, a power statement indistinguishable from post-hoc sensitivity, no treatment of common-method variance, and no reproducibility affordances. Each defect is repairable — most with information already in the authors' possession — but repair requires new computation, new disclosure, and substantial rewriting of the magnitude interpretation, which is beyond editorial polish.

### D2: domain_accuracy

score: not_assessed

### D3: argumentative_coherence

score: warn
trigger: "a plausible rival explanation left unaddressed without changing the overall verdict"

The central argument survives. The paper restricts itself to correlational language, names the reverse pathway explicitly, refuses the causal reading in abstract, discussion, and conclusion, and hedges the onboarding implication. The slippage is local and one-sided: the design's shared-method structure — two self-reports, one instrument, one sitting — is a rival explanation for part of the observed association and is never raised, while the opposing bias (attenuation from coarse categorization and single-item unreliability) is also unaddressed. The consequence is that "moderately associated" is treated throughout as an interpretable magnitude when the design licenses only sign and significance. One inferential claim also outruns its evidence: the Spearman check is said to show the association "did not depend on the parametric assumption," which is not what that coefficient establishes for a five-category variable.

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: not_assessed

### D6: venue_fit_and_contribution

score: not_assessed

## Review Body

This is a modest, honestly framed study, and its restraint is genuine rather than performative: the causal disclaimers are consistent across sections, the limitations are real constraints rather than ritual, and the reported statistics are arithmetically coherent. My objections are not to the paper's ambition, which is appropriately small, nor do I ask for a larger model — 214 cases and two constructs cannot support SEM and should not be asked to. My objections are that the one number the paper exists to report has no defensible interpretation of magnitude as the manuscript currently stands, and that the measurement basis for both variables is undocumented to a degree that prevents any reader from evaluating it independently.

The core problem is a two-sided, unquantified bias bracket. Categorizing an underlying continuum into five ordered levels attenuates a product-moment correlation downward, and a single item of unknown reliability attenuates it further by an unknown amount; both push .42 below whatever the latent association is. In the opposite direction, measuring both constructs by self-report in one instrument at one sitting with adjacent items inflates the observed covariance. The manuscript discusses neither mechanism. It instead reports *r* = .42 to two decimals with a 95% CI of [.30, .52] — an interval that quantifies sampling error and nothing else — and then reads "moderate" off that number as though it were a magnitude estimate. The honest statement is that the sign and the statistical significance are robust to both biases, while the absolute magnitude is bracketed between two unmeasured distortions of opposing sign and should not be characterized on the small/moderate/strong scale at all.

The robustness check compounds this rather than relieving it. Spearman's ρ is a legitimate coefficient, but it does not address the coarseness of a five-category variable correlated against a continuous mean score; with that many ties it is largely redundant with Pearson, which is exactly why ρ = .40 tracked *r* = .42 so closely. The estimator that speaks to the stated concern is the polyserial correlation, which models the ordinal item as a coarsened continuous variate and returns a disattenuated-for-categorization estimate. Computing it requires no new data. Until it is reported, the manuscript has performed a check that cannot detect the problem it purports to address, and has then drawn a conclusion from that check that the check does not license.

On sampling, the study states that all enrolled undergraduates were eligible but never states how many that is, so the response rate is uncomputable and nonresponse bias cannot be bounded even descriptively. The limitations section correctly flags voluntary-response bias, but flagging a bias without a denominator leaves the reader unable to judge whether the concern is trivial or fatal to external validity. Similarly, the power sentence is arithmetically correct — .80 power at α = .05 two-tailed with n = 214 corresponds to detectable *r* ≈ .19 — but that is precisely the sensitivity value one obtains by feeding the achieved sample size back into the formula. The manuscript should say plainly whether a target *n* was set before collection, and if not, should label the statement a sensitivity analysis.

For the domain reviewer's use, one observation crosses into substantive territory: the paper cites Vasquez (2020) to establish that self-reports diverge from behavioral logs, then treats that caution as discharged by relabeling the outcome "perceived use." Relabeling addresses construct naming; it does not address the measurement properties that make the coefficient hard to interpret. Whether that is a fair reading of Vasquez is for the domain seat.

### S1: Reported inferential statistics are complete and internally consistent

The correlation is reported with its effect size, exact-threshold *p* value, confidence interval, and sample size together in one place, and the interval reproduces: Fisher's *z* for *r* = .42 with *n* = 214 gives SE = .0688 and back-transforms to approximately [.30, .52]. This level of reporting completeness is above the median for the LMS-acceptance literature and made the audit above possible.

**Evidence Anchor**: `text: §4 Results "r = .42, 95% CI [.30, .52], p < .001, n = 214"`

### S2: Ethics and consent documentation is complete

Approval body, voluntariness, absence of incentive, anonymity, and the consent mechanism are all stated, and the consent point of delivery is specified rather than implied. Nothing here needs revision.

**Evidence Anchor**: `text: §3.3 Procedure and ethics "The study protocol was reviewed and approved by the university's research ethics committee"`

### S3: Bivariate assumption checking is reported rather than assumed

Linearity, monotonicity, bivariate outliers, and marginal symmetry are all inspected and reported. Most manuscripts at this scale assert Pearson's appropriateness silently; this one shows its work, which materially raises confidence that the coefficient is not artifactual.

**Evidence Anchor**: `text: §3.4 Analysis "Scatterplot inspection showed an approximately linear, monotonic association with no extreme bivariate outliers"`

### S4: Inferential restraint is consistent across sections

The refusal of causal language is not confined to a limitations paragraph; it holds in the abstract, the discussion, and the conclusion, and the reverse pathway is named as equally consistent with the data. Design-to-claim discipline of this kind is the reason D3 is a warn and not worse.

**Evidence Anchor**: `text: §5 Discussion "the correlation cannot establish that perceived usefulness causes use"`

### W1: Response rate is uncomputable because the eligible population is never stated

The manuscript reports 233 responses received and 214 retained but never gives the number of enrolled undergraduates in the eligible frame. Without that denominator no response rate exists, and the voluntary-response bias the authors correctly acknowledge cannot be bounded even to an order of magnitude. This is a one-sentence disclosure the authors already possess; its absence is what turns a routine limitation into an unassessable one.

**Severity**: Major
**Evidence Anchor**: `absence: §3.1 Design and participants — expected the eligible undergraduate enrolment denominator and a computed response rate; checked §3.1, §3.4, §4, §6, and the Abstract`
**Confidence**: 5 — routine survey-reporting standard, verified by reading every section for a population figure

### W2: Validity of the adapted instrument is transferred from the source, not demonstrated

The predictor scale is described as adapted from a validated original, with the original's psychometric strength cited in the same clause. Adaptation is precisely what breaks that inheritance: nothing states what was changed, why, or how many items were reworded versus replaced. Cronbach's α = .88 in the present sample establishes internal consistency and nothing about dimensionality — no factor analysis or CFA is reported, so there is no evidence the adaptation preserved the original structure. The six items are reproduced nowhere in the manuscript, so no reader can evaluate face or content validity independently.

**Severity**: Major
**Evidence Anchor**: `text: §3.2 Measures "adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"`
**Confidence**: 5 — direct specialization in self-report instrument adaptation and validity evidence

### W3: The Spearman robustness check cannot address the ordinality problem it is offered against

Correlating a five-category ordinal item with a continuous mean score raises a coarse-categorization question, and Spearman's ρ does not answer it: with only five levels the rank transformation produces massive ties and yields an estimate nearly collinear with Pearson's, which is what happened here (ρ = .40 versus *r* = .42). The polyserial correlation is the appropriate estimator, requires no new data, and would give the reader an attenuation-corrected magnitude. As written, the manuscript further claims the check shows the association "did not depend on the parametric assumption," a conclusion the check does not support.

**Severity**: Major
**Evidence Anchor**: `text: §4 Results "indicating that the association did not depend on the parametric assumption"`
**Confidence**: 5 — published work on correlation attenuation under categorical measurement

### W4: The single-item outcome makes r = .42 a downward-biased floor of unquantifiable depth

The dependent variable is one five-category self-report item. Two attenuating forces act on it simultaneously: categorization of an underlying continuum into five levels, and single-item unreliability that cannot be estimated because no internal-consistency or test–retest evidence exists for a lone item. The first is correctable by polyserial estimation; the second is not correctable at all with these data. The consequence is that .42 should be presented as a lower bound conditional on the measurement, not as a magnitude to be labelled "moderate," and the paper should say which of the two attenuating sources it can and cannot quantify.

**Severity**: Major
**Evidence Anchor**: `text: §3.2 Measures "Self-reported use was captured with a single five-point frequency item"`
**Confidence**: 5 — core specialization in single-item versus multi-item indicator properties

### W5: Common-method variance is never raised, though it biases the estimate in the opposing direction

Both constructs were measured by self-report, within one instrument, at one sitting, with the use item positioned adjacent to the usefulness items. Consistency motives and item-context effects inflate the observed covariance by an unknown amount. The limitations section addresses only whether self-reported use accurately reflects behavior — a construct-fidelity concern — and never the shared-method concern, which is a distinct threat to the association itself. Because it pushes opposite to the attenuation in W4, the manuscript's true magnitude is bracketed by two unquantified biases of opposing sign, and this should be stated rather than left implicit.

**Severity**: Major
**Evidence Anchor**: `absence: §5 Discussion and §6 Limitations — expected acknowledgement that both variables were self-reported in one instrument at one sitting, inflating the observed association; checked §3.2, §3.4, §5, §6, and §7`
**Confidence**: 5 — standard survey-methods threat, verified absent across all interpretive sections

### W6: The power statement reads as a priori but is indistinguishable from post-hoc sensitivity

The reported figure is the exact sensitivity value implied by the achieved *n*: with n = 214 at α = .05 two-tailed, the detectable *r* at .80 power is ≈ .19. Nothing in the manuscript states whether a target sample size was set before collection or whether the calculation was run afterwards on the sample obtained. The distinction matters for how the phrase "the design was sensitive to" should be read, and one clarifying sentence resolves it.

**Severity**: Minor
**Evidence Anchor**: `text: §3.4 Analysis "the study had greater than .80 power to detect a correlation of r >= .19 at alpha = .05"`
**Confidence**: 4 — arithmetic verified; the a priori/post-hoc question is unresolvable from the text alone

### W7: The use item's category distribution is withheld, hiding the very coarseness at issue

Results give only a median category for the outcome. Without per-category frequencies a reader cannot see whether responses were spread across all five levels or piled into two, cannot judge whether ceiling effects are truncating the association, and cannot assess how much categorization attenuation is likely operating. This is a small table that would materially inform the interpretation of the headline coefficient.

**Severity**: Minor
**Evidence Anchor**: `absence: §4 Results — expected the frequency distribution across the five use categories, or at least a per-category n; checked §4, §3.2, and the Abstract`
**Confidence**: 5 — straightforward descriptive-reporting gap

### W8: Duplicate-removal procedure is unstated and sits in tension with the anonymity claim

Five submissions were removed as duplicates, yet the ethics section states that no identifying information was collected and responses could not be linked to individuals. Deduplication without identifiers is achievable — session tokens, timestamps, or response-pattern matching — but the manuscript names no mechanism, leaving an apparent internal tension and no basis for judging whether legitimate responses were discarded. The 14 incomplete submissions are likewise removed without any characterization of how they differed from retained cases.

**Severity**: Minor
**Evidence Anchor**: `text: §3.3 Procedure and ethics "No identifying information was collected, and responses could not be linked back to individual students"`
**Confidence**: 4 — the tension is plainly visible; benign explanations exist but none is stated

### W9: No reproducibility affordances are provided

There is no data availability statement, no instrument appendix, no analysis code, and no named software or version. For an analysis this simple the reproducibility cost of supplying the six items and a summary data table is near zero, and their absence means the only route to independent verification — recomputing the coefficient from the responses — is closed.

**Severity**: Minor
**Evidence Anchor**: `absence: §3.4 Analysis and end matter — expected a data, instrument, or analysis-code availability statement and named software with version; checked §3.2, §3.3, §3.4, §7, and the reference list`
**Confidence**: 5 — checked every section and the reference list for an availability statement
