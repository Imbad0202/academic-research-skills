# plugin-evals — `academic-paper` revision-coach flow

Eval suite for `claude plugin eval`. One flow per suite: **revision-coach** (reviewer
comments → Revision Roadmap + Response Letter skeleton; committee-correspondence
variant when the user names a real committee).

Quality spec (author-defined, 2026-09-12): the primary axis is **no unauthorised
rewriting** — the response must not draft manuscript prose, must not change things
no reviewer asked for, and must not assert results or changes that have not
happened. Secondary axes: no comment dropped, push-back allowed on wrong
comments, committee letters get a tracker with no peer-review grading.

All inputs are synthetic (fictional studies, no real names or institutions).

## Run

```bash
claude plugin eval . --eval-dir plugin-evals --ablation with-without --judge-model sonnet
```

Add `--no-publish` to keep the HTML report local. Headline number is Δ
(with-plugin score − without-plugin score). `runs: 3` per case.

## Cases

| Case | Fires? | Shape | Primary grader |
|---|---|---|---|
| 01-journal-mixed-format-zh | yes | 3 reviewers, mixed numbered/paragraph/bullet, abstract + methods excerpt attached | no-rewrite (llm, w1.5) |
| 02-decision-letter-email-en | yes | editor email, unnumbered paragraphs, one factually wrong reviewer point | no-rewrite (llm, w1.5) |
| 03-iclr-rebuttal-en | yes | OpenReview scores + "should we push back" | no-fabrication (llm, w1.5) |
| 04-ethics-committee-letter-zh | yes (committee variant) | formal REC letter, user names the committee | tracker-covers-5 (llm, w1.5) + regex on grading labels (w0.5) |
| 05-terse-contradictory-zh | yes | terse opener, contradictory reviewers, scope-changing request | scope-creep-flagged (llm, w1.5) |
| 06-neg-existing-rebuttal-draft-zh | no (rebuttal-audit shape) | comments + existing draft, one point missed | no-new-skeleton (llm, w1.5) + regex |
| 07-neg-landlord-letter-zh | no | non-academic letter | regex + llm + Skill not called |

`skill-fired` (`tool_used: Skill`) on 01–05 is display-only under ablation and
never moves Δ. So is `no-committee-branch` on 03 (`arm: with-only`, #854).

## Routing retest (2026-09-21, #854)

After the #857 command-loading and SessionStart routing changes, case 03 was
run three times with Claude Code 2.1.278, `--ablation none --model opus
--judge-model opus --runs 3 --case '03-*' --no-publish` from outside the plugin
checkout. All three called `academic-research-skills:academic-paper`, read
`revision_coach_agent.md`, and passed the existing no-fabrication and pushback
rubrics. Trace/output inspection found **0 of 3** applying the committee
variant. That branch assessment is manual, not an assertion made by the
existing graders; the same-family judge is not independent validation.

The observed model ID was `claude-opus-5`. This small synthetic retest does
not rule out the intermittent failure or close #854. Earlier intermediate
candidates included timeouts and are not counted as completed passing runs
here. No committee guard or agent definition changed.

## Committee-branch guard (2026-09-24, #854)

The counts and costs in this section are maintainer-reported: they come from
local runs whose outputs are not committed (`plugin-evals/results/` is ignored
by git).

Case 03 gained `no-committee-branch` with the #854 guard (see `CHANGELOG.md`): a
with-only regex that fails when the answer emits a line of the committee
variant's output, that is, a concern-tracker or preserved-source heading or bold
label, a concern-ID heading or comment, the status line, or the blockquoted
human-subjects footer that `committee_correspondence_protocol.md` requires. A
heading or bold-label line with "no", "not", "none", "without", or "n/a" in it
does not count, and an answer that declines the variant in prose passes even
when it names the variant's parts.
`scripts/test_check_committee_correspondence.py` runs examples of both through a
JavaScript `RegExp` with the grader's flags, because the eval runner is a
JavaScript program. Against the maintainer's 2026-09-12 results it flags the two
runs named under Known caveats and none of the other nine, the without-plugin
arms included. Neither flagged run used the protocol's required strings; the
heading pattern caught both. The grader reads only the answer text, so it misses
a run that only announces the branch, or only writes the bundle's files, without
printing their lines. It would flag a peer-review answer that titles a section
"concern tracker" with no negating word, and a refusal that quotes one of those
lines on a line of its own.

Retest with Claude Code 2.1.281, `--ablation none --model claude-opus-5-5
--judge-model sonnet --runs 7 --case '03-*' --no-publish`, from outside the
plugin checkout: with the guard, **0 of 7** runs took the branch; on unchanged
`main` with only the new grader added, also **0 of 7** (5 of those 7 read
`revision_coach_agent.md`). The misroute was seen on `claude-opus-5`, and
Opus 5.5 did not reproduce it without the guard, so this retest shows no
effect of the guard; the guard is prompt-level and its effect is unmeasured.
None of the fourteen runs built the Revision Roadmap or the response skeleton;
each answered the push-back question directly. Cost: US$2.46 with the guard,
US$2.70 on `main`. The retest ran on an earlier text of the guard: the sentence
in `committee_correspondence_protocol.md` came later, and the mode table then
gave the variant its own row, which the final change dropped. It was also graded
with an earlier text of `no-committee-branch`; re-graded with the final text,
the counts are the same.

Case 04 (the ethics-committee letter), 7 runs on the final text with the same
settings: the skill fired in 2 runs, and both took the committee variant
(concern IDs and a segmentation for the user to confirm); `tracker-covers-5`
passed in 1 of 7. In the other 5 runs Opus 5.5 answered without invoking the
skill. The guard sits in files that load only after the skill fires, and the
skill descriptions and the SessionStart hook are unchanged from `main`, so those
5 runs do not test it. The stored 2026-09-12 runs on `claude-opus-5` fired the
skill in 2 of 2. Cost: US$1.58.

## Side channels and ceilings (pilot 2026-09-12, 1 run × 2 arms)

| Channel | Ceiling | Observed max |
|---|---|---|
| wall-clock per run | 600 s (`timeout_seconds`; over = score 0) | 322 s |
| turns per run | 15 (`max_turns`) | 10 |
| agent cost per run | none enforced | $0.80 |
| full pilot (7 cases × 2 arms × 1 run) | — | $4.63 |

## Known caveats

- **03 fires since #851.** Before the #851 description fix the with-plugin arm
  answered the ICLR "should we push back" prompt without invoking the skill
  (0 of 2 pilots). After the fix: 7 of 7 verification runs invoked it. One of
  those seven said it was applying the #668 committee-correspondence branch to
  the ICLR peer reviews (the skill forbids inferring committee authority), and a
  second produced that branch's shape without naming it; four said the
  reviewers are peer review and one did not say. Tracked as #854 (see
  Committee-branch guard above).
- **Judge style matters.** With the runner's judge, rubrics phrased as a bare
  list of claims produced repeated 3-vote FAILs on outputs that a reasoning
  judge (same model, asked to quote evidence first) passed. Every llm rubric in
  this suite that showed that pattern (02 all-covered, 03 no-fabrication,
  03 pushback-per-reviewer) is written as "work through the checks one at a
  time and quote the evidence"; keep that style when adding graders.
- **no-rewrite is judged, not regex-checked.** Manuscript prose vs. quoted
  reviewer text cannot be told apart lexically. A single suggested sentence of
  manuscript text is borderline and judges have passed it.
- **05 and 07 show Δ 0** — the base model already handles them. They stay as
  regression guards.
