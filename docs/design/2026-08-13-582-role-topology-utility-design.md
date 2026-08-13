# #582 role-topology utility study: frozen offline design v0.1

Status: design, repository-owned synthetic seed, and no-call dry-run harness only.
No subject, expert, adjudicator, provider, model, API, tool, or measurement run is
authorized or reported by this change. Issue #582 remains open.

## 1. Question and dependency boundary

This study asks whether additional ARS role seats add task-specific verified value
that justifies their duplicate findings, elapsed time, and token cost. It does not
ask whether one topology is universally best and does not make full panels the
default. arXiv:2512.08296 is a hypothesis source only: its threshold,
decomposability score, and architecture equation are not imported.

The generic #263 deterministic evaluation runner is not a topology dispatcher.
This suite owns a separate offline materializer. The reviewer-class results may not
be interpreted until #653 publishes its prerequisite full-tier measured baseline.
Both eventual class reports use `heldout-measurement/1.1`; their metrics and
evaluator packets remain separate.

## 2. Two independent task classes

### 2.1 Decomposable reviewer evidence review

The unit is an atomic defect or evidence-alignment finding. Two synthetic fixtures
carry planted design, statistics, internal-consistency, qualitative-rigor,
citation-alignment, and scope defects. The four exact arms are:

| Arm | Seats | Frozen topology |
|---|---:|---|
| `review_inline_1` | 1 | one suite-owned inline reviewer/synthesizer |
| `review_panel_2` | 2 | methodology reviewer, then one synthesizer |
| `review_panel_5` | 5 | four parallel specialist reviews, then one synthesizer |
| `review_panel_7` | 7 | neutral field configuration, five separately scoped reviewers, then one synthesizer |

Reviewer outcomes are `detected`, `partial`, `missed`, `false_blocker`, and
`duplicate`. Metrics stay separate: critical-defect recall, all-defect recall,
evidence-anchor faithfulness, unique verified value, duplicate rate, false-blocker
count, elapsed time, input tokens, and output tokens. No aggregate quality score is
permitted.

### 2.2 Sequential writing and revision

The unit is an atomic required revision or an introduced unsupported claim. Two
synthetic fixtures require a bounded quantitative or qualitative paragraph
revision. The four exact arms are:

| Arm | Seats | Frozen topology |
|---|---:|---|
| `writing_inline_1` | 1 | one suite-owned inline revision writer |
| `writing_sequence_2` | 2 | revision coach, then one draft writer |
| `writing_sequence_5` | 5 | structure, argument, citation, revision coaching, then one writer |
| `writing_applicable_full_8` | 8 | all eight roles applicable to the bounded revision, in sequence, ending in one writer |

The evaluator vocabulary is requirement satisfied/partial/unsatisfied,
unsupported claim introduced, and constraint violated. `accept`, `reject`,
`minor_revision`, and `major_revision` are forbidden: a conference or editorial
decision label is not a writing-quality outcome. Metrics stay separate:
requirement coverage, supported-claim retention, unsupported claims introduced,
constraint violations, unique verified value, elapsed time, input tokens, and
output tokens.

## 3. Frozen execution controls

- Inputs: exactly four repository-owned English synthetic scenarios in
  `heldout_set.json`; gold fields never enter subject prompts.
- Replicates: exactly three per scenario-arm cell, paired by scenario and
  replicate id; no adaptive extension or replacement draw.
- Budget: every role call has an input cap of 24,000 tokens and output cap of
  1,500 tokens. Budgets never roll over between seats. More-role arms therefore
  have higher possible total cost; actual cost is an outcome, not hidden.
- Tools: empty allowlist; web, network, external corpus, and workspace reads are
  false. Only the materialized prompt packet is visible.
- Model: reasoning is frozen at `high`, no fallback is allowed, and every subject
  cell must use one exact provider/model. This design deliberately leaves the
  provider/model `UNSELECTED`; a new hash-frozen execution plan naming provider,
  model, CLI version, and authentication mode plus fresh consent is mandatory
  before any dispatch.
- Calls: the dry plan contains 186 subject-role calls: reviewer
  `2 scenarios × 3 replicates × (1+2+5+7) = 90`; writing
  `2 × 3 × (1+2+5+8) = 96`. Expert labeling is not included in that count.

## 4. Unique verified value

One UVV unit must satisfy every condition:

1. it is an atomic task-relevant finding or revision;
2. one role seat originated it before any other seat in that arm;
3. it is not semantically equivalent to the supplied input, a planted-description
   restatement, a requirement restatement, or an earlier role unit;
4. it is supported by a frozen evidence or requirement anchor;
5. two independent task experts blinded to arm, role count, topology, model, and
   aggregate judge it correct, or their separately blinded adjudicator resolves
   the disagreement; and
6. the final synthesis or revised text retains it.

Equivalent later units count once, credited to the earliest originating seat; the
later occurrences are duplicate cost. Reviewer and writing experts use different
rubrics and label packets. Labels cannot be reused across task classes. If two
independent experts and a blind adjudicator are unavailable, UVV and the study
headline are `NOT_COMPUTABLE`; no model-only substitute may be presented as human
verification.

## 5. Stopping, blinding, and uncertainty

Each scenario-arm-replicate is atomic. The first blocked, partial, malformed, or
protocol-deviating call stops the entire study. Retry count is zero. Preserve the
available bytes as blocked evidence, but do not impute, replace, score, or publish
them as measurement. Outcome-dependent early stopping is forbidden.

Subjects cannot see the exact arm id, paired-arm outputs, gold, expected metrics,
expert labels, or aggregate results. A later-stage seat necessarily receives its
own retained dependencies and may therefore infer aspects of the within-arm
topology; the plan does not make an impossible role-count blinding claim. Experts
and adjudicators cannot see arm id, role count, topology, provider/model, or
aggregates; experts also cannot see another expert's labels.

For every metric, publish all replicate values and matched deltas from that task's
one-seat arm. Only after six complete scenario-replicate pairs may the report add
the median, minimum, maximum, and positive/zero/negative sign counts. The small
synthetic seed carries no confidence interval or null-hypothesis test. Task classes
and metrics are never pooled into a scalar.

## 6. Offline harness and claims boundary

`scripts/run_role_topology_utility_dry_run.py` exposes only:

```bash
python scripts/run_role_topology_utility_dry_run.py validate-assets
python scripts/run_role_topology_utility_dry_run.py dry-run
python scripts/run_role_topology_utility_dry_run.py materialize --output-dir /new/empty/path
```

`dry-run` writes nothing. `materialize` refuses a non-empty destination and emits
self-contained neutral prompt templates with the complete source role-contract
bytes and the higher-precedence suite adapter embedded and hash-bound. Later-stage
templates carry explicit prior-call placeholders; a future dispatcher must replace
them with the named retained outputs, enforce the exact provider tokenizer against
the 24,000-token cap, and hash the final prompt before dispatch.

Every role row freezes a hash-bound study output contract. Intermediate reviewer
seats emit role-scoped findings, the field analyst emits configuration without
findings, and only the synthesis seat emits a final review. Intermediate writing
seats emit plans, maps, audits, or diagnostics without revised prose; only the
declared final writer emits the revised passage. This prevents repeated drafting
or shared findings from masquerading as a role-topology effect.

Production role files were not authored for these bounded synthetic inputs: for
example, their phase grammar may assume five reviewer cards, a complete paper, or
a patch document. Every prompt therefore embeds the hash-bound suite invocation
adapter as the higher-precedence runtime authority. The production contract is a
role-perspective source: identity, scholarly focus, anti-invention duties, and
role boundaries remain operative and are specialized by those per-seat output
contracts, while production phase, filesystem, tool,
panel-size, and output-format clauses do not. This disclosed adaptation keeps an
input-shape mismatch from masquerading as a topology effect.

The manifest's plan and held-out digests bind the canonical JSON snapshots used
to build that exact call list; validation deterministically rebuilds every call,
metadata field, dependency placeholder, and prompt from those same snapshots.
The dry-run records a conservative operational estimate
(`ceil(UTF-8 bytes / 3)` plus every dependency's full 1,500-token output cap) and
fails when it exceeds 24,000. This estimate is a preflight, not a provider-tokenizer
claim. The closed manifest keeps
`dispatch_authorized: false` and `measurement_generated: false`. There is no
dispatch or score command, provider import, network transport, retry, or result
writer. The materialized packet is not consent and cannot be renamed into evidence.

This slice establishes a testable protocol surface only. It does not dispatch 186
calls, label outputs, compare arms, generate a measurement row, close #582, or
claim that any role count adds value.
