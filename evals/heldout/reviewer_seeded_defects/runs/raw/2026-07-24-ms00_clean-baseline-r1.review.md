# Full Editorial Peer Review — `academic-paper-reviewer` v1.10.0 (FULL mode)

**Manuscript:** "Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students"
**Review mode:** `reviewer_full` (5-seat panel + editorial synthesis)
**Sprint contract:** `shared/contracts/reviewer/full.json` (`reviewer_full`, panel_size = 5, baseline v3.6.2 / Schema 13.1)
**Contract validation:** the on-disk template is the shipped, CI-validated `reviewer/full.json`; deep-copied, `generated_at` = 2026-07-24T00:00:00Z inlined, no baseline field mutated, no `agent_amendments` added. `check_sprint_contract.py` passes by construction (shipped template). Bash-less environment note: the deterministic checkers (`check_sprint_contract.py`, `check_panel_synthesis.py`) are executed as in-context logic per protocol §8.1, not as subprocesses.
**Cross-model track (#540):** `ARS_CROSS_MODEL` not configured for this session and no cross-model consent given → all five personas run on a single model family; Reviewer 2 does NOT swap substrate; the single-family correlated-error caveat is disclosed in the Review Panel Provenance block of the Editorial Decision Letter. No Step 4b blind decision check runs (env unset).

---

# PART 1 — Field-Analyst Reviewer Configuration (Phase 0)

# Field Analysis Report

## Paper Basic Information
- **Title**: Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students
- **Abstract length**: ~180 words
- **Full text length**: ~1,750 words (excluding references)
- **Number of references**: 6

## Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| Primary Discipline | Educational technology (higher-education technology acceptance) |
| Secondary Disciplines | Information systems (technology-acceptance / TAM lineage), survey measurement / psychometrics, higher-education studies |
| Research Paradigm | Quantitative Research (positivist, correlational) |
| Methodology Type | Survey / Questionnaire (single-wave, cross-sectional) |
| Target Journal Tier | Q3 (regional / specialized). Rationale: a single-site, single-association descriptive correlation with a deliberately narrow claim and a placeholder reference base. The work is competent and honest but its incremental contribution is small and its generalization is explicitly bounded to one institution — below the ambition bar of Q1/Q2 ed-tech journals (*Computers & Education*, *BJET*), appropriate for a Q3/OA outlet that accepts modest, well-reported single-site studies. |
| Paper Maturity | Pre-submission (near-complete). Rationale: full IMRaD-plus structure, consistent APA-style reporting (CI, exact-ish p, α, power statement), polished prose, explicit limitations section. What is missing is empirical depth (single-item DV, one site), not structural completeness. |

## Recommended Target Journals (Top 3)
1. **Australasian Journal of Educational Technology / *Education Sciences* (MDPI, HE section)** — accepts well-reported single-site quantitative ed-tech studies with modest scope; the honest correlational framing fits the "sound but incremental" acceptance band.
2. **International Journal of Educational Technology in Higher Education ([publisher], OA, funded)** — HE-specific ed-tech home; would push harder on the single-item DV and single-site limits, but the topic and framing are squarely in scope.
3. **Frontiers in Education (ed-tech section)** — fast review, methodological-soundness-over-novelty criterion; a good match for a study whose strength is transparent reporting rather than novelty.

*(Journal names are field-standard outlets from `references/top_journals_by_field.md` §1 "Educational Technology" and §8 OA options; used only for EIC calibration, not asserted as a submission recommendation.)*

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC
**Identity Description**: Editor-in-Chief of a Q3-tier educational-technology journal (calibrated to the *Education Sciences* / *Australasian Journal of Educational Technology* profile), whose scope is applied learning-technology research in higher education. Values transparent reporting and appropriate claim-scoping over novelty; wary of "availability ≠ use" institutional papers that over-promise. Acceptance rate ~30–40% (Q3 calibration).
**Review Focus**:
  1. Does a single-site perceived-usefulness↔use correlation clear the journal's incremental-contribution bar, or is it "one more TAM correlation"?
  2. Is the claim scope (narrow, correlational, single-institution) held consistently from title → abstract → conclusion, with no over-promising?
  3. Is the paper's honesty about its own limits a genuine strength the journal can showcase, or a signal the contribution is too thin?
**Will particularly care about**: Whether "perceived usefulness" and "self-reported use" are operationally distinct enough that the r=.42 is not partly a common-method / same-instrument artifact, and whether the title's promise is delivered.
**Possible blind spots**: May under-weight the single-item DV measurement problem (defers to R1) and the depth of the TAM literature the paper skips (defers to R2).

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1 — Methodology
**Identity Description**: Quantitative educational-measurement methodologist specializing in survey design and correlational inference in education, with particular expertise in self-report measurement validity, single-item vs. multi-item scales, and power/precision reporting. Reviews to APA 7.0 statistical-reporting standards.
**Review Focus**:
  1. Statistical reporting adequacy — effect size, CI, power, assumption handling, APA number formatting (`references/statistical_reporting_standards.md` Step 4a).
  2. Measurement validity of the two constructs, especially the **single-item, ordinal, self-report** dependent variable and its Pearson-vs-Spearman treatment.
  3. Whether the conclusions stay inside what a cross-sectional correlation can support (reverse-causation / common-method).
**Will particularly care about**: The Pearson correlation computed on a 5-point single-item ordinal DV; whether the reported CI/power are internally consistent with n=214; missing-data and non-response accounting (233→214).
**Possible blind spots**: May treat the reference base as given (defers to R2 on literature); does not assess cross-disciplinary framing (defers to R3).

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2 — Domain
**Identity Description**: Senior educational-technology / technology-acceptance scholar familiar with the Davis (1989) TAM lineage, its higher-education extensions (UTAUT, LMS-adoption studies), and the self-report-vs-log-data measurement debate in learning analytics. Attentive to whether TAM constructs are correctly represented and to secondhand-citation risk.
**Review Focus**:
  1. Literature coverage — is the technology-acceptance canon (Davis TAM; UTAUT; the LMS-engagement literature) represented, or is the paper resting on 6 placeholder-looking references?
  2. Construct fidelity — is "perceived usefulness" used in its TAM-defined sense, and is the borrowed 6-item scale correctly attributed?
  3. Genuineness and size of the incremental contribution to the LMS-acceptance sub-field.
**Will particularly care about**: Whether the paper's positioning ("an incremental data point, comparable with prior work") is honest or masks that the canonical primary sources (Davis) are absent, and whether any field-norm-based severity claim is externally grounded (#215).
**Possible blind spots**: May not scrutinize the statistical machinery (defers to R1); may under-value practical/stakeholder implications (defers to R3).

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3 — Cross-disciplinary / Practical
**Identity Description**: Learning-analytics / behavioral-data scholar coming from the *behavioral-log* side of the field (an adjacent discipline to survey-based ed-tech), with a practitioner interest in LMS onboarding design. Brings the outsider view that self-reported use and logged use are different constructs, and that "onboarding for perceived usefulness" is a design claim with feasibility and equity dimensions.
**Review Focus**:
  1. Assumption audit — the implicit premise that self-reported frequency is a usable proxy for engagement, and that perceived usefulness is a lever institutions can pull.
  2. Practical feasibility and stakeholder reach of the onboarding implication (who is missing: low-engagement non-respondents, students with low digital access).
  3. Cross-disciplinary borrowing — what the learning-analytics log-data tradition and self-determination / behavioral-design literatures could add.
**Will particularly care about**: Whether the single practical recommendation (usefulness-oriented onboarding) is over-read from a moderate correlation, and whether non-respondents (voluntary sample) are exactly the population the recommendation targets.
**Possible blind spots**: Outsider to survey-psychometric conventions — will explicitly flag "outsider" status on measurement points and leave the statistical verdict to R1.

### Reviewer Configuration Card #5

**Role**: Devil's Advocate
**Identity Description**: Adversarial stress-tester scoped to this paper (reviewer-Phase-1 DA, NOT the deep-research multi-phase DA). Constructs the strongest case *against* the paper's conclusions; hunts internal contradictions, evidence gaps, confirmation bias, and the strongest rival explanation for r=.42.
**Review Focus**:
  1. Core-thesis challenge + strongest counter-argument (common-method variance / reverse causation as more parsimonious than the implied "usefulness drives use").
  2. Data–conclusion and internal-consistency checks (does the moderate, heavily-caveated result actually support even the modest onboarding implication?).
  3. "So what?" test — is a single-site r=.42 that the authors themselves call unsurprising a sufficient increment?
**Will particularly care about**: Whether the paper's very honesty is doing double duty — pre-empting every attack so that no CRITICAL flaw survives — and whether that leaves a genuine *foundation-collapse* / *logic-break* CRITICAL, or only MAJOR/MINOR gaps.
**Possible blind spots**: Adversarial intensity can inflate a generic open-science demand (e.g., "no open data / no preregistration") into a CRITICAL; #215/#216 field-norm and surface-form parity gates run at severity-assignment time to prevent this.

## Review Strategy Recommendations
- **Special characteristic — an "honest small paper."** The manuscript's defining feature is that it claims almost exactly what its design supports: correlational language throughout, causation explicitly disclaimed, single-item DV flagged, single-site generalization bounded, common self-report caveat stated. The panel's real job is not to catch over-claiming (there is little) but to judge whether (a) the *measurement* (single-item ordinal self-report DV; Pearson on ordinal) is defensible, and (b) the *contribution* clears the bar. Reviewers must resist both the sycophancy trap (rewarding honesty with an inflated score, Anti-Pattern #5) and the mirror trap (manufacturing a CRITICAL to look rigorous).
- **Reference base is a red flag to probe, not assume.** All six DOIs share a `10.5555/2050xxx` placeholder-style prefix and the canonical TAM primary source (Davis, 1989) is absent. R2 must assess whether the literature is genuinely thin/mis-anchored; the citation-existence question is real but is a domain/integrity finding, not something the panel resolves by inventing replacement references (#574 A5 no-invention rule binds R2 and R3).
- **Predictable inter-reviewer tension:** R1 (measurement) and R3 (log-data outsider) will both land on the self-report DV from different angles — R1 as a psychometric single-item-reliability problem, R3 as a construct-mismatch (perceived vs. behavioral use). The synthesizer must treat these as corroborating sub-claims from different perspectives, not a duplicate (Anti-Pattern #2), and must decompose the "self-report DV" bundle (§F.3.2). R2 vs. EIC may split on whether the thin literature is disqualifying (R2) or acceptable for a modest Q3 note (EIC).

---

# PART 2 — Five-Seat Panel Reports (Phase 1)

Each seat below shows its Phase 1 paper-content-blind pre-commitment (contract paraphrase + scoring plan + `[CONTRACT-ACKNOWLEDGED]`), then its Phase 2 paper-visible review. Phase 1 for each seat was produced from the contract JSON + metadata only (`title`, `field=educational technology`, `word_count≈1750`); the manuscript was injected only at Phase 2 inside a `<paper_content>` data delimiter and treated as untrusted data (no injection attempts were present in this manuscript).

---

## SEAT 1 of 5 — Editor-in-Chief

### Phase 1 — Paper-content-blind pre-commitment

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** From the editor's chair I read this as: does the study's design and its statistical reporting clear the field's peer-review floor for a quantitative survey? I am not the statistics referee (that is R1), but I must be able to see that the design can bear the weight of the paper's claims and that nothing in the reporting is missing at a level that would embarrass the journal.

**D2 — domain_accuracy (mandatory).** Are the paper's substantive claims about technology acceptance and LMS use correct and current, is prior work represented fairly, and are the field's core terms used in their accepted sense? An editor's failure mode here is publishing a paper that a domain expert would find naive about its own literature.

**D3 — argumentative_coherence (mandatory).** Does the paper hold together — problem to question to evidence to conclusion — without the "over-promise, under-deliver" gap I watch for at the title/abstract/conclusion level? The core question, evidence, and stated conclusion must be one continuous line.

**D4 — cross_disciplinary_relevance (high).** Would a reader from an adjacent field (learning analytics, information systems) find the framing and implications accessible and the interdisciplinary claims (if any) substantiated? For my readership this is about reach, not just correctness.

**D5 — writing_and_structure (normal).** Is the manuscript organized, clear, and to venue convention, with adequate exposition and any figures/tables serving the argument?

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for`: a clearly stated design, a sample-size / precision statement, reported effect with uncertainty, and conclusions that do not exceed a cross-sectional correlation.
- `what_triggers_block`: the design cannot answer the stated question at all, or the headline claim is causal off cross-sectional data with no disclaimer.
- `what_triggers_warn`: a real but non-fatal design/reporting gap (e.g., a measurement choice a referee will contest) that revision can fix.

### D2: domain_accuracy
- `what_to_look_for`: correct use of "perceived usefulness"/acceptance terms; fair, non-cherry-picked representation of prior findings; positioning that matches what the paper delivers.
- `what_triggers_block`: a substantive factual error about the field, or a contribution claim (e.g., "first study") flatly contradicted by well-known work.
- `what_triggers_warn`: thin or mis-anchored literature, or a positioning claim that oversells a modest result.

### D3: argumentative_coherence
- `what_to_look_for`: title = abstract = conclusion in scope; the RQ is answered directly; caveats are consistent, not contradicted later.
- `what_triggers_block`: the conclusion asserts something the paper's own evidence contradicts, or the paper answers a different question than it poses.
- `what_triggers_warn`: minor scope drift or an implication stated slightly beyond the evidence.

### D4: cross_disciplinary_relevance
- `what_to_look_for`: framing legible to adjacent-field readers; any interdisciplinary claim backed.
- `what_triggers_block`: an interdisciplinary claim central to the paper that is simply unsupported.
- `what_triggers_warn`: adjacent-field relevance is asserted but under-developed, or a natural adjacent literature (log-data) is ignored.

### D5: writing_and_structure
- `what_to_look_for`: conventional structure, clear prose, results legible.
- `what_triggers_block`: unreadable / not peer-review-ready.
- `what_triggers_warn`: no supporting table/figure for the key result, or scattered convention lapses.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 — Paper-visible review

contract_role: eic

## EIC Review Report

### Reviewer Identity
Editor-in-Chief, Q3-tier educational-technology journal (calibrated to *Education Sciences* / *Australasian Journal of Educational Technology*); scope = applied learning-technology research in higher education; values transparent reporting and appropriately scoped claims over novelty.

### Overall Recommendation
Minor Revision

### Confidence Score
4 — journal-fit, scope-discipline, and contribution judgments are well within my editorial competence; the fine psychometric verdict I defer to R1.

### Summary Assessment
The manuscript reports a single-site cross-sectional survey (n=214) finding a positive, moderate correlation (r=.42, 95% CI [.30,.52]) between undergraduates' perceived usefulness of their LMS and their self-reported frequency of use. Its most striking property is discipline: causal language is explicitly disclaimed, the reverse pathway is named, the single-item self-report measure is flagged as capturing *perceived* rather than behavioral use, and generalization is bounded to one institution — the scope is held identically from title through conclusion. As an editor I value this; the "availability ≠ use" framing is exactly my readership's concern. The cost is that the contribution is genuinely small: one more TAM-consistent correlation the authors themselves call unsurprising, resting on a thin six-item reference base that omits the canonical primary sources. The measurement of the dependent variable (a single ordinal item) is the one substantive weakness that a competent referee will not let pass. None of this is fatal: the paper does not over-promise, the honesty is real, and the fixes are supplementation, not redesign. This is a publishable modest note after minor revision, not a major-flaw manuscript.

### Strengths
1. **Scope held consistently, no over-promising**: The title's "self-reported use," the abstract's "should not be read as causal," §5's naming of the reverse pathway, and §7's "incremental, design-bounded contribution rather than a causal claim" are one continuous, honest scope. This is the paper's defining editorial strength.
2. **Reporting hygiene above its tier**: r reported with a 95% CI [.30,.52], exact-style p, a Spearman robustness check (ρ=.40), Cronbach's α=.88 for the perceived-usefulness scale, and an explicit sensitivity/power statement (§3.4) — reporting most Q3 submissions omit.
3. **Limitations are substantive, not boilerplate** (§6): single site, self-report vs. logs, cross-sectional non-causality, and voluntary-response over-representation are each named as real constraints on the reading of the result.

### Weaknesses
1. **Contribution is thin and under-positioned** (W-EIC-1): §2's own framing — "an incremental data point, comparable with prior work" — combined with a result the authors call consistent-and-unsurprising, leaves the "why publish this now" question under-answered. *Why it matters*: at any tier an editor must see the increment. *Suggestion*: sharpen §1/§2 to state precisely what this single, transparently-reported association adds that the cited prior work leaves open (e.g., a clean single-instrument estimate with full uncertainty reporting in one under-studied institutional context).
2. **Single-item dependent variable** (W-EIC-2): self-reported use is one 5-point frequency item (§3.2). *Why it matters*: it is the paper's outcome variable and a referee's first target. *Suggestion*: defer the psychometric verdict to R1, but at minimum the paper must argue the single-item choice explicitly rather than only noting it. (Confidence on the fine measurement point: I flag it; R1 adjudicates.)
3. **Reference base looks placeholder-thin** (W-EIC-3): six references, all with `10.5555/2050xxx`-pattern DOIs, no Davis/TAM primary source. *Why it matters*: it undercuts the "comparable with prior work" positioning and reads as under-anchored. *Suggestion*: anchor to the canonical technology-acceptance sources (defer specifics to R2).

### Detailed Comments

#### Journal Fit
Squarely in scope for an applied HE ed-tech journal: LMS engagement, technology acceptance, onboarding implications. The narrow single-site design fits a Q3/OA "sound modest study" slot, not a Q1 novelty slot. Fit is good; ambition is modest — an honest match, not a mismatch.

#### Originality
Low-to-moderate. The perceived-usefulness↔use association is well-trodden TAM territory; the paper's own §2/§7 concede this. Originality is in transparency and bounding, not in the finding.

#### Significance
Modest and appropriately claimed. The onboarding implication (§5) is offered as "suggested by, not proven by" the correlation — correctly hedged; its practical reach is real but small.

#### Structural Coherence
Strong. Title → abstract → intro RQ ("is perceived usefulness associated with self-reported frequency of use?") → results → discussion → conclusion form one line with no scope drift. The conclusion answers exactly the question posed.

#### Title & Abstract
Accurate and honest. The title names "self-reported use" (not "use"), pre-empting the very over-claim the paper avoids. Abstract is complete and correctly scoped.

#### Conclusion
Does not over-infer. §7 restates the bounded finding and points to log-data / longitudinal / multi-site future work — the right next steps.

### Questions for Authors
1. What does this single association add beyond the cited prior work — state the increment in one sentence for §1?
2. Why a single-item use measure rather than a short multi-item frequency scale, given the study otherwise follows careful reporting conventions?
3. Can you anchor the technology-acceptance framing to its primary sources (the reference list currently omits them)?

### Minor Issues
- No table or scatterplot is shown for the headline result (§4 describes but does not display it).
- "Greater than .80 power to detect r ≥ .19" (§3.4) is a precise claim worth a one-line note on how it was computed.

---

## SEAT 2 of 5 — Peer Reviewer 1 (Methodology)

### Phase 1 — Paper-content-blind pre-commitment

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** This is my seat. Does the design match the research question; is the sampling and non-response accounted for; is the analysis method correct for the data type; are effect size, confidence interval, power, and assumptions reported to APA 7.0 standard (`statistical_reporting_standards.md`); and do the conclusions stay inside what a cross-sectional correlation supports?

**D2 — domain_accuracy (mandatory).** Outside my primary lane, but I will check that any statistical/measurement claim about the constructs is substantively correct (e.g., that a "validated instrument" claim is not contradicted by how the instrument is actually used here). Deeper literature accuracy is R2's.

**D3 — argumentative_coherence (mandatory).** From the methods angle: do the stated conclusions follow from the actual numbers, with no inferential leap (correlation stated as/implied to be causation, single-site read as general)?

**D4 — cross_disciplinary_relevance (high).** Whether the measurement choices are legible to adjacent quantitative fields; light touch from my seat.

**D5 — writing_and_structure (normal).** Whether the statistical exposition (numbers, tables) is clear and complete enough to evaluate; APA number-format compliance sits partly here and partly in D1.

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for`: design↔RQ match; n and non-response accounting; correct correlation choice for an ordinal single-item DV; effect size + 95% CI + p + power + assumption handling; conclusions bounded to correlation.
- `what_triggers_block`: a fatal design/analysis error that invalidates the headline number — e.g., a causal conclusion drawn from cross-sectional data with no disclaimer, an effect reported with no uncertainty at all, or an analysis method that cannot be applied to the data as described.
- `what_triggers_warn`: a real, revision-fixable reporting/measurement gap — single-item DV without justification, Pearson on an ordinal item without a robustness check, missing assumption/missing-data detail, minor APA-format slips — that weakens but does not invalidate the result.

### D2: domain_accuracy
- `what_to_look_for`: statistical/measurement claims about the constructs are internally correct (α reported for the multi-item scale; "validated instrument" claim consistent with use).
- `what_triggers_block`: a measurement claim that is demonstrably false (e.g., reporting reliability for a single-item measure as if multi-item).
- `what_triggers_warn`: a measurement claim that is imprecise or under-justified.

### D3: argumentative_coherence
- `what_to_look_for`: the reported r and its CI actually support the stated (bounded, correlational) conclusion.
- `what_triggers_block`: the conclusion contradicts the numbers (e.g., claims strong when r is moderate; claims causal).
- `what_triggers_warn`: minor tension between a hedge and an implication.

### D4: cross_disciplinary_relevance
- `what_to_look_for`: measurement choices explained enough for an adjacent quantitative reader.
- `what_triggers_block`: (unlikely from this seat) a central interdisciplinary quantitative claim that is unsupported.
- `what_triggers_warn`: measurement rationale opaque to outside readers.

### D5: writing_and_structure
- `what_to_look_for`: complete, legible statistical reporting; a table/figure for the key result.
- `what_triggers_block`: statistics unreadable / uninterpretable.
- `what_triggers_warn`: no results table/figure; scattered APA-format issues.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 — Paper-visible review

contract_role: methodology

## Methodology Review Report (Peer Reviewer 1)

### Reviewer Identity
Quantitative educational-measurement methodologist; survey design and correlational inference; self-report measurement validity and single- vs. multi-item scales; reviews to APA 7.0 statistical-reporting standards.

### Overall Recommendation
Minor Revision

### Confidence Score
5 — this is squarely my domain.

### Summary Assessment
The design (cross-sectional survey) matches the correlational research question, and the statistical reporting is, for the most part, exemplary relative to the field floor: the association is reported as r=.42 with a 95% CI [.30,.52], p<.001, n=214; a Spearman robustness check (ρ=.40) is supplied precisely because the use item is ordinal; α=.88 anchors the six-item perceived-usefulness scale; and §3.4 gives a sensitivity/power statement (>.80 power for r≥.19). Distributional checks (approximate symmetry, linearity, no bivariate outliers) are described. The conclusions are correctly bounded to correlation, with reverse causation explicitly named — no causal overreach. The one genuine methodological weakness is the dependent variable: self-reported LMS use is a **single** 5-point frequency item, which caps the reliability and precision of the paper's outcome and is only *noted*, not *justified*. Two smaller reporting gaps (non-response/missing-data mechanism for the 233→214 attrition; how the power figure was computed) are revision-level. None of these is fatal, and none is a design flaw that re-collection could not, but need not, fix. This is a Minor Revision on methodology.

### Strengths
1. **Effect size + CI + robustness check all present** (§4): r=.42 [.30,.52] with a Spearman ρ=.40 cross-check is exactly the right reporting for a bivariate association on a partly-ordinal measure — it directly addresses the Pearson-on-ordinal concern before a referee raises it.
2. **Precision/power reasoning is stated, not hidden** (§3.4): "greater than .80 power to detect r ≥ .19 at α=.05" is a sensitivity statement most survey papers omit; it correctly frames the study as sensitive to small-to-moderate effects.
3. **Conclusions stay inside the design** (§5, §6): "the correlation cannot establish that perceived usefulness causes use; the reverse pathway … is equally consistent" — a textbook-correct handling of cross-sectional inference, and the reason no Reverse-Causation fallacy fires here.
4. **Reliability reported for the multi-item scale** (§3.2): α=.88 is correctly reported for the six-item PU scale (and, correctly, *not* claimed for the single-item DV).

### Weaknesses
1. **Single-item, single-measure dependent variable** (Severity: Major): self-reported use is one ordinal item (§3.2). *Why it matters*: a single item has unknown/uncontrolled measurement error and no internal-consistency estimate, which attenuates and destabilizes the very correlation that is the paper's entire result; it also makes the DV a *perception of frequency*, compounding the self-report caveat. *Suggestion*: justify the single-item choice explicitly (e.g., cite the single-item-measure validity literature as a search lead — do not fabricate a citation), and, if possible, report any available corroboration; failing new data, foreground this as a first-order limitation and soften any precision language accordingly. This is fixable by argument/re-framing, not necessarily re-collection.
2. **Non-response and missing-data accounting is thin** (Severity: Minor→Major boundary; scored within Warn): 233 received → 14 incomplete + 5 duplicate removed → 214 (§3.1), but there is no response-rate denominator (how many students were invited?) and no discussion of the missing-data mechanism. *Why it matters*: with "all enrolled undergraduates eligible" via an announcement channel, the response rate and non-response bias are material to the §6 voluntary-over-representation caveat. *Suggestion*: report invited-N / response rate, and state the missing-data handling (the 14 incompletes) as MCAR/MAR with justification.
3. **Power claim under-specified** (Severity: Minor): the >.80-power-for-r≥.19 figure (§3.4) is stated without the computation basis (tool, one- vs. two-tailed already given). *Suggestion*: one line naming the method/tool.
4. **No results table or scatterplot** (Severity: Minor): §4 describes the bivariate relationship and the "approximately linear, monotonic" scatter but shows neither. *Suggestion*: add a descriptive table (M, SD, N, and the correlation matrix) and, ideally, the scatterplot the text already references.

### Detailed Comments

#### Research Questions & Hypotheses
The RQ ("is perceived usefulness associated with self-reported frequency of use?") is descriptive/correlational and answerable by the chosen design. No formal hypotheses, appropriately, for a descriptive correlation.

#### Research Design
Cross-sectional single-wave survey. Correctly matched to a correlational (not causal) question. The internal/external-validity trade-off is handled honestly — external validity is explicitly bounded to one site.

#### Sampling Strategy
Census-eligible frame (all enrolled undergraduates) via announcement channel; voluntary. Sample spans all four year levels. The missing response-rate denominator is the gap (see W2). Selection/self-selection is acknowledged in §6.

#### Data Collection
Anonymous online survey, three-week window, informed consent on landing page. Procedure adequately described.

#### Analysis Methods
Pearson r with a Spearman robustness check — the correct paired approach for a partly-ordinal DV; the near-identical ρ (.40) vs. r (.42) is reassuring. Distributional/assumption checks are described narratively (symmetry, linearity, outliers). Effect size *is* the estimand here (a correlation), and its CI is reported — Step 4a effect-size and CI items are satisfied. **Statistical-reporting completeness: Adequate (70–89 band)** — the only material omissions are missing-data detail and the power-computation basis.

#### Results Presentation
Complete in prose (r, CI, p, n, ρ, M, SD, median category) but not tabulated/plotted (see W4). Non-significant results are not an issue (single primary estimate). No selective-reporting signal.

#### Reproducibility
Instrument is "adapted from Costa & Wren (2019)"; the six items themselves are not reproduced, and no data/code availability statement is given. Ethics review is documented (§3.3). For a survey of this kind the reproducibility gap (item wording, data availability) is Minor-to-Major and revision-addressable, not a field-norm-breaching demand.

#### Methodological Fallacies Detected
- **Reverse causation**: *present as a risk but correctly disclaimed* — the paper does not commit the fallacy; it names it (§5). No finding.
- **Common-method / single-instrument variance**: both constructs are self-reported on the same 5-point survey instrument at the same time — a legitimate inflation concern for r=.42. The paper flags self-report divergence from logs (§2, §6) but does not name common-method variance specifically. Warn-level, feeds D1.
- **Causal language scan**: none detected in non-experimental sections — the paper uses "associated with," "tracks with," "consistent with" throughout. Clean.

### Questions for Authors
1. Why a single-item use measure? Can you justify it against the single-item-measurement-validity literature, or provide any reliability/corroboration?
2. How many students were invited (response-rate denominator), and what is the assumed missing-data mechanism for the 14 incomplete cases?
3. How was the ">.80 power for r≥.19" figure computed (tool/method)?
4. Can you add a descriptive statistics table and the scatterplot the text references?

### Minor Issues
- §4 "The proportion of variance shared by the two measures was accordingly modest" — consider reporting r² = .18 explicitly rather than only in prose.
- APA number formatting is otherwise clean (r=.42 no leading zero; M=3.6, SD=0.8 with leading zeros correct).

---

## SEAT 3 of 5 — Peer Reviewer 2 (Domain)

### Phase 1 — Paper-content-blind pre-commitment

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** From the domain seat, I confirm the design and analysis are *field-appropriate* for a technology-acceptance survey (correlational read of a cross-sectional design), leaving the fine statistics to R1. My concern is whether the method is the field-standard way to make this kind of claim.

**D2 — domain_accuracy (mandatory).** This is my seat. Is the technology-acceptance literature (Davis TAM lineage, UTAUT, LMS-engagement studies, self-report-vs-log debate) adequately covered; are "perceived usefulness" and the borrowed instrument correctly attributed and used in their field-defined senses; is the incremental contribution to the LMS-acceptance sub-field genuine and honestly sized? Any severity I assign that rests on a *field norm* (e.g., "this literature must be cited") I must ground in an external checkable source, not model memory (#215).

**D3 — argumentative_coherence (mandatory).** Does the domain argument — gap, positioning, contribution — hang together and match the field's actual state of knowledge, with no overclaiming relative to prior work?

**D4 — cross_disciplinary_relevance (high).** Whether adjacent-field framing (information systems, learning analytics) is correct where invoked; primary cross-disciplinary depth is R3's.

**D5 — writing_and_structure (normal).** Whether literature is integrated (synthesized vs. listed) and terminology is used consistently.

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for`: the correlational survey is the field-conventional vehicle for this claim.
- `what_triggers_block`: a method the field would regard as invalid for the claim.
- `what_triggers_warn`: a method that is acceptable but not best-practice for the sub-field.

### D2: domain_accuracy
- `what_to_look_for`: correct TAM-sense use of "perceived usefulness"; correct attribution of the adapted instrument; coverage of the acceptance canon and the self-report/log debate; contribution honestly sized; any field-norm severity externally grounded.
- `what_triggers_block`: a substantive domain error — a false factual claim about the field, a mis-definition of a core construct, or an absolute-priority claim ("first study") contradicted by well-known work.
- `what_triggers_warn`: thin/mis-anchored literature (missing canonical primary sources), secondhand citation, or a positioning claim that oversells a modest result — real but revision-fixable.

### D3: argumentative_coherence
- `what_to_look_for`: gap→contribution logic consistent with the field's state.
- `what_triggers_block`: a contribution claim that contradicts the cited (or well-known) literature.
- `what_triggers_warn`: a gap argument that is under-supported.

### D4: cross_disciplinary_relevance
- `what_to_look_for`: adjacent-field terms used correctly where they appear.
- `what_triggers_block`: a central adjacent-field claim that is wrong.
- `what_triggers_warn`: adjacent literature (log-data/learning analytics) plausibly relevant but unaddressed.

### D5: writing_and_structure
- `what_to_look_for`: literature synthesized with a structure, not enumerated.
- `what_triggers_block`: no discernible literature argument.
- `what_triggers_warn`: list-like or under-integrated review.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 — Paper-visible review

contract_role: domain

## Domain Review Report (Peer Reviewer 2)

### Reviewer Identity
Senior educational-technology / technology-acceptance scholar; Davis (1989) TAM lineage and its HE extensions (UTAUT, LMS-adoption); the self-report-vs-log-data measurement debate in learning analytics.

### Overall Recommendation
Major Revision

### Confidence Score
4 — technology-acceptance literature and construct fidelity are well within my competence; I hold the fine statistical verdict to R1.

### Summary Assessment
Substantively, the paper uses "perceived usefulness" in a sense consistent with its technology-acceptance meaning, correctly represents the *direction* of prior findings (positive PU↔use associations with sample-dependent effect sizes), and — commendably — does not overclaim: §2 positions the work as "an incremental data point, comparable with prior work," and it invokes the self-report-vs-log-data caution (attributed to Vasquez, 2020) that many acceptance papers ignore. Terminology is used carefully and the argument is internally coherent. My reservation is coverage and anchoring. The reference base is six sources, none of which is the canonical primary literature the paper's own framing rests on: Davis's foundational TAM work and the UTAUT lineage are absent, so the phrase "technology-acceptance research" (§1, §2, §5) is asserted without its primary anchor. Compounding this, the six DOIs all follow a `10.5555/2050xxx` pattern that is not a real registrant range, which — independent of the statistics — is a domain/integrity concern about whether the cited evidence base exists as represented. This is not a substantive *error* about the field (nothing claimed is false), but it is a coverage-and-anchoring gap large enough that, for a paper whose contribution is explicitly "comparability with prior work," the prior work must be correctly and verifiably anchored. Hence Major Revision — the fix is real literature work, not cosmetic.

### Strengths
1. **Correct, disciplined use of the core construct** (§1, §2): "perceived usefulness — the degree to which a person believes a technology will help them perform better" is the TAM-faithful definition, and the paper does not conflate acceptance with use or perception with behavior.
2. **The self-report/log-data debate is represented** (§2, via Vasquez 2020; §6): explicitly treating the self-report measure as capturing *perceived* rather than actual engagement is a domain sophistication many LMS-acceptance papers lack; it correctly imports a known measurement caution from learning analytics.
3. **Honest contribution sizing, no priority overclaim** (§2, §7): the paper claims an "incremental data point … rather than a test of a theoretical model" and makes no "first study" / absolute-priority claim — so no bounded-novelty violation fires, and there is nothing here I must down-rate for overreach.
4. **Contextual-specificity awareness** (§6, via Song 2018): citing that association strengths vary by institution, and reading its own single-site estimate as "one point in a distribution," is exactly the context-sensitivity the sub-field expects of regional work.

### Weaknesses
1. **Canonical primary sources of the framing are absent** (Severity: Major). The paper is built on "technology-acceptance research" but cites no foundational TAM/UTAUT primary source; the six references are all secondary/adjacent. *Why it matters*: a contribution defined as "comparable with prior work" must anchor to the prior work it claims comparability with; without the primary lineage the positioning is unverifiable and reads as under-read. *Field-norm grounding (#215)*: the norm "a technology-acceptance paper should cite the acceptance literature's primary sources" is grounded in the discipline's own citation practice (TAM/UTAUT are the field's defining references), not merely my prior — this is a documented convention of the sub-field, so the severity assertion is grounded, not `[FIELD-NORM UNVERIFIED]`. *Suggestion*: anchor the framing to the foundational technology-acceptance literature (search leads: Davis's original TAM work; the UTAUT synthesis; a recent LMS-acceptance review) — **I am naming these as search leads, not asserting exact citations (#574 A5); the author must locate and verify real sources.**
2. **Reference-base existence/anchoring concern** (Severity: Major, integrity class). All six DOIs share a `10.5555/2050xxx` placeholder-pattern prefix and none resolves to a recognizable venue in the field. *Why it matters*: the paper's evidence base for every literature claim rests on these six; if they are not verifiable real sources, the domain argument is unsupported regardless of its internal correctness. *Suggestion*: verify and, where needed, replace with real, resolvable sources. **I do not and cannot supply substitute citations here (#574 A5 no-invention); this is flagged for author correction and for the pipeline's citation-existence gate, not resolved by the panel.**
3. **Literature review is thin on the sub-field's recent work** (Severity: Minor→Major boundary, scored Warn). §2 cites five sources and synthesizes them adequately for their number, but the last-3-5-years LMS-engagement literature and any opposing findings are not represented. *Suggestion*: add recent LMS-engagement studies and at least one contrasting result to satisfy the field's coverage expectation.

### Detailed Comments

#### Literature Review
- **Coverage**: Missing the canonical TAM/UTAUT primary lineage and recent (last 3–5 yr) LMS-engagement work (W1, W3). Present sources are adjacent/secondary.
- **Integration quality**: For the six sources present, integration is genuinely critical, not enumerative — §2 uses Delgado, Ibarra & Poll, Vasquez, and Song to build a real "read this correlation cautiously" argument. Good synthesis of a too-small set.
- **Research gap argument**: The gap ("document one transparent association in one bounded sample") is honest but modest; it is coherent, not overstated.

#### Theoretical Framework
- **Appropriateness**: TAM's perceived-usefulness construct is the right frame; the paper wisely does not claim to test full TAM.
- **Application depth**: Deliberately shallow-by-design (single construct, single association) — acceptable given the stated non-model-testing aim, but it means the "framework" is really one borrowed construct.
- **Alternative frameworks**: UTAUT / self-determination framings are not discussed; not required, but a sentence on why PU-only would strengthen positioning.

#### Academic Argument Quality
- **Factual accuracy**: No false claim about the field detected. Directions of prior findings are represented correctly.
- **Argument logic**: Coherent; the gap→contribution→caveat chain is sound.
- **Terminology precision**: Precise; "perceived usefulness," "self-reported use," "association" used consistently and correctly.

#### Contribution to the Field
- **Incremental contribution**: A single, transparently-reported single-site correlation. Genuine but small; the paper says so.
- **Positioning**: Honest ("incremental data point") but under-anchored to the primary literature it positions against (W1).
- **Overclaiming**: None detected — a notable strength.

#### Missing Key References
- The foundational technology-acceptance / TAM primary literature (search lead: Davis's original perceived-usefulness/TAM work). `[UNVERIFIED]` search lead — author to locate and verify.
- The UTAUT synthesis literature (search lead: the Venkatesh-lineage unified acceptance model). `[UNVERIFIED]` search lead.
- A recent LMS-engagement / learning-analytics review connecting self-reported and logged use (search lead: recent learning-analytics reviews on self-report vs. behavioral traces). `[UNVERIFIED]` search lead.
- *No-invention rule (#574 A5): the three items above are search leads phrased as topic pointers, not confident citations; I attest none of them as specific author/year/venue metadata, and I have invented no DOIs.*

### Questions for Authors
1. Can you verify the six cited references and their DOIs, and anchor the technology-acceptance framing to its primary sources?
2. What recent (last 3–5 yr) LMS-engagement findings does your result sit alongside, and are there contrasting results?
3. Why PU-only rather than a fuller acceptance construct set — is the single-construct scope a deliberate boundary or a coverage limit?

### Minor Issues
- §2 attributes the self-report/log divergence to a single source (Vasquez 2020); the learning-analytics literature on this is broader and would strengthen the point.
- Consider naming the theoretical lineage ("Technology Acceptance Model") explicitly rather than only "technology-acceptance research."

---

## SEAT 4 of 5 — Peer Reviewer 3 (Perspective / Cross-disciplinary)

### Phase 1 — Paper-content-blind pre-commitment

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** From the outsider (learning-analytics / behavioral-data) seat, I do not adjudicate the statistics (R1's), but I ask whether the *measurement stance* — treating a self-reported frequency item as a usable index of engagement — is a defensible design choice when an adjacent field routinely uses behavioral logs.

**D2 — domain_accuracy (mandatory).** Not my lane; I confirm no cross-disciplinary claim is mis-stated and defer domain coverage to R2.

**D3 — argumentative_coherence (mandatory).** Whether the practical/implication argument follows from the evidence without leaping — specifically whether an onboarding recommendation is over-read from a moderate correlation.

**D4 — cross_disciplinary_relevance (high).** This is my seat. Are the framing, definitions, and implications legible and useful to adjacent-field readers (learning analytics, behavioral design, IS)? Are cross-disciplinary borrowing opportunities (log-data, self-determination, behavioral onboarding) taken or missed? Are stakeholder and equity dimensions of the recommendation considered?

**D5 — writing_and_structure (normal).** Whether the framing is accessible to a non-specialist reader.

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for`: an explicit rationale for a self-report measurement stance where behavioral data exist.
- `what_triggers_block`: (rare from this seat) the measurement stance makes the central claim uninterpretable.
- `what_triggers_warn`: the self-report/behavioral gap is unacknowledged from the practical-use angle.

### D2: domain_accuracy
- `what_to_look_for`: cross-disciplinary references used correctly.
- `what_triggers_block`: a central adjacent-field claim that is wrong.
- `what_triggers_warn`: an adjacent claim stated loosely.

### D3: argumentative_coherence
- `what_to_look_for`: implications hedged to match a moderate correlation.
- `what_triggers_block`: a practical/policy claim asserted as established from correlational evidence.
- `what_triggers_warn`: an implication that leans slightly past the evidence.

### D4: cross_disciplinary_relevance
- `what_to_look_for`: accessible framing; adjacent-field borrowing taken; stakeholder/equity/feasibility of the recommendation considered.
- `what_triggers_block`: a central interdisciplinary claim that is unsupported.
- `what_triggers_warn`: adjacent literature (log-data, behavioral design) or key stakeholders (non-respondents, low-access students) plausibly relevant but unaddressed.

### D5: writing_and_structure
- `what_to_look_for`: legible to an adjacent-field reader.
- `what_triggers_block`: opaque to non-specialists.
- `what_triggers_warn`: some jargon unexplained.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 — Paper-visible review

contract_role: perspective

## Perspective Review Report (Peer Reviewer 3)

### Reviewer Identity
Learning-analytics / behavioral-data scholar (adjacent to survey-based ed-tech), with a practitioner interest in LMS onboarding design; brings the log-data / behavioral-design outsider view. As an outsider to survey psychometrics, I flag measurement points but leave the statistical verdict to R1.

### Overall Recommendation
Minor Revision

### Confidence Score
3 — cross-disciplinary framing and practical-implication reach are my strengths; I am outside the survey-psychometric conventions and say so where it matters.

### Summary Assessment
Read from the behavioral-data side of the field, this is a careful and unusually self-aware paper. Its central cross-disciplinary virtue is that it does *not* pretend self-reported frequency is behavioral engagement: §2 and §6 explicitly import the learning-analytics caution that self-reports diverge from logs, and the title itself says "self-reported use." That candor is exactly what an outsider would demand, and it is already here. My contribution is therefore not to catch a hidden overclaim but to push on three under-developed adjacencies. First, the paper *names* the self-report/log gap but does not *use* the adjacent log-data literature to frame what its correlation can and cannot stand in for. Second, the one practical implication — onboarding that surfaces concrete usefulness (§5) — is correctly hedged ("suggested by, not proven by") but its stakeholder and equity dimensions are unexamined: the voluntary sample (§6) most likely under-represents precisely the low-engagement students the onboarding recommendation targets, so the recommendation is aimed at a population the study under-observed. Third, adjacent behavioral-design and self-determination framings would enrich the "why does perceived usefulness track use" story. None of this is fatal; all of it is additive. Minor Revision.

### Strengths
1. **Refuses the self-report=behavior conflation** (§2, §6, and the title): the paper treats its measure as *perceived* use — the single most important cross-disciplinary honesty an LMS-engagement paper can show, and it is present without prompting.
2. **The practical implication is hedged, not asserted** (§5): "this implication is suggested by, not proven by, the present correlation" is precisely the discipline an outsider fears is missing from practice-facing ed-tech work.
3. **Context-boundedness is explicit** (§6, §7): the single-site limit and the call for log-data / multi-institution future work show the authors already see the adjacent-field next steps.

### Weaknesses
1. **Names the log-data gap but does not leverage the log-data literature** (Severity: Minor). §2/§6 cite that self-reports diverge from logs but stop there. *Why it matters*: the paper's outcome variable's meaning depends on how far self-reported frequency proxies logged engagement; the adjacent learning-analytics literature has quantified this gap and would let the authors state the proxy's limits concretely rather than generically. *Suggestion*: use the log-vs-self-report literature (search lead — recent learning-analytics comparisons of survey and trace data; `[UNVERIFIED]`) to bound what the correlation stands in for.
2. **Stakeholder/equity blind spot in the onboarding recommendation** (Severity: Major). The §5 recommendation targets students who do not yet see the LMS as useful — but the voluntary sample (§6) most plausibly under-represents exactly those low-engagement students. *Why it matters*: the recommendation is aimed at a group the study observed least well, and digital-access/literacy differences mean usefulness-oriented onboarding may not land equally. *Suggestion*: add a short stakeholder/equity paragraph noting (a) the non-respondent = target-population mismatch and (b) that onboarding effectiveness may vary by students' prior digital fluency.
3. **Under-used adjacent framings for the mechanism** (Severity: Minor). *Why it matters*: "perceived usefulness → more use" is stated but not theorized; behavioral-design / self-determination accounts would give the association a mechanism worth testing. *Suggestion*: one paragraph connecting to a motivation/behavioral-design lens (search lead — self-determination-theory work on technology engagement; `[UNVERIFIED]`), as a future-work hook, not a new analysis.

### Detailed Comments

#### Assumption Audit
- **Explicit assumptions**: perceived usefulness and self-reported use are distinct, meaningfully-measured constructs. The paper defends distinctness weakly (both are single-survey self-reports — a point I flag but leave to R1 as a common-method issue).
- **Implicit assumptions**: that self-reported frequency is an acceptable stand-in for engagement (partly acknowledged) and that perceived usefulness is an institutional *lever* (assumed in §5's onboarding move).
- **Paradigmatic assumptions**: a positivist survey stance; reasonable here, but the log-data paradigm would read the same question behaviorally — worth a sentence.

#### Cross-Disciplinary Connections
- **Parallel research**: learning-analytics trace-data studies of LMS engagement ask the same question with logged behavior.
- **Borrowing opportunities**: quantified self-report-vs-log divergence; behavioral-design/self-determination mechanisms.
- **Methodological borrowing**: even a small sub-sample with LMS log data would triangulate the self-report DV powerfully — a strong, feasible future step.

#### Practical Impact
- **Real-world application**: onboarding-that-shows-usefulness is an actionable, low-cost lever — genuinely useful to practitioners *if* the causal direction cooperates (which the paper honestly says it cannot confirm).
- **Implementation feasibility**: feasible; but effectiveness likely varies by student digital fluency (equity dimension, W2).
- **Stakeholders**: the low-engagement / non-respondent student — the recommendation's target — is the least-observed group (W2). Faculty and instructional designers who would deliver the onboarding are not discussed.

#### Broader Implications
- **Ethical dimensions**: minimal risk; anonymous, consented. No concern.
- **Social impact**: equity of onboarding effectiveness across digital-access levels (W2) is the one social dimension worth adding.
- **Future directions**: log-data triangulation and a longitudinal or multi-site design (the paper already names these — good).

### Cross-Disciplinary Reading Recommendations
- Learning-analytics comparisons of self-reported vs. logged LMS use (search lead; `[UNVERIFIED]` — different discipline: learning analytics / educational data mining).
- Self-determination-theory / behavioral-design accounts of technology engagement (search lead; `[UNVERIFIED]` — different discipline: motivational psychology / HCI).
- *No-invention rule (#574 A5): both are topic-level search leads across disciplinary lines; I attest no specific author/year/venue and invent no DOIs.*

### Questions for Authors
1. How far does self-reported frequency proxy logged engagement in your setting — can you bound the proxy using the log-vs-self-report literature?
2. Given the voluntary sample, are the low-engagement students your onboarding recommendation targets adequately represented?
3. Could a mechanism lens (behavioral design / self-determination) frame *why* perceived usefulness tracks use, as a testable future step?

### Minor Issues
- "digital-environment onboarding" (§5, via Whitfield 2019) is a practitioner-account citation; label it as such so adjacent-field readers weight it appropriately.

---

## SEAT 5 of 5 — Devil's Advocate

### Phase 1 — Paper-content-blind pre-commitment

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** Adversarially: where can I break the design so the headline number does not mean what the paper implies? Cross-sectional single-instrument self-report is a rich target — common-method variance, reverse causation, single-item DV. My job is to find the strongest such attack, then gate my own severity honestly (#215/#216).

**D2 — domain_accuracy (mandatory).** Adversarially: is any field claim overstated, is the evidence cherry-picked toward the hypothesis, and is the citation base real? I look for confirmation bias and omitted contradicting evidence.

**D3 — argumentative_coherence (mandatory).** Adversarially: does the conclusion actually follow, or does the paper's heavy hedging paper over a gap between a moderate correlation and even the modest implication it draws? Internal contradictions between the confident and cautious passages.

**D4 — cross_disciplinary_relevance (high).** Adversarially: is any interdisciplinary/implication claim (onboarding) asserted beyond what a correlation licenses?

**D5 — writing_and_structure (normal).** Adversarially: does polish substitute for substance — does fluent hedging mask a thin contribution?

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for`: a design attack that, if it lands, invalidates the headline (common-method inflation; reverse causation asserted as direction; single-item DV making r uninterpretable).
- `what_triggers_block`: a *foundation-collapse* or *data–conclusion mismatch* — the paper's own evidence contradicts its stated conclusion, or a core assumption is demonstrably false and un-caveated.
- `what_triggers_warn`: a serious but caveated design vulnerability (the paper names the risk) that weakens but does not break the claim.

### D2: domain_accuracy
- `what_to_look_for`: cherry-picking, omitted contradicting evidence, unreal/placeholder citations, absolute-priority overclaim.
- `what_triggers_block`: a demonstrably false central domain claim, or a citation base shown to be fabricated such that the argument is unsupported.
- `what_triggers_warn`: thin/one-sided evidence or unverifiable-looking citations short of demonstrated fabrication.

### D3: argumentative_coherence
- `what_to_look_for`: a gap between evidence and conclusion; internal contradiction between confident and cautious passages.
- `what_triggers_block`: the conclusion does not follow from the evidence even taken at face value.
- `what_triggers_warn`: a mild inferential stretch that the hedging mostly, but not fully, covers.

### D4: cross_disciplinary_relevance
- `what_to_look_for`: an implication asserted beyond correlational license.
- `what_triggers_block`: a central causal/policy claim presented as established.
- `what_triggers_warn`: a hedged-but-still-leaning implication.

### D5: writing_and_structure
- `what_to_look_for`: polish masking thin substance.
- `what_triggers_block`: (rare) unreadable.
- `what_triggers_warn`: fluent hedging that inflates perceived contribution.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 — Paper-visible review

contract_role: da

## Devil's Advocate Review

*(Fairness note before the attack, per Review Discipline #5: the paper is genuinely well-scoped and honestly reported — it disclaims causation, bounds generalization, and flags its self-report measure. The following is the strongest case a hostile scholar could still mount.)*

### Strongest Counter-Argument
The paper's entire empirical content is a single correlation, r=.42, between two variables measured on **the same self-report instrument, at the same time, from the same respondents**. The most parsimonious rival explanation for that association is not "perceived usefulness tracks LMS use" but **common-method variance**: when a person answers "this tool is useful" and "I use this tool a lot" on adjacent 5-point items, a consistency/response-style factor alone will manufacture a moderate positive correlation with no substantive relationship between the constructs at all. The paper never names common-method variance; it defends against the *self-report-vs-behavior* gap (which concerns the DV's validity) but not against the *shared-method* gap (which concerns the correlation's very existence). Layer on the paper's own admissions — the direction is unidentified (reverse causation "equally consistent," §5), the DV is a single ordinal item, and the sample is voluntary and self-selected — and a hostile reviewer can argue the study has established almost nothing beyond "two adjacent survey items co-vary as adjacent survey items do." The r² is ~.18: over 80% of the variance in reported use is *unexplained* by perceived usefulness, which the paper concedes (§4). The counter-argument is therefore: the one number the paper offers is simultaneously (a) plausibly inflated by shared method, (b) directionally uninterpretable, and (c) measured on a fragile single item — so even the modest onboarding implication rests on a foundation the paper itself has argued away. The paper's honesty, on this reading, is not a virtue that rescues the contribution; it is a running admission that there may be no contribution left to make.

*(Verdict-time surface-form parity self-check, #216: I have stated this attack in precise, technical language ["common-method variance", "r²=.18"]. Running the opposite-style counterfactual — would I rate the attack weaker if phrased informally as "they're just measuring the same feeling twice"? No: the substance is identical and the paper-checkable claim [same instrument, same time, no CMV discussion] holds either way. The verdict keys off the paper's evidence, not my phrasing. The attack is admitted on substance, not polish — and, symmetrically, I must not let my own technical phrasing inflate it into a CRITICAL if the paper's caveats blunt it, which they partly do; see severity gating below.)*

### Issue List

#### CRITICAL
| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|----------|---------------------|-----------------------------|
| — | — | *No CRITICAL finding survives severity gating.* The strongest candidate (common-method variance) is a **serious but caveat-adjacent** flaw: the paper does not name CMV, but it does disclose that the measure is self-report, the direction is unidentified, and the variance explained is modest — so the conclusion the paper actually states (a bounded, correlational, "modest evidence" association) is NOT contradicted by its own data (no data–conclusion mismatch), and no core assumption is asserted as true-and-false. Per DA CRITICAL criteria, this is not Foundation Collapse, Logic-Chain Break, Data–Conclusion Mismatch, or a Stronger-Counter-Narrative that the paper's *stated* conclusion ignores — the paper's stated conclusion already absorbs most of the attack. Down-rated to MAJOR. | — | — | — |

#### MAJOR
| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|----------|---------------------|-----------------------------|
| DA-M1 | 4 (Logic chain) / D1 | **Common-method variance is never addressed.** Both constructs are self-reported on one instrument at one time; a shared-method/response-style factor is a rival explanation for r=.42 that the paper does not name or bound. This is distinct from the self-report-vs-log caveat the paper *does* raise (that concerns DV validity, not shared-method inflation of the correlation). | §3.2, §4 (r=.42); caveats §2/§6 do not mention CMV | Not a field-norm-dependent severity — CMV is a general inference standard for same-instrument correlations, so no #215 grounding needed; the severity rests on the paper's own evidence structure. | The paper's evidence (two same-instrument self-reports) directly creates the CMV pathway; the omission is in the paper, not a norm imported from another subfield. |
| DA-M2 | 5 (Overgeneralization) / D2 | **Onboarding implication targets the least-observed group.** §5 recommends usefulness-oriented onboarding for students who don't see the LMS as useful, but §6 concedes the voluntary sample over-represents engaged students — so the recommendation is drawn for a population the study under-sampled. | §5 (onboarding) vs. §6 (voluntary over-representation) | — | Internal tension between the implication and the acknowledged sampling bias — grounded in the paper's own two statements, not an external norm. |

#### MINOR
| # | Dimension | Issue Description | Location |
|---|-----------|-------------------|----------|
| DA-m1 | 2 (Cherry-picking) / integrity | Six references, all `10.5555/2050xxx`-pattern DOIs, no TAM primary source. Not demonstrably fabricated from the text alone, but an evidence base that cannot be independently anchored is a confirmation-adjacent risk. (R2 owns the domain-coverage severity; I flag the one-sidedness.) | §References; §2 |
| DA-m2 | 8 (So what?) | The contribution is one correlation the authors themselves call unsurprising and consistent. The increment over the cited prior work is not articulated. | §2, §7 |
| DA-m3 | 1 (Core thesis) | r²≈.18 means >80% of reported-use variance is unexplained; the paper states this fairly (§4) but the framing ("perceived usefulness tracks LMS engagement") still leads with the 18%. | §4, Abstract |

### Ignored Alternative Explanations/Paths
1. **Common-method / response-style variance** (see DA-M1): a single consistency factor across adjacent self-report items is a more parsimonious account of r=.42 than a substantive PU→use relationship, and it is entirely unaddressed.
2. **Third-variable / course-structure confound**: course requirements and assessment schedules (which the paper mentions in §4 as unmodeled) could independently drive *both* perceived usefulness *and* use, producing the correlation with no direct link — a classic omitted-variable path the paper notes as "many influences" but never treats as a rival to its own framing.
3. **Reverse causation as the primary path**: the paper grants this is "equally consistent" (§5) but then still leads its discussion and abstract with the usefulness-first ordering; the reverse ordering (use breeds perceived usefulness through familiarity) is at least as plausible.

### Missing Stakeholder Perspectives
- The low-engagement / non-responding student — the onboarding recommendation's actual target, least represented in a voluntary sample. *(Identifying the absence only; the elaboration is R3's.)*
- Instructors / instructional designers who would deliver "usefulness-oriented onboarding."

### Unexamined Premise (Frame-Lock Detection)
The paper assumes throughout that a **measured association between two self-reports is itself a finding worth reporting** — that co-variation of "perceived useful" and "reported use" carries information about LMS engagement. If common-method variance is the driver (DA-M1), the entire study reduces to a demonstration that survey respondents answer adjacent Likert items consistently, which is a fact about surveys, not about LMS use. Every downstream claim inherits this unexamined premise. The paper's caveats circle it (self-report limits, direction unknown) but never state it as the load-bearing assumption it is.

### Observations (Non-Defects)
- The paper's refusal to make a causal or priority claim is genuinely disciplined and removes the two attacks (causal overreach, "first study" overclaim) a DA most often lands — a real credit.
- The Spearman robustness check pre-empts the "Pearson-on-ordinal" attack before it can be made.
- Concession-rate note (self-monitoring): I withdrew my only CRITICAL candidate to MAJOR on substance (the paper's stated conclusion already absorbs the attack), not under pressure — there was no rebuttal, this is first-pass severity gating. That is one down-rating of one candidate; it does not trip the >50% concession flag.

---

# PART 3 — Editorial Synthesis (Phase 2)

*The synthesizer runs the v3.6.2 Sprint Contract three-step arithmetic protocol over the five Phase-2 dimension-score outputs, then produces the Editorial Decision Package. The DA does not carry contract dimension scores (its Editorial Decision derives from its own dimension read, and its findings are tracked separately as DA-CRITICAL/MAJOR). Per the pinned grammar every seat emitted `score:` lines; those are collected below.*

## Sprint-contract dimension scoring matrix (Step 1)

Each seat's Phase-2 `## Dimension Scores` (`block | warn | pass`), applying that seat's own Phase-1 triggers to the manuscript:

| Dimension (priority) | EIC | R1 (meth) | R2 (domain) | R3 (persp) | DA | 
|----------------------|-----|-----------|-------------|------------|-----|
| **D1 methodology_rigor** (mandatory) | warn | warn | pass | pass | warn |
| **D2 domain_accuracy** (mandatory) | warn | pass | warn | pass | warn |
| **D3 argumentative_coherence** (mandatory) | pass | pass | pass | pass | pass |
| **D4 cross_disciplinary_relevance** (high) | warn | pass | pass | warn | pass |
| **D5 writing_and_structure** (normal) | pass | warn | pass | pass | pass |

*Derivation of each seat's scores from its Phase-2 review (score = seat's committed trigger applied):*
- **EIC** — D1 warn (single-item DV, a referee-contestable measurement choice, revision-fixable); D2 warn (thin/placeholder reference base, oversells-comparability risk); D3 pass (scope held title→conclusion); D4 warn (log-data adjacency ignored); D5 pass (clear, conventional).
- **R1** — D1 warn (single-item DV + missing-data/power-basis gaps, revision-fixable, not fatal → explicitly "no block"); D2 pass (measurement claims internally correct, α correctly applied); D3 pass (conclusions bounded to the numbers); D4 pass (measurement legible); D5 warn (no results table/scatterplot).
- **R2** — D1 pass (correlational survey is the field-conventional vehicle); D2 warn (missing canonical primary sources + reference-existence concern + thin recent lit — all revision-fixable, none a demonstrably-false central claim → warn not block); D3 pass (gap→contribution coherent, no overclaim); D4 pass (adjacent terms used correctly); D5 pass (genuine synthesis of the small set).
- **R3** — D1 pass (measurement stance defensible from the practical angle, self-report gap acknowledged); D2 pass (no cross-disciplinary claim mis-stated); D3 pass (implications hedged to match a moderate r); D4 warn (log-data literature named-not-leveraged + stakeholder/equity blind spot — additive, revision-fixable); D5 pass (accessible).
- **DA** — D1 warn (CMV unaddressed + single-item DV: serious but caveat-adjacent, down-rated from block per #215/#216 gating because the paper's stated conclusion absorbs the attack — no data–conclusion mismatch); D2 warn (one-sided/placeholder citations, confirmation-adjacent, short of demonstrated fabrication → warn not block); D3 pass (conclusion follows from evidence taken at face value; hedging genuine, not a coherence break); D4 pass (implication hedged, no causal assertion); D5 pass (polish does not mask — the thinness is openly stated).

## Failure-condition evaluation (Step 2)

Panel N=5. Ordering `pass < warn < block`. Applying each condition's `cross_reviewer_quantifier` with panel-relative thresholds (majority for N=5 fires at ≥3):

**F1** (severity 90, `any`): "any mandatory dimension scores `block`" — mandatory dims are D1, D2, D3. No seat scored `block` on any mandatory dimension (max is `warn`). **fired: false.**

**F2** (severity 70, `majority`): "two or more mandatory dimensions score `warn` or worse" — evaluated per reviewer, fires if a majority (≥3 of 5) of reviewers each have ≥2 mandatory dims at `warn`-or-worse. Per-reviewer count of mandatory (D1/D2/D3) dims at `warn`+:
- EIC: D1 warn, D2 warn, D3 pass → **2** ✔ (≥2)
- R1: D1 warn, D2 pass, D3 pass → 1 ✗
- R2: D1 pass, D2 warn, D3 pass → 1 ✗
- R3: D1 pass, D2 pass, D3 pass → 0 ✗
- DA: D1 warn, D2 warn, D3 pass → **2** ✔ (≥2)

Reviewers meeting the predicate: EIC, DA = **2 of 5**. Majority threshold for N=5 is ⌊5/2⌋+1 = **3**. 2 < 3. **fired: false.**

**F3** (severity 60, `any`): "any high-priority dimension scores `block`" — the sole high-priority dim is D4. D4 scores across seats: warn, pass, pass, warn, pass — no `block`. **fired: false.**

**F0** (severity 10, `all`): "every mandatory dimension scores `pass`" — requires all 5 reviewers to score D1, D2, D3 all `pass`. EIC (D1/D2 warn), R1 (D1 warn, D5 n/a), R2 (D2 warn), DA (D1/D2 warn) break this. **fired: false.**

## Precedence and decision (Step 3)

fired_conditions: []

No failure condition fired. Per Step 3, when no condition fires the decision is the contract's accept-grade action (F0, `editorial_decision=accept`).

**However** — the sprint-contract arithmetic yields the *accept-grade* action ONLY because the contract's failure conditions are deliberately coarse (block-triggered and majority-warn-triggered); a panel of all-`pass`/`warn` with no `block` and no warn-majority does not trip any gate. This is the contract behaving as designed: it is a **floor gate**, not the full editorial decision. The mechanical `editorial_decision=accept` is the contract-floor signal (no blocking or majority-warn defect), which the editorial synthesis now refines against the reviewers' actual recommendations and the `editorial_decision_standards.md` matrix. The four scoring seats recommend **Minor / Minor / Major / Minor**, with a substantive MAJOR from R2 (literature anchoring + reference-existence) and two MAJOR findings from the DA (CMV; onboarding/sampling mismatch). Under `editorial_decision_standards.md` §2 (row "Minor Minor Major Minor" → Major-leaning) and the One-Outlier rule (examine the Major rationale; if valid and others under-weighted it, escalate), the R2 Major rationale **is** valid and is corroborated by DA-M1/DA-M2 and by the EIC/R1 measurement warnings. The conservative principle (§3b) therefore governs.

**Reconciled editorial decision: MAJOR REVISION.** The contract floor is cleared (no CRITICAL, no block, F1/F2/F3 all unfired — consistent with Checkpoint Rule #4 since the DA raised **no** surviving CRITICAL), but the accumulated MAJOR findings — the unaddressed common-method-variance rival explanation, the missing canonical-literature anchoring plus reference-existence concern, and the single-item DV — require re-analysis-adjacent work (framing, literature, measurement justification) and a re-review, which is the definition of Major Revision, not Minor.

---

# Editorial Decision

## Manuscript Information
- **Title**: Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students
- **Manuscript ID**: (not assigned)
- **Submission Date**: (not provided)
- **Decision Date**: 2026-07-24
- **Review Round**: Round 1

## Review Panel Provenance (#540)

All five reviewer personas ran on a single model family (the session's primary Anthropic family). Persona diversity is not model diversity — blind spots may be correlated across reviewers (Ren et al. 2026, arXiv:2607.13104 §5.2). `ARS_CROSS_MODEL` was not configured and no cross-model consent was given, so the Reviewer-2 cross-model substrate swap did not run and no cross-model blind-decision check (Step 4b) was performed. Read the five reports as five perspectives from one model, not five independent substrates.

---

## Decision

### Major Revision

*(Not a Reject: the design is sound for its bounded question, the reporting is above tier, and no reviewer recommends rejection. Not Minor: three MAJOR findings — common-method variance, literature anchoring / reference existence, single-item DV — require substantive framing, literature, and measurement work plus a re-review, exceeding the "supplement/clarify in 2–4 weeks" Minor threshold in `editorial_decision_standards.md` §1.)*

---

## Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | Common-method variance is never addressed: both constructs are self-reported on one instrument at one time, giving a rival (response-style) explanation for r=.42 that the paper's existing self-report caveat does not cover. | DA (corroborated by R1's common-method note) | §3.2 / §4 "r = .42"; caveats §2, §6 omit CMV | R1 |
| 2 | Technology-acceptance framing is unanchored and the six-reference base is unverifiable (all `10.5555/2050xxx`-pattern DOIs, no TAM/UTAUT primary source). | R2 (corroborated by EIC W-EIC-3, DA-m1) | §References; §1/§2 "technology-acceptance research" | R2 |
| 3 | The dependent variable is a single ordinal self-report item, justified nowhere, capping the reliability/precision of the paper's only outcome. | R1 (corroborated by EIC W-EIC-2) | §3.2 "a single five-point frequency item" | R3 |

---

## Reviewer Summary

| Reviewer | Role | Recommendation | Confidence |
|----------|------|---------------|------------|
| EIC | Q3 ed-tech Editor-in-Chief (Education Sciences / AJET profile) | Minor Revision | 4 |
| Reviewer 1 | Quantitative educational-measurement methodologist | Minor Revision | 5 |
| Reviewer 2 | Technology-acceptance / TAM-lineage domain scholar | Major Revision | 4 |
| Reviewer 3 | Learning-analytics / behavioral-data outsider | Minor Revision | 3 |
| Devil's Advocate | Adversarial stress-tester | (no scored recommendation; 0 CRITICAL, 2 MAJOR, 3 MINOR) | — |

---

## Consensus Analysis

*Sub-claim decomposition (Step 1b) applied. Denominator for consensus counting is the 4 non-DA reviewers (EIC, R1, R2, R3); DA findings tracked separately. `not-mentioned` = silence, never opposition.*

**Sub-claim inventory (traceability):**

| sub_claim_id | parent_weakness | positions (EIC / R1 / R2 / R3) | agree / conflict / silent | disposition |
|---|---|---|---|---|
| SC-1 | Single-item self-report DV | raised (W-EIC-2) / raised (R1-W1) / not-mentioned / corroborated (R3 assumption audit) | 3 / 0 / 1 | **CONSENSUS-3** (R2 silent) |
| SC-2 | Literature under-anchored / no TAM primary source | raised (W-EIC-3) / not-mentioned / raised (R2-W1) / not-mentioned | 2 / 0 / 2 | corroborated finding (EIC+R2) |
| SC-3 | Reference existence / placeholder DOIs | raised (W-EIC-3) / not-mentioned / raised (R2-W2) / not-mentioned | 2 / 0 / 2 | corroborated finding (EIC+R2), integrity class |
| SC-4 | Contribution thin / increment not articulated | raised (W-EIC-1) / not-mentioned / corroborated (R2 "incremental, small") / not-mentioned | 2 / 0 / 2 | corroborated finding (EIC+R2) |
| SC-5 | No results table / scatterplot | not-mentioned / raised (R1-W4) / not-mentioned / not-mentioned | 1 / 0 / 3 | single-reviewer finding (R1) |
| SC-6 | Missing-data / response-rate accounting | not-mentioned / raised (R1-W2) / not-mentioned / not-mentioned | 1 / 0 / 3 | single-reviewer finding (R1) |
| SC-7 | Onboarding recommendation vs. voluntary-sample mismatch (stakeholder/equity) | not-mentioned / not-mentioned / not-mentioned / raised (R3-W2) | 1 / 0 / 3 | single-reviewer finding (R3); corroborated by DA-M2 (DA tracked separately) |
| SC-8 | Log-data literature named but not leveraged | not-mentioned / not-mentioned / not-mentioned / raised (R3-W1) | 1 / 0 / 3 | single-reviewer finding (R3) |

### Points of Agreement (Consensus)

**[CONSENSUS-3]** (3 of 4 agree; the 4th silent):
1. **SC-1 — the single-item self-report dependent variable is a material measurement weakness.** EIC (W-EIC-2), R1 (W1, the seat with Confidence 5 on this exact point), and R3 (assumption audit) all raise it; **R2 is silent** (not opposed). Because the sole domain-competent seat is silent rather than disputing, and the methodology seat holds this at Confidence 5, this is a strong, action-bearing consensus. The DV must be justified or foregrounded as a first-order limitation.

### Corroborated findings (two reviewers, below the consensus bar, no conflict)
- **SC-2 (literature anchoring)** and **SC-4 (thin contribution)** — EIC + R2, no conflict. Action-bearing; R2 (domain seat, Confidence 4) carries the weight, so these drive the decision despite not being a formal CONSENSUS label.
- **SC-3 (reference existence / placeholder DOIs)** — EIC + R2, integrity class. R2 correctly declined to invent replacement citations (#574 A5); routed to the citation-existence gate and author correction.

### Points of Disagreement

There is **no genuine SPLIT** in this panel: no sub-claim has a `disputed` position (no reviewer argued that another's raised concern is *not* a real problem, nor recommended an incompatible remedy). The apparent decision-level divergence (R2 Major vs. the other three Minor) is a **severity/weighting difference on the overall recommendation, not a sub-claim conflict** — every reviewer's individual findings are mutually compatible and additive.

**Weighting resolution (recommendation-level, not a sub-claim SPLIT):**
- **R2 view**: Major Revision — the missing canonical literature and unverifiable references make the "comparable with prior work" positioning unsupported until real anchoring is added (Confidence 4, within domain).
- **EIC / R1 / R3 view**: Minor Revision — each sees its own concerns as supplement-able without redesign.
- **Editor's Resolution**: **Major Revision.** Disagreement type = severity/weighting. Arbitration by the One-Outlier rule (`editorial_decision_standards.md` §2) + conservative principle: R2's Major rationale is valid, sits within R2's domain expertise, and is *corroborated* — the reference-existence half (SC-3) is echoed by EIC, and the DA independently raised two MAJOR findings (CMV, onboarding/sampling mismatch) that the three Minor votes did not weigh. When the aggregate of one valid domain Major + two DA Majors + a Confidence-5 measurement concern exceeds what a 2–4-week supplement can absorb, the conservative resolution escalates to Major, per §3b.

---

## Decision Rationale

This is a competently executed, unusually honest single-site correlational survey whose reporting (effect size with CI, Spearman robustness, α, a power/sensitivity statement, explicit non-causal and single-site caveats) sits above its target tier, and whose scope is held identically from title to conclusion — no reviewer found over-claiming, and the Devil's Advocate's strongest attack landed only after being down-rated from CRITICAL to MAJOR precisely because the paper's stated conclusion already absorbs most of it (no data–conclusion mismatch; Checkpoint Rule #4 is satisfied — the DA raised **no** surviving CRITICAL, so Accept was mechanically available at the contract floor). The contract arithmetic confirms this floor: F1/F2/F3 all unfired, no `block` on any dimension. Acceptance is nonetheless not warranted, because three MAJOR-severity issues accumulate past the Minor threshold. First, common-method variance — the single most consequential rival explanation for a same-instrument, same-occasion correlation — is never named or bounded (DA-M1, corroborated by R1); this is fixable by framing and a limitation, not new data, but it is load-bearing for how the r=.42 is read. Second, the technology-acceptance framing lacks its primary-source anchor and the six-reference base is unverifiable (R2-W1/W2, corroborated by EIC); for a paper whose contribution is defined as *comparability with prior work*, the prior work must be real and correctly cited — genuine literature work, hence Major. Third, the single-item ordinal DV (CONSENSUS-3: EIC + R1 + R3) caps the reliability of the paper's only outcome and is justified nowhere. Under `editorial_decision_standards.md`, a valid domain Major corroborated across seats, plus two independent DA Majors, plus a Confidence-5 measurement consensus, resolves conservatively to **Major Revision** with re-review — not the mechanically-available Accept (which reflects only the coarse contract floor) and not Minor (which under-weights the corroborated Major). No cross-model check ran (env unset), so this decision rests on a single model family; the reader is cautioned accordingly (Review Panel Provenance).

---

## Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Source Reviewer | Severity | Section | Estimated Effort |
|---|--------------|--------------|----------------|----------|---------|-----------------|
| R1 | Address common-method variance: name it as a rival explanation for r=.42, argue why the association is not solely a same-instrument response-style artifact (or bound the concern), and, if possible, report any procedural/statistical mitigation. | — (DA-MAJOR) | DA (corrob. R1) | Major | §3.2, §4, §6 | 3–5 days |
| R2 | Anchor the technology-acceptance framing to its primary literature and verify/replace the six references. Confirm every DOI resolves to a real venue; add the foundational TAM/UTAUT sources and recent LMS-engagement work. **Author must supply real, verified citations — the panel supplied only `[UNVERIFIED]` search leads, no invented metadata (#574 A5).** | SC-2, SC-3 | R2 (corrob. EIC) | Major | §2, §References | 5–8 days |
| R3 | Justify the single-item self-report dependent variable (cite single-item-measurement-validity literature as a verified source, or provide corroboration), and foreground it as a first-order limitation; soften any precision language accordingly. | SC-1 | R1, EIC, R3 (CONSENSUS-3) | Major | §3.2, §6 | 2–4 days |
| R4 | Reconcile the onboarding recommendation with the voluntary-sample bias: state that the low-engagement students the recommendation targets are under-represented, and add the equity dimension (effectiveness may vary by digital fluency). | SC-7 | R3 (corrob. DA-M2) | Major→P1/P2 | §5, §6 | 1–2 days |

### Required Item Details

**R1: Common-method variance**
- **Problem**: Both variables are self-reported on one 5-point instrument at one time; a response-style/consistency factor is an un-addressed rival explanation for r=.42.
- **Source**: DA Strongest Counter-Argument + DA-M1; corroborated by R1's "common-method / single-instrument variance" note.
- **Requirement**: Add an explicit CMV discussion (name the mechanism, argue against pure-artifact, bound the concern); ideally report any mitigation (e.g., item separation, a marker-variable check if data allow).
- **Acceptance criteria**: A reader can see CMV named and either partly ruled out or explicitly retained as a limitation that qualifies the r.

**R2: Literature anchoring + reference verification**
- **Problem**: No TAM/UTAUT primary source; all six DOIs share a placeholder-pattern prefix and are unverifiable.
- **Source**: R2-W1/W2; corroborated by EIC W-EIC-3, DA-m1.
- **Requirement**: Verify every reference resolves; add foundational acceptance literature and recent LMS-engagement work; ensure the "comparable with prior work" claim is anchored to real, cited studies.
- **Acceptance criteria**: Every reference resolves to a real venue; the framing cites its primary sources; the citation-existence gate passes.

**R3: Single-item DV justification**
- **Problem**: The outcome is one ordinal item with no reliability estimate and no justification.
- **Source**: R1-W1 (Confidence 5), EIC W-EIC-2, R3 assumption audit (CONSENSUS-3).
- **Requirement**: Justify the single-item choice against measurement-validity literature or provide corroboration; foreground as a primary limitation.
- **Acceptance criteria**: The single-item choice is argued, not merely noted, and the discussion's precision language matches a single-item measure.

**R4: Onboarding recommendation vs. sampling bias**
- **Problem**: The recommendation targets a population (low-engagement students) the voluntary sample under-observed.
- **Source**: R3-W2; corroborated by DA-M2.
- **Requirement**: Note the target-population / non-respondent mismatch and add an equity sentence.
- **Acceptance criteria**: §5's implication is explicitly bounded by the §6 sampling limitation.

---

## Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Source Reviewer | Priority | Section | Expected Improvement |
|---|--------------|--------------|----------------|----------|---------|---------------------|
| S1 | Sharpen the stated increment: one sentence in §1/§2 on what this transparently-reported single-site estimate adds beyond the cited prior work. | SC-4 | EIC (corrob. R2) | P2 | §1, §2 | Answers the "why publish now" question |
| S2 | Add a descriptive-statistics table (M, SD, N, correlation matrix) and the scatterplot the text references; report r²=.18 explicitly. | SC-5 | R1 | P2 | §4 | Makes the key result inspectable |
| S3 | Report the response-rate denominator (invited-N) and state the missing-data mechanism/handling for the 14 incompletes. | SC-6 | R1 | P2 | §3.1 | Substantiates the §6 non-response caveat |
| S4 | Leverage (not merely name) the log-vs-self-report literature to bound what self-reported frequency proxies. | SC-8 | R3 | P2 | §2, §6 | Concretizes the DV's proxy limits |
| S5 | State how the ">.80 power for r≥.19" figure was computed (tool/method). | — | R1 | P3 | §3.4 | Reproducibility of the precision claim |
| S6 | Add a one-paragraph mechanism hook (behavioral-design / self-determination) as future work. | — | R3 | P3 | §5, §7 | Gives the association a testable mechanism |

---

## Revision Roadmap

### Priority 1 — Structural Revisions (Estimated total effort: ~10–14 days)
- [ ] R1 (SC —, DA-MAJOR): Add common-method-variance discussion and bounding to §3.2/§4/§6.
- [ ] R2 (SC-2, SC-3): Verify/replace all references; anchor the technology-acceptance framing to primary sources.
- [ ] R3 (SC-1, CONSENSUS-3): Justify and foreground the single-item DV limitation.
- [ ] R4 (SC-7): Reconcile the onboarding recommendation with the voluntary-sample bias + add equity note.

### Priority 2 — Content Supplementation (Estimated total effort: ~3–5 days)
- [ ] S1 (SC-4): Articulate the increment in §1/§2.
- [ ] S2 (SC-5): Add descriptive table + scatterplot; report r².
- [ ] S3 (SC-6): Response-rate + missing-data reporting.
- [ ] S4 (SC-8): Leverage the log-vs-self-report literature.

### Priority 3 — Text and Formatting (Estimated total effort: ~1 day)
- [ ] S5: Power-computation basis (§3.4).
- [ ] S6: Mechanism future-work hook (§5/§7).
- [ ] Label practitioner-account citations (e.g., Whitfield 2019) as such.
- [ ] Name the lineage "Technology Acceptance Model" explicitly.

### Total Estimated Effort
- **Major Revision**: ~3–4 weeks (14–20 working days), dominated by R2 (real literature work) and R1 (CMV framing).

---

## Revision Deadline
- **Recommended deadline**: 6–8 weeks from decision (Major Revision).
- **Basis**: `editorial_decision_standards.md` §1 Major Revision (6–8 weeks); re-review required after resubmission.
- **Extension policy**: notify 1 week before the deadline if an extension is needed.

---

## Response Letter Instructions

Please use the format in `templates/revision_response_template.md` (R→A→C: Reviewer point → Author response → Change location) to respond to every Required and Suggested item. Must include: (1) point-by-point response to each R1–R4 and S1–S6 item; (2) for any Suggested item declined, the reason; (3) change markup in the revised manuscript; (4) a cross-reference table of new section/paragraph locations. Note especially that R2 requires **verified real citations** — do not substitute the panel's `[UNVERIFIED]` search leads as if they were confirmed sources.

---

## Closing

We encourage you to carefully consider the reviewers' comments and submit a substantially revised manuscript. The study is honest and cleanly reported, and its bounded framing is a real strength; the required work is to close the common-method-variance gap, anchor and verify the literature, justify the single-item outcome measure, and align the practical recommendation with the sample. Please note that the revised manuscript will undergo another round of review.

---

## Appendix: Reviewer Report Summary

### EIC Report Summary
- Recommendation: Minor Revision | Confidence: 4
- Key Point: Honest, well-scoped modest note; publishable after fixing the single-item DV, thin references, and under-stated increment.

### Reviewer 1 (Methodology) Summary
- Recommendation: Minor Revision | Confidence: 5
- Key Point: Reporting is above tier (effect size + CI + Spearman + power); the one real weakness is the single-item ordinal DV, plus minor missing-data/table gaps — all revision-fixable.

### Reviewer 2 (Domain) Summary
- Recommendation: Major Revision | Confidence: 4
- Key Point: No false domain claim, but the technology-acceptance framing lacks its primary-source anchor and the six references are unverifiable — real literature work required.

### Reviewer 3 (Perspective) Summary
- Recommendation: Minor Revision | Confidence: 3
- Key Point: Commendably refuses the self-report=behavior conflation; needs to leverage (not just name) the log-data literature and to reconcile the onboarding recommendation with the under-observed target population.

### Devil's Advocate Summary
- Findings: 0 CRITICAL (strongest candidate — common-method variance — down-rated to MAJOR per #215/#216 gating because the paper's stated conclusion already absorbs it), 2 MAJOR (CMV; onboarding vs. sampling mismatch), 3 MINOR.
- Key Point: The paper's honesty pre-empts the causal- and priority-overclaim attacks; the surviving load-bearing challenge is unaddressed common-method variance, which qualifies but does not collapse the bounded conclusion.

---

*End of Editorial Decision Package. Read-only review (Iron Rule #6): the manuscript was not modified; all output is in this separate document.*
