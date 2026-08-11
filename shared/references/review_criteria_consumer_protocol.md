# Review criteria consumer protocol (#684)

This protocol binds the #683 `ReviewTargetContext` across formative planning,
the academic-paper internal evaluator, and the academic-paper-reviewer external
panel. The binding is workflow conformance only. It never determines severity,
an editorial verdict, a checkpoint state, or author triage.

Normative design:
`docs/design/2026-08-11-684-review-criteria-consumer-binding-spec.md`.
Schemas:
`shared/contracts/review_target/review_criteria_binding_manifest.schema.json`
and
`shared/contracts/review_target/constructive_review_findings.schema.json`.
Tool: `scripts/review_criteria_binding.py`.

## 1. Inputs and authority

The orchestrating layer receives four explicit inputs:

1. the author-confirmed `ReviewTargetDeclaration` already embedded in the
   resolved context;
2. the exact `ReviewTargetContext` JSON;
3. the exact criteria registry named by that context; and
4. a caller-supplied `target_review_id`.

Initialize one manifest before any of the three consumers run:

```bash
python scripts/review_criteria_binding.py init \
  --context phase0/review_target_context.json \
  --context-ref phase0/review_target_context.json \
  --registry shared/review_criteria_registry.json \
  --registry-ref shared/review_criteria_registry.json \
  --target-review-id review-001 \
  --output phase0/review_criteria_binding.json
```

If an active manifest exists, pass it as `--prior-manifest`. A substantive
context change under the same `target_review_id` is a conflict. Starting a new
target review requires a new id and makes the predecessor non-comparable.

The manifest is the exact source of:

- `context_ref` and its raw SHA-256;
- `resolved_digest`;
- ordered `selected_criterion_ids`;
- exact criterion id/version/content-digest pointers;
- unresolved target dimensions; and
- parallel interdisciplinary conflict groups.

Consumers never reconstruct these fields from the Markdown brief and never
copy registry statements into their own instruction files.

## 2. Marker and receipt lifecycle

Before dispatch, render the role-specific marker:

```bash
python scripts/review_criteria_binding.py marker \
  --manifest phase0/review_criteria_binding.json \
  --consumer formative_planning --role FORMATIVE
```

The marker is appended verbatim to the consumer's output. After a successful
consumer call, the output also carries exactly one
`criteria_parallel_conflicts: <canonical compact JSON array>` line rendered
from the manifest. Record only explicitly named artifacts:

```bash
python scripts/review_criteria_binding.py record \
  --manifest phase0/review_criteria_binding.json \
  --consumer formative_planning \
  --artifact FORMATIVE=phase2/paper_outline.md
```

The internal receipt similarly names the paper-blind Phase 6a artifact, not
the later paper-visible decision:

```bash
python scripts/review_criteria_binding.py record \
  --manifest phase0/review_criteria_binding.json \
  --consumer internal_evaluator \
  --artifact INTERNAL=phase6/phase6a_precommitment.md
```

For the external panel, supply all five Phase 1 artifacts in one call:

```bash
python scripts/review_criteria_binding.py record \
  --manifest phase0/review_criteria_binding.json \
  --consumer external_panel \
  --artifact EIC=phase1/eic.md --artifact R1=phase1/methodology.md \
  --artifact R2=phase1/domain.md --artifact R3=phase1/perspective.md \
  --artifact DA=phase1/da.md
```

The recorder checks the complete marker and exact conflict line inside every
artifact, computes raw hashes itself, and appends one receipt atomically. Exact
retry is a no-write. Same-consumer drift is a conflict.

Before a review crosses its handoff boundary, run:

```bash
python scripts/review_criteria_binding.py validate \
  --manifest phase0/review_criteria_binding.json \
  --context phase0/review_target_context.json \
  --registry shared/review_criteria_registry.json \
  --require-complete
```

## 3. Formative planning and writing

Owner: `academic-paper` Phase 2 `structure_architect_agent`.

- Phase 0 resolves the author-confirmed target before Phase 2.
- The Structure Architect receives the pointer-only context and Target Criteria
  Brief. Its outline names relevant criterion ids beside planned sections and
  evidence needs, while keeping scientific validity, venue fit, and submission
  readiness separate.
- `argument_builder_agent` and `draft_writer_agent` consume the same context
  pointer and the Structure Architect's receipt. They do not create a second
  receipt, re-resolve the target, copy criterion prose into their prompts, or
  silently change the author's contribution claim.
- A criterion can motivate a planned check; it never licenses invented evidence,
  results, methods, or a new research question.

The formative output records `FORMATIVE` with the exact marker.

## 4. Internal evaluator

Owner: `academic-paper` Phase 6 `peer_reviewer_agent`.

- Phase 6a receives the sprint/evaluator contract, paper metadata, the
  pointer-only context, and Target Criteria Brief. It remains paper-blind.
- Phase 6a commits the selected criterion ids and keeps each
  `parallel_conflicts[]` group separate. It does not declare applicability.
- The Phase 6a artifact records the `INTERNAL` receipt before any draft is
  visible. Phase 6b receives that unchanged artifact and the draft, assesses
  applicability, repeats the continuity marker, and emits its Critical/Major
  constructive sidecar when applicable.

The internal evaluator may identify a scientific-validity problem independent
of venue fit. It may not turn missing or advisory venue guidance into a blocking
finding.

## 5. External panel, including DA

Owner: the academic-paper-reviewer orchestrating layer.

- Phase 0 uses author-confirmed target metadata. `field_analyst_agent` may
  suggest panel expertise but cannot infer or overwrite venue/track/type.
- Each of `EIC`, `R1`, `R2`, `R3`, and `DA` receives the same context authority
  and brief during the existing paper-content-blind Phase 1 call.
- Each Phase 1 output repeats its role-specific marker and commits the selected
  criterion ids. Conflicting criteria stay parallel.
- Phase 2 receives the unchanged Phase 1 output plus manuscript data. Findings
  cite exact criterion pointers and manuscript evidence/absence anchors.
- `editorial_synthesizer_agent` checks all five marker bindings before
  synthesis. Missing or mismatched bindings abort the criteria-aware run; the
  synthesizer never silently falls back to a self-recalled target.

DA adversarial register does not relax the finding contract. Every DA Critical
or Major item enters the same constructive sidecar and carries the same remedy,
cost, trade-off, author-intent, and no-honest-remedy fields as another seat.

## 6. Constructive finding sidecar

The sidecar covers Critical/Major weaknesses only. Minor and copyedit channels
retain their existing formats. Validate it with:

```bash
python scripts/review_criteria_binding.py validate-findings \
  --manifest phase0/review_criteria_binding.json \
  --context phase0/review_target_context.json \
  --registry shared/review_criteria_registry.json \
  --findings phase2/constructive_review_findings.json
```

Every row separates:

- criterion pointers from manuscript evidence;
- scholarly relevance from confirmed-target relevance;
- the minimum viable remedy from a stronger costlier option;
- effort scope from trade-offs; and
- reviewer advice from author-owned research intent.

If no honest remedy exists, `remedy_status=none`, both option fields are null,
and `no_honest_remedy_reason` explains why. If a stronger option is not
meaningful, it is null and `stronger_option_reason` explains why. An available
option always records `proposed_result_values=false`; new data or intent change
is an author choice, not an assertion that work or results exist.

A stale/unverified or otherwise non-blocking criterion may appear in ordinary
advisory prose, but the validator rejects a Critical/Major sidecar row whose
every criterion pointer has `blocking_eligible=false`.

## 7. Interdisciplinary applicability

Phase 1 commits each selected pointer without manuscript-derived applicability.
After the paper-visible boundary, a consumer may state:

- `applicable`, with a manuscript evidence/absence anchor;
- `not_applicable`, with a manuscript-grounded rationale; or
- `unresolved`, requiring human resolution.

No consumer averages parallel criteria, assigns an adaptive numeric weight, or
selects the criterion whose outcome is easiest to satisfy. Human resolution
belongs in a separate author/reviewer record and starts a new target review if
it changes the selected context.

## 8. Failures and degradation

Binding failures are visible workflow-conformance failures:

- malformed/oversized/symlinked input;
- context or registry hash drift;
- context recomputation mismatch;
- missing/duplicate/wrong-role receipt;
- missing or altered marker;
- selected-pointer mismatch;
- same-id profile change; or
- invalid constructive sidecar.

They stop only the criteria-aware handoff. They do not create an editorial
decision. The user may correct the artifacts, explicitly start a new target
review, or run the pre-#684 field-general workflow with an explicit
`criteria_binding_unavailable` disclosure. That degraded path makes no venue-
alignment claim and is non-comparable to a bound treatment run.

## 9. Measurement boundary

`evals/heldout/review_criteria_constructive_value/measurement_plan.md` owns the
paired behavioral design. CI validates schemas, fixtures, scorer behavior, and
prompt wiring only. It never dispatches a model, judge, or network request.

Until a valid `heldout-measurement/1.1` report is published, describe the
mechanism as implemented but its effect on unsupported-finding rate, severity,
venue alignment, and usefulness as **unmeasured**.
