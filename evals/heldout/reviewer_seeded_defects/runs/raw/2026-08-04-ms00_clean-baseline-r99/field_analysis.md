# Field Analysis Report

## Paper Basic Information

- **Title**: Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students
- **Abstract length**: ~147 words
- **Full text length**: ~1,750 words (main text, Sections 1–7); ~1,880 words including references
- **Number of references**: 6
- **Language**: English (review to be conducted in English)
- **Tables / figures**: none present (a scatterplot is described in §3.4 but not supplied; no descriptive statistics table)

**Data-integrity observation to route to reviewers (not a verdict):** all six references share the DOI prefix `10.5555`, which is a placeholder/test prefix rather than a registered publisher prefix, and several journal titles closely resemble but do not match known field journals (e.g., "*British Journal of Educational Technology Studies*" vs. the actual *British Journal of Educational Technology*). Citation verifiability must be resolved before any substantive verdict on the literature base is meaningful. I flag this as an observation for verification, not as a finding.

---

## Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| **Primary Discipline** | Educational technology in higher education (learning technology / e-learning adoption) |
| **Secondary Disciplines** | (1) Information systems — technology acceptance research (TAM lineage); (2) Educational measurement / survey psychometrics; (3) Learning analytics & institutional research |
| **Research Paradigm** | Quantitative — descriptive-correlational, non-experimental |
| **Methodology Type** | Survey / questionnaire; single-site cross-sectional design; bivariate correlational analysis (Pearson with Spearman robustness check) |
| **Target Journal Tier** | **Realistic: Q3; floor: Q4.** Rationale: a single bivariate association from one institution, one adapted six-item scale, one single-item dependent measure, no multivariate model, no theoretical test, and a six-source literature base. The manuscript is *internally* well-calibrated but the contribution volume is below what Q1/Q2 learning-technology journals require; those venues would likely desk-reject on incrementality rather than on quality. A short-report or research-note track at a Q3 venue is the honest fit. |
| **Paper Maturity** | **Split verdict: pre-submission in form, revised-draft in substance.** Form evidence: complete IMRaD-plus structure, consistent statistical reporting (r, 95% CI, p, n), Spearman robustness check, sensitivity/power statement, dedicated limitations section, formatted DOIs, clean prose with no evident language issues. Substance evidence: six references, no descriptive table or figure, adaptation of the instrument undocumented, response rate absent, r² referred to only as "modest" without a number, and an unreconciled contradiction between "no identifying information was collected" (§3.3) and "5 duplicate entries were removed" (§3.1). |

**Defining characteristic of this manuscript:** it is *deliberately under-claiming*. The author pre-empts nearly every standard criticism (causality, self-report validity, single-site generalizability, voluntary response). This is a genuine strength and also a review hazard — see Review Strategy Recommendations.

---

## Recommended Target Journals (Top 3)

1. **Education and Information Technologies (Springer)** — Highest topical-volume fit; regularly publishes single-institution technology-acceptance surveys of undergraduates, so the topic will not be alien to the readership. Trade-off: this journal's recent acceptance pattern favours multivariate models (SEM / multi-construct TAM or UTAUT), so a single bivariate path is likely to be asked to expand rather than accepted as-is.

2. **Research in Learning Technology (ALT, open access)** — Best *design*-fit. Explicitly hospitable to bounded, transparently reported empirical work and to short-format contributions, and its reviewer culture rewards the epistemic restraint this manuscript displays. Trade-off: lower visibility and impact than option 1; the author must accept that "modest and correct" is the positioning.

3. **Journal of Information Technology Education: Research (JITE:R)** — Accepts incremental single-institution survey evidence with a practice-facing implication, which matches the onboarding discussion in §5. Trade-off: narrower higher-education readership and weaker indexing than the first two.

**Stretch option (for the Journal-Fit Reviewer to consider and probably reject):** *Interactive Learning Environments* or *Australasian Journal of Educational Technology* — plausible topically, but both would need a substantially expanded design.

**Format recommendation:** whichever venue is chosen, this should be submitted to a **Brief Report / Research Note** category rather than as a full article. The manuscript's length and scope are consistent with that category and inconsistent with a full-article contribution claim.

---

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC
**Display role**: Journal-Fit Reviewer
**Identity Description**: Associate Editor of *Education and Information Technologies* with concurrent editorial-board service at *Research in Learning Technology*; handles roughly 200 technology-acceptance submissions per year and makes the desk-reject calls on them; has published editorially on the saturation of TAM-derived LMS studies and on when replication-grade evidence earns journal space.
**Review Focus**:
1. Contribution threshold: does a single bivariate correlation from one campus clear the bar for a full article, or is this a Brief Report / Research Note? Decide the category question explicitly rather than leaving it implicit in the verdict.
2. Readership interest and saturation: the TAM–LMS association is one of the most heavily replicated findings in the field. Determine whether the author's own framing ("an incremental data point, comparable with prior work") is a sufficient contribution claim for the configured journal, or whether it functions as a pre-emptive concession that the paper knows it is below threshold.
3. Journal fit and routing: assess whether the manuscript is better served by the Q3 short-report venue than by the higher-volume Springer venue, and state which of the three recommended journals the paper should actually target after revision.
4. Structural adequacy for publication: absence of any table or figure, and absence of a reported r² value, against the configured journal's reporting norms.

**Will particularly care about**: Whether the paper's honesty is being asked to do the work that contribution is supposed to do — an impeccably calibrated report of a well-known association is still a report of a well-known association, and the fit decision must rest on what a reader gains, not on how carefully the claim is hedged.

**Possible blind spots**: May settle the category question (Brief Report) and treat that as resolving the paper, under-weighting the specific measurement defects that R1 will surface — a Brief Report still has to be right. May also under-weight the citation-verifiability issue because editors typically delegate reference checking to production.

---

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1
**Display role**: Peer Reviewer 1
**Identity Description**: Quantitative survey methodologist and psychometrician in educational measurement; specializes in ordinal-data treatment, single-item measure validity, and the reliability–attenuation problem in correlational education research; regularly serves as statistical reviewer for education journals and has published on the misuse of Cronbach's α as sole evidence of scale quality.
**Review Focus**:
1. **Dependent-variable measurement.** LMS use is a *single* five-point ordinal item. Reliability is unestimable for a single item, so the reported correlation is attenuated by an unknown and unreportable amount. Assess whether r = .42 can bear the interpretive weight placed on it, and whether the manuscript's own §3.2 hedge ("we treat this as an ordinal indicator") is sufficient or merely descriptive of the problem.
2. **Ordinal–continuous analysis choice.** Pearson r is reported as the primary estimate on a 5-category ordinal variable; Spearman ρ = .40 is offered as a robustness check but with no confidence interval. Evaluate whether a polychoric or ordinal-appropriate estimate should be primary, and whether the CI [.30, .52] is being asserted under assumptions the data do not meet. Also check whether the reported CI is consistent with r = .42 at n = 214.
3. **Sample and nonresponse.** 233 received → 214 analyzed, but the denominator ("all enrolled undergraduates") is never given, so no response rate exists and the voluntary-response bias named in §6 cannot be bounded. "Spanned all four year levels" is asserted with no distribution. Assess whether any generalization, even the bounded one claimed, is supportable.
4. **Internal contradiction.** §3.3 states no identifying information was collected and responses could not be linked to individuals; §3.1 states 5 duplicate entries were removed. Determine how duplicates were identified under those conditions and whether one of the two statements must be corrected.
5. **Instrument adaptation and power framing.** The six-item scale is "adapted from Costa and Wren (2019)" with no documentation of what was changed, no factor structure evidence in the present sample, and α = .88 as the only psychometric warrant. Separately, establish whether the power statement in §3.4 is a priori or a post-hoc sensitivity restatement, and whether it is labelled correctly.

**Will particularly care about**: Whether reported precision (CIs to two decimals, a robustness check, a power statement) is doing genuine inferential work or is producing an appearance of rigour on top of a dependent variable that cannot support it.

**Possible blind spots**: Will likely not question whether the research question is worth asking at all, and may accept the paper's contribution premise while fixing its statistics. Also unlikely to comment on the institutional/LMS context that determines what the variance in the use item actually represents.

---

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2
**Display role**: Peer Reviewer 2
**Identity Description**: Senior learning-technology researcher in higher education; has conducted meta-analytic synthesis of technology-acceptance effect sizes in educational settings and has published critique of the TAM research programme's diminishing returns; deeply familiar with the canonical lineage (Davis; Venkatesh and colleagues) and with LMS-specific synthesis work.
**Review Focus**:
1. **Literature base adequacy.** Six references for a technology-acceptance study is far below field norm. The canonical origin of the perceived-usefulness construct is never cited, nor is any UTAUT-generation work, nor any of the existing meta-analyses that already pool LMS acceptance effect sizes. Assess whether §2 can be said to situate the study at all.
2. **The incrementality claim, tested against synthesis.** The manuscript positions itself as "one point in a distribution" (echoing Song, 2018). If pooled meta-analytic estimates for this association already exist, the paper's obligation is to state the pooled estimate and say where r = .42 falls relative to it. Determine whether the incremental-data-point claim survives that test or collapses without it.
3. **Construct stripping.** TAM is reduced to a single path: perceived ease of use, behavioural intention, facilitating conditions, instructor expectations, and assessment design are all absent — yet §4 and §5 invoke "course requirements and assessment schedules" as unmeasured explanations. Assess whether the paper is entitled to that explanation having measured none of it.
4. **Missing institutional context.** The LMS is never named; the institution's usage policy is never described. If assignment submission or grade release runs through the LMS, the use item is partly measuring compulsion, not engagement, and the entire association changes meaning. Establish what contextual reporting is minimally required.
5. **Citation verifiability.** Verify each of the six references. Report the `10.5555` DOI prefix pattern and the near-miss journal titles as a factual finding and state what it implies for the reviewability of §2.

**Will particularly care about**: Whether "perceived usefulness" is operationally distinct from "reported use" in this design, or whether both items tap a single undifferentiated favourability toward the platform — which would make r = .42 a common-method artefact rather than a substantive association.

**Possible blind spots**: Likely to over-index on literature gaps and theoretical expansion, and to under-credit the parts of the design that are genuinely sound (the correlational-language discipline, the Spearman check, the sensitivity statement). Risk of recommending a fundamentally larger paper instead of a correct small one.

---

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3
**Display role**: Peer Reviewer 3
**Identity Description**: Director of learning analytics and institutional research at a public university; owns the institution's LMS telemetry pipeline and the data-governance approvals around it; makes the actual budget decisions about student onboarding programmes; also co-chairs an institutional data-ethics committee reviewing student-trace-data use.
**Review Focus**:
1. **Design-choice defensibility from the practitioner side.** Every university that operates an LMS already possesses per-student access logs. The manuscript names the self-report/log divergence problem (citing Vasquez, 2020) and then proceeds by self-report anyway, without explaining why log data was unavailable, unobtainable, or governance-blocked. Assess whether the limitation is *handled* or merely *disclosed* — this is the paper's central unexamined decision.
2. **Construct validity from an operations viewpoint.** "How often did you access the LMS in a typical week" measures login frequency, which in practice tracks assessment deadlines, timetable structure, and notification settings far more than perceived usefulness. Evaluate whether access frequency is a defensible proxy for "engagement," a term the abstract and conclusion both use.
3. **Actionability of the practical implication.** §5 recommends onboarding that "helps students see concrete usefulness." Judge whether this is specific enough for any institution to act on, or whether it restates the correlation as advice. State what the finding would have to look like to change an onboarding budget line.
4. **Unmeasured equity confounder.** Device access, broadband quality, commuter vs. residential status, and paid-work hours all shape LMS access frequency and are correlated with how useful a platform *can* be to a given student. None appear in the design. Assess whether the omission threatens the interpretation of the association and whether it should be named in §6, which currently omits it.
5. **Ethics and governance coherence.** Read §3.3 against §3.1 from a governance standpoint: an anonymous instrument that nonetheless supports duplicate detection implies some retained identifier or fingerprint. Determine what the ethics approval actually covered and what the manuscript needs to say to be accurate.

**Will particularly care about**: Whether an institution reading this paper would change anything it does — and if not, whether the manuscript should say so plainly instead of offering a hedged onboarding implication.

**Possible blind spots**: May undervalue the legitimacy of perception measures as constructs in their own right (perceived usefulness is *supposed* to be self-reported), and may drift toward "you should have run a different study," which is outside the reviewable scope of this submission. The synthesizer should hold this reviewer to what the current design can be asked to fix.

---

## Review Strategy Recommendations

**1. The calibration hazard — the single most important instruction to all four reviewers.**
This manuscript pre-empts almost every standard objection. It says "not causal," "moderate not strong," "single site," "self-report not behavioural," "suggested by, not proven by." That discipline is real and should be credited. It also creates a specific failure mode in both directions:

- *Inflation risk*: reviewers reward the tone and return a verdict warmer than the criteria support. Honest hedging is not a contribution.
- *Double-penalty risk*: reviewers list the limitations the author already listed, as if newly discovered.

The operative test for every named limitation is **disclosed vs. handled**. §6's four limitations are all disclosed; R3's Focus 1 and R1's Focus 1 are the two places where the review must determine whether any of them were actually addressed. Wording may be developmental; the verdict tracks the criteria regardless.

**2. Scope-creep arbitration is required before synthesis.**
The three peer reviewers will pull in three incompatible directions:

| Reviewer | Implicit remedy | If fully adopted |
|---|---|---|
| R1 (measurement) | Fix the DV, re-estimate with ordinal-appropriate methods, report nonresponse | New data collection needed for the DV |
| R2 (domain) | Add canonical literature, benchmark against meta-analytic pooled r, add TAM constructs | A substantially different, larger paper |
| R3 (analytics/practice) | Use institutional log data | A different study entirely |

Adopting all three produces a different manuscript, not a revision. The Journal-Fit Reviewer must rule on which remedies are in-scope for revision of *this* submission, and the synthesizer must not merge the three into an undeliverable revision list. My recommendation for that ruling: the in-scope set is R1's Focus 2–5 and R2's Focus 1, 4, 5 plus R3's Focus 3–4; R3's Focus 1 (log data) belongs in Future Research and as an explicit justification paragraph, not as a required new analysis.

**3. Two items are gates, not findings — resolve them before weighing anything else.**
- *Citation verifiability* (R2, Focus 5): if the six references cannot be verified, Section 2 is not reviewable and no judgment about literature adequacy is safe.
- *The anonymity/duplicate-removal contradiction* (R1 Focus 4, R3 Focus 5): one of the two statements is wrong. This is a factual defect in the methods section, independent of any methodological opinion, and it touches ethics reporting.

**4. Productive tension to preserve, not resolve.**
R1 and R3 will collide on whether self-report is a defect or a legitimate construct choice. R1 treats the single-item DV as a psychometric weakness; R3 treats the whole self-report strategy as an avoidable design choice; a defensible counter-position is that perceived usefulness *must* be self-reported and only the DV needs behavioural anchoring. Keep both positions on the record rather than averaging them — the disagreement is the substance.

**5. Coverage note.**
This paper is only moderately cross-disciplinary, so the reviewer split is clean: R1 owns measurement and inference, R2 owns field literature and construct theory, R3 owns institutional practice, data governance, and equity. No overlap is expected except at the deliberate R1/R3 collision point in item 4.

**6. Register.**
Developmental. The manuscript is competently written and epistemically careful; the author appears to know what they have. The most useful review outcome is not a list of flaws but a clear answer to one question the author has not asked themselves: *is a correct, small, well-hedged replication of a saturated finding publishable, and if so, where and in what format?* That question belongs primarily to the Journal-Fit Reviewer.
