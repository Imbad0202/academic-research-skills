# Eval preregistration: #907 case 08 retest on the final rule text

Written before the retest. Frozen at the commit that adds it. It follows `preregistration-907-command.md`, whose case 08 runs used an earlier text of the scope and quote rules. Those runs stay as they were reported; this file does not change their bars.

Case 08 (`08-ethics-committee-letter-command-zh`) is unchanged: the case-04 letter with `/academic-research-skills:ars-revision-coach` at the start of the user's message.

## Bars

- **Effective run**: the `academic-paper` skill fires. The `skill-fired` grader checks only that the Skill tool was called, so the maintainer reads the skill name in each run's trace. A run that calls another skill, or no skill, does not test the change; it is counted and reported, not scored for the bars below. If the trace does not show the skill name, the run is reported as "skill not verified" and is not scored. An effective run whose answer was not kept is reported as "answer not readable"; it does not count as meeting the bars, and the result names it (for example, "2 of 2 readable effective runs met both bars; 1 effective run was not readable"). With 0 readable effective runs, the result is "not tested", not a pass.
- **Quote kept**: in every readable effective run, the reply starts with the user's own words that name the committee, in quotation marks (for example 「本校研究倫理審查委員會」). A miss means the run did not meet the bar; the cause is read from the answer and the trace before the report states one.
- **Variant kept**: in every readable effective run, the answer takes the committee variant. The protocol asks the coach to show the segmentation and wait for the user's confirmation before it makes the concerns, so a first answer passes this bar if it either shows a segmentation of the letter and asks the user to confirm it, or gives concern IDs of the committee tracker. An answer that gives a peer-review Revision Roadmap does not pass, even if it numbers its rows as concerns. A miss means the run did not meet the bar; the cause is read from the answer and the trace before the report states one.
- No grader checks the two bars above; the maintainer reads each answer, and the report says so.
- **`tracker-covers-5` and `no-severity-words`**: reported per run. They are the case-04 graders, kept for comparison; they are not bars for this change. `tracker-covers-5` asks for the five items as tracked items, so a first answer that stops at the segmentation can fail it while it meets the bars above.

## Arms

- **with-plugin**: `claude-opus-5-5`, `claude plugin eval <checkout> --eval-dir plugin-evals --ablation none --model claude-opus-5-5 --judge-model sonnet --runs 3 --case '08-*' --no-publish --max-cost-usd 2.5`, run from outside the plugin checkout.
- Cost: the owner's cap for this retest is US$4 (2026-11-19). The runner checks `--max-cost-usd` before it starts each run, so the last run can go over it. On 2026-11-19 the two case-08 runs cost US$1.34 and US$1.13 for the agent and US$0.02 in all for the judge. The worst case is the flag plus one run plus judge calls: with a run at US$1.34 and judge calls at about US$0.06, that is about US$3.9. A run that costs more than about US$1.44 can take the total past US$4; the report then states the overrun. The actual cost is read from `costUsd` and `judgeCostUsd` in the result file.
- No without-plugin arm (owner decision, 2026-11-19).

## Decoys

- None new. The graders are the case-04 graders, unchanged. `tracker-covers-5` failed all 3 case-04 runs on 2026-11-19, where Opus 5.5 wrote its own table without the skill.

## Stop rules

- The runner's `--max-cost-usd 2.5` stops new runs once the spend reaches US$2.5.
- No rerun to get a better number. If there are 0 readable effective runs, report "not tested" and stop.
- A run that times out counts as a failed run, not a skipped one.
- If a bar is missed, stop and report; do not change the case or the rules and rerun under this preregistration.

## Held-out exposure

| set | prior exposure (which runs, which models) | reservation (what this run may read) |
|---|---|---|
| none | case 08 ran 2 times on `claude-opus-5-5` on 2026-11-19 under `preregistration-907-command.md`; its letter is the case-04 letter, run on `claude-opus-5` (2026-09-12) and `claude-opus-5-5` (2026-09-24, 2026-11-19) | the run reads the case prompt and graders only |
