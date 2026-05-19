#!/usr/bin/env python3
"""
De-AI Batch Processor for English Academic Papers
Batch processes entire LaTeX/Typst chapters or documents.

Usage:
    uv run python -B deai_batch.py main.tex --chapter chapter3/introduction.tex
    uv run python -B deai_batch.py main.tex --all-sections
    uv run python -B deai_batch.py main.tex --section introduction --output polished/
"""

import argparse
import re
import sys
from pathlib import Path

# Import local parsers
try:
    from parsers import get_parser
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from parsers import get_parser


class DeAIBatchProcessor:
    """Batch process files for de-AI editing."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = file_path.read_text(encoding="utf-8", errors="ignore")
        self.lines = self.content.split("\n")
        self.parser = get_parser(file_path)
        self.section_ranges = self.parser.split_sections(self.content)
        self.comment_prefix = self.parser.get_comment_prefix()

    def analyze_section(self, section_name: str) -> dict:
        """Analyze a section for AI traces."""
        if section_name not in self.section_ranges:
            return {
                "section": section_name,
                "found": False,
                "lines": 0,
                "traces": [],
            }

        start, end = self.section_ranges[section_name]
        traces = []

        # Get lines for this section
        # Convert 1-based lines to 0-based index
        section_lines = self.lines[start - 1 : end]
        line_num = start

        for line in section_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith(self.comment_prefix):
                line_num += 1
                continue

            visible = self.parser.extract_visible_text(stripped)
            ai_patterns = self._check_ai_patterns(visible)

            if ai_patterns:
                traces.append(
                    {
                        "line": line_num,
                        "original": stripped,
                        "visible": visible,
                        "patterns": ai_patterns,
                    }
                )

            line_num += 1

        return {
            "section": section_name,
            "found": True,
            "lines": end - start + 1,
            "traces": traces,
        }

    def _check_ai_patterns(self, text: str) -> list[str]:
        """Check text for AI writing patterns."""
        patterns = []

        # Empty phrases
        empty_phrases = [
            r"significant (?:improvement|performance|gain)",
            r"comprehensive (?:analysis|study)",
            r"effective (?:solution|method)",
            r"important (?:contribution|role)",
            r"robust performance",
            r"novel approach",
            r"state-of-the-art",
        ]

        # Over-confident
        over_confident = [
            r"\bobviously\b",
            r"\bclearly\b",
            r"\bcertainly\b",
            r"\bundoubtedly\b",
        ]

        # Vague quantifiers
        vague_quantifiers = [
            r"\bmany studies\b",
            r"\bnumerous experiments\b",
            r"\bvarious methods\b",
            r"\bseveral approaches\b",
        ]

        # Template expressions
        template_exprs = [
            r"\bin recent years\b",
            r"\bmore and more\b",
            r"\bplays? an important role\b",
            r"\bwith the (?:rapid )?development of\b",
        ]

        all_checks = [
            ("empty_phrase", empty_phrases),
            ("over_confident", over_confident),
            ("vague_quantifier", vague_quantifiers),
            ("template_expr", template_exprs),
        ]

        for category, pattern_list in all_checks:
            for pattern in pattern_list:
                if re.search(pattern, text, re.IGNORECASE):
                    patterns.append(f"{category}: {pattern}")

        return patterns

    def generate_batch_report(self, analyses: dict[str, dict]) -> str:
        """Generate batch processing report."""
        report = []
        report.append("=" * 70)
        report.append("DE-AI BATCH PROCESSING REPORT")
        report.append("=" * 70)
        report.append(f"Source file: {self.file_path}")
        report.append("")

        total_traces = 0
        total_lines = 0

        for section_name, analysis in analyses.items():
            if not analysis["found"]:
                continue

            trace_count = len(analysis["traces"])
            total_traces += trace_count
            total_lines += analysis["lines"]

            density = (trace_count / analysis["lines"] * 100) if analysis["lines"] > 0 else 0

            report.append(f"\n{'─' * 70}")
            report.append(f"SECTION: {section_name.upper()}")
            report.append(f"{'─' * 70}")
            report.append(f"Lines: {analysis['lines']}")
            report.append(f"AI traces detected: {trace_count}")
            report.append(f"Density: {density:.1f}%")

            if trace_count > 0:
                report.append("\nTraces (first 5):")
                for i, trace in enumerate(analysis["traces"][:5], 1):
                    report.append(f"\n  [{i}] Line {trace['line']}")
                    report.append(f"      Patterns: {', '.join(trace['patterns'])}")
                    report.append(f"      Visible: {trace['visible'][:100]}")

        report.append("\n" + "=" * 70)
        report.append("SUMMARY")
        report.append("=" * 70)
        report.append(f"Total lines analyzed: {total_lines}")
        report.append(f"Total AI traces: {total_traces}")
        overall_density = (total_traces / total_lines * 100) if total_lines > 0 else 0
        report.append(f"Overall density: {overall_density:.1f}%")

        return "\n".join(report)

    def process_section_file(self, chapter_file: Path, output_dir: Path) -> bool:
        """Process a single chapter file."""
        if not chapter_file.exists():
            print(f"[ERROR] Chapter file not found: {chapter_file}")
            return False

        # Determine parser for the chapter file specifically
        chapter_parser = get_parser(chapter_file)
        comment_prefix = chapter_parser.get_comment_prefix()

        content = chapter_file.read_text(encoding="utf-8")
        lines = content.split("\n")

        processed_lines = []
        modifications = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            if not stripped or stripped.startswith(comment_prefix):
                processed_lines.append(line)
                continue

            visible = chapter_parser.extract_visible_text(stripped)
            patterns = self._check_ai_patterns(visible)

            if patterns:
                comment = f"{comment_prefix} DE-AI: Line {i} - {', '.join(patterns)}"
                processed_lines.append(comment)
                processed_lines.append(line)
                modifications.append(
                    {
                        "line": i,
                        "patterns": patterns,
                        "original": stripped,
                    }
                )
            else:
                processed_lines.append(line)

        output_file = output_dir / chapter_file.name
        output_file.write_text("\n".join(processed_lines), encoding="utf-8")

        print(f"[SUCCESS] Processed: {chapter_file.name}")
        print(f"         Output: {output_file}")
        print(f"         Modifications: {len(modifications)}")

        return True


def main():
    parser = argparse.ArgumentParser(
        description="Batch process LaTeX/Typst documents for de-AI editing"
    )

    parser.add_argument("file", type=Path, help="Main file (.tex or .typ)")
    parser.add_argument("--chapter", type=Path, help="Process specific chapter file")
    parser.add_argument("--all-sections", action="store_true", help="Analyze all sections")
    parser.add_argument("--section", type=str, help="Analyze specific section")
    parser.add_argument("--output", type=Path, help="Output directory for processed files")
    parser.add_argument("--report", type=Path, help="Save report to file")

    args = parser.parse_args()

    if not args.file.exists():
        print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    processor = DeAIBatchProcessor(args.file)

    if args.all_sections:
        analyses = {}
        for section_name in processor.section_ranges:
            analyses[section_name] = processor.analyze_section(section_name)

        report = processor.generate_batch_report(analyses)

        if args.report:
            args.report.write_text(report, encoding="utf-8")
            print(f"[SUCCESS] Report saved to: {args.report}")
        else:
            print(report)

    elif args.chapter:
        if not args.output:
            print("[ERROR] --output required when processing chapter file")
            sys.exit(1)

        args.output.mkdir(parents=True, exist_ok=True)
        success = processor.process_section_file(args.chapter, args.output)
        sys.exit(0 if success else 1)

    elif args.section:
        analysis = processor.analyze_section(args.section.lower())

        if not analysis["found"]:
            print(f"[WARNING] Section not found: {args.section}")
            sys.exit(1)

        print(f"\nSection: {args.section}")
        print(f"Lines: {analysis['lines']}")
        print(f"AI traces: {len(analysis['traces'])}\n")

        for trace in analysis["traces"][:10]:
            print(f"Line {trace['line']}:")
            print(f"  Patterns: {', '.join(trace['patterns'])}")
            print(f"  Text: {trace['visible'][:100]}")
            print()

    else:
        print(f"[INFO] Available sections in {args.file.name}:")
        for section_name in processor.section_ranges:
            start, end = processor.section_ranges[section_name]
            print(f"  - {section_name}: lines {start}-{end}")


if __name__ == "__main__":
    main()
