# Module: Tables

**Trigger**: table, 表格, 三线表, three-line, booktabs, tabular, data table, generate table, table format

## Commands

```bash
uv run python -B scripts/check_tables.py main.tex
uv run python -B scripts/check_tables.py main.tex --fix-suggestions
uv run python -B scripts/check_tables.py main.tex --json
uv run python -B scripts/generate_table.py data.csv --style booktabs --bilingual
uv run python -B scripts/generate_table.py data.json --style booktabs
```

## Details

**check_tables.py**: Scans all `table` / `table*` environments in the document. Checks:
- Three-line rule compliance (toprule / midrule / bottomrule only)
- Vertical line presence in column spec
- Caption position (must precede `\begin{tabular}`)
- Table note format ("Note." or "注：")
- Number precision consistency within columns
- `booktabs` package loaded in preamble

**generate_table.py**: Converts structured data (CSV or JSON) into publication-ready table code:
1. Markdown preview (stdout)
2. LaTeX `booktabs` code
3. Bilingual caption suggestion (if `--bilingual`)
4. Word conversion tip

Skill-layer response: convert script output into `% TABLES (Line N) [Severity] [Priority]: ...` findings.

See also: [TABLE_GUIDE.md](../TABLE_GUIDE.md) for the full three-line table specification.
