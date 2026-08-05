# Editorial Decision Package

## Sprint Contract Audit (mechanical — v3.6.2 Synthesizer Protocol, Steps 1–3)

`contract_id: reviewer/reviewer_full/v2` · `mode: reviewer_full` · `panel_size: 5` · seats present: `eic`, `methodology`, `domain`, `perspective`, `da` (5/5 usable — no `[PANEL-SHRUNK]`).

### Step 1 — Role-scoped scoring matrix

Only seats whose `contract_role` appears in a dimension's `eligible_roles` are counted. Ineligible `not_assessed` values are excluded from numerator and denominator.

| Dim | Priority | Eligible roles | Assessed eligible seats | Scores (assessed, eligible) | Dimension verdict |
|---|---|---|---|---|---|
| D1 methodology_rigor | mandatory | methodology | 1/1 | methodology = `block`, `block_class: fatal` | **block(fatal)** |
| D2 domain_accuracy | mandatory | domain | 1/1 | domain = `block`, repairable | block |
| D3 argumentative_coherence | mandatory | da, methodology | 2/2 | da = `block` repairable; methodology = `block` repairable | block |
| D4 cross_disciplinary_relevance | high | perspective | 1/1 | perspective = `block` (no `block_class`) | block |
| D5 writing_and_structure | normal | eic | 1/1 | eic = `block` (no `block_class`) | block |
| D6 venue_fit_and_contribution | mandatory | eic | 1/1 | eic = `block`, repairable | block |

Audit verdict (worst assessed eligible score, fatal rendered): **block(fatal)** — one assessed eligible seat (methodology, owner of D1) declared a fatal block on a mandatory dimension.

**Card-hygiene flags (flagged, not fixed — Phase 1 territory):**
- `perspective` card opens with a `## Scoring Plan Dissent` heading that is then self-withdrawn in the following line. Read as **no dissent emitted**; no fatality minted from it. Card structure irregular.
- `perspective` D4 and `eic` D5 carry no `block_class`. Immaterial to the arithmetic: fatal scope is valid only for mandatory dimensions, and D4 (high) / D5 (normal) are not mandatory.
- No card emits a report-level Overall Recommendation or Confidence Score (contract cards emit dimension scores and per-finding confidence instead). Those Step 1a rows are recorded as *not stated*, not inferred.

### Step 2 — Failure-condition evaluation

| Cond | Sev | Cross-reviewer quantifier | Expression (parsed pattern) | Per-dimension booleans | Fired |
|---|---|---|---|---|---|
| F1 | 95 | any | `any <priority> dimension has a fatal block` (mandatory = D1,D2,D3,D6; fatal scope valid) | D1=T (methodology fatal), D2=F, D3=F, D4—, D5—, D6=F | **true** |
| F2 | 90 | any | `any mandatory dimension scores 'block'` | D1=T, D2=T, D3=T, D6=T | **true** |
| F3 | 70 | majority | `two or more dimensions with priority=mandatory score 'warn' or worse` (n=1 → owner seat; n=2 → both seats) | D1=T, D2=T, D3=T (both seats), D6=T → 4 ≥ 2 | **true** |
| F4 | 60 | any | `any high-priority dimension scores 'block'` (high = D4) | D4=T | **true** |
| F5 | 40 | any | `any dimension scores 'warn' or worse` | D1–D6 all T | **true** |
| F0 | 10 | all | `every dimension scores 'pass'` | no dimension = pass | false |

### Step 3 — Precedence, decision, audit emission

Highest-severity fired condition: **F1 (95)** → `action: editorial_decision=reject`. No fired condition's action is softened.

```
dimension_verdicts: [D1=block(fatal), D2=block, D3=block, D4=block, D5=block, D6=block]
fired_conditions: [F1, F2, F3, F4, F5]
da_critical_adjudications: [C1=VALIDATED, C2=VALIDATED, C3=VALIDATED, C4=VALIDATED, C5=VALIDATED, C6=VALIDATED, C7=VALIDATED]
editorial_decision=reject
```

No `[DA-CRITICAL-VS-ACCEPT]` marker: the mechanical decision is `reject`, not `accept`.

**Coverage note (observation, not an adjustment):** the panel's three Critical ethics findings (EIC W2, R3 W1, DA C7) are *not* arithmetically load-bearing under this contract — no dimension score was driven to block on ethics grounds (R3 scored D4 on generalisation and construct drift; R1 banded ethics as Major W16). They reach the decision through the DA adjudication line and as a stated precondition in the letter below. Had the arithmetic produced `accept`, the DA-CRITICAL-vs-accept escalation marker would have fired. I record this without altering any score or condition.

`ARS_CROSS_MODEL` not set and no consent gate passed → Step 4b blind decision check not run; no behavioural change.

---

## Step 1a — Reviewer Summary Matrix

| Dimension | Journal-Fit Reviewer (eic) | R1 Methodology | R2 Domain | R3 Perspective (ethics/governance) |
|---|---|---|---|---|
| Overall Recommendation | not stated (contract card) | not stated | not stated | not stated |
| Confidence Score (report level) | not stated (per-finding only) | not stated | not stated | not stated |
| Dimensions assessed | D5 block, D6 block(repairable) | D1 block(**fatal**), D3 block(repairable) | D2 block(repairable) | D4 block |
| Key Strengths | 4 (S1–S4) | 5 (S1–S5) | 3 (S1–S3) | 4 (S1–S4) |
| Key Weaknesses | 10 (W1–W10) → decomposed in Step 1b | 18 (W1–W18) → Step 1b | 12 (W1–W12) → Step 1b | 10 (W1–W10) → Step 1b |
| Findings at Critical | 2 | 4 | 1 | 1 |
| Findings at Minor | 1 | 2 | 3 | 2 |

DA card (not one of the 4 for consensus counting): 7 CRITICAL (C1–C7), 9 MAJOR (M1–M9), plus an unbanded minor list.

---

## Step 1b — Weakness Sub-Claim Inventory

Decomposition is confined to sub-claims the seats actually raised; no sub-claim below originates with me.

### Disposition (computed per sub-claim; denominator is always the 4 non-DA seats)

| SC | Sub-claim (short) | agree | conflict | silent | Disposition |
|---|---|---|---|---|---|
| SC-1 | Abstract r = .42 is not the Results r = .24 | 4 | 0 | 0 | **[CONSENSUS-4]** |
| SC-2 | t(156) df exceeds every sample the paper describes | 4 | 0 | 0 | **[CONSENSUS-4]** |
| SC-3 | Exam comparison: t/df/p mutually impossible and contradicts its own prose | 3 | 0 | 1 (R3) | [CONSENSUS-3] |
| SC-4 | Table 2 ns sum to 127 against "all 142 classified" and df = 140 | 3 | 0 | 1 (R3) | [CONSENSUS-3] |
| SC-5 | Clarity item SD = 0.10 unobtainable for 10 integer responses at M = 3.00 | 3 | 0 | 1 (R3) | [CONSENSUS-3] |
| SC-6 | M = 3.847 not attainable at n = 87; spurious 3-decimal precision | 2 | 0 | 2 | corroborated finding |
| SC-7 | No named software/version, code, or data-availability statement | 2 | 0 | 2 | corroborated finding |
| SC-8 | Exposure window truncated by the outcome → part of r is definitional | 1 | 0 | 3 | single-reviewer finding |
| SC-9 | Mid-term recruitment structurally excludes withdrawers (survivorship) | 3 | 0 | 1 (R3) | [CONSENSUS-3] |
| SC-10 | Two mutually exclusive sampling frames in one subsection | 3 | 0 | 1 (R3) | [CONSENSUS-3] |
| SC-11 | No covariate of any kind; reverse causation unaddressed | 2 | 0 | 2 | corroborated finding |
| SC-12 | Retention marginal/base rate never reported | 1 | 0 | 3 | single-reviewer finding |
| SC-13 | Dichotomous outcome as Pearson r, unnamed point-biserial, no logistic model | 1 | 0 | 3 | single-reviewer finding |
| SC-14 | Median split of a right-skewed predictor acknowledged, not remedied | 1 | 0 | 3 | single-reviewer finding |
| SC-15 | No effect sizes, confidence intervals, or power justification | 1 | 0 | 3 | single-reviewer finding |
| SC-16 | IV defined by an untested 30-minute vendor default; no sensitivity check | 1 | 0 | 3 | single-reviewer finding |
| SC-17 | Both survey constructs single-item with no reliability/validity evidence | 2 | 0 | 2 | corroborated finding |
| SC-18 | Final exam score analysed but never operationalised in Measures | 1 | 0 | 3 | single-reviewer finding |
| SC-19 | Discussion/Conclusion assert causation from a cross-sectional association | 4 | 0 | 0 | **[CONSENSUS-4]** |
| SC-20 | "Worldwide"/"dependable"/"generalizable" from one course, contradicting §5.1 | 4 | 0 | 0 | **[CONSENSUS-4]** |
| SC-21 | Limitations omits self-selection/survivorship and the correlational→causal boundary | 2 | 1 (R2) | 1 (R3) | **[SPLIT]** — arbitrated |
| SC-22 | Click-count proxy silently promoted to the SRL construct in §5 | 1 | 0 | 3 | single-reviewer finding |
| SC-23 | SRL framing decorative; Abstract claims SRL behaviour was measured | 1 | 0 | 3 | single-reviewer finding |
| SC-24 | Ferro & Nakamura credited with the reverse of the source's stated finding | 3 | 0 | 1 (R1) | [CONSENSUS-3] |
| SC-25 | No differential-effect/subgroup analysis for a peer-comparison dashboard | 2 | 0 | 2 | corroborated finding |
| SC-26 | Goal-orientation rival account raised in §2, never reconciled in §5 | 2 | 0 | 2 | corroborated finding |
| SC-27 | No systematic review/meta-analysis engaged; novelty never established | 2 | 0 | 2 | corroborated finding |
| SC-28 | Nine of the listed references are never cited in text | 2 | 0 | 2 | corroborated finding |
| SC-29 | Reference list unverifiable (uniform non-resolving `10.5555` prefix) | 1 | 0 | 3 | single-reviewer finding |
| SC-30 | Single-course completion framed and concluded as institutional retention | 2 | 0 | 2 | corroborated finding |
| SC-31 | Uncited empirical claim that single-item ratings are common practice | 1 | 0 | 3 | single-reviewer finding |
| SC-32 | Trace data analysed without informing students; consent scope exceeded | 4 | 0 | 0 | **[CONSENSUS-4]** |
| SC-33 | No ethics approval, waiver rationale, or data-protection statement anywhere | 3 | 0 | 1 (R2) | [CONSENSUS-3] |
| SC-34 | Encouraging engagement converts the observed indicator into a target | 1 | 0 | 3 | single-reviewer finding |
| SC-35 | Nothing actionable for the practitioner audience addressed (no cost/staffing/comparison) | 1 | 0 | 3 | single-reviewer finding |
| SC-36 | No response rate/enrolment denominator; 39% item non-response uncharacterised | 2 | 0 | 2 | corroborated finding |
| SC-37 | Orphan 10-student subsample and ad-hoc run-in numeric presentation | 1 | 0 | 3 | single-reviewer finding |

Totals: 5 CONSENSUS-4, 7 CONSENSUS-3, 1 SPLIT, 10 corroborated (2/4), 14 single-reviewer. `not-mentioned` is silence, never promoted to agreement — no single-reviewer sub-claim above is labelled a consensus.

### Position rows (rows where `position ≠ not-mentioned`; all omitted pairs are `not-mentioned`)

| sub_claim_id | parent_weakness | reviewer_id | position | evidence_pointer | severity (transported) | confidence |
|---|---|---|---|---|---|---|
| SC-1 | EIC-W1 abstract≠results r | EIC | raised | text: Abstract vs §4.2 | Critical | 5 |
| SC-1 | R1-W6 | R1 | corroborated | text: Abstract "r = .42" | Major | 5 |
| SC-1 | R2-W7 | R2 | corroborated | text: Abstract vs §4.2 | Major | 5 |
| SC-1 | R3-W10 | R3 | corroborated | text: Abstract vs §4.2 | Major | 4 |
| SC-2 | R1-W1 df | R1 | raised | text: §4.3 "t(156) = 3.02" | Critical | 5 |
| SC-2 | EIC-W8 | EIC | corroborated | text: §4.3 and §4.1 | Major | 4 |
| SC-2 | R2-W8 | R2 | corroborated | text: §4.3 vs §4.1 "87 respondents" | Major | 4 |
| SC-2 | R3-W9 provenance | R3 | corroborated | text: "142 students provided complete…" + "t(156)" | Minor | 3 |
| SC-3 | R1-W2 t/p | R1 | raised | text: §4.3 "t(140) = 1.31, p = .008" | Critical | 5 |
| SC-3 | EIC-W9 | EIC | corroborated | table: Table 2 + §4.3 prose | Major | 5 |
| SC-3 | R2-W9 | R2 | corroborated | table: Table 2 vs §4.3 | Major | 4 |
| SC-4 | R1-W3 sample unreconciled | R1 | raised | table: Table 2 n column | Major | 5 |
| SC-4 | EIC-W9 | EIC | corroborated | table: Table 2 n = 66 + 61 = 127 | Major | 5 |
| SC-4 | R2-W9 | R2 | corroborated | table: Table 2 vs "all 142 classified" | Major | 4 |
| SC-5 | R1-W4 SD bound | R1 | raised | text: §4.1 "N=10; M=3.00; SD=0.10" | Major | 5 |
| SC-5 | EIC-W10 | EIC | corroborated | text: §4.1 run-in values | Minor | 4 |
| SC-5 | R2-W10 | R2 | corroborated | text: §4.1 | Minor | 4 |
| SC-6 | R1-W5 mean divisibility | R1 | raised | text: §4.1 "3.847" across 87 respondents | Major | 5 |
| SC-6 | EIC-W10 precision | EIC | corroborated | text: §4.1 / Table 1 decimals | Minor | 4 |
| SC-7 | R1-W17 reproducibility | R1 | raised | absence: §3.4 and end matter | Minor | 5 |
| SC-7 | EIC D5 body | EIC | corroborated | text: "no ethics, consent, or data-availability statement" | `[SEVERITY-SOURCE: letter-fallback]` Major-band | `[CONFIDENCE-SOURCE: unavailable]` |
| SC-8 | R1-W7 exposure truncation | R1 | raised | text: §3.3 "sessions … during the term"; §3.2 mid-term announcement | Critical | 5 |
| SC-9 | R1-W7 survivorship | R1 | raised | text: §3.2 "Midway through the term…" | Critical | 5 |
| SC-9 | EIC-W4 | EIC | corroborated | text: §3.2 volunteer/exclusion sentences | Major | 5 |
| SC-9 | R2-W5 under-sampling of disengagers | R2 | corroborated | text: §2 performance-avoidance vs §5 reading | Major | 4 |
| SC-10 | EIC-W4 sampling frame | EIC | raised | text: §3.2 "random sample" vs "chose to respond" | Major | 5 |
| SC-10 | R1-W8 | R1 | corroborated | text: §3.2 "using a random sample…" | Major | 5 |
| SC-10 | R2-W6 | R2 | corroborated | text: §3.2 both sentences | Major | 5 |
| SC-11 | R1-W11 no covariates | R1 | raised | absence: §3.3–§4.2 baseline covariates | Major | 5 |
| SC-11 | EIC-W3 reverse causation | EIC | corroborated | text: §5/§6 claim layer | Major | 5 |
| SC-12 | R1-W10 base rate | R1 | raised | text: §3.4 Pearson correlations | Major | 5 |
| SC-13 | R1-W10 point-biserial | R1 | raised | text: §3.4 "assessed with Pearson correlations" | Major | 5 |
| SC-14 | R1-W14 median split | R1 | raised | text: §3.3 "split at the median" | Major | 5 |
| SC-15 | R1-W12 no ES/CI/power | R1 | raised | absence: §4 effect sizes and intervals | Major | 5 |
| SC-16 | R1-W13 sessionisation | R1 | raised | text: §3.3 "at least thirty minutes of inactivity" | Major | 5 |
| SC-17 | R1-W15 single items | R1 | raised | text: §3.3 "single-item overall ratings are common…" | Major | 4 |
| SC-17 | R2-W12 | R2 | corroborated | text: §3.3 same sentence | Minor | 4 |
| SC-18 | R1-W18 exam score | R1 | raised | table: Table 1 "Final exam score (0-100)" | Minor | 5 |
| SC-19 | R1-W9 causal claims | R1 | raised | text: §5 "improved course retention"; §6 "dependable strategy" | Critical | 5 |
| SC-19 | EIC-W3 | EIC | corroborated | text: §5/§6 | Major | 5 |
| SC-19 | R2-W3 | R2 | corroborated | text: §5/§6 vs §2 declared scope | Major | 5 |
| SC-19 | R3-W4 | R3 | corroborated | text: §6 "For higher education institutions worldwide" | Major | 5 |
| SC-20 | EIC-W3 generalisation | EIC | raised | text: §6 "worldwide" / "generalizable lever" | Major | 5 |
| SC-20 | R1-W9 | R1 | corroborated | text: §6 "across programs and disciplines" | Critical | 5 |
| SC-20 | R2-W2 | R2 | corroborated | text: §1 attrition framing vs §3.3 coding | Major | 5 |
| SC-20 | R3-W4 | R3 | corroborated | text: §6 vs §5.1 | Major | 5 |
| SC-21 | EIC-W3 limitations gap | EIC | raised | text: §5.1 four limitations listed | Major | 5 |
| SC-21 | R1-W11 / body | R1 | corroborated | text: §5.1 silent on selection, survivorship, reverse causation | Major | 5 |
| SC-21 | R2-S2 | R2 | **disputed** | text: §5.1 "operationalized narrowly as session counts…" | `[SEVERITY-SOURCE: letter-fallback]` strength-band | `[CONFIDENCE-SOURCE: unavailable]` |
| SC-22 | R2-W4 proxy→construct | R2 | raised | text: §5 "scaffold monitoring and adjustment" | Major | 5 |
| SC-23 | R2-W4 SRL decorative | R2 | raised | text: Abstract "self-regulated learning behavior" vs §3.3 single item | Major | 5 |
| SC-24 | R2-W1 attribution reversal | R2 | raised | text: §2 claim vs reference title "When dashboards demotivate" | Critical | 5 |
| SC-24 | EIC-W7 | EIC | corroborated | text: §2 and References | Major | 4 |
| SC-24 | R3-W5 | R3 | corroborated | text: §2 "equity-oriented rationale" | Major | 4 |
| SC-25 | R3-W6 no subgroup analysis | R3 | raised | absence: §4 Results and §5 Discussion | Major | 5 |
| SC-25 | R2-W5 | R2 | corroborated | text: §2 vs §5 | Major | 4 |
| SC-26 | R2-W5 goal orientation | R2 | raised | text: §2 performance-avoidance vs §5 | Major | 4 |
| SC-26 | R3-W6 / S3 | R3 | corroborated | text: §2 discouragement mechanism | Major | 5 |
| SC-27 | EIC-W5 no synthesis | EIC | raised | absence: §1/§2/§5/§6 and References | Major | 5 |
| SC-27 | R2-W11 uncited syntheses | R2 | corroborated | absence: References (Halloran, Kessler & Amadou) | Minor | 5 |
| SC-28 | EIC-W6 uncited entries | EIC | raised | text: References — six of sixteen cited | Major | 4 |
| SC-28 | R2-W11 | R2 | corroborated | absence: References, nine named entries | Minor | 5 |
| SC-29 | EIC-W6 DOI prefix | EIC | raised | text: References "https://doi.org/10.5555/1010203" | Major | 4 |
| SC-30 | R2-W2 construct drift | R2 | raised | text: §3.3 coding rule with §1 attrition framing | Major | 5 |
| SC-30 | R3-W3 | R3 | corroborated | text: §6 "student success at scale" | Major | 4 |
| SC-31 | R2-W12 uncited practice claim | R2 | raised | text: §3.3 "common in dashboard studies" | Minor | 4 |
| SC-32 | R3-W1 consent scope | R3 | raised | text: §3.2 "Students were not informed…" | Critical | 5 |
| SC-32 | EIC-W2 | EIC | corroborated | text: §3.2 same sentence | Critical | 5 |
| SC-32 | R1-W16 | R1 | corroborated | text: §3.2 same sentence | Major | 4 |
| SC-32 | R2 body referral | R2 | corroborated | text: §3.2 ("not a mere compliance matter") | `[SEVERITY-SOURCE: letter-fallback]` Major-band | `[CONFIDENCE-SOURCE: unavailable]` |
| SC-33 | R3-W2 no ethics documentation | R3 | raised | absence: §3.2 and front/back matter | Major | 5 |
| SC-33 | EIC-W2 | EIC | corroborated | absence: Abstract, §3, §5.1, §6, References | Critical | 5 |
| SC-33 | R1-W16 | R1 | corroborated | absence: ethics/IRB statement | Major | 4 |
| SC-34 | R3-W7 indicator-as-target | R3 | raised | text: §6 "encouraging students to engage" + §3.3 session definition | Major | 4 |
| SC-35 | R3-W8 nothing actionable | R3 | raised | absence: §6 cost/staffing/comparison | Minor | 4 |
| SC-36 | EIC-W4 response rate | EIC | raised | text: §3.2 "several hundred" enrolled | Major | 5 |
| SC-36 | R1-W3 item non-response | R1 | corroborated | text: §4.1 "87 survey respondents" vs n = 142 | Major | 5 |
| SC-37 | EIC-W10 orphan subsample | EIC | raised | text: §4.1 run-in values | Minor | 4 |

### DA-track findings (adjudicated, not counted in the 4-seat consensus)

| DA id | Claim | Corroborated by | Journal-Fit / editorial assessment | Adjudication |
|---|---|---|---|---|
| C1 | Causal/prescriptive conclusions from an observational design with no rival exclusion | EIC-W3, R1-W9, R2-W3, R3-W4 (SC-19, CONSENSUS-4) | Sustained on four independent grounds | VALIDATED |
| C2 | Partial circularity: engagement accrues only while enrolled | R1-W7 (SC-8, D1 fatal ground) | Sustained; remedy scope disputed (see Disagreement 1) | VALIDATED |
| C3 | Survivorship + volunteer selection at mid-term recruitment | R1-W7, EIC-W4, R2-W5 (SC-9) | Sustained | VALIDATED |
| C4 | Abstract r = .42 vs Results r = .24 | all four seats (SC-1) | Sustained | VALIDATED |
| C5 | t(156) irreconcilable with any described sample | all four seats (SC-2) | Sustained | VALIDATED |
| C6 | t = 1.31 / p = .008 impossible and self-contradicting | R1-W2, EIC-W9, R2-W9 (SC-3) | Sustained | VALIDATED |
| C7 | Trace data analysed without notice; no ethics statement | R3-W1 (Critical), EIC-W2 (Critical), R1-W16, R2 referral (SC-32/33) | Sustained; DA's own confidence 4 is exceeded by two Critical/conf-5 corroborations | VALIDATED |
| M1–M9 | Generalisation contradiction, attribution reversal, sampling contradiction, missing retention marginal, impossible SD, unmodelled mediation, Table 2 sum, missing response rate, proxy→construct | mapped to SC-20, SC-24, SC-10, SC-12, SC-5, SC-22/23, SC-4, SC-36, SC-22 | All carried into the Roadmap | recorded |

DA MAJOR M6 (mediation asserted without a model or temporal ordering) has no non-DA raiser; it is carried into roadmap item R9 as a DA-track finding rather than as a consensus sub-claim.

---

## Step 1c — Surface-Form Parity Check

All five cards are technically phrased, so the informal-vs-precise asymmetry had little surface to act on — but the check was applied where weighting actually happened. Two records:

- **R2's dispute on SC-21** is grounded in a strength note ("Limitations names the correct three constraints"), not in a graded finding, so it carries no transported severity or confidence. I down-weighted it relative to EIC-W3/R1-W11 on **evidence** (the §5.1 text names three items and not the two at issue) and on **expertise** (design-threat identification sits in R1's dimension), not on its informal, non-tabulated form. Opposite-style counterfactual: had R2 filed the same position as a graded finding with an anchor, the arbitration outcome would be unchanged, because §5.1's contents are checkable independently of phrasing.
- **R3's SC-2 corroboration** arrives at Minor/confidence 3 with an explicit disclaimer ("I do not verify statistical computation"). I did not credit it as arithmetic corroboration, and I did not discount R3's *other* findings for the hedged register. Counterfactual: rewritten in confident technical prose, the same seat would still lack an arithmetic basis, so the weight is keyed to the stated basis, not the style.

No sub-claim was marked unevaluable. Authorship was not a weighting input.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript titled "Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment." Your manuscript has been reviewed by five independent reviewers, including a Journal-Fit Reviewer and an adversarial reader.

### Decision: Reject

### Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — this synthesis ran in `reviewer_full` mode, in which one of three provenance statements (cross-model slot active / single-family disclosure / dispatch-failure fallback) is mandatory. No provenance stamp was supplied by the dispatching layer with the five reviewer cards, and I do not infer one. Readers should therefore **not** assume model independence across the five seats: which model family produced which seat's card is not established on this record. The dispatching layer must supply the stamp before this letter is released.

### Consensus Analysis

#### Points of Agreement (Consensus)

- **[CONSENSUS-4]** *(SC-1)* The Abstract's headline correlation (r = .42) is not the correlation the Results report (r = .24). All four seats state that no reader can determine which value the study produced; the difference is roughly threefold in shared variance, and every downstream claim is calibrated against an unknown quantity.
- **[CONSENSUS-4]** *(SC-2)* The perceived-control comparison reports t(156), implying ~158 cases, against an item-level n of 87 and a primary sample of 142. No described sample can produce it.
- **[CONSENSUS-4]** *(SC-19)* The Discussion and Conclusion assert causation ("improved," "raises the probability") from an observational, cross-sectional, volunteer-sample association with no covariate adjustment — in direct breach of the Introduction's own stated commitment and of the critique the paper itself cites (Ibarra, 2023).
- **[CONSENSUS-4]** *(SC-20)* The Conclusion's advice to institutions "worldwide," and its "dependable"/"generalizable" characterisation, are unsupported by one course, one term, one dashboard design, one institution — and contradict the manuscript's own §5.1.
- **[CONSENSUS-4]** *(SC-32)* §3.2 states that students were not informed their dashboard activity data would be analysed for this study, while the described consent covers the survey only and the primary result rests on the logs.
- **[CONSENSUS-3]** *(SC-3, SC-4, SC-5; silent seat: R3)* The exam comparison is internally irreconcilable — t = 1.31 with df = 140 does not give p = .008; the same sentence reports a value below the stated alpha while calling the result non-significant; Table 2's ns sum to 127 against "all 142 students were classified." The secondary clarity item's SD = 0.10 is unobtainable for ten integer responses averaging exactly 3.00.
- **[CONSENSUS-3]** *(SC-9, SC-10; silent seat: R3)* §3.2 gives two mutually exclusive sampling frames — "a random sample of students enrolled in the course section" and a mid-term volunteer opt-in with non-respondents excluded — and the operative recruitment description means students who withdrew before mid-term cannot be in the sample at all.
- **[CONSENSUS-3]** *(SC-24; silent seat: R1)* §2 credits Ferro & Nakamura (2021) with the reverse of what the listed title reports, and the manuscript makes that inverted claim the basis of its equity rationale and returns to it in the Discussion.
- **[CONSENSUS-3]** *(SC-33; silent seat: R2)* No ethics approval, IRB determination, waiver rationale, data-protection basis, or data-availability statement appears anywhere in the submission.

**Corroborated findings (2/4, below the consensus bar but action-bearing):** SC-6, SC-7, SC-11, SC-17, SC-25, SC-26, SC-27, SC-28, SC-30, SC-36. **Single-reviewer findings retained on confidence weight (all at confidence 4–5):** SC-8, SC-12, SC-13, SC-14, SC-15, SC-16, SC-18, SC-22, SC-23, SC-29, SC-31, SC-34, SC-35, SC-37.

#### Points of Disagreement

- **Disagreement 1 — remedy scope for the exposure-window problem (SC-8 / DA C2).** R1 holds that no re-analysis of this sample can separate the definitional from the empirical component of r, because the association would require a full-cohort log extraction with a time-anchored exposure window closed before any withdrawal — a different study. The Devil's Advocate holds the fix is available in principle: count sessions only in a fixed early window (e.g. weeks 1–4) that eventual withdrawers also inhabited.
  - **Editor's Resolution:** R1's reading holds. This is an *existence-of-remedy* question inside R1's owned dimension (expertise-first), and the evidence decides it: §3.2 states "The behavioral log data were drawn from the LMS for the same set of respondents." A fixed early window therefore still runs inside a sample conditioned on surviving to a mid-term announcement, so it cures the circularity component and leaves the survivorship component untouched. The DA's fix is a necessary part of any future design, not a repair to this dataset. This resolution is the substantive ground of the fatal D1 block and hence of the decision.
- **Disagreement 2 — adequacy of the Limitations section (SC-21, [SPLIT]).** EIC and R1 hold that §5.1 omits precisely the two constraints that bound the conclusion drawn (self-selection/survivorship, and the correlational→causal boundary). R2's strength note treats §5.1 as naming "the three constraints a competent referee in this area would expect to see acknowledged."
  - **Editor's Resolution:** the finding is upheld and R2's observation is retained as partial credit. Evidence-first: §5.1's four items are the session-count proxy, self-report bias, the single course, and interface specificity — none of which is selection, survivorship, or reverse causation. Expertise-first: identification of design threats sits in R1's dimension. R2 is right that what §5.1 *does* say is accurate and unhedged; that does not rebut what it omits. Roadmap item R11 carries the repair.
- **Disagreement 3 — gate framing versus revision framing on ethics (SC-32/33).** EIC treats the undisclosed log analysis as a gate item ("not a missing paragraph"); R3 treats it as making publication impossible unless approval status is established, and possibly a conduct-of-research matter; R1 bands it Major with an explicit ceiling that "depends on an editorial and ethics-board determination outside my seat."
  - **Editor's Resolution:** not averaged into a moderate verdict. It is recorded as a **precondition**: whatever happens to the statistics, no version of this work can be reviewed further until the approving body, protocol number, and the waiver or exemption basis for the log analysis are on the record. Because the mechanical decision is already Reject on D1, this precondition does not alter the decision; it constrains any future submission absolutely. R1's ceiling caveat is the correct posture on severity — the ceiling is an editorial determination, and I am making it here.
- **Severity-band divergences recorded without conflict classification.** SC-1 (EIC Critical vs R1/R2/R3 Major), SC-5 (R1 Major "requires audit of all descriptives" vs EIC/R2 Minor "changes no conclusion"), SC-32/33 (Critical vs Major). In each case the recommended remedies are compatible rather than incompatible, so none is classified `disputed`. For SC-5 both actions are carried: the value enters the descriptives audit in R2 *and* the presentation cleanup sits at P3 in S10.

#### Item no configured seat owned

Reference verifiability could not be established. All sixteen entries carry DOIs on the reserved, non-resolving `10.5555` prefix, and ten are never cited in the body. I record this as unverifiable-as-printed, which it is, and not as a substantive judgment about the authors' conduct — the two are different findings and only the first is on the evidence.

### Decision Rationale

The decision follows from the contract's failure conditions applied to the panel's dimension scores, and F1 — a fatal block on a mandatory dimension — is the highest-severity condition fired.

Two independent problems produced it. First, the reported statistics correspond to at least three mutually incompatible sample sizes (127, 142, 158), and two reported descriptives cannot arise from the integer scales the Methods describe. Individually these read as transcription slips; their density and their spread across the sampling frame, the headline association, the self-report result, and the secondary comparison mean that no substantive finding in Section 4 can currently be evaluated. Second — and this is why the verdict is Reject rather than Major Revision — the exposure measure accumulates only while a student remains enrolled, while the outcome is the event that stops accumulation. Part of the reported association is definitional before any behavioural mechanism is invoked, and the mid-term volunteer recruitment window means the logs exist only for students who had already survived past the point where retention variance lives. That is not a reporting defect. Recovering the stated estimand requires full-cohort logs, an exposure window closed before any withdrawal, and baseline covariates — a new study, not a revision of this one.

Independently of both, the manuscript states that students were not informed their trace data would be analysed, with no ethics documentation of any kind. That is a precondition for any further review.

The manuscript's strengths are real and should survive into whatever comes next: an unhedged design statement, an operationalisation that handles the non-obvious retention case, a literature review that names the field's measurement and causal-inference problems and applies them to itself, and a genuinely unhedged single-course limitation. The claim layer, not the self-awareness, is what failed.

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| 1 | Exposure window is truncated by the outcome and the sample is survivorship-filtered by mid-term recruitment, so the stated estimand is not recoverable from this dataset | R1 (D1 fatal); DA C2, C3 | text: §3.3 "the number of distinct sessions in which a student opened the dashboard view during the term"; §3.2 "Midway through the term, an announcement was posted to the course LMS" | R1 |
| 2 | Reported statistics imply at least three incompatible sample sizes and two arithmetically unobtainable descriptives; the Abstract's headline r is not the Results' r | R1, EIC, R2, R3; DA C4, C5, C6, M5, M7 | text: §4.3 "t(156) = 3.02, p = .003"; §4.3 "t(140) = 1.31, p = .008"; Abstract "r = .42" vs §4.2 "r = .24" | R2 |
| 3 | Student trace data analysed without notice, with no ethics approval, waiver rationale, or data-governance statement anywhere in the submission | EIC (Critical), R3 (Critical), R1 (Major), R2 (referral); DA C7 | text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study." | R3 |

---

## Part 2: Revision Roadmap

> This decision is Reject, so the roadmap below is not a revision clock for this manuscript. It is the constructive path a future submission would have to satisfy. Items marked **[new data required]** cannot be met by re-analysing the present dataset.
>
> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. Items with no sub-claim id (DA-only or aggregated editorial) use `—`.

### Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| R1 | Re-estimate the engagement–persistence association on full-cohort logs with an exposure window closed before any withdrawal could occur, and report the retention marginal **[new data required]** | SC-8, SC-12 | Critical | text: §3.3 "the number of distinct sessions in which a student opened the dashboard view during the term" | 5 — measurement-window logic from the paper's own definitions | R1; DA C2, M4 | P1 | ≥1 full term + log extraction |
| R2 | Supply raw analysis output and a variable-level data dictionary, then reconcile or correct every reported statistic (r, both t-tests, all df and p, Table 2 cells, M = 3.847, SD = 0.10) and the Abstract | SC-1, SC-2, SC-3, SC-4, SC-5, SC-6 | Critical | text: §4.3 "t(156) = 3.02, p = .003"; Abstract "r = .42" vs §4.2 "r = .24" | 5 — arithmetic recomputation against the manuscript's own stated Ns | R1, EIC, R2, R3; DA C4–C6, M5, M7 | P1 | 1–2 weeks if analysis files exist |
| R3 | Document the approving body, protocol number, and waiver/exemption basis for the log analysis, plus retention and de-identification arrangements — or withdraw all log-based analyses | SC-32, SC-33 | Critical | text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study." | 5 — the manuscript states the fact; absence checked across all plausible surfaces | EIC, R3 (both Critical), R1, R2 referral; DA C7 | P1 | institutional dependency: days to weeks, or unobtainable |
| R4 | Resolve the sampling-frame contradiction; report the response rate against the enrolment denominator; state the survivorship filter; give a per-analysis exclusion/missingness flow (142 → 127 → 87) | SC-9, SC-10, SC-36 | Critical (R1) / Major (EIC, R2) | text: §3.2 "using a random sample of students enrolled in the course section" vs "Students who chose to respond… were excluded." | 5 — two statements in one subsection cannot both hold | EIC, R1, R2; DA M3, M8 | P1 | 2–3 days |
| R5 | Rewrite the Discussion and Conclusion in strictly associational register; delete the causal verbs, the "dependable"/"generalizable" characterisation, and the worldwide-deployment advice; recalibrate title and Abstract to match | SC-19, SC-20 | Critical (R1) / Major (EIC, R2, R3) | text: §5 "dashboard engagement improved course retention"; §6 "is a dependable strategy for improving retention across programs and disciplines" | 5 — claim-to-design alignment, four independent seats | R1, EIC, R2, R3; DA C1, M1 | P1 | 1 week |
| R6 | Recheck the Ferro & Nakamura (2021) attribution against the source and rebuild the equity rationale and Discussion passage that rest on it | SC-24 | Critical (R2) / Major (EIC, R3) | text: §2 "Dashboards have been shown to reliably improve outcomes for lower-achieving students" vs reference title "When dashboards demotivate: Peer comparison and the lower-achieving student" | 5 — in-text attribution vs the reference entry printed in the same manuscript | R2; EIC, R3; DA M2 | P1 | 3–5 days |
| R7 | Reframe the study as single-course completion throughout (title, Abstract, framing, implications), or measure persistence across enrolment periods **[new data required for the latter]** | SC-30 | Major | text: §3.3 "coded dichotomously as whether the student remained enrolled and completed the final assessment" with §1 "Undergraduate attrition remains a persistent concern" | 5 — construct boundary in persistence research, checked against the paper's coding rule | R2, R3 | P1 | 1 week (reframe) |
| R8 | Fit a covariate-adjusted model (logistic, with prior attainment, credit load, major, concurrent load), name the coefficient point-biserial where correlation is retained, and address reverse causation explicitly **[covariate extraction required]** | SC-11, SC-13 | Major | text: §3.4 "Associations between continuous measures were assessed with Pearson correlations." | 5 — exhaustive read of Measures and Analysis | R1; DA C1 | P1 | 2 weeks |
| R9 | Withdraw or evidence the SRL mechanism claim and the mediation claim; remove "self-regulated learning behavior" from the Abstract unless strategy-use and monitoring measures are added | SC-22, SC-23, — (DA M6) | Major | text: Abstract "we measured dashboard engagement, self-regulated learning behavior, and course persistence" with §3.3 "measured with a single-item overall rating" | 5 — mismatch between invoked constructs and the item administered | R2; DA M6, M9 | P1 | 3–5 days |
| R10 | Run differential-effect/subgroup analysis (minimum: stratified by prior achievement) before any equity or deployment claim, and reconcile the goal-orientation rival account the paper itself raises | SC-25, SC-26 | Major | absence: §4 Results and §5 Discussion — expected differential-effect analysis for a dashboard containing a peer-comparison band; checked Table 1, Table 2, §4.1–§4.3, §5, §5.1 | 5 — harm-profile analysis of relative-standing feedback | R3, R2 | P1 | 1 week |
| R11 | Restate §5.1 to include self-selection/survivorship and the correlational→causal boundary, retaining the four limitations already stated | SC-21 ([SPLIT], arbitrated) | Major | text: §5.1 — four limitations listed, none covering selection, survivorship, or reverse causation | 5 — EIC and R1 at confidence 5; R2's dispute carries no graded finding | EIC, R1 (R2 dissenting; arbitrated in favour of the finding) | P1 | 1 day |
| R12 | Supply resolvable identifiers for every reference; cite or delete the ten uncited entries; engage at least one named systematic review or meta-analysis of student-facing dashboards and state the increment in testable terms | SC-27, SC-28, SC-29 | Major | text: References "https://doi.org/10.5555/1010203"; absence: §1/§2/§5/§6 engagement with any synthesis | 4–5 — pattern directly observable; what the DOI prefix indicates about provenance is not | EIC, R2 | P1 | 3–5 days |

### Required Item Details

#### R1
- **Acceptance criteria**: The engagement measure is computed inside a fixed calendar window that closed before the earliest observed withdrawal, on logs extracted for the full enrolled cohort rather than for survey respondents, and the count and proportion of students coded not retained is reported in Results.

#### R2
- **Acceptance criteria**: Every statistic in Section 4 and both tables is reproducible from supplied raw output and a variable-level data dictionary, each reported df matches its stated analytic n, each p matches its own t and df, the Abstract's correlation equals the Results' correlation, and no descriptive is arithmetically unattainable on its stated response scale.

#### R3
- **Acceptance criteria**: The manuscript names the approving body and protocol identifier, states the waiver or exemption basis covering secondary analysis of individually linked behavioural logs, describes retention and de-identification arrangements, and reproduces the notice students actually received — or contains no log-based analysis.

#### R4
- **Acceptance criteria**: Section 3.2 gives one internally consistent sampling description, reports the survey response rate against the full enrolment denominator, states explicitly that students who withdrew before recruitment are absent from the sample, and supplies a participant flow accounting for every case in each reported analysis.

#### R5
- **Acceptance criteria**: No sentence in the Abstract, Discussion, or Conclusion asserts that dashboard engagement improved, raised, or caused retention, none characterises the finding as dependable or generalizable, none addresses institutions beyond the studied setting, and the title and Abstract state the same effect magnitude as Section 4.

#### R6
- **Acceptance criteria**: Every claim attributed to Ferro and Nakamura (2021) matches that source's stated finding, and the equity rationale in Section 2 and its return in the Discussion are rewritten to follow from the corrected attribution or removed.

#### R7
- **Acceptance criteria**: The word "retention" is used only for the measured construct or replaced by "course completion" throughout, and every implication claim that requires institutional or programme persistence is either supported by cross-period data or deleted.

#### R8
- **Acceptance criteria**: The engagement–completion association is reported from a model adjusting for at least prior attainment and credit load, any retained bivariate coefficient is identified as point-biserial with the outcome marginal reported, and reverse causation is addressed as a named alternative in both Discussion and Limitations.

#### R9
- **Acceptance criteria**: The manuscript either reports strategy-use and monitoring measures supporting the self-regulated learning account, or states in Abstract, Discussion, and Limitations that no regulatory behaviour was measured and that no mediation is claimed or tested.

#### R10
- **Acceptance criteria**: Results reports the association separately by prior-achievement stratum with a differential-effect test, the Discussion states who was and was not observed to benefit, and the goal-orientation counter-account raised in Section 2 is either supported or excluded on reported evidence before any deployment recommendation appears.

#### R11
- **Acceptance criteria**: Section 5.1 names self-selection into the sample, survivorship arising from mid-term recruitment, and the correlational-to-causal boundary, in addition to the four limitations already stated.

#### R12
- **Acceptance criteria**: Every reference carries a resolvable identifier, every listed entry is cited at least once in the body, and Section 1 or 2 positions the study against at least one named systematic review or meta-analysis of student-facing dashboards with an explicit statement of what this study adds.

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| S1 | Report a sessionisation sensitivity analysis across plausible inactivity thresholds (e.g. 10/30/60 minutes) for the independent variable | SC-16 | Major | text: §3.3 "A session was defined as a dashboard view preceded by at least thirty minutes of inactivity" | 5 — established sensitivity of session counts to the threshold | R1 | P2 | 2–3 days |
| S2 | Replace the median split with the continuous predictor already available in the data; retain the split only as a secondary presentation | SC-14 | Major | text: §3.3 "students were split at the median number of dashboard sessions" | 5 — standard result on dichotomisation of continuous predictors | R1 | P2 | 1–2 days |
| S3 | Report standardised effect sizes with confidence intervals for every comparison and an a priori power justification | SC-15 | Major | absence: §4 — expected effect sizes with confidence intervals; checked Analysis, Results, Tables, Abstract | 5 — no such statistics appear | R1 | P2 | 2 days |
| S4 | Provide reliability/validity evidence for the perceived-control measure or replace it with a validated multi-item instrument; report the 39% item non-response as such | SC-17, SC-6 | Major (R1) / Minor (R2) | text: §3.3 "single-item overall ratings are common in dashboard studies to limit survey burden" | 4 — clear from Measures; strength depends on venue norms for single-item global ratings | R1, R2 | P2 | 3–5 days (instrument change: new collection) |
| S5 | Operationalise the final exam score in Measures and state its non-independence from the retention coding | SC-18 | Minor | table: Table 1, row "Final exam score (0-100)" | 5 — the variable is absent from the Measures subsection | R1 | P2 | 0.5 day |
| S6 | Name the statistical software and version, supply analysis code, and add a data-availability statement | SC-7 | Minor (R1) / Major-band `[SEVERITY-SOURCE: letter-fallback]` (EIC) | absence: §3.4 and end matter — expected named software with version, code, and a data availability statement | 5 (R1) / `[CONFIDENCE-SOURCE: unavailable]` (EIC) | R1, EIC | P2 | 1 day |
| S7 | Address indicator corruption: state that a session count driven up by institutional exhortation carries no demonstrated relationship to persistence | SC-34 | Major | text: §6 "encouraging students to engage with them is a dependable strategy"; §3.3 session definition | 4 — standard failure mode in institutional metric deployment | R3 | P2 | 1 day |
| S8 | Add cost, staffing and advising-capacity requirements and a comparison against alternative retention interventions, or withdraw the practitioner address | SC-35 | Minor | absence: §6 — expected cost, staffing, and comparison against alternative interventions; checked §5, §5.1, §6, References | 4 — comparative business cases for analytics investment | R3 | P3 | 2–3 days |
| S9 | Cite or delete the claim that single-item overall ratings are common practice in dashboard studies | SC-31 | Minor | text: §3.3 "single-item overall ratings are common in dashboard studies to limit survey burden" | 4 — the claim is uncited on its face | R2 | P3 | 0.5 day |
| S10 | Remove or integrate the orphan ten-student clarity subsample, replace the run-in numeric list with prose or a table, and harmonise decimal precision across Table 1 and Section 4 | SC-5, SC-37 | Minor | text: §4.1 "the reported secondary-item values were N=10; M=3.00; sample SD=0.10; integer scale=1-5" | 4 — presentation defects directly observable | EIC | P3 | 0.5 day |
| S11 | Aggregated editorial channel: reconcile §3.1's "disciplinary breadth" with §6's "across programs and disciplines"; correct the Abstract's implication that survey data cover all 142 students; harmonise reporting precision throughout | — | (editorial; below finding threshold) | text: §3.1 "giving the sample some disciplinary breadth even within one course" with §6 "across programs and disciplines" | (editorial) | DA minor list | P3 | 1 day |

> Transported metadata appears on every row above: each item carries the driving sub-claim's transported Severity (with `[SEVERITY-SOURCE: letter-fallback]` / `[CONFIDENCE-SOURCE: unavailable]` tags travelling where a card had no graded finding), the finding's typed Evidence Anchor, and its per-finding Confidence. Severity is transported, never re-derived; where seats banded the same sub-claim differently, both bands are shown with their seats.

### Revision Checklist (Checkable List)

#### Priority 1 — Structural (estimated total effort: ≥1 full term for new-data items, plus ~5–6 weeks of re-analysis and rewriting)
- [ ] R1: Re-estimate on full-cohort logs with a pre-withdrawal exposure window; report the retention marginal **[new data required]**
- [ ] R2: Supply raw output and data dictionary; reconcile every statistic; correct the Abstract
- [ ] R3: Document ethics approval and waiver basis for the log analysis, or withdraw the log analyses **[precondition]**
- [ ] R4: Fix the sampling description; report response rate and full participant flow
- [ ] R5: Rewrite Discussion, Conclusion, title, and Abstract in associational register
- [ ] R6: Recheck the Ferro & Nakamura attribution; rebuild the equity rationale
- [ ] R7: Reframe as single-course completion, or measure cross-period persistence
- [ ] R8: Fit a covariate-adjusted model; name point-biserial; address reverse causation
- [ ] R9: Withdraw or evidence the SRL mechanism and mediation claims
- [ ] R10: Run differential-effect analysis; reconcile the goal-orientation account
- [ ] R11: Restate Limitations to include selection/survivorship and the causal boundary
- [ ] R12: Supply resolvable references; cite or delete unused entries; engage a synthesis

#### Priority 2 — Content Supplementation (estimated total effort: ~2 weeks)
- [ ] S1: Sessionisation sensitivity analysis
- [ ] S2: Continuous predictor in place of the median split
- [ ] S3: Effect sizes, confidence intervals, power justification
- [ ] S4: Measurement evidence for perceived control; report item non-response
- [ ] S5: Operationalise final exam score; state its dependence on the retention coding
- [ ] S6: Software, code, and data-availability reporting
- [ ] S7: Address indicator corruption in any practice recommendation

#### Priority 3 — Text and Formatting (estimated total effort: ~3 days)
- [ ] S8: Cost, staffing, and comparative-intervention content, or withdraw the practitioner address
- [ ] S9: Cite or delete the single-item practice claim
- [ ] S10: Remove or integrate the orphan subsample; fix run-in numerics and decimal precision
- [ ] S11: Editorial channel — "disciplinary breadth" slide, Abstract's survey-coverage implication, precision consistency

### Revision Deadline

Not applicable as a revision clock: this is a Reject, and no resubmission of this manuscript to this venue can be reviewed until R3 (ethics documentation) is satisfied. If the work is rebuilt, the timeline is dominated by R1's new cohort-level log extraction (≥1 full term) plus roughly 5–6 weeks of re-analysis and rewriting for the remaining P1 items. Any new submission should be presented as a new study, not a revision.

### Response Letter Template

Use the format in `templates/revision_response_template.md` and respond to every item R1–R12 and S1–S11 individually, quoting the item, stating the action taken, and giving the manuscript location of the change. Two items require a specific form of response: for R3, attach or quote the institutional documentation rather than describing it; for R2, attach the raw analysis output and data dictionary rather than supplying a corrected proof.

### Machine-form (Schema 7)

```json
{
  "schema": 7,
  "roadmap_id": "reviewer/reviewer_full/v2::editorial_synthesis",
  "editorial_decision": "reject",
  "items": [
    {"id": "R1", "priority": "must_fix", "reviewer": "R1", "sub_claims": ["SC-8", "SC-12"], "severity": "critical", "confidence": 5, "evidence_anchor": "text: §3.3 'the number of distinct sessions in which a student opened the dashboard view during the term'", "verification_criteria": "Engagement computed in a fixed window closed before the earliest observed withdrawal, on full-cohort logs; retention marginal reported in Results.", "requires_new_data": true},
    {"id": "R2", "priority": "must_fix", "reviewer": "R1,EIC,R2,R3", "sub_claims": ["SC-1", "SC-2", "SC-3", "SC-4", "SC-5", "SC-6"], "severity": "critical", "confidence": 5, "evidence_anchor": "text: §4.3 't(156) = 3.02, p = .003'; Abstract 'r = .42' vs §4.2 'r = .24'", "verification_criteria": "Every Section 4 and table statistic reproducible from supplied raw output and data dictionary; df matches stated n; p matches t and df; Abstract r equals Results r; no descriptive unattainable on its stated scale.", "requires_new_data": false},
    {"id": "R3", "priority": "must_fix", "reviewer": "EIC,R3,R1,R2", "sub_claims": ["SC-32", "SC-33"], "severity": "critical", "confidence": 5, "evidence_anchor": "text: §3.2 'Students were not informed that their dashboard activity data would be analyzed for this study.'", "verification_criteria": "Approving body and protocol id named; waiver/exemption basis for secondary log analysis stated; retention and de-identification described; student notice reproduced — or no log-based analysis present.", "gate": true},
    {"id": "R4", "priority": "must_fix", "reviewer": "EIC,R1,R2", "sub_claims": ["SC-9", "SC-10", "SC-36"], "severity": "critical", "confidence": 5, "evidence_anchor": "text: §3.2 'using a random sample of students enrolled in the course section'", "verification_criteria": "One internally consistent sampling description; response rate against full enrolment; survivorship filter stated; participant flow accounts for every case in each analysis."},
    {"id": "R5", "priority": "must_fix", "reviewer": "R1,EIC,R2,R3", "sub_claims": ["SC-19", "SC-20"], "severity": "critical", "confidence": 5, "evidence_anchor": "text: §5 'dashboard engagement improved course retention'; §6 'is a dependable strategy for improving retention across programs and disciplines'", "verification_criteria": "No causal verb, dependability or generalizability characterisation, or extra-setting institutional address in Abstract, Discussion, or Conclusion; title and Abstract magnitudes match Section 4."},
    {"id": "R6", "priority": "must_fix", "reviewer": "R2,EIC,R3", "sub_claims": ["SC-24"], "severity": "critical", "confidence": 5, "evidence_anchor": "text: §2 vs reference title 'When dashboards demotivate: Peer comparison and the lower-achieving student'", "verification_criteria": "Every claim attributed to Ferro & Nakamura (2021) matches that source's stated finding; dependent equity rationale rewritten or removed."},
    {"id": "R7", "priority": "must_fix", "reviewer": "R2,R3", "sub_claims": ["SC-30"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.3 'coded dichotomously as whether the student remained enrolled and completed the final assessment' with §1 'Undergraduate attrition remains a persistent concern'", "verification_criteria": "'Retention' used only for the measured construct or replaced by 'course completion'; implication claims requiring cross-period persistence supported or deleted."},
    {"id": "R8", "priority": "must_fix", "reviewer": "R1", "sub_claims": ["SC-11", "SC-13"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.4 'Associations between continuous measures were assessed with Pearson correlations.'", "verification_criteria": "Association reported from a model adjusting for at least prior attainment and credit load; any bivariate coefficient identified as point-biserial with outcome marginal; reverse causation named in Discussion and Limitations.", "requires_new_data": true},
    {"id": "R9", "priority": "must_fix", "reviewer": "R2", "sub_claims": ["SC-22", "SC-23"], "severity": "major", "confidence": 5, "evidence_anchor": "text: Abstract 'we measured dashboard engagement, self-regulated learning behavior, and course persistence' with §3.3 'measured with a single-item overall rating'", "verification_criteria": "Strategy-use and monitoring measures reported, or Abstract/Discussion/Limitations state that no regulatory behaviour was measured and no mediation is claimed or tested."},
    {"id": "R10", "priority": "must_fix", "reviewer": "R3,R2", "sub_claims": ["SC-25", "SC-26"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §4 Results and §5 Discussion — expected differential-effect analysis for a dashboard containing a peer-comparison band", "verification_criteria": "Association reported by prior-achievement stratum with a differential-effect test; Discussion states who was and was not observed to benefit; goal-orientation counter-account supported or excluded before any deployment recommendation."},
    {"id": "R11", "priority": "must_fix", "reviewer": "EIC,R1", "sub_claims": ["SC-21"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §5.1 — four limitations listed, none covering selection, survivorship, or reverse causation", "verification_criteria": "Section 5.1 names self-selection, survivorship from mid-term recruitment, and the correlational-to-causal boundary in addition to the existing four limitations.", "arbitration": "SPLIT: R2 dissenting; finding upheld on evidence and dimension ownership."},
    {"id": "R12", "priority": "must_fix", "reviewer": "EIC,R2", "sub_claims": ["SC-27", "SC-28", "SC-29"], "severity": "major", "confidence": 4, "evidence_anchor": "text: References 'https://doi.org/10.5555/1010203'; absence: §1/§2/§5/§6 engagement with any synthesis", "verification_criteria": "All references carry resolvable identifiers; every listed entry cited at least once; study positioned against a named systematic review or meta-analysis with an explicit increment statement."},
    {"id": "S1", "priority": "should_fix", "reviewer": "R1", "sub_claims": ["SC-16"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.3 'A session was defined as a dashboard view preceded by at least thirty minutes of inactivity'", "verification_criteria": "Association re-estimated at a minimum of three inactivity thresholds with results reported."},
    {"id": "S2", "priority": "should_fix", "reviewer": "R1", "sub_claims": ["SC-14"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.3 'students were split at the median number of dashboard sessions'", "verification_criteria": "Primary analyses use the continuous predictor; any median-split result is secondary and labelled as such."},
    {"id": "S3", "priority": "should_fix", "reviewer": "R1", "sub_claims": ["SC-15"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §4 — expected effect sizes with confidence intervals and a power justification", "verification_criteria": "Standardised effect size with confidence interval reported for every comparison; a priori power justification stated."},
    {"id": "S4", "priority": "should_fix", "reviewer": "R1,R2", "sub_claims": ["SC-17", "SC-6"], "severity": "major", "confidence": 4, "evidence_anchor": "text: §3.3 'single-item overall ratings are common in dashboard studies to limit survey burden'", "verification_criteria": "Reliability/validity evidence supplied or a validated multi-item instrument used; item non-response reported as a rate."},
    {"id": "S5", "priority": "should_fix", "reviewer": "R1", "sub_claims": ["SC-18"], "severity": "minor", "confidence": 5, "evidence_anchor": "table: Table 1, row 'Final exam score (0-100)'", "verification_criteria": "Final exam score defined in Measures with its scoring basis and its dependence on the retention coding stated."},
    {"id": "S6", "priority": "should_fix", "reviewer": "R1,EIC", "sub_claims": ["SC-7"], "severity": "minor", "confidence": 5, "evidence_anchor": "absence: §3.4 and end matter — expected named software with version, code, and a data availability statement", "verification_criteria": "Software and version named; analysis code supplied; data-availability statement present.", "severity_source": "letter-fallback for EIC position", "confidence_source": "unavailable for EIC position"},
    {"id": "S7", "priority": "should_fix", "reviewer": "R3", "sub_claims": ["SC-34"], "severity": "major", "confidence": 4, "evidence_anchor": "text: §6 'encouraging students to engage with them is a dependable strategy'", "verification_criteria": "Manuscript states that an exhortation-driven session count carries no demonstrated relationship to persistence, wherever a practice recommendation appears."},
    {"id": "S8", "priority": "nice_to_fix", "reviewer": "R3", "sub_claims": ["SC-35"], "severity": "minor", "confidence": 4, "evidence_anchor": "absence: §6 — expected cost, staffing and advising-capacity requirements, and comparison against alternative retention interventions", "verification_criteria": "Cost, staffing, and comparative-intervention content supplied, or the practitioner address withdrawn."},
    {"id": "S9", "priority": "nice_to_fix", "reviewer": "R2", "sub_claims": ["SC-31"], "severity": "minor", "confidence": 4, "evidence_anchor": "text: §3.3 'single-item overall ratings are common in dashboard studies to limit survey burden'", "verification_criteria": "Claim carries a citation or is deleted."},
    {"id": "S10", "priority": "nice_to_fix", "reviewer": "EIC", "sub_claims": ["SC-5", "SC-37"], "severity": "minor", "confidence": 4, "evidence_anchor": "text: §4.1 'the reported secondary-item values were N=10; M=3.00; sample SD=0.10; integer scale=1-5'", "verification_criteria": "Orphan subsample removed or connected to a research question; run-in numeric list replaced by prose or a table; decimal precision consistent across Table 1 and Section 4."},
    {"id": "S11", "priority": "nice_to_fix", "reviewer": "DA", "sub_claims": [], "source_kind": "editorial", "verification_criteria": "§3.1 'disciplinary breadth' no longer converted to §6 'across programs and disciplines'; Abstract does not imply survey coverage of all 142 students; reporting precision consistent throughout."}
  ]
}
```

---

## Part 3: Reviewer Report Summary (Appendix)

### Journal-Fit Review Report Summary (eic)
- Dimensions: D5 `block`, D6 `block` (repairable, fatal trigger explicitly not stretched) | Report-level recommendation and confidence: not stated
- Key Point: a careful reader cannot state what this study found — the Abstract's headline r does not exist in Section 4, the sampling frame is described two incompatible ways, and the contribution is never positioned against any synthesis; the ethics omission and the Abstract/Results discrepancy are routed to the panel as gate items rather than absorbed into a fit-level judgement.

### Reviewer 1 (Methodology) Summary
- Dimensions: D1 `block` (**fatal**), D3 `block` (repairable) | Report-level recommendation and confidence: not stated
- Key Point: three reported quantities reconcile and the rest do not; the reported statistics correspond to at least three incompatible sample sizes and two impossible descriptives, and independently of the arithmetic the exposure window is truncated by the outcome in a survivorship-filtered sample, so recovering the stated estimand requires a different study.

### Reviewer 2 (Domain) Summary
- Dimensions: D2 `block` (repairable) | Report-level recommendation and confidence: not stated
- Key Point: this is a scholarship problem rather than a writing problem — one load-bearing citation is credited with the reverse of its own finding, "retention" is the persistence literature's term for something this design did not measure, and the SRL framework does no work the data could have contradicted.

### Reviewer 3 (Perspective — ethics and data governance) Summary
- Dimensions: D4 `block` | Report-level recommendation and confidence: not stated | Card hygiene: self-withdrawn dissent heading, no `block_class`
- Key Point: the study analysed behavioural logs outside the disclosed consent scope with no ethics documentation of any kind, and then recommends institution-wide deployment of a peer-comparison dashboard whose documented harm mechanism the paper itself describes and never tests for.

### Devil's Advocate Summary
- Dimensions: D3 `block` (repairable) | 7 CRITICAL, 9 MAJOR
- Key Point: steelmanned, the paper is a modest association with a mechanism-consistent correlate and would be publishable in some form; as submitted it argues for something its data cannot reach, and the central quantity contradicts itself. All seven CRITICAL findings were adjudicated VALIDATED; the one remedy divergence (C2) was resolved against the DA on the evidence of §3.2's respondent-only log extraction.
