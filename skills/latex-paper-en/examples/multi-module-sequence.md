# Example: Multi-Module Sequence

User request:
Check the introduction for grammar, sentence length, and logic, then review the experiments section for weak baselines and missing ablations.

Recommended module sequence:
1. `grammar`
2. `sentences`
3. `logic`
4. `experiment`

Commands:
```bash
uv run python -B $SKILL_DIR/scripts/analyze_grammar.py main.tex --section introduction
uv run python -B $SKILL_DIR/scripts/analyze_sentences.py main.tex --section introduction
uv run python -B $SKILL_DIR/scripts/analyze_logic.py main.tex --section introduction
uv run python -B $SKILL_DIR/scripts/analyze_experiment.py main.tex --section experiments
```

Expected output:
- Findings grouped by module instead of one mixed comment block.
- Clear separation between prose issues and experiment-review issues.
- Exact command and exit code reported if any module fails.
