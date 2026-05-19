#!/usr/bin/env python3
"""
LaTeX Compilation Script - Unified compiler for pdflatex/xelatex/lualatex

Default Behavior:
    Uses latexmk which automatically handles all dependencies (bibtex/biber,
    cross-references, indexes, glossaries) and determines the optimal number
    of compilation passes. This is the recommended approach for most use cases.

Usage:
    uv run python -B compile.py main.tex                       # Default: latexmk auto
    uv run python -B compile.py main.tex --compiler xelatex    # Explicit compiler
    uv run python -B compile.py main.tex --recipe pdflatex-bibtex  # Traditional BibTeX
    uv run python -B compile.py main.tex --recipe pdflatex-biber   # Modern biblatex
    uv run python -B compile.py main.tex --watch               # Continuous compilation
    uv run python -B compile.py main.tex --clean               # Clean auxiliary files

Recipes (matching VS Code LaTeX Workshop):
    latexmk          - LaTeXmk auto (DEFAULT - recommended)
    pdflatex         - PDFLaTeX single pass
    xelatex          - XeLaTeX single pass
    lualatex         - LuaLaTeX single pass
    pdflatex-bibtex  - pdflatex -> bibtex -> pdflatex*2 (traditional)
    pdflatex-biber   - pdflatex -> biber -> pdflatex*2 (modern biblatex)
    xelatex-bibtex   - xelatex -> bibtex -> xelatex*2
    xelatex-biber    - xelatex -> biber -> xelatex*2
    lualatex-bibtex  - lualatex -> bibtex -> lualatex*2
    lualatex-biber   - lualatex -> biber -> lualatex*2
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


class LaTeXCompiler:
    """Unified LaTeX compilation with multiple recipes."""

    COMPILERS = {"pdflatex", "xelatex", "lualatex"}

    # Default recipe: latexmk handles dependencies automatically (best practice)
    # latexmk auto-detects bibtex/biber needs and runs the correct number of passes
    DEFAULT_RECIPE = "latexmk"

    # Recipes matching VS Code LaTeX Workshop configuration
    # Recommended workflow:
    #   - latexmk (default): Auto-detect and handle all dependencies intelligently
    #   - pdflatex-bibtex: Traditional BibTeX workflow (legacy .bst styles)
    #   - pdflatex-biber: Modern biblatex + biber workflow (recommended for new projects)
    RECIPES = {
        # Single compilation (quick builds)
        "xelatex": ["xelatex"],
        "pdflatex": ["pdflatex"],
        "lualatex": ["lualatex"],
        "latexmk": ["latexmk"],  # Default: auto-handles bibtex/biber
        # Full workflows (explicit control over compilation steps)
        "xelatex-bibtex": ["xelatex", "bibtex", "xelatex", "xelatex"],
        "xelatex-biber": ["xelatex", "biber", "xelatex", "xelatex"],
        "pdflatex-bibtex": ["pdflatex", "bibtex", "pdflatex", "pdflatex"],
        "pdflatex-biber": ["pdflatex", "biber", "pdflatex", "pdflatex"],
        "lualatex-bibtex": ["lualatex", "bibtex", "lualatex", "lualatex"],
        "lualatex-biber": ["lualatex", "biber", "lualatex", "lualatex"],
    }

    # Patterns indicating Chinese content
    CHINESE_PATTERNS = [
        r"\\usepackage.*{ctex}",
        r"\\usepackage.*{xeCJK}",
        r"\\documentclass.*{ctexart}",
        r"\\documentclass.*{ctexbook}",
        r"\\documentclass.*{ctexrep}",
        r"\\documentclass.*{thuthesis}",
        r"\\documentclass.*{pkuthss}",
        r"\\documentclass.*{ustcthesis}",
        r"\\documentclass.*{fduthesis}",
        r"[\u4e00-\u9fff]",  # Chinese characters
    ]

    def __init__(
        self,
        tex_file: str,
        compiler: Optional[str] = None,
        recipe: Optional[str] = None,
        shell_escape: bool = False,
    ):
        self.tex_file = Path(tex_file).resolve()
        self.work_dir = self.tex_file.parent
        self.compiler = compiler or self._detect_compiler()
        self.recipe = recipe
        self.shell_escape = shell_escape

    def _detect_compiler(self) -> str:
        """Auto-detect appropriate compiler based on document content."""
        try:
            content = self.tex_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return "pdflatex"  # Default fallback

        # Check for Chinese content
        for pattern in self.CHINESE_PATTERNS:
            if re.search(pattern, content):
                print("[INFO] Detected Chinese content, using xelatex")
                return "xelatex"

        # Check for explicit engine specification
        if re.search(r"%\s*!TEX\s+program\s*=\s*xelatex", content, re.IGNORECASE):
            return "xelatex"
        if re.search(r"%\s*!TEX\s+program\s*=\s*lualatex", content, re.IGNORECASE):
            return "lualatex"
        if re.search(r"%\s*!TEX\s+program\s*=\s*pdflatex", content, re.IGNORECASE):
            return "pdflatex"

        # Check for fontspec (requires xelatex or lualatex)
        if re.search(r"\\usepackage.*{fontspec}", content):
            print("[INFO] Detected fontspec package, using xelatex")
            return "xelatex"

        return "pdflatex"

    def _check_tools_for_compiler(self) -> tuple[bool, str]:
        """Check tools required for latexmk-based compilation."""
        if not shutil.which("latexmk"):
            return False, "latexmk not found. Install TeX Live or MiKTeX."

        compiler_cmd = self.compiler
        if not shutil.which(compiler_cmd):
            return False, f"{compiler_cmd} not found. Install TeX Live or MiKTeX."

        return True, "All tools available"

    def _check_tools_for_recipe(self) -> tuple[bool, str]:
        """Check tools required by a recipe."""
        steps = self.RECIPES.get(self.recipe, [])
        required = []
        for step in steps:
            if step == "latexmk":
                required.append("latexmk")
            elif step in ("pdflatex", "xelatex", "lualatex", "bibtex", "biber"):
                required.append(step)

        for tool in dict.fromkeys(required):
            if not shutil.which(tool):
                return False, f"{tool} not found. Install TeX Live or MiKTeX."

        return True, "All tools available"

    def _latexmk_engine_args(self) -> list[str]:
        """Build latexmk engine args with optional shell-escape."""
        if self.compiler not in self.COMPILERS:
            return ["-pdf"]

        engine = self.compiler
        if self.shell_escape:
            engine = f"{engine} -shell-escape"

        if self.compiler == "pdflatex":
            return ["-pdf", f"-pdflatex={engine} %O %S"]
        if self.compiler == "xelatex":
            return ["-xelatex", "-pdfxe", f"-xelatex={engine} %O %S"]
        return ["-lualatex", "-pdflua", f"-lualatex={engine} %O %S"]

    def _maybe_warn_shell_escape(self) -> None:
        if self.shell_escape:
            print("[WARNING] Shell escape enabled. Only use with trusted sources.")

    def compile(
        self, watch: bool = False, biber: bool = False, outdir: Optional[str] = None
    ) -> int:
        """
        Compile the LaTeX document.

        Args:
            watch: Enable continuous compilation mode
            biber: Use biber instead of bibtex
            outdir: Output directory for generated files

        Returns:
            Exit code (0 for success)
        """
        effective_recipe = self.recipe
        if not effective_recipe and biber:
            effective_recipe = f"{self.compiler}-biber"
            if effective_recipe not in self.RECIPES:
                print(
                    f"[WARNING] Unsupported compiler for biber recipe: {self.compiler}. "
                    "Falling back to pdflatex-biber."
                )
                effective_recipe = "pdflatex-biber"
            print(f"[INFO] --biber enabled, forcing recipe: {effective_recipe}")

        # Check tools for the actual execution path
        if effective_recipe:
            self.recipe = effective_recipe
            ok, msg = self._check_tools_for_recipe()
        else:
            ok, msg = self._check_tools_for_compiler()
        if not ok:
            print(f"[ERROR] {msg}")
            return 1

        # If recipe is specified (or forced), use recipe-based compilation
        if self.recipe:
            return self._compile_with_recipe(outdir)

        print(f"[INFO] Compiling {self.tex_file.name} with {self.compiler}")
        print(f"[INFO] Working directory: {self.work_dir}")
        self._maybe_warn_shell_escape()

        # Build latexmk command
        cmd = ["latexmk"]

        # Add compiler-specific options
        cmd.extend(self._latexmk_engine_args())

        # Add common options
        cmd.extend(
            [
                "-interaction=nonstopmode",
                "-file-line-error",
                "-synctex=1",
            ]
        )

        # Optional output directory (default latexmk path)
        if outdir:
            cmd.append(f"-outdir={outdir}")

        # Watch mode
        if watch:
            cmd.append("-pvc")
            print("[INFO] Watch mode enabled. Press Ctrl+C to stop.")

        # Add input file
        cmd.append(str(self.tex_file))

        # Run compilation
        try:
            result = subprocess.run(
                cmd,
                cwd=self.work_dir,
                capture_output=False,
            )
            if result.returncode == 0:
                pdf_file = self.tex_file.with_suffix(".pdf")
                print(f"\n[SUCCESS] PDF generated: {pdf_file}")
            else:
                print(f"\n[ERROR] Compilation failed with exit code {result.returncode}")
            return result.returncode

        except KeyboardInterrupt:
            print("\n[INFO] Compilation stopped by user")
            return 0
        except Exception as e:
            print(f"[ERROR] {e}")
            return 1

    def _compile_with_recipe(self, outdir: Optional[str] = None) -> int:
        """Compile using a predefined recipe (VS Code LaTeX Workshop style)."""
        if self.recipe not in self.RECIPES:
            print(f"[ERROR] Unknown recipe: {self.recipe}")
            print(f"[INFO] Available recipes: {', '.join(self.RECIPES.keys())}")
            return 1

        steps = self.RECIPES[self.recipe]
        print(f"[INFO] Using recipe: {self.recipe}")
        print(f"[INFO] Steps: {' -> '.join(steps)}")
        print(f"[INFO] Working directory: {self.work_dir}")
        self._maybe_warn_shell_escape()

        tex_base = self.tex_file.stem

        for i, step in enumerate(steps, 1):
            print(f"\n[STEP {i}/{len(steps)}] Running {step}...")

            # Match VS Code LaTeX Workshop tool configurations exactly
            if step == "latexmk":
                cmd = [
                    "latexmk",
                    "-synctex=1",
                    "-interaction=nonstopmode",
                    "-file-line-error",
                    "-pdf",
                ]
                if self.shell_escape:
                    cmd.append("-shell-escape")
                if outdir:
                    cmd.append(f"-outdir={outdir}")
                cmd.append(str(self.tex_file))
            elif step in ("pdflatex", "xelatex"):
                cmd = [
                    step,
                    "-synctex=1",
                    "-interaction=nonstopmode",
                    "-file-line-error",
                ]
                if self.shell_escape:
                    cmd.append("-shell-escape")
                cmd.append(str(self.tex_file))
            elif step == "lualatex":
                cmd = [
                    "lualatex",
                    "-synctex=1",
                    "-interaction=nonstopmode",
                    "-file-line-error",
                ]
                if self.shell_escape:
                    cmd.append("-shell-escape")
                cmd.append(str(self.tex_file))
            elif step == "bibtex":
                cmd = ["bibtex", tex_base]
            elif step == "biber":
                cmd = ["biber", tex_base]
            else:
                print(f"[ERROR] Unknown step: {step}")
                return 1

            try:
                result = subprocess.run(
                    cmd,
                    cwd=self.work_dir,
                    capture_output=False,
                )
                if result.returncode != 0:
                    # bibtex/biber may return non-zero for warnings, continue anyway
                    if step not in ("bibtex", "biber"):
                        print(f"[ERROR] Step {step} failed with exit code {result.returncode}")
                        return result.returncode
                    else:
                        print(f"[WARNING] {step} returned {result.returncode}, continuing...")

            except FileNotFoundError:
                print(f"[ERROR] {step} not found. Please install it.")
                return 1
            except Exception as e:
                print(f"[ERROR] {e}")
                return 1

        pdf_file = self.tex_file.with_suffix(".pdf")
        if pdf_file.exists():
            print(f"\n[SUCCESS] PDF generated: {pdf_file}")
            return 0
        else:
            print(f"\n[ERROR] PDF not found: {pdf_file}")
            return 1

    def clean(self, full: bool = False) -> int:
        """
        Clean auxiliary files.

        Args:
            full: Also remove output PDF

        Returns:
            Exit code (0 for success)
        """
        print(f"[INFO] Cleaning auxiliary files in {self.work_dir}")

        cmd = ["latexmk", "-c"]
        if full:
            cmd = ["latexmk", "-C"]

        cmd.append(str(self.tex_file))

        try:
            result = subprocess.run(cmd, cwd=self.work_dir, capture_output=True)
            if result.returncode == 0:
                print("[SUCCESS] Auxiliary files cleaned")
            return result.returncode
        except Exception as e:
            print(f"[ERROR] {e}")
            return 1


def main():
    parser = argparse.ArgumentParser(
        description="LaTeX Compilation Script - Unified compiler for pdflatex/xelatex/lualatex",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Default Behavior:
  Uses latexmk which automatically handles all dependencies (bibtex/biber,
  cross-references, etc.) and determines the optimal number of compilation passes.
  This is the recommended approach for most use cases.

Recipes (matching VS Code LaTeX Workshop):
  latexmk          LaTeXmk auto (DEFAULT - recommended)
  pdflatex         PDFLaTeX single pass
  xelatex          XeLaTeX single pass
  lualatex         LuaLaTeX single pass
  pdflatex-bibtex  pdflatex -> bibtex -> pdflatex*2 (traditional workflow)
  pdflatex-biber   pdflatex -> biber -> pdflatex*2 (modern biblatex)
  xelatex-bibtex   xelatex -> bibtex -> xelatex*2
  xelatex-biber    xelatex -> biber -> xelatex*2
  lualatex-bibtex  lualatex -> bibtex -> lualatex*2
  lualatex-biber   lualatex -> biber -> lualatex*2

Examples:
  uv run python -B compile.py main.tex                        # Default: latexmk auto
  uv run python -B compile.py main.tex --recipe pdflatex-bibtex  # Traditional BibTeX
  uv run python -B compile.py main.tex --recipe pdflatex-biber   # Modern biblatex
  uv run python -B compile.py main.tex --biber               # Force detected-compiler biber flow
  uv run python -B compile.py main.tex --outdir build        # Set output directory (latexmk path)
  uv run python -B compile.py main.tex --watch                # Watch mode
        """,
    )
    parser.add_argument("tex_file", help="Main .tex file to compile")
    parser.add_argument(
        "--compiler",
        "-c",
        choices=["pdflatex", "xelatex", "lualatex"],
        help="Compiler to use (auto-detected if not specified)",
    )
    parser.add_argument(
        "--recipe",
        "-r",
        choices=[
            "xelatex",
            "pdflatex",
            "lualatex",
            "latexmk",
            "xelatex-bibtex",
            "xelatex-biber",
            "pdflatex-bibtex",
            "pdflatex-biber",
            "lualatex-bibtex",
            "lualatex-biber",
        ],
        help="Use predefined recipe (VS Code LaTeX Workshop style)",
    )
    parser.add_argument(
        "--watch", "-w", action="store_true", help="Enable continuous compilation (watch mode)"
    )
    parser.add_argument(
        "--biber",
        "-b",
        action="store_true",
        help="Force explicit <compiler>-biber recipe when --recipe is not provided",
    )
    parser.add_argument(
        "--shell-escape",
        action="store_true",
        help="Enable shell-escape (use with trusted sources only)",
    )
    parser.add_argument("--clean", action="store_true", help="Clean auxiliary files")
    parser.add_argument(
        "--clean-all", action="store_true", help="Clean all generated files including PDF"
    )
    parser.add_argument(
        "--outdir", "-o", help="Output directory for generated files (latexmk only)"
    )

    args = parser.parse_args()

    # Validate input file
    tex_path = Path(args.tex_file)
    if not tex_path.exists():
        print(f"[ERROR] File not found: {args.tex_file}")
        sys.exit(1)

    if tex_path.suffix != ".tex":
        print(f"[WARNING] File does not have .tex extension: {args.tex_file}")

    # Create compiler instance
    compiler = LaTeXCompiler(
        args.tex_file,
        args.compiler,
        args.recipe,
        shell_escape=args.shell_escape,
    )

    # Execute requested action
    if args.clean or args.clean_all:
        sys.exit(compiler.clean(full=args.clean_all))
    else:
        sys.exit(
            compiler.compile(
                watch=args.watch,
                biber=args.biber,
                outdir=args.outdir,
            )
        )


if __name__ == "__main__":
    main()
