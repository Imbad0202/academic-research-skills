# Editorial Decision Package

## Contract Arithmetic (v3.6.2 Sprint Contract Synthesizer Protocol)

**Contract:** `reviewer/reviewer_full/v2` · mode `reviewer_full` · panel_size 5 · baseline `v3.20.0`

### Step 1 — Role-scoped scoring matrix

| Dim | Priority | Eligible roles | Assessed eligible seats | Excluded (`not_assessed` / ineligible) | Verdict |
|-----|----------|----------------|--------------------------|-----------------------------------------|---------|
| D1 methodology_rigor | mandatory | methodology | methodology = `block` (`block_class: fatal`) | eic, domain, perspective, da | **block(fatal)** |
| D2 domain_accuracy | mandatory | domain | domain = `block` (repairable) | all others | **block** |
| D3 argumentative_coherence | mandatory | da, methodology | da = `block` (repairable); methodology = `block` (repairable) | eic, domain, perspective | **block** |
| D4 cross_disciplinary_relevance | high | perspective | perspective = `block` (no fatal class; fatality not available on a non-mandatory dimension) | all others | **block** |
| D5 writing_and_structure | normal | eic | eic = `block` | all others | **block** |
| D6 venue_fit_and_contribution | mandatory | eic | eic = `block` (`block_class: repairable`, reasoned on the record) | all others | **block** |

`audit_verdict: block(fatal)` — worst assessed eligible score is `block`, and one assessed eligible seat (methodology, D1) declared a fatal block.

### Step 2 — Failure-condition evaluation

| ID | Sev | Cross-reviewer quantifier | Expression (parse) | Evaluation | Fired |
|----|-----|---------------------------|--------------------|------------|-------|
| F1 | 95 | any | `any <priority=mandatory> dimension has a fatal block` | D1 (mandatory): ≥1 assessed eligible seat declared fatal (methodology) → true; dimension quantifier `any` → true | **true** |
| F2 | 90 | any | `any <priority=mandatory> dimension scores 'block'` | D1, D2, D3, D6 all `block` under `any` → true | **true** |
| F3 | 70 | majority | `two or more <priority=mandatory> dimensions score 'warn' or worse` | D1 (n=1→owner) true; D2 (n=1→owner) true; D3 (n=2→both seats, both `block`) true; D6 (n=1→owner) true; 4 ≥ 2 → true | **true** |
| F4 | 60 | any | `any <priority=high> dimension scores 'block'` | D4 = `block` → true | **true** |
| F5 | 40 | any | `any dimension scores 'warn' or worse` | all six assessed dimensions `block` → true | **true** |
| F0 | 10 | all | `every dimension scores 'pass'` | D1 `block` → false | false |

### Step 3 — Precedence, decision, audit emission

Highest-severity fired condition = **F1 (severity 95)** → `action: editorial_decision=reject`. No softening applied; no substitute scores synthesised; no cross-dimension aggregation beyond the contract's own quantifiers.

```
dimension_verdicts: [D1=block(fatal), D2=block, D3=block, D4=block, D5=block, D6=block]
fired_conditions: [F1, F2, F3, F4, F5]
da_critical_adjudications: [C1=VALIDATED, C2=VALIDATED, C3=VALIDATED, C4=VALIDATED, C5=VALIDATED, C6=VALIDATED, C7=VALIDATED]
editorial_decision=reject
```

No `C<n>=REJECTED` entries, so no rejection-rationale lines are due. Decision is not `accept`, so no `[DA-CRITICAL-VS-ACCEPT]` marker applies.

**Cross-model blind decision check (#518):** `ARS_CROSS_MODEL` not set and no consent gate passed — not run, no behavioural change.

---

## Review Panel Provenance (#540)

`[PROVENANCE-STAMP-MISSING]` — mode is `reviewer_full`, so this block is mandatory and must carry exactly one of the three permitted statements (cross-model slot active / single-family disclosure / dispatch-failure fallback) from the dispatching layer's provenance stamp. No stamp was supplied with this invocation. The synthesizer does not infer model provenance and does not assert or imply model independence that cannot be evidenced. The dispatching layer must supply the stamp before this package is released to the author.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript "Dashboard Engagement and Course Retention: Evidence from an Undergraduate Learning Analytics Deployment." It was assessed by a five-seat panel: a Journal-Fit Reviewer, three peer reviewers (methodology, domain, cross-disciplinary/ethics), and a devil's advocate.

### Decision: Reject

The decision follows the contract's precedence rule on a single fatal block (F1, D1 methodology rigor) and is not a base-rate judgement. Two points of honesty about what that decision does and does not mean. First, five of the six blocked dimensions were classed *repairable* by the seats that own them; the reject is driven by one fatal finding plus one gate-class precondition, not by a diffuse verdict of low quality. Second, the reject is not a statement that the underlying observation is worthless. A narrowed, correctly-scoped, correctly-reported single-site study may well be publishable — but it is a different study from this one, which is why the route is resubmission rather than revision.

### Consensus Analysis

Counts are over the four non-DA seats (Journal-Fit / methodology / domain / cross-disciplinary). `not-mentioned` is silence, not agreement and not opposition. DA findings are adjudicated separately below and are not counted in these denominators.

#### Points of Agreement

- **[CONSENSUS-4] The Abstract's headline correlation does not exist in the Results.** Abstract *r* = .42; §4.2 *r* = .24 — roughly a threefold difference in shared variance. Raised by all four seats (Journal-Fit Critical/conf 5; methodology Major/5; domain Major/5; cross-disciplinary Major/4). The Abstract is also the surface that carries the finding into citation and institutional decision-making.
- **[CONSENSUS-4] Behavioural trace data were analysed without informing students, with no ethics, waiver, or data-governance documentation anywhere in the submission.** All four seats raise it (Journal-Fit Critical/5 as a *gate* item; cross-disciplinary Critical/5 from an IRB seat; methodology Major/4 with the severity ceiling expressly deferred to an editorial and ethics-board determination; domain raises it in body as a referral it declines to score). No seat disputes the existence or the seriousness. The band spread is deference, not dissent, and it is resolved below.
- **[CONSENSUS-4] The Discussion and Conclusion assert causation and worldwide generalisability the design cannot support, and the Limitations section omits the two constraints that would bound them.** All four seats; three of four at confidence 5. Three independent grounds converge — claim-to-design alignment (Journal-Fit), inferential validity (methodology), and citation fidelity against the manuscript's own cited critique of causal overreach (domain), plus a policy-audience reading (cross-disciplinary). Reported once here with all four grounds rather than four times.
- **[CONSENSUS-4] The perceived-control comparison's degrees of freedom match no sample described in the manuscript.** *t*(156) implies ≈158 cases; the item was answered by 87 (df ≈ 85) and the analytic sample is 142. Journal-Fit (Major/4), methodology (Critical/5), domain (Major/4) raise the arithmetic; the cross-disciplinary seat corroborates the downstream consequence — that the processed population is not reconstructable — while expressly declining to verify computation (Minor/conf 3). Weight rests on the methodology seat, which owns D1.
- **[CONSENSUS-3] The exam comparison is internally irreconcilable.** Table 2 sums to *n* = 127 against the text's "all 142 students were classified" and a reported df = 140; *t* = 1.31 at either df gives *p* ≈ .19, not the reported *p* = .008; and the same sentence reports a *p* below the stated alpha while calling the result not significant. Journal-Fit, methodology, domain agree; the cross-disciplinary seat is **silent** on this specific comparison.
- **[CONSENSUS-3] The sampling frame is described in two mutually exclusive ways.** "Random sample of students enrolled in the course section" against a mid-term LMS volunteer opt-in with non-respondents excluded. Journal-Fit, methodology, domain agree at confidence 5; the cross-disciplinary seat is **silent** on the contradiction as such.
- **[CONSENSUS-3] A load-bearing citation is credited with the reverse of what its own title reports.** §2 attributes to Ferro & Nakamura (2021) that dashboards "reliably improve outcomes for lower-achieving students"; the listed title is "When dashboards demotivate: Peer comparison and the lower-achieving student," and the manuscript names this the basis of the equity rationale for institutional deployment and returns to it in the Discussion. Journal-Fit (Major/4, flagged from the reference list only and explicitly not offered as an upper bound), domain (Critical/5, the seat that owns D2), cross-disciplinary (Major/4, on the policy claim built on it). Methodology is **silent** — literature accuracy is outside its seat.

#### Corroborated findings (two seats, no conflict — action-bearing, below the consensus bar)

- **"Retention" is course completion, presented in the vocabulary of institutional persistence.** Domain (Major/5) holds this is not repairable by rewording and requires reframing as a course-completion study; the cross-disciplinary seat (Major/4) agrees the construct drifts across audiences and that unsurvivable claims must be deleted rather than softened. Compatible positions, not a conflict.
- **The SRL framework does no work the data could have contradicted.** Domain (Major/5): a single global control item indexes neither strategy use nor monitoring, yet the Abstract states self-regulated learning *behavior* was measured. Methodology (Major/4) reaches the adjacent measurement conclusion — single items with no reliability or validity evidence carrying one of the two Abstract claims. Theory critique stays with domain; measurement critique with methodology; both feed one roadmap item.
- **The goal-orientation counter-literature the paper itself raises is never reconciled, and no differential-effect analysis is reported.** Domain (Major/4) supplies the rival mechanism — disengaging students stop opening the peer-comparison band and stop completing, producing the same positive association with no facilitative effect. Cross-disciplinary (Major/5) supplies the harm profile: a peer-comparison band recommended institution-wide with no subgroup test.

#### Single-seat findings (weighted by confidence and seat ownership; not consensus, not disputes)

- **The exposure window is truncated by the outcome, so part of the association is definitional.** Methodology only, among the four non-DA seats, at confidence 5 — and DA C2 reached it independently. This count must not be read as weakness: D1's `eligible_roles` is `[methodology]`, so this is a 1-of-1 eligible-seat finding, not a 1-of-4 minority view. Two adjacent seats corroborate components of it (Journal-Fit on self-selection; domain on volunteer under-sampling of disengaging students) without reaching the truncation mechanism itself. This finding is the fatal ground for the decision.
- **Novelty is never established: no systematic review or meta-analysis is engaged anywhere.** Journal-Fit only, confidence 5, and the sole eligible seat for D6. Two synthesis-shaped entries sit uncited in the reference list.
- **Analytic and reporting standards below the field bar.** Methodology only (sole eligible D1 seat), confidence 4–5: Pearson *r* on a dichotomous outcome without naming it point-biserial and with no reported retention marginal to bound its ceiling; no covariate of any kind; median split of an acknowledged right-skewed predictor; no effect sizes, intervals, or power justification; exposure defined by an untested vendor default; no named software, code, or data-availability statement.
- **The recommendation is not actionable and converts the indicator into a target.** Cross-disciplinary only (sole eligible D4 seat), confidence 4: session counts driven up by institutional exhortation carry no demonstrated relation to persistence, and no cost, staffing, advising-capacity, or comparison-with-alternatives content appears.

#### Points of Disagreement and Editor's Resolutions

- **Severity of the nine uncited reference entries.** Journal-Fit bands the reference-list problem Major (unverifiable, and inflating apparent engagement); domain bands the uncited-entries sub-claim Minor on decision impact ("deleting the uncited entries would leave every claim in the paper unchanged"). **Resolution: split the bundle.** (a) The uniform non-resolving `10.5555` DOI prefix is a Journal-Fit-only finding and stands at Major — nothing in the list can be verified as printed. (b) The uncited entries stand at **Minor for decision impact**, per domain's ground, which is correct: no claim rests on them. Both seats' *diagnostic* reading is retained and recorded — a manuscript framed on attrition that lists three persistence sources and cites none in text has assembled rather than consulted a bibliography, and that is the same failure mode that produced the Ferro & Nakamura reversal. Arbitrated on evidence, with the sub-claims separated rather than averaged.
- **Severity of the impossible secondary-item statistics.** Journal-Fit and domain band the *SD* = 0.10 item Minor (it supports no claim); methodology bands it Major (no integer dataset satisfying *N* = 10 and *M* = 3.00 can produce it). **Resolution: Major, per methodology.** Expertise-first: D1 is methodology's dimension, and the finding's weight is not the orphan item's own importance but its membership in the density pattern — three unreconcilable test statistics, two arithmetically unobtainable descriptives, one unreconciled table total, one Abstract/Results mismatch — and that pattern is what carries the decision.
- **Arithmetic arbitration inside the panel.** The DA gives the attainable non-zero *SD* as ≈0.32 and domain as ≈0.33; both figures are incompatible with holding *M* = 3.00 exactly, since a single one-point deviation moves the mean off 3.00. Methodology's bound is the correct one: deviations are integers summing to zero, so either *SD* = 0 or *SD* ≥ √(2/9) ≈ 0.471. The editorial record adopts methodology's bound. This strengthens rather than weakens the finding.
- **Reference-count arbitration.** Journal-Fit reports sixteen entries with ten uncited; the DA reports "nine of the sixteen"; domain reports fifteen with nine uncited. Checked against the submitted list: **15 entries, 6 cited in text (Calloway, Ferro & Nakamura, Osei, Rutledge & Berange, Vandermeer, Ibarra), 9 uncited.** Domain's count is correct and is the count carried into the roadmap.
- **Journal-Fit's Table 2 / Table 1 mean discrepancy.** Journal-Fit reads Table 2's weighted mean (≈70.7) against Table 1's 71.3 as a further inconsistency. **Resolution: not an independent finding.** The gap is fully explained by the fifteen cases already unaccounted for between *n* = 127 and *n* = 142; it is evidence for that finding, not a separate one. Merged into R3.
- **Ethics severity band: gate item or Major reporting gap?** Journal-Fit and the cross-disciplinary seat treat undisclosed secondary use of trace data as a precondition to review; methodology bands it Major and expressly defers the ceiling to an editorial and ethics-board determination; domain refers it out while stating it is not a mere compliance matter. **Resolution: precondition, not one vote among four.** No seat argues the opposing position, methodology's deferral is an invitation for exactly this ruling, and the seat with the relevant standing competence (an IRB member who has drafted trace-data transparency notices) is at confidence 5. This item is not averaged into the revision workload; it is answered first, and everything else is provisional until it is.

#### Devil's Advocate CRITICAL Adjudication

The DA is not one of the four counted seats. Every CRITICAL is adjudicated and none is treated as an automatic veto; the author must respond to each regardless of adjudication.

| ID | DA argument (compressed) | Corroborated by | Adjudication | Required author response |
|----|--------------------------|-----------------|--------------|--------------------------|
| C1 | Causal/prescriptive conclusions from an observational cross-section with no covariates and no rival-explanation exclusion, against the Introduction's own commitment | Journal-Fit W3, methodology W9, domain W3, cross-disciplinary W4 | **VALIDATED** | Rewrite to associational scope (R6) |
| C2 | Partial circularity: engagement accrues across the term while retention determines how much term a student is present for | methodology W7 (fatal ground) | **VALIDATED** | Re-estimate on a fixed early exposure window (R2) |
| C3 | Survivorship + volunteer selection: mid-term recruitment structurally excludes withdrawers, under-samples disengagers | methodology W7/W8, Journal-Fit W4, domain W6 | **VALIDATED** | Full-cohort extraction and response-rate disclosure (R2, R5) |
| C4 | Abstract *r* = .42 vs Results *r* = .24; the "promising lever" claim rests on the larger figure | Journal-Fit W1, methodology W6, domain W7, cross-disciplinary W10 | **VALIDATED** | State which value the data yield and correct the other (R4) |
| C5 | *t*(156) reconciles with no sample in the manuscript | methodology W1, Journal-Fit W8, domain W8 | **VALIDATED** | Supply raw output and exclusion flow (R3) |
| C6 | *t* = 1.31 with *p* = .008 is impossible, and the prose contradicts the reported *p* | methodology W2, Journal-Fit W9, domain W9 | **VALIDATED** | Rerun and rewrite the comparison together (R3) |
| C7 | Trace data analysed without informing students; no ethics approval, waiver, or oversight statement anywhere | Journal-Fit W2, cross-disciplinary W1/W2, methodology W16, domain (referral) | **VALIDATED** | Establish approval and waiver status on the record (R1) |

The DA's own qualification on C7 (confidence 4, venue policy not supplied to that seat) is superseded by the Journal-Fit seat, which supplies the venue standard at confidence 5.

### Decision Rationale

Two independent grounds carry this decision, and neither is reachable by revision of the present manuscript.

The first is the fatal block on methodology rigor. The exposure measure counts dashboard sessions cumulatively "during the term"; the outcome is whether the student reached the final assessment. A student who leaves in week nine accrues nine weeks of sessions against a completer's fifteen, so some non-zero part of *r* = .24 is guaranteed by the operationalisations before any behavioural process is invoked. Mid-term recruitment compounds this: students who had already withdrawn could not respond, and logs were pulled only for respondents, so the retention variance is survivorship-filtered before analysis begins. No re-analysis of this dataset separates the definitional from the empirical component. Recovering the stated estimand requires full-cohort log extraction, an exposure window closed before any withdrawal, and baseline covariates — a new study.

The second is a precondition, not a workload item. The manuscript states in its own voice that students were not informed their dashboard activity would be analysed, and supplies no approving body, protocol number, waiver basis, retention or de-identification arrangement, or notice text. Three seats independently treat this as gate-class; no seat argues otherwise. Retrospective disclosure cannot manufacture consent that was not obtained, and until the authors establish on the record whether this is a documentation failure or a conduct-of-research matter, no substantive assessment is more than provisional.

Behind those two sit findings the panel reached unanimously and that would independently require major work: an Abstract whose headline number does not appear in the Results, three test statistics corresponding to at least three mutually incompatible sample sizes with two descriptives unobtainable from the stated integer scales, a self-contradictory sampling frame, a causal and worldwide-generalisation claim layer the design cannot license, and a reversed load-bearing citation carrying the equity rationale. The manuscript's prose, structure, and self-aware limitations section are genuinely competent, and the panel was instructed not to infer analytic quality from writing quality; it did not.

What survives is worth saying. The measurement critique in §2 is applied to the paper itself, the operational definitions are specific enough to be audited — which is what made these findings detectable — and the primary correlation is the one reported statistic that reconciles exactly with its stated sample size. A tightly scoped course-completion study, correctly reported and ethically documented, is a describable paper. This is not that paper yet.

### Top Blocking Issues (0–3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | Exposure window is truncated by the outcome and the sample is survivorship-filtered, so the engagement–retention estimand is not identifiable in these data | methodology (fatal, D1); DA C2/C3 | text: §3.3 "the number of distinct sessions in which a student opened the dashboard view during the term"; §3.2 "Midway through the term, an announcement was posted to the course LMS inviting students" | R2 |
| 2 | Behavioural trace data analysed outside the disclosed consent scope, with no ethics, waiver, or data-governance documentation anywhere | Journal-Fit (Critical), cross-disciplinary (Critical), methodology, domain (referral); DA C7 | text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study." | R1 |
| 3 | Reported statistics correspond to at least three mutually incompatible sample sizes (127, 142, 158), with two descriptives unobtainable from the stated integer scales and an Abstract value absent from the Results | methodology (Critical ×2), Journal-Fit, domain; DA C4/C5/C6 | text: §4.3 "t(156) = 3.02, p = .003"; §4.3 "the difference was small, t(140) = 1.31, p = .008" | R3 (with R4) |

---

## Part 2: Resubmission Roadmap

Because the decision is Reject, this roadmap describes what a **new submission** would have to establish rather than a revision of the present manuscript. It is emitted in the standard roadmap format so that it is directly consumable as `academic-paper` revision-mode input.

> **Sub-claim column:** this synthesis ran under the v3.6.2 sprint-contract arithmetic protocol, which does not use the Step 1b sub-claim inventory. Items are therefore keyed to reviewer card finding IDs in the `Source` column rather than to synthesizer-assigned `SC-` ids, and `Sub-Claim(s)` reads `—` throughout. No item was created from anything other than a finding a seat actually raised.

### Required Revisions (Must Fix)

> **Ordinal contract:** the `Required Item Details` blocks below are numbered `R1..R8` in this table's order.

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---------------|--------------|----------|-----------------|------------|--------|----------|------------------|
| R1 | Establish on the record the ethics-approval and consent-waiver status of the trace-data analysis, or withdraw the log-based analysis | — | Critical (transported: Journal-Fit W2 Critical; cross-disciplinary W1 Critical; methodology W16 Major, ceiling deferred) | text: §3.2 "Students were not informed that their dashboard activity data would be analyzed for this study." | 5 — the manuscript states the fact; absence of accompanying statements checked across all surfaces by two seats | EIC, R3, R1, R2 (referral); DA C7 | P1 | Not estimable by the authors alone — institutional determination; blocks all other work |
| R2 | Re-establish an identifiable estimand: full-cohort log extraction, exposure counted only in a fixed window every student inhabited, and baseline covariates | — | Critical (transported: methodology W7 Critical, fatal) | text: §3.3 "the number of distinct sessions in which a student opened the dashboard view during the term"; §3.2 mid-term recruitment announcement | 5 — follows directly from the stated exposure and outcome definitions and the recruitment timing | R1; DA C2/C3 | P1 | New data extraction + re-analysis; 3–6 months |
| R3 | Reconcile every reported statistic against the data, and supply raw analysis output, a variable-level data dictionary, and a full exclusion/missingness flow | — | Critical (transported: methodology W1, W2 Critical; W3, W4, W5 Major) | text: §4.3 "t(156) = 3.02, p = .003"; §4.3 "t(140) = 1.31, p = .008"; §4.1 "N=10; M=3.00; sample SD=0.10; integer scale=1-5"; table: Table 2 (n = 66 + 61 = 127) | 5 — closed-form arithmetic and recomputation against the manuscript's own tables | R1, EIC, R2; DA C5/C6, M5/M7 | P1 | 2–3 weeks if the raw data exist; otherwise unresolvable |
| R4 | State which correlation value the data yield and correct the other; re-derive every downstream claim from the corrected value | — | Critical (transported: Journal-Fit W1 Critical; methodology W6, domain W7, cross-disciplinary W10 Major) | text: Abstract "Dashboard engagement correlated positively with retention (r = .42)"; §4.2 "(r = .24, p = .004)" | 5 — direct textual comparison of two reported values for the same association | EIC, R1, R2, R3; DA C4 | P1 | 2–3 days once R3 is settled |
| R5 | Replace the sampling description with an accurate account of recruitment, and report the response rate against the full enrolment denominator | — | Major (transported: Journal-Fit W4, methodology W8, domain W6 — all Major) | text: §3.2 "using a random sample of students enrolled in the course section" against "Students who chose to respond, and who consented to the survey, formed the study sample" | 5 — two adjacent statements in one subsection cannot both hold | EIC, R1, R2; DA C3/M3/M8 | P1 | 1 week |
| R6 | Rewrite Discussion and Conclusion in associational terms; delete the worldwide-deployment and "dependable strategy" claims; add self-selection and the correlational-to-causal boundary to Limitations | — | Critical (transported: methodology W9 Critical; Journal-Fit W3, domain W3, cross-disciplinary W4 Major) | text: §5 "dashboard engagement improved course retention"; §6 "is a dependable strategy for improving retention across programs and disciplines" | 5 — claim-to-design alignment; three of four seats at confidence 5 | R1, EIC, R2, R3; DA C1/M1 | P1 | 1–2 weeks |
| R7 | Recheck the Ferro & Nakamura (2021) attribution against the source and rebuild the equity rationale and the Discussion passage that rests on it | — | Critical (transported: domain W1 Critical; Journal-Fit W7, cross-disciplinary W5 Major) | text: §2 "Dashboards have been shown to reliably improve outcomes for lower-achieving students" against reference title "When dashboards demotivate: Peer comparison and the lower-achieving student" | 5 — direct comparison of an in-text attribution against the reference entry in the same manuscript | R2, EIC, R3; DA M2 | P1 | 1–2 weeks |
| R8 | Reframe the study as a course-completion study, or measure persistence across enrolment periods; retitle, re-abstract, and rebuild the problem statement accordingly | — | Major (transported: domain W2 Major; cross-disciplinary W3 Major) | text: §3.3 "coded dichotomously as whether the student remained enrolled and completed the final assessment" with §1 "Undergraduate attrition remains a persistent concern" | 5 — standard construct boundary in persistence research, checked against the paper's own coding rule | R2, R3 | P1 | 2–4 weeks (reframing) or a new longitudinal design |

### Required Item Details

**R1 — Ethics and consent documentation for the trace-data analysis**
- **Acceptance criteria**: The submission carries the approving body and protocol number, the exemption or waiver basis for analysing individually linked behavioural logs, the retention and de-identification arrangements for the extracted logs, and the text of whatever notice students received about LMS analytics; if no approval covers the log analysis, the log-based analysis is withdrawn from the submission.

**R2 — Identifiable estimand for the engagement–retention association**
- **Acceptance criteria**: Engagement is counted only within a fixed calendar window that closes before any withdrawal in the cohort, logs are drawn for the full enrolled cohort rather than survey respondents, at least prior attainment and credit load enter the model, and the reported association is accompanied by an explicit statement of what remains definitional after the window is fixed.

**R3 — Full statistical reconciliation and analysis materials**
- **Acceptance criteria**: Every reported test statistic, df, and *p*-value reproduces from the supplied raw output; the perceived-control mean is attainable at its stated *n*; the secondary item's *SD* is either corrected or the item is removed; Table 2's group sizes, the text's classification claim, and the reported df agree; and a CONSORT-style exclusion flow accounts for every case from enrolment to each reported analysis, including the 142→87 item non-response.

**R4 — Abstract/Results reconciliation of the headline correlation**
- **Acceptance criteria**: A single correlation value appears in the Abstract, Results, Discussion, and Conclusion, matching the supplied raw output, with the discrepancy's origin stated in the response letter.

**R5 — Accurate sampling description and response rate**
- **Acceptance criteria**: The "random sample" characterisation is removed or substantiated with the randomisation procedure; the recruitment paragraph states the survey response rate against the full enrolment denominator; and every generalisation claim is narrowed to what the actual sampling frame licenses.

**R6 — Claim layer rewritten to the design's inferential scope**
- **Acceptance criteria**: No sentence in the Abstract, Discussion, or Conclusion asserts that engagement improved, raised, or causes retention; the Conclusion contains no worldwide, cross-programme, or "dependable/generalizable" claim; and Limitations names self-selection, survivorship, reverse causation, and the correlational-to-causal boundary explicitly.

**R7 — Citation fidelity for the equity rationale**
- **Acceptance criteria**: The Ferro & Nakamura attribution states that source's actual finding and direction; the equity-oriented deployment rationale is rebuilt on sources that support it or withdrawn; and the Discussion passage that returns to the attribution is rewritten to match.

**R8 — Construct alignment between measure and claim**
- **Acceptance criteria**: The title, Abstract, Introduction, and Conclusion refer to course completion rather than retention wherever the data support only the course-level construct, and the manuscript states explicitly what course completion does and does not evidence about institutional attrition, engaging the persistence literature on that question.

### Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---------------|--------------|----------|-----------------|------------|--------|----------|------------------|
| S1 | Either remove the SRL mechanism and mediation claims, or measure strategy use and monitoring; correct the Abstract's claim that SRL behaviour was measured | — | Major (transported: domain W4 Major; methodology W15 Major) | text: Abstract "we measured dashboard engagement, self-regulated learning behavior, and course persistence" with §3.3 "measured with a single-item overall rating" | 5 (domain) / 4 (methodology — strength depends on venue norms for single-item global ratings) | R2, R1; DA M6/M9 | P2 | 1–2 weeks, or new instrumentation |
| S2 | Add differential-effect/subgroup analysis stratified at minimum by prior achievement, and reconcile the goal-orientation counter-account the paper itself raises | — | Major (transported: cross-disciplinary W6 Major; domain W5 Major) | absence: §4 Results and §5 Discussion — expected a differential-effect or subgroup analysis by prior achievement and goal orientation for a dashboard containing a peer-comparison band; checked Table 1, Table 2, §4.1–§4.3, §5, §5.1 | 5 (cross-disciplinary) / 4 (domain — bias magnitude not estimable from what is reported) | R3, R2 | P2 | 2–3 weeks on existing data if prior attainment is available |
| S3 | Position the contribution against named systematic reviews or meta-analyses of student-facing dashboards and state the increment testably | — | Major (transported: Journal-Fit W5 Major) | absence: §2 Literature Review — expected engagement with at least one systematic review or meta-analysis of student-facing dashboards; checked §1, §2, §5, §5.1, §6, References | 5 — the seat's standing competence is what the review literature already establishes | EIC | P2 | 2–3 weeks |
| S4 | Upgrade the analysis: logistic regression with covariates, point-biserial named and the retention marginal reported, effect sizes with confidence intervals, continuous predictor retained instead of median-split, sessionisation sensitivity check | — | Major (transported: methodology W10–W14 Major) | text: §3.4 "Associations between continuous measures were assessed with Pearson correlations."; §3.3 "students were split at the median number of dashboard sessions" | 5 — standard properties of point-biserial correlation, dichotomisation, and sessionisation sensitivity | R1; DA M4 | P2 | 2–3 weeks |
| S5 | Add reproducibility affordances: named software with version, analysis code, data-availability statement | — | Minor (transported: methodology W17 Minor) | absence: §3.4 and end matter — expected named software with version, analysis code, and a data availability statement; checked Methods, Analysis, Results, References | 5 — no such materials appear in the submission | R1 | P2 | 3–5 days |
| S6 | Address indicator corruption under exhortation, and supply cost, staffing, advising-capacity, and comparison-with-alternatives content for the practitioner audience the Conclusion addresses | — | Major (W7) / Minor (W8), transported from cross-disciplinary | text: "encouraging students to engage with them is a dependable strategy" and "the number of distinct sessions in which a student opened the dashboard view" | 4 — indicator corruption under incentive is a standard institutional-metric failure mode | R3 | P2 | 1–2 weeks |
| S7 | Supply resolvable identifiers for all references; cite or delete the nine uncited entries | — | Major (DOIs, Journal-Fit W6) / Minor (uncited entries, arbitrated to domain W11) | text: References "https://doi.org/10.5555/1010203"; absence: References — expected in-text citation of the nine listed sources (Ainsworth & Devi 2018, Berange 2021, Delacroix & Ohno 2022, Halloran 2020, Kessler & Amadou 2019, Montez 2022, Prakash & Tolliver 2021, Solberg & Whitfield 2018, Wexler & Ojo 2020) | 4 (DOIs, Journal-Fit) / 5 (uncited count, domain — exhaustive comparison) | EIC, R2 | P3 | 3–5 days if the sources exist |
| S8 | Presentation cleanup: remove or correct the orphan clarity item, fix inconsistent decimal precision, define the final-exam measure in §3.3, cite or delete the claim that single-item ratings are common practice | — | Minor (transported: Journal-Fit W10, methodology W18, domain W12 — all Minor) | text: §4.1 "the reported secondary-item values were N=10; M=3.00; sample SD=0.10; integer scale=1-5"; table: Table 1 row "Final exam score (0-100)" | 4–5 — presentation defects directly observable | EIC, R1, R2 | P3 | 2–3 days |

### Revision Checklist

#### Priority 1 — Structural (estimated total effort: 3–7 months, dominated by R2; R1 gates everything)
- [ ] R1: Obtain and document ethics approval / waiver status for the trace-data analysis, or withdraw the log analysis
- [ ] R2: Re-extract full-cohort logs; recount exposure in a fixed pre-withdrawal window; add baseline covariates
- [ ] R3: Reconcile all statistics; supply raw output, data dictionary, and exclusion flow
- [ ] R4: Fix the Abstract/Results correlation discrepancy and re-derive downstream claims
- [ ] R5: Restate recruitment accurately; report response rate against enrolment
- [ ] R6: Rewrite Discussion and Conclusion to associational scope; complete Limitations
- [ ] R7: Correct the Ferro & Nakamura attribution and rebuild the equity rationale
- [ ] R8: Reframe as a course-completion study (title, abstract, framing, conclusion)

#### Priority 2 — Content supplementation (estimated total effort: 8–11 weeks)
- [ ] S1: Remove or properly measure the SRL mechanism; correct the Abstract's measurement claim
- [ ] S2: Add subgroup / differential-effect analysis; reconcile the goal-orientation counter-account
- [ ] S3: Position against named syntheses and state the increment
- [ ] S4: Logistic model, point-biserial naming, retention marginal, effect sizes and intervals, drop median split, sessionisation sensitivity
- [ ] S5: Add software version, code, and data-availability statement
- [ ] S6: Address indicator corruption; add cost, staffing, and comparison content

#### Priority 3 — Text and formatting (estimated total effort: 1 week)
- [ ] S7: Resolvable DOIs; cite or delete the nine uncited entries
- [ ] S8: Remove or correct the orphan clarity item; fix decimal precision; define the final-exam measure; support or delete the single-item-convention claim

### Resubmission Timeline

This is a Reject, so no revision deadline applies. Realistically, R1 must be settled before any further work is worthwhile; if approval and waiver exist, R2 alone implies a 3–6 month re-analysis on newly extracted full-cohort logs, and the package as a whole is a new submission rather than a revision. Authors who cannot complete R2 should consider submitting the narrowed course-completion study described in R8 with the log analysis correctly scoped and every claim in R6 honoured.

### Response Letter

Use `templates/revision_response_template.md` and respond to every item R1–R8 and S1–S8 individually, including the seven DA CRITICAL items C1–C7 adjudicated above. Items adjudicated VALIDATED must be addressed on the merits; "respectfully decline" is not available for any CONSENSUS-4 item or for R1.

### Machine-form Roadmap (Schema 7)

```json
{
  "items": [
    {"id": "R1", "priority": "must_fix", "verification_criteria": "Approving body and protocol number, waiver/exemption basis for log analysis, log retention and de-identification arrangements, and student-facing notice text are all present; or the log-based analysis is withdrawn.", "reviewer": ["eic", "perspective", "methodology", "domain"], "severity": "critical", "evidence_anchor": "text: §3.2 'Students were not informed that their dashboard activity data would be analyzed for this study.'", "confidence": 5, "source_kind": "finding"},
    {"id": "R2", "priority": "must_fix", "verification_criteria": "Exposure counted in a fixed window closing before any cohort withdrawal, logs drawn for the full enrolled cohort, prior attainment and credit load in the model, residual definitional component stated explicitly.", "reviewer": ["methodology"], "severity": "critical", "evidence_anchor": "text: §3.3 'the number of distinct sessions in which a student opened the dashboard view during the term'; §3.2 mid-term recruitment announcement", "confidence": 5, "source_kind": "finding"},
    {"id": "R3", "priority": "must_fix", "verification_criteria": "All reported t, df, and p reproduce from supplied raw output; perceived-control mean attainable at its stated n; secondary-item SD corrected or item removed; Table 2 ns, text classification claim, and df agree; full exclusion/missingness flow supplied including 142 to 87 item non-response.", "reviewer": ["methodology", "eic", "domain"], "severity": "critical", "evidence_anchor": "text: §4.3 't(156) = 3.02, p = .003'; §4.3 't(140) = 1.31, p = .008'; table: Table 2 (n = 66 + 61 = 127)", "confidence": 5, "source_kind": "finding"},
    {"id": "R4", "priority": "must_fix", "verification_criteria": "A single correlation value appears in Abstract, Results, Discussion, and Conclusion, matching supplied raw output; discrepancy origin stated in the response letter.", "reviewer": ["eic", "methodology", "domain", "perspective"], "severity": "critical", "evidence_anchor": "text: Abstract '(r = .42)'; §4.2 '(r = .24, p = .004)'", "confidence": 5, "source_kind": "finding"},
    {"id": "R5", "priority": "must_fix", "verification_criteria": "'Random sample' removed or substantiated with procedure; response rate reported against full enrolment denominator; generalisation claims narrowed to the actual sampling frame.", "reviewer": ["eic", "methodology", "domain"], "severity": "major", "evidence_anchor": "text: §3.2 'using a random sample of students enrolled in the course section' against 'Students who chose to respond ... formed the study sample'", "confidence": 5, "source_kind": "finding"},
    {"id": "R6", "priority": "must_fix", "verification_criteria": "No causal or probability-raising verb in Abstract, Discussion, or Conclusion; no worldwide/cross-programme/'dependable' claim; Limitations names self-selection, survivorship, reverse causation, and the correlational-to-causal boundary.", "reviewer": ["methodology", "eic", "domain", "perspective"], "severity": "critical", "evidence_anchor": "text: §5 'dashboard engagement improved course retention'; §6 'a dependable strategy for improving retention across programs and disciplines'", "confidence": 5, "source_kind": "finding"},
    {"id": "R7", "priority": "must_fix", "verification_criteria": "Ferro & Nakamura attribution states the source's actual finding and direction; equity rationale rebuilt on supporting sources or withdrawn; Discussion passage relying on it rewritten.", "reviewer": ["domain", "eic", "perspective"], "severity": "critical", "evidence_anchor": "text: §2 'Dashboards have been shown to reliably improve outcomes for lower-achieving students' against reference title 'When dashboards demotivate: Peer comparison and the lower-achieving student'", "confidence": 5, "source_kind": "finding"},
    {"id": "R8", "priority": "must_fix", "verification_criteria": "Title, Abstract, Introduction, and Conclusion refer to course completion wherever the data support only the course construct; the manuscript states what course completion does and does not evidence about institutional attrition, engaging the persistence literature.", "reviewer": ["domain", "perspective"], "severity": "major", "evidence_anchor": "text: §3.3 'coded dichotomously as whether the student remained enrolled and completed the final assessment' with §1 'Undergraduate attrition remains a persistent concern'", "confidence": 5, "source_kind": "finding"},
    {"id": "S1", "priority": "should_fix", "verification_criteria": "SRL mechanism and mediation claims removed, or strategy-use and monitoring measures added; Abstract no longer claims SRL behaviour was measured.", "reviewer": ["domain", "methodology"], "severity": "major", "evidence_anchor": "text: Abstract 'we measured dashboard engagement, self-regulated learning behavior, and course persistence' with §3.3 'measured with a single-item overall rating'", "confidence": 5, "source_kind": "finding"},
    {"id": "S2", "priority": "should_fix", "verification_criteria": "Differential-effect analysis stratified at minimum by prior achievement is reported, and the goal-orientation counter-account raised in §2 is explicitly reconciled with the interpretation.", "reviewer": ["perspective", "domain"], "severity": "major", "evidence_anchor": "absence: §4 Results and §5 Discussion — expected differential-effect or subgroup analysis by prior achievement and goal orientation; checked Table 1, Table 2, §4.1-§4.3, §5, §5.1", "confidence": 5, "source_kind": "finding"},
    {"id": "S3", "priority": "should_fix", "verification_criteria": "At least one named systematic review or meta-analysis of student-facing dashboards is engaged in text, with the study's increment stated in a form a reader can test.", "reviewer": ["eic"], "severity": "major", "evidence_anchor": "absence: §2 Literature Review — expected engagement with at least one systematic review or meta-analysis; checked §1, §2, §5, §5.1, §6, References", "confidence": 5, "source_kind": "finding"},
    {"id": "S4", "priority": "should_fix", "verification_criteria": "Logistic regression with covariates reported; coefficient named point-biserial where Pearson r is used on the dichotomous outcome; retention marginal reported; effect sizes with confidence intervals for both comparisons; continuous predictor retained; sessionisation sensitivity across at least two alternative thresholds.", "reviewer": ["methodology"], "severity": "major", "evidence_anchor": "text: §3.4 'Associations between continuous measures were assessed with Pearson correlations.'; §3.3 'students were split at the median number of dashboard sessions'", "confidence": 5, "source_kind": "finding"},
    {"id": "S5", "priority": "should_fix", "verification_criteria": "Software named with version, analysis code supplied, and a data-availability statement present.", "reviewer": ["methodology"], "severity": "minor", "evidence_anchor": "absence: §3.4 and end matter — expected named software with version, analysis code, and data availability statement; checked Methods, Analysis, Results, References", "confidence": 5, "source_kind": "finding"},
    {"id": "S6", "priority": "should_fix", "verification_criteria": "Manuscript addresses that exhorted session counts carry no demonstrated relation to persistence, and supplies cost, staffing/advising-capacity, and comparison-with-alternatives content for any practitioner recommendation retained.", "reviewer": ["perspective"], "severity": "major", "evidence_anchor": "text: 'encouraging students to engage with them is a dependable strategy' and 'the number of distinct sessions in which a student opened the dashboard view'", "confidence": 4, "source_kind": "finding"},
    {"id": "S7", "priority": "nice_to_fix", "verification_criteria": "All reference DOIs resolve to published records; the nine currently uncited entries are either cited in text or deleted.", "reviewer": ["eic", "domain"], "severity": "minor", "evidence_anchor": "text: References 'https://doi.org/10.5555/1010203'; absence: References — expected in-text citation of nine listed sources; checked all sections", "confidence": 4, "source_kind": "finding", "notes": "SPLIT arbitrated: DOI verifiability Major (eic, sole raiser); uncited-entry severity resolved to Minor per domain's decision-impact ground. Correct count is 15 entries, 6 cited, 9 uncited."},
    {"id": "S8", "priority": "nice_to_fix", "verification_criteria": "Orphan clarity item removed or corrected; decimal precision consistent and within instrument resolution; final-exam measure defined in §3.3; single-item-convention claim cited or deleted.", "reviewer": ["eic", "methodology", "domain"], "severity": "minor", "evidence_anchor": "text: §4.1 'the reported secondary-item values were N=10; M=3.00; sample SD=0.10; integer scale=1-5'; table: Table 1 row 'Final exam score (0-100)'", "confidence": 4, "source_kind": "editorial"}
  ]
}
```

---

## Part 3: Reviewer Report Summary (Appendix)

### Journal-Fit Reviewer
- Scored: D5 `block`, D6 `block` (repairable, reasoning on record) | Findings: 4 strengths, 10 weaknesses (2 Critical, 7 Major, 1 Minor)
- Key point: a careful reader cannot state what this study found — the Abstract's headline number is absent from the Results, the sampling frame is described two incompatible ways, and no synthesis literature is engaged, so the increment cannot be judged.

### Peer Reviewer 1 (Methodology)
- Scored: D1 `block` (**fatal**), D3 `block` (repairable) | Findings: 5 strengths, 18 weaknesses (4 Critical, 12 Major, 2 Minor)
- Key point: three reported statistics correspond to at least three mutually incompatible sample sizes and two descriptives are unobtainable from the stated integer scales; independently of that, the exposure window is truncated by the outcome, so the stated estimand is not recoverable from this sample.

### Peer Reviewer 2 (Domain)
- Scored: D2 `block` (repairable) | Findings: 3 strengths, 12 weaknesses (1 Critical, 8 Major, 3 Minor)
- Key point: a load-bearing citation is credited with the reverse of its own finding, "retention" is course completion dressed as institutional persistence, and the SRL framework does no work the data could have contradicted.

### Peer Reviewer 3 (Cross-disciplinary / Ethics)
- Scored: D4 `block` | Findings: 4 strengths, 10 weaknesses (1 Critical, 7 Major, 2 Minor)
- Key point: trace data were analysed outside the disclosed consent scope with no governance documentation; the equity claim addressed to institutional decision-makers is untested, and encouraging engagement converts the observed indicator into a target.

### Devil's Advocate
- Scored: D3 `block` (repairable) | Findings: 7 CRITICAL, 9 MAJOR — all 7 CRITICAL adjudicated VALIDATED
- Key point: steelmanned, the paper reports an association with a mechanism-consistent correlate; as written it argues for something its data cannot reach, and the central quantity contradicts itself across sections.

---

## Synthesis Notes and Card-Hygiene Flags

Flagged, not fixed — Phase 1 reviewer cards are outside this seat's write scope.

1. **`[CARD-ARTIFACT: perspective]`** The cross-disciplinary card opens with a `## Scoring Plan Dissent` heading, then withdraws it in-line ("the heading above is withdrawn and no dissent card is emitted"). No dissent is asserted, so no fatality was minted during scoring-plan dissent and the arithmetic is unaffected; the malformed emission should be corrected at source.
2. **`[CARD-COUNT-ERROR: eic]`** The Journal-Fit card states sixteen references with ten uncited; the submitted list contains fifteen entries with six cited and nine uncited. Domain's count is correct and is what the roadmap carries.
3. **`[CARD-ARITHMETIC-ERROR: da, domain]`** Both give the attainable non-zero *SD* for the secondary item as ≈0.32/0.33; those values require the mean to move off 3.00. Methodology's √(2/9) ≈ 0.471 is the correct bound and is adopted in the editorial record. The finding itself is strengthened, not weakened.
4. **Reference verifiability could not be established.** All fifteen DOIs sit on the reserved, non-resolving `10.5555` prefix, so no citation in this submission could be checked against a published record. Recorded here as a verifiability limitation on the review, not as a substantive scholarly judgement about the authors.
5. **No dimension went unassessed by its eligible seats**, no ineligible seat was allowed to vote, no abstention entered a denominator, and no substitute scores were synthesised. The panel ran at full `panel_size` 5; no `[PANEL-SHRUNK]` condition arose.
