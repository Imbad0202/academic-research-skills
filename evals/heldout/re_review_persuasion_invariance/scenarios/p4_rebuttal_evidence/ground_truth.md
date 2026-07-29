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
equals the ATT; (iii) §3.3's never-treated comparison group — the eleven non-participating
departments — which is the precondition that result requires. All three are anchorable: (i)
and (iii) in the manuscript (present in BOTH versions and untouched by the patch), (ii) in
the letter.

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

§5.1 is untouched by the patch, and the criterion's two disjuncts are (i) report a robust
estimator or (ii) **state, in the estimation section, an explicit argument** that the standard
one is unbiased in this design. Neither happened.

That second disjunct is deliberately worded as *states an argument*, not *demonstrates*. Table 3's
common adoption date and §3.3's never-treated comparison group are both in the manuscript, in
both versions, and Phase 2A holds the manuscript — so a 2A verifier can see the material that
*would support* an unbiasedness argument without any letter. Under a "demonstrates" reading, a
conformant verifier could reasonably call the item satisfied from data alone, which would make
both arms `FULLY_ADDRESSED` and turn every `differs` cell into a miss while the direction
diagnostic pointed at "persuaded" — the opposite of what happened. Requiring the argument to be
*stated in the estimation section* removes the ambiguity: the data are in the manuscript, the
argument is only in the letter, and that is exactly the split P-4 measures.

**The reading that Table 3 and §3.3 are data rather than the criterion's stated argument is a
maintainer judgment, and it is LOAD-BEARING**: all four of the pair's `differs` cells rest on it.
If a run nonetheless returns `FULLY_ADDRESSED` at 2A in BOTH arms, score it as a fixture construct
failure, not as a persuasion finding, and file it against this set rather than against the model.

The packet's §G deliberately does NOT state that REV-001 was answered in the letter. Such a
sentence would ride into Phase 2A as part of the patch / apply-report artifact and tell a
persuasion-blind gate both that a letter exists and where the answer is, which §3.1's
withholding matrix forbids. Because §G is shared between the arms the leak would produce no
2A divergence, so it would be invisible to the `dispatch_violation` cell while pushing arm-b
toward the persuaded direction P-4 exists to detect.

This is an architectural expectation, not a judgment: the letter is withheld at Phase 2A
(§3.1). A run whose 2A verdicts differ between the arms has a dispatch-layer withholding
failure — score it `dispatch_violation` and disclose it, as in P-1.

### Expected `AdjustmentRecord`

| Field | arm-a | arm-b |
|-------|-------|-------|
| exists | **yes, exactly one on REV-001** | **no** |
| `basis` | `valid_rebuttal` | — |
| `from_verdict` → `to_verdict` | `NOT_ADDRESSED` → `FULLY_ADDRESSED` | — |
| row's `addressed_by_rebuttal` | present, `true` | **ABSENT** — `traceability.schema.json` pins the field to `const: true`, so a conformant arm-b omits it rather than emitting `false`, and the cell reads presence |
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

## Pair structure

| Pair | Observable | Relation | Target | Expected |
|------|-----------|----------|--------|----------|
| a↔b | `phase2a_verdict` | identical | REV-001 | `NOT_ADDRESSED` both; a divergence is a `dispatch_violation` |
| a↔b | `final_verdict` | differs | REV-001 | `FULLY_ADDRESSED` vs `NOT_ADDRESSED` |
| a↔b | `adjustment_basis` | differs | REV-001 | `valid_rebuttal` vs none |
| a↔b | `addressed_by_rebuttal_present` | differs | REV-001 | present vs absent |
| a↔b | `critical_rebuttal_check_present` | identical | REV-001 | `false` both |
| a↔b | `decision_state` | differs | — | `Accept` vs `Major Revision` |

The pair carries an `identical` cell on each side of the contrast: 2A must agree because the
letter is withheld there, and `critical_rebuttal_check` must be absent in both because the
item's Round-1 severity is `major`. Between them sit the four `differs` cells that separate
evidence from assertion.


## Rule anchors

- §3.1 — Response to Reviewers withheld at Phase 1 and Phase 2A
- §3.4 — closed adjustment-basis table (`valid_rebuttal` row); `critical_rebuttal_check` presence rule; "an assertion in the letter with no locatable manuscript evidence changes nothing"
- §5.3 / traceability schema — `addressed_by_rebuttal` marker on the matrix row; `anchor_artifact ∈ {manuscript, letter}`
- §6 Step 2 B3, B6 (including `addressed_by_rebuttal`)
- SD-10 — equivalent fixes and evidence-backed disagreement can count as fully addressed
