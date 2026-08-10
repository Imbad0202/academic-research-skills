# Frozen measurement plan — tortured_phrase_conformance/1.0

Status: PRE-REGISTERED / NOT RUN. Issue: #660. Contract:
`heldout-measurement/1.1`; suite class: `mechanical_match`.

## Frozen subject and inputs

The subject is the exact accepted #660 implementation at the first commit reachable
on `main` that contains the complete implementation, public suite, and this plan. The
measurement row must use that same 40-hex main-history commit for both
`subject.config.suite_commit` and `preregistration.frozen_commit`; no working-tree,
plan-only, or later runtime is eligible.

The six seed/data inputs are:

- `scripts/fixtures/tortured_phrase_screening/snapshot.json`;
- `scripts/fixtures/tortured_phrase_screening/snapshot_manifest.json`;
- `scripts/fixtures/tortured_phrase_screening/seed_expectations.json`;
- `scripts/fixtures/tortured_phrase_screening/own_draft.md`;
- `scripts/fixtures/tortured_phrase_screening/own_draft.tex`; and
- `scripts/fixtures/tortured_phrase_screening/corpus_input.yaml`.

The full measurement subject also includes the test harness, runtime, every schema
and carrier fixture it loads, and the Python dependency environment disclosed in the
raw transcript. Every repository path is read from the same frozen commit. The six
items above are not an exhaustive dependency list and may not be substituted from a
later tree.

Only repository-owned synthetic phrases are in scope. No native PPS bytes, network,
model, API, human judge, model judge, or contextual classifier may be introduced.

## Frozen execution

From a clean checkout of the pinned commit, execute exactly once:

```text
python -m pytest -q scripts/test_tortured_phrase_screening.py
```

The exact command is encoded as UTF-8 with no trailing newline;
`execution_manifest.calls[0].prompt_sha256` is SHA-256 over those exact bytes. The
single retained transcript path is
`evals/heldout/tortured_phrase_conformance/runs/2026-08-10/raw/pytest-transcript.json`.
It is strict UTF-8 JSON without a BOM, serialized with sorted keys, no insignificant
whitespace, no non-finite values, and one terminal LF. Its closed fields are:

```text
schema_version = tortured-phrase-conformance-transcript/1.0
command_utf8
started_at
completed_at
exit_code
environment {
  python_implementation
  python_version
  pytest_version
  jsonschema_version
  ruamel_yaml_version
}
stdout_utf8
stderr_utf8
```

`command_utf8` equals the command above exactly. Start/completion are explicit RFC
3339 values; `environment` records the exact interpreter and required package
versions; stdout and stderr preserve the complete decoded strict-UTF-8 streams
separately; and exit code is the process exit status. The execution manifest's
`output_sha256` is SHA-256 over the exact transcript JSON bytes, so stdout, stderr,
exit status, command, and timestamps share one unambiguous framing. The report lists
that exact file under `raw_outputs.paths`.

The execution manifest is
`evals/heldout/tortured_phrase_conformance/runs/2026-08-10/execution-manifest.json`.
It has `created_at == calls[0].completed_at`, one call with
`call_id: tpc-2026-08-10-pytest` and `sequence_index: 1`, and makes no
`same_window`, `ordering`, or `concurrency` claim. No retry is permitted. A non-zero
exit, partial transcript, changed fixture/runtime bytes, or unavailable dependency is
a failed/blocked run and may not be replaced by a hand-authored success record. The
transcript and execution manifest are emitted once, hashed, and thereafter
write-once.

## Frozen metric and verdict

Primary metric: `synthetic_conformance_test_pass_rate`.

- Numerator: pytest test cases reported passed by the exact command.
- Denominator: all collected test cases in that exact command.
- A success verdict requires exit status 0, zero failed/error/skipped/xfailed/xpassed
  cases, and numerator equal to denominator.
- Any collection drift is visible in the raw transcript and reported count. There is
  no outcome-dependent exclusion, rerun, adjudication, or threshold adjustment.
- `replicates.per_item` is 1 with the explicit mechanical determinism exception; the
  same bytes are not rerun to manufacture variance.

The report publishes the exact passed/collected counts, `1.0` only if all cases pass,
and a `point_estimate` label strictly for this finite synthetic suite. It uses zero
judges, no agreement statistic, no adjudication, and no experimental arms.

The report freezes these envelope values:

- `decision_relevant: true`, `suite_class: mechanical_match`,
  `subject.model_id: deterministic-runtime/tortured_phrase_screening.py`, and the
  common main-history commit binding above;
- `judge_plan.exception: mechanical_suite`, `judges: []`, and
  `adjudication: {applies: false}`;
- `aggregate.agreement` is exactly `rate: null`, `divergent_items: []`, with a note
  saying there are no judges; the headline construction rule is the numerator divided
  by denominator under the success rule above;
- `replicates.per_item: 1` and an explicit exception that deterministic exact-byte
  replay is not rerun to manufacture variance;
- preregistration has the exact plan path/hash, the shared frozen commit,
  `frozen_before_dispatch: true`, `rubric_and_plan_frozen_together: true`, no rubric
  or judge-template fields, `amendments_append_only: true`, and an empty amendment
  ledger;
- `results.design: single-arm deterministic synthetic conformance`, both reserved arm
  arrays empty, and suite-specific `passed_tests`, `collected_tests`, `exit_status`,
  and `synthetic_conformance_test_pass_rate` fields; and
- on success, `attempts.partial_published: false` with no blocked runs; otherwise it is
  true and names the single failed/blocked call while retaining the raw transcript.

## Claim ceiling

A passing row may say only: “the pinned deterministic runtime passed the pinned
repository-owned synthetic conformance suite.” It remains `UNMEASURED` for contextual
validity and real-world false-positive/false-negative performance. It cannot certify
clean text or infer paper-mill, AI, misconduct, contamination, quality, acceptance, or
origin. Any wording beyond this ceiling invalidates the row.

## Amendments

The amendment ledger starts empty and is append-only. Any change to subject bytes,
fixtures, command, metric, success rule, claim ceiling, or retry policy requires a new
plan version and a new post-freeze run; it cannot be pooled with this plan.
