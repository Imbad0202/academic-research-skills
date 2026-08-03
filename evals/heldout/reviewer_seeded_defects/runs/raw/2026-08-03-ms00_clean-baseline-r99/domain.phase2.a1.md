contract_role: domain

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: warn
trigger: "an over-general or under-qualified characterisation of the prior literature, a stale or incomplete evidence base on a secondary point"

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I read this manuscript as someone who has spent two decades inside the technology-acceptance tradition in education, including synthesising perceived-usefulness effects on student system use. My remit here is factual and interpretive fidelity to that domain, not elegance of argument or fit to the venue.

The short verdict: nothing in this paper is domain-*false*, and several things in it are domain-*careful* in a way I do not often see. The reported statistics are internally coherent — the 95% confidence interval [.30, .52] is what a Fisher transform on r = .42 with n = 214 produces, the Spearman check at ρ = .40 is consistent with the Pearson estimate, the case-attrition arithmetic (233 − 14 − 5 = 214) closes, and "moderately associated" is the correct verbal label for r = .42 under conventional benchmarks. The paper describes the shared variance as "modest," which is right (r² ≈ .18) and refreshingly unspun. Its handling of the cautionary sources it does cite is faithful rather than opportunistic: the reverse-causation point is correctly attributed, the self-report-versus-log divergence is correctly used to reframe the outcome as *perceived* use, and the multi-campus heterogeneity point is used to argue that a single-site estimate is one draw from a distribution. That last move is, in my reading, the most sophisticated sentence in the manuscript.

Which is exactly where the domain problem lies. Having stated that a single-site estimate should be read as "one point in a distribution," the paper never tells the reader what the distribution looks like. The claim carried in the abstract, the discussion, and the conclusion is that r = .42 is "consistent with prior technology-acceptance research." No comparator value appears anywhere in the manuscript. Costa and Wren (2019) and Ibarra and Poll (2021) are invoked as the consistency check, but neither is reported with an effect size, so the reader cannot tell whether .42 is near, above, or below what those studies found, let alone what the field's cumulative evidence says. As stated, the consistency claim is unfalsifiable. This is a domain-accuracy defect and not merely a rhetorical one, because the paper's entire stated contribution is comparability: "an incremental data point, comparable with prior work."

The correct comparator is not four individual studies but the pooled distribution of PU–use associations, which in education-sector syntheses of this tradition has been repeatedly estimated. My recollection of that literature — and the authors should retrieve current values rather than take mine — is that PU–use associations cluster broadly in the .30–.50 band, with PU–*intention* paths sitting systematically higher. On that reading, r = .42 is close to unremarkable, and the honest framing available to the authors is stronger than the one they chose: "our single-site estimate reproduces the pooled effect." They cannot make that claim, because they never went to the pooled effect. Two further domain facts sharpen this. First, much of the pooled literature shares this paper's common-method design (self-report on both sides), which inflates such estimates; a paper that cites Vasquez (2020) on log-versus-self-report divergence has already conceded the premise that makes this comparability question live, then declines to work through it. Second, effect sizes in this literature vary systematically with instrument and with voluntariness of use — the manuscript itself notes that "effect sizes vary across samples and instruments" and never returns to the implication.

On the literature base: six references, none canonical, nothing after 2021. Davis is absent, so the PU construct's originating definition and measure are absent; UTAUT and its voluntariness moderator are absent; the existing meta-analyses of PU–use associations in education are absent. The consequence is not a citation-etiquette complaint. It is that the manuscript's definition of perceived usefulness — "the degree to which a person believes a technology will help them perform better" — is a near-paraphrase of the tradition's founding definition, attributed here to two secondary sources from 2019 and 2020. A paper positioning itself as an increment to a mature literature has misplaced that literature's provenance, and a "substantial body of work" claim in the introduction rests on a single citation. Authors who know this literature would have anchored the construct where it originates and benchmarked against what the field has already pooled.

On construct architecture: the acceptance tradition models perceived usefulness → behavioural intention → use behaviour. This paper collapses to PU → self-reported use. The paper is entitled to decline a full model test, and says so plainly; I want to be explicit that I am not demanding one. What I am asking for is the domain consequence of the omission, which the paper never states: a PU–use coefficient and a PU–intention coefficient are different estimands with different expected magnitudes, so "consistent with prior technology-acceptance research" is not an apples-to-apples statement unless the authors specify which link they are comparing against. Related and smaller: because only one construct was measured, the estimate cannot be separated from generalised favourability toward the platform, and because LMS use in most courses is at least partly assessment-driven rather than voluntary, the moderator that this literature has studied most directly is the one this design cannot see. The paper names assessment schedules as a competing influence in its results section and then leaves the relevant literature untouched.

On the contribution question my configuration invites me to answer plainly: the field does not need another single-site PU–use correlation reported as a novel association. It can use one reported as a benchmarked replication. The minimum addition that would make this worth the space is not new data collection: it is (a) locating r = .42 within the pooled distribution with actual numbers, (b) stating which estimand that distribution refers to and adjusting the comparison accordingly, and (c) reframing the contribution as replication-with-known-limits rather than increment. Log validation, multi-site sampling, or a moderator analysis would raise the ceiling considerably, but the paper's stated ambition is defensible at the lower ceiling if the benchmarking is actually done.

Two notes for the seats that own dimensions I do not score. For methodology: the single-item ordinal outcome and the undocumented adaptation of the source instrument bear on measurement adequacy, and the power statement's ">.80 to detect r ≥ .19" is right at the boundary (my calculation returns approximately .80, not comfortably above it). For argumentative coherence: the unfalsifiable consistency claim described above is simultaneously a gap in the inferential chain, and I leave that verdict where it belongs.

On the score: I considered a block. My Phase 1 block trigger requires either a central claim contradicted by well-established evidence or a named source misrepresented in a way that props up a headline conclusion. Neither holds. r = .42 is not contradicted by the field's evidence; it is probably squarely consistent with it, which is the irony of the paper's failure to demonstrate as much. The sources actually cited are represented faithfully. What fires is my warn trigger: an over-general and under-qualified characterisation of the prior literature, resting on a stale and incomplete evidence base. I record one interpretive point for the synthesiser: my warn trigger's preamble described such defects as ones that "do not carry a headline conclusion," and here the over-generalisation does touch the abstract. I still read this as warn rather than block, because the defect is unsubstantiation of a claim that is very likely true, not inaccuracy — and because the alternative would penalise a transparently reported, non-inflated correlational study for lacking a model it explicitly and legitimately declined to test.

### S1: Faithful, non-opportunistic use of the cautionary literature it does cite

The reverse-causation, self-report-versus-log, and cross-site-heterogeneity cautions are each attributed to the correct source and used against the authors' own interest rather than decoratively. The Song (2018) framing in particular states the distributional logic that this literature requires of single-site estimates.

**Evidence Anchor**: text: §2 ¶2 "any single-site estimate is best read as one point in a distribution rather than as a fixed value"

### S2: Quantitative record is internally coherent and correctly labelled

The interval, the p value, the sample size, and the Spearman robustness check are mutually consistent, and the verbal characterisations ("moderately," "modest" shared variance) match the numbers rather than overstating them. On the reported record I found no internally impossible or self-contradicting domain quantity.

**Evidence Anchor**: text: §4 ¶2 "r = .42, 95% CI [.30, .52], p < .001, n = 214"

### S3: Correlational language is sustained without causal drift

From abstract to conclusion the association is never upgraded to an effect. In a literature where cross-sectional acceptance surveys routinely slide into causal phrasing by the discussion section, this discipline is a genuine merit and should be preserved in revision.

**Evidence Anchor**: text: Abstract "should not be read as causal, given the cross-sectional design"

### W1: The "consistent with prior research" claim is never benchmarked against any comparator value

The headline comparability claim appears three times (abstract, discussion, conclusion) with no effect size from any cited study and no reference to the field's pooled PU–use estimates. As written, no reader can test whether .42 is consistent, high, or low. Because comparability is the paper's stated contribution, this is not a presentational gap: the contribution claim cannot be evaluated. Repair requires retrieving the meta-analytic distribution for education-sector PU–use associations and locating this estimate within it explicitly, with a stated verdict of near/above/below the pooled value.

**Severity**: Major
**Evidence Anchor**: absence: §2 Literature Review and §5 Discussion — expected a reported comparator effect size or pooled PU–use estimate against which r = .42 could be located; checked abstract, §1, §2, §4, §5, §7, and all six reference entries
**Confidence**: 5 — I have co-authored a meta-analysis of perceived-usefulness effects on student system use and know what benchmarking this claim requires

### W2: Estimand mismatch between this design and the tradition it claims consistency with

The acceptance tradition estimates PU → behavioural intention → use; this paper estimates PU → self-reported use. The authors are entitled to decline a full model test, but the omission changes what their coefficient is comparable to, since PU–intention paths in this literature run systematically larger than PU–use paths, and log-validated use paths differ again from self-reported use paths. The manuscript never states which link its comparison targets, so its consistency claim is not established as an apples-to-apples comparison even in principle. Repair is a paragraph specifying the estimand and adjusting the comparator accordingly, not a new model.

**Severity**: Major
**Evidence Anchor**: text: §1 ¶2 "nor do we test a full acceptance model" and §5 ¶1 "consistent with prior technology-acceptance research"
**Confidence**: 5 — this path-structure distinction and its effect-size consequences are core to the tradition I review in

### W3: Foundational literature absent and the perceived-usefulness construct attributed to secondary sources

The construct's definition is rendered as a near-paraphrase of the tradition's founding formulation but credited to a 2019 instrument paper and a 2020 commentary; the originating source, the extension frameworks that added voluntariness as a moderator, and every existing synthesis of PU–use effects in education are missing, as is anything published after 2021. An introduction that asserts "a substantial body of work" supports it with one citation. The effect is that the manuscript's account of the literature it claims to increment is flattened at the level of provenance and thin at the level of cumulative evidence, which is what makes W1 possible in the first place. Repair requires substantial reworking of §2, not additional citations sprinkled into the existing text.

**Severity**: Major
**Evidence Anchor**: text: §1 ¶1 "a substantial body of work suggests" and §2 ¶1 "the degree to which a person believes a technology will help them perform better"
**Confidence**: 5 — direct familiarity with the canonical sources and the meta-analytic record this manuscript omits

### W4: Reference list is not verifiable as presented and requires editorial checking

All six references carry DOIs under a single prefix (10.5555) with sequential suffixes running 2050001 through 2050006. That prefix is, to my knowledge, a range conventionally used for test and example identifiers rather than live publisher registration, and the sequential numbering across six ostensibly unrelated journals is not a pattern real citations produce. Several journal titles are also near-variants of established titles rather than titles I can confirm. I am reporting a verification requirement, not asserting fabrication: I cannot resolve DOIs from within the manuscript, and a de-identification or production step could in principle explain the pattern. The editor should confirm that each cited work exists and supports the assertion attached to it. If verification fails, my D2 assessment would move from warn to block under the fabricated-evidence trigger I set in Phase 1, because the domain record would then be unreliable rather than merely incomplete; on the record as given, I score the dimension on its substantive content.

**Severity**: Major
**Evidence Anchor**: text: References "https://doi.org/10.5555/2050001" and "https://doi.org/10.5555/2050006"
**Confidence**: 3 — the DOI-prefix inference is strong but unresolvable from the manuscript alone, so this is a flag for verification rather than a finding of fact

### W5: An established moderator of the PU–use relationship is named as a confound and then left unengaged

The results section identifies course requirements and assessment schedules as influences on reported engagement, which is precisely the voluntariness dimension this literature has studied as a moderator of PU–use associations. Neither the moderator literature nor the implication for interpreting a coefficient obtained in a quasi-mandatory setting appears. I am not asking the authors to measure voluntariness; I am asking them to state that their estimate comes from a context where use is partly compelled, and to cite what the field knows about how that changes the association's magnitude and meaning.

**Severity**: Minor
**Evidence Anchor**: text: §4 ¶2 "including course requirements and assessment schedules"
**Confidence**: 4 — the moderator is well established in the extension frameworks this manuscript does not cite

### W6: "Previously validated" over-reads what the adapted instrument's evidence establishes

The source instrument's own title claims development and validation, so the descriptor is defensible for the original. It is not defensible for the six-item adaptation used here, whose modifications are not documented and for which the only psychometric evidence reported is in-sample internal consistency. Reliability is not validity, and undocumented adaptation is one of the mechanisms the manuscript itself invokes when it notes that effect sizes vary "across samples and instruments." This compounds W1: comparability across estimates presupposes measurement equivalence the paper has not shown.

**Severity**: Minor
**Evidence Anchor**: text: Abstract "Perceived usefulness was measured with an adapted, previously validated instrument"
**Confidence**: 4 — standard construct-validity reasoning in this measurement literature

### W7: Single-construct design cannot separate perceived usefulness from generalised platform favourability

Because only one predictor construct was measured, and both sides of the correlation come from the same self-report instrument, part of r = .42 may reflect a general positive orientation toward the platform rather than the specific usefulness judgement the construct names. The tradition distinguishes perceived usefulness from perceived ease of use partly for this reason. The proportionate repair is a caveat in the measures or limitations section acknowledging that discriminant validity is untested here, not the addition of further constructs the paper legitimately declined to model.

**Severity**: Minor
**Evidence Anchor**: absence: §3.2 Measures and §6 Limitations — expected acknowledgement that a single-construct self-report cannot separate perceived usefulness from generalised platform favourability; checked §2, §3.2, §4, §5, §6
**Confidence**: 3 — the common-method concern is well founded, though its magnitude in this specific sample is unknowable from the reported data
