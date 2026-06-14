---
name: reviewer-response
description: "Point-by-point reviewer response package for academic review-and-revision work. Converts decision letters, reviewer comments, author change notes, and draft rebuttals into an auditable response strategy, comment-response tracker, revision-evidence checklist, and submission-ready response package. Modes: draft, audit, revise, triage-only, appeal-like. Triggers on: response to reviewers, rebuttal letter, point-by-point response, reviewer response, revise and resubmit response, decision letter, panel comments, author rebuttal, conference rebuttal, grant response."
metadata:
  version: "0.1.0"
  last_updated: "2026-06-14"
  status: active
  data_access_level: verified_only
  task_type: open-ended
  related_skills:
    - academic-paper
    - academic-paper-reviewer
    - academic-pipeline
---

# Reviewer Response — Reviewer Response Package Builder

Use this skill to turn reviewer, panel, or editor feedback into an auditable point-by-point response package for academic revision work.

The response package is a reviewer-facing verification document. The goal is to show that every concern has been understood, answered, and mapped to a concrete revision action, evidence location, justified scientific disagreement, or explicit author-input placeholder.

> **Routing discipline:** this skill sits beside the core ARS pipeline. Use it when the user's primary need is the response package itself. If the user needs full draft revision execution, `academic-paper` `revision` mode remains the main writer. If the user needs end-to-end orchestration across review, revision, integrity, and finalization, use `academic-pipeline`.

## Quick Start

**Simplest command:**
```text
Draft a response package for this review round: [paste decision letter + reviewer comments]
```

**Typical output:**
1. Response strategy summary
2. Comment-response tracker
3. Draft point-by-point response package
4. Revision-evidence checklist
5. Missing information and risk flags

## Trigger Conditions

### Trigger Keywords

**English**: response to reviewers, rebuttal letter, point-by-point response, reviewer response, revise and resubmit response, decision letter, panel comments, editor comments, author rebuttal, response letter, appeal letter, conference rebuttal, grant response

### Does NOT Trigger

| Scenario | Use Instead |
|----------|-------------|
| Need to revise the main draft text itself | `academic-paper` `revision` |
| Need a fresh simulated peer review | `academic-paper-reviewer` |
| Need full pipeline orchestration | `academic-pipeline` |

### Quick Mode Selection Guide

| Your Situation | Recommended Mode | Spectrum |
|----------------|-----------------|----------|
| Need a new response package from raw reviewer comments | `draft` | balanced |
| Already have a draft response and want QA / gap detection | `audit` | fidelity |
| Need the response package revised after author updates | `revise` | balanced |
| Need only a parsed tracker, not prose drafting yet | `triage-only` | fidelity |
| Need to assess a possible pushback / partial disagreement case | `appeal-like` | originality |

## Operational Modes (5 Modes)

| Mode | Trigger | Output |
|------|---------|--------|
| `draft` | Default / "draft response" | Strategy summary + tracker + point-by-point response package |
| `audit` | "audit this rebuttal" | Gap report + risk flags + corrected response guidance |
| `revise` | "update this response" | Updated tracker + revised response package |
| `triage-only` | "parse comments only" | Comment-response tracker + action map without letter prose |
| `appeal-like` | "should we push back?" | Pushback-risk memo + cautious response posture draft |

## Accepted Inputs

The skill may receive:

- editor or panel decision letter
- reviewer comments
- previous response draft
- revision change notes
- tracked-change summary
- line or page numbers
- figure, table, appendix, or supplement list
- author notes in Chinese or English
- venue or evaluation context, such as journal, conference, grant panel, transfer-after-review, or departmental review

If reviewer boundaries or comment segmentation are ambiguous, flag the ambiguity instead of inventing reviewer structure.

## Workflow

1. Identify task mode and input readiness: `draft`, `audit`, `revise`, `triage-only`, or `appeal-like`.
2. Identify decision type: minor revision, major revision, revise-and-resubmit, transfer after review, conference rebuttal round, grant panel response, or unclear.
3. Extract chair, editor, panel, or meta-review instructions first and assign IDs such as `E.1`, then split reviewer comments with IDs such as `R1.1`, `R1.2`, and `R2.1`.
4. Classify each item by category, severity, action label, missing input, readiness state, and risk.
5. Create a response strategy summary before drafting prose.
6. Draft responses using preserved reviewer comments unless the mode is `triage-only` or `appeal-like`.
7. Map each claimed change to draft location, figure, table, appendix, supplement, citation, planned attachment, or explicit placeholder.
8. Flag missing author input rather than fabricating details.
9. Run QA for completeness, traceability, factuality, tone, and unresolved risk.
10. Return the response package with package readiness: `ready_to_submit`, `draft_with_placeholders`, `needs_author_input`, or `blocked`.

## Output Format

Unless the user asks for another format, return:

```text
Response strategy summary
- Decision type:
- Overall posture:
- Major risks:
- Suggested ordering:

Comment-response tracker
| ID | Reviewer concern | Type | Severity | Proposed action | Missing author input |
|---|---|---|---|---|---|

Draft point-by-point response package
[reviewer-readable English response]

Revision-evidence checklist
- [specific draft changes, evidence locations, or placeholders]

Missing information / risk flags
- [specific unresolved items or "None"]

中文核对
- [when the user writes in Chinese; otherwise omit unless useful]
```

## Related Files

| File | Open when |
|---|---|
| [references/intake-and-routing.md](references/intake-and-routing.md) | Before drafting, to identify task mode, minimum inputs, and readiness state |
| [references/response-structure.md](references/response-structure.md) | You need the response package format or point-by-point package anatomy |
| [references/tone-and-stance.md](references/tone-and-stance.md) | You need recommended language, disagreement tone, or forbidden phrasing |

## Red Lines

- Do not ignore any reviewer comment.
- Do not rephrase reviewer comments in a way that changes their meaning.
- Do not claim a revision was made unless the user supplied it.
- Do not invent line numbers, figure panels, citations, statistical results, or supplementary items.
- Do not use hostile or accusatory language.
- Do not cite time, money, or convenience as the primary reason for declining a requested experiment.
- Do not hide limitations.
