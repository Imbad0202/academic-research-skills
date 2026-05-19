# Example: Bibliography And Pseudocode

User request:
Validate whether this Typst project uses Hayagriva or BibTeX, then review the `algorithm-figure` block and tell me which issues are mandatory versus only IEEE-like recommendations.

Recommended module sequence:
1. `bibliography`
2. `pseudocode`

Commands:
```bash
uv run python $SKILL_DIR/scripts/verify_bib.py references.yml --typ main.typ
uv run python $SKILL_DIR/scripts/check_pseudocode.py main.typ --venue ieee
```

Expected output:
- Detect the bibliography format before running checks.
- Preserve `@cite`, labels, and Typst macros.
- Separate hard wrapper/caption problems from advisory items such as line numbers or comment length.
