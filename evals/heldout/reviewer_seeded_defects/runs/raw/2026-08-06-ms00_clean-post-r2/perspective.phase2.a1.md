## Scoring Plan Dissent

*(omitted — no dimension requires dissent)*

Actually, per protocol this section must be absent when there is no dissent. Disregard the line above and treat the report as beginning below.

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
trigger: "unstated scope conditions, or implications framed more broadly than the presented support warrants in ways fixable by revision"

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I read this as the person who would have to act on it: I run the LMS engagement dashboards and the digital-equity reporting at a public university, and I have the log data and the survey infrastructure the authors say they lack. My question is not whether r = .42 is correctly estimated — that belongs to the methodology reviewer — but whether an adjacent-field reader in institutional research, learning analytics, or student-success practice can tell what this finding applies to and what to do with it. On the first count the paper is unusually disciplined; on the second it falls short in a way that is fixable by revision rather than fatal.

The paper's accessibility fundamentals are sound. LMS is expanded at first use, perceived usefulness is defined conceptually before it is operationalised, the analysis is reported with enough completeness (coefficient, CI, p, n, non-parametric robustness check, prospective power) that an outsider can judge precision without recomputation, and the correlational register is sustained from abstract to conclusion rather than loosening in the Discussion. Nothing here is hermetic. The manuscript also does not over-claim theoretical reach: it explicitly declines to test an acceptance model. That combination is rarer than it should be in this literature, and it is why the dimension is a warn and not a block — the core content transfers, and what does not transfer is the paper's account of *to whom* it transfers.

That account has a specific hole. The survey went out through the institution's course-announcement channel, which is a feature of the platform whose use is the dependent variable. Students who rarely open the LMS are structurally less likely to have seen the invitation. The paper's Limitation 4 records generic volunteer bias and even notes that students engaged with institutional channels may be overrepresented, but it never says that the channel *is* the system under study, so it never reaches the consequence: the sample is thinned exactly at the low end of the outcome. For a reader deciding whether to port this finding to their own campus, that is the single most important boundary condition, and it is unstated. It is also cheaply repairable, and the repair is one this institution can perform — a comparison of respondents' log-activity distribution against the enrolled population would convert an unstated scope condition into a quantified one, without requiring individual-level linkage that anonymity forbids.

The second gap is decision utility, which is where implications reaching outside the home subfield have to earn their keep. The abstract advertises implications for LMS onboarding and Section 5 delivers one: onboarding that helps students see concrete usefulness may be worth institutional attention. I already believed that before reading the paper, and so does every practitioner citation in this space. What the study would need to add is a decision-relevant contrast — what a provost or platform owner should do differently at r = .42 that they would not do at r = .25 or r = .60. No such threshold is offered or even acknowledged as missing, and the single practitioner reference (Whitfield, 2019) is invoked rather than engaged. The honest revision is to restate this as a hypothesis for intervention work, not as an implication of these data.

The third gap is the one I care about most, and it is a framing assumption rather than an error. The paper treats variation in engagement as a perception phenomenon end to end. Nowhere — not in the Introduction, not in the Discussion's list of competing influences, not in Limitations — does it entertain that low LMS use might reflect device access, connectivity, off-campus study, employment or caregiving load, disability and accessibility barriers, or the platform's own usability. Section 4 gestures at "many influences beyond perceived usefulness" and names only course requirements and assessment schedules. This matters because the population the paper's recommendation is aimed at is precisely the low-engagement students who are least likely to be in the sample, and locating their non-use in perception routes institutional money toward messaging rather than provision. An adjacent-field reader in digital equity or accessibility would not recognise their field's evidentiary considerations as having been engaged, even though the paper's practical claim lands in their territory.

Finally, a smaller transferability point that practitioners will notice immediately: the paper calls for behavioural log data as future work while demonstrating that the institution has a live platform and administrative access to it. Whether the obstacle was governance, IRB scope, anonymity commitments, or analyst capacity is exactly the information a reader needs in order to judge whether their own setting could do better. Stating it turns a soft limitation into a credible account of design tradeoffs.

One note in my own disfavour: my instinct is to ask for the study I would have run — logged behaviour, equity covariates, a sampling frame independent of the platform. That is not the standard here. Everything I flag above is answerable inside the manuscript the authors actually produced, by stating conditions and reframing an implication, with one optional descriptive comparison that their existing data permit.

### S1: Correlational register held from abstract to conclusion
The paper's causal restraint is stated where an adjacent-field reader will actually encounter it — in the abstract, not buried in limitations — so the claim's epistemic status travels with the finding when it is cited or summarised second-hand.
**Evidence Anchor**: text: Abstract "should not be read as causal, given the cross-sectional design"

### S2: Reverse pathway named, not merely disclaimed
Section 5 states the reciprocal interpretation explicitly rather than hedging generically, which lets outside readers see that the authors understand which inference the design forecloses and why the cited caution applies to their own numbers.
**Evidence Anchor**: text: §5 "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"

### S3: Precision and sensitivity reported in a form outsiders can use
Prospective power, alpha, tails, and sample size are given alongside the interval estimate, so a reader from an adjacent field can judge what the design could and could not have detected without reconstructing it.
**Evidence Anchor**: text: §3.4 "the study had greater than .80 power to detect a correlation of r >= .19 at alpha = .05"

### S4: Generalisation limits stated in transferable terms
Limitation 1 names the dimensions along which transfer may fail — size, sector, student profile — rather than issuing a bare single-site caveat, which is the form a practitioner needs in order to assess their own setting.
**Evidence Anchor**: text: §6 "the results may not generalize to institutions of different size, sector, or student profile"

### W1: Recruitment channel is the platform under study, and this scope condition is never stated
Distribution through the course-announcement channel means the invitation reached students in proportion to the behaviour being measured; low-frequency users are systematically less likely to have been sampled. Limitation 4 records volunteer bias in generic terms and stops short of identifying the channel as the LMS itself, so the boundary condition that most constrains transfer of the headline coefficient is absent from the paper's own account of its scope. An adjacent-field reader therefore cannot determine which student population the finding describes. The repair is explicit treatment in Methods and Limitations, plus — feasibly, at this institution — a comparison of respondents' aggregate log-activity distribution against the enrolled undergraduate population. I do not adjudicate what this does to the estimate; I flag that the reader is given no way to reason about it.
**Severity**: Major
**Evidence Anchor**: text: §3.1, §6 "The survey was distributed through the institution's course-announcement channel over a three-week window." and "students who engage more with institutional channels may be overrepresented"
**Confidence**: 5 — I administer LMS-channel surveys and routinely benchmark respondent log activity against enrolment records, so this failure mode is one I have measured directly.

### W2: Practice implication carries no decision threshold and is advertised as an implication of the data
The abstract promises implications for onboarding and Section 5 supplies a recommendation that was already the field's working assumption before the study ran. Nothing in the paper indicates what a practitioner should do differently at this effect size versus a materially smaller or larger one, and the one practitioner source is cited rather than engaged, so the claim reaches an applied readership without meeting that readership's evidentiary expectations. Because the paper elsewhere insists on proportionate claims, the mismatch is repairable by restating the recommendation as a hypothesis for intervention research and removing it from the abstract's list of contributions.
**Severity**: Major
**Evidence Anchor**: text: Abstract, §5 "We discuss implications for LMS onboarding" and "onboarding which helps students see concrete usefulness"
**Confidence**: 4 — I prepare the evidence packages that precede platform and onboarding budget decisions, and this is the class of finding that reliably fails to move one.

### W3: Non-use framed exclusively as a perception deficit, with structural and access explanations unconsidered
The manuscript's interpretive frame admits only perception and, secondarily, course requirements and assessment schedules as influences on engagement. Device access, connectivity, off-campus study conditions, employment or caregiving load, disability and accessibility barriers, and platform usability are absent throughout, including from the Limitations, even though the paper's practical recommendation targets the low-engagement students for whom those factors are most plausible. This is an unexamined framing assumption that pushes the proposed remedy toward student-facing messaging and away from institutional provision or platform design, and it means the digital-equity and accessibility literatures whose territory the recommendation enters are never engaged. Reframing costs no new data.
**Severity**: Major
**Evidence Anchor**: absence: §5 Discussion and §6 Limitations — expected consideration of structural or access barriers to LMS use (device availability, connectivity, off-campus study, employment or caregiving load, disability and accessibility, platform usability); checked Abstract, §1 Introduction, §2 Literature Review, §4 Results, §5 Discussion, §6 Limitations, §7 Conclusion
**Confidence**: 5 — digital-equity reporting is a standing responsibility in my unit, and these are the covariates that separate access barriers from preference in our own engagement data.

### W4: Log data deferred to future work with no account of why it was unavailable here
Limitation 2 and the Conclusion both position behavioural log data as a future-research need, while the Methods establish that the institution operates the platform and used it administratively. Whether the constraint was data governance, the IRB's anonymity condition, technical access, or analyst capacity is not stated, so a reader cannot judge whether the same constraint would bind in their own setting or whether this was a resourcing choice. Naming the constraint converts a soft limitation into a credible design-tradeoff account and materially improves transferability judgements.
**Severity**: Minor
**Evidence Anchor**: text: §6, §7 "LMS use was self-reported through a single item rather than measured through system logs" and "Future research using behavioral log data"
**Confidence**: 4 — I negotiate log-data access under governance and IRB constraints regularly, and the plausible reasons are few and easy to state.

### W5: Adapted instrument is not reproduced, so the measured construct cannot be inspected or reused
Section 3.2 reports that six items were adapted from a prior instrument, with reliability but without item wording and without describing what the adaptation changed. A reader outside the immediate subfield — or a practitioner wanting to field the same measure locally — cannot see what "perceived usefulness" concretely asked, nor whether adaptation shifted the construct relative to the source scale. An appendix or an inline item list resolves this.
**Severity**: Minor
**Evidence Anchor**: absence: §3.2 Measures — expected verbatim wording of the six perceived-usefulness items and a statement of what the adaptation altered; checked §3.2, §3.4, §4, References
**Confidence**: 4 — reusing published scales across institutions is routine work in my role, and missing item text is the usual blocker.
