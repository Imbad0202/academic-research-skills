# Citation-Extraction Gold Subset (Phase 1a)

50-tuple gold subset measuring the per-citation `lookup_verified` 3-class enum classification accuracy. Phase 1a shipped the data; **Phase 1b (#263) shipped the harness** (`scripts/run_evals.py`) — it now measures this gold set directly.

Run it with:

```
PYTHONPATH=. python -m scripts.run_evals --task citation_extraction
```

The harness computes the predicted `lookup_verified` itself from each tuple's `resolver_outcomes.*.status` via the #182 Delta 4 reducer (`verification_gate.verify_citation` has not shipped yet; the reducer reconciles when it does). The metric is symmetric 3-class accuracy — `unresolvable` is never collapsed into `false`. Because `expected_outcomes.json` was authored by the same rule, a fresh run scores ~1.0.

## Spec reference

`docs/design/2026-05-21-v3.10-184-extend-eval-harness-spec.md` §3.1.1

## Tuple distribution

| ID range | Kind | n | Expected `lookup_verified` |
|----------|------|---|---------------------------|
| 001–020 | `valid_doi` (DOI, no arXiv) | 20 | `true` |
| 021–030 | `valid_arxiv` (arXiv, no DOI) | 10 | `true` |
| 031–040 | `fabricated` (intentionally-bogus DOI + title) | 10 | `false` |
| 041–045 | `manual_exempt` (`obtained_via: manual`) | 5 | `unresolvable` |
| 046–050 | `fabricated` (intentionally-bogus DOI + title) | 5 | `false` |

## Threshold contract (v3.10.0 binding defaults)

- Aggregate: `accuracy >= 0.90` across all 50 tuples
- Per-class: `accuracy >= 0.85` for each of `true` / `false` / `unresolvable`

Changing these before v3.10.0 ship requires a spec amendment per #184 §3.1.1 / E-V2.

## Tuple file naming

`NNN-{kind-slug}-{discriminator}.json` (zero-padded NNN, lowercase-hyphenated). Filename stem must match the `tuple_id` field inside.

## Fabricated-reference safety

Tuples 031–040 and 046–050 use intentionally-bogus DOIs (`10.99999/ars184.fake.<domain>.<seq>`) and bogus titles. Each carries `fabrication_intent: true` per public-repo discipline. Do not source fabricated tuples from real-but-misattributed citations.

## Amendment: `valid_unresolvable` class removed

The original spec defined a `valid_unresolvable` class (tuples 031–040) — real citations
that are unmatched across all four resolvers. No stable, first-party-verifiable source
satisfying that constraint was found under current index coverage, so the class was
removed and 031–040 are now `fabricated`. The `false` class is carried by `fabricated`
tuples. A known coverage gap (no real-but-unindexed tuple to exercise the resolver's
fuzzy-match false-positive path) is tracked in issue #250.

## Human expert verdicts

10 of 50 tuples (20% per Delta 5) carry an optional `human_expert_verdict` field. The Phase 1b harness emits an `expert_concordance` row per class from these labeled tuples (agreement of the expert verdict vs `expected_outcomes.json`). The verdicts are advisory only — synthetic ground truth in `expected_outcomes.json` is the source of truth for CI gates per E-V3, and concordance never gates.

## Validator

Run this command from the repo root to validate the corpus against its manifest:

`python -m scripts.check_evals_gold_set evals/gold/citation_extraction`

## Lift gate

When a PR changes ranking / scoring logic, run the harness on the base and the change, then compare:

```
PYTHONPATH=. python -m scripts.run_evals --output before.json   # on base
PYTHONPATH=. python -m scripts.run_evals --output after.json    # on change
python -m scripts.check_ranking_lift --baseline before.json --compare after.json --pr-body @pr.txt
```

The gate blocks on any polarity-corrected `signed_lift < -0.05` (or a zero-baseline metric change) unless the PR body carries `[ranking-regression-acknowledged]` + an OPEN follow-up issue and declares the `Affected metric: <task>.<class>.<metric>`. CI wires this via `.github/workflows/eval-harness.yml`.
