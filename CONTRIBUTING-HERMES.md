# Contributing to the Hermes Adaptation

Thank you for improving the Hermes Agent adaptation of Academic Research Skills.

This fork preserves the upstream Claude Code project and adds a Hermes-native layer under `hermes/`. Keep that boundary clear.

## Scope

Hermes-specific contributions should usually touch only:

```text
hermes/
docs/hermes/
.github/workflows/hermes-adaptation.yml
CONTRIBUTING-HERMES.md
llms.txt
llms-full.txt
README.md
```

Avoid changing upstream Claude Code plugin files unless the change is required for compatibility, attribution, or repository hygiene.

## License and attribution

This repository is a fork of `Imbad0202/academic-research-skills` and preserves the upstream **CC BY-NC 4.0** license. Do not relicense copied or adapted upstream material as MIT or commercial-use licensed.

When adding new Hermes material:

- preserve upstream attribution;
- do not remove the upstream license notice;
- keep non-commercial license expectations visible;
- avoid copying third-party text without compatible rights.

## Hermes skill format

Each Hermes skill lives at:

```text
hermes/skills/<skill-name>/SKILL.md
```

A skill must include YAML frontmatter with at least:

```yaml
---
name: hermes-academic-example
description: "Use when ..."
---
```

Keep descriptions concise and specific. Put long procedures in the body or in `references/`.

Supporting files should live under:

```text
references/
templates/
scripts/
assets/
```

## Validation

Before opening a PR or pushing to the Hermes branch, run:

```bash
python hermes/scripts/validate-skills.py
bash hermes/scripts/install-local.sh all
```

For README/docs changes, also run or wait for the link checker workflow.

## README and documentation standard

The root `README.md` is English-first and follows the local README guidelines style:

- centered header;
- shields.io badges;
- tagline;
- preview image;
- feature table;
- quick start;
- tech stack;
- roadmap;
- contributing;
- license;
- no `©` symbol.

Do not add translated README files by default. Add `README-<lang>.md` only when explicitly requested.

Keep these files in sync after material changes:

```text
README.md
HERMES.md
llms.txt
llms-full.txt
docs/hermes/*.html
```

## PR checklist

- [ ] Hermes skill frontmatter validates.
- [ ] Local installer smoke test passes.
- [ ] README links are live or intentionally excluded.
- [ ] `llms.txt` and `llms-full.txt` are updated if public-facing docs changed.
- [ ] No secrets, tokens, real private emails, or credentials are included.
- [ ] License/attribution language remains CC BY-NC 4.0 compatible.
