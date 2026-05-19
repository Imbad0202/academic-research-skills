# Example: Compact Query Search

## User Prompt

`Search references.bib for Cheng papers after 2024 on Mamba forecasting and return both LaTeX and Typst citations.`

## Recommended Module

`query`

## Search Mapping

- topic query: `mamba forecasting`
- author filter: `Cheng`
- year filter: `year>=2024`
- inferred field: `has:code`
- citation mode: `cite:both`
- result limit: `5`

## Command

```bash
uv run python -B $SKILL_DIR/scripts/search_bib.py --bib references.bib --query 'mamba forecasting author:Cheng year>=2024 has:code cite:both limit:5'
```

## Expected Output

- JSON `meta.applied_filters` shows the interpreted author, year, and `has` filters.
- Each returned entry includes bibliographic fields and both LaTeX and Typst snippets.
- If there are no matches, the response suggests which filters to relax first.
