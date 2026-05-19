# Logic Module Reference

Purpose: Check logical coherence, introduction funnel, heading lead-ins, literature review quality, chapter mainline, and cross-section closure.

## AXES Model (Paragraph-Level Coherence)

| Component | Role | Example |
|-----------|------|---------|
| **A**ssertion | Clear topic sentence | "注意力机制能够提升序列建模效果。" |
| **X**ample | Supporting evidence/data | "实验中，注意力机制达到95%准确率。" |
| **E**xplanation | Why evidence supports claim | "这一提升源于其捕获长程依赖的能力。" |
| **S**ignificance | Connection to broader argument | "这一发现为本文架构设计提供了依据。" |

## Heading Lead-In Check (S1)

**Rule**: Every chapter, section, subsection, and content-bearing subsubsection must have a lead-in paragraph before any list, figure, table, formula, or child heading.

**Lead-in minimum**: State what will be discussed, why here, connection to previous content, and preview of internal structure.

**Detection**: Script scans `\chapter`, `\section`, `\subsection`, `\subsubsection`, `\paragraph` — flags if first child is non-prose content.

## Literature Review Quality (A1-A4)

| Check | Rule | Detection |
|-------|------|-----------|
| A1: Topic clustering | Organize by theme, not author/year listing | Script: regex for 3+ consecutive "Author(Year) proposed..." |
| A2: Critical analysis | Each topic group needs evaluative commentary | LLM judgment required |
| A3: Gap derivation | Last paragraph must identify research gap | Script: keyword scan in final 10 lines |
| A4: Funnel citation density | Citations should narrow from broad to specific | LLM judgment required |

## Cross-Section Closure (C3)

**Rule**: Contribution claims in introduction must be echoed in conclusion.

**Detection**: Script extracts contribution keywords from `introduction`, checks for response keywords ("验证了", "证明了", "实验表明") in `conclusion`. Missing echo → Major/P1.

## Transition Signals

| Relation | Chinese | English |
|----------|---------|---------|
| Addition | 此外、进一步 | furthermore, moreover |
| Contrast | 然而、但是 | however, nevertheless |
| Causation | 因此、由此可见 | therefore, consequently |
| Sequence | 首先、随后 | first, subsequently |

> Full details: see [`../LOGIC_COHERENCE.md`](../LOGIC_COHERENCE.md)
