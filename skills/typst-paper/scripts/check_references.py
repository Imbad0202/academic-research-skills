#!/usr/bin/env python3
"""
Figure/Table/Equation Reference Integrity Checker for Typst papers.

Checks for undefined references, unreferenced labels, missing captions,
reference ordering issues, and numbering gaps using Typst syntax.

Usage:
    uv run python check_references.py main.typ
    uv run python check_references.py main.typ --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Regex patterns (Typst)
# ---------------------------------------------------------------------------

# Label definitions: <label-name>
LABEL_RE = re.compile(r"<([a-zA-Z][\w-]*)>")
# References: @label-name (citation/cross-reference) and #ref(<label-name>)
REF_RE = re.compile(r"@([a-zA-Z][\w-]*)|#ref\(\s*<([a-zA-Z][\w-]*)>\s*\)")
# Caption: caption: [ inside a figure call
CAPTION_RE = re.compile(r"caption\s*:\s*\[")
# Figure environment start: #figure(
FIGURE_ENV_RE = re.compile(r"#figure\s*\(")
COMMENT_PREFIX = "//"

# Prefixes tracked for "unreferenced label" warnings
# Typst labels often do not use colon-prefixed conventions, but support
# both plain names (e.g., <fig-arch>) and prefixed names (e.g., <fig:arch>)
TRACKED_PREFIXES = {"fig", "tab", "eq"}

# Prefixes checked for ordering
ORDERING_PREFIXES = {"fig", "tab"}


@dataclass
class LabelInfo:
    """Label definition information."""

    name: str  # Full label name (e.g., "fig-arch")
    prefix: str  # Prefix if present (e.g., "fig" from "fig:arch" or "fig-arch")
    line: int  # Definition line number (1-indexed)
    file: str  # Source file path


@dataclass
class RefInfo:
    """Reference information."""

    name: str  # Referenced label name
    line: int  # Reference line number (1-indexed)
    file: str  # Source file path
    command: str  # Reference command ("ref" or "hash-ref")


# ---------------------------------------------------------------------------
# Checker
# ---------------------------------------------------------------------------


class ReferenceChecker:
    """Single-file Typst reference integrity checker."""

    def __init__(self, content: str, file_path: str = "") -> None:
        self.content = content
        self.file_path = file_path
        self.lines = content.splitlines()
        self.issues: list[dict] = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _is_comment_line(self, line: str) -> bool:
        """Return True if the line (after stripping) is a Typst comment."""
        return line.lstrip().startswith(COMMENT_PREFIX)

    def _strip_comment(self, line: str) -> str:
        """Remove Typst line comment from a line."""
        idx = line.find("//")
        if idx == -1:
            return line
        return line[:idx]

    def _add_issue(
        self,
        line: int,
        severity: str,
        priority: str,
        message: str,
    ) -> None:
        """Append a structured issue dict."""
        self.issues.append(
            {
                "module": "REFERENCES",
                "line": line,
                "severity": severity,
                "priority": priority,
                "message": message,
            }
        )

    @staticmethod
    def _extract_prefix(label_name: str) -> str:
        """
        Extract the prefix of a Typst label.
        Supports both colon style (fig:arch) and hyphen style (fig-arch).
        """
        for sep in (":", "-"):
            if sep in label_name:
                return label_name.split(sep)[0]
        return ""

    # ------------------------------------------------------------------
    # Finders
    # ------------------------------------------------------------------

    def find_labels(self) -> list[LabelInfo]:
        """Find all <label> definitions, skipping comment lines."""
        labels: list[LabelInfo] = []
        for lineno, raw_line in enumerate(self.lines, start=1):
            if self._is_comment_line(raw_line):
                continue
            line = self._strip_comment(raw_line)
            for match in LABEL_RE.finditer(line):
                name = match.group(1).strip()
                prefix = self._extract_prefix(name)
                labels.append(LabelInfo(name=name, prefix=prefix, line=lineno, file=self.file_path))
        return labels

    def find_refs(self) -> list[RefInfo]:
        """Find all @label and #ref(<label>) references, skipping comment lines."""
        refs: list[RefInfo] = []
        for lineno, raw_line in enumerate(self.lines, start=1):
            if self._is_comment_line(raw_line):
                continue
            line = self._strip_comment(raw_line)
            for match in REF_RE.finditer(line):
                # Group 1: @name, group 2: #ref(<name>)
                name = (match.group(1) or match.group(2) or "").strip()
                if not name:
                    continue
                command = "ref" if match.group(1) else "hash-ref"
                refs.append(RefInfo(name=name, line=lineno, file=self.file_path, command=command))
        return refs

    # ------------------------------------------------------------------
    # Checks
    # ------------------------------------------------------------------

    def check_undefined_refs(self, labels: list[LabelInfo], refs: list[RefInfo]) -> None:
        """Check for @x / #ref(<x>) where no <x> label exists. Severity: Critical, P0."""
        defined = {lbl.name for lbl in labels}
        for ref in refs:
            if ref.name not in defined:
                ref_repr = f"@{ref.name}" if ref.command == "ref" else f"#ref(<{ref.name}>)"
                self._add_issue(
                    line=ref.line,
                    severity="Critical",
                    priority="P0",
                    message=f"Undefined reference: {ref_repr} — no matching <{ref.name}> label found",
                )

    def check_unreferenced_labels(self, labels: list[LabelInfo], refs: list[RefInfo]) -> None:
        """Check <label> never referenced (fig/tab/eq prefixes). Severity: Minor, P2."""
        referenced = {ref.name for ref in refs}
        for lbl in labels:
            if lbl.prefix in TRACKED_PREFIXES and lbl.name not in referenced:
                self._add_issue(
                    line=lbl.line,
                    severity="Minor",
                    priority="P2",
                    message=f"Unreferenced label: <{lbl.name}> is never cited in text",
                )

    def check_caption_presence(self, labels: list[LabelInfo]) -> None:
        """
        Check that #figure(...) blocks containing a label also contain a caption: [...].
        Severity: Major, P1.

        Detection strategy: scan for #figure( openers, then track brace depth to find
        the extent of each figure block, and verify caption: [ is present inside.
        """
        content = self.content
        # Build list of (start_line, end_line) for each #figure(...) block
        figure_spans: list[tuple[int, int]] = []

        for fig_match in FIGURE_ENV_RE.finditer(content):
            # Find the opening parenthesis
            open_paren_idx = fig_match.end() - 1
            # Scan forward to find matching closing paren
            depth = 0
            end_idx = open_paren_idx
            for i in range(open_paren_idx, len(content)):
                ch = content[i]
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        end_idx = i
                        break
            # Convert char offsets to 1-indexed line numbers
            start_line = content[: fig_match.start()].count("\n") + 1
            end_line = content[:end_idx].count("\n") + 1
            figure_spans.append((start_line, end_line))

        for lbl in labels:
            if lbl.prefix not in ("fig", "tab"):
                continue
            enclosing = None
            for start, end in figure_spans:
                if start <= lbl.line <= end:
                    enclosing = (start, end)
                    break
            if enclosing is None:
                continue
            start, end = enclosing
            block_lines = self.lines[start - 1 : end]
            block_text = "\n".join(block_lines)
            if not CAPTION_RE.search(block_text):
                self._add_issue(
                    line=lbl.line,
                    severity="Major",
                    priority="P1",
                    message=(
                        f"Missing caption in #figure block: "
                        f"<{lbl.name}> at line {lbl.line} has no caption: [...]"
                    ),
                )

    def check_ordering(self, labels: list[LabelInfo], refs: list[RefInfo]) -> None:
        """
        Check that first @x / #ref(<x>) does not appear before <x> definition.
        Only for fig/tab prefixes. Severity: Minor, P2.
        """
        label_lines: dict[str, int] = {lbl.name: lbl.line for lbl in labels}
        first_ref_lines: dict[str, int] = {}
        for ref in refs:
            if ref.name not in first_ref_lines or ref.line < first_ref_lines[ref.name]:
                first_ref_lines[ref.name] = ref.line

        for name, ref_line in first_ref_lines.items():
            prefix = self._extract_prefix(name)
            if prefix not in ORDERING_PREFIXES:
                continue
            if name in label_lines and ref_line < label_lines[name]:
                self._add_issue(
                    line=ref_line,
                    severity="Minor",
                    priority="P2",
                    message=(
                        f"Reference before definition: @{name} at line {ref_line} "
                        f"appears before <{name}> at line {label_lines[name]}"
                    ),
                )

    def check_numbering_gaps(self, labels: list[LabelInfo]) -> None:
        """
        Detect numbering gaps for labels with numeric suffixes.
        Supports both fig:1 / fig-1 styles. Severity: Minor, P2.
        """
        numeric_suffix_re = re.compile(r"^(.*?)(\d+)$")
        series: dict[str, list[tuple[int, int]]] = {}

        for lbl in labels:
            m = numeric_suffix_re.match(lbl.name)
            if not m:
                continue
            base = m.group(1)
            num = int(m.group(2))
            if base not in series:
                series[base] = []
            series[base].append((num, lbl.line))

        for series_key, entries in series.items():
            if len(entries) < 2:
                continue
            entries_sorted = sorted(entries, key=lambda x: x[0])
            numbers = [e[0] for e in entries_sorted]
            for i in range(len(numbers) - 1):
                if numbers[i + 1] - numbers[i] > 1:
                    missing_start = numbers[i] + 1
                    missing_end = numbers[i + 1] - 1
                    missing_range = (
                        str(missing_start)
                        if missing_start == missing_end
                        else f"{missing_start}–{missing_end}"
                    )
                    report_line = entries_sorted[i][1]
                    self._add_issue(
                        line=report_line,
                        severity="Minor",
                        priority="P2",
                        message=(
                            f"Numbering gap detected: {series_key}{missing_range} "
                            f"missing between {series_key}{numbers[i]} and "
                            f"{series_key}{numbers[i + 1]}"
                        ),
                    )

    # ------------------------------------------------------------------
    # Runner
    # ------------------------------------------------------------------

    def run_all(self) -> list[dict]:
        """Run all checks and return the full issues list."""
        self.issues = []
        labels = self.find_labels()
        refs = self.find_refs()
        self.check_undefined_refs(labels, refs)
        self.check_unreferenced_labels(labels, refs)
        self.check_caption_presence(labels)
        self.check_ordering(labels, refs)
        self.check_numbering_gaps(labels)
        return self.issues


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def _format_issues(issues: list[dict], comment_prefix: str = "//") -> str:
    """Format issues into the project's output protocol."""
    if not issues:
        return ""
    lines = []
    for issue in sorted(issues, key=lambda x: x.get("line") or 0):
        line_part = f"(Line {issue['line']}) " if issue.get("line") else ""
        lines.append(
            f"{comment_prefix} REFERENCES {line_part}"
            f"[Severity: {issue['severity']}] [Priority: {issue['priority']}]: "
            f"{issue['message']}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description="Reference Integrity Checker for Typst papers")
    parser.add_argument("file", help="Source .typ file to check")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
        return 1

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"[ERROR] Cannot read file: {exc}", file=sys.stderr)
        return 1

    checker = ReferenceChecker(content, str(path))
    issues = checker.run_all()

    if args.json:
        print(json.dumps(issues, indent=2, ensure_ascii=False))
    else:
        output = _format_issues(issues, comment_prefix=COMMENT_PREFIX)
        if output:
            print(output)

    has_critical = any(i["severity"] == "Critical" for i in issues)
    return 1 if has_critical else 0


if __name__ == "__main__":
    sys.exit(main())
