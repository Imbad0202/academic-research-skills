# Module: Bibliography

**Trigger**: bib, bibliography, 参考文献, citation, reference format, citation style

## Commands

```bash
uv run python -B scripts/verify_bib.py references.bib
uv run python -B scripts/verify_bib.py references.bib --tex main.tex
uv run python -B scripts/verify_bib.py references.bib --standard gb7714
uv run python -B scripts/verify_bib.py references.bib --tex main.tex --json
uv run python -B scripts/verify_bib.py references.bib --style apa
uv run python -B scripts/verify_bib.py references.bib --style vancouver --tex main.tex
uv run python -B scripts/verify_bib.py references.bib --style nature
```

## Details
Checks: required fields, duplicate keys, missing citations, unused entries.
Style-specific checks (via `--style`): author count vs et al. threshold, page format (en dash), DOI requirements, style-specific required fields.
Key output fields: `missing_in_bib`, `unused_in_tex`.
Skill-layer response: convert the raw verification results into `% BIBLIOGRAPHY ...` style findings when presenting them to the user.

See also: [CITATION_VERIFICATION.md](../CITATION_VERIFICATION.md) for API-based verification.
See also: [CITATION_STYLES.md](../CITATION_STYLES.md) for IEEE/APA/Vancouver/Nature format rules.
See also: [JOURNAL_ABBREVIATIONS.md](../JOURNAL_ABBREVIATIONS.md) for ISO 4 journal name abbreviations.

