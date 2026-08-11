# Frozen blinded expert guide — review-criteria-human-expert-label/1.0

You are labeling repository-owned synthetic review outputs. Work independently.
Do not seek or infer arm identity, mechanism state, another expert's labels, raw
aggregates, or the expected direction. Use only the blinded packet.

For every output, label each supplied criterion as `applicable`,
`not_applicable`, or `unresolved` from the manuscript. For every generated
finding, label:

- support: `supported`, `unsupported`, or `unresolved` from the supplied text;
- severity: `critical`, `major`, `minor`, `none`, or `unresolved`;
- venue alignment: `aligned`, `not_aligned`, `not_claimed`, or `unresolved`;
- usefulness from 1 to 5.

Usefulness anchors: 1 = absent, infeasible, invented, or author-intent
overriding; 2 = vague or materially under-specified; 3 = feasible but incomplete
on effort or trade-offs; 4 = feasible, scoped, and candid about costs; 5 = a
specific minimum remedy that preserves author intent, avoids invented evidence,
and clearly distinguishes stronger optional work. A justified `no honest remedy`
statement may be useful; do not reward a fabricated action merely for being
actionable.

Retain a short rationale per output. Return a JSON file conforming to
`expert_labels.schema.json`. The packet SHA-256 and your stable disclosed
`expert_id` bind the record. Do not view the arm map before your file is sealed.
