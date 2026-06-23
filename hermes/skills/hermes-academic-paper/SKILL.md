---
name: hermes-academic-paper
description: "Use when planning, outlining, drafting, revising, formatting, or polishing an academic manuscript, including conceptual papers, empirical IMRaD articles, literature reviews, policy briefs, and conference papers."
version: 1.0.0
license: CC-BY-NC-4.0
metadata:
  hermes:
    tags: [academic, writing, manuscript, revision, formatting]
    related_skills: [hermes-academic-deep-research, hermes-academic-reviewer, hermes-academic-pipeline]
---

# Hermes Academic Paper

## Overview

Use this skill to convert research material into a manuscript plan, outline, draft, revision, abstract, or submission-ready package. Preserve the manuscript's declared genre: a conceptual/methodological paper should not be forced into an empirical IMRaD structure.

## When to Use

- The user asks to write a paper, outline, abstract, literature review, methodology, discussion, or conclusion.
- The user has reviewer comments and needs a revision plan or revised text.
- The user needs citation format conversion, AI disclosure, or submission package preparation.

Do not use for independent peer review; use `hermes-academic-reviewer`.

## Modes

| Mode | Trigger | Output |
|---|---|---|
| `plan` | guide my paper, unsure structure | paper configuration + outline |
| `outline` | build structure | section plan + word budget |
| `draft` | write manuscript | section-by-section draft |
| `abstract` | write/revise abstract | structured or unstructured abstract |
| `revision` | reviewer comments / improve draft | revision roadmap + patches/proposed edits |
| `citation-check` | check citations | reference and support audit |
| `format` | prepare for journal | formatting checklist + package plan |
| `disclosure` | AI/ethics/data statements | declarations text |

## Core Workflow

1. Classify manuscript genre: empirical IMRaD, conceptual/theoretical, methodological/design, literature review, case study, policy brief.
2. Collect inputs: existing draft, notes, sources, target venue, style, word count.
3. Create a configuration record: title, genre, discipline, audience, contribution, citation style, output format.
4. Build outline with claim-evidence mapping.
5. Draft or revise section by section. Do not invent sources, data, or results.
6. Run self-check for overclaims, unsupported citations, genre mismatch, ethics/disclosure.

## Manuscript Genre Discipline

For conceptual/methodological papers, evaluate and write around:

- recoverability of reconstruction/design logic;
- adequacy of corpus/material;
- conceptual contribution;
- claim strength vs evidence;
- limitations and future validation.

Do not demand samples, statistics, or hypotheses unless the genre requires them.

## Revision Roadmap Shape

- **Major revisions**: claims, method, evidence, structure, ethics, safety.
- **Moderate revisions**: tables, terminology, literature, limitations.
- **Minor revisions**: style, formatting, references, abstract, keywords.

## Pitfalls

1. Do not overstate empirical effects in non-empirical papers.
2. Do not add references that have not been checked.
3. Do not add unsupported results or methods.
4. Do not rewrite the manuscript when the user asked only for a roadmap.
5. For journal submissions, check APC/fees if relevant to the user's constraints.

## Verification Checklist

- [ ] Genre and target audience are explicit.
- [ ] Main contribution is stated in 1-3 sentences.
- [ ] Claims have evidence or are marked as hypotheses.
- [ ] Limitations match evidence status.
- [ ] Ethics, data, funding, AI-use statements are present when needed.
