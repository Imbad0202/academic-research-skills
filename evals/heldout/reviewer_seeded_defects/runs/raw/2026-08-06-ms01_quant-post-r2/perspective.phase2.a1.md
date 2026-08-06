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
trigger: "Central interdisciplinary or generalising claims are asserted with no supporting evidence, mechanism, or citation"

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I review from a learning analytics ethics and student data governance seat: my questions are whether these data should have been collected and used this way, and whether an institution acting on this manuscript would harm the students the work claims to help. I do not adjudicate the statistical estimates or the field-level novelty; those belong to other seats. I note in passing, without scoring it, that the Abstract reports r = .42 while §4.2 reports r = .24, and that §5 asserts engagement "improved" retention from a cross-sectional design — both matter enormously to how an outside reader receives this paper, and both fall to the methodology and argument seats.

On my own dimension, the manuscript fails in both of the ways I said in advance would be disqualifying, and the two failures compound each other. The first is a scope failure. The Conclusion addresses "higher education institutions worldwide" and recommends dashboard investment as a "dependable strategy" and a "practical and generalizable lever ... at scale." Nothing in the manuscript licenses movement from a single introductory statistics course at one university, observed cross-sectionally in one term, to programmes and disciplines generally. No moderator is tested, no comparison context is reported, no mechanism is offered that would explain why the association should hold in a seminar-based humanities course or a clinical programme, and no citation is supplied to carry the generalisation. §5.1 concedes the single-course limitation and then §6 writes as though the concession had not been made. The second is a construct failure that specifically disables adjacent-field readers. The dashboard is the intervention this paper recommends purchasing, yet it is described in one subordinate clause of §3.1 — engagement metrics, assignment progress, a peer-comparison band — with no interface specification, no metric definitions, no refresh cadence, and no visual. An institutional research office, a procurement committee, or a data protection officer reading this paper cannot determine what was deployed, so cannot determine what to deploy, and cannot assess what they would be exposing students to. A recommendation to invest institution-wide in an object that is never specified is not transferable knowledge; it is an endorsement.

The governance vacuum is the most serious problem in the manuscript and it is not, in my judgement, a presentation defect. §3.2 states that students were not informed that their dashboard activity would be analysed for this study. The survey consent covers the survey; it does not cover the behavioural logs, which are the paper's primary predictor and the basis of its headline claim. There is no ethics or IRB approval statement anywhere in the manuscript, no stated lawful basis for secondary use of trace data under FERPA or GDPR as applicable, no anonymisation or retention description, and no data availability statement. Whether this is remediable depends on facts the manuscript does not supply: if an approval exists and was simply not reported, disclosure plus a lawful-basis statement may suffice; if no approval was obtained and no waiver criteria were assessed, retrospective approval for already-analysed identifiable trace data is not something most review boards can grant, and I do not see how a venue with a human-subjects policy accepts the paper in that case. The authors deserve credit for disclosing the non-notification plainly rather than burying it — that candour is what makes this review possible — but disclosure of a governance gap is not closure of it.

Second, the peer-comparison band is an unmonitored intervention with harm potential documented in this paper's own bibliography. It was delivered to every enrolled student from week one with no opt-in. §2 cites Osei (2020) on discouragement from relative-standing feedback and Ferro & Nakamura (2021) on lower-achieving students, and then §2 characterises the latter as showing that dashboards "reliably improve outcomes for lower-achieving students" — a claim that runs opposite to the source's own title, *When dashboards demotivate: Peer comparison and the lower-achieving student*. The domain seat should adjudicate that citation, but the consequence for my seat is direct: the manuscript's equity rationale for deployment rests on an inverted reading of the single source in its reference list that documents harm to the group retention work targets. Against that, the paper reports no harm monitoring, no subgroup analysis by prior achievement, and no discussion of differential effects; §5.1 names interface variation as a limitation but never differential response. The design also makes the potentially harmed population structurally invisible. Recruitment ran mid-term via an LMS announcement and the sample is composed of students who chose to respond, so students who had already disengaged or withdrawn — precisely those a demotivating peer-comparison band would produce — are the least likely to be in the analytic set. A study cannot evidence the safety of a comparison intervention using a sample from which the plausibly injured are filtered out.

Third, deployment realism. Beyond the missing interface specification, the manuscript offers no cost, staffing, or infrastructure estimate to support "at scale," and its recommended target is directly gameable. If institutions act on "encouraging students to engage," the operational target becomes session counts — the coarse proxy that §2, citing Vandermeer (2023), correctly warns should be treated as a rough indicator rather than a measure of cognitive engagement. Nudging session counts optimises the proxy while leaving learning untouched, and it does so by increasing the salience of monitoring for a student body that, per §3.2, was not told its dashboard activity was being analysed. That combination — undisclosed analysis of trace data plus institutional pressure to generate more of it — is how campus analytics programmes lose student trust, and the manuscript gives an institution no framework for avoiding it.

What would move D4 out of block, briefly: a lawful basis and ethics statement with anonymisation, retention, and data availability terms; an interface specification sufficient for replication; a subgroup analysis by prior achievement with explicit differential-effects discussion and a correction to the Ferro & Nakamura characterisation; and a Conclusion whose scope is a single introductory statistics course rather than the world's institutions. The first of these may not be achievable retrospectively, which is why I record the consent finding as Critical rather than Major.

### S1: Literature Review surfaces the harm and proxy critiques it will later need to answer
**Evidence Anchor**: text: §2 Literature Review "Being shown one's position relative to peers can discourage struggling students rather than mobilize them"
**Confidence**: 5 — this is the ethics-relevant literature I audit routinely, and the citations named are the right ones.

The paper is not ignorant of the terrain. Osei (2020) on discouragement, Vandermeer (2023) on click-based proxies, and Ibarra (2023) on causal overreach are all present. The failure is that these warnings never propagate into the design, the analysis, or the recommendation — but a revision has the material it needs already in hand.

### S2: Candid self-criticism about measurement choices
**Evidence Anchor**: text: §3.3 Measures "This median split is a coarse simplification of a continuous measure and was adopted for interpretability rather than statistical efficiency"
**Confidence**: 4 — judging the honesty of methodological self-report is within my reviewing experience, though the statistical merits are another seat's call.

Alongside the median-split caveat, §3.2's disclosure of non-notification is the kind of statement authors often omit. This transparency is genuinely creditable and is the reason a reviewer can locate the governance problem at all.

### S3: Operational definitions of the two behavioural variables are legible to non-specialists
**Evidence Anchor**: text: §3.3 Measures "A session was defined as a dashboard view preceded by at least thirty minutes of inactivity"
**Confidence**: 4 — I assess construct legibility for institutional and ethics-panel audiences regularly.

Engagement and retention are each defined concretely enough that an adjacent-field reader knows what was counted. This makes the contrast with the wholly unspecified dashboard interface sharper, not softer.

### W1: Behavioural trace data analysed without informing students, with no ethics approval or lawful basis stated
**Severity**: Critical
**Evidence Anchor**: text: §3.2 Participants and Sampling "Students were not informed that their dashboard activity data would be analyzed for this study."
**Confidence**: 5 — consent architecture for secondary use of LMS trace data is my primary professional competence.

The survey consent does not extend to the logs, and the logs carry the paper's headline claim. This defect alone, uncorrected, makes acceptance impossible at any venue with a human-subjects policy, independent of every other finding here: the central result rests on data the authors state were used without participant knowledge. Whether it is repairable turns on facts not in the manuscript — an existing but unreported approval is a disclosure fix, whereas no approval at all is not curable retrospectively for identifiable trace data already analysed. I flag it as Critical because the paper as submitted gives an editor no basis to conclude the former.

### W2: The entire data-governance reporting apparatus is missing
**Severity**: Major
**Evidence Anchor**: absence: §3 Methods and manuscript end matter — expected an ethics or IRB approval statement, a stated lawful basis for secondary use of trace data such as FERPA or GDPR as applicable, anonymisation and retention terms, and a data availability statement; checked §3.1, §3.2, §3.3, §3.4, §4, §5.1, §6, and the reference list
**Confidence**: 5 — these are the exact artefacts I require of campus deployments and check as a reviewer for institutional research ethics panels.

Set aside the consent question in W1: even a fully consented study reported this way could not be accepted, because a reader cannot tell who approved it, on what legal basis the logs were reused, how long identifiable records are held, or whether any data can be inspected. This requires substantive new material rather than re-analysis, and the core association claim survives its addition, which is why it is Major and not Critical on its own.

### W3: Peer-comparison feedback deployed to all students with no opt-in and no harm monitoring
**Severity**: Major
**Evidence Anchor**: text: §3.1 Design and Setting "a peer-comparison band"; "available to all enrolled students from the first week of the term and required no separate opt-in"
**Confidence**: 5 — I have halted dashboard pilots specifically over peer-comparison harm and reviewed the monitoring protocols that should accompany them.

Relative-standing feedback was an unavoidable condition of enrolment for a full lecture cohort. No harm indicator was collected, no subgroup analysis by prior achievement was run, no differential-effects discussion appears in §5 or §5.1, and the paper proceeds to recommend the arrangement for worldwide adoption. The core correlational finding can survive; the deployment recommendation cannot without a subgroup analysis and an explicit differential-harm treatment, so this is Major.

### W4: The equity rationale for deployment rests on a source that reports the opposite
**Severity**: Major
**Evidence Anchor**: text: §2 Literature Review "Dashboards have been shown to reliably improve outcomes for lower-achieving students"; "When dashboards demotivate: Peer comparison and the lower-achieving student"
**Confidence**: 4 — the mismatch between claim and cited title is legible on the manuscript's face, though I cannot read the source text to confirm its findings.

§2 attributes a reliable benefit for lower achievers to Ferro & Nakamura (2021), whose listed title describes demotivation of exactly that group, and §2 states the paper will "return to it in the Discussion" — where the favourable reading duly reappears. The domain-accuracy seat owns the citation adjudication; for my purposes the consequence is that the paper's stated equity justification for institutional rollout may invert its only harm-documenting source. Correcting it requires rewriting §2, §5, and §6 while the retention association itself stands, hence Major.

### W5: The population most at risk of harm is structurally excluded from the sample
**Severity**: Major
**Evidence Anchor**: text: §3.2 Participants and Sampling "Students who chose to respond, and who consented to the survey, formed the study sample; those who did not respond were excluded."
**Confidence**: 4 — self-selection effects on who can appear in retention samples are central to my rollout-evaluation work, though the sample-composition arithmetic is Reviewer 1's to settle.

Recruitment occurred midway through the term and depended on students volunteering. Students already disengaged, demoralised, or withdrawn are the least likely respondents and the most likely to have been harmed by relative-standing feedback. The design therefore cannot speak to harm in either direction, and any safety inference drawn from the absence of visible harm is unavailable. Remedy requires either whole-cohort log data or an explicit statement that harm is unmeasurable in this design; the core claim survives that revision, so Major.

### W6: The deployment being recommended is never specified, and no resourcing estimate supports "at scale"
**Severity**: Major
**Evidence Anchor**: absence: §3.1 and §6 — expected an interface specification of the deployed dashboard covering displayed metrics, visual design of the peer-comparison band, and refresh cadence, together with cost, staffing, and infrastructure requirements for the recommended scale-up; checked §3.1 Design and Setting, §3.3 Measures, §4 Results, §5.1 Limitations, and §6 Conclusion
**Confidence**: 5 — advising campus deployments on feasibility is my institutional role, and these are the inputs a rollout decision actually needs.

§5.1 half-concedes the problem by noting that "the specific dashboard design used here differs from those deployed elsewhere," which is precisely why the interface must be documented. Without it the study is not replicable and the recommendation is not transferable; without any resourcing figures, "at scale" is rhetorical. Both are addable in revision, so Major rather than Critical.

### W7: Global transfer claims asserted without evidence, mechanism, or citation
**Severity**: Major
**Evidence Anchor**: text: §6 Conclusion "For higher education institutions worldwide, the implication is clear"; "practical and generalizable lever for supporting student success at scale"
**Confidence**: 5 — assessing whether stated implications are scaled to the evidence is the core of this dimension.

One course, one term, one institution, one cross-sectional design, and a modest association do not support claims about institutions worldwide or about transfer across programmes and disciplines. No moderator, comparison setting, mechanism, or supporting citation is offered. This is the primary driver of my block on D4, and it is repairable by rescaling the Conclusion to the studied context, which is why the finding itself is Major.

### W8: The recommended target is directly gameable and raises surveillance exposure
**Severity**: Major
**Evidence Anchor**: text: §6 Conclusion "encouraging students to engage with them is a dependable strategy"
**Confidence**: 4 — proxy-optimisation and student trust effects are recurring problems in the deployments I advise, though the size of the effect here is untested.

An institution operationalising this advice will set session-count targets, because sessions are what the paper measured. That optimises the click proxy Vandermeer (2023) is cited as warning against, while intensifying monitoring of students who were never told their dashboard activity was analysed. The actionability claim in §6 is materially weakened until the manuscript distinguishes engagement worth encouraging from engagement merely counted; that requires substantial rewriting, so Major.

### W9: Field-specific vocabulary left unglossed for the institutional audience the paper addresses
**Severity**: Minor
**Evidence Anchor**: text: §3.3 Measures "following the platform's default sessionization rule"
**Confidence**: 4 — I routinely translate learning analytics reports for ethics panels and institutional committees.

Terms such as sessionization, performance-avoidance orientation, and self-regulated learning phases are used without definition, and no gloss is offered for the platform default being relied on. §6 addresses institutional decision-makers, who will typically not be learning analytics specialists. This lowers usability without changing any core claim, so Minor.
