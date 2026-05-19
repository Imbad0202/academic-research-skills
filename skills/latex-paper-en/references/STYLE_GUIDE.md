# Academic Writing Style Guide


## Table of Contents

- [Core Principles](#core-principles)
  - [1. Clarity Over Complexity](#1-clarity-over-complexity)
  - [2. Precision Over Vagueness](#2-precision-over-vagueness)
  - [3. Active Voice (When Appropriate)](#3-active-voice-when-appropriate)
- [Sentence Length Guidelines](#sentence-length-guidelines)
- [Paragraph Structure](#paragraph-structure)
  - [Topic Sentence](#topic-sentence)
  - [Supporting Sentences](#supporting-sentences)
  - [Transition](#transition)
- [Academic Vocabulary](#academic-vocabulary)
  - [Reporting Verbs (Neutral)](#reporting-verbs-neutral)
  - [Reporting Verbs (Strong Agreement)](#reporting-verbs-strong-agreement)
  - [Reporting Verbs (Tentative)](#reporting-verbs-tentative)
  - [Reporting Verbs (Critical)](#reporting-verbs-critical)
- [Transition Words](#transition-words)
  - [Addition](#addition)
  - [Contrast](#contrast)
  - [Cause/Effect](#causeeffect)
  - [Example](#example)
  - [Sequence](#sequence)
- [Citation Integration](#citation-integration)
  - [Integral (Author as Subject)](#integral-author-as-subject)
  - [Non-Integral (Content Focus)](#non-integral-content-focus)
  - [Paraphrase (Preferred)](#paraphrase-preferred)
  - [Direct Quote (Sparingly)](#direct-quote-sparingly)
- [Common Section Patterns](#common-section-patterns)
  - [Introduction](#introduction)
  - [Related Work](#related-work)
  - [Methodology](#methodology)
  - [Results](#results)
  - [Conclusion](#conclusion)

---

## Core Principles

### 1. Clarity Over Complexity
- One idea per sentence
- Avoid nested clauses when possible
- Define terms on first use

### 2. Precision Over Vagueness
- Use specific numbers instead of "several" or "many"
- Quantify claims whenever possible
- Avoid hedging without evidence

### 3. Active Voice (When Appropriate)
- ✅ "We propose a novel method..."
- ✅ "This paper presents..."
- ❌ "A novel method is proposed by us..."

## Sentence Length Guidelines

| Type | Word Count | Use Case |
|------|------------|----------|
| Short | 10-15 | Key findings, transitions |
| Medium | 15-25 | Most content |
| Long | 25-40 | Complex relationships |
| Very Long | >40 | ⚠️ Consider splitting |

## Paragraph Structure

### Topic Sentence
First sentence states the main point.

### Supporting Sentences
- Evidence, examples, or elaboration
- 3-5 sentences typical
- Clear logical flow

### Transition
Connect to next paragraph if needed.

## Academic Vocabulary

### Reporting Verbs (Neutral)
- states, notes, observes, reports, describes

### Reporting Verbs (Strong Agreement)
- demonstrates, shows, proves, confirms, establishes

### Reporting Verbs (Tentative)
- suggests, implies, indicates, proposes, hypothesizes

### Reporting Verbs (Critical)
- claims, argues, asserts, alleges, maintains

## Transition Words

### Addition
- Furthermore, Moreover, Additionally, In addition

### Contrast
- However, Nevertheless, Conversely, On the other hand

### Cause/Effect
- Therefore, Consequently, As a result, Thus

### Example
- For instance, For example, Specifically, In particular

### Sequence
- First, Second, Subsequently, Finally

## Citation Integration

### Integral (Author as Subject)
"Smith et al. [1] demonstrated that..."

### Non-Integral (Content Focus)
"Deep learning has shown remarkable success [1-3]."

### Paraphrase (Preferred)
Restate the idea in your own words with citation.

### Direct Quote (Sparingly)
Only for definitions or exceptionally well-phrased ideas.

### Anti-Citation-Stacking Rules (Introduction & Related Work)

Stacking 3+ references without individual discussion is a common AI writing pattern and is unacceptable in top-tier venues. These rules apply to both Introduction and Related Work sections.

**Rules:**
1. **Max 2 clustered citations** without discussion per sentence
   - ❌ "Many methods have been proposed [1], [2], [3], [4], [5]."
   - ✅ "Smith et al. [1] proposed X for scenario A. Building on this, Jones [2] extended the approach to B, while Wang et al. [3] addressed limitation C."

2. **Every cited work must earn its citation** with at least one of:
   - A summary of its core contribution (1 clause minimum)
   - A comparison with another cited work
   - A specific limitation that motivates your work

3. **Narrative over parenthetical** in Introduction and Related Work body:
   - Use integral citations (author as subject) for key works: "Smith et al. [1] demonstrated..."
   - Reserve non-integral citations (content focus) for well-established facts only: "Gradient descent is widely used [1], [2]."

4. **Funnel-appropriate density (Introduction):**
   - Background paragraph (broad context): up to 2 clustered citations for established facts
   - Problem statement paragraph: each citation must be individually discussed
   - Gap/motivation paragraph: every cited limitation must reference a specific paper

5. **Categorical discussion (Related Work):**
   - Group works by methodology/approach, not chronologically
   - Within each group, discuss each work's specific contribution and limitation
   - Use comparative language between works: "Unlike [1], method [2] addresses..."

**Positive patterns (Introduction):**
```latex
Smith et al. [1] proposed method X, achieving Y% accuracy on dataset Z.
However, their approach assumes A, which limits applicability to B.
Jones [2] relaxed this assumption by introducing C, but at the cost of D.
In contrast, our method addresses both limitations by...
```

**Positive patterns (Related Work):**
```latex
\textbf{Transformer-based methods.} Vaswani et al. [1] introduced the
self-attention mechanism for sequence modeling. Li et al. [2] adapted this
architecture for time series, but their method requires O(n^2) memory.
Zhou et al. [3] proposed ProbSparse attention to reduce complexity to O(n log n),
though at the cost of approximation error.
```

**Negative patterns (FORBIDDEN):**
```latex
Many researchers have studied this problem [1], [2], [3], [4], [5].
Several methods have been proposed [6], [7], [8], [9], [10], [11], [12].
Recent advances include [13], [14], [15], [16], [17], [18], [19], [20].
```

## Common Section Patterns

### Introduction
1. General context → Specific problem
2. Gap in existing work
3. Contributions of this work
4. Paper organization

### Related Work
1. Categorize existing approaches
2. Compare and contrast
3. Position your work

### Methodology
1. Overview of approach
2. Detailed steps
3. Justification for choices

### Results
1. Experimental setup
2. Quantitative results
3. Qualitative analysis
4. Comparison with baselines

### Conclusion
1. Summary of contributions
2. Limitations
3. Future work
