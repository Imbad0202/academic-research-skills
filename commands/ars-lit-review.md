---
disable-model-invocation: true
name: ars-lit-review
description: ARS academic-paper `lit-review` mode — annotated bibliography in paper format
model: sonnet
---

First invoke the Skill tool with `skill: "academic-research-skills:academic-paper"`. Pass the mode and the user's request described below as its arguments. Use the loaded skill and its supporting files before producing the result.

Trigger the `academic-paper` skill in `lit-review` mode. Produces an annotated bibliography rendered as a literature review section. Fidelity spectrum, medium oversight.

Stay in `academic-paper` `lit-review` mode and do not reopen the choice of workflow: if the papers or sources the request refers to are missing, ask the user for them or offer to search for them within this mode.

Mode reference: `${CLAUDE_PLUGIN_ROOT}/MODE_REGISTRY.md` § academic-paper.
Skill entry: `${CLAUDE_PLUGIN_ROOT}/academic-paper/SKILL.md`.

Resolve plugin resources from `${CLAUDE_PLUGIN_ROOT}`, not from the paper project's working directory. If the skill or a required file cannot be loaded, report the loading failure and stop; do not substitute this command summary for the mode instructions.
