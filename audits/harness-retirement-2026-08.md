# Harness Retirement Audit — `academic-research-skills` (2026-08)

| | |
|-|-|
| Repo path | `~/Projects/academic-research-skills` |
| Branch / commit audited | `main @ 1bd287f` (working-tree retirement applied after the scan) |
| Date | 2026-08-08 |
| Target model | Codex `gpt-5.6-sol` |
| Scope | All 23 Bucket A agent prompt bodies from `scripts/ars_phase_scope_manifest.json` v1 |
| Files scanned | 23; 8,583 lines before the applied retirement |
| Baselines | `audits/harness-retirement-2026-07.md`; `audits/harness-retirement-2026-07-04.md` |
| Method | Full current-body scan, post-July incremental diff review, mechanical pattern search, lint/checker mirror search, and blame/history adjudication |

## Scope manifest

- **deep-research (10):** `research_question_agent`, `research_architect_agent`, `bibliography_agent`, `source_verification_agent`, `timeline_extraction_agent`, `synthesis_agent`, `editor_in_chief_agent`, `ethics_review_agent`, `risk_of_bias_agent`, `meta_analysis_agent`
- **academic-paper (7):** `literature_strategist_agent`, `structure_architect_agent`, `draft_writer_agent`, `citation_compliance_agent`, `abstract_bilingual_agent`, `peer_reviewer_agent`, `formatter_agent`
- **academic-paper-reviewer (6):** `eic_agent`, `methodology_reviewer_agent`, `domain_reviewer_agent`, `perspective_reviewer_agent`, `devils_advocate_reviewer_agent`, `editorial_synthesizer_agent`

The inventory is derived from the manifest rather than the contents of the three `agents/` directories. Non-Bucket-A agents and top-level mirrors are outside issue #617's scope.

## Executive summary

- **Findings:** 1 P1, 0 P0, 0 P2.
- **Disposition:** the P1 was retired in this working tree and recorded under `CHANGELOG.md` `[Unreleased]`; no follow-up issue is needed.
- **Net prompt change:** one duplicated report template removed; one pseudo-human review scaffold rewritten; fixed strength quotas removed. The five-dimension rubric, verdict mapping, issue bands, two-round revision loop, Phase Boundary, and evaluator contracts are unchanged.
- **Overall verdict:** the current Bucket A prompts are generally free of capability-era model pins, generic retry loops, basic few-shot teaching, and deprecated tool signatures. Residual procedural detail is concentrated in domain algorithms and machine-checked output contracts with current keep reasons.

### Findings by issue #617 category

| Category | Findings | Result |
|---|---:|---|
| Capability-era workarounds | 1 | P1-F01's simulated timed read, gut reactions, and parallel initial score retired |
| Pre-tool-use scaffolds | 0 | Remaining preflights have current failure evidence or cover semantics the deterministic layer cannot enforce |
| Verbose reasoning scaffolds | 1 | P1-F01's duplicate review workflow/template cluster consolidated |
| Defensive few-shot examples | 0 | No new generic happy-path teaching examples found |
| Format guards duplicated by schemas/checkers | 1 | P1-F01's two competing report templates reduced to one; current reviewer sprint mirrors retained for measured conformance |
| Deprecated tool references | 0 | Current tool/script references match frontmatter ownership and shipped entry points |

One finding may span more than one category; totals are finding counts, not additive category counts.

## Finding and applied retirement

### P1-F01 — `academic-paper/agents/peer_reviewer_agent.md` — duplicate output contracts and pseudo-human review scaffold

**Observed debt**

The agent contained both an early `## Output Format` template and a later `### Structured Review Report Format`. They disagreed on headings and detail. Between them, `## Detailed Execution Algorithm` required the model to:

- simulate a 15–20 minute first read;
- assign an unconsumed `Initial Impression Score` in parallel with the weighted evidence score;
- record exactly three gut reactions;
- produce at least one strength per section and at least three strengths overall.

The first three requirements are unobservable process role-play, not a review contract. The fixed strength quotas can manufacture praise when the evidence supports none. Repository-wide search found no parser, schema, script, workflow, or other prompt consumer for `Initial Impression Score`, `gut reactions`, or the deleted template. Blame dates the scaffold to February/March 2026, while the later evidence and output contracts evolved independently.

**Severity rationale**

P1 rather than P2: two live output shapes create direct prompt ambiguity, and the quota can change substantive findings rather than merely consume context.

**Applied change**

- Removed the earlier duplicate report template; retained the later, more complete canonical template.
- Renamed the remaining section `Review Workflow and Scoring Rubric`.
- Replaced timed simulation, gut reactions, and the initial score with one holistic, evidence-grounded read.
- Made dimension evidence authoritative for the verdict.
- Allowed zero strengths when the reviewer states which dimensions were checked; every listed strength must cite a passage.
- Changed failure handling from “find” replacement praise to ground-or-remove.

**Protected surfaces left intact**

- Phase 6a/6b evaluator contract and its bounded lint-failure behavior;
- five weighted dimensions and detailed scoring anchors;
- verdict mapping and maximum two-round revision path;
- Critical/Major/Minor issue bands and actionable revision instructions;
- Output Discipline epistemic-status disclosure.

## Examined and kept

### Phase Boundary blocks

All 23 stay. The deterministic write-scope hook covers structured-write paths only when the hook runs. The prose blocks also govern deliverable ownership, persona simulation, read direction, and return-of-control behavior that the hook does not enforce. They remain both the degradation layer and the human-readable contract.

### Reviewer sprint structural preflights

The Phase 1/2 terminal preflights repeated across reviewer seats look like format scaffolding in isolation, but are retained:

- the H3 prompt bodies are generated from `academic-paper-reviewer/references/reviewer_sprint_prompt_source.md` and byte-sync-linted rather than independently maintained;
- the rules correspond to `check_phase_conformance.py` / `check_panel_synthesis.py` grammar;
- recent E4 rows and #613/#682 provide current failure evidence for dissent visibility, trigger binding, evidence-anchor grammar, and DA terminal-table placement;
- removing them before the pending reviewer measurement would trade prompt size for known conformance aborts without evidence of neutrality.

They should be reconsidered only after a matched measurement demonstrates that the deterministic post-output checks alone preserve usable-panel rate and finding quality.

### Remaining “Detailed Execution Algorithm” sections

The surviving sections in citation compliance, literature strategy, structure allocation, visualization, peer review, and formatting were compared with their surrounding prose. Generic duplicate drafting narration was already retired in July. What remains specifies domain decisions or transformation rules: source-screening branches, citation-style recognition, allocation arithmetic, visual fidelity, score computation, and document conversion. These are task instructions, not merely “think step by step” requests.

### Retry and repair language

No open-ended “try harder” loop was found. The remaining retries are bounded protocol behavior with explicit checker feedback and abort states (notably Phase 6a/6b), or user-controlled workflow rounds. These are retained.

### Examples, model pins, and tools

- No `temperature`, `top_p`, `max_tokens`, or `budget_tokens` override appears in the 23 bodies.
- Agent frontmatter uses inherited routing; model names that remain describe optional external cross-model interfaces or historical evidence, not an agent pin.
- The remaining examples encode grammar, edge cases, evidence anchors, or discipline-specific distinctions. The generic citation-form and writing-process few-shots identified in July remain absent.
- Script and tool references were checked against current files and the Bucket A frontmatter/runtime boundary; no deprecated callable name was found.

## Routing checklist

- [x] Audit report prepared for posting to #617.
- [x] P0 retirements: none.
- [x] P1 retirement logged in `CHANGELOG.md` `[Unreleased]` and applied locally.
- [x] P2+ backlog: none; no issue created merely to record a zero set.

## Verification

- `python3 scripts/run_ci_pytest_manifest.py` — **PASS**, all 95 manifest entries.
- The run includes the phase/write guards, reviewer finding and decision contracts, E4 dispatch/resume suites, prompt-sync locks, #617 issue renderer, and current #665/#678 contract suites.
- `git diff --check` — **PASS**.
- Repository search confirms the retired timed-read, gut-reaction, initial-score, duplicate-output-heading, and fixed-strength-quota phrases are absent from `academic-paper/agents/peer_reviewer_agent.md`.
