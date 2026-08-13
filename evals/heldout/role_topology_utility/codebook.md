# #582 evaluator codebook v0.1

## Shared unit rules

An atomic unit expresses one independently verifiable defect, evidence relation,
or revision operation. Split bundled units before labeling. Semantic equivalents
count once and retain the earliest-seat provenance. Restating the packet, a prior
seat, or a requirement is not unique value. Two independent arm-blinded experts
label first; a separate arm-blinded adjudicator resolves only disagreements and
retains both raw labels.

## Reviewer evidence rubric

- `detected`: correctly identifies the planted defect and its minimum correction.
- `partial`: notices a symptom but misdiagnoses or cannot support it.
- `missed`: final synthesis omits the planted defect.
- `false_blocker`: asserts a critical defect not present in the synthetic packet.
- `duplicate`: semantically repeats an earlier seat without new verified content.

Report critical and all-defect recall separately. Citation/evidence faithfulness
requires the exact supplied evidence id and a claim no stronger than that summary.
Editorial accept/reject language is not a metric.

## Writing revision rubric

- `requirement_satisfied`: the final text makes the full anchored change.
- `requirement_partial`: direction is correct but a required bound is absent.
- `requirement_unsatisfied`: required change is absent or contradicted.
- `unsupported_claim_introduced`: final text adds a fact or inference absent from
  the frozen packet.
- `constraint_violated`: final text violates an explicit task constraint.

Never label writing with `accept`, `reject`, `minor_revision`, or
`major_revision`. Report requirement coverage, supported-claim retention,
unsupported additions, constraint violations, and UVV separately.

## Inline solo role contracts

The suite-owned inline reviewer and writer are one-seat baselines. Each produces
its own final synthesis/text without simulating a panel. They receive the identical
scenario and per-call caps as every other seat, with no tools or gold access.
