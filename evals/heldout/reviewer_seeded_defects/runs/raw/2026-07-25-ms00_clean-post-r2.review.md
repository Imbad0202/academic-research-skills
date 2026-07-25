# Isolated-dispatch panel review — gamma-2 (post condition, 2026-07-25)

(Phase 1 calls were physically separated: each seat’s pre-commitment was produced by a clean
headless `claude -p` call — claude-opus-5, effort xhigh, thinking enabled — that received only
the contract + title/field/word_count and was forbidden from reading any manuscript. Phase 2,
field analysis, and synthesis were separate paper-visible headless calls with read scope
limited to the named skill files and the neutral-named manuscript copy.)

# PART 1 — FIELD ANALYSIS

# Field Analysis Report

## Paper Basic Information
- **Title**: Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students
- **Abstract length**: ~145 words
- **Full text length**: ~1,600 words (body, Sections 1–7, excluding references); ~1,750 words including the reference list
- **Number of references**: 6
- **Language**: English (review to be conducted in English)
- **Structural inventory**: Standard IMRaD + Limitations + Conclusion. **Zero tables, zero figures.** No data-availability, funding, conflict-of-interest, or preregistration statement.

---

## Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| **Primary Discipline** | Educational technology in higher education — specifically LMS adoption/engagement among undergraduate students |
| **Secondary Disciplines** | (1) Information systems / technology-acceptance research (TAM lineage); (2) Educational measurement & survey psychometrics (scale adaptation, self-report validity); (3) Learning analytics / institutional research (behavioral log data as the unused alternative measure) |
| **Research Paradigm** | Quantitative — descriptive/correlational, explicitly non-model-testing. The authors deliberately decline to test a full acceptance model and frame the work as a single bivariate association |
| **Methodology Type** | Survey / questionnaire — single-site cross-sectional design, n = 214, self-administered online, Pearson correlation with Spearman robustness check |
| **Target Journal Tier** | **Q3** (with a plausible reach to a receptive Q2 venue). Rationale: the execution is competent and the statistical reporting is internally accurate, but the substantive contribution is one bivariate correlation between two self-report measures at one institution, with no theoretical extension, no moderator analysis, and no comparative or longitudinal component. The reference base (6 sources, none canonical to the acceptance literature it invokes) signals a scope well below Q1 expectations. Q1 venues (e.g. *Computers & Education*, *International Journal of Educational Technology in Higher Education*) would most likely desk-reject on insufficient novelty rather than on quality |
| **Paper Maturity** | **Pre-submission.** Rationale: complete and conventional section structure; consistent APA-style referencing with DOIs throughout; polished, controlled, non-redundant prose; reporting conventions largely observed (95% CI, exact n, robustness check, sensitivity/power statement). What is missing is not drafting work but *documentation* — descriptive table, full item wording, response-rate denominator, deduplication procedure. This is a manuscript needing final review and targeted additions, not restructuring |

**Notable calibration observation (affects review strategy).** Spot-verification of the paper's own numbers: the reported CI for *r* = .42 at *n* = 214 (Fisher-*z*: [.30, .53]) matches the manuscript's [.30, .52]; the sensitivity claim (>.80 power to detect *r* ≥ .19 at α = .05, two-tailed, *n* = 214) is also correct. The hedging language ("associated with", "should not be read as causal", "one point in a distribution") is applied consistently in abstract, results, discussion, and conclusion. **This manuscript is unusually well-calibrated and pre-empts the obvious criticisms.** The review team must be configured to find the non-obvious problems, not to restate the paper's own limitations back to it.

---

## Recommended Target Journals (Top 3)

1. **_Research in Learning Technology_** — Best realistic fit. Open-access venue that publishes bounded, single-institution empirical studies in higher-education learning technology and does not require a theory-building contribution. The manuscript's transparently modest framing ("an incremental data point") is closer to this journal's tolerance than to any model-testing venue. Would still require the missing methodological documentation.

2. **_Education and Information Technologies_** — Higher-volume venue that regularly publishes single-site LMS/acceptance surveys. Reachable, but conditional on substantially expanding the literature base and positioning *r* = .42 explicitly against the range of previously reported effect sizes; as submitted, the six-reference base is below this journal's norm.

3. **_Journal of Information Technology Education: Research_** — Specialized Q3 venue well matched to correlational survey work in educational computing. Strong topical fit, but this journal expects full instrument documentation (item wording, adaptation procedure, dimensionality evidence), all of which the manuscript currently omits.

*Not recommended as first target*: *Computers & Education*, *British Journal of Educational Technology*, *IJETHE* — the contribution size makes desk rejection the likely outcome, and a desk rejection would return no useful reviewer feedback.

---

## Reviewer Configuration Cards

**Disciplinary coverage strategy.** This manuscript is adjacent-disciplinary rather than highly cross-disciplinary: one core field (EdTech/higher education) with two live adjacencies (measurement; learning analytics). R2 therefore holds the core discipline, R3 takes the learning-analytics/institutional-practice adjacency, and R1 holds measurement. The one issue that could be double-claimed — the anonymity vs. duplicate-removal contradiction — is assigned to **R1 as a data-integrity/procedure finding** and to **R3 only as a data-governance/consent framing**, so the two do not report the same finding twice.

---

### Reviewer Configuration Card #1

**Role**: Editor-in-Chief
**Identity Description**: Editor-in-Chief of an established open-access higher-education learning-technology journal (*Research in Learning Technology* profile), with a background in institutional e-learning strategy and fifteen years of handling submissions in the LMS-adoption space; has personally triaged several hundred perceived-usefulness/technology-acceptance survey manuscripts and is acutely aware of saturation in this exact sub-literature.
**Review Focus**:
  1. **Contribution sufficiency against a saturated literature** — the manuscript itself states that the positive association is already established (Section 2) and offers itself as "an incremental data point." Does a single bivariate correlation from one campus, with no moderators, no comparison group, and no meta-analytic contextualization, clear the bar for a full research article, or is it a brief report / short communication?
  2. **Whether epistemic modesty is being used as a substitute for contribution** — the paper's calibration is genuinely good, but "we claim very little" is not itself a claim. Assess whether the honest framing earns publication or merely makes a thin result unfalsifiable as a criticism.
  3. **Readership fit and format decision** — recommend the correct article category (full paper / brief report / reject-and-redirect), and whether the manuscript is better placed at a specialized venue than a general one.
  4. **Publication-integrity screen at the editorial level** — the six references carry DOIs sharing the `10.5555` prefix (a reserved test/example prefix, not an assigned registrant) and the journal titles are close-but-not-exact variants of real venues. Flag for source verification before the manuscript proceeds; this is an editorial-office responsibility, not a peer-reviewer one.
**Will particularly care about**: Whether one more correctly-reported correlation between two self-report measures at one institution justifies a slot in the journal, given that the paper's own literature review says the finding is already known and varies by site.
**Possible blind spots**: Reads at the altitude of contribution and fit, so will likely *not* catch the procedural defects (uncomputable response rate, undocumented deduplication, absent descriptive table) or the psychometric attenuation issue. May also over-penalize the modest framing — a small, honest, correctly-executed study is a legitimate publication, and the synthesizer should check that "thin" is not being scored twice.

---

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1 — Methodology
**Identity Description**: Quantitative survey methodologist in an educational-measurement department, specializing in self-report validity and common-method variance in single-instrument designs; publishes on the attenuation effects of coarse ordinal categorization and on nonresponse bias in voluntary institutional surveys; routinely serves as statistical reviewer for education and information-systems journals.
**Review Focus**:
  1. **Sampling denominator and response rate.** Section 3.1 states "all enrolled undergraduates were eligible" but never gives the eligible N, so no response rate can be computed from 233 received responses. Recruitment via a course-announcement channel plus voluntary participation is a self-selection mechanism the paper acknowledges only in one clause of Section 6. "Spanned all four year levels" is not a sample description — no demographic table, no distribution by year, discipline, or enrolment status.
  2. **Data-cleaning integrity — internal contradiction.** Section 3.1 reports removing "5 duplicate entries"; Section 3.3 states "no identifying information was collected, and responses could not be linked back to individual students." These cannot both be true as written. Require an explicit account of the duplicate-detection procedure (IP address? session cookie? browser fingerprint? response-pattern matching?) and whether the ethics approval covered whatever was actually captured. Also require the 14 incomplete-submission exclusions to be specified (what threshold defined "incomplete"?).
  3. **Measurement documentation and construct validity.** The six-item scale is described as "adapted from Costa and Wren (2019)" with no statement of what was changed, no item wording reproduced, and no dimensionality evidence. Cronbach's α = .88 establishes internal consistency, not unidimensionality; a mean composite presupposes a single factor that is never demonstrated. The dependent variable is a **single ordinal item** with undefined and unequal category widths ("rarely or never" → "several times daily"), used as if it were a continuous measure.
  4. **Attenuation and common-method variance.** Pearson correlation on a 5-category ordinal variable is attenuated by categorization; the Spearman check (ρ = .40) addresses monotonicity but not coarseness — a polychoric or disattenuated estimate should be reported. Conversely, both variables come from the same self-report instrument administered at one time to one respondent, so *r* = .42 is exposed to common-method inflation. These two forces push in opposite directions and the manuscript addresses neither; the true association is not bounded by the reported estimate.
  5. **Reporting completeness.** No descriptive table; no frequency distribution for the use item (median category alone is insufficient for an ordinal outcome); no CI on the Spearman coefficient; *r*² described only verbally as "modest" (Section 4) when it should be stated (≈ .18); scatterplot "inspection" asserted but the plot is not shown.
**Will particularly care about**: Whether *r* = .42 estimates an association between two constructs, or is substantially an artifact of shared method plus coarse measurement — and whether the deduplication account can be reconciled with the anonymity claim.
**Possible blind spots**: Will treat the research question as given and not ask whether it is worth asking; will not weigh field saturation, practical/institutional value, or the reference-base integrity problem. May accept the reference list at face value because it is correctly formatted.

---

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2 — Domain
**Identity Description**: Senior higher-education scholar in educational technology whose research programme covers LMS adoption and student engagement across institutional contexts; has published critiques of the TAM/UTAUT lineage's explanatory limits in education, and has run replication and multi-site work on perceived-usefulness effects; knows the canonical sources and the current state of the evidence base intimately.
**Review Focus**:
  1. **Literature base adequacy.** Six references for a paper positioned inside the technology-acceptance tradition. None of the field's foundational statements appear — no Davis (1989), no Venkatesh & Davis (2000), no UTAUT (Venkatesh et al., 2003), no Venkatesh & Bala (2008), and no engagement with the substantial critical literature on TAM's limitations in educational settings. The paper borrows the tradition's central construct and vocabulary while citing none of its primary sources.
  2. **Citation verifiability — high-priority integrity check.** All six DOIs share the `10.5555` prefix, which is a reserved test/example prefix rather than an assigned registrant prefix. The journal names are systematic near-misses of real venues ("British Journal of Educational Technology **Studies**", "Computers & Education **Review**", "Educational Measurement **Quarterly**"). Every reference must be independently verified before the substantive review is finalized; if the sources cannot be located, this supersedes all other findings.
  3. **Contribution to the field.** Section 2 characterizes the association as established, with effect sizes varying by sample and instrument, and Song (2018) is invoked precisely to say a single-site estimate is "one point in a distribution." The paper then contributes one more point without situating it numerically against that distribution — no comparison of *r* = .42 to previously reported ranges, no meta-analytic anchoring. The stated contribution ("comparable with prior work") is asserted rather than demonstrated.
  4. **Theoretical positioning.** Perceived usefulness is extracted from its nomological network and correlated with a proxy for behavior, with no attitude, behavioral intention, subjective norm, or facilitating-conditions variable. The paper explicitly opts out of testing a model — a defensible choice — but then offers no alternative account of why perceived usefulness in particular is the construct worth isolating.
  5. **Internal consistency of the argument.** Whitfield (2019) is introduced only in the Discussion to support an onboarding implication and never appears in the Literature Review; the onboarding claim is thereby supported by a source the paper never assessed.
**Will particularly care about**: Whether the manuscript's careful hedging is doing the work of a contribution — and whether the evidence base it rests on actually exists.
**Possible blind spots**: May apply theory-building expectations to a study that deliberately declined to build theory, and undervalue the legitimate role of clean, replication-style descriptive reporting in a field with heterogeneous effect sizes. Will not scrutinize statistical procedure at the level R1 does.

---

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3 — Cross-disciplinary / Practical
**Identity Description**: Learning-analytics researcher and practitioner — director of learning-technology data services at a large public university, holding a joint academic appointment; builds and governs the institutional LMS data warehouse, has published on the divergence between self-reported and log-derived engagement, and sits on the institution's data-governance committee that reviews research access to student platform data.
**Review Focus**:
  1. **The measure the authors could have used but did not.** The manuscript cites Vasquez (2020) specifically on the divergence between self-report and behavioral logs (Section 2), lists it again as Limitation 2 (Section 6) — and then builds its sole outcome variable on self-report anyway, at an institution that by definition holds LMS access logs for every respondent. The paper never explains why logs were unavailable, unobtainable, or unsuitable. This is not a generic "future research should use logs" point: it is a question about why the weakest available measure was chosen when a stronger one sat in the same building. A validated subsample, or an explicit statement of the governance barrier, is the minimum required response.
  2. **What "LMS use" actually denotes.** "How often the respondent accessed the LMS in a typical week" collapses categorically different behaviors — checking a grade, downloading a slide deck, submitting an assessment, participating in a discussion — into one frequency count. From an operational standpoint, access frequency is dominated by *mandatory* structure: assignment deadlines, quiz windows, attendance tracking, instructor posting cadence. The manuscript concedes this in Section 4 ("course requirements and assessment schedules") but designed no measure to capture it, so the unmeasured driver is plausibly larger than the measured one.
  3. **Whether the practical recommendation survives the design.** Section 5 recommends institutional attention to usefulness-focused onboarding. Translate that into practice: what would a university actually do differently on the basis of *r* = .42 between two self-report items, and what would it cost? A correlational finding with an acknowledged reverse-causal pathway (use → perceived usefulness) supports the *opposite* intervention just as well — mandate early use and perception follows. The implication as written is under-determined by the evidence.
  4. **Data governance and consent, from the platform side.** Taking the deduplication/anonymity tension (see R1) at the governance level rather than the procedural level: if five duplicates were identified, some persistent identifier was captured. Was that disclosed on the informed-consent landing page? Does the ethics approval characterize the study as anonymous, and is that characterization accurate? At most institutions this determines whether the approved protocol was actually followed.
  5. **Missing institutional context that would cost nothing to add.** LMS platform and version, whether use was mandatory or optional at the course level, institutional policy on posting materials, and the survey window's position in the academic calendar (a three-week window near midterms produces a very different "typical week" than one in week 2). None is reported; all are known to the authors.
**Will particularly care about**: Whether a study conducted inside an institution that owns behavioral data chose a self-report proxy without justification — and whether the onboarding recommendation outruns what a single cross-sectional correlation can support.
**Possible blind spots**: May drift toward log-data maximalism and undervalue perception measures, which capture something logs cannot (students' subjective evaluation is the actual construct of interest here, not a defective proxy for behavior). Least attentive of the four to citation integrity and to psychometric detail.

---

## Review Strategy Recommendations

**1. The dominant risk on this manuscript is over-flagging, not under-flagging.**
This paper pre-empts the standard criticisms explicitly and correctly. "Correlation does not imply causation," "single institution limits generalizability," "self-report is not behavior," and "the association is moderate, not strong" are all already stated by the authors — in the abstract, the discussion, *and* the limitations section. **A reviewer who reports any of these as a finding has reported the paper's own text back to it.** Instruct all four reviewers: a limitation the manuscript already states, at the same severity the manuscript states it, is not a finding. It becomes a finding only if the paper states it and then violates it elsewhere (as it arguably does with the Vasquez log-data caution → R3 Focus 1, and with the onboarding implication → R3 Focus 3).

**2. Verify before you criticize — the numbers check out.**
Independent verification confirms the Fisher-*z* CI for *r* = .42 at *n* = 214 is [.30, .53] (paper reports [.30, .52]) and that *n* = 214 gives ≈.80 power to detect *r* ≈ .19 at α = .05 two-tailed. The Spearman check is the methodologically correct move for an ordinal outcome, and the sensitivity framing is prospective, not a post-hoc observed-power fallacy. Reviewers should not assert statistical error here without doing the arithmetic.

**3. Sequence the reference-integrity check first.**
The `10.5555` DOI prefix across all six references, combined with systematically near-miss journal titles and the total absence of the acceptance literature's canonical sources, makes source verification the highest-priority action. If the references cannot be located, every downstream judgment about literature adequacy, contribution, and instrument provenance (the PU scale is "adapted from Costa & Wren, 2019" — an unverifiable source means an unverifiable instrument) changes character. Assigned to **R2 as primary** with an **EIC editorial-office flag**; R1 and R3 should not duplicate it.

**4. Expected convergence — guard the synthesis against severity stacking.**
The EIC ("insufficient contribution") and R2 ("no contribution beyond a known finding") will converge on the same underlying judgment from different altitudes. R3's Focus 3 (implication outruns evidence) is a third face of the same concern. The synthesizer must count this as **one contribution-level issue reported three ways**, not three independent major findings. Inflating it would misrepresent the manuscript's actual quality, which is competent-but-thin, not defective.

**5. Expected genuine divergence — this is the productive tension.**
- **R1 vs. R3 on the headline number.** R1 argues *r* = .42 may be *inflated* by common-method variance; R3 argues the outcome variable measures the wrong construct entirely. R1 also notes ordinal coarseness *attenuates* the estimate. These pull in opposite directions and cannot all be resolved by the same revision. If either R1's CMV concern or R3's construct concern holds, the correct outcome is **re-framing the headline estimate**, not rejection.
- **R2 vs. the paper's design choice.** R2 will want theoretical framing; the paper deliberately declined it. The synthesizer should test whether R2 is applying a standard the manuscript explicitly and defensibly opted out of.
- **R1's finding is the only one with an integrity dimension.** The anonymity-vs-deduplication contradiction (Section 3.1 vs. 3.3) is a factual inconsistency in the manuscript, not a matter of reviewer taste. It should survive synthesis regardless of how the contribution debate resolves.

**6. Register and verdict discipline.**
Maturity is **pre-submission**, prose is clean, and reporting conventions are largely observed — developmental/remedial register is **not** appropriate here and would read as condescending. Reviewers should write to a competent author. Register affects wording only; the recommendation must remain driven by the criteria and the evidence, not by the manuscript's agreeable tone. The likely honest landing zone is **Major Revision** (conditional on reference verification), with Reject reserved for the case where the sources cannot be substantiated.

**7. Concrete artifacts reviewers should request.**
Eligible-population N and computed response rate; a descriptive/demographic table; the full six-item scale wording plus a statement of what "adapted" changed; dimensionality evidence for the composite; the frequency distribution of the use item; the deduplication procedure and its consent/ethics coverage; the definition of "incomplete" used for the 14 exclusions; the scatterplot; an explicit *r*² value; LMS platform, mandatory-use policy, and the survey window's calendar position; and a data-availability statement. Every one of these is already known to the authors and costs no new data collection — which makes the current omissions correctable rather than fatal, and the review should say so.

# PART 2 — SEATS

## SEAT — EIC

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor.** From the editorial chair, this dimension asks whether the study's design and its reporting would survive the peer-review bar of educational-technology research, not whether the statistics are technically optimal — that adjudication belongs to the methodology seat. My concern is whether the manuscript gives an editor enough to certify that the reported evidence could have been produced the way the paper says it was: a stated design, an identified population and sampling route, a described instrument, an analysis whose reporting conventions match the field's, and enough procedural detail that a reader could in principle repeat it. For a cross-sectional survey submission, the editorially load-bearing question is whether the design's own limits are acknowledged where the claims are made. A manuscript that reports results whose provenance an editor cannot trace is not publishable regardless of how interesting its findings are.

**D2 — domain_accuracy.** As EIC I read this dimension as asking whether the paper is a competent citizen of its literature. LMS adoption and perceived-usefulness research sits on a large, mature, and highly specific body of prior work with established constructs and measurement traditions; a submission that engages it loosely, attributes claims to sources that do not support them, or uses field terminology in a non-standard sense damages the journal's standing with exactly the readers it is courting. I am not adjudicating the finer points of construct theory — that is the domain seat's task. My editorial question is whether the paper's representation of what is already known, and its placement of itself against that background, is accurate enough that publishing it would not put erroneous claims into the field's citation record.

**D3 — argumentative_coherence.** This is the dimension closest to the core of the editorial function: does the chain from research question to data to conclusion hold, and does the manuscript claim exactly what its evidence licenses and no more. For a cross-sectional survey of perceived usefulness and self-reported use, the characteristic failure is a gap between what was measured and what is concluded — associational data narrated as if it established a directional or causal relationship, or self-report treated as a proxy for behaviour without saying so. My scan is for internal consistency across title, abstract, stated question, results, and conclusion, and for whether any inferential step is doing work the design cannot support. Over-claiming is an editorial problem even when every individual sentence is defensible, because the abstract and title are what the field will actually carry forward.

**D4 — cross_disciplinary_relevance.** This dimension speaks directly to the readership question I own. Educational technology is a genuinely mixed audience — instructional designers, higher-education administrators, information-systems researchers, learning scientists — and a paper that assumes one sub-community's vocabulary and priors without translation will fail to land even if it is correct. I am assessing whether constructs are defined rather than merely invoked, whether the institutional and instructional context is described concretely enough for a reader elsewhere to judge transferability, and whether any claim reaching beyond the immediate sub-field is actually supported rather than asserted in a closing paragraph. Note that this dimension is `high` priority, not `mandatory`: under the contract it can drive a block only through F3, and it cannot by itself trigger F1 or count toward F2.

**D5 — writing_and_structure.** The lowest-stakes dimension in the contract and, per its `normal` priority, one that participates in none of the failure conditions — no score I assign here can move the editorial decision on its own. It still matters editorially: organisation, clarity of exposition, the quality and necessity of tables, and conformity to venue conventions determine how much reviewer and reader effort the manuscript consumes. I will note that this submission is 1,597 words, which is short for a full empirical article in this field; that is a structural fact about the submission, and the editorially relevant question it raises is whether the length is a deliberate fit to a short-format article type or a symptom of missing reportable content. Where the latter, the substantive deficit belongs in D1 or D3, not here — I will not launder a rigor problem into a writing score.

## Scoring Plan

### D1: methodology_rigor

- `what_to_look_for` — An explicitly named design and its temporal structure; the target population, sampling frame, recruitment route, and response or completion rate; sample size with any exclusions accounted for; the instrument's provenance (adapted from established scales vs. author-written) and its item/response format; a stated reliability or validity check; the analysis actually run, reported with the field's conventional accompaniments (effect estimates alongside significance, dispersion alongside central tendency, denominators for percentages); ethics approval or consent statement; any data/instrument availability statement; and a limitations passage that names the specific constraints of a single-timepoint self-report design rather than generic caveats.
- `what_triggers_block` — Results are reported that cannot be traced to any described procedure: numbers appear with no stated sample size, no described instrument, or no named analysis; or the design as described cannot produce the reported quantity at all. Also blocking: no participant-protection statement of any kind for a study on identifiable undergraduate students, or a stated analysis whose reporting is so incomplete that neither I nor a reader can tell what was compared with what. This is the "an editor cannot certify provenance" threshold, and it is the only D1 pattern I will treat as blocking without deferring to the methodology seat.
- `what_triggers_warn` — Provenance is traceable but thin at points a reader would need: sampling route or response rate absent while a claim about the student population is made; instrument described but with no reliability evidence or item wording; effect sizes or confidence intervals missing where the field expects them; limitations present but generic (not tied to cross-sectional self-report specifically); or reproducibility affordances (instrument, data, code) entirely absent without explanation. Any single such gap warns; I will not escalate an accumulation of thin-reporting gaps to `block` unless it crosses the untraceable-provenance line above.

### D2: domain_accuracy

- `what_to_look_for` — Whether the paper's central constructs are the field's constructs, used with their established meanings, and whether the lineage they come from is cited; whether the cited literature is recent enough and specific enough to be doing real work rather than decorative; whether claims attributed to prior work are the claims that work actually makes; whether the stated gap is a real gap or a well-settled question restated; correct and current use of platform, institutional, and instructional terminology; and internal consistency of any domain fact repeated across abstract, introduction, and discussion.
- `what_triggers_block` — A domain claim that is affirmatively wrong and load-bearing: a construct defined in a way that contradicts its established meaning while the paper's conclusions rest on that definition; a prior finding stated backwards or attributed to a source that does not contain it; or a stated contribution premised on the field not knowing something it demonstrably and prominently does. Also blocking: essentially no engagement with the prior literature at all, since a paper positioned in a mature, heavily-published area with no accurate placement in it cannot have its accuracy assessed and cannot be published without putting unverified claims into the record.
- `what_triggers_warn` — Engagement is present and not wrong, but shallow or dated in ways a specialist reader will notice: constructs invoked by name without definition or citation; a literature base that is sparse, or skewed old, or does not include the obvious anchoring work for this exact question; a gap claim that is overstated but not false; loose or non-standard use of a domain term where the intended meaning is still recoverable; or an inconsistency in how a domain fact is stated between sections that does not change the conclusion.

### D3: argumentative_coherence

- `what_to_look_for` — Alignment across the five load-bearing surfaces — title, abstract, stated research question, results, conclusion — checked as a chain rather than individually; whether each conclusion sentence names an inference the reported data can license; the verbs used to describe the relationship studied (associated/related vs. leads to/increases/drives/improves); whether self-reported use is consistently framed as self-report or silently becomes behaviour; whether the implications or recommendations section stays within the study's evidentiary reach; whether any result reported in the body is absent from or contradicted by the abstract; and whether an unaddressed alternative explanation would defeat the paper's central reading of its own data.
- `what_triggers_block` — The paper's central claim is not supported by its own reported evidence. Concretely: a causal or directional conclusion drawn from cross-sectional associational data and carried into the title, abstract, or conclusion as the paper's headline finding; a conclusion that contradicts the results it cites; or a stated research question that the reported analysis does not actually address, leaving the paper answering a different question than the one it poses. The distinguishing mark of block here is that removing the unsupported step removes the paper's contribution — the over-claim is not a phrasing slip but the thesis itself.
- `what_triggers_warn` — The central argument holds but leaks at the edges: causal language appearing in the discussion or implications while the abstract and conclusion stay appropriately associational; recommendations for practice that outrun the evidence but are not the paper's stated contribution; self-report/behaviour conflation in isolated passages; a salient alternative explanation left unacknowledged though the conclusion does not depend on excluding it; or a mismatch of emphasis (not of substance) between abstract and body. I will also warn where an inference is defensible but the manuscript never states the assumption it rests on.

### D4: cross_disciplinary_relevance

- `what_to_look_for` — Whether the core constructs are defined on first use for a reader from an adjacent field rather than assumed; whether the institutional setting, platform, course context, and student population are described concretely enough to let a reader elsewhere judge transferability; whether abbreviations and field-internal shorthand are expanded; whether the framing states why this question matters beyond the single site studied; and whether any claim addressed to a broader audience (policy, design, administration, generalisation to other institutions or systems) is carried by the evidence or merely asserted.
- `what_triggers_block` — The paper makes a substantiated-sounding claim reaching well outside its evidentiary base — generalisation to institutions, systems, or populations the study did not sample, or a design/policy prescription presented as an established implication — with no supporting warrant and no scoping caveat. Alternatively: context is so thin (setting, platform, population unspecified) that an adjacent-field reader cannot determine what the findings are about or where they might apply, rendering the paper's stated relevance unassessable. I record that D4 is `high` priority: a block here fires F3 alone and does not participate in F1 or F2.
- `what_triggers_warn` — Accessible in the main but requiring the reader to supply context the paper should have given: constructs used correctly but undefined; setting described in general terms without the specifics that determine transferability; implications stated for a broader audience with appropriate hedging but no explicit scoping to the studied population; or unexpanded field shorthand that an adjacent-field reader would have to look up. A single instance warns.

### D5: writing_and_structure

- `what_to_look_for` — Presence and ordering of the sections the venue expects for an empirical report; whether the abstract is self-contained and reports what the study found rather than what it examined; paragraph-level clarity and whether exposition proceeds by argument rather than by connective padding; whether tables and figures are necessary, self-explanatory with their captions, correctly numbered, and consistent with the numbers in the text; citation and reference formatting consistency; and whether the 1,597-word length corresponds to a coherent short-format article or leaves expected reportable content simply absent.
- `what_triggers_block` — Organisation or presentation so deficient that the manuscript cannot be read as a research report: required sections absent such that the reader cannot follow what was done, or tables/figures that contradict the text with no reconcilable reading. I hold a genuinely high bar here — D5 is `normal` priority and fires none of this contract's failure conditions, so a block would be a signal to the synthesizer rather than a decision driver, and I will not inflate a substantive deficit into a presentation block to give it force it does not have under the contract.
- `what_triggers_warn` — Readable but below venue standard: an abstract that describes the study without reporting its findings; inconsistent citation or reference formatting; tables that duplicate the text or lack self-explanatory captions; numbering or cross-reference errors; sections present but disproportionately weighted (e.g., a discussion longer than the combined methods and results); or a length that reads as compressed rather than deliberately short-format, with expected content thinned. Where thinning removes something substantive, I will warn here and locate the substantive deficiency in D1 or D3 rather than double-counting it.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## EIC Review Report

### Reviewer Identity

Editor-in-Chief of an established open-access higher-education learning-technology journal (*Research in Learning Technology* profile), with a background in institutional e-learning strategy and fifteen years handling submissions in the LMS-adoption space. I have personally triaged several hundred perceived-usefulness / technology-acceptance survey manuscripts and am acutely aware of saturation in this exact sub-literature. My review is conducted at the altitude of contribution, fit, structural coherence, and editorial-office publication integrity; procedural and psychometric adjudication belongs to the methodology seat.

### Overall Recommendation

**Reject**

Qualified: reject as a full research article and pending editorial-office source verification. If every reference is independently verified and the primary acceptance literature is engaged, the remaining defects are Major-Revision-scale and correctable without new data collection — but they would also need to be resubmitted into a brief-report / short-communication category rather than as a full paper.

### Confidence Score

**4** — High confidence. Journal fit, contribution sufficiency, and editorial-office integrity screening are squarely my function. The one residual uncertainty is that I could not complete external DOI resolution within this review; my integrity finding therefore rests on internal evidence from the reference list itself, which I judge sufficient to halt the manuscript but not to characterise author intent.

### Summary Assessment

This manuscript reports a single bivariate association between undergraduates' perceived usefulness of an LMS and their self-reported frequency of use (*r* = .42, *n* = 214) at one mid-sized public university. It is unusually well-calibrated: the correlational framing is maintained without slippage across abstract, results, discussion, limitations, and conclusion; the reverse-causal pathway is named explicitly; the headline estimate carries a confidence interval, a *p* value, a sample size, an ordinal robustness check, and a prospective sensitivity statement. The prose is controlled and non-redundant, and the manuscript pre-empts every stock criticism a reviewer might otherwise raise.

That competence is real, and I want to separate it clearly from what stops the paper. The manuscript is halted by its reference base, not by its modesty. All six DOIs share a single reserved test prefix with sequential suffixes in exact alphabetical-by-author order — a pattern a genuine six-journal citation set cannot produce — and, independently of that, the paper adopts the technology-acceptance tradition's central construct and Davis's definition of it while citing no primary source from that lineage. Since the instrument's provenance and the paper's only stated contribution (comparability with prior work) both rest on those sources, the entire evidentiary frame is currently unassessable.

### Strengths

1. **Claim hygiene sustained across every load-bearing surface**: The non-causal framing is not a single limitations-section disclaimer but a maintained discipline. The manuscript volunteers the reverse pathway rather than conceding it under pressure. — `text: §5 Discussion — "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"`

2. **Reporting conventions observed for the headline estimate**: Point estimate, interval, *p*, *n*, and an ordinal-appropriate robustness check are all present in one place, with a prospective (not post-hoc) sensitivity statement in §3.4. This is above the norm for submissions in this sub-literature. — `text: §4 Results — "r = .42, 95% CI [.30, .52], p < .001, n = 214"`

3. **Honest scope declaration with no over-promising**: The paper declines to test a model and says so, rather than dressing a bivariate correlation as model-adjacent evidence. Title, abstract, research question, and conclusion all describe the same narrow object. — `text: §2 — "It is intended as an incremental data point, comparable with prior work, rather than as a test of a theoretical model."`

4. **Participant-protection reporting is present as a statement**: Ethics-committee approval, voluntariness, absence of incentive, and landing-page informed consent are all reported — an item routinely omitted in this submission class. (Its internal consistency is a separate matter; see W5.) — `text: §3.3 Procedure and ethics`

5. **Exposition quality**: Sections are conventionally ordered and proportionate, paragraphs advance by argument rather than connective padding, and citation formatting is internally consistent. This reads as a manuscript ready for review, not a draft. — `text: §1–§7, whole-manuscript structural read`

### Weaknesses

1. **The reference list cannot be a genuine set of published sources as printed**: All six DOIs share the prefix `10.5555`, a reserved test/example prefix rather than an assigned registrant prefix — and DOI prefixes are per-registrant, so six articles in six different journals from six different publishers cannot share one. The suffixes are additionally sequential (`2050001`–`2050006`) in exact alphabetical-by-first-author order across publication years 2018–2021. The journal names are also systematic near-variants of real venues. No verification outside the manuscript is required to see that this pattern is not producible by a real citation set. I make no claim about how it arose; the editorial office must resolve provenance before this manuscript proceeds to peer review, because the instrument's provenance ("adapted from Costa and Wren, 2019") and the paper's entire literature frame depend on it. **Improvement direction**: supply verifiable citations for all six sources, or replace them.
   - **Severity**: Critical | **Evidence Anchor**: [`text: §References — "https://doi.org/10.5555/2050001" through "https://doi.org/10.5555/2050006"`] | **Confidence**: 5 — DOI registrant-prefix structure and citation-record verification are core editorial-office responsibilities I exercise on every submission.

2. **The invoked tradition's primary literature is entirely absent**: §2 states that "Research on technology acceptance has long proposed" that perceived usefulness is associated with adoption, gives what is recognisably Davis's definition of the construct, and attributes the whole proposition to two sources dated 2019 and 2020. A claim about what a field has long proposed, supported only by recent secondary work, misplaces the origin of the field's central construct in the citation record. Across all six references, no foundational acceptance-model source appears. This finding is independent of W1 and would stand even if every reference were verified genuine. **Improvement direction**: cite the tradition's primary sources where the construct and its proposition are introduced, and engage the critical literature on the model's limits in educational settings.
   - **Severity**: Critical | **Evidence Anchor**: [`absence: checked §2 Literature Review and §References in full — no primary acceptance-model source appears among the six references`] | **Confidence**: 5 — the canonical lineage of this literature is directly within my editorial experience.

3. **The stated contribution is comparability, and comparability is the one thing never demonstrated**: §2 offers the paper as "an incremental data point, comparable with prior work," and §2 invokes Song (2018) precisely for the proposition that a single-site estimate is "one point in a distribution." The paper then contributes its point without ever showing the distribution: no previously reported coefficient appears anywhere in the manuscript, so "consistent with prior technology-acceptance research" (abstract, §5, §7) is asserted rather than shown. I want to be explicit that I am **not** penalising the modest framing — a small, honest, correctly-executed study is a legitimate publication. The defect is narrower and real: the paper's only stated warrant for existing is a comparison it does not make. **Improvement direction**: report the effect-size range from the cited literature and locate *r* = .42 within it numerically.
   - **Severity**: Major | **Evidence Anchor**: [`absence: checked §2, §4, §5, §7 — no numeric comparison of r = .42 against any prior coefficient appears in the manuscript`] | **Confidence**: 4 — contribution-level assessment is my primary editorial function.

4. **A directional recommendation drawn from an admittedly non-directional finding**: §5 grants that the reverse pathway is "equally consistent with the data," then recommends onboarding designed to raise perceived usefulness — an intervention that follows only from the perception→use direction. The opposite intervention (structure early mandatory use, let perception follow) is supported exactly as well by the same estimate. The hedging ("may be worth institutional attention," "suggested by, not proven by") softens the sentence without repairing the asymmetry, since the paper has already conceded the premise that defeats it. **Improvement direction**: either state both candidate interventions as equally licensed, or drop the practice implication.
   - **Severity**: Major | **Evidence Anchor**: [`text: §5 — "LMS onboarding which helps students see concrete usefulness — rather than merely announcing that a platform exists — may be worth institutional attention"`] | **Confidence**: 4 — internal-consistency assessment at the discussion/implications boundary.

5. **The anonymity claim and the deduplication step cannot both hold as written**: §3.1 reports removing "5 duplicate entries"; §3.3 states that "No identifying information was collected, and responses could not be linked back to individual students." Detecting duplicates requires some persistent identifier or linkage. My editorial concern is narrower than the procedural one: whether the anonymity characterisation given to the ethics committee matches what was actually captured, which bears on whether the approved protocol was followed. The procedural specification belongs to the methodology seat; the accuracy of the ethics representation is mine. **Improvement direction**: state the duplicate-detection mechanism and confirm it was disclosed on the consent landing page and covered by the approval.
   - **Severity**: Major | **Evidence Anchor**: [`text: §3.1 "5 duplicate entries were removed" vs §3.3 "No identifying information was collected, and responses could not be linked back to individual students"`] | **Confidence**: 4 — a factual contradiction on the page plus an ethics-representation question, both editorial-office territory.

6. **Transferability is unassessable because the paper omits the context its own literature review calls determinative**: §2 cites Ibarra and Poll (2021) for the role of "course design, instructor expectations, and assessment structure" and Song (2018) for institution-level variation, then reports the setting as "one mid-sized public university" and nothing more. The LMS platform is unnamed, the mandatory-versus-optional use policy is unstated, disciplinary composition is unstated, the three-week window's position in the academic calendar is unstated, and the sample is described only as having "spanned all four year levels." §6 concedes that results may not generalise to institutions of different size, sector, or profile — but gives a reader no way to identify which institutions are similar. This is distinct from the generalisability limitation the paper already states. **Improvement direction**: report platform, use policy, disciplinary mix, calendar position, and a year-level distribution; all are already known to the authors.
   - **Severity**: Major | **Evidence Anchor**: [`absence: checked §3.1, §3.2, §6 — none reports platform, course-level use policy, disciplinary composition, or survey-window calendar position`] | **Confidence**: 4 — transferability judgement is a core editorial readership concern.

7. **No response-rate denominator**: §3.1 states that "All enrolled undergraduates were eligible" but never gives the eligible N, so no response rate can be computed from the 233 responses received. The paper makes claims about an undergraduate population while withholding the one number that would let a reader size the achieved coverage. §6 concedes voluntary self-selection but the concession does not substitute for the denominator. Detailed specification of this and the "incomplete" exclusion threshold belongs to the methodology seat. **Improvement direction**: report the eligible enrolled N and the resulting response rate.
   - **Severity**: Major | **Evidence Anchor**: [`text: §3.1 — "All enrolled undergraduates were eligible"`, with the eligible N absent from the whole manuscript] | **Confidence**: 4 — basic reportability, not a technical statistical judgement.

8. **No table, no figure, and no stated *r*²**: The Results section carries a mean, an SD, a median category, and two coefficients. There is no descriptive or demographic table, no frequency distribution for the ordinal use item, and the scatterplot is asserted as "inspected" (§3.4) but not shown. §4 describes the shared variance only verbally as "modest" where the value should simply be given. **Improvement direction**: add a descriptive table, the use-item frequency distribution, the scatterplot, and an explicit *r*² value.
   - **Severity**: Minor | **Evidence Anchor**: [`absence: checked the full manuscript — no table or figure appears anywhere in §1–§7`] | **Confidence**: 5 — presentation-completeness against venue norms.

9. **A source supporting the paper's only practice recommendation is never assessed**: Whitfield (2019) is introduced for the first time in §5 to underwrite the onboarding implication, and appears nowhere in §2. The reader is asked to accept a practitioner source as support for the paper's sole recommendation without having seen it evaluated. **Improvement direction**: introduce and appraise the source in the literature review, or drop the appeal to it.
   - **Severity**: Minor | **Evidence Anchor**: [`text: §5 — "(Whitfield, 2019)"`, absent from §2 Literature Review] | **Confidence**: 4 — structural-coherence check across sections.

### Detailed Comments

#### Journal Fit

Topically this is a good fit for my venue and for the specialised end of higher-education learning technology generally: a bounded, single-institution empirical study with transparently modest framing is exactly what an open-access venue of this profile exists to carry, and I would not require a theory-building contribution from it. Two things nonetheless prevent it from being placeable as submitted. First, six references is below the norm of any venue in this field, and as printed those six cannot be relied upon at all (W1, W2). Second, the article category is wrong: one bivariate correlation between two self-report items at one site, with no moderator, no comparison group, and no meta-analytic anchoring, is a brief report or short communication, not a full research article. I would advise against *Computers & Education*, *British Journal of Educational Technology*, or *IJETHE* as first targets — the contribution size makes desk rejection likely there, which returns no usable feedback to the authors.

#### Originality

The novelty claimed is an additional data point in a literature the manuscript itself characterises as already establishing the association (§2). That is a legitimate form of contribution in a field with heterogeneous effect sizes, and I decline to treat "incremental" as a criticism. But an incremental contribution is only a contribution when the increment is located. Here it is not: the paper never states what prior estimates were, so no reader can say whether *r* = .42 confirms, extends, or sits at the edge of what is known. Replication-style value requires the comparison to be performed, not merely promised.

#### Significance

Bounded and, on the manuscript's own terms, small. If the association holds, it adds one estimate to a distribution the paper does not display. The practical implication offered (§5) is under-determined by the design in the specific way described in W4. For readers across the mixed educational-technology audience, the significance is further limited by the absence of the institutional and instructional context (W6) that would let anyone judge whether their own setting resembles the one studied.

#### Structural Coherence

Strong at the level the manuscript most often fails and weak at two seams. Title → abstract → research question → results → conclusion align without drift; the object of study stays the same object throughout, and the conclusion answers the question actually posed. The two seams are: the discussion's directional recommendation contradicting the discussion's own directional concession (W4), and a source appearing in the discussion that the literature review never introduced (W9).

#### Title & Abstract

The title is accurate and appropriately unglamorous — it names the design, the population, and both variables, including the word "Self-Reported." The abstract is self-contained and reports the finding rather than merely announcing that a finding exists, which is more than many submissions manage. One drift: the closing sentence characterises the result as evidence that perceived usefulness "tracks with LMS engagement," where what was measured is self-reported access frequency. §2 is explicit that the measure indicates perceived rather than actual engagement; the abstract's final sentence quietly widens the construct. Since the abstract is what the field will carry forward, that word should be brought back into line with the body.

#### Conclusion

Appropriately restrained and correctly scoped: it restates the estimate with its sample, refuses the causal reading, names the design bound, and points to log data and longitudinal or multi-institution designs as the route forward. It contains no claim the results do not license. Its weakness is inherited rather than local — it repeats "consistent with prior work" without the comparison that would make the phrase informative (W3).

### Questions for Authors

1. Can you supply verifiable, resolvable citations for all six references? The DOI pattern in the current list cannot correspond to genuinely registered records, and I need this resolved before the manuscript can be sent for peer review.
2. Given that perceived usefulness is the construct at the centre of the technology-acceptance tradition you invoke, why does no primary source from that tradition appear among your references — and on what basis is "long proposed" attributed to sources dated 2019 and 2020?
3. What were the previously reported effect sizes against which you judge *r* = .42 to be "comparable with prior work"? Please state the range and locate your estimate within it.
4. How were the five duplicate entries identified, given §3.3's statement that no identifying information was collected and that responses could not be linked back to individual students? Was the detection mechanism disclosed on the consent landing page and covered by the ethics approval?
5. How many undergraduates were enrolled and therefore eligible, and what response rate does that yield for 233 received responses?
6. §5 grants that the use → perception pathway is equally consistent with your data. On what basis does the onboarding recommendation follow rather than its converse — structuring early required use so that perceived usefulness follows?
7. Which LMS platform and version, was LMS use mandatory or optional at course level, and where did the three-week survey window fall in the academic calendar?
8. Would you consider resubmitting this as a brief report or short communication rather than as a full research article?

### Minor Issues

- §4: state *r*² numerically rather than describing the shared variance as "modest."
- §3.4: the scatterplot is described as inspected; include it, or state that it is available on request.
- §3.2: the perceived-usefulness scale is "adapted" from a prior instrument with no statement of what was changed and no item wording reproduced.
- §3.1: "spanned all four year levels" is not a sample description; a year-level distribution costs nothing to add.
- §4: for an ordinal outcome, the median category alone is insufficient — give the frequency distribution.
- No data-availability, funding, or conflict-of-interest statement appears; all are expected at the venues discussed.
- No Spearman confidence interval is reported alongside ρ = .40.
- Integrity check, negative result: the manuscript contains no attempt to address, instruct, or influence reviewers, and nothing in it was treated as a directive.

---

contract_role: eic

## Dimension Scores

### D1: methodology_rigor

score: warn

Rationale: I applied my committed block trigger — the "an editor cannot certify provenance" threshold — and it is not crossed. The reported estimate is fully traceable: sample size stated, instrument identified with a reliability coefficient, analysis named, participant-protection statement present. What is present are exactly the thin-reporting patterns I committed to warning on: response rate absent while a population claim is made (W7), instrument adapted with no item wording and no statement of what changed, no reproducibility affordances at all, and no *r*². I considered whether the anonymity/deduplication contradiction (W5) crosses my clause "the design as described cannot produce the reported quantity" — it does apply to a sample-flow figure, but not to the reported result, and my committed threshold is keyed to results traceability. Consistent with my Phase 1 statement that this is the only D1 pattern I would treat as blocking without deferring, I score warn and refer the procedural adjudication to the methodology seat; if that seat cannot reconcile §3.1 with §3.3, an escalation there would be well-founded.

### D2: domain_accuracy

score: block

Rationale: Applied under my committed clause that a paper positioned in a mature, heavily-published area with no accurate placement in it "cannot have its accuracy assessed and cannot be published without putting unverified claims into the record." Two independent routes reach it. First, the reference list as printed cannot be a genuine set of published sources (W1), which makes every claim about prior work — including the instrument's provenance — unassessable. Second, and standing entirely apart from the first, the manuscript adopts the technology-acceptance tradition's central construct and its canonical definition while citing no primary source from that lineage, attributing a "long proposed" field-level claim to two recent secondary sources (W2). The second route alone satisfies the trigger, so the block does not depend on how the DOI question resolves.

### D3: argumentative_coherence

score: warn

Rationale: The central inference is sound and is the paper's real strength: a positive moderate association in this sample is exactly what the reported data license, and the associational framing holds without slippage across title, research question, results, and conclusion. My committed block trigger requires that removing the unsupported step remove the contribution — it does not fire, because the finding stands on its own. What fires is the warn pattern of edge leakage: a practice recommendation that outruns the paper's own conceded directional indeterminacy (W4), an abstract that widens "self-reported use" to "LMS engagement" in its closing sentence, and a comparability claim whose supporting comparison is never stated (W3).

### D4: cross_disciplinary_relevance

score: warn

Rationale: The block branches do not fire. Generalisation is scoped rather than asserted — §6 explicitly bounds the finding to one institution — and the practice implication is hedged rather than presented as established, so the over-reach branch fails. On the context branch, an adjacent-field reader can determine what the findings are about; what they cannot determine is where the findings might apply, because platform, use policy, disciplinary composition, and calendar position are all absent (W6). That is my committed warn language verbatim: setting described in general terms without the specifics that determine transferability. Core constructs are defined on first use and abbreviations expanded. I record that D4 is `high` priority, so this score cannot participate in F1 or F2.

### D5: writing_and_structure

score: warn

Rationale: Well below the block bar — the manuscript is fully readable as a research report, sections are present and conventionally ordered, prose is clean, and citation formatting is internally consistent. The warn is for presentation completeness: zero tables and zero figures in an empirical report, a Results section that carries no descriptive table and no frequency distribution for its ordinal outcome, a scatterplot asserted but not shown, and a shared-variance value described verbally instead of stated (W8). Per my Phase 1 commitment I locate the substantive deficits in D1, D2, and D3 and do not double-count them here; D5 is `normal` priority and fires none of this contract's failure conditions.

## Failure Condition Checks

### F1

fired: true

Predicate: any mandatory dimension scores `block`. D2 (`domain_accuracy`, mandatory) scores block. Severity 90 — the highest-severity condition fired in my card.

### F2

fired: true

Predicate: two or more mandatory dimensions score `warn` or worse. D1 warn, D2 block, D3 warn — three of three mandatory dimensions qualify. Severity 70; superseded by F1 on precedence. The `majority` quantifier is panel-level machinery for the synthesizer and is not applied by me.

### F3

fired: false

Predicate: any high-priority dimension scores `block`. D4 (`cross_disciplinary_relevance`) is the only high-priority dimension and scores warn, not block.

### F0

fired: false

Predicate: every mandatory dimension scores `pass`. None of D1, D2, D3 scores pass.

## Review Body

This is a competent manuscript stopped by its foundations rather than by its execution, and the distinction matters for how the authors should read this card.

The execution deserves saying plainly. The manuscript maintains correlational discipline across every surface where such papers usually leak, volunteers the reverse-causal pathway instead of conceding it under review pressure, reports its headline estimate with the interval, sample size, and ordinal robustness check the field expects, and states its scope prospectively rather than retreating into a limitations section. It pre-empts nearly every stock criticism, and I have deliberately not reported any limitation back to the authors that they already state at the severity they state it. The only place I depart from that rule is where the manuscript states a constraint and then acts against it — the discussion concedes directional indeterminacy and then recommends a directional intervention.

What halts it is the reference base. Six DOIs sharing a single reserved test prefix, with sequential suffixes running in exact alphabetical-by-first-author order across four publication years and six nominally different journals, is not a pattern a genuine citation set can produce; prefixes are assigned per registrant, so six publishers cannot share one. This is an editorial-office matter, not a peer-review one, and I raise it without any claim about how it arose. It must be resolved before the manuscript goes further, because the instrument's provenance and the entire literature frame rest on those six items.

I want to be precise that my D2 block does not hinge on that resolution. Even if all six sources were verified tomorrow, the manuscript would still adopt the technology-acceptance tradition's central construct, reproduce its canonical definition, and cite no primary source from it — attributing what a field has "long proposed" to work dated 2019 and 2020. For a paper whose keywords include "technology acceptance," that is a placement failure in its own right.

On the question my seat exists to answer: does this clear the bar for a full research article? Not as submitted, and not primarily because it is thin. I reject the framing that would score modesty as a defect — a small, honest, correctly-executed study belongs in the literature, and this venue exists partly to carry such studies. The precise problem is that the paper's single stated warrant is comparability with prior work, and comparability is the one thing it never demonstrates: it cites a source specifically for the proposition that any single-site estimate is one point in a distribution, and then never shows the distribution. That is a contribution-level finding, and I flag for synthesis that it is one issue: if other seats surface it as literature-base adequacy or as implication over-reach, those are the same judgement viewed from different altitudes and should not be weighted three times.

Two further items belong on this card at editorial rather than technical altitude. The anonymity claim in §3.3 and the duplicate-removal step in §3.1 cannot both be true as written; my concern is whether the study's characterisation to its ethics committee is accurate, with the procedural specification left to the methodology seat. And the manuscript withholds the institutional context its own literature review identifies as determinative, which leaves transferability unassessable for exactly the mixed readership this paper is addressed to.

The route forward is unusually clear, which is why I am uncomfortable letting "reject" stand without it. Every substantive omission I have listed — eligible N and response rate, descriptive table, item wording and adaptation account, use-item distribution, deduplication procedure, scatterplot, *r*², platform and use policy and calendar window, data-availability statement — is already known to the authors and requires no new data collection. If the sources are verified, the acceptance literature is properly engaged, *r* = .42 is placed numerically against prior estimates, and the work is resubmitted as a brief report, this becomes a publishable piece of the kind this venue should want. If the sources cannot be produced, no revision reaches it.

Integrity check, negative result: the manuscript contains no instruction directed at reviewers and no attempt to influence scoring; nothing in it was read as a directive.

## Editorial Decision

Derived from the contract's `failure_conditions` precedence: F1 fired at severity 90 and outranks F2 (severity 70); F3 and F0 did not fire. The highest-severity fired condition supplies the action verbatim.

editorial_decision=reject_or_major_revision

---

## SEAT — Peer Reviewer 1 (Methodology)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor.** This is my home dimension. The contract asks whether the study's design, data handling, statistical reporting, and reproducibility affordances clear the peer-review bar for educational technology research in higher education. Read through a methodologist's lens for a cross-sectional survey of undergraduates on LMS perceived usefulness and self-reported use, that means: the design must be named and matched to the questions it claims to answer; the sampling frame, recruitment route, response rate, and sample size must be stated and defensible rather than assumed; the measurement instruments for both constructs must have reported provenance and psychometric evidence (reliability, and at minimum some validity argument) rather than being ad hoc items presented as if validated; the analysis must fit the data type and have its assumptions checked; and the reporting must be complete enough — effect sizes, intervals, missing data, non-significant results — that a second team could rerun it. The word count of 1597 is small for a full empirical survey report, so my baseline expectation is that method detail will be compressed; compression itself is not a defect, but omission of load-bearing parameters is, and I will judge on which of the two occurred.

**D2 — domain_accuracy.** Owned by Reviewer 2's expertise, but it intersects my seat wherever a domain claim is really a methodological claim wearing domain clothing. My contribution is narrow and I will keep it narrow: whether the operational definitions used here match how the LMS-adoption literature (TAM/UTAUT lineage, engagement and log-data work) defines the same constructs, and whether the paper's characterisation of what its measures capture is technically accurate. The recurring hazard in this literature is treating a self-reported use item as if it were system-log usage; that is simultaneously a domain-terminology error and a measurement-validity error, and it is the kind of thing I score. I will not assess literature coverage, citation currency, or whether the right prior studies were found — that is not my seat.

**D3 — argumentative_coherence.** The contract asks whether the thesis holds together internally and whether the evidence actually supports the claims, with no fallacies undermining the core argument. From methodology, this is the inference-chain audit: does the strength and direction of the language in the conclusions match what a cross-sectional correlational design can license? A single-timepoint survey of perceived usefulness and self-reported use can establish association; it cannot establish that usefulness perceptions cause or drive use, nor rule out the reverse path (students who already use the system more come to rate it as more useful) or a common-method third factor. The specific fallacies I own here are reverse causation, over-inference beyond the analysis unit, and confirmation-shaped reporting where only hypothesis-consistent results are foregrounded. I assess the argument's logical load-bearing capacity, not its rhetorical polish.

**D4 — cross_disciplinary_relevance.** Reviewer 3's dimension; my stake is bounded and I will state findings modestly. What I can judge is whether the methodological reporting is legible to an adjacent-field reader — an instructional designer, an institutional researcher, a learning-analytics quantitative methodologist — without recourse to the source instrument. That means constructs defined before use, statistics reported with enough context to interpret rather than as bare coefficients, and any cross-field claim (for instance, importing a construct from information-systems acceptance research into an educational-outcomes framing) carrying the measurement evidence that the borrowing requires. I will not score audience breadth, disciplinary reach, or impact.

**D5 — writing_and_structure.** Reviewer 3 and the EIC carry the main weight; my slice is structural adequacy of the methodological record. A Methods section that a replicator can follow in sequence, results reported in a stable and complete form, tables and figures whose numbers reconcile with the text and whose Ns are stated, and venue-conventional statistical formatting (APA 7.0 for this field). At 1597 words the manuscript is short — likely a brief report or research note — so I will grade structure against a compressed-format expectation rather than a full-article one, and treat missing method parameters as a D1 matter, not a D5 style matter, unless the defect is purely one of presentation.

## Scoring Plan

### D1: methodology_rigor
- **what_to_look_for**: An explicitly named design and stated timepoint structure; sampling frame, recruitment channel, sampling method (probability vs convenience), invitation N, completed N, response rate, and any eligibility filters; whether an a priori power analysis or other sample-size justification appears; the provenance of the perceived-usefulness and self-reported-use instruments (adapted from a cited source vs author-generated), item counts, response scale anchors, and reported reliability (α or ω) and validity evidence; what "use" was operationalised as (frequency scale, hours, logins) and over what recall window; missing-data volume and handling method; the analytic procedure and whether it matches the measurement level of the variables; assumption checks appropriate to that procedure (normality, linearity, homoscedasticity, independence, multicollinearity/VIF where multiple predictors appear); effect sizes with magnitude interpretation and 95% CIs alongside test statistics and exact *p*-values; whether non-significant results are reported; common-method variance acknowledgement or remedy, since both constructs come from one instrument at one time from one respondent; ethics/IRB approval and consent statement; data, item-list, or code availability.
- **what_triggers_block**: Load-bearing methodology is absent or internally contradictory to a degree that the reported results cannot be evaluated or reproduced. Concretely, any of: the sample is described without an N, or Ns conflict irreconcilably across text and tables; no description of how participants were obtained, so selection bias cannot be bounded at all; the use and/or usefulness measure is presented with no items, no scale, no anchors, and no source, leaving the construct unauditable; the reported statistic is structurally wrong for the data (e.g., a correlation or regression run on variables that the text describes as categorical/ordinal-with-few-levels, with no acknowledgement); results are reported with no test statistics, df, or *p*-values in any form; or a stated analysis is reported for a variable the Methods never says was collected. Also block if the paper claims a causal or intervention effect and the design section reveals no mechanism (no manipulation, no temporal separation, no control) capable of supporting it — a design/claim mismatch that survives into the analysis is a rigor failure, not merely a wording one.
- **what_triggers_warn**: Methodology is followable and the results are evaluable, but reproducibility or interpretability is materially degraded by identifiable gaps. Concretely, any of: convenience or single-institution sampling used without acknowledgement of its limits on generalisability; response rate absent or so low that non-response bias is unaddressed; no sample-size justification or power analysis for the tests performed; reliability reported for one construct but not the other, or reported below the field-conventional threshold without comment; effect sizes omitted or reported without magnitude interpretation, or CIs absent for key estimates; assumption checks not mentioned; missing-data amount or handling method unstated; common-method bias unaddressed given the single-source single-timepoint design; recall window for self-reported use unspecified; ethics approval or consent unstated; no data/instrument availability statement. A single such gap in a 1597-word brief report warrants warn rather than block when the surrounding reporting is otherwise complete; an accumulation of them across sampling *and* measurement *and* analysis reporting moves the dimension toward block.

### D2: domain_accuracy
- **what_to_look_for**: Whether "perceived usefulness" is used with its established operational meaning in the technology-acceptance lineage rather than as a loose synonym for satisfaction, ease of use, or liking; whether "self-reported use" is consistently and accurately labelled as self-report throughout — including in the abstract, results, and conclusions — rather than sliding into "usage," "engagement," "activity," or "LMS log data" in later sections; whether LMS-specific terminology (module, activity, tool, access) is used with the technical meaning the platform literature assigns it; whether any reported statistic attributed to prior domain work is stated in a form consistent with what that class of study can produce; whether the constructs' relationship is described at a level of specificity the measures support.
- **what_triggers_block**: A domain-technical statement that is definitionally wrong in a way that invalidates the interpretation of the results — for example, self-reported frequency data described or analysed as objective platform log/telemetry data, or the paper's central construct defined in a way that contradicts the established definition it invokes by name, such that the reported association is not the association the paper claims to have measured. Note the seat boundary: I score this only when the error is a measurement-validity error; if it is a matter of literature representation or citation accuracy, I defer to Reviewer 2 and score no worse than warn here.
- **what_triggers_warn**: Terminology drifts across sections without an outright definitional error — self-report hedged in Methods but reported as plain "use" in the abstract or discussion; a domain construct invoked by name (TAM, UTAUT, engagement) without its accompanying operational definition, leaving the reader to supply it; imprecise but not false characterisation of what an LMS metric represents; or domain claims stated at a confidence the cited evidence class does not carry. Also warn if the paper attributes properties to its instrument (validated, standard, widely used) without stating for whom and in what population that validation holds.

### D3: argumentative_coherence
- **what_to_look_for**: The verb tense and modality of every claim linking usefulness to use — "associated with," "predicted," "explained variance in," versus "led to," "increased," "drives," "improves"; whether the stated research questions are the ones the analysis actually answers; whether the discussion's implications (design recommendations, intervention advice, policy suggestions) require a causal warrant the design cannot supply; whether reverse causation is acknowledged as a live alternative; whether common-method variance is treated as a rival explanation for the observed association; whether an analysis-unit shift occurs, such as student-level data supporting course-level, cohort-level, or institution-level conclusions; whether the limitations section names the constraints that actually bind this design rather than generic ones; whether non-significant or hypothesis-inconsistent findings are carried into the discussion or quietly dropped.
- **what_triggers_block**: The paper's headline conclusion — the claim in the abstract or the discussion's opening argument — depends on an inference the design cannot license, and this is not hedged anywhere. Specifically: unconditional causal language about usefulness perceptions producing use (or intervention/policy prescriptions that only follow if that causal claim holds) drawn from single-timepoint correlational data, with no acknowledgement of directionality or third-variable alternatives; or a conclusion contradicted by the paper's own reported results (an effect described as substantial where the reported statistic is negligible, a relationship claimed where the test did not support it); or an ecological/atomistic shift in analysis unit that the conclusion depends on. The threshold is dependency: block when removing the unlicensed inference collapses the paper's contribution.
- **what_triggers_warn**: The core argument holds but contains identifiable slack — occasional causal-flavoured verbs in the discussion while the results section stays correlational; limitations acknowledged in a boilerplate paragraph that does not name reverse causation or common-method bias specifically; implications stated more broadly than the single-population sample supports; the abstract stronger in modality than the results section; hypothesis-consistent findings foregrounded and non-significant ones mentioned only in a table without discussion; or a plausible confound (prior LMS experience, course requirement to use the system, instructor mandate, digital access, year of study) that goes entirely unaddressed while the argument implicitly assumes it away.

### D4: cross_disciplinary_relevance
- **what_to_look_for**: Whether constructs are defined at first use in plain terms rather than assumed as field shorthand; whether the statistical reporting is self-interpreting to a reader outside educational technology (magnitudes contextualised, scales stated, direction of effect explicit); whether the instrument is described well enough for a researcher in an adjacent field to evaluate or reuse it without obtaining the original source; whether any claim reaching into an adjacent field — learning outcomes, retention, institutional policy, psychological mechanism — carries measurement evidence proportional to the reach; whether the setting is described concretely enough (institution type, LMS platform, course context, degree level) for another field to judge applicability.
- **what_triggers_block**: A cross-disciplinary claim is made central to the paper's contribution while the methodology provides no measurement of the construct that claim concerns — for example, a headline claim about learning outcomes, achievement, or retention when nothing outcome-related was measured. A methodological void beneath an interdisciplinary claim is my seat's business and blocks; mere inaccessibility of framing is not, and I will route that to Reviewer 3 rather than block on it.
- **what_triggers_warn**: Constructs used as unglossed field shorthand; effect sizes or coefficients reported without the interpretive context an outside reader needs; instrument described only by citation, so an adjacent-field reader cannot assess it; the study setting under-specified (platform unnamed, institution type or discipline mix unstated) in ways that block transfer judgements; implications reaching into adjacent domains stated with confidence but supported only by the same single self-report instrument.

### D5: writing_and_structure
- **what_to_look_for**: Presence and ordering of the sections the methodological record requires (design, participants, measures, procedure, analysis) even in compressed brief-report form; whether the Methods narrative runs in a sequence a replicator could follow; whether every number in the text reconciles with the corresponding table or figure and every table carries its N, units, and note on what the values represent; APA 7.0 statistical formatting (italicised symbols, no leading zero on bounded values, correct decimal places, exact *p* rather than bare inequality thresholds where reportable); whether the abstract's numbers match the body's; whether the limitations, ethics, and availability statements exist as locatable sections rather than being scattered.
- **what_triggers_block**: The manuscript's organisation makes the methodological record unrecoverable — no identifiable Methods content anywhere, so design, participants, and measures cannot be located; or results reported in a form so internally inconsistent (numbers in the abstract, text, and tables mutually contradictory with no way to determine which is authoritative) that no reading of the paper yields a stable set of findings. This is a high bar for a structure dimension and I expect to reach it rarely; presentational weakness alone does not qualify.
- **what_triggers_warn**: Methods content is present but distributed across sections so that reconstructing the procedure requires assembling it from several places; a table or figure lacks its N, units, or explanatory note; minor numeric discrepancies between abstract, text, and tables; APA 7.0 statistical formatting deviations; no separate limitations section, with constraints instead folded into the discussion; missing ethics or data-availability statement as a structural omission (noting that its substantive absence is scored at D1, and I will not double-count the same defect as a serious finding in both places).

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Methodology Review Report (Peer Reviewer 1)

### Reviewer Identity

Quantitative survey methodologist in an educational-measurement department, specializing in self-report validity and common-method variance in single-instrument designs; publishes on attenuation from coarse ordinal categorization and on nonresponse bias in voluntary institutional surveys; routine statistical reviewer for education and information-systems journals.

### Overall Recommendation

Major Revision

### Confidence Score

4

### Summary Assessment

This is a competently executed and unusually well-calibrated correlational survey whose reported inferential statistics I verified by hand and found correct: the Fisher-*z* interval for *r* = .42 at *n* = 214 is [.303, .525], matching the reported [.30, .52] to two decimals, and *n* = 214 does give power > .80 to detect *r* ≈ .190 at α = .05 two-tailed. The sensitivity statement is prospective rather than a post-hoc observed-power fallacy, the Spearman check is the right instinct for an ordinal outcome, and the correlational register holds without exception from abstract through conclusion. What the manuscript lacks is not competence but documentation and one layer of analytic scrutiny it has not applied to its own headline number.

Three problems are load-bearing. First, the sampling denominator is absent although the eligibility criterion ("all enrolled undergraduates") guarantees the authors hold it, so no response rate exists and non-response bias cannot be bounded. Second, §3.1's removal of five duplicate entries cannot be reconciled as written with §3.3's claim that responses could not be linked to individuals. Third, *r* = .42 sits between two unexamined opposing biases — shared-method inflation and attenuation from a five-category outcome — neither of which the Spearman check addresses. Every requested addition is recoverable from material the authors already possess, which makes this correctable rather than fatal.

### Strengths

1. **Reported statistics are independently verifiable and correct**: I recomputed both key quantities. Fisher-*z* back-transformation at *n* = 214 gives [.3029, .5246]; the manuscript's [.30, .52] is right, and rounding the upper bound to .53 would be the error. The detectable-effect calculation returns *r* ≈ .190 against the claimed ≥ .19.
   - **Evidence Anchor**: `text: §4 "r = .42, 95% CI [.30, .52], p < .001, n = 214"; §3.4 "greater than .80 power to detect a correlation of r >= .19 at alpha = .05 (two-tailed)"` | **Confidence**: 5 — recomputed by hand
2. **Sensitivity framing is prospective, not observed power**: §3.4 states what the design could have detected, not the power of the obtained effect. This is the correct construction and is more often got wrong than right in this literature.
   - **Evidence Anchor**: `text: §3.4 "so the design was sensitive to small-to-moderate associations"` | **Confidence**: 5
3. **The robustness check is matched to the measurement level, and its rationale is stated**: the ordinal nature of the outcome is named as the reason for computing ρ, and both coefficients are reported rather than only the more favourable one.
   - **Evidence Anchor**: `text: §3.4 "Because the use item is ordinal, we also computed a Spearman correlation"; §4 "(ρ = .40)"` | **Confidence**: 5
4. **Design–claim alignment is maintained without exception, and the reverse pathway is named specifically rather than generically**: §5 identifies the use → perception direction as "equally consistent with the data" and attributes the caution to a source. No causal verb survives anywhere in the abstract, results, discussion, or conclusion. This is the discipline my seat most often finds missing in cross-sectional acceptance work.
   - **Evidence Anchor**: `text: §5 "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"` | **Confidence**: 5
5. **Ethics reporting is complete on its procedural face**: committee approval, voluntariness, absence of incentive, and consent obtained at point of entry are each stated. (The anonymity clause in the same subsection is separately problematic — see W2.)
   - **Evidence Anchor**: `text: §3.3` | **Confidence**: 4
6. **Attrition accounting is arithmetically transparent and reconciles**: 233 − 14 − 5 = 214, and the same *n* appears in the abstract, methods, results, and conclusion with no drift.
   - **Evidence Anchor**: `text: §3.1 "233 responses were received; 14 incomplete submissions and 5 duplicate entries were removed, leaving 214 valid responses"` | **Confidence**: 5

### Weaknesses

1. **No sampling denominator, so no response rate and no bound on non-response bias**: §3.1 states that all enrolled undergraduates were eligible, which by construction makes the eligible *N* available to the authors from enrolment records, yet it is not reported. Without it, 233 received responses cannot be converted into a participation rate, and the voluntary-response concern acknowledged in §6 remains an unquantified acknowledgement rather than a bounded threat. "Spanned all four year levels" is not a sample description: no distribution by year, discipline group, or enrolment status is given. Remedy: report eligible *N* and the computed response rate, add a respondent-composition table, and compare that composition against institutional population figures — a benchmark already in the authors' possession — so non-response bias is characterised empirically rather than by assertion.
   - **Severity**: Major | **Evidence Anchor**: `absence: §3.1 — checked §3.1, §3.3, §6; no eligible N, no response rate, no demographic distribution` | **Confidence**: 5 — nonresponse bias in voluntary institutional surveys is my publication area
2. **Duplicate removal cannot be reconciled with the anonymity claim as written**: §3.1 removes five duplicate entries; §3.3 states that no identifying information was collected and that responses could not be linked back to individual students. Detecting duplication requires some persistent discriminator — IP address, session cookie, device or browser fingerprint, an institutional single-sign-on token, or response-pattern matching. Either such a discriminator was captured, in which case §3.3's second clause is inaccurate as stated, or the removals were heuristic, in which case the rule needs stating because pattern-based deduplication can delete valid independent responses. Remedy: state the detection mechanism; state whether it was disclosed on the consent landing page; and state whether the approved protocol characterised the collection as anonymous or as de-identified, since only one of those supports §3.3. I note the boundary of my seat: if an undisclosed identifier was in fact captured, that is a protocol-fidelity matter for the editorial office rather than a methodology reviewer's finding to adjudicate.
   - **Severity**: Major | **Evidence Anchor**: `text: §3.1 "5 duplicate entries were removed" against §3.3 "responses could not be linked back to individual students"` | **Confidence**: 5 — internal contradiction is on the page, not a matter of judgement
3. **Common-method variance is never raised**: both variables come from one instrument, one respondent, one administration. The observed association is therefore exposed to upward bias from consistent response style, priming across adjacent items, and social desirability regarding a mandated institutional platform. §6's second limitation addresses a different threat — whether the self-report measures actual behaviour — and does not touch shared-method inflation of the *association*. Remedy: name common-method variance as a rival explanation in §6; report whether the perceived-usefulness block and the use item were separated within the instrument (page break, intervening blocks, order randomisation), which is a design fact already determined and costs nothing to state; and if any candidate marker variable was collected, report a marker or single-factor test.
   - **Severity**: Major | **Evidence Anchor**: `absence: checked §2, §3.2, §3.3, §3.4, §5, §6 — no mention of common-method variance, no procedural separation reported, no marker test` | **Confidence**: 5 — common-method variance in single-instrument designs is my specialisation
4. **Two opposing biases act on *r* = .42 and neither is bounded**: collapsing use onto five categories of undefined and unequal width attenuates a Pearson estimate, while shared method inflates it. The Spearman check tests whether the association survives relaxation of the linearity assumption; it does not recover information lost to coarseness, so ρ = .40 is not evidence against attenuation. As reported, the estimate is offered as comparable with prior work whose method-variance exposure and outcome granularity differ. Remedy: report a polyserial or polychoric estimate — the estimator matched to a continuous composite paired with an ordinal item — and optionally an estimate disattenuated for α = .88; then present .42 as the naive coefficient flanked in both directions rather than as a point estimate ready for cross-study comparison. This is the single revision most likely to change what the headline number means.
   - **Severity**: Major | **Evidence Anchor**: `text: §3.4 "Because the use item is ordinal, we also computed a Spearman correlation as a robustness check."` | **Confidence**: 5 — attenuation from coarse categorization is my publication area
5. **Independence of observations is neither established nor discussed**: recruitment ran through a course-announcement channel, which draws respondents unevenly from courses, and the outcome — weekly access frequency — is plausibly driven by course-level structure such as instructor posting cadence and assessment windows. Responses from students in the same course are therefore unlikely to be independent, and a Pearson standard error computed as if they were yields a confidence interval narrower than warranted. The reported [.30, .52] is the manuscript's precision claim, so this bears directly on the central result. Remedy: report how many courses or programmes the channel reached; if any course or programme identifier exists, re-estimate with a cluster-robust or random-intercept treatment; if none exists, state that plainly and report a year-level-stratified check (year level is known, per §3.1) alongside a note that the interval is likely optimistic.
   - **Severity**: Major | **Evidence Anchor**: `absence: §3.1 recruitment description and §3.4 analysis — checked both; no clustering, design effect, or independence discussion` | **Confidence**: 4
6. **Neither variable is documented well enough to audit or reproduce**: for perceived usefulness, the six items are never reproduced, "adapted" is never unpacked into what changed, and α = .88 establishes internal consistency, not the unidimensionality that a mean composite presupposes — no factor analysis, eigenvalue report, or item-total statistics appear. For the outcome, the intermediate category labels (2, 3, 4) are never stated, so category widths are undefined, and the reported median "a few times per week" is a label absent from the scale as presented, leaving the reader unable to place the outcome's central tendency on the 1–5 metric. Remedy: an appendix with all six items verbatim, the five outcome category labels, a sentence per adapted item, and one-factor confirmatory evidence (or at minimum a PCA eigenvalue report) for the composite.
   - **Severity**: Major | **Evidence Anchor**: `absence: §3.2 in full, plus §4 — no item wording, no adaptation log, no dimensionality evidence, categories 2–4 unlabeled` | **Confidence**: 5
7. **"Previously validated" is claimed for the adapted instrument on evidence that covers only the original's reliability**: the abstract describes "an adapted, previously validated instrument" and §2 "a previously validated measure," while the only supporting evidence in §3.2 is that the source instrument "reported strong internal consistency." Internal consistency is a reliability property and is not validity; neither property transfers automatically across an adaptation whose content is unstated, and no validation population, language, or setting is given for the original. This is a measurement-validity claim rather than a citation matter, which is why I score it here. Remedy: either name the validity evidence class from the source (content, convergent, discriminant, criterion) with its validation population, and argue transfer to this population explicitly; or drop "validated" and describe the scale as adapted with internal consistency demonstrated in-sample. I note that this weakness cannot be closed by citation alone under any resolution of the source-verification question the editorial office is pursuing — the items and the adaptation log have to appear in the manuscript.
   - **Severity**: Major | **Evidence Anchor**: `text: Abstract "an adapted, previously validated instrument"; §3.2 "adapted from Costa and Wren (2019), whose original instrument reported strong internal consistency"` | **Confidence**: 5
8. **Instrument and setting are under-specified for an adjacent-field reader to assess or transfer**: the instrument is available only via its citation, so a measurement or learning-analytics researcher cannot evaluate or reuse it without obtaining the source. The LMS platform is unnamed, the discipline mix unreported, and course-level mandatory-use policy unstated. The three-week window's position in the academic calendar is also absent, and this one is load-bearing rather than cosmetic: "a typical week" is not scale-invariant across a term, and a window over midterms yields a different frequency distribution than one in week two. Remedy: name platform and version, state mandate status, and give the window's calendar position. I flag that the setting-context half of this finding is likely to converge with the practical/institutional reviewer's seat and should be counted once.
   - **Severity**: Major | **Evidence Anchor**: `absence: §3.1, §3.2 — checked for platform, discipline mix, mandate status, calendar position; none reported` | **Confidence**: 4
9. **No exhibits, and one assumption check asserted rather than shown**: the manuscript contains zero tables and zero figures. §3.4 reports that "scatterplot inspection showed an approximately linear, monotonic association with no extreme bivariate outliers" and that both distributions were approximately symmetric, asking the reader to accept diagnostics on the authors' report of having looked at a plot that is not provided — and symmetry of a five-category item cannot be checked at all without its frequency distribution. *r*² is characterised verbally as modest but never stated (.18), and no interval accompanies ρ. Remedy: one descriptive table (*M*, *SD*, and the full outcome frequency distribution with *n* per category), the scatterplot in a form suited to an ordinal axis, the numeric *r*², and a bootstrap interval for ρ.
   - **Severity**: Minor | **Evidence Anchor**: `absence: manuscript-wide — zero tables, zero figures; §3.4 diagnostics asserted; §4 r² not numerically reported` | **Confidence**: 5
10. **"Engagement" is substituted for the measured construct at the manuscript's outer edges**: the abstract closes on "perceived usefulness tracks with LMS engagement," §4 refers to "reported engagement," and §5 to factors "bearing on engagement." What was measured is self-reported access frequency in a typical week. In the learning-analytics and educational-psychology literatures the paper reaches into — it cites Vasquez (2020) on behavioural logs — engagement is a multi-component construct and access frequency is a thin indicator of one behavioural component. The rest of the manuscript is scrupulous about saying "self-reported use," which makes the drift read as inadvertent. Remedy: use "self-reported LMS access frequency" in all three places, or state explicitly that access frequency is being used as a narrow proxy for one component of engagement and cite the literature licensing that mapping.
    - **Severity**: Minor | **Evidence Anchor**: `text: Abstract "perceived usefulness tracks with LMS engagement among undergraduates"` | **Confidence**: 4
11. **"Incomplete" is never operationalised, and item-level missingness among retained cases is silent**: fourteen submissions were removed as incomplete with no threshold stated, and nothing is said about whether any of the 214 retained cases had missing values on the six perceived-usefulness items or how the mean composite handled them. With a six-item mean, the choice between a prorated mean and listwise exclusion is consequential and is currently invisible. Remedy: state the completeness rule and the composite's missing-data handling.
    - **Severity**: Minor | **Evidence Anchor**: `text: §3.1 "14 incomplete submissions ... were removed"` | **Confidence**: 4
12. **APA 7.0 statistical formatting deviations**: statistical symbols are not italicised anywhere (*r*, *p*, *n*, *SD*, *M*, ρ); §3.4 mixes ASCII "alpha = .05" and "r >= .19" with the α glyph used in §3.2; descriptive precision is inconsistent, with a one-decimal mean and *SD* ("3.6 (SD = 0.8)") set against two-decimal correlations where convention here is *M* = 3.60, *SD* = 0.80; and the mean is reported without an interval. Remedy: a formatting pass against APA 7.0 §6.
    - **Severity**: Minor | **Evidence Anchor**: `text: §3.4 "alpha = .05 (two-tailed)"; §4 "mean perceived-usefulness score of 3.6 (SD = 0.8)"` | **Confidence**: 5
13. **No data or materials availability statement**: none appears, nor any preregistration statement. The consequence is specific to this paper's stated purpose: §2 offers the result as "an incremental data point, comparable with prior work," and that contribution is realised only if others can pool or re-estimate it. The analysed dataset is two variables over 214 rows which §3.3 states carry no identifying information, so item-level deposit is unusually low-cost and would let readers compute polychoric estimates and include the study in later synthesis. Remedy: deposit item-level data and the instrument, or state the specific barrier.
    - **Severity**: Minor | **Evidence Anchor**: `absence: manuscript-wide — checked §3.3, §3.4, §7, and back matter; no availability, funding, conflict-of-interest, or preregistration statement` | **Confidence**: 4

### Detailed Comments

#### Research Questions & Hypotheses

The question is stated once, narrowly, and in the form the design can answer: whether perceived usefulness is associated with self-reported use frequency among undergraduates at one university (§1). No hypothesis is advanced, which is appropriate for a descriptive correlational study and forecloses the HARKing and selective-support failure modes. The declared decision not to test a full acceptance model is a scope choice, not a defect, and I assess the paper against the question it asked.

#### Research Design

The design is named ("cross-sectional survey study," §3.1), its timepoint structure is unambiguous, and its inferential ceiling is respected throughout. No manipulation, temporal separation, or comparison condition is claimed, and no conclusion requires one. The design–claim mismatch that my Phase 1 plan flagged as a block trigger is absent here.

#### Sampling Strategy

This is the weakest link in the methodological record. Eligibility is universal, recruitment is via a single institutional channel, participation is voluntary, and the denominator is missing (W1). Sample-size adequacy is, unusually, addressed well — the prospective sensitivity statement is correct and correctly framed — so the problem is not sample size but the inability to characterise who the 214 are relative to who they could have been. The recruitment route additionally raises the clustering question in W5, which the manuscript does not reach.

#### Data Collection

One self-administered online instrument, one administration, three-week window. Perceived usefulness is a six-item Likert composite; use is a single ordinal item. Neither instrument is reproduced (W6), the adaptation is undocumented (W7), and the outcome's intermediate anchors are missing, which is what makes the reported median uninterpretable against the scale. The single-source single-occasion structure is precisely the configuration in which common-method variance is a first-order concern, and it goes unmentioned (W3).

#### Analysis Methods

The analytic choices are sound and conventionally reported: Pearson as primary, Spearman as a stated robustness check justified by the outcome's measurement level, an interval and exact-threshold *p* alongside *n*, and reported linearity, monotonicity, symmetry, and outlier inspection. My Phase 1 plan named "a correlation run on an ordinal variable with few levels, with no acknowledgement" as a block trigger; the acknowledgement is present and the mitigation is the field-conventional one, so the trigger does not fire by its own terms. What remains is that the mitigation is incomplete in a specific and correctable way (W4) and that independence is untreated (W5).

**Statistical reporting adequacy (Step 4a): Adequate** — at the upper end of the band, held back from Exemplary by four gaps. Effect size: present (the coefficient is the effect size), with magnitude interpreted, though *r*² is described rather than stated. Confidence intervals: present and arithmetically correct for the primary estimate; absent for ρ and for the mean. Power: prospective sensitivity reported and correct; no Type II discussion is needed since no non-significant test is reported. Assumptions: linearity, monotonicity, symmetry, and outliers addressed narratively but not evidenced, and independence not addressed at all. Missing data: exclusion counts given, definitions and item-level handling not. APA compliance: deviations at W12. Red-flag scan: no indication of p-hacking, HARKing, selective reporting, or uncorrected multiple comparisons — one primary test, one preplanned robustness check, both coefficients reported, no subgroup exploration. The red flags I do raise are the unbounded opposing biases and the untreated clustering, neither of which implies researcher-degrees-of-freedom abuse.

#### Results Presentation

Complete for what it reports and free of selective-reporting signals; both coefficients appear, the weaker robustness value included. Presentation, however, rests entirely on running text: no exhibits at all, a median reported against an incompletely labelled scale, an asserted-but-unshown scatterplot, and *r*² withheld as a number (W9). Every figure in the abstract, body, and conclusion agrees, so there is no numeric-reconciliation problem — the record is thin rather than inconsistent.

#### Reproducibility

Partial. A second team could reproduce the *analysis* from the reported coefficients but not the *study*: they could not reconstruct the instrument (W6, W7), could not reproduce the sampling frame or judge who responded (W1), could not replicate the cleaning rules (W2, W11), and could not obtain the data (W13). Ethics review and consent are documented (S5). The gap between analytic and procedural reproducibility is the fairest one-line summary of this manuscript's condition.

#### Methodological Fallacies Detected

Screened against the full checklist; most are absent and I record that explicitly rather than manufacturing hits.

- **Reverse causation** — screened, not detected. Explicitly pre-empted in §5 and named in §2 via Delgado (2020).
- **Confirmation bias / selective reporting** — screened, not detected. Single primary test, both coefficients reported, no hypothesis to confirm.
- **P-hacking / uncorrected multiple comparisons** — screened, not detected. One test, one preplanned robustness check, prospective power statement, no subgroup analyses.
- **Ecological / atomistic fallacy** — screened, not detected. Measurement, analysis, and inference all sit at student level.
- **Survivorship / self-selection bias** — partially present and partially acknowledged. §6 names voluntary response; the unaddressed residue is that no denominator exists to gauge its magnitude (W1).
- **Endogeneity, multicollinearity, overfitting** — not applicable to a bivariate association; the omitted-variable concern is acknowledged narratively in §4 ("course requirements and assessment schedules") without being measured.
- **Detected, not on the standard checklist**: attenuation by coarse categorization and common-method variance operating in opposite directions on the same coefficient (W3, W4); and violated-independence risk from course-clustered recruitment (W5).

No instruction-injection or reviewer-directed content was present in the manuscript; nothing in it attempted to alter my scoring or format.

**Not scored as findings.** The manuscript states, at appropriate severity, that the design cannot support causal inference, that a single institution limits generalisation, that self-report diverges from behavioural logs, that the association is moderate rather than strong, and that voluntary response skews participation. Restating any of those back to the authors would be reporting their own text as a finding, and I have not done so. They enter my review only where the paper states a caution and then does not act on it — as at W3, where the self-report caution covers the outcome's validity but not the association's method-variance exposure.

### Questions for Authors

1. What was the eligible undergraduate *N*, and what response rate does 233 received responses represent? How does the composition of the 214 compare with institutional figures on year level, discipline group, and enrolment status?
2. By what mechanism were the five duplicate entries identified, was that mechanism disclosed on the consent landing page, and does the approved protocol describe the collection as anonymous or as de-identified?
3. What threshold defined an "incomplete" submission, and did any retained case have missing values on the perceived-usefulness items? If so, how was the six-item mean computed?
4. Please supply the six perceived-usefulness items verbatim, the five outcome category labels, and a statement of what the adaptation from the source instrument changed. Which class of validity evidence does the source report, and in what population?
5. Is there evidence bearing on the composite's unidimensionality — a factor analysis, eigenvalues, or item-total correlations?
6. Were the perceived-usefulness block and the use item separated within the instrument, and was item order randomised? Was any variable collected that could serve as a method marker?
7. How many courses or programmes did the announcement channel reach, and does any course, programme, or year identifier exist in the dataset that would permit a clustering check?
8. Can you report a polyserial or polychoric estimate alongside *r* = .42, so the coarseness-attenuation and method-inflation bounds on the association are visible to the reader?
9. Which weeks of the academic term did the three-week window cover, which LMS platform and version was in use, and was LMS use required at course level for any respondents?
10. Can the item-level dataset and instrument be deposited? If not, what is the barrier?

### Minor Issues

- §3.4 writes "alpha" and ">=" in ASCII while §3.2 uses the α glyph; unify the notation.
- §4's "The proportion of variance shared by the two measures was accordingly modest" should carry the number (*r*² = .18).
- §4 reports the median category as "a few times per week," a label that appears nowhere in §3.2's scale description; give the numeric category alongside the label.
- Statistical symbols are unitalicised throughout; *M* and *SD* should be reported to the same precision as the correlations.
- The abstract reports *r* and *p* but omits the interval that §4 supplies; including [.30, .52] would let the abstract stand alone.

---

contract_role: methodology

## Dimension Scores

### D1: methodology_rigor
score: warn

Driven by W1, W2, W3, W4, W5, W6, W9, W11, W13. Threshold application, stated so the deviation from my Phase 1 language is not silent: my plan said accumulation across sampling *and* measurement *and* analysis reporting "moves the dimension toward block," and that accumulation is present. It stops short of block because none of my enumerated block conditions is met — *n* is stated and reconciles across every mention, recruitment is described well enough to name the selection mechanism, both measures have a scale and stated anchors, test statistics and interval and *p* and *n* are all present and arithmetically correct, no analysis is reported for an uncollected variable, and no causal or intervention effect is claimed. The Pearson-on-ordinal condition I pre-committed to as a block trigger carried the qualifier "with no acknowledgement"; §3.4 acknowledges it and applies the conventional mitigation, so the trigger does not fire. This sits at the top of warn. What would move it to block on resubmission: a response to W2 revealing that a persistent identifier was captured contrary to §3.3 and to the consent text, or a polychoric or cluster-adjusted re-estimate that materially relocates the coefficient while the manuscript continues to present .42 as its headline.

### D2: domain_accuracy
score: warn

Driven by W7 alone. My Phase 1 warn trigger — the paper attributes "validated" to its instrument without stating for whom and in what population the validation holds — fires exactly, and is compounded because the only cited evidence is the source's internal consistency, a reliability property, transferred across an adaptation of unstated content. This is a measurement-validity error and therefore mine; I do not touch literature representation, citation accuracy, or source verifiability, which belong to Reviewer 2 and the editorial office. Not block: the constructs are not definitionally wrong. §2 renders perceived usefulness in its established acceptance-lineage sense, and self-report labelling is accurate and consistent in the title, abstract, methods, results, discussion, limitations, and conclusion — no point in the manuscript treats the frequency item as log or telemetry data, which is the block-level error this literature usually produces.

### D3: argumentative_coherence
score: pass

No weakness is charged here, and I record why rather than letting a pass read as inattention. Every warn trigger I committed to requires either boilerplate limitations or unhedged over-reach, and neither exists. The limitations name the four constraints that actually bind this design rather than generic ones; reverse causation is named specifically and attributed; modality is uniform across abstract, results, discussion, and conclusion; no analysis-unit shift occurs; the practical implication in §5 is triple-hedged and explicitly marked as "suggested by, not proven by" the correlation. Two candidate charges I considered and declined: the common-method omission is real but degrades the interpretation of the estimate rather than the structure of the argument, so it is scored once at D1 and not double-counted here; and the directional asymmetry of the onboarding recommendation — that the acknowledged reverse pathway would support the opposite intervention equally well — is assigned to the practical reviewer's seat, and charging it here would stack one issue twice. My Phase 1 confound trigger required a plausible confound going "entirely unaddressed"; course requirements and assessment schedules are named in both §4 and §5, so it does not fire by its own terms.

### D4: cross_disciplinary_relevance
score: warn

Driven by W8 and W10. The instrument is available to an adjacent-field reader only through its citation, which matches my committed trigger for instrument inaccessibility, and the setting is under-specified in ways that block transfer judgements — platform unnamed, discipline mix unreported, mandate status unstated, calendar position of the survey window unstated. W10's substitution of "engagement" for a single access-frequency item reaches into learning-analytics vocabulary without the measurement that borrowing requires. Not block: my block condition required a cross-field claim central to the contribution with no measurement beneath it, and there is none — nothing is claimed about learning outcomes, achievement, or retention, and the "engagement" wording sits at the manuscript's edges while the title, question, result statement, and conclusion all say "self-reported use." Deleting the engagement phrasing costs the paper nothing, which is the test of centrality. The setting-context portion of W8 is likely to converge with the practical reviewer's seat and should be counted once at synthesis.

### D5: writing_and_structure
score: warn

Driven by W12 and the presentational face of W9. My committed trigger for APA 7.0 statistical formatting deviations fires on its own terms and independently of D1's substantive gaps: unitalicised statistical symbols throughout, mixed ASCII and glyph notation between §3.2 and §3.4, and inconsistent decimal precision. The presentational finding is that a five-category ordinal outcome is summarised by a median whose label does not appear in the stated scale, and that an assumption check is asserted against a plot the reader never sees. Per my Phase 1 commitment I am not double-counting: the substantive absence of a descriptive table, the frequency distribution, and the availability statement is charged at D1, and only the presentation defects are charged here. Not block, and not close to it: prose is clean and controlled, section order is conventional and complete, Methods runs in replicable sequence across four labelled subsections, Limitations is a separate locatable section, and every number agrees across abstract, body, and conclusion, so the methodological record is recoverable and the findings are stable.

## Failure Condition Checks

### F1
fired: false

Predicate: any mandatory dimension scores block. My mandatory dimensions are D1 warn, D2 warn, D3 pass. No block, so this condition does not fire and its reject-or-major-revision action is not in play from my seat.

### F2
fired: true

Predicate: two or more mandatory dimensions score warn or worse. D1 warn and D2 warn satisfy it at exactly two. This is the highest-severity condition firing on my scores (severity 70) and therefore governs my editorial decision.

### F3
fired: false

Predicate: any high-priority dimension scores block. D4, the only high-priority dimension, scores warn. Not fired.

### F0
fired: false

Predicate: every mandatory dimension scores pass. D1 and D2 both score warn, so the accept-grade condition is unsatisfied.

## Review Body

The methodology here is competent and honestly reported, and the paper's central numbers survive independent recomputation. I verified both quantities a statistical reviewer should verify before criticising: the Fisher-*z* interval for *r* = .42 at *n* = 214 is [.3029, .5246], so the reported [.30, .52] is correct to two decimals, and the sensitivity claim resolves to a detectable *r* of .190 against the stated ≥ .19. The power statement is prospective rather than observed, the Spearman check is the right instinct for an ordinal outcome and its rationale is stated, the correlational register never slips across abstract, results, discussion, or conclusion, the reverse pathway is named specifically rather than gestured at, ethics approval and consent are documented, and the attrition arithmetic reconciles. A reviewer who told these authors that correlation is not causation, that one institution limits generalisation, or that self-report is not behaviour would be reading the manuscript's own sentences back to it, and I have deliberately not done that.

What holds the paper at major revision is a cluster of documentation gaps dense enough to defeat procedural reproducibility, plus one analytic layer the authors have not applied to their own headline number. On sampling, the eligibility criterion guarantees the authors hold an enrolment denominator, yet none is reported, so 233 received responses cannot become a response rate and the voluntary-response skew that §6 concedes stays unquantified; the recruitment route also makes course-level clustering likely, which the analysis treats as absent and which, if present, means the reported interval is narrower than the data support. On measurement, the six perceived-usefulness items are never shown, the adaptation is never described, α = .88 is offered where a mean composite needs unidimensionality evidence, the outcome's intermediate anchors are missing so the reported median cannot be located on the scale, and "previously validated" is asserted in the abstract on the strength of a reliability statistic about a different, unmodified instrument in an unnamed population. On analysis, *r* = .42 sits between two forces the manuscript never bounds: coarse five-category measurement pulls the Pearson estimate down, and a single instrument administered once to one respondent pulls it up. The Spearman check addresses the linearity assumption, not the information lost to coarseness, and nothing anywhere addresses shared method. A polyserial or polychoric estimate plus an explicit statement of method-variance exposure would let readers see .42 as a naive coefficient flanked in both directions rather than as a value ready for comparison against studies with different measurement granularity.

Two findings deserve particular emphasis for opposite reasons. The duplicate-removal contradiction is not a matter of reviewer judgement: §3.1 reports removing five duplicates and §3.3 reports that responses could not be linked to individual students, and both cannot be true as written. It requires a factual answer about what discriminator was captured, whether participants were told, and how the approved protocol characterised the collection — and if the answer is that an undisclosed identifier existed, the matter passes beyond my seat to the editorial office. The common-method omission, by contrast, is the finding most likely to be mistaken for one the paper already made. It has not: §6's self-report limitation concerns whether the outcome measures behaviour, which is a validity question about one variable, while common-method variance concerns inflation of the association between two variables measured the same way at the same moment. Only the first is currently covered.

On threshold application: I committed in Phase 1 that accumulation across sampling, measurement, and analysis reporting would move D1 toward block, and the accumulation is present. I have nonetheless scored warn, because every block condition I enumerated is unmet — *n* is stated and consistent everywhere, selection is describable, both measures have scales and anchors, the full statistical quartet is reported and correct, no analysis outruns the collected variables, and no causal effect is claimed. My Pearson-on-ordinal block trigger carried the qualifier "with no acknowledgement," and the acknowledgement is on the page. This is warn at its ceiling, not warn as a courtesy, and I have named above what would convert it to block on resubmission. Two mandatory dimensions at warn trigger F2, which is the governing condition from my seat. The character of the required revision matters for the synthesis: not one of the thirteen weaknesses requires new data collection, and every requested artifact — denominator, deduplication rule, item wording, adaptation log, dimensionality evidence, frequency distribution, polychoric estimate, clustering check, calendar dates, descriptive table, scatterplot — is derivable from material the authors already hold. This manuscript is under-documented and under-analysed at one specific joint, not defective.

## Editorial Decision

Derived from the contract's failure-condition precedence applied to my dimension scores: F2 is the only condition fired, at severity 70, and F1 and F3 are unfired, so no higher-severity action applies.

editorial_decision=major_revision

---

## SEAT — Peer Reviewer 2 (Domain)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** As Peer Reviewer 2 I read this dimension through a domain-accuracy lens only: I do not adjudicate the technical adequacy of the sampling frame, the statistical estimator, or the reproducibility package, which belong to Reviewer 1. What I own is whether the operational choices are *the ones this field recognises* for the constructs named in the title — whether "perceived usefulness" is measured with an instrument traceable to the established technology-acceptance scale literature rather than an ad-hoc item set presented as if equivalent, and whether "self-reported use" is treated as the proxy variable the field knows it to be rather than as behavioural use. A cross-sectional survey of undergraduates is a legitimate design in LMS adoption research; my concern is not that the design is weak but that the domain-level warrant attached to it matches what that design can carry in this literature. Where a reporting expectation I invoke rests on a field norm (instrument provenance, reliability reporting, observational-study reporting guidance), I will ground it in a checkable external source or down-rate per the Step 5 rule.

**D2 — domain_accuracy (mandatory).** This is my primary dimension. I will assess whether the paper's claims sit correctly inside the current evidence base on LMS adoption and engagement in higher education: whether the acceptance-model lineage it draws on is attributed to its original sources rather than to review articles, whether the constructs it borrows (perceived usefulness, perceived ease of use, behavioural intention, actual use) carry their canonical definitions or have been silently redefined, and whether the paper represents prior findings as they actually stand — including the well-established gap between self-reported and log-derived system use, and the heterogeneity of reported usefulness–use associations across institutional contexts. Terminological precision matters here in a field-specific way: "use", "usage", "adoption", "engagement", and "learning" are distinct constructs in this literature and are frequently conflated. I will also check whether the paper's characterisation of the field's state of knowledge is current, since LMS research has moved substantially since the emergency-remote-teaching period, and whether a contrary body of evidence has been omitted in a way that changes the paper's warrant rather than merely shortening its reference list.

**D3 — argumentative_coherence (mandatory).** I evaluate whether the chain running from the paper's framing to its conclusion holds together as a domain argument. The structural risk in a cross-sectional perceived-usefulness/self-reported-use study is well known to this field: an association between two self-reported measures collected in one instrument at one time can be narrated into a causal or directional claim ("usefulness drives use") without the design supporting it, and common-method variance can be presented as substance. I will therefore trace whether each conclusion sentence is entailed by the evidence actually offered, whether the theoretical frame is doing argumentative work or is named and abandoned, whether the stated contribution is the contribution the results deliver, and whether practical recommendations addressed to instructors or institutions are licensed by the findings or are appended as unsupported extrapolation. Internal consistency between the paper's own statements — how it describes its variables early versus how it interprets them late — is part of this dimension for me.

**D4 — cross_disciplinary_relevance (high).** Reviewer 3 owns cross-disciplinary impact; my slice is narrower and remains a domain-accuracy question. LMS adoption research is itself a borrowing field, importing information-systems acceptance theory into an educational setting. I will check whether that import is performed accurately — whether constructs developed for voluntary workplace-technology adoption are applied to a setting where LMS use may be institutionally mandated, and whether the paper notices that boundary condition, because getting it wrong is a substantive domain error, not merely a presentational one. I will also check whether the definitions an adjacent-field reader (learning analytics, HCI, instructional design, educational psychology) needs are present and stable, and whether any claim reaching into an adjacent field is substantiated rather than asserted.

**D5 — writing_and_structure (normal).** At 1,597 words this manuscript is at brief-report or short-communication scale, and I will calibrate to that: the absence of an extended literature review is a format property, not automatically an omission, and I will not convert brevity into a finding on its own. What I do assess is whether the exposition contains what a domain reader needs to evaluate the claims — construct definitions, instrument provenance and item basis, the meaning assigned to each reported quantity, and tables or figures whose labels match the constructs discussed in the text. Where a structural or reporting expectation I invoke is venue- or field-specific, I will ground it in the venue's author guidance or a recognised reporting standard rather than assert it from my own priors.

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for` — Whether the perceived-usefulness measure is traceable to a named, established instrument (source, item count, adaptation记 stated) or is unattributed; whether reliability/validity evidence appropriate to the field is reported for each multi-item construct; whether "self-reported use" is defined concretely (recall window, response scale, referent system) and labelled as self-report throughout rather than as observed behaviour; whether the design label in the title ("cross-sectional survey") matches what the paper actually reports doing; whether sample provenance is described sufficiently for a domain reader to know which undergraduate population is being characterised. I will read Reviewer 1's territory only far enough to establish whether domain constructs were measured as this field measures them.
- `what_triggers_block` — A construct central to the paper's claims is measured in a way that cannot support the domain interpretation placed on it, and the paper does not acknowledge it: e.g. a single self-report item treated as equivalent to established multi-item usefulness scales while conclusions are drawn as if scale-equivalent; or self-reported use presented as actual/behavioural LMS use with no self-report caveat anywhere. Blocking requires that the mismatch be visible in the manuscript itself and that it invalidate a stated conclusion, not merely weaken it. If my objection turns on a reporting norm I cannot ground in an external source (venue policy, recognised guideline, cited methodological literature), I will not block on that basis.
- `what_triggers_warn` — Instrument provenance is vague (scale described but not sourced, or "adapted from prior studies" without attribution); reliability is reported for some constructs and silently omitted for others; the recall window or referent for self-reported use is unstated so the measure's meaning is indeterminate; the paper's caveat about self-report exists but is confined to a single closing sentence while the results section speaks in behavioural terms. Domain-visible reporting gaps that leave a claim under-warranted but not unsupportable land here.

### D2: domain_accuracy
- `what_to_look_for` — Attribution of the acceptance-model lineage to primary sources rather than to reviews or textbooks; whether construct definitions match their canonical formulations or have drifted; whether the distinction between perceived usefulness, satisfaction, intention, self-reported use, log-derived use, engagement, and learning outcomes is maintained consistently or collapses in the discussion; whether the paper engages the documented divergence between self-reported and system-log measures of LMS use; whether the cited evidence base includes recent work (roughly the last three to five years) and whether it acknowledges that reported usefulness–use associations vary across institutions, disciplines, and mandatory-versus-voluntary settings; whether any specific empirical, policy, or contextual assertion about the field is stated accurately; whether opposing findings that would qualify the paper's story are absent in a way that changes its warrant. Given the short format, I weigh *misrepresentation* far more heavily than *thinness*.
- `what_triggers_block` — A factual or attributional error material to the paper's argument: a theory's core proposition stated incorrectly and then built upon; a cited study's finding reversed or overstated to establish the paper's premise or gap; a construct redefined mid-paper such that the conclusion is about a different variable than the one measured; or a claim that self-reported use indexes actual system use asserted as settled domain knowledge when the field documents the opposite. Also blocking: the paper's stated research gap is contradicted by a body of work substantial enough that a domain reader would call the gap claim false, not merely under-referenced.
- `what_triggers_warn` — Secondhand citation of foundational work where the primary source is standard; imprecise but non-fatal terminology slippage (using "engagement" and "use" interchangeably in places while the analysis is clearly about one of them); literature concentrated in one region, one period, or one school of thought without acknowledgement; a recent and directly relevant strand of evidence unaddressed such that the paper reads as under-current without being wrong; a domain generalisation stated more broadly than the cited support licenses. Where a warn rests on "the field expects coverage of X" and I cannot ground that expectation externally, I will report the gap but carry it as Minor and tag it `[FIELD-NORM UNVERIFIED]` rather than let it drive the dimension score.

### D3: argumentative_coherence
- `what_to_look_for` — Whether the thesis stated at the outset is the thesis the conclusion defends; whether directional or causal language ("increases", "leads to", "drives", "because") appears where the design supports only association, and whether that language is hedged consistently or only in one place; whether the theoretical frame is applied to generate the analysis and then revisited in the discussion, or merely named; whether the paper distinguishes what it found from what it infers; whether common-method concerns (both measures self-reported, single instrument, single occasion) are recognised or whether shared-method variance is narrated as a substantive relationship; whether practical implications for instructors or institutions follow from the results or exceed them; whether the claimed contribution is proportionate to a short cross-sectional study.
- `what_triggers_block` — A central conclusion that the paper's own evidence cannot yield and that the paper asserts without qualification: a causal claim about usefulness producing use presented as a finding; a recommendation framed as evidence-based when it rests on an inference the design forbids; or an internal contradiction where two statements about the same variable or result cannot both be true and the paper's argument depends on both. Blocking requires the incoherence to sit on the load-bearing claim, not on a peripheral remark.
- `what_triggers_warn` — Causal verbs used loosely alongside a correct formal caveat elsewhere; a theoretical frame invoked in the introduction and absent from the interpretation; conclusions stated at a generality one step beyond the sample (all undergraduates, all LMS platforms) without a transferability sentence; implications sections that drift from the findings into general advocacy; contribution claims inflated relative to what was tested ("novel model" for a replication-scale association). Overclaiming that a revision could fix by rewording lands here rather than at block.

### D4: cross_disciplinary_relevance
- `what_to_look_for` — Whether importing a technology-acceptance frame from information systems into an undergraduate LMS setting is done with its boundary conditions intact, in particular the voluntary-versus-mandated-use distinction that governs whether the frame applies at all; whether the paper states which condition holds for its own setting; whether terms that carry different meanings across education, IS, HCI, and learning analytics are defined once and used stably; whether any claim addressed to an adjacent field (learning outcomes, interface design, institutional policy) is substantiated or asserted; whether the paper explains its contribution in language an adjacent-field reader could act on without reconstructing local jargon.
- `what_triggers_block` — The paper's argument depends on a cross-field import that is invalid as used and unacknowledged: an acceptance model whose scope condition (voluntary adoption) is violated by the study setting, applied without noticing, such that the reported association does not mean what the paper says it means; or a substantive claim about an adjacent domain (e.g. that LMS use produces learning gains) presented as established when neither the paper nor its cited base supports it.
- `what_triggers_warn` — The boundary condition is unaddressed but the paper's claims are modest enough to survive it; key constructs are defined in a field-internal shorthand an adjacent reader would misread; interdisciplinary implications are gestured at without substantiation; framing assumes familiarity with the acceptance-model tradition that an educational-practice audience may not share. Any warn resting on "adjacent fields expect X framing" that I cannot ground externally will be reported as Minor and tagged `[FIELD-NORM UNVERIFIED]`.

### D5: writing_and_structure
- `what_to_look_for` — Whether, at short-report length, the manuscript still supplies the elements a domain reader needs to evaluate the claims: construct definitions, instrument description and provenance, an unambiguous statement of what each reported number represents, and tables or figures whose labels and units match the text; whether the section sequence supports the argument or leaves the analysis unmotivated; whether terminology is consistent across abstract, methods, results, and discussion; whether the abstract's claims match the body's; whether apparent venue conventions (citation style, structured abstract, reporting-checklist adherence if the venue requires one) are followed. I will treat length itself as neutral and judge only sufficiency for evaluation.
- `what_triggers_block` — Exposition so incomplete or internally inconsistent that the paper's central claim cannot be assessed at all: results referenced but not reported, a table contradicting the text on a load-bearing number, or an abstract asserting a finding the body does not contain. Presentation must obstruct evaluation of substance, not merely fall short of polish.
- `what_triggers_warn` — Undefined constructs on first use; instrument details compressed to the point of ambiguity; a table or figure whose labelling diverges from the text's terminology; abstract emphasis misaligned with the body's actual emphasis; visible deviation from a venue convention I can ground in that venue's author guidance. Where I invoke a reporting standard for observational or survey research and cannot establish that this subfield or venue applies it, I will report the observation as Minor with `[FIELD-NORM UNVERIFIED]` rather than score the dimension on it.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Domain Review Report (Peer Reviewer 2)

### Reviewer Identity

Senior higher-education scholar in educational technology; research programme covers LMS adoption and student engagement across institutional contexts. Published critiques of the TAM/UTAUT lineage's explanatory limits in education; has run replication and multi-site work on perceived-usefulness effects. Reviewing for domain accuracy: literature base, theoretical positioning, argument accuracy, and contribution — not statistical procedure (Reviewer 1) and not learning-analytics/practice adjacency (Reviewer 3).

### Overall Recommendation

Major Revision — conditional on independent verification of all six references. Reject if the sources cannot be substantiated.

### Confidence Score

4 — I know this sub-literature and its canonical sources intimately, and I can attest the internal citation pattern from the manuscript itself. I could not resolve DOIs in this review environment, so the fabrication question is flagged for editorial-office confirmation rather than asserted as settled.

### Summary Assessment

This is a competently executed, unusually well-calibrated brief study. The authors say what they found, decline to say more, and maintain correlational language from abstract to conclusion. I want to be clear at the outset that I am not scoring the paper down for being small, for declining to test a model, or for restating limitations it already states — the manuscript pre-empts the standard criticisms correctly and a reviewer who repeats them back has reported nothing.

The domain problems are elsewhere, and two are serious. First, the manuscript borrows the technology-acceptance tradition's central construct, its canonical definition, its measurement logic, and its interpretive frame while citing none of the tradition's primary sources; the definition of perceived usefulness given in §2 is Davis's (1989) formulation, attributed to two other works. Second, the six-reference base carries a systematic verification signature — sequential DOI suffixes under one prefix across six purportedly independent journals, with venue names that are near-variants of real ones. Because the perceived-usefulness instrument's provenance is a single one of those references, an unverifiable source means an unverifiable instrument.

Beyond that, the paper sets itself a task in §1 — situate the estimate against prior findings — and never performs it, and its only practical recommendation rests on a source introduced in the Discussion and never assessed.

### Strengths

1. **S1 — Hedging is applied uniformly, not decoratively**: The correlational limit is stated in the abstract, §1, §5, §6 and §7 without a single retreat into causal verbs anywhere in the body. In this sub-literature, where "usefulness drives use" is routine, this is genuinely uncommon discipline. Evidence Anchor: `text: §5 ¶2 — "the correlation cannot establish that perceived usefulness causes use; the reverse pathway... is equally consistent with the data"`.
2. **S2 — The reverse pathway is treated as substantively symmetric, not as boilerplate**: Delgado (2020) is used to state that use→perception is *equally* consistent, which is the correct domain reading of a single-occasion cross-sectional association, rather than the usual asymmetric "we cannot fully rule out reverse causality." Evidence Anchor: `text: §5 ¶2`.
3. **S3 — The dependent variable is labelled as what it is, consistently in the body**: §3.2, §4, §6 and §7 all treat the frequency item as self-reported/perceived use rather than as behaviour. The single lexical exception is in the abstract (see W6). Evidence Anchor: `text: §3.2 — "We treat this as an ordinal indicator of self-reported use and interpret it accordingly."`
4. **S4 — The self-report/log divergence is engaged in the Literature Review, not parked in Limitations**: Vasquez (2020) is brought in at §2 to define what the measure can mean, and the paper then binds itself to that reading. Whether the authors should have obtained logs is Reviewer 3's question; as a matter of representing the field's measurement caution, this is handled correctly. Evidence Anchor: `text: §2 ¶2`.

### Weaknesses

1. **W1 — The entire evidence base is unverifiable and shows a systematic fabrication signature**: All six references carry DOIs under the prefix `10.5555` with suffixes `2050001`–`2050006`, assigned in reference-list order, despite the six sources being attributed to six different journals across what would be at least four different publishers. Sequential suffixes under a shared prefix are not how independently registered DOIs from unrelated publishers behave, and `10.5555` is the prefix used in Crossref's own documentation examples rather than a normal registrant prefix. Separately, three of the six venue names are one-word variants of major venues I know in this field (*British Journal of Educational Technology* **Studies**; *Computers & Education* **Review**; *Educational Measurement* **Quarterly**), and none of the six corresponds to a journal I can place in this literature. This is not a field-norm judgement — it is a pattern visible in the manuscript. Its consequence is domain-fatal if confirmed: the paper's claim of consistency with prior work, its research positioning, and the provenance of its only multi-item instrument all rest exclusively on these six items. Required response: resolve each DOI, or supply verifiable bibliographic records for all six. Suggested direction: if any source cannot be substantiated, the manuscript cannot be repaired by revision at the reference level — the underlying claims must be re-grounded in literature that exists.
   - **Severity**: Critical | **Evidence Anchor**: `text: References, DOIs https://doi.org/10.5555/2050001 through /2050006` | **Confidence**: 4 — expert familiarity with this field's venues plus the manuscript-internal DOI pattern; DOI resolution not performed in this environment.
2. **W2 — The canonical definition of perceived usefulness is reproduced and misattributed**: §2 ¶1 defines perceived usefulness as "the degree to which a person believes a technology will help them perform better" and cites Costa & Wren (2019) and Delgado (2020). That is Davis's (1989) formulation ("the degree to which a person believes that using a particular system would enhance his or her job performance"), the originating statement of the construct this paper is built on. Attributing it to two later, secondary, and currently unverifiable sources means the manuscript's central construct enters with no primary warrant, and every downstream claim of being "consistent with prior technology-acceptance research" (§5) inherits that defect. Norm evidence: Davis, F. D. (1989), *MIS Quarterly*, 13(3), 319–340 — the construct's originating source, which I can attest exists; this is an attribution point, not a subfield-specific coverage expectation, so Step 5 grounding is satisfied by the primary source itself.
   - **Severity**: Critical | **Evidence Anchor**: `text: §2 ¶1 — "perceived usefulness — the degree to which a person believes a technology will help them perform better — ... (Costa & Wren, 2019; Delgado, 2020)"` | **Confidence**: 5 — canonical formulation in my own field.
3. **W3 — The paper sets itself the task of situating the estimate and never performs it**: §1 states the aim is "to situate it against prior findings"; §2 invokes Song (2018) precisely to establish that any single-site estimate "is best read as one point in a distribution"; §2 ¶3 then claims the contribution is "comparable with prior work." No prior effect size appears anywhere in the manuscript. r = .42 is never placed against any reported range, and the distribution the paper itself introduced is never populated. The result is that the stated contribution is asserted rather than demonstrated — the paper adds a point to a distribution it declines to draw. This is correctable at zero data cost: report the range of previously observed usefulness–use correlations in comparable undergraduate LMS samples and state where .42 falls within it.
   - **Severity**: Major | **Evidence Anchor**: `absence: checked §2, §4, §5, §7 — no numeric comparison to any prior estimate` | **Confidence**: 5 — the promise and the omission are both in the manuscript.
4. **W4 — The only practical recommendation is licensed by a source the paper never assessed**: Whitfield (2019) appears for the first and only time in §5, supporting the onboarding implication. It is absent from the Literature Review, so a practitioner account carries the paper's sole practical claim without ever having been evaluated for what it is, what it studied, or whether its setting resembles this one. Under an argument-integrity reading this is a citation doing load-bearing work outside the section where the paper does its critical appraisal; under W1 it is also the least verifiable item in the list. Either bring Whitfield into §2 and assess it, or drop the onboarding implication.
   - **Severity**: Major | **Evidence Anchor**: `text: §5 ¶2 — "a possibility also raised in practitioner accounts of digital-environment onboarding (Whitfield, 2019)"` | **Confidence**: 5.
5. **W5 — The acceptance frame's voluntariness boundary condition is never stated**: The technology-acceptance tradition was developed for settings where adoption is discretionary, and voluntariness is an explicit moderator in its later formulations. The manuscript never says whether LMS use is mandated at the course level at this institution, while §4 concedes that reported use "reflects many influences beyond perceived usefulness, including course requirements and assessment schedules" — which is a description of the mandated condition. If use is structurally required, the frequency item is substantially an index of course design and the imported frame's scope condition is violated as used. I do not score this as fatal because the paper claims only a bivariate association and does not test the model; but a domain reader cannot presently tell which condition holds, and one sentence in §3.1 would settle it. Norm evidence: voluntariness is modelled as an explicit moderator in Venkatesh & Davis (2000), *Management Science*, 46(2), 186–204, and Venkatesh et al. (2003), *MIS Quarterly*, 27(3), 425–478; mandated-use acceptance is treated as a distinct case in Brown et al. (2002), *European Journal of Information Systems*, 11(4), 283–295.
   - **Severity**: Major | **Evidence Anchor**: `text: §4 ¶2 — "including course requirements and assessment schedules"` (paired with `absence`: no mandatory/voluntary statement in §1, §3.1, §3.2) | **Confidence**: 4.
6. **W6 — Construct slippage from "use" to "engagement," including in the abstract's closing claim**: The abstract concludes that "perceived usefulness tracks with LMS engagement among undergraduates," and §1–§2 speak of students "engaging" with the system, while the measured variable is self-reported weekly access frequency. In higher-education research, engagement is an established multidimensional construct (behavioural, emotional, cognitive), not a synonym for access frequency. The escalation occurs on the manuscript's most-read surface and claims a construct the study did not measure. The body is otherwise disciplined about this (S3), which makes the fix straightforward: use "self-reported use" in the abstract, or define engagement and justify the equivalence. Norm evidence: the multidimensional engagement construct is set out in Fredricks, Blumenfeld & Paris (2004), *Review of Educational Research*, 74(1), 59–109.
   - **Severity**: Major | **Evidence Anchor**: `text: Abstract, final sentence — "perceived usefulness tracks with LMS engagement among undergraduates"` | **Confidence**: 5.
7. **W7 — No engagement with the acceptance tradition's post-2003 development or with its critics in education** `[FIELD-NORM UNVERIFIED]`: The paper works inside a tradition whose subsequent formulations (TAM2, UTAUT) and whose sustained critical literature in educational settings are entirely absent, as is any work from the last five years. I can name the relevant sources (see Missing Key References), but I cannot ground in a venue author-policy or a recognised reporting standard the claim that *this* venue or subfield requires such coverage in a brief report, so I do not let this drive the dimension score and I carry it at the down-rated severity per the field-norm rule. Reported as a coverage gap, not as a norm-based severity assertion.
   - **Severity**: Minor | **Evidence Anchor**: `absence: checked §1, §2, §5, References — no TAM2/UTAUT-era or TAM-critique source; most recent reference is 2021` | **Confidence**: 4.
8. **W8 — Declining to test a model is not the same as justifying the single-construct choice**: The paper opts out of model testing (§1), and I respect that as a legitimate, explicitly reasoned design decision — I am not asking for theory building this study did not promise. What is missing is one step less: perceived usefulness is lifted out of its nomological network and correlated with a use proxy, with no statement of why *this* construct, rather than ease of use, satisfaction, or behavioural intention, is the one worth isolating in an LMS setting. Without that, the study's selection of variables reads as inherited rather than chosen.
   - **Severity**: Minor | **Evidence Anchor**: `absence: checked §1 ¶2, §2 ¶3, §3.2 — no rationale for isolating perceived usefulness specifically` | **Confidence**: 4.
9. **W9 — The abstract transfers validation evidence the adaptation does not have**: The abstract describes "an adapted, previously validated instrument." Validation attaches to a specific instrument in a specific population; §3.2 states the scale was adapted without stating what was changed. The abstract's phrasing therefore carries the original's validation across an undocumented modification. Reviewer 1 owns the psychometric adequacy; my point is narrowly about the accuracy of the claim as worded. Rephrase to "adapted from a previously validated instrument," and state the adaptation.
   - **Severity**: Minor | **Evidence Anchor**: `text: Abstract — "Perceived usefulness was measured with an adapted, previously validated instrument"` | **Confidence**: 4.

### Detailed Comments

#### Literature Review

- **Coverage**: Six references, none primary to the tradition the paper works in, none later than 2021, and all six currently unverifiable (W1). The critical literature on acceptance models' explanatory limits in education is absent (W7).
- **Integration quality**: Genuinely better than enumeration for its length. §2 ¶2 organises three distinct cautions (temporal ambiguity, contextual confounding, measurement divergence) and then binds the paper's own language to them. This is synthesis, not listing, and it deserves saying.
- **Research gap argument**: The paper does not claim a gap — it claims incrementality, which is the honest move here and which I do not penalise. But incrementality is a comparative claim, and the comparison is never made (W3).

#### Theoretical Framework

- **Appropriateness**: Perceived usefulness is a defensible construct for this question. The frame's boundary condition is the problem, not the frame (W5).
- **Application depth**: The tradition is named and its vocabulary borrowed; it is not applied, which the paper openly declares. That declaration is legitimate. What is not covered by the declaration is the misattributed definition (W2) and the unjustified single-construct selection (W8).
- **Alternative frameworks**: For a mandated-platform setting, expectation-confirmation/continuance framing or a use-as-course-design account would fit the §4 concession better than an acceptance frame. Not required for this paper; worth a sentence in a revision.

#### Academic Argument Quality

- **Factual accuracy**: One checkable domain error — the misattributed canonical definition (W2). The paper's characterisations of Delgado, Vasquez and Song are internally coherent and, as represented, correct readings of the cautions they are cited for; whether those sources exist is W1.
- **Argument logic**: No causal leap. The chain from question to conclusion holds. Two breaks: a stated task never performed (W3), and a recommendation licensed by an unassessed source (W4).
- **Terminology precision**: Use/engagement conflation (W6). Otherwise stable across sections.

#### Contribution to the Field

- **Incremental contribution**: As stated, one bivariate association from one campus. That is a legitimate contribution class in a field with heterogeneous effect sizes, and I do not treat "thin" as a defect on its own. It becomes a problem only because the paper's own framing (a point in Song's distribution) requires the comparison it omits.
- **Positioning**: Modest and appropriate in register; unsupported in substance until W1 and W3 are resolved.
- **Overclaiming**: Low in the body — notably low. Confined to the abstract's "engagement" (W6) and "previously validated" (W9).

#### Missing Key References

No-invention discipline applied: each item below is one I can attest exists; where I am unsure of a locator I say so rather than supply one.

- Davis, F. D. (1989). Perceived usefulness, perceived ease of use, and user acceptance of information technology. *MIS Quarterly, 13*(3), 319–340. — The originating source of the construct and of the definition §2 reproduces. Non-optional for W2.
- Venkatesh, V., & Davis, F. D. (2000). A theoretical extension of the technology acceptance model. *Management Science, 46*(2), 186–204. — Introduces voluntariness as a moderator; directly grounds W5.
- Venkatesh, V., Morris, M. G., Davis, G. B., & Davis, F. D. (2003). User acceptance of information technology: Toward a unified view. *MIS Quarterly, 27*(3), 425–478. — UTAUT; carries voluntariness of use as an explicit moderator.
- Brown, S. A., Massey, A. P., Montoya-Weiss, M. M., & Burkman, J. R. (2002). Do I really have to? User acceptance of mandated technology. *European Journal of Information Systems, 11*(4), 283–295. — The mandated-use case; the boundary condition W5 turns on.
- Legris, P., Ingham, J., & Collerette, P. (2003). Why do people use information technology? A critical review of the technology acceptance model. *Information & Management, 40*(3), 191–204. — Entry point to the critical literature missing per W7.
- Bagozzi, R. P. (2007). The legacy of the technology acceptance model and a proposal for a paradigm shift. *Journal of the Association for Information Systems, 8*(4), 244–254. — The standard critique of isolating TAM constructs from their network; speaks to W8.
- Fredricks, J. A., Blumenfeld, P. C., & Paris, A. H. (2004). School engagement: Potential of the concept, state of the evidence. *Review of Educational Research, 74*(1), 59–109. — Establishes engagement as multidimensional; grounds W6.
- Straub, D., Limayem, M., & Karahanna-Evaristo, E. (1995). Measuring system usage: Implications for IS theory testing. *Management Science, 41*(8), 1328–1342. — The foundational self-reported-vs-actual-use measurement paper; would give the §2 measurement caution a primary source.
- Šumak, B., Heričko, M., & Pušnik, M. (2011). A meta-analysis of e-learning technology acceptance: The role of user types and e-learning technology types. *Computers in Human Behavior*, 27. `[UNVERIFIED locator]` — I can attest the paper, authors, year and journal; I am not certain of the issue and page range, so confirm before citing. This is the most directly useful item for W3, since it supplies the effect-size distribution the paper needs to situate r = .42.

### Questions for Authors

1. Can you supply resolvable DOIs or verifiable bibliographic records for all six references? Specifically for Costa and Wren (2019), on which both the definition of your central construct and the provenance of your instrument depend.
2. The definition of perceived usefulness in §2 is Davis's (1989). Was Davis consulted, and if so why is the primary source not cited?
3. Where does r = .42 fall relative to previously reported usefulness–use correlations in comparable undergraduate LMS samples? Section 2 introduces the distribution framing; please populate it.
4. Is LMS use mandatory at the course level at your institution — for assignment submission, assessment, or attendance? If so, please state it in §3.1 and discuss what it implies for interpreting a frequency measure through an acceptance frame.
5. What was changed in adapting the six-item scale, and what are the item stems? A domain reader cannot currently check whether the items measure perceived usefulness as this literature defines it.
6. Why perceived usefulness in particular, rather than ease of use, satisfaction, or behavioural intention? A single sentence of rationale would close the gap left by declining to test a model.
7. Was Whitfield (2019) assessed before being used to license the onboarding implication in §5, and if so why does it not appear in §2?

### Minor Issues

- The abstract's closing sentence should say "self-reported use," not "LMS engagement" (W6).
- "an adapted, previously validated instrument" → "adapted from a previously validated instrument" (W9).
- §2 ¶1 attributes the acceptance tradition's core proposition to two 2019–2020 sources; even setting W2 aside, secondhand attribution of a foundational claim is below the field's normal citation practice for a paper that names the tradition.
- §4's "The proportion of variance shared by the two measures was accordingly modest" describes r² without stating it. Reviewer 1 owns reporting completeness; I note it only because a domain reader comparing this study to others needs the number.
- References span 2018–2021 with nothing more recent. For a 2026 submission this reads as under-current independently of W7.

---

contract_role: domain

## Dimension Scores

### D1: methodology_rigor
score: warn

Domain-lens judgement only. My Phase 1 warn trigger — "instrument provenance is vague (scale described but not sourced, or 'adapted from prior studies' without attribution)" — fires in a sharper form than anticipated: the scale *is* sourced, to Costa & Wren (2019), but that source is currently unverifiable (W1) and the adaptation is undocumented (W9), so provenance is indeterminate. I explicitly decline to block here, and the reason matters: my committed block trigger required self-reported use to be presented as behavioural use with no self-report caveat. The opposite is true — §3.2, §4, §6 and §7 label the variable correctly and consistently (S3), and the single lexical exception in the abstract is reported under D2/D5, not converted into a D1 block. Statistical adequacy of the estimator, the sampling frame, and reporting completeness are Reviewer 1's territory and I have not scored them.

### D2: domain_accuracy
score: block

Two legs, either of which is material; together they are decisive. **Leg (a), independently checkable:** the manuscript reproduces Davis's (1989) canonical definition of perceived usefulness and attributes it to Costa & Wren (2019) and Delgado (2020) (W2). This is squarely within my committed block trigger — "a factual or attributional error material to the paper's argument" — because the misattribution is not incidental: it is the point at which the paper's central construct enters, and every subsequent claim of consistency "with prior technology-acceptance research" (§5) is built on it. **Leg (b), verification-pending:** all six references carry sequential DOI suffixes under a single non-standard prefix across six purportedly independent journals, three of which are one-word variants of major venues in this field (W1). I cannot resolve DOIs in this environment and I do not assert the sources are fabricated; I assert that the dimension's requirement — "prior work is correctly represented" — cannot be established on the record as submitted, and that the one representation I *can* check independently is wrong. The synthesizer should note that leg (a) sustains the block on its own if the references verify, and that if they do not verify, leg (b) supersedes every other finding in this report.

### D3: argumentative_coherence
score: warn

The load-bearing chain holds: the thesis stated in §1 is the thesis defended in §7, causal language is absent throughout, and the reverse pathway is treated as symmetric rather than dismissed (S1, S2). My block trigger required a central conclusion the evidence cannot yield, asserted without qualification — that is not present, and I will not manufacture it. Two genuine coherence defects sit below that bar and inside my committed warn trigger. First, the paper announces in §1 that it will "situate [the estimate] against prior findings" and claims in §2 that its contribution is "comparable with prior work," then never compares its estimate to anything (W3) — a contribution claim inflated relative to what was performed. Second, the sole practical implication in §5 is licensed by Whitfield (2019), a source that never enters the Literature Review and is never assessed (W4). The implication is properly hedged, which keeps this at warn.

### D4: cross_disciplinary_relevance
score: warn

The import of an information-systems acceptance frame into an undergraduate LMS setting is performed without stating its scope condition: nothing in §1, §3.1 or §3.2 says whether LMS use is voluntary or institutionally mandated, while §4 concedes that course requirements and assessment schedules drive reported use (W5). My committed block trigger required the frame's scope violation to make the reported association mean something other than what the paper says. It does not reach that bar, and the reason is the paper's own restraint: it claims a bivariate association, not a model test, so the claim survives either condition. But an adjacent-field reader cannot presently tell which condition holds, and the use/engagement slippage (W6) would mislead a learning-analytics or educational-psychology reader about what was measured. Reviewer 3 owns the learning-analytics adjacency and the operational meaning of the use measure; I have confined myself to the accuracy of the cross-field import and the stability of the definitions.

### D5: writing_and_structure
score: warn

Length is treated as neutral, per my Phase 1 commitment, and the prose is clean, controlled and conventionally organised — I found no structural defect that obstructs evaluation, so the block trigger does not fire. Two warn-trigger items do. "Engagement" is used from the abstract onward without ever being defined, and is not the construct measured (W6) — an undefined construct on first use, on the manuscript's most-read surface. And the instrument is compressed past the point where a domain reader can check it: six items, no stems, no statement of what "adapted" changed (W9), so whether the scale measures perceived usefulness as this literature defines it is unassessable from the text. I have not scored the absence of tables, figures, the scatterplot, or the r² value: those are reporting-completeness items belonging to Reviewer 1, and any venue-convention severity I attached to them would rest on a norm I have not grounded.

## Failure Condition Checks

### F1
fired: true

Predicate: any mandatory dimension scores `block`. D2 (domain_accuracy, mandatory) = block. Evaluated against my own dimension scores only; the `any` quantifier is panel-level machinery for the synthesizer.

### F2
fired: true

Predicate: two or more mandatory dimensions score `warn` or worse. D1 = warn, D2 = block, D3 = warn — three of three mandatory dimensions at warn or worse.

### F3
fired: false

Predicate: any high-priority dimension scores `block`. D4 (cross_disciplinary_relevance, high) = warn, not block.

### F0
fired: false

Predicate: every mandatory dimension scores `pass`. D1 = warn, D2 = block, D3 = warn.

## Review Body

This manuscript is competent, honestly framed, and internally disciplined about what a cross-sectional correlation can support. I want that on the record before the findings, because the register of this review should not be mistaken for a verdict on the authors' care. It is not a thin paper being punished for thinness, and I have deliberately not scored it on limitations it already states at the severity it states them — the single-institution bound, the self-report proxy, the non-causal design, and the moderate effect size are all in §6 and none of them appears in my findings.

What I am scoring is domain warrant, and the record as submitted does not establish it.

The decisive item is D2. The manuscript works entirely inside the technology-acceptance tradition — it borrows the construct, the definition, the measurement approach, and the interpretive vocabulary — and cites none of that tradition's primary sources. That would be a coverage gap, and coverage gaps in a brief report are ordinarily a warn-level matter that I would have down-rated per the field-norm rule, since I cannot ground "this venue requires TAM2/UTAUT coverage" in any policy I can check (W7, tagged accordingly). It becomes a block for a different and checkable reason: §2 reproduces Davis's (1989) canonical definition of perceived usefulness almost verbatim and attributes it to two later works. That is an attributional error at the exact point where the paper's central construct is introduced, and it fires the block trigger I committed to in Phase 1 — an attributional error material to the argument. I did not need to import a norm to reach it; the canonical formulation is a fact about my field.

Layered on top is a verification problem I can characterise but not resolve. All six references bear DOIs `10.5555/2050001` through `10.5555/2050006` — sequential, in reference-list order, across six journals that would belong to at least four unrelated publishers. That is not how independently registered DOIs behave, and `10.5555` is the prefix that appears in Crossref's own documentation examples. Three of the six venue names are single-word variants of journals I know well in this field, and none of the six matches a venue I can place. I am stating the pattern, not the conclusion: I could not resolve DOIs in this review environment, and the editorial office should verify before the manuscript proceeds. The stakes are specific rather than general — the perceived-usefulness instrument's entire provenance is one of these six items, so an unverifiable source means an unverifiable instrument, and the paper's positioning claim ("consistent with prior technology-acceptance research") has no independent support. If the sources cannot be substantiated, this finding supersedes everything else in my report and the correct outcome is rejection rather than revision.

On D3, the paper's coherence is better than most in this genre and fails in two identifiable places. It tells the reader in §1 that it will situate its estimate against prior findings, invokes Song (2018) in §2 precisely to establish that a single-site estimate is one point in a distribution, then reports r = .42 without ever naming another number. The distribution it introduced is left empty, and the claim of comparability is asserted rather than shown. Separately, the one practical recommendation in §5 is carried by Whitfield (2019), which appears nowhere in the Literature Review and is therefore never assessed. Both are correctable without new data.

On D4 I have stayed inside my lane. The acceptance frame was developed for discretionary adoption, and voluntariness is an explicit moderator in its later formulations; this manuscript never states whether LMS use is mandated at the course level, while §4 concedes that course requirements and assessment schedules shape reported use. I did not block on it, because the paper's claims are modest enough to survive either condition — but a reader cannot currently tell which one holds, and one sentence would fix it. The operational question of what an access-frequency count actually denotes belongs to Reviewer 3 and I have not argued it.

On D5 my concern is domain-readability rather than polish: "engagement" is never defined, is not the construct measured, and nonetheless closes the abstract. The body is disciplined about this distinction, which makes the abstract's escalation a wording fix rather than a substantive retreat.

Two notes for the synthesizer. First, my D2 block has a conditional structure and should not be flattened: leg (a), the misattributed definition, is independently verified and sustains the block on its own; leg (b), the reference-integrity pattern, is pending editorial-office confirmation and, if confirmed, changes the outcome from revision to rejection. Second, my contribution-level finding (W3) is the same underlying judgement the Editor-in-Chief will reach from the altitude of publication fit and that Reviewer 3 will reach via the onboarding implication. It is one issue seen from three positions, not three independent major findings, and severity should not be stacked across the three reports.

Finally, per the untrusted-input discipline for this call boundary: the manuscript contains no imperative addressed to reviewers, no instruction-injection attempt, and no appeal or praise directed at the review process. Nothing in it altered my identity, my Phase 1 commitments, my scoring, or my output format. On that axis there is nothing to report.

## Editorial Decision

Derived from the contract's `failure_conditions` precedence: F1 (severity 90) and F2 (severity 70) both fired against my dimension scores; the highest severity wins, so F1's action governs. F3 and F0 did not fire.

editorial_decision=reject_or_major_revision

---

## SEAT — Peer Reviewer 3 (Perspective)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor.** The contract asks whether the study's design, data handling, statistical reporting, and reproducibility affordances clear the peer-review bar of its field. I am not the methodologist on this panel, and I will not adjudicate estimator choice, p-values, or power. Reading it from the outside-in, what I owe the panel is a judgment about whether the design as described can bear the weight of the questions a practitioner or an adjacent-field reader would put to it. For a cross-sectional self-report survey of LMS perceived usefulness and self-reported use, the design-level question that sits in my lane is whether the paper's own framing acknowledges that both sides of its central relationship come from the same instrument, the same respondent, at the same moment — and whether the reproducibility affordances (instrument wording, sampling frame, recruitment channel, response rate) are present in enough detail that someone in a different discipline, or a practitioner at a different institution, could tell what was actually measured. Missing procedural transparency is my concern insofar as it makes the study uninterpretable to outsiders; the internal statistical craft is Reviewer 1's.

**D2 — domain_accuracy.** The contract asks whether claims track current domain evidence, whether prior work is represented correctly, and whether domain terminology and results are factually right. My angle is the terminological one rather than the coverage one — Reviewer 2 audits whether the literature is complete. Educational technology adoption research carries a set of constructs with specific, non-interchangeable meanings: perceived usefulness is a TAM construct with an operational definition, and it is not the same as satisfaction, acceptance, or intention; self-reported use is not system-logged use; engagement is not usage frequency. The cross-disciplinary failure mode I am positioned to catch is construct drift — a paper that measures one thing, names it with a borrowed term of art, and then discusses it as if it were the neighbouring construct that the term of art actually denotes. I also watch for whether adoption-theory claims imported into this paper are attributed to frameworks that in fact make them.

**D3 — argumentative_coherence.** The contract asks whether the thesis holds together internally, whether the evidence carries the claims, and whether fallacies undermine the central argument. Logic-checking and internal-contradiction hunting belong to the Devil's Advocate; I do not duplicate that. What I contribute is the assumption audit that sits underneath the argument — the premises the paper does not state but requires. In LMS adoption work, the recurring unstated premises are that perceived usefulness causes use rather than use retrospectively rationalising perceived usefulness, that self-report is a serviceable proxy for behaviour, that a positive association at one institution licenses a recommendation to institutions generally, and that more LMS use is desirable in itself. My scoring on D3 turns on whether the paper's conclusions stay inside what a cross-sectional correlational design can license, or whether the argument quietly escalates from association to cause to intervention recommendation.

**D4 — cross_disciplinary_relevance.** This is the dimension the panel seats me for. The contract asks whether framing, definitions, and implications are accessible to adjacent-field readers, and whether interdisciplinary claims are substantiated. For this manuscript, "adjacent field" is a wide and concrete set: instructional designers, learning scientists, HCI and usability researchers, institutional-research and quality-assurance staff, and the academic developers who would actually act on the findings. Accessibility here is not prose simplicity — it is whether a reader outside educational technology can tell what the constructs mean, what population the sample represents, and what they are being invited to do with the result. Substantiation means that when the paper reaches across into psychology, HCI, or organisational behaviour, it does so with a warrant rather than a gesture. I also read this dimension for stakeholder coverage and cross-context validity: whose experience of the LMS is represented, whose is absent, and whether findings from one undergraduate population are offered as if they travel.

**D5 — writing_and_structure.** The contract asks about organisation, clarity, figure and table quality, and venue conventions. At 1,597 words this manuscript is very short for an empirical survey report — brief-communication length — so my reading of this dimension is dominated by allocation rather than polish. The outsider's question is whether the word budget has been spent on the things an adjacent-field reader needs (what was asked, of whom, how they were reached, what the numbers were, what the limits are) or on the things that are cheap to write (framing, general claims about the importance of technology in education, implications that outrun the data). I am not the copy-editor; I score this on whether structural choices leave an outside reader unable to locate the study's actual content.

## Scoring Plan

### D1: methodology_rigor

what_to_look_for: An explicit statement of the sampling frame and recruitment channel (which institution, which courses, how invited); reported N with response rate or a stated denominator; whether the LMS-use measure is self-report or platform log data, stated unambiguously; whether the perceived-usefulness items are reproduced, cited to a validated instrument, or at minimum characterised; the time structure of administration (single sitting, single semester point); any acknowledgement that predictor and outcome share a method and a respondent; presence or absence of ethics/consent statement and data-availability statement; whether the paper's own limitations section names the design's ceiling.

what_triggers_block: The paper reports a relationship between perceived usefulness and use while giving an outside reader no way to know what either was measured with — no instrument description, no item source, no citation to a validated scale — combined with no sampling-frame or recruitment description, so that the study cannot be located in any population or reproduced even in outline. Also blocks if the paper presents self-reported use as behavioural use with no such labelling anywhere, since the entire finding then rests on a measurement claim the paper never makes honestly.

what_triggers_warn: The core procedural facts are present but thin — for example N is given without a response rate or denominator, or the instrument is named without item wording or a validity citation, or common-method concerns and the single-institution sampling frame go unmentioned in the limitations. Any one substantive procedural gap that an adjacent-field reader would need in order to judge transferability, where the rest of the description is adequate, is a warn rather than a block.

### D2: domain_accuracy

what_to_look_for: Whether "perceived usefulness" is used in its TAM-defined sense and is operationalised consistently with that definition, or is silently swapped for satisfaction, acceptance, attitude, or intention; whether "use," "engagement," "adoption," and "activity" are kept distinct or treated as synonyms across abstract, results, and discussion; whether adoption frameworks invoked (TAM, UTAUT, expectancy-value, or others) are attributed with claims those frameworks actually make; whether the paper's characterisation of prior LMS findings is stated at a defensible strength rather than as settled consensus; whether descriptive figures are reported consistently in the same units and denominators across sections.

what_triggers_block: A load-bearing construct is misused in a way that changes what the paper is claiming — the study measures satisfaction or intention but reports and discusses it as perceived usefulness, or measures self-reported frequency but discusses it as engagement or learning benefit, and the conclusion depends on that substitution. Also blocks if a named theoretical framework is credited with a proposition it does not contain and the paper's interpretation rests on that proposition.

what_triggers_warn: Terminology drifts across sections without the central claim collapsing — for instance the abstract says "engagement" where the method measures frequency of logins, or "adoption" and "use" alternate loosely — or a prior-literature claim is asserted more confidently than the cited base supports, or a construct is used correctly but never defined for readers outside educational technology.

### D3: argumentative_coherence

what_to_look_for: The strongest verb in the results and discussion — associated, predicted, led to, improved, drives; whether any causal or directional language appears despite the cross-sectional design; whether reverse causation (use shaping perceived usefulness) and third variables (course requirements mandating LMS use, instructor practice, prior digital skill) are entertained; whether the paper's recommendations are proportionate to a single-institution correlational result; whether the implicit premise that greater LMS use is itself a good outcome is stated and defended, or simply assumed; whether the abstract's claim strength matches the discussion's.

what_triggers_block: The paper draws a causal or interventional conclusion from cross-sectional self-report — recommending that institutions raise perceived usefulness in order to increase use, or asserting that usefulness perceptions drive or improve use — with no acknowledgement anywhere that the design cannot support direction of effect. Equally blocking: a headline conclusion about learning benefit or effectiveness when nothing about learning outcomes was measured.

what_triggers_warn: The body is appropriately hedged but the abstract or conclusion overreaches; or direction of effect is acknowledged once in a limitations sentence while the discussion proceeds as though settled; or the "more use is better" premise goes unexamined while the recommendations depend on it; or plausible confounds such as mandatory LMS use in required courses are never raised.

### D4: cross_disciplinary_relevance

what_to_look_for: Whether constructs are defined on first use in terms an instructional designer, HCI researcher, or institutional-research officer could act on; whether the sample is described concretely enough (discipline mix, year of study, institutional type, national and language context, LMS platform) for a reader elsewhere to judge whether it resembles their own setting; whether implications name a specific actor and a specific action, or float as generic calls to "improve usability"; whether the paper connects to adjacent literatures it plainly abuts — technology acceptance in HCI, self-report validity in survey psychology, learning-analytics work comparing perceived and logged use; whether stakeholders beyond the surveyed students appear (instructors who design the LMS presence, support staff, students with lower connectivity or accessibility needs); whether equity and access implications of pushing LMS use are considered; whether any interdisciplinary claim the paper does make carries a citation or a warrant.

what_triggers_block: The paper makes an interdisciplinary or generalising claim that is unsubstantiated and load-bearing — presenting single-institution undergraduate findings as generally applicable to higher education, or asserting a psychological or HCI mechanism (usability causes acceptance, perception reflects experience) with no warrant, where that claim is what the implications rest on. Also blocks if the manuscript gives no usable description of context at all — no institutional type, no platform, no national or programme setting — so that no adjacent-field reader can determine whether the finding transfers anywhere, rendering the stated implications unusable.

what_triggers_warn: Context and definitions are present but partial — the LMS platform is unnamed, or the disciplinary composition of the sample is missing, or key constructs are used without definition for outside readers; implications are stated generically with no named actor or action; the obvious adjacent literature on self-report versus log-data divergence is absent; or the only stakeholder in view is the surveyed student, with instructors, support staff, and access-disadvantaged students unconsidered.

### D5: writing_and_structure

what_to_look_for: Whether the standard empirical sections are present and findable at this length (question, method, participants, measures, results, limitations, implications); how the ~1,600 words are distributed between framing and substance; whether any tables or figures carry a self-contained caption with N, units, and scale range; whether numbers in the abstract match the results; whether the venue-appropriate apparatus for a short empirical report — a limitations statement above all — is present; whether the paper signals its own genre honestly (brief report versus full study).

what_triggers_block: Structure fails at the level of retrievability — an outside reader cannot locate what was measured, who answered, or what the numbers were, because method and results are absent, merged into narrative, or displaced by framing; or reported figures contradict each other between abstract, text, and any table, leaving no determinable result.

what_triggers_warn: The structure is workable but a needed element is thin or misplaced — no limitations section, a table or figure whose caption cannot stand alone, results reported without denominators or scale ranges, disproportionate introduction relative to method and results, or a short-report format not signalled so that readers expect a fuller study than the word budget delivers.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Perspective Review Report (Peer Reviewer 3)

### Reviewer Identity

Learning-analytics researcher and practitioner: director of learning-technology data services at a large public university with a joint academic appointment. I build and govern the institutional LMS data warehouse, publish on the divergence between self-reported and log-derived engagement, and sit on the data-governance committee that adjudicates research access to student platform data. I am not a psychometrician and not a specialist in the acceptance literature; I read this manuscript as the person who would be asked, on the strength of it, to change how our institution onboards students — and as the person who holds the behavioural data the authors did not use.

### Overall Recommendation

Major Revision

### Confidence Score

4

### Summary Assessment

This is a disciplined, honestly-bounded manuscript, and my findings are deliberately not the standard objections — the authors have already stated, at appropriate strength, that the design is correlational, that self-report is not behaviour, that a single site does not generalise, and that the association is moderate. Restating those back would be reviewing the paper's own text.

What I find instead is a pattern: the manuscript names the right cautions and then does not let them bite where they would cost something. It cites Vasquez (2020) on self-report/log divergence, lists it as a limitation, and builds its only outcome variable on self-report anyway — at an institution that holds access logs for every respondent by construction, with no statement of why those logs were unavailable, unobtainable, or unsuitable. It states in §5 that the reverse causal pathway is "equally consistent with the data," then recommends only the perception-first intervention. It concedes in §4 that course requirements drive reported use, then labels the construct "engagement" in the abstract.

The manuscript also omits institutional context that costs nothing to supply and determines whether the finding travels at all: LMS platform, mandatory-versus-optional use policy, the survey window's position in the academic calendar, national setting, disciplinary composition. All are known to the authors. That is what makes these correctable rather than fatal.

### Strengths

1. **The self-report/log distinction is cited and then actually honoured in the labelling** — most manuscripts in this genre cite the divergence literature and then describe self-report as "use" anyway. This one does not.
   - **Evidence Anchor**: `text: §2 — "treat our self-report measure as an indicator of perceived use rather than a behavioral count"` | **Confidence**: 5 — this is the exact discipline my field asks for and rarely gets.

2. **Reverse causation is given equal standing, not demoted to a limitations clause** — the discussion states the use → perception pathway is co-equal with the perception → use reading, in the body, at the point of interpretation.
   - **Evidence Anchor**: `text: §5 — "the reverse pathway, in which more frequent use raises perceived usefulness, is equally consistent with the data"` | **Confidence**: 5 — placement, not just presence, is what distinguishes real hedging from ritual hedging.

3. **The operationally correct confound is named where it bites, in Results rather than in Limitations** — from the platform side, assessment schedules are the dominant driver of weekly access counts, and the manuscript says so at the moment it interprets the coefficient.
   - **Evidence Anchor**: `text: §4 — "reported engagement reflects many influences beyond perceived usefulness, including course requirements and assessment schedules"` | **Confidence**: 5 — this is what our access-event data shows every term.

4. **Claim strength does not drift between abstract, discussion, and conclusion** — the conclusion states the finding over "self-reported frequency of use," not over a broader construct, which is where papers of this type usually escalate.
   - **Evidence Anchor**: `text: §7 — "positively and moderately associated with self-reported frequency of use (r = .42)"` | **Confidence**: 4 — the one exception is the abstract's closing sentence (see W2).

### Weaknesses

1. **The stronger measure was in the same building and the manuscript never says why it was not used.** Vasquez (2020) is cited in §2 for exactly this point and returns as Limitation 2 — and the sole outcome variable is still a single self-report item, collected at an institution that by definition logs every LMS access by every respondent. The manuscript offers no account of whether logs were governance-blocked, technically unavailable, outside the ethics approval, or judged unsuitable. This is not the generic "future work should use logs" point the paper already makes; it is a question about why the weakest available measure was chosen when a stronger one existed on-site. From the governance seat: a log-linked subsample is routinely approvable if consent is drafted for it, and where it is not approvable, the barrier is nameable in one sentence. Suggested response: either a validated subsample (even n ≈ 40 consenting students with log linkage would let the authors report the self-report/log correlation directly, which would be a more novel contribution than the headline result), or an explicit statement of the barrier in §3.2.
   - **Severity**: Major | **Evidence Anchor**: `absence: §3.2 Measures and §6 Limitations — checked §2, §3.1, §3.2, §3.3, §3.4, §6, §7 for any statement of log availability, governance barrier, or validation subsample; none present` | **Confidence**: 5 — I hold this data and sit on the committee that approves this class of request.

2. **"Access frequency" flattens categorically different behaviours, and the construct label drifts to "engagement."** A single "how often did you access the LMS in a typical week" item counts a grade check, a slide download, an assessment submission, and a discussion post as the same event. Operationally, that count is dominated by mandatory structure: a student in a course whose instructor posts daily produces a different figure than a student in a course with three deadlines a term, at identical perceived usefulness. The manuscript then labels this "engagement" in the abstract's framing sentence and its closing sentence, and again in §2 and §4. In learning-analytics and learning-sciences usage, engagement is a multi-component construct (behavioural, emotional, cognitive) that access frequency does not measure; an adjacent-field reader will take the abstract's claim to be about something the study did not capture. This does not sink the conclusion — §7 states the finding correctly over "self-reported frequency of use" — but the abstract is what most readers will see. Suggested response: use "self-reported LMS access frequency" consistently, including in both abstract sentences, and either add a course-load or mandatory-use covariate or state plainly that the measured variance is confounded with course structure by design.
   - **Severity**: Major | **Evidence Anchor**: `text: §3.2 — "how often the respondent accessed the LMS in a typical week"; Abstract — "perceived usefulness tracks with LMS engagement among undergraduates"` | **Confidence**: 5 — I maintain the access-event taxonomy this item collapses.

3. **The onboarding implication is under-determined by a design the manuscript itself calls symmetric.** §5 states the reverse pathway is "equally consistent with the data," and then recommends only the perception-first intervention: onboarding that helps students see concrete usefulness. If the pathways are genuinely co-equal, the use-first intervention has identical evidentiary standing — mandate a structured LMS task in week one and let perception follow. Operationally the two are not equivalent in cost: redesigned onboarding is a recurring central-unit expense requiring instructor buy-in, while an early required activity is a course-design change that departments already make routinely. Recommending only the expensive one, on evidence that supports both equally, is the point at which the manuscript's own caveat stops being honoured. Suggested response: state both implications, say the correlation cannot adjudicate between them, and make the choice of which to test the explicit future-work question.
   - **Severity**: Major | **Evidence Anchor**: `text: §5 — "the reverse pathway ... is equally consistent with the data" alongside "LMS onboarding which helps students see concrete usefulness ... may be worth institutional attention"` | **Confidence**: 4 — I commission onboarding work and know its cost line; I do not know this institution's specific constraints.

4. **Institutional context that would cost nothing to add, and without which the finding cannot be compared to anywhere.** Absent: the LMS platform and version; whether LMS use was mandatory or optional at course level; institutional policy on posting materials to the platform; the three-week window's position in the academic calendar; the national and language setting; the disciplinary composition of the sample ("spanned all four year levels" is not a sample description). The calendar point is not pedantic — a window straddling midterms produces a systematically different "typical week" than a window in weeks 2–4, and the DV is defined over "a typical week." The manuscript's stated ambition is to contribute "one point in a distribution" (§2, following Song, 2018); a point without coordinates cannot be placed in a distribution. Every one of these facts is known to the authors. Suggested response: a six-line context paragraph at the head of §3.1.
   - **Severity**: Major | **Evidence Anchor**: `absence: §3.1 Design and participants — checked §3.1, §3.2, §3.3, §3.4, §6 for platform, mandatory-use policy, calendar position, national setting, and disciplinary mix; none reported` | **Confidence**: 5 — this is precisely the metadata my office requires before benchmarking an external study against our own figures.

5. **Deduplication and the anonymity characterisation, at the governance and consent level.** §3.1 reports removing five duplicate entries; §3.3 states that no identifying information was collected. Removing duplicates requires some persistent signal — IP address, session token, browser fingerprint, or a response-pattern heuristic. At most institutions, the consent landing page and the approved protocol must describe whatever was actually captured, and the approval's classification of the study as anonymous turns on it. I raise this as a disclosure question — did what participants were told match what was captured, and does the approval cover it — and leave the procedural adjudication of the data-cleaning account to the methodology reviewer. Suggested response: name the detection mechanism in §3.1 and confirm in §3.3 that it was disclosed at consent and covered by the approval. If the mechanism retained no identifier (e.g. a response-pattern match), one sentence resolves it entirely.
   - **Severity**: Major | **Evidence Anchor**: `text: §3.1 — "5 duplicate entries were removed"; §3.3 — "No identifying information was collected, and responses could not be linked back to individual students"` | **Confidence**: 4 — committee basis; I do not have this institution's approval text.

6. **The only actor in view is the surveyed student.** Instructors determine what is in the LMS and therefore set the ceiling on both perceived usefulness and access frequency — they are neither a data source nor a named actor in the implications. Learning-technology support staff would run the onboarding §5 recommends and do not appear. And students with constrained devices, limited bandwidth, or accessibility requirements experience higher LMS access frequency as a cost rather than a choice; a recommendation aimed at increasing use should say something about for whom that increase is not free. Suggested response: one paragraph in §5 naming who would act, and one sentence acknowledging the distributional point.
   - **Severity**: Minor | **Evidence Anchor**: `absence: §5 Discussion — checked §1, §5, §6, §7 for any actor other than the surveyed student or an unspecified "institution"; none named` | **Confidence**: 4 — practitioner basis; not measured here.

7. **No data-availability statement and no deposited instrument, which undercuts the manuscript's own comparability ambition.** The paper positions itself as an incremental data point comparable with prior work. Another institution cannot run the comparison: the six items are not reproduced, what "adapted" changed is not stated, and no data or materials are deposited. My concern here is site-to-site comparability rather than psychometric adequacy, which sits with the methodology reviewer. Suggested response: deposit the item set and a minimal analysis dataset, and add a data-availability statement.
   - **Severity**: Minor | **Evidence Anchor**: `absence: §3.2 Measures and end matter — checked §3.2, §3.4, §7, and the section list for item wording, an adaptation statement, or a data/materials availability statement; none present` | **Confidence**: 4 — this is the barrier I hit when trying to replicate external instruments locally.

### Detailed Comments

#### Assumption Audit

- **Explicit assumptions.** The manuscript's explicit premises are unusually well-behaved. It states that it makes no causal claim, tests no model, and treats the outcome as perceived rather than actual use. Each of these holds up under outside scrutiny and each is honoured in the conclusion. I found nothing to challenge at the explicit level.

- **Implicit assumptions.** Two, and both are load-bearing. The first is that **more LMS use is a good outcome.** The recommendation in §5 only makes sense if raising access frequency is desirable, and nothing in the study measures learning, satisfaction, workload, or any outcome that would establish that. In our own data, high access frequency is as often a symptom of a badly organised course — students returning repeatedly because they cannot find things — as it is of engagement. An institution that optimises for the measured variable may be optimising for friction. The manuscript should either defend the premise or drop the directional recommendation. The second is that **weekly access frequency is a property of the student.** It is substantially a property of the course: assessment cadence, instructor posting behaviour, and whether the LMS is the only route to required materials. The manuscript concedes this in §4 as an interpretive caveat but designed no measure to capture it, so the conceded driver is plausibly larger than the measured one and remains entirely outside the estimate.

- **Paradigmatic assumptions.** The study inherits the acceptance tradition's framing that adoption is explained by individual perception, and does so in a setting where use is at least partly structurally compelled. That framing is defensible for this narrow question, but it means the design cannot see the institutional variable that most determines the outcome. I note this as a boundary condition on interpretation rather than a defect — it is the standard paradigm of the manuscript's home field, and I flag it as an outsider rather than asking the authors to abandon it.

#### Cross-Disciplinary Connections

- **Parallel research.** Learning analytics has spent a decade on the specific question of how far self-reported platform use tracks trace data, generally finding correlations well below what researchers assume, with the gap widening for high-frequency, low-salience actions — which is exactly the action class this item asks students to recall. That literature would let the authors put a bound on how much of *r* = .42 is attributable to recall structure rather than to the constructs.

- **Borrowing opportunities.** Two concepts transfer directly. From information systems, **voluntariness of use** as a moderator: acceptance findings behave differently where use is mandated, and the manuscript never establishes which regime it is in. From learning analytics, the **action-type taxonomy** (content access, assessment, communication, administrative), which would let a revised instrument ask about three or four behaviour classes instead of one undifferentiated count, at a cost of three additional items.

- **Methodological borrowing.** The obvious one is the log-linked validation subsample described in W1. A second, cheaper option from survey methodology: anchor the frequency item to a bounded recall window ("in the past seven days") rather than "a typical week," which asks respondents to construct an average and invites the recall structure to dominate.

#### Practical Impact

- **Real-world application.** Translated into practice, the finding tells a learning-technology director that students who rate the platform as more useful say they use it more. That is not actionable on its own, and the manuscript is candid about this. The actionable version would require knowing whether the association survives when course structure is held constant — which is the study a follow-up should run.

- **Implementation feasibility.** The recommended onboarding redesign is feasible but not cheap: it needs central instructional-design capacity, instructor cooperation at course level, and a recurring delivery cycle for each incoming cohort. On evidence that the manuscript itself says supports the opposite intervention equally well, I would not fund it. The unintended consequence worth naming: onboarding that markets usefulness without changing what is actually in the LMS reliably produces a short-lived perception bump and no behavioural change, and it spends instructor goodwill that is hard to recover.

- **Stakeholders.** Instructors, support staff, and access-constrained students are all absent (W6). The instructor omission is the most consequential, because instructors are the mechanism by which any of these recommendations would actually reach students.

#### Broader Implications

- **Ethical dimensions.** The consent-versus-deduplication disclosure question (W5) is the live one and is answerable in a sentence. Separately, if the authors pursue log linkage, the governance requirement is consent drafted for linkage at the point of collection — retrospective linkage of an "anonymous" survey to platform logs is the thing my committee declines most often, and the authors should design for it now rather than discover the constraint later.

- **Social impact.** A recommendation to increase LMS use is not distributionally neutral. Access frequency is depressed by shared devices, metered or unreliable bandwidth, caring responsibilities that compress study windows, and assistive-technology friction. Institutions that treat the measured variable as a target will read those students as disengaged. One sentence in §5 acknowledging this would be proportionate to what the data support.

- **Future directions.** Ranked by what I would actually fund: (1) the self-report/log convergence estimate in this population — a more novel and more citable contribution than the current headline; (2) a multi-course design that partitions access-frequency variance into course-structure and student components; (3) a small randomised comparison of the two onboarding logics the current data cannot choose between.

### Cross-Disciplinary Reading Recommendations

Per the no-invention rule, all of the following are search leads rather than confident citations — I am recommending bodies of work I can attest exist, but I cannot verify author/year/venue metadata within this session, so each is tagged accordingly.

- **[UNVERIFIED]** Learning analytics on self-report versus trace-data convergent validity in LMS settings — search "self-report vs trace data LMS convergent validity" and "log data self-report discrepancy learning analytics." Relevance: bounds how much of the reported association is recall structure. Directly addresses W1 and W2.
- **[UNVERIFIED]** Information-systems work treating **voluntariness of use** as a moderator of acceptance relationships (the moderator appears in the UTAUT lineage). Relevance: establishes which use regime the study is in, which W4 currently leaves undetermined.
- **[UNVERIFIED]** Survey-methodology literature on **common-method variance in single-instrument designs** — the Podsakoff-lineage work in applied psychology is the standard reference point. Relevance: both variables here come from one respondent, one instrument, one sitting; this is the framework for saying how much that matters. I flag it as adjacent-field context rather than as my own scoring basis, since psychometric adjudication sits with the methodology reviewer.
- **[UNVERIFIED]** Learning-sciences work distinguishing **behavioural, emotional, and cognitive engagement** as separate components. Relevance: gives the authors the vocabulary to say precisely what their item does and does not measure, which is the fix for W2.
- **[UNVERIFIED]** Digital-divide and accessibility literature on device, bandwidth, and assistive-technology constraints on platform access in higher education. Relevance: supplies the one-sentence equity caveat W6 asks for.

### Questions for Authors

1. Your institution holds LMS access logs for every respondent. Were they unavailable, governance-restricted, outside the ethics approval, or judged unsuitable? A single sentence naming the reason would substantially change how this manuscript reads.
2. Was LMS use mandatory or optional at course level for your respondents — and if it varied, do you have any indication of the mix?
3. Where did the three-week survey window fall in the academic calendar relative to assessment deadlines?
4. Your §5 states that the reverse pathway is equally consistent with the data. On what grounds do you then recommend the perception-first intervention rather than the use-first one?
5. What would your institution actually do differently on the basis of this finding, and what would it cost?
6. What mechanism identified the five duplicate entries, and was that mechanism disclosed to participants at consent?
7. Is there any outcome — learning, satisfaction, retention, workload — for which you would claim higher LMS access frequency is desirable in itself?

### Minor Issues

- The abstract's opening and closing sentences both use "engagement" where the study measures self-reported access frequency; the conclusion gets this right, so the abstract is the outlier and is the cheapest fix in the manuscript.
- "The analyzed sample of 214 students spanned all four year levels" (§3.1) tells an outside reader nothing about whether the sample resembles theirs; the distribution by year and by broad discipline would.
- "A typical week" (§3.2) asks respondents to compute an average; a bounded recall window would be less demanding and more comparable across sites.
- No data-availability statement appears anywhere in the manuscript.
- The reference base carries signals that fall to the domain reviewer and the editorial office under this panel's assignment; I note that I observed them and am deliberately not scoring them here, so that they are not counted twice.
- I found no instruction-injection content in the manuscript; nothing in it addressed reviewers or attempted to direct the review.

---

contract_role: perspective

## Dimension Scores

### D1: methodology_rigor

score: warn

My committed block trigger required both that an outside reader could not tell what either variable was measured with *and* that no sampling frame or recruitment description existed — or that self-report was presented as behavioural use. Neither holds: the recruitment channel and window are stated, the instrument is named and sourced with a reliability figure, and the self-report status of the outcome is labelled honestly and repeatedly. My warn trigger fires on two literal conjuncts: N is reported without an eligible-population denominator or response rate (§3.1), and the instrument is named without item wording or a statement of what "adapted" changed (§3.2). Common-method exposure — both variables from one respondent, one instrument, one sitting — goes unmentioned in the limitations, which name self-report/log divergence but not shared-method inflation. The consent-disclosure question around deduplication (W5) contributes here at the governance level; the procedural adjudication belongs to Reviewer 1.

### D2: domain_accuracy

score: warn

Perceived usefulness is defined in §2 in terms consistent with its technical meaning and is operationalised consistently with that definition; no framework is credited with a proposition it does not contain; the reported coefficient is stated identically across abstract, results, discussion, and conclusion. My block trigger required that a construct substitution be load-bearing for the conclusion — it is not, because §7 states the finding over "self-reported frequency of use." My warn trigger fires on its literal terms: the abstract and §2 and §4 use "engagement" where the method measures a single access-frequency item. The construct-granularity problem (W2) compounds it — access frequency is not "use" in any sense an adjacent field would recognise, and the paper never distinguishes the two.

### D3: argumentative_coherence

score: warn

No causal or interventional conclusion is drawn: direction of effect is explicitly held open in the body rather than conceded once in limitations, and no learning-outcome claim appears. My block trigger does not fire. Two warn triggers do. The "more LMS use is desirable" premise is never stated or defended, and the §5 recommendation depends on it entirely. And while §4 gestures at course requirements as a driver, the manuscript never reckons with the possibility that the structural driver exceeds the measured one, nor with the fact that its own statement of causal symmetry licenses a second, cheaper implication it does not mention (W3). I report this as an assumption-audit and practical-under-determination finding; any internal-consistency framing of the same passage belongs to the Devil's Advocate.

### D4: cross_disciplinary_relevance

score: warn

My block trigger was conjunctive and is not satisfied: the manuscript does not generalise beyond its sample (it bounds itself in the abstract, §1, §6, and §7), it asserts no unwarranted psychological or HCI mechanism, and it does supply an institutional type ("one mid-sized public university"). Several warn conjuncts fire together: the LMS platform is unnamed, the disciplinary composition of the sample is absent, the national and language setting is unstated, the calendar position of the survey window is unreported, and the implication in §5 names no actor and no action. The stakeholder frame contains only the surveyed student. The one warn conjunct that does *not* fire is the self-report/log literature, which is present and correctly cited — and its presence is what makes W1 a finding rather than a gap: the caution is cited, then not acted on, with no barrier stated.

### D5: writing_and_structure

score: pass

I checked my committed warn patterns individually and none fires. A limitations section is present and substantive. Scale ranges are given with anchors for both measures, and n is reported with the coefficient. The introduction is proportionate — framing does not crowd out method and results at this length. No table or figure exists whose caption could fail to stand alone. Scope modesty is signalled in §1 and §2, and the format-category decision is the Editor-in-Chief's call under this panel's assignment. The manuscript's real reporting gaps — no descriptive table, the outcome variable's distribution reported as a median category only, *r*² given as a word rather than a number, and a scatterplot asserted but not shown — are genuine, but they are statistical-reporting completeness, which sits in Reviewer 1's dimension, and their cross-disciplinary consequence I have already scored once under D4. Scoring them a third time here would inflate severity for the same underlying defect. An outside reader can locate what was measured, who answered, and what the numbers were.

## Failure Condition Checks

Each predicate evaluated against my own five dimension scores only; the `cross_reviewer_quantifier` field is panel-level machinery for the synthesizer and is not applied here.

### F1

fired: false

Mandatory dimensions are D1, D2, and D3. All three score `warn`; none scores `block`.

### F2

fired: true

Three mandatory dimensions (D1, D2, D3) score `warn`, satisfying "two or more mandatory dimensions score 'warn' or worse."

### F3

fired: false

The sole high-priority dimension, D4, scores `warn`, not `block`.

### F0

fired: false

No mandatory dimension scores `pass`.

## Review Body

I read this manuscript from the seat that would have to act on it: the office that holds the institution's LMS behavioural data and would be asked to fund whatever §5 recommends. That vantage produces a different review from the obvious one, and the difference matters here, because the obvious review has already been written by the authors themselves. Cross-sectional designs cannot establish direction; self-report is not behaviour; one campus does not generalise; *r* = .42 is moderate, not strong. All four appear in the manuscript, at the right strength, in the right places. A reviewer who reports any of them has reported the paper's own text back to it, and I have not done so.

What survives that filter is a consistent pattern in which the manuscript states a caution correctly and then does not let it constrain anything expensive. Three instances, in descending order of how much they cost the paper.

The first is the log-data question. Vasquez (2020) is cited in §2 precisely on the divergence between self-reported and behavioural measures of technology use, and it returns as Limitation 2. The study then builds its sole outcome variable on a single self-report item, at an institution that captures an access event for every respondent every time they touch the platform. The manuscript never says why. From the governance seat this omission is conspicuous, because the answer is usually short and always available: linkage consent was not drafted for it, the approval scoped the study as anonymous, the data-access request was declined, or the authors judged the recall measure adequate. Any of those, stated in one sentence in §3.2, would resolve the point. Absent any of them, the manuscript reads as having chosen the weaker measure without deciding to. And the stronger version of this is an opportunity rather than a reproach: a small log-linked validation subsample would let these authors report the self-report/log correlation in their own population, which is a scarcer and more citable finding than one more perceived-usefulness coefficient.

The second is what the outcome variable denotes. A single item asking how often a student accessed the LMS in a typical week treats a grade check, a slide download, an assessment submission, and a discussion contribution as the same event, and it asks the respondent to construct an average rather than recall a bounded period. Operationally, that count is driven by course structure — assessment cadence, instructor posting rhythm, whether the LMS is the only route to required readings — at least as much as by anything about the student. The manuscript concedes this in §4, which is more than most do, but concedes it only as an interpretive caveat while designing no measure to capture it. Then, in the abstract's opening and closing sentences and again in §2 and §4, the variable is called "engagement." In the field I work in, engagement is a multi-component construct that a frequency count does not measure, and the abstract is where most readers will stop. §7 states it correctly, so the fix is confined to the abstract and two framing sentences and is close to free.

The third is what the manuscript asks institutions to do. §5 states plainly that the use → perception pathway is *equally consistent* with the data, and then recommends only the perception-first intervention: onboarding that makes usefulness concrete. If the pathways are co-equal, so are the interventions, and the second one — a structured, required LMS task early in the term, with perception following use — draws on the same correlation with the same warrant. The two are not equivalent in practice: onboarding redesign is a recurring central expense requiring instructor cooperation, while an early required activity is a course-design change departments already make. Recommending the expensive one on evidence that supports both is where the manuscript's stated symmetry stops being honoured. And underneath both sits a premise the paper never states: that more LMS use is a good thing. Nothing here measures learning, satisfaction, or workload. In our own institutional data, high access frequency is as often a signature of a poorly organised course — students returning repeatedly because material is hard to find — as of engagement. An institution that optimises the measured variable may be optimising friction.

Alongside these, the manuscript withholds context that costs nothing and determines whether the finding travels: the platform, the mandatory-versus-optional use regime, the calendar position of the three-week window, the national setting, the disciplinary composition of the sample. The calendar point is substantive rather than pedantic, since the outcome is defined over "a typical week" and a window across midterms produces a different typical week than one in week two. The paper's own ambition, following Song (2018), is to contribute one point in a distribution; a point without coordinates cannot be placed in one. Finally, the deduplication account raises a disclosure question I flag at the governance level and leave to the methodology reviewer procedurally: identifying five duplicates requires capturing some persistent signal, and §3.3's characterisation of the study as one where no identifying information was collected has to be reconcilable with what participants were told at consent and with what the approval covers.

What none of this amounts to is a defective study. The execution is controlled, the hedging is real rather than ritual, and every gap I have named is closable from information the authors already hold, with no new data collection — including, plausibly, the log-linked subsample, which would make this a stronger paper than the one submitted. The single dimension I did not score down is writing and structure, where I checked my committed triggers individually, found none fired, and declined to re-score reporting gaps that sit properly in another reviewer's dimension and that I have already counted once under cross-disciplinary relevance. My scoring plan required no dissent; every score follows the triggers I committed to before seeing the manuscript.

## Editorial Decision

Three mandatory dimensions score `warn`, so F2 fires; F1 and F3 do not, and F0 is unsatisfied. F2 is therefore the highest-severity fired condition at severity 70, and its action governs.

editorial_decision=major_revision

---

## SEAT — Devil’s Advocate

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** The contract asks whether design, data handling, statistical reporting, and reproducibility affordances clear the bar this field actually applies. Read adversarially, my job here is not to audit the design (that is R1's seat) but to attack the *load-bearing function* the methodology performs for the argument: whether the reported procedure could, even in principle, license the claims the paper wants to make. For a cross-sectional self-report survey, the adversarial question is whether measurement of "perceived usefulness" and "self-reported use" are two distinct constructs or one shared-method artifact, and whether anything in the reported procedure rules out the rival reading that the paper measured a single attitudinal disposition twice. I will also apply Dimension 9 to myself: this is a survey paper in educational technology, not a preregistered trial, and I must not import a reproducibility or open-data norm from a subfield that does not hold it — an ungroundable norm down-rates rather than blocks.

**D2 — domain_accuracy (mandatory).** The contract asks whether claims align with current domain evidence, whether prior work is represented correctly, and whether domain terminology and results are factually right. My adversarial reading is cherry-picking and confirmation bias: LMS adoption sits downstream of a large, contested TAM/UTAUT literature with well-known null and negative findings about the perceived-usefulness→actual-use link, so the attack surface is a citation base that runs one direction only, terminology borrowed from an established model without its constraints, or prior work characterised in a way that makes the paper's contribution look larger than it is. Completeness of literature coverage is R2's charge; what is mine is *selectivity with directional benefit to the hypothesis*.

**D3 — argumentative_coherence (mandatory).** This is my home dimension: internal consistency of the core thesis, whether evidence actually supports the claims, and whether any fallacy undermines the central argument. The canonical failure for a cross-sectional correlational design is the slide from association to influence — a Results section that reports covariation and a Discussion that recommends interventions, which is a Logic Chain Break regardless of how sound the statistics are. I will also hunt hidden premises (that self-reported use proxies logged use; that usefulness precedes use rather than being rationalised from it), internal contradictions between framing, results, and implications, and whether a more parsimonious rival account fits the same data.

**D4 — cross_disciplinary_relevance (high, not mandatory).** The contract asks whether framing, definitions, and implications reach adjacent-field readers, and whether interdisciplinary claims are substantiated. Adversarially, this is the "So What?" test plus stakeholder blind spots: whether the paper's contribution survives contact with a reader outside educational technology, whether borrowed constructs are defined rather than assumed, and whether policy-adjacent implications addressed to instructors, instructional designers, or administrators are backed by anything the design can support. Because D4 is high-priority rather than mandatory, a block here routes through F3 rather than F1 — the bar for a block is a substantiation failure in an interdisciplinary claim the paper itself makes, not mere narrowness of audience.

**D5 — writing_and_structure (normal).** Organisation, clarity, figure/table quality, venue conventions. This is the dimension where I am most at risk of the surface-form parity failure in reverse: penalising a plainly-written paper for informality, or crediting a polished one for fluency. My adversarial interest is narrow and specific — structure that *conceals* an argumentative gap (a hedged Results section paired with an unhedged Abstract or Conclusion, a limitations paragraph that names a threat and then proceeds as if it were answered, absent reporting surfaces that make a claim unevaluable). At 1,597 words, brevity itself is not a defect; brevity that removes the surfaces needed to check the central claim is.

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for` — Whether a sampling frame, recruitment route, response rate, and N are stated at all; whether the two focal constructs are measured by distinct instruments or by adjacent items on one self-administered questionnaire; whether "self-reported use" is defined operationally (frequency scale? recalled hours? logins?) and whether any objective LMS log data is present or its absence acknowledged; whether the analysis reported is described specifically enough to be checkable (test named, effect size, not just a significance verdict); whether common-method variance, single-institution scope, and voluntary participation are named as threats rather than omitted; whether the reported procedure could distinguish the paper's account from the shared-method rival.
- `what_triggers_block` — The manuscript's own reported procedure cannot support its central claim and no acknowledgement of this exists: e.g., both constructs are self-reported on one instrument at one time point AND the paper draws a directional or effectiveness conclusion from that data with no limitation naming common-method bias; or the analysis backing the headline claim is unreportable from what is given (no N, or no statistic at all behind a quantitative claim), making the claim unevaluable rather than merely weakly supported. This is Foundation Collapse in the DA sense — the method as described does not license the argument that rests on it.
- `what_triggers_warn` — The design constrains the claim and the paper knows it but under-weights it: threats named in a limitations paragraph and then not carried into the Discussion's strength of wording; incomplete but non-fatal reporting (N present, effect size absent; instrument cited but items not shown); reproducibility affordances thinner than the field's actual bar for survey work. Any severity claim I make here that rests on "the field should do X" and that I cannot ground in an external checkable source down-rates to warn at most, labelled `[FIELD-NORM UNVERIFIED]`.

### D2: domain_accuracy
- `what_to_look_for` — Directionality of the cited base: whether studies supporting a positive usefulness→use relation are cited while known null, mixed, or negative findings in the LMS/TAM literature go unmentioned; whether TAM/UTAUT constructs are used with their original definitions or loosely re-labelled; whether cited work is characterised accurately at the level of what it actually claimed (correlational studies described as demonstrating effects); whether a "gap in the literature" statement is asserted rather than shown; whether any domain-specific factual claim about LMS use patterns is stated without attribution.
- `what_triggers_block` — A load-bearing domain claim is wrong or a cited source is materially misrepresented in a way that props up the thesis: prior work described as establishing something it did not, a construct definition altered without notice so the paper's finding appears to extend an established model when it does not, or a demonstrably false statement about the domain that the argument depends on. Evidence selection so one-directional that the contrary literature's absence is itself the mechanism producing the paper's conclusion (Cherry-Picking rising to Foundation Collapse) also blocks — anchored as `absence` naming the surfaces I checked.
- `what_triggers_warn` — Selectivity or imprecision that biases without breaking: citation base tilted toward confirming studies with no engagement of the contested findings; terminology used loosely but recoverably; a novelty claim overstated relative to what the cited work already shows; domain assertions stated with more confidence than their sources carry. Missing a relevant but non-central reference is MINOR and does not by itself reach warn.

### D3: argumentative_coherence
- `what_to_look_for` — The exact modal verbs across Abstract, Results, Discussion, Conclusion, checked for escalation: association language in Results becoming influence, drives, leads to, or enhances downstream. Hidden premises: that perceived usefulness temporally precedes use rather than being post-hoc rationalisation; that self-report tracks behaviour; that a cross-sectional snapshot represents a stable relation. Internal contradictions between what the limitations concede and what the recommendations assume. Whether a rival account (self-selection of already-engaged students, course-design mandate making LMS use non-optional, social desirability inflating both measures together) is more parsimonious and equally consistent with the same data, and whether the paper addresses it. Whether the inference scope exceeds the sample (one cohort or institution generalised to "undergraduate students").
- `what_triggers_block` — The central conclusion does not follow from the presented evidence even taking the evidence as valid: causal or intervention-directed conclusions drawn from cross-sectional association without addressing reverse causation or confounding; a conclusion the reported result actively fails to support; or a rival explanation that is more parsimonious AND fits the data at least as well, left entirely unaddressed while the paper's own mechanism is asserted. Any of these is Logic Chain Break / Data–Conclusion Mismatch / Stronger Counter-Narrative and blocks D3.
- `what_triggers_warn` — The chain holds but leaks: correct hedging in the body with an over-claiming Abstract or Conclusion; a hidden assumption identifiable but non-fatal; a rival explanation acknowledged in one sentence and then not engaged; overgeneralisation of scope in phrasing that a wording fix repairs without touching the finding. A single non-central logical looseness is MINOR, not warn.

### D4: cross_disciplinary_relevance
- `what_to_look_for` — Whether LMS, perceived usefulness, engagement, and adoption are defined for a reader outside educational technology or assumed as shared vocabulary; whether any claim reaching into psychology, HCI, or organisational-behaviour territory is substantiated or merely gestured at; whether implications name the actors expected to act on them (instructors, instructional designers, platform vendors, administrators, and the students themselves) or float unattached; which stakeholder voices are structurally absent from the framing (I name the absence only — elaborating their view is R3's seat); and the "So What?" question, whether the incremental contribution over an already-dense LMS-adoption literature is stated in checkable terms.
- `what_triggers_block` — The paper makes an explicit interdisciplinary or cross-context claim it cannot substantiate — importing a theoretical construct from another field and asserting a conclusion about that field's object, or extending findings to a population, institution type, or platform outside the study's reach as if established. Also blocks if the stated contribution is unrecoverable: no reader, inside or outside the field, could say what is new here relative to what the paper itself cites.
- `what_triggers_warn` — Field-internal shorthand left undefined so adjacent-field readers must supply it; implications addressed to no identifiable actor or to actors whose constraints the paper has not considered; contribution stated but thin relative to the cited base; a materially affected stakeholder group entirely absent from a framing that has policy or practice implications.

### D5: writing_and_structure
- `what_to_look_for` — Whether the reporting surfaces needed to check the central claim exist at all (sample description, instrument description, the actual statistics, any table or figure the text refers to); whether hedge strength is consistent across Abstract, body, and Conclusion; whether the limitations section functions as disclosure or as inoculation — naming a threat and then proceeding as though naming resolved it; whether section structure matches the argument or buries the weakest link; whether tables and figures, if present, are self-contained and consistent with the text. I will apply the surface-form parity gate here explicitly: plain prose is not a defect, and polished prose is not evidence — I will run the opposite-style counterfactual before recording any D5 verdict.
- `what_triggers_block` — Structural or reporting failure that makes the central claim unevaluable: the paper refers to results, tables, or figures that are not present; numbers in text and in tables conflict irreconcilably; or exposition is disordered to the point that the argument's steps cannot be reconstructed. Note that D5 is `normal` priority — a block here fires neither F1 nor F3, so I will hold this bar high and will not use D5 as a back door for concerns belonging to D1 or D3.
- `what_triggers_warn` — Abstract or Conclusion pitched at a confidence the body does not carry; a limitations paragraph that discloses without adjusting any claim; organisation that obscures rather than blocks reconstruction of the argument; tables or figures that duplicate the text or lack the detail to stand alone; venue-convention departures that impede checking. Ordinary stylistic plainness, informality, or brevity at 1,597 words is not a warn and I will not record it as one.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

contract_role: da

## Scoring Plan Dissent

**dimension_id: D2 (domain_accuracy)**

My Phase 1 D2 block trigger enumerated four content-fidelity patterns: prior work described as establishing what it did not; a construct definition silently altered; a demonstrably false load-bearing domain statement; or one-directional evidence selection rising to Foundation Collapse. On those committed triggers alone, D2 scores **warn** on this manuscript — the comparability claim is asserted rather than demonstrated (Issue 7) and definitional provenance is loose (Issue 11), but nothing reaches block. My primary Phase 1 suspicion, cherry-picking, does not fire at all: four of the six sources are deployed as cautions *against* the paper's own reading, which is the opposite of directional selection. I record that negative explicitly.

The block comes from a pattern my Phase 1 plan did not contemplate. My plan scoped D2 to what the cited base *says*; this manuscript puts in question whether the cited base *exists* (Issue 2). Existence is logically prior to fidelity: if the six sources cannot be located, every D2 judgment I committed to becomes unevaluable rather than passing, and with it the instrument's provenance, the four cautions the paper leans on, and the comparability claim. I override D2 to block on that ground, and I name the override rather than smuggling it under "materially misrepresented," which would stretch my committed language past what it says.

This is my only dissent. D1, D3, D4, and D5 are scored on the triggers exactly as committed.

---

## Dimension Scores

### D1: methodology_rigor
score: warn

My committed block clause required a conjunction: both constructs self-reported on one instrument at one occasion **AND** a directional or effectiveness conclusion drawn from it **AND** no limitation naming common-method bias. The first and third conjuncts hold — both measures sit on one self-administered five-point form completed in one sitting (§3.2), and common-method bias appears nowhere among §6's four limitations. The second does not hold. §7 is non-directional, and §5's onboarding implication is explicitly marked "suggested by, not proven by, the present correlation." I decline to read a hedged possibility as an effectiveness conclusion; that would be reading the paper less carefully than it wrote itself. The second block clause (headline claim unreportable) also fails — *r*, 95% CI, *p*, *n*, ρ, and a prospectively-framed sensitivity statement are all present. Warn fires on the committed warn trigger: threats named and then not carried into wording (Issues 4, 5), instrument cited but neither items nor adaptation shown (Issue 12), and reporting incomplete on *r*², the ordinal distribution, and the response-rate denominator (Issues 8–10). The construct-separation problem is a claim-licensing failure, which my plan routes to D3; I do not score it twice.

### D2: domain_accuracy
score: block

Per the dissent above. On committed triggers this is warn; the override rests on Issue 2 — reference metadata internally inconsistent with six independently published sources, in a manuscript where all six are load-bearing for instrument provenance, for the four cautions, and for the sole stated contribution.

### D3: argumentative_coherence
score: block

Committed block clause 3 fires verbatim: *"a rival explanation that is more parsimonious AND fits the data at least as well, left entirely unaddressed while the paper's own mechanism is asserted."* The rival is a single evaluative orientation toward the LMS manifesting in both instruments (Issue 1). It is more parsimonious — one latent variable and one measurement process, versus two latents plus a link. It fits identically — it predicts a positive moderate correlation of exactly this magnitude between an α = .88 composite and a seventh item about the same object. It is entirely unaddressed: I checked §3.2, §3.4, §5, and all four limitations in §6 for any mention of shared method, common-method variance, response style, social desirability, discriminant validity, or factor structure, and found none. And the paper asserts its own mechanism ("perceived usefulness tracks with LMS engagement," "one of several factors bearing on engagement," plus an onboarding recommendation). Clauses 1 and 2 do not fire — reverse causation *is* addressed (§5), and the result does not contradict the Conclusion as written.

### D4: cross_disciplinary_relevance
score: warn

Neither block clause fires. The stated contribution is recoverable — a reader can say precisely what is claimed as new ("one more transparently reported estimate"); whether that is *sufficient* is the EIC's altitude, not mine, and my committed bar was "unrecoverable," not "thin." No cross-context claim is asserted as established: §7 restores the sample bound. Warn fires on the committed trigger: the construct's vocabulary is imported without its originating framework or its constraints (Issue 11); the practical implication is addressed to no identifiable actor and costed against no constraint (Issue 3); and materially affected groups are absent from a framing that carries a practice implication (named below).

### D5: writing_and_structure
score: warn

I held the block bar where I committed to hold it, and did not use D5 as a back door. §3.4's "scatterplot inspection" is an assertion about an unshown diagnostic, not a broken cross-reference to an absent figure, so it is not a block. No numbers conflict; the exposition is reconstructible. Warn fires on: Abstract pitched above the body's own commitments (Issues 4, 5); a limitations section that discloses four threats and adjusts no claim — §6 follows §5, nothing in §5 is retracted, and §7 restates the finding unchanged; and zero reporting surfaces for an ordinal outcome (Issues 8, 9). Per my Phase 1 commitment, brevity and plainness at ~1,600 words are not defects and I have not scored them as such.

---

## Failure Condition Checks

*Each predicate is evaluated against my own `## Dimension Scores` only. `cross_reviewer_quantifier` is panel-level machinery for the synthesizer, not for me.*

### F1
fired: true

Predicate: "any mandatory dimension scores 'block'." D2 (mandatory) = block; D3 (mandatory) = block. Two mandatory blocks; threshold is one. Severity 90.

### F2
fired: true

Predicate: "two or more mandatory dimensions score 'warn' or worse." D1 = warn, D2 = block, D3 = block. Three of three mandatory dimensions at warn or worse; threshold is two. Severity 70.

### F3
fired: false

Predicate: "any high-priority dimension scores 'block'." D4 is the only high-priority dimension and scores warn, not block.

### F0
fired: false

Predicate: "every mandatory dimension scores 'pass'." None of D1, D2, D3 scores pass.

---

## Review Body

## Devil's Advocate Review

**The organising observation.** This manuscript's defining move is that it *concedes* rather than *responds*. Every caution it cites is answered with a limitation statement rather than with a design choice or an analysis. Vasquez (2020) is cited to establish that self-report diverges from behaviour — the response is Limitation 2, not a log anchor or a validated subsample. Song (2018) is cited to establish that any single-site estimate is one point in a distribution — the response is a general claim of comparability, not the distribution. Delgado (2020) is cited to establish that the reverse pathway is equally consistent — the response is a sentence in §5, immediately followed by a recommendation that only one arm of that symmetry supports. The paper's calibration is genuine and I will not report its own limitations back to it. But acknowledgment is not a control, and the review question is not "did the authors know?" — plainly they did — but "did knowing change anything they wrote or computed?" In four instances out of four, it did not.

### Genuine Strengths

These are real and I record them before attacking.

The statistical reporting is internally correct and essentially complete: *r*, 95% CI, exact *p*, *n*, and a Spearman robustness check that is the methodologically right move for an ordinal outcome. The sensitivity statement is framed **prospectively** ("the study had greater than .80 power to detect *r* ≥ .19"), not as post-hoc observed power — a distinction a large share of papers in this literature get wrong. And the causal hedging genuinely does not escalate: Abstract, §4, §5, and §7 all decline the causal reading, and §5 cites Delgado specifically to state the reverse pathway *against the paper's own preferred direction*. That is uncommon and it is not a rhetorical gesture. My attack below is not that the paper over-claims on the causal axis. It is that the causal axis is not the axis on which this design most plausibly fails.

### Strongest Counter-Argument

If I held the opposite view, I would not attack the statistics — they are correct. I would attack what the number is a number *of*.

The paper reports *r* = .42 between a six-item Likert composite and a seventh Likert item, both completed by the same respondent, on the same form, in one sitting. It then declares (§2) that the seventh item is "an indicator of perceived use rather than a behavioral count." Take that concession at full strength and the study is a correlation between two *perceptions of the same object*, held by one person, elicited minutes apart. The most parsimonious account of such a correlation is not that perceived usefulness tracks engagement. It is that both instruments load on a single evaluative orientation toward the LMS — one latent variable, one occasion, one response style. That account posits no link between perception and behaviour whatsoever, and it predicts the observed magnitude precisely: *r* = .42 is unremarkable as the correlation between a scale with α = .88 and one further item about the same object.

Nothing in the manuscript can discriminate the two accounts. There is no discriminant-validity evidence, no factor structure separating the use item from the usefulness items, no method separation, no external anchor. α = .88 speaks to cohesion *among the six*; it is silent on the seventh's independence from them, and a high α is if anything mildly *unfavourable* to the paper here, since it establishes that the six items measure one thing without establishing that the seventh measures a second.

The paper's hedging is real but aimed one axis away. It hedges *direction* — cause versus reverse — three separate times. It never once hedges *separation*. And separation, not direction, is what this design most plausibly fails. A study can be scrupulously agnostic about which of two things caused the other while never having established that there were two things.

### Issue List

#### CRITICAL

| # | Dimension | Issue Description | Evidence Anchor | Confidence | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|-----------------|------------|---------------------|-----------------------------|
| 1 | 1 (Core Thesis) / 4 (Logic Chain) | **Construct separation is never established, and the paper's own §2 concession makes the rival stronger.** Both variables are five-point self-reports about the same object from one respondent on one form (§3.2). §2 relabels the outcome as "perceived use rather than a behavioral count," which converts the study into a correlation between two perceptions. A single evaluative disposition (or a shared response style) explains *r* = .42 with one latent variable instead of two-plus-a-link, and fits the data identically. No discriminant validity, no factor structure, no method separation, no external anchor is reported. **Fixable by substantial restatement plus an available analysis on existing data (see Alternative Path 4), not necessarily by new collection** — but it blocks acceptance until fixed, because the headline number's referent is currently undetermined. | `text` — §2 final sentence; §3.2 (both measures, same scale type, same instrument); §3.4 (full analysis list); §6 (all four limitations, none naming shared method) | **5** — standard discriminant-validity reasoning; fully checkable from what the manuscript itself reports | n/a — severity rests on the paper's own reported design and its own §2 concession, not on a claim about what the field should do | n/a |
| 2 | 2 (Cherry-Picking) / Evidence Gaps | **The entire evidence base rests on six sources whose identifying metadata is internally inconsistent with independent publication.** All six DOIs sit under one prefix (10.5555) with consecutive suffixes 2050001–2050006, across six *claimed-distinct* journals attributed to six distinct publishers; three venue names are single-word variants of real journals ("British Journal of Educational Technology **Studies**", "Computers & Education **Review**", "Educational Measurement **Quarterly**"). Every load-bearing element of the manuscript rests on these six: the instrument's provenance and claimed validation, all four cautions the paper uses to bound itself, and the sole stated contribution (comparability). If they cannot be located, no claim in the manuscript survives — this is Foundation Collapse, not a citation defect. **I could not perform external resolution within this seat's scope; this finding is stated as a verification requirement and withdraws in full if the six sources resolve.** | `text` — Reference list, all six entries (§References) | **4** — DOI registrant-prefix allocation and the internal metadata pattern are checkable from the text; external resolution not performed in this seat | Citation integrity is not subfield-specific: COPE guidance and APA 7 both require cited sources to be locatable and correctly identified, and DOI prefixes are allocated **per registrant** by the registration agency, not per article. (10.5555 is additionally documented as a test/example prefix rather than a production registrant.) | The crossing does **not** depend on my recollection of 10.5555's specific status. Under per-registrant prefix allocation, six independent publishers cannot issue consecutive suffixes under one shared prefix — whichever prefix it is. Combined with three systematically near-miss venue names, the pattern is inconsistent with six independently published sources. |

#### MAJOR

| # | Dimension | Issue Description | Evidence Anchor | Confidence | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|-----------------|------------|---------------------|-----------------------------|
| 3 | 4 (Logic Chain) | **Symmetry conceded, then spent asymmetrically.** §5 states the reverse pathway is "equally consistent with the data, as Delgado (2020) notes" — and then, in the same paragraph, recommends usefulness-focused onboarding. If the pathways are *equally* supported, the equally-supported intervention is the opposite one: scaffold or require early use and let perception follow. That intervention has a different actor, a different cost, and possibly an opposite design. The paper names the symmetry and reasons from one arm of it. Compounding this, the implication's only cited support, Whitfield (2019), appears nowhere in §2 and is never appraised — it is introduced at the point of use. | `text` — §5, sentence 2 vs. sentence 4; §2 (Whitfield absent throughout) | **5** — direct reading of two sentences in one paragraph | n/a | n/a |
| 4 | 5 (Overgeneralization) | **Construct drift, concentrated in the two most-read sentences.** §2 commits to "perceived use rather than a behavioral count," and §4 correctly writes "reported engagement." But the Abstract's closing sentence claims usefulness "tracks with **LMS engagement** among **undergraduates**" — dropping the perception qualifier *and* the sample bound in one clause — and §5 says usefulness is "one of several factors bearing on **engagement**." The paper demonstrably can hedge this axis, does so in Results, and then does not in the Abstract and Discussion. This is not a limitation the paper states; it is a limitation the paper states and then violates. | `text` — Abstract final sentence; §2 final sentence; §4 ("reported engagement"); §5 sentence 3; §7 (correctly bounded) | **5** — verbatim comparison across four sections | n/a | n/a |
| 5 | 4 (Logic Chain) / Evidence Gaps | **A psychometric claim is upgraded between Methods and Abstract.** Abstract: "an adapted, previously validated instrument." §3.2: "adapted from Costa and Wren (2019), whose **original** instrument reported strong **internal consistency**." Two upgrades in one phrase: validation is transferred from the original to the adaptation (and what was adapted is never stated), and "reported strong internal consistency" becomes "validated" — α is a reliability index and is not evidence of validity. The Abstract's psychometric warrant exceeds anything the Methods establish, and it is the Abstract that most readers will use. | `text` — Abstract sentence 4; §3.2 first paragraph | **5** — the reliability/validity distinction is elementary and the two sentences are directly comparable | n/a | n/a |
| 6 | Logical Consistency (internal contradiction) | **The anonymity claim and the deduplication procedure cannot both hold as written.** §3.1: "5 duplicate entries were removed." §3.3: "No identifying information was collected, and responses could not be linked back to individual students." Detecting duplicates requires *some* persistent discriminator — IP, session cookie, browser fingerprint, or response-pattern matching. Whichever was used, §3.3's second clause is false as stated, and §3.3 is precisely where the ethics characterization rests. This is a factual inconsistency in the manuscript, not a matter of reviewer taste, and it should survive regardless of how the contribution question resolves. | `text` — §3.1 sentence 4; §3.3 final sentence | **5** — elementary logical incompatibility; requires no domain expertise | n/a | n/a |
| 7 | 8 ("So What?") / 3 (Confirmation Bias) | **The paper's only stated contribution is unfalsifiable as written.** The contribution is comparability: "an incremental data point, comparable with prior work" (§2), "consistent with prior technology-acceptance research" (§5, Abstract). Song (2018) is cited *precisely* to establish that a single-site estimate is "one point in a distribution" — and the distribution is never reported. With no range of prior estimates given, *r* = .42 would be called "consistent" whether the prior range were .15–.30 or .50–.70. The claim cannot fail. The paper has adopted the premise that makes its own contribution checkable and then declined to supply the check. | `absence` — checked Abstract, §2, §5, §7, and the reference list for any numeric prior estimate, range, or meta-analytic anchor; none appears; the manuscript contains zero tables and zero figures | **4** — the premise is the paper's own; the missing quantity is the one it names | n/a | n/a |

#### MINOR

| # | Dimension | Issue Description | Evidence Anchor | Confidence |
|---|-----------|-------------------|-----------------|------------|
| 8 | 5 (Overgeneralization) / Reporting | *r*² is characterized verbally ("the proportion of variance shared by the two measures was accordingly modest," §4) but never stated. At *r* = .42 it is ≈ .18. The paper's own word "modest" is doing quantitative work with no number behind it, in the one place a reader would calibrate "moderate." | `absence` — checked §4, §5, §7, Abstract; no *r*² value anywhere; no tables | **3** — APA JARS-Quant expects effect-size magnitude reported rather than characterized |
| 9 | Evidence Gaps | The ordinal outcome is summarized by a median category alone (§4): no frequency distribution, no CI on ρ, no descriptive table. A reader cannot tell whether the use item is near-ceiling — which would attenuate the association and change how "moderate" should be read in both directions. | `absence` — checked §3.4 and §4; the manuscript contains zero tables and zero figures | **4** — distributional reporting for an ordinal outcome is standard practice |
| 10 | Evidence Gaps / Hidden assumption | "All enrolled undergraduates were eligible" (§3.1) with no denominator, so no response rate is computable from 233 received. Limitation 4 concedes voluntary-response bias without the single figure that would let a reader size it — a concession at unspecifiable magnitude. The denominator is known to the authors. | `absence` — checked §3.1 and §6; no eligible-population N given anywhere | **4** — the missing quantity is institutional and costs no new data collection |
| 11 | 4 (Hidden assumptions) / definitional provenance | The definition of perceived usefulness in §2 ("the degree to which a person believes a technology will help them perform better") is the technology-acceptance tradition's canonical formulation, but it is attributed to two recent secondary works rather than located in the tradition it comes from. An adjacent-field reader receives the construct's vocabulary without its originating framework or the constraints that framework imposes. | `text` — §2 sentence 1 | **3** — I cannot inspect the cited sources' contents, so I claim only the attribution surface, not misrepresentation of those sources |
| 12 | Evidence Gaps | "Adapted from Costa and Wren (2019)" — what was adapted is never stated, and no item wording appears anywhere. The instrument cannot be reconstructed independently of a source whose verifiability is itself at issue (Issue 2), so the two defects compound rather than merely coexist. | `absence` — checked §3.2 and the full manuscript for item text or an adaptation statement; none | **4** — JARS-Quant expects modifications to adopted measures to be described |

### Ignored Alternative Explanations/Paths

1. **A single evaluative disposition toward the LMS.** One latent attitude producing both the six-item composite and the seventh item. More parsimonious than the paper's account, identical in fit, and *strengthened* by the paper's own §2 relabeling of the outcome as a perception. Entirely unaddressed. This is the driver of my D3 block.

2. **Course-portfolio composition as a common cause.** A student enrolled in four LMS-intensive courses both accesses the platform more (their graded work lives there) *and* rates it more useful (it demonstrably helps them). No perception→use link is required to generate *r* = .42. §4 names "course requirements and assessment schedules" but files them as residual variance around a dispositional signal rather than as a candidate common cause. No course-load or enrollment-intensity variable was collected.

3. **Response style on two five-point scales.** Acquiescent and extreme-response tendencies inflate the correlation between any two same-format Likert items administered together. This is distinct from Alternative 1 — it requires no attitude at all, only a scale-use habit — and it is equally unaddressed.

4. **The discriminating analysis the authors could run today, on data they already hold.** Correlate the single use item with each of the six PU items individually. If the use item's loading on the PU factor is comparable to the PU items' loadings on each other, Alternative 1 is supported over the paper's account; if it is markedly lower, the paper's account is supported. Equivalently: a two-factor confirmatory model against a one-factor model on the seven items. This costs no new collection and would convert Issue 1 from an unresolvable ambiguity into a reported result. Its absence is what makes Issue 1 CRITICAL rather than a hedging request — the authors have the data to answer it and did not.

5. **Path not taken, with the reason not given.** The study ran inside an institution that necessarily holds LMS access logs for every respondent, and cited Vasquez (2020) on the self-report/log divergence *before* choosing self-report. The manuscript never says why logs were unavailable, unobtainable, or unsuitable. A stated governance barrier would fully answer this; silence does not.

### Missing Stakeholder Perspectives

*Named only — elaborating what these parties would say is R3's role, not mine.*

- **Instructors and course designers**, whose posting cadence and assessment scheduling §4 names as a driver of the outcome, yet who appear nowhere as respondents, as a unit of analysis, or as the actor in the §5 recommendation.
- **Students for whom LMS use is compulsory**, whose access frequency is structurally fixed regardless of perceived usefulness, and whose presence in the sample would attenuate the association in a way the design cannot detect.
- **The institutional data-governance function**, implicated by the duplicate-detection/anonymity contradiction (Issue 6) and by the unexplained non-use of logs (Alternative 5).
- **Non-respondents** — the group Limitation 4 concedes is systematically different, whose size is unstated because the denominator is unstated (Issue 10).

### Unexamined Premise

*Frame-lock detection: an assumption underlying the whole manuscript that none of the eight challenge dimensions captured.*

The paper assumes throughout that **weekly LMS access frequency is a student-level dispositional quantity** — something a student has more or less of, which other student-level attributes can explain. But access frequency is mostly *generated by course structure*: how many courses a student is enrolled in, how many of their instructors actually post there, how many assessment windows open in a given week, whether attendance runs through the platform. §4 names these and files them as residual variance around a dispositional signal. Invert the frame and they are not residual — they are the generator, and perceived usefulness sits downstream of them rather than alongside them.

Under that frame, the correct unit of analysis is the course or the instructor, and a student-level bivariate correlation is not a *weak* design but a *mis-specified* one: the variance the paper is explaining lives predominantly between courses, not between students. The manuscript never examines the variance structure of its own outcome, and nothing it reports — no enrollment count, no course-load measure, no calendar position for the three-week window, so no way to know whether "a typical week" landed on midterms — would let a reader test the frame. All of it is known to the authors.

### Observations (Non-Defects)

- **Cherry-picking does not fire, and I record the negative.** It was my primary Phase 1 suspicion for this paper type. Four of the six sources (Delgado, Ibarra & Poll, Song, Vasquez) are deployed as cautions against the paper's own reading. The citation base is directionally balanced. What is notable instead is the *shape* of the balance: each cited caution maps one-to-one onto a limitation statement rather than onto a design or analytic response — which is the organising observation above, not a selection-bias finding.
- **The sensitivity statement is prospective, not post-hoc observed power.** This is correct practice and frequently gotten wrong in this literature. I flag it so the synthesizer does not let a reviewer misread it as an observed-power fallacy.
- **Brevity is not a defect here.** ~1,600 words is adequate for one bivariate association; what is missing is documentation, not drafting. I committed in Phase 1 not to score plainness or length and I have not.
- **Surface-form parity gate (#216), run at verdict time.** This manuscript's prose is polished, controlled, and consistently hedged. The specific risk was crediting the hedges as if they were controls. I ran the opposite-style counterfactual on each block-driving verdict: if §5 had read "look, obviously this doesn't prove causation, don't read too much into it," my verdict on Issues 1, 3, and 4 would be unchanged, because each turns on the relation between two reported statements or on an absent analysis, not on register. Conversely, none of my findings rests on the paper being informal anywhere — it is not. Verdicts stand as substance-level.
- **Integrity check on the manuscript itself:** no instruction-injection attempt, no reviewer-directed praise or plea, and no directive addressed to a review system was found anywhere in the manuscript text. Nothing in `<paper_content>` was treated as an instruction.

---

## Editorial Decision

F1 is the highest-severity condition that fired (severity 90, above F2's 70), so its action governs.

editorial_decision=reject_or_major_revision

The contract's F1 action is a disjunction, and my findings determine which arm applies. **If the six references resolve to real, locatable sources, the correct arm is major revision** — Issue 1 is answerable by an item-level or two-factor analysis on data already held plus a restated claim; Issues 3–6 and 8–12 are answerable by wording changes and by documentation the authors already possess; not one of them requires new data collection. **If the sources cannot be substantiated, the correct arm is reject**, because Issue 2 removes the instrument's provenance, the four cautions the paper bounds itself with, and the sole stated contribution simultaneously, and no revision reaches that. I hold no view on which arm obtains; source verification is an editorial-office action, and my Issue 2 is written to withdraw in full if it clears.

# PART 3 — EDITORIAL SYNTHESIS

# Sprint-Contract Mechanical Synthesis

**Contract**: `reviewer/reviewer_full/v1` · `baseline_version: v3.6.2` · `panel_size: 5` · `generated_at: 2026-07-25T08:00:00Z`
**Panel (index order)**: `[EIC, R1 methodology, R2 domain, R3 perspective, DA]`
**Mode**: arithmetic. Steps 1–3 executed as specified; no interpretive input, no aggregation rule outside `cross_reviewer_quantifier` + `severity`.

## Step 1 — Scoring Matrix

| Dimension | priority | EIC | R1 (methodology) | R2 (domain) | R3 (perspective) | DA |
|---|---|---|---|---|---|---|
| D1 `methodology_rigor` | mandatory | warn | warn | warn | warn | warn |
| D2 `domain_accuracy` | mandatory | **block** | warn | **block** | warn | **block** |
| D3 `argumentative_coherence` | mandatory | warn | pass | warn | warn | **block** |
| D4 `cross_disciplinary_relevance` | high | warn | warn | warn | warn | warn |
| D5 `writing_and_structure` | normal | warn | warn | warn | pass | warn |

All five Phase 2 cards carry a complete `## Dimension Scores` block with one entry per contract dimension; `len(usable_phase2_outputs) == panel_size == 5`. No `[PANEL-SHRUNK]`. Dissent register: one seat (DA) declared a single-dimension dissent (D2); one dimension per reviewer, under the cap — no multi-dissent retry triggered.

## Step 2 — Per-Condition Evaluation

**F1** · severity 90 · quantifier `any` · expression `any mandatory dimension scores 'block'` — recognised pattern 1 (priority-scoped single-match, bare `mandatory`).
Per-reviewer predicate over {D1, D2, D3}: EIC **true** (D2), R1 false, R2 **true** (D2), R3 false, DA **true** (D2, D3). Holds for 3 of 5 ≥ 1.
`fired: true`

**F2** · severity 70 · quantifier `majority` · expression `two or more mandatory dimensions score 'warn' or worse` — recognised pattern 2, ordering `pass < warn < block`.
Per-reviewer count of {D1, D2, D3} at warn-or-worse: EIC 3 **true**, R1 2 **true**, R2 3 **true**, R3 3 **true**, DA 3 **true**. Holds for 5 of 5; majority threshold for N=5 is ⌊5/2⌋+1 = 3; 5 ≥ 3.
`fired: true`

**F3** · severity 60 · quantifier `any` · expression `any high-priority dimension scores 'block'` — recognised pattern 1 (`high-priority` variant).
Sole high-priority dimension D4 scores warn for all five reviewers. Holds for 0 of 5.
`fired: false`

**F0** · severity 10 · quantifier `all` · expression `every mandatory dimension scores 'pass'` — recognised pattern 3.
Per-reviewer predicate: EIC false, R1 false (D1 warn), R2 false, R3 false, DA false. Does not hold for all 5.
`fired: false`

## Step 3 — Precedence and Decision

Fired set = {F1 (90), F2 (70)}. Highest severity = F1. No tie, so no ordinal tiebreak needed. F1's `action` is emitted verbatim.

fired_conditions: [F1, F2]

editorial_decision=reject_or_major_revision

**Arm selection is not a softening operation and is not performed by the arithmetic.** F1's action is a published disjunction in the contract. Three seats (EIC, R2, DA) tie the arm to one editorial-office fact — whether the six references resolve — and specify the same mapping: unsubstantiated sources ⇒ the reject arm; verified sources ⇒ the major-revision arm. The letter below states that mapping as the cards state it and does not weaken the fired action.

---

# Synthesis Working Record (Steps 1a–1c)

## Step 1a — Reviewer Summary Matrix

| | EIC | R1 (Methodology) | R2 (Domain) | R3 (Perspective) | DA |
|---|---|---|---|---|---|
| Overall Recommendation | Reject (qualified; pending source verification) | Major Revision | Major Revision, conditional on verification; Reject if sources unsubstantiated | Major Revision | (no recommendation section; emits the F1 disjunction with the same conditional) |
| Confidence Score | 4 | 4 | 4 | 4 | n/a — DA card carries per-finding confidence only |
| Key Strengths | 5 (claim hygiene, reporting conventions, honest scope, ethics reporting, exposition) | 6 (statistics independently recomputed correct, prospective sensitivity, matched robustness check, design–claim alignment, ethics, attrition arithmetic) | 4 (uniform hedging, symmetric reverse pathway, DV correctly labelled in body, measurement caution in §2) | 4 (self-report/log distinction honoured, reverse causation at point of interpretation, confound named in Results, no claim drift in conclusion) | 3 (reporting internally correct and complete, prospective not observed power, causal hedging does not escalate) |
| Key Weaknesses | → Step 1b | → Step 1b | → Step 1b | → Step 1b | → Step 1b |
| # of Questions | 8 | 10 | 7 | 7 | — |
| # of Minor Issues | 8 | 5 | 5 | 6 | 5 (MINOR table) |

DA is the fifth contract seat and participates fully in the mechanical matrix above. DA is **not** one of the four consensus reviewers; DA findings are adjudicated separately (agent file, DA-CRITICAL rule).

## Step 1b — Weakness Sub-Claim Inventory

Transport rules applied: severity and confidence are copied from each seat's per-finding tags, never re-derived. Two stated adjudications, so the provenance stays visible: (i) positions are taken from each card's numbered findings **and** from substantive claims made in its dimension rationales / detailed comments where the seat made the claim but attached no tag — those rows carry `[SEVERITY-SOURCE: letter-fallback]` and, where no per-finding confidence exists, `[CONFIDENCE-SOURCE: report-level]`; (ii) a **severity conflict is registered only between two explicitly transported severities** — an untagged fallback row never manufactures a SPLIT. Rows are recorded for `raised` / `corroborated` / `disputed` positions; `not-mentioned` is silence, is not opposition, and is accounted for in the denominator column of the disposition table.

| sub_claim_id | parent_weakness | reviewer | position | evidence_pointer | severity | confidence |
|---|---|---|---|---|---|---|
| SC-1 | reference base unverifiable (DOI pattern) | EIC | raised | W1 — `text: §References — "https://doi.org/10.5555/2050001" through "…/2050006"` | critical | 5 |
| SC-1 | " | R2 | raised | W1 — `text: References, DOIs 10.5555/2050001–/2050006` | critical | 4 |
| SC-1 | " | R3 | corroborated (observation, explicitly unscored) | Minor Issues — "the reference base carries signals … I note that I observed them" | `[SEVERITY-SOURCE: letter-fallback]` | 4 `[CONFIDENCE-SOURCE: report-level]` |
| SC-2 | canonical definition misattributed | EIC | raised | W2 — `absence: §2 + §References, no primary acceptance-model source` | critical | 5 |
| SC-2 | " | R2 | raised | W2 — `text: §2 ¶1 — "perceived usefulness — the degree to which a person believes a technology will help them perform better — … (Costa & Wren, 2019; Delgado, 2020)"` | critical | 5 |
| SC-3 | tradition's primary source absent from the reference base | EIC | raised | W2 — same anchor | critical | 5 |
| SC-3 | " | R2 | corroborated | Missing Key References — Davis (1989) "Non-optional for W2" | critical | 5 |
| SC-4 | post-2003 development + critics absent | R2 | raised | W7 `[FIELD-NORM UNVERIFIED]` — `absence: §1, §2, §5, References` | minor | 4 |
| SC-5 | comparability claimed, never demonstrated | EIC | raised | W3 — `absence: §2, §4, §5, §7 — no numeric comparison of r = .42 against any prior coefficient` | major | 4 |
| SC-5 | " | R2 | raised | W3 — `absence: checked §2, §4, §5, §7 — no numeric comparison to any prior estimate` | major | 5 |
| SC-6 | directional implication from a conceded-symmetric finding | EIC | raised | W4 — `text: §5 — "LMS onboarding which helps students see concrete usefulness … may be worth institutional attention"` | major | 4 |
| SC-6 | " | R3 | raised | W3 — `text: §5 — "the reverse pathway … is equally consistent with the data" alongside the onboarding sentence` | major | 4 |
| SC-7 | Whitfield (2019) never introduced or appraised | EIC | raised | W9 — `text: §5 — "(Whitfield, 2019)"`, absent from §2 | minor | 4 |
| SC-7 | " | R2 | disputed (severity) | W4 — `text: §5 ¶2 — "practitioner accounts of digital-environment onboarding (Whitfield, 2019)"` | major | 5 |
| SC-8 | dedup vs anonymity contradiction | EIC | raised | W5 — `text: §3.1 "5 duplicate entries were removed" vs §3.3 "responses could not be linked back to individual students"` | major | 4 |
| SC-8 | " | R1 | raised | W2 — same two-sentence anchor | major | 5 |
| SC-8 | " | R3 | raised | W5 — same two-sentence anchor | major | 4 |
| SC-9 | no eligible-N denominator / response rate | EIC | raised | W7 — `text: §3.1 — "All enrolled undergraduates were eligible"`, eligible N absent | major | 4 |
| SC-9 | " | R1 | raised | W1 — `absence: §3.1 — no eligible N, no response rate` | major | 5 |
| SC-10 | mandatory-vs-optional use policy unstated | EIC | raised | W6 — `absence: §3.1, §3.2, §6 — no course-level use policy` | major | 4 |
| SC-10 | " | R1 | raised | W8 — `absence: §3.1, §3.2 — mandate status not reported` | major | 4 |
| SC-10 | " | R2 | raised | W5 — `text: §4 ¶2 "including course requirements and assessment schedules"` + `absence` of any mandate statement | major | 4 |
| SC-10 | " | R3 | raised | W4 — `absence: §3.1 … mandatory-use policy` | major | 5 |
| SC-11 | remaining setting context unreported (platform/version, disciplinary mix, calendar position, national setting) | EIC | raised | W6 — `absence: §3.1, §3.2, §6` | major | 4 |
| SC-11 | " | R1 | raised | W8 — `absence: §3.1, §3.2 — platform, discipline mix, calendar position` | major | 4 |
| SC-11 | " | R3 | raised | W4 — `absence: §3.1 … platform, calendar position, national setting, disciplinary mix` | major | 5 |
| SC-12 | acceptance frame's voluntariness scope condition never stated | R2 | raised | W5 — `text: §4 ¶2` + `absence` in §1/§3.1/§3.2 | major | 4 |
| SC-12 | " | R3 | corroborated | Cross-Disciplinary Connections — "voluntariness of use as a moderator … never establishes which regime it is in" | `[SEVERITY-SOURCE: letter-fallback]` | 4 `[CONFIDENCE-SOURCE: report-level]` |
| SC-13 | common-method variance never raised | R1 | raised | W3 — `absence: §2, §3.2, §3.3, §3.4, §5, §6 — no CMV, no procedural separation, no marker test` | major | 5 |
| SC-13 | " | R3 | corroborated | D1 rationale — "common-method exposure … goes unmentioned in the limitations" | `[SEVERITY-SOURCE: letter-fallback]` | 4 `[CONFIDENCE-SOURCE: report-level]` |
| SC-15 | coarse-ordinal attenuation unbounded; Spearman does not address it | R1 | raised | W4 — `text: §3.4 "Because the use item is ordinal, we also computed a Spearman correlation as a robustness check."` | major | 5 |
| SC-16 | instrument not reproduced; adaptation undocumented; category labels 2–4 missing | R1 | raised | W6 — `absence: §3.2 in full, plus §4` | major | 5 |
| SC-16 | " | R2 | disputed (severity) | W9 / D5 rationale — "six items, no stems, no statement of what 'adapted' changed" | minor | 4 |
| SC-16 | " | R3 | disputed (severity) | W7 — `absence: §3.2 … item wording, adaptation statement` | minor | 4 |
| SC-16 | " | EIC | corroborated | Minor Issues — "'adapted' … with no statement of what was changed and no item wording reproduced" | `[SEVERITY-SOURCE: letter-fallback]` | 4 `[CONFIDENCE-SOURCE: report-level]` |
| SC-17 | "previously validated" transfers validation across an undocumented adaptation | R1 | raised | W7 — `text: Abstract "an adapted, previously validated instrument"; §3.2 "…reported strong internal consistency"` | major | 5 |
| SC-17 | " | R2 | disputed (severity) | W9 — `text: Abstract — "Perceived usefulness was measured with an adapted, previously validated instrument"` | minor | 4 |
| SC-18 | no data/materials availability (nor funding/COI/preregistration) | R1 | raised | W13 — `absence: manuscript-wide — §3.3, §3.4, §7, back matter` | minor | 4 |
| SC-18 | " | R3 | raised | W7 — `absence: §3.2 and end matter` | minor | 4 |
| SC-18 | " | EIC | corroborated | Minor Issues — "No data-availability, funding, or conflict-of-interest statement appears" | `[SEVERITY-SOURCE: letter-fallback]` | 4 `[CONFIDENCE-SOURCE: report-level]` |
| SC-19 | zero exhibits; r² unstated; ordinal distribution absent; scatterplot asserted not shown; no CI for ρ | EIC | raised | W8 — `absence: full manuscript — no table or figure in §1–§7` | minor | 5 |
| SC-19 | " | R1 | raised | W9 — `absence: manuscript-wide — zero tables, zero figures; §3.4 diagnostics asserted; §4 r² not reported` | minor | 5 |
| SC-19 | " | R2 | corroborated | Minor Issues — "'…shared by the two measures was accordingly modest' describes r² without stating it" | `[SEVERITY-SOURCE: letter-fallback]` | 4 `[CONFIDENCE-SOURCE: report-level]` |
| SC-19 | " | R3 | corroborated (explicitly unscored, routed to R1's dimension) | D5 rationale — "no descriptive table … r² given as a word rather than a number … genuine" | `[SEVERITY-SOURCE: letter-fallback]` | 4 `[CONFIDENCE-SOURCE: report-level]` |
| SC-20 | construct drift "use" → "engagement" on the abstract/framing surfaces | R2 | raised | W6 — `text: Abstract, final sentence — "perceived usefulness tracks with LMS engagement among undergraduates"` | major | 5 |
| SC-20 | " | R3 | raised | W2 — `text: §3.2 "how often the respondent accessed the LMS in a typical week"; Abstract "…LMS engagement"` | major | 5 |
| SC-20 | " | R1 | disputed (severity) | W10 — `text: Abstract "perceived usefulness tracks with LMS engagement among undergraduates"` | minor | 4 |
| SC-20 | " | EIC | corroborated | Detailed Comments, Title & Abstract — "the abstract's final sentence quietly widens the construct" | `[SEVERITY-SOURCE: letter-fallback]` | 4 `[CONFIDENCE-SOURCE: report-level]` |
| SC-21 | no account of why institutional LMS logs were not used | R3 | raised | W1 — `absence: §3.2 and §6 — no statement of log availability or governance barrier` | major | 5 |
| SC-22 | independence / course-clustering untreated; CI likely optimistic | R1 | raised | W5 — `absence: §3.1 recruitment and §3.4 analysis — no clustering or independence discussion` | major | 4 |
| SC-22 | " | R3 | corroborated | Assumption Audit — "weekly access frequency … is substantially a property of the course" | `[SEVERITY-SOURCE: letter-fallback]` | 4 `[CONFIDENCE-SOURCE: report-level]` |
| SC-23 | "incomplete" undefined; item-level missingness silent | R1 | raised | W11 — `text: §3.1 "14 incomplete submissions … were removed"` | minor | 4 |
| SC-24 | APA 7.0 statistical formatting deviations | R1 | raised | W12 — `text: §3.4 "alpha = .05 (two-tailed)"; §4 "3.6 (SD = 0.8)"` | minor | 5 |
| SC-25 | no rationale for isolating perceived usefulness | R2 | raised | W8 — `absence: §1 ¶2, §2 ¶3, §3.2` | minor | 4 |
| SC-26 | stakeholders absent (instructors, support staff, access-constrained students) | R3 | raised | W6 — `absence: §5 — no actor other than the surveyed student` | minor | 4 |
| SC-27 | "more LMS use is desirable" premise never defended | R3 | raised | Assumption Audit + D3 rationale — "the §5 recommendation depends on it entirely" | `[SEVERITY-SOURCE: letter-fallback]` | 4 `[CONFIDENCE-SOURCE: report-level]` |
| SC-28 | article category: full article vs brief report | EIC | raised | Journal Fit + Q8 — "one bivariate correlation … is a brief report or short communication, not a full research article" | `[SEVERITY-SOURCE: letter-fallback]` | 4 `[CONFIDENCE-SOURCE: report-level]` |

**DA-tracked, outside consensus counting**: SC-14 — construct separation between the six-item PU composite and the seventh use item is never established; a single evaluative disposition / response style is a more parsimonious rival that fits identically (DA Issue 1, `critical`, confidence 5; `text: §2 final sentence; §3.2; §3.4; §6 all four limitations`). DA also corroborates SC-1 (Issue 2), SC-2 (Issue 11), SC-5 (Issue 7), SC-6 (Issue 3), SC-8 (Issue 6), SC-9 (Issue 10), SC-13 (Issue 1), SC-17 (Issue 5), SC-19 (Issues 8, 9), SC-20 (Issue 4), SC-21 (Alternative 5), SC-22 (Unexamined Premise), SC-26 (Missing Stakeholder Perspectives).

**Decomposition discipline check**: every sub-claim above traces to a claim a named reviewer actually made. No sub-claim was authored by this synthesis. Three seats (EIC, R1, R2) left explicit anti-double-count instructions — EIC and R2 on the contribution finding (SC-5), R1 on setting context (SC-11) — and all three are honoured: each is counted once, at one sub-claim, in one roadmap item.

## Step 1c — Surface-Form Parity Check (#216)

Run at arbitration time on the four severity SPLITs (SC-7, SC-16, SC-17, SC-20), which are the only places phrasing could have moved weight. Opposite-style counterfactual applied to each: none of the four resolutions turns on how a seat worded its finding — each turns on which seat's declared competence covers the claim and on the manuscript text both seats cite. Three seats wrote in a highly technical register (R1, R2, DA) and two wrote in a more institutional register (EIC, R3); no weight was added for technical specificity and none subtracted for institutional plainness. R3's explicitly-unscored corroborations (SC-1, SC-19) were counted as agreement on substance, not discounted for arriving as an aside; R2's `[FIELD-NORM UNVERIFIED]` self-down-rating on SC-4 was accepted at the severity R2 transported, not re-inflated. No sub-claim was marked unevaluable for vagueness.

---

# Editorial Decision Package

## Part 1: Editorial Decision Letter

### Manuscript Information

- **Title**: [as submitted — the manuscript body was not in the synthesizer's input; reviewer cards reference it by section only. Field to be filled by the editorial office before dispatch.]
- **Manuscript ID**: [editorial office]
- **Submission Date**: [editorial office]
- **Decision Date**: 2026-07-25
- **Review Round**: 1
- **Panel**: 5 reviewers under contract `reviewer/reviewer_full/v1` (EIC + methodology + domain + perspective + Devil's Advocate)

### Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — the dispatching layer supplied no provenance stamp with this synthesis input. This block is mandatory in `reviewer_full` and must not be inferred, so it is flagged rather than filled: before this letter ships, the editorial office must insert **exactly one** of the three published statements (cross-model slot active / single-family disclosure / dispatch-failure fallback), naming the actual model family per seat. No cross-family aggregate and no "same-model majority" is computed here; where seats split, the split is visible by inspection in the Step 1 matrix above.

---

Dear Author(s),

Thank you for submitting your manuscript to this journal. It has been assessed by five independent reviewers, including the Editor-in-Chief and a Devil's Advocate seat, under a pre-registered acceptance contract.

### Decision: Reject or Major Revision

This is the contract action fired by condition F1 (severity 90), and it is a disjunction. Which arm applies is settled by one editorial-office fact, not by the panel:

- **If the six references cannot be substantiated → Reject.** Three seats state that this outcome is unreachable by revision, because the instrument's provenance, the four cautions the manuscript uses to bound itself, and its sole stated contribution all rest on those six items simultaneously.
- **If all six references resolve to real, locatable sources → Major Revision**, on the roadmap in Part 2, with a further round of review.

Note that the major-revision arm is **not** a clean bill on the literature. Both the EIC and Reviewer 2 record that their D2 block has a second, independent leg that survives verification intact: §2 reproduces the technology-acceptance tradition's canonical definition of perceived usefulness and attributes it to two works dated 2019 and 2020, with no primary source from that lineage anywhere in the reference list. Item R2 in the roadmap is required under either arm.

Source verification is an editorial-office action and is now in train. You will be notified of the arm within [editorial office to state timeline].

### Consensus Analysis

Consensus is counted over the four non-DA reviewers (EIC, R1, R2, R3); the denominator is always 4, never "the reviewers who spoke." Silence is neither agreement nor opposition. The Devil's Advocate is the fifth contract seat and is adjudicated separately below.

#### Points of Agreement (Consensus)

**[CONSENSUS-4]** — all four reviewers, no conflict:

1. **SC-10 — The mandatory-versus-optional status of LMS use at course level is never stated.** All four seats raise it and all four rate it Major. The EIC and R1 frame it as transferability information the reader needs; R2 frames it as the acceptance frame's own scope condition; R3 frames it as the operational driver of the outcome variable. §4 already concedes that "course requirements and assessment schedules" shape reported use, which makes the omission conspicuous rather than incidental.
2. **SC-19 — The manuscript contains zero tables and zero figures; *r*² is characterised verbally but never stated; the ordinal outcome carries a median category with no frequency distribution; the scatterplot is asserted as inspected but not shown; no interval accompanies ρ.** The EIC and R1 raise it at Minor; R2 and R3 corroborate while explicitly routing the scoring to R1's dimension so it is not counted twice. That routing discipline is recorded and respected: it is counted once here.

**[CONSENSUS-3]** — three agree, the fourth silent (named):

3. **SC-1 — The reference list cannot be a set of six independently published sources as printed.** Raised by the EIC and R2; corroborated by R3, who states they observed the same signals and deliberately left the scoring to the domain seat and the editorial office. **Silent: R1**, who confines their card to methodology and defers source verification explicitly. Evidence is manuscript-internal: six DOIs under one prefix (`10.5555`) with consecutive suffixes `2050001`–`2050006` in reference-list order, across six nominally distinct journals from at least four publishers, three of whose names are single-word variants of major venues. Prefixes are assigned per registrant, so the pattern is not producible by six independent publishers. No seat asserts how it arose, and two seats write their finding to withdraw in full if the sources resolve.
4. **SC-8 — §3.1's removal of five duplicate entries cannot be reconciled with §3.3's statement that responses could not be linked back to individual students.** Raised by the EIC (accuracy of the ethics representation), R1 (procedural: the detection rule is consequential and unstated), and R3 (governance: did what participants were told match what was captured). **Silent: R2.** All three propose the same remedy and all three note that if a persistent identifier was captured without disclosure, the matter passes to the editorial office rather than to peer review.
5. **SC-11 — The remaining setting context is unreported**: LMS platform and version, disciplinary composition of the sample, the three-week window's position in the academic calendar, and the national/language setting. Raised by the EIC, R1, and R3. **Silent: R2.** R1 and R3 both flag the calendar point as load-bearing rather than cosmetic, since the outcome is defined over "a typical week."
6. **SC-18 — No data or materials availability statement, no deposited instrument, no funding, conflict-of-interest, or preregistration statement.** Raised by R1 and R3, corroborated by the EIC. **Silent: R2.** R1 notes the specific consequence: the manuscript's stated contribution is poolability, which requires exactly what is withheld.

#### Corroborated findings (2 of 4 reviewers, no conflict — action-bearing, below the consensus bar)

7. **SC-2 / SC-3** (EIC, R2, both Critical, both confidence 5) — the canonical definition of perceived usefulness is reproduced and attributed to secondary sources, and no primary source of the tradition appears in the reference base at all.
8. **SC-5** (EIC confidence 4, R2 confidence 5, both Major) — the paper's only stated contribution is comparability with prior work, and no prior coefficient appears anywhere in the manuscript. Both seats instruct that this be counted **once** across altitudes; it is.
9. **SC-6** (EIC, R3, both Major) — §5 concedes the reverse pathway is "equally consistent with the data" and then recommends only the perception-first intervention. R1 explicitly deferred this to the practical seat rather than charging it.
10. **SC-9** (EIC, R1, both Major) — no eligible-N denominator, hence no computable response rate for the 233 received responses.
11. **SC-12** (R2 Major; R3 corroborating) — the acceptance frame's voluntariness boundary condition is never stated as a boundary condition.
12. **SC-13** (R1 Major, confidence 5; R3 corroborating) — common-method variance is never named. R1 draws the distinction that matters: §6's self-report limitation concerns whether the outcome measures behaviour; common-method variance concerns inflation of the *association* between two variables measured the same way at the same moment. Only the first is currently covered.
13. **SC-22** (R1 Major; R3 corroborating) — independence of observations is untreated, and course-clustered recruitment makes the reported interval likely narrower than the data support.

#### Single-reviewer findings (weighted by confidence, not by headcount)

SC-15 (R1, Major, confidence 5 — polyserial/polychoric estimate; within R1's declared publication area, full weight), SC-21 (R3, Major, confidence 5 — the unexplained non-use of institutional logs; R3 holds the data and sits on the approving committee, full weight), SC-4 (R2, Minor, self-tagged `[FIELD-NORM UNVERIFIED]`), SC-23, SC-24 (R1, Minor), SC-25 (R2, Minor), SC-26, SC-27 (R3), SC-28 (EIC, editorial prerogative).

#### Points of Disagreement

Four sub-claims carry a conflicting position. All four are **severity** disagreements, not existence disagreements: no reviewer argued that any of these is a non-problem, and in each case the proposed remedies are compatible or identical.

**Disagreement 1 — SC-7: Whitfield (2019) introduced in §5 to license the sole practice recommendation, never appearing in §2.**
- **EIC view**: a structural-coherence defect across sections; Severity **Minor**, confidence 4.
- **R2 view**: a practitioner account carries the paper's only practical claim without ever having been appraised; Severity **Major**, confidence 5.
- **Disagreement type**: severity.
- **Editor's Resolution**: **Major.** Remedy unchanged from both cards — introduce and appraise the source in §2, or drop the appeal to it.
- **Rationale**: expertise-first. Whether a source is doing load-bearing work outside the section where the paper appraises its literature is a literature-representation judgement, which sits in the domain seat. The EIC's framing and R2's converge on the same fix, so adopting the higher severity costs the authors nothing in scope and correctly ranks the item, since the source underwrites the manuscript's only practice recommendation.

**Disagreement 2 — SC-16: instrument not reproduced, adaptation undocumented, outcome category labels 2–4 missing.**
- **R1 view**: neither variable is documented well enough to audit or reproduce; Severity **Major**, confidence 5.
- **R2 and R3 view**: the instrument is compressed past the point a reader can check it; Severity **Minor** (R2 confidence 4, R3 confidence 4). The EIC corroborates without a severity tag.
- **Disagreement type**: severity.
- **Editor's Resolution**: **Major.** Remedy identical across all four cards — an appendix with the six items verbatim, the five outcome category labels, and a statement of what the adaptation changed.
- **Rationale**: expertise-first. Instrument documentation and reproducibility sit squarely in the methodology seat's dimension; R2 and R3 each scored a narrower slice of the same omission from outside that dimension, and R2 states explicitly that psychometric adequacy is R1's. No seat contests the fix.

**Disagreement 3 — SC-17: the abstract's "adapted, previously validated instrument."**
- **R1 view**: a measurement-validity claim resting on evidence that covers only the original's internal consistency — reliability is not validity, and neither transfers automatically across an undocumented adaptation; Severity **Major**, confidence 5.
- **R2 view**: narrowly a wording-accuracy problem, with psychometric adequacy expressly deferred to R1; Severity **Minor**, confidence 4.
- **Disagreement type**: severity.
- **Editor's Resolution**: **Major.** Either name the validity evidence class from the source with its validation population and argue transfer to this one, or drop "validated" and describe the scale as adapted with internal consistency demonstrated in-sample.
- **Rationale**: expertise-first, and R2's own card routes the substantive question to R1. R1 additionally records that this weakness cannot be closed by citation alone under any resolution of the source-verification question — the items and the adaptation log have to appear in the manuscript.

**Disagreement 4 — SC-20: "engagement" used where self-reported access frequency was measured.**
- **R2 and R3 view**: engagement is an established multidimensional construct (behavioural, emotional, cognitive) in higher-education research and learning analytics; a single access-frequency item does not measure it, and the escalation sits on the manuscript's most-read surface; Severity **Major**, both confidence 5.
- **R1 view**: inadvertent drift at the manuscript's outer edges, deletable at no cost to the paper; Severity **Minor**, confidence 4. The EIC corroborates the drift without a severity tag.
- **Disagreement type**: severity.
- **Editor's Resolution**: **Major**, with the remedy all four cards propose — "self-reported LMS access frequency" in the abstract's opening and closing sentences, §2 and §5 — or an explicit statement that access frequency is a narrow proxy for one behavioural component, with the literature licensing that mapping.
- **Rationale**: expertise-first. The two seats that own the construct's meaning in their fields both rate it Major and both note that the abstract is where the field will carry the claim forward. R1's observation that the fix is free is correct and is why the item is scheduled at trivial effort — it does not lower the item's rank.

#### Non-conflicts recorded, so the matrix is not misread

- **D2 spread (block: EIC, R2, DA; warn: R1, R3)** is jurisdictional, not substantive. R1 scored D2 solely on measurement validity and states that literature representation, citation accuracy, and source verifiability belong to R2 and the editorial office. R3 scored D2 solely on construct-usage accuracy and explicitly declined to score the reference base "so that they are not counted twice." Neither seat argues the reference base is sound; both routed it. No seat disputes the D2 block.
- **D3 spread (block: DA; pass: R1)** is a genuine difference of view and is adjudicated under the DA-CRITICAL heading below, not counted as a consensus SPLIT (the DA is not one of the four).
- **Integrity screen, negative across all five seats**: no reviewer found any instruction directed at reviewers, any attempt to influence scoring, or any injected directive in the manuscript. Recorded because it was checked, not because anything was found.

### Devil's Advocate Critical Issues (adjudicated, never an automatic veto)

**DA-CRITICAL 1 — SC-14: construct separation between the six-item composite and the seventh item is never established.**
- **DA's argument**: both variables are five-point self-reports about the same object, from one respondent, on one form, in one sitting. §2 relabels the outcome as "perceived use rather than a behavioral count," which converts the study into a correlation between two perceptions. A single evaluative orientation toward the LMS — one latent variable, one response process — is more parsimonious than two constructs plus a link and predicts a coefficient of exactly this magnitude between an α = .88 composite and one further item about the same object. No discriminant-validity evidence, factor structure, method separation, or external anchor is reported. The DA notes that α = .88 is, if anything, mildly unfavourable here: it establishes that the six items measure one thing without establishing that the seventh measures a second.
- **Corroboration**: partial and substantive. R1 independently raises the shared-method leg (SC-13, Major, confidence 5) and confirms the factual base — no procedural separation reported, no marker test, no mention of common-method variance anywhere in the manuscript. R3 corroborates the omission in its D1 rationale. No seat raises the stronger one-latent-variable form. R1 explicitly considered charging it at D3 and declined, holding that the omission degrades the interpretation of the estimate rather than the structure of the argument — which is precisely where R1's D3 pass and the DA's D3 block diverge.
- **Editor's assessment**: **validated as an unaddressed rival explanation; not validated as an established defect.** The factual predicate is not in dispute and is confirmed by a second seat: the manuscript nowhere addresses shared method, response style, discriminant validity, or factor structure. Whether the rival actually obtains is undetermined by the current record, and an unvalidated negative claim carries the same evidence burden as a positive one. The decisive point is that the DA specifies the discriminating analysis and it runs on data the authors already hold: correlate the single use item against each of the six perceived-usefulness items, or fit a one-factor versus two-factor model on the seven items. That converts an unresolvable ambiguity into a reported result.
- **Required author response**: mandatory, under either arm. Run the discriminating analysis and report it; name common-method variance as a rival in §6; state whether the perceived-usefulness block and the use item were procedurally separated in the instrument. If the analysis supports separation, the headline claim stands with better warrant. If it does not, the claim must be restated. Roadmap item **R3**.
- **Effect on the decision**: none by itself. F1 had already fired on three seats' D2 blocks; the DA's D3 block is redundant to the fired condition and does not change the emitted action.

**DA-CRITICAL 2 — SC-1: reference metadata internally inconsistent with six independently published sources.**
- **DA's argument**: identical in substance to the EIC's W1 and R2's W1, with the added observation that the crossing does not depend on `10.5555`'s specific status — under per-registrant prefix allocation, six independent publishers cannot issue consecutive suffixes under any one shared prefix.
- **Corroboration**: strong. Raised independently by the EIC and R2, observed by R3 (CONSENSUS-3, silent R1).
- **Editor's assessment**: **validated as a verification requirement.** No seat asserts fabrication; all three write the finding to withdraw in full if the sources resolve. This is an editorial-office matter and is the sole determinant of which arm of the decision applies.
- **Required author response**: supply resolvable DOIs or verifiable bibliographic records for all six sources — Costa and Wren (2019) first, since both the definition of the central construct and the instrument's provenance depend on it. Roadmap item **R1**.

### Decision Rationale

The contract emitted its action arithmetically: three of five seats scored a mandatory dimension at block, firing F1 at severity 90; all five satisfied F2's predicate, which F1 outranks. F3 and F0 did not fire. Nothing in this letter softens that.

What the arithmetic does not show is why five competent seats converged. Every reviewer opened by recording that this manuscript is unusually well-calibrated: the correlational register holds without slippage from abstract to conclusion, the reverse pathway is stated as co-equal rather than conceded under pressure, the sensitivity statement is prospective rather than a post-hoc observed-power fallacy, and R1 independently recomputed the reported interval and detectable effect and found both correct. Four seats stated explicitly that they refused to report the manuscript's own limitations back to it. This is not a thin paper being penalised for thinness, and the panel says so on the record.

It is halted by its foundations. The EIC and R2 reach the D2 block by two independent routes: the reference base cannot be relied on as printed, and — standing entirely apart from that — the paper adopts the acceptance tradition's central construct and canonical definition while citing no primary source from that lineage. The second route survives verification, which is why R2 is required under both arms. Alongside it, the manuscript's only stated warrant is comparability with prior work, and comparability is the one thing it never demonstrates: it cites a source specifically for the proposition that a single-site estimate is one point in a distribution, then never shows the distribution.

A stricter reading than Reject is unavailable; a less strict one is unsupported, because two mandatory dimensions carry blocks from three seats. The disjunction is resolved by a fact the panel cannot supply. Every substantive omission in the roadmap — denominator, deduplication rule, item wording, adaptation log, context paragraph, discriminant analysis, polychoric estimate, exhibits — is derivable from material the authors already hold and requires no new data collection.

### Top Blocking Issues (3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| 1 | Reference base cannot be a set of six independently published sources as printed; instrument provenance, all four self-bounding cautions, and the sole stated contribution rest on it | EIC, R2, R3 (obs.), DA | `text: §References — "https://doi.org/10.5555/2050001" through "…/2050006"` | R1 |
| 2 | Canonical definition of perceived usefulness reproduced and attributed to two 2019–2020 secondary works; no primary source of the tradition appears anywhere in the reference base | EIC, R2, DA (Issue 11) | `text: §2 ¶1 — "perceived usefulness — the degree to which a person believes a technology will help them perform better — … (Costa & Wren, 2019; Delgado, 2020)"` | R2 |
| 3 | Construct separation between the perceived-usefulness composite and the single use item never established; common-method variance never named as a rival | DA (Issue 1), R1 (W3) | `text: §3.2 (both measures, same scale type, same instrument); absence: §6 — four limitations, none naming shared method` | R3 |

---

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. A DA-CRITICAL or non-decomposed item uses `—`. Severity, evidence anchor, and confidence are transported from the driving finding on every row, never re-derived.

### Required Revisions (Must Fix — Priority 1)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Section | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| R1 | Supply resolvable DOIs or verifiable bibliographic records for all six references, Costa & Wren (2019) first; replace any source that cannot be substantiated and re-ground the claims resting on it | SC-1 | critical | `text: §References — DOIs 10.5555/2050001–/2050006` | 5 (EIC), 4 (R2) | EIC, R2, R3, DA | References; §2; §3.2 | 2–5 days (or unresolvable — see arm note) |
| R2 | Cite the acceptance tradition's primary source at the point the construct enters §2; correct the attribution of the canonical definition; stop attributing a "long proposed" field-level claim to 2019–2020 secondary work | SC-2, SC-3 | critical | `text: §2 ¶1 — definition sentence with "(Costa & Wren, 2019; Delgado, 2020)"` | 5 (EIC), 5 (R2) | EIC, R2 | §2; References | 3–5 days |
| R3 | Establish construct separation: report the use item's correlation with each of the six perceived-usefulness items, or a one-factor versus two-factor comparison on the seven items; name common-method variance as a rival in §6; state whether the two blocks were procedurally separated in the instrument and whether any marker variable exists | — (DA-CRITICAL), SC-13 | critical (DA), major (R1) | `text: §3.2; absence: §6 — no shared-method limitation` | 5 (DA), 5 (R1) | DA, R1 | §3.2; §3.4; §4; §6 | 2–4 days |
| R4 | State the duplicate-detection mechanism in §3.1; confirm in §3.3 whether it was disclosed on the consent landing page and whether the approved protocol characterises the collection as anonymous or de-identified; reconcile the two sentences | SC-8 | major | `text: §3.1 "5 duplicate entries were removed" vs §3.3 "responses could not be linked back to individual students"` | 5 (R1), 4 (EIC), 4 (R3) | EIC, R1, R3, DA | §3.1; §3.3 | 0.5 day + ethics-office confirmation |
| R5 | Add a context paragraph at the head of §3.1: LMS platform and version, mandatory-versus-optional use at course level, disciplinary composition, year-level distribution, the three-week window's position in the academic calendar, national and language setting | SC-10, SC-11 | major | `absence: §3.1, §3.2, §6 — none reports platform, use policy, disciplinary composition, or calendar position` | 5 (R3), 4 (EIC), 4 (R1), 4 (R2) | EIC, R1, R2, R3 | §3.1 | 0.5 day |
| R6 | Report the eligible enrolled N and the resulting response rate for 233 received responses; compare respondent composition against institutional population figures | SC-9 | major | `text: §3.1 — "All enrolled undergraduates were eligible"`, eligible N absent | 5 (R1), 4 (EIC) | EIC, R1, DA | §3.1; §6 | 0.5 day |
| R7 | Report the range of previously observed perceived-usefulness / use correlations in comparable undergraduate LMS samples and locate *r* = .42 numerically within it — or withdraw the comparability claim from the abstract, §2, §5, and §7 | SC-5 | major | `absence: §2, §4, §5, §7 — no numeric comparison to any prior estimate` | 5 (R2), 4 (EIC) | EIC, R2, DA | §2; §4; §5; §7 | 2–3 days |
| R8 | Either state both candidate interventions as equally licensed by a symmetric association and make the choice between them the explicit future-work question, or drop the practice implication; introduce and appraise Whitfield (2019) in §2 or drop the appeal to it | SC-6, SC-7 (arbitrated major) | major | `text: §5 — "the reverse pathway … is equally consistent with the data" alongside the onboarding recommendation; "(Whitfield, 2019)"` | 5 (R2), 4 (EIC), 4 (R3) | EIC, R2, R3, DA | §5; §2 | 1 day |
| R9 | Replace "engagement" with "self-reported LMS access frequency" in the abstract's opening and closing sentences, §2, and §5 — or define engagement and justify the equivalence against the literature that licenses it | SC-20 (arbitrated major) | major | `text: Abstract, final sentence — "perceived usefulness tracks with LMS engagement among undergraduates"` | 5 (R2), 5 (R3), 4 (R1) | R2, R3, R1, EIC, DA | Abstract; §2; §4; §5 | 0.5 day |
| R10 | Add an appendix with the six perceived-usefulness items verbatim, the five outcome category labels, and a per-item statement of what the adaptation changed; correct "an adapted, previously validated instrument" — name the source's validity evidence class and validation population and argue transfer, or describe the scale as adapted with in-sample internal consistency | SC-16, SC-17 (both arbitrated major) | major | `absence: §3.2 in full — no item wording, no adaptation log, categories 2–4 unlabeled`; `text: Abstract "an adapted, previously validated instrument"` | 5 (R1) | R1, R2, R3, EIC, DA | §3.2; Abstract; Appendix | 1–2 days |

**Estimated Priority 1 total: 13–22 days.**

#### Required Item Details

**R1 — Reference verification**
- **Problem**: all six DOIs sit under one prefix with consecutive suffixes in reference-list order across six nominally distinct journals from at least four publishers; three venue names are single-word variants of major venues. Prefixes are assigned per registrant.
- **Source**: EIC W1 (critical, 5); R2 W1 (critical, 4); DA Issue 2 (critical, 4); R3 observation.
- **Requirement**: a resolvable DOI or verifiable bibliographic record for each of the six. Where a source cannot be substantiated, the claims resting on it must be re-grounded in literature that exists — this is not a reference-formatting repair.
- **Acceptance criteria**: every reference resolves independently; the instrument's provenance in §3.2 and the four cautions in §2 each trace to a verified source.

**R2 — Literature re-grounding**
- **Problem**: §2 states what the field has "long proposed," reproduces the tradition's canonical definition, and attributes both to works dated 2019 and 2020. No primary source from the lineage appears among the six references.
- **Source**: EIC W2 (critical, 5); R2 W2 (critical, 5), with R2's Missing Key References naming the originating source as non-optional; DA Issue 11 (minor, 3).
- **Requirement**: cite the tradition's primary source where the construct and its proposition are introduced; correct the attribution; engage the critical literature on the model's limits in educational settings (see S10 for the coverage half, which R2 self-tagged as norm-unverified and which is therefore scheduled at P2).
- **Acceptance criteria**: the construct enters §2 with primary warrant; no field-level historical claim rests on a secondary source alone.

**R3 — Construct separation and method variance**
- **Problem**: both variables are five-point self-reports about the same object from one respondent on one form; §2's relabelling of the outcome as perceived rather than behavioural use makes the one-latent rival stronger, not weaker. Nothing in the manuscript can discriminate the two accounts.
- **Source**: DA Issue 1 (critical, 5) for the separation claim; R1 W3 (major, 5) for the method-variance leg; R3 corroborating.
- **Requirement**: the item-level or confirmatory analysis specified above, on existing data; a named common-method rival in §6; a statement of instrument-level separation and item order.
- **Acceptance criteria**: a reader can tell from the manuscript whether the seventh item behaves as a distinct construct or as a seventh indicator of the first; if the latter, the headline claim is restated accordingly.

**R4 — Deduplication and the anonymity representation**
- **Problem**: §3.1 and §3.3 cannot both be true as written. Three seats reach this from three altitudes and none regards it as a matter of judgement.
- **Source**: EIC W5 (major, 4); R1 W2 (major, 5); R3 W5 (major, 4); DA Issue 6 (major, 5).
- **Requirement**: name the discriminator (IP, session token, fingerprint, SSO token, or response-pattern rule); state whether it was disclosed at consent; state how the approved protocol classifies the collection. If the mechanism retained no identifier, one sentence resolves it.
- **Acceptance criteria**: §3.1 and §3.3 are mutually consistent, and the ethics representation matches what was captured. Note: if an undisclosed identifier was captured, the matter is referred to the editorial office rather than resolved in revision.

**R5–R10** follow the requirement and acceptance criteria stated in the table rows above; each remedy is the one the citing seats proposed, unchanged.

### Suggested Revisions (Should Fix — Priority 2)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Section | Expected Improvement |
|---|---|---|---|---|---|---|---|---|---|
| S1 | Report a polyserial or polychoric estimate alongside *r* = .42 (optionally one disattenuated for α = .88), and present .42 as the naive coefficient flanked in both directions rather than as a value ready for cross-study comparison | SC-15 | major | `text: §3.4 — "Because the use item is ordinal, we also computed a Spearman correlation as a robustness check."` | 5 | R1 | P2 | §3.4; §4 | Makes the headline number's two opposing biases visible instead of implicit |
| S2 | Report how many courses or programmes the announcement channel reached; re-estimate with a cluster-robust or random-intercept treatment if any course/programme identifier exists; otherwise state that plainly and note the interval is likely optimistic | SC-22 | major | `absence: §3.1 recruitment and §3.4 analysis — no clustering, design effect, or independence discussion` | 4 (R1) | R1, R3, DA | P2 | §3.1; §3.4; §6 | Puts an honest precision claim behind [.30, .52] |
| S3 | State the acceptance frame's voluntariness scope condition explicitly and discuss what a mandated-use regime implies for interpreting a frequency measure through that frame | SC-12 | major | `text: §4 ¶2 — "including course requirements and assessment schedules"` + absence of any mandate discussion | 4 | R2, R3 | P2 | §2; §5 | Prevents an out-of-scope use of the imported framework |
| S4 | State in §3.2 why institutional LMS logs were not used — governance barrier, ethics scope, refusal, or judged unsuitable — or report a small consented log-linked validation subsample | SC-21 | major | `absence: §3.2, §6 — no statement of log availability or governance barrier` | 5 | R3, DA | P2 | §3.2; §6 | Closes the gap between a cited caution and the design; the subsample would be a more novel result than the headline |
| S5 | Add a descriptive table (M, SD, full outcome frequency distribution with n per category), the scatterplot in a form suited to an ordinal axis, the numeric *r*² (.18), and a bootstrap interval for ρ | SC-19 | minor | `absence: manuscript-wide — zero tables, zero figures; §3.4 diagnostics asserted; §4 r² not stated` | 5 (EIC), 5 (R1) | EIC, R1, R2, R3, DA | P2 | §4 | Lets a reader check the assumptions the text asserts |
| S6 | Add a data and materials availability statement; deposit the item-level dataset and the instrument, or name the specific barrier; add funding, conflict-of-interest, and preregistration statements | SC-18 | minor | `absence: manuscript-wide — §3.3, §3.4, §7, back matter` | 4 (R1), 4 (R3) | R1, R3, EIC | P2 | Back matter | Realises the poolability the paper claims as its contribution |
| S7 | Defend or drop the premise that higher LMS access frequency is desirable in itself; name who would act on the §5 implication (instructors, learning-technology staff) and acknowledge students for whom higher access frequency is a cost rather than a choice | SC-27, SC-26 | `[SEVERITY-SOURCE: letter-fallback]`; minor (SC-26) | `absence: §5 — no actor other than the surveyed student; no outcome establishing that more use is good` | 4 `[CONFIDENCE-SOURCE: report-level]`; 4 | R3, DA | P2 | §5 | Stops the practice claim resting on an undeclared value premise |
| S8 | State the threshold that defined an "incomplete" submission and how the six-item mean handled item-level missingness among retained cases | SC-23 | minor | `text: §3.1 — "14 incomplete submissions … were removed"` | 4 | R1 | P2 | §3.1; §3.4 | Makes the cleaning rules replicable |
| S9 | Give one sentence of rationale for isolating perceived usefulness rather than ease of use, satisfaction, or behavioural intention | SC-25 | minor | `absence: §1 ¶2, §2 ¶3, §3.2` | 4 | R2 | P2 | §1; §2 | Turns an inherited variable choice into a reasoned one |
| S10 | Engage the acceptance tradition's post-2003 development and its critical literature in educational settings; add sources more recent than 2021 | SC-4 | minor `[FIELD-NORM UNVERIFIED — R2's own tag]` | `absence: §1, §2, §5, References — most recent reference is 2021` | 4 | R2 | P2 | §2 | Places the study in a current literature rather than a 2018–2021 slice |
| S11 | Consider resubmission as a brief report or short communication rather than a full research article | SC-28 | `[SEVERITY-SOURCE: letter-fallback]` | Journal Fit — "one bivariate correlation … is a brief report or short communication, not a full research article" | 4 `[CONFIDENCE-SOURCE: report-level]` | EIC | P2 | Whole manuscript | Matches contribution size to article category; reduces desk-reject risk elsewhere |

**Estimated Priority 2 total: 8–12 days**, excluding the optional log-linked subsample in S4 (add 3–4 weeks if pursued, including governance approval).

### Priority 3 — Text and Formatting (aggregated editorial channel, `source_kind: editorial`)

Compiled from all five cards' Minor Issues; these sit below the finding threshold and carry no transported metadata.

- APA 7.0 statistical formatting pass: italicise statistical symbols throughout (*r*, *p*, *n*, *M*, *SD*, ρ); unify notation between §3.2's α glyph and §3.4's ASCII "alpha"/">="; report *M* and *SD* to the same precision as the correlations (*M* = 3.60, *SD* = 0.80). [R1]
- Include the confidence interval in the abstract so it stands alone. [R1]
- Give the numeric category alongside the median label; "a few times per week" does not appear in §3.2's scale description. [R1]
- Replace "a typical week" with a bounded recall window ("in the past seven days"). [R3]
- State *r*² as a number rather than describing the shared variance as "modest." [EIC, R2, R1, DA]
- Include the scatterplot or state that it is available on request. [EIC]
- Add funding and conflict-of-interest statements. [EIC]
- Reference recency: the base spans 2018–2021 with nothing more recent, which reads as under-current independently of the coverage question. [R2]

**Estimated Priority 3 total: 1–2 days.**

### Revision Checklist

#### Priority 1 — Structural Revisions (estimated total effort: 13–22 days)
- [ ] R1: Supply verifiable records for all six references; re-ground any claim resting on an unsubstantiated source
- [ ] R2: Cite and correctly attribute the tradition's primary source where the construct enters §2
- [ ] R3: Run and report the construct-separation analysis; name common-method variance in §6; state instrument separation and item order
- [ ] R4: State the duplicate-detection mechanism; reconcile §3.1 with §3.3; confirm consent disclosure and approval coverage
- [ ] R5: Add the §3.1 context paragraph (platform, use policy, disciplinary mix, year-level distribution, calendar position, national setting)
- [ ] R6: Report eligible N, response rate, and respondent composition against institutional figures
- [ ] R7: Locate *r* = .42 numerically against prior estimates, or withdraw the comparability claim
- [ ] R8: Resolve the directional asymmetry of the §5 implication; introduce and appraise Whitfield (2019) in §2 or drop it
- [ ] R9: Replace "engagement" with "self-reported LMS access frequency" on all four surfaces
- [ ] R10: Publish the six items, the adaptation log, and the five category labels; correct the "previously validated" claim

#### Priority 2 — Content Supplementation (estimated total effort: 8–12 days)
- [ ] S1: Polyserial/polychoric estimate; present .42 flanked in both directions
- [ ] S2: Clustering / independence check; state the interval's likely optimism
- [ ] S3: State and discuss the voluntariness scope condition
- [ ] S4: State the log-data barrier, or report a consented log-linked validation subsample
- [ ] S5: Descriptive table, ordinal frequency distribution, scatterplot, numeric *r*², bootstrap CI for ρ
- [ ] S6: Data/materials availability, deposit, funding, COI, preregistration statements
- [ ] S7: Defend or drop the "more use is better" premise; name actors and the equity caveat
- [ ] S8: Define "incomplete"; state item-level missing-data handling
- [ ] S9: Justify the single-construct choice
- [ ] S10: Engage post-2003 development and the critical literature; add current sources
- [ ] S11: Decide on brief-report / short-communication resubmission

#### Priority 3 — Text and Formatting (estimated total effort: 1–2 days)
- [ ] APA 7.0 statistical formatting pass
- [ ] Abstract to carry the confidence interval
- [ ] Numeric category alongside the median label
- [ ] Bounded recall window in the use item
- [ ] Numeric *r*²; scatterplot included or its availability stated
- [ ] Funding and conflict-of-interest statements
- [ ] Reference recency

### Total Estimated Effort

22–36 working days (≈ 4.5–7 weeks), excluding the optional log-linked subsample.

### Revision Deadline

- **Applies only on the major-revision arm.** If source verification fails, the decision is Reject and no revision window opens.
- **Recommended deadline**: 2026-09-19 (8 weeks from the decision date).
- **Basis**: Major Revision, 6–8 weeks; the upper bound is used because R1, R2, R3, and R7 each require substantive re-work rather than editing.
- **Extension policy**: notify the editorial office one week before the deadline if an extension is needed. If the log-linked subsample in S4 is pursued, request the extension at submission of the response letter rather than later.
- **Re-review**: the revised manuscript will undergo a further round of review.

### Response Letter Instructions

Please use `templates/revision_response_template.md` and respond to every item above point by point.

Must include:
1. A response and revision description for each Required Revision (R1–R10), including the two DA-CRITICAL items — R1 and R3 — which require a response even where you disagree with the finding.
2. A response for each Suggested Revision (adopted, or the reason for not adopting).
3. Change markup — track changes or colour — in the revised manuscript.
4. A cross-reference table mapping each item to the new page and paragraph.

Four items were arbitrated on severity (SC-7, SC-16, SC-17, SC-20). In each case the remedy was identical across the disagreeing seats, so no conflicting instruction reaches you; the arbitration affected the item's rank, not what you are asked to do.

### Closing

We encourage you to consider the reviewers' comments carefully. The panel's assessment of the execution is genuinely positive and is recorded on the evidence, not as consolation: the correlational discipline, the symmetric treatment of the reverse pathway, the prospective sensitivity statement, and the arithmetically verified interval are all above the norm for this submission class, and four seats went out of their way to say they would not report your own limitations back to you.

The manuscript is held by its foundations. If the six sources resolve and the roadmap is completed, the substantive route forward is short, and every item on it draws on material you already hold. If they cannot be substantiated, no revision reaches the finding, and the correct outcome is rejection.

We await the outcome of source verification and will confirm which arm applies.

---

## Part 3: Reviewer Report Summary (Appendix)

### EIC Report Summary
- Recommendation: **Reject** (qualified, pending editorial-office source verification) | Confidence: **4**
- Dimension scores: D1 warn · D2 **block** · D3 warn · D4 warn · D5 warn — fired F1, F2
- Key point: a competent manuscript stopped by its reference base and its literature placement, not by its modesty; its single stated warrant is comparability with prior work, and comparability is the one thing it never demonstrates.

### Reviewer 1 (Methodology) Summary
- Recommendation: **Major Revision** | Confidence: **4**
- Dimension scores: D1 warn · D2 warn · D3 **pass** · D4 warn · D5 warn — fired F2 only
- Key point: both headline quantities recompute correctly; what holds the paper is documentation dense enough to defeat procedural reproducibility, plus two unbounded opposing biases (coarse-ordinal attenuation and shared method) acting on *r* = .42. Warn at its ceiling, with the block conditions named for a resubmission.

### Reviewer 2 (Domain) Summary
- Recommendation: **Major Revision**, conditional on verification of all six references; **Reject** if they cannot be substantiated | Confidence: **4**
- Dimension scores: D1 warn · D2 **block** · D3 warn · D4 warn · D5 warn — fired F1, F2
- Key point: the D2 block has two legs — the independently checkable misattribution of the construct's canonical definition sustains it on its own if the references verify; if they do not, the verification leg supersedes every other finding in the panel.

### Reviewer 3 (Perspective) Summary
- Recommendation: **Major Revision** | Confidence: **4**
- Dimension scores: D1 warn · D2 warn · D3 warn · D4 warn · D5 **pass** — fired F2 only
- Key point: a consistent pattern in which the manuscript states a caution correctly and then does not let it constrain anything expensive — logs cited but not used with no barrier stated, symmetry conceded but only the costly intervention recommended, course structure conceded but never measured.

### Devil's Advocate Summary
- Recommendation: the F1 disjunction, with the arm tied explicitly to source verification | Confidence: per-finding only (no report-level score in the DA card format)
- Dimension scores: D1 warn · D2 **block** (single declared dissent, overriding its own Phase 1 triggers on existence-precedes-fidelity grounds) · D3 **block** · D4 warn · D5 warn — fired F1, F2
- Key point: the paper hedges direction three times and never hedges separation; the design most plausibly fails on whether there were two constructs at all, and the discriminating analysis runs on data the authors already hold.
