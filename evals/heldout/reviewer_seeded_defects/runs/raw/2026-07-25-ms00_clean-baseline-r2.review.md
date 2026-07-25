# Isolated-dispatch panel review — gamma-2 (baseline condition, 2026-07-25)

(Phase 1 calls were physically separated: each seat’s pre-commitment was produced by a clean
headless `claude -p` call — claude-opus-5, effort xhigh, thinking enabled — that received only
the contract + title/field/word_count and was forbidden from reading any manuscript. Phase 2,
field analysis, and synthesis were separate paper-visible headless calls with read scope
limited to the named skill files and the neutral-named manuscript copy.)

# PART 1 — FIELD ANALYSIS

# Field Analysis Report

## Paper Basic Information
- **Title**: Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students
- **Abstract length**: ~165 words (single unstructured paragraph, plus 5 keywords)
- **Full text length**: ~1,750 words excluding references (~1,950 words including the reference list); 7 numbered sections
- **Number of references**: 6 (Costa & Wren, 2019; Delgado, 2020; Ibarra & Poll, 2021; Song, 2018; Vasquez, 2020; Whitfield, 2019) — all journal articles, all carrying DOIs in the `10.5555/` prefix range

---

## Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| **Primary Discipline** | Educational technology in higher education — specifically student adoption/engagement with institutional learning platforms (LMS) |
| **Secondary Disciplines** | (1) Information systems / technology acceptance research (TAM lineage — perceived usefulness as a construct); (2) Educational measurement & psychometrics (scale adaptation, reliability, single-item ordinal measurement); (3) Institutional research / higher-education practice (LMS onboarding, service design) |
| **Research Paradigm** | Quantitative Research — single-site cross-sectional correlational design; no qualitative component, no theory-building intent, explicitly framed as descriptive/correlational rather than model-testing |
| **Methodology Type** | Survey / Questionnaire (cross-sectional, non-probability volunteer sample, n = 214); analysis limited to descriptive statistics plus one bivariate association (Pearson r with Spearman ρ robustness check, 95% CI, a priori sensitivity statement) |
| **Target Journal Tier** | **Q3** (realistic), with a plausible Q4 landing and a Q2 stretch only if scope expands. Rationale: the manuscript is methodologically clean and epistemically disciplined but evidentially thin — a single bivariate correlation from one institution, one predictor, one self-report outcome item, no covariates, no subgroup analysis, no theoretical advance. Its own framing ("an incremental data point," "modest, design-bounded evidence") accurately forecloses Q1/Q2 ambition. The reference list (6 sources, no landmark TAM/UTAUT primary literature, no recent meta-analytic anchor) signals a specialized or regional outlet rather than a mainstream field journal. Q3 is where the contribution is defensible **as written**; Q2 would require either a second site, log-data validation, or a multivariate model. |
| **Paper Maturity** | **Pre-submission** — structure is complete and conventional (Abstract → Intro → Lit Review → Methods → Results → Discussion → Limitations → Conclusion → References), prose is polished with no rough drafting artifacts, citation formatting is consistent APA 7 with DOIs throughout, ethics and consent are reported, statistics are reported to journal convention (coefficient + CI + p + n), and limitations are candid and specific. What remains is not repair but **decision-level judgment**: whether a single-association single-site finding clears any given journal's contribution bar, and whether the near-invisible research-design gaps (below) are addressed before or after first submission. |

**Language note (Edge Case 5):** The manuscript is written in fluent academic English. All reviewer output should be produced in English.

**Cross-disciplinary note (Edge Case 1):** This paper touches three secondary fields but is *not* highly cross-disciplinary in the sense that triggers split coverage — the TAM lineage and the measurement critique are both **internal** to the paper's own argument. The genuine cross-disciplinary opening is on the *institutional practice* side (the paper's onboarding implication in §5), which is where Reviewer 3 is deliberately placed.

**Maturity-driven tone note (inverse of Edge Case 4):** This is emphatically *not* a low-quality first draft, and reviewers must be instructed **not** to compensate for its modesty by manufacturing severity. The paper pre-empts most standard criticisms (causality, self-report validity, single-site generalizability, effect-size modesty) in its own text. The risk profile here is the opposite of the usual: reviewers may either (a) reward epistemic humility so warmly that real design gaps go unexamined, or (b) re-issue criticisms the manuscript has already conceded, generating volume without value. Both failure modes are addressed in the cards below.

---

## Recommended Target Journals (Top 3)

1. **Journal of Computing in Higher Education** (Springer, Q2/Q3 boundary) — *Rationale*: publishes empirical LMS/platform-engagement work at modest scale, tolerates single-institution samples when reporting is transparent, and values explicit design-boundedness. Best fit for the paper's own self-description as an incremental, comparable data point. The bar it will apply: what does this add beyond an already large TAM-in-LMS literature? The paper must answer that in the Introduction, not only in the Discussion.

2. **Australasian Journal of Educational Technology (AJET)** (open access, Q2 in field rankings but receptive to institutional-scale studies) — *Rationale*: a long track record of single-site LMS studies with practitioner-facing implications, and an editorial culture that accepts correlational findings when causal language is disciplined — which this manuscript already does. Realistically the strongest of the three for acceptance probability relative to visibility.

3. **Journal of Information Technology Education: Research** (or an equivalent regional/specialized educational-technology outlet, Q3) — *Rationale*: the appropriate fallback tier if the two above reject on incremental-contribution grounds. Explicitly welcomes replication-flavored and single-institution evidence, where "one point in a distribution" (the paper's own Song, 2018 framing) is a feature rather than a deficiency.

*Deliberately excluded*: *Computers & Education*, *British Journal of Educational Technology*, *Internet and Higher Education* — all Q1 and all would desk-reject a single bivariate association from one campus, regardless of how well it is reported. Reviewers should not be configured to evaluate this manuscript against a Q1 bar it is not claiming.

---

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC (Editor-in-Chief)
**Identity Description**: Editor-in-Chief of *Journal of Computing in Higher Education*, a higher-education technology scholar who has handled several hundred LMS-adoption submissions over twelve years, publicly on record about the field's "TAM saturation" problem, and who personally triages roughly 60% of submissions at desk without external review
**Review Focus**:
  1. **Incremental-contribution test against a saturated literature**: The paper openly positions itself as "an incremental data point" (§2, §7). Determine whether that honesty is sufficient — does the manuscript state anywhere *what specific gap in the existing distribution of estimates it fills* (a population not yet sampled? an instrument not yet re-validated? a context-specific estimate)? Currently it names Song (2018) as showing between-institution variation but never says why *this* institution's point estimate is worth publishing. Assess whether that is fixable in revision or fatal at desk.
  2. **Fit and reader interest**: Would this journal's readership — largely practitioners-plus-researchers in institutional technology — find actionable value? The only practice implication (§5, LMS onboarding that "helps students see concrete usefulness") is one sentence, hedged twice, and is supported by a citation (Whitfield, 2019) rather than by the paper's own data. Judge whether the practical payload matches the journal's mandate or whether the paper is better placed in a purely research-oriented outlet.
  3. **Scope-to-claim proportionality and title/abstract accuracy**: Check that the title, abstract, and conclusion make no promise the design cannot keep. Verify the abstract's phrase "consistent with prior technology-acceptance research" is not doing argumentative work the 6-source literature base cannot support.
**Will particularly care about**: Whether "we are honest about our limitations" has been substituted for "we make a contribution" — an epistemically clean paper can still be an unpublishable paper, and the EIC's job is to say so without punishing the honesty.
**Possible blind spots**: The EIC will reason at the portfolio level and may not scrutinize the statistical or measurement internals at all — in particular will likely accept the reported r = .42, CI [.30, .52], α = .88, and the power statement at face value. Will also under-weight the ethics/sampling-frame questions. The synthesizer must not let a desk-level "insufficient contribution" verdict absorb or overshadow the specific technical findings from R1–R3.

---

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1 — Methodology
**Identity Description**: Quantitative methodologist in educational and psychological measurement, PhD in educational statistics, whose own research program is on the psychometrics of single-item versus multi-item measures and the consequences of treating ordinal Likert data as continuous; teaches a doctoral seminar on correlation, attenuation, and statistical power; has served as statistical reviewer for a measurement journal for eight years
**Review Focus**:
  1. **Reliability of the outcome variable and attenuation of the headline estimate**: The predictor is a 6-item scale with α = .88; the outcome is a **single** five-point frequency item whose reliability is unknown and unestimable from these data. Because a correlation is bounded by the geometric mean of the two reliabilities, the reported r = .42 is an attenuated estimate of unknown magnitude — and the paper's central interpretive claim ("moderate") is therefore itself uncertain in a direction the manuscript never discusses. The paper treats single-item self-report only as a *validity* problem (§6, divergence from logs) and never as a *reliability* problem. Determine whether the manuscript can be published without at minimum acknowledging attenuation, and whether test-retest or a multi-item use measure is required.
  2. **Coherence of the ordinal-measure treatment across Methods, Analysis, and Results**: §3.2 explicitly states "we treat this as an ordinal indicator," §3.4 then computes a **Pearson** correlation as the primary estimate with Spearman as a secondary "robustness check," and §4 reports the Pearson coefficient with a 95% CI as the headline. Interrogate this ordering: if the measure is ordinal by the authors' own declaration, the Spearman coefficient is arguably the primary estimate and Pearson the check. Also examine whether the 95% CI [.30, .52] — presumably Fisher-z based, which assumes bivariate normality — is defensible for a five-category ordinal variable, and whether the reported CI's derivation is stated anywhere (it is not). Note additionally that the Results report a **median category** for use (correctly, for ordinal data) while the analysis section correlates that same variable parametrically — an internal inconsistency in how the variable's measurement level is treated.
  3. **Power statement direction, and unreported analytic detail**: §3.4 reports >.80 power to detect r ≥ .19 at α = .05. Verify this is being used correctly — it is a *sensitivity* statement, and the paper deploys it appropriately (to establish the design could detect small effects) rather than as post hoc justification, which is a genuine strength worth affirming. Then check what is missing: whether the correlation is zero-order only with no covariates (yes — year level was collected per §3.1 but never used, despite Ibarra & Poll's 2021 context argument being cited approvingly in §2); whether any missing-data handling beyond listwise removal of the 14 incompletes is described (no); whether the six scale items or the exact use-item wording are reproduced anywhere (no — reproduction and replication both require them); and whether the "adapted" nature of the instrument (§3.2) is documented, since adaptation without reported changes means α = .88 cannot be compared to the source instrument's reliability.
**Will particularly care about**: Whether the numbers as reported are internally consistent and independently reconstructible — specifically that the paper's own stated measurement level for the outcome variable is honored by the statistic it foregrounds, and that the headline "moderate" is not an artifact of unacknowledged attenuation.
**Possible blind spots**: This reviewer will likely treat the substantive question as uninteresting and may dismiss the whole paper as "a correlation, competently reported" without engaging the contribution question or the practice implication. Will also probably not examine the sampling frame, consent, or the literature-base adequacy. Expect terse, technical, high-severity findings with little developmental framing — the synthesizer should preserve the technical content while re-tempering the tone toward the paper's actual (pre-submission, honest) maturity.

---

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2 — Domain
**Identity Description**: Senior higher-education researcher specializing in student engagement with institutional digital environments, who has published critiques of technology-acceptance model over-application in education and co-authored a systematic review of LMS engagement predictors; deeply familiar with the primary TAM/UTAUT lineage (Davis; Venkatesh and colleagues) and with the learning-analytics literature comparing self-reported and log-derived engagement
**Review Focus**:
  1. **Adequacy and provenance of the literature base**: The manuscript builds its entire theoretical warrant on 6 sources and **never cites the primary technology-acceptance literature it invokes**. §2 opens with "Research on technology acceptance has long proposed that perceived usefulness — the degree to which a person believes a technology will help them perform better — is among the factors associated with adoption" and attributes this to Costa & Wren (2019) and Delgado (2020). That definition is Davis's, and the construct's origin, its established measurement properties, and the meta-analytic evidence on its association with use are all absent. Assess whether a paper positioning itself as "comparable with prior work" (§2) can be comparable without naming the canonical instrument lineage or any meta-analytic/systematic-review benchmark against which r = .42 could be judged high, low, or typical. This is the most consequential domain gap in the manuscript and it is invisible from inside the paper's own framing.
  2. **Whether the stated contribution is actually delivered**: The paper claims to contribute "a single, transparently reported association... using a previously validated measure" (§2), positioned as one point in the Song (2018) distribution. Test that claim's internal logic: to be a usable point in a distribution, the estimate needs (a) comparability of instrument — but the instrument was *adapted* with unreported modifications; (b) comparability of outcome measure — but prior studies' outcome operationalizations are never described, so we cannot know whether r = .42 is even commensurable with theirs; and (c) a described population — but the sample is characterized only as "214 undergraduates at one mid-sized public university spanning all four year levels," with no discipline mix, no LMS platform named, no institutional LMS-maturity context. Determine what minimum sample and context description would make the estimate genuinely poolable, since poolability is the paper's whole stated value proposition.
  3. **Construct alignment between the theory invoked and the quantity measured**: The theoretical construct in the acceptance literature is *use behavior*; the measured quantity here is *self-reported access frequency in a typical week*. Access frequency is not engagement, not depth of use, not learning-relevant activity — a student opening the LMS six times daily to check announcements is coded as maximally "using" it. Evaluate whether the paper's Discussion and Conclusion respect this distinction. The manuscript is careful about the *self-report* gap (§2, §6, citing Vasquez, 2020) but silent about the *frequency-versus-engagement* gap, and the Abstract's phrase "perceived usefulness tracks with LMS engagement" quietly substitutes the broader word — a specific instance where the paper's otherwise-disciplined language slips.
**Will particularly care about**: Whether the paper's admirable hedging on *causality* has drawn attention away from an unhedged **construct** claim — the sliding of "self-reported weekly access frequency" into "LMS use," then into "LMS engagement," across Results → Discussion → Abstract, without any point at which the substitution is defended.
**Possible blind spots**: May be so focused on theoretical positioning and literature genealogy that the concrete statistical issues (attenuation, Pearson-versus-Spearman precedence, CI derivation) go unmentioned, and may over-prescribe a full acceptance-model test — which would contradict the paper's deliberately narrow, and legitimate, scope. The synthesizer should keep this reviewer's citation-base finding (which is decisive) while filtering any recommendation that amounts to "write a different, larger paper."

---

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3 — Cross-disciplinary / Practical
**Identity Description**: Director of institutional research and academic-technology assessment at a public university system, background in survey methodology and institutional data governance rather than in educational-technology theory; responsible for the design, fielding, and ethics review of campus-wide student surveys, and for advising provosts on whether a given piece of internal evidence is strong enough to justify spending on a platform or an onboarding programme
**Review Focus**:
  1. **Sampling frame, response rate, and non-response bias — the missing denominator**: §3.1 states "all enrolled undergraduates were eligible" and reports 233 received / 214 analyzed, but **never reports the population size or the response rate**. Without a denominator, 214 could be 15% of a small college or under 2% of a large one, and the survey's representativeness is unassessable. Compounding this, recruitment ran exclusively through "the institution's course-announcement channel" — a channel *inside the LMS being studied*. This is a structural selection problem the manuscript does not name: sampling for a study of LMS use through an LMS-delivered announcement systematically under-samples exactly the low-use students who anchor the low end of both variables, which plausibly restricts range and biases the correlation in an undetermined direction. §6 gestures at this ("students who engage more with institutional channels may be overrepresented") but treats it as generic volunteer bias rather than as *recruitment through the instrument's own subject matter*. Determine what the paper must report — population N, response rate, channel-specific caveat, and any available comparison of respondent to institutional demographics — before an institutional audience could use this estimate at all.
  2. **Duplicate removal, anonymity, and the internal consistency of the ethics account**: §3.3 states "no identifying information was collected, and responses could not be linked back to individual students," while §3.1 states 5 **duplicate entries** were removed. Ask directly how duplicates were identified without any linkable identifier — IP address, session cookie, or device fingerprint would each constitute identifying or quasi-identifying information and would qualify the anonymity claim; response-pattern matching would be a judgment call requiring a stated rule. This is not a technicality: it is the kind of internal contradiction that IRB reviewers and data-protection officers catch, and as written the Methods and the ethics statement cannot both be fully true. The manuscript must state the deduplication criterion explicitly.
  3. **Whether the finding can bear the institutional decision it gestures toward**: §5 suggests onboarding that "helps students see concrete usefulness... may be worth institutional attention." From a resource-allocation standpoint, evaluate what this correlation can and cannot license. A moderate cross-sectional association with a reversible causal direction (which the paper concedes) provides no basis for predicting that an onboarding intervention would change use — yet this sentence is the one an institutional reader will quote to a budget committee. Assess whether the hedging is strong enough for the way this sentence will actually be used, and whether the paper should instead frame the implication as a hypothesis for a pre-post or quasi-experimental follow-up. Also note what the paper collected but did not exploit: year level (§3.1) would have permitted the single most decision-relevant breakdown — whether the association differs for first-year students, precisely the population any onboarding programme targets.
**Will particularly care about**: Whether the survey would survive a campus-institutional-research audit — a stated denominator, a defensible sampling frame, a coherent anonymity-and-deduplication account — since without those, the estimate is not usable evidence for the institutional audience the Discussion addresses.
**Possible blind spots**: Will not evaluate theoretical positioning, TAM lineage, or the psychometrics of attenuation, and may over-weight practical usability relative to scholarly contribution — could recommend additions (demographic tables, subgroup breakdowns) that a research journal would consider out of scope for a short correlational report. Also may treat the response-rate omission as automatically disqualifying, when for some outlets it is a required-revision item rather than a rejection.

---

## Review Strategy Recommendations

**Special characteristics of this paper requiring particular attention:**

1. **The dominant risk is under-review, not over-review.** This manuscript is unusually disciplined: it hedges causality four separate times, cites a self-report-versus-logs critique (Vasquez, 2020) *against its own measure*, reports a Spearman robustness check, reports a CI and an a priori sensitivity analysis, and lists four candid limitations. That posture invites reviewers to grade the *epistemics* and skip the *design*. Every reviewer must be instructed that acknowledging a limitation is not the same as addressing it, and that the specific, still-unexamined issues are: an unreported response rate and population denominator; recruitment through the LMS under study; an unreliability-attenuated headline coefficient; a Methods/ethics contradiction about deduplication under claimed anonymity; a 6-source literature base with no primary TAM citation and no meta-analytic benchmark; and an unhedged construct slide from *access frequency* → *use* → *engagement*.

2. **Reviewers must not re-litigate what the paper already concedes.** Causal inference, single-site generalizability, effect-size modesty, and self-report-versus-log-data are all explicitly and adequately conceded in §2, §5, and §6. A reviewer who raises these as new findings is producing volume, not value. The instruction for all four seats: if a criticism appears in the manuscript's own Limitations, either escalate it to something specific and actionable ("the self-report limitation is stated, but the *reliability* consequence for the coefficient is not") or drop it.

3. **Calibrate to a Q3 bar, and state the bar being applied.** Configuring reviewers to a Q1 standard on a paper that explicitly disclaims Q1 ambition produces a rejection that teaches the author nothing. Reviewers should judge whether the paper is sound and publishable *somewhere appropriate*, and the EIC's contribution verdict should be phrased as a fit judgment ("below this journal's bar, appropriate for X") rather than a quality verdict.

4. **All six references are `10.5555/`-prefixed DOIs — flag for verification, do not adjudicate.** The `10.5555/` prefix is a test/reserved-range pattern, not a live registrant, and all six resolve to sequential `205000N` suffixes. This is consistent with an illustrative or synthetic reference list. The panel should record this as a provenance flag for the deterministic citation-verification layer to resolve; **no reviewer should assert on their own authority that the citations are fabricated**, and equally, no reviewer should treat citation existence as verified. Reviewers evaluate the *literature base's adequacy* (R2's Focus 1) on the assumption the works are as described — that critique holds regardless of how verification resolves.

5. **Three sections carry the paper's real load and should each get direct attention:** §3.1 (design and participants — where the denominator and sampling-frame problems live), §3.4 (analysis — where the measurement-level inconsistency lives), and the Abstract's final sentence (where the construct slide surfaces).

**Complementarity and tension between reviewers:**

- **Non-overlap is by construction.** EIC owns portfolio fit and contribution sufficiency; R1 owns the statistic's internal integrity; R2 owns the literature base and construct definition; R3 owns the sampling frame, the ethics/anonymity account, and decision-usability. No two seats share a focus item. Each seat is the *only* one positioned to catch its own decisive finding: only R1 will see the attenuation problem, only R2 will see the missing TAM primaries, only R3 will see the recruitment-channel circularity and the deduplication-versus-anonymity contradiction, and only the EIC will name the contribution question as a decision rather than a suggestion.

- **R3's angle is genuinely different in kind, not merely broader.** R3 is not "an educational technologist with a practical bent" — R3 is an institutional-research professional who evaluates surveys as *administrative evidence* rather than as *scholarship*. That produces findings the two academic reviewers structurally cannot generate: an academic reviewer accepts "n = 214 from one university" as a scope limitation, whereas an institutional-research reviewer immediately asks "214 out of how many, recruited how, and would I let a provost spend money on this?"

- **Expected tension 1 — scope expansion versus respecting the paper's narrow frame (R2 and R3 against the paper's own design).** R2 may push toward a full acceptance-model test with a proper theoretical genealogy; R3 may push toward demographic tables and subgroup analyses. Both would enlarge the paper past its declared scope. The paper's narrowness is a *legitimate design choice*, explicitly stated in §1 ("a deliberately narrow question"), and the synthesizer must separate "this claim is not supported by this design" (valid — retain) from "this should have been a bigger study" (a preference — demote or drop). The one place these converge legitimately: the **year-level variable was collected and never used** (R1 Focus 3, R3 Focus 3), so a first-year subgroup breakdown is available within the existing data and is not scope expansion. Two independent seats reaching this from different directions makes it a strong, low-cost revision item.

- **Expected tension 2 — R1's severity versus the paper's actual maturity.** R1 will likely be tersely negative in tone; the manuscript is pre-submission quality and reports its statistics better than most single-association papers. The synthesizer should carry R1's technical content forward at full strength while correcting a tonal implication that the paper is careless. It is not careless; it is small.

- **Expected tension 3 — EIC's desk-level verdict swallowing the technical findings.** If the EIC concludes "insufficient contribution for this journal," there is a real risk the decision letter collapses into a reject with the four technical findings appended as afterthoughts. Instruct the synthesizer to keep both tracks fully separate and fully reported: (a) the fit/contribution verdict, and (b) the soundness findings that must be addressed *regardless of which journal the paper goes to*. The author needs both — the first tells them where to submit, the second tells them what to fix before they do.

- **Coverage gap for the synthesizer to close.** No seat as configured is squarely responsible for **reporting-standards compliance** — whether the manuscript meets a survey-reporting checklist (e.g., AAPOR-style response-rate disclosure, or a journal's own survey-reporting requirements), and whether the absence of the six scale items and the exact use-item wording precludes replication. R1 and R3 each touch a fragment of this from opposite sides (R1 on item reproduction, R3 on response-rate disclosure). The synthesizer should consolidate these into one explicit reproducibility finding rather than leaving it split across two seats where it reads as minor in both.

# PART 2 — SEATS

## SEAT — EIC

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** From the editorial chair, this dimension asks whether the study's design, data handling, statistical reporting, and reproducibility affordances clear the bar my reviewers would apply before I send a manuscript out at all. My reading is deliberately bird's-eye: I am not re-deriving estimators or auditing the analysis line by line (that belongs to the methodology seat), but I do own the desk-level question of whether the design the authors chose can carry the claims the paper advertises, and whether enough procedural detail exists for a competent reader to judge that. For a cross-sectional survey of undergraduates in educational technology, the editorially decisive facts are sampling and response, instrument provenance, and whether the reporting is complete enough to be evaluated rather than merely believed.

**D2 — domain_accuracy (mandatory).** This dimension asks whether the paper's claims sit correctly inside the current evidence base of its field, whether prior work is represented as that work actually stands, and whether domain-specific terminology and reported results are used accurately. My editorial interest is representational integrity rather than exhaustive literature coverage: a paper may cite sparsely and still be publishable, but a paper that misattributes a construct, misstates what a named prior model or finding says, or uses a technical term of art in a sense the field does not recognise damages the journal's record. In educational technology specifically, the constructs in play carry a long measurement history, and terms describing use, adoption, and engagement have established meanings that cannot be reassigned silently.

**D3 — argumentative_coherence (mandatory).** This dimension asks whether the paper's central thesis holds together internally, whether the evidence actually offered supports the claims actually made, and whether any reasoning failure undermines the core argument. This is the closest of the five to my defining editorial function — the Title → Abstract → Introduction → Conclusion consistency check. The dominant editorial risk here is over-promising and under-delivering: a research question posed at one level of ambition and answered at another, or conclusions that quietly upgrade the strength of the design that produced them. The most common instance of that upgrade in this literature is the slide from association to causal or effectiveness language, and from a self-report measure to the behaviour it is presumed to stand for.

**D4 — cross_disciplinary_relevance (high priority).** This dimension asks whether the framing, definitions, and implications are legible and useful to readers in adjacent fields, and whether any claim that reaches across disciplinary boundaries is actually substantiated rather than asserted. As EIC this is a readership question first: my subscribers include instructional designers, institutional researchers, higher-education administrators, and information-systems scholars, and a paper earns space by being intelligible and consequential to more than the narrow sub-community that shares its jargon. The dimension is high-priority, not mandatory, which shapes how it can bind — under this contract a `block` here still carries editorial consequence, but a merely parochial framing is a revision matter, not a rejection.

**D5 — writing_and_structure (normal priority).** This dimension asks whether the manuscript is organised, expounded, tabulated, and formatted well enough to be reviewed and read — section logic, clarity of exposition, figure and table quality, and conformity to venue conventions. It is the lowest-stakes of the five and it is the one where my judgement should be most proportionate: prose that is merely plain is not a defect. What matters editorially is whether structural or presentational failure actively obstructs comprehension or verification. The declared length of roughly 1,600 words is itself a structural fact I must weigh — at that scale the question is not whether every conventional section is present at conventional length, but whether the format the authors chose is a coherent one and whether they have disclosed what the compression cost.

---

## Scoring Plan

### D1: methodology_rigor

what_to_look_for: Whether the design is named and matched to the question; sampling frame, recruitment channel, sample size, and response or completion rate; whether the sample is described well enough to bound generalisation (institution count, cohort, discipline mix); provenance of the survey instrument (adapted from an established scale with citation, or newly written) and any reliability or validity evidence for it; whether the outcome described as "self-reported use" is defined operationally (recall window, response scale, anchors); presence of ethics/consent statement; presence of the numbers a reader needs to check the analysis — denominators, dispersion alongside central tendency, effect sizes with intervals rather than bare significance; whether the data, instrument, or analysis code is available or its absence explained. I will treat the paper's own account of its methods as the evidence base and will not infer unreported procedure from convention.

what_triggers_block: Reported procedure is insufficient for any reviewer to establish what was actually done or to bound whom the results describe — for example, no usable account of who was surveyed or how they were recruited, no sample size or a size the reported analysis cannot support, an outcome measure never operationally defined, or inferential claims reported without the statistics that would let them be evaluated. Also block if a design-claim mismatch is fundamental rather than repairable: the analysis performed cannot in principle answer the question the paper says it answers, so no revision short of new data would fix it.

what_triggers_warn: Core procedure is recoverable but materially incomplete or unjustified — response rate absent or low without discussion, single-site convenience sample presented without acknowledging the limit, instrument adapted without citation or without reliability evidence, common-method or self-report bias unaddressed where both variables come from one questionnaire, missing-data handling unstated, or reproducibility affordances absent with no explanation. The distinguishing test is repairability: if the authors could satisfy the concern by reporting what they already have or by adding a bounded limitation, that is `warn`, not `block`.

### D2: domain_accuracy

what_to_look_for: Whether named constructs are used with the meaning the field assigns them, and whether any borrowed theoretical framework is described as its own source describes it; whether cited prior work is characterised accurately in direction and strength rather than recruited as generic support; whether empirical claims about the field's state ("the literature shows…", "it is well established…") are anchored to specific citations that could bear them; whether numbers, percentages, and reported results are internally consistent between abstract, body, and any tables; whether platform- and sector-specific terminology is used correctly; whether claims of novelty are stated in a form that could be checked. I will evaluate representational accuracy, not literature breadth — thin citation is a D3/D5 concern unless it produces a misstatement.

what_triggers_block: A factual or representational error at load-bearing position — a construct or framework misdefined in a way that invalidates how the paper interprets its own results, prior work asserted to say something it does not say and that misattribution carrying an inference the paper depends on, or reported results mutually contradictory across abstract, text, and tables such that the record cannot be trusted. Also block on an unsupportable priority or novelty claim stated as established fact.

what_triggers_warn: Domain slippage that is real but not load-bearing — imprecise or drifting use of a technical term, prior work cited in support of a claim broader than that work made, a general assertion about the field left uncited, a stale evidence base or terminology where the field has visibly moved on, or minor numerical inconsistency that a correction pass would resolve. Warn also applies where a claim's accuracy cannot be assessed from what is presented, and the uncertainty is material but not central.

### D3: argumentative_coherence

what_to_look_for: A research question stated explicitly and answered explicitly, with the answer addressing the question asked; consistency of scope and claim strength across Title → Abstract → Introduction → Results → Conclusion; whether each conclusion traces to a specific reported result; the verbs and modality used around the paper's central relationship, watching for the association→causation and association→effectiveness slides that a cross-sectional design cannot license; whether "self-reported use" is treated throughout as a self-report or silently converted into actual behaviour or learning gain; whether practice and policy recommendations are proportionate to what a single-timepoint survey can establish; whether stated limitations genuinely bound the conclusions or are ritual disclaimers contradicted by the surrounding text; whether alternative explanations (reverse causation, third variables, selection) are acknowledged where the design leaves them open.

what_triggers_block: The central argument does not survive its own evidence — causal, effectiveness, or temporal claims asserted in the abstract or conclusion from a cross-sectional correlational design; conclusions that answer a different question than the one posed; a title or abstract promising a contribution the body never delivers; or a reasoning failure (circularity, treating a measure as its own validation, generalising from the sample to a population the sample cannot represent) that the central thesis rests on. The test is whether removing the flawed step leaves the paper's stated contribution standing; if it does not, this is `block`.

what_triggers_warn: Coherence defects that are local or repairable by rewriting rather than by retreating from the paper's claim — occasional overreaching phrasing alongside otherwise correctly hedged claims, recommendations somewhat stronger than the evidence but not the paper's stated contribution, limitations acknowledged but not carried into the conclusion, a research question implied rather than stated, or an alternative explanation left unaddressed without the main claim depending on its exclusion.

### D4: cross_disciplinary_relevance

what_to_look_for: Whether the institutional platform, the student population, and the setting are described concretely enough for a reader elsewhere to judge transferability; whether field-specific constructs and acronyms are defined at first use for an adjacent-field reader; whether the implications section speaks to anyone beyond the single institution studied — instructional design, platform procurement, institutional policy, or the wider adoption literature; whether any claim reaching into another discipline (learning outcomes, organisational behaviour, information-systems theory, psychometrics) is supported by evidence from that discipline rather than asserted from within this one; whether the contribution is framed as a general question with a local instance, or only as a local report.

what_triggers_block: The paper is inaccessible or inert outside its own niche in a way no editing fixes — implications that hold only for one unnamed local configuration with nothing generalisable stated, or an interdisciplinary claim central to the paper's framing that is advanced with no supporting evidence from the discipline it borrows from. Given this dimension's high (not mandatory) priority, I will reserve `block` for genuine editorial disqualification on relevance grounds and will not use it for a paper that is merely modest in reach.

what_triggers_warn: Reach is narrower than the framing promises, or accessibility is uneven — jargon or acronyms undefined for adjacent readers, setting described too thinly for transferability to be judged, implications asserted for broader audiences without connecting evidence, or a contribution left implicitly local when a short reframing would extend it. Warn also applies where the paper's relevance depends on context the authors possess but have not reported.

### D5: writing_and_structure

what_to_look_for: Whether sections follow a recognisable and internally consistent logic; whether the abstract is a faithful, self-contained summary of what follows; clarity and economy of exposition; whether tables and figures are self-explanatory with defined variables, units, denominators, and complete captions, and whether each is cited and interpreted in the text; whether reference formatting is consistent and every in-text citation appears in the list and vice versa; whether the manuscript observes ordinary venue conventions for a short empirical report; and whether the roughly 1,600-word length is used coherently — proportionate across sections and with any compression-driven omission disclosed rather than silently absorbed.

what_triggers_block: Presentation obstructs review itself — structure so disordered that the argument cannot be followed, an abstract that misrepresents the body, results reported only in a table or figure that is unreadable or unlabelled so the finding cannot be extracted, or a citation apparatus so broken (missing references, systematic in-text/list mismatch) that claims cannot be traced. I will not `block` this dimension for style, register, or length alone.

what_triggers_warn: Defects that impede but do not prevent evaluation — sections out of proportion or a conventional element (e.g. a stated limitations or implications passage) absent without acknowledgement, imprecise or repetitive prose, tables or figures with incomplete captions or undefined abbreviations, inconsistent reference formatting, uneven numeric reporting conventions, or an abstract that under-represents rather than misrepresents the body.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## EIC Review Report

### Reviewer Identity

Editor-in-Chief of *Journal of Computing in Higher Education*, a higher-education technology scholar who has handled several hundred LMS-adoption submissions over twelve years, publicly on record about the field's "TAM saturation" problem, and who personally triages roughly 60% of submissions at desk without external review.

### Overall Recommendation

Major Revision

### Confidence Score

4

- High confidence. The manuscript sits squarely in the submission stream I triage daily; the topic, design, and contribution class are ones I have adjudicated many times. My confidence is not 5 because the statistical internals (attenuation, CI derivation, Pearson-vs-Spearman precedence) are Reviewer 1's territory, and my judgment here rests on the paper's own reporting of them rather than on independent reconstruction.

### Summary Assessment

This is a short, single-site cross-sectional survey (n = 214) reporting one bivariate association between an adapted six-item perceived-usefulness scale (α = .88) and a single-item measure of self-reported weekly LMS access frequency (r = .42, 95% CI [.30, .52], p < .001; Spearman ρ = .40). The manuscript is unusually well-behaved on the axis where papers in this literature most often fail: it declines causal language in §1, §5, §6, and §7; it cites Delgado (2020) against its own inferential reach and Vasquez (2020) against its own measure; it reports a confidence interval and an a priori sensitivity statement; and it names four candid limitations. That discipline is real and should be preserved in revision.

The editorial problem is not soundness but warrant. The paper positions itself as "an incremental data point, comparable with prior work" (§2) and as "one point in a distribution" following Song (2018) — yet it never states which gap in that distribution it fills, and it withholds precisely the information that would make the estimate poolable: no population denominator or response rate (§3.1), no discipline mix or LMS platform named, and an instrument described as "adapted" with no adaptation reported. A second problem is a construct slide the paper's own hedging discipline did not catch: the measured quantity is weekly access frequency, which travels through §4 and §5 as "use" and arrives in the Abstract as "LMS engagement," a broader term the design cannot support. Both are repairable within the existing data and scope. Neither is repaired as written.

### Strengths

1. **Epistemic discipline around causal reach is genuine, not decorative.** The paper does not merely append a causality caveat; it recruits Delgado (2020) in §2 and §5 to articulate the reverse pathway ("students who use a system more may come to perceive it as more useful"), and §7 closes with "offered as an incremental, design-bounded contribution rather than a causal claim." In a literature where correlational LMS surveys routinely drift into effectiveness language by the conclusion, this manuscript holds its line across all four load-bearing sections. This is the paper's strongest editorial asset.

2. **The paper cites the strongest available critique of its own measure.** §2 introduces Vasquez (2020) on the divergence of self-report from behavioral logs and then states, "we... treat our self-report measure as an indicator of perceived use rather than a behavioral count." Recruiting a source against one's own instrument is a marker of an author who has read the literature rather than mined it for support.

3. **Statistical reporting meets convention and exceeds the norm for this paper class.** §3.4 and §4 report coefficient, 95% CI, p, n, an ordinal-appropriate robustness check, a median category for the ordinal variable, and an a priori sensitivity statement (>.80 power to detect r ≥ .19). The sensitivity statement is deployed correctly — as evidence the design could detect small effects, not as post hoc justification of an obtained result. Many submissions at this scale report a bare coefficient and a p value.

4. **Scope is declared, not smuggled.** §1 announces "a deliberately narrow question" and explicitly disclaims testing a full acceptance model. I treat that narrowness as a legitimate design choice, and my objections below are about claims and reporting, not about the paper failing to be a larger study.

5. **Ethics reporting is present and specific.** §3.3 names committee review, voluntary participation, absence of incentive, and landing-page informed consent — reported at a level of detail many short empirical reports omit entirely.

### Weaknesses

1. **The stated contribution is asserted rather than located.** §2 claims the paper "contributes a single, transparently reported association... comparable with prior work," and cites Song (2018) for between-institution variation. But it never says why *this* institution's estimate advances that distribution: no statement of what population, context, or instrument condition is not yet represented in the existing estimates. For a saturated literature, "here is one more correlation, honestly reported" is a description of the object, not an argument for it. *Improvement:* add two to three sentences at the end of §2 stating the specific gap — a population characteristic, an institutional or platform-maturity condition, or a re-estimation with a differently adapted instrument — and carry that claim into §7. This is a rewriting task, not new data.

2. **The paper withholds the information that would make its estimate poolable.** Poolability is the paper's whole value proposition, yet §3.1 gives no population size and no response rate (233 received, 214 analyzed, denominator unstated), no discipline mix, and no LMS platform or institutional platform-maturity context; §3.2 calls the instrument "adapted from Costa and Wren (2019)" without reporting what was changed, which means the α = .88 cannot be compared with the source instrument and the estimate cannot be aligned with studies using the original. A reader cannot place this point in Song's distribution without knowing which axis it sits on. *Improvement:* report population N and response rate, a brief respondent-profile description, the platform and its institutional maturity, and either the adapted item wording or an explicit statement of the modifications.

3. **A construct slide runs from Results to Abstract without ever being defended.** §3.2 measures "how often the respondent accessed the LMS in a typical week." §4 and §5 discuss this as "use." The Abstract's final sentence states that "perceived usefulness tracks with LMS engagement among undergraduates." Access frequency, use, and engagement are three different constructs — a student who opens the platform repeatedly to check announcements is maximally frequent and minimally engaged. The paper hedges *self-report* rigorously and *frequency-versus-engagement* not at all, which is the more consequential substitution because it happens in the abstract, the part most readers will read alone. *Improvement:* fix the terminology to "self-reported access frequency" throughout the Abstract and Conclusion, or defend the broader reading explicitly; the current mixed usage is the one place where the paper's otherwise-careful language fails.

4. **The abstract's comparability claim rests on a literature base that cannot bear it.** The Abstract states the association "was consistent with prior technology-acceptance research," and §2 opens with a definition of perceived usefulness — "the degree to which a person believes a technology will help them perform better" — attributed to Costa & Wren (2019) and Delgado (2020). That is the acceptance literature's canonical construct definition, and the six-source reference list contains no primary technology-acceptance source and no meta-analytic or systematic-review benchmark. Without a benchmark, "consistent with prior research" is unevaluable: the reader has no basis for judging whether r = .42 is typical, high, or low for this relationship. *Improvement:* cite the construct's primary source and at least one quantitative synthesis, and either anchor "consistent with" to a reported range or replace it with a statement of what the estimate is being compared against.

5. **The one practice implication is carried by a citation rather than by the data, and will be over-read.** §5 suggests that onboarding which "helps students see concrete usefulness... may be worth institutional attention," supported by Whitfield (2019) and hedged as "suggested by, not proven by, the present correlation." For this journal's readership — institutional technology practitioners as well as researchers — this is the sentence that will be extracted and quoted to a resourcing committee, and a cross-sectional association with an explicitly reversible direction licenses no prediction about what an onboarding intervention would change. Relatedly, §3.1 records year level but the paper never uses it, forgoing the single most decision-relevant breakdown (first-year students are exactly whom onboarding targets) at zero data cost. *Improvement:* reframe the implication as a hypothesis for a pre-post or quasi-experimental follow-up, and add the year-level analysis, reported as exploratory.

### Detailed Comments

#### Journal Fit

Topically this belongs here: LMS engagement in higher education is core scope, and this journal has a documented tolerance for single-institution samples where reporting is transparent. Two fit questions are live. First, contribution — this journal's bar in a saturated TAM-in-LMS space is that a paper state what its estimate adds to the existing distribution, in the Introduction, not only in the Discussion; as written the manuscript does not clear that bar, and I would not send it out for review in its current form. It is repairable in revision, which is why my recommendation is major revision rather than desk rejection. Second, readership payload — the practice-facing half of my readership will find one hedged sentence in §5, sourced to a citation rather than to these data. That is thin for this outlet. If revision cannot supply either the contribution statement or a stronger practice-facing analysis (the unused year-level variable is the obvious lever for both), the paper is better placed at a research-oriented outlet such as *Australasian Journal of Educational Technology* or the *Journal of Information Technology Education: Research*, where a transparently reported single-site estimate is welcome on its own terms. I want to be explicit that this is a fit and warrant judgment, not a quality verdict: the paper is sound and will be publishable somewhere appropriate once the reporting gaps are closed.

#### Originality

The source of originality is new data, and only new data: no new method, no new instrument, no theoretical development, and by the authors' own declaration no model test. That is an acceptable basis for publication in this field, but only when the new data are characterized well enough to be usable by others — and here they are not (Weakness 2). Novelty is nowhere overclaimed, which I note in the paper's favor; there is no "first study to" language anywhere. The problem is the opposite: the paper is so restrained about its contribution that it never actually makes one, substituting an accurate description of its epistemic posture ("transparently reported," "design-bounded," "incremental") for a claim about what a reader gains. Honesty about limitations is not itself a contribution, and this is the central editorial issue in the manuscript.

#### Significance

If the finding holds, the impact is local and confirmatory: it adds one estimate, consistent in direction with existing work, to a well-populated literature. The paper says as much, and I do not fault it for that. Significance could be raised at no data cost in two ways — by locating the estimate within a stated benchmark range so readers learn something about where this campus sits, and by exploiting the year-level variable to say something about whom the association is stronger or weaker for. Both are within the existing dataset and the existing scope. Timeliness is adequate but not distinctive; LMS engagement remains a standing concern rather than an emerging one.

#### Structural Coherence

Title → Abstract → Introduction → Conclusion consistency is good on the causal axis and defective on the construct axis. The title says "Self-Reported Use," §1 asks about "self-reported frequency of use," §3.2 measures access frequency, §7 says "self-reported frequency of use" — and the Abstract's closing sentence says "LMS engagement." That single word is the coherence break: it is the broadest term in the paper, it appears in the most-read location, and no passage defends the widening. The Abstract also opens by noting that "students' engagement with them varies widely," which primes the same broader reading. The research question in §1 is explicit and the Conclusion answers exactly that question, which is more than many submissions manage. There is no over-promising on design strength; there is over-promising on construct breadth.

#### Title & Abstract

The title is accurate, informative, and appropriately unglamorous — it names both constructs, the design, and the population, and it does not overreach. The abstract is a faithful summary of the body on every point except the final sentence's "engagement" (see above) and the unanchored "consistent with prior technology-acceptance research." One further omission: the abstract reports r and p but not the confidence interval that the body reports and that constitutes part of the paper's reporting-quality case. Given that the paper's pitch is transparent reporting, the CI belongs in the abstract.

#### Conclusion

§7 is proportionate and correctly bounded — it restates the estimate with its design constraints, declines the causal reading, and names the right follow-up designs (log data, longitudinal, multi-institution). Two gaps. It inherits the contribution problem: "offered as an incremental, design-bounded contribution" tells the reader what kind of thing this is, not what they now know that they did not before. And it does not carry forward the limitations that most constrain interpretation — the unreported response rate and the volunteer-channel recruitment are conceded in §6 but exert no visible pressure on how the conclusion is stated.

### Questions for Authors

1. What is the undergraduate population from which the 214 respondents were drawn, and what was the response rate? Without a denominator, a reader cannot judge whether this estimate describes a substantial fraction of the student body or a small self-selected slice.

2. The survey was distributed "through the institution's course-announcement channel" (§3.1). Is that channel inside the LMS under study? If so, please state directly what it means for a study of LMS use to have been recruited through the LMS itself, and how that bears on the low end of both distributions — §6's "students who engage more with institutional channels may be overrepresented" reads as generic volunteer bias and may understate the issue.

3. §3.1 reports removal of 5 duplicate entries; §3.3 states that no identifying information was collected and that responses could not be linked to individuals. By what criterion were duplicates identified? Please state the rule, since as written the two passages are in tension.

4. In what respects was the Costa and Wren (2019) instrument "adapted" (§3.2)? Item count, wording, referent, or response format? This determines whether α = .88 and the resulting coefficient are comparable with studies using the source instrument — which is the precondition for the paper's own poolability claim.

5. Year level was collected (§3.1) but never analyzed. Does the association differ across year levels, particularly for first-year students? Reported as exploratory, this would materially strengthen the §5 onboarding implication at no additional data-collection cost.

6. What specific gap in the existing distribution of estimates does this study fill? A direct answer, placed in §2 and echoed in §7, would resolve my principal editorial reservation.

### Minor Issues

- Abstract: report the 95% CI alongside r = .42, consistent with the body's reporting standard.
- Abstract, final sentence: "LMS engagement" should read "self-reported LMS use" or "self-reported access frequency" unless the broader construct is defended in the body.
- §2: the definition of perceived usefulness is the acceptance literature's canonical formulation but is attributed only to two secondary sources; add the primary citation.
- §4: "The proportion of variance shared by the two measures was accordingly modest" — state the value rather than characterizing it, given the paper's transparency commitment.
- §3.1: name the LMS platform, or state why it is withheld; platform identity is material to transferability.
- §3.4: state how the 95% CI was derived; the derivation method is not reported anywhere.
- §6: the four limitations are listed but none is carried into §7; a one-sentence bridge would close the loop.
- References: all six DOIs fall in the `10.5555/` prefix range with sequential suffixes. I record this as a provenance flag for the deterministic citation-verification layer and make no finding on it here; my assessment of the literature base above holds regardless of how verification resolves, since it concerns adequacy and attribution, not existence.

---

contract_role: eic

## Dimension Scores

### D1: methodology_rigor

score: warn

My Phase 1 plan committed to `warn` where core procedure is recoverable but materially incomplete or unjustified, with repairability as the distinguishing test, and to `block` only where a reviewer could not establish what was done or whom the results describe. The design is named and matched to the question; n = 214 is reported with an exclusion account; the instrument's source, response format, scoring, and α are given; ethics and consent are reported; the outcome item's recall window and anchors are specified; and the analysis reports coefficient, CI, p, n, and an ordinal robustness check. That is enough to establish what was done. Four committed `warn` triggers fire: response rate absent (no population denominator against 233 received), instrument adapted without the adaptation reported (§3.2), recruitment channel and volunteer selection acknowledged only generically (§6), and reproducibility affordances absent — neither the six scale items nor the exact use-item wording is reproduced, and no data or code availability statement appears. A fifth item is an internal-consistency defect rather than a gap: §3.1's removal of 5 duplicates and §3.3's claim that no identifying information was collected cannot both be fully true without a stated deduplication rule. Every one of these is satisfiable by reporting what the authors already possess or by a bounded addition. `warn`, not `block`.

### D2: domain_accuracy

score: warn

My Phase 1 plan reserved `block` for representational error at load-bearing position — a construct misdefined such that the paper's interpretation of its own results is invalidated, prior work asserted to say what it does not say with a dependent inference, or mutually contradictory reported results. None of those is present. Prior work is characterized accurately and with unusual care: Delgado (2020) is cited for the reverse-pathway caution, Vasquez (2020) against the paper's own measure, Song (2018) for between-institution variation, Ibarra and Poll (2021) for context. Numbers are internally consistent across abstract, methods, and results. The committed `warn` triggers do fire. The canonical perceived-usefulness definition in §2 is attributed to two secondary sources with no primary acceptance-literature citation, which is attribution slippage rather than misdefinition. The Abstract's "consistent with prior technology-acceptance research" is a comparability claim broader than a six-source base with no quantitative benchmark can support — real, but not load-bearing, since the paper's finding stands independently of whether it matches a benchmark. And "engagement" in the Abstract's final sentence is a term-of-art widening beyond the measured quantity. Under my committed test this is domain slippage that is real but not invalidating: `warn`.

### D3: argumentative_coherence

score: warn

My Phase 1 plan committed to `block` for causal, effectiveness, or temporal claims asserted from a cross-sectional design, or for a reasoning failure the central thesis rests on, with the test being whether removing the flawed step leaves the stated contribution standing. On the causal axis the paper is exemplary: §1, §5, §6, and §7 all decline the causal reading, §5 states the reverse pathway explicitly, and §7's "rather than a causal claim" is unambiguous. The research question is stated in §1 and answered in §7 at the same scope. The practice implication in §5 is doubly hedged. So the block triggers do not fire on the axis I most expected them to. Two `warn`-tier defects do. First, the construct slide from measured access frequency (§3.2) to "use" (§4, §5) to "engagement" (Abstract) is never defended at any point — repairable by rewriting, and the paper's association claim survives the correction, so it is `warn` under my committed test rather than `block`. Second, §6's four limitations are stated but exert no pressure on §7, which restates the finding without inheriting them; my plan named exactly this pattern ("limitations acknowledged but not carried into the conclusion") as `warn`. I note also that the paper's stated contribution — an incremental, poolable data point — is undermined by the missing comparability information rather than by a reasoning error, which I score under D1 and D2 where the missing reporting lives.

### D4: cross_disciplinary_relevance

score: warn

My Phase 1 plan reserved `block` for a paper inert outside its niche with nothing generalisable stated, or an interdisciplinary claim central to the framing advanced with no supporting evidence, and explicitly declined to use `block` for a paper merely modest in reach. The framing is legible to adjacent readers: perceived usefulness is defined in §2 in plain terms, the acronym is expanded, the design is described in ordinary language, and §4's "in plain terms" gloss is a genuine courtesy to non-specialists. The contribution is framed as a general question with a local instance, which satisfies my committed non-block test. The `warn` triggers fire on transferability and on connecting evidence. The setting is described too thinly for a reader elsewhere to judge transfer — no platform named, no discipline mix, no institutional platform-maturity context, no population denominator — and my plan named exactly this ("setting described too thinly for transferability to be judged"). The one implication reaching into institutional practice (§5, onboarding) is supported by a practitioner citation rather than by these data, which is my committed "implications asserted for broader audiences without connecting evidence" trigger. The unused year-level variable is the low-cost lever that would give the adjacent practitioner readership something actionable. `warn`.

### D5: writing_and_structure

score: pass

My Phase 1 plan committed to `block` only where presentation obstructs review, and to `warn` for defects that impede but do not prevent evaluation, with a stated commitment not to penalize style, register, or length alone. Structure follows a conventional and internally consistent order across seven numbered sections; the exposition is clear and economical; the abstract is self-contained and faithful to the body on every point but one word; the reference list is consistently formatted and every in-text citation appears in it and vice versa; and the roughly 1,750-word length is proportionately distributed with methods carrying the most detail, which is the right allocation for a short empirical report. There are no figures or tables, and given a single bivariate result reported inline with full statistics, none is required — the finding is fully extractable from §4. I considered `warn` on the ground that the abstract's "engagement" is an infidelity to the body, but that defect is a construct claim, not a presentational one, and I have already scored it under D2 and D3; scoring it a third time here would triple-count a single flaw. Nothing in the presentation impedes evaluation. `pass`.

## Failure Condition Checks

### F1

fired: false

Predicate: any mandatory dimension scores `block`. My mandatory dimensions are D1 (warn), D2 (warn), D3 (warn). None scores `block`.

### F2

fired: true

Predicate: two or more mandatory dimensions score `warn` or worse. All three mandatory dimensions — D1, D2, D3 — score `warn`. Threshold of two is exceeded. (The `cross_reviewer_quantifier: majority` is panel-level machinery for the synthesizer; I evaluate only the expression against my own scores.)

### F3

fired: false

Predicate: any high-priority dimension scores `block`. My only high-priority dimension is D4, which scores `warn`, not `block`.

### F0

fired: false

Predicate: every mandatory dimension scores `pass`. D1, D2, and D3 all score `warn`. The condition does not hold.

## Review Body

My editorial position is that this manuscript is sound and dishonest about nothing, but not yet warranted for this journal — and that the distance between those two states is smaller than the author may fear.

Start with what should not be re-litigated. The paper concedes causality, single-site generalizability, effect-size modesty, and the self-report-versus-log-data gap in its own text, at four separate places, with citations recruited against its own position. Re-issuing those as review findings would be volume without value, and I have not done so. Where I have engaged those areas, it is because the concession does not reach the specific consequence: §6 concedes voluntary response, but the recruitment channel appears to be inside the very system under study, which is a structural selection issue rather than generic volunteer bias; §6 concedes self-report, but nothing in the paper carries those four concessions into §7, where the finding is restated as though unconstrained.

The editorial issue proper is warrant. The paper's declared value is that it supplies a poolable point estimate — "one point in a distribution rather than a fixed value," in Song's (2018) framing that §2 adopts. I accept that as a legitimate basis for publication; this journal publishes such papers. But poolability is a demanding property, and the manuscript withholds three of the things that would confer it. There is no population denominator or response rate, so the estimate's representativeness within its own campus is unassessable. There is no platform identity, discipline mix, or institutional platform-maturity description, so a reader cannot say which axis of Song's distribution this point sits on. And the instrument is "adapted" with the adaptation unreported, so neither α = .88 nor r = .42 can be aligned with studies using the source measure. A point estimate that cannot be located is not a point in a distribution; it is a number. All three are reporting gaps, not design failures — the authors almost certainly hold this information — which is why this is a revision, not a rejection.

The second substantive finding is a construct slide, and I flag it precisely because it is the one place where an otherwise disciplined manuscript loses its grip. The measured quantity is how often a respondent accessed the LMS in a typical week. That becomes "use" in §4 and §5 — a defensible shorthand — and then "LMS engagement" in the Abstract's final sentence, which is not. Engagement in this literature connotes depth and learning-relevant activity; access frequency measures neither, and a student who opens the platform six times a day to check announcements scores maximally on the measure and tells us little about engagement. The paper hedges the self-report gap thoroughly and the frequency-versus-engagement gap not at all, and the unhedged one lands in the abstract, where it will be read by people who read nothing else. This is a wording repair, but it is a wording repair in the highest-traffic sentence of the paper.

Third, and bearing on both of the above: §2 builds the entire theoretical warrant on six sources, none of them the primary acceptance literature whose canonical construct definition §2 restates, and none a quantitative synthesis. The Abstract's claim that the association was "consistent with prior technology-acceptance research" therefore has nothing behind it that a reader could check. This is not a demand for literature breadth for its own sake — a short paper may cite sparsely. It is that comparability is the paper's stated contribution, and comparability claims require a benchmark. Separately, I record without adjudicating that all six DOIs fall in the `10.5555/` reserved prefix range with sequential suffixes; that is a matter for the deterministic verification layer, and my finding on the adequacy and attribution of the literature base stands either way.

Two notes on proportionality. First, I have deliberately not scored this manuscript against a Q1 bar it does not claim. §1 declares a deliberately narrow question and disclaims a model test; that narrowness is a design choice I respect, and none of my findings amounts to "this should have been a bigger study." Every repair I have asked for is available within the existing dataset, the existing sample, and the existing scope — including the one addition I actively recommend, the year-level breakdown, using a variable §3.1 says was already collected and §4 never mentions again. Second, on integrity: the manuscript contains no instruction-injection attempt, no address to reviewers, and no rhetorical pressure on the review process; it is content throughout. I note this because its absence is worth recording, not because anything triggered a concern.

The three mandatory dimensions each carry a `warn`, so F2 fires and my seat's contribution to the panel is a major-revision signal. I would restate the substance plainly for the author: nothing here needs to be unlearned or redone. What the paper needs is to say what it adds, report what it already knows, and stop using one word it has not earned. That is a revision I would expect to succeed.

## Editorial Decision

editorial_decision=major_revision

---

## SEAT — Peer Reviewer 1 (Methodology)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** As Peer Reviewer 1, this is my primary charge: does the study's design actually support the inferences it draws? For a cross-sectional survey of undergraduates on LMS perceived usefulness and self-reported use, this means the paper must state its design explicitly, justify its sampling frame and recruitment path, report achieved sample size against some defensibility argument (power analysis or precision target), document the measurement instruments with reliability and validity evidence rather than asserting them, handle missing data transparently, and report analyses with effect sizes and interval estimates rather than bare *p*-values. Reproducibility affordances count here too: procedural detail sufficient for independent replication, instrument availability, ethics approval, and any data/code availability statement. The field's bar for educational-technology survey work is not exotic — it is the ordinary TAM/UTAUT-adjacent standard of documented instrument provenance, reported response rate, and analysis assumptions checked — but a 1,597-word manuscript has very little room to satisfy it, so the compression risk is real and must be judged on what is actually reported, not on what a longer paper would presumably have said.

**D2 — domain_accuracy (mandatory).** From a methodology seat, my legitimate purchase on domain accuracy is narrow and I will keep it narrow: I assess whether methodological and measurement terminology is used correctly and whether reported results are internally consistent with the described procedures. Misuse of psychometric vocabulary (calling a coefficient alpha a validity index, conflating reliability with accuracy), misdescription of a statistical procedure, or numbers in the text that cannot be reconciled with the reported design are within my remit. Whether the paper's substantive claims about LMS adoption literature are current or correctly attributed belongs to Reviewer 2, and I will not score that.

**D3 — argumentative_coherence (mandatory).** I evaluate this dimension strictly through the evidence-to-claim link: do the conclusions stay within what a cross-sectional self-report design can license? This paper type carries two structurally predictable hazards. First, causal or directional language ("perceived usefulness drives use," "increasing usefulness will raise engagement") from correlational cross-sectional data — reverse causation and third-variable explanations are equally consistent with the same correlation. Second, common-method variance: when both the predictor and the outcome are self-reported in one instrument at one sitting, part of the observed association is attributable to shared method rather than shared construct. Coherence here means the argument is stated at the strength the data can carry, and known threats are acknowledged rather than left silent.

**D4 — cross_disciplinary_relevance (high priority).** Reviewer 3 owns the substantive interdisciplinary case; my contribution is methodological transparency as a precondition for any adjacent-field reader to evaluate the work. Concretely: are the constructs operationalized in terms a reader outside educational technology can interpret without knowing the local instrument tradition, and is the population and setting described precisely enough that transfer boundaries are visible? A claim that findings generalize across institutions or disciplines is a methodological claim about sampling and must be substantiated by sampling, not asserted by framing.

**D5 — writing_and_structure (normal priority).** I judge this only within the methodological reporting surface: whether the Methods section is organized so that design, participants, instrument, procedure, and analysis are separately locatable; whether tables and figures report the statistics they claim to report with sufficient labeling to be read independently; and whether reporting conventions (APA 7.0 statistical formatting, decimal and italicization conventions, complete table notes) are followed. General prose quality across the manuscript is not my dimension, and I will not inflate a stylistic complaint into a methodology finding.

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for` — An explicit design statement naming the cross-sectional survey design and its limits; the sampling frame, recruitment channel, and selection method (probability vs convenience) with the term used correctly; achieved *N*, the denominator it came from, and the response rate; any a priori power analysis or precision justification; instrument provenance (adapted from a named source vs newly written), item counts, response scale, and reported reliability (α or ω) with validity evidence (factor structure, CFA fit, discriminant evidence); how "self-reported use" was operationalized (frequency scale, recall window, or single-item estimate) and whether any objective LMS log data was used as a validation anchor; missing-data quantity and handling method; statistical assumption checks appropriate to the analysis run; effect sizes and 95% CIs alongside every test statistic; ethics/IRB approval and consent statement; data, instrument, or code availability.
- `what_triggers_block` — Any one of the following load-bearing absences or contradictions: (a) no usable description of how participants were obtained, so the sample's relation to any population is unknowable; (b) the measurement instrument is neither reproduced, cited to a source, nor described item-by-item, so the constructs cannot be reconstructed; (c) inferential claims are made with no reported test statistics at all, or with statistics that are internally inconsistent (reported *N*, *df*, and test values that cannot coexist); (d) a single-item or unvalidated self-report measure carries the paper's central inferential claim with no reliability evidence and no acknowledgment that this is a limitation; (e) no ethics approval or consent statement for primary human-subjects data collection.
- `what_triggers_warn` — Any one of: effect sizes or confidence intervals absent while *p*-values are reported; reliability reported but validity evidence entirely absent; convenience sample used without justification or without a stated limit on generalization; sample size reported with no power or precision rationale; missing data not quantified or handling method unstated; statistical assumptions not addressed for the tests actually run; APA-noncompliant statistical reporting that leaves a result ambiguous rather than merely untidy; procedure described too thinly for replication (administration mode, timing, incentives, or recall window unstated); no data/instrument availability statement.

### D2: domain_accuracy
- `what_to_look_for` — Correct and consistent use of methodological and psychometric terminology (reliability vs validity, correlation vs association vs prediction, significance vs effect magnitude, sample vs population, response rate vs completion rate); a named theoretical model (TAM/UTAUT or similar) whose constructs are operationalized as that model actually defines them if invoked; numbers that reconcile across abstract, results text, and tables; correct naming of the statistical procedures actually performed.
- `what_triggers_block` — A methodological or measurement claim that is demonstrably wrong on its face and load-bearing for a conclusion: e.g., a reliability coefficient presented as evidence of validity where validity is the claim being defended; a statistical test described as doing something it cannot do (a correlation reported as establishing causal effect, a significance test reported as estimating effect magnitude); or figures that contradict each other across sections in a way that makes the reported result indeterminate.
- `what_triggers_warn` — Loose or drifting terminology that does not by itself invalidate a conclusion: "predicts" used for a cross-sectional association; "representative" used for a convenience sample; a named adoption model invoked without its constructs being operationalized as defined; minor numerical inconsistencies (rounding, a decimal mismatch between text and table) that do not change the substantive result.

### D3: argumentative_coherence
- `what_to_look_for` — Whether the verbs attached to the central finding match a correlational cross-sectional design; whether reverse causation (heavier users rationalize the system as useful) and third-variable explanations (course requirements, instructor mandate, prior digital fluency) are acknowledged; whether common-method variance is named as a threat given both constructs are self-reported in one instrument; whether non-significant or unfavorable results are reported alongside supportive ones; whether the recommendations section stays inside the evidence or slides into intervention prescriptions the design cannot license; whether the abstract's claim strength matches the results section's.
- `what_triggers_block` — Explicit causal or interventionist conclusions drawn from cross-sectional correlational self-report data with no design-based warrant and no acknowledgment of the limitation — e.g., recommending that institutions change LMS design or policy *because* usefulness was shown to raise use; or a stated conclusion that the reported results do not support at all (results show a weak or null association, conclusion asserts a strong one); or evidence of selective reporting, where the analyses described in Methods do not all appear in Results and the omission favors the hypothesis.
- `what_triggers_warn` — Directional language ("influences," "leads to," "drives") used loosely while a limitations section does correctly flag the correlational constraint; common-method variance unaddressed; reverse causation unmentioned; abstract claiming somewhat more than the results section supports; limitations acknowledged in a boilerplate paragraph that does not connect any specific limitation to any specific claim.

### D4: cross_disciplinary_relevance
- `what_to_look_for` — Whether constructs ("perceived usefulness," "use") are operationally defined so a reader from psychology, information systems, or general higher-education research can interpret them without local instrument knowledge; whether the institutional setting, LMS platform, disciplinary mix, and student level are described precisely enough for a reader to judge transferability; whether any claim of broader applicability is backed by the sampling design rather than by framing alone; whether jargon specific to educational-technology adoption research is defined at first use.
- `what_triggers_block` — A generalization claim that the sampling design cannot support and that is central to the paper's stated contribution — e.g., single-institution single-platform convenience data presented as characterizing undergraduate LMS adoption generally, with no boundary statement anywhere in the manuscript.
- `what_triggers_warn` — Constructs used without operational definition so that an adjacent-field reader must infer the measure; setting described too thinly to locate the transfer boundary (platform, institution type, or disciplinary composition unstated); implications addressed to audiences beyond the sampled population without a stated caveat; undefined field-specific jargon that obscures what was measured.

### D5: writing_and_structure
- `what_to_look_for` — A locatable Methods section with distinguishable design / participants / instrument / procedure / analysis components; tables and figures that are self-contained (complete labels, units, *N*, notes defining abbreviations and significance markers); statistics formatted per APA 7.0 (italicized symbols, leading-zero convention for bounded coefficients, correct decimal places, correct *p*-value formatting); consistency between the abstract's methodological summary and the Methods section; no methodological detail that appears only in the discussion.
- `what_triggers_block` — Methodological reporting so disorganized that the procedure cannot be reconstructed from the text at all — e.g., no identifiable Methods content anywhere, or a results table whose labeling makes it impossible to determine what was analyzed. (I set a deliberately high bar here: D5 is normal-priority and a `block` from this seat should reflect unreadability of the method, not stylistic dissatisfaction.)
- `what_triggers_warn` — Methods content scattered across sections rather than consolidated; tables or figures that require the body text to be interpretable (missing notes, undefined abbreviations, absent *N*); recurring APA 7.0 statistical-formatting deviations; abstract's method description inconsistent with the Methods section; word-count compression that visibly omits standard reporting elements rather than merely condensing them.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Methodology Review Report (Peer Reviewer 1)

### Reviewer Identity

Quantitative methodologist in educational and psychological measurement (PhD, educational statistics). My own research program concerns the psychometrics of single-item versus multi-item measures and the consequences of treating ordinal Likert data as continuous; I teach a doctoral seminar on correlation, attenuation, and statistical power, and have served as statistical reviewer for a measurement journal for eight years.

### Overall Recommendation

Major Revision

### Confidence Score

4

### Summary Assessment

This is a competently reported single-association study whose statistical reporting is above the norm for its class: the primary estimate carries a confidence interval, a *p* value, and a sample size; a rank-based robustness check is reported alongside the parametric estimate; assumption inspection is described; and the sensitivity statement in §3.4 is deployed in the correct direction (establishing the smallest detectable effect a priori, not rationalizing an obtained result post hoc). I was able to reconstruct the reported interval and test independently from the reported coefficient and *n*, which is more than most manuscripts of this length permit.

The revision burden is nonetheless substantial and concentrated in measurement. The paper's headline coefficient is the correlation between a six-item composite (α = .88) and a **single** five-point frequency item of unknown and, from these data, unestimable reliability. Because an observed correlation is bounded by the geometric mean of the two reliabilities, r = .42 is an attenuated estimate of unknown magnitude, and the interpretive label "moderate" is therefore itself uncertain in a direction the manuscript never discusses. Compounding this, the authors declare the outcome ordinal in §3.2, foreground a Pearson coefficient in §3.4–§4, and report a median for the same variable in §4 — three different measurement-level commitments in three sections. Neither the scale items nor the exact use-item wording is reproduced, so neither the α nor the association is reconstructible by an independent group.

### Strengths

1. **Sensitivity statement used in the correct direction, and it reconstructs.** §3.4's "greater than .80 power to detect a correlation of *r* ≥ .19 at alpha = .05 (two-tailed)" is a design-sensitivity claim established before the estimate, not a post hoc power calculation on the obtained effect. This is the right use and worth affirming explicitly, because the wrong use is far more common. My own reconstruction lands on the boundary (see Minor Issues), but the logic and the direction are sound.

2. **The primary estimate is independently reconstructible.** From r = .42 and n = 214, a Fisher-*z* interval using SE = 1/√(n − 3) returns [.30, .52], reproducing §4 exactly; the implied *t* ≈ 6.7 on 212 *df* is consistent with *p* < .001. Reporting the coefficient, interval, *p*, and *n* together (§3.4, §4) allowed this check without author correspondence.

3. **One pre-specified association, so no multiple-comparison or selective-reporting exposure.** Every analysis named in §3.4 appears in §4, and nothing appears in §4 that was not named in §3.4. With a single bivariate test and no subgroup or covariate exploration, the manuscript carries essentially no *p*-hacking or HARKing surface — a real methodological virtue that the narrowness of the design purchases. Assumption inspection (linearity, monotonicity, bivariate outliers, distributional symmetry) is reported rather than assumed.

4. **Rank-based robustness check reported and interpreted.** §4's ρ = .40 alongside r = .42 demonstrates that the substantive conclusion does not hinge on the scoring of the ordinal variable as ranks versus integers. The check does not do everything §4 claims for it (see W2), but reporting it at all, in a paper this short, reflects genuine care.

5. **Participant accounting and ethics reporting are complete at the level of counts.** §3.1 gives the full disposition (233 received → 14 incomplete and 5 duplicates removed → 214 analyzed) with reasons attached to counts, and §3.3 reports ethics-committee approval, informed consent on the landing page, voluntariness, and the explicit absence of credit or payment. Many short survey reports omit at least one of these.

### Weaknesses

1. **The outcome's unknown reliability attenuates the headline coefficient by an unquantified amount, and the manuscript treats single-item self-report solely as a validity problem.** §6 acknowledges that use "was self-reported through a single item rather than measured through system logs" and that self-reports diverge from behavioral traces — that is the *validity* concern, and it is correctly stated. The *reliability* consequence is never raised. A correlation cannot exceed √(ρ_xx · ρ_yy); with ρ_xx = .88 the constraint is essentially entirely on the outcome. Purely to illustrate the sensitivity, and not as an estimate: if the use item's reliability were .70, the disattenuated correlation would be ≈ .54; at .50 it would be ≈ .63. Under plausible values the label in the Abstract, §4, §5, and §7 could move from "moderate" to "strong." *Why this matters:* the interpretive adjective is the paper's only substantive claim, and its stability is currently unknown. *Suggested remedy:* either add a defensible reliability estimate for the outcome (a short test–retest sub-sample, or a two-to-three-item use measure), or — if the data are fixed — state the attenuation constraint explicitly in §3.4 and §6, report a disattenuation sensitivity range under stated assumed reliabilities, and label the coefficient as a lower bound on the disattenuated association rather than as a point characterization.

2. **The measurement level of the outcome is treated three different ways across §3.2, §3.4, and §4, and the interval's derivation is neither stated nor justified.** §3.2 declares "we treat this as an ordinal indicator"; §3.4 makes Pearson the primary estimate and Spearman a "robustness check"; §4 reports a median category for the same variable (correct for ordinal data) while headlining the parametric coefficient with a normal-theory interval. *Why this matters:* on the authors' own declaration, Spearman — or better, a polyserial correlation between the continuous composite and the ordinal item — is the design-matched estimator, and Pearson is the check. Further, §4's claim that agreement between r and ρ shows "the association did not depend on the parametric assumption" overstates what the check delivers: both coefficients are computed on the same five heavily tied categories, so their agreement bounds sensitivity to rank-versus-integer scoring but says nothing about the attenuation induced by coarse categorization itself, and nothing about the bivariate-normality assumption underlying the Fisher-*z* interval, which cannot hold for a five-category variable. The interval reproduces under Fisher-*z* with 1/√(n − 3), but the manuscript never says so. *Suggested remedy:* state the interval's derivation in §3.4; add a distribution-free interval (BCa bootstrap) and report it alongside; either promote the rank-based or polyserial estimate to primary or justify in one sentence why Pearson is primary given §3.2's declaration; report ρ with its own interval and *p* rather than as a bare coefficient; and reconcile §4's median with the parametric treatment of the same variable.

3. **The instrument is not reproducible, and the "previously validated" warrant does not survive undocumented adaptation.** §3.2 reports six items "adapted from Costa and Wren (2019)" but reproduces none of them, does not state what the adaptation changed, and does not give the exact wording of the use item beyond a paraphrase. *Why this matters:* three distinct consequences follow. Replication is impossible — a second group cannot administer this instrument. The α = .88 cannot be compared to the source instrument's reliability, because the two are not known to be the same instrument. And the description of the measure as "previously validated" (Abstract, §2) transfers validation evidence from the source form to an altered form on no stated basis; the only psychometric evidence offered in-sample is internal consistency, which speaks to reliability, not to structure or discriminant validity. *Suggested remedy:* reproduce all six items and the verbatim use item in an appendix or supplement; state every modification made to the source items and why; and either add in-sample structural evidence (a one-factor confirmatory model with fit indices, given n = 214) or narrow the wording from "previously validated instrument" to "items adapted from a previously validated instrument, with the adapted form's structure not re-examined here."

4. **The denominator, the response rate, and the outcome's category distribution are all unreported, so restriction of range cannot be assessed.** §3.1 states that "all enrolled undergraduates were eligible" and gives 233 received, but never the size of that eligible population; §4 gives only a median category for the use item. *Why this matters:* this is a statistical problem before it is a representativeness problem. A correlation's magnitude is conditional on the observed variance of both variables. Recruitment through the institution's course-announcement channel — a channel delivered inside the very system under study — plausibly under-represents the low-use tail, and the median of "a few times per week" on a five-point scale is consistent with clustering in the upper categories. If range on the outcome is restricted, r = .42 is attenuated for a second, independent reason; if it is not, the concern dissolves. As written, a reader cannot tell which. *Suggested remedy:* report the eligible population size and the response rate; report the full frequency distribution of the use item across all five categories, plus its interquartile range; state the observed standard deviation of the composite; and if any institutional benchmark on year level or discipline is available, compare respondents to it.

5. **Common-method variance is unaddressed, and one collected covariate is never used.** Both variables were self-reported by the same respondent in the same instrument at the same sitting, which inflates observed association through shared method; the manuscript names the self-report-versus-logs gap (§2, §6) but never the shared-method gap. *Why this matters:* combined with W1, the reported point estimate is bracketed by two unquantified biases running in **opposite** directions — attenuation from outcome unreliability and coarse categorization pushing r down, common-method variance pushing it up — so the manuscript's single number is less informative than its precision suggests, and the two should be discussed together rather than either alone. Separately, §3.1 records that the sample "spanned all four year levels," §2 endorses Ibarra and Poll's (2021) argument that context shapes both perception and use, and yet no analysis anywhere adjusts for or stratifies by year level. This is not selective reporting — §3.4 never promised such an analysis — but it is an available, zero-cost analysis left on the table. *Suggested remedy:* add one paragraph to §6 naming common-method variance as a distinct threat with its expected direction; and report the association by year level (or with year level partialled out) as a supplementary analysis, clearly labeled exploratory, with the year-level distribution given in §3.1.

### Detailed Comments

#### Research Questions & Hypotheses

The research question in §1 is single, explicit, and answerable by the design ("is perceived usefulness of the LMS associated with self-reported frequency of use?"). No directional hypothesis is stated, which is consistent with the descriptive-correlational framing and removes any ambiguity about whether the test was one- or two-tailed — §3.4 states two-tailed. The narrowness of the question is a legitimate design choice, and I do not treat it as a deficiency.

#### Research Design

The design is named as cross-sectional survey in the title, Abstract, and §3.1, and its principal inferential limit is stated in four places. The internal-versus-external-validity trade-off is acknowledged rather than concealed. What the design cannot support is any temporal or causal ordering, and the manuscript does not attempt it — §5 explicitly names the reverse pathway as equally consistent with the data. My concerns are not with design choice but with measurement and with what remains unreported.

#### Sampling Strategy

The eligibility frame and recruitment channel are stated; the achieved sample is 214. Two things are missing. First, the denominator: without the eligible population size, 214 has no interpretable relation to any population, and no response rate can be computed. Second, the sample is a volunteer, non-probability sample, and the manuscript never labels it as such — §6's fourth limitation describes voluntary response but does not name the sampling design. n = 214 is adequate for the single association actually estimated, as §3.4 establishes; the deficiency is in characterization, not in size.

#### Data Collection

Administration mode (online, via the course-announcement channel), field window (three weeks), incentive structure (none), and recall window ("in a typical week") are all stated — a better procedural record than most short survey reports. The gap is instrumental rather than procedural: the item pool is not reproduced. On data handling, 14 incomplete cases (6.0%) and 5 duplicates (2.1%) were removed; listwise deletion is implied but not named, and no comparison of removed to retained cases is reported. The deduplication rule also needs to be stated explicitly: §3.3 reports that no identifying information was collected and that responses could not be linked to individuals, and it is not clear from the text how duplicate submissions were identified under those conditions. Whatever the rule was, reproducibility requires it in writing.

#### Analysis Methods

The estimator choice is the substantive issue (W2). Assumption reporting is otherwise better than typical — linearity, monotonicity, bivariate outliers, and distributional symmetry are all addressed by inspection in §3.4 — but inspection of a five-category variable's symmetry is weak evidence for the normal-theory interval actually reported, and the interval's method is unstated. Effect size is not a separate omission here, since the coefficient *is* the effect size; however, r² is characterized only verbally ("the proportion of variance shared by the two measures was accordingly modest") and never given numerically. It is .18; state it.

#### Results Presentation

Results are complete relative to the analysis plan, with no evidence of selective reporting. Presentation is thin in three specific ways: no table or figure appears anywhere, so the scatterplot referenced in §3.4 is asserted but not shown; the primary outcome's distribution across its five categories is never reported, only its median; and the year-level composition of the sample, though collected, is never tabulated. For a quantitative paper reporting one association, a single descriptive table (composite mean, *SD*, observed range; use item frequency by category; year-level *n*) would close all three at negligible length cost.

#### Reproducibility

Currently not reproducible in the strict sense. The six items and the exact use-item wording are absent; the adaptation is undocumented; the deduplication rule is unstated; there is no data, materials, code, or supplementary-availability statement of any kind. What *is* reproducible is the arithmetic: the interval and test statistic follow from the reported coefficient and *n*, which I verified. Ethics review and consent are documented (§3.3). Adding an appendix with the instrument and a one-line availability statement would move this section from inadequate to adequate without altering any analysis.

#### Methodological Fallacies Detected

Screening against the standard list: **reverse causation** — raised as a risk by the design, but explicitly and correctly disclaimed in §2, §5, §6, and §7, so not committed. **Selective reporting / confirmation bias** — not detected; the analysis plan and the results correspond exactly. **P-hacking / uncorrected multiple comparisons** — not applicable; one test. **Ecological fallacy, Simpson's paradox, overfitting, multicollinearity** — not applicable to a single bivariate estimate at the individual level, though the absence of any subgroup analysis means a Simpson-type year-level reversal cannot be ruled out either way. **Survivorship / selection bias** — present as a risk through voluntary response and recruitment inside the system under study; §6 names volunteer bias generically but does not connect it to restriction of range on the outcome. The two genuine measurement-side fallacy risks — unacknowledged attenuation from outcome unreliability and coarse categorization, and unacknowledged common-method inflation — are the substance of W1 and W5.

### Questions for Authors

1. What reliability evidence exists for the single-item use measure? If none is available, will you state the attenuation constraint and report a disattenuation sensitivity range under explicitly assumed reliability values?
2. Given §3.2's declaration that the use item is ordinal, what is the justification for foregrounding Pearson over the rank-based or polyserial estimate, and how do you reconcile that choice with the median reported for the same variable in §4?
3. How was the 95% CI in §4 computed, and what distributional assumption does that method make about a five-category variable? Would you add a bootstrap interval alongside it?
4. What was the size of the eligible undergraduate population, and what was the response rate? Can you report the full frequency distribution of the use item across its five categories and the observed *SD* of the composite?
5. Exactly what did "adapted" change relative to Costa and Wren's (2019) items, and can the six items and the verbatim use item be published in an appendix? Absent this, on what basis can α = .88 be compared to the source instrument's reliability?
6. By what rule were the 5 duplicate entries identified, given that §3.3 reports no identifying information was collected and no linkage to individuals was possible?
7. Year level was collected but never analyzed. Can you report the association by year level (or with year level partialled out) as a labeled supplementary analysis, and give the year-level distribution of the sample?
8. Will you add common-method variance to §6 as a threat distinct from the self-report-versus-logs concern, and state its expected direction relative to the attenuation discussed in question 1?

### Minor Issues

- Statistical formatting deviations, none of which create ambiguity but which recur: `n = 214` for a total analyzed sample where APA 7.0 uses `N`; the mean reported as "3.6 (SD = 0.8)" without `M =` notation and to one decimal rather than two; degrees of freedom omitted from the correlation, where `r(212) = .42` is the APA form; "alpha = .05" and "r >= .19" rendered as words and ASCII rather than as α and ≥; ρ reported in §4 without an interval or *p* value.
- The sensitivity statement in §3.4 sits exactly on its own boundary. At n = 214 and r = .19, two-tailed α = .05, power reconstructs to ≈ .798 using the 1/√(n − 3) variance and ≈ .802 using 1/√(n − 1) — so "greater than .80" depends on an unnamed convention or software default. Naming the software and its settings, or restating the floor as r ≥ .20, removes the issue.
- r² is described verbally but never reported numerically (it is .18). One figure would strengthen §4's otherwise sensible discussion of unexplained variation.
- No table or figure appears in the manuscript, and no data, materials, code, or supplementary-availability statement is present.

---

contract_role: methodology

## Dimension Scores

### D1: methodology_rigor
score: warn

No committed block trigger fires. Participant acquisition *is* described (eligibility frame, channel, field window, full disposition), so trigger (a) does not fire; the instrument is cited to a source and described at the level of item count, scale, and composite, so (b) does not fire; the reported statistics are internally consistent and I reconstructed both the interval and the implied test statistic, so (c) does not fire; the single-item outcome's limitation *is* acknowledged in §6, so the conjunctive trigger (d) does not fire; ethics approval and consent are reported, so (e) does not fire. Multiple committed warn triggers do fire: reliability reported with in-sample validity evidence entirely absent and validation transferred from an undocumented source form; procedure described too thinly for replication because the six items and the verbatim use item are absent and the adaptation is undocumented; no data or instrument availability statement; and, on the sampling-frame sub-item of my Phase 1 signal list, the population denominator and response rate are unreported so restriction of range on the outcome cannot be assessed. Missing-data quantity is reported but the handling method is only implied and the deduplication rule is unstated.

### D2: domain_accuracy
score: warn

Restricted, per my Phase 1 commitment, to methodological and psychometric terminology and to internal consistency between reported numbers and described procedures. No block trigger fires: the α is not itself offered as validity evidence (the validity warrant is the source citation), no statistical procedure is described as doing something it cannot do, and no two reported figures contradict each other — the coefficient, interval, *p*, and *n* reconcile, and ρ ≈ r as expected. Committed warn triggers fire on drifting terminology that does not invalidate the conclusion: an adapted instrument with unreported modifications called "previously validated," so validation evidence is transferred rather than established; the outcome's measurement level treated as ordinal in §3.2, parametric in §3.4–§4, and ordinal again in §4's median; §4's claim that r/ρ agreement shows the association "did not depend on the parametric assumption," which overstates what a rank check on the same five tied categories can establish about either categorization attenuation or the interval's normality assumption; and the Abstract's "LMS engagement" naming a broader construct than the access-frequency item operationalizes in §3.2.

### D3: argumentative_coherence
score: warn

Assessed strictly through the evidence-to-claim link. No block trigger fires, and the manuscript performs well against the two structurally predictable hazards for this design: causal language is disclaimed in the Abstract, §1, §5, §6, and §7; reverse causation is named explicitly in §5; third-variable explanations (course requirements, assessment schedules, instructor context) are named in §4 and §5; the practice implication in §5 is hedged three times and attributed to a practitioner source rather than to these data, so it does not amount to an interventionist recommendation; and every analysis named in §3.4 appears in §4, so there is no selective-reporting signal. One committed warn trigger fires squarely: common-method variance is unaddressed, despite both variables being self-reported in one instrument at one sitting. Its unstated direction is opposite to the equally unstated attenuation from outcome unreliability, so the manuscript's central quantitative claim rests on a point estimate bracketed by two unacknowledged biases pushing in opposite directions.

### D4: cross_disciplinary_relevance
score: warn

Assessed only as methodological transparency, which is my legitimate purchase on this dimension. No block trigger fires: the manuscript states transfer boundaries repeatedly and at length (§1, §2, §5, §6, §7), so there is no unbounded generalization claim. Two committed warn triggers fire. First, the predictor construct has no operational definition available to a reader outside this instrument tradition — the six items are not reproduced, so an adjacent-field reader must retrieve and trust a cited source to know what "perceived usefulness" was measured as; the outcome item is better served, with its anchors given. Second, the setting is described too thinly to locate the transfer boundary: the LMS platform is never named, the disciplinary composition of the sample is never given, and no information is provided on whether LMS use was course-mandated at this institution — the last of which bears directly on how the association should be read anywhere else.

### D5: writing_and_structure
score: warn

Assessed only within the methodological reporting surface, and at the deliberately high block bar I committed to: no block trigger fires, because §3.1–§3.4 separate design and participants, measures, procedure and ethics, and analysis cleanly, and the procedure can be reconstructed in outline from the text. Two committed warn triggers fire. Recurring APA 7.0 statistical-formatting deviations: `n` for a total sample, no `M =` notation, one-decimal mean and *SD*, omitted degrees of freedom on the correlation, α and ≥ rendered as words and ASCII, and ρ reported without an interval or *p*. And word-count compression that omits standard reporting elements rather than condensing them: no table or figure anywhere, so the scatterplot inspection asserted in §3.4 is not shown; the primary outcome's category distribution is never reported; the year-level composition collected per §3.1 is never tabulated; and there is no availability statement. This is a reporting-completeness finding, not a complaint about prose, which is clear throughout.

## Failure Condition Checks

### F1
fired: false

Predicate: any mandatory dimension scores `block`. My mandatory dimensions are D1, D2, and D3; all three score `warn`. No committed block trigger fired on any of them.

### F2
fired: true

Predicate: two or more mandatory dimensions score `warn` or worse. D1, D2, and D3 all score `warn` — three of three mandatory dimensions. The panel-level `majority` quantifier attached to this condition is synthesizer machinery and I do not apply it; I evaluate the predicate against my own scores only.

### F3
fired: false

Predicate: any high-priority dimension scores `block`. D4 is the sole high-priority dimension and scores `warn`, not `block`; its committed block trigger (a central generalization claim unsupported by sampling with no boundary statement anywhere) did not fire, because boundary statements are present in five sections.

### F0
fired: false

Predicate: every mandatory dimension scores `pass`. None of D1, D2, or D3 scores `pass`.

## Review Body

The manuscript is small, honest, and better reported than most single-association survey papers — and those three facts are exactly why the revision must target what its own candour leaves untouched. Its statistical reporting is verifiable: r = .42 with a 95% interval of [.30, .52] at n = 214 reproduces under Fisher-*z* with the 1/√(n − 3) variance, the implied *t* ≈ 6.7 on 212 *df* is consistent with *p* < .001, and the a priori sensitivity statement in §3.4 is used in the correct direction rather than as post hoc justification. Assumption inspection is reported, a rank-based robustness check is reported, the analysis plan and the results correspond exactly, and ethics approval, consent, and case disposition are all documented. None of this is boilerplate praise; it is the reason the paper's remaining problems are worth stating precisely rather than in bulk.

The load-bearing weakness is that the paper's central number is an attenuated estimate of unknown magnitude and the manuscript does not say so. §6 treats the single-item self-report measure as a validity problem — divergence from behavioural logs — which is correct as far as it goes and is properly cited. It is not the same as the reliability problem. An observed correlation is bounded by the geometric mean of the two reliabilities; with the predictor at α = .88, essentially the entire constraint sits on an outcome whose reliability is unknown and unestimable from a single administration of a single item. Purely illustratively, at assumed outcome reliabilities of .70 and .50 the disattenuated coefficient would be ≈ .54 and ≈ .63. The word "moderate," which appears in the Abstract, §4, §5, and §7 and constitutes the paper's only substantive interpretive claim, is therefore unstable in a direction never discussed. Coarse categorization compounds this: Pearson and Spearman on five heavily tied categories both attenuate relative to a polyserial estimate, so §4's agreement between r and ρ bounds sensitivity to rank-versus-integer scoring and nothing more — it does not, as §4 states, show that the association is independent of the parametric assumption, since the interval's normality assumption cannot hold for a five-category variable and its derivation is never named.

Running the other way is common-method variance, which the manuscript also never names: both variables came from the same respondent, the same instrument, and the same sitting, which inflates the observed association. Taken together, the point estimate is bracketed by two unquantified biases in opposite directions, and the honest revision states both rather than either. Alongside that sit three concrete reporting gaps that are cheap to close and currently block independent evaluation. The six scale items and the verbatim use item are not reproduced and the adaptation is undocumented, so α = .88 is not comparable to the source instrument's, "previously validated" does not transfer to the administered form, and no independent group can replicate the measurement. The eligible-population denominator, the response rate, and the outcome's distribution across its five categories are all unreported, so restriction of range — plausible when recruitment runs through an announcement channel inside the system under study — cannot be assessed in either direction. And year level was collected, is endorsed as theoretically relevant via Ibarra and Poll (2021) in §2, and is never used, which leaves an available zero-cost analysis on the table.

The recommendation is major revision rather than rejection, and the distinction matters. Nothing identified here impugns the design choice, the conduct of the study, or the authors' care; the reported analysis is internally sound and the causal discipline is exemplary. What is required is measurement candour the manuscript has not yet extended to its own coefficient, an estimator ordering that honours the measurement level the authors themselves declare, and roughly a page of additional reporting — instrument, denominator, outcome distribution, one descriptive table, one availability statement. All of it is achievable within the existing data, with the single exception of an outcome reliability estimate, which requires either a small test–retest sub-sample or an explicit statement of the attenuation constraint in its place.

## Editorial Decision

Fired conditions from my own dimension scores: F2 only (severity 70). F1 (severity 90) and F3 (severity 60) did not fire; F0 (severity 10) did not fire. By the contract's severity precedence, the highest-severity fired condition is F2, whose action governs.

editorial_decision=major_revision

---

## SEAT — Peer Reviewer 2 (Domain)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor.** As Peer Reviewer 2 I read this dimension through a domain lens rather than a technical-design lens: my concern is whether the study's design and reporting meet what educational-technology research on LMS adoption actually expects of a cross-sectional survey. Reviewer 1 owns the internal statistical machinery; what I own is whether the methodological choices are recognisable and defensible *as this field practises them* — whether the instrument descends from an identifiable measurement tradition, whether the sampling and administration are reported at the level this literature routinely reports them, and whether the self-report design is handled with the caution the field's own methodological commentary demands. Where I assert that the field expects something, I must ground that expectation in a checkable external source (a journal or venue policy, a reporting guideline, a peer-reviewed methodological reference, or documented community practice) rather than in my own sense of best practice; if I cannot ground it, I down-rate the finding to advisory and label it `[FIELD-NORM UNVERIFIED]`.

**D2 — domain_accuracy.** This is my primary dimension. It asks whether the manuscript's claims sit correctly inside the current evidence base of technology adoption in higher education, whether prior work is represented as its authors actually argued it, and whether field terminology and reported results are factually right. For a paper on perceived usefulness and self-reported LMS use, this bears directly on the constructs at issue: "perceived usefulness" is a technical term with a specific origin and operational definition, "self-reported use" is not "use", and "adoption", "engagement", "acceptance", and "usage intention" are distinct constructs in this literature that are frequently and consequentially conflated. Domain accuracy also covers attribution — whether the theoretical lineage is credited to its original sources rather than to secondhand reviews, and whether the paper acknowledges the substantial body of work that has already interrogated the very relationship it examines.

**D3 — argumentative_coherence.** I read this as domain-argument accuracy rather than as generic logic-checking: does the chain running from the stated research problem through the framework, the constructs, the evidence, and the conclusions hold together when a subject expert inspects each link? The specific risk in this literature is a slide from a cross-sectional association between two self-reported measures to language about influence, driving, determination, or effect, and a second slide from a correlational finding to prescriptive recommendations for institutional practice. Coherence here also means that the claimed research gap actually motivates the study performed, that the theoretical framework named in the front matter is the one used to interpret the results in the back matter, and that the conclusions do not quietly exceed what the design licenses.

**D4 — cross_disciplinary_relevance.** Reviewer 3 owns cross-disciplinary impact proper; my contribution is narrower and domain-anchored. I assess whether the paper's framing, definitions, and implications are legible to adjacent-field readers — instructional designers, information-systems researchers, higher-education administrators, learning-analytics scholars — without either mystifying them with unexplained in-field shorthand or, in the other direction, making unsubstantiated claims about what the findings mean for those adjacent fields. Since this construct family originates in information systems and migrated into education, I also watch for whether borrowed constructs are used with fidelity to their source discipline or have drifted in transit without acknowledgement.

**D5 — writing_and_structure.** The lowest-priority dimension and the one furthest from my seat, but it carries domain content nonetheless: whether the manuscript is organised the way empirical work in this field is organised, whether the exposition of constructs and findings is clear enough that a domain reader can tell what was measured and what was found, and whether tables and figures report the quantities this literature expects to see reported. At 1,597 words this manuscript is short for a full empirical report, so my structural concern is less about polish than about whether the compression has removed content a domain reader needs in order to evaluate the claims. Structural thinness alone is a presentation matter; structural thinness that makes domain claims unassessable escalates into D2 territory and I will score it where it belongs.

## Scoring Plan

### D1: methodology_rigor

- `what_to_look_for`: Whether the survey instrument is identified and traced to a measurement tradition (adapted from a published scale vs. author-constructed) and whether item wording or a full item list is available; whether reliability and, if claimed, validity evidence is reported for each construct; whether sampling is described concretely enough to know who was surveyed, how they were recruited, how many were invited, and what proportion responded; whether the administration context is stated (voluntary/incentivised, in-class/online, institutional pressure); whether the single-source self-report design is acknowledged as a methodological condition of the study rather than passed over; whether any objective LMS log data was available and, if so, why self-report was preferred; whether ethics approval and consent are documented at the level this field's journals require; whether the cross-sectional design is named as such. For every one of these where my criticism depends on a claim about what educational-technology or survey research *should* do, I will look for a groundable source before assigning severity.
- `what_triggers_block`: The manuscript makes empirical claims whose evidentiary basis cannot be located at all from what is reported — no identifiable instrument and no item information, or no sample description sufficient to know what population the numbers describe, or reported results that cannot be tied to any stated procedure — such that a domain reader cannot determine what was actually done. Also blocking: a design-level claim contradicted by the reported procedure (e.g. describing the study as longitudinal or experimental while reporting a single-wave survey), or reported measurement properties that are internally impossible for the described instrument.
- `what_triggers_warn`: Method is recognisable but under-reported against the field's own routine reporting practice — reliability omitted or reported for only some constructs, response rate absent, recruitment described only in general terms, item wording unavailable, ethics/consent unstated, or the self-report/common-method condition unacknowledged — where each omission I penalise is one I can ground in an external source. Also warning: a groundable reporting expectation is met only nominally (a reliability coefficient with no indication of what it was computed on). Where I judge a gap real but cannot ground the norm, the finding is reported advisory with `[FIELD-NORM UNVERIFIED]` and does not by itself drive this dimension below `pass`.

### D2: domain_accuracy

- `what_to_look_for`: Whether "perceived usefulness" is defined in a way consistent with its established meaning in the technology-acceptance literature and attributed to its original source rather than to a secondhand review; whether "self-reported use" is kept distinct from actual use throughout, including in the abstract, results, and conclusions; whether "adoption", "acceptance", "engagement", "usage intention", and "actual use" are used as the distinct constructs this literature treats them as, or slide into one another; whether the theoretical framework's core claims — including which construct is proposed to mediate or predict which — are stated as their originators stated them; whether the literature review covers the foundational sources of the framework, the substantial meta-analytic and review work on technology acceptance in education, the specific LMS-adoption strand, and developments from roughly the last three to five years; whether it engages the well-documented critical strand rather than presenting the framework as uncontested; whether any factual statements about LMS platforms, institutional practice, policy context, or prior study findings are accurate; whether prior studies are characterised in a way their authors would recognise, including studies whose findings run counter to the paper's.
- `what_triggers_block`: A construct is defined or operationalised in a way that contradicts its accepted meaning in the field, and that misdefinition propagates into the paper's conclusions; or a major theoretical claim is attributed to the wrong source or misstated in a way that changes what it asserts; or prior findings are reported as saying something other than what they say; or "self-reported use" is presented as evidence about actual system use in the paper's own claims; or the literature base omits the foundational source of the framework the paper itself uses, or omits the directly-on-point body of prior LMS-acceptance work such that the paper's claim of novelty or gap rests on a literature that is not there. Fabricated or unverifiable citations, if identifiable from the reference list's internal consistency, block here.
- `what_triggers_warn`: Definitions are broadly correct but imprecise or drift between sections; the framework is cited through reviews rather than originals where originals are standard; terminology is used loosely in places without the looseness reaching the conclusions; coverage is thin in one identifiable respect — recent work under-represented, the critical/opposing strand absent, literature concentrated in one region or school without acknowledgement, or the gap statement asserted rather than demonstrated against what has been cited; the review enumerates studies without critical synthesis; individual factual statements about platforms or context are imprecise but not consequential. Any missing-reference recommendation I make will be either specifically attestable or explicitly tagged `[UNVERIFIED]` and phrased as a search lead.

### D3: argumentative_coherence

- `what_to_look_for`: Whether the causal language in the title, abstract, results, and discussion is consistent with each other and with a cross-sectional correlational design; whether any statement of influence, effect, driving, leading to, determining, or improving appears where only association is supported; whether the stated research gap is the gap the study actually fills; whether the framework introduced early is the framework used to interpret findings late, or is named and then abandoned; whether the discussion's claims are traceable to reported results rather than introduced fresh; whether practical or institutional recommendations follow from the strength of evidence actually obtained; whether alternative explanations for the observed association — common-method variance, reverse or reciprocal relation between usefulness perception and use, third variables such as course requirement or instructor mandate — are considered; whether limitations are substantive or perfunctory; whether the conclusion restates what the study found or expands on it.
- `what_triggers_block`: The paper's central conclusion is not licensed by its own design or reported evidence — causal or directional claims asserted from cross-sectional correlational data as the paper's headline finding, or a conclusion that contradicts the results section, or recommendations for institutional practice presented as warranted by evidence that cannot warrant them. Also blocking: the framework named as the study's basis makes a claim the paper's own interpretation reverses without acknowledgement, or the stated gap and the study performed are about different things such that the paper does not answer the question it poses.
- `what_triggers_warn`: Causal language appears in some locations but is correctly hedged elsewhere, indicating slippage rather than a systematic claim; the discussion over-reaches modestly beyond the results; the framework is applied superficially — invoked for justification but not used to interpret specific findings or fed back into at the end; alternative explanations are unaddressed or acknowledged only in a limitations list without bearing on the interpretation; the research gap is asserted rather than argued; limitations are boilerplate. At 1,597 words some argumentative compression is expected, so I will distinguish an argument that is brief from an argument that is broken, and will not penalise brevity as incoherence.

### D4: cross_disciplinary_relevance

- `what_to_look_for`: Whether constructs imported from information systems are defined on first use for an education readership rather than assumed; whether the paper states clearly enough what kind of system an LMS is, and in what institutional context, for a reader outside higher-education technology to interpret the findings; whether implications drawn for adjacent audiences — instructional design, learning analytics, institutional policy, information systems — are supported by the study's own evidence or asserted; whether the paper acknowledges the disciplinary origin of its framework and any adaptation made in transferring it to an educational setting; whether findings are positioned as specific to the studied institution and platform or presented as general facts about students and LMSs; whether the single-institution, single-platform, undergraduate scope is stated and its transferability discussed.
- `what_triggers_block`: A cross-disciplinary claim is made that the study cannot support and that misrepresents the adjacent field — asserting an established finding of information systems, learning analytics, or instructional design that is not established, or presenting the study's results as generalisable evidence about LMS use across institutions, platforms, or student populations when the design supports no such reach. Also blocking: core constructs are used with a meaning that would mislead a reader from the source discipline, with no acknowledgement of the shift.
- `what_triggers_warn`: In-field shorthand goes undefined in ways that would slow but not mislead an adjacent-field reader; the institutional and platform context is thin enough that a reader must guess at scope; implications for adjacent audiences are gestured at rather than substantiated; the framework's disciplinary provenance and any adaptation are unremarked; contextual specificity and transferability are not discussed. Consistent with the field-norm rule, I will not treat "should have included international or cross-institutional comparison" as a deficiency — a single-site study's value is depth, and I require only that scope be stated and transferability discussed, not that breadth be added. D4 is high-priority but not mandatory, and I will not inflate a legibility problem into a substantive one.

### D5: writing_and_structure

- `what_to_look_for`: Whether the manuscript follows the sectional organisation empirical work in this field uses, and whether each section contains what its heading promises; whether constructs are named consistently across abstract, methods, results, and discussion; whether the abstract's reported findings match the body's; whether tables and figures report the quantities this literature expects for survey work (descriptives, the association statistics, sample sizes per analysis) and whether captions state what is shown well enough to be read independently; whether the relationship between text and tables is complementary rather than redundant; whether citation and reference formatting is internally consistent; whether, at 1,597 words, the compression has removed content a domain reader needs — most plausibly the instrument, the sample description, or the engagement with prior work — rather than merely trimming prose.
- `what_triggers_block`: Organisation or exposition is disordered enough that a domain reader cannot determine what was measured or what was found — results reported without identifying which construct or which analysis they belong to, an abstract that reports findings the body does not contain, tables that cannot be reconciled with the text, or a structure that omits an element (method, results) entirely. This is a low-priority dimension and I hold the block bar correspondingly high: presentation must defeat comprehension, not merely inconvenience it. Where thin structure specifically prevents assessment of domain claims, I will score the substantive consequence in D2 rather than double-count it here.
- `what_triggers_warn`: Section content and headings are misaligned in places; terminology varies across sections without meaning to; tables or figures are under-captioned, redundant with the text, or omit a quantity the field routinely reports; reference formatting is inconsistent; the manuscript's brevity has visibly squeezed a section that needed more (typically methods or literature) without the omission rising to unassessability. Where I criticise a reporting-format expectation as a field norm, the same grounding rule applies: sourced, or advisory and labelled `[FIELD-NORM UNVERIFIED]`.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Domain Review Report (Peer Reviewer 2)

### Reviewer Identity

Senior higher-education researcher specializing in student engagement with institutional digital environments; author of published critiques of technology-acceptance-model over-application in education and co-author of a systematic review of LMS engagement predictors. Familiar with the primary TAM/UTAUT lineage and with the learning-analytics literature comparing self-reported and log-derived engagement. Reviewing as Peer Reviewer 2 against a realistic Q3 target tier, not a Q1 bar.

### Overall Recommendation

**Major Revision**

### Confidence Score

4

### Summary Assessment

This is a disciplined, honestly written short report whose epistemic conduct is better than most single-association manuscripts I review. Causal language is controlled, the reverse pathway is named, self-report is treated as an indicator of perceived rather than actual use, and the limitations are specific rather than ritual. None of that is in question, and none of it should be re-litigated.

What is in question is domain substance. The manuscript invokes "research on technology acceptance" and attributes the canonical definition of perceived usefulness to two recent secondary sources, citing no primary source for the construct and no meta-analytic or systematic-review benchmark anywhere in its six references. That matters more here than it would in a model-testing paper, because the paper's *entire stated value proposition* is comparability — "an incremental data point, comparable with prior work," "one point in a distribution" (§2). A poolable estimate requires a described comparator distribution, a documented instrument, and a described population; the manuscript supplies none of the three. Separately, the measured quantity — weekly access frequency — is relabelled "use" and then "engagement," including in the Abstract's final sentence, without the substitution ever being defended.

These are revision-tractable defects. No new data collection is required.

### Strengths (3-5 items)

1. **Causal discipline is real, not cosmetic**: The manuscript hedges directionality in §1, §2, §5, §6, and §7, and — unusually — cites a source *against* its own inference (Delgado, 2020, on the reverse pathway). Many papers in this literature assert influence from exactly this design; this one does not. I do not raise causality as a weakness because the manuscript has already handled it.
2. **Self-report is treated as a measurement condition, not glossed over**: §2 and §6 both engage Vasquez (2020) on the divergence between self-report and behavioral logs, and §3.2 explicitly declares the use item an *ordinal indicator of self-reported use*. That is the correct domain framing and it is stated before the results, not retro-fitted into a limitations list.
3. **Scope is declared rather than smuggled**: §1's "deliberately narrow question" and §7's "incremental, design-bounded contribution" are accurate self-descriptions. A single-site correlational estimate is a legitimate contribution genre in this field; the manuscript does not pretend otherwise, and I do not penalise its narrowness.
4. **Third-variable awareness is present in the Results**: §4's acknowledgement that reported use "reflects many influences beyond perceived usefulness, including course requirements and assessment schedules" is domain-correct and is the right reading of a moderate coefficient.

### Weaknesses (3-5 items)

1. **W1 — The construct's primary literature is absent, and its canonical definition is attributed to secondary sources.** §2 states that "research on technology acceptance has long proposed that perceived usefulness — the degree to which a person believes a technology will help them perform better — is among the factors associated with adoption and continued use," citing Costa & Wren (2019) and Delgado (2020). That definition is the technology acceptance model's, originating with Davis (1989); the reference list contains no primary TAM source, no UTAUT source, and no meta-analytic or systematic-review anchor. *Why it is a problem*: a claim about what a research tradition "has long proposed" is being carried by two papers published in 2019–2020, one of them (per §3.2) an instrument-development study. The paper is at once positioning itself inside a literature and declining to cite that literature's foundations. *Direction of improvement*: cite the construct's origin directly for the definition; retain Costa & Wren (2019) as the instrument source, which is what it actually is. *Norm grounding*: the severity here does not rest on my own sense of best practice. It rests on (a) the manuscript's own APA 7 conformance — APA 7th edition §8.6 directs authors to cite the original work and reserve secondary citation for cases where the original is unavailable — and (b) the manuscript's own §2 commitment to being "comparable with prior work," an internal standard the current reference base cannot meet.
2. **W2 — "Access frequency" becomes "use" and then "engagement," and the substitution is never defended.** The measured quantity is a single item asking "how often the respondent accessed the LMS in a typical week" (§3.2). It is reported as "self-reported LMS use" (§4, §5, §7), and as "engagement" in four places: the Abstract's opening ("students' engagement with them varies widely"), the Abstract's closing ("perceived usefulness tracks with LMS engagement among undergraduates"), §4 ("reported engagement reflects many influences"), and §5 ("one of several factors bearing on engagement"). *Why it is a problem*: in this literature engagement is a defined multidimensional construct spanning behavioral, emotional, and cognitive components, not a synonym for access count. A student who opens the LMS six times a day to check announcements is maximally "using" it and may be minimally engaged with it. The relabelling is not a stylistic variant; it widens the claim, and it does so most in the Abstract, the sentence with the widest circulation. Note the asymmetry: the manuscript is careful about *self-report vs. actual use* and careless about *frequency vs. engagement* — the hedging on the first has drawn attention away from the second. *Direction of improvement*: use one label throughout — "self-reported weekly access frequency" — and either drop "engagement" or state explicitly that access frequency is being used as a thin proxy for a broader construct and that this is a limitation. *Norm grounding*: the engagement construct's multidimensional definition is established in Fredricks, Blumenfeld & Paris (2004), *Review of Educational Research*, 74(1), 59–109; this is a definitional fact in the field, not an unsourced expectation of mine.
3. **W3 — "Previously validated instrument" is claimed for an instrument the paper says it adapted, with the adaptation undocumented.** The Abstract and §2 describe the measure as "previously validated"; §3.2 describes it as "adapted from Costa and Wren (2019)" and reports no adaptation log, no item wording, and no item count comparison to the source. *Why it is a problem*: validity is a property of score interpretations for a specified use, not a transferable property of an instrument; adaptation breaks the transfer unless re-validation evidence is supplied. Reporting α = .88 does not repair this, since without the adaptation record it cannot be compared to the source instrument's coefficient — and §3.2 characterises the source's reliability only as "strong internal consistency," giving no value to compare against. *Direction of improvement*: reproduce the six items in an appendix, state exactly what was changed and why, and either present re-validation evidence or downgrade the claim from "previously validated" to "adapted from a validated instrument, revalidation not undertaken." *Norm grounding*: AERA, APA & NCME, *Standards for Educational and Psychological Testing* (2014), Chapter 1 — validity attaches to interpretations of scores for proposed uses, and modifications require supporting evidence for the modified use.
4. **W4 — The stated contribution (a poolable data point) is asserted but not delivered.** §2's contribution claim has three premises, and the manuscript defeats all three. (a) *Instrument comparability* — undercut by the undocumented adaptation (W3). (b) *Outcome comparability* — the manuscript never states how any prior study operationalised use, so there is no basis on which r = .42 can be declared commensurable with anything; §2 says "effect sizes vary across samples and instruments" without reporting a single one, and §5's "consistent with prior technology-acceptance research" therefore names an agreement the reader cannot check. (c) *Population description* — the sample is characterised only as "214 undergraduates at one mid-sized public university spanning all four year levels": no disciplinary mix, no named LMS platform, no institutional LMS-maturity context, and no denominator or response rate for the sampling frame. *Why it is a problem*: this is not a generic "the study is small" complaint — it is the paper's own value proposition failing on its own terms. Song (2018) is invoked to establish that estimates vary by institution, which is precisely why an unlocated estimate cannot be placed in that distribution. *Direction of improvement*: report the range of prior coefficients with their outcome operationalisations, name the platform and institutional context, describe the sample's disciplinary composition, and state what population the 214 are drawn from. *Grounding*: internal to the manuscript's §2 claim; no external field norm is asserted here. (The sampling-frame audit proper — denominator, non-response bias, recruitment channel — sits with the institutional-research seat; I raise it only as it bears on poolability.)
5. **W5 — Two quantities the manuscript itself invokes are described rather than reported.** §4 states "the proportion of variance shared by the two measures was accordingly modest" without giving the value, and reports only a median category for the use item with no category frequencies or dispersion. *Why it is a problem*: a reader cannot reconstruct the distribution of the outcome variable, which is exactly what a future synthesis would need. *Direction of improvement*: report the shared-variance figure numerically and give the frequency distribution across the five categories. *Norm grounding*: APA Journal Article Reporting Standards for quantitative research (Appelbaum et al., 2018, *American Psychologist*, 73(1), 3–25) require complete descriptive reporting and numerically stated effect sizes. This is a low-priority presentation finding and does not affect my decision.

### Detailed Comments

#### Literature Review

- **Coverage**: Six references, none primary to the framework invoked, none meta-analytic, none systematic-review. The specific LMS-acceptance strand — which is large — is represented by two studies (Ibarra & Poll, 2021; Song, 2018). The critical strand is present in a useful but narrow form: Delgado (2020) on cross-sectional inference and Vasquez (2020) on self-report validity are genuine methodological cautions, engaged in good faith. What is absent is the substantive critical literature on TAM over-application in education, which is directly relevant to a paper that frames itself inside that tradition while declining to test it.
- **Integration quality**: Better than enumeration. §2's second paragraph organises its sources by the caution each supplies and then states how the study responds — that is real synthesis, and it is the strongest paragraph in the manuscript. The weakness is that every synthesised source is a caution; no source supplies a positive benchmark.
- **Research gap argument**: Not argued. The manuscript's warrant is "prior estimates vary by institution, therefore another estimate is useful" (§2, via Song, 2018). That is a coherent premise, but the conclusion requires knowing what the distribution looks like and where this estimate lands in it. Neither is provided, so the gap statement is asserted rather than demonstrated.

#### Theoretical Framework

- **Appropriateness**: Technology acceptance is the right framing for this question, and the decision not to test a full acceptance model (§1) is a legitimate and honestly declared scope choice. I do not ask the authors to write a larger, model-testing paper.
- **Application depth**: Superficial by design, and the design disclaimer is accepted — but there is a tension the manuscript does not resolve. It declines to engage the framework analytically while claiming its result is "consistent with" (§5, Abstract) and "comparable with" (§2) that framework's evidence base. Those are comparative claims, and comparative claims require the comparison to be shown. The framework is invoked for warrant at the front and never fed back into at the end; §7 restates the finding without saying what it implies for, or draws from, the acceptance literature.
- **Alternative frameworks**: Not required. A single-association descriptive report does not need a competing framework, and I would treat "you should have used UTAUT instead" as scope expansion rather than a defect. What is required is accurate attribution of the framework actually invoked.

#### Academic Argument Quality

- **Factual accuracy**: No incorrect factual statement about LMS platforms, institutional practice, or policy context was identified. Prior studies are characterised in terms their authors would plausibly recognise; the cautions attributed to Delgado (2020), Ibarra & Poll (2021), Vasquez (2020), and Song (2018) are used consistently across §2, §5, and §6 without drift. Two imprecisions: the source instrument's reliability is given only qualitatively ("strong internal consistency," §3.2), and "effect sizes vary across samples and instruments" (§2) reports no effect sizes.
- **Argument logic**: The causal chain is sound and appropriately bounded. The comparability chain is not: §2 → §5 → Abstract carries a claim of consistency with prior work whose evidentiary basis is never laid out. §5's practice implication is hedged twice and attributed to Whitfield (2019) rather than to the present data, which is the correct handling of a correlational finding.
- **Terminology precision**: This is where the manuscript's otherwise-disciplined language fails. See W2. The chain runs *access frequency* (§3.2) → *use* (§4, §5, §7) → *engagement* (Abstract, §2, §4, §5). Note also §2's description of prior work as reporting associations with "engagement," which imports the same imprecision into the characterisation of the cited literature — those studies' outcome constructs are never stated, so the reader cannot tell whether the label is theirs or the authors'.

#### Contribution to the Field

- **Incremental contribution**: The contribution genre is right and legitimate for a Q3 outlet: a transparently reported, design-bounded correlational estimate. As written, the estimate is not yet usable by the audience the manuscript names — a future synthesis cannot pool an estimate whose instrument modifications, comparator operationalisations, platform, and population are undescribed. The fix is reporting, not more data.
- **Positioning**: §2 positions the paper as one point in the Song (2018) distribution without stating that distribution's shape. Positioning by analogy rather than by placement.
- **Overclaiming**: Absent on causality — genuinely absent, not merely hedged. Present on construct breadth (W2) and on comparability (W4). The manuscript's risk profile is the inverse of the usual: it under-claims where readers expect over-claiming and over-claims in a place its own hedging discipline never reached.

#### Missing Key References

Metadata below is offered from my own attestation, not from session materials. Authors should verify volume and page details against the record before citing.

- **Davis, F. D. (1989). Perceived usefulness, perceived ease of use, and user acceptance of information technology. *MIS Quarterly*, 13(3), 319–340.** — The primary source for the construct the manuscript defines in §2 and measures throughout. Currently the definition is attributed to a 2019 instrument paper. This is the single most consequential addition.
- **Venkatesh, V., Morris, M. G., Davis, G. B., & Davis, F. D. (2003). User acceptance of information technology: Toward a unified view. *MIS Quarterly*, 27(3), 425–478.** — The consolidation of the acceptance tradition the manuscript invokes; relevant even though the study does not test a model, because §2's characterisation of "research on technology acceptance" needs a locatable referent.
- **Fredricks, J. A., Blumenfeld, P. C., & Paris, A. H. (2004). School engagement: Potential of the concept, state of the evidence. *Review of Educational Research*, 74(1), 59–109.** — Needed if the authors retain the word "engagement" anywhere; it establishes the multidimensional definition their single-item access measure does not capture. If they drop the word, this reference becomes optional.
- **A meta-analytic or systematic-review anchor for TAM in education.** Attestable candidates: **Scherer, R., Siddiq, F., & Tondeur, J. (2019)**, *Computers & Education* (meta-analytic SEM of TAM; note the sample is teachers, so the benchmark is adjacent rather than exact); **Granić, A., & Marangunić, N. (2019)**, *British Journal of Educational Technology* (systematic review of TAM in educational contexts); **Šumak, B., Heričko, M., & Pušnik, M. (2011)**, *Computers in Human Behavior* (meta-analysis of e-learning acceptance). Any one of these gives the reader a distribution against which r = .42 can be read as typical, high, or low — which is exactly what §2 promises and does not deliver.
- **AERA, APA, & NCME (2014). *Standards for Educational and Psychological Testing*.** — Supports the revision to the "previously validated" claim (W3); cite in the Methods if the adaptation is retained.
- **[UNVERIFIED — search lead]** Learning-analytics work comparing self-reported LMS use against trace/log-derived measures, beyond the single source (Vasquez, 2020) currently cited. Search on "self-report versus trace data," "LMS log data and self-reported engagement." I can attest that this body of work exists; I cannot attest specific author/year/venue combinations, so this is a lead rather than a recommendation.

### Questions for Authors

1. What exactly was changed in adapting the Costa and Wren (2019) six-item scale — item wording, item count, response anchors, referent object? Without this, the reported α = .88 cannot be read against the source instrument, and the "previously validated" claim in the Abstract and §2 has no anchor.
2. The Abstract's final sentence says perceived usefulness "tracks with LMS engagement." The measured variable is weekly access frequency. Is the substitution intended as a claim, and if so what is the argument that access frequency indexes engagement? If it is not intended as a claim, the sentence should be rewritten.
3. §5 states the finding is "consistent with prior technology-acceptance research." Consistent with which reported coefficients, from which studies, measured how? Naming the range would convert §2's poolability claim from an assertion into a demonstration.
4. What platform is the LMS, and what is the institution's LMS maturity and mandated-use context? A campus where the LMS carries all assessment submission and a campus where it hosts optional slides produce differently interpretable access-frequency distributions, and neither the estimate nor its transferability can be read without knowing which this is.
5. Year level was collected (§3.1) and never used. Given that §2 cites Ibarra and Poll (2021) approvingly on the contextual shaping of both perception and use, and given that §5's onboarding implication is aimed at newly-arrived students, why was the association not examined by year level? This analysis is available in the data already held.

### Minor Issues

- §3.2 reports the source instrument's reliability only as "strong internal consistency." Give the coefficient.
- §4 reports a median category for the use item but no category frequencies or dispersion; §4's "proportion of variance shared" is described in words but never given as a number.
- The Abstract reports r and p but omits the confidence interval the body reports; if space allows, carrying the interval into the Abstract would match the manuscript's own reporting standard.
- **Reference provenance flag (recorded, not adjudicated):** all six references carry DOIs in the `10.5555/` range with sequential `205000N` suffixes. I record this for the deterministic citation-verification layer and take no position on whether the works exist. My literature-base findings (W1, W4) hold on the assumption that the six works are exactly as described, and none of my dimension scores rest on this flag.
- **Integrity check:** the manuscript contains no imperative or instruction addressed to reviewers, and no attempt at instruction injection. Nothing to report in that class.

---

contract_role: domain

## Dimension Scores

### D1: methodology_rigor
score: warn

Applying my Phase 1 D1 triggers from a domain lens. The block trigger did not fire: the instrument is identified by descent (adapted from Costa & Wren, 2019), the design is correctly named as cross-sectional and matches the reported procedure, ethics approval and informed consent are documented (§3.3), reliability is reported for the multi-item measure, and the self-report condition is acknowledged as a methodological condition rather than passed over (§2, §6). A domain reader can determine what was done in outline. The warn trigger fired on three grounded grounds: the adaptation to the source instrument is undocumented while the manuscript claims "previously validated" status (grounded in AERA/APA/NCME *Standards*, 2014, Ch. 1 — validity attaches to score interpretations for a proposed use, not to an instrument across modifications); the six scale items and the exact use-item wording are reproduced nowhere, so neither reproduction nor comparison to the source is possible; and the population is described without a denominator, so what the estimate describes is indeterminate — I ground this on the manuscript's own §2 poolability commitment rather than on an external reporting norm, since the sampling-frame audit belongs to another seat.

### D2: domain_accuracy
score: block

Two of my committed Phase 1 D2 block triggers fired independently. First: "the literature base omits the foundational source of the framework the paper itself uses ... such that the paper's claim of novelty or gap rests on a literature that is not there." §2 attributes the canonical definition of perceived usefulness to Costa & Wren (2019) and Delgado (2020); no primary acceptance-model source appears in the six references, and no meta-analytic or systematic-review benchmark appears anywhere. The manuscript's own claim to be "comparable with prior work" and to supply "one point in a distribution" therefore rests on a literature base that contains no distribution. Second: "a construct is defined or operationalised in a way that contradicts its accepted meaning in the field, and that misdefinition propagates into the paper's conclusions." The measured quantity is weekly access frequency (§3.2); it is relabelled "engagement" in the Abstract's opening and closing sentences and in §2, §4, and §5, with no point at which the substitution is defended. Engagement has an established multidimensional definition in this field (Fredricks, Blumenfeld & Paris, 2004), and access frequency does not satisfy it. The propagation reaches the Abstract, which is the manuscript's most-read claim surface. I note explicitly that this score does not rest on the `10.5555/` DOI provenance flag, which I record without adjudicating.

### D3: argumentative_coherence
score: warn

My D3 block triggers did not fire and I want that on the record: the central conclusion is licensed by the design, causal language is controlled across every section, the discussion does not contradict the results, the practice recommendation is doubly hedged and attributed to a cited source rather than to the present data, and the stated gap and the study performed are about the same thing. Two warn triggers fired. The framework is applied superficially — invoked for warrant in §1–§2 and never fed back into in §7 — which is a declared scope choice, but it sits in unresolved tension with the comparative claims in §2 ("comparable with prior work") and §5 ("consistent with prior technology-acceptance research"): the manuscript cannot simultaneously decline to engage the acceptance literature analytically and assert agreement with its evidence base without displaying that evidence base. And the research gap is asserted rather than argued — §2's premise that estimates vary by institution establishes that another estimate could be useful, not that this one is placeable, since the distribution's shape is never reported. Consistent with my Phase 1 commitment, I distinguish an argument that is brief from an argument that is broken; this one is brief in most places and unsupported in one specific place.

### D4: cross_disciplinary_relevance
score: warn

Priority is high, not mandatory, and I hold to my Phase 1 commitment not to inflate a legibility problem into a substantive one. The block trigger did not fire: no claim is made about information systems, learning analytics, or instructional design that those fields would not recognise, and the findings are consistently presented as bounded to the studied sample rather than as general facts. Scope is stated and transferability discussed (§6, §7). Three warn triggers fired. The framework's disciplinary provenance is unremarked — perceived usefulness is an information-systems construct imported into education, and the manuscript neither says so nor notes any adaptation made in transit; this follows from the same attribution gap scored in D2. The institutional and platform context is thin enough that an adjacent-field reader must guess at scope: the LMS is never named, institutional LMS maturity and mandated-use context are never described, and the disciplinary composition of the sample is absent — I ground the need for this on the manuscript's own poolability claim rather than on an external expectation, and I tag the broader assertion that this field routinely names the platform as `[FIELD-NORM UNVERIFIED]`, resting no severity on it. And the one implication offered to an adjacent audience (§5, institutional onboarding) is supported by a citation rather than by the study's own evidence. The construct itself is defined in plain language on first use, which is a genuine legibility strength and why this is warn rather than worse.

### D5: writing_and_structure
score: warn

Lowest priority, and the block bar is correspondingly high — it was not approached. Organisation is conventional and complete, every section contains what its heading promises, the Abstract's reported coefficient matches the body, and prose is clear enough that a domain reader can tell what was measured and what was found. Warn fires narrowly on reporting completeness: the shared-variance quantity is described in words but never given numerically, and the ordinal use item is summarised by a median category alone with no frequency distribution or dispersion, so the outcome variable's distribution cannot be reconstructed (grounded in APA Journal Article Reporting Standards for quantitative research, Appelbaum et al., 2018, which require complete descriptives and numerically stated effect sizes). The manuscript's terminology drift across sections also manifests structurally, but per my Phase 1 commitment I score its substantive consequence in D2 and do not double-count it here. This dimension does not bear on any failure condition and does not affect my decision.

## Failure Condition Checks

### F1
fired: true

Expression: any mandatory dimension scores 'block'. Evaluated against my own dimension scores only. D2 (domain_accuracy, mandatory) scores block. Condition satisfied. Severity 90.

### F2
fired: true

Expression: two or more mandatory dimensions score 'warn' or worse. Evaluated against my own dimension scores only. D1 = warn, D2 = block, D3 = warn — three mandatory dimensions at warn or worse. Condition satisfied. Severity 70. The `cross_reviewer_quantifier` on this entry is panel-level machinery for the synthesizer and I have not applied it.

### F3
fired: false

Expression: any high-priority dimension scores 'block'. The sole high-priority dimension, D4 (cross_disciplinary_relevance), scores warn, not block. Condition not satisfied.

### F0
fired: false

Expression: every mandatory dimension scores 'pass'. D1 = warn, D2 = block, D3 = warn. Condition not satisfied.

## Review Body

The manuscript's domain problem is not the one its own hedging anticipates. Having disciplined itself thoroughly on causal inference, self-report validity, single-site generalizability, and effect-size modesty — all of which are conceded accurately and none of which I raise — it leaves two adjacent claims entirely unguarded, and both are load-bearing.

The first is attribution. §2 opens by characterising what "research on technology acceptance has long proposed," supplies the canonical definition of perceived usefulness, and cites a 2019 instrument-development paper and a 2020 methodological commentary for both. No primary source for the construct appears in the six references; no meta-analytic or systematic-review benchmark appears anywhere. This would be a correctable citation lapse in most papers. It is disqualifying as written in this one, because the manuscript's entire declared value proposition is comparability: it offers itself as "an incremental data point, comparable with prior work," as "one point in a distribution" whose spread Song (2018) is invoked to establish. A point can only be placed in a distribution that has been drawn. §2 says effect sizes "vary across samples and instruments" and reports none; §5 says the result is "consistent with prior technology-acceptance research" and names no coefficient it is consistent with. The comparability claim is therefore made three times and demonstrated zero times, and the reader has no material with which to judge whether r = .42 is high, low, or unremarkable for this construct pair in this setting.

Three further conditions of poolability fail alongside it. The instrument was adapted with no record of what changed, so α = .88 cannot be set against the source instrument's reliability — which §3.2 itself reports only qualitatively — and the "previously validated" description in the Abstract and §2 outruns what an undocumented adaptation supports. Prior studies' outcome operationalisations are never described, so commensurability with them is unassessable in principle. And the population is characterised only as 214 undergraduates at one mid-sized public university across four year levels: no platform, no institutional LMS-maturity context, no disciplinary mix, no denominator. Each of these is a reporting fix rather than a design fix, which is why my recommendation is revision rather than rejection.

The second unguarded claim is the construct label. The manuscript measures how often a student accessed the LMS in a typical week (§3.2), reports it as "self-reported use," and then, at four points including both the first and last sentences of the Abstract, calls it "engagement." Engagement in higher-education research denotes a multidimensional behavioral-emotional-cognitive construct; weekly access count indexes at most a fragment of its behavioral component. A student who opens the platform repeatedly to check announcements registers as a maximal user and may be a minimal engager. Nowhere is the substitution flagged, argued, or limited. The asymmetry is instructive: the same authors who declined four separate times to say "influences" when they meant "is associated with" did not notice that they were saying "engagement" when they had measured access. The Abstract's closing sentence — the sentence most likely to be read, quoted, and indexed — carries the widest version of the claim. The remedy is small: one label, used consistently, with an explicit statement if access frequency is to stand as a thin proxy for anything broader.

What I do not ask for is a different paper. The narrow scope declared in §1 is a legitimate design choice; a full acceptance-model test, a second site, or a log-validation study would all improve the evidence and none is required to make this manuscript sound. The one analysis I do press for is already available in the collected data: year level was recorded in §3.1, the manuscript cites Ibarra and Poll (2021) approvingly on contextual shaping in §2, and §5's onboarding implication is aimed squarely at newly-arrived students — yet the association is never examined by year level. That is not scope expansion; it is the use of data already held to answer the question the Discussion itself raises.

The epistemic conduct of this manuscript is above the median for its genre and should be told so plainly. It is blocked on domain accuracy, and it is blocked on defects that a careful revision round can fully close.

## Editorial Decision

Derived mechanically from the contract's `failure_conditions` precedence applied to my own dimension scores: F1 (severity 90) and F2 (severity 70) both fired; highest severity wins; F1 governs.

editorial_decision=reject_or_major_revision

Within that action's range, my seat's recommendation is **Major Revision**. The D2 block rests on a missing literature base and an undefended construct substitution — both correctable in text without new data collection — not on a design defect or an unrecoverable claim.

---

## SEAT — Peer Reviewer 3 (Perspective)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** The contract asks whether the study's design, data handling, statistical reporting, and reproducibility affordances clear the field's peer-review bar. From my seat, I do not audit statistical validity itself — that belongs to Reviewer 1. What I read this dimension as asking of me is whether the chosen design is *fit for the question the paper claims to answer* when viewed from outside the paper's own paradigm. For a cross-sectional survey of self-reported LMS use, the outside-in question is whether a one-shot self-report instrument can bear the interpretive weight the study will place on it, and whether an adjacent discipline (measurement psychology, HCI telemetry work, implementation science) would regard the design as adequate to its stated purpose or as a proxy that quietly substitutes for the construct of interest.

**D2 — domain_accuracy (mandatory).** The contract asks that claims align with current domain evidence, that prior work is represented correctly, and that domain terminology and results carry no factual errors. My angle is not a systematic coverage audit — that is Reviewer 2's. Mine is the accuracy of *borrowed* constructs: educational-technology adoption research imports its central vocabulary from information systems (TAM's perceived usefulness), from behavioural science (intention versus behaviour), and from measurement theory (self-report validity). A paper can be internally faithful to the LMS literature and still misstate what the borrowed construct means in the discipline that produced it. I read D2 as licensing me to flag terminology whose home-discipline meaning has drifted in transit.

**D3 — argumentative_coherence (mandatory).** The contract asks whether the core thesis holds together internally and whether evidence supports the claims. I do not run fallacy detection or internal-consistency checks — those are the Devil's Advocate's. What I contribute here is the assumption layer beneath the argument: the explicit, implicit, and paradigmatic premises that make the argument feel coherent from inside the discipline while being contestable from outside it. In adoption research the standard implicit premises are that perceived usefulness precedes use rather than rationalising it, that self-reported use approximates actual use, and that more LMS use is a good in itself. An argument can be formally valid and still rest on premises an adjacent field would not grant.

**D4 — cross_disciplinary_relevance (high priority).** This is my home dimension. The contract asks whether framing, definitions, and implications are accessible to adjacent-field readers, and whether interdisciplinary claims are substantiated. Two distinct obligations sit here. The accessibility obligation: can a reader from measurement, HCI, or higher-education policy follow what was measured and what it means without importing unstated ed-tech conventions? The substantiation obligation: where the paper reaches into another discipline — invoking a psychological model, a behavioural mechanism, an equity or policy implication — is that reach backed, or is it decoration? Note this dimension is `high`, not `mandatory`: under the contract a `block` here fires F3 (major revision) rather than F1, so the severity ladder differs from D1–D3 and I must score it on its own terms rather than importing mandatory-tier strictness.

**D5 — writing_and_structure (normal priority).** The contract asks about organisation, clarity of exposition, figure and table quality, and adherence to venue conventions. My reading of this from the perspective seat is comprehension across disciplinary boundaries rather than style policing: whether an outside reader can reconstruct what was done and what follows from it. At 1,597 words the manuscript is short for an empirical survey report, so the live structural risk is not verbosity but compression — a Methods section too thin to be interpretable, or a Discussion that has no room to separate what was found from what is inferred. This dimension is `normal` priority and appears in no failure condition, so it cannot by itself drive any editorial decision; I will score it honestly and let its weight fall where the contract puts it.

## Scoring Plan

### D1: methodology_rigor

- **what_to_look_for** — Whether the paper states what "use" actually denotes and how it was captured (self-report frequency estimate, Likert agreement, recalled hours) and whether it acknowledges that this is a proxy rather than behaviour; whether the sampling frame and recruitment route are described well enough for an outsider to judge who is represented and who is structurally absent (non-users, disengaged students, those who dropped the course); whether the cross-sectional, single-timepoint design is matched to the strength of the language used about the usefulness–use relationship; whether reproducibility affordances exist at all (instrument items or source, response rate, institutional and temporal setting); whether common-method concerns are named, given that predictor and outcome plausibly come from the same instrument and the same respondent at the same moment.
- **what_triggers_block** — The paper's own conclusions require a design property the study does not have, and the gap is not acknowledged anywhere: causal or temporal-ordering claims (usefulness "drives", "leads to", "increases" use) resting on single-timepoint self-report; **or** the outcome variable is never operationally defined, so no reader in any discipline can tell what was measured; **or** the sampling frame is undescribed *and* the paper generalises to undergraduates broadly, making the inferential target unrecoverable.
- **what_triggers_warn** — The design is adequately reported and the claims are appropriately hedged, but a material affordance is missing or a known limitation is named without being carried through: the self-report proxy is acknowledged in Limitations yet the Discussion still reasons as though behaviour were measured; **or** response rate, instrument provenance, or institutional context is absent such that replication would require guesswork; **or** the survivorship problem (surveying enrolled, reachable students about a platform they must use) goes unmentioned.

### D2: domain_accuracy

- **what_to_look_for** — Whether "perceived usefulness" is used with the meaning it carries in its source model (a belief about job/task performance improvement) or has silently become general satisfaction, liking, or ease of use; whether "use", "engagement", "adoption", and "acceptance" are held distinct or used interchangeably as if synonymous; whether mandatory-context adoption is distinguished from voluntary adoption, since the institutional-LMS setting typically makes use compulsory and this materially changes what the imported model predicts; whether attributed prior findings are characterised at the right strength (a correlation reported as an effect, a single-site study reported as established); whether any psychometric or behavioural-science term is invoked in a sense its home field would not recognise.
- **what_triggers_block** — A load-bearing construct is factually misdescribed in a way that changes what the study can claim: the central model or its constructs are attributed to the wrong theoretical lineage or defined contrary to their established meaning; **or** the paper asserts as settled domain fact something the cited discipline actively contests, and the study's interpretation depends on that assertion; **or** prior results are reported with a directionality or magnitude the source does not support.
- **what_triggers_warn** — Terminology drifts without a factual error that changes the conclusion: "usefulness", "satisfaction", and "engagement" blur across sections; **or** the voluntary/mandatory adoption distinction is never raised even though the setting is an institutional platform; **or** prior work is represented at a slightly inflated strength (hedge dropped, scope widened) in ways a revision could correct without changing the findings.

### D3: argumentative_coherence

- **what_to_look_for** — Whether the paper states its premises or leaves them to be inferred; whether the direction of the usefulness–use relationship is argued or assumed, given that the reverse path (students who already use the system rationalise it as useful) is equally consistent with cross-sectional data; whether "more use is better" is treated as self-evident rather than defended, and whether any account of learning outcomes connects use to something worth having; whether the positivist framing — that a measurable attitude maps onto measurable behaviour — is at least visible to the authors as a choice; whether alternative explanations for the observed pattern (course design requiring the LMS, instructor mandate, assessment deadlines, workload) are entertained before the attitudinal explanation is adopted.
- **what_triggers_block** — The central conclusion depends on an assumption that is never stated and that a competing reading would deny, with no alternative interpretation acknowledged anywhere in the manuscript: for example, the paper recommends action premised on usefulness causing use while the data cannot distinguish that from the reverse or from a common institutional cause, and this is presented without qualification; **or** the stated conclusion is not the conclusion the presented evidence supports, such that the argument only holds if the reader supplies the missing premise.
- **what_triggers_warn** — The argument is coherent and its conclusion is hedged, but the assumption layer is thin: reverse causation or a third-variable account is plausible and unmentioned; **or** "increased LMS use" is assumed beneficial without any link to a learning or experience outcome; **or** at least one implicit premise (self-report ≈ behaviour, attitude ≈ predictor of action) carries real weight and is never surfaced.

### D4: cross_disciplinary_relevance

- **what_to_look_for** — Whether an adjacent-field reader can reconstruct what was measured from the paper's own definitions without importing unstated ed-tech convention; whether the sample's context is specified enough to judge transferability (institution type, discipline mix, country, delivery mode, pandemic-era or post-pandemic timing), since LMS-engagement patterns are strongly context-bound; whether stakeholders beyond the student respondent appear — instructors who design the courses that generate LMS activity, support staff, platform administrators — or whether the student is treated as the sole locus of adoption; whether implications reaching into other domains (equity, digital access, institutional policy, procurement) are substantiated or asserted; whether the paper acknowledges that students differ in device access, connectivity, and digital literacy, which makes "use" unevenly available rather than purely attitudinal; whether limits of generalisation are stated in terms an outsider can act on.
- **what_triggers_block** — The paper makes an interdisciplinary or policy claim with no support and material consequence: an institutional, procurement, or pedagogical recommendation is issued as though established when the cross-sectional survey cannot ground it; **or** findings from a single narrow context are asserted to hold generally with no scope condition stated at all; **or** a claim is imported from another discipline (psychological mechanism, equity effect, behavioural principle) and used as a load-bearing premise with no substantiation whatsoever.
- **what_triggers_warn** — The framing is defensible but insular: key terms are used in a house sense that an adjacent-field reader would have to guess at; **or** context descriptors needed for transferability are missing or partial; **or** stakeholders other than the surveyed students are entirely absent from the framing; **or** access and digital-literacy variation is unaddressed such that "perceived usefulness" is treated as the only meaningful determinant of use; **or** implications are stated at a level of generality that gives a practitioner nothing to act on.

### D5: writing_and_structure

- **what_to_look_for** — Whether the manuscript's 1,597 words are distributed so that Methods carries enough detail to be interpretable rather than being compressed to make room for framing; whether the boundary between results and interpretation is visible, so an outside reader can tell what was observed from what is inferred; whether tables or figures, if present, are self-contained and their captions state what the data show rather than what the authors conclude; whether the abstract's claims match the body's claims in strength; whether the reported organisation follows recognisable empirical conventions (question → method → result → interpretation → limitation) or leaves an outside reader hunting for basic facts.
- **what_triggers_block** — Exposition failure prevents evaluation: the paper is organised such that core information (what was asked, of whom, with what instrument, with what result) cannot be located or reconstructed at all; **or** presented figures/tables contradict the narrative text; **or** numeric results appear in the text with no basis for interpreting them. *(Noted for the record: D5 is `normal` priority and named in no `failure_conditions` entry, so a `block` here fires no condition and cannot alone move the editorial decision. I commit to scoring it on its own merits regardless.)*
- **what_triggers_warn** — The paper is followable but comprehension costs an outside reader effort: Methods is compressed below the threshold at which the study could be repeated; **or** results and interpretation are interleaved so that the evidentiary base must be disentangled; **or** the abstract overstates relative to the body; **or** venue conventions (structured sections, limitation statement, table numbering) are inconsistently observed.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Perspective Review Report (Peer Reviewer 3)

### Reviewer Identity

Director of institutional research and academic-technology assessment at a public university system. My background is survey methodology and institutional data governance rather than educational-technology theory: I design and field campus-wide student surveys, shepherd them through ethics and data-protection review, and advise provosts on whether a given piece of internal evidence is strong enough to justify spending on a platform or a programme. I am an outsider to the technology-acceptance literature, and where the paper's conventions are field-standard in ways I would not recognise, I have tried to say so rather than assume error.

### Overall Recommendation

Major Revision

### Confidence Score

4

### Summary Assessment

This is a disciplined, honestly-scoped manuscript, and I want to say that plainly before criticising it: the causal hedging is real rather than decorative, the limitations are operational rather than ritual, and an outside reader is not misled about what was found. My concerns are not that the paper overclaims — it does not — but that it is reported below the floor at which my own profession could use it, and that it locates the entire phenomenon inside the individual student.

Three things stand out from an institutional-research seat. First, the survey has no denominator: 233 received and 214 analysed, out of an eligible population never stated, with no response rate. Second, recruitment ran through the institution's course-announcement channel, which by the paper's own §1 description of what an LMS hosts is plausibly inside the platform under study — a structural selection problem distinct from the generic volunteer bias §6 concedes. Third, the paper treats LMS use as an attitude phenomenon, with no instructor, course designer, or platform administrator anywhere in the frame, and no acknowledgement that device access and connectivity make "use" unevenly available regardless of belief.

Each of these is addressable within the existing data and study design. None requires a different, larger paper. Recommendation: major revision.

### Strengths

1. **Scope discipline that survives translation across fields.** The hedging is not decoration. §5 states the reverse pathway, names the source of the caution, and marks the practical implication as "suggested by, not proven by." I read a great many campus reports that would not pass this test, and the manuscript's restraint means an adjacent-field reader is never misled about what the correlation licenses. This is the paper's most transferable virtue.

2. **The contribution *shape* is the right one for institutional evidence.** The Song (2018) framing — any single-site estimate is one point in a distribution — is exactly how my profession needs single-institution findings positioned. Comparable, transparently-bounded point estimates are genuinely scarce, and choosing to be one is a legitimate and useful ambition. My criticism below is not that this shape is wrong but that the paper does not yet supply what pooling would require.

3. **Ethics and consent are reported at all.** Committee approval, voluntariness, no incentive, consent on the landing page. A large share of campus student surveys are never written up with any of this, and its presence here reflects real practice rather than boilerplate. My concern in §3.3 (below) is about completeness of the data-handling account, not about whether the study was conducted properly.

4. **The Results paragraph resists its own headline.** §4 states explicitly that a substantial share of variation is unaccounted for and names course requirements and assessment schedules as other influences. That sentence does more honest work than most discussion sections, and it opens the door to the structural account I argue for below — the paper is closer to my position than it realises.

### Weaknesses

1. **The survey-reporting floor is not met: no denominator, no response rate, no deduplication rule.** §3.1 says all enrolled undergraduates were eligible but never states how many that is. Without the population N, 214 could be 15% of a small college or under 2% of a large one, and representativeness is simply unassessable — this is the first question any institutional-research audit asks, and as written the manuscript cannot answer it. Related and separable: §3.1 reports removing 5 duplicate entries while §3.3 states that no identifying information was collected and responses could not be linked to individuals. I am not alleging an ethics failure; I am saying the data-handling account is incomplete. Duplicates are identified somehow — IP address, session token, device fingerprint, or a stated response-pattern rule — and each of those carries a different implication for the anonymity claim. *Suggested fix, all within existing records:* report eligible population N and the response rate (AAPOR-style disposition if available), state the deduplication criterion in one sentence, and if a quasi-identifier was used, say so and reconcile it with §3.3 by distinguishing anonymity from de-identification. This is a paragraph of writing, not new data collection. I note that this item sits near the Devil's Advocate's internal-consistency remit; I raise it as a governance-and-reporting question because that is the lens under which a data-protection officer would raise it, and I flag the overlap for the synthesiser.

2. **Recruitment ran through the platform under study.** §3.1 distributed the survey via the institution's course-announcement channel; §1 tells us announcements are among the things an LMS hosts. If that channel is LMS-delivered — the authors must confirm this either way — then the sampling instrument is inside the subject matter, and the students least likely to see the invitation are exactly the low-frequency users who would anchor the low end of both variables. §6 concedes that "students who engage more with institutional channels may be overrepresented," but treats this as generic volunteer bias. It is more specific and more consequential than that: it is a plausible truncation of the very range the correlation is estimated over. I leave the magnitude and direction of any effect on the coefficient to the methodologist; my point is that the recruitment route needs naming as a design feature rather than a footnote. *Suggested fix:* state the channel's relationship to the LMS explicitly; if a second, LMS-independent route (institutional email, in-class recruitment, registrar mailing) was available or is available in a follow-up, say so; and if the frequency distribution of the use item shows a thin low tail, report it — that is diagnostic evidence the authors already hold.

3. **The student is the only stakeholder in the frame, which points the recommendation at the weakest available lever.** Nobody but the surveyed undergraduate appears anywhere in this paper. Instructors decide what is posted, what must be submitted through the platform, and how announcements flow; instructional designers shape course templates; administrators set defaults. In my experience the single largest driver of variance in campus LMS access data is not student attitude but instructor course-design practice — a student in four template-rich courses accesses the platform constantly, and the same student in four courses that use it as a file cabinet does not. The paper's §4 already gestures at this ("course requirements and assessment schedules") but never carries it into the framing or the implication. *Suggested reframe:* treat perceived usefulness as one term in a system that also includes course design and instructor practice, and note in §5 that the intervention with the larger expected effect may sit on the instructor side. Implementation-science work on how technologies get embedded through collective rather than individual work (normalisation process theory) offers a ready vocabulary for this; I say more under Cross-Disciplinary Connections.

4. **Access and digital-literacy variation are absent, which leaves the onboarding implication with an untested distributional assumption.** Use is treated throughout as a function of belief. But students differ in device ownership, home connectivity, commuting and work hours, and disability-related access needs, and those differences make LMS use unevenly *available* rather than merely unevenly *desired*. This matters directly for §5: an onboarding programme that works by improving perceived usefulness will, by construction, help students whose low use is attitudinal and do nothing for students whose low use is material. If the second group is a meaningful share of the low tail, the recommended intervention widens rather than narrows a gap. *Suggested fix:* add access and digital-literacy variation to §6 as a named boundary condition on the interpretation, and state in §5 that the onboarding implication assumes the barrier is perceptual — an assumption the present data cannot test. If any access-related item was collected, report it.

5. **"More use is better" is never surfaced, and the one breakdown that would make the implication actionable was collected and left unused.** The paper's only practical payload — onboarding may be worth institutional attention — presupposes that raising LMS access frequency is worth paying for. Nowhere is LMS use linked to a learning outcome, a grade, a satisfaction measure, or any student benefit. This is not a nitpick from my side of the table: it is the first question a budget committee asks, and I cannot answer it from this manuscript. It also has a live alternative reading the paper never considers — a student who opens the LMS several times daily may be responding to an environment with opaque deadlines and scattered materials, in which case high frequency is a symptom of poor design rather than successful engagement. Separately, §3.1 records that the sample spanned all four year levels, and year level is never used. First-year students are precisely the population any onboarding programme targets, and whether the association differs for them is the single most decision-relevant breakdown available. It requires no new data. *Suggested fix:* state the "use is desirable" premise explicitly and defend it or bound it; report the association by year level, or say why it was not examined.

### Detailed Comments

#### Assumption Audit

- **Explicit assumptions.** The paper states its correlational frame plainly (§1) and holds to it. It explicitly assumes the self-report item indicates *perceived* rather than actual use (§2) and declines to test an acceptance model. These explicit commitments withstand outside scrutiny; they are, in fact, the manuscript's strongest feature. One explicit assumption is under-defended: §1's framing that institutions invest "on the assumption that availability translates into use" is reported as an institutional belief but never interrogated, and the paper then proceeds to work inside it.

- **Implicit assumptions.** Three carry weight and none is surfaced. *(a)* That increased LMS use is a good in itself — load-bearing for the entire practical implication, discussed in W5 above. *(b)* That LMS use is meaningfully voluntary. At most institutions it is substantially compelled: assignments are submitted through it, grades appear in it, announcements are pushed through it. A construct built to explain *adoption* behaves differently when the behaviour is partly mandated, and the paper never raises voluntary-versus-mandated as a distinction, even though its own §4 names course requirements as an influence. This is not a matter of citing more literature; it is a matter of stating what kind of behaviour is being explained. *(c)* That use is determined by belief rather than constrained by circumstance — see W4.

- **Paradigmatic assumptions.** The study works inside an individual-attitudinal paradigm: the unit of analysis is the student, the explanatory variable is a mental state, the outcome is a personal behaviour. That is a coherent and conventional choice in this literature, and I do not ask the authors to abandon it. I do ask them to mark it as a choice. From an institutional-research paradigm the same phenomenon is a property of course design, workload distribution, and platform configuration, and the student-attitude variance is residual. Naming the paradigm in one or two sentences would cost the paper nothing and would tell an adjacent-field reader what is being held constant.

- **A construct question I raise from outside the field.** What was measured is self-reported *access frequency in a typical week*. §5 and §7 call this *use*, and the Abstract's closing sentence calls it *engagement*. In my professional vocabulary those three are not interchangeable: a student opening the platform six times daily to check whether an announcement has appeared is maximally frequent and minimally engaged. The paper is admirably careful about the self-report-versus-behaviour gap and silent about the frequency-versus-engagement gap. If "engagement" is standard usage in this field for what a frequency item captures, I defer — but then the Abstract should say so, because outside the field it reads as a widening of the claim between the Results and the summary. *Suggested fix:* use "self-reported access frequency" consistently, or defend the substitution once, explicitly.

#### Cross-Disciplinary Connections

- **Parallel research.** Survey methodology has a mature literature on nonresponse bias that speaks directly to W1 and W2, and its central finding is useful to the authors rather than merely critical: response rate alone is a poor predictor of bias, but bias is unassessable without a denominator and a described frame. Reporting the denominator does not require the response rate to be high; it requires it to be known.

- **Borrowing opportunities.** Two concepts would strengthen the paper at low cost. *Voluntariness of use* appears as an explicit moderator in the extended acceptance literature (UTAUT), which gives the authors a field-internal way to raise my implicit-assumption (b) without leaving their own paradigm. *Normalisation process theory* from implementation science shifts the unit of analysis from individual belief to the collective work of embedding a technology, which is the vocabulary the paper needs for W3 — it would let §5 name the instructor-side lever without abandoning the student-level design.

- **Methodological borrowing.** The obvious complement is LMS log data, which the paper already names as a future direction (§7). I would sharpen that: the highest-value next study is not a bigger survey but a small validation substudy linking the self-report item to platform logs for a consenting subsample, which would let the authors report how their single item behaves against traces and would make every future single-item estimate in this literature more interpretable. A second, cheaper complement: a short qualitative follow-up asking low-frequency respondents *why*, which would directly test whether the low tail is attitudinal or material (W4).

#### Practical Impact

- **Real-world application.** As written, I could not take this to a provost. The finding is credible and the reporting is honest, but without a denominator I cannot state whom it represents, and without an outcome link I cannot state what improving it buys. That is a solvable state, not a fatal one — items 1, 4, and 5 above are the difference between a paper I would read with interest and a paper I could cite in a funding memo.

- **Implementation feasibility.** §5's recommendation is hedged three times, and I want to be fair about that: the authors have not overclaimed. My concern is about how the sentence will travel. A triple-hedged sentence extracted into a budget proposal loses its hedges, and this is the one sentence in the paper an institutional reader will quote. The more robust move is to reframe the implication as a testable hypothesis rather than a suggestion — "whether onboarding that surfaces concrete usefulness changes use is a question a pre-post or quasi-experimental design could answer, and the present correlation does not" — which is both more honest and more useful, because it tells a practitioner what study to commission.

- **Stakeholders.** Instructors, instructional designers, LMS administrators, and student support staff are all absent (W3). So are students who dropped, disengaged, or never saw the invitation (W2). The paper's population of interest is students who use the LMS enough to be reached through it.

#### Broader Implications

- **Ethical dimensions.** The consent and approval account is present; the data-handling account is not complete (W1). I would add one governance point the manuscript does not address: for a study of platform use recruited through the platform, a reader may reasonably wonder whether any platform-side data informed sampling or deduplication. Stating plainly that it did not — if it did not — closes that question in a sentence.

- **Social impact.** The equity dimension in W4 is the one I would most want the authors to add, because it changes who the recommendation serves. Framing low LMS use as a perception problem to be fixed by onboarding implicitly attributes it to the student. Where the cause is a shared laptop, a data cap, or a night shift, that framing misallocates both the diagnosis and the remedy. One paragraph in §6 would fix this.

- **Future directions.** In descending order of value from my seat: a log-validation substudy on a consenting subsample; a year-level and access-stratified re-analysis of the existing data; a multi-site replication with a common instrument and a published denominator, which is what would actually make the Song (2018) pooling vision real.

### Cross-Disciplinary Reading Recommendations

- **AAPOR, *Standard Definitions: Final Dispositions of Case Codes and Outcome Rates for Surveys* (current edition).** The operative standard for reporting eligible population, dispositions, and response rate. Directly addresses W1; adopting even its minimal disclosure set would move this survey over the institutional-usability threshold.
- **Groves, R. M. (2006). Nonresponse rates and nonresponse bias in household surveys. *Public Opinion Quarterly*, 70(5).** Useful to the authors defensively as well as critically: it establishes that a modest response rate is not itself disqualifying, which is why reporting the denominator is safe as well as necessary.
- **Venkatesh, V., Morris, M. G., Davis, G. B., & Davis, F. D. (2003). User acceptance of information technology: Toward a unified view. *MIS Quarterly*, 27(3).** Cited here not for lineage — that is another reviewer's territory — but specifically because voluntariness of use enters as an explicit moderator, which gives the authors a field-internal handle on implicit assumption (b).
- **May, C., & Finch, T. (2009). Implementing, embedding, and integrating practices: An outline of normalization process theory. *Sociology*, 43(3).** The implementation-science frame that relocates adoption from individual belief to collective work. Relevant to W3 and to the paradigmatic assumption above.
- **Hargittai, E. (2002). Second-level digital divide: Differences in people's online skills. *First Monday*, 7(4).** The foundational statement that access is not binary and skill variation persists after connectivity. Grounds W4.
- **[UNVERIFIED] Learning-analytics work comparing self-reported engagement with trace/log-derived engagement in LMS contexts.** I can attest that this body of work exists and is directly relevant to the frequency-versus-engagement distinction, but I cannot attest specific author/year/venue metadata from session materials. Offered as a search lead — suggested terms: "self-report versus log data LMS engagement discrepancy," "trace data validity student engagement" — not as a citation.

### Questions for Authors

1. How many undergraduates were eligible, and what was the response rate? If dispositions were not tracked, please say so explicitly rather than omitting the denominator.
2. Is the "course-announcement channel" delivered inside the LMS being studied? If yes, how do you assess the consequence for who was reachable, and can you report the frequency distribution of the use item so readers can see the shape of the low tail?
3. By what criterion were the 5 duplicate entries identified, and how does that criterion sit with the §3.3 statement that no identifying information was collected?
4. You collected year level. What does the association look like for first-year students specifically — the population an onboarding programme would target?
5. What outcome would make increased LMS access frequency worth an institution's money? If the answer is outside this study's scope, would you be willing to state the premise explicitly in §5 rather than leaving it implied?
6. To what extent is LMS use at your institution compelled by course requirements rather than chosen? Would you consider naming voluntary-versus-mandated use as a boundary condition on how the perceived-usefulness construct should be read here?
7. Would you consider reporting the manuscript's measured quantity consistently as "self-reported access frequency," rather than "use" in §5 and "engagement" in the Abstract?

### Minor Issues

- **Context descriptors are too thin for transferability.** "One mid-sized public university" is nearly the whole context statement. Missing: country/system, discipline mix of respondents, delivery mode (in-person, hybrid, fully online), the LMS platform and how long it has been in place, the academic term and calendar year, and whether the survey window sat inside or outside an assessment period. For a study whose declared value is comparability with other single-site estimates, each of these is a matter of one clause, and their absence is what would stop me pooling this estimate with my own.
- **No table or figure.** A single descriptive table — the distribution of the five-point use item, perceived-usefulness distribution, respondent counts by year level — would let an outside reader see the shape of the data rather than only its summary, and would bear directly on the range question in W2.
- **The instrument is not reproducible.** The six perceived-usefulness items are not printed, the use item's exact wording is paraphrased rather than quoted, and the nature of the "adaptation" from the source instrument is unreported. An appendix would resolve all three.
- **Abstract-to-body strength.** The Abstract's "consistent with prior technology-acceptance research" positions the finding more confidently than the body's careful "one point in a distribution" framing warrants. Aligning the two would cost nothing.
- **Reference provenance flag, not adjudicated.** All six references carry DOIs in the `10.5555/` range with sequential suffixes. I record this for the deterministic citation-verification layer and take no position on it; my assessment above proceeds on the assumption that the cited works are as described, and would not change if verification resolves cleanly.
- **Integrity check, for the record.** I found no instruction-injection attempt in the manuscript — no text addressed to reviewers, no directives, no scoring appeals. Nothing to report in the integrity class.

---

contract_role: perspective

## Dimension Scores

### D1: methodology_rigor
score: warn

Two Phase 1 warn triggers fired, no block trigger fired. Trigger "response rate, instrument provenance, or institutional context is absent such that replication would require guesswork": the eligible-population denominator and response rate are absent (§3.1), the six-item instrument's adaptation is undocumented and its items unreproduced (§3.2), the deduplication criterion is unstated and stands in tension with the §3.3 anonymity account, and the institutional/temporal context is described only as "one mid-sized public university." Trigger "the survivorship problem goes unmentioned": recruitment through the institution's course-announcement channel — plausibly inside the LMS under study, per §1's description of what an LMS hosts — is a structural selection problem that §6 addresses only as generic volunteer bias. No block trigger fired: the outcome variable *is* operationally defined (§3.2), causal language is hedged throughout (§1, §2, §5, §6, §7), and the paper does not generalise beyond its sample (§6). Statistical-validity questions are Reviewer 1's and are excluded from this score.

### D2: domain_accuracy
score: warn

Two Phase 1 warn triggers fired, no block trigger fired. Trigger "terminology blurs across sections": the measured quantity is self-reported access frequency in a typical week (§3.2), reported as "use" in §5/§7 and as "engagement" in the Abstract's closing sentence and §2, with the substitution never defended. Trigger "the voluntary/mandatory adoption distinction is never raised even though the setting is an institutional platform": nowhere does the manuscript address that LMS use is substantially compelled at most institutions, though §4 names course requirements and assessment schedules as influences — a distinction that materially changes what an acceptance construct predicts. No block trigger fired: perceived usefulness is defined consistently with its established meaning (§2), no domain claim is asserted as settled against active contestation, and prior work is characterised with hedges intact. Literature-base coverage and citation lineage are Reviewer 2's and are excluded from this score.

### D3: argumentative_coherence
score: warn

One Phase 1 warn trigger fired, no block trigger fired. Trigger "'increased LMS use' is assumed beneficial without any link to a learning or experience outcome": §5's onboarding implication presupposes that raising access frequency is worth institutional resource, yet no learning outcome, grade, satisfaction measure, or student benefit appears anywhere in the manuscript, and the competing reading — that high access frequency may indicate a poorly-organised environment rather than successful engagement — is unconsidered. The premise is load-bearing for the paper's only practical claim and is never surfaced. No block trigger fired, and this is a genuine credit to the paper: reverse causation is explicitly acknowledged (§5, via Delgado 2020) and a third-variable account is named (§4), so the central conclusion does not depend on an unstated premise a competing reading would deny. Fallacy detection and internal-consistency verification are the Devil's Advocate's and are excluded from this score.

### D4: cross_disciplinary_relevance
score: warn

Four Phase 1 warn triggers fired, no block trigger fired. "Context descriptors needed for transferability are missing or partial": country, discipline mix, delivery mode, platform identity and tenure, term and calendar year are all absent. "Stakeholders other than the surveyed students are entirely absent": no instructor, instructional designer, administrator, or support-staff role appears in the framing, despite course design being a plausible primary driver of LMS access. "Access and digital-literacy variation is unaddressed such that perceived usefulness is treated as the only meaningful determinant of use": device access, connectivity, and work/commuting constraints are nowhere considered, leaving the §5 recommendation with an untested distributional assumption. "Implications are stated at a level of generality that gives a practitioner nothing to act on": §5 is one triple-hedged sentence, and year level was collected (§3.1) but never used, leaving the one decision-relevant breakdown unreported. No block trigger fired: §5's institutional implication is explicitly marked "suggested by, not proven by, the present correlation," so it is not issued as established; §6 states scope conditions rather than asserting generality; and the one cross-disciplinary borrowing (Whitfield 2019 on onboarding) is cited and hedged rather than asserted bare. Consistent with my Phase 1 commitment, I scored this dimension on its own `high`-priority terms and did not import mandatory-tier strictness — and I note that a block here would have fired only the severity-60 condition, below the condition already firing, so no scoring incentive ran the other way.

### D5: writing_and_structure
score: warn

Phase 1 warn triggers fired on two counts. "Methods is compressed below the threshold at which the study could be repeated": scale items unreproduced, use-item wording paraphrased, adaptation undocumented, denominator and deduplication rule absent, survey platform and dates unreported. "The abstract overstates relative to the body": "tracks with LMS engagement" and "consistent with prior technology-acceptance research" both sit above the body's more careful framing. Venue conventions are partially observed — structure is conventional and complete, but there is no table or figure of any kind, so the distribution of the use variable is invisible to the reader. No block trigger fired: the organisation is textbook-conventional, core information is locatable, no figure contradicts the text (there are none), and numeric results are reported with the apparatus needed to interpret them. As committed in Phase 1, I note for the record that D5 is `normal` priority and appears in no failure condition, so this score drives nothing; I scored it on its merits regardless.

## Failure Condition Checks

### F1
fired: false

Predicate: any mandatory dimension scores `block`. My mandatory dimensions are D1 `warn`, D2 `warn`, D3 `warn`. No mandatory dimension scores `block`, so the predicate is not satisfied.

### F2
fired: true

Predicate: two or more mandatory dimensions score `warn` or worse. Three of three mandatory dimensions score `warn` — D1 (survey-reporting floor: denominator, response rate, deduplication rule, instrument provenance; plus the unnamed recruitment-channel selection problem), D2 (access-frequency/use/engagement drift and the unraised voluntary-versus-mandated distinction), and D3 (the unsurfaced "more use is better" premise with no outcome link). The threshold of two is exceeded.

### F3
fired: false

Predicate: any high-priority dimension scores `block`. D4 is the only `high`-priority dimension and scores `warn`. None of my committed D4 block triggers fired — the §5 implication is explicitly marked as suggested rather than proven, §6 states scope conditions, and the one cross-disciplinary borrowing is cited and hedged. The predicate is not satisfied.

### F0
fired: false

Predicate: every mandatory dimension scores `pass`. D1, D2, and D3 all score `warn`. The predicate is not satisfied.

## Review Body

I reviewed this manuscript from an institutional-research and survey-governance seat, and my findings are structurally different in kind from those the methodological and domain seats will produce: I evaluated the survey as administrative evidence, asking not only whether the estimate is defensible but whether I could put it in front of a provost.

The manuscript's honesty is real and I have tried not to punish it. Causal hedging runs through §1, §2, §5, §6 and §7; the reverse pathway is named with its source; §4 volunteers that most variance is unexplained; §6's four limitations are specific rather than ritual. Those concessions are adequate and I have not re-litigated them. My concerns lie in the space the concessions do not reach.

The first is a reporting floor rather than a design flaw. The study has no denominator: eligibility is stated as all enrolled undergraduates, but that population is never counted and no response rate is given, which leaves representativeness unassessable in either direction. Alongside it, §3.1's removal of five duplicate entries and §3.3's statement that no identifying information was collected cannot both be complete without a stated deduplication mechanism, each candidate mechanism carrying a different implication for the anonymity claim. I raise this as a governance-and-reporting question rather than an ethics allegation, and I note the boundary overlap with the Devil's Advocate seat for the synthesiser to resolve.

The second is structural selection. The survey was distributed through the institution's course-announcement channel, and §1 tells us announcements are among the things an LMS hosts. If the recruitment channel sits inside the platform under study, then the students least likely to receive the invitation are the low-frequency users who would anchor the bottom of both distributions. §6 concedes volunteer bias generically; this is a sharper and more specific problem, and the authors should either confirm the channel's independence from the LMS or name the circularity. I leave the consequence for the coefficient to the methodologist and confine myself to the sampling claim.

The third is a framing question, and it is where my seat differs most. This paper locates LMS use entirely inside the individual student — belief in, behaviour out. Nobody else appears: not the instructors whose course-design choices generate most of the access variance I see in institutional data, not the designers, administrators, or support staff. Nor does the paper acknowledge that use is unevenly *available*: device access, connectivity, work and commuting constraints make low use a material condition for some students, not an attitudinal one. Both omissions converge on §5. An onboarding programme that works by improving perceived usefulness helps students whose barrier is perceptual and does nothing for students whose barrier is a shared laptop or a data cap — so the recommendation carries a distributional assumption the study never tests. And beneath the recommendation sits an unstated premise that more LMS access is worth paying for, with no outcome of any kind connecting frequency to student benefit anywhere in the manuscript. A budget committee asks that question first.

Two closing observations. Where the paper calls its measured quantity "engagement" (Abstract, §2) while measuring weekly access frequency (§3.2), I may be applying an outsider's vocabulary to a field convention, and I have flagged rather than asserted it. And the fixes I have proposed are almost all within reach of the existing data and a revision cycle — a denominator, a deduplication sentence, an instrument appendix, a year-level breakdown from a variable already collected, two paragraphs of reframing. Nothing here asks the authors to write a different, larger paper; the narrow scope is a legitimate choice and I have tried to respect it.

## Editorial Decision

Derived mechanically from the contract's failure conditions applied to my own dimension scores. F2 fired (three mandatory dimensions at `warn`); F1, F3, and F0 did not. F2 is the only fired condition, so precedence by severity resolves to it directly and no tie-break on ordinal position is needed.

editorial_decision=major_revision

---

## SEAT — Devil’s Advocate

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** The contract asks whether design, data handling, statistical reporting, and reproducibility affordances clear the field's peer-review bar. As Devil's Advocate I do not redesign the study or run a power analysis — that is R1's seat. My adversarial read of D1 is narrower and harsher: does the manuscript's *argument* survive contact with its own methodological description? A cross-sectional survey reporting perceived usefulness against self-reported use is, by construction, a single-source common-method design, and my job is to ask whether the paper's claims are written as if it were something stronger. I will treat missing instrument provenance, unreported response rate, or absent handling of self-report inflation as adversarially relevant only insofar as they carry weight the conclusions cannot bear. Where my severity would rest on "the field should report X," Dimension 9 binds me: educational-technology survey work has its own accepted-practice boundary (e.g., APA/JARS-Quant survey reporting, TAM-lineage instrument-adaptation conventions), and I must name that external boundary rather than import a reference class from experimental psychology or clinical trials.

**D2 — domain_accuracy (mandatory).** The contract asks whether claims align with current domain evidence and whether prior work is correctly represented. My adversarial version is cherry-picking and confirmation-bias detection, not coverage auditing — completeness of the literature is R2's seat. LMS-adoption research is a field with a large, mature, and notably *mixed* evidence base: the TAM lineage's perceived-usefulness→use path is heavily replicated, but the self-reported-versus-log-data divergence literature is an equally established counter-current. So the specific adversarial question is whether the manuscript's citation set is selected to support its expected direction while the disconfirming strand goes unmentioned or is mentioned only to be dismissed. Misrepresentation of a cited construct (treating perceived usefulness, satisfaction, and engagement as interchangeable; citing a model's original formulation for a claim it does not make) also falls here, because it is a factual error about the domain, not a stylistic one.

**D3 — argumentative_coherence (mandatory).** This is the seat's home dimension: internal consistency of the core thesis, evidence-to-claim fit, and fallacies that undermine the central argument. For a cross-sectional survey the canonical failure is the correlation-to-causation slide, and it typically appears not in the results but in the discussion and implications, where "associated with" becomes "drives," "leads to," or "institutions should therefore invest in." Reverse causation is live here and rarely acknowledged: students who already use the LMS heavily may rate it useful because they use it, not the converse. I will also test for hidden premises (that self-reported use is a proxy for actual use; that perceived usefulness is exogenous to the platform's mandatory status), for internal contradictions between a limitations paragraph that concedes non-causality and a conclusion that assumes it, and for the parsimony question — whether a simpler rival account (course-mandated LMS activity, instructor enforcement, single-factor response style producing the correlation) fits the reported data at least as well as the paper's proposed mechanism.

**D4 — cross_disciplinary_relevance (high priority).** The contract asks whether framing, definitions, and implications are accessible to adjacent-field readers and whether interdisciplinary claims are substantiated. My adversarial reading targets the *substantiated* half rather than the accessibility half. Educational technology sits at the junction of information systems, learning sciences, and higher-education policy, and papers in this space routinely borrow authority across that junction: an IS acceptance model is invoked to license a learning claim, or a correlation among undergraduates is escalated into an institutional policy recommendation. That borrowing is an unearned-transfer argument unless the paper does the work of justifying it. This dimension is also where the "So What?" test and stakeholder blind spots land for me — at 1,597 words on a heavily-replicated construct pair, the incremental contribution claim is itself a claim requiring evidence, and policy-shaped implications that never name instructors, disability/accessibility users, or students without reliable device or network access are asserting reach the design does not have. I name absent voices; what those voices would say is R3's seat, not mine.

**D5 — writing_and_structure (normal priority).** The contract covers organisation, clarity, figure/table quality, and venue conventions. I do not review prose quality as such, and the Surface-Form Parity gate cuts explicitly against me here: polished writing is not evidence of a sound argument, and clumsy writing is not evidence of a broken one. My interest in D5 is confined to structural facts that change what can be verified — a claim in the abstract or conclusion with no corresponding result in the body, numbers that disagree between text and table, an unreported N or missing measure of association that makes a stated conclusion unevaluable, or a limitations section that is present but functions as a ritual disclaimer contradicted by the surrounding text. Presentation defects that leave every claim checkable and consistent are MINOR by construction and will not drive a block from this seat.

## Scoring Plan

### D1: methodology_rigor
- **what_to_look_for**: Whether the stated design (cross-sectional, single administration, self-report on both sides) is carried consistently into how conclusions are worded; whether common-method variance and self-report inflation are acknowledged as *live threats* rather than listed and dropped; sampling frame, recruitment route, response rate, and whether voluntary/convenience participation is treated as a limitation on inference; instrument provenance (adapted scale with citation vs. author-written items), and whether reliability/validity is reported at all or asserted; whether any reported association carries enough numbers (N, effect size or coefficient, and the uncertainty around it) for a reader to check the claim built on it; whether reproducibility affordances are described at the level the ed-tech survey literature actually expects, not at a level imported from another subfield.
- **what_triggers_block**: A conclusion that the design cannot support at all, where the gap is structural rather than fixable by rewording — e.g., a causal or directional-effect claim stated as a finding when both variables are measured once from the same respondents; OR a primary conclusion resting on a quantity the manuscript never reports (no N, no effect estimate, no association statistic), making the central claim unevaluable; OR sampling so evidently non-representative (self-selected volunteers, a single course section) that the stated population-level claim is a different claim from the one the data addresses, with no acknowledgement. For any block whose severity turns on "the field should report X," I must first name the external accepted-practice boundary (a reporting guideline, venue policy, or documented convention in ed-tech survey work) and state why *this* paper's evidence crosses it; failing that, the finding down-rates to advisory and is labelled `[FIELD-NORM UNVERIFIED]` rather than blocking.
- **what_triggers_warn**: The design threats are real and material but the paper's claims can be brought back in line by revision — e.g., common-method bias or self-report/log-data divergence is unmentioned yet the claims stay associational; response rate or sampling frame is missing but the paper does not overreach on representativeness; instrument adaptation is described without citation or reliability evidence while the conclusions do not depend on fine-grained construct discrimination; limitations acknowledge a threat in one sentence but the discussion proceeds as though it were resolved.

### D2: domain_accuracy
- **what_to_look_for**: Directional balance of the cited evidence — whether the reference set runs one way (studies confirming a perceived-usefulness→use link) while the well-established disconfirming strand (self-reported use diverging from LMS log data; acceptance models under-predicting behaviour in mandatory-use settings) is absent or present only as a strawman; whether prior work is characterised accurately or inflated ("established that" for what a source reported as tentative or mixed); whether constructs are used with their field meanings and kept distinct (perceived usefulness vs. satisfaction vs. engagement vs. actual use; adoption vs. mandated compliance); whether any model or framework invoked is attributed a claim it actually makes; whether the institutional/mandatory nature of the platform is acknowledged as changing what the domain literature says about voluntary-adoption findings.
- **what_triggers_block**: A factual misstatement about the domain that the paper's central argument rests on — a cited source's finding reported as its opposite or materially stronger than it is, and the manuscript's thesis depends on that reading; OR two or more constructs treated as interchangeable in a way that makes the headline claim mean something the measures do not support (e.g., self-reported use reported as "engagement" or "learning outcomes"); OR a systematically one-directional evidence base where a substantial and well-known contradicting literature bearing directly on the core claim is entirely absent, such that the paper's framing of the state of the field is not merely incomplete but wrong. Absence of individual references is R2's dimension and does not block from this seat; only misrepresentation of the evidence *direction* does.
- **what_triggers_warn**: Citation selection visibly leans toward supporting work without the disconfirming strand being engaged, but the paper's actual claims are modest enough that the imbalance shapes framing rather than falsifying it; a construct is used loosely in one or two places while measured and reported correctly elsewhere; prior work is slightly over-firmed ("shows" for "suggests") in the introduction without the conclusion depending on it; the mandatory-use context is unremarked but the paper does not claim voluntary adoption.

### D3: argumentative_coherence
- **what_to_look_for**: The exact verbs carrying the main finding, tracked from abstract through results, discussion, conclusion, and implications, watching for escalation from association to influence/drive/lead to/improve; whether reverse causation (use → perceived usefulness) and third-variable accounts (course requirements, instructor enforcement, prior digital skill, workload) are named and addressed or silently excluded; hidden premises the argument needs but never states, above all that self-reported use stands in for actual use and that perceived usefulness is independent of the platform being compulsory; internal contradictions, especially a limitations paragraph conceding non-causality against a conclusion or recommendation that presupposes it; whether a more parsimonious rival explanation (single-source response style, mandated activity) fits the reported pattern at least as well; whether the "so what" of the finding follows from the finding or from a stronger version of it.
- **what_triggers_block**: The main conclusion does not follow from the presented evidence even taking that evidence at face value — a causal, mechanistic, or intervention-warranting claim ("increasing perceived usefulness will increase use," "institutions should invest in X to raise engagement") derived from a single cross-sectional correlation; OR the paper's own reported data contradicts its stated conclusion (a null or negligible association narrated as support); OR an alternative explanation is both simpler and a better fit for the reported pattern and goes entirely unaddressed while the paper's mechanism is presented as established; OR a direct internal contradiction on a load-bearing point (a stated limitation that, if true, falsifies the conclusion drawn two paragraphs later, with no reconciliation).
- **what_triggers_warn**: Causal language appears in loose or hedged form (implications phrased as "may suggest institutions could…") while the results section stays correctly associational; reverse causation or a major confound is acknowledged in limitations but not carried into how the finding is stated; a hidden premise is unstated but plausible and non-fatal, and the conclusion survives making it explicit; the argument has a gap that a paragraph of reasoning would close rather than a redesign; the "so what" is thin or asserted rather than argued, without the core claim itself being unsupported.

### D4: cross_disciplinary_relevance
- **what_to_look_for**: Whether constructs borrowed from information-systems acceptance research are defined in-text for readers from learning sciences or higher-education policy, or used as undefined shorthand; whether a claim licensed in one discipline is transferred into another without justification (an acceptance-model correlation carrying a learning or policy conclusion); whether institution-, sector-, or policy-level recommendations are supported by a student-level cross-sectional sample, and whether the level-of-analysis jump is acknowledged; whether the incremental contribution over a heavily-replicated literature is argued or merely asserted — at ~1,600 words this claim needs to be explicit; which affected groups the implications touch and which are structurally absent (instructors and course designers, students with accessibility needs, students with unreliable device or connectivity access, part-time or distance cohorts, institutional administrators bearing the cost of any recommendation).
- **what_triggers_block**: An interdisciplinary or level-crossing claim that the evidence cannot license and that the paper presents as a principal contribution — e.g., institutional policy or investment prescriptions derived directly from undergraduate self-report at one time point, with no acknowledgement of the level-of-analysis gap; OR a core term carrying different meanings across the paper's source disciplines used equivocally in the central claim, so that the claim is true under one reading and unsupported under the other.
- **what_triggers_warn**: Implications reach modestly past the design (institution-flavoured suggestions offered as suggestions) without the core claim depending on the reach; discipline-specific terminology goes undefined in ways that cost adjacent-field readers clarity but not verifiability; the incremental contribution over the existing acceptance literature is stated but thinly argued; policy-shaped recommendations omit an obviously affected stakeholder group — I name the absent voice and stop there, leaving what that group would say to R3.

### D5: writing_and_structure
- **what_to_look_for**: Traceability of every headline claim to a specific reported result — abstract and conclusion claims matched against the body; numerical consistency between narrative text, tables, and figures (N, percentages, coefficients); whether tables/figures report what their captions say they report and whether the interpretation in the caption follows from the data shown; presence and completeness of the reporting elements a stated conclusion depends on; whether the limitations section does real work or is a ritual disclaimer contradicted by adjacent text; structural placement problems that hide a load-bearing claim where it cannot be checked (a finding announced only in the discussion). I explicitly run the opposite-style counterfactual before scoring: if a claim were rewritten in the opposite register (polished ↔ clumsy), would my verdict change? If yes, the verdict is keying on prose style and must be revised.
- **what_triggers_block**: A structural defect that makes a central claim unverifiable or self-contradicting on the page — the abstract or conclusion reports a finding that appears nowhere in the results; OR the same quantity is reported with materially different values in text versus table with no reconciliation, so the reader cannot tell which supports the claim; OR the key result is presented only as a caption or narrative assertion with no underlying reported data. Note that D5 is normal-priority: under the contract's failure conditions a D5 block does not by itself trigger F1 or F3, so I hold this bar high and reserve it for defects that genuinely destroy checkability, not for organisation I would have done differently.
- **what_triggers_warn**: Claims are traceable but a reader must reconstruct the path (results reported in one order, discussed in another; a figure whose caption over-reads its own data); minor numerical or labelling inconsistencies that do not change which claim is supported; a limitations section that is present but perfunctory relative to the threats the design carries; venue-convention or section-structure deviations that cost clarity without costing verifiability.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Devil's Advocate Review

### Strengths (for fairness, 1–2 sentences)

The manuscript's causal discipline is real and above the median for this literature: it names the reverse pathway explicitly (§5), restricts itself to correlational verbs throughout, and cites a measurement critique (Vasquez, 2020) against its own instrument rather than in defence of it. The a priori sensitivity statement in §3.4 is deployed correctly — as design sensitivity, not post hoc justification — and the Spearman check is reported with its actual value rather than asserted.

### Strongest Counter-Argument

Suppose I hold the view that this paper reports nothing. Both variables come from one respondent, in one sitting, on adjacent Likert items. A single response disposition — a student broadly positive about institutional tools, who reports both high usefulness and high use — generates r ≈ .42 with no relation between the constructs whatsoever. This account is strictly simpler than the acceptance-theoretic one: it requires no mechanism, only a respondent. The manuscript never raises it. Its one measurement caution, Vasquez (2020), concerns whether the use estimate is *accurate*; shared-method covariance concerns whether the two estimates are *independent*. The paper treats the first citation as covering the second problem, and it does not.

Now grant that the correlation is substantive. The paper's defence of its own worth is that it is "one point in a distribution" (§2). That defence requires the point to be locatable, and the manuscript withholds every coordinate: which distribution, what prior estimates, which items survived adaptation, how many of how many enrolled students answered, which platform, and whether use of that platform was compulsory. "Consistent with prior technology-acceptance research" is asserted in the Abstract, in §5, and in §7 without a single prior magnitude appearing anywhere in the paper — a claim that cannot be checked and therefore cannot fail.

And the sentence a reader carries away — "perceived usefulness tracks with LMS engagement among undergraduates" — names a construct the study never measured. The manuscript hedges causality four separate times and hedges its construct claim not once. The humility is concentrated on the axis where the paper is already safe.

### Issue List

#### CRITICAL

| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|----------|---------------------|-----------------------------|
| C1 | 4 (Logic Chain) / Data–Conclusion Mismatch | Unhedged construct substitution in the headline claim. The measured quantity is a single item on self-reported weekly *access frequency* (§3.2). This is relabelled "use" throughout and then, in the Abstract's terminal sentence, "LMS **engagement**" — a construct the study contains no measure of. The same substitution runs through §2 ("their engagement with it," characterising prior work) and §4 ("reported engagement"). The paper defends the self-report↔behaviour substitution at three separate points and never once defends this one. Under the field's meaning of engagement the headline claim is unsupported; a student opening the platform six times daily to read announcements is coded maximally "engaged." | Abstract (final sentence); §2 ¶1; §4 ¶2; §3.2 | *Engagement* in higher-education and educational-technology research is a multidimensional construct (behavioural, emotional, cognitive) — canonical formulation Fredricks, Blumenfeld & Paris (2004), *Review of Educational Research* 74(1) — and the learning-analytics literature the manuscript gestures at via Vasquez (2020) treats platform access counts as a proxy whose relation to engagement is the open question, not a synonym for it. APA JARS-Quant likewise requires the construct named in a conclusion to be the construct operationalised in Measures. | The sole use measure (§3.2) carries no behavioural-depth, task-type, affective, or cognitive component. Nothing in §3, §4, or §6 defends treating access frequency as engagement, and no limitation names the gap. Because the substitution appears in the Abstract's last sentence — the most-read and most-quoted line of the manuscript — it is not a generic reporting shortfall but an unhedged construct claim at the point of maximum reader exposure, in a paper that demonstrably knows how to hedge. |

#### MAJOR

| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|----------|---------------------|-----------------------------|
| M1 | 8 ("So What?") / Evidence Gap | The declared contribution — "an incremental data point, comparable with prior work," "one point in a distribution" — is asserted, never substantiated, and as written cannot be falsified. No prior magnitude is stated anywhere against which r = .42 could be judged typical, high, or low; the instrument is "adapted" with no modification described and no item reproduced; prior studies' outcome operationalisations are never characterised; the platform is unnamed. Comparability is the paper's entire value proposition and every input it requires is withheld. | §2 ¶3; Abstract; §5 ¶1; §7 | APA JARS-Quant (Appelbaum et al., 2018, *American Psychologist* 73(1)) requires reporting of instrument modifications and the psychometric evidence bearing on the modified form; the ITC *Guidelines for Translating and Adapting Tests* set the same item-level documentation expectation. Both are external checkable standards. | §3.2 states the six-item scale was "adapted from Costa and Wren (2019)" and reports α = .88, but no item is reproduced and no modification described — so α = .88 cannot be compared to the source instrument's reliability, and the scale cannot be reconstructed. This crosses the boundary *here specifically* because the manuscript's stated contribution is comparability; an undocumented adaptation removes the basis for the exact comparison the paper offers as its reason to exist. |
| M2 | 4 (Logic Chain) / Internal Contradiction | The onboarding implication is logically incompatible with the concession that precedes it by two sentences. §5 states the reverse pathway is "equally consistent with the data." If that is true, the correlation offers *zero* directional warrant for an intervention that raises perceived usefulness — not "modest support." The hedge ("suggested by, not proven by") softens the assertion without reconciling the incompatibility; it converts a logical problem into a rhetorical one. | §5 ¶2 (both halves) | n/a — internal logic; severity does not rest on a field norm. | n/a |
| M3 | 5 (Overgeneralisation) / Foundation | Recruitment ran through "the institution's course-announcement channel" — a channel inside the platform under study. This systematically under-samples the low-use tail of *both* variables, which is also precisely the population the §5 onboarding implication targets. §6's fourth limitation names generic volunteer bias, not this mechanism. Compounding it, no eligible-population count and no response rate are reported, so 214 could be 15% or 2% of the frame and the direction and magnitude of the resulting range restriction are undeterminable. | §3.1; §6 (fourth limitation) | AAPOR *Standard Definitions* and APA JARS-Quant both require the sampling frame, number approached, and response rate in survey reports. | §3.1 reports 233 received / 214 analysed with no denominator, so the sample fraction is unknown by roughly an order of magnitude. The circularity half of this finding is norm-independent: it is a structural selection problem visible from the manuscript's own text, and §6's wording ("students who engage more with institutional channels may be overrepresented") describes a different, weaker problem than recruiting for a study of LMS use *through the LMS*. |
| M4 | 4 (Logic Chain) / Internal Contradiction | §3.1 reports that "5 duplicate entries were removed." §3.3 states "no identifying information was collected, and responses could not be linked back to individual students." As written, these cannot both be fully true: identifying duplicates requires some persistent or quasi-identifying signal (IP, cookie, device fingerprint) or a stated response-pattern rule. The deduplication criterion is never given, so the ethics account and the data-handling account contradict each other on the page. | §3.1 vs §3.3 | n/a — internal contradiction; severity does not rest on a field norm. | n/a |
| M5 | 2/3 (Rival Account) / Stronger Counter-Narrative | Single-source common-method covariance is nowhere addressed — not in §3, not in §3.4, not in §6. Both variables were collected from the same respondent, in the same instrument, in the same sitting, on the same five-point response format. A consistent responding disposition reproduces the observed pattern with no substantive relation between constructs, and requires strictly fewer assumptions than the acceptance-theoretic reading. The Vasquez (2020) citation is repeatedly deployed as if it covered this; it addresses estimate *accuracy*, not estimate *independence*. | §3.2; §3.4; §6 (all four limitations) | n/a — rival-account gap; severity does not rest on a field norm. | n/a |

#### MINOR

| # | Dimension | Issue Description | Location |
|---|-----------|-------------------|----------|
| m1 | 4 | "The proportion of variance shared by the two measures was accordingly modest" — the number (r² ≈ .18) is never given, so the reader must compute the paper's own most deflationary statistic. |
| m2 | 4 | Declared measurement level contradicts the foregrounded statistic: §3.2 says "we treat this as an ordinal indicator," §3.4 makes Pearson primary and Spearman the "robustness check," and §4 reports a median for the same variable it correlates parametrically. Substantive impact is small (ρ = .40 vs r = .42), which is why this is MINOR rather than MAJOR — but the paper's own declaration and its own headline point in opposite directions. |
| m3 | 4 | The Abstract reports r and p but omits the CI, leaving "moderately" as the reader's only magnitude cue; §3.4 promises a CI without stating its derivation. |
| m4 | 1 | "Perceived usefulness" is defined in-text (§2); "engagement" — the term doing the unearned work in C1 — is never defined anywhere. The defined term is the safe one. |
| m5 | 5 | Whether LMS use is compulsory at this institution is never stated, though the acceptance lineage the paper invokes ("adoption and continued use," §2) is a voluntary-use literature and mandate changes what both variables mean. §4 half-acknowledges this via "course requirements and assessment schedules" and then drops it. |
| m6 | 6 (Alternative Paths) | Year level was collected (§3.1, "spanned all four year levels") and never used, never reported as a distribution, and never broken out — while the paper's only practical implication concerns onboarding, i.e. first-year students. The cheapest available check on the paper's own implication sits unused inside the existing dataset. |

### Ignored Alternative Explanations/Paths

1. **Single-source response style (strongest rival).** One respondent, one sitting, adjacent Likert items, identical response format. A general disposition — acquiescence, self-presentation, or a stable "the platform is fine and I use it" self-concept — produces r ≈ .42 without any relation between perceived usefulness and use. Simpler than the paper's account because it postulates no mechanism at all. Entirely absent from §6.
2. **Course-structure common cause.** Assessment schedules, instructor enforcement, and how much graded work a course places in the platform drive frequency mechanically *and* drive perceived-usefulness ratings (a system hosting your graded work is useful). Ibarra and Poll (2021) is cited for exactly this in §2 and then demoted in §4 to unexplained residual variance rather than treated as a confound. Under this account the correlation is a between-course artifact — and it makes a testable prediction the paper had the data to check.
3. **Reverse pathway as dominant, not co-equal.** §5 calls the reverse direction "equally consistent," which is a symmetry *assumption*, not a finding. Habitual use → familiarity → higher usefulness ratings is a well-motivated single-direction account that fits the data equally well and renders the onboarding implication inert. The paper's even-handedness here is asserted rather than argued.
4. **Truncated-distribution estimation.** If the low-use tail never saw an invitation delivered inside the platform, r was estimated on a restricted range and is not an estimate of the population parameter the paper claims to be contributing "one point" of. Note honestly that this cuts toward attenuation, not inflation — but it makes the reported value's relation to any pooled distribution undefined, which is the claim at stake.

### Missing Stakeholder Perspectives

- Instructors and course designers — named implicitly in §4 as the source of "course requirements" but never as respondents, actors, or an affected group.
- Students who had disengaged from the platform, and students with unreliable device or network access — structurally excluded by an in-platform recruitment channel.
- Students using assistive technology or with accessibility needs — a group for whom "perceived usefulness" and "frequency of access" have materially different content.
- The institutional actor who would fund the §5 onboarding recommendation — the resource-bearing party is absent from the framing that addresses them.
- Part-time, distance, and non-traditional cohorts — the sample is characterised only by year level.

### Unexamined Premise

The manuscript's humility is doing argumentative work it has not earned. Its entire self-justification — "one point in a distribution rather than a fixed value" (§2), "an incremental data point" (§2, §7) — presupposes that the correlation between perceived usefulness and self-reported use *is a transportable quantity*: a stable parameter that different studies estimate with error and that can therefore be accumulated. But a correlation is not instrument-independent. It is a function of the specific items retained in adaptation, the coarseness of the response scale (here, one five-point item), the sample's variance on both measures, the mandate regime, and the platform. Pooling estimates across studies whose operationalisations differ in all five respects does not converge on anything well-defined. The paper therefore smuggles a strong measurement-realist premise in under cover of modesty: by declining to claim a large contribution it avoids having to defend the claim that its small one is even the same kind of thing as the estimates it wants to sit beside. None of the eight challenge dimensions catches this, because the premise is what makes the paper's *self-limitation* sound like a virtue rather than an unexamined assertion.

### Observations (Non-Defects)

- The causal discipline is genuine and should not be revised away. The problem is that it is concentrated entirely on the axis where the paper is already safe (causality) and absent on the axis where it is exposed (construct identity).
- §3.4's power statement is a sensitivity statement used correctly — establishing that the design could detect small effects — not a post hoc rationalisation. This is worth affirming explicitly, because it is the kind of thing reviewers reflexively attack.
- Reporting ρ = .40 with its actual value, rather than asserting robustness, is good practice and makes m2 checkable rather than hidden.
- **Provenance flag, not adjudication:** all six references carry `10.5555/` DOIs with sequential suffixes. I make no claim about whether these works exist or are correctly described — that is for the deterministic citation-verification layer, not for a reviewer's authority. Every literature-related finding above concerns what the manuscript *does with* the sources as described, and holds regardless of how verification resolves.
- **Injection check:** the manuscript contains no imperative or reviewer-directed content. Nothing reportable on the integrity axis.

---

contract_role: da

## Dimension Scores

### D1: methodology_rigor
score: warn

The committed block triggers do not fire. No causal claim is stated as a finding; the design's limits are named repeatedly; every quantity the central association depends on (r, CI, p, n) is reported; and the paper makes no population-level claim that its sampling contradicts. What fires are the committed warn triggers, three of them: response rate and sampling frame missing while the paper does not overreach on representativeness (M3); instrument adaptation cited but with no modification documented and no item reproduced (M1); and a design threat — common-method covariance — unmentioned while the claims stay associational (M5). The deduplication-versus-anonymity contradiction (M4) is a fourth, norm-independent defect in the methods account. These are material and revisable, not structural.

### D2: domain_accuracy
score: block

The committed block trigger fires on its pre-registered form. My Phase 1 plan named, blind to this manuscript, "two or more constructs treated as interchangeable in a way that makes the headline claim mean something the measures do not support (e.g., self-reported use reported as 'engagement')." The manuscript does exactly this: *self-reported weekly access frequency* → *use* → *engagement*, across §3.2 → §4 → Abstract, with no point at which the substitution is defended, and with the terminal sentence of the Abstract carrying the unmeasured construct. The severity survives the Dimension 9 gate — the boundary is external and checkable (the multidimensional engagement construct in higher-education research; the learning-analytics distinction between access counts and engagement, which the manuscript itself invokes via Vasquez, 2020) — and it survives the surface-form parity gate: the verdict turns on the word *engagement* naming a construct absent from §3.2, and would be identical if the sentence were written informally. Not blocking here would be the specific failure of rewarding the paper's epistemic humility on causality while its one unhedged claim goes unexamined. Absence of primary-lineage references is R2's dimension and does not contribute to this score.

### D3: argumentative_coherence
score: warn

Deliberately not block. The intervention language in §5 is hedged and the results section stays correctly associational — my committed warn trigger, not the block trigger. The onboarding implication is logically incompatible with the reverse-pathway concession that precedes it (M2), but that implication is subsidiary: removing it leaves the core thesis intact, so it does not meet my committed bar of "a stated limitation that, if true, falsifies the conclusion." The common-method rival (M5) is simpler than the paper's account and equally fitting, but I committed to requiring *simpler AND better fit* for a block, and equally-fitting does not clear my own bar. The unsubstantiated contribution claim (M1) is a thin-or-asserted "so what," which my Phase 1 plan routes explicitly to warn. Three separate warn triggers fire; no block trigger does.

### D4: cross_disciplinary_relevance
score: warn

I considered and rejected the block trigger for equivocation of a core term across source disciplines. The escape it requires — that the claim be *true under one disciplinary reading* — does not hold here: the information-systems lineage would say "use," not "engagement," so the term is not doing legitimate disciplinary double-duty, it is simply wrong inside the paper's own primary field. That routes the defect to D2, where I scored it, rather than double-counting it here. What fires are warn triggers: implications reaching modestly past the design (institution-level onboarding from student-level cross-sectional data, hedged and subsidiary); an incremental contribution stated but thinly argued (M1); an undefined term costing adjacent-field readers clarity (m4); and policy-shaped implications omitting obviously affected groups — most sharply, the low-use students the recommendation targets and the recruitment channel excludes.

### D5: writing_and_structure
score: warn

Held to the high bar I committed to for this normal-priority dimension. No block: every claim is traceable to §4, the numbers are internally consistent between narrative and text, and there are no tables or figures to disagree with. The opposite-style counterfactual returns the same verdict — the defects are missing reporting elements, not prose quality. Warn on the substance: r² is described but never given (m1); the CI's derivation is promised in §3.4 and never stated (m3); the declared ordinal measurement level and the foregrounded parametric statistic contradict each other (m2); the six items and the exact use-item wording are reproduced nowhere, so the instrument is not reconstructible; and the Limitations section, while genuinely substantive on four counts, omits the recruitment-channel mechanism, the response-rate gap, the mandate context, and the construct substitution — i.e. every threat identified above.

## Failure Condition Checks

### F1
fired: true

D2 (`domain_accuracy`, mandatory) scores `block`. The predicate "any mandatory dimension scores 'block'" is satisfied by my own scores. Severity 90 — highest of the fired conditions.

### F2
fired: true

D1 `warn`, D2 `block`, D3 `warn` — three mandatory dimensions at warn or worse, so "two or more" is satisfied. Severity 70; subordinate to F1 by precedence.

### F3
fired: false

D4 (`cross_disciplinary_relevance`) is the only high-priority dimension and scores `warn`, not `block`. I explicitly considered and rejected the D4 block trigger rather than letting the D2 defect propagate into a second dimension.

### F0
fired: false

Not every mandatory dimension scores `pass`; D2 blocks and D1/D3 warn.

## Review Body

The panel-relevant question this seat exists to answer is whether the manuscript's argument survives contact with its own methodological description. Mostly it does — and that makes the one place it does not more consequential, not less.

This paper is disciplined in a specific and narrow way. It hedges causality in the Abstract, in §2, twice in §5, in §6, and again in §7. It cites Delgado (2020) for the reverse pathway and Vasquez (2020) against the accuracy of its own outcome measure. That posture invites a reviewer to grade the epistemics and skip the design, and the temptation should be named: acknowledging a limitation is not addressing it, and the manuscript's four candid limitations in §6 are all on axes where conceding costs it nothing. Causality is conceded and the paper's thesis does not need causality. Single-site generalisability is conceded and the paper's thesis is explicitly single-site. Self-report-versus-logs is conceded and the paper's thesis is explicitly about perceived use. Every hedge is placed where the paper is already safe.

The one claim carrying real weight is unhedged. The measured quantity, per §3.2, is how often a respondent accessed the platform in a typical week — one item, five categories. That becomes "use" in §4 and "LMS engagement" in the Abstract's final sentence, with §2 and §4 both using "engagement" for the same slot in between. No sentence anywhere defends the substitution, no limitation names it, and "engagement" — unlike "perceived usefulness," which §2 defines carefully — is never defined at all. A student who opens the platform several times daily to check announcements registers as maximally engaged under this measure. This is a factual claim about the domain that the measures do not support, appearing in the sentence most likely to be read in isolation, and it is why D2 blocks. It is also the finding I pre-committed to blind, which is the only reason I am confident it is not manufactured severity.

Two structural problems compound it. First, the paper's declared reason to exist is comparability — "one point in a distribution," "comparable with prior work" — and it withholds every input comparability requires. No prior magnitude appears anywhere, so "consistent with prior technology-acceptance research," asserted three times, is a claim that cannot be checked and therefore cannot fail. The instrument is adapted with no modification documented, so α = .88 is not comparable to its source. The eligible population is unreported, so the sample fraction is unknown. The platform is unnamed and its mandate status unstated. Second, the recruitment channel sits inside the platform under study. §6 records this as generic volunteer bias; it is not. It is selection on the dependent variable's own subject matter, which removes exactly the low-use tail that anchors both distributions — and which is exactly the population the §5 onboarding implication addresses. The paper's one practical recommendation targets a group its design structurally excludes, and it holds an unused year-level variable (§3.1) that would have permitted the single most relevant check.

Beneath all of it sits a premise the paper never states: that this correlation is a transportable quantity at all. It is not instrument-independent — it is a function of which items survived adaptation, of a five-point single-item response scale, of the sample's range on both measures, and of a mandate regime the paper does not report. The manuscript's modesty is what allows this premise to pass unexamined: by claiming little, it never has to argue that its little thing is the same kind of thing as the estimates it wants to be pooled with.

What I am not saying: that this should have been a bigger study. The narrow scope declared in §1 is a legitimate design choice and the requests that would enlarge it are not mine to make. Every finding above is of the form "this claim is not supported by this design" or "this text contradicts that text" — none is "write a different paper." Three of the five findings are closable inside the existing dataset and word count: rename the construct or defend the substitution, report the denominator and the deduplication rule, and state what distribution the estimate is a point in.

## Editorial Decision

Precedence resolution over my own fired conditions: F1 (severity 90) and F2 (severity 70) both fired; F1 carries the higher severity and therefore controls. The controlling defect is the D2 block — the undefended construct substitution culminating in the Abstract's terminal claim — with the D1/D3 warn cluster (undocumented instrument adaptation, missing denominator and recruitment-channel selection, unaddressed common-method rival, the deduplication-versus-anonymity contradiction, and the reverse-pathway/onboarding incompatibility) as the accompanying revision load. `cross_reviewer_quantifier` is panel-level machinery for the synthesiser; this decision is derived from my scores alone.

editorial_decision=reject_or_major_revision

# PART 3 — EDITORIAL SYNTHESIS

# Sprint Contract Mechanical Synthesis

**Contract**: `reviewer/reviewer_full/v1` · `baseline_version` v3.6.2 · `generated_at` 2026-07-25T08:00:00Z · `panel_size` N = 5
**Panel (usable Phase 2 outputs)**: EIC, R1 (methodology), R2 (domain), R3 (perspective), DA — 5 of 5. Cardinality invariant satisfied; no `[PANEL-SHRUNK]`.

## Step 1 — Scoring Matrix

Dimensions resolved by `id`; each cell is the seat's `## Dimension Scores` value verbatim.

| Dimension | `priority` | EIC | R1 | R2 | R3 | DA |
|-----------|-----------|-----|----|----|----|----|
| D1 `methodology_rigor` | mandatory | warn | warn | warn | warn | warn |
| D2 `domain_accuracy` | mandatory | warn | warn | **block** | warn | **block** |
| D3 `argumentative_coherence` | mandatory | warn | warn | warn | warn | warn |
| D4 `cross_disciplinary_relevance` | high | warn | warn | warn | warn | warn |
| D5 `writing_and_structure` | normal | pass | warn | warn | warn | warn |

Mandatory set = {D1, D2, D3}. High-priority set = {D4}. Normal set = {D5}.

## Step 2 — Per-Condition Evaluation

### F1 — severity 90, `cross_reviewer_quantifier: any`

Expression: `any mandatory dimension scores 'block'` → §9 pattern 1 (priority-scoped single-match, bare `mandatory`). Recognised.

Per-reviewer predicate (does any of D1/D2/D3 score `block` for that seat?):

| EIC | R1 | R2 | R3 | DA |
|-----|----|----|----|----|
| false | false | **true** (D2) | false | **true** (D2) |

`any` threshold = ≥ 1 of N=5. Holds for 2. **fired: true.**

### F2 — severity 70, `cross_reviewer_quantifier: majority`

Expression: `two or more mandatory dimensions score 'warn' or worse` → §9 pattern 2 (priority-scoped count-based, ordering `pass` < `warn` < `block`). Recognised.

Per-reviewer predicate (count of mandatory dimensions at `warn` or worse):

| EIC | R1 | R2 | R3 | DA |
|-----|----|----|----|----|
| 3 → true | 3 → true | 3 → true | 3 → true | 3 → true |

`majority` threshold for N=5 = ⌊5/2⌋ + 1 = 3. Holds for 5. **fired: true.**

### F3 — severity 60, `cross_reviewer_quantifier: any`

Expression: `any high-priority dimension scores 'block'` → §9 pattern 1 (`high-priority` variant). Recognised. High-priority set = {D4}; D4 = warn across all five seats.

`any` threshold = ≥ 1 of 5. Holds for 0. **fired: false.**

### F0 — severity 10, `cross_reviewer_quantifier: all`

Expression: `every mandatory dimension scores 'pass'` → §9 pattern 3 (universal over priority). Recognised. No seat has D1/D2/D3 all `pass`.

`all` threshold = 5 of 5. Holds for 0. **fired: false.**

## Step 3 — Precedence and Decision

Fired conditions: F1 (severity 90), F2 (severity 70). Highest severity governs; no tie, so no ordinal tie-break needed. F1's `action` is emitted verbatim.

fired_conditions: [F1, F2]

editorial_decision=reject_or_major_revision

*Consistency note (non-binding): the five seats' own `## Failure Condition Checks` — EIC {F2}, R1 {F2}, R2 {F1, F2}, R3 {F2}, DA {F1, F2} — reconcile with the panel-level evaluation above under the published quantifiers. No `[EXPRESSION-UNRECOGNISED]`, no `[REVIEWER-SELF-INCONSISTENT]`.*

---

# Editorial Decision Package

## Part 1: Editorial Decision Letter

### Manuscript Information

- **Title**: cross-sectional survey of perceived usefulness and self-reported LMS use among undergraduates (the verbatim title string was not carried into the synthesis inputs; the panel cards reference it only in part — "Self-Reported Use")
- **Manuscript ID**: not carried in synthesis inputs
- **Submission Date**: not carried in synthesis inputs
- **Decision Date**: 2026-07-25
- **Review Round**: Round 1
- **Journal**: *Journal of Computing in Higher Education* (per the EIC seat's identity)

### Review Panel Provenance (#540)

No provenance stamp accompanied this dispatch, so this block cannot be filled with one of its three pinned statements without inferring the panel's model-family composition — which the protocol forbids. Recorded as unresolved: **the panel's model-family composition is undisclosed to this synthesis.** No claim of model independence is made, and if the five seats ran on a single family, the correlated-blind-spot caveat (Ren et al. 2026, arXiv:2607.13104 §5.2) applies unmitigated. The orchestrator should supply the stamp and re-emit this block before the letter ships to the author.

---

Dear Author(s),

Thank you for submitting your manuscript to the *Journal of Computing in Higher Education*. Your manuscript has been reviewed by five independent reviewers, including the Editor-in-Chief.

### Decision: Major Revision

The sprint contract's fired action is the disjunctive range `reject_or_major_revision` (condition F1, severity 90). Within that range the editorial decision is **Major Revision**, and this is not a softening of the fired action: every seat that scored the blocking defect — R2 and the Devil's Advocate — states in its own card that the defect is closable in text without new data collection ("blocked on defects that a careful revision round can fully close" — R2; "closable inside the existing dataset and word count" — DA). All five seats independently recommend major revision in prose.

### Reviewer Summary

| Reviewer | Role | Recommendation | Confidence |
|----------|------|---------------|------------|
| EIC | Editor-in-Chief, higher-education technology; LMS-adoption triage | Major Revision | 4 |
| Reviewer 1 | Quantitative methodologist, educational/psychological measurement | Major Revision | 4 |
| Reviewer 2 | Senior higher-education researcher, student engagement with digital environments | Major Revision (within `reject_or_major_revision`) | 4 |
| Reviewer 3 | Director of institutional research and academic-technology assessment | Major Revision | 4 |
| DA | Devil's Advocate | `reject_or_major_revision`; findings framed as revision-closable | not stated (card carries no Confidence Score) |

### Top Blocking Issues (3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | Undefended construct substitution: the measured quantity is self-reported weekly **access frequency**, reported as "use" and then as "**engagement**" in the Abstract's terminal sentence — the sole driver of both D2 `block` scores and therefore of F1 | R2, DA (block); corroborated by EIC, R1, R3 at warn | §3.2 "how often the respondent accessed the LMS in a typical week" vs Abstract, final sentence: "perceived usefulness tracks with LMS engagement among undergraduates" | R1 |
| 2 | The declared contribution — a poolable estimate "comparable with prior work," "one point in a distribution" — is asserted with no prior magnitude, no comparator operationalisation, and no stated gap, so "consistent with prior technology-acceptance research" is unevaluable | R2 (second block trigger), EIC (principal editorial reservation), R3; DA M1 | §2 ¶3; §5 ¶1; Abstract | R7 (+ S2) |
| 3 | The reporting floor for a poolable estimate is not met: no eligible-population denominator or response rate, and an instrument described as "adapted" with the adaptation undocumented and no item reproduced | EIC, R1, R2, R3 (CONSENSUS-4 on both halves); DA M1, M3 | §3.1 "233 received → 214 analysed", no denominator; §3.2 "adapted from Costa and Wren (2019)" | R2, R6 |

### Consensus Analysis

#### Step 1a — Reviewer Summary Matrix

| Dimension | EIC | R1 (Methodology) | R2 (Domain) | R3 (Perspective) |
|-----------|-----|------------------|-------------|------------------|
| Overall Recommendation | Major Revision | Major Revision | Major Revision | Major Revision |
| Confidence Score | 4 | 4 | 4 | 4 |
| Key Strengths | Causal discipline held across four load-bearing sections; cites Vasquez (2020) against its own measure; reporting exceeds the norm for its class; scope declared not smuggled; ethics reported | A priori sensitivity statement used in the correct direction and reconstructs; primary estimate independently reconstructible; one pre-specified test so no p-hacking surface; rank-based check reported; complete case disposition | Causal discipline real not cosmetic; self-report treated as a measurement condition before results; scope declared; third-variable awareness present in Results | Scope discipline survives translation across fields; contribution *shape* right for institutional evidence; ethics and consent reported at all; §4 resists its own headline |
| Key Weaknesses | → Step 1b | → Step 1b | → Step 1b | → Step 1b |
| # of Questions | 6 | 8 | 5 | 7 |
| # of Minor Issues | 8 | 4 | 5 | 6 |

DA (tracked separately): 1 CRITICAL (C1), 5 MAJOR (M1–M5), 6 MINOR (m1–m6), 4 ignored alternative explanations, 5 missing stakeholder perspectives, 1 unexamined premise.

#### Step 1b — Weakness Sub-Claim Inventory

Rows are recorded for every non-silent `(sub_claim, reviewer)` position across the four non-DA reviewers. `not-mentioned` positions are not enumerated here; they are counted explicitly in the disposition table below, where the denominator is always 4.

| sub_claim_id | parent_weakness | reviewer_id | position | evidence_pointer | confidence |
|--------------|-----------------|-------------|----------|------------------|------------|
| SC-1a | Construct substitution (frequency → use → engagement) | EIC | raised | W3; Structural Coherence: "That single word is the coherence break" | 4 |
| SC-1a | " | R1 | corroborated | D2: "the Abstract's 'LMS engagement' naming a broader construct than the access-frequency item operationalizes" | 4 |
| SC-1a | " | R2 | raised | W2; Terminology precision; grounded on Fredricks et al. (2004) | 4 |
| SC-1a | " | R3 | raised | Assumption Audit, construct question; Q7; D2 | 4 |
| SC-1b | Severity of the construct substitution | R2 | raised | D2 `block`: "that misdefinition propagates into the paper's conclusions" | 4 |
| SC-1b | " | EIC | disputed | D2 `warn`: "domain slippage that is real but not invalidating" | 4 |
| SC-1b | " | R1 | disputed | D2 `warn`: block triggers explicitly do not fire | 4 |
| SC-1b | " | R3 | disputed | D2 `warn`: "No block trigger fired"; defers on possible field convention | 4 |
| SC-2 | No population denominator / response rate | EIC | raised | W2; Q1 | 4 |
| SC-2 | " | R1 | corroborated | W4; Q4; Sampling Strategy | 4 |
| SC-2 | " | R2 | corroborated | W4(c): "no denominator or response rate for the sampling frame" | 4 |
| SC-2 | " | R3 | raised | W1; Q1: "the first question any institutional-research audit asks" | 4 |
| SC-3 | Instrument adaptation undocumented; items not reproduced | EIC | raised | W2; Q4 | 4 |
| SC-3 | " | R1 | raised | W3; Q5; Reproducibility | 4 |
| SC-3 | " | R2 | raised | W3; Q1; AERA/APA/NCME (2014) Ch. 1 | 4 |
| SC-3 | " | R3 | raised | Minor Issues: "The instrument is not reproducible"; D1 | 4 |
| SC-4 | "Previously validated" does not transfer to the adapted form | R1 | raised | W3: "transfers validation evidence from the source form to an altered form on no stated basis" | 4 |
| SC-4 | " | R2 | corroborated | W3: "validity attaches to interpretations of scores for proposed uses" | 4 |
| SC-5 | Comparability/poolability asserted without a benchmark | EIC | raised | W1, W4; Originality; Q6 | 4 |
| SC-5 | " | R2 | raised | W4(a)(b); Review Body: "made three times and demonstrated zero times" | 4 |
| SC-5 | " | R3 | corroborated | Strength 2; Minor Issues, "Abstract-to-body strength" | 4 |
| SC-6 | No primary acceptance-literature source; no quantitative synthesis | EIC | raised | W4; Minor Issues §2 | 4 |
| SC-6 | " | R2 | raised | W1; Missing Key References (Davis 1989; Venkatesh et al. 2003; a meta-analytic anchor) | 4 |
| SC-6b | Severity of the missing literature base | R2 | raised | D2 `block` trigger 1: "rests on a literature base that contains no distribution" | 4 |
| SC-6b | " | EIC | disputed | D2 `warn`: "attribution slippage rather than misdefinition" | 4 |
| SC-7 | Common-method variance unaddressed | R1 | raised | W5; Q8; D3 | 4 |
| SC-8 | Outcome reliability unknown → unquantified attenuation; "moderate" unstable | R1 | raised | W1; Q1: "≈ .54 … ≈ .63" under stated assumed reliabilities | 4 |
| SC-9 | Measurement-level inconsistency; r-vs-ρ robustness claim overstated | R1 | raised | W2; Q2; Analysis Methods | 4 |
| SC-10 | CI derivation method unstated | EIC | raised | Minor Issues: "§3.4: state how the 95% CI was derived" | 4 |
| SC-10 | " | R1 | corroborated | W2; Q3 | 4 |
| SC-11 | r² described verbally, never given numerically | EIC | raised | Minor Issues §4 | 4 |
| SC-11 | " | R1 | corroborated | Analysis Methods: "It is .18; state it." | 4 |
| SC-11 | " | R2 | corroborated | W5; APA JARS-Quant grounding | 4 |
| SC-12 | Outcome's five-category distribution and dispersion unreported | R1 | raised | W4; Q4; Results Presentation | 4 |
| SC-12 | " | R2 | corroborated | W5: "a reader cannot reconstruct the distribution of the outcome variable" | 4 |
| SC-12 | " | R3 | corroborated | W2: "if the frequency distribution … shows a thin low tail, report it" | 4 |
| SC-13 | Recruitment inside the platform under study = structural selection | EIC | raised | Q2: "Is that channel inside the LMS under study?" | 4 |
| SC-13 | " | R1 | corroborated | W4: "plausibly under-represents the low-use tail" | 4 |
| SC-13 | " | R3 | raised | W2; Q2: "the sampling instrument is inside the subject matter" | 4 |
| SC-14 | Deduplication rule unstated; tension with §3.3 anonymity | EIC | raised | Q3: "the two passages are in tension" | 4 |
| SC-14 | " | R1 | corroborated | Data Collection; Q6 | 4 |
| SC-14 | " | R3 | raised | W1; Q3: governance-and-reporting framing | 4 |
| SC-15 | Year level collected but never analysed | EIC | raised | W5; Q5 | 4 |
| SC-15 | " | R1 | corroborated | W5; Q7 | 4 |
| SC-15 | " | R2 | corroborated | Q5; Review Body: "not scope expansion" | 4 |
| SC-15 | " | R3 | raised | W5; Q4 | 4 |
| SC-16 | §5 onboarding implication over-reaches its warrant | EIC | raised | W5: "will be extracted and quoted to a resourcing committee" | 4 |
| SC-16 | " | R3 | raised | Implementation feasibility: "reframe … as a testable hypothesis" | 4 |
| SC-16 | " | R2 | corroborated | D4 `warn`: "supported by a citation rather than by the study's own evidence" | 4 |
| SC-16 | " | R1 | disputed | D3: "hedged three times … so it does not amount to an interventionist recommendation" | 4 |
| SC-17 | "More LMS use is better" premise unstated, no outcome link | R3 | raised | W5; D3: "the first question a budget committee asks" | 4 |
| SC-18 | Non-student stakeholders and access/digital-literacy variation absent | R3 | raised | W3, W4; D4 | 4 |
| SC-19 | Voluntary-vs-mandated use never raised | R3 | raised | Assumption Audit (b); Q6; D2 | 4 |
| SC-20 | Context descriptors too thin for transferability | EIC | raised | W2; Minor Issues §3.1 | 4 |
| SC-20 | " | R1 | corroborated | D4: platform unnamed, disciplinary composition absent, mandate status absent | 4 |
| SC-20 | " | R2 | corroborated | W4(c); Q4; D4 | 4 |
| SC-20 | " | R3 | raised | Minor Issues: "Context descriptors are too thin for transferability" | 4 |
| SC-21 | No table/figure; no data or materials availability statement | R1 | raised | Results Presentation; Reproducibility; Minor Issues | 4 |
| SC-21 | " | R3 | corroborated | Minor Issues: "No table or figure" | 4 |
| SC-21 | " | EIC | disputed | D5 `pass`: "given a single bivariate result reported inline with full statistics, none is required" | 4 |
| SC-22 | Abstract omits the CI reported in the body | EIC | raised | Title & Abstract; Minor Issues | 4 |
| SC-22 | " | R2 | corroborated | Minor Issues | 4 |
| SC-23 | APA 7 statistical formatting deviations | R1 | raised | Minor Issues; D5 | 4 |
| SC-24 | §6 limitations exert no pressure on §7 | EIC | raised | Conclusion; Minor Issues §6; D3 | 4 |

#### Step 1c — Surface-Form Parity Check

Run before any weighting. Two sub-claims were candidates for down-weighting on phrasing, and neither was down-weighted:

- **SC-17 / SC-18 / SC-19 (R3).** R3 writes from an institutional-research seat in plainer, less technical register than R1's psychometric prose ("I could not take this to a provost"; "a shared laptop, a data cap, or a night shift"). The opposite-style counterfactual: rewritten as "the study's practical implication rests on an unmeasured utility premise and an untested distributional assumption about barrier type," the substance is identical and the weight would be identical. Weight assigned on substance; informality carried no penalty.
- **SC-8 / SC-9 (R1).** These arrive with named concepts (attenuation bound, polyserial, Fisher-*z*). Technical specificity was **not** credited as corroboration: SC-8 gains weight because R1 supplies a checkable inequality and a reconstruction of the paper's own reported quantities, not because it names psychometric machinery. SC-9 is scored as a single-reviewer finding despite its precision, exactly as SC-17 is scored as a single-reviewer finding despite its plainness.

No sub-claim was marked unevaluable; every position above is legible enough to place.

#### Consensus Dispositions (denominator = 4 non-DA reviewers; precedence rule 1 applied first)

| sub_claim_id | agree | conflict | silent | Disposition |
|--------------|-------|----------|--------|-------------|
| SC-1a | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-1b | 1 (R2) | 3 (EIC, R1, R3) | — | **[SPLIT-A]** |
| SC-2 | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-3 | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-4 | 2 (R1, R2) | 0 | EIC, R3 | corroborated finding |
| SC-5 | 3 (EIC, R2, R3) | 0 | R1 | **[CONSENSUS-3]** (silent: R1) |
| SC-6 | 2 (EIC, R2) | 0 | R1, R3 | corroborated finding |
| SC-6b | 1 (R2) | 1 (EIC) | R1, R3 | **[SPLIT-B]** |
| SC-7 | 1 (R1) | 0 | EIC, R2, R3 | single-reviewer finding (conf 4) |
| SC-8 | 1 (R1) | 0 | EIC, R2, R3 | single-reviewer finding (conf 4) |
| SC-9 | 1 (R1) | 0 | EIC, R2, R3 | single-reviewer finding (conf 4) |
| SC-10 | 2 (EIC, R1) | 0 | R2, R3 | corroborated finding |
| SC-11 | 3 (EIC, R1, R2) | 0 | R3 | **[CONSENSUS-3]** (silent: R3) |
| SC-12 | 3 (R1, R2, R3) | 0 | EIC | **[CONSENSUS-3]** (silent: EIC) |
| SC-13 | 3 (EIC, R1, R3) | 0 | R2 | **[CONSENSUS-3]** (silent: R2) |
| SC-14 | 3 (EIC, R1, R3) | 0 | R2 | **[CONSENSUS-3]** (silent: R2) |
| SC-15 | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-16 | 3 (EIC, R2, R3) | 1 (R1) | — | **[SPLIT-C]** |
| SC-17 | 1 (R3) | 0 | EIC, R1, R2 | single-reviewer finding (conf 4) |
| SC-18 | 1 (R3) | 0 | EIC, R1, R2 | single-reviewer finding (conf 4) |
| SC-19 | 1 (R3) | 0 | EIC, R1, R2 | single-reviewer finding (conf 4) |
| SC-20 | 4 | 0 | — | **[CONSENSUS-4]** |
| SC-21 | 2 (R1, R3) | 1 (EIC) | R2 | **[SPLIT-D]** |
| SC-22 | 2 (EIC, R2) | 0 | R1, R3 | corroborated finding |
| SC-23 | 1 (R1) | 0 | EIC, R2, R3 | single-reviewer finding (conf 4) |
| SC-24 | 1 (EIC) | 0 | R1, R2, R3 | single-reviewer finding (conf 4) |

#### Points of Agreement (Consensus)

- **[CONSENSUS-4] SC-1a** — The manuscript measures self-reported weekly access frequency (§3.2), reports it as "use" (§4, §5, §7), and calls it "engagement" in the Abstract's opening and closing sentences and in §2 and §4. No passage defends the substitution. All four non-DA reviewers propose the *same* remedy: one consistent label — "self-reported access frequency" — or an explicit defence of the broader reading. R2 grounds the objection on the multidimensional definition of engagement (Fredricks, Blumenfeld & Paris, 2004); EIC, R1, and R3 reach the same conclusion independently. R3 flags rather than asserts, allowing that the usage might be a field convention — that is a confidence qualifier on the same position, not opposition.
- **[CONSENSUS-4] SC-2** — §3.1 states that all enrolled undergraduates were eligible and reports 233 received / 214 analysed, but never the population denominator, so no response rate exists and representativeness is unassessable in either direction.
- **[CONSENSUS-4] SC-3** — The six perceived-usefulness items and the verbatim use item are reproduced nowhere and the adaptation of Costa and Wren (2019) is undocumented, so α = .88 cannot be set against the source instrument and no independent group can administer the measure.
- **[CONSENSUS-4] SC-15** — Year level was collected (§3.1), is endorsed as theoretically relevant via Ibarra and Poll (2021) in §2, is the population §5's onboarding implication targets, and is never analysed or even tabulated. All four call for the breakdown; all four note it costs no new data.
- **[CONSENSUS-4] SC-20** — The setting is described as "one mid-sized public university" and little else: no platform named, no disciplinary mix, no delivery mode, no term or window, no institutional platform-maturity context. For a paper whose declared value is comparability, each is a clause.
- **[CONSENSUS-3] SC-5** (silent: R1) — The contribution claim — "an incremental data point, comparable with prior work," "one point in a distribution" — is asserted at three places and substantiated at none: §2 says effect sizes "vary across samples and instruments" and reports no effect size; §5 and the Abstract say the result is "consistent with prior technology-acceptance research" and name no coefficient it is consistent with.
- **[CONSENSUS-3] SC-13** (silent: R2 — who explicitly assigns the sampling-frame audit to the institutional-research seat) — Recruitment ran through the institution's course-announcement channel, which §1's own description of what an LMS hosts suggests is inside the platform under study. §6 concedes generic volunteer bias; the panel's concern is narrower and sharper — selection on the dependent variable's own subject matter, plausibly truncating the low-use tail over which the correlation is estimated.
- **[CONSENSUS-3] SC-14** (silent: R2) — §3.1's removal of 5 duplicate entries and §3.3's statement that no identifying information was collected and responses could not be linked to individuals cannot both be complete without a stated deduplication rule. All three raising reviewers are explicit that this is a reporting-completeness finding, not an ethics allegation.
- **[CONSENSUS-3] SC-12** (silent: EIC) — Only a median category is reported for the five-point use item; no category frequencies, no dispersion, no composite *SD*. This is what a reader would need to judge range restriction and what a future synthesis would need to pool.
- **[CONSENSUS-3] SC-11** (silent: R3) — "The proportion of variance shared by the two measures was accordingly modest" states the paper's most deflationary quantity in words only. It is .18.

Corroborated findings (2/4, no conflict): SC-4, SC-6, SC-10, SC-22. Single-reviewer findings (1/4, no conflict): SC-7, SC-8, SC-9 (R1); SC-17, SC-18, SC-19 (R3); SC-23 (R1); SC-24 (EIC).

#### Points of Disagreement

**Disagreement 1 (SPLIT-A): Is the construct substitution blocking or revisable?**

- **R2 view**: D2 `block`. "A construct is defined or operationalised in a way that contradicts its accepted meaning in the field, and that misdefinition propagates into the paper's conclusions." The propagation reaches the Abstract's terminal sentence, the manuscript's most-read claim surface. The DA concurs from outside the count, on a trigger it pre-committed to blind in Phase 1.
- **EIC / R1 / R3 view**: D2 `warn`. EIC: "domain slippage that is real but not invalidating," since the paper's association claim survives the correction. R1 and R3 each record that their block triggers were considered and did not fire.
- **Disagreement type**: Severity disagreement (existence and remedy are unanimous).
- **Editor's Resolution**: R2's and the DA's classification stands and is decisive for the contract arithmetic — F1 fires and governs. The dissenting seats' point is nonetheless preserved and load-bearing for the *letter's* decision within F1's range: because the association claim survives the correction, the repair is a wording and defence task, not a redesign, which is why this is Major Revision rather than Reject.
- **Resolution Rationale**: Expertise-first — the construct's accepted meaning in higher-education research is R2's primary domain, and R2 grounds the objection on an external, checkable definitional source rather than on reviewer preference. Evidence-first — the DA reached the identical trigger independently and pre-committed to it before seeing the manuscript, which materially reduces the risk of post-hoc severity inflation. Conservative principle — where seats split on severity, the author responds to the higher classification. No seat argues the defect is absent, and no two seats propose incompatible remedies.

**Disagreement 2 (SPLIT-B): Is the missing primary literature base blocking or attribution slippage?**

- **R2 view**: D2 `block` trigger 1. §2 attributes the canonical perceived-usefulness definition to Costa & Wren (2019) and Delgado (2020); no primary acceptance source and no quantitative synthesis appears among six references, so the paper's own comparability claim "rests on a literature base that contains no distribution." Grounded on APA 7 §8.6 (cite the original; reserve secondary citation for unavailable originals) and on the manuscript's own §2 commitment.
- **EIC view**: D2 `warn`. The same fact is "attribution slippage rather than misdefinition"; the comparability claim is "real, but not load-bearing, since the paper's finding stands independently of whether it matches a benchmark."
- **Silent**: R1 (out of scope by his own restriction of D2 to methodological/psychometric terminology); R3 (explicitly defers lineage — "that is another reviewer's territory").
- **Disagreement type**: Severity disagreement.
- **Editor's Resolution**: Both are right about different objects, and the split resolves by separating them. EIC is right that the *finding* — r = .42 with its interval — stands without a benchmark; that is why the citation repair sits at Priority 2 (item S2). R2 is right that the *contribution claim* does not stand without one; that claim's repair sits at Priority 1 (item R7) and is a Top Blocking Issue. The author must do both, and the paper's stated value proposition rides on the P1 half.
- **Resolution Rationale**: Expertise-first (domain seat on domain literature) combined with evidence-first: R2's severity rests on an external standard plus an internal inconsistency with the manuscript's own §2 claim, which is stronger than a general appeal to citation breadth. EIC's narrower reading is not overturned — it is what determines that the *citation* fix is P2 while the *claim* fix is P1.

**Disagreement 3 (SPLIT-C): Does the §5 onboarding implication over-reach?**

- **EIC / R3 / R2 view**: EIC — the sentence "will be extracted and quoted to a resourcing committee," and a cross-sectional association with an explicitly reversible direction licenses no prediction about what an onboarding intervention would change. R3 — a triple-hedged sentence loses its hedges when it travels into a budget proposal; reframe as a testable hypothesis. R2 (D4 `warn`) — the one implication offered to an adjacent audience rests on a citation rather than on these data.
- **R1 view (disputed)**: The implication "is hedged three times and attributed to a practitioner source rather than to these data, so it does not amount to an interventionist recommendation" — i.e. as written, no defect.
- **Disagreement type**: Existence disagreement, with a perspective component (R1 evaluates what the text asserts; R3 and EIC evaluate what the text will be used for).
- **Editor's Resolution**: Sustain the majority, with R1's observation preserved. The required change is **reframing, not retraction**: state the implication as a hypothesis a pre-post or quasi-experimental design could test, and reconcile it in the same edit with §5's own concession that the reverse pathway is "equally consistent with the data" (the DA's M2 makes the logical incompatibility explicit: if the directions are genuinely co-equal, the correlation supplies no directional warrant, and a hedge softens the assertion without reconciling that). Item R11.
- **Resolution Rationale**: Evidence-first. R1's claim is narrowly correct — the sentence as written is not an overclaim on its face — and nothing in the resolution contradicts it, which is why deletion is not required. But three seats identify a defect R1's test does not reach: the warrant is a citation rather than these data, and the logical tension with the reverse-pathway concession two sentences earlier is internal to the manuscript and independent of how heavily the sentence is hedged. Conservative principle applies: the author responds rather than the concern being dismissed.

**Disagreement 4 (SPLIT-D): Is the absence of any table or figure a defect?**

- **R1 / R3 view**: R1 — the scatterplot inspection asserted in §3.4 is not shown, the outcome's category distribution is invisible, the year-level composition is untabulated, and no availability statement exists; one descriptive table closes all of it. R3 — a table would let an outside reader see the shape of the data rather than only its summary.
- **EIC view (disputed)**: D5 `pass`. "Given a single bivariate result reported inline with full statistics, none is required — the finding is fully extractable from §4."
- **Silent**: R2.
- **Disagreement type**: Severity disagreement over format, resting on agreement about content.
- **Editor's Resolution**: The disputed object dissolves once content and container are separated. The *content* R1 and R3 want visible is already required elsewhere and unanimously or near-unanimously so — category frequencies and dispersion under R5 (SC-12), year-level distribution under R9 (SC-15), context descriptors under R10 (SC-20). Whether the author delivers it as a descriptive table or as in-text reporting is left to author discretion (author-autonomy principle); a table is recommended, not required. The uncontested half — a data, materials, and code availability statement (R1 only, D1 reproducibility trigger) — is required as item S9.
- **Resolution Rationale**: EIC is correct that a figure is not required to make a single bivariate finding extractable, and that judgment is squarely within the editor's remit on venue convention. R1 and R3 are correct that the underlying quantities must become visible. Nothing is lost by mandating the content and leaving the container free, and mandating a format no seat argued was necessary would be manufacturing a requirement.

#### DA-CRITICAL Issues

**DA-C1 — Unhedged construct substitution in the headline claim** (Dimension 4, Logic Chain / Data–Conclusion Mismatch; Abstract final sentence, §2 ¶1, §4 ¶2, §3.2).

- **The DA's argument**: The measured quantity is a single item on self-reported weekly access frequency. It is relabelled "use" throughout and "LMS engagement" in the Abstract's terminal sentence — a construct the study contains no measure of. The manuscript defends the self-report↔behaviour substitution at three separate points and never once defends this one. "The humility is concentrated on the axis where the paper is already safe." The DA records that this was its pre-committed, paper-blind D2 block trigger, and that it passed both its own surface-form parity gate and its field-norm gate (the multidimensional engagement construct; the learning-analytics distinction the manuscript itself invokes via Vasquez, 2020).
- **Corroboration by other reviewers**: All four. EIC (W3), R1 (D2), R2 (W2, D2 `block`), R3 (Assumption Audit, D2). This is the panel's single strongest convergence and it is the only defect on which two seats reached `block` independently.
- **EIC's assessment of validity**: Sustained in full. The finding is grounded in the manuscript's own text (§3.2 against the Abstract), the substitution is nowhere defended or limited, and the term "engagement" — unlike "perceived usefulness," which §2 defines carefully — is never defined in the paper at all (DA m4). The DA's observation that the defect sits in the sentence most likely to be read in isolation is an aggravating factor the editor accepts.
- **Required author response**: Mandatory, via roadmap item R1. Either use one label consistently throughout ("self-reported access frequency") or defend the broader reading explicitly with a stated limitation. A response is required even where the author disagrees.

The DA's MAJOR findings map onto sub-claims already carried by the roadmap and require no separate items: M1 → SC-5 + SC-3 (R7, R6); M2 → SC-16 (R11); M3 → SC-13 + SC-2 (R4, R2); M4 → SC-14 (R3); M5 → SC-7 (R8). The DA's "unexamined premise" — that the paper presupposes its correlation is a transportable quantity, when a correlation is a function of the retained items, the response-scale coarseness, the sample's range, the mandate regime, and the platform — is recorded as the DA's framing of SC-5 and should be addressed within R7 rather than as a separate requirement.

### Decision Rationale

The contract's F1 condition fires: two of five seats (R2, DA) score the mandatory dimension D2 `block`, and both do so on the same defect — the undefended slide from measured access frequency to "LMS engagement" in the Abstract's terminal sentence. F2 also fires, unanimously and comfortably: every seat scores all three mandatory dimensions at `warn` or worse. Severity precedence gives F1's action, and within that action's range the decision is Major Revision rather than Reject on the panel's own evidence — R2 and the DA, the two blocking seats, each state in writing that the defect is closable in a revision round without new data collection.

This is not a decision about study quality. The panel is unusually united in praising what the manuscript does well: causal discipline held across §1, §2, §5, §6 and §7; a source cited against its own instrument; an a priori sensitivity statement used in the correct direction; an estimate R1 independently reconstructed from the reported coefficient and *n*. None of that should be revised away, and none of the required work asks for a larger study.

The decision turns on warrant and reporting. The manuscript's declared value is a poolable estimate, and it withholds every input pooling requires — denominator, response rate, instrument adaptation, comparator magnitudes, platform, discipline mix, mandate regime — while naming its measured quantity with a construct it did not measure. Where the seats split, the splits resolved without overturning any seat: EIC's narrower severity reading determines that the *citation* repair is P2 while the *claim* repair is P1 (SPLIT-B); R1's correct observation that §5 is hedged determines that the implication is reframed rather than deleted (SPLIT-C); EIC's judgment that a figure is not required determines that the content is mandated and the container left free (SPLIT-D). Every required item is available within the existing dataset and word count, with one exception — an outcome reliability estimate — for which an explicit statement of the attenuation constraint is accepted in its place.

---

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. A DA-CRITICAL or non-decomposed item uses `—`.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Source | Severity | Section | Priority | Estimated Effort |
|---|--------------|--------------|--------|----------|---------|----------|-----------------|
| R1 | Use one construct label consistently — "self-reported access frequency" — or defend the broader reading explicitly as a stated limitation | SC-1a | EIC, R1, R2, R3 + DA-C1 | Critical | Abstract, §2, §4, §5, §7 | P1 | 0.5 day |
| R2 | Report the eligible undergraduate population size and the response rate (AAPOR-style disposition if tracked); if dispositions were not tracked, say so explicitly | SC-2 | EIC, R1, R2, R3 | Critical | §3.1 | P1 | 0.5 day |
| R3 | State the deduplication criterion and reconcile it with §3.3; if a quasi-identifier was used, say so and distinguish anonymity from de-identification | SC-14 | EIC, R1, R3 (+DA M4) | Critical | §3.1, §3.3 | P1 | 0.5 day |
| R4 | State whether the course-announcement channel is delivered inside the LMS under study; if so, name the resulting structural selection in §6 in place of the current generic volunteer-bias wording | SC-13 | EIC, R1, R3 (+DA M3) | Critical | §3.1, §6 | P1 | 1 day |
| R5 | Report the use item's full frequency distribution across all five categories, its interquartile range, and the composite's observed *SD* | SC-12 | R1, R2, R3 | Major | §4 | P1 | 0.5 day |
| R6 | Reproduce the six perceived-usefulness items and the verbatim use item in an appendix, and state every modification made to Costa and Wren's (2019) items and why | SC-3 | EIC, R1, R2, R3 (+DA M1) | Critical | §3.2, Appendix | P1 | 1 day |
| R7 | Substantiate the comparability claim: report the range of prior coefficients with their outcome operationalisations, state the specific gap this estimate fills, and carry that statement into §2 and §7 | SC-5 | EIC, R2, R3 (+DA M1) | Critical | §2, §5, §7, Abstract | P1 | 3 days |
| R8 | Add measurement candour on both directions at once: state the attenuation constraint imposed by the single-item outcome's unknown reliability with a disattenuation sensitivity range under explicitly assumed values, and add common-method variance as a distinct threat with its opposite expected direction | SC-7, SC-8 | R1 (conf 4; elevated on expertise weighting — see note) | Major | §3.4, §6 | P1 | 2 days |
| R9 | Report the association by year level (or with year level partialled out) as a clearly labelled exploratory analysis, and give the year-level distribution of the sample | SC-15 | EIC, R1, R2, R3 (+DA m6) | Major | §3.1, §4 | P1 | 1 day |
| R10 | Add the context descriptors transferability requires: LMS platform and its institutional tenure/maturity, disciplinary composition, delivery mode, country/system, academic term and whether the window sat inside an assessment period | SC-20 | EIC, R1, R2, R3 | Major | §3.1 | P1 | 0.5 day |
| R11 | Reframe the §5 onboarding implication as a hypothesis a pre-post or quasi-experimental design could test, and reconcile it in the same edit with §5's own "equally consistent" reverse-pathway concession | SC-16 | EIC, R2, R3 (SPLIT-C arbitrated; R1 dissenting) (+DA M2) | Major | §5 | P1 | 1 day |

**Note on R8**: SC-7 and SC-8 are single-reviewer findings (R1, confidence 4) that the other three seats did not address — R3 explicitly defers statistical validity to the methodology seat. They are placed at Priority 1 under the Confidence Score Weighting rule (expertise-first: the methodology seat, within its primary domain, on the paper's only substantive interpretive claim), not under a consensus label. The two are combined into one item because R1's own position is that stating either bias alone is misleading: attenuation pushes the coefficient down, common-method variance pushes it up, and the point estimate is bracketed by both.

### Required Item Details

**R1: Construct label**
- **Problem**: §3.2 measures how often a respondent accessed the LMS in a typical week. §4, §5 and §7 report this as "use"; the Abstract's opening and closing sentences and §2 and §4 call it "engagement." The substitution is nowhere defended, and "engagement" is never defined in the manuscript.
- **Source**: DA C1 (CRITICAL, pre-committed blind trigger); EIC W3; R2 W2 (grounded on Fredricks, Blumenfeld & Paris, 2004); R1 D2; R3 Assumption Audit.
- **Requirement**: Replace "engagement" with "self-reported access frequency" (or "self-reported LMS use") wherever the manuscript refers to its own measured quantity — the Abstract's first and last sentences included. If the broader reading is intended as a claim, defend it explicitly in the body and add the gap to §6 as a named limitation.
- **Acceptance criteria**: No sentence in the manuscript attributes to these data a construct broader than what §3.2 operationalises, or every such sentence carries an explicit, sourced defence plus a limitation.

**R2: Sampling frame**
- **Problem**: §3.1 reports 233 received and 214 analysed with no denominator; representativeness is unassessable in either direction, and R1 notes the statistical consequence — range restriction on the outcome cannot be evaluated.
- **Source**: EIC W2/Q1; R3 W1/Q1; R1 W4/Q4; R2 W4(c).
- **Requirement**: Report the eligible undergraduate population size and the response rate. If dispositions were not tracked, state that explicitly rather than omitting the denominator.
- **Acceptance criteria**: A reader can compute what fraction of the eligible population the 214 represent, or knows exactly why they cannot.

**R3: Deduplication rule**
- **Problem**: §3.1 removes 5 duplicate entries; §3.3 states no identifying information was collected and responses could not be linked to individuals. Both cannot be complete without a stated rule.
- **Source**: EIC Q3; R1 Data Collection/Q6; R3 W1/Q3; DA M4.
- **Requirement**: State the criterion in one sentence (IP, session token, device fingerprint, or a response-pattern rule). If a quasi-identifier was used, say so and reconcile §3.3 by distinguishing anonymity from de-identification.
- **Acceptance criteria**: §3.1 and §3.3 are mutually consistent on the page; the anonymity claim is stated at the strength the procedure actually supports.

**R4: Recruitment channel**
- **Problem**: §1 lists announcements among what an LMS hosts; §3.1 recruited through the institution's course-announcement channel. If that channel is LMS-delivered, the sampling instrument sits inside the subject matter and the students least likely to see the invitation are the low-frequency users anchoring the low end of both variables. §6 describes only generic volunteer bias.
- **Source**: EIC Q2; R3 W2/Q2; R1 W4; DA M3.
- **Requirement**: Confirm the channel's relationship to the LMS either way. If it is LMS-delivered, replace §6's fourth limitation with a statement of the structural selection mechanism and its bearing on the low tail; if a second, LMS-independent route was or could be used, say so.
- **Acceptance criteria**: §6 names the specific mechanism rather than generic voluntary response, and the direction of its expected effect on the estimate is stated.

**R5: Outcome distribution**
- **Problem**: §4 reports only a median category for a five-point item; neither the frequencies, the interquartile range, nor the composite's *SD* appears, so the range over which the correlation was estimated is invisible.
- **Source**: R1 W4/Q4; R2 W5; R3 Minor Issues.
- **Requirement**: Report all five category frequencies, the IQR, and the composite's observed *SD*.
- **Acceptance criteria**: A reader can see whether the low-use tail is thin, and a future synthesis can reconstruct the outcome's distribution. (Delivery as a table or in text is the author's choice — see SPLIT-D.)

**R6: Instrument reproduction and adaptation record**
- **Problem**: The six items and the verbatim use item are reproduced nowhere and the adaptation is undocumented, so α = .88 cannot be compared with the source, the measure cannot be re-administered, and the "previously validated" warrant has no anchor.
- **Source**: EIC W2/Q4; R1 W3/Q5; R2 W3/Q1; R3 Minor Issues; DA M1.
- **Requirement**: Reproduce all six items and the verbatim use item in an appendix or supplement, and state every modification to the source items — wording, count, referent, response format — and its rationale.
- **Acceptance criteria**: A second group could administer the identical instrument from the manuscript alone, and α = .88 can be placed against the source instrument's coefficient.

**R7: Locate the contribution**
- **Problem**: The paper's whole value proposition is comparability — "comparable with prior work," "one point in a distribution" — and it reports no prior magnitude, never characterises prior studies' outcome operationalisations, and never states which gap in the distribution this estimate fills. "Consistent with prior technology-acceptance research" is therefore unevaluable.
- **Source**: EIC W1/W4/Q6 (his principal editorial reservation); R2 W4/Review Body; R3 Strength 2 and Minor Issues; DA M1 and Unexamined Premise.
- **Requirement**: Report the range of prior coefficients with the outcome operationalisation each used; state in two to three sentences at the end of §2 what population, institutional or platform condition, or instrument condition this estimate adds that the existing distribution does not represent; carry that claim into §7. Either anchor "consistent with" to the reported range or replace it with a statement of what the estimate is being compared against. The DA's transportability premise — that a correlation is not instrument-independent — should be addressed here as a stated boundary on poolability.
- **Acceptance criteria**: A reader can judge whether r = .42 is typical, high, or low for this construct pair, and can say what they now know that they did not before.

**R8: Measurement candour in both directions**
- **Problem**: §6 treats the single-item outcome purely as a validity problem (divergence from logs) and never as a reliability problem. An observed correlation is bounded by the geometric mean of the two reliabilities; with the predictor at α = .88, essentially the whole constraint sits on an outcome whose reliability is unknown. R1 illustrates that at assumed outcome reliabilities of .70 and .50 the disattenuated coefficient would be ≈ .54 and ≈ .63, so the label "moderate" — the paper's only substantive interpretive claim, appearing in the Abstract, §4, §5 and §7 — is unstable in a direction never discussed. Running the other way, common-method variance is never named although both variables came from one respondent, one instrument, one sitting, one response format.
- **Source**: R1 W1, W5, Q1, Q8 (conf 4); DA M5 corroborates the common-method half at MAJOR.
- **Requirement**: Either supply a defensible reliability estimate for the outcome (a short test–retest sub-sample or a two-to-three-item use measure), or state the attenuation constraint explicitly in §3.4 and §6, report a disattenuation sensitivity range under stated assumed reliabilities, and describe the coefficient as a lower bound on the disattenuated association rather than as a point characterisation. Add one paragraph to §6 naming common-method variance as a threat distinct from the self-report-versus-logs concern, with its expected direction stated relative to the attenuation.
- **Acceptance criteria**: The manuscript states both biases, states that they run in opposite directions, and no longer characterises the coefficient's magnitude as if the point estimate were unbracketed.

**R9: Year-level analysis**
- **Problem**: Year level was collected, is endorsed as theoretically relevant via Ibarra and Poll (2021), is precisely the population §5's onboarding implication targets, and is never used or tabulated.
- **Source**: EIC W5/Q5; R1 W5/Q7; R2 Q5; R3 W5/Q4; DA m6.
- **Requirement**: Report the association by year level, or with year level partialled out, as a clearly labelled exploratory analysis, and give the sample's year-level distribution in §3.1.
- **Acceptance criteria**: The §5 implication can be read against evidence about the group it targets, or the manuscript states why the breakdown was not run.

**R10: Context descriptors**
- **Problem**: "One mid-sized public university" is nearly the entire context statement; no reader elsewhere can judge transfer, and the estimate cannot be placed on any axis of the distribution §2 invokes.
- **Source**: EIC W2/Minor Issues; R2 W4(c)/Q4; R3 Minor Issues; R1 D4.
- **Requirement**: Name the LMS platform and how long it has been in place, the disciplinary composition of respondents, the delivery mode, the country/system, the academic term and year, and whether the survey window sat inside an assessment period. If any is withheld, state why.
- **Acceptance criteria**: A reader at another institution can say which conditions this estimate is conditional on.

**R11: Reframe the practice implication**
- **Problem**: §5 states the reverse pathway is "equally consistent with the data" and, two sentences later, suggests onboarding that surfaces concrete usefulness may be worth institutional attention — supported by Whitfield (2019) rather than by these data. If the directions are genuinely co-equal, the correlation supplies no directional warrant, and the triple hedge softens the assertion without reconciling the incompatibility.
- **Source**: EIC W5; R3 Implementation feasibility; R2 D4; DA M2. R1 dissents (the sentence is not, as written, an interventionist recommendation) — arbitrated at SPLIT-C.
- **Requirement**: State the implication as a hypothesis a pre-post or quasi-experimental design could test, name what such a study would need to establish, and reconcile the sentence with the reverse-pathway concession in the same edit. Deletion is not required.
- **Acceptance criteria**: A practitioner reading §5 in isolation learns what study to commission, not what programme to fund.

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Source | Priority | Section | Expected Improvement |
|---|--------------|--------------|--------|----------|---------|---------------------|
| S1 | Narrow "previously validated instrument" to "items adapted from a previously validated instrument, with the adapted form's structure not re-examined here," or add in-sample structural evidence (a one-factor confirmatory model, feasible at n = 214) | SC-4 | R1, R2 (corroborated) | P2 | Abstract, §2, §3.2 | The validity claim matches the evidence actually held |
| S2 | Cite the perceived-usefulness construct's primary source for the §2 definition, and add at least one meta-analytic or systematic-review anchor; retain Costa and Wren (2019) as what it is, the instrument source | SC-6 | EIC, R2 (corroborated; SPLIT-B arbitrated) | P2 | §2, References | Attribution is correct and R7's benchmark has a locatable referent |
| S3 | State how the 95% CI was derived and what distributional assumption that method makes about a five-category variable; add a distribution-free (BCa bootstrap) interval alongside it | SC-10 | EIC, R1 (corroborated) | P2 | §3.4, §4 | The reported precision is checkable and robust to the categorisation |
| S4 | Either promote the rank-based or polyserial estimate to primary or justify in one sentence why Pearson is primary given §3.2's ordinal declaration; report ρ with its own interval and *p*; narrow §4's claim that r/ρ agreement shows independence from the parametric assumption | SC-9 | R1 (single-reviewer, conf 4); DA m2 | P2 | §3.2, §3.4, §4 | The declared measurement level and the foregrounded statistic stop pointing in opposite directions |
| S5 | State explicitly the premise that increased LMS access frequency is worth institutional resource, and either defend it or bound it; note the competing reading that high frequency may indicate a poorly organised environment | SC-17 | R3 (single-reviewer, conf 4) | P2 | §1, §5 | The practical implication's load-bearing assumption becomes visible and arguable |
| S6 | Add access and digital-literacy variation as a named boundary condition, and note that instructor and course-design practice is a plausible driver of access variance that this student-level design holds constant | SC-18 | R3 (single-reviewer, conf 4); DA Missing Stakeholders | P2 | §5, §6 | The onboarding implication's distributional assumption is stated rather than assumed |
| S7 | Name voluntary-versus-mandated use as a boundary condition on how an acceptance construct should be read at this institution | SC-19 | R3 (single-reviewer, conf 4); DA m5 | P2 | §2, §6 | Readers can tell what kind of behaviour is being explained |
| S8 | Carry §6's four limitations into §7 with a one-sentence bridge, so the conclusion is stated under the constraints the paper concedes | SC-24 | EIC (single-reviewer, conf 4) | P2 | §6, §7 | The conclusion inherits the pressure the limitations exert |
| S9 | Add a data, materials, code, and supplementary-availability statement | SC-21 (uncontested half) | R1 (single-reviewer, conf 4) | P2 | End matter | Moves reproducibility reporting from inadequate to adequate at no analytic cost |

### Priority 3 — Text and Formatting

| Item | Sub-Claim(s) | Source |
|------|--------------|--------|
| Report r² numerically (.18) rather than characterising it as "modest" | SC-11 | EIC, R1, R2 (CONSENSUS-3; cosmetic in kind, hence P3) |
| Carry the 95% CI into the Abstract alongside r = .42, matching the body's reporting standard | SC-22 | EIC, R2 |
| APA 7 statistical formatting: `N` for the total analysed sample, `M =` notation, two decimals for *M* and *SD*, `r(212) = .42`, α and ≥ as symbols, ρ with its interval and *p* | SC-23 | R1 |
| Give the source instrument's reliability coefficient rather than "strong internal consistency" | — | R2 (Minor) |
| Name the software and settings behind the sensitivity statement, or restate the floor as r ≥ .20 (power reconstructs to ≈ .798 or ≈ .802 depending on the variance convention) | — | R1 (Minor) |
| Optional: a single descriptive table (composite *M*/*SD*/range; use-item frequencies by category; year-level *n*) — recommended, not required, per SPLIT-D | SC-21 | R1, R3 (EIC dissenting) |
| Once R7 lands, align the Abstract's "consistent with prior technology-acceptance research" with the body's framing | SC-5 | R3 (Minor) |

### Revision Checklist

#### Priority 1 — Structural Revisions (estimated total effort: 11.5 days)
- [ ] R1: One construct label throughout; Abstract's first and last sentences included
- [ ] R2: Eligible population size and response rate
- [ ] R3: Deduplication rule stated and reconciled with §3.3
- [ ] R4: Recruitment channel's relation to the LMS named; §6 rewritten to the specific mechanism
- [ ] R5: Full five-category frequency distribution, IQR, composite *SD*
- [ ] R6: Six items and verbatim use item reproduced; every adaptation documented
- [ ] R7: Prior coefficient range reported; the gap this estimate fills stated in §2 and §7
- [ ] R8: Attenuation constraint with sensitivity range, plus common-method variance and its opposite direction
- [ ] R9: Year-level association reported as exploratory; year-level distribution given
- [ ] R10: Platform, maturity, discipline mix, delivery mode, system, term and window
- [ ] R11: §5 implication reframed as a testable hypothesis and reconciled with the reverse-pathway concession

#### Priority 2 — Content Supplementation (estimated total effort: 5 days)
- [ ] S1: "Previously validated" narrowed, or in-sample structural evidence added
- [ ] S2: Primary construct source plus a quantitative synthesis cited
- [ ] S3: CI derivation stated; bootstrap interval added
- [ ] S4: Estimator ordering justified or reordered; ρ reported with interval and *p*; §4's robustness claim narrowed
- [ ] S5: "More use is better" premise stated and bounded
- [ ] S6: Access/digital-literacy variation and the instructor/course-design lever named as boundary conditions
- [ ] S7: Voluntary-versus-mandated use named as a boundary condition
- [ ] S8: §6 limitations carried into §7
- [ ] S9: Data, materials, code availability statement added

#### Priority 3 — Text and Formatting (estimated total effort: 1 day)
- [ ] r² reported as .18
- [ ] 95% CI carried into the Abstract
- [ ] APA 7 statistical formatting pass
- [ ] Source instrument's reliability coefficient given
- [ ] Sensitivity-statement software/settings named, or floor restated as r ≥ .20
- [ ] Optional descriptive table (author's discretion)
- [ ] Abstract's "consistent with" wording aligned with the revised body

### Total Estimated Effort

Approximately 17–18 working days, of which R7 (locating the contribution) and R8 (measurement candour) carry the analytic load. Every other Priority 1 item is reporting the authors already hold or an analysis on data already collected. The single item that may require new collection is the outcome reliability estimate in R8; an explicit statement of the attenuation constraint with a stated sensitivity range is accepted in its place.

### Revision Deadline

- **Recommended deadline**: 2026-09-19 (8 weeks)
- **Basis**: Major Revision — 6–8 weeks; the upper bound is set because R7 requires locating and reporting prior coefficients with their operationalisations, which is a literature task rather than an editing task.
- **Extension policy**: Notify the editorial office one week before the deadline if an extension is needed.
- **Re-review**: The revised manuscript will undergo another round of review.

### Response Letter Instructions

Please use the format in `templates/revision_response_template.md` to respond to every item above, comment by comment.

**Must include**:
1. A response and revision description for each Required Revision (R1–R11)
2. A response for each Suggested Revision (S1–S9) — adopted, or the reason for not adopting
3. A response to DA-C1 specifically, even if you disagree with the finding
4. Change markup (colour or tracked changes) throughout the revised manuscript
5. A cross-reference table of new page and paragraph numbers

Two items carry particular response obligations. **R1 (DA-C1, CONSENSUS-4)** admits no "respectfully decline" option: either the label changes or the broader reading is defended in the body with a stated limitation. **R11** was arbitrated over a dissent from Reviewer 1, who held that the §5 sentence is adequately hedged as written; your response should engage the arbitrated requirement (reframing plus reconciliation with the reverse-pathway concession) rather than the underlying dispute.

### Recorded, Not Adjudicated

All five seats independently recorded that the six references carry DOIs in the `10.5555/` reserved prefix range with sequential suffixes, and all five explicitly declined to adjudicate it, routing the question to the deterministic citation-verification layer. No dimension score, no failure condition, and no roadmap item in this package rests on that flag, and every literature-related finding above concerns what the manuscript does with the sources as described — it holds regardless of how verification resolves. The editorial office will run the verification layer separately.

All five seats also ran an integrity check and reported the same result: the manuscript contains no text addressed to reviewers, no directives, and no attempt at instruction injection. Recorded for completeness.

### Closing

We encourage you to consider the reviewers' comments carefully and to submit a substantially revised manuscript. Please note that the revised manuscript will undergo another round of review.

The panel's assessment of this work is more favourable than the length of this roadmap suggests, and it is worth saying plainly. Five independent reviewers — including one whose seat exists to attack the manuscript — used almost identical language about its epistemic conduct: the causal discipline is real, it is held across every load-bearing section, and it should survive revision untouched. Two reviewers reconstructed your reported statistics independently and both succeeded. Nothing in this letter asks you to unlearn a result, redo an analysis, or write a larger study; the narrowness declared in §1 is a design choice the panel accepted without reservation.

What the manuscript needs is to say what it adds, report what it already knows, and stop using one word it has not earned.

---

## Part 3: Reviewer Report Summary (Appendix)

### EIC Report Summary
- Recommendation: Major Revision | Confidence: 4 | Dimension scores: D1 warn, D2 warn, D3 warn, D4 warn, D5 pass | Self-reported fired: F2
- Key Point: The manuscript is sound and dishonest about nothing, but not yet warranted — it claims to supply a poolable point estimate while withholding the denominator, the platform and context, and the instrument adaptation that would make it locatable, and it lets "engagement" appear in the Abstract's most-read sentence.

### Reviewer 1 (Methodology) Summary
- Recommendation: Major Revision | Confidence: 4 | Dimension scores: D1 warn, D2 warn, D3 warn, D4 warn, D5 warn | Self-reported fired: F2
- Key Point: The reporting is verifiable and better than typical — the interval and test statistic reconstruct from r and n, and the sensitivity statement is used in the correct direction — but the headline coefficient is bracketed by two unacknowledged biases running in opposite directions (attenuation from an unreliable single-item outcome, inflation from common-method variance), and the estimator ordering contradicts the paper's own declaration that the outcome is ordinal.

### Reviewer 2 (Domain) Summary
- Recommendation: Major Revision, within the `reject_or_major_revision` action | Confidence: 4 | Dimension scores: D1 warn, **D2 block**, D3 warn, D4 warn, D5 warn | Self-reported fired: F1, F2
- Key Point: Two independent D2 block triggers fire — the reference base contains no primary acceptance source and no quantitative synthesis, so a paper whose whole value proposition is comparability rests on a literature that contains no distribution; and the measured access frequency is relabelled "engagement," a construct with an established multidimensional definition the measure does not satisfy. Both are correctable in text without new data.

### Reviewer 3 (Perspective) Summary
- Recommendation: Major Revision | Confidence: 4 | Dimension scores: D1 warn, D2 warn, D3 warn, D4 warn, D5 warn | Self-reported fired: F2
- Key Point: From an institutional-research seat the paper falls below the reporting floor at which it could be used as administrative evidence — no denominator, no deduplication rule, recruitment plausibly inside the platform under study — and it locates the entire phenomenon inside the individual student, leaving the onboarding implication resting on an untested assumption that low use is attitudinal rather than material.

### Devil's Advocate Summary
- Recommendation: `reject_or_major_revision`; findings framed as revision-closable | Confidence: not stated | Dimension scores: D1 warn, **D2 block**, D3 warn, D4 warn, D5 warn | Self-reported fired: F1, F2
- Key Point: The manuscript's hedging is placed entirely where the paper is already safe — causality, single-site scope, self-report-versus-logs are each conceded on axes its thesis does not need — while the one claim carrying real weight, the substitution of "engagement" for access frequency in the Abstract's terminal sentence, is unhedged and undefined; and beneath the modesty sits an unexamined premise that this correlation is a transportable quantity at all.

### Appendix: Full Reviewer Reports

The five complete Phase 2 reviewer cards are transmitted verbatim with this letter for the author's reference.
