# Eval preregistration: #907 ethics-committee letter with the mode command

Written before any priced run of case 08. Frozen at the commit that adds it. It follows `preregistration-907.md`, where case 04 fired the skill in 0 of 3 runs, so the change was not tested on the ethics-committee letter.

Case 08 (`08-ethics-committee-letter-command-zh`) is case 04 with `/academic-research-skills:ars-revision-coach` at the start of the user's message. The letter, the graders, and the run settings are the same as case 04. Because the user now names the mode, the results are not comparable with case 04.

## Bars

- **08 skill fired**: the `academic-paper` skill fires in a run. A run where it does not fire does not test the change; it is counted and reported, not scored for the bars below. With 0 runs that fire, the result is "not tested", not a pass.
- **08 tracker kept**: in every run where the skill fires, the answer takes the committee variant (concern IDs and a segmentation for the user to confirm). A miss means the new scope removed the variant from the one input it must keep; the change does not ship until the cause is read from the answer.
- **08 user's words quoted**: in every run where the skill fires, the answer quotes the user's words that name the committee (for example 「本校研究倫理審查委員會」). No grader checks this; the maintainer reads each answer, and the report says so. A miss means the quote rule did not take effect.
- **08 `tracker-covers-5` and `no-severity-words`**: reported per run. They are the case-04 graders, kept for comparison; they are not bars for this change.

## Arms

- **with-plugin**: `claude-opus-5-5`, `claude plugin eval <checkout> --eval-dir plugin-evals --ablation none --model claude-opus-5-5 --judge-model sonnet --runs 3 --case '08-*' --no-publish --max-cost-usd 2`, run from outside the plugin checkout. Expected cost from the case-04 run on 2026-11-19: about US$0.19 per run without the skill; a run with the skill can cost more. The runner is CLI-metered; the actual cost is read from `costUsd` and `judgeCostUsd` in the result file.
- No without-plugin arm (owner decision, 2026-11-19).

## Decoys

- None new. The graders are the case-04 graders. `tracker-covers-5` failed all 3 case-04 runs on 2026-11-19, where Opus 5.5 wrote its own table without the skill; that shows the grader does not pass an answer only because it has a table.

## Stop rules

- The runner's `--max-cost-usd 2` stops the run at US$2.
- No rerun to get a better number. If the skill fires in 0 of 3 runs, report "not tested" and stop.
- A run that times out counts as a failed run, not a skipped one.
- If a bar is missed, stop and report; do not change the case or the rules and rerun under this preregistration.

## Held-out exposure

| set | prior exposure (which runs, which models) | reservation (what this run may read) |
|---|---|---|
| none | case 08 is new; its letter is the case-04 letter, run on `claude-opus-5` (2026-09-12) and `claude-opus-5-5` (2026-09-24, 2026-11-19) | the run reads the case prompt and graders only |
