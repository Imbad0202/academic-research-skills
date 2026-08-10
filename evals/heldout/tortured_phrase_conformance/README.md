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

The frozen post-main measurement was executed once on 2026-08-10 against commit
`86bf0e5c2cedb300d6d1c6428470cdcedfbf97df` under the precommitted
[measurement plan](measurement_plan.md). The exact registered command returned exit
status 0 with 190 of 190 collected tests passed. The
[measurement row](measurement-2026-08-10.json) uses zero judges,
`judge_plan.exception: mechanical_suite`, and `adjudication.applies: false`; its
[raw transcript](runs/2026-08-10/raw/pytest-transcript.json) and
[write-once execution manifest](runs/2026-08-10/execution-manifest.json) retain the
exact execution evidence.

The supported conclusion is only that the pinned deterministic runtime passed the
pinned repository-owned synthetic conformance suite. Contextual validity and
real-world false-positive/false-negative performance remain `UNMEASURED`.

The synthetic positive cases mean “the frozen matcher must emit this match.” The
synthetic negative cases mean “the frozen matcher must not emit this match.” They are
not empirical false-positive or false-negative rates and are never relabelled as such.
