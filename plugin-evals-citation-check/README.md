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
`no-overreach` (w0.5), plus `skill-fired` (`tool_used: Skill`, matching
`academic-research-skills:academic-paper`, display-only under ablation, never
moves Δ). The exact core-skill match excludes command-stub-only invocation.
With `--ablation none`, this grader contributes to the score; report loading
coverage separately from output-quality grades. Every llm rubric is written as "work through the checks
one at a time and quote the evidence"; keep that style when adding graders.

## Routing verification (2026-09-21)

Claude Code 2.1.278, `--ablation none --model sonnet --judge-model opus
--runs 1 --no-publish`, from a working directory outside the plugin checkout:

- All six positive cases called `academic-research-skills:academic-paper`.
  Cases 07 (format conversion) and 08 (unused Python imports) passed their
  negative-case rubrics; 08 made no Skill call.
- The full eight-case run passed six cases. Cases 01 and 02 hit the 600-second
  timeout **after** calling the core skill; their output-quality failures
  remain failures, not successful end-to-end runs.
- Isolated reruns: case 01 passed all rubrics; case 02 completed with the core
  skill invoked but failed `format-caught` and `no-false-positive` (score 0.75).
  It omitted the three-author 「等」 correction and incorrectly called the
  correctly stroke-ordered Chinese references misordered. These output-quality
  failures were the motivation for #882 below; the routing acceptance was not a
  suite-wide pass.
- A separate manual `/academic-research-skills:ars-citation-check` smoke,
  using case 03's synthetic material, called the core skill and read
  `citation_compliance_agent.md`. This is runtime evidence for citation-check,
  not a runtime coverage claim for all 13 mode commands.

These are loading/routing checks, not a with/without ablation or a measured
quality uplift. Earlier candidates are not pooled with this run: simply adding
nested Skill instructions still allowed command-only execution; hiding mode
commands without updating the SessionStart announcement led to attempted
calls to user-only commands. The announcement now names the core Skill-tool
targets for natural-language requests, including resume/compact events.

## Chinese format repair verification (#882, 2026-09-21)

The same case-02 prompt and **all original quality rubrics remain unchanged**.
Additional `agent-loaded` / `locale-guide-loaded` indicators record Read calls;
trace inspection checks that those reads succeeded. They are not quality scores.

The first repair candidate caught the missing three-author abbreviation and
accepted the correct stroke order in all three outputs. One output still
failed `no-false-positive` by promoting a DOI-prefix heuristic into a required
reference correction. The final candidate adds a general evidence boundary:
visible DOI syntax can be checked, but resolution/source claims require actual
resolver/source evidence. No fixture prefix or fixture author names are added
to the operative rules.

Final candidate, Claude Code 2.1.278, observed agent `claude-sonnet-5`, requested
judge `opus`, `--ablation none --no-publish`:

| Run | Result |
|---|---|
| Case 02, three attempts | Two completed outputs passed every original quality rubric and both loading indicators; one timed out after loading both files. |
| Full citation suite, one attempt per case | Cases 01 and 03–08 passed; case 02 timed out after loading both files (7/8 overall). |
| One isolated case-02 follow-up after other runs finished | Completed and passed every original quality rubric and both loading indicators. |

Across those final-candidate case-02 attempts: **3 passed, 2 timed out**.
Timeouts remain failures and are not omitted from denominators. No completed
final-candidate output reproduced either reported defect or the DOI-prefix
false positive. This is bounded synthetic evidence, not a claim of universal
accuracy, a clean full-suite run, or measured with/without uplift.

The separate [Chinese boundary suite](../plugin-evals-citation-locale/README.md)
checks that the repair still detects real ordering errors, preserves two-author
and disambiguation cases, and honors an explicit venue romanization override. All three boundary cases
passed on the final candidate (one run each).

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

- **Historical loading failure (2026-09-13 pilot).** The with-plugin arm
  invoked a command stub but could not find the mode prompt outside its cwd;
  `citation_compliance_agent.md` never loaded. Its near-zero Δ measured the
  stub plus base model, not the complete mode. #857 adds an explicit core-skill
  invocation and plugin-root references, and makes mode command stubs
  user-invocable only so automatic routing selects the core skill directly.
- **Historical trigger rate was 3 of 6 fire cases.** The old loose
  `input_match: academic` counted a command-stub invocation as firing. That
  number is not comparable to the stronger core-skill indicator now used.
  The Spanish trigger `verificar citas` subsequently arrived with #856;
  #858 adds English, Traditional Chinese, and Korean citation-check phrases.
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
