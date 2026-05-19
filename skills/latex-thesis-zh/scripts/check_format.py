#!/usr/bin/env python3
"""
LaTeX Format Checker (Chinese) - chktex wrapper with Chinese support

Usage:
    uv run python check_format.py main.tex
    uv run python check_format.py main.tex --strict
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


class FormatChecker:
    """ChkTeX wrapper with Chinese thesis specific checks."""

    # Chinese-specific checks (in addition to chktex)
    CHINESE_CHECKS = {
        "mixed_punctuation": {
            "pattern": r"[\u4e00-\u9fff][,.:;!?]|[,.:;!?][\u4e00-\u9fff]",
            "message": "Mixed Chinese/English punctuation detected",
            "severity": "warning",
        },
        "missing_space_after_cite": {
            "pattern": r"\\cite\{[^}]+\}[\u4e00-\u9fff]",
            "message": "Missing space after \\cite before Chinese text",
            "severity": "info",
        },
        "oral_expression": {
            "pattern": r"我们|你们|很多|一些|非常|特别",
            "message": "Potential oral expression in academic writing",
            "severity": "warning",
        },
    }

    def __init__(self, tex_file: str, config: Optional[str] = None):
        self.tex_file = Path(tex_file).resolve()
        self.work_dir = self.tex_file.parent
        self.config = config

    def _check_chktex(self) -> tuple[bool, str]:
        """Check if chktex is available."""
        if shutil.which("chktex"):
            return True, "chktex is available"
        return False, "chktex not found"

    def check(self, strict: bool = False) -> dict:
        """Run format checks including Chinese-specific ones."""
        all_issues = []

        # Run chktex if available
        ok, msg = self._check_chktex()
        if ok:
            chktex_issues = self._run_chktex(strict)
            all_issues.extend(chktex_issues)

        # Run Chinese-specific checks
        chinese_issues = self._run_chinese_checks()
        all_issues.extend(chinese_issues)

        return {
            "status": "PASS" if not all_issues else "WARNING",
            "chktex_available": ok,
            "issues": all_issues,
            "total": len(all_issues),
        }

    def _run_chktex(self, strict: bool) -> list[dict]:
        """Run chktex and parse output."""
        cmd = ["chktex"]
        if strict:
            cmd.extend(["-v3"])
        else:
            cmd.extend(["-v0", "-q"])
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
            return self._parse_chktex_output(result.stdout + result.stderr)
        except Exception:
            return []

    def _parse_chktex_output(self, output: str) -> list[dict]:
        """Parse chktex output."""
        issues = []
        pattern = r"(.+?):(\d+):(\d+):\s*(Warning|Error)\s*(\d+):\s*(.+)"

        for line in output.split("\n"):
            match = re.match(pattern, line.strip())
            if match:
                issues.append(
                    {
                        "source": "chktex",
                        "file": match.group(1),
                        "line": int(match.group(2)),
                        "column": int(match.group(3)),
                        "severity": match.group(4).lower(),
                        "code": int(match.group(5)),
                        "message": match.group(6),
                    }
                )

        return issues

    def _run_chinese_checks(self) -> list[dict]:
        """Run Chinese-specific checks."""
        issues = []

        try:
            content = self.tex_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return issues

        lines = content.split("\n")

        for check_name, check_info in self.CHINESE_CHECKS.items():
            pattern = check_info["pattern"]

            for i, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith("%"):
                    continue

                for match in re.finditer(pattern, line):
                    issues.append(
                        {
                            "source": "chinese_check",
                            "file": str(self.tex_file.name),
                            "line": i,
                            "column": match.start() + 1,
                            "severity": check_info["severity"],
                            "code": check_name,
                            "message": check_info["message"],
                            "matched": match.group(),
                        }
                    )

        return issues

    def generate_report(self, result: dict) -> str:
        """Generate human-readable report."""
        lines = []
        lines.append("=" * 60)
        lines.append("LaTeX Format Check Report (Chinese Thesis)")
        lines.append("=" * 60)
        lines.append(f"File: {self.tex_file}")
        lines.append(f"Status: {result['status']}")
        lines.append(f"ChkTeX: {'Available' if result['chktex_available'] else 'Not Available'}")
        lines.append(f"Total Issues: {result['total']}")

        if result["issues"]:
            lines.append("")
            lines.append("-" * 60)
            lines.append("Issues:")
            lines.append("-" * 60)

            # Group by source
            by_source = {}
            for issue in result["issues"]:
                source = issue["source"]
                if source not in by_source:
                    by_source[source] = []
                by_source[source].append(issue)

            for source, issues in by_source.items():
                lines.append(f"\n[{source.upper()}] ({len(issues)} issues)")
                for issue in issues[:10]:
                    sev = issue["severity"].upper()
                    lines.append(f"  [{sev}] Line {issue['line']}: {issue['message']}")
                if len(issues) > 10:
                    lines.append(f"  ... and {len(issues) - 10} more")

        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="LaTeX Format Checker (Chinese Thesis)")
    parser.add_argument("tex_file", help=".tex file to check")
    parser.add_argument("--strict", "-s", action="store_true", help="Enable strict checking")
    parser.add_argument("--json", "-j", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    if not Path(args.tex_file).exists():
        print(f"[ERROR] File not found: {args.tex_file}")
        sys.exit(1)

    checker = FormatChecker(args.tex_file)
    result = checker.check(strict=args.strict)

    if args.json:
        import json

        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(checker.generate_report(result))

    sys.exit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
