contract_role: domain

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: block
trigger: "a central claim attributed to cited literature that does not support it"
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

I read this manuscript as the domain reviewer, asking one question throughout: does this paper know what the technology-acceptance literature already knows, and does it describe that literature as it actually reads?

My answer is mixed in an unusual way. The paper's *interpretive* domain judgement is unusually good. It gets the direction of the reverse-causation problem right, it correctly treats self-report as an indicator of perceived rather than behavioural engagement, it uses "moderate" for r = .42 in a way consistent with conventional benchmarks, and it declines to inflate. I want to be explicit that I am not penalising this paper for being small and honest; a well-hedged single-site estimate is a legitimate scientific object. I also want to be explicit that I am not asking for a structural model or a mediation analysis — a single-item ordinal outcome at n = 214 cannot carry one, and demanding it would be a worse recommendation than anything the paper currently does.

What fails is the paper's relationship to the prior literature it claims to join. The manuscript stakes its entire contribution on comparability — "an incremental data point, comparable with prior work" (§2), "consistent with prior technology-acceptance research" (§5), "consistent with prior work" (§7) — and then never states a single prior estimate against which comparability could be judged. Section 2 goes so far as to raise the relevant heterogeneity ("effect sizes vary across samples and instruments") and then declines to report any of it. This is not a hedging quibble. The perceived-usefulness/use association is one of the most heavily meta-analysed relationships in educational technology; pooled estimates exist and are exactly the benchmark this paper's own framing calls for. As written, "consistent with" is unfalsifiable, and the reader cannot tell whether r = .42 sits at the centre of the distribution, in a tail, or outside the reported range. This is the single highest-leverage revision available, and it requires no new data.

Compounding this, the foundational lineage is absent. Six references for a technology-acceptance paper is not a lean review; it is an absent one. Davis and the UTAUT line are uncited, and — more consequentially for a paper defining perceived usefulness in near-canonical wording — the definition is attributed to two recent secondary sources rather than to its origin.

I must also record a verifiability problem I could not resolve within this review. All six references carry DOIs under the `10.5555` prefix with consecutive suffixes `2050001`–`2050006`, across six ostensibly distinct journals published by distinct publishers. That prefix is the reserved test/example prefix, and consecutive suffixes across unrelated publishers is not how DOI suffixes are assigned. Two of the six journal titles are near-misses of real journals. I did not have live retrieval available in this pass and therefore resolved none of the six; I am reporting structural evidence, not a confirmed finding. The editor should attempt resolution before any decision. If the sources do not resolve, the problem escalates beyond what revision can repair, and my block would no longer be repairable.

Two further domain issues are substantive but ordinary. The paper never defends access frequency as a construct worth explaining, at a point in the field's development where the move toward depth and quality of engagement is precisely a response to frequency conflating compliance-driven access with meaningful use. The manuscript brushes against this in §4 and then walks away from it. And the instrument adaptation is undisclosed, which matters here more than usual: comparability across studies in this literature depends on instrument equivalence, and the paper offers reliability evidence where its abstract makes a validity claim.

### S1: Reverse-causation problem stated correctly and attributed to the right caution
The discussion does not merely disclaim causality; it names the specific alternative pathway and treats it as equally consistent with the data. This is the correct domain-standard treatment of a cross-sectional acceptance correlation, and it is rarer in submitted work than it should be.
- **Evidence Anchor**: text: §5 "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"

### S2: Self-report/behavioural-log distinction handled with the right interpretive consequence
The paper invokes the measurement-divergence literature at the correct point and then carries the consequence through, redefining what its own measure captures rather than citing the caution and ignoring it. The limitations section repeats the point without contradicting it.
- **Evidence Anchor**: text: §2 "studies relying on self-report capture perceived rather than actual engagement"

### S3: Single-site estimate framed as a draw from a distribution
The paper correctly reads multi-campus heterogeneity as implying that any one site's coefficient is a point in a distribution. This is the right conceptual frame for a replication-class contribution, and it is the frame that makes W1 fixable rather than fatal — the authors already understand what they need to do.
- **Evidence Anchor**: text: §2 "any single-site estimate is best read as one point in a distribution rather than as a fixed value"

### W1: The comparability claim has no comparator, and the relevant meta-analytic literature is uncited
The paper's stated contribution is comparability with prior work, asserted three times, and no prior effect size appears anywhere in the manuscript. The two sources cited in support of "consistent with prior technology-acceptance research" (§5) are, on the paper's own account in §2, part of a body whose effect sizes vary — so they cannot establish consistency without their values being stated. Existing pooled estimates of exactly this association are available and uncited. Until a benchmark is stated, the contribution reduces to "we ran a correlation," and the reader has no way to falsify the consistency claim. The repair is bibliographic, not empirical: report the pooled estimate and its range, and locate r = .42 [.30, .52] within it. If the confidence interval overlaps the pooled estimate, say so; if it does not, that is a more interesting paper than the one currently submitted.
- **Severity**: Critical
- **Evidence Anchor**: text: §2 and §5 "It is intended as an incremental data point, comparable with prior work" and "consistent with prior technology-acceptance research"
- **Confidence**: 5 — I have published synthesis work on this exact association and know the pooled estimates the paper would need to cite.

### W2: The reference list carries structural markers of non-resolvable identifiers
Every DOI sits under the reserved `10.5555` test prefix with consecutive suffixes `2050001` through `2050006`, spanning six journals that would have six different publisher prefixes and independently assigned suffixes. "British Journal of Educational Technology Studies" and "Computers & Education Review" are near-misses of real journals rather than titles I recognise. I attempted no live resolution in this pass and so report this as an unresolved verifiability flag rather than a confirmed fabrication; what I can state from domain knowledge is that the identifier pattern is not one a genuine six-source list produces. This bears directly on domain accuracy because if the sources cannot be verified, then every characterisation of prior work in §2 — including the Delgado, Ibarra and Poll, Song, and Vasquez cautions I credited above as strengths — becomes unverifiable, and the paper has no established literature base at all. The editor should resolve all six before deciding; non-resolution would make this disqualifying rather than revisable.
- **Severity**: Critical
- **Evidence Anchor**: text: References "https://doi.org/10.5555/2050001" and "https://doi.org/10.5555/2050006"
- **Confidence**: 4 — confident in the DOI-assignment reasoning and journal-title recognition; not 5 because I could not attempt resolution.

### W3: Canonical construct definition attributed to secondary sources; the foundational lineage is absent
The definition of perceived usefulness given in §2 is a light paraphrase of the field's founding formulation, and it is cited to two sources from 2019 and 2020. Neither Davis nor the UTAUT line appears anywhere, despite "technology acceptance" being a keyword and the paper describing itself as positioned within that literature. For a domain reviewer this reads as a provenance error rather than a stylistic choice: the paper is using the field's vocabulary while crediting it to the wrong place, which also deprives the reader of the theoretical scaffolding needed to judge what a "test of a theoretical model" (§2) would have involved. The repair is straightforward and should be done alongside W1.
- **Severity**: Major
- **Evidence Anchor**: text: §2 "perceived usefulness — the degree to which a person believes a technology will help them perform better"
- **Confidence**: 5 — the Davis-to-UTAUT lineage and its canonical wording are directly within my area.

### W4: Access frequency is never defended as the construct worth explaining
The outcome is how often a student opens the LMS. The paper treats this as self-evidently the thing to explain and never engages the field's move away from frequency toward depth and quality of engagement — a move driven precisely by frequency conflating compliance-driven access (a syllabus requires a weekly quiz) with meaningful use. §4 comes within one sentence of the problem, noting "course requirements and assessment schedules" as unmodelled influences, and then treats that as a variance-explained observation rather than a construct-validity one. The limitations section addresses the *mode* of measurement (self-report versus logs) but never the *construct* (frequency versus depth), so a reader could finish the paper believing log data would have solved the problem. It would not; it would measure the same construct more accurately. This requires rewriting the framing and limitations, not new data.
- **Severity**: Major
- **Evidence Anchor**: absence: Sections 3.2, 5, and 6 — expected a defense of access frequency as an engagement construct distinct from depth of use; checked Measures, Results, Discussion, Limitations
- **Confidence**: 4 — well within my synthesis area, though reasonable reviewers differ on how much a deliberately descriptive paper owes here.

### W5: Instrument adaptation and materials are undisclosed, so the comparability claim cannot be checked
The abstract advertises an "adapted, previously validated instrument." What was validated is the source instrument; what was administered is a six-item adaptation whose wording never appears and whose only reported psychometric evidence here is Cronbach's α = .88 — internal consistency, which is reliability, not validity. For most papers this would be a minor reporting gap. For this paper it is material, because instrument equivalence is the precondition for the comparability on which the contribution rests: a reader cannot judge whether r = .42 is comparable with a pooled estimate without knowing whether the same construct was measured the same way. There is also no data-, materials-, or code-availability statement anywhere, which for a paper whose stated value is comparability undercuts the contribution claim directly.
- **Severity**: Major
- **Evidence Anchor**: absence: Section 3.2 and end matter — expected the adapted six-item wording plus a data-, materials-, or code-availability statement; checked Measures, Procedure, Analysis, Discussion, and reference list
- **Confidence**: 5 — instrument-comparability requirements in acceptance synthesis are the core of my published work.

### W6: The onboarding implication rests on a practitioner account with no intervention evidence engaged
§5 moves from a cross-sectional correlation to a design recommendation about onboarding, supported by a source in a practice-oriented outlet. The paper hedges this properly on two fronts — it labels the source as a practitioner account and says the implication is "suggested by, not proven by" the correlation — which is why this is Minor rather than Major. The remaining problem is domain-specific: the acceptance literature contains actual intervention and quasi-experimental work on whether raising perceived usefulness changes use, and none of it is engaged. Invoking a practitioner account where trial evidence exists understates what is known, in the one place where the paper reaches toward practice.
- **Severity**: Minor
- **Evidence Anchor**: text: §5 "a possibility also raised in practitioner accounts of digital-environment onboarding"
- **Confidence**: 4 — confident the intervention literature exists and is relevant; less certain how much of it maps cleanly onto LMS onboarding specifically.
