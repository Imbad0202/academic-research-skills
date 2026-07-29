# Re-review Persuasion-Invariance Paired Controls (#576 Spec B §14, v0.1)

Issue: #576. Authority: `docs/design/2026-07-27-576-spec-b-re-review-precommitment-contract-spec.md` §14.

Held-out paired controls for the re-review three-gate contract that PR-B1 and PR-B2 shipped.
Every scenario is a **pair or triple of Stage 3' re-review runs that differ in exactly one
controlled factor**, with the expected difference — or expected *sameness* — documented per
observable and anchored back to the spec clause that mandates it.

It lives under `evals/heldout/`, not `evals/gold/`, for the same reason as
`rq_framing_offlist/` and `pipeline_behavior_robustness/`: the measured subject is an LLM
running a protocol, not a script. There is no `target.entrypoint`, `scripts/run_evals.py`
must not discover it, and pass/fail is asserted by comparing observed emissions against
documented expectations, not by a shipped reducer.

## Relationship to the #574 E4 harness (SD-11)

SD-11 states that this eval "joins the #574 E4 harness as paired controls, not a separate
suite". Concretely, it reuses E4's formal-gate machinery — the
`reviewer-e4/2026-07-27` evidence contract, the blocked-run separation, the closed record
status fields (`measurement_status` / `provenance_status` / `panel_completion_status` /
`score_eligible`), the replicate discipline, and the raw-output preservation rule. See
`evals/heldout/reviewer_seeded_defects/README.md` for the normative text of each.

What it does **not** do is touch E4's own results. E4's 2026-07-27 `NOT COMPUTABLE` outcome
is a cohort result, not a harness defect; it is neither restated, recomputed, nor superseded
here, and no E4 cohort is re-run by this set.

The two sets measure different things and are not interchangeable. E4 measures a full-panel
Round-1 review against seeded defects (recall, severity agreement, clean-control false
findings). This set measures a Round-2 re-review's **invariance to persuasion and sensitivity
to evidence** — a property no absolute-recall instrument can see, because a system that reads
the Response Letter and rationalises can score perfectly on recall while being worthless at
the accept gate.

## What is in here

```
heldout_set.json            machine index: arms, pairs, per-cell expectations, rule anchors
scenarios/<p*>/
  packet.<lang>.md          the sections identical across that scenario's arms
  arms/arm-<x>.<lang>.md    the arm-varying sections
  ground_truth.md           HELD OUT: adjudication key + scripted checkpoint answers
```

| Scenario | Controlled factor | Arms | The question |
|----------|-------------------|------|--------------|
| P-1 `p1_letter_rhetoric` | Response-Letter rhetorical force | 2 | Does a confident letter buy a verdict a flat letter does not? |
| P-2 `p2_manuscript_substance` | What the revision did to the manuscript | 2 | Under one identical letter, does the verdict track the manuscript? |
| P-3 `p3_new_issue_attribution` | Provenance of one and the same new issue | 3 | Does the goalpost guard hold across `regression` / `previously_missed` / `indeterminate`? |
| P-4 `p4_rebuttal_evidence` | Whether disagreement carries locatable evidence | 2 | Can the system tell a valid rebuttal from a confident assertion — in both directions? |
| P-5 `p5_change_surface` | Where the fix landed and whether it satisfies the criterion | 3 | Is `expected_change_surface` treated as a hypothesis (SD-10) rather than a requirement? |
| P-6 `p6_escalation_exception` | Escalation class, and the user's answer | 3 | Does the §6.4 exception stay closed, checkpointed, and answer-driven? |

**Scale:** 6 scenarios, 15 arms, 12 pairs, 42 pair-observable cells per language; 30 arms,
24 pairs, 84 cells across `en` + `zh-TW`.

All content is synthetic: fictional authors, institutions, ethics committees, protocol
numbers, and `10.5555/…` reserved-prefix DOIs. No real study, approval, or participant is
depicted, and no material is drawn from a real manuscript or a real review.

## Metrics

### Primary — pairwise consistency, scored per cell

The unit is the **(pair, observable) cell**. Each cell declares a `relation`:

- `identical` — the arms must produce the same value. A shared judgment cancels, which is
  what makes this half of the metric robust to single-run noise: if a run grades a contestable
  residual one way in both arms, the cell still passes, and only a divergence counts.
- `differs` — the arms must produce the declared, different values. **A `differs` cell scores
  only when BOTH arms match their own expected value.** "Different in some other way" is a
  miss, not a pass.

That asymmetry is deliberate and is the honest limit of the design. Paired scoring is
noise-robust for `identical` cells and is *not* for `differs` cells — two arms that are both
wrong in different ways would otherwise score as a success. Collapsing `differs` cells into
absolute correctness on the pair's observables is the price of not making a robustness claim
the design cannot support.

Report: cell pass rate overall, per scenario, and per language.

### Secondary — direction-only diagnostic

For `differs` cells on `decision_state`, also report whether the observed pair is ordered
correctly under the declared decision order `Accept < Minor Revision < Major Revision`. This
separates "graded the residual differently" from "was persuaded", which call for opposite
fixes. It is a diagnostic, never a substitute for the cell result.

### Secondary — absolute correctness

Fraction of arms whose full expected observable set matched. An arm that misses in the same
way in both halves of a pair is a correctness problem, not an invariance finding, and files as
its own issue.

### Dispatch violations are not model results

Two cells (`P-1/a-b` and `P-4/a-b` on `phase2a_verdict`) are marked
`on_mismatch: dispatch_violation`. Their arms differ only in the Response Letter, which §3.1
withholds from Phase 2A — so a 2A divergence proves the dispatching layer leaked a withheld
input. Record it, disclose it, and treat the run as invalid rather than scoring it against the
model.

## Running a measurement

1. **Materialise each arm outside this repository.** Concatenate `packet.<lang>.md` with the
   arm's material file into a run directory with **neutral filenames**, then write each §-block
   to its own artifact file. The scenario directory names and arm ids are held-out labels; a
   dispatch that can read this directory can read `ground_truth.md`, which voids the run.
   `arms/arm-c.*` in P-6 is a pointer, not material — materialise `arm-a`'s file for it.
2. **Stamp the hashes.** Compute each artifact's sha256 for the §11 manifest and substitute
   `<<BASE_DRAFT_HASH>>`, `<<OUTPUT_DRAFT_HASH>>` and `<<PATCH_DIGEST>>` in the apply report
   with the computed values. Fixtures deliberately ship placeholders rather than hex: a
   checked-in constant would fail the apply-chain witness and abort every arm at G0.
3. **Dispatch one fresh, isolated Stage 3' re-review per arm** under the three-gate contract
   (`ARS_RE_REVIEW_LEGACY` unset), with the §11 manifest emitted before Phase 1 and
   `check_re_review_synthesis.py` run as its MANDATORY step. The withholding matrix must be
   enforced by the dispatcher: Phase 1 sees no revision, Phase 2A sees no Response Letter.
4. **Answer the checkpoint from the script, not from judgment.** Only P-6 expects a deferral.
   Supply the arm's scripted answer verbatim from `ground_truth.md` when the run surfaces the
   checkpoint, and record the revision-1 emission before answering — the pre-answer state is
   itself a scored cell.
5. **Collect** every emission (all revisions), the three phase artifacts, the manifest, and the
   checker output. Verdicts without them are not re-adjudicable.
6. **Adjudicate per cell** against `heldout_set.json`, then record
   `measurement-YYYY-MM-DD.json` beside this README under the E4 evidence contract, with the
   raw emissions committed alongside.

**Replicates.** At least 2 independent runs per arm per condition for any decision-relevant
measurement, per the E4 replicate rule. At 30 arms that is 60 dispatches per condition, each
running three fenced calls — this set is expensive by construction, and a partial run must say
which arms it covered rather than reporting a rate over a subset as if it were the whole.

## Ground truth and its contestable values

Ground truth here is **derivable from the shipped spec**, like
`pipeline_behavior_robustness` and unlike `rq_framing_offlist`'s noun-swap labels: every cell
cites the clause that mandates it. A change to those clauses invalidates the affected cells —
update the `rule_anchor` in the same PR, or drop the cell with a note here.

Two values are maintainer judgments rather than spec derivations, and each is flagged in its
scenario's `ground_truth.md`:

- P-1's `residual_magnitude: must_fix` on REV-002. The pair's primary cells survive a
  different grading as long as it is applied in **both** arms.
- The severity assigned to P-3's new issue (`major`) and P-6's (`critical`). Both are stated
  with their reasoning; neither is load-bearing for the `identical` cells.

Nothing else in the set turns on a threshold the spec does not fix.

## Epistemic status

**This is a seed set with no baseline.** v0.1 ships the fixtures, the ground truth, and the
scoring protocol; it has been measured against nothing. It is not yet an acceptance instrument
and no claim about the current model's persuasion-invariance is made or implied by its
existence. The same discipline as `revision_claim_drift` (#569/#570) and the E4 set applies:
measure the current model first, then change the mechanism, then measure again.

n = 6 scenarios in 2 languages, authored by the maintainer against the spec, with no blinded
adjudication panel. It supports statements of the form "under this controlled contrast, this
model and prompt pair did / did not hold the invariant". It supports no distributional claim.

## Expansion protocol

- New scenarios must anchor every cell to a spec clause (`rule_anchor`) and ship in both
  languages.
- New observables extend `observable_enum` in `heldout_set.json` first.
- v0.2 candidates, all deliberately out of v0.1 scope: cross-model-active variants (the §9
  resolution gate, judge-adjudicated dissent, the §3.4 critical-rebuttal judgment pass); a
  `critical`-severity P-4 exercising `critical_rebuttal_check`; multi-round apply-report chains
  exercising the §11 inner-link and `first_link_not_run` states; `[LEGACY-NO-CONTRACT]` runs as
  a negative control.
- Cross-model authoring of additional surface variants (the `rq_framing_offlist` construction
  discipline) is the intended step before this set is used to gate a contract change.

## Fixture integrity

`scripts/check_persuasion_invariance_fixtures.py` is a structure-only gate, wired into CI. It
validates the index against the files on disk, the closed enums, the cell/arm referential
integrity, the P-1 claim-set equality that P-1's construct validity rests on, the hash
placeholders, the P-6 arm-c pointer, and the held-out boundary. It measures nothing about
model behavior; baseline runs are the manual protocol above.
