---
name: ars-disclosure
description: ARS academic-paper `disclosure` mode — venue applicability/status bundle or policy-anchor render
model: sonnet
---

Trigger the `academic-paper` skill in standalone `disclosure` mode. Agent 9 must load `academic-paper/references/disclosure_mode_protocol.md` before rendering; the generic formatter disclosure is not a fallback. The default venue path returns `REQUIRED`, `ACTION_ONLY`, `NOT_REQUIRED`, or `UNKNOWN` applicability plus an explicit typed halt status when needed (15 policy targets supported: ICLR / NeurIPS / Nature / Science / ACL / EMNLP plus medical-publishing targets — ICMJE / NEJM / The Lancet / JAMA / BMJ / PLOS / Frontiers / publisher-wide 中华护理杂志社 / journal-level 国际眼科杂志). The `--policy-anchor` path uses its separate anchor-specific renderer. Fidelity spectrum, low oversight.

Mode reference: `MODE_REGISTRY.md` § academic-paper.
Skill entry: `academic-paper/SKILL.md`.
