# Example: Compile And Format

User request:
Compile this Typst paper for IEEE-style review and tell me whether the layout looks obviously off.

Recommended module sequence:
1. `compile`
2. `format`

Commands:
```bash
uv run python $SKILL_DIR/scripts/compile.py main.typ
uv run python $SKILL_DIR/scripts/check_format.py main.typ --venue ieee
```

Expected output:
- Typst compilation result with the invoked command.
- `// FORMAT ...` findings about paper size, columns, headings, or citations.
