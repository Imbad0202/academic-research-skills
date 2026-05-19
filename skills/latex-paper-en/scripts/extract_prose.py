#!/usr/bin/env python3
"""
Prose Extractor - Extract plain text from LaTeX/Typst for analysis

Usage:
    uv run python -B extract_prose.py main.tex
    uv run python -B extract_prose.py main.tex --keep-structure
    uv run python -B extract_prose.py main.tex --output prose.txt
    uv run python -B extract_prose.py main.tex --keep-structure
"""

import argparse
import sys
from pathlib import Path

# Import local parsers
try:
    from parsers import get_parser
except ImportError:
    # Handle running from root directory
    sys.path.append(str(Path(__file__).parent))
    from parsers import get_parser


class ProseExtractor:
    """Wrapper for document parsing."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path).resolve()
        self.parser = get_parser(self.file_path)

    def extract(self, keep_structure: bool = False) -> str:
        """Extract prose from file."""
        try:
            content = self.file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            raise RuntimeError(f"Cannot read file: {e}") from e

        return self.parser.clean_text(content, keep_structure)

    def extract_sentences(self) -> list[str]:
        """Extract individual sentences."""
        text = self.extract(keep_structure=False)
        # Simple split, consistent with original implementation
        import re

        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]


def main():
    parser = argparse.ArgumentParser(description="Prose Extractor (LaTeX/Typst)")
    parser.add_argument("file", help="File to extract from (.tex or .typ)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument(
        "--keep-structure",
        "-k",
        action="store_true",
        help="Preserve paragraph and section structure",
    )
    parser.add_argument(
        "--sentences", "-s", action="store_true", help="Output as list of sentences"
    )

    args = parser.parse_args()

    if not Path(args.file).exists():
        print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    extractor = ProseExtractor(args.file)

    try:
        if args.sentences:
            sentences = extractor.extract_sentences()
            output = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(sentences))
        else:
            output = extractor.extract(keep_structure=args.keep_structure)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"[SUCCESS] Extracted prose written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
