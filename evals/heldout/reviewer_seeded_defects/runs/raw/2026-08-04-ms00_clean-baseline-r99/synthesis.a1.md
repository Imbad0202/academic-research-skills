# Editorial Decision Package

**Contract**: `reviewer/reviewer_full/v2` · mode `reviewer_full` · stage `reviewer_full_review` · baseline `v3.20.0`
**Panel**: 5 cards received (eic, methodology, domain, perspective, da) = `panel_size: 5`. No seat dropped; no `[PANEL-SHRUNK]`.
**Synthesizer role**: arbitration and arithmetic only. No new review findings are introduced anywhere in this package.

---

# Part 0 — Sprint Contract Audit (mechanical)

## Step 1 — Role-scoped scoring matrix

Ineligible seats are excluded from the matrix entirely; ineligible `not_assessed` values and eligible abstentions enter neither numerator nor denominator.

| Dim | Priority | Eligible roles | Assessed eligible seats (score) | Ineligible/abstained | Dimension verdict |
|-----|----------|----------------|----------------------------------|----------------------|-------------------|
| D1 methodology_rigor | mandatory | methodology | methodology = **block** (`block_class: repairable`) | eic, domain, perspective, da (ineligible) | `block` |
| D2 domain_accuracy | mandatory | domain | domain = **block** (`block_class: fatal`) | eic, methodology, perspective, da (ineligible) | `block(fatal)` |
| D3 argumentative_coherence | mandatory | da, methodology | da = **warn**; methodology = **warn** | eic, domain, perspective (ineligible) | `warn` |
| D4 cross_disciplinary_relevance | high | perspective | perspective = **warn** | all others (ineligible) | `warn` |
| D5 writing_and_structure | normal | eic | eic = **warn** | all others (ineligible) | `warn` |
| D6 venue_fit_and_contribution | mandatory | eic | eic = **block** (`block_class: repairable`) | all others (ineligible) | `block` |

Every dimension has ≥1 assessed eligible seat → no `[DIMENSION-UNASSESSED]`.

**audit_verdict: block(fatal)** (worst assessed eligible score = `block`; one assessed eligible seat — domain on D2, its owner dimension — declared a fatal block).

## Step 2 — Failure-condition evaluation

Two-stage semantics applied throughout: `cross_reviewer_quantifier` over each dimension's assessed eligible seats first, then the expression's dimension quantifier over the resulting per-dimension booleans.

| ID | Sev | Expression (parsed pattern) | Per-dimension evaluation | Fired |
|----|-----|------------------------------|--------------------------|-------|
| F1 | 95 | `any <priority> dimension has a fatal block` (fatal scope on mandatory — valid) | quantifier `any`: D1 false (repairable), **D2 true (fatal)**, D3 false, D6 false → `any` → true | **true** |
| F2 | 90 | `any mandatory dimension scores 'block'` | quantifier `any`: D1 true, D2 true, D3 false, D6 true → `any` → true | **true** |
| F3 | 70 | `two or more <priority> dimensions score '<score>' or worse` | quantifier `majority` per dimension: D1 (n=1, owner) true; D2 (n=1, owner) true; D3 (n=2 → both seats: warn, warn) true; D6 (n=1, owner) true → 4 ≥ 2 | **true** |
| F4 | 60 | `any <priority>-priority dimension scores 'block'` | high-priority set = {D4}; quantifier `any`: perspective = warn ≠ block → false | false |
| F5 | 40 | `any dimension scores 'warn' or worse` | quantifier `any`: D1 true (block ⊃ warn-or-worse) → true | **true** |
| F0 | 10 | `every dimension scores 'pass'` | quantifier `all`: D1 = block → false | false |

## Step 3 — Precedence and emission

Fired = {F1(95), F2(90), F3(70), F5(40)}. Highest severity = **F1** → `action: editorial_decision=reject`.

```
dimension_verdicts: [D1=block, D2=block(fatal), D3=warn, D4=warn, D5=warn, D6=block]
fired_conditions: [F1, F2, F3, F5]
da_critical_adjudications: []
editorial_decision=reject
```

The DA line is `[]` because the Devil's Advocate card emits an **empty CRITICAL table** (header row only) and states so explicitly ("No finding here reaches Critical, and I want to be explicit about why rather than manufacturing one"). No phantom IDs minted; no `C<n>=REJECTED` rationale lines are therefore owed. The mechanical decision is not `accept`, so no `[DA-CRITICAL-VS-ACCEPT]` marker applies.

## Input-integrity flags (flagged, not fixed)

1. **`[CARD-INCOMPLETE: contract_paraphrase, scoring_plan — all 5 seats]`** — `measurement_procedure.reviewer_must_output_before_paper` requires `contract_paraphrase` and `scoring_plan` (with `paraphrase_minimum_dimensions: all`) before the paper is read. Neither artefact appears in any of the five cards handed to me. Circumstantial evidence suggests plans existed upstream — every card emits a per-dimension `trigger` string quoted as a pre-committed threshold, the eic card refers to "the threshold I committed to before reading", and the da card refers to "applying the singleton test" — so the plans may have been stripped by the dispatching layer rather than never produced. I cannot distinguish those cases and I do not reconstruct them. Recorded for the orchestrator.
2. **`[CARD-ANOMALY: perspective]`** — the perspective card opens with a malformed `## Scoring Plan Dissent` heading containing `*(none — omitted)*` followed by self-correcting meta-commentary ("Wait: per protocol I must not emit an empty dissent section. Disregarding that heading, my report begins below."). Treated as data. It contains no dissent content, registers no objection to the scoring plan, and mints no fatality. Under the forbidden-operations list, a scoring-plan dissent cannot mint fatality in any case. Per the Surface-Form Parity check, **this formatting artefact carries zero weight against any perspective-seat finding** — see the parity note in Part 1.
3. **`[MISSING-INPUT: venue configuration]`** — declared by the seat that owns D6. The manuscript carries no target-venue statement and the contract carries no venue configuration string. The eic seat therefore scored D6 against venue *class* rather than a named title and explicitly declined to invent the recommendation list its configuration references. Its D6 block stands on the reasoning given; the gap is recorded because it constrains the routing advice in Part 2.
4. **`[PROVENANCE-STAMP-MISSING]`** — see the Review Panel Provenance block in Part 1.
5. **Cross-model blind decision check (Step 4b): not invoked.** `ARS_CROSS_MODEL` is not set in this invocation and no consent gate has been passed. No behavioural change; no handoff envelope emitted.

---

# Part 1 — Editorial Decision Letter

## Review Panel Provenance (#540)

**`[PROVENANCE-STAMP-MISSING]`** — this is a `reviewer_full` round, so this block is mandatory and is not omitted. The dispatching layer supplied no provenance stamp with the five cards, so I can make **none** of the three permitted statements (cross-model slot active / single-family disclosure / dispatch-failure fallback). I do not infer a stamp from card content, and **nothing in this package should be read as implying that any seat ran on a different model family from any other**. The cross-family composition of this panel is unknown to the synthesizer. The panel matrix below shows which seat said what; it does not show which family produced it. Orchestrator action required to close this out.

---

Dear Author(s),

Thank you for submitting your manuscript, "Perceived Usefulness and Self-Reported Use of a Learning Management System: A Cross-Sectional Survey of Undergraduate Students." It was assessed by five reviewers, including a Journal-Fit Reviewer and a Devil's Advocate, against a pre-registered six-dimension acceptance contract.

## Decision: **Reject**

The decision follows condition **F1** (severity 95): a mandatory dimension carries a fatal block. D2 (domain accuracy) was scored `block(fatal)` by its owner seat on the ground that the manuscript's entire six-source evidence base is unverifiable. Three further conditions also fired (F2, F3, F5); F1 takes precedence on severity.

I want to be exact about the shape of this decision, because it is not the shape of a rejection on quality. Your analysis is arithmetically sound — three independent seats recomputed the Fisher-z interval and the sample reconciliation and found both correct — your causal discipline is above the norm for this literature, and no seat asked you to write a bigger paper. The rejection rests on a defect in the evidence base, and both seats who examined it stated their position conditionally (see Arbitration A4). That conditionality is recorded, not discounted: the fired condition's action is not softened, and this decision is not downgraded. What follows is a roadmap for a resubmission that clears the gate.

## Consensus Analysis

### Panel matrix (Step 1a)

| Dimension | Journal-Fit Reviewer (eic) | R1 Methodology | R2 Domain | R3 Perspective | Devil's Advocate |
|---|---|---|---|---|---|
| Overall recommendation | not emitted (sprint-contract card format) | not emitted | not emitted | not emitted | not emitted |
| Implied stance, quoted verbatim | "after revision, the short-report venue, as a Brief Report" | none stated | "the remaining findings below would stand as a major revision" (conditional on reference verification) | "Whether the resulting contribution clears the venue's bar is the editor-in-chief's call, not mine." | none stated |
| Dimensions assessed | D5 warn, D6 block | D1 block, D3 warn | D2 block(fatal) | D4 warn | D3 warn |
| Report-level confidence score | not emitted (per-finding confidence only) | not emitted | not emitted | not emitted | not emitted |
| Key strengths | 3 (S1–S3) | 4 (S1–S4) | 5 (S1–S5) | 3 (S1–S3) | opening paragraph, untabled |
| Key weaknesses | 7 (W1–W7) → decomposed in Step 1b | 9 (W1–W9) → Step 1b | 8 (W1–W8) → Step 1b | 8 (W1–W8) → Step 1b | 6 MAJOR (M1–M6), 0 CRITICAL |
| Questions section | not emitted | not emitted | not emitted | not emitted | not emitted |
| Minor-issue channel | folded into W-entries | folded into W-entries | folded into W-entries | folded into W-entries | 3 untabled observations |

No card emits an overall Accept/Revise/Reject recommendation or a report-level confidence score; the sprint-contract card format does not require either. The "implied stance" row quotes card text and is not treated as a recommendation in any counting rule.

### Sub-claim inventory (Step 1b)

Weakness bundles are decomposed into atomic sub-claims before any consensus is computed, so that partial support is never read as full resolution. Severity and confidence are **transported** from the cards, never re-derived; where a sub-claim sits inside a bundle whose band differs, the parent's band travels with it and the mismatch is noted.

Table compression, stated for auditability: rows are emitted for `raised`, `corroborated` and `disputed` positions only. Reviewers not listed for a sub-claim hold `not-mentioned`, recorded in the `silent` column. **The denominator is always the 4 non-DA reviewers**, and silence is neither agreement nor opposition — it is never promoted into the `agree` count. DA positions are recorded for visibility with `(off-count)` and never enter any consensus arithmetic.

| SC | Parent weakness | Reviewer | Position | Evidence pointer (transported) | Severity | Conf | Silent (not-mentioned) | Disposition |
|----|-----------------|----------|----------|-------------------------------|----------|------|------------------------|-------------|
| SC-1 | reference base unverifiable | eic W2 | raised | `text: References — "https://doi.org/10.5555/2050001", ".../2050006"` | Critical | 4 | R1, R3 | corroborated finding (2/4) |
| | | R2 W1 | corroborated | same anchor, registrant-prefix analysis | Critical | 5 | | |
| | | DA (off-count) | — | not raised | — | — | | |
| SC-2 | canonical lineage absent; PU definition misattributed to 2019–20 | R2 W2 | raised | `absence: §2 — expected canonical PU source and pooled LMS estimates; checked §1, §2, §5, §7, References` | Major | 5 | eic, R1, R3 | single-reviewer finding (1/4) |
| SC-3 | comparability claim has no numeric benchmark | R2 W3 | raised | `text: §2, §5 — "effect sizes vary across samples and instruments" / "consistent with prior technology-acceptance research"` | Major | 5 | eic, R1, R3 | single-reviewer finding (1/4); DA M5 corroborates off-count |
| SC-4 | contribution conceded, not argued; no gap statement | eic W5 | raised | `absence: §2 closing para — expected statement of what prior work leaves unestablished; checked §1, §2, §5, §7` | Minor | 4 | R1, R3 | corroborated finding (2/4) |
| | | R2 W3 | corroborated | "collapses into an assertion of consistency with an unspecified benchmark" | Major | 5 | | |
| SC-5 | below full-article threshold → Brief Report | eic W1 | raised | `text: §7 — "offered as an incremental, design-bounded contribution rather than a causal claim"` | Major | 5 | R1, R2, R3 (R3 expressly defers) | single-reviewer finding (1/4), owner seat on D6 |
| SC-6 | six item stems nowhere reproduced | R1 W1 | raised | `absence: §3.2 + back matter — expected verbatim item wording; checked §3.2, §3.4, §4, §7, References, no appendix` | Critical | 5 | — | **[CONSENSUS-4]** |
| | | R2 W6 | corroborated | `text: §3.2 — "a six-item scale adapted from Costa and Wren (2019)"` | Major | 4 | | |
| | | R3 W2 | corroborated | `absence: §3.2 + end matter — expected the six item stems or an appendix` | Major | 5 | | |
| | | eic W6 | corroborated | "the six perceived-usefulness items are not reproduced" | Minor | 5 | | |
| SC-7 | adaptation from source instrument undocumented | R1 W1 | raised | as SC-6 anchor, "explicit change log against the source instrument" | Critical | 5 | eic | **[CONSENSUS-3]** (silent: eic) |
| | | R2 W6 | corroborated | `text: §3.2 — "whose original instrument reported strong internal consistency"` | Major | 4 | | |
| | | R3 W2 | corroborated | "'adapted' is doing undisclosed work" | Major | 5 | | |
| | | DA M6 (off-count) | — | `text: §3.2` premise-surfacing | Major | 4 | | |
| SC-8 | no in-sample structural/validity evidence; α is sole warrant | R1 W1 | raised | as SC-6 anchor, "either a confirmatory factor model or the item-level matrix" | Critical | 5 | eic | **[CONSENSUS-3]** (silent: eic) |
| | | R2 W6 | corroborated | "validity is not transitive across adaptation" | Major | 4 | | |
| | | R3 W2 | corroborated | "Internal consistency establishes that the items covary, not what they ask" | Major | 5 | | |
| SC-9 | single-item ordinal DV → reliability unestimable, attenuation unbounded, CI understates uncertainty | R1 W2 | raised | `text: §3.2 — "We treat this as an ordinal indicator of self-reported use and interpret it accordingly."` | Major | 5 | eic, R2, R3 | single-reviewer finding (1/4), owner seat on D1 |
| SC-10 | use-item category labels absent, median category undefined | R1 W2 | raised | same parent anchor | Major | 5 | eic, R2, R3 | single-reviewer finding (1/4); DA untabled observation |
| SC-11 | ordinal-appropriate (polychoric) estimate should be primary | R1 W3 | raised | `text: §3.4 — "Because the use item is ordinal, we also computed a Spearman correlation as a robustness check."` | Major | 5 | eic, R2, R3 | single-reviewer finding (1/4) |
| SC-12 | Spearman as reported (no interval) cannot serve as an inferential alternative | R1 W3 | raised | same parent anchor | Major | 5 | eic | **[SPLIT]** → Arbitration A1 |
| | | R2 S2 | disputed | `text: §4 — "The Spearman robustness check yielded a comparable coefficient (ρ = .40)"` | n/a (strength entry) | `[CONFIDENCE-SOURCE: unavailable]` | | |
| | | R3 S3 | disputed | `text: §4 / §3.4` | n/a (strength entry) | 4 | | |
| SC-13 | self-report chosen over available logs, disclosed but never justified | R3 W8 | raised | `absence: §3.1 + §6 second limitation — expected a stated reason logs were not used; checked §3.1–3.3, §6, §7` | Minor | 4 | eic, R1, R2 | single-reviewer finding (1/4) |
| SC-14 | common-method variance never named as a rival explanation | R1 W8 | raised | `text: §2 — "studies relying on self-report capture perceived rather than actual engagement"` | Major | 5 | eic, R3 | corroborated finding (2/4) |
| | | R2 W4 | corroborated | `text: Abstract — "...tracks with LMS engagement among undergraduates."` | Major | 4 | | |
| | | DA M1 (off-count) | — | `absence: §5 — expected CMV named; checked Abstract, §2, §3.2, §4, §5, §6` | Major | 5 | | |
| SC-15 | PU and self-reported use not shown operationally distinct | R2 W4 | raised | as above | Major | 4 | eic, R1, R3 | single-reviewer finding (1/4) |
| SC-16 | abstract escalates: behavioural "engagement" + single-institution bound dropped | R3 W1 | raised | `text: Abstract "...LMS engagement among undergraduates"; §4 "reported engagement reflects many influences..."` | Major | 5 | — | **[SPLIT]** → Arbitration A2 |
| | | R1 W9 | corroborated | `text: Abstract closing sentence` | Minor | 4 | | |
| | | R2 W4 | corroborated | "the abstract... quietly reinstates the stronger reading" | Major | 4 | | |
| | | eic S2 | disputed | `text: Abstract — "The findings offer modest, design-bounded evidence..."` — "passes without qualification" | n/a (strength entry) | 5 | | |
| | | DA M2 (off-count) | — | `text: Abstract / §2` | Major | 5 | | |
| SC-17 | §3.3 anonymity claim incompatible with §3.1 duplicate removal | R1 W5 | raised | `text: §3.3 — "No identifying information was collected, and responses could not be linked back to individual students."` | Major | 4 | eic, R2 | corroborated finding (2/4) |
| | | R3 W5 | corroborated | `text: §3.1 "5 duplicate entries were removed"; §3.3` | Major | 5 | | |
| SC-18 | no sampling frame, no response rate, no composition distribution | R1 W4 | raised | `absence: §3.1 — expected enrolled population, response rate, year-level distribution; checked §3.1, §3.3, §4, §6, Abstract` | Major | 5 | R2 | **[CONSENSUS-3]** (silent: R2) |
| | | eic W6 | corroborated | `absence: §3.1 — expected sampling-frame size and computable response rate` | Minor | 5 | | |
| | | R3 W7 | corroborated | `text: §3.1 / §6` | Major | 5 | | |
| SC-19 | recruitment ran through the system being measured → selection on the outcome, not merely a generalisation limit | R3 W7 | raised | `text: §3.1 "distributed through the institution's course-announcement channel"; §6 "students who engage more... may be overrepresented"` | Major | 5 | eic, R2 | corroborated finding (2/4) |
| | | R1 W4 | corroborated | "selection into the sample is plausibly correlated with the outcome variable itself" | Major | 5 | | |
| | | DA M4 (off-count) | — | `text: §3.1 / §6` | Major | 4 | | |
| SC-20 | no table or figure anywhere, including the scatterplot reported as an analytic step | eic W3 | raised | `absence: §4 and §3.4 — expected at least one table or figure incl. the scatterplot; checked §3.4, §4, all section bodies, References` | Major | 5 | R1, R2, R3 | single-reviewer finding (1/4) |
| SC-21 | no reproducibility affordances (software, data, code, recomputable descriptives) | R1 W7 | raised | `absence: §3.4 + back matter — expected software/version, data availability, code or cross-tab; checked §3.4, §4, §7, References` | Minor | 5 | R2, R3 | corroborated finding (2/4) |
| | | eic W7 | corroborated | `absence: front/back matter — expected data-availability, funding, competing-interests declarations` | Minor | 5 | | |
| SC-22 | shared variance stated qualitatively where R² ≈ .18 is available | eic W4 | raised | `text: §4 — "The proportion of variance shared by the two measures was accordingly modest"` | Minor | 4 | — | **[CONSENSUS-4]** |
| | | R2 W8 | corroborated | same anchor | Minor | 5 | | |
| | | R3 W6 | corroborated | same anchor | Minor | 4 | | |
| | | R1 W3 | corroborated | same anchor, "the shared-variance statement is made verbally rather than numerically (R² = .18)" | Major (parent-bundle transport; band mismatch noted) | 5 | | |
| | | DA (off-count) | — | untabled observation | — | — | | |
| SC-23 | onboarding implication not actionable / restates the correlation as advice | R3 W4 | raised | `text: §5 — "LMS onboarding which helps students see concrete usefulness..."` | Minor | 5 | eic, R1, R2 | single-reviewer finding (1/4); DA M3 corroborates off-count in a **stronger** form (inferential validity, Major, 4) |
| SC-24 | §6 omits unmeasured access/equity confounders of both variables | R3 W3 | raised | `absence: §6 — expected a named limitation for unmeasured confounders of access frequency; checked §6 items 1–4, §5, §4 parenthetical, §3.2` | Major | 5 | eic, R1, R2 | single-reviewer finding (1/4) |
| SC-25 | LMS never named; mandatory-use policy never reported | R2 W5 | raised | `absence: §3.1, §3.2 — expected platform identity/version + mandatory-use policy; checked §1, §3, §4, §6` | Major | 5 | eic, R1 | corroborated finding (2/4) |
| | | R3 W1 | corroborated | "access frequency... tracks assessment deadlines, timetable structure, and notification defaults" | Major | 5 | | |
| SC-26 | power statement is post-hoc sensitivity presented as design sensitivity; ">.80" generous at the boundary | R1 W6 | raised | `text: §3.4 — "With n = 214, the study had greater than .80 power to detect a correlation of r >= .19"` | Minor | 5 | eic | **[SPLIT]** → Arbitration A3 |
| | | R2 S5 | disputed | `text: §3.4` — "the defensible form of this statement and is worth keeping" | n/a (strength entry) | `[CONFIDENCE-SOURCE: unavailable]` | | |
| | | R3 S3 | disputed | `text: §3.4` — "tells a reader what the design could and could not have detected" | n/a (strength entry) | 4 | | |
| SC-27 | residual variance attributed to specific unmeasured factors | R2 W7 | raised | `text: §4 — "...including course requirements and assessment schedules"` | Minor | 4 | eic, R1 | corroborated finding (2/4) |
| | | R3 W3 | corroborated | "§4 gestures at course requirements... then drops the issue" | Major (parent-bundle transport) | 5 | | |
| SC-28 | venue-required declarations absent | eic W7 | raised | `absence: front/back matter — expected data-availability, funding, competing-interests declarations` | Minor | 5 | R2, R3 | corroborated finding (2/4) |
| | | R1 W7 | corroborated | "no data availability statement appears" | Minor | 5 | | |
| SC-29 | t statistic and df not reported for the primary test | R1 W3 | raised | `text: §3.4 / §4` — "t(212) ≈ 6.74 from the reported values" | Major (parent-bundle transport) | 5 | eic, R2, R3 | single-reviewer finding (1/4) |

Decomposition discipline: every sub-claim above is an atomic part of a claim a reviewer actually made. No sub-claim originates with the synthesizer.

### Points of agreement

- **[CONSENSUS-4] SC-6** — the six perceived-usefulness item stems are reproduced nowhere in the manuscript, and there is no appendix or supplementary-materials statement. All four non-DA reviewers, independently, with anchors.
- **[CONSENSUS-4] SC-22** — the shared-variance statement should carry the number (R² ≈ .18) rather than the adjective "modest". All four non-DA reviewers.
- **[CONSENSUS-3] SC-7** (silent: Journal-Fit Reviewer) — what was "adapted" from Costa & Wren (2019) is nowhere stated, so "previously validated" is unsupported for the instrument actually used.
- **[CONSENSUS-3] SC-8** (silent: Journal-Fit Reviewer) — Cronbach's α is the sole psychometric warrant; internal consistency is not construct validity, and no in-sample structural evidence is offered.
- **[CONSENSUS-3] SC-18** (silent: R2 Domain) — the eligible-population denominator is absent, so no response rate exists and the voluntary-response bias the manuscript itself concedes cannot be sized.
- **Corroborated findings (2/4, no conflict — action-bearing but below the consensus bar):** SC-1 (references, two Critical anchors), SC-4, SC-14 (common-method variance), SC-17 (anonymity/deduplication), SC-19 (selection on the outcome), SC-21, SC-25, SC-27, SC-28.
- **Single-reviewer findings (1/4, no conflict — resolved on confidence weight, not by arbitration):** SC-2, SC-3, SC-5, SC-9, SC-10, SC-11, SC-13, SC-15, SC-20, SC-23, SC-24, SC-29. Every one of these carries a transported confidence of 4 or 5 from a seat operating inside its own remit, so all take full weight under the weighting rule. None is excluded or reduced.

**One agreement across the whole panel that is not a finding, and which the author should read as such:** all five seats independently credit the manuscript's correlational discipline, and three of them recomputed the reported statistics and found them correct. The Fisher-z interval on r = .42 at n = 214 returns [.30, .52] exactly as printed; 233 − 14 − 5 = 214 reconciles; ρ = .40 is consistent with the Pearson estimate. The Devil's Advocate opened on the standard adversarial targets — inflated effect, mismatched interval, smuggled causal verb, headline contradicting the results — and reports that all of them failed. That is worth stating plainly in a rejection letter.

### Points of disagreement, and their resolution

Three sub-claims carry a `disputed` position and therefore route to arbitration ahead of any consensus label. In each case the disputing positions arrive inside **strength** entries rather than as stated objections; that is recorded so their weight is visible, and it does not reduce them to nothing — a reviewer who credits a practice as sufficient is taking a position on it.

**A1 · SC-12 — does the reported Spearman check discharge the ordinal-measurement concern?**
- **R1 (Methodology, conf 5)**: ρ = .40 is reported as a bare coefficient with no interval, so it "cannot serve as an inferential alternative, only as reassurance that the sign is stable."
- **R2 (Domain, S2) and R3 (Perspective, S3, conf 4)**: the rank-based check is the right move for an ordinal outcome and "lets the reader verify that the parametric assumption is not doing the work."
- **Type**: severity disagreement (all three agree the check exists and is appropriate; they disagree on what it establishes).
- **Editor's resolution — both positions upheld on decomposition, R1's remedy required.** R2 and R3 are correct that the check's presence is a genuine strength and that it establishes sign stability; that credit stands and should survive revision. R1 is correct that sign stability is not an inferential alternative: an estimate without an interval cannot carry the paper's magnitude claim, and the magnitude is what the manuscript interprets. **Rationale**: expertise-first (D1 is R1's owned dimension and this is a measurement-estimation question), and evidence-first (R1's position rests on a recomputation and on what the manuscript does and does not print; R2's and R3's rest on the check's presence, which R1 does not deny). Remedy: an ordinal-appropriate primary estimate with an interval, Pearson and Spearman retained as sensitivity analyses **with** intervals. → **R8**.

**A2 · SC-16 — does the abstract's closing sentence overreach?**
- **R3 (Perspective, conf 5, Major)**, **R2 (Domain, conf 4, Major)** and **R1 (Methodology, conf 4, Minor)**: "LMS engagement among undergraduates" imports a behavioural, multidimensional construct that §2 explicitly disowns, and drops the single-institution bound §6 says is required. R3 anchors this in the term of art as used in learning analytics; R2 anchors it in the paper's own §2 commitment; DA M2 (conf 5, off-count) independently reaches the same reading and adds that "engagement" recurs at §2 and §4, so the slippage is sustained rather than a stray word.
- **Journal-Fit Reviewer (conf 5, S2)**: the abstract "describes the paper that follows, including its modesty" and "passes without qualification."
- **Type**: existence disagreement.
- **Editor's resolution — the escalation finding stands; the Journal-Fit Reviewer's credit is upheld on a narrower reading.** The two positions are about different properties of the same sentence. The Journal-Fit Reviewer's concordance check is a check on claim **strength** — whether a correlational finding gets upgraded to a causal one between body and abstract — and on that axis the manuscript passes, which is worth keeping in the record. It is not a check on construct **identity** or on scope bounds, and the card does not address either; the disputing position is therefore silence on the contested point rather than a reasoned rebuttal of it. Against that, three seats supply the same specific anchor, including the seat whose operational remit is institutional engagement metrics and the seat that owns domain construct accuracy. **Rationale**: evidence-first — the manuscript's own §2 ("an indicator of perceived use rather than a behavioral count") and §6 (single-institution restriction) are internal evidence that the abstract's closing sentence contradicts, and no card rebuts that. Remedy: terminological correction, no new data. → **R11**.

**A3 · SC-26 — is the power statement mislabelled?**
- **R1 (Methodology, conf 5)**: the statement is conditioned on the achieved n = 214, the survey ran to a fixed three-week window rather than a recruitment target, and nothing indicates an a priori target; it is a post-hoc sensitivity analysis presented as design sensitivity, and power at r = .19 with n = 214 is ≈ .798, so ">.80" is marginally generous at the stated boundary.
- **R2 (S5) and R3 (S3, conf 4)**: framing the statement as a detectable-effect floor rather than computing power on the observed coefficient is "the defensible form" and "worth keeping."
- **Type**: perspective difference, largely dissolved on inspection — R1 explicitly concedes the same point R2 and R3 make ("it is the defensible form of post-hoc computation... it is not the observed-power fallacy, and the arithmetic is essentially right").
- **Editor's resolution — keep the statement, correct its label and its boundary.** R2 and R3 are upheld: do not delete this, and do not replace it with observed power. R1 is upheld on the two narrow points nobody contests: the phrase "the design was sensitive" implies design-stage planning the manuscript never claims, and ".80" should read "approximately .80" at r = .19. **Rationale**: no evidentiary conflict exists once the sub-claim is decomposed; both remedies are compatible and cheap. → **S3**.

**Scope arbitration (the risk the panel was warned about, and which largely did not materialise).** The three peer seats pull in directions that, adopted wholesale, would produce a different manuscript rather than a revision. Each seat, to its credit, self-limited: R2 opened by naming and declining its own instinct to demand a bigger paper; R3 stated twice that it was not asking for a redesign, only for the rationale behind the design that was run; R1's remedies are disclosure and re-estimation on the existing data, not new collection. I therefore rule only on the two remainders. **In scope for resubmission**: the item-level correlation matrix and any structural evidence obtainable from the existing responses, as discriminant/validity evidence (proposed by R1 and by R2). **Out of scope, and to be written into Future Research rather than the roadmap**: a behavioural criterion or log-based outcome (raised by R2 W4 as one of two options, and expressly *not* demanded by R3). No roadmap item requires new data collection.

### Devil's Advocate adjudication

`da_critical_adjudications: []`

The Devil's Advocate CRITICAL band is empty by the DA's own explicit reasoning, applying the singleton test: each of its findings is repairable by rewriting, added argument, or added reporting, and none alone unseats the manuscript's core claim, which is a correctly computed bounded bivariate correlation. **The synthesizer records that as sound and does not manufacture a CRITICAL to fill the band** — an unvalidated negative claim carries the same evidence burden as a positive one, and there is nothing here to validate. No `C<n>` IDs exist, so no adjudication or rejection-rationale lines are owed.

For visibility, the DA's six MAJOR findings are all carried into the roadmap through corroborating non-DA findings, and none is orphaned: M1 → R10; M2 → R11; M3 → S5 (recorded in the stronger inferential-validity form the DA gives it, alongside R3's weaker actionability version); M4 → R7; M5 → R3; M6 → R2. The DA's three untabled observations map to R8 (R² number), R9 (undefined median category) and, for the "substantial body of work" single-citation point, R4. The DA's D3 warn — driven by the unnamed common-method rival explanation and the Section 5 implication that requires a direction the same section disowns — is one of the two warns that fired F3, and it is the reason R10 and S5 are in this roadmap rather than optional.

### Surface-form parity note

Two places in this synthesis could have let phrasing substitute for substance, and both were checked against the paper rather than against the prose.

The perspective card arrives with a malformed opening heading and visible self-correction. Under the opposite-style counterfactual — would these findings weigh less if the same substance arrived in clean, formal prose? — the answer must be no, and it is: SC-16, SC-17, SC-19, SC-24 and SC-25 are each anchored to specific manuscript text or to an enumerated absence check, and each is independently corroborated or grounded in the seat's stated operational remit. The formatting artefact is recorded in Part 0 as a card anomaly and carries no weight against any finding.

Conversely, no sub-claim gained weight for technical specificity alone. The most precise-sounding material in the panel — recomputed Fisher-z bounds, `t(212) ≈ 6.74`, power ≈ .798, registrant-prefix structure — was credited only because it is checkable against the manuscript's printed values, and I verified the direction of each claim against the paper before letting it drive an item. Authorship of any card played no part in weighting.

### Decision Rationale

The contract's arithmetic returns Reject on F1, and the substance behind it is narrow but load-bearing. Every one of the manuscript's six references carries a DOI on the `10.5555` reserved documentation prefix, with suffixes running unbroken from 2050001 to 2050006 in reference-list order, and five of six journal titles are one or two words from real venues. Two seats reached this independently: the Journal-Fit Reviewer from production experience with prefix resolution, the domain seat from registrant-prefix structure and first-hand knowledge of the venues. Because §2 is built exclusively from those six items, the reference base is not an apparatus problem sitting beside the paper — it *is* the paper's literature review, its measurement provenance, and the whole of its stated contribution, which is comparability with prior work. Nothing about the field can currently be checked, and the manuscript's only claim to novelty rests on sources no reader can retrieve.

Three further conditions fired independently of that. D1 is blocked because the exposure instrument is unrecoverable: six item stems printed nowhere, an undocumented adaptation, no in-sample structural evidence, α standing alone — and comparability, the paper's stated purpose, is exactly what an undocumented adaptation destroys. D6 is blocked because one bivariate coefficient on the most replicated association in this literature does not sustain a full research article. Both D3-eligible seats scored warn on the same unnamed rival explanation, common-method variance between two self-reports collected in one instrument on one occasion, which bears on the magnitude the paper interprets.

What is genuinely good here is not decorative. The causal discipline holds across every section, the reverse pathway is volunteered rather than buried, the ordinal robustness check was run and reported, and the arithmetic survived three independent recomputations. This is a competent small study with an unverifiable foundation, not an overclaimed one.

### Top Blocking Issues (3, ranked)

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|------|----------------|--------------------|-----------------|------------------------|
| 1 | Entire six-source reference base is unverifiable: reserved `10.5555` documentation prefix, sequential suffixes in list order, five near-miss journal titles. §2, §3.2 provenance, §5 and §7 comparability all rest on it. Drives D2 `block(fatal)` and condition F1. | R2 Domain (Critical, conf 5); Journal-Fit Reviewer (Critical, conf 4) | `text: References — "https://doi.org/10.5555/2050001", "https://doi.org/10.5555/2050006"` | R1 |
| 2 | Exposure instrument unrecoverable: item stems nowhere reproduced (CONSENSUS-4), adaptation undocumented (CONSENSUS-3), no in-sample structural evidence (CONSENSUS-3). Drives D1 `block`. | R1 Methodology (Critical, conf 5); R2 (Major, 4); R3 (Major, 5); Journal-Fit Reviewer (Minor, 5) | `absence: §3.2 Measures and manuscript back matter — expected verbatim item wording, an explicit statement of what was changed from Costa and Wren (2019), and factor-structure evidence in the present sample; checked §3.2, §3.4, §4, §7, References, and the absence of any appendix` | R2 |
| 3 | Contribution below the full-article threshold: a single bivariate coefficient on a saturated association from one site, with the paper's own contribution statement conceding incrementality. Drives D6 `block`. | Journal-Fit Reviewer (Major, conf 5) | `text: §7 Conclusion — "offered as an incremental, design-bounded contribution rather than a causal claim"` | R3 |

### Required Item Details

**R1 — Resolve the reference base**
Supply verifiable bibliographic records for all six sources — registered DOIs resolving to retrievable records at the named venues, with correct volume, issue and page ranges — or replace them with verifiable sources and rebuild every claim that depends on them (§2 in full, the §3.2 instrument provenance, the §5 and §7 comparability claims). This item gates the other twelve: no judgement about literature adequacy, measurement provenance, or comparability is meaningful until it clears.
- **Acceptance criteria**: All six references resolve to retrievable records under registered publisher prefixes with matching venue, volume, issue and pages; no `10.5555` DOI remains; every claim in §2, §3.2, §5 and §7 is traceable to a resolvable source.

**R2 — Reproduce the instrument and document the adaptation**
Print the six perceived-usefulness item stems verbatim in an appendix. State explicitly what was changed from Costa & Wren (2019) — wording, item count, response format, target referent — and why. Provide in-sample structural evidence: a confirmatory factor model, or at minimum the item-level inter-correlation matrix. Remove or qualify "previously validated" in the abstract wherever it describes the adapted form rather than the original.
- **Acceptance criteria**: Appendix reproduces all six item stems verbatim; a change log against the source instrument is stated item by item; in-sample structural evidence (CFA or full item-level matrix) is reported; the abstract's validity claim matches the evidence for the adapted scale.

**R3 — Recategorise and argue the contribution**
Resubmit as a Brief Report / Research Note rather than a full research article, and replace the self-deprecating contribution paragraph with a positive positioning claim: state the numeric benchmark (a pooled estimate or reported range from verifiable synthesis work), say where r = .42 falls relative to it, and name the institutional profile under-represented in the existing distribution that this sample fills.
- **Acceptance criteria**: Submission category is Brief Report or Research Note; §2 and §5 state a numeric prior estimate or range with its heterogeneity; §7 locates r = .42 against that benchmark and names what a reader gains that they did not have before.

**R4 — Rebuild §2 around the field's actual lineage**
Cite the canonical source of the perceived-usefulness construct and correct the attribution of its definition, which is currently sourced to 2019–2020 references. Add UTAUT-generation work and any existing synthesis of LMS acceptance. Support the §1 phrase "a substantial body of work" with more than one citation.
- **Acceptance criteria**: The perceived-usefulness definition is attributed to its canonical source; UTAUT-generation work and at least one LMS-acceptance synthesis are cited; no construct definition is attributed to secondary commentary; §1's "substantial body of work" carries multiple citations.

**R5 — Reconcile the anonymity statement with duplicate removal**
Disclose how the five duplicates were identified, whether any identifier or fingerprint (session token, cookie, IP address, device hash, single-use link) was retained and for how long, and what the ethics approval actually covered. Correct whichever of §3.1 and §3.3 is inaccurate. If deduplication used response-pattern matching, state the rule and its false-positive risk.
- **Acceptance criteria**: §3.3 accurately describes the collection condition (anonymous or pseudonymous) given the mechanism disclosed in §3.1; the deduplication mechanism and any identifier retention are stated; the approval scope matches what was collected.

**R6 — Report the sampling frame and participation**
Give the eligible undergraduate enrolment, the number of invitations delivered, and the computed response rate. Report the year-level distribution of the 214 analysed cases against institutional benchmarks rather than asserting that all four levels were present. If available, add an early-versus-late responder comparison as a nonresponse proxy.
- **Acceptance criteria**: §3.1 reports eligible enrolment, invitations delivered and a computed response rate; the year-level (and any available demographic) distribution appears with an institutional comparison; §6's voluntary-response limitation cites a figure a reader can weigh.

**R7 — State the recruitment channel and reclassify the selection threat**
State whether the course-announcement channel is hosted inside the LMS. If it is, treat selection on the outcome variable as a threat to the coefficient itself in §5, not solely as an overrepresentation/generalisability caveat in §6, and say which direction it plausibly biases the estimate.
- **Acceptance criteria**: §3.1 states whether the recruitment channel is LMS-hosted; §5 addresses selection on the outcome as a validity threat to the coefficient with a stated likely direction; §6's fourth limitation no longer files it as generalisability only.

**R8 — Make an ordinal-appropriate estimate primary and complete the test reporting**
Report a polychoric or otherwise ordinal-appropriate correlation as the primary estimate, with a bootstrap or equivalent interval. Retain Pearson and Spearman as sensitivity analyses, each with an interval. Report the test statistic and degrees of freedom alongside the p value. Give R² as a number (≈ .18) in place of "modest". Align decimal precision between the descriptives and the coefficients.
- **Acceptance criteria**: An ordinal-appropriate coefficient with an interval is the primary estimate; Pearson and Spearman appear as sensitivity analyses each with an interval; t and df accompany the p value; R² is reported numerically; decimal precision is consistent across §4.

**R9 — Disclose the outcome measure's uncertainty and its response distribution**
State explicitly that no reliability estimate exists for a single-item outcome, that no correction for measurement error in it is possible, and that the reported interval therefore reflects sampling error only. Frame the coefficient as a lower bound for cross-study comparison. Print all five category labels for the use item and its full frequency distribution, so the reported median category is defined and the distribution is reconstructable.
- **Acceptance criteria**: §3.2 or §4 states that outcome reliability is unestimable and that the interval excludes measurement-error uncertainty; the coefficient is described as a lower bound where it is compared with prior estimates; all five category labels and the response frequencies are reported.

**R10 — Name common-method variance and supply the available discriminant evidence**
Name shared-method / shared-self-report variance in §5 as a rival explanation for the *magnitude* of the association, distinct from the self-report-versus-log accuracy caution already cited. Report any procedural remedies used (item separation, differing response formats, counterbalancing). Supply the item-level correlation matrix, including each perceived-usefulness item against the use item, as the discriminant evidence obtainable from the existing data. Add the third-variable pathway to §5's alternative-explanation set, which currently contains reverse causation only. A behavioural criterion is out of scope for this resubmission and belongs in Future Research.
- **Acceptance criteria**: §5 names common-method variance as a rival explanation for the coefficient's magnitude and distinguishes it from the behavioural-accuracy caution; procedural remedies are reported or their absence stated; the item-level matrix including item-to-outcome correlations is supplied; §5's alternative set includes reverse causation, method artefact and the third-variable pathway.

**R11 — Correct the construct language and restore the scope bound**
Replace "engagement" with "self-reported access frequency" wherever frequency is what was measured — the abstract's closing sentence, §2, §4 and §7 — or, if the term is retained anywhere, state explicitly that it denotes reported access frequency only. Restore the single-institution qualifier to the abstract's closing sentence.
- **Acceptance criteria**: No occurrence of "engagement" in the abstract, §2, §4 or §7 refers to what the single frequency item measured without an explicit gloss; the abstract's closing sentence carries the single-institution bound stated in §6.

**R12 — Report the platform and its mandatory-use policy**
Name the LMS and its version. State whether it is the required channel for assignment submission, quiz delivery and grade release, and whether any course-level LMS activity was compulsory during the three-week survey window. Revise the §4, §5 and §7 interpretation to reflect what the answer implies about what the use item measures.
- **Acceptance criteria**: §3.1 or §3.2 names the platform and version and states its mandatory-use status for submission, quizzes and grade release, plus any compulsory activity in the survey window; §4, §5 and §7 interpret the outcome consistently with that disclosure.

**R13 — Supply the missing display material**
Provide the scatterplot whose inspection §3.4 reports as the basis for linearity, monotonicity, outlier and symmetry checks, plus a descriptives table covering both measures and the use item's category distribution. Currently a reader must accept four assumption checks on the authors' word.
- **Acceptance criteria**: The scatterplot referenced in §3.4 is included as a numbered figure; a descriptives table reports both measures and the full use-item distribution; each assumption check claimed in §3.4 is verifiable from the supplied display material.

---

# Part 2 — Revision Roadmap

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`s each item traces to, so decomposed granularity survives to the output boundary. Every item is keyed to a sub-claim; no `—` rows exist, because no item derives from a pre-decomposition bundle or from a DA-CRITICAL (the CRITICAL band is empty). **Severity and Priority are different axes**: Severity is transported verbatim from the driving finding; Priority is the synthesizer's arbitration of what gates resubmission. Where seats transported different bands for one sub-claim, the driving finding's band is shown and the range is noted.

## Required Revisions (Must Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| R1 | Resolve the reference base: verifiable records for all six sources, or replacement plus rebuild of every dependent claim | SC-1 | Critical (driving: R2 W1; eic W2 also Critical) | `text: References — "https://doi.org/10.5555/2050001", "https://doi.org/10.5555/2050006"` | 5 — registrant-prefix structure and first-hand venue knowledge | R2 Domain; Journal-Fit Reviewer | P1 | 3–5 days if the sources exist; unbounded if they do not |
| R2 | Reproduce the six item stems, document the adaptation, add in-sample structural evidence | SC-6, SC-7, SC-8 | Critical (driving: R1 W1; corroborating bands Major/Major/Minor) | `absence: §3.2 Measures and manuscript back matter — expected verbatim item wording, an explicit statement of what was changed from Costa and Wren (2019), and factor-structure evidence in the present sample; checked §3.2, §3.4, §4, §7, References, and the absence of any appendix` | 5 — routine instrument-documentation audit | R1 Methodology; R2; R3; Journal-Fit Reviewer | P1 | 3–5 days |
| R3 | Recategorise as Brief Report and replace the conceded contribution with an argued, benchmarked positioning claim | SC-5, SC-4, SC-3 | Major (driving: eic W1; R2 W3 Major; eic W5 Minor) | `text: §7 Conclusion — "offered as an incremental, design-bounded contribution rather than a causal claim"` | 5 — contribution-threshold calls are this seat's core caseload | Journal-Fit Reviewer; R2 Domain | P1 | 5–7 days (gated on R1) |
| R4 | Rebuild §2 around the canonical lineage; correct the misattributed construct definition | SC-2 | Major | `absence: §2 Literature Review — expected citation of the canonical perceived-usefulness source and of existing pooled LMS-acceptance estimates; checked §1, §2, §5, §7, and the reference list` | 5 — this is the seat's own lineage | R2 Domain | P1 | 7–10 days (gated on R1) |
| R5 | Reconcile §3.1 and §3.3: disclose the deduplication mechanism, identifier retention, and approval scope | SC-17 | Major (both seats Major) | `text: §3.3 — "No identifying information was collected, and responses could not be linked back to individual students."` + `text: §3.1 — "5 duplicate entries were removed"` | 4 (R1, survey-operations audit); 5 (R3, ethics-committee remit) | R1 Methodology; R3 Perspective | P1 | 1 day |
| R6 | Report eligible enrolment, invitations, response rate, and sample composition against institutional benchmarks | SC-18 | Major (driving: R1 W4; R3 W7 Major; eic W6 Minor) | `absence: §3.1 Design and participants — expected the enrolled undergraduate population size, a computed response rate, and the year-level distribution of the 214 analyzed cases against institutional benchmarks; checked §3.1, §3.3, §4, §6, and the Abstract` | 5 | R1 Methodology; R3; Journal-Fit Reviewer | P1 | 2–3 days |
| R7 | State whether the recruitment channel is LMS-hosted; reclassify selection on the outcome as a coefficient-validity threat | SC-19 | Major (both seats Major) | `text: §3.1 — "The survey was distributed through the institution's course-announcement channel"` + `text: §6 — "students who engage more with institutional channels may be overrepresented"` | 5 (R3, administers institutional survey distribution); 5 (R1) | R3 Perspective; R1 Methodology | P1 | 1 day |
| R8 | Ordinal-appropriate primary estimate with interval; Pearson/Spearman as sensitivity analyses with intervals; t, df; numeric R² | SC-11, SC-12 (A1-arbitrated), SC-22, SC-29 | Major (driving: R1 W3; SC-22 corroborated at Minor by eic/R2/R3) | `text: §3.4 — "Because the use item is ordinal, we also computed a Spearman correlation as a robustness check."` | 5 — standard ordinal-data estimation practice | R1 Methodology (SC-22 also eic, R2, R3 — CONSENSUS-4) | P1 | 2–3 days |
| R9 | Disclose that outcome reliability is unestimable and the interval excludes it; frame r as a lower bound; print all category labels and the distribution | SC-9, SC-10 | Major (both from R1 W2) | `text: §3.2 — "We treat this as an ordinal indicator of self-reported use and interpret it accordingly."` | 5 — classical attenuation theory applied to a single-indicator outcome | R1 Methodology | P1 | 1–2 days |
| R10 | Name common-method variance as a rival explanation for the magnitude; report procedural remedies; supply the item-level matrix; complete §5's alternative set | SC-14, SC-15 | Major (driving: R1 W8; R2 W4 Major) | `text: §2 — "studies relying on self-report capture perceived rather than actual engagement"` | 5 (R1); 4 (R2, cannot rule in or out without item wording) | R1 Methodology; R2 Domain | P1 | 2–3 days (partly gated on R2) |
| R11 | Replace "engagement" with self-reported access frequency in the abstract, §2, §4, §7; restore the single-institution bound | SC-16 (A2-arbitrated) | Major (driving: R3 W1; R2 W4 Major; R1 W9 Minor) | `text: Abstract — "perceived usefulness tracks with LMS engagement among undergraduates"` + `text: §4 — "reported engagement reflects many influences beyond perceived usefulness"` | 5 — manages the telemetry pipeline that produces institutional engagement metrics | R3 Perspective; R2; R1 | P1 | 0.5 day |
| R12 | Name the platform and version; state mandatory-use policy and any compulsory activity in the survey window; revise the interpretation | SC-25 | Major (both seats Major) | `absence: §3.1 and §3.2 — expected the platform identity and version plus the institution's mandatory-use policy for assignment submission and grade release; checked §1, §3, §4, §6` | 5 — standard reporting expectation in LMS-specific research | R2 Domain; R3 Perspective | P1 | 1 day |
| R13 | Supply the §3.4 scatterplot and a descriptives table including the use-item distribution | SC-20 | Major | `absence: §4 Results and §3.4 Analysis — expected at least one table or figure, including the scatterplot whose inspection is reported; checked §3.4, §4, all section bodies, and the reference list for any table or figure caption` | 5 — presence or absence of display material is directly observable | Journal-Fit Reviewer | P1 | 1–2 days |

## Suggested Revisions (Should Fix)

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| S1 | Add a fifth limitation naming unmeasured access/equity confounders (device, broadband, commuter status, paid-work hours); acknowledge in §5 that part of the association may be structural rather than attitudinal | SC-24 | Major | `absence: §6 Limitations — expected a named limitation for unmeasured confounders of access frequency (assessment schedules, timetable structure, notification settings, device and broadband access, commuter status, paid-work hours); checked §6 items one through four, §5 Discussion, the §4 Results parenthetical on course requirements, and §3.2 Measures` | 5 — this confounder set is what the seat's office controls for | R3 Perspective | P2 | 0.5 day |
| S2 | State in one sentence why institutional LMS logs were not used (approval scope, governance route, or feasibility within the window) | SC-13 | Minor | `absence: §3.1 Design and the §6 second limitation — expected a stated reason why institutional LMS access logs were not used or not obtainable; checked §3.1, §3.2, §3.3, §6, and the §7 future-research sentence` | 4 — operates the governance process that grants or denies such access | R3 Perspective | P2 | 0.5 day |
| S3 | Relabel the §3.4 statement as a sensitivity analysis, state whether any a priori target existed, correct the boundary to "approximately .80" | SC-26 (A3-arbitrated) | Minor | `text: §3.4 — "With n = 214, the study had greater than .80 power to detect a correlation of r >= .19"` | 5 — direct recomputation of the stated quantity | R1 Methodology (form upheld per R2 S2, R3 S3) | P2 | 0.5 day |
| S4 | Name statistical software and version; deposit the data or the cross-tabulation sufficient to recompute the coefficient | SC-21 | Minor (both seats Minor) | `absence: §3.4 Analysis and manuscript back matter — expected named statistical software with version, a data availability statement, and analysis code or a cross-tabulation sufficient to recompute the reported coefficient; checked §3.4, §4, §7, References, and the absence of any declarations section` | 5 | R1 Methodology; Journal-Fit Reviewer | P2 | 1 day |
| S5 | Either drop the §5 onboarding implication, or make it actionable (item-level perceived-usefulness responses identifying which functions students found useful), or state plainly that no institutional action follows from a single cross-sectional correlation | SC-23 | Minor (R3 W4); DA M3 records the stronger inferential-validity form at Major | `text: §5 — "LMS onboarding which helps students see concrete usefulness — rather than merely announcing that a platform exists — may be worth institutional attention"` | 5 — holds the onboarding budget line the implication would have to move | R3 Perspective (DA M3, off-count, conf 4) | P2 | 0.5–1 day |
| S6 | Label the §4 residual-variance attribution as conjecture or drop it — course requirements and assessment schedules were not measured | SC-27 | Minor (driving: R2 W7; R3 W3 transports Major) | `text: §4 — "consistent with the view that reported engagement reflects many influences beyond perceived usefulness, including course requirements and assessment schedules"` | 4 (R2); 5 (R3) | R2 Domain; R3 Perspective | P3 | 0.25 day |
| S7 | Add the venue declarations block: data availability, funding, competing interests (overlaps S4 on data availability) | SC-28 | Minor (both seats Minor) | `absence: manuscript front and back matter — expected data-availability, funding, and competing-interests declarations required by mainstream educational-technology venues; checked the title block, §3.3 Procedure and ethics, §7 Conclusion, and the References list` | 5 — submission-compliance screening | Journal-Fit Reviewer; R1 Methodology | P3 | 0.25 day |

> Transported metadata appears on every row above, not only on the three Top Blocking rows: each item carries the driving sub-claim's transported Severity, the finding's typed Evidence Anchor, and its per-finding Confidence. No `[SEVERITY-SOURCE: letter-fallback]` or `[CONFIDENCE-SOURCE: report-level]` tag is needed for any roadmap row — every current-format card carried a per-finding Severity and Confidence on the driving weakness. The only fallback tags in this package sit in the Step 1b inventory on the two `disputed` positions drawn from strength entries (`[CONFIDENCE-SOURCE: unavailable]` for R2 S2 and S5, which carry neither per-finding nor report-level confidence).

## Revision Checklist

### Priority 1 — Structural (estimated total: 27–39 days, sequential dependencies noted)
- [ ] R1: Resolve or replace all six references; rebuild every dependent claim **(gate — do this first)**
- [ ] R2: Appendix with six verbatim item stems + change log + in-sample structural evidence
- [ ] R3: Recategorise to Brief Report; argued, benchmarked positioning claim *(after R1)*
- [ ] R4: Rebuild §2 around the canonical lineage; correct the definition attribution *(after R1)*
- [ ] R5: Reconcile §3.1/§3.3; disclose deduplication mechanism and approval scope
- [ ] R6: Eligible enrolment, invitations, response rate, composition vs benchmarks
- [ ] R7: State whether the recruitment channel is LMS-hosted; reclassify the selection threat
- [ ] R8: Ordinal-appropriate primary estimate + intervals + t, df + numeric R²
- [ ] R9: Outcome-reliability disclosure; r as lower bound; category labels and distribution
- [ ] R10: Name common-method variance; item-level matrix; complete §5's alternative set *(after R2)*
- [ ] R11: "Engagement" → self-reported access frequency; restore the single-institution bound
- [ ] R12: Name the platform and mandatory-use policy; revise the interpretation
- [ ] R13: Scatterplot + descriptives table

### Priority 2 — Content supplementation (estimated total: 3–4 days)
- [ ] S1: Fifth limitation — access and equity confounders; structural-association acknowledgement in §5
- [ ] S2: One sentence on why logs were not used
- [ ] S3: Relabel the sensitivity statement; correct the boundary wording
- [ ] S4: Software and version; deposit data or cross-tabulation
- [ ] S5: Drop, ground, or plainly disclaim the onboarding implication

### Priority 3 — Text and reporting (estimated total: 0.5 day)
- [ ] S6: Label the §4 residual-variance attribution as conjecture, or remove it
- [ ] S7: Data-availability, funding and competing-interests declarations

## Deadline and routing

**No revision deadline applies.** This is a Reject, not a revision request: there is no re-review clock, and R1's outcome determines whether a resubmission is a matter of weeks or a matter of reconstruction. Two points on what happens next, stated precisely so that nothing here reads as a softened decision.

First, **the fired condition's action stands and is not downgraded.** Both seats who examined the references stated their finding conditionally — the domain seat: "If the authors can produce verifiable bibliographic records for all six — real DOIs, real volumes, retrievable PDFs — I would revise this judgement immediately and without complaint"; the Journal-Fit Reviewer: "If verification confirms these sources do not exist, that outcome overrides every dimension score on this panel, including mine." That conditionality is recorded because it tells the author exactly what the gate is. It does not reopen this decision. If the references resolve, the correct route is a **fresh submission assessed in a new round**, not a re-scored version of this one; the D1 and D6 blocks would still need R2 through R13 addressed on their own merits.

Second, **routing.** The Journal-Fit Reviewer's ruling, reached without a venue configuration string (see `[MISSING-INPUT]`, Part 0), is that after revision this belongs at a short-report venue as a **Brief Report**, and that no amount of rewriting makes it a full article at a high-volume educational-technology journal, because the fixes do not change the quantity of evidence. The alternative — retaining the full-article grade — requires new content, specifically behavioural log data alongside the self-report, or a second site. The field-analysis input supplied with this package names three candidate venues (*Education and Information Technologies*; *Research in Learning Technology*; *Journal of Information Technology Education: Research*) and recommends the second on design fit; I attribute those to the field analysis, not to any reviewer, and the Journal-Fit Reviewer expressly declined to invent the list. Treat them as leads to verify, not as an editorial endorsement.

## Response Letter Template

Use `templates/revision_response_template.md`. Respond to every R and S item individually, including items you decline. **R1 through R13 are not declinable** — they map to the three dimension blocks that produced this decision. For SC-12, SC-16 and SC-26, respond to the arbitrated outcome recorded in A1, A2 and A3 rather than to the raw reviewer positions.

## Machine-form Roadmap (Schema 7)

```json
{
  "schema": 7,
  "contract_id": "reviewer/reviewer_full/v2",
  "editorial_decision": "reject",
  "fired_conditions": ["F1", "F2", "F3", "F5"],
  "audit_verdict": "block(fatal)",
  "items": [
    {"id": "R1", "priority": "must_fix", "reviewer": ["domain", "eic"], "source_kind": "reviewer", "sub_claims": ["SC-1"], "severity": "critical", "confidence": 5, "evidence_anchor": "text: References — \"https://doi.org/10.5555/2050001\", \"https://doi.org/10.5555/2050006\"", "verification_criteria": "All six references resolve to retrievable records under registered publisher prefixes with matching venue, volume, issue and pages; no 10.5555 DOI remains; every claim in §2, §3.2, §5 and §7 is traceable to a resolvable source."},
    {"id": "R2", "priority": "must_fix", "reviewer": ["methodology", "domain", "perspective", "eic"], "source_kind": "reviewer", "sub_claims": ["SC-6", "SC-7", "SC-8"], "severity": "critical", "confidence": 5, "evidence_anchor": "absence: §3.2 Measures and manuscript back matter — expected verbatim item wording, an explicit statement of what was changed from Costa and Wren (2019), and factor-structure evidence in the present sample", "verification_criteria": "Appendix reproduces all six item stems verbatim; a change log against the source instrument is stated item by item; in-sample structural evidence (CFA or full item-level matrix) is reported; the abstract's validity claim matches the evidence for the adapted scale."},
    {"id": "R3", "priority": "must_fix", "reviewer": ["eic", "domain"], "source_kind": "reviewer", "sub_claims": ["SC-5", "SC-4", "SC-3"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §7 Conclusion — \"offered as an incremental, design-bounded contribution rather than a causal claim\"", "verification_criteria": "Submission category is Brief Report or Research Note; §2 and §5 state a numeric prior estimate or range with its heterogeneity; §7 locates r = .42 against that benchmark and names what a reader gains."},
    {"id": "R4", "priority": "must_fix", "reviewer": ["domain"], "source_kind": "reviewer", "sub_claims": ["SC-2"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §2 Literature Review — expected citation of the canonical perceived-usefulness source and of existing pooled LMS-acceptance estimates", "verification_criteria": "The perceived-usefulness definition is attributed to its canonical source; UTAUT-generation work and at least one LMS-acceptance synthesis are cited; §1's \"substantial body of work\" carries multiple citations."},
    {"id": "R5", "priority": "must_fix", "reviewer": ["methodology", "perspective"], "source_kind": "reviewer", "sub_claims": ["SC-17"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.3 — \"No identifying information was collected, and responses could not be linked back to individual students.\"", "verification_criteria": "§3.3 accurately describes the collection condition given the mechanism disclosed in §3.1; the deduplication mechanism and any identifier retention are stated; the approval scope matches what was collected."},
    {"id": "R6", "priority": "must_fix", "reviewer": ["methodology", "perspective", "eic"], "source_kind": "reviewer", "sub_claims": ["SC-18"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §3.1 Design and participants — expected the enrolled undergraduate population size, a computed response rate, and the year-level distribution against institutional benchmarks", "verification_criteria": "§3.1 reports eligible enrolment, invitations delivered and a computed response rate; the year-level distribution appears with an institutional comparison."},
    {"id": "R7", "priority": "must_fix", "reviewer": ["perspective", "methodology"], "source_kind": "reviewer", "sub_claims": ["SC-19"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.1 — \"The survey was distributed through the institution's course-announcement channel\"", "verification_criteria": "§3.1 states whether the recruitment channel is LMS-hosted; §5 addresses selection on the outcome as a validity threat with a stated likely direction; §6 no longer files it as generalisability only."},
    {"id": "R8", "priority": "must_fix", "reviewer": ["methodology", "eic", "domain", "perspective"], "source_kind": "reviewer", "sub_claims": ["SC-11", "SC-12", "SC-22", "SC-29"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.4 — \"Because the use item is ordinal, we also computed a Spearman correlation as a robustness check.\"", "verification_criteria": "An ordinal-appropriate coefficient with an interval is the primary estimate; Pearson and Spearman appear as sensitivity analyses each with an interval; t and df accompany the p value; R-squared is reported numerically; decimal precision is consistent across §4."},
    {"id": "R9", "priority": "must_fix", "reviewer": ["methodology"], "source_kind": "reviewer", "sub_claims": ["SC-9", "SC-10"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §3.2 — \"We treat this as an ordinal indicator of self-reported use and interpret it accordingly.\"", "verification_criteria": "§3.2 or §4 states that outcome reliability is unestimable and that the interval excludes measurement-error uncertainty; the coefficient is described as a lower bound where compared with prior estimates; all five category labels and the response frequencies are reported."},
    {"id": "R10", "priority": "must_fix", "reviewer": ["methodology", "domain"], "source_kind": "reviewer", "sub_claims": ["SC-14", "SC-15"], "severity": "major", "confidence": 5, "evidence_anchor": "text: §2 — \"studies relying on self-report capture perceived rather than actual engagement\"", "verification_criteria": "§5 names common-method variance as a rival explanation for the coefficient's magnitude and distinguishes it from the behavioural-accuracy caution; procedural remedies are reported or their absence stated; the item-level matrix including item-to-outcome correlations is supplied; §5's alternative set includes reverse causation, method artefact and the third-variable pathway."},
    {"id": "R11", "priority": "must_fix", "reviewer": ["perspective", "domain", "methodology"], "source_kind": "reviewer", "sub_claims": ["SC-16"], "severity": "major", "confidence": 5, "evidence_anchor": "text: Abstract — \"perceived usefulness tracks with LMS engagement among undergraduates\"", "verification_criteria": "No occurrence of \"engagement\" in the abstract, §2, §4 or §7 refers to the single frequency item without an explicit gloss; the abstract's closing sentence carries the single-institution bound."},
    {"id": "R12", "priority": "must_fix", "reviewer": ["domain", "perspective"], "source_kind": "reviewer", "sub_claims": ["SC-25"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §3.1 and §3.2 — expected the platform identity and version plus the institution's mandatory-use policy", "verification_criteria": "§3.1 or §3.2 names the platform and version and states its mandatory-use status for submission, quizzes and grade release, plus any compulsory activity in the survey window; §4, §5 and §7 interpret the outcome consistently."},
    {"id": "R13", "priority": "must_fix", "reviewer": ["eic"], "source_kind": "reviewer", "sub_claims": ["SC-20"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §4 Results and §3.4 Analysis — expected at least one table or figure, including the scatterplot whose inspection is reported", "verification_criteria": "The §3.4 scatterplot is included as a numbered figure; a descriptives table reports both measures and the full use-item distribution; each §3.4 assumption check is verifiable from the supplied display material."},
    {"id": "S1", "priority": "should_fix", "reviewer": ["perspective"], "source_kind": "reviewer", "sub_claims": ["SC-24"], "severity": "major", "confidence": 5, "evidence_anchor": "absence: §6 Limitations — expected a named limitation for unmeasured confounders of access frequency", "verification_criteria": "§6 names the unmeasured access and equity confounder class; §5 acknowledges that part of the association may be structural rather than attitudinal."},
    {"id": "S2", "priority": "should_fix", "reviewer": ["perspective"], "source_kind": "reviewer", "sub_claims": ["SC-13"], "severity": "minor", "confidence": 4, "evidence_anchor": "absence: §3.1 Design and the §6 second limitation — expected a stated reason why institutional LMS access logs were not used or not obtainable", "verification_criteria": "§3.1 or §6 states the actual reason logs were not used (approval scope, governance route, or feasibility within the window)."},
    {"id": "S3", "priority": "should_fix", "reviewer": ["methodology"], "source_kind": "reviewer", "sub_claims": ["SC-26"], "severity": "minor", "confidence": 5, "evidence_anchor": "text: §3.4 — \"With n = 214, the study had greater than .80 power to detect a correlation of r >= .19\"", "verification_criteria": "§3.4 labels the computation a sensitivity analysis, states whether an a priori target existed, and reads \"approximately .80\" at the stated boundary; the detectable-effect-floor framing is retained."},
    {"id": "S4", "priority": "should_fix", "reviewer": ["methodology", "eic"], "source_kind": "reviewer", "sub_claims": ["SC-21"], "severity": "minor", "confidence": 5, "evidence_anchor": "absence: §3.4 Analysis and manuscript back matter — expected named statistical software with version, a data availability statement, and analysis code or a cross-tabulation", "verification_criteria": "Statistical software and version are named; either the response-level data or the cross-tabulation sufficient to recompute the coefficient is deposited."},
    {"id": "S5", "priority": "should_fix", "reviewer": ["perspective"], "source_kind": "reviewer", "sub_claims": ["SC-23"], "severity": "minor", "confidence": 5, "evidence_anchor": "text: §5 — \"LMS onboarding which helps students see concrete usefulness — rather than merely announcing that a platform exists — may be worth institutional attention\"", "verification_criteria": "§5 either removes the onboarding implication, grounds it in item-level perceived-usefulness responses identifying which functions were found useful, or states plainly that no institutional action follows from a single cross-sectional correlation."},
    {"id": "S6", "priority": "nice_to_fix", "reviewer": ["domain", "perspective"], "source_kind": "reviewer", "sub_claims": ["SC-27"], "severity": "minor", "confidence": 4, "evidence_anchor": "text: §4 — \"consistent with the view that reported engagement reflects many influences beyond perceived usefulness, including course requirements and assessment schedules\"", "verification_criteria": "§4 either removes the attribution to unmeasured factors or labels it explicitly as conjecture the design cannot speak to."},
    {"id": "S7", "priority": "nice_to_fix", "reviewer": ["eic", "methodology"], "source_kind": "reviewer", "sub_claims": ["SC-28"], "severity": "minor", "confidence": 5, "evidence_anchor": "absence: manuscript front and back matter — expected data-availability, funding, and competing-interests declarations", "verification_criteria": "Data-availability, funding and competing-interests declarations are present in the manuscript's front or back matter."}
  ],
  "notes": {
    "editorial_channel_items": 0,
    "editorial_channel_note": "No item derives from an aggregated Minor Issues channel; every item traces to a typed finding with transported severity, evidence anchor and per-finding confidence, so source_kind is 'reviewer' throughout.",
    "gating": "R1 gates R3 and R4; R2 gates part of R10.",
    "out_of_scope_deferred": "Behavioural/log-based outcome measure and a second site are deferred to Future Research per the scope arbitration; no roadmap item requires new data collection."
  }
}
```

---

# Part 3 — Reviewer Report Summary (Appendix)

### Journal-Fit Review Report Summary (eic)
- Dimensions: D5 `warn`, D6 `block` (`repairable`) | Per-finding confidence 4–5 | No overall recommendation emitted
- Key point: this is a Brief Report, not a full article, and the category question is decided rather than left inside the verdict — the manuscript's honesty about its own scope is real but is doing work that contribution is supposed to do; separately, the reference apparatus is unresolvable and the seat declines to delegate that to production.

### Reviewer 1 (Methodology) Summary
- Dimensions: D1 `block` (`repairable`), D3 `warn` | Per-finding confidence 4–5 | No overall recommendation emitted
- Key point: the numbers are internally consistent — the interval, the case flow and the power figure all recompute — but the visible apparatus of precision is doing less inferential work than its presence implies, and the exposure instrument is documented at a level that does not let an independent analyst know what was correlated with what.

### Reviewer 2 (Domain) Summary
- Dimensions: D2 `block` (`fatal`) | Per-finding confidence 4–5 | Implied stance: "the remaining findings below would stand as a major revision", conditional on reference verification
- Key point: the six-source evidence base is unverifiable on structural grounds (one registrant prefix across six venues, sequential suffixes, a documentation-example prefix), and because §2, §3.2, §5 and §7 rest exclusively on it, the fix is reconstruction rather than revision; the seat names and then declines its own instinct to demand a larger paper.

### Reviewer 3 (Perspective) Summary
- Dimensions: D4 `warn` | Per-finding confidence 4–5 | Expressly defers the venue-fit question to the Journal-Fit Reviewer
- Key point: the manuscript's scope discipline is genuine and it teaches an outside reader how to read a single-site estimate, but the discipline lapses at exactly the sentences that travel furthest ("engagement" for weekly access frequency), and the §6 limitation list reads as exhaustive while omitting the access and equity confounders that plausibly drive both variables.

### Devil's Advocate Summary
- Dimensions: D3 `warn` | 0 CRITICAL, 6 MAJOR | Per-finding confidence 4–5
- Key point: the standard adversarial openings all failed — no inflated effect, no mismatched interval, no smuggled causal verb, no headline contradicting the results — and the paper instead fails on one recognisable pattern: a caution is named and then treated as discharged. The seat declined to manufacture a CRITICAL and stated its reasoning, which the synthesizer records as sound.
