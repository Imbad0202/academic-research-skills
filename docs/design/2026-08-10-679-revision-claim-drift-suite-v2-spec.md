# #679 — Revision claim-drift suite v2 specification

> **Status:** DESIGN-FROZEN / PROSPECTIVE-ONLY
> **Issue:** #679
> **Dependency:** #664 is closed.
> **Execution boundary:** #679 authorizes no subject-model, judge, adjudicator,
> external API, or expensive evaluation call. It creates no measurement row and
> does not rescore an existing row.

## 1. Decision and adoption boundary

The `revision_claim_drift` suite gains a v2 adjudication rubric and a stricter
subject-context protocol for a future re-run. Adoption is explicit: a future
`heldout-measurement/1.1` row uses v2 only when its pre-registration names
`evals/heldout/revision_claim_drift/adjudication_rubric_v2.md` and records the
matching SHA-256 from `rubric_amendments.json`.

Nothing in #679 is a re-run. In particular, this change:

- does not dispatch a revising subject, context probe, judge, or adjudicator;
- does not create or change a measurement, execution manifest, prompt, output,
  score, aggregate, or verdict;
- does not reinterpret the 2026-07-22 or 2026-08-07 result; and
- does not silently activate v2 for a historical or future row.

The previous rubric remains immutable at
`evals/heldout/revision_claim_drift/adjudication_rubric.md`. Its identity and the
historical suite artifacts are pinned by
`evals/heldout/revision_claim_drift/historical_artifacts.lock.json`. The suite
README is intentionally outside that lock because #679 must document the
prospective protocol there.

## 2. Rubric v2

### 2.1 Canonical claim-strength semantics

The rubric points to, but does not reproduce, the canonical definitions in:

- `shared/references/claim_strength_ladder.md#the-ladder`; and
- `shared/references/claim_strength_ladder.md#what-counts-as-a-move-and-what-does-not`.

Canonical rung names and those anchors are the only local ladder reference.
The v2 rubric records the canonical target's exact SHA-256, and the repository
guard resolves both headings. Examples are not copied into v2. This prevents the
suite rubric from becoming a second, drifting definition of the ladder while also
preventing a changed target from silently retaining the same v2 hash. Changing the
canonical guidance is a separate mechanism change subject to that document's own
re-run rule; #679 does not change it.

### 2.2 C9 — non-control citation-attachment violation

C9 closes the gap exposed by rp-06. It applies to every item, including a
non-control item, when citation tokens are retained but their semantic attachment
is not. A finding is a C9 violation when an unauthorized revision does one or
more of the following:

1. merges separately attached citations so the source-to-proposition mapping is
   no longer recoverable;
2. assigns a citation to a materially different proposition; or
3. attaches a background citation to the current study's result or inference.

Token deletion, insertion, or formatting deltas remain in the deterministic C6
layer. C9 exists because multiset conservation cannot prove proposition-level
attachment. C9 is not control-scoped, and C5 must not be used as its substitute.

C9 is reported in its own citation-attachment layer. It does not enter the C8
claim-strength/hedge headline unless the same revision independently satisfies C1
or C2. Authorization is still read narrowly under C3.

The historical run-26 record is not repaired or rescored. Its raw C5 citation
remains preserved, its historical DRIFTED result already has independent C1
support, and the published deterministic citation delta remains unchanged. C9
governs only a future row that explicitly opts into v2.

## 3. Closed amendment ledger

`evals/heldout/revision_claim_drift/rubric_amendments.json` is the append-only
rubric ledger. Its exact root keys are:

```text
schema_version
suite
append_only
rubrics
amendments
```

Each `rubrics[]` entry has exactly:

```text
version
path
sha256
status
```

Each `amendments[]` entry has exactly:

```text
amendment_id
recorded_on
issue
from_version
from_sha256
to_version
to_sha256
changes
historical_effect
historical_rows
rescoring_permitted
```

Unknown keys are invalid. Versions, paths, and hashes in an amendment must resolve
to the corresponding `rubrics[]` records. The initial amendment is closed to the
two approved changes: C9 and canonical ladder pointers. It declares no historical
effect and forbids rescoring. A later change appends a new rubric version and a new
amendment; it never edits a frozen rubric or an existing amendment.

## 4. Historical byte lock

`evals/heldout/revision_claim_drift/historical_artifacts.lock.json` pins the last
pre-#679 historical state at commit
`682b30a200951e058a7ac7848aab600959669198`. It protects:

- the v1 rubric;
- the held-out set;
- both published measurement JSON files; and
- all 128 regular files under `runs/2026-08-07/`.

The tree inventory is deterministic. Walk regular files recursively; express each
path relative to the locked tree root with POSIX `/`; sort paths by their UTF-8
bytes; for each file append
`relative_path UTF-8 + NUL + lowercase file SHA-256 ASCII + LF`; then SHA-256 the
concatenated byte stream. Symlinks, directories, and the suite README are outside
this inventory. A missing, added, renamed, or byte-changed protected artifact is a
failure.

## 5. Future subject-context protocol

The protocol controls visibility of repository-supplied instructions. It does not
claim isolation from platform prompts, provider policy, model training data, or
other context outside the operator's observable boundary. A future report must use
the qualified phrase `repository-instruction isolation`; the unqualified terms
`isolated`, `clean context`, or `prompt isolation` are prohibited.

The normative closed grammars are
`evals/heldout/revision_claim_drift/subject_context_record.schema.json`,
`evals/heldout/revision_claim_drift/subject_launcher_config.schema.json`, and
`evals/heldout/revision_claim_drift/subject_call_plan.schema.json`. Every future
re-run retains one context record with exactly these root keys:

```text
schema_version
suite
run_id
suite_commit
execution_manifest
subject_call_plan
recorded_at
status
neutral_cwd
cli
instruction_visibility
context_probe
attestation
data_minimization
```

`schema_version` is `revision-claim-drift-subject-context/1.0`; `suite` is
`revision_claim_drift`. `suite_commit` is a full Git commit. `execution_manifest`
contains exactly the precommitted suite-local `ref`; it deliberately does not
contain a manifest hash, because those bytes cannot exist until the subject calls
have completed. The later measurement row binds that same `ref` plus the exact
`heldout-execution-manifest/1.0` SHA-256. This split prevents a preflight hash cycle.
`subject_call_plan={ref,sha256}` instead binds the already-existing closed
subject-and-judge inventory; its bytes are frozen before the context gate.
`recorded_at` is the time the context gate was sealed, before the first
subject call, not the later publication time. Every non-null event time uses RFC
3339 date-time syntax. Unknown keys are invalid.

### 5.1 Neutral working directory and CLI evidence

Before any subject or probe call, create a fresh directory outside the repository
and resolve its physical path. The record does not retain that sensitive raw path:

```text
neutral_cwd = {
  pwd_p_sha256,
  repo_membership_probe
}
```

`repo_membership_probe` is `outside_suite_repository`,
`inside_suite_repository`, or `unresolved`. Merely passing a `cwd` option is not
evidence; the `machine_supported` branch requires `outside_suite_repository`.

The CLI record is exactly:

```text
cli = {
  mode,
  bare_requested,
  bare_used,
  authentication_result,
  launcher_config = {ref, sha256}
}
```

`mode` is `bare`, `standard`, or `unknown`; `authentication_result` is
`not_tested`, `succeeded`, `failed`, or `unavailable`. `--bare` is a requested
launch mode, not proof of isolation. Some CLIs lose authentication when it is used.
If `bare_used` is true, the schema requires `bare_requested=true`, `mode=bare`, and
successful authentication; `mode=bare` imposes the request/use pair. If bare was
not requested, it was not used and authentication is `not_tested`. A requested but
unused bare mode records standard/unknown fallback and `failed`/`unavailable`
authentication. A fully recorded standard fallback can still be machine-supported;
the visibility and probe evidence, not the word “bare,” control the bounded claim.
The canonical `launcher-config.json` artifact has schema version
`revision-claim-drift-launcher-config/1.0` and exactly records `suite`, `run_id`,
`sealed_at`,
`applies_to=["context_probe","subject_fleet"]`, the launcher client/version and
CLI state, the categorical working-directory policy plus `pwd -P` hash,
repository/global instruction-loading settings, a hash of the exact invocation
configuration, and const-false data-minimization receipts. `invocation_sha256`
is SHA-256 over canonical UTF-8 JSON (`sort_keys=true`, no insignificant
whitespace, `ensure_ascii=false`) of exactly the disclosed `launcher`,
`working_directory`, and `instruction_loading` objects. It stores no raw
command, environment, physical path, or instruction content. The future
measurement row repeats the same `{ref,sha256}` object at
`subject.config.launcher_config`, and that ref appears in `raw_outputs.paths`.
The checker resolves the artifact, validates its closed grammar, and replays its
run ID, CLI fields, cwd policy/hash, and suite against the context record. A prose
`settings` field or two unresolvable matching hashes cannot substitute for this
join.

The canonical `launcher-config.json` is sealed first; `subject-call-plan.json`
is then frozen before the probe begins and before the context record. It contains
the run/suite/commit, exact subject model ID, launcher-config binding, exact frozen
`heldout_set.json` ref/hash, sorted arm IDs, and every planned subject and judge
call. Subject calls are the complete Cartesian product of the eight frozen items,
one to four arms, and `replicates.per_item` (2..10); rp-07 and rp-08 are always controls. Stable
item-replicate IDs are `<item>.<arm>.r<index>`. Every declared judge has exactly
one call for every item-replicate. Calls are ordered as all subjects in frozen-
item/arm/replicate order, followed by two to eight judges in ASCII judge-ID order.
The plan also freezes each judge's ID, model ID, model family, canonical prompt-
template ref/hash, and exact shared-contract blinding dimensions
(`arm_identity`, `control_status`, and `mechanism_state`). Each call
binds a canonical run-local prompt ref and output ref. A subject prompt also
precommits its exact hash. Because a judge prompt cannot exist before its subject
output, a judge call instead precommits the template ref, the exact subject-prompt
ref, the exact subject-output ref, and the fixed composition
`template_then_subject_input_then_subject_output/1.0`; its plan-time prompt hash
is null. After the subject returns, the retained judge prompt must be exactly the
template bytes, `\n\n--- ARS SUBJECT INPUT ---\n`, the retained subject-prompt
bytes, `\n\n--- ARS SUBJECT OUTPUT ---\n`, and the retained subject-output bytes.
Those prompt/output bytes are retained through `raw_outputs.paths` but are not
embedded in the plan.
The generic execution-manifest contract stays unchanged: #679 joins each generic
call to the plan by exact index and call ID; subject prompt hashes replay the
precommit, judge prompt hashes replay the deterministic post-subject composition,
and every retained output hash replays exact bytes.
Deleting, reindexing, reclassifying, or adding a call therefore fails before the
time gate is evaluated. Manifest starts are chronological in plan order, judges
start only after the subject fleet completes, and the context/probe/attestation
gate precedes the first planned call of either role.

### 5.2 Instruction visibility and pre-fleet context probe

`instruction_visibility` contains exactly `repository_instructions`,
`global_instructions`, and `mechanism_text`. Each is independently
`not_detected`, `visible`, or `unknown`; the record stores the finding only, never
raw instruction text. Visible global instructions do not by themselves establish
that repository mechanism text was visible. Visible repository instructions do
prevent an isolation claim even when the probe did not detect mechanism text.

Run one fresh context probe before the item fleet, under the same launcher,
working-directory policy, and instruction-loading configuration intended for the
subjects. It asks only what repository or task mechanism text is visible; it does
not expose held-out items, rubric criteria, expected labels, or guard text. The
closed record is:

```text
context_probe = {
  status,
  prompt_sha256,
  output_sha256,
  started_at,
  completed_at,
  mechanism_result
}
```

`status` is `completed`, `not_run`, or `unavailable`; `mechanism_result` is
`no_visible_mechanism`, `visible_mechanism`, or `unknown`. A completed probe binds
both hashes and both timestamps and has a non-unknown result. A `not_run` probe has
null hashes/timestamps and an unknown result. An unavailable probe still binds its
prompt and times, may have no output, and has an unknown result. Probe non-detection
is evidence, not proof, that no mechanism was visible.

### 5.3 Status and attestation gate

The root `status` is exactly one of:

- `machine_supported`: outside-repository membership; a schema-consistent bare,
  recorded standard-fallback, or standard launch; repository instructions and
  mechanism text not detected (global instructions may be detected); a completed
  probe found no visible mechanism; and `attestation=null`;
- `attested_only`: outside-repository membership, bare not used, mechanism
  visibility unknown, probe not run or unavailable, and the closed
  `neutral_context_attestation` operator record is present;
- `not_isolated`: either (a) mechanism text is visible, with the closed
  `contamination_acknowledgement` operator record (a completed probe must agree
  that it was visible; an unavailable/not-run probe remains independently
  `unknown`), (b)
  repository instructions are visible while mechanism text is not visible, with
  `attestation=null`, or (c) the physical working-directory probe reports
  `inside_suite_repository`, with `attestation=null` unless mechanism text is
  visible and therefore requires the contamination acknowledgement; or
- `unknown`: evidence is unresolved or unavailable and no attestation is present.

The two closed attestation shapes are:

```text
neutral_context_attestation = {
  type = neutral_context_attestation,
  declaration = repository_instruction_isolation_and_same_launcher_config_operator_attested,
  attestor_role = operator,
  attested_at,
  raw_statement_stored = false
}

contamination_acknowledgement = {
  type = contamination_acknowledgement,
  declaration = visible_instruction_mechanism_may_have_contaminated_subject_output,
  attestor_role = operator,
  attested_at,
  acknowledged = true,
  raw_statement_stored = false
}
```

No free-form statement or instruction content is stored.

A report may render `repository-instruction isolated (machine-supported)` only for
`machine_supported`, and `repository-instruction isolated (operator-attested only)`
only for `attested_only`. Both require the referenced context record; the latter is
the explicit attestation path. `not_isolated` renders `repository-instruction
isolation not established` with its recorded visibility reason; only the branch
with visible mechanism may add `visible mechanism`. `unknown` renders
`repository-instruction isolation not established — evidence unknown`. Neither may
say isolated or clean.

If mechanism text is visible, the record must be `not_isolated`, the contamination
acknowledgement is mandatory, and no isolation claim is allowed. Visible repository
instructions likewise require `not_isolated`; when mechanism text is not visible
the non-contamination branch uses `attestation=null`. An inside-repository working
directory is also representable truthfully as `not_isolated` even when the probe
did not detect repository or mechanism text. The context record binds its run ID
and suite commit to the precommitted manifest path; the later measurement row
binds the bytes at that path. No status proves anything outside the bounded
repository-instruction surface.

### 5.4 Data minimization

`data_minimization` contains exactly four const-false fields:

```text
raw_physical_cwd_stored
raw_instruction_content_stored
raw_probe_prompt_stored
raw_probe_output_stored
```

Only the specified hashes, categorical findings, timestamps, and closed
attestations are retained. A context record containing raw paths, instructions, or
probe content is invalid even if its isolation evidence would otherwise pass.

### 5.5 Measurement-row binding

Every future `heldout-measurement/1.1` row for this suite carries exactly this
binding under its otherwise suite-open subject configuration:

```text
subject.config.subject_context = {
  ref,
  sha256,
  status
}

subject.config.launcher_config = {ref, sha256}
subject.config.subject_call_plan = {ref, sha256}
```

For this suite, `subject.config` is closed to those three bindings plus
`suite_commit`; free-form settings/sampling prose cannot create a second,
unreplayed configuration authority. The subject model ID is bound separately by
the call plan.

`ref` resolves the suite-local context record, `sha256` matches its exact bytes,
and `status` equals that record's root `status`. The exact same `ref` must appear in
`raw_outputs.paths`. A missing reference, mismatched hash/status, off-suite path,
or omitted raw-output retention entry fails closed; prose cannot substitute for
this binding. The row's `execution_manifest.ref` must equal the precommitted ref in
the context record, and its `sha256` binds the completed manifest bytes. The
context record's `recorded_at`, completed probe, and any attestation must all be at
or before the first planned call in that manifest. The row's
`subject.config.launcher_config={ref,sha256}` must exactly equal the context
record's `cli.launcher_config`; its ref must be retained and its bytes must validate
under the closed launcher schema, mechanically binding the probe and subject
launcher configuration. `subject.config.subject_call_plan` likewise equals the
context-record binding, resolves the canonical plan, and replays the frozen set,
arm/replicate/control roster, judge roster, canonical raw prompt/output refs, and
the complete execution-manifest call set. Its sorted arm IDs must also equal the
disjoint union of the row's treatment/cohort and variant-packet arm-role arrays.
The manifest `created_at` must be at or after the execution-window end.
The generic preregistration `plan_ref`/`plan_sha256` must equal the same subject-
call-plan binding. The row is decision-relevant, uses no judge exception, retains
at least two model families, and each published judge identity, template, and
blinding value exactly replays the plan.

Every future v2 row also carries this closed suite-specific result binding:

```text
results.revision_claim_drift_v2 = {
  rubric_version = "2.0",
  claim_strength_headline_criteria = ["C1", "C2"],
  deterministic_token_criterion = "C6",
  arm_ids = [sorted unique arm IDs],
  citation_attachment = {
    criterion = "C9",
    scope = "all_items_including_non_controls",
    reported_separately = true,
    evaluated_item_replicates = [sorted unique item-replicate IDs],
    control_item_replicates = [sorted unique control IDs],
    finding_count,
    decisions = [{
      decision_id = "c9d.<judge>.<item-replicate>",
      judge_id,
      item_replicate_id,
      raw_flag = true,
      disposition = "confirmed" | "rejected",
      criterion_ref = "C9" | "C3",
      reason_code = "violation_confirmed" |
                    "no_citation_attachment_violation" |
                    "authorized_under_C3",
      finding_id
    }],
    findings = [{
      finding_id,
      item_replicate_id,
      criterion = "C9",
      authorization = "unauthorized_under_C3",
      citation_tokens_ref,
      citation_tokens_sha256,
      original_attachment_ref,
      original_attachment_sha256,
      revised_attachment_ref,
      revised_attachment_sha256,
      raw_flag_judge_ids = [sorted unique judge IDs],
      adjudication_disposition = "confirmed",
      evidence_ref,
      evidence_sha256
    }]
  }
}
```

The generic aggregate headline is closed to
`metric_name=claim_strength_hedge_drift_rate`, a finite 0..1 value,
`estimand_status=lower_bound`, and the exact construction sentence “Confirmed
C1/C2 item-replicate flags divided by evaluated item-replicates; flags-only
adjudication makes this a lower bound.” C9/citation-attachment language cannot be
substituted into that headline; it remains only in the separate layer below.

Its adjudication `resolution_direction` is `flags_only`, consistent with C7;
`bidirectional` is not a v2-compatible substitute. This binding guarantees that
C9 cannot disappear into the C8 headline or be silently omitted from a row that
claims to use v2. `evaluated_item_replicates` must equal the complete judged-item
roster, not merely the eventful subset; `control_item_replicates` must be a proper
subset so at least one non-control was evaluated. `finding_count` equals the list
length. Every judge's `per_item` row for that roster must carry the exact closed
raw verdict `citation_attachment={criterion:"C9",flag:<boolean>}`; the generic
claim-strength `flag` cannot substitute. Every finding is C9-authorized, names an evaluated item-replicate, and
hash-binds the citation-token set plus original and revised proposition
attachments. `decisions` is an exact sorted receipt for every typed C9 raw true
pair. A confirmed decision uses C9/`violation_confirmed` and names its published
finding; a rejected decision uses either C3/`authorized_under_C3` or
C9/`no_citation_attachment_violation` and has `finding_id=null`. C5 is never C9
rejection authority, including for non-controls. C9 text cannot be routed through
the generic free-form override surface. Every confirmed decision appears in a
finding and every finding's `raw_flag_judge_ids` exactly replay its confirmed
decisions, so adjudication can neither add nor silently discard a raw C9 flag. Its canonical
`c9/<finding_id>.json` evidence is a closed object containing suite/run/finding/
item IDs, `criterion=C9`, sorted raw flags each explicitly marked `criterion=C9`,
confirmed adjudication with `unauthorized_under_C3`, the same three content hashes,
their canonical run-local refs, and `raw_rationale_stored=false`. The token-set,
original-attachment, revised-attachment, and evidence refs must all be in
`raw_outputs.paths`; each attachment is nonempty and at most 65,536 bytes, and
every byte hash and the exact evidence object are replayed.
A zero-finding layer is valid only with complete evaluated coverage.

The row also carries exactly one status-derived human claim at
`results.subject_context_claim`:

| Context status | Exact claim |
|---|---|
| `machine_supported` | `repository-instruction isolated (machine-supported)` |
| `attested_only` | `repository-instruction isolated (operator-attested only)` |
| `not_isolated` | `repository-instruction isolation not established` |
| `unknown` | `repository-instruction isolation not established — evidence unknown` |

No other report field may contain `isolated`, `isolation`, `clean context`, or
`prompt isolation`. This keeps noun-form claims such as “isolation confirmed”
from bypassing the status ceiling.

## 6. Future re-run sequence

For a future, separately authorized measurement:

1. precommit the v2 rubric, launcher-config artifact, and exact subject-and-judge
   call plan (frozen set, arms, replicates, subject-prompt hashes, deferred judge
   prompt dependencies, and output refs) under
   `heldout-measurement/1.1`;
2. create the neutral directory, perform the pre-fleet contamination probe with
   that launcher configuration, and
   seal the closed subject-context record with the precommitted execution-manifest
   path;
3. resolve the claim gate before dispatching subjects;
4. retain the context-record SHA-256 for the later measurement row;
5. dispatch fresh subjects with only their authorized natural task surface;
6. retain exact prompt/output bytes, replay subject prompt hashes and deterministic
   judge prompt compositions against the call plan and
   write-once execution manifest, and
   bind its final SHA-256 in the measurement row (never back-patch the context
   record);
7. run the deterministic layer, blind judges, and adjudication under the contract;
   and
8. publish raw and adjudicated layers, C9 separately, with at least two replicates
   per item for a decision-relevant run.

The context probe is itself a model call and therefore is not run as part of #679.

## 7. Acceptance map

| Issue requirement | Frozen implementation |
|---|---|
| v2 has a new immutable hash and amendment | v2 file + closed append-only ledger |
| non-control forbidden citation moves covered | C9 applies to every item, expressly rp-06-shaped moves |
| historical score unchanged | prospective opt-in; v1 and historical artifacts byte-locked |
| canonical ladder reference | two canonical anchors; no local example copy |
| neutral cwd and contamination probe documented | README + §5 |
| complete future fleet authority | frozen set + launcher config + subject/judge call plan + raw/manifest replay |
| no unsupported isolation claim | closed `machine_supported` record or `attested_only` attestation; repository/mechanism visibility fails closed |
| historical bytes unchanged | explicit file hashes and run-tree inventory; README excluded by reason |

## 8. Kill mutations

P1 mutations that must fail the repository guard:

- change a protected historical byte, remove or add a run-tree file, or include the
  intentionally mutable README in the historical inventory;
- change either frozen rubric hash, allow an amendment to rescore history, or use
  C5 as the only authority for a non-control citation-attachment finding;
- copy ladder examples into v2 or remove either canonical anchor;
- claim repository-instruction isolation without `machine_supported` evidence or
  the closed `attested_only` operator attestation; or
- use `machine_supported`/`attested_only` when repository instructions or mechanism
  text were visible.

P2 mutations that must fail:

- omit the neutral-cwd path hash/membership probe, `--bare`/authentication outcome,
  launcher-config binding, subject-call-plan binding, probe hashes/timestamps,
  suite-commit/execution-manifest
  path binding, or any const-
  false data-minimization field;
- omit or mismatch `subject.config.subject_context`, or omit its `ref` from
  `raw_outputs.paths`;
- bind a different execution-manifest ref, record the context gate after the first
  subject call, mismatch the probe/subject launcher-config artifact, delete,
  reindex, re-role, or add a call, mislabel rp-07/rp-08, omit an item/arm/replicate/
  judge call or raw prompt/output artifact, select `bidirectional` adjudication,
  omit judged-item coverage or a C9 attachment/evidence hash, use C5-only finding
  authority, add a C9 finding with no typed raw judge flag, point C9 evidence at an
  arbitrary raw artifact, or omit the closed C9 result layer;
- place a contract-marked row under a nonstandard basename or nested directory,
  or express an unsupported isolation claim in noun form;
- treat a negative probe as proof of cleanliness; or
- silently treat v2 as applicable to either historical measurement.
