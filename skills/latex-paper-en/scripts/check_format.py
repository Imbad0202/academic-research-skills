#!/usr/bin/env python3
"""
LaTeX Format Checker - chktex wrapper with enhanced reporting

Usage:
    uv run python -B check_format.py main.tex
    uv run python -B check_format.py main.tex --strict
    uv run python -B check_format.py main.tex --config .chktexrc
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


class FormatChecker:
    """ChkTeX wrapper with enhanced error reporting."""

    # Warning levels
    LEVEL_ERROR = "ERROR"
    LEVEL_WARNING = "WARNING"
    LEVEL_INFO = "INFO"

    # Common warning patterns to categorize
    CATEGORIES = {
        "spacing": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
        "punctuation": [14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
        "parentheses": [24, 25, 26, 27, 28, 29, 30],
        "quotation": [31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
        "ellipsis": [41, 42, 43, 44, 45, 46],
    }

    def __init__(self, tex_file: str, config: Optional[str] = None):
        self.tex_file = Path(tex_file).resolve()
        self.work_dir = self.tex_file.parent
        self.config = config

    def _check_chktex(self) -> tuple[bool, str]:
        """Check if chktex is available."""
        if shutil.which("chktex"):
            return True, "chktex is available"
        return (
            False,
            "chktex not found. Install with: apt-get install chktex (Linux) or via TeX Live/MiKTeX",
        )

    def check(self, strict: bool = False) -> dict:
        """
        Run chktex on the document.

        Args:
            strict: Enable strict checking mode

        Returns:
            Dict with check results
        """
        ok, msg = self._check_chktex()
        if not ok:
            return {"status": "UNAVAILABLE", "message": msg, "issues": [], "fallback": True}

        # Build command
        cmd = ["chktex"]

        # Verbosity level
        if strict:
            cmd.extend(["-v3"])  # More warnings
        else:
            cmd.extend(["-v0", "-q"])  # Quiet mode

        # Config file
        if self.config:
            cmd.extend(["-l", self.config])

        # Add input file
        cmd.append(str(self.tex_file))

        try:
            result = subprocess.run(
                cmd,
                cwd=self.work_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            issues = self._parse_output(result.stdout + result.stderr)

            return {
                "status": "PASS" if not issues else "WARNING",
                "message": f"Found {len(issues)} issues",
                "issues": issues,
                "fallback": False,
            }

        except Exception as e:
            return {"status": "ERROR", "message": str(e), "issues": [], "fallback": False}

    def _parse_output(self, output: str) -> list[dict]:
        """Parse chktex output into structured format."""
        issues = []
        # Pattern: filename:line:col: Warning N: message
        pattern = r"(.+?):(\d+):(\d+):\s*(Warning|Error)\s*(\d+):\s*(.+)"

        for line in output.split("\n"):
            match = re.match(pattern, line.strip())
            if match:
                issues.append(
                    {
                        "file": match.group(1),
                        "line": int(match.group(2)),
                        "column": int(match.group(3)),
                        "level": match.group(4).upper(),
                        "code": int(match.group(5)),
                        "message": match.group(6),
                        "category": self._categorize(int(match.group(5))),
                    }
                )

        return issues

    def _categorize(self, code: int) -> str:
        """Categorize warning by code."""
        for category, codes in self.CATEGORIES.items():
            if code in codes:
                return category
        return "other"

    def generate_report(self, result: dict) -> str:
        """Generate human-readable report."""
        lines = []
        lines.append("=" * 60)
        lines.append("LaTeX Format Check Report")
        lines.append("=" * 60)
        lines.append(f"File: {self.tex_file}")
        lines.append(f"Status: {result['status']}")
        lines.append(f"Message: {result['message']}")

        if result.get("fallback"):
            lines.append("")
            lines.append("[FALLBACK MODE] chktex not available")
            lines.append("Install chktex for detailed format checking")
            return "\n".join(lines)

        if result["issues"]:
            lines.append("")
            lines.append("-" * 60)
            lines.append("Issues Found:")
            lines.append("-" * 60)

            # Group by category
            by_category = {}
            for issue in result["issues"]:
                cat = issue["category"]
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(issue)

            for category, issues in sorted(by_category.items()):
                lines.append(f"\n[{category.upper()}] ({len(issues)} issues)")
                for issue in issues[:5]:  # Limit to 5 per category
                    lines.append(f"  Line {issue['line']}: {issue['message']}")
                if len(issues) > 5:
                    lines.append(f"  ... and {len(issues) - 5} more")

        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="LaTeX Format Checker - chktex wrapper")
    parser.add_argument("tex_file", help=".tex file to check")
    parser.add_argument("--strict", "-s", action="store_true", help="Enable strict checking mode")
    parser.add_argument("--config", "-c", help="Path to .chktexrc config file")
    parser.add_argument("--json", "-j", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    # Validate input
    if not Path(args.tex_file).exists():
        print(f"[ERROR] File not found: {args.tex_file}")
        sys.exit(1)

    # Run check
    checker = FormatChecker(args.tex_file, args.config)
    result = checker.check(strict=args.strict)

    # Output
    if args.json:
        import json

        print(json.dumps(result, indent=2))
    else:
        print(checker.generate_report(result))

    # Exit code
    if result["status"] == "ERROR":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
