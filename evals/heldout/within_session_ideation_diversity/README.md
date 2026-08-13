# Within-Session Ideation Diversity (#659, v0.1)

This suite freezes a bounded evaluation of two Layer-1 Socratic mechanisms. The
authority is
[`docs/design/2026-08-13-659-within-session-ideation-diversity-design.md`](../../../docs/design/2026-08-13-659-within-session-ideation-diversity-design.md).

## Current status

Phase 1 only: design, codebook, synthetic actor-role seed, non-production
ablation transform, validator, and tests. **No subject, actor, judge,
adjudicator, or baseline run exists.** No breadth-efficacy claim is computable.

## Contents

- `heldout_set.json`: three English/zh-TW scenario pairs with private synthetic
  scholar-role inventories;
- `heldout_set.schema.json`: closed Draft 2020-12 fixture schema;
- `codebook.md`: frozen units, labels, exclusions, metrics, and blinding rules;
- `nonproduction_variant.json`: exact source digest and replacements for the
  exploratory-guardrails ablation;
- `scripts/validate_ideation_diversity_assets.py`: offline asset and variant
  validator/materializer.

## Offline validation

```bash
python scripts/validate_ideation_diversity_assets.py validate-assets
python scripts/validate_ideation_diversity_assets.py materialize-variant \
  --output /path/to/new/nonproduction-socratic-mentor.md
```

`materialize-variant` refuses an existing output path. It writes a derived
non-production prompt; it never changes
`deep-research/agents/socratic_mentor_agent.md`.

## Claims and dispatch boundary

The role cards are repository-owned synthetic material. They do not represent
real scholars or measure real creativity. Count, dispersion, and facet
follow-through remain separate; model-originated framings never earn scholar
credit.

Before any baseline, freeze and hash an exact run plan under the shared held-out
measurement contract. A decision-relevant run needs at least two independent
replicates per scenario-arm cell, at least two independent blinded judges, and a
separate blind adjudicator. Obtain fresh consent for the exact subject/actor/
judge plan. No earlier model-run consent applies.

The final report uses `heldout-measurement/1.1` with suite class
`paired_controls`. #659 stays open until the per-mechanism baseline and its raw
evidence are published.
