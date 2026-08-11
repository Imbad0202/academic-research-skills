# #673 Cross-run Adjudication Activity — Frozen Contract

**Status:** frozen design; implementation must conform byte-for-byte where this
specification says "exact"
**Issue:** #673
**Date:** 2026-08-10
**Scope:** a user-selected local activity store, deterministic extraction from
explicit canonical artifacts, advisory rendering, deletion, and hermetic tests

## 1. Purpose and authority boundary

This feature records a narrow fact: which explicit adjudication actions were
captured across eligible terminal pipeline runs. It does not infer whether a
user read carefully, was attentive, remained engaged, agreed sincerely, or
retained meaningful ownership. It does not judge whether an action or result
was correct.

The store is an optional, user-owned local artifact. A caller selects it by an
explicit `--store` path on every operation. There is no default path,
environment-variable fallback, home-directory convention, recursive discovery,
passport lookup, or search for nearby stores. Nothing is transmitted or
aggregated across users.

The feature is observability only:

- it is never read by a gate, checkpoint-type selector, editorial decision,
  verdict, score, ranking, model prompt, agent dispatch, or terminal-state
  transition;
- it has no target, threshold, benchmark, rate, health class, pass state,
  traffic-light rendering, or comparison with another user;
- store failure cannot block, delay, undo, or change a pipeline transition; and
- a terminal state is persisted first. Activity capture and rendering run only
  afterwards as a best-effort advisory side effect.

The exact limitation sentence rendered in every output is:

> This records explicit adjudication activity only. It cannot determine correctness, attentiveness, engagement, or whether human ownership is real; genuine agreement and non-review can produce the same history.

The exact following sentence is also mandatory:

> This series is advisory only; it never gates, blocks, scores, or changes any verdict.

Separately and normatively, neither runtime nor renderer may define a target or
threshold or change any checkpoint or decision.

## 2. Frozen implementation surface

The complete production surface is closed to:

- `shared/contracts/activity/adjudication_activity_input.schema.json`, schema
  version `adjudication-activity-input/1.0`;
- `shared/contracts/activity/adjudication_activity_store.schema.json`, schema
  version `adjudication-activity-store/1.0`;
- `scripts/adjudication_activity.py`;
- `academic-pipeline/agents/state_tracker_agent.md`, which owns the closed
  action-time receipt writes and terminal-state receipt projection;
- `academic-pipeline/agents/pipeline_orchestrator_agent.md`,
  `academic-pipeline/SKILL.md`,
  `academic-pipeline/references/pipeline_state_machine.md`, and
  `academic-pipeline/references/process_summary_protocol.md`, which own the
  opt-in post-terminal append/render hook and refused-MANDATORY-skip behavior;
- `shared/compliance_checkpoint_protocol.md`, which owns the paired explicit
  compliance-override receipt;
- `shared/handoff_schemas.md`, which documents that these are local run
  receipts and that neither activity store nor aggregate enters a handoff or
  Material Passport;
- `scripts/check_673_adjudication_activity.py` and focused runtime/integration
  tests, including a static non-consumer check; and
- `scripts/_ci_pytest_manifest.toml` plus the existing spec-consistency
  workflow registration.

The receipt writers create data-minimized local run artifacts only. This file
map does not authorize adding the store, counts, or renderer output to a
passport, handoff, Process Record, agent prompt, or model payload. An
implementation that ships schemas and a CLI without these producer and
terminal-hook paths is incomplete and cannot claim end-to-end acceptance.

There is no legacy loader, migration command, compatibility branch, or
retroactive backfill. Any other schema version fails closed. A historical run
that did not produce a v1 source manifest is not scanned or reconstructed.

## 3. Eligible runs and observation window

One store record represents one eligible terminal run. The only eligible
terminal states are `completed` and `aborted`.

Terminal eligibility is proved by a closed inline `terminal_receipt` in the
input manifest. It copies a minimal projection and binds the exact existing
state-tracker JSON; there is no new terminal-receipt file or schema. The runtime
opens the bound state file beneath the explicit `--artifact-root`, rejects
duplicate keys and non-finite numbers, verifies its raw-byte SHA-256, and
strictly replays these state-tracker fields:

- receipt and input-root `run_id` are equal and both equal the state file's
  `run_id`;
- receipt `pipeline_state`, state-file `pipeline_state`, and input
  `terminal_state` must be equal;
- the state-file `current_stage` must map exactly to receipt `current_stage`
  and input `terminal_stage`;
- receipt `current_stage_status` must equal the status at the state file's raw
  `stages[current_stage]` key;
- a completed run must have `pipeline_state == "completed"`,
  `current_stage == "6"`, and Stage 6 status `completed` or `skipped`; and
- an aborted run must have `pipeline_state == "aborted"`; its exact
  `current_stage` maps to the recorded terminal stage and its copied status is
  exactly one of the state tracker's closed
  `pending | in_progress | completed | skipped | blocked` values.

The closed stage mapping is:

| State-tracker value | Activity value |
|---|---|
| `1` | `pipeline_stage_1` |
| `2` | `pipeline_stage_2` |
| `2.5` | `pipeline_stage_2_5` |
| `3` | `pipeline_stage_3` |
| `3p` | `pipeline_stage_3_prime` |
| `4` | `pipeline_stage_4` |
| `4p` | `pipeline_stage_4_prime` |
| `4.5` | `pipeline_stage_4_5` |
| `5` | `pipeline_stage_5` |
| `6` | `pipeline_stage_6` |

The first replayable aborted stage is Stage 1. Stage 0 is not in this closed
vocabulary because the state tracker has no Stage 0 status record to prove.

This includes both completed paths already defined by the pipeline: Stage 6
completed after terminal acknowledgement, or Stage 6 explicitly declined and
marked `skipped` before the global state becomes `completed`. Merely reaching a
stage, emitting a final draft, or receiving a review decision is not terminal.

### 3.1 Terminal source inventory is run authority

The state-tracker contract gains a stable `run_id` and a closed
`adjudication_activity_sources` inventory. The inventory has exactly the five
source-family rows in §4 order and, for every captured group, every closed
group/stage/role/id/relative-path/raw-SHA binding in canonical order. It also
records each row's capture state and reason. It contains no events, counts, or
prose.

Action-time producers best-effort append their closed receipt/artifact bindings
to pending state-tracker metadata through its sole-writer path. Receipt failure
never changes the action's already-derived routing or state effect.

Terminal integration is strictly two-step. First, the existing terminal
transition is made durable without reading, hashing, validating, or depending
on any activity metadata. Second, and only when the user selected a store, a
post-terminal metadata helper reopens that terminal state, resolves every
family to `captured`, `not_applicable`, or `unavailable`, computes current raw
hashes, validates exact groups, and atomically appends/seals the five-row
inventory in the same state JSON while leaving the terminal
state/stage/status byte-semantically unchanged. Failure of this second write
emits a diagnostic, creates no store row, and cannot roll back or alter the
terminal outcome.

The helper is a deterministic library entry point in
`scripts/adjudication_activity.py` named `seal_terminal_inventory(...)`; the
orchestrator passes explicit state and artifact-root paths and closed pending
receipt bindings. It performs no model reasoning, hash transcription, scan, or
path discovery.

`build-input` may only copy this exact inventory projection. `append-run`
reopens the raw-hash-bound state file, compares every input source field and
artifact binding to the sealed inventory, then reopens each referenced artifact
and verifies its bytes. Consequently a caller cannot splice a valid #670
sidecar or re-review quartet from another run merely by naming its path and
hash.

A state tracker without both stable `run_id` and the post-terminal sealed five-
row inventory is legacy and ineligible for reconstruction. No directory scan
or inferred backfill is allowed. New successfully sealed v1 runs always carry
all five rows, including explicit unavailable rows when action-time capture
failed.

The renderer selects the last `N` retained eligible run records by
`append_sequence`, never by a timestamp, filename, run id, filesystem order, or
event count. `N` defaults to `10`; the closed accepted range is `2..50`. If the
store retains fewer than `N`, all retained records are selected. A captured
zero-event run and a run with one or more unavailable source families both stay
in the selected-run denominator. Deleted sequence gaps stay gaps.

This denominator is deliberately store-relative. A terminal run for which the
user did not select this store, or whose best-effort append failed, has no
fabricated placeholder in the store and is not counted. The renderer never
calls the store the user's complete pipeline history or the last `N` actual
runs; it reports only successfully retained eligible run records in the
explicitly selected store.

Zero or one retained eligible run renders `INSUFFICIENT_HISTORY`, never pass,
healthy, zero-risk, or an inferred absence of adjudication.

## 4. Source-manifest input, not caller-supplied events

The input is a closed source manifest. Its root is:

```json
{
  "schema_version": "adjudication-activity-input/1.0",
  "store_id": "ADJ-ACTIVITY-STORE-example",
  "run_id": "run-42",
  "terminal_state": "completed",
  "terminal_stage": "pipeline_stage_6",
  "terminal_receipt": {
    "artifact_id": "pipeline-state-terminal-receipt",
    "relative_path": "state/run-42.json",
    "sha256": "<64 lowercase hex>",
    "run_id": "run-42",
    "pipeline_state": "completed",
    "current_stage": "pipeline_stage_6",
    "current_stage_status": "completed"
  },
  "sources": ["<the five receipts below, in exact order>"],
  "data_minimization": {
    "raw_prose_embedded": false,
    "user_identity_embedded": false,
    "absolute_paths_embedded": false
  }
}
```

The input contains no events, counts, rates, score, overturn field, free prose,
user identity, absolute path, or timestamp. The runtime alone derives events
after replaying canonical artifacts.

`sources` contains exactly five receipts in this order:

1. `revision_author_adjudication`;
2. `compliance_report`;
3. `re_review_traceability`;
4. `explicit_user_request`; and
5. `mandatory_checkpoint_response`.

Every receipt has one of three states:

- `captured`: at least one relative artifact binding is present and every bound
  artifact is opened, hash-verified, schema-checked, and replayed. A captured
  family may validly derive zero events.
- `not_applicable`: `reason_code` is exactly `not_applicable_for_run`, and the
  artifact list is empty. Normal absence because that workflow path was not
  exercised uses this state, not `unavailable`.
- `unavailable`: the artifact list is empty and `reason_code` is exactly one of
  `source_not_provided | source_unreadable | source_invalid |
  capture_not_supported`. This is an observed capture limitation, not zero
  activity. The run remains in the denominator and the limitation is rendered.

Stage exists only on each source artifact binding as
`artifact_group_stage`. It is non-null only for
`revision_author_adjudication`, with the closed values
`pipeline_stage_3 | pipeline_stage_3_prime`; every artifact in one group has
the same stage. It is null for all other roles and families. The input builder
must replay the terminal state-tracker receipt and require each named author
stage's status to be `completed`; `append-run` repeats that replay. Thus the
stage is explicit and hash-bound without being inferred from a sidecar or
trusted as a free receipt label.

Artifact paths use canonical POSIX relative syntax, have at most 512
characters, and are resolved only under the explicit artifact root. Absolute
paths, drive paths, backslashes, control characters, empty components, `.` or
`..` components, a trailing separator, path escape after resolution, symlinks,
and non-regular files are rejected. Hashes cover exact raw bytes, including a
trailing newline when present.

Every source artifact binding also carries closed `artifact_group_id`,
`artifact_group_stage`, and `artifact_role` fields. `artifact_group_id` is a
bounded ASCII identifier used only to join an exact source set.
`artifact_role` comes from the per-family closed vocabulary below; a free
`artifact_id`, filename, extension, array position alone, or inspected content
may not decide a role. Within one family, group ids are unique and artifacts
are in contract group/stage then role order. A missing, duplicate, extra,
swapped, cross-stage, or cross-group role makes the captured source invalid.

## 5. Canonical sources and extraction

Extraction is a closed projection over the artifacts below. Unknown records,
free-form conversation, prose similarity, sentiment, keywords, and model
classification never create an event.

### 5.1 `revision_author_adjudication`

This family has one or two groups. Each group contains exactly:

1. role `author_adjudication_input`, validated as
   `author-adjudication-input/1.0`; and
2. role `author_adjudication`, validated as `author-adjudication/1.0`.

Both share one group id and one `artifact_group_stage`; no third role is
allowed. Group stages are unique and canonical: Stage 3 first, then Stage
3-prime when both exist. This represents a run that performed initial author
adjudication and later re-review adjudication without dropping either source.

The runtime requires the input/output projections of `author_events`,
`author_adjudications`, `display_order`, and `collateral_authorizations` to be
identical and every adjudication's `author_event_id` to resolve to an explicit
session-user event. It reads the raw #670 author-owned sidecar, never a Schema
11 traceability copy or rendered decision letter.

It emits one event per sidecar adjudication with:

| `author_triage` | `event_type` | `disposition` | Overturn? |
|---|---|---|---|
| `wont_address` | `author_triage_wont_address` | `wont_address` | no |
| `not_on_point` | `author_triage_not_on_point` | `not_on_point` | yes |

`will_address` emits no event. A reason, target count, claim authorization, or
scope entry never becomes a separate event. Stage is exactly the producing
group's `artifact_group_stage`, `pipeline_stage_3` or
`pipeline_stage_3_prime`, after the state-tracker completion replay above; no
other stage is accepted. The resolved unique `author_event_id` is the
occurrence `interaction_id`; runtime derives the event's non-null
`interaction_sha256` by §5.6. The author event's `input_sha256` remains in the
source-event projection but is never used as a causal deduplication key.

### 5.2 `compliance_report`

This family has `1..16` groups in the action-time producer's append order.
Every group contains exactly one `compliance_report` role and zero or one
`compliance_override_action_receipt` role:

1. `compliance_report`, a Schema 12 object validated against
   `shared/compliance_report.schema.json`; and
2. `compliance_override_action_receipt`, required only for a qualifying
   override and forbidden for a plain no-override report.

The action receipt has this exact logical shape and contains no rationale:

```json
{
  "schema_version": "adjudication-compliance-override-action/1.0",
  "receipt_id": "COMPLIANCE-OVERRIDE-1",
  "run_id": "run-42",
  "actor_role": "user",
  "source": "explicit_session_user_action",
  "action": "acknowledge_compliance_limitation",
  "stage": "pipeline_stage_2_5",
  "scope": ["M4"],
  "report_sha256": "<paired report raw-byte SHA-256>",
  "override_ordinal": 1,
  "interaction_id": "USER-ACTION-17",
  "interaction_sha256": "<64 lowercase hex>"
}
```

One `compliance_block_override` event with disposition `block_overridden` is
emitted for one valid group—not for every `scope[]` element—only when all of
these are true:

- `overall_decision == "block"` and `user_action_required == true`;
- `mode == "systematic_review"`, and the report's compliance contribution
  itself is blocking: a non-empty PRISMA
  `by_tier.mandatory.fail` with PRISMA `block_decision == "block"`, a RAISE
  principle status `fail` with RAISE `block_decision == "block"`, or both; a
  legacy-only orchestrator block is not enough;
- `user_override.decision == true`;
- the actual blocking-contributor set is recomputed as the union of systematic-
  review Mandatory PRISMA item ids in the report's fail set and RAISE principle
  ids whose status is `fail`;
- the report `user_override.scope`, action-receipt `scope`, and recomputed
  blocking-contributor set are equal as duplicate-free sets;
- report stage and receipt stage agree; receipt `report_sha256` equals the
  raw-byte hash in the paired manifest binding; and the receipt has a unique
  `receipt_id` plus the exact matching run id, actor, source, action, and
  non-null interaction digest; and
- within each stage, `override_ordinal` starts at 1 and is contiguous without
  gaps or duplicates. Ordinal 2 requires a non-empty rationale and ordinal 3
  and later require at least 100 Unicode scalar values, exactly replaying the
  shipped friction ladder.

Stage `2.5` maps to `pipeline_stage_2_5`; stage `4.5` maps to
`pipeline_stage_4_5`. Non-systematic-review RAISE failures remain warn-capped
and never enter the blocking-contributor set. A PASS or WARN report,
legacy-only block, `user_action_required=false`, an
empty or mismatched scope, a scope that covers a non-blocking contributor but
misses a blocker, an unpaired or report-hash-swapped receipt, or a broken
pair makes the group invalid and emits no event. Schema 12's structural acceptance of a
PASS-plus-`user_override` object is therefore never sufficient evidence. The
event retains the paired receipt's exact `interaction_sha256`. The contiguous
per-stage ordinal makes omitted/reordered predecessors observable; the action-
time writer and extractor both enforce it.

A plain PASS or WARN report with no `user_override` and no action receipt is a
valid report-only group and emits zero events. This is how a run that executed
compliance without an override remains honestly `captured`, not
`not_applicable` or `unavailable`. Conversely, any report containing a
`user_override` claim that fails the full predicate, or any action receipt
paired to a non-qualifying report, fails the captured source rather than being
silently converted to zero.

### 5.3 `re_review_traceability`

The captured set has one group with exactly four roles in this order:

1. current role `input_manifest` (`re-review-input-manifest/1.1`);
2. current role `precommitment`;
3. current role `verdict_record`; and
4. final cumulative role `traceability`.

All four closed schemas validate; `round_id` agrees; and the existing exact
chain is replayed:

```text
restricted-canonical(input_manifest) -> precommitment.input_manifest_hash
restricted-canonical(precommitment)   -> verdict_record.precommitment_hash
restricted-canonical(verdict_record)  -> traceability.verdict_record_hash
```

One `re_review_verdict_changed` event with disposition `verdict_changed` and
stage `pipeline_stage_3_prime` is emitted only for this complete user-owned
chain:

1. a final cumulative `dissent_adjudications[]` record has
   `adjudicator == "user"` and `outcome == "original_upheld"`;
2. the current, non-superseded `reapplications[]` record for the same item has
   `answer_refs` containing `adjudication:<that dissent_id>`;
3. an `adjustments[]` record for the same item has
   `basis == "cross_model_adjudication"`,
   `source_ref == "reapplication:<that reapplication_id>"`, and unequal
   `from_verdict` and `to_verdict`;
4. the adjustment is in the exact non-forking adjustment chain whose tail is
   named by the final row; and
5. the row's final verdict equals the chain tail's `to_verdict`.

Every link must be unique. A superseded reapplication, system answer, user
`replacement_approved` outcome, `user_accepted_fail_closed`, other adjustment
basis, equal from/to verdict, orphan ref, fork, stale traceability emission, or
plain difference between Phase 2A and the final row emits nothing. This avoids
attributing a system Phase 2B adjustment to the user. The current source lacks
a stable shared action receipt, so `interaction_sha256` is `null`.

The exact public meaning of this event is: **“user adjudication was followed by
a verified verdict change.”** It must never be described as the user hand-
setting a verdict. The `g2d_acceptances[].accepted_by == "user"` /
`user_accepted_fail_closed` path is intentionally excluded: it acknowledges a
fail-closed `CANNOT_VERIFY` reapplication, and the re-review contract explicitly
says the user does not hand-set a verdict there. Golden fixtures pin one
positive `original_upheld -> current reapplication ->
cross_model_adjudication from != to` chain and one negative
`g2d_acceptance -> user_accepted_fail_closed` chain.

### 5.4 `explicit_user_request`

The family has one group containing exactly one role,
`explicit_user_request_log`. It is a closed JSON receipt log with this exact
logical shape:

```json
{
  "schema_version": "adjudication-explicit-user-request-log/1.0",
  "run_id": "run-42",
  "records": [
    {
      "request_id": "REQUEST-1",
      "actor_role": "user",
      "source": "explicit_session_user_action",
      "action": "justify_finding",
      "stage": "pipeline_stage_3",
      "finding_id": "REV-001",
      "interaction_id": "USER-ACTION-17",
      "interaction_sha256": "<64 lowercase hex>"
    }
  ]
}
```

The log is an upstream action-time receipt, not a transcript. `run_id` must
match; record ids are unique; `actor_role` and `source` are constants; the
closed actions are `justify_finding | redo_finding`; stages use the full closed
stage enum; ids are bounded to 128 ASCII identifier characters; and the log
contains at most 4,096 records and no prose.

`justify_finding` maps to `finding_justification_requested` /
`justification_requested`; `redo_finding` maps to
`finding_redo_requested` / `redo_requested`. Neither is an overturn merely
because a user requested explanation or another pass. The exact
`interaction_sha256` is retained for cross-family causal deduplication.

### 5.5 `mandatory_checkpoint_response`

The family has one group containing exactly one role,
`mandatory_checkpoint_response_log`. It is a closed JSON receipt log with this
exact logical shape:

```json
{
  "schema_version": "adjudication-mandatory-checkpoint-log/1.0",
  "run_id": "run-42",
  "records": [
    {
      "response_id": "RESPONSE-1",
      "checkpoint_id": "stage-4.5-integrity",
      "checkpoint_type": "MANDATORY",
      "actor_role": "user",
      "source": "explicit_session_user_action",
      "stage": "pipeline_stage_4_5",
      "disposition": "adjust",
      "interaction_id": "USER-ACTION-17",
      "interaction_sha256": "<64 lowercase hex>"
    }
  ]
}
```

The same closed-log constraints apply. Allowed source dispositions are
`proceed | skip | pause | adjust | view_progress | redo | abort`. `proceed`
proves an explicit action but emits no event. `skip` is a refused attempt at a
MANDATORY checkpoint: it must leave pipeline state unchanged and emits
`mandatory_checkpoint_non_proceed` with stored disposition `skip_refused`.
Each of the other five non-proceed choices emits the same event type with its
source disposition unchanged. Allowed stages are the complete replayable
pipeline-stage vocabulary, Stage 1 through Stage 6 including half/prime stages.
This deliberately covers core integrity/review/finalization checkpoints plus
audit-MINOR, score-regression, and structural-revision MANDATORY handlers at
Stage 4/4-prime. Non-MANDATORY checkpoint records are invalid, not silently
counted.

Normalization is owned by the explicit checkpoint handler, never a prose
parser. Handler branches map as follows: `continue`, `ship_with_known_residue`,
and `acknowledge_structural_shape` -> `proceed`; `iterate`, `retry`, and
`another_round` -> `redo`; `narrow`, `expand_exact_scope`, and explicit setting
changes -> `adjust`; progress/status inspection -> `view_progress`; pause/stop-
here -> `pause`; abort/terminate/abort-stage -> `abort`; and an attempted skip
-> `skip`, which is then stored as `skip_refused`. A new handler branch must be
added to this closed normalization table before it can produce activity.

The orchestrator may create these two receipt-log families only from a
structured command, UI action, or an explicit event-writing API at the time of
the user's action. It may not convert unstructured natural-language history
into a receipt after the fact.

### 5.6 Cross-family causal deduplication

Content hashes are not deduplication keys: two distinct actions may have
identical text. Deduplication uses only an equal, non-null
`interaction_sha256` emitted by the action-time source.

Every non-null interaction digest is recomputed, never trusted:

```text
interaction_sha256 = SHA256(
  b"ars.adjudication-activity.interaction/1.0\0" +
  canonical({"run_id": <run_id>, "interaction_id": <interaction_id>})
)
```

`interaction_id` is a unique run-scoped occurrence id, not message content.
For #670 it is the resolved unique `author_event_id`. Compliance, explicit-
request, and mandatory-checkpoint receipts carry it explicitly; when one user
action creates more than one receipt, their action-time producer copies the
same id and derived digest. Re-review stays null when its current chain has no
provable action-time occurrence id. The store retains only the digest.

The source order in §4 is also precedence order. After all candidate events
are derived, for each non-null interaction digest the runtime retains every
per-item event from the earliest family containing that digest and suppresses
events with that digest from later families. Thus a typed author, compliance,
re-review, or explicit-request event wins over a generic mandatory-checkpoint
receipt, while a single interaction that adjudicates several items still keeps
all of those item events inside the winning family. `null` interaction values
never deduplicate.

### 5.7 Exact source-event projections and order

The `source_record` input to `source_event_sha256` is closed per family:

- author: `item_id`, `author_event_id`, `author_triage`, the resolved
  `input_sha256`, and derived `interaction_sha256`;
- compliance: `artifact_group_id`, mapped stage, sorted blocking-contributor
  ids, report raw-byte SHA-256, action-receipt raw-byte SHA-256, and
  `interaction_id` plus `interaction_sha256`;
- re-review: `round_id`, `dissent_id`, `item_id`, `reapplication_id`,
  `adjustment_id`, `from_verdict`, `to_verdict`, and traceability raw-byte
  SHA-256;
- explicit request: exactly `request_id`, `actor_role`, `source`, `action`,
  `stage`, `finding_id`, `interaction_id`, and `interaction_sha256`; and
- mandatory response: exactly `response_id`, `checkpoint_id`,
  `checkpoint_type`, `actor_role`, `source`, `stage`, the source disposition,
  `interaction_id`, and `interaction_sha256`.

No rationale or finding text enters a projection. For `skip`, the source
projection retains source disposition `skip`, while the derived event stores
the mechanically mapped `skip_refused`.

Candidates are generated in family order, then author-sidecar array order,
compliance group order, numeric re-review adjustment-id order, explicit-log
record order, and mandatory-log record order. Causal deduplication preserves
the relative order of surviving candidates. Append-time extraction computes
and freezes this order before the sealed run-record digest is written. Offline
store validation verifies the retained array and its record/event digest
commitments, but does not claim to reconstruct omitted source records from the
data-minimized store. A user who deliberately rewrites a local store and
recomputes every public digest has authored a new self-consistent store; this
feature provides deterministic consistency, not keyed authenticity. The CLI
offers no event-reordering or sealed-run update operation, and event order does
not affect run-window selection or either count.

## 6. Closed event and count semantics

The store's seven event types and exact dispositions are:

| Event type | Exact disposition(s) | Counts as adjudication | Counts as overturn |
|---|---|---:|---:|
| `author_triage_wont_address` | `wont_address` | yes | no |
| `author_triage_not_on_point` | `not_on_point` | yes | yes |
| `compliance_block_override` | `block_overridden` | yes | yes |
| `re_review_verdict_changed` | `verdict_changed` | yes | yes |
| `finding_justification_requested` | `justification_requested` | yes | no |
| `finding_redo_requested` | `redo_requested` | yes | no |
| `mandatory_checkpoint_non_proceed` | `skip_refused | pause | adjust | view_progress | redo | abort` | yes | no |

`adjudication_count` is the number of retained derived events in the selected
runs. `overturn_count` is recomputed as the number whose `event_type` is in the
exact set:

```text
author_triage_not_on_point
compliance_block_override
re_review_verdict_changed
```

Neither count is stored. No caller supplies an overturn boolean. A declined
action, request for justification, redo request, or decision not to proceed is
observable adjudication, but it does not assert that an underlying finding or
verdict was overturned.

An unavailable source contributes no fabricated event and does not mean zero.
For that reason all displayed event totals are labelled as recorded activity,
and `unavailable_run_count` is also shown.

## 7. Store, identity, canonical bytes, and caps

The closed store root is:

```json
{
  "schema_version": "adjudication-activity-store/1.0",
  "store_id": "ADJ-ACTIVITY-STORE-example",
  "revision": 1,
  "next_sequence": 2,
  "runs": ["<sealed run records>"],
  "data_minimization": {
    "raw_prose_embedded": false,
    "user_identity_embedded": false,
    "absolute_paths_embedded": false
  }
}
```

An initialized empty store is `revision=0`, `next_sequence=1`, `runs=[]`.
Every successful append or explicit delete rewrite increments `revision` by
exactly one. Append assigns the current `next_sequence`, then increments it.
Deletion never decrements it. Surviving sequences are strictly increasing,
unique, never renumbered, and never reused. Deleting every run may therefore
leave an empty store with a positive revision and `next_sequence > 1`.
Because each allocated sequence came from one earlier append and deletions add
revisions without allocating sequences, every valid store also satisfies
`revision >= next_sequence - 1`.

Each run is sealed and contains only:

- `append_sequence`, `run_id`, `terminal_state`, and `terminal_stage`;
- exact terminal- and input-receipt hashes;
- `sealed: true` and a run-record hash; and
- the five source rows, which retain capture state, reason, canonical artifact
  hashes, and minimal derived events. Artifact ids and paths are not retained.

Each minimal event contains exactly `event_id`, `event_type`, `stage`,
`disposition`, nullable `interaction_sha256`, and `source_event_sha256`. It
contains no finding text, rationale, response text, user identity, agent name,
model id, timestamp, path, score, or aggregate.

### 7.1 Restricted canonical JSON

Contract digests use the following restricted JCS-compatible encoding; no
broader canonicalization behavior is implied:

- permitted scalar types are string, integer, boolean, and null; floats and
  non-finite values are forbidden;
- duplicate object keys are rejected during parsing;
- contract keys are ASCII and sort by ascending code point;
- arrays preserve contract-defined order;
- encoding uses compact separators, `ensure_ascii=false`, UTF-8, and no BOM;
  and
- canonical digest bytes have no trailing newline. Persisted store bytes are
  those canonical bytes followed by exactly one LF; the LF is excluded from
  contract digests but included in raw-file confirmation hashes.

The exact domain separators and preimages are:

```text
input_receipt_sha256 = SHA256(
  b"ars.adjudication-activity.input/1.0\0" + canonical(input_manifest)
)

source_event_sha256 = SHA256(
  b"ars.adjudication-activity.source-event/1.0\0" +
  canonical({"source_family": <family>, "source_record": <exact projection>})
)

event_digest = SHA256(
  b"ars.adjudication-activity.event-id/1.0\0" +
  canonical({
    "run_id": <run_id>,
    "source_family": <family>,
    "event_type": <type>,
    "stage": <stage>,
    "disposition": <disposition>,
    "interaction_sha256": <sha-or-null>,
    "source_event_sha256": <sha>
  })
)
event_id = "ACTIVITY-EVENT-" + lowercase_hex(event_digest)

record_sha256 = SHA256(
  b"ars.adjudication-activity.run/1.0\0" +
  canonical(<complete run record with only record_sha256 omitted>)
)
```

The family-specific `source_record` is exactly the closed record that caused
the event plus its stable parent identifiers needed to disambiguate it; it
excludes prose not needed by the predicate. The extraction implementation must
freeze those projections as named pure functions and mutation-test every
included field. Raw artifact bindings use ordinary SHA-256 over exact file
bytes, not this canonical form.

### 7.2 Identity and duplicate policy

Within retained records, `run_id`, `append_sequence`, `input_receipt_sha256`,
`record_sha256`, and `event_id` are each unique where applicable. Re-appending
the same `run_id` with the same `input_receipt_sha256` is an idempotent success:
while holding the exclusive lock, runtime validates the retained sealed record,
emits the exact `already_appended` line in §8, and performs no write, revision
increment, sequence allocation, or metadata-time change. The same `run_id` with
a different input receipt, or the same input receipt under a different run id,
fails with `CONFLICT`; append never updates or merges an existing run. A
successful explicit deletion removes the selected record completely and
deliberately removes its deduplication memory. A later new append may reuse that
run id only because the user explicitly deleted the prior record; it receives a
fresh, higher append sequence.

### 7.3 Hard caps

The runtime fails closed before mutation at all of these limits:

- input manifest: 1 MiB raw bytes;
- one referenced artifact: 8 MiB raw bytes;
- all referenced artifacts for one run: 64 MiB raw bytes;
- artifacts per source family: 64;
- source-log records and derived events: at most 4,096 per run;
- derived events: at most 100,000 per store;
- retained runs: at most 10,000; and
- persisted store: at most 16 MiB, including its final LF.

Reaching a cap never evicts, truncates, summarizes, or rewrites an older run.
The append fails without changing the store; the user may explicitly select a
new store or delete records.

## 8. CLI and exact success output

The only commands are:

```text
python scripts/adjudication_activity.py init-store \
  --store <file> --store-id <id>

python scripts/adjudication_activity.py build-input \
  --state <pipeline-state.json> --artifact-root <dir> \
  --store-id <id> --output <manifest.json>

python scripts/adjudication_activity.py append-run \
  --store <file> --artifact-root <dir> --input <manifest.json>

python scripts/adjudication_activity.py render \
  --store <file> [--window <2..50>]

python scripts/adjudication_activity.py validate --store <file>

python scripts/adjudication_activity.py delete-runs \
  --store <file> --store-id <id> --expect-store-sha256 <raw-byte-sha> \
  (--run-id <id> [--run-id <id> ...] | --sequence-range <first>:<last>)

python scripts/adjudication_activity.py delete-store \
  --store <file> --store-id <id> --expect-store-sha256 <raw-byte-sha> \
  --confirm DELETE-ADJUDICATION-ACTIVITY-STORE
```

Every path-bearing operation requires its path explicitly. `init-store` creates
only a missing path as the canonical empty store; an existing path is a
`CONFLICT`, even when its bytes are identical. `build-input` accepts no source
rows, paths, hashes, events, or counts from the caller. It strictly replays the
explicit state path, requires stable `run_id` plus a sealed five-row
`adjudication_activity_sources` inventory, copies only that exact projection,
binds the raw state bytes as `terminal_receipt`, validates every projected
artifact beneath the explicit artifact root, and atomically creates only the
explicit output path. An existing output path is a `CONFLICT` and no ambient
scan or reconstruction is permitted. `append-run` creates a missing store using
the input `store_id`; it never creates a store after a validation or extraction
failure. An existing store id must equal the input id. `validate` verifies
schema, canonical bytes, caps, run digests, ordering, uniqueness, terminal
invariants, source/event family constraints, cross-family causal uniqueness,
`revision`, and `next_sequence`.

`delete-runs` accepts exactly one selection mode. The id set is non-empty and
duplicate-free. A sequence range is inclusive with `first <= last`. Every
selected id must exist; a range must select at least one retained record. The
command requires both the exact store id and SHA-256 of the current raw store
file, then deletes whole records, increments revision once, preserves
`next_sequence`, writes no tombstone or aggregate, and reports:

```text
[ARS-ADJUDICATION-ACTIVITY] deleted_runs=<k>; revision=<r>; next_sequence=<s>
```

`delete-store` takes the same raw-byte hash plus the exact confirmation token.
For a valid store it also verifies `store_id`. If parsing or validation fails,
whole-store deletion remains the sole recovery path: exact path, exact current
raw-byte hash, and exact token are sufficient; no field is trusted from corrupt
JSON. It unlinks only that regular store file and emits:

```text
[ARS-ADJUDICATION-ACTIVITY] deleted_store=true
```

Successful initialization, input construction, append, idempotent append, and
validation emit exactly:

```text
[ARS-ADJUDICATION-ACTIVITY] initialized store_id=<json-string>; revision=0; next_sequence=1
[ARS-ADJUDICATION-ACTIVITY] built_input run_id=<json-string>; source_count=5
[ARS-ADJUDICATION-ACTIVITY] appended run_id=<json-string>; append_sequence=<n>; revision=<r>
[ARS-ADJUDICATION-ACTIVITY] already_appended run_id=<json-string>; append_sequence=<n>; revision=<r>
[ARS-ADJUDICATION-ACTIVITY] valid store_id=<json-string>; retained_runs=<n>; revision=<r>; next_sequence=<s>
```

JSON string quoting is used for ids so control characters can never forge a
line. Success exits `0`. Errors emit one stderr line and no stdout:

```text
[ARS-ADJUDICATION-ACTIVITY ERROR:<CODE>] <bounded detail>
```

The closed exit mapping is:

| Exit | Codes | Meaning |
|---:|---|---|
| 2 | `USAGE` | argument grammar, command, or window error |
| 3 | `PATH`, `INPUT`, `SOURCE` | unsafe path or invalid input/source artifact |
| 4 | `STORE` | missing, non-canonical, schema-invalid, digest-invalid, or corrupt store |
| 5 | `CONFLICT`, `CAP` | conflicting identity/path or hard-cap refusal |
| 6 | `DELETE_CONFIRMATION` | store id, raw hash, target set, range, or confirmation mismatch |
| 7 | `LOCK`, `WRITE` | lock contention/unsupported locking or atomic I/O failure |

Details are capped at 500 Unicode scalar values and never include artifact
content, user prose, or an absolute path.

## 9. Exact renderer

For zero or one selected run, the first line is exactly:

```text
[ARS-ADJUDICATION-ACTIVITY INSUFFICIENT_HISTORY] selected_retained_eligible_run_count=<n>; minimum_required=2; requested_window=<N>.
```

For two or more, the first line is exactly:

```text
[ARS-ADJUDICATION-ACTIVITY] selected_retained_eligible_run_count=<n>; requested_window=<N>; adjudication_count=<k> (denominator: <n> retained eligible terminal run records); overturn_count=<j> (denominator: <k> recorded adjudications); unavailable_run_count=<u> (denominator: <n> retained eligible terminal run records).
```

The insufficient-history form follows its first line with the same three count
clauses, beginning `[ARS-ADJUDICATION-ACTIVITY COUNTS]`. This makes zero/one-run
output honest without turning insufficient data into a pass.

Next, one line per selected run appears in ascending append-sequence order:

```text
sequence=<s>; run_id=<json-string>; terminal_state=<state>; adjudication_count=<k> (denominator: 1 retained eligible terminal run record); overturn_count=<j> (denominator: <k> recorded adjudications); unavailable_source_count=<u> (denominator: 5 source families).
```

Next this exact coverage line appears:

```text
Coverage: only successfully retained records in this explicitly selected store are shown; runs without this store selection or whose append failed are not represented.
```

Finally the exact two sentences in §1 appear, each on its own line. There is no
percentage. When `<k>` is zero, `overturn_count=0 (denominator: 0 recorded
adjudications)` remains literal rather than fabricating a rate. A run is in
`unavailable_run_count` iff at least one of its five source rows is
`unavailable`; `not_applicable` and captured-zero are distinct and visible in
the per-run unavailable-source denominator.

## 10. Locking, atomicity, and corruption

All operations first reject a store path that is a directory, symlink, FIFO,
device, socket, or multiply-linked regular file. A zero-byte adjacent
`<store>.lock` is coordination metadata only: it contains no id, count, digest,
or activity and is not a derived aggregate. Reads take a shared advisory lock;
append and deletion take an exclusive lock. Lock acquisition is one
non-blocking attempt, so the runtime uses no timeout clock. Unsupported locking
or contention fails without reading a mutable snapshot.

A writer performs, while holding the lock:

1. open and validate the current store from one file descriptor;
2. derive the complete candidate in memory and validate it again;
3. enforce every cap before writing;
4. create a mode-`0600` temporary regular file in the same directory;
5. write canonical bytes plus one LF, flush, and `fsync` it;
6. atomically `replace` the selected store path; and
7. `fsync` the parent directory before reporting success.

Any failure before step 6 leaves the old bytes untouched. A fault at or after
replace is reported as `WRITE`; tests reopen the path and accept only the full
old or full new canonical store, never a partial hybrid. No backup, journal,
cache, summary, tombstone, or alternate store is left behind.

Parsing rejects invalid UTF-8, BOM, duplicate keys, floats/non-finite values,
trailing data, schema drift, non-canonical persisted bytes, digest mismatch,
wrong source order, wrong event family/stage/disposition, duplicate identity,
bad revision/sequence relationships, and cap overflow. `append-run`, `render`,
`validate`, and `delete-runs` all fail closed on corruption. Only the raw-byte,
confirmation-bound `delete-store` recovery in §8 may operate on a corrupt
store.

## 11. Integration and data minimization

For every author choice, compliance override, explicit request, and checkpoint
response, the existing handler first derives and durably applies its ordinary
routing/state effect. Only then does it best-effort write the closed activity
receipt and pending inventory binding. Receipt failure cannot refuse, roll
back, or change proceed, pause, adjust, view-progress, redo, abort, or a valid
compliance override. For `skip`, the existing MANDATORY refusal and unchanged
pipeline state are derived first; `skip_refused` is only an after-the-fact
receipt of that result.

The terminal integration order is fixed:

1. make and durably persist the existing terminal state transition, without
   consulting activity state;
2. if and only if a store was selected, best-effort seal the exact five-source
   inventory in post-terminal metadata;
3. deterministically `build-input` from that sealed state, without scanning;
4. invoke idempotent `append-run`;
5. optionally invoke `render`; and
6. surface any step-2-through-5 failure as an advisory diagnostic while
   preserving the already-durable terminal outcome.

The store path, store contents, renderer output, and failure state are never
copied into the Material Passport, handoff schemas, Process Record, reviewer
input, collaboration-depth observer, compliance decision, or model request.
No network, model, judge, external API, ambient clock, directory scan, glob, or
filesystem metadata time participates in extraction, ordering, counting, or
tests.

Source prose is used only transiently when a current canonical validator must
verify its artifact. Only the minimal event projection and digests enter the
store. The runtime must not log raw rationale, finding text, checkpoint answer,
artifact content, user identity, or an absolute path on success or failure.

## 12. Required P1 kill mutations

The focused suite must prove each mutation below fails or, for renderer/control
plane cases, cannot affect the forbidden consumer:

1. add caller-supplied `events`, counts, rates, score, threshold, or overturn
   boolean to the input;
2. accept a running/paused state, a mismatched terminal receipt, completed
   before Stage 6, or an aborted run whose stage does not replay;
3. omit, duplicate, or reorder a source family; turn unavailable into zero;
   exclude captured-zero or unavailable runs from the window denominator;
4. accept an absolute/traversing/symlink/non-regular artifact or a wrong raw
   hash; accept a missing, duplicate, extra, swapped, free-named, or
   cross-group artifact role;
5. extract #670 activity from a Schema 11 copy, count `will_address`, count each
   target/reason, classify `wont_address` as an overturn, or accept an author
   stage outside Stage 3/3-prime; spoof `artifact_group_stage`, fail to bind it
   into the input digest, or omit the matching completed stage in the terminal
   receipt;
6. count one compliance scope element as one event; count a PASS/WARN report,
   `user_action_required=false`, an unpaired/fake action receipt, a scope that
   is not exactly the recomputed blocking-contributor set, or accept a broken
   per-stage friction ladder;
7. count a Phase 2B/system adjustment, `user_accepted_fail_closed`,
   `replacement_approved`, stale/superseded reapplication, equal from/to
   verdict, forked adjustment chain, or orphan re-review ref;
8. infer justify/redo/non-proceed from conversation, accept a non-user receipt,
   count `proceed`, accept a non-MANDATORY checkpoint, silently allow a
   MANDATORY `skip`, store it as anything but `skip_refused`, or let the refused
   skip change pipeline state;
9. deduplicate by content, let a later generic family beat an earlier typed
   family, discard sibling per-item events in the winning family, or deduplicate
   null interaction digests; trust a supplied interaction hash, or use
   `input_sha256` instead of the run/id occurrence digest;
10. store or accept any event type/disposition/stage outside the closed matrix,
    or derive `overturn_count` from any set other than the three exact types;
11. order the window by time/name/id, use a default other than 10, admit a bound
    outside 2..50, renumber a deletion gap, reuse a sequence, or auto-evict;
12. mutate/upsert a sealed run through the CLI, accept a sealed run whose
    retained record/event digests are stale, write or bump revision for an
    identical retained run/input retry, accept the same run id with a different
    input receipt or the same input receipt under a different run id, truncate
    at a cap, or leave a partial store after injected write failure;
13. render, append, or range-delete a corrupt store; delete with a wrong id,
    raw hash, token, id set, or range; or leave a tombstone/aggregate;
14. omit or paraphrase either exact §1 sentence; render pass, health, score,
    benchmark, rate, target, threshold, diagnosis, or attention/ownership claim;
15. read the store from a gate, checkpoint selector, decision, verdict,
    terminal transition, model prompt, or dispatch; or let recorder failure
    affect terminal state; and
16. add a legacy migration, backfill scan, default store path, clock, network,
    model, judge, API, directory walk, or glob.

## 13. Required P2 boundary mutations

Boundary coverage includes:

- duplicate JSON keys, invalid UTF-8/BOM, non-finite/float values, trailing
  data, non-canonical object order, and a contract digest that wrongly includes
  the persisted LF;
- all exact maximums and maximum-plus-one cases for bytes, artifacts, records,
  events, runs, store events, store size, ids, refs, and error detail;
- empty store, one run, exactly two runs, fewer-than-window, exactly 10, exactly
  50, window 1, and window 51;
- completed Stage 6 `completed`, completed Stage 6 `skipped`, and an aborted run
  at every closed stage including `pipeline_stage_4_prime`;
- five captured-zero sources, five unavailable sources, a mix of captured,
  not-applicable, and unavailable, and one unavailable source in an otherwise
  captured run;
- two identical author-input strings with distinct `author_event_id` occurrence
  ids and therefore distinct interaction hashes, the same non-null interaction
  in two families, multiple per-item events for one winning-family interaction,
  and null interaction hashes;
- first append, append after sequence gaps, delete one id, delete several ids,
  inclusive range endpoints, delete all retained runs, raw-hash race, lock
  contention, and corrupt whole-store recovery; and
- deterministic output and digests under a changed locale, timezone, file
  mtime, directory enumeration order, and unavailable network.

## 14. Acceptance

#673 is accepted only when all of the following are green without a live model,
judge, network, API, filesystem scan, or clock dependency:

1. both schemas are Draft 2020-12 valid and closed;
2. input fixtures cover all three capture states and all five source families;
3. source fixtures produce all seven event types, captured-zero, unavailable,
   and the exact re-review chain;
4. event ids and all three contract digest families match independent golden
   vectors;
5. count tests distinguish `adjudication_count` and `overturn_count` exactly;
6. window persistence covers completed, aborted, zero-event, unavailable, and
   deletion-gap runs across process invocations;
7. immutable append, idempotent exact retry, conflicting duplicate refusal,
   locking, atomic fault injection, corruption fail-closed behavior, range
   deletion, and corrupt whole-store deletion pass;
8. renderer golden tests pin every character of insufficient-history, summary,
   per-run denominators, and the two exact limitation/advisory sentences;
9. static non-interference tests prove no gate, decision, verdict, checkpoint
   type, terminal transition, model dispatch, passport, handoff, or Process
   Record consumes the store or its aggregates;
10. every P1 kill mutation in §12 fails for the intended reason and the P2
    boundaries in §13 are exercised; and
11. ordinary repository schema, spec-consistency, lint, and full pytest suites
    remain green.

This acceptance is prospective protocol validation only. It authorizes no
historical reconstruction and requires no engagement, quality, or performance
claim.
