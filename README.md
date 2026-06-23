<div align="center">

# 🪽 Academic Research Skills for Hermes

![Hermes Agent](https://img.shields.io/badge/Hermes-Agent-7C3AED?style=for-the-badge)
![Academic Research](https://img.shields.io/badge/Academic-Research-2563EB?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-CC_BY--NC_4.0-lightgrey?style=for-the-badge&logo=creativecommons)

**Hermes Agent skills for academic research, paper writing, peer review, and publication workflows.**

<a href="https://maximosovsky.github.io/academic-research-skills/">Docs</a> ·
<a href="https://github.com/maximosovsky/academic-research-skills/releases/tag/v0.1.2-hermes">Release</a> ·
<a href="https://github.com/Imbad0202/academic-research-skills">Upstream</a> ·
<a href="HERMES.md">Hermes Notes</a>

</div>

> A Hermes-native adaptation layer for Academic Research Skills: deep research, manuscript writing, simulated peer review, revision roadmaps, and research-to-publication pipelines.

<div align="center">
  <img src="readme-cover.jpg" width="600" alt="Academic Research Skills for Hermes preview">
  <br><br>
  <a href="#-quick-start">Quick Start</a> ·
  <a href="#-features">Features</a> ·
  <a href="#-skills">Skills</a> ·
  <a href="#-tech-stack">Tech Stack</a> ·
  <a href="#-roadmap">Roadmap</a>
</div>

---

## 💡 Concept

This fork keeps the original Claude Code project intact while adding a dedicated `hermes/` layer for **Hermes Agent** users. The goal is simple: use Hermes tools such as `read_file`, `terminal`, `web`, `delegate_task`, and `todo` to run serious academic workflows from local manuscripts, PDFs, folders of notes, and GitHub repositories.

The adaptation is especially useful for completed preprints and manuscript projects that need editor-style diagnosis, simulated peer review, claim-support audits, revision roadmaps, journal-fit checks, and final submission preparation.

> [!NOTE]
> This is a fork of [Academic Research Skills for Claude Code](https://github.com/Imbad0202/academic-research-skills) by Cheng-I Wu. The upstream license is preserved: **CC BY-NC 4.0**.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔎 Deep Research | Research-question shaping, literature review, systematic-review planning, source reliability, and fact-checking. |
| 📝 Academic Paper | Paper planning, outlining, drafting, revision, formatting, and disclosure/declaration checks. |
| 🧑‍⚖️ Peer Review | Simulated editor + reviewer panels, devil's advocate critique, editorial decision, and revision roadmap. |
| 🚀 Academic Pipeline | End-to-end orchestration: research → write → integrity → review → revise → finalize. |
| 📚 Manuscript Genre Discipline | Conceptual, methodological, netnographic, and sport-pedagogy papers are judged by genre-appropriate standards. |
| 🧰 Hermes Tooling | Local installer, skill validator, PDF extraction helper, raw URL installer, templates, protocols, and examples. |
| 🌐 Docs Site | GitHub Pages guide with usage, per-skill overview, and examples. |

---

## 🚀 Quick Start

```bash
git clone -b hermes-adaptation https://github.com/maximosovsky/academic-research-skills.git
cd academic-research-skills
python hermes/scripts/validate-skills.py
bash hermes/scripts/install-local.sh all
```

Then start a fresh Hermes session or run:

```text
/reload-skills
```

<details>
<summary>Install selected skills only</summary>

```bash
bash hermes/scripts/install-local.sh reviewer pipeline
bash hermes/scripts/install-local.sh deep-research paper
```

</details>

<details>
<summary>Install with direct raw URLs</summary>

```bash
python hermes/scripts/install-urls.py
```

Example:

```bash
hermes skills install https://raw.githubusercontent.com/maximosovsky/academic-research-skills/hermes-adaptation/hermes/skills/hermes-academic-reviewer/SKILL.md --name hermes-academic-reviewer
```

Local clone installation is preferred because it also copies `references/` and `templates/`.

</details>

---

## 🧩 Skills

| Skill | Use for |
|---|---|
| `hermes-academic-deep-research` | Literature review, systematic-review planning, source discovery, fact-checking, evidence synthesis, claim verification. |
| `hermes-academic-paper` | Paper plan, outline, abstract, draft, revision, formatting, disclosure, submission package preparation. |
| `hermes-academic-reviewer` | Full peer-review simulation: Editor + 3 reviewers + Devil's Advocate + editorial decision + roadmap. |
| `hermes-academic-pipeline` | Complete research-to-publication workflow with staged integrity checks and checkpoints. |

Example in Hermes:

```text
/skill hermes-academic-reviewer
Полная peer-review имитация Editor + 3 reviewers + devil's advocate + editorial decision для этого PDF.
```

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Agent runtime | Hermes Agent |
| Skill format | Hermes `SKILL.md` |
| Validation | Python + PyYAML |
| Manuscript extraction | PyMuPDF helper script |
| Documentation | GitHub Pages static HTML |
| Upstream base | Academic Research Skills for Claude Code |
| License | CC BY-NC 4.0 preserved from upstream |

<details>
<summary>📁 Project Structure</summary>

```text
academic-research-skills/
├── README.md                 # Hermes-facing landing page
├── README.upstream.md        # Original upstream README
├── HERMES.md                 # Hermes adaptation notes
├── llms.txt                  # Short LLM discovery card
├── llms-full.txt             # Full LLM reference
├── hermes/
│   ├── README.md
│   ├── RELEASE_NOTES.md
│   ├── examples/
│   ├── scripts/
│   │   ├── install-local.sh
│   │   ├── validate-skills.py
│   │   ├── extract-pdf.py
│   │   └── install-urls.py
│   └── skills/
│       ├── hermes-academic-deep-research/
│       ├── hermes-academic-paper/
│       ├── hermes-academic-reviewer/
│       └── hermes-academic-pipeline/
└── docs/                     # GitHub Pages site
```

</details>

---

## 🗺️ Roadmap

- [x] Fork upstream while preserving CC BY-NC 4.0.
- [x] Add Hermes-native skill layer.
- [x] Add local installer and validator.
- [x] Add references, templates, examples, and helper scripts.
- [x] Publish `v0.1.2-hermes` release.
- [x] Add GitHub Pages documentation.
- [x] Open upstream PR with optional Hermes layer.
- [ ] Add more manuscript-specific examples.
- [ ] Add richer citation-audit automation.
- [ ] Package for Hermes skills registry / tap workflow if desired.

---

## 🤝 Contributing

Fork → `feature/name` → PR.

For upstream Claude Code functionality, contribute to the original project. For Hermes-specific workflows, target the `hermes-adaptation` branch and keep changes under `hermes/`, `docs/hermes/`, or the Hermes CI workflow unless there is a clear reason to touch upstream files.

---

## 📄 License

[Maxim Osovsky](https://www.linkedin.com/in/osovsky/). This fork preserves the upstream [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) license from Academic Research Skills by Cheng-I Wu.
