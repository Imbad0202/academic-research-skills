# #743 — Bounded inquiry branch ledger with park, reopen, merge, and invalidation semantics

Status: DESIGN FREEZE for the `inquiry-branch-ledger/1.0` contract: schema
shape, state transitions, invalidation rules, and migration are frozen here,
satisfying the issue's design-frozen-before-implementation acceptance gate.
This document authorizes no implementation, no evaluation run, no new prompt
on the simple path, and no default-on behavior. The alpha, when it ships, is
opt-in behind `ARS_INQUIRY_LEDGER=1` (default OFF = byte-equivalent current
behavior).

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

## 2. Contract: `inquiry-branch-ledger/1.0`

One ledger is one JSON document per project, **event-sourced**: the only
mutable region is an append-only `events[]` list; every branch's current
state is a deterministic replay of its events. This gives the acceptance
properties directly — park/reopen/merge histories are append-only by
construction and round-trip deterministically (replay is a pure function;
canonical serialization of the replayed state is byte-stable).

Top level:

| Field | Req | Shape |
|---|---|---|
| `schema_version` | ✓ | const `inquiry-branch-ledger/1.0` |
| `project_ref` | ✓ | string binding the ledger to its pipeline run/passport |
| `profile_binding` | ✓ | `{profile_id, profile_version, content_sha256}` — the #742 profile in force; rebinding on profile correction appends a `profile_rebound` event, never edits this field silently (the field always mirrors the latest such event) |
| `events` | ✓ | append-only list of event objects (below) |

Event object (closed shape):

| Field | Req | Shape |
|---|---|---|
| `event_id` | ✓ | monotonically increasing integer, dense from 1 |
| `recorded_at` | ✓ | ISO 8601 timestamp |
| `actor` | ✓ | `author` \| `ai` — who initiated the event; every state-changing event below except `facet_surfaced` and `reopen_condition_signal` requires `author` |
| `kind` | ✓ | closed enum, §3 |
| `branch_id` | ✓ | stable slug; new ids may only be introduced by `branch_created` / `facet_surfaced` |
| `payload` | ✓ | kind-specific closed object, §3 |
| `prev_event_sha256` | ✓ | SHA-256 of the canonical serialization of the previous event (64-zero placeholder on event 1) — a hash chain, so truncating or rewriting history is detectable by replay |

Branch state (derived by replay, never stored authoritatively):

- `branch_id`, `parent_id` (nullable — a root framing has no parent);
- `provenance`: `author_originated` \| `ai_surfaced_facet` \|
  `author_adopted` (§4);
- `assumptions[]`, `evidence_sought[]` (non-empty strings, author-editable
  via `branch_annotated` events);
- `status`: `active` \| `parked` \| `rejected` \| `reopened` \| `merged`
  (§3) — the same closed vocabulary the #742 §7 budget counts (`live` =
  `active` + `reopened`);
- `disposition`: `{reason}` from the latest disposition event;
- `reopen_conditions[]`: declarative text, optionally with an evidence
  pointer (§5);
- `downstream_refs[]`: identifiers of pipeline artifacts derived from this
  branch (RQ Brief sections, blueprint choices, draft sections) — the
  invalidation fan-out set (§5);
- `merged_into` (only when `merged`): the surviving `branch_id`.

## 3. Event kinds and the frozen state machine

Closed `kind` enum and transitions:

| kind | actor | Effect (frozen) |
|---|---|---|
| `branch_created` | author | new branch, `provenance: author_originated`, status `active` |
| `facet_surfaced` | ai | new branch, `provenance: ai_surfaced_facet`, status `parked` — an AI-surfaced facet NEVER enters as `active`; it waits for the author |
| `branch_adopted` | author | §4 adoption receipt; `ai_surfaced_facet` → `author_adopted`; status `parked` → `active` |
| `branch_annotated` | author | edits `assumptions` / `evidence_sought` / `reopen_conditions` / `downstream_refs`; no status change |
| `branch_parked` | author | `active` \| `reopened` → `parked`, with `reason` |
| `branch_rejected` | author | `active` \| `reopened` \| `parked` → `rejected`, with `reason` |
| `branch_reopened` | author | `parked` \| `rejected` → `reopened`, with `reason` and (when evidence-triggered) the satisfying evidence pointer; fires §5 invalidation |
| `branch_merged` | author | `active` \| `reopened` → `merged`, with `merged_into` naming a currently-live branch and `reason`; the target absorbs the merged branch's `downstream_refs` |
| `reopen_condition_signal` | ai | records that new session evidence MAY satisfy a stored reopen condition; changes no status — the only lawful consequence is showing the §6 summary to the author |
| `profile_rebound` | author | mirrors a #742 §6 profile correction into `profile_binding` |

Any transition not in this table is invalid; replay fails closed on an
invalid event (a corrupt ledger is an error surface, never a silently
truncated state). `merged` is terminal. `reopened` is a distinct persistent
status — it stays visible as "reopened, awaiting disposition" until the
author explicitly parks, rejects, or merges it; it counts against the live
budget precisely so it cannot silently accumulate.

## 4. Provenance and the adoption receipt

Only author-expressed or explicitly author-adopted framings become scholarly
branches. The frozen rules:

- provenance history is immutable: `author_adopted` records that the branch
  ENTERED as `ai_surfaced_facet`; nothing can relabel it `author_originated`;
- `branch_adopted.payload` is the receipt: it must carry the author's own
  restatement (`author_formulation`, non-empty, not byte-identical to the
  surfaced text) alongside the retained original `surfaced_text`; an
  AI-surfaced facet cannot silently become the research question, and a bare
  "ok" is not an adoption;
- an unadopted `ai_surfaced_facet` never appears in any downstream prompt as
  the author's position, and consumers must render its provenance label
  wherever the branch is shown;
- `facet_surfaced` events are budget-relevant only after adoption (they enter
  `parked`), so the AI cannot exhaust the author's live-branch budget.

## 5. Reopen and invalidation semantics

`reopen_conditions[]` are author-owned declarative statements ("reopen if
the measurement invariance test fails", optionally pointing at an evidence
row). The AI may record a `reopen_condition_signal` when session evidence
plausibly satisfies one; **reopening itself is always an author action**.

On `branch_reopened`, every artifact in the branch's `downstream_refs[]` —
and, transitively, artifacts that other live branches list as derived from
those (`downstream_refs` closure over the recorded pointers only; no
speculative reach) — is marked **stale** with a pointer back to the reopening
event. Stale marking is visible and non-destructive: nothing is rewritten,
deleted, or regenerated automatically. The stale mark clears only when the
author either re-confirms the artifact ("still valid under the reopened
line") or supersedes it. This is the same stale-not-rewritten discipline the
#742 §6 profile correction uses.

## 6. Interaction constraints (opt-in alpha)

- `ARS_INQUIRY_LEDGER` unset or `0`: no ledger file, no prompt, no summary —
  byte-equivalent current behavior. The linear path also remains available
  WITH the flag on: the ledger only materializes once a second branch exists.
- With the flag on, a compact branch summary (one line per live branch;
  parked/rejected counts folded into a single trailing line) appears at
  exactly two moments: a consequential freeze (the Stage 1 design-freeze
  checkpoint and the Stage 2.5 / 4.5 MANDATORY checkpoints) and when a
  `reopen_condition_signal` is recorded. Nowhere else.
- Budget: the #742 §7 semantics verbatim — live = `active` + `reopened`,
  budget and `ask_merge_park_archive` overflow from the bound profile,
  overflowing candidate retained pending disposition.
- Every ledger interaction offers `skip`, `off` (sets the flag's session
  state to off), and reset-to-simple-path; none of these discards
  scholar-owned work (the ledger file persists; only the surfaces stop).
- Simple-path users — flag off, or flag on with ≤ 1 branch — receive **zero**
  additional mandatory prompts (acceptance item, test-pinned at
  implementation time).

## 7. Storage and migration

The ledger is a standalone artifact referenced from the Material Passport by
an optional pointer aggregate (id + content digest), following the existing
aggregate-pointer pattern. Absence of the pointer = feature off. This is
purely additive: existing passports need no migration, and a passport whose
pointer names a missing or hash-mismatched ledger file fails visibly at load
(`LEDGER-BINDING-BROKEN`), never silently continues without it. Cross-session
resume (`ARS_PASSPORT_RESET`) carries the pointer like any other aggregate.

## 8. Evidence registration and evaluation (NOT_RUN)

Before the alpha ships, it must register in the #745 stage capability matrix:
mechanism `inquiry_branch_ledger` @ `inquiry-branch-ledger/1.0`, cross-cutting
rows on the stages whose checkpoints surface it, status `DESIGNED` →
`IMPLEMENTED` with behavioral evidence `NOT_RUN`, claim ceiling: "alternatives
are preserved and recoverable as recorded state; no claim that they are
novel, correct, or valuable, and no usability claim". Structural code may not
precede that record (roadmap Phase 2 gate).

Paired evaluation (breadth, recovery from a wrong turn, burden, time,
abandonment — reported separately, stratified by research-family profile and
user experience) runs under the #742 §8 usability protocol umbrella and its
§8-A pre-recruitment amendment gate; this document authorizes none of it.
Promotion beyond opt-in requires that evidence, per the #742 §8 default-on
decision rule.

## 9. Acceptance mapping

| Issue #743 acceptance item | Where addressed |
|---|---|
| schema, transitions, invalidation, migration design-frozen before implementation | §2, §3, §5, §7 (this freeze) |
| append-only, deterministic round-trip histories | §2 (event sourcing + hash chain; replay is pure) |
| no additional mandatory branch prompt on the simple path | §6 |
| AI provenance never becomes author ownership without a receipt | §4 |
| paired evaluation reports outcomes separately | §8 (design commitment; evidence NOT_RUN — not satisfied) |
| stratified by profile and experience | §8 (same status) |

## 10. Non-goals

No universal research ontology; no automatic branch proliferation or
AI ranking of author-owned branches; no auto-reopen; no default-on release
from prompt tests; no claim that preserved alternatives improve research.

## 11. Deferred

Schema file + replay validator + passport pointer aggregate + checkpoint
summary surfaces (implementation PR bounded by this freeze); the #745 row
lands in that PR; evaluation items per §8.
