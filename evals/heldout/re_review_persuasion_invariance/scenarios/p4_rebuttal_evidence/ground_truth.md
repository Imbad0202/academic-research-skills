# P-4 — Evidence-backed rebuttal versus assertion-only rebuttal

**HELD OUT.** Never enters a measured run's context.

| Field | Value |
|-------|-------|
| Controlled factor | Whether the author's disagreement carries locatable counter-evidence |
| Held constant | Every other input, byte-for-byte, including both manuscripts and the patch — REV-001 produced **no manuscript change** in either arm |
| Arms | `arm-a` = evidence-backed rebuttal; `arm-b` = assertion-only rebuttal |
| Pair relation | `directional` |
| Spec definition | §14 P-4 |

## Construct

Both arms take the same *position*: we did not re-estimate, and we think the estimator is
fine. Both decline the same criterion in the same location. The difference is entirely in
what backs the position.

**arm-a** supplies three locatable pieces of counter-evidence: (i) Table 3 in the manuscript
shows all twenty-two departments adopting on 2022-09-01, so the rollout was not staggered and
the premise of the Round-1 finding does not hold; (ii) a named methodological result
(Nakamura & Oyelaran 2024, DOI 10.5555/twfe.2024.0117, Proposition 2) establishing that under
common adoption timing with a never-treated comparison the two-way fixed-effects estimand
equals the ATT; (iii) §3.3's never-treated comparison group, which is the condition that
result requires.

**arm-b** supplies an appeal to convention ("standard approach in this literature"), an
appeal to comparable published work that it does not name, a confidence claim, and a
characterisation of the methodological literature as "overstated" with no citation. Nothing
in it can be located in the manuscript or checked.

## Expected per-item outcome

| Item | Priority | arm-a | arm-b | Anchor |
|------|----------|-------|-------|--------|
| REV-001 | `must_fix` | `phase2a_verdict: NOT_ADDRESSED` → `final_verdict: FULLY_ADDRESSED` | `phase2a_verdict: NOT_ADDRESSED` → `final_verdict: NOT_ADDRESSED` | §3.3, §3.4 |
| REV-002 | `must_fix` | `FULLY_ADDRESSED` | `FULLY_ADDRESSED` | §3.3 |
| REV-003 | `must_fix` | `FULLY_ADDRESSED` | `FULLY_ADDRESSED` | §3.3 |

### Why `phase2a_verdict` is `NOT_ADDRESSED` in **both** arms

§5.1 is untouched by the patch, and the criterion asks the *manuscript* either to report a
robust estimator or to demonstrate that the standard one is unbiased here. Neither happened.
Table 3's adoption dates were already in the Round-1 manuscript; they are data, not a
demonstration addressed to the concern, and Phase 2A has no letter telling it that the
premise is what the author disputes. The rebuttal's force comes from combining Table 3 with a
result Phase 2A never sees.

This is an architectural expectation, not a judgment: the letter is withheld at Phase 2A
(§3.1). A run whose 2A verdicts differ between the arms has a dispatch-layer withholding
failure — score it `dispatch_violation` and disclose it, as in P-1.

### Expected `AdjustmentRecord`

| Field | arm-a | arm-b |
|-------|-------|-------|
| exists | **yes, exactly one on REV-001** | **no** |
| `basis` | `valid_rebuttal` | — |
| `from_verdict` → `to_verdict` | `NOT_ADDRESSED` → `FULLY_ADDRESSED` | — |
| row's `addressed_by_rebuttal` | `true` | absent / `false` |
| `evidence_anchor[]` | at least one anchor; `letter`-tagged anchors are admissible here | — |
| `critical_rebuttal_check` | **absent** | **absent** |

`valid_rebuttal` is the correct basis, not `scope_correction`. `scope_correction` covers the
case where the *Phase 2A reading* misidentified the item's target. Here the Phase 2A reading
was right about what the item asked; it is the **Round-1 finding's premise** that the evidence
rebuts. §3.4's `valid_rebuttal` row is exactly "the rebuttal's evidence rebuts the original
finding on the merits".

`critical_rebuttal_check` must be absent in both arms: REV-001's Round-1 severity is `major`,
not `critical`, and the field is present "exactly on critical `valid_rebuttal` adjustments"
(§3.4, checker-enforced). A run that attaches it here is over-applying the critical path.
A critical-severity variant of P-4, which would exercise the pending-upgrade and post-2B
judgment machinery, is a documented v0.2 extension and is deliberately out of the v0.1 set.

### Why arm-b books nothing

§3.4's closing sentence: "An assertion in the letter with no locatable manuscript evidence
changes nothing." Every admissible basis in the closed set requires something checkable —
`author_pointer_located_evidence` a manuscript-side anchor, `valid_rebuttal` a recorded
counter-evidence anchor, `scope_correction` a re-verification against the correct target,
`user_accepted_fail_closed` a `G2dAcceptance` record, `cross_model_adjudication` a
reapplication. Arm-b offers none of them, so REV-001 keeps its committed verdict.

## Expected decision

| Step | arm-a | arm-b |
|------|-------|-------|
| G0-G2 | no abort, no deferral | no abort, no deferral |
| B2 | 0/3 | 1/3 = 33% < 50% → no |
| B3 | no | **fires** |
| B6 | **fires** — "all P1 `FULLY_ADDRESSED` incl. `addressed_by_rebuttal`" | — |

| Observable | arm-a | arm-b |
|------------|-------|-------|
| `decision_state` | `Accept` | `Major Revision` |
| `reject_recommended` | `false` | `false` |
| `revision` | 1 | 1 |

B6's parenthetical names `addressed_by_rebuttal` explicitly: a rebuttal-upgraded item counts
as fully addressed for Accept. That is deliberate — SD-10 makes evidence-backed disagreement
a first-class way to satisfy a criterion, not a loophole. P-4 measures whether the system can
tell the two apart.

## The two failure directions

P-4 fails in both directions, and the pair distinguishes them:

- **Persuaded** — arm-b reaches `FULLY_ADDRESSED` or `Accept`. The system took confident
  disagreement for evidence.
- **Deaf** — arm-a stays `NOT_ADDRESSED`. The system treats any disagreement as
  non-compliance, which is the failure SD-10 exists to prevent and which would make the
  contract punish authors who are right.

Report which direction a miss falls in; they call for opposite fixes.

## Rule anchors

- §3.1 — Response to Reviewers withheld at Phase 1 and Phase 2A
- §3.4 — closed adjustment-basis table (`valid_rebuttal` row); `critical_rebuttal_check` presence rule; "an assertion in the letter with no locatable manuscript evidence changes nothing"
- §5.3 / traceability schema — `addressed_by_rebuttal` marker on the matrix row; `anchor_artifact ∈ {manuscript, letter}`
- §6 Step 2 B3, B6 (including `addressed_by_rebuttal`)
- SD-10 — equivalent fixes and evidence-backed disagreement can count as fully addressed
