# Claim-Standing Probe — Stance Seed Set (#655, v0.1)

Authority: `docs/design/2026-08-13-655-search-bounded-claim-standing-probe-design.md`
(§5.1 closed labels, §8 held-out stance set and baseline gate).

```text
STANCE CLASSIFICATION UNMEASURED
```

## Current status

This directory holds the **seed** required by design §8: repository-owned
synthetic claim/candidate pairs, the closed label vocabulary as schemas, the
expert label guide, and a mechanical scorer. **No probe implementation, no
expert labels, no adjudication, no subject run, and no baseline measurement row
exist.** Accordingly:

- `claim_standing_probe` is **deliberately absent from
  `evals/heldout/suite_registry.json`** — registration happens in the
  implementation PR that carries a valid baseline row under the #654/#664
  contract (the validator fails if the suite is registered while the set says
  `seed_unmeasured`);
- nothing here supports any accuracy, usefulness, or coverage claim.

## Contents

- `heldout_stance_set.json` + `.schema.json`: 32 items (16 en + 16 zh-TW), one
  discipline each, covering per language: support ×2, contradict ×2, mixed ×2,
  not_addressed ×2, INSUFFICIENT_EVIDENCE ×2, AMBIGUOUS ×2, missing-abstract,
  metadata-only, irrelevant-candidate, and session-held-full-text slots.
  Claims and abstracts were **cross-model authored** (Codex `gpt-5.6-sol`,
  reasoning xhigh, 2026-08-14) so the future subject's model family did not
  write its own test items; all content is synthetic (fictional actors,
  instruments, venues; DOIs use the reserved `10.99999/csp-*` form).
- `label_guide.md`: the expert labeling procedure operationalizing design
  §5.1's closed enum and cross-field rules (relevance first; missing evidence
  is never `not_addressed`; explicit both-directions → `mixed`, otherwise
  `AMBIGUOUS`; no scalar confidence anywhere).
- `expert_label.schema.json`: one blinded expert's raw label file (≥2
  independent domain-qualified experts required).
- `adjudicated_labels.schema.json`: the sealed ground truth — expert files are
  hash-bound, every disagreement resolved by a separate adjudicator blind to
  subject output, raw labels retained.
- `subject_output.schema.json`: the strict enum surface the future subject
  emits; deliberately closed with no confidence/probability/score field.
- `stance_score_report.schema.json`: the deterministic comparison artifact.
- `scripts/validate_claim_standing_stance_assets.py`: schema + invariant
  validator (slot coverage, id/doi binding, zh-TW simplified-character screen
  as a heuristic defect detector, registration guard).
- `scripts/claim_standing_stance_scorer.py`: the mechanical scorer required by
  design §8 — compares the frozen subject enum to the adjudicated label with
  no model in the loop; reports stance/relevance/check-state confusion counts
  by language, evidence-scope agreement counts, and failure-class counts
  (per-scope and per-failure-class accuracy strata belong to the future
  baseline-row compiler); macro recall and micro accuracy stay separate; an
  abstention on a gold-performed row lands in an explicit
  `NOT_CHECKED` confusion column so abstaining can never inflate recall;
  full-row accuracy includes evidence scope; blocked/partial rows keep their
  failure classes visible and are never imputed; the two-replicate
  decision-relevance flag is computed, not assumed; the adjudication file must
  bind at least two distinct expert label files.

## design_target is not ground truth

Each item carries a `design_target` (the relation its text was commissioned to
realize). It exists for construction coverage accounting only. It is **never**
ground truth, never enters the scorer as gold, and must be stripped from any
expert or subject packet. Ground truth comes exclusively from at least two
independent blinded expert label files plus adjudication
(`adjudicated_labels.schema.json`).

## What must still happen before a baseline row (design §8)

Frozen here: item set, label vocabulary/guide, record schemas, mechanical
scorer. Still future, owned by the implementation PR: the exact eligible
population and sampling rule binding the probe's trigger; the subject prompt,
model/runtime/token settings, replicate and stopping rules, and execution
manifest (hash-frozen before dispatch); expert recruitment, labeling, and
adjudication; the baseline stance-classification measurement row under the
#654/#664 contract; and suite registration. Any model or human dispatch
requires separate consent to the exact frozen plan.

## Accepted seed boundaries

- Static text can only realize the `abstract_missing` failure family; the
  runtime failure classes (`source_missing`, `access_failed`,
  `retrieval_failed`, `judge_timeout`, `judge_error`, `parse_error`) are
  subject/harness vocabulary, to be exercised by fault injection in the
  implementation PR's run plan, not by fixtures.
- The scorer verifies that the adjudication file names two distinct experts
  with distinct file hashes and covers every item, and
  `validate-expert-file` checks one expert file's complete distinct item
  coverage — but nothing here verifies the referenced expert files' bytes
  against the recorded hashes; sealing and hash-verifying expert packets is
  the implementation PR's labeling-workflow tooling.
- Design §5.1's "at least one evidence-row reference" applies to the
  implemented probe's #656 evidence rows; the eval subject output carries a
  bounded rationale and evidence scope instead, because no evidence-row
  surface exists in the seed.

## Offline validation

```bash
python3 scripts/validate_claim_standing_stance_assets.py validate-assets
```
