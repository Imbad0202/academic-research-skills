# Academic Research Skills Changelog

Cross-skill fixes and update history.

---

## 2026-04-09

### Information Systems — Basket of 8 → Senior Scholars' Basket of 11 (v3.1.1)

External contribution from [@cloudenochcsis](https://github.com/cloudenochcsis) via [PR #8](https://github.com/Imbad0202/academic-research-skills/pull/8).

**Files changed**: 1 file, +20 / −2 lines

**`academic-paper-reviewer/references/top_journals_by_field.md`**
- Section 7 heading: "Information Systems (Basket of 8)" → "Information Systems (Senior Scholars' Basket of 11)"
- Added 3 journals to complete the AIS official list:
  - *Decision Support Systems* (Elsevier, IF 6-8) — Analytics, decision-making, DSS design and evaluation
  - *Information & Management* (Elsevier, IF 8-11) — IS management, technology adoption, organizational impact
  - *Information and Organization* (Elsevier, IF 5-7) — Socio-material perspectives, qualitative and interpretive research
- Subsequent sections renumbered: Interdisciplinary → 8, Asian & Regional → 9

**Why Basket of 11 instead of Basket of 8**: The "Basket of 8" is a widely-cited shorthand, but the [AIS College of Senior Scholars](https://aisnet.org/research/seniorscholarsbasket/) officially recognizes 11 premier journals. Most IS doctoral programs and tenure committees reference the full Basket of 11. AIS is the authoritative IS academic organization (equivalent to ACM for computer science or APA for psychology).

**Verification**: All 11 journals cross-checked against the AIS official page. cloudenochcsis's diff matched 1:1 against the source list and used the same metadata format established by the v2.9 Basket of 8 entries.

---

## 2026-04-06

### Anti-Context-Rot + Cognitive Frameworks + Lean Size (v3.1)

Inspired by patterns from [aspi6246/Claude-Code-Skills-for-Academics](https://github.com/aspi6246/Claude-Code-Skills-for-Academics).

**Wave 1: Anti-Context-Rot Anchors**
- Added `## Anti-Patterns` section to all 4 SKILL.md files (29 total: 7-8 per skill)
- Added 22 `⚠️ IRON RULE` markers to critical rules across all skills
- Added Read-Only constraint to academic-paper-reviewer (Checkpoint Rule #6)

**Wave 2: Traceability + Cognitive Frameworks + Reinforcement**
- R&R Traceability Matrix (Schema 11) in `shared/handoff_schemas.md`: `Author's Claim` + `Verified?` columns in re-review output
- New reference: `deep-research/references/argumentation_reasoning_framework.md` (Toulmin, Bradford Hill, IBE, epistemic status)
- New reference: `academic-paper-reviewer/references/review_quality_thinking.md` (three lenses, reviewer traps, calibration)
- New reference: `academic-paper/references/writing_judgment_framework.md` (clarity test, reader's journey, voice, revision matrix)
- Mid-conversation reinforcement protocol in pipeline: stage-specific IRON RULE + Anti-Pattern reminders at every transition
- Self-check questions at every FULL checkpoint (5 questions: citation integrity, sycophancy, quality trajectory, scope, completeness)

**Wave 3: Lean Skill Size**
- Extracted detailed protocols from SKILL.md to `references/` files: 142KB → 85KB (−40%)
- New reference files: `re_review_mode_protocol.md`, `guided_mode_protocol.md`, `integration_guide.md`, `plan_mode_protocol.md`, `workflow_phase_details.md`, `socratic_mode_protocol.md`, `systematic_review_protocol.md`, `cross_agent_quality_definitions.md`, `process_summary_protocol.md`, `external_review_protocol.md`, `integrity_review_protocol.md`, `two_stage_review_protocol.md`, `reproducibility_audit.md`, `progress_dashboard_template.md`, `reinforcement_content.md`
- Changelog extracted from all 4 SKILL.md files to `references/changelog.md`
- All IRON RULE markers preserved in SKILL.md; detailed content loaded on demand

**Historical fixes**:
- Fixed date typo `2025-03-05` → `2026-03-05` in all 4 changelogs
- Added missing Version Info tables to academic-paper and deep-research
- Fixed broken reference path `shared/integrity_verification_agent.md`

**Version bumps**: deep-research v2.7, academic-paper v2.8, academic-paper-reviewer v1.7, academic-pipeline v3.0

---

## 2026-03-27

### Style Calibration + Writing Quality Check (v2.9)

**Files changed**: 10 files across `academic-paper/`, `deep-research/`, `academic-pipeline/`, `shared/`, root

**New files**:
- `shared/style_calibration_protocol.md`: Full calibration flow (6 dimensions: sentence length, paragraph length, vocabulary preferences, citation integration, modifier style, register shifts). Priority system: discipline norms (hard) > journal conventions (strong) > personal style (soft). Conflict resolution with user notification.
- `academic-paper/references/writing_quality_check.md`: Writing quality checklist (5 categories: 25-term AI high-frequency word warnings, punctuation pattern control, throat-clearing detection, structural pattern warnings, burstiness checks). Not a humanizer — good writing rules applicable regardless of author.

**Modified agents**:
- `academic-paper/agents/intake_agent.md`: New Step 10 (Style Calibration, optional). Renumbered Funding Sources to Step 11. Added `style_profile` field to Paper Configuration Record.
- `academic-paper/agents/draft_writer_agent.md`: Step 1 pre-writing checklist gains Style Profile + Writing Quality Check items. Step 2 self-review gains Step 7 (style & lint check).
- `deep-research/agents/report_compiler_agent.md`: New sections for optional Style Calibration and Writing Quality Check before Writing Style Guidelines.
- `academic-pipeline/agents/pipeline_orchestrator_agent.md`: Style Profile carry-through in Material Passport.

**Schema update**:
- `shared/handoff_schemas.md`: Schema 10 (Style Profile) with 8 required fields, 3 optional fields, consumption priority system, and example.

**SKILL.md updates**:
- `academic-paper/SKILL.md`: v2.4 -> v2.5
- `deep-research/SKILL.md`: v2.3 -> v2.4
- `academic-pipeline/SKILL.md`: v2.6 -> v2.7

**README updates**: EN + zh-TW both updated with v2.9 badge, new features in Features list, and changelog entry.

**Design rationale**: The original proposal included 4 features (Argue-First Gate, Skeleton Drafting, Weighting, Style Calibration) under a "Jarvis Framework". Analysis showed Argue-First Gate, Skeleton Drafting, and Weighting overlapped 60-90% with existing Socratic convergence signals, Plan Mode Chapter Summary, and Integrity Verification respectively. Only Style Calibration was genuinely new. Writing Quality Check was adopted from Type A humanizer research (term/pattern replacement) as a writing quality improvement, explicitly not for AI detection evasion.

---

## 2026-03-09

### Intent-Based Mode Activation (v2.6.2)

**Files changed**: 6 files across `deep-research/`, `academic-paper/`, root

**deep-research/SKILL.md**:
- `### Socratic Mode Trigger Keywords` → `### Socratic Mode Activation`
- Replaced keyword-matching logic with intent-based activation: 5 intent signals that work in any language
- Added default rule: ambiguous intent → prefer `socratic` over `full`
- Example triggers condensed to single line with "or equivalent in any language"

**academic-paper/SKILL.md**:
- `### Plan Mode Trigger Keywords` → `### Plan Mode Activation`
- Replaced keyword-matching logic with intent-based activation: 6 intent signals
- Added default rule: ambiguous intent → prefer `plan` over `full`
- Example triggers condensed to single line with "or equivalent in any language"

**README.md / README.zh-TW.md**:
- Updated Supported Languages section: mode activation is intent-based and language-agnostic; general Trigger Keywords (Layer 1) still benefit from bilingual entries for skill-level matching confidence
- Added v2.6.2 changelog entry

**Design rationale — two-layer trigger architecture**:
- Layer 1 (skill activation): YAML `description` keywords → framework-level string matching → bilingual keywords help matching confidence → **keep bilingual**
- Layer 2 (mode routing): intent signals in SKILL.md → Claude's semantic reasoning → language-agnostic → **no per-language keyword lists needed**

---

### Bilingual Trigger Keywords for Socratic & Plan Mode (v2.6.1)

**Files changed**: 4 files across `deep-research/`, `academic-paper/`

**deep-research** (2 files):
- `SKILL.md`: Added Traditional Chinese (繁體中文) trigger keywords to YAML description, general Trigger Keywords section, and Socratic Mode Trigger Keywords section (6 Chinese keyword groups with variants). Added Chinese Quick Start examples. Quick Mode Selection Guide now bilingual.
- `references/mode_selection_guide.md`: Added Chinese trigger examples for socratic mode (5 examples). Common misselection table now bilingual.

**academic-paper** (2 files):
- `SKILL.md`: Added Traditional Chinese trigger keywords to YAML description and general Trigger Keywords section. **New section: Plan Mode Trigger Keywords** — English (5) + Chinese (7 keyword groups with variants). Previously plan mode had no dedicated trigger keywords.
- `references/mode_selection_guide.md`: Common misselection table now bilingual. Added 2 Chinese-specific misselection scenarios (「帶我寫論文」→ plan mode, 「第一次寫論文」→ plan mode).

**Motivation**: Original skills were designed in Chinese, then translated to English. After translation, trigger keywords were English-only, causing Socratic/Plan mode to fail to activate when users prompted in Chinese (defaulting to `full` mode instead).

---

## 2026-03-08

### Academic Skills Suite v2.6 — 15 Improvements Across 4 Skills

**Files changed**: 30 files (17 new, 13 modified) across `deep-research/`, `academic-paper/`, `academic-paper-reviewer/`, `academic-pipeline/`, `shared/`

**deep-research v2.3** (+7 new files, 3 modified):
- New systematic-review / PRISMA mode (7th mode) with 3 new agents: `risk_of_bias_agent` (RoB 2 + ROBINS-I), `meta_analysis_agent` (effect sizes, heterogeneity, GRADE), `monitoring_agent` (post-pipeline literature alerts)
- New references: `systematic_review_toolkit.md`, `literature_monitoring_strategies.md`
- New templates: `prisma_protocol_template.md`, `prisma_report_template.md`
- Enhanced `socratic_mentor_agent`: 4 convergence signals, question taxonomy, auto-end triggers
- Quick Mode Selection Guide added to SKILL.md

**academic-paper v2.3** (+4 new files, 3 modified):
- New agents: `visualization_agent` (11th, 9 chart types, APA 7.0 standards), `revision_coach_agent` (12th, parses unstructured reviewer comments)
- New reference: `statistical_visualization_standards.md` (chart decision tree, accessible palettes)
- New template: `revision_tracking_template.md` (4 status types: RESOLVED, DELIBERATE_LIMITATION, UNRESOLVABLE, REVIEWER_DISAGREE)
- New example: `revision_recovery_example.md` (Major Revision → revision tracking → Accept)
- Enhanced `formatter_agent`: citation format conversion (APA↔Chicago↔MLA↔IEEE↔Vancouver)
- Enhanced `socratic_mentor_agent`: 4 convergence criteria, question taxonomy
- Quick Mode Selection Guide added to SKILL.md

**academic-paper-reviewer v1.4** (+1 new file, 2 modified):
- New reference: `quality_rubrics.md` (5 dimensions scored 0-100 with behavioral indicators)
- Decision mapping: ≥80 Accept, 65-79 Minor, 50-64 Major, <50 Reject
- Updated `peer_review_report_template.md` to use 0-100 scoring referencing rubrics
- Quick Mode Selection Guide added to SKILL.md

**academic-pipeline v2.6** (+3 new files, 4 modified):
- Adaptive checkpoint system: FULL (first use/critical), SLIM (returning user), MANDATORY (integrity gates)
- Phase E Claim Verification protocol in integrity checks (E1 claim extraction, E2 source cross-reference, E3 verdict)
- Material Passport for mid-entry provenance tracking (stage-skip eligibility, freshness rules)
- New references: `mode_advisor.md` (14 scenarios, user archetypes, anti-patterns), `team_collaboration_protocol.md` (5 roles, handoff procedures, conflict resolution), `claim_verification_protocol.md` (Phase E protocol with 5 verdict types)
- New example: `integrity_failure_recovery.md` (Stage 2.5 FAIL → corrections → PASS)
- Enhanced `shared/handoff_schemas.md`: 9 comprehensive schemas with validation rules
- Enhanced orchestrator and state tracker agents for schema validation and adaptive checkpoints

---

### Full English Translation — All Skills Translated to English

**Files changed**: All `.md` files across `academic-pipeline/`, `academic-paper/`, `academic-paper-reviewer/`, `deep-research/`

**Changes**:
- Translated all Chinese content to English across 68+ files (agents, references, templates, examples, SKILL.md)
- TSSCI journal names in `top_journals_by_field.md` retain official Chinese names as proper nouns (with English translations)
- Privacy scan: removed residual `HEEACT Luminai` reference from `deep-research/references/socratic_questioning_framework.md`
- `README.zh-TW.md` intentionally kept in Chinese as the bilingual README option

---

### academic-pipeline v2.5 — External Review Protocol

**Files changed**: `academic-pipeline/SKILL.md`

**Changes**:
- New External Review Protocol section: 4-step workflow for handling real journal reviewer feedback (intake → strategic coaching → revise + Response to Reviewers → completeness check)
- Difference table: internal simulated review vs. external real review
- Strategic Revision Coaching: 4 layers (understanding → judgment → strategy → risk assessment)
- Response to Reviewers auto-generated template
- Self-verification completeness check adjustments
- Capability boundaries: AI verification ≠ real reviewer satisfaction

---

### academic-pipeline v2.4 — Stage 6 Process Summary + Collaboration Quality Evaluation

**Files changed**: `academic-pipeline/SKILL.md`, `README.md`, `README.zh-TW.md`

**academic-pipeline v2.4**:
- New Stage 6 PROCESS SUMMARY: auto-generates structured paper creation process record after pipeline completion
- Asks user preferred language (zh/en/both), generates MD → LaTeX → PDF
- Mandatory final chapter: **Collaboration Quality Evaluation** — 6 dimensions scored 1–100:
  - Direction Setting, Intellectual Contribution, Quality Gatekeeping
  - Iteration Discipline, Delegation Efficiency, Meta-Learning
- Includes: What Worked Well, Missed Opportunities, Recommendations, Human vs AI Value-Add, Claude's Self-Reflection
- Pipeline expanded from 9 to 10 stages (state machine, dashboard, audit trail updated)
- Scoring rubric: 90-100 Exceptional / 75-89 Excellent / 60-74 Good / 40-59 Basic / 1-39 Needs Improvement

**Lesson**: pandoc's newer longtable output uses `\real{}` macro which requires `\usepackage{calc}` in the LaTeX wrapper

---

### academic-pipeline v2.3 — APA 7.0 Formatting & LaTeX-to-PDF

**Files changed**: `academic-pipeline/SKILL.md`, `README.md`, `README.zh-TW.md`

**academic-pipeline v2.3**:
- Stage 5 FINALIZE now prompts user for formatting style (APA 7.0 / Chicago / IEEE) before generating LaTeX
- PDF must compile from LaTeX via `tectonic` (no HTML-to-PDF conversion allowed)
- APA 7.0 uses `apa7` document class (`man` mode) with `natbib` option (no biber required)
- XeCJK for bilingual CJK support; font stack: Times New Roman + Source Han Serif TC VF + Courier New
- Known apa7 quirks documented: `noextraspace` removed in v2.15, pandoc `\LTcaptype{none}` needs `\newcounter{none}`, `\addORCIDlink` takes ID only (not full URL)

**README updates**:
- Added Performance Notes section: recommended model Claude Opus 4.7 with Max plan; large token consumption warning
- Updated pipeline stage 5 description in both EN and zh-TW READMEs

**Lesson**: Always ask the user which academic formatting style they want (APA 7.0, Chicago, IEEE, etc.) before generating the final PDF — formatting style is a separate concern from citation style

---

## 2025-03-05

### v2.2 / v1.3 Cross-Agent Quality Alignment Update (4 skills)

**Files changed**: 19 files across 4 skills (+550 lines)

**deep-research v2.2**:
- Added cross-agent quality alignment definitions (peer-reviewed, currency rule, CRITICAL severity, source tier, minimum source count, verification threshold)
- Synthesis anti-patterns, Socratic quantified thresholds & auto-end conditions
- Reference existence verification (DOI + WebSearch)
- Enhanced ethics reference integrity check (50% + Retraction Watch)
- Mode transition matrix

**academic-paper v2.2**:
- 4-level argument strength scoring with quantified thresholds
- Plagiarism & retraction screening protocol
- F11 Desk-Reject Recovery + F12 Conference-to-Journal Conversion failure paths
- Plan → Full mode conversion protocol

**academic-paper-reviewer v1.3**:
- DA vs R3 role boundaries with explicit responsibility tables
- CRITICAL finding criteria with concrete examples
- Consensus classification (CONSENSUS-4/3/SPLIT/DA-CRITICAL)
- Confidence Score weighting rules
- Asian & Regional Journals reference (TSSCI + Asia-Pacific + OA options)

**academic-pipeline v2.2**:
- Checkpoint confirmation semantics (6 user commands with precise actions)
- Mode switching rules (safe/dangerous/prohibited matrix)
- Skill failure fallback matrix (per-stage degradation strategies)
- State ownership protocol (single source of truth with write access control)
- Material version control (versioned artifacts with audit trail)

---

## 2026-03-01

### Simplify Academic Research Skills SKILL.md (4 files)

**Motivation**: 4 academic research skills totaled 2,254 lines with significant cross-skill duplication and redundant inline content already available as template files.

**Files changed**:
- `academic-paper-reviewer/SKILL.md` (570→470, -100 lines)
- `academic-pipeline/SKILL.md` (675→535, -140 lines)
- `deep-research/SKILL.md` (469→435, -34 lines)
- `academic-paper/SKILL.md` (540→443, -97 lines)

**Changes**:
- A: Reviewer — removed inline templates, replaced with `templates/` file references (kept Devil's Advocate special format notes)
- B: Pipeline — removed ASCII state machine, replaced with concise 9-stage list + reference
- C: Pipeline — simplified Two-Stage Review Protocol to inputs/outputs/branching only
- D: 3 skills — "Full Academic Pipeline" section replaced with one-line reference to `academic-pipeline/SKILL.md`
- E: 4 skills — trimmed routing tables, removed HEI routes already defined in root CLAUDE.md
- F+G: Removed duplicate Mode Selection sections from deep-research and academic-paper
- H: academic-paper Handoff Protocol simplified to overview + upstream reference
- I: academic-paper Phase 0 Config replaced with reference to `agents/intake_agent.md`
- J: 4 skills — Output Language sections reduced to 1 line each
- K: Fixed revision loop cap contradiction (pipeline overrides academic-paper's max 2 rule)

**Result**: 2,254→1,883 lines (-371 lines, -16.5%), all 371 quality tests passed

**Lesson**: Inlining full template content in SKILL.md is unnecessary redundancy — a one-line reference suffices when template files exist at the correct path
