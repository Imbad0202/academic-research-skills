# Academic Research Skills for Claude Code

[![Version](https://img.shields.io/badge/version-v3.7.0-blue)](https://github.com/Imbad0202/academic-research-skills/releases/tag/v3.7.0)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/license-CC%20BY--NC%204.0-lightgrey)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Sponsor](https://img.shields.io/badge/sponsor-Buy%20Me%20a%20Coffee-orange?logo=buy-me-a-coffee)](https://buymeacoffee.com/crucify020v)

[繁體中文版](README.zh-TW.md)

A comprehensive suite of Claude Code skills for academic research, covering the full pipeline from research to publication.

**Install in 30 seconds** (Claude Code CLI / VS Code / JetBrains, v3.7.0+):

```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

Then try `/ars-plan` to walk through your paper structure via Socratic dialogue, or jump to [Quick install](#quick-install) for prerequisites and the traditional symlink flow.

> **AI is your copilot, not the pilot.** This tool won't write your paper for you. It handles the grunt work — hunting down references, formatting citations, verifying data, checking logical consistency — so you can focus on the parts that actually require your brain: defining the question, choosing the method, interpreting what the data means, and writing the sentence after "I argue that."
>
> Unlike a humanizer, this tool doesn't help you hide the fact that you used AI. It helps you write better. Style Calibration learns your voice from past work. Writing Quality Check catches the patterns that make prose feel machine-generated. The goal is quality, not cheating.

### Why human-in-the-loop, not full automation?

Lu et al. (2026, *Nature* 651:914-919) built **The AI Scientist** — the first fully autonomous AI research system to publish a paper through blind peer review at a top-tier ML venue (ICLR 2025 workshop, score 6.33/10 vs workshop average 4.87). Their Limitations section enumerates the failure modes that any fully-autonomous AI research pipeline inherits: implementation bugs, hallucinated results, shortcut reliance, bug-as-insight reframing, methodology fabrication, frame-lock, citation hallucinations.

ARS is built on the premise that **a human researcher augmented by AI avoids these failure modes better than either alone**. Stage 2.5 and Stage 4.5 integrity gates run a 7-mode blocking checklist (see [`academic-pipeline/references/ai_research_failure_modes.md`](academic-pipeline/references/ai_research_failure_modes.md)); the reviewer offers an opt-in calibration mode that measures its own FNR/FPR against a user-supplied gold set.

v3.3 was inspired by [**PaperOrchestra**](https://arxiv.org/abs/2604.05018) (Song, Song, Pfister & Yoon, 2026, Google): Semantic Scholar API verification, anti-leakage protocol, VLM figure verification, and score trajectory tracking.

---

## Architecture & pipeline

**👉 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — the full pipeline view: flow diagram, stage-by-stage matrix, data-access flow, skill dependency graph, quality gates, and mode list.

The architecture doc supersedes the sprawling pipeline description that used to live here. Everything about *what runs in which stage* now lives in one place.

## Quick install

**Prerequisites**

- [Claude Code](https://claude.ai/install.sh) (latest; plugin packaging requires recent versions)
- `ANTHROPIC_API_KEY` exported, or set on first `claude` run
- *Optional:* Pandoc for DOCX, tectonic + Source Han Serif TC for APA 7.0 PDF (Markdown output works without either)

**Plugin install (v3.7.0+, recommended):**

```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

**Verify it works:** run `/ars-plan` and describe a paper you're working on — ARS will start a Socratic dialogue to map out chapter structure. For a single-shot test instead, try `/ars-lit-review "your topic"`.

**👉 [docs/SETUP.md](docs/SETUP.md)** — full guide: install Claude Code, set up API keys, optional Pandoc/tectonic for DOCX/PDF, cross-model verification (`ARS_CROSS_MODEL`), and five installation methods (Plugin, project skills, global skills, claude.ai Project, repo-cloned).

## Performance & cost

**👉 [docs/PERFORMANCE.md](docs/PERFORMANCE.md)** — per-mode token budgets, full-pipeline estimate (~$4–6 for a 15k-word paper), and recommended Claude Code settings (Skip Permissions; Agent Team optional).

## Guides & articles

- [Academic Writing Shouldn't Be a Solo Act](https://open.substack.com/pub/edwardwu223235/p/academic-writing-shouldnt-be-a-solo?r=4dczl&utm_medium=ios) — full pipeline walkthrough (English)
- [學術寫作不該是一個人的事：一套開源 AI 協作工具如何改變研究者的工作流](https://open.substack.com/pub/edwardwu223235/p/ai?r=4dczl&utm_medium=ios) — 完整使用指南（繁體中文）

---

## Features at a glance

- **Deep Research** — 13-agent research team with Socratic guided mode, PRISMA systematic review, intent detection, dialogue health monitoring, optional cross-model DA, Semantic Scholar API verification.
- **Academic Paper** — 12-agent paper writing with Style Calibration, Writing Quality Check, LaTeX hardening, visualization, revision coaching, citation conversion, anti-leakage protocol, and VLM figure verification.
- **Academic Paper Reviewer** — 7-agent multi-perspective peer review with 0–100 quality rubrics (EIC + 3 dynamic reviewers + Devil's Advocate), concession threshold protocol, attack intensity preservation, optional cross-model DA critique / calibration, R&R traceability matrix, read-only constraint.
- **Academic Pipeline** — 10-stage pipeline orchestrator with adaptive checkpoints, claim verification, Material Passport, optional `repro_lock`, optional cross-model integrity verification, mid-conversation reinforcement, and score trajectory tracking.
- **Data Access Level Metadata** (v3.3.2+) — every skill declares `data_access_level` (`raw` / `redacted` / `verified_only`); enforced by `scripts/check_data_access_level.py`. Pattern adapted from Anthropic's automated-w2s-researcher (2026). See [`shared/ground_truth_isolation_pattern.md`](shared/ground_truth_isolation_pattern.md).
- **Task Type Annotation** (v3.3.2+) — every skill declares `task_type` (`open-ended` or `outcome-gradable`). All current ARS skills are `open-ended`.
- **Benchmark Report Schema** (v3.3.5+) — JSON Schema + lint for honest benchmark comparisons. See [`shared/benchmark_report_pattern.md`](shared/benchmark_report_pattern.md).
- **Artifact Reproducibility Lockfile** (v3.3.5+) — optional `repro_lock` sub-block on Material Passport. **Configuration documentation, not replay guarantee** — LLM outputs are not byte-reproducible. See [`shared/artifact_reproducibility_pattern.md`](shared/artifact_reproducibility_pattern.md).

---

## Showcase: real pipeline output

See the complete artifacts from a real 10-stage pipeline run — peer review reports, integrity verification reports, and the final paper:

**[Browse all pipeline artifacts →](examples/showcase/)**

| Artifact | Description |
|---|---|
| [Final Paper (EN)](examples/showcase/full_paper_apa7.pdf) | APA 7.0 formatted, LaTeX-compiled |
| [Final Paper (ZH)](examples/showcase/full_paper_zh_apa7.pdf) | Chinese version, APA 7.0 |
| [Integrity Report — Pre-Review](examples/showcase/integrity_report_stage2.5.pdf) | Stage 2.5: caught 15 fabricated refs + 3 statistical errors |
| [Integrity Report — Final](examples/showcase/integrity_report_stage4.5.pdf) | Stage 4.5: zero regressions confirmed |
| [Peer Review Round 1](examples/showcase/stage3_review_report.pdf) | EIC + 3 Reviewers + Devil's Advocate |
| [Re-Review](examples/showcase/stage3prime_rereview_report.pdf) | Verification after revisions |
| [Peer Review Round 2](examples/showcase/stage3_review_report_r2.pdf) | Follow-up review |
| [Response to Reviewers](examples/showcase/response_to_reviewers_r2.pdf) | Point-by-point author response |
| [Post-Publication Audit Report](examples/showcase/post_publication_audit_2026-03-09.pdf) | Independent full-reference audit: found 21/68 issues missed by 3 rounds of integrity checks |

---

## Companion: Experiment Agent

If your research involves running experiments (code or human studies) before writing, the [Experiment Agent](https://github.com/Imbad0202/experiment-agent) skill fills the gap between ARS Stage 1 (RESEARCH) and Stage 2 (WRITE).

```
ARS Stage 1 RESEARCH  →  RQ Brief + Methodology Blueprint
        ↓
  experiment-agent     →  run/manage experiments → validate results
        ↓
ARS Stage 2 WRITE     →  write paper with verified experiment results
```

**What it does**: executes code experiments (Python, R, etc.) with real-time monitoring, manages human study protocols with IRB ethics checklist, interprets statistics with 11-type fallacy detection, and verifies reproducibility.

**How to use together**: pause the ARS pipeline after Stage 1, run experiments in a separate experiment-agent session, then bring the results (with Material Passport) back to ARS Stage 2. ARS requires zero modification. See the [experiment-agent README](https://github.com/Imbad0202/experiment-agent) for setup instructions.

---

## Usage

### Quick Start

```
# Start a full research pipeline
You: "I want to write a research paper on AI's impact on higher education QA"

# Start with Socratic guidance
You: "Guide my research on AI in educational evaluation"

# Write a paper with guided planning
You: "Guide me through writing a paper on demographic decline"

# Review an existing paper
You: "Review this paper" (then provide the paper)

# Check pipeline status
You: "status"
```

### Individual Skills

#### Deep Research (7 modes)

```
"Research the impact of AI on higher education"       → full mode
"Give me a quick brief on X"                          → quick mode
"Do a systematic review on X with PRISMA"             → systematic-review mode
"Guide my research on X"                              → socratic mode (guided)
"Fact-check these claims"                             → fact-check mode
"Do a literature review on X"                         → lit-review mode
"Review this paper's research quality"                → review mode
```

#### Academic Paper (10 modes)

```
"Write a paper on X"                                  → full mode
"Guide me through writing a paper"                    → plan mode (guided)
"Build a paper outline"                               → outline-only mode
"I have a draft, here are reviewer comments"          → revision mode
"Parse these reviewer comments into a roadmap"        → revision-coach mode
"Write an abstract for this paper"                    → abstract-only mode
"Turn this into a literature review paper"            → lit-review mode
"Convert to LaTeX" / "Convert citations to IEEE"      → format-convert mode
"Check citations"                                     → citation-check mode
"Generate an AI disclosure statement for NeurIPS"     → disclosure mode
```

#### Academic Paper Reviewer (6 modes)

```
"Review this paper"                                   → full mode (EIC + R1/R2/R3 + Devil's Advocate)
"Quick assessment of this paper"                      → quick mode
"Guide me to improve this paper"                      → guided mode
"Check the methodology"                               → methodology-focus mode
"Verify the revisions"                                → re-review mode
"Calibrate this reviewer against my gold set"         → calibration mode
```

#### Academic Pipeline (Orchestrator)

```
"I want to write a complete research paper"           → full pipeline from Stage 1
"I already have a paper, review it"                   → mid-entry at Stage 2.5 (integrity first)
"I received reviewer comments"                        → mid-entry at Stage 4
```

> Pipeline ends with **Stage 6: Process Summary** — auto-generates a paper creation process record with 6-dimension Collaboration Quality Evaluation (1–100 scoring).

### Supported Languages

- **Traditional Chinese** (繁體中文) — default when user writes in Chinese
- **English** — default when user writes in English
- Bilingual abstracts (Chinese + English) for academic papers

> **Using a different language?** Socratic mode (deep-research) and Plan mode (academic-paper) use **intent-based activation** — they detect the meaning of your request, not specific keywords. This means they work in **any language** without modification.
>
> However, the general `Trigger Keywords` section (which determines whether the skill is activated at all) still lists English and Traditional Chinese keywords. If you find the skill isn't activating reliably in your language, you can add your language's keywords to the `### Trigger Keywords` section in each `SKILL.md` file to improve matching confidence.

### Supported Citation Formats

- APA 7.0 (default, including Chinese citation rules)
- Chicago (Notes & Author-Date)
- MLA
- IEEE
- Vancouver

### Supported Paper Structures

- IMRaD (empirical research)
- Thematic Literature Review
- Theoretical Analysis
- Case Study
- Policy Brief
- Conference Paper

---

## Skill Details

Per-agent responsibilities and per-stage artifacts now live in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). Version numbers are anchored here so release metadata stays in one place.

### Deep Research (v2.8)

13-agent research team. Modes: full, quick, review, lit-review, fact-check, socratic, systematic-review. Full agent roster and artifacts: see ARCHITECTURE.md §3.

### Academic Paper (v3.0)

12-agent paper writing pipeline. Modes: full, plan, outline-only, revision, revision-coach, abstract-only, lit-review, format-convert, citation-check, disclosure. Output: MD + DOCX (via Pandoc when available) + LaTeX (APA 7.0 `apa7` class / IEEE / Chicago) → PDF via tectonic. Full agent roster and per-phase responsibilities: see ARCHITECTURE.md §3.

### Academic Paper Reviewer (v1.8)

7-agent multi-perspective review with **0-100 quality rubrics**. Modes: full, re-review, quick, methodology-focus, guided, calibration. **Decision mapping:** ≥80 Accept, 65-79 Minor Revision, 50-64 Major Revision, <50 Reject. First-round review team vs. narrow re-review team boundary: see ARCHITECTURE.md §3 Stage 3 / Stage 3'.

### Academic Pipeline (v3.7)

10-stage orchestrator with integrity verification, two-stage review, Socratic coaching, and collaboration evaluation. Pipeline guarantees: every stage requires user confirmation checkpoint; integrity verification (Stage 2.5 + 4.5) cannot be skipped; R&R Traceability Matrix (Schema 11) independently verifies author revision claims. v3.4 added the Compliance Agent (PRISMA-trAIce + RAISE) at Stage 2.5 / 4.5. v3.5 adds the **Collaboration Depth Observer** (`collaboration_depth_agent`, advisory only — never blocks) at every FULL/SLIM checkpoint and at pipeline completion. MANDATORY integrity gates (2.5 / 4.5) explicitly skip the observer so compliance checks are not diluted. Based on Wang & Zhang (2026), IJETHE 23:11. Stage-by-stage matrix with agents, artifacts, and gates: see ARCHITECTURE.md §3.

---

## v3.0 Optimizations: What We Discovered About AI's Structural Limits

### What happened

While using ARS to write a reflection article about AI in higher education, I ran into three structural problems that no amount of prompt engineering could fix:

1. **Frame-lock**: I asked the AI to run a devil's advocate debate against its own thesis. It did — four rounds, each more refined than the last. But every round stayed inside the frame I'd set. The DA attacked arguments, never premises. It never asked "are we even discussing the right question?" This is the same pattern that caused the 31% citation error rate in v2.7's stress test: the verifying AI and the generating AI share the same cognitive frame.

2. **Sycophancy under pushback**: Every time I challenged the DA's attacks, it conceded too quickly. It retracted findings faster than it launched them. The model's training rewards conversational harmony — so "the user pushed back" was treated as evidence that the attack was wrong, when often it just meant the user was persistent.

3. **Intent misdetection**: The Socratic Mentor kept trying to converge and produce deliverables ("Want me to write this up?") when I was still exploring. It couldn't distinguish "the user wants a deep philosophical discussion" from "the user wants an RQ brief." Both look like engagement, but they need opposite AI behaviors.

### What we changed (v3.0)

**Devil's Advocate — Concession Threshold Protocol** (`deep-research` + `academic-paper-reviewer`)
- DA must now score every rebuttal on a 1-5 scale before responding
- Concession only allowed at score ≥4 (rebuttal directly addresses core attack with evidence)
- Score ≤3: hold position and restate the original attack
- Anti-sycophancy rules: no consecutive concessions, concession rate tracking, frame-lock detection after each checkpoint

**Socratic Mentor — Intent Detection Layer** (`deep-research`)
- Classifies user intent as exploratory vs. goal-oriented at dialogue start and every 3 turns
- Exploratory mode: disables auto-convergence, raises max rounds to 60, prohibits "want me to summarize?" prompts
- Goal-oriented mode: standard convergence behavior
- Anti-premature-closure rules: in exploratory mode, the user decides when to stop

**Socratic Mentor — Dialogue Health Indicator** (`deep-research`)
- Silent self-assessment every 5 turns on three dimensions: persistent agreement, conflict avoidance, premature convergence
- Auto-injects challenging questions when agreement pattern detected
- Invisible to user (to prevent gaming), but log available for post-session review

### Why this matters

These optimizations don't solve AI's structural limits — they make the limits visible and manageable. The DA will still eventually concede if pushed hard enough. The Socratic Mentor will still have some convergence bias. But now there are explicit checkpoints that slow down the sycophancy, force the DA to justify concessions, and prevent the Mentor from wrapping up before the user is ready.

The deeper lesson: AI literacy isn't about learning to use AI as a tool, following ethics rules, or fearing AI risks. It's about engaging AI deeply enough to discover its structural limits yourself — and your own thinking limits in the process.

---

## License

This work is licensed under [CC-BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).

**You are free to:**
- Share — copy and redistribute the material
- Adapt — remix, transform, and build upon the material

**Under the following terms:**
- **Attribution** — You must give appropriate credit
- **NonCommercial** — You may not use the material for commercial purposes

**Attribution format:**
```
Based on Academic Research Skills by Cheng-I Wu
https://github.com/Imbad0202/academic-research-skills
```

---

## Contributors

**Cheng-I Wu** (吳政宜) — Author and maintainer

**[aspi6246](https://github.com/aspi6246)** — Contributor. The v3.1 optimization was inspired by patterns from [Claude-Code-Skills-for-Academics](https://github.com/aspi6246/Claude-Code-Skills-for-Academics): read-only constraint pattern, anti-pattern codification as first-class design, cognitive framework approach (teaching "how to think" not just procedures), and lean skill size philosophy.

**[mchesbro1](https://github.com/mchesbro1)** — Contributor. Originally proposed and drafted the IS Basket of 8 journals for `academic-paper-reviewer/references/top_journals_by_field.md` ([Issue #5](https://github.com/Imbad0202/academic-research-skills/issues/5)).

**[cloudenochcsis](https://github.com/cloudenochcsis)** — Contributor. Extended the IS section from the *Basket of 8* to the full *Senior Scholars' Basket of 11* — adding *Decision Support Systems*, *Information & Management*, and *Information and Organization* ([Issue #7](https://github.com/Imbad0202/academic-research-skills/issues/7), [PR #8](https://github.com/Imbad0202/academic-research-skills/pull/8)). Sourced from the [AIS Senior Scholars' List of Premier Journals](https://aisnet.org/page/SeniorScholarListofPremierJournals).

---

## Changelog

### v3.7.0 (2026-05-05) — Claude Code Plugin Packaging

> Plugin packaging upgrade: ARS now installs in one line on Claude Code CLI / VS Code / JetBrains via `/plugin marketplace add Imbad0202/academic-research-skills` + `/plugin install academic-research-skills`. The traditional `git clone + symlink to ~/.claude/skills/` flow continues to work — both tracks are first-class.

- **Plugin manifest + marketplace metadata** (Phase 1, PR #68). `.claude-plugin/plugin.json` declares the suite (4 skills auto-discovered from `skills/` directory via relative symlinks). `.claude-plugin/marketplace.json` registers the plugin so a single GitHub-hosted endpoint serves both the marketplace listing and the plugin source. README + `README.zh-TW.md` + `docs/SETUP.md` carry dual-track install instructions.
- **10 slash commands** at `commands/ars-*.md` (Phase 2.1, PR #69) mapping `MODE_REGISTRY.md` entries to `/ars-<mode>` triggers. Model routing is pinned in each command's frontmatter — `opus` for `full` and `revision-coach` (architectural / review-interpretation depth), `sonnet` for the other 8. No Haiku per project policy.
- **3 plugin-shipped agents** at `agents/*_agent.md` (Phase 2.1, PR #69) as relative symlinks to the v3.6.7-hardened downstream agents in `deep-research/agents/`: `synthesis_agent`, `research_architect_agent`, `report_compiler_agent`. Underscore filenames preserved to keep `scripts/check_v3_6_7_pattern_protection.py` hard-pinned paths and INV-3 manifest-confined Clause 1 invariant intact. Symlinks (not copies) preserve a single source of truth and prevent the Pattern C3 attack surface that v3.6.7 §6 inversion sweep + INV-1/2/3 lint closes.
- **`model: inherit`** added to those three source agent frontmatters. Inherit chosen over pinning `sonnet` so an opus session running ARS full pipeline keeps opus agents (instead of being capped). The user's `~/.claude/hooks/warn-agent-no-model.sh` PreToolUse hook gates Haiku at the dispatching boundary, so `inherit` resolves through an already-Haiku-free model.
- **SessionStart announce hook** at `hooks/hooks.json` + `scripts/announce-ars-loaded.sh` (Phase 2.2, PR #70). When the plugin loads, the hook injects an `additionalContext` listing the 10 slash commands, the 3 plugin agents, and a token-budget pointer into the LLM's first turn. `startup` and `clear` source values get the full announce; `resume` and `compact` get a one-line ack to avoid burning context. Bash 3.2 compatible — runs on macOS stock `/bin/bash` with no `brew install bash` requirement.
- **Phase 2.2 scope reduction**: a `SubagentStop → run_codex_audit.sh` codex audit hook was scoped out for v3.7.0 due to a contract gap (the SubagentStop payload carries no stage/deliverable info, so the wrapper would have to half-infer required arguments) and an invoker-class boundary (`run_codex_audit.sh` lines 4–7 forbid same-session in-LLM invocation; PostToolUse fires inside the producing session). Real audit-hook integration deferred to a future release when ARS gains a stage/deliverable propagation contract. See `docs/design/2026-04-30-ars-v3.7.0-plugin-packaging-roadmap.md` Update note 2026-05-05 (Phase 2.2 scope reduction).
- **`docs/PERFORMANCE.md` + `.zh-TW.md`** gain a "v3.7.0 Plugin agents and model routing" subsection explaining the inherit semantics and current 3-agent scope boundary.
- **Codex review chain across the three PRs**: 8 inline iterative rounds + 3 fresh PR-level rounds, all converging to 0 P0/P1/P2 findings before merge. The Phase 2.2 fresh PR review caught one P2 (unquoted `${CLAUDE_PLUGIN_ROOT}` breaking install paths with spaces) that the inline rounds missed — confirms the value of separating implementation review (inline) from contract review (fresh).
- **What did NOT change**: the four skill directories, all 25 modes, agent prompts, schema files, and lint contracts. Plugin packaging only adds new top-level surface (`commands/`, `agents/`, `hooks/`, `.claude-plugin/`, `skills/` symlink dir, three plugin-agent `model: inherit` frontmatter additions). Existing 4.3k clone-install users see no breaking change.

### v3.6.8 (2026-05-03) — Generator-Evaluator Contract Gate (v3.6.6 spec ship)

> Naming note: this release ships the **v3.6.6 generator-evaluator contract** spec
> and implementation. The v3.6.6 work landed after v3.6.7 due to project sequencing;
> the design doc retains the v3.6.6 internal naming for the contract gate version,
> while the suite release is tagged v3.6.8 to keep the CHANGELOG monotonic.

- **Schema 13.1** (`shared/sprint_contract.schema.json`) extends Schema 13 with two new `mode` enum values (`writer_full` + `evaluator_full`), two new optional top-level fields (`pre_commitment_artifacts` writer-only, `disagreement_handling` evaluator-only), and 12 `allOf` branches enforcing reviewer- / writer- / evaluator-conditional gates. Existing reviewer contracts validate byte-equivalent under Schema 13.1 (§3.6 zero-touch promise).
- **Two new shipped contract templates** under `shared/contracts/writer/full.json` (D1–D7, F1/F4/F2/F3/F0) and `shared/contracts/evaluator/full.json` (D1–D5, F1/F2/F3/F6/F4/F5/F0). Promoted from design-time artefacts on the spec branch to live shipped status atomically with the Schema 13.1 upgrade.
- **Two-phase orchestration** inside `academic-paper full`: Phase 4 splits into Phase 4a (writer paper-blind pre-commitment) + Phase 4b (writer paper-visible drafting + self-scoring); Phase 6 splits into Phase 6a (evaluator paper-blind pre-commitment) + Phase 6b (evaluator paper-visible scoring + decision). Phase-numbered `<phase4a_output>` / `<phase6a_output>` data delimiters mirror the v3.6.2 reviewer pattern. Lint count summary: writer 3+4 / evaluator 5+5 / reviewer 5+6 (reviewer remains zero-touch).
- **`academic-paper` SKILL + agent files** gain a verbatim `## v3.6.6 Generator-Evaluator Contract Protocol` block (101 lines in SKILL.md plus 47 lines in `draft_writer_agent.md` + 57 lines in `peer_reviewer_agent.md`). SKILL.md also adds a new `## Known limitations` section carrying graceful-degradation + cross-session resume forward notes for v3.6.7+.
- **Validator extensions**: `scripts/check_sprint_contract.py` SC-* mode-gating audit (SC-5 + SC-11 reviewer-only; SC-9 extended across all three mode families). 17 new tests bring the validator unit-test count from 54 to 71 (positive + 5 schema-branch negative + 2 §3.6 reviewer regression + 6 mode-gating tests).
- **Manifest CI lint**: `scripts/check_v3_6_6_ab_manifest.py` enforces §6.2 manifest schema + §6.5 git-tracked invariants on `tests/fixtures/v3.6.6-ab/manifest.yaml`. `.github/workflows/spec-consistency.yml` extends the sprint contract validation loop to iterate writer + evaluator template directories alongside the existing reviewer loop, plus runs the new manifest CI lint.
- **A/B evidence fixture stub** at `tests/fixtures/v3.6.6-ab/` (30 files): manifest + README + 6 paper-A inputs/baseline + 1 paper-C inputs/baseline + Stage 3 reviewer excerpt + 6 codex-judge baseline placeholders. Real fixture data populates in follow-up commits before the implementation work fully completes.

### v3.6.7 (2026-04-30) — Downstream-Agent Pattern Protection (Step 1+2)

- **Three downstream agents hardened against 13 of 18 documented hallucination/drift patterns**: `synthesis_agent` (A1–A5 narrative-side), the survey-designer mode of `research_architect_agent` (B1–B5 instrument-side), and the abstract-only mode of `report_compiler_agent` (C1–C3 publication-side). Each agent prompt now carries a `PATTERN PROTECTION (v3.6.7)` block.
- **Four reference files in `shared/references/`**: `irb_terminology_glossary.md`, `psychometric_terminology_glossary.md`, `protected_hedging_phrases.md`, `word_count_conventions.md`. The reference files carry operational contracts that the agent prompts cite by path.
- **Cross-model audit prompt template** at `shared/templates/codex_audit_multifile_template.md` with seven audit dimensions and a mandatory three-part Section 4(f) check for `report_compiler_agent` bundles. Failure of any sub-check is a P1 finding.
- **Static lint + 29-test mutation suite**: `scripts/check_v3_6_7_pattern_protection.py` enforces protection-clause presence and obligation-phrase shape; `scripts/test_check_v3_6_7_pattern_protection.py` preserves codex review evidence so future checker regressions surface in CI. Both are wired into `.github/workflows/spec-consistency.yml`.
- **Codex review history**: seven rounds of `gpt-5.5` + `xhigh` cross-model review reached SHIP-OK with zero P1+P2 findings. Step 6 (orchestrator runtime hooks) and Step 8 (synthetic eval case) ship in a follow-up PR.

### v3.6.5 (2026-04-27) — Material Passport `literature_corpus[]` Consumer Integration

- **Two Phase 1 literature consumers** wired: `deep-research/agents/bibliography_agent.md` and `academic-paper/agents/literature_strategist_agent.md`. Both follow the same five-step **corpus-first, search-fills-gap** flow when the passport carries a non-empty `literature_corpus[]` and the same four Iron Rules (Same criteria / No silent skip / No corpus mutation / Graceful fallback on parse failure).
- **PRE-SCREENED reproducibility block** in Search Strategy reports: enumerates included / excluded / skipped corpus entries, with F3 zero-hit note and F4a–F4f provenance reporting that compose around partial declaration of `obtained_via` / `obtained_at`. `final_included = pre_screened_included[] ∪ external_included[]` stays neutral — no provenance tags on bibliography entries or literature matrix rows.
- **Consumer protocol reference** at `academic-pipeline/references/literature_corpus_consumers.md` with the canonical PRE-SCREENED template, BAD/GOOD examples, four Iron Rules, and per-consumer reading instructions.
- **CI lint** `scripts/check_corpus_consumer_protocol.py` enforcing nine protocol invariants with manifest-driven consumer list (`scripts/corpus_consumer_manifest.json`).
- **Schema 9 caveat retired**: `shared/handoff_schemas.md` retired the v3.6.4 "Consumer-side integration deferred to v3.6.5+" caveat; replaced with backpointer to the consumer protocol.
- Presence-based, no schema change, no new env flag. Parse failures fall back to external-DB-only flow with a `[CORPUS PARSE FAILURE]` surface. `citation_compliance_agent` corpus integration deferred to v3.6.6+.
- No breaking changes. Existing user adapters work without modification.

### v3.6.4 (2026-04-25) — Material Passport `literature_corpus[]` Input Port

- **`literature_corpus[]` field** added to Schema 9 as an optional input port for user-owned literature. Each entry conforms to `shared/contracts/passport/literature_corpus_entry.schema.json` (CSL-JSON authors, year, title, source_pointer + private optional `abstract` / `user_notes`).
- **Language-neutral adapter contract** at `academic-pipeline/references/adapters/overview.md`: any program (any language) reading a user corpus source can produce conformant `passport.yaml` + `rejection_log.yaml`. Fail-soft entry-level errors, fail-loud adapter-level errors, deterministic ordering.
- **Three reference Python adapters** under `scripts/adapters/`: `folder_scan.py` (filesystem of PDFs), `zotero.py` (Better BibTeX JSON export), `obsidian.py` (vault frontmatter). Starting points only; users are expected to write their own adapters for non-reference sources.
- **Rejection log contract** at `shared/contracts/passport/rejection_log.schema.json` with closed enum of categorical reason values; always emitted (empty when no rejections).
- **CI gates**: `scripts/check_literature_corpus_schema.py` validates schemas + adapter examples; `scripts/sync_adapter_docs.py --check` prevents schema→docs drift; new `pytest.yml` workflow runs `scripts/adapters/tests/` on path-filtered triggers.
- **Input-port-only at v3.6.4**: v3.6.4 shipped the schema and adapter contract without consumer integration. `bibliography_agent` and `literature_strategist_agent` were wired in v3.6.5.
- No breaking changes.

### v3.6.3 (2026-04-23) — Opt-in Passport Reset Boundary

- **Opt-in passport reset boundary** (`ARS_PASSPORT_RESET=1`). Promotes every FULL checkpoint to a context-reset boundary. New `resume_from_passport=<hash>` mode lets users resume in a fresh Claude Code session from the Material Passport ledger alone. `systematic-review` mode with the flag ON makes reset mandatory at every FULL checkpoint; other modes treat reset as the flag-gated default. Flag OFF preserves pre-v3.6.3 behavior byte-for-byte.
- Schema 9 gains an append-only `reset_boundary[]` ledger with two entry kinds (`kind: boundary` + `kind: resume`). Hash uses JSON Canonical Form + SHA-256 with canonical placeholder for self-reference safety. Optional `pending_decision` handles MANDATORY branch choices.
- New `scripts/check_passport_reset_contract.py` CI lint: every mention of the flag must co-locate a pointer to the authoritative protocol doc.
- Protocol doc: `academic-pipeline/references/passport_as_reset_boundary.md`.
- `docs/PERFORMANCE.md` updated with long-running-session guidance.
- No breaking changes. Flag default is OFF.

### v3.6.2 (2026-04-23) — Reviewer Sprint Contract Hard Gate

v3.6.2 introduces Schema 13 sprint contracts and a hard-gate orchestration that forces reviewers to pre-commit their scoring plan before reading the paper. Reviewer-only first test case; writer/evaluator deferred to v3.6.4. See CHANGELOG.

- **Schema 13 sprint contract** with `panel_size`, `acceptance_dimensions`, `failure_conditions` (with `severity` precedence + panel-relative `cross_reviewer_quantifier`), `measurement_procedure`, optional `override_ladder`, bounded `agent_amendments`. Validator: `scripts/check_sprint_contract.py`.
- **Two-call hard gate.** Reviewers run paper-content-blind Phase 1 + paper-visible Phase 2; Phase 1 output is wrapped in `<phase1_output>...</phase1_output>` data delimiter to narrow the self-injection surface.
- **Synthesizer three-step mechanical protocol.** Build cross-reviewer matrix → evaluate each `failure_condition` with panel-relative quantifier + recognised expression vocabulary → resolve precedence by `severity`. Forbidden-ops list explicit in `editorial_synthesizer_agent`.
- **Two reviewer templates ship** (`shared/contracts/reviewer/full.json` panel 5; `shared/contracts/reviewer/methodology_focus.json` panel 2). `reviewer_re_review`, `reviewer_calibration`, `reviewer_guided` are reserved in the schema enum but ship without contract templates in v3.6.2; they retain pre-v3.6.2 behaviour. `reviewer_quick` is excluded from the enum entirely.
- `academic-paper-reviewer` SKILL version: `1.8.1 → 1.9.0`. `academic-pipeline` SKILL version: `3.5.1 → 3.6.2` (suite-version invariant). Suite version bumped to `3.6.2`.
- See spec [`docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md`](docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md) and protocol [`academic-paper-reviewer/references/sprint_contract_protocol.md`](academic-paper-reviewer/references/sprint_contract_protocol.md).

### v3.5.1 (2026-04-22) — Opt-in Socratic Reading-Check Probe

v3.5.1 adds an opt-in honesty probe to the Socratic Mentor (`ARS_SOCRATIC_READING_PROBE=1`). Default off. See CHANGELOG.

- **Opt-in reading-check probe**: when `ARS_SOCRATIC_READING_PROBE=1` is set, the Socratic Mentor fires a one-time honesty probe during goal-oriented sessions where the user has cited a specific paper. Decline is logged without penalty. Outcome flows into the Research Plan Summary and Stage 6 AI Self-Reflection Report. No new agent, no schema change.
- `deep-research` SKILL version: `2.9.0 → 2.9.1`. `academic-pipeline` SKILL version: `3.5.0 → 3.5.1`. Suite version bumped to `3.5.1`.

### v3.5.0 (2026-04-21) — Collaboration Depth Observer

- **New agent**: `collaboration_depth_agent` in `academic-pipeline` (Agent Team grows from 3 to 4). Invoked at every FULL/SLIM checkpoint and at pipeline completion; scores user-AI collaboration against a 4-dimension rubric. **Advisory only — never blocks progression.** MANDATORY checkpoints (Stages 2.5 / 4.5 integrity gates) do NOT invoke the observer.
- **New rubric**: [`shared/collaboration_depth_rubric.md`](shared/collaboration_depth_rubric.md) v1.0. Dimensions: Delegation Intensity, Cognitive Vigilance, Cognitive Reallocation, Zone Classification (Zone 1 / Zone 2 / Zone 3). Based on Wang, S., & Zhang, H. (2026). "Pedagogical partnerships with generative AI in higher education: how dual cognitive pathways paradoxically enable transformative learning." *International Journal of Educational Technology in Higher Education*, 23:11. DOI [10.1186/s41239-026-00585-x](https://doi.org/10.1186/s41239-026-00585-x).
- **Cross-model divergence flagged, not averaged**: when `ARS_CROSS_MODEL` is set the observer runs on both models; dimension disagreement > 2 points is reported rather than silently smoothed. `ARS_CROSS_MODEL_SAMPLE_INTERVAL` escape hatch for cost trade-off.
- **Short-stage guard**: stages with fewer than 5 user turns inject a static `insufficient_evidence` block instead of dispatching the full-model observer.
- **Anti-sycophancy discipline**: scores ≥ 7 require specific dialogue-turn citations; Zone 3 triggers re-audit; no motivational framing.
- `academic-pipeline` SKILL version: `3.3.0 → 3.4.0`. Suite version bumped to `3.5.0`. New lint `scripts/check_collaboration_depth_rubric.py` + 10 tests.

### v3.4.0 (2026-04-20) — Compliance Agent + Schema 12

- **Compliance Agent** (shared): single mode-aware agent running PRISMA-trAIce 17 items (SR mode only) + RAISE 4 principles + 8-role matrix. Hooks existing Stage 2.5 / 4.5 Integrity Gates; tier-based block (Mandatory → block, HR → warn, R/O → info). Non-SR entries run principles-only, warn-only.
- **Schema 12 compliance_report** appended to Material Passport via `compliance_history[]` (append-only).
- **3-round user-override ladder** auto-injects `disclosure_addendum` into manuscript. No detection evasion possible.
- **Calibration with transparent reporting**, no hard FNR/FPR gate — self-consistent with `task_type: open-ended`.
- **Upstream freshness CI** warns on PRISMA-trAIce drift (non-blocking).
- **Long-running session docs**: Material Passport as cross-session resume mechanism.

### v3.3.6 (2026-04-15) — README Streamlining + ARCHITECTURE doc

- Added `docs/ARCHITECTURE.md` as the single source of truth for pipeline structure (flow, matrix, data-access, dependency graph, quality gates, modes). Merged into main via PR #18.
- Added `docs/SETUP.md` (prerequisites, API keys, Pandoc/tectonic, cross-model verification, installation methods) and `docs/PERFORMANCE.md` (token budgets, recommended Claude Code settings). README links to both instead of inlining them.
- Streamlined README: removed the ASCII pipeline diagram and 16-point key-feature list (superseded by ARCHITECTURE.md); Skill Details section now anchors version numbers and points readers to ARCHITECTURE.md §3 for per-agent rosters.
- Note: no functional change to any skill. Pure documentation reorganization. Suite version bumped to `3.3.6`.

### v3.3.5 (2026-04-15)
- Added `benchmark_report.schema.json` + `repro_lock` optional block on Material Passport. Both ship with pattern docs, lints, and examples. First formal Python dev dep manifest (`requirements-dev.txt`).

### v3.3.4 (2026-04-15) — README Changelog Sync Patch

- Synced the embedded changelog sections in `README.md` and `README.zh-TW.md` so they include the missing `v3.3.3` and `v3.3.2` release summaries.
- Extended `scripts/check_spec_consistency.py` so future README changelog drift fails CI.
### v3.3.3 (2026-04-15) — Release Prep + Lint Hardening

- Hardened SKILL frontmatter linting: missing closing `---` fences now fail cleanly instead of being parsed as valid YAML.
- Frontmatter that parses as valid YAML but not as a mapping now reports a readable error instead of crashing.
- Fixed the broken showcase link for the post-publication audit report in both READMEs.
- Added README relative-link validation to the spec consistency check so dead links fail CI.
- Aligned the DOCX output contract across the docs: direct `.docx` generation is Pandoc-dependent, with Markdown + conversion instructions as fallback.
- Prepared the `v3.3.3` release: suite version bump, `academic-paper` -> v3.0.2, `academic-pipeline` -> v3.2.2.

### v3.3.2 (2026-04-15) — Data Access Levels + Task Type Metadata

- Added `metadata.data_access_level` to all top-level `SKILL.md` files with enforced vocabulary: `raw`, `redacted`, `verified_only`.
- Added `metadata.task_type` to all top-level `SKILL.md` files with enforced vocabulary: `open-ended`, `outcome-gradable`.
- Added lint scripts and unit tests for both metadata fields, wired into the GitHub Actions spec consistency workflow.
- Added `shared/ground_truth_isolation_pattern.md` and linked the new vocabulary from `shared/handoff_schemas.md`.

### v3.3.1 (2026-04-14) — Spec Consistency Patch

- Synced README, `.claude/CLAUDE.md`, `MODE_REGISTRY.md`, and `SKILL.md` files to the current mode counts and published skill versions.
- Corrected cross-model wording: integrity sample checks and independent DA critique are implemented today; sixth-reviewer peer review remains planned.
- Clarified adaptive checkpoint semantics so SLIM checkpoints still wait for explicit user confirmation.
- Reaffirmed that Stage 2.5 and Stage 4.5 integrity gates cannot be skipped.
- Added a lightweight spec consistency check and GitHub Actions workflow to catch future drift.

### v3.3 (2026-04-09) — PaperOrchestra-Inspired Enhancements

Integrates techniques from [PaperOrchestra](https://arxiv.org/abs/2604.05018) (Song, Song, Pfister & Yoon, 2026, Google).

- **Semantic Scholar API Verification** — Tier 0 programmatic reference existence check via S2 API. Levenshtein >= 0.70 title matching, DOI mismatch detection, bibliography deduplication via S2 IDs. Graceful degradation if API unavailable.
- **Anti-Leakage Protocol** — Knowledge Isolation Directive prioritizes session materials over LLM parametric memory. Flags `[MATERIAL GAP]` for missing content instead of filling from memory. Reduces Mode 5/6 failure risk.
- **VLM Figure Verification** (optional) — Closed-loop verification of rendered figures using vision-capable LLM. 10-point checklist, max 2 refinement iterations.
- **Score Trajectory Protocol** — Per-dimension rubric score delta tracking across revision rounds (7 dimensions). Detects regressions (delta < -3) and triggers mandatory checkpoint.
- **Stage 2 Parallelization** — Visualization and argument building can run in parallel after outline completion.
- New versions: deep-research v2.8, academic-paper v3.0, academic-pipeline v3.2

### v3.2 (2026-04-09) — Lu 2026 Nature Integration

Integrates insights from Lu et al. (2026, *Nature* 651:914-919) — the first end-to-end autonomous AI research system to pass blind peer review.

- **7-mode AI Research Failure Mode Checklist** — blocks pipeline at Stage 2.5/4.5 on suspected implementation bugs, hallucinated results, shortcut reliance, bug-as-insight, methodology fabrication, frame-lock. Extends existing 5-type citation hallucination taxonomy.
- **Reviewer Calibration Mode** (academic-paper-reviewer v1.8) — opt-in FNR/FPR/balanced-accuracy measurement against user-supplied gold set. 5× ensembling, cross-model default-on, session-scoped confidence disclosure.
- **Disclosure Mode** (academic-paper v2.9) — venue-specific AI-usage statement generator. v1 covers ICLR, NeurIPS, Nature, Science, ACL, EMNLP.
- **Early-Stopping Criterion** (academic-pipeline v3.1) — convergence check + budget transparency at pipeline start.
- **Fidelity-Originality Mode Spectrum** — classifies all modes across 3 skills per Lu 2026 Fig 1c.
- New versions: academic-paper v2.9, academic-paper-reviewer v1.8, academic-pipeline v3.1

### v3.1.1 (2026-04-09) — IS Senior Scholars' Basket of 11

External contributions: [@mchesbro1](https://github.com/mchesbro1) originally proposed and drafted the IS Basket of 8 journals ([Issue #5](https://github.com/Imbad0202/academic-research-skills/issues/5)); [@cloudenochcsis](https://github.com/cloudenochcsis) extended it to the full Senior Scholars' Basket of 11 ([Issue #7](https://github.com/Imbad0202/academic-research-skills/issues/7), [PR #8](https://github.com/Imbad0202/academic-research-skills/pull/8)). Updated `academic-paper-reviewer/references/top_journals_by_field.md` Section 7, adding *Decision Support Systems*, *Information & Management*, and *Information and Organization*. Source: [AIS Senior Scholars' List of Premier Journals](https://aisnet.org/page/SeniorScholarListofPremierJournals).

### v3.1 (2026-04-06) — Anti-Context-Rot + Cognitive Frameworks + Lean Size

Inspired by patterns from [aspi6246/Claude-Code-Skills-for-Academics](https://github.com/aspi6246/Claude-Code-Skills-for-Academics).

**Wave 1: Anti-Context-Rot Anchors**
- 29 explicit Anti-Patterns across all 4 skills (7-8 per skill, tabular format with "Why It Fails" + "Correct Behavior")
- 22 IRON RULE markers on critical rules that must not be violated even in long conversations
- Read-only constraint on academic-paper-reviewer (reviewers cannot modify the manuscript)

**Wave 2: Traceability + Cognitive Frameworks + Reinforcement**
- R&R Traceability Matrix (Schema 11): adds "Author's Claim" and "Verified?" columns to re-review output, enabling independent verification of revision claims
- 3 cognitive framework reference files teaching agents "how to think" not just "what to do":
  - `argumentation_reasoning_framework.md` — Toulmin model, Bradford Hill causal reasoning, inference to best explanation, epistemic status classification
  - `review_quality_thinking.md` — three lenses (internal validity, external validity, contribution), common reviewer traps, calibration questions
  - `writing_judgment_framework.md` — clarity test, reader's journey, discipline-specific voice, revision decision matrix
- Mid-conversation reinforcement protocol: stage-specific IRON RULE + Anti-Pattern reminders at every pipeline transition
- Self-check questions at every FULL checkpoint (citation integrity, sycophantic concession, quality trajectory, scope discipline, completeness)

**Wave 3: Lean Skill Size**
- SKILL.md total size reduced from 142KB to 85KB (−40%) by extracting detailed protocols to `references/` files
- ~15 new reference files created (re-review protocol, guided mode, systematic review, process summary, external review, etc.)
- All IRON RULE markers preserved in SKILL.md; detailed content loaded on demand
- New versions: deep-research v2.7, academic-paper v2.8, academic-paper-reviewer v1.7, academic-pipeline v3.0

### v3.0 (2026-04-03) — Anti-Sycophancy + Intent Detection + Dialogue Health
- **Devil's Advocate Concession Threshold** (deep-research + academic-paper-reviewer): DA must score rebuttals 1-5 before responding. Concession only at ≥4. No consecutive concessions. Concession rate tracking. Frame-lock detection after each checkpoint.
- **Attack Intensity Preservation** (academic-paper-reviewer): DA does not soften under pushback. Rebuttal assessment protocol with explicit deflection detection. Anti-sycophancy rules prevent persistent pushback from being treated as valid evidence.
- **Intent Detection Layer** (deep-research socratic): Classifies user intent as exploratory vs. goal-oriented. Exploratory mode disables auto-convergence, raises max rounds, prohibits premature closure. Re-assesses every 3 turns.
- **Dialogue Health Indicator** (deep-research socratic): Silent self-check every 5 turns for persistent agreement, conflict avoidance, premature convergence. Auto-injects challenges when agreement pattern detected.
- **Cross-Model Verification Protocol** (shared, optional): Use GPT-5.4 Pro or Gemini 3.1 Pro for integrity verification sample cross-checks and independent DA critique. Sixth-reviewer peer review remains planned, not yet implemented. Activated by setting `ARS_CROSS_MODEL` env var — without it, everything works as before. See `shared/cross_model_verification.md` for full setup guide, API patterns, and cost estimates.
- **AI Self-Reflection Report** (academic-pipeline Stage 6): Post-pipeline self-assessment of AI behavioral patterns — DA concession rate, checkpoint skip rate, health alerts, sycophancy risk rating (LOW/MEDIUM/HIGH), frame-lock incidents, convergence pattern analysis. Includes irony caveat: "this self-reflection is itself produced by the same AI that may have been sycophantic."
- Origin: Discovered through a 4-round dialectic experiment where the DA conceded too quickly, the Socratic Mentor tried to converge prematurely, and the entire debate stayed locked in a frame the human set.
- Versions: deep-research v2.5, academic-paper-reviewer v1.5, academic-pipeline v2.8

### v2.9 (2026-03-27) — Style Calibration + Writing Quality Check
- **Style Calibration** (academic-paper intake Step 10, optional): Provide 3+ past papers and the pipeline learns your writing voice — sentence rhythm, vocabulary preferences, citation integration style. Applied as a soft guide during drafting; discipline conventions always take priority. Priority system: discipline norms (hard) > journal conventions (strong) > personal style (soft). See `shared/style_calibration_protocol.md`
- **Writing Quality Check** (`academic-paper/references/writing_quality_check.md`): Writing quality checklist applied during draft self-review. 5 categories: AI high-frequency term warnings (25 terms), punctuation pattern control (em dash ≤3), throat-clearing opener detection, structural pattern warnings (Rule of Three, uniform paragraphs, synonym cycling), and burstiness checks (sentence length variation). These are good writing rules — not detection evasion
- **Style Profile** carried through academic-pipeline Material Passport (Schema 10 in `shared/handoff_schemas.md`)
- **deep-research** report compiler also consumes both features optionally
- Versions: academic-paper v2.5, deep-research v2.4, academic-pipeline v2.7

### v2.8 (2026-03-22) — SCR Loop Phase 1: State-Challenge-Reflect
- **Socratic Mentor Agent** (deep-research + academic-paper): SCR (State-Challenge-Reflect) protocol integration
  - **Commitment Gates**: Collect user predictions before presenting evidence at each layer/chapter transition
  - **Certainty-Triggered Contradiction**: Detect high-confidence language ("obviously", "clearly") and introduce counterpoints
  - **Adaptive Intensity**: Track commitment accuracy, dynamically adjust challenge frequency
  - **Self-Calibration Signal (S5)**: New convergence signal tracking user's self-calibration growth across dialogue
  - **SCR Switch**: Users can say "skip the predictions" to disable or "turn predictions back on" to re-enable mid-dialogue; Socratic questioning continues normally
- `deep-research/references/socratic_questioning_framework.md`: SCR Overlay Protocol mapping SCR phases to Socratic functions
- Added `CHANGELOG.md`

### v2.7 (2026-03-09) — Integrity Verification v2.0: Anti-Hallucination Overhaul
- **integrity_verification_agent v2.0**: Anti-Hallucination Mandate (no AI memory verification), eliminated gray-zone classifications (VERIFIED/NOT_FOUND/MISMATCH only), mandatory WebSearch audit trail for every reference, Stage 4.5 fresh independent verification, Gray-Zone Prevention Rule
- **Known Hallucination Patterns**: 5-type taxonomy (TF/PAC/IH/PH/SH) from GPTZero × NeurIPS 2025 study, 5 compound deception patterns, real-world case study, literature statistics
- **Post-publication audit**: Full WebSearch verification of all 68 references found 21 issues (31% error rate) that passed 3 rounds of integrity checks — proving the necessity of external verification
- **Paper corrections**: Removed 4 fabricated references, fixed 6 author errors, corrected 7 metadata errors, fixed 2 format issues

### v2.6.2 (2026-03-09) — Intent-Based Mode Activation
- **deep-research**: Socratic mode now uses **intent-based activation** instead of keyword matching. Works in any language — detects meaning (e.g., "user wants guided thinking") rather than matching specific strings.
- **academic-paper**: Plan mode now uses **intent-based activation**. Detects intent signals like "user is uncertain how to start" or "user wants step-by-step guidance" in any language.
- Both modes now have a **default rule**: when intent is ambiguous, prefer `socratic`/`plan` over `full` — safer to guide first.
- Two-layer architecture: Layer 1 (skill activation) uses bilingual keywords for matching confidence; Layer 2 (mode routing) uses language-agnostic intent signals.

### v2.6.1 (2026-03-09) — Bilingual Trigger Keywords
- **deep-research**: Added Traditional Chinese trigger keywords for general activation and Socratic mode.
- **academic-paper**: Added Traditional Chinese trigger keywords and Plan Mode trigger section.
- Both mode selection guides now include bilingual examples and Chinese-specific misselection scenarios.

### v2.6 / v2.4 / v1.4 (2026-03-08) — 15+ Improvements
- **deep-research v2.3**: New systematic-review / PRISMA mode (7th); 3 new agents (risk_of_bias, meta_analysis, monitoring); PRISMA protocol/report templates; Socratic convergence criteria (4 signals + auto-end); Quick Mode Selection Guide
- **academic-paper v2.4**: 2 new agents (visualization, revision_coach); revision tracking template with 4 status types; citation format conversion (APA↔Chicago↔MLA↔IEEE↔Vancouver); statistical visualization standards; Socratic convergence criteria; revision recovery example; **LaTeX output hardening** — mandatory `apa7` document class, text justification fix (`ragged2e` + `etoolbox`), table column width formula, bilingual abstract centering, standardized font stack (Times New Roman + Source Han Serif TC VF + Courier New), PDF via tectonic only
- **academic-paper-reviewer v1.4**: Quality rubrics with 0-100 scoring and behavioral indicators; decision mapping (≥80 Accept, 65-79 Minor, 50-64 Major, <50 Reject); Quick Mode Selection Guide
- **academic-pipeline v2.6**: Adaptive checkpoint system (FULL/SLIM/MANDATORY); Phase E Claim Verification in integrity checks; Material Passport for mid-entry provenance; cross-skill mode advisor (14 scenarios); team collaboration protocol; enhanced handoff schemas (9 schemas); integrity failure recovery example

### v2.4 / v1.3 (2026-03-08)
- **academic-pipeline v2.4**: New Stage 6 PROCESS SUMMARY — auto-generates structured paper creation process record (MD → LaTeX → PDF, bilingual); mandatory final chapter: **Collaboration Quality Evaluation** with 6 dimensions scored 1–100 (Direction Setting, Intellectual Contribution, Quality Gatekeeping, Iteration Discipline, Delegation Efficiency, Meta-Learning), honest feedback, and improvement recommendations; pipeline expanded from 9 to 10 stages

### v2.3 / v1.3 (2026-03-08)
- **academic-pipeline v2.3**: Stage 5 FINALIZE now prompts for formatting style (APA 7.0 / Chicago / IEEE); PDF must compile from LaTeX via `tectonic` (no HTML-to-PDF); APA 7.0 uses `apa7` document class (`man` mode) with XeCJK for bilingual CJK support; font stack: Times New Roman + Source Han Serif TC VF + Courier New

### v2.2 / v1.3 (2025-03-05)
- **Cross-Agent Quality Alignment**: unified definitions (peer-reviewed, currency rule, CRITICAL severity, source tier) across all agents
- **deep-research v2.2**: synthesis anti-patterns, Socratic auto-end conditions, DOI+WebSearch verification, enhanced ethics integrity check, mode transition matrix
- **academic-paper v2.2**: 4-level argument scoring, plagiarism screening, 2 new failure paths (F11 Desk-Reject Recovery, F12 Conference-to-Journal), Plan→Full mode conversion
- **academic-paper-reviewer v1.3**: DA vs R3 role boundaries, CRITICAL finding criteria, consensus classification (4/3/SPLIT/DA-CRITICAL), confidence score weighting, Asian & Regional Journals reference
- **academic-pipeline v2.2**: checkpoint confirmation semantics, mode switching matrix, failure fallback matrix, state ownership protocol, material version control

### v2.0.1 (2026-03)
- **Simplify 4 SKILL.md** (-371 lines, -16.5%): remove cross-skill duplication, inline templates → file references, redundant routing tables, duplicate mode selection sections
- Fix revision loop cap contradiction between academic-paper and academic-pipeline

### v2.0 (2026-02)
- **academic-pipeline v2.0**: 5→9 stages, mandatory integrity verification, two-stage review, Socratic revision coaching, reproducibility guarantees
- **academic-paper-reviewer v1.1**: +Devil's Advocate Reviewer (7th agent), +re-review mode (verification), +post-review Socratic coaching
- New agent: `integrity_verification_agent` — 100% reference/data verification with audit trail
- New agent: `devils_advocate_reviewer_agent` — 8-dimension thesis challenger
- Output order: MD → DOCX via Pandoc when available (else instructions) → ask LaTeX → confirm → PDF

### v1.0 (2026-02)
- Initial release
- deep-research v2.0 (10 agents, 6 modes including socratic)
- academic-paper v2.0 (10 agents, 8 modes including plan)
- academic-paper-reviewer v1.0 (6 agents, 4 modes including guided)
- academic-pipeline v1.0 (orchestrator)
