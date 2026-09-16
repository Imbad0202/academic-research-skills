# Academic Research Skills for Claude Code

[![Version](https://img.shields.io/badge/version-v3.22.0-blue)](https://github.com/Imbad0202/academic-research-skills/releases/tag/v3.22.0)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20696614-blue)](https://doi.org/10.5281/zenodo.20696614)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/license-CC%20BY--NC%204.0-lightgrey)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Sponsor](https://img.shields.io/badge/sponsor-Buy%20Me%20a%20Coffee-orange?logo=buy-me-a-coffee)](https://buymeacoffee.com/crucify020v)

[简体中文版](README.zh-CN.md) | [繁體中文版](README.zh-TW.md) | [日本語版](README.ja-JP.md) | [한국어](README.ko-KR.md) | [Español](README.es-ES.md)

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

[**Zhao et al.**](https://arxiv.org/abs/2605.07723) (2026-05) audited 111M references across 2.5M papers on arXiv, bioRxiv, SSRN, and PMC. Their conservative estimate is 146,932 hallucinated citations for 2025 alone, with an observed mid-2024 inflection; for the bioRxiv-to-PMC pairing they report 85.3% preprint-to-published persistence. The paper describes "real citations deployed to support claims the cited references do not actually make" as an open challenge. ARS v3.7.1 added trust-chain frontmatter for source provenance; v3.7.3 added locator infrastructure (three-layer citation anchors) for future claim-level audits and surfaces advisory risk signals at cite time (ARS labels the claim-faithfulness gap internally as "L3"; this is ARS terminology, not the paper's). v3.7.x is motivated by Zhao et al.'s corpus-scale findings; corpus-scale evaluation of ARS itself remains future work.

v3.8 closes the second half of the L3 gap. v3.7.3 made every citation carry a locator anchor; v3.8 adds an opt-in audit pass (`ARS_CLAIM_AUDIT=1`) that fetches the cited source against each anchor and judges whether the claim is actually supported. Five new HIGH-WARN classes (claim-not-supported, negative-constraint-violation, fabricated-reference, anchorless, constraint-violation-uncited) gate-refuse output through the formatter terminal hard gate. Calibration is shipped as a 20-tuple gold set with FNR<0.15 + FPR<0.10 acceptance thresholds; ramp-on plan is deferred to post-calibration evidence per v3.8 spec §5.

[**Ren et al.**](https://arxiv.org/abs/2607.13104) (2026, *Self-Improvements in Modern Agentic Systems: A Survey*) supplies a third, survey-level anchor. Its scientific-discovery synthesis (§7.4) concludes that discovery agents cannot easily verify novelty, correctness, or reproducibility on their own and may exploit weak proxies instead, must manage evidence across heterogeneous tools and literature, and raise governance issues — "scientific writing can also amplify misinformation when the evidence is weak." Its generation-loop chapters (§5.1–§5.2) list human auditing and retained human anchors among the practical safeguards for self-generated evaluation loops, and its historical chapter (§2.2) records the oldest form of the same lesson: the practical success of Lenat's EURISKO depended heavily on the user serving as the external evaluation signal, pruning unproductive heuristic drift — a limitation the survey notes persists in modern agentic systems. ARS cites the survey as design rationale for its human-in-the-loop stance, not as empirical proof that human-in-the-loop pipelines outperform autonomous ones; the survey's actionable deltas for ARS are tracked in #539–#541 and #547–#550.

[**Gartenberg et al.**](https://doi.org/10.1287/orsc.2026.ed.v37.n3) (2026, *Organization Science* 37(3):795-812, "More versus better") supplies a fourth anchor, and the first from the journal side. The *Organization Science* AI Task Force scored every first submission (6,957) and every text-format review (10,389) the journal received between January 2021 and February 2026 with a commercial AI-writing classifier and standard readability indices. Manuscripts scored as heavily AI-written read worse on those indices and were desk-rejected more often; reviews scored as more AI-written leaned toward theory and away from data; and the editors conclude that current AI tools, amplified by publish-or-perish incentives, "appear to be pushing the system toward an equilibrium of more rather than better research." Their §5 contrasts "cognitive surrender" (Shaw & Nave, 2026, as cited there) with human-first use and asks authors to disclose how a manuscript was produced. The evidence is observational, aggregate, and from one journal, and the classifier is a proprietary instrument. ARS cites the editorial as design rationale for recording volume as a non-goal (see `POSITIONING.md`) and for the Collaboration Depth Observer and the claim-strength ladder, not as evidence about ARS output; the actionable deltas are tracked in #829–#833.

[**Wang, Li et al.**](https://arxiv.org/abs/2609.07713) (2026-09, *The Emerging AI Paper-Review Arms Race: Adversarial Co-Evolution in Scholarly Publishing*, a survey of 230 sources) supplies a fifth anchor, and the first that treats research production and peer review as one coupled system. Its evaluative-authority ladder (§4.1) runs from author-facing feedback through reviewer assistance and official AI reviews to scoring and decision support, with the survey's point that capability at one rung does not justify use at the next; ARS's simulated panel sits on the lowest rung by design (see `POSITIONING.md`). Two of its findings shape the reviewer roadmap. First, as the survey summarizes Dycke & Gurevych (2026, §4.5), 391 edits that break a paper's scientific support relations produced no statistically significant difference in the tested automated reviewers' aspects, sentiment, or scores compared with 540 soundness-neutral controls, while presentation-only rewrites with the science held fixed moved AI-review scores (§5.2); the survey's §9.2 conclusion is that a static evaluation can overstate an AI reviewer's reliability once authors can observe and adapt to it. ARS tracks the corresponding Round-1 paired controls in #871 and the author-identity-cue controls (§7.2) in #872; both are measurements, not new mechanisms. Second, its §9.1 cites Brodeur et al. (2026, *PNAS* 123(22):e2524747123), a randomized study in which 288 researchers in 103 teams reproduced published quantitative social-science results under three conditions: human-only, AI-assisted (ChatGPT as a collaborative tool), and AI-led (ChatGPT with minimal human oversight). Human-only and AI-assisted teams reproduced 94% and 91%, AI-led teams 37%, and the AI-assisted teams detected fewer major coding errors than the human-only teams. In that study, then, AI assistance did not verify better than humans alone and AI-led verification did much worse; ARS reads this as a reason to keep verification human-led at every checkpoint, not as evidence that its own checkpoints or integrity gates are effective. The survey is a synthesis rather than an experiment, its structured search stops at 2026-07-01 and the later targeted update did not rerun every query (§10), its deployment evidence is concentrated in a small number of AI/CS conferences, OpenReview-based settings, and selected journals, and its "arms race" framing is a lens, not a finding; ARS cites it as design rationale, not as evidence about ARS output.

v3.3 was inspired by [**PaperOrchestra**](https://arxiv.org/abs/2604.05018) (Song, Song, Pfister & Yoon, 2026, Google): Semantic Scholar API verification, anti-leakage protocol, VLM figure verification, and revision-trajectory tracking. ARS now implements that last idea through categorical, evidence-anchored criterion trajectories rather than score deltas.

---

## Architecture & pipeline

**👉 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — the full pipeline view: flow diagram, stage-by-stage matrix, data-access flow, skill dependency graph, quality gates, and mode list.

The architecture doc supersedes the sprawling pipeline description that used to live here. Everything about *what runs in which stage* now lives in one place.

## Quick install

**Prerequisites**

- [Claude Code](https://docs.claude.com/en/docs/claude-code/setup) (latest; plugin packaging requires recent versions)
- `ANTHROPIC_API_KEY` exported, or set on first `claude` run
- *Optional:* Pandoc for DOCX, tectonic + Source Han Serif TC for APA 7.0 PDF (Markdown output works without either)
- *Optional (real Python):* needed only for the write-scope guard and a few opt-in commands; the core skills are prompt-driven. Details, including the Windows notes on Git Bash and the Microsoft Store Python stub, are in [docs/SETUP.md § Python (optional)](docs/SETUP.md#python-optional).

> **Which controls are active in *your* install channel?** Availability varies by install channel. See the per-channel map: [docs/CONTROL_AVAILABILITY.md](docs/CONTROL_AVAILABILITY.md).

**Plugin install (v3.7.0+, recommended):**

```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

**Verify it works:** run `/ars-plan` and describe a paper you're working on — ARS will start a Socratic dialogue to map out chapter structure. For a single-shot test instead, try `/ars-lit-review "your topic"`.

**👉 [docs/SETUP.md](docs/SETUP.md)** — full guide: install Claude Code, set up API keys, optional Pandoc/tectonic for DOCX/PDF, cross-model verification (`ARS_CROSS_MODEL`), and six installation methods (Plugin, project skills, global skills, claude.ai Project, repo-cloned, Claude Science import).

**👉 [docs/DATA_FLOWS.md](docs/DATA_FLOWS.md)** — what leaves your machine (bibliographic resolvers, optional consent-gated cross-model calls, the plugin update check), what is cached locally, for how long, and how to turn each path off.

**👉 [docs/RISK_REGISTER.md](docs/RISK_REGISTER.md)** — the standing risks the suite knows about, which existing controls address each one, the evidence status behind those controls, and what remains open.

**Using Claude Science?** The four skills import directly: **Skills → Import from GitHub**, paste `https://github.com/Imbad0202/academic-research-skills`, **Preview**, then **Import 4 skills** (requires v3.14.0+ of this repo — the importer reads the explicit skill paths in the marketplace manifest). Imports are point-in-time snapshots: re-import after ARS updates. Imported skills carry the ARS methodology (research / writing / review protocols); Claude Code-specific machinery — slash commands, hooks, subagent orchestration — does not transfer. See [docs/SETUP.md](docs/SETUP.md) Method 5 for details.

**Using Pi?** Install the in-tree, community-maintained wrapper with `pi install git:github.com/Imbad0202/academic-research-skills`. It keeps the original ARS content authoritative and documents Pi-specific orchestration and hook limitations. See [`pi/README.md`](pi/README.md).

**Using Codex CLI?** Install the sibling distribution instead: [`Imbad0202/academic-research-skills-codex`](https://github.com/Imbad0202/academic-research-skills-codex) — same workflow content, Codex-native packaging as a single `$academic-research-suite` skill with `ars-*` aliases.

**Third-party platforms and integrations** that wrap or host ARS are listed in [THIRD_PARTY.md](THIRD_PARTY.md) — community-submitted and not reviewed or endorsed by the maintainer.

**Governance:** who decides, what cross-model review does and does not provide, and the project's end-of-life posture are stated in [GOVERNANCE.md](GOVERNANCE.md); security reporting and triage in [SECURITY.md](SECURITY.md).

## Performance & cost

**👉 [docs/PERFORMANCE.md](docs/PERFORMANCE.md)** — per-mode token budgets, full-pipeline estimate (~$4–6 for a 15k-word paper), and recommended Claude Code settings (Auto mode; Agent Team optional).

## Guides & articles

- [Academic Writing Shouldn't Be a Solo Act](https://open.substack.com/pub/edwardwu223235/p/academic-writing-shouldnt-be-a-solo?r=4dczl&utm_medium=ios) — full pipeline walkthrough (English)
- [學術寫作不該是一個人的事：一套開源 AI 協作工具如何改變研究者的工作流](https://open.substack.com/pub/edwardwu223235/p/ai?r=4dczl&utm_medium=ios) — 完整使用指南（繁體中文）

---

## Features at a glance

- **Deep Research** — 13-agent research team with Socratic guided mode, PRISMA systematic review, intent detection, dialogue health monitoring, optional cross-model DA, Semantic Scholar API verification.
- **Academic Paper** — 12-agent paper writing with Style Calibration, Writing Quality Check, LaTeX hardening, visualization, revision coaching, citation conversion, anti-leakage protocol, and VLM figure verification.
- **Academic Paper Reviewer** — 7-agent multi-perspective peer review with criterion-bound, evidence-anchored narrative judgements (Journal-Fit Reviewer + 3 dynamic reviewers + Devil's Advocate), concession threshold protocol, attack intensity preservation, optional cross-model DA critique / calibration, R&R traceability matrix, read-only constraint. Current live reviews remain `NOT_CALIBRATED`; full calibration produces a bounded candidate profile, while live-profile application is not yet wired.
- **Academic Pipeline** — 10-stage pipeline orchestrator with adaptive checkpoints, claim verification, Material Passport, optional `repro_lock`, optional cross-model integrity verification, mid-conversation reinforcement, and narrative criterion-by-criterion regression checks (the typed trajectory carrier is deferred).
- **Data Access Level Metadata** (v3.3.2+) — every skill declares `data_access_level` (`raw` / `redacted` / `verified_only`); enforced by `scripts/check_data_access_level.py`. Pattern adapted from Anthropic's automated-w2s-researcher (2026). See [`shared/ground_truth_isolation_pattern.md`](shared/ground_truth_isolation_pattern.md).
- **Task Type Annotation** (v3.3.2+) — every skill declares `task_type` (`open-ended` or `outcome-gradable`). All current ARS skills are `open-ended`.
- **Benchmark Report Schema** (v3.3.5+) — JSON Schema + lint for honest benchmark comparisons. See [`shared/benchmark_report_pattern.md`](shared/benchmark_report_pattern.md).
- **Artifact Reproducibility Lockfile** (v3.3.5+) — optional `repro_lock` sub-block on Material Passport. **Configuration documentation, not replay guarantee** — LLM outputs are not byte-reproducible. See [`shared/artifact_reproducibility_pattern.md`](shared/artifact_reproducibility_pattern.md).
- **Model Tiering** (#517, v3.16+) — optional `ARS_MODEL_TIERING` switch with two directions: `economy` (execution-type agents dispatch one tier below the session model, floor Opus-class) and `quality-boost` (judgment-type agents at integrity gates and final review step up to the frontier tier). Default unset = byte-equivalent to pre-#517 behavior. See [`shared/model_tiering.md`](shared/model_tiering.md).
- **Canonical Cross-Model Handoff Envelope** (#527, v3.17+) — the owner→dispatcher→owner blind-checkpoint transport path (#523) now has a machine-stable `[CROSS-MODEL-HANDOFF v1]` envelope with a normative Python grammar (`scripts/cross_model_handoff.py`) instead of prose-only enforcement, pinning agreement/divergence/malformed-result routing across all three checkpoint owners. See [`shared/cross_model_verification.md`](shared/cross_model_verification.md) §"Cross-model handoff envelope".
- **Experiment Provenance Intake** (#260) — optional `experiment_provenance[]` on the Material Passport records experiments the scholar ran **externally** (ARS never runs experiments), and manuscript claims join to them via `claim_intent_manifest.planned_experiment_ids[]`. The integrity gate (Stage 2.5/4.5) audits each experiment-backed claim against declared provenance — `ALIGNED` / `OVERSTATED` / `NOT_SUPPORTED_BY_PROVENANCE` / `PROVENANCE_INSUFFICIENT` — **without judging whether the experiment itself was correct**. A fail-closed `experiment_intake_declaration` makes "did you run experiments?" an explicit Stage 1 decision (even literature-only runs declare `no_experiments_declared`). See [`shared/handoff_schemas.md`](shared/handoff_schemas.md) §"Experiment Provenance Intake (#260)".

**Integrity and verification boundary:** ARS checks the manuscript and the reported process—including citation existence, claim–source alignment, reported methodology, declared experiment–result alignment, figure/table fidelity, and reporting/process/package conformance. Some checks are sampled or LLM-mediated. ARS does **not** establish that procedures were actually performed, raw data are authentic, or results reproduce; a consistently reported fabrication can pass these checks. See [POSITIONING.md § Integrity checks and the empirical-work boundary](POSITIONING.md#integrity-checks-and-the-empirical-work-boundary).

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
| [Peer Review Round 1](examples/showcase/stage3_review_report.pdf) | Journal-Fit Reviewer + 3 Reviewers + Devil's Advocate |
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

**Stage 1 intake declaration (#260)**: at Stage 1, ARS detects whether the run will carry experiment-backed claims and sets a fail-closed `experiment_intake_declaration` on the Material Passport. If you ran experiments externally, the scholar enters one `experiment_provenance[]` entry per experiment (`experiment_id`, nested `repro_lock`, `planned_vs_executed[]`, `negative_results[]`, `known_limitations[]`) and the declaration is set to `experiments_declared`; if not, it is set to `no_experiments_declared`. The declaration is **required on every post-#260 passport** — a run that touches no experiments still declares `no_experiments_declared`, so the integrity gate can never be silently bypassed by a forgotten provenance block. The `experiment_id`s are frozen at this intake point; the writers later reference them via `planned_experiment_ids[]`.

**Teaching-side companion**: [Teaching Skills](https://github.com/YujxZJCN/teaching-skills) applies the ARS architecture (skill ensembles, shared contracts, staged gates, a Course Passport) to the teaching side of academic life — course design → lessons → assessment → delivery → reflection; its `sotl` mode hands classroom-inquiry projects off to ARS deep-research / academic-paper for the publication phase.

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

#### Deep Research (8 modes)

```
"Research the impact of AI on higher education"       → full mode
"Give me a quick brief on X"                          → quick mode
"Do a systematic review on X with PRISMA"             → systematic-review mode
"Guide my research on X"                              → socratic mode (guided)
"Fact-check these claims"                             → fact-check mode
"Do a literature review on X"                         → lit-review mode
"Compare these papers in WHY/HOW/WHAT format"         → three-way-scan mode
"Review this paper's research quality"                → review mode
```

#### Academic Paper (11 modes)

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
"Audit my rebuttal draft against the reviews"         → rebuttal-audit mode
```

#### Academic Paper Reviewer (6 modes)

```
"Review this paper"                                   → full mode (Journal-Fit Reviewer + R1/R2/R3 + Devil's Advocate)
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

### Deep Research (v2.12.1)

13-agent research team. Modes: full, quick, review, lit-review, three-way-scan, fact-check, socratic, systematic-review. Full agent roster and artifacts: see ARCHITECTURE.md §3.

### Academic Paper (v3.3.1)

12-agent paper writing pipeline. Modes: full, plan, outline-only, revision, revision-coach, abstract-only, lit-review, format-convert, citation-check, disclosure, rebuttal-audit. Output: MD + DOCX (via Pandoc when available) + LaTeX (APA 7.0 `apa7` class / IEEE / Chicago) → PDF via tectonic. Full agent roster and per-phase responsibilities: see ARCHITECTURE.md §3.

### Academic Paper Reviewer (v1.11.1)

7-agent multi-perspective review with **criterion-bound narrative judgements**. Modes: full, re-review, quick, methodology-focus, guided, calibration. Current live reviews and Schema 6 packages remain `NOT_CALIBRATED`; full calibration can produce a bounded candidate profile, but application to a live review is not wired. No numerical total is mapped to Accept, Minor Revision, Major Revision, or Reject. First-round review panel vs. contract-governed re-review dispatch boundary: see ARCHITECTURE.md §3 Stage 3 / Stage 3'.

### Academic Pipeline (v3.22.0)

10-stage orchestrator with integrity verification, two-stage review, Socratic coaching, and collaboration evaluation. Pipeline guarantees: every stage requires user confirmation checkpoint; integrity verification (Stage 2.5 + 4.5) is MANDATORY with no unrecorded bypass (every override requires user reasoning recorded for Stage 6); R&R Traceability Matrix (Schema 11) independently verifies author revision claims. v3.4 added the Compliance Agent (PRISMA-trAIce + RAISE) at Stage 2.5 / 4.5. v3.5 adds the **Collaboration Depth Observer** (`collaboration_depth_agent`, advisory only — never blocks) at every FULL/SLIM checkpoint and at pipeline completion. MANDATORY integrity gates (2.5 / 4.5) explicitly skip the observer so compliance checks are not diluted. Based on Wang & Zhang (2026), IJETHE 23:11. Stage-by-stage matrix with agents, artifacts, and gates: see ARCHITECTURE.md §3.

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

**[cloudenochcsis](https://github.com/cloudenochcsis)** — Contributor. Extended the IS section from the *Basket of 8* to the full *Senior Scholars' Basket of 11* — adding *Decision Support Systems*, *Information & Management*, and *Information and Organization* ([Issue #7](https://github.com/Imbad0202/academic-research-skills/issues/7), [PR #8](https://github.com/Imbad0202/academic-research-skills/pull/8)). Sourced from the [AIS Senior Scholars' List of Premier Journals](https://aisnet.org/research/seniorscholarsbasket/).

**[eltociear](https://github.com/eltociear)** (Ikko Eltociear Ashimine) — Contributor. Translated the Japanese README ([`README.ja-JP.md`](README.ja-JP.md)) ([PR #161](https://github.com/Imbad0202/academic-research-skills/pull/161)).

**[xpfo-go](https://github.com/xpfo-go)** (xpfo) — Contributor. Translated the Simplified Chinese README ([`README.zh-CN.md`](README.zh-CN.md)) ([PR #181](https://github.com/Imbad0202/academic-research-skills/pull/181)).

**[devCharlotte](https://github.com/devCharlotte)** — Contributor. Translated the Korean README ([`README.ko-KR.md`](README.ko-KR.md)) ([PR #469](https://github.com/Imbad0202/academic-research-skills/pull/469)).

**[Yaobin29](https://github.com/Yaobin29)** — Contributor. Proposed reviewer-response tooling in [PR #433](https://github.com/Imbad0202/academic-research-skills/pull/433); the `deep-research three-way-scan` mode and the `academic-paper rebuttal-audit` mode (rescued from the PR's `audit` concept) were integrated from that contribution in v3.12.1.

**[ktao732084-arch](https://github.com/ktao732084-arch)** — Contributor. Expanded the `academic-paper` disclosure system with nine medical-publishing policy targets, target-specific required-fact intake, and fail-closed standalone rendering ([Issue #596](https://github.com/Imbad0202/academic-research-skills/issues/596), [PR #599](https://github.com/Imbad0202/academic-research-skills/pull/599)); expanded the EQUATOR clinical-reporting reference with condensed CARE, STARD and TRIPOD+AI guidance plus a fail-closed study-design routing sequence ([Issue #594](https://github.com/Imbad0202/academic-research-skills/issues/594), [PR #601](https://github.com/Imbad0202/academic-research-skills/pull/601)); and designed and contributed the standalone Chinese-literature resolver, API protocol, and synthetic transport-fixture suite ([Issue #595](https://github.com/Imbad0202/academic-research-skills/issues/595), [PR #600](https://github.com/Imbad0202/academic-research-skills/pull/600)).

**[didacrios](https://github.com/didacrios)** — Contributor. Translated the Spanish README ([`README.es-ES.md`](README.es-ES.md)).

---

## Changelog

Only the three most recent releases are summarized here. The full release history, including the one-paragraph summaries that used to live on this page, is in [CHANGELOG.md](CHANGELOG.md).

### v3.22.0 (2026-09-16) — Output-language-pair contract, locale track, plugin eval suites, and Windows / transport repairs

> **Additive structure, bounded evidence:** v3.22.0 lets a run declare its output language pair through a registry-keyed Schema 4 field whose absence reproduces the legacy files exactly (#862 Phase 1, PR #869), and stands up the locale track around it: an es-ES README and conservative trigger phrases contributed by @didacrios, and a community-maintained locale-pack policy with a provisional single-owner route. Two `claude plugin eval` suites (revision-coach, citation-check) and the reviewer-calibration harness ship as regression guards and dispatch substrates only; none claims a measured uplift or calibration value. Repairs: `/ars-mark-read` and the other five lock sites run on Windows through one shared helper with an `msvcrt` backend, the OpenAI request builders stop sending parameters GPT-6 Astra rejects, the contained Codex transport refuses `effort=ultra`, audit provenance records the actual judge identity, Socratic path F6 no longer preselects a direction, and an unsupported claim can no longer be rescued by hedging. READMEs keep three releases; Gartenberg et al. and Wang, Li et al. join the human-in-the-loop anchors. Roadmap Phase 4 (stage-level evidence ceilings) is not delivered in this release; its window carries forward.

### v3.21.2 (2026-09-06) — Model currency for Claude Fable 5.1 and GPT-6 Astra, checkpoint decision provenance, and CJK title-matching repairs

> **Currency and provenance, not new capability:** v3.21.2 aligns the suite to the two September 2026 vendor system cards. `gpt-6-astra` enters the cross-model table as provisional on both transports and becomes the recommended OpenAI verifier under the generation-currency policy; `gpt-5.6-sol` keeps its validated status on the ChatGPT-subscription citation transport, and no new bakeoff result is claimed. The contained Codex transport's reasoning-effort set gains `ultra`. Two guardrails are added, both prompt-level and vendor-motivated rather than ARS-measured: checkpoint decision provenance (only a user turn is a decision; decisions are re-transmitted to subagents verbatim; risk R11) and provider-side monitoring or safety interventions named as a transport failure that is never a verdict. A harness-retirement audit against both cards retires nothing (0 prompt-text retirements; 8 keep-as-debt items now carry a card citation). Fixes: CJK titles no longer fail the exact-title gate in the four index resolvers (#798) and wrapper marks are stripped only as one balanced unit (#800); the autolink round-trip test declares its dependency (#801); `check_surface_form_parity` names a broken environment instead of the manifest; a skill-inventory parity lint (#809); the R10 residual gap de-staled (#813); an MLA key-rules line corrected (#805). Suite/pipeline → v3.21.2; deep-research → v2.12.1; academic-paper → v3.3.1; academic-paper-reviewer → v1.11.1.

### v3.21.1 (2026-08-24) — Bounded workflow substrates, sealed bakeoffs, and transport hardening

> **Measured where stated; otherwise bounded:** v3.21.1 repairs the contained ChatGPT-subscription citation transport for codex-cli 0.147.0 and records the first Promotion Bakeoff: `gpt-5.6-sol` is validated only for that subscription transport, while it remains provisional on the first-party API route. Future bakeoffs now require sealed preregistration. The release also adds a default-off research-workflow profile substrate (offline deterministic conformance only; no pipeline hook or family-specific shipped profile), an opt-in inquiry-ledger alpha (`ARS_INQUIRY_LEDGER=1`), and a design-only alternative register that is not implemented. Their behavioral evidence remains `NOT_RUN`; no usability, recovery, novelty, correctness, or research-outcome benefit is claimed. The review-criteria registry gains one source-backed illustrative MSR 2027 exact-profile proving set—not venue/discipline coverage, a real-author attestation, or constructive-review evidence—and its required independent-human evaluation remains open. Additional changes align `data_access_level`, consolidate markdown lint grammar, register guard-launcher degradations, and list OrcaRouter as a community integration without endorsement. Suite/pipeline → v3.21.1; deep-research → v2.12.1; academic-paper → v3.3.1; academic-paper-reviewer → v1.11.1.
