# Sprint Contract Protocol (v3.6.2)

> Authoritative orchestration reference for the ARS v3.6.2 sprint-contract hard gate.
> Schema: `shared/sprint_contract.schema.json` (Schema 13.2).
> Templates: `shared/contracts/reviewer/*.json`.
> Design spec: `docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md`.
> Canonical inline prompt source: `references/reviewer_sprint_prompt_source.md`.
> Its rendered fragments remain in the five reviewer agents and synthesizer because
> the dispatcher sends those prompt sections verbatim; `scripts/check_reviewer_sprint_prompt_sync.py`
> enforces byte-exact mirrors plus an explicit content-hash re-pin.
>
> **v3.6.6 cross-reference**: this reviewer protocol is byte-equivalent across v3.6.2 → v3.6.6 (zero-touch promise per §3.6 of `docs/design/2026-04-27-ars-v3.6.6-generator-evaluator-contract-design.md`). The v3.6.6 release adds a parallel generator-evaluator protocol inside `academic-paper` for the in-pair writer / evaluator pair (see `academic-paper/SKILL.md` § "v3.6.6 Generator-Evaluator Contract Protocol" and design doc §5).

## 1. Overview

A reviewer sprint contract is a machine-checkable pre-registered acceptance criterion. The orchestrator loads a frozen template, inlines runtime fields (`generated_at`, optional `agent_amendments`), and drives each reviewer through a paper-content-blind Phase 1 followed by a paper-visible Phase 2. The synthesizer then runs a three-step mechanical protocol over the `panel_size` reviewer outputs to emit an editorial decision.

This protocol exists to destroy the "read the paper, then rationalise the scoring standard" drift path. The load-bearing mechanism is the **physical separation of calls**: Phase 1 never sees paper content.

## 2. Two-phase reviewer call

For each role-separated review seat in `range(panel_size)`, using a fresh invocation context and withholding peer outputs until the seat commits. These are execution requirements whose actual status must be recorded in `review-panel-provenance/1.0`; they do not establish independent error processes:

1. **Prepare contract.** Load template from `shared/contracts/<domain>/<mode>.json`. Populate `generated_at` (ISO-8601 UTC). Optionally populate `agent_amendments` (field-specific notes from `field_analyst_agent`). Run `check_sprint_contract.py` on the in-memory object; abort on error.
2. **Phase 1 call (paper-content-blind).**
   - System prompt: the `### Phase 1 — Paper-content-blind pre-commitment` sub-section of the reviewer agent's `## v3.6.2 Sprint Contract Protocol` block.
   - User content: contract JSON + paper metadata ONLY (`title`, `field`, `word_count`).
   - Expected output: `## Contract Paraphrase`, `## Scoring Plan`, terminal `[CONTRACT-ACKNOWLEDGED]` tag.
3. **Phase 1 output lint.** See §4 below.
4. **Phase 2 call (paper-visible).**
   - System prompt: the `### Phase 2 — Paper-visible review` sub-section of the same `## v3.6.2 Sprint Contract Protocol` block.
   - User content: contract JSON (re-injected) + Phase 1 output wrapped in `<phase1_output>...</phase1_output>` data delimiter + full paper wrapped in `<paper_content>...</paper_content>` data delimiter (#574 A6 — the manuscript is author-supplied untrusted material; the reviewer prompts carry the matching data-not-instructions rule).
   - Expected output: optional `## Scoring Plan Dissent`, `## Dimension Scores`, `## Review Body`. Per-seat `## Failure Condition Checks` and `## Editorial Decision` are retired in v2 and fail loudly if present.
5. **Phase 2 output lint.** Run `scripts/check_phase_conformance.py --contract <C> --role <dispatch-role> --phase1 <P1> --phase2 <P2> --manuscript <paper> --metadata <metadata.json>` before synthesis. Exit 3 emits `[PROTOCOL-VIOLATION: phase_conformance=<check>]` and makes the seat unusable; exit 2 is an infra abort. See §5.
6. **Panel cardinality invariant.** After all reviewers complete, verify `len(usable_phase2_outputs) == panel_size`. If any reviewer was dropped, emit `[PANEL-SHRUNK]` and abort the round (see §6).
7. Feed usable Phase 2 outputs into synthesizer (see §7).

The Schema 6 adapter preserves the sprint vocabulary exactly: each contract
dimension becomes one `criterion_judgements` row with
`judgement_scale: sprint_contract` and the unchanged
`block|warn|pass|not_assessed` value. It never maps sprint labels to the
narrative rubric. Package calibration remains `NOT_CALIBRATED`; a seat card
does not need a second calibration field inside the pinned sprint grammar.

## 3. Contract injection

- **Template on disk is frozen.** Do not mutate. Deep-copy into an in-memory dict.
- **Runtime-only fields:** `generated_at`, `agent_amendments.stage_specific_notes`, `agent_amendments.additional_measurement_hints`.
- **Baseline fields are orchestrator-immutable.** Schema cannot enforce this; the orchestrator must not rewrite `acceptance_dimensions` (including `eligible_roles` and `owner_role`) / `failure_conditions` / `measurement_procedure` / `override_ladder` / `mode` / `stage` / `contract_id` / `baseline_version` / `panel_size` between template load and injection. Optional: emit sha256 of baseline-field subset to audit log for drift detection.
- **v1 contracts fail loudly.** A reviewer contract without role-scoped dimensions, the five-field scoring-plan schema, and the four-token decision enum is `[CONTRACT-INVALID]`. Migrate it to v2; do not silently reinterpret it.

## 4. Phase 1 output lint

Structural checks (orchestrator, not validator). On failure retry Phase 1 once with the specific lint gap hinted in the system prompt; second failure aborts that reviewer.

Run these as `scripts/check_phase_conformance.py --contract <C> --role <dispatch-role> --phase1 <P1> --phase1-only --manuscript <paper> --metadata <metadata.json>`, the Phase-1 counterpart of §8.1's `--layer1-only`: the retry decision is taken while Phase 2 has not been requested yet, so the gate has to be answerable on Phase 1 alone. Exit codes carry the same §11 meanings — exit 3 is the reviewer-conformance failure that the one permitted retry addresses, and every exit-2 class aborts the round without a retry.

- Required sections in order: `## Contract Paraphrase`, `## Scoring Plan`, terminal `[CONTRACT-ACKNOWLEDGED]`.
- Paraphrase paragraph count ≥ `measurement_procedure.paraphrase_minimum_dimensions` (for `"all"`, one paragraph per dimension; for integer `k`, at least `k` paragraphs each matching a distinct dimension).
- `## Scoring Plan` has one `### <Dn>: <name>` subsection per dimension whose `eligible_roles` includes this dispatch role, and none for ineligible dimensions.
- Every subsection uses the pinned, unbulleted line grammar exactly once: `dimension_id:`, `what_to_look_for:`, `what_triggers_block:`, `what_triggers_warn:`; a mandatory dimension also requires `what_triggers_fatal:`, which is forbidden on non-mandatory dimensions. Copy each dimension ID and name exactly from the contract. For a non-mandatory dimension, omit the entire `what_triggers_fatal:` line; never emit that key with `NOT_APPLICABLE`, `none`, or another sentinel. The block/warn/fatal trigger strings are pairwise distinct.
- In a #684 criteria-aware call, Phase 1 also receives the pointer-only manifest,
  Target Criteria Brief, and exact role marker. After Scoring Plan it emits one
  `criteria_parallel_conflicts:` line and reproduces the marker byte-for-byte;
  this is a pointer commitment, not manuscript applicability. An unbound call
  instead emits exactly `criteria_binding_unavailable` and makes no venue-fit
  claim. Neither form adds an H2 or copies criterion prose.
- `check_phase_conformance.py` searches every 12-word full-manuscript shingle against Phase 1 after whitespace normalization and case-folding. A hit fails unless it also occurs in the actual metadata-envelope values or the contract JSON. `--manuscript` and `--metadata` are mandatory, so this family cannot be skipped.

Terminal Phase 1 structural preflight (mandatory). Silently inspect the exact text you are about to send:
1. The only H2 sections are exactly one `## Contract Paraphrase` followed by exactly one `## Scoring Plan`. The paraphrase meets `measurement_procedure.paraphrase_minimum_dimensions`: `"all"` means one paragraph per contract dimension; integer `k` means at least `k` paragraphs tied to distinct dimensions.
2. Every `### <Dn>: <name>` heading copies the contract ID and name exactly, and only dimensions eligible for your dispatch role appear.
3. Each scoring-plan subsection contains exactly one unbulleted `dimension_id:`, `what_to_look_for:`, `what_triggers_block:`, and `what_triggers_warn:` line; its block and warn texts are distinct.
4. In every non-mandatory subsection, the literal key `what_triggers_fatal:` occurs zero times; delete the entire line and any sentinel if it appears. In every mandatory subsection, that key occurs exactly once and its text is distinct from block and warn.
5. No `## Dimension Scores`, `## Review Body`, `## Failure Condition Checks`, `## Editorial Decision`, `dimension_scores`, `review_body`, or bare `editorial_decision=` appears, and no manuscript-specific claim appears.
6. Binding: a criteria-aware call contains exactly the supplied marker and one
   `criteria_parallel_conflicts:` line matching the brief; an unbound call
   contains exactly `criteria_binding_unavailable`. Neither form states
   manuscript applicability.
7. The final nonblank output line is exactly `[CONTRACT-ACKNOWLEDGED]`.
Do not send until every check holds.

**Lint is structural, not semantic.** A reviewer can in principle pass this lint by emitting generic boilerplate triggers — semantic judgement (whether triggers are concrete and discriminating) is deferred to a post-v3.6.2 judge-agent layer.

On second Phase 1 failure: emit `[PROTOCOL-VIOLATION: reviewer=<role>, contract=<id>, phase1_lint_failed=true]` and mark this reviewer unusable.

## 5. Phase 2 output lint

Structural checks run before handoff to synthesizer. **No Phase 2 retry** (reviewer has seen the paper; a second call is tainted) EXCEPT the multi-dissent case below.

- Required sections: `## Dimension Scores`, `## Review Body`. `## Failure Condition Checks` and `## Editorial Decision` are forbidden v1 grammar. `## Scoring Plan Dissent` is optional only when a dimension actually dissents; when there is no dissent, omit the whole section rather than emitting an empty or `none` placeholder.
- Each report declares its dispatch role exactly once on one `contract_role: <role>` line immediately before `## Dimension Scores`; never repeat that report-level line inside dimension subsections.
- `## Dimension Scores` has one `### <Dn>: <name>` subsection per contract dimension. Eligible roles use `block | warn | pass`, or `not_assessed` with `abstain_reason`; ineligible roles must use structural `not_assessed` without a reason. An ineligible real score is an out-of-role vote and fails.
- An eligible `warn`/`block` carries a quoted `trigger:` substring of the matching Phase-1 commitment. A mandatory block also carries `block_class: fatal|repairable`; fatal binds only to `what_triggers_fatal`, is forbidden on dissent, and non-mandatory dimensions never carry `block_class`.
- **Multi-dissent rule:** If `## Scoring Plan Dissent` names two or more `dimension_id` entries, orchestrator aborts this reviewer and retries from **Phase 1** once. If the retried Phase 1/2 also multi-dissents, mark the reviewer unusable (`[PROTOCOL-VIOLATION]`). One-dimension-per-reviewer-per-Phase-2-call is the cap.
- **Raw-HTML output grammar (#613/#682):** reviewer cards never contain raw HTML — comment markup, `<script>`/`<template>`, or any other tag; markup a seat needs to mention goes in inline code (`` `<!--` ``). Checker enforcement is span-scoped and code-aware inside `## Scoring Plan Dissent`: a bare `<!--` is read as opening an HTML comment wherever it appears — mid-line and lazy-continuation indents included — and a hidden field aborts as `[DISSENT-HIDDEN]`; any non-comment raw-HTML tag or delimiter outside inline code aborts as `[DISSENT-RAW-HTML]`, including malformed/incomplete openers and tags that hide no field. Neither channel can grant a trigger-binding exemption. Fenced examples and content outside the dissent span preserve their existing semantics; this is not a repository-wide HTML blacklist.
- **Anchor gate:** under `## Review Body`, each non-DA finding with a Severity occupies its own `### W<n>: <title>` subsection with exactly one Severity; every Critical/Major finding also carries its own valid typed Evidence Anchor, never shared with another finding. Strength subsections never carry a `Severity` field or a `Severity: Strength` sentinel. Every Evidence Anchor value begins with the literal `<type>: <locator>` grammar. An opening backtick or `[` immediately before `<type>` starts an outer wrapper and requires its matching closer; nothing may appear between the type and its colon, so `` `text`: §3 `` and `` `text` — §3 `` are both invalid. Wrapper-like characters inside a locator are content and must be locally balanced — a bracketed locator such as `equation: Eq. [3]` and a locator naming inline code such as ``text: §3 "quote" per `df``` are valid. A `text:` anchor contains one or more verbatim excerpts, each inside a balanced pair of straight or curly double quotes, and every quoted excerpt is at most 25 words. Before output, confirm at least one quoted excerpt exists, count each quoted excerpt in a `text:` anchor, and shorten any excerpt over 25 words; never place commentary inside the quotation. An `absence:` anchor uses the exact grammar `absence: <where> — expected <item>; checked <surfaces>`, including the literal single space after the semicolon and non-empty content for every placeholder. The reserved ` — expected ` and `; checked ` separator sequences each occur exactly once.
- The finding field labels may be unindented or Markdown-list-indented and may be separate or pipe-delimited; the complete typed anchor value, including its type and locator, may be bare, backtick-wrapped, or square-bracketed. These are presentation variants only. A Severity outside `## Review Body`, under a non-`W<n>` H3, or nested under H4 fails.
- **DA table gate:** the DA emits exactly one `#### CRITICAL` table and exactly one `#### MAJOR` table, both always present even when empty, with exact `#` and `Evidence Anchor` header columns. The CRITICAL table uses unique dense IDs `C1..Cn`; both tables use the shared parser and anchor checks. The two tables are the terminal suffix of `## Review Body`: every prose paragraph precedes `#### CRITICAL`; only blank lines may separate the end of CRITICAL from `#### MAJOR` or follow MAJOR to the end of Review Body. DA reports may not contain HTML comments.

Terminal Phase 2 structural preflight (mandatory). Silently inspect the exact text you are about to send against your supplied Phase 1:
1. Dissent: if your Phase 2 view differs on exactly one dimension, include `## Scoring Plan Dissent` with exactly one unbulleted `dimension_id: <Dn>` line and exactly one unbulleted `rationale: <nonempty explanation>` line. If it differs on two or more, abort with `[PROTOCOL-VIOLATION: multi_dissent=true]` instead of drafting a card. If none differs, delete the heading and every placeholder beneath it; `none`, `omitted`, and `not applicable` are never a dissent. No bare `<!--` or `-->` — nor any other raw HTML — anywhere in the card outside inline code.
2. Sections and role: emit exactly one `## Dimension Scores` followed by exactly one `## Review Body`. Put exactly one report-level `contract_role: <your dispatch role>` immediately before `## Dimension Scores` and nowhere else. Delete `## Failure Condition Checks`, `## Editorial Decision`, and every bare `editorial_decision=` line.
3. Dimensions and abstentions: emit every contract dimension exactly once with its exact ID/name. An eligible dimension uses `block`, `warn`, `pass`, or `not_assessed`; eligible `not_assessed` has exactly one non-empty `abstain_reason:`, while an ineligible dimension uses only `score: not_assessed` with no `abstain_reason:`. No other score carries `abstain_reason:`.
4. Trigger binding: for every `warn` or `block`, the quoted `trigger:` text is a character-for-character substring of the matching Phase 1 trigger kind for the same dimension. Never paraphrase it. `pass` and `not_assessed` have no `trigger:`.
5. Fatality: every mandatory `block` has exactly one `block_class:`; `fatal` binds to the Phase 1 fatal trigger, a dissented dimension cannot be fatal, and a non-mandatory dimension has no `block_class:`.
6. Finding grammar: apply the role-specific grammar above. For a scoring seat, every weakness is its own `### W<n>` subsection with exactly one parseable Severity, one typed Evidence Anchor, and one Confidence; every strength has a typed Evidence Anchor and no Severity. If either finding polarity is empty, include its required Coverage Receipt. For the DA, emit exactly one `#### CRITICAL` table and one `#### MAJOR` table, both present even when empty, with no standalone Severity. Each table header contains exactly one column named `#` and exactly one named `Evidence Anchor`; every row is outer-pipe-delimited with the header's column count, and CRITICAL IDs are unique and dense `C1..Cn`. For the DA, these tables are the terminal suffix of `## Review Body`: put every prose paragraph before `#### CRITICAL`; after the CRITICAL table emit only blank lines until `#### MAJOR`, and after the MAJOR table emit only blank lines to the end of Review Body. Do not emit HTML comments anywhere in a DA report.
7. Anchors: no findings share an anchor. Every anchor uses a valid typed `<type>: <locator>` value with balanced wrappers. Every `text:` anchor contains at least one balanced quoted verbatim excerpt, and each quoted excerpt is at most 25 words. Every `absence:` anchor uses the exact required separators and non-empty fields.
8. Bands: assign each weakness by its own decision impact, never by a target distribution or bundled cluster; a Critical is singleton rejection-level.
Do not send until every check holds.

On any Phase 2 lint failure other than multi-dissent: emit `[PROTOCOL-VIOLATION]` and mark reviewer unusable. Do not synthesise a substitute score for the synthesizer.

### 5.1 Methodology arithmetic-receipt gate (#610)

> **Epistemic status first**: this gate does not replace the human reviewer.
> `check_phase_conformance.py` verifies receipt AUDITABILITY only — required
> fields present, closed enums respected, mismatch↔weakness linkage intact.
> It never attests the arithmetic is correct; correctness is judged by human
> adjudication (`VERIFIED`/`CLAIM_ONLY`/`MISCOMPUTED`/`MISSED`, #610 spec
> §7.1), and a conforming receipt with wrong arithmetic is still wrong.

The methodology seat's Phase 2 card additionally carries exactly one
`## Arithmetic Receipts` H2 section as the final section of the card, after
`## Review Body` (no other seat may emit it; the heading is matched exactly
and case-sensitively, consistent with every other section grammar). The
section holds either dense `### AR1..ARn` receipt subsections —
one per attempted recomputation, canonical `key: value` machine lines per the
delivered Phase 2 grammar (canonical source: the `methodology-receipt`
fragment of the reviewer sprint prompt source cited in this file's header,
spliced by its sync checker) — or, when the
manuscript reports no statistic covered by a bounded procedure, exactly one
`no_recomputable_statistics: <basis>` attestation line. The attestation is a
mandatory declaration with adjudicated honesty, never machine-checked
triggering: the checker verifies only that the declaration exists and
annotates the passing card with the advisory
`[RECEIPT-ATTESTATION: declaration-only — applicability not machine-verified;
adjudication judges the attestation]`; whether the declaration is TRUE is
judged at adjudication, where a false attestation over recomputable
statistics surfaces as `MISSED` verdicts. Checker-enforced
highlights: closed `procedure_id` / `status` / `not_computable_reason` /
`tail_convention` enums; an unstated-tail p receipt claiming a verdict must
display BOTH labeled tail values, each label sharing its own `;`-segment
with its derived number (either order); a
GRIM/GRIMMER verdict requires
`rounding_interval:` + `nearest_achievable:`; an `n_from_df` verdict must name
its `df_identity:`; every `mismatch` links to a distinct `W<n>` weakness that
carries the matching `**Arithmetic Receipt**: AR<n>` back-reference (the
value exactly `AR<n>`, no trailing text). The receipt section is read
fence-transparently in display form: a fenced receipt line is still read
(an indented fence dedented as CommonMark renders it), the two tolerated
decorations are a single leading list marker and balanced bold around the
key, and any other decorated, table-cell, entity-encoded, or otherwise
re-spelled machine line — and any machine line outside every `### AR<n>`
subsection other than the attestation — aborts loudly instead of being
silently dropped or read as canonical. The section is a comment-free zone:
any unfenced HTML comment markup aborts, and in the Review Body a
back-reference hidden by a block, paragraph-inline, or indented-code
rendering context aborts rather than earning linkage credit. Failures
surface as `[RECEIPT-MISSING]` / `[RECEIPT-GRAMMAR]` / `[RECEIPT-TAILS]` /
`[RECEIPT-LINKAGE]` / `[RECEIPT-SECTION-FORBIDDEN]` at exit 3 — the seat is
unusable per §5, with no Phase 2 retry; the abort-rate cost of this new
mandatory grammar is a tracked #610 §7.1 reporting metric, not a silent
tradeoff. Procedure boundaries and the red-flag classification live in
`references/statistical_reporting_standards.md` §8.

### 5.2 Script-adapter dispatch (#610 step 5, optional orchestration)

An orchestrator that can execute repository scripts MAY dispatch the
methodology seat as three calls: Phase 1; a paper-visible **numeric
extraction** call (system prompt: the seat's `### Phase 2E` section, rendered
from the `methodology-extraction` fragment) whose entire response is one
`## Recompute Extraction` section of typed machine lines — one `### RR<n>`
per arithmetic claim, or the `no_recomputable_statistics:` attestation —
gated by `check_phase_conformance.py --extraction` with ONE structural retry
of the Phase 1 evidence class; then `scripts/recompute_receipts.py`, which
deterministically computes the full `## Arithmetic Receipts` section from
the extraction alone (never the manuscript); then Phase 2 with the computed
receipts injected as a `<computed_receipts>` block. Under injection the seat
must reproduce the receipts verbatim, adding only the `finding_ref:` linkage
lines on `mismatch` receipts; the `--injected-receipts` identity gate
(`[RECEIPT-IDENTITY]`, exit 3) fails the card on any other edit. A
calculator refusal of a gate-passed extraction is an orchestrator infra
fault (exit-2 class), never a seat conformance failure. Without a
`<computed_receipts>` block — every orchestrator that cannot run scripts,
including runtime-Bash-denied sessions — §5.1's self-compute behavior
applies unchanged; the two modes share one receipt grammar and one
adjudication scale, and extraction fidelity (whether the transcribed numbers
are the manuscript's) stays a human-adjudicated question exactly like the
attestation's truth.

## 6. Multi-reviewer orchestration

- **Independent cycles.** Each of the `panel_size` reviewers runs its own Phase 1 + Phase 2. Failures in one do not pause the others.
- **Panel cardinality invariant (§2 step 6).** After all reviewers complete, if `len(usable_phase2_outputs) < panel_size`, abort the editorial round with `[PANEL-SHRUNK]`. Do not silently recompute `cross_reviewer_quantifier` thresholds against a smaller panel — the contract's published aggregation semantics bind on a specific `panel_size`.
- **Operational monitor.** Track `[PANEL-SHRUNK]` rate in real SR runs. If > 5% of rounds abort in first 3 months, v3.6.3 introduces graceful-degradation fallback.

## 7. Reviewer panel mapping

| mode                          | panel_size | invoked reviewers |
|-------------------------------|------------|-------------------|
| `reviewer_full`               | 5          | Journal-Fit Reviewer (`eic`) + methodology + domain + perspective + DA |
| `reviewer_methodology_focus`  | 2          | Journal-Fit Reviewer (`eic`) + methodology (only) |
| `reviewer_re_review`          | —          | NOT a Schema 13 mode (#576 Spec B — removed from the enum): governed by the dedicated contract family `shared/contracts/re_review/` + `scripts/check_re_review_synthesis.py`; see `re_review_mode_protocol.md` § Three-Gate Orchestration |
| `reviewer_calibration`        | —          | not shipped in v3.6.2 |
| `reviewer_guided`             | —          | not shipped in v3.6.2 |

The orchestrator uses `mode` to determine the panel and the contract's `panel_size` as the invariant target. SC-11 validator check ensures mode and `panel_size` are consistent.

## 8. Synthesizer three-step protocol

**Step 1 — Build role-scoped scoring matrix.** For each dimension, gather only assessed values from reports whose `contract_role` is in that dimension's `eligible_roles`. Ineligible/abstained values are excluded from numerator and denominator. Zero assessed eligible seats emits `[DIMENSION-UNASSESSED: <Dn>]` and aborts. Emit a `dimension_verdicts:` audit line with the worst assessed score, using `block(fatal)` if any assessed eligible seat declared fatal.

**Step 2 — Evaluate each `failure_conditions[]`.** For each condition:

1. Parse `expression` against the recognised patterns (see §9 vocabulary). Unrecognised → emit `[EXPRESSION-UNRECOGNISED]`, abort synthesizer.
2. Apply `cross_reviewer_quantifier` separately per selected dimension over its assessed eligible seats: `any` ≥1; `all` = n; `majority` = `⌊n/2⌋+1` for n≥3, both for n=2, and the single owner itself for n=1. Then apply the expression's dimension quantifier. Patterns 1–5 now use this two-stage meaning; the retired per-seat multi-dimension predicate is not valid under role scoping.
3. Record `{condition_id, fired}`.

**Step 3 — Precedence and decision.** Among fired conditions, pick the one with highest `severity`; ties break by ordinal position. Emit exactly one `dimension_verdicts: [...]`, `fired_conditions: [...]`, `da_critical_adjudications: [...]`, and `editorial_decision=<accept|minor_revision|major_revision|reject>` line. DA adjudications are exact and total over the DA's CRITICAL IDs; each REJECTED ID has `C<n> rejection rationale: <nonempty>`. If decision is Accept with one or more VALIDATED/UNRESOLVED DA CRITICALs, also emit `[DA-CRITICAL-VS-ACCEPT: <n> validated/unresolved]`; the orchestrator escalates and does not finalize. The marker never changes the mechanical action.

**Forbidden operations (synthesizer prompt hard constraint):**
- Introduce aggregation rules not derivable from `cross_reviewer_quantifier` + `severity`.
- Average or vote-aggregate scores within a single dimension unless `cross_reviewer_quantifier: majority` explicitly requests it.
- Soften a fired condition's `action` on post-hoc grounds.
- Synthesise substitute scores for reviewers marked unusable — the round is either complete with `panel_size` usable outputs or `[PANEL-SHRUNK]` aborted.

## 8.1 Executable recomputation (#510)

After the synthesizer emits its output, the orchestrator runs
`scripts/check_panel_synthesis.py --contract <contract.json> --report <r1.md> ...
--report <rN.md> --roles <r1,...,rN> --synthesis <synthesis.md>` — a deterministic checker that
re-derives role-scoped panel arithmetic, checks dispatch-role binding, verifies
the emission audit lines, and enforces the DA terminal gate. Consequences by exit code:

- **Exit 1 (synthesis-layer failure)** — void this synthesis and re-run the
  synthesizer ONCE, appending the checker diagnostics wrapped in a data
  delimiter (`<checker_diagnostics>...</checker_diagnostics>`, treat-as-data)
  to the re-run input. ANY nonzero exit on the second attempt aborts the
  editorial round with `[SYNTHESIS-MISMATCH]`.
- **Exit 2 (contract/infra failure)** — abort the round, no retry.
- **Exit 3 (reviewer-report failure)** — that reviewer is unusable per §5 ⇒
  `[PANEL-SHRUNK]` abort; no synthesizer re-run. The orchestrator MAY catch
  this earlier by running `--layer1-only` per reviewer at Phase-2 lint time;
  this parses v2 score grammar but does not replace `check_phase_conformance.py`.

Reviewer reports must satisfy the pinned output grammar in each reviewer
agent's delivered Phase 2 section; the checker parses that grammar and nothing looser.

## 9. Recognised expression vocabulary

Synthesizer recognises the following patterns (with accepted natural-English variants):

1. **Priority-scoped single-match:** `any <priority> dimension scores '<score>'` | `any dimension with priority=<priority> scores '<score>'` | `any <priority>-priority dimension scores '<score>'`
2. **Priority-scoped count-based:** `two or more <priority> dimensions score '<score>' or worse` | `two or more dimensions with priority=<priority> score '<score>' or worse` (ordering `pass` < `warn` < `block`)
3. **Universal over priority:** `every <priority> dimension scores '<score>'`
4. **Single-dimension literal:** `<Dn> scores '<score>'`
5. **Conjunction:** any of the above joined by `AND`
6. **Fatal block:** `any <priority> dimension has a fatal block` | `<Dn> has a fatal block` (mandatory scope only)
7. **Unscoped threshold:** `any dimension scores '<score>' or worse`
8. **Dimension threshold:** `<Dn> scores '<score>' or worse`
9. **Unscoped universal:** `every dimension scores '<score>'`

Shipped template coverage:
- `reviewer/full.json`: F1 pattern 6, F2 pattern 1, F3 pattern 2, F4 pattern 1, F5 pattern 7, F0 pattern 9.
- `reviewer/methodology_focus.json`: F1 pattern 6, F2/F3 pattern 4, F4 pattern 8, F0 pattern 9.

New expression forms require a PR updating this §9, the synthesizer prompt's recognised-pattern list, and the `scripts/check_panel_synthesis.py` expression grammar in lockstep.

## 10. Token cost expectations

Reviewer total calls = `2 × panel_size`. For `reviewer_full` that is 5 → 10 calls; for `reviewer_methodology_focus` 2 → 4. Phase 1 input is small (contract + metadata only); Phase 1 output is short (paraphrase + scoring_plan). Real token bound is well below 2x raw increase.

## 11. Failure modes and diagnostics

Audit-log tags the orchestrator may emit:

| Tag | When | Action |
|-----|------|--------|
| `[CONTRACT-ACKNOWLEDGED]` | normal Phase 1 completion | none (expected) |
| `[PROTOCOL-VIOLATION: phase1_lint_failed=true]` | Phase 1 lint fails twice for a reviewer | mark reviewer unusable |
| `[PROTOCOL-VIOLATION: phase2_lint_failed=<check>]` | Phase 2 lint fails (non multi-dissent) | mark reviewer unusable |
| `[PROTOCOL-VIOLATION: multi_dissent=true]` | Phase 2 has ≥ 2 dissent entries, retry exhausted | mark reviewer unusable |
| `[PANEL-SHRUNK: usable=<k>, panel_size=<N>]` | §6 invariant failed | abort editorial round |
| `[EXPRESSION-UNRECOGNISED: condition_id=<F>, expression=<...>]` | synthesizer step 2.1 | abort synthesizer |
| `[PANEL-SYNTHESIS-MISMATCH: recomputed=..., stated=...]` | checker (§8.1) exit 1 | void synthesis, retry once |
| `[SYNTHESIS-MISMATCH]` | second checker failure after retry | abort editorial round |
| `[REVIEWER-SELF-INCONSISTENT: reviewer=..., ...]` | checker Layer 1 (exit 3) | mark reviewer unusable |
| `[PANEL-CARDINALITY: ...]` | checker cardinality/role guard (exit 2) | abort editorial round |
| `[REPORT-PARSE: <path>: ...]` | checker report-grammar failure (exit 3) | mark reviewer unusable |
| `[RECEIPT-MISSING/-GRAMMAR/-TAILS/-LINKAGE: <path>: ...]` | #610 methodology arithmetic-receipt gate failure (exit 3, §5.1) | mark reviewer unusable |
| `[RECEIPT-SECTION-FORBIDDEN: <path>: ...]` | a non-methodology seat emitted `## Arithmetic Receipts` (exit 3, §5.1) | mark reviewer unusable |
| `[RECEIPT-ATTESTATION: declaration-only — ...]` | #610 attestation-path advisory on a PASSING methodology card (§5.1) | none — advisory; adjudication judges the attestation |
| `[SYNTHESIS-PARSE: <path>: ...]` | checker synthesis-grammar failure (exit 1) | void synthesis, retry once |
| `[CONTRACT-INVALID/-INELIGIBLE: ...]` | checker contract validation failure (exit 2) | abort editorial round |
| `[IO-ERROR: <path>: ...]` | checker file read/encoding failure (exit 2) | abort editorial round |
