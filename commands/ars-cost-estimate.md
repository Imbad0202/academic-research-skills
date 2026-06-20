---
description: Estimate token usage and cost for a given ARS command pipeline.
model: sonnet
---

# `/ars-cost-estimate`

**Purpose**: Provide a quick estimate of how many tokens (and approximate monetary cost) a series of ARS commands will consume.

**Usage**:
```
/ars-cost-estimate --pipeline "ars-plan -> ars-full -> ars-reviewer"
```
- `--pipeline` – a `->`‑separated list of ARS commands you plan to run.
- `--model` – optional model name (default `sonnet`).

**Behaviour**:
1. Parses the pipeline and looks up each command’s typical token budget (defined in `docs/PERFORMANCE.md`).
2. Sums the tokens and multiplies by the model’s per‑token price (hard‑coded for common models).
3. Returns a JSON report:
   ```json
   {"total_tokens": 12345, "estimated_cost_usd": 0.67}
   ```

**Related docs**: See `docs/PERFORMANCE.md` for per‑command token budgets and pricing tables.
