# Figure and Table Caption Generation Guide

When the user requests to generate or optimize a figure or table caption, follow these guidelines strictly to ensure compliance with top-tier publication standards (e.g., NeurIPS, ICLR, ICML).

## 1. Title/Sentence Case Rules

- If the output is a **noun phrase (名词性短语)**: Use **Title Case** (capitalize the first letter of all major words, no period at the end).
- If the output is a **complete sentence (完整句子)**: Use **Sentence case** (capitalize only the first letter of the first word and proper nouns, MUST end with a period).

## 2. Writing Style & Minimalism

- **Direct approach**: Eliminate redundant prefixes like "The figure shows" or "This diagram illustrates". Start directly describing the content (e.g., "Architecture of...", "Performance comparison of...", "Visualization of...").
- **Tables**: Use standard expressions like "Comparison with", "Ablation study on", or "Results on". Avoid flowery words like "showcase" or "depict"—instead use "show", "compare", or "present".
- **Remove "AI flavor"**: Keep the vocabulary precise and simple. Avoid overcomplicated or obscure words.

## 3. Formatting & Output Restrictions

- **Output pure text**: Do NOT prepend "Figure 1:" or "Table 1:". Output only the title text itself.
- **LaTeX compatibility**:
  - MUST escape special characters (e.g., `%`, `_`, `&`).
  - Preserve math formulas exactly as they are (keep the `$` symbols).
- Output the English text only. Do not output any extra dialog or explanations unless the user asks.

## 4. Execution Example

**User Input:** 
"帮我写一段表达：本表展示了我们在ImageNet数据集上的消融实验结果，主要对比了不同深度下的精度。"

**Agent Response:**
```latex
% Caption [Severity: Minor] [Priority: P2]: Translated and optimized caption
% Original: 本表展示了我们在ImageNet数据集上的消融实验结果，主要对比了不同深度下的精度。
% Revised: Ablation study on the ImageNet dataset comparing accuracies at different depths.
```
