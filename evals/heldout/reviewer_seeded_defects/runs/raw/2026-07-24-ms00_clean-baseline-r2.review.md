# Isolated-dispatch panel review — gamma-2

(Phase 1 calls were physically separated: each seat’s pre-commitment was produced by a clean agent that received only the contract + title/field/word_count and was forbidden from reading any manuscript.)

# PART 1 — FIELD ANALYSIS

# Field Analysis Report

## Paper Basic Information
- **Title**: Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students
- **Abstract length**: ~170 words
- **Full text length**: ~1,900 words (excluding references)
- **Number of references**: 6

## Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| Primary Discipline | Educational technology in higher education (technology acceptance / LMS adoption) |
| Secondary Disciplines | Educational measurement/psychometrics, information systems (TAM lineage), higher education studies |
| Research Paradigm | Quantitative Research (correlational, non-experimental) |
| Methodology Type | Survey / Questionnaire — single-site cross-sectional, bivariate correlation (Pearson + Spearman robustness) |
| Target Journal Tier | Q3 (with realistic reach into low Q2). Rationale: the study is competently and honestly executed but is deliberately narrow in scope — one association, one institution, n=214, a single-item outcome measure, and an explicitly incremental "data point" framing. The reference list is thin (6 sources) and the citations appear to be placeholder/synthetic (DOIs all under a single 10.5555 prefix, sequential 2050001–2050006), which is a red flag the reviewers should probe. Ambition level and contribution scope point to a specialized/regional journal, not a flagship. |
| Paper Maturity | Pre-submission. Rationale: complete IMRaD structure, clean prose, consistent APA-style citations and reference formatting, appropriate hedging language throughout, power analysis and CI reported, ethics statement present. The manuscript reads as polished and near-submittable; remaining issues are substantive-scope rather than structural or presentational. |

## Recommended Target Journals (Top 3)
1. **Australasian Journal of Educational Technology (AJET)** — Strong fit for single-institution, correlational LMS-engagement studies with honest, bounded claims; regularly publishes modest-scope empirical technology-acceptance work with methodological transparency. Best overall match.
2. **Journal of Computing in Higher Education** — Appropriate for TAM-lineage LMS studies; would push harder on theoretical contribution beyond a single bivariate correlation, so acceptance would likely require the authors to sharpen the "why this matters" argument.
3. **Education and Information Technologies** — High-volume outlet receptive to incremental empirical contributions on LMS use; a plausible home if the authors keep the framing modest, though reviewers there often ask for a fuller acceptance-model or additional predictors.

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC
**Identity Description**: Editor-in-Chief of a specialized educational-technology journal (AJET-tier), whose own program of work concerns LMS adoption and student engagement in higher education, and who routinely triages high volumes of single-site technology-acceptance survey submissions.
**Review Focus**:
  1. Fit and significance — does a single moderate bivariate correlation (r = .42) from one institution clear the novelty/contribution bar for the journal, or is it "already known" territory that merely re-confirms decades of TAM findings?
  2. Framing calibration — is the narrow descriptive-correlational framing an honest strength or a way to lower the contribution bar; does the paper offer any takeaway a reader could not have predicted from prior work?
  3. Reference base credibility — the 6 references all carry sequential 10.5555 placeholder DOIs; verify these are real, indexed sources and not fabricated/synthetic citations, since this bears directly on whether the manuscript is submittable at all.
**Will particularly care about**: Whether the paper's genuine methodological honesty (correlational-only language, cautions about self-report) is enough to offset its very thin incremental contribution, and whether the citation base is real.
**Possible blind spots**: May under-scrutinize the psychometric and statistical fine points (delegates those to R1); may accept the modest framing at face value without pressing on the single-item outcome's construct validity.

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1 — Methodology (quantitative / psychometrics)
**Identity Description**: A quantitative methodologist and psychometrician with an educational-measurement background, specializing in survey-instrument validation, correlational inference, and the measurement of self-reported behavior; publishes on reliability, single-item vs. multi-item measures, and the interpretation of effect sizes.
**Review Focus**:
  1. Measurement of the outcome — the dependent variable is a single five-point frequency item; probe its reliability (uncomputable for a single item), construct validity, and whether a Pearson r treating an ordinal single item as continuous is defensible (Spearman ρ = .40 is reported, which helps, but interrogate why Pearson is the headline).
  2. Instrument adaptation and reporting completeness — a six-item scale "adapted from Costa & Wren (2019)" with α = .88 is reported, but the adaptation is not described, the items are not shown, factor structure/dimensionality is not examined, and no CI or descriptive detail is given for the use item beyond a median category.
  3. Inferential claims vs. design — check that the power analysis (>.80 power for r ≥ .19), the CI [.30, .52], and the p-value are correctly reported and that no causal or directional language leaks into the results/discussion (spot-check: the paper is generally disciplined here).
**Will particularly care about**: Whether a single-item, self-reported outcome can bear the interpretive weight placed on it, and whether "perceived usefulness → perceived use" is effectively a common-method correlation between two self-reports rather than a substantive perception–behavior link.
**Possible blind spots**: May treat the domain contribution as out of scope; may not evaluate whether the LMS-engagement literature already answers this question (domain concern, left to R2).

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2 — Domain (higher-education educational technology)
**Identity Description**: A senior higher-education educational-technology researcher fluent in the technology-acceptance literature (TAM/UTAUT lineage) and in LMS-engagement studies, who tracks how the field has moved from perception-based self-report toward behavioral log/learning-analytics evidence.
**Review Focus**:
  1. Contribution against the field — situate r = .42 within the existing distribution of LMS perception–use correlations; is this an incremental confirmation, and does the paper add anything (a new population, a new instrument, a discrepant result) that warrants publication?
  2. Literature adequacy and currency — only 6 references, none clearly post-2021, no engagement with UTAUT/UTAUT2, self-determination, or the learning-analytics turn; assess whether the review is complete enough and whether the cited works (Costa & Wren, Delgado, Ibarra & Poll, Song, Vasquez, Whitfield) actually exist and say what is attributed to them.
  3. Common-method / same-source concern — because both measures are self-reported in the same instrument, evaluate whether the finding is confounded by common-method variance and whether the paper adequately flags this specific threat (it flags self-report divergence via Vasquez 2020 but does not name common-method bias).
**Will particularly care about**: Whether the paper's contribution is genuine and non-redundant given a mature literature, and whether the theoretical framing (invoking technology acceptance while explicitly declining to test an acceptance model) is coherent.
**Possible blind spots**: May under-weight statistical/psychometric subtleties (left to R1); may accept the honesty of the framing as sufficient contribution.

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3 — Cross-disciplinary / Practical (learning analytics + institutional practice)
**Identity Description**: A learning-analytics scientist and instructional-technology practitioner who works with LMS system logs and institutional onboarding programs, approaching the paper from a behavioral-data and applied-implementation angle rather than a survey-psychometrics one.
**Review Focus**:
  1. Self-report vs. behavioral reality — from a log-data perspective, press the gap between reported and actual engagement (the paper cites Vasquez 2020 on exactly this); is a self-reported "perceived use" measure meaningful enough to inform practice, and would available LMS logs have been the stronger design?
  2. Practical/onboarding implications — the discussion suggests usefulness-oriented onboarding "may be worth institutional attention" (citing Whitfield 2019, a practitioner account); evaluate whether a moderate correlation between two self-reports can responsibly ground any onboarding recommendation, and whether the recommendation is over-reaching given the design.
  3. Overlooked confounders and assumptions — surface field-obvious drivers of LMS use that are unmeasured here (course requirements, assessment schedule, instructor expectations — the paper gestures at these but does not model them) and assess whether the voluntary-response/self-selection bias is handled honestly.
**Will particularly care about**: Whether the study, as a self-report-only design, can say anything actionable that a learning-analytics/log-based study could not say better, and whether practical claims stay proportional to the evidence.
**Possible blind spots**: May over-emphasize the "should have used logs" critique and undervalue the legitimate, low-cost role of perception surveys; may drift toward re-designing the study rather than reviewing the one submitted.

## Review Strategy Recommendations

- **The paper's defining feature is disciplined honesty, and that is exactly what the panel must stress-test.** The manuscript scrupulously uses correlational language, reports a Spearman robustness check, gives a power analysis and CI, and stacks limitations. The central editorial question is not "are the claims overstated?" (they are not) but "is a deliberately modest, single-association, single-site finding a publishable contribution, or does honest framing merely relabel a thin result?" Reviewers should judge contribution, not just correctness.
- **Citation-integrity flag for all reviewers.** Every one of the 6 references carries a sequential placeholder-style DOI under the 10.5555 test/example prefix (2050001 through 2050006). This is a strong signal that the citations may be synthetic or fabricated. The EIC and R2 in particular should treat verification of these sources as a gating check; a review that praises the paper's "consistency with prior work" without confirming that prior work exists would be a serious miss. This is the single most important item to surface at the synthesis stage.
- **Deliberate methodological complementarity, minimal overlap.** R1 owns the psychometrics and inference (single-item outcome, Pearson-on-ordinal, undescribed scale adaptation, no item-level reporting); R2 owns the domain contribution and literature adequacy; R3 owns the self-report-vs-log-data and applied-implication angle. The one convergence point to watch is **common-method variance** — both R1 (as a measurement artifact) and R2/R3 (as a substantive confound between two self-reports) are likely to raise it. The synthesizer should merge these into a single consolidated concern rather than triple-counting it, while preserving that all three independently flagged it (a signal of its importance).
- **Predictable tension between R3 and the others.** R3's log-data orientation may push toward "this should have been a behavioral study," which risks reviewing the paper the authors did not write. The EIC and R1 should keep the panel anchored to the honest scope the authors declared. Frame R3's contribution as "does the self-report design still yield an actionable finding?" rather than "was self-report the wrong choice?"
- **Tone calibration.** Maturity is pre-submission and the writing is clean, so developmental hand-holding is unnecessary. The appropriate register is a rigorous accept-with-conditions / minor-to-major-revision review focused on (a) verifying the reference base, (b) strengthening or justifying the single-item outcome measure, and (c) sharpening the contribution claim — not line-editing or structural rescue.

# PART 2 — SEATS

## SEAT — EIC

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory):** From the editorial chair I read this dimension as asking whether the study's design and reporting clear the field's peer-review bar for a quantitative undergraduate survey. For a cross-sectional survey of perceived usefulness and self-reported LMS use, that means a defensible sampling frame, an adequate and justified sample, transparent instrument provenance and reliability, and statistical reporting that a reader could in principle reproduce. My concern at the journal level is whether the empirical foundation is solid enough that any contribution built on it will not collapse under scrutiny.

**D2 — domain_accuracy (mandatory):** I read this as whether the paper represents the educational-technology evidence base honestly — TAM/UTAUT-adjacent constructs used correctly, prior LMS-adoption findings cited without distortion, and no factual slips in domain terminology (e.g., conflating perceived usefulness with actual use, or self-reported use with log-based use). As EIC I care that the paper sits accurately inside the conversation it claims to join, so readers trust its scholarship.

**D3 — argumentative_coherence (mandatory):** From the bird's-eye view this dimension is about whether the central thesis holds together from research question through to conclusion, whether the correlational evidence actually supports the claims drawn from it, and whether the paper avoids the causal or generalization fallacies that cross-sectional self-report designs invite. My editorial worry is over-promising: a conclusion that outruns what a single-site cross-sectional survey can license.

**D4 — cross_disciplinary_relevance (high):** I read this as whether the framing, construct definitions, and implications are legible and useful beyond the narrow LMS-research niche — to instructional designers, higher-education administrators, and adjacent HCI/information-systems readers. Interdisciplinary claims (e.g., implications for platform design or institutional policy) must be substantiated, not asserted. As EIC I judge whether the paper earns space for a readership wider than the immediate sub-field.

**D5 — writing_and_structure (normal):** I read this as whether the manuscript is organized, clearly written, and conventionally presented — coherent title-to-abstract-to-conclusion flow, adequate figures/tables for a survey report, and adherence to venue formatting. At ~1597 words this is a very short manuscript, so my editorial attention here is whether the compression sacrifices necessary reporting rather than merely trimming padding.

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for`: A named sampling frame and recruitment method; reported sample size with a justification (power analysis or defensible rationale); response rate for the survey; instrument source (validated scale vs. ad hoc items) with reliability evidence (e.g., Cronbach's alpha); clear operationalization of "self-reported use" and its measurement; statistical tests named with assumptions, effect sizes, and confidence intervals rather than bare p-values.
- `what_triggers_block`: No sampling/recruitment description at all, OR a sample so small or opaque that the analysis is uninterpretable, OR the instrument's provenance and reliability are entirely absent, OR statistical claims reported with no test named and no dispersion/uncertainty — i.e., the empirical foundation cannot be evaluated or reproduced even in principle.
- `what_triggers_warn`: The core design is reportable but has material gaps — missing response rate, reliability stated for only some scales, effect sizes omitted while p-values are present, or sample-size justification absent though the N is plausibly adequate. Recoverable in revision without redoing the study.

### D2: domain_accuracy
- `what_to_look_for`: Correct and current use of adoption-model constructs (perceived usefulness, perceived ease of use, behavioral intention, actual use) with the right lineage cited; prior LMS/e-learning adoption findings represented faithfully; precise terminology that keeps "perceived usefulness," "self-reported use," and "actual/logged use" distinct; no overstated citations of what earlier work found.
- `what_triggers_block`: A load-bearing claim that misrepresents the domain evidence or a foundational construct (e.g., treating self-reported use as objective behavioral data throughout, or attributing to prior work a finding it does not contain) such that the paper's contribution rests on a factual error.
- `what_triggers_warn`: Isolated terminological imprecision or a citation that oversimplifies prior findings without invalidating the argument — correctable by rewording and re-citing.

### D3: argumentative_coherence
- `what_to_look_for`: A research question that the analysis actually answers; conclusions scoped to correlational, single-time-point, self-report evidence; explicit acknowledgment of limits on causality and generalization; internal consistency from title through abstract, hypotheses, results, and conclusion.
- `what_triggers_block`: The central conclusion contradicts or is unsupported by the reported results, OR a causal claim ("X increases use") is drawn from cross-sectional correlational self-report with no hedge — a fallacy that undermines the paper's core argument rather than a fixable overstatement in one sentence.
- `what_triggers_warn`: Occasional over-reach in phrasing (a stronger claim than the data license) or a limitations section that under-states the design's constraints, where the underlying argument remains sound and the fix is rescoping the claims.

### D4: cross_disciplinary_relevance
- `what_to_look_for`: Construct definitions and framing intelligible to adjacent-field readers without LMS insider knowledge; implications for design, practice, or policy that follow from the findings; interdisciplinary assertions backed by evidence or citation rather than asserted.
- `what_triggers_block`: A high-priority failure where the paper's stated cross-disciplinary or applied implications are unsubstantiated to the point of being unsupported claims (e.g., sweeping policy/design prescriptions with no evidentiary link), such that its reach beyond the sub-field is not earned.
- `what_triggers_warn`: Framing that is serviceable but insular — jargon left undefined for outside readers, or implications gestured at but thinly connected to the results — improvable by reframing.

### D5: writing_and_structure
- `what_to_look_for`: Logical section order and a title/abstract/conclusion that agree; prose clear enough to follow the argument on one read; tables/figures that report the survey results legibly and are referenced in text; adherence to venue length and formatting conventions, with the ~1597-word compression not omitting required method or results reporting.
- `what_triggers_block`: Disorganization or opacity severe enough that the argument cannot be followed, or required reporting sections are structurally absent — a rare bar for this normal-priority dimension.
- `what_triggers_warn`: Clarity or structural rough edges — awkward exposition, under-labeled or uncited tables, title/abstract/conclusion drift, or compression that trims necessary detail — that impede but do not prevent comprehension.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

All three files are read. Now I'll produce my Phase 2 EIC review, applying my Phase 1 committed triggers to the manuscript.

Key observations against my committed scoring plan:

- **Reference integrity (my Phase 1 D2 focus + reviewer card gating item):** All 6 references carry sequential DOIs under the `10.5555/2050001`–`2050006` prefix. `10.5555` is the reserved test/example DOI prefix; the strictly sequential numbering is a strong fabrication/placeholder signal. This bears on D2 (domain accuracy — the paper claims consistency with prior work I cannot confirm exists).
- **D1:** Design is honestly reported — sampling frame, N=214, response accounting (233→214), α=.88 for the PU scale, power analysis, CI, Spearman robustness. Gaps: single-item outcome, undescribed scale adaptation, no response rate against eligible population. These are warn-grade under my committed plan, not block.
- **D3:** Discipline is strong — correlational language throughout, causal caveats explicit, limitations stacked. My committed block trigger (unhedged causal claim) does not fire.
- **D4:** Onboarding implication is hedged ("suggested by, not proven by"). Serviceable but thin.
- **D5:** Clean IMRaD, but no table/figure at all for a survey report, and the ~1600-word compression trims item-level reporting.

Now the report.

## EIC Review Report

### Reviewer Identity

Editor-in-Chief of a specialized educational-technology journal (AJET-tier), with a personal program of work on LMS adoption and student engagement in higher education, routinely triaging a high volume of single-site technology-acceptance survey submissions.

### Overall Recommendation

Major Revision

### Confidence Score

4 — High confidence. LMS adoption and technology-acceptance survey work is squarely my area; the one point where I defer is the psychometric fine grain of the single-item outcome, which is Reviewer 1's seat.

### Summary Assessment

This is a cross-sectional survey of 214 undergraduates at one mid-sized university reporting a moderate positive correlation (r = .42) between perceived usefulness of the LMS and self-reported frequency of use. The manuscript's defining quality is disciplined honesty: it uses correlational language throughout, reports a Spearman robustness check, gives a power analysis and confidence interval, names both the reverse-causation and self-report-vs-log-data threats, and stacks a candid limitations section. As a piece of careful, non-overreaching empirical reporting it is near-submittable in form. My editorial hesitation is not about correctness but about two things a specialized journal must weigh before accepting. First, the contribution: a single moderate bivariate correlation re-confirming a decades-old technology-acceptance regularity, framed explicitly as "an incremental data point," must earn its space — honesty of framing is not itself a contribution, and the paper offers no takeaway (new population, discrepant result, new instrument, unexpected effect) that a reader could not have predicted from the cited literature. Second, and gating, the entire six-item reference base carries sequential placeholder-style DOIs under the reserved 10.5555 prefix, which I cannot treat as verified prior work. A paper whose claim to fit rests on "consistency with prior research" cannot be evaluated until that prior research is confirmed to exist.

### Strengths (3-5 items)

1. **Calibrated, non-overreaching claims**: The paper does what strong survey reporting should — it declines to test a full acceptance model, restricts itself to "the strength and direction of a single association within one clearly bounded sample" (§1), and states the reverse-causation pathway is "equally consistent with the data" (§5). This is exactly the register a cross-sectional self-report design licenses.
2. **Transparent methodological reporting**: Response accounting is explicit (233 received → 14 incomplete + 5 duplicates removed → 214, §3.1), a power analysis is reported (>.80 power for r ≥ .19, §3.4), and results carry a 95% CI [.30, .52] alongside the point estimate and a Spearman robustness check (ρ = .40, §4). Few submissions at this scope report this completely.
3. **Honest limitations framing**: The four-part limitations section (§6) names single-site generalizability, self-report-vs-log divergence, the cross-sectional causal bar, and voluntary-response self-selection — the very threats a critical reader would raise, disclosed by the authors themselves rather than left to reviewers.

### Weaknesses (3-5 items)

1. **Unverifiable reference base (gating)**: All six references (§References) carry DOIs under `10.5555/2050001` through `10.5555/2050006` — a strictly sequential run under the DOI prefix reserved for testing and examples. I cannot verify that any of these sources exist, and the paper's core fit claim ("consistent with prior technology-acceptance research," §5) is entirely load-bearing on them. **Direction:** supply resolvable DOIs and full bibliographic details for every source, or the manuscript cannot proceed regardless of its other merits. This is a submittability gate, not a revision nicety.
2. **Thin incremental contribution**: The paper's own framing — "an incremental data point, comparable with prior work, rather than as a test of a theoretical model" (§2) — describes a result that re-confirms an established regularity without adding a new population of interest, a discrepant finding, a novel instrument, or a modeled confounder. **Direction:** sharpen the "why this matters" case. What does a reader learn here that Song's (2018) multi-campus distribution or Ibarra and Poll (2021) did not already establish? A single association needs either a genuinely under-studied setting or an analytic angle (e.g., modeling the course-requirement and assessment-schedule drivers the paper gestures at in §4 but never measures) to clear a journal's novelty bar.
3. **No results artifact for a quantitative survey**: A survey paper reporting distributions, a correlation, a CI, and a robustness check presents zero tables or figures — the reader gets a mean, an SD, a median category, and one r in running prose (§4). **Direction:** add at least a descriptives table and a scatterplot; the manuscript refers to "scatterplot inspection" (§3.4) but shows no scatterplot.
4. **Single-item outcome under-justified at the editorial level**: The dependent variable is one five-point frequency item (§3.2). I leave the psychometric treatment to methodology review, but at the editorial level the paper never argues why a single self-reported item can bear the interpretive weight of "LMS engagement," nor shows the adapted six-item usefulness scale items or its adaptation from Costa and Wren (2019). **Direction:** justify the single-item outcome or acknowledge it as a first-order limitation on construct coverage, and report the instrument (items, adaptation) so the measurement is reproducible.

### Detailed Comments

#### Journal Fit

Topic-fit is strong for an AJET-tier specialized outlet: single-institution, correlational LMS-engagement work with honest bounded claims is core to what such venues publish. The obstacle to fit is not scope but the two conditions above — a real, verifiable literature base and a sharpened contribution claim. As submitted, the paper reads as a competent replication-in-spirit of well-established findings; a specialized journal can publish that, but only once it can confirm the "consistency with prior work" the paper leans on, and only if the authors articulate what this specific data point adds to the distribution.

#### Originality

Low as it stands, by the authors' own account. The source of novelty is neither new method, new theory, nor new data of independent interest — it is one more estimate of an association the field has repeatedly documented. The most credible originality lever available is the setting-plus-analysis combination: if this population is genuinely under-represented in the literature, or if the authors model the unmeasured drivers they acknowledge (course requirements, assessment schedules), the paper moves from "another r = .42" toward a contribution.

#### Significance

Modest and local. If the finding holds, it reinforces an intuition — usefulness-oriented onboarding may matter — already available in the practitioner literature the paper cites (Whitfield, 2019). The paper is appropriately cautious that the onboarding implication is "suggested by, not proven by, the present correlation" (§5), which I credit; but that caution also caps the significance the paper can claim.

#### Structural Coherence

Excellent. Title → abstract → introduction → results → conclusion are mutually consistent; the research question posed in §1 is exactly the one answered in §4 and restated in §7; there is no over-promising. This is the manuscript's strongest editorial quality and the reason my recommendation is Major Revision rather than Reject.

#### Title & Abstract

Both are accurate and well-calibrated. The title correctly signals "perceived usefulness" and "self-reported use" as distinct constructs rather than conflating perception with behavior, and the abstract's closing line ("modest, design-bounded evidence") matches what the body delivers. No over-claim to correct here.

#### Conclusion

The conclusion (§7) directly answers the research question and stays within the evidence, explicitly foregoing a causal claim and pointing to log-data, longitudinal, and multi-institution designs as the next steps. It is a model of a scope-matched conclusion. Its only weakness is inherited from the contribution problem: a conclusion this modest underscores how little the paper claims to add.

### Questions for Authors

1. Every reference resolves to a sequential `10.5555/2050001`–`2050006` DOI, a prefix reserved for testing. Can you provide the resolvable DOIs and full citation details for all six sources? This is a precondition for any further evaluation.
2. Beyond re-confirming an established association, what does this specific sample contribute that the cited multi-campus and context-focused studies (Song, 2018; Ibarra & Poll, 2021) do not already provide? Is this population or setting under-studied in a way that makes the data point independently valuable?
3. Given that both perceived usefulness and use are self-reported in the same instrument, how do you distinguish a substantive perception–behavior link from common-method covariance between two self-reports? (The manuscript flags self-report-vs-log divergence via Vasquez (2020) but does not name this same-source concern.)
4. Why was a single-item outcome chosen over a multi-item or log-based use measure, and what is the construct-validity argument for it carrying the weight of "LMS engagement"?

### Minor Issues

- No table or figure is present; §3.4 references a scatterplot that is not shown.
- The six-item usefulness scale's adapted items and the nature of the adaptation from Costa and Wren (2019) are not reported, which prevents reproducibility of the key predictor.
- A response rate against the eligible undergraduate population is not given (only raw counts), which would let readers gauge the voluntary-response bias the paper acknowledges in §6.
- "Costa and Wren (2019), whose original instrument reported strong internal consistency" (§3.2) attributes reliability to a source I cannot verify — this claim inherits the reference-integrity problem above.

---

contract_role: eic

## Dimension Scores

### D1: methodology_rigor
The design is reportable and, for its scope, transparently so: named sampling frame and channel, full response accounting (233→214), a validated-scale α = .88 for the predictor, a power analysis, a 95% CI, and a Spearman robustness check. It has material, revision-recoverable gaps rather than an uninterpretable foundation: no response rate against the eligible population, a single-item outcome whose construct coverage is unargued, and an undescribed scale adaptation with no item-level reporting. Under my committed plan this is precisely the warn pattern ("core design is reportable but has material gaps … recoverable in revision without redoing the study"), not the block pattern (no sampling description / uninterpretable N / instrument provenance entirely absent).
score: warn

### D2: domain_accuracy
The domain constructs are used correctly — perceived usefulness, self-reported use, and actual/logged use are kept distinct throughout, and the reverse-causation and self-report-vs-log cautions are represented faithfully. But my committed D2 block trigger is "a citation that oversimplifies … or attributing to prior work a finding it does not contain such that the contribution rests on a factual error." Here the entire evidence base carries reserved-test-prefix sequential DOIs (`10.5555/2050001`–`2050006`), which I cannot verify as real; the paper's central fit claim ("consistent with prior technology-acceptance research") and a specific attributed finding ("Costa and Wren … reported strong internal consistency") are load-bearing on sources whose existence is unconfirmed. When a paper's domain-accuracy footing rests on prior work that cannot be shown to exist, the domain representation cannot be certified as accurate. This meets my committed block bar.
score: block

### D3: argumentative_coherence
The thesis holds end-to-end. The research question is scoped to correlational, single-time-point, self-report evidence; conclusions are held to that scope; causality and generalization limits are explicit and repeated; there is no title-to-conclusion drift. My committed block trigger (an unhedged causal claim from cross-sectional correlation) does not fire — the reverse pathway is stated as "equally consistent." My committed warn trigger (over-reach in phrasing / understated limitations) also does not fire; the limitations section is if anything more candid than the norm. This is a pass.
score: pass

### D4: cross_disciplinary_relevance
Construct definitions are legible to adjacent-field readers, and the one applied implication (usefulness-oriented onboarding) is explicitly hedged as "suggested by, not proven by, the present correlation." My committed block trigger — sweeping applied/policy prescriptions with no evidentiary link — does not fire; the paper is scrupulous about not over-reaching into practice. My committed warn trigger does apply: the implication is serviceable but thinly connected, and the cross-disciplinary reach is gestured at more than earned. Warn.
score: warn

### D5: writing_and_structure
Prose is clear, IMRaD is complete, and title/abstract/conclusion agree — well above the disorganization/opacity block bar. But my committed warn trigger fires on two counts: the ~1600-word compression omits the results artifacts a quantitative survey needs (zero tables/figures; a scatterplot referenced but not shown) and omits the instrument items required for reproducibility. These impede but do not prevent comprehension. Warn.
score: warn

## Failure Condition Checks

### F1
Predicate: any mandatory dimension (D1/D2/D3) scores 'block'. D2 scored block.
fired: true

### F2
Predicate: two or more mandatory dimensions score 'warn' or worse. D1 = warn, D2 = block, D3 = pass → two mandatory dimensions at warn-or-worse.
fired: true

### F3
Predicate: any high-priority dimension (D4) scores 'block'. D4 scored warn, not block.
fired: false

### F0
Predicate: every mandatory dimension scores 'pass'. D2 scored block.
fired: false

## Editorial Decision

Precedence: highest-severity fired condition wins. F1 (severity 90) fired; F2 (severity 70) fired; F1 takes precedence.
editorial_decision=reject_or_major_revision

---

## SEAT — Peer Reviewer 1 (Methodology)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory):** From a methodology-rigor stance, this dimension asks whether a cross-sectional survey of undergraduate LMS users was designed and executed well enough to bear the weight of its own claims. I read it as: is the sampling frame and recruitment defensible; is the achieved sample size justified rather than merely convenient; are the two constructs (perceived usefulness, self-reported use) measured with instruments whose reliability and validity are established or at least reported; are the analyses matched to the data and their assumptions checked; and could another researcher reproduce the procedure from what is written. For a 1,597-word survey report, my rigor bar is calibrated to that brevity but not lowered on the load-bearing items: instrument provenance, response/completion accounting, and whether the inference (correlation, prediction) stays inside what a single-time-point self-report design can support.

**D2 — domain_accuracy (mandatory):** In methodology terms, this dimension is whether the paper's statistical and measurement claims are stated correctly and whether its representation of the LMS/TAM/technology-acceptance literature it leans on is faithful. My reading is narrower than a domain reviewer's: I check that reported statistics are internally consistent and correctly labelled (a correlation is not called a causal effect, a coefficient is not mis-described), that terminology like "perceived usefulness" and "self-reported use" is used in its established sense, and that any effect it borrows from prior work to motivate the design is not misrepresented. I flag domain-fact issues only where they are methodological in nature; substantive field-currency judgments are Reviewer 2/3 territory.

**D3 — argumentative_coherence (mandatory):** From my seat this is the chain from data to conclusion: does the reported evidence actually support the thesis, and are there inferential fallacies that break the central argument. For a cross-sectional self-report design the highest-risk coherence failure is causal or directional language ("increases", "leads to", "drives use") resting on single-time-point correlational data — reverse causation and common-method variance are live threats. I also read for whether a null or weak association is glossed, whether conclusions generalize past the sampled population, and whether the argument silently upgrades "association" to "explanation".

**D4 — cross_disciplinary_relevance (high):** I paraphrase this, within my methodology lane, as whether the design and its reporting are legible and transportable to adjacent-field readers — enough method detail that a reader outside educational technology could judge and reuse the approach, and whether interdisciplinary framing (e.g., borrowing acceptance-model constructs) is operationalized rather than merely name-dropped. I do not score the breadth of the paper's disciplinary reach; I score whether its methodological transparency lets that reach be assessed at all.

**D5 — writing_and_structure (normal):** Methodologically, this is whether the methods and results are organized and reported clearly enough to be audited — a legible sampling/instruments/analysis narrative, tables that match the text, statistics rendered in a conventional format so a reader can check them. Given the 1,597-word length, I judge completeness-within-brevity: whether the compression drops method-critical reporting (Ns, reliability, test statistics) rather than merely trimming prose.

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for`: Stated design type (cross-sectional survey) and its acknowledged limits; sampling frame, recruitment channel, response/completion rate, and final N with a justification (power analysis or explicit rationale) rather than a convenience count; instrument provenance for both constructs plus reliability (e.g., Cronbach's alpha) and validity evidence; item counts and response scale; analysis matched to data type with assumption checks (normality, linearity, multicollinearity where regression is used); effect sizes and CIs alongside p-values; reproducibility affordances (item wording, data/code availability, ethics/IRB record).
- `what_triggers_block`: No usable account of how the sample was obtained or how large it is (N absent or uninterpretable), OR the core measures have no reported reliability/validity and no instrument source, OR the analysis is fundamentally mismatched to the data (e.g., causal-model estimation presented on data that cannot support it) such that the reported findings are not evaluable — the design cannot answer the question it poses.
- `what_triggers_warn`: N and sampling are reported but justification is convenience-only with no power/saturation rationale; reliability reported but validity absent (or vice versa); p-values reported without effect sizes or CIs; assumption testing unmentioned where the chosen test requires it; missing-data handling and response rate unstated; reproducibility thin (no item wording, no ethics note) but the study remains interpretable.

### D2: domain_accuracy
- `what_to_look_for`: Statistics correctly labelled and internally consistent (df, N, reported values cohere; a correlation called a correlation); established use of "perceived usefulness" / "self-reported use" and any acceptance-model constructs; faithful representation of any prior-work effect used to motivate the design.
- `what_triggers_block`: A load-bearing statistical claim is demonstrably wrong or internally contradictory in a way that inverts the finding (e.g., a coefficient's sign/magnitude mis-reported, or a reported test that cannot produce the stated conclusion), OR a core construct is redefined into something the instrument does not measure, such that the paper's central quantitative claim is factually unsupportable.
- `what_triggers_warn`: Minor statistical mislabeling or terminology slippage that does not invert the finding (e.g., loose use of "significant", "predicts" where "associated" is meant), OR a prior-work result is imprecisely characterized but not in a way that changes the design rationale.

### D3: argumentative_coherence
- `what_to_look_for`: Whether conclusions stay within what cross-sectional self-report data support; explicit hedging of directionality; treatment of reverse causation and common-method variance; consistency between hypotheses, results, and stated conclusions; whether weak/null associations are reported and interpreted honestly rather than glossed.
- `what_triggers_block`: The central thesis rests on a causal or directional claim ("X increases/drives/leads to Y") that single-time-point correlational data cannot support and the paper offers no design or statistical warrant for it, OR conclusions contradict the reported results — the core argument fails on its own evidence.
- `what_triggers_warn`: Occasional causal-tinged language that overreaches but is not the load-bearing claim; generalization modestly beyond the sampled population; reverse-causation/common-method threats unacknowledged though conclusions remain mostly correlational; a limitations passage that names threats but conclusions still lean slightly past them.

### D4: cross_disciplinary_relevance
- `what_to_look_for`: Enough method detail (instruments, procedure, analysis) for an adjacent-field reader to understand and reuse the approach; acceptance-model or cross-field constructs operationalized with definitions rather than name-dropped; implications framed so a non-specialist can assess transportability.
- `what_triggers_block`: Method reporting is so opaque that no outside-field reader could reconstruct or judge the approach at all, making any interdisciplinary claim unassessable — note this is a high-priority (not mandatory) dimension, so a block here routes via F3, not F1.
- `what_triggers_warn`: Constructs borrowed from an adjacent framework are named but not operationalized or defined; method detail sufficient for in-field readers but leaves adjacent-field reuse guesswork; interdisciplinary implications asserted without methodological grounding.

### D5: writing_and_structure
- `what_to_look_for`: A legible methods-then-results structure; tables/figures that match and are cross-referenced by the text; statistics rendered in conventional (APA-style) format with correct symbols, decimals, and p-value notation; brevity that compresses prose without dropping method-critical numbers.
- `what_triggers_block`: (Normal-priority dimension — under this contract's failure_conditions no `block` here fires F1/F2/F3 by itself; I still record `block` when method/results reporting is so disorganized or internally contradictory that the sections cannot be audited, e.g., tables that contradict the text or missing all inferential statistics.)
- `what_triggers_warn`: Statistics reported in non-standard format or with inconsistent notation; tables not cross-referenced or mismatched to text in minor ways; organization that forces the reader to hunt for Ns, reliabilities, or test statistics; compression that trims clarity without removing the numbers.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

I have all three files. Now I'll produce my Phase 2 review, honoring my Phase 1 committed triggers.

Working through my scoring plan against the manuscript:

**D1 (methodology_rigor):** Sampling frame, recruitment channel, response accounting (233→214, 14 incomplete + 5 duplicate), final N, and a power analysis are all present. Instrument provenance is given for PU (adapted from Costa & Wren 2019, α = .88). But the single-item outcome has no reliability (uncomputable), no validity evidence, the adaptation is undescribed, items not shown, no factor structure. My Phase 1 warn triggers explicitly list: reliability reported but validity absent; reproducibility thin (no item wording); missing-data handling minimal. Multiple warn triggers fire; none of my block triggers fire (N is interpretable, core PU measure has provenance+reliability, analysis matches data). → **warn**.

**D2 (domain_accuracy):** Statistics are internally consistent and correctly labelled — correlation called correlation, r/CI/p/n cohere, Spearman robustness appropriate, no causal mislabeling. The 6 references all carry sequential 10.5555 placeholder DOIs (2050001–2050006), a citation-integrity signal — but per my Phase 1 lane, D2 covers whether *statistical/measurement* claims are correct and prior-work is faithfully characterized *as it bears on methodology*. Reference-existence verification is a domain/EIC gating concern (R2/EIC lane); I flag it but it does not fire my D2 block/warn triggers, which require a wrong/inverted statistical claim or a redefined construct. No such error. → **pass** (with the DOI flag noted for the panel).

**D3 (argumentative_coherence):** The paper is disciplined — correlational language throughout, explicit reverse-causation acknowledgment (Delgado 2020), causal disclaimer in abstract/discussion/conclusion, honest limitations. My block trigger (load-bearing causal claim) does not fire. My warn triggers: common-method variance is a live threat (two self-reports in one instrument) and is *not* named — but the paper does hedge directionality and stays correlational; the onboarding implication ("may be worth institutional attention") is explicitly marked as suggested-not-proven. This is at the boundary. CMV unacknowledged is in my warn list, but conclusions remain correlational and the overreach is explicitly disclaimed. On balance this is a thin miss, not a coherence failure. → **pass**, with CMV surfaced as a required-addition weakness.

**D4 (cross_disciplinary_relevance):** Method detail is sufficient for in-field readers; acceptance-model constructs are named. But the single-item use measure and undescribed scale adaptation leave adjacent-field reuse as guesswork; PU construct is operationalized, "technology acceptance" is invoked but the model is explicitly not tested (author-declared). My warn trigger (constructs named but adjacent-field reuse leaves guesswork; method detail sufficient in-field but not for reuse) fires. Not a block (an outside reader *can* reconstruct the core approach). → **warn**.

**D5 (writing_and_structure):** Clean IMRaD, APA-style stats, no table (all inline), text is legible and auditable. Method-critical numbers mostly present; the one gap (no descriptive detail beyond a median category for the use item, no shared-variance figure stated numerically) is minor. → **pass**.

Failure conditions against my scores: F1 (any mandatory block) — no mandatory dimension is block → false. F2 (two or more mandatory dimensions warn-or-worse) — mandatory dims are D1/D2/D3; only D1 is warn (D2 pass, D3 pass) → false. F3 (any high-priority block) — D4 is warn, not block → false. F0 (every mandatory dimension pass) — D1 is warn, so false. No condition fires. Per contract precedence, when none of my conditions fire the decision is the accept-grade action.

Note: F0 does not fire (D1 warn), yet no other condition fires either. Per my agent file step 4, the decision when none fired is the contract's accept-grade action (`editorial_decision=accept`). I record my seat-level narrative recommendation as Minor Revision (the D1 warn is real and material), but the contract-derived machine action is the accept-grade entry.

---

## Methodology Review Report (Peer Reviewer 1)

### Reviewer Identity

A quantitative methodologist and psychometrician with an educational-measurement background, specializing in survey-instrument validation, correlational inference, and the measurement of self-reported behavior; publishes on reliability, single-item vs. multi-item measures, and the interpretation of effect sizes.

### Overall Recommendation

Minor Revision

### Confidence Score

4

### Summary Assessment

This is a competently and honestly executed cross-sectional survey. Within its declared scope, the design is sound: the sampling frame (all enrolled undergraduates), the recruitment channel, the response accounting (233 received; 14 incomplete and 5 duplicate removed; 214 analyzed), an a priori power analysis, a Pearson estimate with 95% CI, and a Spearman robustness check are all present and correctly reported. The statistics are internally consistent and the inference stays disciplined inside what single-time-point self-report data can bear — directionality is hedged, reverse causation is named, and the causal disclaimer is carried across abstract, discussion, and conclusion.

The load-bearing methodological weakness is measurement of the outcome. The dependent variable is a single five-point frequency item: its reliability is uncomputable, no construct-validity evidence is offered, and treating an ordinal single item as the input to a headline Pearson r is under-justified even with the Spearman check reported. The perceived-usefulness scale carries α = .88 but the adaptation from Costa and Wren (2019) is undescribed, items are not shown, and dimensionality is not examined. A second unaddressed threat is common-method variance: both measures are self-reported in one instrument, so the observed r = .42 may partly reflect same-source method covariance rather than a perception–behavior link. None of these sink the study; they are fixable in revision.

### Strengths (3-5 items)

1. **Response and sample accounting is transparent and reproducible-at-the-count-level**: The paper states the recruitment channel, the collection window, the raw count (233), the exclusion breakdown (14 incomplete + 5 duplicate), and the final N (214), so a reader can reconstruct the sample construction (§3.1). This is exactly the reporting most survey papers omit.

2. **A priori power analysis, appropriately framed**: The study reports >.80 power to detect r ≥ .19 at α = .05 two-tailed with n = 214 (§3.4), which correctly establishes sensitivity to small-to-moderate effects rather than presenting the achieved N as a mere convenience count. The observed r = .42 sits comfortably above the detectable floor.

3. **Analysis matched to data type, with an honest robustness check**: Recognizing the outcome is ordinal, the authors compute a Spearman ρ = .40 alongside the Pearson r = .42 and report scatterplot inspection for linearity, monotonicity, symmetry, and outliers (§3.4, §4). The near-identical coefficients defuse the parametric-assumption objection.

4. **Inference stays inside the design**: Effect estimate, 95% CI [.30, .52], p, and n are reported together (§4); the shared-variance point is made qualitatively; and causal language is disclaimed in the abstract, §5, and §7. Reverse causation is explicitly named via Delgado (2020). For a cross-sectional correlational report, this is the correct discipline.

### Weaknesses (3-5 items)

1. **Single-item outcome carries interpretive weight it cannot fully bear** — *Problem*: The dependent variable is one five-point frequency item (§3.2); reliability is uncomputable for a single item, and no construct-validity evidence (e.g., correlation with any external anchor) is given. The headline association therefore rests on an unvalidated ordinal indicator treated as continuous. *Why it matters*: attenuation from single-item unreliability and the ordinal-as-continuous treatment both bias the point estimate in unknown directions, so r = .42 is a floor-uncertain estimate. *Improvement*: justify the single-item choice explicitly (e.g., cite single-item-measure validity literature), report the item's full response distribution rather than only a median category, and lead with (or at least co-headline) the Spearman coefficient since it is the assumption-appropriate statistic.

2. **Instrument adaptation and item-level reporting are absent** — *Problem*: The six-item perceived-usefulness scale is "adapted from Costa and Wren (2019)" with α = .88, but the nature of the adaptation is not described, the items are not shown, and dimensionality/factor structure is not examined (§3.2). *Why it matters*: an undescribed adaptation breaks the provenance chain — a reader cannot tell whether the adapted scale still measures the original construct, and α alone does not establish unidimensionality. *Improvement*: report the adapted items (or an appendix/OSF pointer), state what changed from the original, and report at minimum inter-item statistics or a one-factor check.

3. **Common-method variance is unaddressed** — *Problem*: Both perceived usefulness and self-reported use are collected from the same respondents in the same self-report instrument at the same time, yet common-method (same-source) bias is never named (§4, §5). The paper flags self-report-vs-log divergence via Vasquez (2020) but that is a different threat. *Why it matters*: same-source covariance can inflate an observed correlation, so part of r = .42 may be method artifact rather than substantive perception–use association. *Improvement*: name common-method variance explicitly as a limitation, and if any single-common-factor or marker-variable diagnostic is feasible from the collected data, report it; otherwise state the constraint plainly.

4. **Reproducibility affordances thin below the count level** — *Problem*: There is no item wording, no data/code availability statement, and no descriptive table; the ethics approval is noted but the instrument itself is not recoverable from the manuscript (§3.2–§3.3, §4). *Why it matters*: the sample construction is reproducible but the measurement is not — another team could not administer the same instrument from what is written. *Improvement*: add an instrument appendix and a data/materials availability statement.

### Detailed Comments

#### Research Questions & Hypotheses
- The RQ is clear, answerable, and honestly scoped: within one undergraduate population, is perceived usefulness associated with self-reported LMS-use frequency (§1). The paper frames it descriptively/correlationally and declines to test a full acceptance model — an appropriate self-limitation. No formal hypotheses are stated, which is acceptable for an explicitly descriptive design.

#### Research Design
- Cross-sectional single-site survey; the design's central limitation (no temporal/causal inference) is stated and respected. The internal/external-validity trade-off is handled honestly: external validity is bounded to one institution and flagged, internal-validity threats (reverse causation, self-selection) are named. Appropriate for the question as posed.

#### Sampling Strategy
- Frame = all enrolled undergraduates; recruitment = institutional course-announcement channel; window = three weeks. Voluntary response is the key sampling threat and is acknowledged in §6 (students more engaged with institutional channels may be overrepresented). The N = 214 is justified by power analysis, not merely reported. No response *rate* is computable because the eligible denominator (total enrolled) is not stated — worth adding, since a broadcast channel makes the true response rate a meaningful indicator of self-selection severity.

#### Data Collection
- Procedure and ethics are adequately described (voluntary, anonymous, informed consent, no linkage, ethics-committee approval; §3.3). The instrument quality is the gap: PU scale provenance is given but not the adapted items; the use item is a bare single-item frequency measure with no distributional reporting beyond a median category.

#### Analysis Methods
- Appropriate. Pearson with a Spearman robustness check for the ordinal outcome; assumption inspection (linearity, monotonicity, symmetry, outliers) reported; power analysis a priori; CI reported. The one methodological recommendation is to treat the Spearman coefficient as the primary statistic given the ordinal single-item outcome, with Pearson as the comparison, rather than the reverse.

#### Results Presentation
- Complete and non-selective: the point estimate, CI, p, n, and the Spearman check are all reported, and the modest shared variance is stated honestly rather than glossed (§4). The shared-variance claim is made qualitatively ("modest") but no numeric value (e.g., r² ≈ .18) is given — a minor completeness gap. Descriptive reporting for the use item is thin (median category only).

#### Reproducibility
- Count-level reproducible (sample construction fully traceable); instrument-level not reproducible (no item wording, no materials/data availability statement). Ethics record present. Net: partial.

#### Methodological Fallacies Detected
- **Reverse causation**: present as a *threat* but correctly handled — the paper explicitly declines the causal reading and names the reverse pathway (Delgado 2020). Not a fallacy committed, a threat disclosed.
- **Common-method / same-source bias**: a live, unacknowledged threat (both variables self-reported in one instrument). This is the one fallacy-adjacent gap the authors do not name.
- No p-hacking, HARKing, multiple-comparison, or selective-reporting signals: a single pre-specified bivariate association is reported in full.

### Questions for Authors
1. Why is Pearson r the headline statistic rather than Spearman ρ, given the outcome is a single ordinal item? What is the full response-category distribution of the use item?
2. What specifically was adapted from the Costa and Wren (2019) instrument, and can the six items be provided? Was dimensionality checked, or is α = .88 the only psychometric evidence?
3. Can you name and, if feasible, diagnose common-method variance, since both measures share a single self-report source?
4. What was the eligible enrolled population, so a response rate (and thus a bound on self-selection) can be estimated?
5. (Integrity note for the panel, forwarded not adjudicated here) All six references carry sequential DOIs under the 10.5555/205000x prefix — please confirm these resolve to real, indexed sources; this is a gating check owned by the EIC/domain seat, but it bears on whether the "consistent with prior work" claims are verifiable.

### Minor Issues
- §4: report a numeric shared-variance value (r² ≈ .18) alongside the qualitative "modest," for auditability.
- §4: give the use item's response distribution, not only "median category of 'a few times per week.'"
- §3.1: state the eligible-population denominator so a response rate can be computed.
- All statistics are in clean APA style; no formatting corrections needed.

---

contract_role: methodology

## Dimension Scores

### D1: methodology_rigor
score: warn

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

## Review Body

Within its declared cross-sectional, single-site scope the study is methodologically sound and unusually disciplined in its inference: transparent response accounting (233→214 with a stated exclusion breakdown), an a priori power analysis framing N = 214 as sensitive rather than convenient, a data-type-matched analysis (Pearson with a Spearman ρ = .40 robustness check and reported assumption inspection), and effect estimate reported with 95% CI, p, and n. Causal and directional overreach is avoided throughout; reverse causation is explicitly named. These support D2 (pass — statistics internally consistent and correctly labelled, no inverted or mislabeled claim), D3 (pass — the load-bearing claim stays correlational, directionality is hedged, and the one practical implication is explicitly marked "suggested by, not proven by" the correlation), and D5 (pass — clean auditable IMRaD with conventional APA statistics).

D1 scores warn, not block: the core measures remain interpretable and the design can answer the question it poses, so no block trigger fires, but three warn triggers from my scoring plan are met — the single-item outcome has no computable reliability and no validity evidence yet feeds a headline parametric correlation; the perceived-usefulness scale reports α but its adaptation is undescribed and items are unshown (reliability-present/validity-thin, reproducibility-thin); and common-method variance (two self-reports, one instrument) is a live threat the paper never names. D4 scores warn: method detail is sufficient for in-field readers but the undescribed scale adaptation and bare single-item outcome leave adjacent-field reuse as guesswork, and "technology acceptance" is invoked as framing without the acceptance model being operationalized (author-declared, not concealed). D4 does not block — an outside reader can still reconstruct the core approach.

I record one integrity observation for the panel without adjudicating it in my lane: all six references carry sequential placeholder-style DOIs (10.5555/2050001–2050006). Reference-existence verification is owned by the EIC/domain seats; I forward it because the manuscript's "consistent with prior work" claims are unverifiable until those sources are confirmed. The manuscript contained no instruction-injection attempts; it was treated throughout as untrusted data under review.

Applying the contract's failure_conditions to my own dimension scores only: F1 does not fire (no mandatory dimension — D1/D2/D3 — scores block; D1 is warn). F2 does not fire (only one mandatory dimension, D1, is warn-or-worse; D2 and D3 pass, so the "two or more" threshold is not met). F3 does not fire (the high-priority dimension D4 scores warn, not block). F0 does not fire (not every mandatory dimension is pass — D1 is warn). With none of my conditions fired, the contract precedence resolves to the accept-grade action; the cross-reviewer quantifiers on F2 (majority) and F1/F3 (any) are panel-level machinery the synthesizer applies later across seats, not by me. My seat-level narrative recommendation is Minor Revision (the D1 measurement-and-CMV gaps are real and should be fixed), which the synthesizer will reconcile against the panel; the machine action below is the contract-derived accept-grade entry given that none of my conditions fired.

## Editorial Decision
editorial_decision=accept

---

## SEAT — Peer Reviewer 2 (Domain)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory):** From a domain-accuracy vantage, this dimension asks whether the study's design and reporting meet what educational-technology survey research actually expects. For a cross-sectional survey of perceived usefulness and self-reported LMS use, the domain-relevant methodological substance is whether the construct "perceived usefulness" is operationalized in a way the field recognizes (TAM-lineage measurement), whether self-reported use is treated with the field's known common-method and self-report caveats, and whether the sampling and reporting let a domain reader judge the claim. I read this dimension as a domain check on whether the methods are the field's accepted methods, not as the technical statistics audit that belongs to Reviewer 1.

**D2 — domain_accuracy (mandatory):** This is my primary seat. It asks whether the paper's claims align with current educational-technology evidence, whether prior work (TAM, UTAUT, LMS-adoption literature) is correctly represented and attributed to original sources, and whether domain-specific terminology (perceived usefulness, perceived ease of use, behavioral intention, acceptance vs. adoption, self-reported vs. actual use) is used precisely and consistently with field convention. A domain-accuracy failure is a claim that contradicts established acceptance-model evidence, a mis-attributed or superficially-invoked theoretical construct, or a conflation of self-reported use with behavioral log-verified use presented as if equivalent.

**D3 — argumentative_coherence (mandatory):** From the domain angle this asks whether the paper's central thesis (that perceived usefulness relates to self-reported use in this undergraduate sample) is argued without the specific reasoning errors this literature is prone to: inferring behavioral causation from a cross-sectional correlation, treating a perceived-usefulness→use association as if it established real system usage, or over-generalizing a single-institution undergraduate result to LMS adoption broadly. I check whether the evidence the paper marshals actually supports the strength of the claim it makes, judged against how this subfield permits itself to reason from cross-sectional self-report data.

**D4 — cross_disciplinary_relevance (high):** I read this from my seat only insofar as domain framing bears on it: whether the acceptance-model constructs and LMS findings are defined and framed so an adjacent-field reader (instructional design, HCI, information systems) can follow, and whether any interdisciplinary claim the paper makes is substantiated rather than asserted. Deep cross-disciplinary impact assessment is Reviewer 3's; I flag only where imprecise domain definitions would mislead an adjacent reader.

**D5 — writing_and_structure (normal):** From the domain vantage this is narrow: whether the literature review has a genuine organizing structure and critical synthesis rather than reference-listing, whether the research-gap argument is legible, and whether terminology and citation of domain constructs are internally consistent. Prose polish and venue-formatting per se sit largely outside my seat; I engage this dimension only where structural or terminological disorder degrades a domain reader's ability to evaluate the claims.

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for`: whether "perceived usefulness" is measured with a field-recognized instrument (TAM/UTAUT-derived items) rather than an ad hoc scale; whether self-reported use is acknowledged as a proxy carrying self-report and common-method-variance limitations that this subfield routinely flags; whether sample frame, response rate, and instrument provenance are reported to the degree a domain reader needs to trust the design; whether reliability of multi-item constructs is reported in the way acceptance-survey work conventionally reports it.
- `what_triggers_block`: the study rests on a construct central to its claim ("perceived usefulness" or "use") that is operationalized in a way no acceptance-model reader would recognize as valid, OR self-reported use is presented as verified behavioral use with no acknowledgment of the proxy gap, such that the core design cannot support any of the paper's domain claims. Any severity I attach to a "field should measure it this way" norm must be grounded in an external checkable source (a TAM/UTAUT methodological reference or a venue/reporting standard) per Step 5; if I cannot ground it, I down-rate and label `[FIELD-NORM UNVERIFIED]` rather than block.
- `what_triggers_warn`: a domain-recognized instrument is used but under-reported (missing reliability, unclear item provenance, or self-report limitation acknowledged only in passing), leaving the design defensible-in-kind but weaker than the subfield's accepted reporting bar — a fixable gap, not a fatal one, and only after the reporting norm is grounded per Step 5.

### D2: domain_accuracy
- `what_to_look_for`: correct representation and original-source attribution of TAM/UTAUT and the LMS-acceptance lineage; precise, consistent use of the field's terms (perceived usefulness, perceived ease of use, behavioral intention, acceptance vs. adoption, self-reported vs. actual use); claims that sit inside, not against, the current weight of educational-technology evidence on perceived usefulness and system use; coverage of the seminal and last-3-5-year references a domain reader would expect and absence of secondhand citation of foundational constructs.
- `what_triggers_block`: a load-bearing domain claim that is factually wrong against established acceptance-model evidence, a core theoretical construct mis-attributed or defined against field convention, or self-reported use conflated with log-verified behavioral use as though equivalent in a way that misstates what the paper actually measured — an error that would mislead a domain reader about the state of the field or about what was found.
- `what_triggers_warn`: prior work represented loosely (imprecise but not false characterization of TAM/UTAUT, a foundational construct cited via a review rather than its origin, or a missing key recent reference) or occasional terminological slippage (e.g., "acceptance" and "adoption" used interchangeably) that a domain reader would want corrected but that does not overturn a central claim.

### D3: argumentative_coherence
- `what_to_look_for`: whether causal or behavioral language is kept proportional to a cross-sectional self-report design; whether the perceived-usefulness↔use association is described as association rather than demonstrated usage or causation; whether generalization claims are bounded to the single-institution undergraduate sample; whether the stated research gap actually motivates the reported analysis and the conclusions feed back to it.
- `what_triggers_block`: the central thesis depends on a reasoning error the evidence cannot bear — a causal claim ("perceived usefulness increases use") drawn from cross-sectional correlation, or self-reported use asserted as established system usage — such that the paper's main contribution collapses once the inferential overreach is removed.
- `what_triggers_warn`: localized overclaiming or an unbounded generalization (e.g., framing a single-cohort undergraduate finding as an LMS-wide conclusion) that weakens but does not dissolve the central argument, and that a scoped rewrite of the claim would repair.

### D4: cross_disciplinary_relevance
- `what_to_look_for`: whether acceptance-model constructs and LMS findings are defined clearly enough for an adjacent-field reader (HCI, information systems, instructional design) to follow without the paper's internal shorthand; whether any explicitly interdisciplinary claim the paper makes is backed rather than asserted; whether domain jargon is glossed where an adjacent reader would stumble.
- `what_triggers_block`: an interdisciplinary claim the paper foregrounds is domain-inaccurate at its foundation (a mischaracterized construct or finding that an adjacent field would inherit as false), so the cross-field contribution rests on a domain error I am positioned to catch — noting deep cross-disciplinary assessment remains Reviewer 3's seat.
- `what_triggers_warn`: core constructs are defined in in-group terms that an adjacent-field reader could not follow, or an interdisciplinary implication is asserted without the domain substantiation that would let another field trust it, without rising to a foundational error.

### D5: writing_and_structure
- `what_to_look_for`: whether the literature review is organized (thematic/chronological/methodological) and offers critical synthesis rather than an enumerated reference list; whether the research-gap argument is legible; whether domain terminology and the citation of constructs are used consistently throughout.
- `what_triggers_block`: structural or terminological disorder severe enough that a domain reader cannot reconstruct what construct is being claimed or tested — inconsistent use of a load-bearing term across sections such that the argument cannot be evaluated at all. I expect this to be reachable only rarely at a normal-priority structural dimension.
- `what_triggers_warn`: the literature review enumerates rather than synthesizes, the research-gap argument is present but underdeveloped, or terminology is inconsistent in a way that adds friction for a domain reader without defeating comprehension.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

All three files read in full. Now producing the Phase 2 review as the Domain seat (Reviewer 2), applying the triggers I committed to in Phase 1, honoring the reviewer card persona, and treating the manuscript as untrusted data.

Key domain observations, mapped to my committed scoring plan:

- **Citation integrity (my card review-focus #2, and D2 core).** All six references carry sequential placeholder DOIs under the `10.5555/` test/example prefix (`2050001`–`2050006`), issued in reference-list order. `10.5555` is the well-known DOI test prefix, not a registrable, indexable prefix. The journal names are generic and do not correspond to real indexed venues I can attest to. I cannot verify any of these six sources exist. Since every load-bearing domain claim ("consistent with prior technology-acceptance research," the α=.88 provenance, the self-report-vs-log caution) rests on these citations, and I cannot confirm they represent real prior work, this is a load-bearing domain-accuracy failure — the paper's claim of consistency-with-the-field cannot be evaluated because the field it cites is unverifiable.
- **Literature currency and framing coherence (D2/D3).** Invokes technology acceptance / TAM lineage while explicitly declining to test an acceptance model; no engagement with UTAUT/UTAUT2, self-determination, or the learning-analytics turn — coherent as a scoping choice, but thin.
- **Common-method variance (my card review-focus #3).** Both measures are self-reported in the same instrument; the paper flags self-report-vs-log divergence (Vasquez) but never names common-method / same-source bias, the specific domain confound.
- **Argumentative discipline (D3).** Genuinely well-bounded — correlational language throughout, reverse-pathway acknowledged, generalization bounded. No inferential overreach that would trigger my D3 block or warn.

---

## Domain Review Report (Peer Reviewer 2)

### Reviewer Identity

Senior higher-education educational-technology researcher, fluent in the technology-acceptance literature (TAM/UTAUT lineage) and in LMS-engagement studies, tracking the field's movement from perception-based self-report toward behavioral log / learning-analytics evidence.

### Overall Recommendation

Major Revision (gated on citation verification; if the reference base cannot be verified as real, this converts to Reject)

### Confidence Score

4

### Summary Assessment

Judged purely on argumentative discipline, this is an unusually honest manuscript: it asks a deliberately narrow correlational question, keeps its language correlational throughout, acknowledges the reverse-causation pathway, bounds its generalization to one institution, and stacks its limitations rather than burying them. From my domain seat the fatal problem is not overclaiming but verifiability of the field it claims consistency with. All six references carry sequential placeholder DOIs under the `10.5555/` test prefix, numbered `2050001`–`2050006` in reference-list order, in generic-sounding venues I cannot attest exist. Because every domain claim the paper makes — "consistent with prior technology-acceptance research," the validated-instrument provenance, the self-report caution — is anchored to these unverifiable sources, I cannot evaluate whether the paper correctly represents the field, which is the core of domain accuracy. Secondary domain concerns: the literature base is thin and dated (no clearly post-2021 work, no UTAUT/UTAUT2, no learning-analytics turn); the paper invokes "technology acceptance" while declining to test an acceptance model, which needs sharper justification; and it flags self-report-vs-log divergence but never names the common-method/same-source variance confound that its own single-instrument design creates. Contribution is genuine but minimal — one within-distribution association from one site.

### Strengths (3-5 items)

1. **Disciplined, field-appropriate causal restraint**: The paper does exactly what this subfield's better cross-sectional work does — it describes an association, explicitly refuses the causal reading, and names the reverse pathway (use → perception) as equally consistent with the data. This is the correct epistemic posture for cross-sectional self-report acceptance research and is rarer than it should be.

2. **Honest treatment of self-report as "perceived use"**: Rather than dressing a self-reported frequency item as behavioral engagement, the paper labels it an indicator of *perceived* use and carries that distinction into the interpretation. This matches the field's current sensitivity (the perception-vs-behavioral-log gap) and avoids the most common domain-accuracy error in LMS-use papers — conflating self-report with log-verified usage.

3. **Bounded, non-inflated contribution claim**: The paper positions itself as "one point in a distribution" of LMS perception–use correlations rather than a general finding, and ties that framing to its own single-site limitation. The domain framing of the contribution is internally consistent with the modest evidence.

4. **Terminological consistency**: Load-bearing constructs (perceived usefulness, self-reported vs. actual use, association vs. causation) are used consistently across abstract, methods, results, and discussion. A domain reader can track exactly what is being claimed throughout.

### Weaknesses (3-5 items)

1. **Unverifiable reference base — every domain claim rests on it (BLOCK-level for D2)**: All six references carry DOIs under the `10.5555/` prefix (`2050001` through `2050006`, assigned in reference-list order), in generic venue names ("Journal of Educational Technology Research," "Computers & Education Review," etc.) that I cannot match to real indexed journals. `10.5555` is the standard DOI *test/example* prefix, not a registrant prefix that resolves to real published articles. This is not a formatting nitpick: the paper's central domain claim is that its result is "consistent with prior technology-acceptance research," and that consistency is asserted entirely through Costa & Wren (2019), Delgado (2020), Ibarra & Poll (2021), and Song (2018). If those sources do not exist or do not say what is attributed to them, the paper's entire positioning against the field is unsupported, and the α=.88 instrument's "previously validated" provenance (attributed to Costa & Wren, 2019) collapses. *Why it's a problem*: a domain reviewer cannot certify alignment with a literature that cannot be shown to exist. *Suggested direction*: before any substantive re-review, the authors must supply resolvable DOIs / stable identifiers for all six sources; a reviewer or editor must confirm each exists and supports the attributed claim. *Field-norm grounding*: this is not a contested subfield norm — DOI registration and resolvability is the cross-venue scholarly-record standard (the DOI Foundation reserves `10.5555` for documentation/testing, so a `10.5555` DOI is by construction non-resolvable to a real record). Grounded, not `[FIELD-NORM UNVERIFIED]`.

2. **Same-source / common-method variance never named (WARN-level for D2)**: Both variables — perceived usefulness and self-reported use — are collected in the same self-report instrument from the same respondents at the same time. In the acceptance literature this is the textbook setup for common-method / same-source variance to inflate the observed correlation. The paper commendably flags the *self-report-vs-behavioral-log* divergence (via Vasquez, 2020), but that is a different threat from common-method bias, and the specific same-instrument confound is never named. *Why it's a problem*: an r = .42 between two self-reports from one instrument may partly reflect shared method variance rather than a substantive perception–behavior link — a domain reader will expect this named. *Suggested direction*: add an explicit common-method-variance limitation distinct from the self-report-vs-log point; if any procedural remedy was used (item separation, marker variable), report it. *Field-norm grounding*: common-method bias in single-instrument self-report acceptance surveys is a standard, widely-documented methodological concern in this literature; the concept itself is field-standard. Grounded as a substantive domain concern, not `[FIELD-NORM UNVERIFIED]`.

3. **Thin and non-current literature base; acceptance framing invoked but not operationalized (WARN-level for D2/D3)**: Six references, none clearly post-2021, with no engagement with UTAUT/UTAUT2, self-determination theory, expectation-confirmation/continuance models, or the learning-analytics turn the field has taken. The paper invokes "technology acceptance" as its framing while explicitly declining to test an acceptance model — a defensible scoping decision, but the paper leans on the acceptance frame's authority for its "consistent with prior research" claim without engaging the frame's current form. *Why it's a problem*: the contribution is positioned against a literature the paper only partially represents, weakening the "one point in a distribution" claim (we cannot see the distribution). *Suggested direction*: either broaden the review to locate the r = .42 within an actual reported range of LMS perception–use correlations, or narrow the framing so it does not borrow acceptance-model authority it declines to use. *Field-norm grounding*: currency/coverage expectation is a general review-adequacy norm; because I am asserting the field has moved on (UTAUT2, learning analytics) without grounding that movement in a verifiable citation here, I cap the *currency* portion of this finding at advisory: `[FIELD-NORM UNVERIFIED]` for the specific "field has moved to X" severity. The thin-base and framing-coherence portions stand independently.

4. **Contribution is minimal and within-distribution (advisory)**: One bivariate association, one institution, n = 214, a single-item outcome, framed by the authors as incremental. Even granting the honesty, the domain question "does this add anything a reader could not predict from prior work?" is answered weakly — no new population characteristic, no discrepant result, no new instrument is foregrounded. *Suggested direction*: sharpen a specific non-redundant angle (a discrepant effect size vs. a named prior estimate, an under-studied population feature) rather than resting on within-distribution confirmation. Advisory — this is a contribution-bar judgment for the EIC, not a domain-accuracy error.

### Detailed Comments

#### Literature Review
- **Coverage**: Thin (6 sources) and non-current (nothing clearly post-2021). No UTAUT/UTAUT2, no expectation-confirmation/continuance, no self-determination, no learning-analytics/behavioral-log strand beyond the single Vasquez self-report-divergence cite. More critically, coverage cannot be certified at all because the cited works carry non-resolvable `10.5555` test DOIs.
- **Integration quality**: Above bare enumeration — the review does group cautions (Delgado on directionality, Ibarra & Poll on context, Vasquez on measurement, Song on cross-site variability) into a small critical synthesis and uses them to motivate the correlational-only stance. That is genuine synthesis, not a reference list. It is just built on an unverifiable base.
- **Research gap argument**: Legible but weak. The "incremental data point comparable with prior work" gap is honestly stated but does not establish non-redundancy, especially when the prior-work distribution it wants to add a point to is never quantified.

#### Theoretical Framework
- **Appropriateness**: The paper deliberately does *not* adopt a full theoretical framework — it invokes technology acceptance as background and declines to test a model. For a single-association descriptive study this is a defensible choice, and the paper is honest about it.
- **Application depth**: Correspondingly shallow by design; "perceived usefulness" is used as a TAM-lineage construct but not embedded in an acceptance model. The risk is borrowing the acceptance frame's credibility ("consistent with prior technology-acceptance research") without operationalizing it. Sharpen or narrow.
- **Alternative frameworks**: If the authors want the acceptance framing to carry weight, UTAUT2 or expectation-confirmation (continuance) would be the current reference points; a learning-analytics framing would suit the behavioral-reality concern. None is engaged.

#### Academic Argument Quality
- **Factual accuracy**: The domain claims that are internal to the study (moderate r, modest shared variance, engagement driven by many factors) are stated accurately and proportionally. The *unverifiable* claims are the external ones — "consistent with prior technology-acceptance research" and the validated-instrument provenance — because their supporting sources cannot be confirmed.
- **Argument logic**: Sound and disciplined. No causal leak from a cross-sectional correlation, reverse pathway acknowledged, generalization bounded. This is the paper's strongest feature and I found no D3-level reasoning error.
- **Terminology precision**: Consistent throughout; perceived usefulness, self-reported/perceived use, association vs. causation are used correctly and do not slip between sections.

#### Contribution to the Field
- **Incremental contribution**: Real but minimal — one within-distribution association from one site with a single-item outcome. Empirical, not theoretical or methodological.
- **Positioning**: The paper positions honestly as one data point, but cannot show the distribution it claims to join.
- **Overclaiming**: Notably absent. The manuscript under-claims if anything; the contribution question is about sufficiency, not inflation.

#### Missing Key References
- The operative issue is not missing references but *unverifiable existing* ones. I will not recommend specific replacement citations, because I cannot attest to specific author/year/venue metadata for this subfield's current LMS perception–use estimates without fabricating it (No-invention rule, #574 A5).
- Search leads the authors should pursue, phrased as leads not citations: `[UNVERIFIED]` current UTAUT2 LMS-acceptance work in higher education; `[UNVERIFIED]` learning-analytics literature comparing self-reported vs. log-based LMS engagement; `[UNVERIFIED]` common-method-variance treatment in single-instrument acceptance surveys. The authors must supply the actual, verifiable sources.

### Questions for Authors
1. Can you provide resolvable DOIs or stable identifiers for all six references? The current DOIs are all under the `10.5555/` test prefix and do not resolve to real records — this must be resolved before the paper can be evaluated as a contribution to the field.
2. Both your predictor and outcome are self-reported in the same instrument. How do you rule out (or bound) common-method variance as a contributor to the r = .42, separate from the self-report-vs-log divergence you already discuss?
3. You invoke "technology acceptance" but decline to test an acceptance model. What specifically does the acceptance framing add here that a plain "perception–reported-use association" framing would not, and why not engage the current form of that literature (e.g., UTAUT2, continuance models)?
4. Can you locate your r = .42 within an actual reported range of LMS perception–use correlations, so the "one point in a distribution" claim is quantified rather than asserted?

### Minor Issues
- The abstract calls the perceived-usefulness instrument "previously validated" but attributes it only to Costa & Wren (2019); given the citation-verification concern, the "validated" claim inherits the same verification dependency.
- "Consistent with prior technology-acceptance research" appears in abstract, results, and discussion; each instance depends on the unverified reference base and should be softened or re-grounded once sources are confirmed.

---

contract_role: domain

## Dimension Scores

### D1: methodology_rigor
From my domain seat, the field-recognized construct ("perceived usefulness," TAM-lineage, six-item adapted instrument, α = .88 reported) is used in a way an acceptance-model reader recognizes, and self-reported use is explicitly labeled as a proxy for perceived use rather than presented as verified behavioral use. My Phase 1 block trigger (construct unrecognizable OR self-report presented as verified behavior) is not met; my warn trigger (domain-recognized instrument under-reported) is partly present — item text and adaptation are not shown — but the reliability IS reported and the proxy limitation IS acknowledged, and the statistical-reporting completeness is Reviewer 1's seat, not mine. I hold this at pass from the domain vantage; the instrument-reporting gap is noted for Reviewer 1.
score: pass

### D2: domain_accuracy
My Phase 1 block trigger includes a load-bearing domain claim that cannot be supported as stated against the field. The paper's load-bearing external claim — consistency with prior technology-acceptance research, plus the "previously validated" instrument provenance — is anchored entirely to six references carrying non-resolvable `10.5555` test-prefix DOIs in unverifiable venues. I cannot certify that the field the paper claims alignment with exists as cited; the domain-accuracy claim therefore cannot be evaluated as supported. This meets my committed block trigger (a load-bearing domain claim unsupportable against established evidence, here because the evidence base is unverifiable). Grounded field-norm: `10.5555` is the DOI test prefix by construction non-resolvable, so this is not a `[FIELD-NORM UNVERIFIED]` severity assertion.
score: block

### D3: argumentative_coherence
The paper keeps causal/behavioral language proportional to a cross-sectional self-report design, describes the perceived-usefulness↔use link as association not causation, explicitly names the reverse pathway as equally consistent, and bounds generalization to the single institution. My Phase 1 block trigger (central thesis depends on a reasoning error the evidence cannot bear) is not met; my warn trigger (localized overclaiming / unbounded generalization) is not met either — generalization is explicitly bounded. This is the manuscript's strongest dimension.
score: pass

### D4: cross_disciplinary_relevance
Core constructs (perceived usefulness, self-reported vs. actual use, association vs. causation) are defined clearly enough that an adjacent-field reader (HCI, information systems, instructional design, learning analytics) can follow without in-group shorthand, and the paper makes no foregrounded interdisciplinary claim that rests on a domain error. My Phase 1 block trigger (a foregrounded interdisciplinary claim domain-inaccurate at its foundation) is not met; my warn trigger (constructs defined in in-group terms an adjacent reader could not follow) is not met. Deep cross-field assessment remains Reviewer 3's seat.
score: pass

### D5: writing_and_structure
The literature review offers genuine (if thin) critical synthesis rather than bare enumeration, the research-gap argument is legible, and domain terminology is internally consistent across all sections. My Phase 1 block trigger (terminological disorder so severe the claim cannot be reconstructed) is not met; my warn trigger (enumeration-not-synthesis, or inconsistent load-bearing terminology) is not met — the review does synthesize and terminology holds. Prose is clean.
score: pass

## Failure Condition Checks

### F1
Predicate: any mandatory dimension (D1, D2, D3) scores 'block'. In my own scores, D2 = block. The predicate is satisfied by my own card.
fired: true

### F2
Predicate: two or more mandatory dimensions score 'warn' or worse. In my own scores, D1 = pass, D2 = block, D3 = pass — exactly one mandatory dimension is 'warn or worse'. Predicate not satisfied by my own card. (`cross_reviewer_quantifier: majority` is panel-level machinery for the synthesizer, not applied by me.)
fired: false

### F3
Predicate: any high-priority dimension (D4) scores 'block'. In my own scores, D4 = pass. Predicate not satisfied.
fired: false

### F0
Predicate: every mandatory dimension (D1, D2, D3) scores 'pass'. In my own scores, D2 = block. Predicate not satisfied.
fired: false

## Editorial Decision

Per contract `failure_conditions` precedence (highest severity among fired conditions wins): F1 fired at severity 90, the highest. F1's action governs.
editorial_decision=reject_or_major_revision

---

## SEAT — Peer Reviewer 3 (Perspective)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor.** From an outsider's vantage, my paraphrase of this dimension is: does the study's design actually license the practical inferences a cross-disciplinary or applied reader would want to draw from a cross-sectional LMS survey? A self-report perceived-usefulness-versus-use design carries a well-known common-method and self-report-of-behavior problem, and I read this dimension as asking whether the reproducibility affordances (sampling frame, response rate, instrument transparency) are strong enough that a practitioner in an adjacent field — an instructional designer, an IT-adoption researcher — could trust and reuse the finding. I do not evaluate the statistics themselves (Reviewer 1's remit); I ask whether the design's limits are honestly surfaced so an outside reader is not misled about what a single-timepoint correlation can support.

**D2 — domain_accuracy.** I paraphrase this as: are the technology-acceptance and educational-technology constructs represented in a way that an adjacent-field reader (information-systems, HCI, adoption theory) would recognize as faithful? "Perceived usefulness" and "self-reported use" are load-bearing TAM/UTAUT terms with a large parallel literature outside education; my concern is whether the paper imports these constructs accurately or flattens them, and whether prior work is characterized correctly enough that a reader crossing in from information systems would not spot a misrepresentation. I flag domain drift from the outside; I do not run a systematic prior-work coverage audit (Reviewer 2's remit).

**D3 — argumentative_coherence.** From the perspective seat, I read this as: does the paper avoid the specific fallacy that most endangers this genre — treating a cross-sectional correlation between perceived usefulness and self-reported use as if it warranted a causal or directional claim, or as if self-reported use stood in for actual use? I attend to whether the central thesis over-reaches its cross-sectional evidence and whether the practical implications the authors draw are actually entailed by what a survey at one timepoint can show. Formal logic and internal contradiction-hunting are the Devil's Advocate's remit; I focus on whether the argument's reach matches its evidence in a way an applied reader would accept.

**D4 — cross_disciplinary_relevance.** This is my home dimension. I paraphrase it as: are the framing, construct definitions, and stated implications accessible and defensible to adjacent-field readers, and are any interdisciplinary claims substantiated rather than gestured at? For an LMS-adoption survey this means asking whether the paper connects to the broader technology-acceptance, information-systems, and learning-sciences conversations it necessarily sits inside, whether it names its stakeholders (students, instructors, institutional IT) rather than only faculty or only the institution, and whether "usefulness" and "use" are defined portably enough that a non-education reader knows exactly what was measured.

**D5 — writing_and_structure.** I paraphrase this as: is a short (1,597-word) empirical survey organized and expositionally clear enough that an outside reader can locate the design, the measures, the results, and the boundary conditions without insider knowledge? At this length the risk is compression that omits the limitations, sampling detail, or construct operationalization an adjacent-field reader needs. I assess clarity of exposition and venue-convention adherence from the outsider's readability standpoint, not copy-editing.

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for`: An explicit statement of the sampling frame, response rate, and whether the sample is representative of the undergraduate population; transparent reporting of the instrument (items, scales, provenance); and an honest limitations passage acknowledging the cross-sectional / self-report ceiling on what can be inferred, especially the gap between self-reported use and actual LMS log-level use.
- `what_triggers_block`: The design cannot support the practical inferences the paper draws and this is not surfaced anywhere — e.g., self-reported use is treated as a valid proxy for actual use with no acknowledgment, or the reproducibility affordances (who was sampled, how many responded, what was asked) are so absent that no adjacent-field reader could evaluate or reuse the result.
- `what_triggers_warn`: The core design limits (cross-sectional single timepoint, common-method / self-report bias, sampling representativeness) are real and material but only partially disclosed or buried, such that an outside practitioner could over-read the finding without careful reading.

### D2: domain_accuracy
- `what_to_look_for`: Faithful use of the technology-acceptance construct family — "perceived usefulness" and "use" defined consistently with their established meaning in TAM/UTAUT and adjacent information-systems literature — and correct, non-distorting characterization of any prior work the paper leans on to motivate the study.
- `what_triggers_block`: A load-bearing construct or prior finding is materially misrepresented in a way an adjacent-field reader would recognize as wrong — e.g., "perceived usefulness" is redefined to mean something the source literature does not support, and a central claim rests on that misrepresentation.
- `what_triggers_warn`: Construct usage or prior-work characterization is loose or imprecise (terms used interchangeably that the parallel literature distinguishes, or a prior result summarized in a way that shades its meaning) without a central claim collapsing on it.

### D3: argumentative_coherence
- `what_to_look_for`: Consistency between the strength of the conclusions and the reach of cross-sectional survey evidence; hedging that matches a correlational, single-timepoint, self-report design; and practical implications that actually follow from what was measured rather than from what the authors hope was measured.
- `what_triggers_block`: The central thesis depends on a claim the evidence cannot bear — a directional or causal reading of a cross-sectional correlation, or self-reported use standing in for actual use — such that if that unwarranted step is removed, the paper's main argument does not hold.
- `what_triggers_warn`: The argument over-reaches at the edges — some implications or phrasing imply more causal or generalizable force than a cross-sectional survey supports — but the core claim, read charitably, still stands on the correlational evidence.

### D4: cross_disciplinary_relevance
- `what_to_look_for`: Framing and definitions portable to adjacent-field readers (information systems, HCI, learning sciences); explicit engagement with the broader technology-acceptance conversation the study sits inside; named stakeholders beyond a single actor (students, instructors, institutional IT); and any interdisciplinary claim backed by something substantiable rather than asserted.
- `what_triggers_block`: The paper makes an interdisciplinary or generalizing claim that is central and wholly unsubstantiated, or is framed so narrowly/insularly that its stated implications are inaccessible or indefensible to the adjacent-field readers those implications explicitly address.
- `what_triggers_warn`: The framing is workable but insular — it under-connects to the obvious parallel technology-acceptance literature, defines "usefulness"/"use" too locally for a non-education reader to port, or omits a materially affected stakeholder — weakening but not voiding cross-field relevance.

### D5: writing_and_structure
- `what_to_look_for`: A clear IMRaD-style path from research question to design to measures to results to boundary conditions; construct operationalization stated plainly; and, at ~1,600 words, no compression that drops the limitations or sampling detail an outside reader needs to interpret the result.
- `what_triggers_block`: Organization or exposition is disordered enough that an adjacent-field reader cannot reliably locate what was measured, on whom, or with what result — the manuscript is not evaluable as presented.
- `what_triggers_warn`: The structure is followable but clarity gaps remain — a missing or thin measures/limitations passage, unclear operationalization, or venue-convention lapses — that force an outside reader to infer what should be stated.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

All three files read in full. Now producing my Phase 2 review, honoring my Phase 1 pre-commitment.

I note the citation-integrity flag from the field analyst: all six references carry sequential placeholder-style DOIs under the 10.5555 test/example prefix (2050001–2050006). This is verification-gate territory (EIC/R2's gating remit and the deterministic citation gate), not my dimension-scoring authority, but from the perspective seat it bears directly on D4 (whether the paper's cross-field "consistency with prior work" claims connect to a real conversation) and D2 (whether characterized prior work exists). I will surface it as an observation, not manufacture a fabrication verdict my seat cannot ground.

Working through my committed triggers against the manuscript, then the machine block.

---

## Perspective Review Report (Peer Reviewer 3)

### Reviewer Identity

Learning-analytics scientist and instructional-technology practitioner. I work with LMS system logs and institutional onboarding programs, and I approach this manuscript from a behavioral-data and applied-implementation angle rather than a survey-psychometrics one. I read it as an outsider to education-survey conventions but as an insider to the log-data reality the paper's self-report measure is standing in for, and to the onboarding practice its discussion gestures toward.

### Overall Recommendation

Minor Revision

### Confidence Score

4

### Summary Assessment

From the applied learning-analytics seat, this is a disciplined, honestly-scoped paper that mostly does what it says. It reports one moderate correlation (r = .42) between perceived usefulness and self-reported LMS use, refuses causal language, runs a Spearman robustness check, and stacks limitations including the self-report-versus-log gap that is my home concern — and it cites that specific gap (Vasquez, 2020) rather than hiding it. That is more methodological honesty than most single-site surveys of this genre show.

My reservations are about reach, not overreach. The paper sits inside a technology-acceptance and learning-analytics conversation it names only glancingly, and defines "use" in a way a non-education reader cannot fully port to behavioral engagement. The one place the argument leans past its evidence is the onboarding implication: a correlation between two self-reports, from a voluntary-response sample, is thin ground for even a hedged institutional recommendation, and the practical claim rests partly on a single practitioner account. None of this voids the contribution; it bounds it. The claims, read as written, stay proportional to a cross-sectional self-report design. I recommend minor revision to tighten the construct definition and the onboarding inference, not to redesign the study the authors did not write.

### Strengths (3-5 items)

1. **The self-report-versus-behavior gap is named, not buried**: The paper explicitly flags (via Vasquez, 2020) that self-reported technology use diverges from behavioral logs, and consequently frames its outcome as *perceived* rather than *actual* use. From a log-data perspective this is exactly the caveat I would demand, and the authors volunteer it. It is a genuine strength that the paper does not pretend a survey item is a behavioral count.

2. **Claims stay proportional to the design**: The reverse-causation pathway (use raising perceived usefulness) is acknowledged as equally consistent with the data; the association is called moderate, not strong; the variance-not-explained point is made in plain terms. An applied reader is not misled about what one cross-sectional correlation can support.

3. **Field-obvious confounders are at least surfaced**: Course requirements and assessment schedules — the two drivers any learning-analytics practitioner would name first as reasons a student opens the LMS — are mentioned as unmodeled influences. The paper does not model them, but it does not pretend they are absent either.

4. **Honest scope as a design choice**: The "incremental data point, not a model test" framing is stated up front and held to consistently. For an adjacent-field reader, this predictability is a virtue: I know exactly what claim I am being asked to accept.

### Weaknesses (3-5 items)

1. **"Use" is defined too locally to port to behavioral engagement (D4)**: The outcome is a single self-reported frequency item ("how often you accessed the LMS in a typical week"). To a learning-analytics reader, "access" and "use" are not interchangeable — a login is not a submission, a page-view is not sustained engagement, and "several times daily" of passive checking can mean less real engagement than one deep weekly session. The paper measures self-reported *access frequency* but discusses *engagement* and *use* as if portable. **Suggestion**: define the construct explicitly as self-reported access frequency, and state in one sentence what dimensions of behavioral engagement (session depth, feature use, submission activity) it does *not* capture, so a log-data reader knows precisely what was and was not measured.

2. **The onboarding implication reaches slightly past a two-self-report correlation (D3, edge)**: The discussion suggests usefulness-oriented onboarding "may be worth institutional attention." The hedging is real ("suggested by, not proven by"), so the core claim does not collapse — but the recommendation rests on (a) a moderate correlation between two measures collected in the *same* self-report instrument and (b) a single practitioner account (Whitfield, 2019). A same-instrument correlation is a weak causal base for an intervention recommendation even a hedged one. **Suggestion**: either drop the onboarding inference to a "future-work question" rather than a soft recommendation, or explicitly note that recommending an onboarding change on the strength of a same-source correlation would require a design (pre/post, or log-validated) the present study did not run.

3. **Under-connection to the parallel technology-acceptance and learning-analytics conversation (D4)**: The paper invokes "technology acceptance" as motivation but engages the broader conversation only glancingly — no connection to the UTAUT/UTAUT2 lineage that an information-systems reader would expect, and no engagement with the learning-analytics turn (behavioral/log evidence) that is precisely the field best positioned to extend this result. The framing is workable but insular; it under-connects to the obvious parallel literature a cross-field reader would reach for. **Suggestion**: one paragraph situating the finding against the acceptance-model lineage and against log-based engagement studies would let an adjacent-field reader place the result in its conversation. (Note: whether the *cited* works adequately cover that literature is Reviewer 2's remit; my point is the framing's reach, not coverage completeness.)

4. **Stakeholder frame is thin for a paper that draws an institutional implication (D4)**: The study is about students, but the one practical implication it draws is institutional (onboarding). Instructors — whose expectations and assessment design the paper itself names as drivers of LMS use — and institutional IT, who would actually implement any onboarding change, are absent as stakeholders. For a finding whose only actionable edge points at institutional practice, naming who is affected and who acts would strengthen cross-field relevance. **Suggestion**: in the discussion, name the affected/acting stakeholders (students, instructors, institutional IT) so the implication is legible to the practitioners it addresses.

### Detailed Comments

#### Assumption Audit

- **Explicit assumptions**: The paper explicitly assumes a self-reported frequency item is a defensible *indicator* of use, and it states this openly and hedges it. This assumption survives cross-disciplinary scrutiny *as stated* (it is labeled an indicator of perceived use), but only because the label is honest — the risk is that later sentences slide from "self-reported use" to "engagement/use" without the qualifier.

- **Implicit assumptions**: The load-bearing implicit assumption from my seat is that *access frequency stands in for engagement*. A learning-analytics reading rejects this equivalence: frequency of access and depth/quality of engagement are empirically distinct in log data. The paper never claims frequency = engagement, but the discussion's language occasionally presumes it. A second implicit assumption is that a same-instrument correlation can motivate a practice recommendation; from an applied-evaluation standpoint, common-source measurement is a weak foundation for any intervention inference.

- **Paradigmatic assumptions**: The paper sits in a perception-based self-report paradigm at a moment when the adjacent field (learning analytics) has moved toward behavioral/log evidence. This is not a flaw — a low-cost perception survey has a legitimate, complementary role — but the paper would be stronger for stating *why* the perception paradigm is the right lens for its question rather than defaulting to it. (I flag this as a paradigmatic observation, not a demand to have run a log study; reviewing the paper the authors wrote, a self-report design is a valid choice.)

#### Cross-Disciplinary Connections

- **Parallel research**: The learning-analytics literature on LMS engagement using clickstream/log data investigates the same substantive question (what predicts LMS use) with behavioral rather than perceptual measures. Situating the r = .42 self-report association against what log-based studies find would tell an adjacent-field reader whether perception tracks behavior or diverges from it — which is the paper's own open question (via Vasquez, 2020).

- **Borrowing opportunities**: The perceived-versus-actual-use divergence the paper cites is itself a live construct in learning analytics; framing the self-report measure explicitly as "perceived engagement, pending log validation" would borrow that field's precision and sharpen the paper's own caveat.

- **Methodological borrowing**: Not a demand, but worth one sentence in future-work: the institution already holds LMS logs; a follow-up correlating this perceived-usefulness measure against actual log-derived access would directly test the self-report-validity question the paper raises and cannot answer. This is the natural cross-field extension.

#### Practical Impact

- **Real-world application**: The honest reading is that this result, on its own, is not yet actionable for practice — it identifies an association, not a lever. The paper mostly respects this. The one place it edges toward action (onboarding) is where I would pull back hardest (see W2).

- **Implementation feasibility**: Any onboarding recommendation would be implemented by institutional IT and instructional-design staff, not by students. The paper's implication is aimed at an institutional actor it never names, and its evidence (a same-source correlation) would not, in an applied-evaluation setting, justify committing onboarding resources without a stronger design. This is a proportionality point, not a rejection.

- **Stakeholders**: Overlooked voices — instructors (named as a driver of use but absent as a stakeholder) and institutional IT (the actor for the sole practical implication). Students are well-centered; the institutional side of the frame is thin.

#### Broader Implications

- **Ethical dimensions**: Minimal and well-handled — anonymous, voluntary, IRB-approved, no linkage to individuals. From an applied-data standpoint the ethics posture is clean. Worth noting only that a future log-validation study (which I recommend as future work, not as a fix here) would raise data-governance questions this survey design correctly sidesteps.

- **Social impact**: Low and appropriately bounded. The paper's modest framing does not risk overclaiming social consequences. No equity concern arises from the design as written.

- **Future directions**: The most valuable cross-field follow-up is a log-validated replication at the same institution: correlate this perceived-usefulness instrument against behavioral log-derived engagement to test whether perception tracks actual use. That single study would convert the paper's biggest caveat into a finding.

#### Citation-base observation (out-of-seat flag, routed to synthesizer)

Not a D-dimension scoring input from my seat, and outside my scoring authority — but as an applied reader I note the field analyst's flag that all six references carry sequential DOIs under the 10.5555 example/test prefix (2050001–2050006). If the cited works do not resolve to real indexed sources, then the paper's repeated "consistent with prior work" framing — including the Vasquez (2020) self-report caveat I credited as a strength and the Whitfield (2019) practitioner account the onboarding claim leans on — would rest on an unverified base. Verification of the reference base is the EIC/R2 gating remit and the deterministic citation gate's job, not mine; I flag it because it directly conditions the cross-field "consistency with prior work" claims I assessed under D2/D4. I do not assert fabrication — I lack the grounding to — but the synthesizer should treat this as gating and confirm the base resolves before crediting any prior-work consistency.

### Cross-Disciplinary Reading Recommendations

- I decline to list specific cross-disciplinary citations here rather than risk inventing metadata (#574 A5 no-invention rule). The genuinely relevant bodies of work I would point the authors to, as **`[UNVERIFIED]` search leads** for them to locate and verify themselves, are: (a) the **learning-analytics literature on LMS clickstream/log-based engagement** (search leads: "LMS log data student engagement," "clickstream learning analytics engagement prediction"); (b) the **UTAUT / UTAUT2 technology-acceptance lineage** (search lead: "UTAUT2 Venkatesh consumer acceptance") as the model-based extension of the acceptance framing the paper invokes; and (c) work on **self-reported versus behaviorally-logged technology use** (the paper's own Vasquez, 2020 sits in this line — the authors should extend that thread). These are field pointers, not confident citations; I attest the *fields* exist, not any specific author/year/venue.

### Questions for Authors
1. Your outcome measures self-reported *access frequency*. From a behavioral-data standpoint, access frequency and engagement depth diverge in log data. Would you be willing to redefine the construct as "self-reported access frequency" and state explicitly which dimensions of engagement it does not capture?
2. The onboarding implication rests on a correlation between two measures collected in the *same* self-report instrument. What, in your view, distinguishes this from a common-source artifact, and would you consider reframing the onboarding point as a future-work hypothesis rather than a soft recommendation?
3. Your institution presumably holds LMS access logs. What prevented a log-validation of the self-report measure, and would you flag such a validation as the natural next study?
4. Who is the intended actor for the onboarding implication — students, instructors, or institutional IT — and how would you name those stakeholders in the discussion?

### Minor Issues
- "Access the LMS" (measures item) and "use"/"engagement" (discussion) are used as if interchangeable; a single construct-definition sentence would fix this throughout.
- The variance-shared point in Results is made in prose ("modest") without stating the value; an adjacent-field reader would benefit from one explicit figure.
- The Whitfield (2019) citation is described as a practitioner account; labeling it explicitly as practitioner (non-empirical) evidence at the point of the onboarding claim would keep the evidence hierarchy transparent to an outside reader.

---

## Machine Block

contract_role: perspective

## Dimension Scores

### D1: methodology_rigor
The design's reproducibility affordances and honest surfacing of the cross-sectional / self-report ceiling are adequate for an outside reader: sampling window, response accounting (233 → 214), exclusion rules, instrument provenance, α, power, and CI are reported, and the self-report-versus-log gap is explicitly disclosed (Vasquez, 2020). My Phase 1 block trigger (self-reported use treated as a valid proxy with no acknowledgment) did not fire — the acknowledgment is present and repeated. My warn trigger (core design limits only partially disclosed or buried) also did not fire: the cross-sectional, common-source, and voluntary-response limits are each surfaced in dedicated sentences. Item-level use-measure detail is thin, but that is R1's psychometric remit, not my reproducibility-for-outsiders standard.
score: pass

### D2: domain_accuracy
The technology-acceptance constructs ("perceived usefulness" as belief a tool aids performance) are represented faithfully to their established TAM-lineage meaning, and prior work is characterized without distortion *as attributed*. My Phase 1 block trigger (a load-bearing construct materially misrepresented) did not fire. My warn trigger (loose or imprecise construct usage) is borderline: "access"/"use"/"engagement" are used with some slippage, but that slippage is a portability/definitional problem I score under D4, not a misrepresentation of the acceptance construct family itself. The citation-base integrity concern is real but is a verification-gate/EIC/R2 matter and does not, from my seat, constitute a domain *misrepresentation* verdict I can ground. D2 stays pass on my committed triggers.
score: pass

### D3: argumentative_coherence
The central thesis — a moderate correlation between perceived usefulness and self-reported use — is stated with hedging that matches a correlational, single-timepoint, self-report design; reverse causation is conceded; no causal claim is load-bearing. My Phase 1 block trigger (the central thesis depends on an unwarranted causal/directional step, or self-report standing in for actual use) did not fire — remove any over-reach and the core correlational claim still stands. My warn trigger (the argument over-reaches at the edges) *does* fire: the onboarding implication reaches past a same-instrument two-self-report correlation, and rests partly on a single practitioner account, even though it is hedged. This is edge over-reach, not core collapse — exactly the warn pattern I committed to.
score: warn

### D4: cross_disciplinary_relevance
This is my home dimension and where the paper is weakest for an adjacent-field reader. My Phase 1 block trigger (a central interdisciplinary claim wholly unsubstantiated, or framing so insular its stated implications are indefensible to the readers they address) did not fire — the paper's core claim is accessible and its implications are hedged. My warn trigger fires on three counts I committed to: (1) "usefulness"/"use" defined too locally for a non-education / log-data reader to port (access frequency conflated with engagement); (2) under-connection to the obvious parallel technology-acceptance and learning-analytics conversation the study sits inside; (3) a materially affected stakeholder set (instructors, institutional IT) omitted from a paper whose sole practical implication is institutional. Workable but insular — the warn pattern, not the block pattern.
score: warn

### D5: writing_and_structure
The manuscript follows a clean IMRaD path; an outside reader can locate the design, measures, results, and boundary conditions without insider knowledge, and the limitations passage is present and substantive. My Phase 1 block trigger (organization disordered enough that an adjacent-field reader cannot locate what was measured, on whom, with what result) did not fire. My warn trigger (followable but with clarity gaps forcing inference) is borderline: the access/use/engagement construct slippage and the unstated variance-shared figure are minor clarity gaps, but they are localized and do not force an outside reader to *infer what should be stated* about the core design — the operationalization, sample, and result are each stated plainly. On balance the exposition clears my outsider-readability bar. Pass.
score: pass

## Failure Condition Checks

### F1
Predicate: any mandatory dimension (D1, D2, D3) scores 'block'. My D1=pass, D2=pass, D3=warn. No mandatory dimension scored block.
fired: false

### F2
Predicate: two or more mandatory dimensions (D1, D2, D3) score 'warn' or worse. My mandatory scores: D1=pass, D2=pass, D3=warn — exactly one at 'warn'. Threshold of two not reached on my seat's scores. (The `cross_reviewer_quantifier: majority` is panel-level machinery the synthesizer applies; I evaluate the predicate against my own scores only.)
fired: false

### F3
Predicate: any high-priority dimension (D4) scores 'block'. My D4=warn, not block.
fired: false

### F0
Predicate: every mandatory dimension (D1, D2, D3) scores 'pass'. My D3=warn, so not every mandatory dimension passed.
fired: false

## Review Body

From the applied learning-analytics seat, this is an honestly-scoped, well-behaved cross-sectional survey whose claims mostly stay proportional to a two-self-report correlational design. Its central correlational thesis holds and is properly hedged, so no mandatory dimension blocks. Two dimensions draw a warn on my committed triggers: D3, because the onboarding implication reaches past a same-instrument correlation and a single practitioner account even while hedged (edge over-reach, not core collapse); and D4, my home dimension, because "use" is defined too locally to port to behavioral engagement, the framing under-connects to the parallel technology-acceptance and learning-analytics conversation, and the stakeholder frame omits the instructors and institutional IT that the paper's one institutional implication actually addresses. D1, D2, and D5 pass: the reproducibility affordances and design-limit disclosures are adequate for an outsider, the acceptance constructs are faithfully represented, and the IMRaD exposition is locatable. On my own scores only one mandatory dimension warns, so neither F1 nor F2 nor F3 fires from this seat; the decision my scores yield is the accept-grade action, though I record it alongside two genuine warn-level findings the synthesizer should weigh against the rest of the panel (and against the still-open reference-base verification, which conditions the prior-work-consistency claims I credited). My recommendation to the author is minor revision: tighten the construct definition, right-size the onboarding inference, and name the stakeholders — none of which requires redesigning the study.

## Editorial Decision

editorial_decision=accept

---

## SEAT — Devil's Advocate

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor.** From the adversarial seat, this dimension is where I stress-test whether the survey machinery can bear the weight the paper puts on it. For a cross-sectional self-report survey of undergraduates, the standard attack surfaces are: an unstated or non-probability sampling frame dressed as if it generalizes; a response rate that is absent, low, or silently redefined; construct measures ("perceived usefulness", "self-reported use") deployed without reliability/validity evidence; and — the load-bearing weakness of this whole design — common-method variance, since both the predictor and the outcome come from the same instrument at the same moment. My job is to ask whether the reported statistics actually license the inferential claims, and whether reproducibility affordances (instrument items, scoring, data) are present or merely gestured at. I judge this against the actual accepted bar for higher-education survey work, not a laboratory-experiment or preregistration reference class I would be wrong to import (Dimension 9 gate).

**D2 — domain_accuracy.** Adversarially, I probe whether the paper's framing of its own constructs and of the prior literature is faithful rather than convenient. "Perceived usefulness" carries a specific TAM lineage; I watch for a paper that borrows the term's authority while measuring something looser, or that cites the technology-acceptance canon selectively to manufacture a supportive backdrop while omitting the well-documented gap between *perceived usefulness* and *actual/behavioral use*. Cherry-picking and confirmation bias live here: a literature section engineered so the hypothesis was foregone. I am not the domain reviewer's completeness auditor — I am hunting misrepresentation and selective use, not counting missing citations.

**D3 — argumentative_coherence.** This is the DA's home dimension. The characteristic failure of a perceived-usefulness/self-reported-use study is the correlation→use slide: interpreting a cross-sectional association between two self-reported attitudes as evidence about real behavior or about a causal mechanism ("students find it useful, therefore they use it"). I look for the logic chain from data to conclusion, hidden assumptions (that self-reported use tracks actual use; that a single time-point supports a directional story), non-sequiturs between the results and the discussion, and whether a rival explanation — social desirability, a third variable such as course requirement or mandated LMS use — fits the data at least as well as the authors' account.

**D4 — cross_disciplinary_relevance.** As adversary I ask whether the paper's framing and implications survive being read by someone outside educational technology, or whether they only cohere inside an in-group vocabulary. Are "usefulness" and "use" defined operationally enough that an adjacent-field reader could evaluate them, or do interdisciplinary implication claims (for instruction, for LMS procurement, for policy) outrun what a single cross-sectional undergraduate survey can support? This is a high-priority dimension, so a block here matters, but I hold it to a relevance-and-substantiation standard, not a novelty standard.

**D5 — writing_and_structure.** At 1597 words this is a short-format manuscript, and my adversarial concern is not prose polish (that is not my seat) but whether brevity has been used to *hide* rather than to *compress*: methods sections too thin to reproduce, results reported without the numbers needed to check the claims, or a structure that lets an unsupported conclusion pass by never confronting it with the data. I flag structural evasion, not stylistic taste.

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for` — Sampling frame and recruitment method; whether the sample is probability or convenience and whether generalization language matches; reported N, response rate, and its denominator; reliability (e.g., internal-consistency) and any validity evidence for the perceived-usefulness and self-reported-use measures; whether items/scoring/data are provided or referenced; explicit acknowledgment of common-method variance and single-time-point limits; alignment between the statistics reported and the inferences drawn.
- `what_triggers_block` — A core inferential claim rests on a design the data cannot support and no revision within the study rescues it: e.g., generalization to "undergraduates" from an unstated or plainly non-representative convenience sample presented as if representative; a primary statistic that contradicts or cannot substantiate the stated conclusion; or self-reported use treated as actual/behavioral use as a load-bearing premise. Norm-dependent severity here is grounded against higher-education survey practice with `field_norm_boundary` + `evidence_crossing_rationale`, else down-rated per the #215 gate.
- `what_triggers_warn` — Real but revision-addressable rigor gaps: missing or unclear response rate, absent reliability/validity evidence, no common-method-variance acknowledgment, or generalization slightly outrunning the sample — each undermining credibility without collapsing the core argument.

### D2: domain_accuracy
- `what_to_look_for` — Faithful use of technology-acceptance terminology ("perceived usefulness" in its TAM sense) versus authority-borrowing with a looser measured construct; correct representation of cited prior work; whether the perceived-usefulness-vs-actual-use gap is acknowledged or suppressed; balance of supporting vs contradicting citations; signs the literature was assembled to predetermine the hypothesis.
- `what_triggers_block` — A demonstrable domain factual error or misrepresentation load-bearing to the argument: a construct claim contradicted by the established meaning it invokes, or prior findings inverted/misstated such that the paper's central claim depends on the misrepresentation.
- `what_triggers_warn` — Selective citation favoring the hypothesis, omission of the well-known usefulness↔use divergence, or imprecise-but-not-false handling of domain terms — evidence-selection bias that weakens credibility but leaves the core claim standing.

### D3: argumentative_coherence
- `what_to_look_for` — The explicit chain from cross-sectional association to each conclusion; whether correlation is silently upgraded to causation or to a claim about real behavior; hidden assumptions (self-report ≈ actual use; single time-point ⇒ directional story); internal contradictions between results and discussion; a rival explanation (social desirability, mandated/required LMS use, a common third variable) that fits the data as well as or better than the authors' account.
- `what_triggers_block` — The main conclusion does not follow from the presented evidence (correlation-to-causation or correlation-to-behavior leap that is central, not incidental), the data actively contradict the stated conclusion, or a stronger counter-narrative is more parsimonious AND better fits the reported data — a Logic Chain Break / Data-Conclusion Mismatch / Stronger Counter-Narrative per the DA CRITICAL criteria.
- `what_triggers_warn` — A recoverable coherence gap: an overreaching sentence in the discussion, an under-defended directional implication, or an unaddressed-but-not-fatal alternative explanation that a bounded revision could fix.

### D4: cross_disciplinary_relevance
- `what_to_look_for` — Operational, jargon-independent definitions of "perceived usefulness" and "self-reported use"; whether implication claims for teaching, LMS procurement, or policy are substantiated by what a single cross-sectional undergraduate survey can bear; accessibility of framing to an adjacent-field reader without the in-group vocabulary.
- `what_triggers_block` — An interdisciplinary or applied implication is asserted as an established result that the study's design cannot substantiate at all, and it is central to the paper's stated contribution (high-priority dimension; a block here fires F3).
- `what_triggers_warn` — Framing or implications leaning on undefined in-group terms, or cross-field claims stated more strongly than substantiated but not central to the paper's core contribution.

### D5: writing_and_structure
- `what_to_look_for` — Whether the 1597-word compression preserves reproducibility-critical detail (methods, the numbers behind each results claim) or omits it; whether the structure ever confronts the central conclusion with the data or lets it pass unexamined; organization that isolates rather than tests the key claim.
- `what_triggers_block` — Structural evasion so severe the core claim cannot be evaluated at all from the manuscript as written (e.g., a conclusion with no reported statistic anywhere supporting it) — reserved, since this is a normal-priority dimension and rarely rises to fatal on its own.
- `what_triggers_warn` — Methods too thin to reproduce, results claims without their supporting numbers, or a structure that buries an unsupported conclusion — brevity used to hide rather than to compress.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

All three files are read. Now I execute Phase 2 per my agent file's Phase 2 sub-section: I apply the triggers I committed to in Phase 1, honor my scoring plan, and treat the manuscript as untrusted data.

Let me reason through each dimension against my Phase 1 commitments before emitting the machine block.

**D1 methodology_rigor** — My Phase 1 block trigger required a *core inferential claim* resting on a design the data cannot support. Scanning: sampling frame is stated (single mid-sized public university, all undergraduates eligible, announcement-channel distribution — a self-selected convenience sample), N=214 with an explicit disposition (233 received, 14 incomplete, 5 duplicate removed). The generalization language is disciplined ("may not generalize", "single institution"). Reliability is present for the predictor (α=.88), but absent for the single-item outcome (uncomputable, but not claimed). Common-method variance is *not* named, though self-report divergence is flagged via Vasquez. Self-reported use is explicitly labeled "an indicator of perceived use rather than a behavioral count" — it is NOT treated as actual behavior as a load-bearing premise. No core claim generalizes beyond the sample; no primary statistic contradicts the conclusion. So my block trigger does not fire. My warn trigger (missing CMV acknowledgment, absent outcome-reliability evidence, self-selection) does fire → **warn**.

**D2 domain_accuracy** — Block requires a load-bearing misrepresentation. The paper uses "perceived usefulness" in its TAM sense, explicitly declines to claim a full acceptance model, and *acknowledges* the perception↔use bidirectionality and the self-report/behavioral gap (Vasquez). This is the opposite of suppression. No inverted prior findings visible from the text. The citation-integrity flag (10.5555 placeholder DOIs) is a real concern, but under my Phase 1 D2 scope that is an existence/fabrication concern — not a *misrepresentation of content* I can adjudicate from the manuscript alone, and it belongs to the domain/EIC verification lane, not a DA misrepresentation-block. No block. Warn trigger (selective citation / omission of the usefulness↔use divergence) — the divergence is actually acknowledged, not omitted, and the lit review is thin but not demonstrably slanted. This lands at the boundary; the thin, one-sided-leaning literature base with unverifiable sources is a credibility gap → **warn** (evidence-selection/currency weakness, core claim still standing).

**D3 argumentative_coherence** — My home dimension. Block requires the correlation→causation or correlation→behavior leap to be *central*. The paper does not make it: causal language is explicitly disclaimed, reverse pathway is granted as "equally consistent", the outcome is framed as perceived/self-reported not actual, and rival third-variables (course requirements, assessment schedules) are named in the results and limitations. The one soft spot is the onboarding implication in the Discussion, but it is hedged ("may be worth institutional attention", "suggested by, not proven by"). No central leap, no data-conclusion contradiction, no stronger counter-narrative the authors left unaddressed. Block does not fire. Warn trigger (an under-defended directional implication) — the onboarding recommendation leans slightly beyond a symmetric correlation, recoverable by revision → **warn**.

**D4 cross_disciplinary_relevance** (high priority) — Block requires an interdisciplinary/applied implication *asserted as an established result* the design cannot support, *central* to the contribution. The onboarding implication is offered, but explicitly as suggestion not proof, and it is not the central contribution (the association is). Definitions are operational and accessible. Block does not fire → no F3. Warn: the applied onboarding claim leans slightly beyond substantiation but is not central → **warn**.

**D5 writing_and_structure** (normal) — Block reserved for structural evasion so severe the core claim can't be evaluated. Every results claim carries its number (r, CI, p, n, ρ, α, means). Methods are thin (items not shown, adaptation undescribed, no CI/descriptive for the use item) — but the core claim IS evaluable. No structural evasion. Warn: methods too thin to fully reproduce (items/adaptation/factor structure absent) → **warn**.

No dimension crosses my Phase 1 block trigger. I hold all five commitments; no dissent needed (and my dissent limit is one anyway). Result: D1–D5 all **warn**, zero **block**.

Failure conditions against my scores: F1 (any mandatory dimension block) → no block anywhere → false. F3 (high-priority D4 block) → D4 warn not block → false. F2 (two-or-more mandatory dimensions warn-or-worse) → D1, D2, D3 all warn → **fired**. F0 (every mandatory pass) → false. F2 is the highest-severity fired condition → `editorial_decision=major_revision`.

---

## Devil's Advocate Review

### Strongest Counter-Argument

If I held the opposite view of this paper, my strongest line of attack would not be that the authors overclaimed — they conspicuously did not — but that the entire result is a **common-method artifact wearing the costume of a substantive finding**. Both the predictor (a six-item perceived-usefulness scale) and the outcome (a single self-reported frequency item) are attitudinal self-reports collected from the same respondent, in the same instrument, at the same moment. A r = .42 between two same-source self-reports is exactly what common-method variance predicts even when no perception→behavior link exists at all: a respondent who endorses "this LMS helps me" is disposed to also endorse "I use it a lot," because both tap a single latent favorability toward the platform. The paper flags self-report/behavioral divergence via Vasquez (2020) but never names common-method bias as the specific threat, which is the one threat that could hollow out the headline number. Under this rival account, the association is not "perceived usefulness tracks engagement" but "self-rated approval correlates with self-rated approval" — a near-tautology that a behavioral-log design would be needed to break. Layer onto this the "So what?" problem: a moderate perception-use correlation has been reported for over a decade across the TAM literature the paper itself cites, so even taking the number at face value, the marginal knowledge added by one more single-site self-report estimate is close to zero. The honest framing is real, but honesty about scope does not manufacture contribution where the design cannot separate the finding from the method that produced it.

### Issue List

#### CRITICAL

*None. No core claim rests on a design the data cannot bear: causal language is disclaimed, the outcome is explicitly framed as perceived/self-reported rather than behavioral, and the reverse pathway and third-variable confounds are conceded in-text. The honest scoping keeps every finding out of Foundation-Collapse / Logic-Chain-Break / Data-Conclusion-Mismatch territory.*

#### MAJOR

| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|----------|---------------------|-----------------------------|
| M1 | 4 (Logic Chain) / 3 (Confirmation) | The headline r = .42 is not defended against the strongest rival explanation for it: **common-method variance**. Both variables are self-reports from one respondent in one instrument, so the correlation is fully consistent with a single latent favorability construct rather than a perception→use link. The paper names self-report/behavioral *divergence* (Vasquez, 2020) but never names or bounds *same-source bias*, which is the specific threat to this specific coefficient. | §2 ¶3; §4 ¶2; §6 (Limitation 2 addresses self-report vs logs, not same-source correlation) | Reporting-guideline norm for survey/self-report psychology (e.g., same-source designs are expected to acknowledge common-method variance as a named threat; Podsakoff-lineage reporting practice is standard in the technology-acceptance subfield the paper invokes) | The paper's *central* quantitative claim is a correlation between two same-instrument self-reports; that is the exact configuration the norm targets, and the omission is not generic reporting incompleteness but a live alternative explanation for the load-bearing number. |
| M2 | 8 ("So What?") / 3 (Confirmation) | The literature base is thin (6 sources), leans uniformly confirmatory, and — as flagged for panel verification — every reference carries a sequential placeholder-pattern DOI (10.5555/2050001–2050006). If the cited prior work cannot be confirmed to exist, the paper's core rhetorical move ("consistent with prior work") is unsupported, and with it the incremental-data-point justification for publishing. | §References (all six); §2; §5 ¶1 | Citation-existence is a floor requirement, not a field-relative norm (a cited source must be a real, locatable work in any field) — so this is grounded independent of subfield practice | The "consistent with prior work" framing and the entire contribution claim ("an incremental data point, comparable with prior work") are load-bearing on the cited corpus being real; a placeholder-DOI pattern across 6/6 references is positive evidence the corpus may be synthetic, which would collapse the stated contribution rationale. |

#### MINOR

| # | Dimension | Issue Description | Location |
|---|-----------|-------------------|----------|
| m1 | 5 (Overgeneralization→Implication) | The onboarding recommendation ("usefulness-oriented onboarding may be worth institutional attention") is drawn from a symmetric cross-sectional correlation the authors themselves say is non-directional; an implication that privileges the perception→use direction leans slightly past what the design licenses, even hedged. | §5 ¶2 |
| m2 | 4 (Hidden Assumption) | The single-item outcome is treated as an adequate stand-in for "use" throughout, with no construct-validity or test-retest support offered; its adequacy is assumed rather than argued (reliability is uncomputable for one item, which the paper does not remark on). | §3.2; §4 ¶1 |
| m3 | 2 (Cherry-Picking, mild) | The instrument is "adapted from Costa & Wren (2019)" but the adaptation is undescribed, items are not shown, and no factor structure is examined — the reader must take the α = .88 on trust without seeing what was measured. | §3.2 |

#### OBSERVATION

- The paper's discipline is genuine and should be credited at synthesis: correlational-only language is maintained throughout, a Spearman robustness check is reported, a power analysis and 95% CI accompany the coefficient, and four limitations are stacked honestly. My findings target what that discipline *cannot* fix (same-source confounding, unverifiable corpus, incremental contribution), not overclaiming — because there is little overclaiming to attack.

### Ignored Alternative Explanations/Paths

1. **Common-method / same-source variance (stronger than the authors' account for the headline number).** A single latent "favorability toward the LMS" disposition would produce r ≈ .42 between two same-instrument self-reports with no perception→use relationship whatsoever. This fits the reported data at least as well as the authors' "perceived usefulness tracks engagement" reading and is never bounded. The available remedy (behavioral log data as the outcome) is named by the authors as future work but not as a threat to the present coefficient.
2. **Requirement-driven use as the real driver.** Course requirements, assessment schedules, and mandated LMS activity — which the paper *lists* as unmodeled influences — could jointly drive both "I find it useful" and "I use it often" (you rate a tool you are forced to use, and depend on, as more useful). This third-variable path is acknowledged as noise but never entertained as a rival *explanation* for the association itself.
3. **Self-selection / voluntary-response inflation.** Because recruitment was via the announcement channel and participation voluntary, the sample over-represents students already engaged with institutional channels, compressing the low-usefulness/low-use corner and mechanically inflating a positive correlation. The paper flags voluntary response as a generalization limit but not as a source of correlation-magnitude bias.

### Missing Stakeholder Perspectives

- Students at the low-engagement / non-responding end — the voluntary-response design structurally excludes exactly the population whose (non-)use the onboarding implication is meant to address.
- Instructors / course designers, whose requirement and assessment decisions are named as the likely dominant drivers of LMS use yet are absent from both the measurement and the framing.

### Unexamined Premise

The paper treats **"perceived usefulness" and "self-reported use" as two conceptually separable variables whose covariation is informative**, when the unstated assumption holding the whole study together is that a respondent's self-rating of *how useful* a tool is and their self-rating of *how much they use* it are independent enough measurements for their correlation to mean something beyond shared self-report disposition. If that separability assumption fails — and the same-source design gives no leverage to test it — the central quantity the paper reports is not a finding about the world but a property of the instrument.

---

contract_role: da

## Dimension Scores

### D1: methodology_rigor
score: warn

### D2: domain_accuracy
score: warn

### D3: argumentative_coherence
score: warn

### D4: cross_disciplinary_relevance
score: warn

### D5: writing_and_structure
score: warn

## Failure Condition Checks

### F1
fired: false

### F2
fired: true

### F3
fired: false

### F0
fired: false

## Review Body

From the adversarial seat, this manuscript is unusual in that its defining feature — scrupulous honesty about scope — deflects the DA's normal attack surface. There is no correlation-to-causation leap to break (causal language is explicitly disclaimed, §5 ¶2), no data-conclusion mismatch (every results claim carries its statistic, §4), and no overgeneralization to "undergraduates" (generalization is repeatedly bounded to the single site). Accordingly I found **no CRITICAL finding**: nothing here is a Foundation Collapse, Logic-Chain Break, Data-Conclusion Mismatch, or an unaddressed Stronger Counter-Narrative that is *central and fatal*. I held every one of my Phase 1 block triggers open and none fired.

What the honest framing cannot rescue lands as two MAJOR concerns. First (M1, D1/D3), the headline r = .42 is a correlation between two same-respondent, same-instrument self-reports, and the single rival explanation that would hollow it out — common-method / same-source variance — is never named or bounded. The paper cites self-report-vs-log *divergence* (Vasquez, 2020) but that addresses a different threat; same-source covariation is precisely the configuration reporting practice in the technology-acceptance subfield expects to be acknowledged, and here it is not. This is grounded, not a generic-standard import (Dimension 9 check applied): the threat targets the paper's *central* quantitative claim, not a peripheral reporting nicety. Second (M2, D2/D8), the six-reference base is thin, uniformly confirmatory, and — per the panel's citation-integrity flag — every DOI follows a sequential placeholder pattern (10.5555/2050001–2050006). The paper's contribution rationale is entirely "consistent with / comparable with prior work"; if that corpus cannot be confirmed real, the rationale collapses. Citation existence is a field-independent floor, so this severity does not rest on a contestable norm. I have scored this against D2 as a credibility/representation weakness rather than a block, because from the manuscript text alone I cannot *adjudicate* fabrication — I can only flag that the pattern is strong positive evidence and gate it to the domain/EIC verification lane.

The remaining concerns are MINOR: an onboarding implication that leans one direction past a symmetric correlation (m1), a single-item outcome whose construct adequacy is assumed rather than argued (m2), and an undescribed instrument adaptation the reader must accept on trust (m3). Each is revision-addressable.

On the dimension scores: I score **all five dimensions `warn`, none `block`**. D1 warn — real, revision-addressable rigor gaps (no CMV acknowledgment, no outcome-reliability evidence, self-selection) that undermine credibility without collapsing the core argument, per my Phase 1 warn trigger; the block trigger did not fire because no core inferential claim outruns the design and self-reported use is explicitly *not* treated as behavior. D2 warn — evidence-selection/currency weakness (thin, confirmatory, unverifiable corpus) with the core claim still standing; no demonstrable in-text misrepresentation, so no block. D3 warn — a recoverable coherence gap in the directional onboarding implication; the central chain does not commit the correlation→behavior leap, so no block. D4 warn — the applied implication leans past substantiation but is explicitly hedged ("suggested by, not proven by") and is not the central contribution, so the high-priority block (which would fire F3) did not trigger. D5 warn — methods too thin to fully reproduce (items, adaptation, factor structure, use-item descriptives all absent), but the core claim remains evaluable, so no structural-evasion block.

Because three mandatory dimensions (D1, D2, D3) score `warn`, F2 fires (two-or-more mandatory warn-or-worse). F1 and F3 do not fire (no block anywhere, including the high-priority D4). F0 does not fire (not every mandatory dimension passes). F2 is the highest-severity fired condition.

## Editorial Decision

editorial_decision=major_revision

# PART 3 — EDITORIAL SYNTHESIS

I have everything I need. I'll deliver the synthesis directly as my final response.

# Sprint-Contract Mechanical Synthesis

**Panel N = 5. Contract: reviewer/reviewer_full/v1 (generated_at=2026-07-24T08:00:00Z).**

## Step 1 — Dimension Scoring Matrix

| Dimension (priority) | EIC | R1 Methodology | R2 Domain | R3 Perspective | DA |
|---|---|---|---|---|---|
| **D1** methodology_rigor (mandatory) | warn | warn | pass | pass | warn |
| **D2** domain_accuracy (mandatory) | block | pass | block | pass | warn |
| **D3** argumentative_coherence (mandatory) | pass | pass | pass | warn | warn |
| **D4** cross_disciplinary_relevance (high) | warn | warn | pass | warn | warn |
| **D5** writing_and_structure (normal) | warn | pass | pass | pass | warn |

## Step 2 — Per-Condition Evaluation

| Cond | Severity | Quantifier | Predicate | Per-reviewer satisfaction | Count / threshold | Fired |
|---|---|---|---|---|---|---|
| **F1** | 90 | any (≥1 of 5) | any mandatory (D1/D2/D3) scores 'block' | EIC ✓(D2), R1 ✗, R2 ✓(D2), R3 ✗, DA ✗ | 2 ≥ 1 | **true** |
| **F2** | 70 | majority (≥3 of 5) | two or more mandatory dims score 'warn' or worse | EIC ✓(D1,D2=2), R1 ✗(1), R2 ✗(1), R3 ✗(1), DA ✓(D1,D2,D3=3) | 2 < 3 | false |
| **F3** | 60 | any (≥1 of 5) | any high-priority dim (D4) scores 'block' | none (all warn/pass) | 0 | false |
| **F0** | 10 | all (5 of 5) | every mandatory dim scores 'pass' | EIC ✗(D2 block), R2 ✗, DA ✗, R1 ✓, R3 ✓ | 2 of 5 | false |

Score ordering `pass < warn < block`; "warn or worse" = {warn, block}.

## Step 3 — Precedence and Decision

Fired conditions: {F1 (sev 90)}. Highest severity = F1 → its action governs.

fired_conditions: [F1]
editorial_decision=reject_or_major_revision

The contract's F1 action is the disjunctive `reject_or_major_revision`. Resolution to the concrete letter decision follows below in the general synthesis: two mandatory-D2 `block` scores anchored on the same fixable defect (unverifiable reference base) plus a clean D3 chain and revision-recoverable D1 gaps place this at the **Major Revision** end of the disjunction, gated on citation verification, not Reject.

---

# Editorial Decision Package

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript titled *"Perceived Usefulness and Self-Reported Learning Management System Use: A Cross-Sectional Survey of Undergraduate Students"* to the journal. Your manuscript has been reviewed by 5 independent reviewers, including the Editor-in-Chief, under our v3.6.2 sprint-contract review panel.

### Review Panel Provenance (#540)

All five reviewer personas ran on a single model family. Persona diversity is not model diversity — blind spots may be correlated across reviewers (Ren et al. 2026, arXiv:2607.13104 §5.2). No cross-family aggregate is computed; the panel matrix above shows each seat's scores by inspection.

### Decision: Major Revision (gated on citation verification)

The sprint-contract arithmetic fired F1 (`reject_or_major_revision`) on two mandatory-dimension `block` scores at D2 (domain_accuracy). Both blocks trace to a single, revision-recoverable defect — an unverifiable reference base — rather than to an uninterpretable design or a broken argument. The manuscript's argumentative discipline (D3 passes on four of five seats) and its revision-recoverable methodology gaps (D1 warns, no D1 block anywhere) place this at the **Major Revision** end of the disjunction. **This decision is conditional: if the six-reference base cannot be shown to consist of real, resolvable prior work, the D2 block is not repairable and the decision converts to Reject** (the position R2 states explicitly and the EIC treats as a submittability gate).

### Consensus Analysis

Consensus is computed across the 4 non-DA reviewers (EIC, R1, R2, R3); the DA's findings are tracked separately. Sub-claims are decomposed from the reviewers' weakness bundles (Step 1b).

#### Weakness Sub-Claim Inventory (Step 1b)

| sub_claim_id | parent_weakness | EIC | R1 | R2 | R3 | DA | evidence anchors |
|---|---|---|---|---|---|---|---|
| SC-1 | Reference base carries reserved-prefix sequential placeholder DOIs (10.5555/2050001–2050006); "consistency with prior work" and instrument provenance load-bearing on it | raised (5) | corroborated¹ (4) | raised (4) | corroborated¹ (4) | raised (4) | EIC W1/Q1; R1 Q5; R2 W1/D2-block; R3 citation-base flag; DA M2 |
| SC-2 | Common-method / same-source variance never named (both variables self-reported, one instrument) | not-mentioned | raised (4) | raised (4) | raised (4) | raised (4) | R1 W3; R2 W2; R3 W2/assumption-audit; DA M1 |
| SC-3 | Single-item outcome under-justified; no reliability/validity, ordinal-as-continuous | raised (4) | raised (4) | not-mentioned | not-mentioned | raised (4) | EIC W4; R1 W1; DA m2 |
| SC-4 | Instrument adaptation from Costa & Wren (2019) undescribed; items not shown; no factor structure | raised (4) | raised (4) | not-mentioned | not-mentioned | raised (4) | EIC minor/W4; R1 W2; DA m3 |
| SC-5 | No results artifact (zero tables/figures; scatterplot referenced §3.4 but not shown) | raised (4) | not-mentioned | not-mentioned | not-mentioned | not-mentioned | EIC W3 |
| SC-6 | Onboarding implication leans past a symmetric same-source correlation | not-mentioned | not-mentioned | not-mentioned | raised (4) | raised (4) | R3 W2/m1-equiv; DA m1 |
| SC-7 | Thin / non-current literature base; acceptance framing invoked but model not operationalized | raised (4) | not-mentioned | corroborated (4) | corroborated (4) | corroborated (4) | EIC W2; R2 W3; R3 W3; DA M2-adjacent |
| SC-8 | "Use"/"access"/"engagement" defined too locally to port to behavioral engagement | not-mentioned | not-mentioned | not-mentioned | raised (4) | not-mentioned | R3 W1 |
| SC-9 | No response rate against eligible population (denominator not stated) | raised (3) | corroborated (4) | not-mentioned | not-mentioned | not-mentioned | EIC minor; R1 §Sampling/minor |
| SC-10 | Contribution minimal / within-distribution ("So what?") | raised (4) | not-mentioned | corroborated (4) | not-mentioned | corroborated (4) | EIC W2; R2 W4; DA M2-tail |
| SC-11 | Stakeholder frame thin (instructors, institutional IT absent) for an institutional implication | not-mentioned | not-mentioned | not-mentioned | raised (4) | corroborated (4) | R3 W4; DA missing-stakeholders |

¹ R1 and R3 forward SC-1 as an integrity flag explicitly routed to the EIC/R2 gating lane rather than scoring it in their own D2; they corroborate the observation without claiming adjudication authority. Counted as `corroborated` (they affirm the concern exists) per the Step 1b rule that position tracks the reviewer's stated stance on the sub-claim, not their scoring lane.

#### Points of Agreement (Consensus)

**[CONSENSUS-4]** (all 4 non-DA reviewers agree; DA also corroborates):
1. **SC-1 — The reference base is unverifiable and load-bearing.** All four non-DA seats and the DA independently flag that every reference carries a sequential DOI under the `10.5555/` prefix reserved for testing/examples (`2050001`–`2050006`), and that the paper's core "consistent with prior technology-acceptance research" claim plus the "previously validated instrument" provenance rest entirely on these sources. R2 and the EIC ground this as a field-independent floor (a `10.5555` DOI is non-resolvable by construction), not a contestable norm. **Author MUST address — no decline option. This is the gating sub-claim.**

**[CONSENSUS-3]** (3 of 4 non-DA reviewers agree; one silent):
2. **SC-2 — Common-method / same-source variance is never named.** R1, R2, R3 all raise it (DA corroborates as its strongest counter-argument M1); the **EIC is silent** on it. Both the predictor (6-item PU scale) and outcome (single self-reported frequency item) are self-reports collected in one instrument, so part of r = .42 may be shared-method covariance. The paper flags self-report-vs-log divergence (Vasquez, 2020) but that is a different threat.
3. **SC-7 — Thin, non-current literature base; acceptance framing invoked without operationalizing the model.** EIC, R2, R3 agree (DA corroborates); **R1 silent**. Six sources, none clearly post-2021, no UTAUT/UTAUT2, expectation-confirmation, or learning-analytics engagement, while the paper leans on the acceptance frame's authority for its consistency claim. R2 caps the specific "the field has moved to X" severity at advisory (`[FIELD-NORM UNVERIFIED]`); the thin-base and framing-coherence portions stand independently.
4. **SC-10 — Contribution is minimal / within-distribution.** EIC, R2 agree, DA corroborates; **R1 and R3 silent** — this is a 2-agree corroborated finding among non-DA seats, not a CONSENSUS-3. Recorded here for grouping; prioritized as P2 below. One bivariate association from one site, framed by the authors themselves as incremental, with no new population, discrepant result, or new instrument foregrounded. R2 and R3 both note this is a contribution-bar judgment owned by the EIC, not a domain-accuracy error.

#### Corroborated / single-reviewer findings (below the consensus bar)

- **SC-3 (single-item outcome under-justified)** — corroborated (EIC, R1, DA; R2, R3 silent). Action-bearing P2.
- **SC-4 (instrument adaptation undescribed, reproducibility)** — corroborated (EIC, R1, DA; R2, R3 silent). Action-bearing P2.
- **SC-6 (onboarding implication over-reaches)** — corroborated (R3, DA; EIC, R1, R2 silent). Action-bearing P2. Note both raising seats stress the implication *is* hedged ("suggested by, not proven by"), so this is edge over-reach, not a coherence collapse.
- **SC-11 (thin stakeholder frame)** — corroborated (R3, DA; three silent). P3.
- **SC-9 (no response rate denominator)** — corroborated (EIC, R1; three silent). P3.
- **SC-5 (no results artifact / missing scatterplot)** — single-reviewer finding (EIC only). P2/P3.
- **SC-8 (local "use"/"engagement" definition)** — single-reviewer finding (R3 only). P2.

#### Points of Disagreement

There are **no `disputed` positions** in the inventory: no reviewer argues any sub-claim is not a real problem, and no two reviewers recommend incompatible remedies. What looks like divergence is scoring-lane assignment, not substantive conflict, and is arbitrated below.

**Disagreement 1: Where does SC-1 (the placeholder-DOI reference base) belong — a D2 `block` or an out-of-lane flag?**
- **EIC / R2 view**: SC-1 is a D2 (domain_accuracy) block. When a paper's domain footing rests on prior work that cannot be shown to exist, the domain representation cannot be certified; both scored D2 = block on this basis.
- **R1 / R3 / DA view**: SC-1 is real but belongs to the EIC/R2 verification lane; from their seats it does not fire *their* D2 block trigger (which each committed as requiring a demonstrable in-text statistical/construct misrepresentation, not an existence concern), so R1 and R3 hold D2 = pass and the DA holds D2 = warn, each forwarding SC-1 rather than scoring it.
- **Disagreement type**: Perspective difference (lane/authority), not existence or direction — all five agree the concern is real and gating.
- **Editor's Resolution**: SC-1 stands as the gating blocker. The EIC/R2 D2-block scoring is *correct within the contract*, and the arithmetic already fired F1 on it. The other three seats' choice to forward-not-score is defensible seat discipline and does not weaken the finding — silence-in-lane is not opposition (Step 2 counting rule). **The manuscript is blocked pending citation verification regardless of which lane owns the score.**
- **Resolution Rationale**: Expertise-first (domain/EIC own citation-existence verification) and evidence-first (a `10.5555` DOI is non-resolvable by construction — a grounded floor, not a norm judgment) both point the same way. No arithmetic softening: F1's action is not diluted by the three non-blocking D2 scores because F1's quantifier is `any`, satisfied by the EIC and R2 alone.

**Disagreement 2: Seat-level recommendations span Minor Revision to Major-Revision-or-Reject.**
- R1 and R3 recommend **Minor Revision** (their contract-derived machine action was the accept-grade entry, F0/none-fired, since no mandatory dim blocked or reached two-warn *on their own cards*); the EIC recommends **Major Revision**; R2 recommends **Major Revision, converting to Reject if citations cannot be verified**; the DA's machine action was **major_revision** (its own card fired F2 with three mandatory warns).
- **Disagreement type**: Severity disagreement driven by per-seat vs. panel-level arithmetic — R1/R3 correctly note the cross-reviewer quantifiers are panel machinery the synthesizer applies, not the seat.
- **Editor's Resolution**: The **panel-level** F1 governs (`reject_or_major_revision`), resolved to Major Revision gated on verification. The seat-level Minor recommendations from R1/R3 are not overridden as *judgments* — both explicitly deferred SC-1 to this lane — but the panel arithmetic, which is the contract's binding aggregation, subsumes them.
- **Resolution Rationale**: Conservative principle + the contract's published semantics. F1 fires on `any` reviewer's mandatory block; two seats supplied one. The synthesizer does not average the five seat recommendations (forbidden operation) and does not recompute thresholds against a sub-panel.

### Decision Rationale

The five reviewers converge on an unusual profile: a manuscript whose *conduct* is exemplary and whose *evidentiary base* cannot be verified. Every seat credits the paper's argumentative discipline — correlational language throughout, the reverse-causation pathway conceded as "equally consistent," generalization bounded to one site, a Spearman robustness check, a power analysis, and a 95% CI. That discipline is why D3 passes on four of five cards and why the DA, whose remit is to break the argument, found **no CRITICAL finding** and explicitly recorded that the honest scoping "deflects the DA's normal attack surface." The decision is therefore not Reject on argumentative grounds.

What forces the block is SC-1: all six references carry sequential `10.5555` test-prefix DOIs, and the paper's entire positioning against the field ("consistent with prior technology-acceptance research") plus the α = .88 instrument's "previously validated" provenance are load-bearing on them. The EIC and R2 score this D2 = block; R1, R3, and the DA forward it to this lane. The sprint-contract arithmetic fires F1 (severity 90) on the two blocks; F2 falls one seat short of its majority threshold (2 of 5, needs 3), and F3/F0 do not fire. F1's disjunctive action resolves to Major Revision rather than Reject because the defect is verification-recoverable and no design or argument is broken — but the decision is explicitly conditional: **if the reference base cannot be shown to be real, resolvable prior work, the D2 block is unrepairable and the decision converts to Reject.** Below the gate, three mandatory D1 warns (single-item outcome, undescribed adaptation, unnamed common-method variance) and the near-unanimous CMV finding (SC-2) are material but revision-recoverable, reinforcing Major over Minor.

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | Entire six-reference base carries reserved-test-prefix sequential DOIs (10.5555/2050001–2050006); "consistency with prior work" + instrument provenance unverifiable | EIC, R2 (block); R1, R3, DA (corroborate) | §References; §5 ¶1 "consistent with prior technology-acceptance research"; §3.2 Costa & Wren (2019) provenance | R1 |
| 2 | Common-method / same-source variance never named; r = .42 between two same-instrument self-reports may be partly method artifact | R1, R2, R3, DA | §4 ¶2; §6 Limitation 2 (addresses self-report vs logs, not same-source) | R2 |
| 3 | Single-item ordinal outcome carries headline-correlation weight with no reliability/validity and no item-level reporting; adaptation of PU scale undescribed | EIC, R1, DA | §3.2 (single 5-point item; scale "adapted from Costa & Wren 2019") | R3 |

---

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. DA-CRITICAL/non-decomposed items use `—`. There are no DA-CRITICAL findings in this round (the DA recorded none).

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Source | Priority | Estimated Effort |
|---|--------------|--------------|--------|----------|-----------------|
| R1 | **Supply resolvable DOIs / stable identifiers and full bibliographic details for all six references; confirm each exists and supports the attributed claim.** Until done, the manuscript cannot proceed. If any source cannot be verified, remove it and re-ground every claim that depended on it. | SC-1 | EIC, R2 (R1/R3/DA corroborate) | P1 | 2–5 days (author) + editor verification |
| R2 | **Name common-method / same-source variance as an explicit limitation distinct from the self-report-vs-log point.** If any single-common-factor, marker-variable, or item-separation diagnostic is feasible from the collected data, report it; otherwise state the constraint plainly and bound its likely effect on r = .42. | SC-2 | R1, R2, R3 (DA corroborates) | P1 | 2–3 days |

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Source | Priority | Estimated Effort |
|---|--------------|--------------|--------|----------|-----------------|
| S1 | Justify the single-item outcome explicitly (cite single-item-measure validity literature); report the item's full response-category distribution rather than a median category only; consider co-headlining the Spearman ρ as the assumption-appropriate statistic. | SC-3 | EIC, R1 (DA corroborates) | P2 | 2–3 days |
| S2 | Report the adapted six PU-scale items (or appendix/OSF pointer), state what changed from Costa & Wren (2019), and give at least inter-item statistics or a one-factor check; add a data/materials availability statement. | SC-4 | EIC, R1 (DA corroborates) | P2 | 2–3 days |
| S3 | Right-size the onboarding implication: reframe as a future-work hypothesis, or explicitly note that recommending an onboarding change on a same-source correlation would require a design (pre/post or log-validated) not run here. | SC-6 | R3 (DA corroborates) | P2 | 1 day |
| S4 | Either broaden the literature review to locate r = .42 within an actual reported range of LMS perception–use correlations, or narrow the framing so it does not borrow acceptance-model authority (UTAUT2, continuance) it declines to operationalize. Ties to R1 once verified sources exist. | SC-7 | EIC, R2, R3 (DA corroborates) | P2 | 3–5 days |
| S5 | Sharpen the specific non-redundant contribution (a discrepant effect size vs. a named prior estimate, or an under-studied population feature) rather than resting on within-distribution confirmation. | SC-10 | EIC, R2 (DA corroborates) | P2 | 2–4 days |
| S6 | Define the outcome construct explicitly as *self-reported access frequency* and state in one sentence which behavioral-engagement dimensions (session depth, feature use, submission activity) it does not capture. | SC-8 | R3 | P2 | 0.5 day |
| S7 | Add at least a descriptives table and a scatterplot (§3.4 references scatterplot inspection but shows none). | SC-5 | EIC | P2/P3 | 1 day |

### Revision Checklist (Checkable List)

#### Priority 1 — Structural / Gating Revisions (Estimated total effort: 4–8 days + editor verification)
- [ ] R1 (SC-1): Provide resolvable DOIs + full details for all 6 references; re-ground or remove any that cannot be verified. **GATE — decision converts to Reject if unmet.**
- [ ] R2 (SC-2): Add common-method-variance limitation, distinct from self-report-vs-log; report a diagnostic if feasible or state the constraint and bound its effect.

#### Priority 2 — Content Supplementation (Estimated total effort: 5–9 days)
- [ ] S1 (SC-3): Justify single-item outcome; report full response distribution; consider Spearman as primary.
- [ ] S2 (SC-4): Report adapted PU items + adaptation delta + dimensionality/one-factor check; add availability statement.
- [ ] S3 (SC-6): Reframe onboarding implication as future-work or state the design it would require.
- [ ] S4 (SC-7): Quantify the prior-work distribution or narrow the acceptance framing.
- [ ] S5 (SC-10): Sharpen the non-redundant contribution.
- [ ] S6 (SC-8): Define outcome as self-reported access frequency; state what it does not measure.

#### Priority 3 — Text and Formatting (Estimated total effort: 1–2 days)
- [ ] S7 (SC-5): Add descriptives table + scatterplot.
- [ ] SC-9: State the eligible-population denominator so a response rate can be computed.
- [ ] SC-11: Name the affected/acting stakeholders (students, instructors, institutional IT) in the discussion.
- [ ] Report a numeric shared-variance value (r² ≈ .18) alongside the qualitative "modest."
- [ ] Label the Whitfield (2019) practitioner account explicitly as non-empirical at the point of the onboarding claim (contingent on R1 verification).

### Total Estimated Effort
- **Major Revision**: 6–8 weeks (dominated by R1 verification/re-grounding and R2 re-analysis; re-review required).

### Revision Deadline
- **Recommended deadline**: 6–8 weeks from receipt of this letter.
- **Basis**: Major Revision. The revised manuscript will undergo another round of review.
- **Extension policy**: If an extension is needed, notify the editor 1 week before the deadline.

### Response Letter Template
Please use the format in `templates/revision_response_template.md` to respond to every Required and Suggested Revision item by item (Reviewer Comment → Author Response → Changes Made), with change markup and a page cross-reference table.

---

## Part 3: Reviewer Report Summary (Appendix)

### EIC Report Summary
- Recommendation: Major Revision | Confidence: 4
- Key Point: Conduct is disciplined and near-submittable in form, but the sequential `10.5555` placeholder reference base is a submittability gate and the contribution is thin/incremental (D2 = block).

### Reviewer 1 (Methodology) Summary
- Recommendation: Minor Revision | Confidence: 4
- Key Point: Within its scope the design is sound and transparently reported; the load-bearing gaps are the unvalidated single-item outcome, undescribed scale adaptation, and unnamed common-method variance (D1 = warn); DOI integrity forwarded to the EIC/domain lane.

### Reviewer 2 (Domain) Summary
- Recommendation: Major Revision, converting to Reject if citations cannot be verified | Confidence: 4
- Key Point: The field the paper claims consistency with is unverifiable — all six references carry non-resolvable `10.5555` test-prefix DOIs — so domain accuracy cannot be certified (D2 = block); secondarily, common-method variance is unnamed and the literature base is thin/non-current.

### Reviewer 3 (Perspective) Summary
- Recommendation: Minor Revision | Confidence: 4
- Key Point: From the applied learning-analytics seat the paper is honestly scoped but "use" is defined too locally to port to behavioral engagement, the framing under-connects to the parallel literature, and the onboarding implication reaches past a same-source correlation (D3/D4 = warn); DOI base flagged to the gating lane.

### Devil's Advocate Summary
- Machine action: major_revision (own card fired F2) | Confidence: not scored as a seat recommendation
- Key Point: The manuscript's honesty deflects the normal adversarial attack surface (no CRITICAL finding); the two surviving MAJOR concerns are that r = .42 is undefended against common-method variance and that the contribution collapses if the placeholder-DOI corpus is not real.

---

**Closing.** We encourage you to carefully address the reviewers' comments and submit a substantially revised manuscript. Priority-1 item R1 is a gate: the revised submission cannot advance until the reference base is verified as real, resolvable prior work; if it cannot be, this decision converts to Reject. The revised manuscript will undergo another round of review.
