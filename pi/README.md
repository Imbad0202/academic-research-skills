# Pi wrapper

Thin, community-maintained compatibility wrapper for running the original Claude Code Academic Research Skills (ARS) in [Pi](https://pi.dev/).

The wrapper does not copy or modify ARS skill, agent, reference, schema, script, or command content. Pi loads the four original `SKILL.md` trees and exposes the original `commands/ars-*.md` files as prompt templates. A small input adapter reads the selected original command at invocation time and preserves trailing user arguments.

## Load-bearing runtime differences from Claude Code

These differences affect how ARS evidence should be interpreted:

1. **The wrapper does not provide agent isolation or orchestration.** If the Pi setup has no matching subagent, workflow, or parallel-agent capability, ARS specialist roles run sequentially in the current context. That is degraded execution and must be disclosed; it is not independent multi-agent review.
2. **Claude hooks do not run in Pi.** In particular, ARS write-scope enforcement remains prompt-level unless the user's Pi environment supplies a separate enforcement mechanism. Do not represent the Claude `PreToolUse` hook boundary as active.

Run `/ars-pi-doctor` to inspect the current environment. The curated [degraded-mode end-to-end evidence](../examples/pi/README.md) shows both boundaries in a completed run.

## Requirements

- Pi with package support (`pi install` / `pi -e`)
- The complete repository package, loaded from GitHub or from a local checkout; `pi/` is only a wrapper around its parent files and cannot be copied by itself
- Optional capabilities depend on the user's Pi setup:
  - a subagent, workflow, or parallel-agent skill/tool for true multi-agent execution
  - a web-search or page-retrieval skill/tool for literature search and verification
  - Python, Pandoc, and tectonic for the optional ARS features that already require them

There are no required Pi orchestration or web-search dependencies. When a capability is unavailable, the wrapper tells Pi to use an installed equivalent or disclose degraded execution instead of pretending the operation ran.

## Try without installing

Load the package temporarily from GitHub for the current Pi run:

```bash
pi -e git:github.com/Imbad0202/academic-research-skills
```

To try a local checkout instead, clone the repository first:

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git
cd academic-research-skills
pi -e ./pi
```

Then inspect optional capabilities and try a mode:

```text
/ars-pi-doctor
/ars-plan
/ars-lit-review AI-assisted systematic reviews
/ars-reviewer
/ars-full
```

The original skills are also directly available:

```text
/skill:deep-research
/skill:academic-paper
/skill:academic-paper-reviewer
/skill:academic-pipeline
```

For automatic ARS skill selection from subsequent natural-language prompts, explicitly enable ARS mode first:

```text
/ars-pi-start
```

## Install from GitHub

Pi can install the canonical repository directly because the root `package.json` points to this wrapper and the original ARS resources:

```bash
pi install git:github.com/Imbad0202/academic-research-skills
```

Pin a branch, tag, or commit that contains the Pi wrapper when needed:

```bash
pi install git:github.com/Imbad0202/academic-research-skills@REF
```

Update installed Git packages with `pi update --extensions`. Remove this package with:

```bash
pi remove git:github.com/Imbad0202/academic-research-skills
```

## Install from this checkout

Keep the checkout at a stable path, then run from the repository root:

```bash
pi install .
```

The nested manifest also supports local installation from the wrapper directory:

```bash
pi install ./pi
```

Pi stores a local path rather than copying the repository. Update ARS with normal Git operations; the wrapper continues to load the original files.

If an optional sandbox restricts reads to the current working directory, allow read access to the repository checkout or run Pi from the repository root. Supporting files are intentionally not copied into the wrapper.

Remove using the same source form used during installation:

```bash
pi remove .
# or: pi remove ./pi
```

## Capability doctor

`/ars-pi-doctor` runs without an LLM call. It reports discovered orchestration and web-retrieval capabilities plus Python, PyYAML, Pandoc, tectonic, sandbox, and Claude-hook status. Missing optional dependencies remain the user's choice; the wrapper does not install them.

## System-prompt scope

For prompts submitted while Pi is idle, installing the package does not add ARS text to ordinary Pi prompts. While ARS mode is inactive, the wrapper removes only this package's four ARS skill entries from the newly started run's system prompt, preventing automatic model invocation without modifying the original `SKILL.md` files.

When Pi is idle, an `/ars-*` command or one of the four direct `/skill:*` entries above activates ARS mode before the new agent run starts, so that request receives both the original skill and the compatibility note. `/ars-pi-start` explicitly enables ARS mode and automatic skill selection for subsequent natural-language prompts. The state survives resuming the same session, follows the selected branch during `/tree` navigation, and resets in a new session. `/ars-pi-doctor` does not activate it.

Pi 0.83.0 does not rebuild the system prompt when a prompt is queued into an agent run that is already streaming. A mid-stream `/ars-*` or direct `/skill:*` prompt can therefore execute under that run's existing system prompt without the wrapper-injected compatibility note; similarly, `/ars-pi-stop` changes the persisted mode immediately but cannot remove ARS text from the in-flight run. The RPC `steer` and `follow_up` methods also bypass Pi's `input` event, so a direct ARS `/skill:*` sent through either method does not activate the wrapper. To receive the scoped system-prompt guarantee, wait for Pi to become idle and submit the request through the normal interactive or RPC `prompt` path.

To hide the ARS skills again and continue unrelated work without the compatibility note, run:

```text
/ars-pi-stop
```

## Wrapper regression test

```bash
node --test pi/wrapper.test.mjs
```

The test covers idle-prompt skill hiding through canonical and symlink-spelled load paths, XML-escaped locations, preservation of missing and adjacent unrelated skills across alternate block formatting, same-request `/ars-*` and direct `/skill:*` activation while idle, manual start/stop toggling, `/tree` state restoration, argument-safe script-path rewriting, and single-pass argument-placeholder substitution.

## What the wrapper translates

The wrapper reads `/ars-*` invocations from the original Claude command files, strips their frontmatter, appends trailing arguments when the command has no argument placeholder, converts executable `python scripts/...` paths to checkout-absolute paths, and expands the original target `SKILL.md` through Pi's native `/skill:*` mechanism. While ARS is active in the session, it also adds a short compatibility note to Pi's system prompt:

- repository-root ARS paths resolve against this checkout
- Claude tool names mean “use the equivalent available Pi capability”
- multi-agent work searches available tools and configured Pi skill locations for an installed orchestration capability, otherwise it uses sequential execution with a disclosure
- `WebSearch`, `WebFetch`, and `/websearch` search available tools and configured Pi skill locations for an installed web capability; no capability means no verification claim
- Claude-specific command model hints are ignored, so the active Pi model is inherited

The `pi/package.json` manifest performs the remaining mapping directly:

| Claude distribution resource | Pi resource |
| --- | --- |
| four original skill directories | four Pi skills |
| `commands/ars-*.md` | `/ars-*` Pi prompt templates with argument-preserving native skill expansion and absolute utility-script paths |
| Claude tool/runtime assumptions | short capability-based compatibility note |

## Scope

This is intentionally a basic wrapper, not a reimplementation of Claude Code or ARS orchestration. The original ARS content remains authoritative and unmodified.

The project license remains CC BY-NC 4.0. Attribution and noncommercial restrictions apply.
