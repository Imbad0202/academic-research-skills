## Scoring Plan Dissent

*(omitted — no dimension requires dissent)*

Wait — that placeholder is not permitted. Correcting below.

contract_role: perspective

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: warn
trigger: "implications stated somewhat more broadly than the design supports yet hedged or bounded elsewhere"

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I read this manuscript as someone who would have to act on it: I run the LMS event-log pipeline into an institutional data warehouse and advise on digital onboarding. That is the adjacent field this paper reaches into when §5 raises onboarding as a target for "institutional attention," so my dimension is engaged not by the correlation itself but by the bridge the paper builds from a two-variable self-report association to institutional practice.

The good news first, and it is real: this is a disciplined paper about its own limits. Correlational language holds throughout, the reverse causal pathway is named rather than buried, the confidence interval and a rank-order robustness check are both reported, and the literature review actively imports a measurement caution from an adjacent literature (self-report versus log divergence) instead of ignoring it. An outside-field reader can locate the claim's scope without reconstructing it. That is why my score is `warn` and not `block`: the characteristic failure I look for — an implication addressed to a population or causal question the study never touched, with no acknowledged limitation — is not present here. The paper does not overclaim in kind. It underspecifies in degree, and that underspecification is concentrated at exactly the two points an institutional reader needs.

The first is the outcome variable. "Accessed the LMS" is not a defined unit of observation. In a real environment that stem bundles background mobile-app sync, a push-notification tap, a deep link from an email, an instructor-forced quiz window, and a genuine study session. Two hundred and fourteen students answering a five-point frequency item are each counting a different thing, and the manuscript never tells the reader which of these it intends the respondent to count. The paper is honest that this is a perception rather than a behavioural trace, which handles the accuracy question. It does not handle the referent question, and the referent is what determines whether the outcome maps onto anything an institution can manage. This is a legibility defect specific to cross-field use: within technology-acceptance work the item is conventional enough to pass unremarked; to a reader who has to translate the result into a system-level intervention, it is unresolvable.

The second is who is in the sample. §3.1 tells me year level and nothing else. §6 correctly notes that voluntary response may overrepresent students who engage with institutional channels, but it frames this as a bias in the estimate. The sharper consequence for the practical implication is different: recruitment through the course-announcement channel structurally excludes the students least engaged with institutional channels, and those are precisely the students in the low-perceived-usefulness tail that an onboarding intervention would target. The recommendation and the missing population are the same population. That is not a caveat on precision; it is a gap between whom the paper measured and whom the paper's implication addresses, and it is invisible in the manuscript as written because no composition data — enrolment status, commuting status, first-generation status, connectivity — is reported at all.

Related, and worth separating from both: the manuscript treats the absence of log data as an inherent property of the design. It was not. The institution surveyed here owns the event logs. Whether log access was sought and declined, sought and infeasible within the ethics approval, or never sought is information an adjacent-field reader needs in order to weigh the self-report, and stating it costs one sentence. I register this as Minor because it does not touch the core claim, but I want to flag the upside honestly: if access was refused on governance grounds, saying so converts a soft limitation into a finding about institutional data access that this readership would value.

On my own blind spot, stated plainly: single-site confirmatory evidence is a legitimate genre and I have not scored this paper down for being incremental. My concerns are answerable by definition and disclosure, not by new data collection — with the partial exception of sample composition, where reporting what was already collected may or may not be possible.

### S1: Directional agnosticism is stated in the paper's own voice, not left to the reader
The reverse pathway is named explicitly at the point where a practice-facing reader would otherwise import a causal reading. This is the single most important thing a paper of this design can do for an outside-field audience, and it is done well.
**Evidence Anchor**: text: §5 "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"
**Confidence**: 5 — routine assessment of causal-language discipline in cross-sectional survey reporting.

### S2: Reporting is complete enough for reuse and pooling by adjacent fields
A confidence interval, sample size, rank-order robustness check, and an explicit sensitivity statement together let a reader outside the home field place this estimate against others rather than take it as a point fact. For anyone assembling comparable institutional estimates, this is the difference between a citable and an uncitable result.
**Evidence Anchor**: text: §3.4 "the study had greater than .80 power to detect a correlation of r >= .19"
**Confidence**: 4 — direct experience reusing published survey estimates for institutional benchmarking.

### S3: The measurement caution from an adjacent literature is imported rather than ignored
Bringing the self-report-versus-log divergence into the literature review, and then explicitly redefining the outcome as perceived use, is the kind of cross-boundary honesty that usually goes missing in this literature.
**Evidence Anchor**: text: §2 "self-reported estimates of technology use diverge, sometimes substantially, from behavioral log data"
**Confidence**: 5 — this is the exact divergence my own log pipeline is used to check.

### W1: "Accessed the LMS" is left undefined, so the outcome has no recoverable referent for an adjacent-field reader
The outcome item asks about frequency of access without specifying what constitutes an access event. Background app sync, a notification tap, an email deep link, a proctored quiz window, and a study session are all "accessing the LMS," and respondents will have counted different subsets of these. Because the manuscript never states the intended referent, an outside-field reader cannot determine what construct the coefficient describes, and cannot map it onto any system-level quantity or intervention. Redefining the outcome explicitly — either as a specified behaviour or as a self-appraisal of engagement intensity, with the claim language adjusted to match — is required before the result transfers outside the home field.
**Severity**: Major
**Evidence Anchor**: text: §3.2 "a single five-point frequency item asking how often the respondent accessed the LMS in a typical week"
**Confidence**: 5 — I administer and reconcile exactly these access definitions against event-log data.

### W2: The population the practical implication targets is the population the recruitment channel excludes, and no sample composition is reported to test this
Beyond year level, the manuscript reports nothing about who the 214 respondents are. §6 treats voluntary response as an overrepresentation problem for the estimate; the more consequential point is that recruitment through the course-announcement channel systematically under-samples students weakly engaged with institutional channels, which is the low-perceived-usefulness tail that §5's onboarding implication is aimed at. As written, the paper cannot tell a reader whether the students an institution most needs to understand are present in the sample at all. Either the available composition data must be reported and the exclusion argued about directly, or the implication must be withdrawn to a research agenda.
**Severity**: Major
**Evidence Anchor**: absence: §3.1 participant description — expected sample composition beyond year level (enrolment status, commuter or residential, first-generation status, connectivity access); checked abstract, §3.1, §3.2, §4, §6
**Confidence**: 4 — routine institutional-research practice on recruitment-channel coverage and digital-equity subgroups.

### W3: The paper's practice-facing implication is actionable only under the causal direction the paper declines to claim
Two sentences after stating that the reverse pathway is equally consistent with the data, §5 offers onboarding that helps students "see concrete usefulness" as potentially worth institutional attention. That implication has force only if perception drives use — the direction the manuscript has just disclaimed. The hedging is genuine but generic: it warns that the implication is unproven without naming the specific dependency, and it does not state what an institution would change, for whom, or at what cost. An adjacent-field reader is therefore invited to act on a conditional whose condition is never surfaced. The fix is to make the directional assumption explicit as a condition of the recommendation, or to demote the paragraph to a stated research agenda.
**Severity**: Major
**Evidence Anchor**: text: §5 "modest support for the intuition that LMS onboarding which helps students see concrete usefulness" and "may be worth institutional attention"
**Confidence**: 4 — I evaluate onboarding-investment cases against evidence of this type as part of my role.

### W4: The absence of log data is presented as inherent to the design rather than as a disclosed choice at an institution that owns the logs
The limitation is stated as though log measurement were unavailable in principle. It was available in principle: the surveyed institution holds the event logs. Whether access was sought and refused, precluded by the ethics approval or the anonymity guarantee, or simply not pursued materially changes how much weight an adjacent-field reader places on the self-report, and it is a one-sentence disclosure. If access was declined on governance grounds, that fact is independently informative to this readership.
**Severity**: Minor
**Evidence Anchor**: text: §6 "LMS use was self-reported through a single item rather than measured through system logs"
**Confidence**: 4 — direct familiarity with LMS log-access governance and ethics-approval constraints.

### W5: The perceived-usefulness instrument is accessible only by citation, and the adaptation is unspecified
The construct is given a one-line conceptual definition and a source, but the six items are not reproduced and the nature of the adaptation is not described. Internal consistency is reported, which speaks to homogeneity rather than to content. A reader outside technology-acceptance research cannot see what "usefulness" was operationalised as, and so cannot judge whether the predictor is about academic benefit, convenience, or instructor compliance — three quite different things for institutional purposes. An appendix with the adapted items resolves this.
**Severity**: Minor
**Evidence Anchor**: text: §3.2 "measured using a six-item scale adapted from Costa and Wren (2019)"
**Confidence**: 4 — standard expectation for instrument transparency when reusing scales across fields.
