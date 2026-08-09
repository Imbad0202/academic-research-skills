# Re-review Persuasion-Invariance Paired Controls (#576 Spec B §14, v0.1)

Issue: #576. Authority: `docs/design/2026-07-27-576-spec-b-re-review-precommitment-contract-spec.md` §14.

> **Archived contract boundary:** v0.1 is frozen evidence for re-review contract
> 1.0. Its P-3 no-original arm and `first_link_not_run` expectations are not
> valid current 1.1 emissions after #670; current 1.1 hard-requires the original
> manuscript and exact Revision-Evidence Bundle replay. This historical set is
> preserved without re-scoring and must not gate current 1.1 behavior.

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

Each scenario declares which lettered sections (§A roadmap … §I manifest declaration) the arm
file supplies; the packet holds the rest. **P-6 is the exception and has to be**: its controlled
factor is the escalation CLASS of a Phase-1 `NewStandardRecord` (§3.2), and §3.1 makes Phase 1
revision-blind, so a class difference can only come from different Round-1 artifacts. There the
arm supplies §A-§H and the packet supplies §I alone.

| Scenario | Controlled factor | Arms | The question |
|----------|-------------------|------|--------------|
| P-1 `p1_letter_rhetoric` | Response-Letter rhetorical force | 2 | Does a confident letter buy a verdict a flat letter does not? |
| P-2 `p2_manuscript_substance` | What the revision did to the manuscript | 2 | Under one identical letter, does the verdict track the manuscript? |
| P-3 `p3_new_issue_attribution` | Provenance of one and the same new issue | 3 | Does the goalpost guard hold across `regression` / `previously_missed` / `indeterminate`? |
| P-4 `p4_rebuttal_evidence` | Whether disagreement carries locatable evidence | 2 | Can the system tell a valid rebuttal from a confident assertion — in both directions? |
| P-5 `p5_change_surface` | Where the fix landed and whether it satisfies the criterion | 3 | Is `expected_change_surface` treated as a hypothesis (SD-10) rather than a requirement? |
| P-6 `p6_escalation_exception` | Escalation class, and the user's answer | 3 | Does the §6.4 exception stay closed, checkpointed, and answer-driven? |

**Scale:** 6 scenarios, 15 arms, 12 pairs, 43 cells per language; 30 arms, 24 pairs, 86 cells
across `en` + `zh-TW`. A cell is a `(pair, observable, target)` triple — see Metrics.

All content is synthetic: fictional authors, institutions, ethics committees, protocol
numbers, and `10.5555/…` reserved-prefix DOIs. No real study, approval, or participant is
depicted, and no material is drawn from a real manuscript or a real review.

## Metrics

### Primary — pairwise consistency, scored per cell

The unit is the **(pair, observable, target) cell** — `target` is part of a cell's identity, and one pair may legitimately carry two cells on the same observable at different targets (P-1/a-b has two `final_verdict` cells, at REV-001 and REV-002, whose expected values are deliberately different). A run-level cell carries `target: null`, written `—` in the ground truths. Each cell declares a `relation`:

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

### Conditional cells are unscoreable, never a miss

A cell may carry `conditional_on`. It is scored only when the stated precondition holds in the
run; otherwise it is **unscoreable** — record the observation and the unmet precondition, exclude
the cell from both numerator and denominator, and never count it as a miss. Preconditions exist
exactly where the spec permits more than one conformant emission and the cell can only read one
of them. One cell in P-6 carries one (`reject_recommended`, conditional on the emitted
`escalation_class`), explained in that scenario's `ground_truth.md`. Where a cell can be made
TOTAL instead — defined on every conformant branch — that is preferred to conditionalising it,
and P-6's `escalation_path_entry` is the worked example.

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
   arm's material file into a run directory with **neutral filenames**, then split the §-blocks
   into artifact files. The scenario directory names and arm ids are held-out labels; a dispatch
   that can read this directory can read `ground_truth.md`, which voids the run.
   `arms/arm-c.*` in P-6 is a pointer, not material — materialise `arm-a`'s file for it.

   The split is not one file per §-block, and three cases need care:
   - **§A** is the roadmap artifact. Strip the Markdown fence and write the RAW JSON; the
     synthesis checker parses JSON, not a fenced block.
   - **§G** holds TWO manifest artifacts — the patch (a `revision_patches[]` entry) and the
     apply report (an `apply_reports[]` entry). Write them separately, and keep the arrays
     equal in length and paired by position.
   - **§E and §G** are absent by design in P-3 arm-c — the original manuscript and both array
     artifacts. Emit `{present: false}` for `original_manuscript`, `revision_patches` and
     `apply_reports`; write no file and no sentinel. **§F is NOT absent there.**
     `revised_manuscript` is hard-required (§11: absent → G0), arm-c carries it, and its own §I
     declares it present — declaring it absent would abort the arm at G0 before any gate ran and
     take seven of P-3's eleven cells with it.
2. **Stamp the hashes.** Compute each artifact's sha256 for the §11 manifest and substitute the
   placeholders in the apply report with the computed values. Widths differ and the checker
   enforces them: `base_draft_hash` and `output_draft_hash` are the **12-hex prefix** form that
   `ars_apply_revision_patch.py` emits, `patch_digest` is the **full 64-hex** sha256 of the exact
   patch bytes. Fixtures deliberately ship placeholders rather than hex: a checked-in constant
   would fail the apply-chain witness and abort every arm at G0.
3. **Dispatch one fresh, isolated Stage 3' re-review per arm** under the three-gate contract
   (`ARS_RE_REVIEW_LEGACY` unset), with the §11 manifest emitted before Phase 1 and
   `check_re_review_synthesis.py` run as its MANDATORY step. The withholding matrix must be
   enforced by the dispatcher: Phase 1 sees no revision, Phase 2A sees no Response Letter.
4. **Answer the checkpoint from the script, not from judgment — and branch on the pending
   RECORDS it carries, not on which scenario it appeared in.** Only P-6 scripts an answer, and
   only for its own §6.4 escalation exception (G2(c)). Every other §6 pending record — a §7
   dissent deferring through G2(a), a G2(b) divergence, a G2(d) acceptance, or a SECOND escalation
   exception — is unscripted **in every scenario, P-6 included**: P-6's roadmap carries `must_fix`
   items too, so a conformant dissent can defer it exactly as it can defer P-2, and arms a and c
   script a disposition for one named exception and nothing else.

   **The unit is the pending RECORD, not the kind.** An arm's script authorises a disposition for
   exactly the pending record it names. §6 G2 fires on "any PENDING user-input state" and the loop
   runs until none remains — and G2(c) is pending independently *per*
   `EscalationExceptionRecord` — so a checkpoint can carry several pending records, including
   several of a kind the arm does script. **If the checkpoint carries any pending record the
   arm's script does not name, do not answer it — not even the record the script does name.**
   Applying a scripted utterance to an unnamed record invents a user decision the fixture never
   made; answering only the named one leaves the loop pending with no disposition. Either way the
   terminate path takes precedence. This set has no authority to improvise the rest. Every §6 answer is a typed record from a closed set, and each option
   carries a substantive commitment the fixture never made:
   `DissentAdjudication{replacement_approved}` lets the dissented criterion stand, which is
   exactly the goalpost reset §7 exists to bound, and `original_upheld` mandates a scoped
   Phase 2B′ re-application. A free-text "not approved" is not a member of either closed set at
   all. Improvising any of them injects a maintainer judgment into a measured run and records it
   as if the protocol had produced it.

   Instead: record the deferral, its G2 sub-state, and the record that caused it; terminate the
   arm unanswered; mark **every cell of every pair involving that arm** unscoreable — the whole
   arm, not a subset, so two operators cannot compute different denominators from the same
   emission; and file the scenario for revision, since a fixture that reliably provokes an
   unscripted deferral has a criterion problem. Write the arm's record with
   `measurement_status: blocked` and `score_eligible: false` under the inherited E4 evidence
   contract, preserving the emissions alongside it.

   For the escalation checkpoint in P-6:
   Supply the arm's scripted answer verbatim from `ground_truth.md`, **in the language of the
   run** (every answer there is given in both), when the checkpoint carries exactly the one
   pending record the script names — the arm's own escalation exception — and nothing else. Record
   the revision-1 emission before answering; the pre-answer state is itself a scored cell.
   arm-a and arm-c have expected-path answers; arm-b has only a contingency answer, since it is
   not expected to defer at all.
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

**Six values** are maintainer judgments rather than spec derivations, and each is flagged as such
in its scenario's `ground_truth.md`. **Three of the six are load-bearing for a scored cell** —
P-3's new-issue severity, P-6's `mechanical_decision_impact`, and P-4's stated-argument reading;
the other three are not.

- P-1's `residual_magnitude: must_fix` on REV-002. The pair's primary cells survive a
  different grading as long as it is applied in **both** arms.
- P-3's new-issue severity (`major`). **Load-bearing**: `critical` and `major` both reach Major
  Revision (through B1 and B3 respectively), but the third legal value `minor` reaches Minor
  Revision through B5, missing the two arm-a-side `decision_state` cells (`P-3/a-b`, `P-3/a-c`).
  P-3's third `decision_state` cell, `P-3/b-c`, is unaffected at any severity — the goalpost guard
  keeps both of its arms out of Step 2.
- P-6's new-issue severity (`critical`). **Not load-bearing**: the goalpost guard keeps a
  `previously_missed` issue out of Step 2 regardless of severity.
- P-6's `mechanical_decision_impact: Major Revision`. This one **is** load-bearing: §6.4 fixes
  only the enum, §6 Step 3 is `max(base, floor)`, and P-6's base is `Accept`, so a conformant
  run emitting `Minor Revision` misses two `differs` cells for a reason unrelated to the
  escalation machinery. Record the emitted value.
- P-6's `escalation_class: research_integrity`. §6.4's closed set also contains `ethics` and
  nothing discriminates between them for this fixture's finding. Only `research_integrity` sets
  `reject_recommended`, so the affected cell is marked `conditional_on` and goes unscoreable
  rather than counting as a miss when a run classifies it `ethics`.
- P-4's reading that Table 3 and §3.3 are *data* rather than the criterion's stated argument.
  **Load-bearing**: the criterion is worded to make it unambiguous (it asks for an argument
  stated in the estimation section), but a run reading it the other way returns
  `FULLY_ADDRESSED` at 2A in **both** arms and loses all four `differs` cells. If that happens it
  is a fixture construct failure and files against this set, not against the model.

Apart from these, no cell depends on a threshold the spec leaves open.

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
- A future current-contract successor must use a new set version and authority;
  v0.2 candidates, all deliberately out of archived v0.1 scope: cross-model-active variants (the §9
  resolution gate, judge-adjudicated dissent, the §3.4 critical-rebuttal judgment pass); a
  `critical`-severity P-4 exercising `critical_rebuttal_check`; multi-round apply-report chains
  exercising the §11 inner-link state and hard-required-original failure; archived
  1.0 alone retains `first_link_not_run`; `[LEGACY-NO-CONTRACT]` runs as
  a negative control.
- Cross-model authoring of additional surface variants (the `rq_framing_offlist` construction
  discipline) is the intended step before this set is used to gate a contract change.

## Fixture integrity

`scripts/check_persuasion_invariance_fixtures.py` is a structure-only gate, wired into CI —
twelve invariants over the index, the files on disk, and each `ground_truth.md`'s declared
`## Pair structure` table. It pins the scenario / arm / pair / cell inventory so nothing can be
deleted silently, checks relation-vs-expected-value agreement, binds each hash placeholder to
its own key (and requires all three keys present exactly once wherever an apply report
appears), requires pointer arms to resolve to real material in one hop, requires each arm's
section set to be EXACTLY what the scenario declares, and keeps the held-out boundary — no
material file may name the ground truth, and every language's scripted answer is checked
against every material file, so a cross-language paste is caught too.

Two limits worth stating rather than leaving to be discovered:

- **Invariant 7 pins the declared `claim_set` arrays, not the letter prose.** Claim ids are
  maintainer-assigned; nothing binds `C3` to a sentence. The check catches a drifted declaration,
  not a factual claim quietly added to one arm's letter. Only review catches that.
- **Invariant 12 compares which cells exist, never what they expect.** It matches
  `(arm-pair, observable, target)` as a multiset, so a collapsed or mis-targeted row fails — but
  a ground-truth table and the index can still agree on the cell set while disagreeing on a
  value, and that class is review's job.

The gate measures nothing about model behavior; baseline runs are the manual protocol above.

## Measurement contract (#654)

New scored rows opt into the `heldout-measurement/1.1` envelope
(`evals/heldout/MEASUREMENT_CONTRACT.md`, `suite_class: paired_controls`). Per
SD-11 this suite reuses the E4 machinery documented in
`evals/heldout/reviewer_seeded_defects/README.md`; the envelope layers judge and
adjudication disclosure on top without touching that machinery.
