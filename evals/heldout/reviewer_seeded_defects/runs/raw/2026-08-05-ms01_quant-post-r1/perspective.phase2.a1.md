contract_role: perspective

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: block
trigger: "Central interdisciplinary or practical claims are asserted with no supporting evidence or mechanism"

Justification: the manuscript's outward-facing claim is not "we observed an association in one course" but the Conclusion's instruction to "higher education institutions worldwide" that dashboard investment "is a dependable strategy for improving retention across programs and disciplines." That is a practical and cross-context claim, and the evidence base for the *transfer* is empty: one dashboard design, one unnamed LMS, one introductory statistics course, one term, one institution, no comparison condition, no implementation-fidelity data, no cost data, and no analysis of who benefits or who is harmed. §5.1 concedes that "the specific dashboard design used here differs from those deployed elsewhere," which the Conclusion then overrides rather than respects. A second, independent branch of the same failure: the recommended lever ("encouraging students to engage") has no mechanism evidence behind it, so an adjacent-field or practitioner reader cannot act on the finding even inside the studied setting. Compounding both, the number that travels to non-specialist readers (Abstract, r = .42) is not the number the study reports (§4.2, r = .24), and the equity rationale exported to institutional readers rests on a source whose own title contradicts the claim attributed to it. The framing is legible enough at sentence level; what fails is substantiation of every claim that leaves the room.

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I read this manuscript from a learning-analytics ethics and data-governance chair, with prior responsibility for a campus analytics deployment that was paused after a student-consent complaint. My scoring lane is whether the paper's framing, constructs, and stated implications are usable and substantiated for readers and decision-makers outside the immediate dashboard-research subfield. Three things dominate that assessment, and I will say the governance one first because it is the one that determines whether the paper is publishable at all in its current form, not merely how strong its findings are.

First, the behavioural-log component appears to sit outside any consent instrument, and there is no ethics approval statement anywhere in the manuscript. §3.2 describes a consent process that covers the survey and then states, without apparent discomfort, that "Students were not informed that their dashboard activity data would be analyzed for this study." Those two sentences sit four lines apart. The paper therefore documents, in its own Methods, secondary research use of individually linked trace data (session-level dashboard views joined to enrollment and withdrawal status) without notice to the data subjects, and it does so while addressing an audience of institutions that in most jurisdictions operate under purpose-limitation, records-privacy, or research-ethics regimes that would not permit a replication as described. This is not a stylistic objection to the paper's tone. It is the reason a governance reader cannot use the paper: the deployment recommendation in §6 is not implementable by the institutions it addresses under the conditions the study itself ran. I note that the primary determination of whether the log analysis was permissible belongs to the methodology seat's data-handling lane (D1); what belongs to mine is that an unqualified worldwide recommendation is unsubstantiated when the study's own data-collection conditions are not reproducible across the jurisdictions being advised.

Second, and this is the finding I care most about, the intervention has a harm mechanism designed into it and the study is structurally arranged so that the harm cannot appear. §3.1 states that the dashboard displayed "a peer-comparison band." The paper's own Literature Review then documents that relative-standing feedback discourages rather than mobilises struggling students, and that performance-avoidance oriented students may respond by "disengaging from the very interface intended to re-engage them" (Osei, 2020). The manuscript reports no subgroup, moderation, or goal-orientation analysis of any kind. It aggregates over precisely the population its cited literature predicts is harmed, and then reads the aggregate as support for continued deployment. The sampling design makes this worse rather than neutral: recruitment happened "midway through the term" via a voluntary LMS announcement, and the analytic sample consists of respondents to that announcement. A student demotivated in weeks two through six, who disengaged and withdrew, is not in the frame to answer a week-eight survey. The population most likely to be harmed is the population least likely to be sampled, so a positive engagement–retention association is close to what this design would produce whether or not the peer-comparison band was hurting anyone. The Discussion's alignment claim with "the view that externalized progress cues can support persistence" is therefore not evidence about who benefits; it is a restatement of who remained.

The equity framing that carries this rationale is also mis-sourced. §2 asserts that "Dashboards have been shown to reliably improve outcomes for lower-achieving students," attributed to Ferro & Nakamura (2021) — a work the reference list gives as *When dashboards demotivate: Peer comparison and the lower-achieving student*. A citation is doing the opposite work from what its title indicates, and it is the citation the paper says "underpins much of the equity-oriented rationale for institutional dashboard deployment." The domain seat owns the accuracy determination; I record it because the equity claim is one of the two claims this paper exports beyond its subfield, and it is exported on an inverted source.

Third, on deployment realism. From a practitioner's chair, §6 asks a provost to fund a system on the basis of r = .24 in one course, and it recommends "encouraging students to engage" as the operative lever. That mistakes an engagement indicator for an engagement cause. The students who opened a dashboard fourteen times already possessed whatever disposition, schedule slack, or prior confidence produced the opening; instructing the remainder to click more does not manufacture that disposition, and the paper offers nothing — no comparison condition, no manipulation, no dose-response with covariate control — that distinguishes the two readings. Nor does it supply the inputs an actual deployment decision requires: licence and integration cost, staff time, whether the dashboard was configured as studied, or what fraction of enrolled students ever opened it. I understand the statistical form of this sorting problem is the methodology seat's to name; the operational form is mine, and it is what makes the Conclusion unusable as guidance.

I want to be explicit about what is genuinely well done here, because it is not nothing and it sharpens the contrast. The Literature Review's fourth paragraph is honest and self-implicating in a way that most dashboard papers are not, and §3.1 and §3.3 state scope and measurement compromises plainly. The paper knows the right things. It then writes a Conclusion that behaves as though it does not. The gap between §5.1's careful single-course caveat and §6's "dependable strategy... across programs and disciplines" is the central cross-disciplinary defect, and it is a writing-and-argument decision, not a data limitation.

Outside my lane but worth flagging for the seats that own it: the reported numbers do not reconcile. Abstract r = .42 against §4.2 r = .24; t(156) in a sample of 142; t(140) = 1.31 paired with p = .008; Table 2 group sizes summing to 127 while the text says "All 142 students in the primary analytic sample were classified into engagement groups"; perceived control reported to three decimals from a 1–5 integer item; and a ten-student subsample reported as M = 3.00 with SD = 0.10, which is not attainable from integer responses. I do not score these and I defer their characterisation to the methodology reviewer.

### W1: Behavioural-log analysis appears to fall outside the consent instrument the paper describes
**Severity**: Critical
**Evidence Anchor**: text: §3.2 "Students who chose to respond, and who consented to the survey, formed the study sample" and "Students were not informed that their dashboard activity data would be analyzed for this study"
**Confidence**: 5 — I chair research-ethics review of trace-data protocols and have paused a deployment over this exact defect.

The consent described covers a survey about study habits. The analysis joins individually identifiable LMS session logs to enrollment, withdrawal, and final-exam outcomes for the same students, and the manuscript states that this use was not disclosed to them. As written, there is no consent, waiver, or notice basis on record for the study's primary data source. Uncorrected, this is not repairable by rewording: either an approved waiver or authorisation exists and must be produced, or the log analysis was conducted without a permissible basis and cannot be published.

### W2: No ethics approval statement anywhere in the manuscript
**Severity**: Major
**Evidence Anchor**: absence: manuscript-wide ethics reporting — expected an IRB or research-ethics committee approval statement with protocol identifier and the consent scope covering LMS log analysis; checked Abstract, §3.1, §3.2, §3.3, §3.4, §5.1, §6, References
**Confidence**: 5 — routine reporting requirement I apply as a reviewer and as an ethics-board member.

This is distinct from W1 and independently disqualifying under most venue policies: a study with fully proper approval and a documented waiver would still fail this reporting requirement, and a study with an approval statement could still have W1's substantive defect. The authors must state the reviewing body, the determination, the date or protocol number, and specifically how the behavioural-log component was covered. Absent that, no reader can verify governance and no adjacent-field reader can assess replicability under their own institution's rules.

### W3: The worldwide deployment recommendation has no transfer evidence behind it
**Severity**: Critical
**Evidence Anchor**: text: §6 "investing in student-facing dashboards and encouraging students to engage with them is a dependable strategy for improving retention across programs and disciplines"
**Confidence**: 5 — I have led an institutional analytics deployment and evaluated vendor generalisation claims of exactly this shape.

Every dimension along which the claim generalises is held at n = 1: one dashboard design, one unnamed LMS, one introductory statistics course, one term, one institution, one cohort. There is no comparison condition, no fidelity measure, no cost information, and no replication. "Dependable" is a reliability claim that requires variance across contexts to earn, and this study observed none. §5.1 states the single-course and single-design limitation, so the Conclusion contradicts the manuscript's own scope statement rather than extending it. Uncorrected, the paper's headline contribution to practice is false as stated, and it is the sentence institutional decision-makers will read.

### W4: The effect size reported in the Abstract is not the effect size the Results report
**Severity**: Major
**Evidence Anchor**: text: Abstract "Dashboard engagement correlated positively with retention (r = .42)" against §4.2 "positively associated with course retention (r = .24, p = .004)"
**Confidence**: 4 — plain internal comparison; I cannot tell which value is correct.

The Abstract is the surface that travels to adjacent fields, practitioners, press, and evidence syntheses. It reports roughly three times the variance-shared of the Results section's value. A reader outside the subfield who cites this paper will cite .42. The authors must state which figure is correct, correct the other, and reconcile the Discussion's "modest size" language with whichever value survives, since that hedge is calibrated to .24 and not to .42.

### W5: No heterogeneous-effects analysis for the subgroup the paper's own cited literature predicts is harmed
**Severity**: Major
**Evidence Anchor**: absence: §4 Results — expected a moderation or subgroup analysis by goal orientation or prior achievement for the students Osei (2020) predicts are harmed by relative-standing feedback; checked §3.4, §4.1, §4.2, §4.3, Table 1, Table 2, §5, §5.1
**Confidence**: 5 — my published work is on algorithmic harm in student-facing systems.

The dashboard included a peer-comparison band; the Literature Review documents demotivation from relative-standing feedback and describes performance-avoidance students disengaging from the interface. The study then reports only aggregate associations, and the mid-term voluntary sampling means students who disengaged early are largely absent from the analytic sample. The design is thus poorly positioned to detect the harm it cites, yet the paper reads its aggregate as support for scaling. Remedy requires either subgroup analysis with pre-registered moderators and a full-enrollment denominator, or explicit acknowledgement in Discussion and Conclusion that the study cannot speak to differential harm and therefore cannot recommend the peer-comparison feature.

### W6: Cited source is characterised as showing the opposite of what its title states
**Severity**: Major
**Evidence Anchor**: text: §2 "Dashboards have been shown to reliably improve outcomes for lower-achieving students" against References "When dashboards demotivate: Peer comparison and the lower-achieving student"
**Confidence**: 4 — title-level contradiction is unambiguous; I have not read the cited work.

The sentence attributing reliable improvement for lower-achieving students to Ferro & Nakamura (2021) is the stated foundation of "the equity-oriented rationale for institutional dashboard deployment," which the paper says it returns to in the Discussion. If the source in fact reports demotivation, the equity rationale inverts, and the recommendation in §6 becomes a recommendation to scale a feature that harms the students the rationale invokes. The domain reviewer owns verification; the authors owe a corrected characterisation and a reconsidered equity argument either way. The word "reliably" also overstates any single study.

### W7: The recommended lever confuses an engagement indicator with an engagement cause
**Severity**: Major
**Evidence Anchor**: text: §5 "increasing dashboard engagement therefore raises the probability that a student completes the course"
**Confidence**: 5 — this is the failure mode I encounter most often when translating analytics findings into institutional practice.

From a cross-sectional association the paper derives an intervention: raise engagement, raise completion. This holds only if dashboard opening causes persistence rather than indexing a disposition that produces both. Nothing in the design distinguishes these: no manipulation, no comparison condition, no covariate adjustment for prior achievement or workload, no temporal ordering within term. Operationally, an institution cannot buy the disposition by instructing students to click more. The Introduction promises to "distinguish the pattern in the data from the causal story," and cites Ibarra (2023) on causal language outrunning evidence; §5 and §6 then do the thing the paper audits. Remedy requires either a design that supports the intervention claim or removal of the actionable framing.

### W8: "Retention" is operationalised as within-course completion but exported in the institutional sense
**Severity**: Minor
**Evidence Anchor**: text: §3.3 "coded dichotomously as whether the student remained enrolled and completed the final assessment"
**Confidence**: 4 — familiar with how retention is defined in institutional-research and policy reporting.

In higher-education policy and institutional-research usage, retention means term-to-term or year-to-year persistence at the institution. Here it means sitting one final exam in one course, and it merges two distinct events (formal withdrawal and enrolled non-attendance) into one code. The Methods definition is clear, but the Abstract and Conclusion use the bare term to address institutional readers, who will import their own meaning. Relabel consistently as course completion, and report withdrawal and non-attendance separately so their different mechanisms remain visible.

### W9: The studied artefact is never specified, so no adjacent-field reader can situate the result
**Severity**: Minor
**Evidence Anchor**: absence: §3.1 Design and Setting — expected the LMS or dashboard product name and a figure or wireframe of the student-facing interface showing the peer-comparison band; checked §3.1, §3.3, Table 1, Table 2, §5.1, §6, References
**Confidence**: 4 — interface specification is standard for any design or HCI reader assessing a student-facing system.

The paper's own §5.1 states that interface features "may shape how students respond," which makes the omission self-undermining: readers are told the design matters and never shown it. The unnamed platform also leaves the sessionization rule ("the platform's default") unspecifiable, so the exposure measure cannot be reconstructed. A named system, a version, and one figure of the interface would let design, HCI, and information-science readers judge which features the finding could plausibly attach to.

### S1: The Literature Review's measurement critique is honest and turns on the paper itself
**Evidence Anchor**: text: §2 "Most dashboard studies, including the present one, infer engagement from coarse behavioral proxies such as page views or session counts"

Very few dashboard papers name their own exposure measure as a rough indicator, and fewer still articulate the specific confound (one careful reading scored below several thoughtless openings). This paragraph is competent scholarship and would survive extraction into a better paper.

### S2: Cross-sectional scope is stated explicitly rather than left for the reader to infer
**Evidence Anchor**: text: §3.1 "Because the design is cross-sectional, all measures reflect a single term and no student was observed across multiple courses or terms"

For an adjacent-field reader this is exactly the right kind of sentence: it fixes the observation window and the unit, and it forecloses a longitudinal misreading. It also establishes the standard against which the Conclusion should be judged, which is why the contrast with §6 is so visible.

### S3: Analytic simplifications are named as simplifications
**Evidence Anchor**: text: §3.3 "This median split is a coarse simplification of a continuous measure and was adopted for interpretability rather than statistical efficiency"

Declaring the cost of a coding decision at the point of the decision is good practice and rare. It gives a methodologically trained outside reader the information needed to discount the group comparisons appropriately without reverse-engineering the authors' reasoning.
