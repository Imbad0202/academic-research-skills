# Module: Grammar Analysis

**Trigger**: grammar, proofread, article usage, tense, subject-verb agreement

**Purpose**: Run a lightweight, rule-based grammar pass on visible prose from an existing LaTeX/Typst document.

## Commands

```bash
uv run python -B scripts/analyze_grammar.py main.tex
uv run python -B scripts/analyze_grammar.py main.tex --section introduction
```

## Raw Script Output

The script emits reviewer-style comment blocks such as:

```latex
% GRAMMAR (Line 23) [Severity: Major] [Priority: P1]: Rule hit: \bwe propose method\b
% Original: We propose method for time series forecasting.
% Revised:  we propose a method for time series forecasting.
% Rationale: Grammar: Article missing before singular count noun.
```

## Skill-Layer Response

- Keep the final answer source-aware and concise.
- Preserve equations, citations, labels, and macros.
- Summarize the raw findings as LaTeX-friendly review comments instead of switching to a separate table format.
