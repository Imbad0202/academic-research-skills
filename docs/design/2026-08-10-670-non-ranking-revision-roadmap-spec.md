# #670 Non-ranking Revision Roadmap and Author Authorization Contract

**Status:** implemented contract
**Issue:** #670
**Date:** 2026-08-10
**Scope:** Schema 7 successor, explicit author adjudication, patch authority,
Revision-Evidence Bundle carriage, and the #576 re-review join

## 1. Problem and boundary

The old author-facing roadmap used `priority` for several non-equivalent
ideas: reviewer severity, editorial obligation, and an implied order in which
the author should spend effort. Only the first two belong to the review
contract. Work order and whether to act belong to the author.

This change therefore separates:

1. `severity`: transported reviewer finding metadata;
2. `obligation_class`: the editorial gate vocabulary
   `must_fix | should_fix | consider`;
3. `cost_scope`: a typed description of the revision surface, never a time
   estimate;
4. `consequence`: a bounded code and target, never a probability or prediction
   of acceptance;
5. `author_triage`: an explicit author choice; and
6. exact work, collateral, and registered-claim authority.

Reviewer detection is out of scope. No reviewer seat, finding grammar,
severity rule, raw held-out run, model call, or evaluation is changed by this
issue.

## 2. Authority split

The review-authority path has four distinct artifacts. Their bytes are never
merged into a single mutable document. Integrity corrections use a second,
disjoint proposal/input/authorization family described in §6.2.

| Artifact | Owner | May contain |
|---|---|---|
| `revision_roadmap.schema.json` | reviewer/editorial synthesis | findings, obligations, bounded metadata, exact proposed targets |
| `claim_surface_manifest.schema.json` | deterministic registry builder | exact registered claim surfaces and Claim Intent bindings |
| `author_adjudication_input.schema.json` | explicit session author input | author event receipts, choices, display view, exact authorizations |
| `author_adjudication.schema.json` | deterministic builder output | hash-bound author sidecar; no reviewer finding may be rewritten |

The roadmap is immutable reviewer-owned core. The author sidecar binds the
exact raw roadmap, base draft, and claim-surface bytes. A producer cannot add
author choices by editing the roadmap, and an author-sidecar builder cannot
edit obligations, severity, verification criteria, or source order.

The current sidecar and registry versions are `author-adjudication/1.0` and
`claim-surface-manifest/1.0`. They are validated as a same-generation set with
the `revision-roadmap/1.0` core; no mixed-version fallback is permitted.

An `author_event` is a closed receipt with:

- `source: explicit_session_user_message`;
- `actor_role: author`; and
- `input_sha256` over the explicit session-held input string.

This is a provenance witness, not identity authentication. The workflow must
not infer choices or fabricate a user message.

## 3. Immutable roadmap core

The canonical schema is
`shared/contracts/revision/revision_roadmap.schema.json`, with
`schema_version: revision-roadmap/1.0`.

Top-level bindings include `revision_round`, full-width
`base_draft_sha256`, and full-width `block_manifest_sha256`. The roadmap also
carries `items`, recomputable item and obligation counts, editorial decision,
consensus summary, and dissenting opinions. It carries no author decision and
no display-order field.

### 3.1 Source order

Each item carries one or more closed `source_refs`:

```json
{
  "seat": "R1",
  "channel": "finding",
  "ordinal": 2,
  "subclaim_ordinal": 0
}
```

The runtime derives immutable order from:

1. seat order `EIC, R1, R2, R3, DA`;
2. source ordinal;
3. subclaim ordinal; and
4. item id as a deterministic tie-breaker.

Severity, obligation, cost, author choice, and display view never enter the
sort. Source references must be unique and the emitted array must already be
in this mechanical order.

### 3.2 Independent item fields

Every item carries, independently:

- `id`, `source_refs`, `description`, and `reviewer`;
- `obligation_class: must_fix | should_fix | consider`;
- transported finding fields for finding-driven items, including `severity`,
  evidence anchors, confidence, and competence basis;
- typed `cost_scope`;
- closed `consequence`;
- `target_section`, `suggested_action`, `consensus_level`, and
  `verification_criteria`; and
- one or more exact `proposed_targets`.

`cost_scope.kind` is one of
`sentence | section | re_analysis | new_data | other`. `other` additionally
requires a controlled `surface_id`. The locator describes a surface; hours,
days, weeks, months, ranking labels, and suggested work order are rejected on
the work-planning fields (`suggested_action`, `verification_criteria`, and the
cost locator). Transported finding prose is not censored merely because the
reviewed science itself discusses time or rank.

`consequence.code` is a closed vocabulary such as
`evidence_gap_remains`, `claim_scope_unsupported`, or
`reporting_requirement_unmet`. Its target is a typed manuscript, section,
claim, table, figure, or dataset locator. The authoritative consequence is the
closed code plus target, and the fixed renderer supplies only the registered
non-predictive phrase for that code. Free transported finding prose is not
treated as a universally classifiable semantic surface; producers remain
forbidden from using locator fields for odds, probability, or categorical
`will be accepted/rejected` predictions.

### 3.3 Exact proposed work scope

Every roadmap item declares exact block-and-operation scopes:

```json
{
  "block_id": "B0007",
  "allowed_operations": ["replace_block", "insert_after"]
}
```

Targets must resolve in the bound block manifest, use canonical ordering, and
may not repeat a block. `DOC-BODY-START` is legal only with `insert_after`.
This is a proposal, not authority: an author must select a subset through the
sidecar before a write is legal.

## 4. Registered claim surfaces

`claim_surface_manifest.schema.json` binds the exact roadmap and base draft.
Every registered surface names:

- a `surface_id`;
- exact `(scoped_manifest_id, claim_id)` resolving in a hash-bound Claim
  Intent Manifest;
- one exact block id;
- absolute UTF-8 byte start/end offsets;
- exact original text and SHA-256;
- the Claim Intent `claim_text` hash; and
- the current field-relative rung.

The validator reopens each named Claim Intent artifact from a caller-supplied
local root, verifies its hash and schema, resolves the manifest/claim pair,
checks the absolute UTF-8 span against the raw draft bytes, requires the exact
surface text to equal the referenced Claim Intent `claim_text` byte-for-byte,
requires that text to occur once in the declared raw block, and rejects overlapping
registered surfaces.

Rung labels remain field-relative strings. The contract does not invent a
universal numeric ladder across heterogeneous claims.

## 5. Explicit author adjudication

The deterministic `build-adjudication` path accepts only the explicit-choice input,
the immutable roadmap, the exact base draft, the block manifest, and the claim
surface manifest. It supplies no default and reads no ambient clock.

The completed sidecar contains exactly one decision per roadmap item:

```json
{
  "item_id": "REV-001",
  "author_event_id": "AUTHOR-EVENT-session-1",
  "author_triage": "will_address",
  "authorized_targets": [
    {"block_id": "B0007", "allowed_operations": ["replace_block"]}
  ],
  "claim_strength_authorizations": []
}
```

The runtime enforces:

- `will_address` has at least one exact authorized target, and each target is
  a subset of the roadmap proposal;
- `wont_address` and `not_on_point` require `author_reason` and carry no work
  or claim authority;
- every event reference resolves to an explicit author event;
- cardinality is exactly one decision per roadmap item; and
- display order is a full unique permutation.

`display_order.mode: user_selected` changes presentation only. In
`source_traceability` mode, the permutation must equal immutable roadmap
order. In neither mode can it affect a decision-letter transport reference,
patch authorization, or #576 decision derivation.

### 5.1 Exact claim-strength authorization

An approved claim move binds all of:

- unique authorization and author-event ids;
- surface id and exact `(scoped_manifest_id, claim_id)`;
- exact block id and original-text hash;
- exact replacement text and replacement-text hash;
- exact `from_rung`, `to_rung`, and `direction`; and
- the author's reason.

The values must replay against the registered surface. `from_rung` must equal
the registered current rung, `to_rung` must differ, and a claim authorization
must belong to a `will_address` item whose exact target permits replacing or
deleting that block.

`will_address` alone authorizes no claim move.

### 5.2 Declined-overlap collateral

If an accepted item and a declined item propose the same block, the declined
item creates a no-touch boundary. A write is legal only with a separate
author-owned collateral authorization naming:

- the accepted authorizing item;
- the declined constrained item;
- the exact block and operation; and
- an explicit reason.

The declined item is never a source of authority. Every declined item touching
that target must be covered exactly; missing and extra collateral coverage both
fail.

## 6. Patch format 1.1 and apply gate

The current schema `shared/contracts/patch/revision_patch.schema.json` accepts
only `patch_format_version: 1.1`. It is a disjoint union:

1. `authorization_context: review_roadmap`; or
2. `authorization_context: integrity_correction`.

The current `scripts/ars_apply_revision_patch.py` rejects 1.0 before writing.
Historical 1.0 replay is isolated under:

- `shared/contracts/patch/legacy/v1_0/revision_patch.schema.json`; and
- `scripts/legacy/ars_apply_revision_patch_v1_0.py`.

The archived loader points only at the archived schema and can never emit a
current 1.3 authorization PASS witness.

### 6.1 Review-roadmap branch

A review patch binds raw roadmap, author-sidecar, and claim-surface SHA-256
values plus a JCS-compatible SHA-256 of the author-decision projection. Every
operation explicitly carries:

- one or more roadmap item ids;
- `claim_strength_changes` (possibly empty); and
- `collateral_authorization_ids` (possibly empty).

Before structural analysis or any output write, apply replays the block
manifest, roadmap, claim registry, author sidecar, and patch authority. It
requires every cited item to be `will_address`, every target/operation to fall
inside that item's exact authorized subset, every claim move to equal one
unused exact authorization, and every declined overlap to have exact unused
collateral coverage.

For registered claim surfaces inside a replaced/deleted block, the new text
must either preserve the exact original once or perform the exact approved
replacement once. Insertions cannot pretend to rewrite a registered surface.

### 6.2 Integrity-correction branch

An integrity issue list is a proposal, never write authority. Each issue has
exact `proposed_targets`. The explicit author input carries one `authorize` or
`stop_without_write` decision per issue and, load-bearingly, the SHA-256 of the
complete proposed patch bytes the author approved. The deterministic builder
copies that hash—it never synthesizes approval from a producer-supplied patch—
and adds only the replayed base/list/round bindings to
`integrity-correction-authorization/1.0`.

Apply requires `--integrity-issue-list` and `--integrity-authorization`. It
replays event references, exact issue coverage, target subsets, exact list/base
bindings, and the author-input patch digest before any write. Every operation
must cite an `authorize` decision and fall inside its exact block/operation
subset. Because the author input binds the entire patch bytes, substituted
`new_text`—including a registered-claim change—invalidates the authorization.
`stop_without_write` grants no target. Claim-move and collateral arrays remain
empty, and all review-roadmap authority arguments are forbidden on this branch.

### 6.3 Apply report and honest E6 boundary

Current apply emits report format 1.3. The report includes the exact patch
digest, pre/post draft hashes, revision round, authorization context,
mechanically replayed `authorization_witness`, and per-operation claim and
collateral declarations.

For review-roadmap writes, the witness reports the number of registered
surfaces checked. For integrity writes, it reports the exact author-input patch
digest and authorization-sidecar digest. Both always set
`unregistered_claim_drift_review_required: true`: review writes protect exact
registered surfaces mechanically, while integrity writes require explicit
author approval of the entire patch, but neither mechanism claims universal
semantic classification of unregistered prose. Those changes remain a
mandatory E6 human/integrity review surface. When E6 reports an unauthorized
strength move, the finding is not a Phase-E verdict issue but is
checkpoint-closing: the author must explicitly select `restore`,
`authorize_with_reason`, or `pause` for every reported row. The separate
hash-bound disposition sidecar permits continuation only when all rows are
authorized with non-blank reasons. This closes disposition coverage, not the
recall or correctness of model-mediated semantic detection.

## 7. Revision-Evidence Bundle

`revision_evidence_bundle.schema.json`, version
`revision-evidence-bundle/1.0`, is a closed local evidence chain.

The chain starts with:

- an exact draft;
- its exact block manifest;
- a receipt whose verdict is literal `PASS`, with zero open issues and an
  exact draft hash; and
- the first revision-round number.

Each following round is exactly one of:

- `review_roadmap`: pre draft/manifest, roadmap, claim surfaces, author
  sidecar, patch, report, and post draft;
- `review_noop`: the same review authority artifacts but no patch/report,
  legal only when every author decision is declined and pre/post bytes are
  identical; or
- `integrity_correction`: pre draft/manifest, issue-list proposal, exact
  author patch-authorization sidecar, patch, report, and post draft.

The validator enforces continuous round numbers, prior-post equals next-pre,
exact local path/hash replay, current patch/report authority replay, and final
draft equals the last post-round draft. For every write round it also reruns
the pure patch validator/splicer in memory, requires byte-exact replay output
to equal the declared post draft, and recomputes operation, fresh-id,
structural, and counter report fields. Re-hashing a forged post/report pair
cannot create a valid round. It rejects absolute paths, traversal, symlinks,
non-regular files, oversized artifacts, ambiguous JSON, and mutation during
its read-once load.

## 8. Author-facing presentation and decision-letter join

The canonical renderer first replays the exact roadmap/base/block manifest,
claim-surface registry, and complete author sidecar; schema-valid but
cross-artifact-invalid choices cannot be displayed as explicit authority. It
then shows separate labels for obligation class, reviewer
severity, cost scope, bounded consequence, author triage, and exact authorized
targets. It contains no `Priority 1/2/3`, P1/P2/P3 work list, rank column,
suggested work order, or model-generated time estimate.

The decision letter's `R<n>` is a transport reference, not a rank. It is
recomputed by filtering immutable roadmap source order for
`obligation_class == must_fix`. Required Item Details always use that order.
Author-selected display order can never change `R<n>`.

## 9. #576 current-contract migration

The current #576 artifact family is contract version 1.1. Version 1.0 schemas
and checker are archived under `shared/contracts/re_review/legacy/v1_0/` and
`scripts/legacy/`; a mixed 1.0/1.1 chain is invalid.

Current names are:

| Legacy field | Current field |
|---|---|
| `priority` | `obligation_class` |
| `residual_magnitude` | `residual_obligation_class` |
| `residual_magnitude_counts` | `residual_obligation_class_counts` |
| `p2_addressed_rate` | `should_fix_addressed_rate` |

The formulas are unchanged: precommitment covers exactly `must_fix` and
`should_fix`; verdict and traceability cover all items; `consider` is
decision-inert.

The current input manifest hard-requires original manuscript, revised
manuscript, exact roadmap, author adjudication, and Revision-Evidence Bundle.
Schema 11 rows copy, without inference:

- `author_triage`;
- conditional `author_reason`;
- exact `authorized_targets`; and
- exact `claim_strength_authorizations`.

The checker validates raw roadmap/base bindings and complete explicit author
events, hash-loads and fully replays the required bundle, binds its final draft
to the manifest's revised manuscript, binds the exact current roadmap/author
pair to one bundle round, then compares every copied field to the hash-bound
sidecar. The letter's `R<n>` join is recomputed only from immutable roadmap
order, never from display view or author choice.

## 10. Detection preservation

`source_finding_projection()` exposes the reviewer-derived subset of a
roadmap. Integration tests freeze the upstream reviewer detection surfaces and
prove that author decisions, view order, cost metadata, and authorization
carriage do not mutate that projection.

Acceptance for this issue is hermetic. It uses schemas, fixtures, exact hashes,
mutation tests, and local replay only. Live model calls, external APIs, judges,
and expensive performance evaluation are excluded.

## 11. Required mutation coverage

The implementation must keep tests for at least:

1. severity, obligation, cost, and consequence independence;
2. rank/time/probability leakage rejection;
3. immutable source ordering and presentation-only view permutations;
4. missing/duplicate decisions and declined-reason requirements;
5. arbitrary target/operation attempts outside exact author scope;
6. declined no-touch with missing, extra, wrong, or reused collateral ids;
7. exact registered-claim preservation and replacement;
8. wrong manifest/claim/surface/block/hash/rung/direction/replacement values;
9. reused claim authorization and unregistered E6 disclosure;
10. current 1.0 patch rejection and archived 1.0 loader isolation;
11. roadmap, author, claim-surface, patch, report, path, and chain mutations;
12. review no-op, continuous rounds, chain-start PASS, and exact final draft;
13. #576 mixed-version rejection and raw sidecar binding;
14. Schema 11 author-field drift and declined-reason round trip;
15. `R<n>` remaining stable under a user-selected view; and
16. renderer and active templates containing no work-rank presentation.

## 12. Non-goals

This issue does not remove reviewer severity, alter editorial decision floors,
automatically choose author triage, authenticate user identity, estimate
acceptance probability, promise universal semantic-drift detection, rewrite
historical raw artifacts, change human-subjects authority, or implement the
cross-run engagement measurement reserved for #673.
