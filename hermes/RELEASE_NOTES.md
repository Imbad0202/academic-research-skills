# v0.1.1-hermes

Hermes Agent adaptation of Academic Research Skills.

## Fixed since v0.1.0-hermes

- Skip upstream Defer Label Gate for `*-hermes` tags so fork releases do not fail when GitHub Issues are disabled.
- Expand Hermes adaptation CI triggers to cover README, `llms.txt`, `llms-full.txt`, and docs changes, not only `hermes/**`.
- Apply the README guidelines standard to the fork landing page: English-first README, centered header, badges, tagline, feature table, quick start, tech stack, roadmap, and license.
- Add `llms.txt` and `llms-full.txt` for LLM discoverability.

## Initial v0.1.0-hermes contents

## Added

- Four Hermes-native skills:
  - `hermes-academic-deep-research`
  - `hermes-academic-paper`
  - `hermes-academic-reviewer`
  - `hermes-academic-pipeline`
- Local installer: `hermes/scripts/install-local.sh`.
- Skill validator: `hermes/scripts/validate-skills.py`.
- PDF extraction helper: `hermes/scripts/extract-pdf.py`.
- Raw install URL helper: `hermes/scripts/install-urls.py`.
- References/protocols for literature review, systematic review, netnography corpus handling, claim-support audit, paper structures, revisions, disclosures, peer review panels, integrity gates, and journal-fit/APC checks.
- Templates for research briefs, literature matrices, paper outlines, abstracts, peer review reports, editorial decisions, journal-fit reports, and revision roadmaps.
- Usage examples for completed PDFs, netnography papers, sport-pedagogy papers, and citation audits.
- GitHub Actions workflow to validate Hermes skills and smoke-test installation.
- GitHub Pages documentation landing page under `docs/`.

## Install

```bash
git clone -b hermes-adaptation https://github.com/maximosovsky/academic-research-skills.git
cd academic-research-skills
python hermes/scripts/validate-skills.py
bash hermes/scripts/install-local.sh all
```

Then start a fresh Hermes session or run `/reload-skills`.

## License

This fork preserves the upstream CC BY-NC 4.0 license.
