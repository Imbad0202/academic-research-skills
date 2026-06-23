---
name: hermes-academic-reviewer
description: "Use when simulating peer review or editorial assessment of an academic manuscript. Produces editor + reviewer reports, devil's advocate critique, editorial decision, and prioritized revision roadmap."
version: 1.0.0
license: CC-BY-NC-4.0
metadata:
  hermes:
    tags: [academic, peer-review, editorial, manuscript-review, revision-roadmap]
    related_skills: [hermes-academic-deep-research, hermes-academic-paper, hermes-academic-pipeline]
---

# Hermes Academic Reviewer

## Overview

Use this skill for pre-submission review, simulated journal peer review, quick editorial diagnosis, rejection-risk analysis, and revision roadmap generation. It is designed for Hermes: extract manuscript text with document tools, use `delegate_task` for independent reviewers, and synthesize a final editorial decision.

## When to Use

- The user asks for peer review, editorial review, referee report, critique, rejection risk, or revision roadmap.
- The user provides a PDF/DOCX/MD/TEX manuscript.
- The user wants `Editor + 3 reviewers + devil's advocate + editorial decision`.

Do not edit the manuscript unless explicitly asked. Review output is separate.

## Quick PDF Workflow

1. Verify the PDF exists.
2. Extract text using PyMuPDF or `pdftotext`; do not read raw PDF bytes as text.
3. Count pages/words and identify title, abstract, genre, sections, references, declarations.
4. Classify manuscript genre before judging it.
5. Choose review panel based on manuscript field.

## Full Peer Review Protocol

Use `delegate_task` in parallel for independent reviewers when available:

- **Reviewer 1 — Domain / field specialist**: contribution, field fit, literature, audience.
- **Reviewer 2 — Methodology / evidence specialist**: corpus, method, data, reproducibility, claim support.
- **Reviewer 3 — Theory / source / implementation specialist**: conceptual framework, source base, practical or disciplinary fit.
- **Devil's Advocate**: strongest rejection reasons and how to neutralize them.
- **Editor**: synthesis, decision, roadmap.

For each reviewer request:

- verdict;
- summary;
- strengths;
- major concerns;
- minor concerns;
- concrete revisions;
- quotes/line references when possible.

## Editorial Decisions

Use one of:

- `Accept` — rare; no major issues.
- `Minor Revision` — publishable after targeted fixes.
- `Major Revision / Revise and Resubmit` — promising but requires substantial revision.
- `Reject with invitation to resubmit` — central framing/method must be rebuilt.
- `Reject` — unsuitable or unsound.

## Common Reviewer Panels

### Conceptual / methodological paper
- Domain specialist
- Method/design specialist
- Theory/source specialist
- Devil's Advocate

### Netnography / comparative corpus paper
- Folklore/traditional-games specialist
- Netnography/qualitative-methodology specialist
- Comparative morphology/diffusion specialist
- Devil's Advocate

### Sport pedagogy / physical education paper
- PE methodology specialist
- Motor learning/praxeology specialist
- Safety/ethics/curriculum specialist
- Devil's Advocate

## Output Template

```markdown
# Editorial Decision
Decision: Major Revision

# Reviewer 1 — ...
## Verdict
## Strengths
## Major Concerns
## Minor Concerns
## Required Revisions

# Devil's Advocate
...

# Editorial Synthesis
## Consensus
## Disagreements

# Revision Roadmap
## Major
## Moderate
## Minor
```

## Pitfalls

1. Do not let reviewers contaminate each other before independent reports are produced.
2. Do not make the Devil's Advocate polite at the expense of identifying real rejection risks.
3. Do not recommend empirical redesign when a conceptual paper only needs claim reframing.
4. Do not output only generic advice; tie comments to the manuscript.
5. Do not call citation existence equivalent to claim support.

## Verification Checklist

- [ ] Manuscript genre identified.
- [ ] Review panel matches discipline and genre.
- [ ] At least three independent perspectives are represented.
- [ ] Devil's Advocate includes concrete fixes.
- [ ] Editorial decision follows from reviewer concerns.
- [ ] Revision roadmap is prioritized and actionable.
