---
name: hermes-academic-deep-research
description: "Use when the user needs rigorous academic research: research-question shaping, literature review, systematic-review planning, source discovery, fact-checking, evidence synthesis, or claim verification before writing a paper."
version: 1.0.0
license: CC-BY-NC-4.0
metadata:
  hermes:
    tags: [academic, research, literature-review, fact-checking, evidence]
    related_skills: [hermes-academic-paper, hermes-academic-reviewer, hermes-academic-pipeline]
---

# Hermes Academic Deep Research

## Overview

Use this skill to turn a topic, hypothesis, folder of notes, or manuscript idea into a grounded research brief. It is Hermes-native: use `web` for current sources, `read_file`/`search_files` for local corpora, `delegate_task` for parallel searches, and `todo` for multi-step research.

## When to Use

- The user asks for literature review, systematic review, research brief, fact-checking, source verification, or research question design.
- The user has a vague topic and wants to clarify a publishable research question.
- The user needs a corpus before drafting an article.
- The user needs to verify claims or citations in a manuscript.

Do not use for manuscript peer review; use `hermes-academic-reviewer`.

## Modes

| Mode | Trigger | Output |
|---|---|---|
| `socratic` | vague idea, user wants guidance | research-question options + scope boundaries |
| `quick` | quick brief | concise state-of-field summary |
| `lit-review` | literature review | themes, sources, gaps, matrix |
| `systematic-plan` | systematic review / PRISMA | protocol, search strings, inclusion/exclusion criteria |
| `fact-check` | verify claims | claim table with support status |
| `three-way-scan` | compare papers | WHY/HOW/WHAT comparison |

## Workflow

1. Classify the task: exploratory, literature, systematic, fact-check, or comparison.
2. Define scope: research question, discipline, date range, languages, venue constraints.
3. Gather sources from local files and/or the web. Use parallel delegation for independent subtopics.
4. Grade sources: peer-reviewed, book, official report, preprint, grey literature, web testimony.
5. Synthesize claims, evidence, contradictions, gaps, and implications.
6. Mark uncertainty: do not present weak or grey evidence as settled fact.

## Output Shapes

### Research Brief

- Research question
- Scope and exclusions
- Key concepts
- State of the field
- Evidence table
- Gaps and controversies
- Recommended next sources

### Fact-Check Table

| Claim | Source cited | Support status | Evidence/quote | Fix |
|---|---|---|---|---|

Support status: `supported`, `partially-supported`, `overstated`, `unsupported`, `needs-source`, `unclear`.

## Pitfalls

1. Do not treat Google snippets or AI summaries as sources.
2. Do not claim a paper supports a statement unless the relevant passage was inspected.
3. Do not fail conceptual/theoretical projects for lacking empirical data; evaluate evidence appropriate to genre.
4. Distinguish source existence from claim support.
5. For grey literature/netnography, create a source reliability hierarchy.

## Verification Checklist

- [ ] Research question and scope are explicit.
- [ ] Sources are named with enough bibliographic detail to verify.
- [ ] Claims are separated from evidence.
- [ ] Weak evidence is marked as weak.
- [ ] Next action is clear: write, review, revise, or gather more data.
