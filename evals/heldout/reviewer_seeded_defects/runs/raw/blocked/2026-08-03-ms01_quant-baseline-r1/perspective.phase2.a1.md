## Scoring Plan Dissent

*(none — omitted)*

Wait — that placeholder is not permitted. Disregard the two lines above; no dissent section is emitted.

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
trigger: "Central interdisciplinary or generalisation claims are asserted without supporting evidence or scope conditions, or core constructs are left so undefined or inconsistently used that an adjacent-field reader cannot determine what was measured"

Both prongs of the block condition fire independently. The Conclusion's central claim reaches "higher education institutions worldwide" and "across programs and disciplines" from one lecture section of one introductory statistics course in one term, with no scope conditions attached and with causal phrasing the design cannot license. Separately, the intervention itself — the dashboard — is a core construct left effectively undefined: a single clause naming three feature categories, with no specification of what the peer-comparison band compares, at what granularity, on what update cadence, or with what accompanying framing. An adjacent-field reader (my own field is information science and HCI) therefore cannot determine what was actually experienced by these students, and consequently cannot determine what the finding would mean in any other setting.

### D5: writing_and_structure

score: not_assessed

### D6: venue_fit_and_contribution

score: not_assessed

## Review Body

I read this manuscript from the vantage point of learning-analytics ethics and data governance, with a secondary interest in whether an interface study specifies its interface well enough for anyone outside the authors' institution to use the result. The manuscript's prose is clear and its literature review is more candid than most in this area. That candour is precisely what makes the paper's end-state so difficult to accept: the authors demonstrably know about the harm mechanism, the proxy-measurement problem, and the causal-language problem, name all three in Section 2, then commit each of them by Section 6.

**The governance record is not merely incomplete; Section 3.2 discloses an ethics violation.** Consent was obtained for a survey about study habits. Behavioural logs were then extracted for those same identified individuals and linked to individual academic outcomes including withdrawal and final-exam scores. The manuscript states, without evident discomfort, that students were not informed of this. Under the ethics policies of every information-science and edtech venue I review for, and under FERPA-aligned institutional practice, that is unconsented secondary use of identifiable educational records, and the disclosure functions as an admission rather than a limitation. There is no ethics-committee approval statement, no data-protection statement, no data-availability statement, and no account of how the survey and log records were linked or whether the linked file was ever de-identified. A linkage of consent-bearing survey responses to non-consented trace data necessarily passes through identifiers, and the manuscript never says who held them or under what authority. My honest reading is that this is not publishable as written. It may be *remediable* — if a protocol and approval exist and were simply omitted, or if a waiver of consent for retrospective log analysis was granted, the paper's ethics posture changes materially. I want the synthesizer to hold that distinction open: my Critical here is a claim about the record as submitted, not a claim that no version of this study could be ethical.

**The interface is missing, and with it the paper's stated contribution.** Section 3.1 gives the dashboard one clause. Section 5.1 then concedes that "the specific dashboard design used here differs from those deployed elsewhere" — an admission that design specifics matter — and Section 6 nonetheless recommends investment in student-facing dashboards as a category. From an HCI standpoint this is the study's structural failure: a single unspecified artifact cannot license a recommendation about a class of artifacts, and without a screenshot, wireframe, or feature specification, no one can build the thing that produced r = .24, let alone test whether their own dashboard is the same intervention. The paper's self-description as offering a "generalizable lever" is therefore not merely overstated; it is unfalsifiable, because the lever is not described.

**The cross-disciplinary warrant is an assertion.** The only textual basis for the claim that findings extend "across programs and disciplines" is the observation that the course served students from a range of majors. No major-level data are reported, no by-discipline breakdown appears in Tables 1 or 2, and no analysis tests whether the association differs across student groups. An adjacent-field reader is asked to accept disciplinary transfer on the strength of the sample's presumed heterogeneity — which, absent any subgroup evidence, is an argument for *unmeasured* variation, not for generalisability.

**The peer-comparison band is the paper's unexamined risk, and the recommendation to scale it up is the consequence.** Section 2 states the mechanism: performance-avoidance students may read an unfavourable comparison as a threat and disengage from the interface meant to re-engage them. Osei (2020) is cited for discouragement effects. The Results then contain no differential-effects analysis, no examination of the low-engagement group's outcomes beyond a mean comparison, and no attempt to ask whether the students who left were the ones the band discouraged. Recommending institution-wide deployment while the harm channel your own citations identify sits unmeasured is, in my view, a responsibility failure independent of the statistical questions. I would add that the manuscript never names the surveillance dimension of what it describes: analytics-driven institutional attention to individual persistence, derived from behaviour students did not know was under study. That framing is standard in information science and its absence will read as naivety to that readership.

**The most consequential silence is about who is absent.** Recruitment happened midway through the term via an LMS announcement; the analytic sample consists of volunteers who responded, and logs were pulled for that same set. Students who had already withdrawn before the recruitment window could not respond, so the retention outcome is partly conditioned on the very survival it purports to predict. Non-respondents are excluded without comparison. The fifty-five respondents who skipped the perceived-control item are excluded without a missingness analysis. Every one of these excluded groups is plausibly the group the intervention failed. The scale-up recommendation rests entirely on the students who stayed. That is where the finding should have been stress-tested, and it is the one place the manuscript does not look.

I also flag several internal numerical inconsistencies below. I am reporting them because I found them, not because I claim statistical adjudication; the methodology seat should own whether they are typographical or substantive. I note that the abstract's r = .42 against the Results' r = .24 is a discrepancy any reader can check, and that it inflates the paper's headline effect by roughly a factor of three in variance explained.

### S1: Literature review names the harm mechanism in terms an outsider can use

The treatment of goal orientation and relative-standing feedback is specific, mechanistic, and legible without motivation-psychology training. An adjacent-field reader can extract a testable prediction from it. This is genuine cross-disciplinary craft, and it is why the absence of any corresponding analysis is so conspicuous.

**Evidence Anchor**: text: §2 "Performance-avoidance oriented students, in particular, may interpret an unfavorable comparison as a threat to be avoided rather than a problem to be solved"

### S2: Operationalisations are stated concretely rather than in field shorthand

The sessionization rule, the dichotomous retention coding, and the exact perceived-control item wording are all given. A reader from another field can see precisely what was counted. This is better practice than much of the dashboard literature and makes the *measures* replicable even though the *intervention* is not.

**Evidence Anchor**: text: §3.3 "A session was defined as a dashboard view preceded by at least thirty minutes of inactivity"

### S3: The manuscript self-flags its own analytic simplifications

Naming the median split as a coarse choice adopted for interpretability, rather than defending it as optimal, is the kind of reflexive candour that lets an outside reader calibrate trust. It also establishes that the authors are capable of the restraint the Conclusion abandons.

**Evidence Anchor**: text: §3.3 "This median split is a coarse simplification of a continuous measure and was adopted for interpretability rather than statistical efficiency."

### W1: Behavioural trace data were analysed and linked to individual outcomes without informing the data subjects

Consent covered a study-habits survey. Dashboard logs for the same identified students were then extracted and joined to individual retention and exam outcomes. The manuscript states outright that students were not told this would happen. Under standard journal ethics policy and FERPA-aligned institutional practice this is unconsented secondary use of identifiable educational records, and no waiver, protocol, or approval is cited that would authorise it. As submitted, this bars acceptance regardless of the paper's analytic merits; it is potentially remediable if an approved protocol exists and was omitted from the write-up.

**Severity**: Critical
**Evidence Anchor**: text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study."
**Confidence**: 5 — routine reviewer for information-science venues; direct research on informed consent for educational trace data.

### W2: The Conclusion's universal, causal recommendation is unsupported by the design and contradicts the paper's own stated care

Section 1 promises to distinguish pattern from causal story. Section 5 then asserts that engagement "improved" retention and that increasing engagement "raises the probability" of completion. Section 6 escalates to a worldwide, all-programs, "dependable strategy" recommendation. No causal identification strategy exists anywhere in the manuscript; the design is explicitly cross-sectional and correlational, and Section 5.1 concedes single-course, single-design scope. The headline claim, as written, is invalid on the paper's own evidence, and it is the claim readers and administrators will act on. Whether this also constitutes a coherence failure is for the devil's-advocate and methodology seats to score; I register it as the load-bearing overreach on cross-disciplinary relevance.

**Severity**: Critical
**Evidence Anchor**: text: §5 and §6 "dashboard engagement improved course retention"; "investing in student-facing dashboards and encouraging students to engage with them is a dependable strategy for improving retention across programs and disciplines"
**Confidence**: 5 — the contradiction is fully on the page and requires no domain adjudication.

### W3: No ethics-approval, data-protection, or data-availability statement, and no account of record linkage or de-identification

Beyond the consent problem itself, the manuscript contains none of the governance apparatus that information-science and edtech venues require. Most consequentially, a study that joins consent-bearing survey responses to non-consented logs for the same individuals must have handled identifiers, and the manuscript never states who held them, under what authority, whether the linked analytic file was de-identified, or where the data now reside. Remedying this requires substantial new documentation, not a sentence.

**Severity**: Major
**Evidence Anchor**: absence: manuscript front and back matter and §3 Methods — expected ethics-committee approval, consent, data-availability, and data-protection statements plus a described log-survey linkage and de-identification procedure; checked Abstract, §3.1, §3.2, §3.3, §3.4, §5.1, §6, References
**Confidence**: 5 — advises a university learning-analytics governance committee; these are the standard required elements.

### W4: The intervention artifact is described in one clause, making the study unreplicable and its class-level claim untestable

Three feature categories are named. Nothing is said about what the peer-comparison band compares (cohort? section? prior-term norm?), at what granularity, how often it refreshes, what framing text surrounds it, or whether students could dismiss it. No screenshot, wireframe, or interface specification is provided. A reader cannot reconstruct the intervention, cannot judge whether their own dashboard is the same treatment, and therefore cannot test the paper's central recommendation about dashboards as a category. Repair requires adding a full artifact specification and narrowing every class-level claim accordingly.

**Severity**: Major
**Evidence Anchor**: text: §3.1 "included a student-facing learning analytics dashboard displaying engagement metrics, assignment progress, and a peer-comparison band"
**Confidence**: 5 — HCI background; interface-specification and replication norms are directly within competence.

### W5: The cross-disciplinary generalisation rests on an asserted "disciplinary breadth" that is never evidenced

The manuscript's only warrant for extending findings across programs and disciplines is the claim that the course drew a range of majors. Major is never reported as a variable, never appears in Tables 1 or 2, and is never used in any analysis. Unmeasured heterogeneity is offered where measured transfer evidence is needed. Repair requires either reporting and analysing discipline-level variation or deleting the cross-disciplinary claim.

**Severity**: Major
**Evidence Anchor**: text: §3.1 "served as a required quantitative-reasoning course for a range of majors, giving the sample some disciplinary breadth even within one course"
**Confidence**: 4 — reading of the generalisation warrant; a discipline variable may exist in data not reported here.

### W6: A harm mechanism the paper itself cites went unmeasured, yet institution-wide deployment is recommended

Section 2 identifies discouragement and disengagement risk for performance-avoidance students facing relative-standing feedback. The Results contain no differential-effect analysis, no examination of whether the peer-comparison band was associated with worse outcomes for any subgroup, and no analysis of the non-retained students. Recommending scale-up on this evidence base asks institutions to deploy at scale an intervention whose plausible harm channel the authors named and then declined to test. Repair requires new analysis of subgroup and non-retained outcomes, and withdrawal of the deployment recommendation pending it.

**Severity**: Major
**Evidence Anchor**: absence: §4 Results and §5 Discussion — expected differential-effect or harm analysis for low-engagement and performance-avoidance students exposed to the peer-comparison band; checked §4.1, §4.2, §4.3, Tables 1-2, §5, §5.1, §6
**Confidence**: 4 — empirical work on how peer-comparison bands affect performance-avoidance learners.

### W7: The retention outcome is conditioned on mid-term survival and on volunteering

Recruitment occurred midway through the term through an LMS announcement, and logs were pulled only for respondents. Students who withdrew before the recruitment window could not enter the sample, so the outcome variable is partly determined by the sampling frame. Non-respondents are excluded with no comparison on any observable. The paper simultaneously describes the sample as drawn by random sampling and as self-selected volunteers, which cannot both be true. Repair requires a full-cohort design or, at minimum, an explicit selection analysis and a heavily narrowed claim. I leave the magnitude of the resulting bias to the methodology seat.

**Severity**: Major
**Evidence Anchor**: text: §3.2 "Midway through the term, an announcement was posted to the course LMS inviting students to complete a short survey"; "those who did not respond were excluded"
**Confidence**: 4 — sampling-frame reasoning is within competence; bias magnitude not independently modelled.

### W8: The abstract reports a substantially larger correlation than the Results section

The abstract gives r = .42; Section 4.2 gives r = .24. These cannot both describe the same association, and the abstract is what most readers and most institutional decision-makers will see. Correction is mandatory, and if .24 is the correct value the "promising lever" framing weakens further.

**Severity**: Major
**Evidence Anchor**: text: Abstract and §4.2 "Dashboard engagement correlated positively with retention (r = .42)"; "Dashboard engagement was positively associated with course retention (r = .24, p = .004)"
**Confidence**: 5 — direct textual comparison requiring no statistical expertise.

### W9: Sample accounting across the Results section cannot be reconciled, and the 55 missing perceived-control responses are never analysed

Section 4.1 reports 87 respondents to the perceived-control item, yet Section 4.3's group comparison on that item reports 156 degrees of freedom, implying 158 cases — more than the 142-student analytic sample. Section 4.3 also states that all 142 students were classified into engagement groups for the exam comparison, while Table 2 lists 66 plus 61, or 127. Fifty-five students are dropped from the perceived-control analysis with no missingness comparison, despite the plausible possibility that non-responders differed in exactly the perceived control being measured. A reader cannot determine which N underlies which reported result. I defer to the methodology seat on whether these are transcription errors or evidence of undisclosed exclusions.

**Severity**: Major
**Evidence Anchor**: text: §4.1 and §4.3 "The mean perceived-control score across the 87 survey respondents who answered the item was 3.847"; "t(156) = 3.02, p = .003"
**Confidence**: 3 — the arithmetic is checkable, but statistical adjudication belongs to the methodology reviewer.

### W10: Surveillance, data-subject rights, and governance preconditions for deployment are never named

The manuscript recommends institutional deployment of an interface that reflects individually derived behavioural comparisons back to students, and that generates data the institution uses to track individual persistence. It never names the surveillance dimension of that arrangement, never mentions student access, correction, or opt-out rights, and never states governance preconditions an institution should satisfy before scaling. For an information-science or governance readership this omission will read as a gap in disciplinary awareness rather than a deliberate scoping choice. Adding a governance-preconditions paragraph would improve the paper without altering its empirical claims.

**Severity**: Minor
**Evidence Anchor**: absence: §1, §5, and §6 — expected explicit treatment of surveillance, learner data-subject rights, or governance preconditions for institution-wide dashboard deployment; checked Abstract, §1, §2, §3.1, §5, §5.1, §6
**Confidence**: 4 — data-governance framework design is a primary research area.
