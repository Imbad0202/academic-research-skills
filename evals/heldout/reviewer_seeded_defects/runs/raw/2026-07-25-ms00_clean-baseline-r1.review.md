# Isolated-dispatch panel review — gamma-1 (baseline condition, 2026-07-25)

(Phase 1 calls were physically separated: each seat’s pre-commitment was produced by a clean
headless `claude -p` call — claude-opus-5, effort xhigh, thinking enabled — that received only
the contract + title/field/word_count and was forbidden from reading any manuscript. Phase 2,
field analysis, and synthesis were separate paper-visible headless calls with read scope
limited to the named skill files and the neutral-named manuscript copy.)

# PART 1 — FIELD ANALYSIS

# Field Analysis Report

## Paper Basic Information
- **Title**: Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students
- **Abstract length**: ~155 words
- **Full text length**: ~1,750 words (excluding references)
- **Number of references**: 6

---

## Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| **Primary Discipline** | Educational technology in higher education — specifically student adoption/engagement with institutional learning platforms (LMS) |
| **Secondary Disciplines** | (1) Information systems / technology-acceptance research (TAM lineage); (2) Educational measurement & psychometrics (scale adaptation, single-item ordinal measurement); (3) Learning analytics / institutional research (self-report vs. behavioral-log evidence) |
| **Research Paradigm** | Quantitative Research — descriptive-correlational, non-inferential in ambition; explicitly non-causal and non-model-testing by the authors' own framing (§1, §5) |
| **Methodology Type** | Survey / Questionnaire — single-site cross-sectional census-eligible convenience survey (n = 214 of an all-undergraduate eligible frame), analyzed with bivariate correlation (Pearson primary, Spearman robustness) plus an a priori sensitivity/power statement |
| **Target Journal Tier** | **Q3**, with a plausible Q2 ceiling only in a "short report" / "brief communication" track. Rationale: the design is sound and unusually well-hedged, but the substantive contribution is a single bivariate correlation from one institution with no theoretical extension, no multivariate control, and no behavioral criterion. The reference list is 6 items — thin even for a short report — and cites no canonical TAM/UTAUT primary sources (Davis, Venkatesh), only intermediary secondary sources. Q1 field journals (*Computers & Education*, *BJET*) would desk-reject on incremental-contribution grounds regardless of execution quality. The paper's own self-positioning ("incremental data point," "modest, design-bounded evidence") is honest and correctly calibrated to Q3. |
| **Paper Maturity** | **Pre-submission.** Rationale: structure is complete and conventional (IMRaD + separate Limitations + Conclusion); prose is polished with no drafting artifacts; APA-7-consistent reference formatting with DOIs throughout; results reported to modern standards (point estimate + 95% CI + p + n + robustness check); ethics subsection present and specific. Remaining gaps are substantive-contribution and reporting-completeness issues, not draft-stage incompleteness. |

**Note on an unusual profile**: this manuscript inverts the common failure pattern. Most submissions at this evidence level over-claim; this one systematically *under*-claims, and the reviewers must be configured to test whether the hedging is genuine epistemic discipline or a rhetorical shield that lets a thin contribution pass without scrutiny. Every reviewer card below carries an explicit instruction on this axis, because a panel that simply rewards visible caution will produce a uselessly favorable review.

---

## Recommended Target Journals (Top 3)

1. **Journal of Computing in Higher Education** (Springer, Q2/Q3 band) — Publishes single-institution empirical studies of technology use in HE, and its readership accepts bounded descriptive contributions when the design and reporting are transparent. Best fit for the paper as written; would likely still ask for multivariate context or a behavioral-data supplement.

2. **Australasian Journal of Educational Technology** (open access, Q2/Q3) — Explicitly welcomes short empirical reports and single-site institutional studies of LMS/platform engagement; the paper's self-limiting framing matches AJET's editorial culture better than a theory-testing venue would. Realistic acceptance target after revision.

3. **International Journal of Educational Technology in Higher Education (ETHE)** or, as a lower-risk alternative, a regional/practitioner venue such as *Research in Learning Technology* — ETHE is the stretch option (higher tier, will demand more than one correlation); *Research in Learning Technology* is the safe landing zone if the authors decline to add analytic depth. Listing both signals the fork the authors face: add multivariate/behavioral substance and aim up, or accept a specialist/practitioner venue.

---

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC (Editor-in-Chief)
**Identity Description**: Editor-in-Chief of *Journal of Computing in Higher Education*, a higher-education technology scholar who has handled roughly 400 LMS/technology-acceptance submissions over twelve years and now desk-rejects the majority of single-site TAM-adjacent correlational surveys; has publicly argued in editorials that the field is saturated with "perceived usefulness correlates with self-reported use" replications and has instituted a "what does this change?" screening question for all such submissions.
**Review Focus**:
  1. **Incremental-contribution triage** — Determine whether a single bivariate correlation (r = .42) from one institution, with no moderator, no multivariate control, and no theoretical extension, clears the journal's contribution bar. Ask explicitly: if this paper did not exist, what would readers not know? Test whether the answer is genuinely "nothing" or merely "little."
  2. **Fit and readership value** — Assess whether the practical implication offered (LMS onboarding should demonstrate concrete usefulness) is actually supported by this study or is a pre-existing intuition that the correlation merely decorates. Check whether the Discussion's practitioner turn (§5, Whitfield, 2019) is doing argumentative work the data cannot bear.
  3. **Honest-framing audit (the paper's defining feature)** — Evaluate whether the pervasive hedging ("modest," "incremental," "design-bounded," "not causal") represents exemplary epistemic discipline that should be rewarded, or a strategy that converts thinness into apparent virtue. Formulate an explicit position: does correct self-description of a limitation cure the limitation, or only disclose it?
**Will particularly care about**: Whether "we know our study is small and correlational" is being used as a substitute for contribution rather than as a caveat on one; and whether the journal's readers — practitioners and institutional researchers — gain any actionable decision from r = .42 that they did not already hold as folk knowledge.
**Possible blind spots**: An EIC optimizing for contribution significance may undervalue the paper's genuine methodological virtues (CI reporting, a priori power statement, Spearman robustness check, honest limitations) and may reject on novelty grounds without crediting reporting quality that most submissions in this genre lack. May also under-attend to statistical detail, assuming the numbers are fine because the prose is careful. The synthesizer must ensure the EIC's contribution verdict does not suppress R1's and R2's technical findings.

---

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1 — Methodology (Quantitative / Survey Psychometrics)
**Identity Description**: Quantitative methodologist in educational measurement, specializing in survey psychometrics and the statistical treatment of ordinal and single-item measures; teaches a doctoral seminar on correlation-versus-agreement and reliability attenuation, publishes on measurement error in self-report educational data, and routinely serves as a statistical reviewer for education journals.
**Review Focus**:
  1. **Single-item ordinal outcome vs. Pearson correlation** — The outcome is one five-point frequency item with unequal, verbally labeled category widths ("rarely or never" through "several times daily"), yet the primary estimate is Pearson's r, with Spearman relegated to a robustness footnote (ρ = .40). Interrogate: is the parametric coefficient the defensible primary estimate here, or is the ordinal-appropriate coefficient the correct primary with Pearson as the supplement? Also examine the unreported reliability of a single-item measure — Cronbach's α is given for the six-item predictor (.88) but no reliability estimate whatsoever exists for the criterion, and single-item reliability is typically far lower. Assess whether attenuation due to criterion unreliability means the reported r = .42 substantially understates (or, through other channels, misstates) the true association, and whether the paper should report a disattenuated estimate or at minimum acknowledge attenuation.
  2. **Reporting completeness and verifiability of the analytic claims** — Several analytic assertions are stated but not evidenced: the scatterplot inspection and distributional symmetry claims (§3.4) are asserted without any figure or numeric support (no skewness/kurtosis values, no plot); the power statement (">.80 power to detect r ≥ .19") should be checked for arithmetic correctness at n = 214, α = .05 two-tailed; the Results paragraph says "the proportion of variance shared by the two measures was accordingly modest" without ever reporting r² (= .18) — a substantive value hidden behind a qualitative phrase. Also verify that no descriptive statistics are given for the outcome beyond a median category — no distribution, no dispersion, no floor/ceiling assessment on a five-point frequency item where ceiling effects are plausible.
  3. **Sample construction, response rate, and exclusion transparency** — The response denominator is never given: 233 responses from "all enrolled undergraduates" at a mid-sized university implies a response rate that is likely in the low single digits, but the eligible population size is never stated, so the response rate is unreportable and the nonresponse-bias magnitude unassessable. Examine the exclusion rules (14 incomplete, 5 duplicate): how were duplicates identified in a survey that collected "no identifying information" and where "responses could not be linked back to individual students" (§3.3)? These two statements are in tension and one of them must be qualified. Also assess whether "spanned all four year levels" is an adequate substitute for reporting the actual demographic composition.
**Will particularly care about**: Whether the measurement model is adequate to the inferential claim — specifically that a single unvalidated ordinal item with unknown reliability is being correlated with a validated multi-item scale, and whether the paper's careful causal hedging has distracted attention from an unhedged *measurement* problem that operates independently of the cross-sectional design.
**Possible blind spots**: May treat the paper as fundamentally sound-but-thin and confine critique to technical reporting fixes, without confronting whether the whole exercise is worth publishing (EIC territory). May also accept the ethics/anonymity claims at face value as an administrative matter rather than following the duplicate-detection contradiction into its IRB implications — R3 is configured to carry that thread.
**Adjustment note**: Per the field-analyst protocol for descriptive-correlational work, this reviewer's mandate extends beyond "is the design rigorous" to "is the measurement instrument capable of supporting even the modest claim made" — because when a paper deliberately shrinks its claims, measurement adequacy, not causal identification, becomes the binding constraint.

---

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2 — Domain (Technology Acceptance / Educational Technology in Higher Education)
**Identity Description**: Senior educational-technology researcher whose program of work is the empirical history of the Technology Acceptance Model in education; author of a meta-analysis synthesizing perceived-usefulness–to–use correlations across higher-education samples, and a frequent critic of what the field calls "TAM replication inflation"; knows the primary-source literature (Davis 1989; Venkatesh & Davis 2000; Venkatesh et al. 2003; Šumak et al. 2011) and the LMS-specific engagement literature in detail.
**Review Focus**:
  1. **Literature foundation and citation adequacy** — Six references for a paper positioning itself inside the technology-acceptance tradition is unusually thin, and none of the canonical primary sources of that tradition are cited; perceived usefulness is defined in §2 in essentially Davis's original terms but attributed to two secondary sources (Costa & Wren, 2019; Delgado, 2020). Assess whether the construct's provenance is properly credited, whether the omission of TAM's primary literature and of any existing meta-analytic synthesis is defensible, and whether "consistent with prior technology-acceptance research" (§5) is a verifiable claim or an unanchored gesture when the comparison set is three papers.
  2. **Benchmarking the estimate against the known distribution** — The paper repeatedly says its finding is "consistent with prior research" but never states what prior research found. Since meta-analytic estimates of the perceived-usefulness/use association exist, evaluate whether r = .42 actually sits where the paper implies, whether the 95% CI [.30, .52] overlaps published pooled estimates, and whether the paper's own cited source (Song, 2018, multi-campus, explicitly reporting between-institution variability) should have been used to place this single-site estimate within a distribution — the paper names this logic in §2 ("one point in a distribution") and then fails to execute it in §5. This is a concrete, actionable gap: the comparison the paper promises is never performed.
  3. **Genuine contribution to the field's knowledge base** — Determine what a reader of this literature learns. If the association is already well established meta-analytically, a single-site replication contributes only if it adds moderator information, a distinctive population, an improved measure, or a preregistered replication design — assess whether any of these are present. Evaluate the stated contribution ("a single, transparently reported association … using a previously validated measure") against whether transparency alone constitutes a contribution, and whether the adaptation of the Costa & Wren instrument was itself re-validated in this sample (α is reported, but α is not validity, and no factor structure is examined).
**Will particularly care about**: Whether the paper's honest self-limitation is being allowed to substitute for the field-situating work it explicitly promises and then never delivers — the manuscript announces the correct interpretive frame ("one point in a distribution") in the Literature Review and then, in Discussion and Conclusion, quietly reverts to standalone reporting without ever locating its estimate against any numeric benchmark.
**Possible blind spots**: Deep familiarity with TAM may lead this reviewer to over-weight canon-citation completeness and treat "add these references" as the fix, when the deeper issue is contribution (EIC) or measurement (R1). May also be unduly reassured by the paper's correct causal hedging, since that is the error this reviewer most often has to correct in submissions, and therefore under-notice the unhedged measurement and reporting problems.

---

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3 — Cross-disciplinary / Practical (Learning Analytics + Institutional Research Ethics)
**Identity Description**: Learning-analytics scientist and institutional-research director who works with LMS server-side event logs at scale, co-authored institutional guidance on the ethics of student-data collection, and has published on the systematic divergence between self-reported and log-measured platform engagement; sits on a university research-ethics committee and reviews student-survey protocols.
**Review Focus**:
  1. **The behavioral-data question the paper raises and then declines to answer** — This study measures LMS use by asking students, at an institution that by definition operates an LMS producing complete server-side access logs for every respondent. The paper cites Vasquez (2020) establishing that self-report diverges "sometimes substantially" from log data, correctly concedes the point in §6, and then proceeds anyway. Interrogate why the criterion measure was not the log data, whether the divergence literature implies the reported r = .42 is an estimate of the association between *perception and perception* rather than perception and behavior, and whether availability of the objective criterion converts this from an acknowledged limitation into an avoidable design choice. This is the single most consequential cross-disciplinary observation available on this manuscript and it is invisible from within a survey-methods frame.
  2. **The anonymity–deduplication contradiction and its ethics/feasibility implications** — §3.3 asserts no identifying information was collected and that responses could not be linked to individuals; §3.1 reports removal of 5 duplicate entries. Deduplication requires some persistent identifier (IP, session token, cookie, institutional SSO handle, device fingerprint), each of which is identifying or quasi-identifying under most institutional data-governance regimes. Assess which claim is inaccurate, what the actual data-collection mechanism must have been, whether the consent language shown to students correctly described it, and whether an ethics committee reviewing the *as-executed* protocol would find the anonymity representation accurate. Note that this also bears on R1's methodological concern (the integrity of the exclusion rule) — flag the overlap for the synthesizer rather than duplicating the statistical analysis.
  3. **Institutional decision-usefulness and sampling ecology** — From a practitioner-decision standpoint, evaluate whether an institution could act on this finding. Recruitment ran through "the institution's course-announcement channel" — a channel located *inside or adjacent to* the very platform under study, which structurally over-samples students already engaged with institutional digital communication and plausibly inflates both variables simultaneously. Assess whether this is a garden-variety volunteer-bias issue (as §6 frames it) or a design-specific confound that could bias the correlation itself, not merely its generalizability. Then judge the onboarding recommendation in §5 against what an institutional decision-maker would actually need (which students, at what point, with what intervention, at what cost).
**Will particularly care about**: Whether the study's core measurement decision was necessary or merely convenient — because a limitation that could have been eliminated with data the institution already holds is a different kind of limitation than one imposed by circumstance, and the manuscript's uniformly apologetic framing flattens that distinction.
**Possible blind spots**: May under-weight the legitimate scholarly reasons to study *perceived* engagement as a construct in its own right (perception can be the theoretically appropriate outcome in acceptance research), and may hold a self-report study to a log-data standard that the acceptance-research tradition does not require — R2 should be relied upon to defend the tradition's own standards where warranted. May also frame ethics findings more severely than an editorial decision warrants, since these read as reporting-accuracy defects rather than misconduct.
**Cross-disciplinary rationale**: This reviewer's angle is genuinely orthogonal to R1's and R2's. R1 asks whether the numbers were computed correctly; R2 asks whether the field already knows this; R3 asks why a proxy was measured when the criterion itself was sitting in the institution's own database — and follows the data-governance thread that neither statistical nor domain expertise would surface.

---

## Review Strategy Recommendations

**Special characteristics of this paper requiring particular attention**

1. **The hedging paradox is the central review problem.** This manuscript is unusual: its rhetoric is more disciplined than most published work in its genre. It refuses causal language, reports a CI, runs a robustness check, states power a priori, names the self-report limitation, and describes itself as "incremental" and "design-bounded." A panel that pattern-matches on "does this paper over-claim?" will return an undeservedly favorable review. Every reviewer has therefore been instructed to evaluate the *substance behind* the hedge. The operative question for the panel is not "is the paper honest about its limits?" (it is) but "does correctly naming a limitation resolve it?" The panel should reach an explicit, stated position on this — it is the axis on which the editorial decision turns.

2. **Under-claiming has its own failure modes, and two are present.** First, hedged prose can conceal unhedged defects: the causal caveat is thorough while the *measurement* caveat is absent (no criterion reliability, single ordinal item analyzed parametrically as primary). Second, qualitative hedging can substitute for numbers the authors owe the reader: "the proportion of variance shared … was accordingly modest" is r² = .18 written in words, and "consistent with prior research" is a benchmark comparison that is promised in §2 and never performed. Both are concrete, fixable, and should appear as specific revision requests, not as tone complaints.

3. **One internal contradiction is load-bearing and should not be missed.** §3.1 (5 duplicates removed) and §3.3 (no identifying information; responses not linkable to individuals) cannot both be literally true as written. It is most likely a reporting imprecision rather than misconduct, and reviewers should say so plainly — but it touches sample integrity (R1) and ethics representation (R3) simultaneously, and it must be raised once, clearly, rather than either dropped or amplified into an accusation.

4. **The reference list is a structural weakness, not a formatting one.** Six references, no TAM primary sources, no meta-analytic anchor, and every empirical comparison mediated through secondary citation. R2 owns this; the synthesizer should ensure it is framed as "the paper cannot substantiate its central comparative claim" rather than the weaker and more easily dismissed "please add citations."

5. **Developmental-vs-gatekeeping calibration.** Per the protocol's maturity handling, this is a pre-submission manuscript, not a first draft — full accept/reject judgment is appropriate and reviewers should not soften into developmental coaching. That said, the paper's execution quality is real and should be credited explicitly in the decision letter; a reject-or-major-revision verdict here should turn on contribution and measurement, and should say so, so the authors can act rather than merely feel discouraged.

**Potential complementarity and tension between reviewers**

- **Designed complementarity.** The four seats form a decision chain with no overlap: EIC asks *should this be published at all* (contribution); R1 asks *are the numbers right and adequately reported* (measurement and statistics); R2 asks *does the field already know this, and is the claim anchored* (literature and benchmarking); R3 asks *why was a proxy used when the criterion was available, and does the data story hold together* (behavioral data and ethics). Each can be answered independently; none presupposes another's verdict.

- **Expected tension 1 — EIC vs. R1/R2 on severity.** The EIC is configured to be sceptical of incremental TAM replications and may favor rejection on contribution grounds alone. R1 and R2 will likely produce lists of fixable defects, which reads as "major revision." The synthesizer must not average these into a soft middle: the correct resolution is to state whether the identified defects are curable *within this design* (R1's reporting fixes: yes; R2's benchmarking: yes; the single-item criterion: only partially; the contribution deficit: not by revision alone).

- **Expected tension 2 — R3 vs. R2 on whether self-report is a defect.** R3 will argue the log data should have been the criterion; R2 may defend perceived engagement as a legitimate construct within acceptance research. This tension is productive and should be preserved in the decision letter rather than resolved by fiat — the honest position is that self-report is defensible *if the paper claims a perception–perception association*, and the paper's own title and abstract ("Self-Reported Use") mostly do this, while §5's onboarding implication quietly assumes behavior. The panel should ask the authors to make that boundary explicit and consistent throughout.

- **Expected tension 3 — everyone risks rewarding tone.** All four reviewers are exposed to the same failure mode: the manuscript is pleasant to read, appropriately modest, and gives reviewers little to attack rhetorically. The synthesizer should verify that each reviewer's report contains at least one finding that is independent of the paper's framing — a defect that exists in the data, the measures, the reference list, or the internal consistency of the Methods, regardless of how the paper describes itself. A report consisting only of "well-hedged but thin" should be treated as an incomplete review and returned for a second pass.

- **Deliberate overlap to manage.** The anonymity/deduplication contradiction sits in both R1's and R3's remit by design (it is simultaneously a sample-integrity and an ethics-representation issue). The synthesizer should consolidate it into a single numbered finding with both framings attached, rather than listing it twice at different severities — duplicated findings inflate apparent defect count and distort the decision.

# PART 2 — SEATS

## SEAT — EIC

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** From the editor's chair, this dimension asks whether the study's design, data handling, statistical reporting, and reproducibility affordances clear the routine peer-review bar for educational-technology research. My role is not to referee statistical technique in depth — that belongs to the methodology seat — but to judge whether the manuscript's evidentiary machinery is sound enough that the journal could stand behind its conclusions. For a cross-sectional survey of undergraduate LMS use, the editorially relevant question is whether the paper reports enough about sampling, instrumentation, response rates, and analysis that a reader could tell what was actually done and whether the inference from a one-time self-report survey is licensed.

**D2 — domain_accuracy (mandatory).** This dimension asks whether the paper's claims sit correctly inside the existing evidence base on technology acceptance and student engagement with institutional learning platforms, whether prior work is represented faithfully, and whether domain terminology is used correctly. As EIC I care about this because a journal's credibility rests on not publishing work that misstates its own field. In this specific field, "perceived usefulness" and "self-reported use" are load-bearing constructs from a well-established acceptance literature, and misusing or under-crediting that lineage — or treating a decades-old finding as novel — is an accuracy failure with editorial consequences, not merely a citation nicety.

**D3 — argumentative_coherence (mandatory).** This dimension asks whether the manuscript's central thesis holds together: whether the stated research question, the evidence produced, and the conclusions drawn form a chain without breaks, and whether any fallacy undermines the core argument. This is the heart of my seat's remit, because incoherence between what a paper promises in its title and abstract and what it actually delivers in its results is the classic editorial reject signal. The specific hazard for a correlational self-report survey is the slide from association to causation or to prescriptive recommendation, and the related hazard of a title that announces more than a cross-sectional design can deliver.

**D4 — cross_disciplinary_relevance (high priority).** This dimension asks whether the framing, definitions, and implications travel beyond the immediate sub-field — whether an adjacent-field reader (an instructional designer, a higher-education administrator, an information-systems scholar) can follow what was studied and why it matters, and whether any interdisciplinary claim the paper makes is actually substantiated. This maps directly onto my journal-fit and significance duties: a paper that only speaks to a single institution's LMS rollout, with no articulated relevance to a broader readership, may be competent work that still does not belong in this venue. It is high priority rather than mandatory, which I read as: weakness here shapes the decision but does not by itself sink the paper.

**D5 — writing_and_structure (normal priority).** This dimension asks whether the manuscript is organised and expressed well enough to be read — clear exposition, usable figures and tables, adherence to venue conventions. As EIC I treat this as the lowest-stakes dimension because prose and formatting are the most repairable defects in the review cycle. It nonetheless carries real editorial weight when structural problems obscure what was done, or when the manuscript's length is grossly mismatched to the venue's article conventions. At 1,597 words, this submission sits far below the typical empirical-article length for the field, so the editorially live question is whether the structure is thin-but-complete (a short-report form) or structurally incomplete for the claims it makes.

## Scoring Plan

### D1: methodology_rigor

- **what_to_look_for**: Whether the sampling frame, recruitment route, and response rate are stated; whether the sample size is reported and adequate for the analyses performed; whether the survey instrument is identified (adapted from a validated scale vs. author-built) with reliability evidence; whether "self-reported use" is defined and operationalised as a measured variable rather than an impression; whether the analysis reported matches the design (correlational statistics for cross-sectional data); whether effect sizes and uncertainty accompany any significance claims; whether ethics approval/consent and any data or instrument availability statement appear. I will also check whether the paper acknowledges common-method variance — both predictor and outcome are self-report from the same instrument at the same time — since that is the defining methodological constraint of this design.
- **what_triggers_block**: Core evidentiary machinery is absent or unrecoverable — no reported sample size or sampling procedure; no description of the instrument at all; numeric claims or statistical conclusions presented with no stated analysis that could have produced them; or an analysis whose form is incompatible with a single-wave cross-sectional survey (e.g., longitudinal/causal estimation asserted from one-time data). Also blocks if reported figures are mutually inconsistent to a degree that no reading reconciles them.
- **what_triggers_warn**: The design is legible and the analysis is appropriate, but material reproducibility affordances are thin — e.g., instrument items not provided or not traceable to a validated source, reliability coefficients missing, response rate unreported while a population is implied, effect sizes omitted in favour of bare p-values, ethics/consent statement absent, or the common-method and single-institution constraints go unmentioned in the limitations.

### D2: domain_accuracy

- **what_to_look_for**: Whether "perceived usefulness" is used in its established technology-acceptance sense and attributed to that lineage rather than reinvented; whether the LMS-adoption and student-engagement literature the paper leans on is represented accurately (findings attributed to the right studies, direction of reported effects preserved, scope of cited claims not inflated); whether the paper states what is already known about the usefulness–use association and positions its own contribution against that baseline honestly; whether higher-education and platform terminology (LMS vs. VLE vs. courseware, adoption vs. engagement vs. usage) is used consistently and correctly; whether cited references appear real, retrievable, and topically apposite.
- **what_triggers_block**: A factual misstatement of the domain that the argument rests on — a core construct defined incorrectly or conflated with a different construct in a way that changes what the results mean; prior findings reported with the wrong direction or attributed to work that does not contain them; apparently fabricated or non-existent citations; or a novelty claim that directly contradicts well-established, uncontested findings in the acceptance literature without engaging them.
- **what_triggers_warn**: The domain content is broadly correct but the positioning is loose — the acceptance-theory lineage is under-acknowledged or cited only glancingly; the literature engaged is dated, thin, or geographically/institutionally narrow relative to the claim being made; terminology drifts between sections without definitional harm; or the paper restates a well-known association without saying what it adds beyond confirmation.

### D3: argumentative_coherence

- **what_to_look_for**: Whether the title, abstract, stated research question, results, and conclusion form a consistent chain; whether the conclusion answers the question actually asked; whether the causal language in the discussion is licensed by a cross-sectional correlational design; whether recommendations to instructors, designers, or administrators are proportionate to the evidence produced; whether alternative explanations (reverse causation — heavier users rating the platform more useful; third variables such as course requirements mandating LMS use; self-report bias) are considered; whether the paper avoids over-promising in the front matter and under-delivering in the results.
- **what_triggers_block**: A break in the chain that invalidates the central argument — the conclusion asserts something the reported results do not test or contradict; causal or effectiveness claims ("improves", "leads to", "drives use") are made from single-wave correlational data and carried into the abstract or conclusion as findings; or the paper's stated research question and its actual analysis are about different things. Also blocks on a central argument sustained by a clear fallacy (e.g., treating a correlation as demonstrating the intervention's efficacy, or generalising from one institution to a population-level claim as a finding rather than a conjecture).
- **what_triggers_warn**: The core chain holds but slips at the edges — occasional causal phrasing in the discussion that the design does not support while the formal claims stay correlational; policy or practice recommendations stretched somewhat beyond the evidence; reverse causation or confounding acknowledged only in passing or not at all while the interpretation quietly assumes one direction; or a title/abstract that promises marginally more scope than the results deliver.

### D4: cross_disciplinary_relevance

- **what_to_look_for**: Whether the paper explains its constructs and its institutional setting well enough for a reader outside educational technology (higher-education administration, information systems, instructional design, learning analytics) to follow; whether the LMS context is described sufficiently that findings can be interpreted against a different platform or system; whether implications are articulated for someone beyond the authors' own institution; whether any claim that reaches into an adjacent discipline (organisational adoption, HCI, psychometrics) is actually supported rather than gestured at; whether the framing states why this matters now for institutions making platform investment and engagement decisions.
- **what_triggers_block**: The framing is so locally bounded or so under-defined that an adjacent-field reader cannot determine what was studied or what would transfer — key constructs left undefined and unreferenced, the platform and setting unspecified so no comparison is possible, or an interdisciplinary claim asserted as a finding with no supporting evidence anywhere in the paper.
- **what_triggers_warn**: The work is legible and situated but its reach is narrow — implications are stated only for the authors' own institution or course context with no articulated transfer; adjacent-field readers would need to supply the acceptance-theory background themselves; the "so what" for practitioners or administrators is implied rather than stated; or interdisciplinary framing appears in the introduction but is never carried through to the discussion.

### D5: writing_and_structure

- **what_to_look_for**: Whether the manuscript carries the sections its claims require (abstract, introduction with a stated question, methods, results, discussion, limitations, conclusion, references); whether the 1,597-word length is handled honestly as a short-report/brief-communication form with a correspondingly bounded claim, or whether it is a full empirical claim in a truncated container; whether tables and figures (if present) are self-explanatory, correctly captioned, and consistent with the text; whether the prose is clear and free of ambiguity that obscures method or result; whether reference formatting and venue conventions are followed consistently; whether the abstract is a faithful miniature of the paper.
- **what_triggers_block**: Structural incompleteness that prevents evaluation — a required section (most critically methods or results) is missing or so compressed that what was done cannot be determined; tables/figures contradict the text or are cited but absent; or the exposition is unclear to the point that the central finding cannot be identified with confidence.
- **what_triggers_warn**: The manuscript is complete and readable but under-developed or uneven — sections present yet disproportionately thin relative to their load (typically methods or limitations); the length sits well below venue norms for a full empirical article without the paper acknowledging or adopting a short-report framing; abstract and body diverge in emphasis or reported numbers; figures/tables under-labelled or redundant with the text; or citation formatting and venue conventions applied inconsistently.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## EIC Review Report

### Reviewer Identity

Editor-in-Chief, *Journal of Computing in Higher Education*. Higher-education technology scholar; roughly 400 LMS and technology-acceptance submissions handled over twelve years; author of editorials arguing that the field is saturated with "perceived usefulness correlates with self-reported use" replications, and originator of this journal's standing screening question for such submissions: *what does this change?*

### Overall Recommendation

**Major Revision**

### Confidence Score

**4** — High confidence. Contribution, fit, framing coherence, and reference-base adequacy are squarely within my editorial remit. Statistical technique (the choice of Pearson as primary estimator for an ordinal criterion, attenuation from unreported criterion reliability) I flag but do not adjudicate; that belongs to the methodology seat.

### Summary Assessment

This is a competently executed, unusually well-disciplined single-site cross-sectional survey (n = 214) reporting one bivariate association between perceived usefulness of an institutional LMS and self-reported frequency of use (r = .42, 95% CI [.30, .52]). Its execution quality is genuinely above the genre median: a confidence interval rather than a bare p-value, an a priori sensitivity statement, a Spearman robustness check, a specific ethics subsection, no causal language anywhere, and a Limitations section that names the design constraints accurately.

The problem is not what the paper claims — it is what the paper does not deliver. Section 2 correctly identifies the interpretive frame its own contribution requires ("any single-site estimate is best read as one point in a distribution rather than as a fixed value," citing Song, 2018), and then never places its point in any distribution. The comparative claim "consistent with prior technology-acceptance research" appears in the Abstract, Section 5, and the Conclusion, and is nowhere substantiated by a single prior numeric estimate. Six references support a paper positioned inside the technology-acceptance tradition, none of them primary sources of that tradition and none meta-analytic.

My position on this manuscript's defining feature is explicit: correctly naming a limitation discloses it; it does not cure it. Honest self-description earns credit against research integrity, not against contribution.

### Strengths

1. **Reporting standards above genre median**: r reported with 95% CI, p, and n together (§4); an a priori sensitivity statement (">.80 power to detect r ≥ .19 at α = .05," §3.4); a Spearman robustness check (ρ = .40) run *because* the criterion is ordinal, not as decoration. Most submissions in this genre arrive with a bare coefficient and an asterisk.

2. **Causal discipline that is real, not cosmetic**: §5 states the reverse pathway ("more frequent use raises perceived usefulness") is "equally consistent with the data," and attributes it to Delgado (2020) rather than burying it. The Abstract, Discussion, and Conclusion are internally consistent on this — there is no front-matter over-promise followed by a hedged body. This is the error I most often have to correct, and it is absent here.

3. **Accurate self-positioning**: the paper calls itself "an incremental data point" (§2) and "a bounded, single-sample descriptive finding" (§6), and the title and abstract say "Self-Reported Use," not "Use." The claim scope matches the measure scope in the front matter.

4. **Ethics and instrument reporting present and specific**: named ethics-committee approval, voluntary participation, informed consent on the landing page (§3.3); the predictor scale is traced to a validated source with in-sample α = .88 (§3.2). Both are routinely missing at this tier.

### Weaknesses

1. **The contribution question is not answered — and the paper's own framework shows why**: Applying this journal's screening question — *if this paper did not exist, what would readers not know?* — the honest answer is: one unanchored point estimate from an unnamed platform at an undescribed institution. Not "nothing," but very close to it, because the paper declines the one move that would convert a data point into a contribution. §2 names the "one point in a distribution" logic; §5 and §7 then revert to standalone reporting. **Fix**: execute the comparison the paper promises — state what Song (2018), Ibarra and Poll (2021), and any pooled estimate actually report, and say where [.30, .52] sits relative to them. If the interval overlaps everything already published, say so; if it does not, that is a finding. Either outcome is worth more than the coefficient alone.

2. **An unsubstantiated comparative claim carried into the Abstract and Conclusion**: "consistent with prior technology-acceptance research" (Abstract; §5; §7 as "consistent with prior work") is a claim about the relationship between this estimate and a literature, and no evidence for it appears anywhere in the manuscript. It is not a hedge — it is an assertion, and it is the only sentence doing the work of situating the study. **Fix**: substantiate it numerically or delete it from all three locations. As written it cannot survive review.

3. **The reference base cannot bear the framing**: six references for a manuscript operating inside the technology-acceptance tradition, with perceived usefulness defined in §2 in essentially the tradition's original terms but attributed to two secondary sources (Costa & Wren, 2019; Delgado, 2020). No primary acceptance-model literature, no meta-analytic anchor. This is not a citation-formatting complaint: it is why weakness 2 is unfixable within the current reference set. **Fix**: add the tradition's primary sources and at least one synthesis, and use the synthesis as the benchmark. **Additionally, and separately — a reference-integrity flag I am obliged to raise as editor**: all six references carry sequential DOIs within a single prefix block (10.5555/2050001–2050006) despite naming six different journals and publishers. Legitimate references from six distinct publishers do not share a DOI prefix or run in sequence. I cannot verify these from my desk and I make no allegation; in live handling this manuscript would go to a reference-integrity check before any decision issued. If that check finds the sources do not resolve, the domain dimension converts from a warning to a blocking failure and the decision converts to rejection. Authors should pre-empt this by supplying resolvable DOIs.

4. **Reportability gaps that are editorial, not merely technical**: (a) the response denominator is never given — "All enrolled undergraduates were eligible" (§3.1) implies a population, so 233 responses implies a response rate, but the eligible N is absent and the rate is therefore unreportable and non-response bias unassessable; (b) r² is given as prose ("the proportion of variance shared by the two measures was accordingly modest," §4) rather than as the number (.18) the reader is owed; (c) §3.4 asserts scatterplot inspection and approximate symmetry, but the manuscript contains no figure, no table, and no distributional statistics for the outcome beyond a median category; (d) §3.1 reports removing 5 duplicate entries while §3.3 states that no identifying information was collected and responses "could not be linked back to individual students" — these two statements cannot both hold as written, since deduplication requires some persistent identifier. I read (d) as reporting imprecision rather than misconduct, but it touches both sample integrity and the accuracy of the anonymity representation shown to participants and to the ethics committee, and it must be corrected rather than left standing. **Fix**: state the eligible population and response rate, report r², add a descriptive table plus the scatterplot, and state the actual deduplication mechanism and reconcile it with the anonymity claim.

5. **The practitioner turn is not licensed by the design, and it switches constructs mid-sentence**: §5's suggestion that onboarding "which helps students see concrete usefulness … may be worth institutional attention" is hedged, but it is intervention-shaped advice derived from a cross-sectional correlation, and it silently moves from *perceived* use — which is what was measured, and what the title correctly says — to behaviour, which was not. The hedge covers the causal problem and misses the construct switch. **Fix**: either hold the boundary consistently (the study speaks to a perception–perception association and the implication should be stated in those terms), or drop the recommendation. An institutional decision-maker cannot act on it as written in any case: it names no target students, no timing, no intervention, and no cost.

### Detailed Comments

#### Journal Fit

Topically in scope. This journal publishes single-institution empirical studies of technology use in higher education, and our readership — practitioners and institutional researchers — accepts bounded descriptive contributions when design and reporting are transparent, which here they largely are. The fit problem is contribution level, not subject matter: as written, the paper offers our readers a coefficient they cannot benchmark, drawn from a platform that is never named and an institution characterised only as "mid-sized public." A reader at another institution has no basis for judging transfer. Fit becomes defensible if the authors execute the benchmarking comparison and characterise the platform and setting; it does not become defensible through further hedging. If the authors decline to add analytic or comparative depth, *Australasian Journal of Educational Technology* (which runs an explicit short-report track matching this manuscript's self-limiting framing) or *Research in Learning Technology* are the honest destinations, and I would say so in the decision letter rather than have them discover it after two more review cycles.

#### Originality

Low, and the authors say so. The association is long-established; the sample is not distinctive; the measure is adapted rather than improved; there is no moderator, no multivariate control, no behavioural criterion, no preregistration, and no theoretical extension. The stated contribution — "a single, transparently reported association … using a previously validated measure" (§2) — proposes transparency itself as the contribution. Transparency is a precondition for publication, not a contribution to knowledge. The one genuinely available originality route sits unused: the institution operates the LMS under study and therefore holds complete server-side access logs for every respondent; the paper cites the literature establishing that self-report diverges from those logs (Vasquez, 2020), concedes the point in §6, and proceeds with the proxy anyway. A limitation that could have been removed with data the institution already holds is a different class of limitation from one imposed by circumstance, and the manuscript's uniformly apologetic framing flattens that distinction.

#### Significance

Bounded and local as it stands. If every claim holds exactly as reported, the field's knowledge state is unchanged and no institutional decision changes. Significance is recoverable — not to Q1 level, but to a real contribution — by placing the estimate against published values, by naming and characterising the platform so the finding is comparable, and by stating what an institution should do differently. Timeliness is neutral: LMS engagement remains a live institutional concern, but nothing in the manuscript ties it to a current decision point.

#### Structural Coherence

Strong at the sentence and section level; broken at one specific joint. Title → Abstract → Introduction → Results → Conclusion are consistent, the research question in §1 is answered directly in §5 and §7, and there is no over-promise/under-deliver pattern of the usual kind. The break is the reverse: the paper *under*-delivers against a promise it makes to itself. §2 commits to situating the finding against prior work and identifies exactly how ("one point in a distribution"); §5 and §7 assert the conclusion of that comparison without performing it. That is not a tone problem — it is an argumentative gap in the manuscript's central positioning claim, and it is the single most concrete, most fixable defect in the submission.

#### Title & Abstract

The title is accurate and appropriately bounded — "Self-Reported Use" rather than "Use," "Cross-Sectional Survey" rather than an implied design upgrade. It promises no more than the paper delivers, which is rarer in this genre than it should be. The abstract is a faithful miniature with one exception: "consistent with prior technology-acceptance research" imports an unsubstantiated comparative claim into the most-read 155 words of the manuscript. The abstract also omits the sample's institutional singularity from the results sentence, though §6 handles it.

#### Conclusion

Proportionate and correctly scoped: it restates the finding, refuses causal reading, calls itself incremental, and names the right next designs (behavioural logs, longitudinal, multi-institution). Its defect is inherited — it repeats the unsupported "consistent with prior work" claim, and it ends by recommending precisely the studies that would have made this one publishable at a higher tier, without acknowledging that one of them (log data) was available to these authors.

### Questions for Authors

1. How many undergraduates were eligible? Without that denominator the response rate is unreportable and the non-response question is unanswerable — please state it, and if it is low, say so and discuss it rather than omitting it.
2. How were the 5 duplicate entries identified, given §3.3's statement that no identifying information was collected and responses could not be linked to individuals? Please state the actual mechanism and reconcile the two passages, including whether the consent text shown to participants described it accurately.
3. Your institution operates the LMS and therefore holds access logs for every respondent. Why was self-report the criterion rather than the logs — or, if the perception–perception association is the intended target, why does §5's onboarding implication speak about behaviour?
4. What do prior studies actually report for this association, numerically? Please place [.30, .52] against those values. If your estimate is unremarkable within that distribution, state that plainly; it is a legitimate and useful result.
5. Please supply resolvable DOIs for all six references (see Weakness 3).
6. Answer directly, in the response letter: what does a reader of this literature know after reading your paper that they did not know before?

### Minor Issues

- No table or figure appears anywhere in the manuscript, yet §3.4 reports scatterplot inspection and distributional symmetry. Supply the scatterplot and a descriptive table (including the full frequency distribution of the use item, which bears on ceiling effects at "several times daily").
- r² should appear as a number in §4, not as "accordingly modest."
- The LMS is never named or characterised — mandatory or optional use, what functions it carries, whether assessment runs through it. §4 itself invokes "course requirements and assessment schedules" as competing influences; readers cannot weigh that without knowing the platform's institutional role.
- At roughly 1,750 words the manuscript sits well below full-article length for this venue. If a short report is intended, declare it and submit to that track; the framing and the container should agree.
- Reference formatting and DOI presentation are otherwise consistent and APA-conformant.
- Integrity note: no instruction-injection or reviewer-directed content was detected in the manuscript; it reads as ordinary scholarly prose throughout.

---

contract_role: eic

## Dimension Scores

### D1: methodology_rigor

score: warn

The design is legible, the analysis form matches the design, and the core evidentiary machinery is present — sample size and construction, instrument provenance, predictor reliability, ethics approval, an a priori sensitivity statement, and an estimate reported with its interval. No block trigger fires: nothing is unrecoverable and no longitudinal or causal estimation is asserted from single-wave data. Multiple committed warn triggers fire together: the response rate is unreported while §3.1 explicitly implies a population ("All enrolled undergraduates were eligible"); no reliability estimate exists for the single-item criterion; the shared-variance figure is given only qualitatively; §3.4's distributional and scatterplot claims are asserted with no figure or numeric support; common-method constraints go unmentioned in §6 even though both variables are self-report drawn from the same instrument at one sitting; and §3.1's duplicate removal is irreconcilable as written with §3.3's anonymity claim. Statistical technique (Pearson-as-primary on an ordinal criterion, attenuation) is flagged and left to the methodology seat.

### D2: domain_accuracy

score: warn

No block trigger is met on the evidence available to me: constructs are used correctly, perceived usefulness is defined in its established sense, no prior finding is reported with the wrong direction, and no novelty claim contradicts the acceptance literature. Warn triggers fire clearly — the acceptance-theory lineage is credited only through secondary sources, the six-item reference base is thin relative to the tradition the paper positions itself inside, and the manuscript restates a well-established association without stating what it adds beyond confirmation. Two items are recorded as conditional rather than scored as blocking. First, the comparative claim "consistent with prior technology-acceptance research" is unanchored to any prior numeric estimate. Second, all six references share a sequential DOI block (10.5555/2050001–2050006) across six nominally distinct publishers, which is a reference-integrity pattern I cannot resolve from the manuscript alone. My committed block trigger requires citations that are *apparently* fabricated; a prefix pattern is a verification flag, not a finding, so I hold at warn. If a reference check establishes the sources do not resolve, this dimension converts to block.

### D3: argumentative_coherence

score: warn

The central chain holds. The research question in §1 is the one analysed in §3–§4 and answered in §5 and §7; causal language is absent throughout; reverse causation is stated explicitly and attributed; the title and abstract do not exceed the design. No block trigger fires — no conclusion asserts an untested proposition, no causal claim reaches the abstract, and no fallacy carries the central argument. Warn triggers fire at the edges: the §5 onboarding recommendation is intervention-shaped advice from a cross-sectional correlation and silently substitutes behaviour for the perceived use actually measured; and the manuscript makes a positioning promise in §2 (situate the estimate as "one point in a distribution") that §5 and §7 assert the conclusion of without performing, so a load-bearing comparative claim appears in the Abstract, Discussion, and Conclusion with no supporting evidence anywhere in the paper.

### D4: cross_disciplinary_relevance

score: warn

An adjacent-field reader can determine what was studied and roughly why, so the block threshold is not met. But reach is narrow in the specific ways my warn triggers name. The platform under study is never identified or characterised and the institution is described only as "one mid-sized public university," so no reader at another institution can judge transfer or comparability. The acceptance-theory background an adjacent reader needs is available only through two secondary citations. The "so what" reduces to a single hedged sentence about onboarding that names no target population, timing, intervention, or cost, and therefore supports no institutional decision. The one genuinely cross-disciplinary thread the paper opens — Vasquez (2020) on self-report versus behavioural logs — is raised in §2, conceded in §6, and never carried into the design or the discussion, despite the log data sitting in the authors' own institution.

### D5: writing_and_structure

score: warn

This is the lowest-stakes and most repairable of my warnings, and the prose deserves credit: the manuscript is complete in structure (IMRaD plus separate Limitations and Conclusion), clearly written, internally consistent between abstract and body, and formatted to a consistent citation standard. The warn triggers that fire are the under-development ones. The manuscript contains no table and no figure at all, while §3.4 reports scatterplot inspection and distributional properties that no reader can check and §4 gives the outcome only as a median category with no dispersion or distribution. Results and Discussion are two paragraphs each, thin relative to the load they carry. At roughly 1,750 words the submission sits well below full-article norms for this venue while describing itself as "incremental" without adopting or declaring a short-report format.

## Failure Condition Checks

### F1

fired: false

Predicate: any mandatory dimension scores block. My mandatory dimensions are D1 warn, D2 warn, D3 warn. No block. (Recorded contingency: a failed reference-integrity check on the DOI pattern would convert D2 to block and fire this condition.)

### F2

fired: true

Predicate: two or more mandatory dimensions score warn or worse. Three do — D1, D2, and D3 all score warn.

### F3

fired: false

Predicate: any high-priority dimension scores block. The single high-priority dimension, D4, scores warn.

### F0

fired: false

Predicate: every mandatory dimension scores pass. None do.

## Review Body

From the editor's chair this manuscript presents an unusual problem, and it is worth naming precisely because the ordinary review reflex will get it wrong. Nearly every heuristic an experienced editor uses to screen this genre is a test for over-claiming, and this paper passes all of them. It refuses causal language, states the reverse pathway explicitly, reports an interval rather than a bare coefficient, runs a robustness check appropriate to its measure, declares its power assumption in advance, names its ethics approval, and describes itself as incremental and design-bounded. A panel that pattern-matches on over-claiming will return a favourable review of a manuscript that is not yet publishable, and will do the authors no service.

My position on that axis is explicit, and I would state it in the decision letter: correctly describing a limitation discloses it, it does not cure it. Disclosure earns credit against research integrity — and this paper earns that credit genuinely — but integrity credit does not transfer to the contribution ledger. The screening question this journal applies to every submission in this genre is *what does this change?*, and the answer here is currently close to nothing, not because the study was executed badly but because the one move that would convert a coefficient into a contribution is promised and then not made. Section 2 states, correctly and citing Song (2018), that any single-site estimate is best read as one point in a distribution. Sections 5 and 7 then report the point and assert — three times, including in the abstract — that it is consistent with prior research, without naming a single prior value. The comparison the paper identifies as necessary is the comparison the paper never performs. That is not a stylistic complaint; it is a gap in the manuscript's only positioning claim, and with six references and no synthesis in the reference list, the authors currently lack the material to close it.

The hedging also turns out to be asymmetric in a way that matters more than its thoroughness. It is exhaustive where the field expects scrutiny — causality — and silent where scrutiny is equally warranted. There is no caveat on the criterion measure at all: a single unvalidated ordinal item with no reliability estimate is correlated with a validated six-item scale, and the manuscript does not mention it. The response rate is not merely unreported but unreportable, because §3.1 implies a population and never sizes it. The shared-variance figure is delivered as an adjective. And §3.1 and §3.3 make claims about deduplication and anonymity that cannot both be literally true; I read that as reporting imprecision rather than misconduct and would say so plainly to the authors, but it must be corrected, since it bears simultaneously on sample integrity and on the accuracy of the anonymity representation made to participants and to the ethics committee. Each of these defects exists in the manuscript's data and methods regardless of how the manuscript describes itself, which is the test I hold my own review to.

One further item belongs on the editorial record rather than the reviewers'. All six references carry sequential DOIs within a single prefix block while naming six different journals and publishers. I make no allegation and cannot resolve it from the desk; live handling of this submission would route it to a reference-integrity check before any decision issued, and I have scored the domain dimension at warn rather than block on that basis. Authors should treat question 5 as the fastest route to closing it.

What holds this at major revision rather than rejection is that the defects sort cleanly into curable and non-curable, and most of them are curable. The reporting gaps — denominator, r², descriptive table, scatterplot, deduplication mechanism — are straightforwardly fixable within the existing data. The benchmarking gap is fixable with a literature pass and is, in my judgement, the revision that would most change my assessment. The single-item criterion is only partially fixable after the fact. The contribution deficit is not fixable by revision alone: it requires either the institution's own log data as a criterion, or a moderator or multivariate layer, or an explicit repositioning as a short report with a correspondingly bounded claim in a venue that runs that track. The authors should be told that fork clearly rather than discovering it across two more review cycles. The execution quality here is real, and the decision letter should say so — this verdict turns on contribution and reporting completeness, not on competence.

## Editorial Decision

Two or more mandatory dimensions scored warn (D1, D2, D3), firing F2 at severity 70. F1 and F3 did not fire; F0 is not satisfied. F2 is the highest-severity fired condition, and its action governs.

editorial_decision=major_revision

---

## SEAT — Peer Reviewer 1 (Methodology)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** As Peer Reviewer 1, this is my primary dimension: whether the study's design, sampling, measurement, analysis, and reporting are strong enough that the paper's claims survive methodological scrutiny at this field's peer-review bar. For a cross-sectional survey in educational technology, that bar means a stated and appropriate design, a defensible sampling frame with reported response/completion rates, validated or at minimum psychometrically documented measures for both perceived usefulness and self-reported use, analyses matched to the data type with assumptions checked, effect sizes and interval estimates alongside p-values, and enough procedural detail that an independent researcher could re-run the study. It also includes the reproducibility affordances the field increasingly expects — instrument availability, data/code availability statements, and evidence of ethics review. Self-report on both sides of the association raises common-method variance as a design-level (not merely discussion-level) threat, and a single-timepoint design constrains what can be inferred at all.

**D2 — domain_accuracy (mandatory).** Reviewer 2 owns literature completeness and domain-claim correctness; my engagement with this dimension is confined to the methodological interface. That means whether constructs are operationalized consistently with how the LMS-adoption/TAM-adjacent literature defines them, whether instruments borrowed from prior work are used at their documented level of measurement and scoring, and whether reported statistics are internally consistent (degrees of freedom, sample sizes, subgroup totals, percentages summing correctly). I will not score the breadth of citation coverage; I will score whether the methodological apparatus misrepresents what it claims to measure or reports numbers that cannot be true simultaneously.

**D3 — argumentative_coherence (mandatory).** From a methodology standpoint this is the inference chain: whether the conclusions the paper draws are the conclusions its design can license. The dominant risk in a cross-sectional perceived-usefulness/use study is the slide from association to causal or directional language, and the reverse-causation problem specifically (use may drive perceived usefulness rather than the converse). Also in scope: whether stated research questions, hypotheses, analyses, and conclusions form a single consistent chain rather than drifting between sections; whether limitations acknowledged in one section are contradicted by claim strength in the abstract or conclusion; and whether any of the classic fallacies on my checklist (ecological, survivorship, confirmation-driven selective presentation, over-inference from non-significant results) undermine the central argument.

**D4 — cross_disciplinary_relevance (high).** Reviewer 3 owns interdisciplinary framing; my methodological share is whether the paper's procedural and analytic reporting is transparent enough for an adjacent-field reader — an instructional designer, an institutional researcher, a learning-analytics reader — to judge the evidence for themselves and to assess transportability to their own setting. Concretely: is the sampling context described well enough (institution type, course context, LMS platform, timeframe) that a reader outside this exact subfield can gauge whether the finding travels, and are generalization claims scoped to the sampled population rather than asserted for undergraduates broadly?

**D5 — writing_and_structure (normal).** My scope here is the methodological reporting surface, not prose style: whether the Method section is organized so that design, participants, measures, procedure, and analysis are locatable and complete; whether tables and figures report the statistics needed to verify claims (Ns, SDs, test statistics, df, exact p, effect sizes, CIs) with accurate captions and no mismatch against the text; and whether reporting follows the venue's/APA 7.0 conventions closely enough that a reader can reconstruct what was done. At a 1,597-word manuscript length I will treat brevity itself as neutral and judge only whether the compression has removed information a methods reader requires.

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for` — An explicitly named design and stated timeframe; sampling frame, recruitment channel, sampling method (random / stratified / convenience), invitation and completion counts, response rate, and any eligibility criteria; final N with a stated justification (a priori power analysis or an argued adequacy rationale); the measurement instruments for perceived usefulness and self-reported use, including item counts, response scale and anchors, provenance (adapted from a named prior instrument vs. author-generated), and reliability evidence (α or ω, ideally with CIs) plus any validity evidence (factor structure, CFA fit); how "use" is operationalized (frequency, duration, self-rated intensity) and whether any objective LMS log data is available or substituted; the analysis plan matched to the data type, with assumption checks (normality, linearity, homoscedasticity, independence, multicollinearity/VIF where regression is used) and the treatment of ordinal Likert data; effect sizes with magnitude interpretation and 95% CIs for all key estimates; missing-data quantity and handling; whether multiple comparisons are corrected; common-method-variance acknowledgement and any procedural or statistical remedy; ethics/IRB approval and consent; data, code, and full-instrument availability.
- `what_triggers_block` — Any one of: (a) the core association is reported with no way to evaluate it — no N, or no test statistic/effect estimate, only a bare significance claim; (b) the measurement of one or both central constructs is undocumented to the point of being unevaluable (no items, no scale, no provenance, and no reliability figure), so the reader cannot know what was measured; (c) the sampling procedure is entirely absent — no recruitment description and no participant characteristics — leaving the sample unidentifiable; (d) a statistical procedure demonstrably inappropriate for the data as described, applied to the paper's headline result (e.g., a test whose stated assumptions the paper's own description violates, with no acknowledgement or alternative); (e) internal numerical contradiction in the primary analysis (reported N, df, or subgroup totals mutually incompatible) that invalidates the headline estimate; (f) a red-flag pattern of undisclosed multiple testing where a large set of tests is run and only significant ones are reported as the finding.
- `what_triggers_warn` — Any of: convenience sampling used without a stated limitation; response rate not reported or clearly low without non-response discussion; N reported but with no power/adequacy justification; reliability reported for only one construct, or reported without item-level detail; instrument adapted from prior work without stating what was changed or revalidated; assumption checks not reported for an analysis that requires them; effect sizes or 95% CIs missing for key estimates while p-values are given; missing data unmentioned; common-method variance from all-self-report measurement unacknowledged; ethics approval or consent not stated; no data/code/instrument availability statement; APA 7.0 statistical-reporting deviations (missing df, "p = .000", non-italicized symbols, incorrect leading zeros) that impede verification without destroying it.

### D2: domain_accuracy
- `what_to_look_for` — Whether "perceived usefulness" is operationalized consistently with its established definition in the adoption literature rather than silently redefined; whether "self-reported use" is defined precisely enough to be distinguished from intention-to-use or from objective usage; consistency between the construct names used in hypotheses, the items described, and the variables named in results; correct use of statistical terminology (correlation vs. prediction vs. explained variance; significance vs. magnitude; reliability vs. validity); internal arithmetic consistency across text, tables, and abstract (percentages, subgroup Ns summing to total N, means within scale range, correlations within [-1, 1], R² consistent with reported coefficients); correct labelling of the design (a single-timepoint survey not described as longitudinal, quasi-experimental, or predictive-in-the-temporal-sense).
- `what_triggers_block` — Any of: (a) a central construct is measured by items that plainly measure a different construct than the one named and claimed (e.g., items capturing satisfaction or intention while the paper reports them as usefulness or as actual use), making the paper's headline claim a claim about something it did not measure; (b) a reported statistic is impossible or mutually contradictory in a way that touches the main result (a correlation outside its bounds, a mean outside the scale range, R² inconsistent with the reported model, or an N in the abstract that contradicts the N in the analysis); (c) the design is misnamed in a way that misrepresents the evidence to readers (a cross-sectional survey presented as longitudinal, experimental, or causal-design).
- `what_triggers_warn` — Any of: construct definitions stated loosely or drifting between sections without contradiction; "usage" and "intention to use" used interchangeably in prose while measured as one thing; statistical terminology used imprecisely (calling an association "impact" or "effect" in results narration); minor numerical inconsistencies in secondary tables or rounding that do not touch the headline estimate; instrument attributed to prior work without a citation locating the specific version used; scale-level assumptions (treating ordinal items as interval) applied without comment.

### D3: argumentative_coherence
- `what_traits` is not applicable; the required lines follow.
- `what_to_look_for` — Whether the stated research question, the hypotheses (if any), the analyses actually run, and the conclusions form one unbroken chain; the verb choices in abstract, results, and conclusion (associated/related vs. leads to/increases/drives/improves); whether directionality between perceived usefulness and use is asserted, and if so on what basis; whether reverse causation and third-variable confounding are named and handled; whether the limitations section's admissions are consistent with the strength of claims elsewhere, especially in the abstract and any practice/policy recommendations; whether non-significant or unsupportive results are reported alongside supportive ones; whether recommendations to institutions are scaled to the strength of the evidence; whether the sample supports the population the conclusion speaks about.
- `what_triggers_block` — Any of: (a) a causal claim about the central relationship (perceived usefulness causes / increases / drives use, or the reverse) presented as a finding of this study, given a single-timepoint correlational design and no causal-identification strategy — this is the reverse-causation fallacy from my checklist and it invalidates the paper's headline inference; (b) conclusions or practice/policy recommendations that require evidence the study did not collect (e.g., intervention efficacy claims from a survey); (c) internal contradiction where the conclusion asserts what the results section reports as unsupported or non-significant; (d) evidence of selective presentation such that the argument is built only on supporting results while stated analyses go unreported.
- `what_triggers_warn` — Any of: causal-adjacent verbs used loosely in discussion while the formal claim stays correlational; directionality implied by framing or model ordering without explicit causal assertion; reverse causation not discussed as a limitation; confounders unaddressed; generalization to "undergraduates" broadly when a single institution or a single course population was sampled; limitations section present but perfunctory relative to the design's actual constraints; conclusion firmer in the abstract than the results section warrants; practice recommendations stated without hedging proportionate to the evidence.

### D4: cross_disciplinary_relevance
- `what_to_look_for` — Whether the study context is described concretely enough for an adjacent-field reader to judge transportability: institution type and size, national/regional and language context, LMS platform and version, whether use was mandatory or optional in the sampled courses, disciplinary composition and year level of respondents, and the data-collection window (including any relationship to term structure or to remote-teaching conditions); whether construct and instrument definitions are stated rather than assumed as insider shorthand; whether the methods are described in terms an institutional-research or instructional-design reader could follow without reconstructing the adoption-model literature; whether the scope of the population to which findings are said to apply is stated explicitly.
- `what_triggers_block` — Any of: (a) the study setting is so underspecified that transportability cannot be assessed at all — no institution/context description, no platform, no timeframe, no participant characteristics — so an outside reader cannot tell what population or system the result pertains to; (b) implications are asserted for populations, platforms, or sectors materially different from the one sampled, with no bridging argument at all (findings from one undergraduate cohort presented as applying to higher education generally or to other education sectors as an established result).
- `what_triggers_warn` — Any of: partial context reporting (platform named but mandatory/optional status unstated, or timeframe omitted); field-specific jargon or model shorthand used without definition where an adjacent-field reader would stall; the target population for generalization left implicit; implications for practice written for one audience only, with transferability caveats absent; no statement of what would need to hold for the finding to travel to another institution or platform.

### D5: writing_and_structure
- `what_to_look_for` — Presence and locatability of the standard method subsections (design, participants, measures, procedure, analysis) or their functional equivalent within the manuscript's length; whether each is complete enough to reconstruct the study; tables/figures that report Ns, Ms, SDs, test statistics with df, exact p-values, effect sizes, and CIs, with captions that stand alone and match the text exactly; consistency of numbers between abstract, results text, and tables; APA 7.0 conventions for statistical notation (italics, decimals, leading zeros, p-value format); whether the abstract's method sentence accurately describes design, sample, and measures; whether the 1,597-word length has been achieved by trimming redundancy (acceptable) or by deleting method detail a replicator needs (not acceptable).
- `what_triggers_block` — Any of: (a) no identifiable methods reporting at all — the reader cannot locate who was sampled, what was administered, or what was computed anywhere in the manuscript; (b) tables/figures that contradict the results text on the primary estimate, or a primary result presented only in a figure with no numeric values reported anywhere, so the headline claim cannot be verified from the document; (c) the abstract materially misdescribes the method (wrong design, wrong N, wrong measures) relative to the body.
- `what_triggers_warn` — Any of: method content present but scattered across sections rather than organized, so reconstruction requires effort; a table missing SDs, df, effect sizes, or CIs; captions that do not stand alone or that use variable labels not defined in the text; minor numeric mismatches between abstract and body that do not change the conclusion; APA 7.0 statistical-notation deviations; overloaded or unreadable table layout; results narrated in prose with no supporting table where the density of statistics warrants one; the compression to ~1,600 words having dropped a described-but-unreported analysis.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Methodology Review Report (Peer Reviewer 1)

### Reviewer Identity

Quantitative methodologist in educational measurement, specializing in survey psychometrics and the statistical treatment of ordinal and single-item measures; teaches a doctoral seminar on correlation-versus-agreement and reliability attenuation, publishes on measurement error in self-report educational data, and serves regularly as a statistical reviewer for education journals.

### Overall Recommendation

Major Revision

### Confidence Score

4

### Summary Assessment

The inferential discipline in this manuscript is genuinely above field norm: the design is named, the estimate carries a CI and an n, a rank-based robustness check is reported, sensitivity to effect size is stated, ethics review is documented, and causal language is refused consistently from abstract to conclusion. I verified the two checkable computations and both are correct — the Fisher-*z* interval for *r* = .42 at *n* = 214 is [.30, .52] as reported, and detectability of *r* ≥ .19 at 80% power, α = .05 two-tailed is right for this *n*. That execution quality is real and should be credited.

The problem is that the paper's caution is concentrated entirely on the causal axis, where the design is already well understood, and is absent on the measurement axis, where the binding constraint on this study actually sits. The criterion is a single ordinal item with no reliability estimate, no reported distribution, and no intermediate anchor labels; the primary coefficient is the interval-assuming one, which the paper's own §3.2 measurement declaration argues against; and the shared-variance figure the Results paragraph describes in words is never printed. None of this is invalidating — the Spearman concordance (ρ = .40) shows the coefficient choice is empirically inconsequential here — but the paper cannot presently be replicated at the instrument level, and its central estimate is very likely attenuated by an amount the manuscript never estimates or acknowledges. The defects are fixable within this design; several are fixable from data the authors already hold.

### Strengths (5 items)

1. **Estimate reported to modern standards, and correctly**: §4 gives point estimate, 95% CI, exact-form *p*, and *n* together (`r = .42, 95% CI [.30, .52], p < .001, n = 214`). I recomputed the interval by Fisher transformation and it reproduces to the reported two decimals. This is more than most submissions in this genre provide.

2. **Sensitivity to effect size stated and arithmetically sound**: §3.4's claim of >.80 power to detect *r* ≥ .19 at α = .05 two-tailed is correct at *n* = 214. Stating detectable magnitude rather than reporting a post hoc observed-power figure is the right choice.

3. **Measurement level of the criterion is explicitly named**: §3.2 states "We treat this as an ordinal indicator," and §3.4 acts on that by adding a Spearman check. The paper does not silently launder an ordinal item into an interval one — a common and usually undisclosed move.

4. **Reverse causation named and correctly located**: §5 treats the reverse pathway as "equally consistent with the data" rather than burying it in a limitations list. On my fallacies checklist, the reverse-causation entry — the dominant risk in this design — does not fire.

5. **Ethics reporting is specific**: §3.3 names committee review, voluntariness, absence of incentive, and consent placement. Most manuscripts at this length compress this to a single unverifiable sentence.

### Weaknesses (5 items)

1. **The criterion has no reliability estimate, and the resulting attenuation is neither estimated nor acknowledged.** α = .88 is reported for the six-item predictor; nothing is reported for the single-item outcome, and single-item frequency measures typically carry substantially lower reliability. *Why it matters*: attenuation from criterion unreliability biases *r* downward, so *r* = .42 is a floor, not an estimate — the paper's repeated characterization of the association as "moderate" may itself be an artifact of measurement error. As illustration only, at plausible criterion reliabilities of .70 and .60 the disattenuated coefficient would be roughly .54 and .58 respectively (using the reported α = .88 for the predictor), which crosses into a different verbal magnitude band. The paper's hedging works in the wrong direction here. *Fix*: add a test-retest or alternate-form reliability estimate for the use item if any subsample allows it; failing that, report a disattenuation sensitivity range across a stated span of assumed *r*<sub>yy</sub> and state explicitly that the reported coefficient is attenuated by an unknown amount. Also revise §3.4's sensitivity statement, which assumes error-free measurement and therefore overstates the study's sensitivity to *true* associations.

2. **The primary/robustness designation is inverted relative to the paper's own measurement declaration.** §3.2 declares the outcome ordinal; §4 reports a median for it (an ordinal-appropriate statistic); §3.4 nonetheless designates Pearson — which requires interval spacing — as the primary estimate and relegates Spearman to a footnote-grade check. *Why it matters*: this is an internal inconsistency in measurement-level reasoning, not merely a stylistic preference, and the five verbal categories ("rarely or never" through "several times daily") plainly do not have equal spacing in frequency terms. *Fix*: promote Spearman's ρ to the primary estimate with its own CI and *p*, and retain Pearson as the supplementary coefficient. Because ρ = .40 and *r* = .42 differ by .02, this costs the paper nothing substantively and removes the inconsistency entirely. Note also that the robustness claim as written — "the association did not depend on the parametric assumption" — is overstated: agreement of two point estimates does not establish that the *inference* is assumption-free, since the reported CI and *p* are both Fisher-*z*-based and no interval or *p* is given for ρ.

3. **The outcome variable's distribution is never reported, and the instrument is not reconstructable.** Only a median category is given — no frequencies, no dispersion, no floor/ceiling assessment on a five-point item where a ceiling is entirely plausible, and no labels for scale points 2–4 (only the two endpoints are stated). *Why it matters*: two distinct failures follow. Analytically, a reader cannot assess whether category clumping is truncating the correlation, which bears directly on Weakness 1. Procedurally, a replicator cannot administer this item, because three of its five anchors are unknown. §3.4's assertions of approximate symmetry and clean scatterplot behavior are likewise unevidenced — no figure, no skewness or kurtosis values, and "approximately symmetric" is not a verifiable description of a five-category variable summarized by a median alone. *Fix*: report the full frequency distribution for the use item, print all five anchor labels verbatim, reproduce the six perceived-usefulness items in an appendix, and either include the scatterplot or replace the inspection claim with reported distributional statistics.

4. **Response rate is unreportable as written, and nonresponse bias is therefore unassessable even in principle.** §3.1 states that all enrolled undergraduates were eligible and that 233 responses arrived, but never gives the size of that eligible frame. *Why it matters*: at a mid-sized university the implied rate is likely very low, and the reader cannot tell whether it is 2% or 20%. Compounding this, the only participant characteristic reported is that the sample "spanned all four year levels" — no counts, no disciplinary composition, no other demographics — so the standard cheap check (comparing the respondent year-level distribution against published institutional enrollment figures) is impossible. Separately, §3.1's recruitment channel is the institution's course-announcement channel, which at most institutions sits inside or immediately adjacent to the platform under study; if so, invitation exposure is conditioned on the outcome variable, which is a selection-on-the-dependent-variable problem affecting the estimate itself, not only its generalizability. §6 currently frames this as external validity alone ("students who engage more with institutional channels may be overrepresented"). The net directional effect is genuinely uncertain — range truncation attenuates, while a homogeneous high-engagement stratum can distort in either direction — and the honest statement is that the bias magnitude is unknown. *Fix*: report the eligible-population denominator and the response rate; report year-level counts and benchmark them against institutional figures; state where the announcement channel is hosted relative to the LMS and, if it is inside the LMS, move this from §6's generalizability list into a stated threat to the estimate.

5. **The exclusion rule cannot be reconciled with the anonymity claim, leaving sample integrity unverifiable.** §3.1 reports removal of 5 duplicate entries; §3.3 states that no identifying information was collected and that responses could not be linked back to individual students. Deduplication requires some persistent identifier — IP, session token, cookie, SSO handle, device fingerprint — and each of these is identifying or quasi-identifying. *Why it matters*: this is almost certainly reporting imprecision rather than misconduct, and I would state that plainly to the authors. But methodologically the consequence is real in either direction: if the identifiers existed, §3.3's characterization of the data is inaccurate; if they did not, the 5 exclusions were made on some undisclosed basis, and the analyzed *N* rests on a rule the reader cannot evaluate. *Fix*: state the exact deduplication mechanism, the criterion applied, and when the identifier was discarded, and align §3.3's anonymity language with what was actually held. This finding also carries an ethics-representation reading that belongs to the panel's practice-and-ethics seat; I flag the overlap for the synthesizer so it is consolidated into a single item rather than counted twice.

### Detailed Comments

#### Research Questions & Hypotheses

The question in §1 is single, narrow, and answerable by the design chosen ("is perceived usefulness of the LMS associated with self-reported frequency of use?"). No hypotheses are stated, which is appropriate for an explicitly descriptive-correlational study, and the analysis run matches the question asked. The chain from §1 through §3.4 to §4 is unbroken. My one reservation is at the abstract's closing sentence, addressed below.

#### Research Design

The design is named ("cross-sectional survey study," §3.1), is appropriate to the stated question, and is described consistently throughout — nowhere is it presented as longitudinal, experimental, or predictive in a temporal sense. The internal/external validity trade-off is acknowledged rather than argued, which is acceptable at this scope. A within-design improvement the authors should be asked to consider is whether any temporal separation between the two measures was possible; administering both constructs in a single instrument at a single sitting leaves shared-method variance operating on the association, and the manuscript never raises this. Note that this is a distinct issue from the self-report-versus-log divergence discussed in §6: divergence concerns the validity of the criterion, whereas common-method variance concerns inflation of the association between the two measures. The paper addresses the former and is silent on the latter.

#### Sampling Strategy

Eligibility, channel, and window are stated; the denominator, response rate, and participant characteristics are not (Weakness 4). The three-week window has no calendar position — no term stage, no year — so a reader cannot judge whether collection coincided with an assessment peak, which would move both variables simultaneously. §3.4's sensitivity statement substitutes appropriately for a design-stage power analysis given that the frame was a census attempt, though it should be labeled as a sensitivity analysis conditional on the achieved *n* rather than phrased in a way that reads as design-stage power.

#### Data Collection

The predictor is well handled: six items, five-point Likert with both anchors given, provenance named, in-sample α = .88 reported. Two gaps remain. First, "adapted from Costa and Wren (2019)" never states what was adapted; if items were reworded for this LMS context, the adaptation is undocumented and the borrowed validation does not automatically transfer. Second, α is internal consistency, not validity — no factor structure is examined, so the six items' unidimensionality in this sample is assumed rather than shown. The criterion's documentation problems are covered in Weakness 3. Missing data is reported only as the 14 pre-analysis exclusions; item-level missingness among the retained 214 is not mentioned, and no handling method is stated.

#### Analysis Methods

The analysis matches the question. Assumption checking is asserted but not evidenced (§3.4), and the assertions concern properties that cannot be confirmed from what is printed. "Analyses were conducted at a conventional significance threshold" should name α explicitly, as §3.4 does elsewhere. The Pearson-as-primary decision is the substantive analytic issue (Weakness 2). One further point on the composite: averaging six five-point Likert items into a mean treats them as interval, which is standard practice and which I would not normally flag — but the paper is explicitly careful about measurement level for the criterion and silent about it for the predictor, and that asymmetry is worth a sentence.

#### Results Presentation

Both computed coefficients are reported; nothing appears selectively withheld, and only two tests are run, so no multiplicity concern arises. The reporting is otherwise incomplete in three specific ways. Degrees of freedom are absent — APA form would give *r*(212) = .42 — and *df* is the only independent confirmation that the analytic *N* equals the reported *N*. The outcome's descriptives are limited to a median category. And "the proportion of variance shared by the two measures was accordingly modest" is *r*² = .18 written in words; the value is substantive, uncontroversial, and one character to print. The manuscript contains no tables and no figures at all, including the scatterplot §3.4 says was inspected.

#### Reproducibility

Currently low, for reasons that are all cheap to fix. Neither instrument is reproduced in full (six predictor items absent; three of five criterion anchors absent), so the study cannot be re-administered as described. There is no data availability statement, no analysis-code statement, and no indication of the software used. Ethics review is documented, which is the one reproducibility affordance the paper does supply. Given that both instruments are short and the dataset is two variables wide, an appendix plus a deposited data file would move this dimension substantially at negligible cost.

#### Methodological Fallacies Detected

- **Reverse causation** — checked and **not fired**. §5 states the reverse pathway explicitly and treats it as equally consistent with the data.
- **Confirmation bias / selective reporting** — **not fired**. Both coefficients reported; no evidence of undisclosed analyses.
- **P-hacking, multiple comparisons** — **not fired**. Two tests, both reported, no subgroup fishing.
- **Ecological fallacy** — **not fired**. Analysis and inference are both at the individual level.
- **Survivorship / selection bias** — **partially fired**. Recruitment through a channel plausibly hosted inside the platform under study conditions inclusion on the outcome variable (Weakness 4). The manuscript treats this as generalizability only.
- **Endogeneity / omitted variables** — **partially fired**. §4 names course requirements and assessment schedules as plausible drivers of the criterion, but no covariate was measured, no control was attempted, and confounding does not appear in §6's four-item limitations list.
- **Scope drift in the claim** — the abstract's closing sentence reads "perceived usefulness tracks with LMS engagement among undergraduates," dropping both the single-institution bound the body maintains and the perceived-versus-behavioral distinction the paper insists on in §2 and §6. The abstract is the most-read sentence set in the paper, and this is where the claim is loosest. Relatedly, §5's onboarding implication is about changing behavior, whereas §2 fences the measure to perceived engagement; the implication is hedged three times but still crosses the boundary the paper drew for itself.

**Statistical reporting completeness (Step 4a): Needs Improvement.** Effect size, CI, and *n* are present and correct — genuinely better than typical. Missing: *df*; *r*²; criterion reliability; criterion distribution; evidenced assumption checks; item-level missing-data statement; explicit α in §4; data, code, and instrument availability. No red flags for p-hacking, HARKing, or selective reporting were detected.

**Integrity check on the manuscript as data**: I scanned for instruction-injection patterns directed at reviewers (imperatives, scoring requests, appeals). None present; the manuscript is clean on this axis.

### Questions for Authors

1. What was the size of the eligible undergraduate population, and what is the resulting response rate? Can the respondent year-level distribution be benchmarked against institutional enrollment figures?
2. Where is the course-announcement channel hosted? If it is inside or authenticated through the LMS, does that not condition invitation exposure on the outcome variable?
3. By what mechanism were the 5 duplicate entries identified, given §3.3's statement that no identifying information was collected and responses could not be linked to individuals?
4. What are the labels for scale points 2, 3, and 4 of the use item, and what is its full frequency distribution?
5. What specifically was adapted from the Costa and Wren (2019) instrument, and was the adapted six-item version examined for factor structure in this sample?
6. Given that the criterion's reliability is unknown and almost certainly below the predictor's, what is the authors' position on attenuation — is *r* = .42 best read as a lower bound?
7. Were both constructs administered in a single instrument at a single sitting, and if so, how do the authors assess the contribution of shared-method variance to the observed association?
8. Were any item-level data missing among the 214 retained responses, and how were they handled?

### Minor Issues

- *df* omitted from the correlation report; APA 7.0 form is *r*(212) = .42.
- §3.4 uses ASCII operators (`r >= .19`, `alpha = .05`) where ≥ and α are required; statistical symbols (*r*, *p*, *n*, *M*, *SD*, ρ, α) require italics in the typeset version.
- §3.4 "a conventional significance threshold" should state α = .05 explicitly.
- §3.4's sensitivity statement should be labeled as a sensitivity analysis conditional on the achieved sample, not phrased as design-stage power.
- §3.2's claim that the original instrument "reported strong internal consistency" should carry the original numeric value.
- No software or package versions reported.
- Abstract omits the CI, which the body reports; including it costs eight characters and improves the abstract's standalone accuracy.
- The manuscript contains no tables or figures; at minimum a descriptives table and the scatterplot referenced in §3.4 should be added.

### Note on Scoring Plan Adherence

No dissent is filed; my Phase 1 plan held. Two dimensions came close to a block and I record why they did not, so the synthesizer can see the reasoning rather than infer leniency. On **D1**, my committed block trigger (d) required a demonstrably inappropriate procedure applied to the headline result "with no acknowledgement or alternative" — the manuscript names the ordinality and supplies Spearman, and the two coefficients agree to .02, so the escape clause is satisfied and the objection is a reporting-hierarchy defect, not an invalidating one. My trigger (b) required the criterion to be undocumented on all four counts (items, scale, provenance, reliability); it fails only on reliability and provenance, so it is under-documented rather than unevaluable. On **D4**, my block trigger (a) was conjunctive across institution description, platform, timeframe, and participant characteristics; the manuscript supplies partial information on three of the four, so the trigger does not fire despite the reporting being thin. I have not escalated either post hoc.

---

contract_role: methodology

## Dimension Scores

### D1: methodology_rigor
score: warn

Warn triggers fired: reliability reported for only one construct; instrument adapted without stating what was changed or revalidated; assumption checks asserted without supporting evidence for an analysis that requires them; response rate not reported (denominator absent) with no substantive nonresponse analysis; missing data addressed only at the exclusion stage; common-method variance from single-sitting all-self-report measurement unacknowledged; no data, code, or full-instrument availability statement; APA statistical-reporting deviations (*df* omitted, ASCII operators) that impede verification without destroying it. No block trigger fired — the headline estimate is fully reportable and arithmetically verified (CI and sensitivity figures both reproduce), the sampling procedure is described, and the contested Pearson-primary choice carries both an acknowledgement and a reported alternative.

### D2: domain_accuracy
score: warn

Warn triggers fired: statistical terminology used imprecisely — "the association did not depend on the parametric assumption" overstates what concordance of two point estimates licenses, since all reported inference remains Fisher-*z*-based and no interval or *p* is given for ρ; the sensitivity computation is phrased as design-stage power; the six-item composite treats averaged ordinal Likert responses as interval without comment while the manuscript explicitly reasons about measurement level for the criterion; the adapted instrument is attributed to prior work without locating the specific adapted version. No block trigger fired — I verified arithmetic consistency across the manuscript (233 − 14 − 5 = 214; CI [.30, .52] reproduces at *r* = .42, *n* = 214; detectable *r* ≥ .19 reproduces at 80% power, α = .05 two-tailed; *M* = 3.6 and *SD* = 0.8 within scale bounds), constructs are named consistently with the items described, and the design is labelled correctly throughout.

### D3: argumentative_coherence
score: warn

Warn triggers fired: generalization to "undergraduates" without institutional qualification in the abstract's closing sentence, which also substitutes "LMS engagement" for the "self-reported use" the body maintains; §5's onboarding implication crosses the perception-versus-behavior boundary the paper itself draws in §2, though it is hedged; confounding is named narratively in §4 but is absent from §6's limitations list and unaddressed analytically. No block trigger fired — no causal claim is asserted as a finding, reverse causation is explicitly handled in §5, no conclusion contradicts the results section, and there is no evidence of selective presentation.

### D4: cross_disciplinary_relevance
score: warn

Warn triggers fired: partial context reporting — the LMS platform is never named, mandatory-versus-optional use in the sampled courses is unstated, the three-week window has no calendar position, and disciplinary composition and year-level counts are absent; the population to which the finding is said to apply is left implicit at the abstract; no statement of what conditions would need to hold for the association to travel to another institution or platform. No block trigger fired — the setting is partially described (institution type and size band, recruitment channel, window length, four year levels represented), and §6 explicitly disclaims generalization rather than asserting it for other sectors.

### D5: writing_and_structure
score: warn

Warn triggers fired: no tables or figures anywhere, including the scatterplot §3.4 states was inspected; the criterion's distribution, dispersion, and three of five anchor labels are absent, so the reporting surface omits information a methods reader requires; *df* omitted; APA notation deviations; a minor abstract-body label mismatch ("LMS engagement" versus "self-reported use") that does not change the conclusion. No block trigger fired — the method subsections are present, locatable, and conventionally organized; the primary estimate is reported numerically in text; and the abstract describes design, sample, and measures accurately.

## Failure Condition Checks

### F1
fired: false

Predicate: any mandatory dimension scores 'block'. Mandatory dimensions are D1, D2, D3; all three score 'warn'. No block.

### F2
fired: true

Predicate: two or more mandatory dimensions score 'warn' or worse. D1, D2, and D3 all score 'warn' — three of three mandatory dimensions, exceeding the threshold of two.

### F3
fired: false

Predicate: any high-priority dimension scores 'block'. The single high-priority dimension, D4, scores 'warn', not 'block'.

### F0
fired: false

Predicate: every mandatory dimension scores 'pass'. D1, D2, and D3 all score 'warn'.

## Review Body

This manuscript is unusual in the direction it errs. Its causal discipline is exemplary and its headline statistics are, as far as I can verify them, correct — I recomputed both the 95% confidence interval and the effect-size sensitivity figure and each reproduces exactly at the reported *n*. The paper refuses causal language at every point where the genre normally reaches for it, states the reverse pathway as equally consistent with the data, and describes its own contribution as bounded. That is real methodological virtue and it should be credited in the decision letter rather than treated as a rhetorical maneuver.

The binding constraint is nonetheless measurement, not inference, and the manuscript is silent exactly there. The criterion is a single ordinal item carrying no reliability estimate, no reported distribution, and only two of its five anchor labels. Three consequences follow, and they are independent of how the paper frames itself. First, the reported association is attenuated by an unknown amount: with the predictor at α = .88 and the criterion's reliability unmeasured, plausible values in the .60–.70 range would put the disattenuated coefficient near .54–.58, which is a different verbal magnitude than the "moderate" the paper repeats. The hedging here cuts against the authors' own result. Second, the study is not replicable at the instrument level — neither the six predictor items nor the three interior criterion anchors are printed, so no one can re-administer what was administered. Third, the designation of Pearson as primary contradicts §3.2's own declaration that the outcome is ordinal; because ρ = .40 and *r* = .42 differ trivially, inverting the designation costs the authors nothing and removes the inconsistency.

Two further items are load-bearing. The response rate is not merely unreported but unreportable as the manuscript stands, since the eligible-frame denominator is never given, and the only participant characteristic supplied ("spanned all four year levels") is too thin to support even a descriptive nonresponse check against institutional enrollment figures. Related to this, the recruitment channel is the institution's course-announcement channel; if that channel is hosted inside or authenticated through the platform under study, invitation exposure is conditioned on the outcome variable, which makes it a threat to the estimate and not only to its generalizability, where §6 currently files it. The direction of that bias is genuinely uncertain and the honest statement is that its magnitude is unknown. Separately, §3.1's removal of 5 duplicate entries cannot be reconciled with §3.3's statement that no identifying information was collected and responses could not be linked to individuals; I read this as reporting imprecision rather than misconduct and would say so to the authors, but as written the exclusion rule underlying the analyzed *N* is unverifiable. That finding also carries an ethics-representation reading owned by another seat, and I flag it for consolidation into a single item rather than double-counting.

The remaining gaps are inexpensive: *r*² = .18 is narrated in words rather than printed; *df* is omitted; distributional and scatterplot claims in §3.4 are asserted without any figure or numeric support; the manuscript contains no tables or figures at all; there is no data, code, or software statement; and the abstract's closing sentence drops both the single-institution bound and the perceived-versus-behavioral distinction that the body otherwise maintains carefully.

Taken together: three mandatory dimensions score warn, which fires F2. Nothing scores block — the headline estimate is verifiable and correct, the design is honestly labelled, no causal claim is asserted, and every contested analytic choice carries an acknowledgement and a reported alternative. Virtually all of the defects above are curable within the existing design, and several are curable from data the authors already possess. What revision cannot supply is a reliability estimate for a single item already administered, so the attenuation problem can be bounded and disclosed but not eliminated; the authors should be asked to do the former rather than left to hedge around it.

## Editorial Decision

Derived from the contract's failure-condition precedence applied to my own dimension scores: F2 (severity 70) is the only condition that fired; F1 (90) and F3 (60) require a block score that no dimension received, and F0 (10) requires all mandatory dimensions to pass. Highest fired severity therefore resolves to F2's action.

editorial_decision=major_revision

---

## SEAT — Peer Reviewer 2 (Domain)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** Read from the domain seat, this dimension asks whether the study's design, data handling, statistical reporting, and reproducibility affordances clear the bar that this specific subfield — quantitative survey research on student technology adoption in higher education — actually enforces, not a generic open-science bar. My reading of it is deliberately narrow: Reviewer 1 owns the technical adequacy of the design; I own whether the design choices are *defensible against what the field already knows*. In educational technology, cross-sectional self-report survey work has a long documented history of specific vulnerabilities (common-method variance, self-reported use as a poor proxy for logged use, single-institution convenience samples), and the field's own literature has repeatedly named them. So my D1 concern is whether the paper's methodological choices are made in awareness of that accumulated field knowledge or in ignorance of it. Any severity I assign here that rests on a claim about what educational-technology survey research *should* report must be grounded in an external checkable source (a reporting guideline, a venue data policy, a documented convention, a peer-reviewed methodological reference) or be down-rated to advisory and tagged `[FIELD-NORM UNVERIFIED]`.

**D2 — domain_accuracy (mandatory).** This is my primary dimension and the one where my seat carries the most weight. It asks whether the paper's claims align with current evidence in educational technology and LMS adoption research, whether prior work is represented as its authors actually argued it, and whether field-specific terminology and reported results are factually correct. For this paper's stated field, the accuracy surface is dense and well-populated: the technology-acceptance lineage (perceived usefulness and perceived ease of use as named constructs with specific operational definitions and a specific originating source), the distinction between *perceived* usefulness and *actual* utility, the distinction between *self-reported* use and *system-logged* use, the distinction between adoption, acceptance, engagement, and continuance intention, and the accumulated finding that self-reported use correlates only modestly with server-log use. Misattributing a construct to the wrong originating source, treating a construct as if it means something adjacent to what the field defines it as, or reporting a well-established field finding backwards are all D2 failures — and they are failures I can detect without any methodological expertise, purely from domain knowledge.

**D3 — argumentative_coherence (mandatory).** This asks whether the paper's central thesis holds together internally, whether its evidence actually supports what it claims, and whether any fallacy undermines the core argument. From the domain seat my angle is specifically the *domain-substantive* half of coherence rather than the purely logical half: does the theoretical framework the paper invokes actually do work in the paper, or is it named in the introduction and abandoned? Does the research gap the paper asserts correspond to a gap that plausibly exists in this literature? Do the conclusions stay inside what the reported evidence licenses, or do they slide from association to causation, from perception to behavior, from one institution to "students" in general? In a cross-sectional design the association-to-causation slide is the canonical coherence failure, and in a self-report design the perception-to-behavior slide is the second.

**D4 — cross_disciplinary_relevance (high priority, not mandatory).** This asks whether framing, definitions, and implications are legible to readers from adjacent fields and whether any interdisciplinary claim is substantiated. I hold this dimension with a light hand because Reviewer 3 owns it as their primary seat; my contribution is bounded to the domain-accuracy face of it. Educational technology sits at the junction of education, information systems, and psychology, and the same words carry different definitions across those three — "usefulness," "engagement," "adoption," "acceptance" all mean measurably different things depending on which literature you came from. My D4 question is therefore whether the paper is precise about *which* disciplinary tradition it is drawing each borrowed construct from, and whether claims that reach into an adjacent field (learning outcomes, motivation, organizational IT adoption) are supported by that field's evidence rather than asserted across the boundary.

**D5 — writing_and_structure (normal priority).** This asks whether the manuscript is organised, clearly expositive, adequate in its figures and tables, and conformant to venue conventions. I read this from the domain seat only where writing quality has *substantive* consequences: whether construct definitions are stated before they are used, whether the literature review is a critically synthesised argument or an annotated list, whether reported statistics are given with enough detail for a domain reader to interpret their magnitude, and whether terminology is used consistently across the manuscript rather than drifting between synonyms that the field treats as distinct. Pure style, prose infelicity, and formatting are outside my seat. The stated word count — roughly 1,600 words — is a structural fact I will hold in mind: at that length a paper is a short report or a brief communication, and the appropriate expectation is compression, not omission. Compression is not a D5 failure; silent omission of load-bearing content is.

## Scoring Plan

### D1: methodology_rigor

- `what_to_look_for` — Whether the paper names its design as cross-sectional and correlational and behaves accordingly in its inferential language; whether the sampling frame, recruitment route, response rate, and institutional setting are stated; whether the self-report use measure is described concretely (recall window, response scale, anchoring) rather than gestured at; whether any validated instrument is named with its source and any reliability evidence reported; whether the analysis reported matches the design (correlational/regression rather than causal-effect language); whether ethics review or informed consent is mentioned; whether common-method variance is acknowledged as a live threat given that predictor and outcome come from the same self-report instrument at the same moment; whether any limitations section engages the self-report-versus-logged-use gap that this subfield has documented at length; whether reproducibility affordances (instrument availability, item wording, data availability) are addressed at all. I will judge each of these against what survey-based educational-technology research demonstrably reports, and I will look for an external, checkable ground for any norm I invoke — a reporting guideline, a journal data policy, or a peer-reviewed methodological source — before I attach a severity to it.
- `what_triggers_block` — A methodological choice that is not merely thin but *substantively indefensible given what the field knows*, and where the indefensibility is visible on the paper's own face. Concretely: the paper draws a causal or effectiveness conclusion (perceived usefulness *increases* use, the LMS *improves* engagement) from cross-sectional self-report data with no design element that could license it; or the reported analysis is incompatible with the stated design (an effect estimate, a change score, a pre-post claim where no second time point exists); or the self-reported use outcome is treated interchangeably with actual system use with no acknowledgement, so the paper's entire result rests on a proxy the field has documented as weak; or the entire measurement apparatus is undescribed to the point that a domain reader cannot tell what was asked of students. A block also fires if a stated methodological fact is internally contradicted (two different sample sizes, two different instruments) such that no single defensible design can be reconstructed. I will not fire a block on a norm-based severity unless I have grounded that norm externally; if I cannot ground it, the finding is reported at advisory with `[FIELD-NORM UNVERIFIED]` and cannot by itself drive this dimension to block.
- `what_triggers_warn` — The design is defensible and the inferential language stays correlational, but the reporting is materially incomplete for a domain reader to assess the work: response rate or sampling route absent, instrument source or item wording unstated, reliability evidence missing for multi-item scales, no acknowledgement of common-method variance or of the self-report/log-data gap, ethics approval unmentioned, or no data/instrument availability statement where the field has a live convention for one. Warn also fires when limitations are present but perfunctory — listing "small sample" while omitting the design-specific threats that this subfield names as central. At ~1,600 words I will treat *compressed* reporting (a single dense methods paragraph that still names design, sample, instrument, and analysis) as acceptable and not warn on brevity alone; I warn when a load-bearing element is absent, not when it is short.

### D2: domain_accuracy

- `what_to_look_for` — Whether "perceived usefulness" is defined as the field defines it (a user's subjective judgment that using the system will improve their performance) rather than conflated with satisfaction, ease of use, liking, or actual benefit; whether the technology-acceptance lineage the paper draws on is attributed to its actual originating source rather than to a downstream review or a later restatement; whether the paper distinguishes acceptance from adoption from continuance from engagement, which the field treats as distinct constructs with distinct measurement traditions; whether self-reported use is named as self-reported rather than as "use" simpliciter; whether any empirical claim the paper makes *about the field* ("prior research consistently shows X", "LMS use is known to improve Y") matches what that literature actually reports, including its documented mixed findings and null results; whether the literature cited is current enough that a reader would recognise the last several years of work on LMS engagement and learning analytics, and whether it is drawn from more than one regional or methodological tradition; whether references are used as evidence for the specific claim they are attached to rather than as generic decoration; whether any reported statistic is described in domain-appropriate terms (a correlation described as a correlation, an effect size interpreted at a magnitude the field would recognise as small/moderate/large rather than inflated). I will also check for secondhand citation — a foundational construct attributed to a review article rather than its original source.
- `what_triggers_block` — A factually wrong domain claim that is load-bearing for the paper's argument. Concretely: a core construct is misdefined or conflated with a different named construct in a way that changes what the paper is measuring (perceived usefulness defined as ease of use, or as satisfaction, or as actual learning benefit); a theory or construct is attributed to the wrong originator, or a theory's central claim is stated backwards; a claim about the state of the LMS-adoption literature is asserted as settled when the field's evidence is mixed or points the other way, *and* the paper's contribution depends on that assertion; self-reported use is presented as actual system use in the paper's own conclusions without qualification; or a reported result is interpreted in a way the domain cannot support (an association between two self-report measures collected simultaneously read as evidence that one produces the other in students' actual behavior). Block also fires on a citation that does not support the claim it is attached to, where that claim is load-bearing — a domain-accuracy failure regardless of whether the reference itself exists. Where a finding of mine rests on a claim about field practice rather than on a checkable fact, the Step 5 grounding rule applies: I ground it externally or down-rate it.
- `what_triggers_warn` — Domain content that is defensible but imprecise or thin. Terminology used loosely but recoverably (adoption and acceptance used interchangeably where the argument does not turn on the difference); a construct defined correctly but never operationalised in terms a domain reader can map to the items; a foundational work cited secondhand through a review while the substantive claim remains correct; literature coverage that omits the last several years, or that is confined to a single region or single methodological tradition without acknowledging that as a scope limit; a real but overstated characterisation of prior findings ("consistently" where the record is "generally, with exceptions"); an effect described without the magnitude context the field would expect; or a construct borrowed from the acceptance tradition without noting that this paper's cross-sectional self-report operationalisation is a weaker instantiation of it than the source tradition used. Warn also fires when the research gap is asserted rather than demonstrated — a gap claim with no evidence that the field has not already addressed it. At ~1,600 words I will not warn on a short reference list per se; I warn when a *specific* body of work that the paper's own argument depends on is absent.

### D3: argumentative_coherence

- `what_to_look_for` — Whether the research question stated at the front is the question the results answer and the conclusion addresses; whether the theoretical framework named in the introduction actually shapes the measures, the analysis, and the discussion, or is dropped after its first mention; whether each conclusion sentence is traceable to a reported result; whether the causal register of the language is stable across abstract, results, discussion, and any practical recommendation, or escalates as the paper proceeds (associations in the results becoming drivers in the discussion becoming interventions in the implications); whether the paper's practical recommendations to institutions follow from what was actually measured; whether the limitations section is consistent with the strength of the claims made elsewhere rather than contradicting them; whether the gap the introduction asserts is the gap the contribution actually fills; whether generalisation from the study's sample to "undergraduate students" broadly is asserted or argued.
- `what_triggers_block` — A coherence break that undermines the central argument. Concretely: the abstract or conclusion states a causal or effectiveness finding the design cannot yield and the results section does not state (the discussion asserting that improving perceived usefulness will raise LMS use, from a single-timepoint correlation); the stated research question and the reported analysis do not correspond, so no reported result addresses the question asked; a conclusion contradicts the paper's own reported numbers or its own limitations section; the paper recommends an institutional intervention whose warrant does not exist anywhere in its evidence; or the theoretical framework is invoked to license a claim it does not actually license. Block also fires when the paper's contribution claim is circular — the gap is defined so as to be filled by whatever the paper happened to measure, with no independent argument that the gap matters.
- `what_triggers_warn` — Coherence is intact at the core but strained at the edges: the theoretical framework is named and loosely honoured but not used to guide analysis or fed back into in the discussion; causal-sounding verbs appear in the discussion while the results stay correlational, without the claim structure actually collapsing; generalisation beyond the sampled institution or population is implied by phrasing rather than argued, and not flagged as a limitation; the research gap is stated plausibly but not substantiated against the literature; a practical implication is reasonable but reaches slightly past the evidence; or the limitations section acknowledges a threat that the discussion elsewhere writes as if resolved. Warn also fires when the argument is compressed to the point that a step is implicit but reconstructible — at ~1,600 words an elided step is a warn, not a block, provided the reader can reconstruct it and it does not contradict anything stated.

### D4: cross_disciplinary_relevance

- `what_to_look_for` — Whether constructs imported from information-systems and psychology traditions are labelled with their source tradition and defined at first use, so an education reader who has not read the acceptance literature can follow; whether the paper's framing makes its stake legible to adjacent readers (learning sciences, higher-education administration, institutional research, information systems) rather than addressing only insiders of one tradition; whether any claim that reaches into an adjacent field — that LMS use relates to learning outcomes, motivation, retention, or institutional effectiveness — is supported by evidence from that field rather than asserted across the boundary; whether jargon carrying different meanings in different disciplines is disambiguated; whether the implications section speaks to more than one audience where the paper claims relevance to more than one. I hold this dimension narrowly since Reviewer 3 owns it primarily; I will contribute only the domain-accuracy face of it and will not duplicate their seat's judgment.
- `what_triggers_block` — An interdisciplinary claim asserted with no substantiation, in a place where the paper's contribution depends on it. Concretely: the paper claims its findings bear on learning outcomes, academic performance, retention, or motivation while having measured none of these and citing no evidence linking its measured constructs to them; or a construct is imported from an adjacent discipline and used with a definition that discipline does not recognise, in a way that makes the paper's claim wrong rather than merely imprecise. Because D4 is high-priority rather than mandatory under this contract, a block here drives the F3 condition rather than F1 — I will therefore hold the block bar at genuine unsubstantiated boundary-crossing, not at accessibility shortfalls, and I will not import Reviewer 3's broader remit into my own scoring.
- `what_triggers_warn` — Constructs used without first-use definition such that an adjacent-field reader must already know the acceptance literature to follow the argument; framing written entirely for one tradition's insiders while the implications claim broader relevance; a cross-field implication stated cautiously but without supporting citation; terminology whose meaning differs across education, psychology, and information systems used without disambiguation; or an implications section that names multiple audiences but addresses only one. At ~1,600 words I will accept compressed definitions — a parenthetical gloss counts as a definition — and warn only when the term is load-bearing and left entirely unglossed.

### D5: writing_and_structure

- `what_to_look_for` — Whether the manuscript has the sections its claims require (a reader can locate the question, the design, the sample, the measures, the results, and the limitations, in whatever compressed form); whether construct definitions precede their use; whether the literature review argues toward the gap rather than listing sources; whether reported statistics carry enough detail to be interpreted (n, direction, magnitude, and precision or uncertainty in whatever form the analysis yields); whether tables and figures, if present, are self-explanatory and consistent with the text's numbers; whether terminology is stable across the manuscript rather than drifting between field-distinct synonyms; whether the abstract accurately represents the paper's design, findings, and hedging rather than presenting a stronger version of them; whether citation practice is consistent. I calibrate all of this to a ~1,600-word short report: the correct expectation is dense compression, and I will treat concision as competence, not deficiency.
- `what_triggers_block` — Structure or exposition that defeats domain review of the substance. Concretely: the paper's numbers are internally inconsistent between abstract, text, and any table, so no single set of results can be reconstructed; a load-bearing result is stated with no supporting detail anywhere in the manuscript (a claimed relationship with no statistic, no direction, no sample attached); the abstract reports a finding the body does not contain, or states it at a strength the body contradicts; or the manuscript lacks any statement of what was done to whom, such that the study cannot be evaluated at all. I set the block bar here deliberately high because D5 is normal-priority and a block on it fires no failure condition in this contract — so I reserve it for exposition failures severe enough that they block substantive assessment, and I will not inflate a writing complaint into a block to manufacture severity.
- `what_triggers_warn` — Organisation or exposition that is workable but materially impedes a domain reader: the literature review enumerates rather than synthesises; a construct is used before it is defined; statistics are reported without magnitude or uncertainty context; terminology drifts between field-distinct synonyms in a way a reader must resolve; a table duplicates rather than extends the text, or its numbers are formatted so the reader must recompute them; the abstract under-hedges relative to the body; section boundaries are absent so design and results run together; or citation practice is inconsistent enough to obscure which source supports which claim. Brevity alone is never a warn at this word count — I warn when compression has crossed into omission of something load-bearing, and I will say which element is missing rather than asserting the paper is "too short."

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Domain Review Report (Peer Reviewer 2)

### Reviewer Identity

Senior educational-technology researcher whose program of work is the empirical history of the Technology Acceptance Model in education; author of a meta-analysis synthesizing perceived-usefulness–to–use correlations across higher-education samples, and a frequent critic of what the field calls "TAM replication inflation." I know the primary-source acceptance literature (Davis, 1989; Venkatesh & Davis, 2000; Venkatesh et al., 2003; Šumak et al., 2011) and the LMS-specific engagement literature in detail, and I read submissions in this genre against the field's accumulated distribution of estimates rather than against a discipline-neutral standard.

### Overall Recommendation

Major Revision

### Confidence Score

4

### Summary Assessment

The manuscript is domain-competent in a way that most submissions in this genre are not. Perceived usefulness is defined in essentially the terms the acceptance tradition uses, the causal direction is left genuinely open (including explicit acknowledgement of the reverse pathway), self-reported use is consistently named as self-reported rather than laundered into behavioural use, and the paper declines to claim it is testing an acceptance model. Those are real domain virtues and I want them credited.

The domain problem is not accuracy but anchoring. The paper asserts three times — abstract, §5, §7 — that its estimate is "consistent with prior technology-acceptance research," and never once states what prior research found. It has no numeric comparator anywhere. Worse, §2 explicitly announces the correct interpretive frame, citing Song (2018) to argue that any single-site estimate "is best read as one point in a distribution," and then the Discussion silently abandons that frame and reverts to standalone reporting. The comparison the paper promises itself is never performed. Compounding this, the six-item reference list contains no primary source for the construct the paper is built on, and no synthesis of the association it claims consistency with — so the comparative claim is not merely unperformed, it is unsupportable from the cited evidence base. The contribution as stated ("a single, transparently reported association") rests on transparency alone, which is a reporting virtue, not a knowledge contribution.

### Strengths

1. **Construct definition matches the field's operative definition.** §2 defines perceived usefulness as "the degree to which a person believes a technology will help them perform better." That is substantively the acceptance tradition's definition, and the paper does not conflate it with ease of use, satisfaction, liking, or actual learning benefit — the four conflations I most often have to correct in this genre. §3.2 keeps the operationalisation consistent with that definition.

2. **The perception/behaviour boundary is held, not blurred.** The title, abstract, measures, results, and conclusion all say "self-reported use." §2 explicitly cites Vasquez (2020) on self-report/log divergence and states the consequence — that such studies "capture perceived rather than actual engagement." This is the single most common domain error in LMS-adoption survey work and the paper does not make it. The one place the boundary softens is §5's onboarding implication (see W3).

3. **Bidirectional causality is conceded, not merely hedged.** §5 states that the reverse pathway — more use raising perceived usefulness — is "equally consistent with the data," attributed to Delgado (2020). Naming the reverse pathway as *equally* consistent is stronger and more accurate than the usual "causality cannot be inferred" formula, and it is the domain-correct reading of a single-timepoint acceptance correlation.

4. **Scope discipline against theory-testing overreach.** §1 and §2 both refuse to present the study as a test of an acceptance model. Given that the field is saturated with single-correlation papers dressed as model tests, declining that framing is a genuine domain virtue and should survive revision.

5. **§2 identifies the correct interpretive frame for a single-site estimate.** The Song (2018) "one point in a distribution" argument is exactly the right way for a domain reader to situate a single-institution correlation. That the paper articulates it is a strength; that it never executes it is W1.

### Weaknesses

1. **W1 — The benchmarking the paper promises in §2 is never performed, so "consistent with prior research" is an unanchored claim.** The manuscript makes the consistency claim three times (Abstract; §5 "consistent with prior technology-acceptance research (Costa & Wren, 2019; Ibarra & Poll, 2021)"; §7 "consistent with prior work") without ever stating a single prior estimate — no r, no range, no pooled value, no CI overlap. §2 sets up the correct frame ("one point in a distribution") and §5 abandons it. This is not a tone problem: it is the paper's central comparative claim, and as written a domain reader cannot evaluate whether r = .42 sits at, above, or below where this literature's estimates cluster. The claim is also unverifiable from the cited set — §2 says effect sizes "vary across samples and instruments" without reporting the variation, and Song (2018), the one cited source explicitly reporting between-institution variability, is never revisited with numbers in §5. **Fix:** state the comparator explicitly. Report at least Song's (2018) across-campus range and, if the authors can obtain one, a meta-analytic pooled estimate for the perceived-usefulness/use association in higher-education samples, then say in one sentence where [.30, .52] falls relative to it. If no numeric comparator can be retrieved, the honest revision is to delete the consistency claim from all three locations rather than retain it unanchored. **Severity grounding:** this severity does not rest on a field-practice norm — it rests on an internal defect visible on the paper's own face (a comparison announced in §2 and not delivered in §5/§7), so no external norm grounding is required.

2. **W2 — The construct's primary source is absent and the comparative claim has no synthesis anchor.** Perceived usefulness is defined in §2 in the acceptance tradition's own terms but attributed solely to Costa and Wren (2019) and Delgado (2020) — two secondary sources within the cited set. No primary source for the construct appears anywhere in the six-item reference list, and no meta-analytic or systematic synthesis of the perceived-usefulness/use association appears either. These are two distinct problems with different consequences. The provenance gap is a scholarly-credit issue and is straightforwardly fixable. The synthesis gap is load-bearing: it is *why* W1 cannot be repaired from the current bibliography, because the paper has no source in hand that reports the distribution it claims consistency with. I want to be precise that "add more references" is not the fix I am asking for — adding six citations without performing the §2 comparison would leave W1 exactly where it is. **Fix:** cite the originating source for perceived usefulness directly rather than through intermediaries, and add at least one synthesis that reports a pooled or ranged estimate, then use it in §5. **Severity grounding:** the primary-source-attribution expectation is a field norm; I have not grounded it against a checkable external source in this session (no venue author policy, style manual, or methodological reference is available to me here), so I report the detection and down-rate the *severity assertion* accordingly — `[FIELD-NORM UNVERIFIED]`. The synthesis-anchor half of this weakness does not depend on a norm: it is the enabling condition for W1's internal defect and carries W1's severity.

3. **W3 — The §5 onboarding implication quietly re-crosses the perception/behaviour boundary the rest of the paper defends.** The recommendation is that "LMS onboarding which helps students see concrete usefulness ... may be worth institutional attention." The paper measured an association between two simultaneously collected self-report measures. The recommendation's warrant requires that raising perceived usefulness changes *behaviour* — but behaviour was not measured, and §2's own citation of Vasquez (2020) establishes that the self-report indicator is not a behavioural count. The hedging ("modest support," "may be," "suggested by, not proven by") correctly disclaims *causality* but does not disclaim the *construct substitution*, which is a separate and unhedged move. The Whitfield (2019) attachment does not repair this: a practitioner account of onboarding is not evidence that perceived usefulness is manipulable or that manipulating it changes use. **Fix:** either restate the implication strictly in perception terms (onboarding that raises perceived usefulness is associated with students who report using the system more), or drop the recommendation. If the authors keep it, the boundary must be stated in the same sentence, not left to §6.

4. **W4 — The stated contribution is a reporting property, not a knowledge property.** §2 offers the contribution as "a single, transparently reported association from one undergraduate sample, using a previously validated measure." Transparency is how a contribution should be *delivered*; it is not itself a contribution to what the field knows. If the perceived-usefulness/use association is already established across the literature (which §2 asserts, if without numbers), a single-site replication adds to knowledge only if it supplies something the existing record lacks — moderator information, a distinctive or under-studied population, an improved measure, a preregistered replication design, or a placement of the estimate within the known distribution. None of the first four is present. The fifth is available at low cost and is exactly what W1 asks for: performing the §2 benchmarking would convert this from "another correlation" into "a datum located within the field's distribution," which is a real if small contribution. I flag as domain-relevant, not as my verdict, that whether that suffices for publication is the Editor's call, not mine. **Fix:** either add substantive analytic depth, or reposition the contribution around the benchmarking that §2 promises and execute it.

5. **W5 — Scale adaptation is reported with reliability but not with validity evidence, and the adaptation is never re-justified in domain terms.** §3.2 says the six-item measure was "adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency," and reports α = .88 in this sample. What "adapted" means is never stated — item rewording, item reduction, context substitution, or all three — and no factor structure or other validity evidence is reported for the adapted version in this sample. Internal consistency is not structural validity; a set of items can cohere at α = .88 while measuring something adjacent to the source construct. This matters at the domain level rather than the psychometric level because the paper's entire comparability claim (W1) presumes its instrument measures the same construct as the studies it claims consistency with. I note the psychometric evaluation of the adaptation belongs to Reviewer 1; my concern is narrowly that an undocumented adaptation weakens the cross-study comparability the paper depends on. **Fix:** state what was changed and why, and either report structural evidence for the adapted six items in this sample or explicitly limit the comparability claim.

### Detailed Comments

#### Literature Review

- **Coverage.** Six references support a paper positioned inside the technology-acceptance tradition. The gap is not the count as such — a short report can be lean — but *which* sources are missing: the construct's originating source and any synthesis reporting the distribution of the association the paper claims consistency with. Both are load-bearing for claims the paper actually makes. Coverage of debate is otherwise better than the count suggests: Delgado (2020) supplies the reverse-causality caution, Ibarra and Poll (2021) supply the contextual-confounding caution, and Vasquez (2020) supplies the measurement caution. The paper engages its cited critics rather than citing them decoratively. Recency and regional/methodological breadth cannot be assessed from the cited set as given — the venues are unfamiliar to me and I will not guess at them.
- **Integration quality.** Genuinely synthesised, not enumerated. §2 organises around a claim (association exists) followed by three distinct cautions, each attributed to a specific source for a specific reason. That is above the median for this genre.
- **Research gap argument.** Weak, and weak in a specific way: the paper does not really argue a gap. It argues *comparability* ("an incremental data point, comparable with prior work"). Comparability is a legitimate rationale, but it converts the §2 benchmarking from optional to obligatory — a data point offered for comparison must actually be compared. The paper's own framing is what makes W1 a structural defect rather than a stylistic one.

#### Theoretical Framework

- **Appropriateness.** Appropriate, with a caveat. The paper draws one construct from the acceptance tradition rather than adopting the framework, and says so. For a single-association descriptive study that is a defensible choice and avoids the overreach of dressing a bivariate correlation as model testing.
- **Application depth.** Deliberately shallow, and honestly declared as such — §1 and §2 both disclaim model-testing. The cost of that honesty is that the framework does no analytic work: it supplies a construct label and nothing more. No theoretical claim is tested, extended, or challenged, and the conclusions do not feed back to theory. Under the paper's own framing this is consistent rather than contradictory, but it means the contribution can only be empirical, which sharpens W4.
- **Alternative frameworks.** None needed for a study of this scope. A richer acceptance framework would require constructs the paper did not measure. Recommending one would be demanding a different study, not improving this one.

#### Academic Argument Quality

- **Factual accuracy.** I found no factually wrong domain claim. The construct definition is right, the reverse-causality logic is right, the self-report/log-divergence characterisation is right, and "moderate" is an accurate qualitative label for r = .42 in this literature. The unsupported claim is comparative, not factual: "consistent with prior technology-acceptance research" asserts a relation to a body of evidence whose values the paper never states (W1). That is an unanchored claim rather than a false one, and I score it as such.
- **Argument logic.** One substantive break: §2 establishes the "one point in a distribution" frame and §5 does not use it. One construct-substitution slide: §5's onboarding implication (W3). Otherwise the inferential register is stable across abstract, results, discussion, and conclusion — notably, the abstract does not strengthen the body's claims, which is the reverse of this genre's usual failure.
- **Terminology precision.** Consistent and field-appropriate. "Association," "correlated," "self-reported use," and "perceived usefulness" are used stably throughout, with no drift between acceptance/adoption/engagement/continuance. One imprecision: §1's "a substantial body of work suggests" is supported by a single citation, and §2's "effect sizes vary across samples and instruments" reports no variation — both are gestures at a literature the paper does not display.

#### Contribution to the Field

- **Incremental contribution.** Empirical and small: one bivariate association from one institution, well reported. No moderator, no multivariate context, no behavioural criterion, no theoretical extension. The available upgrade is the §2 benchmarking, which would locate the estimate in the field's distribution — a modest but real contribution, and one obtainable without new data.
- **Positioning.** Positioned honestly as incremental and design-bounded. The positioning is undermined by its own execution: a paper that positions itself as comparable-with-prior-work and then never compares has not completed its stated positioning.
- **Overclaiming.** Low, and genuinely so — this is not a paper that over-reads its data. But under-claiming is not automatically a virtue: the hedging is thorough on causality and absent on two other axes (construct substitution in §5's implication, W3; instrument comparability, W5). Correctly naming the causal limitation does not resolve the others, and the visible caution should not be read by the panel as evidence that every limitation has been handled.

#### Missing Key References

- The originating primary source for the perceived-usefulness construct in the technology-acceptance tradition. `[UNVERIFIED]` as a citation — I will not assert author/year/venue metadata from memory under the no-invention rule. Search lead: the foundational technology-acceptance paper introducing perceived usefulness and perceived ease of use as named constructs, and the subsequent extensions of that model. Justification: the paper defines the construct in that tradition's terms while citing only intermediaries.
- A meta-analysis or systematic synthesis reporting pooled perceived-usefulness → use estimates in higher-education or LMS samples. `[UNVERIFIED]` as a citation — search lead: meta-analytic syntheses of technology acceptance in e-learning/LMS contexts. Justification: this is the enabling source for the §2 benchmarking the paper promises; without it W1 cannot be repaired.
- Beyond these two, I recommend no additions. The paper's cited critical sources (Delgado, Ibarra & Poll, Vasquez, Song) are doing real argumentative work, and padding the list would not address the defect.

### Questions for Authors

1. §2 argues, via Song (2018), that a single-site estimate is best read as one point in a distribution. What is the distribution? Please state the range Song reports across campuses, and any pooled estimate you can obtain, and say explicitly where [.30, .52] falls relative to it.
2. "Consistent with prior technology-acceptance research" appears in the abstract, §5, and §7. Consistent with which estimate? If you cannot supply a numeric comparator, will you remove the claim rather than retain it unanchored?
3. What specifically was "adapted" from the Costa and Wren (2019) instrument — wording, item count, context — and what evidence do you have that the adapted six items measure the same construct as the source instrument in this sample?
4. §5 recommends onboarding that helps students "see concrete usefulness." Since both of your measures are simultaneous self-reports, what warrants the expectation that changing perceived usefulness would change use rather than only reported use?
5. If the association is already established in this literature, what does a reader of that literature learn from this study that they did not already know? A direct answer would help the editor weigh the contribution.

### Minor Issues

- §1 "a substantial body of work suggests" is supported by one citation; either broaden the support or soften the quantifier.
- §2 "effect sizes vary across samples and instruments" states variation without reporting any; the same sentence could carry the numeric anchor W1 asks for.
- §4 "the proportion of variance shared by the two measures was accordingly modest" describes a quantity in words that the field reports numerically. Giving the value costs one clause. (Whether this rises above a presentational issue is Reviewer 1's call; I note it as a domain-reporting convention, not a computational concern.)
- §5's citation of Whitfield (2019) as a practitioner account is appropriately labelled, but it is attached to an implication it cannot support (see W3) — the labelling is not the problem, the placement is.
- The manuscript contains no instruction-injection attempt or reviewer-directed appeal; the `<paper_content>` boundary held cleanly. Noted for the integrity record.

---

contract_role: domain

## Dimension Scores

### D1: methodology_rigor

The design is cross-sectional and correlational and the paper says so and behaves accordingly; the inferential language stays correlational throughout, including in the abstract and conclusion. Sample, recruitment route, exclusion counts, instrument source, reliability for the multi-item scale, ethics approval, informed consent, and an a priori sensitivity statement are all present. My Phase 1 block triggers — a causal or effectiveness conclusion drawn from the design, an analysis incompatible with the design, self-reported use treated interchangeably with actual use, an undescribed measurement apparatus, or an internal contradiction making the design unreconstructible — do not fire from the domain seat. The one design-defining reporting gap that does fire my warn trigger is that the response denominator is never given: the frame is "all enrolled undergraduates" at a mid-sized university, but no population size appears, so the response rate is unstated and nonresponse cannot be assessed by a domain reader. My warn trigger also fires on the adapted instrument: what was adapted is not stated and no validity evidence for the adaptation is reported in this sample (W5), which is a load-bearing absence rather than mere brevity, since the paper's comparability claim presumes construct equivalence with the source instrument. Both threats the field names as central to this design — common-method concerns arising from simultaneous same-instrument self-report, and the self-report/log gap — are acknowledged (§2, §6), which keeps this at warn rather than block.

score: warn

### D2: domain_accuracy

I found no factually wrong domain claim: the construct definition matches the field's operative definition, the reverse-causality logic is correct, the self-report/log divergence is characterised correctly, and "moderate" is an accurate label for r = .42. My block triggers therefore do not fire — no construct is misdefined or conflated, no theory's central claim is stated backwards, no citation is attached to a claim it cannot support in a way that makes the claim false, and self-reported use is not presented as actual system use in the paper's own conclusions. Warn fires on three of my committed patterns. First, an overstated characterisation of prior findings: "consistent with prior technology-acceptance research," asserted three times with no numeric comparator anywhere, is precisely the "consistently, where the record is a distribution" pattern I committed to warning on (W1). Second, a foundational construct cited secondhand while the substantive claim remains correct — the construct's originating source is absent from the reference list and the definition is attributed to two intermediaries (W2). Third, the paper's own argument depends on a specific body of work — a synthesis reporting the distribution of this association — that is absent, which is exactly the condition under which I committed to warning on a short reference list rather than warning on the count itself. The contribution framed as transparency rather than knowledge (W4) sits in this dimension's "gap asserted rather than demonstrated" pattern. None of these is a factual error, so warn rather than block is the correct score.

score: warn

### D3: argumentative_coherence

The research question stated in §1 is the question the results answer and the conclusion addresses; the causal register is stable across abstract, results, discussion, and conclusion, and the abstract does not strengthen the body. My block triggers — a causal or effectiveness finding the design cannot yield, a mismatch between question and analysis, a conclusion contradicting the paper's own numbers or limitations, or a framework invoked to license a claim it does not license — do not fire. Two of my committed warn patterns do. First, §2 establishes the "one point in a distribution" frame and §5 and §7 abandon it: the framework named in the literature review is not fed back into the discussion, and the comparison the paper sets itself is never performed. Second, §5's onboarding implication reaches past the evidence — not causally, since that is hedged, but by construct substitution: the recommendation's warrant requires behaviour change while the study measured perception and reported perception (W3). The circularity trigger warrants comment: the contribution is framed as comparability rather than as filling a gap, which stops short of the circular gap-definition I committed to blocking on, but leaves the positioning incomplete because the comparison it rests on is not executed. Coherence is intact at the core and strained at exactly two identified points, which is the warn condition, not the block condition.

score: warn

### D4: cross_disciplinary_relevance

Perceived usefulness is glossed at first use in §2 in terms an education or institutional-research reader can follow without prior acceptance-literature knowledge, which satisfies my committed compressed-definition standard for a short report. My block trigger — an interdisciplinary claim asserted with no substantiation where the contribution depends on it — does not fire from my seat: the paper does not claim its findings bear on learning outcomes, academic performance, retention, or motivation, which is the boundary-crossing I committed to blocking on, and it does not import a construct with a definition the source discipline would not recognise. The §5 onboarding implication does reach toward an institutional-practice audience, and its warrant gap is real (W3), but I have scored that under D3 where its coherence character is primary rather than double-counting it here. What remains is a warn-level shortfall: the paper does not disambiguate the traditions it borrows from — "engagement," used in §2 and in the abstract, carries different meanings in the acceptance tradition, in learning analytics, and in the higher-education engagement literature, and the paper uses it as a near-synonym for reported frequency of access without saying so. Reviewer 3 owns this dimension primarily and I defer to their fuller judgment; my contribution is bounded to that terminological point.

score: warn

### D5: writing_and_structure

The manuscript is well organised for a short report: IMRaD with separate Limitations and Conclusion, construct definitions precede their use, the literature review synthesises rather than enumerates, terminology is stable, and the abstract does not overstate the body. Numbers are internally consistent — n = 214 appears consistently across §3.1, §4, §5, and §7, and r = .42 is stated identically wherever it appears. My block triggers — internally inconsistent numbers, a load-bearing result with no supporting detail, an abstract reporting what the body does not contain, or no statement of what was done to whom — do not fire, and I committed to setting this bar high rather than inflating a writing complaint into severity. Two of my warn patterns fire. First, a statistic is reported qualitatively where the field reports it numerically: §4's "the proportion of variance shared by the two measures was accordingly modest" states in words a value the reader must compute. Second, §2's "effect sizes vary across samples and instruments" and §1's "a substantial body of work" both gesture at quantities the manuscript never displays, which impedes a domain reader's ability to interpret the magnitude claims the paper rests on. Both are compression crossing into omission of something load-bearing rather than brevity as such.

score: warn

## Failure Condition Checks

### F1

Predicate: any mandatory dimension (D1, D2, D3) scores `block`. My scores are D1 warn, D2 warn, D3 warn. No mandatory dimension scores block.

fired: false

### F2

Predicate: two or more mandatory dimensions score `warn` or worse. D1 warn, D2 warn, D3 warn — three mandatory dimensions at warn, exceeding the threshold of two. The `cross_reviewer_quantifier` (majority) is panel-level machinery for the synthesizer; I evaluate the expression against my own scores only.

fired: true

### F3

Predicate: any high-priority dimension (D4) scores `block`. D4 scores warn, not block.

fired: false

### F0

Predicate: every mandatory dimension scores `pass`. D1, D2, and D3 all score warn.

fired: false

## Review Body

The domain question this manuscript poses to a reviewer is unusual. Most submissions in the LMS-acceptance genre arrive over-claimed, and the reviewer's job is to pull the conclusions back to what the design supports. This one arrives systematically under-claimed, and the job is to test whether the hedging is doing epistemic work or standing in for it. My finding is that it does both, in identifiable places.

Where the hedging is genuine: the causal disclaimer is not boilerplate. §5 does not merely say causality cannot be inferred; it names the reverse pathway and calls it equally consistent with the data, which is the domain-correct reading of a single-timepoint acceptance correlation and stronger than most published treatments. The perception/behaviour boundary is held in the title, abstract, measures, results, and conclusion, and §2 supplies the reason it must be held via Vasquez (2020). The refusal to dress a bivariate correlation as an acceptance-model test is a real virtue in a field where that dressing is routine. These are not rhetorical gestures; they are correct domain judgments and they should be credited in the decision letter.

Where the hedging substitutes for work: correctly naming a limitation does not discharge it, and the paper has two unhedged problems sitting behind the hedged one. The first is the benchmarking failure. §2 does the intellectually right thing — it invokes Song (2018) to argue that any single-site estimate is one point in a distribution — and then §5 and §7 revert to standalone reporting, asserting consistency with prior research three times without ever naming a comparator. This is not a citation-count complaint and it would not be fixed by adding references. The paper set itself a comparison, the comparison is the interpretive frame it told the reader to use, and the comparison was not performed. A domain reader cannot tell from this manuscript whether r = .42 is typical, high, or low for this literature — which is the one thing a self-described "incremental data point, comparable with prior work" must supply. The reference list makes the failure structural rather than accidental: with no synthesis of the association in hand and no primary source for the construct, the comparison could not have been performed from the cited evidence base.

The second is construct substitution in §5's practical turn. The onboarding recommendation is hedged carefully on causality and not at all on what was measured. Its warrant requires that raising perceived usefulness changes behaviour; the study measured perception and reported perception, and the paper's own §2 citation establishes that the reported measure is not a behavioural count. The Whitfield (2019) attachment labels the source as practitioner work but does not supply the missing warrant. A reader moving quickly through §5 would take away an actionable behavioural claim that the paper's own §6 disclaims — which is the precise pattern the hedged prose makes harder to notice, not easier.

Two further domain observations. The instrument was "adapted" with no statement of what changed and no validity evidence for the adapted form in this sample; α = .88 establishes coherence, not that the six items measure the source construct. That matters here because the comparability claim presumes construct equivalence with the studies being compared to — so W5 and W1 are the same problem seen from two sides. And the stated contribution is transparency, which is a property of the reporting rather than of the knowledge produced; the available upgrade is the benchmarking already promised in §2, which would convert this from another correlation into a located one at no cost in new data. Whether that upgraded contribution clears a publication bar is the Editor's determination and I do not make it here.

Three mandatory dimensions score warn: D1 on the unstated response denominator and the undocumented instrument adaptation, D2 on the unanchored consistency claim and the absent construct-primary and synthesis sources, D3 on the abandoned §2 frame and the §5 construct substitution. None reaches block — there is no factual domain error, no causal overreach, no unreconstructible design, and no internal numeric contradiction — and I decline to manufacture one. But three mandatory warns satisfy F2 on my own scores, and the defects are concrete and mostly curable within the existing design: the benchmarking can be performed, the denominator supplied, the adaptation documented, the §5 implication restated in perception terms. The contribution question is the one item on my list that revision alone may not resolve, and it belongs to the Editor.

## Editorial Decision

Per the contract's `failure_conditions` precedence, F2 (severity 70) is the highest-severity condition that fired on my scores; F1 (severity 90) and F3 (severity 60) did not fire, and F0 is unsatisfied.

editorial_decision=major_revision

---

## SEAT — Peer Reviewer 3 (Perspective)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor.** As the outsider seat, I read this dimension not as a statistics audit (that belongs to Reviewer 1) but as a question of whether the design can bear the interpretive weight the paper will place on it. For a cross-sectional survey of undergraduate LMS adoption, the rigor question that reaches my seat is whether a single-timepoint self-report instrument is being treated as evidence for something it structurally cannot show — behaviour, causal influence, or change over a term. My paraphrase: the study's design, sampling frame, and measurement choices must be described well enough that a reader from an adjacent discipline (information systems, HCI, learning analytics, survey methodology) can judge what population the numbers speak for and what inferential range they license. Where I will speak on D1 is the fit between design and the claims it is asked to support, not the internal correctness of the statistics.

**D2 — domain_accuracy.** For me this is primarily a question of construct integrity and honest borrowing across field boundaries. "Perceived usefulness" is not a free-floating phrase — it is a named construct from the technology-acceptance tradition with a specific operational history, and "self-reported use" has a well-documented and much-studied gap from log-based actual use. Domain accuracy in this paper therefore means the constructs are used as the source literature defines them, the theoretical lineage is named rather than silently absorbed, and known limits of the tradition (self-report inflation, the usefulness–use correlation being partly method variance) are represented as the field actually understands them. A cross-disciplinary reader should not encounter a claim about LMS adoption that contradicts what the adjacent information-systems or learning-analytics literature has established without the paper acknowledging the tension.

**D3 — argumentative_coherence.** I do not audit logical form — no fallacy taxonomy, no section-vs-section contradiction sweep; those are Reviewer 1's and the Devil's Advocate's. What reaches my seat is coherence at the level of premises: whether the paper's argument rests on unstated assumptions that an outside discipline would immediately contest. Typical candidates in this literature are that perceived usefulness causes use, that use is an unqualified good, that a platform's value is captured by frequency of logins, or that students constitute one undifferentiated population. My paraphrase: the chain from "students report finding the LMS useful" to whatever the paper concludes must hold up when someone who does not share the field's default premises walks it step by step.

**D4 — cross_disciplinary_relevance.** This is my primary dimension and I hold it to a two-sided standard. Inward: can an adjacent-field reader — an HCI researcher, an instructional designer, a university administrator, a learning-analytics practitioner — understand what was measured, on what population, in what institutional context, and what it would mean for their own work? Terms native to educational technology must be defined at first use rather than assumed. Outward: any claim the paper makes that reaches beyond its own discipline — about student behaviour, about system design, about institutional policy, about implications for practice — must be substantiated at the same level it is asserted. An interdisciplinary gesture that is decorative rather than load-bearing, or a practice implication asserted with no bridge from the data, is a D4 problem even when every sentence inside the home discipline is defensible. I also read this dimension as covering context transferability: a survey at one institution carries an implicit claim about who else these findings speak for.

**D5 — writing_and_structure.** From the outsider seat, structure is a legibility question rather than a house-style question. At roughly 1,600 words this is a short-report-length manuscript, which makes structural economy a real constraint rather than an aesthetic preference: everything the reader needs to interpret the numbers — instrument, sample, response rate, institutional setting, limitations — must fit, and something has to give. My paraphrase: organisation and exposition should let a reader from another field locate the study's scope, method, and boundary conditions without reverse-engineering them, and the reporting apparatus (tables, item wording or its appendix pointer, limitation statements) should be present in proportion to the claims made. I score this dimension on whether compression has cost the reader interpretive access, not on prose polish.

## Scoring Plan

### D1: methodology_rigor

- `what_to_look_for` — Whether the design is named honestly as cross-sectional and self-report throughout, not just once in the methods; whether the sampling frame is described well enough to know who is represented (single institution? one course? volunteer sample? response rate?); whether "use" is defined as a self-reported quantity with an explicit acknowledgement that platform logs were not consulted; whether the tense and verb choice of the findings match a single-timepoint correlational design; whether the discussion of usefulness and use stays associational; whether known cross-sectional threats relevant to this specific topic — common-method variance from measuring both constructs on one instrument at one sitting, self-selection of engaged students into a voluntary LMS survey — are acknowledged anywhere.
- `what_triggers_block` — The paper's central conclusion requires an inferential move the design cannot support and this is not merely a phrasing slip but the load-bearing claim: causal or directional language about perceived usefulness driving use presented as a finding; self-reported use treated as a measure of actual platform use with no acknowledgement of the gap; recommendations to institutions framed as "this will increase use" on cross-sectional correlational evidence. Also blocks if the sampling frame is so unspecified that no reader can tell what population the findings claim to describe, while the paper nonetheless generalises to undergraduates broadly.
- `what_triggers_warn` — The design–claim fit is mostly sound but slips at the edges: causal verbs appear in the abstract or conclusion while the results section stays correlational; the self-report/actual-use gap is named in a limitations sentence but never affects how findings are stated; response rate, recruitment method, or institutional context is missing but the generalisation is appropriately hedged; common-method variance and self-selection go unmentioned though the claims stay within range.

### D2: domain_accuracy

- `what_to_look_for` — Whether "perceived usefulness" is anchored to its theoretical origin (technology acceptance / TAM lineage or an explicitly stated alternative) rather than used as ordinary language while borrowing the construct's authority; whether the operationalisation matches that definition; whether the well-established self-reported-versus-log-measured use discrepancy in LMS research is represented accurately if invoked; whether the paper's characterisation of what prior work found is recognisable to someone who reads adjacent information-systems and learning-analytics literature; whether LMS-specific terms (engagement, adoption, activity, usage) are used consistently rather than swapped as synonyms; whether any claim about student behaviour contradicts what adjacent fields have established without acknowledging the tension.
- `what_triggers_block` — A construct is used in a way that materially misrepresents the source tradition and the paper's conclusion depends on that misuse: perceived usefulness measured as satisfaction, enjoyment, or general attitude but discussed as the TAM construct; self-reported use presented as equivalent to actual use as an established fact rather than a limitation; a stated finding that contradicts a well-established result in the LMS adoption literature asserted without engaging the contradiction. Also blocks on a factually wrong characterisation of a named prior study or theory that carries the argument.
- `what_triggers_warn` — Construct provenance is thin rather than wrong: the theoretical lineage is implied but never named; terms like adoption, engagement, and use drift between paragraphs without definitional control; the self-report gap is mentioned but described more optimistically than the literature supports; prior work is characterised loosely or at a level of generality that an adjacent-field reader could not check.

### D3: argumentative_coherence

- `what_to_look_for` — Whether the paper states the premise connecting perceived usefulness to use, or leaves it implicit; whether "more use" is treated as self-evidently desirable without a stated warrant linking use to learning; whether the student population is treated as homogeneous when the argument's conclusion depends on it not being (commuter versus residential, first-year versus final-year, differing device or connectivity access, differing prior digital fluency); whether an alternative reading of the same association is acknowledged anywhere — that required coursework drives both the perception and the use, that reverse causation is equally consistent with the data, that instructor-level variation is the actual driver; whether the recommendations follow from what was measured or from the authors' priors.
- `what_triggers_block` — The central argument depends on an unstated premise that a reader from an adjacent discipline would reject on sight, and removing that premise collapses the conclusion. Concretely: the paper concludes that improving perceived usefulness will improve learning outcomes when only usefulness and use were measured; or it treats increased LMS use as an outcome worth pursuing in itself with no warrant anywhere; or its practice recommendation addresses a cause the study never examined. Also blocks when a plainly available alternative explanation would fully account for the reported association and the paper argues as if none existed.
- `what_triggers_warn` — Implicit premises are present but the conclusion survives without them: use-equals-good is assumed in the framing yet the stated conclusions stay descriptive; alternative interpretations are absent from the discussion but the claims are hedged enough to accommodate them; student heterogeneity is unaddressed though the conclusion does not depend on homogeneity; a recommendation reaches slightly past the data but is offered as a suggestion rather than a finding.

### D4: cross_disciplinary_relevance

- `what_to_look_for` — Whether an HCI, instructional-design, learning-analytics, or administrative reader is given the institutional context needed to interpret the result (what the LMS is used for at this institution, whether use is mandatory or discretionary, what the platform actually is); whether field-specific terms are defined at first use; whether stakeholders beyond the surveyed students appear anywhere — instructors who design the courses that drive LMS use, support staff, students with accessibility needs or constrained connectivity; whether any implication offered to practitioners or policymakers is traceable to something measured; whether the paper acknowledges what varies across institutional types, national systems, and disciplines, or writes as if one undergraduate population stands for all; whether interdisciplinary framing, where present, is substantiated rather than gestured at.
- `what_triggers_block` — A cross-disciplinary or applied claim is asserted at a strength the study cannot support and it is not incidental: a design recommendation for LMS platforms, an institutional policy prescription, or a generalisation about undergraduate students as a class, presented with no bridge from the single-context survey data and no hedge. Also blocks when the manuscript is written so entirely inside its own vocabulary and institutional assumptions that an adjacent-field reader cannot determine what was measured or on whom — the framing is not merely unfriendly but interpretively closed. Also blocks when a named interdisciplinary claim (borrowing a construct or a finding from another field) is made without substantiation and the argument leans on it.
- `what_triggers_warn` — Relevance is reachable but underserved: institutional context is thin, so transferability must be inferred; instructors and other stakeholders whose decisions shape student LMS use are absent from the discussion; practice implications are present but generic enough to have been written without the data; terms are used before definition though recoverable from context; cross-context limits are acknowledged in a single limitations sentence rather than shaping how findings are stated. A gestural interdisciplinary reference that decorates rather than carries the argument also lands here.

### D5: writing_and_structure

- `what_to_look_for` — Whether the roughly 1,600-word budget has been allocated so that interpretive essentials survive: sample and setting, instrument and item source, response rate, and limitations; whether the reader can find the study's scope and boundary conditions without reconstructing them; whether tables or reported statistics are legible on their own and consistent with the prose around them; whether the survey instrument is reproduced, appended, or at minimum sourced; whether the abstract's claim strength matches the body's; whether the structure follows a recognisable reporting convention for a short empirical report so an adjacent-field reader knows where to look.
- `what_triggers_block` — Compression has removed something without which the findings cannot be interpreted at all: no description of the sample or setting, no indication of what the instrument asked, or results reported with no accompanying account of how they were obtained. Also blocks when the abstract or conclusion states a materially stronger claim than the body supports, since a short paper is read disproportionately through its abstract and an outside reader will carry that stronger claim away.
- `what_triggers_warn` — The paper is followable but costs the reader work: limitations are compressed to a perfunctory sentence; item wording is neither shown nor sourced; a table's numbers are presented without enough labelling to stand alone or sit slightly inconsistently with the prose; section organisation departs from convention in a way that makes scope and method hard to locate; expository imbalance where framing consumes space that method and limitations needed.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Perspective Review Report (Peer Reviewer 3)

### Reviewer Identity

Learning-analytics scientist and institutional-research director. My daily material is LMS server-side event data at institutional scale; I have published on the divergence between self-reported and log-measured platform engagement, co-authored institutional guidance on the ethics of student-data collection, and I sit on a university research-ethics committee that reviews student-survey protocols. I am not a survey psychometrician and I do not audit the statistics here; I read this manuscript as someone who would either have to act on it institutionally or approve the protocol that produced it.

### Overall Recommendation

Major Revision

### Confidence Score

4

### Summary Assessment

This manuscript is unusually disciplined about what a cross-sectional self-report correlation can mean, and I want to credit that before criticising it: the title carries "self-reported," the reverse-causation reading is named with a citation, and the self-report/log divergence is engaged in the Literature Review rather than buried at the end. From my seat, however, correctly naming a limitation is not the same as resolving one, and this paper's largest limitation was avoidable rather than imposed. The study measures LMS use by asking students, at an institution that by definition holds a complete server-side access record for every respondent. The manuscript cites the divergence literature, concedes the point, and proceeds — without ever telling the reader why the criterion sitting in its own database was not used. There are defensible answers, including ethical ones, and the paper offers none of them.

Three further issues are mine to raise: the anonymity claim in §3.3 cannot coexist as written with the deduplication in §3.1; recruitment ran through a channel structurally adjacent to the platform under study, which touches the estimate and not only its generalisability; and the practice implication in §5 targets students while the paper's own cited mechanism sits with instructors. All are fixable within this design.

### Strengths

1. **The construct is named honestly where readers actually see it.** "Self-Reported Use" is in the title, not only in the limitations. In my field the standard failure is a paper that measures perception and reports it as behaviour; this manuscript closes that door in the first line, and an adjacent-field reader is protected from the most common misreading before they reach the Methods.

2. **The self-report/log divergence is treated as a framing decision, not a disclaimer.** §2 uses Vasquez (2020) to justify an explicit interpretive commitment — "treat our self-report measure as an indicator of perceived use rather than a behavioral count" — and that commitment then governs the Results section's wording. That is the right architecture, and it is rarer than it should be.

3. **The alternative readings an outsider would raise are already on the page.** Reverse causation is named with a source (Delgado, 2020); course requirements and assessment schedules are named as competing influences on reported use (§2, §4). I came to this manuscript expecting to supply those and found them supplied.

4. **Ethics reporting is specific rather than boilerplate.** Committee review, voluntary participation, no incentive, landing-page consent — each stated separately. This is above genre norm, which is precisely why the one internal inconsistency (W2) stands out as a reporting defect rather than as ordinary vagueness.

5. **§2 states the correct epistemics for single-site work.** Reading a single-campus estimate as "one point in a distribution" (via Song, 2018) is the frame an institutional researcher would want. My criticism (W5) is that the paper announces this frame and then does not execute it — but announcing it is a genuine strength to build on.

### Weaknesses

1. **W1 — The criterion was in the institution's own database, and the paper never says why it was not used.** Every respondent generated LMS access events; the institution holds them. The manuscript establishes (§2, Vasquez 2020) that self-report and logs diverge "sometimes substantially," concedes it again in §6, and proceeds. This converts what reads as an imposed limitation into an unexplained design choice. *Why it matters:* r = .42 may be an association between a perception and a second perception — the respondent's belief about their own frequency — rather than between perception and behaviour, and the divergence literature the paper itself cites gives no basis for assuming self-report error is unbiased noise. If students who rate the LMS useful also over-report their access, method variance inflates the estimate; the paper never raises this direction. *Suggested fix, and I mean this in two directions:* add two or three sentences to §3.2 stating the rationale. If it was governance — consent for log linkage, re-identification risk, committee constraints — say so; from an ethics-committee seat that is a *defensible and even preferable* rationale, and stating it converts a silent gap into a methodological position. If the logs were simply not requested, say that too. Better still, add a consent-linked validation sub-sample (§4 below).

2. **W2 — The anonymity representation and the deduplication step are mutually inconsistent, and it is the anonymity claim that is most likely overstated.** §3.1 reports removing 5 duplicate entries; §3.3 states that "no identifying information was collected, and responses could not be linked back to individual students." Detecting a duplicate requires something persistent — IP address, session or survey token, cookie, SSO handle, device fingerprint — and every one of those is identifying or quasi-identifying under most institutional data-governance regimes. *Why it matters:* this is not, in my judgement, misconduct; it reads as imprecise reporting. But an ethics committee reviewing the *as-executed* protocol would want to know whether students were shown a consent notice describing the collection accurately, and a reader cannot currently tell. *Fix:* state the actual deduplication mechanism, and replace the blanket "anonymous" with the accurate term — most likely "de-identified" or "pseudonymous at collection, anonymised before analysis." **Overlap flag for the synthesizer:** this same passage sits in Reviewer 1's remit as a sample-integrity question (how were duplicates identified, and were the 5 truly duplicates). I am reporting only the data-governance and consent-accuracy half; it should be consolidated into one finding, not counted twice.

3. **W3 — The recruitment channel is a selection mechanism on both variables, and §6 treats it as a generalisability problem only.** Distribution ran through "the institution's course-announcement channel" (§3.1) — a channel located inside or immediately adjacent to the platform under study. §6 frames the consequence as overrepresentation of students who engage with institutional channels. *Why it matters:* that framing describes who is in the sample. The sharper problem is that the recruitment mechanism plausibly conditions on both the predictor and the outcome simultaneously, so the effect on the estimate is not a simple, safely-attenuating range restriction — it is a design-specific confound whose direction is not obvious. *Fix:* name the channel's relationship to the LMS explicitly (is the announcement channel part of the LMS?), and move this from the generalisability paragraph to a sentence about the estimate itself. If the institution can supply an aggregate, log-derived activity distribution for the full undergraduate population, comparing it against the sample's self-reported distribution would bound the bias without any individual-level linkage — a cheap analysis that needs no new consent.

4. **W4 — The practice implication is not decision-actionable, and it addresses the wrong actor.** §5 suggests LMS onboarding that helps students see concrete usefulness "may be worth institutional attention." As someone who would receive this recommendation: it does not specify which students, at what point in the term, with what content, at what cost, or measured against what outcome — and it could have been written without collecting these data. *Why it matters more than the usual "implications are generic" complaint:* the paper's own literature review (Ibarra & Poll, 2021) identifies course design, instructor expectations, and assessment structure as shaping both perception and use. That points the lever at instructors and curriculum committees. §5 then points it at students. Instructors, LMS support staff, students with constrained connectivity or device access, and disability services appear nowhere in this manuscript. *Fix:* either drop the implication to a single sentence in Future Directions, or ground it — the honest actionable version is "at this institution, X% of respondents reported using the LMS rarely or never; that tail, not the average, is where an onboarding intervention would have to work," which requires only the descriptive statistic the paper already has and does not report (W5).

5. **W5 — "Engagement" is doing work the measure cannot support, and the distribution an institution would act on is missing.** The abstract's closing sentence, §4, and §5 use "engagement" for what is one five-point item about access frequency in a typical week. In learning analytics, engagement denotes depth, quality, and pattern of interaction; access frequency is one weak indicator of it. Separately, the outcome is reported only as a median category — no distribution, no dispersion, no floor/ceiling assessment. *Why it matters:* the substitution quietly upgrades the finding in the one place most readers stop (the abstract), and the missing distribution removes the single number an institutional decision-maker actually needs. *Fix:* use "self-reported access frequency" wherever the measure is meant, reserving "engagement" for the construct being gestured at; and add a small table with the full frequency distribution of both measures.

### Detailed Comments

#### Assumption Audit

- **Explicit assumptions.** The paper's stated assumptions are modest and largely met: that the association is worth documenting descriptively, that a validated PU instrument transfers to this sample, that correlational language is the appropriate register. I have no quarrel with these as stated. The one explicit commitment that is not honoured throughout is §2's declaration that the study will "situate it against prior findings" — §5 asserts consistency with prior work without stating what prior work found. (Reviewer 2 owns the literature side of this; I note it only because §2 makes it a promise.)

- **Implicit assumptions.** Four, in descending order of consequence. *(a) More LMS use is desirable.* No learning outcome appears anywhere in this manuscript. The onboarding recommendation therefore rests on an unstated warrant that increased platform access is a good in itself. The descriptive conclusion in §7 survives without this premise; §5's recommendation does not. *(b) LMS use at this institution is discretionary enough to vary with perception.* The paper never states whether assessments, submissions, or attendance run through the LMS. This is the interpretive hinge for my field: in a mandatory-submission regime a large share of access frequency is structurally determined by course policy, and r = .42 means something entirely different than it would in a discretionary regime. A reader cannot currently tell which world they are in. *(c) Access frequency represents engagement* (see W5). *(d) Self-report error is unbiased noise.* The paper's treatment implies self-report merely adds attenuating error; the divergence literature it cites does not support the assumption that the error is uncorrelated with the predictor.

- **Paradigmatic assumptions.** This is a between-person, single-timepoint, variable-centred design applied to a behaviour that is, in log data, strongly time-structured and bursty — activity clusters around assessment deadlines and drops between them. Asking about "a typical week" flattens a temporally patterned behaviour into something resembling a stable disposition. I raise this not as a flaw to correct within this study but as a boundary the paper could state: the design measures a person's summary belief about a term-long pattern, which is a different object from the pattern.

#### Cross-Disciplinary Connections

- **Parallel research.** The learning-analytics tradition has asked closely adjacent questions with log-derived measures rather than survey measures, and has repeatedly found that course-level instructional conditions moderate the relationships in question strongly enough that pooled single-level estimates mislead. That literature is the natural comparison set for this paper's own §2 caution about context, and it is currently absent.

- **Borrowing opportunities.** Two concepts would materially strengthen the manuscript at low cost. First, *criterion validation*: a consent-linked sub-sample (even n ≈ 40) whose self-reported frequency is correlated with their own log-derived access count would let the authors report the self-report/log agreement in *their* setting instead of citing someone else's. That single addition converts the paper's largest limitation into its most transferable contribution and is exactly the kind of result other institutions would cite. Second, *common-method variance*: since both variables were collected from the same respondent, on one instrument, at one sitting, the organisational-research toolkit (marker variables, temporal separation) applies directly and is nowhere mentioned in the manuscript.

- **Methodological borrowing.** Beyond the above: (i) short experience-sampling or a one-week diary would reduce recall bias on the use item at modest burden; (ii) if course enrolment is recoverable in aggregate, a course-level nesting structure would let the authors separate instructor-driven from perception-driven variance — which is the analysis their own §2 argument implies; (iii) an aggregate, non-linked comparison of the sample's reported use distribution against the institution's population-level activity distribution would bound the recruitment-channel bias (W3) without any new consent burden.

#### Practical Impact

- **Real-world application.** As written, an institutional-research office cannot act on this paper. It learns that perception and reported use covary moderately at one campus — which most practitioners already hold as working knowledge — but not how many students are in the disengaged tail, who they are, or whether the association differs where LMS use is mandatory. The paper's honesty about being "incremental" is accurate; my concern is that the incremental value could be raised substantially by reporting statistics the authors already possess.

- **Implementation feasibility.** Institutions already run LMS onboarding. The recommendation in §5 therefore lands not as "do this" but as "do the thing you already do, somewhat differently," with no specification of the difference. Cost, timing, target population, and success measure are all unspecified. There is also an unintended consequence worth naming: recommendations framed around raising *use* invite institutions to adopt platform-activity metrics as engagement proxies, which rewards performative access and penalises students whose connectivity or device access constrains their session patterns.

- **Stakeholders.** Missing entirely: instructors and course designers (the actors whose assessment structure drives the behaviour the paper measures, per the paper's own literature); LMS support and administration staff; students in the low-use tail, who are the notional intervention target and are invisible in a median-only report; students with accessibility requirements or constrained connectivity. The 214 respondents are treated as one undifferentiated population beyond "spanned all four year levels."

#### Broader Implications

- **Ethical dimensions.** Two points, pulling in opposite directions, and both belong in the paper. First, the anonymity/deduplication inconsistency (W2) means the manuscript's account of its own data handling is not currently accurate, which matters independently of whether the underlying conduct was sound. Second — and I want to state this plainly because my discipline's reflex is to demand log data — choosing self-report *because* log linkage raises consent, re-identification, and secondary-use problems is a legitimate and arguably better-governed choice. The defect is not that the authors surveyed students; it is that they left the reader unable to distinguish a principled choice from an unexamined one.

- **Social impact.** See the metric-proxy risk above. Additionally, a finding framed around perception as the lever locates the problem in students' beliefs rather than in course design or platform usability, which is a quietly consequential attribution for a paper that will be read by people who allocate institutional effort.

- **Future directions.** In priority order from my seat: (1) the consent-linked log-validation sub-study; (2) multilevel course-nested analysis separating instructor-driven from perception-driven variance; (3) reporting and characterising the low-use tail rather than the central tendency; (4) the multi-institution replication the authors already propose — which becomes far more valuable once (1) establishes how much of the estimate is measurement.

### Cross-Disciplinary Reading Recommendations

- **Podsakoff, MacKenzie, Lee, & Podsakoff (2003), *Journal of Applied Psychology* 88(5), 879–903 — "Common method biases in behavioral research."** The canonical treatment of exactly this design's exposure: two constructs, one respondent, one instrument, one sitting. Directly supports the §3.4 or §6 addition I request.
- **Gašević, Dawson, Rogers, & Gašević (2016), *The Internet and Higher Education* 28, 68–84 — "Learning analytics should not promote one size fits all: The effects of instructional conditions in predicting academic success."** Empirically grounds the authors' own §2 caution about context, and is the strongest available argument for the course-nested analysis I suggest.
- **Slade & Prinsloo (2013), *American Behavioral Scientist* 57(10), 1510–1529 — "Learning Analytics: Ethical Issues and Dilemmas."** The framework I would use to write the missing §3.2 rationale for choosing self-report over logs, and to reason about the consent status of any linked sub-sample.
- **Macfadyen & Dawson (2010), *Computers & Education* 54(2), 588–599 — "Mining LMS data to develop an 'early warning system' for educators."** An early, concrete demonstration of what log-derived LMS activity measures look like and what they support; useful as the contrast case for what this study's criterion is not.
- **Junco (2013), *Computers in Human Behavior* 29(3) — comparing actual and self-reported measures of platform use.** A directly comparable self-report-versus-log discrepancy study outside the LMS context; supports quantifying rather than merely conceding the divergence. *[UNVERIFIED — I am confident of author, year, and journal; verify pagination before citing.]*

I have deliberately not recommended the technology-acceptance primary literature; that is Reviewer 2's territory and my seat adds nothing there.

### Questions for Authors

1. Why was the criterion measured by self-report when the institution holds server-side access logs for every respondent? If the reason was ethical or governance-related, please state it in §3.2 — it would strengthen the paper.
2. Is LMS use at your institution required for assessment submission, attendance, or grade access? Your reader cannot currently tell whether the reported frequency is largely policy-determined, and the interpretation of r = .42 turns on this.
3. What persistent field or mechanism identified the 5 duplicate submissions, and how does that square with §3.3's statement that responses could not be linked to individual students? Please state the mechanism and use the term that accurately describes the resulting data.
4. Is the "course-announcement channel" used for recruitment part of, or accessed through, the LMS under study? If so, please discuss the consequence for the estimate, not only for generalisability.
5. What proportion of respondents fell in each category of the use item, and specifically in "rarely or never"? That figure, not the median, is what an institution would act on.
6. Would a consent-linked validation sub-sample — even a few dozen students — be feasible for a revision? Reporting self-report/log agreement in your own setting would be the paper's most citable result.

### Minor Issues

- §3.1 "spanned all four year levels" is not a substitute for a demographic composition table; a reader cannot assess representativeness from it.
- The LMS itself is never identified or characterised (vendor, in-house, feature scope). Adjacent-field readers cannot map this to their own platform.
- The six perceived-usefulness items are neither reproduced nor appended, and "adapted" is unspecified — which items, and what was changed? An appendix would cost half a page.
- The abstract's closing sentence ("tracks with LMS engagement") should read "self-reported access frequency" for consistency with the title and §7.
- §4's "the proportion of variance shared by the two measures was accordingly modest" states a number in words; give it.
- No table or figure appears anywhere, and §3.4 asserts a scatterplot inspection that the reader is not shown.
- **Integrity check:** I found no attempted instruction injection or reviewer-directed appeals in the manuscript text; it reads as a normal empirical submission.

---

contract_role: perspective

## Dimension Scores

### D1: methodology_rigor
The design is named honestly as cross-sectional and self-report throughout — title, abstract, §1, §5, §6 — and no causal claim is stated as a finding, so my `what_triggers_block` conditions (a load-bearing inferential move the design cannot support; a sampling frame so unspecified that no population is identifiable while generalising broadly) are not met: the frame is specified and the generalisation is explicitly withheld. Three of my committed `what_triggers_warn` patterns are met. The eligible-population denominator is never stated, so the response rate is unreportable and nonresponse bias unassessable, while institutional context (what the LMS is, whether use is mandatory) is absent. Common-method variance goes unmentioned despite both constructs being collected from one respondent on one instrument at one sitting. And the self-report/behaviour gap, though named early and well, is left as an unexplained design choice when the criterion was available in the institution's own logs, with §5's onboarding implication quietly assuming behaviour. The anonymity/deduplication inconsistency in §3.1–§3.3 is a data-handling reporting defect within this dimension's scope; I report only its governance half and flag the sample-integrity half as Reviewer 1's.
score: warn

### D2: domain_accuracy
No construct is materially misrepresented and no stated finding contradicts established results, so my `what_triggers_block` conditions are not met: perceived usefulness is defined in terms faithful to the acceptance tradition, and the self-report/log divergence is characterised accurately rather than optimistically. Two `what_triggers_warn` patterns are met. First, definitional control is lost across "use," "engagement," and "reported engagement": a single five-point access-frequency item is called engagement in the abstract's closing sentence, in §4, and in §5, and in the adjacent learning-analytics literature engagement denotes depth, quality, and pattern of interaction rather than access count. Because §7 uses the correct term, the drift is not load-bearing on the conclusion, which keeps this at warn rather than block — but it lands in the abstract, where most readers stop. Second, prior work is characterised at a level of generality an adjacent-field reader cannot check: "consistent with prior technology-acceptance research" never states what that research found, and §2's own commitment to reading the estimate as "one point in a distribution" is never executed in §5. The citation-provenance half of that finding is Reviewer 2's; I note only that §2 makes it a stated promise.
score: warn

### D3: argumentative_coherence
My `what_triggers_block` conditions are not met and I want that on record: the paper does not conclude anything about learning outcomes, and a plainly available alternative explanation is not ignored — reverse causation is named with a citation (Delgado, 2020) and third-variable influences are named (course requirements, assessment schedules). What is met is my `what_triggers_warn` pattern almost exactly. The premise that more LMS use is desirable is never stated or warranted anywhere; no learning outcome appears in the manuscript at all. §7's descriptive conclusion survives without that premise, but §5's practice recommendation does not — and that recommendation is offered as a hedged suggestion rather than a finding, which is the warn condition rather than the block condition. Two further premises go unexamined: that LMS use at this institution is discretionary enough to vary with perception (never established; if submissions run through the platform, much of the frequency is policy-determined), and that self-report error is unbiased noise rather than correlated with the predictor. Student heterogeneity is unaddressed beyond year level, though the conclusion does not depend on homogeneity. Separately, §5's recommendation addresses students while the paper's own cited mechanism locates the lever with instructors and course design.
score: warn

### D4: cross_disciplinary_relevance
I examined all three of my `what_triggers_block` conditions and none is met. The onboarding implication is an applied claim reaching past the data, but it carries an explicit hedge ("suggested by, not proven by"), and my committed trigger required the absence of a hedge. The manuscript is thin on institutional context but not interpretively closed — an adjacent-field reader can determine what was measured and on whom. And no borrowed interdisciplinary claim is left unsubstantiated while carrying the argument; the one borrowed finding, Vasquez (2020) on self-report/log divergence, is used correctly as a caution. Four `what_triggers_warn` patterns are met. Institutional context is thin enough that transferability must be inferred: the LMS is never identified, and whether its use is mandatory is never stated. Instructors, support staff, students with accessibility or connectivity constraints, and the low-use tail are absent from the discussion. The practice implication is generic enough to have been written without the data. And the strongest observation available from my seat is a warn-level design gap rather than an overclaim: the behavioural criterion was in the institution's own database, the manuscript cites the literature establishing why that matters, concedes the point, and proceeds without stating a reason — leaving the reader unable to distinguish a principled governance choice from an unexamined one.
score: warn

### D5: writing_and_structure
This is the manuscript's strongest dimension and the warn is narrow. My `what_triggers_block` conditions are not met: nothing interpretively essential has been compressed away — sample, setting, instrument source, analysis approach, and a substantive limitations section are all present — and the abstract's claim strength matches the body on every material axis (it states the coefficient, the design, the single site, and the non-causal reading). The single abstract-level slip is the word "engagement," which I have scored under D2 rather than treating as a materially stronger claim here. Two `what_triggers_warn` patterns are met. The six perceived-usefulness items are neither reproduced nor appended, and "adapted from Costa and Wren (2019)" leaves the actual instrument unrecoverable — an adjacent-field reader cannot see what "usefulness" meant to respondents. And the reporting apparatus is under-built relative to the claims: there is no table or figure anywhere, §3.4 asserts a scatterplot inspection the reader is never shown, and the outcome variable is reported only as a median category with no distribution or dispersion — withholding the one figure (the size of the low-use tail) that an institutional reader would need. Both are cheaply fixable with one appendix and one table.
score: warn

## Failure Condition Checks

### F1
Predicate: any mandatory dimension scores 'block'. The mandatory dimensions are D1 (methodology_rigor), D2 (domain_accuracy), and D3 (argumentative_coherence). My scores are warn, warn, and warn respectively. No mandatory dimension scores block. In each case I checked my Phase 1 block triggers explicitly and found them unmet: the paper states no causal finding, specifies its sampling frame, withholds broad generalisation, misrepresents no construct on which its conclusion depends, and does not argue as if alternative explanations were unavailable.
fired: false

### F2
Predicate: two or more mandatory dimensions score 'warn' or worse. D1 = warn, D2 = warn, D3 = warn. Three mandatory dimensions score warn, exceeding the threshold of two.
fired: true

### F3
Predicate: any high-priority dimension scores 'block'. The single high-priority dimension is D4 (cross_disciplinary_relevance), which I scored warn. I evaluated all three of my committed D4 block triggers against the manuscript and none was met — the applied claim is hedged, the framing is thin but not interpretively closed, and no unsubstantiated borrowed claim carries the argument.
fired: false

### F0
Predicate: every mandatory dimension scores 'pass'. D1, D2, and D3 all score warn; none scores pass.
fired: false

## Review Body

From the learning-analytics and institutional-research seat, this manuscript presents an unusual review problem: its rhetoric is more disciplined than most published work in its genre, and a reviewer who tests only for overclaiming will return an undeservedly favourable verdict. My position is that correctly naming a limitation discloses it but does not cure it — and that the distinction matters most where the limitation was avoidable. That is the case here. LMS use was measured by asking students at an institution that holds a complete server-side access record for every respondent. The paper cites the literature establishing that self-report and logs diverge substantially, concedes the point twice, and proceeds without a stated rationale. There are good rationales available, including the ethical one — log linkage raises consent, re-identification, and secondary-use problems that a survey avoids — and I would credit that answer if the authors gave it. The defect is the silence, which leaves a reader unable to tell a principled choice from an unexamined one, and which permits the possibility that r = .42 estimates an association between a perception and a second perception rather than between perception and behaviour.

Three further observations are proper to this seat. The anonymity representation in §3.3 cannot coexist as written with the deduplication in §3.1; deduplication requires a persistent quasi-identifier, so the accurate term is de-identified or pseudonymous rather than anonymous. I read this as reporting imprecision, not misconduct, and it should be consolidated with Reviewer 1's sample-integrity framing of the same passage rather than counted twice. Recruitment through the institution's course-announcement channel — a channel plausibly inside the platform under study — conditions on both variables at once and is treated in §6 as a generalisability matter only. And the practice implication addresses students' perceptions while the paper's own cited mechanism (course design, instructor expectations, assessment structure) locates the lever with instructors, who appear nowhere else in the manuscript.

What the paper does well is real and should be credited in the decision letter: the construct is named honestly in the title, the divergence literature shapes the framing rather than decorating the limitations, and the alternative causal reading is supplied without prompting. Every defect I have identified is curable within this design, most of them cheaply — a rationale paragraph, an accurate data-handling description, a distribution table, and a decision on whether the finding is about perception or behaviour, applied consistently through §5.

## Editorial Decision

Derived mechanically from the contract's `failure_conditions` precedence applied to my own dimension scores. F2 fired at severity 70; F1 (severity 90), F3 (severity 60), and F0 (severity 10) did not fire. The highest-severity fired condition is F2, whose action governs.

editorial_decision=major_revision

---

## SEAT — Devil’s Advocate

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** The contract asks whether the study's design, data handling, statistical reporting, and reproducibility affordances clear the field's peer-review bar. Read adversarially, this is not a checklist of whether methods are *described* but whether the described methods can actually bear the inferential weight the paper will place on them. For a cross-sectional survey of undergraduates, my adversarial reading is that the burden falls on the author to show that sampling, instrumentation, and analysis were fixed in advance and reported completely enough that a hostile reader could reconstruct what was done and predict what would happen on replication. My job here is not to redesign the study (that is R1's territory) but to ask whether a methodological weakness is load-bearing for the conclusions — i.e., whether a rival methodological account explains the results at least as well as the authors' account. Note the field-norm gate (Dimension 9): a cross-sectional survey in educational technology is not obligated to meet an experimental or preregistration standard from a different subfield; if I want to escalate on "the field should do X", I must name the field's actual accepted-practice boundary from a checkable source, or down-rate to advisory.

**D2 — domain_accuracy (mandatory).** The contract asks whether claims align with current domain evidence, whether prior work is represented correctly, and whether domain terminology and results are used without factual error. My adversarial reading converts this into a cherry-picking and misrepresentation audit rather than a coverage audit — coverage completeness belongs to R2. LMS adoption is a field with a dense, well-known, and *contested* theoretical lineage (perceived usefulness is a named construct with an established measurement tradition and an equally established critique). The specific vulnerability I will hunt is a paper that borrows a construct's authority — its name, its instrument, its citation trail — while quietly dropping the conditions under which that construct was validated, or that cites the supporting half of a literature whose contradicting half is equally prominent and equally old. Misrepresenting what a cited source actually established is a domain-accuracy failure even when the citation exists and is correctly formatted.

**D3 — argumentative_coherence (mandatory).** The contract asks whether the core thesis is internally consistent, whether evidence supports the claims, and whether any fallacy undermines the central argument. This is the dimension that sits closest to my seat, and I will apply the strictest standard here. The structural risk in this paper class is well-known and severe: a cross-sectional design can only license associational claims, but the topic ("usefulness → use") is causally framed in ordinary language, and the discussion/implications sections of such papers routinely drift into causal or directional wording that the design cannot support. A second structural risk is common-method variance — perceived usefulness and self-reported use are both self-reported, plausibly in the same instrument at the same moment, so a single shared source of variance (self-presentation, general attitude toward the platform, acquiescence) is a rival explanation for any observed association that is at least as parsimonious as the authors' theory. My job is to build that rival account in its strongest form and test whether the paper's argument survives it.

**D4 — cross_disciplinary_relevance (high).** The contract asks whether framing, definitions, and implications are accessible to adjacent-field readers and whether interdisciplinary claims are substantiated. Adversarially, I read the second clause as the operative one: unsubstantiated interdisciplinary borrowing is a defect, whereas mere insularity is a presentation issue. The characteristic failure in this literature is importing a psychological or economic construct and treating its theoretical baggage as established fact for the education context — or conversely, generalizing an institution-specific, platform-specific, undergraduate-specific finding into a claim about "learners" or "technology adoption" writ large. Overgeneralization is the form D4 failure takes in my seat. Because D4 is high-priority rather than mandatory, a `block` here still fires a failure condition (F3) but does not implicate F1/F2 — I will keep that asymmetry in mind so that I neither inflate a framing complaint into a block nor let a genuinely unsupported cross-field claim slide because the dimension is "only" high-priority.

**D5 — writing_and_structure (normal).** The contract asks about organisation, clarity of exposition, figure/table quality, and adherence to venue conventions. This is the dimension where my seat is at greatest risk of doing the wrong job — style complaints are not my mandate, and no failure condition in this contract references normal-priority dimensions at all, so nothing I score here can move the editorial decision by itself. I will therefore treat D5 adversarially only where structure is *epistemically* load-bearing: where the organisation of the manuscript conceals a logical gap, where a table or figure is presented in a way that makes an unsupported reading the natural one, or where the abstract states more than the body delivers. At 1,597 words the manuscript is short for an empirical report, which raises a specific structural question — whether brevity has been achieved by omitting reportable content that a reader needs in order to evaluate the claims — but shortness is not itself a defect and I will not treat it as one. The Surface-Form Parity gate applies with unusual force here: I must not credit polished prose as evidence, nor down-rate a substantive gap because it is clearly and confidently written.

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for` — Whether the sampling frame, recruitment route, and response/completion rate are stated, and whether the achieved sample is characterized well enough to know who is missing; whether the instrument is identified (adapted from an existing scale vs. author-written), whether items are reproduced or referenced, and whether reliability/validity evidence is reported for *this* sample rather than only cited from the source scale; whether the outcome "self-reported use" is operationalized concretely (recall window, response scale, anchoring) or left as an unspecified self-rating; whether the analysis reported matches the analysis the design permits, and whether all analyses run are reported or only the surviving ones; whether N, effect sizes, and uncertainty (CIs or SEs) accompany any test statistics; whether ethics/consent handling is stated; whether reproducibility affordances normal for survey work in this field — instrument availability, item wording, analysis specification — are present at the level the field actually expects.
- `what_triggers_block` — Evidence that a methodological choice is load-bearing for the paper's headline claim *and* that a rival methodological account explains the result at least as well as the authors' account. Concretely: the analysis reported cannot support the inference the paper draws from it (e.g., an association statistic used to license a directional or magnitude claim about behaviour); or the sample is so unspecified or so evidently self-selected that "who answered" is a more parsimonious explanation of the headline result than the proposed construct relationship; or the primary outcome is undefined to the point that the reader cannot tell what was measured, making the central finding unevaluable; or reported numbers are mutually inconsistent (N, df, percentages, or subgroup counts that do not reconcile) such that at least one reported quantity must be wrong. Any of these is a Foundation Collapse or Data-Conclusion Mismatch in the sense of my CRITICAL criteria.
- `what_triggers_warn` — Evidence of a real methodological gap that weakens but does not dismantle the central claim, and that substantial revision could repair: reliability reported only by citation to the source instrument and not for this sample; response rate absent or uninterpretable but the sample otherwise characterized; recall window or use-measure anchoring left vague while the construct is still identifiable; no uncertainty estimates alongside point estimates; ethics/consent unstated; instrument not reproduced but adequately referenced. Also `warn` where I judge a reproducibility affordance missing but cannot ground the field's actual boundary from a checkable source — in that case the finding is reported with `[FIELD-NORM UNVERIFIED]` and cannot carry `block` on the strength of the norm alone.

### D2: domain_accuracy
- `what_to_look_for` — Whether "perceived usefulness" is used with the definition and measurement conditions of the tradition the paper invokes, or whether the label is borrowed while the construct is redefined mid-paper; whether cited sources are represented as having established what the paper says they established (attribution drift: a correlational source cited for a causal claim, a single-institution study cited as a general finding, a theoretical paper cited as empirical evidence); whether the citation set is directionally lopsided — supporting findings cited while equally prominent null, contradicting, or boundary-condition findings from the same period are absent; whether known and long-standing critiques of the invoked adoption framework are engaged or silently omitted; whether domain terminology (adoption, engagement, use, usage intention, actual use) is used consistently rather than swapped mid-argument to license a stronger reading; whether any claim about "current" domain evidence is anchored in the literature or asserted.
- `what_triggers_block` — A core domain claim on which the paper's contribution rests is demonstrably misrepresented or contradicted by the source it rests on: a cited work is characterized as showing something it does not show and the paper's argument depends on that characterization; or the paper's central construct is used in a sense incompatible with the tradition whose instrument, citations, or authority it borrows, such that the reported result does not measure what the paper claims to have measured; or contradicting domain evidence is prominent, contemporaneous, and directly on-point, its omission is not incidental, and engaging it would reverse the paper's stated conclusion (Stronger Counter-Narrative). Terminological slippage triggers `block` only where the slippage is what carries the argument — i.e., where the conclusion holds under one sense of the term and the evidence supports only the other.
- `what_triggers_warn` — Selective but non-decisive citation: supporting-only citation patterns where the contradicting literature would qualify rather than reverse the conclusion; a construct definition that is loose or drifts in emphasis without becoming incompatible with the invoked tradition; known critiques of the adoption framework unaddressed where addressing them would bound the claim rather than defeat it; individual attribution imprecision that does not carry the central argument; terminology used inconsistently in ways that muddy rather than mislead. Also `warn` where I suspect misrepresentation but the paper's own text is ambiguous enough that the substantive claim cannot be stably judged — per the parity gate, I mark it ambiguous rather than resolving it against the author on stylistic grounds.

### D3: argumentative_coherence
- `what_to_look_for` — The exact modal strength of every claim about the usefulness→use relationship, tracked across abstract, results, discussion, and implications, watching for strengthening as the paper moves away from the data (association in Results becoming influence/driver/leads-to in Discussion, becoming a recommendation premised on causation in Implications); whether the paper acknowledges that both variables are self-reported and confronts common-method variance as a rival account, or leaves it unmentioned; whether reverse causation (students who use the platform more come to perceive it as more useful) is acknowledged, given that a cross-sectional design cannot distinguish the two directions; whether third-variable accounts (course requirements mandating LMS use, instructor practice, assessment design, general conscientiousness, prior digital competence) are considered, since institutionally-compelled use would make the observed association partly artefactual; whether stated hypotheses match what was tested and what is discussed; whether internal contradictions exist between sections, between abstract and body, or between a stated limitation and a conclusion that ignores it; whether limitations are stated and then operationally overridden — a design caveat acknowledged in one paragraph and violated in the next is worse than one never raised, because it establishes the author knew.
- `what_triggers_block` — The main conclusion does not follow from the evidence presented, even taking the evidence at face value (Logic Chain Break): a causal, directional, or intervention-licensing claim drawn from cross-sectional associational data without the design support such a claim requires, where that claim is the paper's stated contribution; or the data as presented contradict the stated conclusion (Data-Conclusion Mismatch — a conclusion of "significant"/"strong" relationship that the reported figures do not sustain); or a rival account — common-method variance, reverse causation, or compelled institutional use — is more parsimonious and fits the presented data at least as well as the authors' explanation, and the paper neither addresses nor can address it within its design (Stronger Counter-Narrative); or the paper states a limitation that logically forecloses its own conclusion and then draws that conclusion anyway. I will apply the opposite-style counterfactual before committing any of these: if the same substantive gap were written in more polished or more casual prose, my verdict must not move.
- `what_triggers_warn` — Directional or causal language present but confined to non-load-bearing passages (a stray verb in the discussion) while the paper's actual stated claim remains associational; rival explanations acknowledged but treated too briefly to be taken seriously, without the conclusion depending on their dismissal; hypotheses and analyses aligned in substance but stated imprecisely; a limitations section that names the design constraint but under-weights it in the implications, where trimming the implications would repair the argument; unstated but recoverable assumptions in the reasoning chain that a revision could make explicit without changing the result.

### D4: cross_disciplinary_relevance
- `what_to_look_for` — Whether the population, platform, institution, and time window of the study are stated with enough specificity that a reader in an adjacent field knows what the finding is *about*, and whether conclusions stay inside that boundary or expand to "students", "learners", "users", or "technology adoption" in general; whether constructs imported from psychology, information systems, or economics arrive with their scope conditions intact or are asserted as settled for the education context; whether definitions of platform-specific or field-specific terms (LMS, engagement, adoption) are given at first use rather than assumed; whether any interdisciplinary claim — that this result speaks to motivation theory, to human-computer interaction, to organizational technology acceptance — is substantiated by evidence in the paper or merely gestured at; whether stated implications for practice or policy are scoped to institutions resembling the study site.
- `what_triggers_block` — An interdisciplinary or generalized claim is central to the paper's stated contribution and is unsupported by its evidence: the conclusion is stated at a population or domain scope the single-site, single-platform, single-timepoint undergraduate sample cannot license, and the paper's claimed contribution *is* that broader claim (Overgeneralization rising to Foundation Collapse); or a construct is imported from another discipline with its validity conditions stripped, and the cross-field authority thereby borrowed is what makes the paper's argument work. I record here that under this contract a D4 `block` fires F3 (severity 60, `major_revision`) and does not by itself reach F1 — I will not inflate a scope complaint to reach a harsher decision, and I will not deflate a genuine unsupported cross-field claim because the dimension is non-mandatory.
- `what_triggers_warn` — Implications stated more broadly than the sample warrants but peripheral to the contribution, repairable by rescoping the discussion; field-specific terms left undefined such that an adjacent-field reader must infer them, without the ambiguity changing what is claimed; imported constructs used appropriately but without their scope conditions made explicit; interdisciplinary relevance asserted in framing (introduction or conclusion) without evidentiary follow-through, where deleting the assertion would cost the paper nothing.

### D5: writing_and_structure
- `what_to_look_for` — Whether the abstract's claims match what the body delivers, since abstract inflation is a structural defect with epistemic consequences; whether the organisation makes a logical gap harder to see — results presented so that an unsupported reading is the natural one, a rival explanation buried where it will not be weighed, a limitation placed after the conclusion it should have constrained; whether tables and figures are self-interpretable and whether their captions state interpretations that the underlying numbers do not support; whether numbers reported in prose match numbers in tables; whether the manuscript's brevity at ~1,597 words corresponds to omitted reportable content (method detail, item wording, uncertainty estimates, limitations) rather than to efficient writing; whether venue conventions for an empirical report — identifiable IMRaD structure, adequate methods reporting — are met. I will not report style, tone, or prose-quality complaints: they are outside my mandate, and no failure condition in this contract references D5.
- `what_triggers_block` — Reserved for the case where presentation is not merely poor but actively misleading: a figure, table, or caption asserts a relationship the underlying reported data do not show; or prose and table report mutually contradictory values for the same quantity; or the abstract states a finding the body does not contain or contradicts. A `block` here fires no failure condition in this contract (D5 is normal-priority and F1/F2 are mandatory-only, F3 high-only), so I will assign it only on this evidentiary standard and will not use it as a backdoor to signal displeasure that belongs in another dimension. If the same defect is really an argument defect, it scores in D3, not here.
- `what_triggers_warn` — Organisation that obscures the argument without misrepresenting it (findings stated before the method that produced them, limitations detached from the conclusions they bear on); tables or figures under-labelled or missing N/units so that a reader must reconstruct them; methods reporting compressed below what evaluation of the claims requires, where the missing content is recoverable by revision; abstract emphasis skewed relative to the body without containing a false statement; internal cross-reference or numbering inconsistencies that impede reading. I will not score `warn` for informal, plain, or unpolished prose alone — per the parity gate, wording style is not a defect unless it changes the truth conditions of a claim or makes the claim unevaluable.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Devil's Advocate Review

### Strongest Counter-Argument

Credit where it is due: the arithmetic is right. The 95% CI [.30, .52] reproduces exactly from r = .42 at n = 214 under Fisher transformation, and the ">.80 power to detect r ≥ .19 at α = .05 two-tailed" figure is correct. The paper reports uncertainty, a robustness coefficient, and its design constraints without being asked to.

Now the refutation. Suppose I hold that this study establishes nothing about perceived usefulness and LMS use. My case needs one move. Everything measured here is a perception, elicited from one respondent, in one instrument, at one sitting: a six-item agreement scale about usefulness, and a one-item self-estimate of frequency. A single general disposition toward the platform — favourability, acquiescence, self-presentation to one's own institution — produces r = .42 across those two blocks with no substantive relation between perceived usefulness and any behaviour whatsoever. The design collected no marker variable, no temporal separation, and no behavioural criterion, so nothing in the manuscript discriminates that account from the authors'. Add two accounts the paper itself names and then abandons: reverse direction (§5, via Delgado) and course-level compulsion (§4, "course requirements and assessment schedules"). Four candidate explanations, one correlation, zero discriminating evidence.

The authors' answer is that they never claimed otherwise. But they do, in the one sentence a reader would act on: §5 offers "modest support for the intuition that LMS onboarding which helps students see concrete usefulness … may be worth institutional attention." Two sentences earlier they state the reverse pathway is "equally consistent with the data." If that is true, the correlation's likelihood ratio between the onboarding hypothesis and its reverse is exactly one, and the support claimed is not modest — it is nil. The hedge does not repair this. It names the constraint and then spends it.

### Issue List

#### CRITICAL

| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|----------|---------------------|-----------------------------|
| C1 | 4 (Logic Chain) | The paper states a limitation that logically forecloses its own practice claim, then makes the claim. §5 asserts the reverse pathway is "equally consistent with the data," which sets the correlation's discriminating power between the forward and reverse directions at zero. The same paragraph then offers the correlation as "modest support for the intuition that LMS onboarding which helps students see concrete usefulness … may be worth institutional attention." An intervention recommendation requires the forward direction; the authors have just conceded they cannot have it. The qualifier "suggested by, not proven by" misdescribes the situation: it converts *no* directional evidence into *weak* directional evidence. This is the only claim in §5 that is not already assumed by the paper's own framing (§1: institutions invest "on the assumption that availability translates into use"), and it is the one claim the design cannot support at all. | §5, sentences 2–4; carried into Abstract ("We discuss implications for LMS onboarding") | *(severity does not rest on a field norm — internal logical contradiction)* | *(n/a)* |

#### MAJOR

| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|----------|---------------------|-----------------------------|
| M1 | 1 (Core Thesis) | Common-method variance is never mentioned anywhere in the manuscript. Both variables are same-source, same-instrument, same-moment self-reports; a single general-favourability or acquiescence factor accounts for r = .42 with no substantive perception–behaviour link. No marker variable, no temporal separation, no behavioural criterion was collected, so the account cannot be discriminated within this design. The paper's causal caveat is thorough while its method-variance caveat is absent — the unhedged rival account is the one that operates independently of the cross-sectional design. | §3.2, §3.4; absent from §6 | *(internal — rival account fits presented data)* | *(n/a)* |
| M2 | 4 (Logic Chain) | The third-variable account is named and then dropped. §4 states reported engagement "reflects many influences beyond perceived usefulness, including course requirements and assessment schedules." Course-level LMS intensity is a common cause of both variables and fits the data exactly as well as PU→use with no additional machinery. Neither course-requirement intensity nor instructor practice was measured, so the account cannot be bounded. | §4, final sentence; §2 (Ibarra & Poll context caution) | *(internal — rival account fits presented data)* | *(n/a)* |
| M3 | 2 (Cherry-Picking) | The comparative claim is unfalsifiable and load-bearing. "Consistent with prior technology-acceptance research" appears in the Abstract, §5, and §7, and no prior numeric estimate appears anywhere in the paper. §2 states the correct frame explicitly — Song (2018), multi-campus, "any single-site estimate is best read as one point in a distribution" — and §5 never cites Song, never states the distribution, and never places r = .42 or its CI against any benchmark. The paper sets its own interpretive standard and then does not meet it; as written, "consistent with" is compatible with almost any value. | §2 ¶2 vs. §5 ¶1, §7; Abstract | *(internal — the paper's own §2 standard)* | *(n/a)* |
| M4 | 2/3 (Cherry-Picking, Confirmation Bias) | Cautions are cited as inoculation, not as constraints. Each caution is named once in §2, where naming costs nothing, and none modifies a downstream claim: Vasquez's self-report/log divergence does not stop the Abstract and §5 from saying "engagement"; Song's distribution frame is never executed (M3); Ibarra & Poll's context caution is re-cited in §5 as *corroboration* for consistency rather than as the caution §2 introduced. The pattern is systematic across all four cited cautions and is checkable sentence by sentence. | §2 ¶2 vs. §4, §5, §6 | *(internal — traceable citation-use mapping)* | *(n/a)* |
| M5 | 1 (Logical Consistency) | Two Methods statements cannot both be literally true. §3.1 removes "5 duplicate entries"; §3.3 states "No identifying information was collected, and responses could not be linked back to individual students." Identifying repeat submissions requires some persistent per-respondent signal. One of the two statements is inaccurate as written, which leaves an exclusion rule the reader cannot audit and an anonymity representation that does not describe the executed protocol. Reported as a reporting-accuracy defect, not an allegation of misconduct. | §3.1 vs. §3.3 | *(internal contradiction)* | *(n/a)* |
| M6 | 4 (Hidden Assumptions) | The stated warrant for the primary parametric estimate is an assertion the paper does not exhibit. §3.4 reports that "scatterplot inspection showed an approximately linear, monotonic association with no extreme bivariate outliers, and both distributions were approximately symmetric." There is no figure, no skewness or kurtosis value, and no distribution for the outcome. Evidence offered as the justification for an analytic choice, but never shown, cannot be checked by any reader. | §3.4 | *(internal — asserted-but-unexhibited warrant)* | *(n/a)* |
| M7 | 4 (Hidden Assumptions) | The paper applies its own reliability standard to one measure and not the other. Cronbach's α = .88 is reported for the six-item predictor; no reliability estimate of any kind is reported for the single-item criterion, and attenuation is never acknowledged. Note the direction honestly: criterion unreliability biases r toward zero, so r = .42 is a floor for the perception–perception association, not an inflated figure. The defect is that the reader cannot bound the floor. | §3.2, §3.4 | APA JARS-Quant survey/quantitative reporting standards require psychometric/reliability evidence for **each** measure used, not a subset | The paper demonstrates it holds this standard (α reported for the predictor) and then omits the criterion entirely; the omission is not a subfield-specific reporting luxury but an asymmetry against the paper's own applied standard |
| M8 | 5 (Overgeneralization) | The estimand, not merely generalizability, is compromised. The frame is "all enrolled undergraduates," but the eligible N is never stated, so the response rate and the magnitude of nonresponse are unreportable. Recruitment ran through "the institution's course-announcement channel" — a channel located in or adjacent to the platform under study — so the sample is conditioned on the dependent variable. The reported r therefore estimates an association within an unspecified restricted-range subpopulation, not the population association. Direction of bias is indeterminate (classic range restriction attenuates; selection on a common effect can run either way), and I decline to claim inflation. §6 treats this purely as a generalizability caveat ("results may not generalize"), which understates it. | §3.1; §6 items 1 and 4 | AAPOR *Standard Definitions* and APA JARS-Quant both require reporting the sampling frame and a computable response/participation rate for survey studies | The denominator exists and is knowable to the authors by their own frame definition ("all enrolled undergraduates"); withholding it makes nonresponse magnitude unassessable, which is not a demand imported from a different subfield |
| M9 | 5 (Overgeneralization) | "Engagement" is never defined and is used interchangeably with a single self-reported weekly-access-frequency item. The word appears in the Abstract ("LMS engagement"), §1, §2, and §5 ("factors bearing on engagement"). §2's own Vasquez citation forecloses that equation by establishing that self-report captures perceived rather than actual engagement. The swap is not cosmetic: it is what makes the Abstract's closing sentence and §5's implication read as institutionally consequential. The Abstract's closing sentence also crosses population scope, generalizing to "undergraduates" without the single-site qualifier the rest of the paper maintains. | Abstract final sentence; §1 ¶1; §2 ¶1; §5 ¶2 | *(internal — contradicted by the paper's own §2)* | *(n/a)* |
| M10 | 4 (Hidden Assumptions) | The outcome scale is not fully reported. Only anchors 1 ("rarely or never") and 5 ("several times daily") are given; categories 2–4 are never labelled. The reported median category, "a few times per week," is not one of the two disclosed anchors, so its position on the scale is unknown. A reader therefore cannot locate the median, cannot assess floor or ceiling compression on a five-point frequency item, and cannot check the symmetry claim in §3.4 (M6). | §3.2, §4 ¶1 | *(internal — reported statistic not mappable to reported scale)* | *(n/a)* |

#### MINOR

| # | Dimension | Issue Description | Location |
|---|-----------|-------------------|----------|
| m1 | 4 | r² is never reported. §4 substitutes "The proportion of variance shared by the two measures was accordingly modest" for a value (.18) that is derivable from the reported r and that the sentence is describing. |
| m2 | 5 | Sample characterization is limited to "spanned all four year levels" — no year-level counts, no demographics — so the composition of the achieved sample cannot be inspected even qualitatively against the frame. |
| m3 | 2 | The §2 definition of perceived usefulness ("the degree to which a person believes a technology will help them perform better") is essentially the canonical formulation of the acceptance tradition but is attributed only to 2019/2020 sources. Flagged as unresolved, not asserted: the manuscript alone does not let me determine whether the cited instrument-development paper originated that wording. |
| m4 | 4 | Whitfield (2019) is a practitioner account and carries the only external support attached to the onboarding implication. Its placement in the sentence lets it read as corroborating an intervention effect, which a practitioner account cannot do. |

### Ignored Alternative Explanations/Paths

1. **A single method factor, not two constructs.** One general disposition toward the LMS (favourability / acquiescence / institutional self-presentation) generates r = .42 across a usefulness block and a frequency self-estimate collected in the same instrument. This is at least as parsimonious as the authors' reading — it posits one latent quantity where they posit two plus a relation — and fits the presented data identically. It is never mentioned.
2. **Course-level LMS intensity as common cause.** Students in courses that route materials and assessment through the platform both use it more and find it more useful. The paper names this in §4, measures none of it, and never treats it as a competitor to its own interpretation.
3. **Reverse direction as the primary account, not a co-equal.** §5 grants reverse causation parity and then proceeds as if the forward direction were the working hypothesis. Habitual use rationalized as usefulness is a well-formed alternative that would leave the correlation intact and reverse the practice implication (build the requirement, and perceived usefulness follows).
4. **Selection on the dependent variable.** Recruiting through the platform's own announcement channel means the sample is drawn from students already accessing the platform. The estimand becomes the association within a truncated slice of the use distribution, an alternative the paper does not consider at all — it converts this into a generalizability sentence.
5. **A path not taken rather than a limitation imposed.** The criterion could have been institutional access logs, which every LMS produces for every respondent. The paper cites Vasquez (2020) on self-report/log divergence, concedes the point in §6, and proceeds. Whether that was necessary or convenient is never addressed, and the manuscript's uniformly apologetic framing flattens the distinction.

### Missing Stakeholder Perspectives

- Instructors and course designers, whose deployment decisions set the compelled-use baseline both variables sit on top of.
- Non-respondents and low-use students — structurally absent from a sample recruited through the platform, yet they are exactly the population the onboarding recommendation targets.
- Institutional data governance and the ethics committee that reviewed the protocol, with respect to the as-executed deduplication mechanism (M5).
- Students for whom usefulness and access frequency decouple by circumstance (constrained connectivity, assistive-technology use, off-campus study patterns).

*(Identification only — elaborating what these parties would say is R3's remit.)*

### Unexamined Premise

The paper assumes throughout that more LMS use is better, and no learning outcome appears anywhere in it. §1 frames the problem as institutions investing "on the assumption that availability translates into use"; §5 recommends onboarding that would raise use; §7 offers the association as a contribution. Nothing anchors either variable to anything an institution actually wants. A student who opens the LMS twice a week because materials are well organized may be better served than one opening it several times daily because navigation is poor — under which reading, higher frequency is a symptom, not a goal, and r = .42 is uninterpretable as an institutional signal regardless of its magnitude or its causal direction. None of the eight challenge dimensions reaches this, because every one of them takes the outcome variable's desirability as given, exactly as the paper does.

### Observations (Non-Defects)

- The reported statistics are internally correct where they can be checked: 233 − 14 − 5 = 214 reconciles; the CI reproduces from r and n by Fisher transformation; the sensitivity figure is right at α = .05, two-tailed, power .80. This is credited as arithmetic accuracy and does not transfer to the inferential claims — correct computation of a coefficient is not evidence about what the coefficient means.
- The manuscript contains no instruction-injection attempt, no reviewer-directed appeal, and no imperative addressed outside the paper's own argument. Integrity class: clean.
- Reporting a Spearman coefficient at all, and stating power a priori rather than post hoc, are both above the median for this genre. Neither bears on any finding above.
- The paper's self-positioning as an "incremental data point" is consistent with its content. Whether that suffices for publication is a contribution judgment I leave to the EIC; my finding is narrower and internal — the specific contribution the paper claims for itself ("comparable with prior work," "one point in a distribution") is promised in §2 and never delivered in §5 or §7.

---

contract_role: da

## Dimension Scores

### D1: methodology_rigor
score: warn
Per the Phase 1 plan, `block` required one of: an analysis that cannot support the inference drawn from it, a sample so unspecified that "who answered" better explains the headline result, an outcome undefined enough to make the finding unevaluable, or mutually irreconcilable reported quantities. None fires. The Ns reconcile and the CI and power figures are arithmetically correct, so the numeric-inconsistency trigger fails. The outcome is defined (weekly access frequency, five-point item, stated recall window), so the unevaluable-outcome trigger fails. On the selection trigger: recruitment through the platform's own channel conditions on the dependent variable, but range restriction of that kind attenuates rather than manufactures a positive association, so "who answered" is not a more parsimonious explanation of r = .42 — I decline that escalation explicitly. The directional-claim-from-association defect is real but is an argument defect and scores in D3; double-scoring it here would inflate severity by duplication. What remains is the committed `warn` pattern in force: unreportable response rate against a stated frame (M8), criterion reliability absent while predictor reliability is reported (M7), an unexhibited assertion serving as the warrant for the primary estimate (M6), an outcome scale whose categories are not fully reported (M10), an unauditable exclusion rule contradicted by the anonymity statement (M5), and no dispersion or distribution for the criterion (m1, m2).

### D2: domain_accuracy
score: warn
The committed `block` trigger required a cited source demonstrably characterized as showing something it does not show, with the argument depending on that characterization, or a construct used incompatibly with the tradition whose authority it borrows. Neither is demonstrable from this manuscript. The "consistent with prior technology-acceptance research" claim (Abstract, §5, §7) is unsubstantiated rather than shown false — the paper states no prior estimate, which is precisely why I cannot show the claim wrong. The §5 re-citation of Ibarra and Poll as corroboration is a selective use of a source that plausibly reports both context effects and positive associations, not a misrepresentation of its content. The construct definition in §2 is the tradition's own, whatever its attribution. That places the findings squarely in the committed `warn` band: a comparative claim that is unfalsifiable as written while doing load-bearing work in three locations (M3), a systematic pattern where every cited caution is named once and constrains nothing downstream (M4), and unresolved provenance for the central construct's definition (m3).

### D3: argumentative_coherence
score: block
Two committed `block` triggers fire independently. First: "the paper states a limitation that logically forecloses its own conclusion and then draws that conclusion anyway." §5 declares the reverse pathway "equally consistent with the data" and then offers the same correlation as "modest support" for an onboarding recommendation that requires the forward pathway. Under the authors' own symmetry statement the correlation's likelihood ratio between the two directions is one, so the support is not modest but absent, and "suggested by, not proven by" misstates zero evidence as weak evidence (C1). Second: Stronger Counter-Narrative — common-method variance (M1) and course-level compulsion (M2) each fit the presented data at least as well as the authors' reading, neither is addressed (CMV is not mentioned at all), and neither can be addressed within a design that collected no marker variable, no temporal separation, and no behavioural criterion. The internal contradiction between §3.1 and §3.3 (M5) corroborates on the consistency axis. Parity gate applied: I rewrote C1's target passage mentally in both a blunter and a more heavily hedged register; the verdict does not move, because no amount of hedging can manufacture directional evidence and no bluntness would remove it if present. The defect is in the inference, not the prose.

### D4: cross_disciplinary_relevance
score: warn
I considered `block` and decline it on merit. The committed `block` trigger required that a generalized or cross-field claim be central to the stated contribution and unsupported, or that an imported construct's stripped validity conditions be what makes the argument work. The undefined "engagement" construct (M9) and the Abstract's unqualified "among undergraduates" are genuine defects, and the swap is what lends the Abstract's closing sentence and §5's implication their institutional weight. But the measured result does not depend on the borrowed construct — the association between two named self-report measures stands or falls without the word "engagement" — and the repair is a consistent rescoping and a definition at first use, changing no reported quantity. That is the committed `warn` pattern verbatim: implications broader than the sample warrants but repairable by rescoping, and field-specific terms left undefined. I note for the record that escalating here would fire F3 (severity 60), which is already subsumed by the F1 the D3 block fires, so nothing in my decision depends on this call — which is why I have judged it on merit rather than effect.

### D5: writing_and_structure
score: warn
The committed `block` standard was reserved for actively misleading presentation: a figure or caption asserting an unshown relationship, prose contradicting a table, or an Abstract stating a finding the body does not contain. The Abstract's "LMS engagement" is an overstatement the body's own §2 forecloses, but by my own Phase 1 discipline that is an argument and scope defect and scores in D3/D4, not here. Nothing presented contradicts the underlying numbers; where the numbers are checkable they are right. `warn` stands on reporting compressed below what evaluating the claims requires: no figure despite an asserted scatterplot inspection (M6), no table anywhere, no distribution or dispersion for the criterion, an incompletely labelled outcome scale (M10), and a substantive quantity replaced by an adjective (m1). Recorded per the parity gate: the manuscript's prose is clear and well organized, and I have not credited that as evidence for any claim, nor down-rated any substantive gap because it is confidently written.

## Failure Condition Checks

### F1
fired: true
Predicate: any mandatory dimension scores `block`. D3 (argumentative_coherence, mandatory) scores `block`. Severity 90. Action (contract): reject_or_major_revision. Evaluated against my own dimension scores only; the `any` quantifier is panel-level machinery for the synthesizer.

### F2
fired: true
Predicate: two or more mandatory dimensions score `warn` or worse. D1 `warn`, D2 `warn`, D3 `block` — three of three mandatory dimensions qualify. Severity 70. Action (contract): major_revision. Subsumed by F1 under precedence. The `majority` quantifier is the synthesizer's to apply, not mine.

### F3
fired: false
Predicate: any high-priority dimension scores `block`. D4 (cross_disciplinary_relevance) is the sole high-priority dimension and scores `warn`, not `block`. See the D4 note on why I declined the escalation on merit rather than on its (nil) effect on my decision.

### F0
fired: false
Predicate: every mandatory dimension scores `pass`. None of D1, D2, D3 scores `pass`.

## Review Body

No `## Scoring Plan Dissent` is filed. Every score above follows a trigger I committed to before seeing the manuscript, and in the two places where the paper-visible evidence invited a harsher call than my plan authorized — the selection-mechanism trigger under D1 and the imported-construct trigger under D4 — the plan held me back and I have said so on the record rather than escalating silently.

The manuscript is an unusual review object, and the temptation it presents runs in the opposite direction from the usual one. It does not over-claim in the ordinary way. It refuses causal verbs, reports a confidence interval, runs an ordinal robustness check, states sensitivity a priori, names four limitations, and describes itself as incremental. A panel that pattern-matches on "does this paper over-claim?" returns a favourable review here. So the operative question is not whether the paper is honest about its limits — it is — but whether correctly naming a limitation resolves it. My answer is: naming a limitation discloses it, and in exactly one place in this manuscript the naming is worse than silence would have been, because it establishes that the authors knew.

That place is §5. The paragraph grants that reverse causation is "equally consistent with the data," which is a precise and correct statement, and then, two sentences later, offers the correlation as "modest support" for an onboarding intervention. Those two sentences cannot both stand. If the forward and reverse readings are equally consistent with the data, then the data are uninformative about which one holds, and an intervention premised on the forward reading receives no evidential support from them — not weak support, none. The qualifier "suggested by, not proven by" is doing something specific and wrong: it grants the claim a nonzero evidential footing that the authors' own symmetry statement has already set to zero. That is a logic chain break under my Phase 1 D3 trigger, and it is the paper's stated practical contribution. I applied the opposite-style counterfactual before committing: rewritten bluntly ("our correlation supports changing onboarding"), I would flag it identically; rewritten with three more hedges, the flaw would remain, because hedging cannot manufacture direction. The verdict does not key off prose form.

Behind that single break sit two rival accounts the paper cannot exclude and, in one case, does not mention. Common-method variance appears nowhere in the manuscript. Both variables are perceptions elicited from one respondent in one instrument at one sitting; a single disposition toward the platform produces r = .42 with no substantive perception–behaviour relation at all. That account posits one latent quantity where the authors posit two and a relation between them, and it fits the presented data identically. No marker variable, no temporal separation, and no behavioural criterion were collected, so the design cannot discriminate. Course-level compulsion is the second: §4 names "course requirements and assessment schedules" as influences on reported use, and the paper then measures none of them and never treats course-level LMS intensity as a common cause of both variables. With reverse causation, that makes four candidate explanations for one coefficient and no evidence that separates any of them. The paper's careful causal hedging is aimed at the third of these and silent on the first.

The pattern generalizes, and it is the most checkable finding in this report. Every caution the paper cites is named once, in §2, where naming costs nothing, and none of them constrains a downstream claim. Vasquez's self-report/log divergence is cited and then the Abstract and §5 keep saying "engagement." Song's "one point in a distribution" is cited as the correct interpretive frame and then §5 asserts consistency with prior research without citing Song, without stating any prior estimate, and without placing r = .42 or its interval against any benchmark — an unfalsifiable comparative claim carrying weight in the Abstract, the Discussion, and the Conclusion. Ibarra and Poll's context caution is inverted in §5 into a corroborating citation for consistency. Read as a set, the citations of caution function as inoculation against the objections rather than as constraints on the conclusions. That is a confirmation-bias signature that does not depend on tone: it is a sentence-level map of which cited constraints have downstream consequences, and the answer is none of them.

The methodological findings are separately real and mostly repairable. The response rate is unreportable against a frame the paper itself defines as all enrolled undergraduates, and recruitment through the platform's own announcement channel conditions the sample on the dependent variable — which makes the reported coefficient an estimate within an unspecified restricted slice of the use distribution, not an estimate of the population association. I state the direction of that bias as indeterminate rather than claiming inflation: classic range restriction attenuates, and selection on a common effect can run either way. §6 handles this as generalizability alone, which is the wrong category. Criterion reliability is absent entirely while predictor α is reported, an asymmetry against the paper's own applied standard; here too the direction is honest — attenuation makes r = .42 a floor, and the defect is that the floor cannot be bounded. The warrant for choosing Pearson as the primary estimate is an inspection the paper asserts and does not exhibit, and the outcome scale's middle categories are never labelled, so the reported median cannot even be located on it. And §3.1's removal of five duplicates cannot be squared with §3.3's statement that no identifying information was collected and responses could not be linked to individuals; one of the two is inaccurate as written, which leaves an exclusion rule no reader can audit. I record that as a reporting-accuracy defect and explicitly not as an allegation about the conduct of the study.

Two things I am not doing. I am not judging whether a single bivariate correlation from one institution clears a publication bar — that is the EIC's call, and my adjacent finding is narrower and internal: the contribution the paper claims for itself in §2, comparability against a distribution of prior estimates, is promised and never delivered in §5 or §7. And I am not treating the manuscript's brevity or its plain prose as defects. Where I could check the arithmetic, it is correct, and the manuscript contains no attempt to address or instruct its reviewers.

Finally, the premise none of my eight dimensions reached. The paper assumes more LMS use is better and contains no learning outcome of any kind. Both of its variables float free of anything an institution wants: a student opening the platform twice a week because the materials are well organized may be better served than one opening it several times daily because navigation is poor. If that is right, then r = .42 is uninterpretable as an institutional signal whatever its magnitude and whatever its causal direction — and the study's whole practical frame rests on a desirability assumption it never states, let alone defends.

By the contract's precedence rule, F1 at severity 90 is the highest-severity condition fired against my own scores and governs the action below.

## Editorial Decision

editorial_decision=reject_or_major_revision

# PART 3 — EDITORIAL SYNTHESIS

# Editorial Synthesis — Sprint Contract (v3.6.2) + Editorial Decision Package

---

# Part 0: Sprint-Contract Mechanical Synthesis

**Contract**: `reviewer/reviewer_full/v1` · `baseline_version` v3.6.2 · `mode` reviewer_full · `stage` reviewer_full_review · `panel_size` N = 5 · `generated_at` 2026-07-25T08:00:00Z
**Panel cardinality**: 5 usable Phase 2 outputs received (EIC, methodology, domain, perspective, da) = `panel_size`. Invariant satisfied; no `[PANEL-SHRUNK]`.
**Dissents filed**: none. R1 and DA each explicitly record "no dissent filed"; no `## Scoring Plan Dissent` section appears in any card. Multi-dissent rule not engaged.

## Step 1 — Scoring matrix

Dimensions resolved by `id`. Values from each reviewer's `## Dimension Scores`.

| Dimension | Priority | EIC | R1 (methodology) | R2 (domain) | R3 (perspective) | DA |
|---|---|---|---|---|---|---|
| D1 methodology_rigor | mandatory | warn | warn | warn | warn | warn |
| D2 domain_accuracy | mandatory | warn | warn | warn | warn | warn |
| D3 argumentative_coherence | mandatory | warn | warn | warn | warn | **block** |
| D4 cross_disciplinary_relevance | high | warn | warn | warn | warn | warn |
| D5 writing_and_structure | normal | warn | warn | warn | warn | warn |

Distinct values present across the matrix: 24 × `warn`, 1 × `block`, 0 × `pass`.

## Step 2 — Failure-condition evaluation

### F1 — severity 90 · quantifier `any`
`expression`: *any mandatory dimension scores 'block'* → §9 recognised pattern 1 (priority-scoped single-match, bare `mandatory`). Mandatory set = {D1, D2, D3}.

| Reviewer | D1 | D2 | D3 | predicate |
|---|---|---|---|---|
| EIC | warn | warn | warn | false |
| R1 | warn | warn | warn | false |
| R2 | warn | warn | warn | false |
| R3 | warn | warn | warn | false |
| DA | warn | warn | block | **true** |

`any` → threshold ≥ 1 of 5; predicate holds for 1. **fired: true**

### F2 — severity 70 · quantifier `majority`
`expression`: *two or more mandatory dimensions score 'warn' or worse* → §9 pattern 2 (priority-scoped count-based; ordering `pass` < `warn` < `block`).

| Reviewer | mandatory dims at warn-or-worse | predicate (≥ 2) |
|---|---|---|
| EIC | 3 (D1, D2, D3) | true |
| R1 | 3 (D1, D2, D3) | true |
| R2 | 3 (D1, D2, D3) | true |
| R3 | 3 (D1, D2, D3) | true |
| DA | 3 (D1 warn, D2 warn, D3 block) | true |

`majority`, N = 5 → threshold ⌊5/2⌋ + 1 = 3; predicate holds for 5. **fired: true**

### F3 — severity 60 · quantifier `any`
`expression`: *any high-priority dimension scores 'block'* → §9 pattern 1 (`high-priority` variant). High-priority set = {D4}.

D4 = warn for all five reviewers; predicate holds for 0. `any` → threshold ≥ 1 of 5, unmet. **fired: false**

### F0 — severity 10 · quantifier `all`
`expression`: *every mandatory dimension scores 'pass'* → §9 pattern 3 (universal over priority).

No reviewer scores any mandatory dimension `pass`; predicate holds for 0. `all` → requires 5 of 5. **fired: false**

## Step 3 — Precedence and decision

Fired set = {F1 (severity 90), F2 (severity 70)}. Highest severity = F1; no tie, so ordinal tiebreak is not engaged. F1's `action` governs verbatim.

fired_conditions: [F1, F2]

editorial_decision=reject_or_major_revision

**Note on F1's two-branch action.** `reject_or_major_revision` is a disjunctive action string; selecting the branch is the editorial judgement the action itself delegates, not a softening of it (the forbidden-operations list bars softening a fired action, not resolving a disjunction the action states). The branch selection and its basis are recorded in the Decision Rationale below. No score was averaged, vote-aggregated, or re-interpreted; the single `block` that fired F1 was not voted down by the four `warn` scores, exactly as the `any` quantifier prescribes.

---

# Part 1: Editorial Decision Letter

## Manuscript Information

- **Title**: *[not supplied to the synthesizer; reviewer cards reference a title containing "…Self-Reported Use…" and "Cross-Sectional Survey"]*
- **Manuscript ID**: *[not supplied]*
- **Journal**: *Journal of Computing in Higher Education*
- **Decision Date**: 2026-07-25
- **Review Round**: 1
- **Panel**: 5 reviewers (Editor-in-Chief, Reviewer 1 Methodology, Reviewer 2 Domain, Reviewer 3 Perspective, Devil's Advocate)

## Review Panel Provenance (#540)

`[PROVENANCE-STAMP-ABSENT]` — the dispatching layer supplied no #540 provenance stamp with the five Phase 2 outputs. Per the never-inferred rule, the synthesizer does not select among the three permitted statements and asserts no claim about model independence across the five seats. **The dispatching layer must fill this block from its provenance stamp before this letter ships to the author.**

---

Dear Author(s),

Thank you for submitting your manuscript to the *Journal of Computing in Higher Education*. It has been read by five independent reviewers, including the Editor-in-Chief, under a pre-registered acceptance contract in which each reviewer committed to their scoring triggers before seeing your paper.

## Decision: **Major Revision**

*(Branch selection within the fired condition's action `reject_or_major_revision`; see Decision Rationale. The rejection branch remains live under one recorded contingency, stated below.)*

## Top Blocking Issues (3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| 1 | The §5 practice recommendation is not licensed by the design. It moves from the *perceived* use you measured to *behaviour* you did not, and it sits two sentences after your own statement that the reverse pathway is "equally consistent with the data." This is the panel's only `block`-level scoring, and it is what fired the highest-severity contract condition. | EIC, R1, R2, R3, **DA (CRITICAL)** | §5: "modest support for the intuition that LMS onboarding which helps students see concrete usefulness … may be worth institutional attention", set against §5's "equally consistent with the data" | **R1** |
| 2 | The comparison your own §2 sets as the correct interpretive frame ("one point in a distribution", citing Song 2018) is never performed, while "consistent with prior technology-acceptance research" is asserted in the Abstract, §5 and §7 with no prior numeric estimate anywhere in the manuscript. As written the claim cannot be evaluated, and your six-item reference list contains no source that would let a reader check it. | EIC, R2, R3, DA | Abstract; §5 "consistent with prior technology-acceptance research (Costa & Wren, 2019; Ibarra & Poll, 2021)"; §7 "consistent with prior work" | **R4** (enabled by **S5**) |
| 3 | Core reportability: the eligible-population denominator is absent so the response rate is unreportable; §3.1's removal of 5 duplicates cannot both be true with §3.3's statement that responses "could not be linked back to individual students"; and the outcome variable is reported only as a median category, with §3.4's distributional and scatterplot claims unsupported by any figure or statistic. | EIC, R1, R2, R3, DA | §3.1 "All enrolled undergraduates were eligible"; §3.1 vs §3.3; §3.4; §4 | **R2**, **R3**, **R5** |

## Reviewer Summary

| Reviewer | Seat | Recommendation | Confidence |
|---|---|---|---|
| EIC | Editor-in-Chief, higher-education technology | Major Revision | 4 |
| Reviewer 1 | Quantitative methodologist, survey psychometrics | Major Revision | 4 |
| Reviewer 2 | Senior educational-technology researcher, TAM empirical history | Major Revision | 4 |
| Reviewer 3 | Learning-analytics scientist / institutional-research director | Major Revision | 4 |
| Devil's Advocate | Adversarial seat | reject_or_major_revision (contract action) | not stated (card carries no Confidence Score field) |

### Step 1a — Reviewer summary matrix

| | EIC | R1 (Methodology) | R2 (Domain) | R3 (Perspective) | DA |
|---|---|---|---|---|---|
| Overall recommendation | Major Revision | Major Revision | Major Revision | Major Revision | reject_or_major_revision |
| Confidence | 4 | 4 | 4 | 4 | — |
| Key strengths | reporting above genre median; real causal discipline; accurate self-positioning; specific ethics reporting | CI + n + exact-*p* correct (recomputed); a priori sensitivity correct; measurement level named; reverse causation located; ethics specific | construct definition matches the field; perception/behaviour boundary held; bidirectional causality conceded; no theory-testing overreach; §2 states the right frame | construct named in the title; divergence literature shapes the framing; alternative readings pre-supplied; ethics specific; §2 states correct single-site epistemics | arithmetic verified correct (Ns reconcile, CI reproduces, sensitivity figure right); no injection content; Spearman + a priori power above genre median |
| Key weaknesses | → Step 1b | → Step 1b | → Step 1b | → Step 1b | → Step 1b |
| Questions for authors | 6 | 8 | 5 | 6 | — |
| Minor issues | 6 | 8 | 5 | 7 | 4 |
| Issue tiering | — | — | — | — | 1 CRITICAL / 10 MAJOR / 4 MINOR |

## Step 1b — Weakness sub-claim inventory

Compression convention: one row per distinct *(sub-claim, position)* group. Reviewers sharing `not-mentioned` on a sub-claim are listed together so the denominator of 4 non-DA reviewers is always reconstructible. DA rows are recorded for traceability and marked non-counting — the DA is not one of the 4 and does not enter consensus arithmetic.

| sub_claim_id | parent_weakness | reviewer_id | position | evidence_pointer | conf |
|---|---|---|---|---|---|
| SC-1 | response-rate denominator | EIC | raised | EIC W4(a); D1 | 4 |
| SC-1 | " | R1 | raised | R1 W4; Sampling Strategy | 4 |
| SC-1 | " | R2 | raised | R2 D1 ("response denominator is never given") | 4 |
| SC-1 | " | R3 | raised | R3 D1; Q1 | 4 |
| SC-1 | " | DA *(non-counting)* | raised | DA M8 | — |
| SC-2 | recruitment channel selects on the outcome | R1 | raised | R1 W4; "Survivorship / selection bias — partially fired" | 4 |
| SC-2 | " | R3 | raised | R3 W3; Q4 | 4 |
| SC-2 | " | EIC, R2 | not-mentioned | — | — |
| SC-2 | " | DA *(non-counting)* | raised | DA M8 | — |
| SC-3 | dedup vs anonymity (consolidated per R1 + R3 request) | EIC | raised | EIC W4(d); Q2 | 4 |
| SC-3 | " | R1 | raised | R1 W5 (flags overlap for consolidation) | 4 |
| SC-3 | " | R3 | raised | R3 W2 (flags overlap for consolidation) | 4 |
| SC-3 | " | R2 | not-mentioned | — | — |
| SC-3 | " | DA *(non-counting)* | raised | DA M5 | — |
| SC-4 | criterion reliability absent; attenuation unbounded | EIC | raised | EIC Review Body; D1 | 4 |
| SC-4 | " | R1 | raised | R1 W1; Q6 | 4 |
| SC-4 | " | R2, R3 | not-mentioned | — | — |
| SC-4 | " | DA *(non-counting)* | raised | DA M7 | — |
| SC-5 | Pearson-as-primary contradicts §3.2's ordinal declaration | EIC | corroborated | EIC Confidence Score note (flags, defers adjudication to R1) | 4 |
| SC-5 | " | R1 | raised | R1 W2 | 4 |
| SC-5 | " | R2, R3 | not-mentioned | — | — |
| SC-6 | §3.4 assumption / scatterplot claims unevidenced | EIC | raised | EIC W4(c); Minor 1 | 4 |
| SC-6 | " | R1 | raised | R1 W3; Analysis Methods | 4 |
| SC-6 | " | R3 | raised | R3 Minor; D5 | 4 |
| SC-6 | " | R2 | not-mentioned | — | — |
| SC-6 | " | DA *(non-counting)* | raised | DA M6 | — |
| SC-7 | outcome distribution / dispersion unreported | EIC | raised | EIC Minor 1 (ceiling at "several times daily") | 4 |
| SC-7 | " | R1 | raised | R1 W3; Q4 | 4 |
| SC-7 | " | R3 | raised | R3 W5; Q5 | 4 |
| SC-7 | " | R2 | not-mentioned | — | — |
| SC-7 | " | DA *(non-counting)* | raised | DA D1; M10 | — |
| SC-8 | instrument not reproducible (anchors 2–4; six PU items) | R1 | raised | R1 W3; Reproducibility | 4 |
| SC-8 | " | R3 | raised | R3 Minor 3; D5 | 4 |
| SC-8 | " | EIC, R2 | not-mentioned | — | — |
| SC-8 | " | DA *(non-counting)* | raised | DA M10 | — |
| SC-9 | *r*² given as prose, not as .18 | EIC | raised | EIC W4(b); Minor 2 | 4 |
| SC-9 | " | R1 | raised | R1 Results Presentation | 4 |
| SC-9 | " | R2 | raised | R2 Minor 3 | 4 |
| SC-9 | " | R3 | raised | R3 Minor 5 | 4 |
| SC-9 | " | DA *(non-counting)* | raised | DA m1 | — |
| SC-10 | §2's promised benchmarking never performed | EIC | raised | EIC W1; Structural Coherence | 4 |
| SC-10 | " | R2 | raised | R2 W1; Q1 | 4 |
| SC-10 | " | R3 | raised | R3 Assumption Audit → explicit assumptions | 4 |
| SC-10 | " | R1 | not-mentioned | — | — |
| SC-10 | " | DA *(non-counting)* | raised | DA M3 | — |
| SC-11 | "consistent with prior TA research" unanchored (Abstract, §5, §7) | EIC | raised | EIC W2 | 4 |
| SC-11 | " | R2 | raised | R2 W1; Q2 | 4 |
| SC-11 | " | R3 | raised | R3 D2 | 4 |
| SC-11 | " | R1 | not-mentioned | — | — |
| SC-11 | " | DA *(non-counting)* | raised | DA M3, M4 | — |
| SC-12 | no primary construct source, no synthesis anchor | EIC | raised | EIC W3 | 4 |
| SC-12 | " | R2 | raised | R2 W2; Missing Key References | 4 |
| SC-12 | " | R1, R3 | not-mentioned | — (R3 explicitly defers to R2) | — |
| SC-12 | " | DA *(non-counting)* | raised (unresolved) | DA m3 | — |
| SC-13 | six references share a sequential DOI block across six publishers | EIC | raised | EIC W3 "Additionally, and separately"; Q5; D2 conditional | 4 |
| SC-13 | " | R1, R2, R3 | not-mentioned | — | — |
| SC-14 | §5 implication substitutes behaviour for measured perception | EIC | raised | EIC W5 | 4 |
| SC-14 | " | R1 | raised | R1 "Scope drift in the claim"; D3 | 4 |
| SC-14 | " | R2 | raised | R2 W3; Q4 | 4 |
| SC-14 | " | R3 | raised | R3 D1 ("§5's onboarding implication quietly assuming behaviour") | 4 |
| SC-14 | " | DA *(non-counting)* | raised | DA C1 | — |
| SC-15 | **[DA-CRITICAL]** §5's claim is logically foreclosed by the same paragraph's "equally consistent" concession | DA *(non-counting)* | raised | DA C1; D3 block | — |
| SC-15 | " | EIC, R2 | disputed *(mechanism only; non-counting sub-claim)* | EIC W5 "The hedge covers the causal problem and misses the construct switch"; R2 W3 "correctly disclaims *causality* but does not disclaim the *construct substitution*" | 4 |
| SC-15 | " | R1 | disputed *(mechanism only)* | R1 fallacy checklist: "Reverse causation — checked and **not fired**" | 4 |
| SC-16 | common-method variance unaddressed | EIC | raised | EIC D1 ("common-method constraints go unmentioned in §6") | 4 |
| SC-16 | " | R1 | raised | R1 Research Design; D1; Q7 | 4 |
| SC-16 | " | R3 | raised | R3 D1; Borrowing opportunities | 4 |
| SC-16 | " | **R2** | **disputed** | R2 D1: "common-method concerns … are acknowledged (§2, §6), which keeps this at warn rather than block" | 4 |
| SC-16 | " | DA *(non-counting)* | raised | DA M1 | — |
| SC-17 | server-side logs available; self-report choice unexplained | EIC | raised | EIC Originality; Q3 | 4 |
| SC-17 | " | R3 | raised | R3 W1; Q1, Q6 | 4 |
| SC-17 | " | R1, R2 | not-mentioned | — | — |
| SC-17 | " | DA *(non-counting)* | raised | DA Ignored Alternative 5 | — |
| SC-18 | LMS unnamed; mandatory-vs-optional use unstated | EIC | raised | EIC Minor 3; D4 | 4 |
| SC-18 | " | R1 | raised | R1 D4 | 4 |
| SC-18 | " | R3 | raised | R3 Minor 2; Assumption Audit (b); Q2 | 4 |
| SC-18 | " | R2 | not-mentioned | — | — |
| SC-18 | " | DA *(non-counting)* | raised | DA M2 | — |
| SC-19 | abstract's closing sentence over-generalises (drops single-site bound and "self-reported") | EIC | raised | EIC Title & Abstract | 4 |
| SC-19 | " | R1 | raised | R1 "Scope drift"; D3 | 4 |
| SC-19 | " | R3 | raised | R3 Minor 4 | 4 |
| SC-19 | " | **R2** | **disputed** | R2 Argument logic: "the abstract does not strengthen the body's claims"; D5: "the abstract does not overstate the body" | 4 |
| SC-19 | " | DA *(non-counting)* | raised | DA M9 | — |
| SC-20 | "engagement" used as an undefined near-synonym for access frequency | R1 | raised | R1 D5 | 4 |
| SC-20 | " | R2 | raised | R2 D4 | 4 |
| SC-20 | " | R3 | raised | R3 W5; D2 | 4 |
| SC-20 | " | EIC | not-mentioned | — | — |
| SC-20 | " | DA *(non-counting)* | raised | DA M9 | — |
| SC-21 | confounding named in §4, absent from §6, unmeasured | R1 | raised | R1 "Endogeneity / omitted variables — partially fired" | 4 |
| SC-21 | " | R3 | corroborated | R3 Assumption Audit (b); Methodological borrowing (ii) | 4 |
| SC-21 | " | EIC, R2 | not-mentioned | — | — |
| SC-21 | " | DA *(non-counting)* | raised | DA M2 | — |
| SC-22 | instrument adaptation undocumented; no validity evidence for adapted form | R1 | raised | R1 Data Collection; Q5 | 4 |
| SC-22 | " | R2 | raised | R2 W5; Q3 | 4 |
| SC-22 | " | R3 | raised | R3 Minor 3 | 4 |
| SC-22 | " | EIC | not-mentioned | — | — |
| SC-23 | stated contribution is a reporting property, not a knowledge contribution | EIC | raised | EIC W1; Originality; Significance; Q6 | 4 |
| SC-23 | " | R2 | raised | R2 W4; Q5 | 4 |
| SC-23 | " | R3 | corroborated | R3 Practical Impact | 4 |
| SC-23 | " | R1 | not-mentioned | — | — |
| SC-24 | practice implication not decision-actionable; wrong actor | EIC | raised | EIC W5 ("no target students, no timing, no intervention, and no cost") | 4 |
| SC-24 | " | R3 | raised | R3 W4; Stakeholders | 4 |
| SC-24 | " | R1, R2 | not-mentioned | — | — |
| SC-24 | " | DA *(non-counting)* | raised (identification only) | DA Missing Stakeholder Perspectives | — |
| SC-25 | unstated "more LMS use is better" premise; no learning outcome | R3 | raised | R3 Assumption Audit (a); D3 | 4 |
| SC-25 | " | EIC, R1, R2 | not-mentioned | — | — |
| SC-25 | " | DA *(non-counting)* | raised | DA Unexamined Premise | — |
| SC-26 | no table or figure anywhere in the manuscript | EIC | raised | EIC Minor 1 | 4 |
| SC-26 | " | R1 | raised | R1 Minor 8 | 4 |
| SC-26 | " | R3 | raised | R3 Minor 6 | 4 |
| SC-26 | " | R2 | not-mentioned | — | — |
| SC-26 | " | DA *(non-counting)* | raised | DA D5 | — |
| SC-27 | APA reporting completeness (*df*, ASCII operators, explicit α, software/data/code) | R1 | raised | R1 Minor 1–6; Reproducibility | 4 |
| SC-27 | " | EIC, R2, R3 | not-mentioned | — | — |
| SC-28 | ~1,750 words below full-article norms; short-report track undeclared | EIC | raised | EIC Minor 4; Journal Fit | 4 |
| SC-28 | " | R1, R2, R3 | not-mentioned | — (DA explicitly declines to treat brevity as a defect) | — |
| SC-29 | item-level missingness among the 214 retained unreported | R1 | raised | R1 Data Collection; Q8 | 4 |
| SC-29 | " | EIC, R2, R3 | not-mentioned | — | — |
| SC-30 | robustness claim overstated; no CI or *p* reported for ρ | R1 | raised | R1 W2 closing paragraph | 4 |
| SC-30 | " | EIC, R2, R3 | not-mentioned | — | — |

### Step 1c — Surface-form parity check

Two arbitrations and several weightings in this synthesis had the potential to key off prose style rather than substance, so the counterfactual was run on each.

- **DA's card is the most technically dense in the panel** (likelihood-ratio framing, marker-variable vocabulary, an explicit parity gate of its own). Its CRITICAL finding was **not** credited for that specificity: SC-15 was assessed against the manuscript's §5 text and against the three seats that read the same passage differently, and it survives on the paper evidence, not on its phrasing. Conversely, DA's severity was not discounted for being adversarial in register.
- **R3's card is the most narrative and practitioner-flavoured** (institutional-seat framing, "as someone who would receive this recommendation"). SC-17, SC-24 and SC-25 were weighted on their paper anchors — the institution's own log holdings, the absence of any learning outcome in the manuscript, the median-only reporting — not down-rated for informal delivery. Rewritten in DA's register, none of these three would gain or lose weight.
- **R2's two disputes (SC-16, SC-19) are stated confidently and technically.** Neither was credited on that basis; both were resolved against the manuscript's own §6 limitation list and abstract text. Rewritten informally ("I think the abstract reads fine"), both would resolve identically.
- No sub-claim was marked unevaluable on wording grounds. Authorship of any card was not a weighting input.

## Consensus Analysis

### Points of Agreement

**[CONSENSUS-4]** — all four non-DA reviewers agree; author **must** address, no respectfully-decline option:

1. **SC-1** — The eligible-population denominator is absent. §3.1 states "All enrolled undergraduates were eligible," which asserts a population; without its size the response rate is unreportable and non-response is unassessable even in principle. → **R2**
2. **SC-14** — §5's onboarding implication crosses from the *perceived* use you measured to behaviour you did not. All four reviewers note that the hedging disclaims causality and leaves the construct substitution undisclaimed. → **R1**
3. **SC-9** — *r*² appears as "the proportion of variance shared by the two measures was accordingly modest" rather than as .18. → **P3-1** (trivial effort, mandatory action)

**[CONSENSUS-3]** — three agree, the fourth is **silent** (not opposed):

4. **SC-3** — §3.1's removal of 5 duplicates and §3.3's "could not be linked back to individual students" cannot both be literally true. *(EIC, R1, R3; R2 silent.)* R1 and R3 both explicitly asked that their sample-integrity and data-governance readings be consolidated into a single finding rather than double-counted; they are. → **R3**
5. **SC-6** — §3.4's scatterplot inspection, linearity, and symmetry claims are the stated warrant for the primary estimator and are exhibited nowhere. *(EIC, R1, R3; R2 silent.)* → **R5**
6. **SC-7** — The outcome is reported only as a median category: no frequencies, no dispersion, no floor/ceiling assessment. *(EIC, R1, R3; R2 silent.)* → **R5**
7. **SC-10** — §2 commits to reading the estimate as "one point in a distribution" and §5/§7 never perform the comparison. *(EIC, R2, R3; R1 silent.)* → **R4**
8. **SC-11** — "consistent with prior technology-acceptance research" appears in the Abstract, §5 and §7 with no prior numeric estimate anywhere in the manuscript. *(EIC, R2, R3; R1 silent.)* → **R4**
9. **SC-18** — The LMS is never named or characterised, and whether its use is required for submission, assessment or grade access is never stated. *(EIC, R1, R3; R2 silent.)* → **R8**
10. **SC-20** — "engagement" is used as an undefined near-synonym for a one-item access-frequency measure. *(R1, R2, R3; EIC silent.)* → **R7**
11. **SC-22** — "Adapted from Costa and Wren (2019)" never states what was adapted, and no validity evidence is reported for the adapted six items in this sample. *(R1, R2, R3; EIC silent.)* → **R9**
12. **SC-23** — The stated contribution ("a single, transparently reported association") is a property of the reporting, not of the knowledge produced. *(EIC, R2, R3; R1 silent.)* → **R10**
13. **SC-26** — The manuscript contains no table and no figure. *(EIC, R1, R3; R2 silent.)* → **R5**

**Corroborated findings** (2 of 4 agree, no conflict — action-bearing, below the consensus bar): SC-2 (R1, R3) → **S2**; SC-4 (EIC, R1) → **S1**; SC-5 (EIC, R1) → **S3**; SC-8 (R1, R3) → **R9**; SC-12 (EIC, R2) → **S5**; SC-17 (EIC, R3) → **S4**; SC-21 (R1, R3) → **S7**; SC-24 (EIC, R3) → **S8**.

**Single-reviewer findings** (1 of 4, all at Confidence 4 → full weight): SC-13 (EIC) → **S6**; SC-25 (R3) → **S9**; SC-27 (R1) → **P3-2**; SC-28 (EIC) → **R10**; SC-29 (R1) → **S10**; SC-30 (R1) → **S3**.

### Points of Disagreement

**Disagreement 1 — SC-16: is common-method variance already addressed?**

- **EIC, R1, R3 view**: CMV is not mentioned anywhere. Both constructs were elicited from one respondent, on one instrument, at one sitting; a single general disposition toward the platform could produce the observed association with no substantive perception-to-behaviour relation. R1 draws the operative distinction explicitly: "divergence concerns the validity of the criterion, whereas common-method variance concerns inflation of the *association* between the two measures. The paper addresses the former and is silent on the latter."
- **R2 view**: "Both threats the field names as central to this design — common-method concerns arising from simultaneous same-instrument self-report, and the self-report/log gap — are acknowledged (§2, §6), which keeps this at warn rather than block."
- **Disagreement type**: Existence disagreement.
- **Editor's Resolution**: **The sub-claim stands.** The manuscript must add a common-method-variance limitation and state what was and was not done about it.
- **Resolution rationale**: Evidence first — §2 and §6 discuss self-report versus behavioural logs, which is a claim about the criterion's *validity*; §6's four-item limitations list contains no item about shared-method variance between the two measures. R2's own weakness list never asserts that CMV is named as such; the acknowledgement R2 credits is the divergence discussion, which is a different threat. Expertise second — measurement threats sit in R1's seat, and R1 supplies the distinction with a paper-level anchor. Note that the resolution changes no dimension score: R2's D1 is `warn` and would remain `warn` on either reading, so the arbitration is about the author's obligation, not about the contract arithmetic (which is fixed by Part 0 and is not revisited here).

**Disagreement 2 — SC-19: does the abstract's closing sentence overreach?**

- **EIC, R1, R3 view**: The closing sentence — "perceived usefulness tracks with LMS engagement among undergraduates" — drops both the single-institution bound the body maintains and the "self-reported" qualifier the title carries. R1 files it under scope drift; EIC notes the abstract "omits the sample's institutional singularity from the results sentence"; R3 asks that it read "self-reported access frequency."
- **R2 view**: "the abstract does not strengthen the body's claims, which is the reverse of this genre's usual failure"; D5 records that the abstract does not overstate the body.
- **Disagreement type**: Severity disagreement (both sides accept the wording is imprecise; they differ on whether it constitutes overreach).
- **Editor's Resolution**: **The sub-claim stands, with R2's qualification recorded.** The required repair is qualifier restoration in the closing sentence, not a rewrite of the abstract's claim strength.
- **Resolution rationale**: R2's substantive point is accepted and is worth saying to the authors — the abstract does not inflate the coefficient, does not upgrade the causal register, and does not report anything the body lacks. That is genuinely unusual in this genre. But R2's own D4 concedes that "engagement" is used "as a near-synonym for reported frequency of access without saying so," which is the same defect at the terminology level (SC-20, on which R2 agrees). The two qualifiers the body maintains — single-site, self-reported — are simply absent from the sentence most readers stop at. Conservative principle applies: a one-sentence repair the author can make without cost, against a scope claim three reviewers read as unbounded.

### DA-CRITICAL: Devil's Advocate finding

**SC-15 — The §5 practice claim is logically foreclosed by the same paragraph.**

- **The DA's argument**: §5 states the reverse pathway is "equally consistent with the data." If that is true, the correlation's likelihood ratio between the forward (onboarding raises use) and reverse (use raises perceived usefulness) readings is exactly one, so the correlation supplies *no* directional evidence — not weak evidence. The qualifier "suggested by, not proven by" therefore misdescribes zero evidence as weak evidence. The DA further argues that common-method variance (M1) and course-level compulsion (M2) each fit the data at least as well as the authors' reading and cannot be discriminated within this design. This is the panel's only `block` score (D3) and it is the score that fired F1.
- **Corroboration**: **On the conclusion, complete.** All four non-DA reviewers independently require that the §5 implication be restated or removed (SC-14, CONSENSUS-4). **On the mechanism, contested.** EIC locates the defect in the construct switch and treats the causal hedge as doing real work ("The hedge covers the causal problem and misses the construct switch"); R2 the same ("correctly disclaims *causality* but does not disclaim the *construct substitution*"); R1's fallacy checklist records reverse causation as explicitly **not fired**. The DA's CMV rival account (M1) is separately corroborated by EIC, R1 and R3 (SC-16, arbitrated above).
- **Editor's assessment of validity**: The finding is **valid on its own terms and its remedy is not in dispute.** The DA's mechanism claim is stronger than three seats accept, and I record that dissent rather than flattening it: the other reviewers treat §5's causal hedging as genuine and locate the failure in the unhedged construct substitution. But the DA's argument does not depend on the other seats agreeing about *why* §5 fails — the "equally consistent" sentence is in the manuscript, the intervention recommendation is in the same paragraph, and no reading of the panel produces a §5 that can stand as written. The required author action is identical under every seat's reasoning, which is why the mechanism dispute does not need adjudication to produce a roadmap item. What the mechanism dispute does affect is the *acceptable repair*: restating the implication in perception terms (EIC, R2, R3's remedy) satisfies the construct objection but not the DA's, which is satisfied only by dropping the directional recommendation. **The author must respond to the DA's argument explicitly in the response letter, and must state which repair they chose and why** — this is required even though three reviewers frame the defect differently.
- **DA's other cross-cutting claims** are folded into the roadmap where other seats corroborate them (M1 → SC-16/**R6**; M2 → SC-21/**S7**; M3, M4 → SC-10, SC-11/**R4**; M5 → SC-3/**R3**; M6 → SC-6/**R5**; M7 → SC-4/**S1**; M8 → SC-1, SC-2/**R2**, **S2**; M9 → SC-19, SC-20/**R7**; M10 → SC-7, SC-8/**R5**, **R9**; Unexamined Premise → SC-25/**S9**).

## Decision Rationale

The contract arithmetic is unambiguous and is recorded in Part 0: the Devil's Advocate scored D3 `block`, which fires F1 (`any` quantifier, severity 90); all five reviewers carry three mandatory dimensions at `warn` or worse, which fires F2 at majority. F1 governs, and its action is `reject_or_major_revision`. Selecting the branch is the judgement that action delegates, and the panel's record settles it toward revision: four reviewers recommend major revision at Confidence 4, none recommends rejection, and the DA — the seat that produced the block — explicitly declines to make the publication-bar judgement, calling it the EIC's.

The substantive basis is the EIC's curability analysis, which the other seats corroborate item by item. The reporting defects (SC-1, SC-3, SC-6, SC-7, SC-9, SC-26, SC-27) are fixable from data the authors already hold. The benchmarking gap (SC-10, SC-11) is fixable with a literature pass, and is the single revision most likely to change the panel's assessment. The §5 defect (SC-14, SC-15) is fixable by restating or deleting one paragraph. What revision cannot supply is a reliability estimate for a single item already administered, so attenuation (SC-4) can be bounded and disclosed but not eliminated; and the contribution deficit (SC-23) is not closed by revision alone — it requires the institution's own log data, or an analytic layer, or an explicit and correctly-venued repositioning as a short report. The authors should be told that fork now rather than discover it after two more cycles.

Rejection was not chosen because no defect is unrecoverable and the execution quality is genuinely above this genre's median — verified arithmetic, an a priori sensitivity statement, a robustness check chosen for the right reason. Minor revision was not available: F2 fired on every seat, and correctly naming a limitation discloses it without curing it.

**Recorded contingency (not part of the mechanical evaluation).** The EIC flags that all six references carry sequential DOIs within a single prefix block (10.5555/2050001–2050006) while naming six different journals and publishers, makes no allegation, and scores D2 `warn` on the ground that a prefix pattern is a verification flag rather than a finding. The EIC records that if a reference-integrity check establishes the sources do not resolve, D2 converts to `block` and the decision converts to rejection. That contingency is the EIC's, is reproduced here faithfully, and did not enter the Part 0 arithmetic — which evaluated the scores as submitted. Roadmap item **S6** is the fastest route to closing it.

---

# Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. A DA-CRITICAL or non-decomposed item uses `—`.

## Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Source | Severity | Section | Priority | Effort |
|---|---|---|---|---|---|---|---|
| R1 | Restate the §5 practice implication strictly in perception terms, or delete it. If retained, the perception/behaviour boundary must appear in the same sentence, not deferred to §6; and the response letter must state explicitly which repair was chosen against the DA's argument that the "equally consistent" concession leaves the recommendation with no directional evidence at all. | SC-14, SC-15 | EIC, R1, R2, R3, **DA-CRITICAL** | Critical | §5, Abstract | P1 | 1 day |
| R2 | Report the eligible undergraduate population and the resulting response rate. Report year-level counts and, if institutional enrollment figures are available, benchmark the respondent distribution against them. If the rate is low, state it and discuss it rather than omitting it. | SC-1 | EIC, R1, R2, R3, DA | Critical | §3.1 | P1 | 2 days |
| R3 | State the exact mechanism by which the 5 duplicate entries were identified, the criterion applied, and when the identifier was discarded. Reconcile §3.3 with what was actually held — most likely replacing "anonymous" with "de-identified" or "pseudonymous at collection, anonymised before analysis" — and confirm whether the consent text shown to participants described the collection accurately. | SC-3 | EIC, R1, R3, DA | Critical | §3.1, §3.3 | P1 | 1 day |
| R4 | Perform the comparison §2 promises. State what Song (2018) reports across campuses and any pooled estimate you can obtain, and say in one sentence where [.30, .52] falls relative to it. Then either substantiate "consistent with prior technology-acceptance research" numerically or delete it from the Abstract, §5 and §7. If your estimate is unremarkable within that distribution, say so plainly — that is a legitimate result. | SC-10, SC-11 | EIC, R2, R3, DA | Critical | §2, §5, §7, Abstract | P1 | 4 days |
| R5 | Report the full frequency distribution of the use item with dispersion and an explicit floor/ceiling assessment. Supply the scatterplot §3.4 says was inspected and a descriptives table; or, if no figure is supplied, replace §3.4's linearity/symmetry assertions with reported distributional statistics. Print *r*² as .18 here rather than in prose. | SC-6, SC-7, SC-26 | EIC, R1, R3, DA | Critical | §3.4, §4 | P1 | 2 days |
| R6 | Add a common-method-variance limitation to §6: both constructs were elicited from one respondent, on one instrument, at one sitting, with no marker variable and no temporal separation. State what this does and does not permit, and distinguish it from the self-report/log divergence §2 and §6 already discuss. *(Arbitrated — see Disagreement 1.)* | SC-16 | EIC, R1, R3, DA · **disputed by R2** | Critical | §6, §3.4 | P1 | 1 day |
| R7 | Rewrite the abstract's closing sentence to restore both qualifiers the body maintains: single-institution scope and "self-reported." Use "self-reported access frequency" wherever the measure is meant, reserving "engagement" for the construct being gestured at, and define it at first use if retained. *(Arbitrated — see Disagreement 2.)* | SC-19, SC-20 | EIC, R1, R3, DA · **disputed by R2 (scope of repair)** | Major | Abstract, §1, §2, §4, §5 | P1 | 0.5 day |
| R8 | Name and characterise the LMS: vendor or in-house, feature scope, and — critically — whether use is required for assessment submission, attendance, or grade access. The interpretation of *r* = .42 turns on whether the sampled regime is discretionary or compelled, and no reader can currently tell. | SC-18 | EIC, R1, R3, DA | Major | §3.1, §3.2 | P1 | 1 day |
| R9 | State what was adapted from Costa and Wren (2019) — wording, item count, context — and either report structural evidence for the adapted six items in this sample or explicitly limit the comparability claim. Reproduce all six perceived-usefulness items and all five use-item anchor labels verbatim in an appendix. | SC-22, SC-8 | R1, R2, R3, DA | Major | §3.2, Appendix | P1 | 1 day |
| R10 | Address the contribution question directly. Either add analytic or comparative depth (the R4 benchmarking is the cheapest route; a log-validated criterion or a moderator/multivariate layer are the substantive ones), or reposition explicitly as a short report and declare the format so framing and container agree. Answer in the response letter, in one paragraph: what does a reader of this literature know after reading your paper that they did not know before? | SC-23, SC-28 | EIC, R2, R3 | Critical | §2, §6, §7, whole manuscript | P1 | 3–10 days |

### Required Item Details

**R1 — The §5 practice implication**
- **Problem**: The recommendation's warrant requires that raising perceived usefulness changes behaviour. You measured perception and reported perception. The hedging disclaims causality thoroughly and leaves the construct substitution undisclaimed; the DA argues further that the same paragraph's "equally consistent with the data" statement sets the correlation's directional evidence to zero, so "modest support" is not a weakened claim but an unsupported one.
- **Source**: EIC W5; R1 "Scope drift in the claim"; R2 W3; R3 D1; DA C1 (CRITICAL).
- **Requirement**: Restate in perception terms (an association between reported usefulness and reported use), *or* drop the recommendation. If restated, the boundary appears in the same sentence. The response letter must state which repair was chosen and answer the DA's directional-evidence argument specifically.
- **Acceptance criterion**: No sentence in §5 or the Abstract asserts or implies that changing perceived usefulness changes use, and no reader can extract an intervention recommendation from the passage.

**R2 — Denominator and response rate**
- **Problem**: §3.1 asserts a population ("All enrolled undergraduates were eligible") and never sizes it, so the response rate is unreportable and non-response is unassessable in principle. The only participant characteristic reported is "spanned all four year levels," which is too thin to support even a descriptive representativeness check.
- **Source**: EIC W4(a); R1 W4; R2 D1; R3 D1; DA M8.
- **Requirement**: State the eligible N and the response rate; add year-level counts and any available demographic composition; benchmark against institutional enrollment figures if obtainable.
- **Acceptance criterion**: A reader can compute the response rate from the manuscript and can compare respondent composition to the frame on at least one axis.

**R3 — Deduplication and the anonymity representation**
- **Problem**: Detecting a repeat submission requires a persistent per-respondent signal; every candidate (IP, session token, cookie, SSO handle, device fingerprint) is identifying or quasi-identifying. As written, either §3.3's characterisation of the data is inaccurate or the 5 exclusions rest on an undisclosed basis. Three reviewers read this as reporting imprecision rather than misconduct, and this letter records it as such — but it bears on the analyzed *N* and on the accuracy of what participants and the ethics committee were told.
- **Source**: EIC W4(d) and Q2; R1 W5; R3 W2; DA M5. R1 and R3 each asked that their two readings be consolidated; they are.
- **Requirement**: State the mechanism, the criterion, and when the identifier was discarded; align §3.3's terminology with what was actually held; confirm the consent text's accuracy.
- **Acceptance criterion**: §3.1 and §3.3 are consistent, and the exclusion rule is auditable by a reader.

**R4 — Execute the benchmarking**
- **Problem**: §2 identifies the correct interpretive frame and §5/§7 assert its conclusion without performing it. Three reviewers independently call this the manuscript's central positioning defect, and R2 notes it is currently unfixable from the cited evidence base — see S5, which is the enabling item.
- **Source**: EIC W1, W2; R2 W1 and Q1–Q2; R3 Assumption Audit; DA M3, M4.
- **Requirement**: Report at least Song's (2018) across-campus range and, if obtainable, a pooled estimate; place [.30, .52] against it in one sentence; substantiate or delete the consistency claim in all three locations.
- **Acceptance criterion**: A reader can determine from the manuscript whether *r* = .42 is typical, high or low for this literature.

## Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Source | Priority | Section | Expected improvement |
|---|---|---|---|---|---|---|
| S1 | Address attenuation from criterion unreliability. Supply a test-retest or alternate-form estimate if any subsample allows; failing that, report a disattenuation sensitivity range across a stated span of assumed criterion reliability and state that *r* = .42 is a floor. Revise §3.4's sensitivity statement, which assumes error-free measurement. | SC-4 | EIC, R1, DA | P2 | §3.2, §3.4, §6 | Bounds a bias the manuscript currently does not acknowledge, and one that runs against the authors' own "moderate" characterisation |
| S2 | State where the course-announcement channel sits relative to the LMS. If it is inside or authenticated through the platform, move this from §6's generalizability list into a stated threat to the estimate, and state the direction of bias as unknown rather than assumed attenuating. | SC-2 | R1, R3, DA | P2 | §3.1, §6 | Correctly classifies a selection mechanism that conditions on the outcome variable |
| S3 | Promote Spearman's ρ to the primary estimate with its own CI and *p*; retain Pearson as supplementary. Soften the robustness claim: agreement of two point estimates does not show the *inference* is assumption-free while all reported inference remains Fisher-*z*-based. | SC-5, SC-30 | EIC (flagged, deferred), R1 | P2 | §3.4, §4 | Removes an internal inconsistency with §3.2's own ordinal declaration at no substantive cost (ρ = .40 vs *r* = .42) |
| S4 | State in §3.2 why self-report was the criterion when the institution holds server-side access logs for every respondent. A governance rationale (consent for linkage, re-identification risk, committee constraint) is a legitimate and arguably preferable answer and should be stated as one. Consider a consent-linked validation sub-sample (n ≈ 40) reporting self-report/log agreement in your own setting. | SC-17 | EIC, R3, DA | P2 | §3.2, §6, §7 | Converts an unexplained design choice into a stated methodological position; the sub-sample would be the paper's most transferable result |
| S5 | Cite the originating primary source for perceived usefulness directly rather than through intermediaries, and add at least one synthesis reporting a pooled or ranged estimate — then use that synthesis as R4's benchmark. Adding references without performing R4 does not close R4. | SC-12 | EIC, R2, DA (unresolved) | P2 | §2, References | Supplies the enabling material for R4 and repairs the construct's scholarly provenance |
| S6 | Supply resolvable DOIs for all six references. | SC-13 | EIC | P2 | References | Closes the reference-integrity contingency recorded in the Decision Rationale by the fastest available route |
| S7 | Add confounding to §6's limitations list. §4 already names course requirements and assessment schedules as competing influences; state that none was measured and no control was attempted. | SC-21 | R1, R3, DA | P2 | §6 | Aligns the limitations section with a threat the Results section already concedes |
| S8 | Either drop the practice implication to a single Future Directions sentence, or ground it in a statistic you already hold — e.g. the proportion of respondents in the "rarely or never" category, which is the tail an onboarding intervention would have to reach. Name the actor: your own cited literature locates the lever with instructors and course design, not with students. | SC-24 | EIC, R3, DA (identification only) | P2 | §5 | Makes the implication actionable or removes it; corrects the actor mismatch |
| S9 | State the premise that more LMS use is desirable, or drop the normative frame. No learning outcome appears anywhere in the manuscript, so both variables currently float free of any institutional objective. | SC-25 | R3, DA | P2 | §1, §5 | Surfaces an unexamined warrant that the descriptive conclusion survives without but the recommendation does not |
| S10 | Report item-level missingness among the 214 retained responses and the handling method. | SC-29 | R1 | P2 | §3.1, §3.4 | Completes the data-handling account beyond the pre-analysis exclusions |

## Revision Checklist

### Priority 1 — Structural Revisions (estimated total: 16–23 days)
- [ ] **R1** [DA-CRITICAL + CONSENSUS-4] Restate or delete the §5 practice implication; answer the DA's directional-evidence argument in the response letter
- [ ] **R2** [CONSENSUS-4] Report eligible population, response rate, and year-level composition
- [ ] **R3** [CONSENSUS-3] State the deduplication mechanism; reconcile §3.1 with §3.3 and with the consent text
- [ ] **R4** [CONSENSUS-3] Perform the §2 benchmarking; substantiate or delete "consistent with prior research" in all three locations
- [ ] **R5** [CONSENSUS-3] Report the criterion's distribution and dispersion; supply the scatterplot and a descriptives table; print *r*² = .18
- [ ] **R6** [ARBITRATED] Add a common-method-variance limitation distinct from the self-report/log divergence
- [ ] **R7** [ARBITRATED] Restore the single-site and "self-reported" qualifiers in the abstract; discipline "engagement" throughout
- [ ] **R8** [CONSENSUS-3] Name and characterise the LMS; state whether use is mandatory
- [ ] **R9** [CONSENSUS-3] Document the adaptation; append both instruments in full, including anchors 2–4
- [ ] **R10** [CONSENSUS-3] Add depth or declare a short-report repositioning; answer "what does this change?" in the response letter

### Priority 2 — Content Supplementation (estimated total: 9–13 days)
- [ ] **S1** Bound and disclose criterion attenuation; correct the sensitivity statement
- [ ] **S2** Locate the recruitment channel relative to the LMS; reclassify as a threat to the estimate
- [ ] **S3** Promote Spearman to primary with CI and *p*; soften the robustness claim
- [ ] **S4** State the rationale for self-report over available logs; consider a consent-linked validation sub-sample
- [ ] **S5** Add the construct's primary source and a synthesis anchor; feed the synthesis into R4
- [ ] **S6** Supply resolvable DOIs for all six references
- [ ] **S7** Add confounding to §6
- [ ] **S8** Ground or drop the practice implication; name the correct actor
- [ ] **S9** State or drop the "more use is better" premise
- [ ] **S10** Report item-level missingness and its handling

### Priority 3 — Text and Formatting (estimated total: 2 days)
- [ ] **P3-1** [CONSENSUS-4 — must address, trivial effort] Print *r*² as .18 in §4 rather than "accordingly modest" *(also covered by R5)*
- [ ] **P3-2** APA reporting completeness: add *df* (*r*(212) = .42); replace ASCII operators with ≥ and α; italicise statistical symbols; state α = .05 explicitly in §3.4; label the sensitivity statement as conditional on the achieved sample rather than as design-stage power; give the original instrument's numeric internal-consistency value; report software and package versions; add data-, code- and instrument-availability statements
- [ ] Include the CI in the abstract (eight characters; improves standalone accuracy)
- [ ] §1: "a substantial body of work suggests" is supported by one citation — broaden the support or soften the quantifier
- [ ] §2: "effect sizes vary across samples and instruments" reports no variation — this is the natural place to carry R4's numeric anchor
- [ ] §5: Whitfield (2019) is correctly labelled as a practitioner account but is attached to an implication it cannot support — the placement, not the labelling, is the issue

**Integrity note.** All five reviewers independently scanned the manuscript for reviewer-directed content or instruction injection and all five report it clean. This is recorded for the file and requires no author action.

## Revision Deadline

- **Recommended**: 8 weeks from the decision date (2026-09-19). Major revision band is 6–8 weeks; the upper bound is recommended because R4 requires a literature pass and R10 may require a repositioning decision.
- **Extension policy**: notify the editorial office one week before the deadline.
- **Re-review**: the revised manuscript will undergo another round of review.

## Response Letter Instructions

Please use `templates/revision_response_template.md` (Reviewer Comment → Author Response → Changes Made) and respond to every item above individually. Required:

1. A response and change description for each Required Revision **R1–R10**.
2. A response for each Suggested Revision **S1–S10** — adopted, or the reason for not adopting.
3. Explicit answers to the two questions the panel asks directly of the response letter rather than of the manuscript: **R1's** statement of which §5 repair you chose and why, against the Devil's Advocate's argument; and **R10's** one-paragraph answer to *what does a reader of this literature know after reading your paper that they did not know before?*
4. Tracked changes or colour markup throughout, plus a page/paragraph cross-reference table between the original and revised manuscripts.

CONSENSUS-4 items (R1, R2, and *r*² under P3-1) carry no respectfully-decline option and must be addressed substantively.

## Closing

We encourage you to consider the reviewers' comments carefully and submit a substantially revised manuscript. Please note that the revised version will undergo another round of review.

Two things should be said plainly alongside the length of this list. First, the execution quality here is real and the panel says so unanimously: your confidence interval, your a priori sensitivity statement, your rank-based robustness check chosen for the right reason, your explicit statement of the reverse pathway, and your specific ethics reporting are all above this genre's median, and two reviewers independently recomputed your headline statistics and found them correct. This decision turns on contribution and reporting completeness, not on competence. Second, the panel's shared finding is that correctly naming a limitation discloses it without curing it — and that your hedging is thorough on the causal axis, where the design is already well understood, and absent on the measurement and comparative axes, where the binding constraints actually sit. Most of what that costs you is recoverable from data and literature already within reach.

One fork deserves stating now rather than after another cycle. If you decline to add analytic or comparative depth under R10, the honest destination for this manuscript is a venue with an explicit short-report track — the EIC names the *Australasian Journal of Educational Technology* and *Research in Learning Technology* — and repositioning there is a legitimate outcome, not a failure. If you do execute R4 and R10, this journal is a defensible home for the paper.

---

# Part 3: Reviewer Report Summary (Appendix)

### EIC
- **Recommendation**: Major Revision | **Confidence**: 4 | **Scores**: D1 warn · D2 warn · D3 warn · D4 warn · D5 warn | **Fired**: F2
- **Key point**: The manuscript passes every screen for over-claiming and still fails the journal's standing question — *what does this change?* — because §2 identifies the comparison that would convert a coefficient into a contribution and §5/§7 assert its conclusion without performing it. Disclosure earns credit against integrity, not against contribution. Records a reference-integrity contingency on the sequential DOI block that would convert D2 to block if the sources do not resolve.

### Reviewer 1 (Methodology)
- **Recommendation**: Major Revision | **Confidence**: 4 | **Scores**: D1 warn · D2 warn · D3 warn · D4 warn · D5 warn | **Fired**: F2
- **Key point**: The inferential discipline is genuine and the arithmetic verifies — the Fisher-*z* interval and the sensitivity figure both reproduce at *n* = 214 — but the paper's caution is concentrated on the causal axis and absent on the measurement axis, where the binding constraint sits: an unreliable, undocumented, non-reproducible single-item criterion whose attenuation is never bounded, plus a response rate that is unreportable rather than merely unreported.

### Reviewer 2 (Domain)
- **Recommendation**: Major Revision | **Confidence**: 4 | **Scores**: D1 warn · D2 warn · D3 warn · D4 warn · D5 warn | **Fired**: F2
- **Key point**: The paper is domain-competent — construct definition, perception/behaviour boundary, bidirectional causality, refusal of theory-testing overreach — and its problem is anchoring, not accuracy: a consistency claim asserted three times with no numeric comparator, unsupportable from a six-item reference list containing neither the construct's primary source nor any synthesis. Dissents from the panel on two points: that common-method concerns are acknowledged in §2/§6, and that the abstract does not overstate the body.

### Reviewer 3 (Perspective)
- **Recommendation**: Major Revision | **Confidence**: 4 | **Scores**: D1 warn · D2 warn · D3 warn · D4 warn · D5 warn | **Fired**: F2
- **Key point**: The study's largest limitation was avoidable rather than imposed — the institution holds server-side logs for every respondent, the paper cites the divergence literature, concedes the point, and proceeds with no stated rationale, leaving a reader unable to distinguish a principled governance choice from an unexamined one. Adds the anonymity-representation reading of the deduplication contradiction, the recruitment channel's effect on the estimate, and the actor mismatch in §5.

### Devil's Advocate
- **Recommendation**: contract action `reject_or_major_revision` | **Confidence**: not stated | **Scores**: D1 warn · D2 warn · **D3 block** · D4 warn · D5 warn | **Fired**: F1, F2
- **Key point**: §5 states a limitation that logically forecloses its own practice claim and then makes the claim — if the reverse pathway is "equally consistent with the data," the correlation supplies no directional evidence and "modest support" misstates zero as weak. Behind that sit two rival accounts the design cannot discriminate: a single method factor (never mentioned in the manuscript) and course-level compulsion (named in §4, measured nowhere). Also documents that every cited caution is named once in §2 and constrains no downstream claim. Declines to escalate two further dimensions where its Phase 1 plan did not authorise it, and records both declines.
