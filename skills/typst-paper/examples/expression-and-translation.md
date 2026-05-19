# Example: Expression And Translation

User request:
Polish the abstract in `main.typ`, tighten the wording, and help translate one Chinese paragraph into academic English.

Recommended module sequence:
1. `expression`
2. `translation`

Commands:
```bash
uv run python $SKILL_DIR/scripts/improve_expression.py main.typ --section abstract
uv run python $SKILL_DIR/scripts/translate_academic.py input_zh.txt --domain deep-learning
```

Expected output:
- Typst-safe wording suggestions.
- Translation guidance that keeps citations and Typst syntax intact.
