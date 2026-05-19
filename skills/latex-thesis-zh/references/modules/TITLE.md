# Title Module Reference

Purpose: Optimize Chinese thesis titles and chapter titles per GB/T 7713.1-2006 standards.

## Quality Standards

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Conciseness | 25% | Remove "关于...的研究", "...的探索", "新型", "改进的" |
| Searchability | 30% | Core terms (method + problem) in first 20 chars |
| Length | 15% | Optimal: 15-25 chars; Acceptable: 10-30 chars |
| Specificity | 20% | Concrete method/problem names, avoid vague terms |
| Compliance | 10% | Follow thesis title norms, avoid obscure abbreviations |

## Title Patterns

| Pattern | Example | Use Case |
|---------|---------|----------|
| Method-based | 基于Transformer的时间序列预测方法研究 | Method innovation |
| Domain-oriented | 工业系统故障检测的图神经网络方法 | Application-driven |
| Theory + Application | 时间序列预测的注意力机制及其在工业控制中的应用 | Dual focus |

## Words to Remove

"关于...的研究", "...的探索", "新型", "新颖的", "改进的", "优化的", "基于...的" (can be simplified)

## University-Specific Limits

- **Tsinghua (thuthesis)**: ≤36 Chinese characters, no abbreviations/formulas
- **Peking (pkuthss)**: ≤25 characters, subtitle with dash allowed
- **Generic (ctexbook)**: 15-25 characters recommended

## Bilingual Alignment

- "基于X的Y" → "X-Based Y" or "Y via X"
- English titles use Title Case
- Avoid word-for-word translation

> Full details: see [`../TITLE_OPTIMIZATION.md`](../TITLE_OPTIMIZATION.md)
