# #744 — Profile-relevant cross-stage alternative explanation register

Status: DESIGN FREEZE for `alternative-stage-map/1.0`,
`alternative-trigger/1.0`, `alternative-explanation-register/1.0`, and #744's
use of the shared `ars-passport-transaction/1.0` envelope. The schema shapes, stage-eligibility
rule, state machine, independent alternative-budget semantics,
provenance/adoption boundary, reopening and invalidation behavior, additive
v1 introduction, storage, and evaluation boundary are frozen here. A future
v1-to-v2 migration contract is NOT frozen (§9). This document authorizes no
implementation, no evaluation run, no new prompt on the simple path, and no
default-on behavior. A future beta is opt-in behind
`ARS_ALTERNATIVE_REGISTER=1`. For a project that has never enabled or
materialized the feature, unset or `0` is byte-equivalent to current behavior;
turning the flag off after materialization makes existing state dormant and
does not delete it.

Parent epic: #741. Roadmap:
[Phase 3](../ROADMAP-v3.20.1-v3.22.md#phase-3--cross-stage-alternative-register).
Upstream contracts: [#742 research-family profile](./2026-08-17-742-research-family-profile-contract-design.md)
and [#743 inquiry branch ledger](./2026-08-17-743-inquiry-branch-ledger-design.md).
Evidence registry: [stage capability matrix](../../shared/contracts/capability/stage_capability_matrix.json).

## 1. Problem and claims boundary

Preserving early research-question branches does not preserve the alternatives
that become relevant during theory choice, design, measurement, analysis,
synthesis, interpretation, drafting, or review. The register carries a
profile-permitted alternative forward, records what happened to it, and makes
later reopening and first-degree invalidation inspectable.

The register is a memory and accountability surface. It does not establish
that an alternative is complete, novel, correct, useful, or preferred; it
does not rank alternatives; and it does not instruct the author to maximize
their number. `supported` and `ruled_out` below are author dispositions
relative to recorded anchors, not ARS truth verdicts. More alternatives are
not treated as better.

Every `actor: author` value has the same boundary as #743: it is a
within-session attestation from the interactive author surface, not
cryptographic identity authentication. Provenance is inspectable, not
forgery-proof against a hostile session.

## 2. Profile and stage vocabulary

The normative stage identifier is the #742 `task_family_id` list. Terms such
as “theory choice”, “measurement”, “analysis”, and “interpretation” describe
decisions within those task families; they are not new universal pipeline
stages. The register must not add an `analysis` stage or infer a discipline
ontology. Pipeline checkpoint ids remain mapped to task families exactly as
frozen in #742 §2.

The `research-workflow-profile/1.0` contract declares a profile-wide stage
map and a profile-wide list of alternative categories, but it deliberately
does not declare which category is relevant at which stage. Its shape is
closed, so #744 must not add a field to it in place. A separately versioned,
hash-bound companion document supplies that missing cross-product.

### 2.1 Companion contract: `alternative-stage-map/1.0`

One immutable stage map binds one exact profile version and content hash.
Changing any content creates a new `map_version`; publishing different bytes
under an existing version is a contract violation.

| Field | Req | Shape |
|---|---|---|
| `schema_version` | yes | const `alternative-stage-map/1.0` |
| `map_id` | yes | stable slug |
| `map_version` | yes | semver |
| `profile_binding` | yes | `{profile_id, profile_version, content_sha256}`; all three must match a canonically validated #742 profile |
| `stage_category_map` | yes | object keyed only by #742 `task_family_id`; omitted keys mean `unresolved_fit`, never applicable |
| `provenance` | yes | the #742 provenance shape and vocabulary: `{source, source_pointer, last_reviewed_at, freshness_state}` |
| `content_sha256` | yes | SHA-256 over JSON Canonical Form with this field replaced by the 64-zero placeholder, exactly as in #742 |

Each present `stage_category_map` value has one closed shape:

- `{state: "applicable", categories: [...], alternative_budget: integer}`: a
  non-empty, duplicate-free list whose values are a subset of the bound
  profile's declared `alternative_categories.categories`; the budget is at
  least 1, at most the JCS-safe integer `9007199254740991`, and is the maximum
  author-owned live alternatives at this one task family (§8);
- `{state: "intentionally_absent", reason: string}`: the profile deliberately
  has no alternative-register surface at this task family; or
- `{state: "unresolved_fit"}`: no applicability claim has been made.

`alternative_budget` belongs to this companion contract. It is not #742's
`branch_budget`, is not derived from it, and does not alter #743 replay. The
profile's `overflow_behavior: ask_merge_park_archive` supplies only the
author-controlled disposition vocabulary used when either independent budget
would overflow; it does not make the two counts interchangeable. A budget is
forbidden on `intentionally_absent`, `unresolved_fit`, or omitted cells.

The following cross-contract invariants fail validation:

1. A stage-map key is `applicable` unless the bound profile marks that same
   task family `applicable`.
2. A category is named unless the bound profile has
   `alternative_categories.state: declared` and names that category.
3. The bound profile has unresolved alternative categories while any
   stage-map key is `applicable` or `intentionally_absent`; unresolved means
   do not infer either presence or absence.
4. The bound profile declares an empty category list while the stage map has
   any `applicable` key. In that case an empty `stage_category_map` is the
   canonical declaration that no register surface applies; no per-stage
   boilerplate is generated.
5. An applicable cell omits `alternative_budget`, supplies a non-integer or a
   value outside `1..9007199254740991`, or any other cell supplies one.
6. Unknown fields, unknown task-family ids, duplicate categories, a
   non-canonical file, or any content-hash mismatch.

A structurally valid map whose provenance is `stale` or `unverified` remains
inspectable but cannot become the effective runtime map; activation fails
visibly until the author supplies or confirms a current map. This mirrors the
#742 distinction between a valid declaration and evidence that it is fresh.

An entry is lawful at one task family only when the effective profile marks
the task family `applicable` **and** the effective companion map marks the
task family `applicable` and includes the entry's category. Eligibility is
permission to record an alternative, never a requirement to create a row or
open a prompt.

### 2.2 Stage-map selection receipt and exact-byte retention

Map provenance says where content came from; it does not grant runtime
authority. Every effective map therefore carries a separate, closed
within-session author receipt:

`{map_id, map_version, content_sha256, profile_binding, selected_by,
actor: "author", recorded_at, interaction_ref}`.

`selected_by` is `user_explicit | user_confirmed_proposal`. Selecting a
profile and its shipped companion in one visible interaction is
`user_confirmed_proposal`; there is no automatic or inferred map selection.
The three map identity fields and `profile_binding` must equal the validated
map document byte-for-byte, and `interaction_ref` is a non-empty pointer to
the interaction that produced this embedded receipt. The receipt itself is
the durable within-session author attestation under §1; `interaction_ref` is
provenance metadata, not a second authentication claim. A map with no matching
receipt cannot become effective, including when the first register event is
AI-authored.

Every register context stores both `stage_map_binding` and the complete
canonical `stage_map_document` that produced it. Replay recomputes the
document's self-digest and requires its derived binding to equal both the
stored binding and selection receipt. This embedded immutable snapshot is the
authoritative resolver for historical stage-map bytes; a shipped catalog or
the original user-authored workspace file is only an import source and may
not be substituted by id/version. Historical #742 profile bytes remain
resolved exactly as #743 §7 requires: by all three binding fields, never by
the currently shipped fallback.

The #742 selection receipt is itself an append-only, mutable document, so a
path to its latest bytes is not a historical resolver. Every register context
that introduces a profile therefore embeds one closed
`profile_selection_receipt_snapshot`:

`{receipt_ref, receipt_sha256, selection_sequence, selection_sha256,
receipt_document}`.

`receipt_document` is the complete parsed and validated
`research-workflow-profile-selection-receipt/1.0` document as observed under
the shared passport lock. The upstream receipt's raw JSON may contain
insignificant whitespace or the CLI's normal trailing LF: #744 validates it
with #742 semantics, converts the parsed value to JCS with no trailing byte,
and embeds that value. `receipt_sha256` is the SHA-256 of those normalized JCS
bytes. `selection_sequence` must name the final `selection_chain` entry in
that snapshot, and `selection_sha256` is the SHA-256 of that entry's exact JCS
bytes. The named entry's profile binding must equal the register context.
`receipt_ref` is a non-empty provenance pointer: at append time its parsed,
validated, JCS-normalized value must equal the embedded document, but replay
uses the embedded document and digests, never whatever later bytes occupy that
path. Unknown fields, an invalid #742 document, a non-final or missing
sequence, or either normalized digest mismatch fails closed. This rule does
not retroactively impose raw-byte canonical storage on #742 receipts.

Resolution never uses the current working directory. `receipt_ref` must be a
normalized workspace-relative POSIX path under the caller-supplied root; every
parent component and the final target are inspected lexically and after
containment resolution, and any symlink or non-regular target is refused. The
runtime performs the first read under the shared passport lock, embeds the
validated normalized value, then re-reads and revalidates that source
immediately before journal publication. A changed normalized whole-receipt
digest or selected-entry digest aborts with no published byte. After that CAS,
the embedded snapshot is authoritative and recovery never reopens the mutable
source path.

### 2.3 Frozen mapping demonstrations

These are synthetic contract demonstrations, not shipped family defaults,
coverage claims, or advice about how research must be conducted. The
implementation acceptance fixtures must encode at least these two materially
different mappings with canonically valid `user_authored` profiles and stage
maps.

| Demonstration profile | Applicable task-family cells in its companion map | Lawful example | Refused example |
|---|---|---|---|
| `quantitative_empirical` | `methodology` (budget 3): `alternative_design`, `alternative_measurement`, `alternative_model`, `boundary_condition`; `retrieval` (2): `disconfirming_query`; `synthesis` (3): `alternative_model`, `disconfirming_query`, `boundary_condition`; `drafting` and `review` (2 each): `alternative_model`, `boundary_condition` | an `alternative_measurement` recorded at `methodology` and later a `boundary_condition` carried to `drafting` | `rival_theory` at `methodology` when that category is absent from the bound profile/map |
| `theoretical_conceptual` | `rq_formation` (budget 3): `rival_theory`, `boundary_condition`; `retrieval` (2): `disconfirming_query`; `synthesis` (3): `rival_theory`, `disconfirming_query`, `boundary_condition`; `drafting` and `review` (2 each): `rival_theory`, `boundary_condition`; `methodology`: `intentionally_absent` with a profile-authored reason | a `rival_theory` carried from `synthesis` to `review` | any alternative row at `methodology`; the absent stage produces no placeholder |

These mappings demonstrate that empirical and non-empirical work can both
conform without sharing one mandatory list. They do not establish that the
examples fit every project in either family.

## 3. Register contract: `alternative-explanation-register/1.0`

One logical register belongs to one project and is event-sourced. The only
authoritative mutable region is an append-only `events[]` sequence; current
alternative, stage, and artifact-staleness state is a deterministic joint
projection of those events, their exact bound #743 prefixes, and the current
passport-authoritative #743 branch-link state. No mutable projection is stored
inside the register. Serialization is JSON Canonical Form.

Top level:

| Field | Req | Shape |
|---|---|---|
| `schema_version` | yes | const `alternative-explanation-register/1.0` |
| `project_ref` | yes | non-empty string equal to the bound #743 ledger's `project_ref` |
| `ledger_binding` | yes | `{ledger_version: "inquiry-branch-ledger/1.0", ledger_project_ref}` |
| `initial_context` | yes | `{profile_binding, profile_selection_receipt_snapshot, stage_map_binding, stage_map_document, stage_map_selection_receipt, ledger_head}` using the exact profile, author-confirmed companion map, and ledger tip in force when the register was created |
| `events` | yes | append-only list of the closed event objects below |

A persisted register must contain at least one event. Enabling the flag,
selecting a map, or reaching an eligible stage alone creates neither file nor
passport pointer; materialization occurs atomically with the first accepted
event.

`stage_map_binding` is `{map_id, map_version, content_sha256}`. `ledger_head`
is `{event_id, event_sha256, ledger_content_sha256}`. `event_sha256` is over
the canonical bytes of that #743 event. `ledger_content_sha256` is over the
canonical complete #743 ledger whose event list ended at exactly that event;
replay reconstructs that prefix document from the current append-only ledger
and verifies the digest. Binding only an event number is insufficient.

The initial context's profile binding must equal the #743 effective profile at
its ledger head, its profile-receipt snapshot must satisfy §2.2, and its
stage-map document and selection receipt must bind that exact profile. A bare
receipt-reference assertion is insufficient. The first register event must
carry the same ledger head as `initial_context`. Thereafter register event
heads are monotonically nondecreasing by #743 `event_id`; every head must
resolve to its exact prefix document in the current passport-authoritative
ledger. All mechanically generated events in one atomic batch carry exactly
the cause event's head.

Historical replay can verify monotonicity and exact prefix bytes but cannot by
itself prove when a write occurred. Therefore the only conforming append path
also enforces an append-time current-tip rule: under the shared passport lock
in §9 it reloads and validates `inquiry_ledger_ref`. For a register-only
append, the proposed head must equal that ledger's current tip. For a joint
ledger/register transaction, pre-disposition register events bind the
reloaded current tip and post-ledger consequences such as relink receipts bind
the staged post-append ledger tip; those are the only two heads permitted in
the batch, in that nondecreasing order, and the staged ledger must extend the
reloaded prefix. The journal records both observed old and staged new ledger
whole-document digests for ledger-changing/joint transactions, with the old
digest as a compare-and-swap precondition. A register-only transaction records
the unchanged ledger as a §9 dependency, so its observed old and effective new
digest are identical and no staged ledger exists. A changed pointer or digest
aborts and retries before any byte is published.

Event object (closed shape):

| Field | Req | Shape |
|---|---|---|
| `event_id` | yes | monotonically increasing integer, dense from 1; list order is replay order |
| `recorded_at` | yes | ISO 8601 timestamp |
| `actor` | yes | `author` \| `ai` \| `system`, constrained by §4 |
| `kind` | yes | closed enum in §4 |
| `alternative_id` | yes | stable slug, or `null` exactly for `context_rebound` and the three artifact-scoped kinds |
| `ledger_head` | yes | exact ledger prefix `{event_id, event_sha256, ledger_content_sha256}` visible to this event |
| `payload` | yes | kind-specific closed object in §4.2 |
| `prev_event_sha256` | yes | SHA-256 of the prior canonical register event; 64 zeroes on event 1 |

The register chain detects interior rewrite and reordering. Like #743, it
cannot alone detect tail truncation; the passport pointer's whole-register
digest is the separately trusted head. Replay fails closed on a missing
ledger prefix, project mismatch, non-dense id, bad hash, invalid transition,
unknown field, or invalid cross-file reference.

An alternative projection contains:

- stable `alternative_id`, immutable `origin_branch_ref`, and current
  `branch_ref` (each `{branch_id, creation_event_id}`);
- immutable category and provenance origin;
- append-only formulation history;
- `current_task_family_id` plus cross-stage history;
- lifecycle `active | parked | reopened | merged | archived`;
- assessment `unresolved | supported | ruled_out | not_applicable`;
- current evidence anchors, typed `relevance_refs`, reopen conditions, and
  first-degree `downstream_refs`;
- author-disposition history and `merged_into`, when applicable; and
- derived profile-context state `current | profile_context_changed |
  profile_ineligible`, derived branch-link state `live |
  temporarily_inactive | merged_terminal | archived_terminal`, and
  `pending_budget_disposition: boolean`.

Each branch reference's `creation_event_id` must identify the #743
`branch_created` or `facet_surfaced` event that created its `branch_id`.
`origin_branch_ref` is immutable. A later `alternative_relinked` may change
the current `branch_ref` while preserving the origin and branch-link history.
At creation/adoption/activation/carry time the current branch must be
author-owned (`author_originated` or `author_adopted`) and live (`active` or
`reopened`) at the event's bound ledger head. An unadopted #743 facet cannot
own a register alternative.

## 4. Event kinds and state machine

| `kind` | Actor | Frozen effect |
|---|---|---|
| `alternative_created` | author | Creates an author-originated alternative, `active` + `unresolved`, at one lawful stage/category cell when budget is available. |
| `alternative_proposed` | author | Durably records an overflowing author-originated proposal as `parked` + `unresolved`, with `pending_budget_disposition: true`; it is not usable or budget-counted until activated. |
| `alternative_surfaced` | ai | Creates one trigger-bound AI-surfaced candidate, `parked` + `unresolved`; it is not author-owned, live, or author-budget-counted and is subject to the §8 candidate cap. |
| `alternative_adopted` | author | Origin-bound adoption receipt; when budget is available the AI candidate becomes `author_adopted`, `active` + `unresolved`. |
| `alternative_adoption_proposed` | author | Durably records the same adoption receipt when activation would overflow; provenance becomes `author_adopted`, lifecycle remains `parked`, and `pending_budget_disposition` becomes true. |
| `alternative_activated` | author | After required merge/park/archive dispositions, moves an author-owned pending proposal from `parked` to `active` + `unresolved` and clears the pending flag. |
| `alternative_rejected` | author | Explicitly rejects an unadopted AI candidate; lifecycle becomes terminal `archived` without converting it to `ruled_out`. |
| `alternative_reformulated` | author | Appends a new author formulation without erasing provenance or prior text, resets assessment to `unresolved`, and emits first-degree stale marks for current dependents. |
| `alternative_annotated` | author | Replaces exactly one of `evidence_anchors`, `relevance_refs`, `reopen_conditions`, or `downstream_refs` wholesale with different bytes. An evidence-anchor replacement resets assessment to `unresolved` and emits first-degree stale marks for current dependents. |
| `alternative_carried` | author | Moves an `active` author-owned alternative to a different lawful task family, appends the prior stage snapshot, and resets current assessment to `unresolved`; evidence history is retained. |
| `alternative_assessed` | author | From `active \| reopened` + `unresolved`: `supported` becomes `active`; `ruled_out` or `not_applicable` becomes `parked`. A parked row cannot bypass reopening through assessment. |
| `alternative_parked` | author | `active \| reopened` to `parked`, retaining the current assessment and a reason. |
| `alternative_reopened` | author | A parked alternative, or an active `supported` alternative contradicted by new evidence, becomes `reopened` + `unresolved` at a lawful task family; fires §7 invalidation. |
| `alternative_reconfirmed` | author | Rebinds an otherwise unchanged alternative to the current profile/map context after `context_rebound`; lawful only in an eligible cell and never clears artifact stale causes. |
| `alternative_merged` | author | `active \| reopened` to terminal `merged`, naming a live target on the same branch, task family, and category; target lists are concatenated then identifier-deduplicated, preserving order. |
| `alternative_archived` | author | Any non-terminal author-owned alternative to terminal `archived`, with reason. |
| `alternative_relinked` | author | After the current #743 branch is merged, relinks a non-terminal author-owned alternative to that exact live merge target, preserving its origin branch, resetting assessment to `unresolved`, and firing §7 invalidation. |
| `reopen_condition_signal` | ai | On a state from which reopen is lawful, records that evidence appears to satisfy one stored condition; changes no state and only opens the compact author decision surface. |
| `context_rebound` | author | Binds either the exact profile correction already recorded in #743 plus a matching map, or a map-only correction under the unchanged effective profile; existing alternatives become context-stale until reconfirmed or disposed. |
| `artifact_marked_stale` | system | Records one first-degree stale cause generated by `alternative_reopened`, `alternative_reformulated`, an evidence-anchor `alternative_annotated`, `alternative_relinked`, or `context_rebound`. |
| `artifact_reconfirmed` | author | Resolves exactly one named register stale cause as still valid. |
| `artifact_superseded` | author | Resolves exactly one stale cause with a named replacement and updates matching register `downstream_refs`. |

Any transition not listed is invalid. `merged` and `archived` are terminal.
Reintroducing a rejected/archived idea creates a new `alternative_id` and
retains its own provenance; terminal history is never rewritten.

Merge concatenates the target's then source's `evidence_anchors`,
`relevance_refs`, `reopen_conditions`, and `downstream_refs`. Identical
stable-id objects are deduplicated; the same stable id attached to different
bytes makes the merge invalid; string artifact refs are deduplicated by exact
value. Formulation histories remain on their original alternatives, and the
source retains only its terminal pointer to the target.

Lawful lifecycle/assessment combinations are closed:

- unadopted AI candidates: `parked` + `unresolved` only;
- pending author proposals/adoptions: `parked` + `unresolved` with
  `pending_budget_disposition: true`; they cannot be used downstream;
- `active`: `unresolved | supported`;
- `reopened`: `unresolved` only, until assessed, parked, merged, or archived;
- `parked`: any assessment; and
- `merged | archived`: the final assessment is retained for history.

### 4.1 Closed source-to-target transition matrix

In addition to the effects above, replay applies these source guards. No-op
events do not escape them, and `merged` / `archived` accept no later
alternative-scoped event.

| Event | Required source | Required context/branch | Target |
|---|---|---|---|
| `alternative_created` | id absent | current eligible cell; author-owned live branch; post-event §8 count is lawful | active/unresolved, not pending |
| `alternative_proposed` | id absent | current eligible cell; author-owned live branch; direct creation would overflow | parked/unresolved, pending |
| `alternative_surfaced` | id absent | current eligible cell; author-owned live branch; lawful trigger and candidate-cap room | unadopted parked/unresolved |
| `alternative_adopted` | unadopted parked candidate | current eligible cell; linked branch live; post-event §8 count is lawful | author-adopted active/unresolved |
| `alternative_adoption_proposed` | unadopted parked candidate | current eligible cell; linked branch live; direct adoption would overflow | author-adopted parked/unresolved, pending |
| `alternative_activated` | author-owned parked/unresolved, pending | current eligible cell; linked branch live; post-event §8 count is lawful after dispositions | active/unresolved, not pending |
| `alternative_rejected` | unadopted parked candidate | any readable profile context | archived/unresolved |
| `alternative_reformulated` | author-owned active/reopened/parked, not pending | current eligible context and live branch | lifecycle retained; assessment unresolved; stale batch |
| `alternative_annotated` | author-owned non-terminal, not pending | current context and live branch; replacement differs | lifecycle retained; non-anchor field retains assessment, evidence-anchor field resets it to unresolved and emits stale batch |
| `alternative_carried` | author-owned active, not pending | current context and live branch; different destination cell eligible; post-event §8 count is lawful | active/unresolved at destination |
| `alternative_assessed` | author-owned active/reopened + unresolved, not pending | current context and live branch | supported→active; ruled-out/not-applicable→parked |
| `alternative_parked` | author-owned active/reopened | any readable context, including branch/context reconciliation | parked; assessment retained |
| `alternative_reopened` | author-owned parked, or active/supported, not pending | current eligible context and live branch; post-event §8 count is lawful | reopened/unresolved; stale batch |
| `alternative_reconfirmed` | author-owned non-terminal with `profile_context_changed` | eligible under current map; linked branch live; post-event §8 count is lawful | lifecycle/assessment retained; profile context current |
| `alternative_merged` | author-owned active/reopened source and live target | both current, same current branch/stage/category; branch live | source terminal merged; target remains live |
| `alternative_archived` | author-owned non-terminal, including pending/stale/inactive | any readable context | terminal archived |
| `alternative_relinked` | author-owned non-terminal, not pending, with `merged_terminal` branch link | named #743 merge event maps the exact source branch to the exact author-owned live target; current cell remains eligible; post-event §8 count is lawful | current branch becomes target; lifecycle retained; assessment unresolved; stale batch |
| `reopen_condition_signal` | author-owned parked, or active/supported, non-terminal, not pending | current stored condition; branch not terminal | no state change |
| `context_rebound` | register context differs from proposed exact context | variant-specific §6 guards | all non-terminal entries context-stale; stale batch |
| `artifact_marked_stale` | exactly the next mechanically expected row after a stale-causing event | cause id/kind, artifact ref, order, and ledger head all match §7 | one outstanding cause added |
| `artifact_reconfirmed` / `artifact_superseded` | named register stale cause outstanding | exact artifact and cause match | exactly that cause resolved |

A #743 branch changing to `parked` or `rejected` derives
`temporarily_inactive`; its alternatives remain readable but cannot be used,
carried, assessed, merged, or newly annotated until the branch reopens. A
branch `merged` or `archived` derives the corresponding terminal link state.
An active/reopened author-owned alternative on either terminal link may be
parked. A non-pending author-owned alternative on a merged source may instead
be relinked to the exact #743 merge target; any author-owned non-terminal entry
may be archived. A parked, non-pending entry may remain immutable history, but
no terminal-linked entry may be used or otherwise edited. A pending entry on a
terminal link may only be archived. An unadopted candidate on either terminal
branch may remain historical or receive `alternative_rejected`, after which it
is terminal history. A linked-branch reopen is subject to the joint §8–§9
preflight before publication.

### 4.2 Frozen payload shapes

All lists below are ordered, duplicate-free by their stable identifier, and
may be empty unless a rule states otherwise.

| `kind` | Closed `payload` shape |
|---|---|
| `alternative_created` / `alternative_proposed` | `{branch_ref, category, task_family_id, author_formulation, evidence_anchors, relevance_refs, reopen_conditions, downstream_refs}` |
| `alternative_surfaced` | `{branch_ref, category, task_family_id, surfaced_text, trigger_snapshot}` |
| `alternative_adopted` | `{source_event_id, surfaced_text, adoption_action: "author_explicit_adopt", interaction_ref, author_formulation}` |
| `alternative_adoption_proposed` | `{source_event_id, surfaced_text, adoption_action: "author_explicit_adopt", interaction_ref, author_formulation}` |
| `alternative_activated` | `{reason}` |
| `alternative_rejected` | `{rejection_action: "author_explicit_reject", interaction_ref, reason}` |
| `alternative_reformulated` | `{author_formulation, reason}` |
| `alternative_annotated` | `{field: "evidence_anchors" \| "relevance_refs" \| "reopen_conditions" \| "downstream_refs", value: full replacement list}` |
| `alternative_carried` | `{from_task_family_id, to_task_family_id, reason}` |
| `alternative_assessed` | `{status: "supported" \| "ruled_out" \| "not_applicable", reason}` |
| `alternative_parked` / `alternative_archived` | `{reason}` |
| `alternative_reopened` | `{task_family_id, reason, condition_id?, evidence_pointer?, signal_event_id?}` |
| `alternative_reconfirmed` | `{reason}` |
| `alternative_merged` | `{merged_into, reason}` |
| `alternative_relinked` | `{from_branch_ref, to_branch_ref, ledger_branch_merged_event_id, reason}` |
| `reopen_condition_signal` | `{condition_id, evidence_pointer}` |
| `context_rebound` profile variant | `{cause: "profile_rebound", profile_binding, profile_selection_receipt_snapshot, stage_map_binding, stage_map_document, stage_map_selection_receipt, ledger_profile_rebound_event_id}` |
| `context_rebound` map-only variant | `{cause: "stage_map_rebound", profile_binding, stage_map_binding, stage_map_document, stage_map_selection_receipt, reason}` |
| `artifact_marked_stale` | `{artifact_ref, cause_event_id, cause_kind: "alternative_reopened" \| "alternative_reformulated" \| "alternative_annotated" \| "alternative_relinked" \| "context_rebound"}` |
| `artifact_reconfirmed` | `{artifact_ref, resolves_stale_event_id, note}` |
| `artifact_superseded` | `{artifact_ref, resolves_stale_event_id, note, replaced_by}` |

`author_formulation`, every reason, and every pointer are non-empty strings;
every SHA-256 field is exactly 64 lowercase hexadecimal characters.
An evidence anchor is
`{anchor_id, evidence_pointer, relation, origin, note}`, where `relation` is
`supports | challenges | bounds`, `origin` is
`author_supplied | ai_surfaced | pipeline_artifact`, and the origin is
immutable. A typed relevance reference is
`{relevance_id, ref_id, ref_type, relation}`, where `ref_type` is
`declared_contribution | evidence` and `relation` is
`addresses | challenges | bounds`. `ref_id` is an opaque stable artifact id,
not a path. A reopen condition is
`{condition_id, statement, evidence_pointer?}`. `downstream_refs` are opaque,
stable artifact identifiers, not filesystem paths.

Anchor and relevance ids are unique per alternative. A replacement may retain
an id only when the complete object is byte-identical; a removed id is retired
forever and cannot be rebound to different evidence, relation, origin, or
type. Reopen-condition identity follows the same no-rebind/no-reuse rule in
§7. Merge unions the source histories and retirement sets; an id collision
with different bytes is invalid. Every `alternative_annotated` replacement
must differ from the current list. Replacing `evidence_anchors` may yield an
empty list because assessment is atomically reset to `unresolved`; it also
fires the complete §7 stale batch over the pre-event downstream refs.

`supported` and `ruled_out` assessments require at least one current evidence
anchor. This is an inspectability requirement, not validation that the anchor
is true or adequate. `not_applicable` requires its non-empty reason but does
not require an evidence anchor.

For `alternative_reopened`, `condition_id` may appear only with an
`evidence_pointer` and must name a current condition. Reopening an active
`supported` alternative requires `evidence_pointer`; a parked alternative may
be reopened from an author reason alone. `signal_event_id`, when present, must
name a prior signal on this alternative and requires both fields to byte-match
that signal; it is forbidden when either field is absent. A carried-stage
snapshot is the deterministic pre-event projection of task family, current
formulation event id, assessment, and the ordered anchor/relevance/condition/
downstream-ref ids; it is derived, not supplied in the payload.

## 5. Provenance, adoption, and explicit author disposition

AI may emit only `alternative_surfaced` and `reopen_condition_signal`.
System may emit only `artifact_marked_stale`. Every creation or durable
proposal of an author-owned alternative, adoption or pending adoption,
activation, rejection, assessment, park, reopen, merge, relink, archive,
context rebind, and stale resolution is an author event.

The adoption receipt is origin-bound:

- `source_event_id` identifies the `alternative_surfaced` event that created
  the same `alternative_id`;
- `surfaced_text` is retained byte-for-byte;
- `adoption_action` is exactly `author_explicit_adopt` and `interaction_ref`
  names the structured author interaction that submitted the action;
- `author_formulation` is non-empty and not byte-identical to
  `surfaced_text`; and
- provenance changes from `ai_surfaced_candidate` to `author_adopted`, never
  to `author_originated`.

The same receipt rules apply to `alternative_adoption_proposed`; only its
activation is deferred. `alternative_id` is exactly `alt-` plus the next
base-10 creation ordinal without leading zeroes; the deterministic append
runtime mints it and neither AI nor author payload may supply it. AI surfacing
is appendable only when its payload binds either an explicit author-request
receipt or a contradiction already recorded by an existing evidence surface.
Eligibility alone never authorizes generation.

`trigger_snapshot` has the closed shape
`{trigger_ref, trigger_sha256, trigger_document}`. `trigger_document` is one
canonical `alternative-trigger/1.0` object with the common fields
`{schema_version, trigger_kind, trigger_id, project_ref, task_family_id,
recorded_at}` and exactly one of these closed variants:

- `trigger_kind: "author_request"` adds `{actor: "author", interaction_ref}`;
  or
- `trigger_kind: "recorded_contradiction"` adds
  `{actor: "system", source_surface_ref, contradiction_statement,
  evidence_refs}`; `evidence_refs` is a non-empty, duplicate-free list of
  opaque refs sorted by unsigned UTF-8 bytes.

At append time `trigger_ref` must resolve, under the caller-supplied workspace
root, to a contained regular non-symlink canonical JSON artifact registered by
the current interactive author-receipt store or a passport-authoritative
evidence surface. Its exact bytes must equal the embedded document's JCS
bytes and hash to `trigger_sha256`; project and task family must match the
event. The author-request artifact must have been written by the structured
request interaction, and the contradiction artifact by the named existing
evidence surface. A free-form producer string, an unregistered file, or a
digest without resolvable exact bytes is refused. Historical replay verifies
the embedded bytes and digest, so later source-file evolution cannot rewrite
the trigger. Like the profile receipt, the source is re-read under the shared
lock immediately before journal publication and its exact JCS digest must
still match; recovery thereafter relies only on the embedded snapshot. The
implementation PR must provide the closed trigger schema and two resolver
fixtures before AI surfacing can be enabled.

At each task family, current unadopted candidates are capped at that cell's
`alternative_budget`; reaching the cap refuses another AI event without
dropping or auto-archiving an existing candidate. This candidate count is
closed: provenance is `ai_surfaced_candidate`, lifecycle is `parked`, current
task family is the counted cell, profile-context state is `current`, and the
branch-link state is `live` or `temporarily_inactive`. A terminal-linked or
context-stale candidate is historical and cannot be adopted; it may still be
explicitly rejected. Keeping temporarily inactive candidates in the count
prevents a park/reopen cycle from bypassing the cap.

A bare acknowledgement is not adoption: no free-chat text, regardless of
case, punctuation, spacing, language, or Unicode form, is interpreted through
an acknowledgement lexicon. Only the explicit structured adopt action plus
its separately submitted non-empty formulation can emit an adoption event.
Rejection analogously requires the exact structured action token
`author_explicit_reject` and its `interaction_ref`. Before adoption, a
candidate cannot be assessed, annotated, carried, merged, used in downstream
prompts as the author's position, or assigned dependent artifacts. It is
rendered with its AI provenance wherever it appears. Rejection is a distinct
author receipt; it is not evidence-based `ruled_out` and does not launder the
candidate into scholarly ownership.

No event contains a score, rank, recommendation probability, or “best
alternative” field. Rendering uses the fixed status-group order
`reopened`, `active`, `pending`, `parked`, `unadopted`, `historical`, then
UTF-8-byte lexical order of `(task_family_id, category, alternative_id)`
within a group. The UI labels this as canonical identifier order, not merit
order. Runtime-minted ids and this ordering prevent the renderer from
presenting producer sequence as a merit ranking; they do not claim to remove
ordinary position effects, which remain part of the §11 burden evaluation.

Durable author and AI strings retain their exact bytes, but no such string is
rendered as control syntax. Every compact, action, signal, CLI, Markdown, and
terminal line begins with renderer-owned
`[status=<closed-status>; provenance=<closed-provenance>]`, followed by a
delimiter and only then data text. The one-line data renderer applies this
closed transform: map every Unicode whitespace run (including CR/LF and line
separators) to one U+0020 and trim it; replace every remaining Unicode `Cc` or
`Cf` scalar, including ANSI escape and bidi controls, with visible
`U+<uppercase-hex>`; replace each ASCII scalar in the exact set
``\\ ` * _ { } [ ] ( ) < > # + - . ! | &`` with its visible `U+00XX`
token; and consume at most 160 source scalars before appending a visible
ellipsis. Stable ids,
artifact refs, formulations, evidence pointers, and signal text all pass the
same transform. Full raw text remains available only through an escaped detail
view. Prefix fields come only from validated enums and cannot be supplied or
overridden by event text; signal/action lines are not exceptions.

## 6. `not_applicable` and profile correction

The canonical assessment token is `not_applicable`. The issue prose's
`inapplicable` spelling is not an alias and is refused, preventing two durable
states with the same meaning.

`not_applicable` means: **this already named alternative does not apply to
this branch at this task family under the current, author-bound context**. It
does not mean that the profile's category is absent, that no alternative
exists, or that every project in the family should omit it. It is created
only by an explicit author assessment with a reason, becomes parked, is
visible as history or a folded count, and never generates a placeholder in
another stage.

Profile-level absence is different:

- a #742 `intentionally_absent` task family or companion-map
  `intentionally_absent` cell permits no new entry there;
- an omitted or `unresolved_fit` cell permits no inferred entry or prompt;
- a profile-declared empty alternative-category list materializes no
  register; and
- a category absent from the companion map is refused, not recorded as a
  mandatory `not_applicable` row.

When #743 records a profile correction, the register cannot silently keep
using the old context. Until an author `context_rebound` binds the exact new
profile and a matching author-confirmed companion map, loading the register
yields visible `REGISTER-CONTEXT-RECONCILIATION-REQUIRED`; historical data
stays readable, but no event other than that reconciliation or an explicit
park/archive disposition is accepted.

The profile-rebound variant is valid only when all of these replay invariants
hold:

1. `ledger_profile_rebound_event_id` names a #743 `profile_rebound` event in
   the exact ledger prefix bound by this register event;
2. it is the latest #743 profile-rebound event at that head, and the head is at
   or after it;
3. its three profile identity fields are byte-equal to `profile_binding` and
   its `selection_receipt_ref` is byte-equal to the embedded
   `profile_selection_receipt_snapshot.receipt_ref`; the snapshot passes §2.2
   and its selected entry binds that exact profile;
4. replaying that ledger prefix yields the same effective profile binding;
5. the embedded stage-map document binds that profile and its selection
   receipt passes §2.2; and
6. the projected context differs from the prior register context.

A stage map may be corrected or renewed without manufacturing a no-op #743
profile correction. The map-only `context_rebound` variant requires the
profile binding to remain byte-equal to both the prior register context and
the effective profile at the event's current-tip ledger head; the embedded
map binding must differ, bind that same profile, and carry a new valid §2.2
author receipt. Reusing one `(map_id, map_version)` with different content is
always invalid; when `map_id` is unchanged, `map_version` must change. The
map-only variant contains no ledger profile-event id or profile-selection
receipt snapshot. These two closed variants are the only lawful context
changes.

Either rebound marks existing non-terminal entries
`profile_context_changed`; terminal entries remain immutable history. A
non-terminal cell the new context disallows is instead `profile_ineligible`;
it remains history and may be parked or archived, but cannot be reconfirmed,
carried, or used downstream. No `not_applicable` row is manufactured from
that change. The passport pointer's `stage_map_binding` must always equal the
latest projected context, so pointer/register disagreement is a load error.

An eligible entry returns to `current` only through
`alternative_reconfirmed`. That event does not clear the stale state #742
assigns to stage outputs or any register stale cause; artifact reuse remains
a separate author decision. Because rebound makes every non-terminal entry
context-stale, the rebound event itself has a post-event alternative count of
zero even when the new map lowers a cell budget. Each later
`alternative_reconfirmed` is independently refused once the new cell budget
would be exceeded; correction never requires destructive pre-disposition.

## 7. Reopen conditions and first-degree invalidation

Reopen-condition identity follows #743 exactly: ids are unique per
alternative; a replacement may retain an id only with byte-identical
statement text; a removed id is retired forever. An AI signal names exactly
one stored condition and an evidence pointer, changes no state, and cannot
decide that the condition is met. Only the author can reopen.

Applying `alternative_reopened`, `alternative_reformulated`,
`alternative_relinked`, or an `alternative_annotated` event whose field is
`evidence_anchors` emits one `artifact_marked_stale` event for every current
`downstream_refs` identifier on that alternative. The anchor replacement and
assessment reset are the cause event; its stale rows are mandatory even if the
new anchor list is non-empty. Applying `context_rebound` emits the same for the
ordered union of first-degree refs held by non-terminal entries under the prior
context. Generated stale events
immediately follow their cause in ascending unsigned UTF-8-byte order of
`artifact_ref`, carry exactly the cause event's `ledger_head`, and form one
atomic register append batch; replay rejects a missing, extra, reordered,
head-mismatched, or non-contiguous generated event. This byte collation, not
locale or Unicode normalization, governs every “ordered union” in v1.

Staleness is visible and non-destructive. Nothing is rewritten, deleted, or
regenerated automatically. Per artifact, the projection is the set of
outstanding `(register, artifact_marked_stale event_id)` causes. An artifact
remains stale while any register cause, #743 ledger cause, or other pipeline
cause remains unresolved. Each reconfirm/supersede event resolves one exact
register cause. Supersession replaces the old ref in each matching non-terminal
register entry's current `downstream_refs`; terminal entries retain the old ref
as immutable history. It does not mutate the separate #743 ledger, whose own
reference requires its own event.

The claim is intentionally first-degree. Transitive artifact-to-artifact
dependency propagation belongs to the pipeline artifact model and is out of
scope for v1.

Outstanding invalidation is never reduced to an unreachable `+N more` count.
Every compact surface that reports stale state shows a trusted
`[STALE-DETAILS: register_sha256=<digest> offset=0 total=<count>]` handle and
the first detail page inline. Detail rows are the complete set of
`(artifact_ref, artifact_marked_stale event_id)` pairs, ordered by unsigned
UTF-8 bytes of `artifact_ref` and then numeric event id, in fixed pages of 20.
Each row renders as a §5-safe data line with trusted `status=stale` and
`provenance=system`, the validated cause event id, and separate exact-id
`reconfirm` / `supersede` actions. A non-final page includes the only lawful
next cursor `{register_sha256, offset: offset + 20}`; the digest must still
equal the passport pointer when that cursor is consumed. Pages continue until
every pair has appeared exactly once. Register evolution invalidates an old
cursor visibly. There is no aggregate clear action, and a folded category
count never substitutes for this cause-level surface.

## 8. Stage-specific budget and interaction constraints

Two independent bounds apply and must never be conflated:

- #742 `branch_budget` retains its frozen meaning: the global count of live
  #743 branch ids. Only #743 replay enforces that number.
- The effective companion cell's `alternative_budget` is the count of live,
  author-owned #744 alternatives at that one `current_task_family_id`.

Both use the author-controlled `ask_merge_park_archive` disposition vocabulary
from #742; neither number is derived from or compared with the other.

A register alternative counts at a task-family surface only when all are
true:

1. it is author-originated or author-adopted;
2. lifecycle is `active` or `reopened`;
3. its linked #743 branch is `active` or `reopened` at the current ledger
   head;
4. profile-context state is `current`; and
5. it is not pending budget disposition.

Parked, merged, archived, unadopted, context-stale, profile-ineligible, and
alternatives whose linked branch is not live do not count. The same
alternative carried to a new stage counts only at its current stage; prior
stage snapshots are history. `alternative_created`, direct adoption,
activation, carry, reopen, reconfirmation, relink, a linked-branch reopen, or
another branch-state transition that makes the link live must not produce a
count above the effective cell's alternative budget.

An overflowing new author formulation is never held only in process memory:
the append path records `alternative_proposed`; an overflowing adoption uses
`alternative_adoption_proposed`. Both are durable parked proposals, retain
the complete author formulation and origin receipt, and remain unusable until
an `alternative_activated` event passes budget replay after the author has
merged, parked, or archived enough live alternatives. A crash or session
reset therefore cannot silently drop the proposed scholar-owned text. The
author may instead archive the proposal; no automatic pruning is lawful.

The register projection depends on current #743 branch state, so every #743
append must preflight the passport-authoritative register when its pointer
exists, even while the UI flag is dormant. This preflight has two explicit
layers. Storage integrity is unconditional: pending journal recovery,
pathname containment/alias checks, pointer presence and shape, schema,
canonical bytes, digest, project, exact ledger-prefix, and profile/map
bindings intrinsic to every stored historical context must all validate. A
valid historical binding that differs from the staged/current effective
context is semantic context drift handled by §6, not binding corruption. Any
actual integrity failure is binding-broken and blocks both active and dormant
writers; there is no implicit detach or quarantine. Only after that layer
passes does the runtime predict semantic budget, context, and terminal-link
effects. With the register active, a proposed branch reopen is
refused if it would activate too many alternatives at any stage unless a joint
author batch first parks, merges, or archives enough alternatives. A branch
merge/archive similarly offers the §4.1 terminal-link dispositions. Any
active operation that changes both files commits the ledger, register, and
passport through the common §9 transaction or publishes none of them.

Dormancy cannot create a hidden prompt or let a #744 semantic rule veto a
ledger append that is lawful under #743 and the shared storage contract. Once
the unconditional integrity layer passes, its read-only preflight permits the
ledger-only append even when the predicted post-state has a budget, context,
or terminal-link conflict. If reopening then places a task family over its
alternative budget, or a terminal branch leaves an author-owned alternative
active/reopened or pending, re-enabling the register yields
`REGISTER-BRANCH-RECONCILIATION-REQUIRED`. History is readable.
For a live-link budget conflict, only park/merge/archive dispositions are
accepted. For a terminal link, the exact §4.1 park, archive, and (on a merged
source) non-pending exact-target relink dispositions are accepted; a terminal
unadopted candidate is already historical and may only be rejected. A parked,
non-pending terminal-linked row is lawful history and does not itself keep the
reconciliation cause open. No normal surface opens until every count and
blocking branch link is lawful. Merge/archive derives link state without
mutating the register and defers any optional relink decision.
This recoverable dormant state is not a valid active surface and cannot be
used to evade the append-time budget check on a #744 event.

The relevance input used at drafting/review is one closed canonical runtime
value: `{project_ref, task_family_id, checkpoint_ref,
declared_contribution_refs, evidence_refs, content_sha256}`. Both ref lists
contain duplicate-free opaque strings sorted by unsigned UTF-8 bytes;
`content_sha256` uses the §2 placeholder-hash procedure and the project/task
family must match the current checkpoint. Missing, malformed, or mismatched
input yields no alternative row in the compact drafting/review view and never
falls back to model-inferred relevance.

The frozen progressive-disclosure rules are:

- flag off before first materialization: no register file, pointer, prompt, or
  summary; flag off after materialization: the existing file and pointer stay
  dormant, no register UI is opened, and no register event is appended; #743
  writes still perform the read-only consistency preflight just described;
- the register also requires a valid #743 ledger pointer and a validated,
  current, author-confirmed companion stage map; it never creates a ledger
  implicitly;
- eligibility never opens a surface by itself;
- with the flag on, a compact summary appears only at a relevant
  consequential freeze in the current eligible task family, when a stored
  reopen condition is currently signalled, or when a contradiction is
  recorded by an existing pipeline evidence surface. A signal is current only
  when it is the register tip, its ledger head equals the current
  passport-authoritative ledger tip, the named condition is still current,
  and the alternative still passes every present-time guard for an author
  `alternative_reopened` decision. Any later register event, retired
  condition, terminal lifecycle/link, stale context, or ledger-tip advance
  makes the signal historical and unable to open an action surface;
- drafting and review show only alternatives that satisfy all five count
  predicates above, have assessment exactly `unresolved`, have current stage
  respectively `drafting` or `review`, and carry at least one typed
  `relevance_ref` whose `(ref_type, ref_id)` is an exact member of the
  digest-bound checkpoint input's `declared_contribution_refs` or
  `evidence_refs` set. Opaque string equality is the whole predicate: no model
  may infer semantic relevance, and `supported` alternatives are not shown in
  this unresolved view;
- the compact view has one line per live alternative up to the cell's
  `alternative_budget`, in the canonical §5 order, then one folded line of
  pending, parked, ruled-out, not-applicable, unadopted, and historical
  counts. Outstanding stale causes additionally use §7's complete paginated
  exact-id surface and cannot be represented only by that fold; every row and
  action line uses §5's trusted status/provenance prefix and safe one-line
  renderer, and no graph is default-visible;
- every interaction offers `skip`, `off`, and reset-to-simple-path without
  deleting the register, ledger, or scholar-owned artifacts; and
- no register interaction is mandatory. A simple-path task opens zero
  register surfaces even when the feature flag is on.

## 9. Storage, resume, and additive v1 introduction

The stage map may be a shipped profile companion or a user-authored workspace
artifact. The register itself is always a user-project artifact beside the
Material Passport and #743 ledger; it is never committed to the ARS
repository. Repository fixtures are synthetic or carry explicit
redistribution permission.

The passport gains one optional aggregate:

`alternative_register_ref: {register_path, register_version:
"alternative-explanation-register/1.0", content_sha256,
stage_map_binding, ledger_project_ref}`.

`content_sha256` is SHA-256 over canonical bytes of the complete register;
there is no placeholder because the digest lives only in the pointer. The
path is workspace-relative and containment-checked. The pointer is the
authority. Its `stage_map_binding` must equal the latest context projected
from the register's embedded exact map snapshots, and `ledger_project_ref`
must equal both register and #743 project references.

The aggregate is absent by omitting the key; a present
`alternative_register_ref: null` is invalid, not an absence alias. At first
materialization the caller may supply one explicit same-directory,
workspace-relative `register_path`; otherwise the deterministic default is
`<passport-basename>.alternative-explanations.json` beside the passport. Once
materialized, that path is immutable in v1. With no pointer, the runtime
examines only that explicit or deterministic candidate path and never scans by
glob, modification time, or content. An existing candidate is reported as an
orphan and is neither overwritten nor adopted.

The workspace root is always caller-supplied, never inferred from the current
working directory. Passport, ledger, register, lock, journal, and temporary
targets must be regular non-symlink paths whose resolved parents are the same
contained directory; a path escape, symlink component, cross-directory rename,
or target alias is refused before a lock or write.

### 9.1 One passport transaction domain

#744 must not ship with a second mechanism-specific passport lock or journal.
It promotes the frozen #743 physical sidecar domain to the logical shared
`ars-passport-transaction/1.0` domain. For passport basename `<P>`, every old
and new writer therefore uses #743's existing `.<P>.lock`; both journal schemas
use #743's existing `.<P>.inquiry-ledger.transaction.json` publication path
and `.<P>.inquiry-ledger.transaction.tmp` publication-temp path. The
`inquiry-ledger` spelling is an intentionally retained v1 filesystem basename,
not a statement that the new journal is ledger-only. Renaming either physical
path is deferred until cross-version support is explicitly dropped by a later
contract.

Every cooperating reader acquires that same lock and completes any intact
journal before reading the passport, ledger, or register. Under the lock, a
new runtime validates the journal envelope and dispatches only by its exact
`schema_version`: `inquiry-ledger-transaction/1.0` invokes frozen #743 legacy
recovery; `ars-passport-transaction/1.0` invokes the recovery below; any other
value is a visible fail-closed recovery error. It may publish a new journal
only after the shared path is absent following successful recovery. An older
#743 runtime uses the same lock and journal path; if it encounters a common
journal, its closed legacy validator rejects the new schema before any read or
write. Thus it cannot ignore a half-published common transaction or serialize
a stale passport snapshot. Recovery of that transaction requires a runtime
that understands the common schema.

The caller-selected workspace root and passport path are the lock-owner
authority. Before opening any sidecar, the runtime normalizes that selected
passport to its workspace-relative lexical path, validates its non-symlink
parent/target, and derives `<P>`, the lock, journal, publication temp, and all
fixed stage paths solely from that trusted path. A journal's `passport_path`
must be byte-equal to the caller-selected relative passport path. No journal
field may redirect the lock owner or choose the basename used to derive a
sidecar; a mismatch fails before any target/stage read, cleanup, or replace.

That cross-version guarantee is storage crash safety, not retroactive semantic
awareness in an older binary. A runtime predating #744's register preflight is
treated as a dormant external writer: it must preserve the unknown optional
`alternative_register_ref`, and its completed ledger-only append is checked on
the next #744-capable load. Any resulting context, budget, or terminal-link
conflict enters the corresponding recoverable reconciliation state in §§6 and
8. Such an append is not a conforming active-#744 operation and cannot support
an active-surface claim. The §14 implementation gate therefore upgrades #743's
writer to perform the §8 preflight before #744 can materialize a register; all
#744-capable writers perform it even when the UI flag is dormant.

The common journal has one ordered `targets[]` list covering exactly the files
changed by the operation and one ordered `dependencies[]` list covering every
passport-authoritative ledger/register file whose bytes are relied on but not
changed. This distinction does not weaken compare-and-swap: dependencies are
full-byte CAS inputs and are revalidated during commit and recovery.

The journal's closed top level is `{schema_version:
"ars-passport-transaction/1.0", transaction_id, passport_path,
old_passport_sha256, new_passport_sha256, old_inquiry_ledger_ref,
new_inquiry_ledger_ref, old_alternative_register_ref,
new_alternative_register_ref, preserved_passport_projection_sha256, targets,
dependencies}`. Nullable old/new pointer fields mean exact absence, not
unknown. `preserved_passport_projection_sha256` is JCS SHA-256 over the parsed
passport after removing exactly the two optional pointer keys
`inquiry_ledger_ref` and `alternative_register_ref`. Each target is
`{role: "ledger" | "register" | "passport", destination_path, staged_path,
old_sha256, new_sha256}`; each dependency is
`{role: "ledger" | "register", path, sha256}`. `transaction_id` is a non-empty
runtime-minted slug. All shapes are closed.

The role is authority; journal path strings do not choose arbitrary files.
For passport basename `<P>`, v1 computes these exact staged siblings:

- passport → `.<P>.inquiry-ledger.passport.tmp`;
- ledger → `.<P>.inquiry-ledger.ledger.tmp`; and
- register → `.<P>.inquiry-ledger.register.tmp`.

A passport target appears exactly once and has `destination_path ==
passport_path`, its fixed staged path above, and old/new digests equal to the
top-level passport digests. A ledger target or dependency path equals the
corresponding inquiry-ledger pointer path; a register target or dependency
path equals the corresponding alternative-register pointer path. Their
digests equal the pointer `content_sha256` values. Once an artifact pointer
exists, its path is immutable; v1 permits absent→present materialization but
neither move nor deletion. Thus `old_sha256` is null exactly for a newly
materialized artifact and never for the passport. A role appears at most once
across `targets` and `dependencies`.

For each artifact role, absent old+new pointers require no row; byte-identical
old+new pointers require exactly one dependency; and a lawful digest change or
absent→present transition requires exactly one target. A register-only append
therefore has register+passport targets and a ledger dependency. A ledger-only
append has ledger+passport targets and, when a register pointer exists, a
register dependency. A joint append has ledger+register+passport targets.
No other cardinality or role set is valid. Dependencies and changed
non-passport targets each sort by unsigned UTF-8 bytes of their
workspace-relative path; the passport target is always last.

Before any lock-side cleanup, stage, or replace, the runtime computes a
reserved-name key as Unicode NFD followed by case folding. The passport,
ledger/register destinations, shared lock, journal, journal-publication temp,
and all three fixed stage paths must be pairwise distinct under that key and
must have the same contained, resolved, non-symlink parent. Every live or
staged object is a regular non-symlink file. Cleanup may unlink only one of the
three exact computed stage paths or the exact journal-publication temp after
validating that ownership relation; it never unlinks a path merely because a
journal supplied it. A duplicate role, unexpected path, alias, mutable pointer
path, pointer/digest mismatch, unknown field, or wrong order fails before the
first replacement.

All staged byte images are written exclusively to those fixed paths, flushed,
and directory-fsynced before the journal is published. Before the first
replacement, commit and recovery validate the complete prospective state:
every dependency still has its exact digest and valid canonical schema; every
staged-or-already-published ledger/register has canonical bytes, the expected
project and bindings, a valid event chain, and the pointer-bound digest; an
existing ledger/register target is a strict append-only extension of its old
generation; the staged register's ledger heads satisfy §3 against the live or
staged ledger; and the complete staged passport contains exactly the recorded
new pointers. The parsed old and staged-new passports, after removing exactly
those two pointer keys, must be recursively equal in every remaining known or
unknown key, scalar, and list order and must both hash to
`preserved_passport_projection_sha256`. Register-only operations may change
only `alternative_register_ref`; ledger-only operations only
`inquiry_ledger_ref`; joint operations only those two. No compliance,
reset-boundary, artifact, or other passport entry may be added, dropped,
rewritten, or reordered. The writer derives the new round-trip YAML tree by
copying the locked old tree and replacing only the authorized pointer keys; it
never rebuilds a whitelist of known fields. A joint staged ledger must be a
strict append-only extension of the exact old ledger, not merely another valid
ledger with a matching tip. The §8 active/dormant rules are then applied to the
predicted joint projection.

Dependencies and not-yet-replaced old generations are re-read immediately
before every replacement and again before journal removal. Recovery accepts
each target only in its recorded old or new generation, publishes every
remaining new generation idempotently in target-list order, verifies all
destination and dependency digests plus both passport pointers and the
preserved passport projection, then removes the journal and fsyncs the
directory. While the passport is still in its old generation, recovery repeats
the old/new recursive-equality check before publishing it; if it is already
the validated new generation, its non-pointer projection must still match the
journal digest. A changed dependency/old digest, unknown
target, missing staged bytes when the destination is not already the validated
new generation, or passport state outside the recorded old/new generations is
a visible recovery error; no reader guesses from modification time.

This is a logical multi-file transaction, not a claim that several pathname
replacements are one filesystem primitive. A crash after any replacement
completes from the durable journal without minting another event. The common
lock also prevents the shipped #743 writer and future #744 writer from
serializing independent stale passport snapshots and losing one another's
pointer updates.

Load states are closed (a present null aggregate is a malformed pointer, not
the absent-pointer state):

- no pointer and no register file = never materialized;
- pointer plus readable canonical file, matching digest, project, stage map,
  selection receipts, exact embedded historical map documents, monotonic
  ledger-prefix bindings, and current projected pointer fields = valid (and
  may be active or dormant according to the session flag);
- pointer without a readable digest-matching file =
  `ALTERNATIVE-REGISTER-BINDING-BROKEN`;
- missing/broken #743 pointer, project mismatch, or a register head not found
  in the ledger = `ALTERNATIVE-LEDGER-BINDING-BROKEN`;
- ledger profile changed without `context_rebound` = the recoverable,
  read-only reconciliation state in §6, not silent continuation; and
- a lawful ledger-only append made while the register was dormant that causes
  an alternative-budget or terminal-link conflict = the recoverable
  `REGISTER-BRANCH-RECONCILIATION-REQUIRED` state in §8, never a corrupt-file
  diagnosis or silent active surface.

Binding-broken errors take precedence and stop replay. Otherwise context and
branch reconciliation causes may coexist and are reported as a set, rather
than collapsed into one ambiguous status. While both are outstanding, only the
exact §6 `context_rebound` and explicit park/archive dispositions are accepted;
after the rebound, any remaining branch cause admits the full §8 disposition
set. Normal surfaces resume only when the set is empty.

An explicitly named register file without a passport pointer is ignored with
a visible orphan notice, matching #743; it is never selected by modification
time. Existing passports require no migration: absence of the optional
aggregate is the complete additive v1 introduction rule. Cross-session resume
carries the optional pointer through the same reset-boundary protocol as #743
without deleting state. Active/dormant choice is deliberately not persisted:
every new session independently reads the default-off environment/session
flag, and the mere presence of a pointer never activates the feature. Unknown
schema versions are refused.

A future v1-to-v2 migration is outside this freeze. It will require its own
design and receipt schema covering exact source/destination hashes, status
mapping, rollback/preservation, pointer transition, and common-journal crash
recovery. Until that contract exists, no spelling alias, implicit status
conversion, or in-place rewrite is authorized.

## 10. Capability registration and claim ceiling

The first structural implementation and its matrix rows must land in the
same commit. It registers mechanism `alternative_explanation_register @
alternative-explanation-register/1.0` once for every task family that the
runtime actually surfaces; a dynamic profile map is not a claim that every
task family is implemented. The initial row state is `IMPLEMENTED` only
after schema, replay, cross-file, and interaction tests are CI-gated;
behavioral evidence remains `NOT_RUN` and external outcome evidence `none`.

Required transport limits include: opt-in only; depends on exact #742 profile,
companion map, and #743 ledger bindings; within-session author attestation;
first-degree invalidation only; no human-participant usability or usefulness
evidence. The maximum licensed claim is:

> A closed, replayable substrate can preserve profile-eligible alternatives,
> explicit author dispositions, and visible first-degree invalidation as
> recorded state. It does not show that the alternatives are complete,
> correct, useful, or better than the simple path, and licenses no usability
> or research-outcome claim.

README, release-note, and issue-closing language cannot exceed that ceiling.

## 11. Evaluation boundary (`NOT_RUN`)

Evaluation is a paired human-participant comparison under #742 §8 and cannot
begin before that protocol's §8-A amendment gate is complete. The evaluated
intervention freezes the ARS release, exact profile and stage-map versions and
hashes, #743/#744 mechanism versions, model/provider, task cards, and
experience strata. ARS agents may not substitute for participants or
independent judges.

The following outcomes are reported separately, never collapsed into one
score or used to rescue a failed stratum:

- **useful follow-through**: a preregistered relevant alternative reaches its
  named downstream decision and is used there, judged under the §8-A-frozen
  rubric;
- **false alternative inflation**: surfaced or adopted alternatives that the
  task ground truth or blinded rubric judges irrelevant, reported separately
  for AI-surfaced and author-originated items;
- **inapplicable inflation**: any row, prompt, or boilerplate opened in a
  profile/map-ineligible cell, plus author-marked `not_applicable` items as a
  separate descriptive count;
- **omission**: a preregistered relevant alternative absent at its named
  downstream decision;
- **burden**: added prompts, time, abandonment, and perceived control under
  the existing #742 definitions and non-inferiority rules; and
- **recovery behavior**: signalled conditions, author reopen decisions,
  visible stale marks, and resolution completion, without treating reopen
  frequency as quality.

Task completion, decision usefulness, safety/authority regressions, and all
#742 family × experience guardrails remain separately reported as well.
Thresholds, sample size, missing-data handling, judge training, and utility
rubrics are not invented here; they are blocked on §8-A. The beta remains
opt-in until the exact research-family × release passes the parent gates.
Evidence in one family, profile/map version, or release cannot authorize
another; the parent default-on rule still requires at least three materially
different families with usability evidence, including one non-empirical
family, and no hidden subgroup safety/authority regression.

## 12. Acceptance mapping

| Issue #744 acceptance item | Where addressed | Freeze-time status |
|---|---|---|
| At least one empirical and one non-empirical profile demonstrate lawful stage mapping | §2.1–§2.3 | Normative synthetic mappings frozen; executable fixtures deferred |
| Inapplicable categories never become mandatory boilerplate | §2.1, §6, §8 | Semantics frozen; runtime test deferred |
| Evidence-triggered reopen visibly invalidates dependent artifacts | §4, §7 | Deterministic first-degree behavior frozen; implementation deferred |
| Author rejection/adoption is explicit and AI ranking is absent | §4–§5 | Receipt/state rules frozen; implementation deferred |
| Evaluation reports useful follow-through, false/inapplicable inflation, burden, and omission separately | §11 | Protocol boundary frozen; evidence `NOT_RUN` |
| No default-on change until parent research-family and usability gates pass | Status, §8, §11 | Satisfied as a design rule; no default change authorized |

This document satisfies the design-freeze prerequisite. It does not claim
that implementation- or evidence-dependent acceptance items have passed.

## 13. Non-goals

No universal rival-explanation list; no universal stage/category mapping; no
requirement that a paper retain multiple theories, methods, measures, or
models; no AI ranking or automatic adoption; no automatic reopen; no
transitive artifact dependency graph; no venue-fit or acceptance prediction;
no claim that preservation improves research; and no default-on release from
structural tests alone.

## 14. Deferred implementation

Deferred to a bounded implementation PR:

- the stage-map, trigger, register, and shared passport-transaction JSON
  schemas (including profile-receipt snapshots, fixed targets, and unchanged
  dependencies) plus their canonical validators;
- one empirical and one non-empirical synthetic mapping fixture plus negative
  profile/stage/category/budget/selection-receipt and trigger-resolver
  cross-contract cases;
- event replay, hash-chain, ledger-prefix, provenance, adoption, lifecycle,
  alternative-budget, durable-pending, branch-link, exact profile/map rebound,
  typed-relevance, evidence-anchor reassessment/invalidation, safe-rendering,
  current-signal, and incomplete-invalidation-batch tests;
- refactoring #743 and implementing #744 on the shared crash-recoverable
  ledger/register/passport transaction domain plus the passport pointer
  aggregate, fixed-path mutation matrix, unchanged-dependency CAS, and legacy
  crash-phase compatibility tests; passport mutations must separately prove
  that every non-pointer field and ordered list is semantically identical
  across add/drop/change/reorder attempts;
- upgrading every current passport reader/writer—not only #743/#744, but also
  reset/resume and other orchestrator paths—to dispatch and complete the shared
  journal under the stable sidecar lock before reading; no #744 register may
  materialize until that integration test is green;
- opt-in checkpoint/contradiction summaries with `skip`, `off`, and reset;
- stale-detail pagination tests covering exact-once cause enumeration, digest-
  bound cursor invalidation, safe rendering, and exact-id resolution actions;
- same-commit stage-capability matrix registration; and
- all human-participant evaluation work in §11, still blocked on #742 §8-A.

The future v1-to-v2 migration design and receipt schema are also deferred and
are not authorized by this v1 implementation list.
