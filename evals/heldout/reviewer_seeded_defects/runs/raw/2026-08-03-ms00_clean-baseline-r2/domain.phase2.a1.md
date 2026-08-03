contract_role: domain

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: block
block_class: repairable
trigger: "a cited source represented as supporting a conclusion it does not support"

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I read this as a technology-acceptance researcher. Let me state the shape of my assessment before the details, because it matters for what revision I am asking for.

The paper's central virtue is restraint. It runs a bivariate correlation, reports it with an interval, refuses causal language, names the reverse pathway, and reframes its outcome as *perceived* use rather than behavioural use. Those are exactly the moves an acceptance paper of this design should make, and I want to be explicit that I am **not** asking the authors to add constructs, mediators, or a structural model. A 214-response single-item-outcome dataset cannot carry a full acceptance model, and demanding one would destroy the paper's best quality. Every repair I ask for below is a citation, framing, or interpretation repair — no new data, no new constructs.

That said, the manuscript has a domain-accuracy problem that I do not think is cosmetic, and it clusters around one sentence that appears three times: the claim that r = .42 is "consistent with prior technology-acceptance research."

First, the theoretical provenance. Perceived usefulness is not a generic phrase; it is a specific construct with a specific primary definition, an extension lineage, and a continuance branch. §2 reproduces something very close to that primary definition ("the degree to which a person believes a technology will help them perform better") and attributes it, along with the claim that the field has "long proposed" it, to two sources dated 2019 and 2020. The reference list contains no primary theoretical source at all. The practical consequence is not a missing citation courtesy — it is that a reader cannot check whether the six adapted items measure the field's construct or a local variant, because the only available definition of the construct in this manuscript is downstream of an instrument paper whose own content is never described beyond "reported strong internal consistency."

Second, and more consequentially, the comparability claim has no anchor. The manuscript's stated contribution is that it supplies "an incremental data point, comparable with prior work," and §2 borrows Song (2018) to say that a single-site estimate should be read as "one point in a distribution." I accept that framing — but a distribution has to be named for the framing to do any work. Nowhere does the manuscript report a single prior effect size, pooled or otherwise, from the education-sector acceptance literature. The reader is told .42 is consistent with prior work and given no number to compare it to. This is where I move from "thin" to a domain-accuracy failure: in §5, Costa & Wren (2019) and Ibarra & Poll (2021) are cited as the warrant for that quantitative comparability judgement, yet the manuscript itself characterises the first as an instrument-development study and the second as a paper emphasising contextual moderators. Neither is anywhere described as reporting a PU–use correlation magnitude. Two sources are therefore standing behind a numerical conclusion that the manuscript gives no evidence they contain. Pooled estimates for this relationship in educational settings do exist; the fix is to name one, with its interval, and state plainly where .42 sits relative to it — inside, at the low tail, wherever the truth lands. If it turns out to sit below the pooled estimate, that is a more interesting paper, not a worse one.

Third, an estimand issue that compounds the second. The manuscript models perceived usefulness directly against use and explicitly declines to "test a full acceptance model." That design choice is legitimate and I am not contesting it. But the parent theory specifies behavioural intention as the mediator between usefulness and use, and the bulk of the literature the authors are implicitly comparing themselves to estimates usefulness against *intention*, not against self-reported frequency. Those two quantities do not share a magnitude range. A .42 that is unremarkable against PU–intention estimates may be notably high or low against PU–behavioural-use estimates. The authors do not need to measure intention; they need one paragraph acknowledging that the intention step is bypassed and that the comparison set must therefore be restricted to studies estimating the same PU-to-use link.

Fourth, the boundary condition I care most about, and here I want to be careful to press the right question rather than the loudest one. LMS engagement in contemporary undergraduate programmes is substantially compelled — submission deadlines, attendance, announcements. Voluntariness is a well-established moderator in this literature, and acceptance constructs attenuate as predictors when use is not discretionary. §4 gestures at this in a trailing clause and then proceeds; §6, which otherwise lists four limitations conscientiously, does not mention compulsion at all. The question the authors must answer explicitly is whether compulsion *bounds* their finding or *invalidates the frame*. My own read is that it bounds rather than invalidates, precisely because the paper claims only a descriptive association and disclaims theory testing — but that argument has to be made in the manuscript, not inferred by the reviewer, and it belongs in §6 alongside the other four constraints. Note also the interaction with limitation four: if the sample over-represents students who engage with institutional channels, and if LMS use is largely compelled, the observed variance in the outcome may be compressed at the top, which bears directly on the magnitude being compared.

None of this is fatal. The dataset is fine, the analysis is internally coherent, and the empirical statement about these 214 students survives intact. What does not survive intact in the current draft is the interpretive claim that carries the paper's contribution. That claim needs primary-source grounding, a named comparison distribution, an estimand caveat, and an honest voluntariness limitation. That is substantive rewriting of §2, §5, and §6 — which is why I score domain accuracy as a repairable block rather than a warn.

### S1: Reverse-causation caution represented faithfully and consequentially

The manuscript does not merely cite Delgado (2020) as a decoration; it states the reverse pathway in specific terms and grants it equal standing with the forward pathway. In a literature where cross-sectional acceptance correlations are routinely narrated in causal-adjacent language, this is a correct and unusually disciplined use of a methodological caution from the cited source.

- **Evidence Anchor**: `text: §5 Discussion "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"`
- **Confidence**: 5 — I have reviewed and synthesised many cross-sectional acceptance studies and can judge how rarely this is done properly.

### S2: Self-report/log divergence caution applied to the construct, not just acknowledged

Vasquez (2020) is characterised accurately and then acted upon: the outcome is redefined as an indicator of perceived use, and that redefinition is carried consistently into §3.2, §4, and §6. This is the correct domain move, and the paper is more defensible for having made it rather than merely conceding self-report as a limitation in passing.

- **Evidence Anchor**: `text: §2 Literature Review "studies relying on self-report capture perceived rather than actual engagement"`
- **Confidence**: 4 — familiar with the self-report/trace-data literature in educational technology, though I have not verified the cited source's contents.

### S3: Reported quantities are mutually coherent

The interval and the coefficient are consistent with each other at the stated sample size, the Spearman check sits where a comparable rank estimate should sit, and the shared-variance remark in §4 is described qualitatively rather than inflated. I checked the numbers against each other and found no internal contradiction between abstract, §3.4, §4, and §7.

- **Evidence Anchor**: `text: §4 Results "r = .42, 95% CI [.30, .52], p < .001, n = 214"`
- **Confidence**: 4 — arithmetic consistency is checkable, though statistical detail is not my primary strength.

### W1: Construct genealogy absent; primary definition attributed to secondary sources

§2 presents the field's canonical definition of perceived usefulness and attributes both the definition and the claim that the field has "long proposed" it to sources published in 2019 and 2020. The reference list contains no primary theoretical source for the construct, no extension formulation, and nothing from the continuance branch. Because the construct's only definition in this manuscript is downstream of an instrument paper whose contents are never described, a reader cannot verify that the six adapted items operationalise the field's construct rather than a local variant. Repair is bounded: cite the primary definition, re-attribute the "long proposed" claim to its actual origin, and state which formulation the six items descend from.

- **Severity**: Major
- **Evidence Anchor**: `text: §2 Literature Review "Research on technology acceptance has long proposed" and "the degree to which a person believes a technology will help them perform better"`
- **Confidence**: 5 — this is the specific lineage I work in and publish on.

### W2: The incremental claim has no named distribution to be incremental against

The paper's contribution is framed as one point in a distribution of prior estimates, yet no prior estimate appears anywhere in the manuscript — not a pooled coefficient, not an interval, not a range. Education-sector syntheses of this relationship exist and can supply the anchor. Without it, "comparable with prior work" is unfalsifiable and the incremental framing has nothing to rest on, which matters because that framing *is* the stated contribution. The fix is a sentence in §2 and a sentence in §5 naming a pooled estimate with its interval and locating .42 relative to it.

- **Severity**: Major
- **Evidence Anchor**: `absence: §2 and §5 comparability claim — expected a named pooled PU-use estimate from education-sector acceptance meta-analyses with its interval, and an explicit statement of where r = .42 falls relative to that interval; checked Abstract, §1 Introduction, §2 Literature Review, §5 Discussion, §7 Conclusion, and the six-entry reference list`
- **Confidence**: 5 — I have conducted meta-analytic syntheses of acceptance research in educational settings.

### W3: Estimand mismatch between the reported association and the comparison literature

The modelled path runs from perceived usefulness directly to self-reported use, bypassing behavioural intention, which the parent theory specifies as the mediator. The design choice is acceptable and I am not asking for an intention measure. The problem is that the comparison claim does not distinguish PU-to-intention estimates from PU-to-use estimates, and these do not share a magnitude range; conflating them makes "consistent with prior technology-acceptance research" imprecise regardless of which anchor W2's repair supplies. The manuscript should state why the intention step is bypassed and restrict its comparison set to studies estimating the same link.

- **Severity**: Major
- **Evidence Anchor**: `text: §1 Introduction "nor do we test a full acceptance model" and §5 Discussion "consistent with prior technology-acceptance research"`
- **Confidence**: 5 — mandatory-versus-voluntary and estimand-specification issues are my direct research area.

### W4: Mandatory-use boundary condition conceded in a trailing clause and omitted from Limitations

Undergraduate LMS engagement is largely compelled by submission, attendance, and announcement functions. Voluntariness is an established moderator of acceptance constructs' predictive strength, and in compelled-use settings those constructs weaken as predictors. §4 acknowledges assessment-driven use in a single trailing clause and then proceeds as if the frame were unaffected; §6 lists four limitations and does not include compulsion among them. The authors must take an explicit position on whether compulsion bounds the finding or undermines the theoretical frame — those imply different revisions — and, if the former, say so in §6 with the interaction against the voluntary-response bias already noted there.

- **Severity**: Major
- **Evidence Anchor**: `text: §4 Results "including course requirements and assessment schedules"`
- **Confidence**: 5 — mandatory-use boundary conditions are the specific problem I study.

### W5: Instrument provenance and validation context not reconciled with present use

The source instrument is titled as an instrument for perceived usefulness and *continued* use of learning platforms, whereas the present outcome is typical-weekly access frequency in a sample spanning all four year levels — a population mixing early-stage acceptance with established continuance. Initial acceptance and continuance have different determinant structures, and the manuscript does not say which it takes itself to be measuring. Relatedly, the abstract describes the measure as "previously validated" while §3.2 describes it as adapted; adaptation does not automatically inherit the source's validation evidence, and only internal consistency is reported in-sample. A short paragraph reconciling the instrument's validation context with the present operationalisation would resolve both points.

- **Severity**: Minor
- **Evidence Anchor**: `text: §3.2 Measures "adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency" and References "Perceived usefulness and continued use of learning platforms: Instrument development and validation"`
- **Confidence**: 3 — the acceptance/continuance distinction is well within my expertise, but I cannot inspect the six items or the source instrument's validation evidence.
