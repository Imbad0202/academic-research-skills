# #666 Multi-profile human-subjects authority contract V1

## Decision

V1 is a declaration-and-resolution contract. It records exact, author-confirmed
authority selections and a deterministic applicability trace. It does not issue a
legal, compliance, readiness, authorization, exemption, approval, or review-pathway
result.

The contract has exactly two independent axes:

1. `review_ethics`
2. `data_protection`

Institutional and funder requirements are explicit additive overlays. `funder` is
not an axis. An overlay cannot fill an unresolved base axis, replace a base
profile, remove a requirement, or win a collision by precedence.

The canonical artifacts are:

- `shared/contracts/human_subjects/irb_context_record.schema.json`
  (`irb-context-record/1.0`)
- `shared/contracts/human_subjects/authority_profile_registry.schema.json`
  (`human-subjects-authority-registry/1.0`)
- `shared/contracts/human_subjects/resolved_authority_context.schema.json`
  (`resolved-human-subjects-authority-context/1.0`)
- `shared/human_subjects_authority_registry.json`
- `scripts/resolve_human_subjects_authority.py`
- `shared/references/human_subjects_authority_protocol.md`

The JSON Schemas are the field-shape authority. This specification freezes the
cross-record and resolver semantics that JSON Schema cannot express alone.

## 1. Author-owned context record

The IRB Context Record is declaration-only. ARS never derives a jurisdiction,
institution, data-protection regime, profile, population, study type, data
location, transfer, or funder from locale, language, affiliation, manuscript
content, or model memory.

Its exact root fields are:

```json
{
  "schema_version": "irb-context-record/1.0",
  "context_record_id": "ctx.cross-border-example",
  "confirmed_by": "author",
  "confirmed_at": "2026-08-09T10:00:00+08:00",
  "applicability_as_of": "2026-08-09",
  "scope_dimensions": {
    "review_jurisdictions": ["review.tw"],
    "institutions": ["institution.example"],
    "data_protection_regimes": ["regime.eu-gdpr"],
    "funders": [],
    "study_types": ["study.survey"],
    "populations": ["population.competent-adults"],
    "data_locations": ["location.collection-de", "location.analysis-tw"],
    "cross_border_transfers": ["transfer.de-to-tw"]
  },
  "declared_facts": [
    {
      "fact_id": "study.personal-data-processed",
      "value_type": "boolean",
      "state": "declared",
      "value": true,
      "provenance": "author_declared"
    },
    {
      "fact_id": "gdpr.member-state-research-law-identified",
      "value_type": "boolean",
      "state": "unknown",
      "value": null,
      "provenance": "author_declared"
    }
  ],
  "profile_selection_state": {
    "review_ethics": "selected",
    "data_protection": "selected"
  },
  "selected_profiles": [
    {
      "axis": "review_ethics",
      "profile_id": "tw.mohw.human-subjects-research-act",
      "profile_version": "2019.01",
      "profile_digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "authority_scope_ids": ["review.tw"]
    },
    {
      "axis": "data_protection",
      "profile_id": "eu.gdpr.research-core-bounded",
      "profile_version": "2018.05",
      "profile_digest": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
      "authority_scope_ids": ["regime.eu-gdpr"]
    }
  ],
  "overlay_selection_state": {
    "institutional": "none_declared_by_author",
    "funder": "none_declared_by_author"
  },
  "selected_overlays": [],
  "display_precedence": [
    {
      "axis": "review_ethics",
      "purpose": "display_only_no_suppression",
      "ordered_authorities": [
        {
          "authority_kind": "profile",
          "axis": "review_ethics",
          "authority_id": "tw.mohw.human-subjects-research-act",
          "authority_version": "2019.01",
          "authority_digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        }
      ]
    },
    {
      "axis": "data_protection",
      "purpose": "display_only_no_suppression",
      "ordered_authorities": [
        {
          "authority_kind": "profile",
          "axis": "data_protection",
          "authority_id": "eu.gdpr.research-core-bounded",
          "authority_version": "2018.05",
          "authority_digest": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        }
      ]
    }
  ]
}
```

### 1.1 Unknown is not false or confirmed none

`scope_dimensions` contains the fact ids assigned to all eight required
declaration dimensions. An empty dimension list means undeclared or unknown. It
does not assert that the dimension has no applicable authority or condition.

A declared fact uses `state=unknown` and `value=null` for an explicit unknown.
An omitted fact is also unknown at evaluation time. Neither is coerced to boolean
false. A declared boolean must be a JSON boolean; the string `"false"` is invalid.

Overlay absence has three distinct states per kind:

- `selected`
- `not_provided`
- `none_declared_by_author`

Only the last is an affirmative author declaration that none was selected.

### 1.2 Exact selection

Every base selection is plural, axis-qualified, and pins
`profile_id + profile_version + profile_digest + authority_scope_ids`. The
resolver rejects an unknown id, version mismatch, digest mismatch, duplicate
selection, axis mismatch, or unknown scope. It never chooses the newest profile
or substitutes a nearby authority.

`profile_selection_state.review_ethics=selected` and
`profile_selection_state.data_protection=selected` each require at least one
selected profile on that axis. `unresolved` requires none. An overlay selection pins
`overlay_kind + axis + overlay_id + overlay_version + overlay_digest` and must
agree with its selection-state field.

`display_precedence` is author-declared trace order only. Its two entries cover
the two axes and always carry `purpose=display_only_no_suppression`.

## 2. Authority registry

The closed registry root contains exactly `schema_version`, `registry_id`,
`registry_version`, `as_of`, `fact_definitions`, `sources`, `profiles`, and
`overlays`. A valid instance contains the schema-required catalog entries on
both axes; an empty-array skeleton is intentionally not shown as valid JSON.

The checker rejects duplicate JSON keys, non-finite numbers, duplicate ids in
each catalogue, duplicate requirement ids, and undeclared fields.

### 2.1 Fact catalogue and predicate language

Every declared or referenced fact must resolve to one `fact_definitions[]` row:

```json
{
  "fact_id": "study.personal-data-processed",
  "value_type": "boolean",
  "allowed_values": null,
  "description": "Whether personal-data processing was declared by the author."
}
```

The value types are `boolean`, `string`, `string_enum`, `string_set`, and `date`.
`allowed_values` is required and is either null or a nonempty string list whose
use must agree with the value type.

`fact_equals` and `fact_in` accept scalar facts only: boolean, string,
string-enum, or date. A date operand must be a real ISO 8601 calendar date.
`fact_contains` is exact membership in a `string_set`; it is never substring
matching on a string. A string-set equality test is not part of V1.

`applies_if` is a closed recursive predicate AST. Its only operators are:

```json
{"op": "fact_equals", "fact_id": "study.personal-data-processed", "value": true}
```

```json
{
  "op": "fact_in",
  "fact_id": "study.type",
  "values": ["survey", "interview"]
}
```

```json
{"op": "fact_contains", "fact_id": "study.populations", "value": "competent-adults"}
```

```json
{
  "op": "all",
  "operands": [
    {"op": "fact_equals", "fact_id": "study.personal-data-processed", "value": true},
    {"op": "fact_contains", "fact_id": "study.populations", "value": "competent-adults"}
  ]
}
```

```json
{
  "op": "any",
  "operands": [
    {"op": "fact_equals", "fact_id": "study.direct-collection", "value": true},
    {"op": "fact_equals", "fact_id": "study.secondary-use", "value": true}
  ]
}
```

```json
{
  "op": "not",
  "operand": {"op": "fact_equals", "fact_id": "study.personal-data-processed", "value": false}
}
```

The checker binds operators and values to the fact definition, rejects unknown
facts/operators and excessive nesting, and never executes a string expression.

Evaluation uses Strong Kleene three-valued logic:

- a missing fact or `state=unknown` leaf is `unknown`;
- `all` is false if any operand is false, true if all are true, otherwise unknown;
- `any` is true if any operand is true, false if all are false, otherwise unknown;
- `not(true)=false`, `not(false)=true`, and `not(unknown)=unknown`.

At selected-profile scope, false emits `PROFILE_SCOPE_CONFLICT` and unknown emits
`APPLICABILITY_UNRESOLVED`; both block the downstream gate, and neither is a
legal non-applicability finding.
At requirement scope, false remains an explicit predicate result and unknown
remains unresolved. Neither is a compliance conclusion.

### 2.2 Source records and authority anchors

Each `sources[]` row separates concepts that must not be collapsed:

- `canonical_url` and nullable `snapshot_url`;
- `provision_locator` plus a closed `allowed_provisions` list;
- `effective_from` and nullable `effective_until`;
- nullable `source_amended_or_published_date`;
- `retrieved_at` and `verified_at`;
- `source_language` and boolean `controlling_language`;
- `authenticity_status`;
- nullable `content_digest` and `digest_scope`;
- `rights_status`;
- `freshness`.

The accepted authenticity values distinguish authentic official text,
official controlling-language text, authoritative-but-unofficial publication,
official consolidation, and official reference translation.

Every requirement repeats a closed `authority_anchor` containing its source id,
authority and snapshot URLs, provision, effective interval, source amendment or
publication date, retrieval and verification dates, language/control flag,
authenticity, content digest/scope, and rights status. The checker requires the
anchor to agree with its referenced source, requires that source to occur in the
profile or overlay `source_ids`, requires `provision` to occur in the source's
closed `allowed_provisions`, and requires `effective_date` to equal that
provision source's separately verified `effective_from`.

An amendment or publication date is provenance, not automatically the effective
date. In particular, the Taiwan official page's amendment date must be recorded in
`source_amended_or_published_date`; it may not be copied into `effective_from` or
`effective_date` without a separately verified legal basis. The controlling
Chinese source and official English reference translation remain distinguishable.

A future-effective, expired, stale, unverified, superseded, or
non-controlling-translation-only source produces
`AUTHORITY_SOURCE_NOT_CURRENT` and cannot enable a profile-dependent result. The
runtime resolver does not fetch or refresh sources.

### 2.3 Bounded base profiles

Every profile carries exactly the schema fields:

- `profile_id`, `profile_version`, `profile_digest`
- one `axis`
- `authority_scope_ids`
- `title` and `authority_level`
- `coverage_status=bounded_subset`
- `covered_provisions`, `known_exclusions`, and `known_gaps`
- `no_completeness_claim=true`
- `source_ids`
- profile-level `applies_if`
- `requirements`

`profile_digest` is SHA-256 over canonical profile JSON with the digest field
excluded. A context selection must match it exactly.

V1 ships three bounded subsets:

1. `us.hhs.45-cfr-46.subpart-a` on `review_ethics`;
2. `tw.mohw.human-subjects-research-act` on `review_ethics`;
3. `eu.gdpr.research-core-bounded` on `data_protection`.

The shipped US subset covers only §46.107 IRB membership and §46.116 general
informed-consent requirements. It does not present the Common Rule as a universal
US regime and does not ship scope, exemption, waiver, documentation, or other
Subpart A rows. Its source records keep the revised rule's publication
(`2017-01-19`), effective date (`2018-07-19`), and general compliance date
(`2019-01-21`, retained as the profile version) distinct. The shipped Taiwan
subset covers only Article 7 committee composition and Article 14 consent
information, without translating either into US taxonomy. The shipped GDPR
subset covers only Articles 6, 9, 13, 14, 89(1), and 89(2). Material/territorial
scope, transfers, Member State implementing law, and every registry-listed
exclusion remain gaps rather than implied coverage.

### 2.4 Requirement rows

Every profile and overlay requirement uses this exact shape:

```json
{
  "requirement_id": "tw.hsra.art7.committee-composition",
  "axis": "review_ethics",
  "title": "IRB composition",
  "summary": "Short curator summary; no vendored normative text.",
  "obligation_kind": "require",
  "obligated_actor": "research-entity-or-irb",
  "consumer_scopes": ["committee-governance", "pathway-trace"],
  "applies_if": {"op": "fact_equals", "fact_id": "review.tw-selected", "value": true},
  "structured_expectations": [
    {"field_id": "committee.member-count", "operator": "gte", "value": 5},
    {
      "field_id": "committee.external-member-fraction",
      "operator": "gte",
      "value": {"numerator": 2, "denominator": 5}
    }
  ],
  "evidence_expected": [
    {
      "evidence_id": "committee-roster",
      "held_by": "responsible-irb",
      "artifact_type": "committee-roster",
      "description": "Roster or institutional record held by the responsible IRB."
    }
  ],
  "waiver_or_exception_route": {
    "state": "not_applicable",
    "requirement_ids": [],
    "decision_maker_role": null
  },
  "authoritative_decision_maker": {
    "role_id": "responsible-irb-or-competent-authority",
    "description": "The institutionally authorized decision maker."
  },
  "interaction": {
    "collision_key": "committee.composition",
    "policy": "parallel_authorities"
  },
  "authority_anchor": {
    "source_id": "tw.moj.hsra-art7",
    "authority_url": "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=L0020176",
    "snapshot_url": null,
    "provision": "Article 7",
    "effective_date": "2011-12-28",
    "effective_until": null,
    "source_amended_or_published_date": "2019-01-02",
    "retrieved_at": "2026-08-09",
    "verified_at": "2026-08-09",
    "source_language": "zh-Hant",
    "controlling_language": true,
    "authenticity_status": "official_controlling_language",
    "content_digest": null,
    "digest_scope": "not_recorded",
    "rights_status": "curator_summary_only"
  }
}
```

The example keeps the Act's separately supported effective date distinct from
the `2019-01-02` amendment date. A committed row must verify the effective date
for its cited provision and version from the controlling authority; it must
never copy `source_amended_or_published_date` into `effective_date` by default.

`obligated_actor` and `consumer_scopes` are load-bearing. A future packet
consumer must not turn an IRB-composition obligation into an investigator packet
artifact.

The waiver/exception states are `profiled`, `external_authority_required`,
`not_profiled_in_bounded_profile`, and `not_applicable`. A profiled route records
only an available route and decision-maker role. It never means the route was
requested, applicable, or granted.

### 2.5 Additive overlays and display precedence

Each overlay carries:

- `overlay_id`, `overlay_version`, and `overlay_digest`
- `overlay_kind=institutional | funder`
- one of the two real axes
- `issuer`, `title`, and `authority_scope_ids`
- exact `target_profiles[]` id/version/digest pointers
- `source_ids`
- `operation=add | supplement | conflict`
- `requirements_removed=false`
- additive `requirements`

The checker requires every target profile to be selected exactly on the same
axis. An overlay cannot introduce a third axis or target an approximate/latest
profile.

The applicability inherited from an overlay's exact targets is the Strong
Kleene `all` of every target-profile applicability result. Each overlay
requirement is then the Strong Kleene `all` of that inherited result and its own
predicate. A false or unknown inherited result emits
`OVERLAY_BASE_UNRESOLVED`; an overlay never becomes independently applicable
when any exact base target remains false or unknown.

Precedence is used only to construct `trace_order`. Changing
`display_precedence` cannot change selection, predicate results, collision
membership, unresolved reasons, downstream eligibility, or complete requirement
accounting. It can change only display positions and therefore the resolved
digest.

Rows sharing a non-null collision key remain parallel. The resolver emits every
participating id with
`resolution=parallel_authorities_require_human_resolution` and
`requirements_removed=false`. It does not merge US and Taiwan committee rules or
deduplicate review-ethics consent requirements against GDPR information duties.

## 3. Pointer-only resolved artifact

The resolved artifact never embeds the context or registry. It binds them by
digest:

```json
{
  "schema_version": "resolved-human-subjects-authority-context/1.0",
  "context_pointer": {
    "context_record_id": "ctx.cross-border-example",
    "schema_version": "irb-context-record/1.0",
    "context_digest": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
  },
  "registry_pointer": {
    "registry_id": "ars-human-subjects-authorities",
    "registry_version": "2026.08",
    "as_of": "2026-08-09",
    "registry_digest": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
  },
  "selected_profiles": [],
  "selected_overlays": [],
  "requirement_results": [],
  "collisions": [],
  "trace_order": [],
  "resolution_state": "resolved",
  "unresolved_reasons": [],
  "downstream_gate": {
    "both_axes_selected": true,
    "exact_selection_resolved": true,
    "all_applicability_resolved": true,
    "profile_dependent_result_allowed": true
  },
  "resolved_digest": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
}
```

Selected-profile results carry exact selection fields, a `/profiles/0`-form
pointer, tri-state applicability, the recursive predicate trace, and
`source_state=current | unresolved`. Overlay results carry exact overlay fields,
an `/overlays/0`-form pointer, target profile ids, and
`requirements_removed=false`.

Every requirement result carries the authority kind/id/version/digest, axis,
actor, consumer scopes, applicability, predicate trace, requirement digest,
requirement pointer, and authority-anchor pointer. It does not copy the
requirement summary, structured expectations, evidence text, or authority anchor.

Each predicate-trace row records `expression_path`, operator, tri-state result,
nullable fact id, and declared state (`declared | unknown | missing | compound`).
Every requirement result occurs exactly once in `trace_order`, whose entries carry
only position, requirement id, authority id, and
`purpose=display_only_no_suppression`.

Resolution states are:

- `resolved`
- `jurisdiction_unresolved`
- `applicability_unresolved`

The closed unresolved codes are:

- `JURISDICTION_UNRESOLVED`
- `APPLICABILITY_UNRESOLVED`
- `OVERLAY_BASE_UNRESOLVED`
- `AUTHORITY_SOURCE_NOT_CURRENT`
- `PROFILE_SCOPE_CONFLICT`

Each unresolved-reason row is pointer-only and contains exactly `code`, `axis`,
nullable `authority_id`, and nullable `requirement_id`. It contains no prose or
free-text `detail`. `requirement_id` identifies a requirement-level reason;
profile-, overlay-, and missing-axis reasons leave it null.

`resolved` requires an empty `unresolved_reasons` array and all four downstream
booleans true. It also requires at least one selected profile on each axis,
`applicability=true` and `source_state=current` for every selected profile, and
no requirement with `applicability=unknown`. Either unresolved state requires at
least one reason and `profile_dependent_result_allowed=false`. JSON Schema
enforces those local conditions. The replay checker enforces semantic uniqueness
of profile identities and exact equality with the context selections.

The resolved digest is SHA-256 over canonical UTF-8 JSON with sorted keys and
compact separators, with the `resolved_digest` field itself excluded.
Confirmation time is excluded from the separately computed semantic context
digest, but the substantive context digest, exact selections,
registry/profile/overlay/requirement digests, predicate traces, collisions,
unresolved reasons, gates, and trace order are included.
Permutation of semantically unordered selection arrays does not change the
digest. Reconfirmation alone does not change it. A material fact, selection,
source, applicability, collision, or display-order change does.

## 4. Runtime and acceptance

The resolver is standard-library-only. It reads only the explicitly named context
and registry JSON files, rejects duplicate keys and non-finite values, and never
reads a manuscript, scans sibling files, queries a network service, or renders a
user-facing brief.

JSON Schema owns closed shapes. The deterministic checker owns cross-record id
uniqueness, exact digest matching, scope and overlay target resolution, source
semantics, Strong Kleene evaluation, recursion limits, complete requirement
accounting, collision preservation, pointer correctness, gate derivation, and
stable digests.

Consumers of a serialized result must call
`validate_resolved_context(result, context, registry)`. That checker validates
the bound context and registry, deterministically replays resolution, recomputes
the resolved digest with `resolved_digest` excluded, and requires exact object
equality with the supplied result. Schema validation alone cannot establish
cross-row uniqueness, resolve a JSON Pointer, bind a digest to an input, or prove
that a gate was derived rather than copied.

Hermetic fixtures and mutations must prove:

1. both shipped review-ethics profiles and the GDPR data-protection profile use
   the same schema and resolver path;
2. simultaneous two-axis selection works;
3. a missing or unresolved axis yields `JURISDICTION_UNRESOLVED` and cannot enable
   a profile-dependent result;
4. `funder` cannot appear as an axis and a funder overlay cannot fill an axis;
5. unknown id/version/digest, duplicate selection, and scope/axis mismatch fail;
6. omitted and explicitly unknown facts remain unknown; string booleans fail;
7. every AST operator follows Strong Kleene logic, including
   `not(unknown)=unknown`;
8. unknown fact/operator, malformed recursive nodes, and excessive nesting fail;
9. future, expired, stale, unverified, superseded, or
   non-controlling-translation-only authority degrades;
10. the Taiwan amendment date cannot be silently substituted for an effective
    date; an off-list provision or anchor source absent from its authority's
    `source_ids` also fails;
11. wrong-target overlays fail, every target of a multi-target overlay must be
    exact-selected, and `not_provided` is distinct from
    `none_declared_by_author`;
12. display-order permutations preserve selection and collisions and never
    suppress requirements;
13. cross-axis participant-information rows remain distinct;
14. a waiver/exception route is never represented as granted;
15. committee-governance rows cannot masquerade as submission-packet rows;
16. resolved output is pointer-only, carries no free-text diagnostic, and every
    pointer/digest resolves; deterministic replay rejects a schema-shaped
    pointer, digest, applicability, or gate mutation;
17. verdict, pathway, readiness, authorization, and conformance fields are rejected;
18. duplicate JSON keys and duplicate catalogue ids fail;
19. selection permutations and reconfirmation preserve the semantic digest;
20. a sibling manuscript sentinel is never read and no runtime network call occurs;
21. the existing #665 output-boundary and #668 correspondence tests remain green.

## 5. Consumer boundary and non-goals

#666 owns declaration, registry validation, resolution, and provenance only.

- #667 may later consume only an allowed resolved artifact and filter by
  `consumer_scopes` and `obligated_actor`.
- #668 remains valid in `artifact_agnostic` degraded mode; profile enrichment may
  never rewrite committee source text or authority.
- #669 may later consume exact requirement and anchor pointers to render a rule
  trace, never a determination.
- #680 owns correction and migration of mixed-jurisdiction reference prose.

V1 does not select profiles automatically, claim completeness, offer legal advice,
inspect packet prose, assess consent quality, estimate review timing, issue any
determination, migrate `irb_decision_tree.md`, or change #665's independent
readiness/authorization grammar and fixed non-authorization footer.
