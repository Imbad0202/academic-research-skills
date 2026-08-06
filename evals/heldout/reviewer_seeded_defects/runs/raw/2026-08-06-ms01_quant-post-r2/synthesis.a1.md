# Editorial Decision Package

**Contract**: `reviewer/reviewer_full/v2` · mode `reviewer_full` · stage `reviewer_full_review` · baseline `v3.20.0` · `panel_size: 5`
**Synthesizer mode**: v3.6.2 Sprint Contract (arithmetic). The general-protocol sub-claim inventory (Step 1b) is not used in this mode; roadmap traceability is carried by reviewer-card finding IDs instead.

---

## Part 0: Sprint Contract Arithmetic

### Step 1 — Role-scoped scoring matrix

Only seats whose `contract_role` appears in a dimension's `eligible_roles` are counted. Ineligible entries and `not_assessed` values are excluded from both numerator and denominator.

| Dim | Priority | Eligible roles | Assessed eligible seats | Scores | Dimension verdict |
|---|---|---|---|---|---|
| D1 methodology_rigor | mandatory | methodology | methodology (1) | `block` (block_class: **fatal**) | `block(fatal)` |
| D2 domain_accuracy | mandatory | domain | domain (1) | `block` (repairable) | `block` |
| D3 argumentative_coherence | mandatory | da, methodology | da, methodology (2) | `block` (repairable), `block` (repairable) | `block` |
| D4 cross_disciplinary_relevance | high | perspective | perspective (1) | `block` | `block` |
| D5 writing_and_structure | normal | eic | eic (1) | `block` | `block` |
| D6 venue_fit_and_contribution | mandatory | eic | eic (1) | `block` (block_class: **fatal**) | `block(fatal)` |

Exclusions applied: the `da` card's D6 entry is **ineligible** (`eligible_roles: [eic]`) and was excluded on that ground independently of the card's own self-correction to `not_assessed`. All `not_assessed` values from ineligible seats were excluded, not counted as abstentions.

**Audit verdict**: `block(fatal)` — worst assessed eligible score is `block`, and fatal blocks were declared by eligible seats on two mandatory dimensions (D1, D6).

### Step 2 — Failure-condition evaluation

| Condition | Severity | Quantifier | Expression | Per-dimension result | Fired |
|---|---|---|---|---|---|
| F1 | 95 | any | any mandatory dimension has a fatal block | D1 ✓ (methodology, fatal), D2 ✗, D3 ✗, D6 ✓ (eic, fatal) → `any` satisfied | **true** |
| F2 | 90 | any | any mandatory dimension scores 'block' | D1 ✓, D2 ✓, D3 ✓, D6 ✓ → `any` satisfied | **true** |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1 ✓ (n=1 → owner seat), D2 ✓ (n=1), D3 ✓ (n=2 → both seats), D6 ✓ (n=1) → ≥2 satisfied | **true** |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4 ✓ (perspective) → `any` satisfied | **true** |
| F5 | 40 | any | any dimension scores 'warn' or worse | all six ✓ → `any` satisfied | **true** |
| F0 | 10 | all | every dimension scores 'pass' | no dimension scores `pass` | false |

Fatal scope was tested only on mandatory dimensions (D1, D2, D3, D6), as the protocol requires.

### Step 3 — Precedence, decision, audit emission

Highest-severity fired condition: **F1 (95)** → `action: editorial_decision=reject`. No softening applied.

```
dimension_verdicts: [D1=block(fatal), D2=block, D3=block, D4=block, D5=block, D6=block(fatal)]
fired_conditions: [F1, F2, F3, F4, F5]
da_critical_adjudications: [C1=VALIDATED, C2=VALIDATED, C3=VALIDATED, C4=VALIDATED]
editorial_decision=reject
```

No `[DA-CRITICAL-VS-ACCEPT]` marker: the mechanical decision is `reject`, not `accept`. No `C<n>=REJECTED` entries, so no rejection-rationale lines are required.

**Cross-model blind decision check (#518)**: not run. `ARS_CROSS_MODEL` was not supplied with this invocation and no consent gate was passed, so no external transport was prepared and no handoff envelope emitted. No behavioural change.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript, *"Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment,"* for review. Five independent reviewers assessed it against the venue's six acceptance dimensions: a Journal-Fit Reviewer, a methodology reviewer, a domain reviewer, a cross-disciplinary reviewer (learning analytics ethics and student data governance), and a Devil's Advocate.

### Decision: Reject

This decision follows mechanically from the contract: two mandatory dimensions carry fatal blocks from their owning seats (D1 methodology rigor; D6 venue fit and contribution), which fires F1 at severity 95. I state plainly that the decision was not reached by weighing tone, distribution, or reviewer count — it is the arithmetic result of the scoring matrix in Part 0.

### Review Panel Provenance (#540)

No provenance stamp accompanied this invocation. Mode is `reviewer_full`, in which this block is mandatory and may be neither omitted nor inferred, so I record the input gap rather than assert any of the three permitted statements. It is **not established here** whether a cross-model reviewer slot was active, whether the panel ran single-family, or whether dispatch failed to a fallback. Readers must not infer model independence across the five seats from this letter. No cross-family aggregate and no "same-model majority" has been computed; per-seat scores are visible by inspection in the Part 0 matrix.

### Consensus Analysis

Under the role-scoped contract, dimensions are owned by specific seats, so "consensus" here means corroboration across seats on individual findings, not multi-seat voting on a dimension. Corroboration counts below are stated against the five-seat panel.

#### Points of agreement

- **[5/5] Causal and policy overreach in §5–§6 against the manuscript's own §1 standard.** Journal-Fit W2 (Critical), methodology W8 (Critical), perspective W7 (Major), DA C2 (Critical); domain W2 corroborates on scope. Every seat reached this independently, and each supplied a distinct warrant — the field's split-ownership structure held: methodology owns the inference-to-design mismatch, domain owns construct scope and generalisation, perspective owns action-recommendation risk. Merged as one roadmap item (R9) with three warrants, not counted three times.
- **[5/5] Abstract r = .42 vs §4.2 r = .24.** Journal-Fit W3, methodology W6, domain W6, DA C1; perspective notes it explicitly as outside its seat. The paper's single most-read quantity is unknown.
- **[4/5] Perceived-control df = 156 is unattainable from any reported sample.** Methodology W1 (Critical, receipt AR5), Journal-Fit W9, DA C4. Not raised by domain or perspective, both of which deferred it explicitly to the methodology seat — that is deferral, not dissent.
- **[4/5] Sampling account is internally contradictory and the coverage rate is never reported.** Methodology W9, Journal-Fit W5, DA M4/M5/M13, perspective W5 (on who is structurally excluded).
- **[4/5] Ferro & Nakamura (2021) is cited against its own listed title, and the inversion is load-bearing.** Domain W1 (Critical), Journal-Fit W8, perspective W4, DA M6.
- **[3/5] Table 2's 127 contradicts the stated N = 142 and df = 140.** Methodology W3 (AR8), Journal-Fit W4, DA M2.
- **[3/5] Ethics approval, lawful basis, and data availability statements are entirely absent, with §3.2 disclosing that students were not informed their dashboard activity would be analysed.** Perspective W1 (Critical) / W2, Journal-Fit W6, DA M12.
- **[3/5] Reference apparatus cannot be verified from the identifiers supplied** (all entries under the reserved `10.5555` test prefix). Journal-Fit W7, domain W7, DA (minor). **Three seats independently declined to assert fabrication.** I preserve that: non-existence is **unverified**, and this letter asserts nothing about it.
- **[2/5] Exposure-window confound: the outcome mechanically truncates the predictor.** Methodology W7 (Critical), DA C3 (Critical). Only two seats, but both owners of the relevant dimensions, both at high confidence, and neither contradicted.
- **[Also creditable, 5/5]** Every seat independently named real strengths: §2 states the field's methodological problem against interest; §3.1 and §3.3 disclose design and analytic compromises rather than burying them; §3.3's sessionisation rule is replicable; the retention correlation is the one statistic that reproduces (methodology S1). §3.2's disclosure of non-notification is the candour that made this review possible at all.

#### Points of disagreement

1. **Remediability — the panel's one substantive divergence.** Methodology, domain, perspective and the DA each describe a repair path: methodology scores D1 fatal but frames the defect as traceable with case-level data and script; domain scores D2 `repairable`; the DA scores D3 `repairable` and states a coherent modest thesis is recoverable; perspective states the core association survives most of its findings. The Journal-Fit Reviewer scores D6 fatal on the opposite ground: the contribution deficit **is not repairable within the current data collection**, because correcting every statistic and deleting every causal verb still leaves a local audit.
   - **Editor's resolution**: Both hold, at different levels, and they are not in conflict. The four repair paths are internal to the manuscript; the Journal-Fit finding is about what the dataset can produce. Sustained on expertise-first grounds: D6 is the Journal-Fit seat's owned and sole-eligible dimension, and its confidence-5 rationale (no new measure, no mechanism test, no disconfirming result, no named prior study improved upon, plus §2's own concession that the engagement measure is the field's standard coarse proxy) is specific and evidenced, not asserted. It changes nothing mechanically — F1 fires on either fatal — but it is why revision of this manuscript is not the recommended route.
2. **Whether the consent gap is remediable at all.** Perspective W1 states this turns on facts the manuscript does not supply: an existing-but-unreported approval is a disclosure fix, whereas no approval for already-analysed identifiable trace data is likely not curable retrospectively. No other seat has standing to resolve it.
   - **Editor's resolution**: **Unresolved dissent, recorded as such.** The panel did not resolve it, and I apply no directional prior in either direction. The authors must address it (R10); I neither presume an approval exists nor presume none does.
3. **Nearest attainable sample SD for the clarity item.** Methodology AR3 derives 0.4714 (SS = 2), showing SS = 1 is unreachable because integer deviations from an integer mean cannot sum to zero with a single unit deviation. DA M9 states 0.316.
   - **Editor's resolution**: Methodology's value stands. Expertise-first (D1 owner) and evidence-first (a full receipt with stated assumptions, comparison rule and rounding interval, versus an unshown figure that appears to use an *n*-denominator on an unreachable SS). Both seats agree the reported 0.10 is impossible; only the nearest-attainable value differs, and no decision turns on it.
4. **The perceived-control SD = 0.62.** DA M8 flags it as sitting "uneasily" with the stated range. Methodology AR2 returns `not_computable` (`mean_grim_inconsistent`), declining to test it because no candidate response vector exists while the mean is GRIM-inconsistent.
   - **Editor's resolution**: Methodology's abstention is the disciplined position and stands. DA's unease is not a receipt. The authors need only fix the mean (R6) for this to become checkable.
5. **Reference-list arithmetic across cards.** Journal-Fit and DA state 15 entries with 9 uncited; domain states 16 entries with 8 uncited, while enumerating 9 names.
   - **Editor's resolution**: Direct count of the supplied reference list yields **15 entries**; in-text citations are Calloway 2019, Ferro & Nakamura 2021, Osei 2020, Rutledge & Berange 2022, Vandermeer 2023, Ibarra 2023 — **6 cited, 9 uncited**. This matches the enumerated name lists in *all* cards, including domain's. The numerals 16 and 8 are transcription slips; the substance is not in dispute.

### Devil's Advocate critical adjudications

All four DA CRITICAL issues are adjudicated **VALIDATED**, each corroborated by at least one other seat on independent evidence. None is treated as an automatic veto; each is validated on its own evidence.

- **C1 (r = .42 vs .24)** — VALIDATED. Corroborated by three further seats; methodology AR4 shows *p* = .004 is consistent with .24 at *N* = 142, so this is not a rounding variant.
- **C2 (causal/policy claims from an unmanipulated cross-sectional design)** — VALIDATED. Unanimous corroboration; the manuscript's own §1 and its citation of Ibarra (2023) supply the standard it breaks.
- **C3 (exposure-window truncation)** — VALIDATED. Independently derived by methodology W7 at confidence 5 as standard exposure-window confounding. The DA's own confidence of 4 correctly reflects that raw logs were unavailable; validation rests on the design description, which is sufficient.
- **C4 (df = 156 unattainable)** — VALIDATED. Methodology AR5 supplies the receipt, including the Welch upper bound that closes the obvious escape route.

### Decision Rationale

This manuscript is rejected because two mandatory dimensions carry fatal blocks, and the two failures are independent of each other.

The first is arithmetic. Five reported quantities cannot be produced by the data the paper describes: *df* = 156 on an item answered by 87 respondents within a sample of 142; *t*(140) = 1.31 paired with *p* = .008, which fails under both tail conventions; Table 2 summing to 127 against a text that affirmatively states all 142 were classified; a mean of 3.847 unreachable from 87 integers; and a sample SD of 0.10 unreachable from ten integers summing to 30. These are not revision items. No rewriting produces a degree of freedom the described data cannot generate, so the reported findings are currently non-evaluable pending case-level data and analysis code — which the manuscript also does not provide. The audit is targeted, not blanket: the headline retention correlation reproduces, which is precisely what makes the other five diagnostic rather than dismissible as formatting.

The second is contribution, and it survives every correction. The manuscript joins a saturated sub-literature, concedes in §2 that its engagement measure is the field's standard coarse proxy, runs no mechanism test, reports no disconfirming result, and nowhere states what it adds relative to a named prior study — including the two most on-point sources sitting uncited in its own bibliography. Repositioning cannot manufacture an increment the data collection did not produce.

Two further findings would independently block acceptance at a venue with a human-subjects policy: trace data analysed without informing students, with no approval or lawful-basis statement; and a cited source characterised against its own findings, with the inversion load-bearing in both §2 and §5.

What is genuinely working should be said. The Literature Review engages the critical literature rather than assembling a supportive wall. §3.1 and §3.3 disclose their own constraints. §5.1 names four real limitations unprompted. The Introduction states the correct epistemic standard. The failure here is numerical control, claim calibration, and governance disclosure — not competence. That is why the roadmap below is written to be actionable, and why I recommend a new design over a revision of this one.

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| 1 | No stated or achievable increment over the saturated dashboard–outcome literature; the deficit is not repairable within the current data collection (fatal block, D6) | Journal-Fit (EIC-W1) | `absence: §1 and §2 — expected an explicit statement of the increment this study adds over the cited dashboard-outcome studies; checked Abstract, §1, §2, §5, §6` | R1 |
| 2 | Five reported statistics are unreachable from the described samples, making the findings non-evaluable; no data or code is supplied to adjudicate them (fatal block, D1) | R1 methodology (MET-W1/AR5, W2/AR7, W3/AR8, W4/AR1, W5/AR3), Journal-Fit (W4, W9, W10), DA (C4, M1, M2, M8, M9) | `text: §4.3 "t(156) = 3.02, p = .003"` (AR5: implied total 158 vs 87 scored responses, 142 maximum) | R2 (with R4–R7, R17) |
| 3 | Behavioural trace data analysed without informing students; no ethics approval, lawful basis, anonymisation/retention terms, or data availability statement anywhere | R3 perspective (PER-W1 Critical, W2), Journal-Fit (W6), DA (M12) | `text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study."` | R10 |

### Required Item Details

#### R1
- **Acceptance criteria**: The manuscript states, in the Abstract and §1, what it adds relative to at least one named prior study, and that increment is one of a new or validated measure, a mechanism test, a disconfirming result, or a dataset of scale-changing size — none of which the present data collection supports, so this is satisfied only by a new design.

#### R2
- **Acceptance criteria**: The perceived-control comparison is recomputed from case-level data on a stated sample whose size is consistent with the reported degrees of freedom, or the result is withdrawn.

#### R3
- **Acceptance criteria**: A single value for the engagement–retention association appears in both the Abstract and §4.2, with a statement of which analysis produced it and how the other figure arose.

#### R4
- **Acceptance criteria**: The final-exam comparison reports a *t*, *df* and *p* that are mutually consistent under a stated tail convention, and the surrounding prose describes the result the statistic actually supports at the stated α.

#### R5
- **Acceptance criteria**: Table 2's group sizes sum to the analysed total implied by the reported degrees of freedom, with the median tie rule stated and any excluded cases accounted for.

#### R6
- **Acceptance criteria**: The reported perceived-control mean is attainable as an integer sum divided by its stated denominator, or the denominator or scale is corrected to match.

#### R7
- **Acceptance criteria**: The clarity item's reported sample SD is attainable from ten integer responses summing to 30 on a 1–5 scale, or the underlying responses are supplied.

#### R8
- **Acceptance criteria**: Dashboard engagement is measured over a window every student shares — a per-enrolled-week rate, or sessions counted only to a common early cut-point — with a sensitivity analysis reported, before any directional or associational reading is offered.

#### R9
- **Acceptance criteria**: No sentence in §5 or §6 asserts that dashboard engagement improved, raises, or dependably improves retention, generalises beyond the studied course, or recommends institutional investment; §5's third-paragraph calibration becomes the paper's stated claim.

#### R10
- **Acceptance criteria**: The manuscript states an ethics approval or documented waiver covering analysis of the behavioural logs, the lawful basis for secondary use, anonymisation and retention terms, and a data availability statement — or, if no approval covering the log analysis exists, the log-based analysis is withdrawn.

#### R11
- **Acceptance criteria**: Every reference carries a resolvable identifier that a reader can check, and the editorial office confirms resolution against an index.

#### R12
- **Acceptance criteria**: Ferro & Nakamura (2021) is characterised in §2 consistently with its own findings, and §2's equity rationale and §5's interpretive warrant are rebuilt on what it actually reports.

#### R13
- **Acceptance criteria**: §3.2 gives one recruitment mechanism, reports the enrolment denominator and response/coverage rate, and §5.1 lists volunteer self-selection and mid-term survivorship among the limitations.

#### R14
- **Acceptance criteria**: The Abstract no longer claims that self-regulated learning behaviour was measured, and §5 draws no SRL inference, unless a validated SRL instrument is added in new data collection.

#### R15
- **Acceptance criteria**: The outcome is named course completion throughout, withdrawal and enrolled-but-absent counts are reported separately, and §6 makes no claim about retention across programmes or disciplines.

#### R16
- **Acceptance criteria**: The binary outcome is modelled with logistic regression including at least prior-achievement and general-course-activity covariates, the bivariate coefficient is labelled point-biserial with the marginal retention split reported, and the continuous engagement predictor is used rather than the median split.

#### R17
- **Acceptance criteria**: Software name and version, the analysis script, a data availability statement, a codebook, and the full instrument text are supplied, sufficient for a reader to reproduce every reported statistic.

---

## Part 2: Revision Roadmap

> **Direction of travel.** The decision is Reject, so this roadmap is not a revise-and-resubmit checklist for this venue. It has two uses. Items R1 and R8 are what a *new* study must be designed to satisfy; the remainder are what any version of this work must satisfy at any reputable venue. On the panel's own reasoning (disagreement 1 above), a corrected version of this manuscript would still lack a contribution increment, so the productive route is a redesigned study rather than a revision.

> **Sub-Claim column**: `—` throughout. This synthesis ran in v3.6.2 sprint-contract arithmetic mode, which does not build the general protocol's Step 1b sub-claim inventory. Traceability is carried instead by reviewer-card finding IDs in the `Source` column, which is stronger provenance: every item resolves to a named finding in a named seat's card.

> **Ordinal contract (#576 §5.1)**: the `### Required Item Details` blocks above are `R1..R17`, contiguous, in this table's row order.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| R1 | State and evidence a contribution increment over named prior work, or re-scope into a study whose data collection can produce one | — | Critical | `absence: §1 and §2 — expected an explicit statement of the increment this study adds over the cited dashboard-outcome studies; checked Abstract, §1, §2, §5, §6` | 5 — handles this journal's single-institution dashboard stream, screens against this criterion | EIC-W1 | P1 | Not achievable with the present dataset; new design |
| R2 | Recompute or withdraw the perceived-control comparison: *df* = 156 requires 158 cases against 87 scored responses and a 142 maximum | — | Critical | `text: §4.3 "t(156) = 3.02, p = .003"` (receipt AR5) | 5 — direct application of the df identity for the named test | MET-W1/AR5; corrob. EIC-W9, DA-C4 | P1 | Not repairable by revision; requires case-level data + script |
| R3 | Resolve r = .42 (Abstract) vs r = .24 (§4.2) and state which analysis produced which | — | Major | `text: Abstract "Dashboard engagement correlated positively with retention (r = .42)"; §4.2 "(r = .24, p = .004)"` | 5 — direct comparison of two reported values for the same parameter | MET-W6; corrob. EIC-W3, DOM-W6, DA-C1 | P1 | 1 day once the source analysis is identified |
| R4 | Recompute the final-exam comparison; *t*(140) = 1.31 gives *p* ≈ .19 two-tailed / ≈ .096 one-tailed, and the prose contradicts the printed *p* in the opposite direction | — | Major | `text: §4.3 "the difference was small, t(140) = 1.31, p = .008"` (receipt AR7) | 5 — recomputation from a fully specified statistic and df | MET-W2/AR7; corrob. EIC-W10, DA-M1 | P1 | Not repairable by revision; requires data |
| R5 | Reconcile Table 2's 66 + 61 = 127 with the stated *N* = 142 and *df* = 140, and state the median tie rule | — | Major | `table: Table 2, n column, 66 high-engagement and 61 low-engagement cases` (receipt AR8) | 5 — arithmetic against a reported df identity | MET-W3/AR8; corrob. EIC-W4, DA-M2 | P1 | 1–2 days with the analytic file |
| R6 | Correct the GRIM-inconsistent perceived-control mean: 3.847 × 87 = 334.689; adjacent attainable means are 3.8391 and 3.8506 | — | Major | `text: §4.1 "was 3.847 (SD = 0.62) on the 1-5 scale"` (receipt AR1) | 5 — granularity check on a stated N, precision and integer scale | MET-W4/AR1; corrob. DA-M8 | P1 | 1 day with the response-level data |
| R7 | Correct the clarity item's unattainable sample SD = 0.10; attainable values begin 0, 0.4714, 0.6667 | — | Major | `text: §4.1 "the reported secondary-item values were N=10; M=3.00; sample SD=0.10; integer scale=1-5"` (receipt AR3) | 5 — reachability enumeration on a fully specified scale and N | MET-W5/AR3; corrob. DA-M9 | P1 | Under 1 day with the ten responses |
| R8 | Normalise the exposure window (sessions per enrolled week, or a common early cut-point) with sensitivity analysis, before offering any reading of the association | — | Critical | `text: §3.3 "the number of distinct sessions in which a student opened the dashboard view during the term"` and `"was coded dichotomously as whether the student remained enrolled and completed the final assessment"` | 5 — standard exposure-window confounding in observational trace-data designs | MET-W7; corrob. DA-C3 | P1 | 1–2 weeks with held logs; redesign if the association does not survive |
| R9 | Withdraw all causal and policy claims from §5 and §6 (three warrants: inference-to-design, construct scope, action-recommendation risk) | — | Critical | `text: §1 "We are careful throughout to distinguish the pattern in the data from the causal story"; §5 "dashboard engagement improved course retention"; §6 "a dependable strategy for improving retention across programs and disciplines"` | 5 — claim–evidence calibration; inference-to-design matching | EIC-W2, MET-W8, PER-W7, DA-C2; scope corrob. DOM-W2 | P1 | 3–5 days; requires a rewritten Conclusion, not a copy-edit |
| R10 | Supply ethics approval or documented waiver covering the log analysis, lawful basis for secondary use, anonymisation and retention terms, and a data availability statement; address the non-notification | — | Critical | `text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study."` | 5 — consent architecture for secondary use of LMS trace data is this seat's primary competence | PER-W1 (Critical), PER-W2; corrob. EIC-W6, DA-M12 | P1 | Days if an unreported approval exists; **may be unachievable retrospectively if none does** (panel unresolved) |
| R11 | Supply resolvable identifiers for every reference; all 15 entries currently carry the reserved `10.5555` test prefix | — | Major | `text: §References, all entries under one prefix, e.g. "https://doi.org/10.5555/1010203"` and `"https://doi.org/10.5555/1516718"` | 4 — prefix uniformity verified by inspection; source existence **unverified** | EIC-W7; corrob. DOM-W7 (conf. 3) | P1 | Days; requires editorial-office resolution against an index |
| R12 | Correct the Ferro & Nakamura (2021) inversion and rebuild §2's equity paragraph and §5's interpretive warrant on what the source reports | — | Critical | `text: §2 "Dashboards have been shown to reliably improve outcomes for lower-achieving students"; References "When dashboards demotivate: Peer comparison and the lower-achieving student"` | 5 — verifiable from the manuscript's own reference list | DOM-W1 (Critical); corrob. EIC-W8, PER-W4, DA-M6 | P1 | 1 week; §2 and §5 both change |
| R13 | Give one truthful sampling account, report the enrolment denominator and coverage rate, and carry volunteer plus mid-term survivorship selection into §5.1 | — | Major | `text: §3.2 "Participants were drawn from the course enrollment using a random sample of students enrolled in the course section"` and `"Students who chose to respond, and who consented to the survey, formed the study sample; those who did not respond were excluded"` | 5 — routine assessment of sampling frames in survey-plus-log designs | MET-W9; corrob. EIC-W5, DA-M4/M5/M13, PER-W5 | P1 | 3–5 days |
| R14 | Delete the Abstract's SRL measurement claim and §5's SRL warrant, or add a validated SRL instrument in new collection | — | Major | `text: Abstract "we measured dashboard engagement, self-regulated learning behavior, and course persistence"; §5 "consistent with a self-regulated learning account in which dashboards scaffold monitoring and adjustment"` | 5 — SRL instrumentation requirements are well established and none is present | DOM-W3 | P1 | 2–3 days to delete; new collection to instrument |
| R15 | Rename the outcome course completion throughout, report withdrawal and enrolled-but-absent counts separately, and rescope §6 | — | Major | `text: §6 "a dependable strategy for improving retention across programs and disciplines"; §3.3 "whether the student remained enrolled and completed the final assessment"` | 5 — standard terminological boundary in the persistence literature | DOM-W2; corrob. DA-M11 | P1 | 3–5 days |
| R16 | Model the binary outcome appropriately (logistic with covariates), label the bivariate coefficient point-biserial with the marginal split, and analyse the continuous predictor | — | Major | `text: §3.4 "Associations between continuous measures were assessed with Pearson correlations"` | 5 — model-selection standards for binary outcomes in educational measurement | MET-W10; corrob. MET-W14, DA (minor) | P1 | 2–3 weeks; re-analysis, not relabelling |
| R17 | Supply reproducibility affordances: named software and version, analysis script, data availability statement, codebook, full instrument | — | Major | `absence: Analysis and end matter reproducibility affordances — expected named software with version, a data availability statement, and analysis code; checked §3.4 analysis, §3.3 measures, §5.1 limitations, §6 conclusion, and the reference list` | 5 — reproducibility reporting standards for LMS trace-data studies | MET-W12 | P1 | 1 week; **prerequisite for R2, R4–R7** |

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| S1 | Treat the ~39% item nonresponse: report the item response rate, name the missing-data mechanism, compare responders with nonresponders, add sensitivity analysis | — | Major | `absence: Methods and Results treatment of item nonresponse — expected a stated missing-data mechanism, an item response rate, and a comparison of responders with nonresponders; checked §3.2, §3.3, §3.4, §4.1, Table 1, §5.1` | 5 — standard missing-data reporting for survey-linked trace data | MET-W11 | P2 | 1 week |
| S2 | Run subgroup analysis by prior achievement, discuss differential effects explicitly, and state what harm monitoring accompanied the peer-comparison band | — | Major | `text: §3.1 "a peer-comparison band"; "available to all enrolled students from the first week of the term and required no separate opt-in"` | 5 — has halted dashboard pilots over peer-comparison harm | PER-W3; corrob. DA-M7 | P2 | 1–2 weeks; needs whole-cohort data to be meaningful |
| S3 | Engage Halloran (2020) and Wexler & Ojo (2020) in the text, and either cite or remove the 9 uncited entries | — | Major | `absence: §2 Literature Review and §5 Discussion — expected in-text engagement with Halloran (2020) and Wexler & Ojo (2020); checked every in-text citation in §1 through §6 against the reference list` | 5 — direct enumeration of in-text citations against the reference list | DOM-W4; corrob. EIC-W7, DA (minor) | P2 | 1–2 weeks; §2 substantially rewritten |
| S4 | Specify the deployed dashboard (displayed metrics, peer-comparison band visual, refresh cadence) and supply cost, staffing and infrastructure figures for any scale claim | — | Major | `absence: §3.1 and §6 — expected an interface specification of the deployed dashboard covering displayed metrics, visual design of the peer-comparison band, and refresh cadence, together with cost, staffing, and infrastructure requirements for the recommended scale-up; checked §3.1, §3.3, §4, §5.1, §6` | 5 — advising campus deployments on feasibility is this seat's institutional role | PER-W6 | P2 | 1 week |
| S5 | Report confidence intervals and standardised effect sizes for the correlation and both comparisons, plus a power or precision statement | — | Minor | `absence: Inferential reporting in Results — expected confidence intervals and standardised effect sizes for the correlation and both t-tests, plus a power or precision statement; checked §3.4, §4.2, §4.3, Table 1, Table 2` | 5 — routine effect-size and interval reporting standards | MET-W13; corrob. EIC-W11 | P2 | 2–3 days |
| S6 | Analyse the continuous engagement predictor and reserve the median split for illustration; state the tie rule | — | Minor | `text: §3.3 "students were split at the median number of dashboard sessions into high-engagement and low-engagement groups"` | 5 — standard critique of dichotomising skewed continuous predictors | MET-W14 | P2 | 3–5 days (folded into R16) |
| S7 | Operationally define the final exam score: composition, scoring, raw vs curved, and handling of non-sitting students | — | Minor | `absence: Measures section definition of the final exam outcome — expected an operational definition, scoring range, and administration details; checked §3.1, §3.3, §3.4, §4.3, Table 1` | 5 — measurement documentation requirements for analysed variables | MET-W15 | P2 | 1 day |
| S8 | Drop the mediation claim or test it; the mediator is a single item collected simultaneously with the predictor and the reverse path is equally consistent | — | Major | `text: §5 "It also complements accounts emphasizing perceived control as a mediating construct"` | 5 — comparison of the mediation claim against the stated analysis plan | DA-M10 | P2 | 2–3 days to drop |
| S9 | State the tail convention in §3.4; two receipts (AR4, AR6) returned `not_computable` on tail ambiguity alone, including for the one statistic that otherwise reproduces | — | Minor `[SEVERITY-SOURCE: letter-fallback]` | `text: §3.4 "an alpha of .05 was adopted throughout"` (AR4 / AR6, `not_computable_reason: tail_ambiguous`) | 5 — stated in the methodology card's receipts and body `[CONFIDENCE-SOURCE: report-level]` | MET (Review Body, AR4/AR6) | P2 | Under 1 day |
| S10 | Ground the retention framing in a theory of student departure, or drop retention framing in favour of course completion | — | Minor | `absence: §1 theoretical framing — expected an account of student departure grounded in persistence theory; checked §1, §2, §5, and the reference list for Tinto, Bean, or successor departure models` | 4 — absence confirmed by reading; some allowance that the venue may not require it | DOM-W5 | P2 | 1 week |
| S11 | Distinguish engagement worth encouraging from engagement merely counted; address proxy-gaming and surveillance exposure before any actionability claim | — | Major | `text: §6 Conclusion "encouraging students to engage with them is a dependable strategy"` | 4 — proxy-optimisation and trust effects recur in advised deployments; effect size untested | PER-W8 | P2 | 3–5 days (interacts with R9) |
| S12 | Reduce reported precision to two decimals throughout, matched to the measure | — | Minor | `table: Table 1, Perceived control (1-5) row, M column` | 5 — reporting-precision conventions for single-item ordinal measures | MET-W16; corrob. EIC-W11 | P3 | Under 1 day |
| S13 | Gloss field-specific vocabulary (sessionization, performance-avoidance orientation, SRL phases, the platform default) for the institutional audience §6 addresses | — | Minor | `text: §3.3 "following the platform's default sessionization rule"` | 4 — routinely translates LA reports for ethics panels and institutional committees | PER-W9 | P3 | 1 day |

> **Transported metadata.** Every row above carries the driving finding's transported Severity, typed Evidence Anchor, and per-finding Confidence, copied from the reviewer cards rather than re-derived. Two fallback tags travel with S9, whose source is the methodology card's Review Body and receipts rather than a numbered weakness, so it carries no per-finding severity or confidence tag of its own. No editorial-channel items were created: every item resolves to a numbered reviewer finding or a named receipt.

### Revision Checklist

#### Priority 1 — Structural (estimated 8–14 weeks of work, plus items that cannot be completed at all with the present data)
- [ ] R1: Establish a contribution increment over named prior work — **not achievable with this dataset**
- [ ] R2: Recompute or withdraw the perceived-control comparison (df = 156)
- [ ] R3: Resolve r = .42 vs r = .24
- [ ] R4: Recompute the final-exam comparison (t = 1.31 / p = .008)
- [ ] R5: Reconcile Table 2's 127 with N = 142 and df = 140
- [ ] R6: Correct the GRIM-inconsistent mean (3.847)
- [ ] R7: Correct the unattainable clarity-item SD (0.10)
- [ ] R8: Normalise the exposure window and re-estimate
- [ ] R9: Withdraw all causal and policy claims in §5–§6
- [ ] R10: Supply ethics approval, lawful basis, retention terms, data availability — **may be unachievable retrospectively**
- [ ] R11: Supply resolvable reference identifiers
- [ ] R12: Correct the Ferro & Nakamura inversion; rebuild §2 and §5
- [ ] R13: One sampling account, with coverage rate and selection limitations
- [ ] R14: Remove or instrument the SRL claim
- [ ] R15: Rename the outcome; rescope §6
- [ ] R16: Re-analyse with an appropriate model and covariates
- [ ] R17: Supply reproducibility affordances (**do this first — R2 and R4–R7 depend on it**)

#### Priority 2 — Content supplementation (estimated 6–9 weeks)
- [ ] S1: Missing-data treatment for the perceived-control item
- [ ] S2: Subgroup analysis by prior achievement; differential-effects discussion
- [ ] S3: Engage Halloran (2020) and Wexler & Ojo (2020); resolve the 9 uncited entries
- [ ] S4: Specify the dashboard interface; supply resourcing figures
- [ ] S5: Confidence intervals, effect sizes, precision statement
- [ ] S6: Analyse the continuous predictor; state the tie rule
- [ ] S7: Define the final exam measure
- [ ] S8: Drop or test the mediation claim
- [ ] S9: State the tail convention in §3.4
- [ ] S10: Ground or drop the retention framing
- [ ] S11: Address proxy-gaming and surveillance exposure

#### Priority 3 — Text and formatting (estimated 2 days)
- [ ] S12: Two-decimal precision throughout
- [ ] S13: Gloss field-specific vocabulary

### Next steps (Reject)

There is no resubmission deadline, because there is no revise-and-resubmit invitation. The constructive path, in order:

1. **Do R17 and R10 first, before any writing.** Locate the analysis script and case-level data, and establish whether an ethics approval covering the log analysis exists. Both are threshold facts. If the data and script cannot be produced, or no approval covering the logs exists and none can be obtained, the log-based analysis cannot be published anywhere and the remaining items are moot.
2. **Then resolve R8.** If the association does not survive exposure-window normalisation, the finding does not exist, and that is worth knowing before further investment. If it does survive, you have a real result.
3. **Then address R1 by design, not by writing.** The panel's judgement is that no revision of this manuscript produces a contribution increment. A study that would: a dashboard-exposure design with temporal separation, whole-cohort logs rather than a self-selected survey sample, a validated SRL instrument, prior-achievement stratification to address the who-benefits question the paper raises and does not answer, and multi-course or multi-term coverage. That design would also make R14, S2 and S10 satisfiable rather than merely deletable.
4. **On venue.** Once the numbers are reconciled and the claims rescoped, the *Journal of Learning Analytics* is the natural disciplinary home, and it is also the venue most likely to insist that §1's stated standard be honoured in §6. BJET and AJET are realistic alternatives, both of which will expect the multivariable model in R16 and the governance statements in R10. A study centred on course completion rather than institutional persistence should not be pitched to retention journals under the current outcome definition (R15).
5. **A note on what is worth keeping.** Four seats independently credited §2's engagement with the critical literature, §3.1/§3.3's disclosure of design and analytic compromises, §3.3's replicable sessionisation rule, and §3.2's candour about non-notification. The methodology seat verified that the headline retention correlation reproduces exactly. You already hold the epistemic standard this manuscript breaks — §1 states it, and §5's third paragraph applies it correctly. The gap is between that paragraph and the two sections that follow it.

### Response Letter Template

If any part of this work is resubmitted here in future, respond to every item above using the format in `templates/revision_response_template.md`, one entry per R/S identifier, each stating what changed and where.

---

## Part 3: Reviewer Report Summary (Appendix)

The cards supplied were sprint-contract cards carrying per-dimension scores rather than an overall recommendation field. I report the dimension verdicts and do not synthesise recommendation labels or report-level confidence scores that the cards did not contain.

### Journal-Fit Reviewer (role: eic — owns D5, D6)
- D5 `block`; D6 `block` / **fatal**. Findings: 3 strengths, 11 weaknesses (2 Critical, 7 Major, 2 Minor).
- Key point: the manuscript states the field's correct epistemic standard in §1, cites the audit of exactly this failure mode in §2, then commits it in §5–§6; and the sub-literature it joins is saturated, with no increment stated and none achievable within the present scope.

### Peer Reviewer 1 — Methodology (role: methodology — owns D1, eligible D3)
- D1 `block` / **fatal**; D3 `block` / repairable. Findings: 3 strengths, 16 weaknesses (3 Critical, 9 Major, 4 Minor), plus 8 arithmetic receipts (5 mismatch, 3 not_computable).
- Key point: five reported quantities are unreachable from the described samples and no prose revision can repair them; the one statistic that reproduces makes the failures diagnostic rather than dismissible; and the outcome definition mechanically truncates the predictor.

### Peer Reviewer 2 — Domain (role: domain — owns D2)
- D2 `block` / repairable. Findings: 3 strengths, 7 weaknesses (1 Critical, 5 Major, 1 Minor).
- Key point: a cited source is characterised against its own findings and the inversion is load-bearing in both §2 and §5; "retention" names a construct the study did not measure; SRL is claimed as measured, is not, and is then used as an interpretive warrant.

### Peer Reviewer 3 — Cross-disciplinary / LA ethics and data governance (role: perspective — owns D4)
- D4 `block`. Findings: 3 strengths, 9 weaknesses (1 Critical, 7 Major, 1 Minor).
- Key point: the paper's primary predictor comes from trace data students were not told would be analysed, with no approval or lawful basis stated; a peer-comparison band was an unavoidable condition of enrolment with no harm monitoring; and the population most at risk of harm is structurally excluded from the sample.

### Devil's Advocate (role: da — owns D3)
- D3 `block` / repairable; D6 entry emitted then self-corrected to `not_assessed` (and ineligible regardless). Findings: 4 CRITICAL (all VALIDATED), 13 MAJOR, plus recorded minors.
- Key point: a coherent modest thesis exists inside the manuscript and the paper does not argue for it; the central empirical quantity may be an artefact of enrolment duration; and limitations are acknowledged where they are cheap and omitted where they would cost the conclusion.

---

## Card and Input Integrity Flags (advisory — flagged, not fixed)

Per the phase boundary, I record these rather than repair them.

1. **Missing `measurement_procedure` artifacts.** The contract requires `contract_paraphrase` and `scoring_plan` output before the paper, with `paraphrase_minimum_dimensions: all`. Neither artifact was present in the five cards supplied to me. The `eic` card contains a `## Scoring Plan Dissent` section stating its Phase 1 plan stands; no paraphrase or plan schema entries (`dimension_id`, `what_to_look_for`, `what_triggers_block`, `what_triggers_warn`, `what_triggers_fatal`) appear in any card. I cannot verify Phase 1 compliance with `measurement_procedure` from the inputs I received. This did not affect the arithmetic, which operates on the emitted dimension scores.
2. **DA card D6 formatting.** The `da` card emitted `score: pass_not_applicable` for D6, then a self-correction to `not_assessed`. D6's `eligible_roles` is `[eic]`, so the DA entry was excluded as ineligible on independent grounds and the correction had no effect on the matrix. Noted because the emitted-then-corrected form may indicate a card-template ambiguity worth fixing upstream.
3. **Reference-count transcription slips.** Two inputs state 16 entries with 8 uncited while enumerating 9 names; direct count of the supplied list gives 15 entries, 6 cited, 9 uncited. Arbitrated in the letter; no decision turns on it.
4. **Cross-model check not available.** `ARS_CROSS_MODEL` unset and no consent gate passed, so the Step 4b blind decision check was not run and the decision was not compared against an external model. Stated for transparency; no behavioural change.
5. **Provenance stamp absent in a `reviewer_full` invocation.** Recorded in Part 1 rather than inferred. No panel-level model-independence claim is made or implied.
