---
description: Validate all citations in a paper against a bibliography file.
model: sonnet
---

# `/ars-citation-audit`

**Purpose**: Scan the generated manuscript for citation keys, compare them with the provided bibliography (e.g., `references.bib`), and report missing or unused entries.

**Usage**:
```
/ars-citation-audit --bib <path/to/references.bib>
```
- `--bib` – path to the bibliography file (BibTeX, CSL‑JSON, or plain text).
- `--strict` – fail the command if any missing citations are found.

**Behaviour**:
- Parses the current document (or the last generated output) for citation markers like `[@key]`.
- Loads the bibliography and builds a set of valid keys.
- Returns a JSON report with:
  - `missing`: list of citation keys referenced but not present in the bibliography.
  - `unused`: list of bibliography entries never referenced.

**Related docs**: See `docs/ARCHITECTURE.md` for the citation‑validation stage.
