## Scoring Plan Dissent

*(omitted — no dimension requires dissent)*

Wait — per protocol, an empty dissent section is invalid. Removing it.

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
trigger: "the paper asserts substantive implications for other disciplines or for practice with no supporting evidence or citation, such that an adjacent-field reader cannot determine what was measured or what may legitimately be carried across"

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I read this manuscript as the person who would be handed it by a provost with a note saying "let's do this." My question is not whether the correlation is real but whether an adjacent-field reader — an institutional researcher, a registrar, an IT governance officer, a programme director in a discipline other than statistics — could take the paper's stated implication and act on it without harming students or violating their own data policies. On that test the manuscript fails, and it fails specifically at the point where it reaches outward.

The internal machinery is more legible than most papers of this type. The three core measures are operationally defined in terms an outsider can reconstruct: sessions with a thirty-minute inactivity rule, retention as a dichotomous completion flag, perceived control as a single 1–5 item. Section 2 is unusually candid about the weakness of click-based proxies, and §5.1 states the single-course, single-interface scope without hedging. Those are real strengths and I want them on the record, because they make the failure at the outward-facing boundary more conspicuous rather than less.

That failure is the Conclusion. Section 5.1 says the study sits inside one introductory statistics course with one particular dashboard design; §6 then tells "higher education institutions worldwide" that dashboards plus encouragement are a "dependable strategy" and a "generalizable lever" "across programs and disciplines." Nothing in the design licenses either the geographic or the disciplinary reach. The only gesture toward disciplinary breadth is §3.1's assertion that the course served "a range of majors" — a composition claim with no distribution reported anywhere, and no analysis by major. So a reader from another field is handed two mutually contradictory scope statements and no basis for choosing between them. Under my Phase 1 block criterion this is the second branch exactly: a substantive practice implication asserted without supporting evidence, leaving an adjacent-field reader unable to determine what may legitimately be carried across. Note also that the abstract, which is what most cross-field readers will actually consume, reports an effect (r = .42) nearly double the one in §4.2 (r = .24) and frames the finding as a "lever." The version of this paper that travels between disciplines is stronger than the version that was measured.

Then the operational question. Strip the recommendation to what was actually measured and it says: increase the number of dashboard sessions. I have been on the receiving end of that mandate. Once an institution instruments a metric and tells staff to raise it, the metric moves — through nudge emails, course-page placement, participation credit — whether or not anything cognitive changes underneath. Section 2 already told me (via Vandermeer 2023) that session counts are not cognitive engagement. Section 6 nonetheless recommends acting on session counts. The manuscript owes a practitioner one paragraph distinguishing the construct from the lever and naming the gaming risk; it contains none.

The equity strand worries me most. Section 2 reports that relative-standing feedback can discourage struggling students and that direction of effect depends on goal orientation. The peer-comparison band was shown to every enrolled student by default, with no opt-in and no opt-out described. The study then runs no analysis by prior attainment, engagement trajectory, or goal orientation, and recommends universal encouragement. Worse, the sampling design excludes precisely the students the equity rationale is about: participation required responding to a mid-term announcement, so early withdrawers, non-respondents, and the disengaged are structurally absent from the sample used to justify a policy aimed at them. Scaling this recommendation concentrates its untested risk on the population it claims to serve. I also note that §2's equity premise — dashboards "reliably improve outcomes for lower-achieving students" — is attributed to a source whose own title says dashboards demotivate that group; the domain seat should adjudicate that, but the recommendation leans on it.

Finally, the governance layer, which is where I would be blocked from implementing anything. Section 3.2 states that students were not informed their dashboard activity would be analysed. There is no ethics-approval statement, no legal-basis or legitimate-interest reasoning, no data-minimisation or retention terms, and no opt-out. For a GDPR-aligned or DELICATE-style institution, and for most venues in this space, that is a submission prerequisite rather than a formatting nicety. It is also self-undermining: a paper recommending institutional-scale trace-data practice should model the disclosure regime it wants adopted.

I have flagged several arithmetic and reporting inconsistencies below because they are visible without any statistical audit, but I defer their inferential consequences to the methodology seat.

### S1: Core measures are operationally defined at a level an outsider can reconstruct
Section 3.3 gives the sessionization rule, the retention coding decision (including the enrolled-but-absent case), and the exact wording and scale of the perceived-control item. An adjacent-field reader can state what was counted without guessing, and can judge comparability against their own platform's logging conventions.
**Evidence Anchor**: text: §3.3 "A session was defined as a dashboard view preceded by at least thirty minutes of inactivity, following the platform's default sessionization rule."
**Confidence**: 5 — I specify log-based engagement measures for institutional reporting.

### S2: Literature review states the measurement caveat plainly enough for non-specialists
Section 2 explains, in ordinary language and with citation, why page-view and session proxies conflate distinct behaviours. A reader from outside learning analytics arrives at §3.3 already equipped to discount the measure appropriately — which is exactly the kind of scaffolding cross-disciplinary readability requires.
**Evidence Anchor**: text: §2 "click-based engagement metrics should be treated as rough indicators rather than as faithful measures of the cognitive engagement the theory implicates"
**Confidence**: 5 — this is the caveat I raise most often with campus stakeholders.

### S3: Section 5.1 states local scope honestly
The limitations paragraph concedes the single-course setting and the interface-specific design without softening. This is the correct scope statement; my objection is that §6 abandons it.
**Evidence Anchor**: text: §5.1 "the study was conducted within a single introductory statistics course, and the specific dashboard design used here differs from those deployed elsewhere"
**Confidence**: 5 — plain reading of an explicit concession.

### W1: Dashboard trace data were analysed without informing the students concerned
Section 3.2 states outright that consent covered the survey only and that students were not told their dashboard activity would be analysed for research. The behavioural log data — the paper's primary outcome-side variable — therefore rest on undisclosed secondary use of identifiable trace data. Under GDPR-aligned governance and DELICATE-style frameworks this requires, at minimum, a documented legal basis, a transparency notice, and either consent or an approved justification for its absence. None appears. Uncorrected, no institution can cite this paper as precedent and most venues cannot publish it; the defect alone makes acceptance impossible until the authors document approval and disclosure conditions.
**Severity**: Critical
**Evidence Anchor**: text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study."
**Confidence**: 5 — student-data governance and secondary-use review is my primary advisory area.

### W2: No ethics approval, data-minimisation, retention, or opt-out statement anywhere in the manuscript
I searched the Methods, Limitations, Conclusion, and reference apparatus for any of the standard governance elements: an IRB or research-ethics committee reference, a waiver justification, a statement of what log fields were extracted and for how long they were retained, a de-identification procedure, and whether students could suppress the peer-comparison band shown to them by default. None is present. Without these, a practitioner cannot replicate the deployment lawfully in their own jurisdiction, and a reviewer cannot tell whether W1's non-disclosure was sanctioned or simply unexamined. This requires substantive new text and possibly retrospective institutional review, but the study's findings could survive it.
**Severity**: Major
**Evidence Anchor**: absence: Methods §3.1–§3.4 and front matter — expected ethics-approval/IRB statement, data-minimisation and retention terms, and a dashboard opt-out provision; checked §3.1, §3.2, §3.3, §3.4, §5.1, §6, and the reference list
**Confidence**: 5 — I assess exactly this checklist for campus research proposals.

### W3: The Conclusion asserts worldwide, cross-programme applicability that the design cannot support and that §5.1 contradicts
Section 6 addresses "higher education institutions worldwide" and characterises dashboard investment plus encouragement as a "dependable strategy" that is "generalizable" "across programs and disciplines." The evidence base is one lecture section of one introductory statistics course at one institution, one term, one interface, a self-selected respondent pool, and a cross-sectional correlation of r = .24. No second discipline, institution, term, or dashboard design is present in the data, and no citation is offered to bridge the gap. Because §5.1 states the opposite scope, an adjacent-field reader receives contradictory instructions about what transfers and has no principled way to resolve them. This is the defect that blocks D4: as written, the paper's central practical claim is not supported by anything in it, and correcting it means rewriting the paper's headline implication.
**Severity**: Critical
**Evidence Anchor**: text: §6 "For higher education institutions worldwide" and "investing in student-facing dashboards and encouraging students to engage with them is a dependable strategy for improving retention across programs and disciplines"
**Confidence**: 5 — no domain expertise is needed to see a single-course design asked to license a worldwide claim.

### W4: Causal phrasing in §5 and §6 contradicts the design and the paper's own stated discipline
The Introduction promises to "distinguish the pattern in the data from the causal story that might explain it." Section 5 then opens by stating that engagement "improved" retention and that increasing engagement "therefore raises the probability" of completion; §6 repeats that dashboard engagement "is associated with, and raises," retention. A cross-sectional correlation among self-selected respondents cannot support either verb, and the more plausible reverse and confounded readings — students who are already going to persist are the ones who keep opening the dashboard — are never addressed. For readers outside the field this is the sentence that will be quoted, so the wording is not cosmetic. Argumentative coherence belongs to other seats; I flag it because it is the mechanism by which the overreach propagates outward.
**Severity**: Major
**Evidence Anchor**: text: §5 "dashboard engagement improved course retention" and "increasing dashboard engagement therefore raises the probability that a student completes the course"
**Confidence**: 4 — the design-to-verb mismatch is plain; I leave the inferential audit to the methodology seat.

### W5: The abstract reports an effect roughly double the one in the Results
The abstract states r = .42; §4.2 states r = .24. Both are presented as the same association between dashboard engagement and retention. Whichever is correct, the abstract is the artefact that circulates to adjacent fields, to practitioners, and into evidence syntheses, and it currently overstates the finding by a factor of nearly two while framing it as a "promising lever." Correcting this changes the magnitude of the paper's headline claim and requires the authors to reconcile both figures and confirm which analysis produced which.
**Severity**: Major
**Evidence Anchor**: text: Abstract "Dashboard engagement correlated positively with retention (r = .42)" and §4.2 "Dashboard engagement was positively associated with course retention (r = .24, p = .004)"
**Confidence**: 4 — direct comparison of two reported values; I have not attempted to recompute either.

### W6: The recommendation reduces to raising a click metric, with no implementation guidance or gaming safeguard
The only engagement quantity in the study is session count. Section 6's advice to "encourage students to engage" therefore operationalises, in any real deployment, as a mandate to raise session counts — through reminder emails, participation credit, landing-page placement, or advisor scripts. Section 2 has already established that session counts are not the cognitive engagement the theory implicates, so the recommended lever and the theorised mechanism are known to be different things. The manuscript nowhere warns that the metric is inflatable independently of learning, nowhere distinguishes a construct from a target, and nowhere tells an implementer what a successful deployment would look like other than more clicks. Without that, the paper hands institutions a gaming target and calls it a strategy. Adding this guidance is substantial work but does not overturn the reported association.
**Severity**: Major
**Evidence Anchor**: absence: §5 Discussion and §6 Conclusion — expected implementation guidance separating dashboard session counts from cognitive engagement plus a safeguard against incentivising the click metric; checked §5, §5.1, §6, and the abstract's implications sentence
**Confidence**: 5 — I have implemented and audited "increase dashboard use" mandates on campus.

### W7: Universal encouragement is recommended with no subgroup analysis, despite the paper's own demotivation literature
Section 2 records that relative-standing feedback can discourage struggling students and that the direction of effect depends on goal orientation, singling out performance-avoidance learners. The peer-comparison band was displayed to every enrolled student from week one with no opt-in. Yet the Results contain no analysis by prior attainment, engagement trajectory, goal orientation, or any other axis on which the literature predicts heterogeneous — including negative — effects. Section 5.1 does not list this as a limitation. The paper thus recommends a universal intervention while remaining silent on the subgroup its own review flags as at risk of harm, and it does so on a sample that structurally excludes the disengaged and the early withdrawers. A practitioner reading only §6 would have no reason to monitor for harm. Remedying this requires new analysis or withdrawal of the universal recommendation.
**Severity**: Major
**Evidence Anchor**: absence: §4 Results — expected subgroup analysis by prior attainment, engagement trajectory, or goal orientation before recommending universal encouragement; checked §4.1, §4.2, §4.3, Table 1, Table 2, and §5.1
**Confidence**: 5 — differential-impact review before scaling is the core of my advisory work.

### W8: The sampling frame is described in two incompatible ways within one subsection
Section 3.2 first says participants were drawn "using a random sample of students enrolled in the course section," then describes a mid-term LMS announcement to which "students who chose to respond" formed the sample, with non-respondents excluded. These are different designs with different external-validity properties, and the difference is exactly what determines whether the retention association can be read as anything other than a volunteer artefact. An outside reader cannot tell which occurred, which means they cannot judge comparability with their own student population — the central question when deciding whether to adopt a finding from another setting. Resolution requires the authors to state the actual recruitment mechanism and re-derive every generalisation claim from it.
**Severity**: Major
**Evidence Anchor**: text: §3.2 "Participants were drawn from the course enrollment using a random sample of students enrolled in the course section" and "Students who chose to respond, and who consented to the survey, formed the study sample"
**Confidence**: 5 — reading two contradictory sampling descriptions requires no statistical expertise.

### W9: Reported denominators do not reconcile across the Results
Section 4.3 states that all 142 students in the primary analytic sample were classified into engagement groups for the exam comparison, but Table 2 reports group sizes of 66 and 61, totalling 127. Separately, §4.1 reports 87 respondents answering the perceived-control item while §4.3's perceived-control comparison is reported on 156 degrees of freedom. A reader cannot determine which N supports which result, which means they cannot judge how much of the sample any given claim rests on or how much attrition sits behind each comparison. I am reporting the arithmetic contradiction only; its inferential consequences belong to the methodology seat.
**Severity**: Major
**Evidence Anchor**: table: Table 2 group n values (66 + 61 = 127) versus §4.3's claim that all 142 students were classified into engagement groups
**Confidence**: 4 — arithmetic reconciliation is straightforward; I have not audited the tests themselves.

### W10: Descriptive statistics cannot be read at face value
Perceived control is reported as 3.847 with SD = 0.62 from a single integer 1–5 item — three-decimal precision that no such measure supports and that gives outside readers a false impression of measurement resolution. More seriously, the secondary clarity item is reported as N = 10, M = 3.00, SD = 0.10 on an integer 1–5 scale; with ten integer responses averaging exactly 3.00, the sample SD must be either 0 or roughly 0.47 or larger, so 0.10 cannot arise from the stated design. The item is descriptive-only and carries no claim, so this does not move the paper's conclusions, but it signals a reporting or extraction error the authors should trace.
**Severity**: Minor
**Evidence Anchor**: text: §4.1 "3.847 (SD = 0.62)" and "N=10; M=3.00; sample SD=0.10; integer scale=1-5"
**Confidence**: 4 — the impossibility follows from the stated scale; I flag it for the methodology seat rather than resolving it.

### W11: The disciplinary-breadth claim that underwrites the Conclusion's reach is unsubstantiated
Section 3.1 asserts that because the course was a required quantitative-reasoning offering, the sample has "some disciplinary breadth even within one course." No distribution of majors is reported, no analysis is stratified by major, and no citation supports the inference that a service course's enrolment mix substitutes for sampling across disciplines. This single unsupported sentence is the only bridge between a one-course study and §6's promise of results holding "across programs and disciplines." Either the composition data are reported and analysed, or the claim and everything resting on it must go.
**Severity**: Major
**Evidence Anchor**: text: §3.1 "served as a required quantitative-reasoning course for a range of majors, giving the sample some disciplinary breadth even within one course"
**Confidence**: 5 — this is the load-bearing assumption a practitioner would rely on when judging transfer.

### W12: The equity premise is attributed to a source whose title states the opposite finding
Section 2 asserts that "Dashboards have been shown to reliably improve outcomes for lower-achieving students," citing Ferro and Nakamura (2021), and says this position "underpins much of the equity-oriented rationale for institutional dashboard deployment." The reference list gives that work's title as "When dashboards demotivate: Peer comparison and the lower-achieving student." The Discussion then invokes this premise to align the study's result with the view that progress cues support persistence. If the citation is a mischaracterisation, the paper's equity rationale — and my main reason for demanding subgroup analysis in W7 — is built on an inverted reading of its own source. Domain accuracy sits with another seat; I flag it because the recommendation depends on it.
**Severity**: Major
**Evidence Anchor**: text: §2 "Dashboards have been shown to reliably improve outcomes for lower-achieving students" and reference list "When dashboards demotivate: Peer comparison and the lower-achieving student"
**Confidence**: 4 — I compared claim to cited title; I have not read the cited work.

### W13: A result is narrated as non-significant while its reported p value falls below the stated alpha
Section 3.4 adopts an alpha of .05 throughout. Section 4.3 then reports the exam-performance comparison as one that "did not reach a comparable level," with "the difference was small, t(140) = 1.31, p = .008," and §5 describes it as "weaker still." As printed, that p value is significant under the paper's own decision rule, and it is inconsistent with the reported t statistic. A reader outside the field cannot tell whether the intended message is a null result, a small significant result, or a typographical error, and the Discussion's calibration of the whole finding depends on which it is.
**Severity**: Major
**Evidence Anchor**: text: §4.3 "the difference was small, t(140) = 1.31, p = .008" and §3.4 "an alpha of .05 was adopted throughout"
**Confidence**: 4 — the contradiction with the stated alpha is visible on its face; the statistical reconciliation is the methodology seat's.
