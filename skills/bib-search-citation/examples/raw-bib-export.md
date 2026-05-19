# Example: Raw BibTeX Export

## User Prompt

`Find the best TimeMachine match in references.bib and return one raw entry plus cite snippets.`

## Recommended Module

`query`

## Search Mapping

- topic query: `TimeMachine`
- raw export: `raw:true`
- citation mode: `cite:both`
- result limit: `1`

## Command

```bash
uv run python -B $SKILL_DIR/scripts/search_bib.py --bib references.bib --query 'TimeMachine raw:true cite:both limit:1'
```

## Expected Output

- The top match includes `raw_bib` exactly as parsed from the source file.
- The result includes LaTeX and Typst citation snippets.
- The answer does not rewrite, normalize, or invent missing metadata.
