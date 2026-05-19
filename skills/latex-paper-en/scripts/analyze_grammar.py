#!/usr/bin/env python3
"""
Grammar Analysis (MVP) for English LaTeX/Typst papers.

Outputs diff-comment style suggestions without modifying source files.
"""

import argparse
import re
import sys
from pathlib import Path

try:
    from parsers import get_parser
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from parsers import get_parser


def _apply_rules(text: str) -> list[tuple[str, str, str]]:
    """Return list of (issue, revised, rationale)."""
    findings: list[tuple[str, str, str]] = []
    rules = [
        (
            r"\bwe propose method\b",
            "we propose a method",
            "Grammar: Article missing before singular count noun.",
        ),
        (
            r"\bthe data shows\b",
            "the data show",
            "Grammar: Subject-verb agreement ('data' is plural in formal academic usage).",
        ),
        (
            r"\bthis approach get\b",
            "this approach gets",
            "Grammar: Third-person singular verb form required.",
        ),
        (
            r"\bthese method\b",
            "these methods",
            "Grammar: Plural demonstrative requires plural noun.",
        ),
    ]

    lowered = text.lower()
    for pattern, replacement, rationale in rules:
        if re.search(pattern, lowered):
            revised = re.sub(pattern, replacement, lowered)
            findings.append((pattern, revised, rationale))
    return findings


def analyze(file_path: Path, section: str | None = None) -> list[str]:
    parser = get_parser(file_path)
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = content.split("\n")
    sections = parser.split_sections(content)

    selected_ranges: list[tuple[int, int]] = []
    if section:
        key = section.lower()
        if key not in sections:
            return [f"% ERROR [Severity: Critical] [Priority: P0]: Section not found: {section}"]
        selected_ranges.append(sections[key])
    else:
        if sections:
            selected_ranges.extend(sections.values())
        else:
            selected_ranges.append((1, len(lines)))

    output: list[str] = []
    for start, end in selected_ranges:
        for line_no in range(start, min(end, len(lines)) + 1):
            raw = lines[line_no - 1].strip()
            if not raw or raw.startswith(parser.get_comment_prefix()):
                continue
            visible = parser.extract_visible_text(raw)
            if not visible:
                continue

            findings = _apply_rules(visible)
            for pattern, revised, rationale in findings:
                output.extend(
                    [
                        f"% GRAMMAR (Line {line_no}) [Severity: Major] [Priority: P1]: Rule hit: {pattern}",
                        f"% Original: {visible}",
                        f"% Revised:  {revised}",
                        f"% Rationale: {rationale}",
                        "",
                    ]
                )
    if not output:
        output.append("% GRAMMAR: No rule-based issues detected in selected scope.")
    return output


def main() -> int:
    cli = argparse.ArgumentParser(description="Grammar analysis for LaTeX/Typst files (MVP)")
    cli.add_argument("file", type=Path, help="Target .tex or .typ file")
    cli.add_argument("--section", help="Section name to analyze")
    args = cli.parse_args()

    if not args.file.exists():
        print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
        return 1

    print("\n".join(analyze(args.file, args.section)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
