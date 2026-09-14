---
name: ars-abstract
description: ARS academic-paper `abstract-only` mode — bilingual abstract + keywords
model: sonnet
---

Trigger the `academic-paper` skill in `abstract-only` mode. Produces a bilingual abstract plus keywords. Abstract languages follow the run's declared `output_language_pair`, which is a per-run value defaulting to `zh-tw-en` (zh-TW + EN) — so an unconfigured run keeps the pre-#862 pairing. Fidelity spectrum, medium oversight. Carries the v3.6.7 `report_compiler_agent` PATTERN PROTECTION layer when invoked through the pipeline.

Mode reference: `MODE_REGISTRY.md` § academic-paper.
Skill entry: `academic-paper/SKILL.md`.
