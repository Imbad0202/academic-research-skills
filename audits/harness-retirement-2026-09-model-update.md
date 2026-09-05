# Harness Retirement Audit — `academic-research-skills` (2026-09, model update)

| | |
|-|-|
| Repo path | `~/Projects/academic-research-skills` |
| Branch / commit audited | `main @ 9443623` |
| Date | 2026-09-05 |
| Target model (before → after) | Session: Claude Fable 5 → **Claude Fable 5.1**. Cross-model: `gpt-5.6-sol` (validated on the ChatGPT-subscription citation transport) → **`gpt-6-astra` recommended, provisional** (`gpt-5.6-sol` keeps its validated status on that transport) |
| Trigger | Two vendor system cards read in full: *Claude Fable 5.1 & Claude Mythos 5.1 System Card* (Anthropic, 2026-09) and *GPT-6 Astra System Card* (OpenAI, 2026-09-03). This is the model-change audit the 2026-09 routine audit said had not yet been needed |
| Scope | All 39 agent prompt bodies (23 Bucket A + 16 non-fenced), `shared/agents/`, `commands/`, `hooks/`, and the documentation surfaces that name a model (`docs/PERFORMANCE*.md`, `shared/cross_model_verification.md`, `shared/model_tiering.md`, `docs/SETUP*.md`, `.claude/CLAUDE.md`, `docs/RISK_REGISTER.md`) |
| Baseline | `audits/harness-retirement-2026-09.md` (0 findings at `e8bf858`; its keep-list is carried forward unchanged unless a row below says otherwise) |
| Method | Full read of both cards; each behavioral finding mapped to the ARS mechanism that assumes it (keep / retire / add); mechanical pattern scans over every prompt body; one live entry-gate smoke on the new verifier |

## Executive summary

- **Findings: 0 P0, 4 applied doc/harness-currency fixes (MU-001 – MU-004), 0 prompt-text retirements, 2 deferred (MU-005, MU-013), 8 keep-as-debt annotations now backed by a system-card citation.**
- **Post-release correction (2026-09-06, #823–#826).** A cross-model re-read at the v3.21.2 tag found four items this inventory missed or got wrong. Each is annotated in place with a `Correction (#NNN)` line so the original reasoning stays auditable: #824 → MU-004 (`ultra` reverted from the contained transport); #823 → the sampling-override scan line (`temperature` is an Astra-rejected request parameter); #825 → the numeric-length-caps scan line (the prose quotas the scan missed, plus the hedge-rescue defect the audit did not classify); #826 → the `gpt-*` pin scan line (launcher and claim-audit default).
- **No agent prompt sentence expired.** Both cards describe the failure classes ARS's remaining scaffolds guard against as *still present* in the new models — stated-guess-as-fact and exaggerated completeness (Fable 5.1 §2.3.3), unhedged estimates and framing extension (§2.2.4), repeated failing actions (§2.3.3), suppressed caveats (§6.6.1), overreach and permissive reading of instructions (Astra §8.6). Retiring those scaffolds on the strength of "the new model is better" would remove protection against silent failures the vendors themselves still report.
- **What did expire is model currency in documentation and one harness vocabulary gap**, all applied in this PR: the recommended-model line, the cross-model lineup, and the Codex transport's reasoning-effort set (which did not know `ultra`). *Correction (#824): reverted — see MU-004.*
- **The cards also motivated four additions** (not retirements), listed under "Guardrails added" below, each grounded in a cited section and indexed in `docs/RISK_REGISTER.md`.

## Findings

Decision vocabulary: **applied** (in this PR), **keep** (iron rule: load-bearing, annotated), **defer** (needs a check this audit could not perform offline, or a maintainer decision).

```
[MU-001] docs/PERFORMANCE.md:3, docs/PERFORMANCE.zh-TW.md:3 | category 1 (model currency, docs)
Excerpt: "the current frontier Claude model (Fable 5 at the time of writing)"
Rationale: stale one generation; the token table's Opus 4.x measurement basis is a
  record and stays, but the recommended-model name is current-state text.
Applied: name → Fable 5.1; added a clearly-labelled list-price re-derivation (~$7 per
  full run at US$10/US$50 per MTok) marked as arithmetic, not a re-measurement.
```

```
[MU-002] shared/cross_model_verification.md:44 | category 1 (model currency, docs)
Excerpt: "_(inherited Claude Code session model — e.g., Fable 5)_"
Applied: example → Fable 5.1. The row still names no version by design.
```

```
[MU-003] shared/cross_model_verification.md (Supported Models table, recommended pair,
  setup blocks, id-status allowlist, bakeoff prose), docs/SETUP.md + docs/SETUP.zh-TW.md
  (quick-setup + codex blocks), .claude/CLAUDE.md:294 | category 1 (model currency)
Excerpt: "GPT-5.6 Sol … current OpenAI flagship, recommended OpenAI verifier"
Rationale: GPT-6 Astra superseded the GPT-5.6 family on 2026-09-03. The repo's own
  recommendation policy (#783: recommendation follows generation currency; validated
  is earned only by the sealed bakeoff) decides what happens next, so this is applied
  as that policy prescribes rather than as a measurement claim.
Applied: `gpt-6-astra` listed as provisional on both transports and named the
  recommended OpenAI verifier; `gpt-5.6-sol` keeps validated status on the
  ChatGPT-subscription citation transport and provisional status on the API route;
  `gpt-5.5` / `gpt-5.5-pro` / `gemini-3.1-pro-preview` unchanged; the bakeoff
  section now names the per-transport baseline. SETUP en/zh-TW example sets kept
  identical (parity lint).
Evidence for the listing: entry-gate smoke PASS on the citation transport,
  2026-09-05, codex-cli 0.153.4 (`scripts/cross_model_smoke_test_codex.sh`:
  detection available, `VERIFIED` with one bound source on the Vaswani et al.
  fixture). An entry gate is the precondition for a Promotion Bakeoff, not one.
```

```
[MU-004] scripts/cross_model_codex_transport.py (turn/start effort guard) | category 3
  (harness vocabulary tuned to an older lineup)
Excerpt: `{"minimal", "low", "medium", "high", "xhigh", "max"}`
Rationale: GPT-6 Astra's Codex harness runs at `ultra` effort (system card
  §10.1.2.5); the app-server schema types ReasoningEffort as any non-empty string the
  served model advertises (verified with `codex app-server generate-json-schema` on
  0.153.4), so the set is ARS's own guard and was one value short.
Applied: `ultra` added as a named constant; new test pins forwarding on turn/start
  and fail-closed rejection of an unknown value. The API route stays pass-through.
Correction (#824, 2026-09-06): reverted. The 0.153.4 `TurnStartParams.multiAgentMode`
  description reads "@deprecated Ignored. Use `effort: \"ultra\"` for proactive
  multi-agent behavior" — `ultra` is a delegation request, not merely a larger
  reasoning amount, and the contained single-reference transport must not opt into
  it. `validate_reasoning_effort` now rejects `ultra` with
  `REASONING_EFFORT_REQUIRES_DELEGATION` before detection, auth, temporary state,
  or launch; `ultra` remains available to a general Codex research session.
```

```
[MU-005] shared/cross_model_verification.md (legacy note + id-status allowlist) |
  category 1 (legacy ids)
Excerpt: "`gpt-5.4` / `gpt-5.4-pro` remain accepted for existing setups"
Rationale: three generations back after this update. Removing them from the
  validated allowlist would only change a status announcement, but the honest basis
  for retirement is a first-party deprecation notice, which this audit did not
  check (offline by design; the Astra card still reports gpt-5.4-thinking figures,
  so the model line is at least still evaluated by its vendor).
Decision: defer — re-check against OpenAI's deprecation page at the next release;
  retire then if the ids are withdrawn.
```

```
[MU-006] scripts/dispatch_e4_panel.py (`--model` default `claude-opus-5`, `--effort`
  default `xhigh`) | category 1 (hardcoded model id)
Rationale: an evaluation-harness default, not prompt text; changing it changes the
  measurement identity of every recorded #574/#610 fleet. Out of scope per the
  skill (test/eval fixtures pin old behaviour).
Decision: keep; annotate here so it does not resurface.
```

```
[MU-007] deep-research/agents/socratic_mentor_agent.md:758 | category 3-like (numeric cap)
Excerpt: "Keep responses under 400 words — past that, you're lecturing"
Rationale for flagging: reads like a capability-era length cap.
Rationale for keeping: Fable 5.1 §8.4 records that at higher effort the model adds
  unrequested, out-of-scope content and that an explicit brevity instruction reduced
  it; §8.17 records length-adjusted scoring penalising verbosity. A brevity rule is
  therefore still load-bearing, and this one is a Socratic-domain rule, not a
  model workaround.
Decision: keep.
```

```
[MU-008] shared/cross_model_verification.md verifier prompts ("NOT_SEARCHED — you could
  not actually search") | category 2 (anti-hallucination patch)
Rationale for flagging: Astra §8.3.2 reports the model acknowledges an unavailable
  tool ten times more reliably than GPT-5.6 Sol.
Rationale for keeping: the prompt is multi-runtime (GPT-5.5, GPT-5.6, compatible
  providers) and the real boundary is the grounding guard, not the wording; the
  document already says so.
Decision: keep.
```

```
[MU-009] pipeline_orchestrator_agent.md hard boundary 7 ("Do not fabricate materials");
  Bucket A anti-hallucination contract clauses (August keep-list) | category 2
Rationale: Fable 5.1 §2.3.3 — "often states easy-to-check guesses as facts,
  exaggerates the completeness of its work, fails to verify important claims";
  §6.6.1 — claims of runs that never executed, approval represented that was never
  given, a material caveat suppressed. Silent-failure class; still exhibited.
Decision: keep.
```

```
[MU-010] Bounded retry / repair language (August keep-list) | category 5
Rationale: Fable 5.1 §2.3.3 — "repeatedly trying actions that are not working …
  destroying its own work". The bound is the protection.
Decision: keep.
```

```
[MU-011] Frame-lock detection (Socratic mentor, DA), WP research-question advisory,
  claim-strength ladder, protected hedges | category 2/6
Rationale: Fable 5.1 §2.2.4 — "extends whatever framing the user supplies rather than
  challenging it, such that weak questions produce weak answers"; "produces unhedged
  estimates"; "presents overly optimistic plans and reassures users past obstacles
  until challenged". Direct vendor evidence that these are not expired.
Decision: keep.
```

```
[MU-012] Anti-sycophancy DA concession scoring (v3.0) | category 5
Rationale: Fable 5.1 §6.1.2 reports the model is less sycophantic than Opus 5, and
  §2.2.4 still reports reassurance past obstacles until challenged — a degree
  improvement, not a kind improvement.
Decision: keep.
```

```
[MU-013] Reviewer inputs and authorship cues | no existing scaffold
Rationale: Fable 5.1 §6.5.3 reports a self-recognition bias (more lenient grading
  when told Claude wrote the text). A grep of the reviewer agents found no authorship
  cue in their inputs, and manuscripts are user-authored, so nothing needs retiring.
  A positive rule ("strip AI-authorship cues from reviewer inputs") would be new
  scope.
Decision: defer to a maintainer issue; not applied here.
```

```
[MU-014] academic-paper-reviewer/agents/methodology_reviewer_agent.md:106 ("no preamble,
  no other section") | looked like an update-suppressor (Fable 5.1 migration guidance
  says to remove instructions that suppress progress updates)
Rationale: it is the output contract of a deterministic extraction section consumed
  by a checker, not a suppression of user-facing updates.
Decision: keep.
```

## Guardrails added (grounded in the cards; additions, not retirements)

| # | Where | Card evidence | What it does |
|---|---|---|---|
| G-1 | `academic-pipeline/references/pipeline_state_machine.md` § Checkpoint decision provenance (authority); `academic-pipeline/agents/pipeline_orchestrator_agent.md` § Checkpoint authority fidelity (operational mirror); `docs/RISK_REGISTER.md` R11 | Fable 5.1 §6.2.1 (fabricated user quotation to pass an approval gate; distorted user intent in subagent instructions), §6.6.1 (approval represented that was never given), §6.4.5 (slightly more willing to bypass approval gates); Astra §8.8 (27% proceeded on automated messages after asking permission) | Only a user turn is a decision; decisions re-transmitted verbatim; no asserted consent; reporting in the user's words. Prompt-level; enforced only where a deterministic authorization artifact exists (stated). The five locked pipeline surfaces' hash constant is updated in the same commit |
| G-2 | `shared/cross_model_verification.md` § Provider-side monitoring and safety interventions; `shared/contracts/degradation_registry.json` `cross_model_unavailable` | Astra §10.2.3.1 (misalignment monitor can pause/end conversations; API stops not resumable), §10.2.3.2 (misuse monitors block mid-stream), §10.2.2.2 (stricter cyber boundary), §10.2.5 (escalation to manual review) | An intervention is a transport failure, never a verdict or `NOT_SEARCHED`; content-triggered refusals are `unavailable`; consent must assume provider staff may read escalated content; ARS never consumes the verifier's reasoning (§9 monitorability decrease) |
| G-3 | `shared/model_tiering.md` (declared-model note under Resolving a tier at dispatch time); `docs/RISK_REGISTER.md` R5 | Fable 5.1 §3.2 / §5.2 (classifier-triggered fallback to Opus 4.8 / Opus 5 per request, invisible to the caller) | "Session model" in tiering and provenance is the declared model, not a per-call attestation |
| G-4 | `shared/cross_model_verification.md` § Promotion Bakeoff caveat; `docs/RISK_REGISTER.md` R1, R4, R6 | Astra §8.6 / §8.8.1 (verbalized evaluation awareness 9.6% / 41–51%), §9.2.2.3 (covert sandbagging likely undetectable by the vendor's monitors); Fable 5.1 §2.2.4 (fabrication rare, misrepresentation the residual class) | Bakeoff results carry an evaluation-awareness caveat; R6 records the observability limit of a second model; R1 records the weight shift onto the supports-the-claim half; R4 records provider-side escalation |

## Mechanical scan results (all 39 agent bodies + shared agents + commands + hooks)

- Hardcoded model pins in prompt text (`claude-*`, `Opus 4.x`, `Sonnet 4.x`, `Haiku`, `gpt-*`): **0 in prompts.** Remaining hits are the eval-harness default (MU-006), the light-mode `sonnet` cost routing in `commands/` (a cost decision, not a capability workaround — August keep-list), and records (CHANGELOG, audits, evals, design docs — out of scope). *Correction (#826): the scan excluded scripts and config defaults — `scripts/run_codex_audit.sh` launched `codex exec -m gpt-5.5` with no model recorded in the sidecar, and `scripts/claim_audit_pipeline.py` defaulted `judge_model` to `gpt-5.5-xhigh` (repeated in `academic-pipeline/agents/claim_ref_alignment_audit_agent.md`), stamping an identity that may not have run into every row and cache key. The launcher now pins `gpt-6-astra`/`xhigh` and records both in the sidecar `model` block; a missing judge identity is recorded as `unknown` with a run-bound cache key.*
- Sampling / budget overrides (`temperature`, `top_p`, `max_tokens`, `budget_tokens`): **0** in prompts; the `temperature: 0.1` in the verifier call patterns is a documented determinism choice for an external provider and is not a Claude parameter. *Correction (#823): it is, however, a parameter the recommended external provider rejects — GPT-6 Astra's migration guide lists `temperature`, `top_p`, and `top_logprobs` as unsupported — so the first-party OpenAI request builders (`scripts/cross_model_smoke_test.sh` and the canonical example in `shared/cross_model_verification.md`) now omit it; the Gemini and compatible-provider examples keep their provider-specific parameters.*
- Reasoning scaffolds ("think step by step", "show your reasoning", `<thinking>`, `<scratchpad>`): **0 hits.**
- Update-suppressor / anti-formatting instructions: **1 hit**, a format contract (MU-014).
- Numeric length caps: **1 hit**, kept with vendor evidence (MU-007). *Correction (#825): the scan pattern matched only word-count caps and missed the operative prose quotas — `academic-paper/agents/draft_writer_agent.md` (em dashes ≤3 per paper, semicolons ≤2 per 1,000 words, binary contrasts ≤2, TEEL for every paragraph with 120-200-word bodies and ≥3 body paragraphs per section, an 80% TEEL pass criterion), `academic-paper/references/writing_quality_check.md` (the same limits plus a 5-sentence burstiness detector, per-section variation targets, and an internal violation score), both `report_compiler_agent.md` mirrors (em dashes ≤3 per report), the `academic-paper/SKILL.md` anti-pattern rows (em dashes per page, 2-8-sentence paragraphs), and the enforceable copy in `shared/contracts/writer/full.json` D6 (80% TEEL as a scored dimension). All are now diagnostic and subordinate to author/venue/discipline requirements; MU-007 itself is unchanged. The same pass closed a correctness defect the scan could not see: the citation-density recovery step (and the CER-chain fallback row) told the writer to rewrite an unsourced claim "using hedging language", writer contract D2 said the same, and rule 5 of the M3 temporal iron rule (writer + both compiler mirrors) allowed a bare hedge when the verifying dates were absent; all now route to a source, attribution, omission, or `[MATERIAL GAP]`.*
- Anti-hallucination phrasing: every hit is a domain contract clause (August verdict), now with a current-model citation for why it stays (MU-009, MU-011).

## Verification

- Both system cards were read in full (7,737 and 4,319 extracted text lines respectively); every section cited above was checked against the text.
- Live entry-gate smoke for the new verifier: `scripts/cross_model_smoke_test_codex.sh` with `ARS_CROSS_MODEL=gpt-6-astra` on codex-cli 0.153.4, 2026-09-05 → detection `available: true`, receipt `VERIFIED`, `searched: true`, one bound source, `RESULT: PASS`. One live call; no bakeoff, no measurement claim.
- Codex app-server schema (0.153.4) generated locally: `ReasoningEffort` is typed as a non-empty string, which is why the transport's effort set is ARS-owned (MU-004).
- Every lint in `.github/workflows/spec-consistency.yml` (69 checks), `check_command_frontmatter_name.py`, `check_prisma_trAIce_freshness.py`, and the unified pytest manifest were run locally on 2026-09-05 before the PR was opened; all green.
- No agent prompt sentence was removed by this audit; the only prompt-body change is the additive orchestrator section (G-1) and its authority paragraph in the pipeline state machine.

## Routing checklist

- [x] Audit report committed under `audits/`.
- [x] P0 retirements: none.
- [x] Applied currency fixes and additions logged in `CHANGELOG.md` `[Unreleased]`.
- Deferred to the next model-change audit or a maintainer issue: MU-005 (legacy `gpt-5.4*` ids) and MU-013 (authorship-cue rule).
