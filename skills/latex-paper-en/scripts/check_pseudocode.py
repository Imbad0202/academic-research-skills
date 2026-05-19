#!/usr/bin/env python3
"""
IEEE-aware pseudocode checker for English LaTeX paper projects.

This checker distinguishes:
- hard IEEE constraints that should block a gate
- IEEE-safe defaults that are recommended but not mandatory

Usage:
    uv run python -B check_pseudocode.py main.tex
    uv run python -B check_pseudocode.py main.tex --venue ieee
    uv run python -B check_pseudocode.py main.tex --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

COMMENT_PREFIX = "%"
REF_RE = re.compile(r"\\(?:ref|autoref|cref|Cref|pageref)\{([^}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
CAPTION_TEXT_RE = re.compile(r"\\caption(?:\[[^\]]*\])?\{([^}]*)\}")
ALGORITHM_FLOAT_RE = re.compile(r"\\begin\{algorithm\*?\}")
ALGORITHMIC_RE = re.compile(r"\\begin\{algorithmic\}(?:\[(\d+)\])?")
PACKAGE_RE = re.compile(r"\\usepackage(?:\[[^\]]*\])?\{([^}]*)\}")
LONG_COMMENT_RE = re.compile(r"\\Comment\{([^}]*)\}")
LONG_LINE_RE = re.compile(r"\\(?:State|Statex|Require|Ensure)\b(.*)")
CONTROL_TOKEN_RE = re.compile(
    r"\\(?:State|Statex|Require|Ensure|If|ElsIf|Else|For|While|Repeat|Until|Procedure|Function)\b"
)
PSEUDOCODE_MARKER_RE = re.compile(
    r"\\begin\{algorithmic\}|\\(?:Require|Ensure|State|Comment|LComment|Procedure|Function)\b"
)
FIGURE_BEGIN_RE = re.compile(r"\\begin\{figure\*?\}")
FIGURE_END_RE = re.compile(r"\\end\{figure\*?\}")


@dataclass
class FigureSpan:
    start_line: int
    end_line: int
    text: str


class PseudocodeChecker:
    """Check pseudocode blocks in a LaTeX paper."""

    def __init__(self, tex_file: str, venue: str = "") -> None:
        self.tex_file = Path(tex_file).resolve()
        self.venue = venue.lower().strip()
        self.content = self.tex_file.read_text(encoding="utf-8")
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

    def _iter_packages(self) -> list[str]:
        packages: list[str] = []
        for match in PACKAGE_RE.finditer(self.content):
            packages.extend(part.strip() for part in match.group(1).split(","))
        return packages

    def _find_line(self, pattern: re.Pattern[str]) -> int | None:
        for idx, line in enumerate(self.lines, start=1):
            if pattern.search(line):
                return idx
        return None

    def _find_figure_spans(self) -> list[FigureSpan]:
        spans: list[FigureSpan] = []
        stack: list[int] = []
        for lineno, raw_line in enumerate(self.lines, start=1):
            line = re.sub(r"(?<!\\)%.*", "", raw_line)
            if FIGURE_BEGIN_RE.search(line):
                stack.append(lineno)
            if FIGURE_END_RE.search(line) and stack:
                start = stack.pop()
                text = "\n".join(self.lines[start - 1 : lineno])
                spans.append(FigureSpan(start, lineno, text))
        return spans

    def _first_ref_line(self, label_name: str) -> int | None:
        for lineno, raw_line in enumerate(self.lines, start=1):
            line = re.sub(r"(?<!\\)%.*", "", raw_line)
            for match in REF_RE.finditer(line):
                if match.group(1).strip() == label_name:
                    return lineno
        return None

    def _count_words(self, text: str) -> int:
        return len(re.findall(r"[A-Za-z0-9_+-]+", text))

    def check_ieee_float_rule(self) -> None:
        if self.venue != "ieee":
            return

        for lineno, raw_line in enumerate(self.lines, start=1):
            line = re.sub(r"(?<!\\)%.*", "", raw_line)
            if ALGORITHM_FLOAT_RE.search(line):
                self._add_issue(
                    lineno,
                    "Critical",
                    "P0",
                    "IEEE-safe pseudocode should not use floating algorithm environments; wrap "
                    "algorithmic content in a figure instead.",
                )

        packages = set(self._iter_packages())
        if "algorithm2e" in packages and self._find_line(ALGORITHM_FLOAT_RE) is None:
            self._add_issue(
                self._find_line(re.compile(r"algorithm2e")),
                "Minor",
                "P2",
                "algorithm2e is loaded. For IEEE submissions, prefer figure-wrapped algorithmicx/"
                "algpseudocodex unless the venue template explicitly allows another float model.",
            )

    def check_pseudocode_figures(self) -> None:
        for span in self._find_figure_spans():
            if not PSEUDOCODE_MARKER_RE.search(span.text):
                continue

            caption_match = CAPTION_TEXT_RE.search(span.text)
            label_match = LABEL_RE.search(span.text)

            if caption_match is None:
                self._add_issue(
                    span.start_line,
                    "Major",
                    "P1",
                    "Pseudocode figure is missing a caption. IEEE-style algorithm blocks should carry "
                    "a figure caption.",
                )
            else:
                caption = re.sub(r"\\[A-Za-z]+\b(?:\{[^}]*\})?", "", caption_match.group(1)).strip()
                if re.match(r"^(?:The|A|An)\b", caption):
                    self._add_issue(
                        span.start_line,
                        "Minor",
                        "P2",
                        "Pseudocode caption starts with an article. IEEE-safe defaults prefer direct "
                        "captions such as 'Adaptive inference procedure' rather than 'The ...'.",
                    )

            if label_match is None:
                self._add_issue(
                    span.start_line,
                    "Major",
                    "P1",
                    "Pseudocode figure is missing a label. Add a label so the text can reference the "
                    "algorithm block explicitly.",
                )
            else:
                label_name = label_match.group(1).strip()
                ref_line = self._first_ref_line(label_name)
                if ref_line is None:
                    self._add_issue(
                        span.start_line,
                        "Major",
                        "P1",
                        "Pseudocode figure label is never referenced in the text before or after the "
                        "block. Reference the block explicitly from the surrounding prose.",
                    )
                elif ref_line > span.start_line:
                    self._add_issue(
                        span.start_line,
                        "Major",
                        "P1",
                        "The first reference to this pseudocode figure appears after the block. IEEE "
                        "style normally references figures before they appear.",
                    )

            has_require = r"\Require" in span.text or r"\KwIn" in span.text or "Input:" in span.text
            has_ensure = r"\Ensure" in span.text or r"\KwOut" in span.text or "Output:" in span.text
            if not (has_require and has_ensure):
                self._add_issue(
                    span.start_line,
                    "Minor",
                    "P2",
                    "Input/output markers are not both explicit. IEEE-safe defaults recommend stating "
                    "inputs and outputs clearly for long algorithm blocks.",
                )

            numbered_match = ALGORITHMIC_RE.search(span.text)
            has_line_numbers = numbered_match is not None and numbered_match.group(1) == "1"
            if not has_line_numbers and "alglinenumber" not in span.text:
                self._add_issue(
                    span.start_line,
                    "Minor",
                    "P2",
                    "Line numbers were not detected. They are recommended for IEEE-like review but not "
                    "required.",
                )

            for comment_match in LONG_COMMENT_RE.finditer(span.text):
                if self._count_words(comment_match.group(1)) > 12:
                    self._add_issue(
                        span.start_line,
                        "Minor",
                        "P2",
                        "A \\Comment{...} line is unusually long. Prefer short inline comments and move "
                        "long explanation into the main text or use \\LComment.",
                    )
                    break

            for local_index, raw_line in enumerate(span.text.splitlines(), start=span.start_line):
                stripped = re.sub(r"(?<!\\)%.*", "", raw_line).strip()
                long_line_match = LONG_LINE_RE.search(stripped)
                if not long_line_match:
                    continue
                payload = long_line_match.group(1).strip()
                if CONTROL_TOKEN_RE.search(stripped):
                    payload = re.sub(r"\\[A-Za-z]+(?:\[[^\]]*\])?(?:\{[^}]*\})?", " ", payload)
                if self._count_words(payload) > 22:
                    self._add_issue(
                        local_index,
                        "Minor",
                        "P2",
                        "A pseudocode line contains a prose-length explanation. Keep algorithm steps "
                        "short and move paragraph-style explanation back into the main text.",
                    )
                    break

    def check(self) -> list[dict]:
        self.issues = []
        self.check_ieee_float_rule()
        self.check_pseudocode_figures()
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
    parser = argparse.ArgumentParser(description="IEEE-aware pseudocode checker for LaTeX papers")
    parser.add_argument("file", help="Source .tex file to check")
    parser.add_argument(
        "--venue",
        default="",
        choices=["", "ieee", "acm", "springer", "neurips", "icml"],
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
