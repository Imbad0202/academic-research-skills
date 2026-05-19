# De-AI Module Reference

Purpose: Detect and reduce AI-generated writing traces while preserving LaTeX syntax and technical accuracy.

## Core Principles

1. **Syntax preservation**: Never modify `\cite{}`, `\ref{}`, `\label{}`, math, or LaTeX commands
2. **Zero fabrication**: Never add data, metrics, comparisons, or claims
3. **Information density**: Every sentence must convey verifiable information
4. **Restrained wording**: Avoid unsupported certainty; use appropriate hedging

## High-Priority AI Patterns (Must Fix)

| Pattern | Example | Fix |
|---------|---------|-----|
| Empty adjectives | "显著提升" | Replace with specific metric: "MAE 降低 12%" |
| Absolute assertions | "显而易见", "必然" | Add qualification: "实验结果表明" |
| Vague quantifiers | "大量研究" | Use numbers: "三项研究 [1-3]" |
| Template openings | "近年来", "随着科技的飞速发展" | Start from specific problem context |
| Stacked citations | "[1]-[5]" without discussion | Discuss each cited work individually |
| Filler connectors | "总之", "不可否认的是", "值得注意的是" | Delete; state conclusion directly |

## AI Density Scoring

| Score | Action |
|-------|--------|
| >70% | Urgent: immediate rewrite |
| 50-70% | High: rewrite soon |
| 30-50% | Medium: review and revise |
| <30% | Low: light polish only |

## Edit Types

1. Delete empty phrases  2. Add specifics  3. Split long sentences  4. Restructure  5. Downgrade certainty  6. Remove redundancy  7. Add missing subjects  8. Replace templates

> Full details: see [`../DEAI_GUIDE.md`](../DEAI_GUIDE.md)
