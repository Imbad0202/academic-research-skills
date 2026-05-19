# Example: Grammar And Logic Review

User request:
Check the introduction and related work sections for grammar, sentence length, and argument flow, but do not touch equations or citations.

Recommended module sequence:
1. `grammar`
2. `sentences`
3. `logic`

Commands:
```bash
uv run python -B $SKILL_DIR/scripts/analyze_grammar.py main.tex --section introduction
uv run python -B $SKILL_DIR/scripts/analyze_sentences.py main.tex --section related
uv run python -B $SKILL_DIR/scripts/analyze_logic.py main.tex --section related
```

Expected output:
- LaTeX comment findings grouped by module.
- A short explanation of whether the issue is grammatical, readability-related, or logical.
