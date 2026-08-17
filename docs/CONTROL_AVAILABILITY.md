# Control Availability by Install Channel

**Purpose.** ARS documentation names several enforcement mechanisms — the write-scope
guard, the citation-verification gate, mandatory checkpoints, the tools allowlist. Which
of those actually operate depends on *how you installed ARS*. Those facts were previously
documented honestly but scattered (README Requirements, `docs/SETUP.md` methods,
`pi/README.md`, `hooks/run_guard.sh`). This page is the single map: one row per
mechanism, one column per install channel, so a user evaluating an integrity claim can
see in one place whether it holds in their channel.

**Origin.** ISO/IEC 42001-spirit gap assessment
([`audits/iso42001-spirit-gap-assessment-2026-08-17.md`](../audits/iso42001-spirit-gap-assessment-2026-08-17.md),
finding T-6, [#757](https://github.com/Imbad0202/academic-research-skills/issues/757)).
Transparency here is one of this repo's distilled operating principles (with informative
anchors to ISO/IEC 42001) — not an ISO-mandated artifact.

## Install channels

| Channel | Documented in |
|---|---|
| **Plugin** — Claude Code plugin install | [SETUP Method 0](SETUP.md#method-0-claude-code-plugin-v370-recommended-for-claude-code-cli--ide-users) |
| **Skills copy** — skill folders copied into a project's `.claude/skills/` or the global `~/.claude/skills/` | [SETUP Method 1](SETUP.md#method-1-as-project-skills-recommended) |
| **Repo clone** — Claude Code run inside a clone of this repository | [SETUP Method 2](SETUP.md#method-2-as-a-standalone-project) |
| **Cowork** — skills uploaded to Claude Cowork (desktop) | [SETUP Method 3](SETUP.md#method-3-claude-cowork-desktop) |
| **claude.ai Project** — repo attached to a claude.ai Project as retrievable knowledge (Method 4b; the not-recommended Method 4a upload is noted below) | [SETUP Method 4](SETUP.md#method-4-use-with-claudeai-web) |
| **Claude Science** — skills imported via "Import from GitHub" | [SETUP Method 5](SETUP.md#method-5-claude-science-import-v3140) |
| **Pi port** — community-maintained wrapper for the Pi coding agent | [`pi/README.md`](../pi/README.md) |

## Availability matrix

Legend: **Active** = operates as documented · **Conditional** = operates only under the
noted conditions, with a defined degraded state otherwise · **Absent** = does not operate
in this channel · **Upstream** = runs in this repository's CI, never on a user machine.

| Mechanism | Plugin | Skills copy | Repo clone | Cowork | claude.ai Project | Claude Science | Pi port |
|---|---|---|---|---|---|---|---|
| Methodology layer (the four skills' `SKILL.md` protocols) | Active | Active | Active | Active ⁽¹⁾ | Conditional ⁽²⁾ | Active ⁽³⁾ | Active ⁽⁷⁾ |
| Skill auto-routing (trigger keywords → skill activation) | Active | Active | Active | Active ⁽¹⁾ | Absent ⁽²⁾ | Conditional ⁽³⁾ | Conditional ⁽⁷⁾ |
| `/ars-*` slash commands | Active ⁽⁴⁾ | Absent | Absent | Absent | Absent | Absent | Conditional ⁽⁷⁾ |
| SessionStart announce + update reminder | Active | Absent | Absent | Absent | Absent | Absent | Absent |
| Write-scope guard (`PreToolUse` hook) | Conditional ⁽⁵⁾ | Absent ⁽⁶⁾ | Absent ⁽⁶⁾ | Absent | Absent | Absent ⁽³⁾ | Absent ⁽⁷⁾ |
| Plugin agents with tools allowlist (#514: `Read/Write/Edit/Grep/Glob`, no Bash, no network tools) | Active | Absent ⁽⁶⁾ | Absent ⁽⁶⁾ | Absent | Absent | Absent | Absent |
| Subagent orchestration (Task-tool multi-agent dispatch) | Active | Active | Active | Absent ⁽¹⁾ | Absent ⁽²⁾ | Absent ⁽³⁾ | Conditional ⁽⁷⁾ |
| Python-backed opt-in features (citation-verification gate CLI, revision token-conservation checker, submission-package verifier, PDF read preflight, cache commands) | Conditional ⁽⁸⁾ | Conditional ⁽⁸⁾ | Conditional ⁽⁸⁾ | Absent | Absent | Absent ⁽³⁾ | Conditional ⁽⁸⁾ |
| Cross-model verification (consent-gated second model) | Conditional ⁽⁹⁾ | Conditional ⁽⁹⁾ | Conditional ⁽⁹⁾ | Absent | Absent | Absent ⁽³⁾ | Absent ⁽⁷⁾ |
| Prompt-level checkpoints and integrity gates | Active ⁽¹⁰⁾ | Active ⁽¹⁰⁾ | Active ⁽¹⁰⁾ | Conditional ⁽¹⁾ | Absent ⁽²⁾ | Conditional ⁽³⁾ | Conditional ⁽⁷⁾ |
| CI lints, mutation tests, content locks, changelog gates | Upstream ⁽¹¹⁾ | Upstream ⁽¹¹⁾ | Upstream ⁽¹¹⁾ | Upstream ⁽¹¹⁾ | Upstream ⁽¹¹⁾ | Upstream ⁽¹¹⁾ | Upstream ⁽¹¹⁾ |

## Notes

1. **Cowork** uploads each skill as a standalone instruction set. The skills respond
   individually, but Cowork's uploaded-skill runtime provides no Task-tool subagent
   dispatch, so the coordinated pipeline (`academic-pipeline` chaining research → write →
   review → revise, each skill driving its own sub-agents) does not run the way it does
   in Claude Code — and the pipeline's staged checkpoints therefore do not fire as
   designed. Source: SETUP Method 3.
2. **claude.ai Project (Method 4b)** brings the repo in as *retrievable knowledge*:
   Claude can read and cite the skill bodies, references, and schemas, but nothing
   executes — no skill activation, routing, hooks, scripts, or orchestration. The
   Method 4a Custom Skill upload is documented but not recommended for this suite
   (see SETUP § Method 4a); it would surface the SKILL.md instructions without the
   multi-agent dispatch that produces the suite's actual outputs.
3. **Claude Science** imports the methodology layer only. Per SETUP Method 5, the
   Claude Code-specific machinery — `/ars-*` slash commands, hooks (including the
   write-scope guard), cross-model verification scripts, and Task-tool subagent
   orchestration — does not transfer. Claude Science runs its own specialist-agent
   system and its own citation-checking reviewer; treat a run as "ARS methodology +
   Claude Science's own machinery", not a 1:1 pipeline port. Imports are point-in-time
   snapshots (re-import after releases).
4. Plugin installs namespace commands as `/academic-research-skills:ars-<mode>`; the
   bare `/ars-<mode>` alias also works on Claude Code v2.1.216+ when no other command
   claims the name (SETUP Method 0, #633).
5. The write-scope guard needs a **real Python interpreter** and a `bash` to run its
   launcher. Missing either produces a *defined degraded state*, never a block — see
   the [environment degradations](#environment-degradations-within-a-channel) table.
   The guard is optional subagent hardening; core skills are unaffected when it is
   inactive (README Requirements).
6. Hooks and plugin agents are wired by the **plugin manifest** (`hooks/hooks.json`,
   `agents/`, resolved via `CLAUDE_PLUGIN_ROOT`). A skills-copy or repo-clone install
   does not wire them: the `PreToolUse` write-scope guard and the SessionStart announce
   do not run, and agent dispatch uses the in-skill prompt templates without the #514
   frontmatter tools allowlist. A user may wire the hook into their own Claude Code
   settings manually, at which point the note-5 conditions apply.
7. **Pi port** is community-maintained and explicitly documents its two boundaries
   (`pi/README.md`): (a) no agent isolation or orchestration — without a matching Pi
   capability, ARS specialist roles run *sequentially in the current context*, which is
   degraded execution and must be disclosed, not independent multi-agent review; (b)
   Claude hooks do not run in Pi — write-scope enforcement remains prompt-level unless
   the Pi environment supplies its own mechanism. The wrapper ships its own commands
   (e.g. `/ars-pi-doctor` reports discovered capabilities); it documents no cross-model
   transport wiring. Optional Python-backed features work if Python and the repo are
   present.
8. These features shell out to Python scripts that live at the repository root
   (`scripts/`, `shared/`) — they are not inside the four skill folders. They need
   (a) a real Python interpreter and (b) the repo checkout present: automatic for the
   plugin channel (the plugin root is the repo snapshot) and repo clones; for a
   skills-copy install, keep the original clone — the copied skill folders alone cannot
   run them.
9. Cross-model verification requires provider credentials, `curl`, the repo scripts,
   and — per [`shared/cross_model_verification.md`](../shared/cross_model_verification.md) —
   the user's **explicit consent per session**: the `ARS_CROSS_MODEL` environment
   variable is configuration, not consent. Unset, the feature is invisible and makes
   zero network calls.
10. The MANDATORY checkpoints, integrity gates, and IRON RULE constraints are
    **prompt-level, trust-based controls with audit trails**, executed by the session
    model following the skill instructions — not coercive runtime enforcement. Documented
    overrides require recorded reasoning, and final integrity responsibility stays with
    the human researcher (see the
    [gap assessment §3](../audits/iso42001-spirit-gap-assessment-2026-08-17.md)).
    This row says the *instructions* are present and active in the channel, nothing
    stronger.
11. CI checks run in this repository's GitHub Actions on every change — they protect
    the *published artifact* every channel ships from, and never run on a user machine.
    No install channel gains or loses them.

## Environment degradations within a channel

Independent of install channel, the write-scope guard has documented degraded states
(sources: README Requirements bullet, `hooks/run_guard.sh` header comments, SETUP
Method 0):

| Condition | Behavior |
|---|---|
| No real Python found (Git Bash / POSIX shell present) | Guard silently no-ops (pass-through); core skills unaffected. On Windows, note the 0-byte Microsoft Store `python3` stub is rejected, not mistaken for Python. |
| Windows without Git Bash | Claude Code falls back to PowerShell, which cannot run the `.sh` launcher: guard inactive, and the `PreToolUse` hook logs an error per call (accepted degradation — noisy, never blocking). |
| No `timeout` binary | Portable background-watchdog fallback with the same wall-clock bound and the same pass-through-on-overrun posture. |
| Claude Code older than v2.1.216 | Slash commands appear only in their bare `/ars-<mode>` form (still invocable; the namespaced form loses autocomplete). |

All guard degradations resolve toward **pass-through, never block**: the guard is an
optional hardening layer, and a broken guard must not lock a user out of their own
files (maintainer decision recorded in `hooks/run_guard.sh`).

## How to read an integrity claim against this matrix

- A claim about the **write-scope guard** or the **tools allowlist** holds only in the
  Plugin column, under the note-5 conditions.
- A claim about **mandatory checkpoints** or **integrity gates** holds wherever the
  matrix says the prompt layer is active — as a trust-based control (note 10), in every
  channel.
- A claim about the **citation-verification gate** or other script-backed checks holds
  wherever Python-backed features are available (note 8).
- **Claude Science and claude.ai Project users** get the methodology and the reading
  material, not the enforcement machinery; **Pi users** get sequential degraded
  execution with disclosure.
