#!/usr/bin/env python3
"""
Typst Compilation Script - Fast compilation for Typst documents

Usage:
    uv run python compile.py main.typ                    # Compile once
    uv run python compile.py main.typ --watch            # Watch mode (auto-recompile)
    uv run python compile.py main.typ --format png       # Export as PNG
    uv run python compile.py main.typ --output out.pdf   # Custom output name
    uv run python compile.py main.typ --font-path ./fonts # Custom font directory

Features:
    - Fast compilation (milliseconds)
    - Watch mode for live preview
    - Multiple output formats (PDF, PNG, SVG)
    - Custom font support
    - Automatic error reporting
"""

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


class TypstCompiler:
    """Unified Typst compilation with multiple output formats."""

    SUPPORTED_FORMATS = ["pdf", "png", "svg"]

    def __init__(self, typ_file: str):
        self.typ_file = Path(typ_file).resolve()
        self.work_dir = self.typ_file.parent

    def _check_typst(self) -> tuple[bool, str]:
        """Check if Typst is installed."""
        if not shutil.which("typst"):
            return False, (
                "Typst not found. Install it using:\n"
                "  - Cargo: cargo install typst-cli\n"
                "  - Homebrew (macOS): brew install typst\n"
                "  - Package manager (Linux): check your distro's package manager\n"
                "  - Download: https://github.com/typst/typst/releases"
            )
        return True, "Typst is available"

    def compile(
        self,
        output: Optional[str] = None,
        format: str = "pdf",
        font_path: Optional[str] = None,
        watch: bool = False,
    ) -> int:
        """
        Compile the Typst document.

        Args:
            output: Output file path (optional)
            format: Output format (pdf, png, svg)
            font_path: Custom font directory
            watch: Enable watch mode for live preview

        Returns:
            Exit code (0 for success)
        """
        # Check if Typst is installed
        ok, msg = self._check_typst()
        if not ok:
            print(f"[ERROR] {msg}")
            return 1

        # Validate format
        if format not in self.SUPPORTED_FORMATS:
            print(f"[ERROR] Unsupported format: {format}")
            print(f"[INFO] Supported formats: {', '.join(self.SUPPORTED_FORMATS)}")
            return 1

        # Build command
        if watch:
            cmd = ["typst", "watch"]
            print(f"[INFO] Watch mode enabled for {self.typ_file.name}")
            print("[INFO] File will be recompiled automatically on changes")
            print("[INFO] Press Ctrl+C to stop")
        else:
            cmd = ["typst", "compile"]
            print(f"[INFO] Compiling {self.typ_file.name}")

        # Add input file
        cmd.append(str(self.typ_file))

        # Add output file if specified
        if output:
            cmd.append(output)
        elif not watch:
            # Default output name
            default_output = self.typ_file.with_suffix(f".{format}")
            cmd.append(str(default_output))

        # Add format option (only for compile, not watch)
        if not watch and format != "pdf":
            cmd.insert(2, "--format")
            cmd.insert(3, format)

        # Add font path if specified
        if font_path:
            cmd.extend(["--font-path", font_path])

        print(f"[INFO] Working directory: {self.work_dir}")
        print(f"[INFO] Command: {' '.join(cmd)}")

        # Run compilation
        try:
            start_time = time.time()
            result = subprocess.run(
                cmd,
                cwd=self.work_dir,
                capture_output=False,
            )
            elapsed = time.time() - start_time

            if result.returncode == 0:
                if not watch:
                    output_file = output or self.typ_file.with_suffix(f".{format}")
                    print(f"\n[SUCCESS] Output generated: {output_file}")
                    print(f"[INFO] Compilation time: {elapsed:.3f}s")
            else:
                print(f"\n[ERROR] Compilation failed with exit code {result.returncode}")

            return result.returncode

        except KeyboardInterrupt:
            print("\n[INFO] Compilation stopped by user")
            return 0
        except Exception as e:
            print(f"[ERROR] {e}")
            return 1

    def list_fonts(self) -> int:
        """List available fonts in the system."""
        ok, msg = self._check_typst()
        if not ok:
            print(f"[ERROR] {msg}")
            return 1

        print("[INFO] Listing available fonts...")
        try:
            result = subprocess.run(
                ["typst", "fonts"],
                cwd=self.work_dir,
                capture_output=False,
            )
            return result.returncode
        except Exception as e:
            print(f"[ERROR] {e}")
            return 1

    def query(self, selector: str) -> int:
        """Query document metadata."""
        ok, msg = self._check_typst()
        if not ok:
            print(f"[ERROR] {msg}")
            return 1

        print(f"[INFO] Querying: {selector}")
        try:
            result = subprocess.run(
                ["typst", "query", str(self.typ_file), selector],
                cwd=self.work_dir,
                capture_output=False,
            )
            return result.returncode
        except Exception as e:
            print(f"[ERROR] {e}")
            return 1


def main():
    parser = argparse.ArgumentParser(
        description="Typst Compilation Script - Fast compilation for Typst documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run python compile.py main.typ                        # Compile to PDF
  uv run python compile.py main.typ --watch                # Watch mode
  uv run python compile.py main.typ --format png           # Export as PNG
  uv run python compile.py main.typ --output paper.pdf     # Custom output name
  uv run python compile.py main.typ --font-path ./fonts    # Custom fonts
  uv run python compile.py main.typ --list-fonts           # List available fonts

Output Formats:
  pdf    Portable Document Format (default)
  png    Portable Network Graphics (raster image)
  svg    Scalable Vector Graphics (vector image)

Installation:
  - Cargo: cargo install typst-cli
  - Homebrew (macOS): brew install typst
  - Package manager (Linux): check your distro
  - Download: https://github.com/typst/typst/releases
        """,
    )
    parser.add_argument("typ_file", help="Main .typ file to compile")
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: same name as input with appropriate extension)",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["pdf", "png", "svg"],
        default="pdf",
        help="Output format (default: pdf)",
    )
    parser.add_argument("--font-path", help="Custom font directory")
    parser.add_argument(
        "--watch",
        "-w",
        action="store_true",
        help="Enable watch mode (auto-recompile on file changes)",
    )
    parser.add_argument(
        "--list-fonts", action="store_true", help="List available fonts in the system"
    )
    parser.add_argument("--query", "-q", help='Query document metadata (e.g., "<heading>")')

    args = parser.parse_args()

    # Validate input file
    typ_path = Path(args.typ_file)
    if not typ_path.exists():
        print(f"[ERROR] File not found: {args.typ_file}")
        sys.exit(1)

    if typ_path.suffix != ".typ":
        print(f"[WARNING] File does not have .typ extension: {args.typ_file}")

    # Create compiler instance
    compiler = TypstCompiler(args.typ_file)

    # Execute requested action
    if args.list_fonts:
        sys.exit(compiler.list_fonts())
    elif args.query:
        sys.exit(compiler.query(args.query))
    else:
        sys.exit(
            compiler.compile(
                output=args.output, format=args.format, font_path=args.font_path, watch=args.watch
            )
        )


if __name__ == "__main__":
    main()
