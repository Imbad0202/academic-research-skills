# #743 — Bounded inquiry branch ledger with park, reopen, merge, and invalidation semantics

Status: DESIGN FREEZE for the `inquiry-branch-ledger/1.0` contract: schema
shape, state transitions, invalidation rules, and migration are frozen here,
satisfying the issue's design-frozen-before-implementation acceptance gate.
At the 2026-08-17 freeze this document authorized no implementation or
evaluation run, and it still authorizes no simple-path prompt or default-on
behavior. The shipped alpha is opt-in behind `ARS_INQUIRY_LEDGER=1` (default
OFF = byte-equivalent current behavior).

Implementation status (2026-08-24): the bounded alpha now ships the closed
ledger and passport-pointer schemas, a strict canonical loader and pure replay
runtime, profile-bound budget enforcement, deterministic append/invalidation
helpers, compact checkpoint views, and a crash-recoverable two-file
ledger/passport transaction. The flag remains OFF by default, state is not
materialized before a second branch exists, and all behavioral evidence stays
`NOT_RUN`.

Parent epic: #741. Roadmap: `docs/ROADMAP-v3.20.1-v3.22.md` Phase 2.
Companion freezes: #742 profile contract
(`docs/design/2026-08-17-742-research-family-profile-contract-design.md`,
whose §7 budget semantics this document consumes verbatim) and the #745
stage capability matrix (`shared/contracts/capability/`), in which the alpha
must register before shipping. Nearest measurement dependency: #659.

## 1. Problem and claims boundary

The pipeline passport carries primarily one active line of inquiry forward.
Alternatives surfaced early — and the reasons they were set aside — are not
durable first-class state, which makes early decisions path-dependent: there
is nothing to reopen when later evidence undercuts the chosen framing.

The ledger preserves **inspectable alternatives and recovery state**. It does
not establish that any alternative is novel, correct, or scientifically
valuable (#659 is the nearest ideation measurement, itself `DESIGNED` /
`NOT_RUN`), and it is a memory surface, never an instruction to maximize the
number of branches. More alternatives are not treated as better.

One boundary applies to every "author" field in this contract: the ledger
records **within-session attestations**, the same way the `/ars-mark-read`
human-read ledger does. ARS cannot cryptographically authenticate the human
behind the session; `actor: author` means "entered through the interactive
author surface", not "identity-verified". The receipts make provenance
inspectable and auditable, not forgery-proof against a hostile session.

## 2. Contract: `inquiry-branch-ledger/1.0`

One ledger is one JSON document per project, **event-sourced**: the only
authoritative mutable region is an append-only `events[]` list; everything
else — branch states, artifact-staleness states, the effective profile
binding — is a deterministic projection of the events. Replay is a pure
function; serialization is JSON Canonical Form (the Schema 9 `reset_boundary`
convention), so park/reopen/merge histories are append-only by construction
and round-trip byte-stably.

Top level:

| Field | Req | Shape |
|---|---|---|
| `schema_version` | ✓ | const `inquiry-branch-ledger/1.0` |
| `project_ref` | ✓ | string binding the ledger to its pipeline run/passport |
| `initial_profile_binding` | ✓ | `{profile_id, profile_version, content_sha256}` — immutable; the EFFECTIVE binding is a projection: the latest `profile_rebound` event, else this field |
| `events` | ✓ | append-only list of event objects (below) |

Event object (closed shape):

| Field | Req | Shape |
|---|---|---|
| `event_id` | ✓ | monotonically increasing integer, dense from 1; replay order IS list order, and a list whose ids are not dense ascending fails replay |
| `recorded_at` | ✓ | ISO 8601 timestamp |
| `actor` | ✓ | `author` \| `ai` \| `system` — who initiated the event (§1 attestation boundary); `ai` may emit only `facet_surfaced` and `reopen_condition_signal`; `system` may emit only `artifact_marked_stale`; everything else requires `author` |
| `kind` | ✓ | closed enum, §3 |
| `branch_id` | ✓ | stable slug, or `null` exactly for `profile_rebound` (ledger-scope) and the three `artifact_*` kinds (artifact-scope); new branch ids may only be introduced by `branch_created` / `facet_surfaced` |
| `payload` | ✓ | kind-specific closed object, §3.1 — unknown payload fields fail replay |
| `prev_event_sha256` | ✓ | SHA-256 of the canonical serialization of the previous event (64-zero placeholder on event 1) |

**Tamper evidence, stated precisely.** The hash chain makes interior
rewriting and reordering detectable by replay. It cannot by itself detect
truncation of the tail — that requires a separately trusted head, which is
exactly what the §7 passport pointer's ledger content digest provides. The
integrity claim is therefore: chain + passport digest together detect
rewrite, reorder, and truncation; the chain alone detects only the first two.

Branch state (projection, never stored authoritatively): `branch_id`,
`parent_id` (nullable), `provenance` (`author_originated` \|
`ai_surfaced_facet` \| `author_adopted`, §4), `assumptions[]`,
`evidence_sought[]`, `status` (`active` \| `parked` \| `rejected` \|
`reopened` \| `merged` \| `archived` — the same closed vocabulary the #742
§7 budget counts, `live` = `active` + `reopened`), latest disposition
reason,
`reopen_conditions[]` (each `{condition_id, statement, evidence_pointer?}`),
`downstream_refs[]` (artifact identifiers derived from this branch),
`merged_into` (when `merged`).

Artifact-staleness state (projection): per artifact identifier, the SET of
outstanding stale causes (each an `artifact_marked_stale` event id) plus the
resolution history. An artifact is stale while ANY cause is unresolved; a
clearing event resolves exactly the cause its `resolves_stale_event_id`
names (§5), so two branches invalidating the same artifact require two
resolutions.

## 3. Event kinds and the frozen state machine

Closed `kind` enum and transitions:

| kind | actor | Effect (frozen) |
|---|---|---|
| `branch_created` | author | new branch, `provenance: author_originated`, status `active` |
| `facet_surfaced` | ai | new branch, `provenance: ai_surfaced_facet`, status `parked` — an AI-surfaced facet NEVER enters as `active`; it waits for the author |
| `branch_adopted` | author | §4 adoption receipt; lawful only on an `ai_surfaced_facet` branch in `parked`; provenance → `author_adopted`, status → `active` |
| `branch_annotated` | author | REPLACES `assumptions` / `evidence_sought` / `reopen_conditions` / `downstream_refs` wholesale (replacement semantics, never a patch — deterministic without merge rules); no status change |
| `branch_parked` | author | `active` \| `reopened` → `parked`, with `reason` |
| `branch_rejected` | author | `active` \| `reopened` \| `parked` → `rejected`, with `reason` |
| `branch_reopened` | author | `parked` \| `rejected` → `reopened`, with `reason` and optionally the `condition_id` + evidence pointer that motivated it; lawful only on author-owned branches (`author_originated` / `author_adopted`) — an unadopted facet's only lawful exits from `parked` are `branch_adopted`, `branch_rejected`, or `branch_archived`, and a rejected or archived unadopted facet is terminal (re-proposal is a NEW `facet_surfaced`); fires §5 invalidation |
| `branch_merged` | author | `active` \| `reopened` → `merged`, with `merged_into` naming a currently-live branch and `reason`; the target's `downstream_refs` becomes target-list-then-merged-list, deduplicated by identifier, order-preserving |
| `branch_archived` | author | any non-terminal status → `archived`, with `reason`; terminal like `merged` (recovery is a NEW branch, not a reopen); archived branches never count against the budget and are excluded from summaries |
| `reopen_condition_signal` | ai | records that session evidence claims to satisfy exactly one stored `condition_id` (payload carries the evidence pointer); changes no status — the only lawful consequence is showing the §6 summary to the author, who judges the claim |
| `profile_rebound` | author | ledger-scope (`branch_id: null`); mirrors a #742 §6 profile correction; the effective binding is the projection over these events |
| `artifact_marked_stale` | system | artifact-scope; emitted mechanically as part of applying a `branch_reopened` event (§5), one per affected artifact, carrying the reopening `event_id` |
| `artifact_reconfirmed` | author | artifact-scope; clears a stale mark: "still valid under the reopened line" |
| `artifact_superseded` | author | artifact-scope; closes a stale mark by naming the replacing artifact |

Any transition not in this table is invalid; replay fails closed on an
invalid event (a corrupt ledger is an error surface, never a silently
truncated state). `merged` and `archived` are terminal. `reopened` is a distinct persistent
status — visible as "reopened, awaiting disposition" until the author parks,
rejects, or merges it — and counts against the live budget precisely so it
cannot silently accumulate.

**Budget as a replay invariant.** After applying ANY event — including
`profile_rebound` — the live count (`active` + `reopened`) must not exceed
the then-effective profile's `branch_budget`; an event whose post-state
violates this is INVALID and replay fails closed. Surfaces therefore must
obtain the #742 `ask_merge_park_archive` disposition BEFORE appending the
exceeding `branch_created` / `branch_adopted` / `branch_reopened` event, and
a rebind to a lower-budget profile is appendable only after the author has
disposed live branches down to the new budget (the interaction layer walks
the author through those dispositions first); the candidate or pending
rebind awaiting disposition exists only at the interaction layer, never as
ledger state, so the recorded ledger can never exceed the budget. (An
unadopted `facet_surfaced` enters `parked` and is budget-irrelevant, so the
AI cannot force this interaction.)

### 3.1 Frozen payload shapes

| kind | payload (closed) |
|---|---|
| `branch_created` | `{parent_id: slug\|null, statement: string, assumptions: [string], evidence_sought: [string], reopen_conditions: [{condition_id, statement, evidence_pointer?}], downstream_refs: [string]}` (lists may be empty) |
| `facet_surfaced` | `{parent_id: slug\|null, surfaced_text: string}` |
| `branch_adopted` | `{source_event_id: int (the originating facet_surfaced), surfaced_text: string (retained verbatim), author_formulation: string (non-empty, not byte-identical to surfaced_text)}` |
| `branch_annotated` | `{field: "assumptions"\|"evidence_sought"\|"reopen_conditions"\|"downstream_refs", value: full replacement list}` |
| `branch_parked` / `branch_rejected` / `branch_archived` | `{reason: string}` |
| `branch_reopened` | `{reason: string, condition_id?: string, evidence_pointer?: string}` |
| `branch_merged` | `{merged_into: slug, reason: string}` |
| `reopen_condition_signal` | `{branch_id_ref: slug, condition_id: string, evidence_pointer: string}` (event-level `branch_id` carries the same slug) |
| `profile_rebound` | `{profile_id, profile_version, content_sha256, selection_receipt_ref: string}` |
| `artifact_marked_stale` | `{artifact_ref: string, reopening_event_id: int}` |
| `artifact_reconfirmed` / `artifact_superseded` | `{artifact_ref: string, resolves_stale_event_id: int (the artifact_marked_stale event being resolved), note: string}` + (`superseded` only) `{replaced_by: string}` |

## 4. Provenance and the adoption receipt

Only author-expressed or explicitly author-adopted framings become scholarly
branches. The frozen rules:

- provenance history is immutable: `author_adopted` records that the branch
  ENTERED as `ai_surfaced_facet`; nothing can relabel it `author_originated`;
- the adoption receipt binds to its origin: `source_event_id` must name the
  `facet_surfaced` event that created this branch (replay verifies), the
  original `surfaced_text` is retained verbatim, and `author_formulation`
  must be non-empty and not byte-identical — a bare "ok" is not an adoption;
- per §1, the receipt is a recorded within-session attestation, not an
  authentication — the guarantee is that adoption is always an explicit,
  inspectable, origin-bound record, never an implicit promotion;
- an unadopted `ai_surfaced_facet` never appears in any downstream prompt as
  the author's position, and consumers must render its provenance label
  wherever the branch is shown;
- unadopted facets sit in `parked`, outside the live budget (§3), so the AI
  cannot exhaust the author's budget or trigger disposition prompts.

## 5. Reopen and invalidation semantics

`reopen_conditions[]` are author-owned declarative statements with stable
`condition_id`s ("reopen if the measurement invariance test fails",
optionally pointing at an evidence row). Identity is replay-enforced:
`condition_id`s are unique per branch; a `branch_annotated` replacement may
keep an existing id only with a byte-identical `statement` (rebinding an id
to new text is invalid), and a removed id is retired permanently — it can
never be reused on that branch, so a recorded signal always denotes exactly
one historical condition text. The AI may record a
`reopen_condition_signal` naming exactly one `condition_id` when session
evidence claims to satisfy it; **judging the claim and reopening are always
author actions**. A signal remains historical evidence, not a perpetual UI
trigger: the signal-moment surface is lawful only while that exact condition
is still in the branch's current `reopen_conditions[]` and the branch is
presently eligible for `branch_reopened` (`parked` or `rejected`, with
`author_originated` or `author_adopted` provenance). The action line prefixes
the signal with that trusted current status/provenance pair. Removing the
condition, reopening/archiving/merging the branch, or leaving it as an
unadopted AI facet closes the surface without rewriting the event history.

Applying `branch_reopened` mechanically emits one `artifact_marked_stale`
event per identifier in the reopened branch's own `downstream_refs[]` (actor
`system`, carrying the reopening `event_id`), so invalidation is itself
event-sourced and replay reproduces the full stale/clear history. Scope,
stated honestly: the ledger marks **first-degree** derived artifacts — the
ones the author recorded against the branch. Artifact→artifact dependency
tracking is the pipeline's artifact model, not ledger state, and transitive
propagation is explicitly out of scope of v1; the visible stale mark on the
first-degree artifact is the handle the pipeline surfaces from.

Stale marking is visible and non-destructive: nothing is rewritten, deleted,
or regenerated automatically. Each stale cause clears only through
`artifact_reconfirmed` ("still valid under the reopened line") or
`artifact_superseded` (named replacement), whose `resolves_stale_event_id`
binds the resolution to one specific cause — an artifact stays stale while
any other cause remains outstanding. Applying `artifact_superseded`
additionally replaces `artifact_ref` with `replaced_by` in the
`downstream_refs` of EVERY branch that lists it (first-degree link
maintenance, part of the event's deterministic effect — distinct from the
excluded transitive tracking), so the next reopen invalidates the current
artifact, not the retired one. This is the same stale-not-rewritten
discipline the #742 §6 profile correction uses.

## 6. Interaction constraints (opt-in alpha)

- `ARS_INQUIRY_LEDGER` unset or `0`: no ledger file, no prompt, no summary —
  byte-equivalent current behavior. With the flag on, the linear path also
  remains available: no ledger file or passport pointer exists until a
  second branch is recorded (§7 defines both absence states).
- With the flag on, a compact branch summary (one line per live branch;
  parked/rejected counts folded into a single trailing line) appears at
  exactly two moments: a consequential freeze (the Stage 1 design-freeze
  checkpoint and the Stage 2.5 / 4.5 MANDATORY checkpoints) and when a
  `reopen_condition_signal` names a stored `condition_id` (the author judges
  the claimed satisfaction), subject to the current-condition/current-reopen
  eligibility rule in §5. Nowhere else. All event-carried display strings use
  the same deterministic one-line control/Markdown escaping and 160-character
  display bound. Stale artifacts are never count-folded: every stale
  `artifact_ref` receives its own bounded line and every outstanding cause
  event id receives its own line until individually resolved.
- Budget: the #742 §7 semantics verbatim, enforced as the §3 replay
  invariant — the ledger can never record more live branches than the
  effective profile's budget, and the only overflow behavior is
  `ask_merge_park_archive`.
- Every ledger interaction offers `skip`, `off` (sets the flag's session
  state to off), and reset-to-simple-path; none of these discards
  scholar-owned work (the ledger file persists; only the surfaces stop).
- Simple-path users — flag off, or flag on with ≤ 1 branch — receive **zero**
  additional mandatory prompts (acceptance item, test-pinned at
  implementation time).

## 7. Storage, migration, and data boundary

The ledger is a **user-project artifact**: it lives beside the Material
Passport in the user's workspace, is never committed to the ARS repository,
and committed test fixtures are synthetic-only (roadmap repository data
boundary). The passport references it through one optional aggregate:

- field `inquiry_ledger_ref`: `{ledger_path: workspace-relative path,
  ledger_version: "inquiry-branch-ledger/1.0", content_sha256}` —
  `content_sha256` is defined exactly as SHA-256 over the JSON Canonical
  Form serialization of the entire ledger document — no placeholder step,
  because the ledger embeds no self-digest (the digest lives only in this
  pointer) and nested hashes (profile bindings, event chain) are hashed as
  ordinary content; consumers reject non-canonically-stored ledgers; this
  digest is the trusted head that closes the §2 truncation hole;
- ledger writes are atomic (write-temp, fsync, rename) and every write
  updates the pointer digest in the same passport transaction;
- absence semantics are closed: no pointer AND no file = feature off or not
  yet materialized (both lawful); pointer without a readable, digest-matching
  file = `LEDGER-BINDING-BROKEN`, a visible load error, never a silent
  continue; a file without a pointer is ignored with a visible notice (the
  passport is the authority).

**Implementation clarification — cross-file crash consistency.** “The same
passport transaction" is a logical transaction, not a claim that two pathname
replacements are one filesystem primitive. The runtime uses the stable adjacent
`.<passport-basename>.lock` sidecar shared with the reset-boundary protocol,
plus a durable recovery journal that binds both staged byte images and their
destination hashes. Cooperating readers finish an intact
journal idempotently before loading either file. A crash after one rename can
therefore complete without minting a second event or silently accepting a
mismatch. If no valid recoverable journal exists, the §7 absence rules remain
authoritative: a digest mismatch is `LEDGER-BINDING-BROKEN`, and an explicitly
named candidate file without a pointer is ignored with a visible orphan
notice. The workspace root is always caller-supplied; `ledger_path` is resolved
relative to that root, must remain contained, and the ledger must be beside
the passport rather than inferred from the current working directory.

Replay also requires the exact profile documents named by the initial binding
and every `profile_rebound`. A binding alone does not carry `branch_budget`, so
an unresolved `{profile_id, profile_version, content_sha256}` fails closed;
the runtime never substitutes the currently shipped fallback for missing
historical profile bytes.

The 2026-08-24 reset-boundary concurrency amendment makes this stable sidecar
the lock domain for every current ARS passport writer. A pre-amendment writer
that locks the replaceable passport inode is not concurrency-compatible and
must not run alongside the alpha; acquiring both locks cannot bridge an inode
rename. This is an explicit mixed-version exclusion, not a safety claim about
non-cooperating writers.

Absolute and relative ledger arguments share one lexical policy: the runtime
does not resolve away a symlink before validation, and rejects a symlinked
ledger target (including a dangling final-component alias) in either form.
The NFD+casefolded reserved namespace also includes the future companion
`.<passport-basename>.inquiry-ledger.register.tmp` pathname before #744 is
implemented, so an earlier #743 ledger cannot occupy that deterministic temp.
Transaction lock timeouts must be finite numbers in the closed interval
0–60 seconds; NaN and either infinity fail before a lock sidecar is opened.
Authoritative CLI `append` and user-facing `summary` calls require an explicit
expected `project_ref`, just like bound load/commit. The optional
`--project-ref` compatibility on standalone `validate`/`replay` is diagnostic
only and does not authorize mutation or display in a project workflow.

This is purely additive: existing passports need no migration. Cross-session
resume (`ARS_PASSPORT_RESET`, per the reset-boundary protocol in
`academic-pipeline/references/passport_as_reset_boundary.md`) carries the
pointer like any other aggregate.

## 8. Evidence registration and evaluation (NOT_RUN)

Before the alpha ships, it must register in the #745 stage capability matrix:
mechanism `inquiry_branch_ledger` @ `inquiry-branch-ledger/1.0`, rows on the
stages whose checkpoints surface it, status `DESIGNED` → `IMPLEMENTED` with
behavioral evidence `NOT_RUN`, transport limits recorded ("opt-in alpha;
single-session attestation model per §1; no usability evidence"), claim
ceiling: "alternatives are preserved and recoverable as recorded state; no
claim that they are novel, correct, or valuable, and no usability claim".
The registration lands in the same PR as the first structural code and the
matrix lint gates that PR's CI, so structural code cannot merge ahead of the
record (roadmap Phase 2 gate, enforced by the same-commit discipline the
matrix's inventory locks already impose).

Paired evaluation (breadth, recovery from a wrong turn, burden, time,
abandonment — reported separately, stratified by research-family profile and
user experience) runs under the #742 §8 usability protocol umbrella and its
§8-A pre-recruitment amendment gate; this document authorizes none of it.
Promotion beyond opt-in requires that evidence, per the #742 §8 default-on
decision rule.

## 9. Acceptance mapping

| Issue #743 acceptance item | Where addressed |
|---|---|
| schema, transitions, invalidation, migration design-frozen before implementation | §2, §3, §3.1, §5, §7 (this freeze) |
| append-only, deterministic round-trip histories | §2 (canonical form, dense-id replay order, chain + pointer-digest head), §3.1 (closed payloads, replacement semantics), §5 (event-sourced staleness) |
| no additional mandatory branch prompt on the simple path | §6 |
| AI provenance never becomes author ownership without a receipt | §3 (facet exits), §4 (origin-bound receipt; §1 attestation boundary) |
| paired evaluation reports outcomes separately | §8 (design commitment; evidence NOT_RUN — not satisfied) |
| stratified by profile and experience | §8 (same status) |

## 10. Non-goals

No universal research ontology; no automatic branch proliferation or
AI ranking of author-owned branches; no auto-reopen; no default-on release
from prompt tests; no cryptographic author authentication (§1); no
transitive artifact-dependency tracking (§5); no claim that preserved
alternatives improve research.

## 11. Deferred

Only the evaluation items in §8 remain deferred. Promotion beyond the opt-in
alpha remains prohibited until those human-participant results satisfy the
#742 gates.
