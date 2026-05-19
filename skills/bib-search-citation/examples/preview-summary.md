# Example: Preview Summary

## User Prompt

`Search my Zotero-exported library for photovoltaic forecasting entries, then show me a compact human-readable summary.`

## Recommended Module Sequence

1. `query`
2. `preview`

## Command

```bash
uv run python -B $SKILL_DIR/scripts/search_bib.py --bib references.bib --query 'photovoltaic forecasting cite:both limit:5' > results.json
uv run python -B $SKILL_DIR/scripts/preview_bib_search.py --input results.json
```

## Expected Output

- `search_bib.py` produces the machine-readable JSON source of truth.
- `preview_bib_search.py` renders a short summary without exposing raw BibTeX.
- The final answer keeps exact filtering/scoring claims tied to the JSON payload.
