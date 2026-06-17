---
title: Academic Research Skills
description: AI-augmented academic research pipeline with integrity verification
version: 3.12.1
license: CC BY-NC 4.0
---

# Academic Research Skills for GitHub Copilot

## Quick Summary
This repository contains a comprehensive suite of AI agents and skills for academic research, designed to augment human researchers rather than replace them. It covers the complete pipeline from deep research through paper writing and peer review, with built-in integrity verification and quality gates.

## Core Principle
**AI is your copilot, not the pilot.** The system handles grunt work (references, formatting, verification) while humans focus on substantive decisions, methodology, and interpretation.

## When to Use Each Component

### Use Deep Research When:
- Conducting literature reviews
- Need PRISMA systematic review structure
- Seeking cross-disciplinary connections
- Want to verify source availability
- Need intent detection for research direction

### Use Academic Paper When:
- Writing research papers or dissertations
- Need style calibration to your voice
- Want citation verification before submission
- Need help with revision and polish
- Require LaTeX compilation support

### Use Academic Paper Reviewer When:
- Preparing for peer review submission
- Need diverse reviewer perspectives
- Want quality rubric feedback
- Need R&R traceability
- Seeking devil's advocate critique

### Use Academic Pipeline When:
- Running the full publication workflow
- Need claim verification at scale
- Want experiment provenance tracking
- Need material passport for reproducibility
- Require adaptive checkpoints

## Installation

### Via Plugin (Recommended)
```
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

### Via Local Symlink
```bash
# Clone repo
git clone https://github.com/imbad0202/academic-research-skills
cd academic-research-skills

# Set up Claude Code to use the skills
# See docs/SETUP.md for detailed instructions
```

## Getting Started

**Test it works:** Run `/ars-plan` and describe a paper you're working on. ARS will guide you through structure via Socratic dialogue.

**For literature review:** Use `/ars-lit-review "your topic"`

**For full pipeline:** Use `/ars-pipeline` to run the orchestrated 10-stage workflow

## Important Failure Modes (Know These!)

The project explicitly addresses AI research failure modes identified by Lu et al. (2026):
- Implementation bugs
- Hallucinated results
- Shortcut reliance
- Methodology fabrication
- Citation hallucinations (see Zhao et al. 2026 corpus analysis)

Mitigations:
- 7-mode blocking checklist (Stage 2.5 and 4.5 gates)
- Claim-level audit with locator anchors
- Trust-chain frontmatter for provenance
- FNR/FPR calibration on custom measures

## Cost & Performance

- **Estimated cost:** $4–6 for a 15k-word paper
- **Token budgets:** See `docs/PERFORMANCE.md`
- **Recommended settings:** Skip Permissions, optional Agent Team

## File Structure for Contributors

- `agents/` - Individual agent implementations
- `commands/` - CLI entry points and user interactions
- `skills/` - Reusable skill modules with `data_access_level` and `task_type`
- `shared/` - Common patterns: ground truth isolation, benchmarking, reproducibility
- `scripts/` - Validation and checking utilities
- `docs/` - Full architecture, setup, performance, positioning

## Data Access & Task Annotations

All new code should declare:

```python
METADATA = {
    "data_access_level": "raw|redacted|verified_only",  # Data scope
    "task_type": "open-ended|outcome-gradable",         # Task classification
}
```

Enforcement: `python scripts/check_data_access_level.py`

## Key Commands for Researchers

- `/ars-plan` — Socratic dialogue for paper structure
- `/ars-lit-review TOPIC` — Quick literature review
- `/ars-deep-research` — Full 13-agent research team
- `/ars-write` — 12-agent paper writing
- `/ars-review` — 7-agent peer review
- `/ars-pipeline` — Full 10-stage orchestrated workflow

## Documentation Pointers

- **Architecture:** `docs/ARCHITECTURE.md` — flow diagrams, stage matrix, dependency graph
- **Setup:** `docs/SETUP.md` — installation, API keys, optional tools
- **Performance:** `docs/PERFORMANCE.md` — token budgets, costs
- **Positioning:** `docs/POSITIONING.md` — design philosophy, research grounding

## License & Citation

- **License:** CC BY-NC 4.0 (non-commercial use)
- **Citation:** See `CITATION.cff`
- **DOI:** [10.5281/zenodo.20696614](https://doi.org/10.5281/zenodo.20696614)

## Support & Community

- **Report issues:** GitHub Issues
- **Contribute:** See `CONTRIBUTING.md`
- **Security concerns:** See `SECURITY.md`
- **Sponsor development:** [Buy Me a Coffee](https://buymeacoffee.com/crucify020v)

## Version
v3.12.1 — see `CHANGELOG.md` for updates

---

**Remember:** This tool helps you write *better*, not helps you hide that you used AI. Integrity and human judgment are non-negotiable.
