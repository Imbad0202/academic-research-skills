# Editorial Decision Package

**Contract:** `reviewer/reviewer_full/v2` · mode `reviewer_full` · stage `reviewer_full_review` · baseline `v3.20.0` · `panel_size: 5`
**Synthesizer mode:** v3.6.2 Sprint Contract Synthesizer Protocol (arithmetic). The general-mode Step 1b sub-claim inventory is **not** run in this mode; the decision derives from the role-scoped dimension matrix and `failure_conditions[]` only.

---

## Part 0: Mechanical Audit Emission

### Step 1 — Role-scoped scoring matrix

Only seats whose `contract_role` appears in a dimension's `eligible_roles` are counted. `not_assessed` values from ineligible seats are excluded from numerator and denominator alike.

| Dim | Priority | Eligible roles | Assessed eligible seats | Seat scores | Dimension verdict |
|---|---|---|---|---|---|
| D1 methodology_rigor | mandatory | methodology | 1 (methodology) | block, `block_class: fatal` | **block(fatal)** |
| D2 domain_accuracy | mandatory | domain | 1 (domain) | block, repairable | **block** |
| D3 argumentative_coherence | mandatory | da, methodology | 2 (da, methodology) | block/repairable, block/repairable | **block** |
| D4 cross_disciplinary_relevance | high | perspective | 1 (perspective) | block | **block** |
| D5 writing_and_structure | normal | eic | 1 (eic) | block (no fatal; normal priority) | **block** |
| D6 venue_fit_and_contribution | mandatory | eic | 1 (eic) | block, `block_class: fatal` | **block(fatal)** |

Fatal scope check: both fatal declarations (D1, D6) sit on **mandatory** dimensions and are therefore in scope. No dimension is unassessed by its eligible seats; no `[DIMENSION-UNASSESSED]` abort. All 5 cards are usable; no `[PANEL-SHRUNK]`.

**Audit verdict:** worst assessed eligible score across all dimensions = `block`, with fatal blocks declared → `block(fatal)`.

### Step 2 — Failure-condition evaluation

| ID | Sev | Cross-reviewer quantifier | Expression | Per-dimension evaluation | Fired |
|---|---|---|---|---|---|
| F1 | 95 | any | any mandatory dimension has a fatal block | D1 true (methodology fatal), D2 false, D3 false, D6 true (eic fatal); dimension quantifier `any` → true | **true** |
| F2 | 90 | any | any mandatory dimension scores 'block' | D1/D2/D3/D6 all true → true | **true** |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1 (n=1→owner), D2 (n=1→owner), D3 (n=2→both seats), D6 (n=1→owner) all true; "two or more" over 4 → true | **true** |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4 = block → true | **true** |
| F5 | 40 | any | any dimension scores 'warn' or worse | all six true → true | **true** |
| F0 | 10 | all | every dimension scores 'pass' | false | false |

### Step 3 — Precedence and emission

Highest-severity fired condition: **F1 (severity 95)** → `action: editorial_decision=reject`.

```
dimension_verdicts: [D1=block(fatal), D2=block, D3=block, D4=block, D5=block, D6=block(fatal)]
fired_conditions: [F1, F2, F3, F4, F5]
da_critical_adjudications: [C1=VALIDATED, C2=VALIDATED, C3=VALIDATED, C4=VALIDATED, C5=VALIDATED, C6=VALIDATED, C7=VALIDATED]
editorial_decision=reject
```

No `C<n>=REJECTED`, so no rejection-rationale lines are required. The mechanical decision is not `accept`, so no `[DA-CRITICAL-VS-ACCEPT]` marker applies.

**DA CRITICAL adjudication basis** (adjudication and visibility, not veto — F1 fired independently of the DA seat, whose only score was D3 `repairable`):

- **C1** causal/prescriptive conclusion from a cross-sectional design — VALIDATED. Corroborated by EIC W5, R1 D3/§Inferential warrant, R2 W2, R3 W6; verifiable against §1 vs §5–§6 in the manuscript.
- **C2** abstract `r = .42` vs Results `r = .24` — VALIDATED. Corroborated by EIC W4, R1 W1, R2 W6, R3 W8.
- **C3** predictor partly determined by outcome (session counts accrue over the term withdrawal truncates) — VALIDATED. Independently reached by EIC W3 as an exposure-window confound; follows from §3.3's own definitions.
- **C4** sample conditioned on the outcome plus the random/volunteer contradiction — VALIDATED. Corroborated by R1 W4 and W10, R2 W7, R3 W5, EIC W7.
- **C5** worldwide institutional applicability against §5.1's own limitations — VALIDATED. Corroborated by EIC W5/W6, R2 W2, R3 W6.
- **C6** `t(156)` describes a sample appearing nowhere in the manuscript — VALIDATED. R1 W2 recomputed that `t = 3.02` at `df = 156` yields exactly the reported `p = .003`, which is the specific evidence that the figure entered a computation rather than being mistyped; corroborated by EIC W8, R2 W12.
- **C7** trace data analysed without notice, no ethics statement — VALIDATED as a disclosure fact stated by the authors in §3.2. What is validated is the absence of documentation, not a finding about what approval does or does not exist; EIC W1, R1 W5, R3 W1/W2 concur.

### Panel and card hygiene (flagged, not repaired)

Per the phase boundary I flag rather than fix. Two items:

1. Three cards (methodology, domain, perspective) open with a **Scoring Plan Dissent** heading that is then self-retracted in the body. I read all three as **no dissent filed**, consistent with the protocol's instruction to omit the section entirely. No score was altered on this basis, and no fatality was minted or removed.
2. The contract's `measurement_procedure` requires `contract_paraphrase` and `scoring_plan` output before the paper, with `paraphrase_minimum_dimensions: all`. **Neither appears in any of the five cards as supplied to me.** They may exist as Phase 1 pre-outputs outside the excerpt I received; I cannot verify that from here. This is a compliance observation for the orchestrator, not a scoring input — it did not affect the matrix, the fired conditions, or the decision.

No cross-model check was run: `ARS_CROSS_MODEL` is not indicated as set and no consent gate is recorded, so Step 4b produces no behavioural change.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript titled "Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment." Your manuscript has been reviewed by five independent reviewers, including a Journal-Fit Reviewer and a Devil's Advocate seat.

### Decision: Reject

This decision is mechanical under the review contract. Two mandatory dimensions carry fatal blocks — **D1 methodology_rigor** and **D6 venue_fit_and_contribution** — which fires condition F1 (`editorial_decision=reject`). Four further conditions fired at lower severity and would each have produced Major Revision; F1 takes precedence. I did not, and under this protocol cannot, soften a fired condition's action on post-hoc grounds.

### Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — this block is mandatory in `reviewer_full` mode and must not be omitted, but the dispatching layer supplied no provenance stamp with the five cards. I am required not to infer it, because doing so risks implying model independence that may not have existed. The dispatching layer must supply exactly one of the three permitted statements (cross-model slot active / single-family disclosure / dispatch-failure fallback) before this letter is released to the author. I computed no cross-family aggregate and no same-model majority; the per-seat matrix in Part 0 shows each seat's scores by inspection.

### Consensus Analysis

A note on labelling. In sprint-contract mode the Step 1b sub-claim inventory is not run, so I do not apply the general-mode `[CONSENSUS-4]` / `[CONSENSUS-3]` labels here — those labels are defined over decomposed sub-claims, and attaching them to undecomposed weakness bundles is precisely the partial-evidence error the protocol warns against. I instead report convergence counts over the four non-DA cards (EIC, R1 methodology, R2 domain, R3 perspective) with the DA tracked separately.

#### Convergent findings (4 of 4 non-DA cards, plus DA)

- **The abstract's `r = .42` contradicts the Results' `r = .24`.** EIC W4, R1 W1, R2 W6, R3 W8, DA C2. R1's recomputation establishes that `.24` is the internally coherent value (`t = 2.93`, `df = 140`, `p = .0040`).
- **§5 and §6 assert causation and worldwide institutional applicability that the design cannot support**, abandoning the standard §1 and §2 set for themselves. EIC W5, R1 D3, R2 W2, R3 W6, DA C1 and C5.
- **Trace data were analysed without notice to students, and no ethics approval, consent waiver, legal basis, anonymisation, retention, or data-availability statement appears anywhere.** EIC W1, R1 W5, R2 W11, R3 W1 and W2, DA C7.
- **§3.2 gives two mutually exclusive sampling descriptions** (random sample vs. self-selected volunteers), and no response rate or denominator is reported. EIC W7, R1 W10, R2 W7, R3 W5, DA C4 and M8.
- **Reported sample sizes, degrees of freedom, and group totals cannot be reconciled**: 142 stated, 87 item respondents, `df = 156`, Table 2 summing to 127. EIC W8, R1 W2 and W8, R2 W12, R3 (deferred), DA C6 and M2.

#### Convergent findings (3 of 4 non-DA cards, plus DA)

- **Ferro & Nakamura (2021) is cited against its own stated finding**, and §5's equity reading depends on the inverted version. R2 W1 (Critical), EIC W10, R3 W9, DA M1. **R1 (methodology) is silent on this** — not opposed, silent.
- **"Retention" shifts from single-course completion in Methods to programme- and institution-level persistence in the Introduction and Conclusion.** EIC W6, R2 W3, DA M7; **R1 and R3 silent.**
- **All fifteen references carry the reserved `10.5555` test DOI prefix and cite no independently verifiable venue.** EIC W2, R2 W8, plus R2 W5 on the nine uncited entries; **R1 and R3 silent.**

#### Findings raised by one or two cards, weighted by stated confidence

- **Two reported statistics are arithmetically unreachable, not merely inconsistent.** R1 W3 (GRIM failure: `M = 3.847` cannot arise from 87 integer 1–5 responses; the neighbouring achievable values are 3.8391 and 3.8506) and R1 W9 (`SD = 0.10` at `n = 10`, `M = 3.00` on an integer scale, where the smallest non-zero sample SD is √(2/9) ≈ 0.471). Corroborated at Major by R2 W13 and DA M4; EIC W13/W14 touched the same numbers as presentation defects only. R1 is the sole eligible seat on D1 and reports Confidence 5 on both, from deterministic checks. Full weight.
- **The engagement measure is not separable from time-in-course.** EIC W3 and DA C3 reached this independently from §3.3's own definitions; no other card raises it. Both at Confidence 5. Full weight.
- **No locatable contribution increment over the existing systematic-review consensus.** EIC W3, Confidence 5. This is the D6 fatal block and rests on the single eligible seat for that dimension.
- **Harm went unmeasured despite the paper's own literature review describing the mechanism.** R3 W4, Confidence 4; no other card raises it as a finding.
- **Deployment parameters an institution would need are entirely absent.** R3 W7, Confidence 5.

#### Points of Disagreement

The five cards are unusually convergent. I found no dimension on which two eligible seats scored in opposite directions, so no scoring conflict required arbitration. Three severity-level divergences are worth recording:

- **The abstract's inflated coefficient**: R1 W1 and DA C2 file it Critical; EIC W4, R2 W6, R3 W8 file it Major. **Resolution**: retained at Critical, on expertise-first grounds — R1 is the eligible seat for the dimension the error falls under (D1) and the one that recomputed it, and R1's basis is that the figure is not merely wrong but that which value the analysis produced is currently undeterminable from the manuscript. Nothing turns on this for the decision; it governs roadmap priority only.
- **The trace-data consent gap**: EIC, R1, and R3 file it Critical; R2 W11 files it Major at Confidence 3, explicitly disclaiming it as outside their expertise. **Resolution**: retained at Critical. R2's own stated confidence directs the weight elsewhere, and three seats with domain standing on it concur.
- **Whether the numerical discrepancies form a one-directional pattern**: the field brief anticipated that every discrepancy would favour the hypothesis; R1 tested that and **declined to claim it in full**, finding three directional errors (`r` .42 over .24; `p` .008 over .19; `df` 156 over 85) and two directionless ones. **Resolution**: R1's narrower claim stands as the panel's position. I record this because it is the correct handling — the reviewer discounted their own prior against the evidence, and the narrower finding is still decisive: three independent inflating errors coexisting with two arithmetically impossible summaries cannot be adjudicated as transcription error from the manuscript alone.

I also record one **unresolved** matter that neither evidence nor expertise on this panel can settle. EIC and R2 were each asked to state whether the `10.5555` reference apparatus indicates a template artefact or fabricated citations. EIC (W2, Confidence 4) holds that if the works exist the authors must supply verifiable citations, and if they do not, the list is not a reference list — declining to choose between readings. R2 (W8, Confidence 4) explicitly declines to assert fabrication and flags it as a verification failure requiring editorial confirmation, noting that if the sources do not exist the correct outcome escalates beyond the block recorded. **The panel did not resolve this**, and I do not resolve it here. It requires editorial verification outside peer review. Its resolution does not change today's decision, which F1 already determines on other grounds, but it does change what a future submission would mean.

### Decision Rationale

Five reviewers, working from non-overlapping briefs, converged on a manuscript whose surfaces and substance have come apart. The presentation is complete and the literature review is genuinely self-critical: §2 anticipates the click-proxy problem, the demotivation risk, and the field's causal-language problem, and §3.3 volunteers that its own median split is a coarse simplification. That candour is real and is credited by four of the five cards.

Two independent fatal conditions nevertheless close the file. On **D1**, the reported statistics do not describe one dataset: 142, 87, `df = 156`, and Table 2's 127 cannot be simultaneously true, and two summary values (`M = 3.847` at `n = 87`; `SD = 0.10` at `n = 10`, `M = 3.00`) cannot be produced by any integer response set. That is a claim about which datasets exist, and it cannot be edited away. Compounding it, mid-term voluntary recruitment against an end-of-term outcome conditions the sample on partial survival, so the estimand is not the one the paper claims, and no reanalysis of these 142 cases recovers it.

On **D6**, the sole eligible seat finds no locatable increment. After the abstract's coefficient is corrected, the causal verbs of §5–§6 withdrawn, and the exposure-window confound conceded, what remains restates what the systematic reviews the manuscript itself cites already establish.

Separately and prior to merit, four seats record that behavioural data were analysed without notice to the students, with no approval documentation anywhere. Retroactive approval is not available for an analysis already performed.

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| 1 | Behavioural trace data were analysed without notice to participants, with no ethics approval, consent waiver, legal basis, anonymisation, retention, or data-availability statement anywhere in the manuscript. Not curable retroactively; the engagement variable, the retention association, and both group comparisons all derive from the unconsented reuse. | EIC (W1), R1 (W5), R2 (W11), R3 (W1, W2), DA (C7) | text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study." | R1 |
| 2 | **D1 fatal.** Sample sizes and degrees of freedom cannot be reconciled to one dataset, and two reported summaries are arithmetically unreachable on the stated scales and *n*s. Adjudicating this requires the analysis data and code, which the manuscript neither supplies nor accounts for. | R1 (W2, W3, W6, W8, W9), corroborated by EIC (W8), R2 (W12, W13), DA (C6, M2, M4) | table: Table 1, perceived-control row (M = 3.847, SD = 0.62), with n = 87 per §4.1 | R2, R4 |
| 3 | **D6 fatal.** No locatable increment over the systematic-review consensus the manuscript itself restates; the stated contribution names a setting and a data combination, not a claim. Text revision cannot supply an increment these data do not contain. | EIC (W3) | text: §1 "The present study contributes to this literature by examining the association between dashboard engagement and course retention in a single large undergraduate course" | R12 |

### Required Item Details

Numbering matches the Part 2 Required Revisions table row-for-row (R1 is the first Required row, and so on, contiguously through R12).

**R1 — Ethics, consent, and data governance**
Establish and document the basis on which the dashboard log data were analysed. EIC, R1, and R3 each treat this as a gate prior to scientific merit; R3 sets out the ordered remedies.
- **Acceptance criteria**: Documented ethics/REC approval plus a stated data-protection basis covering secondary analysis of dashboard trace data, with anonymisation, retention, and data-availability statements; failing that, documented retrospective consent; failing that, withdrawal of all log-based analyses.

**R2 — Arithmetically impossible statistics and the absent data trail**
Two reported values cannot arise from the described response sets, and no availability statement permits independent reconciliation. R1 notes the appropriate editorial action is a data request, not a list of errata.
- **Acceptance criteria**: The analysis dataset and code are supplied, `M = 3.847` (n = 87) and `SD = 0.10` (n = 10, M = 3.00) are either corrected against the data or their inputs restated, and a data/code availability statement or an explicit withholding rationale appears in the manuscript.

**R3 — The abstract's headline coefficient**
The abstract reports nearly double the Results value, and builds "a promising lever" on it. R1 established `.24` as the internally coherent figure.
- **Acceptance criteria**: A single coefficient is reported consistently in abstract and Results, the manuscript states which value is the analysis of record, and the inference built on it is rewritten to match.

**R4 — Reconstruction of the analytic sample and every reported test statistic**
142, 87, `df = 156`, `df = 140`, and Table 2's 66 + 61 = 127 cannot all describe one dataset; `t(140) = 1.31` with `p = .008` is impossible at the stated df; and the same result is narrated as non-significant. R1 further shows the fifteen unaccounted cases must average ≈76.8 to reconcile the two tables, which contradicts the claim that all 142 were classified.
- **Acceptance criteria**: A per-analysis *n* table is reported, every *t*, *df*, and *p* is recomputed and internally consistent, Table 2 reconciles with the stated analytic sample, and the verbal characterisation of each result matches its recomputed *p*.

**R5 — Causal and scope claims in §5 and §6**
§1 promises to keep pattern separate from cause and §2 cites an audit of exactly this failure; §5 and §6 then assert improvement, probability-raising, dependability, and worldwide generalisability. Four cards plus the DA treat this as one systemic failure, not a set of wording nits.
- **Acceptance criteria**: §5, §6, and the abstract are rewritten wholly in associational terms with all causal verbs removed, and every recommendation is bounded to one course, one term, and one interface.

**R6 — The Ferro & Nakamura (2021) attribution**
R2 (Critical, Confidence 5) finds the source cited against its own stated finding, forwarded explicitly into the Discussion, where it carries §5's equity reading; §2 then cites Osei (2020) for the opposite proposition two sentences later.
- **Acceptance criteria**: The attribution is corrected against the source, §2's equity paragraph and §5's alignment reading are rebuilt on what the cited work actually reports, and the word "reliably" is either removed or supported.

**R7 — Analytic model, precision, and base rate**
A dichotomous outcome is analysed by Pearson correlation with no covariates; no confidence interval or effect size beyond *r* appears anywhere; the retention base rate is never reported, which bounds the attainable point-biserial magnitude.
- **Acceptance criteria**: Logistic regression on the binary outcome with prior achievement, credit load, and basic demographics as covariates; confidence intervals on every estimate and at least one effect size per comparison; the retention base rate reported as count and proportion; and the median split either dropped or justified against the acknowledged right skew.

**R8 — Sampling frame, exposure window, and selection intensity**
Mid-term voluntary recruitment against an end-of-term outcome conditions the sample on partial survival; §3.2's two sampling descriptions are mutually exclusive; no response rate is given against an enrolment of "several hundred"; and session counts accrue over the same interval whose completion they predict.
- **Acceptance criteria**: A full-cohort sampling frame including pre-recruitment withdrawals, the word "random" removed and the volunteer route stated, response rate and eligible-enrolment denominator reported, withdrawal timing reported, and dashboard sessions normalised for exposure time or restricted to a common pre-withdrawal window.

**R9 — Verifiability of the reference apparatus**
All fifteen entries carry the reserved `10.5555` test prefix, nine are never cited in text, and the load-bearing premises that most need attribution carry none. No characterisation of prior work can currently be checked.
- **Acceptance criteria**: Every reference carries a resolvable DOI and a verifiable venue, uncited entries are either invoked in text or removed, the gateway-attrition premise and the self-regulated learning model receive primary-source citations, and at least one review of dashboard–outcome studies is engaged.

**R10 — The "retention" construct**
Methods operationalise remaining enrolled and sitting one course's final assessment; the title, §1, and §6 use the same word for institutional persistence across programmes and disciplines. No year-level or enrolment-continuation data are reported.
- **Acceptance criteria**: The measured outcome is named as single-course completion throughout, all programme- and institution-level persistence claims are removed, and the first-year/gateway framing is either evidenced from the sample or deleted.

**R11 — The SRL measure and the mediation claim**
The abstract claims a self-regulated learning behavioural measure that §3.3 does not contain; §5 calls a single cross-sectional item a "mediating construct" with no model, coefficient, or temporal ordering, where the reverse ordering is at least as plausible.
- **Acceptance criteria**: The abstract's SRL-behaviour claim is either withdrawn or backed by an operationalised behavioural measure; "mediating construct" is either removed or replaced by an estimated mediation model with temporal ordering; and the single-item constructs carry reliability or validity evidence or are labelled as unvalidated single items.

**R12 — A locatable contribution increment**
EIC finds the stated contribution names a setting and a data combination rather than a claim, and identifies no prior claim revised, extended, or overturned. I record plainly that this item is **not achievable by revising the text of this manuscript**; it is the reason the decision is Reject rather than Major Revision.
- **Acceptance criteria**: A future submission identifies a specific prior claim it revises, extends, or contradicts, and supports that claim with a design capable of doing so.

---

## Part 2: Revision Roadmap

Because the decision is Reject, this roadmap is not a resubmission checklist for the present manuscript. It is the constructive statement Edge Case 2 requires: the conditions a defensible version of this study would have to meet. Items R1 and R12 in particular cannot be satisfied by revising this text.

> The `Sub-Claim(s)` column carries `—` throughout: sprint-contract mode does not run the Step 1b sub-claim inventory, so no `sub_claim_id`s exist. Traceability is carried instead by the `Source` column, which names the originating card and finding ID for every item. No item introduces a concern absent from the five cards.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| R1 | Document ethics approval and legal basis for secondary analysis of dashboard logs, or obtain retrospective consent, or withdraw all log-based analyses | — | Critical (transported, EIC W1; concurrent Critical R1 W5, R3 W1) | text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study." | 5 — direct editorial responsibility for ethics-statement screening on trace-data submissions (EIC W1) | EIC W1, R1 W5, R3 W1/W2, DA C7 | P1 | Not resolvable by revision; institutional process |
| R2 | Supply analysis data and code; resolve the two arithmetically unreachable summaries | — | Critical (transported, R1 W3; R1 W6 Critical; R1 W9 Major) | table: Table 1, perceived-control row (M = 3.847, SD = 0.62), with n = 87 per §4.1 | 5 — GRIM test is deterministic given an integer scale and a known *n* (R1 W3) | R1 W3/W6/W9, R2 W13, DA M4 | P1 | Days, if the data exist |
| R3 | Reconcile the abstract's `r = .42` with the Results' `r = .24` and state the analysis of record | — | Critical (transported, R1 W1; Major per EIC W4, R2 W6, R3 W8 — divergence arbitrated in Part 1) | text: Abstract "Dashboard engagement correlated positively with retention (r = .42)" vs §4.2 "r = .24, p = .004" | 5 — direct recomputation of the correlation-to-*t* transform at the stated *n* (R1 W1) | R1 W1, EIC W4, R2 W6, R3 W8, DA C2 | P1 | Hours |
| R4 | Re-derive the analytic sample; make every reported *n*, *df*, *t*, *p*, and table total mutually consistent | — | Critical (transported, R1 W2); Major (R1 W8, EIC W8, DA M2/M3) | text: §4.3 "t(156) = 3.02, p = .003"; table: Table 2, group n column (66 and 61, summing to 127) | 5 — statcheck-style recomputation plus arithmetic on the two candidate sample sizes (R1 W2) | R1 W2/W7/W8, EIC W8/W11, R2 W12, DA C6/M2/M3 | P1 | 1–2 weeks with data access |
| R5 | Rewrite §5, §6, and the abstract in associational terms; bound all recommendations to one course and one interface | — | Critical (transported, R2 W2, DA C1/C5); Major (EIC W5) | text: §5 "dashboard engagement improved course retention"; §6 "is a dependable strategy for improving retention across programs and disciplines" | 5 — the design is described as cross-sectional and observational by the authors (R2 W2) | R2 W2, EIC W5, R1 D3, R3 W6, DA C1/C5 | P1 | 3–5 days |
| R6 | Correct the Ferro & Nakamura attribution and rebuild the §2/§5 equity argument on what the source reports | — | Critical (transported, R2 W1); Major (EIC W10, R3 W9, DA M1) | text: §2 and References, "Dashboards have been shown to reliably improve outcomes for lower-achieving students" attributed to "When dashboards demotivate: Peer comparison and the lower-achieving student" | 5 — the contradiction is internal to the manuscript and does not depend on retrieving the source (R2 W1) | R2 W1, EIC W10, R3 W9, DA M1 | P1 | 3–5 days |
| R7 | Replace the correlational analysis with covariate-adjusted logistic regression; report base rate, intervals, and effect sizes | — | Major (transported, R1 W11, W12, W13) | text: §3.4 "Associations between continuous measures were assessed with Pearson correlations."; absence: §4.2-4.3 with §3.4 — expected confidence intervals and at least one effect size beyond r for the correlation and both t-tests | 5 — standard modelling requirement for binary outcomes in observational educational data (R1 W11) | R1 W11/W12/W13 | P1 | 1–2 weeks |
| R8 | Establish a full-cohort sampling frame; resolve the random/volunteer contradiction; report response rate and withdrawal timing; normalise session counts for exposure | — | Critical (transported, R1 W4, DA C3/C4); Major (R1 W10, R2 W7, R3 W5, EIC W7, DA M8) | text: §3.2 "Midway through the term, an announcement was posted to the course LMS inviting students to complete a short survey"; §3.2 "a random sample of students enrolled in the course section" and "Students who chose to respond, and who consented to the survey, formed the study sample" | 5 — selection-bias mechanism in learning-analytics trace samples is my primary specialization (R1 W4) | R1 W4/W10, EIC W3/W7, R2 W7, R3 W5, DA C3/C4/M8 | P1 | Requires new data extraction; not resolvable within these 142 cases |
| R9 | Supply verifiable citations; cite or remove the nine uncited entries; attribute the load-bearing premises; engage a dashboard–outcome review | — | Critical (transported, EIC W2); Major (R2 W5, R2 W8) | text: References, Ainsworth & Devi (2018) and Wexler & Ojo (2020) entries "https://doi.org/10.5555/1010203" and "https://doi.org/10.5555/1516718" | 4 — familiar with DOI registration practice and the reserved 10.5555 test range, though not with every named venue (EIC W2) | EIC W2, R2 W5/W8 | P1 | Days; contingent on editorial verification (see unresolved item, Part 1) |
| R10 | Relabel the outcome as single-course completion; remove programme- and institution-level persistence and gateway framing | — | Major (transported, EIC W6, R2 W3, DA M7) | text: §3.3 "was coded dichotomously as whether the student remained enrolled and completed the final assessment"; §6 "practical and generalizable lever for supporting student success at scale" | 5 — this is a core distinction in the retention literature the paper invokes (R2 W3) | R2 W3, EIC W6, DA M7 | P1 | 2–3 days |
| R11 | Withdraw or substantiate the abstract's SRL-behaviour claim; drop or estimate mediation; address single-item validity | — | Major (transported, R1 W15, R1 W16, R2 W4, DA M5/M6) | absence: §3.3 Measures — expected an operational self-regulated learning behavioural measure matching the abstract's claim; checked §3.3 measure list, §3.4 analysis plan, Table 1 rows, and §4.1-4.3 | 5 — direct comparison of abstract claims against the enumerated measures (R1 W15) | R1 W15/W16, R2 W4, DA M5/M6 | P1 | 3–5 days for the claim; longer if a measure is added |
| R12 | Establish a locatable contribution increment: name the prior claim revised, extended, or contradicted | — | Critical (transported, EIC W3) | text: §1 "The present study contributes to this literature by examining the association between dashboard engagement and course retention in a single large undergraduate course" | 5 — editorial baseline for this submission class is precisely the judgement being made here (EIC W3) | EIC W3 | P1 | Not achievable on these data; requires a new design |

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| S1 | Document the dashboard artefact with a figure or annotated screenshot and a specification of the peer-comparison band | — | Major (transported, EIC W9) | absence: §3.1 and the §4 exhibit set — expected a figure or annotated screenshot documenting the dashboard interface and its peer-comparison band; checked §1, §3.1, §3.3, §4.1, §4.2, §4.3, Table 1, Table 2, §5.1 | 5 — venue norms for this track require the artefact to be shown (EIC W9) | EIC W9 | P2 | 1–2 days |
| S2 | Report whatever harm analyses the data permit — subgroup by prior achievement, exposure of non-retained students, goal-orientation moderation — and state plainly which harm questions the design cannot answer | — | Major (transported, R3 W4) | text: §2 "Being shown one's position relative to peers can discourage struggling students rather than mobilize them" | 4 — algorithmic accountability review of student-facing analytics deployments (R3 W4) | R3 W4 | P2 | 1 week with data access |
| S3 | If any institutional recommendation is retained, supply the parameters a funding decision requires | — | Major (transported, R3 W7) | absence: §6 institutional recommendation — expected a course retention base rate, a withdrawal timing distribution, dose-response information across session counts, a deployment cost figure, and comparison against alternative retention supports; checked §4.1, §4.2, §4.3, Table 1, Table 2, and §5 | 5 — I have advised three campuses on whether to fund dashboard rollouts (R3 W7) | R3 W7 | P2 | 1 week, or moot if §6 is rewritten per R5 |
| S4 | Sensitivity analysis across alternative sessionization windows, with a rationale for the 30-minute threshold | — | Major (transported, R1 W14) | text: §3.3 "following the platform's default sessionization rule" | 4 — the definitional gap is explicit; the magnitude of its influence is unknowable without the data (R1 W14) | R1 W14 | P2 | 3–5 days with data access |
| S5 | Add an operational definition of the final-exam outcome, including scoring, weighting, timing, and treatment of non-sitters | — | Minor (transported, EIC W12) | absence: §3.3 Measures — expected an operational definition of the final-exam outcome including scoring and administration timing; checked §3.1, §3.2, §3.3, §3.4, §4.1, Table 1, §4.3, Table 2 | 5 — straightforward completeness check of the Measures subsection (EIC W12) | EIC W12 | P3 | Hours |
| S6 | Round the perceived-control mean to a precision the single-item ordinal scale supports, consistently with adjacent table rows | — | Minor (transported, EIC W13) | table: Table 1, Perceived control (1-5) row reporting M = 3.847 against the one-decimal convention used in the adjacent rows | 5 — presentation convention, no recomputation required (EIC W13) | EIC W13 | P3 | Minutes |
| S7 | Rewrite the ten-student clarity item as prose or a table row rather than raw variable notation | — | Minor (transported, EIC W14) | text: §4.1 "the reported secondary-item values were N=10; M=3.00; sample SD=0.10; integer scale=1-5" | 5 — copy-editing judgement squarely within this dimension (EIC W14) | EIC W14 | P3 | Minutes |
| S8 | Add a per-measure *n* column to Table 1 separating the 142-case log sample from the 87-case item subsample | — | Minor (transported, R1 W17) | absence: Table 1 — expected a per-measure n column separating the 142-case log sample from the 87-case item subsample; checked Table 1 header, §3.2 sampling text, and the §4.1 narrative | 5 — the table's columns are visible and contain no *n* (R1 W17) | R1 W17 | P3 | Minutes |
| S9 | Resolve the SRL phase terminology drift between §1's reflective phase and §2's forethought/self-monitoring | — | Minor (transported, R2 W10) | text: §2 "dashboards are hypothesized to support the forethought and self-monitoring phases of learning" and §1 "phases of forethought, performance, and reflection" | 4 — standard phase definitions in the SRL tradition (R2 W10) | R2 W10 | P3 | Hours |
| S10 | Report the distribution of majors and year levels, or drop the "disciplinary breadth" claim | — | Minor (transported, R2 W9) | absence: §3.1 sample description — expected a reported distribution of majors or year levels evidencing disciplinary breadth; checked §3.1, §3.2, §4.1, Table 1, and Table 2 | 4 — based on what a reader would need to accept the breadth claim (R2 W9) | R2 W9 | P3 | Hours |
| S11 | Extend §5.1 to cover the consent question and the unmeasured-harm question | — | Minor (transported, R3 W3) | text: §5.1 "Several limitations qualify these findings. First, dashboard engagement was operationalized narrowly as session counts" | 4 — limitations-scoping review across analytics deployment appraisals (R3 W3) | R3 W3 | P3 | Hours; does not substitute for R1 or S2 |

> Transported metadata appears on every row above, not only on the Top Blocking rows. Severity is copied from each seat's explicit per-finding **Severity** tag and re-rated nowhere; where eligible seats tagged the same underlying finding at different bands, both are shown and the arbitration is recorded in Part 1. Confidence is each finding's own per-finding value with its stated basis. No `[SEVERITY-SOURCE: letter-fallback]` or `[CONFIDENCE-SOURCE: report-level]` tags were needed — all five cards carry per-finding severity and confidence in current format.

### Revision Checklist (Checkable List)

#### Priority 1 — Structural (four items are not resolvable by revising this manuscript: R1, R8, R12, and R9 pending editorial verification)
- [ ] R1: Document ethics approval and legal basis for trace-data analysis, or obtain retrospective consent, or withdraw the log-based analyses
- [ ] R2: Supply analysis data and code; resolve `M = 3.847` (n = 87) and `SD = 0.10` (n = 10, M = 3.00)
- [ ] R3: Reconcile the abstract's `r = .42` with the Results' `r = .24`; state the analysis of record
- [ ] R4: Re-derive the analytic sample; make every *n*, *df*, *t*, *p*, and table total consistent
- [ ] R5: Rewrite §5, §6, and the abstract in associational terms; bound all recommendations
- [ ] R6: Correct the Ferro & Nakamura attribution; rebuild the equity argument
- [ ] R7: Covariate-adjusted logistic regression; base rate, intervals, effect sizes
- [ ] R8: Full-cohort sampling frame; response rate; withdrawal timing; exposure normalisation
- [ ] R9: Verifiable citations; attribute load-bearing premises; engage a dashboard–outcome review
- [ ] R10: Relabel the outcome as single-course completion; remove institutional framing
- [ ] R11: Withdraw or substantiate the SRL-behaviour and mediation claims; address single-item validity
- [ ] R12: Establish a locatable contribution increment

#### Priority 2 — Content supplementation (estimated 2–3 weeks with data access)
- [ ] S1: Document the dashboard artefact
- [ ] S2: Report permissible harm analyses; state which harm questions the design cannot answer
- [ ] S3: Supply deployment parameters if any institutional recommendation is retained
- [ ] S4: Sessionization sensitivity analysis and threshold rationale

#### Priority 3 — Text and formatting (estimated 1–2 days)
- [ ] S5: Operationalise the final-exam outcome
- [ ] S6: Round the perceived-control mean to a supportable precision
- [ ] S7: Rewrite the clarity-item report as prose or a table row
- [ ] S8: Add a per-measure *n* column to Table 1
- [ ] S9: Resolve the SRL phase terminology drift
- [ ] S10: Evidence or drop the disciplinary-breadth claim
- [ ] S11: Extend §5.1 to the consent and harm questions

### Revision Deadline

**Not applicable.** The decision is Reject, so no revision deadline is set and no resubmission of this manuscript is invited. Constructive next steps, per Edge Case 2:

1. **Resolve R1 first.** If ethics approval covering the log data does not exist and retrospective consent is not obtainable, the log-based analyses cannot be published anywhere, and nothing downstream is worth doing.
2. **Resolve the reference-apparatus question (R9) before drafting anything.** Two readings remain open on this panel — template artefact or fabricated citations — and the panel did not resolve it. The answer changes what every other finding means.
3. **If both clear, a redesigned study is the path, not a revision.** R8 and R12 require new data and a new claim, not new prose: a full-cohort frame including pre-recruitment withdrawals, exposure-normalised engagement, covariate-adjusted logistic modelling, and a stated prior claim the study revises or contradicts.
4. **A smaller honest paper is available in the interim.** Three of five cards independently described the same scoped claim: that in one introductory statistics course, among students still enrolled and volunteering at mid-term, dashboard session count showed a small positive association with course completion, direction and mechanism unresolved. R1, R2, and the DA seat all judged that claim survivable after correction. It is a modest descriptive contribution and a Q2-tier submission at best, but it is defensible in a way the present manuscript is not.

### Response Letter Template

Should the authors pursue a new submission, use `templates/revision_response_template.md` and respond to every item above individually. Items R1, R8, R9, and R12 require a substantive statement rather than a change log — for each, state either what was obtained or newly collected, or that the item cannot be met and what the manuscript therefore no longer claims.

---

## Part 3: Reviewer Report Summary (Appendix)

These cards were produced in sprint-contract mode and therefore carry **dimension scores rather than an overall Accept/Revise/Reject recommendation**, and per-finding confidence rather than a single report-level Confidence Score. I report what the cards contain and do not synthesise the missing fields.

### Journal-Fit Reviewer (EIC) — Associate Editor, dashboard and feedback-intervention track
- Assessed: **D5 = block**, **D6 = block (fatal)**. All other dimensions `not_assessed` (outside eligible roles).
- Findings: 3 strengths, 14 weaknesses (3 Critical, 8 Major, 3 Minor). Per-finding confidence 4–5.
- Key point: topic fit is not in question, but no increment over the existing review consensus is locatable, and the ethics gap plus an unverifiable reference apparatus each bar publication prior to scientific merit.

### Peer Reviewer 1 (Methodology) — quantitative methodologist, reported-statistics integrity
- Assessed: **D1 = block (fatal)**, **D3 = block (repairable)**. All others `not_assessed`.
- Findings: 3 strengths, 17 weaknesses (6 Critical, 10 Major, 1 Minor). Per-finding confidence 4–5.
- Key point: the reported statistics cannot be reconciled to one dataset and two are arithmetically unreachable; the estimand is separately compromised by survivorship conditioning. Notably, this reviewer tested and **declined to fully claim** the one-directional error pattern the field brief anticipated.

### Peer Reviewer 2 (Domain) — learning analytics / SRL and retention
- Assessed: **D2 = block (repairable)**. All others `not_assessed`.
- Findings: 4 strengths, 13 weaknesses (2 Critical, 9 Major, 2 Minor). Per-finding confidence 3–5.
- Key point: a key source is cited against its own finding and the misread does structural work in §5; the SRL frame constrains no prediction; course completion is conflated with institutional persistence. Stopped short of fatal because a corrected empirical core could survive.

### Peer Reviewer 3 (Perspective) — learning analytics ethics and data governance
- Assessed: **D4 = block**. All others `not_assessed`.
- Findings: 3 strengths, 9 weaknesses (2 Critical, 5 Major, 2 Minor). Per-finding confidence 3–5.
- Key point: accessibility is adequate but the export is not earned — the paper's headline implications travel to populations and decision contexts the design cannot reach, and the population that would falsify the claim is structurally absent from the sample.

### Devil's Advocate
- Assessed: **D3 = block (repairable)**. All others `not_assessed`.
- Findings: 7 CRITICAL (C1–C7), 8 MAJOR (M1–M8). Per-finding confidence 4–5.
- Key point: a concede-and-proceed pattern in which every concession is made where it costs nothing and withdrawn where it would cost something. Constructed the strongest version of the paper's argument first, and identified the scoped claim that would survive repair — which is why D3 was scored `repairable` rather than fatal.
