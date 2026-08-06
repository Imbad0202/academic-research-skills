contract_role: domain

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: block
trigger: "materially misrepresent, established domain evidence or a cited source, such that the stated contribution cannot stand as written without substantial correction and re-analysis of the literature"
block_class: repairable

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I read this manuscript for one thing only: whether its domain content is true to the field it cites. On several counts it is, and I want to be clear about that before I explain why I am nonetheless blocking. The causal restraint is handled to the standard the acceptance-methodology literature actually sets, including the reverse pathway stated in its own right rather than buried in a limitations list. The self-report versus behavioural-log distinction is not merely acknowledged but carried into the construct label, so the paper measures and reports "perceived use" and does not quietly upgrade it to engagement. The result itself is reported completely and, as far as I can check it, correctly: the confidence interval is consistent with the coefficient and sample size, the rank-order robustness check is reported with its value rather than asserted, and the shared-variance statement does not inflate what a coefficient of that size licenses. Papers of this kind routinely fail on exactly these points. This one does not.

The block rests on the paper's single contributory claim. The authors describe the study as "an incremental data point, comparable with prior work," and the abstract, discussion, and conclusion each assert that the association is consistent with prior technology-acceptance research. That claim carries the entire contribution — remove it and what remains is a local descriptive statistic from one campus with no stated bearing on anything. Yet the manuscript never identifies a target estimate, never states a comparison, and never says whether the result converges with or diverges from what came before. "Incremental" has a technical meaning in this field: a result that measurably tightens, corroborates, or challenges an existing estimate. As used here it functions as a disclaimer, not as a finding. The two citations attached to the consistency claim in §5 cannot support it. Costa and Wren (2019) is, by its own title, an instrument-development-and-validation study, which is not a source for an effect-size comparison. Ibarra and Poll (2021) is characterised in §2 as a study of contextual moderation of perception and use, which is likewise not a source for a comparable point estimate. Neither is reported as supplying a coefficient against which .42 could be judged.

The problem compounds when the manuscript's own literature reading is taken seriously. Section 2 reports Song (2018) as finding that association strengths varied by institution, and concludes that any single-site estimate is best read as one point in a distribution. If that is the state of the evidence, then a bare "consistent with prior research" is unfalsifiable, because a sufficiently wide distribution accommodates almost any value. The paper therefore uses Song to establish heterogeneity and then makes a point-consistency claim that heterogeneity cannot license, without reconciling the two. That is a misuse of a cited source in the service of the headline positioning, and it is what moves this from a rewriting request to a block: substantiating the claim requires the authors to go back into the literature, extract actual estimates or ranges, and state where .42 falls relative to them. That is re-analysis of the literature, not copy-editing.

Second, the construct provenance is wrong. Section 2 defines perceived usefulness as the degree to which a person believes a technology will help them perform better, which is, in substance, Davis's original definition, and attributes it to sources from 2019 and 2020. A paper that situates itself within "technology-acceptance research" and builds its measure on that literature's flagship construct cites neither Davis nor the UTAUT line, and cites nothing from the past decade of LMS engagement or learning-analytics work in which this exact association has been examined repeatedly. Six references cannot situate a study in this area. I want to be precise about what I am and am not asking. I am not asking the authors to test TAM or UTAUT; that would inflate the scope far past their declared question and past what bivariate data can support, and the decision not to test a model is defensible. What I am asking is that the decision be defended rather than assumed. If perceived usefulness is measured outside the nomological network in which it was constructed and validated, the authors owe the reader an account of what the resulting coefficient means and what is gained by the extraction. At present the construct is borrowed with its authority intact and its provenance unstated, which leaves a reader unable to check the definition against its source.

Third, a substantive interpretive omission. Both variables are self-reported by the same respondent within the same instrument at the same sitting. The acceptance literature has treated common-method variance as a first-order threat to precisely this design for decades, and the paper's own citation of Vasquez (2020) sharpens the issue rather than settling it: if self-report indexes perception rather than behaviour, then this is a correlation between two perceptual reports sharing a method. Section 5 offers reverse causation as the alternative reading and stops there. Shared method and self-presentation variance is a third reading that bears directly on how much of .42 should be believed, and it appears nowhere in the manuscript.

Two smaller matters. The instrument section reports that a six-item scale was adapted, and then offers only internal consistency as evidence of quality, for both the source instrument and the present sample. What was adapted is not stated, and dimensionality is not reported, so a reader cannot judge whether the adapted version retains the properties that made the original usable. Separately, and as a matter for the editor rather than the authors' argument: I was unable to verify any of the six cited works. All six DOIs sit under the same reserved prefix in a single sequential run, and the journal titles closely resemble established venues in this field without matching them. I state this as a verification flag, not as a finding of fabrication, but it should be resolved before any editorial decision, because if the citations do not resolve, nothing above about literature repair is achievable.

To be explicit about the score: none of the individual findings below is on its own fatal, and the data and their reporting appear sound, so this is a repairable block, not a rejection. It is a block rather than a warning because the joint effect of the unsubstantiated comparison and the missing construct provenance is that the paper's stated contribution cannot stand as written. What would clear it: name the prior estimates the study is being compared against, state whether .42 converges or diverges from them and by how much, cite the canonical acceptance sources whose construct is being used, defend measuring that construct outside its model, and address common-method variance in the interpretation of the coefficient.

### S1: Causal restraint matches the field's methodological caution literature
The manuscript states the reverse-causation pathway as an equally consistent reading of the same data and attributes it to the cited source that makes that argument, rather than confining the point to a limitations disclaimer. This is how the caution actually reads in the acceptance-methodology literature, and the correlational language is maintained consistently across abstract, results, discussion, and conclusion.
**Evidence Anchor**: `text: §5 "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data, as Delgado (2020) notes"`
**Confidence**: 5 — three decades reviewing acceptance work in education; this boundary is the one I check first.

### S2: Correct handling of the self-report versus behavioural-log distinction
Rather than citing the self-report/log divergence and then proceeding as if it did not apply, the authors carry it into the construct label and restrict their claim to perceived use. The limitations section repeats the constraint without softening it. This is the correct move given the cited measurement evidence, and it is more often gotten wrong than right in LMS engagement papers.
**Evidence Anchor**: `text: §2 "treat our self-report measure as an indicator of perceived use rather than a behavioral count"`
**Confidence**: 5 — sustained work on LMS engagement measurement.

### S3: Complete and internally accurate reporting of the association
The coefficient is reported with its interval, p value, and sample size together; the rank-order robustness check is given as a value rather than asserted to be adequate; and the shared-variance statement is proportionate to a coefficient of this magnitude, with competing influences named. The interval is consistent with the coefficient and n as reported.
**Evidence Anchor**: `text: §4 "r = .42, 95% CI [.30, .52], p < .001, n = 214"`
**Confidence**: 4 — I checked the interval against the coefficient and n; detailed statistical adjudication belongs to the methodology seat.

### W1: The contributory claim of consistency with prior work is unsubstantiated and rests on citations that cannot support it
The paper's only claim to contribution is that its estimate is an incremental data point comparable with prior work. No target estimate, no stated comparison, and no convergence-or-divergence statement is supplied anywhere in the manuscript. The two sources attached to the consistency claim are, on the manuscript's own descriptions, an instrument-validation study and a study of contextual moderation; neither is reported as providing a comparable coefficient. Compounding this, §2 invokes multi-campus heterogeneity to argue that any single-site estimate is one point in a distribution, which makes a bare consistency claim unfalsifiable rather than supported. Repair requires returning to the literature for actual estimates and stating where .42 sits relative to them.
**Severity**: Major
**Evidence Anchor**: `text: §5 "consistent with prior technology-acceptance research (Costa & Wren, 2019; Ibarra & Poll, 2021)"`
**Confidence**: 5 — I have written on replication and comparison norms in educational technology; this is the norm the claim fails.

### W2: Perceived usefulness is defined with its canonical definition but attributed to recent secondary sources, with the foundational acceptance literature absent
The construct definition given in §2 is in substance the original TAM formulation, cited to 2019 and 2020 sources. Neither Davis nor the UTAUT line appears in a manuscript that positions itself inside technology-acceptance research, and no LMS engagement or learning-analytics work from the past decade is cited. A reader cannot check the definition against its source, and the construct's evidentiary standing is imported without its provenance. The related interpretive gap is that the construct is measured outside the nomological network in which it was validated with no account of what the resulting coefficient then means. I am not asking for a model test, which would exceed the declared question and the data; I am asking that the extraction be defended and the canon it borrows from be cited.
**Severity**: Major
**Evidence Anchor**: `text: §2 "the degree to which a person believes a technology will help them perform better"`
**Confidence**: 5 — direct expertise in the migration of acceptance research from information systems into education.

### W3: Common-method variance is not addressed anywhere, though both variables share a single self-report instrument
Both constructs were reported by the same respondent in the same questionnaire at the same time. Shared method and self-presentation variance is a long-standing first-order threat to this design in the acceptance literature, and the manuscript's own citation of self-report/log divergence makes the concern more acute, not less. Section 5 offers only reverse causation as an alternative reading of the coefficient. How much of the reported association is attributable to method rather than substance is therefore left unexamined, which bears directly on the interpretation of the headline number.
**Severity**: Major
**Evidence Anchor**: `absence: Discussion §5 and Limitations §6 — expected acknowledgement of common-method variance arising from single-instrument self-report of both constructs; checked §2 literature review, §3.2 measures, §3.4 analysis, §5 discussion, §6 limitations, reference list`
**Confidence**: 4 — standard in this literature; I cannot quantify the inflation from the reported material.

### W4: Instrument adaptation is unspecified and supported only by internal consistency
The scale is described as adapted from a prior instrument, but what was changed is not stated, and the only psychometric evidence offered for either the source or the present version is internal consistency. Dimensionality is not reported. Validity is a property of an instrument in a given use, not a label that transfers with an adaptation, so a reader cannot judge whether the adapted six items retain the properties that justified using the original.
**Severity**: Minor
**Evidence Anchor**: `text: §3.2 "a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"`
**Confidence**: 4 — routine instrument-adaptation reporting expectations in this field.

### W5: None of the six cited works could be verified from the identifiers supplied
All six DOIs sit under a single reserved prefix in a sequential run, and the journal titles closely resemble established venues in the field without matching any of them. I raise this as a verification flag for the editor rather than as a finding of fabrication, since I cannot establish invalidity from the manuscript alone. It matters because every literature repair requested above presupposes that these sources exist and say what the manuscript reports them as saying; if they do not resolve, the domain grounding of the paper is not repairable by revision.
**Severity**: Major
**Evidence Anchor**: `text: References, "https://doi.org/10.5555/2050001" and "https://doi.org/10.5555/2050006"`
**Confidence**: 3 — the identifier pattern is unusual, but verification requires database access I do not have here.
