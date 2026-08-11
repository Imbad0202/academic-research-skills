# Review-criteria constructive-value paired evaluation (#684)

Status: **PRE-REGISTERED / NOT RUN / EFFECT UNMEASURED**.

This held-out suite measures whether the #684 pointer binding and constructive
finding contract improve review behavior. It does not measure the deterministic
manifest builder; its subject is the three criteria-aware consumer prompts.

The paired arms are:

- `baseline`: the frozen pre-#684 prompt surface; and
- `treatment`: the same prompt surface plus the manifest marker, Target
  Criteria Brief, conflict discipline, and constructive-finding contract.

Each pair uses the same sealed scenario bytes, exact `ReviewTargetContext`,
model, sampling settings, tools, input/output token caps, and replicate count.
Only the #684 mechanism differs. Every item has at least two fresh replicates
per arm. Phase 1 is manuscript-blind in both arms.

Two or more independent domain/methodology experts label the blinded outputs.
They adjudicate disagreements without seeing arm identity. The closed
post-adjudication record covers:

1. exact profile resolution;
2. criterion applicability;
3. supported versus unsupported findings;
4. Critical/Major severity agreement;
5. confirmed-venue alignment; and
6. remedy usefulness on a 1–5 anchored scale.

Metrics are reported separately. There is no composite review-quality score and
no single metric can be substituted for another. `scripts/score_review_criteria_constructive_value.py`
only reduces a completed, expert-adjudicated record; it does not call a model,
judge, API, network, clock, or filesystem scanner.

The scenario content must be synthetic or explicitly authorized. The default is
24 isolated Codex CLI subject calls under the operator's ChatGPT subscription
(six items x two arms x two replicates), followed by blinded human expert labels
and human adjudication. The decision-relevant report separately requires two
judge configurations from two model families; each uses a subscription CLI
where available, and human experts do not replace that envelope requirement. The
incremental metered API spend ceiling is **USD 0**; subscription quota is
disclosed. Dispatch is manual and requires operator consent for provider, exact
model, content class, and quota/cost.

There is no automatic API fallback. A blocked subscription call or missing
second subscribed judge family stops the run and is retained. Any proposed API
run needs a new frozen plan, an explanation of why CLI is insufficient, total
call count, worst-case USD estimate, and fresh explicit consent. Raw subject
outputs, judge outputs, the exact execution
manifest, and the final `heldout-measurement/1.1` report are retained. Until such
a valid report is committed, ARS may say the mechanism is implemented but must
describe its behavioral effect as **unmeasured**.

Normative plan: `measurement_plan.md`. Closed adjudication record:
`paired_adjudication.schema.json`. Public scenario skeleton:
`heldout_set.json`.
