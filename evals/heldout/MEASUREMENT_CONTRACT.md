# Held-Out Measurement Contract (#654, `heldout-measurement/1.0`)

Issue: #654. Machine artifacts: `measurement_report.schema.json` + `suite_registry.json`
(this directory). Enforcement: `scripts/check_heldout_measurement_report.py` —
schema branches B1-B4, cross-field invariants I1-I12, reference-resolution
checks R1-R3 (the rubric file must exist and match its hash, raw-output paths
must exist, the suite commit must be a real object in this repository), and
location binding L1 (a row filed under `evals/heldout/<dir>/` must declare
`suite == <dir>`); mutation-tested by
`scripts/test_check_heldout_measurement_report.py`; CI runs `--all`.

## Premise

There is no unified held-out harness and this contract does not create one:
`scripts/run_evals.py` discovers `evals/gold/` only, and the suites under
`evals/heldout/` stay deliberately undiscovered (their subject is an LLM, not a
script). What the suites previously lacked was a **shared report envelope**: each
published row disclosed its judge, adjudication, and replicate discipline in its own
ad-hoc shape. This contract standardizes the envelope; suite-specific payloads stay
suite-specific.

External anchor: Ren et al. (arXiv:2607.13104) §8.1.2 recommends repeated runs with
variance estimates, aggregation across judge instances, evaluator independence, and
exact judge/rubric/budget disclosure. Two rules layered on top are **ARS design
choices, not Ren requirements**: judges drawn from different model families, and
pre-registered maintainer adjudication.

Sibling envelope: `shared/benchmark_report_pattern.md` + `shared/benchmark_report.schema.json`
govern ARS-versus-human benchmark reports (scorer-independence vocabulary:
`scoring_independence`). The two artifact families stay separate by design; do not
grow a third — extend one of these.

## Opt-in and retrofit scope

A report opts in by carrying `"measurement_contract": "heldout-measurement/1.0"`
(the version constant is single-sourced from the schema's `const`). The contract
governs **future runs and re-runs only**. Legacy rows (e.g.
`revision_claim_drift/measurement-2026-07-22.json`, the `rq_framing_offlist`
2026-07-11 rows, the E4 cohorts) are never retrofitted, rewritten, or re-validated.

Discovery is by marker, not by filename: the checker's `--all` mode walks
`evals/heldout/` (case-insensitive `.json`, following directory symlinks with a
cycle guard) and validates every file carrying the `measurement_contract` key,
wherever a suite files its rows. Files that never mention the key are not parsed
at all; a file that mentions it but fails strict JSON parsing (duplicate keys,
non-finite numbers, undecodable bytes) fails loudly, and a near-miss marker value
(homoglyph, stray whitespace, case games) fails loudly rather than skipping
validation. Unmarked files are skipped by design.

The #652 interaction is the canonical exception pattern: a re-measurement that must
stay comparable to a legacy baseline keeps the **original judge configuration as its
legacy-comparability row** (`judge_plan.exception: "legacy_comparability"`, which
must name the legacy row in `judge_plan.legacy_baseline_ref` — branch B4), and any
additional judges report separately — never merged into the comparability row.

## Suite classes and the registry

`evals/heldout/suite_registry.json` is the **authoritative** suite → class mapping;
a report's `suite` must be a registry key and its `suite_class` must match (I5) —
mislabeling the class cannot shed clauses. New suites register there first. The
table below is an informative mirror:

| Suite | Class | Notes |
|---|---|---|
| `revision_claim_drift` | `llm_judged` | cross-model judge + maintainer adjudication |
| `rq_framing_offlist` | `llm_judged` | judge + replicate protocol already in its README |
| `pipeline_behavior_robustness` | `mechanical_match` | full-expectation mechanical match; judge only transcribes |
| `reviewer_seeded_defects` | `seeded_manifest_adjudicated` | E4 machinery remains normative and unchanged; see adoption surface below |
| `re_review_persuasion_invariance` | `paired_controls` | reuses E4 machinery per its README (SD-11) |

Class semantics (schema branches B1-B3 + checker):

- `mechanical_match` may run zero judges (`judge_plan.exception: "mechanical_suite"`,
  `adjudication.applies: false`) — pass/fail is a mechanical match against
  documented expectations.
- `llm_judged` and `seeded_manifest_adjudicated` require `adjudication.applies: true` (B2).
- Every non-mechanical class requires >= 1 judge (B1), and the `mechanical_suite`
  exception is legal only on `mechanical_match` (B3).
- `paired_controls` requires judges but not adjudication: its verdicts are
  per-pair expectation matches anchored to spec clauses; adjudication applies (and
  should then be declared) only when judged elements enter the comparison.

**Adoption surface for E4-shaped suites** (`reviewer_seeded_defects`,
`re_review_persuasion_invariance`): the envelope is a whole-file format, and E4
per-run records keep their own shape (emitted by `dispatch_e4_panel.py`, governed
by the `reviewer-e4/*` evidence contract). Those suites adopt at the **cohort
roll-up level**: a `measurement-<date>.json` summary row in envelope form whose
`raw_outputs.paths` reference the per-run records under `runs/` — the envelope adds
disclosure around the E4 machinery, it does not replace or reshape it.

## Multi-judge rules

- **The judge minimum is derived, never author-declared**: a decision-relevant,
  non-mechanical run with `judge_plan.exception: "none"` requires **>= 2 judge
  configurations from >= 2 distinct model families** (I2; families compared
  case-/NFKC-folded). Fewer judges requires a labeled exception; `"none"` is not a
  label. Identity hygiene backs the count (I9, all fields fold-compared):
  duplicate `judge_id`s, one `model_id` under two family labels, or two judges
  sharing the same `(model_id, prompt_ref)` configuration are all rejected.
  These are the mechanically detectable forms — an *aliased* model id
  (`gpt-x` vs `gpt-x-run2`) is not machine-decidable and stays a review item
  (§ Known residue).
- **Per-judge disclosure is mandatory** (schema-required): exact `model_id`,
  `model_family`, `prompt_ref`, `evidence_provided`, `judging_budget`, and the full
  `per_item` rows — each row carries at least one verdict field beside `item_id`,
  and judged suites may not publish empty `per_item` arrays (B1). Verdict fields
  must be **comparable across judges**: per-item key-sets must match (I9), payload
  comparison is type-aware (JSON `true` and `1` are different verdicts), and item
  ids are folded (NFKC + format-character strip) before indexing so a zero-width
  re-spelling cannot split an item into two (I9, the #524 fold-before-compare
  lesson).
- **Judge failure**: a judge that fails an item after the declared retry policy
  (`attempts.atomicity`) leaves that item out of its `per_item` rows. On a
  decision-relevant run every such gap must be named in `attempts.blocked_runs`
  and `partial_published` must be true (I11) — on non-decision runs the gap is a
  W1 warning. Replacement judges are new `judges[]` entries, disclosed like any
  other — never a silent swap.

## Aggregation

- **Agreement rate is a diagnostic, never the headline** — and it is recomputed,
  not trusted: the checker recomputes `1 - |divergent| / |items judged by >= 2
  judges|` and rejects a mismatched or null-when-computable rate (I1). The headline
  metric declares its `construction_rule` — how per-judge rows and adjudication
  produce the number, including tie handling when judges split evenly (state the
  rule; the default is "ties escalate to adjudication", not majority-of-two).
- **Divergent items surface individually** (`aggregate.agreement.divergent_items`),
  and the declared list must **equal** the recomputed divergent set: real divergence
  must be listed (I8) and non-divergent items may not be declared divergent (I3).
  Every divergent item needs a recorded resolution — an adjudication override in
  adjudication-required classes, a non-empty `agreement.note` otherwise (I10).

## Replicates and spread

- `replicates.rule_ref` anchors the suite's own replicate rule — the contract
  records each suite's rule; it does not force uniformity across suites.
- **Decision-relevant runs replicate >= 2 per item** (I6); a seed/exploratory run
  below that either sets `decision_relevant: false` or writes an explicit
  `replicates.exception`. Where behavior is stochastic, report `spread`, not just
  point estimates.

## Adjudication (pre-registered, blinded, raw-preserving)

- The rubric is committed in-repo and **hashed before any judge output exists**
  (`rubric_sha256`; `rubric_precommitted` is a schema-level `const: true`
  attestation). At validation time the reference must resolve: the rubric file
  exists in the repository and its recomputed sha256 matches (R1); raw-output
  paths exist (R2); the subject's `suite_commit` is a real commit here (R3).
  Amendments after first use are new rubric versions with new hashes, logged in
  the run notes — never silent edits. What stays human-audited: that the hashed
  rubric's *commit date* precedes the judge outputs, and that each override's
  `raw` transcription is faithful — the checker binds identities, the maintainer
  attests history.
- `blinded_to` enumerates exactly which dimensions the adjudicator was blinded to:
  `condition`, `mechanism_state`, `subject_model`, `judge_identity`,
  `expected_label`, `raw_aggregate`. An empty list is legal and honest; an
  undeclared blinding claim is not.
- Every override records the **criterion it applied** (`criterion_ref` into the
  precommitted rubric) — adjudication against a standard, not taste — and targets a
  judge that exists and an item that judge actually scored (I4).
- **Raw pre-adjudication numbers always publish alongside adjudicated ones**
  (`raw_published: const true`; the revision_claim_drift baseline already practiced
  this — the contract makes it structural).
- Raw subject and judge outputs are retained at `raw_outputs.paths`
  (`retained: const true`, non-empty paths per I7).

## What this contract is not

- Not a runner: nothing here executes suites or changes `run_evals.py`.
- Not a gate on suite semantics: `results` and per-item verdict fields stay
  suite-specific; E4's own evidence contract and closed status fields remain the
  normative machinery for `reviewer_seeded_defects` (and, via SD-11,
  `re_review_persuasion_invariance`), with the envelope adopted at the cohort
  roll-up level only.
- Not the benchmark envelope: ARS-versus-human benchmark reports stay under
  `shared/benchmark_report_pattern.md`.
- Not retroactive: README/CHANGELOG claims built on legacy rows keep citing those
  rows as-is; only new rows gain the envelope's stronger disclosure.

## Known residue (human-audited by design)

The checker binds identities and recomputes what is recomputable; the following
stay with the human reviewer, deliberately:

- **Verdict semantics.** The envelope forces per-item rows to carry verdict
  fields and key-sets to match, but cannot know that a field IS a verdict: a
  constant field on every row yields a formally correct `agreement.rate` that
  carries no information, and `aggregate.headline.value` is never derived from
  the rows (`construction_rule` is the auditable statement). Constant-verdict
  runs are legitimate (clean-control panels agree everywhere), so no invariant
  can close this without false-firing — the reviewer audits that per-item
  fields are real suite verdicts.
- **`decision_relevant: false` is a self-declaration** — and the widest waiver
  in the contract (sheds I2 and I6, demotes I11 to W1). Whether a row is
  actually cited for a decision is a review question; a row cited in
  README/CHANGELOG with `decision_relevant: false` is a red flag reviewers
  look for.
- **Aliased judge identities.** I9 rejects every mechanically detectable form
  of judge duplication; a renamed `model_id` under an invented family label is
  not detectable from the report alone.
- **Pre-registration history.** R1 proves the committed rubric matches its
  hash; that the rubric's commit *predates* the judge outputs is attested in
  the run notes and checkable from git history at review time, not by the gate.
- **Override transcription.** `overrides[].raw` is bound to a real judge and a
  scored item (I4), but its faithfulness to that judge's actual output is a
  logic read.
- **Blocked-run attribution.** I11 requires the missing *item* to be named
  (token-delimited) in `attempts.blocked_runs`; which judge failed is prose.
- **Registry governance.** A suite key can land in the same PR as its first
  report; PR review is the control for that ordering.
- **Exception sincerity.** `replicates.exception` must be a written sentence
  (schema minLength), but a schema cannot test sincerity — 20 characters of
  filler satisfy the letter. The reviewer reads the sentence.
- **Identifier folding.** Ids and identity fields are compared NFKC-folded
  with format characters stripped (anti-spoof); two intentionally distinct
  compatibility-character spellings will collide and be rejected. Use ASCII
  ids (all current suites do).
