# Within-Session Ideation Diversity (#659, v0.4 durable no-call envelope)

This suite freezes a bounded evaluation of two Layer-1 Socratic mechanisms. The
authority is
[`docs/design/2026-08-13-659-within-session-ideation-diversity-design.md`](../../../docs/design/2026-08-13-659-within-session-ideation-diversity-design.md).

## Current status

Phase 1 assets are frozen. Phase 2 now provides a file-only, no-call execution
envelope for an exact 48-cell plan (2 experiments x 6 scenarios x 2 arms x 2
replicates). **No subject, actor, judge, adjudicator, or baseline run exists.**
No breadth-efficacy claim is computable.

## Contents

- `heldout_set.json`: three English/zh-TW scenario pairs with private synthetic
  scholar-role inventories;
- `heldout_set.schema.json`: closed Draft 2020-12 fixture schema;
- `codebook.md`: frozen units, labels, exclusions, metrics, and blinding rules;
- `nonproduction_variant.json`: exact source digest and replacements for the
  exploratory-guardrails ablation;
- `run_plan.schema.json`: exact plan, prompt/order/hash, 48-cell, no-call, stop,
  and later human-labeling requirements;
- `authorization_record.schema.json`: closed exact-run authorization structure
  bound to plan, run, commit, execution, ordered scope, decision, and time;
- `transcript.schema.json`: contract for one externally recorded session,
  canonical external-session receipt, and closed canonical raw-event stream;
- `ingestion_manifest.schema.json`: append-only ingestion and first-stop
  evidence contract;
- `stop_intent.schema.json`: durable write-once quarantine marker that embeds
  blocked raw bytes and the exact stopped-state replay before state replacement;
- `blind_intent.schema.json`: durable deterministic blinding transaction that
  freezes blind ids and every packet/inventory/map hash before staging begins;
- `blind_packet.schema.json`: one isolated arm-blind session packet without
  labels, adjudication, or human evidence;
- `blind_inventory.schema.json`: public inventory of only 48 blind ids and
  packet hashes, without content or assignment fields;
- `blind_manifest.schema.json`: exact finalized packet/map inventory and replay
  binding to the pre-blind ingestion state;
- `private_arm_map.schema.json`: closed private assignment-map structure with
  explicit procedural-only protection semantics;
- `judge_assignment_ledger.schema.json`: closed operator-authored first-round
  assignment ledger (pseudonymous judges + blind ids only, hash-bound to the
  exact bundle);
- `assignment_gate_receipt.schema.json`: write-once pass receipt sealed by the
  assignment-ledger gate, embedding the exact accepted ledger;
- `first_round_delivery_marker.schema.json`: write-once per-assignment delivery
  claim marker (one delivery per verified assignment, exact resume only);
- `scripts/validate_ideation_diversity_assets.py`: offline asset and variant
  validator/materializer;
- `scripts/run_ideation_diversity_no_call.py`: offline-only plan initializer,
  materializer, validator, transcript ingester, and blind-packet preparer;
- `scripts/ideation_diversity_assignment_gate.py`: closed first-round
  assignment-ledger gate (`verify` + `deliver`), kept outside the no-call
  runner.

## Offline validation

```bash
python scripts/validate_ideation_diversity_assets.py validate-assets
python scripts/validate_ideation_diversity_assets.py materialize-variant \
  --output /path/to/new/nonproduction-socratic-mentor.md
```

`materialize-variant` refuses an existing output path. It writes a derived
non-production prompt; it never changes
`deep-research/agents/socratic_mentor_agent.md`.

## Phase-2 no-call workflow

The runner exposes exactly `init-run`, `materialize`, `validate`, `ingest`, and
`prepare-blind-packet`. It has no transport, dispatch, probe, actor, subject,
judge, or adjudicator command. Initialization does not grant consent and every
run plan requires a fresh external authorization before any session occurs.

```bash
PYTHONPATH=scripts python scripts/run_ideation_diversity_no_call.py init-run \
  --run-dir /path/to/new/run --run-id RUN_ID \
  --suite-commit 40_LOWERCASE_HEX_COMMIT --order-seed ORDER_SEED_AT_LEAST_8_CHARS \
  --subject-provider PROVIDER --subject-model MODEL \
  --subject-runtime RUNTIME --subject-runtime-version VERSION \
  --auth-mode AUTH_MODE --reasoning-effort EFFORT \
  --input-token-cap INPUT_CAP --output-token-cap OUTPUT_CAP

PYTHONPATH=scripts python scripts/run_ideation_diversity_no_call.py materialize \
  --run-dir /path/to/new/run --plan-sha256 64_LOWERCASE_HEX_PLAN_SHA

PYTHONPATH=scripts python scripts/run_ideation_diversity_no_call.py validate \
  --run-dir /path/to/new/run --plan-sha256 64_LOWERCASE_HEX_PLAN_SHA
```

`materialize` writes only the two frozen prompt inputs, 48 repository-owned
synthetic actor packets, and 48 non-executable session envelopes. It produces
no actor or subject messages. After separately authorized sessions have been
recorded outside this runner, ingest exactly one external transcript at a time
in the frozen sequence:

```bash
PYTHONPATH=scripts python scripts/run_ideation_diversity_no_call.py ingest \
  --run-dir /path/to/new/run --plan-sha256 64_LOWERCASE_HEX_PLAN_SHA \
  --transcript /path/to/external-transcript.json \
  --authorization-record /path/to/fresh-external-authorization-record

PYTHONPATH=scripts python scripts/run_ideation_diversity_no_call.py prepare-blind-packet \
  --run-dir /path/to/new/run --plan-sha256 64_LOWERCASE_HEX_PLAN_SHA
```

The authorization record must pass its closed schema and bind the exact plan
SHA, run id, operator-declared suite commit, complete execution envelope, ordered 48-cell scope,
decision, and decision time. Its bytes must match the transcript-declared hash.
Each transcript also carries a canonical, hash-bound external-session receipt
with unique receipt/session ids, exact cell/order binding, fresh-context
attestation, and start/completion times. Authorization must precede session
start; start must not follow completion; accepted sessions cannot reuse an
artifact, receipt, or session id or regress behind the preceding cell's
completion time. This proves only structural and byte binding: the runner
cannot authenticate the operator, recorder, or fresh-context attestation and
cannot establish that genuine consent occurred. Those remain procedural
responsibilities; arbitrary or blank records are rejected.

The no-call runner does not inspect Git objects. `suite_commit` is therefore an
operator-declared, unverified provenance string, not proof that the commit
exists; the plan SHA and per-file `asset_bindings` are the verifiable byte
authority. Input/output token caps are likewise operator-declared and
unverified here: this runner has no provider tokenizer, records no observed
usage, and does not enforce or claim that either cap was honored.

Every `raw_event_utf8` value is itself canonical closed JSON. The runner parses
those bytes, derives event kind/turn index from them, rejects unknown fields or
event kinds, classifies tool/network/partial/write-failure events before
consulting outer normalized fields, and requires every transcript turn's text
to equal its raw message-event text byte-for-byte. The stream contains exactly
one first `session_started` and exactly one last `session_completed`; lifecycle
events may not restart or complete midstream. A free-form runtime event cannot
be mislabeled as benign and pass.

The first binding/authorization mismatch, Unicode-normalized semantic arm/pair/
replicate leak, ineligible/partial session,
unplanned tool or network event, evidence-write failure, actor-protocol
deviation, out-of-order ingestion, or contract failure stops permanently. The
runner first advances a materialization-time, per-cell attempt guard from
`ready` to `active`, then publishes a closed write-once `stop-intent.json` (or
its exact-byte fallback slot) that embeds and
hash-binds the raw rejected bytes plus the exact stopped manifest. An input
that cannot be acquired within the 4 MiB bound instead commits a bounded
acquisition-failure record with bounded observed metadata and a 64 KiB prefix hash;
that terminal record is also permanently retry-forbidden. If both marker slots
fail, the already-active immutable guard remains the durable poison state, so
later input cannot retry that cell. NFKC-normalized raw messages require a
letter, number, or symbol, while execution and authorization identity text
requires a letter or number. Spaces, invisible format characters, and isolated
combining marks cannot stand in for provider identity, consent, or subject
output. The runner then
publishes content-addressed raw evidence and atomically replaces state. If that
replacement fails, every command rejects retry and a later load may recover
only the embedded exact stopped state. Validation replays marker, state, and
blocked evidence. A compact canonical digest binds every unexpected file and
directory without embedding unbounded paths in the marker. Registered marker
hardlink aliases and manifest-replacement staging bytes are exact-replayed; a
new, missing, or changed entry fails closed. If a write failure occurs after
authorization/transcript/receipt or staging bytes were created before the
success manifest commits, the surviving bytes remain evidence and are bound by
the receipt or compact inventory rather than deleted.

After all 48 transcripts pass, blinding rejects transcript free text containing
any frozen cell/scenario/pair/experiment/arm/block identifier, explicit mapping
marker, prior-label/adjudication marker, or claimed human-evidence marker. It
first publishes a deterministic write-once `blind-intent.json` that freezes a
one-time private nonce and binds the exact plan and complete ingestion state.
The intent freezes all 48 blind ids and every packet, inventory, private-map,
and manifest hash before writing the in-run `blind-staging/` transaction. The
intent is a `0600` procedural-nondisclosure artifact that must never be delivered
to judges. A partial staging failure may only resume
the same exact transaction; a collision is quarantined, and a second set of
ids or mappings cannot be generated. The staging directory is then atomically
renamed into one bundle with 48 isolated packets, a content-free public
inventory, an exact blind manifest, and a private map. The
complete-byte staging path uses deterministic aliases derived from target refs
and intent-bound hashes under a `0700` root. If alias cleanup fails, the
hardlink remains registered evidence and exact-resumes against the same target
without creating another mapping. The
ingestion state becomes `blind_finalized`; validation reconstructs every packet
from its source transcript and verifies the complete bundle inventory and
hashes. A crash before bundle publication resumes only the bound staging
transaction; a crash after publication but before the state update is
recoverable only by exact replay of that bundle. A first-round judge may
receive a packet only after the closed assignment-ledger gate verifies
that the same judge has not and will not receive another arm or replicate that
shares its scenario/pair/role card. The no-call runner still does not implement
that ledger, and the bundle alone does not prove exposure blindness; the gate
is the separate `scripts/ideation_diversity_assignment_gate.py` (see "First-round
assignment-ledger gate" below). Never deliver the
complete packet directory. These unlabeled packets cannot
stand in for two independent human judges or the separate arm-blind human
adjudicator. Packet flags state only that no structured label, adjudication, or
human-evidence artifact is attached; they do not claim the codebook lacks label
instructions.

Once that gate passes, delivery is exactly one isolated packet per
first-round assignment.

## First-round assignment-ledger gate

`scripts/ideation_diversity_assignment_gate.py` implements the closed gate the
paragraphs above require, deliberately outside the no-call runner so the
runner's own boundary statement stays true. The operator authors a ledger
(`judge_assignment_ledger.schema.json`): binding hashes for the exact run plan,
inventory, blind manifest, and private arm map; a pseudonymous judge roster; an
adjudicator handle (schema-excluded from first-round assignments); and the
first-round assignments themselves as `judge_id`/`blind_session_id` rows only —
the ledger never carries arm, pair, scenario, experiment, or replicate fields.

```bash
PYTHONPATH=scripts python scripts/ideation_diversity_assignment_gate.py verify \
  --run-dir /path/to/run --ledger /path/to/assignment-ledger.json

PYTHONPATH=scripts python scripts/ideation_diversity_assignment_gate.py deliver \
  --run-dir /path/to/run --judge judge-01 \
  --blind-session-id blind-24_LOWERCASE_HEX --dest /path/to/judge-desk
```

`verify` replays the complete finalized bundle, checks the four hash bindings
and private-map permissions, then enforces: every one of the 48 packets carries
at least two distinct first-round judges; the roster equals exactly the set of
assigned judges; and no judge receives two packets whose cells share a
`pair_id` — the pair groups the en/zh-TW variants of one synthetic scholar
context, so blocking at pair level subsumes scenario and role-card sharing,
including the same scenario appearing in both experiments. Only when every
check passes does it seal a write-once pass receipt
(`assignment_gate_receipt.schema.json`) embedding the exact accepted ledger. A
failed check writes nothing, and an exposure failure carries no judge or
blind identifiers — even that pairing exists inside one judge's set is
private-map information once combined with the ledger. Gate
artifacts live in a sibling `<run>-assignment-gate/` directory, never inside
the run directory, so the runner's exact run-inventory validation stays green.

`deliver` consumes only the sealed receipt (never a mutable ledger path), but
treats it as evidence rather than authority: it replays the complete bundle
validation and every semantic gate check — exactly what `verify` runs —
against the embedded ledger, so a hand-fabricated receipt cannot authorize a
delivery that `verify` would refuse, even over a consistently tampered
bundle. It then requires the exact
`judge_id`/`blind_session_id` assignment, verifies the packet's sealed
inventory hash, and publishes exactly one isolated packet into a
destination outside the run and gate directories that the gate itself
creates — `mkdir` is the atomic desk claim, so a new delivery refuses any
pre-existing destination and two racing deliveries cannot both own one
desk. Each assignment is claimed
by a write-once delivery marker (`first_round_delivery_marker.schema.json`)
and closed by a write-once completion marker after publication: an
interrupted identical delivery may exact-resume once, but a completed
assignment is never re-issued, even by an identical command. One residual is
accepted by design: a crash in the instant between packet publication and the
completion marker leaves that one assignment resumable, which can
re-materialize the identical bytes for the same judge — the same assignment,
so no exposure or blinding property is affected. Desk ownership is acquired atomically at creation, and a
post-publication isolation re-scan remains as defense in depth: a desk is
certified only by a successful exit over exactly one packet.

Two known bounded weaknesses are accepted for concurrent operator misuse
(parallel gate commands aimed at one desk, itself a protocol violation), per
the 2026-08-14 review disposition: an assignment that loses the atomic desk
claim keeps its write-once claim marker bound to the lost destination and
needs manual operator recovery before re-delivery, and two concurrent resumes
of the same completed-identical delivery can both report success. Neither
interleaving can expose a judge to a second scholar context, contaminate a
certified desk, or re-issue a completed assignment. The gate
verifies structural exposure
constraints only: it cannot authenticate that two handles are two distinct
people, and judge/adjudicator independence remains a procedural
responsibility, as the ledger's `identity_boundary` block states.

The assignment map is kept under a `0700` directory as a `0600` file and is
declared `procedural_nondisclosure_only`, with `encrypted=false`. These local
permissions reduce accidental disclosure but are not encryption or an
enforced cannot-open seal. Operators must withhold the map until raw labels and
adjudication are sealed.

## Claims and dispatch boundary

The role cards are repository-owned synthetic material. They do not represent
real scholars or measure real creativity. Count, dispersion, and facet
follow-through remain separate; model-originated framings never earn scholar
credit.

The Phase-2 schema freezes and hashes the exact plan under the shared held-out
measurement contract. A decision-relevant run still needs two complete
independent replicates per scenario-arm cell, at least two independent blinded
human judges, and a separate arm-blind human adjudicator. Obtain fresh consent
for the exact subject/actor/judge plan. No earlier model-run consent applies,
and the no-call envelope itself is never consent.

The final report uses `heldout-measurement/1.1` with suite class
`paired_controls`. #659 stays open until the per-mechanism baseline and its raw
evidence are published.
