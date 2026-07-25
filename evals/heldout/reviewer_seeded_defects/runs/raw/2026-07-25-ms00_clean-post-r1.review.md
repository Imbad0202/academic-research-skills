# Isolated-dispatch panel review — gamma-1 (post condition, 2026-07-25)

(Phase 1 calls were physically separated: each seat’s pre-commitment was produced by a clean
headless `claude -p` call — claude-opus-5, effort xhigh, thinking enabled — that received only
the contract + title/field/word_count and was forbidden from reading any manuscript. Phase 2,
field analysis, and synthesis were separate paper-visible headless calls with read scope
limited to the named skill files and the neutral-named manuscript copy.)

# PART 1 — FIELD ANALYSIS

# Field Analysis Report

## Paper Basic Information
- **Title**: Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students
- **Abstract length**: ~140 words (single paragraph, unstructured)
- **Full text length**: ~1,700 words including abstract; ~1,540 words of body text (Sections 1–7), excluding references
- **Number of references**: 6 (all journal articles, all with DOIs, dated 2018–2021)
- **Language**: English (review to be conducted in English)

## Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| Primary Discipline | Educational technology in higher education (LMS adoption and student engagement) |
| Secondary Disciplines | Information systems / technology-acceptance research (TAM lineage); educational measurement and psychometrics; higher-education institutional practice (learning-technology administration, learning analytics) |
| Research Paradigm | Quantitative — descriptive and correlational, explicitly non-model-testing |
| Methodology Type | Survey / questionnaire; cross-sectional single-site design; bivariate correlational analysis (Pearson with Spearman robustness check) |
| Target Journal Tier | **Q3**, with a defensible Q2 route only as a short/brief report. Rationale: the design is clean and the reporting is disciplined (95% CI, exact n, sensitivity analysis, a priori-style power statement, α for the predictor scale), which lifts it above Q4 entry level. But the substantive yield is a single bivariate coefficient from one institution, the literature base is 6 sources, and there is no theoretical extension, no moderator, no comparison group, and no behavioral criterion. Q1 field journals would desk-reject on contribution weight rather than on quality; mainstream Q2 outlets would likely require either substantial literature expansion or a format downgrade. |
| Paper Maturity | **Pre-submission.** Rationale: structure is complete and conventional (Intro → Lit Review → Methods → Results → Discussion → Limitations → Conclusion); prose is polished with no register slippage; numbers are internally consistent across abstract, results, discussion, and conclusion (r = .42 stated identically in all four; CI [.30, .52] is arithmetically correct for n = 214); references are uniformly formatted with DOIs; ethics, consent, and anonymity are reported. Remaining gaps are disclosure-level and reporting-level (response rate, demographics table, data-availability / funding / COI statements), not developmental. |

**Distinguishing characteristic — flag for the whole panel:** this manuscript is unusually well *calibrated*. Its claims are already hedged to the level its evidence supports: causality is disclaimed in the abstract, introduction, literature review, discussion, limitations, and conclusion; self-report is explicitly framed as an indicator of *perceived* rather than actual use, with a supporting citation (Vasquez, 2020); single-site limits are stated twice; the moderate effect size is characterized as moderate and the unexplained variance is acknowledged. The panel's principal risk here is therefore **not** missing overclaims — it is manufacturing them. See Review Strategy Recommendations.

## Recommended Target Journals (Top 3)

1. ***Education and Information Technologies*** — The closest match by topic and by the volume of comparable LMS-acceptance survey work it publishes; single-institution correlational designs are squarely within its accepted scope. Realistic outcome: major revision, with the demand being a substantially deeper literature base and a clearer statement of what this coefficient adds to an already crowded set of published estimates.
2. ***Research in Learning Technology*** — Open-access, and editorially receptive to modest, transparently bounded empirical contributions and shorter empirical papers. The manuscript's deliberate restraint is a fit with this journal's culture rather than a liability, and its self-description as "an incremental data point" would read as appropriate scoping rather than as an admission of thinness.
3. ***Journal of Information Technology Education: Research*** — A specialized outlet where an honestly framed single-site correlation can stand largely as written, particularly if reformatted as a research note. Lower prestige, but the lowest revision burden and the best odds of publication without distorting the paper's careful scope.

*(A brief-report or research-note format at any of the three should be raised explicitly by the EIC; the manuscript's length and single-coefficient yield fit that container better than a full research article.)*

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC
**Identity Description**: Editor-in-Chief of *Education and Information Technologies*, a mainstream high-volume educational-technology journal; former Associate Editor with portfolio responsibility for technology-acceptance submissions; has publicly written about the journal's desk-rejection criteria for single-site acceptance surveys and personally handles roughly 40 LMS-perception manuscripts a year, of which a large majority are declined on contribution grounds rather than on quality grounds.
**Review Focus**:
  1. **Contribution weight versus format.** Assess whether one bivariate correlation (r = .42) from a single institution, supported by 6 references, constitutes a full research article for this readership, or whether the correct editorial action is to invite resubmission as a brief report / research note. State the format recommendation explicitly rather than leaving it implicit in a revision list.
  2. **Fit and readership interest.** Determine what a reader of this journal learns that they could not already infer from the existing corpus of published perceived-usefulness/use correlations. The manuscript itself claims value as a comparable data point in a distribution (invoking Song, 2018) — test whether that claim is actually delivered, i.e. whether the paper gives readers what they would need to *place* this estimate in that distribution (comparable instrument details, sample characteristics, setting descriptors) or merely asserts comparability.
  3. **Disclosure and publication-readiness at the journal-policy level.** Check for the items the journal requires and the manuscript omits: response rate and eligible-population denominator, a participant-characteristics table, data-availability statement, funding statement, conflict-of-interest statement, and (given the ethics approval) the approval reference. These are gatekeeping items independent of scientific merit.

**Will particularly care about**: Whether the manuscript's admirable epistemic honesty is doing editorial work it cannot do — that is, whether "we offer this as a modest, incremental, design-bounded data point" is a virtue of framing or a self-diagnosis that the study does not clear the journal's novelty bar. The EIC must resolve that tension rather than praising the honesty and ducking the decision.
**Possible blind spots**: May under-credit the genuine methodological discipline in Sections 3.4 and 4 (the CI, the sensitivity analysis, the Spearman check, the refusal to over-read) because contribution concerns dominate the editorial frame. May also default to "add more literature and a theoretical model," which would push the author toward the model-testing the paper deliberately declines — the synthesizer should check that the EIC's demands do not silently redesign the study.

---

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1 — Methodology
**Identity Description**: Associate Professor of educational measurement and psychometrics; specializes in measurement error in self-reported behavior, the statistical behavior of single-item outcome measures, and correlation methods for ordinal data; has published simulation work quantifying attenuation and confidence-interval distortion when a continuous predictor is correlated with a coarse 5-category outcome, and reviews regularly for measurement-oriented journals.
**Review Focus**:
  1. **The single-item ordinal outcome.** The predictor is a 6-item scale with α = .88; the outcome is one 5-point frequency item with no reliability estimate and no validity evidence. Evaluate the consequences: attenuation of r toward zero, coarse-category ceiling on the observable correlation, and the impossibility of correcting for unreliability in the outcome. Note that the reported r = .42 is therefore a *lower bound with unknown slack*, and ask whether the manuscript's characterization of the effect as "moderate" should be qualified in that direction. Credit the Spearman check (ρ = .40) but state clearly what it does and does not address — it tests monotonicity/parametric form, not measurement coarseness or reliability.
  2. **Sample construction and the recruitment channel.** Three linked gaps: (a) no response rate and no eligible-population denominator, so non-response bias is unquantifiable and the "all enrolled undergraduates were eligible" frame is unverifiable; (b) recruitment ran through "the institution's course-announcement channel" — if that channel is delivered inside or through the LMS, recruitment is conditioned on the dependent variable, truncating the low-use end of the distribution; the Limitations section gestures at this ("students who engage more with institutional channels may be overrepresented") without identifying the mechanism or its directional effect on r; (c) 5 duplicate entries were identified and removed in a survey that states "no identifying information was collected" and that responses "could not be linked back to individual students" — ask how duplicates were detected, and whether that procedure is consistent with the anonymity claim in Section 3.3.
  3. **Instrument adaptation and common-method variance.** The perceived-usefulness scale is *adapted* from Costa and Wren (2019), but no adaptation log, item wording, or re-validation beyond α is provided (α establishes internal consistency, not that the adapted items measure the original construct). Separately, both variables come from the same self-report instrument, at the same moment, from the same respondent — common-method variance is a plausible upward contributor to r = .42 and is not discussed anywhere in the manuscript. Also verify: the reported median use category ("a few times per week") is not one of the two anchors given in Section 3.2, so the full response-option wording is missing.

**Will particularly care about**: Whether the precision of the *reporting* (CI, power statement, robustness check) is matched by precision about the *measures* — i.e. that a well-reported coefficient built on an unvalidated single-item outcome and a same-source method is not thereby a well-estimated one. This reviewer's characteristic move is to accept the paper's inferential humility and then ask for the same humility one level down, at the measurement layer.
**Possible blind spots**: Likely to have little interest in whether the study matters to the field or to practice; may produce a technically excellent minor-to-major revision list that implicitly assumes the paper should be published once the reporting gaps close. May also treat the substantive question — is LMS *frequency* a construct worth correlating with anything? — as out of scope. Covered by Reviewer 3.

---

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2 — Domain
**Identity Description**: Professor of higher education with a research programme on institutional learning-platform engagement; has published a systematic review of TAM/UTAUT applications in higher education documenting the accumulation of near-identical perceived-usefulness/use correlations, and co-authored empirical work pairing survey perceptions with LMS log traces; sits on the editorial boards of two educational-technology journals.
**Review Focus**:
  1. **Literature adequacy and currency.** Six references for a topic with hundreds of directly relevant published studies is the paper's most conspicuous domain-level weakness. Identify what is structurally absent, not merely "more citations": the post-TAM trajectory (UTAUT/UTAUT2 and the critiques of perceived usefulness as a predictor of *actual* rather than *intended* use), the learning-analytics literature comparing self-reported with log-derived LMS engagement (of which Vasquez, 2020 is the paper's sole representative), and any meta-analytic estimate of the perceived-usefulness/use association — which is the natural benchmark for r = .42 and is nowhere invoked. Note also that no source is later than 2021.
  2. **Whether the "incremental data point" claim is cashed out against the field.** The manuscript positions itself as one comparable point in a distribution of estimates (Section 2, final paragraph; Section 7). Test that against the field: does the paper cite the distribution it claims to join, report its estimate in a form comparable to those studies, and say where it falls relative to them? At present the comparison is asserted qualitatively ("consistent with prior technology-acceptance research") without a single competing coefficient quoted. This is a fixable and high-value revision.
  3. **Theoretical positioning as a deliberate choice.** The paper explicitly declines to test an acceptance model. Judge whether that abstention is coherent or evasive: it borrows the TAM construct and instrument while disowning the framework, which raises the question of what licenses the construct's use and interpretation. Distinguish carefully between "this paper should have tested a model" (scope creep — not the reviewer's call) and "this paper should justify why it uses a theory's central construct without the theory" (legitimate and answerable in a paragraph).

**Will particularly care about**: Whether the field learns anything, and whether the author's stated modesty has been used as a substitute for engaging the prior literature closely enough to know whether the finding is confirmatory, discrepant, or already superseded. This reviewer's sharpest question is not "is this true?" but "given the field, is this news?"
**Possible blind spots**: The strong pull toward "add UTAUT, add moderators, add a model" would convert a deliberately narrow descriptive study into a different paper; the synthesizer must hold this reviewer to the paper's declared scope. Also unlikely to scrutinize the duplicate-removal/anonymity tension or the single-item attenuation issue at technical depth (covered by Reviewer 1), and unlikely to question whether LMS use frequency is a normatively worthwhile outcome at all (covered by Reviewer 3).

---

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3 — Cross-disciplinary / Practical
**Identity Description**: Director of Learning Technology and Academic Analytics at a large public university — a platform owner, not an academic researcher; responsible for LMS procurement, onboarding programmes, and the institution's engagement dashboards; has run the internal evaluations that decide whether onboarding investment continues, and has repeatedly had to explain to senior leadership why LMS login frequency is a poor proxy for learning.
**Review Focus**:
  1. **Construct relevance of the outcome — the paper's largest unexamined assumption.** The dependent variable is *how often students access the LMS*. Nothing in the manuscript argues that more frequent access is desirable, and the framing ("institutions invest heavily on the assumption that availability translates into use") quietly inherits use-as-good from the institution rather than interrogating it. A well-designed course requiring three deliberate visits per term and a badly designed one forcing daily hunting for materials would score in opposite directions on this scale. Ask the authors to state explicitly what use frequency is a proxy for, and to bound the Discussion accordingly — this is a framing-and-limitations fix, not a demand for a new study.
  2. **Actionability of the practice implication, and whether the design can bear it.** Section 5 offers onboarding-that-demonstrates-usefulness as a possible institutional lever (citing Whitfield, 2019 — a source introduced only in the Discussion and never set up in the literature review). From the seat that would actually fund that onboarding: a moderate cross-sectional correlation of unknown direction cannot distinguish "make students see usefulness → they use it more" from "required use → they retrospectively rate it useful," and the paper's own text concedes the reverse path is equally consistent. Press for the implication to be stated as a hypothesis worth testing rather than as an attention-worthy direction, and note that the residual variance the paper attributes to "course requirements and assessment schedules" points at instructor and assessment design as the more plausible lever — which the study does not measure.
  3. **The unasked institutional question, plus access as a confound.** Every institution running an LMS already holds complete behavioral logs for the exact construct this study approximated by self-report; the manuscript never explains why logs were not used or sought (an ethics/approval constraint would be a perfectly good answer, but it needs to be given). Separately, from a practitioner's field experience: low reported use frequently reflects device access, connectivity, commuting, and paid-work schedules rather than low perceived usefulness. With no demographic or access variables collected, perceived usefulness may be partly standing in for material conditions — an equity-relevant confound absent from Section 6.

**Will particularly care about**: What a decision-maker could legitimately do with this paper on Monday morning — and whether measuring clicks-as-perceived-by-students, rather than learning or access, embeds an instrumentalist assumption that the authors have not surfaced. This reviewer's distinctive value is challenging the *worth* of the outcome variable, which no other panel member is positioned to do.
**Possible blind spots**: Will not evaluate statistical execution, instrument psychometrics, or literature completeness, and may undervalue the paper's methodological restraint because it does not answer a decision question. Highest risk of the panel for scope creep — critiques 1 and 3 can slide into "run a different study with log data and demographics," which is future-research advice, not a revision. The synthesizer should convert these into framing, limitation, and justification requirements wherever the underlying study cannot be re-run.

---

## Review Strategy Recommendations

**1. The panel's dominant failure mode here is the false positive, not the miss.** This manuscript's claims are already matched to its evidence. Before any reviewer asserts overreach, they must quote the sentence that overreaches. The following criticisms are **pre-empted by the text** and must not be raised as findings unless a reviewer can quote a specific contrary claim:
- "Correlation does not imply causation" — disclaimed in the abstract, §1, §5 (with the reverse pathway named), §6, and §7.
- "Self-report is not behavior" — stated in §2 (with Vasquez, 2020), §3.2, §6, and §7.
- "Single institution limits generalizability" — stated in the abstract, §6, and §7.
- "r = .42 is weak / no effect size reported" — characterized as moderate, with a 95% CI, exact n, exact p, a Spearman robustness check, and explicit acknowledgment of unexplained variance in §4.
- "No power analysis / no assumption checks" — both present in §3.4.
- "Ethics not addressed" — §3.3 covers approval, voluntariness, anonymity, consent, and absence of incentives.

A reviewer who raises these anyway is reviewing a generic weak survey paper, not this one. Reviewers should be instructed to credit calibration explicitly where it is present, so the synthesizer can distinguish "the paper handles this" from "no one checked."

**2. The genuinely open issues, ranked by defensibility.** These survive scrutiny and should carry the report:
- (i) **No response rate or eligible-population denominator** — non-response bias is unquantifiable (R1, EIC).
- (ii) **Duplicate removal versus the anonymity claim** — 5 duplicates identified in a survey stated to collect no identifying information and to be unlinkable to individuals; an internal tension in §3.1/§3.3 requiring explanation (R1).
- (iii) **Recruitment channel possibly internal to the LMS** — selection conditioned on the dependent variable; §6 names the symptom, not the mechanism or its direction (R1, R3).
- (iv) **Single-item, unvalidated ordinal outcome** — attenuation of unknown magnitude; r = .42 is a lower bound (R1).
- (v) **Common-method variance** — same source, same instrument, same moment; undiscussed (R1).
- (vi) **Six references; no meta-analytic or post-TAM benchmark** — the claimed comparability to prior estimates is asserted, never quantified (R2).
- (vii) **Use frequency's construct relevance never argued** (R3).
- (viii) **Adapted instrument not documented or re-validated beyond α; full response-option wording missing** (R1).
- (ix) **Missing disclosure furniture**: participant-characteristics table, data availability, funding, COI, ethics approval reference (EIC).
- (x) **Contribution weight and article-versus-note format** (EIC, R2).

**3. Designed complementarity.** The four lenses are deliberately non-overlapping: EIC = journal fit, format, and disclosure policy; R1 = measurement and inferential validity; R2 = field-level novelty against specific prior literature; R3 = worth of the outcome construct, practice actionability, and equity. The one boundary needing enforcement is **EIC versus R2 on contribution**: the EIC decides fit, readership, and container (article vs. note); R2 decides novelty against named prior studies. If both simply write "the contribution is thin," the synthesizer should collapse them into one finding and preserve only the EIC's format recommendation and R2's specific literature gaps.

**4. Anticipated tension the synthesizer must arbitrate.** R1 will likely converge on major-but-fixable revisions (a reporting-and-disclosure package). R2 and R3 will each be tempted to demand a *different study* — R2 toward model-testing with moderators, R3 toward log data plus demographics. Neither is a revision of this manuscript. The synthesizer should route those to Future Research and hold both reviewers to what the existing data can support: clearer positioning, clearer bounding, clearer justification. Conversely, the EIC may lean toward decline-on-contribution while all three peer reviewers find the execution sound; that split is the substantive editorial question of this review and should be surfaced as such, not averaged away into "major revision."

**5. The strongest genuinely adversarial line — for the Devil's Advocate.** Not overclaiming (there is little to find) but **sufficiency and self-defeat**: does a manuscript whose central claim is that it offers one modest, bounded, non-causal coefficient, supported by six references, describe a contribution or concede its absence? Push further: the paper's honesty is partly *load-bearing* — extensive hedging in §5 and §6 substitutes for design features that would have removed the need to hedge (log data, a second institution, a validated multi-item outcome), several of which were plausibly available at low cost. The sharpest version of the challenge is that exemplary calibration about a weak design is not the same as a strong study, and that the panel should not let epistemic virtue purchase a publication recommendation on its own.

**6. Register and language.** Maturity is pre-submission, so the register is *polish and disclose*, not developmental scaffolding — reviewers should write to an author who understands inference and needs specific, actionable items. The manuscript is in English; all reviews, the synthesis, and the recommendation are to be written in English. Per calibration discipline, register governs wording only: whatever tone each reviewer adopts, the recommendation must follow from the evidence against the criteria, and no reviewer's verdict may soften or harden because the paper is pleasant to read.

# PART 2 — SEATS

## SEAT — EIC

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor.** From the editorial chair, this dimension asks whether the study's design and its evidentiary machinery clear the bar my journal's readers would apply before they trust a number. For a cross-sectional survey in educational technology, that means the sampling frame and recruitment route are stated well enough that a reader can judge who the respondents represent, the instrument's provenance and reliability evidence are disclosed, response and completion rates are reported rather than implied, and any inferential statistics arrive with effect sizes, uncertainty intervals, and the assumptions they rest on. I am not the seat that audits the arithmetic — that is Reviewer 1's technical work — but I am the seat that decides whether the reporting is complete enough that the paper's conclusions could survive editorial scrutiny at all. Reproducibility affordances (instrument availability, item wording, data or analysis-script access) matter here as an editorial condition of publication, not as a methodological nicety.

**D2 — domain_accuracy.** This dimension asks whether the manuscript is a competent citizen of its own literature. LMS adoption and student engagement is a field with a long, dense theoretical spine — technology acceptance and its successors, engagement constructs with contested operationalisations, decades of self-report-versus-log-data debate — and an editor's first job is to check that the paper knows where it stands in that spine. I look for whether constructs are used with their established meanings rather than redefined silently, whether cited prior work actually says what the manuscript claims it says, whether the empirical picture presented as settled is in fact settled, and whether the currency of the evidence base matches a field that has moved substantially in the last several years. Misrepresenting the field is an editorial hazard distinct from a methodological one: it damages the journal's standing with the readers who know the literature best.

**D3 — argumentative_coherence.** Here I read the paper as a single chain and ask whether it holds under tension from title to conclusion. The research question stated in the introduction must be the question the design can answer, the design must produce evidence of the kind the discussion then invokes, and the conclusion must claim no more than that evidence licenses. In a cross-sectional self-report design the standing hazard is the slide from association to causation or to behavioural fact — "perceived usefulness" and "self-reported use" are both perceptions, and any language that converts them into demonstrated effects on actual usage or learning breaks the chain. I also watch for the over-promise pattern: a title or abstract that pledges more scope than the body delivers. This is the dimension where my bird's-eye vantage is most diagnostic, because incoherence is usually visible only across sections, not within any one of them.

**D4 — cross_disciplinary_relevance.** My journal's readership is not confined to one methodological tribe, so this dimension asks whether an intelligent reader from an adjacent field — instructional design, higher-education policy, information systems, learning analytics — can enter the paper, understand what was done, and extract something usable. That requires constructs defined on first use rather than assumed, an institutional and technological context specific enough that a reader can judge transfer to their own setting, and implications that are stated at a level a non-specialist could act on. Where the paper reaches across disciplinary lines to borrow a framework or claim relevance to another field's problems, that reach must be substantiated rather than asserted. Note that the contract marks this high priority, not mandatory: a paper can be narrow and still publishable, but a paper that overclaims its reach is a different and more serious matter.

**D5 — writing_and_structure.** This is the dimension where I assess whether the manuscript is fit to be read as a member of my journal's article types. Organisation should follow the conventions the readership expects, exposition should be clear enough that the argument's load is carried by its content rather than by the reader's reconstructive effort, and tables and figures should be self-contained and honestly labelled. The 1,597-word length is itself an editorial datum I must weigh under this dimension: it sits far below the length of a standard empirical article in this field, and I will need to determine whether the paper is being submitted as a short-form or brief-report article type where that length is appropriate, or whether the compression has cost the manuscript reporting elements the venue requires. The contract marks this dimension normal priority, so it cannot by itself drive a failure condition — but it can and does shape my editorial commentary.

## Scoring Plan

### D1: methodology_rigor

- `what_to_look_for`: A stated sampling frame and recruitment method with the target population identified; sample size with response and completion rates; the instrument's origin (adapted from a named validated scale versus author-constructed) with item wording available or referenced; reliability evidence for each multi-item construct; explicit statement of how "self-reported use" was measured (frequency scale, recall window, anchors); the analysis actually run, with effect sizes and uncertainty, not p-values alone; a limitations passage that names the design's own constraints (single time point, single institution, common-method variance, self-report as proxy for behaviour); any statement about data, instrument, or code availability; ethics approval and consent for human-subjects research.
- `what_triggers_block`: The manuscript reports empirical results while omitting the information a reader needs to judge whether those results mean anything — for instance, quantitative findings presented with no sample size or no description of who was surveyed and how they were recruited; a survey instrument with no provenance and no reliability evidence for its constructs; inferential or relational claims with no reportable statistics attached; or the absence of any human-subjects ethics statement for a study surveying students. Any one of these is a standalone block, because it makes the reported evidence editorially unusable regardless of how the analysis was conducted.
- `what_triggers_warn`: The core reporting elements are present but materially thin or partially disclosed — for example, sample size and recruitment stated but response rate absent so self-selection cannot be assessed; reliability reported for some constructs but not others; statistics reported without effect sizes or intervals; a limitations section that exists but omits the design's most consequential constraint; no reproducibility affordance offered where the field increasingly expects one. Warn is the score when a reader could reconstruct roughly what was done but could not judge how well.

### D2: domain_accuracy

- `what_to_look_for`: Whether "perceived usefulness" is used in its established technology-acceptance sense with attribution, or borrowed loosely; whether "engagement" and "use" are distinguished as the separate constructs the literature treats them as; whether cited works are characterised accurately and support the specific claim they are attached to; the recency and range of the evidence base, and whether it includes the field's post-2020 shift in LMS usage conditions; whether contested findings in the LMS-adoption literature are presented as contested rather than settled; whether the gap the paper claims to fill is genuinely open given what is cited; whether LMS-specific and higher-education-specific terminology is used correctly.
- `what_triggers_block`: A load-bearing claim rests on a demonstrable misrepresentation of prior work or of an established construct — a cited source characterised as showing something it does not, a canonical framework's terms redefined in a way that inverts their meaning while retaining the citation, or a factual assertion about the domain that the field's evidence contradicts. Also blocking: the paper's central novelty claim is falsified by literature the paper itself cites or by work so central to LMS adoption that its absence signals the argument was built without engaging the field.
- `what_triggers_warn`: The domain engagement is present but shallow or dated — a literature base that is thin for the claim being made, citations skewed to a narrow window or a single strand, a construct used correctly but without attribution to the framework it comes from, or an evidence claim stated more confidently than the cited work supports. Warn also applies where a genuinely contested question is narrated as consensus without acknowledging the dissenting line.

### D3: argumentative_coherence

- `what_to_look_for`: Whether the research question stated in the introduction is answerable by a cross-sectional survey design and is the question actually answered by the results; whether the language describing the relationship between perceived usefulness and self-reported use stays associational throughout, including in the abstract and conclusion where compression most often breeds overreach; whether "self-reported use" is consistently treated as report rather than silently converted to actual use or to learning outcome; whether the conclusion's scope of generalisation matches the sample's scope; whether the title and abstract promise what the body delivers; whether recommendations to practice or policy follow from the findings or arrive unsupported.
- `what_triggers_block`: The central argument breaks — the conclusion asserts a causal or directional effect that a single-time-point correlational design cannot establish, and this causal reading is load-bearing rather than an isolated phrasing slip; or the paper answers a materially different question than the one it poses; or the conclusion contradicts the results it reports; or self-reported use is treated as established behavioural fact and the paper's contribution depends on that conversion. Block is the score when removing the unsupported inferential step would leave the paper with no stated contribution.
- `what_triggers_warn`: The chain holds but leaks at identifiable points — causal verbs appear in the abstract or discussion while the results section stays properly associational; the conclusion generalises somewhat beyond the sampled population without flagging it; implications are stated more strongly than the effect magnitudes justify; the stated research question is broader than what is answered but the answered question is still a legitimate part of it. Warn is the score when the unsupported steps are correctable by revision without dismantling the contribution.

### D4: cross_disciplinary_relevance

- `what_to_look_for`: Whether the constructs are defined on first use in terms an adjacent-field reader would follow rather than assumed as insider vocabulary; whether the institutional setting, LMS platform, student population, and disciplinary context are described concretely enough for a reader elsewhere to judge transferability; whether the framing connects to problems adjacent fields recognise (instructional design, higher-education policy, information systems, learning analytics) rather than speaking only to LMS-adoption specialists; whether implications are actionable at a level a non-specialist could use; whether any claim of relevance beyond the immediate sub-field is substantiated by the evidence presented rather than asserted in the discussion.
- `what_triggers_block`: The paper asserts substantive interdisciplinary reach — that its findings bear on learning outcomes, on institutional policy, on a named adjacent discipline's problems — and offers nothing that could support it: no measure of the outcome claimed, no data from the setting invoked, no argument connecting what was measured to what is claimed to follow. Unsubstantiated interdisciplinary overclaim is what the contract makes blockable at this priority level, not narrowness itself.
- `what_triggers_warn`: The work is legible mainly to its own sub-field — constructs used without definition, context described too thinly for a reader to judge transfer, implications addressed only to LMS researchers, or a discussion that gestures at broader relevance without developing it. A paper that is honestly narrow and says so lands at warn or pass depending on how self-aware the framing is; a paper that is narrow while implying breadth lands at warn.

### D5: writing_and_structure

- `what_to_look_for`: Whether the manuscript follows the sectional conventions its article type requires and whether the 1,597-word length is consistent with a declared short-form or brief-report submission or represents under-development of a standard empirical article; whether each section carries its expected content or has been compressed to a placeholder; whether tables and figures are self-contained, correctly labelled, consistent with the text, and not merely restating it; whether the abstract is a faithful and complete miniature of the paper; whether the prose is clear enough that the argument is carried by the writing rather than reconstructed by the reader; whether referencing is complete and internally consistent.
- `what_triggers_block`: The manuscript is not readable as a scholarly article in the venue's terms — sections missing or reduced to fragments such that the study cannot be followed end to end, tables or figures that contradict the text or are uninterpretable as presented, or an abstract that misdescribes what the paper reports. I note that this dimension is `normal` priority and therefore cannot itself fire F1 or F3; a block here signals to the synthesizer that presentation alone would bar publication in its current form, and I will say so in prose rather than expecting the score to carry the decision.
- `what_triggers_warn`: The paper is followable but its presentation costs the reader — sections present yet visibly thin relative to what the claims require, an abstract that under-reports the results, tables that duplicate rather than complement the text, uneven or unconventional organisation for the venue, or referencing and formatting inconsistencies frequent enough to distract. Given the stated word count, a length materially below the venue's norm without an evident short-form article type is by itself sufficient for warn here.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## EIC Review Report

### Reviewer Identity

Editor-in-Chief of *Education and Information Technologies*, a mainstream high-volume educational-technology journal; former Associate Editor with portfolio responsibility for technology-acceptance submissions. I handle roughly forty LMS-perception manuscripts a year and have written publicly about this journal's desk-rejection criteria for single-site acceptance surveys. My seat evaluates fit, contribution weight, container (article versus note), structural coherence across the whole manuscript, and journal-policy disclosure. I do not audit the statistics or the psychometrics; those belong to Reviewer 1.

### Overall Recommendation

**Major Revision** — with an explicit invitation to resubmit in a shorter container (brief report / research note) rather than as a full research article. The revision I am asking for is one of positioning, disclosure, and description. I am expressly **not** asking the authors to add a theoretical model, moderators, log data, or a second institution; those would be a different study, and the paper's decision to decline model-testing is defensible and should be preserved.

### Confidence Score

**5** — Journal fit, article-type decisions, contribution weight against this readership's corpus, and publication-policy disclosure are the core of my editorial remit, and this submission type is the single most frequent one crossing my desk.

### Summary Assessment

This is a cross-sectional survey of 214 undergraduates at one mid-sized public university, reporting a single bivariate association between perceived usefulness of the institutional LMS and a self-reported LMS access-frequency item (r = .42, 95% CI [.30, .52], p < .001), with a Spearman robustness check. What it does, it does with unusual discipline. The claims are matched to the evidence rather than stretched past it: causality is disclaimed in the abstract, introduction, discussion, limitations, and conclusion; the reverse pathway is named as equally consistent; self-report is framed as perceived rather than actual use with a supporting citation; the single-site bound is stated three times. The reported numbers are internally consistent across abstract, results, discussion, and conclusion. Ethics approval, consent, voluntariness, and absence of incentives are all reported.

The editorial problem is not overreach, and reviewers should not manufacture one. It is weight and placement. The manuscript's stated contribution is to be "one point in a distribution" of comparable estimates — but the distribution is never shown, no competing coefficient is quoted, the evidence base is six sources with nothing after 2021, and the setting is described too thinly for any reader to place this estimate against another. On top of that sit the journal's standard gatekeeping omissions: no response rate, no eligible-population denominator, no participant table, and no data-availability, funding, or conflict-of-interest statements. Sound execution, under-delivered positioning, and a container mismatch.

### Strengths

1. **Claims are calibrated to the evidence throughout, not only in the limitations section**: the non-causal bound is carried in every section where compression usually breeds overreach, including the abstract and conclusion. This is rarer than it should be in this submission stream and I credit it explicitly so the panel can distinguish "the authors handled this" from "nobody checked."
   - **Evidence Anchor**: `text: §5, "the correlation cannot establish that perceived usefulness causes use; the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"`

2. **The inferential reporting package is complete by this journal's standards**: point estimate with a 95% confidence interval, exact *n*, exact *p*, a distribution-free robustness check, an a-priori-style sensitivity statement, and an explicit acknowledgment that most variance in reported use is unaccounted for.
   - **Evidence Anchor**: `text: §4, "r = .42, 95% CI [.30, .52], p < .001, n = 214. The Spearman robustness check yielded a comparable coefficient (ρ = .40)"`

3. **The six sources, though far too few, are well chosen**: they name the three cautions that actually bear on this design — reverse causality (Delgado, 2020), self-report/log divergence (Vasquez, 2020), and between-site variability of the estimate (Song, 2018). This is not the citation profile of an author who ignored the field; it is one who engaged it narrowly.
   - **Evidence Anchor**: `text: §2, "self-reported estimates of technology use diverge, sometimes substantially, from behavioral log data"`

4. **Human-subjects reporting is substantively complete**: ethics-committee review and approval, voluntary participation, anonymity, informed consent at the landing page, and explicit absence of incentives.
   - **Evidence Anchor**: `text: §3.3 (protocol, consent, voluntariness, anonymity, no incentives)`

5. **Organisation and prose meet the journal's baseline without editorial intervention**: conventional IMRaD-plus-limitations sequence, no register slippage, uniformly formatted references with DOIs, and the headline coefficient stated identically in the abstract, results, discussion, and conclusion.
   - **Evidence Anchor**: `text: §§1–7 section sequence; r = .42 reported identically in Abstract, §4, §5, §7`

### Weaknesses

1. **The paper's own contribution claim is asserted rather than delivered.** The manuscript positions itself as "an incremental data point, comparable with prior work" and as one point in the distribution Song (2018) documents. Comparability is a testable promise, and the manuscript does not keep it: not one prior coefficient is quoted, no meta-analytic or pooled benchmark is invoked, and the reader is never told whether r = .42 sits at, above, or below the published range. As it stands the comparison is a qualitative gesture ("consistent with prior technology-acceptance research"). **Improvement**: quote three to six comparable published coefficients with their samples and instruments, and state where this estimate falls relative to them. This is the single highest-value revision in the paper and requires no new data.
   - **Severity**: Major | **Evidence Anchor**: `text: §2, "It is intended as an incremental data point, comparable with prior work"` | **Confidence**: 5 — this is the exact claim my seat is required to test against the journal's existing corpus.

2. **Journal-policy disclosure items are missing.** Absent, and required before this manuscript could publish here: response rate and the eligible-population denominator (§3.1 states all undergraduates were eligible but never says how many that is, so voluntary-response bias cannot be sized by any reader); a participant-characteristics table; the ethics approval reference number, given that approval is claimed; and data-availability, funding, and conflict-of-interest statements. The adapted instrument's item wording and full response-option anchors are also unavailable, which blocks both replication and the comparability claim in W1. **Improvement**: add the standard end-matter statements, the denominator and response rate, a demographics table, and the instrument as an appendix or deposited file.
   - **Severity**: Major | **Evidence Anchor**: `absence: checked §3.1 (sampling/denominator), §3.2 (instrument wording/anchors), §3.3 (approval reference), §3.4 (analysis), post-§7 end matter, and References — none present` | **Confidence**: 5 — these are this journal's published submission requirements.

3. **The setting is described too thinly for either transfer or comparison.** "One mid-sized public university" is the whole of it. The LMS platform is never named, nor the country or system, delivery mode (in-person, blended, fully online), disciplinary mix, or the period of data collection. A reader in instructional design, learning analytics, or higher-education policy cannot judge whether this finding travels to their setting, and — more damaging to the paper's own case — cannot place this estimate against another study's, which is precisely what W1's contribution claim requires. **Improvement**: name the platform, the national/sectoral context, the delivery mode, the disciplinary composition, and the collection window.
   - **Severity**: Major | **Evidence Anchor**: `text: §3.1, "This was a cross-sectional survey study conducted at one mid-sized public university."` | **Confidence**: 5 — judging transferability from setting descriptors is routine editorial work at this journal.

4. **The abstract's closing sentence widens the construct beyond what was measured.** The outcome is a single self-reported item on how often a respondent accessed the LMS in a typical week. The abstract concludes that "perceived usefulness tracks with LMS *engagement*," and §5 speaks of "one of several factors bearing on engagement." Engagement in this literature is a multidimensional construct; self-reported access frequency is a thin proxy for one of its facets. The manuscript's operational language is otherwise consistently correct ("self-reported frequency of use"), which is exactly why the slide in the most-read sentence of the paper matters. **Improvement**: replace "engagement" with "self-reported frequency of access" wherever the paper's own finding is being restated, and reserve "engagement" for characterising prior work that measured it. This is a one-to-two-sentence fix, and I flag it so the synthesizer does not inflate the revision burden.
   - **Severity**: Major | **Evidence Anchor**: `text: Abstract, "The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates."` | **Confidence**: 5 — title-to-abstract-to-body scope consistency is a first-pass editorial check.

5. **The published ethics statement is internally inconsistent and cannot go to press as written.** §3.1 reports that "5 duplicate entries were removed"; §3.3 states that "No identifying information was collected, and responses could not be linked back to individual students." A journal is accountable for the accuracy of the ethics and anonymity statements it prints. I am not evaluating the deduplication technique — that is the methodologist's call — but I do require the two passages to be reconciled in the manuscript. **Improvement**: state what fields or signals were used to identify duplicates and revise §3.3 so the anonymity claim is precise (e.g. pseudonymous session or response-level metadata retained without identifiers), or explain the reconciliation if no such data existed.
   - **Severity**: Major | **Evidence Anchor**: `text: §3.1, "5 duplicate entries were removed" vs. §3.3, "responses could not be linked back to individual students"` | **Confidence**: 4 — editorial handling of ethics-statement accuracy, not survey-platform forensics.

6. **Presentation is under-built for a quantitative submission.** There is not a single table or figure: no participant table, no descriptives table, no correlation table, and no scatterplot — despite §3.4 reporting that "Scatterplot inspection showed an approximately linear, monotonic association," an assertion the reader is asked to take on trust. Whitfield (2019) is introduced for the first time in the Discussion and never set up in the Literature Review, which leaves the paper's only practice implication resting on an unframed source. At roughly 1,540 words of body text, the manuscript is well below this journal's research-article norm, and no article type is declared anywhere. **Improvement**: add a descriptives/correlation table and the scatterplot; move Whitfield into §2; and declare the intended article type (see Journal Fit).
   - **Severity**: Minor | **Evidence Anchor**: `absence: no table or figure appears anywhere in §§1–7; scatterplot referenced at §3.4 but not presented` | **Confidence**: 5 — presentation conventions for this journal's empirical articles.

### Detailed Comments

#### Journal Fit

Topically this is squarely within scope; single-institution correlational LMS-acceptance work is a submission type this journal publishes regularly. The mismatch is **container, not topic**. One bivariate coefficient, one site, six references, and no table or figure is not a full research article for this readership — it is a research note. I want to be exact about why, because the reasoning is easy to misstate: I am not declining the work for being small, and I am not treating the authors' modesty as an admission. The problem is that the manuscript's *own* contribution claim (a comparable point in a distribution) is a claim only a paper with comparative positioning and setting descriptors can cash, and this one currently supplies neither. Fix W1, W2, and W3 and the note becomes genuinely useful to this audience: a clean, transparently bounded estimate a meta-analyst or a subsequent author can actually use.

My recommendation is therefore explicit: **resubmit as a brief report / research note**, with the positioning and disclosure package added. If the authors want the full-article container instead, the price is a substantially deeper literature base and a developed comparative section — not a redesigned study.

I will also state plainly the tension my seat is required to resolve rather than duck. The manuscript's epistemic honesty is real and I have credited it in five separate strengths. But calibration is a property of the *reporting*, not of the *contribution*. A precisely described small finding is still a small finding, and "we offer this as a modest, incremental, design-bounded data point" describes the size of the contribution — it does not substitute for one. The correct editorial response is to give the finding a container that fits it, not to let its honesty purchase a full-article slot, and not to punish the honesty by treating it as a confession.

#### Originality

The source of originality here is new data, not new method, framework, or perspective — and the authors say so. That is an acceptable basis for a note. What it cannot support without W1's revision is the claim of *comparability*, which is the paper's stated reason for existing. At present a reader finishing §7 knows this estimate exists but not what it adds. Note also that no cited source postdates 2021, the TAM lineage supplying the paper's central construct is never named (the definition in §2 is the canonical one, attributed only to a secondary source), and no meta-analytic benchmark is invoked. Reviewer 2 will have the field-specific list; from my seat the editorial point is narrower: the paper borrows a framework's central construct while declining the framework, and it owes the reader one paragraph justifying that use.

#### Significance

Local rather than broad. If the finding holds, the field gains one more estimate consistent with an already crowded set — valuable for cumulative purposes, unremarkable individually. The practice implication in §5 (onboarding that demonstrates concrete usefulness) is the paper's reach toward institutional readers, and I want to record that it survives my block test: it is offered as a possibility, explicitly labelled "suggested by, not proven by, the present correlation," and attached to a source. That is a hedged conjecture, not an unsubstantiated interdisciplinary claim, and it should not be attacked as overreach. It would be strengthened by being stated as a hypothesis worth testing.

#### Structural Coherence

Strong. The research question posed in §1 is narrow, answerable by the design, and is the question actually answered in §4 and restated in §7. The conclusion does not exceed the results. The reported coefficient is identical in all four places it appears. The single break in the chain is W4's construct widening in the abstract's closing sentence and §5's "factors bearing on engagement" — identifiable, quotable, and correctable without touching the contribution.

#### Title & Abstract

The title is accurate and appropriately narrow; it promises exactly what the body delivers and I would not change it. The abstract is a faithful miniature except in two respects: it omits the confidence interval that the body reports (a small loss for a paper whose main virtue is reporting precision), and its final sentence commits the construct widening in W4. It is unstructured single-paragraph at ~140 words, which is acceptable here but short of the journal's preferred structured form.

#### Conclusion

Appropriately scoped and correctly bounded, and the future-research direction it names (log data, longitudinal and multi-institution designs) is the right one. Its weakness mirrors the paper's: "consistent with prior work" is asserted without a single comparison, so the conclusion inherits W1 unresolved.

### Questions for Authors

1. How many undergraduates were eligible, and what was the response rate? Without the denominator the voluntary-response caveat in §6 cannot be sized by any reader.
2. Was the course-announcement channel used for recruitment delivered inside or through the LMS itself? If so, recruitment was conditioned on the outcome variable, and §6's statement about over-representation should name that mechanism and its likely direction rather than gesturing at it.
3. How were the five duplicate entries identified, given §3.3's statement that no identifying information was collected and responses could not be linked to individuals? Please reconcile these two passages.
4. Which published perceived-usefulness/use coefficients do you regard as the comparison set, and where does r = .42 fall relative to them?
5. Which LMS platform, in which national and institutional context, over what collection period, and with what disciplinary composition of respondents?
6. Do you wish this considered as a research note or as a full research article? If the latter, what do you see as justifying the longer container?
7. What licenses the use of the perceived-usefulness construct while declining the acceptance framework it comes from? One paragraph would settle it.

### Minor Issues

- The abstract omits the 95% CI reported in §4; include it.
- Whitfield (2019) appears only in §5; introduce it in §2 or drop the implication's citational support.
- §4's median use category, "a few times per week," is not one of the two anchors given in §3.2; report the full response-option wording.
- "Analyses were conducted at a conventional significance threshold" (§3.4) is vague where the rest of the section is precise — state α explicitly.
- Consider the journal's structured-abstract format.
- Standardise on one term for the outcome across title, abstract, and body (see W4).

---

contract_role: eic

## Dimension Scores

### D1: methodology_rigor
score: warn

Applying my committed Phase 1 triggers: none of my block conditions is met — sample size and recruitment route are stated, the instrument's provenance is named with reliability evidence for the multi-item scale, the relational claim arrives with a full statistical package, and a human-subjects ethics statement is present. My warn conditions are met on four counts: recruitment stated but response rate and eligible-population denominator absent, so self-selection cannot be assessed; reliability reported for the predictor but not the outcome; no reproducibility affordance (no data-availability statement, no item wording, no adaptation documentation); and the limitations section, while present and honest, names the symptom of voluntary-response bias without its mechanism. Scored at the editorial-completeness level my seat owns, not as a technical audit.

### D2: domain_accuracy
score: warn

No block condition fired: I found no misrepresented source, no inverted construct, and no factual domain error; the four substantive citations are characterised consistently with what they claim to report, and the novelty claim is not falsified by the paper's own citations. Warn fires on my committed pattern of thin-and-dated engagement: six sources for a topic with hundreds of directly relevant studies, nothing after 2021, the TAM lineage supplying the central construct never named, no meta-analytic or pooled benchmark, and — the load-bearing instance — an evidence claim (comparability with prior estimates) stated more confidently than anything cited actually supports, since no competing coefficient appears anywhere.

### D3: argumentative_coherence
score: warn

I tested every block condition I committed to and none fired: no causal assertion anywhere, including abstract and conclusion; self-reported use never converted into behavioural fact; the question posed is the question answered; the conclusion does not contradict the results. I record explicitly that the standard criticisms of this design (correlation-causation, self-report-as-behaviour, single-site generalisation, missing effect size) are pre-empted in the text and must not be raised as findings. Warn fires on the narrower committed pattern of an identifiable, correctable leak: the abstract's concluding sentence and one Discussion sentence restate the finding in terms of "engagement" when the measure is a single self-reported access-frequency item. This is the thinnest of my three mandatory warns and the most easily discharged — two sentences — and I note it does not change my decision, which F2 would produce from D1 and D2 alone.

### D4: cross_disciplinary_relevance
score: warn

Block did not fire, and the candidate was tested directly: §5's onboarding implication is the paper's reach toward institutional practice, but it is offered as a possibility, cited, and explicitly labelled as suggested rather than proven, so it is not the unsubstantiated interdisciplinary assertion my block condition requires. Warn fires on context: the setting is described only as "one mid-sized public university," with no platform, country, sector detail, delivery mode, disciplinary mix, participant characteristics, or collection period, which leaves an adjacent-field reader unable to judge transfer — and, more consequentially, undercuts the paper's own claim to be a comparable point in a distribution.

### D5: writing_and_structure
score: warn

Block did not fire: the study can be followed end to end, no table or figure contradicts the text, and the abstract does not misdescribe what the paper reports. Warn fires on my committed length trigger — roughly 1,540 words of body text with no declared short-form article type is by itself sufficient — compounded by the complete absence of tables and figures in a quantitative submission (including the scatterplot §3.4 relies on), and by Whitfield (2019) entering only in the Discussion without literature-review setup. This dimension is `normal` priority and cannot itself drive a failure condition; I record it as editorial commentary and it is reflected in my container recommendation rather than in the decision.

## Failure Condition Checks

### F1
fired: false

Predicate: any mandatory dimension scores `block`. My mandatory dimensions are D1 = warn, D2 = warn, D3 = warn. No block. Evaluated against my own scores only.

### F2
fired: true

Predicate: two or more mandatory dimensions score `warn` or worse. Three do — D1, D2, and D3. This is the highest-severity condition fired from my seat (severity 70) and therefore governs my decision. Evaluated against my own scores only; the `majority` quantifier is panel-level machinery for the synthesizer, not mine to apply.

### F3
fired: false

Predicate: any high-priority dimension scores `block`. D4 is the only high-priority dimension and scores warn, not block — the interdisciplinary reach the paper does make (§5's onboarding implication) is hedged and cited, which is what kept it off block.

### F0
fired: false

Predicate: every mandatory dimension scores `pass`. None does.

## Review Body

From the editorial chair, this manuscript presents a clean version of a hard problem: the execution is sound and the epistemic conduct is better than most of what reaches my desk in this submission stream, while the contribution is thin and its stated value is not yet delivered. I want the panel record to be unambiguous on both halves, because the two are easy to trade off against each other and neither should be.

On the first half: the authors have matched their claims to their evidence in every section where compression normally produces overreach. Causality is disclaimed five times, the reverse pathway is named as equally consistent, self-report is framed as an indicator of perceived rather than actual use with a supporting citation, the single-site bound is stated in the abstract, the limitations, and the conclusion, and the coefficient is reported with a confidence interval, an exact *n*, a distribution-free robustness check, and an acknowledgment that most variance is unaccounted for. Ethics approval, consent, voluntariness, and non-incentivisation are all reported. I tested each of the standard criticisms of this design against the text and found every one of them pre-empted; a reviewer who raises them is reviewing a generic weak survey rather than this manuscript, and I have recorded them as handled rather than unchecked.

On the second half: the manuscript's own account of why it should exist is that it supplies a comparable data point in a distribution of published estimates. That is a promise about the field, and it is not kept. No competing coefficient is quoted anywhere. No meta-analytic or pooled benchmark is invoked. The evidence base is six sources with nothing later than 2021, and the framework supplying the paper's central construct is never named. Worse for the promise specifically, the setting is described so thinly — one mid-sized public university, no platform, no country, no delivery mode, no disciplinary mix, no collection period, no participant table — that no reader could place this estimate against another even if the comparison set were named. Layered on top are the journal's ordinary gatekeeping omissions: no response rate, no eligible-population denominator, and no data-availability, funding, or conflict-of-interest statements. Separately, the printed ethics statement is internally inconsistent — five duplicate entries were removed from a survey stated to collect no identifying information — and a journal cannot publish an anonymity claim it has not reconciled.

The tension my seat must resolve, rather than praise and duck, is whether the authors' calibration earns the paper a place. It does not, by itself. Calibration is a property of the reporting; it describes how honestly the contribution has been sized, not how large it is. But the inverse error would be worse: treating the authors' own modesty as a confession and declining on that basis. The right editorial action is to give the finding the container that fits it — a brief report or research note — and to require the positioning, description, and disclosure package that would make it genuinely usable by the next author or meta-analyst. Everything I am asking for can be written from data already in hand. I am explicitly not asking for a theoretical model, moderators, log data, or a second site; the decision to decline model-testing is coherent and should survive revision, and I would regard a revision that added those as a different paper rather than a responsive one.

Three mandatory dimensions score warn under the triggers I committed to before seeing the manuscript, none scores block, and the high-priority dimension is warn rather than block because the paper's one reach toward institutional practice is hedged and cited. F2 is the highest-severity condition fired from my seat and supplies the action below. I flag for the synthesizer that my D3 warn rests on a single quotable construct slide in the abstract and is the lightest of the three; the decision would be identical without it.

## Editorial Decision

editorial_decision=major_revision

---

## SEAT — Peer Reviewer 1 (Methodology)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor.** From a methodology seat, this dimension asks whether the study's design, data handling, statistical reporting, and reproducibility affordances would survive scrutiny by a competent methodologist in educational technology. For a cross-sectional survey of undergraduates on LMS perceived usefulness and self-reported use, that means: an explicitly named design with its inferential ceiling acknowledged; a sampling frame, recruitment route, response rate, and non-response consideration that let a reader judge who the respondents represent; instruments with reported reliability and validity evidence rather than assertion; analyses matched to the measurement level of the data with assumptions checked; effect sizes and interval estimates alongside any *p*-values; missing-data amount and handling stated; and enough procedural detail — items, scoring, ethics approval, data/code availability — that an independent team could rerun the study. Because both focal constructs are self-reported and measured at one time point, common-method variance and the impossibility of temporal ordering are core rigor questions here, not stylistic quibbles.

**D2 — domain_accuracy.** My reading of this dimension stays inside my seat: I judge accuracy only where it is methodological accuracy — whether measurement constructs are used with their established technical meaning, whether statistics and psychometric quantities are named and interpreted correctly, and whether borrowed instruments or analytic conventions are described as their sources actually define them. Whether the paper fairly represents the LMS-adoption and technology-acceptance literature, and whether its substantive domain claims match current evidence, belongs to Reviewer 2; I will not score that content. A methodology-side block here means a construct or statistic is used in a way that is technically wrong, not merely under-cited.

**D3 — argumentative_coherence.** In methodology terms, coherence is the chain from research question to design to data to conclusion. I ask whether the stated question is answerable by the design chosen, whether every inferential claim is licensed by the analysis actually run, and whether the discussion stays at the level the data support. A cross-sectional correlational survey is a design that invites exactly the fallacies on my checklist: reverse causation, ecological or level-of-analysis mismatch, and over-inference from association to effect. Coherence fails methodologically when the conclusion is stronger, more causal, or more general than the evidence produced.

**D4 — cross_disciplinary_relevance.** I read this dimension narrowly and methodologically: can a reader from an adjacent field reconstruct what was done and judge its warrant without insider knowledge? That depends on whether the design label, measures, scale anchors, statistics, and their interpretations are defined at the point of use rather than assumed. Judging the substantive value of the work to adjacent disciplines is Reviewer 3's call; my contribution is whether the methodological account is legible and whether any claim of broader applicability rests on a sampling and design basis that could support it.

**D5 — writing_and_structure.** For me this is reporting completeness rather than prose quality. The question is whether the manuscript's Methods and Results are organised and specified well enough to be audited: a Methods section that carries participants, materials, procedure, and analysis plan; tables and figures with the *n*s, statistics, and precision needed to verify the numbers in the text; consistency between text, tables, and abstract; and adherence to reporting conventions such as APA 7.0 statistical formatting. I note that at 1,597 words this manuscript is short for an empirical survey report, so I will treat compression as a plausible cause of missing detail — but a reader cannot score rigor on detail that is absent, and I will record absence as absence rather than assume it was done and merely unreported.

## Scoring Plan

### D1: methodology_rigor
- **what_to_look_for**: An explicitly named design and its stated limits; population, sampling frame, recruitment channel, and sampling method (random vs. convenience) with sample size and response rate; any a priori power or precision justification; instrument provenance (adapted vs. original), item counts, response scale and anchors, and reported reliability (α/ω) and validity evidence for both perceived-usefulness and self-reported-use measures; how "use" was operationalised (self-report only, or triangulated against LMS server logs); analysis methods matched to the data's measurement level; assumption checks reported; effect sizes and 95% CIs accompanying every inferential test; missing-data amount and handling method; ethics approval/consent statement; data, item-bank, and analysis-code availability.
- **what_triggers_block**: Any of — no sampling method or sample size recoverable from the text, so the *n* and who it represents cannot be established; reliability/validity evidence absent for the focal measures with no source for adapted items; the reported analysis cannot be reconstructed at all (test not named, or named test incompatible with the described data); statistics reported that are internally impossible or mutually inconsistent (e.g., *df* irreconcilable with the stated *n*, correlations outside [-1, 1]); or evidence of a red-flag reporting pattern — uncorrected mass testing, only-significant results retained, or hypotheses that appear fitted after the fact.
- **what_triggers_warn**: The design is identifiable and the core analysis reconstructible, but material rigor affordances are thin or missing — e.g., effect sizes or CIs absent while *p*-values are reported; assumption testing unmentioned; response rate or non-response absent though the sampling route is described; missing data unaddressed; convenience sampling used without acknowledgment of its limits; single-source self-report used for both variables with no common-method-variance discussion; no ethics statement; no data/code availability statement; or no power/precision justification for the achieved *n*.

### D2: domain_accuracy
- **what_to_look_for**: Correct technical use of measurement and design vocabulary (reliability vs. validity, construct vs. indicator, "perceived usefulness" used as the established latent construct rather than a loose synonym for satisfaction); correct naming and interpretation of statistics (correlation vs. regression coefficient, variance explained, significance vs. magnitude); accurate description of any borrowed instrument's structure and scoring relative to its source; correct labelling of the design (a one-shot survey not described as quasi-experimental or longitudinal).
- **what_triggers_block**: A statistic or psychometric quantity is defined or interpreted incorrectly in a way that changes what the results mean — e.g., a reliability coefficient reported as validity evidence, *R²* or a correlation read as a proportion of respondents or as a causal effect, significance interpreted as effect magnitude — or an adapted instrument is described in a way its cited source contradicts (wrong dimensionality, wrong scoring direction, wrong anchors).
- **what_triggers_warn**: Terminology drifts without corrupting the result — constructs and their indicators used interchangeably, "generalisability" claimed loosely for a non-probability sample, "reliable" used colloquially, a design label imprecise but recoverable from the procedure, or instrument adaptation acknowledged without specifying what was changed.

### D3: argumentative_coherence
- **what_to_look_for**: A stated research question or hypothesis set that the chosen design can actually answer; alignment between the hypotheses stated up front and the tests reported; conclusions that stay associational when the data are cross-sectional; explicit acknowledgment that perceived usefulness and use cannot be temporally ordered here; discussion claims scoped to the sampled population; non-significant or unsupportive results carried through into the discussion rather than dropped; and limitations that name the design's real constraints rather than generic caveats.
- **what_triggers_block**: Causal or directional language load-bearing for the paper's conclusion or recommendations — perceived usefulness stated to *increase*, *drive*, *lead to*, or *cause* use on the strength of cross-sectional association; or practical/policy recommendations built on that causal reading; or a conclusion that contradicts the reported results (e.g., support claimed for a hypothesis whose test was non-significant, or a headline claim with no corresponding analysis anywhere in the paper).
- **what_triggers_warn**: The core inference stays associational but the framing overreaches at the edges — occasional causal verbs in abstract or discussion while the results section is properly hedged; generalisation to "students" or "higher education" beyond a single-institution or single-cohort sample; a limitations section that omits the design's central constraint (temporal ordering, common-method variance, or self-report validity of the "use" measure); or reported results discussed selectively without the full set being addressed.

### D4: cross_disciplinary_relevance
- **what_to_look_for**: Design, constructs, scale anchors, and statistics defined at first use so a reader outside educational technology can evaluate the warrant; the LMS platform, its institutional context, and what "use" concretely denotes specified rather than assumed; statistics interpreted in substantive units, not left as bare coefficients; any claim of relevance beyond the study setting backed by the sampling basis and design that would license it.
- **what_triggers_block**: The methodological account is unreconstructible by a competent outside reader because core procedure is undefined — the instrument, the response scale, or the analysis is referred to only by in-group shorthand or an uncited acronym, so no reader outside the immediate subfield can judge what was done or whether the numbers follow; or a claim of broad cross-context applicability is asserted from a sample and design that structurally cannot support it and no qualification appears anywhere.
- **what_triggers_warn**: The account is followable but assumes insider knowledge in places — undefined acronyms or platform-specific terms, scale anchors omitted, statistics reported without substantive interpretation, or transfer to other institutional contexts implied without stating the sampling and design conditions under which it would hold.

### D5: writing_and_structure
- **what_to_look_for**: A discernible Methods section carrying participants, materials, procedure, and analysis plan; Results organised so each stated hypothesis or question maps to a reported analysis; tables/figures that report *n*, the test statistic, *df*, exact *p*, effect size, and CI, with self-sufficient captions; numerical consistency across abstract, text, and tables; APA 7.0 statistical formatting (italicised symbols, leading zeros, decimal precision, *p*-value form); and a limitations subsection.
- **what_triggers_block**: No recoverable Methods section or reporting so disorganised that procedure and results cannot be told apart; or a direct contradiction between numbers in the abstract, text, and tables (different *n*, different coefficient, different significance) leaving no determinable value; or results referenced in the text that appear in no table, figure, or sentence anywhere in the manuscript.
- **what_triggers_warn**: Structure is present but reporting is incomplete or inconsistent in ways that impede verification — a table without *n* or *df*, a caption not self-contained, APA formatting errors in statistical notation, a missing limitations subsection, key procedural detail displaced into the discussion, or compression that leaves the analysis plan implied rather than stated (the 1,597-word length makes this the most likely warn path, but I will score on what is absent, not on why).

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Methodology Review Report (Peer Reviewer 1)

### Reviewer Identity

Associate Professor of educational measurement and psychometrics. Specialist in measurement error in self-reported behavior, the statistical behavior of single-item outcome measures, and correlation methods for ordinal data; published simulation work on attenuation and confidence-interval distortion when a continuous predictor is correlated with a coarse 5-category outcome; regular reviewer for measurement-oriented journals.

### Overall Recommendation

Major Revision

### Confidence Score

4

### Summary Assessment

This is a disciplined study whose inferential claims are already matched to its design, and I want to be explicit that the usual complaints about survey work in this area do not apply: causality is disclaimed and the reverse pathway is named, the single-site limit is stated repeatedly, an interval estimate and a sensitivity statement accompany the coefficient, assumptions are inspected rather than assumed, and ethics reporting is complete. I verified the two checkable numbers: the 95% CI [.30, .52] reproduces from *r* = .42 and *n* = 214 under Fisher's *z*, and the power statement reproduces at ≈ .80. Nothing here is internally impossible and nothing suggests selective reporting.

The manuscript's exposure is one level down, at the measurement layer, where the reporting is markedly thinner than the inferential prose. The outcome is a single unsourced 5-category self-report item with no reliability or validity evidence; both variables come from one respondent, one instrument, one sitting, and common-method variance is discussed nowhere; the adapted predictor scale is undocumented beyond α; the recruitment channel may be internal to the dependent variable; and there is no response rate, no denominator, and no participant description. The consequence is not that *r* = .42 is wrong but that its net measurement bias is of unknown sign and its precision is probably overstated. All of it is addressable in revision on the existing data, mostly by disclosure. The length of the list below reflects reporting surface, not design failure.

### Strengths

1. **Inferential calibration matched to the design**: causal language is withheld throughout and the competing pathway is stated, not merely conceded — "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data" (§5). From a methodology seat this is the manuscript's strongest feature. — **Evidence Anchor**: [`text`: §5]
2. **Interval estimate reported and internally correct**: *r* = .42, 95% CI [.30, .52], *p* < .001, *n* = 214 (§4). Recomputed under Fisher's *z* with *n* = 214, the interval is [.303, .525] — the reported bounds are right, and the same *n* and coefficient appear in the abstract, §4, §5, and §7 without drift. — **Evidence Anchor**: [`text`: §4, "r = .42, 95% CI [.30, .52], p < .001, n = 214"]
3. **A robustness check chosen for a stated reason, and read correctly**: Spearman ρ = .40 is computed *because* the use item is ordinal (§3.4), and the paper claims only that the association "did not depend on the parametric assumption" (§4) rather than treating it as a general vindication of the measure. — **Evidence Anchor**: [`text`: §3.4–§4]
4. **Assumption inspection reported, not assumed**: linearity, monotonicity, bivariate outliers, and distributional symmetry are each addressed specifically (§3.4). Thin on displayed evidence (see M4), but above the median for a short survey report. — **Evidence Anchor**: [`text`: §3.4]
5. **Sensitivity of the achieved sample stated quantitatively**: the paper says what *n* = 214 could detect (r ≥ .19 at α = .05, two-tailed, power > .80) instead of asserting adequacy (§3.4). — **Evidence Anchor**: [`text`: §3.4]
6. **Ethics reporting complete at the procedural level**: committee approval, voluntariness, anonymity, informed consent at point of entry, and explicit absence of incentives (§3.3). — **Evidence Anchor**: [`text`: §3.3]
7. **Case-attrition arithmetic auditable**: 233 received − 14 incomplete − 5 duplicates = 214 analyzed, stated as a chain (§3.1); the arithmetic checks. — **Evidence Anchor**: [`text`: §3.1]
8. **Explicit measurement humility about the outcome's status**: "We treat this as an ordinal indicator of self-reported use and interpret it accordingly" (§3.2), with the self-report/log divergence sourced (§2, Vasquez, 2020) rather than left implicit. — **Evidence Anchor**: [`text`: §3.2]

### Weaknesses

1. **No response rate and no eligible-population denominator**: §3.1 states that "All enrolled undergraduates were eligible" but never reports how many that was, so 233 invitations-answered cannot be converted into a response rate and non-response bias is unquantifiable. The problem is not the low rate a census invitation would likely produce — it is that the reader cannot bound who the 214 represent, which is the precondition for reading any single-site estimate. Report the enrolled-undergraduate *N* and the response rate; compare respondents against institutional enrollment distributions on whatever the registry holds (year level, faculty, sex); and label the sample explicitly as self-selected/non-probability, which the manuscript currently never does.
   - **Severity**: Major | **Evidence Anchor**: [`absence`: checked Abstract, §3.1, §4, §6 — no denominator or rate on any surface] | **Confidence**: 5 — survey non-response is core to my area.
2. **The recruitment channel may be conditioned on the dependent variable**: the survey was "distributed through the institution's course-announcement channel" (§3.1), and the manuscript never says whether that channel is inside the LMS, triggered by it, or independent of it. If announcements are LMS-delivered, exposure to the invitation is itself a function of the outcome variable, truncating the low-use tail. §6 registers the symptom — "students who engage more with institutional channels may be overrepresented" — but attributes it to voluntariness rather than to a delivery channel structurally correlated with the outcome, so the mechanism and its consequence go unnamed. Direction is not determinate: low-end truncation typically attenuates *r*, while selection on the joint high end of both variables would inflate it; either way the reported interval is conditional on an unspecified selection process. State exactly what the channel is; if LMS-delivered, name it as a threat with the mechanism; if multiple routes existed, report the proportion recruited by each.
   - **Severity**: Major | **Evidence Anchor**: [`text`: §3.1 "the institution's course-announcement channel"; §6] | **Confidence**: 4 — the mechanism is standard, but I cannot know this institution's channel architecture.
3. **Single-item ordinal outcome with no reliability or validity evidence, and a bias direction the paper does not resolve**: the predictor is six items with α = .88; the outcome is one 5-point item (§3.2) with no source citation, no reliability estimate — none is obtainable from a single item in one administration — and no validity evidence beyond the general self-report caution. Two consequences go unstated. First, random error in the outcome attenuates *r*, and the standard correction *r*/√(ρ*xx*·ρ*yy*) cannot be applied because ρ*yy* is unknown and unestimable from these data; coarsening into five ordered categories imposes a further ceiling on the observable Pearson coefficient. Second, common-method variance (W4) pushes the other way. The defensible statement is therefore not that .42 is a lower bound but that its **net measurement bias is of indeterminate sign** — and "moderate" (§4, §5) should be qualified in exactly those terms. The Spearman check deserves its credit but should be described for what it does: it addresses monotonicity and the parametric form of the coefficient, not unreliability, category coarseness, or shared method. Implementable on existing data: report the item's full frequency distribution; add a polyserial correlation, which models the ordinal outcome as a coarsened continuum; and present a disattenuation band across plausible ρ*yy* values (e.g. .60–.85) declared as an explicit assumption rather than a result.
   - **Severity**: Major | **Evidence Anchor**: [`text`: §3.2 "a single five-point frequency item"] | **Confidence**: 5 — single-item measures and attenuation are my published area.
4. **Common-method variance is not addressed on any surface**: both variables come from the same respondent, the same instrument, and the same sitting, so consistency motives, priming and item-order effects, and shared response style are candidate upward contributors to *r* = .42. §6's second limitation concerns self-report versus behavioral logs — that is criterion validity of the outcome measure, a different threat, and it does not cover same-source bias between the two variables. Name CMV in §6, state its direction alongside W3's attenuation, and conclude that the net bias on .42 is indeterminate. Report the item order (was perceived usefulness administered before the use item?), which is knowable and bears directly on the plausible magnitude.
   - **Severity**: Major | **Evidence Anchor**: [`absence`: checked §3.2, §3.4, §5, §6, Abstract — no mention of same-source or method bias] | **Confidence**: 5.
5. **Instrument adaptation undocumented and unre-validated beyond internal consistency**: §3.2 reports a "six-item scale adapted from Costa and Wren (2019)" without saying what was adapted — item wording, item count, referent platform, or response format — so a reader cannot judge whether the six retained items preserve the source instrument's construct coverage. α = .88 establishes internal consistency only; it is not evidence that the adapted set measures the construct the source validated, and no factor structure, item-total statistics, or convergent/discriminant evidence is given. Relatedly, "previously validated instrument" (Abstract, §2) is accurate about the source but is applied to the adapted version by inheritance. Supply the six items verbatim in an appendix with a change log against Costa and Wren; report item-level descriptives and at minimum item-total correlations (a single-factor CFA is feasible with *n* = 214); and rephrase to "adapted from a previously validated instrument."
   - **Severity**: Major | **Evidence Anchor**: [`text`: §3.2 "adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"] | **Confidence**: 5.
6. **Duplicate removal cannot be reconciled with the anonymity claim as written**: §3.1 removes "5 duplicate entries"; §3.3 states "No identifying information was collected, and responses could not be linked back to individual students." Detecting duplicates requires either quasi-identifying metadata (IP address, session cookie, device fingerprint, submission timestamp) — which contradicts "no identifying information" as a reader will understand it — or inference from response-pattern similarity, which can misclassify genuinely similar respondents and constitutes a substantive exclusion rule that should be pre-stated. Both sections cannot stand as written. State the detection rule, disclose any metadata captured and confirm the ethics approval covered it, and report a one-line sensitivity check (*r* with the 5 cases retained, *n* = 219, against *n* = 214).
   - **Severity**: Major | **Evidence Anchor**: [`text`: §3.1 "5 duplicate entries were removed"; §3.3 "responses could not be linked back to individual students"] | **Confidence**: 5.
7. **The independence assumption is unexamined, and the paper's own account of residual variance is the clustering mechanism**: respondents reached through a course-announcement channel are nested in courses, programmes, and year levels, and §4–§5 attribute unexplained variation to "course requirements and assessment schedules" — precisely the shared course-level influences that would induce intra-cluster correlation on both variables. No clustering identifier appears to have been collected and no cluster-robust or multilevel treatment is mentioned, so the reported CI [.30, .52] is likely narrower than the design warrants. This affects the precision of the estimate, not its sign. Because the existing data cannot support re-analysis, add nesting to §6 as a named threat to precision, and collect a course or programme identifier in any replication so a design-effect adjustment becomes possible.
   - **Severity**: Major | **Evidence Anchor**: [`absence`: checked §3.1, §3.4, §6 — no nesting, clustering, or design-effect consideration, against the mechanism the authors themselves invoke in §4–§5] | **Confidence**: 4 — the mechanism is certain, its magnitude here unknown.
8. **The outcome measure and its object are not fully specified**: three gaps compound. (i) Only the endpoint anchors of the use item are given (1 = rarely or never; 5 = several times daily, §3.2), yet §4 reports a median category of "a few times per week" — a label matching neither anchor, so the three middle options are unrecoverable and the median cannot be placed on the scale. (ii) The LMS is never characterised: which functions it hosts, and in particular whether access is required for assessment submission or grade retrieval, is unstated, so what "use" concretely denotes is unavailable to any reader outside this institution. (iii) The reference period ("in a typical week") is retrospective and unbounded in recall window. Give all five response options verbatim and one short paragraph on the platform and its role in assessment.
   - **Severity**: Major | **Evidence Anchor**: [`text`: §3.2 anchors; §4 "a median category of 'a few times per week'"] | **Confidence**: 5.

### Detailed Comments

#### Research Questions & Hypotheses

The question is stated narrowly and answerably: whether perceived usefulness is associated with self-reported use in one undergraduate population (§1). No hypotheses are formally advanced, which is coherent with the declared descriptive-correlational framing rather than a gap; no directional prediction is smuggled in and no test appears that was not announced. I see no HARKing signal: one association was of interest, one primary test was run, one robustness check accompanies it.

#### Research Design

Correctly labelled cross-sectional and correlational, with the inferential ceiling acknowledged in five separate places. The design cannot order the two variables in time and the manuscript says so. The design's other structural feature — that both variables are measured by the same instrument from the same respondent at the same moment — receives no comparable treatment (W4). Internal/external validity trade-off is handled honestly on the external side (§6) and incompletely on the internal side.

#### Sampling Strategy

The frame is a census invitation and the realised sample is self-selected, but the manuscript never names it as non-probability. *n* = 214 is stated consistently, and §3.4 tells the reader what that *n* could detect. What is missing is the denominator and the resulting response rate (W1), any participant description beyond "spanned all four year levels" (M2), and specificity about whether the recruitment channel is itself the dependent variable (W2). These three together, not any one alone, leave representativeness unassessable.

#### Data Collection

The procedure is described at a workable level (three-week window, single administration, consent at landing page). The predictor's provenance is cited but its adaptation is undocumented (W5); the outcome has no provenance at all (W3) and its response options are partly missing (W8). Data cleaning is auditable by count but not by rule, and the duplicate rule collides with the anonymity statement (W6).

#### Analysis Methods

Method matches data adequately and is transparently reported. Pearson on a mean-scale predictor against a 5-category ordinal outcome is defensible when accompanied by a rank-based check, and the authors provide one. Assumption inspection is reported for linearity, monotonicity, outliers, and symmetry; independence is not considered (W7). The estimator matched to the measurement model — polyserial — is not attempted, and would strengthen the paper cheaply. The power statement is a sensitivity analysis rather than an a priori justification of *n* (M1). Effect size *is* the estimate here, so the usual effect-size complaint does not arise; what is missing is the shared-variance figure being given rather than described (M5).

#### Results Presentation

Complete for what was analysed, and free of selective-reporting indicators: a single planned association, no multiplicity, no uncorrected mass testing, non-trivial unexplained variance acknowledged rather than buried. But the results section contains no table and no figure at all: the scatterplot that grounds the assumption claims is described and not shown, the use item's category frequencies are absent, and there is no participant-characteristics table. The reader is asked to accept distributional claims on assertion.

#### Reproducibility

Unusually, the headline statistics are self-verifying — I reproduced both the CI and the power figure from the reported numbers — so the analytic step is effectively replicable from the text. Measure-level replication is not: the six adapted items, the five response options, and the software used are all unreported, and there is no data-availability statement (M4, W5, W8). Ethics review is documented (§3.3).

#### Methodological Fallacies Detected

- **Reverse causation** — checked and *not* present as a fallacy: pre-empted explicitly in the Abstract, §1, §5 (with the reverse pathway named and sourced to Delgado, 2020), §6, and §7.
- **Self-selection / selection on the dependent variable** — present and under-treated (W1, W2).
- **Attenuation from unreliability and categorisation** — present and unaddressed (W3).
- **Common-method variance** — present and unaddressed (W4).
- **Violated independence via nesting** — plausibly present and unaddressed (W7).
- **P-hacking, HARKing, selective reporting, multiplicity, overfitting, multicollinearity, ecological fallacy, survivorship** — checked; no evidence in this manuscript.
- **Simpson's paradox** — cannot be ruled out because no subgroup analysis is reported despite year level having been collected (M2). Recorded as unchecked, not as detected.

### Questions for Authors

1. How many undergraduates were enrolled and eligible, and what was the response rate?
2. Is the "course-announcement channel" delivered inside the LMS, or by a route independent of it? If inside, how does that change the reading of the low end of the use distribution?
3. How were the 5 duplicate entries identified, and how is that procedure consistent with §3.3's statement that no identifying information was collected and responses could not be linked to individuals? Does *r* change if those 5 cases are retained?
4. What exactly was adapted from Costa and Wren (2019) — wording, item count, referent, or response format — and can the six items be printed verbatim?
5. What are the full five response options for the use item, and which numeric point corresponds to "a few times per week"?
6. Was perceived usefulness administered before the use item, and was any procedural separation used between them?
7. Was year level (or any other characteristic) analysed at any point, and if so with what result?

### Minor Issues

1. **§3.4's power statement is a sensitivity analysis, not an a priori power analysis** — no target effect was pre-specified and no required *n* derived, so *n* = 214 is unjustified prospectively. The sentence does not mislabel itself, so this is a clarity fix: call it a sensitivity analysis, and report the prospective target if one existed. Separately, the figure sits at the boundary: under Fisher's *z* with *n* = 214, power at *r* = .19 is ≈ .798, reaching .80 at *r* ≈ .191, and the value is method-dependent (Fisher *z* vs. exact/noncentral *t*). Immaterial to any conclusion — name the method used. **Severity**: Minor | **Evidence Anchor**: [`text`: §3.4] | **Confidence**: 5.
2. **Year level collected but neither described nor used** — "spanned all four year levels" (§3.1) is the only participant characteristic given. Add a characteristics breakdown and state explicitly whether any subgroup or covariate analyses were run. I see no selective-reporting evidence; the point is that the reader currently cannot verify that. **Severity**: Minor | **Evidence Anchor**: [`text`: §3.1] | **Confidence**: 4.
3. **Missing-data handling is implicit** — 14 incomplete cases were excluded, but the manuscript does not state whether the retained 214 were complete on both focal variables, nor how the excluded cases compared. One sentence closes it. **Severity**: Minor | **Evidence Anchor**: [`text`: §3.1] | **Confidence**: 5.
4. **No reproduction infrastructure** — no analysis software or version, no item bank, no data-availability statement, and the scatterplot referenced in §3.4 is not displayed. Rated Minor only because the reported statistics are independently recomputable; the measure-level replication gap is carried at Major in W5 and W8. **Severity**: Minor | **Evidence Anchor**: [`absence`: checked §3.4, §4, and the manuscript's back matter] | **Confidence**: 5.
5. **Reporting-precision items** — the correlation carries no *df* (APA 7.0 form: *r*(212) = .42); the Spearman coefficient is given without *p* or CI; *r*² is characterised verbally ("the proportion of variance shared by the two measures was accordingly modest", §4) but never stated (*r*² = .18); statistical symbols (*r*, *p*, *n*, *SD*, α, ρ) are not italicised although the reference list does use italics, so this reads as oversight rather than platform limitation; α = .05 is recoverable only from the power sentence, not from the analysis plan; descriptives are reported to one decimal where two is conventional. **Severity**: Minor | **Evidence Anchor**: [`text`: §3.4, §4] | **Confidence**: 5.
6. **Abstract's closing sentence generalises one step wider than the body** — "perceived usefulness tracks with LMS engagement among undergraduates" appears two sentences after the abstract has correctly flagged single-institution limits, and §7 is bounded correctly. Flagged as wording, not as an overclaim: add "at one institution." **Severity**: Minor | **Evidence Anchor**: [`text`: Abstract, final sentence] | **Confidence**: 4.

---

contract_role: methodology

## Dimension Scores

### D1: methodology_rigor
score: warn

Committed Phase 1 block triggers were tested and none fired: the design is named, *n* = 214 and the recruitment route are recoverable, the analysis is fully reconstructible, and the reported statistics are internally consistent and independently reproducible (CI [.30, .52] recomputes to [.303, .525]; the power figure recomputes to ≈ .80). The block trigger "reliability/validity evidence absent for the focal measures with no source for adapted items" is conjunctive and does not fire: the predictor carries α = .88 and a cited source. Multiple committed warn triggers fire — response rate and non-response absent though the sampling route is described (W1); single-source self-report for both variables with no common-method-variance discussion (W4); missing data unaddressed beyond case counts (M3); no data/code availability statement (M4); no prospective power/precision justification for the achieved *n* (M1) — with the outcome measure's absent reliability and validity evidence (W3) and the undocumented instrument adaptation (W5) as the heaviest instances of "material rigor affordances thin or missing."

### D2: domain_accuracy
score: warn

Judged only where accuracy is methodological accuracy, per my Phase 1 narrowing. No block trigger fires: α is correctly named as internal consistency and never presented as validity; *r*² is correctly described as shared variance; significance is not conflated with magnitude; the design label ("cross-sectional survey", "correlational") is accurate; nothing contradicts what the cited sources are represented as reporting. The committed warn trigger "instrument adaptation acknowledged without specifying what was changed" fires directly (W5), as does "a design label imprecise but recoverable from the procedure" — the realised sample is self-selected and non-probability but is never so labelled (W1). "Previously validated instrument" is accurate of the source and applied to the adapted version by inheritance: terminology drift that does not corrupt the result, which is the warn band by definition.

### D3: argumentative_coherence
score: warn

No block trigger fires, and I record that positively: no causal or directional verb is load-bearing anywhere, the reverse pathway is named as equally consistent (§5), the practice implication is triple-hedged and absent from the conclusion, and no claim contradicts the reported results. The committed warn trigger "a limitations section that omits the design's central constraint (temporal ordering, common-method variance, or self-report validity of the use measure)" fires: §6's four limitations cover single-site scope, self-report versus logs, temporal ordering, and voluntary response, but omit same-source common-method variance (W4) and the reliability/coarseness consequences of the single-item outcome (W3), which are the central constraints of a one-instrument, one-occasion design. Secondarily, the onboarding implication (§5) presupposes the PU→use direction that the same paragraph concedes is unresolved; hedged, so Minor, but it is a coherence seam.

### D4: cross_disciplinary_relevance
score: warn

No block trigger fires: the account is followable, no in-group shorthand or uncited acronym blocks reconstruction, and no broad cross-context applicability claim is asserted — §6 and §7 bound transfer explicitly. Committed warn triggers fire on "scale anchors omitted" — only the two endpoints of the outcome item are given, so the §4 median category "a few times per week" cannot be mapped to a scale point (W8) — on platform-specific context left undefined (the LMS's functions and its role in assessment are never described, so "use" has no concrete referent for an outside reader), and on "statistics reported without substantive interpretation" (*r*² described but never given, M5).

### D5: writing_and_structure
score: warn

No block trigger fires: Methods is present and complete in structure (design/participants, measures, procedure and ethics, analysis), Results maps to the single stated question, a limitations subsection exists, and I found no numerical contradiction — *r* = .42 and *n* = 214 are identical across Abstract, §4, §5, and §7, and the attrition arithmetic (233 − 14 − 5 = 214) checks. Warn fires on incomplete reporting that impedes verification: no table or figure anywhere, including the scatterplot the assumption claims rest on; no *df* on the correlation and no *p* or CI on the Spearman coefficient; statistical symbols unitalicised while references are italicised; no participant-characteristics table; and no reported frequency distribution for the ordinal outcome (M5, W8, W7).

## Failure Condition Checks

### F1
fired: false
Predicate — any mandatory dimension (D1, D2, D3) scores `block`. My scores are D1 warn, D2 warn, D3 warn; no mandatory dimension reaches block. Each committed block trigger was tested against text and found not met, as recorded per dimension above.

### F2
fired: true
Predicate — two or more mandatory dimensions score `warn` or worse. D1 = warn, D2 = warn, D3 = warn: three of three mandatory dimensions, against a threshold of two. Action carried: major_revision, severity 70. The `majority` cross-reviewer quantifier is panel-level machinery for the synthesizer; I evaluated the predicate against my own dimension scores only.

### F3
fired: false
Predicate — any high-priority dimension scores `block`. D4 is the only high-priority dimension and scores warn, not block; its committed block triggers (unreconstructible procedure, or unqualified broad-applicability claim) were both tested and neither is met.

### F0
fired: false
Predicate — every mandatory dimension scores `pass`. D1, D2, and D3 all score warn, so the accept-grade condition does not hold.

## Review Body

No scoring-plan dissent is filed. My Phase 1 plan applied to this manuscript without requiring override on any of the five dimensions, and every score above is derived from a trigger I committed to before seeing the paper.

The methodological substance of this review is a single observation applied at three points. The manuscript's inferential discipline is real and, in this literature, better than typical: I tested each of the standard complaints against the text and found them pre-empted rather than merely unaddressed. Causality is disclaimed in five sections and the reverse pathway is named and sourced. The single-site limit is stated three times. An interval estimate accompanies the point estimate, a rank-based robustness check is run for a stated reason, assumptions are inspected and reported, and ethics reporting is complete. I recomputed the two verifiable numbers and both hold. A reviewer who arrives here with a generic critique of weak survey work will be reviewing a different paper.

That discipline stops at the measurement layer, and this is where my seat's contribution lies. The predictor is a six-item scale with α = .88 whose adaptation from its source is entirely undocumented, so internal consistency is the only psychometric fact available and it does not establish that the adapted items measure the construct the source validated. The outcome is one 5-category self-report item with no source, no reliability estimate, no validity evidence, and — because only its endpoints are printed — no fully recoverable response scale. Random error and categorisation in that outcome attenuate the observed coefficient, and no correction is possible because its reliability is unknown and unestimable from a single administration. At the same time, both variables were rated by the same respondent, on the same instrument, in the same sitting, and common-method variance appears nowhere in the manuscript; §6's self-report limitation concerns divergence from behavioral logs, which is a different threat. These two biases oppose each other. The honest conclusion is therefore stronger than either half taken alone: *r* = .42 is a point estimate whose net measurement bias is of indeterminate sign, and "moderate" should be qualified in exactly those terms rather than as a floor or as a settled magnitude. I note that the Spearman check, which the paper is right to run, addresses the parametric form of the coefficient and not one of these three issues.

The sampling account has the same shape — precise where it reports, silent where it matters. The eligible population is invoked but never counted, so the response rate is unavailable and non-response is unquantifiable; the realised sample is self-selected but never labelled as such; and the recruitment channel is described in a phrase that leaves open whether invitation exposure was itself a function of the dependent variable. If course announcements are LMS-delivered, the low-use tail is truncated by the recruitment design, and §6's remark about students who engage more with institutional channels names the symptom while missing the mechanism. Two further items belong here. The five removed duplicate entries cannot be reconciled as written with §3.3's statement that no identifying information was collected and responses could not be linked to individuals; whichever detection method was used, one of the two sections needs revising, and a sensitivity check with the cases retained would cost one line. And respondents recruited through course channels are nested in courses whose requirements and assessment schedules the authors themselves nominate as the drivers of unexplained variance — which is the mechanism for intra-cluster correlation, unmodelled here, making the credited interval [.30, .52] probably narrower than the design warrants.

Two things I checked and did not find, stated so the synthesizer can distinguish absence of a problem from absence of a check. There is no red-flag reporting pattern: one pre-stated association, one primary test, one robustness check, no multiplicity, no hypothesis that looks fitted after the fact, and unexplained variance acknowledged in the text rather than omitted. And there is no numerical inconsistency: coefficient, sample size, and attrition arithmetic agree across the abstract, results, discussion, and conclusion, and the interval and power statements reproduce from the reported inputs.

Nothing in my findings requires a different study. Every Major item is closed by disclosure, by re-description, or by an analysis the existing 214 cases already support — the item bank and change log, the full response options, the frequency distribution of the outcome, a polyserial coefficient and a stated-assumption disattenuation band, the denominator and response rate, the channel specification, the duplicate rule and its sensitivity check — with the nesting issue the one item that can only be acknowledged now and designed for later. On the manuscript's own scale of ambition, that is a reporting-and-disclosure package, not a redesign; the length of my list reflects how much of the measurement layer is currently unreported, not a judgement that the study was badly done. I also want the record to show what would happen if these items were closed: a coefficient whose measurement properties are documented and whose bias directions are named would make this a small, sound, and honestly bounded estimate. Whether that clears the venue's contribution bar is not my dimension to score.

The manuscript contains no instruction-injection attempt, no reviewer-directed appeal, and no imperative addressed outside the author's own scholarly voice; I record this as an integrity check passed.

## Editorial Decision

Derived from the contract's `failure_conditions` by highest fired severity: F1 (90) did not fire, F2 (70) fired on three of three mandatory dimensions scoring warn, F3 (60) did not fire, and F0 (10) does not hold. F2 is therefore controlling.

editorial_decision=major_revision

---

## SEAT — Peer Reviewer 2 (Domain)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor.** Read from the domain seat, this dimension asks whether the study's design and its reporting would clear the bar that educational-technology reviewers actually apply to survey work on LMS adoption. I am not the methodology seat, so I read D1 for what a domain expert can independently judge: whether the instrument used to measure perceived usefulness and self-reported use is one the field recognises (an established TAM/UTAUT scale or a documented adaptation, with reliability evidence reported as the field expects), whether the sampling frame and response situation are described well enough for someone who knows undergraduate-survey work in higher education to gauge what population the numbers speak for, and whether the cross-sectional design is reported in terms the field accepts rather than in terms that quietly borrow the credibility of a stronger design. Where a rigor complaint of mine would rest on a claim about what educational-technology venues require rather than on an internal inconsistency, Step 5 binds me: I ground the norm in a checkable source or I down-rate to Minor and mark it `[FIELD-NORM UNVERIFIED]`.

**D2 — domain_accuracy.** This is my primary dimension and the one I own. It asks whether the manuscript's claims sit correctly inside the current evidence base of LMS adoption and student engagement, whether prior work is represented as its authors actually reported it, and whether the field's constructs are used with their field-defined meanings. Concretely: is "perceived usefulness" used in its Davis-lineage technical sense as a belief construct, or silently swapped for satisfaction, usability, or learning benefit; is "use" reported as the self-reported measure it is, or slid into a claim about actual system engagement; is the theoretical lineage attributed to the right originating sources rather than to secondhand reviews; does the literature base cover both the foundational acceptance-model work and the last three-to-five years of LMS-adoption findings, including the studies that complicate the usefulness–use link (self-report/log-data divergence, mandatory-versus-voluntary use contexts) rather than only those that support it. Factual claims about the field's state of knowledge, and about what LMS platforms and higher-education contexts are like, fall here too.

**D3 — argumentative_coherence.** From the domain seat this asks whether the paper's central story about perceived usefulness and use holds together on the field's own terms. The characteristic failure in this literature is the correlation-to-causation slide: a cross-sectional association read as usefulness *driving* use, or a recommendation that institutions raise perceived usefulness in order to raise use, which is a causal instruction dressed as an implication. Equally in scope: whether the research gap argued in the introduction is the gap the results actually address, whether conclusions stay inside what a single cross-sectional undergraduate sample can support, and whether the theoretical framework named up front is the one that actually organises the analysis and discussion, or is named and then abandoned. I judge internal consistency of the argument, not the statistical machinery that produced the numbers.

**D4 — cross_disciplinary_relevance.** Reviewer 3 owns the deep cross-disciplinary assessment; my share is narrower and domain-anchored. I ask whether the field-specific vocabulary a neighbouring reader will meet — perceived usefulness, behavioural intention, LMS, engagement, adoption — is defined at first use with its field meaning intact, so that an adjacent reader (instructional design, information systems, higher-education policy) is not misled by a term that means something looser in ordinary English. And where the paper reaches outward — claiming implications for learning outcomes, institutional policy, or information-systems theory — I ask whether that reach is substantiated by what was actually measured, since a self-reported-use survey does not carry a learning-outcomes claim.

**D5 — writing_and_structure.** At a manuscript of roughly 1,600 words, my domain reading of this dimension is whether the exposition carries the domain content it needs to carry. Does the literature review have an organising logic and critical synthesis rather than an enumerated list; are constructs defined before they are used; are the reported quantities labelled precisely enough (which scale, which anchors, which N) that a domain reader can interpret them; are citations complete and attributed to the sources that actually make the claim. I treat the compressed length as a structural fact rather than a defect in itself — brevity is only a domain problem where it removes information the field needs to evaluate the claims.

## Scoring Plan

### D1: methodology_rigor
- **what_to_look_for**: Named measurement instrument with its source and any adaptation described; reliability evidence for the perceived-usefulness and use scales reported in the form the field expects; sampling frame, recruitment route, N, and response rate stated; whether use is measured by self-report only or triangulated with system logs; explicit labelling of the design as cross-sectional; whether reported analyses match the design (association language for association analyses); ethics/consent statement if the venue norm calls for one; whether limitations name the design's actual constraints rather than generic ones.
- **what_triggers_block**: The manuscript reports quantitative relationships between perceived usefulness and use while giving no identifiable instrument provenance *and* no sample-description sufficient to know who was surveyed — leaving a domain reader unable to say what population or construct the numbers refer to; or the analysis reported is structurally incapable of supporting the relationship claimed (e.g. a mediation or effect claim asserted with no corresponding analysis reported anywhere in the manuscript).
- **what_triggers_warn**: One material reporting element is absent or unclear but the study remains interpretable — e.g. reliability evidence missing for an otherwise-identified scale, response rate or sampling route unstated, self-report-only measurement of use never acknowledged as a limitation, or an adapted instrument whose modifications are not documented. Any warn resting on a "the field requires this" claim must carry grounded norm evidence; ungrounded, it is reported at Minor with `[FIELD-NORM UNVERIFIED]` and does not by itself drive the dimension below pass.

### D2: domain_accuracy
- **what_to_look_for**: Definition of perceived usefulness and its consistency with the Davis/TAM lineage throughout the paper; whether "use" is consistently qualified as self-reported; correct attribution of TAM/UTAUT/related models to their originating sources rather than to review articles; presence of foundational acceptance-model citations *and* recent (roughly last five years) LMS-adoption work; whether the known complications of this literature are acknowledged (self-report versus log-data divergence, mandatory-use contexts compressing variance, the usefulness–use link being weaker for required systems); accuracy of any factual statements about LMS platforms, adoption rates, or institutional context; whether cited studies are characterised as their authors actually reported them; concept conflation between usefulness, ease of use, satisfaction, and engagement.
- **what_triggers_block**: A core domain construct is used in a way that contradicts its field definition and that misuse carries the paper's conclusion — e.g. perceived usefulness operationalised or interpreted as satisfaction or as learning gain while conclusions are stated about usefulness; or a foundational theory's claims are misstated in a way that inverts what the model predicts; or a cited study is characterised as finding something it did not find, where that mischaracterisation is load-bearing for the argued gap or conclusion.
- **what_triggers_warn**: Domain representation is imprecise but not conclusion-inverting — e.g. theory attributed only through secondhand review citations, literature base skewed to confirmatory findings with the contrary strand unacknowledged, recent LMS-adoption work (last 3–5 years) thin or absent, self-reported use referred to as "use" in places without qualification, or terminology drifting between usefulness/ease-of-use/engagement without conflating them at the point of the main claim.

### D3: argumentative_coherence
- **what_to_look_for**: Whether the association between perceived usefulness and self-reported use is described in associational language throughout, including abstract, discussion, and any practical implications; whether recommendations addressed to institutions or instructors presuppose a causal direction the design cannot establish; whether the gap claimed in the introduction is the gap the findings address; whether the theoretical framework named at the outset actually structures the analysis and discussion or is dropped after the introduction; whether conclusions stay within a single-institution, single-timepoint, self-reported undergraduate sample; whether limitations, if present, actually constrain the conclusions drawn or are decorative.
- **what_triggers_block**: The paper's central conclusion is causal or directional while the reported evidence is a cross-sectional association — for instance stating that perceived usefulness increases, drives, or leads to LMS use, or recommending that institutions raise perceived usefulness in order to raise use — and this framing is not confined to a hedged aside but carries the abstract, discussion, or implications; or the stated conclusion contradicts the reported result; or the theoretical framework is invoked to license a claim it does not support.
- **what_triggers_warn**: Causal or directional language appears in bounded, non-load-bearing places (a single implication sentence, a stray verb) while the main claims stay associational; or the introduction's gap and the discussion's contribution are misaligned without either being wrong; or the framework is named and then only loosely connected to the analysis; or generalisation reaches modestly past the sample (to "undergraduates" broadly) without a transferability caveat.

### D4: cross_disciplinary_relevance
- **what_to_look_for**: First-use definitions of perceived usefulness, LMS, self-reported use, engagement, and any acceptance-model term, checked for field fidelity as well as accessibility; whether the paper distinguishes LMS *use* from *learning* and from *engagement* rather than letting them stand as synonyms for an outside reader; whether reaches into adjacent domains (learning outcomes, institutional policy, information-systems theory) are matched by what was measured; whether the abstract and discussion are readable by an instructional-design or higher-education-policy reader without prior TAM knowledge.
- **what_triggers_block**: The paper asserts a substantive interdisciplinary claim wholly unsupported by its measurements — e.g. concluding something about learning outcomes, academic achievement, or teaching effectiveness from a perceived-usefulness and self-reported-use survey — and that claim appears in the abstract or conclusions rather than as flagged speculation.
- **what_triggers_warn**: Field-specific terms are used without first-use definition so that an adjacent-field reader would import the everyday meaning; or "use", "engagement", and "adoption" are used interchangeably; or an outward implication for policy or practice is stated with more confidence than the measurement supports but is confined to a clearly marked implications passage.

### D5: writing_and_structure
- **what_to_look_for**: Whether the literature review is organised (thematic, chronological, or methodological) and synthesised rather than enumerated; whether constructs are defined before first substantive use; whether reported quantities are labelled with scale, anchors, and N so a domain reader can interpret them; whether tables/figures, if present, are self-describing; internal consistency of numbers between abstract, results, and any table; completeness and correct attribution of citations; whether the ~1,600-word length is used on the domain-critical content (constructs, instrument, findings, limitations) or spent on generic preamble.
- **what_triggers_block**: The manuscript's domain content is unrecoverable from the text as written — key constructs never defined, results reported without stating what was measured or on what scale, or numbers that contradict each other between sections so that a domain reader cannot determine what was found. Prose infelicity alone never reaches block at this dimension.
- **what_triggers_warn**: The literature review enumerates rather than synthesises; a construct is used substantively before being defined; a reported quantity lacks its scale, anchors, or N; citations are incomplete or attributed to the wrong source; or the compressed length has displaced domain-critical material (limitations, instrument description) into a single perfunctory sentence.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Domain Review Report (Peer Reviewer 2)

### Reviewer Identity

Professor of higher education with a research programme on institutional learning-platform engagement; author of a systematic review of TAM/UTAUT applications in higher education documenting the accumulation of near-identical perceived-usefulness/use correlations; co-author of empirical work pairing survey perceptions with LMS log traces; editorial board member at two educational-technology journals.

### Overall Recommendation

Major Revision

### Confidence Score

4 — high competence on the acceptance-research literature, construct provenance, and how single-site estimates are placed against published ones; lower on the psychometric and sampling technicalities that belong to Reviewer 1.

### Summary Assessment

This is a disciplined, honestly bounded manuscript, and I want to say so before I say anything else: the construct is defined in its field-correct sense, self-reported use is never allowed to drift into behavioural use, the literature review foregrounds the strand that complicates the paper's own finding rather than the strand that flatters it, and the conclusion is pitched at exactly the level the design supports. Domain reviewers of this literature spend most of their time deleting causal verbs; here there are none to delete.

The problems are of a different kind, and they are real. The paper's stated contribution is to supply "an incremental data point, comparable with prior work" and "one point in a distribution" — a claim that requires the distribution to be shown, and it never is. Not one competing coefficient appears anywhere in the manuscript. The construct is borrowed from an acceptance framework the paper explicitly declines, with no statement of what then licenses the construct's interpretation. Perceived usefulness is defined without reference to the tradition that originated it, and "long proposed" is attributed to sources from 2019 and 2020. The setting descriptors a reader would need to place this estimate against others — above all, whether LMS use was required in these students' courses — are absent, although the manuscript itself identifies course requirements as a driver of the outcome. Finally, "engagement" is used as a synonym for a single access-frequency item, including in the abstract's payload sentence.

None of this is a demand for a different study. Every item above is answerable within the existing data by reporting, positioning, and one paragraph of justification.

### Strengths

1. **Self-reported use is held to its actual referent throughout**: The manuscript names the self-report/log divergence problem in the literature review and then honours it in its own language at every subsequent point — measure description, results, limitations, conclusion. In a literature where "use" routinely slides into a behavioural claim between the methods and the abstract, this is the single most creditable domain feature of the paper.
   - **Evidence Anchor**: `text: §2 ¶2 — "we take these cautions seriously, restrict ourselves to correlational language throughout, and treat our self-report measure as an indicator of perceived use rather than a behavioral count"` (corroborated at §3.2, §6, §7)

2. **The literature review synthesises, and it synthesises against itself**: §2 is organised (construct → cautions → positioning) rather than enumerated, and its middle paragraph is given over entirely to work that complicates the paper's finding: the reverse pathway (Delgado, 2020), contextual determination by course and assessment design (Ibarra & Poll, 2021), between-site variability of the estimate (Song, 2018), and measurement divergence (Vasquez, 2020). Reviewing a thin reference list that nonetheless spends most of itself on counter-evidence is unusual.
   - **Evidence Anchor**: `text: §2 ¶2 — "Several authors caution against over-reading these associations."`

3. **Perceived usefulness is used with its field meaning intact and does not drift**: The definition given is the belief-about-performance-benefit construct, not satisfaction, not ease of use, not perceived learning gain, and it stays that construct through Methods, Results, and Discussion. The most common domain-accuracy failure in this manuscript class — the silent substitution of a satisfaction or usability reading at the point of the main claim — does not occur here.
   - **Evidence Anchor**: `text: §2 ¶1 — "perceived usefulness — the degree to which a person believes a technology will help them perform better"`

4. **The reverse pathway is stated in the Discussion, not quarantined in the Limitations**: Papers of this design routinely put the causal disclaimer in §6 where implication-hungry readers do not go, then write §5 as though direction were settled. Here the alternative direction appears in the interpretive section itself, and the practice implication that follows is explicitly marked as suggested rather than shown.
   - **Evidence Anchor**: `text: §5 ¶2 — "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"`

### Weaknesses

1. **The paper's own contribution claim — comparability with prior estimates — is asserted and never delivered**: The manuscript positions itself twice as an incremental, comparable data point and invokes Song (2018) for the idea that a single-site estimate is "one point in a distribution." A reader who accepts that framing then asks the obvious next question: where in the distribution? The manuscript reports no competing coefficient, no range from Song's multi-campus data, no benchmark of any kind. "Consistent with prior technology-acceptance research" is the only comparison offered, and it is qualitative. This is the highest-value revision available: the claim is the paper's central justification for existing, and cashing it out costs a table or a paragraph. Report two to four published coefficients for perceived usefulness against self-reported LMS use, with their sample sizes and settings, and state where r = .42 falls among them — above, below, or squarely inside. The severity here does not rest on any external norm; it rests on the manuscript's own claim being unsupported within the manuscript.
   - **Severity**: Major | **Evidence Anchor**: [`absence: comparator estimates absent from §2 ¶3, §4, §5 ¶1, §7, and the reference list — all surfaces where a distribution claim could be substantiated`] | **Confidence**: 5 — systematic-review work cataloguing precisely this estimate distribution

2. **The construct is borrowed from a framework the paper declines, with no stated warrant**: The manuscript twice refuses to test an acceptance model, which is a legitimate scoping decision and not something I will ask you to reverse. But it then uses that framework's central construct, that framework's instrument lineage, and that framework's interpretive vocabulary ("consistent with prior technology-acceptance research"). If the theory is not doing work here, what licenses reading a six-item mean as *perceived usefulness* rather than as an unlabelled attitude scale, and what licenses treating the resulting coefficient as commensurable with coefficients produced inside the framework? This is answerable in one paragraph — either the construct is used as a measured attitude with the theoretical baggage explicitly set down, or the framework is retained at the construct level and that retention is stated. As written, the paper takes the framework's credibility while disowning its commitments.
   - **Severity**: Major | **Evidence Anchor**: [`text: §1 ¶2 — "nor do we test a full acceptance model"; §2 ¶3 — "rather than as a test of a theoretical model"; against §5 ¶1 — "consistent with prior technology-acceptance research"`] | **Confidence**: 4 — theoretical positioning of TAM-derived constructs in higher-education research

3. **Construct provenance is attributed to secondhand and anachronistic sources**: §2 opens with "Research on technology acceptance has long proposed that perceived usefulness … is among the factors associated with adoption and continued use," and cites Costa and Wren (2019) and Delgado (2020) for it. A claim about what a field has long proposed cannot be carried by two sources published in 2019 and 2020; the temporal claim and its support are internally mismatched. The originating source of the construct is not cited anywhere in the manuscript. A domain reader's first inference is that the acceptance literature has been read through recent instrument papers rather than at its source, which then makes the framework question in W2 harder to answer credibly. Add the foundational attribution (see Missing Key References).
   - **Severity**: Major | **Evidence Anchor**: [`text: §2 ¶1 — "Research on technology acceptance has long proposed … (Costa & Wren, 2019; Delgado, 2020)"`] | **Confidence**: 5 — construct-provenance patterns are the core subject of my review work

4. **"Previously validated" is claimed for an instrument the paper reports as adapted**: §2 warrants the measure as "a previously validated measure of perceived usefulness," and the abstract compresses this to "an adapted, previously validated instrument." §3.2 then reports that the six items were *adapted* from Costa and Wren (2019). Validation evidence attaches to the instrument that was validated; adaptation is precisely the operation that puts that transfer in question, and the paper supplies no adaptation record — no item wording, no statement of what was changed or why, no re-validation beyond an internal-consistency coefficient. I raise this at the domain level, where it bears on whether the reported construct is the construct the prior literature measured and therefore on the comparability claim in W1; the psychometric depth belongs to Reviewer 1. The severity here rests on the manuscript's own validation claim exceeding what the manuscript reports, not on an external reporting standard. Fix: state the adaptations, or report the items in an appendix.
   - **Severity**: Major | **Evidence Anchor**: [`text: §3.2 — "a six-item scale adapted from Costa and Wren (2019)"; against §2 ¶3 — "using a previously validated measure of perceived usefulness"`] | **Confidence**: 4 — construct-comparability judgement; psychometric detail deferred to Reviewer 1

5. **"Engagement" is used as a synonym for a single access-frequency item**: The measured outcome is how often a respondent reports accessing the LMS in a typical week. The manuscript nonetheless describes this as engagement in the abstract's opening and, more consequentially, in the abstract's concluding sentence — the line most readers will carry away. In higher-education and learning-analytics usage, engagement is a broader, multi-dimensional construct; access frequency is one coarse behavioural proxy for one of its facets. An adjacent-field reader will import the broader meaning, and the abstract invites them to. This is fixable by wording alone: say what was measured.
   - **Severity**: Major | **Evidence Anchor**: [`text: Abstract — "The findings offer modest, design-bounded evidence that perceived usefulness tracks with LMS engagement among undergraduates"; against §3.2 — "a single five-point frequency item asking how often the respondent accessed the LMS in a typical week"`] | **Confidence**: 5 — terminology conventions in higher-education engagement research

6. **The setting is not characterised on the variable the paper itself identifies as decisive**: §4 attributes unexplained variance to "course requirements and assessment schedules," and §5 endorses Ibarra and Poll (2021) on instructor expectations and assessment structure. The manuscript never says where its own institution sits on that variable — whether LMS use was required for coursework, submission, or grade access; which platform; what mix of disciplines and delivery modes. Having named the factor as a principal driver of its outcome, the paper owes its own value on it, and a reader cannot otherwise judge whether this coefficient is comparable to any other (W1) or whether the observed variance in reported use is even free to vary. Two or three sentences of setting description resolve this.
   - **Severity**: Major | **Evidence Anchor**: [`absence: no requirement/platform/discipline descriptors in §3.1, §3.2, or §5, although §4 and §5 both name course requirements and assessment structure as drivers`] | **Confidence**: 5 — institutional learning-platform research

7. **Literature base is narrow and stops at 2021**: Six sources, none later than 2021, with no representation of the post-TAM trajectory (UTAUT and its successors, and the critique of perceived usefulness as a predictor of *actual* rather than intended use), and a single representative (Vasquez, 2020) for the self-report-versus-log-data strand that the paper's own measurement decision makes central. I report the gap as detected. I am rating it Minor rather than Major because its severity rests on what an educational-technology venue expects of a literature base and how current it must be, and I have not grounded that expectation in a checkable venue policy or reporting standard within this review. `[FIELD-NORM UNVERIFIED]` The substantive consequence of the thin base — no benchmark against which to place r = .42 — is charged at Major under W1, where it is grounded in the manuscript's own claim.
   - **Severity**: Minor | **Evidence Anchor**: [`absence: reference list, §§63–75 — six entries, latest 2021, no UTAUT-lineage or meta-analytic source`] | **Confidence**: 5 — coverage of this literature

8. **The Limitations name a selection risk the manuscript gives no means to bound**: §6 states that "students who engage more with institutional channels may be overrepresented," which is the right worry, and the recruitment route was the institution's course-announcement channel. But the manuscript reports no response rate and no eligible-population denominator, so a reader cannot gauge how large the risk is. I flag the internal tension — a stated bias with no information supplied to bound it — and defer the sampling analysis to Reviewer 1. Severity is set at Minor because the demand that a response rate be reported is a field reporting expectation I have not grounded in a venue policy or reporting guideline here. `[FIELD-NORM UNVERIFIED]`
   - **Severity**: Minor | **Evidence Anchor**: [`text: §6 — "response was voluntary, so students who engage more with institutional channels may be overrepresented"; against §3.1, which reports 233 → 214 with no denominator`] | **Confidence**: 3 — sampling technicalities are Reviewer 1's competence, not mine

9. **The reported median use category cannot be located on the reported scale**: §3.2 gives only the two endpoint anchors (1 = rarely or never; 5 = several times daily). §4 reports a median category of "a few times per week," which is neither anchor. A domain reader cannot tell whether that is category 3 or category 4, and therefore cannot compare this sample's use distribution with any published one — which again bears on W1. Report the full response-option wording.
   - **Severity**: Minor | **Evidence Anchor**: [`text: §4 — "Self-reported LMS use had a median category of 'a few times per week'"; against §3.2 — "(1 = rarely or never to 5 = several times daily)"`] | **Confidence**: 5 — straightforward interpretability check

10. **Whitfield (2019) carries the paper's only practice implication but is never set up**: The onboarding recommendation in §5 rests on a source that appears nowhere in §2. A reader meets it for the first time at the moment it is asked to do argumentative work, with no account of what it found, in what setting, or with what evidence — and the manuscript itself flags it as a practitioner account rather than an empirical study. Introduce it in the literature review or drop the reliance.
   - **Severity**: Minor | **Evidence Anchor**: [`text: §5 ¶2 — "a possibility also raised in practitioner accounts of digital-environment onboarding (Whitfield, 2019)"`] | **Confidence**: 4 — literature integration

11. **The shared-variance statement is given qualitatively where a number was available**: §4 says "The proportion of variance shared by the two measures was accordingly modest" without reporting the value, though r is reported to two decimals in four places. Stating it (≈18%) makes the modesty the paper is claiming concrete for readers and comparable across studies.
   - **Severity**: Minor | **Evidence Anchor**: [`text: §4 — "The proportion of variance shared by the two measures was accordingly modest"`] | **Confidence**: 5

### Detailed Comments

#### Literature Review

- **Coverage**: Six sources for a topic with a large published corpus. Structurally absent, in order of consequence: (a) any benchmark estimate — meta-analytic or otherwise — against which r = .42 could be placed, which is what the paper's own positioning claim requires; (b) the originating source of the perceived-usefulness construct; (c) the post-TAM trajectory and its critique of perceived usefulness as a predictor of actual rather than intended use; (d) more than one representative of the self-report-versus-log-data strand, given that this paper's measurement choice sits directly on it. No source is later than 2021.
- **Integration quality**: Genuinely synthesised, not enumerated — and organised so that the counter-evidence occupies the centre of the section. This is above the norm for this manuscript class and should be preserved through revision.
- **Research gap argument**: The paper does not argue a gap, which is honest — it argues contribution by accumulation instead. That is a legitimate move, but it transfers the entire justificatory burden onto the comparability claim (W1), which is exactly the claim the manuscript does not discharge. Either substantiate the accumulation argument with actual comparators, or the paper is left with no stated warrant for its own existence.

#### Theoretical Framework

- **Appropriateness**: The decision not to test an acceptance model is coherent with the research question as posed and I do not ask for it to be reversed; a descriptive bivariate study is a legitimate container for a bivariate question. Reviewers pushing this manuscript toward model-testing with moderators would be commissioning a different paper.
- **Application depth**: The abstention is under-argued rather than incoherent. The construct, the instrument lineage, and the interpretive vocabulary all come from the framework; only the commitments are declined. What is missing is the paragraph that says why the construct travels without its theory (W2).
- **Alternative frameworks**: Not required. If the authors wish to keep the study atheoretical, the cleanest revision is to say so explicitly and to justify the construct's standalone use — not to bolt on a framework the design cannot test.

#### Academic Argument Quality

- **Factual accuracy**: No domain-factual errors detected in the manuscript's characterisations of prior work; the four cautions attributed to Delgado, Ibarra and Poll, Vasquez, and Song are each used consistently with what the manuscript reports them to say and each is honoured in the paper's own language. I cannot independently verify the six sources' contents from session materials, so this is a coherence check, not a citation-content audit. One internal mismatch does surface: the "long proposed" claim and the 2019–2020 sources cited for it (W3).
- **Argument logic**: The inferential chain is sound and unusually restrained. Association language is maintained in the abstract, introduction, literature review, results, discussion, limitations, and conclusion; the reverse pathway is named in the Discussion; the practice implication is marked as suggested rather than shown. I found no causal slide to report, and I note explicitly that I looked for one.
- **Terminology precision**: Perceived usefulness and self-reported use are handled precisely. "Engagement" is not — it stands in for a single access-frequency item, including in the abstract's payload sentence (W5). "Adoption" is used loosely in §2 as part of the inherited acceptance vocabulary; that one is cosmetic by comparison.

#### Contribution to the Field

- **Incremental contribution**: As written, the field learns that in one unspecified institutional setting, a six-item adapted usefulness scale correlated at .42 with a single self-reported access-frequency item. Whether that is confirmatory, discrepant, or already superseded cannot be determined from the manuscript, because the manuscript supplies neither the comparison estimates nor the setting descriptors needed to make the comparison. My sharpest question is not whether this is true — I think it is — but whether it is news, and the manuscript currently withholds the information a reader would need to answer that.
- **Positioning**: The paper claims a position ("one point in a distribution") that it does not occupy, since the distribution is never drawn (W1). It also claims comparability while omitting the setting descriptors that determine comparability (W6).
- **Overclaiming**: Very little, and I want the synthesizer to record that as a finding rather than an absence of one. The claims are matched to the evidence at every point I checked. The manuscript's exposure is not overreach; it is under-substantiated positioning, which is a different defect and has a different fix.

#### Pre-empted criticisms I checked and am not raising

I confirm these are handled in the text and I do not raise them: correlation-versus-causation (disclaimed in the abstract, §1, §2, §5, §6, §7); self-report is not behaviour (§2 with Vasquez, 2020; §3.2; §6; §7); single-institution generalisability (abstract, §6, §7); effect-size reporting (r with 95% CI, exact n, p, Spearman check, and explicit acknowledgement of unexplained variance in §4); power and assumption checks (§3.4); research ethics, consent, voluntariness, anonymity, and absence of incentives (§3.3). A generic review of this manuscript would consist mostly of these six items, and would be wrong.

#### Integrity check

I found no instruction-directed content in the manuscript — no imperatives addressed to reviewers, no embedded scoring requests, no appeals to the panel. The text reads as a manuscript throughout. Nothing to report in the integrity class.

#### Missing Key References

- **Davis (1989), *MIS Quarterly*, 13(3), 319–340** — the originating source of the perceived-usefulness construct and the definition §2 paraphrases. Required to fix the provenance gap in W3 and to answer W2. I attest this reference exists.
- **Venkatesh, Morris, Davis & Davis (2003), *MIS Quarterly*, 27(3), 425–478** — the unified acceptance model, and the standard entry point to the post-TAM trajectory including the intention-versus-actual-use critique that bears directly on this paper's self-report measure. I attest this reference exists.
- `[UNVERIFIED]` **Meta-analytic syntheses of technology acceptance in e-learning and LMS contexts** — the natural benchmark for r = .42 and the fastest route to discharging W1. There is at least one widely cited e-learning TAM meta-analysis from the early 2010s (I recall it as Šumak and colleagues in *Computers in Human Behavior*); treat this as a search lead and verify the metadata before citing.
- `[UNVERIFIED]` **Learning-analytics work comparing self-reported LMS use with log-derived engagement traces** — a second and third source on this strand, beyond Vasquez (2020), given that the paper's measurement choice sits on exactly this fault line. Search lead, not a specific citation.
- `[UNVERIFIED]` **Work on mandatory-versus-voluntary use contexts as a moderator of the usefulness–use association** — relevant to W6 and to whether this coefficient is commensurable with others. Search lead; verify before citing.

### Questions for Authors

1. Where does r = .42 fall relative to published estimates of the same association? Please name at least two comparators with their coefficients, sample sizes, and settings, and state whether your estimate is consistent with, above, or below them. Your contribution claim depends on this answer.
2. Was LMS use required of these students — for submission, for grade access, for materials only available there — and does that requirement vary across the courses respondents were taking? What platform, and what discipline mix?
3. If the study does not test an acceptance model, what licenses interpreting the six-item mean as *perceived usefulness* in the theory's sense and treating the resulting coefficient as commensurable with coefficients produced inside that theory? One paragraph is enough.
4. What exactly was adapted from the Costa and Wren (2019) instrument, and on what basis do you regard the original validation evidence as transferring to the adapted six items? Please report the item wording.
5. What are the full labels for all five response options on the use item, and which category does "a few times per week" correspond to?

### Minor Issues

- Abstract: "perceived usefulness tracks with LMS engagement" should say what was measured — self-reported frequency of LMS access.
- §2 ¶1: "long proposed" is not supportable by 2019 and 2020 citations; either add the foundational source or drop the temporal claim.
- §4: report r² (≈18%) rather than describing the shared variance qualitatively.
- §5: Whitfield (2019) needs a setup in §2 or should stop carrying the practice implication alone.
- §2 ¶1: "adoption" is used as a near-synonym for continued use; tighten or define.

---

contract_role: domain

## Dimension Scores

### D1: methodology_rigor
score: warn

Applying my Phase 1 warn trigger — "one material reporting element is absent or unclear but the study remains interpretable … an adapted instrument whose modifications are not documented." The instrument is adapted from a named source with no adaptation record, while the manuscript warrants it as "previously validated" (W4); the median use category cannot be located on the reported response scale (W9). The block trigger is not met: instrument provenance is given, the sample is described, the design is labelled cross-sectional throughout, and a correlation is a structurally adequate analysis for an association claim. The response-rate gap (W8) is reported at Minor with `[FIELD-NORM UNVERIFIED]` per my Phase 1 commitment and does not by itself carry this dimension below pass; W4 does, on internal-warrant grounds.

### D2: domain_accuracy
score: warn

Two committed warn triggers fire on internally grounded evidence: "theory attributed only through secondhand review citations" (W3 — the construct's originating source is absent and a "long proposed" claim is carried by 2019–2020 sources) and unsubstantiated positioning against the field's evidence base (W1 — the comparability claim is asserted at three points and never discharged, with W2 and W6 compounding it). The block trigger is not met: perceived usefulness is used in its field-defined belief-construct sense at the point of the main claim, self-reported use is consistently qualified, no foundational theory's predictions are inverted, and no cited study is characterised inconsistently with how the manuscript itself reports it. Literature currency (W7) is charged at Minor with `[FIELD-NORM UNVERIFIED]` and is not a driver of this score.

### D3: argumentative_coherence
score: pass

None of my committed triggers fires. Association language is maintained in the abstract, introduction, literature review, results, discussion, limitations, and conclusion; the reverse pathway appears in the Discussion rather than only in the Limitations; the practice implication is explicitly marked as suggested rather than proven; conclusions stay inside a single-site, single-timepoint, self-report sample with the transferability caveat stated twice; the limitations actually constrain the claims rather than decorating them. On my warn trigger "the framework is named and then only loosely connected to the analysis": the manuscript does not claim framework guidance and then abandon it — it declines a framework at the outset and consistently does not test one, which is coherence rather than looseness. The residual issue, that a theory-derived construct is used without its theory (W2), is a positioning and warrant gap and I have charged it under D2; charging it here as well would be double-scoring the same defect.

### D4: cross_disciplinary_relevance
score: warn

My committed warn trigger — "'use', 'engagement', and 'adoption' are used interchangeably" — fires on W5: the outcome is a single self-reported access-frequency item, and it is called engagement in the abstract's opening line and again in the abstract's concluding claim, where an instructional-design or higher-education-policy reader will import the broader, multi-dimensional field meaning. "Adoption" is used loosely in §2. The block trigger is not met: no claim about learning outcomes, academic achievement, or teaching effectiveness appears anywhere in the manuscript, and the abstract is readable by an adjacent-field reader without prior acceptance-model knowledge. First-use definitions of LMS, perceived usefulness, and self-reported use are present and field-faithful.

### D5: writing_and_structure
score: warn

My committed warn trigger — "a reported quantity lacks its scale, anchors, or N" — fires on W9: the reported median category is not among the two anchors given, so a domain reader cannot place it on the five-point scale or compare it with published use distributions. Supporting: Whitfield (2019) enters only at the point of the implication it supports with no literature-review setup (W10), and the shared-variance statement is qualitative where the value was available (W11). The block trigger is not met — constructs are defined before use, the numbers are internally consistent across abstract, results, discussion, and conclusion, and the domain content is fully recoverable from the text. The literature review is organised and synthesised, which counts in the paper's favour at this dimension.

## Failure Condition Checks

### F1
fired: false

Predicate: any mandatory dimension scores 'block'. My mandatory dimensions are D1 (warn), D2 (warn), and D3 (pass). No block.

### F2
fired: true

Predicate: two or more mandatory dimensions score 'warn' or worse. D1 = warn and D2 = warn; two mandatory dimensions meet the threshold.

### F3
fired: false

Predicate: any high-priority dimension scores 'block'. D4 is the only high-priority dimension and scores warn, not block.

### F0
fired: false

Predicate: every mandatory dimension scores 'pass'. D1 and D2 score warn.

## Review Body

The domain seat's verdict on this manuscript is that its execution and its calibration are sound and its positioning is not. I want the record to be explicit on the first half, because a panel reading a 1,600-word single-coefficient survey has a standing temptation to supply the overclaim it expects to find. There is none here. The causal disclaimer appears in six sections. Self-report is marked as self-report at every point where a behavioural reading would have been more flattering. The single-site limit is stated three times. The effect is characterised as moderate, with a confidence interval, an exact n, a robustness check, and an acknowledgement of the variance left unexplained. Any review of this paper whose substance is "correlation is not causation" and "self-report is not behaviour" is a review of a different manuscript.

What the manuscript does not do is establish that the field should care. Its stated contribution is accumulation — one comparable estimate added to a distribution of estimates, with Song (2018) invoked for the idea. That claim carries the entire justification for publication, and the manuscript never discharges it. Not one competing coefficient is quoted anywhere, so no reader can determine whether r = .42 is confirmatory, discrepant, or already superseded. Nor are the descriptors supplied that would make the comparison meaningful even if the comparators were present: whether LMS use was required in these students' courses, on what platform, across which disciplines. The omission is sharpened by the manuscript itself, which twice identifies course requirements and assessment structure as principal drivers of the outcome and then declines to say where its own institution stands on them. A paper that names the moderator and withholds its own value on it has not positioned its estimate; it has only asserted that positioning is possible.

Two further gaps sit at the construct level. The paper defines perceived usefulness correctly and then attributes the definition, and a claim about what the field has "long proposed," to sources from 2019 and 2020; the originating source is absent from the reference list entirely. And the paper borrows that construct, its instrument lineage, and its interpretive vocabulary while explicitly declining the framework that supplies all three. I am not asking for a model test — that would be commissioning a different study, and the descriptive scoping here is legitimate. I am asking what licenses the construct's standalone use and its commensurability with coefficients produced inside the framework. That is a paragraph, not a redesign. Relatedly, the instrument is warranted as "previously validated" while being reported as adapted, with no record of what changed; validation attaches to what was validated, and the manuscript claims a transfer it does not evidence.

The terminological slippage is smaller but sits in the worst possible place. The outcome is one self-reported access-frequency item. The abstract calls it engagement, in its opening sentence and again in the sentence readers carry away. In higher-education and learning-analytics usage engagement denotes a broader construct, and adjacent-field readers will read the broader thing. That is a wording fix, and it should be made.

On scoring: D1 and D2 are at warn, D3 at pass, D4 at warn, D5 at warn. I want to be explicit that D3 passes on the merits and not by omission — I checked the abstract, introduction, literature review, results, discussion, limitations, and conclusion for causal or directional framing and found the paper consistently associational, including in its practice implication. The construct-without-theory problem is a positioning and warrant defect, which I have charged once, under D2, rather than twice. Two mandatory dimensions at warn fires F2, and F2 is the highest-severity condition that fires from my scores.

I record two findings at Minor under the Step 5 discipline rather than at the severity my domain instinct would assign. The literature base — six sources, nothing after 2021, no post-TAM lineage — and the absent response rate both rest on claims about what an educational-technology venue expects, and I have not grounded those expectations in a venue policy or reporting guideline within this review. Both carry `[FIELD-NORM UNVERIFIED]`. Their substantive consequences are charged separately where they are internally grounded: the missing benchmark under W1 at Major, because the manuscript's own contribution claim requires it, and the unbounded selection risk noted as an internal tension in §6 with the sampling analysis left to Reviewer 1.

Every revision I have asked for is executable on the existing dataset. The authors need to report comparators, describe their setting, attribute their construct, document their adaptation, and say "self-reported access frequency" where they currently say "engagement." I would not ask them to add moderators, a second institution, log data, or a model; that advice belongs in Future Research, and pressing it would convert a deliberately narrow study into a different one. This paper's problem is not that it is small. It is that it has not yet shown the field where it fits.

## Editorial Decision

editorial_decision=major_revision

---

## SEAT — Peer Reviewer 3 (Perspective)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor.** As the outside-perspective seat, I read this dimension as asking whether the study's design and reporting would survive scrutiny not only from within educational technology, but from the adjacent fields that actually own the constructs in play. A cross-sectional self-report survey of perceived usefulness and self-reported LMS use sits squarely on terrain that psychometrics, survey methodology, and behavioural measurement research have already mapped: common-method variance when predictor and outcome share a single instrument and a single moment, the well-documented gap between self-reported and log-recorded system use, sampling frames that recruit through the very platform being studied. My reading of "rigor" here is therefore not a statistics audit — that belongs to Reviewer 1 — but whether the design's known-from-elsewhere limits are acknowledged and whether the reproducibility affordances (instrument wording, sampling procedure, response rate, analysis choices) let a reader from another discipline judge the study on its own terms.

**D2 — domain_accuracy.** For me this dimension is about whether borrowed constructs are represented faithfully to the disciplines they were borrowed from. "Perceived usefulness" is not a generic phrase; it is a TAM construct with a specific operational history in information systems research, and the LMS-adoption literature it now travels in has accumulated decades of qualification. The cross-disciplinary failure mode is importing a term while discarding its lineage — treating perceived usefulness as though it were an unproblematic proxy for value, or citing an adoption model without acknowledging that its own originating field has substantially revised it. I also read this dimension as covering whether the paper's characterisation of student behaviour is consistent with what neighbouring evidence bases (learning analytics, engagement research) already show.

**D3 — argumentative_coherence.** I approach this dimension from its assumptions rather than its logic gates; formal fallacy detection is the Devil's Advocate's remit and internal contradiction-hunting is not mine. What I ask is whether the chain from a correlation between two self-reported variables to whatever the paper concludes rests on premises that hold once you step outside the paper's own paradigm. The implicit assumptions in this genre are usually the interesting ones: that perceived usefulness precedes use rather than being rationalised after it, that more LMS use is a good in itself, that a student's report of their own behaviour is a measurement rather than a self-presentation. Coherence, in my reading, means the conclusions do not quietly require a stronger warrant than the design can issue.

**D4 — cross_disciplinary_relevance.** This is my home dimension, and I read it more demandingly than "is the prose accessible." Accessibility to adjacent-field readers is the floor: are constructs defined rather than assumed, is the context specified enough that a reader elsewhere can judge transferability, are the institutional and cultural particulars of the sample visible. Above that floor sits substantiation: if the paper reaches toward instructional design, human-computer interaction, learning sciences, or educational policy, do those reaches carry warrant, or are they gestures. And beneath both sits the question of who is missing — students as stakeholders with workload and access constraints, instructors whose design choices produce the LMS the students perceive, and students whose non-use reflects circumstance rather than attitude.

**D5 — writing_and_structure.** From an outsider's vantage this dimension is really about whether the manuscript gives a non-specialist reader the handholds needed to evaluate it: a clear statement of what was measured and how, tables or figures that report the actual distributions rather than only summary claims, and a structure where the limitations are load-bearing rather than decorative. At roughly 1,600 words, the paper is short for an empirical report, so I read structure partly as an allocation question — whether the available space is spent on what a reader from another field would need, or on framing that could be assumed.

## Scoring Plan

### D1: methodology_rigor
- **what_to_look_for**: Whether the single-instrument, single-timepoint design is named as such and its consequences engaged; whether self-reported use is distinguished from actual use, and whether any objective referent (LMS logs, timestamps) is available or its absence acknowledged; how the sample was recruited and whether the recruitment channel is entangled with the outcome (e.g., recruiting via the LMS); reported response rate and non-response handling; instrument provenance (adapted from a published scale vs. author-written) and reliability evidence; whether the analysis reported is one a reader from a neighbouring field could reproduce from the description given.
- **what_triggers_block**: The paper draws directional, causal, or effectiveness conclusions from cross-sectional self-report co-variation with no acknowledgement of the design's inferential ceiling — i.e., the limitations section either omits the common-method and self-report problems entirely or names them in a sentence that the conclusions then contradict. Also blocking: the sampling procedure is so underspecified that the population the findings are supposed to describe cannot be identified at all.
- **what_triggers_warn**: The design's limits are acknowledged but only pro forma — listed in a limitations paragraph without shaping the strength of the claims made elsewhere; or the instrument's origin and reliability go unreported; or response rate and sample composition are given too thinly for a reader outside the field to judge who is represented, while the conclusions remain appropriately hedged.

### D2: domain_accuracy
- **what_to_look_for**: Whether "perceived usefulness" is defined and traced to its construct lineage rather than used as an everyday phrase; whether the adoption framework invoked is represented as its own literature currently represents it, including known revisions and criticisms; whether "use" is operationally defined (frequency? duration? which features?) or left as an undifferentiated quantity; whether claims about student behaviour or LMS effects are stated at a strength the cited evidence base actually supports; whether terminology imported from information systems, learning analytics, or instructional design is used consistently with those fields' meanings.
- **what_triggers_block**: A core construct is materially misrepresented — the paper attributes to perceived usefulness, to the adoption model it invokes, or to prior findings something those sources do not say, and that misrepresentation carries the paper's central claim. Also blocking: the paper asserts an established empirical relationship as settled domain fact when the cited or citable evidence is genuinely contested.
- **what_triggers_warn**: Constructs are used loosely but not wrongly — borrowed terminology deployed without definition, an adoption framework cited in its original form with no acknowledgement of subsequent qualification, or "LMS use" left operationally vague such that an adjacent-field reader cannot tell what behaviour was measured. Also warn-level: prior work is characterised accurately but flatly, in a way that overstates consensus without stating anything false.

### D3: argumentative_coherence
- **what_to_look_for**: The implicit premises the argument needs but does not state — that perceived usefulness causes use rather than following it, that greater LMS use indicates greater learning or engagement, that self-report tracks behaviour, that the platform's affordances are constant across the sample; whether the conclusion's verbs stay within what a correlational design licenses; whether the practical or policy implications drawn actually follow from the finding rather than from the topic; whether alternative explanations of the same pattern (course design requiring LMS use, assessment mechanics, differential access) are entertained.
- **what_triggers_block**: The central conclusion requires a premise the paper neither states nor defends and that is contestable on its face — most likely a causal or effectiveness claim ("improving perceived usefulness will increase use / engagement / learning") resting on cross-sectional association, or an implication for practice that only follows if use is assumed to be intrinsically beneficial. The argument does not survive the removal of the unstated premise.
- **what_triggers_warn**: The assumptions are present and unexamined but the claims stay correspondingly modest — associations reported as associations, implications phrased as possibilities — while at least one plausible alternative explanation for the observed pattern is left entirely unconsidered. Also warn-level: the framing sets up a stronger question than the design answers, and the mismatch is never reconciled.

### D4: cross_disciplinary_relevance
- **what_to_look_for**: Whether constructs and instruments are explained sufficiently for a reader from instructional design, HCI, learning sciences, or education policy to follow without prior TAM fluency; whether the institutional, national, disciplinary, and platform context of the sample is specified enough to let readers elsewhere judge transferability; whether stakeholders beyond the surveyed students appear — instructors who design the LMS experience, institutions that mandate its use, students whose access is constrained by device, connectivity, or disability; whether the paper's practical recommendations are implementable given real institutional resources; whether any interdisciplinary claim it does make carries warrant beyond assertion.
- **what_triggers_block**: The paper makes interdisciplinary or generalising claims it cannot substantiate — presenting findings from one institutional and cultural context as general truths about students or about LMS platforms, or asserting implications for learning, pedagogy, or policy without engaging the fields that own those claims. Also blocking at this level: recommendations directed at practitioners that are infeasible or that ignore the equity consequences of pushing platform use onto students with unequal access, presented with no acknowledgement of either.
- **what_triggers_warn**: Findings are reported responsibly but hermetically — context underspecified so that transferability cannot be assessed, constructs assumed rather than defined for outside readers, or a single stakeholder voice (surveyed students) standing in for a system that visibly includes others. Also warn-level: implications gestured at adjacent fields without engagement, and equity or access dimensions of LMS use noted nowhere despite being directly implicated by the topic.

### D5: writing_and_structure
- **what_to_look_for**: Whether an outside reader can locate, in order, what was asked, of whom, how, and what was found; whether tables or figures report the underlying distributions and instrument items rather than only conclusions; whether limitations are positioned to constrain the claims rather than parked at the end; whether the ~1,600-word budget is allocated to method and results or consumed by generic framing; whether venue conventions for reporting survey research (sample description, instrument appendix or summary, ethics and consent statement) are met.
- **what_triggers_block**: The manuscript omits a section a reader needs to evaluate it at all — no reportable method, or results presented without the numbers behind them — such that the study cannot be assessed independently of the authors' own summary of it.
- **what_triggers_warn**: All components are present but thin or misproportioned — method or results compressed below the point of interpretability while introduction and discussion run long; tables that restate the text without adding data; missing ethics/consent statement or instrument summary; organisation that forces the reader to reconstruct the study's logic from scattered pieces.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Perspective Review Report (Peer Reviewer 3)

### Reviewer Identity

Director of Learning Technology and Academic Analytics at a large public university. I am a platform owner rather than an academic researcher: I run LMS procurement, onboarding programmes, and the institution's engagement dashboards, and I have repeatedly had to explain to senior leadership why login frequency is a poor proxy for learning. I read this manuscript from the seat that would have to act on it, and I say up front that measurement theory, statistical execution, and literature coverage are not my competence — three colleagues on this panel own those, and I defer to them there.

### Overall Recommendation

Major Revision

### Confidence Score

4 — high confidence on construct relevance, equity/access, stakeholder completeness, and practice actionability; lower on psychometrics and literature coverage, which I have not attempted to assess.

### Summary Assessment

This is a careful, honest manuscript, and I want to be precise about where my objections land, because most of the criticisms a reviewer would reflexively raise against a single-site LMS survey have already been pre-empted by the authors. Causality is disclaimed with the reverse pathway named explicitly; self-report is framed as perceived rather than actual use and that framing is carried consistently across four sections; the ethics surface is complete; the residual variance is acknowledged rather than buried.

My concerns sit elsewhere, in the space between the coefficient and the decision it invites. The outcome variable — how often a student accesses the LMS — is never argued to be a desirable thing, yet it is verbally upgraded to "engagement" in the abstract and literature review. Nothing in the manuscript tells me who these 214 students are or where they study, which defeats the paper's own stated purpose of contributing a comparable point in a distribution. Material conditions that plainly shape both variables — device access, connectivity, commuting, paid work — appear nowhere. And the one practice lever the paper recommends is not the lever its own results point at. None of these require a new study; all are framing, bounding, and disclosure fixes to the manuscript in hand.

### Strengths

1. **The reverse pathway is named, not merely disclaimed**: Most papers in this genre write "correlation does not imply causation" and move on. This one specifies the alternative: "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data" (§5). From my seat this is the single most useful sentence in the manuscript — it is what I would quote to a leadership team tempted to fund the wrong thing.
   - **Evidence Anchor**: `text: §5 Discussion — "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"`

2. **Construct discipline is structural rather than decorative**: The self-report-is-not-behavior qualification appears in §2 with a supporting source, again in §3.2 as an interpretive commitment ("We treat this as an ordinal indicator of self-reported use"), and again in §6. It shapes the language of §5 and §7 rather than being parked in Limitations. Papers that hedge only in the limitations paragraph are common; this one does not.
   - **Evidence Anchor**: `text: §3.2 — "We treat this as an ordinal indicator of self-reported use and interpret it accordingly"`

3. **Unexplained variance is acknowledged and attributed to plausible structural causes**: §4 states that reported engagement "reflects many influences beyond perceived usefulness, including course requirements and assessment schedules." That is the correct next question, and the authors handed it to the reader unprompted.
   - **Evidence Anchor**: `text: §4 Results — "including course requirements and assessment schedules"`

4. **The ethics surface is complete for a student-facing platform survey**: Approval, voluntariness, anonymity, informed consent, and — a detail I notice specifically because it is so often missed — the explicit absence of course credit or payment (§3.3). Incentivised LMS surveys systematically distort the population you are trying to measure; declining incentives is a real methodological choice, not boilerplate.
   - **Evidence Anchor**: `text: §3.3 — "no course credit or payment was offered"`

5. **Declared scope and delivered scope match**: §1 announces "a deliberately narrow question" and §7 does not exceed it. I checked the abstract, §1, §5, and §7 for the usual drift and found none in the causal register.
   - **Evidence Anchor**: `text: §1 Introduction — "It asks a deliberately narrow question"`

### Weaknesses

1. **The outcome variable's worth is never argued, and it is verbally upgraded en route**: The dependent variable is how often a student accesses the LMS in a typical week (§3.2). Nothing in the manuscript argues that more frequent access is desirable. §1 inherits that premise from the institution ("Institutions invest heavily in these platforms on the assumption that availability translates into use") and never returns to it. Meanwhile the term drifts: the abstract closes on "perceived usefulness tracks with LMS engagement," and §2 speaks of students' "engagement with it." In my field, engagement is not access frequency — a well-designed course requiring three deliberate visits per term and a badly designed one forcing daily hunting for materials score in opposite directions on this scale, and the badly designed course wins. **What I am asking for is a paragraph, not a study**: state explicitly what use frequency is intended to proxy for, state what it demonstrably does not proxy for, and either retire "engagement" as a synonym or define it as the authors are using it. This is a framing-and-bounding fix.
   - **Severity**: Major | **Evidence Anchor**: `text: Abstract — "perceived usefulness tracks with LMS engagement among undergraduates"; cf. §3.2 — "how often the respondent accessed the LMS in a typical week"` | **Confidence**: 5 — I build and defend the engagement dashboards that make exactly this conflation, and have had to unmake it in front of senior leadership.

2. **Material conditions are absent from a study whose outcome they directly determine**: §6 lists four limitations — single site, self-report, cross-sectional design, voluntary response. None concerns access. In my institution's own internal evaluations, low reported LMS use tracks device sharing, unreliable home connectivity, commuting time, and paid-work schedules at least as strongly as it tracks attitude. If those conditions depress both variables — a student who cannot reliably reach the system does not find it useful, because for them it is not — then some unknown share of r = .42 is material circumstance wearing the costume of perception. No demographic or access variables were collected, so this cannot be tested here, and I am not asking the authors to test it. I am asking for it to appear in §6 as a named third-variable explanation with a stated direction, and for §5's practice implication to be bounded accordingly. There is an equity stake in leaving it out: a paper that reads low use as low perceived usefulness invites institutions to respond with persuasion when the constraint is a laptop.
   - **Severity**: Major | **Evidence Anchor**: `absence: no access, device, connectivity, employment, or commuting variable appears in §3.1 (participants), §3.2 (measures), §4 (results), or §6 (limitations) — all four surfaces checked` | **Confidence**: 4 — grounded in practitioner field experience and internal institutional evaluations; I cannot estimate the magnitude of the confound in this specific sample.

3. **The paper's stated purpose is transferability, and the manuscript withholds what transferability requires**: §2 and §7 position this as "an incremental data point, comparable with prior work," and §2 endorses Song's (2018) framing of any single-site estimate as one point in a distribution. To place a point in a distribution I need to know where the point sits. The manuscript tells me "one mid-sized public university" (§3.1) and that the sample "spanned all four year levels." It does not tell me the country or region, the disciplinary mix, whether teaching is on-campus, hybrid, or online, which platform is in use, what the response rate was against what eligible population, or anything about who answered. As the person who would decide whether this estimate is relevant to my campus, I cannot make that judgement from what is here — which means the paper's central contribution claim is asserted rather than delivered. A participant-characteristics table and a short setting paragraph close this entirely.
   - **Severity**: Major | **Evidence Anchor**: `text: §3.1 — "one mid-sized public university"; combined with absence: no participant-characteristics table, no response rate, no denominator, no platform, delivery mode, or national context anywhere in §3.1–§3.4` | **Confidence**: 5 — this is precisely the judgement my role requires me to make about published estimates, and I make it routinely.

4. **The recommended lever is not the lever the paper's own results nominate**: §5 offers LMS onboarding that demonstrates concrete usefulness as the institutional implication. But §4 attributes the unexplained variation to "course requirements and assessment schedules" — that is, to instructor and assessment design. The paper's own text therefore points at a stronger lever than the one it recommends, and instructors, who construct the very LMS experience students are rating, never appear as stakeholders in the design, the sample, or the recommendation. Compounding this, the paper concedes in the same section that the reverse causal path is equally consistent with the data, which means the correlation cannot distinguish "help students see usefulness → they use it more" from "required use → they retrospectively rate it useful." As someone who has had to justify continued onboarding investment: this correlation cannot fund that decision. **Suggested repair**: recast §5's implication as a hypothesis worth testing rather than a direction worth attention, and add a sentence naming course and assessment design — and thus instructors — as the alternative lever the study did not measure.
   - **Severity**: Major | **Evidence Anchor**: `text: §5 — "LMS onboarding which helps students see concrete usefulness ... may be worth institutional attention"; cf. §4 — "including course requirements and assessment schedules"` | **Confidence**: 5 — I have run the internal evaluations that decide whether onboarding investment continues.

5. **No statement of why institutional log data were not used or sought**: Every institution running an LMS holds complete behavioural traces for the exact construct this study approximated by self-report. §6 names the self-report limitation but never addresses the obvious practitioner question: the data existed, so why the survey? An ethics-approval constraint, a governance restriction, an unavailability of institutional-research support, or a deliberate interest in perception rather than behaviour would each be a perfectly good answer — the paper simply needs to give one. As written, a reader cannot tell whether self-report was a constraint or a convenience, which affects how much weight to place on the estimate. One or two sentences in §3.4 or §6.
   - **Severity**: Minor | **Evidence Anchor**: `absence: no rationale for the self-report design choice appears in §3.1, §3.3 (ethics), §3.4 (analysis), or §6 (limitations) — all four checked` | **Confidence**: 5 — I hold this data at my own institution and know both the access routes and the governance constraints on it.

6. **The instrument is not reportable to a reader outside the field**: The six perceived-usefulness items are never shown, the nature of the adaptation from Costa and Wren (2019) is not documented, and the frequency scale is only partially specified — §3.2 gives anchors 1 and 5, while §4 reports a median category, "a few times per week," that does not appear among them. I cannot locate the reported median on the scale as described. For a paper whose contribution is comparability with other estimates, the instrument surface is the thing most needed and least supplied. An appendix with the six items, a note on what was changed in adaptation, and the full five response labels resolve this.
   - **Severity**: Minor | **Evidence Anchor**: `text: §3.2 — "1 = rarely or never to 5 = several times daily"; cf. §4 — "a median category of 'a few times per week'"` | **Confidence**: 4 — the reporting gap is plain on the page; whether the adaptation itself is sound is Reviewer 1's determination, not mine.

### Detailed Comments

#### Assumption Audit

- **Explicit assumptions**: The stated premises are unusually modest and mostly hold. The paper explicitly assumes only that perceived usefulness and self-reported use are both measurable by questionnaire and that their association is worth documenting. It explicitly declines the larger assumption — that an acceptance model is being tested — and says so in §1 and §2. I found no explicit assumption that fails cross-disciplinary scrutiny.

- **Implicit assumptions**: Two, both consequential. The first is that **more LMS use is better**, or at least that variation in use frequency is a phenomenon worth explaining in the direction of increasing it. This premise is inherited from the institutional framing in §1 and is never examined; it is what makes §5's onboarding implication legible as a recommendation rather than as a neutral observation. Remove it and the practice implication loses its point, though the descriptive finding survives intact — which is why I score this a warning rather than a structural failure. The second is that **reported use reflects disposition rather than circumstance**. The paper carefully distinguishes reported from actual use, which is a measurement caution; it does not consider that reported use might be accurate and still be a measure of what a student's material conditions permit rather than what their attitude produces. That second assumption is invisible from inside the technology-acceptance frame and highly visible from an operations seat.

- **Paradigmatic assumptions**: The technology-acceptance paradigm treats the individual student's perception as the unit of analysis and the locus of variation. From a systems perspective, the LMS a student perceives is not a fixed object: it is an artefact assembled by instructors, course designers, and assessment policy, and it differs materially between two students at the same institution in the same week. The paper's own §2 (via Ibarra and Poll) and §4 both gesture at this, but the design cannot accommodate it, because the platform is treated as constant across the sample. I note this as a boundary condition on the paradigm, not as a defect the authors should have avoided — it is standard practice in their field, and I flag it in the spirit of "this may be conventional in acceptance research, but from a platform-operations perspective it hides most of the variance."

#### Cross-Disciplinary Connections

- **Parallel research**: The learning-analytics literature has spent a decade on precisely the question this paper approaches by survey — how self-reported platform use relates to trace-derived use — and has produced the finding that the two correlate far less well than researchers assume. The manuscript's sole representative of this literature is Vasquez (2020), cited once. The relevant point for the authors is not "cite more" (that is Reviewer 2's territory) but that this literature offers a defensible way to *bound* their estimate rather than merely disclaim it.

- **Borrowing opportunities**: Two concepts would materially strengthen the paper at low cost. First, the multidimensional treatment of **student engagement** as behavioural, emotional, and cognitive — borrowing this vocabulary would force the terminological precision that W1 asks for, and would let the authors say exactly which sliver of engagement their item touches. Second, the information-systems distinction between **frequency, duration, depth, and feature-breadth of system use** — this would let the authors state, in one sentence, that they measured the least informative of the four and why that was nevertheless a reasonable choice.

- **Methodological borrowing**: I will not ask for a different study. But I will note that the cheapest available strengthening is not longitudinal design or log linkage — it is the addition of two or three access-condition items to the existing questionnaire (device availability, connectivity reliability, weekly paid-work hours), which would convert the equity confound from an unexaminable worry into a testable covariate at essentially zero marginal cost. I raise this as a note for future work, not as a revision requirement for this manuscript.

#### Practical Impact

- **Real-world application**: What could I do with this on Monday morning? Honestly: very little, and the paper's own hedging correctly signals as much. A moderate correlation of undetermined direction between a perception and a self-reported frequency does not identify an intervention. The paper is at its most useful not as a decision input but as a caution — its §5 concession that the reverse path is equally consistent is the sentence a practitioner should carry away. The risk of "academically meaningful but practically inert" is present here, and I do not think it is fatal, because the authors do not claim otherwise. The risk becomes real only in §5's onboarding sentence, which is the one place a hurried reader could extract a spending decision the design cannot support.

- **Implementation feasibility**: Onboarding-that-demonstrates-usefulness is entirely feasible — it is routine institutional work, not an infrastructure demand, and I have funded versions of it. My objection is not feasibility but attribution: I would be funding it on the strength of a correlation that the authors themselves say could run the other way. The unintended consequence worth naming is that institutions under pressure to raise dashboard engagement numbers will reach for the cheapest lever, and persuasion is cheaper than course redesign or device provision. A paper that identifies perception as the correlate of use, without bounding that finding, makes the cheap lever look evidence-backed.

- **Stakeholders**: Students are surveyed. Instructors — who determine whether visiting the LMS is necessary at all — are absent from the design, the sample, and the recommendation, appearing only as an unmeasured influence in §4. Institutional administrators appear as investors in §1 and as onboarding actors in §5, but their actual decision needs are not addressed. Students who did not respond, and students whose non-use reflects circumstance rather than attitude, are structurally invisible: voluntary response through an announcement channel is acknowledged in §6 as a limitation, but the specific group most relevant to my concerns — students who are hardest to reach through institutional channels because of the same constraints that suppress their LMS use — is the group least likely to be in this sample and is never named as such.

#### Broader Implications

- **Ethical dimensions**: The human-subjects surface is properly handled (§3.3). The ethical question I would raise is different and is about framing rather than procedure: treating platform access frequency as the object of institutional improvement effort, without stating what it is a proxy for, quietly ratifies an instrumentalist view of student behaviour in which clicks are the thing being optimised. The authors have not endorsed that view; they have also not declined it, and the abstract's "engagement" phrasing leans toward it.

- **Social impact**: The equity dimension is the most significant absence in the manuscript and is directly implicated by the topic. If reported LMS use partly indexes device access, connectivity, and time poverty, then an institution acting on this paper's implication would direct resources toward changing the perceptions of students who are already well-resourced, while the students whose use is genuinely constrained receive an onboarding session they may not be able to attend. I want to be fair: nothing in the manuscript advocates this, and the authors could not have detected it with the data they collected. But a limitations section that names four constraints and omits this one leaves the reader without the warning.

- **Future directions**: The highest-value follow-up from my seat is not the log-data study the conclusion proposes, valuable though that is. It is a design that treats the LMS as a variable rather than a constant — pairing student perception with course-level design characteristics (assessment structure, materials placement, instructor posting frequency) to ask whether student-level perception explains anything once course-level design is accounted for. My operational expectation, which the authors are free to disagree with, is that it would explain considerably less.

### Cross-Disciplinary Reading Recommendations

Per the no-invention rule, I can attest to no specific external citation from this session's materials, so every item below is a search lead rather than a citation. None carries author or year metadata, because I would be guessing.

- **[UNVERIFIED] search lead** — Learning analytics on the concordance between self-reported and trace-derived platform use (search terms: *self-report versus trace data LMS*, *clickstream engagement validity*, *survey–log discordance higher education*). Relevance: lets the authors bound their estimate quantitatively rather than disclaim it qualitatively, addressing W1 and W5.
- **[UNVERIFIED] search lead** — The student-engagement construct literature distinguishing behavioural, emotional, and cognitive dimensions (search terms: *multidimensional student engagement construct*, *behavioural engagement operationalisation*). Relevance: supplies the vocabulary to fix the abstract's "engagement" slippage precisely rather than by deletion.
- **[UNVERIFIED] search lead** — Digital equity and digital-divide research in higher education, particularly on device ownership, home connectivity, commuter and working students (search terms: *digital divide higher education device access*, *commuter student technology access*, *working students online learning constraints*). Relevance: the direct source base for W2's third-variable explanation.
- **[UNVERIFIED] search lead** — Information-systems work distinguishing dimensions of system use — frequency, duration, depth, feature breadth (search terms: *deep structure usage*, *rich versus lean system use*, *IS use construct dimensionality*). Relevance: gives the authors a principled one-sentence justification for measuring frequency, which is currently unstated.
- **[UNVERIFIED] search lead** — Governance and ethics of secondary use of LMS trace data for institutional research (search terms: *learning analytics data governance consent*, *secondary use LMS logs ethics approval*). Relevance: would let the authors give the missing W5 explanation with a citable basis if a governance constraint is in fact the reason.

### Questions for Authors

1. What is self-reported access frequency a proxy for? Please answer in the manuscript, in one or two sentences, and please also say what it is not a proxy for. If the answer is "nothing beyond itself — we report frequency as frequency," that is a perfectly acceptable answer and would resolve most of my first weakness; but then "engagement" should not appear as its synonym in the abstract or §2.
2. Your institution holds complete LMS logs for the construct you approximated by self-report. Why were they not used or sought? A governance constraint, an ethics-approval boundary, or a deliberate interest in perception over behaviour would each fully answer this — the manuscript simply needs to say which.
3. Were any access or circumstance variables collected — device, connectivity, employment hours, commuting — even if not analysed? If not, would you accept that unmeasured material conditions constitute a plausible third-variable explanation for part of the observed association, and add it to §6 with a stated expected direction?
4. Your §4 attributes residual variance to course requirements and assessment schedules — that is, to instructor and course design. Your §5 recommends student onboarding. Why is the recommendation aimed at the population your own results suggest is not where the leverage sits?
5. Your paper asks to be read as one point in a distribution of estimates. What would a reader at another institution need to know about your setting to place your point in that distribution — and would you be willing to supply it as a participant-characteristics table and a short setting paragraph?

### Minor Issues

- The reported median use category, "a few times per week" (§4), is not among the response anchors given in §3.2; a reader cannot locate it on the scale as described.
- "Use" and "engagement" are used interchangeably across the abstract, §2, and §4 while the measure supports only the former.
- Whitfield (2019) is introduced for the first time in the Discussion as the source for the onboarding implication, without having been established in the literature review.
- Neither the LMS platform nor the country/region of the institution is identified anywhere, and both bear on transferability.
- No delivery-mode descriptor (on-campus, hybrid, fully online) is given, though it plausibly conditions baseline access frequency more than any attitudinal variable.

---

contract_role: perspective

## Dimension Scores

### D1: methodology_rigor
score: warn

The design's inferential ceiling is not treated pro forma — the cross-sectional limit is engaged in §1, §5, §6, and §7, and the self-report/behaviour distinction is carried across four sections rather than parked at the end. My Phase 1 block trigger therefore does not fire, and I record that explicitly so the synthesiser can distinguish "handled" from "unchecked." What fires is the third clause of my warn trigger: response rate and sample composition are given too thinly for a reader outside the field to judge who is represented. There is no response rate, no eligible-population denominator, and no participant description beyond "spanned all four year levels" and "one mid-sized public university." Separately, the instrument's adaptation is undocumented and the response-scale wording is incomplete. Conclusions remain appropriately hedged throughout, which is why this is warn and not block.

### D2: domain_accuracy
score: warn

No core construct is materially misrepresented and no contested relationship is asserted as settled — §2 explicitly notes that effect sizes vary across samples and instruments. Perceived usefulness is defined rather than assumed. What fires is my warn trigger's operational-vagueness clause, in its sharper form: "LMS use" is measured as undifferentiated access frequency, with no statement of what counts as an access, and is then verbally equated with "engagement" in the abstract and §2. In the learning-analytics and engagement literatures those are not the same construct, and the substitution imports a claim the item cannot carry. The central finding is stated in use terms in §5 and §7 and survives without the substitution, which is why this stops at warn.

### D3: argumentative_coherence
score: warn

I read this dimension for load-bearing unstated premises, not for formal fallacies, which are the Devil's Advocate's remit. Two implicit premises are present and unexamined: that greater LMS use is desirable, and that reported use indexes disposition rather than circumstance. My block trigger requires that the argument not survive removal of the unstated premise; the central descriptive conclusion in §7 does survive — only §5's practice implication depends on the use-is-good premise, and that implication is already triple-hedged ("modest support," "may be worth institutional attention," "suggested by, not proven by"). Warn therefore fires on my committed pattern: assumptions unexamined while claims stay correspondingly modest, with at least one plausible alternative explanation left entirely unconsidered — here, material access conditions as a common cause of both variables, absent from §6's four-item limitations list.

### D4: cross_disciplinary_relevance
score: warn

Both of my warn clauses fire. Context is underspecified to the point where transferability cannot be assessed — no country, sector detail, platform, delivery mode, disciplinary mix, demographics, or response rate — which is a self-inflicted wound given the paper's own claim to be a comparable point in a distribution. And equity and access are noted nowhere despite being directly implicated by a study of how often students can reach an online system. My block trigger does not fire: the paper does not present its findings as general truths (single-site limits are stated in the abstract, §6, and §7), and its practitioner recommendation is feasible and non-coercive rather than infeasible or access-blind by mandate. Instructors, who construct the artefact being rated, are absent as stakeholders — a single surveyed voice standing in for a system that visibly includes others.

### D5: writing_and_structure
score: warn

No required section is missing and the results carry their numbers, so my block trigger does not fire; organisation is conventional and the prose is clear, with the "in plain terms" gloss in §4 an asset for outside readers. Warn fires on the instrument-summary and reporting-surface clause: the six perceived-usefulness items are never shown, the adaptation is undocumented, the response-scale categories are incompletely specified such that the reported median cannot be located on the scale, and there are no tables or figures at all — including no participant-characteristics table, which for survey research is a venue convention rather than an optional extra. Ethics and consent are present and complete, and I credit that.

## Failure Condition Checks

### F1
fired: false

Predicate: any mandatory dimension scores 'block'. Mandatory dimensions are D1, D2, D3; I scored all three warn. No block on any mandatory dimension.

### F2
fired: true

Predicate: two or more mandatory dimensions score 'warn' or worse. D1 warn, D2 warn, D3 warn — three of three mandatory dimensions at warn, exceeding the threshold of two.

### F3
fired: false

Predicate: any high-priority dimension scores 'block'. D4 is the sole high-priority dimension and I scored it warn, not block.

### F0
fired: false

Predicate: every mandatory dimension scores 'pass'. None of D1, D2, D3 scored pass.

## Review Body

I applied my Phase 1 scoring plan without deviation and record no dissent. Every trigger I fired is one I committed to before seeing the manuscript, and — because the field analysis warned this panel that its dominant risk is manufacturing overreach rather than missing it — I state affirmatively that none of my findings rests on the criticisms this manuscript has already pre-empted. It disclaims causation and names the reverse pathway; it distinguishes self-report from behaviour and sustains that distinction across sections; it bounds itself to one institution three times; it reports a confidence interval, an exact n, a robustness check, a power statement, and an assumption inspection; it covers approval, consent, anonymity, and the absence of incentives. A reviewer raising any of those here would be reviewing a generic weak survey, not this one.

My objections are of a different kind, and they concentrate at the seam between the coefficient and the decision it invites. The outcome variable is access frequency, and the manuscript never argues that more of it is good. It inherits that premise from the institutional framing of §1 and then, in the abstract and §2, quietly renames it: access frequency becomes "engagement." From an operations seat these are not near-synonyms but near-opposites in the cases that matter — a course requiring three deliberate LMS visits per term and a course whose materials are so badly organised that students must hunt daily would rank in opposite directions on this item, with the badly organised course scoring higher. The repair is a paragraph, not a study: say what frequency proxies for, say what it does not, and either retire "engagement" or define it as used.

The second concentration is who is missing. The manuscript surveys students and recommends to institutions, but the LMS a student perceives is assembled by instructors through assessment structure, materials placement, and posting behaviour, and instructors appear only as an unmeasured influence in §4. The paper's own residual-variance sentence nominates course requirements and assessment schedules as where the unexplained variation lives, then §5 recommends student onboarding — the paper points at one lever and reaches for another. Beneath that sits an absence with equity stakes: material conditions. Device sharing, unreliable connectivity, commuting time, and paid-work hours plausibly depress reported use and perceived usefulness together, which would make some share of r = .42 circumstance dressed as attitude. No such variable was collected, so it cannot be tested here and I am not asking for it to be; I am asking for it to be named in §6 as a third-variable explanation with a stated direction, and for §5 to be bounded accordingly. §6 currently names four limitations and this is not among them, which leaves a reader free to interpret low use as low enthusiasm and to respond with persuasion when the binding constraint is a laptop.

The third concentration is that the paper's declared contribution is not delivered. §2 and §7 ask to be read as one comparable point in a distribution of estimates. To place a point in a distribution a reader must know where it sits, and the manuscript supplies "one mid-sized public university" and four year levels — no country, no platform, no delivery mode, no disciplinary mix, no demographics, no response rate against any denominator. As the reader this paper is implicitly written for, the person deciding whether an outside estimate transfers to their own campus, I cannot make that judgement from what is here. That, together with an instrument whose items are never shown and whose response categories are incompletely specified, is why my structural and relevance dimensions both warn.

I want to be clear about what I am not asking for, because my seat carries a known risk of scope creep. I am not asking for log data, a second institution, a longitudinal design, a moderator, or a theoretical model. Every finding above is answerable within the existing dataset and manuscript: a construct-purpose paragraph, a named third-variable limitation, a participant-characteristics table and setting paragraph, a rebalanced practice implication, a one-sentence rationale for the self-report design, and an instrument appendix. That is a substantial but bounded revision package, and it is the reason my scores are uniformly warn rather than block. This is a well-made study that has been reported for its own field and not yet for anyone standing outside it.

## Editorial Decision

Three of three mandatory dimensions scored warn, which satisfies F2 (severity 70). F1 and F3 did not fire, as I recorded no block on any dimension, and F0 is excluded by the warns. F2 is therefore the highest-severity fired condition among my own scores, and its action governs.

editorial_decision=major_revision

---

## SEAT — Devil’s Advocate

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor.** The contract asks whether study design, data handling, statistical reporting, and reproducibility affordances clear the field's peer-review bar. As Devil's Advocate I do not re-run the Methodology Reviewer's design audit; I read this dimension for the point where methodological weakness becomes an *argumentative* liability — the place where a design choice quietly determines the conclusion the paper reaches. My question is not "was the procedure adequate?" but "if a hostile reader assumed the worst about how these data were produced, would the paper's central claim survive?" For a cross-sectional survey of undergraduates on perceived usefulness and self-reported use, the adversarial reading is that design and measurement are the same instrument: both constructs are self-report, collected at one moment, from one convenience-shaped population, and any relationship between them may be an artefact of that arrangement rather than a finding about it. I will treat unreported sampling frame, response rate, non-response comparison, or measurement provenance not as tidiness complaints but as gaps that make the headline claim unfalsifiable from the manuscript alone.

**D2 — domain_accuracy.** The contract asks whether claims align with current domain evidence, whether prior work is correctly represented, and whether domain terminology and results are factually right. My adversarial angle is asymmetry rather than coverage — checking literature *completeness* belongs to the Domain Reviewer, so I will not count missing citations. I will look instead for evidence selection that tilts one way: prior work cited when it agrees, characterised loosely when it disagrees, or absent precisely where the field's known null and mixed results live. LMS adoption in higher education is a domain with a dominant borrowed theory (TAM and its descendants) and a well-documented critique of that theory's central assumption, so the sharpest domain-accuracy failure available here is not a wrong fact but a theoretical frame imported without its own known limitations, presented as settled. I also treat mis-transfer of a construct's established meaning — using a validated instrument's label for an unvalidated item set, for instance — as a domain-accuracy defect, because it borrows credibility the paper has not earned.

**D3 — argumentative_coherence.** The contract asks whether the core thesis is internally consistent, whether the evidence actually supports the claims, and whether fallacies undermine the central argument. This is my home dimension and the one I will press hardest. My standard is the logic chain: premise → evidence → conclusion, with every hidden step made visible. The structural hazard implied by the metadata is that "perceived usefulness" and "self-reported use" are both perceptions reported by the same person at the same time, so an observed association is compatible with at least three explanations the paper must beat — common-method variance, reverse direction (people who use a system rationalise it as useful), and a third factor (course requirement, instructor mandate) driving both. I will also test whether the paper's own hedges are consistent with its own conclusions: a limitations paragraph that concedes correlation while an abstract or implications section prescribes action is not caution, it is a contradiction the paper has published on both sides of. Coherence failures here are gradable by decision impact, not by how forcefully the paper asserts itself.

**D4 — cross_disciplinary_relevance.** The contract asks whether framing, definitions, and implications are accessible to adjacent-field readers, and whether interdisciplinary claims are substantiated. Adversarially, I read this as a test of whether the paper's constructs mean anything outside the sentence that introduced them. "Perceived usefulness" and "use" are terms borrowed across information systems, education, and psychology, and each field operationalises them differently; a paper that does not fix its own definition invites every reader to supply a favourable one. The failure mode I hunt is *borrowed authority* — invoking a neighbouring discipline's theory, construct, or instrument as a warrant while importing none of that discipline's evidentiary obligations. I also read the implications for scope creep across field boundaries: a survey of undergraduates at one point in time that concludes with recommendations for institutional policy, instructional design, or vendor selection has crossed a disciplinary line its evidence does not reach. Note this dimension is `high` priority, not mandatory — under F3 a `block` here still forces major revision, so I will not treat it as a soft dimension.

**D5 — writing_and_structure.** The contract asks about organisation, clarity of exposition, figure and table quality, and venue conventions. I hold this dimension to a deliberately narrow adversarial reading, because prose polish is the easiest place for a Devil's Advocate to manufacture severity out of taste. I score here only when structure or presentation does *argumentative* work: when a result is reported in a form that cannot be checked (an effect with no interval, no n, no exact statistic), when the section ordering conceals that a claimed analysis was never performed, or when a table and the surrounding text disagree. Given a 1,597-word manuscript, I additionally expect that brevity itself becomes an evidentiary problem — at that length something reportable has been left out, and I will judge whether the omission is compression or concealment. Aesthetic complaints, house-style deviations, and citation formatting are explicitly out of my seat's scope and will not be scored here.

## Scoring Plan

### D1: methodology_rigor
- **what_to_look_for**: Whether the sampling frame, recruitment route, and response rate are stated at all, and whether the achieved sample is described well enough for a reader to know who is missing; whether "self-reported use" is defined as a measurable quantity (frequency, logins, hours) or left as an ordinal impression; whether the instrument's items, scale anchors, and any reliability evidence are reproducible from the text; whether analyses reported were specified before the data were seen or selected after; whether a single-timepoint design is acknowledged as constraining what can be inferred; whether common-method safeguards (marker variable, procedural separation, Harman-type check) are present or absent; whether any raw-data, instrument, or ethics/consent statement exists. Every absence I score will be recorded as an `absence` anchor naming the surfaces I checked (methods, measures, appendix, tables, availability statements).
- **what_triggers_block**: The paper's central quantitative claim cannot be evaluated or reproduced from what is reported — e.g. an association is asserted with no n, no test statistic, no interval, and no description of how "use" was measured; **or** the design as described cannot support the inference actually drawn (a cross-sectional self-report used to claim that usefulness *produces* use, with no acknowledgement); **or** the sample is presented as representative of undergraduates generally while the recruitment route is undisclosed or self-evidently self-selecting and no non-response comparison exists. Threshold: a fatal reporting or design gap that revision cannot patch without new data or a re-analysis.
- **what_triggers_warn**: Reporting is incomplete but the core claim remains checkable in outline — e.g. response rate absent while sample composition is given; instrument adapted from a prior source without its items or reliability reproduced; single-site convenience sample used with the limitation stated but the conclusions not actually narrowed to match; common-method bias unaddressed but the paper's claims stay associational. Threshold: substantial revision required, core result not yet falsified.

### D2: domain_accuracy
- **what_to_look_for**: Whether the adoption framework invoked (TAM/UTAUT lineage or equivalent) is represented with its established definitions rather than a loosened paraphrase; whether cited prior work is characterised accurately in direction and strength; whether the paper's citation pattern is one-directional — supportive findings cited specifically, contrary or null findings absent, aggregated away, or dismissed in a single clause; whether known field-level results are stated as settled when the literature is mixed (notably the documented weak link between self-reported and log-recorded LMS use); whether a validated instrument's name is attached to items that were not validated; whether domain terms (adoption, engagement, use, usefulness) are used with stable meaning across the manuscript. Field-norm gating applies: if I judge severity on "the field expects X", I must name the actual accepted-practice boundary from a checkable external source and say why *this* paper crosses it, or down-rate to MINOR with `[FIELD-NORM UNVERIFIED]`.
- **what_triggers_block**: A domain claim the paper's argument rests on is demonstrably wrong or a cited source is materially misrepresented (a null or opposite finding reported as supporting), **or** the paper asserts a settled domain consensus that does not exist and the central conclusion depends on that assertion being true. Threshold: the foundation of the argument is factually unsound, not merely under-referenced.
- **what_triggers_warn**: Directional citation asymmetry that a competent domain reader would notice — supporting studies described in detail while known contrary evidence is unmentioned or waved past; theory imported without its documented limitations; a construct used with a meaning that drifts between sections; terminology conflating perception with behaviour. Threshold: credibility seriously dented, correctable by even-handed re-engagement with the literature.

### D3: argumentative_coherence
- **what_to_look_for**: The explicit chain from data to conclusion, with hidden premises named; whether the paper's causal or directional language exceeds what a single-timepoint self-report design licenses (verbs like drives, leads to, increases, improves); whether the three standing rival explanations — common-method variance, reverse causation, a third variable such as course requirement or instructor mandate — are named and argued against rather than left unmentioned; whether abstract, results, discussion, and limitations make mutually compatible claims about the same finding; whether a stated limitation is then behaved as if it were resolved; whether any recommendation is entailed by the reported evidence or merely adjacent to it; whether a simpler explanation of the same data is available and unaddressed. Surface-form parity applies at verdict time: I will judge the substance of each concern, run the opposite-style counterfactual, and neither reject a correct concern for informal wording nor credit a technical-sounding claim I have not checked against the paper.
- **what_triggers_block**: The main conclusion does not follow from the presented evidence — a correlational or purely associational result carried into a causal, prescriptive, or mechanistic conclusion without the confounds being addressed; **or** the paper contradicts itself on the finding that carries the contribution (results and discussion state incompatible things about the same relationship); **or** an alternative explanation is both more parsimonious and a better fit to the reported data than the one the paper proposes. Threshold: foundation collapse, logic-chain break, data-conclusion mismatch, or stronger counter-narrative, per the DA CRITICAL criteria.
- **what_triggers_warn**: The chain holds but has unsupported links — causal language appearing in the abstract or implications while the results section stays properly associational; rival explanations acknowledged in one line and never engaged; conclusions stated with more confidence than the evidence carries; an inference that requires an unstated premise the paper never defends. Threshold: the argument is repairable by rewriting claims to match the evidence.

### D4: cross_disciplinary_relevance
- **what_to_look_for**: Whether "perceived usefulness" and "use" are defined operationally in the paper's own words rather than left to the reader's home discipline; whether a borrowed theory or instrument arrives with its evidentiary obligations or only with its prestige; whether implications addressed to instructional designers, administrators, or platform vendors are supported by evidence from the population actually sampled; whether the paper explains why an adjacent-field reader (learning sciences, information systems, institutional research) should find the result usable, or merely asserts general importance; whether interdisciplinary claims — that the finding bears on learning outcomes, engagement, or institutional strategy — are substantiated or asserted. I will note that a `block` here fires F3 on its own and score accordingly, without inflating a genuine but ordinary accessibility gap.
- **what_triggers_block**: A cross-disciplinary claim central to the paper's stated contribution is unsubstantiated — e.g. self-reported LMS use presented as evidence about learning, engagement, or educational outcomes with nothing measuring those; **or** policy/practice recommendations aimed at a different population or decision level than the one sampled, presented as warranted by these data; **or** core constructs left so undefined that an adjacent-field reader cannot determine what was measured, making the result uninterpretable outside the authors' own framing.
- **what_triggers_warn**: Definitions present but thin or discipline-internal; implications gestured toward adjacent fields without the bridging argument; a borrowed construct used without noting that neighbouring disciplines operationalise it differently; the paper's relevance claim resting on the topic's general importance rather than on this study's specific result. Threshold: accessible after revision, not currently portable.

### D5: writing_and_structure
- **what_to_look_for**: Whether numbers in text, tables, and abstract agree; whether every reported result carries the statistics needed to check it (n, estimate, dispersion or interval, exact test statistic); whether the structure makes the analysis path traceable or lets an unperformed step pass as done; whether tables and figures are self-contained and legible without the prose; whether the 1,597-word length has compressed away something a reviewer must see (methods detail, full results, limitations) versus merely trimming discussion; whether section boundaries hold — results asserting interpretation, discussion introducing new results. Presentation defects with no argumentative consequence I will log as MINOR or OBSERVATION rather than score, and citation formatting is out of my seat entirely.
- **what_triggers_block**: Presentation actively defeats verification of the central claim — the headline result appears in the abstract or discussion with no corresponding reportable result anywhere in the manuscript, **or** text and table state materially different values for the same quantity with no way to tell which is real, **or** a described analysis has no reported output at all. Threshold: a reader cannot establish what was actually found.
- **what_triggers_warn**: Results underspecified but partially checkable (effect sizes without intervals, percentages without denominators, unlabelled scale ranges); organisation that forces reconstruction of the analysis path; a table duplicating text without adding information while a needed breakdown is missing; brevity that has removed reviewable methods or limitations content. Threshold: substantial revision to reporting, core finding still discernible.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Devil's Advocate Review

### Genuine Strengths (brief, before the attack)

Three things here are real and I will not pretend otherwise. First, the reported statistics are internally consistent and arithmetically correct: r = .42 appears identically in the abstract, §4, §5 and §7, and the 95% CI [.30, .52] is what a Fisher-z interval on r = .42 at n = 214 actually returns (z = .448, SE = .0689, back-transformed [.303, .525]) — I checked rather than assumed. Second, the manuscript cites evidence that cuts against itself: Vasquez (2020) on self-report/log divergence, Delgado (2020) on the reverse pathway, Song (2018) on cross-site variability. That is the inverse of cherry-picking, and Challenge Dimension 2 returns nothing here. Third, the manuscript contains no instruction directed at reviewers — no injection attempt, nothing in the integrity class.

I therefore do not raise, and the panel should not credit as findings: "correlation is not causation," "self-report is not behaviour," "no effect size / no CI," "single site not acknowledged," "no ethics statement." All five are pre-empted by the text.

### Strongest Counter-Argument

If I held the opposite view I would not attack the coefficient. I would take the manuscript's own concessions literally and show that they consume the finding. Sections 2 and 6 state that a self-report captures *perceived* rather than actual engagement. Grant that. Then both variables in this study are perceptions, supplied by one respondent, on one instrument, at one sitting: a rating of how useful the LMS is, and a rating of how often the respondent thinks they open it. r = .42 is then not evidence that usefulness tracks use; it is evidence that a student's favourable view of the platform and their impression of their own behaviour hang together — the internal consistency of a single attitude, not a relation between two things. The manuscript never distinguishes those two readings, and it collected nothing that could: no behavioural criterion, no second method, no marker variable, no discriminant evidence.

Section 5 compounds it, offering onboarding-that-demonstrates-usefulness as an institutional lever in the same paragraph that concedes the reverse pathway is "equally consistent with the data." The hedge "suggested by, not proven by" protects the claim's certainty, not its direction.

The defence — that the paper is modest, bounded, incremental — is where the hostile reader closes: the hedging is load-bearing. It substitutes for design features (a log-derived criterion, a multi-item outcome, a second site) that would have removed the need to hedge, and it is asserted rather than earned, because the sample the paper calls "clearly bounded" is never described beyond four year levels and an undisclosed denominator. Exemplary calibration about a thin design is not a strong study.

**Why I stop short of CRITICAL.** My own Phase 1 block trigger for D3 required a rival explanation that is *both* more parsimonious *and* a better fit to the reported data. The single-attitude account is more parsimonious. I cannot show it fits better, because the manuscript reports nothing that would discriminate the two accounts — no CMV diagnostic, no second method, no discriminant evidence. An unexcluded rival is not a demonstrated-superior rival. It lands MAJOR, and I am declining the escalation on the record rather than letting adversarial register carry it upward (#574 B1).

### Issue List

#### CRITICAL

| # | Dimension | Issue Description | Evidence Anchor | Confidence | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|-----------------|------------|---------------------|-----------------------------|

*None. The core result statement ("perceived usefulness was positively and moderately associated with self-reported frequency of use") is exactly what was measured, so there is no data–conclusion mismatch, no logic-chain break at the headline, and no self-contradiction on the finding that carries the contribution.*

#### MAJOR

| # | Dimension | Issue Description | Evidence Anchor | Confidence | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|-----------------|------------|---------------------|-----------------------------|
| M1 | 4 (Logic Chain) | §5 concedes in one clause that "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data," then in the next offers onboarding that "helps students see concrete usefulness" as an institutional lever. That recommendation only follows if the forward direction holds. The hedge "suggested by, not proven by" addresses degree of proof, not direction — it does not repair a claim the same paragraph has declared directionally symmetric. | `text` — §5, both clauses, single paragraph | 5 — two directly quotable adjacent sentences; no domain judgment required | n/a — internal inconsistency, no external norm invoked | n/a |
| M2 | 1 / 4 (Alternative Explanation) | Common-method variance is nowhere addressed. Predictor and outcome come from the same respondent, the same instrument, the same sitting. The manuscript's own §2 premise (self-report indexes perception, per Vasquez 2020) makes a shared-perception contributor to r = .42 a live rival that the design cannot exclude and the text never names. | `absence` — checked abstract, §3.2, §3.4, §4, §5, §6; no marker variable, procedural separation, or Harman-type check reported anywhere | 4 — same-source rival is readable directly off the manuscript's own design description | n/a — severity rests on the paper's own §2 premise, not on an external practice standard | n/a |
| M3 | 4 (Logic Chain) | §4 files course requirements and assessment schedules as explanations for the *unexplained* variance ("reported engagement reflects many influences beyond perceived usefulness, including course requirements and assessment schedules"). A mandated-use course plausibly drives both the outcome *and* the rating of usefulness, i.e. it is a candidate confound for the observed association, not a residual. Naming the third variable in a position where it cannot threaten the coefficient neutralises the one rival explanation the manuscript does surface. | `text` — §4, final sentence | 4 — quotable sentence plus elementary confounding logic | n/a — internal reasoning defect | n/a |
| M4 | 4 (Internal Contradiction) | §3.1 reports that "5 duplicate entries were removed." §3.3 states that "no identifying information was collected, and responses could not be linked back to individual students." Duplicate detection requires some linking key. Either the anonymity statement overstates what was done, or an undisclosed procedure (IP, fingerprint, response-pattern matching) was used and the ethics description is incomplete. Both readings are reportable; the manuscript supports neither. | `text` — §3.1 and §3.3, in tension | 5 — two quotable sentences in direct logical conflict | n/a — internal contradiction | n/a |
| M5 | 2 / 3 (Borrowed Authority) | The abstract claims "an adapted, previously validated instrument" and §2 "a previously validated measure." §3.2 confirms the six items were *adapted* from Costa and Wren (2019) and reports α = .88. Internal consistency is not validity, and the cited source's validation (its title is "Instrument development and validation") attaches to the item set the authors modified, not to theirs. The manuscript claims validation credit for an instrument whose adapted form has none reported, with no adaptation record, no item wording, and no re-validation. | `text` — abstract, §2, §3.2; `absence` — item wording, adaptation log, re-validation: checked §3.2, §3.4, references, no appendix present | 4 — the manuscript itself says "adapted"; α ≠ validity is definitional, not a norm claim | n/a — the boundary is supplied by the manuscript's own cited source title, not by my prior | n/a |
| M6 | 4 / 5 (Construct Drift) | The measured outcome is "how often the respondent accessed the LMS" on one five-point item (§3.2). The abstract's closing sentence concludes that "perceived usefulness tracks with LMS engagement among undergraduates"; §4 refers to "reported engagement"; §2 to "engagement with it." One measure is carried under two labels, and the broader label is the one that reaches the manuscript's most-read sentence. Whatever "engagement" is taken to mean, the paper never states that it means self-reported access frequency. | `text` — abstract (final sentence), §2, §3.2, §4 | 4 — label mismatch is quotable; severity argued from internal inconsistency, not from a claim about field usage | n/a — deliberately framed as internal label inconsistency so that no unverifiable field norm carries the severity | n/a |
| M7 | 5 / 8 (Overgeneralization / Self-Defeat) | The manuscript's defence against generalization criticism is that its finding is bounded to "one clearly bounded sample" (§1, §6, §7). The bound is never disclosed: no response rate, no eligible-population denominator (despite "all enrolled undergraduates were eligible"), no participant characteristics beyond "spanned all four year levels," no completer/non-completer comparison for the 14 removed incompletes. A reader cannot state who the finding is bounded *to*, so the hedge is asserted rather than earned and non-response bias is unquantifiable in either direction. | `absence` — checked §3.1, §3.3, §4; no demographics table, no denominator, no rate reported anywhere in the manuscript | 4 — the omission is verifiable by exhaustive reading; the inferential consequence follows from the paper's own framing | n/a — severity rests on the manuscript's own bounding claim, not on a disclosure norm I would have to import | n/a |
| M8 | 8 (So What? / Portability) | The stated contribution is comparability: "an incremental data point, comparable with prior work" (§2), "consistent with prior technology-acceptance research" (abstract, §5), "one point in a distribution rather than a fixed value" (§2, invoking Song 2018). No competing coefficient is quoted anywhere, and the descriptors another reader would need to place this estimate — item wording, full response options, sample composition, setting characteristics — are absent. The claim to value is therefore unsupported by the manuscript's own text. This is narrower than literature-coverage adequacy, which is R2's call: I am attacking only the comparability claim the paper makes about itself. | `absence` — checked §2, §4, §5, §7 and the reference list for any quoted prior estimate; `text` — §2 final paragraph | 4 — the claim is quotable and the supporting comparison verifiably absent | n/a — no external norm invoked; the standard is the manuscript's own assertion | n/a |

#### MINOR

| # | Dimension | Issue Description | Evidence Anchor | Confidence |
|---|-----------|-------------------|-----------------|------------|
| m1 | 2 (Evidence Selection) | Whitfield (2019) is introduced only in §5 and supports the manuscript's single prescriptive move. It is the one source never set up or characterised in §2, so the paper's only actionable claim rests on its only unvetted citation. | `text` — §5; `absence` — §2 contains no mention of Whitfield | 4 — verifiable by comparing §2 and §5 |
| m2 | 5 (Reporting) | §3.2 discloses only the two extreme anchors (1 = rarely or never, 5 = several times daily). §4 then reports a median category of "a few times per week," which is not one of the disclosed anchors. The middle response options are never published, so the median cannot be mapped to a scale point and the category spacing cannot be judged. | `text` — §3.2 and §4 | 5 — direct comparison of two passages |
| m3 | 5 (Reporting) | Shared variance is described qualitatively only — "the proportion of variance shared by the two measures was accordingly modest" — with no numeric r². The reader can compute .18, but the manuscript declines to state the quantity it is characterising. | `text` — §4 | 5 — arithmetic and quotation |
| m4 | 1 (Selection) | Recruitment ran through "the institution's course-announcement channel" (§3.1); whether that channel is delivered inside the LMS is never stated. If it is, sampling is conditioned on the outcome variable. §6 names the symptom ("students who engage more with institutional channels may be overrepresented") without the mechanism or its direction. Held at MINOR deliberately: the plausible direction is range restriction at the low-use end, which attenuates r and is therefore conservative for the paper's claim. | `text` — §3.1 and §6 | 4 — channel description is quotable; direction reasoning is standard |
| m5 | 5 (Presentation) | The manuscript contains no table and no figure. A scatterplot is reported as inspected (§3.4) but not shown, and the outcome variable's distribution is summarised by a median category alone with no dispersion. | `absence` — full-manuscript scan for tables/figures returned none | 5 — exhaustive read |
| m6 | 4 (Hidden Premise, secondary) | §1 states that "institutions invest heavily in these platforms on the assumption that availability translates into use" and adopts that framing without comment. See Unexamined Premise below; logged here so the premise is also traceable as an issue. | `text` — §1 | 4 — quotable framing sentence |

### Ignored Alternative Explanations/Paths

1. **Single-attitude / common-method account.** One favourable disposition toward the platform generates both ratings. More parsimonious than two constructs covarying, and fully compatible with everything reported. Not excluded, not mentioned. This is the counter-argument above and the reason D3 sits at warn rather than pass.
2. **Instructor- and assessment-level confounding.** Courses that require frequent LMS activity produce both high reported access and post-hoc usefulness ratings. §4 mentions these variables but as residual noise (M3), never as a confound; nothing at course or instructor level was measured.
3. **Selection conditioned on the outcome.** If the recruitment channel sits inside the LMS, the low-use tail was never sampled. §6 gestures at overrepresentation without identifying the mechanism or its direction (m4).
4. **Material-conditions third variable.** Device access, connectivity, commuting and paid-work hours could depress reported access independently of any perception. No demographic or access variable was collected, so perceived usefulness may be partly standing in for circumstances. Named here as an unmeasured alternative; what affected groups would say about it is R3's territory, not mine.
5. **The path not taken, and not explained.** §6 concedes that self-reports "are known to diverge from behavioural traces" — the divergence its own Vasquez (2020) citation documents. Every institution running an LMS holds the logs for exactly this construct. The manuscript never says whether logs were unavailable, ethically out of scope, or simply not sought, so a reader cannot tell whether the central measurement limitation was a constraint or a choice. I am **not** demanding a log study: that would be redesigning the manuscript. I am noting that one sentence of justification is missing and that its absence lets a limitation read as unavoidable when it may not have been.
6. **Reverse pathway** — acknowledged (§5, citing Delgado 2020) and therefore *not* listed as ignored. It is acknowledged and then behaved against in the same paragraph, which is M1, a different defect.

### Missing Stakeholder Perspectives

*(Named only — elaborating what these parties would say is R3/Perspective Reviewer's role.)*

- Instructors and course designers, who set the requirements that plausibly drive both measured variables.
- Non-respondents, and the 19 excluded submissions — the population whose size the manuscript never establishes.
- Students at the low-access end, systematically the least likely to be reached by a channel-based recruitment route.
- Institutional data stewards / ethics reviewers, who hold both the logs and the answer to the duplicate-detection question in M4.

### Unexamined Premise

**That more frequent LMS access is the thing worth explaining.** The manuscript's opening frame — institutions invest "on the assumption that availability translates into use" (§1) — inherits use-as-good from the institution and never interrogates it, and §5's practice implication spends that premise: onboarding is "worth institutional attention" only if raising access frequency is a gain. But a well-designed course requiring three deliberate visits and a badly designed one forcing daily hunting for materials score in opposite directions on this item, with the second scoring higher. Nothing in the manuscript states what access frequency is a proxy for. Every one of the eight challenge dimensions passes over this, because the premise is never asserted and so never checked: it is the frame, not a claim inside it. Repair is framing and bounding, not new data — one paragraph stating what the outcome stands for, and a Discussion bounded accordingly.

### Observations (Non-Defects)

- The α = .05, n = 214 power statement in §3.4 claims >.80 power to detect r ≥ .19; the exact detectable r at 80% power for n = 214 is ≈ .193, so r = .19 sits fractionally below the stated threshold. Rounding-level, no consequence for any claim, and power analysis is R1's seat — logged as an observation, not scored.
- The Spearman check (ρ = .40) is a genuine robustness addition, but it tests parametric form and monotonicity only. It does not speak to measurement coarseness, outcome unreliability, or common-method contribution, and the manuscript does not claim otherwise.
- The manuscript's numeric self-consistency across abstract, §4, §5 and §7 is unusual and worth crediting explicitly, so the synthesizer can distinguish "handled" from "unchecked."
- No instruction, plea, or reviewer-directed imperative appears anywhere in the manuscript. Nothing to report in the integrity class.

---

contract_role: da

## Dimension Scores

### D1: methodology_rigor
score: warn
Basis: Phase 1 warn triggers fired — response rate and eligible-population denominator absent while the manuscript's own defence rests on the sample being "clearly bounded" (M7); instrument adapted from a prior source with neither items nor re-validation reproduced (M5); common-method safeguards absent while claims remain associational (M2); an internal contradiction in the data-handling/anonymity description (M4). No Phase 1 block trigger fired: n, r, CI, exact p, ρ and the use-measure description are all present, the design's limits are acknowledged rather than overrun, and the sample is not presented as representative.

### D2: domain_accuracy
score: warn
Basis: Phase 1 warn triggers fired on borrowed-credibility and construct stability — a validated instrument's standing claimed for an adapted item set (M5), one measure carried under two labels with the broader one reaching the abstract's conclusion (M6), and the sole prescriptive claim resting on the sole citation never set up in the literature review (m1). No block: no cited source is misrepresented, no false consensus is asserted, and directional citation asymmetry is *absent* — the manuscript foregrounds Delgado, Vasquez and Song, all of which cut against it.

### D3: argumentative_coherence
score: warn
Basis: Phase 1 warn triggers fired — a practice implication whose direction contradicts the symmetry conceded in the same paragraph (M1), a rival explanation named in a position where it cannot threaten the coefficient (M3), and a same-source rival never named at all (M2). Block declined on the record: the headline claim matches what was measured, the manuscript does not contradict itself about the finding that carries the contribution, and the single-attitude counter-narrative is more parsimonious but cannot be shown to fit the reported data better, since nothing reported discriminates the accounts.

### D4: cross_disciplinary_relevance
score: warn
Basis: Phase 1 warn triggers fired — the contribution claim rests on comparability that is asserted and never cashed out in any comparable quantity or descriptor (M8), and the constructs are not portable as reported (six items never shown, middle response options never published, "accessed" never operationalised). Block declined: the manuscript makes no claim about learning or educational outcomes, its one practice implication is explicitly marked as suggested rather than warranted, and an adjacent-field reader can determine in outline what was measured.

### D5: writing_and_structure
score: warn
Basis: Phase 1 warn trigger "unlabelled scale ranges / brevity that removed reviewable content" fired — the outcome item's middle response options are undisclosed yet §4 reports a median in their terms (m2), r² is characterised without being stated (m3), participant characteristics are absent (M7), and no table or figure exists at all (m5). Block declined: the central result is fully reportable and checkable from §4.

## Failure Condition Checks

*Predicates evaluated against this seat's `## Dimension Scores` only. Each condition's `cross_reviewer_quantifier` is panel-level machinery for the synthesizer to apply; it is not mine to apply and I have not.*

### F1
fired: false
Predicate "any mandatory dimension scores 'block'": mandatory dimensions are D1, D2, D3 — all warn. No block assigned on any dimension, mandatory or otherwise.

### F2
fired: true
Predicate "two or more mandatory dimensions score 'warn' or worse": three of three mandatory dimensions (D1, D2, D3) score warn. Threshold exceeded.

### F3
fired: false
Predicate "any high-priority dimension scores 'block'": the sole high-priority dimension, D4, scores warn, not block.

### F0
fired: false
Predicate "every mandatory dimension scores 'pass'": none of D1, D2, D3 scores pass.

## Review Body

This manuscript is calibrated well enough that the ordinary adversarial inventory returns almost nothing. Causality is disclaimed in six places, self-report is framed as perception with a supporting citation that cuts against the paper, the single-site limit is stated three times, the effect is called moderate and given a correctly computed interval, and the reference set foregrounds cautions rather than confirmations. Cherry-picking detection returns one thin item, not a pattern. The panel's exposure here is manufacturing overreach, and I have declined it: no CRITICAL finding, no block on any dimension, and one counter-narrative explicitly held down a band because I could not meet my own Phase 1 escalation bar.

What survives is narrower and harder. The manuscript's defences are load-bearing, and three of them are asserted rather than earned. It calls its instrument "previously validated" while §3.2 concedes the items were adapted and reports only internal consistency — the validation belongs to the item set the authors changed. It calls its sample "clearly bounded" while never disclosing a response rate, a denominator, or any participant characteristic beyond four year levels, so the bound the hedge invokes does not exist in the text. It calls its contribution "comparable with prior work" and "one point in a distribution" while quoting no competing estimate and supplying none of the descriptors a reader would need to place this one. Each hedge answers a criticism the manuscript anticipated; none is backed by what the manuscript reports. That is the shape of the D1, D2 and D4 warns.

The coherence findings are tighter. In §5 the manuscript states that the reverse pathway is "equally consistent with the data" and then, in the next sentence, offers onboarding that helps students see usefulness as a lever worth institutional attention. The trailing hedge — "suggested by, not proven by" — concedes that the implication is unproven, which is not the defect. The defect is that the implication is directionally unsupported by a symmetry the same paragraph asserts, and no amount of certainty-hedging repairs a direction. In §4 the manuscript surfaces course requirements and assessment schedules, then files them as sources of residual variance; a mandated-use course is a candidate confound for the association itself, so the one third variable the paper names has been placed where it cannot do any damage. And common-method variance appears nowhere across the abstract, §3.2, §3.4, §4, §5 and §6, although the paper's own §2 premise — that a self-report indexes perception — is precisely what makes a shared-perception contributor to r = .42 live. Taken together with the strongest counter-argument, the manuscript has conceded enough about its measures to leave open the reading that r = .42 indexes the coherence of a single attitude rather than a relation between usefulness and use, and it never distinguishes that reading from its own.

Two findings are contradictions rather than gaps, and they are cheap to fix and cheap to verify. §3.1 removes five duplicate entries; §3.3 states that no identifying information was collected and that responses could not be linked to individuals. One of those statements is incomplete. Separately, the measured outcome is how often a respondent accessed the LMS, but the abstract's concluding sentence reports a result about "LMS engagement" and §4 about "reported engagement." I have argued that one from internal inconsistency rather than from any claim about how the field uses the word, precisely so that no unverifiable norm carries the severity — the manuscript has used two labels for one measure, and the broader label is the one most readers will take away.

On reporting, my seat stays narrow. The outcome item's middle response options are never published, yet §4 reports a median stated in their terms; shared variance is characterised as "modest" without the number; the scatterplot is inspected but not shown; there is no table or figure in the manuscript. I score these only because what "use" means is the paper's outcome variable and the reader cannot see either the question or the options. None of it threatens the central result.

Where I have stayed out: power analysis and psychometric consequence are R1's, literature coverage is R2's, the worth of the outcome variable to a decision-maker and what absent groups would say are R3's, and journal fit, format and disclosure policy are the EIC's. Where my findings overlap theirs, I have reported them anyway rather than suppress corroboration, and left deduplication to synthesis. Three of my findings are reframings a reader might otherwise route elsewhere: M5 attacks the *validation claim*, not the psychometrics; M8 attacks the manuscript's *own comparability assertion*, not its reference count; the Unexamined Premise attacks a *hidden premise in the argument*, not the practical merit of measuring clicks.

Decision logic: three mandatory dimensions at warn, none at block, and the high-priority dimension at warn. F1 does not fire, F3 does not fire, F0 does not fire, F2 fires. F2 is the highest-severity fired condition at 70, and its action governs. Every finding above is repairable by revision to claims, disclosure and framing; none requires new data collection, which is why the outcome is revision rather than rejection.

## Editorial Decision

editorial_decision=major_revision

# PART 3 — EDITORIAL SYNTHESIS

## Sprint-Contract Mechanical Synthesis

**Contract**: `reviewer/reviewer_full/v1` · `baseline_version: v3.6.2` · `generated_at: 2026-07-25T08:00:00Z` · `panel_size N = 5`
**Panel (seat order)**: S1 = EIC · S2 = Methodology · S3 = Domain · S4 = Perspective · S5 = Devil's Advocate
**Panel cardinality invariant**: 5 usable Phase 2 outputs / `panel_size` 5 — satisfied, no `[PANEL-SHRUNK]`.

### Step 1 — Scoring matrix

Dimensions resolved by `id`. Values are `$defs.score` (`block | warn | pass`), transcribed verbatim from each seat's `## Dimension Scores`.

| Dimension (`id` — name, priority) | EIC | Methodology | Domain | Perspective | DA |
|---|---|---|---|---|---|
| D1 — methodology_rigor (mandatory) | warn | warn | warn | warn | warn |
| D2 — domain_accuracy (mandatory) | warn | warn | warn | warn | warn |
| D3 — argumentative_coherence (mandatory) | warn | warn | **pass** | warn | warn |
| D4 — cross_disciplinary_relevance (high) | warn | warn | warn | warn | warn |
| D5 — writing_and_structure (normal) | warn | warn | warn | warn | warn |

Per-seat mandatory-dimension profile (D1, D2, D3): EIC `warn/warn/warn` · Methodology `warn/warn/warn` · Domain `warn/warn/pass` · Perspective `warn/warn/warn` · DA `warn/warn/warn`.
No `block` appears anywhere in the matrix. One `pass` appears (Domain, D3).

### Step 2 — Failure-condition evaluation

Contract action strings take the form `editorial_decision=<value>`; the `<value>` alone is given in the Action column so the pinned emission line below remains the only one of its kind in this document.

| `condition_id` | severity | quantifier | expression (§9 pattern) | per-seat predicate (EIC / Meth / Dom / Persp / DA) | holds for | threshold | fired | Action `<value>` |
|---|---|---|---|---|---|---|---|---|
| F1 | 90 | `any` | "any mandatory dimension scores 'block'" — pattern 1 (bare `mandatory`) | F / F / F / F / F | 0 of 5 | ≥ 1 | **false** | `reject_or_major_revision` |
| F2 | 70 | `majority` | "two or more mandatory dimensions score 'warn' or worse" — pattern 2 | T / T / T / T / T | 5 of 5 | ≥ ⌊5/2⌋+1 = 3 | **true** | `major_revision` |
| F3 | 60 | `any` | "any high-priority dimension scores 'block'" — pattern 1 (`high-priority` variant) | F / F / F / F / F | 0 of 5 | ≥ 1 | **false** | `major_revision` |
| F0 | 10 | `all` | "every mandatory dimension scores 'pass'" — pattern 3 | F / F / F / F / F | 0 of 5 | 5 of 5 | **false** | `accept` |

Per-condition working:

- **F1** — predicate is per-seat "∃ d ∈ {D1, D2, D3} : score(d) = `block`". Every seat's three mandatory scores are `warn` or `pass`; no `block` exists in the matrix. `any` requires ≥ 1 of 5; 0 of 5 hold. Not fired.
- **F2** — predicate is per-seat "|{d ∈ {D1, D2, D3} : score(d) ⪰ `warn`}| ≥ 2" under the ordering `pass` < `warn` < `block`. EIC 3, Methodology 3, Domain 2 (D1, D2 — D3 is `pass` and does not count), Perspective 3, DA 3. All five reach the count-2 threshold. `majority` for N = 5 requires ≥ 3; 5 of 5 hold. **Fired.**
- **F3** — predicate is per-seat "∃ d with priority `high` : score(d) = `block`". D4 is the sole high-priority dimension and every seat scored it `warn`. `any` requires ≥ 1 of 5; 0 of 5 hold. Not fired.
- **F0** — predicate is per-seat "∀ d ∈ {D1, D2, D3} : score(d) = `pass`". No seat has even one mandatory `pass` except Domain (D3 only), which still fails the universal. `all` requires 5 of 5; 0 of 5 hold. Not fired.

All four expressions parsed against `sprint_contract_protocol.md §9`; no `[EXPRESSION-UNRECOGNISED]`.

### Step 3 — Precedence and decision

Fired set = {F2}. Single member, so precedence-by-`severity` (70) and the ordinal tiebreak are both trivially satisfied. F2's action is emitted verbatim.

fired_conditions: [F2]

editorial_decision=major_revision

---

# Editorial Decision Package

## Manuscript Information

- **Title**: *[not supplied to the synthesizer — the five Phase 2 cards do not quote it]*
- **Manuscript ID**: not available
- **Journal**: *Education and Information Technologies* (per the EIC seat's identity statement)
- **Decision Date**: 2026-07-25
- **Review Round**: 1
- **Panel**: 5 reviewers (Editor-in-Chief, Methodology, Domain, Perspective, Devil's Advocate), `reviewer_full` mode

## Review Panel Provenance (#540)

`[PROVENANCE-STAMP-ABSENT: the dispatching layer supplied no #540 provenance stamp with this invocation.]` The block is required in `reviewer_full` and must not be inferred, so no one of the three statements is asserted here: this synthesizer cannot state whether the Reviewer 2 slot ran cross-model, whether all five personas ran on one family, or whether a cross-model dispatch failed and fell back. Readers should treat model independence across the five seats as **unestablished**, not as established or excluded. Cross-family splits, had any been stamped, would be visible by inspection in the Step 1 matrix; no aggregate over families is computed.

`[CROSS-MODEL-CHECKPOINT: not run — ARS_CROSS_MODEL not indicated for this invocation; no behavioural change per Step 4b.]`

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript to *Education and Information Technologies*. It has been assessed by five independent reviewers, including the Editor-in-Chief, under a pre-registered sprint contract in which each reviewer committed their scoring triggers before seeing your paper.

### Decision: Major Revision

The contract arithmetic is reproduced above: three of the five mandatory-dimension profiles (and all five seats' count predicates) satisfy F2, no seat recorded a `block` on any dimension, and the accept-grade condition F0 does not hold. F2 is the only fired condition and its action governs.

The Editor-in-Chief additionally invites you to consider resubmitting in a **brief report / research note** container rather than as a full research article. That invitation is an editorial option, not a condition of the decision — see roadmap item R11.

### A note on what this panel did *not* find

Five seats independently checked, and five seats independently recorded, that the standard criticisms of this design are pre-empted in your text rather than merely unaddressed. Causality is disclaimed in the abstract, introduction, literature review, discussion, limitations and conclusion, with the reverse pathway named as equally consistent and sourced. Self-report is framed as an indicator of perceived rather than actual use, with supporting citation, and that framing is sustained across sections. The single-site bound is stated three times. The coefficient is reported with an exact *n*, an exact *p*, a 95% confidence interval, a distribution-free robustness check, a sensitivity statement and an explicit acknowledgement that most variance is unaccounted for. Ethics approval, consent, voluntariness, anonymity and the absence of incentives are all reported. The Methodology and Devil's Advocate seats independently recomputed the interval and the power figure from your reported inputs and both reproduce. Your reference set foregrounds work that cuts against your own finding.

None of that is offered as consolation. It is a finding of record, and it is the reason this decision is Major Revision rather than anything harsher: nothing in the panel's list requires a different study.

### Consensus Analysis

Consensus is computed per sub-claim over the **four non-DA seats** (denominator always 4). `not-mentioned` is silence, not opposition, and is never promoted into agreement. The Devil's Advocate's positions are tracked separately and never enter the count.

#### Step 1a — Reviewer summary matrix

| | EIC | R1 · Methodology | R2 · Domain | R3 · Perspective | DA |
|---|---|---|---|---|---|
| Overall recommendation | Major Revision | Major Revision | Major Revision | Major Revision | Major Revision |
| Report-level confidence | 5 | 4 | 4 | 4 | n/a (per-finding only) |
| Weaknesses emitted | 6 (5 major, 1 minor) | 8 (8 major) | 11 (6 major, 5 minor) | 6 (4 major, 2 minor) | 14 (0 critical, 8 major, 6 minor) |
| Key strengths recorded | 5 | 8 | 4 | 5 | 3 |
| Key weaknesses | → Step 1b | → Step 1b | → Step 1b | → Step 1b | → Step 1b |
| Questions to authors | 7 | 7 | 5 | 5 | 0 (issue list instead) |
| Minor issues | 6 | 6 | 5 | 5 | 6 |

*(The template's four-column form predates the five-seat `reviewer_full` panel; the DA column is additive.)*

#### Step 1b — Weakness sub-claim inventory

Positions other than `not-mentioned` are listed; silent seats are named in the disposition table that follows. Severity and confidence are **transported** from each card's per-finding tags, never re-derived.

| SC | parent weakness | reviewer | position | evidence pointer | severity | conf |
|---|---|---|---|---|---|---|
| SC-1 | comparability claim undelivered | EIC W1 | raised | `text: §2, "It is intended as an incremental data point, comparable with prior work"` | major | 5 |
| SC-1 | " | R2 W1 | corroborated | `absence: comparator estimates absent from §2 ¶3, §4, §5 ¶1, §7, reference list` | major | 5 |
| SC-1 | " | R3 W3 | corroborated | `text: §3.1 "one mid-sized public university"` + `absence: §3.1–§3.4` | major | 5 |
| SC-1 | " | DA M8 | corroborated | `absence: §2, §4, §5, §7 + reference list — no quoted prior estimate` | major | 4 |
| SC-2 | setting/platform/context undescribed | EIC W3 | raised | `text: §3.1, "conducted at one mid-sized public university"` | major | 5 |
| SC-2 | " | R1 W8(ii) | corroborated | `text: §3.2 anchors; §4 median` (LMS role in assessment unstated) | major | 5 |
| SC-2 | " | R2 W6 | corroborated | `absence: no requirement/platform/discipline descriptors in §3.1, §3.2, §5` | major | 5 |
| SC-2 | " | R3 W3 | corroborated | `text: §3.1` + `absence: platform, delivery mode, national context` | major | 5 |
| SC-2 | " | DA M8 | corroborated | `absence: sample composition, setting characteristics` | major | 4 |
| SC-3 | no participant-characteristics table | EIC W2 | raised | `absence: checked §3.1, §3.2, §3.3, §3.4, end matter, References` | major | 5 |
| SC-3 | " | R1 M2 | corroborated | `text: §3.1 "spanned all four year levels"` | minor | 4 |
| SC-3 | " | R3 W3 | corroborated | `absence: no participant-characteristics table` | major | 5 |
| SC-3 | " | DA M7 | corroborated | `absence: §3.1, §3.3, §4 — no demographics table` | major | 4 |
| SC-4 | response rate / denominator absent; sample never labelled non-probability | EIC W2 | raised | `absence: §3.1 sampling/denominator` | major | 5 |
| SC-4 | " | R1 W1 | corroborated | `absence: Abstract, §3.1, §4, §6 — no denominator or rate` | major | 5 |
| SC-4 | " | R3 W3 | corroborated | `absence: no response rate, no denominator` | major | 5 |
| SC-4 | " | R2 W8 | **disputed** (severity) | `text: §6 voluntariness vs §3.1 233→214` · `[FIELD-NORM UNVERIFIED]` | minor | 3 |
| SC-4 | " | DA M7 | corroborated | `absence: no rate reported anywhere` | major | 4 |
| SC-5a | data-availability statement absent | EIC W2 | raised | `absence: post-§7 end matter` | major | 5 |
| SC-5a | " | R1 M4 | corroborated | `absence: §3.4, §4, back matter` | minor | 5 |
| SC-5b | funding / COI / ethics-approval reference absent | EIC W2 | raised | `absence: post-§7 end matter; §3.3 approval reference` | major | 5 |
| SC-6 | response options incomplete; median unlocatable | EIC W2 | raised | `absence: §3.2 instrument wording/anchors` | major | 5 |
| SC-6 | " | R1 W8(i) | corroborated | `text: §3.2 anchors; §4 "a median category of 'a few times per week'"` | major | 5 |
| SC-6 | " | R2 W9 | corroborated | `text: §4 median vs §3.2 "(1 = rarely or never to 5 = several times daily)"` | minor | 5 |
| SC-6 | " | R3 W6 | corroborated | `text: §3.2 anchors; cf. §4 median` | minor | 4 |
| SC-6 | " | DA m2 | corroborated | `text: §3.2 and §4` | minor | 5 |
| SC-7 | instrument adaptation undocumented; items never shown | EIC W2 | raised | `absence: §3.2 instrument wording` | major | 5 |
| SC-7 | " | R1 W5 | corroborated | `text: §3.2 "adapted from Costa and Wren (2019)…"` | major | 5 |
| SC-7 | " | R2 W4 | corroborated | `text: §3.2 "a six-item scale adapted from Costa and Wren (2019)"` | major | 4 |
| SC-7 | " | R3 W6 | corroborated | `text: §3.2 anchors; adaptation undocumented` | minor | 4 |
| SC-7 | " | DA M5 | corroborated | `absence: item wording, adaptation log, re-validation` | major | 4 |
| SC-8 | "previously validated" claimed for the adapted set | R1 W5 | raised | `text: §3.2 vs Abstract/§2 "previously validated instrument"` | major | 5 |
| SC-8 | " | R2 W4 | raised | `text: §3.2 vs §2 ¶3 "using a previously validated measure"` | major | 4 |
| SC-8 | " | DA M5 | corroborated | `text: abstract, §2, §3.2` | major | 4 |
| SC-9 | "engagement" used for a single access-frequency item | EIC W4 | raised | `text: Abstract, "perceived usefulness tracks with LMS engagement"` | major | 5 |
| SC-9 | " | R1 M6 | corroborated | `text: Abstract, final sentence` | minor | 4 |
| SC-9 | " | R2 W5 | corroborated | `text: Abstract vs §3.2 "a single five-point frequency item"` | major | 5 |
| SC-9 | " | R3 W1 | corroborated | `text: Abstract vs §3.2 "how often the respondent accessed the LMS"` | major | 5 |
| SC-9 | " | DA M6 | corroborated | `text: abstract (final sentence), §2, §3.2, §4` | major | 4 |
| SC-10 | duplicate removal vs anonymity claim | EIC W5 | raised | `text: §3.1 "5 duplicate entries were removed" vs §3.3` | major | 4 |
| SC-10 | " | R1 W6 | corroborated | `text: §3.1; §3.3 "could not be linked back to individual students"` | major | 5 |
| SC-10 | " | DA M4 | corroborated | `text: §3.1 and §3.3, in tension` | major | 5 |
| SC-11 | common-method variance unaddressed | R1 W4 | raised | `absence: §3.2, §3.4, §5, §6, Abstract` | major | 5 |
| SC-11 | " | DA M2 | corroborated | `absence: abstract, §3.2, §3.4, §4, §5, §6` | major | 4 |
| SC-12 | single-item outcome, no reliability/validity; net bias sign | R1 W3 | raised | `text: §3.2 "a single five-point frequency item"` | major | 5 |
| SC-12 | " | EIC D1 | corroborated | `text: §3.2 — reliability for predictor only` · `[SEVERITY-SOURCE: letter-fallback]` `[CONFIDENCE-SOURCE: report-level]` | — | 5 |
| SC-13 | recruitment channel may be internal to the outcome | R1 W2 | raised | `text: §3.1 "the institution's course-announcement channel"; §6` | major | 4 |
| SC-13 | " | EIC Q2 | corroborated | `text: EIC Question 2` · `[SEVERITY-SOURCE: letter-fallback]` `[CONFIDENCE-SOURCE: report-level]` | — | 5 |
| SC-13 | " | DA m4 | corroborated (lower severity, direction conservative) | `text: §3.1 and §6` | minor | 4 |
| SC-14 | nesting/clustering unexamined; CI likely too narrow | R1 W7 | raised | `absence: §3.1, §3.4, §6 — no nesting or design-effect consideration` | major | 4 |
| SC-15a | construct borrowed from a declined framework, no warrant | R2 W2 | raised | `text: §1 ¶2 "nor do we test a full acceptance model" vs §5 ¶1` | major | 4 |
| SC-15a | " | EIC Originality | corroborated | `text: EIC §Originality; Question 7` · `[SEVERITY-SOURCE: letter-fallback]` `[CONFIDENCE-SOURCE: report-level]` | — | 5 |
| SC-15b | construct provenance secondhand/anachronistic | R2 W3 | raised | `text: §2 ¶1 "long proposed … (Costa & Wren, 2019; Delgado, 2020)"` | major | 5 |
| SC-15b | " | EIC Originality | corroborated | `text: EIC §Originality — TAM lineage never named` · `[SEVERITY-SOURCE: letter-fallback]` `[CONFIDENCE-SOURCE: report-level]` | — | 5 |
| SC-16a | §5 implication directionally unsupported by a symmetry the same paragraph concedes | R3 W4 | raised | `text: §5 onboarding vs §5 reverse-pathway concession` | major | 5 |
| SC-16a | " | R1 D3 | corroborated | `text: §5 — "hedged, so Minor, but it is a coherence seam"` | minor | 4 |
| SC-16a | " | EIC §Significance / D4 | **disputed** (existence) | `text: §5 "suggested by, not proven by, the present correlation"` | — | 5 |
| SC-16a | " | R2 D3 / §Argument logic | **disputed** (existence) | `text: §5 ¶2 — implication marked as suggested; D3 scored pass` | — | 4 |
| SC-16a | " | DA M1 | corroborated | `text: §5, both clauses, single paragraph` | major | 5 |
| SC-16b | recommendation targets students; paper's own results nominate course/assessment design; instructors absent | R3 W4 | raised | `text: §5 onboarding vs §4 "course requirements and assessment schedules"` | major | 5 |
| SC-16b | " | DA §Missing Stakeholders | corroborated | `text: §4; instructors named as absent party` | — | — |
| SC-17 | course requirements filed as residual variance, not as candidate confound | DA M3 | raised | `text: §4, final sentence` | major | 4 |
| SC-18 | material/access conditions absent as third variable; equity gap in §6 | R3 W2 | raised | `absence: no access/device/connectivity/employment variable in §3.1, §3.2, §4, §6` | major | 4 |
| SC-18 | " | DA §Ignored Alternatives #4 | corroborated | `absence: no demographic or access variable collected` | — | — |
| SC-19 | no rationale for not using institutional log data | R3 W5 | raised | `absence: §3.1, §3.3, §3.4, §6` | minor | 5 |
| SC-19 | " | DA §Ignored Alternatives #5 | corroborated | `text: §6 self-report concession` | — | — |
| SC-20 | no tables or figures; scatterplot undisplayed | EIC W6 | raised | `absence: no table or figure in §§1–7; scatterplot referenced at §3.4` | minor | 5 |
| SC-20 | " | R1 M4 | corroborated | `absence: §3.4, §4, back matter` | minor | 5 |
| SC-20 | " | R3 D5 | corroborated | `absence: no tables or figures at all` · `[SEVERITY-SOURCE: letter-fallback]` `[CONFIDENCE-SOURCE: report-level]` | — | 4 |
| SC-20 | " | DA m5 | corroborated | `absence: full-manuscript scan returned none` | minor | 5 |
| SC-21 | Whitfield (2019) enters only in §5 | EIC W6 | raised | `text: Whitfield appears only in §5` | minor | 5 |
| SC-21 | " | R2 W10 | corroborated | `text: §5 ¶2 "practitioner accounts of digital-environment onboarding"` | minor | 4 |
| SC-21 | " | R3 Minor #3 | corroborated | `text: §5` · `source_kind: editorial` | editorial | — |
| SC-21 | " | DA m1 | corroborated | `text: §5; absence: §2` | minor | 4 |
| SC-22 | r² described but never stated | R1 M5 | raised | `text: §3.4, §4` | minor | 5 |
| SC-22 | " | R2 W11 | raised | `text: §4 "the proportion of variance shared … was accordingly modest"` | minor | 5 |
| SC-22 | " | DA m3 | corroborated | `text: §4` | minor | 5 |
| SC-23 | literature base thin and stops at 2021 | R2 W7 | raised | `absence: reference list — six entries, latest 2021` · `[FIELD-NORM UNVERIFIED]` | minor | 5 |
| SC-23 | " | EIC Originality / D2 | corroborated | `text: EIC §Originality — no source postdates 2021` · `[SEVERITY-SOURCE: letter-fallback]` `[CONFIDENCE-SOURCE: report-level]` | — | 5 |
| SC-24 | the outcome variable's worth never argued; what frequency proxies for never stated | R3 W1 | raised | `text: Abstract vs §3.2; §1 institutional framing` | major | 5 |
| SC-24 | " | DA §Unexamined Premise / m6 | corroborated | `text: §1 "availability translates into use"` | minor | 4 |
| SC-25 | article type undeclared; container mismatch | EIC W6 / §Journal Fit | raised | `text: ~1,540 words of body text; no article type declared` | minor | 5 |

**Decomposition discipline note.** Every sub-claim above traces to a claim a seat actually made. Three bundles were split to avoid the partial-evidence trap: EIC W2 → SC-3 / SC-4 / SC-5a / SC-5b / SC-6 / SC-7 (R1 corroborates only the data-availability half of the end-matter bundle, so SC-5a and SC-5b carry different counts); R1 W8 → SC-2 / SC-6; R3 W3 → SC-1 / SC-2 / SC-3 / SC-4, and R3 W4 → SC-16a / SC-16b (the EIC and Domain seats dispute only the first half).

#### Step 1c — Surface-form parity check

Two weighting decisions turned on phrasing and were re-tested against substance rather than polish. **SC-4**: the Domain seat's entry is hedged and self-limiting ("sampling technicalities are Reviewer 1's competence, not mine", `[FIELD-NORM UNVERIFIED]`), while three other seats state the same gap flatly at Major. The opposite-style counterfactual was run: if the Domain seat's substance were rewritten in the assertive register the others used, its severity assignment would still rest on the same stated ground (it could not verify a venue norm), and if the EIC's entry were rewritten in the Domain seat's hedged register it would still carry the venue-policy grounding. The weight therefore keys off grounding, not register. **SC-18** and **SC-24** are phrased in practitioner rather than technical vocabulary ("circumstance wearing the costume of perception", "a laptop"); no weight was deducted for that, and both are carried at their transported Major severity because their substance is checkable against §6's four-item limitations list. Conversely, no sub-claim gained weight for technical specificity alone — SC-14 (clustering) is precisely stated and still carries only one seat's support, which is exactly how it is recorded and priced. Authorship was not a weighting input.

#### Points of Agreement

**[CONSENSUS-4]** (all 4 non-DA seats agree, 0 disputed):

1. **SC-2 — The setting is not described.** Platform, country/sector, delivery mode, disciplinary mix, collection window, and whether LMS use was required for submission or grade access are all absent. Corroborated by the DA. The Domain seat sharpens the point: your own §4 and §5 nominate course requirements and assessment structure as principal drivers of the outcome, then decline to state where your institution sits on that variable.
2. **SC-6 — The outcome item's response scale is not fully reported.** Only the two endpoint anchors appear, so §4's median category "a few times per week" cannot be placed on the scale. Four seats plus the DA.
3. **SC-7 — The adapted instrument is undocumented.** Six items never shown, no record of what was changed against Costa and Wren (2019), no re-validation beyond α. Four seats plus the DA.
4. **SC-9 — "Engagement" stands in for a single self-reported access-frequency item**, including in the abstract's closing sentence. Four seats plus the DA; the Methodology seat rates it Minor and the other three Major, but all four ask for the same edit.

**[CONSENSUS-3]** (3 agree, 4th silent — silence is not opposition):

5. **SC-1 — Your stated contribution is not delivered.** EIC, Domain and Perspective; the **Methodology seat is silent** (it states explicitly that the venue's contribution bar is not its dimension to score). Corroborated by the DA. No competing coefficient appears anywhere, so no reader can determine whether *r* = .42 is confirmatory, discrepant, or superseded.
6. **SC-3 — No participant-characteristics table.** EIC, Methodology, Perspective; the **Domain seat is silent**. Corroborated by the DA.
7. **SC-20 — No tables or figures anywhere**, including the scatterplot §3.4's assumption claims rest on. EIC, Methodology, Perspective; the **Domain seat is silent**. Corroborated by the DA.
8. **SC-21 — Whitfield (2019) enters only in §5.** EIC, Domain, Perspective; the **Methodology seat is silent**. Corroborated by the DA.

**Corroborated findings** (2 of 4, no conflict — action-bearing, below the consensus label): SC-5a (data-availability statement), SC-8 ("previously validated" claimed for the adapted set — plus DA), SC-10 (ethics/anonymity contradiction — plus DA), SC-12 (single-item outcome psychometrics), SC-13 (recruitment channel — plus DA), SC-15a (construct without its framework), SC-15b (construct provenance), SC-22 (r² unstated — plus DA), SC-23 (literature base thin and dated).

**Single-reviewer findings** (1 of 4, weighted by confidence and seat competence): SC-5b (EIC, 5), SC-11 (Methodology, 5 — plus DA), SC-14 (Methodology, 4), SC-16b (Perspective, 5 — plus DA), SC-18 (Perspective, 4 — plus DA), SC-19 (Perspective, 5 — plus DA), SC-24 (Perspective, 5 — plus DA), SC-25 (EIC, 5).

**[DA-ONLY]**: SC-17 (course requirements filed as residual variance rather than as a candidate confound; DA M3, major, 4). Zero of four non-DA seats spoke to it — that is **silence, not rejection**, and it is carried into the roadmap at P2 on the DA's own internally-grounded reasoning. It is adjacent to, but not the same claim as, SC-2 and SC-16b.

#### Points of Disagreement

**Disagreement 1 — SC-4: is the missing response rate and denominator a Major or a Minor deficiency?**

- **EIC view**: Major, confidence 5. The denominator and response rate are this journal's published submission requirements; without them "voluntary-response bias cannot be sized by any reader."
- **Methodology view**: Major, confidence 5. "The problem is not the low rate a census invitation would likely produce — it is that the reader cannot bound who the 214 represent, which is the precondition for reading any single-site estimate."
- **Perspective view**: Major, confidence 5. Named as one of the descriptors that defeats the manuscript's own transferability claim.
- **Domain view**: Minor, confidence 3, tagged `[FIELD-NORM UNVERIFIED]`. The Domain seat agrees the gap is real and flags the internal tension in §6, but declines to charge it at Major because "the demand that a response rate be reported is a field reporting expectation I have not grounded in a venue policy or reporting guideline here," and explicitly defers the sampling analysis to the Methodology seat.
- **Disagreement type**: Severity disagreement.
- **Editor's Resolution**: **Sustained at Major.** Roadmap item R3, Priority 1.
- **Resolution Rationale**: Expertise-first and evidence-first converge. The Domain seat's stated reason for the lower rating is that it could not verify the venue norm — and the seat that owns venue norms did verify it, at confidence 5, citing this journal's published submission requirements. The Methodology seat, which owns sampling, independently rates it Major at confidence 5 on a ground the Domain seat never contests (the sample cannot be bounded). The Domain seat is deferring, not opposing; its own text routes the substantive consequence to SC-1 at Major. No surface-form deduction was applied: the hedged phrasing was not counted against it, and the resolution rests on which seat holds the grounding, not on which wrote more assertively.

**Disagreement 2 — SC-16a: is §5's onboarding implication a defect?**

- **Perspective view** (raised, major, 5): the recommendation "only follows if the forward direction holds," and as the reader who would fund such a programme, "this correlation cannot fund that decision."
- **DA view** (M1, major, 5): the hedge "suggested by, not proven by" addresses degree of proof, not direction — "no amount of certainty-hedging repairs a direction."
- **Methodology view** (corroborated at minor, 4): the implication "presupposes the PU→use direction that the same paragraph concedes is unresolved; hedged, so Minor, but it is a coherence seam."
- **EIC view** (disputed, 5): it "survives my block test: it is offered as a possibility, explicitly labelled 'suggested by, not proven by, the present correlation,' and attached to a source. That is a hedged conjecture, not an unsubstantiated interdisciplinary claim, and it should not be attacked as overreach."
- **Domain view** (disputed, 4): D3 scored `pass` on the merits; "the practice implication is explicitly marked as suggested rather than shown. I found no causal slide to report, and I note explicitly that I looked for one."
- **Disagreement type**: Existence disagreement (2 agree / 2 disputed among the non-DA seats).
- **Editor's Resolution**: **Sustained in part, not escalated, and the residual dissent is recorded as unresolved.** The narrow logical point — a hedge on certainty does not license a direction — is unrebutted: neither disputing seat addresses it; both establish only that the hedge is present, which no one denies. That point stands. Whether it rises to a publication-relevant defect is a venue judgment the EIC owns, and the EIC's answer is no. The panel therefore did **not** resolve the severity question, and this letter does not pretend it did: the Perspective seat and the DA continue to hold it at Major, the Methodology seat at Minor, the EIC and Domain seats at non-defect. What the panel *did* converge on is the remedy — the EIC ("it would be strengthened by being stated as a hypothesis worth testing") and the Perspective seat ("recast §5's implication as a hypothesis worth testing") ask for the same edit from opposite verdicts. That edit is required at Priority 2 (S8), and the author must respond to the dissent on the record whichever view they find persuasive.

**Disagreement 3 — SC-13: what direction does the recruitment channel bias the coefficient?**

- **Methodology view** (W2, major, 4): "Direction is not determinate: low-end truncation typically attenuates *r*, while selection on the joint high end of both variables would inflate it."
- **DA view** (m4, minor, 4): held at Minor deliberately — "the plausible direction is range restriction at the low-use end, which attenuates *r* and is therefore conservative for the paper's claim."
- **Disagreement type**: Severity/direction disagreement. The DA is not one of the four counted seats, so this is not a SPLIT; it is recorded here because it changes what the author should write.
- **Editor's Resolution**: Adopt the Methodology seat's indeterminate framing (S5). The DA's reading is a proper subset of it — attenuation is the more likely of the two mechanisms, not the only one — and the manuscript should name the channel, the mechanism, and the indeterminacy rather than assert a conservative direction it has not established.

#### Devil's Advocate adjudication

The Devil's Advocate returned **zero CRITICAL findings** and declined an available escalation on the record: its strongest counter-argument (that both variables are perceptions, so *r* = .42 may index the internal coherence of a single attitude rather than a relation between two constructs) was held at Major because, by its own pre-committed trigger, an unexcluded rival is not a demonstrated-superior rival — nothing your manuscript reports discriminates the two accounts. This editorial office records that as correct discipline and does not treat the counter-argument as a veto. It is not dismissed either: it is the substantive reason SC-11 and SC-12 sit at Priority 1 (roadmap R10). If you report the item order, name common-method variance, and state the net bias direction as indeterminate, the single-attitude reading is bounded rather than left open.

The DA's eight MAJOR findings map as follows: M1 → SC-16a (SPLIT, above), M2 → SC-11, M3 → SC-17 (DA-only, P2), M4 → SC-10, M5 → SC-7/SC-8, M6 → SC-9, M7 → SC-3/SC-4, M8 → SC-1. All five seats independently recorded that the manuscript contains no instruction-injection attempt and nothing in the integrity class.

### Decision Rationale

Every seat scored `warn` on at least two mandatory dimensions and none scored `block` on any; F2 is the only fired condition and it prescribes major revision. The qualitative record supports the same place on the scale from both directions.

Against a harsher outcome: five seats independently checked and pre-empted the criticisms that would ordinarily justify one. There is no causal overreach, no self-report-as-behaviour slide, no selective reporting, no numerical inconsistency, no misrepresented source, no ethics omission at the procedural level. Two seats recomputed your interval and power figure and both reproduce. The Domain seat scored argumentative coherence `pass` on the merits after checking every section. Nothing on the panel's list requires new data, a second site, log linkage, a longitudinal design, moderators, or a theoretical model — and this office explicitly declines to ask for any of them. Your decision not to test an acceptance model is coherent with your research question and should survive revision.

Against a lighter outcome: the manuscript's own account of why it should exist is that it supplies a comparable estimate in a distribution of published estimates, and that promise is not kept anywhere. No competing coefficient is quoted, and the setting descriptors that would make a comparison meaningful are absent, so the promise could not be cashed even if the comparators were named — a CONSENSUS-3 and a CONSENSUS-4 finding standing on each other. Layered onto that are four measurement disclosures the panel is unanimous or near-unanimous on, a printed ethics statement whose two halves contradict each other, and a construct label in the abstract's most-read sentence that names something broader than what was measured. Three of the panel's Priority 1 items go to whether a reader can tell what you measured; two go to whether a reader can tell whom you measured. That accumulation is beyond clarification.

Calibration is a property of your reporting, not a substitute for the contribution it describes — and equally, your own modesty is not a confession and has not been read as one. The gap is between what the manuscript claims to offer and what it currently supplies, and every item below closes it from data already in hand.

### Top Blocking Issues (3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | The stated contribution — a comparable point in a distribution of published estimates — is asserted and never delivered: no competing coefficient appears anywhere, and the setting descriptors needed to place the estimate are absent | EIC, R2·Domain, R3·Perspective, DA | `text: §2, "It is intended as an incremental data point, comparable with prior work"` + `absence: comparator estimates absent from §2 ¶3, §4, §5 ¶1, §7, reference list` | R1, R2 |
| 2 | The printed ethics statement is internally inconsistent — five duplicate entries were removed from a survey stated to have collected no identifying information and to be unlinkable to individuals | EIC, R1·Methodology, DA | `text: §3.1 "5 duplicate entries were removed" vs §3.3 "responses could not be linked back to individual students"` | R5 |
| 3 | The measurement surface is not reportable: the six adapted items are never shown and the adaptation is undocumented, and the outcome item's middle response options are unpublished so §4's median cannot be located on the scale | EIC, R1·Methodology, R2·Domain, R3·Perspective, DA | `text: §3.2, "a six-item scale adapted from Costa and Wren (2019)"`; `text: §3.2 anchors vs §4 "a median category of 'a few times per week'"` | R6, R7 |

---

## Part 2: Revision Roadmap

**Legend.** Roadmap item IDs are `R1…R11` (Required) and `S1…S14` (Suggested). Reviewer seats are written `EIC`, `R1·Method`, `R2·Domain`, `R3·Persp`, `DA` to avoid collision with roadmap IDs. Severity and confidence are transported from the cards; fallback tags travel with them.

### Required Revisions (Must Fix)

| # | Revision item | Sub-claim(s) | Severity | Evidence anchor | Confidence | Source | Section | Effort |
|---|---|---|---|---|---|---|---|---|
| R1 | Quote 3–6 published perceived-usefulness/use coefficients with their sample sizes, instruments and settings, and state where *r* = .42 falls relative to them — above, below, or inside the range | SC-1 | major | `text: §2, "It is intended as an incremental data point, comparable with prior work"` | 5 — EIC W1; 5 — R2·Domain W1; 5 — R3·Persp W3; 4 — DA M8 | EIC, R2·Domain, R3·Persp, DA | §2, §5, §7 | 2 d |
| R2 | Describe the setting: platform, country/sector, delivery mode, disciplinary composition, collection window, and above all whether LMS use was required for submission, grade access, or materials | SC-2 | major | `text: §3.1, "conducted at one mid-sized public university"` | 5 — EIC W3; 5 — R1·Method W8; 5 — R2·Domain W6; 5 — R3·Persp W3 | EIC, R1·Method, R2·Domain, R3·Persp, DA | §3.1 | 1 d |
| R3 | Report the eligible-undergraduate *N* and the response rate; label the realised sample self-selected / non-probability; compare respondents against institutional enrolment distributions on whatever the registry holds | SC-4 | major (arbitrated — see Disagreement 1; R2·Domain dissents at minor with `[FIELD-NORM UNVERIFIED]`) | `absence: checked Abstract, §3.1, §4, §6 — no denominator or rate on any surface` | 5 — EIC W2; 5 — R1·Method W1; 5 — R3·Persp W3; dissent 3 — R2·Domain W8 | EIC, R1·Method, R3·Persp (DA corroborates) | §3.1, §6 | 1 d |
| R4 | Add a participant-characteristics table (year level, faculty, and whatever else was collected) | SC-3 | major (EIC W2, R3·Persp W3); minor (R1·Method M2) | `absence: no participant-characteristics table anywhere in §3.1–§3.4` | 5 — EIC; 4 — R1·Method; 5 — R3·Persp; 4 — DA M7 | EIC, R1·Method, R3·Persp, DA | §3.1 | 0.5 d |
| R5 | Reconcile §3.1 and §3.3: state the duplicate-detection rule, disclose any metadata captured and confirm the ethics approval covered it, revise the anonymity sentence to be precise, and report *r* with the 5 cases retained (*n* = 219) | SC-10 | major | `text: §3.1 "5 duplicate entries were removed" vs §3.3 "responses could not be linked back to individual students"` | 4 — EIC W5; 5 — R1·Method W6; 5 — DA M4 | EIC, R1·Method, DA | §3.1, §3.3 | 1 d |
| R6 | Print the six adapted perceived-usefulness items verbatim in an appendix with a change log against Costa and Wren (2019); report item-level descriptives and at minimum item–total correlations (a single-factor CFA is feasible at *n* = 214) | SC-7 | major (EIC W2, R1·Method W5, R2·Domain W4, DA M5); minor (R3·Persp W6) | `text: §3.2, "a six-item scale adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"` | 5 — EIC; 5 — R1·Method; 4 — R2·Domain; 4 — R3·Persp; 4 — DA | EIC, R1·Method, R2·Domain, R3·Persp, DA | §3.2, Appendix | 1.5 d |
| R7 | Report all five response options for the use item verbatim, state which numeric point corresponds to "a few times per week", and give the item's full frequency distribution | SC-6 | major (EIC W2, R1·Method W8); minor (R2·Domain W9, R3·Persp W6, DA m2) | `text: §3.2 "(1 = rarely or never to 5 = several times daily)" vs §4 "a median category of 'a few times per week'"` | 5 — EIC; 5 — R1·Method; 5 — R2·Domain; 4 — R3·Persp; 5 — DA | EIC, R1·Method, R2·Domain, R3·Persp, DA | §3.2, §4 | 0.5 d |
| R8 | Rephrase "previously validated instrument" to "adapted from a previously validated instrument" wherever the adapted six-item set is described | SC-8 | major | `text: Abstract and §2 ¶3 "a previously validated measure" vs §3.2 "adapted from"` | 5 — R1·Method W5; 4 — R2·Domain W4; 4 — DA M5 | R1·Method, R2·Domain, DA | Abstract, §2, §3.2 | 0.5 d |
| R9 | Replace "engagement" with "self-reported frequency of LMS access" wherever the paper restates its own finding — including the abstract's closing sentence — and reserve "engagement" for characterising prior work that measured it | SC-9 | major (EIC W4, R2·Domain W5, R3·Persp W1, DA M6); minor (R1·Method M6) | `text: Abstract, "perceived usefulness tracks with LMS engagement among undergraduates"` | 5 — EIC; 4 — R1·Method; 5 — R2·Domain; 5 — R3·Persp; 4 — DA | EIC, R1·Method, R2·Domain, R3·Persp, DA | Abstract, §2, §4, §5 | 0.5 d |
| R10 | Name common-method variance in §6 as a same-source threat distinct from the self-report/log divergence already listed; state it alongside the attenuation from the single-item outcome's unreliability and five-category coarsening; conclude that the **net measurement bias on *r* = .42 is of indeterminate sign** and qualify "moderate" in those terms; report the item order | SC-11, SC-12 | major (R1·Method W3, W4; DA M2); EIC D1 rationale `[SEVERITY-SOURCE: letter-fallback]` | `absence: checked §3.2, §3.4, §5, §6, Abstract — no mention of same-source or method bias` | 5 — R1·Method; 4 — DA; 5 — EIC `[CONFIDENCE-SOURCE: report-level]` | R1·Method, DA, EIC | §4, §6 | 1 d |
| R11 | Declare the intended article type and respond to the editorial invitation to resubmit as a brief report / research note. If you prefer the full-article container, state what justifies it | SC-25 | minor (EIC W6; the container recommendation itself is stated in the EIC's Journal Fit section rather than as a numbered weakness — `[SEVERITY-SOURCE: letter-fallback]` for that element) | `text: ~1,540 words of body text; no article type declared anywhere` | 5 — EIC `[CONFIDENCE-SOURCE: report-level]` | EIC | Front matter | 0.5 d |

*Priority note on R5 and R10*: both are corroborated (2/4) or single-reviewer (1/4) findings rather than consensus items, and are placed at Priority 1 on stated grounds rather than by count — R5 because the seat that owns venue policy states the ethics statement "cannot go to press as written," R10 because it changes how the headline coefficient must be characterised and is owned by the methodology seat at confidence 5 with independent DA corroboration. R11 is a Minor-severity item at Priority 1 because it is an editorial gate on the container, not a severity-derived priority.

### Required Item Details

**R1: Deliver the comparability claim**
- **Problem**: The manuscript positions itself twice as an incremental, comparable data point and invokes Song (2018) for "one point in a distribution," but quotes no competing coefficient anywhere and offers only the qualitative "consistent with prior technology-acceptance research."
- **Source**: EIC W1 (*"the manuscript does not keep it: not one prior coefficient is quoted"*); R2·Domain W1 (*"where in the distribution?"*); R3·Persp W3; DA M8.
- **Requirement**: Name the comparison set. For each comparator give the coefficient, sample size, instrument and setting. State explicitly whether *r* = .42 is above, below, or inside that range.
- **Acceptance criteria**: A reader can locate your estimate relative to at least three named published estimates without leaving the manuscript.

**R2: Describe the setting**
- **Problem**: "One mid-sized public university" is the entirety of the setting description, while §4 and §5 both nominate course requirements and assessment schedules as principal drivers of the outcome.
- **Source**: EIC W3; R1·Method W8(ii); R2·Domain W6 (*"Having named the factor as a principal driver of its outcome, the paper owes its own value on it"*); R3·Persp W3.
- **Requirement**: Two to three sentences in §3.1 covering platform, national/sectoral context, delivery mode, disciplinary composition, collection window, and whether LMS access was required for coursework, submission, or grade retrieval.
- **Acceptance criteria**: A reader at another institution can judge whether your coefficient is commensurable with one produced at theirs.

**R5: Reconcile the ethics and anonymity statements**
- **Problem**: §3.1 removes five duplicate entries; §3.3 states no identifying information was collected and responses could not be linked to individuals. Duplicate detection requires either quasi-identifying metadata or response-pattern inference; both readings are reportable and the manuscript supports neither.
- **Source**: EIC W5 (*"A journal is accountable for the accuracy of the ethics and anonymity statements it prints"*); R1·Method W6; DA M4.
- **Requirement**: State the detection rule; disclose any metadata captured and confirm the ethics approval covered it; revise §3.3 so the anonymity claim is precise; add a one-line sensitivity check reporting *r* with the five cases retained.
- **Acceptance criteria**: §3.1 and §3.3 can both be true as written, and the exclusion rule is stated rather than implied.

**R10: State the net measurement-bias direction**
- **Problem**: Random error and five-category coarsening in the single-item outcome attenuate the coefficient; same-source measurement of both variables inflates it. Neither is named. §6's self-report limitation concerns divergence from behavioural logs, which is criterion validity of the outcome — a different threat.
- **Source**: R1·Method W3 and W4 (*"its net measurement bias is of indeterminate sign"*); DA M2; EIC D1 rationale.
- **Requirement**: Name both mechanisms in §6, state their opposing directions, and qualify "moderate" in §4 and §5 accordingly. Report whether perceived usefulness was administered before the use item and whether any procedural separation was used. Note explicitly that the Spearman check addresses parametric form and monotonicity, not unreliability, coarseness, or shared method — a point the manuscript does not currently claim, and should not begin to.
- **Acceptance criteria**: No reader can take *r* = .42 as a floor or as a settled magnitude from the revised text.

### Suggested Revisions (Should Fix)

| # | Revision item | Sub-claim(s) | Severity | Evidence anchor | Confidence | Source | Priority | Effort |
|---|---|---|---|---|---|---|---|---|
| S1 | Add a data-availability statement | SC-5a | major (EIC W2); minor (R1·Method M4) | `absence: post-§7 end matter` | 5 — EIC; 5 — R1·Method | EIC, R1·Method | P2 | 0.25 d |
| S2 | Add funding, conflict-of-interest, and ethics-approval-reference statements | SC-5b | major | `absence: end matter; §3.3 claims approval without a reference number` | 5 — EIC W2 | EIC | P2 | 0.25 d |
| S3 | State in one paragraph what licenses interpreting the six-item mean as *perceived usefulness* in the theory's sense, and treating the coefficient as commensurable with framework-internal coefficients, while declining the framework | SC-15a | major (R2·Domain W2); EIC Originality `[SEVERITY-SOURCE: letter-fallback]` | `text: §1 ¶2 "nor do we test a full acceptance model" vs §5 ¶1 "consistent with prior technology-acceptance research"` | 4 — R2·Domain; 5 — EIC `[CONFIDENCE-SOURCE: report-level]` | R2·Domain, EIC | P2 | 0.5 d |
| S4 | Cite the originating source of the perceived-usefulness construct and either support or drop the "long proposed" temporal claim. The Domain seat attests that Davis (1989, *MIS Quarterly* 13(3), 319–340) and Venkatesh, Morris, Davis & Davis (2003, *MIS Quarterly* 27(3), 425–478) exist | SC-15b | major | `text: §2 ¶1, "Research on technology acceptance has long proposed … (Costa & Wren, 2019; Delgado, 2020)"` | 5 — R2·Domain W3; 5 — EIC `[CONFIDENCE-SOURCE: report-level]` | R2·Domain, EIC | P2 | 0.5 d |
| S5 | State whether the course-announcement channel is delivered inside the LMS. If so, name the mechanism (invitation exposure conditioned on the outcome) and state that the resulting bias direction is indeterminate; if multiple routes existed, report the proportion recruited by each | SC-13 | major (R1·Method W2); minor (DA m4); EIC Q2 `[SEVERITY-SOURCE: letter-fallback]` | `text: §3.1 "the institution's course-announcement channel"; §6` | 4 — R1·Method; 4 — DA; 5 — EIC `[CONFIDENCE-SOURCE: report-level]` | R1·Method, EIC, DA | P2 | 0.5 d |
| S6 | Add course/programme nesting to §6 as a named threat to the *precision* of [.30, .52]; commit to collecting a cluster identifier in any replication so a design-effect adjustment becomes possible | SC-14 | major | `absence: checked §3.1, §3.4, §6 — no nesting or design-effect consideration, against the mechanism §4–§5 themselves invoke` | 4 — R1·Method W7 | R1·Method | P2 | 0.5 d |
| S7 | Name unmeasured material conditions (device access, connectivity, commuting, paid work) in §6 as a third-variable explanation with a stated expected direction, and bound §5's implication accordingly | SC-18 | major | `absence: no access, device, connectivity, employment or commuting variable in §3.1, §3.2, §4, §6` | 4 — R3·Persp W2; DA §Ignored Alternatives #4 | R3·Persp, DA | P2 | 0.5 d |
| S8 | Recast §5's onboarding implication as a hypothesis worth testing rather than a direction worth attention, and add a sentence naming course and assessment design — and thus instructors — as the alternative lever the study did not measure | SC-16a (unresolved dissent), SC-16b | major (R3·Persp W4, DA M1); minor (R1·Method D3); disputed as a defect by EIC and R2·Domain | `text: §5, "the reverse pathway … is equally consistent with the data"` adjacent to `text: §5, "LMS onboarding which helps students see concrete usefulness … may be worth institutional attention"` | 5 — R3·Persp; 5 — DA; 4 — R1·Method | R3·Persp, DA, R1·Method (EIC and R2·Domain dissent) | P2 | 0.5 d |
| S9 | Re-file course requirements and assessment schedules as a candidate confound for the association itself, not only as a source of residual variance | SC-17 `[DA-ONLY — 0/4 non-DA corroboration; silence, not rejection]` | major | `text: §4, final sentence — "reported engagement reflects many influences beyond perceived usefulness, including course requirements and assessment schedules"` | 4 — DA M3 | DA | P2 | 0.25 d |
| S10 | State in one or two sentences what self-reported access frequency is intended to proxy for, and what it demonstrably does not proxy for. "Nothing beyond itself — we report frequency as frequency" is an acceptable answer if "engagement" is then retired as its synonym | SC-24 | major (R3·Persp W1); minor (DA m6) | `text: §1, "Institutions invest heavily in these platforms on the assumption that availability translates into use"` | 5 — R3·Persp; 4 — DA | R3·Persp, DA | P2 | 0.5 d |
| S11 | Give a one-sentence rationale for the self-report design where institutional log data existed — governance constraint, ethics-approval boundary, unavailability of institutional-research support, or deliberate interest in perception rather than behaviour | SC-19 | minor | `absence: no rationale in §3.1, §3.3, §3.4, or §6` | 5 — R3·Persp W5; DA §Ignored Alternatives #5 | R3·Persp, DA | P2 | 0.25 d |
| S12 | Add a descriptives/correlation table and display the scatterplot §3.4's linearity and monotonicity claims rest on | SC-20 | minor (EIC W6, R1·Method M4, DA m5); R3·Persp D5 `[SEVERITY-SOURCE: letter-fallback]` | `absence: no table or figure appears anywhere in §§1–7; scatterplot referenced at §3.4 but not presented` | 5 — EIC; 5 — R1·Method; 4 — R3·Persp `[CONFIDENCE-SOURCE: report-level]`; 5 — DA | EIC, R1·Method, R3·Persp, DA | P2 | 0.5 d |
| S13 | Broaden and update the literature base: the post-TAM lineage and its intention-versus-actual-use critique, a meta-analytic or pooled benchmark, and a second source on the self-report/log strand your measurement choice sits on | SC-23 | minor — `[FIELD-NORM UNVERIFIED]` (R2·Domain W7); EIC Originality `[SEVERITY-SOURCE: letter-fallback]` | `absence: reference list — six entries, latest 2021, no UTAUT-lineage or meta-analytic source` | 5 — R2·Domain; 5 — EIC `[CONFIDENCE-SOURCE: report-level]` | R2·Domain, EIC | P2 | 1 d |
| S14 | Add a polyserial correlation (modelling the ordinal outcome as a coarsened continuum) and a disattenuation band across plausible ρ*yy* values (e.g. .60–.85), declared as an explicit assumption rather than a result | SC-12 | major | `text: §3.2, "a single five-point frequency item"` | 5 — R1·Method W3 | R1·Method | P2 | 1 d |

Two seats flagged `[UNVERIFIED]` search leads rather than citations, and this office forwards them as leads only, to be verified before citing: e-learning/LMS technology-acceptance meta-analyses (R2·Domain, recalled as Šumak and colleagues in *Computers in Human Behavior*, metadata unverified); learning-analytics work comparing self-reported LMS use with log-derived traces (R2·Domain, R3·Persp); mandatory-versus-voluntary use context as a moderator (R2·Domain); the multidimensional behavioural/emotional/cognitive engagement construct (R3·Persp); the information-systems distinction among frequency, duration, depth and feature-breadth of system use (R3·Persp); digital-equity and digital-divide research on device ownership, connectivity, commuter and working students (R3·Persp); governance and ethics of secondary use of LMS trace data (R3·Persp).

### Revision Checklist

#### Priority 1 — Structural Revisions (estimated total effort: 10 days)
- [ ] R1: Quote 3–6 comparable published coefficients and locate *r* = .42 among them
- [ ] R2: Write the setting paragraph — platform, country/sector, delivery mode, discipline mix, collection window, required-vs-voluntary use
- [ ] R3: Report the eligible-population denominator and response rate; label the sample non-probability
- [ ] R4: Build the participant-characteristics table
- [ ] R5: Reconcile §3.1 duplicate removal with §3.3 anonymity; add the *n* = 219 sensitivity line
- [ ] R6: Append the six items verbatim with a change log against Costa and Wren (2019); add item-level statistics
- [ ] R7: Print all five response options and the outcome item's frequency distribution
- [ ] R8: Fix "previously validated" → "adapted from a previously validated instrument"
- [ ] R9: Replace "engagement" with "self-reported frequency of LMS access" wherever the paper restates its own finding
- [ ] R10: Name common-method variance and outcome unreliability as opposing biases; state net bias as indeterminate; report item order
- [ ] R11: Declare the article type / answer the research-note invitation

#### Priority 2 — Content Supplementation (estimated total effort: 7 days)
- [ ] S1: Data-availability statement
- [ ] S2: Funding, COI, ethics-approval reference
- [ ] S3: Paragraph licensing the construct without its framework
- [ ] S4: Foundational construct citation; fix or drop "long proposed"
- [ ] S5: Specify the recruitment channel and its mechanism
- [ ] S6: Add course/programme nesting to §6 as a precision threat
- [ ] S7: Add material/access conditions to §6 as a third variable with a stated direction
- [ ] S8: Recast §5 as a testable hypothesis; name course/assessment design as the alternative lever
- [ ] S9: Re-file course requirements as a candidate confound, not residual variance
- [ ] S10: State what access frequency proxies for — and what it does not
- [ ] S11: One-sentence rationale for self-report over available logs
- [ ] S12: Descriptives/correlation table and the scatterplot
- [ ] S13: Broaden and update the literature base
- [ ] S14: Polyserial coefficient and a stated-assumption disattenuation band

#### Priority 3 — Text and Formatting (estimated total effort: 2 days)
*(Aggregated EDITORIAL channel — Minor Issues from all five cards; `source_kind: "editorial"`, no transported finding metadata.)*
- [ ] Introduce Whitfield (2019) in §2 or drop the practice implication's reliance on it (SC-21 — CONSENSUS-3; silent seat: R1·Method)
- [ ] Report *r*² (≈ .18) rather than describing shared variance qualitatively (SC-22)
- [ ] Add the 95% CI to the abstract (EIC)
- [ ] State α explicitly in §3.4 rather than leaving it recoverable only from the power sentence (EIC, R1·Method)
- [ ] Relabel §3.4's power statement as a sensitivity analysis and name the method used (Fisher *z* vs exact/noncentral *t*) (R1·Method M1)
- [ ] State whether the retained 214 were complete on both focal variables and how the 14 excluded cases compared (R1·Method M3)
- [ ] Reporting precision: add *df* to the correlation (*r*(212) = .42), give *p* and a CI for the Spearman coefficient, italicise statistical symbols, report descriptives to two decimals (R1·Method M5)
- [ ] State whether any subgroup or covariate analysis (e.g. by year level) was run, and with what result (R1·Method M2)
- [ ] Tighten or define "adoption" in §2 (R2·Domain)
- [ ] Consider the journal's structured-abstract format (EIC)
- [ ] Note the analysis software and version (R1·Method M4)

### Total Estimated Effort

**Major Revision: 4–6 weeks**, of which no part requires new data collection. Every Priority 1 and Priority 2 item is closed by disclosure, re-description, or an analysis the existing 214 cases already support — with one exception, S6, where the nesting issue can only be acknowledged now and designed for in a replication.

### Revision Deadline

- **Recommended deadline**: 2026-09-19 (8 weeks)
- **Basis**: Major Revision — 6–8 weeks
- **Extension policy**: notify the editorial office one week before the deadline
- **Re-review**: the revised manuscript will undergo another round of review

### Response Letter Instructions

Please respond item by item using `templates/revision_response_template.md` (Reviewer Comment → Author Response → Changes Made). Your response must include:

1. A response and revision description for every Required Revision (R1–R11)
2. A response for every Suggested Revision (S1–S14) — adopted, or the reason for not adopting
3. An explicit response to **Disagreement 2 (SC-16a)**, which the panel did not resolve. Two seats hold §5's implication to be a defect at Major, one at Minor, and two hold it not to be a defect at all. You must address the unrebutted logical point — that a hedge on degree of proof does not license a direction — whichever verdict you find persuasive
4. Answers to the seats' direct questions, which are the fastest route through several roadmap items: the eligible-undergraduate *N* and response rate; whether course announcements are LMS-delivered; how the five duplicates were identified; what exactly was adapted from Costa and Wren (2019); the full five response options and which corresponds to "a few times per week"; whether perceived usefulness was administered before the use item; whether any access or circumstance variables were collected; and whether you wish this considered as a research note or a full article
5. Change markup throughout, and a cross-reference table of new page and paragraph numbers

### Closing

We encourage you to consider the reviewers' comments carefully and to submit a substantially revised manuscript. The revised version will undergo another round of review.

We want to be plain about what this decision does and does not say. The panel found your inferential conduct better than typical for this submission stream and said so in five separate cards, unprompted and independently. What it did not find was the evidence for the manuscript's own claim about why it matters. Close that gap — show the distribution you say you are adding a point to, describe the setting well enough for someone to place it, and print the measurement surface so the estimate can be reused — and this becomes a small, sound, transparently bounded contribution that a subsequent author or a meta-analyst can actually use. That is the paper you set out to write, and everything needed to finish it is already in your hands.

---

## Part 3: Reviewer Report Summary (Appendix)

### EIC Summary
- **Recommendation**: Major Revision | **Confidence**: 5 | **Dimensions**: D1 warn, D2 warn, D3 warn, D4 warn, D5 warn | **Fired**: F2
- **Key point**: Execution and calibration are sound; the contribution claim is asserted rather than delivered, the setting is described too thinly to support it, and the journal's disclosure package and the printed ethics statement are not publication-ready. Recommends the brief-report / research-note container, expressly not a redesigned study.

### Reviewer 1 (Methodology) Summary
- **Recommendation**: Major Revision | **Confidence**: 4 | **Dimensions**: D1 warn, D2 warn, D3 warn, D4 warn, D5 warn | **Fired**: F2
- **Key point**: Inferential discipline is real and the reported statistics reproduce; the exposure is one level down at the measurement layer, where attenuation from a single unvalidated ordinal outcome and inflation from same-source method variance leave the net bias on *r* = .42 of indeterminate sign. Every Major item closes on the existing 214 cases.

### Reviewer 2 (Domain) Summary
- **Recommendation**: Major Revision | **Confidence**: 4 | **Dimensions**: D1 warn, D2 warn, **D3 pass**, D4 warn, D5 warn | **Fired**: F2
- **Key point**: The construct is used with its field meaning intact and no causal slide exists — D3 passes on the merits after an explicit section-by-section check. The paper has not shown the field where it fits: no comparator coefficient, construct provenance attributed to 2019–2020 secondary sources, and a construct borrowed from a framework the paper declines without a stated warrant.

### Reviewer 3 (Perspective) Summary
- **Recommendation**: Major Revision | **Confidence**: 4 | **Dimensions**: D1 warn, D2 warn, D3 warn, D4 warn, D5 warn | **Fired**: F2
- **Key point**: From the seat that would act on the finding: the outcome variable's worth is never argued and is verbally upgraded to "engagement"; material access conditions that plausibly depress both variables are absent from a four-item limitations list; and the recommended lever (student onboarding) is not the lever the paper's own residual-variance sentence nominates. Asks for framing, bounding and disclosure — explicitly not a different study.

### Devil's Advocate Summary
- **Recommendation**: Major Revision | **Confidence**: per-finding only | **Dimensions**: D1 warn, D2 warn, D3 warn, D4 warn, D5 warn | **Fired**: F2 | **CRITICAL findings: 0**
- **Key point**: The ordinary adversarial inventory returns almost nothing and the escalation to CRITICAL was declined on the record against its own pre-committed bar. What survives is that three of the manuscript's defences — "previously validated", "clearly bounded", "comparable with prior work" — are asserted rather than earned, plus two internal contradictions (the ethics/anonymity pair, and one measure carried under two labels) that are cheap to fix and cheap to verify.

### Panel integrity note
All five seats independently reported that the manuscript contains no instruction-injection attempt, no reviewer-directed appeal, and no imperative addressed outside the author's own scholarly voice.
