contract_role: domain

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: block
trigger: "materially misrepresent a cited source, such that a central conclusion of the manuscript rests on an inaccurate account of the field's evidence"
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

I read this manuscript as a persistence researcher, asking three questions: does the paper report the literature it cites faithfully, does it use the field's constructs with the meanings the field assigns them, and does the theory it invokes have any measurement standing behind it. On all three the answer is no, and the failures are load-bearing rather than cosmetic.

The most serious problem is a citation inversion. §2 asserts that "Dashboards have been shown to reliably improve outcomes for lower-achieving students, who are said to gain the most from externalized progress cues," and attributes this to Ferro & Nakamura (2021). The reference list gives that source's title as "When dashboards demotivate: Peer comparison and the lower-achieving student." A paper with that title does not support the proposition it is cited for; on any reasonable reading it supports the opposite. The manuscript then compounds the error by making the inverted premise do work: §2 says "we return to it in the Discussion," and §5 duly reports that the finding "aligns with the view that externalized progress cues can support persistence." So the equity-oriented rationale in the literature review and one of the two interpretive warrants in the Discussion both rest on a source characterised against its own findings. This matters especially here because the dashboard actually deployed included "a peer-comparison band" (§3.1), which is precisely the feature the demotivation literature implicates. The manuscript therefore had, sitting in its own bibliography, the source most likely to complicate its result, and converted it into corroboration.

The second problem is the construct labelled "retention." §3.3 codes it as "whether the student remained enrolled and completed the final assessment" in one 15-week course. In the persistence literature retention is a term of art for continued enrolment in a programme or institution across terms, and the distinction is not pedantic: course completion and institutional persistence have different determinants, different base rates, and different policy levers. Calling one-course completion "retention" is a terminology error the field will notice immediately, and the manuscript's own §3.1 concedes that "no student was observed across multiple courses or terms." The Conclusion nonetheless recommends dashboards to "higher education institutions worldwide" as "a dependable strategy for improving retention across programs and disciplines." The measured construct cannot carry that scope, and §5.1's limitation about a "single introductory statistics course" is contradicted two paragraphs later rather than honoured.

Third, self-regulated learning is invoked but never measured. The Abstract states that "we measured dashboard engagement, self-regulated learning behavior, and course persistence." §3.3 contains no SRL instrument. The nearest thing is a single-item perceived-control rating, which is not an SRL measure by any standard the field recognises: SRL research uses multi-component instruments covering forethought, strategy use, monitoring, and reflection, and a global perceived-control item indexes none of these separately. Yet §5 treats the perceived-control difference as "consistent with a self-regulated learning account in which dashboards scaffold monitoring and adjustment." SRL functions here first as framing and then as an interpretive warrant, with nothing measured in between.

Beyond SRL, the paper offers no theory of departure at all. There is no engagement with the integration-and-departure tradition or its critics, no account of why students leave gateway courses, and consequently no principled reason to expect a visibility mechanism to move an outcome that the field attributes to academic preparation, financial pressure, competing obligations, and institutional fit. What stands in for theory is a mechanism story about visibility, asserted in §1 and never tested.

I also note that eight of the sixteen references are never cited in the text, and the pattern is not random. Halloran (2020), "Retention in the gateway course: A review of intervention studies," and Wexler & Ojo (2020), "Retention modeling with LMS trace data: A cautionary study," are the two entries most directly on the paper's own question, and neither appears in the body. Berange (2021), "Goal orientation and dashboard response in introductory courses," is uncited even though §2's performance-avoidance sentence is exactly its subject and is attributed instead to Osei (2020). This bears on what the reviewer card asked me to weigh: whether, once the overclaiming is removed, a contribution remains that is distinguishable from what Wexler & Ojo and Halloran already established. On the present text I cannot tell, because the manuscript never says what those studies found or how its own result differs. A paper whose novelty claim depends on the thinness of prior retention evidence must engage the prior retention evidence it has itself listed.

Two matters I flag but do not score. First, the Discussion's causal turn — §5's "dashboard engagement improved course retention" and §6's "is associated with, and raises" — directly commits the error the paper cites Ibarra (2023) to warn against, after §1 promises restraint. That is argumentative coherence (D3) and belongs to the discourse-analysis seat, though it compounds the D2 problem because the paper cites a critique and then instantiates it. Second, the statistical anomalies visible on the page — a t-test reported at t(156) when the analytic sample is 142, and t(140) = 1.31 paired with p = .008 — are methodology-seat matters (D1); I flag their existence without adjudicating them.

On fatality: I score D2 `block` with class `repairable`, not fatal. The Ferro & Nakamura inversion can be corrected by re-characterising the source and rebuilding §2's equity paragraph and §5's warrant around what it actually found; "retention" can be renamed course completion and the Conclusion rescoped; the unmeasured SRL claims can be deleted; the uncited on-point literature can be engaged. An association between dashboard sessions and course completion, honestly labelled, survives all of that. The one condition under which I would revisit this judgement is W7 below: if the reference-verifiability check confirms that these sources do not exist, the finding moves from misrepresentation to fabrication, and my fatal criterion — systematically mis-attributed or non-existent sources — would be met. I did not verify the references externally and do not assert fabrication here.

### S1: Accurate and appropriately cited treatment of engagement-measurement limits

§2's discussion of behavioural proxies is the strongest passage in the paper and represents the field correctly: click-count measures do conflate attention with frequency, and Vandermeer (2023) is cited for a proposition consistent with its stated title. §3.3 and §5.1 restate the limitation rather than quietly dropping it.

**Evidence Anchor**: text: §2 "click-based engagement metrics should be treated as rough indicators rather than as faithful measures of the cognitive engagement the theory implicates"

### S2: Candour about the median split

The field's standard objection to dichotomising a continuous predictor is stated by the authors themselves rather than left for a reviewer, and the justification offered (interpretability, not efficiency) is the honest one.

**Evidence Anchor**: text: §3.3 "This median split is a coarse simplification of a continuous measure"

### S3: Fair characterisation of the dashboard literature's outcome deficit

The claim that published dashboard work skews toward adoption and satisfaction metrics rather than downstream academic outcomes is an accurate description of the evidence base as it stands, and is the correct motivation for a study of this kind.

**Evidence Anchor**: text: §1 "Much of the published work reports adoption metrics or student satisfaction rather than downstream academic outcomes"

### W1: Ferro & Nakamura (2021) is cited for the opposite of its own finding, and the inversion is load-bearing

The §2 claim that dashboards "reliably improve outcomes for lower-achieving students" is attributed to a source titled "When dashboards demotivate: Peer comparison and the lower-achieving student." The manuscript flags this premise as one it will "return to in the Discussion," and §5 uses it as the warrant for reading the result as evidence that "externalized progress cues can support persistence." A cited source is thus made to underwrite a conclusion it contradicts, in a paper whose deployed dashboard contains the peer-comparison band that source implicates. Uncorrected, this places a false attribution in the published record and voids one of the Discussion's two interpretive supports; it alone justifies a block on this dimension.

**Severity**: Critical
**Evidence Anchor**: text: §2 and References "Dashboards have been shown to reliably improve outcomes for lower-achieving students" / "When dashboards demotivate: Peer comparison and the lower-achieving student"
**Confidence**: 5 — the inversion is verifiable from the manuscript's own reference list; I work in this dashboard-effectiveness literature.

### W2: "Retention" names a construct the study did not measure, and the Conclusion generalises past it

The outcome is completion of one course's final assessment in one term. The field reserves "retention" for programme or institutional persistence, which has different determinants and different intervention targets. The Conclusion recommends dashboards as a dependable strategy for "retention across programs and disciplines" and addresses institutions "worldwide," a scope no single-course completion variable can license, and one that §5.1's own limitation contradicts. Repair requires renaming the outcome throughout, rewriting §6, and reframing the contribution as course-completion evidence.

**Severity**: Major
**Evidence Anchor**: text: §6 and §3.3 "a dependable strategy for improving retention across programs and disciplines" / "whether the student remained enrolled and completed the final assessment"
**Confidence**: 5 — standard terminological boundary in the persistence literature.

### W3: Self-regulated learning is claimed as measured, is not measured, and is then used as an interpretive warrant

The Abstract asserts that SRL behaviour was measured. §3.3 contains no SRL instrument; the only candidate is a single global perceived-control item, which indexes no SRL phase and is not validated in this study. §5 nonetheless reads the group difference as consistent with an SRL account of monitoring and adjustment. The Abstract statement is factually incorrect about the study's own measures, and the §5 inference has no instrument behind it. Repair means deleting the SRL measurement claim, removing SRL from the interpretive apparatus, or adding a validated instrument in new data collection.

**Severity**: Major
**Evidence Anchor**: text: Abstract and §5 "we measured dashboard engagement, self-regulated learning behavior, and course persistence" / "consistent with a self-regulated learning account in which dashboards scaffold monitoring and adjustment"
**Confidence**: 5 — SRL instrumentation requirements are well established and none is present.

### W4: The two most directly relevant sources in the paper's own bibliography are never engaged

Halloran (2020) reviews gateway-course retention interventions and Wexler & Ojo (2020) is a cautionary study of retention modelling from LMS trace data; both sit in the reference list and neither appears in the text. Berange (2021) on goal orientation and dashboard response is likewise uncited while §2 attributes its subject matter to Osei (2020). Eight of sixteen references are uncited overall. The manuscript's positioning claim that retention evidence "remains thin," and any implicit novelty claim, cannot be assessed against prior work the paper lists but does not discuss. Substantial rewriting of §2 and §5 is required to establish what, if anything, this study adds beyond those two sources.

**Severity**: Major
**Evidence Anchor**: absence: §2 Literature Review and §5 Discussion — expected in-text engagement with Halloran (2020) and Wexler & Ojo (2020); checked every in-text citation in §1 through §6 against the 16-entry reference list
**Confidence**: 5 — direct enumeration of in-text citations against the reference list.

### W5: No theory of student departure is offered anywhere

The paper makes retention claims without any account of why students leave. Neither the integration-and-departure tradition nor its critics nor any successor model appears in the text or the reference list; §1 substitutes a visibility-supports-self-regulation mechanism story. This leaves the interpretation ungrounded and gives readers no basis for judging where a dashboard would sit among known determinants of departure, but it does not by itself alter the observed association.

**Severity**: Minor
**Evidence Anchor**: absence: §1 theoretical framing — expected an account of student departure grounded in persistence theory; checked §1, §2, §5, and the reference list for Tinto, Bean, or successor departure models
**Confidence**: 4 — absence confirmed by reading; some allowance that the venue may not require theoretical framing.

### W6: The Abstract reports an effect size nearly double the one reported in Results

The Abstract states r = .42; §4.2 reports r = .24. One of the two is wrong, and the Abstract is the version that will be indexed, quoted, and extracted into any synthesis. Until the authors say which value is correct, the headline quantity of the paper is unknown, and §5's characterisation of the effect as "reliable but not large" is consistent only with the smaller figure. The analytic adjudication belongs to the methodology seat; the misstated quantity is a record-accuracy matter here.

**Severity**: Major
**Evidence Anchor**: text: Abstract and §4.2 "Dashboard engagement correlated positively with retention (r = .42)" / "Dashboard engagement was positively associated with course retention (r = .24, p = .004)"
**Confidence**: 5 — direct comparison of two stated values.

### W7: The reference list is not verifiable from the identifiers supplied

All sixteen entries carry DOIs under the 10.5555 prefix, which is the DOI system's reserved test prefix and does not resolve to registered scholarly records, and the suffixes follow a visibly patterned digit sequence. I did not attempt external verification and I do not assert that these sources are fabricated. But as supplied, no reference in this paper can be checked by a reader, which is what allowed the W1 inversion to be detectable only from a title. Authors should supply resolvable identifiers for every entry. I flag this to corroborate the journal-fit seat's independent verifiability check; if that check establishes non-existence, this dimension escalates from misrepresentation to fabrication.

**Severity**: Major
**Evidence Anchor**: text: References "https://doi.org/10.5555/1010203" and "https://doi.org/10.5555/1516718"
**Confidence**: 3 — confident that 10.5555 is a non-production test prefix; the inference about the sources themselves is unverified and deferred to the verifiability seat.
