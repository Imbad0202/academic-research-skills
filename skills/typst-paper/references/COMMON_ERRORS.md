# Common Chinglish Errors in Academic Writing


## Table of Contents

- [Category 1: Sentence Structure](#category-1-sentence-structure)
  - [1.1 Topic-Prominent Structure](#11-topic-prominent-structure)
  - [1.2 Run-on Sentences](#12-run-on-sentences)
  - [1.3 Missing Articles](#13-missing-articles)
- [Category 2: Word Choice](#category-2-word-choice)
  - [2.1 Weak Verbs](#21-weak-verbs)
  - [2.2 Informal Expressions](#22-informal-expressions)
  - [2.3 Redundant Expressions](#23-redundant-expressions)
- [Category 3: Hedging (避免绝对化)](#category-3-hedging-避免绝对化)
  - [Forbidden Absolute Words](#forbidden-absolute-words)
  - [Academic Hedging](#academic-hedging)
- [Category 4: Tense Usage](#category-4-tense-usage)
  - [Abstract](#abstract)
  - [Introduction](#introduction)
  - [Methods](#methods)
  - [Results](#results)
  - [Discussion](#discussion)
- [Category 5: Common Phrase Errors](#category-5-common-phrase-errors)
  - [Preposition Errors](#preposition-errors)
  - [Collocation Errors](#collocation-errors)
- [Category 6: Chinese-English Translation Patterns](#category-6-chinese-english-translation-patterns)
  - [6.1 Direct Translation Errors](#61-direct-translation-errors)
  - [6.2 Academic Expression Patterns](#62-academic-expression-patterns)
- [Typst-Specific Notes](#typst-specific-notes)
  - [Comment Syntax](#comment-syntax)
  - [Common Typst Errors](#common-typst-errors)

---

## Category 1: Sentence Structure

### 1.1 Topic-Prominent Structure
❌ "This method, its advantage is obvious."
✅ "The advantage of this method is obvious."

### 1.2 Run-on Sentences
❌ "We propose a method it can solve the problem."
✅ "We propose a method that can solve the problem."

### 1.3 Missing Articles
❌ "Deep learning is popular technology."
✅ "Deep learning is a popular technology."

## Category 2: Word Choice

### 2.1 Weak Verbs
| Chinglish | Academic |
|-----------|----------|
| make | construct, generate, produce, create |
| do | perform, conduct, execute, carry out |
| get | obtain, achieve, derive, acquire |
| use | employ, utilize, leverage, adopt |
| show | demonstrate, illustrate, reveal, indicate |
| find | discover, identify, observe, determine |

### 2.2 Informal Expressions
| Avoid | Use Instead |
|-------|-------------|
| a lot of | numerous, substantial, considerable |
| big | significant, substantial, major |
| very | highly, considerably, substantially |
| things | factors, elements, aspects, components |
| good | effective, efficient, optimal, superior |

### 2.3 Redundant Expressions
| Redundant | Concise |
|-----------|---------|
| completely eliminate | eliminate |
| future prospects | prospects |
| past history | history |
| basic fundamentals | fundamentals |
| advance planning | planning |

## Category 3: Hedging (避免绝对化)

### Forbidden Absolute Words
- ❌ "obviously", "clearly", "certainly", "undoubtedly"
- ❌ "always", "never", "all", "none"
- ❌ "prove", "prove that" (unless mathematical proof)

### Academic Hedging
- ✅ "It appears that...", "It seems that..."
- ✅ "The results suggest...", "The data indicate..."
- ✅ "This may be attributed to..."
- ✅ "One possible explanation is..."

## Category 4: Tense Usage

### Abstract
- Present tense for general statements
- Past tense for specific findings

### Introduction
- Present tense for established facts
- Present perfect for recent developments

### Methods
- Past tense (what you did)

### Results
- Past tense for your findings
- Present tense for tables/figures ("Table 1 shows...")

### Discussion
- Present tense for interpretations
- Past tense for referencing results

## Category 5: Common Phrase Errors

### Preposition Errors
| Wrong | Correct |
|-------|---------|
| according with | according to |
| based in | based on |
| compare with (similar) | compare to (similar) |
| different with | different from |
| focus at | focus on |

### Collocation Errors
| Wrong | Correct |
|-------|---------|
| do an experiment | conduct/perform an experiment |
| make a conclusion | draw/reach a conclusion |
| take efforts | make efforts |
| rise a question | raise a question |
| solve problems | address/tackle problems |

## Category 6: Chinese-English Translation Patterns

### 6.1 Direct Translation Errors
| 中文 | ❌ Chinglish | ✅ English |
|------|-------------|-----------|
| 越来越多 | more and more | increasingly |
| 近年来 | in recent years | recently / since 2020 |
| 发挥重要作用 | play an important role | is crucial for / enables |
| 取得了很大进展 | made great progress | has advanced significantly |
| 随着...的发展 | with the development of | as X advances / given advances in |

### 6.2 Academic Expression Patterns
| 中文 | English |
|------|---------|
| 本文提出... | We propose... / This paper presents... |
| 实验结果表明... | Experimental results demonstrate that... |
| 与...相比 | Compared with... / In comparison to... |
| 综上所述 | In summary / In conclusion |
| 值得注意的是 | Notably / It is worth noting that |

## Typst-Specific Notes

### Comment Syntax
```typst
// This is a single-line comment
/* This is a
   multi-line comment */
```

### Common Typst Errors
❌ Using LaTeX syntax: `\cite{}`
✅ Using Typst syntax: `@cite`

❌ Using LaTeX math: `\frac{a}{b}`
✅ Using Typst math: `$a/b$` or `$(a)/(b)$`

❌ Using LaTeX environments: `\begin{figure}`
✅ Using Typst functions: `#figure(...)`
