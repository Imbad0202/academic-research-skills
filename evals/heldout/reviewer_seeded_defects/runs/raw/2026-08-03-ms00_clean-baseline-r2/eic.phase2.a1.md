contract_role: eic

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: warn
trigger: "formatting departures from venue convention"

### D6: venue_fit_and_contribution
score: block
block_class: repairable
trigger: "the stated novelty is not supported by the work actually reported"

## Review Body

This is a competently written, unusually well-calibrated short manuscript that does not yet make a publishable claim in the form submitted. I want to separate those two judgements clearly, because they pull in opposite directions and the synthesis needs both.

On craft and calibration, this submission sits above the median of what crosses my desk at this tier. The section architecture is conventional and complete, the abstract previews the study that the body actually reports, the hedging is proportionate rather than defensive, and the statistical reporting includes a confidence interval, an explicit sensitivity statement, a non-parametric robustness check, and a limitations section that names the right four constraints in the right order. Authors at this scale routinely report a bare coefficient and a p value; these authors did not. That deserves to survive into the panel synthesis intact, and I will say so plainly: the calibration is not the problem.

The problem is that correct calibration is being asked to function as a contribution. The manuscript's only stated contribution is comparability — "an incremental data point, comparable with prior work," positioned as "one point in a distribution rather than as a fixed value." Delivering that claim requires two things the manuscript does not supply. First, at least one prior coefficient to compare against: no prior effect size appears anywhere in the paper, so the reader is told the finding is consistent with prior work and given nothing against which to check consistency. Second, comparators a reader can locate: all six references carry the DOI prefix 10.5555, which is Crossref's reserved test/demonstration range rather than a live registrant, and none of the six journal titles corresponds to an indexed periodical I can find. The consequence for my dimension is specific and not a matter of taste. If the contribution is comparability, and neither the comparison nor the comparators can be established, then the stated contribution is not delivered by the manuscript as submitted. That is why D6 blocks rather than warns.

I have scored the block repairable rather than fatal, and I want to be explicit about why. The topic is squarely within a learning-technology readership's remit. The data collection appears real and the reporting of it is honest. The defects are informational rather than architectural: supply verifiable sources, state the prior coefficients, report the denominator, and state one thing an institution can now do differently. All of that is within the authors' control. This is a major revision, not a rejection.

On format, my recommendation is unambiguous: this is a Research Note, not an Original Research article. At roughly 1,900 words carrying a single bivariate coefficient with no tables or figures, the submission is well matched to the short empirical note format and poorly matched to the full-article format it currently occupies. Reclassification is not a demotion here — it is the correct container for a modest, cleanly reported single-site estimate, and it would relieve the manuscript of an expectation it cannot meet.

Two disclosures about my own seat. First, I am the editorial-fit and reporting-standards reader, not the methodologist. Whether a single ordinal self-report item and an adapted instrument of unverifiable provenance can support even the bounded claim made here is D1's call, and the methodology seat may reasonably conclude that the measurement problem caps the maximum defensible claim rather than being fixable in revision. If that is their reading, it should govern; I have not scored around it. Second, my instinct genuinely does run toward "fixable in revision," and I have tried to check that instinct against the one finding where it does not apply: I cannot verify the instrument's validation, and no amount of revision to the prose changes that — only a verifiable source does.

### S1: Statistical reporting is more complete than the tier norm

The analysis section reports a sensitivity floor rather than a post hoc power figure, and the results section pairs the coefficient with a confidence interval, an exact-threshold p value, the sample size, and a Spearman check that confirms the finding does not rest on the parametric assumption. For a submission of this length this is close to exemplary reporting practice, and it materially reduces the editorial work needed to evaluate the estimate.

**Evidence Anchor**: text: §3.4 "the study had greater than .80 power to detect a correlation of r >= .19 at alpha = .05"

### S2: Claim strength does not drift across sections

The abstract, results, discussion, limitations, and conclusion all describe the same moderate correlational finding at the same strength. The single practical implication offered is disclaimed in the sentence that offers it. Claim inflation between results and conclusion is the most common failure I triage in this class of submission, and it is absent here.

**Evidence Anchor**: text: §5 "this implication is suggested by, not proven by, the present correlation"

### S3: Abstract and title accurately preview the study

The title names the design, the population, and the two constructs; the abstract states the sample, the measures, the coefficient, the design limitation, and the scope of generalisation. A reader deciding whether to read further is not misled about what the study is, which is the abstract's editorial job.

**Evidence Anchor**: text: Abstract "The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates."

### W1: Every cited source is editorially unverifiable, including the study's measurement warrant

All six references share the DOI prefix 10.5555, which is a reserved test and demonstration range rather than an assigned registrant prefix, and none of the six journal titles matches an indexed periodical. This is not a citation-formatting defect. It means the editorial office cannot verify the source on which the study's central methodological warrant rests: the claim that perceived usefulness was measured with an instrument "previously validated" by Costa and Wren (2019) whose original reported strong internal consistency. It also means the abstract's and discussion's claims of consistency with prior technology-acceptance research cannot be checked, and the manuscript's own three methodological cautions (Delgado on cross-sectional inference, Vasquez on self-report divergence, Song on between-site variation) are attributed to sources a reader cannot consult. Uncorrected, no responsible journal can send this to production, and it alone justifies the block on D6. Whether the underlying works exist is a factual determination for the domain seat; my finding is narrower and does not depend on that determination — as submitted, nothing in the evidence base can be verified by an editor or a reader.

**Severity**: Critical
**Evidence Anchor**: text: References and §3.2 "https://doi.org/10.5555/2050001" and "a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"
**Confidence**: 5 — DOI and source verification is routine editorial-office screening, and the reserved status of the 10.5555 range is a matter of public record.

### W2: The contribution statement is a description of scale, not a claim of use

"An incremental data point" tells me how big the paper is, not what it gives anyone. The manuscript positions itself as one point in a distribution but never reports the distribution: no prior coefficient from Song (2018), Ibarra and Poll (2021), or Costa and Wren (2019) appears anywhere, so a reader cannot tell whether r = .42 is typical, high, or low against the literature the paper invokes. The one practical implication — that onboarding emphasising concrete usefulness may merit attention — is offered and withdrawn in the same sentence, and would in any case follow from the prior literature without this study. Revision must state, in one sentence, what a reader or an institution can now do that they could not do before this paper, and that sentence has to survive contact with a moderate cross-sectional correlation. This is a rewriting and repositioning requirement, not new data, and the empirical finding itself is unaffected.

**Severity**: Major
**Evidence Anchor**: text: §2 "It is intended as an incremental data point, comparable with prior work, rather than as a test of a theoretical model."
**Confidence**: 5 — contribution-statement screening against delivered content is the core function of this seat.

### W3: No sampling frame or response rate, so the manuscript's own selection caveat cannot be sized

Section 3.1 states that all enrolled undergraduates were eligible and that 233 responses were received, but never gives the size of that eligible population and never reports a response rate. Survey reporting conventions treat the denominator as required, and here it is load-bearing: the limitations section concedes that "students who engage more with institutional channels may be overrepresented," yet without a response rate neither an editor nor a reader can tell whether that overrepresentation is a marginal caveat or the dominant feature of the sample. The composition detail that is given — that the sample "spanned all four year levels" — is unquantified, so representativeness cannot be assessed on that axis either. Supplying the frame size, the response rate, and a year-level distribution requires information the authors already hold, but it is new reported content rather than a copy-edit.

**Severity**: Major
**Evidence Anchor**: absence: §3.1 Design and participants — expected the size of the eligible undergraduate population and the resulting response rate; checked §3.1, §3.3, §3.4, §6 Limitations, and the Abstract
**Confidence**: 5 — screening submissions against survey reporting requirements is a standing part of this role.

### W4: Quantities are described verbally where they should be stated

The results section says the shared variance was "modest" rather than reporting r² = .18, and says scatterplot inspection showed an approximately linear association without showing the plot or reporting the descriptive detail that would let a reader accept the claim. The manuscript contains no table or figure of any kind, so the descriptive statistics, the frequency distribution of the ordinal use item, and the bivariate pattern all exist only as prose assertions. For a note-length paper the fix is small — one compact table and the numeric r² — but as submitted the reader is asked to take characterisations where numbers were available.

**Severity**: Minor
**Evidence Anchor**: text: §4 "The proportion of variance shared by the two measures was accordingly modest"
**Confidence**: 4 — presentation judgement grounded in venue convention rather than a hard reporting rule.

### W5: The adapted instrument is neither reproduced nor its adaptation documented

The scale is described as "adapted" from a source instrument, but the six item stems are not reproduced, the nature and extent of the adaptation are not stated, and there is no appendix or supplementary-materials pointer. A reader therefore cannot see what "perceived usefulness" meant operationally in this sample, and the reported α = .88 attaches to items nobody outside the author team can inspect. On its own this is a reproducibility and clarity gap that an appendix closes, which is why I band it Minor. I note without inflating the band that it interacts badly with W1: with the source unverifiable, the item text is the only remaining route to knowing what was measured.

**Severity**: Minor
**Evidence Anchor**: absence: §3.2 Measures — expected the six perceived-usefulness item stems and a statement of how the adapted wording differs from the source instrument; checked §3.2, §3.4, §7, the reference list, and any appendix or supplementary-materials statement
**Confidence**: 4 — standard reporting expectation for adapted survey instruments.

### W6: A sixth source appears only at the point where the practical implication is made

The literature review builds its scaffolding from five sources and never introduces Whitfield (2019), which then surfaces in the discussion to support the onboarding implication. The effect is that the paper's one forward-looking recommendation leans on a citation the reader meets for the first time in the sentence that uses it. Either introduce it in section 2 alongside the other practitioner-facing material or drop the appeal to it and let the implication stand on the correlation, with the hedge already present.

**Severity**: Minor
**Evidence Anchor**: text: §5 "a possibility also raised in practitioner accounts of digital-environment onboarding (Whitfield, 2019)"
**Confidence**: 4 — structural consistency of the citation apparatus is directly observable.

For revision, my editorial requirements are ordered: replace the reference list with sources a reader can locate and resolve, including a verifiable provenance for the perceived-usefulness instrument; report the prior coefficients this estimate is meant to sit alongside; supply the sampling frame, response rate, and year-level distribution; state in one sentence what changes for a reader or an institution because of this paper; and resubmit as a Research Note with one table. If the first and fourth of those are met, this becomes a clean, honest note that the format exists to carry. If the first cannot be met, no amount of work on the others will make the manuscript publishable, and the decision should be revisited on that basis alone.
