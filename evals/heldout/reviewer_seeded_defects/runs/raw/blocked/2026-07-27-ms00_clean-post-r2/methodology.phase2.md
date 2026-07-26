contract_role: methodology

## Dimension Scores

### D1: methodology_rigor

score: block
block_class: repairable
trigger: "Core analytic quantities are unreportable or unverifiable as written"

The manuscript's entire empirical content is a single bivariate coefficient, and the reporting does not let a reader establish where that coefficient came from or what biases sit inside it. Three gaps compound: the composition of the analytic sample cannot be verified (the deduplication procedure is unspecified and contradicts the stated data-collection protocol), the population the sample estimates from cannot be characterised (no denominator, no response rate, no respondent breakdown), and the dominant known bias in a same-instrument self-report correlation — shared method variance — is never named, let alone diagnosed. Individually each is repairable; jointly they place the provenance and interpretation of *r* = .42 beyond independent evaluation as written. This is `repairable`, not `fatal`: the reported statistics are internally consistent and arithmetically sound, and every gap can be closed by disclosure plus analyses on the existing data and institutional enrolment records. No re-collection is required.

### D2: domain_accuracy

score: not_assessed

### D3: argumentative_coherence

score: warn
trigger: "a limitation named in one section and then disregarded in another"

The inference chain from design to conclusion is unusually disciplined. Causal language is avoided in the abstract, results, discussion, and conclusion; the reverse-causality pathway is named explicitly; the self-report/behavioural-trace gap is flagged in both the literature review and the limitations. The core empirical claim survives intact. Two local defects prevent a `pass`. First, §5 names the bidirectionality caveat and then, within the same paragraph, derives a directional intervention recommendation that only holds if the pathway the paper has just declared indeterminate runs forward; the hedge acknowledges the gap without closing it. Second, the dependent variable is defined narrowly in §3.2 as a self-reported weekly access-frequency item but is narrated as "engagement" in the abstract's headline sentence and again in §5. Neither defect overturns the reported association, so this stops short of `block`.

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: not_assessed

### D6: venue_fit_and_contribution

score: not_assessed

## Review Body

I reviewed this manuscript for design adequacy, measurement specification, data-handling transparency, statistical reporting, reproducibility affordances, and the coherence of the inference chain from design to stated conclusion. I did not assess literature coverage, construct selection relative to learning-analytics alternatives, venue fit, or presentation; those sit with other seats on the panel.

The honest summary is that this paper's execution discipline exceeds its evidentiary disclosure. Its inferential register is calibrated — genuinely so, not performatively — and I found no causal overreach to attack. What I did find is that the number the entire manuscript rests on is reported without the surrounding apparatus a reader needs to judge it: no response rate, no eligible-population denominator, an exclusion procedure that contradicts the stated anonymity protocol, a dependent variable whose response anchors are only partially reported and whose reliability is unknowable by construction, an independent variable described only as "adapted" from a prior instrument with no statement of what was adapted, and no acknowledgement anywhere that two self-report measures collected on one instrument at one sitting will produce an inflated association.

That last point deserves emphasis because it is structural rather than cosmetic. The reported CI [.30, .52] expresses sampling uncertainty only. It excludes two larger and opposing error sources that the design guarantees are present: upward shared-method inflation, and downward attenuation from binning a continuous behaviour into five self-assessed categories. Neither is quantified, neither is bounded, and neither is mentioned. The manuscript then compares .42 against prior findings and against Song's (2018) cross-institutional distribution as though it were a comparable estimate. It is not yet demonstrably one. The repair is not a redesign — it is naming shared-method variance as a limitation, running whatever post hoc diagnostic the existing data permit, reporting the response rate, and explicitly framing .42 as an upper bound on the substantive association under method inflation and a lower bound under DV coarseness.

On the ethics/deduplication contradiction: I want to be precise about why this matters beyond tidiness. If duplicates were identified through IP addresses, cookies, or session tokens, then the §3.3 claim that no identifying information was collected is incorrect as written, and the ethics-approval account needs correcting. If duplicates were identified heuristically from response patterns, then genuinely distinct respondents may have been deleted and the rule used should be stated so a reader can judge its false-positive risk. Both branches are legitimate and publishable; what is not publishable is leaving the reader unable to tell which occurred while asserting a protocol under which neither is possible.

Two things I am deliberately not asking for. I am not asking the authors to fit a full acceptance model with mediators — the paper declined that scope explicitly and reasonably, and the decision is defensible for a descriptive-correlational report. I am also not asking for behavioural log data as a condition of publication from this seat; that is a construct-and-data-source question belonging elsewhere on the panel. My requirements are confined to what the existing design can be made to disclose about itself.

### S1: Statistical reporting includes the quantities needed to judge magnitude and uncertainty

The coefficient is reported with its confidence interval, exact-threshold *p*, and sample size in a single statement rather than as a bare significance claim. I independently back-transformed the Fisher *z* interval for *r* = .42 at *n* = 214 and obtained [.303, .525], which rounds to the reported [.30, .52]. The interval is correct, not decorative.

**Evidence Anchor**: `text: §4 "r = .42, 95% CI [.30, .52], p < .001, n = 214"`
**Confidence**: 5 — direct recomputation of the Fisher transformation.

### S2: The ordinal-measurement objection is pre-empted with an appropriate robustness check

Rather than silently applying Pearson correlation to a five-category ordinal item, §3.4 states the concern and reports Spearman ρ = .40 alongside it, together with scatterplot inspection for linearity, monotonicity, and bivariate outliers. The near-identity of the two coefficients is what one would expect under a monotonic association without strong non-linearity, and it closes the parametric-assumption question cleanly.

**Evidence Anchor**: `text: §3.4 "Because the use item is ordinal, we also computed a Spearman correlation as a robustness check."`
**Confidence**: 5 — standard practice in survey psychometrics.

### S3: Sample accounting is transparent and internally consistent

Every exclusion is enumerated and the arithmetic reconciles exactly (233 − 14 − 5 = 214). This is above the norm at this tier, where analytic *n* frequently appears without a reconciled path from responses received. My objection in W1 concerns the deduplication *mechanism*, not the accounting, which is sound.

**Evidence Anchor**: `text: §3.1 "A total of 233 responses were received" and "leaving 214 valid responses"`
**Confidence**: 5 — arithmetic verification.

### S4: Inferential language is calibrated to what the design supports, including the rival direction

The manuscript names the reverse pathway rather than gesturing at "correlation is not causation," and it does so in the discussion where the temptation to overreach is strongest. Combined with the consistent correlational register across abstract, results, and conclusion, this is a genuinely disciplined inference chain and is the main reason D3 warrants `warn` rather than `block`.

**Evidence Anchor**: `text: §5 "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"`
**Confidence**: 4 — reading of the full inferential chain across sections.

### W1: Duplicate-removal procedure contradicts the stated anonymity and data-collection protocol

§3.1 reports the removal of five duplicate entries; §3.3 states that no identifying information was collected and that responses could not be linked back to individual students. Under the §3.3 protocol as written, duplicate identification is not possible. The manuscript must state the deduplication rule, and if it relied on IP address, cookie, or session token, correct the §3.3 anonymity claim and confirm that the approved protocol covered that collection. If it relied on response-pattern matching, the matching rule and its false-positive risk must be stated so a reader can judge whether distinct respondents were removed. Until then, the composition of the *n* = 214 analytic sample cannot be verified and the ethics account cannot be taken at face value.

**Severity**: Major
**Evidence Anchor**: `text: §3.1 and §3.3 "5 duplicate entries were removed" and "No identifying information was collected, and responses could not be linked back to individual students"`
**Confidence**: 5 — the two statements are directly incompatible as written.

### W2: Common method variance is unaddressed at every stage — design, analysis, and limitations

Both variables are self-reported, on the same instrument, at the same sitting, in adjacent Likert-type formats. This is the canonical condition for shared-method inflation of an observed correlation. The manuscript applies no procedural remedy (item separation, differing response formats, marker variable, temporal separation) and reports no post hoc diagnostic, and — more consequentially — never names the problem, so a reader is given no signal that .42 should be read as an upper bound. §6's self-report limitation concerns the self-report/log-trace divergence, which is a different issue and does not cover this one. Since the paper's stated purpose is to contribute a coefficient "comparable with prior work," an uncorrected and unacknowledged method-inflation component undermines exactly the comparability being claimed.

**Severity**: Major
**Evidence Anchor**: `absence: §3.4 Analysis and §6 Limitations — expected any procedural remedy or post hoc diagnostic for common method variance between two same-instrument self-report measures; checked abstract, §3.2 Measures, §3.4 Analysis, §4 Results, §6 Limitations`
**Confidence**: 5 — core area of my own methodological practice.

### W3: No response rate, no eligible-population denominator, and no respondent characteristics

§3.1 states that all enrolled undergraduates were eligible and that recruitment ran through the institutional announcement channel, but gives neither the enrolment figure nor a participation rate. §6 then asserts that students who engage more with institutional channels may be overrepresented — a plausible claim, but one the manuscript supplies no evidence to evaluate, bound, or rule out. The claim that the sample "spanned all four year levels" is offered without any breakdown, so even the crudest representativeness check is unavailable. Institutional enrolment figures are ordinarily retrievable, so this is a disclosure gap rather than a design constraint.

**Severity**: Major
**Evidence Anchor**: `absence: §3.1 Design and participants — expected the eligible-population denominator, the resulting response rate, and a respondent characteristics breakdown; checked §3.1, §3.4 Analysis, §4 Results, §6 Limitations`
**Confidence**: 5 — routine survey-reporting requirement.

### W4: Single-item ordinal dependent variable with unknown reliability and incompletely reported anchors

A single item cannot have its reliability estimated, so the attenuation it introduces into *r* is unquantifiable and no disattenuation is possible; no rationale is given for preferring it over a multi-item use scale. Compounding this, §3.2 supplies only the endpoint anchors (1 = rarely or never; 5 = several times daily), while §4 reports the median category as "a few times per week" — a label that appears nowhere in the scale definition. A reader therefore cannot determine whether the median falls at category 3 or 4, and cannot locate the sample's central tendency on the instrument at all. Report all five anchors, justify the single-item choice, and discuss the attenuation it imposes alongside the inflation in W2, since the two run in opposite directions and neither is currently bounded.

**Severity**: Major
**Evidence Anchor**: `text: §3.2 "Self-reported use was captured with a single five-point frequency item asking how often the respondent accessed the LMS in a typical week"`
**Confidence**: 5 — single-item indicator performance is my specialisation.

### W5: "Adapted" instrument is unspecified, breaking the inherited validation evidence

The perceived-usefulness measure is described as a six-item scale adapted from Costa and Wren (2019), with the original's validation invoked as support. No statement is given of which items were altered, how many, or why. Adaptation of unknown extent does not carry forward the source instrument's validity evidence, so the α = .88 obtained here attaches to a scale no reader can reconstruct. Internal consistency at that level is also not evidence of unidimensionality, and no factor-structure evidence from the present sample is reported. No instrument appendix, data availability statement, analysis-code statement, or software identification is provided, so none of this can be resolved externally. Supply the item wording, describe every adaptation, and add availability information.

**Severity**: Major
**Evidence Anchor**: `text: §3.2 "measured using a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"`
**Confidence**: 5 — routine instrument-adaptation reporting standard.

### W6: Power claim is marginally overstated at the stated effect size

At *n* = 214, α = .05 two-tailed, power to detect *r* = .19 computes to approximately .798, not "greater than .80"; the claim becomes true at roughly *r* ≥ .191. This has no bearing on any substantive conclusion and I raise it only for accuracy. Either state "approximately .80" or round the detectable effect to *r* ≥ .20.

**Severity**: Minor
**Evidence Anchor**: `text: §3.4 "the study had greater than .80 power to detect a correlation of r >= .19 at alpha = .05 (two-tailed)"`
**Confidence**: 5 — direct power computation.

### W7: The onboarding recommendation presupposes the directional pathway the same section declares indeterminate

§5 states that the reverse pathway is equally consistent with the data, then proposes that onboarding designed to raise perceived usefulness may warrant institutional attention. That proposal is only warranted if perception drives use — the direction just disclaimed. The qualifier "suggested by, not proven by, the present correlation" registers the gap without repairing it, because the issue is not strength of evidence for a direction but availability of any directional evidence at all. The single practitioner citation offered does not supply the missing warrant. Either withdraw the recommendation, or ground it in intervention evidence external to this correlation and attribute it accordingly. The core empirical claim is unaffected, but the recommendation is carried into the abstract and so requires more than a paragraph-level trim.

**Severity**: Major
**Evidence Anchor**: `text: §5 "may be worth institutional attention, a possibility also raised in practitioner accounts of digital-environment onboarding"`
**Confidence**: 4 — inference-chain analysis; the authors may hold implementation evidence not cited here.

### W8: Terminological drift between the measured variable and the reported conclusion

§3.2 defines the dependent variable narrowly and correctly as a self-reported weekly access-frequency item, and §4 reports it as such. The abstract's closing sentence and §5, however, describe the finding in terms of "engagement," which is a broader construct than the one measured. I raise this strictly as an internal consistency problem — whether access frequency is an adequate operationalisation of engagement in the first place is a separate question I leave to the panel seat that owns construct selection. The repair is inexpensive: use "self-reported access frequency" consistently wherever the finding is stated, including the abstract and conclusion.

**Severity**: Minor
**Evidence Anchor**: `text: abstract "The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates."`
**Confidence**: 4 — comparison of the operational definition against the reporting language.
