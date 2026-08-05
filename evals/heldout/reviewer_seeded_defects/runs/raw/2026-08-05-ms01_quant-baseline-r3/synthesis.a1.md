# Editorial Decision Package

**Contract**: `reviewer/reviewer_full/v2` · mode `reviewer_full` · stage `reviewer_full_review` · baseline `v3.20.0` · `panel_size: 5`
**Cards received**: 5 of 5 (`eic`, `methodology`, `domain`, `perspective`, `da`) — no `[PANEL-SHRUNK]`.
**Reviewer label mapping used below**: `EIC` = Journal-Fit Reviewer · `MTH` = Peer Reviewer 1 (methodology) · `DOM` = Peer Reviewer 2 (domain) · `PSP` = Peer Reviewer 3 (perspective) · `DA` = Devil's Advocate. Roadmap item IDs are `R<n>`/`S<n>`; reviewer labels are alphabetic, so the two namespaces do not collide.

---

## Part 0: Sprint Contract Audit (mechanical)

### Step 1 — Role-scoped scoring matrix

Only assessed scores from seats whose `contract_role` appears in the dimension's `eligible_roles` are admitted. Every `not_assessed` from an ineligible seat is excluded from numerator and denominator. No dimension is unassessed, so no `[DIMENSION-UNASSESSED]` abort.

| Dim | Priority | `eligible_roles` | Assessed eligible seats | Scores | Fatality declared | Verdict (worst assessed eligible) |
|---|---|---|---|---|---|---|
| D1 methodology_rigor | mandatory | methodology | MTH | block | **yes** (`block_class: fatal`) | **block(fatal)** |
| D2 domain_accuracy | mandatory | domain | DOM | block | no (`repairable`) | block |
| D3 argumentative_coherence | mandatory | da, methodology | DA, MTH | block, block | no (both `repairable`) | block |
| D4 cross_disciplinary_relevance | high | perspective | PSP | block | no (`block_class` absent → read as non-fatal, not inferred) | block |
| D5 writing_and_structure | normal | eic | EIC | block | no (`block_class` absent → non-fatal) | block |
| D6 venue_fit_and_contribution | mandatory | eic | EIC | block | no (`repairable`) | block |

`dimension_verdicts: [D1=block(fatal), D2=block, D3=block, D4=block, D5=block, D6=block]`

### Step 2 — Failure-condition evaluation

| ID | Sev | Cross-reviewer quantifier | Expression (parsed pattern) | Per-dimension evaluation | Fired |
|---|---|---|---|---|---|
| F1 | 95 | any | `any <priority> dimension has a fatal block` (fatal scope on mandatory — valid) | D1 **true** (MTH fatal); D2/D3/D6 false | **true** |
| F2 | 90 | any | `any <priority> dimension scores '<score>'` | D1 true; D2, D3, D6 also true | **true** |
| F3 | 70 | majority | `two or more dimensions with priority=mandatory score 'warn' or worse` | D1 (n=1→owner) true; D2 (n=1) true; D3 (n=2→both) true; D6 (n=1) true → 4 ≥ 2 | **true** |
| F4 | 60 | any | `any <priority>-priority dimension scores 'block'` | D4 true | **true** |
| F5 | 40 | any | `any dimension scores 'warn' or worse` | D1–D6 all true | **true** |
| F0 | 10 | all | `every dimension scores 'pass'` | D1 false at first test | false |

`fired_conditions: [F1, F2, F3, F4, F5]`

### Step 3 — Precedence, decision, audit emission

Highest severity among fired conditions is F1 (95) → its `action` is applied verbatim, unsoftened.

`da_critical_adjudications: [C1=VALIDATED, C2=VALIDATED, C3=VALIDATED, C4=VALIDATED]`

`editorial_decision=reject`

No `[DA-CRITICAL-VS-ACCEPT]` marker: the mechanical decision is `reject`, not `accept`.

### Advisory flags (not abort conditions)

- **`[MEASUREMENT-ARTIFACT-NOT-FORWARDED]`** — `measurement_procedure.reviewer_must_output_before_paper` requires `contract_paraphrase` and `scoring_plan` with `paraphrase_minimum_dimensions: all`. None of the five forwarded cards carries either artifact as a discrete block. Each card quotes a per-dimension `trigger` string and the MTH card refers to "what my scoring plan named as fatal for D1", so the plans evidently existed upstream, but I cannot verify compliance from what was forwarded. Flagged, not repaired — Phase 1 card content is outside my write scope.
- **`[CROSS-MODEL: not run]`** — `ARS_CROSS_MODEL` not set; no consent gate passed. Step 4b skipped, no behavioural change.

---

## Part 1: Editorial Decision Letter

### Review Panel Provenance (#540)

**`[PROVENANCE-STAMP-NOT-SUPPLIED]`** — this submission ran in `reviewer_full`, so this block is mandatory and must carry exactly one of the three provenance statements (cross-model slot active / single-family disclosure / dispatch-failure fallback) from the dispatching layer's stamp. No stamp was included in my input. I will not infer which statement applies, and I compute no cross-family aggregate. **The dispatching layer must fill this block before the letter ships**; as it stands, a reader cannot determine which seat ran on which model family, and nothing here should be read as implying model independence.

---

Dear Author(s),

Thank you for submitting *"Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment."* The manuscript was assessed by five reviewers — a Journal-Fit Reviewer, three peer reviewers (methodology; higher-education persistence and literature; learning-analytics ethics, governance and institutional decision-use), and a Devil's Advocate seat.

### Decision: Reject

This decision is mechanical under the review contract. One reviewer declared a **fatal block on a mandatory dimension** (D1, methodology rigour), which fires the contract's highest-severity failure condition and its stated action. I record two things plainly rather than smoothing them over. First, I have no authority to soften that action, and I am not doing so. Second, the reviewers themselves do not think the underlying study is worthless: three of the four blocks were classified `repairable`, the methodology seat describes "the correlational paper underneath" as publishable, and every seat identified real strengths in your operationalisation and measurement candour. What follows is therefore a reject with a resubmission roadmap, not a reject with a dismissal.

### Consensus Analysis

Consensus is computed over the **four non-DA seats** (EIC, MTH, DOM, PSP). Silence is silence: a seat that did not speak to a sub-claim is neither agreeing nor dissenting, and several silences here are *explicit deferrals* recorded in the cards (DOM and PSP both formally deferred the statistical arithmetic to MTH; MTH and EIC did not enter the source-fidelity territory). Where a seat deferred, the low agreement count understates the finding's weight, and I say so in each row rather than letting the count speak alone.

Compound weaknesses were decomposed into atomic sub-claims before counting, so that a bundle whose parts reached different support levels produces separately prioritised roadmap items instead of one blurred item. The inventory below compacts the per-`(sub_claim, reviewer)` rows into one row per sub-claim; every reviewer position, transported severity, and transported confidence is retained.

#### Sub-claim inventory and dispositions

| SC | Sub-claim (parent weakness) | Positions — seat: position (severity, confidence) | agree/conflict/silent | Disposition |
|---|---|---|---|---|
| SC-1 | Abstract *r* = .42 vs Results *r* = .24 | EIC: raised (Critical, 5) · MTH: raised (Critical, 5) · DOM: raised (Major, 5) · PSP: raised (Major, 5) · DA C2 | 4/0/0 | **[CONSENSUS-4]** |
| SC-2 | Abstract implies survey from all 142; §4.1 reports 87 responders | EIC: raised (Critical, 5) · others: not-mentioned | 1/0/3 | single-reviewer |
| SC-3 | Abstract claims "self-regulated learning behavior" measured; only a single perceived-control item exists | DA: M10 (Major, 5) · all four non-DA: not-mentioned | 0/0/4 | DA-MAJOR (action-bearing, no consensus label) |
| SC-4 | *t*(156) exceeds any described sample | EIC: raised (Major, 4) · MTH: raised (Critical, 5) · DOM: not-mentioned (explicit deferral) · PSP: not-mentioned (explicit deferral) · DA C4 | 2/0/2 | corroborated (D1 owner seat, conf 5) |
| SC-5 | *t*(140) = 1.31 with *p* = .008 is impossible | EIC: raised (Major, 4) · MTH: raised (Major, 5) · DOM: raised (unscored body observation) `[SEVERITY-SOURCE: letter-fallback]` `[CONFIDENCE-SOURCE: unstated]` · PSP: not-mentioned (deferral) · DA M3 | 3/0/1 | **[CONSENSUS-3]** (PSP silent by deferral) |
| SC-6 | Table 2 *n* = 66 + 61 = 127 vs 142 classified | EIC: raised (Major, 5) · MTH: raised (Major, 5) · DOM/PSP: not-mentioned | 2/0/2 | corroborated |
| SC-7 | Perceived-control *M* = 3.847 unattainable on an integer item at *N* = 87 | MTH: raised (Major, 5) · others: not-mentioned | 1/0/3 | single-reviewer (D1 owner, conf 5) |
| SC-8 | Clarity item *N* = 10, *M* = 3.00, *SD* = 0.10 impossible | MTH: raised (Major, 5) · EIC: **disputed on severity** (Minor, 4) · DOM: raised (body observation) · DA M4 | 3/1/0 | **[SPLIT]** — arbitrated below |
| SC-9 | Decimal precision inconsistent (3 dp *M* vs 2 dp *SD*) | EIC: raised (Minor, 4) · MTH: raised (body) | 2/0/2 | corroborated (Minor) |
| SC-10 | Causal/effectiveness verbs in §5–§6 contradict the cross-sectional design and §1's own commitment | EIC: raised (Critical, 5) · MTH: raised (Major, 5) · DOM: raised (Major, 4) · PSP: raised (Major, 4) · DA C1 | 4/0/0 | **[CONSENSUS-4]** |
| SC-11 | §6 generalises to institutions "worldwide" and "across programs and disciplines" | EIC: raised (Critical, 5) · MTH: raised (Major, 5) · DOM: raised (Critical, 5) · PSP: raised (Critical, 5) · DA M5 | 4/0/0 | **[CONSENSUS-4]** |
| SC-12 | §5.1 omits the threats that actually govern interpretation | MTH: raised (Major, 5) · PSP: raised (Major, 5) · DA C3/M7 · EIC/DOM: not-mentioned | 2/0/2 | corroborated |
| SC-13 | Ferro & Nakamura (2021) cited against its own listed title; equity warrant inverted | DOM: raised (Critical, 5) · PSP: raised (Major, 4) · DA M2 · EIC/MTH: not-mentioned | 2/0/2 | corroborated (D2 owner seat, Critical) |
| SC-14 | "Retention" measured as one course's completion, discussed as institutional persistence | DOM: raised (Critical, 5) · others: not-mentioned | 1/0/3 | single-reviewer (D2 owner, conf 5) |
| SC-15 | Perceived control called a "mediating construct" with no mediation analysis | DOM: raised (Major, 4) · DA M6 (5) · others: not-mentioned | 1/0/3 | single-reviewer + DA |
| SC-16 | SRL framework carries the argument but is never sourced; phase vocabulary inconsistent | DOM: raised (Major, 4) · others: not-mentioned | 1/0/3 | single-reviewer |
| SC-17 | "Who benefits" positioning unearned — no subgroup analysis by prior achievement | DOM: raised (Major, 4) · PSP: raised (Major, 5) · EIC/MTH: not-mentioned | 2/0/2 | corroborated |
| SC-18 | Institution-wide recommendation carries no equity safeguard despite a deployed peer-comparison band | PSP: raised (Major, 5) · others: not-mentioned | 1/0/3 | single-reviewer (governance seat, conf 5) |
| SC-19 | Log data analysed without informing students; no ethics-approval statement | PSP: raised (Critical, 5) · EIC: raised (Major, 4, with explicit escalation clause) · MTH: raised (Major, 3) · DOM: not-mentioned · DA M8 (4) | 3/0/1 | **[CONSENSUS-3]** |
| SC-20 | No lawful basis, retention, de-identification, or log-to-survey linkage protocol | PSP: raised (Major, 5) · EIC: raised (body, "no protocol reference") | 2/0/2 | corroborated |
| SC-21 | Sampling described as random *and* as voluntary response; no computable response rate | MTH: raised (Major, 5) · PSP: raised (Major, 4) · DA M1 · EIC/DOM: not-mentioned | 2/0/2 | corroborated |
| SC-22 | Mid-term recruitment truncates the retention outcome; estimand not identified | MTH: raised (Critical, 5) · others: not-mentioned | 1/0/3 | single-reviewer (D1 owner, Critical, 5) |
| SC-23 | Exposure-time confound: withdrawers have fewer weeks to accumulate sessions | DA: C3 (Critical, 4) · non-DA: not-mentioned | 0/0/4 | DA-CRITICAL → adjudicated below |
| SC-24 | Pearson used for a count-by-binary association; skew undermines the normality basis | MTH: raised (Major, 5) · DA M11 (4) · PSP: not-mentioned (deferral) | 1/0/3 | single-reviewer (D1 owner) |
| SC-25 | No covariate adjustment for prior attainment or baseline LMS activity | MTH: raised (Major, 5) · DA M7 (5) | 1/0/3 | single-reviewer + DA |
| SC-26 | Median split discards the continuous predictor | MTH: raised (Major, 5) · EIC/DOM: strength-noted **on the disclosure only** | 1/0/3 | single-reviewer — **not** a conflict (see arbitration note 3) |
| SC-27 | No effect sizes, no confidence intervals, no retention base rate | MTH: raised (Major, 5) · DA M9 (5) | 1/0/3 | single-reviewer + DA |
| SC-28 | ~39% item nonresponse on perceived control never characterised | MTH: raised (Major, 4) | 1/0/3 | single-reviewer |
| SC-29 | Reproducibility affordances absent (software/version, data, code, preregistration) | MTH: raised (Minor, 5) · EIC: raised (Minor, 5, data availability element) | 2/0/2 | corroborated (Minor) |
| SC-30 | Single-item construct measure with no validity/reliability evidence | MTH: raised (Minor, 4) · DOM: raised (within W3, Major) | 2/0/2 | corroborated |
| SC-31 | Nine listed references are never cited | EIC: raised (Minor, 5, states "of sixteen") · DOM: raised (Minor, 4, states "of fifteen") | 2/0/2 | corroborated — count arbitrated below |
| SC-32 | Final exam score analysed and tabled but never defined as a measure | EIC: raised (Minor, 4) | 1/0/3 | single-reviewer |
| SC-33 | No data-availability, funding, or conflict-of-interest declarations | EIC: raised (Minor, 5) · MTH: raised (Minor, 5, partial) | 2/0/2 | corroborated (Minor) |
| SC-34 | No positioning against the synthesis literature on dashboard effects | EIC: raised (Major, 4) · DOM: **disputed on severity** (Minor, 4) | 1/1/2 | **[SPLIT]** — arbitrated below |
| SC-35 | Recommendation not actionable — no cost, comparator, or implementation conditions | PSP: raised (Major, 4) | 1/0/3 | single-reviewer |
| SC-36 | All 15 references carry the reserved `10.5555` test DOI prefix | DOM: raised (body, explicitly unscored, flagged for editorial verification) | 1/0/3 | single-reviewer — editorial verification gate |
| SC-37 | Naming Meridian State University may breach venue anonymity policy | EIC: raised (body) | 1/0/3 | single-reviewer (administrative) |

#### Points of agreement (consensus)

- **[CONSENSUS-4]** The Abstract's headline correlation (*r* = .42) contradicts the Results (*r* = .24), and the two cannot both be the analysis (SC-1).
- **[CONSENSUS-4]** §5 and §6 state the association in causal and effectiveness terms that a cross-sectional observational design cannot license — and that §1 and §2 of this same manuscript explicitly disclaim (SC-10).
- **[CONSENSUS-4]** §6's recommendation to "higher education institutions worldwide," "across programs and disciplines," on the basis of one volunteer sample in one course section, is unsupported in full (SC-11).
- **[CONSENSUS-3]** *t*(140) = 1.31 cannot yield *p* = .008 (SC-5; PSP silent by explicit deferral to the methodology seat).
- **[CONSENSUS-3]** Behavioural log data were analysed without informing students and no ethics-approval statement appears anywhere in the manuscript (SC-19; DOM silent).

#### Points of disagreement, and the editor's resolutions

**1. SC-8 — severity of the impossible clarity-item statistics.** MTH scores the *N* = 10, *M* = 3.00, *SD* = 0.10 triplet Major (conf 5): the value is arithmetically unobtainable. EIC scores the same triplet Minor (conf 4) on the ground that no core claim depends on the item.

> **Editor's resolution: Major, remediated at Priority 1 alongside the other arithmetic impossibilities — with removal of the item accepted as a sufficient remedy.** Rationale is expertise-first and evidence-first. Statistical reporting integrity sits in D1, whose `eligible_roles` is `[methodology]`; the seat holding that territory rates it Major at confidence 5. I also verified the arithmetic independently rather than relaying it: ten integers on a 1–5 scale with mean exactly 3.00 sum to 30, so the sample *SD* is either 0 (all responses 3) or at least √(2/9) ≈ 0.47. There is no set of responses that produces 0.10. Note that EIC does not dispute the impossibility — only its weight — and EIC's own proposed remedy ("either proper reporting or removal") satisfies MTH's requirement. The two seats are therefore compatible on action and split only on band; the higher band governs, and both remedies remain open to you.

**2. SC-34 — severity of the missing synthesis-literature positioning.** EIC scores the absence of any review or meta-analysis of dashboard effects Major (conf 4), because it is load-bearing for the contribution-increment question. DOM rates the same absence Minor (conf 4), bundled into general citation hygiene.

> **Editor's resolution: Major, Priority 1.** D6 (venue fit and contribution) is eligible only to the `eic` seat, and the question "what does one more single-course *r* ≈ .24 add to a synthesis baseline that already says small, heterogeneous, design-dependent?" is precisely that seat's territory. DOM's Minor rating attaches to citation hygiene as a class — where it is correct and is honoured separately at Priority 3 (S9) — not to the contribution argument. This is not an averaging of the two bands; it is an allocation of the sub-claim to the dimension that owns it.

**3. SC-26 — apparent conflict on the median split (resolved as no conflict).** EIC and DOM both list the median split among the manuscript's *strengths*, while MTH scores it as a defect. This is not a disagreement and I decline to arbitrate it as one: EIC and DOM praise the **disclosure** of the simplification at the point of use (§3.3, "a coarse simplification of a continuous measure"), whereas MTH criticises the **analytic choice** itself. Both are correct simultaneously. Candour about a suboptimal choice does not convert it into a good one, and a naive reading that scored this as a split would have manufactured a dispute that no reviewer made.

**4. SC-31 — the reference count.** EIC reports "nine of sixteen references" uncited; DOM reports "nine of fifteen." Arbitrated on direct evidence: the reference list contains fifteen entries, six of which are cited in text. **DOM's count is correct**; the roadmap uses nine of fifteen. This is a slip in one card, recorded here only so the corrected figure travels forward.

**5. The predicted MTH-vs-PSP tension on *what to do with the paper*.** MTH's logic points to "the design cannot answer the question"; PSP's points to "the ethics disclosure may bar publication regardless of design." I do not average these and I do not rank one over the other. They are **sequential, independently sufficient gates**: even a fully corrected and re-specified analysis remains unpublishable if the log-based analyses were conducted without a documented basis, and a fully documented ethics record does not repair an unauditable results section. Both appear in the roadmap as Priority 1, and neither is contingent on the other.

**6. The predicted EIC-vs-DOM tension on novelty (preserved, not resolved).** EIC finds the contribution too thin against the existing review literature as currently framed; DOM identifies a salvageable descriptive study if the outcome is honestly renamed to course completion. These are not in conflict, and I am leaving both on the record deliberately: EIC's D6 block is scored `repairable` precisely because a defensible contribution exists underneath, and DOM's route to it — rename the construct, reposition against the course-completion literature — is the same route EIC describes as "a legitimate if modest brick." Read together they define the resubmission you can actually write. What neither seat supports is the paper as submitted.

#### Devil's Advocate CRITICAL adjudications

Every DA CRITICAL finding appears here exactly once, with corroboration status and my assessment of validity. Adjudication is visibility, not veto.

| ID | DA claim | Corroborated by | Editor's adjudication |
|---|---|---|---|
| **C1** | Causal/effectiveness conclusions from an explicitly cross-sectional design, contradicting the manuscript's own stated commitment | EIC W2, MTH W17, DOM W7, PSP W4 — all four non-DA seats | **VALIDATED.** Unanimous, and independently checkable on the page: §3.1 states the design is observational and cross-sectional; §5 states engagement "improved" retention and "raises the probability" of completion. Roadmap R3. |
| **C2** | Headline association reported as *r* = .42 (Abstract) and *r* = .24 (Results) | EIC W1, MTH W1, DOM W6, PSP W8 | **VALIDATED.** I reconciled this myself rather than relaying it: at *n* = 142, *r* = .24 implies *t* ≈ 2.93 (*p* ≈ .004) and *r* = .42 implies *t* ≈ 5.47 (*p* < .001). The printed *p* = .004 is consistent with .24 and not with .42. Roadmap R1. |
| **C3** | Exposure-time confound: withdrawn students necessarily had fewer weeks to accumulate sessions, so part of *r* = .24 is definitional | No non-DA seat raised this specific mechanism | **VALIDATED, with scope stated.** The mechanism is real and the manuscript never raises it (absent from §3.3, §3.4, §5.1). Two scope qualifications belong on the record and neither defeats it: it bites on students who *withdrew*, not on the "enrolled but did not sit the final" group, who had full-term exposure and are also coded not-retained; and because recruitment was mid-term, the differential-exposure window is bounded by the post-recruitment weeks. Its magnitude is unquantifiable from the reported record, since no retention base rate and no withdrawal timing are reported (SC-27). It is **distinct from**, not redundant with, MTH W3 — W3 concerns who could enter the sample, C3 concerns how the predictor accumulates within it. Roadmap R10. |
| **C4** | *t*(156) = 3.02 on an item answered by 87 respondents within a 142-student sample | EIC W5, MTH W2 | **VALIDATED.** An independent-samples test on 87 cases admits at most *df* = 85; the full analytic sample caps *df* at 140. No described subset yields 156. Roadmap R2. |

### Decision Rationale

The decision is `reject`, fired by a fatal block on mandatory dimension D1. I have not softened that action and could not: the contract's precedence rule selects the highest-severity fired condition, and the fatality was declared by the only seat eligible to score statistical rigour.

The substance behind the mechanics is that this manuscript's results section cannot currently be audited from its own text. Five reported quantities are not merely questionable but unobtainable from the described samples — I verified each independently: *r* = .42 against a printed *p* that matches .24; *df* = 156 where no sample exceeds 140; *t* = 1.31 paired with *p* = .008 where the *t*-distribution gives *p* ≈ .19; Table 2 subgroups summing to 127 against 142 classified students; and two survey means (3.847 at *N* = 87; *SD* = 0.10 at *N* = 10, *M* = 3.00) that no integer responses can produce. Until a reader can tell which numbers the study found, the interpretive critiques cannot be weighted, because some of them target results that will not survive correction.

Three further gates are independently sufficient. The manuscript asserts causation and worldwide generalisability that its own Introduction disclaims and its own cited audit warns against — unanimous across all four non-DA seats. It analyses student behavioural traces without notice and without any approval statement, which the governance seat rates as precluding acceptance at any venue with an ethics requirement, and which the Journal-Fit seat rates Major only on the express assumption that documentation exists off-page. And it cites Ferro & Nakamura (2021) for the reverse of what that source's own listed title reports, with the equity rationale for institutional deployment resting on the inversion.

Two things this decision does not say. It does not say the study is without merit: the sessionisation rule, the retention coding of the enrolled-but-absent case, the self-implicating measurement critique in §2, and the disclosure of the median split are genuine and were named as strengths by multiple seats. And it does not say the path forward is cosmetic. Three of the four blocks are `repairable`; the honest version of this paper — a single-site, single-course, volunteer-sample descriptive association between dashboard sessions and *course completion*, positioned against the synthesis literature, with a documented ethics basis and no deployment prescription — is a narrower paper than the one submitted and a publishable one. That paper requires a re-analysis and a rewritten claim set, which is a new submission rather than a revision.

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| 1 | The results record contains at least five quantities unobtainable from the described samples, so no reported finding can be audited from the text. This is the fatal block that fires the decision. | MTH (Critical/fatal, 5); EIC (Major, 4); DA C2, C4, M3, M4 | text: §4.3 "t(156) = 3.02, p = .003" and "t(140) = 1.31, p = .008"; table: Table 2 subgroup *n* 66 + 61 = 127 against §4.3's 142 | R2 |
| 2 | Behavioural trace data analysed without participant notice, with no ethics approval, lawful basis, waiver rationale, or log-to-survey linkage protocol disclosed. Potentially not curable by rewriting: absent approval, the log-based analyses — which produce the headline result — must be withdrawn. | PSP (Critical, 5); EIC (Major, 4, with escalation clause); MTH (Major, 3); DA M8 | text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study." | R5 |
| 3 | Causal and effectiveness claims plus worldwide, cross-programme generalisation — the manuscript's advertised contribution — contradicted by its own design statement, its own Introduction, and its own cited audit. | All four non-DA seats + DA C1, M5 | text: §5, §6 "dashboard engagement improved course retention"; "is a dependable strategy for improving retention across programs and disciplines" | R3, R4 |

> **A fourth gating condition is excluded only by this section's 0–3 cap** and must not be read as secondary: the D2 (domain accuracy) block rests on two Critical findings from the seat that owns that dimension — the Ferro & Nakamura inversion (R6) and the silent substitution of one course's completion for institutional persistence (R7). Both are unconditional and both must be resolved before resubmission.

---

## Part 2: Revision Roadmap

> **Framing.** The decision is Reject, so this is a **resubmission roadmap**: these are the conditions under which the material could return as a new submission, not a revise-and-resubmit invitation. The format is unchanged so that it drops directly into `academic-paper` revision mode.
>
> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to. Items with no sub-claim id use `—`. Severity, Evidence Anchor, and Confidence are **transported** from the reviewer cards, never re-derived; fallback tags travel with the row.

### Required Revisions (Must Fix)

> **Ordinal contract:** the `### Required Item Details` blocks below are numbered `R1..R13` in exactly this table's order.

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| R1 | Make every quantity and construct in the Abstract match Methods and Results — the correlation, the survey *N*, and the claim to have measured self-regulated learning behaviour | SC-1, SC-2, SC-3 | Critical | text: §Abstract, §4.2 "Dashboard engagement correlated positively with retention (r = .42)" vs "(r = .24, p = .004)" | 5 | EIC, MTH, DOM, PSP, DA | P1 | 1 day (after R2) |
| R2 | Reconcile or withdraw every remaining reported statistic and tabled *n* against a stated denominator | SC-4, SC-5, SC-6, SC-7, SC-8, SC-9 | Critical (fatal-declared on D1) | text: §4.3 "t(156) = 3.02, p = .003"; "t(140) = 1.31, p = .008"; table: Table 2 *n* 66 + 61 = 127 | 5 | MTH (owner), EIC, DOM, DA | P1 | 2–3 weeks |
| R3 | Remove all causal and effectiveness language; restate every outcome claim as associational across Abstract, §5, §6, and add explicit treatment of reverse-direction and common-cause explanations | SC-10 | Critical | text: §5, §6 "dashboard engagement improved course retention"; "raises the probability that a student completes the course" | 5 | EIC, MTH, DOM, PSP, DA C1 | P1 | 3–5 days |
| R4 | Delete the worldwide/cross-programme deployment recommendation and restate the contribution as a single-site, single-course, single-interface, volunteer-sample association | SC-11, SC-35 | Critical | text: §6 "For higher education institutions worldwide, the implication is clear"; "a dependable strategy for improving retention across programs and disciplines" | 5 | PSP, EIC, DOM, MTH, DA M5 | P1 | 3–5 days |
| R5 | Supply the ethics record — approval, lawful basis, any notification-waiver rationale, retention, de-identification, log-to-survey linkage, debriefing — or withdraw all log-based analyses | SC-19, SC-20 | Critical (PSP) / Major with escalation clause (EIC) | text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study." | 5 | PSP (owner territory), EIC, MTH, DA M8 | P1 | 1 day if documented; otherwise indeterminate |
| R6 | Verify and correct the Ferro & Nakamura (2021) attribution and rebuild every claim that depended on it, in §2 and in §5's who-benefits positioning | SC-13 | Critical | text: §2 "Dashboards have been shown to reliably improve outcomes for lower-achieving students"; References "When dashboards demotivate: Peer comparison and the lower-achieving student" | 5 | DOM (owner), PSP, DA M2 | P1 | 3–5 days |
| R7 | Rename the outcome to course completion throughout, or measure institutional persistence; restate the contribution against the course-completion literature | SC-14 | Critical | text: §3.3 "Course retention was coded dichotomously as whether the student remained enrolled and completed the final assessment"; §6 "improving retention across programs and disciplines" | 5 | DOM (owner) | P1 | 1 week |
| R8 | Re-specify the primary analysis: label the coefficient correctly, model the binary outcome appropriately, retain the continuous predictor, adjust for prior attainment and baseline LMS activity, and report an interval | SC-24, SC-25, SC-26 | Major | text: §3.4 "Associations between continuous measures were assessed with Pearson correlations." | 5 | MTH (owner), DA M7, M11 | P1 | 2 weeks |
| R9 | State the recruitment procedure once and accurately, report the response rate against the enrolled denominator, and compare respondents with non-respondents | SC-21 | Major | text: §3.2 "using a random sample of students enrolled in the course section" and "Students who chose to respond… formed the study sample" | 5 | MTH, PSP, DA M1 | P1 | 1 week |
| R10 | Address both identification threats in analysis and in Limitations: mid-term recruitment truncating the retention outcome, and exposure-time confounding of cumulative session counts | SC-22, SC-23, SC-12 | Critical | text: §3.2 "Midway through the term, an announcement was posted to the course LMS"; absence: §5.1 — expected treatment of exposure-time confounding; checked §3.3, §3.4, §4.2, §5, §5.1, §6 | 5 (MTH) / 4 (DA C3) | MTH (owner), DA C3, PSP | P1 | 1–2 weeks |
| R11 | Position the contribution against the synthesis literature on student-facing dashboard effects, citing at least one systematic review or meta-analysis | SC-34 | Major (arbitrated — see disagreement 2) | absence: §2 and References — expected at least one systematic review or meta-analysis of student-facing dashboard effects on academic outcomes; checked §1, §2, §5, References | 4 | EIC (D6 owner) | P1 | 1 week |
| R12 | Either report differential-effect analyses by prior achievement, or withdraw the who-benefits claim and the unqualified engagement recommendation and state that the study cannot identify who is harmed | SC-17, SC-18 | Major | absence: §4 and §5 — expected subgroup or differential-effect analysis by prior achievement and goal orientation for a dashboard containing a peer-comparison band; checked Table 1, Table 2, §4.1–§4.3, §5, §5.1, §6 | 5 (PSP) / 4 (DOM) | PSP, DOM | P1 | 1 week (withdrawal route) |
| R13 | Verify every reference and its DOI: all fifteen entries carry the reserved `10.5555` test prefix, which resolves to no live record | SC-36 | Unscored by the raising seat — flagged for editorial verification `[SEVERITY-SOURCE: letter-fallback]` | text: References — all fifteen entries, e.g. "https://doi.org/10.5555/3040506" | Unstated `[CONFIDENCE-SOURCE: unstated]` | DOM (raised expressly as verification, not as a scored finding) | P1 | 1 day |

### Required Item Details

**R1 — Abstract fidelity**
- **Acceptance criteria**: The Abstract reports the same correlation value as §4.2, states the survey subsample size actually analysed rather than implying 142 respondents, and describes what was measured (a single perceived-control rating) rather than claiming self-regulated learning behaviour.

**R2 — Reporting-integrity reconciliation**
- **Acceptance criteria**: Every reported statistic is traceable to a stated denominator, with the perceived-control test's degrees of freedom consistent with its analysed *n*, the exam comparison's *t* and *p* mutually consistent and consistent with the surrounding narrative, Table 2's subgroup *n* summing to the sample the text says was classified, both survey means attainable from integer responses at their stated *N* (removal of the ten-student clarity item is an acceptable route), and decimal precision consistent within each row.

**R3 — Associational restatement**
- **Acceptance criteria**: No sentence in the Abstract, §5, or §6 asserts that dashboard engagement improved, raised, or caused retention, and §5 explicitly addresses the reverse-direction reading (that dashboard use marks students already likely to persist) and the common-cause reading (general course engagement).

**R4 — Scope restatement**
- **Acceptance criteria**: §6 contains no recommendation addressed to institutions beyond the study site, no characterisation of dashboard investment as dependable or generalisable, and states instead what evidence would be required before an institutional investment decision.

**R5 — Ethics record**
- **Acceptance criteria**: The Methods carry an ethics-approval statement with protocol identifier, the lawful basis for processing behavioural data collected for another purpose, the rationale for any notification waiver, the log-to-survey linkage and key-handling procedure, retention and de-identification arrangements, and any debriefing offered — or, if no approval covering log analysis exists, all log-based analyses are removed from the manuscript.

**R6 — Source-fidelity correction**
- **Acceptance criteria**: The characterisation of Ferro & Nakamura (2021) in §2 matches what that source reports, the sentence identifying it as underpinning the equity rationale is rewritten accordingly, and every §5 claim that inherited the inverted reading is revised or removed.

**R7 — Construct renaming**
- **Acceptance criteria**: The measured outcome is named course completion in the title, Abstract, Methods, Results, Discussion, and Conclusion, the term retention is used only where institutional persistence is genuinely at issue, and the contribution is stated against the course-completion literature rather than the persistence literature.

**R8 — Analysis re-specification**
- **Acceptance criteria**: The engagement–completion association is estimated with a model appropriate to a binary outcome, using the continuous session measure rather than the median split, adjusted for prior attainment and baseline LMS activity, reported with an interval, and the coefficient is labelled correctly wherever a correlation is retained.

**R9 — Recruitment description**
- **Acceptance criteria**: §3.2 describes one recruitment procedure without contradiction, reports the enrolled denominator and the resulting response rate, and compares respondents with non-respondents on the characteristics available in the log data.

**R10 — Identification threats**
- **Acceptance criteria**: The analysis addresses exposure duration explicitly (for example a rate measure or an analysis window closing before the earliest withdrawal), and §5.1 names both mid-term recruitment truncating the retention outcome and unmeasured confounding among its limitations.

**R11 — Contribution positioning**
- **Acceptance criteria**: §2 engages at least one systematic review or meta-analysis of student-facing dashboard effects on academic outcomes, and §1 or §5 states what this study's estimate adds to, refines, or falls below in that synthesis baseline.

**R12 — Differential-effect analysis or withdrawal**
- **Acceptance criteria**: Either the Results report an achievement-stratified or interaction analysis addressing who benefits and who may be harmed by the deployed peer-comparison band, or §5 and §6 withdraw the who-benefits positioning and state explicitly that the study cannot identify differential harm.

**R13 — Reference verification**
- **Acceptance criteria**: Every reference resolves to a verifiable record with a registrant DOI, and no entry retains the reserved `10.5555` test prefix.

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| S1 | Report the retention base rate and retained/not-retained counts, plus an effect size and confidence interval for every comparison | SC-27 | Major | absence: §4 — expected retention base rate, retained versus not-retained counts, and confidence intervals; checked Table 1, Table 2, §4.1–§4.3 | 5 | MTH, DA M9 | P2 | 3 days |
| S2 | Characterise the ~39% item nonresponse on perceived control and compare the 87 responders with the 142-student sample | SC-28 | Major | absence: §3.2 and §4.1 — expected a missing-data analysis comparing item responders with the analytic sample; checked §3.2, §3.3, §3.4, §4.1, §5.1 | 4 | MTH | P2 | 3 days |
| S3 | Remove the "mediating construct" language, or conduct an actual mediation analysis on an adequately instrumented measure | SC-15 | Major | text: §5 "It also complements accounts emphasizing perceived control as a mediating construct" | 4 | DOM, DA M6 | P2 | 1 day (removal route) |
| S4 | Ground the self-regulated learning framework in canonical sources and resolve the forethought/reflection phase inconsistency between §1 and §2 | SC-16 | Major | absence: §1 and §2 — expected citation to a canonical self-regulated learning source for the forethought/performance/reflection cycle; checked §1, §2, all in-text citations, and the reference list | 4 | DOM | P2 | 3 days |
| S5 | Define the final exam score as a measure in §3.3, including its relationship to the "final assessment" used to code the outcome | SC-32 | Minor | absence: §3.3 — expected an operational definition of the final exam score reported in Table 1; checked §3.1, §3.3, §3.4, Table 1 | 4 | EIC | P2 | 1 day |
| S6 | Add reproducibility affordances: named software with version, data and code availability, preregistration status | SC-29 | Minor | absence: §3.4 and end matter — expected named software with version, data and code availability, and preregistration status; checked §3.4, §4, §5.1, §6, References | 5 | MTH, EIC | P2 | 2 days |
| S7 | Provide psychometric support for the single-item perceived-control measure, or state the absence of validity evidence as a limitation | SC-30 | Minor (MTH) / Major within DOM W3 | text: §3.3 "Perceived control over learning was measured with a single-item overall rating" | 4 | MTH, DOM | P2 | 1 day |
| S8 | Cite the nine listed-but-uncited references where they are load-bearing, or remove them | SC-31 | Minor | absence: References versus in-text citations — expected an in-text citation for each listed reference; checked §1–§6 | 5 (EIC) / 4 (DOM) | EIC, DOM | P3 | 1 day |
| S9 | Add data availability, funding, and conflict-of-interest declarations | SC-33 | Minor | absence: front and back matter — expected data availability, funding, and conflict-of-interest declarations; checked Abstract, §3, §5.1, §6, References | 5 | EIC, MTH | P3 | 0.5 day |
| S10 | Report the secondary clarity item as prose or a table rather than as an inline semicolon-delimited string, or remove it | SC-8, SC-9 | Minor | text: §4.1 "the reported secondary-item values were N=10; M=3.00; sample SD=0.10; integer scale=1-5" | 4 | EIC | P3 | 0.5 day |
| S11 | Confirm that naming Meridian State University complies with the venue's review-anonymity policy | SC-37 | Unstated (raised in the EIC review body) `[SEVERITY-SOURCE: letter-fallback]` | text: §3.1 "at Meridian State University" | Unstated `[CONFIDENCE-SOURCE: unstated]` | EIC | P3 | 0.5 day |

### Revision Checklist

#### Priority 1 — Structural revisions (estimated total effort: 8–10 weeks, excluding any ethics remediation)
- [ ] R1: Correct the Abstract's correlation, survey *N*, and construct claim.
- [ ] R2: Reconcile or withdraw every impossible statistic and tabled *n*.
- [ ] R3: Strip causal and effectiveness language; add rival explanations.
- [ ] R4: Delete the worldwide deployment recommendation; restate scope.
- [ ] R5: Supply the full ethics record, or withdraw the log-based analyses.
- [ ] R6: Correct the Ferro & Nakamura attribution and rebuild dependent claims.
- [ ] R7: Rename the outcome to course completion; reposition the contribution.
- [ ] R8: Re-specify the primary analysis with an appropriate model and covariates.
- [ ] R9: State recruitment once; report the response rate; compare non-respondents.
- [ ] R10: Address survivorship truncation and exposure-time confounding.
- [ ] R11: Position against the synthesis literature.
- [ ] R12: Report differential effects, or withdraw the who-benefits claims.
- [ ] R13: Verify all references and DOIs.

#### Priority 2 — Content supplementation (estimated total effort: 2 weeks)
- [ ] S1: Base rate, effect sizes, confidence intervals.
- [ ] S2: Item-nonresponse characterisation.
- [ ] S3: Remove or test the mediation claim.
- [ ] S4: Ground and reconcile the SRL framework.
- [ ] S5: Define the final exam score.
- [ ] S6: Reproducibility affordances.
- [ ] S7: Single-item measure validity.

#### Priority 3 — Text and formatting (estimated total effort: 2–3 days)
- [ ] S8: Cite or remove the nine uncited references (nine of fifteen — see arbitration 4).
- [ ] S9: Data availability, funding, conflict-of-interest declarations.
- [ ] S10: Report or remove the secondary clarity item properly.
- [ ] S11: Confirm anonymity-policy compliance for the named institution.

### Resubmission Timeline

Because the decision is Reject, no revision deadline applies. Realistically, R2, R8, R9, and R10 require re-analysis on the underlying data rather than editing, so **8–12 weeks** is the honest floor before this material is ready to enter review anywhere. R5 is not schedulable: if approval covering log analysis exists, disclosure closes it in a day; if it does not, the log-based analyses cannot be published as described and the timeline question is moot.

If a redesign is not feasible, two seats independently identify a defensible landing: an honestly scoped single-course descriptive study of dashboard sessions and course completion, positioned against the synthesis literature, would suit *Australasian Journal of Educational Technology* or *Technology, Knowledge and Learning*. That paper is narrower than the one submitted, and it is real.

### Response Letter Template

Use `templates/revision_response_template.md` and respond to every numbered item (R1–R13, S1–S11) individually. Two items warrant a specific note. For R2, state for each corrected statistic which value was wrong and why, rather than silently replacing numbers — the reporting-integrity finding is what fired this decision, and a resubmission that presents corrected values without accounting for the originals will not clear it. For R5, attach the approval documentation rather than asserting that approval existed.

### Machine-form Roadmap (Schema 7)

```json
{
  "schema": 7,
  "contract_id": "reviewer/reviewer_full/v2",
  "editorial_decision": "reject",
  "items": [
    {"id": "R1",  "priority": "must_fix", "reviewer": "eic,methodology,domain,perspective,da", "verification_criteria": "Abstract reports the same correlation as §4.2, states the analysed survey subsample size, and describes a single perceived-control rating rather than self-regulated learning behaviour.", "severity": "critical", "evidence_anchor": "text: §Abstract, §4.2 'r = .42' vs 'r = .24, p = .004'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-1","SC-2","SC-3"]},
    {"id": "R2",  "priority": "must_fix", "reviewer": "methodology,eic,domain,da", "verification_criteria": "Every reported statistic traces to a stated denominator; df consistent with analysed n; t and p mutually consistent; Table 2 subgroup n sums to the classified sample; both survey means attainable from integer responses at their stated N; decimal precision consistent.", "severity": "critical", "evidence_anchor": "text: §4.3 't(156) = 3.02, p = .003'; 't(140) = 1.31, p = .008'; table: Table 2 n 66 + 61 = 127", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-4","SC-5","SC-6","SC-7","SC-8","SC-9"], "notes": "fatal block declared on D1 by the methodology seat"},
    {"id": "R3",  "priority": "must_fix", "reviewer": "eic,methodology,domain,perspective,da", "verification_criteria": "No causal or effectiveness assertion remains in Abstract, §5, §6; reverse-direction and common-cause explanations addressed explicitly.", "severity": "critical", "evidence_anchor": "text: §5, §6 'dashboard engagement improved course retention'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-10"]},
    {"id": "R4",  "priority": "must_fix", "reviewer": "perspective,eic,domain,methodology,da", "verification_criteria": "§6 contains no recommendation beyond the study site and no dependability or generalisability characterisation; states what evidence an investment decision would require.", "severity": "critical", "evidence_anchor": "text: §6 'a dependable strategy for improving retention across programs and disciplines'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-11","SC-35"]},
    {"id": "R5",  "priority": "must_fix", "reviewer": "perspective,eic,methodology,da", "verification_criteria": "Methods carry approval statement with protocol id, lawful basis, waiver rationale, log-to-survey linkage and key handling, retention and de-identification, debriefing; or all log-based analyses are removed.", "severity": "critical", "evidence_anchor": "text: §3.2 'Students were not informed that their dashboard activity data would be analyzed for this study.'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-19","SC-20"], "notes": "PSP Critical/5; EIC Major/4 with explicit escalation clause"},
    {"id": "R6",  "priority": "must_fix", "reviewer": "domain,perspective,da", "verification_criteria": "§2 characterisation of Ferro & Nakamura (2021) matches the source; the equity-rationale sentence is rewritten; every dependent §5 claim revised or removed.", "severity": "critical", "evidence_anchor": "text: §2 'reliably improve outcomes for lower-achieving students'; References 'When dashboards demotivate'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-13"]},
    {"id": "R7",  "priority": "must_fix", "reviewer": "domain", "verification_criteria": "Outcome named course completion throughout; retention used only for institutional persistence; contribution stated against the course-completion literature.", "severity": "critical", "evidence_anchor": "text: §3.3 retention coding; §6 'improving retention across programs and disciplines'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-14"]},
    {"id": "R8",  "priority": "must_fix", "reviewer": "methodology,da", "verification_criteria": "Binary-outcome model on the continuous session measure, adjusted for prior attainment and baseline LMS activity, reported with an interval; any retained correlation labelled correctly.", "severity": "major", "evidence_anchor": "text: §3.4 'Associations between continuous measures were assessed with Pearson correlations.'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-24","SC-25","SC-26"]},
    {"id": "R9",  "priority": "must_fix", "reviewer": "methodology,perspective,da", "verification_criteria": "§3.2 describes one recruitment procedure; enrolled denominator and response rate reported; respondents compared with non-respondents on available log characteristics.", "severity": "major", "evidence_anchor": "text: §3.2 'random sample' vs 'Students who chose to respond'", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-21"]},
    {"id": "R10", "priority": "must_fix", "reviewer": "methodology,da,perspective", "verification_criteria": "Analysis addresses exposure duration explicitly; §5.1 names mid-term recruitment truncation and unmeasured confounding.", "severity": "critical", "evidence_anchor": "text: §3.2 'Midway through the term, an announcement was posted'; absence: §5.1 exposure-time confounding", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-22","SC-23","SC-12"]},
    {"id": "R11", "priority": "must_fix", "reviewer": "eic", "verification_criteria": "§2 engages at least one systematic review or meta-analysis of dashboard effects; §1 or §5 states the increment over that baseline.", "severity": "major", "evidence_anchor": "absence: §2 and References — expected a systematic review or meta-analysis of student-facing dashboard effects", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-34"], "notes": "SPLIT arbitrated to Major on D6 eligibility"},
    {"id": "R12", "priority": "must_fix", "reviewer": "perspective,domain", "verification_criteria": "Results report an achievement-stratified or interaction analysis, or §5 and §6 withdraw the who-benefits positioning and state that differential harm cannot be identified.", "severity": "major", "evidence_anchor": "absence: §4 and §5 — expected differential-effect analysis for a dashboard with a peer-comparison band", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-17","SC-18"]},
    {"id": "R13", "priority": "must_fix", "reviewer": "domain", "verification_criteria": "Every reference resolves to a verifiable record with a registrant DOI; no entry retains the reserved 10.5555 prefix.", "severity": "unscored_by_raising_seat", "evidence_anchor": "text: References — all fifteen entries use https://doi.org/10.5555/...", "confidence": null, "source_kind": "finding", "sub_claims": ["SC-36"], "notes": "SEVERITY-SOURCE: letter-fallback; CONFIDENCE-SOURCE: unstated; raised expressly for editorial verification"},
    {"id": "S1",  "priority": "should_fix", "reviewer": "methodology,da", "verification_criteria": "Retention base rate, retained/not-retained counts, and an effect size with confidence interval for every comparison.", "severity": "major", "evidence_anchor": "absence: §4 — expected base rate and confidence intervals", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-27"]},
    {"id": "S2",  "priority": "should_fix", "reviewer": "methodology", "verification_criteria": "Item-nonresponse mechanism characterised; 87 responders compared with the 142-student sample.", "severity": "major", "evidence_anchor": "absence: §3.2 and §4.1 — expected a missing-data analysis", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-28"]},
    {"id": "S3",  "priority": "should_fix", "reviewer": "domain,da", "verification_criteria": "Mediation vocabulary removed, or a mediation analysis on an adequately instrumented measure reported.", "severity": "major", "evidence_anchor": "text: §5 'perceived control as a mediating construct'", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-15"]},
    {"id": "S4",  "priority": "should_fix", "reviewer": "domain", "verification_criteria": "SRL cycle cited to a canonical source; §1 and §2 phase claims consistent.", "severity": "major", "evidence_anchor": "absence: §1 and §2 — expected a canonical SRL citation", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-16"]},
    {"id": "S5",  "priority": "should_fix", "reviewer": "eic", "verification_criteria": "§3.3 defines the final exam score and its relationship to the final assessment used for outcome coding.", "severity": "minor", "evidence_anchor": "absence: §3.3 — expected an operational definition of the final exam score", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-32"]},
    {"id": "S6",  "priority": "should_fix", "reviewer": "methodology,eic", "verification_criteria": "Software and version named; data and code availability and preregistration status stated.", "severity": "minor", "evidence_anchor": "absence: §3.4 and end matter — expected named software with version and availability statements", "confidence": 5, "source_kind": "finding", "sub_claims": ["SC-29"]},
    {"id": "S7",  "priority": "should_fix", "reviewer": "methodology,domain", "verification_criteria": "Psychometric support for the single-item measure supplied, or its absence stated as a limitation.", "severity": "minor", "evidence_anchor": "text: §3.3 'measured with a single-item overall rating'", "confidence": 4, "source_kind": "finding", "sub_claims": ["SC-30"]},
    {"id": "S8",  "priority": "nice_to_fix", "reviewer": "eic,domain", "verification_criteria": "Each of the nine uncited entries is either cited where load-bearing or removed; the corrected count is nine of fifteen.", "severity": "minor", "evidence_anchor": "absence: References versus in-text citations", "confidence": 5, "source_kind": "editorial", "sub_claims": ["SC-31"]},
    {"id": "S9",  "priority": "nice_to_fix", "reviewer": "eic,methodology", "verification_criteria": "Data availability, funding, and conflict-of-interest declarations present.", "severity": "minor", "evidence_anchor": "absence: front and back matter — expected the standard declaration block", "confidence": 5, "source_kind": "editorial", "sub_claims": ["SC-33"]},
    {"id": "S10", "priority": "nice_to_fix", "reviewer": "eic", "verification_criteria": "Secondary clarity item reported as prose or a table with a stated purpose, or removed.", "severity": "minor", "evidence_anchor": "text: §4.1 'the reported secondary-item values were N=10; M=3.00; sample SD=0.10'", "confidence": 4, "source_kind": "editorial", "sub_claims": ["SC-8","SC-9"]},
    {"id": "S11", "priority": "nice_to_fix", "reviewer": "eic", "verification_criteria": "Institution naming confirmed compatible with the venue's review-anonymity policy.", "severity": "unstated", "evidence_anchor": "text: §3.1 'at Meridian State University'", "confidence": null, "source_kind": "editorial", "sub_claims": ["SC-37"], "notes": "SEVERITY-SOURCE: letter-fallback; CONFIDENCE-SOURCE: unstated"}
  ]
}
```

---

## Part 3: Reviewer Report Summary (Appendix)

The cards are sprint-contract dimension cards; they carry per-dimension scores and per-finding confidence rather than an overall recommendation or a single report-level confidence score. The matrix below reports the contract-mode equivalents rather than inventing recommendations the seats did not make.

| Dimension | EIC (Journal-Fit) | MTH (Peer 1, Methodology) | DOM (Peer 2, Domain) | PSP (Peer 3, Perspective) | DA (Devil's Advocate) |
|---|---|---|---|---|---|
| Dimensions scored | D5 block, D6 block(repairable) | D1 block(**fatal**), D3 block(repairable) | D2 block(repairable) | D4 block | D3 block(repairable) |
| Dimensions not assessed | D1–D4 | D2, D4, D5, D6 | D1, D3–D6 | D1–D3, D5, D6 | D1, D2, D4–D6 |
| Per-finding confidence range | 4–5 | 3–5 | 4–5 | 4–5 | 4–5 |
| Key strengths named | 4 | 4 | 3 | 3 | — (no strengths section in DA format) |
| Findings: Critical / Major / Minor | 2 / 4 / 4 | 3 / 15 / 2 | 2 / 5 / 1 | 2 / 7 / 0 | 4 CRITICAL / 11 MAJOR |
| Weaknesses row | → decomposed in Step 1b inventory | → Step 1b | → Step 1b | → Step 1b | → Step 1b |

### Journal-Fit Reviewer (EIC)
- Scored: D5 `block`, D6 `block` (`repairable`) · confidence 4–5
- **Key point**: The manuscript's headline claim does not survive contact with its own Results, and the contribution case is never built against the syntheses the field already has — so the paper cannot be screened through to acceptance even before the reporting errors are counted, but the topic is in scope and the contribution needs rebuilding rather than abandoning.

### Peer Reviewer 1 — Methodology (MTH)
- Scored: D1 `block` (`fatal`), D3 `block` (`repairable`) · confidence 3–5
- **Key point**: Five independent arithmetic impossibilities mean the results section cannot be audited from the text; beyond that, the estimator does not match the data types, and mid-term recruitment truncates the outcome so the claimed estimand is not identified even by a corrected analysis.

### Peer Reviewer 2 — Domain (DOM)
- Scored: D2 `block` (`repairable`) · confidence 4–5
- **Key point**: A load-bearing citation is used for the reverse of what its own title reports, and "retention" is measured as one course's completion while being discussed as institutional persistence — both correctable by re-reading and renaming, but both reaching the abstract, Discussion, and Conclusion.

### Peer Reviewer 3 — Perspective (PSP)
- Scored: D4 `block` · confidence 4–5
- **Key point**: Every hop from a volunteer sample in one course to a recommendation for institutions worldwide is asserted rather than argued, and the governance record — no approval, no lawful basis, no linkage protocol, no equity safeguard on a deployed peer-comparison band — cannot be cleared from the text provided.

### Devil's Advocate (DA)
- Scored: D3 `block` (`repairable`) · confidence 4–5 · 4 CRITICAL, 11 MAJOR
- **Key point**: The manuscript diagnoses its own central failure in §1–§2 and commits it in §5–§6; grant every claim and the association still does not survive unassisted, because cumulative session counts are partly a function of how many weeks a student remained enrolled.

---

*Synthesis note: this package arbitrates and consolidates the five Phase 1 cards. It introduces no finding of its own. Where I verified arithmetic independently (the r/p reconciliation, the df bounds, the integer-mean and SD bounds, the Table 2 sum, and the reference count), that verification confirms or corrects a claim already on a card rather than adding a new one; the reference-count correction and the SC-26 non-conflict finding are arbitration outcomes, not new review comments.*
