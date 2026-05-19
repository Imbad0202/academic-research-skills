# Example: Compile And Bibliography

User request:
Compile my IEEE paper, then tell me why two citations are unresolved in `main.tex`.

Recommended module sequence:
1. `compile`
2. `bibliography`

Commands:
```bash
uv run python -B $SKILL_DIR/scripts/compile.py main.tex
uv run python -B $SKILL_DIR/scripts/verify_bib.py references.bib --tex main.tex
```

Expected output:
- Build result with the exact failing command if compilation breaks.
- `% COMPILE ...` or `% BIBLIOGRAPHY ...` comments pointing to unresolved references or missing BibTeX keys.
