# Hermes Adaptation

This branch adds a Hermes Agent adaptation layer for Academic Research Skills.

## License

This is a fork of `Imbad0202/academic-research-skills` and preserves the upstream license: **CC BY-NC 4.0**. The Hermes adaptation files are distributed as part of this fork under the same repository license unless a future rights-holder-approved relicensing is obtained.

## What this adds

Hermes-native skill folders live under:

```text
hermes/skills/
```

Current modules:

- `hermes-academic-deep-research`
- `hermes-academic-paper`
- `hermes-academic-reviewer`
- `hermes-academic-pipeline`

These skills translate the ARS workflow into Hermes idioms:

- use `read_file`, `search_files`, `terminal` for local manuscripts and corpora;
- use `web` for current literature and fact checking;
- use `delegate_task` for independent reviewer panels;
- use `todo` for multi-stage orchestration;
- keep manuscript review output separate from manuscript edits unless explicitly requested.

## Added package surface

- `hermes/skills/` — four Hermes skills.
- `hermes/skills/*/references/` — Hermes-native protocols and checklists.
- `hermes/skills/*/templates/` — report, outline, matrix, and roadmap templates.
- `hermes/examples/` — ready-to-use prompts for common manuscript workflows.
- `hermes/scripts/` — local install, validation, PDF extraction, and raw URL helpers.

## Install selected skills into Hermes

From the repo root:

```bash
bash hermes/scripts/install-local.sh all
# or:
bash hermes/scripts/install-local.sh reviewer pipeline
```

Validate before installing:

```bash
python hermes/scripts/validate-skills.py
```

Then start a fresh Hermes session or run `/reload-skills`.

## Direct skill URLs

Hermes can install a direct `SKILL.md` URL, but local installation is preferred because supporting references/templates are copied too.

```bash
hermes skills install https://raw.githubusercontent.com/maximosovsky/academic-research-skills/hermes-adaptation/hermes/skills/hermes-academic-reviewer/SKILL.md --name hermes-academic-reviewer
```

## Relationship to Claude Code plugin surface

This adaptation does not attempt to port Claude Code slash commands (`/ars-plan`, `/ars-reviewer`, etc.) as Hermes slash commands. Instead, each Hermes skill has trigger instructions and can be loaded with `/skill <name>` or selected automatically by Hermes.
