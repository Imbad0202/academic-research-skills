# Pi wrapper

Thin, community-maintained compatibility wrapper for running the original Claude Code Academic Research Skills (ARS) in [Pi](https://github.com/badlogic/pi-mono).

The wrapper does not copy or modify ARS skill, agent, reference, schema, script, or command content. Pi loads the four original `SKILL.md` trees and exposes the original `commands/ars-*.md` files as prompt templates. A small input adapter reads the selected original command at invocation time and preserves trailing user arguments.

## Requirements

- Pi with package support (`pi install` / `pi -e`)
- This complete repository checkout; `pi/` is only a wrapper around its parent files
- Optional capabilities depend on the user's Pi setup:
  - a subagent, workflow, or parallel-agent skill/tool for true multi-agent execution
  - a web-search or page-retrieval skill/tool for literature search and verification
  - Python, Pandoc, and tectonic for the optional ARS features that already require them

There are no required Pi orchestration or web-search dependencies. When a capability is unavailable, the wrapper tells Pi to use an installed equivalent or disclose degraded execution instead of pretending the operation ran.

## Try without installing

From the repository root:

```bash
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

## Install from GitHub

When this branch exists on GitHub, Pi can install the repository directly because the root `package.json` points to this wrapper and the original ARS resources:

```bash
pi install git:github.com/OWNER/academic-research-skills
```

Pin a branch, tag, or commit when needed:

```bash
pi install git:github.com/OWNER/academic-research-skills@REF
```

## Install from this checkout

Keep the checkout at a stable path, then run from the repository root:

```bash
pi install .
```

The nested manifest remains usable for wrapper-only local installation:

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

## What the wrapper translates

The wrapper reads `/ars-*` invocations from the original Claude command files, strips their frontmatter, appends trailing arguments when the command has no argument placeholder, converts executable `python scripts/...` paths to checkout-absolute paths, and expands the original target `SKILL.md` through Pi's native `/skill:*` mechanism. It also adds a short compatibility note to Pi's system prompt:

- repository-root ARS paths resolve against this checkout
- Claude tool names mean “use the equivalent available Pi capability”
- multi-agent work searches available tools and configured Pi skill locations for an installed orchestration capability, otherwise it uses sequential execution with a disclosure
- `WebSearch`, `WebFetch`, and `/websearch` search available tools and configured Pi skill locations for an installed web capability; no capability means no verification claim
- Claude-specific command model hints are ignored, so the active Pi model is inherited

The `pi/package.json` manifest performs the remaining mapping directly:

| Claude distribution resource | Pi resource |
|---|---|
| four original skill directories | four Pi skills |
| `commands/ars-*.md` | `/ars-*` Pi prompt templates with argument-preserving native skill expansion and absolute utility-script paths |
| Claude tool/runtime assumptions | short capability-based compatibility note |

## Scope

This is intentionally a basic wrapper, not a reimplementation of Claude Code or ARS orchestration. The original ARS content remains authoritative and unmodified.

The project license remains CC BY-NC 4.0. Attribution and noncommercial restrictions apply.
