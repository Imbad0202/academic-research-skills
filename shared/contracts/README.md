# ARS Shared Contracts

Schema files for cross-skill contracts: reviewer sprint contracts, Material Passport
ports, and (v3.6.7+) cross-model audit artifact pipelines.

## PDF read-integrity and optional content advisory (#512 follow-up)

- `pdf/pdf_read_preflight.schema.json` accepts the unchanged legacy structural sidecar
  or the all-or-nothing opt-in content extension. In that extension, `verdict` is
  explicitly `verdict_scope: STRUCTURE_ONLY`; `OCR_RECOMMENDED` never rewrites that
  structural value into a content claim. The schema binds the legacy shape to tool
  version 1.0.0 and the extension shape to 1.1.0.
- `pdf/pdf_content_classifier_worker.schema.json` closes the stdout of the fixed
  isolated worker to two classifications, three unavailable reasons, finite bounded
  confidence, and bounded non-negative page indexes. Runtime additionally binds every
  page to the structural page count.
- `pdf/pdf_content_classifier_diagnostic.schema.json` is the separate POSIX-only,
  local mode-`0600` operator artifact. Platforms without `fchmod` reject its CLI
  option before path creation. Its explicitly untrusted detail is capped and never
  copied into or referenced by the sidecar. File-writing CLI invocations use
  conservative NFC/casefold keys, path resolution, and existing-inode checks to reject
  aliases before worker launch; the stdout-only legacy path adds no such precondition.
  POSIX sidecar output pre-binds the parent dirfd/inode, then uses a private `0700`
  fixed-name staging directory and anchored dirfd-relative publication. Open-inode
  checks reject staging entry swaps; atomic final-entry replacement does not follow
  post-check links. Non-POSIX output fails closed; stdout classification remains
  available. The diagnostic parent is likewise dirfd-bound before the worker. These are
  instantaneous inode postconditions, not a general same-UID sandbox; callers control
  the output parent. A failed diagnostic unlinks only the no-follow leaf still matching
  its created fd inode, preserving the primary error and any attacker replacement while
  keeping its exclusive path retryable.

Runtime: `scripts/pdf_read_preflight.py` and
`scripts/pdf_content_classifier_worker.py`. Frozen opt-in scope and residual risk:
`docs/design/2026-08-13-512-pdf-content-classification-sandbox-spec.md`.

## Claim-standing candidate ledger (#655 Track A)

- `claim_standing/query_plan.schema.json` (`claim-standing-query-plan/1.0`)
  binds one exact high-impact checkpoint claim, at most three accepted queries,
  at most four discovery-index identities, filters, authorized content class,
  frozen caps, and retrieval-only consent through a closed consentable-plan
  projection.
- `claim_standing/retrieval_input.schema.json`
  (`claim-standing-retrieval-input/1.0`) carries already-retained,
  adapter-neutral attempts, closed retry-authorization receipts, raw hits,
  explicit version relations, and caller-supplied relevance success/failure
  evidence bound to exact claim/candidate inputs and canonical prompt bytes.
- `claim_standing/candidate_ledger.schema.json`
  (`claim-standing-candidate-ledger/1.0`) preserves every attempt and raw-hit
terminal state while recording deterministic work-family selection.

Provider retention disclosure is also closed: `known` requires a non-empty
reference and `unknown` requires null.

The schema-level `\\S` checks are portable first screens. The runtime applies a
single NFKC visible-semantic-text predicate to the claim/query, disclosure,
identity, available-abstract, successful-assessment, and failure-detail
surfaces; it rejects surrogates and text made only of Unicode control/format,
separator, combining, whitespace, or punctuation characters. Failed malformed
assessment raw output remains exact evidence and may itself be whitespace- or
format-only. DOI text is stable identity only when strict NFKC/prefix-trimmed
`10.<4-9 digits>/<suffix>` validation succeeds.

The pure local finalizer is
`scripts/build_claim_standing_candidate_ledger.py`; the authoritative boundary
is `shared/references/claim_standing_candidate_ledger_protocol.md`. This slice
has no discovery adapter, network/model call, stance classification, rendering,
evidence-row extension, pipeline hook, or held-out dispatch. It is an offline
substrate only, remains unmeasured, and does not close #655.
Its CLI never creates an output for a `session_only` plan. `build --output`
requires the existing, hash-bound `explicit_local_export` consent state; there
is no command-line override. Authorized output must exactly match the
hash-bound absolute `authorized_output_path`, is exclusive/no-follow where the host
supports it, mode `0600` from creation, file- and directory-fsynced, and
truthfully carries the consented persistence/export/path state at the ledger root
and in each work family's sharing scope. Its separate rights basis remains
`not_assessed`; local persistence consent is not a rights claim.

## Codex subscription citation transport (#630)

- `cross_model/codex_citation_request.schema.json` — closed, bounded data-only
  request for one citation; no path or caller-authored prompt is representable.
- `cross_model/codex_citation_receipt.schema.json` — closed verdict plus exact
  app-server search-result bindings and a fixed containment receipt.

Runtime: `scripts/cross_model_codex_transport.py`. Protocol and limitations:
`shared/cross_model_verification.md`. Frozen design:
`docs/design/2026-08-11-630-codex-subscription-citation-transport-spec.md`.
The adapter is scoped to Stage 2.5 / 4.5 citation-integrity calls and is not a
general DA, reviewer, judgment, or handoff transport.

## Sprint contracts (v3.6.2+)

Sprint contract templates for reviewer hard-gate orchestration.

Schema: `shared/sprint_contract.schema.json` (Schema 13).
Validator: `scripts/check_sprint_contract.py`.
Spec: `docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md`.
Protocol: `academic-paper-reviewer/references/sprint_contract_protocol.md`.

### Shipped templates

**v3.6.2 (reviewer family)**:

- `reviewer/full.json` — panel 5, 5 dimensions, 4 failure conditions
- `reviewer/methodology_focus.json` — panel 2, 2 dimensions, 3 failure conditions

**v3.6.6 / suite v3.6.8 (generator-evaluator family)**:

- `writer/full.json` — single-agent writer, 7 dimensions (D1 section_completeness / D2 citation_density / D3 argument_blueprint_fidelity / D4 total_word_count / D5 per_section_word_count / D6 acknowledged_limitations / D7 register_consistency), 5 failure conditions (F1 / F4 / F2 / F3 / F0). No `scoring_plan` field.
- `evaluator/full.json` — single-agent evaluator, 5 dimensions (D1 originality / D2 methodological_rigor / D3 evidence_sufficiency / D4 argument_coherence / D5 writing_quality), 7 failure conditions (F1 / F2 / F3 / F6 / F4 / F5 / F0). Carries full `scoring_plan` + `disagreement_handling`.

Both writer + evaluator templates ship under Schema 13.1 (allOf branches 11/12 require `pre_commitment_artifacts` for `writer_full` and `disagreement_handling` for `evaluator_full`; branches 5/6 pin `failure_conditions[].action` to mode-specific enums; branches 8/9 pin F0 contains to the mode's accept variant). Orchestration block lives in `academic-paper/SKILL.md` § "v3.6.6 Generator-Evaluator Contract Protocol" + the writer/evaluator agent files.

### Reserved reviewer modes without shipped templates

`reviewer_calibration` and `reviewer_guided` are in the schema enum but ship without
templates. Those modes continue to operate in their existing form (no contract, no
hard-gate) until a follow-up patch release adds their templates. `reviewer_re_review`
left the Schema 13 enum with #576 Spec B: re-review is governed by the dedicated
contract family under `re_review/` (four schemas + `scripts/check_re_review_synthesis.py`),
not by a Schema 13 template — a contract claiming `mode: reviewer_re_review` no longer
validates.

### How to add a new template

1. Add the file under `shared/contracts/<domain>/<mode>.json`.
2. Run `python scripts/check_sprint_contract.py <path> --ars-version vX.Y.Z`; expect
   zero errors and zero soft warnings.
3. If `expression` strings use new phrasing, update `sprint_contract_protocol.md`
   and the synthesizer prompt's recognised-pattern list in the same PR.

## Passport contracts (v3.6.4+)

Schemas for Material Passport input ports.

- `passport/literature_corpus_entry.schema.json` (v3.6.4) — Schema 9 `literature_corpus[]`
  entries produced by user-written adapters.
- `passport/bibliographic_integrity_signal.schema.json` (#678/#651/#660) — v1.0
  additive signal carrier, v1.1 authoritative retraction-status rows, and the
  v1.2 title/abstract tortured-phrase advisory profile,
  including resolver disagreement/reinstatement, judgment context, freshness,
  and opt-in finalizer policy eligibility. The separate
  `retraction_status_cache_v1` namespace and pure resolver live in
  `scripts/retraction_status.py`.
- `passport/rejection_log.schema.json` (v3.6.4) — adapter output companion logging
  entries that could not be included in the corpus.
- `passport/reset_ledger_entry.schema.json` (v3.6.3) — `reset_boundary[]` ledger entries
  for the opt-in passport reset boundary protocol.
- `passport/audit_artifact_entry.schema.json` (v3.6.7 Step 6) — `audit_artifact[]` entries
  recording one cross-model audit run per downstream-agent deliverable. Two lifecycle
  states (proposal / persisted) share the schema via `oneOf`. Cross-artifact invariants
  are enforced by `scripts/check_audit_artifact_consistency.py`. Spec:
  `docs/design/2026-04-30-ars-v3.6.7-step-6-orchestrator-hooks-spec.md` §3.1-§3.2.
- `passport/version_records.schema.json` (Kong #258) — optional
  `phase2_investigation/version_records.yaml` sidecar for academic citation version
  families (preprint -> proceedings -> journal extension). This is deliberately a
  sidecar: `literature_corpus_entry.schema.json` stays adapter-owned and unmodified.
- `passport/human_read_log.schema.json` (#513) — the user-owned human-read ledger
  (`<passport-stem>_human_read_log.yaml`, written by `scripts/ars_mark_read.py`),
  including the optional #513 `read_scope` honest-coverage attestation
  (`level`/`locators`/`note`, declaration-only). Deliberately a sidecar for the same
  reason as above: corpus entries MUST NOT carry human-read state (v3.6.8 firm rule 3).
  Audit/test-time validation only — the CLI stays dependency-light at runtime.

## Shared evidence rows (#656)

`shared/contracts/evidence/evidence_row.schema.json` defines the closed
`evidence-row/1.0` carrier for evidence shown at human-adjudication checkpoints.
V1 has one consumer discriminator, `surface: phase_e_claim_verification`: the
Stage 2.5/4.5 Phase E Claim Verification Report persists
one row per `(claim_id, ref_slug, anchor)` at Integrity Report
`phases.E_claims.evidence_rows[]`. The array is additive: a positively identified
pre-#656 report may omit it and, only with `--allow-legacy-absence`, renders
exactly `LEGACY — EVIDENCE ROWS UNAVAILABLE`; missing shape alone is not legacy
proof and never means that evidence was checked. The opt-in Stage 4→5
`claim_audit_results[]` contract is a separate lifecycle and is unchanged.

The one evidence-state vocabulary is:

- `verified_exact_match` — a once-decoded writer `quote` anchor matched the
  exact session-held source string;
- `agent_extracted` — a `page`/`section` passage selected by the auditing agent,
  also exact-substring checked, but labeled non-authoritative because passage
  selection is agent judgment;
- `unconfirmed_anchor` — session source was present but the writer's decoded
  quote did not match it;
- `not_checked`, `source_missing`, `access_failed`, `retrieval_failed`, and
  `anchorless` — explicit empty states. V1 maps `paragraph` to `not_checked` and
  `none`/a missing marker to `anchorless`.

These states describe excerpt provenance/availability only. They never compute
or change the independent Phase E `verdict`, issue severity/count, or PASS/FAIL
decision. Viewing a row is not reading the source: the runtime never reads or
writes `human_read_log`, never invokes `/ars-mark-read`, and never affects
LOW-WARN/read-scope promotion.

`scripts/evidence_rows.py` is the standard-library-only normative runtime:

```python
strict_percent_decode(value)
build(row, session_source_or_none, *, extracted_text=None,
      failure_state=None, cached_row=None)
validate(row, session_source_or_none=None)
paginate(rows, page=1, page_size=25)
render_markdown(rows, page=1, page_size=25, *, session_sources=None)
render_html(rows, page=1, page_size=25, *, session_sources=None)
```

The decoder is strict UTF-8 and runs exactly once (`+` is not a space;
`%2520` becomes the literal `%20`). Positive excerpts must be an exact
contiguous substring of the explicitly supplied session source. Quote anchors
and excerpts are each capped at 25 words by whitespace split and 1000 Unicode
code points. `source_content_sha256` hashes the exact session source encoded as
UTF-8 with no Unicode, whitespace, or newline normalization;
`source_artifact_sha256` hashes optional raw artifact bytes and never substitutes
for the content hash. UTF-8 byte offsets bind an excerpt to the content hash.
`row_sha256` covers canonical JSON for the complete row except the digest field
itself. It is an unkeyed integrity checksum, not a signature or independent
proof of provenance. Source-bound trust is established by replaying the row
against explicitly supplied session source text. Direct Python
`validate(row)` without its optional source argument checks only closed shape,
cross-fields, and self-contained integrity; it does not prove source provenance.

Cache keys bind schema/surface, claim and citation identity, source-content
hash, decoded anchor, resulting state, and (for `page`/`section`) the candidate
excerpt hash. A key match is replay-validated against the current session
source before reuse. Hits preserve the original excerpt and `captured_at`, then
set `cache.status: hit` and recompute `row_sha256`. Claim/source/content/candidate
drift is a miss. A corrupt candidate is ignored and rebuilt from current explicit
inputs; it is never returned as a hit. Current explicit failure states win without
reading cached evidence; failure/empty states are never cached.

Renderers are pure functions over persisted rows plus the explicit in-memory
`session_sources` mapping supplied by their caller. Every source-bound row must
have a matching `ref_slug → exact source text` entry and is replay-validated
before anything is displayed; missing or drifting text fails closed. Empty-state
rows need no source map. The renderer does not accept or follow a source pointer,
URL, DOI, retrieval client, model, cache, or read ledger. Integrity validation
checks the stored encoded/decoded-anchor relationship; display does not decode or
alter the stored anchor again. Markdown and HTML external strings are rendered
inert, including percent-decoded markup, table delimiters, bare URLs/email,
newlines, all Unicode `Cc`/`Cf` controls, and U+2028/U+2029. A render page contains
at most 25 rows, preserves document order, reports total/page bounds and
deterministic previous/next/explicit-page navigation, and never silently
truncates. There is intentionally no `--all`; any number of persisted rows
remains accessible by page.

For any Integrity Report wrapper with `evidence_rows` present, the adapter
requires integer `E_claims.checked` and `E_claims.verified`; it checks that unique
evidence `claim_id` count equals `checked`, unique `VERIFIED` claim count equals
`verified`, and every row sharing a claim ID carries the same claim object and
claim-level verdict. Thus `checked > 0` with an empty present array fails. Raw
single-row and row-array inputs remain valid standalone runtime inputs. Only an
absent `evidence_rows` field is legacy-compatible. Exact omission
of a selected `(claim_id, ref_slug, anchor)` tuple cannot be proved from this
wrapper alone because the E1 selected-tuple registry is not machine-carried here;
the current producer must enforce that completeness before handoff.

Rows containing an excerpt or decoded quote anchor default to
`session_only`/`not_assessed`. Only an explicit user declaration may set the
paired `user_confirmed_shareable`/`user_declared_authorized` values. The length
limit is data minimization, not a licence, copyright exception, or publication
right; exported reports must retain the row handling label/caveat or strip the
external text.

Validate persisted rows or render exactly one page. On both CLI commands, any
source-bound row requires replay from an explicit `ref_slug → source text` JSON
map:

```bash
python scripts/evidence_rows.py validate evidence-rows.json \
  --source-map session-sources.json

python scripts/evidence_rows.py render evidence-rows.json \
  --format markdown --page 1 --page-size 25 \
  --source-map session-sources.json
```

`--source-map` is required whenever either CLI command receives a document with
a source-bound state; it is the only extra file the command opens. Missing
`evidence_rows` is a render failure by default. A positively identified pre-#656
Integrity Report renders the exact fixed legacy label with exit 0 only when the
caller adds `--allow-legacy-absence`; `validate` always rejects the absence.
Current producers may never use the compatibility flag.

`shared/contracts/evidence/evidence_row_v1_1.schema.json` is the separately
versioned extension for `surface: authority_profile_content_coverage` (#681).
It replaces Phase E claim/verdict fields with exact authority-requirement,
structured-expectation, packet-artifact, and document-locator bindings. Its
states are `agent_extracted`, `checked_no_match`, `not_checked`,
`source_missing`, `access_failed`, and `retrieval_failed`; they describe only
the provenance or absence of one bounded advisory passage. The shared 25-word,
1,000-code-point, strict once-decode, exact UTF-8 replay, inert rendering,
rights, and human-read-ledger boundaries still apply. V1.1 performs no cache
lookup. `scripts/evidence_rows.py` exposes `build_advisory(...)` for this
surface, while the existing `evidence-row/1.0` builder and rendered bytes remain
unchanged. The versioned surfaces cannot be mixed in one page.

`shared/contracts/evidence/evidence_row_v1_2.schema.json` is the separate closed
version for `surface: cross_document_consistency` (#672). It binds one complete
ordered bilateral or trilateral advisory observation to the exact accepted
manuscript and optional completed-preregistration bytes. It is finalized only by
`scripts/build_cross_document_consistency_advisory.py`; the existing 1.0/1.1
schemas and `scripts/evidence_rows.py` identities and behavior remain unchanged.

## Non-ranking revision authority (#670)

The current reviewer-to-author revision family lives under `revision/`:

- `revision_roadmap.schema.json` — immutable reviewer-owned
  `revision-roadmap/1.0`, exact draft/manifest bindings, source-trace order,
  independent severity/obligation/cost/consequence, and proposed target scopes;
- `claim_surface_manifest.schema.json` — exact registered Claim Intent surfaces,
  raw UTF-8 spans, hashes, blocks, current rungs, and byte-identical equality
  between every protected surface and its referenced ClaimIntent `claim_text`;
- `author_adjudication_input.schema.json` and
  `author_adjudication.schema.json` — explicit session-author choices and the
  deterministic raw-hash-bound sidecar; and
- `integrity_correction_list.schema.json` plus the integrity authorization
  input/output schemas — proposal-only issues and explicit author approval of
  the complete exact patch SHA-256; and
- `revision_evidence_bundle.schema.json` plus the integrity receipt schema
  — a continuous local chain from exact integrity PASS through current
  review-write/no-op/integrity rounds to the final draft.

`scripts/revision_roadmap.py` builds, validates, renders, and bundle-replays this
family without a model, network, API, directory scan, or ambient clock. It opens
only explicitly named local artifacts through containment, symlink, and
read-once guards. Bundle validation reruns the pure current patch engine for
every write round and requires byte-exact replay output to equal the named post
draft; rewritten artifact/report hashes cannot substitute for authorized bytes.

The current patch schema accepts only format 1.1 and separates
`review_roadmap` from `integrity_correction` authority. Registered claim
replacements and declined-overlap collateral authority are exact and
single-use. An integrity issue list grants no write by itself: apply requires a
separate author sidecar whose explicit input already carries the exact proposed
patch digest. Apply report 1.3 records the replayed witness and explicitly leaves
unregistered semantic drift to E6 review. Patch 1.0 lives only under
`patch/legacy/v1_0/` with its archived loader.

The current #576 `re_review/` family is version 1.1, uses
`obligation_class`, hard-requires original/revised drafts, roadmap, author
sidecar, and bundle, and copies
author fields exactly into Schema 11. Version 1.0 is archived under
`re_review/legacy/v1_0/`; mixed chains are invalid.

Spec: `docs/design/2026-08-10-670-non-ranking-revision-roadmap-spec.md`.

## Human-subjects correspondence contract (#668)

`human_subjects/committee_correspondence.schema.json` defines the standalone
`academic-paper revision-coach` committee-correspondence variant. It binds every
confirmed source comment to one concern record while preserving the entire UTF-8
letter byte-for-byte, including non-comment material. The contract carries
multi-label actions, explicit authority/provenance, optional profile enrichment,
fixed unresolved placeholders, the #665 administrative boundary, and no model
priority or severity.

Validate a bundle with:

```bash
python scripts/check_committee_correspondence.py \
  committee_correspondence/<source-sha12>/concern_tracker.json
```

The checker recomputes file/segment hashes, contiguous byte coverage, exact
comment-to-concern accounting, source order, full-permutation working views, and
response-skeleton coverage. Spec:
`docs/design/2026-08-08-668-committee-correspondence-spec.md`.

## Human-subjects authority context (#666)

The `human_subjects/` authority family keeps selection explicit and separates three
closed artifacts:

- `irb_context_record.schema.json` — the author-confirmed facts plus exact,
  axis-qualified profile and overlay pins;
- `authority_profile_registry.schema.json` — curator-owned, versioned, bounded
  profiles and row-local source anchors;
- `resolved_authority_context.schema.json` — a pointer-only, deterministic
  three-valued applicability trace and downstream gate.

V1 has exactly two axes: `review_ethics` and `data_protection`. Institutional and
funder rules are additive overlays, never a third axis; display precedence cannot
remove, merge, or satisfy a requirement. The shipped registry demonstrates the
same contract with bounded US 45 CFR 46, Taiwan Human Subjects Research Act, and
GDPR research subsets. It is not a completeness, compliance, pathway, exemption,
or authorization claim.

Resolve an explicit context offline, lint the registry alone, or replay-check a
serialized result before consuming it:

```bash
python scripts/resolve_human_subjects_authority.py \
  --context context.json \
  --registry shared/human_subjects_authority_registry.json \
  --output resolved-authority-context.json

python scripts/resolve_human_subjects_authority.py \
  --registry shared/human_subjects_authority_registry.json \
  --check-registry

python scripts/resolve_human_subjects_authority.py \
  --context context.json \
  --registry shared/human_subjects_authority_registry.json \
  --check-resolved resolved-authority-context.json
```

The resolver is standard-library-only, opens only named files, evaluates a closed
Strong-Kleene predicate AST, never infers a jurisdiction, and rejects duplicate
JSON keys and non-finite numbers. Protocol:
`shared/references/human_subjects_authority_protocol.md`. Spec:
`docs/design/2026-08-09-666-human-subjects-authority-contract-spec.md`.

## Human-subjects submission-packet manifest (#667)

Two closed contracts define the deterministic packet layer:

- `shared/contracts/human_subjects/submission_packet_inventory.schema.json` — an author-declared
  list of exact packet-relative files, byte digests, evidence bindings, responsible
  holder roles, declared structure metadata, waiver/exception claims, and
  caller-supplied authorization status; and
- `shared/contracts/human_subjects/submission_packet_manifest.schema.json` — the pointer-only,
  replay-bound result with five structural status tokens, exact requirement and
  evidence pointers, independent #665 readiness/authorization fields, and the
  fixed non-authorization boundary.

The checker consumes a #666 authority result only after exact replay against its
named context and registry. It filters to `submission_packet` consumer rows and
uses only `evidence_expected` ids, artifact types, and holders. It never evaluates
or copies `structured_expectations`, descriptions, or attachment prose; exact
whole-row bytes are canonical-hashed only for replay integrity. It never infers a
jurisdiction, grants a waiver, verifies institutional acceptance, or updates the
caller-supplied authorization value. An evidence row is packet-owned only when
both its exact obligated actor and exact expected holder occur in the declared
packet-responsibility roles. Declared version, date, signature, and certificate
metadata is syntax/internal-consistency only unless a separately versioned,
source-backed mechanical expectation exists.
Once the authority and capability gates permit packet observation, every
inventoried path retains a `DOCUMENTED` or `CONFLICTING` row for
declared-vs-attached visibility, including extra files not consumed by the
selected profiles. A closed gate leaves observations empty and does not open the
packet root. Observation status alone does not change readiness; only an
applicable packet-owned evidence entry can create a listed packet gap.
The runtime rejects more than 512 copied consumer scopes, more than 4,096 entry
or exclusion rows, and any final canonical manifest larger than 8 MiB, ensuring
that every successful build can be replayed by the same CLI.

Build, replay-validate, or render a manifest offline with:

```bash
python scripts/build_submission_packet_manifest.py build \
  --inventory inventory.json \
  --packet-root packet \
  --context context.json \
  --registry shared/human_subjects_authority_registry.json \
  --resolved resolved-authority-context.json \
  --output submission-packet-manifest.json

python scripts/build_submission_packet_manifest.py validate \
  --manifest submission-packet-manifest.json \
  --inventory inventory.json \
  --packet-root packet \
  --context context.json \
  --registry shared/human_subjects_authority_registry.json \
  --resolved resolved-authority-context.json

python scripts/build_submission_packet_manifest.py render \
  --manifest submission-packet-manifest.json \
  --inventory inventory.json \
  --packet-root packet \
  --context context.json \
  --registry shared/human_subjects_authority_registry.json \
  --resolved resolved-authority-context.json
```

The authority triplet is all-or-none. An intentionally absent triplet produces an
unresolved manifest without a default profile; a partial or mismatched triplet is
a contract error. `render` requires the same inputs and exact replay, so a
self-consistent but forged manifest digest is insufficient.

Protocol: `shared/references/submission_packet_manifest_protocol.md`. Spec:
`docs/design/2026-08-09-667-submission-packet-manifest-spec.md`.

## Review-pathway rule trace (#669)

Two closed Draft 2020-12 contracts define the determination-adjacent trace:

- `shared/contracts/human_subjects/review_pathway_trace_request.schema.json`
  binds caller-owned candidate question labels to an exact, complete partition
  of every selected-profile `pathway_trace` requirement; and
- `shared/contracts/human_subjects/review_pathway_rule_trace.schema.json`
  carries matched, unmatched, and unresolved predicate work, profile-local
  alternatives, exact fact occurrences, responsible authority roles, exact
  requirement/anchor pointers, the fixed institutional result, and the #665
  footer.

The standard-library-only builder first replays the exact #666 context,
registry, and resolved artifact. It never invents a candidate name, profile,
predicate, authority anchor, determination, probability, rank, or timeline. All
selected profiles on both axes are accounted for, but candidates and
alternatives stay profile-local. An unknown requirement fact remains unresolved;
a missing profile halts without candidate rows at `JURISDICTION_UNRESOLVED`.

Build, replay, render, and lint only explicitly named artifacts:

```bash
python scripts/build_review_pathway_rule_trace.py build \
  --request pathway-trace-request.json \
  --context context.json \
  --registry shared/human_subjects_authority_registry.json \
  --resolved resolved-authority-context.json \
  --output pathway-rule-trace.json

python scripts/build_review_pathway_rule_trace.py validate \
  --request pathway-trace-request.json \
  --context context.json \
  --registry shared/human_subjects_authority_registry.json \
  --resolved resolved-authority-context.json \
  --trace pathway-rule-trace.json

python scripts/build_review_pathway_rule_trace.py render \
  --request pathway-trace-request.json \
  --context context.json \
  --registry shared/human_subjects_authority_registry.json \
  --resolved resolved-authority-context.json \
  --trace pathway-rule-trace.json \
  --output pathway-rule-trace.md

python scripts/check_review_pathway_output.py \
  --trace-json pathway-rule-trace.json \
  --rendered pathway-rule-trace.md
```

The banned-output lint is surface-scoped to those named generated files and
permits a pathway term only in the exact candidate grammar. Successful replay or
lint never changes a readiness, authorization, acceptance, verdict, checkpoint,
or workflow gate. Protocol:
`shared/references/review_pathway_rule_trace_protocol.md`. Spec:
`docs/design/2026-08-11-669-review-pathway-rule-trace-spec.md`.

## Authority-profile content-coverage advisory (#681)

`shared/contracts/human_subjects/content_coverage_advisory.schema.json` defines
the closed final `content-coverage-advisory/1.0` carrier. It consumes a #667
manifest only after exact replay against the named inventory, packet root,
#666 context, authority registry, and resolved context. It then binds explicit
evaluator judgments to exact `structured_expectations[]` pointers and exact
session-held artifact strings through `evidence-row/1.1` rows. The standard
library finalizer is `scripts/build_content_coverage_advisory.py`.

The output layer is always `LLM-ADVISORY`, and its independent field is
`advisory_coverage_status`. The finalizer copies deterministic packet status,
readiness, caller-supplied authorization, institutional-acceptance boundary,
authority/evidence pointers, and digests without changing them. A structural
gap, external dependency, or waiver/exception boundary cannot be converted into
a semantic missing-element finding. Applicability-false requirements remain
excluded, and every profiled structured expectation is either explicitly
checked or explicitly `not_checked`; missing session content never becomes an
implicit negative result.
An open authority/capability gate with an explicitly unprovided overlay
selection preserves each selected base requirement as
`APPLICABILITY_UNRESOLVED` without inspecting content; a fully closed gate has
no exact requirement to report and is rejected.

The final carrier is deliberately marked `evaluation_status: UNMEASURED`.
UNMEASURED is not a scored measurement row, and this feature makes no accuracy,
coverage-improvement, or efficacy claim. The finalizer and renderer open only
named inputs, perform no directory scan or retrieval, and invoke no model/API;
the draft judgments and positive-row capture timestamps are caller-supplied
advisory observations. Rendering first replays the deterministic manifest and
every source-bound evidence row, so a self-consistent digest alone is
insufficient. The carrier retains all rows, while one render call exposes only
one explicit page of at most 25 evidence rows with deterministic navigation;
there is no render-all mode.

Protocol:
`shared/references/authority_content_coverage_advisory_protocol.md`. Spec:
`docs/design/2026-08-09-681-authority-content-coverage-advisory-spec.md`.

## Tortured-phrase screening contracts (#660)

The #660 family is local, hash-bound, and advisory-only:

- `audit/tortured_phrase_snapshot.schema.json` defines the closed canonical
  `literal` / `all` / `any` / `near` AST and rule-level `exclude_if` grammar;
- `audit/tortured_phrase_snapshot_manifest.schema.json` binds the exact raw
  snapshot bytes, source/version/as-of metadata, preprocessing disclosure,
  zero unsupported rules, and rights; and
- `audit/tortured_phrase_advisory.schema.json` defines the replay-bound
  own-draft `HEURISTIC-ADVISORY` / `UNMEASURED` transcript.

`scripts/tortured_phrase_screening.py` accepts only explicitly named local
snapshot/manifest and input paths. A snapshot is either user supplied or a
repository-authored synthetic fixture. ARS includes no native PPS importer,
fetch option, or redistributed PPS list content, and this path invokes no
model, external API, human/model judge, ambient clock, file time, or network
time. Snapshot SHA-256 covers the exact UTF-8 file bytes; required timestamps
are explicit arguments.

The same runtime can return a new passport copy carrying
`bibliographic-integrity-signal/1.2` rows for each cited title and abstract
surface. A missing abstract is an explicit `not_checked` / `unresolved`
`ABSTRACT_MISSING` row; a present whitespace-only abstract uses
`ABSTRACT_EMPTY`. Consumers remain read-only and the enricher refuses
in-place output. A detected row is only a phrase-list match requiring review;
a zero match is not a clean certificate. No result establishes origin,
paper-mill production, contextual validity, or accuracy, and no result creates
a marker, terminal gate, replacement text, or automatic rewrite. All corpus
rows render in the one canonical `Bibliographic Integrity Advisories` section.

Spec: `docs/design/2026-08-10-660-tortured-phrase-screening-spec.md`.

## Cross-document consistency advisory (#672)

The #672 family is a standalone replay-bound advisory:

- `passport/preregistration_artifact.schema.json` defines the persistent
  `preregistration-artifact/1.0` handoff sidecar;
- `audit/cross_document_source_manifest.schema.json` binds exactly the accepted
  manuscript plus the exact sidecar projection;
- `audit/cross_document_consistency_advisory_draft.schema.json` accepts the
  closed caller-supplied semantic observations;
- `evidence/evidence_row_v1_2.schema.json` binds their exact bilateral or
  trilateral evidence; and
- `audit/cross_document_consistency_advisory.schema.json` defines the canonical
  final `LLM-ADVISORY` / `UNMEASURED` carrier.

Only `scripts/build_cross_document_consistency_advisory.py` may build or update
the preregistration sidecar. The non-shell research architect supplies only the
explicit caller status and companion handle. Academic-paper intake and every
pipeline handoff validate and carry the same sidecar and, when provided, the
same companion bytes unchanged. The repository template is guidance, not
evidence.

Finalization replays the sidecar, exact two-artifact manifest, accepted draft,
optional preregistration companion, and every quote or checked scope before
consuming observations. Methods absence requires an exact named counterpart
scope. An undisclosed preregistration deviation requires a third exact manuscript
disclosure-scope witness. Missing or unavailable inputs cannot become a
no-listed result.

At the one mandatory Stage-5 entry checkpoint, #660 runs first and #672 second
against the same accepted-draft artifact ID/SHA-256. Their carriers and failure
semantics stay separate. #672 failure writes no output and produces only bounded
`ADVISORY_UNAVAILABLE:<CODE>`; neither advisory changes Stage 4.5 or Stage-5
routing. Any manuscript revision stales both and requires both to rerun.

The final carrier has no score, pass/fail, gate, readiness, authorization,
rewrite, ClaimIntent, consent/protocol duplicate, or clean-document meaning.
Protocol: `shared/references/cross_document_consistency_advisory_protocol.md`.
Spec: `docs/design/2026-08-10-672-cross-document-consistency-advisory-spec.md`.

## Audit artifact contracts (v3.6.7 Step 6)

The `audit/` directory carries the three wrapper-emitted artifact schemas that pair
with the passport-side `audit_artifact_entry.schema.json` above. Together they form
the four-schema contract that `scripts/run_codex_audit.sh` (Phase 6.1) writes and the
orchestrator agent reads at every per-agent audit gate.

- `audit/audit_jsonl.schema.json` — Layer 2 evidence: per-row schema for the codex CLI
  0.125+ `--json` event stream (`thread.started` / `turn.started` / `item.completed` /
  `turn.completed` / `error`). One JSONL line per event row.
- `audit/audit_sidecar.schema.json` — Layer 3 evidence: runner / timing / process /
  stream / prompt metadata. Cross-file rules linking sidecar fields to JSONL events,
  on-disk files, and passport entries (B1-B7 in spec §3.7 family B) are enforced by
  `scripts/check_audit_artifact_consistency.py` (Phase 6.3), not by this schema alone.
- `audit/audit_verdict.schema.json` — verdict file shape (PASS / MINOR / MATERIAL /
  AUDIT_FAILED). The artifact orchestrator parses for ship/block decisions; cross-field
  consistency with `finding_counts` and `failure_reason` is lint-enforced per
  spec §3.7 A1 / A2 / A5 / A6.

Spec: `docs/design/2026-04-30-ars-v3.6.7-step-6-orchestrator-hooks-spec.md` §3.

## Review target contracts (#683)

The `review_target/` family keeps target selection author-owned and separates it
from deterministic criterion resolution:

- `review_target_declaration.schema.json` — the closed author-confirmed discipline,
  exact venue/track/contribution-type (or explicit no-venue fallback), overlay,
  selection, precedence, and as-of input;
- `criteria_registry.schema.json` — the versioned four-part authority registry with
  criterion provenance, applicability/exclusions, freshness, and blocking policy;
- `review_target_context.schema.json` — the pointer-only resolved profile, three
  independent outcome dimensions, parallel conflicts, fallback state, and stable
  digests.

`shared/review_criteria_registry.json` intentionally ships only a field-general
baseline. It does not present remembered or synthetic journal rules as official
venue guidance. Exact venue × track × contribution-type behavior is covered by
synthetic fixtures.

Resolve a declaration and optionally emit the Phase 0/1 Target Criteria Brief:

```bash
python scripts/resolve_review_target_context.py \
  --context declaration.json \
  --output review-target-context.json \
  --brief target-criteria-brief.md
```

The resolver is standard-library-only and opens only the named context and registry
inputs. It never reads manuscript content, infers a venue, averages interdisciplinary
criteria, or applies adaptive numeric weights. Spec:
`docs/design/2026-08-08-683-review-target-context-spec.md`.

## Review criteria consumer binding (#684)

The #684 layer binds the #683 context across the three actual consumer classes
without copying criterion prose or inventing a second resolver:

- `review_target/review_criteria_binding_manifest.schema.json` — the closed,
  pointer-only manifest with exact formative, internal-evaluator, and
  five-seat external-panel receipt roles;
- `review_target/constructive_review_findings.schema.json` — the closed
  Critical/Major finding sidecar with exact criterion pointers, typed
  manuscript anchors, separate scholarly/target relevance, honest remedies,
  costs/trade-offs, and author-choice boundaries.

Build, record, render markers, and validate with
`scripts/review_criteria_binding.py`. The tool reads only explicit paths,
hashes artifacts itself, and has no model/API/network/clock/ambient-scan path.
The manifest is workflow-conformance authority only: it never supplies a
severity, verdict, checkpoint, or author triage. Operational protocol:
`shared/references/review_criteria_consumer_protocol.md`. Frozen spec:
`docs/design/2026-08-11-684-review-criteria-consumer-binding-spec.md`.
