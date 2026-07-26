# Isolated-dispatch panel review — 2026-07-27-ms00_clean-post-r1

(Every seat's Phase 1 and Phase 2 was a physically separate headless `claude -p` call on claude-opus-5 at effort xhigh. The review processes had no tools and ran outside the repository; Phase 1 received only contract plus title/field/word_count.)

# PART 1 — FIELD ANALYSIS

# Field Analysis Report

## Paper Basic Information

- **Title**: Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students
- **Abstract length**: ~185 words
- **Full text length**: ~1,900 words (excluding references) — brief-report scale, roughly a quarter of a standard empirical article
- **Number of references**: 6
- **Language**: English (review to be conducted in English)
- **Structural completeness**: All IMRaD sections present, plus a standalone Limitations section; ethics statement present; CI, p, n, and a robustness check all reported

## Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| **Primary Discipline** | Educational technology in higher education — specifically LMS adoption/engagement research |
| **Secondary Disciplines** | (1) Information systems / technology-acceptance research (TAM lineage); (2) educational measurement and survey psychometrics; (3) learning analytics & institutional research |
| **Research Paradigm** | Quantitative — descriptive/correlational, non-experimental |
| **Methodology Type** | Cross-sectional survey (single-site, voluntary-response); bivariate correlational analysis (Pearson with Spearman robustness check) |
| **Target Journal Tier** | **Q3**, with a plausible Q2 landing as a short/brief report. Rationale: the paper's *craft* is above its *contribution*. It reports one bivariate correlation from one institution using an adapted instrument, with no theoretical extension, no moderators, no multivariate model, and no novel construct. The reference base (6 sources) is far below the norm for Q1 educational-technology journals. It is competently and honestly executed, but a Q1 outlet (*Computers & Education*, *BJET*, *Internet and Higher Education*) would very likely desk-reject on novelty and scope. |
| **Paper Maturity** | **Pre-submission**. Prose is polished and internally consistent; hedging language is disciplined and uniform; reporting standards (CI, exact n, power statement, robustness check) exceed what a first or revised draft typically shows. Remaining work is substantive gap-filling, not restructuring. |

### Notes on the tier judgment

Tier assignment here is unusually contested and the review team should be told so explicitly. The manuscript's defining feature is **epistemic restraint** — it repeatedly refuses causal language, flags the reverse-causal pathway, treats self-report as perceived rather than actual use, and frames itself as "an incremental data point." That restraint is genuinely uncommon and is the paper's strongest asset. It is also, from an editor's standpoint, an argument *against* acceptance at any journal that requires a contribution claim: a paper that accurately describes itself as incremental has made the desk-rejection case on the editor's behalf. This tension is the central editorial question of the review and must not be smoothed over.

## Recommended Target Journals (Top 3)

Journal quartiles shift year to year; the labels below are indicative of typical positioning rather than fixed.

1. **Education and Information Technologies** (Springer) — The most realistic honest match. High-volume, routinely publishes single-institution TAM/LMS survey studies of exactly this scope, and the manuscript's reporting quality would sit at or above the journal's median. Main risk: reviewers there frequently demand a fuller acceptance model (PU + PEOU + BI + actual use, SEM), which would require the authors to abandon the narrow framing that is currently the paper's best feature.

2. **Contemporary Educational Technology** — Open access, receptive to bounded single-site empirical work, and explicitly tolerant of modest-scope contributions. Better fit for the paper *as written* because it does not pressure the authors toward a model they deliberately declined to test. Lower visibility is the trade-off.

3. **Journal of Information Technology Education: Research (JITE:Research)** — Accepts brief empirical reports and replication-adjacent work; the manuscript's transparent limitations section aligns well with the journal's stated values. Best option if the authors decide to reframe explicitly as a replication/brief report rather than a novel contribution.

**Stretch option, only if substantially strengthened:** *Australasian Journal of Educational Technology* — would require log-data validation of the self-report measure, a real response rate, and either a multivariate model or a defensible replication framing.

## Reviewer Configuration Cards

---

### Reviewer Configuration Card #1

**Role**: Editor-in-Chief

**Identity Description**: Editor-in-Chief of a mid-tier international educational-technology journal (Q2/Q3 range) that publishes both full articles and short empirical reports. Fifteen years handling LMS adoption and technology-acceptance submissions; has personally desk-rejected several hundred single-institution TAM survey papers and is known for a standing editorial position that the field is saturated with underpowered, non-replicable acceptance studies. Has publicly argued that journals should accept *fewer but better-reported* correlational studies, and has piloted a "brief report" track for exactly this reason.

**Review Focus**:
1. **Contribution versus craft.** Determine whether disciplined reporting and honest framing constitute sufficient grounds for publication when the substantive finding (perceived usefulness correlates ~.4 with self-reported use) has been reported many times since the late 1980s. Decide explicitly whether this is a *replication* — and if so, whether the authors should say so — or an *original contribution*, which the manuscript's own text does not sustain.
2. **Format fit.** Assess whether the manuscript should be redirected to a short-report or research-note track rather than reviewed as a full article, given ~1,900 words and 6 references.
3. **Reader interest and scope.** Judge whether the journal's international readership gains anything actionable from a single unnamed mid-sized public university, and whether the absence of any institutional or national context (system, sector, LMS platform, country) makes the finding uninterpretable for comparative readers.

**Will particularly care about**: Whether the paper's honesty is doing real work or is functioning as pre-emptive cover — i.e., whether "we acknowledge this is modest" has been substituted for actually making the study less modest, when cheap design upgrades (log data, response rate, a second use item) were available.

**Possible blind spots**: An editor primed to see saturation may undervalue the genuine field-level scarcity of well-calibrated correlational reporting, and may underweight the value of adding a clean estimate to a literature whose published effect sizes are likely inflated by selective reporting. May also default to a scope-based rejection without engaging the specific technical merits the methodologist will surface.

---

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1 — Methodology

**Identity Description**: Quantitative methodologist in educational measurement, specializing in survey psychometrics and the analysis of ordinal and single-item measures. Trained in item response theory and structural equation modeling; publishes on measurement invariance and on the statistical consequences of treating Likert responses as continuous. Serves as a statistical reviewer for two journals and has written on reporting standards (APA JARS-QUANT) for correlational research.

**Review Focus**:
1. **Single-item outcome measure.** The dependent variable is one five-point frequency item. No reliability can be estimated for it, its response categories ("rarely or never" → "several times daily") are non-equidistant and almost certainly non-linear in actual access counts, and its coarseness attenuates the observed correlation by an unknown amount. Evaluate whether any correction for attenuation is warranted, whether a polyserial/polychoric estimate should be reported instead, and whether the paper should report the full frequency distribution rather than only a median category.
2. **Instrument adaptation and validation chain.** The six-item scale is described only as "adapted from Costa and Wren (2019)." What was changed, and why? Cronbach's α = .88 establishes internal consistency but nothing about dimensionality or structural validity in this sample; no CFA, no factor loadings, no item-level statistics, and no evidence that the adapted version measures what the original did. Determine whether "previously validated" is a defensible claim for a modified instrument.
3. **Sample, response rate, and reporting completeness.** No response rate is reported and none can be computed: the eligible population ("all enrolled undergraduates") is never enumerated. Sample description is limited to "spanned all four year levels" — no year-level distribution, no discipline, no gender, no age, no prior LMS experience. Also verify the power statement (n = 214 sits marginally below the ~215 typically required for .80 power at r = .19, α = .05, two-tailed, so ">.80 power to detect r ≥ .19" is borderline as stated), and assess common-method variance, since predictor and outcome were collected from the same respondents in the same instrument at the same moment.

**Will particularly care about**: Whether the reported precision is honest precision. The 95% CI [.30, .52] is correctly computed for r = .42 at n = 214, and the Spearman check is appropriate — but a correctly computed interval around a measure of unknown validity conveys false confidence. This reviewer will treat the gap between *statistical* rigor and *measurement* rigor as the paper's core technical problem.

**Possible blind spots**: May treat measurement adequacy as a purely technical matter and undervalue the paper's careful inferential restraint, which is a genuine methodological virtue. May also push for psychometric elaboration (CFA, IRT) disproportionate to a brief report, and is unlikely to raise the ethics/deduplication inconsistency or the practical-utility question.

---

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2 — Domain

**Identity Description**: Senior higher-education researcher specializing in technology adoption in university settings, with two decades of work tracing the TAM/UTAUT lineage and its educational applications. Has published critical reviews of acceptance-model research in higher education and is familiar with the long-standing information-systems critique of TAM as theoretically exhausted (Bagozzi; Benbasat & Barki). Regularly reviews for LMS and digital-learning journals and maintains an active reading of the LMS engagement literature.

**Review Focus**:
1. **Literature base adequacy and provenance.** Six references is far below field norms and cannot support the claim that findings are "consistent with prior technology-acceptance research." The foundational acceptance literature (Davis 1989; Venkatesh & Davis 2000; Venkatesh et al. 2003) is entirely absent, as are the last five years of LMS-engagement studies. Separately and importantly: **all six references carry DOIs under the 10.5555 prefix, which is a reserved test/example prefix, not a live registrant prefix** — none of the cited works can be resolved. This is stated as an observation requiring verification, not an allegation, but it must be resolved before any recommendation is issued.
2. **Theoretical positioning.** The paper isolates perceived usefulness while omitting perceived ease of use, behavioral intention, facilitating conditions, and social influence. Assess whether extracting one path from a well-specified model and reporting it as a bare bivariate correlation is a defensible simplification or an under-specified model that guarantees omitted-variable confounding — particularly given that course requirements and assessment schedules (which the authors themselves name in the Results) plausibly drive both variables.
3. **Contribution to the field's cumulative knowledge.** The paper positions itself as "one point in a distribution" (citing Song, 2018, on cross-institution variability). Evaluate whether it delivers on that framing: does it report enough contextual detail — LMS platform, institutional policy on LMS use, whether LMS use is mandatory for assessment — for any future meta-analyst or comparative researcher to actually use this estimate? Currently it does not.

**Will particularly care about**: Whether "perceived usefulness" is doing conceptual work at all here, or whether it is a proxy for compliance. If the institution requires LMS access for submitting assessments, both variables partly index course structure rather than perception, and the correlation becomes substantively uninterpretable regardless of its statistical properties.

**Possible blind spots**: Deep familiarity with the acceptance literature may pull toward "test the full model" recommendations that would destroy the manuscript's deliberate narrowness — the very restraint the EIC and synthesizer must weigh. May also underweight measurement detail and is unlikely to notice the operational contradiction in the ethics procedure.

---

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3 — Cross-disciplinary / Practical

**Identity Description**: Director of learning analytics and institutional research at a public university, with a computer science background and operational responsibility for the institution's LMS data warehouse. Builds engagement dashboards from LMS event logs, advises senior leadership on educational technology investment, and sits on the institution's research ethics committee as the data-governance member. Publishes occasionally in learning analytics venues but works primarily as a practitioner. Approaches every study by asking what an institution would actually *do* on Monday morning with the finding.

**Review Focus**:
1. **The self-report choice was avoidable, not merely limiting.** Every LMS in production emits per-user access logs. The authors surveyed students at their own institution about their use of their own institution's system, and then cite Vasquez (2020) to acknowledge that self-report diverges from behavioral traces — while declining to use the behavioral traces that were sitting in the institution's own database. Assess whether this is a defensible constraint (ethics approval scope, data access, anonymity requirements) or an unexamined design default, and require the authors to state which.
2. **Operational contradiction between anonymity and deduplication.** Section 3.3 states "no identifying information was collected" and that "responses could not be linked back to individual students." Section 3.1 states that "5 duplicate entries" were removed. These cannot both be fully true without some persistent identifier — IP address, session token, browser fingerprint, or an institutional SSO handle. Determine what was actually collected, whether the ethics submission disclosed it, and whether the anonymity claim to participants was accurate as stated on the consent landing page.
3. **Actionability of the practical implication.** The Discussion suggests LMS onboarding emphasizing "concrete usefulness" may deserve institutional attention. Evaluate whether r = .42 (≈18% shared variance) between two self-reported perceptual measures can support any resource-allocation decision, and whether recommending an onboarding intervention on the basis of a cross-sectional correlation — which the authors elsewhere correctly refuse to read causally — is internally consistent with the paper's own stated inferential limits.

**Will particularly care about**: The gap between what a practitioner needs and what this study supplies. An institution deciding whether to fund LMS onboarding needs to know which students under-engage, in which courses, and whether an intervention moves behavior — none of which a single bivariate perceptual correlation can address, and all of which the institution's existing log data could begin to answer at near-zero marginal cost.

**Possible blind spots**: Practitioner framing may undervalue the legitimate scholarly purpose of contributing a comparable estimate to a distributed literature, and may hold a brief report to an intervention-evaluation standard it never claimed to meet. Log-data enthusiasm may also underweight the real privacy and ethics constraints on using institutional trace data for research, and the fact that perceived usefulness is genuinely not observable in logs.

---

## Review Strategy Recommendations

### Special characteristics requiring attention

**1. Mandatory first-party citation verification before any recommendation is finalized.** All six references resolve to DOIs under the `10.5555` prefix, which is the reserved test/example prefix and does not correspond to a live registrant. The journal names and volume/issue/page patterns are plausibly formatted but none of the works could be located. This must be verified deterministically — by attempting DOI resolution and database lookup on each entry — rather than assessed by impression. If confirmed, this supersedes every substantive review point: no recommendation other than reject or return-to-author is available for a manuscript whose entire evidentiary and positioning base is unverifiable. Reviewers 2 and 3 should be instructed to flag but not adjudicate this; the EIC adjudicates after verification.

**2. The manuscript's virtue is also the case against it.** The disciplined refusal to over-claim is real and should be credited explicitly in every review — it is rarer than it should be. But credit for restraint must not become a substitute for evaluating the contribution. The synthesizer must resolve, not average, the question of whether an accurately-described modest finding clears the publication bar. A recommendation of "accept because the authors are honest about the weaknesses" is not evidence-based; neither is "reject because it is modest" without engaging what the modest finding actually adds.

**3. Arithmetic and reporting checks already performed and confirmed correct** (so reviewers do not waste effort re-litigating them): the 95% CI [.30, .52] is correctly derived for r = .42 at n = 214 via Fisher's z; r² ≈ .18 is consistent with the "modest shared variance" characterisation; the Spearman/Pearson convergence (ρ = .40 vs r = .42) is the appropriate robustness check for an ordinal outcome. The one item worth a reviewer's attention is the power statement, which is marginal rather than wrong (n = 214 versus ~215 required for .80 power at r = .19). Reviewer 1 owns this.

**4. Register.** This is a pre-submission manuscript of competent craft, not a weak first draft. Reviews should use a normal evaluative register, not developmental scaffolding. Register affects wording only — the recommendation itself must remain driven by the evidence against the criteria, and must not soften because the authors write carefully.

### Anticipated complementarity and tension between reviewers

- **R2 versus the manuscript's design logic (primary tension).** R2 will likely recommend specifying a fuller acceptance model. Doing so would require abandoning the narrow correlational framing that the EIC may identify as the paper's chief merit. The synthesizer must adjudicate this directly rather than passing both recommendations through: "test the full model" and "we commend the paper's deliberate narrowness" cannot both appear in a coherent decision letter.

- **R1 and R3 converge on the outcome measure from non-overlapping directions.** R1 argues from measurement theory (a single ordinal item cannot carry the inferential load placed on it); R3 argues from data infrastructure (behavioral logs existed and were not used). These are complementary, not duplicative, and their convergence is the strongest technical finding in the review set. The synthesizer should present them as a single reinforced conclusion with two independent lines of support.

- **R3 uniquely owns the ethics/deduplication contradiction.** No other reviewer configuration is positioned to catch it. If R3's review is thin, this issue will be lost, and it is a genuine problem — an anonymity claim made to participants that appears operationally inconsistent with the reported data-cleaning procedure.

- **EIC and R2 risk redundancy on novelty.** Keep them separated in scope: the EIC judges *fit and format* (should this be a short report, does the readership benefit); R2 judges *literature adequacy and theoretical positioning* (is the citation base sufficient, is single-path extraction defensible). If both simply say "TAM is saturated," one of them has not done its job.

- **Coverage confirmation.** No reviewer's primary focus overlaps another's: EIC = editorial fit and contribution threshold; R1 = measurement and inference within the chosen design; R2 = literature base and theoretical positioning; R3 = data infrastructure, research ethics operations, and institutional actionability.

# PART 2 — SEATS

## SEAT — EIC

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory, owned by the methodology reviewer).** This dimension asks whether the study's design, sampling, data handling, and statistical reporting would survive scrutiny by a competent methodologist in the paper's own field, and whether enough procedural detail is disclosed that another team could plausibly repeat the work. It is a mandatory gate, so a fatal finding here drives outright rejection under F1. This dimension is not open to my dispatch role; I paraphrase it only to demonstrate that I understand what the methodology reviewer is being asked to guard.

**D2 — domain_accuracy (mandatory, owned by the domain reviewer).** Here the question is whether the substantive claims match the current state of evidence in the field, whether prior literature is characterised faithfully rather than conveniently, and whether field-specific terminology, constructs, and reported results are used correctly. Misrepresenting a cited source or misusing an established construct falls squarely here. Also mandatory, also outside my role's eligibility.

**D3 — argumentative_coherence (mandatory, owned by the discourse-analysis reviewer, with methodology also eligible).** This dimension tests the internal logic of the manuscript: whether the central thesis holds together without contradicting itself, whether the evidence actually licenses the conclusions drawn from it, and whether any reasoning defect is severe enough to undermine the paper's spine rather than merely a local infelicity. It is mandatory and assigned to two eligible roles, neither of which is mine.

**D4 — cross_disciplinary_relevance (high priority, owned by the perspective reviewer).** The concern is whether a reader from an adjacent field can enter the paper — whether framing, definitions, and stated implications are legible outside the narrow specialty, and whether any claim reaching across disciplinary boundaries is actually backed rather than asserted. High priority rather than mandatory, so a block here triggers major revision under F4 rather than rejection. Not eligible for my role.

**D5 — writing_and_structure (normal priority, owned by me as EiC).** This is my dimension. It covers how the manuscript is organised, whether the exposition is clear enough for the reader to follow the argument without reconstructing it, whether figures and tables are of adequate quality and properly integrated, and whether the manuscript observes the conventions the venue expects. It carries normal priority, so problems here reach at most minor revision under F5 unless they compound with other dimensions.

**D6 — venue_fit_and_contribution (mandatory, owned by me as EiC).** Also mine, and mandatory. It asks two linked questions: whether this manuscript belongs in the configured venue at all given its scope and readership, and whether it offers something original and consequential enough to justify the space it would occupy. Because it is mandatory, a fatal finding here reaches F1 rejection and a block reaches F2 major revision, so the threshold for declaring a fatal must be genuinely severe and not merely a judgement that the contribution is modest.

## Scoring Plan

### D5: writing_and_structure

dimension_id: D5
what_to_look_for: Whether sections follow a coherent and conventional progression, whether the abstract and introduction accurately preview what the body delivers, whether terminology and notation stay consistent throughout, whether every figure and table is numbered, captioned, legible, and referenced in the text, and whether length, citation format, and reporting conventions match what the venue expects.
what_triggers_block: Organisation or exposition so defective that a competent reader cannot reliably determine what was done or what is being claimed — for example missing or unlabelled essential sections, figures and tables that are uninterpretable or contradict the text, or prose so unclear that key statements admit incompatible readings.
what_triggers_warn: Localised but real presentation defects that impede rather than prevent comprehension — for example redundant or misordered subsections, inconsistent terminology, uncaptioned or never-referenced exhibits, undefined abbreviations, or departures from venue formatting and reporting conventions.

### D6: venue_fit_and_contribution

dimension_id: D6
what_to_look_for: Whether the topic, scope, methods, and intended audience fall within the configured venue's remit; whether the manuscript states a clear contribution and positions it against existing work; whether that contribution is genuinely novel rather than a restatement of settled knowledge; and whether its significance is proportionate to the venue's readership and to the manuscript's declared length and ambition.
what_triggers_block: A substantial mismatch with the venue or a contribution too thin to warrant publication as submitted — for example scope well outside the venue's stated remit, a contribution indistinguishable from prior work already in the literature, or claimed significance that the manuscript's own scope cannot support without further work.
what_triggers_warn: Fit and contribution are defensible but underspecified — for example the novelty claim is real yet never explicitly positioned against the closest prior work, the implications for the venue's readership are asserted rather than argued, or the framing skews toward an adjacent venue while the substance still belongs here.
what_triggers_fatal: No identifiable contribution or venue relationship at all — for example the manuscript is categorically out of scope for the venue, offers no claim beyond what is already established, or is a duplicate or near-duplicate of previously published work.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

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
score: warn
trigger: "departures from venue formatting and reporting conventions"

### D6: venue_fit_and_contribution
score: block
block_class: repairable
trigger: "a contribution indistinguishable from prior work already in the literature"

## Review Body

I read this manuscript from the editor's chair, which means my question is narrower than my colleagues': does this paper belong in this journal, in this format, and does it give this readership something it does not already have? I am deliberately leaving the adequacy of the six-item scale, the sufficiency of the citation base as a matter of theoretical positioning, and the internal logic of the argument to the reviewers who own those dimensions.

Let me start with what is genuinely good, because it is unusual and it should be said plainly rather than buried under the criticism that follows. This manuscript does not over-claim. It refuses causal language in the abstract, names the reverse-causal pathway in the discussion, treats a self-report item as an indicator of perceived rather than actual use, and closes by describing itself as incremental. I handle a great many single-institution acceptance surveys, and the majority of them assert more than their design can carry. This one does not. The reporting of the correlation itself is complete in the way I wish were standard: coefficient, confidence interval, exact p, exact n, a power statement, and an ordinal robustness check. The limitations section names real constraints rather than reciting the four sentences that usually appear there.

That restraint, though, is precisely where my editorial problem begins, and I want to be direct about it rather than diplomatic. Honest self-description is not a contribution. When a manuscript accurately reports that it is "an incremental data point," it has stated the case for desk rejection on my behalf, and my job is to decide whether the increment is worth the pages. Two things persuade me it is not, as submitted.

First, the substantive finding — perceived usefulness correlates moderately with self-reported use — is among the most repeatedly reported results in this literature, and the manuscript nowhere positions itself as a replication. It positions itself as a contribution. Those are different submissions with different evaluation criteria, and the authors have chosen the framing under which their result is weakest. A replication framing would let the estimate do real work; the contribution framing invites the comparison it cannot survive.

Second, and more damaging to the authors' own stated purpose, the paper claims to supply "one point in a distribution" of cross-institutional estimates but withholds everything a comparative reader would need to locate that point. There is no country, no sector, no LMS product, no statement of whether LMS access is required for assessment submission, no response rate, and no sample composition beyond the assertion that four year levels were represented. An estimate that cannot be placed in a distribution cannot serve as a point in one. This is the specific sense in which I find the honesty doing less work than it appears to: the manuscript acknowledges its narrowness eloquently while declining several low-cost reporting steps that would have made the narrowness informative rather than merely admitted.

I want to be equally clear about what I am *not* saying. I am not rejecting this on the ground that it is modest. A well-reported modest estimate has real value in a literature whose published effect sizes are plausibly inflated by selective reporting, and this manuscript's calibration is above the median of what I receive. My block is repairable and I mean that: reframe as a brief report or replication, supply the institutional and platform context, report a response rate against an enumerated eligible population, and the same data set becomes publishable in this journal's short-report track. That is a revision, not a rejection.

One matter overrides the ordinary sequence of review and I am flagging it for verification before any decision letter issues. Every one of the six references carries a DOI under the `10.5555` prefix, which is reserved for testing and documentation and does not correspond to a live registrant. As submitted, no cited source in this manuscript is resolvable. I am stating this as an observation requiring first-party verification, not as an allegation — I have not been able to attempt DOI resolution or database lookup within this review, and there are innocent explanations, including placeholder insertion during anonymisation. But the editorial consequence is unavoidable: if verification confirms that these works cannot be located, the manuscript's entire evidentiary and positioning base collapses, my D6 block escalates beyond repairable, and no recommendation other than return-to-author is available. Reviewers should flag this; the editorial office should resolve it deterministically before the substantive review points are weighed.

On presentation, the manuscript reads cleanly and its sections are correctly ordered, with no drift between what the abstract promises and what the body delivers. My warn on writing and structure rests on reporting apparatus rather than prose. The paper contains no numbered exhibit of any kind: a scatterplot is described as having been inspected but is not shown, the shared-variance figure is characterised verbally without ever being stated numerically, and the five-category outcome is summarised by a median category alone. For a paper whose entire result is one coefficient, the reader is entitled to see the distribution behind it. Separately, a submission of roughly 1,900 words with six references is not a full article in this journal's conventions, and it should be routed accordingly.

### S1: Disciplined refusal of causal inference, including the reverse pathway

The manuscript does not merely disclaim causality in a stock sentence; it names the specific alternative account and grants it equal standing against the data. This is rarer in this submission stream than it should be, and it is the paper's strongest asset.

**Evidence Anchor**: `text: §5 Discussion — "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"`
**Confidence**: 5 — routine editorial judgement of inferential register across a large volume of comparable submissions.

### S2: Complete reporting of the focal estimate

Coefficient, interval, exact p, exact n, a stated power floor, and an ordinal robustness check are all present in one place. Many submissions at this scope report the coefficient alone.

**Evidence Anchor**: `text: §4 Results — "r = .42, 95% CI [.30, .52], p < .001, n = 214"`
**Confidence**: 5 — direct inspection against standard correlational reporting expectations.

### S3: Substantive rather than boilerplate limitations section

The limitations name design-specific threats, including voluntary-response bias, rather than the generic three sentences that usually occupy this slot.

**Evidence Anchor**: `text: §6 Limitations — "response was voluntary, so students who engage more with institutional channels may be overrepresented"`
**Confidence**: 4 — comparative judgement against the limitations sections I routinely handle.

### S4: No claim drift between abstract, results, and conclusion

The abstract's characterisation of the finding matches what the results report and what the conclusion asserts. Over-claim inflation between abstract and body is one of the commonest structural faults at this scope, and it is absent here.

**Evidence Anchor**: `text: Abstract — "The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates"`
**Confidence**: 5 — direct cross-section comparison of the three summary statements.

### W1: The entire reference apparatus is unresolvable as submitted

All six references carry DOIs under the `10.5555` prefix, which is reserved for testing and example use and resolves to no registrant. A reader cannot retrieve a single cited source, which means the manuscript's positioning against prior work, its claim of consistency with prior technology-acceptance research, and every methodological caution it attributes to Delgado, Vasquez, and Song are unverifiable. I raise this as an observation requiring first-party resolution attempts, not as a fabrication allegation; the diagnosis space includes anonymisation placeholders and a systematic formatting error. The severity reflects the state of the submitted evidentiary base, not a presumption about cause: uncorrected, it makes acceptance impossible regardless of the study's own merits, and it must be adjudicated before any other finding is weighed.

**Severity**: Critical
**Evidence Anchor**: `text: §References — "https://doi.org/10.5555/2050001" and "https://doi.org/10.5555/2050006"`
**Confidence**: 4 — the prefix pattern is directly inspectable and its reserved status is well established, but I could not attempt resolution or database lookup within this review.

### W2: The result is presented as a contribution when its only defensible framing is replication

The manuscript's declared contribution is a transparently reported association comparable with prior work. But the association in question is the single most repeatedly reported result in this literature, and the paper offers no theoretical extension, no moderator, no multivariate specification, and no novel construct. Framed as an original contribution, it is indistinguishable from settled knowledge. Framed explicitly as a replication or a brief report, the same estimate has a defensible function. The authors have selected the framing under which their own work is weakest, and the fix requires substantial repositioning of the introduction, literature review, and conclusion rather than a cosmetic edit.

**Severity**: Major
**Evidence Anchor**: `text: §2 Literature Review — "It is intended as an incremental data point, comparable with prior work"`
**Confidence**: 5 — editorial familiarity with the submission stream this manuscript enters.

### W3: The "one point in a distribution" claim is unfulfilled because no comparative metadata is reported

The paper's stated value rests on being usable by future comparative or meta-analytic readers. That use requires knowing where the point sits: national system, institutional sector, LMS platform, whether LMS access is mandatory for assessment submission, and what fraction of the eligible population responded. None of this is reported, and the response rate is not merely omitted but uncomputable, since the eligible population is never enumerated. As submitted, the estimate cannot perform the function the authors assign to it. Repairing this requires new reporting, not rewording.

**Severity**: Major
**Evidence Anchor**: `absence: §3.1 Design and participants — expected institutional and platform context (country, sector, LMS product, mandatory-use policy) plus a computable response rate against an enumerated eligible population; checked §3.1, §3.2, §3.3, §4, §6, and the Abstract`
**Confidence**: 5 — reporting requirements for comparative usability are unambiguous and the omissions are directly verifiable.

### W4: Submission format does not match the manuscript's scale

At roughly 1,900 words with six references, this is a research note submitted as a full article. It is neither developed to full-article scale nor designated as a short report, so it will be evaluated against expectations it was never built to meet. The substance survives the mismatch; only the track changes.

**Severity**: Minor
**Evidence Anchor**: `absence: manuscript-level format designation — expected either an explicit short-report or research-note label or full-article-scale development of literature and analysis; checked Abstract, §1, §2, §5, and the six-entry reference list`
**Confidence**: 5 — direct measurement of length and reference count against venue conventions.

### W5: No exhibits, and key quantities are described rather than reported

The manuscript contains no numbered table or figure. The analysis section states that a scatterplot was inspected, but it is not shown. The shared-variance quantity is characterised as "modest" without ever being stated numerically, obliging the reader to compute it. The five-point outcome is summarised only by a median category, so the reader cannot see whether responses cluster at a ceiling. For a paper whose entire finding is one coefficient, this is a real gap in the reporting apparatus, though remedying it requires adding a table rather than new analysis.

**Severity**: Minor
**Evidence Anchor**: `absence: §4 Results — expected a descriptive table carrying the five-category frequency distribution of the use item, the numeric shared-variance value, and the inspected scatterplot; checked §3.4, §4, and the full body for any numbered exhibit`
**Confidence**: 5 — presence or absence of exhibits and stated quantities is directly verifiable.

### W6: The single practical implication is neutralised in the sentence that states it

The only actionable statement offered to the readership is that LMS onboarding emphasising concrete usefulness may deserve institutional attention, and the same sentence withdraws it as suggested rather than proven. I do not fault the caution, which is correct. But the effect is that the manuscript leaves the reader with no residue they can act on, which weakens the case for the space it occupies in a journal whose readership includes practitioners.

**Severity**: Minor
**Evidence Anchor**: `text: §5 Discussion — "may be worth institutional attention" and "this implication is suggested by, not proven by, the present correlation"`
**Confidence**: 4 — judgement about readership utility rather than a factual defect in the text.

## SEAT — METHODOLOGY

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory, my owned dimension).** From a methodology standpoint, this dimension asks whether the study's design can actually bear the weight of the inferences drawn from it. That means an explicit, defensible sampling and recruitment procedure; a clear account of how data were collected, cleaned, and handled including missingness and exclusions; measurement instruments whose provenance and psychometric properties are stated; statistical procedures that match the design and the measurement level of the variables; effect estimates reported with uncertainty rather than bare significance verdicts; and enough procedural detail — instrument items, analysis specification, data or code availability — that an independent reader could reproduce the analysis. The bar is the field's ordinary peer-review standard, not perfection, but the burden of demonstrating rigor sits with the manuscript, not with the reviewer's charity.

**D2 — domain_accuracy (mandatory).** This dimension concerns whether the substantive claims are correct with respect to the current state of evidence in the field: whether cited prior work is characterised faithfully rather than stretched to fit, whether field-specific constructs and terminology are used with their accepted meanings, and whether reported results are factually accurate. It is owned by the domain reviewer, so I do not score it, though methodological defects can obviously have downstream domain consequences.

**D3 — argumentative_coherence (mandatory, methodology-eligible).** This asks whether the paper's central thesis holds together logically end to end: whether the stated research question, the evidence actually produced, and the conclusions asserted form a chain without gaps or reversals; whether the strength of language in the conclusions is licensed by the strength of the evidence; and whether any inferential fallacies — question-begging, equivocation between constructs, conclusions that do not follow from the reported results — undermine the argument. The domain-analysis reviewer owns it, but methodology is an eligible scorer because the most common coherence failures in empirical work are inferential over-reach from the design that was actually run.

**D4 — cross_disciplinary_relevance (high priority).** This dimension evaluates whether a reader from an adjacent field can enter the paper without insider knowledge: whether framing, key definitions, and stated implications are legible outside the immediate specialty, and whether any claims that reach across disciplinary boundaries are actually supported rather than asserted. It belongs to the perspective reviewer; I do not score it.

**D5 — writing_and_structure (normal priority).** This covers the manuscript as a document: whether its organisation serves the argument, whether the exposition is clear, whether figures and tables are well constructed and self-explanatory, and whether it conforms to the target venue's formatting and reporting conventions. It is the editor-in-chief's dimension; I do not score it.

**D6 — venue_fit_and_contribution (mandatory).** This dimension asks whether the manuscript belongs in the configured venue at all, and whether what it adds is original and consequential enough for that venue's readership rather than a restatement of settled ground. It is owned by the editor-in-chief; I do not score it.

## Scoring Plan

### D1: methodology_rigor

dimension_id: D1
what_to_look_for: Explicit sampling frame, recruitment procedure and response rate; sample size with any power or precision justification; provenance and reliability/validity evidence for every measured construct; documented handling of missing data, exclusions and outliers; analysis methods matched to the design and to the measurement level of the variables; effect estimates reported with confidence intervals or equivalent uncertainty; ethics approval and consent; and reproducibility affordances such as full item wording, analysis specification, and data or code availability.
what_triggers_block: A defect that makes the reported estimates uninterpretable or the design incapable of supporting the inferences drawn — for example an undocumented or opaque sampling and recruitment procedure with no response rate, absent or clearly mismatched statistical procedures, results reported without any uncertainty or test statistics, or measurement instruments with no stated provenance or reliability evidence for the constructs the conclusions rest on.
what_triggers_warn: Rigor gaps that are real but repairable within the existing data — for example missing-data and exclusion handling described only in passing, no sample size or precision justification, effect sizes omitted while tests are otherwise adequately reported, partial instrument documentation, or reproducibility affordances (item wording, analysis specification, data availability) that are incomplete rather than absent.
what_triggers_fatal: Evidence that the reported analysis could not have produced the reported numbers or that the data provenance is not credible — for example internally contradictory sample sizes or degrees of freedom that cannot be reconciled anywhere in the manuscript, statistics that are arithmetically impossible given the stated design or scale range, or an analysis described as performed on data the stated collection procedure could not have yielded.

### D3: argumentative_coherence

dimension_id: D3
what_to_look_for: A traceable chain from research question to design to reported results to conclusions; conclusions whose causal and generalisation strength is licensed by what a cross-sectional self-report design can actually establish; consistent use of each construct across introduction, methods, and discussion without silent redefinition; stated limitations that are actually reflected in how the claims are worded; and no reliance on premises the study itself was supposed to test.
what_triggers_block: A central inferential break that undermines the paper's main thesis — for example causal or directional conclusions asserted from associational evidence, generalisation to populations the sampling procedure cannot reach, or a headline conclusion that the reported results do not support even on a charitable reading.
what_triggers_warn: Localised coherence slippage that does not topple the thesis — for example discussion language that drifts stronger than the results section warrants, a construct used with slightly shifting meaning between sections, limitations acknowledged but not carried into the phrasing of the claims, or a secondary claim left without supporting evidence.
what_triggers_fatal: Direct self-contradiction at the core of the argument that no revision short of a different study could resolve — for example a stated conclusion that reverses the direction of the paper's own reported finding, or a thesis whose supporting premise is asserted on the basis of the conclusion it is meant to establish.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

contract_role: methodology

## Dimension Scores

### D1: methodology_rigor
score: block
trigger: "measurement instruments with no stated provenance or reliability evidence for the constructs the conclusions rest on"
block_class: repairable

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: warn
trigger: "discussion language that drifts stronger than the results section warrants"

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

This manuscript is unusual among single-site LMS surveys in that its *statistical* reporting is close to exemplary while its *measurement and sampling* reporting is thin enough to make the headline estimate hard to interpret. That asymmetry is the whole methodological story, and I want to state it plainly before enumerating findings: the authors have done the reporting-standards work (interval estimate, exact n, ordinal robustness check, pre-analysis distributional inspection, honest limitations) and have not done the design-documentation work (sampling frame, response rate, instrument provenance, outcome-measure psychometrics, item wording, data availability). A correctly computed confidence interval placed around a quantity of unknown provenance does not become a trustworthy quantity; it becomes a precise-looking one. My block on D1 rests on that gap, not on any arithmetic error — I re-derived the interval and the Fisher-z power calculation myself and found the reported numbers internally consistent apart from the borderline power claim noted in W5.

Two defects independently reach the block threshold I set out in advance. The first is the sampling architecture: eligibility is asserted as "all enrolled undergraduates," but that population is never enumerated, recruitment was a broadcast announcement over a three-week window, and no response rate is reported or computable from anything in the manuscript. The analyzed 214 are therefore a voluntary-response sample of unknown coverage from an unquantified frame, yet the paper attaches a 95% confidence interval — a sampling-theory object presupposing a defined population and a known selection mechanism — and offers the resulting estimate for comparison against prior studies. The second is the outcome measure: a single five-point frequency item with no provenance, no reliability estimate, no validity evidence, and no reported frequency distribution, carrying the entire dependent side of the sole reported result. The paper's own literature review cites Vasquez (2020) on self-report/log divergence and then declines to act on that caution in the design or in the analysis.

On the analytic choices themselves I am largely satisfied. Pearson with a Spearman cross-check on a five-category ordinal outcome is a defensible pairing, the near-convergence (r = .42, ρ = .40) does the work claimed of it, and the scatterplot-based checks on linearity, monotonicity, outliers, and symmetry are reported rather than merely assumed. What is missing is any acknowledgment that a five-category outcome attenuates the observed coefficient by an unknown amount, and any consideration of a polyserial or polychoric estimate that would bound that attenuation. Because the paper positions itself as contributing "one point in a distribution" comparable with prior estimates, attenuation of unknown magnitude is not a technicality — it directly degrades the one use the estimate is offered for. The same applies to common-method variance: predictor and outcome were collected from the same respondents, in the same instrument, at the same moment, which inflates the association in the opposite direction. Neither bias is quantified, neither is mentioned, and they do not cancel in any known way.

On D3 I score warn rather than block. The central chain — narrow correlational question, correlational design, correlational result, correlational conclusion — holds, and it holds better than most manuscripts of this type. The authors name the reverse-causal pathway, refuse causal verbs, relabel the construct as *perceived* rather than actual use, and disclaim generalisation. That restraint is real and I credit it in S3. The warn is driven by two localised slippages: a practical recommendation whose logic presupposes the very direction the same paragraph declines to assert (W7), and a comparability claim asserted against a literature the paper itself describes as heterogeneous in effect size (W8). I have deliberately scored the "previously validated instrument" equivocation between the Abstract and §3.2 under D1 as a measurement-documentation defect (W2) rather than counting it twice as a coherence defect; the underlying problem is evidentiary, not rhetorical.

One matter outside my scoring lane, referred rather than scored: every reference carries a DOI under the 10.5555 prefix, which is not a live registrant prefix. That is a citation-provenance question belonging to the domain and editorial seats, and I make no finding on it here; I note only that it does not bear on my D1 block, which rests entirely on the study's own design documentation and would stand unchanged if every reference resolved cleanly.

### W1: Sampling frame unenumerated and response rate neither reported nor computable, while a sampling-theory interval is attached to the estimate
The manuscript states that all enrolled undergraduates were eligible, but never gives the size of that population, so no response rate exists anywhere in the paper and none can be reconstructed by a reader. Recruitment was a broadcast through the course-announcement channel — a mechanism that self-selects on precisely the behaviour being measured, since students who check institutional announcements are plausibly the students who access the LMS more. The Limitations section names this ("students who engage more with institutional channels may be overrepresented") but naming a selection mechanism is not characterising it. Uncorrected, the reported r = .42 and its interval have no defined population referent, which defeats the paper's stated function of supplying an estimate comparable with prior work and situatable "as one point in a distribution." The repair is available from institutional data at low cost: report the eligible N, the achieved response rate, the year-level and discipline composition of respondents against the enrolled population, and either justify the interval or reframe it explicitly as descriptive of the achieved sample.
**Severity**: Critical
**Evidence Anchor**: absence: §3.1 Design and participants — expected eligible-population size and a computable response rate with respondent-versus-population composition; checked §3.1, §3.4 Analysis, §6 Limitations, and the Abstract
**Confidence**: 5 — survey sampling and non-response reporting are my primary review area; the absence is verifiable by exhaustive reading of a 1,900-word manuscript.

### W2: Instrument adaptation undocumented and the original instrument's validation transferred to the modified version without argument
Section 3.2 reports that a six-item scale was "adapted from Costa and Wren (2019)," and the Abstract upgrades this to an "adapted, previously validated instrument." What was adapted is never stated: item deletions, rewording, referent changes from a generic platform to this institution's LMS, or response-format changes each have different consequences for whether the original validation evidence carries over. Cronbach's α = .88 establishes internal consistency in this sample and nothing else — it speaks to neither dimensionality nor structural validity, and a unidimensional six-item scale and a two-factor scale can both produce α near .88. No factor structure, no item-level means or loadings, and no verbatim item wording are given, so a reader cannot judge what construct the composite indexes or reproduce the measure. For a paper whose contribution is a comparable point estimate, the measure must be reconstructable; here it is not.
**Severity**: Major
**Evidence Anchor**: text: §3.2 "a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"
**Confidence**: 5 — survey psychometrics and the limits of coefficient alpha as validity evidence are within my core competence.

### W3: Single-item ordinal outcome with no distribution, no reliability, and unaddressed attenuation
The dependent variable is one five-point frequency item whose categories ("rarely or never" through "several times daily") are neither equidistant nor plausibly linear in actual access counts. Only a median category is reported; the full frequency distribution is withheld, so a reader cannot assess floor or ceiling concentration — and given that the sample was recruited through the LMS-adjacent announcement channel, concentration in the upper categories is likely and would itself compress the observable association. No reliability can be estimated for a single item, and the manuscript neither bounds the resulting attenuation nor reports a polyserial or polychoric alternative that would. The consequence is directional and unquantified: r = .42 is an attenuated estimate of an unknown parameter, simultaneously inflated by common-method variance from same-instrument collection of both variables. The minimum repair is the full category distribution plus a polyserial estimate alongside the Pearson coefficient; the strong repair is validation of the item against the institution's LMS access logs in a subsample.
**Severity**: Major
**Evidence Anchor**: text: §3.2 "captured with a single five-point frequency item asking how often the respondent accessed the LMS in a typical week"
**Confidence**: 5 — analysis of ordinal and single-item measures, including attenuation and polychoric estimation, is my declared specialty.

### W4: Data-cleaning pipeline undocumented, and the deduplication step is operationally inconsistent with the stated anonymity procedure
The 233→214 reduction is reported as a bare arithmetic pipeline: 14 incomplete submissions and 5 duplicates removed. No criterion for "incomplete" is given (any missing item, or missing on analysis variables?), no comparison of excluded against retained cases is offered, and no mechanism for identifying duplicates is described. That last omission is not merely a documentation gap: removing duplicate submissions requires some persistent marker — session token, IP address, browser fingerprint, or an SSO handle — yet §3.3 asserts that no identifying information was collected and that responses could not be linked to individual students. Both statements cannot hold in their strongest reading. There are innocent reconciliations (a survey-platform session cookie identifies a browser, not a person; duplicates may have been detected by response-pattern matching), but the manuscript supplies none, so a reader cannot verify that the analyzed dataset was constructed as described, nor that the anonymity representation made to participants on the consent landing page was accurate. I flag this as a data-provenance documentation failure within my lane and leave the ethics-governance dimension to the seat that owns it.
**Severity**: Major
**Evidence Anchor**: text: §3.1 "14 incomplete submissions and 5 duplicate entries were removed" against §3.3 "No identifying information was collected, and responses could not be linked back to individual students"
**Confidence**: 4 — the inconsistency is plain on the face of the text; I cannot rule out an undisclosed non-identifying deduplication method, which is precisely what the manuscript must state.

### W5: Power statement overstated at the stated threshold
Section 3.4 claims greater than .80 power to detect r ≥ .19 at α = .05, two-tailed, with n = 214. By the Fisher-z approximation the required n at exactly r = .19 is approximately 216, giving observed power near .795 rather than above .80. The error is small and does not affect any substantive conclusion, but a power claim is a precision claim, and this one is stated in the direction that flatters the design. The clean fixes are to restate the detectable effect at the achieved n (r ≈ .191 at .80 power), or to report the achieved power at r = .19 as approximately .79, or to specify the software and method used so the discrepancy is adjudicable.
**Severity**: Minor
**Evidence Anchor**: text: §3.4 "the study had greater than .80 power to detect a correlation of r >= .19 at alpha = .05 (two-tailed)"
**Confidence**: 4 — recomputed independently by Fisher-z; small differences remain possible across power software conventions.

### W6: Reproducibility affordances absent rather than merely incomplete
No verbatim item wording is provided for either measure, no analysis software or version is named, no analysis script is offered, and there is no data availability statement. For a two-variable correlational analysis the analytic burden is light, which makes the omission harder to justify rather than easier: a de-identified 214×7 matrix could be deposited without residual disclosure risk, and doing so would let any future meta-analyst recompute the estimate under alternative measurement assumptions. As written, an independent reader can verify neither the composite construction nor the coefficient, and the manuscript's own framing — an incremental data point offered for comparison — depends on exactly that verifiability.
**Severity**: Minor
**Evidence Anchor**: absence: §3.2 and §3.4 — expected verbatim item wording, analysis software and version, and a data or code availability statement; checked §3.2, §3.4, §7 Conclusion, and the reference list
**Confidence**: 5 — reporting-standards compliance for correlational research is an area in which I review routinely.

### W7: Practical implication presupposes the causal direction the same paragraph declines to assert
Within a single Discussion paragraph the manuscript states that the reverse pathway (use raising perceived usefulness) is "equally consistent with the data," and then recommends onboarding designed to raise perceived usefulness as a lever worth institutional attention. The recommendation is intelligible only under the forward pathway; under the reverse pathway an onboarding intervention targeting perception would be expected to do nothing to behaviour. The double hedge ("may be worth," "suggested by, not proven by") softens the assertion without repairing the underlying asymmetry, and the supporting citation (Whitfield, 2019) is a practitioner account introduced nowhere in the Literature Review, so the claim leans on a source the reader has not been given grounds to weigh. Either derive the implication symmetrically — noting that under the reverse pathway the actionable lever is structured early exposure, not perception-shaping — or drop it.
**Severity**: Minor
**Evidence Anchor**: text: §5 "may be worth institutional attention, a possibility also raised in practitioner accounts of digital-environment onboarding (Whitfield, 2019)"
**Confidence**: 4 — the internal tension is legible from the text; reasonable reviewers may read the hedging as sufficient.

### W8: Consistency-with-prior-work claim asserted without any numeric comparison
Both the Abstract and the Discussion assert that the finding is consistent with prior technology-acceptance research, but no prior coefficient, interval, or range is reported anywhere for comparison. The manuscript's own Literature Review states that effect sizes vary across samples and instruments and cites Song (2018) on cross-institution variability, which makes "consistent with" nearly unfalsifiable as used here: an estimate can be consistent with a heterogeneous literature almost regardless of its value. Since positioning this estimate against prior estimates is the paper's stated contribution, the comparison should be made explicitly — report the coefficients from the cited studies and state whether .42 [.30, .52] overlaps them — or the claim should be weakened to a statement of direction only.
**Severity**: Minor
**Evidence Anchor**: text: §5 and Abstract "consistent with prior technology-acceptance research"
**Confidence**: 4 — the absence of comparison values is verifiable from the text; the cited sources' actual coefficients were not independently checked.

### S1: Uncertainty reporting is complete and the ordinal robustness check is the correct one
The result is reported as a coefficient with a 95% confidence interval, an exact p value, and the sample size, and §3.4 pre-commits to that reporting format rather than delivering it opportunistically. The Spearman cross-check is the appropriate robustness test for an ordinal outcome, and the near-convergence with the Pearson estimate genuinely supports the inference drawn from it. I re-derived the interval by Fisher's z and confirm it is correct for r = .42 at n = 214. This is above the median for the genre and should be preserved through revision.
**Evidence Anchor**: text: §4 "The Spearman robustness check yielded a comparable coefficient (ρ = .40), indicating that the association did not depend on the parametric assumption"

### S2: Distributional assumptions were inspected and the inspection was reported
Most correlational manuscripts of this length assert linearity implicitly by choosing Pearson. This one reports that linearity, monotonicity, bivariate outliers, and marginal symmetry were checked before the coefficient was interpreted. The check would be stronger if the scatterplot were shown, but reporting that it was performed, and what it showed, is a real and uncommon discipline.
**Evidence Anchor**: text: §3.4 "Scatterplot inspection showed an approximately linear, monotonic association with no extreme bivariate outliers"

### S3: Limitations are binding rather than decorative, and the inferential language is consistently calibrated to the design
The Limitations section names the four constraints that actually bind this design — single site, self-report in place of log data, cross-sectional timing, and voluntary response — and, unusually, those constraints are carried into how the claims are worded elsewhere rather than quarantined in §6. The construct is relabelled as *perceived* use in §3.2 and held there; the reverse-causal pathway is named in the Discussion rather than buried; the Conclusion declines the causal reading explicitly. This calibration is why D3 is a warn and not a block, and it should not be traded away in revision under pressure to make stronger claims.
**Evidence Anchor**: text: §6 "response was voluntary, so students who engage more with institutional channels may be overrepresented"

## SEAT — DOMAIN

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory, methodology role).** This dimension asks whether the study's architecture holds up under the scrutiny a competent peer reviewer in this field would apply: whether the design can actually answer the question posed, whether sampling and data collection are described with enough specificity to be evaluated, whether statistical treatment matches the measurement level and design, and whether enough procedural detail exists that another team could repeat the work. From my seat as the domain reader I note that methodology quality and domain accuracy interact — an inference that overreaches a design is also usually a misstatement about what the field's evidence supports — but the formal scoring of this dimension is not mine to make, and I will not issue a score for it.

**D2 — domain_accuracy (mandatory, domain role).** This is my owned dimension. It asks whether the manuscript's substantive claims are consistent with what the current body of evidence in educational technology and higher education actually shows; whether the prior literature it invokes is characterised faithfully rather than flattened, inflated, or attributed to work that says something different; and whether the field's technical vocabulary, constructs, instruments, and reported quantities are used correctly. Three distinct failure surfaces live here: misrepresented antecedent work, misused or conflated domain constructs, and internally or externally inconsistent numerical and terminological reporting of results.

**D3 — argumentative_coherence (mandatory, da/methodology roles).** This concerns whether the paper's central thesis stays consistent with itself from framing through discussion, whether the evidence actually adduced carries the weight the conclusions place on it, and whether any reasoning defect is severe enough to undercut the main argument rather than merely blemish a side passage. My role is not eligible to score it, so I will only note domain-side observations that a coherence reviewer might use.

**D4 — cross_disciplinary_relevance (high priority, perspective role).** This asks whether a reader from an adjacent field can follow the framing, whether specialist terms are defined at the point they matter, and whether any claim that reaches beyond the home discipline is backed rather than asserted. Not scored by me.

**D5 — writing_and_structure (normal priority, eic role).** This covers organisation, exposition clarity, quality and self-sufficiency of figures and tables, and conformity to the venue's format conventions. Not scored by me.

**D6 — venue_fit_and_contribution (mandatory, eic role).** This asks whether the manuscript belongs in the configured venue and whether it advances something original and consequential for that readership rather than restating settled ground. Not scored by me.

## Scoring Plan

### D2: domain_accuracy

dimension_id: D2
what_to_look_for: Whether cited prior work is represented as it actually stands in the educational technology and higher education literature; whether domain constructs (for example acceptance-model constructs, perceived usefulness, behavioural intention, self-reported versus system-logged use) are defined and used in their accepted sense rather than conflated or silently redefined; whether instrument provenance, adaptation, and psychometric claims match what the source instruments support; whether reported quantities, effect magnitudes, and directional statements are internally consistent and consistent with established findings; and whether the strength of causal or generalising language is licensed by the evidence class the design produces.
what_triggers_block: A substantive domain claim that is contradicted by the evidence base or by the cited source itself — for example attributing a finding to prior work that the source does not report, treating a self-report measure as if it established actual system use, or asserting a construct relationship that established results in the field contradict — where the error is load-bearing for at least one stated conclusion.
what_triggers_warn: Domain imprecision that a specialist would flag but that does not overturn a conclusion — loose or drifting construct definitions, missing provenance for an adapted instrument, dated or thin literature grounding for a specific assertion, overstated but recoverable generalisation language, or terminology used inconsistently across sections.
what_triggers_fatal: Pervasive domain misrepresentation that makes the manuscript unsalvageable by revision — fabricated, non-existent, or systematically fictitious attributions to prior work; results that are mutually contradictory across the manuscript in ways no correction can reconcile; or a core construct so fundamentally misunderstood that the entire reported analysis measures something other than what the paper claims to measure.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

contract_role: domain

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: block
trigger: "attributing a finding to prior work that the source does not report"
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

I reviewed this manuscript from the standpoint of the higher-education technology-adoption literature: whether the prior work it invokes is represented as that work actually stands, whether acceptance-model constructs are used in their accepted sense, and whether the paper delivers the kind of estimate it says it is contributing.

The manuscript's inferential discipline is genuine and I want to record that first, because it is uncommon in this literature. The paper does not slide from correlation to causation, it names the reverse-causal pathway rather than burying it, it labels its outcome as perceived rather than actual use in the title, abstract, measures, and limitations alike, and it declines to describe itself as a model test. Those are four separate places where papers in this genre routinely overreach, and this one does not. That restraint is real and is the strongest thing here.

The blocking problem is the evidentiary base those careful claims rest on. All six references carry DOIs under the `10.5555` prefix with strictly sequential suffixes `2050001` through `2050006`. Two things follow from the manuscript's own text, without external lookup. First, DOI prefixes are assigned per registrant; six works appearing in six different journals cannot share one prefix, and `10.5555` in particular is the reserved test/example prefix rather than a live registrant. Second, five of the six journal titles are near-miss variants of real journals rather than journals I can identify — *British Journal of Educational Technology Studies* against the actual *BJET*, *Computers & Education Review* against *Computers & Education*, *Journal of Educational Technology Research* against *ETR&D*, *Educational Measurement Quarterly* against *Journal of Educational Measurement* / *Educational Measurement: Issues and Practice*, and *Higher Education Practice* against nothing I recognise. Only *International Journal of Learning Technology* exists, and the Song (2018) article placed in it at 13(1), 55–69 is not one I can identify. I have read this literature for two decades and none of these six author–journal pairings is familiar.

I am flagging this rather than adjudicating it, per the division of labour in this review. My calibrated position: the DOIs as printed are certainly not resolvable, and my domain judgment is that the reference list is fabricated. I have not performed first-party DOI resolution, so I have scored this block as repairable rather than fatal. If deterministic resolution confirms these works do not exist, the correct handling is not a revision request — it is rejection with an integrity referral, and every other point in this review becomes moot. The editor should resolve that question before weighing anything else I have written.

Setting the resolution question aside, several domain-accuracy problems remain that would survive a citation correction and would need substantive work.

### W1: Reference base is structurally non-resolvable and carries the signature of fabrication, and every positioning claim rests on it

Six independently published works cannot share a DOI prefix, and `10.5555` is a reserved test prefix in any case. Combined with sequential suffixes and five of six journal titles being plausible-sounding variants of real journals, the pattern is that of synthetically generated citations. This is load-bearing rather than cosmetic: the reverse-causality caution is attributed to Delgado (2020), the self-report/log divergence to Vasquez (2020), the cross-campus variability framing to Song (2018), and the definition of the paper's central construct to Costa & Wren (2019). The instrument itself is described as adapted from Costa & Wren (2019). If those sources cannot be resolved, the Literature Review, the Discussion's consistency claim, the instrument's provenance, and the paper's self-description as "one point in a distribution" all lose their footing simultaneously. There is no reading on which the manuscript is acceptable while this is unresolved.

**Severity**: Critical
**Evidence Anchor**: `text: References "https://doi.org/10.5555/2050001" and "https://doi.org/10.5555/2050006"`
**Confidence**: 5 — DOI prefix allocation is deterministic and checkable from the manuscript text; my 4/5 confidence attaches to the fabrication inference, which rests on domain familiarity with these journal titles rather than on resolution.

### W2: The foundational acceptance literature is absent, and the definition of perceived usefulness is Davis's but attributed elsewhere

The paper's central construct originates in a specific, well-known operationalisation, and the manuscript's gloss — "the degree to which a person believes a technology will help them perform better" — is a close paraphrase of that canonical definition. It is attributed to two 2019/2020 sources instead. Davis (1989), Davis, Bagozzi & Warshaw (1989), Venkatesh & Davis (2000), and Venkatesh et al. (2003) are absent, as is the information-systems critique of TAM (Bagozzi 2007; Benbasat & Barki 2007) that bears directly on this paper's core move of extracting one path from a specified model. A reader cannot tell from the manuscript that "perceived usefulness" is a technical term with a defined lineage rather than a plain-language phrase. Repairing this is not a matter of adding citations; the Literature Review would need to be rewritten so that the construct is anchored where it actually comes from.

**Severity**: Major
**Evidence Anchor**: `text: §2 "the degree to which a person believes a technology will help them perform better"`
**Confidence**: 5 — direct familiarity with the origin and standard wording of the construct.

### W3: "Consistent with prior technology-acceptance research" is asserted without any stated comparison quantity

Consistency with a body of evidence is a quantitative claim, and the manuscript nowhere states what that body reports. No comparison range, no meta-analytic estimate, no indication of whether prior coefficients cluster near .42 or elsewhere. This matters more than it might in another paper, because the manuscript's whole contribution logic is comparability: it offers itself as "an incremental data point, comparable with prior work." The reader is asked to accept the comparison without being shown the distribution the point is supposed to sit in. The problem is compounded by an unstated distinction the acceptance literature treats as material — the perceived-usefulness-to-intention path and the perceived-usefulness-to-use path have systematically different magnitudes, and the paper measures the latter while invoking a literature dominated by the former.

**Severity**: Major
**Evidence Anchor**: `text: §5 "consistent with prior technology-acceptance research (Costa & Wren, 2019; Ibarra & Poll, 2021)"`
**Confidence**: 4 — familiar with the reported ranges in this literature and with the intention/use path distinction.

### W4: The construct interpretation is indeterminate because institutional LMS policy is never reported

At most institutions, LMS access is required for assessment submission, material access, or attendance. Where that holds, both the perceived-usefulness rating and the frequency item partly index course structure rather than perception, and the correlation becomes substantively hard to interpret regardless of its statistical properties — perceived usefulness may be functioning as a proxy for compliance. The manuscript comes close to this itself in the Results, naming course requirements and assessment schedules as influences on reported use, but then never tells the reader whether LMS use at this institution is mandatory, discretionary, or mixed. Without that, a domain reader cannot say what construct was measured. This is answerable at essentially zero cost from institutional policy documents and should not be deferred to future research.

**Severity**: Major
**Evidence Anchor**: `absence: §3.1 Design and participants — expected a statement of institutional LMS policy indicating whether assessment submission or material access requires LMS use; checked abstract, §1, §3.1, §3.2, §4, §6`
**Confidence**: 4 — based on how LMS mandatoriness varies across institutions and how it confounds acceptance estimates.

### W5: The paper does not report the contextual detail its own comparative framing requires

The manuscript positions its estimate as one observation in a cross-institutional distribution, which is a defensible purpose. But delivering on it requires that a future comparative researcher or meta-analyst be able to code this study. They cannot. The LMS platform is never named, and Moodle, Canvas, Blackboard, and D2L differ substantially in interface, default course structure, and how much routine access they compel. No country or national system is given. "Mid-sized public university" is the entire site description. No discipline mix and no year-level distribution are reported beyond the statement that all four year levels appeared. The estimate is therefore not comparable in the sense the paper claims for it, which undercuts the specific contribution it argues for.

**Severity**: Major
**Evidence Anchor**: `absence: §3.1 site and platform description — expected LMS platform name, national or system context, and discipline and year-level composition; checked abstract, §3.1, §3.2, §4, §7`
**Confidence**: 4 — grounded in what moderator coding in this literature actually requires.

### W6: "Previously validated instrument" mischaracterises what adaptation preserves

The abstract describes the measure as "an adapted, previously validated instrument," and §3.2 repeats the provenance without specifying what was changed. Validation attaches to an instrument as administered in a population, not to a construct label, and it does not transfer intact through adaptation. The phrasing as written invites the reader to credit the adapted six-item version with evidence that belongs to a different version. I raise this narrowly as a terminology-accuracy point; the psychometric substance — dimensionality, item-level statistics, structural validity in this sample — belongs to the methodology reviewer and I defer the depth of that assessment.

**Severity**: Minor
**Evidence Anchor**: `text: Abstract "Perceived usefulness was measured with an adapted, previously validated instrument"`
**Confidence**: 4 — standard measurement-terminology usage in this field.

### S1: Self-reported use is treated as perceived engagement rather than behavioural use, consistently

The conflation of self-reported frequency with actual system use is endemic in this literature, and the manuscript avoids it at every point where the temptation arises — the title, the abstract, the measures section, the results narration, and the limitations. The measure is labelled for what it is rather than for what the authors would prefer it to be.

**Evidence Anchor**: `text: §2 "treat our self-report measure as an indicator of perceived use rather than a behavioral count"`

### S2: The bidirectional pathway is named rather than suppressed

The reciprocal relationship between perceived usefulness and use is empirically documented in longitudinal acceptance work, and cross-sectional papers in this genre routinely acknowledge it in a limitations sentence while writing the Discussion as though it did not apply. This manuscript places it in the Discussion at the point where the reader would otherwise draw a directional inference, and states the alternative as equally consistent rather than as merely possible. That is the correct domain reading of what a cross-sectional coefficient supports.

**Evidence Anchor**: `text: §5 "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"`

### S3: The scope of the claim matches the scope of the design

Papers that extract a single path from an acceptance model frequently narrate the result as though the model had been tested. This one states in the Introduction that it is doing neither, and holds that line through the Conclusion. The narrowness is declared rather than concealed, which makes the paper's actual epistemic position legible to a domain reader.

**Evidence Anchor**: `text: §1 "We do not claim to establish that perceived usefulness causes use, nor do we test a full acceptance model"`

On the path forward, one caution for whoever synthesises this panel. If the citation question resolves in the authors' favour, the remaining domain repairs — anchoring the construct in its actual lineage, stating the comparison distribution, reporting institutional LMS policy and platform, adding site and sample composition — are all achievable without abandoning the narrow correlational framing. I am not recommending that the authors build a full acceptance model. The restraint recorded in S1 through S3 is the paper's best feature, and a recommendation to specify PEOU, behavioural intention, facilitating conditions, and social influence would destroy it while adding an underpowered structural model to a literature that already has too many. The fixes I am asking for are contextual and provenance-related, not architectural.

## SEAT — PERSPECTIVE

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory, methodology-owned).** This dimension asks whether the study's design, sampling, data handling, and statistical reporting would survive scrutiny by a competent methodologist in the paper's own field, and whether enough procedural detail is disclosed that another team could repeat the work. From where I sit as the cross-disciplinary reader, methodological rigour matters because readers in adjacent fields cannot independently reconstruct the analysis; they inherit whatever the authors report. But this dimension is owned by the methodology reviewer and I do not score it.

**D2 — domain_accuracy (mandatory, domain-owned).** This dimension checks that the manuscript's substantive claims match what the field currently knows, that cited prior work is represented as its authors would recognise it, and that field-specific terms, instruments, and reported results are used correctly. Its relevance to my role is indirect: mis-stated domain facts are exactly the material that adjacent-field readers are least equipped to detect. Even so, adjudicating domain correctness belongs to the domain reviewer, and I do not score it.

**D3 — argumentative_coherence (mandatory, DA-owned).** This dimension asks whether the central thesis holds together on its own terms — whether the stated evidence actually licenses the stated conclusions, whether the inferential chain is free of gaps and fallacies, and whether the paper's own claims remain consistent from abstract to discussion. It overlaps my concerns because an argument that only coheres given unstated in-field assumptions will read as a non sequitur to outsiders, but the coherence verdict is the discourse analyst's to render, not mine.

**D4 — cross_disciplinary_relevance (high priority, my dimension).** This is the dimension I own. It asks whether the framing, the operational definitions, and the stated implications are intelligible and usable to a reader trained in an adjacent field rather than the authors' own subspecialty — and, separately, whether any claim the paper makes about relevance beyond its home discipline is actually backed by evidence in the manuscript rather than asserted. Two failure modes sit here in tension: hermetic writing that locks outsiders out, and inflated reach claims that invite outsiders in on false terms. I look for both, and I treat an unearned interdisciplinary claim as at least as serious as an under-explained one, because the former exports error while the latter merely withholds value.

**D5 — writing_and_structure (normal priority, EiC-owned).** This dimension covers organisation, exposition clarity, the quality and self-sufficiency of figures and tables, and conformity to the venue's formatting and reporting conventions. My interest overlaps at the margins — unclear prose and uninterpretable tables raise the entry cost for outsiders — but presentation quality as such is the editor's call, and I do not score it.

**D6 — venue_fit_and_contribution (mandatory, EiC-owned).** This dimension asks whether the manuscript belongs in the configured venue and whether it advances something original and consequential for that venue's readership. It brushes against my dimension whenever a paper's claimed audience is broader than its actual venue, but the fit-and-contribution judgement is reserved to the editor-in-chief, and I do not score it.

## Scoring Plan

### D4: cross_disciplinary_relevance

dimension_id: D4
what_to_look_for: Whether constructs, instruments, and outcome measures are operationally defined in terms an adjacent-field reader can reconstruct without prior subspecialty training; whether field-specific jargon, acronyms, and named frameworks are glossed at first use; whether the stated implications name the audiences and settings they are meant to travel to; and whether every claim of relevance beyond the home discipline is tied to evidence actually presented in the manuscript rather than asserted in framing or discussion.
what_triggers_block: The manuscript advances substantive interdisciplinary or generalising claims — transferability to other fields, populations, systems, or practice settings — that the presented design and data cannot support, or its core constructs remain undefined to the point that an adjacent-field reader cannot determine what was measured or what the conclusions would mean outside the authors' subspecialty.
what_triggers_warn: Framing and definitions are broadly followable but carry unglossed jargon, undefined acronyms, or unexplained named frameworks at load-bearing points; or implications are gestured at for wider audiences without specifying the conditions and boundaries under which they would hold, leaving outsiders to guess at scope.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

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
trigger: "implications are gestured at for wider audiences without specifying the conditions and boundaries under which they would hold"

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I read this manuscript from the seat of a practitioner-researcher: learning analytics and institutional research, with operational responsibility for an LMS data warehouse and a data-governance role on a research ethics committee. My assigned question is not whether the statistics are correct or whether the acceptance literature is adequately covered — those belong to other seats — but whether an adjacent-field reader can reconstruct what was measured, and whether the reach the paper claims beyond its own subspecialty is earned by what is on the page.

On the first question the manuscript does better than most. Its operational definitions are unusually legible to an outsider. The authors state plainly that the outcome is an ordinal indicator of *perceived* use rather than a behavioural count, and they flag the reverse-causal pathway in the Discussion rather than burying it in Limitations. For a reader arriving from learning analytics, where "LMS use" is a log-derived quantity by default, that disambiguation is not a courtesy — it prevents a specific and common misreading. I want that credited without hedging.

On the second question the manuscript is weaker than its own framing implies, and in a way its restraint conceals rather than repairs. The Literature Review commits the paper to a particular kind of cross-context usefulness: it invokes Song (2018) on cross-institution variability and positions itself as "one point in a distribution." That is a claim about comparability — an assertion that a reader elsewhere, in another institution or another discipline, can place this estimate alongside others. But the manuscript withholds nearly everything that would make placement possible. There is no LMS platform, no country or higher-education system, no disciplinary composition, no year-level distribution, and — most consequentially — no statement of whether LMS access is required to submit assessments at this institution. That last item is not a nicety. If access is compulsory for assessment, both variables partly index course structure rather than student perception, and the coefficient means something categorically different from the same coefficient at an institution where the LMS is optional. A comparative reader cannot tell which paper they are reading. The authors themselves gesture at this in the Results when they name "course requirements and assessment schedules" as unmodelled influences, then decline to report the institutional facts that would let a reader gauge how large that shadow is.

The paper's single outward-facing claim — that onboarding emphasising concrete usefulness "may be worth institutional attention" — is where the otherwise disciplined boundary-marking lapses. It is addressed to a different audience than the rest of the manuscript: administrators making resource decisions, not researchers accumulating estimates. To that audience it supplies no conditions of application, no counterfactual, and no indication of what magnitude of association would warrant spending. Roughly 18% shared variance between two perceptual measures collected in the same instrument from the same respondents at the same moment cannot discriminate between funding an onboarding redesign and doing nothing. The manuscript's hedge ("suggested by, not proven by") disclaims proof but does not supply scope, and scope is what a practitioner reader actually needs.

Two further gaps sit squarely in my governance lane. First, §3.3 states that no identifying information was collected and that responses could not be linked to individual students; §3.1 states that five duplicate entries were removed. Removing duplicates requires some persistent discriminator — an IP address, a session token, a browser fingerprint, an SSO handle, or a distinctive response pattern. One of these two statements is incomplete as written, and which one it is determines whether the anonymity representation shown to participants on the consent landing page was accurate. Second, the manuscript cites Vasquez (2020) to concede that self-report diverges from behavioural traces, at an institution whose own system emits per-user access logs continuously, and never says why those logs were not used. There is a good possible answer — a genuinely anonymous survey cannot be linked to identified log records without a governance mechanism the study may not have had — but the authors do not give it, so an adjacent-field reader cannot distinguish a principled constraint from an unexamined default.

Finally, an integrity observation I flag rather than adjudicate. Every one of the six references carries a DOI under the `10.5555` prefix, which is a reserved test/example prefix rather than a live registrant prefix, and the six suffixes run sequentially (2050001 through 2050006) across six ostensibly different journals and publishers. Real DOIs from six unrelated publishers do not arrive in a consecutive block. I did not attempt live resolution and make no allegation about how this arose; I am reporting what is checkable from the printed strings alone. This must be resolved by first-party verification before any recommendation on the substantive points is acted upon, because the manuscript's entire positioning claim — that its result is "consistent with prior technology-acceptance research" — rests on works a reader currently cannot retrieve.

### S1: Explicit reverse-causal disclosure in the Discussion, not only in Limitations

The bidirectionality problem is stated where a reader encounters the interpretation, rather than quarantined in a section that skimming readers skip. For adjacent-field readers who lack the tacit conventions of acceptance research, placement matters as much as presence.

**Evidence Anchor**: `text: §5 "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"`
**Confidence**: 5 — routine assessment of inferential framing in correlational reporting.

### S2: The outcome construct is explicitly demarcated from behavioural use

This single sentence blocks the most likely cross-field misreading of the paper — that "self-reported LMS use" is a proxy for logged access. Learning-analytics and institutional-research readers import log semantics by default; the authors pre-empt that.

**Evidence Anchor**: `text: §2 "treat our self-report measure as an indicator of perceived use rather than a behavioral count"`
**Confidence**: 5 — direct professional overlap with the misreading being pre-empted.

### S3: Transferability boundary named in concrete institutional terms

The Limitations section identifies the specific institutional attributes along which the estimate may not travel, rather than issuing a generic single-site caveat. That specificity is what lets an outside reader judge whether their setting is inside or outside the boundary.

**Evidence Anchor**: `text: §6 "the study drew on a single mid-sized university, so the results may not generalize to institutions of different size, sector, or student profile"`
**Confidence**: 4 — familiar with how comparative readers assess site transferability.

### S4: Plain-language restatement of the coefficient

The Results give a non-technical gloss of what the association means before qualifying its size. A reader from policy, administration, or a non-quantitative discipline can extract the finding without decoding the statistic.

**Evidence Anchor**: `text: §4 "In plain terms, students who perceived the LMS as more useful tended to report using it more often"`
**Confidence**: 4 — routine judgement about accessibility to non-specialist audiences.

### W1: Every cited reference carries a reserved test DOI prefix with sequential suffixes

All six references resolve to `10.5555/2050001` through `10.5555/2050006`. The `10.5555` prefix is a reserved test/example prefix, not a live registrant prefix, and six consecutive suffixes spanning six different journals and publishers is not a pattern real registration produces. The manuscript's positioning claim — consistency with prior technology-acceptance research — and its entire methodological warrant (the "previously validated" instrument, the self-report/log divergence caution, the cross-institution variability framing) all rest on works that a reader cannot currently retrieve. Uncorrected and unexplained, this alone forecloses acceptance regardless of the merits of anything else in the paper. I flag it; verification and adjudication belong to the domain seat and the editor. I did not attempt live DOI resolution and make no claim about origin.

**Severity**: Critical
**Evidence Anchor**: `text: §References, "https://doi.org/10.5555/2050001" and "https://doi.org/10.5555/2050006"`
**Confidence**: 4 — working familiarity with DOI registration conventions from repository and metadata governance work; live resolution not performed by me.

### W2: Anonymity claim and duplicate-removal procedure cannot both be complete as written

Section 3.3 tells the reader that no identifying information was collected and that responses could not be linked back to individual students. Section 3.1 tells the reader that five duplicate entries were removed. Deduplication requires a persistent discriminator of some kind. The manuscript does not disclose what it was, whether the ethics submission covered it, or whether the consent landing page described data collection accurately to participants. This is a reproducibility problem for any reader trying to reconstruct the procedure and a governance problem for any ethics reviewer assessing whether the anonymity representation was met. Resolution requires the authors to state what was actually collected and to confirm the ethics record matches; depending on the answer, the participant-facing anonymity claim may need correcting.

**Severity**: Major
**Evidence Anchor**: `text: §3.3 "No identifying information was collected, and responses could not be linked back to individual students." with §3.1 "5 duplicate entries were removed"`
**Confidence**: 5 — direct operational experience with survey deduplication mechanics and ethics-committee anonymity review.

### W3: The comparability claim is unsupported because the contextual metadata a comparative reader needs is absent

The manuscript explicitly positions its estimate as "one point in a distribution" of cross-institution results, which is a claim that the number is usable by researchers elsewhere. Delivering on it requires reporting the LMS platform, the national system and sector, the disciplinary and year-level composition of the sample, and — decisively — whether LMS access is required for assessment submission at this institution. None appears. Without the mandatory-use fact in particular, a reader cannot tell whether the coefficient indexes student perception or institutional course design, which means it cannot be meaningfully compared with an estimate from a site with a different policy. The paper thus asserts cumulative usefulness while withholding the information that would make it cumulative. Repair requires new reporting, not rewording.

**Severity**: Major
**Evidence Anchor**: `absence: §3.1 Design and participants — expected LMS platform, national system and sector, sample composition, and whether LMS access is required for assessment submission; checked Abstract, §1, §3.1, §3.2, §3.3, §3.4, §4, §6`
**Confidence**: 5 — this is the metadata I require operationally when benchmarking an institutional estimate against published ones.

### W4: The practice-facing implication names no conditions, population, or decision it could inform

The onboarding implication is the manuscript's only claim addressed to a non-research audience, and it is the one place where the paper's otherwise careful boundary-marking does not operate. It does not specify which students, which courses, what the alternative use of the resources would be, or what magnitude of association would justify acting. Between two perceptual self-reports collected in one instrument at one moment, a moderate correlation cannot discriminate any resource-allocation option. The hedge that follows disclaims causal proof but supplies no scope, and scope is the missing element for the audience the sentence reaches toward. The claim appears in the Abstract as well, so repair means rewriting the implication in both places — either bounding it to a specific decision context or withdrawing it in favour of a research-facing next step.

**Severity**: Major
**Evidence Anchor**: `text: §5 "the finding offers modest support for the intuition that LMS onboarding" and "may be worth institutional attention"`
**Confidence**: 4 — sustained practitioner experience translating correlational findings into institutional investment decisions.

### W5: The load-bearing theoretical tradition is invoked but never named or explained

The Abstract, Literature Review, and Discussion all lean on "technology-acceptance research" as the standard against which the result is judged consistent. The tradition is never named, its model never identified, and "perceived usefulness" is glossed only in passing. A reader from an adjacent field — educational measurement, information systems outside the acceptance lineage, higher-education policy — has no way to locate the body of work being invoked or to judge what consistency with it would mean. One or two sentences naming the framework and its provenance would close this.

**Severity**: Minor
**Evidence Anchor**: `text: Abstract "The association was consistent with prior technology-acceptance research"`
**Confidence**: 4 — judgement about outsider legibility, from repeatedly briefing non-specialist institutional audiences.

### W6: The frequency categories are reported in a form no adjacent-field reader can translate

Only a median category is given for the outcome; the full distribution is not reported. The response anchors span a range whose categories are not equidistant in any underlying access quantity, and a reader working with log data has no way to map the reported median onto sessions, page views, or active days. This blocks the most natural form of external validation available to an adjacent field — comparing the reported use profile against a known log-derived profile. Reporting the full frequency distribution would cost one table and would make the measure interpretable outside the survey tradition.

**Severity**: Minor
**Evidence Anchor**: `text: §4 "Self-reported LMS use had a median category of" with §3.2 "1 = rarely or never to 5 = several times daily"`
**Confidence**: 4 — routine work reconciling self-reported engagement categories against LMS event logs.

### W7: The reason log data were not used is never stated, so readers cannot tell constraint from default

The manuscript concedes that self-reports diverge from behavioural traces and cites a source for that divergence, at an institution whose LMS emits per-user access logs as a matter of course. It never says why the logs were not used. There is a plausible and defensible answer — anonymous collection may have made linkage impossible without a governance mechanism the study lacked — and stating it would convert an apparent omission into a documented design constraint. Leaving it unstated invites adjacent-field readers to conclude the option was never considered.

**Severity**: Minor
**Evidence Anchor**: `absence: §3.4 Analysis and §6 Limitations — expected a stated reason why institutional LMS access logs were not used or linked; checked §3.1, §3.3, §3.4, §5, §6, §7`
**Confidence**: 5 — direct operational knowledge of what LMS log access and linkage require in practice.

## SEAT — DA

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor.** This dimension asks whether the study's design and its statistical machinery would survive scrutiny from a competent methodologist in the paper's own field. Adversarially, I would be hunting for whether the sampling frame is defensible, whether the analytic choices match the data structure, whether reported statistics are complete enough to be checked rather than merely asserted, and whether anyone else could reproduce the reported numbers from what is disclosed. Failure here looks like undisclosed exclusions, statistics reported without the quantities needed to interpret them, or an inference procedure that does not match the design that generated the data. I am not the owner of this dimension and am not eligible to score it, so my concern with it is only to understand what the panel's methodologist is responsible for catching.

**D2 — domain_accuracy.** This dimension asks whether the paper's substantive claims are true in the field's current state of evidence, whether cited prior work is characterised as its authors would recognise, and whether specialised terms and reported results are used correctly rather than loosely. The adversarial posture is to treat every attribution to prior literature as a potentially misquoted one and every domain term as potentially misapplied. Failure looks like citing a source for a claim it does not make, misdescribing an established construct, or reporting a result that contradicts what the underlying data can show. This dimension belongs to the domain reviewer, not to me, so I will not score it.

**D3 — argumentative_coherence.** This is the dimension I own. It asks whether the manuscript's central thesis holds together on its own terms: whether the conclusion the paper draws is the conclusion its evidence licenses, whether the chain from data to claim has any missing links, and whether the paper commits reasoning errors serious enough that the main argument does not survive them. Adversarially, my job is to reconstruct the paper's argument in its strongest form and then test whether the stated evidence actually carries it — checking for inferential overreach beyond what the design permits, for conclusions that quietly change the claim between abstract and discussion, for circularity where a construct is used to explain itself, and for internal contradictions between sections. A paper can be methodologically clean and factually accurate and still fail here if the thesis it advertises is not the thesis its results support.

**D4 — cross_disciplinary_relevance.** This dimension asks whether a reader from a neighbouring field could follow the framing, understand the operative definitions without insider knowledge, and see why the implications matter beyond the paper's immediate subfield — and whether any claim reaching across disciplinary lines is actually backed rather than gestured at. Adversarially the test is whether interdisciplinary language is doing real work or decorating a narrow result. This dimension is owned by the perspective reviewer and is outside my scoring role.

**D5 — writing_and_structure.** This dimension asks whether the manuscript is organised so that its argument is findable, whether the prose explains rather than obscures, whether figures and tables are legible and self-sufficient, and whether the submission follows the venue's stated conventions. Adversarially, the question is whether apparent clarity is real or whether smooth prose is concealing gaps. The editor-in-chief role owns this dimension; I will not score it.

**D6 — venue_fit_and_contribution.** This dimension asks whether the manuscript belongs in the configured venue at all and whether it advances something its readership does not already have. Adversarially the test is whether the stated novelty is genuinely new or a restatement of settled knowledge, and whether the significance claimed is proportionate to what was actually done. This dimension is owned by the editor-in-chief and is outside my scoring role.

## Scoring Plan

### D3: argumentative_coherence

dimension_id: D3
what_to_look_for: Reconstruct the paper's central thesis and trace every link from reported evidence to stated conclusion, checking whether the claim asserted in the abstract, results, and discussion is the same claim throughout, whether the inference type invoked is licensed by the study design and data actually collected, whether constructs are defined independently of the outcomes they are used to explain, and whether alternative explanations the paper's own evidence cannot rule out are acknowledged rather than silently dismissed.
what_triggers_block: The central conclusion asserts a relationship or effect the presented evidence cannot establish — for example a causal or directional claim drawn from data whose structure permits only association, a generalisation to a population the reported sample cannot support, or a construct used both as predictor and as its own explanation — such that the paper's headline thesis fails unless the claim is restated or new evidence is supplied.
what_triggers_warn: The core argument is sustainable but has repairable weaknesses: hedging that varies across sections so the strength of the claim drifts, a supporting sub-claim advanced without a stated warrant, an alternative explanation left unaddressed that does not by itself sink the main thesis, or a discussion that overstates practical implications relative to the results section while the primary finding still stands.
what_triggers_fatal: The manuscript's argument is internally self-contradictory in a way no revision can reconcile — the stated results contradict the stated conclusion, or two load-bearing premises cannot both be true, or the thesis is unfalsifiable as constructed so that no reported evidence could bear on it, leaving nothing coherent for revision to repair.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

contract_role: da

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: block
trigger: "a generalisation to a population the reported sample cannot support"
block_class: repairable

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

Let me first state the manuscript's argument in its strongest form, because the case against it is only interesting if the case for it is taken seriously. The paper claims: (a) it asked one bounded descriptive question; (b) it answered that question with a correctly computed estimate and an appropriate ordinal robustness check; (c) it refuses causal reading explicitly and names the reverse pathway itself; (d) it therefore contributes a comparable estimate to a literature whose institution-level estimates are known to vary. That is a coherent argumentative shape, and it is executed with more discipline than most submissions of this type. The inferential restraint is real and I credit it without qualification.

My challenge is that the restraint is unevenly distributed, and it thins out at exactly the points where the paper has to earn something. Three of the four load-bearing moves in the argument are hedged carefully in the body and then made without hedge where they do work: in the abstract, in the contribution claim, and in the practical implication.

Start with the abstract's closing sentence. The paper's own Literature Review commits it to the position that self-report "capture[s] perceived rather than actual engagement," and the Methods restate that the outcome is "an ordinal indicator of self-reported use." The Conclusion honours this: "Among 214 undergraduates at one university... self-reported frequency of use." The abstract does not. It reports that perceived usefulness "tracks with LMS engagement among undergraduates," dropping the perceived/behavioural qualifier and the single-institution qualifier in one sentence. This is not stylistic compression. The two qualifiers dropped are precisely the two the paper elsewhere identifies as its binding constraints, and the sentence that drops them is the sentence most likely to be read, indexed, and cited. The Discussion repeats the first half of the slide ("one of several factors bearing on engagement"). A reader who reads only the abstract receives a claim about undergraduate behaviour in general; the study licenses a claim about perceptual self-report in one self-selected sample.

Second, the contribution claim. The paper asserts consistency with prior technology-acceptance research in the abstract, the Discussion, and the Conclusion. It never reports a single prior effect size. Worse, its own framing forecloses the comparison: §2 states that "effect sizes vary across samples and instruments" and that association strengths "varied by institution." If the prior distribution is wide and unspecified, then no obtainable positive coefficient could have been inconsistent, and the consistency claim is unfalsifiable as constructed. The same defect undermines the positioning that follows from it. A paper that offers itself as "one point in a distribution" owes the reader the distribution, or at least its rough location and spread; otherwise the claim of comparability is a promise rather than a result. Related, though smaller: "a substantial body of work" in §1 is supported by exactly one citation.

Third, the onboarding recommendation. The Discussion states that the reverse pathway "is equally consistent with the data," and then, two sentences later, recommends attention to onboarding that helps students see concrete usefulness. An intervention recommendation is a directional claim; it presupposes that moving perceived usefulness moves use. If the two directions are genuinely equally supported, the data provide no differential warrant for that intervention over its converse (give students reasons to use the system and usefulness perceptions may follow). The hedge — "suggested by, not proven by" — attaches a strength qualifier to a claim whose problem is direction, not strength. The hedge does not repair the structure; it only signals awareness of it.

Fourth, and the point I most want the panel to weigh: the limitations inventory is well-constructed but selectively populated. It names single-site scope, self-report versus logs, cross-sectional design, and voluntary response. Every one of these is a limitation that bounds the finding without threatening its existence. The alternative explanation that would threaten its existence goes unnamed anywhere in the manuscript: both variables are self-reports elicited from the same respondent, in the same instrument, at the same moment, and a respondent who rates a system favourably has a general disposition to report engaging with it. Under that reading the r = .42 is not two constructs relating to each other but one self-report tendency measured twice. I am not asserting that this is what happened; I am observing that the paper's own restraint-inventory omits the one candidate that would matter most, while listing four that do not. That asymmetry is what makes the restraint read, to an adversarial eye, as partly protective rather than fully diagnostic.

Two further gaps compound the sampling argument. The eligible population is never enumerated, no response rate is reported, and the Limitations concede over-representation of institutionally engaged students. The consequence the paper never draws is that the estimate has no defined target — not the sector, not the institution, not even the institution's undergraduates. And the recruitment channel is described only as "the institution's course-announcement channel." If that channel runs through the LMS, respondents were selected on the dependent variable, and the estimate is conditioned on the outcome it reports. The manuscript does not say either way, so the reader cannot rule it out. That is one sentence of repair, but until it is written the central estimate is uninterpretable in a way the paper does not acknowledge.

On scoring. I have set D3 to block, repairable, not fatal. The block is not carried by any single finding: no defect below is individually rejection-level, and I decline to inflate one for adversarial effect. It is carried by the cumulative fact that the paper's headline claim, its contribution warrant, and its practical implication each assert more than the design delivers, and that repairing them requires restating claims rather than collecting data. Fatal would require that no revision could reconcile the argument; that is plainly not the case here — the Conclusion section already contains a correctly bounded version of the thesis, which is evidence that the authors can write the paper their data support. To flip D3 to pass I would need: the abstract restated to the Conclusion's standard of precision; prior effect sizes reported so "consistent" becomes checkable; the onboarding sentence either removed or re-derived as a hypothesis with its converse named; the shared-self-report-source explanation added to the limitations inventory; and the recruitment channel and response rate specified.

One matter outside my scoring remit that I flag and do not adjudicate. All six references carry DOIs under the 10.5555 prefix with sequential suffixes 2050001 through 2050006. Six works attributed to six different journals with six different publishers cannot share a single DOI registrant prefix, and cannot carry consecutive suffixes; that is verifiable from the reference list alone, independent of whether the works exist. If deterministic resolution confirms the entries are non-resolvable, every warrant in this manuscript that runs through prior literature collapses, including the instrument's validation, the reverse-causation caution, the self-report caution, and the entire comparability framing. I have deliberately not imported this into my D3 score: citation veracity is D2's remit and the editor's to adjudicate after verification, and folding it into my dimension would launder an external finding into an internal-coherence judgment. The synthesizer should treat C1 as conditional on verification and as superseding the substantive discussion if confirmed.

#### CRITICAL

| # | Issue | Decision impact | Evidence Anchor | Confidence |
|---|---|---|---|---|
| C1 | All six references share the 10.5555 DOI registrant prefix with consecutive suffixes, despite being attributed to six different journals and publishers. This is structurally impossible under real DOI assignment; 10.5555 is a reserved example/test prefix. | Acceptance is impossible until resolved by first-party DOI resolution. If confirmed non-resolvable, every literature-dependent warrant fails: instrument validation, the reverse-causation caution, the self-report caution, and the comparability framing. Flagged, not adjudicated: this is D2 and editorial territory. | text: References list, "https://doi.org/10.5555/2050001" through "https://doi.org/10.5555/2050006" | 5 (deterministic reading of DOI prefix and suffix structure against registration practice) |

#### MAJOR

| # | Issue | Decision impact | Evidence Anchor | Confidence |
|---|---|---|---|---|
| M1 | The abstract's closing claim drops both qualifiers the paper elsewhere treats as binding, widening from self-reported use to engagement and from one institution to undergraduates generally. | The most-read sentence states a thesis the design does not license; the correctly bounded version already exists in §7, so repair is restatement, but the core claim as advertised is unsupported. | text: Abstract, "perceived usefulness tracks with LMS engagement among undergraduates" versus §2 "perceived rather than actual engagement" | 5 (direct textual comparison of abstract against body claims) |
| M2 | Consistency with prior research is asserted three times with no prior effect size reported, while the paper's own framing says prior effect sizes vary widely, making the claim unfalsifiable as constructed. | The comparability claim is the paper's stated reason for existing; it is asserted rather than executed. Repairable by reporting prior estimates, but the contribution warrant currently rests on nothing checkable. | text: §5, "consistent with prior technology-acceptance research" and §2 "effect sizes vary across samples and instruments" | 4 (warrant analysis; partly dependent on sources I cannot verify) |
| M3 | The onboarding recommendation presupposes the perceived-usefulness-to-use direction that the Discussion declares equally consistent with its converse. The hedge qualifies claim strength, not claim direction. | A practical implication carried in the abstract is not derivable from the reported evidence; the paper's own inferential rule forbids it. Repairable by deletion or by reframing with the converse named. | text: §5, "is equally consistent with the data" and "may be worth institutional attention" | 5 (directional logic of intervention recommendations) |
| M4 | The limitations inventory omits the one alternative that threatens the finding's existence: both variables are single-occasion self-reports from the same respondent in the same instrument, so the correlation may index one response tendency measured twice. | Leaves the core estimate's construct interpretation unaddressed while four non-threatening limitations are disclosed. Requires added argument and, ideally, discriminant evidence; the numeric result survives, the interpretation may not. | absence: §5 alternative-explanation inventory — expected treatment of the shared self-report source common to both measures; checked Abstract, §2, §3.2, §3.4, §4, §5, §6 | 4 (survey-inference reasoning on same-source measurement) |
| M5 | The estimate has no defined target population: the eligible frame is never enumerated, no response rate is reported, and §6 concedes over-representation of engaged students, yet the paper positions the result as a usable point in a cross-institution distribution. | The contribution framing requires a population parameter the design does not define, so the paper's stated value proposition is unwarranted as written. Repairable by reporting the frame and restricting the claim. | text: §6, "students who engage more with institutional channels may be overrepresented" and §2 "one point in a distribution" | 4 (sampling-inference reasoning) |
| M6 | The recruitment channel is never identified. If the course-announcement channel runs through the LMS, respondents were selected on the dependent variable and the estimate is conditioned on the outcome it reports. | A reader cannot presently evaluate whether the central estimate is confounded by frame construction. One clarifying sentence may repair it, or may confirm a substantive selection problem. | text: §3.1, "distributed through the institution's course-announcement channel over a three-week window" | 3 (inference about institutional channel practice from unstated detail) |

# PART 3 — EDITORIAL SYNTHESIS

# Editorial Decision Package

**Contract:** `reviewer/reviewer_full/v2` · baseline v3.20.0 · panel_size 5
**Manuscript:** *Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students*
**Synthesis mode:** v3.6.2 Sprint Contract (role-scoped arithmetic), paper-blind, cards-only

---

## Review Panel Provenance (#540)

**[PROVENANCE-STAMP-ABSENT]** — No provenance stamp was supplied by the dispatching layer with this invocation. I therefore cannot state that any cross-model slot was active, and I do not infer one. Absent a stamp, this panel must be treated as **single-family** for the purpose of any independence claim: the five review cards carry no attestation that any seat ran on a different model family from the others. No cross-family aggregate is computed, and none of the arithmetic below assumes seat independence beyond role separation. If the dispatching layer holds a provenance stamp, it should replace this statement; it must not be inferred from the panel's internal disagreement.

---

## Part 0: Contract Audit Emission

dimension_verdicts: [D1=block, D2=block, D3=block, D4=warn, D5=warn, D6=block]

fired_conditions: [F2, F3, F5]

da_critical_adjudications: [C1=UNRESOLVED]

editorial_decision=major_revision

### Derivation (auditable)

**Step 1 — Role-scoped matrix.** Only seats whose `contract_role` appears in a dimension's `eligible_roles` contribute; `not_assessed` from ineligible seats is excluded from both numerator and denominator.

| Dim | Priority | Eligible roles | Assessed eligible seats | Verdict (worst) | Fatal? |
|-----|----------|----------------|--------------------------|-----------------|--------|
| D1 methodology_rigor | mandatory | methodology | methodology=block (repairable) | **block** | no |
| D2 domain_accuracy | mandatory | domain | domain=block (repairable) | **block** | no |
| D3 argumentative_coherence | mandatory | da, methodology | da=block (repairable), methodology=warn | **block** | no |
| D4 cross_disciplinary_relevance | high | perspective | perspective=warn | **warn** | — |
| D5 writing_and_structure | normal | eic | eic=warn | **warn** | — |
| D6 venue_fit_and_contribution | mandatory | eic | eic=block (repairable) | **block** | no |

Audit verdict: **block**, no fatal. Every seat that declared a block declared it `repairable`; no seat minted a fatal block, and I do not mint one.

**Step 2 — Condition evaluation.**

| ID | Sev | Cross-reviewer quantifier | Expression | Per-dimension evaluation | Fired |
|----|-----|---------------------------|-----------|--------------------------|-------|
| F1 | 95 | any | any mandatory dimension has a fatal block | D1/D2/D3/D6: no assessed eligible seat declared fatal | **false** |
| F2 | 90 | any | any mandatory dimension scores 'block' | D1=T, D2=T, D3=T (da), D6=T → any → T | **true** |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1 (n=1, owner methodology)=T; D2 (n=1, owner domain)=T; D3 (n=2, both seats required: block+warn)=T; D6 (n=1, owner eic)=T → 4 ≥ 2 | **true** |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4=warn ≠ block | **false** |
| F5 | 40 | any | any dimension scores 'warn' or worse | D1–D6 all T | **true** |
| F0 | 10 | all | every dimension scores 'pass' | D1 fails immediately | **false** |

**Step 3 — Precedence.** Fired: F2 (90) > F3 (70) > F5 (40). Highest severity selects **F2 → `editorial_decision=major_revision`**.

**Escalation note (no fatality minted).** Four seats flag a citation-integrity condition that, if confirmed, would plausibly warrant rejection. F1 requires a *fatal* block on a mandatory dimension, and no seat declared one — both the EIC and the domain reviewer deliberately scored `repairable` pending verification. I therefore cannot and do not escalate to reject on the current cards. If deterministic verification resolves adversely, the correct route is a **re-scoring round on verified inputs**, not a synthesizer-side re-derivation. This is recorded as a hard precondition in Part 1.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Your manuscript has been assessed by a five-seat panel: an Editor-in-Chief, three peer reviewers (methodology, domain, cross-disciplinary/practical), and a Devil's Advocate seat.

### Decision: Major Revision

### Precondition on this decision (must be resolved before revision begins)

Four of five seats independently report that all six references carry DOIs under the `10.5555` prefix — a reserved test/example prefix, not a live registrant — with sequential suffixes `2050001` through `2050006` across six ostensibly different journals and publishers. **No seat performed first-party DOI resolution, and this synthesis was conducted paper-blind and cannot perform it either.** The editorial office must run deterministic resolution and database lookup on all six entries before this decision letter issues to you.

The observation is unanimous; the *cause* is not adjudicated (see Split 1). If the works resolve, the substantive roadmap below stands unchanged. If they cannot be located, this manuscript does not proceed as a revision: the correct handling is return-to-author with an integrity referral under venue policy, and every substantive point below becomes moot. Do not begin revision work until you have been told which branch applies.

### Consensus Analysis

Consensus is computed per sub-claim across the four non-DA seats (EIC, R1 methodology, R2 domain, R3 perspective). Denominator is always 4. Silence is not agreement. The DA seat is tracked separately.

#### Points of agreement

**[CONSENSUS-4] The printed reference apparatus is unresolvable as submitted (SC-1a).** All four seats read the `10.5555` prefix off the reference list; the DA adds the sequential-suffix pattern. R1 corroborates the observation while expressly referring adjudication elsewhere. No seat performed resolution.

**[CONSENSUS-4] The manuscript's inferential restraint is real and is its strongest asset (SC-S).** All four seats, and the DA, credit the same four behaviours without qualification: refusal of causal verbs, explicit naming of the reverse pathway in the Discussion rather than in Limitations, consistent labelling of the outcome as *perceived* rather than behavioural use, and explicit refusal to claim a model test. This is not a courtesy finding. It is the reason three of the four blocks are repairable by restatement rather than by new data collection, and it must survive revision.

**[CONSENSUS-3] The comparative metadata the paper's own framing requires is absent (SC-3).** EIC, R2, R3 agree; R1 silent. No LMS platform, no country or national system, no sector, no discipline mix, no year-level distribution. The paper offers itself as "one point in a distribution" while withholding what a comparative reader needs to locate the point.

**[CONSENSUS-3] Institutional LMS mandatory-use policy is never stated, leaving the construct indeterminate (SC-4).** EIC, R2, R3 agree; R1 silent. R2 states the consequence most sharply: if LMS access is required for assessment submission, both variables partly index course structure, and perceived usefulness may be functioning as a proxy for compliance.

**[CONSENSUS-3] The full frequency distribution of the outcome item is not reported (SC-6a).** R1, EIC, R3 agree; R2 silent. Only a median category is given, so no reader can assess ceiling concentration — which matters especially given the recruitment channel.

#### Corroborated findings (two seats, no conflict — below the consensus bar, still action-bearing)

- **SC-2** Sampling frame unenumerated, response rate neither reported nor computable, while a sampling-theory confidence interval is attached to the estimate (R1 Critical/5, EIC Major/5; DA M5 corroborates independently).
- **SC-5** Instrument adaptation undocumented; "previously validated" transferred to the modified version without argument (R1 Major/5; R2 Minor/4, explicitly scoped to terminology and deferring psychometric depth to R1 — a deferral, not a dispute).
- **SC-8** Deduplication of 5 entries is operationally inconsistent with the §3.3 anonymity claim (R3 Major/5 from ethics-governance; R1 Major/4 from data-provenance). The field brief predicted only R3 would be positioned to catch this; R1 caught it independently, which strengthens it.
- **SC-7** Common-method / shared-self-report-source variance is unaddressed (R1, R3; DA M4 makes it the centrepiece of its case).
- **SC-10** "Consistent with prior technology-acceptance research" is asserted with no comparison quantity anywhere (R2 Major/4, R1 Minor/4; DA M2).
- **SC-11** Foundational acceptance literature absent; the construct's canonical definition is used but attributed elsewhere (R2 Major/5 on lineage; R3 Minor/4 on outsider legibility — different audiences, same remedy direction).
- **SC-16** Institutional LMS logs existed and were not used; no reason is stated (R3 Minor/5, R1 corroborating).
- **SC-17** No numbered exhibit of any kind; the scatterplot is described but not shown; shared variance is characterised but never stated numerically (EIC Minor/5, R1 corroborating).

#### Single-seat findings (weighted by confidence, not by count)

- **SC-12** Framed as an original contribution when only a replication or brief-report framing is defensible; ~1,900 words with six references is a research note submitted as a full article (EIC, confidence 5, and the EIC owns D6). This single-seat finding carries the D6 block.
- **SC-6b** Attenuation from the coarse ordinal outcome is unquantified; no polyserial/polychoric alternative reported (R1, confidence 5, D1 owner).
- **SC-14** Reproducibility affordances absent: no verbatim items, no software/version, no data or code availability (R1, confidence 5).
- **SC-15** Power statement marginally overstated — ~.795 rather than ">.80" at r = .19, n = 214 (R1, confidence 4; the field brief had pre-flagged this as the one arithmetic item worth attention, and R1 recomputed it independently).

#### Anticipated tension that did **not** materialise

The panel design anticipated that R2 would demand a full acceptance model (PEOU, behavioural intention, facilitating conditions, social influence), colliding with the manuscript's deliberate narrowness. **R2 explicitly declined to do so**, writing that such a recommendation "would destroy it while adding an underpowered structural model to a literature that already has too many," and confined itself to contextual and provenance repairs. There is no arbitration to perform here, and I am not manufacturing one. Authors: you are **not** being asked to build a structural model.

### Points of disagreement

**Split 1 — SC-1b: is the reference list fabricated, or is the pattern unexplained?**
R2 (domain) states plainly that the DOIs "are certainly not resolvable" and that "my domain judgment is that the reference list is fabricated," citing sequential suffixes plus five of six journal titles being near-miss variants of real journals; remedy = rejection with integrity referral. EIC disputes the inference, not the observation: "an observation requiring first-party verification, not an allegation," naming placeholder insertion during anonymisation and systematic formatting error as live alternatives; remedy = verification, then return-to-author. R1 and R3 both report the pattern and expressly decline to allege cause.

> **Editor's Resolution: UNRESOLVED DISSENT — not adjudicated by this panel.** The discriminating test is deterministic DOI resolution and database lookup, and no seat performed it; I am paper-blind and cannot perform it either. On evidence available to the panel, neither side can be resolved, so I record dissent rather than defaulting to either the charitable or the punitive reading. Both seats are right about different things: R2 has the stronger domain grounds (two decades in this literature; near-miss title analysis is a *second, independent* deterministic check that does not depend on DOI resolution and should also be run), and the EIC has the stronger procedural grounds (a fabrication finding carries consequences that require verification, not inference). The editorial office resolves this before the letter issues. If the works cannot be located, R2's route applies and this revision does not proceed.

**Split 2 — SC-9: the onboarding implication.**
R1 (Minor/4), R3 (Major/4), and DA M3 (5) all argue the recommendation is defective — R1 and the DA on *direction* (an intervention recommendation presupposes the forward pathway that §5 declares "equally consistent" with its converse), R3 on *scope* (no conditions, no population, no decision, no threshold magnitude). The EIC (Minor/4) diagnoses the opposite defect: the caution is correct, but the double hedge neutralises the only actionable residue the manuscript offers its practitioner readership. Strengthen versus withdraw are incompatible remedies.

> **Editor's Resolution: the R1/R3/DA remedy prevails.** Evidence first: the manuscript's own §5 sentence — the reverse pathway "is equally consistent with the data" — is decisive. A recommendation intelligible only under one direction cannot be strengthened without contradicting the paper's own stated inferential position, so the EIC's remedy is unavailable on the paper's own terms. Expertise second: direction-of-inference sits with R1 (D1 owner) and the DA (D3 owner); the EIC's concern is about reader value, which is a consequence of the design rather than a defect of the sentence. **Required action:** either re-derive the implication symmetrically, naming the converse lever (under the reverse pathway the actionable lever is structured early exposure, not perception-shaping), or withdraw it in favour of a research-facing next step — in both the Discussion and the Abstract. The EIC's underlying concern is addressed by a different route: the practitioner residue this paper can honestly offer comes from the log-data next step and the contextual reporting in R3/R4/S3, not from strengthening an unwarranted recommendation.

**Split 3 — abstract claim drift (EIC S4 versus DA M1).**
The EIC records as a strength that there is "no claim drift between abstract, results, and conclusion" (confidence 5). The DA reads the *same abstract sentence* and finds that it drops both binding qualifiers, widening from self-reported use to "LMS engagement" and from one institution to "undergraduates" (confidence 5). The DA is not one of the four consensus seats, but this is a direct contradiction on a single sentence and must be resolved rather than passed through.

> **Editor's Resolution: partially reconciled — both findings stand, on different tests.** The EIC's check is *magnitude* drift: does the abstract assert a stronger effect than the results support? It does not, and that strength survives. The DA's check is *scope-qualifier* preservation: does the abstract retain the constraints the body treats as binding? It does not — "modest, design-bounded" is a generic hedge that names no bound, "engagement" is not "self-reported use," and "among undergraduates" is not "among 214 undergraduates at one university." The DA's finding is upheld and enters the roadmap as R6. The authors' own §7 already contains the correctly bounded formulation, which is direct evidence that this is a restatement task, not a research task.

### Decision Rationale

The decision is mechanically determined: four mandatory dimensions score `block` (D1 methodology, D2 domain accuracy, D3 argumentative coherence, D6 venue fit), which fires F2 at severity 90 and selects Major Revision. F3 and F5 also fire and are subsumed by precedence. Reject was not available: F1 requires a fatal block on a mandatory dimension and no seat declared one — every blocking seat declared `repairable`, and I do not mint fatality.

That arithmetic tracks a coherent editorial picture. This is a manuscript whose *craft exceeds its documentation*. The statistical reporting is above the median for its genre — interval estimate, exact n, exact p, an appropriate ordinal robustness check, pre-committed distributional inspection, and a limitations section that binds rather than decorates. R1 independently re-derived the confidence interval by Fisher's z and confirmed it correct. The inferential restraint is credited without qualification by every seat.

But the blocks rest on what is *absent*, not on what is wrong. The sampling frame is never enumerated, so a sampling-theory interval is attached to an estimate with no defined population referent. The instrument's adaptation is undocumented, so the original's validation cannot be shown to transfer. The comparative metadata the paper's own framing requires is withheld, so the estimate cannot perform the one function claimed for it. And the paper's most-read sentence, its contribution claim, and its single practical implication each assert more than the design delivers, while the correctly bounded versions already exist elsewhere in the same manuscript.

The pattern the EIC identified is the one to take seriously in revision: the manuscript's honesty is currently doing less work than it appears to, because it acknowledges narrowness eloquently while declining several low-cost reporting steps that would have made the narrowness *informative* rather than merely *admitted*. Most of the roadmap below is reporting, not research.

### Top Blocking Issues (ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | Entire reference apparatus carries a reserved `10.5555` DOI prefix with sequential suffixes; no cited source is retrievable as printed. Every literature-dependent warrant — instrument provenance, reverse-causation caution, self-report caution, comparability framing — runs through it. | EIC, R2, R3, DA (C1); R1 referring | `text: §References — "https://doi.org/10.5555/2050001"` through `"…/2050006"` | R1 |
| 2 | Estimate has no defined target population: eligible frame unenumerated, response rate neither reported nor computable, recruitment channel unidentified — yet a 95% CI is attached and offered for cross-study comparison. | R1 (Critical/5), EIC (Major/5), DA M5/M6 | `absence: §3.1 — expected eligible-population size and computable response rate; checked §3.1, §3.4, §6, Abstract` | R2, R13 |
| 3 | Claims exceed design at the three points that carry the paper: the abstract drops both binding qualifiers, the contribution is framed as original when only replication is defensible, and the practical implication presupposes a direction the paper itself declares undetermined. | DA (M1, M3), EIC (W2, W4), R1 (W7), R3 (W4) | `text: Abstract — "perceived usefulness tracks with LMS engagement among undergraduates"` vs `§2 "perceived rather than actual engagement"` | R6, R7, R14 |

---

## Part 2: Revision Roadmap

> `Sub-Claim(s)` carries the Step 1b identifiers. Severity and Confidence are **transported** from the reviewer cards, never re-derived; where seats transported different severities for the same repair, both are shown with their source. Every card in this panel carried per-finding Severity and Confidence, so no `[SEVERITY-SOURCE: letter-fallback]` or `[CONFIDENCE-SOURCE: report-level]` tags were required. DA-sourced items carry the DA's table severity band.

### Required Revisions (Must Fix)

| # | Revision item | Sub-Claim(s) | Severity | Evidence anchor | Confidence | Source | Priority | Effort |
|---|---------------|--------------|----------|-----------------|------------|--------|----------|--------|
| R1 | **Gate item.** Resolve the reference apparatus: supply retrievable DOIs, or state that the printed strings are anonymisation placeholders and provide the actual sources. Editorial office runs first-party resolution and title verification before this item is actionable. | SC-1a, SC-1b | Critical | `text: §References — "https://doi.org/10.5555/2050001"–"…/2050006"` | 5 (R2, DA); 4 (EIC, R3) | EIC, R2, R3, DA C1 | P1 | 1–3 d if placeholder; otherwise terminal |
| R2 | Report the eligible undergraduate population N, the achieved response rate, and respondent composition (year level, discipline) against the enrolled population. Either justify the 95% CI against a defined frame or reframe it explicitly as descriptive of the achieved sample. | SC-2 | Critical (R1); Major (EIC) | `absence: §3.1 — expected eligible-population size and computable response rate; checked §3.1, §3.4, §6, Abstract` | 5 (R1); 5 (EIC) | R1, EIC, DA M5 | P1 | 3–5 d |
| R3 | Report the comparative metadata the "one point in a distribution" framing requires: LMS platform by name, country/national system, institutional sector, discipline mix, year-level distribution. | SC-3 | Major | `absence: §3.1 site and platform description — expected LMS platform name, national or system context, discipline and year-level composition; checked Abstract, §3.1, §3.2, §4, §7` | 5 (EIC, R3); 4 (R2) | EIC, R2, R3 | P1 | 1 d |
| R4 | State whether LMS access is required for assessment submission or material access at this institution — mandatory, discretionary, or mixed. Address the consequence for construct interpretation if mandatory. | SC-4 | Major | `absence: §3.1 — expected statement of institutional LMS policy; checked Abstract, §1, §3.1, §3.2, §4, §6` | 5 (R3, EIC); 4 (R2) | R2, R3, EIC | P1 | 0.5 d |
| R5 | Document what was adapted from the source instrument and why (deletions, rewording, referent or response-format changes). Supply verbatim item wording, item-level statistics, and dimensionality evidence. Withdraw or qualify "previously validated" in the Abstract — α = .88 is internal consistency, not structural validity. | SC-5 | Major (R1); Minor (R2, terminology-scoped) | `text: §3.2 "a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"` | 5 (R1); 4 (R2) | R1, R2 | P1 | 3–5 d |
| R6 | Restate the Abstract's closing claim to the precision the §7 Conclusion already achieves: restore the *perceived/self-reported* qualifier and the single-institution qualifier. | SC-13 | Major | `text: Abstract "perceived usefulness tracks with LMS engagement among undergraduates"` vs `§2 "perceived rather than actual engagement"` | 5 | DA M1 (upheld over EIC S4 — see Split 3) | P1 | 0.5 d |
| R7 | Reframe explicitly as a replication or brief report rather than an original contribution, and route to the short-report track. Requires repositioning the Introduction, Literature Review, and Conclusion — not a cosmetic edit. | SC-12 | Major (W2); Minor (W4, format designation) | `text: §2 "It is intended as an incremental data point, comparable with prior work"` | 5 | EIC | P1 | 4–6 d |
| R8 | Report the full five-category frequency distribution of the outcome item in a numbered table; state shared variance numerically rather than verbally; show the inspected scatterplot. | SC-6a, SC-17 | Minor (EIC, R3); within R1's Major parent | `absence: §4 Results — expected the five-category frequency distribution, the numeric shared-variance value, and the inspected scatterplot; checked §3.4, §4, full body for any numbered exhibit` | 5 (EIC, R1); 4 (R3) | EIC, R1, R3 | P1 | 1 d |
| R9 | Address the two unquantified biases running in opposite directions: attenuation from the coarse ordinal outcome (report a polyserial/polychoric estimate alongside Pearson) and common-method variance from same-instrument collection. Add the shared-self-report-source explanation to the limitations inventory. | SC-6b, SC-7 | Major (R1); Major (DA M4) | `text: §3.2 "captured with a single five-point frequency item asking how often the respondent accessed the LMS in a typical week"` | 5 (R1); 4 (DA, R3) | R1, R3, DA M4 | P1 | 3–4 d |
| R10 | Reconcile §3.1's removal of 5 duplicates with §3.3's claim that no identifying information was collected. State what discriminator was used, confirm the ethics submission disclosed it, and confirm the participant-facing anonymity statement was accurate — correcting it if not. Also state the "incomplete" exclusion criterion and compare excluded against retained cases. | SC-8 | Major | `text: §3.1 "14 incomplete submissions and 5 duplicate entries were removed"` vs `§3.3 "No identifying information was collected, and responses could not be linked back to individual students"` | 5 (R3); 4 (R1) | R3, R1 | P1 | 2–4 d |
| R11 | Report the prior coefficients or the meta-analytic range, and state whether .42 [.30, .52] overlaps them — or weaken "consistent with prior technology-acceptance research" to a statement of direction only. Distinguish the PU→intention path from the PU→use path, which have systematically different magnitudes. *Contingent on R1.* | SC-10 | Major (R2); Minor (R1) | `text: §5 "consistent with prior technology-acceptance research (Costa & Wren, 2019; Ibarra & Poll, 2021)"` | 4 (R2, R1, DA) | R2, R1, DA M2 | P1 | 2–4 d |
| R12 | Anchor perceived usefulness in its actual lineage — the gloss in §2 is a close paraphrase of the canonical operationalisation and is attributed elsewhere. Name the framework being invoked so adjacent-field readers can locate it. *Contingent on R1.* | SC-11 | Major (R2); Minor (R3) | `text: §2 "the degree to which a person believes a technology will help them perform better"` | 5 (R2); 4 (R3) | R2, R3 | P1 | 3–5 d |
| R13 | Identify the recruitment channel and state whether it runs through the LMS. If it does, respondents were selected on the dependent variable and the estimate is conditioned on its own outcome. | SC-2 (channel) | Major | `text: §3.1 "distributed through the institution's course-announcement channel over a three-week window"` | 3 | DA M6 | P1 | 0.5 d |
| R14 | **Arbitrated (Split 2).** Either re-derive the onboarding implication symmetrically — naming the converse lever (structured early exposure) — or withdraw it in favour of a research-facing next step. Apply in both §5 and the Abstract. Do **not** strengthen it. | SC-9 | Major (R3); Minor (R1, EIC); Major (DA M3) | `text: §5 "is equally consistent with the data"` and `"may be worth institutional attention"` | 5 (DA); 4 (R1, R3, EIC) | R1, R3, DA M3 (EIC dissent overruled) | P1 | 0.5 d |

### Suggested Revisions (Should Fix)

| # | Revision item | Sub-Claim(s) | Severity | Evidence anchor | Confidence | Source | Priority | Effort |
|---|---------------|--------------|----------|-----------------|------------|--------|----------|--------|
| S1 | Supply reproducibility affordances: verbatim item wording for both measures, analysis software and version, and a data/code availability statement. A de-identified 214×7 matrix carries negligible disclosure risk and would let a meta-analyst recompute under alternative measurement assumptions. | SC-14 | Minor | `absence: §3.2 and §3.4 — expected verbatim item wording, analysis software and version, and a data or code availability statement; checked §3.2, §3.4, §7, reference list` | 5 | R1 | P2 | 1–2 d |
| S2 | Correct the power statement. At n = 214, achieved power at r = .19 is ≈ .79, not > .80. Restate as r ≈ .191 at .80 power, or report achieved power ≈ .79, or name the software and method. | SC-15 | Minor | `text: §3.4 "the study had greater than .80 power to detect a correlation of r >= .19 at alpha = .05 (two-tailed)"` | 4 | R1 | P2 | 0.5 d |
| S3 | State why institutional LMS access logs were not used — anonymous collection precluding linkage without a governance mechanism is a defensible answer and converts an apparent omission into a documented design constraint. | SC-16 | Minor | `absence: §3.4 and §6 — expected a stated reason why institutional LMS access logs were not used or linked; checked §3.1, §3.3, §3.4, §5, §6, §7` | 5 (R3); corroborated R1 | R3, R1 | P2 | 0.5 d |
| S4 | Name and briefly explain the theoretical tradition being invoked, for adjacent-field readers who cannot currently locate "technology-acceptance research" or judge what consistency with it means. *Overlaps R12; may be satisfied by the same rewrite.* | SC-11 (outsider legibility) | Minor | `text: Abstract "The association was consistent with prior technology-acceptance research"` | 4 | R3 | P3 | 0.5 d |
| S5 | Report the outcome categories in a form translatable to log-derived measures (sessions, page views, active days), so adjacent-field readers can attempt external validation. *Satisfied in part by R8.* | SC-6a | Minor | `text: §4 "Self-reported LMS use had a median category of"` with `§3.2 "1 = rarely or never to 5 = several times daily"` | 4 | R3 | P3 | 0.5 d |

### Revision Checklist

**Gate (blocks all work below)**
- [ ] R1: Reference apparatus resolved by the editorial office; branch confirmed to authors before revision begins

**Priority 1 — Structural revisions (est. 20–31 person-days, substantially parallelisable)**
- [ ] R2: Eligible population N, response rate, respondent-vs-population composition; CI justified or reframed
- [ ] R3: LMS platform, country/system, sector, discipline mix, year-level distribution
- [ ] R4: Institutional LMS mandatory-use policy stated, with construct consequence addressed
- [ ] R5: Instrument adaptation documented; verbatim items, item-level statistics, dimensionality; "previously validated" withdrawn or qualified
- [ ] R6: Abstract restated to §7's standard of precision
- [ ] R7: Reframed as replication/brief report; short-report track
- [ ] R8: Frequency distribution table, numeric shared variance, scatterplot exhibit
- [ ] R9: Attenuation and common-method variance addressed; shared-self-report-source added to limitations
- [ ] R10: Deduplication mechanism disclosed; ethics record and participant-facing anonymity claim reconciled; exclusion criterion stated
- [ ] R11: Prior effect sizes reported or consistency claim weakened; PU→intention vs PU→use distinguished
- [ ] R12: Construct anchored in its actual lineage; framework named
- [ ] R13: Recruitment channel identified; LMS-routing addressed
- [ ] R14: Onboarding implication re-derived symmetrically or withdrawn, in §5 and Abstract

**Priority 2 — Content supplementation (est. 2–3 person-days)**
- [ ] S1: Verbatim items, software/version, data availability
- [ ] S2: Power statement corrected
- [ ] S3: Rationale for not using LMS logs

**Priority 3 — Text and reporting apparatus (est. 1 person-day)**
- [ ] S4: Theoretical tradition named for adjacent-field readers
- [ ] S5: Outcome categories reported in log-translatable form

### What you are *not* being asked to do

The panel considered and explicitly declined to require a full acceptance-model specification. R2 — the seat best positioned to demand it — wrote against it directly. The narrow correlational framing is not the defect; the undocumented design and the over-reaching claim wording are. Every P1 item above is compatible with keeping the study exactly as narrow as it is.

### Revision deadline

**8 weeks** from the date the reference-apparatus gate is resolved in your favour. The upper bound of the Major Revision range is justified by three items with real lead time: the R7 repositioning rewrite, the R12 literature re-anchoring, and the R10 ethics-record check, which depends on institutional records outside your direct control. If the gate resolves adversely, this deadline does not apply.

### Response letter

Use `templates/revision_response_template.md`. Respond to every numbered item R1–R14 and S1–S5 individually. Items marked CONSENSUS-3 or CONSENSUS-4 are not open to "respectfully decline." For the arbitrated items (R14, R6) the panel's resolution is recorded above with its rationale; if you contest either, address the stated basis of the arbitration — reasserting the original position without new argument will not reopen it.

---

## Part 3: Reviewer Report Summary (Appendix)

> The contract's card format carries per-dimension scores and per-finding confidence rather than a per-seat overall recommendation or a report-level confidence score. The matrix below therefore reports what the cards actually contain; no overall recommendation is inferred for any seat.

| Dimension | EIC | R1 Methodology | R2 Domain | R3 Perspective | DA |
|-----------|-----|----------------|-----------|----------------|-----|
| D1 methodology_rigor | n/a | **block** (repairable) | n/a | n/a | n/a |
| D2 domain_accuracy | n/a | n/a | **block** (repairable) | n/a | n/a |
| D3 argumentative_coherence | n/a | warn | n/a | n/a | **block** (repairable) |
| D4 cross_disciplinary_relevance | n/a | n/a | n/a | warn | n/a |
| D5 writing_and_structure | warn | n/a | n/a | n/a | n/a |
| D6 venue_fit_and_contribution | **block** (repairable) | n/a | n/a | n/a | n/a |
| Findings | 6 W / 4 S | 8 W / 3 S | 6 W / 3 S | 7 W / 4 S | 1 C / 6 M |

"n/a" = `not_assessed` and role-ineligible; excluded from both numerator and denominator throughout.

**Editor-in-Chief** — Blocks D6 on contribution framing: a result indistinguishable from settled knowledge, framed as original rather than as replication, with none of the comparative metadata its "one point in a distribution" claim requires. Warns D5 on reporting apparatus (no exhibits, verbal rather than numeric shared variance) rather than on prose. Key point: *the manuscript's honesty is doing less work than it appears to, because low-cost reporting steps that would make its narrowness informative were declined.*

**Reviewer 1, Methodology** — Blocks D1 on two independently sufficient grounds: an unenumerated sampling frame carrying a sampling-theory interval, and a single-item ordinal outcome with no provenance, reliability, distribution, or attenuation treatment. Warns rather than blocks D3, crediting the inferential calibration explicitly. Independently re-derived the CI (correct) and the power calculation (marginally overstated). Key point: *a correctly computed interval around a quantity of unknown provenance does not become trustworthy; it becomes precise-looking.*

**Reviewer 2, Domain** — Blocks D2 on the reference apparatus plus attribution of the construct's canonical definition to the wrong sources, an unfalsifiable consistency claim, and undeclared institutional LMS policy. Scored `repairable` rather than fatal precisely because no first-party resolution was performed. Notably declined the full-model recommendation the panel design anticipated. Key point: *if the sources cannot be resolved, the correct handling is not a revision request — and every other point becomes moot.*

**Reviewer 3, Cross-disciplinary/Practical** — Warns D4: operational definitions are unusually legible to outsiders, but the comparability claim is unsupported without platform, system, sector, composition, and mandatory-use policy, and the single practice-facing implication supplies no scope. Uniquely positioned on the ethics/deduplication contradiction — though R1 caught it independently. Key point: *without the mandatory-use fact, a reader cannot tell whether the coefficient indexes student perception or institutional course design.*

**Devil's Advocate** — Blocks D3, and states the block is carried by cumulative claim–design mismatch rather than by any single rejection-level defect, declining to inflate one for adversarial effect. Deliberately excluded the citation finding from its own dimension score to avoid laundering an external finding into an internal-coherence judgment. Supplied an explicit flip-to-pass condition list, which is now the P1 spine of this roadmap. Key point: *the limitations inventory lists four constraints that bound the finding and omits the one that would threaten its existence.*

---

*Cross-model blind decision check (#518): `ARS_CROSS_MODEL` not set for this invocation. No behavioural change; no checkpoint marker emitted.*
