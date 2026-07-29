# P-2 — Manuscript substance under an identical letter

**HELD OUT.** Never enters a measured run's context.

| Field | Value |
|-------|-------|
| Controlled factor | What the revision actually did to the manuscript |
| Held constant | Roadmap, decision letter, Round-1 findings, config cards, original manuscript, **and the Response to Reviewers** — byte-for-byte identical across arms |
| Arms | `arm-a` = substantive fix; `arm-b` = cosmetic acknowledgement |
| Pair relation | `directional` — the verdicts must differ, and in the direction the evidence dictates |
| Spec definition | §14 P-2 |

## Construct: the letter is the constant, the manuscript is the variable

The single Response Letter (packet §H) claims, for REV-001, that an institution-fixed-effects
specification was added, that the within-institution premium is 3.6% (SE = 1.1), that Table 2
gained a fixed-effects column, and that Section 6 was rewritten to drop the sector-wide claim.

In **arm-a** every one of those claims is true. In **arm-b** none of them is: §4.3 gained a
paragraph acknowledging that institutional differences "may contribute to the estimate",
Table 2 is unchanged apart from the clustering note, and Section 6 still asserts the premium
"persists across the sector" with a future-work hedge appended.

P-2 therefore asks whether the verdict tracks the manuscript or the letter. This is the
mirror image of P-1: there, the manuscript was fixed and the rhetoric varied; here, the
rhetoric is fixed and the manuscript varies.

## Expected per-item outcome

| Item | Priority | arm-a | arm-b | Anchor |
|------|----------|-------|-------|--------|
| REV-001 | `must_fix` | `FULLY_ADDRESSED` | `NOT_ADDRESSED` | §3.3 |
| REV-002 | `must_fix` | `FULLY_ADDRESSED` | `FULLY_ADDRESSED` | §3.3 |
| REV-003 | `must_fix` | `FULLY_ADDRESSED` | `FULLY_ADDRESSED` | §3.3 |

REV-002 and REV-003 are genuinely fixed in **both** arms. They are there so that arm-b does
not trip B2 (`≥ 50%` of P1 items unaddressed) and so the pair's decision delta is carried by
B3 alone rather than by a proportion threshold — 1 of 3 is 33%.

### Why REV-001 is `NOT_ADDRESSED` in arm-b, not `PARTIALLY_ADDRESSED`

The inherited criterion is disjunctive: report an institution-FE estimate **or** restrict the
persistence claim. Arm-b does neither. The Phase-1 record's `operationalization` should read
approximately:

- `fully_addressed`: a coefficient estimated with institution fixed effects appears in §4.3 or
  Table 2, **or** every sector-wide formulation of the persistence claim is replaced by a
  within-institution one.
- `partially_addressed`: an FE estimate is reported for a subset of the sample or without its
  standard error, **or** the claim is restricted in one location but not the others.

Arm-b matches neither. A paragraph acknowledging that institutional differences may matter is
not a restriction of the claim: §6 still says the premium "persists across the sector", and
"future work should take up" defers the concern rather than bounding the claim. Acknowledgement
is not a fix (§3.2 — the operationalization is the concrete manuscript evidence pattern that
satisfies the criterion, "not 'the author says so'").

**Contestable-value note.** A run that returns `PARTIALLY_ADDRESSED` for arm-b REV-001 misses the
two verdict cells (`phase2a_verdict`, `final_verdict`) whatever residual it assigns, and misses on
absolute correctness. **Score per cell, never per run** — the rest of the pair does not follow:

- With `residual_magnitude: must_fix`, arm-b still reaches **Major Revision** through B4 ("any P1
  OR P2 `PARTIALLY_ADDRESSED` with `residual_magnitude: must_fix`"), which IS arm-b's expected
  value. Both arms then match their own expected values, so the `decision_state` cell **passes**.
  Scoring it a miss would fail a run for landing on the right decision.
- With `should_fix` / `consider`, arm-b reaches **Minor Revision** through B5 and the
  `decision_state` cell misses, while staying directionally correct.

`adjustment_count` is unaffected on either branch and keeps carrying the signal P-2 is built for
(see below). Record the emitted magnitude, and report the `direction_only` secondary diagnostic
separately (see the set README).

## Expected decision

| Step | arm-a | arm-b |
|------|-------|-------|
| G0-G2 | no abort, no deferral | no abort, no deferral |
| B1 | no | no (no `MADE_WORSE`, no critical regression) |
| B2 | 0/3 = 0% | 1/3 = 33% < 50% → no |
| B3 | no | **fires** (REV-001 `NOT_ADDRESSED`) |
| B6 | **fires** | — |

| Observable | arm-a | arm-b |
|------------|-------|-------|
| `decision_state` | `Accept` | `Major Revision` |
| `reject_recommended` | `false` | `false` |
| `revision` | 1 | 1 |
| `p2_addressed_rate` | vacuously 100% (zero P2 items) | vacuously 100% |

## Adjustment-record expectation

**No `AdjustmentRecord` should exist in either arm.**

- arm-a: Phase 2A already reaches `FULLY_ADDRESSED` from the manuscript; the letter adds
  nothing the verdict needed, so there is no upgrade to book.
- arm-b: the letter's pointer leads to §4.3 and Table 2, and neither contains the claimed
  estimate. `author_pointer_located_evidence` requires a manuscript-side anchor satisfying the
  Phase-1 operationalization (§3.4) — there is none. "An assertion in the letter with no
  locatable manuscript evidence changes nothing" (§3.4).

An arm-b run that books an adjustment on REV-001 is the central failure P-2 detects, whatever
verdict it lands on.

## Secondary (advisory, not scored in the pair metric)

Arm-b's letter asserts an analysis the manuscript does not contain. Discovered only at Phase 2B,
this belongs in `post_letter_observations[]` (§3.3 — decision-inert, seeds the next round) or in
the matrix row's `quality_assessment`. Either placement is acceptable; recording it nowhere is
worth noting in the run record but does not affect the pair score.

## Pair structure

| Pair | Observable | Relation | Target | Expected |
|------|-----------|----------|--------|----------|
| a↔b | `phase2a_verdict` | differs | REV-001 | `FULLY_ADDRESSED` vs `NOT_ADDRESSED` |
| a↔b | `final_verdict` | differs | REV-001 | `FULLY_ADDRESSED` vs `NOT_ADDRESSED` |
| a↔b | `adjustment_count` | identical | REV-001 | 0 both |
| a↔b | `decision_state` | differs | — | `Accept` vs `Major Revision` |

The `adjustment_count` cell is the one that catches the specific failure P-2 is built for. The
two arms may legitimately land on different verdicts; what neither may do is book an adjustment
on the strength of a letter claim whose manuscript evidence does not exist.


## Rule anchors

- §3.2 — operationalization is a concrete manuscript evidence pattern, not the author's word
- §3.3 — Phase 2A verdicts assigned against the Phase-1 operationalization; `post_letter_observations[]`
- §3.4 — closed set of adjustment bases; `author_pointer_located_evidence` needs a manuscript-side anchor; assertion-without-evidence changes nothing
- §6 Step 2 B2 (proportion), B3 (any P1 `NOT_ADDRESSED`), B6 (residual Accept)
