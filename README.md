# Academic Research Skills — Hermes Adaptation

This fork adapts **Academic Research Skills for Claude Code** into **Hermes Agent** skills.

> Upstream project: https://github.com/Imbad0202/academic-research-skills  
> Upstream author: Cheng-I Wu  
> License preserved: **CC BY-NC 4.0**

## What this fork is

The upstream repository is a Claude Code plugin. This fork keeps the upstream project intact, but adds a Hermes-native adaptation layer under:

```text
hermes/
```

The default branch of this fork is `hermes-adaptation`.

## Hermes skills included

| Skill | Purpose |
|---|---|
| `hermes-academic-deep-research` | Research questions, literature review, systematic-review planning, fact-checking, evidence synthesis. |
| `hermes-academic-paper` | Planning, outlining, drafting, revising, formatting and declaration checks for manuscripts. |
| `hermes-academic-reviewer` | Simulated peer review: editor + reviewers + devil's advocate + editorial decision + revision roadmap. |
| `hermes-academic-pipeline` | End-to-end workflow orchestration: research → write → integrity → review → revise → finalize. |

## What's included beyond SKILL.md

- `references/` protocols for literature review, systematic-review planning, netnography corpora, claim-support audits, manuscript genre discipline, peer-review panels, integrity gates, and journal-fit/APC checks.
- `templates/` for research briefs, literature matrices, paper outlines, abstracts, peer review reports, editorial decisions, and revision roadmaps.
- `examples/` with ready-to-use Hermes prompts for completed PDFs, netnography papers, sport-pedagogy papers, and citation audits.
- `scripts/` for local install, skill validation, PDF extraction, and raw URL install command generation.

## Install into Hermes

```bash
git clone -b hermes-adaptation https://github.com/maximosovsky/academic-research-skills.git
cd academic-research-skills
bash hermes/scripts/install-local.sh all
```

Validate the Hermes layer:

```bash
python hermes/scripts/validate-skills.py
```

Install only selected skills:

```bash
bash hermes/scripts/install-local.sh reviewer pipeline
```

Then start a fresh Hermes session or run:

```text
/reload-skills
```

## Use in Hermes

```text
/skill hermes-academic-reviewer
Полная peer-review имитация Editor + 3 reviewers + devil's advocate + editorial decision для этого PDF.
```

```text
/skill hermes-academic-pipeline
Проведи полный research-to-publication workflow для этой статьи.
```

## Upstream README

The original upstream README is preserved as:

```text
README.upstream.md
```

## License

This fork preserves the upstream **CC BY-NC 4.0** license. Do not treat this fork as MIT or commercial-use licensed unless the upstream rights holder grants a separate license.
