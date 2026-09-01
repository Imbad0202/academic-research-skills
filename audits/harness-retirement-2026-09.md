# Harness Retirement Audit — `academic-research-skills` (2026-09)

| | |
|-|-|
| Repo path | `~/Projects/academic-research-skills` |
| Branch / commit audited | `main @ e8bf858` |
| Date | 2026-09-01 |
| Target model | Claude Fable 5 (session) / Codex `gpt-5.6-sol` (cross-model transport) — unchanged since the 2026-08 audit |
| Scope | All 23 Bucket A agent prompt bodies from `scripts/ars_phase_scope_manifest.json` v1 |
| Files scanned | 23 (15 changed since the 2026-08 baseline; 8 unchanged) |
| Baseline | `audits/harness-retirement-2026-08.md` (full 23-file scan at `1bd287f`, 2026-08-08; its P1-F01 retirement is applied and verified absent) |
| Method | Incremental full-diff review of every Bucket A change since `1bd287f`, mechanical pattern search across all 23 current bodies, referenced-path existence check, and commit/issue adjudication for every new block |

## Scope manifest

- **deep-research (10):** `research_question_agent`, `research_architect_agent`, `bibliography_agent`, `source_verification_agent`, `timeline_extraction_agent`, `synthesis_agent`, `editor_in_chief_agent`, `ethics_review_agent`, `risk_of_bias_agent`, `meta_analysis_agent`
- **academic-paper (7):** `literature_strategist_agent`, `structure_architect_agent`, `draft_writer_agent`, `citation_compliance_agent`, `abstract_bilingual_agent`, `peer_reviewer_agent`, `formatter_agent`
- **academic-paper-reviewer (6):** `eic_agent`, `methodology_reviewer_agent`, `domain_reviewer_agent`, `perspective_reviewer_agent`, `devils_advocate_reviewer_agent`, `editorial_synthesizer_agent`

Changed since the August baseline (15): `research_question_agent`, `research_architect_agent`, `bibliography_agent`, `ethics_review_agent`, `literature_strategist_agent`, `structure_architect_agent`, `draft_writer_agent`, `peer_reviewer_agent`, `formatter_agent`, and all six reviewer-skill agents. Unchanged (8): `source_verification_agent`, `timeline_extraction_agent`, `synthesis_agent`, `editor_in_chief_agent`, `risk_of_bias_agent`, `meta_analysis_agent`, `citation_compliance_agent`, `abstract_bilingual_agent` — these carry the August full-body clean verdict forward, re-confirmed by this month's mechanical pattern scan.

## Executive summary

- **Findings: 0 P0, 0 P1, 0 P2.**
- No model change has landed since the 2026-08 audit (same session-model tier, same cross-model transport), so no scaffold has newly *expired*. Every prompt-body change since `1bd287f` traces to a documented, currently-shipping contract feature (issue-anchored, most under a month old): #651 retraction status, #660 tortured-phrase advisory, #667/#669/#681 human-subjects authority family, #670 revision authorization, #672 cross-document consistency, #684/#706 review-criteria binding, #697 non-ranking roadmap, #738 read-scope resolver, #740 panel provenance, #743 inquiry ledger, and the v3.20.1 Socratic visible-exit rule.
- Several of the month's changes are themselves retirements of debt-like patterns, landed through their own reviewed PRs rather than through this audit: `peer_reviewer_agent`'s numeric weighted-scoring rubric and score→verdict mapping replaced by categorical criterion-bound judgements; `editorial_synthesizer_agent`'s confidence-score weighting table ("Score-5 beats two Score-2") demoted to a disclosure-only field; the Priority 1/2/3 work-ranking, estimated-effort hours, and revision-deadline suggestions removed from the roadmap; `literature_strategist_agent`'s universal numeric quotas (minimum source counts, 10-year default window, fixed language-mix percentages, 1–3-point quality scoring) replaced by claim-coverage judgements.
- **Overall verdict:** the Bucket A prompts remain free of capability-era model pins, sampling overrides, generic anti-hallucination boilerplate, teaching-grade few-shot blocks, open-ended retry loops, and deprecated tool references. The August keep-list stands unchanged.

### Findings by issue #811 category

| Category | Findings | Result |
|---|---:|---|
| Capability-era workarounds | 0 | No new role priming, coercion, or capability-limit retries; the remaining "Bash denied" statements describe the current runtime tool-deny boundary (#134), not a superseded model limit |
| Pre-tool-use scaffolds | 0 | New preflights (reviewer binding check 6, ethics replay-consumption rules) guard semantics the deterministic layer does not enforce, per their design docs |
| Verbose reasoning scaffolds | 0 | New text is contract prose, not step-by-step reasoning templates; repetition across reviewer seats is byte-sync-linted from `reviewer_sprint_prompt_source.md` (August keep reason unchanged) |
| Defensive few-shot examples | 0 | No new generic happy-path teaching examples; remaining examples encode grammar and edge cases |
| Format guards | 0 | New output shapes (criterion tables, `NOT_CALIBRATED` blocks, binding markers) are consumed by current checkers/schemas, not duplicates of them |
| Deprecated tool references | 0 | All 87 script/schema/reference paths cited across the 23 bodies exist on disk at `e8bf858` |

## Mechanical scan results (all 23 current bodies)

- Hardcoded model pins (`claude-*`, `Opus 4.x`, `Sonnet 4.x`, `Haiku`): **0 hits.** Remaining model names describe optional external cross-model interfaces, as in August.
- Sampling/budget overrides (`temperature`, `top_p`, `max_tokens`, `budget_tokens`): **0 hits.**
- Anti-hallucination phrasing: every hit is a domain contract clause, not a generic patch — R-CIM-D experiment-id emission rules, the #574 A5 no-invention/`[UNVERIFIED]` recommendation grammar, RoB 2/ROBINS-I instrument fidelity, bounded-arithmetic procedure limits, search-bounded novelty statements. High-stakes academic-citation domain: kept per the iron rule (silent-failure class).
- Negative-framing density: highest counts sit in the reviewer seats and synthesizer, where the negatives are hard contract boundaries (forbidden-operations lists, blinding rules, no-invention rules) already examined and kept in August. No new gratuitous prohibition cluster was introduced this month.

## Examined and kept (delta over the August keep-list)

The full August keep-list (Phase Boundary blocks, reviewer sprint structural preflights, remaining Detailed Execution Algorithm sections, bounded retry/repair language, examples/model-pins/tools) stands unchanged. This month adds:

### Human-subjects replay-consumption prose (`ethics_review_agent`, `research_architect_agent`)

The #667/#669/#681 blocks repeat "this role must not simulate or claim that replay" across five protocol surfaces. Kept: each instance guards a distinct artifact family (resolved context, rule trace, packet manifest, content-coverage advisory, finalized advisory), the protocols shipped within the last month with their own design-frozen specs, and the failure they prevent (a non-shell agent asserting a validation it cannot run) is silent. Reconsider only if a future release consolidates the five consumption contracts into one shared reference the agents can point to.

### #684 binding blocks repeated across the five reviewer seats

The criteria-binding commitment, preflight check 6, and constructive-findings blocks are near-identical across `eic` / `methodology` / `domain` / `perspective` / `devils_advocate`. Kept for the same reason as the sprint preflights in August: the H3 prompt bodies are generated from `academic-paper-reviewer/references/reviewer_sprint_prompt_source.md` and byte-sync-linted, so the duplication is single-sourced, not independently maintained.

## Verification

- `git diff` review covered every Bucket A change in `1bd287f..e8bf858` (≈1,080 inserted lines across 15 files), with the August P1-F01 retirement commit (`20c937a`) identified and excluded from re-adjudication.
- Referenced-path existence check: 87/87 paths resolve against the repo root or their skill directory.
- No prompt file was modified by this audit; no CHANGELOG entry is required (zero retirements applied).

## Routing checklist (issue #811)

- [x] Audit report posted as comment on #811.
- [x] P0 retirements: none.
- [x] P1 retirements: none; nothing logged in `CHANGELOG.md` `[Unreleased]`.
- [x] P2+ backlog: none; no issue created merely to record a zero set.
