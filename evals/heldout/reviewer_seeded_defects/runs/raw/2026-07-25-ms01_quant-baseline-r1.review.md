# Isolated-dispatch panel review — alpha-1 (baseline condition, 2026-07-25)

(Phase 1 calls were physically separated: each seat’s pre-commitment was produced by a clean
headless `claude -p` call — claude-opus-5, effort xhigh, thinking enabled — that received only
the contract + title/field/word_count and was forbidden from reading any manuscript. Phase 2,
field analysis, and synthesis were separate paper-visible headless calls with read scope
limited to the named skill files and the neutral-named manuscript copy.)

# PART 1 — FIELD ANALYSIS

# Field Analysis Report

## Paper Basic Information

- **Title**: Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment
- **Abstract length**: ~155 words
- **Full text length**: ~3,100 words (excluding references and tables)
- **Number of references**: 15 (all with `10.5555/` placeholder DOIs — a prefix reserved for test/example registration, which suggests a synthetic or non-verified bibliography)

## Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| Primary Discipline | Learning Analytics / Educational Technology (student-facing dashboards) |
| Secondary Disciplines | Higher education student retention & persistence research; Educational psychology (self-regulated learning, goal orientation); Research methodology & applied statistics (measurement, inference) |
| Research Paradigm | Quantitative (nominally mixed-methods in framing — behavioral logs + self-report survey — but the survey component is a single Likert item analyzed descriptively, so this is a single-paradigm quantitative study, not genuine mixed methods) |
| Methodology Type | Observational cross-sectional survey + LMS trace-log analysis; correlational design with median-split group comparison (Pearson *r*, independent-samples *t*-tests). No experimental or quasi-experimental control, no comparison condition, no longitudinal component. |
| Target Journal Tier | **Author's apparent ambition: Q1/Q2** (framing of "practical and generalizable lever," institution-scale implications, worldwide claims). **Evidence-supported tier: Q3 at best in current form** — single-course convenience sample, correlational design, single-item construct measure, no multivariable adjustment, and internal numerical inconsistencies. References are exclusively to low-visibility/likely-fabricated venues with placeholder DOIs, which is itself a signal that the citation base does not support a Q1/Q2 submission. |
| Paper Maturity | **Revised draft** — structure is complete (IMRaD with abstract, keywords, tables, reference list), prose is polished and grammatically clean, and section flow is professional. But the paper is NOT pre-submission: reported statistics contradict each other across the Abstract, Results, and Tables (r = .42 vs r = .24; N = 142 vs t(156) vs t(140) vs Table 2 n = 66 + 61 = 127; p = .008 described as non-significant with t(140) = 1.31; SD = 0.62 with a claimed Min = 1, Max = 5 range at M = 3.847), and the Discussion/Conclusion assert causation from an explicitly correlational design. These are substantive, not cosmetic, defects. |

**Language**: English. Review should be conducted in English.

---

## Recommended Target Journals (Top 3)

1. ***Journal of Learning Analytics*** (SoLAR, open access) — The natural disciplinary home for student-facing dashboard research. Publishes empirical dashboard-engagement studies and has an established methodological review culture that would engage directly with the sessionization definition, the click-proxy validity problem, and the correlational-scope question. Realistic fit **only after** the statistical inconsistencies are resolved and the causal language is removed.

2. ***Computers & Education*** (Elsevier, Q1) — Matches the stated ambition (institutional deployment, retention outcomes, scale), and routinely publishes LMS-trace + self-report designs. However, this journal's reviewers reliably demand multivariable modeling (logistic regression for a dichotomous retention outcome, prior-achievement controls) and would almost certainly reject the current median-split + bivariate-correlation analysis as underpowered against confounding. Listed as an aspirational target that would require substantial methodological strengthening.

3. ***Journal of Computing in Higher Education*** or ***Australasian Journal of Educational Technology*** (Q2, single-institution studies welcome) — The most honest match for a single-course, single-term observational study. Both accept contextually bounded institutional deployments provided the claims are scoped to the setting. This is where the paper can plausibly land after a scope-honest revision (retitled/reframed as an association study in one course).

*Assessment note for the panel*: the recommendation gap between the author's evident ambition (Conclusion: "For higher education institutions worldwide... a dependable strategy") and what the design supports is itself a first-order review finding, not merely a placement question.

---

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC (Editor-in-Chief)
**Identity Description**: Editor-in-Chief of the *Journal of Learning Analytics*, a learning analytics scholar who has served on the SoLAR executive and chaired two LAK conference program committees; has written editorially on the field's persistent "adoption metrics substituting for outcome evidence" problem and personally desk-rejects manuscripts whose conclusions outrun their design.
**Review Focus**:
  1. **Claim–evidence proportionality as a fit question**: Whether the manuscript's core contribution — as stated in the Abstract ("increasing dashboard engagement is a promising lever") and the Conclusion ("associated with, and raises, course retention"; "dependable strategy"; "practical and generalizable lever") — is one this journal can put its name to given an explicitly cross-sectional, single-course design. Assess whether this is a fixable framing problem or a fatal mismatch between what was measured and what is claimed.
  2. **Novelty and contribution against the existing dashboard literature**: The manuscript itself concedes in §2 that "much dashboard research relies on cross-sectional or correlational designs" and cites a critical audit of causal overreach (Ibarra, 2023) — then commits precisely that error. Judge what marginal knowledge a 15th correlational dashboard study adds, and whether the perceived-control component supplies enough novelty to warrant space.
  3. **Publishability integrity screen**: Whether the internal numerical contradictions (Abstract r = .42 vs Results r = .24; sample sizes of 142 / 156+2 / 140+2 / 127 across four locations; p = .008 reported as a *weaker* result than p = .003) are correctable typographical errors or evidence that the reported analyses cannot be reconstructed. Also flag the reference list's uniform `10.5555/` placeholder DOIs, which no production journal would let past copy-editing.
**Will particularly care about**: Whether the paper's own Literature Review diagnoses a field-level pathology (causal language outrunning evidence) that the paper's own Discussion and Conclusion then enact — a self-refuting structure that, for an editor, is disqualifying in its current form regardless of how clean the prose is.
**Possible blind spots**: An EIC operating at the level of fit and framing may accept the *reported* statistics at face value and treat the number conflicts as production errors rather than tracing whether any single coherent dataset could generate all reported values; may also under-scrutinize the participant-consent and data-use disclosure in §3.2, which is an ethics matter rather than an editorial-fit matter. Synthesizer should ensure R1 and R3 close both gaps.

---

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1 — Methodology
**Identity Description**: Quantitative methodologist in educational measurement with a psychometrics and applied-statistics appointment; specializes in observational-data inference for dichotomous educational outcomes (logistic regression, propensity methods for non-randomized educational interventions) and has published on the statistical costs of dichotomizing continuous predictors. Routinely reviews for *Journal of Educational Psychology* and *Educational Researcher* and reconstructs every reported test statistic from the manuscript's own reported degrees of freedom before writing a word.
**Review Focus**:
  1. **Arithmetic reconstruction of every reported statistic against the stated sample.** Specifically: (a) the Abstract reports *r* = .42, §4.2 reports *r* = .24 for what appears to be the same association; (b) §4.3's *t*(156) = 3.02 implies n ≈ 158 groups, but only 87 respondents answered the perceived-control item and only 142 are in the analytic sample; (c) §4.3's *t*(140) = 1.31 implies n = 142, yet Table 2's group *n*s sum to 127; (d) *t*(140) = 1.31 cannot yield *p* = .008 — that *t* corresponds to *p* ≈ .19 two-tailed — and the manuscript simultaneously describes this *p* = .008 result as failing to "reach a comparable level" to a *p* = .003 result, inverting the significance logic; (e) whether a Pearson *r* is the appropriate statistic for a dichotomous retention outcome at all (point-biserial should be named, and a logistic model is the defensible analysis).
  2. **Design–inference gap and confounding.** With no control for prior achievement, motivation, or baseline course engagement, dashboard sessions are a plausible *proxy* for general conscientiousness and overall LMS activity rather than an independent driver of retention. Evaluate the untested reverse-causation and common-cause explanations, and note that the manuscript's own cited caution about retention modeling with trace data (Wexler & Ojo, 2020) goes unaddressed in the analysis.
  3. **Measurement and sampling validity.** (a) The median split on a right-skewed session count discards variance and creates arbitrary groups — the manuscript concedes this is "coarse" but proceeds anyway; (b) *perceived control* is a single item, so no reliability estimate is possible and the construct is unestimable, yet it carries a load-bearing role in the Discussion's SRL mechanism story; (c) a mean of 3.847 with SD = 0.62 on 87 integer responses spanning the full 1–5 range is distributionally implausible and the three-decimal precision is unjustified; (d) §3.2 claims a "random sample" but then describes a voluntary mid-term announcement response — these are incompatible, and the resulting self-selection biases the sample toward students already persisting (retention-outcome survivorship), which alone could manufacture the reported association.
**Will particularly care about**: Whether the reported numbers can be reconstructed from *any* single dataset — if the statistics are mutually incompatible, no amount of revision to the framing rescues the paper, and the correct recommendation is rejection pending the underlying data, not major revision.
**Possible blind spots**: Likely to treat the ethics and consent problem in §3.2 ("Students were not informed that their dashboard activity data would be analyzed for this study") as out of methodological scope; may also under-weight the domain-literature misattribution and the practical-deployment critique. Synthesizer must route those to R2 and R3 respectively and ensure the ethics issue is not lost between seats.

---

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2 — Domain
**Identity Description**: Senior higher education researcher specializing in undergraduate persistence and retention theory (Tinto/Bean lineage), with a decade of work on gateway-course attrition and institutional early-alert systems; has published critical syntheses of learning analytics' engagement with retention theory and reviews for *Research in Higher Education* and *Studies in Higher Education*. Reads reference lists adversarially — checks whether each cited source actually says what the citing sentence claims.
**Review Focus**:
  1. **Citation–claim fidelity audit.** The most serious domain finding: §2 states "Dashboards have been shown to reliably improve outcomes for lower-achieving students, who are said to gain the most from externalized progress cues (Ferro & Nakamura, 2021)" — but that reference is titled *"When dashboards demotivate: Peer comparison and the lower-achieving student."* The citation is attached to a claim that appears to be the *opposite* of the source's thesis, and the word "reliably" imports a certainty the manuscript's own §2 says the literature does not have. Similarly, verify that Osei (2020) and Rutledge & Berange (2022) are represented accurately. Also flag that 8 of 15 listed references (Ainsworth & Devi; Berange; Delacroix & Ohno; Halloran; Kessler & Amadou; Montez; Prakash & Tolliver; Solberg & Whitfield; Wexler & Ojo) never appear in the text — an uncited reference list is a padding signal.
  2. **Theoretical framework depth versus decoration.** Self-regulated learning is invoked as the explanatory mechanism throughout, but no SRL phase is operationalized and no SRL instrument is used — a single "in control" item is not a measure of self-regulation. Assess whether SRL functions here as genuine theory or as post-hoc ornamentation, and whether the retention outcome is theorized at all: the paper measures *course completion*, but the persistence literature it gestures at concerns *institutional* retention. These are different constructs with different determinants, and the Conclusion silently generalizes from one to the other ("retention across programs and disciplines").
  3. **Positioning against what the field already knows.** Whether the manuscript engages the established finding that dashboard effects are heterogeneous and conditional on goal orientation and prior achievement — it names this debate in §2 (Osei, 2020; framing effects; performance-avoidance) but performs no subgroup or moderation analysis, so it cannot contribute to the debate it raises. Evaluate whether the paper's stated contribution to the "who benefits" question in §5 is actually supported by anything it reports.
**Will particularly care about**: Whether the manuscript's *retention* construct is defined tightly enough to mean anything — "remained enrolled and completed the final assessment" is course completion measured at one time point in one course, and the Conclusion's leap to institution-wide, program-wide, worldwide retention strategy is a construct-validity failure compounded by an external-validity failure.
**Possible blind spots**: A retention-theory specialist may accept the statistical reporting as given rather than recomputing it, and may not press the interface-design or data-governance questions. May also be more forgiving of a single-course design than the deployment-practitioner perspective would be. Synthesizer should hold R1's arithmetic findings and R3's deployment findings as independent of this seat's verdict.

---

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3 — Cross-disciplinary / Practical
**Identity Description**: Director of learning technology and student data governance at a large public university — a practitioner-scholar who has actually deployed and then decommissioned two student-facing analytics dashboards at scale, chairs the institution's research data-ethics review for learning-technology studies, and publishes on the ethics and governance of educational trace data (consent, secondary use, algorithmic transparency). Deliberately NOT a retention theorist and NOT a statistician: this seat reads the paper as the person who would be asked to act on it, and as the person who would have had to approve it.

*Note on this seat's angle*: the paper's own framing (Conclusion: institutions "worldwide" should invest in dashboards) invites an implementation-and-governance reading that neither the methodologist nor the retention theorist is positioned to give. This seat supplies the two perspectives the manuscript most conspicuously lacks — research ethics and deployment reality.

**Review Focus**:
  1. **Research ethics and participant consent — the manuscript's undisclosed problem.** §3.2 states plainly: *"Students were not informed that their dashboard activity data would be analyzed for this study."* The survey obtained consent; the behavioral trace data did not. There is no IRB/ethics-approval statement anywhere in the manuscript, no data-availability statement, no conflict-of-interest declaration, and no description of how log data were de-identified or linked to survey responses. Assess whether this constitutes undisclosed secondary use of identifiable student data, whether the linkage of survey responses to individual LMS logs was disclosed to participants, and whether the manuscript is publishable at all without an ethics statement.
  2. **Deployment reality and the actionability of the recommendation.** The Conclusion advises institutions to invest in dashboards and to "encourage students to engage with them" — treating engagement as a manipulable lever. From a deployment standpoint this is the core practical error: engagement is a *behavior of already-engaged students*, and every practitioner attempt to drive dashboard usage (nudges, mandatory check-ins, gamification) tests a fundamentally different intervention from the one this study observed. Evaluate the cost, opportunity cost, and likely null result of acting on this recommendation, and note that a *r* = .24 association explains ~6% of variance — a figure the Conclusion's "dependable strategy" language cannot survive.
  3. **Interface specification, data governance, and reproducibility for adopters.** The dashboard is described only as showing "engagement metrics, assignment progress, and a peer-comparison band" — the peer-comparison band is precisely the feature the manuscript's own §2 identifies as potentially *demotivating*, yet its design (norm group, framing, opt-out) is unspecified. Without interface specification, no institution can replicate the deployment; without the sessionization rule's provenance ("the platform's default") being tied to a named platform, no institution can replicate the measure. Also assess the equity dimension the paper raises and drops: if dashboards differentially affect lower-achieving students, an undifferentiated "encourage everyone to engage" recommendation may be actively harmful to the students the equity rationale is meant to serve.
**Will particularly care about**: Whether a study that did not tell students their behavioral data would be analyzed should be recommending that institutions worldwide expand behavioral analytics deployment — the gap between the paper's own governance practice and its governance-scale recommendation is, from this seat, the finding.
**Possible blind spots**: May under-engage the statistical inconsistencies (defers to R1) and the SRL theory question (defers to R2); as a practitioner, may also over-weight institutional implementability relative to the paper's scholarly contribution, and could conflate "not useful to me" with "not publishable." Synthesizer should weight this seat's ethics finding heavily and its publishability verdict at parity with the others, not above them.

---

## Review Strategy Recommendations

**Special characteristics of the paper requiring particular attention**

1. **This is a "polished surface, unsound core" manuscript, and the panel must not be anchored by fluency.** The prose is clean, the structure is complete, the hedging in §5.1 is professionally written, and the Literature Review displays genuine field awareness. A fast reader — human or model — will over-score it. The defects are all *below* the prose layer: internal numerical contradiction, causal claims the design cannot license, a citation that inverts its source, and an undisclosed ethics gap. Instruct all four reviewers to verify rather than read, and to resist the halo of competent writing. Anti-sycophancy discipline matters more than usual here.

2. **The numerical inconsistencies are the single highest-priority finding and must be resolved before any other verdict is meaningful.** At minimum five independent conflicts exist across Abstract / §4.2 / §4.3 / Table 1 / Table 2: r = .42 vs .24; four incompatible sample sizes (142, ~158, 142, 127); a *t*(140) = 1.31 that cannot produce *p* = .008; a *p* = .008 result narrated as weaker than a *p* = .003 result; and a three-decimal mean (3.847, SD = 0.62) whose distribution is implausible for 87 integer responses spanning 1–5. If these cannot be reconciled against the underlying data, the correct editorial outcome is **reject**, not major revision — a manuscript whose reported analyses cannot be reconstructed is not revisable by editing.

3. **The paper diagnoses its own fatal flaw and then commits it.** §2 cites Ibarra (2023), *"Causal language in correlational learning analytics: A critical audit,"* and §1 promises to "distinguish the pattern in the data from the causal story." §5 then opens with "dashboard engagement **improved** course retention... increasing dashboard engagement therefore **raises** the probability," and §6 concludes with "associated with, **and raises**." This is not an incautious phrase; it is a structural contradiction between the paper's stated epistemic discipline and its actual claims. Every reviewer should encounter this independently — do not let one seat's report inoculate the others.

4. **The Limitations section is a decoy and should be scored as such.** §5.1 lists four real limitations (session-count proxy, self-report bias, single course, dashboard specificity) and thereby performs methodological maturity — while omitting every limitation that would actually constrain the conclusions: the correlational design's inability to support causal claims, self-selection in a voluntary sample, absence of confounding controls, the single-item measure's unestimable reliability, the median split, and the survivorship problem whereby students who dropped out could not respond to a mid-term survey. Reviewers should evaluate what §5.1 *omits*, not only what it includes. A well-written limitations section that excludes the disqualifying limitations is a more serious problem than no limitations section at all.

5. **The reference list requires an existence and fidelity check.** All 15 references carry `10.5555/` DOIs — a prefix reserved for testing and examples, resolving to nothing. Eight of the fifteen are never cited in text. One (Ferro & Nakamura, 2021) is cited for a claim its title contradicts. Whether these are fabricated, placeholder, or anonymized-for-review, the panel should treat citation verification as a first-class review dimension rather than a copy-editing note.

6. **Developmental tone is warranted; developmental verdicts are not.** The manuscript is at revised-draft maturity with genuine strengths — a real research question, appropriate epistemic caution in §1 and §5's third paragraph, and honest self-criticism about the median split and click proxies in §3. Reviewers should write constructively and specify what a defensible version of this study would look like (logistic regression with prior-achievement controls; validated multi-item SRL instrument; full-cohort rather than volunteer sample; scope-honest title and conclusion). But constructive tone must not soften the verdict: the causal claims, the arithmetic, and the ethics gap are each independently sufficient to prevent acceptance.

**Potential complementarity or tension between reviewers**

- **Designed non-overlap.** R1 owns arithmetic, inference, and measurement validity. R2 owns literature fidelity, theoretical framework, and construct definition. R3 owns ethics, governance, and deployment actionability. The EIC owns fit, contribution, and the publishability screen. No two seats are assigned the same finding, and each seat's declared blind spot is covered by at least one other seat — the ethics gap in particular is R3-owned precisely because both R1 and R2 would plausibly let it pass as out of scope.

- **Expected convergence (a strong signal, not redundancy).** All four seats will independently reach the causal-overreach finding by different routes: the EIC via claim–evidence fit, R1 via design–inference gap, R2 via construct generalization, R3 via the actionability of "increasing engagement." When four differently-configured reviewers converge on one finding from four directions, the synthesizer should treat it as the panel's most robust conclusion, not as four instances of the same comment to be merged and discounted.

- **Expected divergence 1 — verdict severity.** R1 is positioned to recommend **reject** (unreconstructable statistics). The EIC and R2 will likely land on **major revision** (fixable framing, salvageable if the numbers resolve). R3 may split: publishable-after-ethics-disclosure, or not publishable at all depending on how the consent gap is read. The synthesizer must not average these into a comfortable middle. Under the panel's precedence-by-severity rule, R1's finding is *conditional* — "reject unless the data reconcile" — and that conditionality should be preserved explicitly in the decision letter rather than collapsed into a severity ranking.

- **Expected divergence 2 — R3 versus R2 on the equity question.** R2 will read the "who benefits from dashboards" debate as a theoretical gap (no moderation analysis). R3 will read it as a harm risk (undifferentiated encouragement may damage the lower-achieving students the equity rationale invokes). These are not the same finding and should not be merged; the theoretical gap is a revision request, the harm risk is a caution about the recommendation itself.

- **Tension to manage — R3's practitioner frame.** R3's deployment lens can slide into "this isn't useful to me," which is not a publishability criterion. The synthesizer should extract R3's ethics and reproducibility findings at full weight while discounting any purely preference-based objection to single-institution scholarship.

- **Devil's Advocate priming.** The strongest available counter-case is: *the manuscript never claims an experiment, states its correlational scope in §1, hedges in §5's third paragraph, and concedes its measurement limits in §3 — perhaps the causal verbs in §5 and §6 are careless phrasing rather than a claim, and the number conflicts are transcription errors in an otherwise sound analysis.* The DA should press this seriously, because if true it converts a reject into a major revision. The panel's counter is that the causal phrasing appears at both the Discussion's opening sentence and the Conclusion's — the two most load-bearing positions in the paper — and is accompanied by explicit prescriptive advice to institutions, which no reading recovers as accidental; and that no single dataset generates all reported statistics, so the errors cannot be confined to transcription without the authors supplying the data.

# PART 2 — SEATS

## SEAT — EIC

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** As Editor-in-Chief I read this dimension as asking whether the study, as reported, would survive the field's peer-review bar on design, data handling, statistical reporting, and reproducibility affordances. My reading is deliberately bird's-eye: I am not the seat that re-derives an estimator or audits a model specification line by line — that belongs to the methodology reviewer. What I own is whether the manuscript's methodological reporting is *sufficient for an editor to send it out and defend the eventual decision*: is there enough of a design description that a reader can tell what was compared to what, are the data provenance and analytic choices stated rather than implied, and does the reporting standard match what this journal's readers have come to expect from a deployment study. For a 2,487-word report in learning analytics, my prior is that space pressure will force compression somewhere in the methods; the editorial question is whether the compression removed detail or removed *verifiability*.

**D2 — domain_accuracy (mandatory).** This dimension asks whether the paper's claims sit correctly inside the current evidence base of its own field, whether prior work is represented as that prior work actually stands, and whether domain-specific terms and results are used accurately. From the EIC seat this is largely a question of scholarly citizenship and journal risk: a paper that misdescribes the field it is entering, or that claims novelty against a literature it has not properly read, damages the journal's standing with exactly the readership it is courting. In learning analytics specifically, the domain has a well-developed and contested vocabulary around dashboards, engagement, retention, and effect estimation; my concern is whether the paper is fluent in that vocabulary or merely adjacent to it.

**D3 — argumentative_coherence (mandatory).** This asks whether the central thesis holds together on its own terms: whether the evidence presented actually supports the claim advanced, and whether any reasoning defect undermines the core argument rather than merely a peripheral one. This is the dimension closest to the editorial core of my seat, because it is where "over-promising and under-delivering" lives — the chain from title to research question to results to conclusion. The title of this submission pairs an engagement measure with a retention outcome; the coherence question is whether the paper's own stated claim about that pairing is the claim its evidence can carry, and whether the abstract and conclusion make the same claim as the results section.

**D4 — cross_disciplinary_relevance (high priority).** This dimension asks whether framing, definitions, and implications are legible to readers in adjacent fields, and whether any interdisciplinary claims made are actually substantiated rather than gestured at. As EIC this is the readership question: learning analytics sits at the intersection of educational research, institutional practice, and data science, and its journals are read by people who hold only one of those three. A paper that is comprehensible only to one sub-community narrows the journal's audience; a paper that reaches across but *asserts* rather than *supports* its reach across is worse, because it borrows authority from a field it has not engaged. Note this is high-priority, not mandatory — it can drag a decision down without alone being able to fire the mandatory-dimension conditions.

**D5 — writing_and_structure (normal priority).** This asks whether the manuscript is organised coherently, exposited clearly, supported by adequate figures and tables, and compliant with the venue's conventions. It is the lowest-stakes of the five in the contract's own weighting, and I treat it accordingly: presentation problems are typically fixable in revision and rarely justify a hard editorial stop on their own. What matters at my seat is the point where presentation stops being cosmetic and starts obstructing evaluation — where a reader cannot locate the study's claim, or where the length is mismatched to what the venue and the argument require. At 2,487 words this submission is short for a full empirical article in most learning-analytics venues, which raises a live structural and format-fit question rather than a presumption of failure.

## Scoring Plan

### D1: methodology_rigor

what_to_look_for: Whether the design is nameable from the text (what was compared, over what period, at what unit of analysis) and whether the paper is explicit about being observational rather than causal; whether the sample is described with enough detail — population, N, the deployment context, how the analytic sample was constituted — that an editor can gauge generalisability; whether the engagement measure and the retention outcome are each operationally defined rather than left as constructs; whether statistical reporting includes uncertainty (intervals, standard errors, model specification) and not only point estimates or p-values; whether reproducibility affordances (data availability, analysis code, instrument or log-schema description, ethics/consent approval for student log data) are stated in some form. Because I am the editorial seat, I score the *adequacy of reported methodology for editorial judgment*, and defer technical adjudication of any specific analytic choice to the methodology reviewer.

what_triggers_block: A methodological gap large enough that no reviewer could evaluate the central claim from the manuscript as submitted, or that the paper's headline claim is structurally unsupportable by the design described. Concretely, any of: (a) the outcome or the exposure/engagement measure is never operationally defined, so the reported association has no determinable referent; (b) no sample description at all — no N, no population, no deployment setting — for an empirical claim; (c) a causal or effectiveness claim about the dashboard advanced from a design with no comparison condition and no acknowledgement of confounding or self-selection, i.e. the paper is not merely under-adjusted but is asserting something its design cannot produce; (d) results reported with no quantification whatsoever supporting the stated conclusion; (e) student behavioural log data used with no mention of ethics approval, consent, or governance where the venue expects it.

what_triggers_warn: Methodology is reportable and evaluable but thinner than the field's bar, in ways revision could repair. Concretely, any of: (a) design and measures are described but key parameters are missing (time window, exclusion rules, handling of missing or zero-engagement students); (b) uncertainty is reported inconsistently — some estimates with intervals, others bare; (c) confounding is acknowledged in prose but not addressed analytically, and the conclusion is hedged accordingly; (d) no data/code availability statement, or one that is pro forma; (e) the compression to ~2,487 words has evidently displaced methodological detail into unstated assumptions that a reader must reconstruct. Multiple minor omissions of this kind aggregate to `warn` rather than each being excused individually.

### D2: domain_accuracy

what_to_look_for: Whether the paper's account of the student-facing dashboard literature reflects that literature as it currently stands, including its well-documented null and mixed findings and its known heterogeneity of effect across student subgroups; whether cited work is characterised as it actually argues, rather than recruited as generic support; whether field-specific terms — engagement, dashboard use, retention, persistence, at-risk identification — are used with their established technical meanings and not silently swapped for adjacent constructs; whether the novelty claim (if any) is bounded by what has been searched rather than asserted absolutely; whether reported quantities are internally consistent wherever the same figure appears more than once.

what_triggers_block: A factual or representational error at the load-bearing level. Concretely, any of: (a) a central claim contradicts well-established findings in the dashboard/learning-analytics evidence base with no acknowledgement that the contradiction exists and no evidence offered for the departure; (b) prior work is materially misrepresented in a way that manufactures the paper's own gap — the cited study is said to have found or not found something it did not; (c) a core domain term is used with a meaning inconsistent with its established use in a way that changes what the paper's claim means; (d) citations that cannot be reconciled with the claims they are attached to, or bibliographic entries whose existence or attribution is doubtful; (e) numeric inconsistency between abstract, results, and conclusion on the paper's headline quantity.

what_triggers_warn: Domain handling is defensible but imprecise or dated. Concretely, any of: (a) the literature is engaged selectively — the supportive strand is cited, the null/mixed strand acknowledged only in passing or not at all; (b) an unbounded novelty or priority claim ("the first study to…") where a search-bounded formulation is what the evidence supports; (c) terminology used loosely but recoverably, e.g. dashboard *access* discussed interchangeably with *engagement* without stating the equivalence; (d) coverage of the field skewed toward older work with no engagement of recent developments; (e) an implication drawn for practice that overshoots what the domain evidence, including this paper's, actually licenses.

### D3: argumentative_coherence

what_to_look_for: Whether title, abstract, research question, results, and conclusion make one consistent claim, or whether the claim strengthens as it travels from results to abstract; whether the stated research question is actually answered by what is reported; whether correlational evidence is described in correlational language throughout, including in the abstract and the practice implications, given that the title pairs engagement with retention; whether limitations are stated where they bite the central claim rather than parked as a generic paragraph; whether alternative explanations for the reported association — particularly self-selection, whereby already-persisting students are also the ones who open the dashboard — are engaged rather than ignored; whether the conclusion's recommendations follow from the finding or from the authors' priors.

what_triggers_block: A defect that undermines the paper's central argument rather than a subsidiary one. Concretely, any of: (a) the conclusion asserts causation or dashboard effectiveness where the reported evidence establishes only association, and this is the paper's headline claim, not an aside; (b) the abstract or title states a finding the results section does not report or contradicts; (c) the stated research question is not answered anywhere in the paper, or a different question is answered in its place; (d) the self-selection/reverse-direction explanation is not merely under-addressed but is *incompatible* with the conclusion drawn and goes wholly unmentioned; (e) an internal contradiction between two claims the paper needs simultaneously for its argument to stand.

what_triggers_warn: The argument holds but leaks. Concretely, any of: (a) claim strength drifts upward between the results section and the abstract or conclusion — hedged in one place, unhedged in another; (b) alternative explanations are named in a limitations paragraph but not carried back into how the conclusion is phrased; (c) practice or policy implications are stated at a confidence the evidence does not fund, without an explicit conditional; (d) the research question is answered but obliquely, requiring the reader to assemble the answer from scattered results; (e) limitations are generic ("as with all observational studies") rather than specific to this deployment and this measure.

### D4: cross_disciplinary_relevance

what_to_look_for: Whether the framing is accessible to the three constituencies this venue serves — education researchers, institutional practitioners, and data/analytics readers — without requiring membership in any one of them; whether technical and educational terms alike are defined at first use for readers coming from the other side; whether the deployment context is described in enough institutional detail that a reader from another system can judge transferability; whether the implications section speaks to more than one of those constituencies; whether any claim that reaches into an adjacent field — learning science mechanisms, behavioural theory, institutional retention policy — is supported by engagement with that field rather than by assertion.

what_triggers_block: This is a high-priority dimension, and under the contract a `block` here fires F3, so I reserve it for a genuine failure of reach, not for stylistic narrowness. Concretely: (a) the paper is unintelligible outside a single narrow sub-community — core constructs or the analytic apparatus are never defined and cannot be inferred, so an adjacent-field reader cannot determine what was found; (b) a substantive interdisciplinary claim (a learning-science mechanism, a psychological process, a policy consequence) is central to the argument and is advanced with no supporting evidence or engagement with the field it is borrowed from; (c) the deployment is described so thinly — no institutional type, no course context, no system description — that the finding is not transferable or even interpretable outside the originating site.

what_triggers_warn: Reach is limited but the paper remains legible. Concretely, any of: (a) written primarily for one constituency, with the others addressed pro forma in a closing sentence; (b) technical terms defined for analytics readers but educational constructs assumed, or the reverse; (c) implications drawn for practice with no consideration of what would differ in another institutional context; (d) an interdisciplinary framing invoked in the introduction and then abandoned, never returning to inform the interpretation; (e) context described but under-specified in ways that hedge transferability without destroying it.

### D5: writing_and_structure

what_to_look_for: Whether the manuscript follows a recognisable and navigable structure for an empirical report in this field; whether the abstract is a faithful, self-contained summary; whether each figure or table is necessary, readable standalone, and captioned so that its interpretation follows from the data shown rather than from the caption's assertion; whether the exposition is clear enough that the central claim is locatable on a first read; whether length and format are appropriate to the venue — at 2,487 words this is short for a full empirical article and may indicate either a well-disciplined brief report or a full study compressed past the point of adequate reporting, and I will note which without assuming the latter; whether reference formatting and venue conventions are observed.

what_triggers_block: Presentation problems severe enough to obstruct evaluation itself. Concretely, any of: (a) the central claim cannot be located because the manuscript has no recognisable results section or no stated finding; (b) figures or tables that the argument depends on are absent, illegible, or captioned in a way that contradicts the data they display; (c) organisation so disordered that reviewers cannot map text to the study's structure; (d) the submission is not a full manuscript — a fragment, an extended abstract submitted as an article, or a text whose length makes the required reporting impossible in principle rather than merely tight. I will not `block` on length alone if the paper is complete and self-consistent as a brief report; a short but complete manuscript is a category question for the editor, not a quality failure.

what_triggers_warn: Presentation degrades the reading without preventing it. Concretely, any of: (a) the abstract omits or misstates a key element of the study (design, sample, headline result); (b) figures or tables are present but under-labelled, redundant, or requiring the body text to be intelligible; (c) sections are disproportionate — an extended introduction against a compressed methods and results, a plausible signature of the ~2,487-word budget; (d) prose is repetitive or imprecise in ways that obscure specific claims; (e) referencing or venue conventions are inconsistently applied; (f) length is mismatched to the article category such that the paper should be resubmitted or reframed as a brief report, which I will raise as a fit-and-format matter rather than a defect of the work.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## EIC Review Report

### Reviewer Identity

Editor-in-Chief of the *Journal of Learning Analytics*, a learning analytics scholar who has served on the SoLAR executive and chaired two LAK conference program committees. I have written editorially on the field's persistent "adoption metrics substituting for outcome evidence" problem, and I desk-reject manuscripts whose conclusions outrun their design. My seat is fit, originality, overall quality, and the publishability screen — not technical adjudication of the estimator, which belongs to the methodology reviewer.

### Overall Recommendation

Reject

### Confidence Score

4

### Summary Assessment

The manuscript reports an observational, cross-sectional study of 142 undergraduates in one introductory statistics course, asking whether students who open a learning analytics dashboard more often are more likely to complete the course. It combines LMS session counts with a single-item perceived-control survey, reports a positive association, and concludes that institutions should invest in dashboards as a retention strategy. The topic is squarely within my journal's scope, the prose is clean, and the Literature Review shows real field awareness — it names the click-proxy validity problem (Vandermeer, 2023), the demotivation risk (Osei, 2020), and the field's causal-language pathology (Ibarra, 2023).

That last citation is where the manuscript turns on itself. Section 2 diagnoses the field's habit of letting causal language outrun correlational evidence, and §1 promises to "distinguish the pattern in the data from the causal story." The Discussion then opens with "dashboard engagement **improved** course retention... increasing dashboard engagement therefore **raises** the probability," and the Conclusion repeats it as "associated with, **and raises**," before advising institutions worldwide to adopt a "dependable strategy." That is not a stray verb; it occupies the two most load-bearing sentences in the paper and is attached to prescriptive advice.

Independently, the reported statistics do not describe one dataset — the headline correlation appears at two different values, and the sample size takes four incompatible values across the Abstract, §4.3, and Table 2. A manuscript whose reported analyses cannot be reconstructed is not revisable by editing.

### Strengths

1. **Genuine field awareness in the Literature Review**: §2 engages the substantive debates rather than assembling generic support — the reflective-prompt framing (Calloway, 2019), the demotivation and goal-orientation strand (Osei, 2020), the click-proxy measurement critique (Vandermeer, 2023), and the causal-overreach audit (Ibarra, 2023). This is the section of a knowledgeable author.

2. **A real and timely research question**: "Whether students who engage more with a learning analytics dashboard are more likely to persist in and complete their course" (§1) is exactly the outcome-level question my readership complains the field keeps avoiding in favour of adoption metrics. The question deserves an answer; my objection is to what this manuscript does with it.

3. **Honest self-criticism at the measurement layer**: §3.3 concedes the median split is "a coarse simplification of a continuous measure and was adopted for interpretability rather than statistical efficiency," and §2 concedes that the present study infers engagement from coarse proxies. Authors who name their own measurement compromises in the Methods are rare and I credit it.

4. **Appropriate restraint in one passage**: §5's third paragraph — "the modest size of the engagement-retention association counsels against overstatement... dashboards help at the margin" — is the correctly calibrated version of this paper's finding. It demonstrates the authors can write the defensible claim; they simply did not put it in the Discussion's opening sentence or the Conclusion.

### Weaknesses

1. **The paper commits the error it diagnoses (fatal in current form)**: §2 cites Ibarra (2023), *"Causal language in correlational learning analytics: A critical audit,"* and §1 pledges to separate pattern from causal story. §5 opens: "dashboard engagement **improved** course retention... increasing dashboard engagement therefore **raises** the probability that a student completes the course." §6: "associated with, **and raises**, course retention." No cross-sectional design with no comparison condition, no adjustment, and a volunteer sample can license "raises." **Improvement direction**: the causal verbs must be removed from §5's opening sentence and §6 entirely, and the Conclusion's prescriptive advice withdrawn or restated as a hypothesis for experimental test. But note that this repair alone does not make the paper publishable — see W2.

2. **Reported statistics do not reconstruct to any single dataset**: the Abstract reports *r* = .42; §4.2 reports *r* = .24 for what reads as the same association. The analytic sample is 142 (Abstract, §3.2, §4.3), yet §4.3 reports *t*(156) and *t*(140), and Table 2's group *n*s sum to 127 for a comparison the text says used "all 142 students." §4.3 also narrates *p* = .008 as failing to "reach a comparable level" to *p* = .003, inverting significance logic. I flag these at the editorial level as a reconstruction failure, not a copy-edit matter; the methodology seat owns the arithmetic. **Improvement direction**: the authors must supply the analysis dataset and script and re-derive every reported quantity. Until they do, no framing revision is meaningful, because it is not established which finding is being reframed.

3. **A citation is attached to a claim its own title contradicts**: §2 asserts "Dashboards have been shown to **reliably** improve outcomes for lower-achieving students... (Ferro & Nakamura, 2021)," but that reference is titled *"When dashboards demotivate: Peer comparison and the lower-achieving student."* The manuscript then builds its equity rationale on this sentence and promises to "return to it in the Discussion" — where it does not return. The word "reliably" also imports a certainty §2 elsewhere says the literature lacks. **Improvement direction**: re-read the source, restate what it actually argues, and rebuild the equity rationale on it — which, on the title's evidence, points the opposite way from the Conclusion's undifferentiated "encourage students to engage."

4. **Contribution does not clear the bar for a further correlational dashboard study**: the manuscript's own §2 states that "much dashboard research relies on cross-sectional or correlational designs." A fifteenth such study earns its space only by adding a design advance, a mechanism test, or a moderation analysis. This one adds a single-item perceived-control descriptive, and §5 claims to "speak to an ongoing debate... about who benefits from dashboards" while reporting no subgroup or moderation analysis at all. **Improvement direction**: either run the moderation analysis the paper says it contributes to, or drop that claim and reposition as a bounded single-site association report.

5. **Governance and ethics disclosure is absent, and §3.2 discloses a problem rather than an approval**: "Students were not informed that their dashboard activity data would be analyzed for this study." There is no ethics-approval statement, no data-availability statement, no conflict-of-interest declaration, and no account of how survey responses were linked to individual LMS logs. My journal cannot publish a behavioural-trace study on this record, and the contrast with a Conclusion urging institutions worldwide to expand behavioural analytics is not one I can print. **Improvement direction**: supply the ethics-approval record and the consent and linkage procedure; if no approval was obtained for the log analysis, that is a matter for the authors' institution before it is a matter for this journal.

### Detailed Comments

#### Journal Fit

Topically this is a natural fit for the *Journal of Learning Analytics*: student-facing dashboards, trace data, and a retention outcome are core scope, and my readers care about exactly the outcome-level question §1 poses. Fit fails on two other axes. First, evidentiary standard: my editorial position is that this journal does not publish adoption-or-association findings dressed as effectiveness findings, and §5/§6 do precisely that. Second, publication record integrity: all fifteen references carry `10.5555/` DOIs, a prefix reserved for test and example registrations that resolves to nothing, and eight of the fifteen (Ainsworth & Devi; Berange; Delacroix & Ohno; Halloran; Kessler & Amadou; Montez; Prakash & Tolliver; Solberg & Whitfield; Wexler & Ojo) never appear in the text. No production journal passes that reference list through copy-editing, and I cannot treat it as a formatting slip when the one reference I can check against its own title (Ferro & Nakamura) is cited for the opposite of what it says.

Should the numbers reconcile and the claims be scoped honestly, this journal remains the right disciplinary home. A single-course observational association study framed as such would also sit well at *Journal of Computing in Higher Education* or *Australasian Journal of Educational Technology*. *Computers & Education*, which the manuscript's institutional ambition seems to target, would demand multivariable modelling with prior-achievement controls that this analysis does not contain.

#### Originality

The core contribution — dashboard engagement covaries with course completion — is not new, and the manuscript concedes as much in §2. The candidate novelty is the perceived-control component, connecting behaviour to the regulatory experience the theory predicts. That component is carried by a single item ("Overall, I feel in control of my learning in this course"), which cannot bear the mechanism story §5 rests on it, and it is measured on 87 respondents while the headline analysis uses 142. As it stands the paper's originality is the pairing of two familiar things, not a new finding about either.

#### Significance

If the association held and were causal, the implication would be substantial: a cheap, scalable retention lever. Neither condition is established. The reported *r* = .24 corresponds to roughly 6% of variance — a figure the Conclusion's "dependable strategy" cannot survive even if every number were verified. And the practical recommendation misidentifies its own target: §6 treats engagement as a manipulable lever, but what was observed is the behaviour of students who chose to open a dashboard. An institution acting on this advice would deploy nudges or mandatory check-ins, which is a different intervention from the one studied here and has no support in this paper. Significance, at present, is local at best.

#### Structural Coherence

This is where my decision is made. The chain from title to conclusion breaks in two places. The title says "Dashboard Engagement and Course Retention," correctly associational; the Abstract escalates to "a promising lever"; §5 escalates to "improved" and "raises"; §6 lands on "dependable strategy" and "generalizable lever" for institutions "worldwide" — from one course, one term, one dashboard, one volunteer sample. The escalation is monotonic and ends in prescription.

The second break is that §5.1 performs methodological maturity while omitting every limitation that would constrain the conclusion. It lists four real limitations — session-count proxy, self-report bias, single course, dashboard specificity — and omits the design's inability to support causal claims, self-selection in a mid-term volunteer sample (students who had already dropped could not respond, which alone could manufacture the association), the absence of any confounding control, the single-item measure, and the median split the Methods themselves flagged. A limitations section that excludes the disqualifying limitations is worse than none, because it purchases reader trust it has not earned.

I also note §5's claim to address "who benefits from dashboards" when no subgroup analysis is reported, and §2's promise to "return to it in the Discussion" regarding the lower-achieving-student equity claim, which is never redeemed.

#### Title & Abstract

The title is the most accurate sentence in the manuscript and should be the model for the rest: it names an association and bounds it to a deployment. The Abstract is not a faithful summary. It reports *r* = .42 where §4.2 reports .24; it describes "self-regulated learning behavior" as measured when what was measured is a single perceived-control item; it omits the design's cross-sectional nature until the reader reaches §3; and it closes on "a promising lever for improving retention," which is a policy claim, not a finding. An abstract that cannot be reconciled with its own results section is a first-order defect, not a polish item.

#### Conclusion

§6 is the manuscript's weakest paragraph and does the most damage. "Associated with, and raises" asserts both the defensible and the indefensible claim in one clause, as though the conjunction resolved the tension. "For higher education institutions worldwide, the implication is clear" generalizes a single introductory statistics section at one university to global practice. "A dependable strategy" characterizes a ~6%-of-variance association. "Across programs and disciplines" silently converts course completion into institutional retention — different constructs with different determinants, a substitution the persistence literature the paper gestures at would not permit. The correctly scoped version of this conclusion already exists in the manuscript, in §5's third paragraph; the authors need to promote it and delete §6's current text.

### Questions for Authors

1. Which is the correct correlation between dashboard engagement and retention — the Abstract's *r* = .42 or §4.2's *r* = .24 — and what analysis produced the other one?
2. Please reconcile the sample sizes: 142 in the Abstract, §3.2, and §4.3's text; *t*(156) and *t*(140) in §4.3; and 127 as the sum of Table 2's group *n*s for a comparison the text states used all 142 students. Can you supply the analysis dataset and script so every reported quantity can be re-derived?
3. §3.2 states participants were "drawn from the course enrollment using a random sample" and, in the next paragraph, that students "who chose to respond" to a mid-term announcement "formed the study sample." These are incompatible sampling descriptions. Which occurred?
4. Was ethics or IRB approval obtained for the analysis of student dashboard activity logs, and under what authority were survey responses linked to individual LMS records, given §3.2's statement that students were not informed their activity data would be analyzed?
5. On what basis does §2 attribute to Ferro & Nakamura (2021) the finding that dashboards "reliably improve outcomes for lower-achieving students," when the cited work is titled *"When dashboards demotivate: Peer comparison and the lower-achieving student"*?
6. §5 states the study speaks to the debate about "who benefits from dashboards." Which reported analysis addresses that question?
7. Given a design with no comparison condition and no adjustment for prior achievement or baseline LMS activity, what warrants "improved" (§5) and "raises" (§6) rather than "was associated with"?

### Minor Issues

- All fifteen references use `10.5555/` DOIs, a prefix reserved for testing and examples; none resolve.
- Eight references are listed but never cited in text (Ainsworth & Devi, 2018; Berange, 2021; Delacroix & Ohno, 2022; Halloran, 2020; Kessler & Amadou, 2019; Montez, 2022; Prakash & Tolliver, 2021; Solberg & Whitfield, 2018; Wexler & Ojo, 2020).
- Perceived control is reported to three decimals (3.847) from 87 integer responses; two decimals at most, and one would be defensible.
- Table 1 reports a final exam score that is never introduced in §3.3 Measures as a study variable, yet §4.3 analyses it.
- Table 2's caption and the §4.3 text disagree on which students were included; the table needs an explicit total.
- The dashboard's peer-comparison band is named in §3.1 but never specified (norm group, framing, opt-out), so the deployment cannot be replicated — and it is the same feature §2 identifies as potentially demotivating.
- The sessionization rule is attributed to "the platform's default" without naming the platform, so the primary measure cannot be reproduced.
- Keywords list "self-regulated learning," but no SRL instrument or phase was operationalized.
- The manuscript contains no data-availability statement, no conflict-of-interest declaration, and no funding statement.

*Integrity note: I checked the manuscript for instruction-injection content addressed to reviewers. None is present; the text is ordinary scholarly prose throughout. No content inside the manuscript altered my scoring or format.*

---

contract_role: eic

## Dimension Scores

### D1: methodology_rigor

score: block

My Phase 1 block trigger (c) reads: "a causal or effectiveness claim about the dashboard advanced from a design with no comparison condition and no acknowledgement of confounding or self-selection, i.e. the paper is not merely under-adjusted but is asserting something its design cannot produce." That trigger fires exactly. §3.1 states an observational cross-sectional design in a single course; §3.4 reports Pearson correlations and t-tests with no adjustment for any covariate; §3.2 describes a mid-term volunteer sample whose self-selection is never analytically addressed; and §5/§6 assert "improved," "raises," and "raises" again. Trigger (e) fires independently: student behavioural log data are analysed with no ethics approval, consent, or governance statement, and §3.2 affirmatively records that students were not informed. Trigger (d) is also engaged in substance — the reported quantification does not reconstruct to a single dataset (r = .42 vs .24; 142 vs 156 vs 140 vs 127; t(140) = 1.31 narrated with p = .008), so the numbers supporting the stated conclusion cannot be taken as reported. Any one of these is sufficient; three fire together.

### D2: domain_accuracy

score: block

My Phase 1 block trigger (b) reads: "prior work is materially misrepresented in a way that manufactures the paper's own gap — the cited study is said to have found or not found something it did not." §2's sentence "Dashboards have been shown to reliably improve outcomes for lower-achieving students... (Ferro & Nakamura, 2021)" is attached to a source titled *"When dashboards demotivate: Peer comparison and the lower-achieving student."* The citation is load-bearing: it carries the equity rationale the paper says it will return to in the Discussion. Trigger (e) fires independently — numeric inconsistency between the Abstract (r = .42) and the Results (r = .24) on the paper's headline quantity. Trigger (d) is engaged by the reference list as a whole: fifteen entries with `10.5555/` placeholder DOIs that resolve to nothing, eight never cited in text. Together these are representational errors at the load-bearing level, not imprecision.

### D3: argumentative_coherence

score: block

My Phase 1 block trigger (a) reads: "the conclusion asserts causation or dashboard effectiveness where the reported evidence establishes only association, and this is the paper's headline claim, not an aside." §5's opening sentence and §6's closing claim are the two most load-bearing positions in the manuscript, and both assert causation ("improved," "raises... the probability," "associated with, and raises"), with §6 adding prescriptive advice to institutions worldwide. Trigger (b) fires independently: the Abstract states r = .42, a value the Results section does not report. Trigger (d) is engaged — the self-selection explanation (a mid-term survey cannot be answered by students who already left, so the retained are structurally over-represented) is incompatible with the conclusion drawn and goes entirely unmentioned, including in §5.1. That §1 and §2 explicitly commit the paper to avoiding this exact error, and §5's third paragraph shows the authors can state the calibrated version, makes the defect a structural contradiction rather than a slip.

### D4: cross_disciplinary_relevance

score: warn

I committed to reserving a `block` here for genuine failures of reach, not stylistic narrowness. The manuscript is legible to all three of my journal's constituencies — the constructs are definable from the text, and an education researcher, a practitioner, and an analytics reader can each determine what was measured. My Phase 1 warn triggers (c), (d), and (e) fire. The deployment is under-specified in ways that hedge transferability: the dashboard is characterised only as showing "engagement metrics, assignment progress, and a peer-comparison band," with no norm group, framing, or opt-out described, and the sessionization rule is attributed to an unnamed "platform's default." The self-regulated learning framing is invoked in §1 and §2 and then abandoned — no SRL phase is operationalized and no SRL instrument used, so it decorates rather than informs the interpretation. And §6 draws institution-wide, worldwide implications with no consideration of what would differ in another institutional context, silently substituting course completion for institutional retention.

### D5: writing_and_structure

score: warn

My Phase 1 block triggers require presentation problems that obstruct evaluation itself; none apply. The manuscript has a recognisable IMRaD structure, a locatable claim, and clean prose. Warn triggers (a), (b), and (e) fire. The Abstract misstates the headline result (r = .42 against §4.2's .24) and describes "self-regulated learning behavior" as measured when a single perceived-control item was collected. Table 1 reports a final exam variable never introduced in §3.3 Measures; Table 2's group *n*s (66 + 61 = 127) contradict the adjacent text's "all 142 students" and the table carries no total. Referencing conventions are not observed — placeholder DOIs throughout, eight uncited entries. I record explicitly that I am *not* scoring the paper's brevity as a defect: at this length a complete brief report would be acceptable, and the compression is not the problem here.

## Failure Condition Checks

### F1

fired: true

D1 (methodology_rigor, mandatory), D2 (domain_accuracy, mandatory), and D3 (argumentative_coherence, mandatory) each score `block`. The expression "any mandatory dimension scores 'block'" is satisfied three times over. Severity 90 — highest in the contract.

### F2

fired: true

The expression "two or more mandatory dimensions score 'warn' or worse" is satisfied: D1, D2, and D3 all score `block`, which is worse than `warn`. Severity 70; subordinate to F1.

### F3

fired: false

D4 (cross_disciplinary_relevance) is the only high-priority dimension and scores `warn`, not `block`. The expression is not satisfied.

### F0

fired: false

The expression "every mandatory dimension scores 'pass'" is not satisfied — none of D1, D2, or D3 scores `pass`.

## Review Body

My seat's judgment is that this manuscript is not publishable in its present form, and that the reason is structural rather than presentational.

The paper is unusually well-informed about its own field. §2 correctly identifies the three live problems in dashboard research — that click counts are poor proxies for cognitive engagement, that peer comparison can demotivate rather than mobilize, and that causal language in this literature routinely outruns correlational evidence — and cites Ibarra (2023) specifically for the last. §1 then commits the study to "distinguish the pattern in the data from the causal story." That commitment is abandoned in the Discussion's opening sentence and again in the Conclusion's, both of which assert that dashboard engagement "raises" retention, and the Conclusion converts the assertion into advice for institutions worldwide. A manuscript that names a field-level pathology and then enacts it in its two most load-bearing sentences presents an editor with a problem no copy-edit resolves. This is not a phrasing accident; the correctly hedged version of the claim exists in §5's third paragraph, which means the authors possessed the calibrated sentence and chose a stronger one for the positions that carry the paper's message.

Underneath the framing problem sits a reconstruction problem. The Abstract's r = .42 and §4.2's r = .24 cannot both describe the same association; 142, 156, 140, and 127 cannot all be the same sample; and §4.3 narrates a p = .008 result as weaker than a p = .003 one. I am the fit-and-framing seat and I defer the arithmetic to the methodology reviewer, but the editorial consequence is within my authority: revision instructions presuppose a known finding to revise toward, and here it is not established which finding that is. That is why my recommendation is rejection rather than major revision. The distinction matters practically — a major-revision letter would ask the authors to rescope claims around a result the manuscript does not unambiguously report.

Two further findings are each independently serious. First, §2's assertion that dashboards "reliably improve outcomes for lower-achieving students" is sourced to Ferro & Nakamura (2021), *"When dashboards demotivate: Peer comparison and the lower-achieving student"* — a citation apparently attached to the inverse of its source's thesis, and one that carries the paper's equity rationale. Combined with fifteen non-resolving `10.5555/` DOIs and eight references never cited in text, the citation base cannot be accepted as verified. Second, §3.2 states that students were not informed their dashboard activity would be analyzed, and the manuscript carries no ethics approval, no consent account for the log data, no linkage or de-identification procedure, and no data-availability statement. I cannot print a study on that record, and I particularly cannot print it alongside a conclusion urging the worldwide expansion of behavioural analytics deployment.

On contribution: the manuscript's own §2 observes that dashboard research already leans heavily on cross-sectional and correlational designs. Another such study warrants space only if it advances design, tests mechanism, or resolves heterogeneity. This one claims in §5 to address the debate about "who benefits from dashboards" while reporting no subgroup or moderation analysis, and its candidate novelty — the perceived-control link — rests on a single item administered to 87 of the 142 students. On the paper's own reported effect size, roughly 6% of variance, "dependable strategy" is not a characterization the evidence funds.

I want to be clear about what I am not saying. The topic is worth studying and the research question in §1 is one my readership wants answered. A defensible version of this work exists: a logistic model for the dichotomous retention outcome with prior-achievement and baseline-activity controls, a full-cohort rather than volunteer sample, a validated multi-item self-regulation instrument, an ethics record for the trace data, a specified dashboard interface, and a title and conclusion scoped to one course at one institution. That paper would be a reasonable submission to this journal. The path there runs through new analysis and, in the ethics case, through the authors' own institution — not through revision of this text. Should the underlying data reconcile all reported quantities and the ethics approval prove to exist and simply be undisclosed, the case for a major-revision route strengthens materially, and I would want the panel's decision letter to preserve that conditionality explicitly rather than foreclose it.

Under the contract, F1 fired at severity 90 on three mandatory `block` scores; F2 fired at severity 70 and is subordinate by precedence. The action attached to the highest-severity fired condition governs my seat's decision.

## Editorial Decision

F1 is the highest-severity fired condition (severity 90), and its action string governs. Within that action's range, my seat's recommendation is rejection, for the reason given above: the reported statistics do not reconstruct to a single dataset, so there is no established finding for a revision to be scoped toward, and the ethics gap is not addressable by revising the manuscript.

editorial_decision=reject_or_major_revision

---

## SEAT — Peer Reviewer 1 (Methodology)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** As Peer Reviewer 1, this is my primary charge: whether the study's design can actually answer the question it poses, and whether the reader is given enough to believe and re-run it. For a learning-analytics deployment study of dashboard engagement and course retention, that means the design type is named and matched to the causal or associational claim being made; the sampling frame (which cohort, which courses, which term, who was excluded) is specified; the outcome (retention) and the exposure (dashboard engagement) are operationally defined at a stated unit and time window; the analysis handles the observational structure of platform log data (students self-select into dashboard use, courses cluster students, engaged students differ systematically from non-engaged ones); statistical reporting meets APA 7.0 (effect sizes, CIs, assumption checks, missing-data handling, power); and reproducibility affordances exist (procedure detail, instrument descriptions, data/code availability, ethics/IRB record for student log data). At 2,487 words this is a short-format paper, so I will judge reporting completeness against what a short report can reasonably carry — but brevity excuses omitted *detail*, not omitted *safeguards*: a missing confounding-control strategy or a missing denominator is a rigor failure at any length, while a missing appendix-level table is a warn-level reporting gap.

**D2 — domain_accuracy (mandatory).** Read through the methodology lens, this dimension is about whether the paper's technical and domain-specific vocabulary is used correctly and whether reported results are internally accurate — not whether the literature review is complete (Reviewer 2's charge) or whether the framing travels to adjacent fields (Reviewer 3's). My scope here is narrow and method-adjacent: correct use of learning-analytics and measurement terminology (engagement metrics, dashboard exposure, "at-risk" flags, retention vs. persistence vs. completion vs. pass rate — these are distinct constructs in this literature and conflating them is a domain error, not a style quibble); correct use of statistical terminology (significance vs. effect magnitude, correlation vs. prediction vs. causation, reliability vs. validity); and arithmetic/reporting consistency between text, tables, and abstract. Where the paper characterises prior LA dashboard findings as a methodological premise for its own design, I check that the characterisation is technically defensible; I do not audit citation coverage.

**D3 — argumentative_coherence (mandatory).** Methodologically, this is the inferential chain: research question → design → data → results → conclusion, with nothing added at the end that the data cannot carry. In a dashboard-deployment study the canonical failure is a causal or quasi-causal conclusion ("the dashboard improved retention", "students should be given dashboards") resting on an observational association between voluntary dashboard use and staying enrolled — reverse causation (already-persisting students visit dashboards) and selection on unobservables (motivation, prior attainment) are the obvious rival explanations. I also check for internal contradiction between stated limitations and stated implications, ecological/level-of-analysis mismatch, and whether non-significant or unfavourable results are carried into the conclusion rather than dropped. This is coherence of *inference*, distinct from D1's coherence of *procedure*: a study can execute a defensible design and still over-claim in the discussion.

**D4 — cross_disciplinary_relevance (high priority, not mandatory).** From my seat, the methodological content of this dimension is whether the method is legible and portable to a reader outside student-facing learning analytics — an institutional-research analyst, a higher-education administrator, an HCI researcher. Concretely: are platform-specific metrics defined rather than assumed (what counts as a "dashboard view"; is engagement a count, a duration, a binary, a latent composite); is the deployment context specified sufficiently that a reader elsewhere can judge transferability (institution type, course modality, whether dashboard access was opt-in, universal, or instructor-mediated); and if the paper makes claims that reach into adjacent domains (behavioural nudges, self-regulated learning theory, student wellbeing, institutional retention policy), does the study design actually license those reaches. I score this on substantiation and definitional adequacy, not on writing style or on breadth of citation.

**D5 — writing_and_structure (normal priority).** My methodological interest here is confined to whether the exposition lets a reviewer verify the method at all: does a recognisable methods section exist and appear before results; are figures and tables self-contained and consistent with the text (Ns, denominators, units, axis labels, error representation); are results reported in a way that separates what was found from what it is taken to mean; does the manuscript follow the reporting conventions of an empirical LA venue. At 2,487 words a compressed or merged structure is normal and not per se a defect — I flag structure only where it actively obstructs methodological verification, and I do not score prose elegance, which is outside my seat.

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for` — An explicitly named design (observational/correlational, quasi-experimental, pre-post, RCT, mixed) and whether it matches the claim type; sampling frame and unit of analysis (student? student-course? session?); N with denominator and derivation (enrolled → eligible → analysed), attrition/exclusions accounted; operational definitions of "dashboard engagement" (metric, threshold, aggregation window) and "retention" (measured when, against what baseline); temporal ordering of exposure and outcome; identification/confounding strategy (covariate adjustment, matching, fixed effects, instrument, or an explicit disclaimer of causal intent); clustering of students within courses/instructors addressed or acknowledged; statistical reporting per Step 4a — effect sizes with interpretation, 95% CIs on key estimates, a priori power or a Type II discussion for null results, assumption tests (linearity/independence/multicollinearity/VIF; for a binary retention outcome, model-appropriate diagnostics), missing-data amount and handling (listwise/MI/FIML), APA 7.0 numeric formatting; reproducibility affordances — procedural detail sufficient to replicate, instrument/log-extraction description, data and analysis-code availability statement, IRB/ethics approval or an explicit exemption for institutional log data; red-flag scan for p-hacking, HARKing, uncorrected multiple comparisons, selective subgroup reporting.
- `what_triggers_block` — Any one of: (a) no identifiable design or analysis description, such that a reader cannot tell what was done; (b) the effect estimate is uninterpretable because the sample is undefined — no N, no denominator, or an N that cannot be reconciled across text/tables; (c) an association between self-selected dashboard use and retention is estimated with **no** confounding-control strategy **and no** explicit renunciation of causal claiming — i.e., selection bias is neither modelled nor disclaimed; (d) the primary outcome or the primary exposure is never operationally defined, so the reported relationship has no fixed referent; (e) an inferential claim rests on statistics that are absent, internally contradictory, or misapplied to the data type (e.g., a linear model reported for a binary outcome with no acknowledgement, or a significance claim with no test reported); (f) log data on identifiable students is analysed with no ethics/consent/exemption record and no de-identification statement.
- `what_triggers_warn` — Any one of: (a) design is identifiable but under-specified — named but with a key parameter (window, cohort, modality, opt-in status) left implicit; (b) effect sizes absent or reported without magnitude interpretation, or CIs missing on the headline estimates; (c) no a priori power analysis, or null results reported without Type II discussion; (d) assumption testing unreported (a length-plausible omission at 2,487 words, hence warn not block, provided a defensible model is named); (e) missing data acknowledged without quantity or handling method, or not mentioned where log data plainly produces it; (f) clustering/nesting acknowledged in prose but not handled in the model; (g) no data/code availability statement, or ethics stated only as a bare sentence with no approving body or protocol identifier; (h) multiple comparisons run without correction but with the exploratory status disclosed; (i) confounding is disclaimed in the limitations but the analysis still adjusts for nothing observable (partial disclosure — the block condition (c) requires *neither* control *nor* disclaimer).

### D2: domain_accuracy
- `what_to_look_for` — Whether retention/persistence/completion/pass-rate/withdrawal are used as the distinct constructs they are in the LA and higher-education literature, and whether the one measured is the one named throughout; whether engagement metrics are described with enough technical precision to be unambiguous (clicks vs. sessions vs. dwell time vs. distinct-days-active), and whether a composite is described as a composite; correct statistical vocabulary — "significant" not used to mean "large", "predicts" not used where only concurrent association is estimated, "reliability" not used where "validity" is meant, "control" not used for descriptive stratification; internal numeric consistency across abstract, text, tables, and figures (percentages summing, subgroup Ns summing to total, effect estimates matching between sections); whether methodological premises attributed to prior LA dashboard work are technically defensible characterisations (e.g., what prior deployments actually demonstrated about dashboard efficacy); correct handling of platform/vendor terminology where it carries a technical meaning.
- `what_triggers_block` — Any one of: (a) the headline construct is misidentified — the paper reports and discusses "retention" while measuring something materially different (e.g., final-week login activity, course pass rate, or single-assessment completion) without stating the substitution; (b) an irreconcilable numeric contradiction on a load-bearing result between abstract/text/table such that at least one reported value must be wrong and the correct one cannot be determined; (c) a statistical quantity is defined or interpreted incorrectly in a way that changes the reported finding (e.g., a p-value interpreted as effect magnitude or as the probability the hypothesis is false, an odds ratio read as a risk ratio in the conclusion); (d) a prior-work methodological premise that the design rests on is materially misstated in a way that invalidates the design rationale.
- `what_triggers_warn` — Any one of: (a) retention/persistence/completion used interchangeably in prose while the measured construct is defined correctly once — terminological looseness without measurement error; (b) engagement metric named in a colloquial way ("used the dashboard") with the precise operationalisation recoverable but stated only in passing; (c) minor numeric inconsistencies (rounding, decimal places, a percentage off by <1 point) that do not change any inference; (d) "predict"/"impact"/"drive" used loosely in non-conclusion sentences where the design supports only association (loose language in the conclusion escalates to D3); (e) domain terminology used correctly but without definition where a non-specialist could misread it (overlaps D4 — I will score it once, at its more serious location).

### D3: argumentative_coherence
- `what_to_look_for` — Whether the stated research question is the question the analysis answers; whether every conclusion sentence has a traceable line back to a reported result; whether causal language in the abstract, discussion, and implications is licensed by the design; whether reverse causation (persisting students visit dashboards, rather than dashboard visits producing persistence) is named and addressed; whether selection on unobservables (motivation, prior GPA, digital access) is acknowledged; whether the unit of analysis in the inference matches the unit in the data (ecological fallacy — course-level or cohort-level patterns used to claim individual student effects); whether subgroup results, if reported, are checked against the aggregate (Simpson's paradox); whether limitations stated in one section are contradicted by claims in another — particularly a "correlational, not causal" limitation coexisting with prescriptive recommendations; whether non-significant or contrary results survive into the discussion; whether the practical recommendation (deploy dashboards, mandate access, target at-risk students) is proportionate to the estimated effect.
- `what_triggers_block` — Any one of: (a) a causal claim or a direct policy prescription ("dashboards should be deployed to improve retention", "the dashboard increased retention by X") drawn from observational self-selected engagement data, with no identification strategy and no hedge — the central inference of the paper is unsupported; (b) an explicit self-contradiction on a load-bearing claim, e.g. the limitations concede no causal inference is possible while the abstract or conclusion asserts a causal effect; (c) the conclusion answers a different question than the one posed and analysed (bait-and-switch between RQ and claim); (d) results presented as confirming a hypothesis that the reported statistics do not support, or a null result reframed as support; (e) individual-level effect claims built entirely on aggregate-level (course or cohort) association with no acknowledgement of the level mismatch.
- `what_triggers_warn` — Any one of: (a) causal-adjacent verbs ("influenced", "led to", "drove") used in the discussion while the abstract and limitations correctly hedge — inconsistent register rather than a false claim; (b) reverse causation acknowledged in a single limitations sentence but never engaged with analytically or in the interpretation of the headline estimate; (c) practical implications outrun the effect magnitude (a small or imprecisely estimated effect converted into a confident deployment recommendation); (d) selection bias listed among limitations without stating its likely direction or magnitude; (e) a subgroup or moderator result highlighted in the discussion beyond what its precision supports; (f) generalisation to student populations, institution types, or platforms outside the studied deployment without a transferability argument; (g) non-significant results reported but not carried into the conclusion's overall framing.

### D4: cross_disciplinary_relevance
- `what_to_look_for` — Whether platform-specific and LA-specific constructs (dashboard, engagement metric, at-risk flag, LMS log, learning analytics intervention) are defined at first use for a reader from institutional research, HCI, or higher-education policy; whether the deployment context is specified enough to judge transferability — institution type and size, discipline(s), course modality (online/hybrid/in-person), class size, whether dashboard access was universal, opt-in, or instructor-mediated, and what else was running alongside it; whether the retention outcome is defined against an institutional definition a reader elsewhere could map onto their own (course-level vs. term-to-term vs. programme-level); whether claims that reach into adjacent disciplines — self-regulated learning theory, behavioural nudging, student wellbeing or equity, institutional retention policy, dashboard interface design — are substantiated by this study's design and data, or merely asserted; whether implications addressed to non-LA audiences (administrators, instructional designers, policy) are framed with the study's actual scope conditions attached.
- `what_triggers_block` — Any one of: (a) a substantive interdisciplinary claim is made as a headline contribution — e.g., that the dashboard operates through a named self-regulated-learning mechanism, or that it advances equity for a named student population — while the study measured neither the mechanism nor the population, and the claim is asserted rather than framed as conjecture; (b) the deployment context is so unspecified (no institution type, no modality, no access model, no course context) that no reader inside or outside the field can judge to what the finding applies, making the interdisciplinary implications unfalsifiable; (c) core operational constructs are used throughout with no definition anywhere, such that "engagement" and "retention" carry no fixed technical meaning for any reader. *(Note: D4 is `high` priority, not mandatory — a block here fires F3, not F1.)*
- `what_triggers_warn` — Any one of: (a) constructs defined but only in field-internal shorthand that an adjacent-field reader would have to reconstruct; (b) context partially specified — modality or access model stated, institution type or scale omitted; (c) implications addressed to administrators or policy audiences without scope conditions restated at the point of the recommendation; (d) an adjacent-field concept invoked as framing (nudge, self-regulation, engagement theory) without engaging what that field would require as evidence, but also without resting the paper's contribution on it; (e) retention defined only by local institutional convention with no bridge to a comparable external definition; (f) transferability discussed generically ("future work in other contexts") rather than by naming the scope conditions that would have to hold.

### D5: writing_and_structure
- `what_to_look_for` — Presence and placement of a methods section distinguishable from results and discussion; whether the sequence lets a reviewer trace question → method → result → interpretation without cross-hunting; whether figures and tables are self-contained (Ns, denominators, units, axis labels, what error bars or shaded bands represent, group definitions in the caption) and consistent with the text; whether results are stated separately from their interpretation; whether reporting follows empirical-venue conventions for an LA/EdTech outlet (structured abstract with method and N, statistics reported in-line per APA 7.0, tables numbered and called out); whether the compression demanded by ~2,487 words is achieved by trimming elaboration rather than by dropping method.
- `what_triggers_block` — Any one of: (a) no methods content is locatable anywhere in the manuscript — not merely brief but absent, so methodological verification is impossible (note this will normally co-fire D1 block (a)); (b) figures or tables carrying the headline result are unreadable or unlabelled to the point that the reported values cannot be checked against the text; (c) results and interpretation are so intermixed that what was measured cannot be separated from what is claimed about it.
- `what_triggers_warn` — Any one of: (a) methods present but scattered across sections rather than consolidated, requiring reconstruction; (b) a figure or table missing N, denominator, units, or an error-bar definition, while the value remains checkable from the text; (c) a table or figure never called out in the text, or called out with a mismatched number; (d) statistics reported in non-APA form (missing italics, wrong decimals, leading zeros, malformed p-values) without ambiguity of meaning; (e) the abstract omits method, N, or the headline estimate; (f) venue conventions partially unmet (no explicit limitations section, missing ethics/data-availability statement placement) where the content exists elsewhere; (g) organisational compression that costs elaboration but not verifiability — noted as a minor issue, warn only if it recurs across multiple method-bearing passages.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Methodology Review Report (Peer Reviewer 1)

contract_role: methodology

### Reviewer Identity

Quantitative methodologist in educational measurement (psychometrics and applied statistics), specializing in observational-data inference for dichotomous educational outcomes — logistic regression and propensity methods for non-randomized educational interventions — with published work on the statistical costs of dichotomizing continuous predictors. Reviews regularly for *Journal of Educational Psychology* and *Educational Researcher*. Standard practice: reconstruct every reported test statistic from the manuscript's own reported degrees of freedom and group descriptives before writing.

### Overall Recommendation

**Reject** — conditional in one specific sense: the reported statistics are mutually incompatible, so the manuscript is not revisable by editing. If the authors supply the analysis dataset and code and the numbers reconcile, a resubmission built on a re-specified design could be reconsidered as new work. Absent that data, no revision to the framing rescues it.

### Confidence Score

5

### Summary Assessment

The design is named honestly (observational, cross-sectional, single course, single term) and the operational definitions in §3.3 are specific enough to audit — which is precisely what made the audit possible and damaging. Four independent problems each independently prevent acceptance.

First, the reported statistics cannot be generated by any single dataset. Four sample sizes appear (142, ≥158 implied by *t*(156), 142 implied by *t*(140), 127 in Table 2); a *t* of 1.31 is reported with *p* = .008 when it corresponds to *p* ≈ .19 at either candidate *df*; and a mean of 3.847 is arithmetically unattainable from 87 integer responses. Second, the exposure is not landmarked: dashboard sessions accumulate over enrollment time, so students who withdrew before the final mechanically accrued fewer sessions. The headline association is partly definitional. Third, no confounding is controlled — not prior achievement, not total LMS activity, not motivation — while §5 and §6 assert that engagement *raises* retention. Fourth, §3.2 states students were not informed their behavioral data would be analyzed, and no ethics approval, de-identification, or data-availability statement appears anywhere.

The prose quality and the candid self-criticism in §2 and §3.3 should not be mistaken for methodological soundness. They are separable, and here they diverge sharply.

### Strengths

1. **Design type is named and its scope stated at the design level**: §3.1 declares an observational, cross-sectional design and closes with "all measures reflect a single term and no student was observed across multiple courses or terms." Naming the design correctly and pre-empting the multi-term reading is the right instinct, and it is the standard against which the Discussion's causal verbs should be judged.

2. **Operational definitions are specific and auditable**: §3.3 gives dashboard engagement as distinct sessions under a 30-minute inactivity rule, retention as a stated dichotomy (remained enrolled *and* completed the final assessment), and perceived control as a verbatim item on a stated 1–5 integer scale. This specificity is uncommon in dashboard research and is what allowed the numeric audit below. It should be preserved in any revision.

3. **Honest measurement self-criticism**: §2 concedes that click-based proxies "conflate very different kinds of activity," and §3.3 labels the median split "a coarse simplification of a continuous measure... adopted for interpretability rather than statistical efficiency." The authors see the measurement problem clearly; the defect is proceeding as though naming it neutralized it.

4. **Table 2 reports group *n*s, means, and SDs, permitting independent reconstruction**: from Table 2 alone I recover *t* = 1.308 — a reproducibility affordance most manuscripts do not provide. Extending this practice to every reported test (and to the perceived-control comparison, which reports no descriptives at all) would materially improve the paper.

5. **The exposure has one selection pathway closed by design**: the dashboard was universal from week 1 with no opt-in (§3.1), so access-based selection is genuinely ruled out. This is a real design merit, and it isolates the remaining selection problem to *use*, which is where the analysis must then work.

### Weaknesses

1. **The reported statistics cannot be reconstructed from any single dataset.** Six checks are set out under *Analysis Methods* below; four fail arithmetically. *Why this is a problem*: an inferential claim whose supporting statistics are internally contradictory has no determinable content — a reader cannot tell which reported value is the estimate. This is not a copy-editing matter, because at least one conflict (*p* = .008 at *t* = 1.31) is unattainable under either candidate *df*, and another (M = 3.847 from 87 integers) is unattainable under any dataset of the stated shape. *How to improve*: deposit the analysis dataset and analysis script, re-derive every number in the manuscript from that script, and report each test with its *n*, *df*, effect size, and 95% CI in a single table. Until that is done, no revision to wording changes the manuscript's evidential status.

2. **The exposure window is not landmarked, so the headline association is partly mechanical.** Dashboard sessions are counted "during the term" (§3.3) while retention is coded at the final assessment. A student who withdrew in week 8 had roughly half the opportunity to accumulate sessions of a student enrolled through week 15. *Why this is a problem*: exposure time is a function of the outcome, so a positive session-count/retention association is generated in part by the measurement definition itself, independent of any behavioral effect. This is reverse causation in its most mechanical form and is not addressed anywhere in §5.1. *How to improve*: fix the exposure to a pre-outcome landmark window in which all students were still enrolled (e.g., weeks 1–4, or up to the institutional withdrawal deadline) and re-estimate; or model person-time explicitly with a rate offset or a time-to-event specification with dashboard use as a time-varying covariate.

3. **No confounding is controlled, and the conclusion is causal.** The analysis contains no covariates at all — no prior achievement, no total LMS activity outside the dashboard, no demographics, no baseline course engagement. Dashboard sessions are a plausible proxy for general conscientiousness and overall platform activity. *Why this is a problem*: §5 opens with "dashboard engagement improved course retention... increasing dashboard engagement therefore raises the probability," and §6 states the relationship is "associated with, and raises" retention, followed by a prescription to institutions worldwide. My Phase 1 commitment permits either an identification strategy *or* an explicit renunciation of causal claiming; this manuscript supplies neither, and §5.1 omits confounding, self-selection, and design-based causal limits from its list of limitations while including four milder ones. *How to improve*: fit a logistic regression of retention on continuous dashboard engagement adjusting at minimum for prior achievement and non-dashboard LMS activity; report adjusted odds ratios with 95% CIs; state a sensitivity analysis (e-value or equivalent) for unmeasured confounding; and confine every claim to association.

4. **Sampling is self-contradictory and structurally conditioned on the outcome.** §3.2 states participants were "drawn from the course enrollment using a random sample," then describes a mid-term LMS announcement to which "students who chose to respond... formed the study sample." These are incompatible; the realized sample is a volunteer sample. *Why this is a problem*: recruitment occurred mid-term, so students who withdrew before the announcement could not enter the sample at all. The "not retained" stratum is therefore restricted to late withdrawals, the retention base rate is inflated, and the association can be manufactured by the recruitment window alone. The enrollment denominator ("several hundred students") is never stated as a number, so the coverage rate is unknown. *How to improve*: the retention analysis needs no survey — run it on the full-cohort log data with the enrollment denominator and an explicit CONSORT-style flow from enrolled → eligible → analysed; reserve the volunteer subsample for the perceived-control analyses only, and compare respondents to non-respondents on log-derived variables.

5. **The median split and the single-item measure jointly waste and misrepresent the data.** Splitting a right-skewed count at its median (§3.3) discards roughly 36% of the effective sample relative to the continuous predictor, produces a "high" group that is internally heterogeneous (Max = 48 against M = 14.6), and cannot be reconciled with Table 2's uneven 66/61 groups. Perceived control is a single item, so no reliability coefficient is estimable and no validity evidence is offered — yet it carries the entire self-regulated-learning mechanism story in §5. *Why this is a problem*: an unestimable construct cannot support a mechanistic interpretation, and dichotomization costs power the study cannot spare. *How to improve*: keep engagement continuous throughout (report the point-biserial or logistic estimate directly); replace the single item with a validated multi-item instrument (MSLQ or OSLQ subscale) and report α or ω with a CI. If only the single item is available, restrict it to a descriptive role and remove the mechanism claim from §5.

### Detailed Comments

#### Research Questions & Hypotheses

The question in §1 — "whether students who engage more with a learning analytics dashboard are more likely to persist in and complete their course" — is clear, answerable, and correctly associational in form. No hypotheses are formally stated and no directional predictions are pre-registered, which for an observational study is acceptable but means the three reported tests must be described as exploratory. They are not. The question the analysis answers is narrower than the question §6 answers: §1 asks about persistence in *this* course; §6 concludes about "retention across programs and disciplines" worldwide.

#### Research Design

Correctly identified as observational and cross-sectional. The design is appropriate for estimating an association and cannot support the causal claims made in §5 and §6. Two design-level gaps: (a) the exposure window is unbounded and terminates at the outcome (Weakness 2); (b) there is no comparison condition of any kind, so "dashboard engagement" is contrasted only against less dashboard engagement within the same universal deployment — which is the right contrast for an association study and the wrong one for the deployment recommendation in §6. Internal validity is low by construction; external validity is bounded to one introductory statistics course at one institution in one term. Course modality (online, hybrid, in-person) is never stated, which matters materially for interpreting dashboard access and for any transfer of the finding.

#### Sampling Strategy

The frame is undefined in numeric terms: "several hundred students" (§3.1) is not a denominator. N = 142 constitutes the analytic sample, 87 answered the perceived-control item (39% item-level missingness on the only survey measure), and Table 2 accounts for 127. No flow diagram, no non-response analysis, no exclusion counts. The "random sample"/volunteer contradiction in §3.2 must be resolved explicitly — as written, one of the two sentences is false. Survivorship operates twice: once through mid-term recruitment (early withdrawals structurally absent), and once in the exam comparison (see below), where the 15-student gap between 142 and 127 is most plausibly explained by non-retained students having no final exam score. If that reconstruction is correct, the exam comparison is conditioned on the outcome variable — a collider — and the entire retention association rests on approximately 15 non-retained cases. The authors must confirm or refute this; the manuscript as written asserts the opposite ("All 142 students in the primary analytic sample were classified into engagement groups for this comparison").

#### Data Collection

Log extraction is described at the level of a rule but not a system. The 30-minute sessionization rule is attributed to "the platform's default" without naming the platform or its version, so the measure is not reproducible elsewhere. The rule itself is ambiguous: a session is "a dashboard view preceded by at least thirty minutes of inactivity" — inactivity in the dashboard specifically, or across the LMS? These yield materially different session counts. The dashboard is described only by its three components (engagement metrics, assignment progress, peer-comparison band); the peer-comparison band's norm group, framing, and opt-out are unspecified, which is a reproducibility gap and not merely a design-description gap, because §2 identifies that exact feature as potentially demotivating. Final exam score appears in Table 1 and §4.3 but is never defined as a measure in §3.3 — no scoring scheme, no reliability, no administration detail.

#### Analysis Methods

Statistical analysis is described in three sentences (§3.4). Software is unnamed. No assumption testing of any kind is reported. Pearson *r* is applied to a right-skewed count against a dichotomous outcome: with one variable dichotomous this is arithmetically the point-biserial coefficient and should be named as such, and bivariate normality plainly fails. For a dichotomous retention outcome the defensible analysis is logistic regression; note also that with (on the reconstruction above) roughly 15 non-retained cases, events-per-variable constraints permit at most one or two covariates, which is itself a finding the authors need to confront rather than a reason to omit adjustment.

Arithmetic reconstruction of every reported statistic:

| # | Reported value | Location | Independent check | Verdict |
|---|---|---|---|---|
| 1 | *r* = .42 | Abstract | §4.2 reports *r* = .24 for the same association; *r* = .42 at *n* = 142 gives *p* < .001, not .004 | **Incompatible** |
| 2 | *r* = .24, *p* = .004, *n* = 142 | §4.2 | *t* = .24 × √140 / √(1 − .24²) = 2.93, *df* = 140 → *p* = .004 | Internally consistent |
| 3 | *t*(156) = 3.02, *p* = .003 | §4.3 | *p* is correct for *df* = 156, but *df* = 156 requires *n* = 158; only 87 students answered the item (max *df* = 85), and the full analytic sample gives *df* = 140 | **Impossible under any stated sample** |
| 4 | *t*(140) = 1.31, *p* = .008 | §4.3 | *t* = 1.31 corresponds to *p* ≈ .19 two-tailed at *df* = 140, and *p* ≈ .19 at *df* = 125 | **Unattainable at either *df*** |
| 5 | *n* = 66 + 61 = 127 | Table 2 | Pooled SD = 12.05, SE = 2.14, *t* = 2.8/2.14 = 1.308 at *df* = 125 — Table 2 reproduces the reported *t* exactly, at a *df* of 125 | Table 2 self-consistent; contradicts both "all 142" and *df* = 140 |
| 6 | M = 3.847, *n* = 87 integers | §4.1 / Table 1 | 3.847 × 87 = 334.69, not an integer; the nearest attainable means are 334/87 = 3.839 and 335/87 = 3.851 | **Arithmetically unattainable** |

Check 5 is the informative one: Table 2's descriptives reproduce the reported *t* to three decimals at *df* = 125, which suggests the analysis was in fact run on 127 students and that the *df* = 140 and the "all 142" sentence are wrong. But that reading does not rescue *p* = .008, which is unattainable at either *df*. At least two of the four values in §4.3's second paragraph must be incorrect, and the manuscript provides no basis for deciding which.

Two further statistical-reporting failures follow from the same passage. First, §4.3 narrates *p* = .008 as failing to "reach a comparable level" to *p* = .003 — at the stated α of .05, *p* = .008 is significant, so the sentence inverts the decision rule it declared in §3.4. Second, the exam comparison is treated as evidence of a weak effect when it is simply underpowered: *d* = 0.23 at 66/61 yields achieved power of roughly 25%, and 95% CIs of [−1.44, 7.04] on the mean difference and [−0.12, 0.58] on *d*. The correct statement is that the exam comparison is uninformative, not that it is weaker.

No effect sizes accompany either *t*-test. No confidence interval appears anywhere in the manuscript. For the headline correlation, *r* = .24 at *n* = 142 carries a 95% CI of approximately [.08, .39] — compatible with a negligible association — and *r*² = .058, roughly 6% of variance. No a priori power analysis is reported; three tests are run without correction and without exploratory framing. Missing data are handled by exclusion ("Respondents who skipped the item were excluded") with no quantity reported in the Methods, no mechanism examined, and no accounting for the 15-student gap in Table 2.

**Statistical reporting completeness: Unacceptable.** Effect sizes absent; CIs absent; power absent; assumption testing absent; missing-data reporting absent; APA numeric formatting inconsistent (three-decimal mean against two-decimal SD, correlations reported without *n* or *df* in the Abstract); and four of six reconstructable values fail arithmetic verification.

#### Results Presentation

Results are formally separated from interpretation, but interpretive sentences intrude into §4.2 ("The association was modest but statistically reliable") and §4.3 ("consistent with the interpretation that dashboard use and self-regulatory perception travel together"). Table 1 carries no *n* column, which matters because its three rows have different denominators (142 for sessions, 87 for perceived control, and — on the reconstruction above — 127 for final exam). Table 1's Min = 1 / Max = 5 for perceived control combined with SD = 0.62 is distributionally strained though not impossible; the impossible element is the mean itself. Table 2 carries no total and no test statistic. The perceived-control group comparison in §4.3 reports no group means, SDs, or *n*s at all, so it is the one test that cannot be reconstructed even in principle. Selective-reporting risk is moderate: only three tests are reported, the null exam result is included (a point in the paper's favor), but the reported *p* for it is wrong in the direction that makes it look like a near-miss rather than a null.

#### Reproducibility

Inadequate on every axis. No data availability statement. No analysis code. No named statistical software or version. No named LMS platform, so the sessionization rule cannot be reproduced. No interface specification for the dashboard. **No ethics or IRB record appears anywhere in the manuscript**, and §3.2 states affirmatively that "Students were not informed that their dashboard activity data would be analyzed for this study." Survey consent was obtained; behavioral trace consent was not, and the linkage of survey responses to individual LMS logs is described nowhere — no de-identification procedure, no pseudonymization, no data-handling statement. My Phase 1 scoring plan committed this pattern as a block-level trigger for D1 (reproducibility and ethics affordances), and I score it accordingly. The governance and secondary-use analysis belongs to Reviewer 3; the methodological point stands on its own: an analysis of identifiable student trace data with no approval record and no de-identification statement is not verifiable, and a journal cannot confirm the study was permitted to be conducted.

#### Methodological Fallacies Detected

- **Reverse causation** — present in mechanical form: exposure accumulates over enrollment time, which is determined by the outcome. Never raised in §5.1.
- **Survivorship bias** — twice: mid-term recruitment excludes early withdrawals from the sampling frame entirely; the exam comparison appears to condition on having sat the final, i.e., on retention.
- **Endogeneity / omitted variables** — no covariates whatsoever; prior achievement and total LMS activity are obvious common causes of both dashboard use and persistence, and neither is measured.
- **Confirmation bias in limitation selection** — §5.1 lists four real but non-disqualifying limitations (session proxy, self-report, single course, dashboard specificity) while omitting the correlational design's causal limits, self-selection, absence of confounding control, the median split, the single-item measure's unestimable reliability, and survivorship. A limitations section that excludes the disqualifying limitations performs rigor rather than exercising it.
- **Dichotomization artifact** — median split on a right-skewed count discards variance and power and produces groups that do not reconcile with the stated *N*.
- **Uncorrected multiple comparisons** — three tests, no correction, no exploratory declaration. Minor relative to the above, but unaddressed.

*Not detected*: ecological fallacy (the analysis and the inference are both at the student level), Simpson's paradox (no subgroup analyses are reported — which is itself a gap, since §2 raises the heterogeneity question the study never tests), and multicollinearity (no multivariable model exists to assess).

### Questions for Authors

1. Which correlation is the estimate — .42 (Abstract) or .24 (§4.2)? Please supply the analysis output. Note that *p* = .004 at *n* = 142 is consistent only with the latter.
2. §4.3 reports *t*(156) = 3.02 for the perceived-control comparison. With 87 students answering the item, the maximum available *df* for an independent-samples test is 85. How was *df* = 156 obtained, and what were the group *n*s, means, and SDs?
3. *t*(140) = 1.31 corresponds to *p* ≈ .19, and *t*(125) = 1.31 to the same. How was *p* = .008 obtained, and given α = .05, on what basis is a *p* of .008 described as failing to reach a level comparable to *p* = .003?
4. Table 2's group *n*s sum to 127, while §4.3 states that all 142 students were classified. Which 15 students are absent, and were they excluded because, not having been retained, they had no final exam score? If so, the exam comparison is conditioned on the outcome and this must be stated.
5. §4.1 reports a mean of 3.847 across 87 integer responses; 3.847 × 87 = 334.69. What is the actual sum of responses, and what is the actual *n*?
6. §3.2 describes both a "random sample of students enrolled in the course section" and a voluntary response to a mid-term announcement. Which describes the realized sample, and what was the enrollment denominator and the response rate?
7. Over what window were dashboard sessions counted for students who withdrew before the final assessment, and what steps were taken to prevent differential exposure time from generating the observed association?
8. Was ethics or IRB approval obtained for the analysis of behavioral trace data, and if so from which body under what protocol number? How were survey responses linked to individual LMS logs, and how were the linked data de-identified?
9. Will the analysis dataset and analysis code be made available? Which LMS platform supplied the default 30-minute sessionization rule, and does "inactivity" refer to dashboard views or to all LMS activity?
10. Was the final exam measure (Table 1, §4.3) defined and scored as described anywhere? It does not appear in §3.3.

### Minor Issues

- §3.4 states an alpha of .05 but no test in §4 is evaluated against it consistently (see Question 3).
- Three-decimal reporting for the perceived-control mean against two-decimal SD; APA 7.0 would give M = 3.85, SD = 0.62. The excess precision is not just a style issue — it is what made the impossibility detectable.
- Correlations in the Abstract are reported without *n*, *df*, *p*, or CI.
- §3.3's justification that "single-item overall ratings are common in dashboard studies to limit survey burden" describes prevalence, not validity; it should not stand as the measure's warrant.
- Table 1 and Table 2 both lack an *n* column and a note stating what each denominator is.
- §5.1 is titled "Limitations" but sits inside the Discussion with no separate ethics, data-availability, or conflict-of-interest statements anywhere in the manuscript.
- Integrity check: I found no instruction-injection attempt or reviewer-directed appeal in the manuscript text. Nothing in it was treated as directive.

---

## Dimension Scores

### D1: methodology_rigor
score: block

Four of my committed block triggers fire. **(b)** The sample is not reconcilable: 142 (§3.2, §4.3), ≥158 implied by *t*(156), 142 implied by *t*(140), and 127 in Table 2, with the enrollment denominator given only as "several hundred." **(c)** An association between self-selected dashboard use and retention is estimated with no confounding-control strategy of any kind *and* no renunciation of causal claiming — §5 and §6 assert that engagement raises retention. **(e)** Inferential claims rest on statistics that are internally contradictory and misapplied: *t*(140) = 1.31 with *p* = .008 is unattainable at either candidate *df*; *t*(156) is impossible given 87 item respondents; M = 3.847 is unattainable from 87 integer responses; and Pearson *r* is applied to a dichotomous outcome without naming the point-biserial case or fitting the model the data type requires. **(f)** Identifiable student log data are analysed with no ethics, consent, or exemption record and no de-identification statement, with §3.2 stating affirmatively that students were not informed. Additionally, the exposure window is not landmarked and terminates at the outcome, which makes the headline association partly definitional — a rigor failure independent of the arithmetic.

### D2: domain_accuracy
score: block

Two committed block triggers fire. **(b)** An irreconcilable numeric contradiction exists on load-bearing results: the headline correlation is .42 in the Abstract and .24 in §4.2, and §4.3's exam comparison reports a *df*, an *n*, and a *p* that cannot simultaneously hold (Table 2 reproduces the reported *t* at *df* = 125, contradicting both the stated *df* = 140 and the stated classification of all 142 students, while *p* = .008 is unattainable under either). At least two reported values must be wrong and the manuscript supplies no basis for determining which. **(c)** A statistical quantity is interpreted incorrectly in a way that changes the reported finding: at the declared α = .05, *p* = .008 is significant, yet §4.3 narrates it as failing to "reach a comparable level" to *p* = .003 — inverting the decision rule the manuscript itself adopted, and converting either a significant result into a reported null or a null into a misreported *p*. Terminology elsewhere (engagement operationalization, retention coding) is used with acceptable precision, which is why this scores on the numeric and inferential axis rather than the vocabulary axis.

### D3: argumentative_coherence
score: block

Two committed block triggers fire. **(a)** A causal claim and a direct policy prescription are drawn from observational, self-selected engagement data with no identification strategy and no hedge at the load-bearing positions: §5's opening sentence states that "dashboard engagement improved course retention" and that "increasing dashboard engagement therefore raises the probability that a student completes the course"; §6 states the relationship is "associated with, and raises" retention and advises institutions worldwide that dashboard investment "is a dependable strategy." **(b)** This self-contradicts load-bearing commitments made elsewhere in the same manuscript: §1 promises to "distinguish the pattern in the data from the causal story that might explain it," §2 cites a critical audit of exactly this failure (Ibarra, 2023) and states that "causal language frequently outruns the evidence," and §3.1 declares the design cross-sectional. The manuscript diagnoses the field-level error and then commits it. The mismatch compounds at the level of scope: the measured outcome is completion of one assessment in one course, while §6 concludes about "retention across programs and disciplines." §5.1's limitation list omits every limitation that would constrain these claims.

### D4: cross_disciplinary_relevance
score: warn

No block trigger fires. Core constructs are defined (engagement, retention, perceived control all carry operational definitions in §3.3), and the deployment context is partially specified — a 15-week undergraduate introductory statistics course, universal dashboard access with no opt-in from week 1, LMS-delivered — so an adjacent-field reader can locate the finding, which keeps trigger (b) and (c) from firing. The self-regulated-learning account in §5 is framed as consistency ("consistent with a self-regulated learning account") rather than asserted as a demonstrated mechanism, so trigger (a) does not fire on my committed reading. Four warn triggers do fire: **(b)** context is partially specified — course modality (online, hybrid, in-person) and institution type and scale are never stated, and the peer-comparison band's norm group, framing, and opt-out are unspecified, so no adjacent reader or adopting institution can judge transferability or replicate the exposure; **(c)** the §6 recommendation addresses institutions worldwide with no scope conditions restated at the point of recommendation; **(d)** SRL is invoked as the explanatory frame without engaging what that field would require as evidence — no SRL phase is operationalized and the single "in control" item is not a self-regulation measure; **(f)** transferability is discussed generically ("Future work should examine a wider range of dashboard designs and disciplinary contexts") rather than by naming the conditions that would have to hold.

### D5: writing_and_structure
score: warn

No block trigger fires: a methods section exists, precedes results, and is locatable; the tables are legible and the headline values are checkable against the text. Five warn triggers fire. **(b)** Table 1 has no *n* column despite its three rows carrying three different denominators (142, 87, and apparently 127), and Table 2 reports neither a total nor a test statistic; the perceived-control comparison in §4.3 reports no descriptives at all, making it the one result that cannot be reconstructed even in principle. **(c)** Table 2's group *n*s contradict the sentence that calls it out. **(d)** APA 7.0 numeric formatting is inconsistent — a three-decimal mean against a two-decimal SD, correlations reported in the Abstract without *n*, *df*, or CI. **(e)** The Abstract reports a headline estimate that differs from the one in Results. **(f)** Venue conventions are partially unmet: no ethics statement, no data-availability statement, no conflict-of-interest declaration anywhere in the manuscript, and the final exam measure appears in Table 1 and §4.3 without being defined in §3.3. These obstruct verification without preventing it, which is the warn/block boundary I committed to.

## Failure Condition Checks

### F1
fired: true

Predicate: any mandatory dimension scores `block`. D1 (methodology_rigor, mandatory), D2 (domain_accuracy, mandatory), and D3 (argumentative_coherence, mandatory) each score `block`. Severity 90 — the highest fired condition in my scores.

### F2
fired: true

Predicate: two or more mandatory dimensions score `warn` or worse. Three of the three mandatory dimensions (D1, D2, D3) score `block`, which is worse than `warn`. Severity 70 — fired but subordinate to F1 on severity precedence.

### F3
fired: false

Predicate: any high-priority dimension scores `block`. The sole high-priority dimension, D4 (cross_disciplinary_relevance), scores `warn`, not `block`. No committed D4 block trigger fired: constructs are operationally defined, deployment context is partially specified, and the SRL mechanism is framed as consistency rather than asserted as a headline interdisciplinary contribution.

### F0
fired: false

Predicate: every mandatory dimension scores `pass`. All three mandatory dimensions score `block`.

## Review Body

The manuscript is a single-course, single-term observational study whose design is named correctly and whose measures are defined specifically enough to audit. That specificity is what exposes the problem: the reported statistics cannot be produced by any one dataset. Four sample sizes appear across four locations (142, ≥158 implied by *t*(156), 142 implied by *t*(140), and 127 in Table 2); *t* = 1.31 is reported with *p* = .008 when it corresponds to *p* ≈ .19 at both candidate degrees of freedom; the Abstract's *r* = .42 conflicts with §4.2's *r* = .24, and only the latter is consistent with the reported *p* = .004 at *n* = 142; and a perceived-control mean of 3.847 is arithmetically unattainable from 87 integer responses on a 1–5 scale. Table 2's own descriptives reproduce the reported *t* to three decimals at *df* = 125, which suggests the analysis ran on 127 students and that the sentence claiming all 142 were classified is false — most plausibly because the 15 non-retained students had no final exam score, which would mean the exam comparison silently conditions on the outcome. The authors must confirm or refute this; on the face of the manuscript it is undisclosed.

Beneath the arithmetic sit three design failures that would matter even if every number reconciled. First, dashboard sessions are counted across the whole term while retention is determined at its end, so students who withdrew mechanically accrued less exposure — the headline association is partly definitional, and no landmark window, person-time offset, or time-to-event specification is used. Second, the analysis contains no covariates at all; dashboard use is a plausible proxy for prior achievement and general LMS activity, and neither is measured, while §5 and §6 conclude that engagement *raises* retention and prescribe institutional investment worldwide. My scoring plan permitted either an identification strategy or an explicit renunciation of causal claiming; this manuscript has neither, and §5.1's four listed limitations exclude confounding, self-selection, the causal limits of the design, the median split, the single item's unestimable reliability, and survivorship — a limitations section that performs rigor while omitting the disqualifying limitations. Third, §3.2 describes the sample as both random and volunteer; the realized sample is volunteer, recruited mid-term, so students who withdrew early could not enter the frame, and the enrollment denominator is never given as a number.

Reporting is inadequate on every APA 7.0 axis: no effect size for either *t*-test, no confidence interval anywhere (the headline *r* carries a 95% CI of roughly [.08, .39] and explains about 6% of variance), no power analysis, no assumption testing, no software named, and no missing-data accounting despite 39% item-level missingness on the only survey measure. The exam comparison is not a weak result but an uninformative one — achieved power of roughly 25% for the observed *d* = 0.23, with a mean-difference CI of [−1.44, 7.04] — and §4.3 compounds this by narrating *p* = .008 as weaker than *p* = .003 at a declared α of .05, inverting its own decision rule. Reproducibility affordances are absent: no data, no code, no named platform behind the 30-minute sessionization rule, no interface specification. No ethics or IRB record appears anywhere, and §3.2 states that students were not informed their dashboard activity would be analysed, with no de-identification or linkage procedure described — a block-level trigger under my Phase 1 commitment for D1, independent of the governance analysis that belongs to another seat.

The recommendation follows from the arithmetic, not from the framing. If only the causal language were at fault, this would be a revision. Because the reported analyses cannot be reconstructed from any single dataset, editing cannot fix it: the authors must supply the data and code, at which point what is warranted is a re-specified study — full-cohort logs, a landmarked exposure window, continuous engagement, logistic regression with prior-achievement and total-LMS-activity adjustment, a validated multi-item instrument, an ethics record, and a title and conclusion scoped to one course.

## Editorial Decision

Derived mechanically from the contract's `failure_conditions` precedence applied to my own dimension scores: F1 (severity 90) and F2 (severity 70) both fired; F1 carries the highest severity and its action governs.

editorial_decision=reject_or_major_revision

---

## SEAT — Peer Reviewer 2 (Domain)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** Read from the domain seat, this dimension asks whether the study's design, data handling, statistical reporting, and reproducibility affordances meet the bar that learning-analytics peer review actually applies. I am not the methodologist of record (that is Reviewer 1), so my paraphrase is deliberately narrower: my concern is where methodological choices carry *domain* consequences — whether the reported design is one the field recognizes as capable of supporting a retention claim, and whether the reporting completeness matches what learning-analytics venues expect of a single-institution dashboard deployment. Where I would need to assert what the field requires methodologically, that assertion is a field-norm claim and falls under the Step 5 grounding rule.

**D2 — domain_accuracy (mandatory).** This is my primary dimension. It asks whether the paper's claims align with current evidence in learning analytics and student-facing dashboards, whether prior work is represented as its authors actually argued it, and whether field-specific terminology and reported results are factually correct. For this field that means: correct use of the dashboard/learning-analytics vocabulary (engagement, dashboard access, self-regulated learning, at-risk prediction, retention versus persistence versus completion), correct attribution of the frameworks the field borrows, correct characterization of the known and contested findings about whether dashboard use helps, harms, or does nothing for different student groups, and coverage of the literature a domain reader would consider unmissable — both the foundational work and the last three to five years, including the null and adverse-effect results.

**D3 — argumentative_coherence (mandatory).** From the domain seat this asks whether the paper's central thesis holds together on the field's own terms: whether the theoretical framing it invokes is actually doing work in the argument or is named and abandoned, whether the chain from dashboard engagement to retention is argued at a strength the presented evidence licenses, and whether the conclusions the paper draws are the conclusions its stated framework and cited literature can support. Selection effects, reverse causation, and construct slippage between "engagement" and its logged proxy are the field-specific ways this argument typically breaks.

**D4 — cross_disciplinary_relevance (high).** Framing, definitions, and implications should be legible to adjacent-field readers, and any interdisciplinary claim should be substantiated rather than gestured at. Learning analytics is constitutively cross-disciplinary — it sits across education research, HCI, institutional research, and applied statistics — so my domain-seat reading is narrow by design: I assess whether the paper's borrowings from adjacent fields are accurate *as those fields state them*, and whether its terms are defined well enough that an education researcher and a data-science reader would not walk away with different meanings. Deep assessment of cross-disciplinary reach belongs to Reviewer 3; I check for domain misstatement, not breadth of appeal.

**D5 — writing_and_structure (normal).** Organisation, clarity of exposition, figure and table quality, and adherence to venue conventions. My angle here is domain-inflected rather than stylistic: whether the manuscript's structure lets a domain reader locate the intervention description, the outcome definition, and the evidentiary basis for each claim; whether tables and figures report what the field expects to see reported; and whether definitional and citational apparatus is complete enough to audit. At 2,487 words this is a short-form submission, so brevity itself is not a defect — but compression that removes the material a domain reader needs to verify a claim is.

## Scoring Plan

### D1: methodology_rigor

- `what_to_look_for` — Whether the design is stated with enough specificity to name it (observational cohort, quasi-experiment, RCT, pre-post); whether the retention outcome is operationally defined (which term, which census point, which denominator, withdrawal versus non-re-enrolment); whether "dashboard engagement" is defined as a measured quantity (logins, sessions, dwell time, unique days) rather than left as a construct word; whether the analytic sample, exclusions, and attrition are reported; whether covariates plausibly related to both dashboard use and retention (prior attainment, entry qualifications, financial aid status, first-generation status, course load) are handled at all; whether effect sizes and uncertainty accompany any significance claim; whether reproducibility affordances (analysis code, variable dictionary, model specification, data-availability statement) are described, and if withheld, whether the stated reason is one that institutional student-records governance actually supports. Where the deployment is a single-institution course-level rollout, I check whether clustering (by course, section, instructor) is acknowledged.
- `what_triggers_block` — Any of: (a) the retention outcome is never operationally defined, so the headline claim cannot be checked against any measurable quantity; (b) the engagement measure is never operationally defined, leaving the exposure variable unspecified; (c) a causal or intervention-effect claim about retention is made from a design that contains no comparison condition and no adjustment for selection into dashboard use, with no acknowledgement that this is what was done; (d) reported statistics are internally impossible (denominators that do not reconcile, percentages inconsistent with the stated N, a reported test that cannot be produced by the stated design). For (c) I score `block` on the *unacknowledged inferential leap*, which is a discipline-neutral defect, not on the absence of a randomized design — a non-randomized dashboard study is normal and accepted practice in this field.
- `what_triggers_warn` — Any of: (a) the design is identifiable and the outcome defined, but key confounders are neither adjusted for nor discussed; (b) significance is reported without effect sizes or intervals; (c) the analytic sample is reported but exclusions/attrition are not, so the denominator's provenance is unclear; (d) course/section clustering is present by construction and unaddressed; (e) no data-availability or reproducibility statement, and no reason given. On (e) I record the observation but will down-rate the *severity* to advisory and tag it `[FIELD-NORM UNVERIFIED]` unless I can ground the expectation in a checkable source — the target venue's data policy, a learning-analytics community data-sharing statement, or a documented convention — because student-records data legitimately carries release restrictions and a generic open-science expectation is exactly the miscalibration Step 5 forbids. A `warn` on D1 from me will rest on (a)-(d), not on (e) alone.

### D2: domain_accuracy

- `what_to_look_for` — Whether cited work is represented as its authors actually argued it, including cases where the paper's framing depends on a prior study having found something it did not; whether the literature base covers both the foundational dashboard/learning-analytics work and the last three to five years; whether the well-documented heterogeneity in this field is acknowledged — that dashboard effects are known to vary by student prior attainment and self-regulatory capacity, and that comparative/social-reference dashboard designs have documented adverse effects on some students; whether null and negative findings appear at all or the review is built exclusively from positive results; whether the terminology is used to the field's conventions — retention versus persistence versus completion versus progression are not interchangeable, engagement versus access versus use are not interchangeable, and "at-risk" carries a specific predictive-modelling meaning; whether the theoretical framework named (self-regulated learning, Tinto-lineage integration/departure models, feedback-intervention theory, or another) is defined accurately and matches how its originators specified it; whether secondhand citation is used where an original source is required; whether the described dashboard is characterized precisely enough (what it displayed, to whom, when, with what comparison referent) for a domain reader to know which dashboard genre is under study.
- `what_triggers_block` — Any of: (a) a factual misstatement about what a cited work found or claimed, where the paper's own argument leans on the misstatement; (b) a named theoretical framework whose core construct is defined incorrectly — for instance, presenting self-regulated learning as equivalent to observed platform activity, or attributing a claim to a framework that the framework does not make; (c) systematic misuse of a load-bearing field term such that the paper's headline claim changes meaning depending on the reading — most concretely, a "retention" claim whose evidence is actually about within-term persistence, course completion, or next-term enrolment, used interchangeably; (d) the literature review presents dashboard efficacy as a settled positive finding, with the field's documented null and adverse-effect results absent, in a paper whose contribution claim depends on that settled framing.
- `what_triggers_warn` — Any of: (a) coverage is thin in a way that omits recognizable recent developments but nothing load-bearing is misrepresented; (b) the theoretical framework is named and broadly correct but applied superficially — invoked in the framing and never used to guide the analysis or interpretation; (c) terminology is imprecise in places without changing what the central claim means; (d) the literature is skewed to one region, one platform ecosystem, or one school of thought without the paper acknowledging the boundary; (e) opposing findings are cited but only in a limitations sentence rather than engaged; (f) secondhand citation where an original source was reachable. Where a coverage complaint would require me to assert what this field *must* cite, I ground that expectation in checkable evidence (an actual citation I can attest, or a documented community/venue expectation) or I state the gap without asserting severity and tag it `[FIELD-NORM UNVERIFIED]`. I hold the field's genuine constraints in view: at 2,487 words this is a short paper, and short-format venues in this field legitimately carry compressed literature sections — thinness alone is a `warn` candidate only when what is missing is load-bearing for the paper's own claim, and a single-institution deployment study is a recognized and valued genre here, not a defect.

### D3: argumentative_coherence

- `what_to_look_for` — Whether the causal strength of the language tracks the evidence: whether "associated with", "predicts", "leads to", "improves", and "increases retention" are used deliberately or drift across abstract, results, and discussion; whether the abstract's claim and the discussion's claim are the same claim; whether the paper confronts the central alternative explanation in this literature — that students who are already persisting are the students who log in, so engagement is a marker of the outcome rather than a cause of it; whether reverse causation and selection into dashboard use are named; whether the framework invoked in the introduction reappears in the interpretation, or is dropped; whether the practical or policy recommendation that closes the paper is licensed by the evidence actually presented; whether stated limitations are honoured in the conclusions rather than contradicted by them; whether the construct chain (dashboard engagement → self-regulatory behaviour change → retention) has its middle term evidenced or silently assumed.
- `what_triggers_block` — Any of: (a) an internal contradiction where the discussion or abstract asserts a causal/effectiveness claim that the results section's own framing disavows, or where a stated limitation is directly contradicted by a conclusion; (b) the central inference rests on a leap with no supporting step and no acknowledgement — most specifically, treating the engagement–retention association as demonstrated causation with the selection explanation neither tested nor mentioned anywhere in the manuscript; (c) the conclusion recommends an institutional action (mandate the dashboard, target students by engagement score) whose justification requires a causal claim the paper elsewhere declines to make; (d) the framework's own predictions and the reported findings conflict, and the paper does not register the conflict.
- `what_triggers_warn` — Any of: (a) selection and reverse causation are named in limitations but never engaged in the interpretation, so the discussion proceeds as if they were resolved; (b) causal language appears in the abstract or conclusion while the body stays correlational — inconsistent hedging rather than a single sustained overclaim; (c) the mediating construct is assumed rather than evidenced, but the paper is explicit that it is proposing rather than demonstrating the mechanism; (d) the framework is coherent with the argument but does not do interpretive work, leaving the findings under-explained rather than misexplained; (e) practical implications outrun the evidence in tone but are phrased conditionally.

### D4: cross_disciplinary_relevance

- `what_to_look_for` — Whether constructs borrowed from adjacent fields are stated as those fields state them: self-regulated learning and motivation constructs from educational psychology, retention/departure models from higher-education research, feedback and information-display principles from HCI, and any predictive-modelling vocabulary from applied statistics; whether the dashboard's design rationale is connected to any established interface or feedback principle or asserted bare; whether terms with different meanings across the contributing fields — engagement, feedback, model, significance, intervention — are disambiguated where the paper relies on them; whether implications are stated so an institutional-research reader, an instructor, and a platform designer can each tell what the finding means for them; whether the paper's own boundary conditions (one institution, one course context, one dashboard design, one student population) are stated so readers outside the immediate subfield do not over-transfer the result.
- `what_triggers_block` — Any of: (a) a claim attributed to an adjacent discipline that misstates that discipline's position in a way the paper's framing depends on — for example, presenting a contested higher-education retention model as settled consensus, or invoking a statistical/predictive concept incorrectly in a load-bearing way; (b) a load-bearing term left so undefined that its adjacent-field readings give materially different meanings to the paper's headline claim, with no definition available anywhere in the manuscript; (c) an interdisciplinary claim (that the finding transfers to other institutions, platforms, or student populations) asserted flatly with no supporting evidence and no boundary statement. I will not score `block` here for a paper that is simply written for its home subfield — narrow framing is a `warn`-class issue at most, not a defect.
- `what_triggers_warn` — Any of: (a) adjacent-field concepts are accurate but used as labels without enough definition for an outside reader to follow the argument; (b) implications are written for one audience only, leaving the other stakeholder groups the paper names unaddressed; (c) contextual specificity (institution type, student population, course discipline, dashboard genre) is under-described, so transferability cannot be judged even though no over-transfer is claimed; (d) generalizability is discussed but only as a limitations formality, without saying what would or would not travel; (e) an adjacent-field term is used in a sense that conflicts with that field's convention, without changing the paper's central claim.

### D5: writing_and_structure

- `what_to_look_for` — Whether the manuscript's sections let a domain reader locate, in order, what the dashboard was, who saw it and when, what was measured, what was found, and on what basis; whether the intervention description is complete enough for another institution to recognize the same system; whether tables and figures report Ns, denominators, units, time windows, and uncertainty, and whether captions state what the display shows rather than what the authors conclude from it; whether figures are interpretable without the body text; whether every claim that needs a citation has one and every citation resolves to a reference-list entry; whether abstract, results, and conclusion are numerically consistent with each other; whether venue conventions apparent from the manuscript (structured abstract, reporting order, ethics/consent statement, section requirements) are followed; whether the 2,487-word length is used on the paper's own contribution or spent on generic background.
- `what_triggers_block` — Any of: (a) the manuscript is disorganized or incomplete to the point that a core element — what the dashboard did, what the outcome was, or what result is claimed — cannot be located at all; (b) numbers stated in the abstract, results, and tables contradict each other, so the reader cannot tell which is the finding; (c) citations are systematically broken — in-text citations with no matching reference entries, or a reference list that does not correspond to the text — such that the evidentiary base cannot be audited; (d) figures or tables are cited in support of a claim they do not contain.
- `what_triggers_warn` — Any of: (a) the structure is followable but the intervention description is too thin to identify the dashboard genre; (b) tables or figures omit Ns, denominators, or uncertainty, or captions editorialize the finding rather than describe the display; (c) individual citation or formatting errors that do not compromise auditability; (d) disproportionate space on generic background relative to the study's own contribution, in a short-format paper where that space is the binding constraint; (e) an ethics/consent or data-governance statement is absent where the manuscript's own description implies individual-level student-records data was used — reported as an observation, with the severity grounded in the venue's or the field's documented requirement, or tagged `[FIELD-NORM UNVERIFIED]` and left advisory if I cannot ground it.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Domain Review Report (Peer Reviewer 2)

### Reviewer Identity

Senior higher education researcher specializing in undergraduate persistence and retention theory, with a decade of work on gateway-course attrition and institutional early-alert systems; publishes critical syntheses of learning analytics' engagement with retention theory. Reads reference lists adversarially — checks whether each cited source actually says what the citing sentence claims.

### Overall Recommendation

Reject

### Confidence Score

4

### Summary Assessment

This manuscript is well written and its Literature Review displays genuine field awareness — it names the demotivation risk, the goal-orientation moderation, the click-proxy measurement problem, and the field's causal-language overreach. That awareness makes what follows harder to excuse rather than easier, because the paper commits each of the errors it catalogues.

Three domain findings are disqualifying in their current form. First, a load-bearing citation in §2 is attached to a claim that inverts the thesis stated in the manuscript's own reference-list title, and adds a certainty ("reliably") that the surrounding paragraph denies. Second, "retention" is operationalized in §3.3 as completing one final assessment in one course in one term, then generalized in §6 to retention "across programs and disciplines" for institutions "worldwide" — a construct-validity failure compounded by an external-validity failure. Third, self-regulated learning is named as the explanatory mechanism throughout while the Abstract's claim that SRL behavior was measured is falsified by §3.3, where the only self-report instrument is a single perceived-control item.

Separately, the outcome variable appears in no table and its base rate is never reported, and 9 of 15 listed references are never cited in text. The contribution the paper claims to the "who benefits" debate is not supported by anything it reports.

### Strengths

1. **Genuinely balanced literature review (§2)**: This is the manuscript's strongest section. It does not present dashboard efficacy as settled — it foregrounds discouragement effects of relative-standing feedback (Osei, 2020), the dependence of effect direction on framing and goal orientation, the inadequacy of click-based proxies (Vandermeer, 2023), and a critical audit of causal language in correlational learning analytics (Ibarra, 2023). Many manuscripts in this genre cite only confirming results; this one does not.

2. **Operational transparency on the exposure and outcome measures (§3.3)**: Dashboard engagement is defined as distinct sessions under a stated 30-minute sessionization rule, and retention is given a coded definition rather than left as a construct word. The median split is explicitly labelled "a coarse simplification" adopted "for interpretability rather than statistical efficiency" — the authors name the cost rather than hiding it.

3. **A recognized and valuable genre**: A single-institution, single-course deployment study is not a defect in this field. Contextually bounded institutional studies carry real value, and the paper's research question — do students who engage more with a dashboard persist more — is a legitimate and unresolved one.

4. **The manuscript contains, in §5's third paragraph, the reading its own data support**: "the modest size of the engagement-retention association counsels against overstatement... dashboards help at the margin, nudging some students toward completion without transforming the underlying determinants of academic success." That paragraph is calibrated correctly. The problem is that §5's opening sentence and §6 contradict it.

### Weaknesses

1. **W1 — A load-bearing citation is attached to a claim that inverts its own listed source.** §2 states: "Dashboards have been shown to reliably improve outcomes for lower-achieving students, who are said to gain the most from externalized progress cues (Ferro & Nakamura, 2021)." The manuscript's own reference list gives that source as *"When dashboards demotivate: Peer comparison and the lower-achieving student"* (p. 112). A source whose title identifies lower-achieving students as the ones dashboards demotivate cannot support a claim that they reliably benefit most. The word "reliably" also contradicts the same paragraph's framing and §2's opening concession that findings are "far from uniform." This is not decorative: the manuscript says this position "underpins much of the equity-oriented rationale for institutional dashboard deployment, and we return to it in the Discussion," and §5's "who benefits" paragraph depends on it. *Direction of improvement*: verify the source, restate what it actually found, and rebuild the equity rationale on whatever the evidence supports — most likely a heterogeneity claim rather than a uniform-benefit claim. *Severity grounding*: this rests on an inconsistency internal to the manuscript (citing sentence vs. its own reference-list title), not on any external field norm.

2. **W2 — The retention construct will not carry the weight the Conclusion puts on it.** §3.3 defines retention as "whether the student remained enrolled and completed the final assessment" — one course, one term, one time point. §6 concludes that dashboards are "a dependable strategy for improving retention across programs and disciplines" for "higher education institutions worldwide." Nothing in the design observes a second course, a second term, a second institution, or program-level or institution-level outcomes; §3.1 states plainly that "no student was observed across multiple courses or terms." The Abstract compounds the drift by calling the same variable "course persistence," so three terms (retention / persistence / completion) circulate for one measured quantity. *Direction of improvement*: retitle and rescope to course completion, confine every implication to the observed setting, and state explicitly what the study does not license. *Severity grounding*: the over-transfer is established internally — the evidence does not cover the units §6 generalizes to. The further claim that course completion and institutional retention are separately theorized constructs with different determinants in higher-education persistence research is a field-norm claim I cannot ground in session materials `[FIELD-NORM UNVERIFIED]`.

3. **W3 — Self-regulated learning is ornamentation, and the Abstract misstates what was measured.** The Abstract states "we measured dashboard engagement, self-regulated learning behavior, and course persistence." §3.3 contains no SRL measure. The only self-report instrument is one item, "Overall, I feel in control of my learning in this course." §1 defines SRL as a cycle of forethought, performance, and reflection; §2 cites Rutledge and Berange (2022) for the boundary condition that dashboards support these phases "only when learners possess the regulatory strategies to act on what they see." Neither the phases nor the regulatory strategies are operationalized, so the framework's own stated boundary condition is named and then abandoned, and §5's inference that perceived control indexes a self-regulatory mechanism is construct substitution. *Direction of improvement*: either use a validated instrument and test the mediation, or remove SRL from the Abstract and recast §5's mechanism paragraph as a hypothesis the study does not test. *Severity grounding*: the mismatch between the Abstract's measurement claim and §3.3, and between §2's stated boundary condition and the analysis, is internal to the manuscript. The additional expectation that SRL claims require a validated multi-item instrument is a field-norm claim I cannot ground here `[FIELD-NORM UNVERIFIED]`.

4. **W4 — The paper diagnoses causal overreach in §2 and then performs it, with a Limitations section that omits every limitation that would constrain the conclusions.** §1 promises to "distinguish the pattern in the data from the causal story that might explain it." §4.2 reports an association. §5 opens: "dashboard engagement improved course retention... increasing dashboard engagement therefore raises the probability that a student completes the course." §6: "associated with, and raises, course retention." Selection into dashboard use and reverse causation are named nowhere in the manuscript. This is the field's best-documented alternative explanation for exactly this association — that students who are persisting are the students who log in — and §5.1's four limitations (session-count proxy, self-report bias, single course, dashboard specificity) do not include it, nor the correlational design's inferential limits, nor the volunteer sample. The recruitment design makes this acute in a way the manuscript never registers: §3.2 describes a mid-term LMS announcement to which "students who chose to respond" formed the sample. Students who had already withdrawn could not respond, so the analytic sample is conditioned on partial persistence before the outcome is measured. §3.2 also calls this "a random sample of students enrolled in the course section," which is incompatible with the volunteer recruitment it then describes. *Direction of improvement*: remove every causal verb, add selection and reverse causation to the Limitations as first-order threats, and reconcile the sampling description. *Severity grounding*: internal — the manuscript's stated epistemic commitment (§1), its cited critique of this exact error (§2), and its Discussion and Conclusion are mutually inconsistent.

5. **W5 — The reference base cannot be audited.** Six of fifteen listed references are cited in text (Calloway 2019; Ferro & Nakamura 2021; Osei 2020; Rutledge & Berange 2022; Vandermeer 2023; Ibarra 2023). Nine appear only in the list: Ainsworth & Devi (2018), Berange (2021), Delacroix & Ohno (2022), Halloran (2020), Kessler & Amadou (2019), Montez (2022), Prakash & Tolliver (2021), Solberg & Whitfield (2018), Wexler & Ojo (2020). Several of the uncited nine are precisely the sources the argument needed: §1's uncited assertion that the first-year gateway course is a point of elevated risk sits beside an uncited *"Retention in the gateway course: A review of intervention studies"*; §2's goal-orientation claim is routed to Osei (2020) rather than to the uncited *"Goal orientation and dashboard response in introductory courses"*; and a listed *"Retention modeling with LMS trace data: A cautionary study"* is never engaged in a paper that models retention from LMS trace data. Separately, all fifteen entries carry DOIs under a single identical `10.5555/` prefix despite spanning six differently-named journals. *Direction of improvement*: cite what is listed or remove it, and supply resolvable identifiers. *Severity grounding*: the uncited-list proportion (9/15) is checkable in the manuscript. The inference that a shared `10.5555/` prefix across six distinct journals indicates placeholder or non-registered identifiers rests on DOI-registry practice I cannot verify from session materials `[FIELD-NORM UNVERIFIED]` — I report it as an observation warranting editorial verification rather than asserting its severity.

### Detailed Comments

#### Literature Review

- **Coverage**: For a short paper the coverage is respectable in kind — reflective-prompt framing, demotivation, goal-orientation moderation, measurement critique, and causal-language critique are all present. The gap is not breadth but the absence of any engagement with higher-education persistence scholarship. The paper opens on undergraduate attrition and gateway-course risk (§1) and closes on institution-wide retention strategy (§6), yet no retention theory, model, or intervention literature is cited anywhere. The retention half of a retention paper has no literature.
- **Integration quality**: §2 is a genuine synthesis, not an enumeration — it moves from optimism to heterogeneity to measurement to method critique with an argumentative through-line. This is above the norm for the format.
- **Research gap argument**: The gap is stated persuasively ("more enthusiasm than evidence," "adoption metrics or student satisfaction rather than downstream academic outcomes"), but the study does not fill it. §2 concedes that "much dashboard research relies on cross-sectional or correlational designs" and cites an audit of causal overreach; §3.1 then reports a cross-sectional correlational design and §5 delivers the overreach. The gap the paper identifies is one it reproduces rather than closes.

#### Theoretical Framework

- **Appropriateness**: SRL is a defensible framework for a dashboard study, and §1's three-phase description is a fair statement of the cyclical model. The choice is not the problem.
- **Application depth**: Superficial. The framework guides neither the design (no SRL instrument, no phase operationalized), nor the analysis (no mediation test, no subgroup analysis), nor the interpretation beyond an assertion of consistency. §5's claim that the perceived-control result is "consistent with a self-regulated learning account" is unfalsifiable as stated: the result is equally consistent with perceived control being a correlate of general conscientiousness, prior attainment, or the survivorship of the volunteer sample. The conclusions do not feed back to theory in any form — no extension, no revision, no challenge.
- **Alternative frameworks**: If the paper wants to speak to retention, a persistence or departure framework would connect the outcome to the literature it invokes in §1 and §6. If it wants to keep SRL, it needs a measure. It cannot claim both while measuring neither. The manuscript also never discusses the limits of SRL's applicability in this context, which §2's own citation of the "only when learners possess the regulatory strategies" boundary condition invites.

#### Academic Argument Quality

- **Factual accuracy**: The W1 citation inversion is the most serious instance. Two lesser ones: §2 attaches a goal-orientation moderation claim to a source whose listed title is about discouragement effects, while a goal-orientation source sits uncited in the list; and §1's gateway-course framing is asserted without citation and is not established for this setting — §3.1 describes a required quantitative-reasoning course serving "a range of majors" and never states it is a first-year course.
- **Argument logic**: One contradiction is fully derivable from domain reasoning without recomputing any statistic. §4.3 states "All 142 students in the primary analytic sample were classified into engagement groups for this comparison," and the comparison is on final exam score. But §3.3 codes as not retained any student who "withdrew before the final assessment, or who was enrolled but did not sit the final." Non-retained students therefore have no final exam score, so they cannot be in an exam comparison. Table 2's groups sum to 127, not 142. Either the 15-student difference is the non-retained group — in which case the text's "All 142" is false and the retention base rate is approximately 89% — or the retention variable has no variance and §4.2's correlation could not have been computed. The manuscript forces this inference and never states it. Relatedly, in a paper about retention, retention appears in no table and its base rate is never reported anywhere. That base rate is decisive for interpreting the association: an r of .24 on a dichotomy where roughly one student in nine is not retained rests on very few discordant cases, and a domain reader cannot assess it without the number.
- **Terminology precision**: Retention / persistence / completion are used interchangeably across the title, Abstract, and §3.3 for one measured quantity (see W2). "Engagement" slides between the theoretical construct in §1–§2 and its logged proxy in §3.3, despite §2 explicitly warning against exactly that conflation via Vandermeer (2023) — the manuscript names the trap and then walks into it. Perceived control is reported to three decimals (3.847) for a 1–5 integer item, a precision the measure does not carry; the distributional question this raises belongs to Reviewer 1.

#### Contribution to the Field

- **Incremental contribution**: Presently thin. As an association study in one course, the finding that dashboard sessions and course completion covary at r ≈ .24 adds a data point to a literature the paper itself characterizes as already saturated with cross-sectional correlational work. The perceived-control component is the only element with novelty potential, and it rests on a single unvalidated item.
- **Positioning**: §5 claims the results "speak to an ongoing debate in the literature about who benefits from dashboards." They cannot. Answering that question requires moderation or subgroup analysis by prior achievement or goal orientation — the very moderators §2 identifies. The paper reports one pooled association and one median-split group comparison, neither stratified. It raises a debate it has no instrument to enter.
- **Overclaiming**: High and structural rather than incidental. The overclaim appears at the Discussion's opening sentence and the Conclusion's opening sentence — the two most load-bearing positions in the manuscript — and is accompanied by prescriptive advice to institutions ("investing in student-facing dashboards and encouraging students to engage with them is a dependable strategy"). "Dependable" is not supportable from a modest association in one course, and the recommendation treats engagement as a manipulable lever when the study only observed it as a behavior. No reading recovers this as careless phrasing.

#### Missing Key References

**No-invention note**: the manuscript's reference list is not verifiable from session materials (no resolvable identifiers), and I can attest no external reference from this session. Everything below is a tagged search lead, not a citation, and carries no author/year/venue metadata I have not read in the manuscript itself.

- Two sources already in the author's own list are the ones the argument needed and did not use: the listed gateway-course retention-intervention review (Halloran, 2020, p. 114) belongs at §1's uncited gateway-risk sentence, and the listed cautionary study on retention modeling with LMS trace data (Wexler & Ojo, 2020, p. 132) belongs in §3.4 or §5.1, where its cautions go unaddressed. I can attest these appear in the manuscript's list; I cannot attest they exist.
- `[UNVERIFIED]` Higher-education persistence and departure theory — the interactionalist departure tradition and its critiques — to ground the §1 attrition framing and to make explicit why institutional retention is not what §3.3 measures. Search lead only.
- `[UNVERIFIED]` Systematic reviews or meta-analyses of student-facing learning analytics dashboards with academic-outcome (not adoption or satisfaction) endpoints, to position the marginal contribution of another correlational study. Search lead only.
- `[UNVERIFIED]` Empirical work on heterogeneous and conditional dashboard effects by prior achievement and goal orientation, which the paper's §5 "who benefits" claim requires and does not have. The listed-but-uncited goal-orientation entry (Berange, 2021, p. 106) may be this literature; verify before citing.

### Questions for Authors

1. Ferro and Nakamura (2021) is listed as *"When dashboards demotivate: Peer comparison and the lower-achieving student."* What in that source supports the §2 claim that dashboards "reliably improve outcomes for lower-achieving students," and what supports "reliably"? If the source in fact reports demotivation, how does the equity rationale in §2 and §5 survive its correction?
2. What proportion of the 142 students were retained under the §3.3 coding? Please report the base rate and add retention to Table 1.
3. §4.3 states that all 142 students were classified into engagement groups for the final-exam comparison, but non-retained students by definition did not sit the final and Table 2 sums to 127. Which 15 students are absent from Table 2, and on what variable were they lost?
4. The Abstract states that self-regulated learning behavior was measured. Which instrument in §3.3 measures it? If the answer is the single perceived-control item, on what basis is that item treated as an SRL measure rather than as a distinct construct?
5. §3.2 describes both "a random sample of students enrolled in the course section" and a voluntary mid-term announcement to which students "chose to respond." Which was it? If recruitment was mid-term and voluntary, students who withdrew earlier could not enter the sample — how does that conditioning affect the retention association?
6. §6 recommends dashboards as a strategy for retention "across programs and disciplines" and for institutions "worldwide." Which observation in this study extends beyond one course, one term, one dashboard, and one institution?
7. Nine of the fifteen listed references are never cited in text, and all fifteen share a single `10.5555/` DOI prefix across six differently-named journals. Please supply resolvable identifiers and either cite or remove the uncited entries.

### Minor Issues

- §1's framing of the setting as a first-year gateway course is never established; §3.1 describes a required quantitative-reasoning course for a range of majors without stating year level.
- Three-decimal reporting (M = 3.847) on a 1–5 integer single item asserts precision the instrument does not have.
- §5 describes the exam comparison as not reaching "a comparable level" while reporting p = .008 against a declared alpha of .05 — the narration inverts the significance logic on its face. Detailed reconstruction of the reported test statistics belongs to Reviewer 1.
- §3.1's "several hundred students" leaves the sampling fraction unknowable; give the enrollment.
- §3.2 discloses that "students were not informed that their dashboard activity data would be analyzed for this study," and the manuscript contains no ethics-approval, data-availability, or data-governance statement despite analysing individual-level student records linked to survey responses. I record this as an observation and do not assign it a severity: whether it is disqualifying depends on the venue's and the institution's documented requirements, which I cannot ground here `[FIELD-NORM UNVERIFIED]`. This finding belongs to the cross-disciplinary/practical seat and must not be lost between seats.
- The dashboard's "peer-comparison band" (§3.1) is the feature §2 identifies as potentially demotivating, yet its norm group, framing, and opt-out are unspecified — a domain reader cannot tell which dashboard genre is under study.

contract_role: domain

## Dimension Scores

### D1: methodology_rigor
score: block

My Phase 1 block trigger (c) fires: a causal/intervention-effect claim about retention ("improved," "raises," §5 and §6) from a design with no comparison condition and no adjustment for selection into dashboard use, with the inferential leap nowhere acknowledged — §5.1's limitations omit the correlational design, the volunteer sample, and selection entirely. Trigger (d) also fires on the face of the manuscript: the Abstract's r = .42 and §4.2's r = .24 describe the same association, and §4.3's "All 142 students" cannot be reconciled with Table 2's 127 given §3.3's retention coding. Consistent with my Phase 1 commitment, I score on the unacknowledged inferential leap, which is discipline-neutral, and not on the absence of randomization — a non-randomized dashboard study is normal practice in this field. Arithmetic reconstruction of the reported test statistics is Reviewer 1's determination; I record the conflicts as observed and defer their resolution.

### D2: domain_accuracy
score: block

Trigger (a) fires: §2's claim that dashboards "reliably improve outcomes for lower-achieving students" is attached to a source the manuscript's own reference list titles *"When dashboards demotivate: Peer comparison and the lower-achieving student,"* and the paper's equity rationale in §2 and §5 leans on the misstatement. Trigger (c) fires: "retention" is defined as single-course completion in §3.3 and generalized to program-, discipline-, and institution-level retention in §6, so the headline claim changes meaning between Methods and Conclusion. Trigger (b) fires in its second branch: the Abstract asserts that self-regulated learning behavior was measured when §3.3 contains no such measure, and §5 attributes to SRL an equivalence between perceived control and self-regulation that the framework does not assert. Trigger (d) does **not** fire — §2 genuinely engages null, adverse, and critical findings, which is a real strength.

### D3: argumentative_coherence
score: block

Triggers (a), (b), and (c) all fire. (a): §5's third paragraph counsels against overstatement and reads the effect as marginal, while §6 calls dashboards "a dependable strategy" and "a practical and generalizable lever"; §1 promises to distinguish pattern from causal story while §5 and §6 assert causation. (b): selection into dashboard use and reverse causation — the central alternative explanation in this literature, and acute here because a mid-term volunteer sample conditions on partial persistence — are named nowhere in the manuscript. (c): §6 recommends institutional investment and encouraging students to engage, an action whose justification requires the causal claim §4.2 declines to make. (d) fires partially: §2's heterogeneity and goal-orientation framing predicts differential effects, the study reports a pooled association with no moderation, and the conflict is unregistered.

### D4: cross_disciplinary_relevance
score: warn

No block trigger fires on my committed criteria. Trigger (b) does not fire because §3.3 does supply a definition of the outcome; trigger (c) does not fire because §5.1 does state boundary conditions (single course, specific dashboard design), even though §6 then contradicts them; trigger (a) does not fire because the manuscript does not misstate an adjacent discipline's position — it declines to engage higher-education persistence scholarship at all rather than misrepresenting it. Warn triggers (a), (b), (c), (d), and (e) all fire: SRL is used as a label without operational content; the Abstract promises implications for instructional design and institutional deployment that §5 does not deliver for either audience; institution type, student population, and dashboard genre (notably the peer-comparison band's norm group and framing) are under-described so transferability cannot be judged; and generalizability appears in §5.1 as a formality that §6 overrides. Per my Phase 1 commitment, narrow framing is a warn-class issue here, not a block.

### D5: writing_and_structure
score: block

Trigger (b) fires: the Abstract's r = .42 and §4.2's r = .24 stand for the same association with no reconciliation, so a reader cannot tell which is the finding; §4.3's "All 142 students" contradicts Table 2's 127 under §3.3's own retention coding; and the outcome variable of a retention paper appears in no table and its base rate is never reported. Trigger (c) fires in its second branch: 9 of 15 reference-list entries never appear in text, and all 15 carry an identical DOI prefix across six differently-named journals, so the evidentiary base cannot be audited. Trigger (a) does not fire — the intervention, outcome, and claimed result are each locatable. Prose quality and section flow are professional; the defects are below the prose layer.

## Failure Condition Checks

### F1
fired: true

Predicate: any mandatory dimension scores `block`. D1, D2, and D3 are mandatory and all score `block`. Severity 90.

### F2
fired: true

Predicate: two or more mandatory dimensions score `warn` or worse. D1, D2, and D3 all score `block`, which is worse than `warn`. Severity 70. (The `majority` quantifier is panel-level machinery for the synthesizer; I evaluate the predicate against my own scores only.)

### F3
fired: false

Predicate: any high-priority dimension scores `block`. The only high-priority dimension, D4, scores `warn`.

### F0
fired: false

Predicate: every mandatory dimension scores `pass`. D1, D2, and D3 all score `block`.

## Review Body

From the domain seat, this manuscript's problem is not competence but self-refutation. §2 is the work of authors who know their field: they know dashboard effects are heterogeneous, that click counts are not cognitive engagement, and that causal language in this literature outruns its evidence. §1 commits explicitly to distinguishing the pattern from the causal story. Everything after §4 abandons those commitments. §5 opens by asserting that engagement "improved" retention and that increasing it "raises" completion probability; §6 asserts "associated with, and raises," then prescribes worldwide institutional investment as "a dependable strategy." A limitations section that lists four real but non-binding limitations, while omitting the correlational design, the volunteer sampling, selection, and reverse causation, performs methodological maturity without exercising it — and is a more serious problem than no limitations section would be.

Two domain defects sit beneath the causal one. The citation in §2 that supports the equity rationale is attached to a claim that inverts the thesis stated in the manuscript's own reference-list title, and imports a certainty ("reliably") that the same paragraph elsewhere denies. This is checkable inside the manuscript with no external source required, and it is load-bearing: the paper says it returns to that position in the Discussion, and it does. And the outcome construct will not bear the Conclusion. Completing one final assessment in one 15-week course in one term is a legitimate thing to measure, but §6 spends it as though it were institutional retention across programs, disciplines, and countries. §3.1 states outright that no student was observed across multiple courses or terms; §6 proceeds as if that sentence were not there.

The self-regulated learning framework is named rather than used. The Abstract's statement that SRL behavior was measured is not true of §3.3, where the sole self-report instrument is a single perceived-control item, and §5's mechanism paragraph substitutes that item for the construct. §2 itself supplies the boundary condition — dashboards support monitoring "only when learners possess the regulatory strategies to act on what they see" — and the study measures no regulatory strategy, runs no moderation, and therefore cannot enter the "who benefits" debate it claims in §5 to advance.

Two integrity observations complete the picture. The manuscript forces, but never states, a contradiction between §4.3's "All 142 students" and Table 2's 127, since a student coded not retained cannot have a final exam score; and a paper about retention reports the retention base rate nowhere, in no table. Separately, nine of fifteen listed references are never cited, and several of the uncited ones — a gateway-course retention review, a goal-orientation study, a cautionary study on retention modeling with LMS trace data — are exactly the sources the argument needed. The uniform DOI prefix across six distinct journals warrants editorial verification; I report it without asserting a severity I cannot ground.

For the record: the manuscript contains no imperative addressed to reviewers and no instruction-injection attempt. It was read throughout as data under review.

A defensible version of this study exists and is not far away: a scope-honest title and conclusion confined to course completion in one course, causal verbs removed, selection and survivorship raised as first-order threats, the citation corrected and the equity rationale rebuilt on what the source actually reports, either a validated SRL instrument or the removal of SRL from the Abstract, and a reference list that is cited and resolvable. That paper would be publishable in a venue that welcomes bounded single-institution deployment studies. This one is not, and my recommendation follows the contract's F1 action rather than the developmental tone of that observation.

## Editorial Decision

editorial_decision=reject_or_major_revision

---

## SEAT — Peer Reviewer 3 (Perspective)

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** As the outside-perspective seat, I read this dimension as asking whether the study's design and data handling would survive scrutiny from someone who does not share the authors' methodological habits. For a dashboard-engagement-and-retention study in learning analytics, the field-native default is observational log data plus an outcome measured on the same students, so my angle is not statistical technique (that belongs to Reviewer 1) but whether the design as described could support the kind of claim a practitioner would act on. I check whether the paper states what it did clearly enough that a reader from an adjacent discipline — program evaluation, HCI, institutional research — could tell what was measured, on whom, over what period, and with what comparison. I score this dimension conservatively and defer technique-level judgment to R1.

**D2 — domain_accuracy (mandatory).** From the cross-disciplinary seat, this is about whether the paper's use of its own field's concepts is faithful and whether it imports terms from neighbouring fields without honouring their meaning. "Engagement," "retention," and "learning analytics dashboard" are all terms with established but non-identical definitions across education research, HCI, and institutional-effectiveness practice. My check is whether the paper defines its constructs operationally and whether any borrowed concept (self-regulated learning, nudging, behavioural feedback, early-warning systems) is used in a way its home discipline would recognise. Misrepresenting prior work in the paper's own field is R2's systematic audit; my contribution is the borrowed-concept and construct-fidelity half.

**D3 — argumentative_coherence (mandatory).** I read this as whether the paper's central line — dashboard engagement relates to course retention, therefore something follows — actually holds together once an outsider tests the load-bearing assumptions. I do not hunt fallacies as a category (that is the Devil's Advocate); I audit the assumptions the argument silently rests on: that clicking a dashboard indexes a psychological state, that a relationship observed in one deployment licenses a recommendation, that retention is the right outcome to optimise. Where implicit assumptions carry more weight than the stated evidence, the argument is incoherent from where I sit even if every sentence is locally valid.

**D4 — cross_disciplinary_relevance (high priority; my primary dimension).** This is the seat's home dimension. It asks whether the framing, definitions, and stated implications land for a reader from an adjacent field — an HCI researcher, a behavioural scientist, a student-affairs practitioner, an educational-data-ethics scholar — and whether any interdisciplinary claim the paper makes is actually substantiated rather than gestured at. Given the topic, the adjacent fields with the strongest claim on this paper are behaviour-change / nudge research, HCI dashboard-design work, and the fairness-and-surveillance literature on student-facing analytics. I also read this dimension as covering stakeholder coverage and practical implementability: a paper whose recommendations cannot be enacted by the people named in them, or which discusses students without any student-side consideration, has an unsubstantiated interdisciplinary reach.

**D5 — writing_and_structure (normal priority).** I read this as whether an adjacent-field reader can navigate the manuscript and reconstruct what was done from its organisation, exposition, and any figures or tables. At 2,487 words this is a short-format submission, so my bar is proportionate: brevity is not a defect, but a short paper still owes the reader an unambiguous statement of design, sample, measures, and limits. I score structure on whether compression has removed information a cross-disciplinary reader needs, not on stylistic preference or venue-formatting minutiae.

## Scoring Plan

### D1: methodology_rigor

- `what_to_look_for` — An explicit statement of design type (observational log study, quasi-experiment, RCT); who the students were and how they entered the sample; the operational definition of "dashboard engagement" (logins, dwell time, sessions, a composite) and of "retention" (course completion, non-withdrawal, next-term enrolment); the observation window and its relation to the outcome's timing; whether any comparison or control condition exists; whether the deployment context (one course, one cohort, one institution) is stated; whether data/code/instrument availability is mentioned at all.
- `what_triggers_block` — The paper's central claim is causal or quasi-causal ("the dashboard improved retention," "increasing engagement raises completion") while the reported design can only support association, AND no acknowledgement of that gap appears; **or** the operationalisation of either core construct (engagement, retention) is never stated, so a reader cannot tell what was measured; **or** self-selection into dashboard use is the obvious alternative explanation and the paper neither addresses nor names it.
- `what_triggers_warn` — Design and measures are stated but thin in a way that blocks independent judgment (window length, cohort size, or attrition handling absent); **or** causal language appears only in the abstract/conclusion framing while the body is properly hedged; **or** the deployment's scope (single course/term/institution) is inferable but never stated, leaving reproducibility affordances weaker than the field's bar without making the study uninterpretable.

### D2: domain_accuracy

- `what_to_look_for` — Whether "engagement" is defined behaviourally, psychologically, or left to float between the two; whether "retention" is used in the course-level sense the title implies rather than sliding into institutional persistence; whether imported constructs (self-regulated learning, nudging/behavioural feedback, early-warning or at-risk identification, dashboard "actionability") are used consistently with their home-discipline meaning; whether characterisations of prior learning-analytics deployments are stated as evidence or as background assertion; whether known field-level findings (heterogeneous and often null dashboard effects; usage skewing toward already-successful students) are represented rather than contradicted.
- `what_triggers_block` — A borrowed construct is redefined in a way that inverts its established meaning and the paper's conclusion depends on that redefinition (e.g., treating clickstream volume as "self-regulated learning" and then claiming an SRL effect); **or** a factual assertion about the domain that is squarely contradicted by well-established field knowledge is used as a load-bearing premise; **or** the same term is used with two incompatible meanings at points where the argument depends on them being the same.
- `what_triggers_warn` — Constructs are used loosely but recoverably (engagement conflated with behavioural proxy without an explicit statement that the proxy is a proxy); **or** an adjacent-field concept is invoked decoratively without engaging its literature, inflating apparent theoretical grounding; **or** prior-work characterisation is directionally right but flattened in a way that overstates consensus.

### D3: argumentative_coherence

- `what_to_look_for` — The chain from measured behaviour → inferred engagement → retention outcome → stated implication, and which links are argued versus assumed; whether the paper states its implicit premises (dashboard viewing indexes motivation or metacognition; retention is desirable for the student, not only the institution; more engagement is better without a ceiling or backfire region); whether the conclusion's scope matches the evidence's scope; whether recommendations follow from what was found or from what the authors hoped to find; whether contrary or null possibilities are entertained anywhere.
- `what_triggers_block` — The stated implication or recommendation cannot be derived from the reported finding even granting every stated assumption (e.g., an association is reported and a "deploy dashboards to raise retention" prescription is issued as the paper's conclusion); **or** a load-bearing implicit assumption is both unstated and false in a way that collapses the argument (reverse causality — persisting students keep using the dashboard — is the more parsimonious reading and is never confronted).
- `what_triggers_warn` — The core argument holds but one link is asserted rather than argued and the paper does not flag it as an assumption; **or** conclusion scope over-reaches modestly beyond the deployment studied (single-context finding stated as a general property of dashboards) while remaining recoverable with hedging; **or** an alternative interpretation is named in the limitations but never allowed to bear on the conclusion.

### D4: cross_disciplinary_relevance

- `what_to_look_for` — Whether definitions and framing are legible without prior learning-analytics training (jargon such as "clickstream," "at-risk flag," "LMS event" glossed or not); whether adjacent-field work with a direct claim on this topic is engaged — HCI dashboard/visualisation design, behaviour-change and nudge research (including backfire and demotivation effects of downward social comparison), and the ethics/fairness literature on student-facing monitoring; whether the student is present as a stakeholder with their own interests rather than only as a data source; whether the equity dimension is considered (who has the digital access, time, and literacy to engage with a dashboard, and whether an engagement-based signal advantages already-advantaged students); whether stated implications for instructors or administrators are implementable given ordinary institutional resources; whether any interdisciplinary claim the paper does make is backed rather than asserted.
- `what_triggers_block` — The paper issues an actionable recommendation about intervening on students (targeting, flagging, nudging, or allocating support by dashboard engagement) with no consideration of student-side consequences — equity, privacy, surveillance, demotivation, or the self-fulfilling effect of at-risk labelling; **or** an explicit interdisciplinary claim ("this is a behaviour-change intervention," "this operationalises self-regulated learning theory," "this addresses equity gaps") is made with no substantiation from the field it borrows from; **or** the framing is so field-internal that an adjacent-field reader cannot determine what the dashboard shows students or what action it invites, making the contribution unassessable outside the specialty.
- `what_triggers_warn` — Student stakeholder interests are acknowledged in a sentence but never bear on the interpretation or recommendations; **or** an adjacent literature with an obvious claim on the finding (nudge backfire, dashboard-design effects on interpretation, engagement-metric equity) is entirely absent while the paper's claims would materially change if it were engaged; **or** generalisation across institutional types, disciplines, or student populations is asserted without a boundary-condition statement; **or** the practical recommendation is stated at a level of abstraction ("institutions should promote dashboard use") that a practitioner cannot act on.

### D5: writing_and_structure

- `what_to_look_for` — Whether the reader can locate design, sample, measures, results, and limits as distinct, findable content; whether the abstract's claim matches the body's claim; whether any figure or table is self-contained (axes, units, denominators, N) and whether its caption's interpretation actually follows from what it displays; whether the short format has been used to compress redundancy or to omit substance; whether a limitations statement exists at all; whether terminology is used consistently across sections.
- `what_triggers_block` — The manuscript's organisation makes the study unreconstructable — results cannot be tied to a stated method, or the reported numbers/figures contradict the narrative claim in a way a reader cannot resolve; **or** a figure or table is the sole evidence for the central claim and is uninterpretable (no denominators, no units, unlabelled axes) so the claim cannot be checked at all.
- `what_triggers_warn` — Structure is followable but a needed element is missing or buried (no limitations section; sample description scattered across sections; measures defined only in a figure caption); **or** abstract and body differ in claim strength; **or** figure/table captions assert an interpretation stronger than the display supports; **or** venue conventions are visibly unmet (missing ethics/data-availability statement for a study on identifiable student behavioural data) in a way that is remediable in revision.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Perspective Review Report (Peer Reviewer 3)

### Reviewer Identity

Director of learning technology and student data governance at a large public university; practitioner-scholar who has deployed and later decommissioned two student-facing analytics dashboards at scale, chairs an institutional research data-ethics review for learning-technology studies, and publishes on consent, secondary use, and algorithmic transparency in educational trace data. Deliberately not a retention theorist and not a statistician: I read this manuscript as the person who would be asked to act on it, and as the person who would have had to approve it.

### Overall Recommendation

**Reject** — resubmission welcome as a re-scoped study, not as a revision of this one. (The contract-derived action from my scores is the F1 reject-or-major-revision branch; my own reading within that branch is the reject side, for the reasons in W1 and W4. I hold this at parity with the other seats, not above them.)

### Confidence Score

4

### Summary Assessment

I want to be explicit about my outsider status: I am not positioned to adjudicate the statistics, and where a finding of mine touches numbers I flag it and route it to Reviewer 1. What I can assess is whether this study could have been approved at my institution, and whether its recommendation could be acted on at mine.

On the first question, §3.2 states that students were not informed their dashboard activity would be analysed for this study. The survey obtained consent; the behavioural trace data did not. There is no ethics-approval statement, no data-availability statement, no account of how logs were de-identified or linked to survey responses. That is undisclosed secondary use of identifiable student behavioural data, and a paper carrying it should not recommend that institutions worldwide expand behavioural analytics deployment. The gap between the paper's own governance practice and its governance-scale recommendation is, from where I sit, the finding.

On the second question, §6 treats engagement as a lever institutions can pull. It is not. This study observed students who chose to open a dashboard; the recommendation proposes inducing students to open it. Those are different interventions with different populations and different failure modes, and the paper supplies no evidence about the second. Meanwhile the students the retention question is actually about — those who left — are structurally absent from a sample recruited by a mid-term announcement.

The prose is clean and the field awareness in §2 is real. Neither compensates.

### Strengths

1. **Candour about the measurement problem**: §2's paragraph on click proxies, and §3.3's concession that the median split is "a coarse simplification," are more self-critical than most deployment papers I read. That instinct is the seed of a better study.
2. **The right construct pairing**: pairing behavioural trace with a subjective regulatory measure is a genuinely good design instinct for the self-regulated-learning question. It should survive into whatever the authors build next, with a validated instrument in place of the single item.
3. **Correct register in one place**: §5's third paragraph ("the modest size of the engagement–retention association counsels against overstatement") is the tone the whole Discussion needed. The authors can already write the paper they should have written.
4. **Disclosure of the consent gap**: §3.2 says plainly what was not done. Many manuscripts in this space simply omit the sentence. The disclosure is creditable even though what it discloses is disqualifying — and it should not be removed in revision; it should be resolved.
5. **Field-level self-awareness in §2**: naming the causal-overreach critique and the heterogeneity debate shows the authors know the terrain, which makes the remedy a matter of discipline rather than of learning.

### Weaknesses

1. **Undisclosed secondary use of behavioural data, and no ethics apparatus at all** (§3.2): students consented to a survey, not to log analysis; survey responses were evidently linked to individual LMS records with no stated basis; there is no IRB/ethics statement, no de-identification account, no data-availability statement, no conflict-of-interest declaration. *Why it matters*: at my institution this is not a reporting omission, it is a protocol failure — the linkage is the part that would have required review, and it is exactly the part not described. *Suggestion*: state the approving body and protocol number, the legal/ethical basis for trace-data analysis, the linkage and de-identification procedure, and whether students could opt out. If no approval exists, that has to be said, and the manuscript's scope narrowed accordingly; a journal ethics editor, not a reviewer, should then decide whether it is publishable.
2. **A recommendation about intervening on students with no student-side consideration** (§6): the paper advises institutions to invest in dashboards and encourage engagement, with nothing on equity, privacy, demotivation, surveillance, or the self-fulfilling effect of engagement-based flagging. *Why it matters*: §2 itself raises the demotivation risk (peer comparison discouraging struggling students, goal-orientation dependence) and then drops it — the risk the authors identified is the risk their recommendation runs. Undifferentiated "encourage everyone to engage" may be actively harmful to precisely the students the equity rationale invokes. *Suggestion*: either add a student-consequences section that carries into the recommendation, or drop the prescription and report the association.
3. **Engagement is treated as a manipulable lever, which is a deployment error, not a phrasing one** (§5–§6): what was observed is spontaneous use by students who were already persisting; what is recommended is induced use via nudges, mandatory check-ins, or gamification. *Why it matters*: every practitioner attempt I know of to drive dashboard usage tests a different intervention from the one this study observed, and the modest association reported here — roughly six percent of shared variance, on the paper's own number — cannot carry the word "dependable." *Suggestion*: state the intervention the study licenses (none) separately from the hypothesis it generates (that induced use might matter, to be tested by a design that induces it).
4. **The people the paper is about are not in its data** (§3.2): recruitment ran through a mid-term LMS announcement, and the outcome is whether students persisted to the final. Students who had already disengaged or withdrawn could not answer. *Why it matters*: this is a who-is-missing problem before it is a statistics problem — the sample is filtered on something close to the outcome, and the association could be produced by that filter alone. It is nowhere named. *Suggestion*: use the full cohort's log and registrar data, with the survey as an optional overlay; and name self-selection into dashboard use as a live alternative explanation, not only in limitations.
5. **The deployment is unreproducible, and the one specified feature is the risky one** (§3.1, §3.3): the dashboard is described as showing "engagement metrics, assignment progress, and a peer-comparison band." No norm group, no framing, no opt-out, no screenshot, no platform named — and the sessionization rule is attributed to "the platform's default" without saying which platform. *Why it matters*: no institution can replicate this deployment or this measure, so the finding cannot travel, which is fatal to a paper whose contribution is claimed to be practical. *Suggestion*: publish the interface specification (or a figure), name the LMS and the sessionization rule, and report the peer-comparison band's design — it is the feature §2 flags as potentially demotivating.

### Detailed Comments

#### Assumption Audit

- **Explicit assumptions**: §1 states the load-bearing one — "visibility supports self-regulation." The paper treats this as the theoretical warrant and then never tests it; the single perceived-control item is a correlate of use, not evidence that visibility produced regulation. A second explicit assumption, that dashboard use is the relevant unit of intervention, is inherited from the field rather than argued.
- **Implicit assumptions** (the audit my seat owes you): (a) that opening a dashboard indexes a psychological state rather than general conscientiousness or overall LMS habit; (b) that engagement is institutionally manipulable — this is the assumption §6's entire recommendation rests on, and it is never stated; (c) that retention is good *for the student*, not only for the institution — the paper never separates the two, though a student leaving a mis-chosen course may be making a good decision; (d) that the students who left would have behaved like those who stayed; (e) that observing students is ethically costless, which §3.2 quietly demonstrates the authors assumed.
- **Paradigmatic assumptions**: the manuscript inherits learning analytics' trace-as-truth positivism — that the log is the behaviour and the behaviour is the mind — together with a monotonic "more visibility, better regulation" model that has no ceiling and no backfire region, even though §2 cites the backfire case. It also inherits the field's habit of treating the student as a data source rather than a party with interests. From data-governance work, the productive counter-frame is that a dashboard is a disclosure to the student *and* a collection from the student; this paper theorises only the first half.

#### Cross-Disciplinary Connections

- **Parallel research**: behaviour-change and nudge research has spent a decade on exactly this shape of claim — an observed correlation between voluntary uptake of a feedback tool and a downstream outcome — and has repeatedly found that induced uptake does not reproduce voluntary-uptake associations, and that downward social comparison can reverse the intended effect. That literature has a direct claim on §6 and is entirely absent here.
- **Borrowing opportunities**: three concepts would materially strengthen the paper. *Backfire / boomerang effects* would give §2's demotivation paragraph somewhere to land. *Differential susceptibility* would convert the "who benefits" gesture in §5 into a testable moderation question. *Data subject* framing from information-governance work would supply the vocabulary the manuscript lacks for what happened in §3.2.
- **Methodological borrowing**: from program evaluation, an intention-to-treat frame over the full cohort would remove the volunteer filter. From HCI, a specification-plus-instrumentation report (interface, event taxonomy, sessionization) is a routine publication component that would make the deployment replicable. From service-design practice, a decommissioning or non-adoption analysis — why students who never opened it never opened it — would answer a question this design cannot.

#### Practical Impact

- **Real-world application**: if I took this paper to my provost, I could not act on it. It does not tell me what the dashboard showed, on what platform, to which students, or what happened to the students who left. Its actionable content reduces to "buy a dashboard and encourage use," which is where the sector already was before the study.
- **Implementation feasibility**: the recommendation is cheap to state and expensive to follow. Driving engagement means either nudge campaigns (which test a different intervention, and which the paper's own §2 suggests may harm the intended beneficiaries) or mandatory check-ins (which convert a self-regulation tool into a compliance task and destroy the mechanism). The opportunity cost is real: the same budget buys advising outreach with a considerably better evidence base. My honest expectation, from having run this play twice, is a null result and a decommissioning two years later.
- **Stakeholders**: students appear only as data sources — not as parties to the data collection, not as people with a view on being compared to peers, not as the constituency whose withdrawal the paper is nominally about. Instructors receive no actionable guidance. Advising and student-support staff, who would absorb any real intervention, are absent. So is the institutional data-governance function, which in this case was apparently bypassed. Power asymmetry is not discussed anywhere: students could not decline the log analysis because they were not told it was happening.

#### Broader Implications

- **Ethical dimensions**: beyond the consent gap itself, the manuscript normalises a practice — analysing student behavioural traces for research without notice — while recommending its expansion. That combination is what makes this more than a paperwork problem. The linkage of survey responses to individual logs also means the dataset is identifiable at the point of analysis, which is the condition under which most institutional review frameworks require prior approval.
- **Social impact**: engagement-based signals track digital access, time, and device quality as much as motivation. A student working two jobs on a phone will look disengaged. If institutions allocate attention or flags by dashboard engagement, the signal advantages already-advantaged students and risks a self-fulfilling at-risk label for the rest. The §6 leap to "institutions worldwide" is the point at which this becomes a distributive question: the recommendation is least affordable and most likely to displace human support precisely where support is thinnest.
- **Future directions**: the studies I would fund after this one are (a) a full-cohort study with an interface specification published alongside, (b) a moderation analysis testing whether the peer-comparison band helps or harms by prior achievement, (c) a consent-forward design in which students are told what is collected and can opt out, with uptake itself as an outcome, and (d) a decommissioning study, since the field's null results are systematically unpublished.

### Cross-Disciplinary Reading Recommendations

I cannot attest to any of the manuscript's 15 references — all carry `10.5555/` placeholder DOIs, which resolve to nothing — and I will not answer that with invented citations of my own. The following are search leads, not citations:

- `[UNVERIFIED]` Nudge/behaviour-change work on **boomerang effects of descriptive social-norm feedback** — search lead: "descriptive norm feedback boomerang effect" plus "social comparison demotivation." Directly relevant to the peer-comparison band in §3.1.
- `[UNVERIFIED]` Learning-analytics **ethics and consent frameworks** for institutional deployment — search lead: "learning analytics ethics framework consent transparency" and the DELICATE-style checklists used in European institutional practice. Relevant to §3.2 and to what the manuscript would need to state.
- `[UNVERIFIED]` HCI work on **dashboard interpretation and visualisation framing effects** — search lead: "learning dashboard design interpretation misreading." Relevant to why interface specification is not a cosmetic omission.
- `[UNVERIFIED]` **Voluntary-versus-induced uptake** in digital-feedback interventions — search lead: "engagement with self-monitoring tools induced versus voluntary" in health behaviour change, where the design problem is best documented. Directly relevant to §6's lever assumption.
- `[UNVERIFIED]` **Equity of engagement metrics / algorithmic at-risk labelling** in education — search lead: "early warning system equity self-fulfilling label student." Relevant to the dropped equity thread.

### Questions for Authors

1. Under what approval, and on what basis, were behavioural logs analysed for students who were not informed of that analysis — and how were survey responses linked to individual log records?
2. What proportion of students who withdrew before the mid-term announcement are represented in the analytic sample, and how would the association look computed on the full cohort rather than on volunteers?
3. What exactly does the peer-comparison band display — which norm group, what framing, can a student turn it off — and how do you reconcile deploying that feature with the demotivation risk you raise in §2?
4. §6 recommends encouraging students to engage. What evidence do you have that *induced* engagement behaves like the *voluntary* engagement you observed, and what would you expect to happen to performance-avoidance-oriented students under such a campaign?
5. The abstract states that self-regulated learning behaviour was measured. Which measure is that, and if it is the single perceived-control item, would you accept a rewrite that removes the SRL measurement claim throughout?

### Minor Issues

- §3.1 says "several hundred students" enrolled; give the number, since it sets the volunteer response rate that §3.2 never reports.
- The sessionization rule is attributed to "the platform's default" without naming the platform — unusable for replication.
- Final exam score appears in Table 1 and §4.3 but is never defined in §3.3 Measures.
- Three-decimal reporting of a mean from a 1–5 integer item (3.847) implies a precision the instrument does not have.
- No data-availability, ethics, or conflict-of-interest statement anywhere; most target venues require all three for trace-data studies.
- Eight of the fifteen listed references never appear in the text (Reviewer 2's territory; noting it only because an adopter checking provenance will hit it immediately).
- **Integrity note**: I found no instruction-injection attempt in the manuscript. It reads as an ordinary submission; nothing in it addressed reviewers or attempted to direct scoring.

---

contract_role: perspective

## Dimension Scores

### D1: methodology_rigor
Applying my committed block trigger, third clause: self-selection is the obvious alternative explanation for the reported association and the manuscript neither names nor addresses it. Two independent selection mechanisms operate — self-selection *into dashboard use* (the students who open a dashboard are plausibly the conscientious ones, and no baseline LMS activity, prior achievement, or motivation measure is reported), and self-selection *into the sample* (§3.2's mid-term announcement can only recruit students still present, so the retention outcome is measured on a set filtered on something close to the outcome). §5.1 lists four limitations and omits both. I note but do not score the §3.2 contradiction between "a random sample of students enrolled in the course section" and the volunteer-response recruitment described two sentences later; whether the reported analyses can be reconstructed at all is Reviewer 1's adjudication, and I defer it there rather than double-score it here.
score: block

### D2: domain_accuracy
Two findings in my committed construct-fidelity lane. First, the abstract states that "self-regulated learning behavior" was measured. It was not: the only regulatory measure is a single perceived-control item, and §5's SRL mechanism account depends on treating that item as evidence of self-regulation. That is a borrowed construct used in a way its home literature would not recognise, at the most-read point in the paper, with the conclusion resting on it. Second, "retention" is operationalised in §3.3 as remaining enrolled and sitting the final assessment in one course, then generalised in §6 to "retention across programs and disciplines" for "institutions worldwide" — course completion and institutional persistence are different constructs with different determinants, and §6's recommendation requires them to be the same. I also register, without claiming it as my finding, that §2's assertion that dashboards "reliably improve outcomes for lower-achieving students" is attached to a source titled *When dashboards demotivate*, and that the manuscript itself declares that claim load-bearing ("underpins much of the equity-oriented rationale... we return to it in the Discussion"); the systematic citation–claim audit belongs to Reviewer 2.
score: block

### D3: argumentative_coherence
My committed block trigger fires on both clauses. The recommendation in §6 — that institutions worldwide invest in dashboards and encourage engagement as "a dependable strategy" — cannot be derived from the reported association even granting every stated assumption, because nothing in the design speaks to what happens when engagement is induced rather than chosen. And the load-bearing implicit assumption is never confronted: persisting students continue using the dashboard because they are persisting, which reads at least as parsimoniously as the paper's direction and is nowhere entertained. §5 opens with "dashboard engagement improved course retention... increasing dashboard engagement therefore raises the probability," and §6 with "associated with, and raises" — these are the two most load-bearing positions in the manuscript, and §1's promise to "distinguish the pattern in the data from the causal story" makes their content a contradiction rather than an oversight.
score: block

### D4: cross_disciplinary_relevance
My primary dimension, and my committed block trigger fires on its first clause. §6 issues an actionable recommendation about intervening on students — invest, encourage engagement, at institutional scale, worldwide — with no consideration of any student-side consequence: no equity analysis of who has the access, time, and literacy to engage; no privacy or surveillance discussion, in a study that analysed behavioural traces without notice (§3.2); no engagement with the demotivation risk the manuscript itself raises in §2; nothing on the self-fulfilling effect of engagement-based at-risk signals. The student appears throughout as a data source and never as a party. Independently, the third clause is also met at the practical end: the dashboard is specified only as "engagement metrics, assignment progress, and a peer-comparison band," which leaves an adjacent-field reader unable to determine what students were shown or what action it invited, and leaves an adopting institution unable to replicate either the deployment or the measure.
score: block

### D5: writing_and_structure
Applying my committed warn trigger rather than the block one, deliberately. The manuscript's organisation is followable — IMRaD is clean, measures are located in §3.3, results map to method — so the block clause's "unreconstructable" bar is not met from my lane. What is missing are required elements: no ethics-approval statement, no data-availability statement, and no conflict-of-interest declaration for a study on identifiable student behavioural data, which is a venue-convention failure remediable in revision; and a limitations section (§5.1) that performs methodological maturity while omitting every limitation that would constrain the conclusions — correlational design, volunteer self-selection, absence of confounding controls, the single-item measure, the median split. I also observe, and route to Reviewer 1 rather than score here, that the abstract's r = .42 and §4.2's r = .24 differ, and that §4.3's statement that all 142 students were classified into engagement groups does not match Table 2's group sizes summing to 127; whether those are transcription errors or evidence that the analyses cannot be reconstructed determines their weight, and that determination is not mine to make.
score: warn

## Failure Condition Checks

### F1
Predicate: any mandatory dimension scores 'block'. D1, D2, and D3 are mandatory and all score block.
fired: true

### F2
Predicate: two or more mandatory dimensions score 'warn' or worse. Three mandatory dimensions (D1, D2, D3) score block, which is worse than warn.
fired: true

### F3
Predicate: any high-priority dimension scores 'block'. D4 is the high-priority dimension and scores block.
fired: true

### F0
Predicate: every mandatory dimension scores 'pass'. None do.
fired: false

## Review Body

This manuscript reads as competent until you ask what it would take to have run it and what it would take to act on it. Both questions return the same answer: the paper's practice and its prescription point in opposite directions.

On practice, §3.2 discloses that students were not informed their dashboard activity would be analysed. The survey obtained consent; the trace data did not, and survey responses were evidently linked to individual log records with no stated basis, no de-identification account, and no ethics-approval statement anywhere in the manuscript. This is undisclosed secondary use of identifiable student behavioural data. It is not a reporting omission that a revision can tidy, because the linkage — the part not described — is the part that would have required prior review. A manuscript carrying that gap while recommending that institutions worldwide expand behavioural analytics deployment is asking the field to adopt at scale a practice it did not itself follow at one site.

On prescription, §6 treats engagement as a lever. The study observed students who chose to open a dashboard; the recommendation proposes inducing students to open one. Those are different interventions on different populations, and the manuscript supplies no evidence about the second. Every practitioner route to driving usage — nudge campaigns, mandatory check-ins, gamification — either tests something this study did not observe or converts a self-regulation tool into a compliance task and destroys the mechanism the theory depends on. On the paper's own number, the association accounts for roughly six percent of shared variance, which the word "dependable" cannot survive.

Two absences compound this. The students the retention question is about are largely not in the data: a mid-term announcement can only recruit students still present, so the sample is filtered on something close to the outcome, and §5.1 never names it. And the deployment is unreproducible: no platform, no interface specification, no norm group or framing or opt-out for the peer-comparison band — the one feature §2 identifies as potentially demotivating is the one left undescribed. An adopting institution cannot replicate either the intervention or the measure, which is fatal to a contribution claimed as practical and generalizable.

The equity thread is raised and dropped. §2 establishes that dashboard effects are conditional on goal orientation and prior achievement, and that peer comparison can discourage the students it is meant to help. §5 gestures at the "who benefits" debate without a moderation analysis, and §6 then recommends undifferentiated encouragement — the intervention most likely to harm the constituency the equity rationale invokes. Engagement metrics also track digital access and available time, so an engagement-based signal advantages already-advantaged students and risks a self-fulfilling label for the rest. None of this appears.

What should be preserved: the construct pairing of behavioural trace with a subjective regulatory measure is a good instinct, §2's candour about click proxies is better than the field average, and §5's third paragraph shows the authors can write in the register the rest of the paper needed. A defensible version of this study exists — full cohort rather than volunteers, a validated multi-item regulatory instrument in place of the single item, prior-achievement and baseline-activity controls, a published interface specification, moderation by prior achievement, an ethics statement that answers the §3.2 problem, and a title and conclusion scoped to one course at one institution. That is a different study, not a revision of this one, which is why my reading within the contract's severity-90 branch is the reject side. I hold that verdict at parity with the other seats and note that my ethics finding stands independently of how Reviewer 1 resolves the reported statistics.

## Editorial Decision

Precedence resolution over my own fired conditions: F1 (severity 90), F2 (70), and F3 (60) all fired; F0 did not. Highest severity wins, so F1 governs.

editorial_decision=reject_or_major_revision

---

## SEAT — Devil’s Advocate

### Phase 1 (blind call)

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** The contract asks whether the study's design, data handling, statistical reporting, and reproducibility affordances clear the field's peer-review bar. As Devil's Advocate I do not re-run the methodology reviewer's design critique; I read this dimension as an attack surface: does the reported methodological apparatus actually license the inferential weight the paper places on it, or is there a gap between what the design can identify and what the argument needs it to identify? For a retention-outcome study in learning analytics, the adversarial question is whether the reported procedure permits any causal or predictive claim at all, and whether the reproducibility affordances present are sufficient for a reader to tell. I score `block` only when the gap is foundation-collapsing, not when the design is merely modest — and per Challenge Dimension 9 (#215), any severity of mine that rests on "this field should release X / report Y" must name the field's actual accepted-practice boundary from a checkable source, or it down-rates to advisory with `[FIELD-NORM UNVERIFIED]`.

**D2 — domain_accuracy (mandatory).** The contract asks whether claims align with current domain evidence, whether prior work is correctly represented, and whether domain terminology and reported results are factually right. My adversarial reading of this dimension is not "did the authors cite enough" — literature-coverage completeness belongs to R2 — but rather: is the evidence base *selectively assembled*? Cherry-picking (Challenge 2) and confirmation bias (Challenge 3) live here for me. In student-facing dashboard research, the domain has a well-known mixed-to-null evidence record and known constructs (engagement measured as logins/clicks versus engagement as a latent construct); misrepresenting a cited finding's direction or strength, or silently redefining a contested construct as if settled, is the failure pattern I scan for. Terminological misuse only reaches high severity when the misuse is load-bearing for a claim.

**D3 — argumentative_coherence (mandatory).** The contract asks whether the core thesis is internally consistent, whether the evidence actually supports the claims, and whether fallacies undermine the central argument. This is my home dimension — Challenges 1, 4, and 5 map onto it directly, and it is where Foundation Collapse, Logic Chain Break, Data-Conclusion Mismatch, and Stronger Counter-Narrative CRITICAL criteria apply most often. The paper's title pairs "dashboard engagement" with "course retention," which is a correlational pairing; the adversarial question is whether every inferential step from observed association to whatever the paper concludes is licensed, whether hidden assumptions (that dashboard use causes rather than indexes conscientiousness, for instance) are stated, and whether the stated scope of inference matches the evidence. Selection into dashboard use is the obvious rival explanation class, and I will judge whether the paper's argument survives it.

**D4 — cross_disciplinary_relevance (high priority, not mandatory).** The contract asks whether framing, definitions, and implications are accessible to adjacent-field readers and whether interdisciplinary claims are substantiated. Adversarially, I treat this as a load-bearing-borrowing test, not a readability test: when a paper imports a construct or a warrant from an adjacent field (retention theory from higher-education research, engagement from motivation psychology, an econometric identification claim), does the import carry the source field's conditions with it, or is the borrowed term doing work its home discipline would not endorse? I also read Challenge 7 (stakeholder blind spots) here in its bounded form — I name whose perspective is structurally absent from the framing, without elaborating what they would say, since that elaboration is R3's role. Note that D4 is `high`, not `mandatory`: a `block` here fires F3 (severity 60), never F1.

**D5 — writing_and_structure (normal priority).** The contract asks about organisation, exposition clarity, figure and table quality, and venue conventions. This is the dimension where a Devil's Advocate is most at risk of manufacturing findings, and also where the Surface-Form Parity gate (#216) bites hardest in the opposite direction: I must not treat polished prose as evidence of a sound argument, nor treat rough prose as a defect in the argument. My adversarial interest in D5 is narrow and specific — structural choices that *conceal* argumentative weakness (a results presentation that makes a null or weak primary outcome hard to locate, a figure whose caption interprets beyond what the artifact shows, an abstract whose claim strength exceeds the body's). A 2,487-word manuscript is short — brevity is not itself a defect and I will not score it as one, but omission of load-bearing detail that the argument depends on is a D3 or D1 finding surfacing through D5. No failure condition in this contract is triggered by D5 alone; it is reportable, never decisive.

## Scoring Plan

### D1: methodology_rigor
- `what_to_look_for`: Whether an inferential design is stated at all and what it can identify (single-cohort observational, quasi-experimental, RCT, pre/post); how the analytic sample was constituted and whether attrition or exclusions are accounted for; what "dashboard engagement" is operationally (logins, sessions, dwell time, feature events) and whether that operationalisation is stable across the analysis; whether retention is defined with an explicit window and denominator; whether the reported statistics carry the quantities needed to evaluate them (effect sizes, uncertainty intervals, N per cell) rather than significance markers alone; whether the temporal ordering of engagement measurement and the retention outcome is specified, since engagement measured through the outcome window is partly the outcome; whether any pre-registration, analysis-plan, code, or data-availability statement exists and what the field's actual stated norms are for such a statement.
- `what_triggers_block`: The design as described cannot support the inferential claim the paper is built on, and no revision short of new data could rescue it — for example, engagement is measured over a window that includes or postdates the retention outcome (temporal circularity), or the analytic sample is defined by a rule that mechanically produces the reported association, or the primary comparison's denominator/attrition is unrecoverable from the text such that the headline quantity is not evaluable. Also `block` if a reported statistical quantity is internally impossible or contradicts another reported quantity in a way that invalidates the primary result.
- `what_triggers_warn`: The design supports a weaker claim than the one made but the gap is closable by rescoping the claims — missing effect sizes or uncertainty, unreported attrition, an operationalisation of engagement that is stated but never justified or sensitivity-checked, or reproducibility affordances that are thinner than the paper's own claims require. Also `warn` when I identify a reproducibility or reporting deficit whose severity depends on a field norm I cannot ground in an external checkable source: in that case the finding is recorded and labelled `[FIELD-NORM UNVERIFIED]` and capped at `warn` — it may not be escalated to `block` on the strength of the norm.

### D2: domain_accuracy
- `what_to_look_for`: Whether cited prior work is represented with its actual direction, magnitude, and boundary conditions, or flattened into support; whether the known heterogeneity of the student-facing dashboard literature (including null and negative findings, and documented differential effects across student subgroups) is acknowledged or silently dropped; the ratio of supporting to disconfirming citations relative to what the field's record plausibly contains; whether contested constructs (engagement, retention, "at-risk") are defined as if settled; whether domain-specific terms are used in their field-standard sense; whether any factual claim about a named system, dataset, policy, or prior result is checkable against the paper's own presented evidence and internally consistent.
- `what_triggers_block`: A load-bearing factual misrepresentation of prior work or domain fact — a cited finding's direction or conclusion is reversed or materially overstated and the paper's argument depends on that reading, or a central construct is defined in a way that contradicts its field-standard meaning while the paper's conclusion trades on the standard meaning. Also `block` if the evidence base is assembled so selectively that a known and directly relevant contradicting body of evidence is absent *and* the paper's central claim would not survive its inclusion (Stronger Counter-Narrative criterion, not a coverage-completeness complaint).
- `what_triggers_warn`: Detectable one-directional selection in the cited evidence, or prior findings presented without their boundary conditions, or a contested construct treated as settled — where the paper's core claim would survive correction but its stated confidence would not. Also `warn` for terminological imprecision that is non-load-bearing but recurrent enough to mislead an adjacent reader. Per the parity gate (#216), I score the substance of the misrepresentation, not whether the citation prose sounds authoritative; a precisely-worded claim about a prior study is not credited as accurate until checked against what the paper itself shows.

### D3: argumentative_coherence
- `what_to_look_for`: The explicit statement of the core thesis and whether it is held constant across abstract, results, and discussion, or escalates; every inferential step from observed association to the paper's conclusion, and which steps carry unstated assumptions; whether selection into dashboard use is treated as a rival explanation or assumed away (the canonical confound here — students who check dashboards may be the students who would persist regardless, making engagement an index of an underlying disposition rather than a cause of retention); whether causal or quasi-causal verbs ("improves", "drives", "leads to", "increases") appear where the design only licenses association; whether the scope of generalisation matches the sampled context (one undergraduate deployment, one institution, one term); whether any internal contradiction exists between sections; whether a more parsimonious alternative explanation fits the presented data at least as well as the paper's.
- `what_triggers_block`: The main conclusion does not follow from the presented evidence even taking that evidence at face value — a Logic Chain Break, a Data-Conclusion Mismatch (the reported result does not sustain the stated conclusion), a Foundation Collapse (a core assumption is contradicted by the paper's own reported data), or a Stronger Counter-Narrative where an alternative explanation (selection, reverse causation, a common cause such as prior achievement or conscientiousness, or a floor/ceiling artifact) is both more parsimonious and a better fit to the presented data than the paper's account, and the paper does not address it. Also `block` if the abstract or conclusion asserts a causal or policy-actionable claim that the design and results cannot license, since that is the claim readers will carry away.
- `what_triggers_warn`: The core inference holds but individual steps are under-argued — a hidden assumption that is defensible once surfaced, a rival explanation acknowledged but dismissed without evidence, generalisation language slightly exceeding the sampled context, or claim-strength drift between the abstract and the body where the body is defensible. Also `warn` when I can construct a serious counter-argument the paper does not address but cannot show it fits the presented data *better* than the authors' account — the counter-argument is reported in full at that severity rather than inflated to `block`.

### D4: cross_disciplinary_relevance
- `what_to_look_for`: Which adjacent fields the paper borrows from (higher-education retention research, motivation and self-regulated-learning psychology, HCI, causal inference or econometrics) and whether each borrowed construct or warrant travels with the conditions its home field attaches to it; whether "retention" is used in the institutional sense, the course-completion sense, or the persistence-theory sense, and whether the paper is consistent about which; whether an implication addressed to an adjacent audience (instructional designers, institutional policy, dashboard vendors) is substantiated by this paper's evidence or imported from elsewhere; whether definitions sufficient for an adjacent-field reader to evaluate the claims are present; which stakeholders are structurally absent from the framing (I name the absence only — the elaboration of their perspective is R3's, not mine).
- `what_triggers_block`: An interdisciplinary claim is load-bearing and unsubstantiated — the paper's conclusion rests on a construct or warrant imported from an adjacent field while stripping the condition that makes it valid there (for example, invoking a causal-inference framework's language for an identification claim the design does not meet, or invoking a persistence-theory mechanism as if this study tested it), and the conclusion does not survive restoring the condition. Note that this fires F3 (major_revision), not F1.
- `what_triggers_warn`: Borrowed terminology is used loosely but not load-bearingly; a central construct is left undefined for adjacent readers such that the claims are hard to evaluate outside learning analytics; implications are addressed to an audience whose situation this deployment does not represent; or a stakeholder group whose interests are materially affected by the paper's recommendations is structurally absent from the framing.

### D5: writing_and_structure
- `what_to_look_for`: Whether the argument's load-bearing quantities are findable and reported in the body rather than only asserted in the abstract; whether figure and table captions interpret beyond what the artifact actually shows; whether the primary outcome is presented as prominently as secondary or favourable results, or is structurally de-emphasised; whether the abstract's claim strength matches the discussion's; whether limitations are a genuine section or a disclaimer that concedes a weakness in one line and proceeds as if it were resolved; whether the 2,487-word length reflects an appropriately scoped short-form contribution or an argument whose supporting detail has been omitted. Per the parity gate (#216), I judge substance over polish in both directions: fluent prose earns no credit toward correctness, and rough prose is no evidence of a defective argument.
- `what_triggers_block`: Reserved and expected to be unused at this dimension. It would require presentation so defective that the paper's central claim cannot be evaluated at all — for example, the primary result is nowhere reported in a form a reader could check, or a figure/table and the text state mutually contradictory values for the primary outcome with no way to resolve which is intended. If I find such a case I will also state plainly whether the finding's true home is D1 or D3, because a `block` here fires no failure condition on its own and the misplacement would understate the defect.
- `what_triggers_warn`: Organisation or presentation that obscures rather than merely inconveniences — a caption interpreting beyond the data, an abstract stronger than the body, a null or weak primary result reported only in passing, missing information the argument depends on, or a limitations treatment that names the study's central threat and then does not carry it into the conclusions. Ordinary prose roughness, stylistic infelicity, venue-convention deviations, and citation formatting do not reach `warn`; they are `pass` with a note at most, and citation formatting is explicitly not mine to score.

[CONTRACT-ACKNOWLEDGED]

### Phase 2 (paper-visible call)

## Devil's Advocate Review

### Strengths (for fairness)

The manuscript asks a real question, and §2 demonstrates genuine field awareness — it names the click-proxy validity problem (Vandermeer, 2023), the goal-orientation moderation debate (Osei, 2020), and the field's causal-overreach pathology (Ibarra, 2023). §3.3's own admission that the median split is "a coarse simplification" and §1's stated commitment to "distinguish the pattern in the data from the causal story" are the marks of an author who knows what the standards are.

### Strongest Counter-Argument

If I held the opposite view — that this paper reports something real about dashboards and retention — I would still be unable to defend it, because the paper's own text refutes it three times over.

Start with the sharpest counter-narrative the paper never addresses: **the reported association is manufactured by the sampling frame, not observed in the world.** §3.2 states that recruitment ran "midway through the term" via a voluntary LMS announcement, and that "students who chose to respond... formed the study sample; those who did not respond were excluded." A student who withdrew in week 3 cannot answer a week-8 announcement. The sample is therefore conditioned on survival past the recruitment window — and retention, the outcome, is measured downstream of that same survival. Add that dashboard use is itself a marker of continued LMS presence, and the r = .24 becomes the expected artifact of a survivorship-filtered sample: both variables are partial functions of "was still around and still logging in." This alternative is *more parsimonious* than the SRL mechanism story — it requires no theory of metacognition, only the recruitment procedure the authors themselves describe — and it fits the presented data at least as well. That satisfies the Stronger Counter-Narrative criterion outright.

Second, **the paper's central claim contradicts the paper's own numbers.** The Abstract reports r = .42; §4.2 reports r = .24 for what is described identically. §4.3 asserts that all 142 students were classified into engagement groups for the exam comparison, and reports t(140) — yet Table 2's own group sizes are 66 + 61 = 127, which yields df = 125, not 140. The perceived-control comparison reports t(156), implying roughly 158 cases, when only 87 respondents answered that item and the full analytic sample is 142. And §4.3 reports t(140) = 1.31 with p = .008 — a t of 1.31 on 140 df corresponds to p ≈ .19 — then narrates that p = .008 result as failing to "reach a comparable level" to a p = .003 result, inverting the significance logic in the same sentence. These are not four typographical slips in one otherwise-coherent dataset; they are mutually incompatible in a way that means no single dataset generates all reported values. The primary quantity is not evaluable.

Third, and most damning for a paper that cites Ibarra (2023) on causal overreach: **the paper commits the exact error it diagnoses.** §5's opening sentence is "dashboard engagement improved course retention... increasing dashboard engagement therefore raises the probability that a student completes the course." §6 concludes "associated with, and raises." These sit at the Discussion's opening and the Conclusion's core — the two most load-bearing positions in any manuscript — and are accompanied by prescriptive advice to institutions "worldwide."

I want to steelman the defense, because it is the only reading that saves the paper: *the causal verbs are careless phrasing; §1 states correlational scope, §5's third paragraph hedges, and §3 concedes measurement limits; the numbers are transcription errors.* I press this seriously and reject it. Carelessness does not survive contact with §6's prescription that dashboard investment "is a dependable strategy for improving retention across programs and disciplines" — a recommendation is a causal claim in the imperative mood, and no editing recovers it as accidental. And "transcription error" is not available as a defense when the errors are *mutually* inconsistent: a single mistyped digit is a transcription error; four sample sizes that cannot coexist (142 / ~158 / 142 / 127) is an analysis that cannot be reconstructed. Notably, the r = .42 → .24 discrepancy runs in exactly one direction — the larger value sits in the Abstract, where readers who go no further will find it. The stated caution is a rhetorical layer, not a constraint the paper's conclusions actually obey.

What survives, if anything? A descriptive report that in one introductory statistics course, students who opened a dashboard more often were somewhat more likely to complete — with the association's magnitude unresolvable from the text as written, and the sample's construction offering a complete explanation for it that does not involve dashboards at all.

### Issue List

#### CRITICAL

| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|----------|---------------------|-----------------------------|
| C1 | 4 (Logic Chain) / Data-Conclusion Mismatch | The Abstract reports r = .42; §4.2 reports r = .24 for the same association. No reconciliation, no indication these are different quantities. The headline effect size differs by a factor of ~1.75 between where readers see it and where it is reported — and the larger value occupies the Abstract. The paper's primary quantity is not evaluable from its own text. | Abstract (¶1) vs §4.2 | — (severity does not rest on a field norm; the paper contradicts itself) | — |
| C2 | 4 (Logic Chain) / Foundation Collapse | Sample sizes are mutually incompatible across four locations: §3.2 states N = 142 analytic sample; §4.3 reports t(156) for a comparison drawn from at most 87 perceived-control respondents; §4.3 states "all 142 students... were classified into engagement groups" and reports t(140), but Table 2's own ns are 66 + 61 = 127 (df = 125). No single dataset produces all four values. This is not a reporting gap — it means the reported analyses cannot be reconstructed, and therefore cannot be revised into correctness by editing. | §3.2; §4.3 (both paragraphs); Table 2 | — | — |
| C3 | 4 (Logic Chain) / Data-Conclusion Mismatch | §4.3 reports t(140) = 1.31, p = .008. That t on 140 df yields p ≈ .19 two-tailed. The same sentence then describes this p = .008 result as not reaching "a comparable level" to a p = .003 result — narrating a *smaller* p as the weaker finding. Whichever number is wrong, the surrounding inferential narration is wrong with it. A reader cannot determine whether the exam comparison was null or significant. | §4.3, ¶2 | — | — |
| C4 | 1 (Core Thesis) / Logic Chain Break | §5 opens "dashboard engagement **improved** course retention... increasing dashboard engagement therefore **raises** the probability"; §6 concludes "associated with, **and raises**." The design is explicitly cross-sectional and observational (§3.1) with no control, no comparison condition, no temporal ordering, and no covariate adjustment. The causal verbs sit at the Discussion's opening sentence and the Conclusion's core claim, and are operationalized as prescriptive advice to institutions. The paper cites Ibarra (2023), *"Causal language in correlational learning analytics: A critical audit,"* in §2 and commits the audited error in §5–§6. | §5 ¶1; §6; against §2 ¶5 and §3.1 | — | — |
| C5 | 1 / 2 (Cherry-Picking, Survivorship) / Stronger Counter-Narrative | Recruitment occurred "midway through the term" (§3.2) via voluntary response; non-responders were excluded. Students who withdrew before the recruitment window are structurally absent from the sample, yet withdrawal is the outcome's negative pole. Both dashboard sessions and retention are partial functions of continued LMS presence. Survivorship-conditioned sampling is a more parsimonious explanation for r = .24 than the SRL mechanism, requires no auxiliary theory, and fits the presented data at least as well. The paper never raises it — not in §3.2, not in §5, not in §5.1. | §3.2; unaddressed in §5.1 | — | — |
| C6 | 2 (Cherry-Picking) / Foundation Collapse of the equity rationale | §2 ¶2 states: "Dashboards have been shown to **reliably** improve outcomes for lower-achieving students... (Ferro & Nakamura, 2021)." The cited source is titled *"When dashboards demotivate: Peer comparison and the lower-achieving student."* The citation is attached to a claim its own title contradicts, and "reliably" imports a certainty §2 ¶1 and ¶5 explicitly say the literature lacks. The manuscript then says "we return to it in the Discussion" and builds the equity-oriented deployment rationale on it. A load-bearing claim rests on a source that appears to say the opposite. | §2 ¶2; References p. Ferro & Nakamura (2021) | — (the defect is internal: citing sentence vs cited title, both present in this manuscript) | — |

#### MAJOR

| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|----------|---------------------|-----------------------------|
| M1 | 5 (Overgeneralization) | §6 generalizes from one introductory statistics course at one institution in one term to "higher education institutions **worldwide**," "retention **across programs and disciplines**," and calls dashboard investment "a **dependable** strategy" and "a practical and **generalizable** lever." §3.1's own text says the design is cross-sectional, single-course, single-term. The inferential scope exceeds the sampled context by several orders of magnitude. | §6; against §3.1 | — | — |
| M2 | 4 (Logic Chain) / hidden assumption | The construct measured is course completion — "remained enrolled and completed the final assessment" (§3.3) — but §6 concludes about "retention across programs and disciplines," which is institutional persistence. These are distinct constructs with distinct determinants. The paper substitutes one for the other without argument, and the substitution is what makes the institutional recommendation appear to follow. | §3.3 vs §6 | — | — |
| M3 | 3 (Confirmation Bias) | The interpretive framing is one-directional throughout. §5 ¶2 reads the result as aligning "with the view that externalized progress cues can support persistence," and reads perceived control as evidence for a "mediating construct" — but no mediation was tested, and the correlational design licenses the reverse reading (students who feel in control use dashboards) equally. §2 raises demotivation (Osei, 2020) and goal-orientation moderation, then §5 ¶2 claims the paper "speak[s] to" that debate without reporting any subgroup or moderation analysis. The paper claims a contribution to a debate its analysis cannot enter. | §5 ¶1–¶2; against §2 ¶3 | — | — |
| M4 | 4 (Logic Chain) / rival explanations unaddressed | Three rival explanations are never named: (a) reverse causation — students on track to complete keep using the dashboard because it shows good news; (b) common cause — prior achievement, conscientiousness, or overall LMS activity drives both dashboard sessions and completion, making dashboard use an *index* rather than a *lever*; (c) general-activity confounding — dashboard sessions may simply be a subset of total LMS activity, which was neither measured nor controlled. §5.1 lists four limitations and omits all three. | §5; §5.1 | — | — |
| M5 | 3 (Confirmation Bias) / structural | §5.1's limitations perform methodological maturity while excluding every limitation that would constrain the conclusions. It names session-count proxying, self-report bias, single-course setting, and dashboard specificity — all real, none disqualifying. It omits: the correlational design's inability to support §5's causal verbs, voluntary-response self-selection, survivorship in the recruitment window, absence of confounding controls, the single-item measure's unestimable reliability, and the median split's cost. A limitations section that concedes the survivable and omits the fatal is a more effective concealment than no limitations section. | §5.1 | — | — |
| M6 | 4 (Logic Chain) / measurement-to-claim gap | *Perceived control* — a single item, "Overall, I feel in control of my learning in this course" (§3.3) — carries the entire SRL mechanism story in §5 ¶1 ("consistent with a self-regulated learning account in which dashboards scaffold monitoring and adjustment"). A single global rating is not a measure of self-regulated learning; no SRL phase (forethought, performance, reflection) named in §1 and §2 is operationalized or measured anywhere. The theoretical framework is invoked but never tested, then cited as if the data supported it. | §3.3; §5 ¶1; against §1 ¶2 | — | — |
| M7 | 4 (Logic Chain) / internal inconsistency | §3.2 states participants "were drawn from the course enrollment using a **random sample**," then the next paragraph describes a voluntary response to an LMS announcement in which "students who chose to respond... formed the study sample." These are incompatible sampling frames. The paper asserts the property (randomness) that would license its inferences while describing the procedure (self-selection) that forecloses them. | §3.2 ¶1 vs ¶2 | — | — |
| M8 | 4 (Logic Chain) / distributional implausibility | Table 1 reports perceived control M = 3.847, SD = 0.62, Min = 1, Max = 5, on 87 integer responses. An SD of 0.62 on a 1–5 integer scale centered at 3.85 is difficult to reconcile with observations at both 1 and 5; the reported three-decimal precision is also unjustified for 87 integer responses. Either the range or the SD is misreported, and the descriptive foundation of the perceived-control analysis is unverifiable. | §4.1; Table 1 | — | — |

#### MINOR

| # | Dimension | Issue Description | Location |
|---|-----------|-------------------|----------|
| m1 | 4 | A Pearson *r* is reported for an association between a continuous predictor and a dichotomously coded outcome (§3.3 codes retention dichotomously). The statistic is not named for what it is, and the reader cannot tell which coefficient was computed. | §3.4; §4.2 |
| m2 | 6 (Alternative Paths) | The paper treats dashboard engagement as the intervention lever without considering alternatives its own §2 implies would be at least as promising: instructor outreach triggered by dashboard signals, early-alert routing to advisors, or dashboard *redesign* (removing the peer-comparison band §2 identifies as potentially demotivating). No justification is given for why "encourage engagement" is the recommended path. | §6; against §2 ¶3 |
| m3 | 8 ("So What?") | §2 ¶5 concedes that "much dashboard research relies on cross-sectional or correlational designs" and that causal language outruns evidence. The paper then supplies another cross-sectional correlational study with causal language. The stated marginal contribution — perceived control — is measured with one item and analyzed descriptively, so it does not supply the differentiating value the paper needs. | §2 ¶5; §5 |
| m4 | 4 | The sessionization rule is defined as "the platform's default" 30-minute inactivity threshold (§3.3), but no platform is named. The primary independent variable's operational definition is therefore not recoverable by any reader. | §3.3 |
| m5 | 7 (Stakeholder Blind Spot — naming only) | Perspectives structurally absent from the framing: students as data subjects (§3.2 states they "were not informed that their dashboard activity data would be analyzed for this study"), students who withdrew before recruitment, and instructors/advisors who would act on dashboard signals. Naming only — elaboration is R3's scope. | §3.2; §6 |
| m6 | 2 | Eight of fifteen listed references (Ainsworth & Devi; Berange; Delacroix & Ohno; Halloran; Kessler & Amadou; Montez; Prakash & Tolliver; Solberg & Whitfield; Wexler & Ojo) are never cited in text. Wexler & Ojo (2020), *"Retention modeling with LMS trace data: A cautionary study,"* is directly on point for this paper's central design and appears only in the list. | References; §2 |

### Ignored Alternative Explanations/Paths

1. **Survivorship-conditioned sampling (strongest).** A mid-term voluntary recruitment window structurally excludes early withdrawers, who are precisely the negative cases of the retention outcome. The sample is conditioned on partial survival; the outcome measures full survival. The observed association is what that filter predicts even if dashboards do nothing. This is more parsimonious than the SRL account and requires only §3.2's own description.

2. **Reverse causation.** Students who are on track — passing assignments, submitting on time — receive favorable information from a dashboard and therefore keep opening it. Students falling behind avoid a display that confirms it (a mechanism §2 ¶3 itself describes via performance-avoidance orientation, then never applies to its own data). Retention status drives dashboard use, not the converse.

3. **Common cause / dashboard use as index, not lever.** Conscientiousness, prior achievement, and general LMS activity all plausibly drive both dashboard sessions and course completion. None was measured or controlled. On this reading dashboard engagement is a *symptom* of the disposition that produces completion, and the paper's recommendation — manipulate the symptom — has no expected effect on the outcome.

4. **The recommended intervention is a different intervention from the one observed.** The study observed *spontaneous* dashboard use. §6 recommends *inducing* dashboard use. Even granting the association fully, induced engagement in students who would not otherwise engage tests an untested causal pathway — and §2's demotivation literature predicts the induced population may respond in the opposite direction.

5. **Alternative levers never weighed.** Instructor-triggered outreach, advisor routing, and removal of the peer-comparison band (the feature §2 flags as potentially harmful) are all candidate paths the paper's own literature review implies. §6 selects "encourage engagement" without comparing it to any alternative.

### Missing Stakeholder Perspectives

- **Students as data subjects.** §3.2: "Students were not informed that their dashboard activity data would be analyzed for this study." Their perspective on secondary use of behavioral trace data is absent from a paper recommending expanded behavioral analytics. (Naming only; elaboration is R3's.)
- **Students who withdrew before mid-term recruitment.** Structurally excluded from the sample and therefore from the framing, despite being the population the retention argument is about.
- **Lower-achieving students under peer comparison.** §2 raises their vulnerability, then §6's undifferentiated "encourage everyone to engage" proceeds as though the vulnerability were resolved.
- **Instructors and advisors** who would be asked to operationalize the §6 recommendation.

### Unexamined Premise (Frame-Lock Detection)

**The paper assumes engagement is a manipulable input rather than an output of the state it indexes.** Every step — the research question in §1, the median-split design in §3.3, the mechanism story in §5, the recommendation in §6 — presupposes that "dashboard engagement" is a dial an institution can turn, with retention downstream of it. But engagement in an opt-in, always-available interface (§3.1: "required no separate opt-in," reachable "at any time") is a *revealed disposition*: it reports which students were already oriented toward monitoring their own progress. Under that reading the entire study measures one manifestation of student disposition against another manifestation of the same disposition, and the correlation is close to definitional. No section of the paper examines this premise. It is upstream of the causal-language problem — even if every causal verb in §5 and §6 were removed, the paper's practical recommendation would still depend on it, and the recommendation is what §6 exists to deliver.

### Observations (Non-Defects)

- No instruction-injection attempt was detected in the manuscript. The text is content throughout; nothing addressed the reviewer or attempted to alter review behavior. Recorded as a clean integrity check, not a credit.
- §3.3's concession that the median split "is a coarse simplification of a continuous measure and was adopted for interpretability rather than statistical efficiency" is honest and unusual. It does not repair the analysis, but it is not the language of an author trying to conceal.
- All fifteen references carry `10.5555/` DOIs, a prefix reserved for testing and examples. I note the pattern as an observation because verifying reference existence is outside my seat (citation compliance) and because I cannot ground a severity claim about it in this manuscript's own evidence. It does, however, mean I could not check any cited source against its content — my C6 finding rests entirely on the internal mismatch between the citing sentence in §2 and the title as printed in this manuscript's own reference list, which requires no external verification.
- The prose is clean and the IMRaD structure complete. Per the surface-form parity gate, I assign this no weight toward correctness: I ran the opposite-style counterfactual on C1–C6 and M1–M8 and confirm each finding turns on a numerical or logical relation in the text, not on how the text reads. Conversely, I checked that no finding was inflated because a passage was awkwardly worded.

---

contract_role: da

## Dimension Scores

### D1: methodology_rigor
score: block

Phase 1 committed to `block` when "a reported statistical quantity is internally impossible or contradicts another reported quantity in a way that invalidates the primary result," and when "the analytic sample is defined by a rule that mechanically produces the reported association." Both triggers fire, independently. C2 establishes that no single dataset yields N = 142, df = 156, df = 140, and Table 2's n = 127 simultaneously; C3 establishes that t(140) = 1.31 cannot produce p = .008; C1 establishes that the headline r is reported at two irreconcilable values. C5 establishes that the mid-term voluntary recruitment window conditions the sample on partial survival while the outcome measures full survival. This is the "unrecoverable primary quantity" condition I named in advance, not a severity import from an external norm — no `[FIELD-NORM UNVERIFIED]` label applies, because the defect is internal contradiction, not a failure to meet a practice standard I would have to source.

### D2: domain_accuracy
score: block

Phase 1 committed to `block` on "a load-bearing factual misrepresentation of prior work — a cited finding's direction or conclusion is reversed or materially overstated and the paper's argument depends on that reading." C6 fires precisely: §2 ¶2 attributes to Ferro & Nakamura (2021) the claim that dashboards "reliably improve outcomes for lower-achieving students," while the reference list prints that source's title as *"When dashboards demotivate: Peer comparison and the lower-achieving student."* The direction appears reversed, "reliably" overstates certainty the manuscript's own §2 ¶1 and ¶5 deny the literature has, and the sentence carries the equity-oriented deployment rationale that §6 cashes out. The mismatch is verifiable inside this manuscript — citing sentence against printed title — so the finding does not depend on external source retrieval. Supporting but not decisive: §2 raises the demotivation and goal-orientation literature and §5 then treats the evidence as one-directionally supportive without moderation analysis (M3).

### D3: argumentative_coherence
score: block

Phase 1 committed to `block` on Logic Chain Break, Data-Conclusion Mismatch, Stronger Counter-Narrative, or "the abstract or conclusion asserts a causal or policy-actionable claim that the design and results cannot license." Three of the four fire. C4: §5 ¶1 and §6 assert causation ("improved," "raises") from a design §3.1 declares cross-sectional and observational, with §6 converting it into prescriptive advice — the strongest form of the trigger I named. C5: survivorship-conditioned sampling is more parsimonious than the SRL account, requires only the paper's own §3.2, and is nowhere addressed — the Stronger Counter-Narrative criterion in full. C1/C3: the reported data do not sustain the stated conclusions, and in the exam comparison actively contradict the narration. M2 compounds it — the conclusion's construct (institutional retention) is not the construct measured (course completion).

### D4: cross_disciplinary_relevance
score: block

Phase 1 committed to `block` when "the paper's conclusion rests on a construct or warrant imported from an adjacent field while stripping the condition that makes it valid there, and the conclusion does not survive restoring the condition." Two imports fail this test. (a) Self-regulated learning is imported from educational psychology as the explanatory mechanism (§1 ¶2, §2 ¶4, §5 ¶1), but no SRL phase is operationalized and the sole measure is one global item (M6); restoring the source field's condition — that SRL is a multi-phase process requiring instrumented measurement — removes the mechanism, and with it §5's interpretation. (b) *Retention* is imported from higher-education persistence research, where it denotes institutional persistence, while §3.3 measures course completion; §6 then generalizes to "retention across programs and disciplines" (M2). Restoring the home discipline's construct boundary invalidates the institutional recommendation, which is the paper's terminal claim. Per contract, a `block` here fires F3 (severity 60), not F1.

### D5: writing_and_structure
score: warn

Phase 1 committed to `warn` for "an abstract stronger than the body, a null or weak primary result reported only in passing, missing information the argument depends on, or a limitations treatment that names the study's central threat and then does not carry it into the conclusions" — and reserved `block` for presentation so defective the central claim cannot be evaluated. I score `warn`, not `block`, and I state where the true home lies for each item. The Abstract carries r = .42 while §4.2 reports r = .24 (C1) — presentationally this is abstract-exceeds-body, but its true home is D1/D3, and I do not double-count severity here. §5.1 lists four survivable limitations and omits every disqualifying one (M5) — a structural concealment, reportable at this dimension. Table 2's group sizes contradict §4.3's stated df (C2), and Table 1's SD/range combination is implausible (M8). The prose itself is clean and the structure complete; per the parity gate I credit neither. Brevity is not scored as a defect. No failure condition in this contract is triggered by D5 alone.

## Failure Condition Checks

### F1
fired: true

Predicate: "any mandatory dimension scores 'block'." Mandatory dimensions are D1, D2, D3. All three score `block`. Severity 90.

### F2
fired: true

Predicate: "two or more mandatory dimensions score 'warn' or worse." D1, D2, and D3 all score `block`, which is worse than `warn` — three mandatory dimensions satisfy the predicate. Severity 70. (The `cross_reviewer_quantifier` "majority" is panel-level machinery for the synthesizer; I evaluate the expression against my own scores only.)

### F3
fired: true

Predicate: "any high-priority dimension scores 'block'." D4 is the sole `high` priority dimension and scores `block`. Severity 60.

### F0
fired: false

Predicate: "every mandatory dimension scores 'pass'." D1, D2, and D3 all score `block`. Not satisfied.

## Review Body

This manuscript fails at three independent levels, and each failure is sufficient on its own.

**The reported analyses cannot be reconstructed.** The Abstract's r = .42 and §4.2's r = .24 describe the same association at values differing by a factor of 1.75, with the larger figure placed where the most readers will encounter it. Four incompatible sample sizes appear across §3.2, §4.3, and Table 2 — 142, ~158 implied by t(156), 142 asserted alongside t(140), and 127 summed from Table 2's own rows. A t(140) = 1.31 is reported with p = .008 when that statistic yields p ≈ .19, and the same sentence then treats p = .008 as the weaker result relative to p = .003. I pressed the most generous available reading — that these are transcription errors in a sound analysis — and it does not survive: a transcription error is a single mistyped value, whereas these values are mutually exclusive. No editorial revision reconciles them. Only the underlying data can, and the manuscript supplies no data-availability statement.

**The conclusions are causal; the design is not.** §3.1 declares an observational, cross-sectional design with no control condition, no covariate adjustment, and no temporal ordering between predictor and outcome. §5's opening sentence nonetheless states that "dashboard engagement improved course retention" and that "increasing dashboard engagement therefore raises the probability" of completion; §6 states "associated with, and raises," then instructs institutions worldwide that dashboard investment "is a dependable strategy." The placement is the aggravating fact: these are the Discussion's first sentence and the Conclusion's core, the two positions a reader is most likely to carry away, and the claim is issued as prescription. §2 ¶5 cites Ibarra (2023) on causal language outrunning evidence in exactly this literature; §1 ¶3 promises to "distinguish the pattern in the data from the causal story." The manuscript therefore states the standard, cites the audit of its violation, and then violates it — the hedging in §1 and §5 ¶3 functions as a rhetorical layer that the conclusions do not obey.

**A rival explanation the paper never names fits the data better.** §3.2 describes a mid-term LMS announcement to which students volunteered; non-responders were excluded. Students who withdrew before that window could not respond. The sample is thus conditioned on survival past mid-term, while retention — the outcome — measures survival to the final assessment. Dashboard sessions, meanwhile, are a function of continued LMS presence. Both variables partially measure the same thing: still being there. This account explains r = .24 without invoking metacognition, self-regulation, or any dashboard property; it draws entirely on the recruitment procedure the authors themselves describe. It is more parsimonious than the SRL story and fits the data at least as well. §5.1 does not raise it, nor reverse causation, nor common causes such as prior achievement or general LMS activity. §3.2 additionally asserts a "random sample" one paragraph before describing voluntary response — the paper claims the sampling property that would license its inferences while describing the procedure that forecloses them.

Three further problems compound these. The SRL framework that supplies the paper's entire explanatory mechanism is measured by one global item ("Overall, I feel in control of my learning in this course"); no forethought, performance, or reflection phase is operationalized, so §5 ¶1's claim of consistency with an SRL account has nothing behind it. The §2 attribution to Ferro & Nakamura (2021) — that dashboards "reliably improve outcomes for lower-achieving students" — is attached to a source whose title, as printed in this manuscript's own reference list, is *"When dashboards demotivate: Peer comparison and the lower-achieving student"*; the equity rationale for institutional deployment rests on that sentence. And §5.1 performs limitations while omitting the correlational design's causal ceiling, self-selection, survivorship, absent controls, single-item unreliability, and the median split's cost — every limitation that would constrain §6's recommendation is the limitation that is missing.

Beneath all of this sits an unexamined premise: that dashboard engagement is a lever institutions can pull rather than an output of the disposition it indexes. In an always-available, opt-in-free interface (§3.1), engagement reports which students were already monitoring their progress. On that reading the study correlates one expression of student disposition with another, and the recommendation in §6 — induce engagement — proposes an intervention this study never observed and whose effect §2's own demotivation literature predicts may run negative in the induced population.

What could be salvaged: a scope-honest descriptive report of one introductory statistics course, with the numbers reconciled against the underlying data, an association framed as association, the sampling frame's survivorship acknowledged as a candidate explanation, the Ferro & Nakamura attribution corrected, and §6's institutional prescription withdrawn. That is a different manuscript, and it requires the data — not editing — to build.

## Editorial Decision

F1 fired at severity 90, the highest among fired conditions (F2 at 70, F3 at 60), so F1's action controls.

editorial_decision=reject_or_major_revision

# PART 3 — EDITORIAL SYNTHESIS

# Editorial Synthesis — Sprint Contract `reviewer/reviewer_full/v1`

**Contract:** `reviewer/reviewer_full/v1` · `baseline_version` v3.6.2 · `mode` `reviewer_full` · `stage` `reviewer_full_review` · `generated_at` 2026-07-25T08:00:00Z
**Panel cardinality:** `panel_size` = 5; usable Phase 2 outputs = 5 (EIC, methodology, domain, perspective, DA). Invariant satisfied — no `[PANEL-SHRUNK]`.
**Expression parsing:** F1 → §9 pattern 1 (bare `mandatory`); F2 → §9 pattern 2; F3 → §9 pattern 1 (`high-priority` variant); F0 → §9 pattern 3. All four recognised — no `[EXPRESSION-UNRECOGNISED]`.
**Reviewer self-consistency:** each card's `## Editorial Decision` matches the action derivable from its own `## Failure Condition Checks` under the §8 step-3 precedence rule — no `[REVIEWER-SELF-INCONSISTENT]`.

## Step 1 — Scoring matrix

Dimensions resolved by `id`. Array order: EIC, methodology (R1), domain (R2), perspective (R3), DA.

| Dimension (`id`, priority) | EIC | R1 | R2 | R3 | DA | matrix array |
|---|---|---|---|---|---|---|
| D1 `methodology_rigor` (mandatory) | block | block | block | block | block | `[block, block, block, block, block]` |
| D2 `domain_accuracy` (mandatory) | block | block | block | block | block | `[block, block, block, block, block]` |
| D3 `argumentative_coherence` (mandatory) | block | block | block | block | block | `[block, block, block, block, block]` |
| D4 `cross_disciplinary_relevance` (high) | warn | warn | warn | **block** | **block** | `[warn, warn, warn, block, block]` |
| D5 `writing_and_structure` (normal) | warn | warn | **block** | warn | warn | `[warn, warn, block, warn, warn]` |

## Step 2 — Failure-condition evaluation

| `condition_id` | severity | quantifier | threshold (N=5) | per-reviewer predicate [EIC, R1, R2, R3, DA] | holds for | `fired` |
|---|---|---|---|---|---|---|
| F1 — `any mandatory dimension scores 'block'` | 90 | `any` | ≥ 1 | [T, T, T, T, T] | 5 / 5 | **true** |
| F2 — `two or more mandatory dimensions score 'warn' or worse` | 70 | `majority` | ≥ ⌊5/2⌋+1 = 3 | [T, T, T, T, T] (3 mandatory `block` each; `block` > `warn`) | 5 / 5 | **true** |
| F3 — `any high-priority dimension scores 'block'` | 60 | `any` | ≥ 1 | [F, F, F, T, T] (D4 is the sole `high` dimension) | 2 / 5 | **true** |
| F0 — `every mandatory dimension scores 'pass'` | 10 | `all` | 5 / 5 | [F, F, F, F, F] | 0 / 5 | false |

## Step 3 — Precedence and decision

Fired: F1 (90), F2 (70), F3 (60). Highest severity governs; no tie. F1's `action` is emitted verbatim.

fired_conditions: [F1, F2, F3]

editorial_decision=reject_or_major_revision

---

# Editorial Decision Package

## Part 1: Editorial Decision Letter

### Manuscript Information

- **Title**: *Dashboard Engagement and Course Retention* (as quoted from the manuscript by the EIC; the cards do not reproduce the full submitted title string)
- **Manuscript ID**: not supplied to this synthesis
- **Submission Date**: not supplied to this synthesis
- **Decision Date**: 2026-07-25
- **Review Round**: Round 1
- **Journal**: *Journal of Learning Analytics* (per the EIC seat's declared identity)

### Review Panel Provenance (#540)

No provenance stamp was supplied by the dispatching layer with this synthesis input. The #540 block is mandatory in `reviewer_full` and its statement must not be inferred, so none of the three permitted statements is selected here. **Consequence for the reader:** it cannot be established from the materials on file whether the Reviewer 2 slot ran on a second model family or on the primary family, and therefore the single-family correlated-blind-spot caveat (Ren et al. 2026, arXiv:2607.13104 §5.2) cannot be ruled out. Cross-family splits, if any, are visible by inspection in the Step 1 panel matrix above; no cross-family aggregate is computed.

---

### Decision

#### Reject

**Subtype:** Fundamental Flaw — *Resubmit Encouraged* (as a re-specified study, not as a revision of this text).

The contract's governing action is a range (F1: `reject_or_major_revision`). Within that range all four scoring seats and the Devil's Advocate independently land on the reject side, each for the same two reasons: the reported analyses cannot be reconstructed from any single dataset, so there is no established finding for a revision to be scoped toward; and the trace-data governance gap is not addressable by editing the manuscript. One conditional branch is preserved explicitly in the Decision Rationale below.

---

### Top Blocking Issues (3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| 1 | Reported statistics do not reconstruct to any single dataset, so the headline quantity is not evaluable | EIC, R1, R2, R3, DA | Abstract *r* = .42 vs §4.2 *r* = .24; §4.3 *t*(156) and *t*(140) vs Table 2's 66 + 61 = 127; *t*(140) = 1.31 reported with *p* = .008; §4.1 *M* = 3.847 from 87 integer responses | R1 (with R5) |
| 2 | Causal and prescriptive claims from an observational design with no adjustment, and a limitations section that omits every disqualifying limitation | EIC, R1, R2, R3, DA | §5 ¶1 "dashboard engagement **improved** course retention… therefore **raises** the probability"; §6 "associated with, **and raises**… a dependable strategy"; §5.1's four listed limitations | R3, R4 |
| 3 | Behavioural trace data analysed with no ethics record, no consent basis, and no linkage/de-identification account | EIC, R1, R2, R3 | §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study"; no ethics, data-availability, or COI statement anywhere | R2 |

---

### Reviewer Summary (Step 1a)

| Reviewer | Role identity | Overall recommendation | Confidence | # Questions | # Minor issues |
|---|---|---|---|---|---|
| EIC | Editor-in-Chief, *Journal of Learning Analytics*; fit / originality / publishability screen | Reject | 4 | 7 | 9 |
| Reviewer 1 | Quantitative methodologist, educational measurement; observational inference for dichotomous outcomes | Reject (conditional on data supply — see card) | 5 | 10 | 7 |
| Reviewer 2 | Senior higher-education researcher; undergraduate persistence and retention theory | Reject | 4 | 7 | 6 |
| Reviewer 3 | Director of learning technology and student data governance; practitioner-scholar | Reject (resubmission as re-scoped study) | 4 | 5 | 7 |
| DA | Devil's Advocate (adversarial seat) | — (the DA card carries no `Overall Recommendation` or `Confidence` field; neither is required by the Phase 2 grammar for this seat) | — | — | 6 CRITICAL / 8 MAJOR / 6 MINOR |

**Key Strengths** (converging across all five cards): §2 is a genuinely balanced literature review that names the click-proxy validity problem (Vandermeer, 2023), the demotivation and goal-orientation strand (Osei, 2020), and the causal-overreach audit (Ibarra, 2023); §3.3's operational definitions are specific enough to audit; §3.3 and §2 concede their own measurement compromises rather than hiding them; the dashboard was universal from week 1 with no opt-in, which genuinely closes the access-selection pathway (R1); and §5's third paragraph already contains the correctly calibrated reading of the finding.
**Key Weaknesses** → decomposed in Step 1b below.

---

### Consensus Analysis

#### Step 1b — Weakness sub-claim inventory

Positions are recorded in matrix form rather than one row per `(sub_claim, reviewer)` pair, so that all 5 × 37 positions — including every `not-mentioned` — remain visible without a 180-row table; no position information is lost relative to the row-per-pair form. Codes: **R** = raised · **C** = corroborated · **D** = disputed · **—** = not-mentioned. Consensus counting uses the 4 non-DA seats only; the DA column is recorded for traceability and excluded from the count. `conf` = highest Confidence Score among agreeing seats (EIC 4 / R1 5 / R2 4 / R3 4).

| SC | parent_weakness | EIC | R1 | R2 | R3 | DA | evidence_pointer | conf | disposition |
|---|---|---|---|---|---|---|---|---|---|
| SC-1 | Statistical reconstruction failure | R | R | R | C | R | Abstract *r*=.42 vs §4.2 *r*=.24 — EIC W2; R1 check 1; R2 D5(b); R3 D5 (routed to R1); DA C1 | 5 | CONSENSUS-4 |
| SC-2 | Statistical reconstruction failure | R | R | R | C | R | 142 / *t*(156) / *t*(140) / Table 2's 127 — EIC W2; R1 checks 3–5; R2 argument-logic; R3 D5; DA C2 | 5 | CONSENSUS-4 |
| SC-3 | Statistical reconstruction failure | C | R | — | — | R | *t*(140)=1.31 ⇒ *p*≈.19; *t*(156) impossible on 87 respondents — R1 checks 3–4; EIC D1; DA C3 | 5 | corroborated finding (2/4) |
| SC-4 | Inverted significance narration | R | R | R | — | R | §4.3 narrates *p*=.008 as weaker than *p*=.003 against declared α=.05 | 5 | CONSENSUS-3 (silent: R3) |
| SC-5 | Impossible descriptive | — | R | — | — | C | §4.1 *M*=3.847 × 87 = 334.69, non-integer — R1 check 6 | 5 | single-reviewer finding (R1) |
| SC-6 | Over-precision | R | R | R | R | R | Three decimals on a 1–5 integer single item | 5 | CONSENSUS-4 |
| SC-7 | Outcome-conditioned comparison | — | R | R | — | — | Table 2's 127 vs §4.3's "all 142"; non-retained students sat no final ⇒ collider | 5 | corroborated finding (2/4) |
| SC-8 | Statistical reporting completeness | — | R | — | — | — | No effect sizes, no CI, no power, no assumption tests, no software; exam test ~25% power | 5 | single-reviewer finding (R1) |
| SC-9 | Outcome never described | — | C | R | — | — | Retention base rate reported nowhere; retention in no table | 4 | corroborated finding (2/4) |
| SC-10 | Causal overreach | R | R | R | R | R | §5 ¶1 "improved… raises"; §6 "and raises" from §3.1's cross-sectional design | 5 | CONSENSUS-4 |
| SC-11 | Unlicensed prescription | R | R | R | R | R | §6 "dependable strategy", "institutions worldwide", "generalizable lever" | 5 | CONSENSUS-4 |
| SC-12 | Self-refutation | R | R | R | R | R | §2 cites Ibarra (2023); §1 pledges to separate pattern from causal story; §5/§6 do the opposite | 5 | CONSENSUS-4 |
| SC-13 | Limitations omission | R | R | R | R | R | §5.1 lists four survivable limitations, omits causal ceiling / selection / survivorship / controls / single item / median split | 5 | CONSENSUS-4 |
| SC-14 | Construct substitution | R | R | R | R | R | §3.3 course completion → §6 "retention across programs and disciplines"; retention/persistence/completion interchangeable | 5 | CONSENSUS-4 |
| SC-15 | Sampling self-contradiction | R | R | R | C | R | §3.2 "random sample" vs "students who chose to respond… formed the study sample" | 5 | CONSENSUS-4 |
| SC-16 | Survivorship in recruitment | R | R | R | R | R | Mid-term announcement cannot reach early withdrawers; sample filtered on near-outcome | 5 | CONSENSUS-4 |
| SC-17 | No confounding control | R | R | R | R | R | §3.4 reports no covariates; prior achievement and total LMS activity unmeasured | 5 | CONSENSUS-4 |
| SC-18 | Un-landmarked exposure | — | R | — | — | C | Sessions counted "during the term"; withdrawn students mechanically accrue fewer | 5 | single-reviewer finding (R1) |
| SC-19 | Reverse causation | — | R | R | R | R | On-track students keep opening a dashboard that shows good news; never raised in §5.1 | 5 | CONSENSUS-3 (silent: EIC) |
| SC-20 | Citation–claim inversion | R | — | R | C | R | §2 "reliably improve outcomes for lower-achieving students (Ferro & Nakamura, 2021)" vs listed title *When dashboards demotivate* | 4 | CONSENSUS-3 (silent: R1) |
| SC-21 | Reference identifiers | R | — | **D** | R | (obs.) | All 15 entries carry `10.5555/` DOIs across six differently-named journals | 4 | **[SPLIT]** — severity |
| SC-22 | Uncited references | R | — | R | C | R | 8–9 of 15 listed entries never appear in text | 4 | CONSENSUS-3 (silent: R1) |
| SC-23 | Abstract misstates measurement | R | R | R | R | R | Abstract: "we measured… self-regulated learning behavior"; §3.3 has one perceived-control item | 5 | CONSENSUS-4 |
| SC-24 | SRL as ornament | R | R | R | R | R | No SRL phase operationalized; §2's own "only when learners possess the regulatory strategies" boundary abandoned | 5 | CONSENSUS-4 |
| SC-25 | Estimator/dichotomization | — | R | — | — | R | Median split on a right-skewed count; Pearson *r* on a dichotomous outcome, point-biserial unnamed; logistic model indicated | 5 | single-reviewer finding (R1) |
| SC-26 | Trace-data governance | R | R | C | R | R | §3.2 "Students were not informed…"; no ethics record, consent basis, linkage or de-identification account | 5 | CONSENSUS-4 |
| SC-27 | Missing declarations | R | R | R | R | — | No data-availability, conflict-of-interest, or funding statement | 5 | CONSENSUS-4 |
| SC-28 | Deployment unreproducible | R | R | R | R | — | Peer-comparison band's norm group, framing, opt-out unspecified; no interface figure | 5 | CONSENSUS-4 |
| SC-29 | Measure unreproducible | R | R | — | R | R | Sessionization attributed to "the platform's default"; platform unnamed; inactivity scope ambiguous | 5 | CONSENSUS-3 (silent: R2) |
| SC-30 | Undefined measure | R | R | — | R | — | Final exam score in Table 1 and §4.3, absent from §3.3 Measures | 5 | CONSENSUS-3 (silent: R2) |
| SC-31 | Unknown denominator | — | R | R | R | — | §3.1 "several hundred students"; response and coverage rate unknowable | 5 | CONSENSUS-3 (silent: EIC) |
| SC-32 | No data or code | R | R | — | — | C | No data-availability statement, no analysis script, software unnamed | 5 | corroborated finding (2/4) |
| SC-33 | "Who benefits" claim unsupported | R | R | R | R | R | §5 claims to address who benefits; no subgroup or moderation analysis reported | 5 | CONSENSUS-4 |
| SC-34 | Contribution insufficient | R | — | R | R | R | §2 concedes the literature already leans on cross-sectional correlational designs | 4 | CONSENSUS-3 (silent: R1) |
| SC-35 | Wrong intervention | R | C | R | R | R | Study observed voluntary use; §6 recommends inducing use | 5 | CONSENSUS-4 |
| SC-36 | No student-side consequences | C | — | C | **R** | R | §6 recommends intervening on students with no equity, privacy, demotivation, or labelling analysis | 4 | **[SPLIT]** — severity |
| SC-37 | Abstract not a faithful summary | R | R | R | C | R | Abstract's headline value, "self-regulated learning behavior", omitted design, "promising lever" | 5 | CONSENSUS-4 |

**Decomposition discipline check:** every sub-claim above traces to a claim at least one reviewer actually made; no sub-claim was authored by this synthesis.

#### Step 1c — Surface-form parity check (#216)

The five cards differ markedly in register: R1 and the DA argue in dense numeric-technical prose; R3 argues largely in practitioner and governance language with an explicit statement of outsider status; R2 attaches `[FIELD-NORM UNVERIFIED]` tags rather than asserting severities. I ran the opposite-style counterfactual on every sub-claim whose weight is not unanimous — SC-3, SC-5, SC-7, SC-8, SC-9, SC-18, SC-25, SC-32, SC-36 — asking whether the weight would change if the same substance were rewritten in the other seat's register. Two results:

- **No weight was reduced for informal or hedged phrasing.** SC-36 arrives in the least technical wording on the panel and carries R3's dimension-level `block`; it is arbitrated on substance and expertise, not on polish. R2's severity abstentions (SC-21, SC-26) were read as abstentions, not as weak evidence: on SC-26 R2 explicitly insists the finding "must not be lost between seats," which is corroboration of existence, so SC-26 counts 4/4.
- **No weight was added for technical specificity.** R1's arithmetic sub-claims (SC-3, SC-5, SC-8, SC-18, SC-25) gain their weight from the reconstruction R1 shows against the manuscript's own reported values and from Confidence 5 in R1's declared lane — not from the presence of formulae. Where R1 stands alone (SC-5, SC-8, SC-18, SC-25) the label remains *single-reviewer finding*; the technical register did not promote any of them to a consensus label.

No sub-claim was marked unevaluable on wording grounds. Authorship was not a weighting input.

#### Points of Agreement (Consensus)

**[CONSENSUS-4]** — all four scoring seats agree on the sub-claim and the recommended action:

1. **Causal verbs occupy the manuscript's two most load-bearing sentences** (SC-10, SC-12). §5 opens "dashboard engagement **improved** course retention… increasing dashboard engagement therefore **raises** the probability"; §6 states "associated with, **and raises**." §3.1 declares the design observational and cross-sectional; §1 pledged to "distinguish the pattern in the data from the causal story"; §2 cites Ibarra (2023) on precisely this failure. All four seats treat this as a structural contradiction rather than a phrasing slip, and note that §5's third paragraph already contains the calibrated version.
2. **The Conclusion's prescription is unlicensed and mis-targeted** (SC-11, SC-14, SC-35). One introductory statistics course, one term, one dashboard, one volunteer sample → "a dependable strategy… for higher education institutions worldwide," "retention across programs and disciplines." Course completion is silently substituted for institutional retention, and voluntary use is silently substituted for induced use.
3. **§5.1 omits every limitation that would constrain the conclusions** (SC-13). Four real but survivable limitations are listed; the correlational design's causal ceiling, volunteer self-selection, mid-term survivorship, the absence of confounding control, the single item's unestimable reliability, and the median split are all absent. Three seats state independently that this is worse than no limitations section.
4. **Selection is unaddressed on both axes** (SC-15, SC-16, SC-17). §3.2 describes the sample as both random and volunteer; a mid-term announcement cannot reach students who already withdrew, so the analytic sample is filtered on something close to the outcome; and no covariate of any kind is fitted.
5. **The headline statistics do not reconstruct** (SC-1, SC-2). *r* = .42 and *r* = .24 cannot both describe the same association; 142, ≥158, 140 and 127 cannot all be the same sample.
6. **Self-regulated learning is claimed as measured and is not** (SC-23, SC-24). The Abstract states SRL behaviour was measured; §3.3's only self-report instrument is one perceived-control item; no SRL phase is operationalized.
7. **The "who benefits" contribution claim has no supporting analysis** (SC-33). No subgroup or moderation analysis is reported anywhere.
8. **Trace-data governance is absent** (SC-26, SC-27). §3.2 records that students were not informed; there is no ethics approval, no consent basis for the log analysis, no account of how survey responses were linked to individual LMS records, and no data-availability, conflict-of-interest, or funding statement.
9. **The deployment cannot be replicated** (SC-28). The peer-comparison band — the feature §2 itself identifies as potentially demotivating — is named but never specified.
10. **The Abstract is not a faithful summary of the Results** (SC-37, SC-6), and the title is the most accurate sentence in the manuscript.

**[CONSENSUS-3]** — three seats agree, the fourth is **silent** (not opposed):

1. **§4.3 inverts its own significance logic** — narrating *p* = .008 as failing to reach a level comparable to *p* = .003 against a declared α = .05 (SC-4; silent: **R3**, who routed reconstruction of the reported statistics to R1).
2. **Reverse causation is never entertained** — on-track students keep opening a dashboard that shows good news (SC-19; silent: **EIC**, whose card raises confounding and self-selection but not reverse causation by name).
3. **The Ferro & Nakamura (2021) attribution inverts its own listed title**, and carries the equity rationale §2 promises to return to (SC-20; silent: **R1**, whose lane is methodology).
4. **Eight to nine of fifteen listed references are never cited in text** (SC-22; silent: **R1**). The count itself must be verified against the list: the EIC's prose says eight while enumerating nine names; R2 states nine and enumerates nine.
5. **The sessionization rule is unreproducible** — "the platform's default," platform unnamed, inactivity scope ambiguous (SC-29; silent: **R2**).
6. **The final exam measure is analysed but never defined in §3.3** (SC-30; silent: **R2**).
7. **The enrollment denominator is given only as "several hundred,"** so the response and coverage rates are unknowable (SC-31; silent: **EIC**).
8. **The contribution does not clear the bar for another correlational dashboard study** on the manuscript's own account of the literature (SC-34; silent: **R1**).

**Corroborated findings (2/4, no conflict)** — action-bearing, below the consensus label: SC-3 (the *p* = .008 / *t*(156) arithmetic, EIC + R1); SC-7 (Table 2's 127 implies the exam comparison is conditioned on the outcome, R1 + R2); SC-9 (retention base rate reported nowhere, R1 + R2); SC-32 (no data or code deposit, EIC + R1).

**Single-reviewer findings** — each from R1 at Confidence 5, in R1's declared primary lane, therefore carried at full weight: SC-5 (*M* = 3.847 arithmetically unattainable); SC-8 (no effect sizes, CIs, power, assumption testing, or named software; the exam comparison is uninformative rather than weak, at ~25% achieved power); SC-18 (un-landmarked exposure window makes the association partly definitional); SC-25 (median split and the un-named point-biserial / missing logistic specification).

#### Points of Disagreement

**Disagreement 1 — Severity of the reference-identifier finding (SC-21)**

- **EIC view**: all fifteen references carry `10.5555/` DOIs, a prefix reserved for test and example registrations that resolves to nothing; combined with the eight uncited entries and the one checkable citation being attached to the inverse of its source's thesis, "the citation base cannot be accepted as verified." Treated as a fit-level integrity bar, not a formatting slip.
- **R2 view**: the uncited proportion is checkable inside the manuscript, but the inference that a shared prefix across six differently-named journals indicates placeholder or non-registered identifiers "rests on DOI-registry practice I cannot verify from session materials `[FIELD-NORM UNVERIFIED]`" — reported as an observation warranting editorial verification, with severity deliberately unassigned. R3 records the same observation; the DA likewise declines to ground a severity claim.
- **Disagreement type**: Severity disagreement.
- **Editor's Resolution**: R2's sequencing governs the required *action*; the EIC's judgment governs the *consequence if verification confirms*. The authors must supply resolvable identifiers for all fifteen entries and either cite or remove the uncited ones (roadmap item **R6**, Priority 1). If the identifiers do not resolve, the reference list stands as unverified at the fit level per the EIC's position, with no further author opportunity needed to establish that.
- **Resolution Rationale**: Evidence first — R2 is correct that no seat verified registry practice from the materials on file, so a severity asserted on that inference would outrun the panel's evidence. Conservative principle — the author must respond either way, so nothing is lost by sequencing verification ahead of severity. This arbitration does not affect the decision, which is over-determined by SC-1/SC-2 and SC-26.

**Disagreement 2 — Severity of the missing student-side consequence analysis (SC-36, D4)**

- **R3 view** (`block` on D4): §6 issues an actionable recommendation about intervening on students at institutional scale with no equity analysis of who has the access and time to engage, no privacy or surveillance discussion in a study that analysed traces without notice, no engagement with the demotivation risk the manuscript itself raises, and nothing on the self-fulfilling effect of engagement-based flagging. The student appears throughout as a data source and never as a party. R3 additionally holds the deployment under-specification to be a practical failure of reach.
- **EIC / R2 view** (`warn` on D4): both explicitly reserved `block` on this dimension for genuine failures of reach rather than narrowness — the EIC because the constructs are definable from the text and all three of the journal's constituencies can determine what was measured; R2 because §3.3 does define the outcome and §5.1 does state boundary conditions, and because the manuscript declines to engage adjacent scholarship rather than misrepresenting it. R1 is silent on the sub-claim and scores D4 `warn` on other grounds (unstated modality, generic transferability discussion).
- **Disagreement type**: Severity disagreement, rooted in a perspective difference — R3 reads as the person who would be asked to act on the paper and to have approved it; the EIC and R2 read as the people who would place it in a literature.
- **Editor's Resolution**: R3's severity stands for the D4 dimension score, and SC-36 is carried into the roadmap as a Priority 1 required item (**R10**). All three seats converge on the same operational remedy — either add the student-consequence analysis at the point of recommendation, or withdraw the recommendation — so the divergence changes the dimension score and not the work required.
- **Resolution Rationale**: Expertise first — student data governance and the practical consequences of deployment recommendations are R3's declared primary lane, and D4's own definition ("implications are accessible to adjacent-field readers; interdisciplinary claims are substantiated") reaches the substance R3 names. Conservative principle — the author must respond regardless. Mechanically, this arbitration only determines whether F3 (severity 60) fires as a subordinate condition; F1 at severity 90 governs the decision either way.

**Disagreement 3 — Dimension attribution of the reporting defects (D5)**

- **R2 view** (`block` on D5): the unreconciled *r*, the §4.3-vs-Table 2 contradiction, the absence of the outcome from every table, and the unauditable reference base make the evidentiary base unreadable at the presentation layer.
- **EIC / R1 / R3 / DA view** (`warn` on D5): the same defects have their true home in D1/D3; the DA states explicitly that it does not double-count severity at D5, and the EIC records that it is not scoring the manuscript's brevity as a defect.
- **Disagreement type**: Severity disagreement (dimension attribution).
- **Editor's Resolution**: No arbitration required and none performed. D5 is `normal` priority and no failure condition in this contract references it, so the attribution has no mechanical consequence; the underlying sub-claims (SC-1, SC-2, SC-7, SC-9, SC-21, SC-22) are already labelled CONSENSUS-4 or CONSENSUS-3 and carried at Priority 1.
- **Resolution Rationale**: Recording the divergence preserves it for the author without introducing an aggregation rule the contract does not authorise.

#### Devil's Advocate Critical Issues (tracked independently of the consensus count)

Every DA CRITICAL finding is corroborated by at least one scoring seat; none is orphaned.

| DA finding | DA's argument | Corroborated by | EIC's assessment | Required author response |
|---|---|---|---|---|
| **C1** — headline *r* reported at two values | Abstract *r* = .42 against §4.2's *r* = .24, differing by a factor of ~1.75, with the larger value placed where most readers stop; the primary quantity is not evaluable | EIC, R1, R2, R3 (SC-1) | Valid, and the EIC's own card makes it a first-order defect: "An abstract that cannot be reconciled with its own results section is a first-order defect, not a polish item" | State which value is the estimate and what analysis produced the other; supply the output |
| **C2** — four incompatible sample sizes | 142 / ~158 implied by *t*(156) / 142 asserted alongside *t*(140) / 127 summed from Table 2; no single dataset yields all four, so the analyses cannot be revised into correctness by editing | EIC, R1, R2, R3 (SC-2) | Valid; the EIC treats it as "a reconstruction failure, not a copy-edit matter" and makes it the stated basis for rejection over major revision | Identify the analytic sample for every reported test and reconcile all four values against the deposited data |
| **C3** — *t*(140) = 1.31 with *p* = .008, then narrated as the weaker result | The statistic yields *p* ≈ .19; whichever number is wrong, the inferential narration is wrong with it, and a reader cannot tell whether the exam comparison was null or significant | EIC, R1 (SC-3); R2 on the narration (SC-4) | Valid; the EIC independently flags the inversion of significance logic | Report the correct *t*, *df*, and *p*, and rewrite the narration against the declared α |
| **C4** — causal verbs in the two most load-bearing positions | §5 ¶1 and §6 assert causation from a design §3.1 declares cross-sectional, operationalized as prescriptive advice; the paper cites Ibarra (2023) on this exact error. The DA steelmans "careless phrasing" and rejects it, because a recommendation is a causal claim in the imperative mood | EIC, R1, R2, R3 (SC-10, SC-12) | Valid, and the EIC reaches the same conclusion about carelessness: the calibrated sentence exists in §5 ¶3, so the stronger verb was a choice, not an accident | Remove the causal verbs; withdraw or reframe the prescription; state what warrants any causal reading |
| **C5** — survivorship-conditioned sampling as a stronger counter-narrative | A mid-term voluntary window cannot recruit early withdrawers; retention measures survival to the final; dashboard sessions are a function of continued LMS presence. Both variables partly measure "still being there," which explains *r* = .24 with no theory of metacognition — more parsimonious than the SRL account and drawn entirely from §3.2 | EIC, R1, R2, R3 (SC-16) | Valid; the EIC's card states the same mechanism could "alone… manufacture the association" | Address survivorship as a first-order threat; re-estimate on full-cohort data |
| **C6** — equity rationale rests on an inverted citation | §2's "reliably improve outcomes for lower-achieving students (Ferro & Nakamura, 2021)" against the listed title *When dashboards demotivate*; "reliably" imports certainty §2 elsewhere denies; the mismatch is verifiable inside the manuscript with no external retrieval | EIC, R2, R3 (SC-20) | Valid; the EIC treats it as a load-bearing citation attached to the inverse of its source's thesis | Re-read the source, restate what it argues, rebuild the equity rationale on it |

**DA frame-lock finding (unexamined premise)** — engagement is treated throughout as a manipulable input rather than as an output of the disposition it indexes; in an always-available, opt-in-free interface, engagement is a revealed disposition, so the study may correlate one expression of student disposition with another. Corroborated in substance by R3 (SC-35) and by the EIC's Significance section ("§6 treats engagement as a manipulable lever, but what was observed is the behaviour of students who chose to open a dashboard"). **The author must respond to this premise directly**, because — as the DA notes — it survives removal of every causal verb and still undercuts §6.

**DA MAJOR finding with a severity divergence (M8)** — the DA holds that *M* = 3.847, *SD* = 0.62, Min = 1, Max = 5 on 87 responses means "either the range or the SD is misreported." R1, the seat that owns distributional arithmetic, judges the SD/range combination "distributionally strained though not impossible" and locates the impossibility in the mean itself. **Resolution**: R1's narrower reading governs the claim's severity (expertise first); the author must nonetheless report the actual sum of responses, the actual *n*, the *SD*, and the observed range, which resolves both readings at once (roadmap item **R1**).

---

### Decision Rationale

The decision is Reject, and the reason is that this manuscript's two governing defects are not addressable by revising the text.

The first is reconstruction. Four seats and the DA converge on the same finding: the Abstract's *r* = .42 and §4.2's *r* = .24 cannot both describe one association; 142, ≥158, 140 and 127 cannot all be one sample; *t*(140) = 1.31 does not yield *p* = .008 at either candidate *df*; and *M* = 3.847 is unattainable from 87 integer responses. R1 (Confidence 5, in lane) shows that Table 2's own descriptives reproduce the reported *t* to three decimals at *df* = 125, which suggests the analysis ran on 127 students — most plausibly because the fifteen non-retained students had no final exam score, in which case the exam comparison silently conditions on the outcome. The DA pressed the most generous reading, that these are transcription errors in a sound analysis, and it fails on its own terms: mutually exclusive values are not a mistyped digit. The editorial consequence, which the EIC states and this synthesis adopts, is that a major-revision letter would ask the authors to rescope claims around a result the manuscript does not unambiguously report.

The second is governance. §3.2 records that students were not informed their dashboard activity would be analysed; the manuscript carries no ethics approval, no consent basis for the trace data, no linkage or de-identification account, and no data-availability statement. Three seats treat this as independently disqualifying; R2 abstains on severity as venue-dependent while insisting the finding not be lost between seats. R3's point is decisive for sequencing: the linkage is the part that would have required prior review and is exactly the part not described, so the remedy runs through the authors' institution before it runs through any journal.

Neither disagreement changed this outcome. Both were severity disagreements, both were arbitrated on expertise and evidence, and both left the required work unchanged.

**The conditional branch is preserved explicitly, at the EIC's request and consistent with R1's and R3's cards.** If the authors deposit the analysis dataset and code and every reported quantity re-derives, and if the ethics approval proves to exist and to have simply gone undisclosed, then the case for the contract action's major-revision branch strengthens materially. That branch would still require the re-specified analysis in item **R5**, because SC-13, SC-16, SC-17 and SC-18 are defects of design and reporting rather than of transcription. Absent the data, no wording revision changes the manuscript's evidential status.

*Cross-model blind decision check (Step 4b) was not engaged: `ARS_CROSS_MODEL` is not set for this run, so no behavioural change applies and no handoff envelope was emitted.*

---

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. A DA-CRITICAL or non-decomposed item uses `—`. This roadmap is supplied because the panel's decision sits inside a range action and because a Reject on this record still owes the authors an executable path; it is not an invitation to resubmit this text unchanged.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Source | Severity | Section | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|
| R1 | Deposit the analysis dataset and analysis script; re-derive every reported quantity from that script; report each test in one table with *n*, *df*, effect size, and 95% CI. Reconcile: the headline *r*; the four sample sizes; *t*(156) against 87 item respondents; *t*(140) = 1.31 against *p* = .008; the sum of perceived-control responses behind *M* = 3.847; the *SD*/range pair | SC-1, SC-2, SC-3, SC-5, SC-6, SC-32 | EIC, R1, R2, R3, DA | Critical | Abstract, §4.1–§4.3, Tables 1–2 | P1 | 1–2 weeks **if the data exist**; gating for everything below |
| R2 | Supply the ethics/IRB approval record and protocol number, the ethical and legal basis for analysing behavioural logs, the survey-to-log linkage and de-identification procedure, and whether students could opt out; add data-availability, conflict-of-interest, and funding statements. If no approval was obtained, resolve with the authors' institution before any resubmission | SC-26, SC-27 | EIC, R1, R2, R3 | Critical | §3.2, front/back matter | P1 | Institution-dependent; not author-schedulable |
| R3 | Remove the causal verbs from §5's opening sentence and from §6; withdraw the institutional prescription or restate it as a hypothesis for experimental test; scope title, Abstract, and Conclusion to course completion in one course in one term; stop substituting institutional retention for course completion, and stop treating induced engagement as equivalent to the voluntary engagement observed. Promote §5 ¶3's calibrated reading into the Discussion's opening | SC-10, SC-11, SC-12, SC-14, SC-35, SC-37 | EIC, R1, R2, R3, DA | Critical | §5, §6, Abstract, Title | P1 | 3–5 days |
| R4 | Rebuild §5.1 so it leads with the disqualifying limitations: the correlational design's causal ceiling, volunteer self-selection, mid-term survivorship, the absence of any confounding control, the single item's unestimable reliability, and the median split. Add reverse causation as a named rival explanation | SC-13, SC-16, SC-19 | EIC, R1, R2, R3, DA | Critical | §5.1 | P1 | 3–5 days |
| R5 | Re-specify the analysis: run the retention model on full-cohort log data (no survey needed); fix the exposure to a pre-outcome landmark window in which all students were still enrolled, or model person-time explicitly; keep engagement continuous; fit logistic regression adjusting at minimum for prior achievement and non-dashboard LMS activity; report adjusted odds ratios with 95% CIs and a sensitivity analysis for unmeasured confounding; supply a CONSORT-style flow from enrolled → eligible → analysed with the enrollment denominator and response rate; report the retention base rate and add retention to Table 1; state whether the exam comparison conditions on the outcome. Confront the events-per-variable limit rather than using it as grounds to omit adjustment | SC-7, SC-8, SC-9, SC-15, SC-17, SC-18, SC-25, SC-31 | R1 (lead, Conf 5), EIC, R2, R3, DA | Critical | §3.1–§3.4, §4 | P1 | 3–4 weeks, contingent on registrar and full-log access |
| R6 | Correct the Ferro & Nakamura (2021) attribution to what the source actually argues and rebuild the equity rationale on it; supply resolvable identifiers for all fifteen references; cite or remove every uncited entry, and state the verified count (the cards report eight and nine) | SC-20, SC-21, SC-22 | EIC, R2, R3, DA | Critical | §2, References | P1 | 1 week |
| R7 | Remove the self-regulated-learning measurement claim from the Abstract and keywords, **or** replace the single item with a validated multi-item instrument and report α or ω with a CI. Either way, confine perceived control to a descriptive role and delete §5's mechanism claim unless mediation is actually tested | SC-23, SC-24 | EIC, R1, R2, R3, DA | Critical | Abstract, §3.3, §5, Keywords | P1 | 3 days for removal; a full term for new instrumented data |
| R8 | Either run the subgroup/moderation analysis by prior achievement (and goal orientation) that the "who benefits" claim requires, **or** delete the claim and reposition the paper as a bounded single-site association report | SC-33, SC-34 | EIC, R2, R3, DA | Critical | §5, §6 | P1 | 1 week once R5's data exist |
| R9 | Publish the deployment specification: name the LMS and version; state the sessionization rule and whether "inactivity" means dashboard views or all LMS activity; specify the peer-comparison band's norm group, framing, and opt-out; include an interface figure; define the final exam measure in §3.3 with its scoring and administration | SC-28, SC-29, SC-30 | EIC, R1, R2, R3 | Critical | §3.1, §3.3 | P1 | 1 week |
| R10 | Add the student-side consequence analysis at the point of any recommendation — equity of engagement metrics against access, time, and device quality; privacy and surveillance; the demotivation risk §2 itself raises; the self-fulfilling effect of engagement-based at-risk flagging — **or** drop the recommendation entirely | SC-36 | R3 (lead), EIC, R2, DA | Critical | §5, §6 | P1 | 1 week |

#### Required Item Details

**R1: Reconstruct every reported quantity from deposited data**
- **Problem**: four sample sizes, two values for the headline correlation, a *p* unattainable at either candidate *df*, and a mean unattainable from the stated response count. No single dataset generates all reported values.
- **Source**: R1's six-check reconstruction table (checks 1, 3, 4, 5, 6 fail); EIC W2 and Q1–Q2; R2's argument-logic section; R3's D5 routing note; DA C1–C3.
- **Requirement**: deposit dataset and script; re-derive every number; one table per test with *n*, *df*, effect size, 95% CI; state which analytic sample each test used.
- **Acceptance criteria**: an independent reader reproduces every reported value from the deposited script, and no two reported quantities remain in conflict.

**R2: Establish the governance record for the trace data**
- **Problem**: §3.2 states students were not informed their dashboard activity would be analysed; no approval, consent basis, linkage, or de-identification account appears anywhere.
- **Source**: R3 W1 and Review Body; EIC W5 and Q4; R1's Reproducibility section and D1 trigger (f); R2's minor-issue record, with severity abstained but the finding flagged as not-to-be-lost.
- **Requirement**: approving body and protocol number; the basis on which logs were analysed and linked to survey responses; the de-identification procedure; opt-out availability; plus data-availability, COI, and funding statements. If no approval exists, that must be stated and resolved institutionally first.
- **Acceptance criteria**: the journal can confirm the study was permitted to be conducted, and a reader can see how identifiable records were handled.

**R3: Bring the claims back inside the design**
- **Problem**: causal verbs and an institution-scale prescription sit in the Discussion's opening and the Conclusion's core, from a design §3.1 declares cross-sectional, against §1's explicit pledge and §2's own cited audit.
- **Source**: CONSENSUS-4 across all four scoring seats; DA C4 and M1–M2.
- **Requirement**: "was associated with," not "improved" or "raises"; no policy prescription without a design that supports it; title/Abstract/Conclusion bounded to course completion in one course; §5 ¶3's calibrated reading promoted.
- **Acceptance criteria**: no sentence in the manuscript asserts more than the reported design licenses, and the Abstract's claims match §4's reported values.

**R5: Re-specify the analysis**
- **Problem**: exposure accumulates over enrollment time and terminates at the outcome, making the association partly definitional; no covariates are fitted; the sample is a mid-term volunteer set with an unstated denominator; the outcome's base rate is never reported.
- **Source**: R1 W2–W4 and the Analysis Methods section (Confidence 5, declared lane); EIC D1; R2 W4; R3 W4; DA C5 and M4.
- **Requirement**: full-cohort logs; landmarked exposure or explicit person-time; continuous engagement; logistic regression with prior-achievement and non-dashboard-activity adjustment; adjusted ORs with CIs; unmeasured-confounding sensitivity analysis; participant flow with denominators; base rate reported.
- **Acceptance criteria**: the reported association is estimated on a sample not filtered on the outcome, with an exposure window that precedes it, and every estimate carries an interval.

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Source | Priority | Section | Expected Improvement |
|---|---|---|---|---|---|---|
| S1 | Report group *n*s, means, and SDs for every test — the perceived-control comparison currently reports none; add *n* columns and explicit totals to Tables 1 and 2, whose rows carry different denominators | SC-2, SC-9 | R1, EIC | P2 | §4.3, Tables 1–2 | Makes every result independently reconstructable, as Table 2 already partly is |
| S2 | Bring numeric reporting to APA 7.0: two decimals for *M* against two-decimal *SD*, correlations reported with *n*, *df*, *p*, and CI including in the Abstract | SC-6 | EIC, R1, R2, R3 | P3 | Abstract, §4, Tables | Removes the false precision that made the impossible mean detectable |
| S3 | Replace §3.3's justification that single-item ratings are "common… to limit survey burden" with validity evidence, or drop it as a warrant | SC-23 | R1 | P2 | §3.3 | Prevalence is not validity; the measure needs a real warrant or a reduced role |
| S4 | Establish the §1 gateway/first-year framing against §3.1's description, or drop it; state course modality (online, hybrid, in-person) and institution type and scale | SC-34 | R2, R1, R3 | P2 | §1, §3.1 | Lets an adjacent reader or adopting institution judge transferability |
| S5 | Remove "self-regulated learning" from the keywords unless an SRL instrument is actually used | SC-24 | EIC | P3 | Keywords | Stops the framing claim reappearing in indexing after R7 removes it from the text |
| S6 | State the handling of three uncorrected tests, or declare the analyses exploratory as an observational design permits | SC-8 | R1 | P2 | §3.4, §4 | Aligns the inferential framing with what was actually done |
| S7 | Weigh the alternative levers the manuscript's own §2 implies — instructor-triggered outreach, advisor routing, redesign or removal of the peer-comparison band — rather than selecting "encourage engagement" without comparison | SC-35, SC-36 | DA m2, R3 | P2 | §6 | Makes any surviving recommendation a reasoned choice rather than a default |
| S8 | Engage higher-education persistence scholarship and dashboard-outcome syntheses; two of the manuscript's own listed-but-uncited entries (Halloran, 2020 on gateway-course retention interventions; Wexler & Ojo, 2020 on retention modelling with LMS trace data) are directly on point. **Caveat carried from R2 and R3**: these are the manuscript's own list entries and neither seat can attest that they exist — verify before citing; all other leads in the cards are tagged `[UNVERIFIED]` search leads, not citations | SC-22, SC-34 | R2, R3 | P2 | §1, §2, §5.1 | Supplies the retention literature a retention paper currently lacks |

### Revision Checklist

#### Priority 1 — Structural Revisions (estimated total: 8–11 weeks of author-controlled work, plus institution-dependent time for R2 and a full term if R7 requires new instrumented data)
- [ ] R1: Deposit data and code; re-derive and reconcile every reported quantity **(gating — do this first)**
- [ ] R2: Establish and report the ethics, consent, linkage, and de-identification record; add the three missing declarations **(gating — institution-dependent)**
- [ ] R3: Remove causal verbs; withdraw or reframe the prescription; rescope title, Abstract, and Conclusion to course completion
- [ ] R4: Rebuild §5.1 around the disqualifying limitations; name reverse causation
- [ ] R5: Re-specify on full-cohort logs with a landmarked exposure window, continuous engagement, adjusted logistic model, intervals, and participant flow
- [ ] R6: Correct the Ferro & Nakamura attribution; supply resolvable identifiers; cite or remove uncited entries
- [ ] R7: Remove the SRL measurement claim, or instrument it properly and test the mechanism
- [ ] R8: Run the moderation analysis the "who benefits" claim requires, or delete the claim
- [ ] R9: Publish the deployment and measure specification; define the final exam variable
- [ ] R10: Add the student-side consequence analysis at the point of recommendation, or drop the recommendation

#### Priority 2 — Content Supplementation (estimated total: 5–8 days)
- [ ] S1: Full descriptives for every test; *n* columns and totals in both tables
- [ ] S3: Replace the prevalence-based warrant for the single item
- [ ] S4: Establish or drop the gateway framing; state modality and institution type
- [ ] S6: State multiple-comparison handling or declare the analyses exploratory
- [ ] S7: Weigh alternative levers before recommending one
- [ ] S8: Engage the persistence and dashboard-outcome literatures (verify the two listed entries first)

#### Priority 3 — Text and Formatting (estimated total: 2–3 days)
- [ ] S2: APA 7.0 numeric formatting throughout, including the Abstract
- [ ] S5: Remove "self-regulated learning" from keywords
- [ ] Add an explicit total to Table 2 and reconcile its caption with the §4.3 text
- [ ] Give the enrollment figure in §3.1 as a number rather than "several hundred"
- [ ] Correct §3.4's stated α so every test in §4 is evaluated against it consistently
- [ ] Move interpretive sentences out of §4.2 and §4.3 into the Discussion

#### Total Estimated Effort
- **Major-revision branch, if the conditional in the Decision Rationale is opened**: 8–10 weeks of author-controlled work, gated on R1 and R2 and on registrar/full-log access for R5.
- **Reject-and-resubmit-as-new-work path (what four seats describe)**: a re-specified study — full cohort, landmarked exposure, adjusted model, validated instrument, ethics record, specified deployment, scope-honest title and conclusion.

### Revision Deadline

- **No revision deadline attaches to this decision.** The manuscript is rejected; a resubmission as new work is welcomed and carries no clock.
- **If the conditional major-revision branch is opened** — the authors supply data and code that reconcile every reported quantity, and an ethics record that proves to exist — the applicable window is **8 weeks** from that determination, at the upper end of the 6–8-week major-revision band, because item R5 requires new data access rather than rewriting.
- **Extension policy**: notify the editorial office one week before the deadline.

### Response Letter Template

Please use `templates/revision_response_template.md` and respond to **every** item above, and to every question in the five reviewer reports, in R→A→C form (Reviewer Comment → Author Response → Changes Made). Three requirements specific to this manuscript:

1. Answer R1's Questions 1–5 and the EIC's Questions 1–2 **with output from the deposited analysis script**, not with narrative reconciliation. A response that asserts which value is correct without the script does not close R1.
2. Respond to the DA's frame-lock premise — that dashboard engagement may be an output of the disposition it indexes rather than a manipulable input — even though no roadmap item can resolve it by revision. It survives the removal of every causal verb and it is the premise §6 rests on.
3. Where you decline an item, give the reasoning and the evidence, not the position. R2's `[FIELD-NORM UNVERIFIED]` tags and R3's routing notes mark exactly where the panel's own evidence stops; you are entitled to push back there on evidence.

---

## Part 3: Reviewer Report Summary (Appendix)

### EIC Report Summary
- **Recommendation**: Reject | **Confidence**: 4
- **Key point**: The manuscript names the field's causal-overreach pathology, cites the audit of it, and then enacts it in the Discussion's opening sentence and the Conclusion — and because the reported statistics do not reconstruct to any single dataset, there is no established finding for a revision letter to scope toward.

### Reviewer 1 (Methodology) Summary
- **Recommendation**: Reject, conditional in one specific sense (data and code first, then a re-specified study as new work) | **Confidence**: 5
- **Key point**: Four of six independently reconstructable reported values fail arithmetic verification; beneath the arithmetic, the exposure window is not landmarked, no covariate is fitted, the sample is a mid-term volunteer set, and reporting is inadequate on every APA axis.

### Reviewer 2 (Domain) Summary
- **Recommendation**: Reject | **Confidence**: 4
- **Key point**: The problem is not competence but self-refutation — a load-bearing citation inverts its own listed title, "retention" is measured as one course's completion and spent as institutional persistence, and self-regulated learning is named rather than used.

### Reviewer 3 (Perspective) Summary
- **Recommendation**: Reject; resubmission welcome as a re-scoped study | **Confidence**: 4
- **Key point**: The paper's own governance practice and its governance-scale prescription point in opposite directions — trace data were analysed without notice, while §6 urges institutions worldwide to expand behavioural analytics and to induce an engagement the study only ever observed as a choice.

### Devil's Advocate Summary
- **Recommendation**: — (seat carries no recommendation field) | **Confidence**: — (not scored by this seat)
- **Key point**: The strongest counter-narrative the paper never addresses is that the association is manufactured by the sampling frame — a mid-term recruitment window makes both variables partial functions of "still being there" — and the steelman that the causal verbs and the numbers are careless slips fails, because a recommendation is a causal claim in the imperative mood and mutually exclusive values are not transcription errors.

### Appendix: Full Reviewer Reports

All five complete Phase 2 reports (EIC, Reviewer 1 Methodology, Reviewer 2 Domain, Reviewer 3 Perspective, Devil's Advocate) are attached unaltered for the authors' reference. Every roadmap item above traces to a specific passage in one or more of them; no issue in this letter originates with the editorial synthesis.

---

### Closing

After careful consideration, we are unable to accept your manuscript for publication in the *Journal of Learning Analytics*.

We want to be precise about what drove this. Your Literature Review is the work of authors who know this field: it names the click-proxy validity problem, the demotivation risk of relative-standing feedback, and the field's habit of letting causal language outrun correlational evidence. Your Methods define engagement, retention, and perceived control specifically enough that a reviewer could audit them — which is uncommon, and is why the audit was possible. And §5's third paragraph already contains the correctly calibrated statement of your own finding. Two things stand in the way of publication rather than revision: the reported statistics cannot be reconstructed from any single dataset, so it is not established which finding a revision would be scoped toward; and the analysis of student behavioural logs carries no ethics record, no consent basis, and no linkage account, which is a matter for your institution before it is a matter for this journal.

The path forward is set out in Part 2. If the deposited data reconcile every reported quantity and the ethics approval proves to exist and to have gone undisclosed, write to the editorial office — the major-revision branch of this decision remains genuinely open, and it is deliberately not foreclosed here. Otherwise, the study four of our five seats described is a different and considerably stronger one: full-cohort logs rather than volunteers, a landmarked exposure window, continuous engagement in an adjusted logistic model, a validated multi-item regulatory instrument, a published interface specification, a moderation analysis by prior achievement, and a title and conclusion bounded to one course at one institution.

Should the numbers reconcile and the claims be scoped honestly, this journal remains a natural disciplinary home for that work. A single-course observational association study, framed as such, would also sit well at the *Journal of Computing in Higher Education* or the *Australasian Journal of Educational Technology*. *Computers & Education*, which your Conclusion's institutional ambition appears to target, would require the multivariable modelling with prior-achievement controls that item R5 specifies.

We appreciate the effort behind this submission and hope the reviewers' comments are useful to the next version of the research.
