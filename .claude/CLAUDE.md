# Academic Research Skills

A suite of Claude Code skills for rigorous academic research, paper writing, peer review, and pipeline orchestration.

## Skills Overview

| Skill | Purpose | Key Modes |
|-------|---------|-----------|
| `deep-research` v2.9.3 | 13-agent research team | full, quick, socratic, review, lit-review, fact-check, systematic-review |
| `academic-paper` v3.1.1 | 12-agent paper writing | full, plan, outline-only, revision, revision-coach, abstract-only, lit-review, format-convert, citation-check, disclosure |
| `academic-paper-reviewer` v1.9.0 | Multi-perspective paper review (5 reviewers + optional cross-model DA critique) | full, re-review, quick, methodology-focus, guided, calibration |
| `academic-pipeline` v3.8.1 | Full pipeline orchestrator | (coordinates all above) |

## v3.7.3 Key Additions (in progress)

**External motivation:** Zhao et al. arXiv:2605.07723 (2026-05). The paper documents 146,932 hallucinated citations across arXiv / bioRxiv / SSRN / PMC in 2025 alone, with inflection at mid-2024 and 85.3% of preprint hallucinations surviving into the published record. It names the L3 (claim faithfulness) gap explicitly as the load-bearing unsolved problem. v3.7.3 closes the locator-channel half of that gap and adds contamination advisory signals.

**L3-1 — Three-Layer Citation Emission (claim faithfulness locator):**

- `synthesis_agent`, `draft_writer_agent`, `report_compiler_agent` gain `## Three-Layer Citation Emission (v3.7.3)` H2 sections. Extends v3.7.1 Two-Layer with `<!--anchor:<kind>:<value>-->` after `<!--ref:slug-->`, `<kind>` ∈ `{quote, page, section, paragraph, none}`. Quote anchors capped at 25 words; URL-encoded values; no frontmatter reads (v3.6.7 partial-inversion preserved).
- `pipeline_orchestrator_agent` finalizer becomes 5-cell with precedence-zero NO-LOCATOR check. `formatter_agent` gains explicit hard-gate refusal for `[UNVERIFIED CITATION — NO QUOTE OR PAGE LOCATOR]`.

**L3-2 — Contaminated-source advisory signals:**

- `literature_corpus_entry.schema.json` adds optional `contamination_signals: { preprint_post_llm_inflection, semantic_scholar_unmatched }` object. Backward compat: entries without the field stay valid.
- `bibliography_agent` computes both signals at ingest time. Preprint signal: `year >= 2024 AND venue ∈ closed-list-of-6`. SS-unmatched signal: existing Semantic Scholar protocol returns no match; exempted for `obtained_via: manual`; omitted on API degradation.
- Finalizer annotates `ok` / `LOW-WARN` markers with `CONTAMINATED-PREPRINT` / `CONTAMINATED-UNMATCHED` / `CONTAMINATED-PREPRINT+UNMATCHED`. Advisory only — does NOT change gate decision.

**Lint + tests:**

- New `scripts/check_v3_7_3_three_layer_citation.py` + 14 tests.
- New 6 contamination_signals tests in existing literature_corpus schema test file.
- New v3.7.3 line-budget test; v3.6.7 Phase 6.6 budget test updated to subtract v3.7.3 extension lines alongside v3.7.1 Step 3b.

**Regression status (final, post round-10 convergence):** 967 pass / 3 skipped / 0 failed (pre-review baseline 925; +42 tests across F1-F22 closures). v3.6.7 PATTERN PROTECTION + v3.7.1 / v3.7.2 lints unchanged. v3.7.3 lint wired into spec-consistency.yml CI workflow. 11-round review trajectory (Codex×10 + Gemini 3.1-pro-preview cross-model×1): F1-F22 closed across 10 codex rounds + 1 gemini round, no cross-reviewer overlap — canonical review-vs-challenge cascade per `feedback_codex_workflow_consolidated.md`. Round 10 codex returned **0 findings**, convergence signal achieved.

Spec: `docs/design/2026-05-12-ars-v3.7.3-claim-faithfulness-and-contaminated-source-spec.md`.

## v3.7.0 Key Additions

- **Claude Code plugin packaging**: ARS now installs in one line via `/plugin marketplace add Imbad0202/academic-research-skills` + `/plugin install academic-research-skills`. The traditional `git clone + symlink to ~/.claude/skills/` flow continues to work — both tracks are first-class. Repo gains four top-level directories: `.claude-plugin/`, `commands/`, `agents/`, `hooks/`, plus a `skills/` symlink dir; existing 4 skill directories untouched.
- **10 slash commands** (`commands/ars-*.md`) mapping `MODE_REGISTRY.md` entries to `/ars-<mode>` triggers with model routing pinned in frontmatter — `opus` for `full` and `revision-coach`, `sonnet` for the other 8, no Haiku.
- **3 plugin-shipped agents** (`agents/*_agent.md`) as relative symlinks to the v3.6.7-hardened downstream agents in `deep-research/agents/`. Source frontmatter gains `model: inherit` so an Opus session keeps Opus agents while the user's PreToolUse `warn-agent-no-model.sh` hook gates Haiku at dispatch.
- **SessionStart announce hook** (`hooks/hooks.json` + `scripts/announce-ars-loaded.sh`) lists the 10 slash commands + 3 agents + token-budget pointer when the plugin loads. Bash 3.2 compatible.
- **Phase 2.2 scope reduction note**: a `SubagentStop → run_codex_audit.sh` codex audit hook was scoped out for v3.7.0 (contract gap: hook payload carries no stage/deliverable; invoker boundary: same-session in-LLM Bash forbidden by the wrapper). Deferred to a future release.

## v3.6.8 Key Additions

> **Naming note**: this release ships the v3.6.6 generator-evaluator contract design (`docs/design/2026-04-27-ars-v3.6.6-generator-evaluator-contract-design.md`) and its implementation. The v3.6.6 spec/implementation work landed after v3.6.7 due to project sequencing (v3.6.7 downstream-agent pattern protection shipped first); the design doc retains the **v3.6.6 internal naming** for the contract gate version (`writer_full` / `evaluator_full` mode, Schema 13.1, `pre_commitment_artifacts` + `disagreement_handling` schema fields), while the suite release is tagged **v3.6.8** to keep the CHANGELOG monotonic.

- **Schema 13.1 generator-evaluator contract gate** for `academic-paper full` mode. `shared/sprint_contract.schema.json` upgrades to Schema 13.1 with two new `mode` enum values (`writer_full` + `evaluator_full`), two new optional top-level fields (`pre_commitment_artifacts` writer-only, `disagreement_handling` evaluator-only), and 12 `allOf` branches enforcing reviewer-conditional / writer-conditional / evaluator-conditional gates. Existing reviewer contracts validate byte-equivalent under Schema 13.1 (§3.6 zero-touch promise).
- **Two new shipped contract templates**: `shared/contracts/writer/full.json` (D1–D7 dimensions, F1/F4/F2/F3/F0 conditions, no `scoring_plan`) and `shared/contracts/evaluator/full.json` (D1–D5 dimensions, F1/F2/F3/F6/F4/F5/F0 conditions, full `scoring_plan` + `disagreement_handling`).
- **Two-phase orchestration inside `academic-paper full` mode**: Phase 4 (writer drafting) splits into Phase 4a paper-blind pre-commitment + Phase 4b paper-visible drafting + self-scoring; Phase 6 (in-pair evaluator review) splits into Phase 6a paper-blind pre-commitment + Phase 6b paper-visible scoring + decision. Phase-numbered `<phase4a_output>` / `<phase6a_output>` data delimiters mirror the v3.6.2 reviewer pattern. Lint counts: writer 3+4 / evaluator 5+5 / reviewer 5+6 zero-touch. `[GENERATOR-PHASE-ABORTED]` abort tag with 5%/three-month operational monitor.
- **`academic-paper/SKILL.md` `## v3.6.6 Generator-Evaluator Contract Protocol` orchestration block** (101 lines): four-call structure, system-vs-user content discipline, schema-vs-runtime emission distinction, per-phase lint, abort handling, two valid Stage 3 entry paths (standard F0/F4 + exceptional F5), cross-session resume scope. Plus `## Known limitations` section carrying graceful-degradation forward note + cross-session resume forward note + in-pair vs external reviewer tech debt.
- **`draft_writer_agent.md` + `peer_reviewer_agent.md`** each gain a verbatim `## v3.6.6 Generator-Evaluator Contract Protocol` section with system-prompt sub-sections for Phase 4a/4b (writer) and Phase 6a/6b (evaluator).
- **`scripts/check_sprint_contract.py` SC-* mode-gating audit**: SC-5 (measurement_procedure canonical outputs) and SC-11 (panel_size sanity) now mode-gated to `mode.startswith("reviewer_")`; SC-9 (paraphrase_minimum_dimensions exceeds dim count) extended across all three mode families with each mode reading its own field path. Mode-agnostic warnings (SC-1/2/3/4/7/10) unchanged.
- **17 new validator tests** (54 → 71): 4 shipped writer/evaluator template positive tests, 5 schema-branch negative tests (branches 11/12/4/5/6 hard-fail; cross-mode field leakage intentionally NOT tested per §7.1 R1 settled), 2 §3.6 reviewer regression tests, 6 SC-5/SC-9/SC-11 mode-gating tests.
- **`scripts/check_v3_6_6_ab_manifest.py` + workflow extension**: enforces §6.2 manifest schema + §6.5 git-tracked invariants on `tests/fixtures/v3.6.6-ab/manifest.yaml`. `.github/workflows/spec-consistency.yml` extends the sprint contract validation loop to iterate writer + evaluator template directories alongside the existing reviewer loop, plus runs the new manifest CI lint as an additional step.
- **`tests/fixtures/v3.6.6-ab/` A/B evidence fixture stub** (30 files): manifest + README + 6 paper-A inputs/baseline + 1 paper-C inputs/baseline + Stage 3 reviewer excerpt + 6 codex-judge baseline placeholders. `manifest_lint_mode: spec_branch`, `fixture_version: 0.1.0`. Real fixture data populates in follow-up commits.
- **`academic-paper-reviewer/references/sprint_contract_protocol.md` cross-reference** noting Schema 13.1 since v3.6.6 + pointing readers at `academic-paper/SKILL.md` + design doc §5 for the parallel generator-evaluator protocol.

## v3.6.7 Key Additions

- **Downstream-agent pattern protection layer (Step 1+2)**: `synthesis_agent`, `research_architect_agent` (survey-designer mode), and `report_compiler_agent` (abstract-only mode) carry a `PATTERN PROTECTION (v3.6.7)` block hardening 13 of 18 documented hallucination/drift patterns (A1–A5 narrative-side, B1–B5 instrument-side, C1–C3 publication-side). Step 6 (orchestrator runtime hooks) and Step 8 (synthetic eval case) ship in a follow-up PR.
- **Four reference files in `shared/references/`**: `irb_terminology_glossary.md` (anonymity/confidentiality/de-identification/pseudonymization), `psychometric_terminology_glossary.md` (true reverse-coded vs contrast item), `protected_hedging_phrases.md` (five-rule contract for upstream-marked hedges), `word_count_conventions.md` (whitespace-split + 3–5% buffer).
- **Cross-model audit prompt template** at `shared/templates/codex_audit_multifile_template.md` covering seven audit dimensions plus a mandatory three-part Section 4(f) check for `report_compiler_agent` bundles.
- **Static lint + 29-test mutation suite** at `scripts/check_v3_6_7_pattern_protection.py` and `scripts/test_check_v3_6_7_pattern_protection.py`, both wired into `.github/workflows/spec-consistency.yml`.
- **Ship-quality target update**: per spec §10, ARS pipeline target moves from "each agent produces a clean v1" to "end-to-end deliverable set passes independent xhigh cross-model audit at 0 P1+P2 finding within three rounds."

## v3.6.5 Key Additions

- **Material Passport `literature_corpus[]` consumer integration in Phase 1**: `deep-research/agents/bibliography_agent.md` and `academic-paper/agents/literature_strategist_agent.md` now read `literature_corpus[]` via the **corpus-first, search-fills-gap** flow when the passport carries a non-empty corpus. Both consumers follow the same five-step shared flow (Step 0 presence detection → Step 1 pre-screen → Step 2 search-fills-gap → Step 3 merge → Step 4 emit Search Strategy report) and the same four Iron Rules (Same criteria / No silent skip / No corpus mutation / Graceful fallback on parse failure).
- **PRE-SCREENED reproducibility block**: Search Strategy reports gain a PRE-SCREENED FROM USER CORPUS block enumerating included / excluded / skipped corpus entries, with F3 zero-hit note and F4a–F4f provenance reporting that compose around partial declaration of `obtained_via` / `obtained_at`. `final_included = pre_screened_included[] ∪ external_included[]` stays neutral — no provenance tags on bibliography entries or literature matrix rows.
- **Consumer protocol reference**: `academic-pipeline/references/literature_corpus_consumers.md` carries the canonical PRE-SCREENED template, BAD/GOOD examples, four Iron Rules, and per-consumer reading instructions. Both consumer agents backpoint to this reference.
- **CI lint** `scripts/check_corpus_consumer_protocol.py` enforcing nine protocol invariants with manifest-driven consumer list (`scripts/corpus_consumer_manifest.json`).
- **Schema 9 caveat retired**: `shared/handoff_schemas.md` retired the v3.6.4 "Consumer-side integration deferred to v3.6.5+" caveat; replaced with backpointer to the consumer protocol.
- **No schema change**: existing user adapters work without modification. Consumer integration is presence-based: auto-engages when passport carries a non-empty `literature_corpus[]` and parses cleanly. Parse failures fall back to external-DB-only flow with a `[CORPUS PARSE FAILURE]` surface. No new env flag introduced. `citation_compliance_agent` corpus integration deferred (target version TBD post-v3.8).

## v3.6.4 Key Additions

- **Material Passport `literature_corpus[]` input port**: Schema 9 gains an optional `literature_corpus[]` field defined by `shared/contracts/passport/literature_corpus_entry.schema.json`. Entries carry CSL-JSON authors, year, title, and `source_pointer` back to the user's own KB. `abstract` and `user_notes` are private optional fields with copyright caveats.
- **Language-neutral adapter contract**: `academic-pipeline/references/adapters/overview.md` specifies how any adapter produces literature_corpus entries. Fail-soft error handling with mandatory `rejection_log.yaml`, deterministic ordering (sort by `citation_key` / `source`), and extension points for user-written adapters.
- **Three reference Python adapters**: `scripts/adapters/{folder_scan,zotero,obsidian}.py` with tests and fixtures. Starting points only; users are expected to write their own adapters for non-reference corpus sources.
- **Rejection log contract**: `shared/contracts/passport/rejection_log.schema.json`. Always emitted, empty when no rejections; closed enum of categorical reason values.
- **CI lint + pytest job**: `scripts/check_literature_corpus_schema.py` validates schemas + examples; `scripts/sync_adapter_docs.py --check` prevents schema→docs drift; new `pytest.yml` workflow runs `scripts/adapters/tests/` on path-filtered triggers.
- **Input-port-only at v3.6.4**: v3.6.4 shipped the schema and adapter contract; consumer integration landed in v3.6.5.

## v3.6.3 Key Additions

- **Opt-in passport reset boundary**: new `ARS_PASSPORT_RESET=1` flag promotes every FULL checkpoint to a context-reset boundary. New `resume_from_passport=<hash>` mode in `academic-pipeline` lets users resume a pipeline run in a fresh Claude Code session from the Material Passport ledger alone, without replaying prior turns. For `systematic-review` mode with the flag ON, reset is mandatory at every FULL checkpoint; other modes treat reset as the flag-gated default. Flag OFF preserves pre-v3.6.3 continuation behavior byte-for-byte.
- **Schema 9 `reset_boundary[]` append-only ledger** with two entry kinds: `kind: boundary` (recorded at FULL checkpoints) and `kind: resume` (recorded when a boundary is consumed). Hash uses JSON Canonical Form + SHA-256 with canonical `"000000000000"` placeholder for self-reference safety. Optional `pending_decision` field handles MANDATORY branch choices (Stage 3 reject/restructure/abort, Stage 5 finalization) that would otherwise be lost on reset.
- **Protocol doc** `academic-pipeline/references/passport_as_reset_boundary.md` (authoritative) + **CI lint** `scripts/check_passport_reset_contract.py` enforcing every mention of the flag co-locates a protocol-doc reference.
- **Docs** `docs/PERFORMANCE.md` + `docs/PERFORMANCE.zh-TW.md` updated with long-running-session guidance for the reset workflow.

## v3.6.2 Key Additions

- **Sprint Contract hard gate for reviewers**: Schema 13 + validator + two reviewer templates (`full.json` panel 5, `methodology_focus.json` panel 2). Reviewer runs paper-content-blind Phase 1 + paper-visible Phase 2 via `<phase1_output>` data delimiter. Synthesizer runs three-step mechanical protocol (build matrix → evaluate with panel-relative quantifier + expression vocabulary → resolve precedence by severity). Forbidden-ops list in `academic-paper-reviewer/agents/editorial_synthesizer_agent.md`. Reserved reviewer modes (`re_review`, `calibration`, `guided`) keep pre-v3.6.2 behaviour until follow-up templates land. Spec: `docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md`. Orchestration ref: `academic-paper-reviewer/references/sprint_contract_protocol.md`.

## v3.5.1 Key Additions

- **Opt-in Socratic reading-check probe**: new §"Optional Reading Probe Layer" in `deep-research/agents/socratic_mentor_agent.md`. Gated by `ARS_SOCRATIC_READING_PROBE=1`. Fires at most once per goal-oriented Socratic session when the user has cited a specific paper. Decline is logged without penalty. Outcome is recorded inline in the Research Plan Summary and carried into the Stage 6 AI Self-Reflection Report. No new agent, no new mode, no schema change. See `docs/design/2026-04-22-ars-v3.7.3-reading-check-probe-design.md`.

## v3.5 Key Additions

- **Collaboration Depth Observer**: new `collaboration_depth_agent` in `academic-pipeline` (Agent Team grows 3 → 4). Invoked at every FULL/SLIM checkpoint and at pipeline completion; scores user-AI collaboration on 4 dimensions (Delegation Intensity, Cognitive Vigilance, Cognitive Reallocation, Zone Classification) per `shared/collaboration_depth_rubric.md`. **Advisory only — never blocks.** MANDATORY integrity checkpoints (2.5, 4.5) preserved and do not invoke the observer. Cross-model divergence flagged, not silently averaged. Based on Wang & Zhang (2026) IJETHE 23:11 (DOI 10.1186/s41239-026-00585-x).

## v3.4 Key Additions

- **Compliance Agent (shared)**: single mode-aware agent running PRISMA-trAIce 17 items + RAISE 4 principles + 8-role matrix. Hooks Stage 2.5 / 4.5 Integrity Gates with tier-based block. Non-SR entries run principles-only warn-only. See `shared/agents/compliance_agent.md`.
- **Schema 12 compliance_report**: append-only audit trail in Material Passport via `compliance_history[]`.
- **3-round override ladder**: user overrides produce auto-injected `disclosure_addendum`. See `shared/compliance_checkpoint_protocol.md`.
- **Long-running session docs**: `docs/PERFORMANCE.md` now covers cross-session resume via Material Passport.

## v3.3 Key Additions

- **Semantic Scholar API Verification**: Tier 0 programmatic reference verification. See `deep-research/references/semantic_scholar_api_protocol.md`.
- **Anti-Leakage Protocol**: Knowledge isolation prioritizing session materials over LLM memory. See `academic-paper/references/anti_leakage_protocol.md`.
- **VLM Figure Verification**: Optional closed-loop figure verification via vision LLM. See `academic-paper/references/vlm_figure_verification.md`.
- **Score Trajectory Protocol**: Per-dimension rubric score delta tracking across revision rounds. See `academic-pipeline/references/score_trajectory_protocol.md`.
- **Stage 2 Parallelization**: Visualization and argument building can run in parallel after outline.

## v3.2 Key Additions

- **7-mode AI Research Failure Mode Checklist**: blocks pipeline at Stage 2.5/4.5 on suspected failures (Lu 2026). See `academic-pipeline/references/ai_research_failure_modes.md`.
- **Reviewer Calibration Mode**: opt-in FNR/FPR/balanced-accuracy measurement. See `academic-paper-reviewer/references/calibration_mode_protocol.md`.
- **Disclosure Mode**: venue-specific AI-usage statement (ICLR/NeurIPS/Nature/Science/ACL/EMNLP). See `academic-paper/references/disclosure_mode_protocol.md`.
- **Early-Stopping + Budget Transparency**: convergence check + token cost estimate at pipeline start.
- **Fidelity-Originality Mode Spectrum**: classifies all modes. See `shared/mode_spectrum.md`.

## v3.0 Key Additions

- **Anti-sycophancy protocols**: DA agents score rebuttals 1-5 before conceding. No concession below 4/5. Frame-lock detection.
- **Intent detection**: Socratic Mentor classifies user intent as exploratory vs. goal-oriented. Exploratory mode disables auto-convergence.
- **Cross-model verification** (optional): Set `ARS_CROSS_MODEL` env var to enable GPT-5.4 Pro or Gemini 3.1 Pro for integrity sample checks and independent Devil's Advocate critique. Peer-review sixth-reviewer support remains planned. See `shared/cross_model_verification.md`.
- **AI Self-Reflection Report**: Pipeline Stage 6 now includes AI behavioral self-assessment (concession rate, health alerts, sycophancy risk rating).

## Routing Rules

1. **academic-pipeline vs individual skills**: academic-pipeline = full pipeline orchestrator (research → write → integrity → review → revise → final integrity → finalize). If the user only needs a single function (just research, just write, just review), trigger the corresponding skill directly without the pipeline.

2. **deep-research vs academic-paper**: Complementary. deep-research = upstream research engine (investigation + fact-checking), academic-paper = downstream publication engine (paper writing + bilingual abstracts). Recommended flow: deep-research → academic-paper.

3. **deep-research socratic vs full**: socratic = guided Socratic dialogue to help users clarify their research question. full = direct production of research report. When the user's research question is unclear, suggest socratic mode.

4. **academic-paper plan vs full**: plan = chapter-by-chapter guided planning via Socratic dialogue. full = direct paper production. When the user wants to think through their paper structure, suggest plan mode.

5. **academic-paper-reviewer guided vs full**: guided = Socratic review that engages the author in dialogue about issues. full = standard multi-perspective review report. When the user wants to learn from the review, suggest guided mode.

## Key Rules

- All claims must have citations
- Evidence hierarchy respected (meta-analyses > RCTs > cohort > case reports > expert opinion)
- Contradictions disclosed with evidence quality comparison
- AI disclosure in all reports
- Default output language matches user input (Traditional Chinese or English)

## Full Academic Pipeline

```
deep-research (socratic/full)
  → academic-paper (plan/full)
    → integrity check (Stage 2.5)
      → academic-paper-reviewer (full/guided)
        → academic-paper (revision)
          → academic-paper-reviewer (re-review, max 2 loops)
            → final integrity check (Stage 4.5)
              → academic-paper (format-convert → final output)
                → Process Summary + AI Self-Reflection Report
```

## Handoff Protocol

### deep-research → academic-paper
Materials: RQ Brief, Methodology Blueprint, Annotated Bibliography, Synthesis Report, INSIGHT Collection

### academic-paper → academic-paper-reviewer
Materials: Complete paper text. field_analyst_agent auto-detects domain and configures reviewers.

### academic-paper-reviewer → academic-paper (revision)
Materials: Editorial Decision Letter, Revision Roadmap, Per-reviewer detailed comments

## Version Info
- **Suite version**: 3.8.1 (per CHANGELOG.md)
- **Last Updated**: 2026-05-17
- **Author**: Cheng-I Wu
- **License**: CC-BY-NC 4.0
