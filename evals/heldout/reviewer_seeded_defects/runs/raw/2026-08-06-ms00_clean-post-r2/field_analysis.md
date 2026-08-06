# Field Analysis Report

## Paper Basic Information

- **Title**: Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students
- **Abstract length**: ≈155 words
- **Full text length**: ≈1,700 words main text (Sections 1–7), ≈2,000 words including abstract and references — unusually short for a full empirical article; effectively a brief report in full-article clothing
- **Number of references**: 6
- **Language**: English (review should be conducted in English)

---

## Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| **Primary Discipline** | Educational technology in higher education — specifically learning technology adoption / student engagement with institutional platforms |
| **Secondary Disciplines** | (1) Information systems — technology acceptance research lineage (TAM/UTAUT); (2) Educational measurement and psychometrics — scale adaptation, single-item measurement, self-report validity; (3) Institutional research / learning analytics — LMS log data, operational decision use |
| **Research Paradigm** | Quantitative, non-experimental. Descriptive-correlational; deliberately framed as association-only with no model testing |
| **Methodology Type** | Cross-sectional survey (single site, voluntary response), analyzed with bivariate correlation (Pearson with Spearman robustness check). No multivariate modeling, no comparison groups, no time dimension |
| **Target Journal Tier** | **Q3** realistic, Q4 floor, Q2 only after substantial extension. Rationale for Q3: the reporting discipline is genuinely above field norm (95% CI, ρ robustness check, sensitivity/power statement, ethics detail, explicit refusal of causal language), which lifts it above Q4 mills. Rationale against Q2/Q1: the entire empirical yield is one bivariate coefficient from one site with a single-item dependent variable; the reference base is 6 items and does not engage the canonical or meta-analytic literature; no theoretical or methodological advance is claimed or delivered. Mainstream Q1/Q2 ed-tech journals (Computers & Education, BJET, Internet and Higher Education, ETHE) would desk-reject on contribution, not on rigor |
| **Paper Maturity** | **Pre-submission on execution, first-draft on contribution.** These two must be separated. Structure is complete, prose is clean, citations are consistently formatted with DOIs, claims are calibrated to the design, limitations are specific rather than boilerplate. But the study's *scope* — 6 references, one correlation, no positioning against known pooled effect sizes — is at a stage where the contribution argument has not been built. Reviewers must not read polish as maturity |

**Integrity pre-flag (must be verified, not assumed):** all six references carry DOIs under the `10.5555/` prefix, which is the reserved non-resolving prefix used for tests and examples, and the journal titles are near-miss variants of real venues (*Computers & Education Review*, *British Journal of Educational Technology Studies*, *Journal of Educational Technology Research*). This is unverified by me and may be an artifact of a de-identified or synthetic manuscript. It is assigned to Peer Reviewer 2 to check against the actual literature and flagged to the Journal-Fit Reviewer for escalation, because if the references are non-existent, that determination overrides all ordinary review commentary.

---

## Recommended Target Journals (Top 3)

1. **Research in Learning Technology** (ALT, open access) — *Best fit and the configured journal for Card #1.* Publishes short empirical papers, values transparent bounded reporting over theoretical novelty, and serves a mixed researcher–practitioner readership that tolerates single-institution evidence when it is honestly framed. The paper's greatest asset (calibration) is what this venue actually rewards.
2. **Electronic Journal of e-Learning** or **Journal of Information Technology Education: Research** — Q3 venues that routinely publish single-institution LMS survey studies. Contribution threshold is reachable without redesigning the study; the main required work is literature positioning, not new data.
3. **Cogent Education** or **Frontiers in Education (Digital Education)** — scope-tolerant, soundness-oriented venues that accept incremental single-site findings if methods and reporting are defensible. Fallback rather than first choice; APC and perceived-prestige tradeoffs should be surfaced to the author explicitly.

*Stretch targets, only after extension:* **Australasian Journal of Educational Technology** or **Education and Information Technologies** — viable only if the study adds LMS log data, a second institution, or a full acceptance model. Not recommended as a first submission in the current form.

---

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC
**Display role**: Journal-Fit Reviewer
**Identity Description**: Associate Editor of *Research in Learning Technology*, a learning-technology researcher who has handled roughly 300 submissions on institutional platform adoption and who chairs her institution's digital education committee. Known for triaging on the "so what for our readers" question within the first two pages and for actively recommending format reclassification (Short Paper / Research Note) rather than rejecting sound-but-thin work outright.

**Review Focus**:
1. **Contribution-to-scope match.** Does one bivariate coefficient from one site justify a full-length research article, or is the honest outcome a Short Paper / Research Note? Assess whether the title and abstract promise more than Section 4 delivers (the abstract's "examined the association" framing is proportionate; the seven-section full-article architecture is not).
2. **Readership interest and fit.** Would this journal's mixed researcher–practitioner audience act on or cite this? Evaluate whether the paper's actual selling point — a transparently reported, design-bounded, non-inflated single-site estimate — is made explicit as a contribution claim, or whether it is left implicit and therefore reads as thin rather than as disciplined.
3. **Positioning against the field's existing answer.** The paper claims to be "an incremental data point, comparable with prior work" (Section 2) but never states what prior work's pooled estimate *is*. Without that anchor, incrementality is asserted, not demonstrated. Judge whether the comparability claim is redeemable in revision.
4. **Integrity escalation.** Verify the reference list resolves to real, locatable sources. If it does not, this becomes an editorial-integrity matter that supersedes the ordinary accept/revise/reject calculus.

**Will particularly care about**: Whether the manuscript's evident honesty is being used as a substitute for contribution. Calibrated hedging is a virtue and should be praised as such, but it does not by itself create a reason for the paper to exist — the verdict must rest on evidence against the criteria, not on how agreeable the prose is.

**Possible blind spots**: Will not audit the statistics. Likely to miss the ordinal/single-item measurement problems, the α-without-dimensionality gap, and the internal contradiction between anonymity and duplicate removal. May also under-weight the equity dimension of who is absent from the sample, since fit judgments tend to stop at scope rather than sample composition.

---

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1
**Display role**: Peer Reviewer 1
**Identity Description**: Quantitative survey methodologist and psychometrician in an education research unit, specializing in measurement of self-reported behavior, ordinal-data treatment, and the consequences of single-item indicators. Teaches a graduate seminar on why attenuation from unreliable measures makes "moderate" correlations uninterpretable, and reviews regularly for measurement-oriented journals.

**Review Focus**:
1. **The single-item ordinal dependent variable.** Section 3.2 measures the entire outcome with one five-point frequency item; Section 3.4 then applies Pearson r and reports a 95% CI [.30, .52] premised on interval-level, bivariate-normal data. The Spearman check (ρ = .40) addresses monotonicity but not the CI's assumptions, and no reliability can be estimated for a single item, so the observed r = .42 is an unknown amount of attenuation away from the construct-level association. Probe whether polyserial/polychoric estimation or an explicit attenuation discussion is required, and whether the CI should be bootstrapped.
2. **Instrument adaptation and dimensionality evidence.** The six-item scale is "adapted from Costa and Wren (2019)" with no report of what was changed, no items reproduced, and no appendix. Cronbach's α = .88 is offered as the sole psychometric evidence — α presumes essential unidimensionality and does not establish it. Ask for the adapted items verbatim, documentation of the adaptation process, a CFA or at minimum an EFA in this sample, and α with a confidence interval.
3. **Sampling accounting and the anonymity/duplicate contradiction.** No response rate is reported because no denominator is given: "All enrolled undergraduates were eligible" (3.1) but the eligible N is absent, making 233 responses uninterpretable. Beyond that, 3.1 states 5 duplicate entries were removed while 3.3 states no identifying information was collected and responses "could not be linked back to individual students" — these cannot both be true as written, and the mechanism of duplicate detection must be disclosed. Sample description is also inadequate: "spanned all four year levels" with no distribution, no discipline mix, no gender or age breakdown, no comparison to institutional population.
4. **Power framing and analytic completeness.** The sensitivity statement (>.80 power for r ≥ .19) is welcome but must be labeled as a priori or post hoc. Descriptives are incomplete: a median category is reported for the use item with no full frequency distribution, and the shared-variance figure is described in prose ("accordingly modest") but never given as a number.

**Will particularly care about**: Whether r = .42 is a property of the constructs or an artifact of the measurement instruments. Until reliability of the outcome measure and dimensionality of the predictor are established, the headline coefficient has no defensible interpretation as "moderate."

**Possible blind spots**: Indifferent to whether the finding matters to the field or to practice; may accept the study as publishable once measurement is patched, without asking whether a corrected coefficient is worth publishing. Unlikely to interrogate the reference list's authenticity or the practical utility of the onboarding recommendation.

---

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2
**Display role**: Peer Reviewer 2
**Identity Description**: Senior educational technology researcher who has published meta-analytic and synthesis work on technology acceptance in education, and who has spent a decade arguing in print that the field has an oversupply of single-site TAM correlations and an undersupply of studies that specify what they add to the pooled estimate. Familiar with the Davis-to-UTAUT lineage and with the existing meta-analyses of the perceived-usefulness/use relationship.

**Review Focus**:
1. **Literature base adequacy and canonical omission.** Six references for a technology-acceptance paper is not a lean literature review, it is an absent one. The foundational acceptance literature (Davis 1989; Venkatesh and colleagues on UTAUT) is uncited, and — more damaging to this paper's specific self-positioning — the existing meta-analyses of exactly this association are uncited. Section 2 says prior "effect sizes vary across samples and instruments" without reporting a single one.
2. **The incrementality claim.** The paper stakes its contribution on being "an incremental data point, comparable with prior work" (Section 2) and "consistent with prior technology-acceptance research" (Sections 4 and 5). Both claims require a stated benchmark. Where does r = .42 fall relative to established pooled estimates — at the center, in a tail, or outside the reported range? Without this, "consistent with" is unfalsifiable and the contribution collapses to "we ran a correlation." This is the single highest-leverage revision available to the authors and requires no new data.
3. **Construct positioning: use frequency as an outcome.** The paper never defends access frequency as a construct worth explaining. The acceptance literature has moved toward quality and depth of engagement precisely because frequency conflates compliance-driven access with meaningful use — a tension the paper brushes against ("course requirements and assessment schedules," Section 4) without addressing. Also assess whether Section 5's onboarding implication is warranted by the literature it invokes, given that Whitfield (2019) is characterized as a practitioner account.
4. **Reference verifiability and open materials.** Check whether the six cited sources exist and are correctly characterized; report specifically what was searched and what resolved. Separately, note the absence of any data-availability, materials-availability, or analysis-code statement — for a paper whose stated value is comparability with prior work, non-reproducible materials undercut the contribution claim directly.

**Will particularly care about**: Whether this study knows what the field already knows. A well-hedged replication is genuinely publishable, but only if it is positioned as a replication against a specified prior estimate rather than presented as an isolated finding.

**Possible blind spots**: Prone to demanding a full structural model or mediation analysis that a single-item outcome and n = 214 cannot support — a recommendation Peer Reviewer 1 will contradict. May also undervalue the legitimate scientific worth of small, honest, non-inflated estimates, and is unlikely to notice the recruitment-channel selection problem.

---

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3
**Display role**: Peer Reviewer 3
**Identity Description**: Director of institutional research and learning analytics at a public university, responsible for LMS engagement dashboards, digital-equity reporting, and the evidence packages that go to provosts before platform and onboarding budget decisions. Reviews from the position of the person who would have to act on this paper: has both the log data and the survey infrastructure, and has repeatedly seen "students who like it use it more" findings fail to change any decision.

**Review Focus**:
1. **The recruitment channel is inside the construct being measured.** The survey was distributed "through the institution's course-announcement channel" (3.1) — that is, through the very platform whose use is the dependent variable. Students who rarely access the LMS are therefore structurally less likely to have seen the invitation. This is not generic volunteer bias, which Limitation 4 does mention; it is selection on the outcome variable, producing range restriction at the low end and likely biasing r. The paper's own Limitation 4 gestures at "students who engage more with institutional channels may be overrepresented" without recognizing that the channel *is* the LMS and that this specifically compromises the headline coefficient. Requires explicit treatment, and ideally a comparison of respondent log-activity distribution against the full student body.
2. **Decision utility: what changes at 9 a.m. Monday?** Section 5 recommends onboarding that "helps students see concrete usefulness." Ask what this study contributes to that recommendation that was not already assumed before the study ran, and what a practitioner would do differently at r = .42 versus r = .25 or r = .60. If no decision threshold exists, the practical implication should be stated as a hypothesis for future intervention work, not as an implication of these data.
3. **Feasibility gap the paper does not acknowledge.** The institution self-evidently possesses LMS log data — it distributed the survey through the platform. Limitations 2 and the Conclusion both call for behavioral log data as *future* research, without explaining why log data was not obtained here. Was it a governance, IRB, or capacity constraint? Stating this converts a soft limitation into a credible account of design tradeoffs, and it is information practitioners need in order to judge transferability to their own setting.
4. **Equity blind spot.** The policy-relevant population is precisely the low-engagement students — those least likely to be in this sample. The paper treats non-use as a perception problem, with no consideration of device access, connectivity, off-campus study, caregiving or employment load, disability and accessibility barriers, or LMS design failures. Framing low use as a perception deficit rather than a structural or access barrier is an unexamined assumption with real consequences for the intervention the paper proposes.

**Will particularly care about**: That the students this finding is supposedly about are the ones most likely missing from the data, and that the resulting recommendation locates the problem in student perception rather than in institutional provision or platform design.

**Possible blind spots**: Not equipped to adjudicate correlation coefficient estimation, scale dimensionality, or CI assumptions. May undervalue incremental descriptive research on principle, and may push for a study the authors were not resourced to conduct rather than for improvements to the study they did conduct.

---

## Review Strategy Recommendations

**Register: developmental, but the verdict stays evidence-based.** This is the defining feature of this manuscript and the main risk to the review. The paper is unusually well-calibrated — it refuses causal language, names the reverse-causation pathway, cites a methodological caution against its own measure, and reports a CI and a robustness check. That deserves explicit, specific praise, because it is rarer than it should be. But tone must change wording, never the verdict: the substantive problems (a single-item outcome carrying the whole result, a 6-reference literature base with no benchmark, recruitment through the outcome variable's own channel, no response rate, and an anonymity/duplicate-removal contradiction) are independent of how gracefully the paper is written. Reviewers who feel disarmed by the humility should be treated as having a calibration problem, not as having found a strength that offsets thin evidence.

**Coverage strategy across reviewers.** The paper sits at the intersection of educational technology, information systems, and measurement. Reviewer 2 owns the primary discipline and its literature; Reviewer 1 owns the measurement and sampling machinery; Reviewer 3 owns the institutional-practice and equity perspective that neither of the others is positioned to see. Assigned ownership is deliberately non-overlapping on the sampling issue in particular: **Reviewer 1** owns the missing denominator, absent response rate, and thin sample description; **Reviewer 3** owns the recruitment-channel-as-outcome-variable selection problem. Both touch Limitation 4; they must not duplicate each other's argument.

**Predicted tension requiring synthesis.** Reviewer 2 will likely ask for a fuller acceptance model or theoretical framing. Reviewer 1 will hold that a single-item outcome of unknown reliability cannot support additional modeling and that the existing coefficient is not yet interpretable. Reviewer 3 will ask for log data the authors may not be able to obtain. These three demands cannot all be satisfied in one revision. The synthesizer should resolve them into two clearly separated paths and hand the choice to the author with the real costs stated in plain terms:

- **Path A — reframe within existing data.** Reclassify as a Short Paper / Research Note, add the meta-analytic benchmark and state where r = .42 falls against it, reproduce the adapted items and add dimensionality evidence, disclose the eligible-N denominator and response rate, resolve the anonymity/duplicate contradiction, and treat the recruitment channel as a threat to the estimate rather than a generic volunteer caveat. No new data collection. Realistic outcome: a defensible Q3 publication.
- **Path B — extend the study.** Add LMS log data as an outcome, or a second institution, and only then attempt model testing. Realistic outcome: Q2 becomes plausible; cost is a new data-collection cycle and governance approval.

Path A is the recommendation unless the authors want the Q2 target, in which case the honest advice is that the current dataset cannot get them there no matter how well it is written up.

**Integrity gate precedes everything.** Reviewer 2's reference-verification task must be reported with specifics — what was searched, what resolved, what did not — and must not be summarized as a general impression. If the references prove non-existent, the Journal-Fit Reviewer's editorial-integrity finding governs the outcome and the substantive review commentary becomes secondary.
