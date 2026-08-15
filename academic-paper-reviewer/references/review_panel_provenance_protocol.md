# Typed Review Panel Provenance Protocol

This protocol records what is known about how a review panel was executed. It
does not turn reviewer names, roles, or personas into a binary independence
claim.

## Canonical artifacts

- Input: `shared/contracts/reviewer/review_panel_provenance_input.schema.json`
- Output: `shared/contracts/reviewer/review_panel_provenance.schema.json`
- Schema 6 carrier: `shared/contracts/reviewer/review_panel_provenance_carrier.schema.json`
- Builder and replay validator: `scripts/review_panel_provenance.py`

This artifact family is closed to `reviewer_full`. Every input binds
`mode: reviewer_full`, `contract_id: reviewer/reviewer_full/v2`, and the pinned
SHA-256 of the exact raw bytes of `shared/contracts/reviewer/full.json`. Its
seat roster is ordered exactly `EIC`, `R1`, `R2`, `R3`, `DA`; a missing,
additional, renamed, duplicated, or reordered seat is invalid. Other modes do
not borrow this family and must omit the Schema 6 carrier.

The dispatching layer records one input seat per actual review execution. The
fixed `seat_id` identifies the contract seat, but `role_id` is still an actual
execution observation: an unrecorded role or other observation may be omitted,
and the builder normalizes it to `null` or `unknown`. Producers MUST NOT fill an
absent fact by inference from the fixed seat label, persona, role prompt,
configured model, or intended routing plan.

```json
{
  "schema_version": "review-panel-provenance-input/1.0",
  "panel_id": "review-round-1",
  "mode": "reviewer_full",
  "contract_id": "reviewer/reviewer_full/v2",
  "contract_sha256": "e9712090d2469fea15a37b8e22d4e137afbcb2bf38d5789939c5df56738ef7af",
  "seats": [
    {
      "seat_id": "EIC",
      "role_id": "eic",
      "context_id": "invocation-eic",
      "peer_outputs_visible": false,
      "actor_type": "model",
      "model_family": "family-a",
      "provider": "provider-a",
      "human_reviewer_id": null
    },
    {
      "seat_id": "R1",
      "role_id": "methodology",
      "context_id": "invocation-r1",
      "peer_outputs_visible": false,
      "actor_type": "model",
      "model_family": "family-a",
      "provider": "provider-a",
      "human_reviewer_id": null
    },
    {
      "seat_id": "R2",
      "role_id": "domain",
      "context_id": "invocation-r2",
      "peer_outputs_visible": false,
      "actor_type": "model",
      "model_family": "family-b",
      "provider": "provider-b",
      "human_reviewer_id": null
    },
    {
      "seat_id": "R3",
      "role_id": "perspective",
      "context_id": "invocation-r3",
      "peer_outputs_visible": false,
      "actor_type": "model",
      "model_family": "family-a",
      "provider": "provider-a",
      "human_reviewer_id": null
    },
    {
      "seat_id": "DA",
      "role_id": "da",
      "context_id": "invocation-da",
      "peer_outputs_visible": false,
      "actor_type": "model",
      "model_family": "family-a",
      "provider": "provider-a",
      "human_reviewer_id": null
    }
  ]
}
```

`context_id` identifies the actual isolated invocation context, not a topic,
prompt template, or persona. `peer_outputs_visible` records whether that seat
could see another seat's output before committing its own review. A seat that
combines accountable human judgment and model execution uses `actor_type:
"hybrid"`; the builder rejects contradictory `human` and `model` identity
claims rather than guessing.

`model_family` and `provider` use the dispatcher's canonical lower-case IDs,
not display names. The schema rejects case and whitespace variants so trivial
label drift cannot manufacture diversity. Alias/version taxonomy beyond those
canonical IDs remains the dispatcher's responsibility.

## Closed axes

Each output axis is exactly `true`, `false`, or `"unknown"`:

| Axis | `true` means | `false` means | `unknown` means |
|---|---|---|---|
| `role_separated` | Every seat has a recorded, unique role ID | A recorded role ID is reused | At least one role ID is unrecorded and no reuse is proven |
| `fresh_context` | Within this one panel attempt, every seat has a recorded, unique invocation-context ID | Within this attempt, a recorded context ID is reused | At least one context ID is unrecorded and no within-attempt reuse is proven |
| `blind_to_peer_outputs` | Every seat records that peer outputs were not visible | At least one seat records that peer outputs were visible | No visibility is proven, but at least one observation is unrecorded |
| `model_family_distinct` | At least two model families are proven present | Model participation is proven, all relevant family observations are complete, and only one family is present | Family evidence is incomplete or model-family applicability cannot be established |
| `provider_distinct` | At least two model providers are proven present | Model participation is proven, all relevant provider observations are complete, and only one provider is present | Provider evidence is incomplete or provider applicability cannot be established |
| `human_distinct` | At least two accountable human reviewer IDs are proven present | Complete actor evidence proves fewer than two human reviewer IDs | Actor or human-identity evidence could conceal a second human reviewer |

Two known model families or providers are sufficient to establish the
corresponding diversity axis even if another seat is unknown. A `false` value
requires complete evidence capable of ruling diversity out.

Every artifact and carrier fixes
`fresh_context_scope: within_panel_attempt_only`. The builder receives no
prior-attempt history. Therefore `fresh_context: true` does **not** establish
that any context ID is new relative to retries, earlier rounds, or another
artifact; two attempts can each truthfully report within-panel separation while
reusing the same identifiers across attempts. A future history-aware contract
would require an explicit closed attempt ledger and is not simulated here.

## No binary independence reduction

The output carries the fixed value:

```json
"independence_claim": "not_computed_from_personas"
```

The schemas are closed and reject an `independent` property at the panel or
seat level. Consumers MUST display the six axes individually and MUST NOT
collapse them to a binary or numeric independence score. In particular,
`role_separated: true` proves role separation only.

## Correlated-error disclosure

The builder derives the disclosure from `model_family_distinct`:

- `false`: disclosure is required with reason `same_model_family`.
- `"unknown"`: disclosure is required with reason `model_family_unknown`;
  correlated-error risk cannot be ruled out.
- `true`: the family-status disclosure is not required. This does not establish
  independence on any other axis.

Same-family text is fixed by the schema and cannot be suppressed or replaced
by a generic persona-diversity statement.

## Build and replay validation

```bash
python scripts/review_panel_provenance.py build panel-input.json --output panel-provenance.json
python scripts/review_panel_provenance.py validate panel-provenance.json
python scripts/review_panel_provenance.py build-carrier panel-provenance.json --artifact-ref artifacts/panel-provenance.json --output panel-carrier.json
python scripts/review_panel_provenance.py validate-carrier panel-carrier.json --artifact-root .
python scripts/review_panel_provenance.py validate-schema6 review-report.json --mode reviewer_full --artifact-root .
```

Validation checks the closed schema, duplicate seat IDs, actor/identity
coherence, exact mode/contract/roster binding, the canonical
normalized-manifest digest, every derived axis, the fixed scope and
non-independence claim, and the correlated-error disclosure. A manually edited
derived field fails deterministic replay.

The output also carries `execution_topology_sha256`, a deterministic hash over
the exact mode/contract binding, ordered seat id/observed role, actor type,
actual model family/provider, accountable human identity, peer-output
visibility, all six derived axes, and the fixed freshness scope. Per-run
`context_id` values are excluded so the same configuration can match across
attempts; the within-panel `fresh_context` axis remains included. This digest
is an exact configuration-match key for bounded calibration profiles, not a
score, a history check, or an independence claim.

## Schema 6 carrier

Current `reviewer_full` output must carry exactly one object validated by
`review_panel_provenance_carrier.schema.json`. Its `valid` branch contains the
relative artifact path, SHA-256 of the artifact's **exact raw bytes**, the
artifact's normalized-manifest and execution-topology digests, the fixed
fresh-context scope, and all six axes. Runtime validation resolves the path
under an explicit artifact root, rejects path escape, hashes the raw bytes,
schema-validates and deterministically replays the artifact, and compares every
carried value. Letter prose is never a substitute.

The `invalid` branch records one reason — `absent`, `unreachable`,
`digest_mismatch`, `schema_invalid`, or `replay_invalid` — and fixes all six
axes to `unknown`. It cannot retain a path or digest that could look verified.
An invalid branch is a structurally valid, fail-visible execution state; the
CLI reports it with a non-zero status. `reviewer_full` cannot silently omit the
field. `reviewer_methodology_focus`, `reviewer_re_review`, `reviewer_quick`,
`reviewer_guided`, and `reviewer_calibration` must omit it because no equivalent
typed artifact contract is shipped for those modes; unknown mode labels are
rejected rather than treated as another omission case.
