# Frozen measurement plan — review_criteria_constructive_value/1.0

Status: PRE-REGISTERED / NOT RUN. Issue: #684. Contract:
`heldout-measurement/1.1`; suite class: `paired_controls`.

## Freeze and subject

Before any subject call, pin one clean main-history commit containing this plan,
the #683 resolver/registry, the #684 schemas/runtime/prompts, the scenario set,
and scorer. The same 40-hex commit is used for both arms and for
`subject.config.suite_commit` and `preregistration.frozen_commit` in the report.
No post-outcome prompt, rubric, scenario, or threshold edit is pooled into that
run.

## Scenarios and labels

The frozen run uses every item in `heldout_set.json`. Materials are synthetic;
real manuscripts require separate explicit authorization. Exact target
declarations are resolved from the pinned registry before dispatch and the raw
context bytes are sealed into the execution manifest.

At least two independent experts with relevant venue/domain or methodology
competence label every blinded replicate. They do not see arm identity,
mechanism state, other judges, raw aggregates, or expected treatment direction.
They label profile resolution, each declared criterion's applicability,
finding support, Critical/Major severity, confirmed-target alignment, and remedy
usefulness. Disagreement is adjudicated by a disclosed expert who also remains
blind to arm identity. The final closed record conforms to
`paired_adjudication.schema.json`; pre-adjudication judge records and reasoning
are retained separately. The closed record also binds every raw label row to
every declared `expert_id`; unanimous raw labels cannot be overwritten by the
adjudicated value.

## Paired execution

For every item, run baseline and treatment with:

- identical target context bytes and resolved digest;
- identical manuscript/outline material and role;
- identical model id/family, tools, sampling configuration, input token cap,
  output token cap, and system-level safety settings;
- at least two fresh isolated replicates per arm; and
- a balanced, predeclared arm order.

Baseline is the pinned pre-#684 consumer prompt. Treatment differs only by the
#684 binding marker, Target Criteria Brief, parallel-conflict discipline, and
constructive-finding contract. Phase 1 receives no manuscript, abstract,
finding, score, or other reviewer output in either arm. No retry may depend on
the observed outcome; blocked/partial calls are retained and reported.

## Metrics

The deterministic scorer reports per arm and treatment-minus-baseline deltas:

- `profile_resolution_rate`: exact target digest and selected-id match;
- `applicability_accuracy`: exact match over expert-labelled criterion rows;
- `unsupported_finding_rate`: unsupported findings / all support-labelled
  findings, with unresolved rows excluded and counted separately;
- `severity_agreement_rate`: exact Critical/Major match on supported findings;
- `venue_alignment_accuracy`: exact aligned/not-aligned match where experts
  resolved venue relevance; and
- `mean_usefulness`: mean 1–5 expert usefulness rating, with distribution
  counts also published.

No composite score, outcome-dependent exclusion, adaptive weighting, or silent
threshold exists. The report includes numerator/denominator for every rate and
the replicate-level rows needed to reproduce them. Raw expert unanimity is
reported separately for applicability, support, severity, venue alignment,
and usefulness; it is a diagnostic, not a performance metric. Profile resolution and
applicability are correctness metrics; unsupported findings are a harm metric;
severity, alignment, and usefulness remain distinct diagnostics.

## Evidence and reporting

Use `heldout-measurement/1.1`, `decision_relevant: true`, at least two subject
replicates per item, and at least two judge model families when model judges are
also used. Human expert labels remain required regardless of model judges.
Retain raw subject and judge outputs, exact prompts/hashes, execution manifest,
environment, blocked attempts, adjudication direction, and agreement. CI may
validate these artifacts and the scorer but never dispatch subjects or judges.

The claim ceiling before a valid report is: “the #684 consumer-binding
mechanism is implemented; its effect on unsupported-finding rate, severity,
venue alignment, and usefulness is unmeasured.” A future report may state only
the separate observed metrics for its pinned synthetic suite and model; it may
not claim general reviewer superiority or real-world venue acceptance.

## Amendments

The amendment ledger starts empty and is append-only. Any change to prompts,
items, labels, budgets, metric definitions, judge plan, or claim ceiling after
freeze creates a new plan version and new run; results are not pooled.
