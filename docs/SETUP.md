# ARS Setup

Prerequisites and optional setup for Academic Research Skills. If you only need Markdown output and the default Claude Opus 4.7 pipeline, you can skip most of this — see "Minimum viable setup" below.

---

## Minimum viable setup

1. Install Claude Code (see below).
2. Export `ANTHROPIC_API_KEY`.
3. `claude` in this repo (or any project that has ARS in `.claude/skills/`).

That is enough for Markdown output + DOCX conversion instructions. Everything else in this document is optional.

---

## Install Claude Code

**Recommended: Native installer** (no Node.js required, auto-updates):

```bash
# macOS / Linux
curl -fsSL https://claude.ai/install.sh | bash

# Windows (PowerShell)
irm https://claude.ai/install.ps1 | iex
```

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
# 1. Install adapter dependencies (PyYAML + jsonschema, already in requirements-dev.txt)
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

ARS exposes a few opt-in flags. All default to OFF; setting them changes behaviour for the current session only.

| Flag | Since | What it does | Reference |
|---|---|---|---|
| `ARS_CROSS_MODEL` | v3.0 | Enable cross-model verification (see next section) | [§"Cross-model verification"](#cross-model-verification-optional) |
| `ARS_SOCRATIC_READING_PROBE=1` | v3.5.1 | Activate the Socratic reading-check probe layer in `socratic_mentor_agent`. Goal-oriented intent only; fires at most once per session when user has cited a specific paper; decline logged without penalty. | `deep-research/agents/socratic_mentor_agent.md` |
| `ARS_PASSPORT_RESET=1` | v3.6.3 | Promote every FULL checkpoint to a context-reset boundary. Required to *emit* boundary entries; **not** required to invoke `resume_from_passport=<hash>` in a fresh session. With the flag ON in `systematic-review` mode, reset is mandatory at every FULL checkpoint. | `academic-pipeline/references/passport_as_reset_boundary.md` |
| `ARS_CROSS_MODEL_SAMPLE_INTERVAL` | v3.5.0 | Sampling interval for cross-model integrity checks (advisory) | `shared/cross_model_verification.md` |

---

## Cross-model verification (optional)

ARS works with Claude Opus 4.7 alone. For higher confidence, you can optionally enable a second AI model to independently verify integrity checks and challenge the devil's advocate.

### Quick setup

```bash
# Step 1: Set your API key (choose one or both)
export OPENAI_API_KEY="sk-your-key-here"        # For GPT-5.4 Pro
export GOOGLE_AI_API_KEY="AIza-your-key-here"    # For Gemini 3.1 Pro

# Step 2: Choose your cross-verification model
export ARS_CROSS_MODEL="gpt-5.4-pro"            # Best reasoning
# or: export ARS_CROSS_MODEL="gemini-3.1-pro-preview"  # Strong at factual verification

# Step 3: Run Claude Code as normal — cross-verification activates automatically
claude
```

### What changes when enabled

| Feature | Without cross-model | With cross-model |
|---|---|---|
| Integrity verification | Single-model 100% check | + 30% sample independently verified by 2nd model |
| Devil's Advocate | Single-model DA | + Cross-model generates independent critique, novel findings added |
| Peer Review | 5 reviewers (same model) | Same 5 reviewers + cross-model DA critique/calibration support |

### Cost

Full pipeline adds ~$0.60-1.10 in cross-model API costs (GPT-5.4 Pro pricing). See [`shared/cross_model_verification.md`](../shared/cross_model_verification.md) for the detailed breakdown.

### No API key? No problem

Without `ARS_CROSS_MODEL` set, everything works exactly as before. The cross-model features are invisible and add zero overhead.

---

## Installation methods

### Method 1: As project skills (recommended)

Clone this repo into your project's `.claude/skills/` directory:

```bash
cd /path/to/your/project
mkdir -p .claude/skills
git clone https://github.com/Imbad0202/academic-research-skills.git .claude/skills/academic-research-skills
```

Then copy the `.claude/CLAUDE.md` content into your project's `.claude/CLAUDE.md` (merge with existing if you have one).

> **Global installation:** To make skills available across all your projects, install to `~/.claude/skills/` instead:
>
> ```bash
> mkdir -p ~/.claude/skills
> git clone https://github.com/Imbad0202/academic-research-skills.git ~/.claude/skills/academic-research-skills
> ```

### Method 2: As a standalone project

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
4. For Method 1: move the extracted folder to `.claude/skills/academic-research-skills` inside your project
5. For standalone use: open a terminal in the extracted folder and run `claude`

</details>

### Method 3: Claude Cowork (desktop)

Use these skills in [Claude Cowork](https://claude.com/product/cowork) — Claude Desktop's agentic workspace.

**Option A: folder access (quickest)**

1. Clone this repo locally:
   ```bash
   git clone https://github.com/Imbad0202/academic-research-skills.git ~/academic-research-skills
   ```
2. Open Claude Desktop → click **Cowork** tab (top bar)
3. Select the cloned `academic-research-skills` folder as the working directory
4. Claude will auto-detect the skills from `SKILL.md` files and load them as needed

**Option B: as project skills**

If you already have a project folder in Cowork:

```bash
cd /path/to/your/project
mkdir -p .claude/skills
git clone https://github.com/Imbad0202/academic-research-skills.git .claude/skills/academic-research-skills
```

Skills auto-load when relevant — e.g., saying "help me write a paper" triggers `academic-paper`.

**Requirements:** Claude Desktop (latest version) with Cowork enabled; paid plan (Pro, Max, Team, or Enterprise).

### Method 4: Use with claude.ai (web)

You can use these skills on [claude.ai](https://claude.ai) via the **Project** feature with GitHub integration — no Claude Code installation needed.

1. Sign in to [claude.ai](https://claude.ai) (requires a paid plan)
2. Create a new Project: **Projects** → **Create Project**
3. Import from GitHub: in the Project, click **Files** → **+** → **GitHub** → select `Imbad0202/academic-research-skills`

   **Recommended selections** (to stay within capacity):

   | Select | Directory | Why |
   |---|---|---|
   | ✅ | `.claude/` | Routing rules |
   | ✅ | `deep-research/` | Core skill |
   | ✅ | `academic-paper/` | Core skill |
   | ✅ | `academic-paper-reviewer/` | Core skill |
   | ✅ | `academic-pipeline/` | Core skill |
   | ✅ | `shared/` | Cross-model verification, handoff schemas |
   | ✅ | `MODE_REGISTRY.md` | Mode definitions |
   | ❌ | `examples/` | Takes ~39% capacity — skip unless you have room |
   | ❌ | `.github/`, READMEs, LICENSE, etc. | Not needed for functionality |

4. (Optional) Set **Instructions** in the Project to the content of `.claude/CLAUDE.md` for better routing
5. Start chatting: "Guide my research on X" or "Help me write a paper about Y"

**claude.ai vs Claude Code:**

- claude.ai does not support parallel multi-agent execution or shell commands; results may be less comprehensive than Claude Code
- Cross-model verification (`ARS_CROSS_MODEL`) requires Claude Code with API keys
- Direct `.docx` generation requires Pandoc, and LaTeX/PDF output requires Claude Code with `tectonic`; claude.ai can still produce Markdown and DOCX conversion instructions
