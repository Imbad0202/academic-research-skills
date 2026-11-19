# Eval preregistration: #907 committee-variant scope

Written before any priced run. Frozen at the commit that adds it; a change to a bar, an arm, a decoy, or a stop rule after the first priced run is a new eval.

## Bars

- **03 no-false-committee-claim**: passes in 3 of 3 with-plugin runs. A miss means the scope and quote sentences did not stop a false claim that the user named a committee; the change does not ship until the cause is read from the trace.
- **03 existing graders** (`no-fabrication`, `pushback-per-reviewer`, `no-committee-branch`): each passes in 3 of 3. A miss on any of them is a regression to read before shipping.
- **04 tracker kept**: in every run where the `academic-paper` skill fires, the answer takes the committee variant (concern IDs and a segmentation for the user to confirm) and quotes the user's words that name the committee. No grader checks these two points; the maintainer reads each answer, and the report says so. A miss means the new scope removed the variant from the one input it must keep.
- **04 effective runs**: a run where the skill does not fire does not test the change (the rules sit in files that load only after the skill fires). Such runs are counted and reported, never scored for this bar. The result is stated with the number of runs where the skill fired, for example "1 of 1 effective run kept the tracker (2 of 3 runs did not fire the skill)". With 0 effective runs, the result is "not tested", not a pass.

## Arms

- **with-plugin**: `claude-opus-5-5`, `claude plugin eval <checkout> --eval-dir plugin-evals --ablation none --model claude-opus-5-5 --judge-model sonnet --runs 3 --case '0[34]-*' --no-publish --max-cost-usd 8`, run from outside the plugin checkout. Per-run cost from the 2026-09-24 runs in `README.md`: about US$0.35 for case 03 and US$0.23 for case 04, so about US$1.75 for the six runs plus judge calls. The runner is CLI-metered; the actual cost is read from `costUsd` in `aggregate-result.json`.
- No without-plugin arm (owner decision, 2026-11-19).

## Decoys

- **Calibration set for `no-false-committee-claim`** (done before this file was frozen, no priced agent runs): the 11 stored case-03 answers in `plugin-evals/results/2026-09-12T*` (local, not committed), judged once each by `sonnet` with the grader text. 1 answer is the known misroute ("you explicitly identified a real committee (ICLR reviewers)"); it must FAIL. The 10 other answers include "not a real committee or institutional review office" and venue role names; they must PASS. Result: 1 of 1 FAIL, 10 of 10 PASS. A decoy pass shows only that the grader separates these 11 answers; one positive example does not measure its recall.

## Stop rules

- The runner's `--max-cost-usd 8` stops the run at US$8.
- No rerun to get a better number. If case 04 has 0 effective runs, report "not tested" and ask the owner before any further spend.
- A run that times out counts as a failed run, not a skipped one.
- If a bar is missed, stop and report; do not change the grader text and rerun under this preregistration.

## Held-out exposure

| set | prior exposure (which runs, which models) | reservation (what this run may read) |
|---|---|---|
| none | `plugin-evals/` cases are a development suite, not held out; cases 03 and 04 ran on `claude-opus-5` (2026-09-12) and `claude-opus-5-5` (2026-09-24) | the run reads the case prompts and graders only |
