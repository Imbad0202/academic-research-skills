# plugin-evals-citation-check — `academic-paper` citation-check flow

Eval suite for `claude plugin eval`. One flow per suite: **citation-check**
(manuscript excerpt + reference list + a user-supplied "source pack" → citation
error report). Sibling of `plugin-evals/` (revision-coach); the two suites do not
share cases.

Quality spec (author-defined, 2026-09-13): the four citation failures that
matter are 無中生有 (a reference the user has no source for), 張冠李戴 (right
paper, wrong authors), 小題大作 (a hedged or minor finding cited as an established
result), and 以訛傳訛 (citing a retracted or concern-flagged paper as live
evidence). Every fire case supplies a complete source pack so these are
detectable **offline**; the sandbox has no network, so "無中生有" is graded as
"flags it as unverifiable and does not claim it exists", never as a real lookup.
Secondary axes: mechanical errors (orphans, numbering, et al., & vs and),
no false positives on clean entries, no claim of online verification, no
rewriting of the manuscript.

All inputs are synthetic (fictional papers, journals, authors; DOIs use the
reserved `10.5555` example prefix and graders explicitly allow the model to
say so).

## Run

```bash
claude plugin eval . --eval-dir plugin-evals-citation-check --ablation with-without --judge-model opus
```

Add `--no-publish` to keep the HTML report local. Headline number is Δ
(with-plugin score − without-plugin score). `runs: 3` per case. Cases pin
`model: sonnet` (the `/ars-citation-check` command pins sonnet itself), so the
judge must be a different, larger model — the runner's default judge is haiku,
which is both too small and never to be used here.

## Cases

| Case | Fires? | Style × language | Planted | Primary graders |
|---|---|---|---|---|
| 01-apa-en-misattribution | yes | APA 7 × en | wrong authors; ref not in pack; orphan in-text; uncited entry; & vs and | content-caught (llm w1.5) |
| 02-apa-zh-mixed-overclaim | yes | APA 7 × zh-TW mixed | claim strength exceeds source; Expression of Concern in pack; 三人未用「等」 | content-caught (llm w1.5) |
| 03-ieee-en-prose | yes | IEEE × en | wrong authors; simulation cited as production; [7] with no entry; numbering not in order of appearance | content-caught (llm w1.5) |
| 04-vancouver-en-terse-retraction | yes | Vancouver × en, style not named | retraction in pack; ref not in pack; year mismatch on one entry | content-caught (llm w1.5) |
| 05-apa-es-locale | yes | APA 7 × es (#850 scenario) | wrong authors; orphan in-text; uncited entry | content-caught (llm w1.5) + locale-respected (llm w1) + no-chinese-chars regex |
| 06-chicago-nb-en-footnotes | yes | Chicago NB × en | book not in pack; hypothesis cited as established; note without bibliography entry; pinpoint outside page range | content-caught (llm w1.5) |
| 07-neg-convert-apa-to-ieee | no (format-convert shape) | — | — | is-conversion (llm) + numbered-in-order regex + not-audit-report regex |
| 08-neg-python-unused-imports | no | — | — | regex on the two unused imports co-occurring with an "unused" statement + `tool_used: Skill` with `min: 0, max: 0, arm: both` (scored in both arms, unlike the display-only `skill-fired`) |

Shared graders on 01–06: `content-caught` (w1.5), `format-caught` (w0.5, spec-
level mechanics), `no-false-positive` (w1), `honest-unverified` (w1),
`no-overreach` (w0.5), plus `skill-fired` (`tool_used: Skill`, display-only under
ablation, never moves Δ). Every llm rubric is written as "work through the checks
one at a time and quote the evidence"; keep that style when adding graders.

## Side channels and ceilings (pilot 3, 2026-09-13, 1 run × 2 arms, sonnet agents)

| Channel | Ceiling | Observed max |
|---|---|---|
| wall-clock per run | 600 s (`timeout_seconds`; over = score 0) | 142 s |
| turns per run | 20 (`max_turns`) | 7 |
| agent cost per run | none enforced | $0.45 |
| full pilot (8 cases × 2 arms × 1 run, incl. opus judge) | — | $4.65 |

Pilot 1 (before calibration, opus agents) cost $6.89 and peaked at 155 s / 7
turns / $0.83 per run; pilot 2 (sonnet agents) cost $3.99. Pilot 3 followed a
cross-model review of the suite (13 findings, 12 applied: disputable plantings
replaced, presence regexes tied to an "unused" statement, metadata preservation
required on the conversion negative, real journal names replaced).

## Known caveats

- **The with-plugin arm cannot load the mode's own prompt in the eval sandbox.**
  `/ars-citation-check` is a command stub that tells the model to read
  `MODE_REGISTRY.md` and `academic-paper/SKILL.md`; the plugin directory is
  outside the sandbox cwd, `Glob`/`Read` there are denied under `dontAsk`, and the
  model never falls back to invoking the `academic-paper` skill itself
  (`--allow-tools 'Read(<plugin>/**)'` does not help: the model does not know the
  path). So in this suite the with arm ≈ command text + base model, and
  `citation_compliance_agent.md` never runs. Δ ≈ 0 across the suite is the
  honest current reading, not a calibration failure. Fix belongs in the plugin
  (command should invoke the skill, or carry `${CLAUDE_PLUGIN_ROOT}` paths): #857.
- **Trigger rate with sonnet is 3 of 6 fire cases** (01, 02, 06 fired; 03 prose
  "check the citations", 04 terse "look over the refs", 05 Spanish did not).
  05 is exactly the #850 gap: the skill description carries no Spanish
  triggers. Display-only; tracked in #858 (triggers) and #850 (locale).
- **03 was a `/ars-citation-check` slash-command case in pilot 1.** The
  without-plugin arm answered "Unknown command" and Δ was +0.70 for the wrong
  reason (command existence). Switched to a prose trigger.
- **Clean entries must be clean at the claim level too.** Pilot 1 failed
  `no-false-positive` in 5 of 6 fire cases because the planted "clean" sentences
  overstated their own abstracts and the models (correctly) said so. Inputs were
  tightened and the grader now defines a false positive narrowly (entry-level
  error, listed under corrections, or proposed change); claim-wording comments,
  DOI-prefix remarks, and conditional house-style notes are allowed.
- **02 order of scripts is not graded.** The reference list puts English
  entries before Chinese ones; the author accepts either order for Taiwan
  journals, so `format-caught` only checks the 「等」 rule.
- **02 bold vs italic on Chinese journal names** is house style, not an error;
  entries are plain and the grader treats either remark as neutral.
- **no-overreach** allows per-sentence replacement wording for a misrepresenting
  claim and an *offer* to redraft; a rewritten whole excerpt or design-level
  critique fails it.
- **Regex presence checks are secondary.** `orphan-named` (w0.5) only proves the orphan key was mentioned; the paired llm `format-caught` decides whether it was flagged. In 08 the regexes require the import name within 120 characters of an "unused" statement (headings such as 「沒用到的引用：」 on the line above count).
- **04 does not require the style to be named.** Both arms fixed the planted year mismatch without ever writing "Vancouver"; the grader only fails a response that applies author-date rules to the numbered list.
- **07 and 08 show Δ 0** — the base model already handles them. They stay as
  regression guards (07 must not become an audit report; 08 must not fire).
