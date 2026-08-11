# Human-Subjects Authority Selection and Resolution Protocol (#666)

This protocol governs exact authority selection and deterministic applicability
tracing. It is not a committee, legal opinion, authorization, compliance result,
submission-readiness result, or review-pathway result.

Canonical artifacts:

- `shared/contracts/human_subjects/irb_context_record.schema.json`
- `shared/contracts/human_subjects/authority_profile_registry.schema.json`
- `shared/contracts/human_subjects/resolved_authority_context.schema.json`
- `shared/human_subjects_authority_registry.json`
- `scripts/resolve_human_subjects_authority.py`
- `docs/design/2026-08-09-666-human-subjects-authority-contract-spec.md`

The schemas are authoritative for field names and local shape. This protocol
governs cross-artifact use.

## Two axes and bounded profiles

V1 has exactly two axes: `review_ethics` and `data_protection`. A study may select
multiple profiles on either axis. Funder and institutional requirements are
overlays, never axes.

Every shipped profile carries `coverage_status=bounded_subset` and
`no_completeness_claim=true`:

- `us.hhs.45-cfr-46.subpart-a`
- `tw.mohw.human-subjects-research-act`
- `eu.gdpr.research-core-bounded`

Profiles contain curator summaries and primary-source links, not a claim of
complete law or legal advice. Do not vendor unlicensed normative text.

## Author declaration

The context record uses:

- `context_record_id`
- `confirmed_by=author`
- `confirmed_at`
- `applicability_as_of`
- `scope_dimensions`
- typed `declared_facts`
- `profile_selection_state` and exact `selected_profiles`
- `overlay_selection_state` and exact `selected_overlays`
- `display_precedence`

Do not infer any of these from locale, language, affiliation, filenames,
manuscript text, or model memory.

Each selected profile pins axis, id, version, digest, and authority scope ids.
Each selected overlay pins kind, axis, id, version, and digest. Unknown or
mismatched pointers fail; never choose a latest version automatically.

An empty scope-dimension list is unknown, not confirmed absence. A missing fact or
a fact with `state=unknown` and `value=null` is `unknown`, never false.
`overlay_selection_state=not_provided` is distinct from
`none_declared_by_author`.

## Predicate evaluation

Registry predicates are a closed recursive AST with only:

- `fact_equals`
- `fact_in`
- `fact_contains`
- `all`
- `any`
- `not`

Facts must resolve through `fact_definitions`, and declared value types must agree
with the catalogue. Do not execute string expressions or add profile-specific
branches.

`fact_equals` and `fact_in` accept scalar boolean, string, string-enum, or date
facts only, and every date operand must be a real ISO 8601 calendar date.
`fact_contains` means exact membership in a `string_set`; it never performs
substring matching on a string. V1 has no string-set equality operator.

Use Strong Kleene logic:

- missing or unknown fact leaf → `unknown`;
- `all`: false if any false, true if all true, otherwise unknown;
- `any`: true if any true, false if all false, otherwise unknown;
- `not(true)=false`, `not(false)=true`, `not(unknown)=unknown`.

A selected profile whose predicate is false emits `PROFILE_SCOPE_CONFLICT`; an
unknown predicate emits `APPLICABILITY_UNRESOLVED`. Both block the downstream
gate, and the resolver does not assert legal non-applicability.
Requirement predicate results remain `true | false | unknown` and never become a
compliance conclusion.

## Authority provenance

Source records separately record `canonical_url`, `snapshot_url`,
`provision_locator`, closed `allowed_provisions`, `effective_from`, `effective_until`,
`source_amended_or_published_date`, `retrieved_at`, `verified_at`,
`source_language`, `controlling_language`, `authenticity_status`,
`content_digest`, `digest_scope`, `rights_status`, and `freshness`. Row-local
`authority_anchor` records use their schema-defined counterparts, including
`authority_url`, `provision`, and `effective_date`.

The anchor source must occur in its profile or overlay `source_ids`; its
`provision` must occur in that source's `allowed_provisions`; and its
`effective_date` must equal the source's provision-specific `effective_from`.

Never infer an effective date from an amendment date. For Taiwan, the page's
amendment date belongs in `source_amended_or_published_date`; it is not, without a
separate controlling-authority basis, the profile's `effective_from` or a
requirement's `effective_date`. Keep the controlling Chinese source distinct from
the official English reference translation.

Future-effective, expired, stale, unverified, superseded, or
non-controlling-translation-only authority produces
`AUTHORITY_SOURCE_NOT_CURRENT`. Runtime resolution is offline; it never refreshes
these records from the network.

## Requirements and overlays

Every requirement identifies its axis, obligated actor, consumer scopes,
applicability AST, structured expectations, expected evidence and holder,
waiver/exception route, authoritative decision maker, collision metadata, and
full authority anchor.

Consumers must respect `obligated_actor` and `consumer_scopes`. Committee
composition evidence held by an IRB is not an investigator packet requirement.
A profiled exception route records only that a route exists; it never means the
route was applicable, requested, or granted.

Overlays use exact `target_profiles` id/version/digest pointers. Their operation is
`add`, `supplement`, or `conflict`, and `requirements_removed` is always false.
They cannot replace a base profile, delete a base row, fill an unresolved axis, or
introduce a funder axis.

Every target profile must be selected exactly. An overlay inherits the Strong
Kleene `all` of all target-profile applicability results; each overlay requirement
combines that inherited result with its own predicate using Strong Kleene `all`.
If any target is false or unknown, emit `OVERLAY_BASE_UNRESOLVED`, preserve that
tri-state result on the overlay requirements, and keep the downstream gate closed.

## Display-only precedence and collisions

`display_precedence` and resolved `trace_order` are presentation order only.
Every precedence entry says `display_only_no_suppression`.

Changing display order must not change selected authorities, predicate results,
unresolved reasons, downstream gates, collision membership, or requirement
accounting. Every requirement result appears exactly once in `trace_order`.

Requirements sharing a collision key remain parallel with
`parallel_authorities_require_human_resolution` and
`requirements_removed=false`. Never average or deduplicate different
jurisdictions or the two independent axes.

## Resolver procedure

1. Read only the explicitly supplied context and registry JSON files.
2. Reject duplicate JSON keys, non-finite values, and unknown fields.
3. Validate the context and registry schemas.
4. Recompute and match every selected profile/overlay id, version, and digest.
5. Resolve authority scopes and exact overlay targets without fallback.
6. Require selected base profiles on both axes.
7. Validate source interval, freshness, language, authenticity, digest, and rights
   metadata at `applicability_as_of`.
8. Evaluate every profile and requirement AST using Strong Kleene logic.
9. Account for every selected requirement exactly once.
10. Preserve all collisions and build display-only `trace_order`.
11. Emit the pointer-only resolved artifact and canonical digests; compute
    `resolved_digest` with its own field excluded.

The resolver does not read manuscripts, scan sibling files, access the network,
judge prose, decide legal applicability, or render a user-facing brief.

## Pointer-only result and gate

The resolved artifact carries a `context_pointer` and `registry_pointer`; it does
not embed either input. Profile, overlay, requirement, and authority-anchor data
are represented through schema-defined pointers and digests.

Its states are `resolved`, `jurisdiction_unresolved`, and
`applicability_unresolved`. Its closed unresolved codes are:

- `JURISDICTION_UNRESOLVED`
- `APPLICABILITY_UNRESOLVED`
- `OVERLAY_BASE_UNRESOLVED`
- `AUTHORITY_SOURCE_NOT_CURRENT`
- `PROFILE_SCOPE_CONFLICT`

Each unresolved reason contains exactly `code`, `axis`, nullable `authority_id`,
and nullable `requirement_id`. It contains no prose or free-text detail. A
requirement-level reason identifies its requirement; profile-, overlay-, and
missing-axis reasons use `requirement_id=null`.

The downstream gate contains exactly:

```json
{
  "both_axes_selected": true,
  "exact_selection_resolved": true,
  "all_applicability_resolved": true,
  "profile_dependent_result_allowed": true
}
```

Only `resolution_state=resolved` may set all four true. A resolved result contains
at least one selected profile on each axis, every selected profile has
`applicability=true` and `source_state=current`, and no requirement applicability
is unknown. Either unresolved state requires an unresolved reason and forces
`profile_dependent_result_allowed=false`. A profile or overlay on one axis never
cures a missing base profile on the other.

Before consuming a serialized result, call
`validate_resolved_context(result, context, registry)`. It validates the bound
inputs, deterministically replays resolution, recomputes `resolved_digest` with
that field excluded, and requires exact object equality. The replay checker—not
JSON Schema alone—owns semantic uniqueness across rows, JSON Pointer resolution,
digest-to-input binding, and gate derivation.

## Consumer boundary

- #667 consumes a serialized authority result only after
  `validate_resolved_context(result, context, registry)` succeeds and the
  profile-dependent gate is open. It filters to `submission_packet`, preserves
  exact requirement and authority-anchor pointers, and then uses only the
  closed `evidence_expected` fields `evidence_id`, `held_by`, and
  `artifact_type` for status derivation. It never interprets, evaluates, or copies
  `structured_expectations` or an evidence description; exact whole-row bytes are
  canonical-hashed only for replay integrity. Content-coverage questions belong
  to #681.
- #681 consumes authority rows only through a #667 manifest that has first been
  replay-validated against this same context/registry/resolved triplet and its
  exact packet inventory/root. It may then dereference exact
  `structured_expectations[]` pointers and join separately session-held content
  through `shared/references/authority_content_coverage_advisory_protocol.md`.
  Its carrier is always `LLM-ADVISORY` and `UNMEASURED`; it cannot alter
  applicability, deterministic packet status, readiness, caller authorization,
  institutional acceptance, or any authority pointer/digest.
- #668 remains valid in `artifact_agnostic` mode and no profile may rewrite its
  source correspondence or committee authority.
- #669 consumes every selected-profile requirement scoped to `pathway_trace`
  only after exact #666 replay, then projects exact fact occurrences,
  authoritative-decision-maker role ids, and authority anchors under
  `shared/references/review_pathway_rule_trace_protocol.md`. Its caller-owned
  candidate names and ordering are display-only; the trace never determines,
  predicts, ranks, approves, clears, exempts, authorizes, or gates. A missing
  profile preserves `JURISDICTION_UNRESOLVED`. The protocol's narrow display of
  requirement-level unknown predicates does not open or alter this resolver's
  `profile_dependent_result_allowed` gate.
- #680 owns correction and migration of mixed-jurisdiction reference prose.

#666 itself changes no user-facing output. It emits no verdict, pathway,
readiness, authorization, conformance result, or timeline. The #665 independent
status grammar and fixed non-authorization footer remain unchanged.

## #667 capability-envelope facts

The registry also catalogs seven author-declared booleans used only to decide
whether the deterministic submission-packet checker is within its V1 technical
capability envelope:

- `packet_v1.non_clinical=true`
- `packet_v1.single_institution=true`
- `packet_v1.competent_adults_only=true`
- `packet_v1.biospecimens_involved=false`
- `packet_v1.regulated_clinical_trial=false`
- `packet_v1.cross_border_material_transfer=false`
- `packet_v1.multisite_reliance=false`

These facts are not legal characterizations and cannot select an authority,
satisfy an axis, or change a profile or requirement digest. A missing, unknown,
or non-matching value makes #667 return `APPLICABILITY_UNRESOLVED`; it never
means that an authority is legally inapplicable. The complete #667 contract is
`shared/references/submission_packet_manifest_protocol.md`.
