# Abstract Structure Guide

An effective academic abstract contains five structural elements that together tell a complete research story. This guide defines each element, how to detect it, and what makes it strong or weak.

## Five-Element Model

### 1. Background

**Purpose**: Establish the research context — the real-world problem, knowledge gap, or motivation.

**Detection markers (EN)**: "however", "remains unclear", "limited research", "growing interest", "challenge", "gap", "despite", "little is known", "increasingly important"

**Detection markers (ZH)**: "然而", "尚不清楚", "研究不足", "日益增长", "挑战", "空白", "尽管", "鲜有研究"

**Quality criteria**: Moves from broad context to specific gap in 1-2 sentences. A vague background restates the field name without identifying a gap.

### 2. Objective

**Purpose**: State what this specific study aims to answer or accomplish.

**Detection markers (EN)**: "this study aims", "we investigate", "the purpose of", "this paper presents", "we propose", "our goal", "in this work", "we address", "this research examines"

**Detection markers (ZH)**: "本文旨在", "本研究探讨", "本文提出", "研究目的", "为此我们", "本工作", "本文研究"

**Quality criteria**: Specific and falsifiable. A vague objective says "we study X" without specifying what aspect or what question about X.

### 3. Methods

**Purpose**: Describe the approach, data, tools, or analytical framework used.

**Detection markers (EN)**: "we propose", "using", "dataset", "participants", "method", "approach", "framework", "model", "algorithm", "collected", "trained", "evaluated", "sample", "experiment"

**Detection markers (ZH)**: "采用", "方法", "数据集", "样本", "模型", "算法", "框架", "实验", "训练", "评估"

**Quality criteria**: Names the specific technique, data source, or experimental setup. Missing methods make the abstract feel like an opinion piece.

### 4. Results

**Purpose**: Report the key findings with concrete data.

**Detection markers (EN)**: "results show", "achieved", "outperforms", "accuracy", "improved", "reduced", "found that", "demonstrates", "significant", numbers, percentages, p-values

**Detection markers (ZH)**: "结果表明", "达到", "优于", "准确率", "提高", "降低", "发现", "显著", numbers

**Quality criteria**: Must contain at least one quantitative finding (number, percentage, ratio, or comparative statement with magnitude). A results section without numbers is classified as VAGUE.

### 5. Conclusion / Significance

**Purpose**: State the contribution, implications, or practical value of the findings.

**Detection markers (EN)**: "our findings suggest", "contributes to", "implications", "demonstrates that", "can be used", "enables", "provides", "advances", "potential"

**Detection markers (ZH)**: "研究发现表明", "为...提供", "有助于", "具有...意义", "可用于", "推动", "贡献"

**Quality criteria**: Goes beyond restating results — connects findings to the broader field or practice. A hollow conclusion just repeats the results in different words.

## Common Defect Patterns

| Defect | Description | Typical fix |
|--------|-------------|-------------|
| Missing background | Jumps straight to "We propose..." | Add 1 sentence on the problem context |
| Vague objective | "We study deep learning for NLP" | Specify: "We investigate whether... improves..." |
| No methods | Describes results without explaining how | Add the core technique and data source |
| Data-free results | "Our method performs well" | Add a key metric: "achieves 94.2% F1" |
| Echo conclusion | Restates results verbatim | Add implication: "enabling real-time..." |

## Word Count Guidelines

| Context | Language | Range |
|---------|----------|-------|
| Default (no venue specified) | English | 150–250 words |
| Default (no venue specified) | Chinese | 200–300 characters |
| IEEE conference | English | 150–200 words |
| ACM conference | English | 150–250 words |
| NeurIPS/ICML | English | ≤ 200 words (strict) |
| Chinese thesis (GB/T) | Chinese | 300–500 characters |

Venue-specific limits override defaults. Check VENUES.md for exact requirements.

## Diagnostic Output Format

The analyzer outputs a per-element diagnosis:

```
Background:  ✅ PRESENT  — "Despite growing interest in X, the impact of Y remains unclear."
Objective:   ⚠️ VAGUE    — "This paper studies X." → Suggestion: specify the research question
Methods:     ✅ PRESENT  — "We propose a framework based on Z, evaluated on dataset W."
Results:     ❌ MISSING  — No quantitative findings detected → Add key metrics
Conclusion:  ⚠️ VAGUE    — Restates results without implications → Add practical significance
```

## Constraints

- Never alter the author's core claims or fabricate data
- Never add results or conclusions not present in the original text
- Preserve all citations, labels, and math environments
- Mark all modifications with brackets: [ADDED: ...] or [REVISED: ...]
