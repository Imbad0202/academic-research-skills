contract_role: eic

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: block
trigger: "tables or figures whose numbers cannot be reconciled with the text"

The manuscript's exhibits and its narrative do not agree on the quantities they report. Table 2 sums to 127 students in the two engagement groups immediately after the text states that all 142 were classified; the perceived-control comparison in §4.3 carries a degrees-of-freedom value that no stated sample can produce; and the Abstract's headline correlation is not the value the Results section reports. Individually each is a correctable error. Collectively they mean a careful reader cannot determine what was found, which is the condition my Phase 1 plan reserved for a block rather than a warn. D5 is normal priority, so this score carries no fatality tier and no `block_class`; it registers that the presentation layer must be rebuilt before the substance can be fairly assessed.

### D6: venue_fit_and_contribution
score: block
trigger: "the study reads as a single-site descriptive report whose stated significance outruns what it delivers"
block_class: repairable

The topic is squarely within the scope of a learning-analytics venue, so the fatal tier I defined in Phase 1 (categorical scope mismatch or no discernible contribution) does not apply and I do not invoke it. What the manuscript delivers, however, is a single-course, single-term, cross-sectional correlation between a click-count proxy and a dichotomous completion variable, drawn from a self-selected subset of an unstated enrollment, with a single-item self-report as its second measure. Against that, the Conclusion offers institutions worldwide a "dependable" and "generalizable" retention strategy. The Introduction criticizes the field for reporting adoption metrics and satisfaction instead of downstream outcomes; the study answers that criticism by attaching a retention variable to the same design, without adding a measurement, mechanism, or multi-site contribution that an international readership needs. No explicit novelty claim is argued against the closest prior work, which appears in the reference list and is never discussed. Substantial repositioning and added evidence are required, but a viable and honest paper is recoverable from this material, so the block is repairable rather than fatal.

## Review Body

I read this manuscript as the editor who would have to decide whether it enters review, and my judgement is about whether the paper can be trusted as a document, not only about whether its sentences are well made. On that test it currently fails, for a reason that sits at manuscript level rather than in any single section: the Abstract, Discussion, and Conclusion make claims that the Methods and Results cannot license, and the numbers in the front matter do not match the numbers in the Results.

On scope and advance. The Introduction diagnoses the field accurately: much dashboard work reports adoption or satisfaction rather than academic outcomes. But the study's own design reproduces the pattern it criticizes with a retention variable bolted on. Engagement is session counts, which §2 itself concedes conflates careful study with repeated idle opening. Retention is a dichotomous completion flag. Perceived control is one item. There is no comparison condition, no adjustment for prior achievement or concurrent workload, no dashboard-design contribution, and no second site or term. For an international learning-analytics readership, a modest bivariate correlation from one introductory statistics course is a local evaluation report, not a contribution that changes what the field knows or does. The paper could become publishable in this venue as a candid measurement-limitations study, or as one arm of a multi-course comparison, but it is not currently framed as either.

On claim architecture. The Abstract reports r = .42; §4.2 reports r = .24. The Discussion's first sentence says engagement "improved" retention and that increasing engagement "raises the probability" of completion. The Conclusion escalates to a "dependable" and "generalizable" institutional lever "across programs and disciplines." None of that is available from an observational design with a volunteer sample and no controls. The manuscript's own third Discussion paragraph, which notes the association is "reliable but not large" and counsels against overstatement, is the only passage calibrated to the evidence, and it contradicts the two passages that bracket it. That internal split is what makes this an editorial rather than a copy-editing matter: a reader cannot tell which of the paper's voices represents the authors' actual position.

On the paper's consistency with its own critique. §2 cites Ibarra (2023) precisely on causal language outrunning correlational evidence, and §1 promises to "distinguish the pattern in the data from the causal story." The Discussion breaks that promise in its opening clause. A paper that holds the field to a standard and then violates it in its own headline sentence invites the reviewer to distrust its other judgement calls, and here that distrust is confirmed elsewhere: a source titled "When dashboards demotivate" is cited for the proposition that dashboards "reliably improve outcomes" for lower-achieving students, and nine of fifteen listed references never appear in the text.

On the discrepancy that decides the case. I cannot determine intent from the text, and I will not assert one. What I can record is that the discrepancy runs in the direction that flatters the thesis, that the inflated value is the one placed where most readers stop, and that it is not isolated: the perceived-control test reports df = 156 when the largest stated sample is 142 and the item-level sample is 87; the exam comparison reports p = .008 for t(140) = 1.31 while describing the difference as small and unremarkable; Table 2's group sizes do not sum to the number of students the text says were classified; and a ten-student integer-scale item is reported with SD = 0.10, a value the methodology seat should verify as arithmetically attainable. A single transposed digit is a correction. Four mutually inconsistent statistics, one of them the headline, is a reporting-control failure that the authors must account for before any statistical claim in the paper can be relied on. If the author response cannot reconcile these values against source output, this ceases to be a review matter and becomes an institutional integrity query; that determination is not mine to make from the manuscript alone, which is why I have scored D6 as a repairable block rather than reaching for the fatal tier my Phase 1 plan bound exclusively to scope and absence of contribution.

Two further editorial matters. First, the submission lacks the apparatus this venue expects: no ethics or institutional review statement, no data availability statement, no funding or conflict declaration, and no reproduction of the survey items beyond their stems. Second, and more seriously, §3.2 discloses that students were not informed their dashboard activity would be analyzed. I would normally treat consent questions as an ethics-office matter, but a learning-analytics venue cannot publish a trace-data study that states on its face that participants were unaware of the secondary use of their behavioral records without documented approval covering that use. That has to be resolved before publication, not after.

### S1: Candid, unusually specific acknowledgement of measurement weakness

The manuscript names the limitations of its own operationalizations in the Methods rather than burying them in §5.1, including the concession that the median split sacrifices statistical efficiency for interpretability and that click-based proxies do not capture engagement quality. This candor is genuine and is the strongest basis for a recoverable revision.

**Evidence Anchor**: text: §3.3 "This median split is a coarse simplification of a continuous measure and was adopted for interpretability rather than statistical efficiency"
**Confidence**: 5 — direct reading of an explicit authorial concession.

### S2: Clear, conventional structure with locatable operational definitions

The IMRaD organisation with numbered subsections, keywords, and a per-measure definition block makes the study auditable: sessionization rule, retention coding, and item wording are all stated in one place, which is why the inconsistencies elsewhere in the paper are detectable at all. This is a real craft strength and lowers the cost of the revision I am asking for.

**Evidence Anchor**: text: §3.3 "A session was defined as a dashboard view preceded by at least thirty minutes of inactivity"
**Confidence**: 4 — structural assessment against standard venue expectations.

### S3: Limitations section identifies the right constraints, including dashboard-design specificity

§5.1 correctly flags proxy narrowness, self-report bias, and single-course confinement, and goes further than most submissions by noting that the particular interface may drive the response. The problem is not that the authors are unaware of their constraints; it is that the Conclusion ignores them.

**Evidence Anchor**: text: §5.1 "the specific dashboard design used here differs from those deployed elsewhere"
**Confidence**: 4 — comparison against limitations sections in comparable submissions.

### W1: Abstract's headline correlation contradicts the Results section

The Abstract reports the primary association as r = .42; §4.2 reports r = .24 for the same relationship. The abstract value is roughly 75% larger and is the number most readers, citers, and institutional decision-makers will carry away. Uncorrected, no reader can know what the study found about its own central question, and no acceptance is possible with two incompatible headline values in one document. The direction of the error favors the paper's thesis, which is why it requires an author account against source output rather than a silent fix at proof stage.

**Severity**: Critical
**Evidence Anchor**: text: Abstract "Dashboard engagement correlated positively with retention (r = .42)"; §4.2 "Dashboard engagement was positively associated with course retention (r = .24, p = .004)"
**Confidence**: 5 — both values quoted verbatim from the manuscript.

### W2: Causal and generalizability claims the design cannot license, contradicting the paper's own stated standard

§5 opens by asserting that engagement "improved" retention and that increasing engagement "raises the probability" of completion; §6 recommends dashboards as a "dependable" and "generalizable" lever for institutions worldwide. The design is cross-sectional, observational, uncontrolled, and drawn from volunteers in one course. §1 promised to keep pattern and cause distinct and §2 cited Ibarra (2023) against exactly this failure. Repair requires rewriting the Abstract's concluding sentence, the Discussion's opening paragraph, and the whole of §6 to associational language, plus removing the institutional investment recommendation. The empirical kernel survives that rewrite, so this is not on its own fatal.

**Severity**: Major
**Evidence Anchor**: text: §5 "dashboard engagement improved course retention"; §6 "is a dependable strategy for improving retention across programs and disciplines"
**Confidence**: 5 — verbatim claim language against the stated design in §3.1.

### W3: Table 2 group sizes cannot be reconciled with the text's stated analytic sample

§4.3 states that all 142 students in the primary analytic sample were classified into engagement groups for the exam comparison. Table 2 reports n = 66 and n = 61, totalling 127. Fifteen students are unaccounted for, and the reader cannot tell whether they were dropped, misclassified, or omitted from the table. The exam comparison and its Discussion reading must be re-run and re-reported with a reconciled sample accounting.

**Severity**: Major
**Evidence Anchor**: table: Table 2 (§4.3), group n values 66 and 61 against the 142 students stated as classified in the same subsection
**Confidence**: 5 — arithmetic on the table as printed.

### W4: Perceived-control comparison reports a sample larger than any the paper describes

§4.3 reports t(156) = 3.02 for the high- versus low-engagement comparison on perceived control. The item was answered by 87 respondents per §4.1, and the whole analytic sample is 142. No described sample supports this test. Because perceived control is the paper's second headline result and the basis for its self-regulated-learning interpretation, this result is currently uninterpretable and needs re-analysis with an explicit denominator.

**Severity**: Major
**Evidence Anchor**: text: §4.3 "t(156) = 3.02, p = .003"; §4.1 "the 87 survey respondents who answered the item"
**Confidence**: 4 — comparison of reported values; formal statistical adjudication belongs to the methodology seat.

### W5: Reported p-value for the exam comparison contradicts both its own test statistic and the paper's stated decision rule

§4.3 describes the exam difference as small and as not reaching a comparable level, yet reports p = .008 against the α = .05 threshold declared in §3.4, where p = .008 would be a significant result. The Discussion then reads the comparison as "weaker still." One of the three statements must be wrong. §4.3 and the corresponding Discussion paragraph require re-analysis and re-writing before either can be read.

**Severity**: Major
**Evidence Anchor**: text: §4.3 "the difference was small, t(140) = 1.31, p = .008"
**Confidence**: 4 — internal inconsistency is plain on the page; exact recomputation deferred to the methodology seat.

### W6: Novelty is asserted rather than demonstrated, and most of the reference list is never engaged

Nine of the fifteen listed references never appear in the text, including Wexler and Ojo (2020) on retention modeling with LMS trace data, which is the closest published analogue to this study's own design and the work against which any novelty claim would have to be argued. The manuscript never states what it contributes beyond prior work; it states only that it "contributes to this literature." A reference list functioning as padding rather than as an argument is also the direct evidentiary basis for the D6 block: the contribution cannot be assessed as original if the nearest prior work is uncited.

**Severity**: Major
**Evidence Anchor**: absence: References list versus in-text citations — expected an in-text citation for each of the fifteen listed references, plus substantive engagement with Wexler & Ojo (2020) on retention modeling with LMS trace data; checked §1, §2, §3, §4, §5, §6 and the References list
**Confidence**: 5 — exhaustive cross-check of every listed reference against body text.

### W7: Missing ethics, data-availability, and disclosure apparatus, alongside a stated absence of participant notification

The submission carries no ethics or institutional review statement, no data availability statement, no funding or conflict declaration, and no full survey instrument, all of which this venue expects for trace-data work. §3.2 additionally states that students were not informed their dashboard activity would be analyzed for the study. Resolution may require institutional documentation the authors do not currently supply, so this cannot be handled at copy-edit stage.

**Severity**: Major
**Evidence Anchor**: text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study"
**Confidence**: 4 — the disclosure is explicit; approval status is unknown and must be queried.

### W8: The sampling paragraph describes two mutually exclusive designs and omits its denominators

§3.2 first states that participants were drawn by random sample, then describes a mid-term LMS announcement to which students chose to respond, with non-responders excluded. These are a probability sample and a voluntary-response sample; they cannot both be true. The course enrollment is given only as "several hundred," and the number invited and the number responding are never reported, so the response rate and the direction of selection cannot be estimated. Since students who answer a dashboard survey are plausibly the students who use the dashboard, this defect bears directly on the generalization claims in §6 and must be resolved with a full participant-flow account.

**Severity**: Major
**Evidence Anchor**: text: §3.2 "using a random sample of students enrolled in the course section"; §3.2 "Students who chose to respond, and who consented to the survey, formed the study sample"
**Confidence**: 5 — the two descriptions sit in adjacent paragraphs.

### W9: Inconsistent numeric precision and an inline run-on statistics report

The perceived-control mean is given to three decimals (3.847) for a single-item integer scale while every other statistic in the paper uses one decimal, and Table 1 repeats the three-decimal value. The secondary clarity item is reported as an inline run-on string of semicolon-separated values rather than in prose or a table. Both are presentation defects rather than substantive ones. I note, without claiming the finding, that the reported SD = 0.10 for ten integer responses with M = 3.00 warrants an arithmetic check by the methodology seat; if it proves unattainable, the item becomes an integrity matter rather than a formatting one.

**Severity**: Minor
**Evidence Anchor**: text: §4.1 "the reported secondary-item values were N=10; M=3.00; sample SD=0.10; integer scale=1-5"
**Confidence**: 4 — presentation conventions are within my remit; the arithmetic verification is not.

### W10: A cited source is invoked for a proposition its own title appears to contradict

§2 states that dashboards "have been shown to reliably improve outcomes for lower-achieving students," attributing this to Ferro and Nakamura (2021). The reference list gives that work's title as "When dashboards demotivate: Peer comparison and the lower-achieving student." The manuscript then says this position underpins the equity rationale it returns to in the Discussion, so a supporting claim rests on a source that may say the opposite. The word "reliably" is also unhedged in a paragraph whose surrounding sentences are careful. The formal dimension here belongs to the domain seat; I record it because it compounds the editorial trust problem and requires the authors to re-verify their characterizations of cited work.

**Severity**: Major
**Evidence Anchor**: text: §2 "Dashboards have been shown to reliably improve outcomes for lower-achieving students"; References "When dashboards demotivate: Peer comparison and the lower-achieving student"
**Confidence**: 3 — the mismatch between claim and title is clear, but the source's actual findings cannot be verified from the manuscript alone.
