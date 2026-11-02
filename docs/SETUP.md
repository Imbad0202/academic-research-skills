# ARS Setup

Prerequisites and optional setup for Academic Research Skills. If you only need Markdown output and the default Claude pipeline (the inherited session model), you can skip most of this — see "Minimum viable setup" below.

---

## Minimum viable setup

1. Install Claude Code (see below).
2. Export `ANTHROPIC_API_KEY`.
3. `claude` in this repo (or any project that has ARS in `.claude/skills/`).

That is enough for Markdown output + DOCX conversion instructions. Everything else in this document is optional.

## Python (optional)

The core skills (research / write / review) need no Python — they are prompt-driven. A **real Python interpreter** is needed only for: the `PreToolUse` write-scope guard (optional subagent hardening — if no real Python is found it cleanly no-ops and the guard is simply inactive; core skills are unaffected), plus a few opt-in features that shell out to Python (revision-patch mode, the submission-package verifier, and the `/ars-cache-invalidate` / `/ars-mark-read` / `/ars-unmark-read` commands). On Windows, note that `python3` is often a non-functional Microsoft Store placeholder rather than real Python; install Python from python.org (or via `winget`) so the launcher can find a real interpreter. The guard launcher is a POSIX shell script and `hooks.json` invokes it through `bash`, so on Windows it needs **Git Bash** (bundled with Git for Windows). With Git Bash present, a missing real Python degrades cleanly (the guard no-ops, silently). Without Git Bash, Claude Code falls back to PowerShell, which cannot run the `.sh` launcher at all: the guard is inactive and the `PreToolUse` hook will log an error per call rather than no-op quietly (accepted degradation — the guard is optional and never blocks your writes, but the hook noise is the trade-off until Git Bash is installed).

---

---

## Install Claude Code

**Recommended: Native installer** (no Node.js required, auto-updates):

```bash
# macOS / Linux
curl -fsSL https://claude.ai/install.sh | bash

# Windows (PowerShell)
irm https://claude.ai/install.ps1 | iex
```

**Platform support.** macOS and Linux are the tested platforms; CI runs on Ubuntu only. Windows is best-effort: the scripts that lock files share one helper (`scripts/file_lock.py`) with an `msvcrt` backend, no Windows CI job exists, and Windows behaviour rests on contributor verification (#843, #845). On Windows, shared read locks degrade to exclusive locks with a short wait, indefinite lock waits are capped at 30 seconds, and the inquiry branch ledger alpha refuses to run.

<details>
<summary>Alternative: npm install (deprecated)</summary>

Requires Node.js 18+.

```bash
npm install -g @anthropic-ai/claude-code
```

</details>

## Set up API key

Get an Anthropic API key at <https://console.anthropic.com/>.

```bash
# Claude Code will prompt for your API key on first run
claude
```

Or set it as an environment variable:

```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxx
```

## DOCX output (optional)

Direct `.docx` generation uses [Pandoc](https://pandoc.org/). If Pandoc is unavailable, the formatter falls back to Markdown + DOCX conversion instructions.

```bash
# macOS
brew install pandoc

# Linux (Debian/Ubuntu)
sudo apt-get install pandoc

# Windows — download from https://pandoc.org/installing.html
```

## LaTeX / PDF output (optional)

PDF output requires [tectonic](https://tectonic-typesetting.github.io/) and specific fonts. **This is optional** — Markdown output and DOCX conversion instructions work without any of this.

```bash
# macOS
brew install tectonic

# Linux (Debian/Ubuntu)
curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh

# Windows — download from https://tectonic-typesetting.github.io/en-US/install.html
```

**Required fonts** (for APA 7.0 CJK output):

- **Times New Roman** — usually pre-installed on macOS/Windows; on Linux install `ttf-mscorefonts-installer`
- **Source Han Serif TC VF** (思源宋體) — download from [Google Fonts](https://fonts.google.com/specimen/Noto+Serif+TC) or [Adobe GitHub](https://github.com/adobe-fonts/source-han-serif)
- **Courier New** — usually pre-installed

> If you only need Markdown output or DOCX conversion instructions, skip this entirely. Direct `.docx` generation requires Pandoc, and PDF generation requires `tectonic`.

---

## Material Passport `literature_corpus[]` adapters (v3.6.4+, optional)

If you maintain a curated literature corpus (Zotero, Obsidian, a folder of PDFs, etc.), you can pre-load it into a Material Passport so Phase 1 ARS agents read your library *before* searching external databases. This is opt-in and presence-based — when no corpus is supplied, ARS runs the external-DB-only flow unchanged.

Three reference Python adapters ship with v3.6.4 at `scripts/adapters/`:

```bash
# 1. Install the dev dependencies (the adapter requirements are declared in requirements-dev.txt)
pip install -r requirements-dev.txt

# 2. Run a reference adapter (pick one that matches your corpus source).
#    Both --passport and --rejection-log are required.
python scripts/adapters/folder_scan.py --input /path/to/pdfs               --passport passport.yaml --rejection-log rejection_log.yaml
python scripts/adapters/zotero.py      --input my-zotero-export.json       --passport passport.yaml --rejection-log rejection_log.yaml
python scripts/adapters/obsidian.py    --input ~/Obsidian/Lit\ Notes       --passport passport.yaml --rejection-log rejection_log.yaml

# 3. Pass the resulting passport.yaml into your ARS session
#    (concrete invocation depends on which skill you're running — see scripts/adapters/README.md)
```

Each adapter emits two files: `passport.yaml` (Schema 9 with `literature_corpus[]` populated) and `rejection_log.yaml` (always emitted, empty when no rejections — closed enum of categorical reasons). Users with non-reference corpus sources are expected to write their own adapters following [`academic-pipeline/references/adapters/overview.md`](../academic-pipeline/references/adapters/overview.md).

v3.6.5 wires `bibliography_agent` (deep-research, Phase 1) and `literature_strategist_agent` (academic-paper, Phase 1) as the consumers — both run the corpus-first / search-fills-gap flow when a non-empty corpus is present and parses cleanly. See [`academic-pipeline/references/literature_corpus_consumers.md`](../academic-pipeline/references/literature_corpus_consumers.md) for the consumer protocol.

## Optional environment flags (v3.5.1+)

ARS exposes a few opt-in flags. All default to OFF; setting them changes behaviour for the current session only. These flags are behavior toggles; for standing *content* preferences (citation style, search inclusion), see [§"Standing preferences via CLAUDE.md"](#standing-preferences-via-claudemd) below.

| Flag | Since | What it does | Reference |
|---|---|---|---|
| `ARS_CROSS_MODEL` | v3.0 | Enable cross-model verification (see next section) | [§"Cross-model verification"](#cross-model-verification-optional) |
| `ARS_CROSS_MODEL_TRANSPORT=codex` | #630 | Use ChatGPT subscription transport for citation-integrity calls only; all DA/reviewer/judgment paths remain API-key based | `shared/cross_model_verification.md` |
| `ARS_SOCRATIC_READING_PROBE=1` | v3.5.1 | Activate the Socratic reading-check probe layer in `socratic_mentor_agent`. Goal-oriented intent only; fires at most once per session when user has cited a specific paper; decline logged without penalty. | `deep-research/agents/socratic_mentor_agent.md` |
| `ARS_PASSPORT_RESET=1` | v3.6.3 | Promote every FULL and MANDATORY checkpoint to a context-reset boundary. Required to *emit* boundary entries; **not** required to invoke `resume_from_passport=<hash>` in a fresh session. With the flag ON in `systematic-review` mode, reset is mandatory at every FULL and MANDATORY checkpoint. | `academic-pipeline/references/passport_as_reset_boundary.md` |
| `ARS_AUDIT_ARTIFACT_GATE=1` | #925 | Turn on the v3.6.7 Audit Artifact Gate, which has you run `scripts/run_codex_audit.sh` outside the session at each transition after a `synthesis_agent` / `research_architect_agent` (survey-designer) / `report_compiler_agent` (abstract-only) deliverable; the wrapper sends the deliverable to an external model, and the gate blocks on its findings. The flag is configuration, not consent: the gate runs only after you agree for the run. Off by default; the Stage 2.5 / 4.5 integrity gates run either way. | `academic-pipeline/agents/pipeline_orchestrator_agent.md` § 3.5 |
| `ARS_CROSS_MODEL_SAMPLE_INTERVAL` | v3.5.0 | With cross-model on, run the second-model collaboration-depth observer every N checkpoints instead of every one (default `1`; the Stage 6 whole-pipeline pass always runs). It does not change integrity-gate sampling. | `academic-pipeline/agents/pipeline_orchestrator_agent.md` § Collaboration Depth Observer |
| `ARS_CLAIM_AUDIT=1` | v3.8 | Turn on the claim-faithfulness audit: claims are judged against their cited sources, and unsupported ones block final output. In pipeline runs it first runs at Stage 4.5, so a finding can still be corrected. | `academic-pipeline/agents/pipeline_orchestrator_agent.md` § 3.6 |
| `ARS_SOCRATIC_ADJACENT_PROBE=1` | v3.13.0 (#461) | Let the Socratic Mentor raise one adjacent framing at a time, as a question, at most twice per session. | `deep-research/agents/socratic_mentor_agent.md` |
| `ARS_RE_REVIEW_LEGACY=1` | v3.20.0 (#576) | Run Stage 3' re-review with the archived pre-contract schemas and checker instead of the three-gate contract. | `academic-paper-reviewer/references/re_review_mode_protocol.md` § Legacy Mode |
| `ARS_INQUIRY_LEDGER=1` | v3.21.1 (#743) | Alpha inquiry branch ledger. It needs a research-workflow profile binding, which no pipeline step creates; without one the run stays linear and says so. | `academic-pipeline/agents/pipeline_orchestrator_agent.md` § Inquiry Branch Ledger |
| `ARS_VERIFICATION_CACHE_PATH` | v3.11 | Override the citation-verification cache location (see below). Not an on/off flag — the cache is on by default; this only relocates it. | `scripts/verification_cache.py` |
| `ARS_CACHE_STALE_ADVISORY_DAYS` | v3.18.0 (#541) | Age threshold (days) for the cache-staleness advisory: cache-served verifications older than this surface as `ADV-CACHE` advisory rows at the integrity checkpoints (never gating). Default 30; `0` disables; malformed/negative values fall back to the default. | `scripts/verification_cache.py` |
| `ARS_CACHE_REVALIDATE=1` | v3.18.0 (#541) | Opt-in live re-verification at the gate: cached rows past the staleness threshold are re-verified live (per-row bypass, then re-populated) instead of served. Cost scales with the stale-row count. Default off = advisory-only. | `scripts/verification_gate/__init__.py` + `integrity_verification_agent.md` § A0.5 |
| `ARS_MODEL_TIERING` | v3.16.0 (#517) | Opt-in model tiering: `economy` (frontier session — execution-type agents step down one tier, floor Opus-class) or `quality-boost` (below-frontier session — judgment-type agents jump up to the frontier tier at the checkpoint surfaces: Stage 2.5/4.5 gates, the opt-in Stage 4→5 claim–ref audit, and final review). Unset = session model everywhere; unknown values warn once and behave as unset. | `shared/model_tiering.md` |

---

## Standing preferences via CLAUDE.md

ARS deliberately ships no user-level configuration file. The supported way to get "set once, applies every run" behavior for content preferences is a preferences block in your project's `CLAUDE.md`: Claude Code loads it at session start, and every ARS agent dispatched in that session inherits it as context. This is a stated design position, not a missing feature — search-related preferences are per-project inclusion/exclusion criteria that belong in the Annotated Bibliography's `search_strategy` (Schema 2), and a machine-global config silently inherited across projects would be a methodological hazard for systematic-review work. Decision record: #634.

Copy-pasteable template (adjust to taste):

```markdown
## ARS standing preferences

- Citation style: APA 7th unless a venue template says otherwise.
- Literature search: exclude preprints unless I explicitly ask; prefer
  peer-reviewed journal articles.
- Journal tier: when ranking or shortlisting sources, prefer higher-tier
  journals in the field, and say so when unsure of a journal's tier.
- Open access: prefer OA versions when citing, and link the OA copy.
```

Two honest limitations:

- **Journal tiers are model judgment.** None of the four lookup indexes (Semantic Scholar, OpenAlex, Crossref, arXiv) serves quartile or tier data, so a tier preference is applied from the model's own knowledge and should be stated as such — treat tier claims as advisory, never as verified metadata.
- **There is intentionally no output-directory setting.** The user-supplied Material Passport path is the single discovery anchor (v3.6.8 design round, decision R4-003); a standing output-location preference would create a second source of truth. Name the destination per run.

If a preference changes what a systematic review may include (preprint exclusion, language limits, date windows), record it in that project's `search_strategy` rather than relying on the ambient block — the ambient block sets defaults, the Schema 2 `search_strategy` is the auditable record.

Re-evaluation trigger (recorded in #634): an ARS-owned preferences surface gets revisited only if additional users independently request it, or a platform port lacks a `CLAUDE.md` equivalent. If ever built, the architecturally consistent shape is a Material Passport-level `user_preferences` input aggregate (like `literature_corpus[]`), not a machine-global config file.

---

## Citation verification cache (v3.11, #182)

The deterministic citation-existence gate (#182) cross-checks each reference against Semantic Scholar, OpenAlex, Crossref, and arXiv. To avoid re-querying the same paper across drafts, results are cached in a local SQLite store.

- **No setup required.** The cache is created automatically at `~/.cache/ars/verification.db` on first use; entries expire after 90 days. The arXiv resolver needs no API key.
- **Relocate it** by exporting `ARS_VERIFICATION_CACHE_PATH=/your/path.db` (e.g. to share one cache across projects, or to keep it on a faster disk).
- **Invalidate one citation** with `/ars-cache-invalidate <citation_key>` — removes every cached row for that key (all four resolvers, all query forms); idempotent no-op if nothing is cached.

The cache is single-process (SQLite WAL); concurrent multi-user access to one cache file is out of scope.

For the complete picture of what leaves the machine (resolvers, optional cross-model
calls, the update check) and every local store's lifetime and deletion path, see
[DATA_FLOWS.md](DATA_FLOWS.md).

---

## Cross-model verification (optional)

ARS works with the inherited Claude session model alone. For higher confidence, you can optionally enable a second AI model to independently verify integrity checks and challenge the devil's advocate.

### Quick setup

```bash
# Step 1: Set your API key (choose one or both)
export OPENAI_API_KEY="sk-your-key-here"        # For GPT-6 Astra / GPT-5.6 Sol / GPT-5.5
export GOOGLE_AI_API_KEY="AIza-your-key-here"    # For Gemini 4 Argon / Gemini 3.1 Pro

# Step 2: Choose your cross-verification model
export ARS_CROSS_MODEL="gpt-6-astra"            # Current OpenAI flagship — provisional pending ARS validation (run scripts/cross_model_smoke_test.sh)
# or: export ARS_CROSS_MODEL="gemini-4-argon"  # Current Google flagship — provisional pending ARS validation (no Gemini smoke script; check one known citation first)
# or: export ARS_CROSS_MODEL="gemini-3.1-pro-preview"  # Previous Google generation — validated, strong at factual verification
# or: export ARS_CROSS_MODEL="gpt-5.6-sol"      # Previous generation — validated on the ChatGPT-subscription citation transport, provisional on this API route
# or: export ARS_CROSS_MODEL="gpt-5.5"          # Previous generation — validated (designated API-route bakeoff baseline)

# Optional: reasoning effort for OpenAI verifier calls (unset = provider default)
# GPT-6 Astra API: low|medium|high|xhigh|max (the Codex citation transport rejects ultra)
# export ARS_CROSS_MODEL_REASONING_EFFORT="medium"

# Step 3: Run Claude Code as normal — cross-verification activates automatically
claude
```

### What changes when enabled

| Feature | Without cross-model | With cross-model |
|---|---|---|
| Integrity verification | Single-model 100% check | + risk-stratified verification by 2nd model: 100% of high-impact references (final gate adds 100% of new/changed-claim references) + a sampled remainder |
| Devil's Advocate | Single-model DA | + Cross-model generates a blind, separately executed critique; novel findings added |
| Peer Review | 5 reviewers (same model) | Same 5 reviewers + cross-model DA critique/calibration support |
| Irreversible checkpoints | Single-model decision | + Blind cross-model decision at design freeze + final editorial decision; divergence escalated to you, never averaged |

### Cost

Full pipeline adds ~$0.60-1.10 in cross-model API costs (order-of-magnitude; measured at GPT-5.4 Pro pricing). See [`shared/cross_model_verification.md`](../shared/cross_model_verification.md) for the current model lineup and detailed breakdown.

### No API key? No problem

Without `ARS_CROSS_MODEL` set, everything works exactly as before. The cross-model features are invisible and add zero overhead.

### ChatGPT subscription transport (citation integrity only)

If Codex CLI 0.147.0+ is logged in through a ChatGPT subscription, citation-integrity
calls can use that subscription without an OpenAI API key. This does not cover
Devil's Advocate, Reviewer 2, calibration, re-review, or checkpoint judgments.

```bash
# Citation-integrity calls only. General DA/reviewer/judgment calls remain on API transport.
export ARS_CROSS_MODEL_TRANSPORT="codex"
# gpt-6-astra: current OpenAI flagship — provisional on this transport (entry-gate
# smoke PASS 2026-09-05 on codex-cli 0.153.4; no bakeoff run yet).
export ARS_CROSS_MODEL="gpt-6-astra"
# gpt-5.6-sol is validated for THIS transport (2026-08-19 codex-transport bakeoff,
# superiority on recall + latency — audits/bakeoff-gpt-5-6-sol-codex-2026-08-19.md):
# export ARS_CROSS_MODEL="gpt-5.6-sol"

python3 scripts/cross_model_codex_transport.py detect
# The producer sends one closed codex_citation_request/1.0 object on stdin:
printf '%s' "$CITATION_REQUEST_JSON" | scripts/cross_model_codex_verify.sh
```

The detector honors custom `CODEX_HOME` and requires the exact subscription
attestation `Logged in using ChatGPT`; it never prints credentials. The adapter
uses an auth-only ephemeral home, empty working root, read-only sandbox, no local
tools, and binds accepted source URLs to structured search results. The optional
live smoke `scripts/cross_model_smoke_test_codex.sh` spends subscription/model/network
capacity and is never run by CI.

---

## Installation methods

Claude discovers skills at `<install-root>/<skill-name>/SKILL.md`. This repo contains five separate skills, each with its own `SKILL.md`:

- `deep-research`
- `academic-paper`
- `academic-paper-reviewer`
- `academic-pipeline`
- `sr-screener`

Do not install the whole repository as one nested skill folder under `.claude/skills/academic-research-skills/`; that buries the five `SKILL.md` files one level too deep for discovery. See Anthropic's [Claude Code Skills documentation](https://code.claude.com/docs/en/skills).

The methods below differ in more than convenience: hooks, slash commands, the tools
allowlist, subagent orchestration, and script-backed checks are each available in some
channels and degraded or absent in others. Before relying on any of those mechanisms,
check the per-channel map: [CONTROL_AVAILABILITY.md](CONTROL_AVAILABILITY.md).

### Method 0: Claude Code Plugin (v3.7.0+, recommended for Claude Code CLI / IDE users)

If you use Claude Code CLI, VS Code extension, or JetBrains extension, install ARS as a plugin:

```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

The five skills (`deep-research`, `academic-paper`, `academic-paper-reviewer`, `academic-pipeline`, `sr-screener`) load from the skill paths declared in `.claude-plugin/plugin.json`. The repository has no `skills/` symlink directory: a plugin copy synced from a claude.ai account marketplace drops symlinks, and Claude Code would load every skill twice if it found both (#1035).

**Slash command forms (#633).** Plugin installs namespace commands as `/academic-research-skills:ars-<mode>` — that form is canonical. Every command also declares an explicit frontmatter `name`, so on Claude Code v2.1.216 or later the bare `/ars-<mode>` alias works too whenever no other command claims that name; the bare form is what the session-start announce lists. On Claude Code older than v2.1.216, the frontmatter `name` replaces the whole command name, so commands appear only in their bare `/ars-<mode>` form (still invocable; the namespaced form loses autocomplete).

**Strongly recommended: open auto-update.** Open the `/plugin` UI, find `academic-research-skills`, and toggle auto-update on. ARS releases roughly every 1–2 weeks; auto-update keeps you in sync without manual refreshes. To refresh manually: `/plugin update academic-research-skills`. (`/plugin marketplace update academic-research-skills` only refreshes the marketplace source list, not the installed plugin itself.)

**Built-in update reminder.** The plugin also nudges you on its own: at session start it compares your installed version against `main` (at most one network request per day, 3-second ceiling, silent on any failure) and, when you are behind, prepends one line to the session-start announce pointing at `/plugin update academic-research-skills`. Set `ARS_UPDATE_CHECK=0` to disable the check entirely. Privacy: the check performs a single HTTPS GET of this repository's public `.claude-plugin/plugin.json` and transmits no user data.

#### Install from claude.ai or Claude Desktop (account marketplace)

On a paid plan (Pro, Max, Ultra, Team, Enterprise), you can add the same plugin from claude.ai or Claude Desktop. See Anthropic's [Use plugins in Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude).

1. Open **Customize → Plugins**.
2. Select **Add → Add marketplace → Add from a repository**.
3. Enter `Imbad0202/academic-research-skills`.
4. Install `academic-research-skills` from the new marketplace.

What runs depends on where you use it. Anthropic's article says skills and commands work in chat, in Cowork and in Claude Code, and that hooks and sub-agents run in Cowork and Claude Code but not in chat. We checked on Claude Desktop (macOS) on 2026-11-02, once before #1037 and once after it:

- **Plain chat:** one skill loaded, `/ars-lit-review` ran, and a skill script ran in Claude's cloud environment. The SessionStart announce did not appear. After #1037 the session listed only built-in subagent types (`general-purpose`, `Explore`, `Plan` and others), no plugin agents, and offered `general-purpose` instead.
- **Work in a project or a local folder:** in a local folder before #1037, the SessionStart announce appeared, and a script ran on a cloud copy of the plugin and wrote its output to the folder. In a project after #1037, the session listed the four plugin agents (for example `academic-research-skills:synthesis-agent`) and dispatched `synthesis-agent` directly.
- **Not tested:** the write-scope guard, the tools allowlist, the update reminder, cross-model verification, sr-screener's dual review, a full pipeline run, and projects on claude.ai in a browser. Do not assume the write-scope guard is active on claude.ai or Claude Desktop.

Before #1037 the four plugin agents had underscore names, which claude.ai rejects: the marketplace page showed a warning for each one, saying the listed items were not included. They are now `synthesis-agent`, `research-architect-agent`, `report-compiler-agent` and `screening-reviewer-agent`, and the warnings are gone. The per-mechanism map is in [CONTROL_AVAILABILITY.md](CONTROL_AVAILABILITY.md).

The marketplace syncs new commits from this repository: after two merges in November 2026 the synced commit moved without a reinstall.

The account marketplace also syncs the plugin to Claude Code v2.1.273 or later when Claude Code is signed in with the same account. It does not sync when Claude Code uses an API key or a cloud provider such as Amazon Bedrock. In our check, with ARS also installed from the GitHub marketplace, `claude plugin list` showed the synced copy as not loaded, so the skills did not load twice.

Use one install route in each place. If you uploaded the skill zips (Method 3 or 4a) or copied the skill folders into Claude Code (Methods 1-2), remove those copies when you move to the plugin, or the same skill can appear twice.

**Plugin platform scope:**
- ✅ Claude Code CLI / VS Code extension / JetBrains extension — full support
- ✅ claude.ai and Claude Desktop, paid plans — through the account marketplace above; hooks and plugin agents do not run in plain chat, and the write-scope guard is untested there
- ❌ Anthropic API direct calls — plugins not supported
- ➡️ Codex CLI — install the sibling distribution [`Imbad0202/academic-research-skills-codex`](https://github.com/Imbad0202/academic-research-skills-codex) (same workflow content, Codex-native packaging)

### Method 1: As project skills (recommended)

Use this when you want ARS available inside an existing Claude Code project.

Clone the repo to a stable local path, then copy each skill folder into your project's `.claude/skills/` directory:

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git ~/academic-research-skills

cd /path/to/your/project
mkdir -p .claude/skills
cp -R ~/academic-research-skills/deep-research .claude/skills/deep-research
cp -R ~/academic-research-skills/academic-paper .claude/skills/academic-paper
cp -R ~/academic-research-skills/academic-paper-reviewer .claude/skills/academic-paper-reviewer
cp -R ~/academic-research-skills/academic-pipeline .claude/skills/academic-pipeline
cp -R ~/academic-research-skills/sr-screener .claude/skills/sr-screener
```

Expected path shape:

```text
/path/to/your/project/.claude/skills/deep-research/SKILL.md
/path/to/your/project/.claude/skills/academic-paper/SKILL.md
/path/to/your/project/.claude/skills/academic-paper-reviewer/SKILL.md
/path/to/your/project/.claude/skills/academic-pipeline/SKILL.md
/path/to/your/project/.claude/skills/sr-screener/SKILL.md
```

`sr-screener` runs its screening reviewers as a subagent. For a project-skills install, also copy `sr-screener/agents/screening_reviewer_agent.md` into `.claude/agents/` (details: `sr-screener/references/orchestration.md` § 1).

Then copy the `.claude/CLAUDE.md` content into your project's `.claude/CLAUDE.md` (merge with existing if you have one).

> **Global Claude Code installation:** To make these skills available across your Claude Code projects, install the five folders to `~/.claude/skills/` instead:
>
> ```bash
> git clone https://github.com/Imbad0202/academic-research-skills.git ~/academic-research-skills
>
> mkdir -p ~/.claude/skills
> cp -R ~/academic-research-skills/deep-research ~/.claude/skills/deep-research
> cp -R ~/academic-research-skills/academic-paper ~/.claude/skills/academic-paper
> cp -R ~/academic-research-skills/academic-paper-reviewer ~/.claude/skills/academic-paper-reviewer
> cp -R ~/academic-research-skills/academic-pipeline ~/.claude/skills/academic-pipeline
> cp -R ~/academic-research-skills/sr-screener ~/.claude/skills/sr-screener
> ```

### Method 2: As a standalone project

Use this when you want to work directly inside the ARS repository.

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git
cd academic-research-skills
claude
```

<details>
<summary><strong>No Git?</strong> Download as ZIP instead</summary>

1. Go to <https://github.com/Imbad0202/academic-research-skills>
2. Click the green **Code** button → **Download ZIP**
3. Extract the ZIP to your desired location
4. For Method 1: copy the five extracted skill folders (`deep-research`, `academic-paper`, `academic-paper-reviewer`, `academic-pipeline`, `sr-screener`) into `.claude/skills/` inside your project
5. For standalone use: open a terminal in the extracted folder and run `claude`

</details>

### Method 3: Claude Cowork (desktop)

This fallback uploads the five ARS skills to [Claude Cowork](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork), Claude Desktop's agentic workspace.

> **Use this only when you cannot add the plugin.** On claude.ai and Claude Desktop, the recommended route is the [account marketplace](#install-from-claudeai-or-claude-desktop-account-marketplace) in Method 0. It installs the five skills together with the `/ars-*` commands, the plugin agents and the hooks, and it syncs new commits from this repository. Upload the skills only in one of these cases:
>
> - Your plan has no plugins. The plans Anthropic lists for plugins are all paid plans.
> - Your organization's marketplace allow list or block list does not permit this repository ([Manage plugins for your organization](https://support.claude.com/en/articles/13837433-manage-plugins-for-your-organization)).
>
> Uploading also needs skill uploads to be available to you: on Team and Enterprise, an admin can turn off user-created skills. The upload route installs the skills only, and you upload again for each release.
>
> Anthropic is merging chat and Cowork into one experience, in stages ([Claude Cowork and chat are one Claude](https://support.claude.com/en/articles/16761823-claude-cowork-and-chat-are-one-claude)). Uploaded skills carry over. Where this section says "Cowork Task", read "a conversation" on an account that has the merged experience.

> **Cowork does not read `~/.claude/skills/`.** That directory belongs to Claude Code (the CLI / IDE), and Cowork does not scan it. Cowork loads skills you upload through **Customize → Skills**, each as its own zip. Symlinking or copying the skill folders into `~/.claude/skills/` will not make them appear in Cowork, no matter how many times you restart.

#### Prerequisites

- Claude Desktop latest version on macOS or Windows. Download from Anthropic's [Claude Desktop page](https://claude.ai/download).
- Active internet connection; Cowork tasks call the Anthropic API.
- Keep Claude Desktop open while Cowork tasks run. Cowork runs inside the Desktop process.
- A paid plan with Cowork access. See Anthropic's [Cowork requirements](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork) for current plan availability.
- **Code execution / file creation must be enabled** in **Settings → Capabilities**, or the Skills section will not appear. See Anthropic's [Use Skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude).
- On Team or Enterprise plans, your organization admin may have disabled Skills. If the Skills section is missing after enabling code execution, ask your admin to check org-level controls.

#### Step 1: Build one zip per skill

Clone the repo, then zip each of the five skill folders on its own. Anthropic's [Create custom skills](https://claude.com/docs/skills/how-to) asks for the skill folder at the top of the zip, so the archive holds `<skill-name>/SKILL.md`, and for a folder name that matches the `name` field in `SKILL.md`. The `-x "*.DS_Store"` flag keeps macOS metadata out of the archive.

Anthropic provides a skill named `deep-research`. On Claude Desktop on 2026-11-02 it was already in the Skills list, and an upload with the same name was refused ("This skill name is already in use"). The commands below therefore zip a copy of `deep-research` named `ars-deep-research`, with its `name` field changed to match. The clone itself does not change.

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git
cd academic-research-skills

for s in academic-paper academic-paper-reviewer academic-pipeline sr-screener; do
  zip -r "$s.zip" "$s" -x "*.DS_Store"
done

# deep-research is uploaded as ars-deep-research
rm -rf ars-deep-research && cp -R deep-research ars-deep-research
perl -pi -e 's/^name: deep-research(\r?)$/name: ars-deep-research$1/' ars-deep-research/SKILL.md
zip -r ars-deep-research.zip ars-deep-research -x "*.DS_Store"
rm -rf ars-deep-research
```

This produces five zips in the repo root: `ars-deep-research.zip`, `academic-paper.zip`, `academic-paper-reviewer.zip`, `academic-pipeline.zip`, `sr-screener.zip`. Run `unzip -l <zip>` to check one: every entry starts with the skill folder, for example `ars-deep-research/SKILL.md`, `ars-deep-research/agents/` and `ars-deep-research/references/` (`sr-screener` also carries `sr-screener/scripts/`).

The other ARS skills refer to `deep-research` by name. In an upload install, whether such a reference reaches the uploaded `ars-deep-research` or Anthropic's `deep-research` has not been tested.

#### Step 2: Upload each zip

1. In Claude Desktop (or claude.ai — uploaded skills sync to the same account), go to **Customize → Skills** (the location Anthropic's [Create custom skills](https://claude.com/docs/skills/how-to) gives for both claude.ai and the desktop app; older versions placed it under Settings → Capabilities → Skills).
2. Use the **+** in the Skills panel to upload a skill, and select one of the five zips. Repeat for all five, one at a time.
3. Each skill then appears under **Personal skills**, already enabled, with **Trigger: Slash command + auto**. Re-uploading a skill with the same name replaces the existing one (useful when updating to a new ARS release).

Checked on Claude Desktop in June 2026: `deep-research.zip` installed, the full skill description was kept, and `/deep-research` appeared in the Cowork command palette. That was before the name clash above. On 2026-11-02, two `ars-deep-research.zip` files were checked: one built with the commands above, and one with `SKILL.md` at its top level, the layout earlier versions of this page gave. Both uploaded with the 1,021-character description and ran in a conversation (see the trade-off below).

#### Step 3: Use the skills in a Cowork Task

Type `/` in a Cowork Task to open the command palette and select a skill, or describe your intent in plain language (e.g. "do a deep literature review on X") and Cowork routes by the skill's `description`.

#### One trade-off versus Claude Code

Uploaded this way, each skill runs on its own as a standalone instruction set. This is a different experience from Claude Code. In Claude Code the skills work as a coordinated team: `academic-pipeline` chains them (research → write → review → revise) and each skill drives its own group of sub-agents. Uploaded skills do not register ARS's own agents, commands or hooks. In two checks on 2026-11-02 (Claude Desktop on macOS, chat merged with Cowork, the ARS plugin removed), one for each zip layout above, a conversation using the uploaded `ars-deep-research` skill dispatched a built-in `Explore` sub-agent, which read `agents/synthesis_agent.md` from the uploaded skill and returned its first heading. Each time, the first dispatch did not run and a retry did. Whether the skills' multi-agent stages, and the full end-to-end pipeline, run this way has not been tested. For the full orchestrated experience, install ARS in Claude Code through Method 0 (plugin) or Method 1 (project skills) above. On Claude Desktop, the account marketplace in Method 0 also brings the plugin agents to project and folder work; a full pipeline run there has not been tested.

### Method 4: Use with claude.ai (web)

> **To run the skills on claude.ai, use Method 0.** On a paid plan, the [account marketplace](#install-from-claudeai-or-claude-desktop-account-marketplace) installs ARS as a plugin. This section covers the two older routes: reading the repository as Project knowledge (4b) and uploading skill zips (4a).

ARS is a Claude Code-native suite. The skills are multi-agent teams (4 to 13 agents each) that depend on multi-agent orchestration, executable scripts under `scripts/`, and Material Passport file handoffs. claude.ai's web interface delivers a different runtime than Claude Code, and the two routes covered here reach this repository in different ways:

- **Method 4b — Project + GitHub integration** (to read the repository): brings the repository into a claude.ai Project as retrievable knowledge. Claude can read the skill bodies, references, schemas, and example outputs, and answer questions or draft against them. Not a Skill install — auto-loading and skill routing do not happen, but the content is fully available for reading and citation.
- **Method 4a — Custom Skill upload**: claude.ai's standard Skill install path (Customize → Skills, one zip per skill). Not recommended for this suite — see the rationale below before using it.

#### Prerequisites

- A claude.ai account. Plan availability differs by sub-method (see below).
- **For Method 4b**: claude.ai Projects are available across plan tiers per Anthropic's [What are Projects?](https://support.claude.com/en/articles/9517075-what-are-projects); paid plans (Pro, Max, Team, Enterprise) get larger knowledge capacity and stronger retrieval. GitHub authentication is required through the Anthropic connector — see [Using the GitHub integration](https://support.claude.com/en/articles/10167454-using-the-github-integration) and [Set up Claude integrations](https://support.claude.com/en/articles/10168395-set-up-claude-integrations). Private repositories require the Anthropic GitHub App to be authorized on the repo or organization. Team and Enterprise plans require owner-level connector enablement before users can add GitHub-sourced files.
- **For Method 4a**: Custom Skills are available on Free, Pro, Max, Team, and Enterprise per Anthropic's [Use Skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude). The same article notes that Skills require **code execution to be enabled** in Settings → Capabilities. No GitHub authentication is needed for Method 4a — you zip each skill folder locally and upload one zip per skill through Customize → Skills. Zip structure errors and a skill name already in use surface as upload-time errors; see Anthropic's [Custom Skills packaging documentation](https://claude.com/docs/skills/how-to) and [How to create custom Skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills).

#### Method 4b: Project + GitHub integration (repository reading)

claude.ai Projects deliver content as static knowledge for Claude to retrieve and cite — see Anthropic's [What are Projects?](https://support.claude.com/en/articles/9517075-what-are-projects). This is NOT a Skill install. Skill auto-loading does not happen. Trigger phrases do not route. Claude can read the repo content for reading and citation, and answer questions about it, but does not execute the skills as agentic workflows.

Use this when you want claude.ai to have access to the repo content — including the agent definitions, references, and example outputs — for reading and citation, without needing agentic skill execution. For agentic execution, use Method 0 (plugin, including the account marketplace on claude.ai and Claude Desktop), or Methods 1-2 in Claude Code.

> **The merged chat and Cowork experience does not support this yet.** Anthropic lists "Add from GitHub" as not yet supported once chat and Cowork are one experience ([Claude Cowork and chat are one Claude](https://support.claude.com/en/articles/16761823-claude-cowork-and-chat-are-one-claude)). On an account that has the merged experience, step 3 below may not be available.

1. Sign in to [claude.ai](https://claude.ai).
2. Create a new Project: **Projects** → **Create Project**.
3. Import from GitHub: in the Project, click **Files** → **+** → **GitHub** → select `Imbad0202/academic-research-skills`.
4. Select the folders/files below.

   | Select | Directory / file | Why |
   |---|---|---|
   | ✅ | `deep-research/` | Core skill content for reading |
   | ✅ | `academic-paper/` | Core skill content for reading |
   | ✅ | `academic-paper-reviewer/` | Core skill content for reading |
   | ✅ | `academic-pipeline/` | Core skill content for reading |
   | ✅ | `sr-screener/` | Core skill content for reading |
   | ✅ | `shared/` | Cross-model verification, handoff schemas, shared protocols |
   | ✅ | `scripts/` | `literature_corpus[]` adapters (`folder_scan`, `zotero`, `obsidian`) + schema validators; required for Material Passport corpus mode and CI-style validation |
   | ✅ | `MODE_REGISTRY.md` | Mode definitions |
   | Optional | `.claude/` | Project-level routing rules. Skip if you set Project Instructions in step 5 below (recommended path); include only if you prefer to keep routing rules visible as Project files. |
   | Optional | `examples/` | Useful for reference examples; skip if you want a smaller Project knowledge set |
   | Optional | `.github/`, READMEs, LICENSE, etc. | Repository metadata; not needed for core reading context |

5. (Recommended) Set **Instructions** in the Project to the content of `.claude/CLAUDE.md` for better routing.
6. Start chatting: "Guide my research on X" or "Help me write a paper about Y".

Anthropic's current [Project file limits](https://support.claude.com/en/articles/8241126-upload-files-to-claude) state that Project file count is not artificially capped at 200; files have a 30 MB per-file limit and total usable content is still subject to context-window limits at runtime. Keep the Project focused so Claude retrieves the relevant files reliably.

#### Method 4a: Custom Skill upload (not recommended for this suite)

Method 4a is claude.ai's standard Custom Skill install path: zip each skill folder, upload through Customize → Skills, and Claude treats it as an installed Skill with auto-loading and routing. claude.ai's Custom Skills do support multi-file skill packages including `scripts/` (see Anthropic's [How to create custom Skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) on supporting files and code execution), so Method 4a is mechanically capable of hosting skills with executable assets. It is not recommended for this suite because the account marketplace in Method 0 installs the same skills together with their agents, commands and hooks. Two points about the upload route:

1. **ARS was built around Claude Code's orchestration**. Each ARS skill drives 12-13 specialised agents and hands files across sessions through the Material Passport. Uploaded skills do not register ARS's agents, commands or hooks. Checks on 2026-11-02 found that an uploaded skill can dispatch a built-in sub-agent (see the [Method 3 trade-off](#one-trade-off-versus-claude-code)); whether the multi-agent stages and the cross-session handoffs work this way has not been tested.
2. **Description length**. Anthropic's [Create custom skills](https://claude.com/docs/skills/how-to) allows a `description` of up to 1,024 characters, the limit in the [Agent Skills specification](https://agentskills.io/specification), and on 2026-11-02 Claude Desktop accepted the 1,021-character `deep-research` description, uploaded under the name `ars-deep-research`. This page used to cite a 200-character cap; that cap no longer applies, and the ARS descriptions are not trimmed.

**Recommended paths instead:**

- For skill execution on claude.ai or Claude Desktop, use the [account marketplace in Method 0](#install-from-claudeai-or-claude-desktop-account-marketplace) on a paid plan. Plugin agents and hooks do not run in plain chat there.
- Only if you cannot add the plugin (the cases listed in [Method 3](#method-3-claude-cowork-desktop)), upload the skills through Method 3. The five skills upload as standalone skills, without the plugin agents, commands or hooks.
- For claude.ai web access to the repo content, use [Method 4b (Project + GitHub integration)](#method-4b-project--github-integration-repository-reading). Claude reads the skill bodies, references, and examples, and you can ask questions or draft against them in a normal claude.ai chat.
- For Claude Code projects, use [Method 1 (project skills)](#method-1-as-project-skills-recommended) or [Method 2 (standalone)](#method-2-as-a-standalone-project).

If you still want to upload the skills, build and upload the zips as in [Method 3](#method-3-claude-cowork-desktop) Steps 1-2, including the `ars-deep-research` copy. Anthropic's [Create custom skills](https://claude.com/docs/skills/how-to) gives the same upload page for claude.ai and the desktop app.

**claude.ai vs Claude Code:**

- Method 4b is for content reading, not active Skill execution. For agentic skill execution, prefer Method 0 (Claude Code, or the account marketplace on claude.ai and Claude Desktop) or Methods 1-2.
- claude.ai does not support local shell commands; results may be less comprehensive than Claude Code workflows that rely on local scripts.
- Cross-model verification (`ARS_CROSS_MODEL`) requires Claude Code with API keys.
- Direct `.docx` generation requires Pandoc, and LaTeX/PDF output requires Claude Code with `tectonic`; claude.ai can still produce Markdown and DOCX conversion instructions.
### Method 5: Claude Science import (v3.14.0+)

Claude Science imports the five ARS skills straight from GitHub:

1. Open **Customize → Capabilities → Skills → Import from GitHub**.
2. Paste `https://github.com/Imbad0202/academic-research-skills` and click **Preview**.
3. All five skills (`academic-paper`, `academic-paper-reviewer`, `academic-pipeline`, `deep-research`, `sr-screener`) appear — click **Import** (the v3.14.0 check, before `sr-screener` was added, showed **Import 4 skills**).

**Notes:**

- Requires repo state v3.14.0+ — the importer reads the explicit skill paths declared in `.claude-plugin/marketplace.json`. Earlier tags exposed skills only through the symlinked `skills/` directory, which GitHub-API importers cannot traverse (they report "no skills/ dirs with SKILL.md").
- Imports are **point-in-time snapshots**: Claude Science does not track the repo. Re-import after an ARS release to pick up changes.
- **What transfers:** the methodology layer — each skill's `SKILL.md` and its protocols (research / writing / review), which Claude Science's agent reads when relevant.
- **What does not transfer:** Claude Code-specific machinery — the `/ars-*` slash commands, hooks (including the write-scope guard), cross-model verification scripts, and Task-tool subagent orchestration. Claude Science runs its own specialist-agent system and a built-in citation-checking reviewer; treat a Claude Science run as "ARS methodology + Claude Science's own machinery", not a 1:1 pipeline port.
