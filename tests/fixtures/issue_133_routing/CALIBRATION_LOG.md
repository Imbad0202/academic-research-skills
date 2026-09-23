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
| 04 slash command | `academic-paper:lit-review` | pass, on `claude-sonnet-5` | pass, on `claude-sonnet-5` |
| 05 direct mode | `bibliography_agent` | **fail (D)**: "I haven't started `bibliography_agent` yet because the 30 PDFs didn't come through"; the agent was named, never dispatched or read | pass: read the headings of `deep-research/agents/bibliography_agent.md` (Grep); "route straight to the deep-research `bibliography_agent`" |
| 06 token mid-message | clarify | pass: said the token was ignored; a-d options | pass: said the token was ignored; a-d options |
| 07 token, capitalized | `academic-paper:abstract` (the `abstract-only` mode) | pass: Skill `academic-paper`, "abstract-only" | pass: Skill `academic-paper`, "abstract-only" |
| 08 draft + abstract + literature + reviews | clarify | pass: a-d workflow options | pass: a-d workflow options |
| 09 Korean revise | `academic-paper:revision` | pass: "`revision` 모드로 진행하려고" | pass: Skill `academic-paper`, "mode=revision" |
| 10 Korean review | `academic-paper-reviewer:full` | pass: Skill reviewer, "full mode" | pass: Skill reviewer, "mode: full" |
| 11 Spanish revise | `academic-paper:revision` | **fail (RC, D)**: "necesito que elijas cómo pulirlo", four routes; read revision mode as needing reviewer comments; the Skill call named no mode | **fail (RC)**: "Indica también qué ruta prefieres", two routes, neither of them revision mode alone; the Skill call named `revision`, so D passes by the rule's wording |
| 12 Spanish review | `academic-paper-reviewer:full` | **fail (RC)**: Skill reviewer "full", then "Confírmame cuál quieres": review, edit, or citations | pass: Skill reviewer "full"; asked only for the manuscript |
| **Total** | | **9 of 12** (8 of 11 without 04) | **11 of 12** (10 of 11 without 04) |

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
| 01-04, 07-10 | as in pass 1 | pass (04 on `claude-sonnet-5`) | pass (04 on `claude-sonnet-5`) |
| 05 direct mode | `bibliography_agent` | pass: read `deep-research/agents/bibliography_agent.md`, then asked for the files | pass: read the agent file; asked for the folder and the research question, with criteria optional |
| 06 token mid-message | clarify | **fail (RC, D)**: read `deep-research/agents/bibliography_agent.md`; "Once I have them, I'll run bibliography_agent directly, with no workflow questions"; the token was not mentioned | pass: said the token was ignored; a-d options |
| 11 Spanish revise | `academic-paper:revision` | pass: "Voy a trabajar en modo revisión", which "también sirve cuando aún no hay comentarios" | pass: "He enrutado la petición al modo `revision`" |
| 12 Spanish review | `academic-paper-reviewer:full` | pass: proceeds with the full review; closes with an offer to switch if an edit was meant | pass: routed to `full` directly |
| **Total** | | **11 of 12** (10 of 11 without 04) | **12 of 12** (11 of 11 without 04) |

### Change after pass 2 (`147222de`)

In pass 2, Opus 5.5 treated an agent named without the byte-0 token as explicit intent
(fixture 06). The pass-1 Step 0 sentence ended "do not offer other workflows" without
tying it to an honored token, which is the likely cause; one session per fixture cannot
show it. Step 0 now applies the missing-input rule only when the token is honored, and
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
| 04 slash command | `academic-paper:lit-review` | pass, on `claude-sonnet-5` | pass, on `claude-sonnet-5` |
| 05 direct mode | `bibliography_agent` | pass: read the agent file; "I'll run `bibliography_agent` directly, as `[direct-mode]` asks"; asked for the PDFs, the research question, and the criteria | pass: read the agent file; "The `[direct-mode]` token is honored"; asked for the PDFs and the research question |
| 06 token mid-message | clarify | pass: "`[direct-mode]` only skips this question when it's the very first thing in your message"; a-d options | pass: said the token does not apply mid-sentence; a-d options |
| 07 token, capitalized | `academic-paper:abstract` (the `abstract-only` mode) | pass: Skill `academic-paper`, "abstract-only mode" with the stripped message | pass: Skill `academic-paper`, "abstract-only" with the stripped message |
| 08 draft + abstract + literature + reviews | clarify | pass: a-d workflow options | pass: a-d workflow options |
| 09 Korean revise | `academic-paper:revision` | pass: Skill `academic-paper`, "mode: revision" | pass: Skill `academic-paper`, "revision" |
| 10 Korean review | `academic-paper-reviewer:full` | pass: Skill reviewer, "mode: full" | pass: Skill reviewer, "mode=full" |
| 11 Spanish revise | `academic-paper:revision` | pass: Skill `academic-paper`, "mode=revision"; "No hace falta cambiar de flujo" | pass: Skill `academic-paper`, "mode: revision"; "Este modo no exige comentarios de revisores" |
| 12 Spanish review | `academic-paper-reviewer:full` | pass: Skill reviewer "full"; offers to switch to revision mode if an edit was meant | pass: Skill reviewer "full" |
| **Total** | | **12 of 12** (11 of 11 without 04) | **12 of 12** (11 of 11 without 04) |

### What the three passes show

- On the final prose (`147222de`), each fixture passed on every field once per model,
  and fixture 04 passed once on `claude-sonnet-5`. No fixture failed, so the stop rule
  opens no follow-up issue.
- Pass 3 is not held out. The prose was changed twice after failures on these same
  fixtures, and one session per fixture cannot separate a prose effect from run-to-run
  variation: fixture 06 on Opus 5.5 passed, failed, and passed across the three passes.
- Not covered: plugin and skills-copy installs, where the routing prose does not load
  (#892); any effort setting other than the CLI default; and the README's secondary
  targets, which no pass ran.
