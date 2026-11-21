# Antigravity wrapper

Thin, community-maintained wrapper for running the original Claude Code Academic Research Skills (ARS) in [Google Antigravity](https://antigravity.google/) (`agy` CLI).

The wrapper does not copy or modify ARS skill, agent, reference, schema, script, or command content. An installer writes a small native Antigravity plugin whose skills are loaders: each one carries the original skill's frontmatter, so it triggers on the same phrases, and tells the agent to read the original file from this checkout.

Maintainer of this port: [@MohammadSlo](https://github.com/MohammadSlo). Report Antigravity-specific problems to the port maintainer, not as core ARS bugs.

## Load-bearing differences from Claude Code

Read these before interpreting any ARS output produced on Antigravity.

1. **No write-scope guard.** The ARS `PreToolUse` hook is not installed. Antigravity's hook input carries no agent identity, and the guard fences a write only when it knows which ARS agent made it, so it could not engage. Phase Boundary rules are prompt-level only.
2. **Agent isolation is not guaranteed.** The compatibility rules tell the agent to dispatch ARS specialist roles as Antigravity subagents and to disclose any role it ran inline. Whether it does depends on the model: in the recorded runs, Gemini 4 Argon and Gemini 4 Hydrogen dispatched subagents and Gemini 3.8 Flash ran everything inline and said so. The four plugin agents under `agents/` are not registered, because Antigravity rejects their `tools:` frontmatter, and neither their tool allowlists nor the `model:` hints in commands apply. An inline role is not an independent review.
3. **Citation verification depends on the model and on network permissions.** The original verification steps are loaded and the compatibility rules repeat that they are mandatory, but nothing deterministic enforces them. Antigravity's terminal blocked ARS's index-lookup scripts (HTTP 403) until the index hosts were allowed; start `agy` with the settings file shown under Use. In the recorded runs a small model claimed more verification than it did. Check the disclosure at the end of each output for what was verified and how.
4. **Full texts are usually out of reach.** Antigravity's terminal and page tools reach only allowed hosts, and the shipped settings file allows the four index APIs, not publisher sites. In the recorded pipeline run the agent read abstracts, search snippets and catalogue records for all 65 sources and no full text, and said so. Supply PDFs in the project folder, or allow the hosts you need with further `read_url(...)` rules.
5. **`sr-screener` is not included.** Its design depends on two blinded reviewer subagents with read-only tools, which this wrapper cannot provide.
6. **Calibrated for Claude.** ARS prompts are tuned for Claude Opus and Sonnet. Use a strong model (`agy --model ...`; `agy models` lists them). The CLI default was Gemini 3.8 Flash in testing, which is below what ARS expects.

## Why a wrapper is needed

Measured on Antigravity CLI 1.5.5, macOS:

- Antigravity loads only the first 24,000 bytes of a skill body (`agy plugin validate` reports it). The four ARS skill files are 50 to 67 KB. In the body of `deep-research/SKILL.md` (v2.12.1) the first AI-disclosure rule is at byte 24,086 and the Three-Way Scan Mode section starts at byte 31,429, so a directly mounted skill triggers and formats but never sees those rules.
- The loader ignores symlinked skill directories and symlinked `SKILL.md` files inside a plugin.
- `agy plugin install` on this repository, which converts it as a Claude Code plugin, registers the 16 commands but none of the core skills, skips all four agents, and installs the guard hook with a payload shape the guard does not understand.

## Requirements

- Antigravity CLI (`agy`). Tested with 1.5.5.
- Python 3.9 or later, to run the installer.
- A full checkout of this repository at a stable path. The plugin points at it.
- A `python3` on the PATH that has PyYAML (`pip install pyyaml`). ARS scripts such as the run ledger need it; in one recorded run the ledger could not be written because it was missing.
- Pandoc and tectonic for the optional ARS features that already need them.

## Install

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git
cd academic-research-skills
python3 antigravity/install.py
```

This writes `~/.gemini/config/plugins/academic-research-skills/` with 20 skills: the four core skills and the 16 `/ars-*` commands. Start a new `agy` session and run `/skills` to confirm; do not ask the model whether a skill is loaded.

The installer refuses to replace a directory it did not create. If you previously ran `agy plugin install` or `agy plugin import` for ARS, remove that copy first with `agy plugin uninstall academic-research-skills`.

Run the installer again after `git pull` (skill descriptions and commands may have changed) or after moving the checkout. Uninstall with `agy plugin uninstall academic-research-skills`.

## Use

Work from your paper's project directory, not from the ARS checkout, and give the agent read access to the checkout:

```bash
cd ~/my-paper
agy --add-dir /path/to/academic-research-skills \
    --settings /path/to/academic-research-skills/antigravity/settings.json \
    --model <a strong model>
```

[`settings.json`](settings.json) applies to that session only. It lets terminal commands reach the four bibliographic indexes ARS queries (Crossref, OpenAlex, Semantic Scholar, arXiv). To make it permanent, add the same `read_url(...)` rules to `permissions.allow` in `~/.gemini/antigravity-cli/settings.json`.

Then use plain language ("compare three papers on ... by WHY / HOW / WHAT") or a command:

```text
/ars-3w retrieval-augmented generation and hallucination
/ars-plan
/ars-reviewer
/ars-full
```

## What the wrapper translates

Every generated skill ends with the same short compatibility note, from [`compatibility.md`](compatibility.md):

- read every ARS file to its last line, because of the 24,000-byte limit
- `${CLAUDE_PLUGIN_ROOT}` and repository-root paths resolve against the checkout
- Claude tool names mean the equivalent Antigravity tool
- specialist agents are dispatched as subagents, or run inline with a disclosure
- verification steps are mandatory and reported as actually performed
- AI-use disclosure names the real model and Antigravity, and lists what was degraded
- no write-scope guard; human checkpoints unchanged

The note is part of the ARS skills only. Installing the plugin adds no always-on rule; other sessions see just the 20 skill names and descriptions, as with the Claude Code plugin.

## Test

```bash
python3 antigravity/test_install.py
```

Checks that every generated skill is under 24,000 bytes, that core skill frontmatter is byte-identical to the original, that no unresolved `${CLAUDE_PLUGIN_ROOT}` remains in a command, and that the installer refuses to overwrite a directory it does not own.

Evidence from three recorded runs of one lightweight mode, and the state of a full `academic-pipeline` run that is still in progress, is in [`examples/antigravity/`](../examples/antigravity/README.md).

## Scope

A basic wrapper, not a reimplementation of Claude Code or of ARS orchestration. The original ARS content stays authoritative and unmodified.

The project license remains CC BY-NC 4.0. Attribution and noncommercial restrictions apply.
