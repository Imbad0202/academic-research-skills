# Compile Module Reference

Purpose: Diagnose and fix compilation issues in Chinese LaTeX thesis projects.

## Compiler Selection

| Compiler | Best For | Command |
|----------|----------|---------|
| XeLaTeX | Chinese documents, Unicode, system fonts | `latexmk -xelatex main.tex` |
| LuaLaTeX | Modern features, Lua scripting, future-proofing | `latexmk -lualatex main.tex` |
| pdfLaTeX | English-only papers (poor CJK support) | `latexmk -pdf main.tex` |

## latexmk Configuration

Create `.latexmkrc` in project root:
```perl
$pdf_mode = 5;  # xelatex
$xelatex = 'xelatex -interaction=nonstopmode -shell-escape %O %S';
$bibtex_use = 2;
$biber = 'biber %O %S';
```

## Common Issues

| Problem | Solution |
|---------|----------|
| Chinese font not found | Specify fonts: `\setCJKmainfont{SimSun}[BoldFont=SimHei]` |
| Missing package | `tlmgr install <package-name>` |
| Bibliography not updating | `latexmk -C main.tex && latexmk -xelatex main.tex` |

## Watch Mode

```bash
latexmk -xelatex -pvc main.tex  # auto-recompile on changes
```

> Full details: see [`../COMPILATION.md`](../COMPILATION.md)
