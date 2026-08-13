# Claim-standing candidate-ledger protocol

Status: Track A offline substrate implemented; live retrieval and claim-standing measurement remain unimplemented.

This protocol fixes the deterministic boundary between a consent-bound search plan, already-retained adapter-neutral retrieval records, and a candidate ledger. It does not retrieve records, call a model, infer stance, render claim standing, or dispatch a held-out evaluation.

## Contract identities

- `claim-standing-query-plan/1.0`: the frozen checkpoint, tier rule, query/index envelope, caps, and consent receipt.
- `claim-standing-retrieval-input/1.0`: explicit attempts, retained raw hits, caller-supplied relevance assessments bound to exact claim/candidate/prompt bytes, and a whole-input digest.
- `claim-standing-candidate-ledger/1.0`: an auditable terminal state for every attempt and raw hit plus deterministic work-family selection.

All three contracts are closed Draft 2020-12 JSON Schemas. Hashes are lowercase SHA-256 over canonical JSON (UTF-8; sorted keys; compact separators; the digest field omitted from the object being hashed). The consent receipt additionally binds a closed consentable-plan projection containing the probe id, exact claim and eligibility basis, queries and their date/index targets, provider roster, language and document-type allowlists, authorized content classes, caps, and plan creation time. Provider retention is conditional: `known` requires a non-empty reference and `unknown` requires null. Changing any authorization surface invalidates the old receipt.

## Deterministic finalization

The pure builder `scripts/build_claim_standing_candidate_ledger.py` accepts only local JSON files. It validates consent and exact-claim bindings, then applies these operations in order:

1. require exactly one visible initial attempt for every planned query/index pair;
2. mark hits that have neither a title nor a stable identifier;
3. apply date, language, and document-type filters in that order;
4. form work families by normalized DOI, explicit version relation, normalized title/year/first author, then title plus a supplied relation; a no-DOI record cannot transitively bridge distinct DOI components;
5. choose a canonical record by published-over-preprint status, DOI presence, abstract presence, provider rank, then ASCII `(index_id, provider_record_id)`;
6. apply the caller-supplied relevance assessment independently of canonical selection, verifying its canonical exact-claim/candidate/assessor input digest and exact prompt UTF-8 digest, then retaining its outcome, raw output and matching digest, rationale, or explicit failure;
7. select relevant and ambiguous families by deterministic relevance/rank order, up to 40 families, preserve assessment failures as `not_checked`, and mark every remaining eligible family `candidate_cap_exceeded`; a derived work-family id resolves only otherwise exact ordering ties.

The envelope is fixed at three queries, four indexes, 20 retained hits in aggregate per `(query,index)` across attempts, 240 raw hits, and 40 selected work families. Every raw hit receives exactly one terminal state. Attempt failures remain separate ledger rows; the builder never hides or retries them. A pair has one initial attempt; any later attempt must name the failed attempt and a fresh, unique authorization identifier.

Relevance is an explicit retained input, not a model decision made by this builder. Each row binds the exact claim text/digest, candidate title and abstract state/text digest, assessor identity/version contract, and canonical prompt UTF-8 bytes before its output is considered. A successful assessment must retain checked state, raw output, matching SHA-256, and rationale. A failed assessment retains its failure code/detail and any malformed raw output, and finalizes truthfully as `not_checked`; it is never converted into a relevance judgment or omitted.

## Consent, privacy, and failure behavior

Only the exact checkpoint proposition, allowed query/index envelope, filters, retrieval content class, and retained-input hashes authorized by the consent receipt may be processed. Credential fields, API keys, full text, stance/model configuration, and network locations are outside these contracts; the only prompt field is the bounded relevance-only prompt bound to the explicit assessment input. Every planned target pair must have one visible root attempt. A retry requires a closed hash-bound authorization receipt for the exact plan, probe, consent receipt, failed attempt, and query/index pair, accepted after that failure and before the retry starts. Attempt, hit, authorization, assessment, and input timestamps are checked for their required monotonic order. A schema error, stale hash, unauthorized retry, cap violation, missing assessment, or changed exact claim fails closed without output replacement.

Build a new local ledger:

```text
PYTHONPATH=scripts python3 scripts/build_claim_standing_candidate_ledger.py build --query-plan query_plan.json --retrieval-input retrieval_input.json --output candidate_ledger.json
```

Validate an existing ledger by exact deterministic replay:

```text
PYTHONPATH=scripts python3 scripts/build_claim_standing_candidate_ledger.py validate --query-plan query_plan.json --retrieval-input retrieval_input.json --candidate-ledger candidate_ledger.json
```

The current slice deliberately excludes live adapters, pipeline wiring, evidence-row 1.3, presentation/measurement gates, and held-out dispatch. `STANCE CLASSIFICATION UNMEASURED` remains mandatory until a separately authorized later track is implemented and evaluated.
