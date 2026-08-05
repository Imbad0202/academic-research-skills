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
trigger: "generalising to other institutions, populations, settings, or disciplines without supporting data or an argued warrant"

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I read this manuscript as the person who would have to sign the data-access approval before the study could run and then be asked, a year later, whether its evidence justifies a procurement decision. Both of those readings fail, and they fail for reasons that sit inside my assigned dimension rather than outside it: the manuscript's stated reach — to "higher education institutions worldwide," "across programs and disciplines" — is not a rhetorical flourish appended to a careful study. It is the paper's advertised contribution, and there is nothing in the evidence presented that supports it.

Let me be precise about the distance travelled. What was observed is an association of *r* ≈ .24 between dashboard session counts and course completion, among students who volunteered to answer a mid-term LMS announcement, in one section of one introductory statistics course, at one institution, in one term, with one particular dashboard design. What is recommended is that institutions worldwide invest in student-facing dashboards as "a dependable strategy" and a "generalizable lever." Every hop in that chain — from volunteers to enrolled populations, from one course to all programs, from one interface to dashboards in general, from one campus to all campuses, from association to lever — is asserted rather than argued. §5.1 correctly names the single-course and single-design constraints and says future work "should examine a wider range of dashboard designs and disciplinary contexts"; §6 then proceeds as though that work had already been done. A limitations paragraph that the conclusion contradicts is not a scope safeguard.

The governance problem is separate from the inference problem and, in my judgement, more immediately disqualifying. §3.2 discloses that students were not informed their dashboard activity would be analyzed for this study. That disclosure is stated plainly and to the authors' credit, but it arrives with no accompanying ethics approval statement, no lawful basis for processing behavioral data collected for one purpose and used for another, no retention or de-identification protocol, and no account of how log records were joined to survey responses that were consented separately. That last omission matters more than it may appear: if the survey was consented as a study of "study habits and dashboard use" and then keyed to individual trace logs, students consented to one thing and were enrolled in another. I am not asserting that no approval existed. I am observing that a reader — or an editor, or a data-protection officer at a campus considering this evidence — cannot tell, and that a paper whose central recommendation is that institutions collect and act on student trace data at scale carries a heightened obligation to model the governance it is implicitly asking others to adopt.

The equity gap follows from the same posture. §2 correctly reports that relative-standing feedback can discourage rather than mobilize struggling students, and that performance-avoidance oriented learners may disengage from the very interface meant to re-engage them. §3.1 then discloses that the deployed dashboard includes a peer-comparison band. Those two facts sit forty lines apart and are never brought into contact. There is no subgroup analysis by prior achievement or goal orientation, no examination of whether the students who did *not* persist were disproportionately those the literature predicts would be harmed, and no equity condition attached to the institution-wide recommendation. At *n* = 142 in one course, a differential-harm analysis would be underpowered — but the honest response to that is to withhold the deployment recommendation, not to issue it while the analysis is missing. A recommendation to encourage all students toward an interface that the paper's own cited literature says may demotivate some of them, unaccompanied by any safeguard, is not a neutral omission at institutional scale.

There is also a citation that appears to have been inverted. §2 states that dashboards "have been shown to reliably improve outcomes for lower-achieving students," attributed to Ferro & Nakamura (2021); the reference list gives that work's title as "When dashboards demotivate: Peer comparison and the lower-achieving student." I cannot read the cited source, so I state only what is visible on the page — but this is the sentence that carries "much of the equity-oriented rationale for institutional dashboard deployment," and the Discussion returns to it. If the citation is misused, the equity warrant for the paper's central recommendation is not merely thin, it points the other way.

On decision-usefulness, which is the question I would actually be asked: an institutional decision-maker can do nothing with this paper. There is no cost or resourcing information, no comparison against alternative retention interventions competing for the same budget, no implementation conditions, and no engagement with the possibility that dashboard use is a marker of students who were already going to persist rather than a manipulable lever. The manuscript treats "engagement is associated with retention" and "encouraging engagement raises retention" as interchangeable; a procurement officer acting on the second would be acting on evidence for the first. §5 briefly floats a plausible marginal reading ("dashboards help at the margin"), which is the most defensible sentence in the Discussion, and then §6 abandons it entirely.

Two caveats on my own competence. I do not adjudicate the degrees-of-freedom and *p*-value arithmetic in §4.3, the composition of Table 2 relative to the stated analytic sample, or whether a Pearson correlation is the right estimator for a dichotomous retention outcome; those belong to the methodology seat and I defer to it. I do flag the abstract/results discrepancy separately, because that is a cross-surface reading task rather than a statistical one, and because the abstract is the surface a decision-maker actually reads. And I want to record what the study does contribute: within one course, it documents a modest positive association between dashboard session counts and completion, and it does so with an operationalization transparent enough that another team could replicate the measurement. That is a real, if narrow, descriptive finding. The manuscript's problem is not that it found too little; it is that it reported its findings as though it had found something else.

My dimension scores `block`. Reframed as a single-course, single-cohort, volunteer-sample descriptive association study with a full ethics statement and an explicit refusal to issue deployment guidance, this manuscript would be assessable. As written, its interdisciplinary and cross-institutional reach is asserted at a scale the evidence cannot carry.

### S1: Literature Review is genuinely even-handed and legible to adjacent-field readers

§2 does what a good cross-disciplinary introduction should: it names the demotivation risk, the goal-orientation moderator, the click-proxy measurement problem, and the causal-language critique, in plain language a reader from institutional research or student affairs can follow without prior learning-analytics training. The section is the strongest part of the manuscript and, ironically, supplies most of the grounds on which the Conclusion should have been withheld.

**Evidence Anchor**: text: §2 Literature Review, demotivation paragraph — "Performance-avoidance oriented students, in particular, may interpret an unfavorable comparison as a threat to be avoided rather than a problem to be solved"

### S2: Engagement measure is operationalized concretely enough to be audited and replicated

§3.3 states the sessionization rule explicitly rather than gesturing at "engagement," and codes retention with a stated decision rule for withdrawn and non-sitting students. An outside team could reproduce the measurement definition from the text alone, which is not the norm in this literature and is a genuine transparency contribution.

**Evidence Anchor**: text: §3.3 Measures, dashboard engagement definition — "A session was defined as a dashboard view preceded by at least thirty minutes of inactivity"

### S3: Limitations section correctly identifies the measurement and scope constraints

§5.1 names the click-proxy narrowness, the self-report vulnerability, and the single-course, single-interface scope without hedging. The content of this paragraph is accurate and would, if honoured, have produced a publishable paper.

**Evidence Anchor**: text: §5.1 Limitations, first limitation — "dashboard engagement was operationalized narrowly as session counts, which does not capture the depth or quality of engagement"

### W1: Conclusion generalises to worldwide institutional deployment on evidence from one volunteer sample in one course

The Conclusion asserts global, cross-programme, cross-disciplinary transferability and characterises dashboard investment as "dependable." No supporting evidence is offered for any of these extensions: no second site, no second course, no second dashboard design, no cohort comparison, no argued warrant for why an association observed among self-selected respondents in an introductory statistics section should hold elsewhere. This is not an overstated sentence attached to a sound study; it is the manuscript's advertised contribution, and it is unsupported in full. Uncorrected, the claim a reader takes away is one the paper contains no evidence for, and it would equally justify blocking on the mandatory coherence and contribution dimensions owned by other seats. Remedy: delete the deployment recommendation and restate the contribution as a single-site, single-course descriptive association.

**Severity**: Critical
**Evidence Anchor**: text: §6 Conclusion — "For higher education institutions worldwide, the implication is clear" and "investing in student-facing dashboards and encouraging students to engage with them is a dependable strategy for improving retention across programs and disciplines"
**Confidence**: 5 — external-validity assessment of institutional evidence claims is my routine adjudication task

### W2: Behavioral trace data were analyzed without informing the students, as disclosed

§3.2 states that students were not told their dashboard activity would be analyzed for this study. Survey consent was obtained separately and covered a different object ("a short survey about their study habits and their use of the dashboard"). As described, this is secondary use of identifiable behavioral data without notice, in a study whose recommendation is that institutions do more of exactly this. Whether an approving body granted a notification waiver is not stated, so the procedure cannot be evaluated as published. This defect alone makes acceptance impossible at any venue with an ethics-statement requirement, independent of every other finding here. Remedy: supply the approval record and its conditions, state the lawful basis, document any waiver rationale, and describe the debriefing offered to participants — or, absent approval, withdraw the log-based analyses.

**Severity**: Critical
**Evidence Anchor**: text: §3.2 Participants and Sampling, recruitment paragraph — "Students were not informed that their dashboard activity data would be analyzed for this study"
**Confidence**: 5 — direct competence; approving student trace-data analyses is my institutional appointment

### W3: No ethics approval, lawful basis, retention, de-identification, or log-to-survey linkage protocol is disclosed

Distinct from W2's disclosed practice, the manuscript provides none of the documentation that would let a reader determine whether the practice was sanctioned or how the data were handled afterwards. The linkage question is the sharpest: survey responses consented under one description were evidently joined at the individual level to LMS logs, and no procedure, key-handling arrangement, or de-identification step is described. A campus data-protection reviewer could not clear this study from the text provided. Remedy: add a full data-governance statement covering approval, basis, linkage, retention, de-identification, and access controls.

**Severity**: Major
**Evidence Anchor**: absence: §3 Methods — expected ethics approval statement, lawful basis for processing, retention and de-identification protocol, and log-to-survey linkage procedure; checked §3.1 Design and Setting, §3.2 Participants and Sampling, §3.3 Measures, §3.4 Analysis, §5.1 Limitations, and the absent acknowledgements and data-availability sections
**Confidence**: 5 — reviewing data-protection documentation for student-data studies is my day work

### W4: Discussion asserts causation from a cross-sectional design, contradicting the paper's own stated commitment

§1 promises to distinguish the observed pattern from the causal story that might explain it, and §3.1 states the design is cross-sectional. §5 then opens by declaring that engagement "improved" retention and that increasing engagement "raises the probability" of completion. No temporal ordering, no counterfactual, no control for prior achievement, motivation, or enrolment intent supports this. The alternative reading — that dashboard use marks students who were already going to persist — is never addressed. Remedy: restate all outcome language as associational throughout §5 and §6, and add explicit treatment of the reverse-direction and common-cause explanations.

**Severity**: Major
**Evidence Anchor**: text: §1 Introduction and §5 Discussion, opening claims — "We are careful throughout to distinguish the pattern in the data from the causal story that might explain it" and "dashboard engagement improved course retention" and "increasing dashboard engagement therefore raises the probability that a student completes the course"
**Confidence**: 4 — inferential adjudication is adjacent to my seat, but the design statement and the contradiction are explicit on the page

### W5: The equity warrant rests on a citation that appears inverted relative to its own listed title

§2 attributes to Ferro & Nakamura (2021) the claim that dashboards reliably improve outcomes for lower-achieving students, and identifies this as underpinning "much of the equity-oriented rationale for institutional dashboard deployment." The reference list titles that same work as a study of dashboard demotivation and peer comparison affecting lower-achieving students. On the visible evidence the in-text claim and the source point in opposite directions. Because this sentence is load-bearing for the deployment recommendation, the discrepancy must be resolved before the recommendation can stand. Remedy: verify and correct the attribution, and revise any Discussion claim that depends on it.

**Severity**: Major
**Evidence Anchor**: text: §2 Literature Review and References list, Ferro & Nakamura entry — "Dashboards have been shown to reliably improve outcomes for lower-achieving students, who are said to gain the most from externalized progress cues" and "When dashboards demotivate: Peer comparison and the lower-achieving student"
**Confidence**: 4 — I can compare the in-text claim against the listed title, but cannot read the cited source itself

### W6: Institution-wide recommendation carries no equity safeguard and no differential-effect analysis, despite a deployed peer-comparison band

The dashboard studied includes a peer-comparison band (§3.1); the paper's own literature review says such bands may demotivate lower-achieving and performance-avoidance oriented students (§2); the Conclusion nonetheless recommends encouraging all students to engage, at scale, across programmes. No analysis examines whether non-retained students differed systematically, no subgroup breakdown appears in Table 1 or Table 2, and §5.1 does not list differential harm among its limitations. At *n* = 142 such an analysis would be underpowered, which is a reason to withhold the recommendation rather than to issue it unqualified. Remedy: either conduct and report differential-effect analyses by prior achievement, or remove the deployment recommendation and state explicitly that the study cannot speak to who is harmed.

**Severity**: Major
**Evidence Anchor**: absence: §4 Results and §5 Discussion — expected subgroup or differential-effect analysis by prior achievement and goal orientation for a dashboard containing a peer-comparison band; checked Table 1, Table 2, §4.1 Descriptive Statistics, §4.2 Dashboard Engagement and Retention, §4.3 Group Comparisons, §5 Discussion, §5.1 Limitations, and §6 Conclusion
**Confidence**: 5 — equity review of student-success systems is core to my appointment

### W7: The recommendation is not actionable by any institutional decision-maker

Even bracketing the generalisation problem, the Conclusion gives a decision-maker nothing to decide with: no cost or resourcing figures, no comparison against advising, early-alert outreach, supplemental instruction, or any other intervention competing for the same retention budget, no implementation conditions specifying which dashboard features or contexts the finding might apply to, and no engagement with whether engagement is manipulable at all. An *r* ≈ .24 in one course, with no comparator, cannot rank dashboards against alternatives. The manuscript's practical contribution is therefore asserted rather than delivered. Remedy: replace the procurement framing with a specification of what evidence would be needed before an investment decision, and state explicitly what this study does not establish.

**Severity**: Major
**Evidence Anchor**: absence: §6 Conclusion — expected implementation conditions, cost or resourcing data, and comparison against alternative retention interventions such as advising or early-alert outreach; checked §1 Introduction, §2 Literature Review, §5 Discussion, §5.1 Limitations, and Table 1
**Confidence**: 4 — procurement and intervention-comparison judgement is my institutional-research responsibility

### W8: The abstract reports a substantially larger headline correlation than the Results section

The abstract gives the engagement-retention correlation as *r* = .42; §4.2 gives it as *r* = .24. These cannot both be right, and the abstract is the surface most institutional readers will act on — the two values differ by roughly a factor of three in variance explained, which is precisely the difference between "modest marginal association" and "substantial effect worth funding." I do not adjudicate which value is correct. Remedy: correct the discrepancy and confirm which figure the Discussion's "modest size" characterisation refers to.

**Severity**: Major
**Evidence Anchor**: text: Abstract and §4.2 Dashboard Engagement and Retention — "Dashboard engagement correlated positively with retention (r = .42)" and "Dashboard engagement was positively associated with course retention (r = .24, p = .004)"
**Confidence**: 5 — direct cross-surface comparison of two reported values

### W9: The sampling frame is described in two incompatible ways within a single subsection

§3.2 opens by describing a random sample of enrolled students and then describes recruitment by open LMS announcement with self-selected respondents, excluding non-responders. These are different sampling frames with different generalisability properties, and the manuscript never reconciles them. Because every transfer claim in §6 depends on knowing which population the 142 students represent, this contradiction has to be resolved before any external-validity statement can be assessed. Remedy: state the actual recruitment procedure, report the response rate against the enrolled cohort, and compare respondents to non-respondents on available characteristics.

**Severity**: Major
**Evidence Anchor**: text: §3.2 Participants and Sampling, sampling frame statement versus recruitment description — "Participants were drawn from the course enrollment using a random sample of students enrolled in the course section" and "Students who chose to respond, and who consented to the survey, formed the study sample"
**Confidence**: 4 — reading and reconciling sampling-frame descriptions is standard institutional-research practice
