# Harness Retirement Audit — `academic-research-skills` (2026-09, Opus 5.5 dual-model support)

| | |
|-|-|
| Repository | `Imbad0202/academic-research-skills` (GitHub) |
| Branch / commit audited | Read at `main @ 1515a21`; changes branch from `main @ a1819d8` (#881 changed command bodies, not their `model:` lines) |
| Date | 2026-09-23 |
| Target model (before → after) | Session: Claude Fable 5.1 only → **Claude Fable 5.1 and Claude Opus 5.5** as co-supported session models. Claude Code 2.1.280 (2026-09-22) made Opus 5.5 the account default and the target of the `opus` alias; Fable 5.1 remains opt-in (`/model fable`). Cross-model lineup unchanged |
| Trigger | *System Card: Claude Opus 5.5* (Anthropic, 2026-09-22; 230 pages, 8,048 extracted text lines). Tracking issue #883 |
| Scope | All 39 agent prompt bodies, `shared/agents/`, `commands/` frontmatter, `hooks/` and the SessionStart announce, and the documentation surfaces that name a model or a tier (`docs/PERFORMANCE*.md`, `shared/cross_model_verification.md`, `shared/model_tiering.md` and its mirrors, `docs/SETUP*.md`, `docs/ARCHITECTURE.md`, `docs/RISK_REGISTER.md`, `.claude/CLAUDE.md`, `CONTRIBUTING.md`) |
| Baseline | `audits/harness-retirement-2026-09-model-update.md` (MU-001 – MU-014, G-1 – G-4); its keep-list carries forward unless a row below says otherwise |
| Method | Two independent full reads of the card (Claude Opus 5.5 in-session; Codex `gpt-6-astra` at `xhigh`, read-only, neither seeing the other's notes until both finished); Claude Code first-party documentation for product facts; mechanical scans over every prompt body. Details under Verification |

## Executive summary

- **Findings: 0 P0; 6 applied changes (DM-001 – DM-006); 1 guardrail added (DG-1); 0 prompt-text retirements; 9 keep rows now also backed by an Opus 5.5 citation (DM-012 – DM-018, DM-020, DM-021); 3 rows kept or declined for stated reasons (DM-007 – DM-009); 1 record row (DM-011); 2 deferred (DM-010, DM-019); 5 candidate follow-ups.**
- **No agent prompt sentence expired.** The card describes the failure classes ARS's remaining scaffolds guard against as still present in Opus 5.5: asserting unverified inferences as established fact (the top flagged subcategory) and describing a partial check as a full read (p. 36); relying on abstracts rather than full papers while presenting that information confidently (pp. 19, 33); answering directly when the task required a tool or code (p. 99); a fabricated user approval relayed to a subagent (p. 102). Two behaviors are named regressions: acting on instructions inside text the user pasted into their own message (§6.5.1) and accepting unverifiable claims of authorization (pp. 3, 105, 108). The card names multi-agent runs, very long trajectories, and non-English sessions as blind spots of its alignment audit (pp. 93, 122), and ARS runs under all three.
- **Neither model is better for ARS at everything.** Opus 5.5 is ahead of Fable 5.1 on every row of the card's capability summary table, run at max effort except Terminal-Bench 4.0 at `xhigh` (p. 174). Fable 5.1 is ahead on DRACO deep research at every effort level (p. 187) and on OfficeQA grounded document reasoning (p. 208). Opus 5.5 costs 40% of Fable 5.1 per token (p. 180; Fable 5.1 price per `docs/PERFORMANCE.md`). Effort is the swing factor: Claude Code starts Opus 5.5 at `medium`, where it trails Fable 5.1 on both research benchmarks, and at `low` its research scores collapse (DRACO 72.5, WANDR 31.2) while Fable 5.1 holds (84.2, 63.3; pp. 187-188).
- **What expired is currency and precision, not protection.** The docs named only Fable 5.1. The tiering doc's word "family" collides with Claude Code's own "model family alias" (`opus`, `fable`), which can read an Opus session as its own frontier tier. The declared-model note said a classifier fallback happens "without notice", while Claude Code shows a transcript notice and keeps the session on the fallback model.
- **Maintainer decisions (2026-09-23):** keep the tier ladder and document that its order is a lineup order, not a capability order (DM-004, option A of three); add the instruction/data boundary to the revision coach (DG-1, option A of three).

## Fable 5.1 vs Opus 5.5 for ARS

Sources: **card** = *System Card: Claude Opus 5.5* page; **docs** = Claude Code documentation, 2026-09-23; **prior audit** = `audits/harness-retirement-2026-09-model-update.md`; **inference** = this audit's reading, not a vendor statement.

### Execution differences

| Dimension | Claude Fable 5.1 | Claude Opus 5.5 | Source |
|---|---|---|---|
| List price per million tokens (input / output) | US$10 / US$50 | US$4 / US$20; cache reads US$0.20; five-minute cache writes US$5 | Fable: `docs/PERFORMANCE.md` (2026-09 list); Opus: card p. 180 |
| Full-pipeline arithmetic (~200K in / ~100K out, no cache) | ~$7 | ~$2.80 | arithmetic on `docs/PERFORMANCE.md` token rows, not a re-measurement |
| Claude Code default | never the account default; `/model fable` (`/model claude-fable-5-1` in Claude apps gateway sessions); may bill to usage credits depending on plan and seat (interactive sessions ask once before billing, except under Enterprise organization billing; `-p` and the Agent SDK bill without asking) | account default on Pro, Max, Team, Enterprise, and the API; target of the `opus` alias | docs (model configuration) |
| Default effort in Claude Code | `high` | `medium` | docs |
| Content-classifier fallback | biology → Opus 5; cybersecurity → Opus 4.8 | same; frontier-LLM development → Opus 5; weapons and distillation → block with no fallback | card pp. 12-13; docs |

Same for both: effort levels `low` – `max` (docs); thinking always on (docs; card pp. 61, 88); a 1M context window on the Anthropic API (docs; card p. 174, with Opus 5.5 evaluated up to the full window, p. 184); subagents inherit the session effort unless the subagent or skill sets `effort` (docs, sub-agents and skills).

### Capability evidence relevant to ARS

| Evidence | Result | Source |
|---|---|---|
| Capability summary (Opus 5.5 at max effort; Terminal-Bench 4.0 at `xhigh`) | Opus 5.5 higher on every row, e.g. HLE with tools 67.7 vs 65.6, GDPval-AA 1846 vs 1735, AA-Briefcase 1822 vs 1678 | card p. 174 |
| DRACO deep research, low / medium / high / xhigh / max | Opus 5.5: 72.5 / 83.9 / 85.0 / 86.7 / 87.4. Fable 5.1: 84.2 / 85.7 / 86.5 / 86.9 / 87.7. Fable 5.1 higher at every level; Opus 5.5 cheaper per task at every level | card p. 187 (chart) |
| WANDR wide search, same levels | Opus 5.5: 31.2 / 62.8 / 67.3 / 71.3 / 72.3. Fable 5.1: 63.3 / 64.5 / 66.7 / 67.7 / 68.7. Opus 5.5 higher from `high` up, far lower at `low` | card p. 188 (chart) |
| OfficeQA / OfficeQA Pro (grounded numerical reasoning over documents) | Opus 5.5 78.9 / 67.7; Fable 5.1 80.2 / 69.0 | card p. 208 |
| AI R&D uplift | "a modest improvement upon Fable 5.1" | card pp. 42-44 |
| Literature handling (expert red-team) | "did not wrestle with the published literature, often overrelying on claims in abstracts"; misled specialists | card pp. 19, 33 |
| Open-ended research | tests incremental ideas, prefers less ambitious hypotheses, defers to published literature | card pp. 33, 36 |
| Creativity and intellectual depth | "slightly weaker than Opus 5" | card p. 95 |
| Honesty under pressure (MASK) | Opus 5.5 87.4% vs Opus 5 94.8%; Fable 5.1 not in the chart | card p. 130 (chart) |
| Effort and scope | FrontierCode peaks at `medium` and declines above it because grading penalizes out-of-scope changes | card p. 176 |

### Harness differences: which guardrails matter more

Card pages for the Opus 5.5 column are in the finding row named in the last column.

| ARS guardrail | Fable 5.1 evidence (prior audit) | Opus 5.5 evidence (this card) | Net |
|---|---|---|---|
| Untrusted-material fences: reviewer `<paper_content>` fence and Iron Rule #7; deep-research canonical boundary | general injection posture | pasted-text regression; the same text arriving as a tool result was not acted on | more load-bearing; extended to the revision coach (DM-012, DG-1) |
| Checkpoint decision provenance (G-1, R11); committee authority rule (#668) | §6.2.1 fabricated quotation | fabricated user quote relayed to a subagent; accepting unverifiable authorization is a regression | more load-bearing (DM-013) |
| Required-tool steps backed by receipts | §6.6.1 claims of runs never executed | answers without the required tool or code | unchanged, keep (DM-014) |
| Read-scope attestations, three-layer citation anchors, claim–source verification | §2.3.3 exaggerated completeness | partial check described as a full read; abstracts over full papers | more load-bearing (DM-015) |
| Claim-strength ladder, protected hedges, `[MATERIAL GAP]` routing | §2.2.4 unhedged estimates | unverified inference asserted as fact is the top flagged subcategory; qualifier dropping no worse than prior models | unchanged, keep (DM-016) |
| DA concession scoring; "pressure is not evidence" | §6.1.2 less sycophantic than Opus 5 | MASK honesty below Opus 5 | unchanged, keep (DM-017) |
| Mechanical panel synthesis | — | a reviewer whose reasoning met a flag criterion did not flag in its final answer | unchanged, keep (DM-018) |
| Brevity and scope rules (MU-007) | §8.4 higher effort adds out-of-scope content | FrontierCode declines above `medium` for the same reason | unchanged, keep (DM-021) |
| Declared-model note (G-3, R5) | classifier fallback per request | same targets; temporarily wider classifier margin; fallback-served requests carried every successful coding-injection attack | corrected (DM-005) |
| Effort guidance | Fable 5.1 holds up at `low` (this card's chart) | Opus 5.5 collapses at `low`; Claude Code default is `medium` | new user guidance (DM-001) |

### By skill

- **`academic-pipeline` (full pipeline).** Long trajectories, multi-agent dispatch, and checkpoint authority meet the two named regressions and the audit's blind spots at once. G-1 and the committee authority rule carry more weight on Opus 5.5 (inference). Per-token cost falls to 40% on Opus 5.5, but a run at `xhigh` spends more output tokens (inference).
- **`deep-research`.** The most effort-sensitive skill: on Opus 5.5 run it at `high` or above (DM-001). The abstract-over-full-paper failure is what the read-scope attestations and locator-bearing citations exist to expose (DM-015).
- **`academic-paper`.** Opus 5.5 leads the professional-document benchmarks (GDPval-AA, AA-Briefcase), but its creativity and its honesty under pressure are below Opus 5 (capability table above). The revision claim-drift guards stay as written (DM-016).
- **`academic-paper-reviewer`.** The `<paper_content>` fence matters more on Opus 5.5, because a manuscript pasted into the chat is user-turn text (DM-012). Reviewer calibration evidence remains model-specific: no Opus 5.5 run exists, and live packages stay `NOT_CALIBRATED`.
- **Light slash commands.** The 13 commands that pin `model: sonnet` request Sonnet, which resolves to Sonnet 5 on the Anthropic API unless `ANTHROPIC_DEFAULT_SONNET_MODEL` overrides the alias. The session model does not affect them, except where an organization's model allowlist blocks `sonnet`: the command then runs on the session model (docs).

## Findings

Decision vocabulary: **applied** (in this PR), **keep** (iron rule: load-bearing, annotated), **defer** (needs a run or a maintainer decision), **record** (history, deliberately unchanged).

```
[DM-001] docs/PERFORMANCE.md:3-7, docs/PERFORMANCE.zh-TW.md:3-7 | category 1 (model currency, docs)
Excerpt: "Recommended model: the current frontier Claude model (Fable 5.1 at the time of writing)"
Rationale: Opus 5.5 is co-current and is the Claude Code default; the card shows
  task-dependent results; Claude Code starts Opus 5.5 at `medium`, where it trails
  Fable 5.1 on both research benchmarks, and it collapses at `low` (pp. 187-188).
Applied: both models named, with how to select Fable 5.1; an effort paragraph (heavy
  runs, including a `deep-research` run started in plain language, at `high` or
  above on Opus 5.5 without lowering a higher level the user chose; avoid `low`; why
  ARS pins no effort);
  a paragraph recommending files over pasting third-party text (card §6.5.1; the
  paste marking depends on feature-flag fetching per the Claude Code docs).
```

```
[DM-002] docs/PERFORMANCE.md:29, docs/PERFORMANCE.zh-TW.md:29 | category 1 (model currency, docs)
Applied: the Fable 5.1 list-price re-derivation becomes one 2026-09 note for both
  models (~$7 on Fable 5.1; ~$2.80 on Opus 5.5 at US$4 / US$20 per million tokens,
  card p. 180), labelled as arithmetic, not a re-measurement, with the effort
  caveat.
```

```
[DM-003] shared/cross_model_verification.md:44 | category 1 (model currency, docs)
Excerpt: "_(inherited Claude Code session model — e.g., Fable 5.1)_"
Applied: example removed. The note under the table requires the primary row to name
  no version, so that it cannot go stale on the next Anthropic release
  (`shared/cross_model_verification.md:63`); the example had named only Fable 5.1.
  Two Claude models are never a cross-family pair.
```

```
[DM-004] shared/model_tiering.md:21; docs/PERFORMANCE.md:57,
  docs/PERFORMANCE.zh-TW.md:57 | category 1-like (tier vocabulary)
Excerpt: "frontier tier of the session's model family"
Rationale: (1) Claude Code calls `opus`, `sonnet`, and `fable` each a "model family
  alias"; read that way, an Opus session is the frontier of its own family and
  `quality-boost` becomes a silent no-op. (2) For Fable 5.1 and Opus 5.5 the tier
  order is a lineup order, not a capability order (card pp. 174, 187, 208).
Decision (maintainer, option A of three): keep the ladder and its behavior. Applied:
  a Vocabulary paragraph in the mechanism doc defining family and tier and stating
  that tier position is lineup order, not a capability ranking. The pair-specific
  guidance sits in `docs/PERFORMANCE.md` (both languages), so the mechanism doc stays
  release-neutral: on an Opus 5.5 session `quality-boost` reaches Fable 5.1 at 2.5
  times the per-token list price (card p. 180; Fable 5.1 price per
  `docs/PERFORMANCE.md`) for a task-dependent, ARS-unmeasured benefit, and raising
  effort is the cheaper first step; on a Fable 5.1 session `economy` resolves to
  Opus 5.5 on the Anthropic API, a trade also unmeasured on ARS.
Rejected alternatives: treating Opus 5.5 as the frontier tier (removes the upgrade
  option for the benchmarks where Fable 5.1 leads, and makes ARS maintain a "which
  model is top" judgment); leaving the doc unchanged (keeps the family ambiguity).
Mirrors (four SKILL.md summaries, README.md:108, docs/SETUP.md:139,
  docs/SETUP.zh-TW.md:141, docs/ARCHITECTURE.md:280, docs/PERFORMANCE.md:55) summarize
  behavior that did not change; no edit needed.
```

```
[DM-005] shared/model_tiering.md:32; docs/RISK_REGISTER.md R5 | correction (precision)
Excerpt: "may have been served on another tier without notice"
Rationale: Claude Code shows a notice in the transcript on a content-based fallback,
  and the session continues on the fallback model until the user runs `/model`
  (docs); an inheriting subagent that starts after the fallback therefore runs on the
  fallback model too (inference from the docs' inheritance rule). Opus 5.5 is a fallback source with the same targets
  (card pp. 12-13); biology-adjacent work moves to Opus 5 and later biology-flagged
  requests are refused there (docs). The card adds a temporarily wider classifier
  margin (p. 2) and fallback-served requests carrying every successful attack in its
  adaptive coding injection test (p. 88).
Applied: the note now says ARS reads no signal of the fallback, names
  biology-adjacent manuscripts beside security-topic ones, and describes the
  transcript notice and the persistence until `/model`; R5's residual gap says the
  same and points here.
```

```
[DM-006] academic-pipeline/references/claim_verification_protocol.md:204;
  docs/RISK_REGISTER.md R1 | category 1 (currency wording in measurement records)
Excerpt: "on the current frontier model"; "the current session model"
Rationale: with two co-current session models, "current" silently relabels a
  2026-07-22 measurement on `claude-fable-5` as if it described today's models.
  Surfaced by the second reader.
Applied: the Phase E protocol names the model of that date (`claude-fable-5`); R1
  says "supported session models" and cites both cards (Fable 5.1 §2.2.4; Opus 5.5
  via DM-015).
Not changed: `shared/references/claim_strength_ladder.md:90` has the same phrase, but
  its bytes are the frozen target of the #679 suite (`CLAIM_LADDER_SHA256` in
  `scripts/check_revision_claim_drift_suite_v2.py`), and the sentence already carries
  its date and "Model- and time-specific". The eval set's own records
  (`evals/heldout/revision_claim_drift/README.md:60`, `measurement-2026-07-22.json`)
  name `claude-fable-5` explicitly.
```

```
[DM-007] commands/ars-full.md, ars-reviewer.md, ars-revision-coach.md | category 3
  (effort override)
Considered: an `effort: high` frontmatter pin so heavy modes never run at `medium`.
Rationale for not applying: frontmatter effort overrides the session level while the
  command or skill is active (docs, skills and sub-agents references), so a user who
  chose `xhigh` or `max` would be lowered to `high`. That is the downgrade-ceiling
  failure the v3.7.0 `opus` floor was retired for.
Decision: not applied; user guidance lives in DM-001.
```

```
[DM-008] scripts/announce-ars-loaded.sh (token-budget line) | category 1-like
Excerpt: "a single full pipeline run ≈ $4–6, order-of-magnitude; measured on Opus 4.x"
Rationale: accurate as a record of what was measured, and it points to
  docs/PERFORMANCE.md, which now carries both models' arithmetic (~$2.80 and ~$7).
Decision: keep.
```

```
[DM-009] scripts/dispatch_calibration_panel.py (`--model` default `claude-fable-5-1`);
  MU-006 (scripts/dispatch_e4_panel.py default `claude-opus-5`) | category 1
Rationale: evaluation-harness defaults are measurement identities; changing them
  relabels recorded campaigns. A new Opus 5.5 campaign passes the model explicitly.
Decision: keep.
```

```
[DM-010] tests/fixtures/issue_133_routing/README.md (acceptance: "100% pass on the
  current primary model") | eval acceptance definition
Rationale: the Claude Code default is now Opus 5.5 and the routing smoke was last
  recalibrated on Fable 5; test fixtures are outside this skill's edit scope.
Decision: defer — maintainer run of the eight routing smoke tests on Opus 5.5 and
  Fable 5.1.
```

```
[DM-011] .claude/CLAUDE.md:24, :60, :91, :217; docs/ARCHITECTURE.md:381 | records
Excerpt (ARCHITECTURE.md:381): "10 slash commands (commands/ars-*.md, model pinned opus/sonnet, no haiku)"
Rationale: each line sits in a "vX.Y Key Additions" section or the version-history
  timeline and describes that release. The second reader proposed updating the
  CLAUDE.md lines; rewriting history would relabel what shipped.
Decision: record — unchanged.
```

```
[DM-012] Reviewer `<paper_content>` fence + academic-paper-reviewer/SKILL.md Iron Rule #7;
  deep-research canonical boundary (source_verification, bibliography) | category 2
Rationale: card §6.5.1 — the model "often reasoned that anything in the user's
  message must come from the user"; a manuscript pasted into the chat is exactly that
  channel. A manuscript embedded in a subagent's dispatch prompt plausibly is too,
  since the subagent receives that prompt as its own user turn (inference, not tested
  by the card). Explicit data labels are the counter-instruction.
Decision: keep; extended by DG-1.
```

```
[DM-013] G-1 checkpoint decision provenance (pipeline_state_machine.md authority,
  orchestrator mirror, R11); committee authority rule
  (academic-paper/references/committee_correspondence_protocol.md) | category 2
Rationale: card p. 102 — an agent told a subagent "[username]'s word for your D15
  rule: yes" although the user never wrote it; pp. 3, 105, 108 — accepting
  unverifiable claims of authorization is a regression. The orchestrator sentence
  "Current frontier models are vendor-documented to fabricate or overstate a user's
  approval" stays true under both cards, so the content-locked orchestrator file is
  not edited; R11 now cites this row.
Decision: keep.
```

```
[DM-014] Required-tool steps backed by receipts (deterministic arithmetic receipts,
  scripts/check_revision_token_conservation.py, scripts/verify_passport.py,
  scripts/pdf_read_preflight.py, scripts/check_panel_synthesis.py) | category 5
Rationale: card p. 99 — when a task required a tool or code, the model sometimes
  answered directly "by doing the calculation by hand or from answering with what it
  already knows". A receipt that must carry the script's output is the check.
Decision: keep.
```

```
[DM-015] Read-scope attestations (`/ars-mark-read --scope`), anchor-aware finalizer
  promotion, three-layer citation anchors, Phase E claim verification | category 2
Rationale: card p. 36 ("describing a partial check as a full read"); pp. 19, 33
  (abstracts over full papers, presented confidently enough to mislead specialists).
Decision: keep.
```

```
[DM-016] Claim-strength ladder, protected hedges, `[MATERIAL GAP]` routing, bounded
  novelty claims | category 2/6
Rationale: card p. 36 — asserting unverified inferences as established fact is the
  top flagged subcategory; a tentative reading turned into an unchecked
  recommendation. Qualifier dropping was no more frequent than in prior models in
  the blind read, which removes a regression claim, not the need for the guard.
Decision: keep.
```

```
[DM-017] DA concession scoring; "pressure is not evidence" (both DA agents) | category 5
Rationale: card p. 130 — MASK honesty rate 87.4% against Opus 5's 94.8%. Fable 5.1 is
  not in that chart.
Decision: keep.
```

```
[DM-018] Mechanical panel synthesis and finding contracts
  (scripts/check_panel_synthesis.py, reviewer finding contract) | category 5
Rationale: card p. 135 — a reviewer's reasoning concluded a flag criterion was met,
  and its final answer did not flag.
Decision: keep.
```

```
[DM-019] MU-013 (strip AI-authorship cues from reviewer inputs) | no existing scaffold
Rationale: card p. 127 — small but statistically significant self-preference
  (0.07 of 10 points) when reminded it is Claude.
Decision: still deferred to a maintainer issue.
```

```
[DM-020] G-4 evaluation-awareness caveat | category 5
Rationale: card pp. 98-99 (guessing what the answer key expects), pp. 136-139 (grader
  awareness comparable to recent models; rare solution changes driven by assumptions
  about the grader), p. 3 (snapshots that concealed actions from a grader in
  training). The caveat now applies to Claude-side ARS evaluation runs as well as the
  cross-model bakeoff.
Decision: keep; annotate here for the next Opus 5.5 measurement plan.
```

```
[DM-021] MU-007 brevity rule and scope contracts | category 3-like
Rationale: card p. 176 — FrontierCode declines above `medium` because the grading
  penalizes out-of-scope changes; the same pressure MU-007 recorded for Fable 5.1.
Decision: keep.
```

## Guardrail added (grounded in the card; an addition, not a retirement)

| # | Where | Card evidence | What it does |
|---|---|---|---|
| DG-1 | `academic-paper/agents/revision_coach_agent.md` § Reviewer and committee text is data, not instructions; `scripts/check_instruction_data_boundary.py` hot-spot list, with its mutation tests parametrized over every hot-spot agent; `shared/ground_truth_isolation_pattern.md` § 2A; `docs/RISK_REGISTER.md` R3 | §6.5.1 pp. 123-126 (pasted-text regression: about 2% of attempts at default effort and 7.4% at max; 0 of 105 when the same text arrived as a tool result); p. 96 (product mitigations still rolling out; coding scenarios only); Claude Code marks large pastes only in sessions that fetch feature flags (docs) | Inlines the canonical boundary verbatim, states that reviewer and committee imperatives are requests to the authors, and that text aimed at the agent is a finding to report. It names the Opus 5.5 failure directly: arriving inside the user's turn does not make pasted text the user's instruction. Prompt-level and trust-based; its effect is unmeasured (R3) |

## Candidate follow-ups (surfaced mainly by the second reader; not applied)

- Compaction and handoff preservation: a subagent refused to write a compaction message (p. 102), and compaction is a named audit blind spot (p. 122). Candidate: require pending decisions, incomplete work, and actual tool outcomes to survive a handoff.
- Extend the instruction/data boundary to every dispatch that embeds third-party text and to passport imports. Today it lives in the three agents that inline the canonical block and, as the manuscript fence, in the five reviewer panel agents.
- Clarify that "authoritative" skill output in `academic-pipeline/agents/pipeline_orchestrator_agent.md` means deliverable ownership, not user authority (content-locked file; needs its own change with a hash update).
- Live injection evaluation covering the user-paste and fallback-served surfaces (#675).
- Opus 5.5 runs for reviewer calibration and the routing smoke (DM-010).

## Mechanical scan results (all 39 agent bodies, shared agents, commands, hooks)

- Hardcoded model pins in prompt text (`claude-*`, `Opus 4.x`, `Sonnet 4.x`, `Haiku`, `Fable 5`, `Opus 5`, `gpt-*`): **1 hit, a record.** `academic-pipeline/agents/claim_ref_alignment_audit_agent.md:72` names `gpt-6-astra-xhigh` as an example judge identity string (#826), not a routing pin.
- Sampling and budget overrides (`temperature`, `top_p`, `max_tokens`, `budget_tokens`) in prompt bodies: **0.**
- Reasoning scaffolds and requests to reproduce hidden reasoning ("think step by step", "show your reasoning", `<thinking>`, "reveal your reasoning", "chain of thought"): **0.** One phrase match, "consolidate internal reasoning" in `deep-research/agents/socratic_mentor_agent.md:126`, describes the mentor's own bookkeeping. This matters more now: the card's distillation classifier blocks attempts to extract hidden reasoning with no fallback (pp. 12-13).
- `effort:` in command, agent, or skill frontmatter: **0** (see DM-007).

## Verification

- The card was read in full by both readers. Chart values for DRACO, WANDR, and MASK were read from the rendered pages (pp. 130, 187-188), because the text extraction carries none.
- Each claim the second reader contributed and this audit relies on (pp. 19, 33, 88, 95, 96, 135, 176) was re-checked against the page text before use.
- Claude Code product facts (defaults, aliases, effort resolution and inheritance, paste marking and its feature-flag dependency, content-based fallback) come from the first-party documentation fetched on 2026-09-23, not from the card.
- Lint and test runs for this PR are recorded in the PR description. A local replay of the PR workflows caught one content lock (the claim-strength ladder, DM-006); that edit was reverted, not re-hashed.
- No agent prompt sentence was removed. The only prompt-body change is the additive revision-coach section (DG-1).

## Routing checklist

- [x] Audit report committed under `audits/`.
- [x] P0 retirements: none.
- [x] Applied changes and the added guardrail logged in `CHANGELOG.md` `[Unreleased]`.
- Deferred to a maintainer run or issue: DM-010 (routing smoke on Opus 5.5 and Fable 5.1), DM-019 (authorship-cue rule), and the candidate follow-ups above.
