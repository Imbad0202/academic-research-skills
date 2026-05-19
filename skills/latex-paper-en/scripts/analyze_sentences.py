#!/usr/bin/env python3
"""
Long sentence analyzer (MVP) for LaTeX/Typst papers.
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


CLAUSE_MARKERS = {"which", "that", "because", "although", "while", "whereas", "if", "when"}


def _count_words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def _count_clauses(text: str) -> int:
    lowered = text.lower()
    marker_hits = sum(1 for marker in CLAUSE_MARKERS if re.search(rf"\b{marker}\b", lowered))
    comma_parts = max(0, text.count(","))
    return marker_hits + comma_parts


def _simplify_sentence(text: str) -> str:
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if len(parts) <= 1:
        return text
    head = parts[0]
    tail = ". ".join(parts[1:])
    return f"{head}. {tail}."


def analyze(file_path: Path, section: str | None, max_words: int, max_clauses: int) -> list[str]:
    parser = get_parser(file_path)
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = content.split("\n")
    sections = parser.split_sections(content)

    if section:
        key = section.lower()
        if key not in sections:
            return [f"% ERROR [Severity: Critical] [Priority: P0]: Section not found: {section}"]
        ranges = [sections[key]]
    else:
        ranges = list(sections.values()) if sections else [(1, len(lines))]

    output: list[str] = []
    for start, end in ranges:
        for line_no in range(start, min(end, len(lines)) + 1):
            raw = lines[line_no - 1].strip()
            if not raw or raw.startswith(parser.get_comment_prefix()):
                continue
            visible = parser.extract_visible_text(raw)
            if not visible:
                continue
            for sentence in re.split(r"(?<=[.!?])\s+", visible):
                sent = sentence.strip()
                if not sent:
                    continue
                words = _count_words(sent)
                clauses = _count_clauses(sent)
                if words <= max_words and clauses <= max_clauses:
                    continue

                simplified = _simplify_sentence(sent)
                output.extend(
                    [
                        f"% LONG SENTENCE (Line {line_no}, {words} words, {clauses} clauses) "
                        "[Severity: Minor] [Priority: P2]",
                        f"% Original: {sent}",
                        f"% Suggested: {simplified}",
                        "% Rationale: Sentence exceeds complexity threshold, split for readability.",
                        "",
                    ]
                )
    if not output:
        output.append("% LONG SENTENCE: No sentences exceeded configured thresholds.")
    return output


def main() -> int:
    cli = argparse.ArgumentParser(description="Long sentence analysis for LaTeX/Typst files (MVP)")
    cli.add_argument("file", type=Path, help="Target .tex/.typ file")
    cli.add_argument("--section", help="Section name to analyze")
    cli.add_argument("--max-words", type=int, default=50, help="Max words per sentence")
    cli.add_argument("--max-clauses", type=int, default=3, help="Max clauses per sentence")
    args = cli.parse_args()

    if not args.file.exists():
        print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
        return 1

    print("\n".join(analyze(args.file, args.section, args.max_words, args.max_clauses)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
