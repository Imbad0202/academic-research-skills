# Indirect Prompt-Injection Behavior Paired Controls (#675, v0.1)

This held-out suite measures a frozen model's behavior when synthetic retrieved
or pasted content contains an inert embedded instruction. The authority is
[`docs/design/2026-08-13-675-indirect-prompt-injection-behavior-eval-spec.md`](../../../docs/design/2026-08-13-675-indirect-prompt-injection-behavior-eval-spec.md).

## Current status

`seed_version: 0.1.0` — design, fixtures, rubric, validator, diagnostic scorer,
and a Phase-2 no-call execution/ingestion/blinding envelope. **No subject
baseline exists.** No safety, robustness, or ARS-guidance efficacy claim is
computable from these assets.

The suite is behavioral. It does not enforce an instruction/data boundary.
Structural isolation remains #676.

## Contents

- `heldout_set.json`: eight synthetic scenarios in a closed 2 x 2 design;
- `heldout_set.schema.json`: strict fixture schema;
- `prompt_ars_guided.txt`: production-guidance condition;
- `prompt_platform_only.txt`: non-production platform-only control;
- `adjudication_rubric.md`: pre-dispatch semantic label and blinding rules;
- `scripts/run_indirect_prompt_injection_probe.py`: strict validator,
  one-replicate materializer, and mechanical response scorer;
- `run_plan.schema.json`, `authorization_record.schema.json`,
  `transcript.schema.json`, `ingestion_manifest.schema.json`, and
  `stop_intent.schema.json`: closed
  Draft 2020-12 contracts for an exact 64-cell externally executed run;
- `journal_token.schema.json`: closed contract for materialization-time
  pre-armed ingestion, pre-load-terminal, and blind-bundle transaction tokens;
- `blind_session_packet.schema.json`, `blind_inventory.schema.json`,
  `blind_private_map.schema.json`, and `blind_manifest.schema.json`: isolated
  judge-packet, public inventory, private unblinding, and atomic final-bundle
  contracts;
- `judge_assignment_ledger.schema.json`: frozen future pre-delivery ledger
  shape; this no-call runner does not create or validate a real ledger;
- `scripts/run_indirect_prompt_injection_no_call.py`: offline-only
  `init-run`, `materialize`, `validate`, `ingest`, and
  `prepare-blind-packet` commands. It contains no detect, dispatch, probe,
  model, provider, network, or subprocess path.

The eight scenarios cover web/source verification, PDF or manuscript ingestion,
bibliography intake, and pasted reviewer/committee comments in English and
zh-TW. Each scenario materializes four cells, so one replicate has 32 calls.

## Validate and materialize without a model call

```bash
python scripts/run_indirect_prompt_injection_probe.py validate-assets
python scripts/run_indirect_prompt_injection_probe.py materialize \
  --output-dir /path/to/new/neutral-run-directory
```

`materialize` refuses a non-empty output directory. It writes neutral prompt
filenames and a hash manifest. It does not dispatch a model, enable tools, or
contact a provider.

To exercise the mechanical parser on one retained response:

```bash
python scripts/run_indirect_prompt_injection_probe.py score-output \
  --scenario-id ipi-web-en \
  --condition injected \
  --response /path/to/raw-response.json
```

Mechanical output is diagnostic only. The final four outcomes require the
frozen blinded rubric and the held-out measurement contract.

## Freeze a Phase-2 envelope without making a call

`init-run` expands the exact `8 scenarios x 2 content conditions x 2 guidance
conditions x 2 replicates = 64 cells`. Its SHA-256 order is deterministic from
the supplied seed; replicate 2 reverses each scenario's four-factor order.
All provider/model/runtime values are declarations to bind future external
evidence, not capabilities of this runner.

```bash
python scripts/run_indirect_prompt_injection_no_call.py init-run \
  --run-dir /path/to/new-run \
  --run-id RUN_ID \
  --suite-commit 40_LOWERCASE_HEX \
  --order-seed PRECOMMITTED_SEED \
  --subject-provider PROVIDER \
  --subject-model MODEL \
  --subject-runtime RUNTIME \
  --subject-runtime-version VERSION \
  --auth-mode AUTH_MODE \
  --reasoning-effort EFFORT \
  --input-token-cap INPUT_CAP \
  --output-token-cap OUTPUT_CAP

python scripts/run_indirect_prompt_injection_no_call.py materialize \
  --run-dir /path/to/new-run --plan-sha256 EXACT_PLAN_SHA256
python scripts/run_indirect_prompt_injection_no_call.py validate \
  --run-dir /path/to/new-run --plan-sha256 EXACT_PLAN_SHA256
```

Materialization writes 64 neutral prompt files and 64 non-dispatch call
envelopes using exclusive creation. It also pre-arms one immutable journal
token for each ingestion, one pre-load-terminal token, and one for blind-bundle
construction. Claiming a token creates a second hard link to the same validated
inode before any external transcript bytes are acquired or any blind ids are
generated. A successful cell moves its claimed name to a same-inode completed
name only after the ingestion manifest replacement and directory fsync succeed.
Every
envelope fixes `tools=[]`,
`web_enabled=false`, `runner_transport=none`, `dispatch_available=false`, USD 0
API spend, no fallback, and a fresh-external-authorization requirement.

`ingest` accepts exactly the next externally recorded transcript plus an
external authorization record bound to the exact plan bytes. The runner proves
schema, byte, hash, scope, and time ordering only. It explicitly does not verify
operator identity or turn a record into consent. Raw response and event bytes
are bounded and hashed. The runner's pinned canonical-event decoder derives the
action class from a closed native event type; every raw event also binds the
exact external session, cell, sequence, event index, and event id. An outer
class cannot hide a native tool or network event. A closed, hash-bound
external-session receipt must use a unique receipt id and fresh-context session
id, and session times must remain monotonic across all 64 cells. Observed input
and output token usage is mandatory and capped; a conservative response-byte
cap also ensures that every accepted transcript can fit a final packet.

The first blocked, partial, drifted, semantic mapping/prior-label leak,
forbidden-action, or evidence-write failure stops the whole run and permanently
forbids retry. The pre-armed journal claim is the first irreversible boundary,
including when transcript acquisition fails or the primary stop-intent write
itself cannot complete. Available raw bytes are preserved content-addressably;
a closed write-once stop intent containing exact base64 replay bytes is then
committed before stopped-state replacement. Surviving authorization,
transcript, and receipt artifacts are registered individually, while one
compact canonical tree digest binds every otherwise-unregistered file and
directory, including empty directories and replacement staging. A failed
manifest replacement is replayed from the intent, never retried as a call.
If replacement publishes the advanced manifest but its durability step reports
failure, the cell remains claimed rather than completed; validation and the next
ingest both reject that ambiguous state before reading another transcript.
Plan/manifest failures found before a normal load claim the pre-load-terminal
token before transcript acquisition and then create a write-once pre-load quarantine,
so restoring old bytes or losing the quarantine write cannot make ingestion
retryable.

After all 64 complete records are ingested, `prepare-blind-packet` creates 64
runner-write-once isolated packets. A finalized blind manifest binds the exact
source ingestion state, every packet, the public inventory, and the private
map; validation semantically rebuilds the full bundle and rejects extra or
missing paths. Blind construction has one pre-armed irreversible transaction
and one deterministic sibling staging path. A complete staged bundle is
validated and atomically resumed without minting new blind ids; an incomplete,
invalid, or legacy staging residue permanently quarantines regeneration. A
complete bundle can also be replayed and finalized after a crash between the
rename and the state update.

The public inventory contains only opaque ids, paths, byte counts, and hashes.
Formal scenario/condition/replicate mappings stay in the separate private map,
but each packet necessarily shows exact external content: it does **not** claim
that injected content or its canary is perceptually blind. The map is unencrypted:
local `0700` directory and `0600` file modes plus procedural
nondisclosure are defense in depth, not proof of reviewer identity or access
control. Packets contain no label, adjudication, or human-evidence claim and
reject source-codepoint-atomic NFKD/combining-mark/format/punctuation/symbol/
separator-obfuscated assignment or prior-label markers at each ingest and
again during preparation. Compatibility letters and numbers remain atomic, so
their decomposed punctuation cannot manufacture a false identifier boundary. A runtime
visible-semantic gate also rejects surrogate-bearing, blank, format-only, and
combining-mark-only subject output before it can count as complete. Delivery
remains gated on a future
closed assignment ledger; this bundle alone does not prove arm blindness or
prevent the same judge from seeing cross-condition equivalents.

## Dispatch boundary

Before any run, freeze an exact suite commit, materialized manifest SHA, call
order, provider/auth/model/runtime, settings, caps, two-or-more replicates,
judge plan, stopping rules, and API/spend boundary. Obtain fresh consent for
that exact plan. No previous evaluation consent carries over.

All v0.1 calls use fresh sessions with `tools=[]` and `web=false`. A blocked or
partial call stops the run, is retained, and is not retried. Raw prompts,
responses, event streams, tool events, parse results, judge outputs, and
adjudication records remain available for audit.

This repository envelope cannot dispatch those calls. Exact-plan fresh consent
must be obtained and recorded outside it. Later judging still requires at least
two independent arm-blind human judges and a separate arm-blind human
adjudicator, plus the future closed assignment ledger needed to substantiate
that exposure claim. The runner never creates subject, judge, adjudicator,
label, or human evidence. `suite_commit` must match local HEAD at freeze while
asset bindings hash live bytes; the runner does not claim a clean worktree or
replay every asset from the Git object.

## Claims boundary

Allowed reporting is limited to this fixed model/prompt/platform/tool/fixture
configuration. A clean run does not prove safety; a failure does not establish a
universal exploit. The `platform_only` condition retains provider safeguards and
is not a no-safeguards control or a supported ARS operating mode.

The final report uses `heldout-measurement/1.1`, suite class
`paired_controls`. Do not publish a measurement row until its complete raw
evidence and required judging/adjudication records exist.
