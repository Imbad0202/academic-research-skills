# #684 review-criteria consumer binding and constructive-value specification

## Decision

#684 consumes the `ReviewTargetContext` produced by #683. It does not add a
second target resolver, copy registry prose into agent prompts, or allow a
reviewer to infer a target from manuscript quality.

One append-only `ReviewCriteriaBindingManifest` is the authority for a target
review. It binds the exact context and registry bytes, the context's
`resolved_digest`, and its selected criterion pointers. Exactly three consumer
classes record receipts against that authority:

1. `formative_planning` — the academic-paper planning/writing surface;
2. `internal_evaluator` — academic-paper Phase 6; and
3. `external_panel` — the standalone review panel, including `EIC`, `R1`,
   `R2`, `R3`, and `DA`.

Each receipt repeats only pointer metadata needed for mechanical equality and
the hashes of the consumer artifacts. Criterion statements remain in the named
registry and are hydrated at dispatch time through the #683 Target Criteria
Brief. A receipt or finding sidecar containing copied criterion prose is
invalid.

## Artifacts

- `shared/contracts/review_target/review_criteria_binding_manifest.schema.json`
  — the closed binding authority and three receipt shapes.
- `shared/contracts/review_target/constructive_review_findings.schema.json` —
  the closed Critical/Major finding sidecar.
- `shared/references/review_criteria_consumer_protocol.md` — producer,
  consumer, blind-safety, profile-change, and rendering rules.
- `scripts/review_criteria_binding.py` — stdlib-only manifest builder,
  receipt recorder, validator, marker renderer, and finding validator.
- `evals/heldout/review_criteria_constructive_value/` — preregistered
  paired evaluation assets. Live subject/judge dispatch is manual and is never
  a CI action.

## Binding authority

`init` reads only explicitly named context and registry paths. It recomputes
the #683 resolution from the context's declaration and the registry and
requires byte-for-byte semantic equality with the supplied context. The
manifest records:

- caller-supplied `target_review_id`;
- portable context and registry references plus raw SHA-256 hashes;
- `resolved_digest`;
- ordered `selected_criterion_ids` and exact id/version/content-digest
  pointers;
- unresolved rows and parallel conflict groups by pointer; and
- optional predecessor identity.

The manifest never stores criterion title, statement, source title, or other
prose. A raw context/registry hash mismatch, a recomputation mismatch, or a
closed-schema violation fails before any manifest is written.

## Profile changes and comparability

When `--prior-manifest` is supplied:

- the same `target_review_id` requires the same context and registry authority;
  a changed digest, selected pointer, or authority hash is a conflict;
- a changed context requires a new `target_review_id`; and
- a new target review records the predecessor id and digest but does not claim
  comparability.

Callers must pass the active prior manifest when one exists. The tool does not
scan the workspace for ambient state. A missing prior therefore means “no
predecessor asserted”, never “the profile is unchanged”.

## Receipt contract

Each consumer output contains the exact rendered marker:

```text
[REVIEW-TARGET-BINDING v1]
target_review_id=<id>
consumer_id=<consumer>
role=<role>
context_ref=<portable path>
context_sha256=<raw sha256>
resolved_digest=<resolved digest>
selected_criterion_ids=<canonical compact JSON array>
[/REVIEW-TARGET-BINDING]
```

`record` verifies the marker and exact canonical `criteria_parallel_conflicts:`
line against the manifest, hashes the explicit artifact path, and appends a
receipt atomically. The role sets are closed:

- `formative_planning`: `FORMATIVE`;
- `internal_evaluator`: `INTERNAL`; and
- `external_panel`: `EIC`, `R1`, `R2`, `R3`, `DA`.

The internal receipt hashes the paper-blind Phase 6a pre-commitment artifact;
Phase 6b repeats the marker for continuity but is not substituted as the blind
witness.

An identical retry is idempotent and performs no write. A second receipt for
the same consumer with different artifact bytes is a conflict. `validate
--require-complete` requires all three consumer receipts and every external
seat.

## Blind-safe sequencing

The external panel and internal evaluator retain their existing two-call
discipline.

- Phase 1 receives the sprint contract, author-confirmed target metadata, the
  pointer-only context, and the Target Criteria Brief. It receives no
  manuscript, abstract, score, finding, or reviewer output.
- Phase 1 commits criterion ids and separate treatment of every declared
  `parallel_conflicts[]` group. It never decides manuscript applicability.
- Phase 2 receives the unchanged Phase 1 artifact plus manuscript content. It
  may then record applicability and findings.

The formative surface receives the same context authority during planning. It
may map criteria to planned sections and evidence needs, but it must not treat
venue fit as scientific validity, invent evidence, or silently change the
author's contribution claim.

## Interdisciplinary conflicts

Every conflict group from the context remains a set of parallel criterion
pointers. Consumers may mark a criterion `applicable`, `not_applicable`, or
`unresolved`, with an evidence/absence anchor or rationale after the
paper-visible boundary. They may not average criteria, select one from model
preference, or collapse a conflict into a scalar weight. Human resolution is
recorded outside the model-produced finding sidecar.

## Constructive Critical/Major findings

The machine sidecar contains only actionable `critical` and `major` findings.
Every row carries:

- exact criterion id/version/content-digest pointers selected in the active
  context;
- a typed manuscript evidence or absence anchor;
- scholarly relevance and confirmed-target relevance as separate fields;
- a minimum viable remedy, and a stronger costlier option when meaningful;
- resource/effort scope and explicit trade-offs;
- whether an option changes the author's research intent and therefore needs
  author choice; and
- either an honest remedy or an explicit statement that no honest remedy
  exists.

Remedies cannot assert invented data, results, completed analyses, or author
intent. `proposed_result_values` is structurally fixed to `false`. New-data or
research-intent-changing options are choices, never reviewer commands.

Scientific validity, venue fit, and submission readiness remain separate.
Criteria with `blocking_eligible=false` may inform advisory prose but cannot be
the sole pointer for a blocking Critical/Major finding.

## Failure behavior and authority boundary

Malformed JSON, duplicate keys, non-canonical ids, missing roles, pointer drift,
copied prose, changed profiles under one target-review id, symlinks, oversized
inputs, and invalid findings fail visibly. Binding conformance may stop a
consumer handoff because it proves inputs are mismatched; it never supplies an
editorial verdict, severity, gate decision, checkpoint decision, or author
triage.

The manifest and validator do not prove semantic correctness. Evidence
support, applicability, severity, venue alignment, and remedy usefulness remain
behavioral claims measured separately.

## Held-out evaluation

The paired evaluation uses the same sealed scenario, exact
`ReviewTargetContext`, token/output budget, tools, model, and replicate rule for
both arms:

- baseline: the pre-#684 consumer prompts;
- treatment: the binding marker, Target Criteria Brief, conflict discipline,
  and constructive-finding contract.

The preregistered expert labels cover profile resolution, criterion
applicability, unsupported findings, severity, venue alignment, and usefulness.
Usefulness judges whether a minimum remedy is feasible, preserves author intent,
states costs/trade-offs, and avoids invented evidence. Metrics are reported
separately; there is no composite “review quality” score.

The run publishes under `heldout-measurement/1.1`, retains raw outputs and exact
execution manifests, uses at least two replicates per item, and discloses either
model judges or the closed human-expert exception plus adjudication. No
model/API/subscription/network call runs in CI. Dispatch
requires explicit operator consent for provider, exact model, synthetic content
class, and quota/cost. The default subject transport is an isolated Codex CLI
session authenticated by the operator's ChatGPT subscription: the minimum run is
24 subject calls (six items, two arms, two replicates), and human experts supply
the required labels. The report selects the paired-controls-only
`human_expert_panel` exception, binds the suite-owned expert record by SHA-256,
and dispatches no redundant model judges. Its incremental metered API spend
ceiling is USD 0. Subscription quota consumption is still disclosed.

There is no automatic API fallback. A subscription quota interruption, missing
model, or unavailable CLI control is retained as blocked/partial and pauses the
run. Moving to an API is a new amended run and requires a call-count estimate,
worst-case USD estimate, an explanation of why the CLI is insufficient, and new
explicit operator consent. An API key or environment selector is never consent.
Provider-managed settings that the CLI does not expose are recorded as
unavailable rather than invented; both arms use the same observable controls and
balanced same-window order. Until a valid report is committed, documentation
says the constructive-value effect is unmeasured and makes no efficacy claim.

## Non-goals

- No venue scraping or model-memory criteria.
- No adaptive weights or silent conflict resolution.
- No change to the author-owned target or contribution claim.
- No automatic manuscript revision, invented data, or reviewer-owned research
  redesign.
- No replacement for #653 reviewer error calibration or #648 severity-band
  calibration.
- No live model call in tests or CI.
