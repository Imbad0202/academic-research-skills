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

Claude discovers skills at `<install-root>/<skill-name>/SKILL.md`. This repo contains four separate skills, each with its own `SKILL.md`:

- `deep-research`
- `academic-paper`
- `academic-paper-reviewer`
- `academic-pipeline`

Do not install the whole repository as one nested skill folder under `.claude/skills/academic-research-skills/`; that buries the four `SKILL.md` files one level too deep for discovery. See Anthropic's [Claude Code Skills documentation](https://code.claude.com/docs/en/skills).

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
```

Expected path shape:

```text
/path/to/your/project/.claude/skills/deep-research/SKILL.md
/path/to/your/project/.claude/skills/academic-paper/SKILL.md
/path/to/your/project/.claude/skills/academic-paper-reviewer/SKILL.md
/path/to/your/project/.claude/skills/academic-pipeline/SKILL.md
```

Then copy the `.claude/CLAUDE.md` content into your project's `.claude/CLAUDE.md` (merge with existing if you have one).

> **Global Claude Code installation:** To make these skills available across your Claude Code projects, install the four folders to `~/.claude/skills/` instead:
>
> ```bash
> git clone https://github.com/Imbad0202/academic-research-skills.git ~/academic-research-skills
>
> mkdir -p ~/.claude/skills
> cp -R ~/academic-research-skills/deep-research ~/.claude/skills/deep-research
> cp -R ~/academic-research-skills/academic-paper ~/.claude/skills/academic-paper
> cp -R ~/academic-research-skills/academic-paper-reviewer ~/.claude/skills/academic-paper-reviewer
> cp -R ~/academic-research-skills/academic-pipeline ~/.claude/skills/academic-pipeline
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
4. For Method 1: copy the four extracted skill folders (`deep-research`, `academic-paper`, `academic-paper-reviewer`, `academic-pipeline`) into `.claude/skills/` inside your project
5. For standalone use: open a terminal in the extracted folder and run `claude`

</details>

### Method 3: Claude Cowork (desktop)

Use this when you want the four ARS skills available in [Claude Cowork](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork), Claude Desktop's agentic workspace.

Cowork uses the same skill folder shape: `~/.claude/skills/<skill-name>/SKILL.md`.

#### Prerequisites

- Claude Desktop latest version on macOS or Windows. Download from Anthropic's [Claude Desktop page](https://claude.ai/download).
- Active internet connection; Cowork tasks call the Anthropic API.
- Keep Claude Desktop open while Cowork tasks run. Cowork runs inside the Desktop process.
- Folder/file permissions that allow Cowork to read and write in the project folder.
- A paid plan with Cowork access. See Anthropic's [Cowork requirements](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork) for current plan availability.
- On Team or Enterprise plans, your organization admin may have disabled Skills, plugins, connectors, or egress. If installed skills do not register after restart, ask your admin to check org-level controls.

#### Option A: symlink install (fastest, single-machine)

Use symlinks if you work on one machine and want updates by pulling the repo.

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git ~/academic-research-skills

mkdir -p ~/.claude/skills
cd ~/.claude/skills
ln -s ~/academic-research-skills/deep-research deep-research
ln -s ~/academic-research-skills/academic-paper academic-paper
ln -s ~/academic-research-skills/academic-paper-reviewer academic-paper-reviewer
ln -s ~/academic-research-skills/academic-pipeline academic-pipeline
```

Expected path shape:

```text
~/.claude/skills/deep-research/SKILL.md
~/.claude/skills/academic-paper/SKILL.md
~/.claude/skills/academic-paper-reviewer/SKILL.md
~/.claude/skills/academic-pipeline/SKILL.md
```

If you sync `~/.claude/skills` across machines via a cloud folder, use Option B instead. Absolute-path symlinks can break on a fresh checkout or another machine.

#### Option B: copy install (cross-machine safe, no auto-update)

Use copies if you sync `~/.claude/skills` across machines or do not want symlinks. Updates require re-running the four `cp -R` commands.

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git ~/academic-research-skills

mkdir -p ~/.claude/skills
cp -R ~/academic-research-skills/deep-research ~/.claude/skills/deep-research
cp -R ~/academic-research-skills/academic-paper ~/.claude/skills/academic-paper
cp -R ~/academic-research-skills/academic-paper-reviewer ~/.claude/skills/academic-paper-reviewer
cp -R ~/academic-research-skills/academic-pipeline ~/.claude/skills/academic-pipeline
```

Expected path shape:

```text
~/.claude/skills/deep-research/SKILL.md
~/.claude/skills/academic-paper/SKILL.md
~/.claude/skills/academic-paper-reviewer/SKILL.md
~/.claude/skills/academic-pipeline/SKILL.md
```

#### Create or open a Cowork Project

See Anthropic's [Organize your tasks with Projects in Claude Cowork](https://support.claude.com/en/articles/14116274-organize-your-tasks-with-projects-in-claude-cowork) for the canonical UI walk-through.

1. Open Claude Desktop.
2. Use the mode selector (**Chat / Cowork**) and switch to **Cowork**.
3. In **Tasks**, use the left navigation panel and choose **Use an existing folder**.
4. Select the local folder you want Cowork to work in. This creates a Cowork Project pointing at that folder.
5. Restart Cowork after installing or updating the skill folders so the four skills register.

#### How Cowork invokes the skills

Claude uses each skill's `description` to judge relevance, as described in Anthropic's [Skills documentation](https://code.claude.com/docs/en/skills). Example phrases such as "help me write a paper" are illustrative, not literal trigger phrases; paraphrased intent works too.

If description-based routing does not select the skill you want, Cowork also provides explicit UI surfaces described in Anthropic's [Cowork plugins documentation](https://support.claude.com/en/articles/13837440-use-plugins-in-claude-cowork):

- Type `/` in a Cowork Task to use the command palette and select an available skill.
- Use the `+` capability picker to add a skill to the current Task.

### Method 4: Use with claude.ai (web)

claude.ai has two different ways to use this repository. They are not equivalent:

- **Method 4a** uploads real Custom Skills. This is the standard claude.ai Skill install path, with auto-loading and skill routing.
- **Method 4b** adds repository files to Project knowledge through GitHub integration. This is fallback knowledge mode, not a Skill install.

#### Prerequisites

- A paid claude.ai plan. See Anthropic's current plan information at [claude.ai](https://claude.ai).
- For Method 4a, no GitHub authentication is needed. You zip each skill folder locally and upload one zip per skill through **Settings** → **Capabilities** → **Skills**. Zip structure errors and the 200-character `description` cap surface as upload-time errors; see Anthropic's [Custom Skills packaging documentation](https://claude.com/docs/skills/how-to).
- For Method 4b, GitHub authentication is required through the Anthropic connector. See [Using the GitHub integration](https://support.claude.com/en/articles/10167454-using-the-github-integration) and [Set up Claude integrations](https://support.claude.com/en/articles/10168395-set-up-claude-integrations). Private repositories require the Anthropic GitHub App to be authorized on the repo or organization. Team and Enterprise plans require owner-level connector enablement before users can add GitHub-sourced files.

#### Method 4a: Custom Skill upload (claude.ai's standard Skill install path)

This is the real Skill install path for claude.ai. Upload one zip per skill via **Settings** → **Capabilities** → **Skills**.

Each zip must have the skill folder as its top-level entry, so the zip contains `<skill-name>/SKILL.md`, not `<skill-name>/<skill-name>/SKILL.md`.

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git
cd academic-research-skills

zip -r deep-research.zip deep-research
zip -r academic-paper.zip academic-paper
zip -r academic-paper-reviewer.zip academic-paper-reviewer
zip -r academic-pipeline.zip academic-pipeline
```

Then upload:

1. Sign in to [claude.ai](https://claude.ai).
2. Open **Settings**.
3. Open **Capabilities**.
4. Open **Skills**.
5. Upload `deep-research.zip`.
6. Upload `academic-paper.zip`.
7. Upload `academic-paper-reviewer.zip`.
8. Upload `academic-pipeline.zip`.

Current blocker in v3.6.5.1: the four skill `description` fields in this repo currently exceed the 200-character cap and would be rejected by the upload UI. The description trim ships in a follow-up patch (v3.6.5.2). This path is documented here so the install instructions are correct in advance; until v3.6.5.2 ships, prefer Method 1, Method 2, or Method 3.

#### Method 4b: Project + GitHub integration (fallback knowledge mode, not a Skill install)

claude.ai Projects deliver content as static knowledge for Claude to retrieve and cite — see Anthropic's [What are Projects?](https://support.claude.com/en/articles/9517075-what-are-projects). This is NOT a Skill install. Skill auto-loading does not happen. Trigger phrases do not route. Claude can read the repo content but does not execute the skills as agentic workflows.

Use this when you want claude.ai to have access to the repo content for reading/citation, but you do not need agentic skill execution.

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
   | ✅ | `shared/` | Cross-model verification, handoff schemas, shared protocols |
   | ✅ | `scripts/` | `literature_corpus[]` adapters (`folder_scan`, `zotero`, `obsidian`) + schema validators; required for Material Passport corpus mode and CI-style validation |
   | ✅ | `MODE_REGISTRY.md` | Mode definitions |
   | Optional | `.claude/` | Project-level routing rules. Skip if you set Project Instructions in step 5 below (recommended path); include only if you prefer to keep routing rules visible as Project files. |
   | Optional | `examples/` | Useful for reference examples; skip if you want a smaller Project knowledge set |
   | Optional | `.github/`, READMEs, LICENSE, etc. | Repository metadata; not needed for core reading context |

5. (Recommended) Set **Instructions** in the Project to the content of `.claude/CLAUDE.md` for better routing.
6. Start chatting: "Guide my research on X" or "Help me write a paper about Y".

Anthropic's current [Project file limits](https://support.claude.com/en/articles/8241126-upload-files-to-claude) state that Project file count is not artificially capped at 200; files have a 30 MB per-file limit and total usable content is still subject to context-window limits at runtime. Keep the Project focused so Claude retrieves the relevant files reliably.

**claude.ai vs Claude Code:**

- Method 4b is for content reading, not active Skill execution. If you need agentic skill execution, prefer Method 1, Method 2, Method 3, or Method 4a after v3.6.5.2.
- claude.ai does not support local shell commands; results may be less comprehensive than Claude Code workflows that rely on local scripts.
- Cross-model verification (`ARS_CROSS_MODEL`) requires Claude Code with API keys.
- Direct `.docx` generation requires Pandoc, and LaTeX/PDF output requires Claude Code with `tectonic`; claude.ai can still produce Markdown and DOCX conversion instructions.