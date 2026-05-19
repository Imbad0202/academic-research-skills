# LaTeX Compilation Guide

## Compiler Selection

### pdfLaTeX
- **Best for**: English papers, fast compilation
- **Limitations**: Poor CJK support, requires `CJKutf8` package
- **Command**: `latexmk -pdf main.tex`

### XeLaTeX (Recommended for Chinese)
- **Best for**: Chinese documents, Unicode support, system fonts
- **Packages**: `ctex`, `xeCJK`, `fontspec`
- **Command**: `latexmk -xelatex main.tex`

### LuaLaTeX
- **Best for**: Modern features, Lua scripting, complex typography
- **Note**: Actively maintained, recommended for future-proofing
- **Command**: `latexmk -lualatex main.tex`

## latexmk Configuration

Create `.latexmkrc` in project root:

```perl
# For XeLaTeX (Chinese documents)
$pdf_mode = 5;  # xelatex
$xelatex = 'xelatex -interaction=nonstopmode -shell-escape %O %S';

# For pdfLaTeX (English papers)
# $pdf_mode = 1;
# $pdflatex = 'pdflatex -interaction=nonstopmode -shell-escape %O %S';

# Bibliography
$bibtex_use = 2;
$biber = 'biber %O %S';

# Output directory (optional)
# $out_dir = 'build';

# Clean extensions
@generated_exts = (@generated_exts, 'synctex.gz', 'nav', 'snm', 'vrb');
```

## Common Issues

### Chinese Font Not Found
```latex
% Specify fonts explicitly
\setCJKmainfont{SimSun}[BoldFont=SimHei, ItalicFont=KaiTi]
\setCJKsansfont{SimHei}
\setCJKmonofont{FangSong}
```

### Missing Package
```bash
# TeX Live
tlmgr install <package-name>

# MiKTeX (auto-install on first use)
# Or use MiKTeX Console
```

### Bibliography Not Updating
```bash
# Force rebuild
latexmk -C main.tex  # Clean all
latexmk -xelatex main.tex  # Rebuild
```

## Watch Mode (Continuous Compilation)

```bash
# Auto-recompile on file changes
latexmk -xelatex -pvc main.tex

# With PDF viewer sync
latexmk -xelatex -pvc -view=pdf main.tex
```

## Cross-Platform Notes

### Windows
- Install MiKTeX or TeX Live
- Use PowerShell or CMD
- Path: Use forward slashes or escaped backslashes

### Linux
```bash
sudo apt-get install texlive-full latexmk
```

### macOS
```bash
brew install --cask mactex
# Or: brew install basictex
```
