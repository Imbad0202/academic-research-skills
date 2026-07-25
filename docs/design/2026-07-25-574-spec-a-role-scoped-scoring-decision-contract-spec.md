# #574 Spec A — Role-scoped scoring, abstention, and the canonical per-mode decision contract (design)

> Issue: #574 (umbrella), normative basis: the 2026-07-24 codex acceptance review adopted as
> the issue's normative overlay (rescope comment) — this spec implements overlay items
> **P0 gap 1** (role-scoped scoring + abstention), **P0 gap 2** (executable Phase 1→Phase 2
> conformance validation), **C3** (role semantics), **C5** (canonical per-mode decision
> contract), and — by the scope ruling in §2 — the **B1 residual** named by the E4
> re-measurement (seat-level severity-band anchoring).
> Status: design only — no code or prompt change ships with this document.
> Predecessors: `docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md` (Schema 13),
> `docs/design/2026-04-27-ars-v3.6.6-generator-evaluator-contract-design.md` (Schema 13.1),
> `docs/design/2026-07-15-510-panel-synthesis-checker-design.md` (executable checker),
> PR #581 (behavior batch A1/A2/A3/B1), PR #583 (E4 re-measurement on claude-opus-5).

## 1. Problem

Four strands, all evidenced in the shipped repo state and/or the E4 held-out measurements.

### 1.1 Role semantics are self-contradictory (C3 / P0 gap 1)

The sprint contract forces **every seat to score every dimension** (`shared/contracts/reviewer/full.json`
`panel_size: 5`; protocol §8 builds a length-N array per dimension), while the surrounding
role architecture says the opposite:

- `devils_advocate_reviewer_agent.md:26` (Phase Boundary MUST NOT): *"Score the paper — your
  job is to challenge, not score. Scoring is the other 4 reviewers' work."* The same file's
  Phase 2 protocol (`:77-88`) then **requires** the DA to emit `## Dimension Scores` for
  D1–D5 and an `## Editorial Decision`. This is a live self-contradiction inside one file.
- `eic_agent.md:12`: the EIC *"won't dive into methodological technical details (that's
  Reviewer 1's job)"* — yet its D1 (`methodology_rigor`) score carries the same weight as
  the methodology seat's in every quantifier.
- The synthesizer's general protocol counts consensus over **4 non-DA reviewers** with the DA
  handled separately, while its sprint protocol aggregates **5** seats; the same file says
  both "5 reviewer cards" (`:18,27`) and "4 review reports" (`:37,82-90`).

Consequence (overlay P0 gap 1): **a majority of non-specialists can override the actual
specialist** on the one dimension that specialist was configured for, and the DA's forced
scores on out-of-remit dimensions inject noise the panel arithmetic cannot distinguish from
signal.

### 1.2 The decision contract emits an invalid hybrid and has no Minor path (C5)

- `reviewer/full.json` F1 and `methodology_focus.json` F1 emit
  `editorial_decision=reject_or_major_revision` — a hybrid token that is **not a value of the
  Schema 6 `editorial_decision` enum** (`"Accept" / "Minor Revision" / "Major Revision" /
  "Reject"`, `shared/handoff_schemas.md` § Schema 6). Every E4 run that fired F1 emitted a
  decision no downstream schema accepts.
- **No shipped condition maps to `minor_revision`.** Worse, the zero-fired fallback is the
  accept-grade action: under `full.json`, a panel where one reviewer warns one mandatory
  dimension fires neither F0 nor F1/F2/F3 — and the round emits **accept**. A single
  `normal`-priority block (e.g. D5 writing) also falls through to accept. The E4 clean-control
  runs show the practical result of the missing Minor rung: 3 of the 4 opus-5 clean-control
  runs decided `reject_or_major_revision` (the fourth, post-#581 r1, reached
  `major_revision`) — a deliberately sound-at-its-scale control has no contract path to the
  Minor Revision a human editor would give it.
- Three scales coexist without a declared governor: 0–100 (`quality_rubrics.md` Decision
  Mapping: Minor ≥ 65), 1–5 (`editorial_decision_standards.md` §1: Minor ≥ 3.5 ⇒ ≈ 70), and
  `block|warn|pass` (sprint). #399 reconciled the score-trajectory surface to 0–100 but the
  fix never propagated to `editorial_decision_standards.md` — a recurrence, so the fix here
  must carry a defrift guard (overlay verification note).

### 1.3 Phase 1→Phase 2 conformance is promised but not executable (P0 gap 2)

`check_panel_synthesis.py` (#510) recomputes scores → fired conditions → decision, but nothing
executable validates that the two-phase discipline actually held: Phase 1 plan adequacy is a
prose lint the orchestrator "should" run (§4), the §5 "Phase 2 score must substring-match
Phase 1 trigger tokens" consistency check has no implementation, manuscript leakage into
Phase 1 has no detector (the E4 campaign found exactly this class: the superseded
single-context dispatch leaked manuscript content into "blind" Phase 1 plans), the
multi-dissent cap lives only in prompts, and A2's "Critical/Major must carry an adequate
anchor" has no machine check before synthesis.

### 1.4 Seat-level severity bands are unanchored (B1 residual, E4-measured)

The #581 behavior batch achieved A3's transport goal — post-change E4 runs show per-finding
tag coverage 0 → 100% on the non-DA formal registers and letter-fallback cells 4 → 0 — but
the frozen severity-agreement metric **regressed 0.663 → 0.536** because the four newly
tagged seats skew critical: post MS01-r1 the Domain seat tagged **7/7 findings critical** and
the EIC **8/9**, while DA-only agreement stayed flat-to-up (0.621 → 0.644). Five
expected-major defects were assessed critical, and SD-09 (expected minor) reached critical by
being bundled into a "numbers unreconstructible" narrative. The seats now *carry* severity;
nothing anchors *which band they pick*. This is the named B1 follow-up residual
(`evals/heldout/reviewer_seeded_defects/README.md`, 2026-07-25 post row).

## 2. Scope ruling: B1 seat-level severity-band anchoring is folded INTO Spec A

Decision: **fold in** (not a separate follow-up issue). Rationale:

1. **Same delivery surface.** Band anchoring must live inside the canonical Finding Contract
   block, which sits inside the delivered `### Phase 2 — Paper-visible review` subsection on
   all five seats (PR #581's load-bearing structural find: sprint runs inject ONLY that
   subsection as the reviewer's system prompt). Spec A already rewrites exactly those blocks
   for role-scoped scoring — two sequential PRs editing the same lint-pinned canonical
   literals means two rounds of witness churn for no benefit.
2. **Measurement economics.** Spec A's implementation is a reviewer-prompt change, so it must
   re-run the E4 protocol regardless (12-run two-condition fleets are the expensive step).
   Folding B1 in means one measurement campaign covers both.
3. **Attribution stays clean inside the batch.** Role scoping and the decision contract touch
   dimension *scores* and panel arithmetic; they do not touch per-finding severity tags. Any
   movement in the severity-agreement metric therefore attributes to the B1 anchoring change
   specifically, even inside the combined batch.
4. **The gate is currently failing.** Severity agreement is the one E4 gate the #581 batch
   failed (0.536 as frozen-measured). Deferring B1 means Spec A's own E4 gate run would be
   judged against the degraded number and the named regression stays open across yet another
   measurement cycle.

Mechanism in §11. The anchoring is designed to be compatible with the three documented keeps
(§19) — in particular it is a per-finding decision-impact test, never a distributional
target, so it does not reintroduce the base-rate anchors B1 removed.

## 3. Settled decisions

1. **Role scoping is contract-carried.** Each `acceptance_dimensions[]` entry gains
   `eligible_roles` (who may score it) and `owner_role` (the configured specialist,
   `owner_role ∈ eligible_roles`). Eligibility is data, not prose — the same contract JSON
   both phases already receive delivers it, and the checker enforces it (§4, §5).
2. **The DA scores exactly its remit dimension(s), not zero and not all.** In the shipped
   `full` contract the DA is eligible on D3 (`argumentative_coherence`) only — its documented
   DO list (logical consistency, evidence gaps, counter-arguments, data–conclusion mismatch)
   *is* D3. The alternative (DA fully non-scoring, panel arithmetic over 4 seats) was
   rejected: it would disconnect the panel's most band-stable seat (E4: DA-only agreement
   0.644, best of all twelve runs on MS02-r2) from the mechanical gate entirely, leaving
   DA input only on the prose adjudication channel. The `devils_advocate_reviewer_agent.md:26`
   MUST-NOT clause is reworded to match ("score only the dimension(s) the contract makes you
   eligible for; challenges remain your primary channel") — resolving the §1.1
   self-contradiction in the direction the contract actually needs (C3: role semantics
   resolved, not just wording).
3. **Findings are NOT role-scoped.** Any seat may still report any weakness with severity +
   anchor + confidence; role scoping governs formal dimension scores only. This preserves the
   cross-seat detection redundancy the E4 recall numbers depend on (SD-01 GRIM was caught by
   R1 AND the DA independently in both post replicates) and keeps the DA-CRITICAL
   adjudication channel intact. A methodology insight from the DA lands as a finding; it just
   no longer lands as a D1 score.
4. **Abstention (`not_assessed`) has two distinct forms.** *Structural*: an ineligible seat
   MUST mark `score: not_assessed` for that dimension (checker-enforced both directions —
   a real score from an ineligible seat is an out-of-role vote and fails the report).
   *Declared*: an eligible seat MAY abstain only with an explicit `abstain_reason:` naming a
   material-inapplicability basis; a dimension left with zero assessed eligible seats aborts
   the round loudly (`[DIMENSION-UNASSESSED]`) rather than silently passing (§5.3).
5. **Panel evaluation becomes two-stage (per-dimension verdicts first).** The v1 semantics —
   per-seat predicate over all dimensions, then a panel-level quantifier — is incompatible
   with role scoping (no seat is eligible on two mandatory dimensions, so v1's F2 could never
   fire). v2: `cross_reviewer_quantifier` applies **per dimension over that dimension's
   assessed eligible seats**; expressions quantify over the resulting dimension verdicts
   (§7). This is the overlay's "compute each denominator from eligible seats only",
   made precise.
6. **Per-seat `## Failure Condition Checks` and `## Editorial Decision` are dropped in v2.**
   Under role scoping a seat cannot evaluate conditions spanning dimensions it did not
   assess; a partial per-seat "decision" would be arithmetic theater. The integrity value the
   per-seat decision provided (catching narrative/score divergence) is replaced by a stronger
   executable signal: score-to-committed-trigger binding (§10). The panel decision has
   exactly one producer — the synthesizer — matching its "sole decision authority" role.
7. **`reject_or_major_revision` dies.** Schema 13.2's reviewer action enum drops it; the
   checker rejects it; the templates replace it with the fatal/repairable split (§8). The
   canonical output enum everywhere is exactly `Accept | Minor Revision | Major Revision |
   Reject` (sprint tokens `accept | minor_revision | major_revision | reject`, fixed total
   mapping).
8. **Fatality is pre-committed, not post-hoc.** Reject (vs Major Revision) on a blocked
   mandatory dimension turns on whether the flaw is fixable by revision. That judgment is
   made by the eligible seat AT SCORING TIME against a Phase-1 pre-committed
   `what_triggers_fatal` anchor (paper-blind, same anti-rationalization mechanism as
   block/warn triggers), never by the synthesizer interpretively (§8.1).
9. **Clean cut to v2 — no dual-grammar runtime.** Contracts for the two shipped reviewer
   modes MUST carry `eligible_roles` after this change; the v1 all-seats-score grammar is
   retired rather than kept as a parallel path. Keeping both would force every Phase 1/2
   subsection to carry conditional instructions ("if the contract has eligible_roles do X
   else Y") — permanent prompt weight and a drift surface — to preserve compatibility with
   frozen user copies that fail loudly (CONTRACT-INVALID) anyway. Writer/evaluator contracts
   are untouched (the v3.6.6 zero-touch promise holds for them; every new gate is
   reviewer-mode-conditional). Migration in §16.
10. **Executable conformance is a new per-seat checker**, `scripts/check_phase_conformance.py`,
    run at Phase-2 lint time per seat (like `--layer1-only`), importing shared parsing from
    `check_panel_synthesis.py` (reused, never forked). Five fail-closed check families:
    plan adequacy, manuscript leakage, trigger binding, dissent cap, anchor presence (§10).
11. **B1 anchoring is three rules inside the canonical Finding Contract block** (per-band
    decision-impact tests + per-finding anti-bundling + singleton-Critical test), with the
    expanded table in the report template for standard mode (§11).
12. **C5 gets one authority table** (§9) declaring, per mode, which decision engine and scale
    govern — pinned by a new defrift lint (§13) so the #399-class propagation failure cannot
    recur.
13. **Full mode gains a decision-bearing venue-fit dimension** (D6
    `venue_fit_and_contribution`, mandatory, EIC-owned; cross-model round-1 finding). The
    EIC's core remit was never expressible in the mechanical gate, and role scoping removes
    the informal escape valve (an EIC scope objection smuggled through another dimension's
    block) — without D6, a wholly out-of-scope paper that is otherwise sound mechanically
    Accepts. Methodology-focus deliberately does NOT gain it (§5.2). Grounding and
    fatal/repairable mapping in §5.1/§8.2.

## 4. Contract Schema 13.2

### 4.1 Additions

`acceptance_dimensions[]` items gain two properties:

```json
{
  "id": "D1",
  "name": "methodology_rigor",
  "description": "…",
  "priority": "mandatory",
  "eligible_roles": ["methodology"],
  "owner_role": "methodology"
}
```

- `eligible_roles`: array, `minItems: 1`, items from the closed role vocabulary
  `{"eic", "methodology", "domain", "perspective", "da"}`.
- `owner_role`: string from the same vocabulary. Declarative + downstream-operational:
  it documents the configured specialist, feeds the standard protocol's expertise-first
  arbitration, and is the routing artifact #576 (spec B) needs for re-review verification
  routing by source dimension. It has **no arithmetic role** in v2 panel evaluation
  (no owner-weighting — quantifiers treat eligible seats uniformly).

`measurement_procedure.scoring_plan_schema.required` gains a fifth canonical field
`what_triggers_fatal` (enum-constrained alongside the existing four; `minItems` 4 → 5).
Phase 1 scoring plans pre-commit the fatality anchor per eligible dimension (§8.1).

### 4.2 Conditional gates (new allOf branches)

- **Branch 13 (reviewer modes):** every `acceptance_dimensions[]` item requires
  `eligible_roles` + `owner_role`. This is what makes the cut "clean" at the schema layer —
  a v1 reviewer contract no longer validates. Writer/evaluator modes: no change (the
  properties are absent from their dimension items; `additionalProperties: false` on the
  dimension object is relaxed only by the two new named properties, which the branch makes
  reviewer-required and which writer/evaluator templates simply do not carry — presence in a
  writer contract is rejected by a validator hard invariant rather than a schema branch, to
  keep the branch count from doubling).
- **Branch 4 (reviewer action enum) revised:** drops
  `editorial_decision=reject_or_major_revision`. The four surviving tokens are the closed
  enum.

Validator (`check_sprint_contract.py`) hard invariants (errors, not SC warnings):

- `owner_role ∈ eligible_roles` per dimension.
- `eligible_roles ⊆ ROLE_SETS[mode]` per dimension (mode-subset can't be expressed cheaply
  in the schema; it is a hard invariant here and a CONTRACT-INVALID in the checker).
- All-or-none is moot under branch 13 (all reviewer dimensions carry the fields), but the
  validator still rejects `eligible_roles` / `owner_role` on writer/evaluator contracts.
- Every role in `ROLE_SETS[mode]` is eligible on ≥ 1 dimension (a seat with zero scoring
  duties would make its Phase-1 scoring plan empty; if a future contract genuinely wants a
  non-scoring seat, that is a deliberate schema revision, not a silent state).

New SC warnings: SC-12 — a `mandatory` dimension with `len(eligible_roles) == 1` is flagged
informationally (single-judge mandatory gate; accepted in the shipped templates, see §5,
but a contract author should choose it consciously).

## 5. Role–dimension eligibility maps (shipped templates v2)

Grounded in each agent's documented remit (Role & Identity + DO/DON'T lists):

### 5.1 `reviewer/full.json` → `reviewer/reviewer_full/v2`

| Dim | Name | Priority | eligible_roles | owner | Grounding |
|-----|------|----------|----------------|-------|-----------|
| D1 | methodology_rigor | mandatory | `[methodology]` | methodology | EIC disclaims method detail (`eic_agent.md:12`); DA disclaims methodology design (`Does NOT Do`); R2/R3 disclaim explicitly |
| D2 | domain_accuracy | mandatory | `[domain]` | domain | R1/R3 explicitly route literature/domain accuracy to R2; EIC/DA have no domain-accuracy remit |
| D3 | argumentative_coherence | mandatory | `[da, methodology]` | da | DA's DO list IS D3 (logic chain, evidence gaps, counter-arguments, data–conclusion mismatch); methodology's "are the conclusions supported by data?" overlaps on inference validity — two eligible seats keep the one DA-owned mandatory gate redundant |
| D4 | cross_disciplinary_relevance | high | `[perspective]` | perspective | R1/R2 explicitly route cross-disciplinary impact to R3 |
| D5 | writing_and_structure | normal | `[eic]` | eic | EIC's structural-coherence + venue-convention + readership steps are D5's definition |
| D6 | venue_fit_and_contribution | mandatory | `[eic]` | eic | NEW dimension — the EIC's core remit (journal fit, originality, significance) was never decision-bearing: no v1 dimension expresses it, and under role scoping the EIC loses the informal valve of expressing a scope objection through a D1–D4 block. Without it, a sound, coherent, well-written but wholly out-of-scope paper passes every dimension and F0 mechanically emits Accept, while the decision standards define Reject — Out of Scope as a first-class outcome. Fatality carries the subtype: a repairable D6 block (fit recoverable by reframing/repositioning) drives Major Revision via F2; a fatal D6 block (topic outside scope no revision can cure — the standards' "even with revision" bar) drives Reject via F1 |

### 5.2 `methodology_focus.json` → `reviewer/reviewer_methodology_focus/v2`

| Dim | Name | Priority | eligible_roles | owner |
|-----|------|----------|----------------|-------|
| D1 | methodology_rigor | mandatory | `[methodology]` | methodology |
| D2 | writing_and_structure | normal | `[eic]` | eic |

Note the design consequence: in v2 the EIC no longer scores D1 in methodology-focus mode —
which is exactly what its own role definition says it should not have been doing. The EIC
seat still reviews the whole paper and reports findings on anything (decision 3).
Methodology-focus deliberately carries NO venue-fit dimension: it is a focused methods
gate the user invokes for methodology verification, not an editorial fitness decision —
its output speaks to methods and presentation only (the §9 authority table row states
this scope).

D6 design notes (full mode): eligibility is deliberately EIC-only. The domain seat's
"is the contribution genuine and incremental" remit overlaps the contribution half, but
venue fit is exclusively editorial — a mixed eligible set would let a venue-blind seat
outvote the one seat configured with the venue identity. The domain seat's contribution
judgment still reaches the decision through its D2 score and its findings. Adding D6
keeps the overlay's venue-aware separation intact: venue mismatch drives the decision
through its OWN dimension with the Out-of-Scope subtype, never by mislabeling sound
science as a D1–D3 failure.

`panel_size` is unchanged (5 / 2): it remains the cardinality invariant (all seats run, all
produce cards, `[PANEL-SHRUNK]` semantics untouched). Eligibility narrows who *scores*, not
who *reviews*.

### 5.3 Abstention semantics

- **Ineligible seat**: `score: not_assessed`, nothing else (no reason line — it is
  structural). A real score here is an out-of-role vote → report fails (exit 3).
- **Eligible seat**: normally MUST score. May emit `score: not_assessed` +
  `abstain_reason: <one line>` only for material inapplicability (e.g. a methods dimension
  against a paper with no empirical component — note the methodology agent's existing
  special-handling guidance maps theory papers to argumentation-rigor assessment, so this
  path is expected to be rare). Missing `abstain_reason` → exit 3.
- **Zero-assessed dimension**: if every eligible seat abstained, the panel cannot evaluate
  any condition scoped over that dimension. The checker emits
  `[DIMENSION-UNASSESSED: <Dn>]` and the round aborts (orchestrator treats it like
  `[PANEL-SHRUNK]`). Fail-closed by design: a contract whose dimensions don't fit the paper
  should bounce to the user for a different mode/contract, never silently pass.

## 6. Reviewer output grammar v2

### 6.1 Phase 1 (paper-content-blind)

- `## Contract Paraphrase`: unchanged — one paragraph per dimension, ALL dimensions
  (understanding the whole contract is blind-safe and keeps the seat able to *report
  findings* everywhere).
- `## Scoring Plan`: one `### <Dn>: <name>` subsection **per eligible dimension only**, each
  carrying the five committed fields (`dimension_id`, `what_to_look_for`,
  `what_triggers_block`, `what_triggers_warn`, `what_triggers_fatal`). A scoring-plan
  subsection for an ineligible dimension is a Phase-1 lint failure (it would manufacture the
  out-of-role vote's paper trail).
- `[CONTRACT-ACKNOWLEDGED]` terminal tag: unchanged.

### 6.2 Phase 2 (paper-visible)

Per-dimension subsections cover ALL contract dimensions (explicit `not_assessed` is a cheap
witness that the seat knows its role — silence would be indistinguishable from parser loss):

```
contract_role: methodology

## Dimension Scores

### D1: methodology_rigor
score: block
block_class: repairable
trigger: "reported df cannot be produced by any integer sample allocation"

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: warn
trigger: "conclusion generalizes beyond the sampled population without a stated limitation"

…

## Review Body
…
```

Grammar rules (machine-parsed, anchored full lines, fenced code stripped — same parsing
discipline as #510):

- `score: <block|warn|pass|not_assessed>` exactly once per subsection.
- `block_class: <fatal|repairable>` REQUIRED iff `score: block`; forbidden otherwise.
- `trigger: "<text>"` REQUIRED iff `score ∈ {block, warn}`; the quoted text must be a
  verbatim substring (after whitespace normalization) of that seat's Phase-1
  `what_triggers_block` / `what_triggers_warn` / `what_triggers_fatal` (matching the score:
  block-class fatal binds to the fatal trigger) for that dimension (§10.3). Forbidden for
  `pass` / `not_assessed`.
- `abstain_reason: <text>` REQUIRED iff `not_assessed` by an ELIGIBLE seat; forbidden
  otherwise.
- `## Scoring Plan Dissent` unchanged (one-dimension cap, retry-from-Phase-1 on multi-dissent);
  a dissented dimension is exempt from trigger binding — the dissent entry itself must name
  the dimension and the override rationale, and only that one dimension is exempt.
- `## Failure Condition Checks` and `## Editorial Decision` are REMOVED (decision 6). Their
  presence in a v2 report is a grammar failure (loud, not tolerated — prevents a stale
  prompt from half-running v1).
- `## Review Body` unchanged as a section; its Critical/Major findings acquire an executable
  anchor check (§10.5).

### 6.3 Synthesizer emission block v2

Exactly one of each pinned line:

```
dimension_verdicts: [D1=block(fatal), D2=pass, D3=warn, D4=pass, D5=pass, D6=pass]
fired_conditions: [F1, F2, F5]
editorial_decision=reject
```

The `dimension_verdicts` line is new — an **audit artifact**, defined as the worst score
among the dimension's assessed eligible seats (`pass < warn < block`), carrying the
`(fatal)` flag when any of those seats declared a fatal block. Verdict tokens:
`pass | warn | block | block(fatal)`. The checker recomputes and verifies this line, but
conditions are NEVER evaluated from it — condition evaluation always runs from the seat
scores directly with each condition's own quantifier (§7), because two conditions with
different quantifiers legitimately see the same dimension differently (on a two-eligible
dimension, `any` fires on one blocking seat while `majority` needs both). The line exists so
a human reading the synthesis can see the aggregation layer at a glance and the checker can
pin it; it is not a second decision input.

## 7. Panel evaluation semantics v2

Two-stage, replacing the v1 per-seat-predicate → panel-quantifier pipeline:

**Stage A — per-dimension seat indicators.** For a condition atom over dimension d with score
threshold t: each assessed eligible seat i yields `indicator_i(d, t)`. Comparisons use the
order `pass(0) < warn(1) < block(2)`; `block_class: fatal` is a flag on `block`, not a fourth
rung — the atom "scores 'block'" matches a fatal block too; the fatal atom (§7.1) matches
only flagged blocks. Abstained/ineligible seats are absent from both numerator and
denominator.

**Stage B — quantifier per dimension, then dimension counting.** The condition's
`cross_reviewer_quantifier` is applied to `{indicator_i(d, t)}` over d's assessed eligible
seats, producing a boolean per dimension; the expression's dimension quantifier ("any … / two
or more … / every …") then evaluates over those booleans.

Quantifier thresholds over n = assessed eligible seats of the dimension:

- `any`: ≥ 1. `all`: n. `majority`: `⌊n/2⌋ + 1` for n ≥ 3; both for n = 2; **the seat itself
  for n = 1**. The v1 `n == 1 ⇒ never fires` vacuity rule (#531) is deliberately NOT carried
  into per-dimension evaluation: v1's rule guarded the degenerate `panel_size: 1` contract,
  while a single-eligible-seat dimension is a designed owner-decides case — a vacuous
  majority there would make every owner-only mandatory gate unfireable (fail-open). The
  SC-11 `panel_size: 1` warning itself is unchanged.

### 7.1 Expression vocabulary v2 (§9 lockstep)

The five recognised patterns keep their surface strings, re-read under the two-stage
semantics above, plus **four new atom forms** (6–9). The additions exist because the §8.2
v2 condition sets use them — without them the shipped templates would abort with
`[EXPRESSION-UNRECOGNISED]` on their own conditions:

6. **Fatal block:** `any <priority> dimension has a fatal block` |
   `<Dn> has a fatal block`
7. **Unscoped any + threshold:** `any dimension scores '<score>' or worse`
   (no priority scope = ranges over ALL contract dimensions; ordered comparison
   `pass < warn < block`)
8. **Dimension-literal threshold:** `<Dn> scores '<score>' or worse`
9. **Unscoped universal:** `every dimension scores '<score>'`
   (no priority scope = all contract dimensions)

Protocol §9, the synthesizer prompt's recognised-pattern list, and the checker's expression
grammar update **in lockstep in the same PR** (standing §9 rule; patterns 6–9 follow the
protocol's existing closed-vocabulary extension route). The semantic shift of
patterns 1–5 (per-dimension verdicts instead of per-seat multi-dimension predicates) is
called out explicitly in §9's text — it is a deliberate breaking reinterpretation, required
because per-seat predicates are undefined under role scoping (§3 decision 5).

## 8. Decision contract v2 (C5)

### 8.1 Repairable vs fatal blocks

A `block` on a mandatory dimension is Major Revision when the flaw is fixable by revision and
Reject when it is not (`editorial_decision_standards.md`: Reject = "fundamental unfixable
issues"). v2 makes that boundary **pre-committed and seat-owned**:

- Phase 1: each eligible seat commits `what_triggers_fatal` per dimension — the evidence
  pattern that would make the dimension's failure unfixable-by-revision (e.g. for D1: "the
  design cannot answer the RQ even in principle; no reanalysis of the collected data can
  recover validity"). Committed paper-blind, same anti-rationalization mechanism as
  block/warn triggers.
- Phase 2: `score: block` carries `block_class: fatal` only when the fatal trigger fired, and
  the `trigger:` line must bind to the committed fatal trigger text.
- The synthesizer/checker aggregate fatality with the condition's quantifier like any other
  indicator (§7); no interpretive fixability judgment ever happens at synthesis
  ("arithmetic, not interpretive" preserved).

### 8.2 Shipped condition sets v2

`reviewer/reviewer_full/v2`:

| id | sev | quantifier | expression | action |
|----|-----|-----------|------------|--------|
| F1 | 95 | any | any mandatory dimension has a fatal block | reject |
| F2 | 90 | any | any mandatory dimension scores 'block' | major_revision |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | major_revision |
| F4 | 60 | any | any high-priority dimension scores 'block' | major_revision |
| F5 | 40 | any | any dimension scores 'warn' or worse | minor_revision |
| F0 | 10 | all | every dimension scores 'pass' | accept |

`reviewer/reviewer_methodology_focus/v2`:

| id | sev | quantifier | expression | action |
|----|-----|-----------|------------|--------|
| F1 | 95 | any | D1 has a fatal block | reject |
| F2 | 90 | any | D1 scores 'block' | major_revision |
| F3 | 70 | any | D1 scores 'warn' | major_revision |
| F4 | 40 | any | D2 scores 'warn' or worse | minor_revision |
| F0 | 10 | all | every dimension scores 'pass' | accept |

Design notes:

- **The Minor path exists and the fall-through dies.** F5/F4(mf) catch every single-warn and
  every normal-priority defect; F0's scope widens from "every mandatory" to "every
  dimension". Consequence: the condition set is **exhaustive** — for any assignment of panel
  verdicts, at least one condition fires (all-pass ⇒ F0; otherwise some dimension is
  warn-or-worse ⇒ F5). The zero-fired accept fallback (protocol §8 step 3 / checker
  `accept_grade_action`) becomes provably unreachable for the shipped templates; it is
  retained in the engine as belt-and-suspenders for custom contracts, and the test suite
  proves unreachability for the shipped ones by enumeration (§15).
- **The conditions are priority-scoped, so D6 rides them without new entries**: a fatal D6
  block hits F1 (reject — the Out-of-Scope subtype), a repairable one hits F2, its warns
  count toward F3/F5, and F0's accept now REQUIRES the venue-fit dimension to pass —
  Accept mechanically certifies fit, matching the standards' Accept criteria.
- **methodology-focus stays deliberately stricter** (sole-mandatory warn ⇒ major_revision,
  preserving v1's intent for a methods-gate mode), while full mode's single-mandatory-warn ⇒
  minor_revision replaces v1's accept fall-through. Both are strict improvements toward the
  overlay's "repairable versus fatal blocks defined and exhaustively tested".
- A normal-priority block (D5 writing) lands Minor Revision — consistent with the decision
  standards' "poor writing quality does not affect the academic decision, but require
  language revision".
- Severity values keep gaps (95/90/70/60/40/10) for future insertions; ties remain
  ordinal-position-broken (unchanged engine rule).

### 8.3 Canonical decision tokens

Sprint tokens ↔ Schema 6 enum, fixed total mapping, single-sourced:

`accept → "Accept"`, `minor_revision → "Minor Revision"`, `major_revision → "Major
Revision"`, `reject → "Reject"`. The hybrid token is removed from: schema branch 4, checker
`ACTION_ENUM`, both templates, protocol §9 examples, and every live prose surface (negative
witness in §13; historical surfaces — CHANGELOG, design docs, committed E4 run records — are
out of the witness's scope on purpose: they are records, not rules).

## 9. Canonical per-mode decision authority table (C5)

New authority section at the TOP of `references/editorial_decision_standards.md` (§0), with
SKILL.md and the sprint protocol pointing at it:

| Mode | Decision engine | Working scale | Output |
|------|-----------------|---------------|--------|
| `full` (sprint contract) | mechanical synthesizer over contract v2 (§7–§8); the recommendation matrix and rubric mapping NEVER override it | `block/warn/pass` + `block_class` | four-value enum |
| `methodology-focus` (sprint contract) | same | same | four-value enum — scoped to methods + presentation; carries no venue-fit dimension by design |
| `full`/`methodology-focus` without a contract (legacy standard protocol) | Synthesis Protocol Steps 1–4 + decision matrix + arbitration (this file §§1–2) | reviewer recommendations (four-value) | four-value enum |
| `re-review` | #576 scope (spec B); until then `re_review_mode_protocol.md` governs | — | four-value enum |
| `quick` | EIC assessment only; explicitly NOT an editorial decision (advisory signal) | — | signal, not a decision letter |
| `guided` | no editorial decision letter (issue-list dialogue) | — | — |
| `calibration` | rubric 0–100 → `quality_rubrics.md` Decision Mapping, measurement-only | 0–100 | four-value labels vs gold set |

Single-sourcing repairs in the same PR:

- `editorial_decision_standards.md` §1's 1–5 numeric criteria (avg ≥ 4.0 / ≥ 3.5 / 2.5–3.4 /
  < 2.5) are **removed**; the section keeps its qualitative criteria + reviewer-recommendation
  counts and points numeric thresholds at `quality_rubrics.md`'s 0–100 Decision Mapping — the
  scale #399 already established as canonical. §3's "Cross-Dimension Decision Impact" table
  rows re-key from "R1 score = 1" (1–5 residue) to descriptor language.
- The under-a-contract governor sentence ("the mechanical synthesizer governs; the matrix is
  the no-contract path") is stated in §0 and mirrored where the matrix lives.
- Defrift guard: §13's lint pins the four-token enum across all surfaces AND pins the numeric
  thresholds' single residency in `quality_rubrics.md` (the 1–5 recurrence class the overlay
  flagged).

## 10. Executable Phase 1→Phase 2 conformance (P0 gap 2)

New `scripts/check_phase_conformance.py`, per-seat:

```
python scripts/check_phase_conformance.py --contract C.json --role <role> \
    --phase1 <seat>.phase1.md --phase2 <seat>.phase2.md --manuscript m.md
```

`--role` and `--manuscript` are both REQUIRED. `--role` is the dispatch-assigned role
(the orchestrator knows which seat it invoked); the checker fails (exit 3) unless it
equals the report's self-declared `contract_role` line — otherwise two swapped reports
could each have their out-of-role scores accepted under the other's eligibility while
the panel-level role-set check still passes. `--manuscript` omission is exit 2
(infra), never a silent skip — an optional flag would let the leakage family (check 2)
be disabled by invocation shape, contradicting the fail-closed posture (§14).

Exit codes: 0 pass / 2 contract-infra / 3 conformance failure (⇒ that reviewer unusable,
protocol §5 class). Shares the contract loader and markdown parsing helpers with
`check_panel_synthesis.py` by import (reused, never forked). Six check families, all
fail-closed:

0. **Role binding.** `--role` ∈ `ROLE_SETS[mode]` (else exit 2) and equals the report's
   `contract_role` (else exit 3). `check_panel_synthesis.py` gains the panel-side
   counterpart: an optional `--roles r1,...,rN` list positionally matched to the
   `--report` order; when provided, any mismatch with a report's `contract_role` is
   exit 3 — the orchestrator MUST provide it in operational runs (protocol §5 wiring).

1. **Plan adequacy (Phase 1).** Per eligible dimension: all five committed fields present and
   non-empty; `what_triggers_block` ≠ `what_triggers_warn` ≠ `what_triggers_fatal` as
   normalized strings (a copy-pasted identical trigger set is not a plan). Advisory (warning,
   not failure): any trigger under 8 words. Deeper semantic adequacy (are the triggers
   concrete and discriminating?) remains the documented judge-layer limitation — this floor
   is deterministic on purpose.
2. **Manuscript leakage (Phase 1).** Every 12-word shingle (whitespace-normalized,
   case-folded) of the manuscript body is literal-searched in the Phase 1 output; any hit
   that does not also occur in the contract JSON or the metadata (title/field) fails the
   seat. This is the executable form of the E4 campaign's single-context-leak lesson;
   12 words is conservative against idiom collisions, and literal containment (no regex
   over manuscript text) keeps it injection- and ReDoS-inert. The manuscript input is
   mandatory (see the CLI contract above), so this family cannot be skipped by
   invocation shape.
3. **Trigger binding (Phase 2).** Every `trigger:` line's quoted text must be a verbatim
   substring (whitespace-normalized) of the SAME seat's Phase-1 committed trigger of the
   matching kind for that dimension. Score without a trigger line, trigger text absent from
   the commitment, or kind mismatch (e.g. a fatal block binding to the warn trigger) = silent
   trigger drift → fail. Dissent exemption: exactly the one dimension named in
   `## Scoring Plan Dissent`.
4. **Dissent cap.** ≥ 2 dissent dimensions → fail (the prompt/orchestrator rule becomes
   machine-checked).
5. **Anchor presence (Phase 2 Review Body).** Role-aware, matching the two committed
   report grammars: for the four scoring seats, every finding whose `**Severity**:` is
   Critical or Major must carry an `**Evidence Anchor**:` field with a valid type token
   (`text|table|figure|equation|dataset|absence`); for `role=da`, findings live as table
   rows under the `#### CRITICAL` / `#### MAJOR` issue-table headings (severity is the
   section band, anchors are the `Evidence Anchor` column), so the checker parses those
   tables and fails any CRITICAL/MAJOR row whose anchor cell is empty or carries no valid
   type token. In both grammars: `text` anchors must contain a quoted string of ≤ 25
   words; `absence` anchors must name checked surfaces (non-empty tail after the type
   token). Minor findings: advisory only. (The Finding Contract's prose rule gets a
   machine gate at the same boundary that feeds synthesis.)

Orchestrator wiring: protocol §5 gains "run `check_phase_conformance.py` per seat before
handoff to the synthesizer; exit 3 ⇒ `[PROTOCOL-VIOLATION: phase_conformance=<check>]`, seat
unusable". Missing Phase-1 artifact is exit 2 (infra) — the check cannot be skipped into a
pass.

`check_panel_synthesis.py` upgrades in the same PR: v2 report grammar (`not_assessed`,
`block_class`, `trigger`/`abstain_reason` lines; per-seat decision sections rejected),
eligibility cross-check (out-of-role real score → exit 3; this is the overlay's
"mutation-test that out-of-role votes are rejected or excluded" — both: rejected at parse,
and provably excluded from arithmetic by the denominator tests), two-stage Stage A/B
recomputation, `dimension_verdicts:` line verification, fatal atoms, and
`[DIMENSION-UNASSESSED]`.

## 11. B1 — seat-level severity-band anchoring

Three rules, added INSIDE the canonical Finding Contract block (delivered surface, all five
seats — compact form), with the expanded table in
`templates/peer_review_report_template.md` § Severity Levels (standard mode):

1. **Per-band decision-impact tests** (seat-neutral generalization of the DA's existing
   "What Constitutes a CRITICAL Finding" gate):
   - **Critical** — this single defect, uncorrected, invalidates the paper's core claim or
     makes acceptance impossible; test: *would this finding alone justify `block` on a
     mandatory dimension?*
   - **Major** — materially weakens confidence in a core claim; substantial revision
     required; the core survives; test: *does this finding alone require re-analysis,
     rewriting, or new data — without invalidating the core?*
   - **Minor** — quality/clarity improvement; core claims unaffected.
2. **Per-finding, never per-narrative (anti-bundling).** A finding takes the band its OWN
   decision impact justifies — it never inherits the band of the narrative or defect cluster
   it contributes to. (E4 exemplar: SD-09, an expected-minor reporting-granularity issue,
   reached critical only by being folded into a "numbers unreconstructible" storyline.)
   If several findings jointly reach a higher impact, that is the DIMENSION SCORE's and the
   synthesizer's job to express — not a promotion of each member finding.
3. **Singleton-Critical test.** If the defect needs siblings to reach rejection-level
   impact, it is not Critical alone.

Keep-compatibility (bridges, mirroring the #581 discipline): these are **per-finding
decision-impact tests, never distributional targets** — no expected band frequencies, no
"most findings should be Major", nothing the Decision Symmetry section forbids. They
compose with (not replace) the existing sentence "severity is assigned by decision impact
alone; register never moves a band" — they operationalize *which* band that impact selects.
The DA's own CRITICAL-criteria section stays; its four criteria are the D3-flavored instance
of test 1 and remain the DA's stricter local gate.

Acceptance instrument: the E4 severity-agreement metric under the frozen highest-tagged-seat
ladder (§17). Expected direction: non-DA tag distributions de-skew (the 7/7-critical Domain
pattern), agreement recovers toward/above the 0.663 same-model pre-batch mark. The gate
itself remains "does not regress vs the operative baseline"; the recovery target is the
measured intent, not a promised number.

## 12. Delivery-surface map (which rule lives where)

Premise (structural, from #581 round 2): sprint runs inject ONLY the `### Phase 1 …` /
`### Phase 2 — Paper-visible review` subsections as the seat's system prompt; the contract
JSON rides user content in both phases. A rule placed anywhere else in the agent file is
NOT delivered to sprint runs.

| Rule | Delivered home | Also mirrored (non-delivered, doc/consistency) |
|------|----------------|-----------------------------------------------|
| Eligibility: score only eligible dims; `not_assessed` grammar; abstain_reason | `### Phase 2` subsection, all 5 agents (reads `eligible_roles` from the contract JSON in-context) | protocol §5 |
| Phase-1 plan scope (eligible dims only) + `what_triggers_fatal` | `### Phase 1` subsection, all 5 agents | protocol §4; schema |
| `block_class` + trigger-binding emission | `### Phase 2` subsection, all 5 agents | protocol §5; conformance checker |
| Removal of per-seat Failure Condition Checks / Editorial Decision | `### Phase 2` subsection, all 5 agents (steps 3–4 rewritten) | protocol §5; checker grammar |
| Finding Contract + B1 band anchors (compact) | inside `### Phase 2` subsection — canonical block, byte-identical across the 4 scoring agents; DA variant carries the same anchor sentences | template § Severity Levels (expanded table); lint owns the literals |
| Two-stage panel arithmetic + `dimension_verdicts` emission + fatal atoms | synthesizer's `## v3.6.2 Sprint Contract Synthesizer Protocol` section | protocol §8/§9; checker |
| DA role rewording (score-eligible-dims-only) | DA Phase Boundary MUST-NOT list + `### Phase 2` subsection | — |
| C5 authority table + governor sentence | `editorial_decision_standards.md` §0 | SKILL.md; protocol |
| C3 canonical wording (5 cards; 4-seat findings consensus; per-dimension score denominators) | synthesizer Core Mission / Step 1a / Step 2 | SKILL.md mode table |

Every "Delivered home" cell is a witness target in §13 — witnesses bind to the delivered
block (parent-bound under the `## v3.6.2 Sprint Contract Protocol` H2), never to file-level
presence (file-level = fail-open, per the #581 lesson).

## 13. Lint / witness plan

Threat model identical to the shipped reviewer lints (stated in each docstring): accidental
drift by well-intentioned edits — deletions, rewordings, relocations, re-spellings.
Adversarial repo editors are out of scope (anyone who can craft a pathological decoy can
equally edit the lint; terminal defense is human review of lint-file diffs).

1. **`check_reviewer_finding_contract.py` (extend).** The canonical Finding Contract literal
   grows the B1 anchor sentences — the lint OWNS the new string (hardcoded literal,
   parent-bound to the delivered Phase 2 subsection on all five seats). Template § Severity
   Levels gains pinned anchor-test rows. Every new file the lint reads joins the mutation
   test's `_mirror` list **in the same commit** (the #581 exit-2 lesson).
2. **New `check_role_scoped_contract.py`.** Witnesses, all hardcoded literals:
   - both v2 templates carry EXACTLY the §5 eligibility maps (expected mapping inlined in
     the lint, not read from a shared constant — non-self-referential per the defrift
     discipline);
   - the five Phase 2 subsections carry the `not_assessed` / `block_class` / `trigger:`
     grammar sentences (parent-bound);
   - the five Phase 1 subsections carry the eligible-dims-only scope sentence + the
     five-field commitment list;
   - protocol §9's pattern list, the synthesizer prompt's recognised-pattern list, and a
     hardcoded expected-pattern list in the lint agree (three-way lockstep witness);
   - the DA Phase-Boundary clause is the reworded form (the old "not to score" literal is a
     negative witness).
3. **Decision-enum parity + negative witness (C5 defrift guard), in the same new lint or a
   sibling `check_decision_contract.py`:**
   - the four sprint tokens and the four Schema 6 values agree across: schema branch 4,
     `check_panel_synthesis.py` `ACTION_ENUM`, both templates, `handoff_schemas.md` Schema 6,
     `editorial_decision_standards.md` §0, SKILL.md — hardcoded four-token list in the lint;
   - `reject_or_major_revision` appears NOWHERE on live rule surfaces
     (`academic-paper-reviewer/**`, `shared/contracts/reviewer/**`,
     `shared/sprint_contract.schema.json`, `shared/handoff_schemas.md`,
     `scripts/check_panel_synthesis.py`, `scripts/check_sprint_contract.py`, SKILL.md) —
     scope excludes `evals/` run records, `docs/design/`, `CHANGELOG.md`, and the lint/tests
     themselves (records and witnesses, not rules);
   - numeric decision thresholds (80/65/50) reside ONLY in `quality_rubrics.md`; the 1–5
     average-score criteria pattern is a negative witness on
     `editorial_decision_standards.md`.
4. **Mutation/inverse tests** (pytest, registered in the local manifest AND CI in the same
   commit — the v3.15 local-green/CI-red lesson): see §15.
5. **No new whole-file content locks.** The academic-pipeline CONTENT_LOCKS convention stays
   scoped to the five pipeline boundary files (none change here); reviewer surfaces use the
   sentence-pin + parent-bound witness style of the shipped reviewer lints. If any pipeline
   surface unexpectedly needs touching at implementation time, its pinned hash updates in the
   same commit (standing rule).

## 14. Threat model (design-level)

- **Well-intentioned drift** (primary): covered by §13 witnesses + mutation tests.
- **Runtime manuscript injection**: unchanged posture — the #578/#581 data fences
  (`<paper_content>`, `<phase1_output>`) are not modified; role scoping adds no new
  untrusted-input surface. The conformance checker READS the manuscript for the leakage
  check: it treats it as literal data (normalized substring containment only — no regex
  compiled from manuscript text, no eval), so a hostile manuscript cannot break the checker
  or smuggle instructions through it.
- **Seat gaming the binding**: a seat could pre-commit vacuous triggers in Phase 1 and bind
  trivially in Phase 2. The deterministic floor (§10.1) narrows this; genuine semantic
  adequacy remains the documented judge-layer limitation (unchanged from protocol §4's
  existing note). The binding still buys real integrity: the seat must decide its evidence
  bar before seeing the paper and must cite which bar fired — silent post-hoc re-standarding
  becomes machine-visible.
- **Fail-open via absence**: every conditional grammar element is required-iff (missing
  `block_class` on a block, missing `trigger` on warn/block, missing `abstain_reason` on
  eligible abstention are all failures); a zero-assessed dimension aborts; a missing Phase-1
  artifact is infra-failure, never a skip.

## 15. Tests

Mutation/inverse suites, hardcoded expectations throughout:

1. **Schema/validator**: v2 templates validate; a reviewer contract without
   `eligible_roles`/`owner_role` fails branch 13; `owner_role ∉ eligible_roles` fails;
   `eligible_roles ⊄ ROLE_SETS[mode]` fails; the hybrid action fails branch 4; writer /
   evaluator shipped templates still validate byte-identically (zero-touch regression pair).
2. **Checker (panel arithmetic)**: out-of-role real score → exit 3; ineligible-seat
   `not_assessed` accepted; eligible-seat `not_assessed` without reason → exit 3;
   **denominator exclusion** — a fixture panel where counting ineligible seats' would-be
   scores WOULD flip the decision, asserting the v2 result ignores them (the overlay's
   named mutation test); majority n=1 owner-decides; `[DIMENSION-UNASSESSED]` abort;
   `dimension_verdicts` mismatch → exit 1; fatal-atom firing incl. F1-over-F2 precedence;
   v1-grammar report (with Failure Condition Checks section) → loud grammar failure.
3. **Decision-contract exhaustiveness**: enumerate ALL seat-score profiles — per dimension,
   every assignment of `{pass, warn, block, block(fatal)}` to each assessed eligible seat,
   PLUS the valid partial-abstention states (on the two-eligible D3, each seat additionally
   takes the `abstained` state, excluding the both-abstained profile, which is the separately
   tested `[DIMENSION-UNASSESSED]` abort — 24 non-aborting D3 states; single-eligible
   dimensions have no non-aborting abstention state). Full v2: 4⁵ × 24 = 24,576 profiles;
   methodology-focus v2: 4×4 = 16. Assert ≥ 1 condition fires in every profile (zero-fired
   unreachable for the shipped templates) and exactly one action is selected; spot-assert
   the mapped decisions for the boundary states (single mandatory warn ⇒ minor_revision in
   full / major_revision in mf; single normal block ⇒ minor_revision; any fatal mandatory
   block ⇒ reject, including a fatal D6 block — the Out-of-Scope path; D3 split block —
   one eligible seat blocks, the other passes — fires F2 (`any`) but not an
   `all`-quantified condition; D3 with one abstained seat exercises the dynamic
   majority-n=1 path for both choices of abstaining seat).
4. **Conformance checker**: per check family, one failing and one passing fixture —
   `--role` absent or not in the mode's role set (exit 2); `--role` ≠ the report's
   `contract_role` (exit 3 — the swapped-reports case); `--manuscript` absent (exit 2,
   never a skip); missing fatal trigger field; identical block/warn triggers; a 12-word
   manuscript shingle in Phase 1 (and the title-collision inverse: title text does NOT
   fire); Phase 2 trigger text absent from Phase 1 (drift) and kind-mismatch (fatal block
   binding warn trigger); two-dissent report; Critical finding with no anchor / with `text`
   anchor over 25 words / `absence` anchor without checked surfaces (fail) and the
   compliant forms (pass); DA-grammar fixtures — a `#### CRITICAL` table row with an empty
   Evidence Anchor cell (fail) and a fully-anchored DA table (pass). Panel-side: a
   `--roles` list mismatching a report's `contract_role` (exit 3) and the matching
   inverse (pass).
5. **Lints**: mutation tests flipping each witnessed literal (eligibility map cell, grammar
   sentence, enum token, threshold residency) → lint fails; `_mirror` lists updated in the
   same commit as every newly-read file.

## 16. Migration & compatibility

- **Shipped templates**: replaced in-place, `contract_id` `…/v1` → `…/v2`,
  `baseline_version` bumped to the release version. The v1 files do not survive as
  alternates (decision 9).
- **User-frozen custom v1 contracts**: fail LOUDLY at the first gate
  (`check_sprint_contract.py` branch 13 / checker CONTRACT-INVALID) with a migration message.
  Migration is mechanical: add `eligible_roles`/`owner_role` per dimension, add
  `what_triggers_fatal` to `scoring_plan_schema.required`, replace any
  `reject_or_major_revision` action with the fatal/repairable pair. Documented in the
  protocol's §3 and the release notes. No silent reinterpretation of old contracts — loud
  failure is the compatibility contract.
- **Baseline-immutable fields** (protocol §3): `eligible_roles`, `owner_role` join the
  orchestrator-immutable list.
- **Schema 6 / Schema 7 and the pipeline**: no changes — v2 only ever emits tokens that map
  onto the existing four-value enum (the hybrid was the one violator, and it is removed).
  Writer/evaluator (v3.6.6) surfaces: untouched.
- **E4 instrument**: fixtures and adjudication protocol unchanged; run records will show the
  new decision tokens (`minor_revision` becomes reachable on clean controls). Historical
  rows keep their recorded hybrid decisions — records, not rules.
- **`quick`/`guided`/`calibration`/`re-review`**: no behavior change in this spec beyond the
  §9 authority-table row that documents their existing engines; `re-review` is explicitly
  #576's (spec B) — this spec deliberately creates only the artifact spec B consumes
  (`owner_role` for verification routing), no more.

## 17. Acceptance measurement (E4)

Implementation is a reviewer-prompt + contract change ⇒ the seeded-defect protocol applies
in full (`evals/heldout/reviewer_seeded_defects/README.md`): re-measure post-change with
2 replicates × 3 fixtures on the current model, frozen dispatch shape (isolated per-seat
two-phase calls — headless CLI recipe), against the newest same-model baseline rows
(2026-07-25 claude-opus-5: recall 1.00/1.00, clean-control false findings 2/1,
severity agreement 0.536 post-#581).

Gates (unchanged, replicate means): strict recall does not regress (overall AND critical
band); clean-control false findings do not increase; severity agreement does not regress.
Additional spec-A-specific observables to record (diagnostic, not gates): non-DA per-seat
tag distributions (the 7/7-critical pattern is the B1 target); clean-control decisions (the
Minor path should become reachable — a sound-at-its-scale control landing Minor Revision is
the designed outcome); `[DIMENSION-UNASSESSED]` / conformance-failure rates (operational
monitors, expected ≈ 0).

## 18. Implementation plan

- **PR-A (this document).** Design only. `docs(design)` prefix (changelog-gate exempt).
- **PR-B (implementation, single PR — the §9 lockstep rule makes the surfaces atomic):**
  Schema 13.2 + validator invariants; v2 templates; `check_panel_synthesis.py` v2 semantics;
  `check_phase_conformance.py`; the five agents' Phase 1/Phase 2 subsections + DA
  Phase-Boundary rewording + synthesizer protocol section; protocol §§2–9 updates;
  `editorial_decision_standards.md` §0 + single-sourcing repairs; template § Severity
  Levels + Finding Contract B1 anchors; the two lints (extended + new) + mutation tests +
  CI/pytest-manifest wiring. Dual-track review (codex xhigh + /security-review) per repo
  convention; the review prompts restate the P1 bar, probe budget, and axis-termination
  declarations each round (defrift discipline), including the §14 threat-model declaration.
- **PR-C (measurement):** E4 post-change fleet + README row + gate verdicts. Gates decide
  whether PR-B's behavior surfaces ship in the next release or get a corrective iteration.

## 19. Non-goals and preserved keeps

- **The three documented keeps stand untouched, bridges intact and lint-pinned** (#581):
  the #506 calibration leniency prior (measurement-reading prior, never a decision rule);
  the v3.0 DA no-consecutive-concessions ladder (pressure-time anti-sycophancy procedure,
  never first-pass severity); the quota range-pattern precision-over-recall tradeoff
  (documented in place). Nothing in this spec modifies those blocks; §11's anchors compose
  with the severity-by-decision-impact sentence they bridge to.
- **DA iron rules unchanged** (#574 non-goal): DA-CRITICAL visible adjudication, the
  concession ladder, and the challenge-report primacy all stand; decision 2 narrows only the
  DA's *formal score* footprint.
- **No new hard-block on report format beyond the existing unusable-reviewer semantics**;
  severity/anchor requirements continue to gate report validity, not the editorial decision
  directly (#574 non-goal preserved — the decision moves only through scores and conditions).
- **Cross-model tracks (#540 reviewer track, #518 blind checkpoints) untouched**; role
  scoping is orthogonal to which model family a seat runs on.
- **Semantic adequacy judging of Phase-1 triggers** beyond the deterministic floor: still
  deferred (documented limitation, unchanged).
- **`re-review` three-gate work**: #576 / spec B. This spec only supplies `owner_role`.
- **Rubric-anchor redesign (E6) and calibration-tier work (E5)**: separate backlog items,
  not touched here.
