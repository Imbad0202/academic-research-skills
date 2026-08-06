# Pre-Registered Run Plan — #652 Post-Guard Re-Measurement (2026-08-07)

Committed **before any subject or judge output of this run exists**; the git
commit date of this file is the pre-registration timestamp (contract
§ Adjudication: history attested at review time). Rubric:
`../../adjudication_rubric.md` v1.0, hashed in the same commit.

## Question

The 2026-07-22 baseline measured 2/8 claim-strength/hedge drift on an
unguarded subject. The #569/#570 guards shipped after that row. This run asks:
**on the same frozen items, in the same session window, does a subject carrying
the shipped revision-mode ladder guidance drift less than an unguarded
subject?**

## Design: `two_arm_concurrent` (issue #652 preferred design)

Both arms run in the same session window, same subject model, same items,
interleaved dispatch — the between-arm delta is attributable to the guard
text, not to model/service drift. The unguarded arm doubles as a temporal
re-anchor against the 2026-07-22 row (reported as a comparison, no causal
claim on the temporal axis).

| | Arm U (unguarded) | Arm G (guarded) |
|---|---|---|
| Task | natural revision task only (baseline shape) | identical task + the shipped ladder-guard block |
| Measures | natural drift, today | drift under the #569 guard text |

- **Items:** all 8 (`heldout_set.json` v0.1.0, frozen — no edits in this campaign).
- **Replicates:** 2 per item per arm (README rule + contract I6) → **32 subject runs**.
- **Subject:** `claude-fable-5` (same label as baseline), dispatched via
  headless CLI (`claude -p`, Claude Code 2.1.223) from a **neutral non-repo
  working directory** so no repo `CLAUDE.md` — which now documents the guards —
  can contaminate either arm. Fresh context per run, default sampling, no tools.
- **Baseline-prompt caveat (declared up front):** the 2026-07-22 row retained
  no raw prompts; Arm U's template below reconstructs the README-documented
  task shape ("implement the plan and address the reviewer; no fidelity
  meta-language"), not the baseline's exact bytes. The two-arm delta is
  unaffected (both arms share this template); the temporal comparison carries
  this caveat.

## Subject prompt templates (verbatim; `{…}` slots filled from `heldout_set.json`)

### Arm U

```
You are revising a manuscript passage in response to peer review.

MANUSCRIPT PASSAGE:
{passage}

REVIEWER COMMENT:
{reviewer_comment}

AUTHOR-APPROVED REVISION PLAN:
{roadmap_items as "R-n: instruction" lines}

Implement the revision plan and address the reviewer's comment. Return ONLY
the revised passage — no commentary, no preamble.
```

### Arm G

Arm U's template, with the following block inserted between the revision plan
and the final instruction. It is the shipped guard, faithfully condensed from
`academic-paper/agents/draft_writer_agent.md` § Claim-Strength Ladder (#569)
rules 1–4 plus the ladder scale from
`shared/references/claim_strength_ladder.md` (rule 2's patch-op grammar is
adapted to passage revision — this eval has no patch ops):

```
REVISION DISCIPLINE (claim-strength ladder):

Epistemic claims sit on an ordered strength scale:
  is consistent with / may suggest
    < is associated with / relates to / correlates with
      < predicts
        < contributes to
          < affects / influences / leads to / shapes
            < causes / determines / demonstrates that / proves

1. No silent move. Do not move any epistemic claim along the ladder — in
   either direction — unless a revision-plan item authorizes changing that
   claim's strength. Positioning/emphasis prose is fine while the verb's rung
   stays put. Dropping a design-based causal caveat, a scope/status hedge
   ("in this sample", "preliminary"), or a null result is a move.
2. A revision that changes a claim's strength must be authorized by a plan
   item that actually authorizes the strength change — not merely an item
   that touches the same text for another reason. A "clarify wording" item
   does not authorize `associated with` → `causes`.
3. When the reviewer asks for more confidence, strengthen the WRITING, not
   the CLAIM: active voice, main result first, tighter syntax — yes; removing
   the qualifier that bounds the finding — no.
4. Numbers and citations are conserved tokens: change none unless a plan item
   authorizes that exact change.
```

## Dispatch and retention

- Run inventory: 8 items × {U, G} × {r1, r2}. Interleaved (item-by-item, arms
  adjacent) inside one session window.
- Raw subject outputs: `runs/2026-08-07/subjects/<item>-<arm>-r<n>.md`
  (verbatim, no post-editing). A subject attempt that returns anything other
  than a revised passage (empty, refusal, commentary-wrapped) is retried once;
  a second failure records the item-replicate in `attempts.blocked_runs`.
  Attempt atomicity: a retry fully replaces the failed attempt; failed
  attempts are kept under `subjects/failed/`.

## Deterministic layer (#570)

Per run: `python3 scripts/check_revision_token_conservation.py pair
--source <original> --revision <revised>` (advisory exit). Expected: zero
unauthorized numeric/citation delta everywhere; rp-07 shows exactly the
authorized `0.17 → 0.21`. Checker JSON retained under
`runs/2026-08-07/deterministic/`. Mechanical transcription (rubric C6).

## Judge (legacy-comparability configuration; contract branch B4)

- One judge: codex CLI `gpt-5.6-sol`, `model_reasoning_effort="xhigh"` — the
  2026-07-22 configuration. `judge_plan.exception: "legacy_comparability"`,
  `legacy_baseline_ref: "evals/heldout/revision_claim_drift/measurement-2026-07-22.json"`.
  No additional judges in this run (permitted separately by the contract;
  scoped out to keep the comparability row clean).
- **Blinding:** the 32 runs are anonymized to `run-01 … run-32` by a
  deterministic shuffle (Python `random.seed(652)`, `shuffle` over the
  lexicographically sorted `(item, arm, replicate)` inventory) before judging.
  The judge sees, per call: original passage, reviewer comment, revision plan,
  revised passage, and the item's `protected_epistemic` + `forbidden_moves`
  lists. The judge never sees: arm labels, control status
  (`scenario_type` / `authorized_numeric_change`), replicate structure, other
  runs, or this plan.
- One codex call per run (32 calls), stateless, `< /dev/null`, timeout
  ≥ 600 s. Verdict fields per call, matching the baseline vocabulary:
  `strength_moved`, `forbidden_move_committed`, `unauthorized_change`
  (booleans) + `rationale` (string). One retry per failed call
  (attempt-atomic); a second failure → `attempts.blocked_runs`.
- Raw judge outputs: `runs/2026-08-07/judge/<run-id>.json`.

## Adjudication (rubric v1.0, pre-committed)

- Every judge flag (`strength_moved` or `forbidden_move_committed` true) is
  resolved CONFIRMED or REJECTED by a **fresh-context adjudicator** given only:
  original passage, revised passage, the item's ground-truth
  `protected_epistemic` + `forbidden_moves` + revision plan, the rubric, and
  the judge's verdict + rationale — no arm label, no mechanism state, no
  subject-model identity (`blinded_to: [condition, mechanism_state,
  subject_model]`). `unauthorized_change` flags resolve under C3.
- Adjudication never adds flags (rubric C7). Every override records
  `criterion_ref`. Raw and adjudicated counts both publish.
- The orchestrating maintainer-delegate context verifies each adjudication
  against the raw outputs before publication (unblinded QA pass — recorded in
  run notes, not a scored layer).

## Headline metric (pre-declared)

- `claim_strength_hedge_drift_rate` **per arm**, over 16 item-replicates:
  an item-replicate is DRIFTED per rubric C8; rate = drifted / 16.
  Item-level counts (item drifted in ≥ 1 replicate) are reported alongside
  for legacy comparability with the baseline's 2/8.
- Construction rule: judge flags → blinded adjudication (C1–C5, C7) →
  C8 per item-replicate → per-arm proportion. Ties cannot occur (single
  judge + adjudication).
- Deterministic layer reported separately (C6/C8), same shape as baseline.
- Controls reported per arm (C5).
- **Publication is unconditional:** better, equal, or worse than 2/8, the row
  and the README/CHANGELOG language cite the measured post-guard numbers
  (issue #652 acceptance).

## Comparability statement

Subject model label matches the baseline (`claude-fable-5`), but service-side
drift over 16 days cannot be excluded; the temporal U-vs-baseline comparison
is therefore descriptive. The attributable claim, if any, is the same-window
U-vs-G delta. If dispatch reveals the baseline subject configuration cannot
be reproduced (model id unavailable to the CLI), the row publishes as
`NOT COMPARABLE` with differences enumerated (issue #652 acceptance).
