#!/usr/bin/env python3
"""
Table Structure Checker - Validate three-line table compliance in LaTeX documents.

Usage:
    uv run python -B check_tables.py main.tex
    uv run python -B check_tables.py main.tex --fix-suggestions
    uv run python -B check_tables.py main.tex --json
"""

import argparse
import json
import re
import sys
from pathlib import Path


class TableChecker:
    """Validate LaTeX tables against the three-line (booktabs) standard."""

    LEVEL_ERROR = "ERROR"
    LEVEL_WARNING = "WARNING"
    LEVEL_INFO = "INFO"

    # Booktabs commands that define valid three-line rules
    VALID_RULES = {r"\toprule", r"\midrule", r"\bottomrule"}

    # Forbidden rule commands inside tabular body
    FORBIDDEN_RULES = {r"\hline", r"\vline", r"\cline"}

    def __init__(self, tex_file: str):
        self.tex_file = Path(tex_file).resolve()
        self.content = ""
        self.lines: list[str] = []
        self.issues: list[dict] = []

    def _load(self) -> bool:
        """Load the .tex file content."""
        if not self.tex_file.exists():
            self.issues.append(
                {
                    "line": 0,
                    "level": self.LEVEL_ERROR,
                    "priority": "P1",
                    "message": f"File not found: {self.tex_file}",
                    "category": "file",
                }
            )
            return False
        self.content = self.tex_file.read_text(encoding="utf-8", errors="replace")
        self.lines = self.content.split("\n")
        return True

    def check(self, fix_suggestions: bool = False) -> dict:
        """Run all table structure checks."""
        if not self._load():
            return self._result()

        self._check_booktabs_loaded()
        tables = self._find_table_environments()

        for table in tables:
            self._check_vertical_lines(table)
            self._check_rule_commands(table)
            self._check_caption_position(table)
            self._check_table_notes(table)
            self._check_number_precision(table)

        if fix_suggestions:
            for issue in self.issues:
                issue["fix"] = self._suggest_fix(issue)

        return self._result()

    def _result(self) -> dict:
        """Build result dictionary."""
        if not self.issues:
            status = "PASS"
        elif any(i["level"] == self.LEVEL_ERROR for i in self.issues):
            status = "FAIL"
        else:
            status = "WARNING"

        return {
            "status": status,
            "file": str(self.tex_file),
            "table_count": len(self._find_table_environments()),
            "issue_count": len(self.issues),
            "issues": self.issues,
        }

    def _check_booktabs_loaded(self) -> None:
        """Check if booktabs package is loaded."""
        has_booktabs = False
        for line in self.lines:
            stripped = line.split("%")[0]  # Ignore comments
            if re.search(r"\\usepackage(\[[^\]]*\])?\{.*booktabs.*\}", stripped):
                has_booktabs = True
                break
        if not has_booktabs and re.search(r"\\begin\{table\*?\}", self.content):
            self.issues.append(
                {
                    "line": 0,
                    "level": self.LEVEL_WARNING,
                    "priority": "P2",
                    "message": "booktabs package not loaded. Add \\usepackage{booktabs} for professional three-line tables.",
                    "category": "package",
                }
            )

    def _find_table_environments(self) -> list[dict]:
        """Find all table/table* environments with their line ranges."""
        tables = []
        pattern = re.compile(r"\\begin\{(table\*?)\}")
        end_pattern = re.compile(r"\\end\{(table\*?)\}")

        stack: list[dict] = []
        for i, line in enumerate(self.lines, 1):
            stripped = line.split("%")[0]
            for m in pattern.finditer(stripped):
                stack.append({"env": m.group(1), "start": i, "start_col": m.start()})
            for _m in end_pattern.finditer(stripped):
                if stack:
                    entry = stack.pop()
                    entry["end"] = i
                    entry["content"] = "\n".join(self.lines[entry["start"] - 1 : i])
                    tables.append(entry)

        return tables

    def _check_vertical_lines(self, table: dict) -> None:
        """Check for vertical lines in column specifications."""
        content = table["content"]
        # Find tabular column spec: \begin{tabular}{|c|c|c|}
        col_specs = re.findall(r"\\begin\{tabular\*?\}(?:\{[^}]*\})?\{([^}]+)\}", content)
        for spec in col_specs:
            if "|" in spec:
                self.issues.append(
                    {
                        "line": table["start"],
                        "level": self.LEVEL_ERROR,
                        "priority": "P1",
                        "message": f"Vertical lines detected in column spec: {{{spec}}}. Three-line tables must not have vertical lines.",
                        "category": "vertical_lines",
                    }
                )

        # Also check for \vline
        for i, line in enumerate(self.lines[table["start"] - 1 : table["end"]], table["start"]):
            stripped = line.split("%")[0]
            if r"\vline" in stripped:
                self.issues.append(
                    {
                        "line": i,
                        "level": self.LEVEL_ERROR,
                        "priority": "P1",
                        "message": "\\vline detected. Three-line tables must not have vertical lines.",
                        "category": "vertical_lines",
                    }
                )

    def _check_rule_commands(self, table: dict) -> None:
        """Check for correct rule commands (booktabs vs hline)."""
        content = table["content"]

        # Find tabular body
        tabular_match = re.search(
            r"\\begin\{tabular\*?\}(?:\{[^}]*\})?\{[^}]+\}(.*?)\\end\{tabular\*?\}",
            content,
            re.DOTALL,
        )
        if not tabular_match:
            return

        tabular_body = tabular_match.group(1)

        # Count booktabs rules
        toprule_count = len(re.findall(r"\\toprule", tabular_body))
        midrule_count = len(re.findall(r"\\midrule", tabular_body))
        bottomrule_count = len(re.findall(r"\\bottomrule", tabular_body))

        # Check for forbidden rules
        for i, line in enumerate(self.lines[table["start"] - 1 : table["end"]], table["start"]):
            stripped = line.split("%")[0]
            if r"\hline" in stripped:
                self.issues.append(
                    {
                        "line": i,
                        "level": self.LEVEL_WARNING,
                        "priority": "P1",
                        "message": "\\hline detected. Use \\toprule, \\midrule, \\bottomrule (booktabs) instead.",
                        "category": "hline",
                    }
                )
            if re.search(r"\\cline\{[^}]+\}", stripped):
                self.issues.append(
                    {
                        "line": i,
                        "level": self.LEVEL_INFO,
                        "priority": "P3",
                        "message": "\\cline detected. Consider \\cmidrule (booktabs) for partial rules under sub-headers.",
                        "category": "hline",
                    }
                )

        # Validate three-line structure
        if toprule_count == 0 and midrule_count == 0 and bottomrule_count == 0:
            # No booktabs at all — check if using hline
            hline_count = len(re.findall(r"\\hline", tabular_body))
            if hline_count > 0:
                self.issues.append(
                    {
                        "line": table["start"],
                        "level": self.LEVEL_WARNING,
                        "priority": "P1",
                        "message": f"Table uses \\hline ({hline_count}x) instead of booktabs commands. Replace with \\toprule/\\midrule/\\bottomrule.",
                        "category": "booktabs_missing",
                    }
                )
        else:
            if toprule_count != 1:
                self.issues.append(
                    {
                        "line": table["start"],
                        "level": self.LEVEL_WARNING,
                        "priority": "P2",
                        "message": f"Expected exactly 1 \\toprule, found {toprule_count}.",
                        "category": "rule_count",
                    }
                )
            if bottomrule_count != 1:
                self.issues.append(
                    {
                        "line": table["start"],
                        "level": self.LEVEL_WARNING,
                        "priority": "P2",
                        "message": f"Expected exactly 1 \\bottomrule, found {bottomrule_count}.",
                        "category": "rule_count",
                    }
                )

    def _check_caption_position(self, table: dict) -> None:
        """Check that caption appears before tabular environment."""
        content = table["content"]

        caption_pos = -1
        tabular_pos = -1

        caption_match = re.search(r"\\caption", content)
        tabular_match = re.search(r"\\begin\{tabular\*?\}", content)

        if caption_match:
            caption_pos = caption_match.start()
        if tabular_match:
            tabular_pos = tabular_match.start()

        if caption_pos < 0:
            self.issues.append(
                {
                    "line": table["start"],
                    "level": self.LEVEL_WARNING,
                    "priority": "P2",
                    "message": "No \\caption found in table environment.",
                    "category": "caption",
                }
            )
        elif tabular_pos >= 0 and caption_pos > tabular_pos:
            self.issues.append(
                {
                    "line": table["start"],
                    "level": self.LEVEL_WARNING,
                    "priority": "P2",
                    "message": "Caption should appear above the table (before \\begin{tabular}), not below.",
                    "category": "caption_position",
                }
            )

    def _check_table_notes(self, table: dict) -> None:
        """Check table note format if present."""
        content = table["content"]

        # Look for common note patterns
        has_note = False
        if re.search(r"\\item\s+Note\.", content):
            has_note = True
        if re.search(r"\\item\s+注[：:]", content):
            has_note = True
        if re.search(r"\\footnotesize\s*Note\.", content):
            has_note = True
        if re.search(r"\\footnotesize\s*注[：:]", content):
            has_note = True

        # Check if there are significance markers but no note explaining them
        if (
            re.search(r"\*\*?\*?", content)
            and not has_note
            and re.search(r"\d+\.?\d*\s*\*{1,3}", content)
        ):
            self.issues.append(
                {
                    "line": table["start"],
                    "level": self.LEVEL_INFO,
                    "priority": "P3",
                    "message": "Statistical significance markers (*/**/ ***) detected but no table note defining them. Add a note: 'Note. * p<0.05; ** p<0.01; *** p<0.001.'",
                    "category": "table_note",
                }
            )

    def _check_number_precision(self, table: dict) -> None:
        """Check for inconsistent decimal precision within columns."""
        content = table["content"]

        # Extract data rows (lines between \midrule and \bottomrule)
        data_match = re.search(r"\\midrule(.*?)\\bottomrule", content, re.DOTALL)
        if not data_match:
            return

        data_section = data_match.group(1)
        rows = [r.strip() for r in data_section.split(r"\\") if r.strip()]

        if len(rows) < 2:
            return

        # Parse columns
        parsed_rows = []
        for row in rows:
            # Remove LaTeX commands for analysis
            cleaned = re.sub(r"\\textbf\{([^}]*)\}", r"\1", row)
            cleaned = re.sub(r"\\bfseries\s*", "", cleaned)
            cleaned = re.sub(r"\$[^$]*\$", "", cleaned)
            cells = [c.strip() for c in cleaned.split("&")]
            parsed_rows.append(cells)

        if not parsed_rows:
            return

        # Check each column for precision consistency
        n_cols = max(len(r) for r in parsed_rows)
        for col_idx in range(n_cols):
            decimals_seen: set[int] = set()
            for row in parsed_rows:
                if col_idx < len(row):
                    cell = row[col_idx].strip().rstrip("*")
                    # Extract numbers
                    nums = re.findall(r"\d+\.(\d+)", cell)
                    for n in nums:
                        decimals_seen.add(len(n))

            if len(decimals_seen) > 1:
                self.issues.append(
                    {
                        "line": table["start"],
                        "level": self.LEVEL_WARNING,
                        "priority": "P3",
                        "message": f"Inconsistent decimal precision in column {col_idx + 1}: found {sorted(decimals_seen)} decimal places. Use consistent precision within each column.",
                        "category": "precision",
                    }
                )

    def _suggest_fix(self, issue: dict) -> str:
        """Generate fix suggestion for an issue."""
        cat = issue.get("category", "")
        if cat == "vertical_lines":
            return "Remove all | characters from the column specification."
        if cat == "hline":
            return "Replace \\hline with \\toprule (first), \\midrule (after header), \\bottomrule (last)."
        if cat == "booktabs_missing":
            return "Add \\usepackage{booktabs} and replace \\hline with \\toprule/\\midrule/\\bottomrule."
        if cat == "caption_position":
            return "Move \\caption{...} before \\begin{tabular}."
        if cat == "precision":
            return "Align all values in the column to the same number of decimal places."
        if cat == "package":
            return "Add \\usepackage{booktabs} to the preamble."
        return ""

    def generate_report(self, result: dict) -> str:
        """Generate human-readable report."""
        lines = []
        lines.append("=" * 60)
        lines.append("Table Structure Check Report")
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
        description="Table Structure Checker - three-line table compliance"
    )
    parser.add_argument("tex_file", help=".tex file to check")
    parser.add_argument(
        "--fix-suggestions", "-f", action="store_true", help="Include fix suggestions"
    )
    parser.add_argument("--json", "-j", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    if not Path(args.tex_file).exists():
        print(f"[ERROR] File not found: {args.tex_file}")
        sys.exit(1)

    checker = TableChecker(args.tex_file)
    result = checker.check(fix_suggestions=args.fix_suggestions)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(checker.generate_report(result))

    sys.exit(1 if result["status"] == "FAIL" else 0)


if __name__ == "__main__":
    main()
