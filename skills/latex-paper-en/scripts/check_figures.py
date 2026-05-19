#!/usr/bin/env python3
"""
Figure Quality Checker for Academic Papers
Checks resolution (DPI), format, and sequence of figures.

Usage:
    uv run python -B check_figures.py main.tex
    uv run python -B check_figures.py main.tex --min-dpi 300
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

try:
    from PIL import Image
except ImportError:  # pragma: no cover - runtime fallback
    Image = None

try:
    from parsers import get_parser
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from parsers import get_parser


class FigureChecker:
    def __init__(self, file_path: Path, min_dpi: int = 300):
        self.file_path = file_path
        self.root_dir = file_path.parent
        self.min_dpi = min_dpi
        self.content = file_path.read_text(encoding="utf-8", errors="ignore")
        self.parser = get_parser(file_path)

        # Try to find graphics path in LaTeX
        self.graphics_paths = [self.root_dir]
        self._parse_graphics_path()

    def _parse_graphics_path(self):
        r"""Parse \graphicspath{{path1}{path2}} from LaTeX."""
        match = re.search(r"\\graphicspath\{(.*?)\}", self.content, re.DOTALL)
        if match:
            paths = re.findall(r"\{([^}]+)\}", match.group(1))
            for p in paths:
                full_path = self.root_dir / p.strip()
                if full_path.exists():
                    self.graphics_paths.append(full_path)

    def find_figures(self) -> list[dict]:
        """Find all figure inclusions."""
        figures = []
        lines = self.content.split("\n")

        # LaTeX pattern: \includegraphics[options]{path}
        latex_pattern = r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}"
        # Typst pattern: #figure(image("path", ...)) or image("path")
        typst_pattern = r'image\("([^"]+)"'

        pattern = typst_pattern if str(self.file_path).endswith(".typ") else latex_pattern

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith(self.parser.get_comment_prefix()):
                continue

            for match in re.finditer(pattern, line):
                rel_path = match.group(1)
                resolved_path = self._resolve_path(rel_path)

                figures.append(
                    {
                        "line": i,
                        "rel_path": rel_path,
                        "abs_path": resolved_path,
                        "status": "FOUND" if resolved_path else "MISSING",
                    }
                )
        return figures

    def _resolve_path(self, rel_path: str) -> Optional[Path]:
        """Resolve image path using graphics_paths."""
        # Clean path extensions if missing (common in LaTeX)
        extensions = ["", ".pdf", ".png", ".jpg", ".jpeg", ".eps"]

        for base_path in self.graphics_paths:
            # Try exact path
            candidate = base_path / rel_path
            if candidate.exists():
                return candidate

            # Try with extensions
            for ext in extensions:
                candidate_ext = base_path / (rel_path + ext)
                if candidate_ext.exists():
                    return candidate_ext

        return None

    def check_quality(self, figure: dict) -> list[str]:
        """Check quality of a single figure."""
        issues = []
        path = figure["abs_path"]

        if not path:
            return ["File not found"]

        ext = path.suffix.lower()

        # Format check
        if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
            issues.append(f"Raster format ({ext}) used. Prefer Vector (PDF/EPS).")

            # DPI check for raster images
            if Image is None:
                issues.append(
                    "Pillow not installed; skipped DPI analysis (install Pillow for DPI checks)."
                )
                return issues

            try:
                with Image.open(path) as img:
                    width, height = img.size
                    # Assume typical figure width of 3 inches if metadata missing
                    # This is a heuristic estimate
                    width / 3.0

                    # Try to get real DPI
                    info = img.info
                    if "dpi" in info:
                        dpi_x, dpi_y = info["dpi"]
                        if dpi_x < self.min_dpi or dpi_y < self.min_dpi:
                            issues.append(
                                f"Low DPI: {int(dpi_x)}x{int(dpi_y)} (Min: {self.min_dpi})"
                            )
                    else:
                        # Fallback heuristic
                        if width < 1000:  # Arbitrary threshold for "likely low res"
                            issues.append(f"Potential low resolution (Width: {width}px)")

            except Exception as e:
                issues.append(f"Cannot analyze image: {e}")

        return issues

    def run(self):
        print(f"Checking figures in {self.file_path}...")
        figures = self.find_figures()

        print(f"Found {len(figures)} figures.")
        print("-" * 60)

        issues_count = 0

        for fig in figures:
            if fig["status"] == "MISSING":
                print(f"[ERROR] Line {fig['line']}: Image not found: {fig['rel_path']}")
                issues_count += 1
                continue

            quality_issues = self.check_quality(fig)
            if quality_issues:
                print(f"[WARN]  Line {fig['line']}: {fig['rel_path']}")
                for issue in quality_issues:
                    print(f"        - {issue}")
                issues_count += 1
            else:
                print(f"[OK]    Line {fig['line']}: {fig['rel_path']}")

        print("-" * 60)
        if issues_count == 0:
            print("✅ All figures passed check.")
            sys.exit(0)
        else:
            print(f"⚠️ Found {issues_count} potential issues.")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Check figure quality")
    parser.add_argument("file", type=Path, help="Main file")
    parser.add_argument("--min-dpi", type=int, default=300, help="Minimum DPI for raster images")

    args = parser.parse_args()

    if not args.file.exists():
        print("File not found.")
        sys.exit(1)

    checker = FigureChecker(args.file, args.min_dpi)
    checker.run()


if __name__ == "__main__":
    main()
