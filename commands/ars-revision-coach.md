---
disable-model-invocation: true
name: ars-revision-coach
description: ARS academic-paper `revision-coach` — peer-review roadmap or source-accounted research-ethics-review response skeleton
---

First invoke the Skill tool with `skill: "academic-research-skills:academic-paper"`. Pass the mode and the user's request described below as its arguments. Use the loaded skill and its supporting files before producing the result.

Trigger the `academic-paper` skill in `revision-coach` mode. Ordinary reviewer comments produce a Revision Roadmap plus Response Letter skeleton without writing the revision. If the user says, or the pasted text shows, that the comments may come from a research ethics or human-subjects protection review (for example, from a research ethics committee or an institutional review board (IRB)), load the protocol of the #668 committee-correspondence variant (`committee_correspondence_protocol.md`). The Activation gate in `committee_correspondence_protocol.md` decides which comments this variant covers and what to quote from the user before taking it; comments that the gate excludes take normal `revision-coach` (#907). On the variant, preserve the UTF-8 source, emit the separate concern tracker and placeholder response skeleton, and run its deterministic completeness checker. Never infer committee authority from tone, and never emit priority, severity, determination, or Schema 11 on that branch. Runs on the inherited session model — the v3.7.0 `opus` frontmatter floor was retired in the 2026-06 harness pass so a stronger session model is never silently downgraded.

Mode reference: `${CLAUDE_PLUGIN_ROOT}/MODE_REGISTRY.md` § academic-paper.
Skill entry: `${CLAUDE_PLUGIN_ROOT}/academic-paper/SKILL.md`.

Resolve plugin resources from `${CLAUDE_PLUGIN_ROOT}`, not from the paper project's working directory. If the skill or a required file cannot be loaded, report the loading failure and stop; do not substitute this command summary for the mode instructions.
