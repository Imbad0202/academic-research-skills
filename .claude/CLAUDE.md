# Academic Research Skills

A suite of Claude Code skills for rigorous academic research, paper writing, peer review, and pipeline orchestration.

## Skills Overview

| Skill | Purpose | Key Modes |
|-------|---------|-----------|
| `deep-research` v2.11.0 | 13-agent research team | full, quick, socratic, review, lit-review, three-way-scan, fact-check, systematic-review |
| `academic-paper` v3.2.0 | 12-agent paper writing | full, plan, outline-only, revision, revision-coach, abstract-only, lit-review, format-convert, citation-check, disclosure, rebuttal-audit |
| `academic-paper-reviewer` v1.10.0 | Multi-perspective paper review (5 reviewers + optional cross-model DA critique) | full, re-review, quick, methodology-focus, guided, calibration |
| `academic-pipeline` v3.15.0 | Full pipeline orchestrator | (coordinates all above) |

## v3.15 Key Additions (release-gate hardening + prompt-debt retirement round 2 + defrift locks)

- **Prompt-debt retirement round 2 (#489 → #490).** Deep-scanned the 17 agents the #476 pass deferred (all 5 academic-pipeline, 5 deep-research, 5 academic-paper, field_analyst, compliance_agent) via 4 parallel batches + codex cross-model challenge. 13 findings (2 P1 + 11 P2, 2 user-rejected): both `socratic_mentor` agents carried live self-contradictions (stale "quit after 15 rounds" vs documented typical 20-30) — auto-end machinery merged to a single authority per file, threshold 30; the repo-wide stale "hook deferred to #134" enforcement sentence (false since PR #294) rewritten at 29 surfaces; few-shot/duplication trims across 7 agents. The 2026-06-10 F-007 negative-framing deferred item closes as verified-no-rewrite-needed. Report: `audits/harness-retirement-2026-07-04.md`.
- **Defrift locks (#491 → #492).** `check_v3_9_2_phase_boundary.py` invariant 4 pins the canonical enforcement sentence verbatim across all 23 Bucket A blocks (the drift class that sat wrong for a month now fails CI); new `check_setup_cross_model_parity.py` pins SETUP en/zh-TW `ARS_CROSS_MODEL` examples to each other and to the canonical model tables (table-column-scoped after a codex P1); local pytest manifest gains the v3.9.4 temporal test whose CI-only coverage caused a local-green/CI-red split (58 → 60 entries).
- **Release-gate hardening (#483, #487, #486).** `check_changelog_covers_merges.py` pre-tag gate (every release-worthy merge since the previous tag must be documented in CHANGELOG, fail-closed); version-consistency invariants 9-11 (release-notes body ≥100 chars, Last-Updated within ±7 days of the CHANGELOG date, Key-Additions heading matches suite version) + a `tag-version-match.yml` gate re-running the full lint at tag time; command-invariants gate pinning the SessionStart announce list to the actual 16-command inventory (announce list had drifted twice).
- **DOI badge fix (#482).** Served from shields.io (Zenodo's badge endpoint rate-limits GitHub's image proxy); link target stays the concept DOI.

## v3.14 Key Additions (Claude Science importability + eval-comment rendering + prompt-debt retirement)

- **Claude Science / GitHub-importer compatibility (#480).** `.claude-plugin/marketplace.json` declares explicit skill paths (`"skills": [...]`); symlink-blind GitHub-API importers (Claude Science "Import from GitHub", Windows checkouts) now find all four skills. Marketplace-root replace semantics keep Claude Code installs loading the same four skills — no content change, no double-loading. Verified end-to-end on Claude Science; import guide in README + docs/SETUP.md Method 5.
- **Eval-harness PR comment renderer (#479).** `scripts/render_eval_comment.py` renders a one-line verdict + per-task table + raw JSON folded into `<details>`, replacing the raw report dump. The row verdict mirrors the threshold gate's failure signal (aggregate AND per-class) with a CI-pinned agreement test; table cells escape pipes/line boundaries. Evaluation logic untouched.
- **Prompt-debt retirement (#476/#477 → #478).** Expired writing-harness scaffolds removed from `abstract_bilingual_agent`, `citation_compliance_agent`, `draft_writer_agent`, and `research_question_agent` (net −111 lines) after the 2026-07 harness-retirement audit (report under `audits/`); three-track verification (sub-agent audit + codex review + eval harness at 100%).
- **Platform Port Reminder CI (#473).** Remind-don't-block workflow surfacing the "Platform ports (community-maintained only)" policy when a PR adds a new top-level directory.
- **Changelog backlog rollup.** 16 `[Unreleased]` entries whose code shipped before the v3.13.0 tag (#390 diff/patch revision mode, #394 submission-package verifier, #215/#216 eval gold sets, and more) are versioned under 3.14.0 with a provenance note.

## v3.13 Key Additions (portability + verifier reach + guard correctness)

- **Write-scope guard: `CLAUDE.md` dropped from infra-protected globs (#459).** Closes the residual half of #448/#449. Under the git-clone + symlink install layout `plugin_root` collapses onto `workspace_root`, so the bare `CLAUDE.md` / `.claude/CLAUDE.md` infra globs re-denied the user's own `CLAUDE.md`. `CLAUDE.md` is documentation, not a load-bearing enforcement file, so it is removed from the infra list; every load-bearing file (guard script, manifest, hooks, plugin metadata, agent frontmatter, lint) stays protected.
- **Windows Python hook portability + graceful no-Python degradation (#454).** The PreToolUse write-scope guard is now launched via a cross-platform `hooks/run_guard.sh` that finds a real interpreter (rejecting the 0-byte Microsoft Store `python3` stub) and runs the guard as a time-bounded supervised subprocess; if no interpreter is found or the guard misbehaves, the launcher emits a valid pass-through and never spams the hook log.
- **Provider-agnostic cross-model verification (#455).** The cross-model verification layer accepts OpenAI-compatible endpoints (MiMo, DeepSeek, self-hosted) alongside first-party OpenAI, with the grounded first-party path preserved and never silently downgraded.
- **Opt-in Socratic adjacent-framing probe (#461; `deep-research` 2.10.0 → 2.11.0).** When `ARS_SOCRATIC_ADJACENT_PROBE=1`, the Socratic Mentor may surface ONE adjacent research framing as a pure question during exploratory Layer-1 framing (STORM-borrowed perspective expansion). Default OFF, prose-layer only, Kong L2 verb-test bounded.

Spec: `docs/design/2026-06-16-448-infra-protection-plugin-root-scope-spec.md` (+ the #454/#453/adjacent-probe design docs).

## v3.12 Key Additions (Kong auto-research feature track + partial-evidence decomposition)

**External motivation:** Kong et al. arXiv:2605.18661 (2026), *AI for Auto-Research: Roadmap & User Guide*. v3.12 ships the Kong feature track plus the §F.3.2 partial-evidence-trap work (Kim et al. arXiv:2605.20668v1), all additive and backward-compatible. `academic-pipeline` tracks the suite at v3.12.0; the other three skill versions are unchanged.

- **Experiment Provenance Intake + claim→experiment alignment (#260).** A schema-first evidence-ledger layer for experiment-backed claims — intake and alignment only; the scholar runs experiments externally and ARS never executes them. New `experiment_provenance[]` Material Passport aggregate (nested `repro_lock`, `planned_vs_executed[]`, `negative_results[]` / `known_limitations[]`) + a fourth ref_slug-less `experiment_alignment_results[]` aggregate with a MECE verdict enum, verdict produced AT the integrity gate (worst-verdict-wins on mixed-evidence claims). Seven cross-array invariants (EP-INV-1..5 / EA-INV-1..2) + fail-closed `experiment_intake_declaration` legacy boundary.
- **Figure/Table Fidelity Gate (#261).** Extends the VLM Figure Verification Protocol with a `figure_table_trace[]` prose contract — checks whether a caption's interpretation follows from the data and whether the manuscript cites the artifact for a claim it actually supports. Stage 4.5 Phase C3. Prose-layer only (no schema).
- **Cross-Paper Contradiction inventory (#262).** A `synthesis_agent` Step 3b emitting `cross_paper_tensions[]` so the assessed paper-pairs and unresolved tensions are enumerable for scholar confirmation, with a mandatory Coverage Note stating the recall limitation. Prose-layer only.
- **Partial-evidence decomposition (#213 / #214).** Sub-claim decomposition before judgment in both the citation judge (#213, schema + INV-19 + calibration) and the editorial synthesizer (#214, prose-layer), closing the §F.3.2 partial-evidence trap on both layers.
- **Guidance + interpretive layer.** Concise-output + pressure-stable boundary reinforcement across the report-producing reviewers (#274); a same-family / rubric-aware calibration epistemic note (#273); the retrieved-content instruction/data boundary as a standing principle (#367) — all guidance/interpretive, with explicit epistemic-status lines (no runtime-enforcement claim).
- **Negative scope + release discipline.** The Kong META (#255) closed with a POSITIONING.md "Rejected mechanisms" section + two Tier D design-lesson docs; version-consistency lint extended to invariants 5–7 (#357) and ARCHITECTURE component-version policing (#345).

Spec: `docs/design/2026-06-08-260-experiment-provenance-intake-spec.md` (+ the Kong sub-issue design docs).

## v3.11 Key Additions (#182 — deterministic citation verification gate)

**External motivation:** Zhao et al. arXiv:2605.07723 (2026-05). #182 promotes a **deterministic citation-existence verification gate** that runs independently of LLM peer review, closing the lookup-channel half of the hallucinated-citation problem. v3.11 implements all five spec deltas; the gate **inherits the v3.10 `terminal_policies` opt-in model** rather than introducing a second hard-block philosophy.

- **Four-index verification (Delta 1).** New `scripts/arxiv_client.py` adds arXiv (no API key) as the fourth resolver alongside Semantic Scholar / OpenAlex / Crossref. The v3.9.0 contamination triangulation matrix extends from three indexes (k=0..3) to four (k=0..4) with `arxiv_unmatched`; four new advisory suffixes render (`CONTAMINATED-ARXIV-UNMATCHED` at the k=1/k_max=1 arxiv-only carve-out, `CONTAMINATED-QUADRANGULATION-UNMATCHED` at k=4/k_max=4, + two PREPRINT compositions). All advisory — the refusal list is unchanged (R-L3-2-E).
- **Persistent cache (Delta 2).** `scripts/verification_cache.py` — local SQLite (`~/.cache/ars/verification.db`, `ARS_VERIFICATION_CACHE_PATH` override, 90-day TTL) so each paper is verified once across drafts. New `/ars-cache-invalidate <citation_key>` command.
- **`citation_existence` terminal policy (Delta 3 / C-V6).** New `terminal_policies` key `citation_existence` ∈ {`advisory`, `strict`} (per-key absence = advisory). The finalizer is the sole policy evaluator; `formatter_agent.md` rule 12 refuses on a `lookup_verified == false` row **only under `strict`**. `false` is narrowed to **ID-keyed unmatched** (C-V6(a)) — a title-only-unmatched legitimately-unindexed citation is `unresolvable`, never blocked (acknowledged precision-over-recall tradeoff, mirroring `strict_articles_only`). Detection is unconditional; only terminality is policy-gated.
- **Unified status surface + standalone API (Delta 4+5).** `citation_verification_summary.schema.json` + `.py` write a per-citation `lookup_verified` ∈ {`true`, `false`, `unresolvable`} + `anchor_present` + `resolver_outcomes`. `scripts/verification_gate/__init__.py` + `scripts/verify_passport.py` extract the gate into a callable API + standalone CLI.

Spec: `docs/design/2026-05-21-v3.10-182-promote-citation-gate-spec.md` (§0 v3.11 amendment + INVARIANT C-V6).

## v3.10 Key Additions (#127 — triangulation policy layer)

**External motivation:** Zhao et al. arXiv:2605.07723 (2026-05). v3.9.0 shipped three-index triangulation as advisory-only and explicitly deferred the policy layer (hard-block / strict modes). v3.10 ships it, rescoped after a first-party spec-collision audit (2026-05-31) that found `triangulation_policy` and the `R-L3-2-A` firm-rule wording were staked by two unshipped specs at once.

**Two PRs.** PR-A (shipped) disambiguated the `R-L3-2-A/B/C` ID overload (renamed the borrowed claim-manifest copies to `R-CIM-A/B/C`) and stood up `shared/references/firm_rules.md` as the canonical firm-rule source + `check_firm_rules_sync.py`. PR-B (this) builds the policy layer on that base.

**PR-B — terminal policy layer (opt-in; default byte-equivalent to v3.9.0):**

- **Namespaced `terminal_policies` (D1).** New passport-level `shared/contracts/passport/terminal_policies.schema.json` (standalone — NEVER inside the entry schema, Invariant 11). `contamination_triangulation` ∈ {`advisory`, `strict`, `strict_articles_only`} (wired). `temporal_integrity` accepts only `advisory` (forward-reserved; a wired-less `strict` would be false safety, Invariant 3). Per-key absence = advisory (evaluator default, not a JSON-Schema `default`); whole-object absence = all-advisory = byte-equivalent v3.9.0 (Invariant 7).
- **`venue_type` entry fields.** `venue_type` (closed enum incl. explicit `unknown`), `venue_type_provenance` (no `_inferred` values, R-L3-2-D), `venue_type_source` (required iff `trusted_source_declared`; lint-guarded against naming a lookup index — laundering guard). Adapter-declared only; pair dependencies bidirectional with a one-way `unknown ⟹ unknown` rule that still lets a known type carry `unknown` provenance.
- **Hard-block at the emission boundary (D2).** The finalizer is the sole policy evaluator: it stamps a fully-encoded `policy_hash` on every ref marker and, under `strict`, co-emits a `TERMINAL-BLOCK severity=HIGH-BLOCK` token alongside (not replacing) the advisory suffix. `strict_articles_only` is a deliberate PRECISION mode (DOI + journal/conference venue + declared provenance; DOI-less / unknown-venue stays advisory by design). The formatter is a STAMP-ONLY two-gate (freshness + generic rule-11 refusal), never re-evaluating policy logic (Invariant 13). `HIGH-BLOCK` is terminal — not `/ars-mark-read` ack-able. Manual entries exempt (k=3 unreachable).
- **Firm rule + sync (D3).** R-L3-2-A reworded to the broad default-advisory + opt-in-strict form in the canonical block; mirrors stay by-ID references (single-sourced), with a contradiction guard (scoped to the R-L3-2-A reference sentence, so the Collaboration Depth Observer's "never blocks" is not false-flagged).
- **Migration + adapters + lint.** `migrate_literature_corpus_to_v3_10.py` deep-merge-seeds `terminal_policies` (idempotent, dry-run, no venue backfill). The three reference adapters declare `venue_type`. New `check_v3_10_policy.py` (alongside the v3.9.0 lint) + CI wiring.

Spec: `docs/design/2026-05-31-ars-v3.10-policy-layer-rescope-spec.md`.

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

**Regression status (final, post-convergence):** 967 pass / 3 skipped / 0 failed (pre-review baseline 925; +42 tests across F1-F22 closures). v3.6.7 PATTERN PROTECTION + v3.7.1 / v3.7.2 lints unchanged. v3.7.3 lint wired into spec-consistency.yml CI workflow. F1-F22 closed across an 11-round independent cross-model review trajectory with no cross-reviewer overlap. The final round returned **0 findings**, convergence signal achieved.

Spec: `docs/design/2026-05-12-ars-v3.7.3-claim-faithfulness-and-contaminated-source-spec.md`.

## v3.9.0 Key Additions

**External motivation:** Zhao et al. arXiv:2605.07723 (2026-05) §3 — cross-index triangulation across multiple bibliographic indexes is a viable false-positive-reduction strategy for hallucinated-citation detection. v3.7.3 shipped single-index (Semantic Scholar) detection; v3.9.0 extends to three-index triangulation (S2 + OpenAlex + Crossref) as **advisory evidence only**. Terminal gate behavior unchanged from v3.7.3.

**Schema additions (additive):**
- `contamination_signals.openalex_unmatched` (optional bool) — per `deep-research/references/openalex_api_protocol.md`.
- `contamination_signals.crossref_unmatched` (optional bool) — per `deep-research/references/crossref_api_protocol.md`.
- Manual-entry not-rule extends from `required: [semantic_scholar_unmatched]` to `anyOf: [s2, openalex, crossref]` — manual entries cannot carry any lookup unmatched field. Preprint flag remains exempt (heuristic, not lookup).

**Finalizer 4-tier advisory matrix (all advisory, gate unchanged):**
- k=0: no suffix.
- k=1 (k_max=1, present field = S2): `CONTAMINATED-UNMATCHED` (v3.7.3 legacy preserved).
- k=1 (k_max=1, present field = OpenAlex or Crossref): `CONTAMINATED-COVERAGE-NOISE`.
- k=1 (k_max=2-3): `CONTAMINATED-COVERAGE-NOISE`.
- k=2: `CONTAMINATED-PARTIAL-UNMATCH`.
- k=3: `CONTAMINATED-TRIANGULATION-UNMATCHED`.
- Preprint composition: `CONTAMINATED-PREPRINT+<triangulation>` (PREPRINT first per canonical token order).

**Formatter pass-through allowlist:** extends from 3 v3.7.3 suffixes to 9 (3 legacy + 6 v3.9.0). Refusal rules 1-10 unchanged. R-L3-2-E enforces this distinction (refusal list NOT extended, pass-through allowlist MUST extend in lockstep with finalizer).

**Migration:** v3.7.3 corpora → run `scripts/migrate_literature_corpus_to_v3_9_0.py`. Pre-v3.7.3 corpora → run v3.7.3 migration first (daisy-chained per spec §3.7).

**Out of v3.9.0 scope (v3.10 policy layer):** `venue_type` field, `venue_type_provenance` field, `triangulation_policy` field, strict modes, `HIGH-BLOCK` tier.

**Lint:** `scripts/check_v3_9_0_triangulation.py` set-equality on formatter allowlist + refusal-list-unchanged guard.

Spec: `docs/design/2026-05-17-ars-v3.9.0-cross-index-triangulation-measurement-spec.md`.

## v3.7.0 Key Additions

- **Claude Code plugin packaging**: ARS now installs in one line via `/plugin marketplace add Imbad0202/academic-research-skills` + `/plugin install academic-research-skills`. The traditional `git clone + symlink to ~/.claude/skills/` flow continues to work — both tracks are first-class. Repo gains four top-level directories: `.claude-plugin/`, `commands/`, `agents/`, `hooks/`, plus a `skills/` symlink dir; existing 4 skill directories untouched.
- **10 slash commands** (`commands/ars-*.md`) mapping `MODE_REGISTRY.md` entries to `/ars-<mode>` triggers — `sonnet` pinned in frontmatter for the light modes (cost routing); the heavy modes (`full`, `reviewer`, `revision-coach`) inherit the session model (the original v3.7.0 `opus` floor was retired in the 2026-06 Fable 5 harness pass — under a stronger session model a floor becomes a downgrade ceiling), no Haiku.
- **3 plugin-shipped agents** (`agents/*_agent.md`) as relative symlinks to the v3.6.7-hardened downstream agents in `deep-research/agents/` (materialized to real byte-identical copies in #413 — symlinks break Windows checkouts and zip installs; `scripts/check_agents_mirror_sync.py` now pins the byte-equality in CI). Source frontmatter gains `model: inherit` so an Opus session keeps Opus agents while the user's PreToolUse `warn-agent-no-model.sh` hook gates Haiku at dispatch.
- **SessionStart announce hook** (`hooks/hooks.json` + `scripts/announce-ars-loaded.sh`) lists the 10 slash commands + 3 agents + token-budget pointer when the plugin loads. Bash 3.2 compatible.
- **Phase 2.2 scope reduction note**: a `SubagentStop → run_codex_audit.sh` cross-model audit hook was scoped out for v3.7.0 (contract gap: hook payload carries no stage/deliverable; invoker boundary: same-session in-LLM Bash forbidden by the wrapper). Deferred to a future release.

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
- **`tests/fixtures/v3.6.6-ab/` A/B evidence fixture stub** (30 files): manifest + README + 6 paper-A inputs/baseline + 1 paper-C inputs/baseline + Stage 3 reviewer excerpt + 6 cross-model judge baseline placeholders. `manifest_lint_mode: spec_branch`, `fixture_version: 0.1.0`. Real fixture data populates in follow-up commits.
- **`academic-paper-reviewer/references/sprint_contract_protocol.md` cross-reference** noting Schema 13.1 since v3.6.6 + pointing readers at `academic-paper/SKILL.md` + design doc §5 for the parallel generator-evaluator protocol.

## v3.6.7 Key Additions

- **Downstream-agent pattern protection layer (Step 1+2)**: `synthesis_agent`, `research_architect_agent` (survey-designer mode), and `report_compiler_agent` (abstract-only mode) carry a `PATTERN PROTECTION (v3.6.7)` block hardening 13 of 17 documented hallucination/drift patterns (A1–A5 narrative-side, B1–B5 instrument-side, C1–C3 publication-side). Step 6 (orchestrator runtime hooks) and Step 8 (synthetic eval case) ship in a follow-up PR.
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
- **Cross-model verification** (optional): Set `ARS_CROSS_MODEL` env var to enable a non-Anthropic verifier (currently GPT-5.5 / GPT-5.5 Pro or Gemini 3.1 Pro) for integrity sample checks and independent Devil's Advocate critique. Peer-review sixth-reviewer support remains planned. See `shared/cross_model_verification.md` for the supported-model table.
- **AI Self-Reflection Report**: Pipeline Stage 6 now includes AI behavioral self-assessment (concession rate, health alerts, sycophancy risk rating).

## Routing Discipline (v3.9.2)

**Routing precedence:** This section runs BEFORE Routing Rules 1-5. Once this section settles on a destination, Rules 1-5 apply within that destination's skill family.

**Step 0 — Escape hatch check (before any classification):** If the user's first message begins with `[direct-mode]` (case-insensitive byte-0 token, optionally preceded by whitespace/newlines that are stripped on parse), record this fact, strip the prefix and surrounding whitespace from the message, and skip directly to **Step 1 explicit-intent handling** on the stripped content. The literal `[direct-mode]` is NOT passed through to the dispatched agent. If the stripped message itself has no clear skill named, Step 1 falls through to Step 3 clarification (the escape hatch bypasses cross-phase clarification (Step 2), not all routing).

Otherwise, classify the user's input:

1. **Explicit clear intent** — user invokes a specific skill via `/ars-*` slash command, or uses an unambiguous trigger keyword that maps to a single skill (e.g., "lit-review this", "review my paper", "draft an abstract"):
   → Route directly; no clarification, no orchestrator detour.

2. **Cross-phase materials detected** — user provides artifacts spanning ≥ 2 pipeline phases without naming a specific skill (e.g., pre-written abstract + pre-collected literature; full draft + reviewer comments + bibliography):
   → **Clarify**. Do NOT auto-route to a single-phase agent. List candidate workflows as a-d options in markdown body (NOT via AskUserQuestion tool). See `shared/references/intent_clarification_protocol.md` for the message template.
   → Reason: clarification is the safest action when materials don't unambiguously identify intent. (v3.10 active conductor (#134) will handle this via structured intake; v3.9.2 asks.)

3. **Ambiguous intent, no materials** — user provides no artifacts and no clear request:
   → Clarify per `shared/references/intent_clarification_protocol.md`.

**Anti-pattern (caused #133):** Receiving ambiguous cross-phase materials and silently auto-routing to a single-phase agent based on which phase the materials "look closest to." This bypasses orchestrator-level reconciliation and lets the subagent inherit the full ambiguity without independent oversight.

**Forward note (v3.10):** Active conductor (#134) will reframe this gate as structured intake with task envelope dispatch. v3.9.2 ships clarification-only as interim hot-fix.

## Routing Rules

1. **academic-pipeline vs individual skills**: academic-pipeline = full pipeline orchestrator (research → write → integrity → review → revise → final integrity → finalize). If the user only needs a single function (just research, just write, just review), trigger the corresponding skill directly without the pipeline.

2. **deep-research vs academic-paper**: Complementary. deep-research = upstream research engine (investigation + fact-checking), academic-paper = downstream publication engine (paper writing + bilingual abstracts). Recommended flow: deep-research → academic-paper.

3. **deep-research socratic vs full**: socratic = guided Socratic dialogue to help users clarify their research question. full = direct production of research report. When the user's research question is unclear, suggest socratic mode.

4. **academic-paper plan vs full**: plan = chapter-by-chapter guided planning via Socratic dialogue. full = direct paper production. When the user wants to think through their paper structure, suggest plan mode.

5. **academic-paper-reviewer guided vs full**: guided = Socratic review that engages the author in dialogue about issues. full = standard multi-perspective review report. When the user wants to learn from the review, suggest guided mode.

6. **rebuttal-audit vs revision-coach (input-shape gate)**: both touch reviewer comments, so route by INPUT SHAPE, not verbs. Route to `academic-paper rebuttal-audit` ONLY when the user supplies BOTH the reviewer comments AND an existing rebuttal/response draft to evaluate (it does advisory QA, generates nothing). If only reviewer comments are present (no draft yet), route to `revision-coach` (it generates a Response Letter Skeleton). If unclear which, clarify rather than guess. `rebuttal-audit` is standalone/advisory and never emits Schema 11 or marks anything verified.

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
- **Suite version**: 3.15.0 (per CHANGELOG.md)
- **Last Updated**: 2026-07-04
- **Author**: Cheng-I Wu
- **License**: CC-BY-NC 4.0
