# Consistency Module Reference

Purpose: Check terminology, abbreviation, and notation uniformity across thesis chapters.

## Terminology Consistency Rules

1. **First-use definition**: Every technical term must be defined on first use, with the English equivalent in parentheses if applicable
2. **Consistent naming**: Once a term is introduced (e.g., "注意力机制"), use the same form throughout — do not alternate with synonyms ("注意力方法", "Attention 机制") without reason
3. **Cross-chapter alignment**: Terms defined in Chapter 1 must use the same form in all subsequent chapters

## Abbreviation Rules

1. **First-use expansion**: Write the full form first, followed by abbreviation in parentheses: "长短期记忆网络（LSTM）"
2. **Subsequent uses**: Use abbreviation only after it has been introduced
3. **Per-chapter re-introduction**: For theses, re-introduce abbreviations at first use in each chapter (reader may start from any chapter)
4. **Avoid in titles**: Do not use abbreviations in chapter/section titles unless universally known (AI, CNN, LSTM)

## Notation Uniformity

- **Variables**: Use consistent math notation (e.g., always bold for vectors, italic for scalars)
- **Subscripts/superscripts**: Maintain consistent conventions across all equations
- **Units**: Use SI units consistently; do not mix units for the same quantity

## Common Issues

| Issue | Example | Fix |
|-------|---------|-----|
| Synonym drift | "模型"/"网络"/"架构" used interchangeably | Pick one primary term |
| Undefined abbreviation | "使用 GAN 生成" without prior definition | Add first-use expansion |
| Inconsistent translation | "Transformer"/"转换器" mixed | Standardize on one form |
| Notation conflict | $x$ as both input and output in different sections | Assign unique symbols |

## Detection Approach

Script `check_consistency.py --terms` scans for:
- Abbreviations used before definition
- Terms with multiple surface forms
- Inconsistent capitalization of technical terms

> For logic and coherence checks (non-terminology), see [`LOGIC.md`](LOGIC.md). Full reference: [`../LOGIC_COHERENCE.md`](../LOGIC_COHERENCE.md)
