# OpenClaw harness port — proposal, not a merge candidate

## What this is

An **unaffiliated OpenClaw-harness port** of Academic Research Skills v3.22.1, offered for
your consideration. It is also published as a standalone repo:
<https://github.com/ChunkyPanda29/academic-research-skills-openclaw>

## Why it is a draft

**This PR will not pass your CI, by design.** Our ported `SKILL.md` files deliberately
diverge from upstream's harness assumptions, so your existing lints will report failures:

| Your lint | Why it fails |
|---|---|
| `scripts/check_routing_core_sync.py` | We changed the routing-core *carrier paragraph* (the prose above the `<!-- routing-core:begin -->` marker) to describe OpenClaw's install path. The marker block itself is preserved. |
| `scripts/check_skill_description_length.py` | Rewritten descriptions; all four measure under your 1,024-code-point bound, but the text differs. |
| `scripts/check_command_skill_dispatch.py` / command-parity lints | We have no `commands/` parity expectation, because OpenClaw has no user slash-command surface for skill modes. |
| `scripts/check_skill_inventory_parity.py` | Directory structure differs from your `skills/` symlink + manifest set-equality expectation. |

It is therefore a **proposal**, not a patch we expect you to merge. If the approach
interests you, the right shape is probably a documented adaptation guide under
`docs/` — or nothing at all. We are content with either answer.

## What the port changes

**Harness vocabulary only.** The academic methodology is unmodified and remains
Cheng-I Wu's work.

| Claude Code mechanism | OpenClaw equivalent |
|---|---|
| `Task tool` / `subagent_type` | `sessions_spawn` + `agents_wait` |
| `AskUserQuestion` | `ask_user` |
| `/ars-*` slash commands | natural-language trigger phrases in the skill `description` |
| `SessionStart` hook | none — routing core inlined in each `SKILL.md` |
| `PreToolUse` hook (`run_guard.sh`) | explicit pre-write step (weaker; see below) |
| `.claude/CLAUDE.md` project config | none — routing core inlined |
| `ARS_*` environment variables | operator-set env vars, default unset |

**19 body substitutions + 4 frontmatter rewrites** across the four `SKILL.md` files.
All **38 `agents/*.md` files were verified as needing no change** and are untouched.
`references/`, `templates/`, `examples/`, and `shared/` are untouched.

## Known limitation we want to be explicit about

Your `run_guard.sh` is a `PreToolUse` hook the agent cannot bypass. **OpenClaw has no
pre-tool hook system.** We preserve the guard as a *cooperative pre-write step the skill
runs itself*. This is **weaker than upstream**: enforcement rests on the skill's own
procedure, and the guard's documented fail-open behaviour means a broken guard yields no
protection at all, with no harness-level backstop.

We are not claiming parity, and we are not claiming that OpenClaw execution reproduces
your measurements. Nothing in the port is benchmarked.

## Provenance

- Original work: "Academic Research Skills" by Cheng-I Wu (github.com/Imbad0202)
- Ported from: v3.22.1, commit `a3f6569`
- License: CC-BY-NC-4.0 — `LICENSE` copied **verbatim** (SHA-256 verified identical)
- Attribution: `NOTICE.md`; transform record: `PORTING.md`

## Files in this PR

Added at the repository root: `deep-research/`, `academic-paper/`,
`academic-paper-reviewer/`, `academic-pipeline/`, `shared/`, `scripts/`, `commands/`,
`LICENSE`, `NOTICE.md`, `PORTING.md`, `README.md`.

If you would prefer this not live in your tree at all, say so and we will close it and
keep the standalone repo as the only home.
