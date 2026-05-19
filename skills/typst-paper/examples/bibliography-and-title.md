# Example: Bibliography And Title

User request:
Validate the bibliography in my Typst submission and tell me whether the title is too vague for a systems paper.

Recommended module sequence:
1. `bibliography`
2. `title`

Commands:
```bash
uv run python $SKILL_DIR/scripts/verify_bib.py references.bib --typ main.typ
uv run python $SKILL_DIR/scripts/optimize_title.py main.typ --check
```

Expected output:
- Missing/unused citation findings for BibTeX or Hayagriva.
- Title score plus candidate refinements.
