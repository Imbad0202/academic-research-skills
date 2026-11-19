---
disable-model-invocation: true
name: ars-revision-coach
description: ARS academic-paper `revision-coach` — peer-review roadmap or source-accounted research-ethics-review response skeleton
---

First invoke the Skill tool with `skill: "academic-research-skills:academic-paper"`. Pass the mode and the user's request described below as its arguments. Use the loaded skill and its supporting files before producing the result.

Trigger the `academic-paper` skill in `revision-coach` mode. Ordinary reviewer comments produce a Revision Roadmap plus Response Letter skeleton without writing the revision. If and only if the user explicitly identifies a body that reviews research with human participants or their data for research ethics or human-subjects protection (such as a research ethics committee, an IRB, or a human research ethics office; not a scientific, statistical, data-access, or safety review, a thesis committee, or a grant panel), use the #668 committee-correspondence variant: quote the user's words that name the body, preserve the UTF-8 source, emit the separate concern tracker and placeholder response skeleton, and run its deterministic completeness checker. Never infer committee authority from tone, and never emit priority, severity, determination, or Schema 11 on that branch. Runs on the inherited session model — the v3.7.0 `opus` frontmatter floor was retired in the 2026-06 harness pass so a stronger session model is never silently downgraded.

Mode reference: `${CLAUDE_PLUGIN_ROOT}/MODE_REGISTRY.md` § academic-paper.
Skill entry: `${CLAUDE_PLUGIN_ROOT}/academic-paper/SKILL.md`.

Resolve plugin resources from `${CLAUDE_PLUGIN_ROOT}`, not from the paper project's working directory. If the skill or a required file cannot be loaded, report the loading failure and stop; do not substitute this command summary for the mode instructions.
