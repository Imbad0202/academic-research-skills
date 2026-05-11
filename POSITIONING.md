# Positioning

## What this is

Academic Research Skills (ARS) is a **source-available academic research copilot framework** for noncommercial scholarly use. The reference distribution is a suite of Claude Code skills that assists human researchers through the full research-to-publication pipeline. Sibling distributions for other agent platforms (e.g. Codex) follow the same workflow content, the same human-in-the-loop design philosophy, and the same license terms; see [CONTRIBUTING.md § Platform ports](CONTRIBUTING.md#platform-ports-community-maintained-only).

It is licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). This is not an open source license — it restricts commercial use by design, to keep the tool free for academic communities.

## What this is not

ARS is not an autonomous paper-writing system. It is not a replacement for the researcher. It does not claim authorship, and its outputs are not submission-ready without human review.

## Allowed uses

- Research assistance: literature search, source verification, citation checking
- Teaching: demonstrating research methodology, peer review processes, academic writing standards
- Method training: using Socratic modes to develop research question formulation and argumentation skills
- Noncommercial academic collaboration: research groups, labs, departments using the tool for shared workflows

## Discouraged uses

- Submitting AI-generated papers as solely human-authored without disclosing AI assistance
- Using the tool to produce papers without engaging with the content (the pipeline has mandatory checkpoints specifically to prevent this)
- Treating AI-generated review feedback as a substitute for actual peer review

## Prohibited uses (per license)

- Commercial SaaS or hosted services built on ARS
- Consulting or freelance services that package ARS as a paid product
- Enterprise or institutional paid deployments without separate licensing
- Commercial API wrappers or resale of ARS functionality

These reflect our policy intent. See the [CC BY-NC 4.0 license](https://creativecommons.org/licenses/by-nc/4.0/) for the precise legal terms. For commercial licensing inquiries, contact the maintainer.

## Design philosophy

**Assistive, not deceptive.** ARS helps you write better, not hide that you used AI.

- Style Calibration learns your voice from past papers — so the output sounds like you, not like a machine
- Writing Quality Check catches AI-typical patterns — to improve prose quality, not evade detection
- Disclosure Mode generates venue-specific AI usage statements — because transparency is the standard

**Human-in-the-loop, always.** The pipeline's checkpoint system is mandatory by design:

- FULL checkpoints present all deliverables and require explicit user confirmation
- MANDATORY checkpoints at integrity gates and review decisions cannot be skipped
- "Full mode" means full-pipeline execution, not full autonomy — the human decides at every gate
- Max 2 revision loops, after which remaining issues become "Acknowledged Limitations" rather than being silently resolved

**Failure modes are made visible, not hidden.** The 7-mode AI Research Failure Mode Checklist (v3.2) and Reviewer Calibration Mode exist so that users can see where the AI might be wrong — not so that the AI can claim it's always right.

## Citing this tool

If you use ARS in your research, please cite it:

```
Wu, C.-I. (2026). Academic Research Skills for Claude Code (Version 3.3) [Computer software]. https://github.com/Imbad0202/academic-research-skills
```
