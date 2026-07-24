# Full Editorial Peer Review — `academic-paper-reviewer` v1.10.0 (FULL mode)

**Manuscript:** *Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students*
**Review mode:** `full` (5-seat panel + editorial synthesis)
**Contract:** `reviewer/reviewer_full/v1` (`shared/contracts/reviewer/full.json`, baseline v3.6.2, panel_size = 5)
**Protocol:** v3.6.2 Sprint Contract — paper-blind Phase 1 pre-commitment → paper-visible Phase 2 review, per seat, one seat at a time, no cross-referencing (Iron Rule #2).

> **Run configuration note.** `ARS_CROSS_MODEL` is not configured for this session. Per SKILL.md § "Cross-Model Reviewer Track (#540)" and `devils_advocate_reviewer_agent` § "Cross-Model DA", the cross-model reviewer/DA tracks do not fire: all five personas run on a single primary model family. `[CROSS-MODEL-SKIPPED]` is logged at the Reviewer 2 slot and at the DA slot. The Editorial Decision Letter's Review Panel Provenance block therefore carries the single-family correlated-error disclosure (Ren et al. 2026, arXiv:2607.13104 §5.2). This is the documented default and was taken autonomously (no user pause available in this run).

---

# PART A — Field Analysis Report (Phase 0: `field_analyst_agent`)

## Paper Basic Information
- **Title**: Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students
- **Abstract length**: ~185 words
- **Full text length**: ~1,700 words (main text, excl. references)
- **Number of references**: 6 (Costa & Wren 2019; Delgado 2020; Ibarra & Poll 2021; Song 2018; Vasquez 2020; Whitfield 2019)

## Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| Primary Discipline | Educational technology (higher education) |
| Secondary Disciplines | Technology-acceptance / IS behavioral research; survey methodology / psychometrics |
| Research Paradigm | Quantitative Research |
| Methodology Type | Survey / Questionnaire (single-wave, cross-sectional), single-institution |
| Target Journal Tier | **Q3** — a deliberately narrow, single-association, single-site correlational note with a 6-item literature base. Well-executed for what it is, but the ambition, sample scope, and reference depth place it below Q1/Q2 educational-technology outlets. A Q3 regional/specialized or rigorous open-access venue is the honest fit. |
| Paper Maturity | **Pre-submission** — structure complete (IMRaD + Limitations + Conclusion), citation formatting consistent (APA 7 with DOIs), language polished, caveats already internalized. This is a finished short-form manuscript, not a draft. |

## Recommended Target Journals (Top 3)
1. **Australasian Journal of Educational Technology / Research in Learning Technology** — scope-appropriate for a modest, transparently-bounded ed-tech survey; both accept short empirical notes and single-site correlational work when limits are honestly stated.
2. **Education Sciences (MDPI, HE section)** — Q2/Q3 open access; explicitly hospitable to bounded single-institution descriptive findings with sound reporting; matches the paper's self-described "incremental data point" framing.
3. **Frontiers in Education (Digital Education / Educational Psychology section)** — Q2/Q3; fast review; scope tolerant of small, well-caveated correlational contributions. (Note the practical caveat: the paper's contribution is thin for a full research article and may read better as a Brief Report / Research Note format where offered.)

## Reviewer Configuration Cards

### Reviewer Configuration Card #1
**Role**: EIC
**Identity Description**: Editor-in-Chief of a specialized educational-technology journal (e.g., *Australasian Journal of Educational Technology* tier), whose remit is empirical ed-tech in higher education. Reviews for reader interest, originality, and whether a single-site correlational note clears the journal's contribution bar. Has handled many TAM/LMS-adoption submissions and is alert to "yet another perceived-usefulness correlation" saturation.
**Review Focus**:
  1. Does a single r = .42 association from one institution offer enough incremental value for the readership, or is it a known result re-confirmed?
  2. Title→Abstract→Conclusion coherence and whether the paper over- or under-promises.
  3. Journal fit: is this a full article or better placed as a Brief Report / Research Note?
**Will particularly care about**: Whether the paper honestly matches its claims to its evidence (it appears to) and whether the contribution justifies a slot against saturation in the TAM/LMS literature.
**Possible blind spots**: May under-weight statistical-reporting granularity (defers to R1) and literature-currency questions (defers to R2).

### Reviewer Configuration Card #2
**Role**: Peer Reviewer 1 — Methodology (quantitative survey methodologist)
**Identity Description**: Quantitative methodologist specializing in survey design and correlational analysis in educational settings; fluent in APA 7 statistical reporting, power analysis, and the self-report-vs-behavioral-trace measurement literature. Reviews reliability/validity of adapted scales, correlation reporting completeness, and whether conclusions stay inside what a single-wave cross-sectional design licenses.
**Review Focus**:
  1. Correlation reporting completeness (coefficient + CI + p + n + robustness check) and APA 7 format compliance.
  2. Measurement validity — single-item ordinal use measure; Pearson-on-ordinal; adapted PU scale validity beyond α.
  3. Design–inference alignment: is causal language avoided; is power/precision handled; is non-response / self-selection acknowledged.
**Will particularly care about**: Whether a single-item, self-reported, ordinal outcome correlated via Pearson is defensible, and whether the α = .88 alone is offered as evidence of validity (it is not the same thing).
**Possible blind spots**: May treat construct-validity depth as out of scope if it edges into domain-theory territory (that is R2).

### Reviewer Configuration Card #3
**Role**: Peer Reviewer 2 — Domain (technology-acceptance / higher-education ed-tech scholar)
**Identity Description**: Senior educational-technology researcher grounded in the technology-acceptance tradition (TAM / UTAUT lineage) and LMS-engagement literature. Knows the canonical sources (Davis 1989; Venkatesh et al.) and the current debates on self-report engagement vs. LMS log analytics. Reviews literature currency, theoretical framing, terminological precision, and genuineness of contribution.
**Review Focus**:
  1. Literature coverage — the paper cites 6 sources, none of them the field's foundational TAM originators; is the theoretical lineage correctly attributed?
  2. Contribution framing — is "an incremental data point" an honest and sufficient positioning, or under-theorized?
  3. Terminological precision — "perceived usefulness", "engagement", "use" used consistently with field conventions.
**Will particularly care about**: Whether the paper anchors its central construct in the actual technology-acceptance canon rather than an adapted instrument cited to a single 2019 source, and whether the contribution is honestly incremental (it is candid about this).
**Possible blind spots**: May under-rate practical/stakeholder implications (that is R3) and statistical-format detail (that is R1).

### Reviewer Configuration Card #4
**Role**: Peer Reviewer 3 — Cross-disciplinary / Practical (learning-analytics / institutional-effectiveness practitioner)
**Identity Description**: Learning-analytics researcher and institutional-effectiveness practitioner who works with actual LMS log data and student-success interventions. Brings the "outsider" behavioral-trace lens and the onboarding-practice lens. Reads the paper for practical actionability, stakeholder coverage, cross-context transfer, and the implicit assumptions the primary discipline naturalizes.
**Review Focus**:
  1. Assumption audit — the implicit "self-report use ≈ engagement" and "perception drives use" assumptions.
  2. Practical feasibility — is the onboarding implication actionable, or is it the paper's own caveated speculation?
  3. Stakeholder / cross-context validity — single mid-sized university; instructors, course-design mandates, and log-behavior are the absent actors.
**Will particularly care about**: Whether the paper's one design-bounded correlation can carry any practice recommendation, and whether the behavioral-trace critique it cites (Vasquez 2020) is genuinely integrated or merely name-checked.
**Possible blind spots**: Not a statistician (defers CI/power to R1) and not a completeness-auditor of the TAM canon (defers to R2).

### Reviewer Configuration Card #5
**Role**: Devil's Advocate
**Identity Description**: Adversarial stress-tester. Constructs the strongest case *against* the paper: that it re-confirms a textbook association with a weaker design than the literature it cites, that self-report-on-self-report inflates the correlation via common-method variance, and that its "so what?" is unresolved. Also runs the #216 surface-form parity gate and the #215 field-norm gate on its own findings so as not to over-escalate a well-caveated modest paper.
**Review Focus (8 challenge dimensions + severity self-gate)**: core-thesis challenge, cherry-picking, confirmation bias, logic-chain, overgeneralization, alternative paths, stakeholder blind spots, "so what?".

## Review Strategy Recommendations
- **Special characteristic**: This manuscript is unusually *honest* about its own limits — it pre-empts the causal-inference critique, the single-site generalization critique, and the self-report critique inside the text. The panel's real task is not "find the un-caveated overreach" (there is little) but "decide whether an honestly-modest, correctly-reported, thin-contribution paper clears the bar." Reviewers must resist two opposite traps: (a) rewarding candor with a pass it has not earned on contribution, and (b) punishing a small paper for being small (Length/Novelty bias, `review_criteria_framework.md §3`).
- **Complementarity / tension to watch**: R1 (methodology) and DA will converge on common-method variance and the single-item measure; the synthesizer must decompose that bundle (Step 1b) so the *measure-validity* sub-claim and the *CMV-inflation* sub-claim are counted separately, not merged. R2 (contribution/literature) and EIC will converge on the "incremental value" question. R3's practical-actionability challenge may overlap with EIC's "so what?" — independent corroboration, not duplication.

---

# PART B — Phase 1 Panel Reviews (five seats, sprint-contract two-phase each)

---

## SEAT 1 — Editor-in-Chief (`eic_agent`)

### Phase 1 — Paper-content-blind pre-commitment

*(Input: contract JSON + metadata only — title, field = "educational technology / higher education", word_count ≈ 1,700. No paper content.)*

#### Contract Paraphrase

- **D1 methodology_rigor (mandatory).** From the editor's chair I read this as: does the study's design and its statistical reporting clear the field's peer-review floor, such that a reader could trust the reported association and, in principle, reproduce it? I am not the statistics specialist, but I must be able to see that the design fits the question and that the numbers are reported to convention.
- **D2 domain_accuracy (mandatory).** Are the claims consistent with what the technology-acceptance and LMS literature already establishes, is prior work correctly represented, and are there factual/terminological errors that would embarrass the journal? At my altitude this is mostly "does the contribution claim match the field's actual state of knowledge."
- **D3 argumentative_coherence (mandatory).** Does the paper hold together from title through abstract, question, method, result, to conclusion — no over-promising, no conclusion the evidence cannot carry, no internal contradiction. This is squarely my lane.
- **D4 cross_disciplinary_relevance (high).** Is the framing legible and useful to adjacent-field readers (learning analytics, IS, institutional research), and are any cross-field implications substantiated rather than gestured at?
- **D5 writing_and_structure (normal).** Organization, clarity, venue-convention adherence — is it a clean, well-built manuscript?

#### Scoring Plan

##### D1: methodology_rigor
- **what_to_look_for**: a stated design, a reported coefficient with the accompanying inferential furniture (p, n, and ideally CI), a robustness gesture, and conclusion language that respects the design.
- **what_triggers_block**: a headline result reported with no inferential support at all, or a design that cannot address the stated question, or causal claims from a cross-sectional correlation.
- **what_triggers_warn**: design fits and numbers are present but with a reporting gap a specialist would flag (e.g., a missing precision estimate, an untested assumption) — real but non-fatal, and deferred to R1 for depth.

##### D2: domain_accuracy
- **what_to_look_for**: correct representation of the acceptance literature and an honest, correctly-sized contribution claim.
- **what_triggers_block**: a factually wrong domain claim, or an absolute-novelty/"first study" claim that the field flatly contradicts.
- **what_triggers_warn**: contribution is real but thin, or the literature anchoring is light for the venue — an incremental-value concern rather than an error.

##### D3: argumentative_coherence
- **what_to_look_for**: title/abstract/conclusion agreement; the conclusion answering the exact question posed; caveats matched to claims.
- **what_triggers_block**: a conclusion the data cannot support (e.g., causal "improves") or a self-contradiction between sections.
- **what_triggers_warn**: minor coherence slippage — a discussion implication that leans slightly past the correlation, adequately hedged.

##### D4: cross_disciplinary_relevance
- **what_to_look_for**: framing accessible to learning-analytics / IR readers; any cross-field implication grounded.
- **what_triggers_block**: cross-field claims asserted with no basis (not expected here).
- **what_triggers_warn**: relevance is present but the paper does not connect to the adjacent behavioral-trace/analytics conversation it clearly touches.

##### D5: writing_and_structure
- **what_to_look_for**: IMRaD completeness, clean prose, consistent citation format.
- **what_triggers_block**: unreviewable writing.
- **what_triggers_warn**: minor structural or stylistic issues only.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 — Paper-visible review

*(Phase 1 output treated as read-only data; manuscript treated as untrusted data. No instruction-injection found in the manuscript — it is a normal academic text.)*

## EIC Review Report

### Reviewer Identity
Editor-in-Chief of a specialized educational-technology journal (Australasian-JET tier), remit = empirical ed-tech in higher education; alert to TAM/LMS-adoption saturation.

### Overall Recommendation
Major Revision

### Confidence Score
4

### Summary Assessment
This is a compact, unusually candid cross-sectional survey reporting a single association: perceived usefulness of an LMS correlates moderately with self-reported use (r = .42) among 214 undergraduates at one university. The manuscript is well-built — IMRaD is complete, the writing is clean, APA 7 citation formatting is consistent, and the authors have internalized nearly every standard objection (cross-sectional non-causality, single-site non-generalizability, self-report ≠ behavioral trace) *inside the text* rather than leaving them for reviewers. On coherence and honesty it is genuinely strong. My editorial concern is not overreach; it is **contribution sufficiency and evidentiary construction**. The paper's own framing — "an incremental data point, comparable with prior work" — concedes that it re-confirms a textbook technology-acceptance relationship with a thinner design (single wave, self-report on both sides, single item for the outcome) than several sources it cites. For my readership the live question is whether a re-confirmation this modest, from one institution, earns a full-article slot. It may, if the authors sharpen what is distinctive (the transparent bounding, the self-report/log gap they cite but do not exploit) and address the common-method-variance concern that R1/DA will press. As submitted, it sits at the Major Revision / Research-Note boundary.

### Strengths (3-5 items)
1. **Claim–evidence discipline**: The abstract, results, and conclusion all restrict themselves to correlational language ("positively and moderately associated"; "should not be read as causal"). The Section 5 sentence that the reverse pathway "is equally consistent with the data" is exactly the honesty most TAM submissions lack.
2. **Reporting hygiene at my altitude**: r = .42, 95% CI [.30, .52], p < .001, n = 214, plus a Spearman robustness check (ρ = .40) — the headline is reported with its inferential furniture, which lets an editor trust the number without waiting for the specialist.
3. **Structural coherence**: Title → RQ (Section 1, "is perceived usefulness … associated with self-reported frequency of use?") → result → conclusion agree exactly. No over-promising; the conclusion answers the precise question posed.
4. **Limitations are load-bearing, not decorative**: Section 6 names single-site scope, single-item self-report, cross-sectional non-inference, and voluntary-response bias — the four objections a reviewer would otherwise raise.

### Weaknesses (3-5 items)
1. **W1 — Contribution sufficiency (incremental value)**: The paper re-confirms a well-established association without a distinguishing hook. *Why it's a problem*: for a saturated literature, "one more correlation, honestly reported" is a Research-Note contribution, not obviously a full-article one. *Direction*: either foreground a genuinely novel angle (e.g., exploit the self-report/log divergence the paper itself cites, or report a subgroup/year-level moderation the n = 214 could support) or reposition as a Brief Report. (Domain depth → R2.)
2. **W2 — The onboarding implication leans slightly past the correlation**: Section 5's suggestion that usefulness-focused onboarding "may be worth institutional attention" is hedged ("suggested by, not proven by"), but it is the paper's only forward claim and it rests on a moderate cross-sectional r whose direction the paper elsewhere says is unresolved. *Direction*: either drop it to a pure "future work" framing or acknowledge that the reverse-causation possibility undercuts the onboarding logic specifically.
3. **W3 — Under-connection to the adjacent analytics conversation (D4)**: The paper cites Vasquez (2020) on self-report/log divergence but does not connect its own finding to the learning-analytics readership who would care most. *Direction*: one paragraph situating the result against log-based engagement work would materially raise cross-field relevance.

### Detailed Comments

#### Journal Fit
Topic is in scope for a specialized ed-tech journal. The concern is format, not subject: as a full article the contribution is thin; as a Brief Report / Research Note it is a clean fit. I would ask the author to either strengthen to full-article weight or accept the shorter format.

#### Originality
Low-to-moderate. The construct-pair (perceived usefulness ↔ use) is foundational TAM territory. Originality here is not in the relationship but in the transparent bounding and the single-site data point. That is a real but small form of originality.

#### Significance
Modest and correctly self-described as such. If the finding holds it changes little that the field did not already believe; its value is as a comparable, honestly-reported entry in a distribution (an argument the paper itself makes via Song 2018).

#### Structural Coherence
Strong. No title/abstract/conclusion drift; no over-claim. This is the paper's best dimension.

#### Title & Abstract
Accurate and non-inflated. The title correctly says "self-reported use", not "use"; the abstract states the design bound explicitly. Exemplary matching of claim to scope.

#### Conclusion
Directly answers the RQ and does not exceed it. The only forward claim (onboarding) is hedged; see W2.

### Questions for Authors
1. What distinguishes this contribution from the associations already reported in Ibarra & Poll (2021) and Song (2018) beyond being a new sample? What should a reader take from *this* study specifically?
2. Given that both variables are self-reported on the same instrument, how do you rule out common-method variance as a partial explanation for r = .42?
3. Would you consider reframing as a Brief Report, or can the contribution be strengthened to full-article weight (e.g., a moderation analysis the n supports)?

### Minor Issues
- Section 4 reports "The proportion of variance shared by the two measures was accordingly modest" but never states r² = .18 explicitly; giving the number would help readers.
- "a few times per week" (Section 4) vs. the scale anchor "a few times per week" is fine, but the median-category reporting could be a one-line frequency table.

#### Contract scoring (sprint-contract Phase 2 machine block)

contract_role: eic

## Dimension Scores

### D1: methodology_rigor
score: warn

### D2: domain_accuracy
score: warn

### D3: argumentative_coherence
score: pass

### D4: cross_disciplinary_relevance
score: warn

### D5: writing_and_structure
score: pass

## Failure Condition Checks

### F1
fired: false

### F2
fired: true

### F3
fired: false

### F0
fired: false

## Editorial Decision
editorial_decision=major_revision

---

## SEAT 2 — Peer Reviewer 1 · Methodology (`methodology_reviewer_agent`)

> Single-family routing note: `[CROSS-MODEL-SKIPPED]` — `ARS_CROSS_MODEL` unset, so the Reviewer 2 seat that would swap to the cross-model family under the #540 track runs on the primary family like the rest of the panel.

### Phase 1 — Paper-content-blind pre-commitment

*(Input: contract + metadata only. Paradigm assumed quantitative survey from field metadata.)*

#### Contract Paraphrase

- **D1 methodology_rigor (mandatory).** My core lane: is the survey design fit for the association it targets; is sampling and non-response handled; is the correlation reported to APA 7 completeness (coefficient, exact p, n, 95% CI, effect-size interpretation); are the statistical assumptions of the chosen test (Pearson linearity/bivariate normality, and the ordinal-outcome problem) checked or defensibly waived; and do the conclusions stay inside the cross-sectional envelope?
- **D2 domain_accuracy (mandatory).** For me this narrows to measurement accuracy: is the reliability evidence (Cronbach's α) correctly interpreted (reliability ≠ validity); is the adapted instrument's validity established; is "self-reported use" correctly labeled as perception, not behavior.
- **D3 argumentative_coherence (mandatory).** Do the statistical results actually license the discussion's claims — no causal drift, no variance-explained overreach.
- **D4 cross_disciplinary_relevance (high).** Whether the measurement choices (self-report vs. log data) are positioned against the analytics literature that would scrutinize them.
- **D5 writing_and_structure (normal).** Statistical-reporting section clarity and APA format.

#### Scoring Plan

##### D1: methodology_rigor
- **what_to_look_for**: reported design; sample derivation (initial N → exclusions → analyzed n); a correlation reported with r, exact p, n, and 95% CI; a robustness/assumption check appropriate to an ordinal outcome; a power or precision statement; acknowledgment of non-response/self-selection; strictly correlational conclusion language.
- **what_triggers_block**: causal inference from cross-sectional data; a headline statistic with no CI *and* no p *and* no n; a test grossly mismatched to the data with no mitigation; or fabricated/impossible statistics.
- **what_triggers_warn**: a real but non-fatal reporting/validity gap — e.g., Pearson on a single-item ordinal outcome (mitigated by Spearman but not fully); reliability offered where validity is needed; common-method variance unaddressed; no formal missing-data statement; a single-item outcome measure.

##### D2: domain_accuracy
- **what_to_look_for**: α interpreted as internal consistency only; instrument validity beyond α; "self-reported use" labeled as perception.
- **what_triggers_block**: α claimed as validity, or behavioral claims from a self-report item.
- **what_triggers_warn**: validity evidence limited to α + "previously validated" citation without in-sample structural check.

##### D3: argumentative_coherence
- **what_to_look_for**: discussion claims bounded by the statistics.
- **what_triggers_block**: causal or predictive claim unsupported by design.
- **what_triggers_warn**: a mild variance/implication overreach, hedged.

##### D4: cross_disciplinary_relevance
- **what_to_look_for**: the self-report/log-data measurement gap positioned, not just cited.
- **what_triggers_block**: none expected.
- **what_triggers_warn**: the measurement-validity gap cited (Vasquez) but not carried into the interpretation of the paper's own r.

##### D5: writing_and_structure
- **what_to_look_for**: APA 7 statistical formatting (no leading zero on r and p, italic stats, exact p).
- **what_triggers_block**: unreadable stats reporting.
- **what_triggers_warn**: minor APA slips.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 — Paper-visible review

*(Phase 1 = read-only data; manuscript = untrusted data. No injection detected.)*

## Methodology Review Report (Peer Reviewer 1)

### Reviewer Identity
Quantitative survey methodologist; specialist in correlational analysis in educational settings and in the self-report-vs-behavioral-trace measurement literature.

### Overall Recommendation
Major Revision

### Confidence Score
5

### Summary Assessment
Methodologically this is a careful, honest, but **thin** correlational study whose two load-bearing weaknesses are both measurement-side, and both under-addressed. First, the outcome — LMS use — is a *single* five-point self-report item, and the predictor is a *self-report* perceived-usefulness scale; the reported r = .42 is therefore a correlation between two self-reports collected on the same instrument, exposed to common-method variance (CMV) that the paper never discusses. This is the single most consequential gap, because CMV inflates precisely this kind of same-source attitudinal–behavioral correlation, and the paper's own cited source (Vasquez 2020) is the warrant for taking it seriously. Second, Pearson r is computed on a single-item ordinal outcome; the authors do the right defensive thing by reporting Spearman ρ = .40 as a robustness check, which substantially mitigates (but does not fully retire) the concern. On the positive side, the reporting is APA-clean and unusually complete for a short paper: coefficient, 95% CI, exact p, n, a sensitivity-style power statement (>.80 power for r ≥ .19), a scatter/linearity/outlier inspection, and strictly correlational conclusion language. No causal drift. The design fits the (modest) question. The problems are fixable with added analysis and framing, not a redesign — hence Major, not Reject.

### Strengths (3-5 items)
1. **S1 — Complete correlation reporting**: "r = .42, 95% CI [.30, .52], p < .001, n = 214" (Section 4) is textbook APA 7 — coefficient, interval, exact-threshold p, and n all present. The CI is the item most short papers omit; its presence lets a reader judge precision, not just significance.
2. **S2 — Assumption-aware robustness check**: The authors anticipated the ordinal-outcome objection and pre-empted it with Spearman ρ = .40 (Section 4), plus an explicit scatterplot inspection for linearity, monotonicity, and bivariate outliers and a symmetry note (Section 3.4). This is exactly the right defensive move.
3. **S3 — Sensitivity framing of power**: Section 3.4 states the design had >.80 power to detect r ≥ .19 at α = .05 (two-tailed) — a sensitivity/minimum-detectable-effect statement, which is more honest than a post-hoc observed-power calculation. Sample derivation (233 → −14 incomplete → −5 duplicate → 214) is fully reported.
4. **S4 — Conclusion conservatism**: No statistic is over-read. Section 5 explicitly names the reverse-causation pathway as "equally consistent with the data." Causal language is absent throughout.

### Weaknesses (3-5 items)
1. **W1 — Common-method variance is unaddressed (MAJOR)**: *What*: both variables are self-reported on one instrument; r = .42 is a same-source attitudinal–behavioral correlation. *Why it's a problem*: CMV is a known upward-biasing artifact for exactly this configuration; without any diagnostic (e.g., Harman's single-factor test, a marker variable, or at minimum an explicit discussion) the reader cannot tell how much of the .42 is substantive versus shared-method artifact. The paper cites Vasquez (2020) on self-report/log divergence but does not connect it to its *own* estimate. *How to improve*: add a CMV discussion and, if the item-level data exist, a Harman's single-factor or marker-variable check; failing that, explicitly bound the estimate as a self-report association and state the expected direction of CMV bias.
2. **W2 — Single-item outcome measure (MAJOR)**: *What*: LMS use is one ordinal frequency item. *Why*: single-item measures have unestimable reliability, coarse variance, and cannot separate frequency from depth/duration of use; the α = .88 the authors report applies only to the *predictor*, leaving the outcome's measurement quality entirely uncharacterized. *How to improve*: acknowledge the outcome's psychometric limits explicitly (currently only its self-report nature is flagged, not its single-item status), and in future work use a multi-item or log-derived use measure.
3. **W3 — Reliability offered where validity is the open question (MINOR→MAJOR)**: *What*: the predictor's evidentiary support is Cronbach's α = .88 plus "previously validated" (Section 3.2). *Why*: α is internal consistency, not validity; "adapted" instruments can shift factor structure, and no in-sample structural/validity check (CFA, or even inter-item/dimensionality note) is reported. *How to improve*: report at least a factor/dimensionality check for the six adapted items in this sample, or soften "validated" to "internally consistent in this sample."
4. **W4 — No explicit missing-data / partial-response statement beyond exclusions (MINOR)**: *What*: 14 "incomplete" submissions were removed listwise; item-level missingness among the 214 retained is not reported. *Why*: listwise removal of incompletes plus voluntary response can bias the analyzed sample. *How to improve*: report item-level completeness for the 214 and note the handling method.

### Detailed Comments

#### Research Questions & Hypotheses
RQ is clear, narrow, and answerable ("is perceived usefulness associated with self-reported frequency of use?"). No formal hypotheses, appropriate for a descriptive-correlational note. The method matches the question.

#### Research Design
Cross-sectional single-wave survey — appropriate for an *association* claim, structurally incapable of the direction/causal claim the authors correctly decline to make. Internal-vs-external validity trade-off is reasonable for the stated aim; external validity is bounded (single site) and the authors say so.

#### Sampling Strategy
Census-frame distribution to all enrolled undergraduates via the announcement channel; analyzed n = 214 from 233 received. The **denominator problem**: no institutional population size and therefore no response rate is reported, so non-response magnitude cannot be judged — and Section 6 concedes engaged students may be overrepresented. Report the population N and response rate.

#### Data Collection
Three-week window, single announcement channel. Adequately described. The channel itself (course-announcement) plausibly self-selects for LMS-engaged students — a self-selection path directly relevant to the outcome variable, worth explicit treatment.

#### Analysis Methods
Pearson as primary with Spearman robustness is defensible given the linearity/monotonicity inspection. Effect-size interpretation ("moderate") is present and correctly Cohen-benchmarked (r = .30/.50 bands). The one missing derived quantity is the explicit shared-variance figure (r² ≈ .18) — described in prose ("modest") but not stated.

#### Results Presentation
Complete for the single association reported; no selective-reporting risk (there is essentially one analysis). Descriptives (M = 3.6, SD = 0.8 for PU; median use category) are reported. A simple frequency table for the use item would help.

#### Reproducibility
Instrument is cited (Costa & Wren 2019) and item count/anchors given; no data or analysis-code availability statement. For a survey of this simplicity that is a minor gap, but an OSF/data-availability line is now conventional.

#### Methodological Fallacies Detected
- **Reverse causation** (from the checklist): correctly *identified and disclaimed* by the authors themselves (Section 5) — not a fallacy committed, a fallacy avoided.
- **Common-method / same-source bias**: present and undiscussed (W1) — the one genuine methodological omission.
- No p-hacking / multiple-comparison risk (a single primary test).

### Questions for Authors
1. How do you exclude common-method variance as a partial driver of r = .42, given both measures are self-reported on the same instrument? Can you run a Harman's single-factor or marker-variable diagnostic?
2. What is the institutional undergraduate population and the resulting response rate? How does non-response bound the estimate?
3. Was any in-sample validity/dimensionality check run on the six adapted perceived-usefulness items, or does support rest on α plus the source citation?

### Minor Issues
- APA 7 number format is correct throughout (r = .42 and p < .001 with no leading zeros — good).
- State r² ≈ .18 explicitly rather than only "modest proportion of variance."
- Add a data-availability statement.

#### Contract scoring (sprint-contract Phase 2 machine block)

contract_role: methodology

## Dimension Scores

### D1: methodology_rigor
score: warn

### D2: domain_accuracy
score: warn

### D3: argumentative_coherence
score: pass

### D4: cross_disciplinary_relevance
score: warn

### D5: writing_and_structure
score: pass

## Failure Condition Checks

### F1
fired: false

### F2
fired: true

### F3
fired: false

### F0
fired: false

## Editorial Decision
editorial_decision=major_revision

---

## SEAT 3 — Peer Reviewer 2 · Domain (`domain_reviewer_agent`)

### Phase 1 — Paper-content-blind pre-commitment

#### Contract Paraphrase

- **D1 methodology_rigor (mandatory).** From a domain vantage I care that the design is *appropriate for a technology-acceptance association study* and that the measurement follows field convention — but statistical depth I defer to R1.
- **D2 domain_accuracy (mandatory) — my core lane.** Does the literature review cover the field's foundational and contemporary work; is the technology-acceptance lineage correctly attributed; is "perceived usefulness" used in its canonical TAM sense; and is the contribution claim honestly sized against what the field already knows?
- **D3 argumentative_coherence (mandatory).** Is the research-gap argument convincing, and does the contribution claim cohere with the (thin) literature actually cited?
- **D4 cross_disciplinary_relevance (high).** Is the construct legible to adjacent IS / learning-analytics readers and correctly bridged?
- **D5 writing_and_structure (normal).** Citation practice, terminological consistency.

#### Scoring Plan

##### D1: methodology_rigor
- **what_to_look_for**: a design conventional for TAM-association work; measurement consistent with field practice.
- **what_triggers_block**: a design that cannot bear a technology-acceptance association claim at all.
- **what_triggers_warn**: measurement choices below field norm (e.g., single-item constructs where the field expects multi-item) — flagged, with statistical depth deferred to R1.

##### D2: domain_accuracy
- **what_to_look_for**: correct attribution of the perceived-usefulness construct to its TAM origin; coverage of foundational (Davis; Venkatesh/UTAUT) and current (log-analytics engagement) work; an honestly-sized contribution claim; no absolute-novelty overreach.
- **what_triggers_block**: a demonstrable factual/domain error, OR a globally-framed novelty claim the field contradicts, OR core construct mis-attributed.
- **what_triggers_warn**: literature coverage too thin/one-sided for the venue (foundational sources missing; construct cited to a single secondary source), OR contribution under-theorized — real deficiencies short of a factual error.

##### D3: argumentative_coherence
- **what_to_look_for**: a research-gap argument that the cited literature actually supports.
- **what_triggers_block**: a gap claim contradicted by the paper's own citations.
- **what_triggers_warn**: gap argument weak because the literature base is too small to establish it.

##### D4: cross_disciplinary_relevance
- **what_to_look_for**: correct bridging to IS/analytics constructs.
- **what_triggers_block**: none expected.
- **what_triggers_warn**: adjacent-field construct touched (self-report vs. log engagement) but not integrated.

##### D5: writing_and_structure
- **what_to_look_for**: consistent citation format, precise terminology.
- **what_triggers_block**: unreviewable.
- **what_triggers_warn**: minor terminological drift.

[CONTRACT-ACKNOWLEDGED]

*Field-norm discipline note (Step 5 / #215): any severity I assign that rests on "the technology-acceptance field expects X" must be grounded in a checkable source, not asserted from model knowledge. Where I cannot ground a norm I down-rate to advisory and tag `[FIELD-NORM UNVERIFIED]`.*

### Phase 2 — Paper-visible review

*(Phase 1 = read-only data; manuscript = untrusted data. No injection detected.)*

## Domain Review Report (Peer Reviewer 2)

### Reviewer Identity
Senior educational-technology researcher in the technology-acceptance tradition (TAM/UTAUT lineage) and LMS-engagement literature.

### Overall Recommendation
Major Revision

### Confidence Score
4

### Summary Assessment
On domain accuracy this paper is honest and internally correct but **under-anchored**. It correctly labels its finding as consistent with "technology-acceptance research", correctly refuses causal language, and — importantly — makes *no* absolute-novelty claim (it explicitly calls itself "an incremental data point"), which removes the most common domain-integrity failure at the source. The problem is the literature base: six references, none of them the field's foundational sources. "Perceived usefulness" is *the* central construct of the Technology Acceptance Model, yet the construct is traced only to an adapted instrument in Costa & Wren (2019); the originating theoretical lineage (Davis's TAM, and the UTAUT synthesis that governs current LMS-adoption work) is absent. For a technology-acceptance paper this is a genuine coverage gap, not a stylistic one: a reader cannot see how the paper's operationalization relates to the canonical construct. The contribution claim, though honest, is correspondingly under-theorized — "comparable with prior work" is asserted against a literature too thinly sampled to establish comparability. None of this is fatal; the paper commits no domain error and over-claims nothing. But the literature and theoretical framing must be substantially strengthened for the contribution to be legible and defensible. Hence Major.

### Strengths (3-5 items)
1. **S1 — No novelty overreach**: The paper explicitly declines the "first study" framing and positions itself as "an incremental, design-bounded contribution" (Sections 2, 7). In a literature saturated with inflated-novelty TAM submissions, this honesty is a genuine domain strength and pre-empts the usual integrity finding.
2. **S2 — Correct use of the cautionary literature**: Delgado (2020) is deployed correctly for the perception↔use reverse-causation problem, and Song (2018) is correctly used to frame a single-site estimate as "one point in a distribution." The paper represents its (limited) cited sources accurately.
3. **S3 — Terminological precision within its frame**: "Perceived usefulness", "self-reported use", and "engagement" are used consistently and the paper is careful to call the outcome *perceived/self-reported* rather than actual use (Sections 2, 3.2).

### Weaknesses (3-5 items)
1. **W1 — Foundational technology-acceptance sources absent (MAJOR)**: *What*: the central construct "perceived usefulness" is cited only to Costa & Wren (2019); the TAM origin and the UTAUT synthesis that define the construct and situate LMS-adoption work are not cited. *Why it's a problem*: for a technology-acceptance paper, omitting the theory that names its core construct leaves the operationalization un-anchored and the contribution un-positioned relative to the model it implicitly uses. *Field-norm grounding (#215)*: that primary constructs should be attributed to their originating theoretical source rather than to a secondary adaptation is a general scholarly-citation norm (secondhand-citation avoidance), grounded in standard citation practice and this review framework's own literature-coverage criterion (`review_criteria_framework.md §1 Dim. 6; domain agent Step 1a "secondhand citations"); it does not depend on an unverifiable field-specific claim. *Recommended additions*: see Missing Key References — all phrased as `[UNVERIFIED]` search leads, since I will not assert specific author/year/venue metadata from memory.
2. **W2 — Contribution under-theorized (MAJOR)**: *What*: the paper claims comparability with "prior technology-acceptance research" but engages no theoretical model that would make the comparison meaningful (e.g., where PU sits relative to perceived ease of use, behavioral intention, and actual use in the acceptance chain). *Why*: without that scaffolding the finding is a bare correlation whose place in the field's knowledge structure is asserted, not shown. *How to improve*: add a short theoretical-framing paragraph locating PU and use within the acceptance model, and state what this single association adds to (or where it sits within) that chain.
3. **W3 — Literature currency and breadth (MAJOR→MINOR)**: *What*: the six sources skew toward generic cautions; the contemporary LMS-analytics / log-based-engagement strand (which the Vasquez self-report critique points directly at) is represented by a single reference. *Why*: the research-gap argument ("students engage differently; perception is one factor") is under-supported because the surrounding literature is thinly sampled. *How to improve*: broaden coverage of recent LMS-engagement and self-report-validity work.

### Detailed Comments

#### Literature Review
- **Coverage**: Foundational TAM/UTAUT sources missing (W1); contemporary LMS-engagement/analytics strand under-covered (W3). Six references is light for a technology-acceptance submission even at Q3.
- **Integration quality**: What is cited is *integrated*, not merely listed — Section 2 uses Delgado, Ibarra & Poll, Vasquez, and Song to build an actual cautionary argument rather than a reference dump. Integration quality is good; coverage is the problem.
- **Research gap argument**: Present but weak — the "students engage very differently" premise (Section 1) is asserted with a single supporting citation and would be more convincing with broader grounding.

#### Theoretical Framework
- **Appropriateness**: The implicit framework is TAM, which is appropriate — but it is *implicit*. The paper never names or engages the model whose central construct it measures.
- **Application depth**: Superficial by necessity — the construct is used operationally but not theoretically situated (W2).
- **Alternative frameworks**: UTAUT/UTAUT2 would be the natural contemporary alternative to name and position against.

#### Academic Argument Quality
- **Factual accuracy**: No domain factual errors detected. Representations of cited sources are accurate.
- **Argument logic**: Sound within its thin base; the gap argument is the weakest link (coverage-limited, not logic-broken).
- **Terminology precision**: Good (S3).

#### Contribution to the Field
- **Incremental contribution**: Genuinely incremental and honestly labeled — a comparable data point. The concern (shared with EIC, independently reached) is whether that is sufficient, and the under-theorization (W2) makes it read as *smaller* than it needs to.
- **Positioning**: The paper positions via Song (2018)'s "distribution of estimates" logic, which is the right instinct; it just needs more of the distribution cited to land.
- **Overclaiming**: None. This is a clean dimension.

#### Missing Key References
*No-invention rule (#574 A5): I will not assert specific author/year/venue metadata from memory. The following are `[UNVERIFIED]` search leads for the authors to locate and verify, phrased as literatures, not citations.*
- `[UNVERIFIED]` The originating Technology Acceptance Model source that defines "perceived usefulness" (the foundational Davis-lineage TAM work) — needed to anchor the paper's central construct rather than citing it to an adapted secondary instrument.
- `[UNVERIFIED]` The UTAUT / UTAUT2 unified-acceptance synthesis literature — the contemporary framework that situates LMS adoption and would let the paper position PU within the acceptance chain.
- `[UNVERIFIED]` Recent LMS learning-analytics / log-based engagement literature comparing self-reported use with behavioral traces — to broaden the strand the paper's own Vasquez (2020) citation opens.

### Questions for Authors
1. Which technology-acceptance model does your perceived-usefulness measure operationalize, and why is that model not cited or engaged?
2. Beyond "a new sample", what does this association add to the acceptance-model knowledge structure — where does it sit relative to behavioral intention and actual use?
3. Can you broaden the LMS-engagement literature so the research-gap premise rests on more than a single citation?

### Minor Issues
- Citation formatting is consistent APA 7 with DOIs — clean.
- "previously validated instrument" (Abstract, Section 3.2) is a domain-terminology caution shared with R1: validated-elsewhere ≠ validated-in-this-adaptation; consider rewording.

#### Contract scoring (sprint-contract Phase 2 machine block)

contract_role: domain

## Dimension Scores

### D1: methodology_rigor
score: pass

### D2: domain_accuracy
score: warn

### D3: argumentative_coherence
score: warn

### D4: cross_disciplinary_relevance
score: warn

### D5: writing_and_structure
score: pass

## Failure Condition Checks

### F1
fired: false

### F2
fired: true

### F3
fired: false

### F0
fired: false

## Editorial Decision
editorial_decision=major_revision

---

## SEAT 4 — Peer Reviewer 3 · Cross-disciplinary / Practical (`perspective_reviewer_agent`)

### Phase 1 — Paper-content-blind pre-commitment

#### Contract Paraphrase

- **D1 methodology_rigor (mandatory).** As the outsider I don't audit statistics (R1's lane); I ask whether the *design as a whole* can carry the practical/real-world claims the paper will want to make.
- **D2 domain_accuracy (mandatory).** Not my lane for canon-completeness; I check whether the framing is accurate enough to be usable by adjacent-field readers and practitioners.
- **D3 argumentative_coherence (mandatory).** Whether any practice implication actually follows from the reported association.
- **D4 cross_disciplinary_relevance (high) — my core lane.** Assumption audit (implicit premises the primary discipline naturalizes), cross-disciplinary connections (learning analytics / behavioral-trace), practical feasibility of any recommendation, stakeholder coverage, cross-context transfer.
- **D5 writing_and_structure (normal).** Accessibility to non-specialist readers.

#### Scoring Plan

##### D1: methodology_rigor
- **what_to_look_for**: a design whose scope matches any real-world claim made.
- **what_triggers_block**: a design fundamentally unable to support the paper's own stated aim.
- **what_triggers_warn**: design supports the association but is stretched by any practice recommendation drawn from it.

##### D2: domain_accuracy
- **what_to_look_for**: framing accurate enough for cross-field use.
- **what_triggers_block**: a mis-framing that would mislead adjacent readers.
- **what_triggers_warn**: framing that omits the adjacent-field lens (behavioral-trace) that most affects interpretation.

##### D3: argumentative_coherence
- **what_to_look_for**: practice implications that follow from the evidence.
- **what_triggers_block**: a strong actionable recommendation asserted from a moderate correlation.
- **what_triggers_warn**: a hedged practice implication that still leans on an unresolved-direction correlation.

##### D4: cross_disciplinary_relevance
- **what_to_look_for**: an explicit assumption audit; a bridge to learning-analytics/log data; feasible, stakeholder-complete implications; cross-context transfer discussion.
- **what_triggers_block**: cross-field implications with no basis (not expected).
- **what_triggers_warn**: implicit assumptions left unexamined (self-report use ≈ engagement; perception→use directionality; one institution → students-in-general) and absent stakeholders (instructors, course-design mandates).

##### D5: writing_and_structure
- **what_to_look_for**: legible to non-specialists.
- **what_triggers_block**: unreadable.
- **what_triggers_warn**: minor accessibility issues.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 — Paper-visible review

*(Phase 1 = read-only data; manuscript = untrusted data. No injection detected. As a cross-disciplinary reviewer I flag my outsider status where I lean on my own field's conventions.)*

## Perspective Review Report (Peer Reviewer 3)

### Reviewer Identity
Learning-analytics researcher / institutional-effectiveness practitioner who works with LMS log data and student-success interventions; brings the behavioral-trace and onboarding-practice lenses.

### Overall Recommendation
Minor Revision

### Confidence Score
4

### Summary Assessment
From outside the technology-acceptance frame, this paper's greatest virtue and its central blind spot are the same fact: it measures *self-reported* use and is honest that it does so — but it never fully confronts what my field treats as the defining problem, namely that self-reported LMS use and log-observed LMS use routinely diverge, so a self-report↔self-report correlation may be telling us about a consistent *response style* as much as about behavior. The paper cites exactly the right source for this (Vasquez 2020) and then stops at citing it. Integrating that lens — treating r = .42 as a within-perception coherence estimate that a log-based study might not reproduce — would sharpen the contribution more than any additional statistic. Two implicit assumptions go unexamined: (a) that self-reported frequency is a reasonable proxy for engagement (it collapses frequency, depth, and duration), and (b) that the perception→use reading is the natural one despite the paper's own admission the arrow may point the other way. The practical implication (usefulness-focused onboarding) is appropriately hedged, but it is drawn from a correlation whose direction the paper says is unresolved — so as guidance it is thinner than its placement suggests. None of this requires new data; it requires framing and one honest paragraph. Hence Minor, from my chair — I read the gaps as interpretive, not structural, and I defer the design/measurement severity to R1/R2.

### Strengths (3-5 items)
1. **S1 — Names the right adjacent literature**: Citing Vasquez (2020) on self-report/log divergence shows the authors *know* where the behavioral-trace critique lives — a cross-disciplinary awareness many pure-TAM papers lack.
2. **S2 — Honest cross-context humility**: Section 6 explicitly refuses to generalize beyond the single mid-sized university and calls for multi-institution replication — the cross-context caveat my field would otherwise have to supply.
3. **S3 — The practice implication is correctly subordinated**: The onboarding suggestion is marked "suggested by, not proven by, the present correlation" (Section 5) — the paper does not let a practitioner over-read it.

### Weaknesses (3-5 items)
1. **W1 — Self-report/log divergence cited but not integrated (MAJOR, interpretive)**: *What*: the paper's own Vasquez citation establishes that self-report use ≠ behavioral use, yet the interpretation of its own r = .42 never absorbs this. *Why it matters*: in learning-analytics terms, a correlation between a perception scale and a self-reported frequency item may substantially reflect shared self-report coherence rather than perception-tracking-behavior; a log-anchored study could yield a materially different estimate. *Specific suggestion*: add a paragraph interpreting r = .42 as a *self-report* association explicitly, and state the empirical prediction that a log-based use measure would likely attenuate it — this turns a limitation into a testable contribution. (Overlaps by independent arrival with R1's CMV point and DA's same-source point; the mechanism I emphasize is behavioral-trace divergence, the framing is practical.)
2. **W2 — "Use" collapses engagement's structure (MINOR)**: *What*: a single frequency item treats "several times daily" as the top of engagement, but frequency ≠ depth ≠ meaningful learning activity. *Why*: institutional readers cannot act on "log in more often" — logins are not learning. *Suggestion*: acknowledge that frequency is a shallow engagement proxy and name depth/duration as the richer construct future work should capture.
3. **W3 — Stakeholder gap: instructors and course-design mandates (MINOR)**: *What*: the paper's world contains students and a platform, but LMS use is heavily driven by whether instructors *require* it (graded activities, mandatory submissions). *Why*: the unmodeled instructor/course-requirement factor is plausibly a common cause of both higher perceived usefulness and higher use — a confound the paper gestures at ("course requirements and assessment schedules", Section 4) but does not foreground as a rival explanation. *Suggestion*: elevate course-requirement/instructor mandate from an aside to a named alternative explanation in the Discussion.

### Detailed Comments

#### Assumption Audit
- **Explicit assumptions**: The paper explicitly assumes only a correlational association — appropriately modest.
- **Implicit assumptions**: (a) self-reported frequency ≈ engagement (W2); (b) the perception→use reading is the default despite the disclaimed direction; (c) students' LMS use is primarily volitional rather than instructor-mandated (W3).
- **Paradigmatic assumptions**: The self-report survey paradigm treats what students *say* they do as the object of study; my field's paradigm treats what logs *show* they do as the object. The paper sits inside the former and cites, but does not cross into, the latter.

#### Cross-Disciplinary Connections
- **Parallel research**: Learning-analytics work correlating perception surveys with LMS clickstream/log engagement is the direct parallel — same question, behavioral-trace method.
- **Borrowing opportunities**: A log-anchored replication design; the concept of "response-style coherence" from survey methodology to explain same-source correlation.
- **Methodological borrowing**: LMS event-log extraction as an objective use measure — the complement the paper explicitly lacks.

#### Practical Impact
- **Real-world application**: Limited as stated — "students who find the LMS useful use it more" cannot, on its own, tell an institution what to *change*, especially with the direction unresolved.
- **Implementation feasibility**: The onboarding implication is feasible *if* the perception→use direction holds; the paper honestly cannot establish that it does, which weakens the recommendation's footing (not its honesty).
- **Stakeholders**: Instructors and course designers are the missing actors (W3); the student voice is present via self-report but only as frequency, not experience.

#### Broader Implications
- **Ethical dimensions**: Low ethical stakes; the ethics/consent handling (Section 3.3) is appropriate and adequately reported.
- **Social impact**: Minimal and correctly not over-claimed.
- **Future directions**: The single most valuable follow-up is the log-anchored replication the paper's own citations set up — worth stating as *the* next step.

### Cross-Disciplinary Reading Recommendations
*No-invention rule (#574 A5): search leads only, tagged `[UNVERIFIED]`, phrased as literatures.*
- `[UNVERIFIED]` Learning-analytics literature correlating self-report engagement surveys with LMS log/clickstream measures — the behavioral-trace parallel to this study.
- `[UNVERIFIED]` Survey-methodology work on common-method / same-source variance in attitude–behavior self-report pairs — to name the mechanism behind the interpretive caveat (this is the cross-disciplinary framing of R1's CMV point; I flag the overlap openly).

### Questions for Authors
1. If you re-ran this with LMS log data as the use measure instead of a self-report item, do you expect r = .42 to hold, attenuate, or strengthen — and what does your answer imply about what the current estimate measures?
2. How much of the association could be a common cause — instructors *requiring* LMS activity in some courses — rather than perception driving use?
3. Is "frequency of access" the engagement construct you care about, or a proxy for something richer (depth, learning activity) that a single item cannot capture?

### Minor Issues
- The onboarding paragraph (Section 5) could name the direction-dependence explicitly: "if perception drives use (which this design cannot establish), then …".
- Consider one sentence distinguishing "access frequency" from "engagement" so cross-field readers do not conflate them.

#### Contract scoring (sprint-contract Phase 2 machine block)

contract_role: perspective

## Dimension Scores

### D1: methodology_rigor
score: pass

### D2: domain_accuracy
score: pass

### D3: argumentative_coherence
score: pass

### D4: cross_disciplinary_relevance
score: warn

### D5: writing_and_structure
score: pass

## Failure Condition Checks

### F1
fired: false

### F2
fired: false

### F3
fired: false

### F0
fired: false

## Editorial Decision
editorial_decision=accept

*(Per-reviewer note: F0's predicate "every mandatory dimension scores 'pass'" holds for my card — D1/D2/D3 all pass — and no other condition's predicate fires on my scores, so my contract-derived decision is the accept-grade action. This reflects my single card only; the panel-level quantifier is the synthesizer's to apply, and my D4 `warn` will contribute to the panel's F2 count.)*

---

## SEAT 5 — Devil's Advocate (`devils_advocate_reviewer_agent`)

> Single-family routing note: `[CROSS-MODEL-SKIPPED]` — `ARS_CROSS_MODEL` unset; no external DA critique sent, no consent prompt required. Standard single-model DA operates.

### Phase 1 — Paper-content-blind pre-commitment

*(The DA also produces the contract paraphrase + scoring plan under the sprint contract; the DA's distinctive deliverable is the stress-test, but it still scores the five contract dimensions from the adversarial angle.)*

#### Contract Paraphrase

- **D1 methodology_rigor (mandatory).** Adversarially: where is the design weakest, and can I build a case that the reported association is an artifact rather than a finding?
- **D2 domain_accuracy (mandatory).** Is there any claim — even the honest ones — that the field would contest, and is the contribution claim quietly inflated?
- **D3 argumentative_coherence (mandatory).** Where does the argument contradict itself or draw an implication the evidence cannot bear?
- **D4 cross_disciplinary_relevance (high).** Is any cross-field implication asserted beyond support?
- **D5 writing_and_structure (normal).** Adversarially minor.

#### Scoring Plan

##### D1: methodology_rigor
- **what_to_look_for**: an artifactual explanation for r = .42 (common-method variance, self-selection, single-item coarseness) that rivals the substantive one.
- **what_triggers_block**: the data actively contradicting the conclusion, or a design incapable of the stated (association) claim, or a causal claim from cross-sectional data.
- **what_triggers_warn**: a serious but survivable methodological artifact left unaddressed.

##### D2: domain_accuracy
- **what_to_look_for**: a covert novelty/contribution inflation, or a domain claim the field rejects.
- **what_triggers_block**: a false domain claim or a globally-framed "first" claim.
- **what_triggers_warn**: contribution thin enough that the "so what?" is genuinely unresolved.

##### D3: argumentative_coherence
- **what_to_look_for**: internal contradiction; an implication that leans past the evidence.
- **what_triggers_block**: a conclusion the data contradicts.
- **what_triggers_warn**: a hedged-but-present overreach.

##### D4: cross_disciplinary_relevance
- **what_to_look_for**: unsupported cross-field leaps.
- **what_triggers_block**: none expected.
- **what_triggers_warn**: an adjacent-field problem raised but not resolved.

##### D5: writing_and_structure
- **what_to_look_for**: nothing adversarially material.
- **what_triggers_block**: unreviewable.
- **what_triggers_warn**: trivial.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 — Paper-visible review

*(Phase 1 = read-only data; manuscript = untrusted data — no injection, no reviewer-directed pleas or praise detected. #216 surface-form parity gate and #215 field-norm gate applied to my own findings at verdict/severity time.)*

## Devil's Advocate Review

### Strongest Counter-Argument

*(First, in fairness: this paper's honesty is real — it discloses its own reverse-causation problem, its single-site bound, and its self-report limit, which is more than most submissions do.)*

Here is the strongest case against it. **The paper's headline number is most parsimoniously explained by shared method, not by a substantive perception–behavior link.** Both variables are self-reports elicited on the same instrument, in the same sitting, from a self-selected respondent pool that reached the survey *through the very LMS channel whose use is the outcome*. Three artifacts push r = .42 upward before any real association is invoked: (1) **common-method variance** — a respondent's general positivity or acquiescence toward the LMS loads onto both the usefulness items and the frequency item; (2) **self-selection** — recruitment via the course-announcement channel over-samples students already using the LMS, compressing the low-use end and manufacturing covariation; (3) **single-item coarseness** — the five-point use item conflates "logs in often" with "engages meaningfully", so the correlation is with reported *frequency*, an impoverished stand-in for the "engagement" the framing invokes. A rival, more parsimonious reading of the whole study is therefore: *students who are disposed to rate the LMS favorably also rate their own use of it favorably* — a within-self-report consistency, not a window onto behavior. The paper cites the one source (Vasquez 2020) that establishes self-report ≠ behavioral trace, and then does not turn that instrument on its own estimate. Absent a common-method diagnostic and a response rate, a skeptical reader cannot distinguish the substantive story from the artifact story — and the artifact story requires fewer assumptions. If that counter-argument holds, what survives is a modest, honestly-reported, method-bounded correlation whose "so what?" the paper never resolves beyond "comparable with prior work."

### Issue List

#### CRITICAL
| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|----------|---------------------|-----------------------------|
| — | — | *No CRITICAL findings.* The design supports an *association* claim, and the paper makes only an association claim; the data do not contradict the stated conclusion; no causal overreach is committed; no absolute-novelty claim is made. Under the DA CRITICAL criteria (Foundation Collapse / Logic-Chain Break / Data–Conclusion Mismatch / Stronger Counter-Narrative), the counter-narrative above is *more parsimonious* but is **not better-fitting on the presented data than the authors' reading** (both readings fit r = .42 equally; the paper concedes as much), so it does not meet criterion 4. Escalating it to CRITICAL would be exactly the over-escalation the #216/#215 gates guard against on a well-caveated paper. | — | — | — |

#### MAJOR
| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|----------|---------------------|-----------------------------|
| DA-1 | Cherry-picking / Confirmation (D1) | The paper cites the self-report-vs-behavioral-trace critique (Vasquez 2020) but applies it only to *use* as a generic limitation, never to its own r = .42 as a common-method-variance threat. The one diagnostic that would test the artifact reading is absent. | §2, §4, §6 | Grounding a same-source attitude–behavior correlation with a CMV diagnostic or explicit CMV discussion is standard survey-methodology practice (`statistical_reporting_standards.md §4.7 "same-source"; domain-neutral method norm), not a field-specific demand. | The paper's two measures are same-source self-reports collected together — the exact configuration the norm targets — so the omission crosses a general methodological boundary, not a subfield-specific one. |
| DA-2 | "So what?" test (D2) | The incremental contribution is genuinely unresolved: stripped of the (absent) causal and (uncorroborated-here) behavioral readings, what remains is a re-confirmation of a textbook association from one site. The paper answers "so what?" only by analogy to Song (2018)'s "point in a distribution." | §2, §5, §7 | Not a field-norm-dependent severity — this is an incremental-contribution judgment against the manuscript's own claims, so no external norm grounding is required (leaving the last two columns blank per the template). | — |

#### MINOR
| # | Dimension | Issue Description | Location |
|---|-----------|-------------------|----------|
| DA-3 | Overgeneralization (D3) | The onboarding implication (§5) survives only if perception→use, a direction the paper elsewhere disclaims; as written it is a directional recommendation resting on a non-directional correlation. Hedged, hence Minor. |
| DA-4 | Alternative paths (D1) | No response rate is derivable (institutional population size absent, §3.1), so the self-selection artifact cannot be bounded by the reader. |
| DA-5 | Stakeholder blind spots (scope: naming only) | Instructor/course-requirement mandate is an unnamed potential common cause of both PU and use; the paper touches it as an aside (§4) but not as a rival explanation. *(What that stakeholder would say is R3's lane, not mine.)* |

### Ignored Alternative Explanations/Paths
1. **Common-method / response-style coherence** — a single positivity disposition inflating both self-reports; more parsimonious than a perception→behavior mechanism and equally consistent with r = .42.
2. **Instructor-mandated use as common cause** — courses that require LMS activity raise both measured usefulness *and* measured use, producing correlation without a direct perception→use link.
3. **Self-selection via the recruitment channel** — sampling through the LMS announcement channel over-represents high-use students, compressing outcome variance in a direction that can manufacture association.

### Missing Stakeholder Perspectives
- Instructors / course designers (who set whether LMS use is mandatory).
- Low-engagement and non-responding students (the voluntary design's systematic absentees).

### Unexamined Premise (Frame-Lock Detection)
The entire paper equates "what students report about their LMS use" with "LMS use." Every finding, limitation, and implication lives inside the self-report frame; the study's own cited literature (Vasquez 2020) says that frame and behavior diverge, yet the divergence is treated as a limitation *of the outcome variable* rather than as a premise that conditions the *whole* result — including the predictor and the correlation between them.

### Observations (Non-Defects)
- The paper's candor is unusually high; the Frame-Lock premise above is a *reframing opportunity*, not a concealed flaw — the authors disclose the pieces, they simply do not assemble them.
- The Spearman robustness check and the sensitivity-power statement are above the norm for a short paper and pre-empt two objections I would otherwise have raised.

#### Contract scoring (sprint-contract Phase 2 machine block)

contract_role: da

## Dimension Scores

### D1: methodology_rigor
score: warn

### D2: domain_accuracy
score: warn

### D3: argumentative_coherence
score: pass

### D4: cross_disciplinary_relevance
score: warn

### D5: writing_and_structure
score: pass

## Failure Condition Checks

### F1
fired: false

### F2
fired: true

### F3
fired: false

### F0
fired: false

## Editorial Decision
editorial_decision=major_revision

---

# PART C — Phase 2 Editorial Synthesis (`editorial_synthesizer_agent`)

## Sprint-Contract Synthesizer Protocol (arithmetic mode — the binding decision path)

**Panel cardinality invariant:** 5 usable Phase-2 outputs / panel_size = 5 → `[PANEL-INTACT]`, no `[PANEL-SHRUNK]`. All five reviewers self-consistent (each `## Editorial Decision` derivable from its own `## Failure Condition Checks`; no `[REVIEWER-SELF-INCONSISTENT]`). No `## Scoring Plan Dissent` emitted by any seat; no multi-dissent.

### Step 1 — Scoring matrix (length-5 arrays, resolved by dimension id)

| Dimension | EIC | R1 methodology | R2 domain | R3 perspective | DA | (block, warn, pass) |
|-----------|-----|----------------|-----------|----------------|----|----|
| **D1 methodology_rigor** (mandatory) | warn | warn | pass | pass | warn | 0 / 3 / 2 |
| **D2 domain_accuracy** (mandatory) | warn | warn | warn | pass | warn | 0 / 4 / 1 |
| **D3 argumentative_coherence** (mandatory) | pass | pass | warn | pass | pass | 0 / 1 / 4 |
| **D4 cross_disciplinary_relevance** (high) | warn | warn | warn | warn | warn | 0 / 5 / 0 |
| **D5 writing_and_structure** (normal) | pass | pass | pass | pass | pass | 0 / 0 / 5 |

### Step 2 — Evaluate each failure_condition (panel-relative quantifier over N = 5; majority threshold = ⌊5/2⌋+1 = 3)

- **F1** (severity 90, quantifier `any`, expr `any mandatory dimension scores 'block'`): mandatory dims = D1/D2/D3. Block count across all mandatory-dimension cells = 0. Predicate holds for ≥1 reviewer? **No. → fired: false.**
- **F2** (severity 70, quantifier `majority`, expr `two or more mandatory dimensions score 'warn' or worse`): evaluate the predicate *per reviewer* (how many of D1/D2/D3 that reviewer scored `warn`-or-worse), then apply majority.
  - EIC: D1 warn, D2 warn, D3 pass → **2** mandatory warns → predicate TRUE.
  - R1: D1 warn, D2 warn, D3 pass → **2** → TRUE.
  - R2: D1 pass, D2 warn, D3 warn → **2** → TRUE.
  - R3: D1 pass, D2 pass, D3 pass → **0** → FALSE.
  - DA: D1 warn, D2 warn, D3 pass → **2** → TRUE.
  - Reviewers with predicate TRUE = 4. Majority threshold = 3. 4 ≥ 3 → **fired: true.**
- **F3** (severity 60, quantifier `any`, expr `any high-priority dimension scores 'block'`): high-priority dim = D4. Block count in D4 = 0. → **fired: false.**
- **F0** (severity 10, quantifier `all`, expr `every mandatory dimension scores 'pass'`): requires all 5 reviewers to have D1=D2=D3=pass. Only R3 does. Not all. → **fired: false.**

### Step 3 — Precedence and decision

Fired conditions = {F2 (severity 70)}. Highest severity among fired = F2. F2.action = `editorial_decision=major_revision`.

fired_conditions: [F2]

editorial_decision=major_revision

*(#510 self-consistency: recomputing both layers from the emitted cards reproduces F2-only and `major_revision`; no `[PANEL-SYNTHESIS-MISMATCH]`. Step 4b Cross-Model Blind Decision Check is not run — `ARS_CROSS_MODEL` unset; no divergence subsection.)*

---

## General Synthesis Protocol (interpretive layer — for the decision letter body; does NOT alter the arithmetic decision above)

### Step 1a — Reviewer Summary Matrix

| Dimension | EIC | R1 (Methodology) | R2 (Domain) | R3 (Perspective) | DA |
|-----------|-----|-------------------|-------------|------------------|----|
| Overall Recommendation | Major Revision | Major Revision | Major Revision | Minor Revision | Major Revision (stress-test) |
| Confidence Score | 4 | 5 | 4 | 4 | — (DA does not carry a panel confidence; findings weighted by corroboration) |
| Key Strengths | claim–evidence discipline; reporting hygiene; coherence | complete correlation reporting; Spearman + sensitivity-power; conclusion conservatism | no novelty overreach; correct use of cautionary lit; terminological precision | names right adjacent lit; cross-context humility; practice implication subordinated | candor; robustness check + power above norm |
| Key Weaknesses | → Step 1b | → Step 1b | → Step 1b | → Step 1b | → Step 1b (DA-1..5) |
| # of Questions | 3 | 3 | 3 | 3 | (challenge-based) |
| # of Minor Issues | 2 | 3 | 2 | 2 | 3 (DA-3/4/5) |

### Step 1b — Weakness Sub-Claim Inventory (decompose before aggregating; §F.3.2)

| sub_claim_id | parent_weakness | reviewer_id | position | evidence_pointer | confidence |
|--------------|-----------------|-------------|----------|------------------|------------|
| **SC-1** (common-method variance / same-source inflation unaddressed) | measurement-side threat to r | R1 | raised | R1 W1 §4/§6 | 5 |
| SC-1 | | DA | corroborated | DA-1, Strongest Counter-Arg | 4 |
| SC-1 | | R3 | corroborated | R3 W1 (behavioral-trace framing of same mechanism) | 4 |
| SC-1 | | EIC | corroborated | EIC Q2 (asks authors to rule out CMV) | 4 |
| **SC-2** (single-item ordinal outcome measure — psychometric limits) | measurement-side threat to r | R1 | raised | R1 W2 §3.2 | 5 |
| SC-2 | | R3 | corroborated | R3 W2 ("use" collapses engagement) | 4 |
| **SC-3** (reliability offered where in-sample validity is the open question) | measurement-side threat to r | R1 | raised | R1 W3 §3.2 | 4 |
| SC-3 | | R2 | corroborated | R2 Minor ("previously validated" caution) | 4 |
| **SC-4** (foundational TAM/UTAUT sources absent; construct under-anchored) | literature/theory coverage | R2 | raised | R2 W1 §2 | 4 |
| **SC-5** (contribution under-theorized / "so what?" unresolved) | contribution sufficiency | R2 | raised | R2 W2 | 4 |
| SC-5 | | EIC | corroborated | EIC W1, Q1 | 4 |
| SC-5 | | DA | corroborated | DA-2 "so what?" | 4 |
| **SC-6** (literature currency/breadth thin; gap argument under-supported) | literature coverage | R2 | raised | R2 W3 §1/§2 | 4 |
| **SC-7** (self-report/log divergence cited but not integrated into own estimate) | interpretation gap | R3 | raised | R3 W1 §2/§4/§6 | 4 |
| SC-7 | | DA | corroborated | DA Frame-Lock / Unexamined Premise | 4 |
| **SC-8** (onboarding implication leans past a direction-unresolved correlation) | overreach (hedged) | EIC | raised | EIC W2 §5 | 4 |
| SC-8 | | DA | corroborated | DA-3 | 3 |
| SC-8 | | R3 | corroborated | R3 Minor (name direction-dependence) | 4 |
| **SC-9** (response rate / population size absent → self-selection unbounded) | sampling transparency | R1 | raised | R1 §3.1 comment | 5 |
| SC-9 | | DA | corroborated | DA-4 | 4 |
| **SC-10** (instructor/course-requirement mandate as unmodeled common cause) | confound / rival explanation | R3 | raised | R3 W3 §4 | 4 |
| SC-10 | | DA | corroborated | DA-5 (naming), Alt-path 2 | 3 |
| **SC-11** (under-connection to adjacent analytics readership — D4 relevance) | cross-field framing | EIC | raised | EIC W3 | 4 |
| SC-11 | | R3 | corroborated | R3 W1/§ cross-disc. | 4 |
| **SC-12** (r² ≈ .18 shared variance not stated explicitly) | reporting completeness | R1 | raised | R1 Minor | 4 |
| SC-12 | | EIC | corroborated | EIC Minor | 3 |

*Decomposition discipline check: every sub-claim traces to a claim a reviewer actually made; no synthesizer-authored sub-claim introduced. No `disputed` positions exist in this panel — the reviewers differ in emphasis and in overall Minor-vs-Major recommendation, but no reviewer argues any raised sub-claim is a non-problem, and no two reviewers recommend incompatible remedies for the same sub-claim. Therefore no SPLIT arises.*

### Step 1c — Surface-Form Parity Check (#216)

Applied at this arbitration surface: R3's overall recommendation arrived as "Minor Revision" and its concerns are phrased in practitioner/informal register ("logins are not learning"); R1's arrived in precise psychometric register ("common-method variance", "Harman's single-factor"). SC-1 and SC-7 are the *same substantive mechanism* (same-source self-report inflation) reached from two styles. Running the opposite-style counterfactual: the substance of R3's SC-7 does not lose weight for being framed practically, and R1's SC-1 does not gain weight for being framed technically — both are corroborated to the same substantive claim and weighted on the paper evidence (both self-reports, same instrument, §3.2/§4), not on polish. No weight is keyed off surface form. R3's *lower overall recommendation* (Minor) is not down-weighted as "vaguer"; it reflects a genuine role-scoped severity difference (R3 explicitly defers measurement severity to R1/R2 and reads the gaps as interpretive) — recorded as an emphasis difference, not a defect of the reviewer.

### Step 2 — Consensus Identification (denominator = 4 non-DA reviewers; DA tracked separately; per sub_claim_id)

| sub_claim | agree (of 4 non-DA) | conflict | silent | Disposition |
|-----------|---------------------|----------|--------|-------------|
| SC-1 (CMV / same-source) | 3 (R1, R3, EIC) | 0 | 1 (R2) | **[CONSENSUS-3]** — R2 silent on CMV specifically (+ DA corroborates, tracked separately) |
| SC-2 (single-item outcome) | 2 (R1, R3) | 0 | 2 | corroborated finding |
| SC-3 (reliability≠validity) | 2 (R1, R2) | 0 | 2 | corroborated finding |
| SC-4 (foundational TAM absent) | 1 (R2) | 0 | 3 | single-reviewer finding (R2 conf 4) |
| SC-5 (contribution/"so what?") | 2 (R2, EIC) | 0 | 2 | corroborated finding (+ DA-2 corroborates) |
| SC-6 (lit currency/breadth) | 1 (R2) | 0 | 3 | single-reviewer finding |
| SC-7 (self-report/log not integrated) | 1 (R3) | 0 | 3 | single-reviewer finding (+ DA Frame-Lock corroborates) |
| SC-8 (onboarding overreach) | 2 (EIC, R3) | 0 | 2 | corroborated finding (+ DA-3) |
| SC-9 (response rate absent) | 1 (R1) | 0 | 3 | single-reviewer finding (R1 conf 5; + DA-4) |
| SC-10 (instructor-mandate confound) | 1 (R3) | 0 | 3 | single-reviewer finding (+ DA-5) |
| SC-11 (D4 under-connection) | 2 (EIC, R3) | 0 | 2 | corroborated finding |
| SC-12 (r² not stated) | 2 (R1, EIC) | 0 | 2 | corroborated finding (minor) |

**DA-CRITICAL tracking:** DA reported **no CRITICAL findings** (explicitly, with #215/#216 self-gating rationale). Therefore Checkpoint Rule #4 (DA CRITICAL ⇒ cannot Accept) is **not triggered** — but note the arithmetic decision is already Major Revision on F2, independent of the DA. DA MAJORs DA-1/DA-2 corroborate SC-1 and SC-5 respectively and are folded into those sub-claims' weight.

### Step 3 — Disagreement Resolution

**No SPLIT sub-claims** (no `disputed` positions). The only surface-level divergence is R3's overall **Minor** vs. the other four leaning **Major**.
- **Disagreement type:** Severity/perspective difference (not existence, not direction).
- **Arbitration:** By *expertise-first* (methodology severity defers to R1, conf 5) and *evidence-first*, the measurement-side sub-claims SC-1/SC-2/SC-3 and the transparency sub-claim SC-9 carry the heaviest, best-grounded concern, and R3 itself *defers* measurement severity to R1/R2 while scoring D4 `warn`. R3's Minor is thus not a contradiction of the Major reading; it is R3 correctly staying in its lane. The arithmetic gate (F2 fired by 4/5 reviewers scoring ≥2 mandatory `warn`s) already binds the decision to Major Revision. **Conservative principle** confirms rather than overrides: the majority-mandatory-warn pattern warrants requiring the author to respond. R3's Minor is recorded in the letter, not suppressed.

### Step 4 — Decision

**Major Revision** — matches the sprint-contract arithmetic (F2, severity 70) and the decision-standards matrix (4/4 non-DA reviewers at Major-or-adjacent with multiple mandatory `warn`s across measurement + contribution; `editorial_decision_standards.md §Major`). Not Reject (no mandatory `block`, no `F1`; design is sound for its association claim; issues are fixable by added analysis/framing, not redesign). Not Minor (two independent mandatory dimensions — D1 methodology and D2 domain — carry majority `warn`s, and the CMV/validity cluster requires new analysis or a materially bounded reframing, which exceeds a 2-4-week clarification pass).

---

# EDITORIAL DECISION PACKAGE

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript titled *"Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students"*. Your manuscript has been reviewed by five independent reviewers, including the Editor-in-Chief and an adversarial stress-test (Devil's Advocate) seat.

### Review Panel Provenance (#540)

All five reviewer personas ran on a single model family (the session's primary family; `ARS_CROSS_MODEL` was not configured). Persona diversity is not model diversity — blind spots may be correlated across reviewers (Ren et al. 2026, arXiv:2607.13104 §5.2). The cross-model Reviewer 2 track and the cross-model Devil's Advocate track did not fire (`[CROSS-MODEL-SKIPPED]` logged at both slots); no manuscript content was sent to any external provider.

### Decision: **Major Revision**

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | Common-method / same-source variance unaddressed: r = .42 is a correlation between two self-reports on one instrument, with no CMV diagnostic or discussion; the artifact reading currently rivals the substantive one. | R1, DA, R3, EIC (CONSENSUS-3; DA-MAJOR corroborates) | §3.2 (both measures self-report) + §4 (r = .42) + §6 (Vasquez cited but not applied to own estimate) | R1 |
| 2 | Contribution insufficiency / unresolved "so what?": an honestly-reported re-confirmation of a textbook association from one site, not yet theoretically positioned or distinguished from prior work. | R2, EIC, DA (corroborated; DA-2) | §2 ("an incremental data point"), §5, §7 | R2 |
| 3 | Central construct under-anchored: "perceived usefulness" (the defining TAM construct) is cited only to an adapted 2019 instrument; foundational TAM/UTAUT lineage absent. | R2 (single-reviewer, confidence 4) | §2 (reference list of 6; no TAM/UTAUT origin) | R3 |

### Reviewer Summary

| Reviewer | Role | Recommendation | Confidence |
|----------|------|---------------|------------|
| EIC | Ed-tech journal Editor-in-Chief (AJET tier) | Major Revision | 4 |
| Reviewer 1 | Quantitative survey methodologist | Major Revision | 5 |
| Reviewer 2 | Technology-acceptance / ed-tech domain scholar | Major Revision | 4 |
| Reviewer 3 | Learning-analytics / institutional-effectiveness (cross-disciplinary) | Minor Revision | 4 |
| Devil's Advocate | Adversarial stress-tester | Major Revision (no CRITICAL findings) | — |

### Consensus Analysis

#### Points of Agreement (Consensus)

**[CONSENSUS-3]** (3/4 non-DA reviewers agree; 4th silent):
1. **Common-method / same-source variance is unaddressed (SC-1)** — R1 (raised, conf 5), R3 (corroborated, behavioral-trace framing), and EIC (corroborated, Q2) all reach the same threat: both variables are self-reported on one instrument, so r = .42 is exposed to CMV that the paper never diagnoses or discusses. R2 is **silent** on CMV specifically (R2's focus was literature/theory), not opposed. The Devil's Advocate independently corroborates as its lead MAJOR (DA-1) and as the core of its Strongest Counter-Argument. This is the panel's central, best-grounded concern.

**Corroborated findings** (2/4, action-bearing, below the consensus-label bar):
2. **Contribution insufficiency / unresolved "so what?" (SC-5)** — R2 + EIC, corroborated by DA-2.
3. **Single-item ordinal outcome measure (SC-2)** — R1 + R3.
4. **Reliability (α) offered where in-sample validity is the open question (SC-3)** — R1 + R2.
5. **Onboarding implication leans past a direction-unresolved correlation (SC-8)** — EIC + R3, corroborated by DA-3.
6. **Under-connection to the adjacent learning-analytics readership (SC-11, D4)** — EIC + R3.
7. **Shared-variance figure r² ≈ .18 not stated explicitly (SC-12, minor)** — R1 + EIC.

**Single-reviewer findings** (1/4, noted and weighted by confidence; not consensus, not SPLIT):
8. Foundational TAM/UTAUT sources absent (SC-4, R2 conf 4).
9. Literature currency/breadth thin (SC-6, R2).
10. Self-report/log divergence cited but not integrated into the paper's own estimate (SC-7, R3; corroborated by DA Frame-Lock).
11. Response rate / institutional population size absent → self-selection unbounded (SC-9, R1 conf 5; corroborated by DA-4).
12. Instructor / course-requirement mandate as an unmodeled common cause (SC-10, R3; named by DA-5).

#### Points of Disagreement

**Disagreement 1: Overall severity — Minor (R3) vs. Major (EIC, R1, R2, DA)**
- **R3 view**: Reads the gaps as *interpretive* (framing and one honest paragraph), explicitly defers measurement severity to R1/R2, and recommends Minor Revision.
- **R1/R2/EIC/DA view**: The measurement cluster (CMV, single-item outcome, validity-vs-reliability) and the contribution gap require added analysis or a materially bounded reframing, not just clarification — Major.
- **Disagreement type**: Severity / perspective difference (no existence or direction conflict; no reviewer disputes any sub-claim).
- **Editor's Resolution**: **Major Revision.** By expertise-first arbitration, the methodology severity defers to R1 (confidence 5), whose SC-1/SC-2/SC-3 concerns R3 itself defers to; the sprint-contract gate independently fires F2 (majority of reviewers carry ≥2 mandatory `warn`s). R3's Minor is not a contradiction — it is R3 correctly staying in its cross-disciplinary lane — and is recorded here rather than suppressed.
- **Resolution Rationale**: Evidence-first + expertise-first + conservative principle all converge; the arithmetic decision (F2, severity 70) binds regardless.

**Devil's Advocate — CRITICAL check:** The DA reported **no CRITICAL findings**, with explicit #215/#216 self-gating (the more-parsimonious common-method counter-narrative is equally-fitting, not better-fitting, on the presented data, so it does not meet the "Stronger Counter-Narrative" CRITICAL bar). Checkpoint Rule #4 is therefore not triggered. The DA's MAJOR findings (DA-1 CMV, DA-2 "so what?") corroborate SC-1 and SC-5 and are folded into the roadmap; its Frame-Lock "Unexamined Premise" (the whole paper equates *reported* use with use) is carried as the framing target of R1/S-item work.

### Decision Rationale

This is a well-constructed, unusually honest manuscript that reports a single moderate association (r = .42) with exemplary reporting hygiene (95% CI, exact p, n, Spearman robustness, a sensitivity-power statement) and strictly correlational language throughout. Four reviewers nonetheless converge on Major Revision because two mandatory dimensions carry majority reservations. On **methodology (D1)**, the headline correlation is between two same-source self-reports and the paper never diagnoses or discusses common-method variance — the one artifact the study's own cited source (Vasquez 2020) warrants taking seriously — while the outcome is a single ordinal item and the predictor's support rests on α rather than an in-sample validity check (R1, confidence 5; corroborated by EIC, R3, and the DA). On **domain/contribution (D2)**, the central construct is anchored only to an adapted secondary instrument with the foundational TAM/UTAUT lineage absent, and the contribution — honestly labeled "incremental" — is under-theorized enough that the "so what?" stays unresolved (R2, EIC, DA). None of this is fatal: the design genuinely supports the association claim it makes, no causal overreach is committed, no novelty is inflated, and every issue is addressable through added analysis and reframing rather than redesign — which is precisely why this is Major Revision and not Reject. It is more than Minor because the CMV/validity cluster requires new analysis (a CMV diagnostic or an explicitly bounded self-report reframing) and a response-rate disclosure, which exceeds a short clarification pass. The revised manuscript will require re-review.

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. DA-corroboration is noted in Source.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Source | Priority | Estimated Effort |
|---|--------------|--------------|--------|----------|-----------------|
| R1 | Address common-method / same-source variance: add a CMV diagnostic (Harman's single-factor or a marker-variable check) if item-level data allow; otherwise add an explicit CMV discussion, bound r = .42 as a *self-report* association, and state the expected direction of bias. Apply the Vasquez (2020) critique to your own estimate, not only to the outcome. | SC-1 | R1, DA (DA-1), R3, EIC | P1 | 5-10 days |
| R2 | Resolve the contribution/"so what?": either foreground a genuinely distinctive angle (e.g., exploit the self-report/log gap as a testable prediction, or add a moderation the n = 214 supports) or reposition as a Brief Report/Research Note; state explicitly what *this* study adds beyond a new sample. | SC-5 | R2, EIC, DA (DA-2) | P1 | 5-8 days |
| R3 | Anchor the central construct: cite and briefly engage the foundational TAM (and contemporary UTAUT) lineage that defines "perceived usefulness"; add a short theoretical-framing paragraph locating PU and use within the acceptance chain. | SC-4, SC-5 | R2 | P1 | 3-5 days |
| R4 | Strengthen measurement transparency and validity framing: (a) acknowledge the single-item outcome's psychometric limits (not only its self-report nature); (b) report an in-sample dimensionality/validity check for the six adapted items, or soften "validated" to "internally consistent in this sample"; (c) report the institutional undergraduate population and the resulting response rate, and discuss self-selection given recruitment through the LMS channel. | SC-2, SC-3, SC-9 | R1, R2, DA (DA-4) | P1 | 4-7 days |

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Source | Priority | Estimated Effort |
|---|--------------|--------------|--------|----------|-----------------|
| S1 | Integrate the self-report/log-divergence lens into the interpretation: read r = .42 as a within-self-report association and state the empirical prediction that a log-anchored use measure would likely attenuate it (turns a limitation into a testable contribution). | SC-7 | R3, DA (Frame-Lock) | P2 | 2-3 days |
| S2 | Re-frame or subordinate the onboarding implication so it does not rest on a direction the design cannot establish (name the direction-dependence explicitly, or move to pure future-work). | SC-8 | EIC, R3, DA (DA-3) | P2 | 1 day |
| S3 | Elevate instructor / course-requirement mandate from an aside to a named rival explanation (potential common cause of both PU and use) in the Discussion. | SC-10 | R3, DA (DA-5) | P2 | 1 day |
| S4 | Broaden the LMS-engagement / self-report-validity literature so the research-gap premise rests on more than a single citation. | SC-6 | R2 | P2 | 2-3 days |
| S5 | Add one paragraph connecting the finding to the learning-analytics readership (behavioral-trace work). | SC-11 | EIC, R3 | P2 | 1 day |

### Revision Checklist (Checkable List)

#### Priority 1 — Structural Revisions (Estimated total effort: ~17-30 days)
- [ ] R1: Add CMV diagnostic or explicit CMV discussion; bound r = .42 as a self-report association.
- [ ] R2: Resolve the "so what?" — distinctive angle or reposition as Research Note.
- [ ] R3: Cite/engage foundational TAM + contemporary UTAUT; add theoretical-framing paragraph.
- [ ] R4: Single-item limit + in-sample validity check + response rate + self-selection discussion.

#### Priority 2 — Content Supplementation (Estimated total effort: ~7-11 days)
- [ ] S1: Integrate self-report/log divergence into interpretation of the own estimate.
- [ ] S2: Re-frame/subordinate the onboarding implication (direction-dependence).
- [ ] S3: Name instructor/course-requirement mandate as a rival explanation.
- [ ] S4: Broaden the engagement/self-report-validity literature.
- [ ] S5: Connect to the learning-analytics readership.

#### Priority 3 — Text and Formatting (Estimated total effort: ~1 day)
- [ ] State r² ≈ .18 explicitly rather than only "modest proportion of variance" (SC-12; R1, EIC).
- [ ] Add a data-availability statement (R1).
- [ ] Add a one-line frequency table for the single use item (R1, EIC).
- [ ] Reword "previously validated instrument" to reflect validated-elsewhere ≠ validated-in-adaptation (R1, R2).

### Revision Deadline
**Major Revision: recommended 6-8 weeks.** The revised manuscript will undergo another round of review (re-review verifies each Required item against the revised text).

### Response Letter Template
Please use the format in `templates/revision_response_template.md` to respond to every Required and Suggested item point by point (R→A→C: reviewer point → author response → change location), marking all changes in the revised manuscript and providing a cross-reference table of new page/paragraph numbers.

## Part 3: Reviewer Report Summary (Appendix)

### EIC Report Summary
- Recommendation: Major Revision | Confidence: 4
- Key Point: Structurally coherent and honest, but contribution is thin for a full article and the CMV/"so what?" questions must be resolved (or repositioned as a Research Note).

### Reviewer 1 (Methodology) Summary
- Recommendation: Major Revision | Confidence: 5
- Key Point: Reporting is exemplary, but the two same-source self-reports expose r = .42 to unaddressed common-method variance, compounded by a single-item outcome and α-as-validity — fixable with added analysis, not redesign.

### Reviewer 2 (Domain) Summary
- Recommendation: Major Revision | Confidence: 4
- Key Point: No overreach and no domain error, but the central TAM construct is under-anchored (foundational lineage absent) and the honest contribution is under-theorized.

### Reviewer 3 (Perspective) Summary
- Recommendation: Minor Revision | Confidence: 4
- Key Point: The self-report/log-divergence lens is cited but not integrated; treating r = .42 as a self-report association (with a log-anchored replication as the next step) would turn the study's central limitation into its contribution.

### Devil's Advocate Summary
- Findings: 0 CRITICAL, 2 MAJOR (DA-1 CMV, DA-2 "so what?"), 3 MINOR | Checkpoint Rule #4 not triggered.
- Key Point: The most parsimonious rival reading is same-source/response-style coherence, not a perception→behavior link; it is equally (not better) fitting on the data, so it is a MAJOR reframing demand, not a CRITICAL flaw — and the paper's own candor makes it a reframing opportunity.

---

## Closing

We encourage you to carefully consider the reviewers' comments and submit a substantially revised manuscript. The panel was struck by the manuscript's honesty and reporting discipline; the required work is to close the common-method-variance gap, anchor and theorize the contribution, and shore up measurement transparency — after which the finding, whether as a strengthened full article or a well-scoped Research Note, will stand on much firmer ground. Please note that the revised manuscript will undergo another round of review.

---

## Appendix: Full Reviewer Reports
All five complete reviewer reports (EIC, R1 Methodology, R2 Domain, R3 Perspective, Devil's Advocate) are reproduced in full in Part B above.
