# Reviewer Perspective Guide

## Table of Contents
- [Four-Dimensional Review Criteria](#four-dimensional-review-criteria)
- [Six-Point Scoring Scale](#six-point-scoring-scale)
- [Reviewer Reading Behavior](#reviewer-reading-behavior)
- [Pre-Submission Checklist](#pre-submission-checklist)
- [Rebuttal Best Practices](#rebuttal-best-practices)

## Four-Dimensional Review Criteria

| Criterion | What Reviewers Look For | Common Deduction Reasons |
|-----------|------------------------|--------------------------|
| **Quality** | Technical soundness, well-supported claims | Flawed proofs, missing baselines, unfair comparisons |
| **Clarity** | Clear writing, reproducible by experts | Ambiguous notation, missing details, poor organization |
| **Significance** | Community impact, advances understanding | Incremental improvement, narrow applicability |
| **Originality** | New insights (doesn't require new method) | Known results, obvious extensions |

## Six-Point Scoring Scale

(NeurIPS scale, widely adopted)

| Score | Rating | Typical Characteristics |
|-------|--------|------------------------|
| 6 | **Strong Accept** | Groundbreaking contribution, technically flawless, very high impact |
| 5 | **Accept** | Technically solid, high impact, well-written |
| 4 | **Borderline Accept** | Solid contribution, limited evaluation or novelty concerns |
| 3 | **Borderline Reject** | Technical merits but weaknesses outweigh strengths |
| 2 | **Reject** | Technical flaws, insufficient evaluation, unclear contribution |
| 1 | **Strong Reject** | Known results, ethical issues, or fundamental errors |

### What Moves Papers from 3→4 (Borderline → Accept):
- [ ] Address obvious weakness proactively (limitations section)
- [ ] Add one more strong baseline or ablation
- [ ] Improve clarity of main contribution statement
- [ ] Add reproducibility details (code, hyperparameters)

## Reviewer Reading Behavior

Understanding how reviewers read helps prioritize your effort:

| Paper Section | % Reviewers Who Read | Time Spent | Implication |
|---------------|---------------------|------------|-------------|
| Abstract | 100% | 2-3 min | Must be perfect |
| Introduction | 90%+ (skimmed) | 3-5 min | Front-load contribution |
| Figures/Tables | Before methods | 2-3 min | Figure 1 is critical |
| Methods | Only if interested | 5-10 min | Don't bury the lede |
| Experiments | If methods seem sound | 5-10 min | Clear claims + evidence |
| Appendix | Rarely (<30%) | As needed | Supplementary only |

**Key Insight**: If your abstract and intro don't hook reviewers, they may never read your methods.

## Pre-Submission Checklist

### Universal Checklist (All Venues)
- [ ] Paper compiles without errors
- [ ] All figures are referenced in text
- [ ] All tables are referenced in text
- [ ] No orphaned citations (every \cite has a bib entry)
- [ ] No placeholder text (TODO, FIXME, XXX)
- [ ] Anonymous submission (no author names in blind review)
- [ ] Page limit respected (excluding references)
- [ ] Consistent notation throughout
- [ ] All acronyms defined on first use
- [ ] Limitations section included

### NeurIPS Specific (16 items)
- [ ] Paper checklist completed (Appendix)
- [ ] Broader Impact Statement included
- [ ] Code submission prepared (if applicable)
- [ ] Lay summary prepared (for accepted papers)
- [ ] Ethics review flagged if applicable
- [ ] Supplementary material ≤ 50MB
- [ ] Main paper ≤ 9 pages (+ unlimited references/appendix)
- [ ] Uses official NeurIPS style file
- [ ] Reproducibility details: random seeds, compute, datasets
- [ ] Error bars included with methodology specified
- [ ] Statistical significance tests where appropriate
- [ ] Dataset licensing and consent documented
- [ ] Potential negative societal impacts discussed
- [ ] Limitations clearly stated
- [ ] Comparison with appropriate baselines
- [ ] Ablation studies for key design choices

## Rebuttal Best Practices

### Dennett's Criticism Method (Adapted for Academic Rebuttals)
1. **Acknowledge**: Re-state the reviewer's concern fairly
2. **Agree**: Find points of agreement
3. **Learn**: Show what you learned from the criticism
4. **Respond**: Then (and only then) address disagreements with evidence

### Rebuttal Structure Template

```
We thank Reviewer [X] for their thoughtful feedback.

**[Concern 1: Brief summary]**

We agree that [acknowledgment]. To address this:
- [Action taken / experiment added / clarification provided]
- [Evidence: "Table X shows..." / "We added Section Y..."]

**[Concern 2: Brief summary]**

[Same structure...]

**Summary of Changes:**
- [Bullet list of all modifications]
```

### Common Rebuttal Mistakes
- ❌ Arguing that the reviewer is wrong
- ❌ Ignoring a concern (address ALL points)
- ❌ Promising future work instead of showing results
- ❌ Being defensive or dismissive
- ✅ Providing concrete evidence (new experiments, tables)
- ✅ Acknowledging valid criticisms
- ✅ Showing actual revisions made
