# De-AI Writing Guide for Typst Academic Papers


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
  - [Results (结果)](#results-结果)
  - [Discussion (讨论)](#discussion-讨论)
  - [Conclusion (结论)](#conclusion-结论)
- [Output Format for De-AI Editing](#output-format-for-de-ai-editing)
- [Change Categories](#change-categories)
- [Typst-Specific Syntax Preservation](#typst-specific-syntax-preservation)
  - [Protected Elements (NEVER Modify)](#protected-elements-never-modify)
  - [Modifiable Elements (Text Only)](#modifiable-elements-text-only)
- [Quick Reference: Common Replacements](#quick-reference-common-replacements)
- [Bibliography](#bibliography)

---

## 目的 (Purpose)

This guide helps reduce AI-generated writing traces while maintaining technical accuracy and Typst syntax integrity.

**Target Mode**: IEEE TOP期刊 (Mode I) - Concise, precise, and restrained

---

## 核心原则 (Core Principles)

### 1. Syntax Fidelity (语法保真优先)
- **NEVER modify**: Typst functions (`#set`, `#show`, `#let`), math environments, citations (`@cite`), labels (`<label>`)
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
| many studies | three recent studies @ref1 @ref2 @ref3 |
| numerous experiments | experiments on X datasets |
| substantial gain | 12% improvement |
| the majority | 78% of cases |
| significantly better | outperforms by p<0.01 |

**Detection Pattern**: Quantifiers without actual numbers or references.

### Category 5: Template Introductions (模板引言)

❌ "Time series forecasting is an important problem with wide applications."
✅ "Time series forecasting is critical for supply chain optimization @ref1, energy management @ref2, and financial planning @ref3."

❌ "Machine learning has revolutionized many fields."
✅ "Machine learning has improved prediction accuracy in healthcare @ref1, manufacturing @ref2, and finance @ref3."

**Detection Pattern**: Broad generalizations that could be in any textbook.

---

## Section-Specific Guidelines

### Abstract (摘要)

**Structure**: Purpose → Method → Key Results (with numbers) → Conclusion

**Common AI Traps**:
- ❌ "We propose a novel approach for..."
- ✅ "We propose an attention-based mechanism for..."

- ❌ "Experimental results show significant improvements."
- ✅ "On dataset X, our method reduces MAE by 12% compared to the baseline."

- ❌ "This work has important implications for..."
- ✅ "This method enables real-time forecasting with <10ms latency."

**Constraints**:
- No generic claims ("novel", "significant", "important") without specifics
- Include concrete numbers for key results
- State specific contributions, not general value

**Example**:
```typst
// ❌ AI-like
This paper proposes a novel deep learning approach for time series
forecasting. The method achieves significant performance improvements
over existing methods. Experimental results demonstrate the effectiveness
of our approach.

// ✅ Human-like
This paper proposes an attention-based mechanism for multivariate time
series forecasting. Our method reduces MAE by 12% on the UCR archive
compared to the Transformer baseline @ref1. Experimental results show that
the attention mechanism improves long-term dependency capture.
```

---

### Introduction (引言)

**Structure**: Importance → Gap → Contribution → Organization

**Common AI Traps**:
- ❌ "Time series forecasting plays an important role in modern society."
- ✅ "Time series forecasting is critical for energy grid optimization @ref1."

- ❌ "However, existing methods have limitations."
- ✅ "However, existing methods fail to capture long-term dependencies in noisy environments @ref2 @ref3."

- ❌ "Our main contributions are as follows:"
- ✅ "This paper makes three contributions:"

**Contribution Statement Rules**:
- Each contribution must be verifiable
- Avoid "novel", "first", "state-of-the-art" without evidence
- State what you did, not how important it is

**Example**:
```typst
// ❌ AI-like
Time series forecasting is very important. Many researchers study this
problem. However, existing methods have some limitations. This paper
proposes a novel method with significant improvements.

// ✅ Human-like
Time series forecasting enables proactive decision-making in energy
management @ref1 and supply chain optimization @ref2. Recent approaches
based on Transformers @ref3 @ref4 show promise but struggle with noisy
data @ref5. This paper proposes a noise-robust attention mechanism that
reduces prediction error by 12% compared to standard Transformers.
```

---

### Related Work (相关工作)

**Structure**: Categorize → Compare → Position

**Common AI Traps**:
- ❌ "Smith et al. proposed a method. It is good."
- ✅ "@smith2020 proposed X, which achieves Y accuracy on dataset Z."

- ❌ "Existing methods can be divided into two types: A and B."
- ✅ "Existing methods follow two paradigms: statistical approaches @ref1 @ref2 @ref3 and deep learning approaches @ref4 @ref5 @ref6."

- ❌ "Our method is different from them."
- ✅ "Unlike @ref1 @ref2, our method incorporates attention mechanisms to..."

**Guidelines**:
- Group by approach/paradigm, not chronologically
- Compare specific technical differences
- State what you do differently
- Avoid vague praise ("excellent", "outstanding")

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

---

### Results (结果)

**Structure**: Main results → Ablation → Analysis

**Common AI Traps**:
- ❌ "Our method performs much better than baselines."
- ✅ "Our method reduces MAE by 12% compared to the best baseline."

- ❌ "The results demonstrate the effectiveness of our method."
- ✅ "@tab:results shows that our method achieves lowest MAE on 4/5 datasets."

- ❌ "We can see from Figure 2 that our method is superior."
- ✅ "@fig:comparison shows that our method maintains accuracy with 50% less training data."

**Guidelines**:
- Report facts and numbers only
- Don't explain why (that's Discussion)
- Avoid interpretive language ("superior", "outperforms" without numbers)
- Let tables/figures speak for themselves

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
- ✅ "This paper proposed an attention-based mechanism that reduces MAE by 12%."

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

```typst
// ============================================================
// DE-AI EDITING (Line X - [Section Name])
// ============================================================
// Original: [AI-like text]
// Revised: [Human-like text]
//
// Changes:
// 1. [Type of change]: [details]
// 2. [Type of change]: [details]
//
// ⚠️ [PENDING VERIFICATION]: [claim needing evidence]
// ============================================================

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

## Typst-Specific Syntax Preservation

### Protected Elements (NEVER Modify)

**1. Function Calls**
```typst
#set text(...)      // NEVER modify
#show heading: ...  // NEVER modify
#let func = ...     // NEVER modify
```

**2. Citations and References**
```typst
@smith2020          // NEVER modify citation keys
<fig:example>       // NEVER modify labels
@fig:example        // NEVER modify cross-references
```

**3. Math Environments**
```typst
$x^2 + y^2 = z^2$   // NEVER modify math content
$ integral x dif x $ // NEVER modify display math
```

**4. Markup Syntax**
```typst
*bold*              // Can modify text, keep markup
_italic_            // Can modify text, keep markup
`code`              // NEVER modify code content
```

### Modifiable Elements (Text Only)

**1. Paragraph Text**
```typst
// ✅ Can modify
This method achieves significant improvements.
→ This method reduces error by 12%.
```

**2. Heading Text**
```typst
// ✅ Can modify text, keep syntax
= Novel Approach for Time Series
→ = Attention-Based Mechanism for Time Series
```

**3. Caption Text**
```typst
// ✅ Can modify text inside caption
#figure(
  ...,
  caption: [This shows significant improvements.]
)
→
#figure(
  ...,
  caption: [This shows 12% error reduction.]
)
```

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
- [TYPST_SYNTAX.md](TYPST_SYNTAX.md): Typst syntax reference
