# #575 scope-closure audit — 2026-08-24

**Audited issue:** #575 — User-confirmed review target and source-backed
field/venue criteria
**Repository state:** `main@7ef93e0cb52b93f9909e163aad912255d4471850`
**Verdict:** **DO NOT CLOSE**

This audit compares #575's current objective and completion rule with the
artifacts shipped by #683/#684 and the retained #684 subject run. It is a
scope/closure check, not a semantic review of any venue criterion and not a
substitute for the preregistered human-expert evaluation.

## Closure findings

| #575 obligation | Repository evidence | Status |
|---|---|---|
| Author-confirmed target is authoritative; no target means an explicit field-general fallback | `docs/design/2026-08-08-683-review-target-context-spec.md`, the three review-target schemas, `scripts/resolve_review_target_context.py`, and focused tests | **Implemented** |
| Criteria are partitioned by authority, provenance/freshness aware, and digest bound | `shared/contracts/review_target/criteria_registry.schema.json` and resolver validation | **Mechanism implemented** |
| The live registry externalizes standards for a declared discipline, exact venue/track/type, and reporting/design overlay | `shared/review_criteria_registry.json` contains four `broad_field_fallback` rows; `official_venue_type`, `field_society_standard`, and `reporting_design_overlay` each contain zero rows | **OPEN — scope gap** |
| Formative planning, internal evaluation, and external review bind to the same resolved pointers/digest | `shared/contracts/review_target/review_criteria_binding_manifest.schema.json`, `scripts/review_criteria_binding.py`, three-consumer integration guards, and #684 tests | **Mechanically implemented/tested** |
| Constructive-review value is measured under the preregistered boundary | Evidence commit `5cc3e93` retains 24/24 subject outputs, receipts, execution manifest, and a 24-output blinded expert packet; it retains no two independent expert label files, blind adjudication, paired record, or `heldout-measurement/1.1` report | **OPEN — human evidence required** |
| Both child tracks are complete and the behavioral result supports only its measured claim | #683 is closed; #684 remains open and correctly describes effect as unmeasured | **OPEN** |

## Material scope mismatch

#575's objective is not merely to prove that a generic registry can resolve
synthetic exact-target fixtures. It says ARS externalizes standards for a
declared discipline, venue, track, and contribution type. The accepted rescope
also called for a bounded, source-backed live proving set. The shipped live
registry deliberately stops at a field-general baseline:

```text
official_venue_type        0
field_society_standard     0
reporting_design_overlay   0
broad_field_fallback       4
```

That boundary is honest and safe—unknown targets resolve as
`declared_target_unresolved` rather than impersonating venue guidance—but it
does not satisfy the epic's current scope. Synthetic `Example Research
Journal` fixtures demonstrate mechanism behavior only; they are not external
venue authority.

## Required decisions before closure

1. **Preferred: preserve the current #575 objective.** Open or adopt a bounded
   source-backed registry follow-up that supplies a human-verified proving set
   with at least one exact official venue × track × contribution-type profile,
   one field/society standard, and one reporting/design overlay. Each row must
   obey the existing provenance, applicability, freshness, conflict, and
   advisory-only rules. The selected set is a proving set, not a coverage
   claim.
2. Complete #684 with at least two independent blinded human experts and the
   separate blind adjudicator, then validate/finalize the retained run and
   publish its `heldout-measurement/1.1` row. Agent/model output cannot stand in
   for these people.
3. Re-run this closure audit against the final registry and measurement report.
   Confirm that #575's completion text and roadmap claim match what actually
   shipped.

The alternative is an explicit maintainer decision to narrow #575 to a
field-general mechanism plus synthetic evaluation and defer all real
source-backed profiles. That would require editing the epic objective,
completion rule, and roadmap; it must not happen implicitly by closing the
issue against the present registry.

## Claim ceiling until closure

ARS may say that the target-context resolver and three-consumer pointer binding
are implemented and deterministically tested. It may not say that live
discipline/venue criteria coverage or constructive-review improvement has been
established. The latter remains unmeasured until the human-expert record and
measurement report exist.
