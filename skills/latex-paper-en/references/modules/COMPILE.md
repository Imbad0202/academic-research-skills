# Module: Compile

**Trigger**: compile, 编译, build, pdflatex, xelatex

**Default Behavior**: Uses `latexmk` which automatically handles all dependencies (bibtex/biber, cross-references, indexes) and determines the optimal number of compilation passes. This is the recommended approach for most use cases.

**Tools** (matching VS Code LaTeX Workshop):
| Tool | Command | Args |
|------|---------|------|
| xelatex | `xelatex` | `-synctex=1 -interaction=nonstopmode -file-line-error` |
| pdflatex | `pdflatex` | `-synctex=1 -interaction=nonstopmode -file-line-error` |
| latexmk | `latexmk` | `-synctex=1 -interaction=nonstopmode -file-line-error -pdf -outdir=%OUTDIR%` |
| bibtex | `bibtex` | `%DOCFILE%` |
| biber | `biber` | `%DOCFILE%` |

**Recipes**:
| Recipe | Steps | Use Case |
|--------|-------|----------|
| latexmk | latexmk (auto) | **DEFAULT** - Auto-handles all dependencies |
| PDFLaTeX | pdflatex | Quick single-pass build |
| XeLaTeX | xelatex | Quick single-pass build |
| pdflatex -> bibtex -> pdflatex*2 | pdflatex → bibtex → pdflatex → pdflatex | Traditional BibTeX workflow |
| pdflatex -> biber -> pdflatex*2 | pdflatex → biber → pdflatex → pdflatex | Modern biblatex (recommended for new projects) |
| xelatex -> bibtex -> xelatex*2 | xelatex → bibtex → xelatex → xelatex | Chinese/Unicode + BibTeX |
| xelatex -> biber -> xelatex*2 | xelatex → biber → xelatex → xelatex | Chinese/Unicode + biblatex |

**Usage**:
```bash
# Default: latexmk auto-handles all dependencies (recommended)
uv run python -B scripts/compile.py main.tex                          # Auto-detect compiler + latexmk

# Single-pass compilation (quick builds)
uv run python -B scripts/compile.py main.tex --recipe pdflatex        # PDFLaTeX only
uv run python -B scripts/compile.py main.tex --recipe xelatex         # XeLaTeX only

# Explicit bibliography workflows (when you need control)
uv run python -B scripts/compile.py main.tex --recipe pdflatex-bibtex # Traditional BibTeX
uv run python -B scripts/compile.py main.tex --recipe pdflatex-biber  # Modern biblatex (recommended)
uv run python -B scripts/compile.py main.tex --recipe xelatex-bibtex  # XeLaTeX + BibTeX
uv run python -B scripts/compile.py main.tex --recipe xelatex-biber   # XeLaTeX + biblatex

# With output directory
uv run python -B scripts/compile.py main.tex --outdir build

# Force detected-compiler biber workflow
uv run python -B scripts/compile.py main.tex --biber

# Utilities
uv run python -B scripts/compile.py main.tex --watch                  # Watch mode
uv run python -B scripts/compile.py main.tex --clean                  # Clean aux files
uv run python -B scripts/compile.py main.tex --clean-all              # Clean all (incl. PDF)
```

**Auto-detection**: Script detects Chinese content (ctex, xeCJK, Chinese chars) and auto-selects xelatex.

