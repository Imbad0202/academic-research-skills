# Field Analysis Report

## Paper Basic Information

- **Title**: Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment
- **Abstract length**: ≈135 words
- **Full text length**: ≈2,700 words excluding references (estimate from section-level counts; Methods is the longest section at ≈640 words, Discussion+Conclusion the shortest at ≈480)
- **Number of references**: 15 entries in the reference list; **6 cited in text** (Calloway 2019; Ferro & Nakamura 2021; Osei 2020; Rutledge & Berange 2022; Vandermeer 2023; Ibarra 2023) → **9 uncited entries**
- **Integrity note for the reviewers**: all 15 DOIs use the `10.5555/` prefix, which is a reserved test/placeholder prefix, and none of the cited journal titles corresponds to a recognized indexed venue. This may indicate a synthetic manuscript, a template artifact, or fabricated citations. I am not asserting which; I am flagging it as a mandatory verification item (assigned to the Journal-Fit Reviewer and Reviewer 2 below).

---

## Field Analysis

| Dimension | Analysis Result |
|---|---|
| **Primary Discipline** | Learning analytics / educational technology in higher education — specifically student-facing dashboard research |
| **Secondary Disciplines** | (1) Educational psychology — self-regulated learning theory; (2) Higher education student success / retention studies; (3) Student data ethics & governance (institutional research, privacy law) |
| **Research Paradigm** | Quantitative. Single-paradigm despite the two data sources — the survey is used as an additional quantitative variable, not as a qualitative strand, so this is **not** mixed methods in any design sense |
| **Methodology Type** | Observational cross-sectional correlational study: LMS trace-log analysis + single-wave self-report survey; analysis limited to Pearson correlations, median-split grouping, and independent-samples *t*-tests. No covariates, no regression, no causal identification strategy |
| **Target Journal Tier** | **Aspirational Q1** (framing, abstract register, and the "institutions worldwide" conclusion are pitched at a top-venue audience), **current state Q3 at best**. Rationale: the substantive design — one course, one term, one institution, n=142, self-selected mid-term sample, single-item constructs, no covariates — is below the evidentiary bar that Q1 learning analytics venues now apply to dashboard–outcome claims. Compounding this, the manuscript contains at least six internal numerical inconsistencies (detailed under Reviewer 1) that would trigger desk rejection at any tier if caught, plus an unresolved research-ethics disclosure. Tier judgment is therefore conditional, not fixed |
| **Paper Maturity** | **Surface pre-submission, substantive early draft.** Structure is complete (abstract, numbered sections, tables, limitations subsection, formatted APA-style references), language is polished, and the Introduction/Literature Review show genuine methodological self-awareness. But the Results section does not internally reconcile, the Discussion and Conclusion contradict the correlational commitment made in §1 and §2, and the reference apparatus is unverified. Classify as **revised draft, not submission-ready** |

**Note on the maturity split**: this paper's failure mode is unusual and reviewers should be briefed on it. §1 ("We are careful throughout to distinguish the pattern in the data from the causal story") and §2 (citing Ibarra 2023 on causal overreach) explicitly promise correlational discipline. §5 then states dashboard engagement "improved course retention" and "raises the probability," and §6 calls it a "dependable strategy" that is "generalizable." This is not three separate wording nits — it is one systemic inconsistency between the paper's stated epistemic standard and its claims, and it should be reviewed as a single issue.

---

## Recommended Target Journals (Top 3)

1. **Journal of Learning Analytics (SoLAR)** — Best structural fit. It is the field's home venue for dashboard studies, publishes modest-effect empirical work when claims are calibrated to design, and has an active internal critique of causal overreach that this paper could speak to honestly. Hard gate: JLA requires an explicit ethics/consent statement, which this manuscript currently cannot satisfy (see §3.2).
2. **British Journal of Educational Technology** — Receptive to single-context technology-in-HE studies with a theoretical frame (SRL), and its readership includes the instructional designers the paper addresses. Would demand a proper analytic model (logistic regression with covariates) rather than *t*-tests, and would push back hard on the generalization claim.
3. **Technology, Knowledge and Learning** *or* **Journal of Computing in Higher Education** — Realistic Q2 landing spot if the authors will not or cannot strengthen the design. Accepts smaller-scope empirical contributions, but only with the causal language fully stripped and the sampling limitation moved from §5.1 into the abstract.

**Not recommended**: *Computers & Education*, *Internet and Higher Education* — the design is not competitive there and submission would likely end in desk rejection.

---

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC
**Display role**: Journal-Fit Reviewer
**Identity Description**: Associate Editor of the *Journal of Learning Analytics*, with editorial responsibility for the dashboard and feedback-intervention track; served on the SoLAR program committee that introduced mandatory ethics-statement screening for trace-data submissions, and has desk-rejected roughly a third of incoming single-course dashboard correlational studies for insufficient contribution over existing systematic reviews.

**Review Focus**:
1. **Contribution above the existing pile.** The field already holds multiple systematic reviews of student-facing dashboards concluding that evidence on downstream outcomes is thin and heterogeneous. Judge whether one course, one term, n=142, r=.24 adds anything beyond confirming that thinness. What is the specific claim a reader could not have made before reading this?
2. **Title/abstract/conclusion vs. evidence.** The title promises "Evidence from an Undergraduate Learning Analytics Deployment"; the abstract reports r = .42 and calls engagement "a promising lever"; §6 calls it "a dependable strategy... for higher education institutions worldwide." Assess whether the manuscript's public-facing claims — which is what most readers will actually consume — are supportable at all, independent of the internal statistics.
3. **Publishability gates.** (a) No IRB/ethics approval statement anywhere; §3.2 states students were not informed their dashboard activity would be analyzed. (b) Reference list uses placeholder `10.5555/` DOIs across all 15 entries and cites no verifiable venues. Determine whether either condition is a hard bar to publication at any journal, prior to any question of scientific merit.

**Will particularly care about**: Whether the abstract, which is what gets cited and press-released, can be brought into alignment with a modest correlational finding — and whether a paper that abandons its own stated standard between §2 and §5 can be trusted with a calibrated revision.

**Possible blind spots**: Will not recompute reported statistics or check degrees of freedom against sample sizes. May treat the SRL framing as adequate because it is conventional in the field. Unlikely to interrogate whether "retention" as operationalized matches retention as the HE literature defines it.

---

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1
**Display role**: Peer Reviewer 1
**Identity Description**: Quantitative methodologist in educational measurement and applied statistics for observational data, with a specialization in reported-statistics integrity auditing (GRIM/GRIMMER-style consistency checking, statcheck-style *p*-value recomputation) and in selection bias in learning-analytics trace data. Regularly consulted by journals to adjudicate whether numerical inconsistencies in a submission are typographical or structural.

**Review Focus**:
1. **Reported-statistics reconciliation — recompute everything.** Specific items to check: (a) abstract reports **r = .42**, §4.2 reports **r = .24, p = .004**; note that r = .24 with n = 142 does yield p ≈ .004, so .42 is the unsupported figure, and it is the one in the abstract. (b) §4.3 reports **t(156) = 3.02** for the perceived-control comparison, but the analytic sample is n = 142 and only **87** answered that item, implying df = 85; df = 156 implies n = 158 and is reconcilable with neither. (c) §4.3 reports **t(140) = 1.31, p = .008**; t = 1.31 at df = 140 gives two-tailed p ≈ .19, and the text simultaneously describes the difference as small and non-comparable — the *p*-value, the *t*-value, and the verbal interpretation are mutually incompatible. (d) Table 2 group sizes **66 + 61 = 127**, not the 142 the same paragraph says were "all classified into engagement groups," and df = 140 also implies 142; 15 students are unaccounted for. (e) A **median split of 142** should produce roughly 71/71, not 66/61. (f) Perceived control **M = 3.847 with n = 87** on an integer 1–5 item is arithmetically impossible: 87 integer responses must sum to an integer, and 334/87 = 3.8391 while 335/87 = 3.8506, so no achievable sum yields 3.847 (GRIM failure). Three-decimal precision on a single-item ordinal measure is also unjustified. (g) The secondary clarity item — **n = 10, integer 1–5 scale, M = 3.00, sample SD = 0.10** — is impossible: an all-3 response set gives SD = 0, and the smallest nonzero sample SD compatible with a mean of exactly 3.00 is √(2/9) ≈ 0.471. (h) Cross-check Table 1's full-sample final-exam M = 71.3 against Table 2's weighted group mean of ≈70.7 and state whether the 15 missing cases explain the gap.
2. **Design validity, specifically survivorship conditioning.** Recruitment occurred **midway through the term** via voluntary LMS announcement, and retention was measured at end of term. Students who had already withdrawn could not enter the sample. The outcome variable is therefore conditioned on partial survival, which mechanically attenuates or distorts the engagement–retention association in an unknown direction. Additionally, §3.2 describes the sample as "a random sample of students enrolled in the course section" and then, two sentences later, as students who "chose to respond" — these are incompatible sampling descriptions and the design is a voluntary-response convenience sample. Response rate is never reported despite an enrollment of "several hundred."
3. **Measurement and analytic model.** (a) Median split applied to an explicitly right-skewed distribution, discarding variance for "interpretability"; (b) dichotomous retention analyzed via Pearson correlation with no covariates — no prior achievement, no credit load, no demographics — where logistic regression is the minimum defensible model; (c) session count defined by a 30-minute platform default inactivity rule, adopted without justification and acknowledged in §2 to conflate distinct engagement types; (d) single-item constructs with no reliability or validity evidence; (e) no effect sizes beyond r, no confidence intervals anywhere; (f) the abstract claims "self-regulated learning behavior" was measured, but no SRL behavioral measure exists in §3.3 — only one perceived-control item.

**Will particularly care about**: Whether the numerical inconsistencies form a pattern in one direction — every discrepancy inflates the finding (r .42 over .24; p = .008 over .19; df 156 over 85) — because that pattern distinguishes careless transcription from something that requires the underlying data.

**Possible blind spots**: May not evaluate whether the SRL literature is being represented accurately, may treat the undisclosed log-data use as a limitation rather than an ethics gate, and may undervalue whatever descriptive contribution survives once the errors are corrected.

---

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2
**Display role**: Peer Reviewer 2
**Identity Description**: Senior higher education researcher specializing in student-facing learning analytics and self-regulated learning, who has co-authored a systematic review of dashboard–outcome studies and works at the junction of SRL theory and institutional retention research (Tinto/Bean traditions). Known for insisting that theory in learning analytics papers be load-bearing rather than decorative.

**Review Focus**:
1. **Citation fidelity and literature integrity.** §2 states that "Dashboards have been shown to reliably improve outcomes for lower-achieving students... (Ferro & Nakamura, 2021)" — but that reference's own title is "*When dashboards demotivate: Peer comparison and the lower-achieving student*." The source appears to be cited against its own argument, and this is not a minor slip: the misread claim is explicitly carried forward ("we return to it in the Discussion") and does structural work in §5's equity argument. Also assess: 9 of 15 reference-list entries are never cited in text, which suggests the list was assembled independently of the argument; and every DOI uses the `10.5555/` test prefix, so no citation is currently verifiable.
2. **Is the SRL frame load-bearing?** The paper invokes forethought/performance/reflection cycles and argues dashboards "supply the feedback that fuels the reflective phase." But nothing in the design tests any phase of that cycle: there is one cross-sectional perceived-control item. §5 then describes perceived control as "a mediating construct" with no mediation analysis, no temporal ordering, and no path model — perceived control could equally be an antecedent of dashboard use, which would reverse the entire mechanism story. Determine whether the theory constrains any prediction or merely decorates the introduction.
3. **Construct validity of "retention" against the HE literature.** The paper operationalizes retention as remaining enrolled and sitting the final assessment in one course, then discusses implications for "undergraduate attrition," "the first-year gateway course," and institutional retention "across programs and disciplines." Course completion and institutional persistence are distinct constructs with distinct determinants, and the retention literature the paper gestures at (attrition, gateway risk) is cited to no specific source. Assess whether the conflation is corrigible by rewording or whether it invalidates the framing. Also note that §3.1's claim of "disciplinary breadth even within one course" is asserted, not evidenced — no major distribution is reported.

**Will particularly care about**: Whether the field learns anything it did not already know from the reviews this paper does not engage — and whether the authors' genuine methodological self-awareness in §1 and §2 reflects real understanding or borrowed hedging language that they then abandon when it becomes inconvenient in §5.

**Possible blind spots**: Likely to accept reported statistics at face value and not recompute degrees of freedom. May not press on data-protection or consent questions, treating them as an IRB matter outside peer review.

---

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3
**Display role**: Peer Reviewer 3
**Identity Description**: Learning analytics ethics and student data governance specialist with an information science background, working in an institutional research office with responsibility for FERPA/GDPR compliance on trace-data reuse and for algorithmic accountability review of student-facing analytics deployments. Has advised three campuses on whether to fund dashboard rollouts and has twice recommended against it.

**Review Focus**:
1. **Undisclosed secondary use of behavioral data.** §3.2 states plainly: "Students were not informed that their dashboard activity data would be analyzed for this study," while consent was obtained only for the survey. There is no IRB/REC approval statement, no data-protection basis, no anonymization description, and no data-availability or retention statement anywhere in the manuscript. Under most institutional and statutory frameworks this is a consent defect in the research conduct itself, not a study limitation — and §5.1's limitations list omits it entirely. Assess whether the manuscript is publishable in its current disclosure state and what the minimum remedy is (documented approval and legal basis, or retrospective consent, or withdrawal of the log-based analyses).
2. **The dashboard is an intervention with a plausible harm profile, and harm went unmeasured.** §3.1 discloses that the dashboard displayed "a peer-comparison band" to all enrolled students with no opt-in. §2 then reviews evidence that relative-standing feedback can demotivate struggling and performance-avoidance-oriented students (Osei 2020; and, correctly read, Ferro & Nakamura 2021). The paper never asks whether the intervention harmed anyone: no subgroup analysis by prior achievement, no analysis of whether non-retained students were disproportionately exposed to unfavorable comparisons, and — critically — the students most likely to be harmed are precisely those who withdrew before the mid-term survey and are therefore absent from the data. A study measuring only the retained cannot detect the harm mechanism its own literature review describes.
3. **What an institution would actually need before spending money.** §6 tells institutions "worldwide" that dashboard investment is "a dependable strategy" and "a practical and generalizable lever... at scale," on the basis of r = .24 in one statistics course. From a deployment-decision standpoint this is unusable: there is no base rate for retention in the course, no withdrawal-timing data, no dose–response information (how many sessions matter?), no cost figure, no comparison against cheaper retention interventions, and no plausible causal path that survives the obvious confound — that conscientious students both open dashboards and finish courses. Evaluate whether the recommendation is merely overstated or whether it is the kind of claim that, if acted on, would waste institutional resources and displace better-evidenced supports.

**Will particularly care about**: That the students who most needed protection — those who left, and those shown they were behind — are structurally invisible in this dataset, and that the paper's confident institutional recommendation is built on a sample defined by their absence.

**Possible blind spots**: Will not adjudicate SRL theory or recompute the reported statistics, and may under-credit the manuscript's real methodological candor in §1–§2. Risk of letting the governance critique crowd out any assessment of whether a corrected, properly scoped version of this study would be worth publishing.

---

## Review Strategy Recommendations

**Coverage design.** The four briefs are non-overlapping by construction: #1 judges fit and public-facing claims, #2 recomputes numbers and interrogates design validity, #3 audits theory and literature fidelity, #4 addresses consent, harm, and deployment consequence. The only deliberate overlap is Ferro & Nakamura (2021), which #3 examines as a citation-integrity failure and #4 examines as evidence that a known harm mechanism went unmeasured. These are genuinely different findings from the same source and should both be retained.

**Anticipated tension between reviewers, and how to hold it.** #1 and #3 will likely converge on "major revision or reject on contribution grounds," which is a normal editorial outcome. #2 and #4 are each positioned to find something categorically harder: #2 may conclude that the reported statistics cannot be reconciled without the raw data, and #4 may conclude that the log-based analyses lack a consent basis. Neither of those is a severity level that "major revision" can absorb, and the synthesizer must not average them away against #1's more routine verdict. If either holds, it governs.

**Systemic issues to review as single items, not as scattered nits.**
1. *The register split.* §1–§2 commit to correlational discipline and cite Ibarra (2023) on causal overreach; §5–§6 assert improvement, causation, dependability, and worldwide generalizability. Reviewers should address this once, as one failure, rather than flagging six sentences separately.
2. *Directional error pattern.* Every numerical discrepancy in the manuscript points the same way — toward a stronger finding (r .42 vs .24; p .008 vs ≈.19; df 156 vs 85). #2 should state explicitly whether this pattern is consistent with transcription error.
3. *Survivorship conditioning.* Mid-term voluntary recruitment plus end-of-term outcome measurement is a single structural defect that simultaneously undermines #2's validity assessment and #4's harm assessment. It should be named once and referenced by both.

**Register guidance.** Given the manuscript's structural completeness and its authors' evident awareness of the field's causal-inference problem, a developmental register is appropriate — the feedback should tell the authors what a defensible version of this study would look like. Register affects wording only. The recommendation itself stays evidence-based against the criteria; a constructive tone must not soften the verdict on the arithmetic, the consent gap, or the unverifiable reference list.

**Verification item requiring resolution before substantive review is meaningful.** All 15 references carry `10.5555/` placeholder DOIs and cite unrecognizable venues. Two readings are open: this is a template or synthetic manuscript, or the citations are fabricated. #1 and #3 should each state which reading they hold and on what basis, because the answer changes what every other finding means.
