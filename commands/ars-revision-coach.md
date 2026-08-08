---
name: ars-revision-coach
description: ARS academic-paper `revision-coach` — peer-review roadmap or source-accounted real-committee response skeleton
---

Trigger the `academic-paper` skill in `revision-coach` mode. Ordinary reviewer comments produce a Revision Roadmap plus Response Letter skeleton without writing the revision. If and only if the user explicitly identifies a real committee or institutional review office, use the #668 committee-correspondence variant: preserve the UTF-8 source, emit the separate concern tracker and placeholder response skeleton, and run its deterministic completeness checker. Never infer committee authority from tone, and never emit priority, severity, determination, or Schema 11 on that branch. Runs on the inherited session model — the v3.7.0 `opus` frontmatter floor was retired in the 2026-06 harness pass so a stronger session model is never silently downgraded.

Mode reference: `MODE_REGISTRY.md` § academic-paper.
Skill entry: `academic-paper/SKILL.md`.
