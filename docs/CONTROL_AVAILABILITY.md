# Control Availability by Install Channel

**Purpose.** ARS documentation names several controls — the write-scope guard, the
citation-verification gate, mandatory checkpoints, the tools allowlist. Which of those
actually operate depends on *how you installed ARS*. This page maps mechanism ×
channel in one place, so a user evaluating an integrity claim can see whether it holds
in their channel. The linked source documents remain authoritative for each fact.

**Origin.** ISO/IEC 42001-spirit gap assessment
([`audits/iso42001-spirit-gap-assessment-2026-08-17.md`](../audits/iso42001-spirit-gap-assessment-2026-08-17.md),
finding T-6, [#757](https://github.com/Imbad0202/academic-research-skills/issues/757)).
Transparency here is one of this repo's distilled operating principles (with informative
anchors to ISO/IEC 42001) — not an ISO-mandated artifact.

## Install channels

| Channel | Documented in | Channel-wide limitation |
|---|---|---|
| **Plugin** — Claude Code plugin install | [SETUP Method 0](SETUP.md#method-0-claude-code-plugin-v370-recommended-for-claude-code-cli--ide-users) | None — the reference channel. |
| **Skills copy** — skill folders copied into a project's `.claude/skills/` or the global `~/.claude/skills/` | [SETUP Method 1](SETUP.md#method-1-as-project-skills-recommended) | Nothing wired by the plugin manifest runs (note 3). |
| **Repo clone** — Claude Code run inside a clone of this repository | [SETUP Method 2](SETUP.md#method-2-as-a-standalone-project) | Nothing wired by the plugin manifest runs (note 3). |
| **Cowork** — skills uploaded to Claude Cowork (desktop) | [SETUP Method 3](SETUP.md#method-3-claude-cowork-desktop) | Each skill runs standalone: no Task-tool subagent dispatch, so the coordinated pipeline — and its staged checkpoints — does not run as designed. |
| **claude.ai Project** — repo attached to a claude.ai Project as retrievable knowledge | [SETUP Method 4](SETUP.md#method-4-use-with-claudeai-web) | Read-only knowledge: Claude can read and cite the skill bodies, but nothing executes — no activation, routing, hooks, scripts, or orchestration. (The Method 4a upload path is documented but not recommended; see SETUP § Method 4a.) |
| **Claude Science** — skills imported via "Import from GitHub" | [SETUP Method 5](SETUP.md#method-5-claude-science-import-v3140) | Methodology layer only; Claude Code-specific machinery does not transfer, and Claude Science substitutes its own agent system (details: SETUP Method 5). Imports are point-in-time snapshots. |
| **Pi port** — community-maintained wrapper for the Pi coding agent | [`pi/README.md`](../pi/README.md) | Two documented boundaries: the wrapper itself supplies no agent isolation or orchestration — an installed Pi orchestration capability is used when available, otherwise roles run sequentially (degraded execution, disclosed, not independent multi-agent review) — and no Claude hooks (write-scope enforcement stays prompt-level). `/ars-pi-doctor` reports what the local environment supplies. |

## Availability matrix

Legend: **Active** = operates as documented · **Conditional** = operates only under the
noted conditions, with a defined degraded state otherwise · **Absent** = does not operate
in this channel. Read down your channel's column: a claim about a mechanism holds only
where its row says Active — or Conditional with the linked note's conditions met — after
applying your channel's channel-wide limitation above.

| Mechanism | Plugin | Skills copy | Repo clone | Cowork | claude.ai Project | Claude Science | Pi port |
|---|---|---|---|---|---|---|---|
| Methodology layer (the four skills' `SKILL.md` protocols) | Active | Active | Active | Active | Conditional | Active | Active |
| Skill auto-routing (trigger keywords → skill activation) | Active | Active | Active | Active | Absent | Conditional | Conditional |
| `/ars-*` slash commands | Active ⁽¹⁾ | Absent | Absent | Absent | Absent | Absent | Conditional |
| SessionStart announce + update reminder | Conditional ⁽⁸⁾ | Absent ⁽³⁾ | Absent ⁽³⁾ | Absent | Absent | Absent | Absent |
| Write-scope guard (`PreToolUse` hook) | Conditional ⁽²⁾ | Absent ⁽³⁾ | Absent ⁽³⁾ | Absent | Absent | Absent | Absent |
| Plugin agents with tools allowlist (#514) ⁽⁴⁾ | Active | Absent ⁽³⁾ | Absent ⁽³⁾ | Absent | Absent | Absent | Absent |
| Subagent orchestration (Task-tool multi-agent dispatch) | Active | Active | Active | Absent | Absent | Absent | Conditional |
| Python-backed opt-in features (repo `scripts/`) | Conditional ⁽⁵⁾ | Conditional ⁽⁵⁾ | Conditional ⁽⁵⁾ | Absent | Absent | Absent | Conditional ⁽⁵⁾ |
| Cross-model verification (consent-gated second model) | Conditional ⁽⁶⁾ | Conditional ⁽⁶⁾ | Conditional ⁽⁶⁾ | Absent | Absent | Absent | Absent |
| Prompt-level checkpoints and integrity gates | Active ⁽⁷⁾ | Active ⁽⁷⁾ | Active ⁽⁷⁾ | Conditional | Absent | Conditional | Conditional |

CI-side checks (mutation-tested lints, content locks, changelog gates) are deliberately
not a matrix row: they run in this repository's GitHub Actions, protecting the
published artifact all channels ship from, and never run on a user machine —
identical for every channel. They do not all enforce at the same strength or fire on
every change: the per-workflow classification (blocking / advisory / administrative /
post-push detection, with triggers and bypass tokens) is
[ARCHITECTURE.md §7.1](ARCHITECTURE.md#71-ci-workflow-enforcement-classes-755). The machine-readable index of the suite's
runtime graceful-degradation mechanisms is
[`shared/contracts/degradation_registry.json`](../shared/contracts/degradation_registry.json).

## Notes

1. Plugin installs namespace commands as `/academic-research-skills:ars-<mode>`; a bare
   `/ars-<mode>` alias also works on recent Claude Code versions — the exact minimum
   version and the older-version behavior are documented in SETUP Method 0 (#633).
2. The write-scope guard needs a **real Python interpreter** and a `bash` to run its
   launcher; missing either produces a *defined degraded state*, never a block — see
   the [environment degradations](#environment-degradations-within-a-channel) table.
   The guard is optional subagent hardening; core skills are unaffected when it is
   inactive (README Requirements).
3. Hooks and plugin agents are wired by the **plugin manifest** (`hooks/hooks.json`,
   `agents/`, resolved via `CLAUDE_PLUGIN_ROOT`). A skills-copy or repo-clone install
   does not wire them: the `PreToolUse` write-scope guard and the SessionStart announce
   do not run, and agent dispatch uses the in-skill prompt templates without the
   frontmatter tools allowlist. A user may wire the hook into their own Claude Code
   settings manually, at which point the note-2 conditions apply.
4. The allowlist's canonical contents live in the three plugin agents' frontmatter,
   pinned in CI by `scripts/check_tools_allowlist.py` — this page deliberately does not
   restate the list.
5. These features (e.g. the citation-verification gate CLI, the revision
   token-conservation checker, the submission-package verifier, the PDF read preflight,
   the cache commands — a non-exhaustive, growing set) shell out to Python scripts at
   the repository root (`scripts/`, `shared/`), not inside the four skill folders. They
   need (a) a real Python interpreter and (b) the repo checkout present: automatic for
   the plugin channel (the plugin root is the repo snapshot) and repo clones; for a
   skills-copy install, keep the original clone — the copied skill folders alone cannot
   run them. On Pi, they work if Python and the repo are present (`pi/README.md`).
6. Note-5 conditions, plus a transport: provider API credentials and `curl` for the
   general transports, or — for the citation-only calls — a Codex CLI
   ChatGPT-subscription login (`ARS_CROSS_MODEL_TRANSPORT=codex`). All transports sit
   behind the same boundary defined in
   [`shared/cross_model_verification.md`](../shared/cross_model_verification.md): the
   user's **explicit consent per session** — the `ARS_CROSS_MODEL` environment variable
   is configuration, not consent. Unset, the feature is invisible and makes zero
   network calls.
7. The MANDATORY checkpoints, integrity gates, and IRON RULE constraints are
   **prompt-level, trust-based controls with audit trails**, executed by the session
   model following the skill instructions — not coercive runtime enforcement. Documented
   overrides require recorded reasoning, and final integrity responsibility stays with
   the human researcher (see the
   [gap assessment §3](../audits/iso42001-spirit-gap-assessment-2026-08-17.md)).
   This row says the *instructions* are present and active in the channel, nothing
   stronger.
8. The SessionStart hook is launched through `bash`, so on Windows it needs Git Bash
   (the same PowerShell limitation as the guard launcher); its update-reminder path
   additionally needs `curl`, stays silent on any failure, and is disabled entirely by
   `ARS_UPDATE_CHECK=0` (SETUP Method 0).

## Environment degradations within a channel

Independent of install channel, the write-scope guard has documented degraded states.
None of them *introduces* a block: launcher failure paths resolve to **pass-through**,
and a missing `timeout` binary is a bounding-mechanism swap under which the guard keeps
operating normally — its real decisions (including deny) still apply, with only an
overrun resolving to pass-through. The guard is an optional
hardening layer, and a broken guard must not lock a user out of their own files
(maintainer decision recorded in `hooks/run_guard.sh`; user-facing summary in the
README Requirements bullet). This table is a convenience summary, not a second
authority: the indexed rows are the `write_scope_guard_*` mechanisms in
[`shared/contracts/degradation_registry.json`](../shared/contracts/degradation_registry.json)
(#769), whose anchors into `hooks/run_guard.sh` are lint-pinned, and which also cover
two states this table omits — guard subprocess misbehaves or the launcher fails
internally (→ pass-through), and the documented multi-megabyte payload edge (an
accepted, untested case with no pinned outcome):

| Condition | Behavior |
|---|---|
| No real Python found (Git Bash / POSIX shell present) | Guard silently no-ops (pass-through); core skills unaffected. On Windows, the 0-byte Microsoft Store `python3` stub is rejected, not mistaken for Python. |
| Windows without Git Bash | Claude Code falls back to PowerShell, which cannot run the `.sh` launcher: guard inactive, and the `PreToolUse` hook logs an error per call (accepted degradation — noisy, never blocking). |
| No `timeout` binary | Portable background-watchdog fallback with the same wall-clock bound and the same pass-through-on-overrun posture. |
