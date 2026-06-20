---
description: Export the generated manuscript to a LaTeX .tex file.
model: sonnet
---

# `/ars-export-latex`

**Purpose**: Take the current manuscript (or the last generated output) and write it to a LaTeX file ready for compilation.

**Usage**:
```
/ars-export-latex --output <path/to/file.tex>
```
- `--output` – destination path for the .tex file (default `output.tex`).
- `--include-bibliography` – embed the bibliography section if present.

**Behaviour**:
- Retrieves the manuscript text from session state.
- Wraps it in a minimal LaTeX preamble (`\documentclass{article}` etc.).
- Writes the file to the specified location.
- Returns the absolute path of the created file.

**Related docs**: See `docs/ARCHITECTURE.md` for the export stage.
