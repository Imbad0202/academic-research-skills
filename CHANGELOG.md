# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### #103 — v3.8 claim ↔ reference faithfulness audit agent (2026-05-16)

**Parent issue:** [#103](https://github.com/Imbad0202/academic-research-skills/issues/103) — closes the L3 (claim-faithfulness) gap left open by v3.7.3 (which closed the locator-channel half). Spec: `docs/design/2026-05-15-issue-103-claim-alignment-audit-spec.md` + decision doc `docs/design/2026-05-15-issue-103-claim-alignment-audit-decision.md` (D1-D6 settled).

**Why:** Zhao et al. arXiv:2605.07723 (2026-05) shows 146,932 hallucinated citations across arXiv / bioRxiv / SSRN / PMC in 2025; v3.7.3 stopped the "no locator" path but a present-but-wrong claim ↔ source mismatch was still undetected. v3.8 adds a Stage 4→5 audit pass that judges every sampled citation against its retrieved excerpt, emits 5 new passport aggregates, and drives 5 new HIGH-WARN annotation classes through the formatter terminal hard gate.

**New components:**

- **`claim_ref_alignment_audit_agent`** (1 new agent, `academic-pipeline/agents/`) — opt-in (`ARS_CLAIM_AUDIT=1`, default OFF for v3.8.0) audit agent dispatched between v3.7.1 cite finalizer and formatter hard gate. Takes citations + manifests + corpus + Stage 4 draft sentence stream (full uncited + D4-c filtered subset).
- **5 new passport schemas** (`shared/contracts/passport/`): `claim_audit_result`, `claim_intent_manifest`, `claim_drift`, `uncited_assertion`, `constraint_violation`. Cross-field invariants INV-1..INV-18 / M-INV-1..M-INV-4 / U-INV-1..U-INV-4 / D-INV-1..D-INV-4 / CV-INV-1..CV-INV-4 lint-enforced (JSON Schema can't express the conditional matrix relating judgment / audit_status / defect_stage / ref_retrieval_method).
- **Runtime pipeline** (`scripts/claim_audit_pipeline.py`) — implements §4 step 1-6 + manifest set-diff (D6 set-of-text semantics). Per-citation judge wrapping (`_invoke_judge` + `_invoke_retrieve` translate transient failures to INV-14 `audit_tool_failure` rows: judge_timeout / judge_api_error / judge_parse_error / cache_corruption / retrieval_api_error / retrieval_timeout / retrieval_network_error). Cache hits re-validated through the same surface. Per-manifest uncited judge calls to prevent MNC id collisions across manifests.
- **8-row finalizer matrix** (`scripts/claim_audit_finalizer.py`) — discriminates paywall (LOW-WARN advisory) / fabricated reference (HIGH-WARN gate-refuse) / anchorless (HIGH-WARN defense-in-depth) / audit_tool_failure (MED-WARN advisory) via `ref_retrieval_method` alongside `(judgment, defect_stage)`.
- **5 new HIGH-WARN annotation classes** in `formatter_agent` REFUSE list: `[HIGH-WARN-CLAIM-NOT-SUPPORTED]` / `[HIGH-WARN-NEGATIVE-CONSTRAINT-VIOLATION]` / `[HIGH-WARN-FABRICATED-REFERENCE]` / `[HIGH-WARN-CLAIM-AUDIT-ANCHORLESS]` / `[HIGH-WARN-CONSTRAINT-VIOLATION-UNCITED]`. Mirrors v3.7.3 R-L3-1-A asymmetry — `/ars-mark-read` does NOT clear; remediation is fixing the prose.
- **"Claim Intent Manifest Emission" sibling section** added to `synthesis_agent` / `draft_writer_agent` / `report_compiler_agent` per v3.6.7 PATTERN PROTECTION pattern. The §3a SHA-pinned blocks stay byte-equivalent to commit `e7e775a0e1b4`.
- **Calibration runner** (`scripts/claim_audit_calibration.py` + `scripts/test_claim_audit_calibration.py` + `scripts/fixtures/claim_audit_calibration/gold_set.json`) — 20-tuple gold set (12 alignment + 8 constraint); T-C1 threshold gate (FNR < 0.15 + FPR < 0.10), T-C2 per-class FNR/FPR, T-C3 gold-set shape integrity. Re-run: `PYTHONPATH=. python3 -m unittest scripts.test_claim_audit_calibration -v`.
- **2 new lints + 1 new pytest module + 7 new unittest modules wired into CI** (`.github/workflows/spec-consistency.yml`): `check_claim_audit_consistency.py` (38 invariant checks + schema validation), `check_v3_8_annotation_literal_sync.py` (formatter-finalizer literal drift gate). Test suite: 194 unittest tests across the 7 modules.

**Review trail (Step 13 dual-track, 2026-05-16):** 8 rounds codex (gpt-5.5 xhigh) + 1 round Gemini 3.1-pro-preview before Gemini quota exhausted. Trajectory R1 4P1+2P2 → R2 0P1+3P2 → R3 0P1+5P2 → R4 2P1+2P2 → R5 0P1+2P2+1P3 → R6 1P1+1P2 → R7 1P1+1P2+1P3 → **R8 0P1+4P2 → ship**. Per `feedback_codex_review_surface_loop_design_phase.md` design-phase P2 noise floor doesn't auto-converge; the user declared ship signal at R8 with all P0/P1 closed and 4 R8 P2 carried over to v3.8.1 ([#120](https://github.com/Imbad0202/academic-research-skills/issues/120)).

**Carry-over follow-up issues:**

- [#118](https://github.com/Imbad0202/academic-research-skills/issues/118) — uncited path NOT_VIOLATED swallow on judge failure (schema-level decision)
- [#119](https://github.com/Imbad0202/academic-research-skills/issues/119) — nested schema-invalid shapes still crash invariant helpers
- [#120](https://github.com/Imbad0202/academic-research-skills/issues/120) — 4 R8 P2 findings (CV-INV-4 dedupe scope / invariant walker short-circuit / judgment + method type-check before set membership)

**Regression baseline (post-ship):**

- pytest: 1356 passed, 3 skipped, 103 subtests (was 1107 pre-#103, +249 tests across schema / pipeline / detector / manifest / finalizer / e2e / calibration / lint coverage)
- v3.x lints: 7/7 PASS (v3.6.7 / v3.6.8 ×4 / v3.7.3 / v3.8)
- personal-boundary: 0 violations (614 files scanned)
- SHA-pinned zero-touch: `shared/sprint_contract.schema.json` 0 lines diff, `shared/contracts/passport/audit_artifact_entry.schema.json` 0 lines diff against main

### #115 — Semantic Scholar client maturity: throttle + outage latch (2026-05-15)

**Parent issue:** [#115](https://github.com/Imbad0202/academic-research-skills/issues/115) — follow-up to #105 PR codex round-5 [P2]×2 findings (R5-2 throttle + R5-3 outage latch). Both deferred during #105 ship per architectural-inflection discipline; this entry closes the SS-client maturity gap.

**Modified files:**

- `scripts/semantic_scholar_client.py` — two additions:
  - **Throttle** (#115 R5-2): new ctor params `clock` + `min_interval_seconds`. Defaults: 1.0s unauthenticated (1 req/s per protocol), auto-drops to 0.1s when `S2_API_KEY` detected (authenticated 10 req/s tier). Pre-request pacing tracks `_last_request_at`; sleeps `max(0, min_interval - elapsed)` before each call. First request passes through.
  - **Outage latch** (#115 R5-3): `_latched_unavailable` flag set on `URLError`. Subsequent `lookup()` calls short-circuit with `SemanticScholarUnavailable` without invoking urlopen. New `reset_outage_latch()` method lets long-running tools retry between passport batches. HTTP 5xx does NOT latch (server-side error ≠ transport outage).
- `scripts/test_semantic_scholar_client.py` — 9 new tests (5 throttle: first-no-sleep / back-to-back / past-interval / authenticated-tier / override; 3 latch: URLError short-circuits / reset restores / 5xx does not latch; 1 efficiency: 429-retry refreshes throttle anchor).
- `scripts/contamination_signals.py` — new `reset_client_outage_latch(client)` helper. Production clients implementing the outage-latch pattern expose `reset_outage_latch()`; mocks may not. Helper invokes when present, no-ops when absent — avoids AttributeError when callers swap clients. 2 new tests.
- `scripts/migrate_literature_corpus_to_v3_7_3.py` — `migrate_directory` resets the SS client's outage latch between passports so a transient network blip on one passport doesn't permanently disable lookups for the rest of the directory. Within a single passport the latch still short-circuits to protect a dead service from N retry waves.

**Production behavior change:**

- `_build_default_ss_client()` API unchanged (`SemanticScholarClient()` no-arg). New throttle is automatic per protocol — no migration tool changes required.
- For a 5000-entry unauthenticated migration: same ~1.5hr runtime (already constrained by 1 req/s); now achieves it via deterministic pacing rather than 429-retry exhaustion.
- For an authenticated migration (`S2_API_KEY` set): drops to 0.1s/call = ~8min for 5000 entries.
- Network outage during large corpus: previously retried every entry independently (up to 30s timeout per entry on the slow path); now the first URLError latches the client and subsequent entries short-circuit until the next batch boundary calls `reset_outage_latch()`. The `migrate_directory` helper does this reset automatically between passports.

**Out of scope:** migration tool (`migrate_literature_corpus_to_v3_7_3.py`) — #105 partial-fill / provenance contract correct as shipped. Protocol doc — already correct; this issue is implementation alignment.

**Regression:** 472 unittest (+8 #115 tests) + 201 pytest adapters + spec_consistency + preprint_venues all green.

### #105 — v3.7.3 contamination_signals backfill migration tool (2026-05-15)

**Parent issue:** [#105](https://github.com/Imbad0202/academic-research-skills/issues/105). Spec anchor: v3.7.3 §3.2 R-L3-2-B (the deferred batch operation; bibliography_agent computes signals at ingest, this tool delivers post-hoc backfill on legacy corpora). Design: `docs/design/2026-05-15-issue-105-contamination-signals-backfill-design.md`.

**New files:**

- `scripts/contamination_signals.py` — two pure-function resolvers + emission rules + `SemanticScholarClient` protocol. `compute_preprint_signal()` (Signal 1, deterministic year+venue check against 10-server closed list). `compute_ss_unmatched_signal()` (Signal 2, dependency-injected SS client, returns `None` on manual exemption + API degradation per spec).
- `scripts/migrate_literature_corpus_to_v3_7_3.py` — CLI tool: `[--dry-run] [--verbose] <passport_or_dir>`. Uses `ruamel.yaml` round-trip to preserve comments + key order + quoting style. Reports `processed / patched / skipped_already_migrated / skipped_insufficient_data` counts. Idempotent.
- `scripts/test_contamination_signals.py` — 25 unit tests covering Signal 1 (15 cases: 10 preprint venues × year boundary, non-preprint venue, missing year, missing venue), Signal 2 (6 cases: manual exemption / match / no-match / API degradation × 2 paths / unexpected exception), emission rules (4 cases).
- `scripts/test_migrate_literature_corpus_to_v3_7_3.py` — 9 unittest cases covering dry-run, full migration per emission rules, idempotency, insufficient-data skip, empty-corpus passport, directory scan (non-recursive), comment preservation.
- `docs/migration/v3.7.3-contamination-signals-backfill.md` — user-facing migration guide (when to run, dry-run workflow, idempotency, SS API rate-limit considerations, what's out of scope).

**Modified files:**

- `shared/contracts/passport/literature_corpus_entry.schema.json` — purely additive: new optional `contamination_signals_backfilled_at` field (ISO-8601 date-time string). Existing v3.7.3 ingest-time entries (which lack this field) remain valid; pre-v3.7.3 entries (which lack both this field and `contamination_signals`) remain valid.
- `scripts/adapters/tests/test_literature_corpus_entry_schema.py` — 3 new tests for the additive field (valid present / absent / non-string rejected).
- `requirements-dev.txt` — add `ruamel.yaml>=0.17`.

**Open-question resolutions (user-chosen 2026-05-15):**

- Q1 API rate-limit handling: backoff-only via existing SS protocol (429 → 2s × 3); no resumable checkpoint (YAGNI per minimal scope)
- Q2 schema field naming: scalar `contamination_signals_backfilled_at` ISO-8601 timestamp; strictly additive upgrade path if v3.7.4 needs structured provenance
- Q3 multi-passport batch mode: directory-scan only; no `--input-list` (YAGNI)
- Q4 YAML library: `ruamel.yaml` round-trip to preserve user-owned passport formatting (memory `feedback_toml_duplicate_table_corruption` spirit)

**Spec discipline (per v3.7.3 R-L3-2-B):**

- Migration is offline + opt-in: user explicitly invokes; pipeline doesn't auto-trigger
- Idempotency keyed on `contamination_signals` presence: first-migration timestamp preserved across re-runs
- `obtained_via=manual` exemption preserved at migration time (semantic_scholar_unmatched field omitted, matches the v3.7.3 schema cross-field rule)
- API degradation → field omitted (NOT set to False, per "absence ≠ negative confirmation" rule)

**Files explicitly NOT touched:**

- `deep-research/agents/bibliography_agent.md` — v3.7.3 ingest-time computation frozen
- `academic-pipeline/agents/pipeline_orchestrator_agent.md` — finalizer behavior unchanged
- Existing `scripts/adapters/*` — adapters produce ingest-time entries; migration is downstream

**Regression status:** 1053 #108 baseline + 17 #111 baseline + 25 resolver + 9 migration + 3 schema = 1107 total. All green. No regression on the existing 4 `allOf` cross-field invariants (manual exemption + preprint year=2024 boundary verified by adapter pytest).

### #104 — README motivation: add Zhao et al. corpus-scale evidence anchor (2026-05-15)

**Parent issue:** [#104](https://github.com/Imbad0202/academic-research-skills/issues/104). Doc-only — no code changes.

Adds a third evidence anchor to the `### Why human-in-the-loop, not full automation?` README section, between the ARS positioning paragraph and the PaperOrchestra paragraph. Closes the gap where v3.7.x trust-and-locator machinery appeared in the codebase without its corpus-scale motivation surfaced in the public-facing README.

**Modified files:**

- `README.md` — new Zhao et al. paragraph
- `README.zh-TW.md` — translated equivalent

**Three motivation anchors now read in sequence:**

- Lu et al. (Nature 651:914-919) — case-study evidence of autonomous-pipeline failure modes
- Zhao et al. (arXiv:2605.07723) — corpus-scale evidence of the citation-faithfulness problem (111M references / 2.5M papers / 146,932 conservative 2025 estimate / mid-2024 inflection / 85.3% bioRxiv-to-PMC persistence)
- PaperOrchestra (Song et al., arXiv:2604.05018) — method-level technique source

**Discipline (#104 acceptance criteria):**

- Statistics verified directly against Zhao et al. abstract (111M / 2.5M / 146,932 / conservative qualifier) + v3.7.3 spec which carries the body-level numbers (85.3% bioRxiv→PMC specificity, mid-2024 inflection) through prior 10-round codex + gemini cross-model review.
- No claims that v3.7.x "closes" L3 — only "adds locator infrastructure" / "advisory risk signals".
- L3 attributed to ARS terminology, not the paper's.
- "Motivated by" not "responds to".

### #111 — slr_lineage emission on systematic-review → academic-paper full handoff (2026-05-15, unreleased)

**Parent issue:** [#111](https://github.com/Imbad0202/academic-research-skills/issues/111), follow-up to #108 (PR #110, merged 70c8678) round-8 P2 #1. Design: `docs/design/2026-05-15-issue-111-slr-lineage-emission-design.md`.

> Version label `v3.7.4` below is provisional and will be confirmed at the next release sweep per `feedback_version_bump_sweep_checklist.md`. If this work ships as part of v3.7.3 (the in-progress release at writing time), the version stamps in this entry and the prose files below are swept to the final label at release tag.

Closes the pipeline-plumbing gap surfaced by #108: `disclosure --policy-anchor=prisma-trAIce` now dispatches automatically when the documented `deep-research systematic-review → academic-paper full → disclosure` path runs, without the user manually supplying `mode=systematic-review` at cold-start.

**New files added:**

- `scripts/slr_lineage.py` — two pure functions: (a) `resolve_from_stages(stages)` returns `True` iff any stage was produced by `deep-research` in systematic-review mode (bound to the deep-research producer specifically — a non-deep-research stage carrying mode='systematic-review' does NOT trigger SLR lineage); (b) `emit(stages, incoming_slr_lineage)` is the monotonic-OR wrapper the orchestrator calls at every handoff. The OR preserves any signal already persisted on the incoming passport (load-bearing for `resume_from_passport=<hash>` sessions whose `state_tracker.stages` is empty — codex round-1 [P2] closure).
- `scripts/test_slr_lineage_emission.py` — 17 conformance tests: resolver semantics (7 cases: positive / non-SLR / mid-entry / empty / alias `slr` / non-deep-research / missing-mode), renderer integration (3 cases: pipeline-emitted dispatches without `mode_param` / non-SLR still blocks / pre-#111 cold-start fallback preserved), end-to-end pipeline handoff (2 cases), and monotonic-OR emit semantics (5 cases: resume preserves true / in-session false-to-true / no-evidence false / None incoming / default arg ergonomics).

**Modified files:**

- `shared/handoff_schemas.md` — Schema 9 Material Passport gains optional top-level `slr_lineage: boolean` row + dedicated "Run-level lineage signal (v3.7.4)" subsection documenting semantics, producer, consumer, backward compat, and G1 boundary note (passport-level vs corpus-entry-level distinction).
- `academic-pipeline/agents/pipeline_orchestrator_agent.md` — §4 Transition Management gains a "Run-level lineage emission (v3.7.4+)" step computed at every handoff transition before dispatch. Passport carry-line updated to reference `slr_lineage` from v3.7.4+.

**Files explicitly NOT touched (matches #111 §Scope out-of-scope):**

- `scripts/policy_anchor_disclosure_referee.py` — #108 referee, contract unchanged
- `academic-paper/references/policy_anchor_disclosure_protocol.md` — #108 protocol, unchanged
- `academic-paper/references/policy_anchor_table.md` — #108 anchor table, unchanged
- `academic-paper/references/disclosure_mode_protocol.md` — already references `slr_lineage` as pipeline-supplied
- `shared/contracts/passport/literature_corpus_entry.schema.json` — G1 invariant frozen (corpus entry schema, not passport schema)

**G1 boundary clarification:** Decision Doc §4.4 #11 G1 invariant scope is `literature_corpus_entry.schema.json` (corpus entry data schema). Schema 9 Material Passport top-level extensions follow the v3.6.3 (`reset_boundary[]`) / v3.6.4 (`literature_corpus[]`) / v3.6.7 (`audit_artifact[]`) precedent and are permitted per Decision Doc §4.4 #11's "non-renderer code changes for §4.4 concerns are permitted" provision.

**Backward compat:** passports written by pre-v3.7.4 runs lack the `slr_lineage` field; renderer treats absence as `false` (cold-start path requiring explicit `mode_param='systematic-review'`). Identical to pre-v3.7.4 behavior.

**Regression status:** 1053-baseline frozen (no #108 contract drift); +17 new tests cover this issue's acceptance criteria #1-#3 plus codex round-1 [P2] (monotonic-OR emit across resume).

### #108 — AI disclosure policy-anchor renderer (2026-05-14, audit-trail-shipped)

**Parent docs:** Decision Doc (`docs/design/2026-05-14-ai-disclosure-schema-decision.md`, PR #109, merged commit 20ed72d) + implementation spec (`docs/design/2026-05-14-ai-disclosure-impl-spec.md`).

**Migration note (G1 + G6 invariants):** **no migration required**. Decision Doc §2.1 G1 invariant: no `ai_disclosure` field is added to `shared/contracts/passport/literature_corpus_entry.schema.json`. Decision Doc §3 G6: no deprecation horizon — legacy entries (which by §1 fact-check do not carry any AI-disclosure field today) stay byte-equivalent. The implementation extends the runtime renderer path, not the data schema.

**New files added:**

- `academic-paper/references/policy_anchor_table.md` — 4-anchor (PRISMA-trAIce / ICMJE / Nature / IEEE) × 16-field source-of-truth reference table carrying verbatim policy quotes lifted from discovery doc §4.3-4.6 (PR #107, commit 299c4b6) + per-anchor renderer rules.
- `academic-paper/references/policy_anchor_disclosure_protocol.md` — LLM-prose runtime protocol for the new `--policy-anchor=<a>` track: 7-section flow covering inputs / G10 7-row precedence table / per-anchor render flows / auto-promotion forbiddance / venue-anchor conflict resolution / three-state completeness flag / 11-concern resolution map.
- `shared/policy_data/nature_policy.md` — canonical Nature substantive policy source; both the policy-anchor track and the v3.2 venue track cross-reference this path for the G4 dedup invariant.
- `scripts/check_policy_anchor_table.py` + `scripts/test_check_policy_anchor_table.py` — anchor table structural lint with 13 mutation tests + Nature dedup guard wired into the main lint command.
- `scripts/check_policy_anchor_protocol.py` + `scripts/test_check_policy_anchor_protocol.py` — protocol doc lint with 12 mutation tests covering §4.3 8 invariants + §4.4 11 concerns + G10 7-row precedence table + auto-promotion forbiddance + anchor inventory closed-enum.
- `scripts/policy_anchor_disclosure_referee.py` + `scripts/test_policy_anchor_disclosure.py` — executable specification (referee) of §3 G10 7-row decision table + 8 invariant predicates; 61 conformance tests covering every (input × expected output) combination + forbidden-path negative fixtures.

**Modified files:**

- `academic-paper/references/disclosure_mode_protocol.md` — `--policy-anchor=<a>` track added in parallel to v3.2 `--venue=<v>` track. Phase 1 dispatch becomes selector-aware (step 1a / step 1b venue / step 1c anchor). Venue-only flow unchanged; anchor flow delegates Phase 3+4 to `policy_anchor_disclosure_protocol.md`. Concern #7 venue+anchor conflict resolution enforced.
- `academic-paper/references/venue_disclosure_policies.md` — Nature entry gains derivation note + dedup pointer to `shared/policy_data/nature_policy.md`. v3.2 venue rendering content unchanged (derived view, manual sync to canonical source until future refactor).
- `.github/workflows/spec-consistency.yml` — 5 new CI steps wiring the new validators and conformance test suite into the existing spec-consistency job.

**§4.4 11 open concerns resolved** (4 user-chosen, 7 inline; full table in impl spec §3):
1. Track-selection lookup: explicit `slr_lineage` input from pipeline orchestrator (user-chosen).
2. Tool identity collection: auto-detect from session metadata (mirror v3.2 Phase 4).
3. Prompt scope: per-(tool × task) tuple per PRISMA M6.a.
4. IEEE section locator: free-form list with recommended IMRaD exemplars.
5. Nature image metadata: hybrid output channel (annotation block + suggested inline patches) (user-chosen).
6. UNCERTAIN per-facet finalization: USED-full + per-facet annotation alongside still-UNCERTAIN (user-chosen).
7. Venue+anchor conflict: reject conflicting selectors with explicit error.
8. Three-state completeness flag: full computation logic encoded in §6 of protocol doc.
9. Test set scope: 86 new tests covering 8 invariants + 10 concerns × {positive, negative}.
10. `ai_used:true` substantive-content gate: force v3.2 categorization flow (user-chosen).
11. G1 invariant scope: data layer untouched; non-renderer pipeline plumbing permitted.

**Known follow-up (out of #108 scope):** the academic-pipeline orchestrator does not yet emit `slr_lineage` on the documented `systematic-review → academic-paper full` handoff. Authors targeting `--policy-anchor=prisma-trAIce` must supply `mode=systematic-review` manually until that plumbing lands in a separate PR (touches `academic-pipeline/` + `shared/handoff_schemas.md`, outside §4.1 items 1-5 NO-CHANGE boundary).

**Regression status:** 967 baseline + 86 new tests = 1053 passing / 3 skipped / 0 failed. Public-repo boundary clean. Eight rounds of codex gpt-5.5 xhigh review (R1 4 P2 → R8 2 P2); shipped audit-trail-complete per user decision rather than pushing past Decision Doc 11-round high water mark. R8 P2 #1 captured as the known follow-up above.

### v3.7.3 — claim faithfulness locator + contaminated-source advisory (2026-05-12, in progress)

**External motivation:** Zhao, Wang, Stuart, De Vaan, Ginsparg, Yin "LLM hallucinations in the wild: Large-scale evidence from non-existent citations" (arXiv:2605.07723, 2026-05). Corpus-scale audit of 111M references across 2.5M papers across arXiv / bioRxiv / SSRN / PMC finds 146,932 hallucinated citations estimated for 2025 alone, with the inflection point at mid-2024, 85.3% of preprint hallucinations surviving into the published record, and Google Scholar increasingly indexing citation-only entries. The paper names the L3 (claim faithfulness) gap explicitly: *"real citations deployed to support claims the cited references do not actually make ... remains an open challenge for which reliable detection methods remain under active development."* v3.7.3 closes the locator-channel half of that gap (anchor infrastructure for future L3 audit) and surfaces two contamination signals (preprint post-LLM-inflection + Semantic Scholar unmatched) as advisory cite-time markers.

**L3-1 — Three-Layer Citation Emission (claim faithfulness locator):**

- `deep-research/agents/synthesis_agent.md`, `academic-paper/agents/draft_writer_agent.md`, `deep-research/agents/report_compiler_agent.md` gain `## Three-Layer Citation Emission (v3.7.3)` H2 section that extends v3.7.1 Two-Layer with a third hidden marker: `<!--anchor:<kind>:<value>-->` where `<kind>` ∈ `{quote, page, section, paragraph, none}`. Production-mandatory locator rule (R-L3-1-A) requires `<kind>` ≠ `none` for every visible citation; emitting `none` triggers finalizer MED-WARN-NO-LOCATOR (gate-refused). Quote anchors capped at 25 words by whitespace split (R-L3-1-B). Anchor values come from corpus context only — no frontmatter reads (R-L3-1-C, inherits v3.6.7 partial-inversion discipline).
- `academic-pipeline/agents/pipeline_orchestrator_agent.md` gains a `## Cite-Time Provenance Finalizer — v3.7.3 extension` H2 section: 4-cell matrix becomes 5-cell along a new precedence-zero locator-presence axis. NO-LOCATOR resolution: `[UNVERIFIED CITATION — NO QUOTE OR PAGE LOCATOR]<!--ref:slug--><!--anchor:none:-->`.
- `academic-paper/agents/formatter_agent.md` gains a `## Cite-Time Provenance Hard Gate (v3.7.1 + v3.7.3)` section formalizing the terminal hard-gate refusal across all three v3.7.x severity tiers (HIGH-WARN-NO-ORIGINAL, MED-WARN-NOT-CROSS-CHECKED, MED-WARN-NO-LOCATOR).

**L3-2 — Contaminated-source advisory signals:**

- `shared/contracts/passport/literature_corpus_entry.schema.json` adds optional `contamination_signals: { preprint_post_llm_inflection, semantic_scholar_unmatched }` object. Both sub-fields optional within the object; both default to absent (signals not computed). `additionalProperties: false` enforced on the sub-object. Backward compat: entries without the field stay valid.
- `deep-research/agents/bibliography_agent.md` gains `## Contamination Signal Computation (v3.7.3)` section. Signal 1 (`preprint_post_llm_inflection`): `year >= 2024 AND venue ∈ {arXiv, bioRxiv, medRxiv, SSRN, Research Square, Preprints.org}`. Signal 2 (`semantic_scholar_unmatched`): existing Semantic Scholar API protocol returns no match by DOI or title; exempted when `obtained_via: manual`; omitted (not `false`) on API degradation.
- Pipeline finalizer (in pipeline_orchestrator) annotates `ok` / `LOW-WARN` markers with `CONTAMINATED-PREPRINT` / `CONTAMINATED-UNMATCHED` / `CONTAMINATED-PREPRINT+UNMATCHED` suffix per `contamination_signals` state. Annotations are **advisory only** — they do NOT change the gate decision (v3.5 Collaboration Depth Observer precedent).

**Lint + tests:**

- New `scripts/check_v3_7_3_three_layer_citation.py` static lint: every `<!--ref:slug-->` must be followed by `<!--anchor:<kind>:<value>-->`; `quote` values ≤25 words; orphan anchors rejected.
- New `scripts/test_check_v3_7_3_three_layer_citation.py`: 14 tests covering positive (5 kinds × passing cases, contamination-suffix marker, LOW-WARN-resolved marker, multi-citation) + negative (bare ref, orphan anchor, invalid kind, 26-word quote).
- New 6 contamination_signals tests in `scripts/adapters/tests/test_literature_corpus_entry_schema.py`: absence / empty / both-false / both-true / unknown-subfield-rejected / non-boolean-rejected.
- New `V373ExtensionLineBudgetTest` in `scripts/test_v3_6_7_phase_6_6.py`: 60-line budget for `## Cite-Time Provenance Finalizer — v3.7.3 extension` block; existing Phase 6.6 +60 v3.6.7 budget test updated to subtract both v3.7.1 Step 3b AND v3.7.3 extension lines.

**Regression status (final, post round-10 convergence):** 967 tests pass, 3 skipped, 0 failed (42 new tests across rounds 1-10 fixes; pre-review baseline was 925). v3.6.7 + v3.6.8 + v3.7.1 + v3.7.2 lints all PASS unmodified. v3.6.7 PATTERN PROTECTION blocks remain byte-equivalent (SHA gate v2 unchanged). Material Passport literature_corpus_entry schema backward compatible (new contamination_signals field optional; cross-field rules only fire when explicitly set). New v3.7.3 lint wired into spec-consistency.yml CI workflow per F18.

**Cross-model review closure (2026-05-12, 11 rounds total — 10 codex + 1 gemini cross-model):**

| Round | Reviewer | Findings | Closures |
|---|---|---|---|
| 1 (initial) | Codex | 0 P1 / 2 P2 | F3 (untracked artifacts → closed at commit), F4 (NO-LOCATOR acknowledgment contradiction → removed `/ars-mark-read` promise from formatter+finalizer+spec Q5) |
| 1 (initial) | Gemini 3.1-pro-preview | 2 P1 / 2 P2 / 1 P3 | F1 (hyphen-encode → 3 prompts + lint + 3 tests), F2 (whitespace/newline tolerance → finalizer clarification + 4 tests), F5 (year<2024 schema cross-field → allOf + 4 tests), F6 (venue list 6 → 10 added ChemRxiv / EarthArXiv / OSF Preprints / TechRxiv), F7 (fenced code block isolation → helper + 4 tests) |
| 2 | Codex | 0 P1 / 2 P2 | F8 (lint regex widened to {0,2} suffix tokens → 3 tests), F9 (empty non-`none` anchor value rejection → 5 tests) |
| 3 | Codex | 0 P1 / 2 P2 | F10 (premature HTML comment terminator sentinel scan → 3 tests), F11 (schema manual-entry exemption → 4 tests) |
| 4 | Codex | 0 P1 / 1 P2 / 1 P3 | F12 (orphan_pattern lookbehind removed → 3 tests), F13 (schema venue list description sync 6 → 10) |
| 5 | Codex | 0 P1 / 1 P2 | F14 (malformed ref broad-scan detector → 4 tests) |
| 6 | Codex | 0 P1 / 1 P2 | F15 (prompt-vs-lint alignment on `--` rule → 2 tests; prompts loosened to match lint's narrower contract) |
| 7 | Codex | 0 P1 / 3 P2 | F16 (finalizer status-suffix-tolerant for revision-loop reruns), F17 (standalone deep-research self-gate), F18 (CI workflow wires v3.7.3 lint into spec-consistency.yml) |
| 8 | Codex | 0 P1 / 3 P2 | F19 (decode value before empty check → 3 tests), F20 (formatter raw `anchor:none` gate), F21 (F17 self-gate scoped to standalone mode only via prompt mode-detection) |
| 9 | Codex | 0 P1 / 1 P2 | F22 (self-gate also rejects bare refs without anchor — parity with pipeline finalizer's precedence-zero "no anchor = anchor=none" rule) |
| **10 (final)** | **Codex** | **0 findings** | **Convergence achieved.** |

- **No cross-finding overlap across reviewers.** Codex and Gemini found complementary defect classes — Codex caught contract gaps + regex completeness + architectural integration; Gemini caught HTML comment parsing edge cases + cross-field schema rules + venue completeness. This is the canonical value split documented in `feedback_codex_workflow_consolidated.md`.
- **Cascade pattern:** each round's closure introduced no new defects in its OWN scope, but interactions with other v3.7.3 surfaces surfaced new layers — F19 was an F9 layer (encoded-whitespace bypass after the F9 raw-value fix), F21 was a F17 regression (self-gate ran in pipeline mode and interfered with finalizer), F22 was an F17+F21 boundary (only catching explicit `none` markers missed bare-ref legacy form). The 10-round convergence trajectory is consistent with the v3.6.8 18-round implementation precedent and `feedback_complex_spec_review_inventory_pattern.md`.
- **F23+ not yet observed.** Round 10 returned no findings on the 9th amended branch state, providing the convergence signal. Future codex challenge mode (adversarial scope) may surface architecturally deeper gaps; tracked separately as a v3.7.4+ concern.

**Out of v3.7.3 scope (tracked as follow-up issues):**

- v3.7.4 retrieval-side hardening: OpenAlex + Crossref triangulation as second contamination signal (Vector 2 currently single-source via Semantic Scholar only).
- v3.8 L3 full audit: `claim_ref_alignment_audit_agent` running LLM-as-judge over (claim, ref full-text) pairs. v3.7.3 anchors are the input; v3.8 verifies anchor content faithfulness.
- AI disclosure schema split (per-stage: drafting / editing / **reference suggestion** / data analysis) — Zhao et al. Fig. 1l correlates AI-writing-signature with hallucination rate.
- Public README motivation update citing arXiv:2605.07723.
- Migration tool for legacy `literature_corpus[]` entries lacking `contamination_signals`.

Spec: `docs/design/2026-05-12-ars-v3.7.3-claim-faithfulness-and-contaminated-source-spec.md`.

### Backlog — gbrain harness borrow analysis (2026-05-10, post codex review)

Source: 2026-05-10 analysis of `garrytan/gbrain` (14.2k★ agent harness for OpenClaw/Hermes), with codex cross-model review same day. Two candidates surfaced; they have different risk profiles and are tracked separately.

**Candidate A — Shared `shared/_invariants.md` cross-skill rules file** (gbrain pattern P3). Status: backlog, low-risk.

ARS cross-cutting rules are scattered today: Iron Rules in adapter overview, hedging contract in `protected_hedging_phrases.md`, citation precedence in agents' frontmatter, integrity gates referenced from multiple SKILL.md. When a rule evolves (e.g. v3.6.5 corpus protocol Iron Rules), secondary mentions drift.

Shape if adopted:
- `shared/_invariants.md` enumerating **positive invariants only** (no rejected-reasoning column; that was the contamination vector in the 2026-05-10 anti-pattern-table evaluation)
- File stays short, normative, and example-free — additional examples turn invariants into demonstrations and re-introduce few-shot drift
- Each SKILL.md references it via a stronger convention than `## See Also` (which reads as optional reading); proposed wording at adoption time
- Frontmatter `validated_against: <version>` enables a stale-reference grep job on minor bumps. **The grep job detects version drift only — it does NOT validate semantic compliance.** Semantic checks remain a human / codex review responsibility.

**Candidate B — Declarative `shared/_review_pairs.yaml` cross-model review config** (gbrain pattern P6). Status: **needs design spike before becoming a real candidate**, higher-risk.

ARS cross-model review is currently invoked imperatively: `ARS_CROSS_MODEL=1` env flag + manual codex review per phase. A declarative `(deliverable_kind, reviewer_model, dimensions, when_to_invoke)` map could improve reproducibility for Stage 2.5 / 4.5 integrity gates and Phase 6 in-pair evaluator review.

Three open problems before this is shippable:
1. **Refusal-routing semantics conflict.** gbrain's chain (primary → DeepSeek → Qwen → Groq, silent switch) routes past refusal; ARS treats reviewer disagreement as signal. Borrowing the YAML format without resolving this imports the wrong invariant. Likely answer is "borrow the declarative-pairing shape, drop the refusal-routing chain entirely."
2. **Embedding governance in config.** A YAML that decides "this deliverable triggers this reviewer with these dimensions" is workflow policy. Wrong shape locks in a bad routing decision across all phases. Needs a usage survey of existing manual invocations before designing the schema.
3. **Lower confidence than Candidate A.** ARS already has review phases and cross-model invocation working manually; the missing piece is reproducibility, not the capability. If manual invocation isn't causing missed reviews or inconsistent reviews in practice, this should drop too.

Rejected from same gbrain analysis: P1 RESOLVER.md dispatcher (10 slash commands serve dispatch), P4 trust boundary (research tool, no untrusted caller class), P5 pain-triggered subagent routing (covered in user CLAUDE.md, repo-level not relevant). **P2 friction protocol** is a soft reject — codex review pointed out a first-class friction CLI captures pain at the moment of pain, which 5+ round codex review at deliverable-time does not. Re-examine if ARS skill development surfaces recurring author-time pain that retrospective review doesn't capture.

Meta-lesson from this analysis: "we already do something adjacent" is weaker than it sounds as a reject reason. The test is whether the existing mechanism captures the same signal at the same time with the same enforcement strength.

### Added (v3.6.7 Step 6 Phase 6.8 — Step 8 evaluation case)

- **17 micro-fixtures + 1 chapter-level integration fixture** under
  `tests/fixtures/v3_6_7_pattern_eval/` exercising the 17 numbered downstream
  -agent patterns (A1–A5, B1–B5, C1–C3, D1–D4) per spec §7. Each micro
  fixture: `manifest.json` (`fixture_kind: "micro"`) + `upstream_context/`
  (`passport_snippet.yaml` + `prior_artifacts/`) + `bad_run/` + `good_run/`
  with `deliverable.md`, `expected_audit_findings.yaml`,
  `expected_orchestrator_action.yaml`. Integration fixture under
  `integration/chapter_level_run/` exercises A3+C2+D4+C1 across 3-round
  MATERIAL escalation → ship_with_known_residue acknowledgement per §7.3.
- **`scripts/check_pattern_eval_manifest.py`** — fixture_kind discriminator
  routing micro (§7.2) vs integration (§7.3) JSON Schema 2020-12 manifest
  schemas; `audit_verdict.schema.json` validation on every
  `expected_audit_findings.yaml`; path-safety rejects absolute paths and `..`
  segments; coverage cross-check enforces 17/17 numbered IDs covered (with
  hard-fail on unknown directory names per §7.5).
- **`scripts/test_pattern_eval_runtime.py`** — 112-test parametrized harness
  reading expected verdicts as synthesized output and asserting against
  expected orchestrator action. Per-pattern parametrized tests (BAD signal +
  GOOD passes + run_id F1 regex + BAD/GOOD uniqueness); integration state
  runner driving §7.3 5-step procedure (load verdicts → drive §5.6 → verify
  pipeline state per round → feed escalation user_response → verify final
  passport state); Path A re-verification axis (≥6 A7 happy-path legs at
  rounds 2+3); finding-id lineage carry-forward per audit-template Section 6;
  per-phase synthetic injections (24 of 26 PHASE_TO_PASSPORT_MUTATION rows
  validated for "none" / "appended"); A1.5 supersession-preflight axis tests.
- **`scripts/test_run_codex_audit_e2e.py`** — Phase 6.1 deferred end-to-end
  dispatch test (Linux Bash 4+ only; macOS stock Bash 3.2 self-skips). Mocks
  codex CLI via PATH-prefix shim emitting canonical Phase 2 JSONL stream.
  Validates wrapper produces 4 contract files + 3 diagnostic files; proposal
  entry validates against `audit_artifact_entry.schema.json --mode proposal`
  (Pattern C3 defense — `verified_at`/`verified_by` absent); `--dry-run`
  writes nothing; `--round=2` without `--previous-findings` rejected with
  `EX_USAGE`.
- **`.github/workflows/spec-consistency.yml`** — 4 new CI steps: Phase 6.8
  manifest validation, pattern-eval-unit (micro fixtures + phase inventory +
  synthetic non-supersession), pattern-eval-integration (integration fixture
  + synthetic supersession), Phase 6.1 wrapper E2E (Linux runner only).
- **`docs/design/TODO-l-doc-1-18-patterns-prose-retirement.md`** — files
  L-doc-1 follow-up enumerating 8 retirement locations for the docs-only PR
  retiring "18 patterns" prose to "17 patterns" per §9.2.
- **Spec amendments** at `docs/design/2026-04-30-ars-v3.6.7-step-6-orchestrator
  -hooks-spec.md`: §7.4 success criterion 1 prose updated for C2 MINOR
  special case + D2 PASS convergence-policy assertion; §7.4 phase example
  updated `escalation` → `B11`; §7.6 deployment note explaining named-step
  CI deployment (vs literal "two separate jobs"); §9.2 L-doc-1 row points at
  the TODO file; §7.3 example manifest snippet updated to F-101/F-103.

### Notes

- **11 codex review rounds converged to 0 findings**. Cumulative 24
  findings closed (4 P1 + 18 P2 + 2 P3) across rounds 1-10.
- 135 Phase 6.8-specific tests; total repo regression 742 pytest + 251
  unittest = 993 green + 3 skipped (macOS Bash 3.2 wrapper E2E gate).
- v3.6.7 Step 6 + Step 8 now structurally complete: prompt-level pattern
  protection (Step 1+2) + version sweep (Step 7) + runtime audit-artifact
  gate (Step 6 §1-§11 + Phases 6.1-6.7) + synthetic evaluation case
  (Phase 6.8) deliver the §10 ship-quality target.

## [3.7.0] - 2026-05-05

> **Claude Code plugin packaging.** ARS now installs in one line on Claude Code
> CLI / VS Code / JetBrains via `/plugin marketplace add Imbad0202/academic-research-skills`
> + `/plugin install academic-research-skills`. The traditional
> `git clone + symlink to ~/.claude/skills/` flow continues to work — both
> tracks are first-class.

### Added

- **Plugin manifest + marketplace metadata** (Phase 1, PR #68).
  `.claude-plugin/plugin.json` declares the suite. `.claude-plugin/marketplace.json`
  registers the plugin so a single GitHub-hosted endpoint serves both the
  marketplace listing and the plugin source. `skills/` directory carries
  relative symlinks to the four existing skill directories so the plugin
  loader auto-discovers them without moving repo layout.
- **10 slash commands** at `commands/ars-*.md` (Phase 2.1, PR #69) mapping
  `MODE_REGISTRY.md` entries to `/ars-<mode>` triggers. Model routing pinned
  in each command's frontmatter — `opus` for `full` and `revision-coach`
  (architectural / review-interpretation depth), `sonnet` for the other 8.
  No Haiku per `feedback_no_haiku.md`.
- **3 plugin-shipped agents** at `agents/*_agent.md` (Phase 2.1, PR #69)
  as relative symlinks to the v3.6.7-hardened downstream agents in
  `deep-research/agents/`: `synthesis_agent`, `research_architect_agent`,
  `report_compiler_agent`. Underscore filenames preserved to match
  `scripts/check_v3_6_7_pattern_protection.py` hard-pinned paths and the
  INV-3 manifest-confined Clause 1 invariant. Symlinks (not copies) preserve
  a single source of truth and prevent the Pattern C3 attack surface that
  v3.6.7 §6 inversion sweep + INV-1/2/3 lint closes.
- **`model: inherit`** added to those three source agent frontmatters
  (PR #69 R1 codex finding). Inherit chosen over pinning `sonnet` so an
  Opus session running the full pipeline keeps Opus agents (instead of
  being capped) while the user's existing PreToolUse `warn-agent-no-model.sh`
  hook gates Haiku at the dispatch boundary.
- **SessionStart announce hook** at `hooks/hooks.json` +
  `scripts/announce-ars-loaded.sh` (Phase 2.2, PR #70). When the plugin
  loads, the hook injects `additionalContext` listing the 10 slash commands,
  the 3 plugin agents, and a token-budget pointer into the LLM's first
  turn. `startup` and `clear` source values get the full announce; `resume`
  and `compact` get a one-line ack to avoid burning context on every
  resume. Bash 3.2 compatible — runs on macOS stock `/bin/bash` with no
  `brew install bash` requirement. `${CLAUDE_PLUGIN_ROOT}` quoted for
  install paths containing spaces.
- **`docs/PERFORMANCE.md` + `.zh-TW.md`** subsection
  "v3.7.0 Plugin agents and model routing" explaining `model: inherit`
  semantics and the current 3-agent scope boundary.
- **`docs/ARCHITECTURE.md`** Evolution Timeline extended with v3.6.7 / v3.6.8 /
  v3.7.0 entries.
- **README + README.zh-TW** version badge bumped to v3.7.0; Pipeline section
  heading bumped to v3.7; CHANGELOG entry added.

### Deferred (future release)

- **SubagentStop → `run_codex_audit.sh` codex audit hook** (Phase 2.2 scope
  reduction). Two compounding reasons: (a) wrong invoker class —
  `run_codex_audit.sh` lines 4–7 forbid same-session in-LLM invocation
  (Pattern C3 attack surface), and the original PostToolUse Write|Edit
  matcher would fire from inside the producing session; (b) contract gap —
  the SubagentStop hook payload carries no stage/deliverable info, so a
  wrapper would have to half-infer those required arguments. Real
  audit-hook integration deferred to a future release when ARS gains a stage/deliverable
  propagation contract. See
  `docs/design/2026-04-30-ars-v3.7.0-plugin-packaging-roadmap.md`
  Update note 2026-05-05 (Phase 2.2 scope reduction).

### Changed

- `academic-pipeline/SKILL.md` frontmatter `version: "3.7.0"` + H1 +
  Version Info table.
- `MODE_REGISTRY.md` Last updated bumped to `v3.7.0 (2026-05-05)`.
- `.claude/CLAUDE.md` Skills Overview row + Suite version footer bumped
  to 3.7.0.
- `scripts/check_spec_consistency.py` lint pins (Suite version, README
  badge, MODE_REGISTRY heading, CHANGELOG section heading) bumped to
  v3.7.0.

### Unchanged

The four skill directories, all 25 modes, agent prompts, schema files,
and lint contracts. Plugin packaging only adds new top-level surface
(`commands/`, `agents/`, `hooks/`, `.claude-plugin/`, `skills/` symlink
dir, three plugin-agent `model: inherit` frontmatter additions).
Existing 4.3k clone-install users see no breaking change.

### Codex review chain

8 inline iterative rounds + 3 fresh PR-level rounds across the three
PRs (#68 / #69 / #70), all converging to 0 P0/P1/P2 findings before
merge. The Phase 2.2 fresh PR review caught one P2 (unquoted
`${CLAUDE_PLUGIN_ROOT}` breaking install paths with spaces) that the
inline rounds missed — confirms the value of separating implementation
review (inline) from contract / install-time review (fresh).
Reference: `feedback_codex_review_vs_resume_audit_scope.md`.

## [3.6.8] - 2026-05-03

> **Naming note**: this release ships the **v3.6.6 generator-evaluator contract**
> spec (`docs/design/2026-04-27-ars-v3.6.6-generator-evaluator-contract-design.md`)
> and its implementation. The v3.6.6 work landed after v3.6.7 due to project
> sequencing; the design doc retains the v3.6.6 internal naming for the
> contract gate version (`writer_full` / `evaluator_full` mode, Schema 13.1,
> `pre_commitment_artifacts` + `disagreement_handling` schema fields), while
> the suite release is tagged v3.6.8 to keep the CHANGELOG monotonic.

### Added

- **Schema 13.1 generator-evaluator contract gate** for `academic-paper full`
  mode (`shared/sprint_contract.schema.json`, design doc §3): two new `mode`
  enum values (`writer_full` + `evaluator_full`); two new optional top-level
  fields (`pre_commitment_artifacts` writer-only with
  `acceptance_criteria_paraphrase.minimum_dimensions`; `disagreement_handling`
  evaluator-only with `paraphrase_minimum_dimensions` + `scoring_plan` +
  `pre_commitment_check_protocol` + `disagreement_resolution`); 12 `allOf`
  branches enforcing reviewer- / writer- / evaluator-conditional gates
  (existing 2 + 10 new per design doc §3.5 table).
- **Two new shipped contract templates**: `shared/contracts/writer/full.json`
  (writer dimensions D1 section_completeness / D2 citation_density /
  D3 argument_blueprint_fidelity / D4 total_word_count /
  D5 per_section_word_count / D6 acknowledged_limitations /
  D7 register_consistency; F-conditions F1/F4/F2/F3/F0; no `scoring_plan`)
  and `shared/contracts/evaluator/full.json` (evaluator dimensions
  D1 originality / D2 methodological_rigor / D3 evidence_sufficiency /
  D4 argument_coherence / D5 writing_quality; F-conditions F1/F2/F3/F6/F4/F5/F0;
  full `scoring_plan` + `disagreement_handling`). Templates already shipped on
  the spec branch as design-time artefacts since 2026-04-28; this release
  promotes them to live status atomically with the Schema 13.1 upgrade.
- **Two-phase orchestration inside `academic-paper full` mode** (design doc §5):
  Phase 4 splits into Phase 4a paper-blind writer pre-commitment + Phase 4b
  paper-visible drafting + self-scoring. Phase 6 splits into Phase 6a
  paper-blind evaluator pre-commitment + Phase 6b paper-visible scoring +
  decision. Phase-numbered `<phase4a_output>` / `<phase6a_output>` data
  delimiters mirror the v3.6.2 reviewer pattern. Lint counts: writer 3+4 /
  evaluator 5+5 / reviewer 5+6 (reviewer surfaces remain zero-touch per §3.6).
  `[GENERATOR-PHASE-ABORTED]` abort tag with 5% / three-month operational
  monitor.
- **`academic-paper/SKILL.md` `## v3.6.6 Generator-Evaluator Contract Protocol`
  orchestration block** (101 lines): four-call structure with system-vs-user
  content discipline, schema-vs-runtime emission distinction, per-phase lint,
  abort handling, two valid Stage 3 entry paths (standard F0/F4 + exceptional
  F5), cross-session resume scope. Plus a new `## Known limitations` section
  carrying the graceful-degradation forward note (v3.6.7 candidate) + the
  cross-session resume `pre_commitment_history[]` forward note (v3.6.7+
  candidate) + in-pair Phase 6 evaluator vs external `academic-paper-reviewer`
  tech debt.
- **`academic-paper/agents/draft_writer_agent.md` + `peer_reviewer_agent.md`**
  each gain a verbatim `## v3.6.6 Generator-Evaluator Contract Protocol`
  section with the system-prompt sub-sections for Phase 4a/4b (writer) and
  Phase 6a/6b (evaluator). The orchestrator includes the relevant sub-section
  verbatim in the system prompt for the corresponding call; user content
  carries contract JSON, paper metadata, delimiter blocks, and upstream
  artefacts per the SKILL.md discipline.
- **`scripts/check_sprint_contract.py` SC-* mode-gating audit** (per §7.1
  implementation requirement): SC-5 (measurement_procedure canonical outputs)
  and SC-11 (panel_size sanity) now mode-gated to
  `mode.startswith("reviewer_")` so they do not noise on clean writer /
  evaluator templates. SC-9 (paraphrase_minimum_dimensions exceeds dim count)
  extended across all three mode families: reviewer reads
  `mp.paraphrase_minimum_dimensions`, writer reads
  `pre_commitment_artifacts.acceptance_criteria_paraphrase.minimum_dimensions`,
  evaluator reads `disagreement_handling.paraphrase_minimum_dimensions`.
  Mode-agnostic warnings (SC-1 baseline lag, SC-2 single dimension, SC-3 no
  mandatory, SC-4 orphan dim ref, SC-7 conflicting actions, SC-10 unreferenced
  mandatory/high) unchanged.
- **17 new validator tests** (54 → 71 total): 4 writer/evaluator template
  positive tests; 5 schema-branch negative tests covering branches 11 / 12 /
  4 / 5 / 6 hard-fail (cross-mode field leakage intentionally NOT a v3.6.6
  hard-fail per §7.1 R1 settled — v3.7.x `not`-clause hardening is the
  long-term fix); 2 §3.6 reviewer regression tests
  (`test_existing_reviewer_contracts_still_valid_under_13_1` +
  `test_byte_equivalent_validation_for_reviewer_contracts`); 6 SC-5/SC-9/SC-11
  mode-gating tests.
- **`scripts/check_v3_6_6_ab_manifest.py`** (new) implements the §7.5 manifest
  CI lint: schema-shape checks per §6.2 (top-level required fields with
  declared types; per-paper required fields; paper_id uniqueness; aggregate
  role counts 6+1; paper-A paper_type families 3 × 2; paper-A required
  judge_output_baseline; paper-C must-have known_failure_mode +
  failure_evidence; paper-C must-not-have judge / metrics fields);
  path-existence checks (mode-conditional + populated-optional);
  reverse-scan against fixture-orphans; exit-1-on-malformed-YAML mirrors
  `check_sprint_contract.py` convention.
- **`.github/workflows/spec-consistency.yml`** extends the "Validate sprint
  contract templates" step to iterate writer + evaluator template directories
  alongside the existing reviewer loop, and adds a new "Validate v3.6.6 A/B
  fixture manifest" step running the new manifest CI lint script as an
  additional step inside the existing `spec-consistency` job.
- **`tests/fixtures/v3.6.6-ab/` A/B evidence fixture stub** (30 files):
  manifest.yaml + README.md + 6 paper-A inputs/baseline + 1 paper-C
  inputs/baseline + Stage 3 reviewer excerpt + 6 codex-judge baseline
  placeholders. `manifest_lint_mode: spec_branch`, `fixture_version: 0.1.0`.
  Each placeholder explains the expected populated content; real fixture data
  (existing deep-research synthesis reports for paper-A; v3.6.5 session log
  + Stage 3 reviewer excerpt for paper-C; codex gpt-5.5 + xhigh judge runs
  against paper-A baseline) populates in follow-up commits before the
  v3.6.6 implementation work fully completes.
- **`academic-paper-reviewer/references/sprint_contract_protocol.md`
  cross-reference** noting Schema 13.1 since v3.6.6 + pointing readers at
  `academic-paper/SKILL.md` + design doc §5 for the parallel
  generator-evaluator protocol. The reviewer protocol itself is byte-equivalent
  across v3.6.2 → v3.6.8 (zero-touch promise per §3.6).

### Changed

- **Suite version**: v3.6.7 → v3.6.8 (per the naming note above; design doc
  retains v3.6.6 for the contract gate version).
- **`academic-pipeline` skill version** bumped from v3.6.7 to v3.6.8 in the
  `.claude/CLAUDE.md` Skills Overview table.

### Deferred

- **Real fixture data populate** for `tests/fixtures/v3.6.6-ab/` (30
  placeholders → real paper-A inputs + baseline + paper-C session log + codex
  judge runs) lands in follow-up commits.
- **Treatment runs** (writer Phase 4a/4b + evaluator Phase 6a/6b on the seven
  fixtures), **codex judge against treatment**, and **metrics computation
  + summary.md** require actual `academic-paper full` invocations + Semantic
  Scholar API + codex CLI runs; deferred to follow-up commits before the
  fixture-completeness work concludes.
- **manifest_lint_mode flip** from `spec_branch` to `implementation_pr`
  co-lands with the treatment population in the same atomic merge state per
  §6.5 invariant 3.
- **ROADMAP §3.6.4 description correction** per design doc §9.3 ("Extend
  v3.6.2 sprint contract pattern to the existing `academic-paper`
  writer/evaluator pair via contract-gated phase splits and Schema 13.1
  conditional gates. No new agent files; existing `draft_writer_agent` and
  `peer_reviewer_agent` gain per-phase sub-section instructions") lands in
  the private ROADMAP.md (gitignored, lives in claude-memory-sync), not in
  this repo PR.

## [3.6.7] - 2026-04-30

### Added

- **Downstream-agent pattern protection layer** (`docs/design/2026-04-29-ars-v3.6.7-downstream-agent-pattern-protection-spec.md`).
  Hardens three downstream agents against 18 hallucination/drift patterns
  documented in the spec: `synthesis_agent` (A1–A5 narrative-side), the
  survey-designer mode of `research_architect_agent` (B1–B5 instrument-side),
  and the abstract-only mode of `report_compiler_agent` (C1–C3 publication-
  side), plus four cross-cutting patterns (D1–D4). Patterns observed in
  production output across multiple chapter-length runs.
- **Four reference files in `shared/references/`** carrying the operational
  contracts that protection clauses cite:
  - `irb_terminology_glossary.md` — anonymity vs confidentiality vs
    de-identification vs pseudonymization (B1).
  - `psychometric_terminology_glossary.md` — true reverse-coded vs contrast
    item, with construct-equivalence rule (B2).
  - `protected_hedging_phrases.md` — five-rule contract for upstream-marked
    hedge protocol (conservative inclusion, anchor every entry, no
    duplicates, verbatim preservation, conflict reporting) (C1).
  - `word_count_conventions.md` — whitespace-split standard (`body.split()`),
    3–5% buffer below hard cap, publisher conventions (C1).
- **Cross-model audit prompt template** at
  `shared/templates/codex_audit_multifile_template.md` — seven audit
  dimensions (cross-ref, hallucination, primary-source integrity, internal
  coherence, instrument quality, Round-N framing, COI adequacy) plus a
  mandatory three-part Section 4(f) check for `report_compiler_agent`
  bundles (whitespace-split cap-minus-buffer, protected-hedge verbatim,
  abstract no less hedged than body — failure of any sub-check is P1).
- **Static lint** at `scripts/check_v3_6_7_pattern_protection.py` enforcing
  protection-clause presence and obligation-phrase shape across the
  reference files, audit template, and three downstream agent prompts.
  Per-regex `allow_prohibition` flag scopes the prohibition exemption so
  prohibition-style obligations (`DO NOT simulate`, `must not claim
  audit-passed state`, `does not paraphrase`) do not leak the exemption to
  assertion-style obligations on the same Check. Span-restricted exemption
  rejects a second prohibition elsewhere in the bullet. Modal/advisory
  weakener coverage: `may`, `should`, `can`, `will`, `would`, `ought to`,
  `ideally`, `preferably`, `We recommend that`, `is/are recommended`,
  `is/are allowed`, `is/are permitted`, plus exception qualifiers
  (`except`, `unless`, `save when`).
- **Mutation test suite** at
  `scripts/test_check_v3_6_7_pattern_protection.py` with 29 tests
  preserving codex review evidence (R2–R6). Future checker regressions
  surface in CI rather than only in ad-hoc mutation runs.
- **CI wiring** in `.github/workflows/spec-consistency.yml` runs both the
  static lint and the mutation suite on every push and pull request.

### Changed

- **`deep-research/agents/synthesis_agent.md`** carries a `PATTERN
  PROTECTION (v3.6.7)` block with five clauses covering effect-inventory
  cross-section consistency self-check, pending-verification hedge wrap,
  one-line anchor justification, verbatim phrase boundary on quotes, and
  the prohibition on declarative claims about un-provided documents
  (with conditional-language fallback).
- **`deep-research/agents/research_architect_agent.md`** survey-designer
  mode carries a `PATTERN PROTECTION (v3.6.7)` block with five clauses
  covering IRB terminology pass-through, reverse-coded construct-
  equivalence justification, event-anchored retrospective default
  (calendar-anchored only when sample shares a common event date),
  neutral-balanced item phrasing with chapter argument vocabulary
  forbidden, and primary-source list enumerate-fully (no subsetting,
  no over-setting, no scope cross-contamination).
- **`deep-research/agents/report_compiler_agent.md`** abstract-only mode
  carries a `PATTERN PROTECTION (v3.6.7)` block with three clauses
  covering whitespace-split word budget plus 3–5% buffer with budget-
  protected hedges, explicit-temporal-bounds reflexivity disclosure
  (year range / past-tense disambiguating verb / "former" prefix; deictic
  phrases forbidden), and the anti-fake-audit guard (DO NOT simulate any
  audit step; DO NOT claim to have run codex/external review; output
  metadata must not claim audit-passed state).

### Notes

- v3.6.7 ships in two stages. **Step 1 + Step 2** (this entry) include
  the four reference files, the audit template, the static lint, the
  mutation test suite, the CI wiring, and the three agent-prompt
  protection blocks. **Step 6** (orchestrator hooks for automatic
  per-agent audit and anti-fake-audit guard wiring) and **Step 8**
  (synthetic evaluation case demonstrating all 18 patterns triggered +
  protected) ship in a follow-up PR. Step 6 is cross-agent runtime work
  that warrants its own design discussion and is intentionally decoupled
  from this prompt-and-lint PR.
- Codex review history: seven rounds of `gpt-5.5` + `xhigh` cross-model
  review reached SHIP-OK with zero P1 + P2 findings. R1 closed ten
  Step-1 findings; R2 closed four cascade gaps plus the per-Check
  `allow_prohibition` leak; R3 closed three P2 findings (span-restricted
  exemption, token→regex with imperative anchoring, `except/unless/
  save when` weakeners); R4 closed three P2 findings (modal verb scope
  expansion, §6 sub-clause coverage, lint→CI wiring); R5 closed one P2
  plus one P3 (`should/can/permitted` modals and the mutation test
  suite); R6 closed one P2 (`will/would/ought to/ideally/preferably/
  We-recommend-that` weakeners) and explicitly deferred orchestrator
  runtime hooks to the Step 6 follow-up PR. R7 surfaced only one P3
  add-counter signal (`try to / generally / where relevant` weakeners),
  which is non-blocking polish.
- ARS pipeline ship-quality target updates from "each agent produces a
  clean v1" to "end-to-end deliverable set passes independent xhigh
  cross-model audit at 0 P1 + P2 finding within three rounds" (per spec
  §10).

## [3.6.5.2] - 2026-04-27

### Changed

- **`docs/SETUP.md` Method 4 (claude.ai) recommendation revised**. Method 4b
  (Project + GitHub integration) is now presented first as the recommended
  claude.ai path, since it brings the repository into Project knowledge for
  reading and citation without losing fidelity. Method 4a (Custom Skill upload)
  is now explicitly marked as **not recommended for this suite**, with a
  rationale paragraph covering two compounding reasons:
  - ARS depends on Claude Code-only orchestration features. Each skill drives
    12-13 specialised agents through Claude Code's Task / subagent tooling
    and Material Passport file handoffs that resume across sessions.
    claude.ai Custom Skills do support multi-file packages with `scripts/`
    and code execution per Anthropic's documentation, but the Anthropic-
    documented scope of the claude.ai Custom Skill runtime does not include
    Claude Code's Task / subagent control surface or cross-session Material
    Passport handoffs. The recommendation is forward-looking based on those
    documented assumptions; we have not run a live upload to characterise
    the actual surfacing in claude.ai.
  - Trimming the four `description` fields below claude.ai's 200-character cap
    would weaken Claude Code and Cowork routing on the platforms the suite was
    actually built for. The Agent Skills specification and Claude Code Skills
    documentation both allow up to 1,024 characters; only claude.ai's upload
    UI enforces 200. Trading Claude Code and Cowork routing precision for
    partial functionality on the limited claude.ai path was judged not worth
    it.
- **Method 4a install commands kept in place** for users who decide to try it
  anyway, framed as "if you want to try this path despite the limitations"
  rather than as a recommended flow. The upload UI's expected rejection on
  description-too-long is documented as deliberate, not an oversight to fix
  later.
- **`docs/SETUP.zh-TW.md`** mirrors the English changes end-to-end.

### Notes

- Doc-only patch. No `SKILL.md` (frontmatter or body), no agent file, no
  schema, no script, no test, no workflow, and no version bump in any skill
  changed in this patch. The four current `description` fields stay at their
  Claude Code-native lengths (440-842 characters) so routing on Claude Code
  and Cowork remains intact.
- This patch is a scope change from the v3.6.5.2 originally forecast in the
  v3.6.5.1 SETUP doc. The earlier plan was a description trim; on review, the
  trim direction was abandoned because it would have damaged Claude Code and
  Cowork routing to unblock a path that delivers an untested partial fit
  anyway. The v3.6.5.1 SETUP text's forward-promise of a description trim is
  removed here.
- Issue [#44](https://github.com/Imbad0202/academic-research-skills/issues/44)
  receives a single consolidated reply on this PR's merge, summarising both
  v3.6.5.1 (SETUP doc rewrite) and v3.6.5.2 (Method 4a recommendation), and
  closes there.

## [3.6.5.1] - 2026-04-27

### Fixed

- **`docs/SETUP.md` Method 3 install paths** — Option A (symlink) and Option B (copy)
  now install each of the four skill folders separately into `~/.claude/skills/<skill-name>/`,
  matching the `<install-root>/<skill-name>/SKILL.md` discovery convention. The previous
  text installed the whole repo under `~/.claude/skills/academic-research-skills/`, which
  buried the four `SKILL.md` files one level too deep for Cowork / Claude Code discovery.
- **`docs/SETUP.md` Method 4 (claude.ai) restructured** — split into Method 4a
  (Custom Skill upload via Settings → Capabilities → Skills, the standard claude.ai Skill
  install path) and Method 4b (Project + GitHub integration, fallback knowledge mode and
  not a Skill install). The previous text framed GitHub integration as a Skill install
  path, which conflated content retrieval with skill execution. Method 4a documents the
  current 200-character `description` cap blocker (this entry originally forecast a
  description trim in v3.6.5.2; see the v3.6.5.2 entry above for the actual decision —
  Method 4a is documented as not recommended for this suite, and descriptions remain at
  their Claude Code-native lengths).
- **Method 3 prerequisites** — expanded from one sentence to a full prerequisites
  subsection covering Claude Desktop version, internet connectivity, Cowork process model,
  folder permissions, paid plan, and Team/Enterprise org-admin controls.
- **Method 4 prerequisites** — split per sub-method. 4a documents zip structure +
  description cap surfacing as upload-time errors; 4b documents GitHub authentication via
  the Anthropic connector, private-repo App authorization, and Team/Enterprise owner-level
  connector enablement.
- **Cowork UI terminology** — replaced "Cowork tab" / "working directory" with current
  Cowork UI labels: mode selector (Chat / Cowork), Tasks view, "Use an existing folder"
  in the left navigation panel, and Cowork Project as the canonical term.
- **Skill invocation framing** — clarified that Claude uses each skill's `description`
  for relevance routing rather than literal trigger-phrase matching, and documented the
  Cowork `/` command palette and `+` capability picker as explicit invocation surfaces.
- **Method 4 directory table** — added the `scripts/` row (required for Material Passport
  `literature_corpus[]` adapters and schema validators) and refreshed the project-capacity
  guidance against current Anthropic Project file limits (per-file 30 MB; file count is
  not artificially capped at 200).
- **`docs/SETUP.zh-TW.md`** — mirrored the English rewrite end-to-end so Traditional
  Chinese readers see the same structure and content for Methods 1-4.
- **`QUICKSTART.md` Step 1** — install commands aligned with the new Method 3 four-symlink
  approach.

### Notes

- Doc-only patch. No skill content (`SKILL.md`), no agent file, no schema, no script,
  and no test changed in this patch.
- Issue [#44](https://github.com/Imbad0202/academic-research-skills/issues/44) (philpav)
  reports SETUP problems on Cowork and claude.ai. v3.6.5.1 fixes the SETUP doc;
  this entry originally forecast a `SKILL.md` description-length fix in v3.6.5.2,
  but v3.6.5.2 instead documents Method 4a as not recommended for this suite (see
  the v3.6.5.2 entry above for the actual decision). Issue #44 receives a single
  consolidated reply and closes on v3.6.5.2 ship.

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
