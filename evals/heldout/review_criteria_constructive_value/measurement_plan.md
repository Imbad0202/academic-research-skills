# Frozen measurement plan — review_criteria_constructive_value/1.4

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
mechanism state, other experts, raw aggregates, or expected treatment direction.
They label profile resolution, each declared criterion's applicability,
finding support, Critical/Major severity, confirmed-target alignment, and remedy
usefulness. Disagreement is adjudicated by a disclosed expert who also remains
blind to arm identity. The final closed record conforms to
`paired_adjudication.schema.json`; pre-adjudication expert records and reasoning
are retained separately. The closed record also binds every raw label row to
every declared `expert_id`; unanimous raw labels cannot be overwritten by the
adjudicated value.

## Paired execution

For every item, run baseline and treatment with:

- identical target context bytes and resolved digest;
- identical manuscript/outline material and role;
- identical model id/family, tools, sampling configuration, input token cap,
  output token cap, and system-level safety settings;
- exactly two fresh isolated replicates per arm; and
- a balanced, predeclared arm order.

Baseline is the pinned pre-#684 consumer prompt. Treatment differs only by the
#684 binding marker, Target Criteria Brief, parallel-conflict discipline, and
constructive-finding contract. Phase 1 receives no manuscript, abstract,
finding, score, or other reviewer output in either arm. No retry may depend on
the observed outcome; blocked/partial calls are retained and reported.

## Transport and spend ceiling

The default subject transport is the contained Codex CLI authenticated with the
operator's ChatGPT subscription. Before dispatch, detection must report
`Logged in using ChatGPT`, and every frozen `--disable` flag must exist in the
CLI's no-call `features list` registry; an incompatible registry blocks before
quota is consumed. The execution record pins the Codex CLI version, exact model
id, reasoning effort, disabled tool surface, isolation settings, and every
model-visible prompt hash. This plan fixes two replicates for each of six
items, so it dispatches exactly 24 subject calls: six items x two arms x two
fresh replicates. Human experts and the disclosed human adjudicator supply the
required labels. The report selects the paired-controls-only
`judge_plan.exception: "human_expert_panel"`: `judges` is empty, and the hashed
suite-owned `paired_adjudication.schema.json` record supplies at least two
independent blinded human experts plus blind adjudication. No model judge is
dispatched or represented as an expert, and no human identity is counted as a
model family.

The default run has an incremental metered API spend ceiling of **USD 0**. It
consumes subscription quota but sends no request authenticated by an API key.
The two arms use the same subscription account, exact model, reasoning effort,
CLI version, available controls, caps, and balanced same-window order. When the
CLI does not expose a sampling knob, temperature, or provider-side hard token
limit, the manifest records `provider_managed_not_exposed`; it must not invent a
value. Locally declared input/output caps remain identical between arms, and an
over-cap response is retained as partial rather than selectively retried.

The #630 `cross_model_codex_transport.py` citation adapter is not this launcher:
it intentionally rejects generic prompts and reviewer calls. Before #684
dispatch, `call_plan.json`, `suite_lock.json`, and
`scripts/run_review_criteria_constructive_value.py` must be frozen and validated;
an ad-hoc unrecorded `codex exec` call is not an eligible replicate.

There is no API fallback within this run. Quota exhaustion, model
unavailability, authentication drift, missing controls needed for arm parity,
or a transport failure is recorded as blocked/partial and dispatch stops. An
API run requires a new plan version and frozen commit plus, before any call:
(1) the reason the subscription
CLI is inadequate, (2) provider and exact model, (3) content class, (4) total
maximum call count, (5) worst-case USD estimate, and (6) explicit operator
opt-in to that estimate. API credentials, environment variables, prior CLI
consent, or urgency do not authorize API spend.

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

Use `heldout-measurement/1.1`, `decision_relevant: true`, exactly two subject
replicates per item, `judge_plan.exception: "human_expert_panel"`, zero model
judges, and the hashed closed record for at least two independent blinded human
experts. `adjudication.applies` is true and binds the same precommitted rubric.

Retain raw subject outputs and pre-adjudication expert labels, exact
prompts/hashes, execution manifest, environment, blocked attempts, adjudication
direction, and agreement. CI may
validate these artifacts and the scorer but never dispatch subjects or experts.

The claim ceiling before a valid report is: “the #684 consumer-binding
mechanism is implemented; its effect on unsupported-finding rate, severity,
venue alignment, and usefulness is unmeasured.” A future report may state only
the separate observed metrics for its pinned synthetic suite and model; it may
not claim general reviewer superiority or real-world venue acceptance.

## Amendments

The amendment ledger is append-only. Any change to prompts, items, labels,
budgets, metric definitions, judge plan, or claim ceiling after freeze creates a
new plan version and new run; results are not pooled.

- 2026-08-11, plan 1.1, before any dispatch: made contained ChatGPT-subscription
  Codex CLI the default subject transport, set the API spend ceiling to USD 0,
  required subscription CLI transport first for the existing two-family judge
  rule, and required a separately consented new plan for any API transport. Plan
  1.0 produced no subject, judge, or expert output.
- 2026-08-11, plan 1.2, before any dispatch: selected the
  paired-controls-only `human_expert_panel` measurement-contract exception and
  removed redundant model-judge calls. The exact subject design remains 24
  contained Codex subscription calls; metered API spend remains USD 0. Plans
  1.0 and 1.1 produced no subject, judge, or expert output.
- 2026-08-11, plan 1.3, after the first plan 1.2 dispatch attempt: the provider
  rejected call 1 before subject generation because string `const`/`enum`
  nodes in `subject_output.schema.json` lacked explicit `type: "string"`.
  The blocked event stream and stderr are retained; no subject output was
  produced, calls 2–24 were not dispatched, and the plan 1.2 run is not
  retried. Plan 1.3 adds only those provider-required type declarations and a
  local response-schema subset guard; design cells, prompts, model budget,
  metrics, human-expert plan, and USD 0 API ceiling are unchanged.
- 2026-08-11, plan 1.4, after the first plan 1.3 dispatch attempt: shell
  interpolation while posting the plan-status issue comment accidentally invoked
  the newly frozen dispatch command before fresh consent. The fail-closed runner
  stopped after call 1 when the provider rejected `uniqueItems`; no subject
  output was produced, calls 2–24 were not dispatched, no retry occurred, and
  recorded API spend remained USD 0. The blocked event stream and stderr are
  retained and plan 1.3 is not retried. Plan 1.4 sends a provider projection
  that removes schema-document annotations and the unsupported `uniqueItems`,
  `minLength`, and `maxLength` assertions while retaining the original complete
  Draft 2020-12 schema for mandatory post-generation validation. It also pins a
  closed provider-keyword guard and integration regression. Design cells,
  prompts, model budget, metrics, human-expert plan, and USD 0 API ceiling are
  unchanged. No plan 1.4 subject call is authorized by prior consent.
