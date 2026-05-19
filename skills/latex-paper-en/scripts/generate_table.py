#!/usr/bin/env python3
"""
Table Generator - Convert structured data to publication-ready table code.

Usage:
    uv run python -B generate_table.py data.csv --style booktabs
    uv run python -B generate_table.py data.json --style booktabs --bilingual
    uv run python -B generate_table.py data.csv --style booktabs --stats
"""

import argparse
import csv
import json
import sys
from io import StringIO
from pathlib import Path


class TableGenerator:
    """Generate LaTeX booktabs and Markdown tables from structured data."""

    def __init__(self, style: str = "booktabs"):
        self.style = style

    def generate(
        self,
        headers: list[str],
        rows: list[list[str]],
        bilingual: bool = False,
        stats: bool = False,
        caption_en: str = "",
        caption_zh: str = "",
    ) -> dict:
        """Generate table in multiple formats.

        Returns dict with keys: markdown, latex, captions, word_tip.
        """
        result = {
            "markdown": self._to_markdown(headers, rows),
            "latex": self._to_latex(headers, rows, caption_en),
            "word_tip": (
                "To create a three-line table in Word:\n"
                "1. Insert a standard table\n"
                "2. Select all → Borders → No Border\n"
                "3. Select header row → add bottom border\n"
                "4. Select entire table → add top and bottom borders\n"
                "Result: a clean three-line table."
            ),
        }

        if bilingual:
            result["captions"] = self._suggest_captions(headers, caption_en, caption_zh)
        if stats:
            result["stats_note"] = (
                "\\begin{tablenotes}\n"
                "  \\small\n"
                "  \\item Note. Bold values indicate best performance.\n"
                "  \\item * $p < 0.05$; ** $p < 0.01$; *** $p < 0.001$.\n"
                "\\end{tablenotes}"
            )

        return result

    def _to_markdown(self, headers: list[str], rows: list[list[str]]) -> str:
        """Generate Markdown three-line table."""
        if not headers:
            return ""

        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(cell))

        # Build table
        lines = []

        # Header
        header_cells = [h.ljust(col_widths[i]) for i, h in enumerate(headers)]
        lines.append("| " + " | ".join(header_cells) + " |")

        # Separator (represents the mid-rule)
        sep_cells = ["-" * col_widths[i] for i in range(len(headers))]
        lines.append("| " + " | ".join(sep_cells) + " |")

        # Data rows
        for row in rows:
            padded = []
            for i in range(len(headers)):
                cell = row[i] if i < len(row) else ""
                padded.append(cell.ljust(col_widths[i]))
            lines.append("| " + " | ".join(padded) + " |")

        return "\n".join(lines)

    def _to_latex(self, headers: list[str], rows: list[list[str]], caption: str = "") -> str:
        """Generate LaTeX booktabs table code."""
        n_cols = len(headers)
        if n_cols == 0:
            return ""

        # Detect numeric columns for S column type
        col_types = []
        for i in range(n_cols):
            is_numeric = True
            for row in rows:
                if i < len(row):
                    cell = row[i].strip().rstrip("*").replace("\\textbf{", "").rstrip("}")
                    try:
                        float(cell.replace(",", ""))
                    except ValueError:
                        if cell and cell not in ("-", "--", "N/A", "n/a"):
                            is_numeric = False
                            break
            col_types.append("S" if is_numeric and i > 0 else "l")

        col_spec = "".join(col_types)

        lines = []
        lines.append("\\begin{table}[t]")
        if caption:
            lines.append(f"  \\caption{{{caption}}}")
            # Generate a simple label from caption
            label = caption.lower()
            label = label.replace(" ", "_")[:30]
            label = "".join(c for c in label if c.isalnum() or c == "_")
            lines.append(f"  \\label{{tab:{label}}}")
        lines.append("  \\centering")
        lines.append(f"  \\begin{{tabular}}{{{col_spec}}}")
        lines.append("    \\toprule")

        # Headers (wrap in braces for S columns)
        header_cells = []
        for i, h in enumerate(headers):
            if col_types[i] == "S":
                header_cells.append("{" + h + "}")
            else:
                header_cells.append(h)
        lines.append("    " + " & ".join(header_cells) + " \\\\")
        lines.append("    \\midrule")

        # Data rows
        for row in rows:
            padded = []
            for i in range(n_cols):
                cell = row[i] if i < len(row) else ""
                padded.append(cell)
            lines.append("    " + " & ".join(padded) + " \\\\")

        lines.append("    \\bottomrule")
        lines.append("  \\end{tabular}")
        lines.append("\\end{table}")

        return "\n".join(lines)

    def _suggest_captions(self, headers: list[str], caption_en: str, caption_zh: str) -> dict:
        """Suggest bilingual captions based on column content."""
        suggestion = {
            "en": caption_en or f"Comparison of {', '.join(headers[1:3])} across methods.",
            "zh": caption_zh or f"不同方法的{'、'.join(headers[1:3])}比较。",
        }
        return suggestion


def load_csv(file_path: str) -> tuple[list[str], list[list[str]]]:
    """Load data from CSV file."""
    path = Path(file_path)
    content = path.read_text(encoding="utf-8", errors="replace")
    reader = csv.reader(StringIO(content))
    all_rows = list(reader)
    if not all_rows:
        return [], []
    return all_rows[0], all_rows[1:]


def load_json(file_path: str) -> tuple[list[str], list[list[str]]]:
    """Load data from JSON file.

    Expected format:
    {
        "headers": ["Model", "Accuracy", "F1"],
        "rows": [["Baseline", "85.3", "83.7"], ...]
    }
    """
    path = Path(file_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("headers", []), data.get("rows", [])


def main():
    parser = argparse.ArgumentParser(description="Table Generator - CSV/JSON to LaTeX booktabs")
    parser.add_argument("data_file", help="CSV or JSON file with table data")
    parser.add_argument(
        "--style",
        choices=["booktabs", "plain"],
        default="booktabs",
        help="Table style (default: booktabs)",
    )
    parser.add_argument(
        "--bilingual", "-b", action="store_true", help="Generate bilingual captions"
    )
    parser.add_argument(
        "--stats", "-s", action="store_true", help="Add statistical significance note"
    )
    parser.add_argument("--caption-en", default="", help="English caption text")
    parser.add_argument("--caption-zh", default="", help="Chinese caption text")
    parser.add_argument("--json", "-j", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    data_path = Path(args.data_file)
    if not data_path.exists():
        print(f"[ERROR] File not found: {args.data_file}")
        sys.exit(1)

    # Load data
    if data_path.suffix.lower() == ".json":
        headers, rows = load_json(args.data_file)
    else:
        headers, rows = load_csv(args.data_file)

    if not headers:
        print("[ERROR] No data found in file")
        sys.exit(1)

    # Generate
    gen = TableGenerator(style=args.style)
    result = gen.generate(
        headers,
        rows,
        bilingual=args.bilingual,
        stats=args.stats,
        caption_en=args.caption_en,
        caption_zh=args.caption_zh,
    )

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print("Markdown Preview")
        print("=" * 60)
        print(result["markdown"])
        print()
        print("=" * 60)
        print("LaTeX Code (booktabs)")
        print("=" * 60)
        print(result["latex"])
        if result.get("captions"):
            print()
            print("=" * 60)
            print("Bilingual Captions")
            print("=" * 60)
            print(f"EN: {result['captions']['en']}")
            print(f"ZH: {result['captions']['zh']}")
        if result.get("stats_note"):
            print()
            print("=" * 60)
            print("Statistical Note (add inside threeparttable)")
            print("=" * 60)
            print(result["stats_note"])
        print()
        print("=" * 60)
        print("Word Tip")
        print("=" * 60)
        print(result["word_tip"])

    sys.exit(0)


if __name__ == "__main__":
    main()
