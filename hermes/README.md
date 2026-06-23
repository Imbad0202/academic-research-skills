# Hermes Skills for Academic Research Skills

This directory contains Hermes Agent skill adaptations of the ARS workflow.

## Skills

| Skill | Use for |
|---|---|
| `hermes-academic-deep-research` | Research questions, literature review, systematic-review planning, fact-checking. |
| `hermes-academic-paper` | Paper planning, outlining, drafting, revision, formatting, declarations. |
| `hermes-academic-reviewer` | Editor + reviewers + devil's advocate + editorial decision + revision roadmap. |
| `hermes-academic-pipeline` | End-to-end orchestration across research, write, review, revise, finalize. |

## Install

```bash
bash hermes/scripts/install-local.sh all
```

Override target:

```bash
HERMES_SKILLS_DIR="$HOME/AppData/Local/hermes/skills/research" bash hermes/scripts/install-local.sh all
```

## Example

```text
/skill hermes-academic-reviewer
Полная peer-review имитация Editor + 3 reviewers + devil's advocate + editorial decision для этого PDF.
```
