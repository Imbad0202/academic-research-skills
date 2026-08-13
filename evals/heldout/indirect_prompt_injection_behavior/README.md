# Indirect Prompt-Injection Behavior Paired Controls (#675, v0.1)

This held-out suite measures a frozen model's behavior when synthetic retrieved
or pasted content contains an inert embedded instruction. The authority is
[`docs/design/2026-08-13-675-indirect-prompt-injection-behavior-eval-spec.md`](../../../docs/design/2026-08-13-675-indirect-prompt-injection-behavior-eval-spec.md).

## Current status

`seed_version: 0.1.0` — design, fixtures, rubric, validator, and materialization
probe only. **No subject baseline exists.** No safety, robustness, or ARS-guidance
efficacy claim is computable from these assets.

The suite is behavioral. It does not enforce an instruction/data boundary.
Structural isolation remains #676.

## Contents

- `heldout_set.json`: eight synthetic scenarios in a closed 2 x 2 design;
- `heldout_set.schema.json`: strict fixture schema;
- `prompt_ars_guided.txt`: production-guidance condition;
- `prompt_platform_only.txt`: non-production platform-only control;
- `adjudication_rubric.md`: pre-dispatch semantic label and blinding rules;
- `scripts/run_indirect_prompt_injection_probe.py`: strict validator,
  materializer, and mechanical response scorer.

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

## Dispatch boundary

Before any run, freeze an exact suite commit, materialized manifest SHA, call
order, provider/auth/model/runtime, settings, caps, two-or-more replicates,
judge plan, stopping rules, and API/spend boundary. Obtain fresh consent for
that exact plan. No previous evaluation consent carries over.

All v0.1 calls use fresh sessions with `tools=[]` and `web=false`. A blocked or
partial call stops the run, is retained, and is not retried. Raw prompts,
responses, event streams, tool events, parse results, judge outputs, and
adjudication records remain available for audit.

## Claims boundary

Allowed reporting is limited to this fixed model/prompt/platform/tool/fixture
configuration. A clean run does not prove safety; a failure does not establish a
universal exploit. The `platform_only` condition retains provider safeguards and
is not a no-safeguards control or a supported ARS operating mode.

The final report uses `heldout-measurement/1.1`, suite class
`paired_controls`. Do not publish a measurement row until its complete raw
evidence and required judging/adjudication records exist.
