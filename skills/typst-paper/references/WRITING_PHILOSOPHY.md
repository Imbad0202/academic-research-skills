# Writing Philosophy for Academic Papers

> "A paper is a short, rigorous, evidence-based technical story with a takeaway readers care about." — Neel Nanda

## Table of Contents
- [The Narrative Principle](#the-narrative-principle)
- [5-Sentence Abstract Formula](#5-sentence-abstract-formula)
- [Gopen-Swan 7 Principles](#gopen-swan-7-principles)
- [Word Choice](#word-choice)
- [Precision Over Brevity](#precision-over-brevity)
- [Micro-Level Tips](#micro-level-tips)
- [Section-by-Section Guide](#section-by-section-guide)
- [Time Allocation](#time-allocation)

## The Narrative Principle

(Neel Nanda, Google DeepMind)

Your paper is NOT a collection of experiments — it's a story with ONE clear contribution.

**Three Pillars** (must be crystal clear by end of introduction):

| Pillar | Description | Example |
|--------|-------------|---------|
| **The What** | 1-3 specific novel claims within cohesive theme | "We prove that X achieves Y under condition Z" |
| **The Why** | Rigorous empirical evidence supporting claims | Strong baselines, experiments distinguishing hypotheses |
| **The So What** | Why readers should care | Connection to recognized community problems |

**If you cannot state your contribution in one sentence, you don't yet have a paper.**

## 5-Sentence Abstract Formula

(Sebastian Farquhar, DeepMind)

1. What you achieved: "We introduce...", "We prove...", "We demonstrate..."
2. Why this is hard and important
3. How you do it (with specialist keywords for discoverability)
4. What evidence you have
5. Your most remarkable number/result

**Delete** generic openings like "Large language models have achieved remarkable success..."

## Gopen-Swan 7 Principles

(Based on "The Science of Scientific Writing")

| # | Principle | Rule | Example |
|---|-----------|------|---------|
| 1 | **Subject-verb proximity** | Keep subject and verb close | ❌ "The model, which was trained on..., achieves" → ✅ "The model achieves... after training on..." |
| 2 | **Stress position** | Place emphasis at sentence ends | ❌ "Accuracy improves by 15% when using attention" → ✅ "When using attention, accuracy improves by **15%**" |
| 3 | **Topic position** | Put context first, new info after | ✅ "Given these constraints, we propose..." |
| 4 | **Old before new** | Familiar info → unfamiliar info | Link backward, then introduce new |
| 5 | **One unit, one function** | Each paragraph makes one point | Split multi-point paragraphs |
| 6 | **Action in verb** | Use verbs, not nominalizations | ❌ "We performed an analysis" → ✅ "We analyzed" |
| 7 | **Context before new** | Set stage before presenting | Explain before showing equation |

## Word Choice

(Zachary Lipton)

### Be Specific
- ❌ "performance" → ✅ "accuracy" or "latency" (say what you mean)
- ❌ "significant" → ✅ "statistically significant (p < 0.05)" or remove

### Eliminate Hedging
Drop "may" and "can" unless genuinely uncertain.
- ❌ "This may improve performance" → ✅ "This improves accuracy by 3.2%"

### Avoid Incremental Vocabulary
- ❌ "combine," "modify," "expand" → ✅ "develop," "propose," "introduce"

### Delete Intensifiers
- ❌ "provides *very* tight approximation" → ✅ "provides tight approximation"

## Precision Over Brevity

(Jacob Steinhardt, UC Berkeley)

- **Consistent terminology**: Different terms for same concept creates confusion. Pick one and stick with it.
- **State assumptions formally**: Before theorems, list all assumptions explicitly
- **Intuition + rigor**: Provide intuitive explanations alongside formal proofs
- **Define before use**: Every symbol and term defined before first use

## Micro-Level Tips

(Ethan Perez, Anthropic)

- [ ] **Minimize pronouns**: ❌ "This shows..." → ✅ "This result shows..."
- [ ] **Verbs early**: Position verbs near sentence start
- [ ] **Unfold apostrophes**: ❌ "X's Y" → ✅ "The Y of X" (when awkward)
- [ ] **Delete filler words**: "actually," "a bit," "very," "really," "basically," "quite," "essentially"
- [ ] **Avoid vague "this"**: Always attach a noun after "this"
- [ ] **Active voice**: ❌ "The method was applied" → ✅ "We applied the method"

## Section-by-Section Guide

| Section | Length | Key Requirements |
|---------|--------|-----------------|
| **Abstract** | 150-250 words | 5-sentence formula; delete generic openings |
| **Introduction** | 1-1.5 pages max | 2-4 bullet contribution list; methods should start by page 2-3 |
| **Methods** | As needed | Enable reimplementation; all hyperparameters listed |
| **Experiments** | Main body | State claim before each experiment; error bars mandatory |
| **Related Work** | 1-1.5 pages | Organize methodologically; each cited work needs individual discussion; max 2 clustered citations |
| **Limitations** | 0.5-1 page | Required by all major venues; pre-empt reviewer criticisms |

### Introduction Must Include:
- Clear problem statement
- 2-4 bullet contribution list (max 1-2 lines each)
- Brief approach overview
- **Citation integration**: Each cited work must be accompanied by a brief description of its contribution, method, or limitation — max 2 clustered citations without discussion (see STYLE_GUIDE.md Anti-Citation-Stacking Rules)

### Experiments Must Include:
- What claim each experiment supports
- Error bars with methodology (std dev vs std error)
- Hyperparameter search ranges
- Compute infrastructure (GPU type, total hours)

## Time Allocation

(Neel Nanda)

Spend approximately **equal time** on each of:
1. The abstract
2. The introduction
3. The figures
4. Everything else combined

**Why?** Most reviewers form judgments before reaching your methods.

**Reader encounter order**: title → abstract → introduction → figures → maybe the rest.

## Sources

| Source | Key Contribution | Link |
|--------|-----------------|------|
| Neel Nanda (Google DeepMind) | The Narrative Principle | [How to Write ML Papers](https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/) |
| Sebastian Farquhar (DeepMind) | 5-sentence abstract formula | [How to Write ML Papers](https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/) |
| Gopen & Swan | 7 principles of reader expectations | [Science of Scientific Writing](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf) |
| Zachary Lipton | Word choice, eliminating hedging | [Heuristics for Scientific Writing](https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/) |
| Jacob Steinhardt (UC Berkeley) | Precision, consistent terminology | [Writing Tips](https://bounded-regret.ghost.io/) |
| Ethan Perez (Anthropic) | Micro-level clarity tips | [Easy Paper Writing Tips](https://ethanperez.net/easy-paper-writing-tips/) |
| Andrej Karpathy | Single contribution focus | Various lectures |
