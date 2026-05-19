#!/usr/bin/env python3
"""
LaTeX Compilation Script - 中文学位论文编译器 (xelatex/lualatex)

默认行为:
    使用 latexmk + XeLaTeX 自动处理所有依赖（bibtex/biber、交叉引用、
    索引、术语表），并自动决定最优编译次数。这是中文论文的推荐方案。

Usage:
    uv run python compile.py main.tex                       # 默认: latexmk + xelatex
    uv run python compile.py main.tex --compiler xelatex    # 显式指定编译器
    uv run python compile.py main.tex --recipe xelatex-bibtex  # 传统 BibTeX
    uv run python compile.py main.tex --recipe xelatex-biber   # 现代 biblatex
    uv run python compile.py main.tex --watch               # 监视模式
    uv run python compile.py main.tex --clean               # 清理辅助文件

Recipes (中文论文推荐 XeLaTeX/LuaLaTeX):
    latexmk          - LaTeXmk + XeLaTeX 自动处理 (默认 - 推荐)
    xelatex          - XeLaTeX 单次编译
    lualatex         - LuaLaTeX 单次编译
    xelatex-bibtex   - xelatex -> bibtex -> xelatex*2 (传统)
    xelatex-biber    - xelatex -> biber -> xelatex*2 (现代 biblatex)
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

    # Default recipe: latexmk with XeLaTeX for Chinese documents (best practice)
    # latexmk auto-detects bibtex/biber needs and runs the correct number of passes
    DEFAULT_RECIPE = "latexmk"

    # Recipes matching VS Code LaTeX Workshop configuration
    # Chinese thesis: XeLaTeX/LuaLaTeX recommended for proper CJK support
    # Recommended workflow:
    #   - latexmk (default): Auto-detect and handle all dependencies with XeLaTeX
    #   - xelatex-bibtex: Traditional BibTeX workflow (legacy .bst styles)
    #   - xelatex-biber: Modern biblatex + biber workflow (recommended for new theses)
    RECIPES = {
        # Single compilation (quick builds)
        "xelatex": ["xelatex"],
        "lualatex": ["lualatex"],
        "latexmk": ["latexmk-xelatex"],  # Default: XeLaTeX + auto-handles bibtex/biber
        # Full workflows (explicit control over compilation steps)
        "xelatex-bibtex": ["xelatex", "bibtex", "xelatex", "xelatex"],
        "xelatex-biber": ["xelatex", "biber", "xelatex", "xelatex"],
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
            if step == "latexmk-xelatex":
                required.extend(["latexmk", "xelatex"])
            elif step == "latexmk-lualatex":
                required.extend(["latexmk", "lualatex"])
            elif step in ("xelatex", "lualatex", "bibtex", "biber"):
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
        # Check tools
        if self.recipe:
            ok, msg = self._check_tools_for_recipe()
        else:
            ok, msg = self._check_tools_for_compiler()
        if not ok:
            print(f"[ERROR] {msg}")
            return 1

        # If recipe is specified, use recipe-based compilation
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

        # Biber support
        if biber:
            cmd.append("-bibtex")

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

            if step == "latexmk-xelatex":
                cmd = [
                    "latexmk",
                    "-xelatex",
                    "-interaction=nonstopmode",
                    "-synctex=1",
                    "-file-line-error",
                ]
                if self.shell_escape:
                    cmd.append("-shell-escape")
                if outdir:
                    cmd.append(f"-outdir={outdir}")
                cmd.append(str(self.tex_file))
            elif step == "latexmk-lualatex":
                cmd = [
                    "latexmk",
                    "-lualatex",
                    "-interaction=nonstopmode",
                    "-synctex=1",
                    "-file-line-error",
                ]
                if self.shell_escape:
                    cmd.append("-shell-escape")
                if outdir:
                    cmd.append(f"-outdir={outdir}")
                cmd.append(str(self.tex_file))
            elif step in ("xelatex", "lualatex"):
                cmd = [step, "-interaction=nonstopmode", "-synctex=1", str(self.tex_file)]
                if self.shell_escape:
                    cmd.insert(2, "-shell-escape")
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
        description="LaTeX 中文学位论文编译脚本 - 支持 xelatex/lualatex",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
默认行为:
  使用 latexmk + XeLaTeX 自动处理所有依赖（bibtex/biber、交叉引用等），
  并自动决定最优编译次数。这是中文论文的推荐方案。

Recipes (中文论文推荐 XeLaTeX):
  latexmk          LaTeXmk + XeLaTeX 自动处理 (默认 - 推荐)
  xelatex          XeLaTeX 单次编译
  lualatex         LuaLaTeX 单次编译
  xelatex-bibtex   xelatex -> bibtex -> xelatex*2 (传统 BibTeX)
  xelatex-biber    xelatex -> biber -> xelatex*2 (现代 biblatex)
  lualatex-bibtex  lualatex -> bibtex -> lualatex*2
  lualatex-biber   lualatex -> biber -> lualatex*2

Examples:
  uv run python compile.py main.tex                        # 默认: latexmk + xelatex
  uv run python compile.py main.tex --recipe xelatex-bibtex  # 传统 BibTeX
  uv run python compile.py main.tex --recipe xelatex-biber   # 现代 biblatex
  uv run python compile.py main.tex --watch                # 监视模式
        """,
    )
    parser.add_argument("tex_file", help="主 .tex 文件路径")
    parser.add_argument(
        "--compiler",
        "-c",
        choices=["pdflatex", "xelatex", "lualatex"],
        help="编译器 (未指定时自动检测，中文默认 xelatex)",
    )
    parser.add_argument(
        "--recipe",
        "-r",
        choices=[
            "xelatex",
            "lualatex",
            "latexmk",
            "xelatex-bibtex",
            "xelatex-biber",
            "lualatex-bibtex",
            "lualatex-biber",
        ],
        help="使用预定义编译配置 (中文推荐 XeLaTeX)",
    )
    parser.add_argument("--watch", "-w", action="store_true", help="启用监视模式 (持续编译)")
    parser.add_argument("--biber", "-b", action="store_true", help="使用 biber 处理参考文献")
    parser.add_argument(
        "--shell-escape",
        action="store_true",
        help="启用 shell-escape (仅用于可信源)",
    )
    parser.add_argument("--clean", action="store_true", help="清理辅助文件")
    parser.add_argument("--clean-all", action="store_true", help="清理所有生成文件 (含 PDF)")
    parser.add_argument("--outdir", "-o", help="输出目录 (仅 latexmk 配置支持)")

    args = parser.parse_args()

    # Validate input file
    tex_path = Path(args.tex_file)
    if not tex_path.exists():
        print(f"[ERROR] 文件不存在: {args.tex_file}")
        sys.exit(1)

    if tex_path.suffix != ".tex":
        print(f"[WARNING] 文件扩展名不是 .tex: {args.tex_file}")

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
