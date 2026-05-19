# Academic Writing Style Guide (Typst)


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
- [Citation Integration (Typst Syntax)](#citation-integration-typst-syntax)
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
- [Typst-Specific Formatting](#typst-specific-formatting)
  - [Headings](#headings)
  - [Emphasis](#emphasis)
  - [Lists](#lists)
  - [Math](#math)
  - [Figures and Tables](#figures-and-tables)
  - [Cross-references](#cross-references)

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

## Citation Integration (Typst Syntax)

### Integral (Author as Subject)
```typst
@smith2020 demonstrated that...
According to @jones2021, the method...
```

### Non-Integral (Content Focus)
```typst
Deep learning has shown remarkable success @smith2020 @jones2021 @wang2022.
```

### Paraphrase (Preferred)
Restate the idea in your own words with citation.

### Direct Quote (Sparingly)
Only for definitions or exceptionally well-phrased ideas.

### Anti-Citation-Stacking Rules (Introduction & Related Work)

Stacking 3+ references without individual discussion is a common AI writing pattern and is unacceptable in top-tier venues. These rules apply to both Introduction and Related Work sections.

**Rules:**
1. **Max 2 clustered citations** without discussion per sentence
   - ❌ "Many methods have been proposed @smith2020 @jones2021 @wang2022 @li2023 @chen2024."
   - ✅ "@smith2020 proposed X for scenario A. Building on this, @jones2021 extended the approach to B, while @wang2022 addressed limitation C."

2. **Every cited work must earn its citation** with at least one of:
   - A summary of its core contribution (1 clause minimum)
   - A comparison with another cited work
   - A specific limitation that motivates your work

3. **Narrative over parenthetical** in Introduction and Related Work:
   - Use integral citations (author as subject) for key works: "@smith2020 demonstrated..."
   - Reserve non-integral citations for well-established facts only: "Gradient descent is widely used @smith2020 @jones2021."

4. **Funnel-appropriate density (Introduction):**
   - Background paragraph (broad context): up to 2 clustered citations for established facts
   - Problem statement paragraph: each citation must be individually discussed
   - Gap/motivation paragraph: every cited limitation must reference a specific paper

5. **Categorical discussion (Related Work):**
   - Group works by methodology/approach, not chronologically
   - Within each group, discuss each work's specific contribution and limitation
   - Use comparative language between works: "Unlike @smith2020, @jones2021 addresses..."

**Positive patterns (Introduction):**
```typst
@smith2020 proposed method X, achieving Y% accuracy on dataset Z.
However, their approach assumes A, which limits applicability to B.
@jones2021 relaxed this assumption by introducing C, but at the cost of D.
In contrast, our method addresses both limitations by...
```

**Positive patterns (Related Work):**
```typst
*Transformer-based methods.* @vaswani2017 introduced the self-attention
mechanism for sequence modeling. @li2019 adapted this architecture for
time series, but their method requires $O(n^2)$ memory. @zhou2021 proposed
ProbSparse attention to reduce complexity to $O(n log n)$, though at the
cost of approximation error.
```

**Negative patterns (FORBIDDEN):**
```typst
Many researchers have studied this problem @a2020 @b2021 @c2022 @d2023 @e2024.
Several methods have been proposed @f2020 @g2021 @h2022 @i2023 @j2024 @k2024.
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

## Typst-Specific Formatting

### Headings
```typst
= Introduction          // Level 1
== Background          // Level 2
=== Related Work       // Level 3
```

### Emphasis
```typst
*bold text*            // Bold
_italic text_          // Italic
`code text`            // Code/monospace
```

### Lists
```typst
// Unordered list
- Item 1
- Item 2
  - Nested item

// Ordered list
+ First item
+ Second item
  + Nested item
```

### Math
```typst
// Inline math
The equation $x^2 + y^2 = z^2$ shows...

// Display math
$ x^2 + y^2 = z^2 $

// Numbered equation
$ x = (a + b) / 2 $ <eq:mean>
```

### Figures and Tables
```typst
// Figure
#figure(
  image("figure.png", width: 80%),
  caption: [Description of the figure.]
) <fig:example>

// Table
#figure(
  table(
    columns: 3,
    [Header 1], [Header 2], [Header 3],
    [Data 1], [Data 2], [Data 3],
  ),
  caption: [Description of the table.]
) <tab:example>
```

### Cross-references
```typst
As shown in @fig:example, the method...
Table @tab:example presents the results...
Equation @eq:mean defines the average...
```
