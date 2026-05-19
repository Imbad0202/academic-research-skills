# Module: De-AI Editing

**Trigger**: deai, humanize, reduce AI traces, natural writing, tone cleanup

**Purpose**: Detect likely AI-writing traces in visible prose while preserving LaTeX structure and technical claims.

## Commands

```bash
uv run python -B scripts/deai_check.py main.tex --section introduction
uv run python -B scripts/deai_check.py main.tex --analyze
uv run python -B scripts/deai_batch.py main.tex --all-sections
```

## Raw Script Output

- `deai_check.py` emits section-level analysis, trace scores, and optional fix suggestions.
- `deai_batch.py` supports broader batch inspection across sections.

## Skill-Layer Response

- Treat the script output as analysis, not as permission to rewrite the paper by default.
- Return `% DE-AI ...` style findings or a short risk summary unless the user explicitly asks for source edits.
- Preserve `\cite{}`, `\ref{}`, `\label{}`, custom macros, and math environments.
- Never invent new claims, metrics, baselines, or references while smoothing the prose.

Reference: [DEAI_GUIDE.md](../DEAI_GUIDE.md)
