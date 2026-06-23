---
name: hermes-academic-pipeline
description: "Use when orchestrating an end-to-end academic workflow: research, paper planning, drafting, integrity checks, peer review, revision, final verification, formatting, and submission preparation."
version: 1.0.0
license: CC-BY-NC-4.0
metadata:
  hermes:
    tags: [academic, pipeline, research-to-publication, orchestration]
    related_skills: [hermes-academic-deep-research, hermes-academic-paper, hermes-academic-reviewer]
---

# Hermes Academic Pipeline

## Overview

This skill orchestrates a full research-to-publication workflow in Hermes. It does not replace researcher judgment. It routes work to deep research, paper writing, peer review, revision, integrity checking, and final formatting.

## When to Use

- The user asks for a complete research-to-paper or paper-to-submission workflow.
- The user has a manuscript and wants review -> revision -> final check.
- The user has notes and wants an article developed through staged checkpoints.

If the user only needs one function, use the specialized skill directly.

## Stages

| Stage | Name | Primary skill | Deliverable |
|---|---|---|---|
| 1 | Research | `hermes-academic-deep-research` | RQ, corpus, synthesis |
| 2 | Plan/Write | `hermes-academic-paper` | outline or draft |
| 2.5 | Integrity | deep research + paper | claim/citation/data check |
| 3 | Review | `hermes-academic-reviewer` | editorial decision + reports |
| 4 | Revise | `hermes-academic-paper` | revision roadmap / revised text |
| 4.5 | Final integrity | deep research + reviewer | final claim support check |
| 5 | Finalize | `hermes-academic-paper` | formatted package |

## Entry Point Detection

- No clear topic -> Stage 1 Socratic research.
- Topic + notes -> Stage 1 lit review or Stage 2 plan.
- Full manuscript PDF/DOCX/MD -> Stage 2.5 integrity or Stage 3 review.
- Reviewer comments -> Stage 4 revision.
- Final draft + target journal -> Stage 5 finalize.

## Checkpoint Discipline

At major transitions, present a concise checkpoint:

- what was produced;
- main risks found;
- recommended next stage;
- user decision needed.

Do not silently move from research to writing, or from review to revision, when the user needs to approve direction.

## Integrity Gates

Before review and before finalization, check:

- citation existence;
- claim support;
- overclaims;
- source reliability;
- data availability;
- ethics/AI/funding declarations;
- genre mismatch;
- venue requirements.

For non-empirical manuscripts, do not demand empirical data; instead verify whether claims are framed as conceptual, methodological, or hypothetical.

## Recommended Pipelines

### Completed preprint

1. Extract clean text.
2. Quick editorial diagnosis.
3. Full peer-review simulation.
4. Citation/claim audit.
5. Revision roadmap.
6. Journal-fit/APC check.
7. Final formatting and declarations.

### New article from notes

1. Research-question shaping.
2. Literature matrix.
3. Paper outline.
4. Draft sections.
5. Self-review and citation check.
6. External-style peer review.
7. Revision.

## Pitfalls

1. Running a full pipeline when the user requested one stage.
2. Skipping source verification before writing strong claims.
3. Treating preprints as peer-reviewed evidence.
4. Forgetting user constraints such as APC avoidance, language, or venue.
5. Continuing automatically past a major decision point.

## Verification Checklist

- [ ] Entry point identified.
- [ ] Correct specialized skill loaded or followed.
- [ ] Artifacts from prior stages are preserved or summarized.
- [ ] Integrity checks are explicit.
- [ ] User-facing next step is clear.
