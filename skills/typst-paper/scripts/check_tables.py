#!/usr/bin/env python3
"""
Table Structure Checker for Typst - Validate three-line table compliance.

Usage:
    uv run python -B check_tables.py main.typ
    uv run python -B check_tables.py main.typ --fix-suggestions
    uv run python -B check_tables.py main.typ --json
"""

import argparse
import json
import re
import sys
from pathlib import Path


class TableChecker:
    """Validate Typst tables against the three-line standard."""

    LEVEL_ERROR = "ERROR"
    LEVEL_WARNING = "WARNING"
    LEVEL_INFO = "INFO"

    def __init__(self, typ_file: str):
        self.typ_file = Path(typ_file).resolve()
        self.content = ""
        self.lines: list[str] = []
        self.issues: list[dict] = []

    def _load(self) -> bool:
        """Load the .typ file content."""
        if not self.typ_file.exists():
            self.issues.append(
                {
                    "line": 0,
                    "level": self.LEVEL_ERROR,
                    "priority": "P1",
                    "message": f"File not found: {self.typ_file}",
                    "category": "file",
                }
            )
            return False
        self.content = self.typ_file.read_text(encoding="utf-8", errors="replace")
        self.lines = self.content.split("\n")
        return True

    def check(self, fix_suggestions: bool = False) -> dict:
        """Run all table structure checks."""
        if not self._load():
            return self._result()

        tables = self._find_table_blocks()
        for table in tables:
            self._check_vertical_lines(table)
            self._check_hline_count(table)
            self._check_stroke_none(table)
            self._check_number_precision(table)

        if fix_suggestions:
            for issue in self.issues:
                issue["fix"] = self._suggest_fix(issue)

        return self._result()

    def _result(self) -> dict:
        if not self.issues:
            status = "PASS"
        elif any(i["level"] == self.LEVEL_ERROR for i in self.issues):
            status = "FAIL"
        else:
            status = "WARNING"

        return {
            "status": status,
            "file": str(self.typ_file),
            "table_count": len(self._find_table_blocks()),
            "issue_count": len(self.issues),
            "issues": self.issues,
        }

    def _find_table_blocks(self) -> list[dict]:
        """Find table() calls in the Typst source."""
        tables = []
        # Simple heuristic: find lines containing table( and track the block
        for i, line in enumerate(self.lines, 1):
            stripped = line.strip()
            # Skip comments
            if stripped.startswith("//"):
                continue
            if "table(" in stripped:
                # Find the extent of this table block
                block_lines = [line]
                depth = 0
                start = i
                for ch in stripped[stripped.index("table(") + 6 :]:
                    if ch == "(":
                        depth += 1
                    elif ch == ")":
                        if depth == 0:
                            break
                        depth -= 1

                # If not closed on same line, scan forward
                if depth >= 0 and stripped.count("(") > stripped.count(")"):
                    for j in range(i, min(i + 100, len(self.lines))):
                        block_lines.append(self.lines[j])
                        full = "\n".join(block_lines)
                        if full.count("(") <= full.count(")"):
                            break

                tables.append(
                    {
                        "start": start,
                        "end": start + len(block_lines) - 1,
                        "content": "\n".join(block_lines),
                    }
                )

        return tables

    def _check_vertical_lines(self, table: dict) -> None:
        """Check for table.vline() in the table."""
        content = table["content"]
        if "table.vline" in content:
            self.issues.append(
                {
                    "line": table["start"],
                    "level": self.LEVEL_ERROR,
                    "priority": "P1",
                    "message": "table.vline() detected. Three-line tables must not have vertical lines.",
                    "category": "vertical_lines",
                }
            )

    def _check_hline_count(self, table: dict) -> None:
        """Check for correct number of table.hline() calls."""
        content = table["content"]
        hline_count = len(re.findall(r"table\.hline", content))

        if hline_count == 0:
            self.issues.append(
                {
                    "line": table["start"],
                    "level": self.LEVEL_WARNING,
                    "priority": "P1",
                    "message": "No table.hline() found. A three-line table needs exactly 3 horizontal lines (top, mid, bottom).",
                    "category": "hline_missing",
                }
            )
        elif hline_count > 3:
            self.issues.append(
                {
                    "line": table["start"],
                    "level": self.LEVEL_WARNING,
                    "priority": "P2",
                    "message": f"Found {hline_count} table.hline() calls. A three-line table should have exactly 3.",
                    "category": "hline_excess",
                }
            )

    def _check_stroke_none(self, table: dict) -> None:
        """Check that the table has stroke: none to disable default borders."""
        content = table["content"]
        # Look for stroke: none in the table() call
        if "stroke:" in content and "stroke: none" not in content and "stroke:none" not in content:
            self.issues.append(
                {
                    "line": table["start"],
                    "level": self.LEVEL_WARNING,
                    "priority": "P1",
                    "message": "Table has a stroke setting but not 'stroke: none'. Set stroke: none and use table.hline() for three-line style.",
                    "category": "stroke",
                }
            )

    def _check_number_precision(self, table: dict) -> None:
        """Check for inconsistent decimal precision in table data."""
        content = table["content"]
        # Extract cell values: look for [number] patterns
        cells = re.findall(r"\[(\d+\.?\d*)\]", content)
        if len(cells) < 2:
            return

        decimals_seen: set[int] = set()
        for cell in cells:
            if "." in cell:
                decimals_seen.add(len(cell.split(".")[1]))

        if len(decimals_seen) > 1:
            self.issues.append(
                {
                    "line": table["start"],
                    "level": self.LEVEL_WARNING,
                    "priority": "P3",
                    "message": f"Inconsistent decimal precision: found {sorted(decimals_seen)} decimal places. Use consistent precision.",
                    "category": "precision",
                }
            )

    def _suggest_fix(self, issue: dict) -> str:
        cat = issue.get("category", "")
        if cat == "vertical_lines":
            return "Remove all table.vline() calls."
        if cat == "hline_missing":
            return "Add table.hline(stroke: 0.8pt) at top and bottom, table.hline(stroke: 0.5pt) after headers."
        if cat == "hline_excess":
            return "Keep only 3 table.hline() calls: top, after header, and bottom."
        if cat == "stroke":
            return "Set stroke: none on the table() call."
        if cat == "precision":
            return "Align all values to the same number of decimal places."
        return ""

    def generate_report(self, result: dict) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append("Table Structure Check Report (Typst)")
        lines.append("=" * 60)
        lines.append(f"File: {result['file']}")
        lines.append(f"Tables found: {result['table_count']}")
        lines.append(f"Status: {result['status']}")
        lines.append(f"Issues: {result['issue_count']}")

        if result["issues"]:
            lines.append("")
            lines.append("-" * 60)

            by_category: dict[str, list[dict]] = {}
            for issue in result["issues"]:
                cat = issue.get("category", "other")
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(issue)

            for category, issues in sorted(by_category.items()):
                lines.append(f"\n[{category.upper()}] ({len(issues)} issues)")
                for issue in issues:
                    prefix = f"  Line {issue['line']}" if issue["line"] else "  Global"
                    lines.append(f"{prefix}: [{issue['level']}] {issue['message']}")
                    if issue.get("fix"):
                        lines.append(f"    Fix: {issue['fix']}")

        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Table Structure Checker (Typst) - three-line table compliance"
    )
    parser.add_argument("typ_file", help=".typ file to check")
    parser.add_argument(
        "--fix-suggestions", "-f", action="store_true", help="Include fix suggestions"
    )
    parser.add_argument("--json", "-j", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    if not Path(args.typ_file).exists():
        print(f"[ERROR] File not found: {args.typ_file}")
        sys.exit(1)

    checker = TableChecker(args.typ_file)
    result = checker.check(fix_suggestions=args.fix_suggestions)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(checker.generate_report(result))

    sys.exit(1 if result["status"] == "FAIL" else 0)


if __name__ == "__main__":
    main()
