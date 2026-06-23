# Hermes Skills for Academic Research Skills

This directory contains Hermes Agent skill adaptations of the ARS workflow.

## Skills

| Skill | Use for |
|---|---|
| `hermes-academic-deep-research` | Research questions, literature review, systematic-review planning, fact-checking. |
| `hermes-academic-paper` | Paper planning, outlining, drafting, revision, formatting, declarations. |
| `hermes-academic-reviewer` | Editor + reviewers + devil's advocate + editorial decision + revision roadmap. |
| `hermes-academic-pipeline` | End-to-end orchestration across research, write, review, revise, finalize. |

## What's included

- `skills/*/SKILL.md` — Hermes-native skill instructions.
- `skills/*/references/` — protocols and checklists.
- `skills/*/templates/` — reusable report/matrix/roadmap templates.
- `examples/` — ready-to-use Hermes prompts.
- `scripts/` — install, validate, PDF extraction, and raw URL helpers.

## Install

```bash
bash hermes/scripts/install-local.sh all
```

Override target:

```bash
HERMES_SKILLS_DIR="$HOME/AppData/Local/hermes/skills/research" bash hermes/scripts/install-local.sh all
```

## Validate

```bash
python hermes/scripts/validate-skills.py
```

## Helper scripts

| Script | Purpose |
|---|---|
| `install-local.sh` | Copy selected skills into the local Hermes skills directory. |
| `validate-skills.py` | Validate Hermes `SKILL.md` frontmatter and basic structure. |
| `extract-pdf.py` | Extract local PDF text for review/citation workflows. |
| `install-urls.py` | Print direct `hermes skills install` commands for raw GitHub URLs. |

## Example

```text
/skill hermes-academic-reviewer
Полная peer-review имитация Editor + 3 reviewers + devil's advocate + editorial decision для этого PDF.
```

More examples live in `hermes/examples/`.
