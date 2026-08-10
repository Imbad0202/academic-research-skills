# Tortured-Phrase Mechanical Conformance

Issue: #660. Suite class: `mechanical_match`.

This suite measures only whether the deterministic #660 runtime matches the public,
repository-owned synthetic expectations in
`scripts/fixtures/tortured_phrase_screening/seed_expectations.json`. It does not
contain Problematic Paper Screener content, a native PPS importer, real manuscripts,
or contextual false-positive/false-negative labels. A passing row therefore supports
only a synthetic grammar/normalization/parser/replay conformance statement. It does
not support claims about real-world accuracy, paper-mill or AI origin, source quality,
source cleanliness, publisher screening, or contextual validity.

The implementation PR registers and freezes this suite but remains `UNMEASURED`.
Measurement occurs only after that exact implementation is reachable on `main`, under
the precommitted [measurement plan](measurement_plan.md). The resulting
`heldout-measurement/1.1` row uses zero judges,
`judge_plan.exception: mechanical_suite`, and `adjudication.applies: false`. Raw
command/output bytes and a write-once execution manifest remain beside the row.

The synthetic positive cases mean “the frozen matcher must emit this match.” The
synthetic negative cases mean “the frozen matcher must not emit this match.” They are
not empirical false-positive or false-negative rates and are never relabelled as such.
