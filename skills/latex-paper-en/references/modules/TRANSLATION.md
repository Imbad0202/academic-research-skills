# Module: Translation (Chinese -> English)

**Trigger**: translate, Chinese to English, bilingual polishing, terminology alignment

**Purpose**: Translate Chinese technical prose into academic English while keeping LaTeX commands and math segments intact.

## Commands

```bash
uv run python -B scripts/translate_academic.py "本文提出了一种基于Transformer的方法" --domain deep-learning
uv run python -B scripts/translate_academic.py input_zh.txt --domain industrial-control --output translation_report.md
```

## Raw Script Output

The script returns three sections:
- terminology confirmation table
- translation draft
- ambiguity notes that may need manual confirmation

Protected fragments such as `\cite{...}`, `\ref{...}`, and `$...$` should remain verbatim in the translation draft.

## Skill-Layer Response

- Report the translated prose plus any ambiguity notes.
- Do not edit or normalize LaTeX fragments unless the user explicitly asks.
- If terminology is still ambiguous, surface the uncertainty instead of silently guessing.

Reference: [TERMINOLOGY.md](../TERMINOLOGY.md), [TRANSLATION_GUIDE.md](../TRANSLATION_GUIDE.md)
