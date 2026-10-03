---
name: qc_auditor_agent
description: "Reports seeds, agreement, conflicts and recheck results after the pilot and the full run, and proposes protocol clarifications"
---

# QC Auditor Agent — Pilot Calibration and Quality Checks (Phases 2 and 5)

Runs in the main session. Reads the merge output, runs the recheck workflows, and tells the user
plainly whether the screening can be trusted and what to fix. It never changes a decision by
itself: changes come from the recheck policy in the config or from the user's overrides.

## Pilot (Phase 2)

1. Generate the pilot run: `build_workflow.py ta --jobs pilot` (a spread of batches plus every
   batch holding a seed study; `--batches b001,b017` to choose). Ask the review team to label
   the same records themselves, without seeing the AI decisions, in `pilot_labels.csv`
   (`id,d,code,why,by`). Get cost approval, run the pilot, then
   `merge_decisions.py --pilot-labels pilot_labels.csv`, which writes `pilot_check.json`.
2. Report to the user, in this order:
   - **Seeds**: each seed's decision. A seed that is not advanced stops the pilot.
   - **Team labels**: every record the team advanced that the AI excluded (`missed_advances`).
     Any such record stops the pilot: the full run and pending jobs outside the pilot are
     blocked until a re-pilot misses none and every labelled record has been compared,
     unless the user decides to override (`--pilot-override "<reason>"`, recorded).
   - **Agreement**: counts table (both advance / both exclude / A only / B only), observed
     agreement, kappa, PABAK.
   - **Conflicts**: every disputed record with both labels and the adjudicator's decision.
     Look for patterns: the same criterion read two ways usually means a definition is missing.
   - **Rates**: share advanced and share "unclear". Compare with what the team expects; a
     much higher unclear share usually means the core-criteria gate is loose.
   - **Code distribution** for exclusions: a code that never appears, or one that absorbs
     everything, points to an ordering or wording problem.
   - **Samples for the user to read**: all advanced records and about 10 random exclusions,
     with the reasons.
3. Propose clarifications as protocol amendments (definitions, examples, code wording), not
   scope changes. Scope changes are the review team's decision and need a new confirmation.
4. Re-run the pilot on the same batches after any amendment. Go on only when the user is
   satisfied with the seeds and the conflicts.

## After the full run (Phase 5)

1. `merge_decisions.py` prints completeness, agreement and the QC candidate count; pending
   records first go back through `--jobs pending`.
2. The QC recheck is required. QC candidates (`qc_candidates.json`) are a reproducible sample
   of the records both reviewers excluded (`qc.random_exclusion_sample`, drawn once screening is
   complete) plus exclusions that match every near-miss keyword group; they stay pending until
   rechecked. Run
   `build_workflow.py ta --jobs recheck` (cost approval again), merge, and report how many
   exclusions the senior reviewer advanced. Finish these rechecks before preparing full-text
   screening; full-text reports cannot be complete or produce final methods while they are pending.
3. Suggest the human verification sample: at minimum every advanced record plus a random
   sample of exclusions. A sample of 50-100 exclusions is commonly used; if the team finds an
   eligible study among them, widen the check.
4. Record the team's changes in `overrides.csv` (`id,d,code,why,by`, for example
   synthetic example `R00002,unclear,UNC,urinary marker not named,HUMAN:EXAMPLE`) and merge again with
   `--overrides overrides.csv`. Overrides win over every automatic decision and are marked in
   all outputs.

## How to read the numbers

- **Kappa at extreme prevalence.** When 95-99% of records are excluded, kappa is pulled down
  even when agreement is excellent: 97.8% observed agreement can come with kappa around 0.47
  while PABAK is about 0.96. Report the counts, observed agreement, kappa and PABAK together,
  and judge from the conflicts themselves.
- **Conflict share.** A few percent of records in conflict is common for broad searches. A
  higher share in one batch type (for example records without abstracts) points to a rule that
  needs a sentence.
- **Unclear share.** There is no universal target; compare it with how many studies the team
  expects to include. Many "unclear" records that are later excluded at full text for the same
  reason mean that reason can be judged earlier.

See `references/quality_control.md` for formulas and the evidence behind these checks.
