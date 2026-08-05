## Scoring Plan Dissent

*(omitted — Phase 2 findings fall within the Phase 1 plan for D4)*

Wait — per protocol, no dissent applies; the heading above is withdrawn and no dissent card is emitted.

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
trigger: "the paper's headline implications extend to populations, institutions, disciplines, or policy decisions well outside the studied setting with no evidence or hedging offered to support that extension"

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I read this manuscript from a learning analytics ethics and educational data governance seat: my question is not whether the correlation is computed correctly but what happens if an institution actually does what the Conclusion tells it to do, and whether the study itself stayed inside the boundaries students were told about. On both counts the manuscript has problems that additional statistical polish will not repair.

Start with the sentence that ends §3.2. The authors write that students were not informed their dashboard activity data would be analysed for this study, while §3.2 also states that the sample consists of those who "consented to the survey." That is a consent-scope mismatch stated in the manuscript's own voice: survey consent was obtained; trace-data consent was not. There is no ethics approval statement, no IRB determination, no waiver rationale, no legal-basis or data-protection framing, and no declarations section anywhere in the paper. I cannot tell from the text whether this is a disclosure failure (approval and a waiver exist but were not written up) or a conduct-of-research failure (behavioural logs were pulled for research purposes outside any approved protocol). That distinction decides whether the item is fixable in revision, and the authors are the only people who can resolve it. Any journal I have advised would require, before further review: the approving body and protocol number, the waiver or exemption basis for the log analysis, the retention and de-identification arrangements for the extracted logs, and the text of whatever notice students did receive about LMS analytics. I flag this here because it is the most consequential thing in the manuscript, while noting that it binds to a mandatory dimension owned by the methodology seat rather than to my own D4 score.

My scored dimension turns on two things. The first is construct drift across audiences. "Retention" is defined tightly and well in §3.3 as remaining enrolled and completing the final assessment in one 15-week course. By §6 the same word is doing policy work: retention "across programs and disciplines," "student success at scale." Those are different constructs. A higher-education policy reader, an institutional research officer, or a provost reads "retention" as term-to-term or degree persistence, which this study did not measure and could not have measured with a single-course cross-section. The second is the reach of the recommendation. The Conclusion addresses institutions worldwide, calls dashboard investment "dependable" and the lever "generalizable," and does so on one course, one term, one dashboard design, one institution, with a correlational design the authors themselves describe as cross-sectional. The paper's own §5.1 says the opposite — single course, dashboard-specific interface effects, wider designs needed in future work — and then §6 proceeds as if §5.1 were not there. This is not a hedge that needs strengthening; it is a recommendation that needs withdrawing and rebuilding at the scope the evidence supports.

The equity story deserves separate attention because the manuscript inverts it. §2 tells readers that dashboards "reliably improve outcomes for lower-achieving students" and attributes this to Ferro & Nakamura (2021) — a source whose title in the reference list is "When dashboards demotivate: Peer comparison and the lower-achieving student." The paper then names this as the basis for "the equity-oriented rationale for institutional dashboard deployment." Whichever reading of that source is correct is R2's call, but the cross-disciplinary claim built on it is mine: an equity claim about who benefits from an intervention containing a peer-comparison band, offered to an audience of institutional decision-makers, with no subgroup analysis, no differential-effect test, and no discussion of who might be harmed. §2 itself describes performance-avoidance students disengaging from the interface intended to re-engage them. The paper documents the harm mechanism and then recommends institution-wide encouragement without testing for it.

Finally, a practitioner-feasibility point the manuscript never confronts. The recommended action is to encourage students to engage with the dashboard; the engagement measure is session counts under a thirty-minute sessionization rule. Once an institution encourages the behaviour, the metric stops being the passive indicator whose association with retention was observed and becomes a target students and advisors can hit directly. The observational association gives no warrant that a session count driven up by exhortation carries the same relationship to persistence. Combined with the total absence of cost, staffing, advising-capacity, or comparison-with-alternatives content, there is nothing here a real institution could responsibly act on, even setting the ethics issue aside.

### S1: Retention is operationally defined in terms an outside reader can apply
The dichotomous coding rule is stated concretely enough that an adjacent-field reader can see exactly what "retained" means in the data and can judge for themselves whether it maps onto their own institution's retention definitions. This is better practice than much of the dashboard literature.
**Evidence Anchor**: text: "coded dichotomously as whether the student remained enrolled and completed the final assessment"

### S2: The engagement measure is specified reproducibly at the platform level
The sessionization rule is named rather than assumed, which lets a reader from information science or HCI reconstruct the measure and assess its known failure modes.
**Evidence Anchor**: text: "A session was defined as a dashboard view preceded by at least thirty minutes of inactivity"

### S3: The literature review surfaces the discouragement mechanism in accessible language
§2 explains the goal-orientation pathway to demotivation without requiring prior grounding in achievement-goal theory, which is exactly the kind of translation that makes a paper usable to adjacent fields. The problem is that §5 and §6 then ignore it.
**Evidence Anchor**: text: "Performance-avoidance oriented students, in particular, may interpret an unfavorable comparison as a threat to be avoided rather than a problem to be solved"

### S4: Limitations names the single-course and single-design constraint plainly
The constraint is stated without euphemism, giving reviewers and readers the correct scope boundary. It is the Conclusion that contradicts it, not the Limitations section that hides it.
**Evidence Anchor**: text: "the study was conducted within a single introductory statistics course, and the specific dashboard design used here differs from those deployed elsewhere"

### W1: Behavioural trace data analysed beyond the disclosed consent scope
Participants consented to a survey; their dashboard activity logs were extracted and analysed without being told. On its own, uncorrected, this makes publication impossible at any venue with a research-ethics policy, irrespective of how sound the analysis is, because the data underlying the headline finding were obtained outside the disclosed purpose. Remedy requires the authors to establish, on the record, the approval and waiver status of the log analysis; if none exists, this is a conduct-of-research matter rather than a revision item.
**Severity**: Critical
**Evidence Anchor**: text: "Students were not informed that their dashboard activity data would be analyzed for this study."
**Confidence**: 5 — I sit on an institutional review board and have drafted student-facing transparency notices for LMS trace-data research

### W2: No ethics approval, waiver rationale, or data-protection statement anywhere in the manuscript
Independently of W1, the manuscript contains no approving-body identification, no exemption or waiver basis, no de-identification or retention description, and no declarations section. Even if approval exists, its absence prevents any reviewer or reader from assessing the governance basis of the dataset, and prevents an institution from judging whether it could lawfully replicate the study.
**Severity**: Major
**Evidence Anchor**: absence: Methods §3.2 and the manuscript front and back matter — expected an ethics approval or IRB determination statement with consent-waiver rationale, data-protection basis, and log retention and de-identification arrangements; checked §3.1, §3.2, §3.3, §3.4, §5.1, the full section list §1 through §6, and the References
**Confidence**: 5 — this is the documentation set I request as an IRB member and advise on for institutional analytics deployments

### W3: "Retention" drifts from single-course completion to institutional and programme-level persistence
The measured construct is completing one final assessment in one course. The stated implications concern retention across programmes and disciplines and student success at scale, which are the constructs adjacent-field readers in higher-education policy will hear. Every implication claim must be re-labelled to the measured construct, and the claims that cannot survive that re-labelling removed.
**Severity**: Major
**Evidence Anchor**: text: "offer institutions a practical and generalizable lever for supporting student success at scale"
**Confidence**: 4 — I work with institutional retention definitions and reporting in a university system context

### W4: Global, unconditional recommendation unsupported by a one-course, one-term, one-dashboard cross-section
The Conclusion addresses institutions worldwide and characterises the strategy as dependable, with no evidence for transportability across institutions, dashboard designs, disciplines, or student populations, and in direct contradiction of §5.1. Repair means restating the contribution as a single-site correlational observation and deleting the worldwide-deployment advice, not softening it with an additional caveat.
**Severity**: Major
**Evidence Anchor**: text: "For higher education institutions worldwide, the implication is clear"
**Confidence**: 5 — this is the generalisation pattern I evaluate professionally when institutions cite external studies as deployment warrant

### W5: The equity rationale for deployment contradicts the source it cites and is never tested
The claim that dashboards reliably improve outcomes for lower-achieving students, presented as the equity basis for institutional deployment, is attributed to a source whose title indicates a demotivation finding, and no data in this study bear on differential benefit. An interdisciplinary equity claim addressed to decision-makers must be substantiated, not asserted. The citation-direction question itself belongs to the domain seat; the unsubstantiated policy claim built on it is my finding.
**Severity**: Major
**Evidence Anchor**: text: "Dashboards have been shown to reliably improve outcomes for lower-achieving students" and "This position underpins much of the equity-oriented rationale for institutional dashboard deployment"
**Confidence**: 4 — equity-impact assessment of analytics interventions is central to my advisory work; I have not independently obtained the cited source

### W6: No differential-effect or subgroup analysis for an intervention containing a peer-comparison band
The dashboard displays relative standing; the paper's own literature review documents discouragement and disengagement risks concentrated in lower-achieving and performance-avoidance students; the analysis reports only pooled correlations and a median-split comparison. Without differential-effect testing, the recommendation to encourage engagement institution-wide could plausibly harm the students the paper says it wants to help. This requires new analysis of the existing data, at minimum stratified by prior achievement.
**Severity**: Major
**Evidence Anchor**: absence: §4 Results and §5 Discussion — expected a differential-effect or subgroup analysis by prior achievement and goal orientation for a dashboard containing a peer-comparison band; checked Table 1, Table 2, §4.1, §4.2, §4.3, §5, and §5.1
**Confidence**: 5 — harm-profile analysis of relative-standing feedback is squarely within my area

### W7: Encouraging engagement converts the observed indicator into a target, invalidating the recommendation's warrant
The recommended action operates directly on the measure whose passive association with retention was observed. Session counts driven up by institutional exhortation carry no demonstrated relationship to persistence, and the measure is trivially inflatable under the stated sessionization rule. The manuscript nowhere acknowledges this, which leaves its central practical claim resting on a step the design cannot license.
**Severity**: Major
**Evidence Anchor**: text: "encouraging students to engage with them is a dependable strategy" and "the number of distinct sessions in which a student opened the dashboard view"
**Confidence**: 4 — indicator-corruption under incentive is a standard failure mode in institutional metric deployment

### W8: Nothing actionable for the practitioner audience the Conclusion addresses
The paper advises investment without cost figures, staffing or advising-capacity requirements, implementation timeline, or any comparison against alternative retention interventions, including the intervention review the manuscript's own reference list contains. An administrator cannot act on this, and adding the missing content would materially raise the manuscript's usefulness without altering its empirical claims.
**Severity**: Minor
**Evidence Anchor**: absence: §6 Conclusion — expected cost, staffing and advising-capacity requirements, and comparison against alternative retention interventions such as the gateway-course intervention review the paper cites; checked §5, §5.1, §6, and the References
**Confidence**: 4 — I advise on comparative business cases for institutional analytics investment

### W9: Data provenance for the log extraction is not reconstructable
The analytic population is stated inconsistently across the manuscript, so a governance reviewer cannot determine whose trace data was actually processed or how many students' logs were extracted. That question is prior to the statistics: it determines the scope of the undisclosed secondary use in W1. The arithmetic and reporting defects themselves are for the methodology seat to band; the provenance ambiguity is what I record here.
**Severity**: Minor
**Evidence Anchor**: text: "A total of 142 students provided complete behavioral log and retention data" and "t(156) = 3.02"
**Confidence**: 3 — I do not verify statistical computation; my basis is data-inventory practice for trace-data protocols

### W10: The abstract reports a different headline effect size from the Results
The abstract gives one correlation and §4.2 gives a materially smaller one. The abstract is the only surface most cross-disciplinary and practitioner readers will ever see, and it also carries lever-language absent from the Results. Whichever value is correct, outside readers are currently being given a stronger finding than the paper reports. The determination of which figure is right belongs to the methodology and domain seats.
**Severity**: Major
**Evidence Anchor**: text: "Dashboard engagement correlated positively with retention (r = .42)" and "Dashboard engagement was positively associated with course retention (r = .24, p = .004)"
**Confidence**: 4 — reading abstracts as institutional decision surfaces is core to my advisory role
