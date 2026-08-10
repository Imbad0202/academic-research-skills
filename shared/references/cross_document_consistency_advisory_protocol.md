# Cross-document Consistency Advisory Protocol (`#672`)

This protocol defines the consumer and handoff boundary for the closed
`cross-document-consistency-advisory/1.0` family. The frozen design is
`docs/design/2026-08-10-672-cross-document-consistency-advisory-spec.md`.
The deterministic implementation is
`scripts/build_cross_document_consistency_advisory.py`.

The family consists of:

- `preregistration-artifact/1.0`, the persistent deep-research handoff sidecar;
- `cross-document-source-manifest/1.0`, the exact two-artifact source authority;
- `cross-document-consistency-advisory-draft/1.0`, untrusted semantic input;
- `cross-document-consistency-advisory/1.0`, the replay-finalized carrier; and
- `evidence-row/1.2`, whose only surface is
  `cross_document_consistency`.

## Advisory-only meaning

Every final carrier fixes `layer=LLM-ADVISORY` and
`evaluation_status=UNMEASURED`. The runtime does not call a model: it validates
caller-supplied semantic observations and exact evidence. Repository fixtures
measure contract behavior only. They do not measure semantic accuracy,
coverage, false-positive rate, or false-negative rate.

The only performed outcomes are
`POTENTIAL_INCONSISTENCY_LOCATED` and
`NO_LISTED_INCONSISTENCY_LOCATED`. The latter always means **not proof of
agreement, completeness, or a clean document**. An unperformed observation is
`check_state=not_checked` with a null outcome.

This carrier has no score, confidence, severity, PASS/FAIL, gate, readiness,
acceptance, authorization, terminal-policy effect, rewrite instruction, or
replacement text. It never creates or changes ClaimIntent, a revision roadmap,
author adjudication, patch authority, Integrity Report counts/verdicts, Phase E
claim rows, or Material Passport state. Consent/protocol review remains owned by
#667/#681; this family adds no consent/protocol role, enum, observation, or
consumer.

## Preregistration sidecar ownership

The research architect is a non-shell declarer. It records only the explicit
caller status and, for a completed supplied artifact, the explicitly named
companion handle. It must not hash the file, guess a digest, copy the repository
template into the handoff, or construct/update the sidecar itself.

Before the deep-research handoff, a shell-capable orchestrator invokes:

```bash
python scripts/build_cross_document_consistency_advisory.py \
  build-preregistration-artifact \
  --status <provided|not_provided|access_failed|retrieval_failed> \
  --declared-at <explicit-rfc3339> \
  ...
```

The named deterministic builder is the only owner allowed to create or update
`preregistration-artifact/1.0`. It emits exactly one record, including an
explicit unavailable receipt. It never reads an ambient clock. A `provided`
record binds the strict-UTF-8 companion's exact artifact/content SHA-256 and
byte sizes and uses `author_provided_completed_preregistration` provenance
(`synthetic_fixture` is reserved for repository tests). The unavailable states
have null paths and byte bindings, `not_provided` provenance, and the caller's
explicit RFC3339 declaration time.

The companion is explicitly named by the caller. The sidecar never embeds,
locates, fetches, or follows it. The repository file
`deep-research/templates/preregistration_template.md` is guidance only and can
never be evidence or a replacement companion.

Academic-paper intake and every pipeline handoff strict-parse and replay the
same sidecar and, when provided, the same companion bytes. They then carry both
byte-for-byte without reinterpretation. Omission, silent substitution, digest
repair, or rebuilding from prose is invalid. A later explicit user supply must
produce a new fully bound sidecar through the same builder; it cannot be spliced
into the old receipt.

## Stage 4.5 source authority and replay

The source manifest contains exactly two artifacts:

1. the designated, present accepted manuscript draft; and
2. the exact projection of the current preregistration sidecar.

All manuscript and disclosure evidence roles bind the designated accepted-draft
artifact. Only the `preregistration` role binds the preregistration artifact.
Extra, unused, or prior manuscript artifacts are invalid.

Sidecar projection is exact:

| sidecar status | manifest state | binding rule |
|---|---|---|
| `provided` | `present` | same ID/path/provenance and four byte bindings |
| `not_provided` | `source_missing` | same ID; null path/bindings; `not_provided` provenance |
| `access_failed` | `access_failed` | same ID; null path/bindings; `not_provided` provenance |
| `retrieval_failed` | `retrieval_failed` | same ID; null path/bindings; `not_provided` provenance |

If a previously provided companion is unreadable or no longer replays, the
result is `SOURCE_BINDING_INVALID`. It is not downgraded to `not_checked` and no
carrier is written.

Finalization takes only explicitly named local inputs: draft, source manifest,
sidecar, accepted draft, and the preregistration companion when provided. It
strict-parses and replay-validates the complete sidecar and source bundle before
reading any observation outcome. Its `input_binding` fixes the raw draft and
manifest SHA-256, sidecar raw SHA-256 and `record_digest`, accepted-draft artifact
ID/SHA-256, and source-bundle SHA-256. Validation and rendering require those
same inputs and rebuild the carrier byte-for-byte; a self-consistent digest alone
is insufficient.

The exact `input_binding` roster is:

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

`source_bundle_sha256` is canonical-JSON framing over the exact manifest SHA,
sidecar raw SHA/record digest, designated accepted-draft ID/SHA, and every
manifest artifact's ID, kind, state, provenance, artifact/content hashes, and
sizes in bytewise ASCII artifact-ID order. It is never raw-byte concatenation.
`report_id` is `XDOC-` plus the first 24 lowercase hex digits of SHA-256 over
canonical compact JSON containing exactly the draft SHA, manifest SHA, sidecar
raw SHA/record digest, accepted-draft ID/SHA, and source-bundle SHA. Display
`ADV-XDOC-*` and `EVR-XDOC-*` IDs derive from canonical pair/observation-key
order; callers cannot select them.

The accepted draft limit is 8 MiB, the preregistration artifact limit is 64 MiB,
and their aggregate UTF-8 limit is 72 MiB. Files are strict UTF-8, are not
normalized, and are admitted before semantic consumption.

## Pair roster and evidence

Each carrier has exactly four pair results, in this order:

1. `abstract_results` (`abstract`, `results`);
2. `discussion_results` (`discussion`, `results`);
3. `methods_reported_analyses` (`methods`, `reported_analyses`); and
4. `manuscript_preregistration` (`manuscript_report`, `preregistration`,
   `disclosure_scope`).

The performed finding vocabulary is closed:

| pair | allowed finding types |
|---|---|
| `abstract_results` | `numeric_mismatch`, `direction_mismatch`, `significance_mismatch`, `claim_strength_rung_mismatch` |
| `discussion_results` | `direction_mismatch`, `claim_strength_rung_mismatch`, `scope_or_population_overreach` |
| `methods_reported_analyses` | `declared_analysis_no_reported_counterpart`, `reported_analysis_no_declared_counterpart`, `analysis_specification_conflict` |
| `manuscript_preregistration` | `undisclosed_preregistration_deviation` |

The first three use exactly two evidence slots. The preregistration pair uses
exactly three; its manuscript disclosure witness is never optional for a
performed observation. Logical roles remain distinct even when several roles
bind the same accepted manuscript bytes.

Methods absence requires one quote and one `checked_no_match` over an exact,
non-empty, explicitly named counterpart scope. A generic, incomplete, blank, or
unprovided scope is `not_checked`, never evidence of absence. An undisclosed
preregistration-deviation observation requires manuscript and preregistration
quotes plus `checked_no_match` over the exact named manuscript disclosure scope.
An exact disclosure quote for the same `deviation_id` produces a no-listed
observation; absent or unreplayed disclosure scope makes the whole observation
not checked.

Performed no-listed observations use only `legitimate_compression`,
`same_rung_rewording`, `disclosed_deviation`, or
`other_no_listed_observation`, under their pair-specific schema branches. A
checked scope carries
`caller_declared_complete_named_scope_not_independently_authenticated`; this is
replay provenance, not independent proof of completeness. Not-checked reasons
are closed to `PAIR_CHECK_NOT_PERFORMED`, `COUNTERPART_DOCUMENT_MISSING`,
`COUNTERPART_SCOPE_NOT_PROVIDED`, `SOURCE_ACCESS_FAILED`, and
`SOURCE_RETRIEVAL_FAILED`. Missing source takes precedence, then access failure,
then retrieval failure. Invalid schema, role, digest, or replay is a contract
error and cannot be laundered into one of those receipts.

`evidence-row/1.2` is separate from 1.0 and 1.1. It carries the complete ordered
bilateral or trilateral evidence unit under
`surface=cross_document_consistency`. The legacy 1.0 Phase E shape and 1.1
authority-profile content-coverage shape, their schemas, runtime behavior, and
serialized identities remain unchanged. Versions/surfaces cannot be mixed.

Every positive quote or checked scope is exact-source bound. External text is
strictly percent-decoded once (`+` stays literal), capped at 25 Python
whitespace-split words and 1,000 Unicode code points, hashed, and replayed by a
half-open UTF-8 byte span. Overflow is rejected rather than truncated. All text
is rendered inert and defaults to `session_only/not_assessed`; shareable rows
require the paired user-declared rights value. No cache, network, retrieval,
normalization, or ambient clock participates.

The field-relative ladder in
`shared/references/claim_strength_ladder.md` is semantic caller guidance only.
There is no deterministic keyword matcher or numeric ranker, and no ladder
observation grants revision authority.

## Legacy multi-file audit non-migration

The existing Codex multi-file audit runner, its rounds/convergence state, and
its `audit_artifact_entry` gate remain separate legacy consumers. An old
multi-file audit `PASS` cannot be mapped, projected, or translated into
`NO_LISTED_INCONSISTENCY_LOCATED`. Conversely, a #672
`POTENTIAL_INCONSISTENCY_LOCATED` observation cannot be mapped, projected, or
translated into an old-audit P1/P2/P3 finding, `PASS` / `MINOR` / `MATERIAL`
verdict, gate result, convergence decision, or `audit_artifact_entry`.

#672 never invokes the legacy runner, consumes an old audit output, or writes
into its carrier. Existing audit behavior and bytes remain unchanged; the two
surfaces may be shown independently but cannot satisfy, suppress, aggregate, or
change one another.

## Pipeline coexistence with #660

#660 tortured-phrase screening and #672 run inside the **single existing**
mandatory Stage-5 entry checkpoint after the same exact Stage 4.5 PASS. The
orchestrator runs #660 first and #672 second and surfaces two independent
carriers. The exact machine join is:

```text
#660 input_binding.artifact.artifact_id
  == #672 input_binding.accepted_draft_artifact_id
#660 input_binding.artifact.artifact_sha256
  == #672 input_binding.accepted_draft_sha256
```

Neither carrier consumes, suppresses, aggregates, or changes the other. A #660
loaded-snapshot failure may still write its schema-valid degraded artifact and
exit 1; the checkpoint preserves and validates it. A #672 contract/runtime
failure writes no output and records only a bounded, redacted
`ADVISORY_UNAVAILABLE:<CODE>` diagnostic. Neither behavior changes Stage 4.5,
blocks or delays the mandatory checkpoint, requires remediation, or alters
Stage-5 dispatch after user confirmation.

Any manuscript revision makes both carriers stale. The manuscript must re-enter
integrity review, obtain a new exact Stage 4.5 PASS, and rerun #660 then #672
against the same new accepted bytes. Reusing either carrier or rerunning only one
is invalid cargo.

This advisory is not a formatter input, Phase E row, Material Passport terminal
state, or additional checkpoint. It is displayed as a separate `ADV-XDOC-*`
table at the existing checkpoint.

## Rendering, failure, and measurement limits

`render` performs the same full replay before display. One explicit page contains
at most 25 observations; `--all` does not exist. Navigation names the preceding
or next explicit page, while the complete canonical JSON remains authoritative.

On #672 failure, no schema-valid output is created or replaced. Only a closed
`ADVISORY_UNAVAILABLE:<CODE>` diagnostic of at most 80 ASCII characters is
retained; it cannot contain source/quote text, local paths, or raw exceptions.
The diagnostic is informational and nonblocking.

Held-out documentation remains `UNMEASURED`. No measurement JSON, model output,
judge record, live model/API call, expensive evaluation, semantic efficacy claim,
or clean-document claim is authorized by this protocol.
