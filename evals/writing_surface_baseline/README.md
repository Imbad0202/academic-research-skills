# Frozen writing-surface baseline (#830)

This baseline describes the existing saved held-out outputs at commit `060cb3cbffc2ca1bdfb8f7c6d2ffa4883cf09b1a`, before adding writing-surface instructions or changing any measurements.

Run from the repository root with Python 3.10 or later and Git:

```sh
python3 scripts/build_writing_surface_baseline.py \
  --source-ref 060cb3cbffc2ca1bdfb8f7c6d2ffa4883cf09b1a \
  > /tmp/writing-surface-baseline.json
cmp evals/writing_surface_baseline/baseline.json /tmp/writing-surface-baseline.json
```

The builder reads Git blobs at that commit, ignoring working-tree changes. The JSON records every input path and SHA-256 hash, the measurement and builder hashes, and the vocabulary hash. No timestamp or machine-specific path enters the output.

## Selection and coverage

The complete path selector is `eligible()` in `scripts/build_writing_surface_baseline.py`. It selects all 32 Markdown subject outputs under `evals/heldout/revision_claim_drift/runs/2026-08-07/subjects/`, excluding README files. It also selects all 108 saved Phase 2 seat reports and synthesis attempts under `evals/heldout/reviewer_seeded_defects/runs/raw/`, excluding blocked-run directories. Prompts, Phase 1 strategy files, fixtures, and judgements are excluded. Repeated attempts remain separate observations; these are not independent samples or unique manuscripts.

Of 140 selected outputs, 86 have complete Latin-token coverage and 54 are partial because they contain unsupported tokens. None is wholly unchecked. Per-file counts and measurements remain visible for all outputs. Distributions include only complete-coverage outputs and omit null measurements; each metric reports its own sample size. SMOG is omitted below 30 detected sentences. A complete Latin-token result does not establish that its source language was English; inspect individual records before interpreting them.

## Interpretation

The JSON records minimum, median, maximum, mean, and population standard deviation by corpus and in aggregate. These are descriptive values for saved repository outputs, without thresholds or recommended ranges. They neither compare against human writing nor establish scientific quality or authorship. Mixed-script exclusions, repeated attempts, synthetic tasks, and heuristic extraction limit generalisation. This is a baseline before the new instructions, not evidence that those instructions improve writing or that live callers follow them.
