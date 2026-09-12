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
never moves Δ.

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
  those seven misrouted ICLR peer reviews into the #668 committee-correspondence
  branch (the skill forbids inferring committee authority); the other six
  reasoned explicitly that anonymous conference referees are peer review.
  Tracked separately from #851.
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
