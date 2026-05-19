#!/usr/bin/env python3
"""
Figure/Table/Equation Reference Integrity Checker for LaTeX (Chinese theses).

Extends the single-file checker with multi-file support via \\input{} and \\include{}.
Resolves included files relative to the main file's directory.

Usage:
    uv run python check_references.py main.tex
    uv run python check_references.py main.tex --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Regex patterns (LaTeX, multi-file)
# ---------------------------------------------------------------------------

LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
# Chinese theses may also use \hyperref[label]{text}
REF_RE = re.compile(
    r"\\(?:ref|eqref|autoref|cref|Cref|pageref)\{([^}]+)\}"
    r"|\\hyperref\[([^\]]+)\]\{[^}]*\}"
)
CAPTION_RE = re.compile(r"\\caption(?:\[[^\]]*\])?\{")
FIGURE_ENV_RE = re.compile(r"\\begin\{(figure|table)\*?\}")
FIGURE_ENV_END_RE = re.compile(r"\\end\{(figure|table)\*?\}")
COMMENT_PREFIX = "%"

# Prefixes tracked for "unreferenced label" warnings
TRACKED_PREFIXES = {"fig", "tab", "eq"}

# Prefixes checked for reference-before-definition ordering
ORDERING_PREFIXES = {"fig", "tab"}


@dataclass
class LabelInfo:
    """Label definition information."""

    name: str  # Full label name (e.g., "fig:arch")
    prefix: str  # Prefix (e.g., "fig", "tab", "eq")
    line: int  # Definition line number (1-indexed, within the source file)
    file: str  # Source file path


@dataclass
class RefInfo:
    """Reference information."""

    name: str  # Referenced label name
    line: int  # Reference line number (1-indexed, within the source file)
    file: str  # Source file path
    command: str  # Reference command (e.g., "ref", "eqref", "hyperref")


# ---------------------------------------------------------------------------
# Single-file checker (base)
# ---------------------------------------------------------------------------


class ReferenceChecker:
    """Single-file LaTeX reference integrity checker."""

    def __init__(self, content: str, file_path: str = "") -> None:
        self.content = content
        self.file_path = file_path
        self.lines = content.splitlines()
        self.issues: list[dict] = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _is_comment_line(self, line: str) -> bool:
        """Return True if the line (after stripping) is a LaTeX comment."""
        return line.lstrip().startswith(COMMENT_PREFIX)

    def _strip_comment(self, line: str) -> str:
        """Remove LaTeX inline comment from a line (handles escaped %)."""
        return re.sub(r"(?<!\\)%.*", "", line)

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
        """Extract the prefix of a label (part before first colon)."""
        if ":" in label_name:
            return label_name.split(":")[0]
        return ""

    # ------------------------------------------------------------------
    # Finders
    # ------------------------------------------------------------------

    def find_labels(self) -> list[LabelInfo]:
        """Find all \\label{} definitions in self.content, skipping comment lines."""
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
        """Find all reference commands in self.content, skipping comment lines."""
        refs: list[RefInfo] = []
        for lineno, raw_line in enumerate(self.lines, start=1):
            if self._is_comment_line(raw_line):
                continue
            line = self._strip_comment(raw_line)
            for match in REF_RE.finditer(line):
                # Group 1: standard \ref{...} family; group 2: \hyperref[...]{...}
                name = (match.group(1) or match.group(2) or "").strip()
                if not name:
                    continue
                # Determine command
                full = match.group(0)
                if full.startswith(r"\hyperref"):
                    command = "hyperref"
                else:
                    cmd_match = re.match(r"\\(\w+)\{", full)
                    command = cmd_match.group(1) if cmd_match else "ref"
                refs.append(RefInfo(name=name, line=lineno, file=self.file_path, command=command))
        return refs

    # ------------------------------------------------------------------
    # Checks
    # ------------------------------------------------------------------

    def check_undefined_refs(self, labels: list[LabelInfo], refs: list[RefInfo]) -> None:
        """Check for \\ref{x} where no \\label{x} exists. Severity: Critical, P0."""
        defined = {lbl.name for lbl in labels}
        for ref in refs:
            if ref.name not in defined:
                self._add_issue(
                    line=ref.line,
                    severity="Critical",
                    priority="P0",
                    message=(
                        f"Undefined reference: \\{ref.command}{{{ref.name}}} "
                        f"— no matching \\label found"
                    ),
                )

    def check_unreferenced_labels(self, labels: list[LabelInfo], refs: list[RefInfo]) -> None:
        """Check \\label{x} never referenced (fig:, tab:, eq: only). Severity: Minor, P2."""
        referenced = {ref.name for ref in refs}
        for lbl in labels:
            if lbl.prefix in TRACKED_PREFIXES and lbl.name not in referenced:
                self._add_issue(
                    line=lbl.line,
                    severity="Minor",
                    priority="P2",
                    message=f"Unreferenced label: \\label{{{lbl.name}}} is never cited in text",
                )

    def check_caption_presence(self, labels: list[LabelInfo]) -> None:
        """
        Check that figure/table environments containing \\label{fig:*} or \\label{tab:*}
        also contain a \\caption. Severity: Major, P1.
        """
        # Build list of (start_line, end_line, env_type) from self.lines
        envs: list[tuple[int, int, str]] = []
        stack: list[tuple[int, str]] = []

        for lineno, raw_line in enumerate(self.lines, start=1):
            if self._is_comment_line(raw_line):
                continue
            line = self._strip_comment(raw_line)
            begin_match = FIGURE_ENV_RE.search(line)
            if begin_match:
                stack.append((lineno, begin_match.group(1)))
            end_match = FIGURE_ENV_END_RE.search(line)
            if end_match and stack:
                start_lineno, env_type = stack.pop()
                envs.append((start_lineno, lineno, env_type))

        for lbl in labels:
            if lbl.prefix not in ("fig", "tab"):
                continue
            enclosing = None
            for start, end, env_type in envs:
                if start <= lbl.line <= end:
                    enclosing = (start, end, env_type)
                    break
            if enclosing is None:
                continue
            start, end, env_type = enclosing
            env_text = "\n".join(self.lines[start - 1 : end])
            if not CAPTION_RE.search(env_text):
                self._add_issue(
                    line=lbl.line,
                    severity="Major",
                    priority="P1",
                    message=(
                        f"Missing caption in {env_type} environment: "
                        f"\\label{{{lbl.name}}} at line {lbl.line} has no \\caption"
                    ),
                )

    def check_ordering(self, labels: list[LabelInfo], refs: list[RefInfo]) -> None:
        """
        Check that first \\ref{x} does not appear before \\label{x} (same file only).
        Only for fig:/tab: prefixes. Severity: Minor, P2.
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
                        f"Reference before definition: \\ref{{{name}}} at line {ref_line} "
                        f"appears before \\label{{{name}}} at line {label_lines[name]}"
                    ),
                )

    def check_numbering_gaps(self, labels: list[LabelInfo]) -> None:
        """
        Detect numbering gaps for labels with numeric suffixes.
        Severity: Minor, P2.
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
# Multi-file checker (ThesisReferenceChecker)
# ---------------------------------------------------------------------------


class ThesisReferenceChecker(ReferenceChecker):
    """
    Multi-file reference checker supporting \\input and \\include.

    Resolves included files relative to the main file's directory and
    adds .tex extension automatically if missing.  Labels and references
    are tracked per-file so ordering checks remain meaningful.
    """

    INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")

    def __init__(self, main_file: str) -> None:
        self.main_file = Path(main_file).resolve()
        self.base_dir = self.main_file.parent
        # Map from resolved file path -> file content
        self.all_files: dict[str, str] = {}
        self._resolve_includes(self.main_file)
        # Build combined content (used by base class for caption/env detection)
        combined = "\n".join(self.all_files.values())
        super().__init__(combined, str(self.main_file))
        # Per-file label/ref lists (populated by _scan_all_files)
        self._all_labels: list[LabelInfo] = []
        self._all_refs: list[RefInfo] = []
        self._scan_all_files()

    def _resolve_includes(self, file_path: Path, visited: set[str] | None = None) -> None:
        """Recursively load file_path and all files it \\input/\\includes."""
        if visited is None:
            visited = set()
        resolved = str(file_path.resolve())
        if resolved in visited:
            return  # Prevent infinite loops from circular includes
        visited.add(resolved)

        if not file_path.exists():
            return  # Missing file — skip silently

        content = file_path.read_text(encoding="utf-8", errors="replace")
        self.all_files[resolved] = content

        for match in self.INPUT_RE.finditer(content):
            raw = match.group(1).strip()
            included = Path(raw)
            # Add .tex extension if missing
            if not included.suffix:
                included = included.with_suffix(".tex")
            # Resolve relative to the parent file's directory
            candidate = (file_path.parent / included).resolve()
            self._resolve_includes(candidate, visited)

    def _scan_all_files(self) -> None:
        """Scan every loaded file to collect per-file labels and refs."""
        for file_path_str, content in self.all_files.items():
            checker = ReferenceChecker(content, file_path_str)
            self._all_labels.extend(checker.find_labels())
            self._all_refs.extend(checker.find_refs())

    # Override run_all to use the cross-file label/ref sets
    def run_all(self) -> list[dict]:
        """Run all checks across all resolved files."""
        self.issues = []
        labels = self._all_labels
        refs = self._all_refs
        self.check_undefined_refs(labels, refs)
        self.check_unreferenced_labels(labels, refs)
        # Caption check: run per-file so line numbers are valid
        for file_path_str, content in self.all_files.items():
            per_file_checker = ReferenceChecker(content, file_path_str)
            per_file_labels = [lbl for lbl in labels if lbl.file == file_path_str]
            per_file_checker.check_caption_presence(per_file_labels)
            self.issues.extend(per_file_checker.issues)
        # Ordering: cross-file ordering is not meaningful, skip per-file
        for file_path_str in self.all_files:
            file_labels = [lbl for lbl in labels if lbl.file == file_path_str]
            file_refs = [ref for ref in refs if ref.file == file_path_str]
            if file_labels and file_refs:
                per = ReferenceChecker("", file_path_str)
                per.check_ordering(file_labels, file_refs)
                self.issues.extend(per.issues)
        self.check_numbering_gaps(labels)
        return self.issues


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def _format_issues(issues: list[dict], comment_prefix: str = "%") -> str:
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
    parser = argparse.ArgumentParser(
        description="Reference Integrity Checker for LaTeX (Chinese theses, multi-file)"
    )
    parser.add_argument("file", help="Main .tex file to check")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
        return 1

    checker = ThesisReferenceChecker(str(path))
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
