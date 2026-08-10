# #672 — Cross-document consistency advisory

> **Status:** DESIGN-FROZEN / UNMEASURED
> **Issue:** #672
> **Dependencies:** #569, #654, #656, #667, and #681 are closed.
> **Execution boundary:** this design authorizes no live model, external API,
> network access, human or model judge, existing Codex multi-file audit run, or
> expensive evaluation.

## 1. Decision and claim boundary

ARS will add a standalone, replay-bound advisory for four logical document pairs:

1. abstract versus results;
2. discussion versus results;
3. methods versus reported analyses; and
4. manuscript report versus preregistration.

The semantic observation is supplied in a closed, untrusted draft. A deterministic
finalizer validates the draft, replays every named source and evidence span, derives
stable identifiers and digests, and emits a closed final carrier. It never decides
whether two propositions are equivalent, whether a claim moved on the field-relative
claim-strength ladder, whether a semantic counterpart exists, or whether a
preregistration deviation was adequately disclosed.

Every final carrier fixes:

```text
layer = LLM-ADVISORY
evaluation_status = UNMEASURED
```

`LLM-ADVISORY` identifies the epistemic layer of the caller-supplied observation;
it does not authorize this hermetic finalizer to call a model. `UNMEASURED` means
that the repository fixtures validate contract behavior only. They do not measure
semantic accuracy, coverage, false-positive rate, or false-negative rate.

The only performed outcomes are:

```text
POTENTIAL_INCONSISTENCY_LOCATED
NO_LISTED_INCONSISTENCY_LOCATED
```

An unperformed row uses `check_state=not_checked` and `outcome=null`. The second
performed outcome must always be rendered as:

> NO LISTED INCONSISTENCY LOCATED — not proof of agreement, completeness, or a
> clean document.

No carrier or renderer may emit `PASS`, `FAIL`, `CONSISTENT`, a scalar score,
confidence, probability, severity, readiness, acceptance, terminal-policy effect,
rewrite instruction, replacement text, or clean-document certification.

## 2. Contract ownership and compatibility

### 2.1 New evidence-row version

#672 introduces a separate closed `evidence-row/1.2` with:

```text
surface = cross_document_consistency
```

It does not widen or reinterpret either existing evidence-row contract:

- `evidence-row/1.0` remains `surface=phase_e_claim_verification` and retains its
  Phase E claim/verdict shape.
- `evidence-row/1.1` remains
  `surface=authority_profile_content_coverage` and retains its #681 authority
  requirement shape.

The implementation guard freezes these current compatibility identities:

```text
shared/contracts/evidence/evidence_row.schema.json
  02f4fc4e32658249e7065724f1cb5c2f9dcec3f599f86a1a7ffee726ae422f5a
shared/contracts/evidence/evidence_row_v1_1.schema.json
  ab7fdb15b8845bcf898fef5177c636b8ca43f2785c3b79bf284fa04a4ede14b9
scripts/evidence_rows.py
  eccfa0a5cfe9b438aac9c4ec85cd6c2ca07052de7eb521cfc1e7f799a971d7e3
shared/contracts/passport/claim_intent_manifest.schema.json
  d6c4fd060812dc2a2b2dd73b6d9e77e366fcc0803486d5f38b4def6893d70cec
shared/contracts/revision/claim_surface_manifest.schema.json
  85460c1c195c890eb505c95e2767f72461c4a1f631203b7b26decb7a841afb1d
```

The new runtime may reproduce the frozen #656 replay rules, but it must not modify
the old runtime or change its default constants, CLI behavior, serialization, or
validation behavior. A mixed-version page or a 1.2 row carrying an old surface is
invalid.

### 2.2 New draft and final carrier

The new contracts are:

```text
preregistration-artifact/1.0
cross-document-source-manifest/1.0
cross-document-consistency-advisory-draft/1.0
cross-document-consistency-advisory/1.0
evidence-row/1.2
```

The canonical implementation paths are:

```text
shared/contracts/passport/preregistration_artifact.schema.json
shared/contracts/evidence/evidence_row_v1_2.schema.json
shared/contracts/audit/cross_document_source_manifest.schema.json
shared/contracts/audit/cross_document_consistency_advisory_draft.schema.json
shared/contracts/audit/cross_document_consistency_advisory.schema.json
shared/references/cross_document_consistency_advisory_protocol.md
scripts/build_cross_document_consistency_advisory.py
scripts/test_cross_document_consistency_advisory.py
scripts/check_cross_document_consistency_advisory_integration.py
scripts/test_check_cross_document_consistency_advisory_integration.py
scripts/fixtures/cross_document_consistency/
evals/heldout/cross_document_consistency/README.md
```

`preregistration-artifact/1.0` is the closed, persistent handoff sidecar created by
deep-research and carried byte-for-byte through academic-paper and the pipeline. Its
root contains exactly:

```text
schema_version
status
artifact_id
relative_path
artifact_provenance
source_artifact_sha256
source_artifact_size_bytes
source_content_sha256
source_content_utf8_bytes
declared_at
record_digest
```

`status` is `provided`, `not_provided`, `access_failed`, or `retrieval_failed`. A
provided record has a strict UTF-8
artifact, all four exact byte bindings, explicit RFC3339 `declared_at`, and
`author_provided_completed_preregistration` provenance (or `synthetic_fixture` in
repository tests). Every unavailable record has null path/byte bindings,
`not_provided` provenance, and an explicit RFC3339 `declared_at` recording that
caller-held state. `record_digest` is SHA-256 over canonical JSON excluding
only itself. The source bytes travel as an explicitly named companion artifact;
the sidecar never embeds, locates, or fetches them.

The research architect supplies only the caller declaration and companion handle;
it never guesses a digest. Before handoff, the shell-capable orchestrator invokes
the deterministic runtime's `build-preregistration-artifact` subcommand to emit
exactly one sidecar, including an explicit unavailable receipt. Academic-paper
intake and every subsequent handoff validate and carry the same sidecar and
companion bytes without reinterpretation. A later explicit user supply creates a
new fully bound sidecar through that same builder; omission or silent substitution
is invalid. At Stage 4.5, the source manifest must project the exact current sidecar
fields and bytes. It cannot mint preregistration authority that was not present in
the handoff chain.

At Stage 4.5 the projection is exact: `provided` becomes a `present` manifest
artifact with the same ID/path/provenance/four byte bindings; `not_provided` becomes
`source_missing`; and `access_failed`/`retrieval_failed` retain the same state. All
three unavailable projections keep the sidecar artifact ID, use null relative path
and byte bindings, and use `not_provided` provenance. If a provided sidecar's named
companion later cannot be read or replayed, that is `SOURCE_BINDING_INVALID`, not a
new manifest failure receipt.

The source manifest is the standalone, closed authority for the explicitly named
session artifacts. It records its schema version, manifest ID, each logical
artifact's ID/kind/availability state, normalized relative display path (or null
when unavailable), exact raw
artifact SHA-256 and byte size, exact session-content SHA-256 and UTF-8 byte size,
closed caller provenance, and a manifest digest. Availability is closed to
`present`, `source_missing`, `access_failed`, or `retrieval_failed`. Present
artifacts require all byte bindings; the three unavailable states require null
byte bindings. It never contains or follows a filesystem pointer.

Caller provenance is closed to `author_provided_manuscript`,
`author_provided_completed_preregistration`, `synthetic_fixture`, or
`not_provided`. A present manuscript requires `author_provided_manuscript` or
`synthetic_fixture`; a present preregistration requires
`author_provided_completed_preregistration` or `synthetic_fixture`; an unavailable
artifact requires `not_provided`. These are explicit caller claims, not independent
authenticity findings. The runtime additionally rejects blank content and the exact
shipped blank guidance template at
`deep-research/templates/preregistration_template.md`, whose frozen SHA-256 is
`40054e26c527ff3dd237a5eef3fee60b821cf8549e210d48a057005333c8e0d2`;
the integration guard freezes both canonical path and digest. The runtime does not
otherwise judge preregistration authenticity or completeness.

The draft is untrusted semantic input. The final carrier binds the exact draft,
exact source-manifest bytes, and exact session source bundle and embeds every 1.2
evidence row required to support or delimit each observation. All four schemas are
closed recursively, as is the preregistration handoff sidecar.

The final carrier contains exactly four `pair_results`, in this canonical order:

```text
abstract_results
discussion_results
methods_reported_analyses
manuscript_preregistration
```

Each pair result contains at least one observation. Missing input is represented by
an explicit not-checked receipt; omission is never a clean result. The finalizer
sorts observations by their closed pair order and stable caller-supplied
`observation_key`, rejects duplicate keys, and derives `ADV-XDOC-...` display IDs.

`observation_key` is lowercase ASCII
`^[a-z0-9][a-z0-9._-]{0,199}$` and is globally unique in one draft. Canonical order
is the fixed pair ordinal above followed by bytewise ASCII `observation_key` order.
The global one-based ordinal derives both
`advisory_id=ADV-XDOC-{ordinal:06d}` and
`row_id=EVR-XDOC-{ordinal:06d}`. `report_id` is `XDOC-` plus the first 24 lowercase
hex digits of SHA-256 over canonical compact JSON containing only the exact
`draft_sha256`, `source_manifest_sha256`, `preregistration_record_sha256`,
`preregistration_record_digest`, `accepted_draft_artifact_id`,
`accepted_draft_sha256`, and `source_bundle_sha256`. IDs are never
caller-selected or locale-sorted.

### 2.3 No ClaimIntent or write authority

ClaimIntent, claim-surface manifests, revision roadmaps, author adjudication, and
revision-patch authorization are not inputs to this V1. A #672 row cannot authorize
an edit, claim-strength movement, replacement byte sequence, or revision operation.
If a user later wants to act on an advisory, the ordinary author-owned revision
workflow must obtain its own current authority.

### 2.4 Exact payload skeletons

The source-manifest root contains exactly:

```text
schema_version
manifest_id
accepted_draft_artifact_id
accepted_draft_sha256
artifacts
manifest_digest
```

Each artifact contains exactly:

```text
artifact_id
document_kind
relative_path
artifact_state
artifact_provenance
source_artifact_sha256
source_artifact_size_bytes
source_content_sha256
source_content_utf8_bytes
```

`document_kind` is `manuscript` or `preregistration`. Artifact IDs use lowercase
ASCII identifiers and are unique; the manifest array is bytewise ASCII sorted.
`accepted_draft_artifact_id` resolves exactly one present manuscript artifact, and
`accepted_draft_sha256` equals both of that artifact's raw/content SHA-256 fields.
Every manuscript-role evidence slot in V1 binds that designated artifact; only the
`preregistration` slot binds the sidecar-projected preregistration artifact.
`manifest_digest` is SHA-256 over canonical JSON of the complete manifest excluding
only that digest field. A present artifact has four non-null byte bindings; an
unavailable artifact has all four null. V1 contains exactly two artifact entries:
the one designated present accepted manuscript and the exact sidecar-projected
preregistration artifact or unavailable receipt. Extra, unused, or older
manuscript artifacts are invalid.

The advisory-draft root contains exactly:

```text
schema_version
layer
recorded_at
observations
```

Each draft observation contains exactly:

```text
observation_key
pair_kind
check_state
outcome
finding_type
negative_basis
not_checked_reason
deviation_id
deviation_domain
evidence_slots
```

All fields are structurally present; conditionally inapplicable fields are null.
`recorded_at` and quote/scope event times are explicit RFC3339 values. The draft
may be unordered; the finalizer establishes canonical order.

Each draft evidence slot contains exactly:

```text
logical_role
artifact_id
document_locator
evidence_state
anchor_value_encoded
quote_source_span_utf8
checked_scope_input
captured_at
sharing_scope
rights_basis
```

For `agent_extracted`, the encoded quote, exact caller-selected source span, and
`captured_at` are non-null and `checked_scope_input` is null. This prevents an
ambiguous repeated quote from being resolved by first-match guessing. For
`checked_no_match`, quote/span/captured_at are null and `checked_scope_input`
contains the exact span, explicit `checked_at`, and
`scope_completeness=caller_declared_complete_named_scope_not_independently_authenticated`.
Unavailable/not-checked slots carry neither quote nor scope payload.

The final carrier contains exactly:

```text
schema_version
layer
evaluation_status
report_id
input_binding
pair_results
boundary
report_digest
```

`input_binding` contains the exact draft schema/raw-byte SHA-256, source-manifest
schema/raw-byte SHA-256, preregistration-sidecar schema/raw-byte SHA-256 and
`record_digest`, designated accepted-draft artifact ID/SHA-256, and source-bundle
SHA-256. `pair_results` uses a four-item
`prefixItems` roster in the canonical order. Each final observation copies its
closed semantic fields, adds
`semantic_provenance=caller_supplied_not_deterministically_verified`, and embeds
exactly one complete evidence-row/1.2.

The exact `input_binding` member names are:

```text
draft_schema_version
draft_sha256
source_manifest_schema_version
source_manifest_sha256
preregistration_record_schema_version
preregistration_record_sha256
preregistration_record_digest
accepted_draft_artifact_id
accepted_draft_sha256
source_bundle_sha256
```

`report_digest` is the lowercase SHA-256 of canonical JSON for the complete final
carrier excluding only `report_digest` itself. It is an unkeyed integrity checksum,
not a signature or independent provenance proof; current advice still requires
exact draft/manifest/source replay. The final file SHA-256 is a separate hash over
the complete canonical bytes including `report_digest`.

`boundary` fixes all of the following to true:

```text
semantic_observation_not_recomputed
stage_4_5_verdict_unchanged
stage_5_routing_unchanged
integrity_issue_counts_unchanged
formatter_gate_unchanged
terminal_policy_unchanged
score_not_produced
automatic_rewrite_not_performed
agreement_not_certified
```

`not_checked_reason` is null for performed rows. It is required for not-checked
rows and closed to `PAIR_CHECK_NOT_PERFORMED`,
`COUNTERPART_DOCUMENT_MISSING`, `COUNTERPART_SCOPE_NOT_PROVIDED`,
`SOURCE_ACCESS_FAILED`, or `SOURCE_RETRIEVAL_FAILED`. Invalid schema, role, digest,
or replay data is a contract error and is never mapped to one of these receipts.
Failure-state precedence is deterministic: any required `source_missing` slot maps
to `COUNTERPART_DOCUMENT_MISSING`; otherwise any `access_failed` maps to
`SOURCE_ACCESS_FAILED`; otherwise any `retrieval_failed` maps to
`SOURCE_RETRIEVAL_FAILED`. With only `not_checked` slots,
`COUNTERPART_SCOPE_NOT_PROVIDED` is allowed only for methods/preregistration and
means the caller did not declare a complete named scope. For methods, exactly one
side must be `agent_extracted` and the counterpart side `not_checked`; for
preregistration, left/right must both be `agent_extracted` and only the third
`disclosure_scope` slot may be `not_checked`. Every other all-present not-checked
configuration uses `PAIR_CHECK_NOT_PERFORMED`. A lower-precedence or contradictory
reason is invalid.

## 3. Pair and role taxonomy

The pair-to-role and finding-type matrix is closed:

| `pair_kind` | left role | right role | allowed finding types |
|---|---|---|---|
| `abstract_results` | `abstract` | `results` | `numeric_mismatch`, `direction_mismatch`, `significance_mismatch`, `claim_strength_rung_mismatch` |
| `discussion_results` | `discussion` | `results` | `direction_mismatch`, `claim_strength_rung_mismatch`, `scope_or_population_overreach` |
| `methods_reported_analyses` | `methods` | `reported_analyses` | `declared_analysis_no_reported_counterpart`, `reported_analysis_no_declared_counterpart`, `analysis_specification_conflict` |
| `manuscript_preregistration` | `manuscript_report` | `preregistration` | `undisclosed_preregistration_deviation` |

Role identity is logical, not file identity. Abstract, results, discussion, methods,
and reported analyses may all bind the same manuscript artifact, path, and content
hash while retaining different role and locator identities. The implementation
must never deduplicate bilateral evidence by artifact ID, path, or SHA-256.

For `manuscript_preregistration`, the manuscript and preregistration must be
different logical artifacts. A repository template, research plan prompt, or empty
placeholder is not an author-held preregistration artifact.

Every performed preregistration observation must carry exactly one closed
`deviation_domain`:

- `hypothesis`
- `primary_outcome`
- `sample_size_or_stopping`
- `analysis_model`
- `transformation`
- `exclusion`
- `inference_criterion`
- `confirmatory_exploratory_designation`

`consent_protocol` is not a pair or role and must be rejected by schema and runtime.
Consent/protocol comparison remains owned by #667/#681; #672 adds only an interface
note to that existing authority.

## 4. Evidence-row/1.2

Every advisory observation embeds exactly one evidence-row/1.2. That row contains
an ordered `evidence_slots` array with exactly two distinct slots for the first
three pair kinds (left, then right), and exactly three for
`manuscript_preregistration` (left, right, then `disclosure_scope`). The third
slot's `logical_role` is exactly `disclosure_scope` and its document kind is
exactly `manuscript`; replacement with any other role is invalid. One
`row_sha256` covers the complete bilateral or trilateral row. A slot is present
even when its source is missing or could not be checked, so a schema-valid 1.2 row
can never be unilateral.

Each 1.2 row contains:

- its schema version, surface, row ID, pair and observation identity;
- the exact ordered slot cardinality and logical roles for that pair;
- within each slot, a non-empty named locator, explicit source-artifact and
  source-content binding, anchor/excerpt or checked-scope payload, no-cache
  declaration, and external-text sharing/rights pairing; and
- a canonical `row_sha256` over the complete row except that digest field.

The allowed evidence states are:

```text
agent_extracted
checked_no_match
not_checked
source_missing
access_failed
retrieval_failed
```

Slot state and manifest state must agree. `agent_extracted`, `checked_no_match`,
and `not_checked` require a present manifest artifact. `source_missing`,
`access_failed`, and `retrieval_failed` require the identically named manifest
state. Preregistration and disclosure roles bind the preregistration/manuscript
document kinds respectively; all other roles bind manuscript. The preregistration
artifact ID must differ from the manuscript artifact ID.

`agent_extracted` requires a quote anchor, bounded text, exact excerpt SHA-256,
strict UTF-8 half-open source span, and explicit RFC3339 `captured_at`.

`checked_no_match` requires a source-bound, exact non-empty named scope. Its
`checked_scope` block carries a strict UTF-8 half-open source span, exact scope
SHA-256, exact scope UTF-8 byte count, explicit RFC3339 `checked_at`, and
`completeness_provenance=caller_declared_complete_named_scope_not_independently_authenticated`.
It carries no quote excerpt. The finalizer replays the exact scope bytes, but the
row still records only the caller's semantic assertion that no counterpart was
located there. The deterministic finalizer neither proves semantic absence nor
proves that the named scope is complete.

`not_checked` carries an empty anchor, no checked scope, excerpt, span, or
timestamp. When its source artifact is present, it retains the exact manifest
artifact/content bindings so replay cannot substitute a later file. The three
source-unavailable states carry an empty anchor and null byte bindings, excerpt,
scope, span, and timestamp. Their failure state is provenance, not a semantic
result.

All external text follows the #656 limits:

- strict UTF-8;
- exactly one strict RFC 3986 percent decode, with `+` retained literally;
- at most 25 words by Python whitespace split;
- at most 1,000 Unicode code points;
- exact excerpt hash and exact source replay; and
- rejection, not truncation, on overflow.

External-text rows default to `session_only/not_assessed`. A
`user_confirmed_shareable` row requires `user_declared_authorized`, and the inverse
also holds. The 25-word ceiling is data minimization, not a license judgment.

## 5. State and evidence matrix

| Semantic case | left evidence | right evidence | disclosure evidence | result |
|---|---|---|---|---|
| Abstract/results or discussion/results potential inconsistency | quote | quote | absent by pair type | `performed / POTENTIAL_INCONSISTENCY_LOCATED` |
| Legitimate abstract compression | quote | quote | absent by pair type | `performed / NO_LISTED_INCONSISTENCY_LOCATED` |
| Same-rung rewording | quote | quote | absent by pair type | `performed / NO_LISTED_INCONSISTENCY_LOCATED` |
| Methods declaration with no reported counterpart | methods quote | exact named reported-analysis scope `checked_no_match` | absent | potential finding |
| Reported analysis with no declared method | exact named methods scope `checked_no_match` | reported-analysis quote | absent | potential finding |
| Analysis specification conflict | methods quote | reported-analysis quote | absent | potential finding |
| Methods/result scope missing, blank, incomplete, or not checked | available evidence or failure slot | failure slot | absent | `not_checked / null` |
| Undisclosed preregistration deviation | manuscript departure quote | preregistered-plan quote | exact named disclosure scope `checked_no_match` | potential finding |
| Disclosed preregistration deviation | manuscript departure quote | preregistered-plan quote | disclosure quote for the same `deviation_id` | no-listed result |
| Disclosure scope missing, unchecked, or unavailable | available left/right evidence | available left/right evidence | failure slot | `not_checked / null` |
| Any required counterpart document missing | available slot or failure slot | missing-side failure slot | prereg pair retains its third slot | `not_checked / null` |

A performed positive observation requires every evidence slot shown in its row.
The finalizer rejects a positive draft that omits a required quote or scope; it does
not silently downgrade a forged or structurally incomplete positive into
`not_checked`.

Every performed `manuscript_preregistration` observation has a non-empty,
schema-safe `deviation_id`, globally unique in the draft, and a closed
`deviation_domain`. Both fields live in the single observation-level evidence row
that covers all three slots. A not-checked preregistration receipt may carry both
as null; non-prereg rows require both null.

For performed no-listed observations, `negative_basis` is closed to:

```text
legitimate_compression
same_rung_rewording
disclosed_deviation
other_no_listed_observation
```

The first three are mandatory hermetic negative fixtures. `disclosed_deviation`
requires a disclosure quote bound to the same `deviation_id`; a generic disclosure
for another deviation does not satisfy it.

Outcome-dependent fields are exact: `finding_type` is required only for
`POTENTIAL_INCONSISTENCY_LOCATED`; `negative_basis` is required only for
`NO_LISTED_INCONSISTENCY_LOCATED`; each is non-null exactly when applicable and
null otherwise, and both are null for `not_checked`. Negative-basis
pair scope is closed: `legitimate_compression` only on `abstract_results`,
`same_rung_rewording` only on abstract/results or discussion/results, and
`disclosed_deviation` only on manuscript/preregistration with its same-deviation
disclosure quote. `other_no_listed_observation` is limited to the first three pair
kinds and requires quote/quote evidence. It carries no clean/agreement meaning.

The performed evidence combinations are closed: abstract/results and
discussion/results findings are quote/quote; methods declaration without result is
quote/checked-scope; reported analysis without declaration is
checked-scope/quote; methods specification conflict is quote/quote; and an
undisclosed preregistration deviation is quote/quote/checked-scope. A no-listed
legitimate-compression, same-rung, or methods-other observation is quote/quote; a
disclosed deviation is quote/quote/disclosure-quote. A not-checked observation has
at least one required slot in `not_checked`, `source_missing`, `access_failed`, or
`retrieval_failed` and has no semantic outcome fields.

## 6. Semantic limits by pair

### 6.1 Abstract versus results

The semantic caller may identify a number, direction, significance statement, or
field-relative claim-strength mismatch. An abstract's omission of detail is not by
itself an inconsistency. Legitimate compression that preserves the proposition,
direction, qualifiers, and rung is a required non-finding.

### 6.2 Discussion versus results

The semantic caller may identify direction, claim-strength, or population/scope
overreach. The only claim-strength guidance is
`shared/references/claim_strength_ladder.md`; V1 does not copy it into a second
numeric ladder or implement a deterministic keyword ranker. Same-rung rewording is
a required non-finding.

### 6.3 Methods versus reported analyses

An absence finding requires a quote on the declaring/reporting side plus
`checked_no_match` over the exact, explicitly named counterpart scope. Empty,
whitespace-only, generic, incomplete, missing, or inaccessible scope is
`not_checked`, not evidence of absence. The runtime does not infer exploratory
designation, analysis execution status, or semantic counterpart from prose.

### 6.4 Manuscript versus preregistration

A deviation is not itself a defect. `undisclosed_preregistration_deviation` requires:

1. a preregistered-plan quote;
2. a manuscript departure quote; and
3. `checked_no_match` over an exact, explicitly named manuscript disclosure scope.

If an exact disclosure quote covers the same deviation, the observation must be a
no-listed result with `negative_basis=disclosed_deviation`. If the disclosure scope
was not checked or cannot be replayed, the entire observation is `not_checked`.
V1 does not judge whether preregistration was required, timely, authentic, complete,
or whether a deviation was justified.

## 7. Deterministic finalization and replay

The finalizer accepts only explicitly named local files at the CLI boundary:

- one strict-JSON advisory draft;
- one strict-JSON source manifest; and
- one strict-JSON `preregistration-artifact/1.0` sidecar plus its explicitly named
  companion when `status=provided`; and
- the explicitly named accepted-draft UTF-8 file. A provided preregistration
  companion is the manifest's second present source and is named only once.

It performs no directory scan or pointer dereference. The separately schema-checked
`cross-document-source-manifest/1.0` binds logical artifact IDs, document kinds,
normalized relative display paths, availability state, exact raw artifact
SHA-256/byte sizes, and exact session-content SHA-256/UTF-8 byte sizes.
V1 is UTF-8-artifact-only: the explicitly named source file is both the raw artifact
and the session content. It must be strict UTF-8 without BOM or normalization, so
the raw artifact and re-encoded session-content byte streams are identical and
their SHA-256/byte-size pairs must be equal. Supporting a binary container plus a
separately extracted text stream requires a later contract version.
`source_bundle_sha256` hashes canonical compact JSON with the exact
`source_manifest_sha256`, preregistration-sidecar raw SHA-256/`record_digest`, and
designated accepted-draft ID/SHA-256 plus every manifest artifact's ID, kind, state,
provenance, artifact/content digests, and byte sizes in bytewise ASCII artifact-ID
order. Unavailable receipts remain in that framing with null bindings; raw-byte
concatenation is forbidden.
The runtime hashes bytes before consuming semantic observations, then validates the
complete source bundle and pair-role matrix before it reads observation outcomes.

The finalizer then:

1. strict-parses the closed preregistration sidecar, draft, and manifest, rejecting
   BOM, duplicate decoded
   keys, non-finite numbers, unsafe controls, surrogates, and unknown fields;
2. verifies the sidecar record digest/companion, exact sidecar-to-manifest
   projection, and designated accepted-draft ID/SHA before reading observations;
3. verifies the complete four-pair roster and source-role bindings;
4. replays each quote or checked scope against the exact source bytes;
5. derives 1.2 evidence rows, stable IDs, row digests, source-bundle digest, draft
   digest, and report digest;
6. canonicalizes pair and observation order; and
7. writes the final artifact atomically.

`validate` requires the exact draft, source manifest, preregistration sidecar and
companion (when provided), and source files and rebuilds
the expected carrier in memory. Final artifacts use strict canonical JSON: UTF-8,
no BOM or trailing newline, sorted keys, `ensure_ascii=false`, compact separators,
and no non-finite numbers. The accepted final-file bytes must equal the rebuilt
canonical bytes exactly; semantic object equality alone is insufficient. `render`
first performs that same full replay. A stale draft or source cannot be displayed
as current advice.

All timestamps are explicit RFC3339 inputs. The runtime must not read a clock, file
mtime, Git time, environment state, cache, network, model, API, subprocess, or old
Codex audit output. Invalid contract data exits nonzero and does not become an
ordinary not-checked receipt.

The runtime is standard-library-only. Exact V1 ceilings are:

```text
draft JSON bytes                    16 MiB
source-manifest JSON bytes           1 MiB
preregistration-sidecar JSON bytes   1 MiB
final-advisory JSON bytes            32 MiB
accepted-draft UTF-8 artifact         8 MiB
preregistration UTF-8 artifact       64 MiB
all UTF-8 source artifacts           72 MiB
source artifacts                      2
observations                       4,096
JSON nesting depth                   100
JSON aggregate nodes           1,000,000
render page size                      25
```

One JSON node is each decoded JSON value (object, array, string, number, boolean,
or null), including the root and every object member value/array element; member
names are not separate nodes. The node ceiling applies independently to the draft,
manifest, sidecar, and final carrier. All four use the same strict-JSON rules before
schema validation. Identifiers are at most 200 lowercase ASCII characters;
normalized relative POSIX paths are at most 1,024 Unicode code points and reject
absolute, empty, dot, parent, backslash, control, format, and surrogate components.
Equality at each limit is accepted and limit+1 fails
before unbounded allocation,
semantic consumption, or partial write. Each entry/content/output admission check
is charged before copying or expanding the admitted value.

## 8. Renderer

The `render` CLI first loads only the explicitly named draft, source manifest,
preregistration sidecar/companion, and source files and validates the complete
carrier against them. It then passes the
validated in-memory carrier to a pure renderer that performs no I/O. Each Markdown
page contains at most 25 observations in canonical order. The CLI supports
`--page` and `--page-size` with `1 <= page_size <= 25`; there is no `--all`.
The pure paginator unit tests cover synthetic lists of 0, 1, 25, 26, and 1,001
items without loss,
duplication, or reordering. The complete machine JSON remains the authority, and
every page states its index, total pages/rows, report ID/SHA, and deterministic
previous/next explicit `--page` command when that adjacent page exists.

It shows:

- advisory layer and `UNMEASURED` status;
- pair kind, left/right roles, locators, and evidence states;
- bounded inert quotes or explicit `NOT CHECKED` state;
- the third disclosure witness for preregistration observations;
- finding type or negative basis; and
- the fixed no-listed claim ceiling.

All external strings are rendered inert: HTML/control/bidirectional text and
Markdown links, images, tables, and emphasis cannot become active markup. After
the CLI's explicit replay-validation phase, the pure display function performs no
file access, retrieval, extraction, semantic inference, or rewriting.

## 9. Pipeline and consumer boundary

The advisory runs only after an exact Stage 4.5 PASS and before Stage 5 formatting.
It accompanies the exact accepted draft at the mandatory checkpoint as a separate
`ADV-XDOC-*` table. A nonzero contract/runtime result writes no schema-valid
advisory, does not create or replace the named output, and is recorded only as an
`ADVISORY_UNAVAILABLE:<CODE>` diagnostic. The closed codes are
`NAMED_INPUT_UNREADABLE`, `DRAFT_CONTRACT_INVALID`,
`SOURCE_MANIFEST_INVALID`, `SOURCE_BINDING_INVALID`,
`EVIDENCE_REPLAY_INVALID`, `FINAL_ARTIFACT_INVALID`, and `RESOURCE_LIMIT`.
The checkpoint records only this fixed prefix/code (at most 80 ASCII characters),
never source text, quote text, a local/absolute path, or an unbounded exception
message. It never
changes the already-established Stage 4.5 verdict, blocks or delays the mandatory
Stage-5 checkpoint/dispatch, requires remediation, or changes routing. Stage 5
proceeds under its existing authority once the user confirms that checkpoint.

The carrier must not enter or alter:

- Integrity Report `phases.*`, `overall_issues`, or `verdict`;
- C2 issue counts or `Internal Consistency Pass/Fail`;
- Phase E claim verdicts or evidence rows;
- audit `PASS/MINOR/MATERIAL`, P1/P2/P3, round, or convergence state;
- Material Passport readiness, acceptance, terminal policy, or formatter markers;
- revision-roadmap, author-adjudication, or patch-authorization state; or
- automatic correction routing.

If a completed preregistration artifact exists, the deep-research handoff carries
its exact artifact identity/hash and explicit session content through academic-paper
to the Stage 4.5 checkpoint without modifying it. If it is not provided, the
manuscript/preregistration pair remains explicitly not checked. The repository
preregistration template is guidance, never substitute evidence.

Consent/protocol consistency remains an interface note pointing to #667/#681. No
consent/protocol enum, fixture, semantic observation, or consumer is added here.

### 9.1 Coexistence with #660 at the one Stage-5 entry checkpoint

#660 tortured-phrase screening and #672 share the single checkpoint after the same
exact Stage 4.5 PASS. The orchestrator binds both to the identical accepted-draft
bytes/SHA-256, runs #660 first and #672 second, and surfaces two independent
carriers. Ordering is operational only; neither consumes, suppresses, aggregates,
or changes the other.

The machine join is exact: #660
`input_binding.artifact.artifact_id/artifact_sha256` must equal #672
`input_binding.accepted_draft_artifact_id/accepted_draft_sha256`. The #672 source
manifest contains no other manuscript artifact, and every manuscript/disclosure
slot binds this designated ID. Any ID or digest mismatch rejects the #672 carrier
as stale/substituted diagnostic evidence without changing pipeline routing.

Their failure semantics remain deliberately distinct. A #660 loaded-snapshot scan
may write a schema-valid degraded artifact and exit 1; the checkpoint preserves and
validates that artifact under #660's contract. A #672 contract/runtime failure
writes no output and records only the closed `ADVISORY_UNAVAILABLE:<CODE>`
diagnostic above. Neither result changes Stage 4.5, the mandatory checkpoint, or
Stage-5 routing.

Any later manuscript revision makes both carriers stale simultaneously. The draft
must re-enter the existing integrity route, obtain a new exact Stage 4.5 PASS, and
then rerun #660 followed by #672 against the new accepted bytes. Reusing either old
carrier or rerunning one without the other is invalid pipeline cargo.

## 10. Existing multi-file coverage: reuse and non-migration

| Existing surface | #672 treatment |
|---|---|
| Integrity C2 number/arithmetic/table-to-body checks | unchanged; never consumes #672 rows |
| Multi-file template bundle inventory and §3.4 internal coherence concepts | conceptual input only |
| Multi-file §4(f)(iii) abstract/body hedge rule | semantic guidance for `abstract_results` only |
| Multi-file audit runner, P1/P2/P3, PASS/MINOR/MATERIAL, rounds, convergence | not invoked or migrated |
| `audit_artifact_entry` stage gate | never produced or consumed by #672 |
| F6 bilingual abstract check | remains separate |
| #261 caption/data fidelity | remains separate |
| #569 claim-strength ladder | sole field-relative rung guidance; no deterministic ranker |
| #667/#681 consent/protocol authority | interface note only |

An old multi-file audit PASS cannot be translated into
`NO_LISTED_INCONSISTENCY_LOCATED`. Conversely, an #672 potential inconsistency
cannot be translated into an old audit issue or gate result.

## 11. Fixtures and measurement boundary

The repository ships invented, redistributable hermetic fixtures for:

- one positive observation for each of the four pair kinds;
- legitimate abstract compression;
- same-rung rewording;
- a disclosed preregistration deviation;
- a missing counterpart;
- an empty or incomplete counterpart scope;
- both directions of methods checked-no-match; and
- the preregistration three-witness rule.

The fixtures are caller-supplied semantic labels used to test mapping and replay.
They are not a held-out semantic benchmark. The held-out directory contains only a
README stating `UNMEASURED`; it contains no `measurement-*.json`, raw model output,
judge record, or accuracy claim.

## 12. Acceptance and kill mutations

The implementation is acceptable only when hermetic mutations prove all of the
following:

1. evidence-row 1.0/1.1 schemas and runtime identities above are unchanged;
2. wrong evidence version/surface, unknown pair/role/finding, role swap, duplicate
   pair, duplicate observation, and incomplete four-pair roster fail closed;
3. same-file roles remain distinct and cannot be deduplicated by path/hash;
4. a sidecar/manifest-declared unavailable counterpart is not checked, never
   performed/no-listed; a previously provided companion that later becomes
   unreadable is a contract failure with no carrier;
5. every performed positive has all required replay-bound evidence;
6. methods absence without an exact named nonblank scope fails;
7. preregistration positive without its third checked-no-match witness fails;
8. a disclosure quote for the same deviation cannot remain an undisclosed finding;
9. source, artifact, role, locator, quote, UTF-8 span, timestamp, draft digest,
   source-bundle digest, row digest, or report digest tampering fails replay;
10. malformed/double percent decoding, 26 words, 1,001 code points, BOM, duplicate
    keys, non-finite values, unsafe controls, surrogates, traversal, and resource
    limit+1 fail closed;
11. legitimate compression, same-rung rewording, and disclosed deviation remain
    no-listed observations with the fixed non-agreement wording;
12. runtime and tests contain no model, API, judge, network, subprocess, cache,
    ambient clock, directory scan, or legacy audit invocation;
13. renderer is inert, never exceeds 25 per page, has no `--all`, paginates
    deterministically, and never reads sources without full replay;
14. no PASS/FAIL/consistent/score/severity/gate/authorization/rewrite field or
    effect can be injected;
15. old C2, Phase E, multi-file audit, F6, #261, #660, #667/#681, and #670 behaviors are
    unchanged and cannot consume the new carrier;
16. README, protocol, CHANGELOG, and held-out notes make no efficacy, coverage,
    accuracy, agreement, or clean-document claim;
17. preregistration-sidecar omission, substitution, record/raw digest drift,
    companion drift, status/provenance/path mismatch, projection widening, template
    substitution, and later unreadability all fail before semantic consumption;
18. #660/#672 accepted-draft ID/SHA mismatch, suppression of either carrier,
    reversed/merged error semantics, and reuse of either carrier after revision all
    fail, while their fixed #660-then-#672 order and independent nonblocking results
    remain intact; the accepted-draft 8 MiB equality is accepted and 8 MiB+1 is
    rejected consistently with frozen #660 admission; and
19. the non-shell research architect never computes a digest; only the named
    deterministic builder may create/update the handoff sidecar.

Closure requires schema checks, focused and adjacent tests, direct integration
guards, CI-manifest lint, version/mirror checks, ruff, py_compile, diff-check, and
an independent adversarial review at 0 P1 / 0 P2. No live model, external API,
judge, or expensive evaluation is required or authorized.
