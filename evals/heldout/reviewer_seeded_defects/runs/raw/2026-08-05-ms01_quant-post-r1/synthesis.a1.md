# Editorial Decision Package

**Contract**: `reviewer/reviewer_full/v2` · mode `reviewer_full` · stage `reviewer_full_review` · baseline `v3.20.0` · `panel_size: 5`
**Manuscript**: *Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment*

---

## Part 0: Sprint Contract Audit (v3.6.2 arithmetic mode)

### Step 1 — Role-scoped scoring matrix

Only cards whose `contract_role` appears in a dimension's `eligible_roles` contribute. `not_assessed` from ineligible seats is excluded from numerator and denominator. Every dimension had ≥1 assessed eligible seat, so no `[DIMENSION-UNASSESSED]` marker applies.

| Dim | Priority | Eligible roles | Assessed eligible seats | Seat scores | Dimension verdict |
|---|---|---|---|---|---|
| D1 methodology_rigor | mandatory | methodology | methodology | `block` (`block_class: fatal`) | `block(fatal)` |
| D2 domain_accuracy | mandatory | domain | domain | `block` (repairable) | `block` |
| D3 argumentative_coherence | mandatory | da, methodology | da, methodology | `block` (repairable), `block` (repairable) | `block` |
| D4 cross_disciplinary_relevance | high | perspective | perspective | `block` | `block` |
| D5 writing_and_structure | normal | eic | eic | `block` | `block` |
| D6 venue_fit_and_contribution | mandatory | eic | eic | `block` (repairable) | `block` |

Audit verdict = worst assessed eligible score = **`block(fatal)`** (fatality declared by the methodology seat on D1, a mandatory dimension it exclusively owns — fatal scope is therefore valid).

### Step 2 — Failure-condition evaluation

| ID | Severity | Cross-reviewer quantifier | Expression | Per-dimension evaluation | Fired |
|---|---|---|---|---|---|
| F1 | 95 | any | any mandatory dimension has a fatal block | D1 fatal (sole eligible seat = owner, `any` satisfied) | **true** |
| F2 | 90 | any | any mandatory dimension scores 'block' | D1, D2, D3, D6 all `block` | **true** |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1 (n=1, owner) ✓; D2 (n=1) ✓; D3 (n=2, both seats) ✓; D6 (n=1) ✓ → 4 ≥ 2 | **true** |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4 = `block` | **true** |
| F5 | 40 | any | any dimension scores 'warn' or worse | all six dimensions | **true** |
| F0 | 10 | all | every dimension scores 'pass' | no dimension scores `pass` | false |

### Step 3 — Precedence, decision, audit emission

Highest-severity fired condition: **F1 (severity 95)** → `action: editorial_decision=reject`.

```
dimension_verdicts: [D1=block(fatal), D2=block, D3=block, D4=block, D5=block, D6=block]
fired_conditions: [F1, F2, F3, F4, F5]
da_critical_adjudications: [C1=VALIDATED, C2=VALIDATED, C3=VALIDATED, C4=VALIDATED, C5=VALIDATED, C6=VALIDATED]
editorial_decision=reject
```

No `C<n>=REJECTED` entries, so no rejection-rationale lines are required. The mechanical decision is not `accept`, so no `[DA-CRITICAL-VS-ACCEPT]` marker applies.

### Cross-model blind decision check

`ARS_CROSS_MODEL` is not set and no consent gate has been passed. Not invoked; no behavioural change.

### Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — the dispatching layer supplied no provenance stamp with this invocation. This letter therefore makes **no** claim about which model family executed which reviewer seat, and no cross-family model independence may be assumed for any of the five cards. Recorded as a fallback, not inferred.

### Card-hygiene notes (flagged, not repaired — Phase Boundary)

- The `da` card opens with a stray meta-line (`Wait: per protocol, no dissent section is emitted`) before its `contract_role`. Cosmetic; the card is structurally complete and was scored as submitted.
- The `domain` card's strength entries (S1–S3) carry Evidence Anchors but no per-finding Confidence. No weighting depended on them.
- No card carries an overall Accept/Revise/Reject recommendation field. This is expected in sprint-contract format (the decision is derived from `failure_conditions[]`, not from seat recommendations) and is not a gap.
- `domain` W9 registers a **contingent escalation**: its `repairable` block_class on D2 is conditional on the fifteen `10.5555`-prefix DOIs resolving to real records. That contingency does not alter the emitted decision (F1 already governs) but is logged below as an editor-side verification action.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript titled *"Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment."* Your manuscript was assessed by five independent reviewers: a Journal-Fit Reviewer, a methodology reviewer, a domain reviewer, a cross-disciplinary/governance reviewer, and a Devil's Advocate.

### Decision: Reject

The decision follows the contract arithmetic recorded in Part 0: the methodology reviewer — the sole seat eligible for the mandatory methodology-rigor dimension — recorded a fatal block on that dimension, which fires F1 (severity 95). I state plainly what that does and does not mean. It means the manuscript **as submitted** cannot be evaluated as a report of a completed analysis, because five independent internal consistency checks fail in five different ways and no data, code, or reconciliation is available to determine which numbers describe the analysis that was actually run. It does not mean the underlying study is worthless. Four of the five seats characterised their own blocks as **repairable**, and the Devil's Advocate explicitly withheld fatality on the grounds that the logs are timestamped and the analysis could be re-derived. I have not softened F1's action on that basis, and I will not: the fatality declaration was made by the dimension's owner and no eligible seat disputed it. But the roadmap below is written as a reconstruction path, not as a dismissal.

### Consensus Analysis

Consensus is computed per sub-claim over the **four non-DA reviewers** (Journal-Fit / R1 methodology / R2 domain / R3 perspective). `not-mentioned` is silence, not agreement and not opposition. The Devil's Advocate is tracked separately.

#### Step 1a — Reviewer summary matrix

| Dimension | Journal-Fit (eic) | R1 (methodology) | R2 (domain) | R3 (perspective) | DA |
|---|---|---|---|---|---|
| Dimensions assessed | D5, D6 | D1, D3 | D2 | D4 | D3 |
| Worst score | block | block | block | block | block |
| Fatality | withheld (explicit) | **declared (D1)** | withheld (contingent) | not declared | withheld (explicit) |
| Strengths logged | 3 | 4 | 3 | 3 | — |
| Weaknesses logged | 11 | 17 (+10 arithmetic receipts) | 10 | 9 | 6 CRITICAL / 8 MAJOR |
| Key weaknesses | → Step 1b | → Step 1b | → Step 1b | → Step 1b | → adjudication table |

#### Step 1b — Weakness sub-claim inventory

Compacted to one row per sub-claim with each reviewer's position encoded in the `positions` column (information-preserving compression of the `(sub_claim, reviewer)` grid). Positions: `R`=raised, `C`=corroborated, `–`=not-mentioned, `D`=disputed. Order: **eic / R1 / R2 / R3 / DA**.

| ID | Parent weakness | Positions | Evidence pointer | Severity (transported) | Conf. | Disposition |
|---|---|---|---|---|---|---|
| SC-1 | Headline *r* differs between Abstract and Results | R/C/C/C/C | `text: Abstract "r = .42"` vs `§4.2 "r = .24, p = .004"` | Critical (eic W1) / Major (R1 W7, R2 W7, R3 W4) | 5,5,5,4 | **[CONSENSUS-4]** |
| SC-2 | `t(156)` implies 158 cases; no described sample supports it | R/R/C/C/C | `text: §4.3 "t(156) = 3.02"` vs `§4.1 "87 survey respondents"` (R1 AR7) | Critical (R1 W2) / Major (eic W4) | 5,4 | **[CONSENSUS-4]** |
| SC-3 | Table 2 ns (66+61=127) contradict stated 142 and df=140 | R/R/C/C/C | `table: Table 2 n column` vs `§4.3 "All 142 students"` (R1 AR9) | Major (eic W6, R1 W3) | 5,5 | **[CONSENSUS-4]** |
| SC-4a | `t(140)=1.31, p=.008` arithmetically impossible | R/R/C/C/C | `text: §4.3` (R1 AR10; two-tailed p ≈ .192) | Major (eic W7, R1 W4) | 4,5 | **[CONSENSUS-4]** |
| SC-4b | Prose calls a printed-significant result non-significant | C/R/–/C/C | `text: §4.3 "did not reach a comparable level"` vs `p=.008` at α=.05 | Major (R1 W15) | 5 | corroborated (2/4) |
| SC-5 | Perceived-control mean 3.847 unattainable from 87 integers | –/R/–/C/C | `text: §4.1` (R1 AR1; nearest 3.83908 / 3.85057) | Major (R1 W5) | 5 | corroborated (2/4) |
| SC-6 | Secondary item SD=0.10 unattainable (N=10, M=3.00, integers) | R/R/C/C/C | `text: §4.1` (R1 AR3; attainable 0.000 / 0.471) | Major (R1 W6) / Minor (eic W11) | 5,4 | **[CONSENSUS-4]** |
| SC-7a | §3.2 states two mutually exclusive sampling mechanisms | R/C/–/–/C | `text: §3.2 "a random sample"` vs `"Students who chose to respond"` | Major (eic W8, R1 W8) | 5,5 | corroborated (2/4) |
| SC-7b | No enrolment denominator, response rate, or non-respondent comparison | C/R/–/C/C | `text: §3.2 "several hundred students"` | Major (R1 W8) | 5 | **[CONSENSUS-3]** (silent: R2) |
| SC-8 | Four analytic samples (142/127/87/10), no missing-data accounting | –/R/–/–/– | `absence: §3.2–§4.3` (R1 W9) | Major (R1 W9) | 5 | single-reviewer (1/4) |
| SC-9 | Outcome mechanically truncates exposure; association artifactual | –/R/–/C/C | `text: §3.3 "sessions … during the term"` (R1 W1; DA C3) | Critical (R1 W1) | 5 | corroborated (2/4) |
| SC-10 | §5 asserts causation ("improved", "raises the probability") | R/C/C/C/C | `text: §5` vs `§3.1 "observational, cross-sectional"` | Critical (eic W2) / Major (R1 W13, R3 W7) | 5,5,5 | **[CONSENSUS-4]** |
| SC-11 | §6 asserts worldwide, cross-disciplinary "dependable strategy" | R/C/C/R/C | `text: §6` vs `§5.1 "a single introductory statistics course"` | Critical (eic W2, R3 W3) / Major (R1 W14, R2 W8) | 5,5,5,4 | **[CONSENSUS-4]** |
| SC-12 | No stated increment over the cited prior work | R/–/–/–/– | `absence: §1, §5` (eic W9) | Major (eic W9) | 4 | single-reviewer (1/4) |
| SC-13 | Log data analysed without informing students; consent covered survey only | R/C/–/R/C | `text: §3.2 "Students were not informed…"` | Critical (eic W3, R3 W1) / Major (R1 W16) | 4,5,4 | **[CONSENSUS-3]** (silent: R2) |
| SC-14 | No ethics/IRB approval statement anywhere | R/C/–/R/C | `absence: manuscript-wide ethics reporting` (eic W5, R3 W2) | Major (eic W5, R3 W2) | 5,5 | **[CONSENSUS-3]** (silent: R2) |
| SC-15 | No data-availability, funding, or COI declarations | R/C/–/–/– | `absence: front/back matter` (eic W5) | Major (eic W5) / Minor (R1 W17) | 5,5 | corroborated (2/4) |
| SC-16 | No effect sizes, CIs, or covariate adjustment | –/R/–/C/C | `absence: §3.4, §4.2–§4.3` (R1 W10) | Major (R1 W10) | 5 | corroborated (2/4) |
| SC-17 | Median split of a skewed predictor; tie rule and group sizes unexplained | –/R/–/–/– | `text: §3.3 "split at the median"` (R1 W11) | Major (R1 W11) | 5 | single-reviewer (1/4) |
| SC-18 | "Retention" names institutional persistence, measures course completion | –/–/R/D(severity)/– | `text: §6` + `Abstract`; `§3.3` | Critical (R2 W2) vs Minor (R3 W8) | 5,4 | **[SPLIT]** — see below |
| SC-19 | Missed final coded as "not retained", conflated with withdrawal | –/C/R/C/– | `text: §3.3 coding rule` (R2 W3, R1 W12) | Major (R2 W3, R1 W12) | 5,5 | **[CONSENSUS-3]** (silent: eic) |
| SC-20 | Ferro & Nakamura (2021) attribution inverted; §5 builds on it | –/–/R/C/C | `text: §2` vs `References "When dashboards demotivate…"` | Critical (R2 W1) / Major (R3 W6) | 5,4 | corroborated (2/4) |
| SC-21 | Nine of fifteen reference entries never cited in body | –/–/R/–/– | `absence: reference list vs body text` (R2 W4) | Major (R2 W4) | 5 | single-reviewer (1/4) |
| SC-22 | Persistence / gateway-course / early-alert literature never engaged | –/–/R/–/– | `absence: §1, §2` (R2 W5) | Major (R2 W5) | 5 | single-reviewer (1/4) |
| SC-23 | SRL framing invoked but unmeasured; Abstract claims SRL behaviour measured | C/–/R/–/C | `text: §5` + `§3.3`; `absence: §3.3 Measures` (DA M7) | Major (R2 W6) | 4 | corroborated (2/4) |
| SC-24 | Mediation asserted with no mediation model | C/–/C/–/C | `text: §5 "perceived control as a mediating construct"` (DA M5) | Major (R2 W6 branch) | 4 | corroborated (2/4) |
| SC-25 | Peer-comparison harm mechanism; no subgroup analysis; design cannot detect it | –/–/–/R/– | `absence: §4 Results` (R3 W5) | Major (R3 W5) | 5 | single-reviewer (1/4) |
| SC-26 | All fifteen DOIs share the `10.5555` placeholder prefix | –/–/R/–/– | `text: References` (R2 W9) | Major (R2 W9) | 3 | single-reviewer (1/4) |
| SC-27 | Table 1 reports a measure §3.3 never defines | R/–/–/–/C | `table: Table 1 "Final exam score"` (eic W10) | Minor (eic W10) | 5 | single-reviewer (1/4) |
| SC-28 | Uncited claim that single-item ratings are standard practice | –/–/R/–/– | `text: §3.3` (R2 W10) | Minor (R2 W10) | 4 | single-reviewer (1/4) |
| SC-29 | No named software, no data or code, no analysis plan | C/R/–/–/– | `absence: §3.4, end matter` (R1 W17) | Minor (R1 W17) | 5 | corroborated (2/4) |
| SC-30 | Dashboard/LMS never named; no interface figure | –/–/–/R/– | `absence: §3.1` (R3 W9) | Minor (R3 W9) | 4 | single-reviewer (1/4) |
| SC-31 | §5.1 omits confounding, reverse causation, mid-term selection | C/C/–/C/R(DA M4) | `absence: §5.1 Limitations` | Major (R1 W1/W10 branch) | 5 | **[CONSENSUS-3]** (silent: R2) |

#### Step 1c — Surface-form parity check

Applied before any weighting decision. No sub-claim's weight was reduced on grounds of informal or vague phrasing, and no sub-claim gained weight from technical specificity alone. The opposite-style counterfactual was run on the two rows where phrasing could plausibly have driven weight: SC-25 (a governance-register argument that could read as an objection rather than a finding) and SC-26 (a pattern-level inference at confidence 3). SC-25 is anchored to a specific absence in §4 against a specific mechanism documented in §2 and retains full weight on that substance. SC-26 retains its stated confidence of 3 because the reviewer's own uncertainty — not its wording — bounds it; it is routed to editor verification rather than down-ranked. Reviewer authorship was not a weighting input.

#### Points of agreement (Consensus)

- **[CONSENSUS-4] SC-1** — The paper's central quantitative claim is reported at two irreconcilable magnitudes (`r = .42` in the Abstract, `r = .24` in §4.2). No exhibit supports either.
- **[CONSENSUS-4] SC-2** — The perceived-control t-test's 156 degrees of freedom require 158 cases, exceeding both the 87 item respondents and the 142-student primary sample. One of the Abstract's two pillar claims currently has no checkable support.
- **[CONSENSUS-4] SC-3** — Table 2's group sizes total 127 against a stated classification of all 142 students and a reported df of 140. Fifteen cases are unaccounted for.
- **[CONSENSUS-4] SC-4a** — `t(140) = 1.31` cannot yield `p = .008` under either tail convention (two-tailed p ≈ .192).
- **[CONSENSUS-4] SC-6** — Ten integer responses on a 1–5 scale with a mean of exactly 3.00 admit sample SDs of 0.000, 0.471, 0.667 and upward; 0.10 is unattainable.
- **[CONSENSUS-4] SC-10** — §5's "dashboard engagement improved course retention" and "increasing dashboard engagement therefore raises the probability" are causal assertions from a design §3.1 declares observational and cross-sectional. §2 cites Ibarra (2023) against exactly this practice.
- **[CONSENSUS-4] SC-11** — §6's "dependable strategy… across programs and disciplines" for institutions "worldwide" contradicts §5.1's own single-course, single-design concession one section earlier.
- **[CONSENSUS-3] SC-13** (silent: R2 domain) — §3.2 states that students were not informed their dashboard activity data would be analysed, while consent covered the survey only. The log data carry the paper's primary finding.
- **[CONSENSUS-3] SC-14** (silent: R2 domain) — No ethics or IRB approval statement appears anywhere in the manuscript. This is independent of SC-13: a properly approved study would still fail this reporting requirement.
- **[CONSENSUS-3] SC-7b** (silent: R2 domain) — The enrolment denominator is given only as "several hundred", so no response rate is computable and no respondent/non-respondent comparison is possible.
- **[CONSENSUS-3] SC-19** (silent: Journal-Fit) — Coding "enrolled but did not sit the final" as *not retained* places still-enrolled students in the same category as withdrawals.
- **[CONSENSUS-3] SC-31** (silent: R2 domain) — §5.1's three limitations omit the rival explanations that would dissolve the finding: confounding by prior attainment, reverse causation, and selection on mid-term persistence.

Corroborated (2/4) findings carried into the roadmap without a consensus label: SC-4b, SC-5, SC-7a, SC-9, SC-15, SC-16, SC-20, SC-23, SC-24, SC-29.

Single-reviewer findings, weighted by confidence and seat expertise: SC-8, SC-12, SC-17, SC-21, SC-22, SC-25, SC-26, SC-27, SC-28, SC-30.

#### Points of disagreement

- **SC-18 — severity of the retention-construct substitution.** R2 (domain) bands this Critical: the title, Abstract, and Conclusion use the persistence tradition's vocabulary for an outcome defined as sitting one final in one course, and the distinction is never drawn, including in §5.1 where it would belong. R3 (perspective) bands the same defect Minor, scoped narrowly to how institutional readers will import their own meaning.
  - **Editor's resolution**: **Critical**, with R3's remedy adopted intact. Expertise-first (arbitration principle 2): construct definition in the persistence tradition is R2's primary area of empirical work and D2 is R2's owned dimension; R3's Minor band is calibrated to the export surface rather than to the construct. This is a severity split only — both reviewers propose the same repair (relabel consistently as course completion; confine the Conclusion to that outcome), so no direction conflict needed arbitration.

- **Repairability of the manuscript's defects.** R1 (methodology) declares D1 fatal: five independent checks failing in five ways means the reader cannot determine which analysis ran on which cases, and with no data, code, software identification, or subsample reconciliation on offer, the condition is not curable by rewriting. The Journal-Fit Reviewer, R2, R3, and the DA all characterise their own blocks as repairable.
  - **Editor's resolution**: **No conflict on the merits, and the fatality stands.** The four repairability judgements are scoped to different dimensions (D6, D2, D4, D3) than R1's fatality (D1); no seat eligible for D1 disputed it. The DA's explicit withholding of fatality reasons about the *argument chain* under D3, not about the arithmetic under D1, and is compatible with R1's position. F1 therefore fires as written and is not softened. The practical reading: reject as submitted, with a reconstruction path that is genuinely available if — and only if — the source data can be produced.

- **Contingency on the reference apparatus (SC-26).** R2 conditions its `repairable` block_class on D2 upon the fifteen `10.5555`-prefix DOIs resolving to real records, at confidence 3, and states that if verification fails, the literature framing has no evidentiary basis. Recorded as an **unresolved contingency**, not arbitrated: it cannot be resolved from the manuscript, and it does not alter the emitted decision. Editor-side verification is logged as S11.

#### Devil's Advocate CRITICAL adjudication

Every DA CRITICAL ID appears exactly once. Adjudication is visibility and arbitration, not veto.

| ID | DA's argument | Corroborated by | Journal-Fit assessment | Verdict |
|---|---|---|---|---|
| C1 | Headline association reported at two irreconcilable magnitudes | eic W1, R1 W7, R2 W7, R3 W4 (all four non-DA seats) | Directly checkable from the printed text; no inference required | **VALIDATED** |
| C2 | Central finding stated causally from an observational cross-sectional design | eic W2, R1 W13, R2 (routed), R3 W7 | Claim-to-design comparison; §2's own Ibarra citation supplies the standard violated | **VALIDATED** |
| C3 | Predictor and outcome mechanically entangled; mid-term recruitment excludes early withdrawers | R1 W1 (independently, conf 5), R3 (survivorship branch) | Independently derived by the D1 owner, who teaches this failure mode; unaddressed anywhere in §5.1 | **VALIDATED** |
| C4 | `t(156)` exceeds every described sample; second pillar claim unsupported | eic W4, R1 W2 + receipt AR7, R2 (routed), R3 (routed) | Arithmetic receipt AR7 confirms df = 156 ⇒ N = 158 > 142 > 87 | **VALIDATED** |
| C5 | §6 asserts a worldwide policy recommendation contradicting §5.1's scope concession | eic W2, R1 W14, R2 W8, R3 W3 | Manuscript asserts a scope restriction and its negation as jointly true | **VALIDATED** |
| C6 | Log data analysed without notice; no ethics statement; precludes publication | eic W3, R1 W16, R3 W1/W2 | Stated in the manuscript's own Methods; not curable retrospectively by adding a sentence | **VALIDATED** |

The DA's eight MAJOR items were folded into the sub-claim inventory (M1→SC-4a/4b, M2→SC-3, M3→SC-7a/7b, M4→SC-31, M5→SC-24, M6→SC-20, M7→SC-23, M8→SC-6/SC-5) and require no separate adjudication line.

### Decision Rationale

The manuscript's distinguishing feature is a gap between surface quality and substrate quality, and the panel converged on it from five independent routes. The prose is competent, the structure conventional, and §2's measurement critique is self-implicating in a way the panel credited unanimously — all five seats logged the same strengths. That polish is exactly what makes the substrate failures consequential rather than cosmetic.

Three defects drive the decision. First, reporting integrity: five internal consistency checks fail in five different ways (Abstract *r* vs Results *r*; df = 156 against a maximum of 140; Table 2 totalling 127 against 142; `p = .008` from `t = 1.31`; an unattainable SD on the secondary item), and the manuscript offers no data, no code, no named software, and no reconciliation of its four shifting subsamples. Any one is a transcription slip; five is a different finding — the reader cannot determine what analysis was run on whom. That is the condition F1 names.

Second, the design cannot support the headline claim in any version. Sessions accumulate across the full term while non-retained students exited early, so the outcome constitutes part of the exposure and a positive association is guaranteed by the measurement window alone. Recruitment by mid-term volunteer response compounds it, removing early withdrawers — the population §2's own cited literature predicts the peer-comparison band harms — from the frame entirely.

Third, the manuscript violates its own stated epistemic commitment. §1 promises to distinguish pattern from cause and §2 recruits a published audit of causal overclaiming; §5 then asserts that engagement "improved" retention and §6 sells a "dependable strategy" to institutions "worldwide". Publishing this would lend the venue's imprimatur to precisely the inference its critical literature exists to resist.

Separately and independently: §3.2 records that students were not informed their activity data would be analysed, and no ethics approval appears anywhere. That defect is not repairable by rewording, and the panel did not resolve whether an approval or waiver exists — only that none is on record.

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| 1 | Five independent internal impossibilities in Section 4; no artefact exists from which the reader can determine which analysis ran on which cases (the fatal D1 driver) | R1 (owner, fatal), eic, R2, R3, DA C1/C4 | `text: §4.3 "t(156) = 3.02, p = .003"` against `§4.1 "the 87 survey respondents who answered the item"` (R1 receipt AR7) | R1, R2, R3, R4, R5, R6 |
| 2 | Behavioural log data — the source of the primary finding — analysed without notice to the students it describes, with no ethics approval on record | eic W3, R1 W16, R3 W1/W2, DA C6 | `text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study."` | R10 |
| 3 | The outcome mechanically truncates the exposure, so the reported association is what the measurement window alone produces | R1 W1, R3, DA C3 | `text: §3.3 "the number of distinct sessions in which a student opened the dashboard view during the term"` | R7 |

---

## Part 2: Revision Roadmap

Because the decision is Reject, this roadmap defines what a defensible version of this study would require. It is not a conditional-acceptance checklist; it is the reconstruction path, offered because the panel judged four of five blocks repairable and because the underlying data may support a narrower, honest paper. Items are keyed to Step 1b `sub_claim_id`s.

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. Items with no sub-claim id use `—`.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| R1 | Determine which correlation is correct, correct the other, and recalibrate every magnitude-dependent statement to the surviving value | SC-1 | Critical (eic W1) / Major (R1 W7, R2 W7, R3 W4) | `text: Abstract "r = .42"` vs `§4.2 "r = .24, p = .004"` | 5 (eic), 5 (R1), 5 (R2), 4 (R3) | eic, R1, R2, R3 | P1 | 1 day (given data) |
| R2 | Re-run and re-report the perceived-control comparison on its actual respondents, with group ns, and correct the descriptive mean | SC-2, SC-5 | Critical (R1 W2) / Major (eic W4, R1 W5) | `text: §4.3 "t(156) = 3.02"` vs `§4.1 "87 survey respondents"` (AR7, AR1) | 5 (R1), 4 (eic) | R1, eic, DA C4 | P1 | 2–3 days |
| R3 | Reconcile Table 2's group sizes with the classification statement and the reported df; account for the 15 missing cases | SC-3 | Major (eic W6, R1 W3) | `table: Table 2 n column (66 + 61 = 127)` vs `§4.3 "All 142 students"` (AR9) | 5 (eic), 5 (R1) | eic, R1, DA M2 | P1 | 1–2 days |
| R4 | Re-report the exam comparison's p-value from the actual test, and rewrite the surrounding narrative to match whichever value survives | SC-4a, SC-4b | Major (eic W7, R1 W4, R1 W15) | `text: §4.3 "the difference was small, t(140) = 1.31, p = .008"` (AR10) | 4 (eic), 5 (R1) | eic, R1, DA M1 | P1 | 1 day |
| R5 | Correct or withdraw the ten-student secondary item; state its analytic purpose or remove it | SC-6 | Major (R1 W6) / Minor (eic W11) | `text: §4.1 "N=10; M=3.00; sample SD=0.10; integer scale=1-5"` (AR3) | 5 (R1), 4 (eic) | R1, eic, R2, R3, DA M8 | P1 | 0.5 day |
| R6 | Supply a complete sample-accounting table (142 / 127 / 87 / 10), the missing-data mechanism, the enrolment denominator, the response rate, and a respondent vs non-respondent comparison | SC-8, SC-7b | Major (R1 W9, R1 W8) | `absence: §3.2–§4.3 — reconciliation of the four analytic subsamples` | 5 (R1) | R1 (owner), eic, R3, DA M3 | P1 | 3–5 days |
| R7 | Re-measure exposure over a fixed window that closes before any withdrawal can occur; adjust for prior attainment and baseline LMS activity; report effect sizes with confidence intervals; address reverse causation and mid-term selection explicitly in Limitations | SC-9, SC-16, SC-31 | Critical (R1 W1) / Major (R1 W10) | `text: §3.3 "the number of distinct sessions … during the term"` | 5 (R1), 5 (R3) | R1 (owner), R3, DA C3/M4 | P1 | 3–4 weeks (new analysis) |
| R8 | Withdraw every causal and interventional formulation from §5 and §6; restate the finding as an association and keep §1's stated commitment through to the Conclusion | SC-10 | Critical (eic W2) / Major (R1 W13, R3 W7) | `text: §5 "dashboard engagement improved course retention"` vs `§3.1 "observational, cross-sectional"` | 5 (eic), 5 (R1), 5 (R3) | eic, R1, R2, R3, DA C2 | P1 | 2–3 days |
| R9 | Remove the worldwide, cross-disciplinary, and "dependable" claims; confine all implications to one course section in one term at one institution with one dashboard design | SC-11 | Critical (eic W2, R3 W3) / Major (R1 W14, R2 W8) | `text: §6 "a dependable strategy for improving retention across programs and disciplines"` | 5 (eic), 5 (R3), 5 (R1), 4 (R2) | eic, R1, R2, R3, DA C5 | P1 | 2 days |
| R10 | Produce the ethics-review determination, protocol identifier, and the consent or waiver basis specifically covering the behavioural-log component; if none exists, the log analysis cannot be published as conducted | SC-13, SC-14 | Critical (eic W3, R3 W1) / Major (R1 W16, R3 W2) | `text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study."` | 4 (eic), 5 (R3), 4 (R1) | eic, R1, R3, DA C6 | P1 | Not author-schedulable (institutional review) |
| R11 | Correct the Ferro & Nakamura (2021) characterisation to what that source argues, and rebuild the equity rationale and §5's alignment claim on the corrected reading | SC-20 | Critical (R2 W1) / Major (R3 W6) | `text: §2 "Dashboards have been shown to reliably improve outcomes for lower-achieving students"` vs `References "When dashboards demotivate…"` | 5 (R2), 4 (R3) | R2 (owner), R3, DA M6 | P1 | 3–5 days |
| R12 | Relabel the outcome as course completion throughout; report withdrawal and enrolled-non-attendance as separate codes and re-estimate on the corrected variable | SC-18, SC-19 | Critical (R2 W2, arbitrated) / Major (R2 W3, R1 W12) / Minor (R3 W8) | `text: §3.3 coding rule`; `§6 "retention across programs and disciplines"` | 5 (R2), 5 (R1), 4 (R3) | R2 (owner), R1, R3 | P1 | 1 week |
| R13 | Resolve the sampling account: state one mechanism, and state it as the volunteer-response procedure the section actually describes | SC-7a | Major (eic W8, R1 W8) | `text: §3.2 "a random sample"` vs `"Students who chose to respond"` | 5 (eic), 5 (R1) | eic, R1, DA M3 | P1 | 0.5 day |
| R14 | Either measure self-regulated learning with phase-appropriate instruments or withdraw the SRL and mediation claims, including the Abstract's statement that SRL behaviour was measured | SC-23, SC-24 | Major (R2 W6) | `text: §5 "consistent with a self-regulated learning account…"`; `absence: §3.3 Measures — an SRL instrument` | 4 (R2), 4 (eic) | R2, eic, DA M5/M7 | P1 | 1 week (withdraw) / new collection (measure) |

### Required Item Details

**R1** — Abstract and §4.2 report `r = .42` and `r = .24` for the same quantity; the Abstract's value overstates shared variance roughly threefold and is the number that circulates. §5's "modest size" hedge is calibrated to .24.
- **Acceptance criteria**: One correlation value appears throughout the manuscript, is supported by a reported analysis with its N and test, and every magnitude-dependent characterisation in the Abstract, §5, and §6 is consistent with it.

**R2** — `t(156)` requires 158 cases under any two-group identity; the item's respondents number 87 (df ≤ 85) and the primary sample 142 (df ≤ 140). The reported mean of 3.847 is also unattainable from 87 integer responses (adjacent attainable values 3.83908 and 3.85057).
- **Acceptance criteria**: The perceived-control comparison is reported with group ns that sum to the stated respondent count, df consistent with those ns, and a descriptive mean attainable from that N at the stated integer scale.

**R3** — §4.3 states all 142 students were classified and reports df = 140; Table 2 reports 66 + 61 = 127. R1's pooled recomputation from Table 2's own means and SDs returns t ≈ 1.31 on 125 df, which is flagged as an unreceipted hand calculation requiring author verification against source data.
- **Acceptance criteria**: Table 2's group ns, the text's classification statement, and the reported df all describe the same set of cases, with any excluded cases enumerated and their exclusion reason stated.

**R4** — `t = 1.31` on 140 df gives two-tailed p ≈ .192 and one-tailed p ≈ .096; the printed .008 is unreachable under either convention and would be significant at the stated α = .05, contradicting the sentence containing it and §5's "weaker still" reading.
- **Acceptance criteria**: The reported p follows from the reported t and df under a stated tail convention, and the narrative characterisation in §4.3 and §5 matches that value against the stated alpha.

**R5** — Ten integer responses on a 1–5 scale with a mean of exactly 3.00 admit sample SDs of 0.000, 0.471, 0.667 and upward. No claim in the paper rests on this item, which is why the panel's transported severity ranges from Minor to Major; its impossibility is nonetheless direct evidence that a reported summary does not come from the data as described.
- **Acceptance criteria**: The secondary item is either removed or reported with a dispersion attainable from ten integer responses at the stated mean, together with a stated analytic purpose.

**R6** — Four analytic samples appear (142, 127, 87, 10) with no statement of how each was formed. Item skippers are described as excluded, which is unstated listwise deletion. With retention as the outcome and volunteer recruitment as the mechanism, missingness is plausibly related to both exposure and outcome.
- **Acceptance criteria**: A sample-accounting table traces every reported N from the enrolment denominator forward, states the missing-data mechanism assumed, and reports a respondent vs non-respondent comparison on available covariates.

**R7** — Sessions accumulate over 15 weeks while non-retained students exited early, so the outcome partly constitutes the exposure and a positive association is expected from the measurement window alone. §5.1's three limitations omit confounding by prior attainment, reverse causation, and selection on mid-term persistence.
- **Acceptance criteria**: Exposure is measured over a window closing before any outcome event, the association is re-estimated with adjustment for prior attainment and baseline LMS activity, effect sizes with confidence intervals accompany every comparison, and Limitations addresses reverse causation and mid-term selection by name.

**R8** — §1 promises to distinguish pattern from cause and §2 recruits Ibarra (2023) against causal overclaiming; §5 then asserts that engagement "improved" retention and "raises the probability" of completion.
- **Acceptance criteria**: No sentence in §5 or §6 asserts that dashboard engagement improves, raises, or causes retention, and the Discussion's framing is consistent with the design stated in §3.1.

**R9** — §5.1 concedes the single-course, single-design constraint; §6 then addresses institutions "worldwide" with a "dependable strategy… across programs and disciplines". Every generalisation dimension is held at n = 1, with no comparison condition, fidelity measure, or cost data.
- **Acceptance criteria**: The Conclusion's scope does not exceed the sampled setting, and no reliability or transferability claim is made without variance across contexts to support it.

**R10** — Consent covered a survey about study habits; the analysis joins individually identifiable session logs to enrolment, withdrawal, and exam outcomes for the same students. No approval statement, protocol identifier, or waiver appears anywhere. The panel records that it cannot determine from the manuscript whether an approval exists.
- **Acceptance criteria**: The manuscript states the reviewing body, determination, date or protocol number, and the specific consent or waiver basis covering the behavioural-log component, or the log analysis is withdrawn.

**R11** — §2 attributes "reliably improve outcomes for lower-achieving students" to a source titled *When dashboards demotivate: Peer comparison and the lower-achieving student*, declares the sentence load-bearing for the equity rationale, and §5 cashes it out. R2 verified the other five in-text attributions as sound, which is why this is judged discrete rather than systematic.
- **Acceptance criteria**: The §2 characterisation matches what Ferro & Nakamura (2021) argues, and §5's alignment claim and the equity rationale are rewritten on the corrected reading rather than retained unchanged.

**R12** — The paper uses the persistence tradition's vocabulary for an outcome defined as sitting one final in one course, and merges formal withdrawal with enrolled non-attendance into one code. Arbitrated to Critical on expertise grounds; R2 and R3 propose the same remedy.
- **Acceptance criteria**: The outcome is named course completion wherever it is reported, withdrawal and enrolled non-attendance are reported as distinct codes, and no claim about institutional persistence is made anywhere in the manuscript.

**R13** — §3.2's first sentence claims a random sample of enrolled students; three sentences later it describes an LMS announcement with voluntary response and non-respondents excluded. Only the second is compatible with the described procedure.
- **Acceptance criteria**: §3.2 states a single sampling mechanism consistent with the recruitment procedure it describes, and every inferential claim is qualified to that mechanism.

**R14** — Forethought, performance, and reflection are named in §1 and §2 and measured nowhere; §5 reads a single "perceived control" item as evidence about monitoring, and the Abstract claims SRL behaviour was measured. The mediation claim rests on a two-group mean comparison with no model and no temporal ordering.
- **Acceptance criteria**: Either phase-appropriate SRL measures are reported and analysed, or the Abstract, §5's SRL account, and the mediation claim are withdrawn and the perceived-control item is described only as what it is.

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| S1 | Cite the nine unused reference entries where they bear on the argument, or remove them, and revise §2's coverage account accordingly | SC-21 | Major (R2 W4) | `absence: reference list vs body text — nine entries never cited` | 5 (R2) | R2 | P2 | 3–5 days |
| S2 | Engage the persistence, gateway-course intervention, and early-alert evaluation literatures; supply a citation for §1's elevated-risk premise | SC-22 | Major (R2 W5) | `absence: §1 and §2 — persistence and gateway-course literatures` | 5 (R2) | R2 | P2 | 1 week |
| S3 | Add a moderation or subgroup analysis by goal orientation or prior achievement, or state explicitly that the design cannot speak to differential harm and withdraw any recommendation of the peer-comparison feature | SC-25 | Major (R3 W5) | `absence: §4 Results — moderation analysis for the subgroup Osei (2020) predicts is harmed` | 5 (R3) | R3 | P2 | 1–2 weeks |
| S4 | Analyse the continuous engagement measure as primary; if the median split is retained for exposition, state the tie rule and explain the resulting group sizes | SC-17 | Major (R1 W11) | `text: §3.3 "students were split at the median number of dashboard sessions"` | 5 (R1) | R1 | P2 | 2–3 days |
| S5 | State the increment over the named prior studies explicitly, in the Introduction and again in the Discussion | SC-12 | Major (eic W9) | `absence: §1 and §5 — explicit statement of increment over named prior work` | 4 (eic) | eic | P2 | 2 days |
| S6 | Add data availability, funding, and conflict-of-interest declarations | SC-15 | Major (eic W5) / Minor (R1 W17) | `absence: manuscript front and back matter` | 5 (eic), 5 (R1) | eic, R1 | P2 | 0.5 day |
| S7 | Name the statistical software and version, identify the procedures used, and supply analysis code and a codebook | SC-29 | Minor (R1 W17) | `absence: §3.4 and end matter — named software, code, analysis plan` | 5 (R1) | R1, eic | P2 | 2–3 days |
| S8 | Define final exam score in §3.3 Measures, and distinguish it from the retention variable built on the same assessment | SC-27 | Minor (eic W10) | `table: Table 1 "Final exam score (0-100)"` with no §3.3 definition | 5 (eic) | eic | P3 | 0.5 day |
| S9 | Support or drop the claim that single-item overall ratings are common practice for this construct | SC-28 | Minor (R2 W10) | `text: §3.3 "single-item overall ratings are common in dashboard studies"` | 4 (R2) | R2 | P3 | 0.5 day |
| S10 | Name the LMS and dashboard, state the version, and include a figure or wireframe showing the peer-comparison band | SC-30 | Minor (R3 W9) | `absence: §3.1 — platform name and interface figure` | 4 (R3) | R3 | P3 | 1–2 days |
| S11 | Supply resolvable identifiers for all fifteen references (editor-side verification also logged: all share the reserved `10.5555` prefix) | SC-26 | Major (R2 W9) | `text: References "10.5555/1010203" and "10.5555/1516718"` | 3 (R2) | R2 | P2 | 1 day |

> Transported metadata appears on every row: each item carries the driving sub-claim's transported Severity, the finding's typed Evidence Anchor, and its per-finding Confidence. No `[SEVERITY-SOURCE: letter-fallback]` or `[CONFIDENCE-SOURCE: report-level]` tags were required — every current-format card supplied per-finding Severity and Confidence except the `domain` card's strength entries, which carried no findings into the roadmap.

### Revision Checklist

#### Priority 1 — Structural (estimated total: 8–10 weeks, plus institutional review time that is not author-schedulable)
- [ ] R1: Resolve the two reported correlations and recalibrate all magnitude language
- [ ] R2: Re-report the perceived-control comparison on its actual respondents
- [ ] R3: Reconcile Table 2 with the classification statement and df
- [ ] R4: Re-report the exam comparison p-value and align the narrative
- [ ] R5: Correct or withdraw the ten-student secondary item
- [ ] R6: Supply full sample accounting and missing-data treatment
- [ ] R7: Re-measure exposure in a pre-outcome window; adjust, add effect sizes and CIs, address rival explanations
- [ ] R8: Withdraw all causal formulations
- [ ] R9: Withdraw the worldwide and "dependable" generalisation
- [ ] R10: Produce the ethics determination and consent basis for the log component
- [ ] R11: Correct the Ferro & Nakamura attribution and rebuild the equity rationale
- [ ] R12: Relabel the outcome; separate withdrawal from non-attendance
- [ ] R13: State one sampling mechanism
- [ ] R14: Measure SRL or withdraw the SRL and mediation claims

#### Priority 2 — Content supplementation (estimated total: 3–4 weeks)
- [ ] S1: Repair the reference apparatus
- [ ] S2: Engage the persistence and gateway-course literatures
- [ ] S3: Subgroup/moderation analysis or explicit harm disclaimer
- [ ] S4: Continuous predictor as primary; state the tie rule
- [ ] S5: State the increment over named prior work
- [ ] S6: Add data availability, funding, and COI declarations
- [ ] S7: Name software and supply code and codebook
- [ ] S11: Supply resolvable reference identifiers

#### Priority 3 — Text and exhibits (estimated total: 2–3 days)
- [ ] S8: Define final exam score in Measures
- [ ] S9: Support or drop the single-item practice claim
- [ ] S10: Name the platform and add an interface figure

### Deadline / next step

Not a revision deadline. The decision is Reject, so resubmission would be a **new submission**, and R7, R10, R12, and R14 each require work that cannot be completed inside a revision window: a re-measured exposure variable, a retrospective institutional ethics determination, a redefined outcome, and either new instrumentation or the withdrawal of one of the paper's two headline claims.

Two paths are genuinely open. The narrower one — relabelling the outcome as course completion, reporting a corrected association from a pre-withdrawal exposure window with adjustment and intervals, withdrawing the causal and global claims, and correcting the citation record — yields a modest, honest single-site descriptive paper. R2 (domain) and the DA both judged that path available without new data collection, provided the source data and an ethics basis can be produced. The wider one requires new collection with disclosed consent, phase-appropriate SRL measurement, and a comparison condition. Neither path survives R10 failing: if no consent or waiver basis for the behavioural-log component exists, the primary dataset cannot be published as analysed, and the study would have to be rebuilt on data collected under disclosure.

For venue: on the field analysis's own reading, a rigorously re-analysed and honestly scoped single-site study fits a Q2 venue such as *Journal of Computing in Higher Education* or *Australasian Journal of Educational Technology*, not the Q1 framing this manuscript is written for.

### Response Letter Template

If you pursue resubmission, use `templates/revision_response_template.md` and respond to every R and S item above by its ID, including the ones you decline — for R1–R14 a decline requires the substantive counter-argument, not a statement of intent. For R2, R3, R4, and R5, the response must show the reconciliation arithmetic, not assert that it was performed. For R3 specifically, R1's pooled recomputation from Table 2's own means and SDs (t ≈ 1.31 on 125 df, suggesting 127 as the true analytic N) is flagged by that reviewer as an unreceipted hand calculation: verify it against source data rather than adopting it.

---

## Part 3: Reviewer Report Summary (Appendix)

### Journal-Fit Review Report Summary (eic)
- Dimensions assessed: D5 `block`, D6 `block` (repairable) | Fatality withheld explicitly on D6 | 3 strengths, 11 weaknesses
- Key point: the topic fits, but the claims do not — an *r* of .24 in one course becomes a dependable worldwide lever by §6, which is exactly the inferential slippage this venue's own published critique resists; and the reported numbers do not reconcile in ways a reader will catch even if a copy-editor does not.

### Reviewer 1 (Methodology) Summary
- Dimensions assessed: D1 `block` (**fatal**), D3 `block` (repairable) | 4 strengths, 17 weaknesses, 10 arithmetic receipts (3 mismatch, 1 consistent, 4 not-computable with stated reasons)
- Key point: not one inferential statistic in Section 4 reconciles with the sample the manuscript describes, and with no data, code, or software named, the reader cannot determine which analysis ran on which cases — while the exposure window is closed by the outcome, so the headline association is what the design produces with or without a dashboard effect.

### Reviewer 2 (Domain) Summary
- Dimensions assessed: D2 `block` (repairable, contingent on DOI verification) | 3 strengths, 10 weaknesses
- Key point: the paper measures course completion and reports institutional persistence, inverts the argument of a named source that its Discussion then builds on, and leaves nine of fifteen reference entries — including the one review directly on its own framing premise — uncited.

### Reviewer 3 (Perspective / governance) Summary
- Dimensions assessed: D4 `block` | 3 strengths, 9 weaknesses
- Key point: the log analysis sits outside any consent instrument the paper describes and no ethics approval appears anywhere; the dashboard's peer-comparison band is a harm mechanism the study's mid-term volunteer sampling makes structurally undetectable; and the worldwide deployment recommendation is unimplementable under the conditions the study itself ran.

### Devil's Advocate Summary
- Dimensions assessed: D3 `block` (repairable, fatality withheld explicitly) | 6 CRITICAL, 8 MAJOR — all 6 CRITICAL adjudicated **VALIDATED**
- Key point: granting every datum and disputing only the inferences, the chain breaks at P2→C2 and again at C2→C3, and the perceived-control pillar rests on a test that cannot have been run on any sample the paper describes; the revision is demanding but does not strictly require new data, provided the authors abandon the thesis as currently stated.
