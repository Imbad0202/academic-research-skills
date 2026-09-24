# #133 routing fixtures: calibration log

Each entry records one calibration pass: the condition, the scoring rules fixed before
the run, and the per-fixture result against every field of the fixture's `expected.yaml`.
A pass is a smoke-test observation on one session per fixture, not a measured rate.

## 2026-09 pass (#889): Claude Opus 5.5 and Claude Fable 5.1

### Condition

- **Date and models**: 2026-09-23, all three passes; `claude-opus-5-5` and
  `claude-fable-5-1` through `--model` on Claude Code 2.1.280. The init event of every
  session confirms the model id, except fixture 04 (see the notes below).
- **Subject**: a fixed checkout of this repository at `95929c00`, never modified during
  the run.
- **Subject amendment (after the first probes, before any fixture ran).** The first
  probes ran on a git worktree under the operator's home directory, and both failed:
  each session reported the operator's user-level `CLAUDE.md` and ran under the
  operator's output style, although `CLAUDE_CONFIG_DIR` was empty. Two leak paths were
  found on Claude Code 2.1.280. The upward walk from the session's working directory
  reached `~/.claude/CLAUDE.md` in an ancestor directory, and a git worktree resolved
  project-local settings from the main checkout's untracked
  `.claude/settings.local.json`. Every pass below therefore runs on a standalone clone
  at the stated commit, outside the home directory, and each pass's probes on both
  models reported only the project `.claude/CLAUDE.md`, the `v3.9.2` heading, no
  output style, and no user-level instruction.
- **Install condition: repo clone.** Each session's working directory is that checkout,
  so the project `.claude/CLAUDE.md` (Routing Discipline) loads; ARS is loaded from the
  same checkout with `--plugin-dir`. This pass says nothing about plugin or skills-copy
  installs, where the routing prose does not load by the Claude Code documentation
  (#892).
- **Isolation**: one `claude -p` session per fixture, each with a fresh, empty
  `CLAUDE_CONFIG_DIR` and an environment allowlist, so no user-level `CLAUDE.md`,
  settings, output style, or language setting reaches the session. One contamination
  probe per model runs first; its init event is recorded below.
- **Tools**: Bash, Write, Edit, MultiEdit, NotebookEdit, WebFetch, WebSearch, Agent,
  Task, and TodoWrite are disallowed; Read, Glob, Grep, and Skill stay available, so a
  routing decision is observable as a clarifying question, a Skill call, or the start of
  the task.
- **Effort**: each model's Claude Code default (no `--effort` flag); the value is
  recorded when the CLI reports it. Claude Code 2.1.280's init event reports no effort
  value, so none is recorded.
- **Credential**: a subscription OAuth token (`claude setup-token`), passed only in the
  child environment.
- **Transcripts**: stream-json, every assistant message kept; not committed (they carry
  session identifiers). The observed-response column quotes the deciding part.

### Scoring rules (fixed before the run)

A fixture passes only when every field below passes.

- **`expected_routing_class: clarify`** passes when the first assistant turn asks the
  user to choose a workflow or deliverable (enumerated options or an equivalent explicit
  question), invokes no Skill that starts phase work, and does not begin producing a
  deliverable.
- **`expected_routing_class: proceed`** passes when the first assistant turn does not ask
  the user to choose among workflows and starts the task: a Skill call, a read of the
  chosen skill or agent file, or the work itself. Asking for a missing input file after
  naming the chosen route still counts as proceed.
- **`expected_destination: clarification_only`** passes when no Skill is called and no
  phase work starts.
- **`expected_destination: <skill>:<mode>`** passes when the Skill call names that skill
  (with or without the plugin prefix) and the call or the response names or evidently
  starts that mode. With no Skill call, it passes only if the response names that skill
  and mode as the route it is taking. A different skill or mode fails.
- **`expected_destination: <agent>`** passes when the response dispatches, reads, or
  explicitly acts as that agent.
- **`escape_hatch_applied: true`** passes when the response does not clarify and no
  forwarded instruction (Skill arguments or quoted task text) carries the `[direct-mode]`
  token. **`false`** passes when the fixture's other fields pass without the escape hatch
  being treated as honored.
- **`direct_mode_stripped_message`** passes when forwarded Skill arguments carry the
  stripped message; when nothing is forwarded, it is recorded as not observable, which
  is not a failure.

### Notes that apply to every pass

- **Fixture 04 does not measure either model.** `/ars-lit-review` pins `model: sonnet`
  in its command frontmatter, so the session switches to `claude-sonnet-5` for that
  fixture in both arms (the init event records the model). Its result is reported as a
  Sonnet 5 observation.
- **No attachment exists.** The fixtures describe attached files that are not supplied,
  and every read of a path named in a message was refused by the session's permission
  check. A session that names its route and asks for the missing files passes the
  routing class under the rules above.
- **No session read the answers.** No tool call or tool result in any pass contains
  `issue_133_routing`, `expected.yaml`, `rationale.md`, or `CALIBRATION_LOG` (checked
  over the full stream-json of every session).
- **Probes.** Before each pass, the probe on each model ran in that pass's clone and
  reported the project `.claude/CLAUDE.md` as the only instruction file, the routing
  heading's version (3.9.2), no output style, and no user-level instruction; its init
  event showed the requested model, output style `default`, and no API key source.
- **Cost.** The CLI reported 19.27 USD (pass 1), 19.19 USD (pass 2), and 19.02 USD
  (pass 3) of API-equivalent cost for both models together; the runs used a
  subscription token.

Field abbreviations: RC routing class, D destination. A failure names every
independent field that failed; the other fields passed. `escape_hatch_applied: false`
passes only when the other fields pass, so it fails with them and is not listed again.
In every pass, `direct_mode_stripped_message` passed on fixture 07 (the Skill arguments
carry the stripped message) and was not observable on fixture 05 (nothing forwarded),
and no Skill argument carried the `[direct-mode]` token.

### Pass 1: subject `95929c00`, routing prose as shipped

| Fixture | Expected | Claude Opus 5.5 | Claude Fable 5.1 |
|---|---|---|---|
| 01 cross-phase | clarify | pass: a-d workflow options, no Skill call | pass: a-d workflow options, no Skill call |
| 02 literature only | `academic-paper:lit-review` | pass: Skill `academic-paper`, "lit-review"; asked for folder access and for the paper configuration to be confirmed | pass: Skill `academic-paper`, "mode=lit-review" |
| 03 no materials | clarify | pass: stage options a-d | pass: stage options a-d |
| 04 slash command | `academic-paper:lit-review` | **fail (RC)**, on `claude-sonnet-5`: Skill `academic-paper` "lit-review", then offered to route to `deep-research` lit-review instead ("Say the word and I'll invoke it") and asked "Which would you like?" | pass, on `claude-sonnet-5`: Skill `academic-paper` "lit-review"; asked for the papers or for leave to search within the same mode, and mentioned `deep-research` lit-review only as a recommendation (scored pass because both offered paths stay in the invoked mode; a second reviewer read it as a workflow choice) |
| 05 direct mode | `bibliography_agent` | **fail (D)**: "I haven't started `bibliography_agent` yet because the 30 PDFs didn't come through"; the agent was named, never dispatched or read | pass: read the headings of `deep-research/agents/bibliography_agent.md` (Grep); "route straight to the deep-research `bibliography_agent`" |
| 06 token mid-message | clarify | pass: said the token was ignored; a-d options | pass: said the token was ignored; a-d options |
| 07 token, capitalized | `academic-paper:abstract` (the `abstract-only` mode) | pass: Skill `academic-paper`, "abstract-only" | pass: Skill `academic-paper`, "abstract-only" |
| 08 draft + abstract + literature + reviews | clarify | pass: a-d workflow options | pass: a-d workflow options |
| 09 Korean revise | `academic-paper:revision` | pass: "`revision` 모드로 진행하려고" | pass: Skill `academic-paper`, "mode=revision" |
| 10 Korean review | `academic-paper-reviewer:full` | pass: Skill reviewer, "full mode" | pass: Skill reviewer, "mode: full" |
| 11 Spanish revise | `academic-paper:revision` | **fail (RC, D)**: "necesito que elijas cómo pulirlo", four routes; read revision mode as needing reviewer comments; the Skill call named no mode | **fail (RC)**: "Indica también qué ruta prefieres", two routes, neither of them revision mode alone; the Skill call named `revision`, so D passes by the rule's wording |
| 12 Spanish review | `academic-paper-reviewer:full` | **fail (RC)**: Skill reviewer "full", then "Confírmame cuál quieres": review, edit, or citations | pass: Skill reviewer "full"; asked only for the manuscript |
| **Total** | | **8 of 12** (8 of 11 without 04) | **11 of 12** (10 of 11 without 04) |

### Change after pass 1 (`46a563a9`)

Neither model passed every fixture, so the routing prose was tightened, not the fixtures
(`.claude/CLAUDE.md` § Routing Discipline and
`shared/references/intent_clarification_protocol.md`). Step 1 now says a request stays
explicit when the mode's usual input is absent or a word has other everyday senses,
with the two observed cases as examples: a revision request without reviewer comments
is revision mode's "feel certain sections need improvement" case, and "revisar
artículo" is the reviewer's trigger. Step 0 said that when the named agent or skill
needs inputs the message does not supply, its file is read, the user is asked for what
it requires, and no other workflows are offered.

### Pass 2: subject `46a563a9`

| Fixture | Expected | Claude Opus 5.5 | Claude Fable 5.1 |
|---|---|---|---|
| 01 cross-phase | clarify | pass: a-d workflow options, no Skill call | pass: a-d workflow options, no Skill call |
| 02 literature only | `academic-paper:lit-review` | pass: Skill `academic-paper`, "mode=lit-review"; asked for folder access and for the setup to be confirmed | pass: Skill `academic-paper`, "lit-review"; "Routing is settled"; asked for folder access |
| 03 no materials | clarify | pass: stage options a-d | pass: stage options a-d |
| 04 slash command | `academic-paper:lit-review` | pass, on `claude-sonnet-5`: Skill `academic-paper`, "mode: lit-review"; asked only for the papers | pass, on `claude-sonnet-5`: Skill `academic-paper`, "mode: lit-review"; asked for the papers or for leave to search within the same mode |
| 05 direct mode | `bibliography_agent` | pass: read `deep-research/agents/bibliography_agent.md`, then asked for the files | pass: read the agent file; asked for the folder and the research question, with criteria optional |
| 06 token mid-message | clarify | **fail (RC, D)**: read `deep-research/agents/bibliography_agent.md`; "Once I have them, I'll run bibliography_agent directly, with no workflow questions"; the token was not mentioned | pass: said the token was ignored; a-d options |
| 07 token, capitalized | `academic-paper:abstract` (the `abstract-only` mode) | pass: Skill `academic-paper`, "abstract-only mode" with the stripped message | pass: Skill `academic-paper`, "abstract-only" with the stripped message |
| 08 draft + abstract + literature + reviews | clarify | pass: a-d workflow options | pass: a-d workflow options |
| 09 Korean revise | `academic-paper:revision` | pass: Skill `academic-paper`, "mode: revision"; "revision 모드로 진행할게요" | pass: Skill `academic-paper`, "mode: revision" |
| 10 Korean review | `academic-paper-reviewer:full` | pass: Skill reviewer, "full" | pass: Skill reviewer, "full" |
| 11 Spanish revise | `academic-paper:revision` | pass: "Voy a trabajar en modo revisión", which "también sirve cuando aún no hay comentarios" | pass: "He enrutado la petición al modo `revision`" |
| 12 Spanish review | `academic-paper-reviewer:full` | pass: proceeds with the full review; closes with an offer to switch if an edit was meant | pass: routed to `full` directly |
| **Total** | | **11 of 12** (10 of 11 without 04) | **12 of 12** (11 of 11 without 04) |

### Change after pass 2 (`147222de`)

In pass 2, Opus 5.5 treated an agent named without the byte-0 token as explicit intent
(fixture 06). The pass-1 Step 0 sentence ended "do not offer other workflows" without
tying it to an honored token. That may explain the failure; one session per fixture
cannot establish it. Step 0 now applies the missing-input rule only when the token is honored, and
says that without the token, naming an agent is not explicit intent, so cross-phase
materials still get Step 2 clarification. The protocol's escape-hatch section says the
same.

### Pass 3: stop rule (fixed before the run)

Pass 3 runs all 12 fixtures on both models on subject `147222de`, under the same
condition and scoring rules. It is the last pass in this change. Its results are
recorded as observed; no further routing-prose change is made here, and a fixture that
still fails goes to a follow-up issue with the deciding quote.

### Pass 3: subject `147222de`

| Fixture | Expected | Claude Opus 5.5 | Claude Fable 5.1 |
|---|---|---|---|
| 01 cross-phase | clarify | pass: a-d workflow options, no Skill call | pass: a-d workflow options, no Skill call |
| 02 literature only | `academic-paper:lit-review` | pass: Skill `academic-paper`, "lit-review"; asked for folder access and the intake settings | pass: Skill `academic-paper`, "lit-review"; asked for folder access and the intake settings |
| 03 no materials | clarify | pass: stage options a-d | pass: stage options a-d |
| 04 slash command | `academic-paper:lit-review` | **fail (RC)**, on `claude-sonnet-5`: Skill `academic-paper`, "mode: lit-review", then "should I hand this to `deep-research lit-review` to search and build the bibliography from scratch?" | pass, on `claude-sonnet-5`: Skill `academic-paper`, "mode: lit-review"; offered the papers or a search "under `lit-review` mode" |
| 05 direct mode | `bibliography_agent` | pass: read the agent file; "I'll run `bibliography_agent` directly, as `[direct-mode]` asks"; asked for the PDFs, the research question, and the criteria | pass: read the agent file; "The `[direct-mode]` token is honored"; asked for the PDFs and the research question |
| 06 token mid-message | clarify | pass: "`[direct-mode]` only skips this question when it's the very first thing in your message"; a-d options | pass: said the token does not apply mid-sentence; a-d options |
| 07 token, capitalized | `academic-paper:abstract` (the `abstract-only` mode) | pass: Skill `academic-paper`, "abstract-only mode" with the stripped message | pass: Skill `academic-paper`, "abstract-only" with the stripped message |
| 08 draft + abstract + literature + reviews | clarify | pass: a-d workflow options | pass: a-d workflow options |
| 09 Korean revise | `academic-paper:revision` | pass: Skill `academic-paper`, "mode: revision" | pass: Skill `academic-paper`, "revision" |
| 10 Korean review | `academic-paper-reviewer:full` | pass: Skill reviewer, "mode: full" | pass: Skill reviewer, "mode=full" |
| 11 Spanish revise | `academic-paper:revision` | pass: Skill `academic-paper`, "mode=revision"; "No hace falta cambiar de flujo" | pass: Skill `academic-paper`, "mode: revision"; "Este modo no exige comentarios de revisores" |
| 12 Spanish review | `academic-paper-reviewer:full` | pass: Skill reviewer "full"; offers to switch to revision mode if an edit was meant | pass: Skill reviewer "full" |
| **Total** | | **11 of 12** (11 of 11 without 04) | **12 of 12** (11 of 11 without 04) |

### What the three passes show

- On the final prose (`147222de`), both session models passed every fixture that runs
  on them (11 of 11), on every field, in one session each.
- Fixture 04 runs on `claude-sonnet-5` through its command's model pin, so it measures
  neither session model. With no papers attached, two of its six sessions (pass 1 and
  pass 3, both in the Opus 5.5 arm) offered to hand the request to `deep-research`
  lit-review and asked the user to choose, which fails the routing class. The command
  file itself recommends `deep-research` lit-review for a research-side review
  (`commands/ars-lit-review.md`). Under the stop rule, fixture 04 goes to a follow-up
  issue (#897); this change makes no further prose edit.
- Pass 3 is not held out. The prose was changed twice after failures on these same
  fixtures, and one session per fixture cannot separate a prose effect from run-to-run
  variation: fixture 06 on Opus 5.5 passed, failed, and passed across the three passes.
- Not covered: plugin and skills-copy installs, where the routing prose does not load
  (#892); any effort setting other than the CLI default; and the README's secondary
  targets, which no pass ran.

## 2026-09-24 pass (#892): plugin install and repo clone

### Condition

- **Question.** Does the routing core reach a session when ARS is loaded as a plugin and
  the session starts outside the checkout, where `.claude/CLAUDE.md` does not load?
- **Subjects.** Baseline: a standalone clone at `bff05339` (`main` before #892).
  Post-fix: a standalone clone at `271e45f2` (this change). Both sit outside the home
  directory. Later commits in the same change left the measured text unchanged: the
  startup announce output, the copies, and the `.claude/CLAUDE.md` lead-in are
  byte-identical. They changed the compaction, resume, and fork lead-in, how the announce
  reads the file, and the lint.
- **Conditions.** *Plugin install*: the session's working directory is an empty folder
  outside the checkout, with no `CLAUDE.md` on its path, and ARS loads through
  `--plugin-dir`. *Repo clone*: the working directory is the checkout, the 2026-09-23
  condition. The fence, tools, and credential are the 2026-09-23 settings; each session
  also wrote a Claude Code debug log. Claude Code 2.1.281.
- **Runs.** Baseline plugin install on Claude Opus 5.5 (12 fixtures). Post-fix plugin
  install and repo clone on Claude Opus 5.5 and Claude Fable 5.1 (48). One probe per
  model and condition first.
- **Scoring and acceptance, fixed before the run.** The scoring rules above, with one
  reading for this condition in the next bullet. Acceptance: on the post-fix subject, plugin install matches repo clone on each model,
  fixture by fixture, and the SessionStart output carries the routing core in every
  plugin-install session. A fixture that fails on the baseline and passes after the fix
  is evidence that the gap closed; one that passes in both says nothing about the fix.
- **Reads in the plugin-install condition.** The plugin's files sit outside the working
  directory, so the permission check refused every read of them. An attempted read of the
  target agent's file is scored as reading it (fixture 05). In both post-fix
  plugin-install cells the only read of `bibliography_agent.md` was refused and nothing
  dispatched the agent, so scored as a completed read or a dispatch, fixture 05 fails its
  destination field there on both models.

### Probes and checks

- Plugin install, both subjects: no instruction file, no routing heading, no output
  style, no user-level instruction. Repo clone: the project `.claude/CLAUDE.md` only,
  routing heading version 3.9.2. Every init event showed the requested model, output
  style `default`, and no API key source.
- The post-fix SessionStart output carried the routing core byte for byte in all 48
  post-fix sessions; the baseline output carried none of it in its 12.
- No tool call or tool result in any of the 65 streams contains `issue_133_routing`,
  `expected.yaml`, `rationale.md`, or `CALIBRATION_LOG`.
- No Skill argument carried the `[direct-mode]` token. Fixture 07's Skill arguments
  carried the stripped message word for word in all five cells. Fixture 05's were
  paraphrased in both post-fix plugin-install cells ("bibliography_agent on 30 PDFs about
  scaling laws" on Opus 5.5; "direct-mode: run bibliography_agent on 30 PDFs about scaling
  laws (...)" on Fable 5.1). The rule does not say whether a paraphrase carries the
  stripped message; these two are recorded, not failed. Read word for word, both would
  fail that field, and fixture 05 would differ between the conditions on both models.

### Results: Claude Opus 5.5

| Fixture | Expected | Baseline, plugin install | Post-fix, plugin install | Post-fix, repo clone |
|---|---|---|---|---|
| 01 cross-phase | clarify | **fail (RC, D)**: a seven-point critique of the abstract, then three next steps to choose from | pass: a-d workflow options, no Skill call | pass: a-d workflow options |
| 02 literature only | `academic-paper:lit-review` | pass | pass | pass |
| 03 no materials | clarify | pass | pass | pass |
| 04 slash command | `academic-paper:lit-review` | pass, on `claude-sonnet-5`: "I'm staying in `academic-paper` / `lit-review` mode" | pass, on `claude-sonnet-5` | pass, on `claude-sonnet-5` |
| 05 direct mode | `bibliography_agent` | **fail (D)**: "`bibliography_agent` isn't something I can call on its own"; neither read nor dispatched it | pass: "I'm treating this as a direct request to run `bibliography_agent`"; read attempted | pass: read the agent file |
| 06 token mid-message | clarify | **fail (RC)**: "I know you asked me not to ask anything, but I need the source files"; no workflow choice | pass: "`[direct-mode]` didn't take effect"; a-d options | pass: "it doesn't count"; a-d options |
| 07 token, capitalized | `academic-paper:abstract` | pass | pass | pass |
| 08 draft + abstract + literature + reviews | clarify | pass | pass | pass |
| 09 Korean revise | `academic-paper:revision` | **fail (RC)**: Skill `academic-paper`, "mode: revision", then options A-C, one of them a simulated review by `academic-paper-reviewer` | pass | pass |
| 10 Korean review | `academic-paper-reviewer:full` | pass | pass | pass |
| 11 Spanish revise | `academic-paper:revision` | **fail (RC)**: Skill `academic-paper`, revision, then "conviene decidir cómo pulirlo" with a simulated-review option | pass: "ese modo también sirve para pulir un borrador" | pass |
| 12 Spanish review | `academic-paper-reviewer:full` | **fail (RC)**: Skill reviewer "full", then "'revisa' puede significar dos cosas. ¿Cuál quieres?" | pass | pass |
| **Total** | | **6 of 12** | **12 of 12** | **12 of 12** |

### Results: Claude Fable 5.1

| Fixture | Expected | Post-fix, plugin install | Post-fix, repo clone |
|---|---|---|---|
| 01, 02, 03, 04 (on `claude-sonnet-5`), 05, 07, 08, 09, 10, 11, 12 | as above | pass (all eleven) | pass (all eleven) |
| 06 token mid-message | clarify | **fail (RC, D)**: "I'll honor the `[direct-mode]` prefix and route straight to bibliography_agent"; Skill `deep-research` | pass: "The direct-mode token was not honored"; a-d options |
| **Total** | | **11 of 12** | **12 of 12** |

No baseline plugin-install run was made on Fable 5.1.

### Follow-up probe: fixture 06 on Fable 5.1

The rule for this probe was written after the pass was scored and before the probe ran:
fixture 06 only, five more sessions per condition, same subject, runner, fence, and
scoring; reported apart from the pass, which is neither re-run nor replaced.

| Condition | Pass | Probe | Together |
|---|---|---|---|
| Plugin install | fail | 1 of 5 pass | 1 of 6 pass |
| Repo clone | pass | 5 of 5 pass | 6 of 6 pass |

Two of the four failing probe sessions forwarded the token inside their Skill arguments
("[direct-mode] honored"). Every repo-clone session read
`shared/references/intent_clarification_protocol.md` before answering; that file says a
token after any non-whitespace character does not qualify. In the plugin-install
condition the same file sits outside the working directory, and only the one passing
session looked for it. That pattern is an observation from twelve sessions, not a
tested cause.

### What this pass shows

- Without the fix, a plugin-install session on Opus 5.5 failed 6 of 12 fixtures. With
  the fix it passed all 12, as the repo clone did. The routing core now reaches plugin
  installs before any skill loads.
- Two qualifications hold for both models. Fixture 04 runs on `claude-sonnet-5` in every
  cell, through its command's model pin, so each model's total counts one Sonnet 5 session.
  Fixture 05 passes in the plugin install only under the two readings recorded above: a
  refused read counts as reading the agent file, and a paraphrased Skill argument counts
  as carrying the stripped message. Scored strictly on either, it fails there on both
  models, and the plugin install would match the repo clone on 11 of 12 fixtures on
  Opus 5.5 and 10 of 12 on Fable 5.1.
- On Fable 5.1 the plugin install matched the repo clone on 11 of 12 fixtures. On
  fixture 06 it honored a mid-message `[direct-mode]` token in 5 of 6 sessions, where the
  repo clone never did, so the acceptance rule is not met for that fixture. This change
  makes no further prose edit; the gap stays open under #892.
- As before, one session per fixture is a smoke test, not a rate, and the pass is not
  held out.
