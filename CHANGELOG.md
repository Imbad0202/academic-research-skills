# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [3.6.5] - 2026-04-27

### Added

- Material Passport `literature_corpus[]` consumer integration in Phase 1
  (deep-research/bibliography_agent + academic-paper/literature_strategist_agent).
  Corpus-first, search-fills-gap flow with PRE-SCREENED reproducibility block.
  Reproducibility for systematic-review use is preserved through Iron Rule 1
  same-criteria parity plus Step 2 case C (standard external search runs even
  when corpus fully covers RQ subtopics).
- `academic-pipeline/references/literature_corpus_consumers.md` — consumer protocol
  reference with four Iron Rules (Same criteria / No silent skip / No corpus mutation /
  Graceful fallback on parse failure) and per-consumer reading instructions.
- `scripts/check_corpus_consumer_protocol.py` — CI lint enforcing nine protocol invariants
  with manifest-driven consumer list and stub-block opt-out.
- `scripts/corpus_consumer_manifest.json` — supported-consumer manifest.

### Changed

- `shared/handoff_schemas.md` Schema 9 — retired the v3.6.4 "Consumer-side integration
  deferred to v3.6.5+" caveat; replaced with backpointer to the consumer protocol.
- `deep-research/SKILL.md` 2.9.1 → 2.9.2 — bibliography_agent corpus-first flow (also
  syncs Version Info footer that lagged at 2.9.0).
- `academic-paper/SKILL.md` 3.1.0 → 3.1.1 — literature_strategist_agent corpus-first flow.
- `academic-pipeline/SKILL.md` 3.6.4 → 3.6.5 — suite version invariant.
- `.claude/CLAUDE.md`, `MODE_REGISTRY.md`, `README.md`, `README.zh-TW.md`,
  `scripts/check_spec_consistency.py` updated for the version bump (suite version,
  badge, tag, changelog heading).

### Notes

- Consumer integration is presence-based: auto-engages when passport carries a
  non-empty `literature_corpus[]` and parses cleanly. Parse failures fall back
  to external-DB-only flow with a `[CORPUS PARSE FAILURE]` surface. No new env
  flag introduced.
- Schema is unchanged from v3.6.4. Existing user adapters work without modification.
- `citation_compliance_agent` corpus integration deferred to v3.6.6+.
- `source_pointer` is not dereferenced by consumers; URI resolution remains a future
  `source_verification_agent` concern.

## [3.6.4] - 2026-04-25

### Added

- **Material Passport `literature_corpus[]` input port**. Schema 9 gains an optional `literature_corpus[]` field defined by `shared/contracts/passport/literature_corpus_entry.schema.json`. Each entry carries `citation_key`, CSL-JSON `authors`, `year`, `title`, and a `source_pointer` back to the user's own KB. `abstract` and `user_notes` are private optional fields with copyright caveats.
- **Adapter contract** (`academic-pipeline/references/adapters/overview.md`): language-neutral specification for producing literature_corpus entries from user-owned corpus sources. Covers fail-soft entry-level error handling, mandatory `rejection_log.yaml` output, deterministic ordering (sort by `citation_key` / `source`), and extension points for user-written adapters.
- **Three reference Python adapters** (`scripts/adapters/`): `folder_scan.py` (filesystem of PDFs), `zotero.py` (Better BibTeX JSON export), `obsidian.py` (vault frontmatter, BibTeX-style or literature-note convention). Each ships with pytest tests, fixtures, and golden expected outputs.
- **Rejection log contract** (`shared/contracts/passport/rejection_log.schema.json`). Always emitted; empty when no rejections; closed enum of categorical reason values.
- **CI lint + pytest job**: `scripts/check_literature_corpus_schema.py` (schema + adapter example validation), `scripts/sync_adapter_docs.py --check` (schema→docs drift detector with auto-regen mode), and a new `.github/workflows/pytest.yml` running `scripts/adapters/tests/` on path-filtered triggers.
- `_common.ensure_unique_citekey(key, existing)` helper for adapters whose source already supplies a citekey (zotero, obsidian frontmatter), with sanitization to satisfy the schema pattern and a/b/...zz alpha-suffix collision disambiguation.
- `_common.path_to_file_uri(path)` helper that delegates to `Path.as_uri()` so spaces and reserved characters in filenames are properly percent-encoded.

### Changed

- `academic-pipeline/references/passport_as_reset_boundary.md`: "deferred to v3.6.4, PR-B" placeholders replaced with forward references to `adapters/overview.md` and `literature_corpus_entry.schema.json`.
- `shared/handoff_schemas.md`: Schema 9 optional fields table adds `literature_corpus`; new "Literature Corpus Input Port (v3.6.4)" subsection appended after Reset Boundary Extension.
- `academic-pipeline/SKILL.md` bumped 3.6.3 → 3.6.4 (suite version invariant). Other skills retain independent semver.
- `.claude/CLAUDE.md`, `MODE_REGISTRY.md`, `README.md`, `README.zh-TW.md`, `scripts/check_spec_consistency.py` updated for the version bump (suite version, badge, tag, changelog heading).

### Not changed (explicit non-goals)

- No ARS agent consumes `literature_corpus[]` yet. Consumer-side integration is deferred to v3.6.5+. v3.6.4 defines the input port only.
- No PDF parsing, no text extraction, no live API clients, no authenticated library crawling. The reference adapters read filenames or local export files and never make network calls.

## [3.6.3] - 2026-04-23

### Added
- **Opt-in passport reset boundary** via `ARS_PASSPORT_RESET=1`. Every FULL checkpoint becomes a context-reset boundary when the flag is set. `systematic-review` mode with the flag ON makes reset mandatory; other modes treat reset as the flag-gated default.
- **`resume_from_passport=<hash>` mode** in `academic-pipeline`. Lets users resume a pipeline run in a fresh Claude Code session from the Material Passport ledger alone.
- **Schema 9 `reset_boundary[]`** optional append-only field with two entry kinds (`boundary`, `resume`). Entry shape in `shared/contracts/passport/reset_ledger_entry.schema.json` (oneOf split with `kind` discriminator). Hash computed via JSON Canonical Form + SHA-256 with `"000000000000"` placeholder for self-reference safety. Optional `pending_decision` field handles MANDATORY branch choices (Stage 3 reject/restructure/abort, Stage 5 finalization) that survive the reset boundary.
- **Protocol doc:** `academic-pipeline/references/passport_as_reset_boundary.md` (authoritative; every file mentioning `ARS_PASSPORT_RESET` must co-locate a reference).
- **CI lint:** `scripts/check_passport_reset_contract.py` + unittest suite. Wired into `.github/workflows/spec-consistency.yml`.
- **`docs/PERFORMANCE.md` + `docs/PERFORMANCE.zh-TW.md`** long-running-session subsection documenting when reset beats continuation, passport file-location convention, and empirical-measurement disclaimer.

### Changed
- `academic-pipeline/agents/pipeline_orchestrator_agent.md` adds §"Passport Reset Boundary (v3.6.3+)" and §"Resume Mode: `resume_from_passport`". FULL Checkpoint Template includes conditional reset-handoff tag slot.
- `academic-pipeline/references/pipeline_state_machine.md` documents `awaiting_resume` transitions derived from the ledger (no out-of-band state).
- `academic-pipeline/SKILL.md` adds `resume_from_passport` to the mode table and bumps version 3.6.2 → 3.6.3.
- `shared/handoff_schemas.md` Schema 9 gains `reset_boundary` row + "Reset Boundary Extension (v3.6.3)" subsection with full YAML example showing both kinds.

### Changed (post-P1 fixes)
- `pending_decision.options[]` now carries per-branch routing (`{value, next_stage, next_mode}`); `value` uniqueness within one options array is enforced by CI lint (`scripts/check_passport_reset_contract.py`). The matched option's `next_stage` supersedes the boundary entry's advisory `next` field. `next` MAY be `null` when all branches terminate or no sensible default exists.
- Exclusive advisory lock (POSIX `fcntl.flock LOCK_EX`, bounded timeout not exceeding 60 s, 30 s recommended) is required for the resume read-check-append sequence. Non-POSIX implementations MUST refuse to resume rather than degrade silently.

### Notes
- **Flag OFF is the default.** Pre-v3.6.3 behavior is preserved byte-for-byte when `ARS_PASSPORT_RESET` is unset or `=0`.
- Out of scope (deferred to v3.6.4): `examples/adapters/{folder_scan, zotero, obsidian}/` reference adapters and the `literature_corpus` entry shape on Schema 9.
- No breaking changes. No existing mode behavior changes when the flag is OFF.

## [3.6.2] - 2026-04-23

### Added

- **Sprint Contract (Schema 13) — reviewer hard gate.** `shared/sprint_contract.schema.json` defines machine-checkable acceptance criteria (`panel_size`, `acceptance_dimensions`, `failure_conditions` with `severity` + `cross_reviewer_quantifier`, `measurement_procedure`, optional `override_ladder`, bounded `agent_amendments`). Validator `scripts/check_sprint_contract.py` (schema validation + `check_structural_invariants()` hard check + nine soft warnings SC-1..SC-11 with SC-6 documented as dead path and SC-8 promoted to hard check). Two templates ship: `shared/contracts/reviewer/full.json` (panel 5) and `shared/contracts/reviewer/methodology_focus.json` (panel 2). Reviewer orchestration reshaped into paper-content-blind Phase 1 + paper-visible Phase 2 hard gate. Synthesizer runs three-step mechanical protocol (build matrix → evaluate with quantifier → resolve precedence). See `docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md`.
- **Token cost note.** Reviewer total calls under sprint contract = `2 × panel_size`. For `reviewer_full`: 5 → 10 calls. Phase 1 input is metadata-only and output short, so real token bound is well below 2x.

### Changed

- **`academic-paper-reviewer` v1.8.1 → v1.9.0.** Five reviewer agent markdown files (EIC + methodology + domain + perspective + DA) gain Phase 1/2 protocol sections; `editorial_synthesizer_agent.md` gains the three-step synthesizer protocol + forbidden-operations list.
- **Harness retirement notes folded in.** The prior `[Unreleased]` harness-retirement pass (Task A per `project_ars_v3.6_execution_order.md`) ships with this release — 7 negative-framing blocks rewritten to positive / split form across 7 files, no behaviour change:
  - `academic-paper/agents/socratic_mentor_agent.md` — Core Principles items 1, 6 (F-001)
  - `deep-research/agents/socratic_mentor_agent.md` — Quality Standards items 2, 3, 4 (F-002)
  - `academic-paper/agents/draft_writer_agent.md` — quick style check, paragraph variation, colloquialisms, transition-word usage (F-003, 4 spots)
  - `academic-pipeline/agents/pipeline_orchestrator_agent.md` — **split** "Prohibited Actions" (9 items, all negative) into "Scope (delegate, don't perform)" (items 1-6, positive delegation) + "Hard boundaries (never violate)" (items 7-9, kept negative as intentional safety directives for silent-failure modes: fabrication, skipped checkpoints, skipped integrity gates) (F-004)
  - `academic-pipeline/agents/collaboration_depth_agent.md` — Agent-specific boundaries 4 bullets (F-005)
  - `academic-pipeline/SKILL.md` — single-line UX guidance (F-006)
  - `academic-paper/references/academic_writing_style.md` — §4 Formality 3 items (F-007, discovered during apply)

### Notes

- `reviewer_re_review`, `reviewer_calibration`, `reviewer_guided` are reserved in the Schema 13 `mode` enum but ship without contract templates in v3.6.2. Those modes continue pre-v3.6.2 behaviour until a follow-up patch adds their templates.
- `reviewer_quick` is intentionally excluded from the Schema 13 `mode` enum (Q3-A' boundary).
- CI gate: `validate-sprint-contracts` step in `.github/workflows/spec-consistency.yml` runs the full unit test suite and validates every template under `shared/contracts/reviewer/*.json` against the current ARS version.
- Kept-as-debt from harness retirement: ~50 anti-hallucination references across `deep-research/`, `academic-paper/references/anti_leakage_protocol.md`, `academic-pipeline/references/ai_research_failure_modes.md`, `shared/agents/compliance_agent.md`, `shared/compliance_checkpoint_protocol.md` — load-bearing integrity architecture (Lu 2026 7-mode; S2 API Tier-0; `[MATERIAL GAP]` taxonomy). Not retired under the iron rule clause for silent-failure domains.

## [3.5.1] - 2026-04-22

### Added

- **Opt-in Socratic reading-check probe.** When `ARS_SOCRATIC_READING_PROBE=1` is set, the Socratic Mentor fires a one-time honesty probe during goal-oriented sessions where the user has cited a specific paper. The probe asks the user to paraphrase one passage. Decline is logged without penalty. Outcome is recorded in the Research Plan Summary and flows into the Stage 6 AI Self-Reflection Report when the pipeline continues. Default OFF. Roadmap slot: v3.7.3. See `deep-research/agents/socratic_mentor_agent.md` §"Optional Reading Probe Layer".

### Changed

- `deep-research/SKILL.md`, `deep-research/references/socratic_mode_protocol.md`, `academic-pipeline/references/process_summary_protocol.md` — aligned text updates for the new probe section. No behaviour change when the env var is unset.

### Version

- Suite: 3.5.0 → 3.5.1 (patch; opt-in, default OFF, no breaking change)
- `deep-research` skill: 2.9.0 → 2.9.1
- `academic-pipeline` skill: 3.5.0 → 3.5.1 (tracks suite version per `check_version_consistency.py` invariant)

## [3.5.0] - 2026-04-21

### Added
- `shared/collaboration_depth_rubric.md` v1.0 — canonical 4-dimension rubric (Delegation Intensity, Cognitive Vigilance, Cognitive Reallocation, Zone Classification). Based on Wang, S., & Zhang, H. (2026). "Pedagogical partnerships with generative AI in higher education: how dual cognitive pathways paradoxically enable transformative learning." *International Journal of Educational Technology in Higher Education*, 23:11. DOI 10.1186/s41239-026-00585-x. Licensed CC-BY-NC 4.0.
- `academic-pipeline/agents/collaboration_depth_agent.md` — observer agent (Agent Team grows 3 → 4). Invoked at every FULL/SLIM checkpoint and at pipeline completion; scores user-AI collaboration pattern against the canonical rubric. **Advisory only — never blocks progression.** Frontmatter declares `blocking: false`, `measures: collaboration_depth`, `rubric_ref: shared/collaboration_depth_rubric.md`.
- `scripts/check_collaboration_depth_rubric.py` + `scripts/test_check_collaboration_depth_rubric.py` — new lint enforces: (1) rubric file exists; (2) rubric cites Wang & Zhang 2026 with DOI; (3) `rubric_version` frontmatter field; (4) four canonical dimension headings; (5)/(6) any agent claiming `measures: collaboration_depth` references the canonical rubric path and declares `blocking: false`; (7)/(8) orchestrator and SKILL.md mention observer with non-blocking semantics. 10 unit tests, all green.
- `academic-pipeline/references/changelog.md` row v2.8.
- `academic-pipeline/references/reinforcement_content.md` row for FULL/SLIM checkpoint — IRON RULE: observer is advisory only, never blocks, never a leaderboard.

### Changed
- `academic-pipeline/SKILL.md` — version bump `3.3.0 → 3.4.0`. Agent Team table grows to 4 rows. New "Collaboration Depth Observer" section with explicit non-blocking guarantees and distinction from integrity verification and Stage 6 self-reflection. Reference Files table adds rubric entry.
- `academic-pipeline/agents/pipeline_orchestrator_agent.md` — checkpoint Steps flow amended: after `state_tracker` update the orchestrator invokes `collaboration_depth_agent` on the just-completed stage's dialogue range (FULL/SLIM only; MANDATORY integrity gates explicitly skip) and injects its output into checkpoint templates as a named "Collaboration Depth" section. FULL checkpoint template expanded with the observer block; SLIM template gains a one-line compact observer summary; MANDATORY template unchanged (integrity gates never dilute). New "Collaboration Depth Observer" subsection under §3 Checkpoint Management covers invocation, cross-model behaviour, short-stage guard, and non-blocking IRON RULE.
- `academic-pipeline/agents/state_tracker_agent.md` — Write Access Control adds `collaboration_depth_agent` (append-only `collaboration_depth_history[]`). New `dialogue_log_ref` turn-range pointer per stage; new `collaboration_depth_history[]` root-level array; new `append_observer_report()` function (only function that writes the history; preconditions block any attempt to turn observer output into a blocking condition).
- `scripts/_skill_lint.py` — new shared `split_frontmatter(text) -> (dict|None, str)` lenient helper, reused by the new lint.
- Suite version bumped to `3.5.0` across `README.md`, `README.zh-TW.md`, `MODE_REGISTRY.md`, `.claude/CLAUDE.md`; new `### v3.5.0 (2026-04-21)` section in both READMEs; new `## v3.5 Key Additions` block in `.claude/CLAUDE.md`.
- `scripts/check_spec_consistency.py` — README version expectations bumped to `v3.5.0`; `MODE_REGISTRY.md` last-updated expectation updated; `.claude/CLAUDE.md` suite version expectation updated. New embedded-changelog regression checks for `### v3.5.0 (2026-04-21)` entries.

### Notes
- MANDATORY integrity checkpoints (Stages 2.5, 4.5) are **not** instrumented by the observer. The observer never appears in the "Flagged" line of any checkpoint. `blocked_by: collaboration_depth_agent` is never a legal state. The orchestrator's numbered Step 3 explicitly branches on checkpoint_type.
- Cross-model behaviour (`ARS_CROSS_MODEL`): observer runs on both models; dimension disagreement > 2 points is flagged explicitly, never silently averaged. `ARS_CROSS_MODEL_SAMPLE_INTERVAL` escape hatch documented.
- Short-stage guard: if the completed stage has fewer than 5 user turns, a static `insufficient_evidence` block is injected and the full-model observer call is skipped.
- Credit: Wang & Zhang (2026) introduced the dual-pathway SEM and three-zone (Zone 1 / Zone 2 / Zone 3) framework that anchors the rubric's dimension operationalisation and synthesis rule.

## [3.4.0] - 2026-04-20

### Added

- `shared/agents/compliance_agent.md` — single mode-aware agent for PRISMA-trAIce + RAISE compliance. Dispatches on `compliance_mode ∈ {systematic_review, primary_research, other_evidence_synthesis}`. See design spec `docs/design/2026-04-20-v3.4-prisma-trAIce-raise-readcheck-design.md`.
- `shared/prisma_trAIce_protocol.md` — verbatim 17-item snapshot from `cqh4046/PRISMA-trAIce` (2025-12-10) + per-item ARS check procedure + 4-tier behaviour table. Citation: Holst et al. 2025, JMIR AI, doi:10.2196/80247.
- `shared/raise_framework.md` — 4 principles (human oversight / transparency / reproducibility / fit-for-purpose) + 8-role matrix + mandatory scope disclaimer. Citation: Thomas et al. 2025, NIHR ESG Best Practice Working Group, 17 July 2025.
- `shared/compliance_checkpoint_protocol.md` — Stage 2.5 / 4.5 dual-gate behaviour spec, decision precedence, override ladder, fail-loop integration, boundary behaviour for non-pipeline invocation.
- `shared/compliance_report.schema.json` — Schema 12 validator (Draft 2020-12).
- `examples/compliance/fixture_sr_full_compliant.yaml`, `fixture_sr_missing_M4.yaml`, `fixture_primary_raise_weak.yaml` — regression fixtures + user reference templates.
- `scripts/check_compliance_report.py` + tests — Schema 12 CLI validator.
- `scripts/validate_compliance_fixtures.py` + tests — YAML→JSON fixture loop used by CI.
- `scripts/check_prisma_trAIce_freshness.py` + tests — non-blocking upstream-drift warning (180-day threshold).
- `.github/workflows/freshness-check.yml` — weekly cron (Monday 09:00 UTC) + path-filtered push trigger for freshness check.
- `docs/PERFORMANCE.md` + `.zh-TW.md`: new "Long-running session management" section + v3.4.0 token-cost deltas.

### Changed

- `shared/handoff_schemas.md`: Schema 12 pointer + Material Passport `compliance_history[]` (append-only audit trail).
- `academic-pipeline/SKILL.md` (v3.2.2 → v3.3.0): Stage 2.5 / 4.5 extended with compliance payload; checkpoint dashboard gains compliance row.
- `deep-research/SKILL.md` (v2.8.1 → v2.9.0): `systematic-review` mode now triggers `compliance_agent` at both gates.
- `academic-paper/SKILL.md` (v3.0.2 → v3.1.0): `full` mode adds pre-finalize RAISE principles-only check (warn-only). `disclosure` mode unchanged and complementary.
- `.github/workflows/spec-consistency.yml`: added compliance validator + unit test runner steps.
- `scripts/check_spec_consistency.py`: version pins bumped.
- `README.md`, `README.zh-TW.md`, `.claude/CLAUDE.md`, `MODE_REGISTRY.md`: suite version → 3.4.0.

### Notes

- Calibration philosophy: compliance_agent ships with transparent reporting, **no hard FNR/FPR threshold**. This is self-consistent with ARS's v3.3.2 `task_type: open-ended` truth-in-advertising annotation — publishing a hard gate would contradict the "not a benchmark task" declaration.
- Compliance Mandatory failures in SR mode are blocking, but the 3-round override ladder preserves human-in-the-loop authority. Overrides auto-inject `disclosure_addendum` into the final manuscript — no detection evasion.
- The v3.2 Failure Mode Checklist and the v3.4.0 compliance agent run in parallel at the same gates. Their scopes are non-overlapping: failure-mode checks research validity; compliance checks reporting transparency.
- Internal numbering: compliance_report is Schema 12 (not 10). Schema 10 is Style Profile (v2.7+); Schema 11 is R&R Traceability Matrix. The plan's initial Schema 10 assignment was corrected mid-branch before Task 9.

## [3.3.6] - 2026-04-15

### Added
- `docs/ARCHITECTURE.md` — single source of truth for pipeline structure (flow, stage × dimension matrix, data-access flow, skill dependency graph, quality gates, modes). Merged into main via PR #18.
- `docs/SETUP.md` + `docs/SETUP.zh-TW.md` — prerequisites, API keys, Pandoc / tectonic setup, cross-model verification (`ARS_CROSS_MODEL`), and four installation methods.
- `docs/PERFORMANCE.md` + `docs/PERFORMANCE.zh-TW.md` — per-mode token budgets, full-pipeline cost estimate, and recommended Claude Code settings (Agent Team, Ralph Loop, Skip Permissions).

### Changed
- `README.md` and `README.zh-TW.md` streamlined: removed the ASCII pipeline diagram and the 16-point key-feature list (superseded by `docs/ARCHITECTURE.md`). Setup, performance, and installation sections relocated to `docs/`. Skill Details now anchors version numbers and routes readers to ARCHITECTURE.md §3 for per-agent rosters.
- `scripts/check_spec_consistency.py` — bumped README version expectations to `v3.3.6`; DOCX contract expectations (both EN and zh-TW) moved from READMEs to the new `docs/SETUP.*` docs; added `check_setup_docs()` step.
- Suite version bumped to `3.3.6` across `README.md`, `README.zh-TW.md`, `.claude/CLAUDE.md`, and `MODE_REGISTRY.md`.

### Notes
- No functional change to any skill. Pure documentation reorganization.

## [3.3.5] - 2026-04-15

### Added
- `shared/benchmark_report.schema.json` — JSON Schema (draft-2020-12) defining required fields for ARS benchmark reports. Catches the "n=2 author-conducted baseline" failure mode from Anthropic's automated-w2s-researcher paper.
- `shared/benchmark_report_pattern.md` — narrative hub doc explaining the schema.
- `scripts/check_benchmark_report.py` + tests — validator with self-scored and small-sample warnings.
- `examples/benchmark_report_template.json` — fillable template.
- `repro_lock` optional sub-block added to Material Passport (Schema 9 in `shared/handoff_schemas.md`). Configuration lockfile; NOT a deterministic replay guarantee.
- `shared/artifact_reproducibility_pattern.md` — hub doc with mandatory "not a replay guarantee" disclaimer section and required `stochasticity_declaration` field.
- `scripts/check_repro_lock.py` + tests — passport validator.
- `examples/passport_with_repro_lock.yaml` — example.
- `requirements-dev.txt` — formal Python dev dep manifest (pyyaml + jsonschema).

### Changed
- `.github/workflows/spec-consistency.yml` installs via `pip install -r requirements-dev.txt` instead of ad-hoc `pip install`.
- `academic-pipeline/references/reproducibility_audit.md` cross-links to new artifact-reproducibility pattern.

## [3.3.4] - 2026-04-15

### Fixed
- Embedded changelog sections in `README.md` and `README.zh-TW.md` now include the missing `v3.3.3` and `v3.3.2` summaries, so the README history matches the published releases.
- `scripts/check_spec_consistency.py` now verifies that the README changelog summaries include the latest release entries, so future drift fails CI.

### Changed
- Suite version bumped to `3.3.4` across release-facing docs after the README changelog sync patch release.

## [3.3.3] - 2026-04-15

### Fixed
- `scripts/_skill_lint.py` now rejects SKILL frontmatter that is missing a closing `---` fence instead of silently treating the rest of the file as YAML.
- `scripts/_skill_lint.py` now reports a readable error when frontmatter parses as valid YAML but not as a mapping object, instead of crashing with `AttributeError`.
- Broken showcase link for the post-publication audit report corrected in both `README.md` and `README.zh-TW.md`.
- `scripts/check_spec_consistency.py` now validates README relative Markdown links so future dead links fail CI.

### Changed
- DOCX generation contract aligned across README, `academic-paper/SKILL.md`, `academic-paper/agents/formatter_agent.md`, `academic-pipeline/SKILL.md`, and `academic-pipeline/agents/pipeline_orchestrator_agent.md`: direct `.docx` output is Pandoc-dependent, with Markdown + conversion instructions as the fallback.
- Added regression tests covering missing closing fences and non-mapping YAML frontmatter in both lint test suites.
- Suite version bumped to `3.3.3` across release-facing docs; `academic-paper` patch-bumped to `3.0.2` and `academic-pipeline` patch-bumped to `3.2.2`.

## [3.3.2] - 2026-04-15

### Added
- `metadata.data_access_level` field on every top-level SKILL.md. Three-tier vocabulary (`raw` | `redacted` | `verified_only`) declaring what kind of data each skill may consume. Inspired by the three-tier isolation pattern in Anthropic's automated-w2s-researcher (2026).
  - `deep-research` = `raw`
  - `academic-paper` = `redacted`
  - `academic-paper-reviewer` = `verified_only`
  - `academic-pipeline` = `verified_only`
- `scripts/check_data_access_level.py` lint script with unit tests; wired into `.github/workflows/spec-consistency.yml`.
- Pointer section in `shared/handoff_schemas.md` documenting the vocabulary for future skill authors.
- `metadata.task_type` field on every top-level SKILL.md. Two-value vocabulary (`open-ended` | `outcome-gradable`) declaring whether the task has a scalar ground-truth metric. All current ARS skills are `open-ended` — the field is a truth-in-advertising signal that ARS targets domain-judgment work, not benchmark tasks.
- `scripts/check_task_type.py` lint script with 4 unit tests; wired into the same CI workflow.
- Pointer section in `shared/handoff_schemas.md` for the `task_type` vocabulary.
- `shared/ground_truth_isolation_pattern.md` — narrative pattern doc explaining the three-layer model behind `data_access_level` and `task_type`. Cross-references existing protocols (S2 verification, anti-leakage, integrity gates, calibration mode). Linked from `handoff_schemas.md` and `CONTRIBUTING.md`.

### Changed
- Per-skill `metadata.version` patch-bumped on all 4 SKILL.md files; `last_updated` refreshed to 2026-04-15.
- Suite version bumped to 3.3.2 across `README.md`, `README.zh-TW.md`, and `.claude/CLAUDE.md`.

## [3.3.1] - 2026-04-14

### Fixed
- Public contract drift across `README.md`, `README.zh-TW.md`, `.claude/CLAUDE.md`, `MODE_REGISTRY.md`, and the affected `SKILL.md` files
- Cross-model wording now matches the implemented scope: integrity sample verification and independent DA critique are shipped; sixth-reviewer peer review remains planned
- `academic-pipeline` checkpoint docs now state that SLIM checkpoints still wait for explicit user confirmation
- `academic-pipeline` integrity gate docs now consistently state that Stage 2.5 and Stage 4.5 cannot be skipped
- `academic-paper/SKILL.md` mode-count heading and `academic-paper-reviewer/SKILL.md` Version Info block

### Added
- `scripts/check_spec_consistency.py` to catch mode-count, version-block, and forbidden-claim drift
- `.github/workflows/spec-consistency.yml` to run the consistency check on pushes and pull requests

## [3.3] - 2026-04-09

### Added — PaperOrchestra-inspired enhancements
Integrates techniques from Song et al. (2026, *arXiv:2604.05018*) "PaperOrchestra: A Multi-Agent Framework for Automated AI Research Paper Writing."

- **Semantic Scholar API Verification** (deep-research, academic-pipeline): Tier 0 programmatic reference verification via S2 API. Title search with Levenshtein >= 0.70 matching. DOI mismatch detection for Compound Deception Pattern #5. Bibliography deduplication via S2 IDs. Graceful degradation if API unavailable.
  - New file: `deep-research/references/semantic_scholar_api_protocol.md`
  - Modified: `source_verification_agent`, `bibliography_agent`, `integrity_verification_agent`
- **Anti-Leakage Protocol** (academic-paper, deep-research): Knowledge Isolation Directive prioritizes session materials over LLM parametric memory for factual content. Flags `[MATERIAL GAP]` for missing content instead of silently filling from memory. Reduces Mode 5/6 failure risk.
  - New file: `academic-paper/references/anti_leakage_protocol.md`
  - Modified: `draft_writer_agent`, `report_compiler_agent`
- **VLM Figure Verification** (academic-paper): Optional closed-loop verification of rendered figures using vision-capable LLM. 10-point checklist covering data accuracy, APA 7.0 compliance, and visual quality. Max 2 refinement iterations.
  - New file: `academic-paper/references/vlm_figure_verification.md`
  - Modified: `visualization_agent`
- **Score Trajectory Protocol** (academic-pipeline): Per-dimension rubric score delta tracking across revision rounds. Detects regressions (delta < -3) and triggers mandatory checkpoint. Extends v3.2 early-stopping with dimension-level granularity.
  - New file: `academic-pipeline/references/score_trajectory_protocol.md`
  - Modified: `integrity_review_protocol.md`, `handoff_schemas.md` (Schema 5)
- **Stage 2 Parallelization Directive** (academic-pipeline): Visualization and argument building can run in parallel after outline completion.
- **Handoff Schema Updates** (shared): `semantic_scholar_id` field added to Bibliography source object. `score_trajectory` structure added to Integrity Report schema.

**Version bumps**: deep-research v2.8, academic-paper v3.0, academic-pipeline v3.2

## [3.2] - 2026-04-09

### Added — Lu 2026 integration
Integrates insights from Lu et al. (2026, *Nature* 651:914-919) — the first end-to-end autonomous AI research system to pass blind peer review.

- **AI Research Failure Mode Checklist** (academic-pipeline): 7-mode taxonomy extending the existing 5-type citation hallucination taxonomy. Covers implementation-bug blindness, hallucinated experimental results, shortcut reliance, bug-as-insight, methodology fabrication, and pipeline-level frame-lock. Runs at Stage 2.5 and 4.5 with mandatory blocking behaviour. Reported at Stage 6 in the Failure Mode Audit Log subsection of the AI Self-Reflection Report.
  - New file: `academic-pipeline/references/ai_research_failure_modes.md`
- **Reviewer Calibration Mode** (academic-paper-reviewer v1.8): opt-in mode that measures FNR / FPR / balanced accuracy / AUC against a user-supplied gold-standard set of 5-20 papers. Uses 5x ensembling with fresh context per run. Cross-model verification default-on. Session-scoped confidence disclosure.
  - New file: `academic-paper-reviewer/references/calibration_mode_protocol.md`
- **Disclosure Mode** (academic-paper v2.9): venue-specific AI-usage disclosure statement generator. v1 database covers ICLR, NeurIPS, Nature, Science, ACL, EMNLP. Unknown venues halt and prompt user to paste policy.
  - New files: `academic-paper/references/disclosure_mode_protocol.md`, `academic-paper/references/venue_disclosure_policies.md`
- **Fidelity-Originality Mode Spectrum** (all skills): classifies all modes on a fidelity–originality axis per Lu 2026 Fig 1c. Quick Mode Selection Guides updated with Spectrum column.
  - New file: `shared/mode_spectrum.md`
- **Early-Stopping Criterion** (academic-pipeline v3.1): convergence check (delta < 3 points + no P0) suggests stopping revision loop. Budget transparency estimate at pipeline start.
- **README Positioning Update**: "Why human-in-the-loop, not full automation?" section citing Lu 2026 as external evidence for ARS's design thesis. Both EN and zh-TW updated.

### Changed
- `.claude/CLAUDE.md`: synced all skill versions and mode lists to reality (deep-research v2.7, academic-paper v2.9, academic-paper-reviewer v1.8, academic-pipeline v3.1)
- `quality_rubrics.md`: added "Known error profile" preamble explaining rubric scores are ordinally but not cardinally interpretable without calibration

**Version bumps**: academic-paper v2.9, academic-paper-reviewer v1.8, academic-pipeline v3.1

## [3.1.1] - 2026-04-09

### Added
- **Information Systems — Senior Scholars' Basket of 11** (extending the *Basket of 8* added in v2.9): *Decision Support Systems*, *Information & Management*, *Information and Organization* — completing the AIS College of Senior Scholars' official list of premier IS journals
- Section heading updated from "Information Systems (Basket of 8)" to "Information Systems (Senior Scholars' Basket of 11)" in `academic-paper-reviewer/references/top_journals_by_field.md`
- Original IS Basket of 8 proposed and drafted by [@mchesbro1](https://github.com/mchesbro1) — [Issue #5](https://github.com/Imbad0202/academic-research-skills/issues/5). Extended to Basket of 11 by [@cloudenochcsis](https://github.com/cloudenochcsis) — [Issue #7](https://github.com/Imbad0202/academic-research-skills/issues/7), [PR #8](https://github.com/Imbad0202/academic-research-skills/pull/8). Source: [AIS Senior Scholars' List of Premier Journals](https://aisnet.org/page/SeniorScholarListofPremierJournals)

## [2.9.1] - 2026-04-03

### Added
- `status` and `related_skills` metadata to all 4 SKILL.md frontmatters
  - Enables skill discovery tools and cross-skill navigation for users with multiple skills installed
  - `deep-research` ↔ `academic-paper` ↔ `academic-paper-reviewer` ↔ `academic-pipeline`

## [2.9] - 2026-03-27

### Added
- **Style Calibration** — learn the author's writing voice from past papers (optional, intake Step 10)
- **Writing Quality Check** — checklist catching overused AI-typical patterns (renamed from AI Writing Lint)
- Information Systems Basket of 8 journals added to academic-paper reference list
- Copilot philosophy tagline to README EN + zh-TW
- Substack guide articles to both READMEs

### Fixed
- Skill Details section version numbers and agent descriptions updated
- /simplify review — stale refs, lint sweep efficiency, schema fields
- Removed last v4.0 reference in CHANGELOG

## [2.8] - 2026-03-22

### Added
- **SCR Loop Phase 1** — State-Challenge-Reflect mechanism integrated into Socratic Mentor Agent
  - Commitment gates at layer/chapter transitions (collect user predictions before presenting evidence)
  - Certainty-triggered contradiction (probes high-confidence statements with counterpoints)
  - Adaptive intensity (tracks commitment accuracy, adjusts challenge frequency)
  - Self-calibration signal (S5) for convergence detection
  - SCR Switch — users can disable/re-enable predictions mid-dialogue
- `deep-research/agents/socratic_mentor_agent.md` — SCR Protocol section with commitment gates, divergence reveal, and adaptive intensity
- `deep-research/references/socratic_questioning_framework.md` — SCR Overlay Protocol mapping SCR phases to Socratic functions
- `academic-paper/agents/socratic_mentor_agent.md` — Chapter-level SCR Protocol with per-chapter commitment questions and cross-chapter pattern tracking

## [2.7.3] - 2026-03-10

### Fixed
- Version badge corrected in both EN and zh-TW READMEs

## [2.7.2] - 2026-03-10

### Added
- Version, license, and sponsor badges to README
- zh-TW README badges

## [2.7.1] - 2026-03-10

### Fixed
- Buy Me a Coffee username corrected

## [2.7] - 2026-03-09

### Added
- Integrity Verification v2.0: Anti-Hallucination Overhaul
- Full academic research skills suite (4 skills, 116 files)
- Deep Research v2.3 — 13-agent research team with 7 modes
- Academic Paper v2.4 — 12-agent paper writing with LaTeX hardening
- Academic Paper Reviewer v1.4 — Multi-perspective peer review with quality rubrics
- Academic Pipeline v2.6 — 10-stage orchestrator with integrity verification
