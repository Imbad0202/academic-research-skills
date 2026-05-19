# De-AI Writing Guide for English Academic Papers


## 目录

- [目的 (Purpose)](#目的-purpose)
- [核心原则 (Core Principles)](#核心原则-core-principles)
  - [1. Syntax Fidelity (语法保真优先)](#1-syntax-fidelity-语法保真优先)
  - [2. Zero Fabrication (零捏造)](#2-zero-fabrication-零捏造)
  - [3. Information Density (提高信息密度)](#3-information-density-提高信息密度)
  - [4. Academic Restraint (克制措辞)](#4-academic-restraint-克制措辞)
- [Common AI Writing Patterns to Remove](#common-ai-writing-patterns-to-remove)
  - [Category 1: Empty Phrases (空话口号)](#category-1-empty-phrases-空话口号)
  - [Category 2: Over-Confident Language (过度确定)](#category-2-over-confident-language-过度确定)
  - [Category 3: Mechanical Structures (机械排比)](#category-3-mechanical-structures-机械排比)
  - [Category 4: Vague Quantification (模糊量化)](#category-4-vague-quantification-模糊量化)
  - [Category 5: Template Introductions (模板引言)](#category-5-template-introductions-模板引言)
- [Section-Specific Guidelines](#section-specific-guidelines)
  - [Abstract (摘要)](#abstract-摘要)
  - [Introduction (引言)](#introduction-引言)
  - [Related Work (相关工作)](#related-work-相关工作)
  - [Methods (方法)](#methods-方法)
  - [Experiments (实验)](#experiments-实验)
  - [Results (结果)](#results-结果)
  - [Discussion (讨论)](#discussion-讨论)
  - [Conclusion (结论)](#conclusion-结论)
- [Output Format for De-AI Editing](#output-format-for-de-ai-editing)
- [Change Categories](#change-categories)
- [Detection Checklist (use with `deai_check.py --analyze`)](#detection-checklist-use-with-deai_checkpy---analyze)
  - [High-Priority AI Traces (Must Fix)](#high-priority-ai-traces-must-fix)
  - [Medium-Priority AI Traces (Should Fix)](#medium-priority-ai-traces-should-fix)
  - [Low-Priority AI Traces (Consider Fixing)](#low-priority-ai-traces-consider-fixing)
- [Section-Wise AI Trace Density Scores](#section-wise-ai-trace-density-scores)
- [Quick Reference: Common Replacements](#quick-reference-common-replacements)
- [Bibliography](#bibliography)

---

## 目的 (Purpose)

This guide helps reduce AI-generated writing traces while maintaining technical accuracy and LaTeX syntax integrity.

**Target Mode**: IEEE TOP期刊 (Mode I) - Concise, precise, and restrained

---

## 核心原则 (Core Principles)

### 1. Syntax Fidelity (语法保真优先)
- **NEVER modify**: LaTeX commands, environments, math, citations, labels
- **ONLY modify**: Visible paragraph text, section titles, caption text
- **Preserve**: All structural integrity for compilation

### 2. Zero Fabrication (零捏造)
- **NEVER add**: New data, metrics, comparisons, experimental settings
- **NEVER add**: New claims, contributions, or conclusions
- **ONLY improve**: Expression clarity and natural flow

### 3. Information Density (提高信息密度)
- Every sentence must convey verifiable information
- Delete empty phrases without substance
- Replace vague claims with specific statements (if available)
- Mark unverifiable claims as [PENDING VERIFICATION]

### 4. Academic Restraint (克制措辞)
- Avoid over-confident language without evidence
- Use appropriate hedging for speculative claims
- Present contributions objectively, not hyperbolically

---

## Common AI Writing Patterns to Remove

### Category 1: Empty Phrases (空话口号)

| ❌ AI-like | ✅ Human-like | Notes |
|-----------|---------------|-------|
| significant improvement | reduces error by X% | Use specific numbers |
| comprehensive analysis | analyzes X, Y, Z | List what was analyzed |
| effective solution | outperforms baseline by X | State comparison metric |
| important contribution | proposes method for X | State the contribution |
| robust performance | maintains accuracy under Y | Specify condition |
| novel approach | extends X by introducing Y | Explain what's new |

**Detection Pattern**: Look for adjectives that can be replaced with measurable claims.

### Category 2: Over-Confident Language (过度确定)

| ❌ Absolute | ✅ Qualified |
|-------------|--------------|
| obviously | the results indicate |
| clearly | evidence suggests |
| necessarily | under these conditions |
| completely | in most cases |
| undoubtedly | appears to be |
| always | consistently in our experiments |
| never | rarely observed |

**Detection Pattern**: Absolute claims without qualification or evidence.

### Category 3: Mechanical Structures (机械排比)

**Three-part parallelisms without substance**:
❌ "Our method is **fast**, **accurate**, and **efficient**."
✅ "Our method processes 1000 samples/sec with 95% accuracy."

**Template transitions**:
❌ "In recent years, deep learning has developed rapidly."
✅ "Deep learning has achieved state-of-the-art performance in X since 2020."

**Generic openings**:
❌ "With the rapid development of technology..."
✅ Start directly with the specific problem context.

**Detection Pattern**: Phrases that could apply to any paper in any field.

### Category 4: Vague Quantification (模糊量化)

| ❌ Vague | ✅ Specific |
|----------|------------|
| many studies | three recent studies [1-3] |
| numerous experiments | experiments on X datasets |
| substantial gain | 12% improvement |
| the majority | 78% of cases |
| significantly better | outperforms by p<0.01 |

**Detection Pattern**: Quantifiers without actual numbers or references.

### Category 5: Template Introductions (模板引言)

❌ "Time series forecasting is an important problem with wide applications."
✅ "Time series forecasting is critical for supply chain optimization [1], energy management [2], and financial planning [3]."

❌ "Machine learning has revolutionized many fields."
✅ "Machine learning has improved prediction accuracy in healthcare [1], manufacturing [2], and finance [3]."

**Detection Pattern**: Broad generalizations that could be in any textbook.

---

## Section-Specific Guidelines

### Abstract (摘要)

**Structure**: Purpose → Method → Key Results (with numbers) → Conclusion

**Common AI Traps**:
- ❌ "We propose a novel approach for..."
- ✅ "We propose an attention-based mechanism for..."

- ❌ "Experimental results show significant improvements."
- ✅ "On dataset X, our method reduces MAE by 12\% compared to the baseline."

- ❌ "This work has important implications for..."
- ✅ "This method enables real-time forecasting with <10ms latency."

**Constraints**:
- No generic claims ("novel", "significant", "important") without specifics
- Include concrete numbers for key results
- State specific contributions, not general value

**Example**:
```latex
% ❌ AI-like
This paper proposes a novel deep learning approach for time series
forecasting. The method achieves significant performance improvements
over existing methods. Experimental results demonstrate the effectiveness
of our approach.

% ✅ Human-like
This paper proposes an attention-based mechanism for multivariate time
series forecasting. Our method reduces MAE by 12\% on the UCR archive
compared to the Transformer baseline [1]. Experimental results show that
the attention mechanism improves long-term dependency capture.
```

---

### Introduction (引言)

**Structure**: Importance → Gap → Contribution → Organization

**Common AI Traps**:
- ❌ "Time series forecasting plays an important role in modern society."
- ✅ "Time series forecasting is critical for energy grid optimization [1]."

- ❌ "However, existing methods have limitations."
- ✅ "However, existing methods fail to capture long-term dependencies in noisy environments [2, 3]."

- ❌ "Our main contributions are as follows:"
- ✅ "This paper makes three contributions:"

**Contribution Statement Rules**:
- Each contribution must be verifiable
- Avoid "novel", "first", "state-of-the-art" without evidence
- State what you did, not how important it is

**Example**:
```latex
% ❌ AI-like
Time series forecasting is very important. Many researchers study this
problem. However, existing methods have some limitations. This paper
proposes a novel method with significant improvements.

% ✅ Human-like
Time series forecasting enables proactive decision-making in energy
management [1] and supply chain optimization [2]. Recent approaches
based on Transformers [3, 4] show promise but struggle with noisy
data [5]. This paper proposes a noise-robust attention mechanism that
reduces prediction error by 12\% compared to standard Transformers.
```

---

### Related Work (相关工作)

**Structure**: Categorize → Compare → Position

**Common AI Traps**:
- ❌ "Smith et al. proposed a method. It is good."
- ✅ "Smith et al. [1] proposed X, which achieves Y accuracy on dataset Z."

- ❌ "Existing methods can be divided into two types: A and B."
- ✅ "Existing methods follow two paradigms: statistical approaches [1-3] and deep learning approaches [4-6]."

- ❌ "Our method is different from them."
- ✅ "Unlike [1, 2], our method incorporates attention mechanisms to..."

**Guidelines**:
- Group by approach/paradigm, not chronologically
- Compare specific technical differences
- State what you do differently
- Avoid vague praise ("excellent", "outstanding")

**Example**:
```latex
% ❌ AI-like
Many people have studied time series forecasting. Some use statistics,
others use deep learning. Smith proposed a good method. Jones also
proposed a method. Our method is better than theirs.

% ✅ Human-like
Time series forecasting methods fall into two categories: statistical
models [1-3] and deep learning approaches [4-6]. Smith et al. [1]
proposed ARIMA, which assumes linear relationships. Recent Transformer-based
methods [4, 5] capture non-linear patterns but require large datasets.
Unlike [4, 5], our method uses a hybrid architecture that maintains
accuracy with limited data.
```

---

### Methods (方法)

**Structure**: Overview → Details → Algorithm → Complexity

**Common AI Traps**:
- ❌ "We use a neural network. It is very powerful."
- ✅ "We use a 3-layer LSTM with 256 hidden units."

- ❌ "The algorithm works well."
- ✅ "The algorithm converges within 100 epochs."

- ❌ "The model has good performance."
- ✅ "The model processes 1000 samples/second."

**Guidelines**:
- Provide implementation details for reproducibility
- State hyperparameters and architecture choices
- Include algorithm complexity if relevant
- Focus on what you did, not how well it works (that's Results)

**Example**:
```latex
% ❌ AI-like
We use a deep learning model. The model has many layers and learns
features automatically. We train the model with gradient descent.

% ✅ Human-like
We use a 4-layer Transformer with 8 attention heads (Section 3.1).
The model is trained using Adam optimizer with learning rate 0.001
and batch size 32 (Section 3.2). Training converges in 50 epochs
on a single NVIDIA V100 GPU.
```

---

### Experiments (实验)

**Structure**: Setup → Datasets → Metrics → Baselines

**Common AI Traps**:
- ❌ "We conducted extensive experiments."
- ✅ "We evaluated on 5 datasets from UCR archive."

- ❌ "We compared with many methods."
- ✅ "We compared with 4 baselines: ARIMA [1], LSTM [2], Transformer [3], and Informer [4]."

- ❌ "The experimental setup is reasonable."
- ✅ "We use 70%/15%/15% train/validation/test split."

**Guidelines**:
- State what you actually did
- List specific datasets and baselines
- Describe evaluation metrics
- Avoid subjective assessments ("reasonable", "comprehensive")

---

### Results (结果)

**Structure**: Main results → Ablation → Analysis

**Common AI Traps**:
- ❌ "Our method performs much better than baselines."
- ✅ "Our method reduces MAE by 12\% compared to the best baseline."

- ❌ "The results demonstrate the effectiveness of our method."
- ✅ "Table 1 shows that our method achieves lowest MAE on 4/5 datasets."

- ❌ "We can see from Figure 2 that our method is superior."
- ✅ "Figure 2 shows that our method maintains accuracy with 50% less training data."

**Guidelines**:
- Report facts and numbers only
- Don't explain why (that's Discussion)
- Avoid interpretive language ("superior", "outperforms" without numbers)
- Let tables/figures speak for themselves

**Example**:
```latex
% ❌ AI-like
The experimental results are shown in Table 1. Our method performs
the best. The baseline methods are not as good as ours. From the
results we can see that our method is very effective.

% ✅ Human-like
Table 1 reports MAE for all methods on 5 datasets. Our method
achieves the lowest MAE on 4 datasets (Electricity, Traffic, Solar,
Exchange). Compared to the best baseline (Transformer), our method
reduces MAE by 12\% on average.
```

---

### Discussion (讨论)

**Structure**: Interpretation → Mechanism → Limitations → Future Work

**Common AI Traps**:
- ❌ "The good performance proves our method is excellent."
- ✅ "The improved accuracy suggests that attention mechanisms capture long-term dependencies."

- ❌ "Our method has no limitations."
- ✅ "Our method requires more training time (2.3 hours vs 1.5 hours for baselines)."

- ❌ "Future work includes more experiments."
- ✅ "Future work will explore the attention mechanism's interpretability."

**Guidelines**:
- Explain mechanisms, not just outcomes
- Acknowledge failures and boundary conditions
- State limitations honestly
- Propose specific future work

---

### Conclusion (结论)

**Structure**: Summary → Answer research question → Future work

**Common AI Traps**:
- ❌ "In this paper, we proposed a novel method that achieved significant improvements."
- ✅ "This paper proposed an attention-based mechanism that reduces MAE by 12\%."

- ❌ "Our work has important theoretical and practical value."
- ✅ "This work enables real-time forecasting with limited computational resources."

- ❌ "In the future, we will continue to improve our method."
- ✅ "Future work will extend this method to multivariate time series with missing data."

**Guidelines**:
- Answer the research question directly
- No new results or claims
- No new experiments
- Specific, actionable future work

---

## Output Format for De-AI Editing

```latex
% ============================================================
% DE-AI EDITING (Line X - [Section Name])
% ============================================================
% Original: [AI-like text]
% Revised: [Human-like text]
%
% Changes:
% 1. [Type of change]: [details]
% 2. [Type of change]: [details]
%
% ⚠️ [PENDING VERIFICATION]: [claim needing evidence]
% ============================================================

[revised source code]
```

## Change Categories

1. **Removed empty phrase**: Deleted vague adjective/adverb
2. **Added specificity**: Replaced vague with concrete
3. **Split long sentence**: Divided sentence >50 words
4. **Reordered structure**: Improved logical flow
5. **Downgraded claim**: Added appropriate hedging
6. **Deleted redundancy**: Removed repetitive content
7. **Added subject**: Inserted missing grammatical subject
8. **Fixed template expression**: Replaced generic with specific

---

## Detection Checklist (use with `deai_check.py --analyze`)

### High-Priority AI Traces (Must Fix)
- [ ] Adjectives without specifics: significant, comprehensive, effective, important
- [ ] Absolute claims: obviously, clearly, necessarily, completely
- [ ] Vague quantifiers: many, numerous, substantial, majority
- [ ] Template phrases: in recent years, more and more, play an important role

### Medium-Priority AI Traces (Should Fix)
- [ ] Mechanical parallelisms without substance
- [ ] Generic openings that apply to any paper
- [ ] Over-confident predictions or claims
- [ ] Three-part lists without specific content

### Low-Priority AI Traces (Consider Fixing)
- [ ] Repetitive sentence structures
- [ ] Over-use of transition words
- [ ] Passive voice where active is clearer

---

## Section-Wise AI Trace Density Scores

After running `deai_check.py --analyze`, prioritize sections with:

| Score | Action |
|-------|--------|
| >70% | Critical: Rewrite immediately |
| 50-70% | High: Rewrite soon |
| 30-50% | Medium: Review and revise |
| <30% | Low: Minor polish only |

---

## Quick Reference: Common Replacements

| ❌ Remove | ✅ Replace With |
|-----------|-----------------|
| significant improvement | [specific metric + number] |
| comprehensive study | analyze X, Y, Z |
| effective solution | outperforms baseline by X% |
| novel approach | extends X by introducing Y |
| robust performance | maintains accuracy under [condition] |
| clearly/obviously | evidence suggests / results indicate |
| many studies | [number] studies [citations] |
| in recent years | since [year] / in [specific period] |
| more and more | increasingly / growing from X to Y |
| play an important role | enables / is critical for / is essential to |

---

## Bibliography

This guide should be used together with:
- [STYLE_GUIDE.md](STYLE_GUIDE.md): General academic writing rules
- [COMMON_ERRORS.md](COMMON_ERRORS.md): Chinglish patterns to avoid
- [VENUES.md](VENUES.md): Venue-specific requirements
