contract_role: domain

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: block
trigger: "a cited source materially misrepresented in a way that changes what the manuscript is entitled to assert"
block_class: repairable

Two independent defects fire this dimension's block condition. The first is the trigger quoted above: Ferro & Nakamura (2021) is credited in §2 with a finding that its own title states in reverse, and that misreading is the stated foundation of the equity rationale the Discussion returns to. The second is the clause "a core construct used in a sense the field does not recognise": *retention*, an institutional term with a settled operational meaning in the persistence literature, is measured as sitting one course's final assessment and then discussed and concluded in the vocabulary of programme- and institution-level persistence. I record the block as **repairable** rather than fatal because my fatal condition is reserved for fabricated or non-reconstructible content: the reference entries are internally consistent, the study's factual account can be reconstructed, and both defects are correctable by re-reading the cited source, renaming the construct to what was actually measured, and rewriting the claims that depended on each. The corrections are substantial and reach the abstract, title framing, Discussion, and Conclusion, but they do not require abandoning the dataset.

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

This manuscript asks a question the field genuinely needs answered — whether student-facing dashboards move persistence outcomes rather than satisfaction metrics — and it is unusually candid in places about the limits of click-based engagement measurement. My assessment concerns whether its claims survive contact with the literature it invokes and with the technical vocabulary it borrows. On both counts I found problems that reach the paper's headline contribution rather than its margins.

The most serious is a source-fidelity failure. Section 2 states as settled that "Dashboards have been shown to reliably improve outcomes for lower-achieving students," attributing this to Ferro & Nakamura (2021). The reference list gives that source's title as *"When dashboards demotivate: Peer comparison and the lower-achieving student."* A paper carrying that title is, on any ordinary reading, reporting a demotivation effect concentrated among exactly the population the manuscript credits it with helping. The manuscript does not merely mention this source in passing; it says the position "underpins much of the equity-oriented rationale for institutional dashboard deployment, and we return to it in the Discussion," which it does. The equity framing therefore rests on an inversion. Compounding this, §2 goes on to describe the demotivation risk under Osei (2020) without ever noticing that it has just placed two of its own sources in flat contradiction — which is itself evidence that the Ferro & Nakamura entry was not read closely.

The second problem is constructual. In the higher education persistence literature, "retention" is not a loose synonym for finishing something; it denotes a student's continued enrolment across an institutionally defined interval, and institutions report it as such. The manuscript's §3.3 defines retention as remaining enrolled through and sitting the final assessment of one 15-week course. That is course completion, which is a legitimate outcome and a defensible thing to study — but it is a different construct, with different determinants, from persistence. The substitution is silent: the term is introduced without definition in the abstract and title, operationalised narrowly in Methods, and then re-expanded in §6 to "improving retention across programs and disciplines" for "higher education institutions worldwide." The Limitations section flags the single-course setting and the single-institution dashboard design, but never flags that the outcome variable does not mean what the surrounding prose says it means. Two references in the list, Halloran (2020) on gateway-course retention interventions and Wexler & Ojo (2020) on retention modelling with LMS trace data, are precisely the sources whose engagement would have caught this, and neither is cited anywhere in the text.

Two further observations I record without scoring them. First, the arithmetic of several reported quantities does not hold — a 1–5 integer item with N = 10 and M = 3.00 cannot produce a sample SD of 0.10, and t(140) = 1.31 does not yield p = .008. These belong to the methodology seat's statistical-reporting audit, and I defer the full check there; I flag them only because they bear on whether the *domain* quantities carried into the Discussion can be trusted at all. Second, all fifteen references share the DOI prefix 10.5555, which is a reserved test prefix rather than a registrant prefix and resolves to no live record. I raise this for editorial verification rather than scoring it, because I cannot distinguish a manuscript-preparation placeholder from a fabrication, and the difference between those two readings is the difference between a repairable block and a fatal one.

Reviewer note on my own limits: I have assessed the interpretation and representation of domain quantities rather than auditing the underlying computations, and I have not evaluated the sessionization rule's technical feasibility.

### S1: Accurate and appropriately specific handling of the achievement-goal literature
The treatment of goal orientation is the strongest piece of literature work in the paper. It correctly identifies performance-avoidance orientation as the moderator that turns relative-standing feedback into a threat signal, and correctly frames the direction of effect as contingent rather than uniform. This is the accepted account in the field and it is stated without overreach.
**Evidence Anchor**: text: §2 "Performance-avoidance oriented students, in particular, may interpret an unfavorable comparison as a threat to be avoided"

### S2: Correct representation of the measurement critique of click-based proxies
The manuscript states the click-count problem as the field states it — that session and page-view counts index opportunity for engagement rather than cognitive engagement itself — and applies the critique to its own measure rather than only to others'. The Vandermeer (2023) attribution is consistent with the source's stated scope.
**Evidence Anchor**: text: §2 "click-based engagement metrics should be treated as rough indicators rather than as faithful measures"

### S3: Methods-level candour about an analytic simplification
Naming the median split as a coarse choice made for interpretability, at the point of use rather than buried in Limitations, is the right convention and is not universally observed in this literature.
**Evidence Anchor**: text: §3.3 "This median split is a coarse simplification of a continuous measure"

### W1: Ferro & Nakamura (2021) is cited for the reverse of its finding, and the equity argument is built on the reversal
The claim that this source shows dashboards "reliably improve outcomes for lower-achieving students" is contradicted by the source's own title, which reports demotivation among that population. The manuscript designates this position as the foundation of the equity rationale for institutional deployment and returns to it in §5 when positioning its results within the "who benefits" debate. Every downstream sentence that leans on differential benefit for lower-achieving students inherits the error. Uncorrected, the paper would publish a false statement about a specific study into the record, and its equity positioning would be unsupported at the root; no correction short of re-reading the source and rebuilding §2 and the corresponding Discussion passage repairs it.
**Severity**: Critical
**Evidence Anchor**: text: §2 "Dashboards have been shown to reliably improve outcomes for lower-achieving students"; References "When dashboards demotivate: Peer comparison and the lower-achieving student"
**Confidence**: 5 — direct comparison of the attributed claim against the cited title, both present in the manuscript.

### W2: "Retention" is operationalised as single-course completion and then discussed as institutional persistence
The outcome measured is whether a student sat one course's final assessment. The outcome claimed, in the abstract, Discussion, and Conclusion, is retention in the sense the persistence literature and institutional reporting use — continued enrolment across programmes and disciplines. These constructs have different base rates, different determinants, and different policy levers; a student may complete a gateway course and not re-enrol, or withdraw from it and persist in the institution. Because the substitution is never acknowledged, the paper's stated contribution to the retention literature is a contribution to a literature it did not measure, and §6's recommendation to institutions rests on an inference the design cannot license. Repair requires renaming the construct throughout, restating the contribution against the course-completion literature, and deleting or heavily qualifying the institutional generalisation — after which the empirical core survives, but as a different and smaller paper than the one submitted.
**Severity**: Critical
**Evidence Anchor**: text: §3.3 "Course retention was coded dichotomously as whether the student remained enrolled and completed the final assessment"; §6 "improving retention across programs and disciplines"
**Confidence**: 5 — the operational definition and the generalised claim are both explicit in the text; the construct distinction is standard in the persistence literature.

### W3: Perceived control is named a mediating construct in the Discussion but is never modelled as one
Mediation is a specific claim about causal ordering that requires the mediator to be tested on a path between predictor and outcome. The manuscript's only analysis involving perceived control is a two-group mean comparison; the outcome variable does not appear in it. Calling the construct "mediating" in the Discussion therefore imports a technical term the analysis does not support. The problem is aggravated by the measure itself — a single global item, defended as conventional for burden reasons, which cannot carry a mediation claim even if one were tested. Repair requires either an actual mediation analysis on a properly instrumented measure, or removal of the mediation vocabulary and its replacement with a statement of co-occurrence.
**Severity**: Major
**Evidence Anchor**: text: §5 "It also complements accounts emphasizing perceived control as a mediating construct"
**Confidence**: 4 — the term's technical meaning is unambiguous; I am confident no mediation model is reported, less certain whether one was estimated and omitted.

### W4: The self-regulated learning framework carries the theoretical argument but is never sourced to its canonical literature
The forethought / performance / reflection cycle is introduced in §1 as the mechanism justifying the study, with no citation of any kind. The only SRL citation in the paper is Rutledge & Berange (2022), a dashboard-specific application, and the framework's phase vocabulary is applied inconsistently: §1 says the dashboard "fuels the reflective phase," while §2 says dashboards support "the forethought and self-monitoring phases." A reader cannot tell which phase the study claims to engage, and no phase is measured. A synthesis source appearing in the reference list, Kessler & Amadou (2019), would have supplied the missing grounding and is never cited. The consequence is that the theoretical account is narrated around the results rather than tested by them.
**Severity**: Major
**Evidence Anchor**: absence: Introduction and Literature Review theoretical framing — expected citation to a canonical self-regulated learning source for the forethought/performance/reflection cycle; checked §1, §2, all in-text citations, and the 15-entry reference list
**Confidence**: 4 — exhaustive check of in-text citations against the reference list; the phase inconsistency is verbatim in the two sections.

### W5: The claimed position in the "who benefits from dashboards" debate is not earned by any reported analysis
Section 5 opens by asserting that the results speak to the differential-benefit debate. That debate is about heterogeneity of effect by prior achievement. The manuscript reports no subgroup analysis by prior achievement, no interaction term, and no achievement covariate anywhere; the only stratification is a median split on the predictor itself, which cannot address heterogeneity in who benefits. Combined with the reversed key citation for that debate (W1), the manuscript's entry into the differential-benefit conversation is unsupported from both directions — the literature it cites and the analysis it ran. Either the claim is withdrawn or the analysis is performed on data that would need to include a prior-achievement measure the paper does not report collecting.
**Severity**: Major
**Evidence Anchor**: text: §5 "These results speak to an ongoing debate in the literature about who benefits from dashboards"
**Confidence**: 4 — based on a full read of §3.4 and §4 for any achievement-stratified analysis.

### W6: The abstract reports a correlation nearly double the one in the Results, and the stronger value carries the abstract's claim
The abstract states r = .42; §4.2 states r = .24. These describe the same association and cannot both be correct. The difference is not cosmetic: .42 is a moderate association that would support the abstract's "promising lever" framing, while .24 accounts for under 6% of shared variance and is closer to the "help at the margin" reading §5 offers. Readers, and any subsequent meta-analysis, would extract the abstract value. Repair requires identifying which value is correct and rewriting whichever claims depended on the discarded one, including the abstract's concluding sentence.
**Severity**: Major
**Evidence Anchor**: text: Abstract "Dashboard engagement correlated positively with retention (r = .42)"; §4.2 "positively associated with course retention (r = .24, p = .004)"
**Confidence**: 5 — direct textual comparison of two stated values for one association.

### W7: Causal language in the Discussion and Conclusion contradicts the design, and contradicts the audit the paper itself cites
Section 1 promises to "distinguish the pattern in the data from the causal story," and §2 cites Ibarra (2023) for the finding that causal language in this literature outruns the evidence. Sections 5 and 6 then assert that engagement "improved" retention, that increasing engagement "raises the probability" of completion, and that dashboard investment is "a dependable strategy." From an observational, cross-sectional design with a self-selected volunteer sample, none of these is licensed; the reverse pathway, in which students already on track to complete are the ones who open a progress display, is at least as consistent with the data. Citing the audit and then committing the audited error is a source-fidelity problem as much as an inferential one, because it misrepresents the manuscript's own compliance with a standard it has invoked. Repair is a rewrite of the causal verbs across §5 and §6 and of the abstract's concluding sentence.
**Severity**: Major
**Evidence Anchor**: text: §5 "dashboard engagement improved course retention"; §2 "causal language frequently outruns the evidence"
**Confidence**: 4 — the design description and the causal verbs are both explicit; the strength of the reverse-pathway alternative is my judgement.

### W8: Nine of fifteen references are never cited, including the two retention sources most relevant to the paper's central construct
Only Calloway (2019), Ferro & Nakamura (2021), Osei (2020), Rutledge & Berange (2022), Vandermeer (2023), and Ibarra (2023) appear in the text. The nine uncited entries include Halloran (2020) on gateway-course retention interventions, Wexler & Ojo (2020) on retention modelling with trace data, and Solberg & Whitfield (2018) on institutional deployment — the three that bear most directly on the claims of §6. No systematic review of student-facing dashboards is cited anywhere, which leaves the abstract's assertion that the evidence base "remains thin" resting on the authors' impression rather than on any synthesis. On its own this is a citation-hygiene and coverage defect that improves the paper's grounding without changing its core claims; its significance here is diagnostic, since the uncited sources are the ones that would have surfaced W2.
**Severity**: Minor
**Evidence Anchor**: absence: Reference list versus in-text citations — expected in-text engagement with the nine listed but never cited sources, including Halloran (2020) and Wexler & Ojo (2020); checked §1 through §6 for every reference-list entry
**Confidence**: 4 — entry-by-entry match of the reference list against in-text mentions.
