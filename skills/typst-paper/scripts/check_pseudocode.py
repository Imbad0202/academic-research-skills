#!/usr/bin/env python3
"""
IEEE-aware pseudocode checker for Typst paper projects.

Usage:
    uv run python -B check_pseudocode.py main.typ
    uv run python -B check_pseudocode.py main.typ --venue ieee
    uv run python -B check_pseudocode.py main.typ --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

COMMENT_PREFIX = "//"
CAPTION_RE = re.compile(r"caption\s*:\s*\[")
FIGURE_RE = re.compile(r"#figure\s*\(")
ALGORITHM_FIGURE_RE = re.compile(r"#algorithm-figure\s*\(")
ALGORITHMIC_IMPORT_RE = re.compile(r'@preview/algorithmic(?::[^"]+)?')
LOVELACE_IMPORT_RE = re.compile(r'@preview/lovelace(?::[^"]+)?')
STYLE_ALGORITHM_RE = re.compile(r"style-algorithm")
LINE_NUMBER_RE = re.compile(r"(?:line[- ]?numbers?|numbering)\s*:\s*true|line[- ]?numbers?")


class PseudocodeChecker:
    """Check Typst pseudocode blocks for IEEE-like output quality."""

    def __init__(self, typ_file: str, venue: str = "") -> None:
        self.typ_file = Path(typ_file).resolve()
        self.venue = venue.lower().strip()
        self.content = self.typ_file.read_text(encoding="utf-8")
        self.lines = self.content.splitlines()
        self.issues: list[dict] = []

    def _add_issue(self, line: int | None, severity: str, priority: str, message: str) -> None:
        self.issues.append(
            {
                "module": "PSEUDOCODE",
                "line": line,
                "severity": severity,
                "priority": priority,
                "message": message,
            }
        )

    def _line_for_token(self, token: str) -> int | None:
        for lineno, line in enumerate(self.lines, start=1):
            if token in line:
                return lineno
        return None

    def _find_parenthesized_blocks(self, pattern: re.Pattern[str]) -> list[tuple[int, int, str]]:
        blocks: list[tuple[int, int, str]] = []
        for match in pattern.finditer(self.content):
            open_idx = match.end() - 1
            depth = 0
            end_idx = open_idx
            for index in range(open_idx, len(self.content)):
                char = self.content[index]
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                    if depth == 0:
                        end_idx = index
                        break
            start_line = self.content[: match.start()].count("\n") + 1
            end_line = self.content[:end_idx].count("\n") + 1
            blocks.append((start_line, end_line, self.content[match.start() : end_idx + 1]))
        return blocks

    def _word_count(self, text: str) -> int:
        return len(re.findall(r"[A-Za-z0-9_\-\u4e00-\u9fff]+", text))

    def check_algorithmic_blocks(self) -> None:
        uses_algorithmic = bool(ALGORITHMIC_IMPORT_RE.search(self.content)) or bool(
            ALGORITHM_FIGURE_RE.search(self.content)
        )
        if not uses_algorithmic:
            return

        if not STYLE_ALGORITHM_RE.search(self.content):
            self._add_issue(
                self._line_for_token("style-algorithm"),
                "Major",
                "P1",
                "algorithmic blocks were detected without style-algorithm. IEEE-like output is more "
                "stable when the package styling hook is applied explicitly.",
            )

        for start_line, _end_line, text in self._find_parenthesized_blocks(ALGORITHM_FIGURE_RE):
            if CAPTION_RE.search(text) is None:
                self._add_issue(
                    start_line,
                    "Major",
                    "P1",
                    "algorithm-figure is missing a caption. IEEE-like pseudocode should use a figure "
                    "caption so the block can be referenced consistently.",
                )
            if LINE_NUMBER_RE.search(text) is None:
                self._add_issue(
                    start_line,
                    "Minor",
                    "P2",
                    "Line numbers were not detected in algorithm-figure. They are recommended for "
                    "IEEE-like review but not required.",
                )

            for local_line, raw_line in enumerate(text.splitlines(), start=start_line):
                stripped = raw_line.strip()
                if "comment(" not in stripped and "//" not in stripped:
                    continue
                payload = stripped.split("comment(", 1)[-1].rstrip(")")
                if "//" in stripped:
                    payload = stripped.split("//", 1)[-1]
                if self._word_count(payload) > 16:
                    self._add_issue(
                        local_line,
                        "Minor",
                        "P2",
                        "A pseudocode comment is unusually long. Keep comments short and move "
                        "paragraph-level explanation back into the main text.",
                    )
                    break

    def check_lovelace_blocks(self) -> None:
        if not LOVELACE_IMPORT_RE.search(self.content):
            return

        has_wrapper = bool(
            FIGURE_RE.search(self.content) or ALGORITHM_FIGURE_RE.search(self.content)
        )
        if self.venue == "ieee" and not has_wrapper:
            self._add_issue(
                self._line_for_token("lovelace"),
                "Critical",
                "P0",
                "lovelace output is not wrapped in a figure-like container. IEEE-like submissions "
                "should wrap free-form pseudocode in #figure(...) with a caption.",
            )

        if has_wrapper and CAPTION_RE.search(self.content) is None:
            self._add_issue(
                self._line_for_token("lovelace"),
                "Major",
                "P1",
                "A lovelace-based pseudocode block appears to be wrapped without a caption. Add a "
                "caption for IEEE-like figure handling.",
            )

    def check_prose_length(self) -> None:
        figure_blocks = self._find_parenthesized_blocks(
            FIGURE_RE
        ) + self._find_parenthesized_blocks(ALGORITHM_FIGURE_RE)
        for start_line, _end_line, text in figure_blocks:
            if "algorithm" not in text.lower() and "lovelace" not in self.content.lower():
                continue
            for local_line, raw_line in enumerate(text.splitlines(), start=start_line):
                stripped = raw_line.strip()
                if not stripped or stripped.startswith("//") or "caption:" in stripped:
                    continue
                if self._word_count(stripped) > 24:
                    self._add_issue(
                        local_line,
                        "Minor",
                        "P2",
                        "A pseudocode line contains prose-length explanation. Prefer short algorithmic "
                        "steps and move long explanation into the surrounding paragraph.",
                    )
                    return

    def check(self) -> list[dict]:
        self.issues = []
        self.check_algorithmic_blocks()
        self.check_lovelace_blocks()
        self.check_prose_length()
        return sorted(self.issues, key=lambda item: (item.get("line") or 0, item["severity"]))

    def generate_report(self, issues: list[dict]) -> str:
        if not issues:
            return ""
        lines = []
        for issue in issues:
            line_part = f"(Line {issue['line']}) " if issue.get("line") else ""
            lines.append(
                f"{COMMENT_PREFIX} PSEUDOCODE {line_part}[Severity: {issue['severity']}] "
                f"[Priority: {issue['priority']}]: {issue['message']}"
            )
        return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="IEEE-aware pseudocode checker for Typst papers")
    parser.add_argument("file", help="Source .typ file to check")
    parser.add_argument(
        "--venue",
        default="",
        choices=["", "ieee", "acm", "springer", "neurips", "cvpr"],
        help="Venue context used for stricter checks",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
        return 1

    checker = PseudocodeChecker(str(path), venue=args.venue)
    issues = checker.check()

    if args.json:
        print(json.dumps(issues, indent=2, ensure_ascii=False))
    else:
        output = checker.generate_report(issues)
        if output:
            print(output)

    return 1 if any(issue["severity"] == "Critical" for issue in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
