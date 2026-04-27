# Academic Research Skills

A suite of Claude Code skills for rigorous academic research, paper writing, peer review, and pipeline orchestration.

## Skills Overview

| Skill | Purpose | Key Modes |
|-------|---------|-----------|
| `deep-research` v2.9.2 | 13-agent research team | full, quick, socratic, review, lit-review, fact-check, systematic-review |
| `academic-paper` v3.1.1 | 12-agent paper writing | full, plan, outline-only, revision, revision-coach, abstract-only, lit-review, format-convert, citation-check, disclosure |
| `academic-paper-reviewer` v1.9.0 | Multi-perspective paper review (5 reviewers + optional cross-model DA critique) | full, re-review, quick, methodology-focus, guided, calibration |
| `academic-pipeline` v3.6.5 | Full pipeline orchestrator | (coordinates all above) |

## v3.6.5 Key Additions

- **Material Passport `literature_corpus[]` consumer integration in Phase 1**: `deep-research/agents/bibliography_agent.md` and `academic-paper/agents/literature_strategist_agent.md` now read `literature_corpus[]` via the **corpus-first, search-fills-gap** flow when the passport carries a non-empty corpus. Both consumers follow the same five-step shared flow (Step 0 presence detection → Step 1 pre-screen → Step 2 search-fills-gap → Step 3 merge → Step 4 emit Search Strategy report) and the same four Iron Rules (Same criteria / No silent skip / No corpus mutation / Graceful fallback on parse failure).
- **PRE-SCREENED reproducibility block**: Search Strategy reports gain a PRE-SCREENED FROM USER CORPUS block enumerating included / excluded / skipped corpus entries, with F3 zero-hit note and F4a–F4f provenance reporting that compose around partial declaration of `obtained_via` / `obtained_at`. `final_included = pre_screened_included[] ∪ external_included[]` stays neutral — no provenance tags on bibliography entries or literature matrix rows.
- **Consumer protocol reference**: `academic-pipeline/references/literature_corpus_consumers.md` carries the canonical PRE-SCREENED template, BAD/GOOD examples, four Iron Rules, and per-consumer reading instructions. Both consumer agents backpoint to this reference.
- **CI lint** `scripts/check_corpus_consumer_protocol.py` enforcing nine protocol invariants with manifest-driven consumer list (`scripts/corpus_consumer_manifest.json`).
- **Schema 9 caveat retired**: `shared/handoff_schemas.md` retired the v3.6.4 "Consumer-side integration deferred to v3.6.5+" caveat; replaced with backpointer to the consumer protocol.
- **No schema change**: existing user adapters work without modification. Consumer integration is presence-based: auto-engages when passport carries a non-empty `literature_corpus[]` and parses cleanly. Parse failures fall back to external-DB-only flow with a `[CORPUS PARSE FAILURE]` surface. No new env flag introduced. `citation_compliance_agent` corpus integration deferred to v3.6.6+.

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
- **Suite version**: 3.6.5 (per CHANGELOG.md)
- **Last Updated**: 2026-04-27
- **Author**: Cheng-I Wu
- **License**: CC-BY-NC 4.0
