# ARS Performance Notes

> **Recommended models: Claude Fable 5.2, Claude Fable 5.1, or Claude Opus 5.5** (at the time of writing) with **Max plan** (or equivalent configuration). Claude Code starts on Opus 5.5 by default on Anthropic plans, the Anthropic API, and most cloud providers (Microsoft Foundry defaults to Sonnet 4.5). Select Fable 5.2 with `/model fable`; it needs Claude Code v2.1.321 or later (in Claude apps gateway sessions, where `fable` means Fable 5, use `/model claude-fable-5-2`). Select Fable 5.1 by its model ID, `/model claude-fable-5-1`; Anthropic now lists it as a legacy model that is still available. On Pro and Max plans, a `claude-fable-5-1` saved in your user settings moves to the `fable` alias, and so to Fable 5.2, the first time you run v2.1.321 or later; run `/model` to see which model a session uses. Fable 5.2 requires 30-day data retention and is not available under zero data retention unless Anthropic expressly authorizes it. No model is better at everything. By its own count, the Fable 5.2 system card puts Fable 5.2 highest on 14 of the 16 Fable 5.2 results in its summary table (p. 4), and on WANDR wide search at every effort level. It puts Fable 5.2 below Opus 5.5 on DRACO deep research from `medium` to `xhigh` and on the GDPval-AA and AA-Briefcase Elo ratings of documents, and below Fable 5.1 on DRACO at every level under `max` (Fable 5.2 card pp. 4, 207, 219, 221, 239; Fable 5.1's middle DRACO values are in the Opus 5.5 card, p. 187). Between the two older models, the Opus 5.5 system card puts Opus 5.5 ahead of Fable 5.1 on every row of its capability summary table, but behind it on DRACO deep research and OfficeQA document reasoning (Opus 5.5 card pp. 174, 187, 208). Current Claude models use adaptive thinking; you no longer set a fixed thinking budget.
>
> **Set the effort level on Fable 5.2 and Opus 5.5.** Claude Code starts both at `medium` effort, and Fable 5.1 at `high`. A session that moved from Fable 5.1 to Fable 5.2 also starts at `medium`, unless you already chose a level for it. On the cards' two research benchmarks, DRACO deep research and WANDR wide search, Fable 5.1 at its `high` default scores 86.5 and 66.7. Fable 5.2 scores 82.2 / 73.6 at `medium`, 84.1 / 79.3 at `high`, and 85.2 / 80.6 at `xhigh` (Fable 5.2 card pp. 219, 221). Opus 5.5 scores 86.7 / 71.3 at `xhigh`, 83.9 / 62.8 at `medium`, and 72.5 / 31.2 at `low` (Opus 5.5 card pp. 187-188). Before a heavy run on a Fable 5.2 or Opus 5.5 session (`/ars-full`, `/ars-reviewer`, `/ars-revision-coach`, or a `deep-research` run started in plain language), make sure effort is at least `high`: if it is lower, raise it with `/effort high` or `/effort xhigh` (a level typed after `/effort` also becomes your saved default for that model), and keep `xhigh` or `max` if you already use them. Avoid `low` on Opus 5.5. Higher effort does not remove one finding in the Fable 5.2 card: in its replayed coding sessions the model, tested as Claude Mythos 5.2 (the same underlying model with different safeguards), left doable, requested work undone in 6 to 13% of sessions at `medium` to `xhigh`, against 4% for Fable 5.1 (p. 34). ARS has not measured this on its own stages, so check at each checkpoint that the stage produced what it should have. ARS deliberately does not pin effort in command frontmatter: a pin would also lower a user who chose `xhigh` or `max`.
>
> **Give third-party text to ARS as a file when you can.** Opus 5.5 is more likely than earlier models to act on instructions hidden in text you paste into your own message (Opus 5.5 card §6.5.1). The Fable 5.2 card reports the same behavior at a lower rate for Claude Mythos 5.2, the model Fable 5.2 shares: 0.3 to 0.5% of attempts in a coding test, and 0 to 0.3% with the product mitigations in place (Fable 5.2 card p. 133). In both cards' tests, the same text arriving through a tool, such as a file read, was never acted on (0 of 105). Claude Code marks large pastes for the model only in sessions that fetch feature flags; sessions with telemetry disabled, Claude apps gateway sessions, and most third-party-provider sessions do not fetch them ([pasted text](https://code.claude.com/docs/en/terminal-config#how-claude-treats-pasted-text)).
>
> The full academic pipeline (10 stages) consumes a **large amount of tokens** — a single end-to-end run can exceed 200K input + 100K output tokens depending on paper length and revision rounds. Budget accordingly.
>
> Individual skills (e.g., `deep-research` alone, or `academic-paper-reviewer` alone) consume significantly less.

## Estimated token usage by mode

| Skill / Mode | Input Tokens | Output Tokens | Estimated Cost |
|---|---|---|---|
| `deep-research` socratic | ~30K | ~15K | ~$0.60 |
| `deep-research` full | ~60K | ~30K | ~$1.20 |
| `deep-research` systematic-review | ~100K | ~50K | ~$2.00 |
| `academic-paper` plan | ~40K | ~20K | ~$0.80 |
| `academic-paper` full | ~80K | ~50K | ~$1.80 |
| `academic-paper-reviewer` full | ~50K | ~30K | ~$1.10 |
| `academic-paper-reviewer` quick | ~15K | ~8K | ~$0.30 |
| **Full pipeline (10 stages)** | **~200K+** | **~100K+** | **~$4-6** |
| + Cross-model verification | +~10K (external) | +~5K (external) | +~$0.60-1.10 |

*Estimates based on a ~15,000-word paper with ~60 references. Actual usage varies with paper length, revision rounds, and dialogue depth. Costs measured on Opus 4.x at Anthropic API pricing as of April 2026 — treat as order-of-magnitude anchors under newer models rather than exact quotes.*

> **2026-11 list-price re-derivation.** At 2026-11 list prices, the full-pipeline token figures above (~200K in + ~100K out) come to roughly **~$5.60** per run on Claude Fable 5.2 (US$8 / US$40 per million input / output tokens, with cache reads at US$0.20 per million; Fable 5.2 system card p. 240), **~$7** on Claude Fable 5.1 (US$10 / US$50; 2026-09 list price, not re-checked), and **~$2.80** on Claude Opus 5.5 (US$4 / US$20, with cache reads at US$0.20 per million; Opus 5.5 system card p. 180), before any cache discount. This is arithmetic on the token columns, not a re-measurement: no pipeline run has been re-timed on any of the three models. All three always reason (thinking cannot be disabled), so dialogue-heavy modes may spend more output tokens than the Opus 4.x rows recorded, and a higher effort level spends more still.

> **v3.11 citation verification (#182).** The deterministic citation-existence gate calls external bibliographic APIs (Semantic Scholar / OpenAlex / Crossref / arXiv), not the LLM, so it adds **no Claude token cost** to the figures above — only network latency on first lookup. The persistent SQLite cache (`~/.cache/ars/verification.db`, 90-day TTL) means each paper is verified once and reused across drafts; a re-run over an already-cached bibliography does no network work. See [SETUP](SETUP.md#citation-verification-cache-v3.11-182).

## Recommended Claude Code settings

| Setting | What it does | How to enable | Docs |
|---|---|---|---|
| **Agent Team** (optional) | Enables `TeamCreate` / `SendMessage` tools for manual multi-agent coordination. **ARS's internal parallelization does not require this flag** — skills spawn subagents via the built-in `Agent` tool directly. Only useful if you want to manually orchestrate persistent team workflows across sessions. | Set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (research preview) | Experimental feature — no stable docs yet |
| **Auto mode** (recommended) | Auto-accepts most tool actions so long pipeline runs keep moving, while a server-side classifier still blocks actions that escalate beyond what you asked for (e.g. production deploys, force-pushes or direct pushes to main, data exfiltration). Explicit ask rules and classifier blocks can still prompt. The middle ground between manual approval and zero checks. | Launch with `claude --permission-mode auto` (when available), or set `"permissions": { "defaultMode": "auto" }` in `~/.claude/settings.json`; verify the active mode after startup (research preview) | [Permission modes](https://code.claude.com/docs/en/permission-modes) |
| **Skip Permissions** | Skips routine tool-use confirmations with no safety checks. Faster than auto mode but removes all guardrails. Intended for ephemeral isolated sandboxes without internet access, not real development machines. | Launch with `claude --dangerously-skip-permissions` (equivalent to `--permission-mode bypassPermissions`) | [Permission modes](https://code.claude.com/docs/en/permission-modes) |

> **⚠️ Choosing a mode**: For most unattended pipeline runs, auto mode is the recommended setting. It keeps most long runs moving while a classifier gates dangerous escalations, though ask rules and classifier blocks can still prompt. Auto mode is a research preview: it does not guarantee safety and is not a replacement for human review on sensitive operations, and its behavior may change. Skip Permissions removes that safety net entirely and should only be used in an isolated sandbox without internet access, where you are comfortable with Claude executing file reads, writes, and shell commands with no checks.

### v3.7.0 Plugin agents and model routing

When ARS is installed as a Claude Code plugin (`/plugin install academic-research-skills`), three downstream worker agents are exposed as plugin-shipped subagents: `synthesis-agent`, `research-architect-agent`, and `report-compiler-agent` (underscore names before #1037). Each declares `model: inherit` in its frontmatter, which means they run under the **dispatching session's model** rather than a pinned floor:

- An Opus session running the full pipeline gets Opus agents, preserving the integrative depth those agents were designed for.
- A Sonnet session gets Sonnet agents, matching the cost/latency profile of the parent run.
- The agents never silently fall back to Haiku — `inherit` resolves through the parent session's model, which is itself gated by the project policy of "no Haiku for ARS runs."

Since #514 (shipped in #521), each of the three also carries a pinned tools allowlist in the same frontmatter — `tools: Read, Write, Edit, Grep, Glob`, no shell and no network fetch — so dispatch-time capability is least-privilege; the exact value is CI-locked by `scripts/check_tools_allowlist.py` (#524).

This means **plugin-agent token costs track the per-mode estimates above unchanged** (with `ARS_MODEL_TIERING` unset); there is no separate plugin agent surcharge or discount, because dispatched agents inherit the same model the parent run already pays for. Under `ARS_MODEL_TIERING=economy`, plugin-exposed execution-type agents (e.g. `report_compiler_agent`) follow the tiering rule instead — one tier below the session model, floor Opus-class (see `shared/model_tiering.md`). If you change the main session model mid-pipeline (e.g., downshift to Sonnet for a long revision pass), the next agent dispatch picks up the new floor automatically.

Other ARS agents (`bibliography_agent`, `literature_strategist_agent`, etc.) are not plugin-exposed in v3.7.0; they remain in-skill prompt templates that the main session executes inline, with no separate model routing layer **by default**. The opt-in `ARS_MODEL_TIERING` switch (#517) adds a dispatch-time routing rule on top: when a tiering direction applies to a role, the session dispatches it as a subagent pinned to the target tier (inline roles included — dispatch-as-subagent is the mechanism); with the flag unset, this paragraph describes behavior unchanged. See `shared/model_tiering.md`. Wider plugin-agent coverage is deferred to a future release.

**Tiering with the Fable models and Opus 5.5 (2026-11).** The tier ladder puts the Fable models above Opus 5.5 because that is the vendor's lineup order, not because a Fable model scores higher on every task (see the model note at the top of this page). On an Opus 5.5 session, `quality-boost` sends the checkpoint calls to the frontier tier. Where the runtime resolves that tier to Fable 5.2, the calls cost 2 times the Opus 5.5 per-token list price (2.5 times where it resolves to Fable 5.1), for a benefit ARS has not measured; raising the session effort is the cheaper first step. On a Fable 5.2 or Fable 5.1 session, `economy` sends execution-type agents to the Opus class, which Claude Code resolves to Opus 5.5 on the Anthropic API (some providers resolve the `opus` alias to an older Opus model); the quality cost of that trade is also unmeasured on ARS. In both directions, a subagent dispatched on another model does not carry the effort level you chose for the session; it starts at that model's own level ([effort of subagents](https://code.claude.com/docs/en/model-config#effort-level-of-subagents-and-teammates)).

## Long-running session management

The full academic pipeline is designed for human-in-the-loop execution, with mandatory user confirmation at every stage. In practice, a full run often spans hours to days — longer than Anthropic's prompt cache TTL (5 minutes). Two consequences:

1. **Cache misses between checkpoints are normal.** When a stage checkpoint pauses longer than 5 minutes, the next stage reads its context uncached. This is an unavoidable cost of human-paced pipelines.
2. **Cross-session resume relies on Material Passport.** ARS does not maintain its own orchestrator state between sessions. To resume in a new session, paste your Material Passport YAML back; the orchestrator reads `compliance_history[]` and stage completion markers to locate your breakpoint.

### v3.6.2 Sprint Contract reviewer cost (always-on for `full` / `methodology-focus`)

The Schema 13 sprint contract gate splits each reviewer agent's run into Phase 1 (paper-content-blind, commits scoring plan) + Phase 2 (paper-visible review). For modes that ship templates (`full` panel 5 + `methodology-focus` panel 2), each reviewer therefore costs roughly two LLM turns instead of one. Reserved modes (`re-review` / `calibration` / `guided` / `quick`) keep pre-v3.6.2 behaviour.

| Skill / Mode | Effect on tokens | Notes |
|---|---|---|
| `academic-paper-reviewer full` | ~+30-40% input + small output bump per reviewer × 5 reviewers | Each reviewer reads the contract template + paper metadata in Phase 1, then full paper in Phase 2 |
| `academic-paper-reviewer methodology-focus` | Same shape, panel 2 | Two reviewers (Journal-Fit Reviewer + methodology) each run two phases |
| Synthesizer (always one) | +~2-3K input | Reads contract + reviewer outputs to run three-step mechanical protocol |

Empirical measurement pending real review runs at scale. The two-phase shape is non-optional for the gated modes; treat as fixed overhead, not a tunable.

### v3.4.0 compliance agent cost

Adding the mode-aware `compliance_agent` to Stage 2.5 and Stage 4.5 increases full-pipeline SR tokens by approximately:

| Skill / Mode | Input Tokens | Output Tokens | Estimated Cost |
|---|---|---|---|
| `deep-research systematic-review` (2.5 only) | +~5–8K | +~3–5K | +~$0.15 |
| Full pipeline SR (2.5 + 4.5) | +~10–15K | +~5–8K | +~$0.30 |
| `academic-paper full` (pre-finalize) | +~3–5K | +~2–3K | +~$0.08 |

These are on top of the existing per-skill costs in the table above (same 15,000-word / 60-reference basis; see footnote on line 23). Cross-model verification costs (if enabled) are unchanged.

### v3.6.3 Passport reset boundary (opt-in)

When `ARS_PASSPORT_RESET=1` is set, every FULL and MANDATORY checkpoint becomes a context-reset boundary. The intended workflow is:

1. Run a stage to FULL checkpoint in session A.
2. Copy the `[PASSPORT-RESET: hash=<hash>, stage=<completed>, next=<next>]` tag from the checkpoint notification.
3. Start a fresh Claude Code session (session B) and paste `resume_from_passport=<hash>`. Optional overrides: `resume_from_passport=<hash> stage=<n> mode=<m>`.
4. Session B loads only the passport ledger; no replay of session A's turns. The orchestrator locates the matching `kind: boundary` entry, appends a `kind: resume` entry to consume it, and continues. The resumed stage is determined by: a `stage=` CLI override if supplied, else the matched option's `next_stage` when the boundary carries a `pending_decision` (the orchestrator re-prompts the user first), else the recorded `next` field. `next` MAY be `null` when all decision branches terminate.

**When reset beats continuation:**

- Long pipelines where session A has accumulated >100K input tokens of context that the next stage does not actually need.
- `systematic-review` mode runs where stage independence is cleanly defined by the Material Passport.
- Any case where you hit the 5-minute prompt-cache TTL mid-pipeline; a reset lets the next stage start fresh instead of paying a cache miss on a bloated context.

**When continuation still wins:**

- Short pipelines (< 30K input tokens end-to-end).
- Stages with implicit in-session state that the passport does not capture (e.g., a Socratic dialogue branch the user wants to keep warm).
- When the flag is OFF, continuation is the unchanged pre-v3.6.3 default.

**Passport file location convention:**

By default, the orchestrator looks for the passport file in `./passports/<slug>/` or matching `./material_passport*.yaml` relative to the current working directory. Resolving the hash to a passport file on disk is the integrator's responsibility; the orchestrator loads whichever passport the enclosing tool provides. See §"Passport file location convention" above for the `./passports/<slug>/` default.

The resume command only defines the hash and optional stage/mode overrides:

```
resume_from_passport=<hash> [stage=<n>] [mode=<m>]
```

There is no path syntax on the resume command itself. Custom passport locations are configured in the project's `CLAUDE.md` or handled by the integrator's tooling before the orchestrator is invoked.

**Empirical token savings:** measurement pending a real `systematic-review` run with instrumentation. This section will be updated with observed token deltas once available; until then, no numeric claim is made. See [`../academic-pipeline/references/passport_as_reset_boundary.md`](../academic-pipeline/references/passport_as_reset_boundary.md) for the full protocol.

## Literature corpus ingestion (v3.6.4+)

The Material Passport `literature_corpus[]` field is populated by user-written adapters, not ARS itself. Three reference adapters ship with v3.6.4: `scripts/adapters/folder_scan.py`, `scripts/adapters/zotero.py`, `scripts/adapters/obsidian.py`. See [`scripts/adapters/README.md`](../scripts/adapters/README.md) for how to run them and how to write your own.

### Performance posture

- Adapters run out-of-band (before an ARS session, not during). Their runtime is the user's problem, not ARS's.
- Adapters must be deterministic: re-running on identical input produces byte-identical output modulo timestamps.
- `literature_corpus[]` entries are sorted by `citation_key`; rejections are sorted by `source`.
- Adapter output size grows linearly with corpus size. A 500-entry Zotero library typically produces a passport of ~300 KB YAML. ARS consumers should lazy-load when the corpus is large.

### Ingestion-layer boundaries

- Does not ingest PDFs, extract text, or run OCR.
- Does not call the Zotero Web API, Notion API, or any live service.
- Does not fetch paywalled content or use user credentials to access institutional libraries.

These boundaries are deliberate and reflect the ARS data-layer decision: ARS is a writing/review-layer framework; corpus integration stays in user-owned code. Users who want API-based live-sync adapters are expected to write them themselves, using the three reference adapters as starting points.

### Consumer-side integration

As of v3.6.5, two Phase 1 literature agents read `literature_corpus[]` via the **corpus-first, search-fills-gap** flow: `deep-research/agents/bibliography_agent.md` and `academic-paper/agents/literature_strategist_agent.md`. Both consumers follow the same five-step shared flow and four Iron Rules (Same criteria / No silent skip / No corpus mutation / Graceful fallback on parse failure). Search Strategy reports gain a PRE-SCREENED reproducibility block that enumerates included / excluded / skipped corpus entries with F3 zero-hit and F4 provenance reporting. Consumer integration is presence-based — auto-engages when the passport carries a non-empty `literature_corpus[]` and parses cleanly; parse failures fall back to external-DB-only flow with a `[CORPUS PARSE FAILURE]` surface.

See [`academic-pipeline/references/literature_corpus_consumers.md`](../academic-pipeline/references/literature_corpus_consumers.md) for the full consumer protocol. `citation_compliance_agent` corpus integration is deferred (target version TBD post-v3.8).

### v3.6.5 corpus consumer cost (presence-gated)

When the Material Passport carries a non-empty `literature_corpus[]`, Phase 1 reads scale with corpus size. The PRE-SCREENED block emit itself is prompt-layer (effectively free); the LLM cost is Step 1 pre-screening — applying the current Inclusion / Exclusion criteria to each corpus entry's `title` (always present) and any populated optional fields (`abstract` / `tags`).

| Corpus size | Step 1 pre-screening (per consumer) | Notes |
|---|---|---|
| Empty / absent | 0 | External-DB-only flow runs unchanged |
| ~50 entries (typical Zotero subset) | +~3-5K input + ~1-2K output | Title + abstract scan |
| ~200 entries | +~10-15K input + ~3-5K output | Title-only scan dominates; abstract scan only when populated |
| ~500 entries (large library) | +~25-40K input + ~8-12K output | Consider trimming the corpus before passport emit |

Step 2 search-fills-gap reduces external-DB cost when `uncovered_topics` is small (case A), which can offset Step 1 cost. Empirical net delta pending real systematic-review run instrumentation; until then, no aggregate numeric claim is made. Parse failures cost roughly one short turn (parse + emit `[CORPUS PARSE FAILURE]` + fall back).
