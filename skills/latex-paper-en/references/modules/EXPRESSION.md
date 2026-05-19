# Module: Expression Restructuring

**Trigger**: academic tone, 学术表达, improve writing, weak verbs

Weak verb replacements:
- use → employ, utilize, leverage
- get → obtain, achieve, acquire
- make → construct, develop, generate
- show → demonstrate, illustrate, indicate

```bash
uv run python -B scripts/improve_expression.py main.tex
uv run python -B scripts/improve_expression.py main.tex --section related
```

Output format:
```latex
% EXPRESSION (Line 23) [Severity: Minor] [Priority: P2]: Improve academic tone
% Original: We use machine learning to get better results.
% Revised: We employ machine learning to achieve superior performance.
% Rationale: Replace weak verbs with academic alternatives
```

Style guide: [STYLE_GUIDE.md](../references/STYLE_GUIDE.md)

