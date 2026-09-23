# #133 routing fixtures: calibration log

Each entry records one calibration pass: the condition, the scoring rules fixed before
the run, and the per-fixture result against every field of the fixture's `expected.yaml`.
A pass is a smoke-test observation on one session per fixture, not a measured rate.

## 2026-09 pass (#889): Claude Opus 5.5 and Claude Fable 5.1

### Condition

- **Subject**: a fixed checkout of this repository at `95929c00`, never modified during
  the run.
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
  recorded when the CLI reports it.
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

### Results

(Filled in after the run.)
