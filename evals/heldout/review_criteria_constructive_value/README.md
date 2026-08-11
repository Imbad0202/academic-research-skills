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
and human adjudication. The decision-relevant report uses the
paired-controls-only `human_expert_panel` exception: it binds the suite-owned
expert record by SHA-256 and carries zero model judges. The incremental metered
API spend ceiling is **USD 0**; subscription quota is disclosed. Dispatch is
manual and requires operator consent for provider, exact model, content class,
and quota/cost.

There is no automatic API fallback. A blocked subscription call stops the run
and is retained. Any proposed API run needs a new frozen plan, an explanation
of why CLI is insufficient, total
call count, worst-case USD estimate, and fresh explicit consent. Raw subject
outputs, raw expert labels, the exact execution manifest, and the final
`heldout-measurement/1.1` report are retained. Until such
a valid report is committed, ARS may say the mechanism is implemented but must
describe its behavioral effect as **unmeasured**.

Normative plan: `measurement_plan.md`. Closed adjudication record:
`paired_adjudication.schema.json`. Public scenario skeleton:
`heldout_set.json`.

## Contained run lifecycle

`suite_lock.json` seals the six synthetic scenarios, synthetic registry, ABBA/
BAAB 24-call plan, both prompt arms, output schemas, expert guide, and
adjudication contract, plus the exact runner and scorer bytes. Validate without
making a model call:

```bash
PYTHONPATH=scripts python scripts/run_review_criteria_constructive_value.py validate-assets
PYTHONPATH=scripts python scripts/run_review_criteria_constructive_value.py detect --model <exact-gpt-model>
```

After the locked assets are on one clean main-history commit, initialize a new
run directory. This only writes the 24 exact prompts and a run plan; it does not
dispatch:

```bash
PYTHONPATH=scripts python scripts/run_review_criteria_constructive_value.py init-run \
  --run-dir <new-run-dir> --suite-commit <40-hex-commit> \
  --model <exact-gpt-model> --codex-version <exact-version> \
  --reasoning-effort high --input-token-cap 12000 --output-token-cap 3000
```

The operator reviews the resulting `run-plan.json` and its printed SHA-256.
Only a separately confirmed command carrying that exact digest and the explicit
24-call flag may consume subscription quota:

```bash
PYTHONPATH=scripts python scripts/run_review_criteria_constructive_value.py dispatch \
  --run-dir <run-dir> --plan-sha256 <exact-sha256> \
  --execute-24-subscription-calls
```

Dispatch requires `Logged in using ChatGPT`, copies only subscription auth into
an ephemeral home, strips API-key variables, uses an empty read-only work root,
disables local/web/app/plugin/agent tools, scans the JSONL event stream, and
stops on the first blocked call. Exact completed receipts are resumable without
another model call. CI and ordinary validation never invoke `dispatch`.

After all 24 outputs exist, `prepare-expert-packet` writes a randomly blinded
packet and a separate arm map. Two independent humans submit files conforming
to `expert_labels.schema.json`; a blind adjudicator submits
`adjudication_decisions.schema.json`. `validate-labels` and `finalize` retain raw
labels, prohibit overturning unanimous labels, verify the sealed arm map, and
produce the scorer input. The arm map is never sent to experts before their
files are sealed.

With the packet, arm map, both raw label files, decisions, and final paired
record retained under the run directory, `build-report` creates and resolves a
`heldout-measurement/1.1` report. It selects `human_expert_panel`, leaves
`judges` empty, embeds the separate scorer metrics with `composite_score: null`,
and binds the expert record and write-once execution manifest by SHA-256:

```bash
PYTHONPATH=scripts python scripts/run_review_criteria_constructive_value.py build-report \
  --run-dir <run-dir> --paired-adjudication <run-dir>/paired-adjudication.json \
  --measurement-date YYYY-MM-DD \
  --output evals/heldout/review_criteria_constructive_value/measurement-YYYY-MM-DD.json
```
