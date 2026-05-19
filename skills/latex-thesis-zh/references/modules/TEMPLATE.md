# Template Module Reference

Purpose: Detect and validate the university thesis template/class in use.

## Template Detection Workflow

1. **Scan document class**: Look for `\documentclass{thuthesis}`, `\documentclass{pkuthss}`, `\documentclass[...]{ctexbook}`, etc.
2. **Check package imports**: Identify `ctex`, `xeCJK`, `fontspec` and other template-specific packages.
3. **Match template**: Compare against known templates in `references/UNIVERSITIES/`.
4. **Report**: Output detected template name, version (if available), and any config warnings.

## Supported Templates

| Template | University | Document Class |
|----------|-----------|---------------|
| thuthesis | 清华大学 | `\documentclass{thuthesis}` |
| pkuthss | 北京大学 | `\documentclass{pkuthss}` |
| ctexbook (generic) | Various | `\documentclass[...]{ctexbook}` |

## Key Config Files

- `.latexmkrc` — compiler settings
- `*.cls` — template class file
- `*.cfg` — template configuration
- `refs.bib` / `references.bib` — bibliography database

## After Detection

Once the template is identified, load the corresponding university-specific rules from:
- `references/UNIVERSITIES/{university}.md` for per-university constraints
- `references/UNIVERSITIES/generic.md` as fallback for unknown templates

> See [`../UNIVERSITIES/`](../UNIVERSITIES/) for per-university rule files.
