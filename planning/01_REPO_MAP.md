# 01 — REPO_MAP
## academic-research-skills: Structural Map & Tech Stack

**Repo:** `Imbad0202/academic-research-skills`
**Current HEAD:** `v3.9.4.2` (2026-05-19)
**License:** CC BY-NC 4.0
**Primary Language:** Markdown (Claude Code skill definitions) + Python (validation/lint scripts) + YAML (schemas)

---

## What It Does

A **Claude Code plugin suite** (4 skills, 25 modes) that automates the academic research pipeline from research question to published paper. It coordinates a multi-agent team across 10 stages with integrity gates, claim-faithfulness auditing, and peer review simulation. The core premise: human-AI collaboration avoids AI-only failure modes better than either alone.

**Skills (in `skills/`):**
| Skill | Dir | Version | Modes | Data Access |
|-------|-----|---------|-------|-------------|
| `deep-research` | `skills/deep-research/` | 2.9.4 | 7 (full/quick/review/lit-review/fact-check/socratic/systematic-review) | raw |
| `academic-paper` | `skills/academic-paper/` | 3.1.2 | 10 (full/plan/outline-only/revision/revision-coach/abstract-only/lit-review/format-convert/citation-check/disclosure) | redacted |
| `academic-paper-reviewer` | `skills/academic-paper-reviewer/` | 1.9.1 | 6 (full/re-review/quick/methodology-focus/guided/calibration) | verified_only |
| `academic-pipeline` | `skills/academic-pipeline/` | 3.9.4.2 | 1 orchestrator + resume | verified_only |

**Plugin commands (in `commands/`):** 13 `/ars-*` slash commands (abstract, citation-check, disclosure, format-convert, full, lit-review, mark-read, outline, plan, reviewer, revision-coach, revision, unmark-read).

**Agents (13 per skill subdirectory):** Each skill has its own `agents/` dir with named agent prompts (`.md` files).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Skill Definition | Markdown with YAML frontmatter (`SKILL.md`) |
| Agent Prompts | Markdown (`.md` files in `*/agents/`) |
| Validation Scripts | Python 3 (70+ scripts in `scripts/`) |
| Schemas | JSON (`*.schema.json`) + YAML |
| CI/CD | GitHub Actions (11 workflow files in `.github/workflows/`) |
| Testing | pytest (400+ tests across `tests/` + inline `test_*.py` in `scripts/`) |
| Plugin Packaging | `.claude-plugin/plugin.json` + `marketplace.json` |
| Session Hooks | Bash (`hooks/hooks.json` + `scripts/announce-ars-loaded.sh`) |

**Key Python modules in `scripts/`:**
- `check_spec_consistency.py` — README/CHANGELOG/ARCHITECTURE drift detection
- `check_version_consistency.py` — semver consistency across frontmatter
- `check_claim_audit_consistency.py` — claim audit schema validation
- `check_pipeline_integrity.py` — detects phase scope inflation (#133)
- `check_sprint_contract.py` — Schema 13 sprint contract enforcement
- `temporal_integrity_audit.py` — 5-pass temporal failure mode detector
- `claim_audit_pipeline.py` — L3 claim-faithfulness audit runner
- `migrate_literature_corpus_to_v3_9_0.py` — cross-index triangulation backfill
- Semantic Scholar / OpenAlex / Crossref API clients (`*_client.py`)

---

## Directory Structure

```
academic-research-skills/
├── .claude/              # CLAUDE.md routing rules
├── .claude-plugin/       # Plugin manifest + marketplace metadata
├── .github/workflows/   # 11 CI workflows
├── academic-paper/       # Skill: 12-agent paper writing
│   ├── SKILL.md
│   ├── agents/           # 12 named agent prompts
│   ├── references/       # Domain knowledge (journal lists, writing guides)
│   ├── examples/        # Sample outputs
│   └── templates/       # Output templates
├── academic-paper-reviewer/ # Skill: 7-agent peer review simulation
│   ├── SKILL.md
│   ├── agents/          # 7 named agents (EIC + 3 reviewers + DA + synthesizer + ...)
│   ├── references/
│   ├── examples/
│   └── templates/
├── academic-pipeline/   # Orchestrator: 10-stage pipeline
│   ├── SKILL.md
│   ├── agents/          # orchestrator + claim_ref_alignment_audit_agent + collaboration_depth_agent
│   ├── references/      # pipeline protocols, literature corpus consumer guide
│   └── examples/
├── deep-research/       # Skill: 13-agent research team
│   ├── SKILL.md
│   ├── agents/          # 13 named agents (Socratic mentor, bibliography, synthesis, ...)
│   ├── references/      # API protocols (OpenAlex, Crossref), bias assessment
│   └── examples/
├── commands/            # 13 /ars-* plugin command definitions
├── docs/                # ARCHITECTURE.md, SETUP.md, PERFORMANCE.md
│   ├── design/          # 30+ design docs (v3.4–v3.9 specs)
│   └── migration/       # Schema migration tools
├── hooks/               # SessionStart hook for plugin announce
├── scripts/             # 70+ Python validation/lint/test scripts
├── shared/              # Cross-skill: schemas, templates, patterns, rubric
│   ├── contracts/       # Sprint contract templates (reviewer/writer/evaluator)
│   ├── references/      # Pattern docs (IRB glossary, hedging phrases, ...)
│   ├── templates/       # Codex audit template
│   └── *_pattern.md     # Design patterns (ground_truth_isolation, benchmark, repro_lock, ...)
├── skills/              # Symlinks to the 4 skill dirs above
├── tests/               # pytest fixtures + e2e tests
├── examples/showcase/   # Real pipeline run artifacts (PDFs)
├── CHANGELOG.md        # 141KB, v2.8 → v3.9.4.2
├── MODE_REGISTRY.md    # Single source of truth for all 25 modes
├── POSITIONING.md      # Market/competitor positioning
├── QUICKSTART.md
├── CONTRIBUTING.md
├── SECURITY.md
├── NOTICE.md
├── README.md (+ .zh-CN, .zh-TW, .ja-JP)
└── requirements-dev.txt
```

---

## v3.9 → v3.10 Known Roadmap

From multiple `defer:v3.10` labels and README v3.10 references:

| Issue | Description | Blocker for |
|-------|-------------|-------------|
| #134 | Active Conductor Architecture — replace passive routing with intent-aware controller | v3.10 |
| #182 | Add deterministic citation verification gate | #198 |
| #183 | Add mandatory epistemic_status field | #198 |
| #184 | Build local gold set + lift gate on ranking changes | #198 |
| #160 | Refactor `scripts/_test_helpers.py` → `tests/test_helpers.py` | v3.10 |
| #151 | Generic repo hygiene CI (gitleaks, etc.) | v3.10 |
| #197 | Fix prose-only arg passing in commands (add `$ARGUMENTS` substitution) | Unlabeled |

**v3.10 policy layer** (deferred from v3.9.0): `venue_type` + `triangulation_policy` hard-block tier for contamination signals.

---

## README Translations

| File | Content |
|------|---------|
| `README.md` | English (canonical) |
| `README.zh-CN.md` | Simplified Chinese (translator: xpfo-go, PR #181) |
| `README.zh-TW.md` | Traditional Chinese (canonical) |
| `README.ja-JP.md` | Japanese (translator: eltociear, PR #161) |

---

## Key Contacts

- **Author:** Cheng-I Wu (吳政宜) — `Imbad0202`
- **Contributors:** aspi6246, mchesbro1, cloudenochcsis, eltociear, xpfo-go
- **Sponsor:** Buy Me a Coffee (link in README)