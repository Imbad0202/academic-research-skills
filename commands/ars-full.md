---
disable-model-invocation: true
name: ars-full
description: ARS full pipeline — research → write → review → revise → finalize
---

First invoke the Skill tool with `skill: "academic-research-skills:academic-pipeline"`. Pass the mode and the user's request described below as its arguments. Use the loaded skill and its supporting files before producing the result.

Trigger the `academic-pipeline` orchestrator (`(pipeline)` in `${CLAUDE_PLUGIN_ROOT}/MODE_REGISTRY.md` — the orchestrator has no named mode of its own). Loads the skill and executes the complete academic research workflow (10-stage orchestration: deep-research → academic-paper → integrity → academic-paper-reviewer → revision → re-review → final integrity → finalize).

Mode reference: `${CLAUDE_PLUGIN_ROOT}/MODE_REGISTRY.md` § academic-pipeline.
Skill entry: `${CLAUDE_PLUGIN_ROOT}/academic-pipeline/SKILL.md`.

Resolve plugin resources from `${CLAUDE_PLUGIN_ROOT}`, not from the paper project's working directory. If the skill or a required file cannot be loaded, report the loading failure and stop; do not substitute this command summary for the mode instructions.
