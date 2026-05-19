"""
Document Parsers for Academic Writing Skills (Typst)
Support for Typst document parsing.
"""

import re
from abc import ABC, abstractmethod
from typing import Any


class DocumentParser(ABC):
    """Abstract base class for document parsers."""

    @abstractmethod
    def split_sections(self, content: str) -> dict[str, tuple[int, int]]:
        """
        Split document into sections.
        Returns map of {section_name: (start_line, end_line)}.
        """
        pass

    @abstractmethod
    def extract_visible_text(self, line: str) -> str:
        """
        Extract text visible to reader, preserving structure markers.
        Used for line-by-line AI trace checking.
        """
        pass

    @abstractmethod
    def clean_text(self, content: str, keep_structure: bool = False) -> str:
        """
        Extract pure prose text, removing all markup.
        Used for prose extraction and word counting.
        """
        pass

    @abstractmethod
    def get_comment_prefix(self) -> str:
        """Get the comment prefix for the language."""
        pass


class TypstParser(DocumentParser):
    """Parser for Typst documents."""

    # Section patterns (Heading 1-3)
    # Matches: = Introduction or == Related Work
    SECTION_PATTERNS = {
        "introduction": r"^=\s+(?:Introduction|INTRODUCTION|绪论|引言)",
        "related": r"^=\s+(?:Related\s+Work|RELATED\s+WORK|相关工作|文献综述)",
        "method": r"^=\s+.*(?:Method|Methodology|Approach|方法|原理|设计)",
        "experiment": r"^=\s+.*(?:Experiment|Evaluation|Implementation|实验|实现|测试)",
        "result": r"^=\s+.*(?:Result|Performance|结果|性能)",
        "discussion": r"^=\s+.*(?:Discussion|Analysis|讨论|分析)",
        "conclusion": r"^=\s+.*(?:Conclusion|Conclusions|结论|总结与展望)",
        "abstract": r"#abstract\[",
    }

    PRESERVE_PATTERNS = [
        r"@[a-zA-Z0-9_-]+",  # Citations @key
        r"#cite\([^)]+\)",  # Function calls #cite()
        r"#figure\([^)]+\)",  # Figures
        r"#table\([^)]+\)",  # Tables
        r"\$[^$]+\$",  # Math $...$
        r"//.*",  # Line comments
        r"/\*.*?\*/",  # Block comments
        r"<[a-zA-Z0-9_-]+>",  # Labels <label>
        r"#link\([^)]+\)",  # Links
    ]

    def get_comment_prefix(self) -> str:
        return "//"

    def split_sections(self, content: str) -> dict[str, tuple[int, int]]:
        lines = content.split("\n")
        sections = {}
        current_section = "preamble"
        start_line = 0

        for i, line in enumerate(lines, 1):
            line = line.strip()
            # Ignore comments
            if line.startswith("//"):
                continue

            for section_name, pattern in self.SECTION_PATTERNS.items():
                if re.search(pattern, line, re.IGNORECASE):
                    if current_section != "preamble":
                        sections[current_section] = (start_line, i - 1)
                    current_section = section_name
                    start_line = i
                    break

        if current_section != "preamble":
            sections[current_section] = (start_line, len(lines))

        return sections

    def extract_visible_text(self, line: str) -> str:
        # Same logic as LatexParser but with Typst patterns
        temp_line = line

        # Remove comments first for Typst
        if "//" in temp_line:
            temp_line = temp_line.split("//")[0]

        preserved = []
        for pattern in self.PRESERVE_PATTERNS:
            matches = list(re.finditer(pattern, temp_line, re.DOTALL))
            for match in reversed(matches):
                preserved.append(
                    {"start": match.start(), "end": match.end(), "text": match.group()}
                )
                placeholder = " " * (match.end() - match.start())
                temp_line = temp_line[: match.start()] + placeholder + temp_line[match.end() :]

        preserved.sort(key=lambda x: x["start"])

        visible_parts = []
        last_end = 0
        for item in preserved:
            if item["start"] > last_end:
                visible_parts.append(temp_line[last_end : item["start"]])
            last_end = item["end"]
        if last_end < len(temp_line):
            visible_parts.append(temp_line[last_end:])

        return " ".join(visible_parts).strip()

    def clean_text(self, content: str, keep_structure: bool = False) -> str:
        # Remove comments
        content = re.sub(r"//.*", "", content)
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

        # Remove math
        content = re.sub(r"\$[^$]+\$", "", content)

        # Handle headers
        if keep_structure:
            content = re.sub(r"^=+\s+(.+)$", r"\n\n## \1\n\n", content, flags=re.MULTILINE)
        else:
            content = re.sub(r"^=+\s+.+$", "", content, flags=re.MULTILINE)

        # Remove function calls #func(...) - basic support
        content = re.sub(r"#[a-zA-Z0-9_]+\([^)]*\)", "", content)
        content = re.sub(r"@[a-zA-Z0-9_-]+", "", content)
        content = re.sub(r"<[a-zA-Z0-9_-]+>", "", content)

        # Cleanup
        content = re.sub(r"\n+", "\n", content)
        content = re.sub(r" +", " ", content)
        content = re.sub(r"\.(\s*\.)+", ".", content)  # Fix multiple periods
        return content.strip()


def get_parser(file_path: Any) -> DocumentParser:
    """Factory method to get appropriate parser for Typst files."""
    return TypstParser()


def _normalize_whitespace(text: str) -> str:
    """Collapse whitespace to single spaces."""
    return re.sub(r"\s+", " ", text).strip()


def _extract_balanced_block(content: str, start_idx: int, opener: str, closer: str) -> str:
    """Extract a balanced block body from content starting at opener index."""
    if start_idx < 0 or start_idx >= len(content) or content[start_idx] != opener:
        return ""

    depth = 0
    block_start = -1

    for i in range(start_idx, len(content)):
        char = content[i]
        if char == opener:
            depth += 1
            if depth == 1:
                block_start = i + 1
        elif char == closer:
            depth -= 1
            if depth == 0 and block_start >= 0:
                return content[block_start:i]
            if depth < 0:
                return ""
    return ""


def _strip_typst_markup(text: str) -> str:
    """Strip lightweight Typst markup for title/abstract extraction."""
    cleaned = text
    cleaned = re.sub(r"#\w+\([^)]*\)", " ", cleaned)

    # Collapse simple bracket macros repeatedly (e.g., #emph[Paper], nested forms).
    while True:
        collapsed = re.sub(r"#\w+\[([^\[\]]*)\]", r"\1", cleaned)
        if collapsed == cleaned:
            break
        cleaned = collapsed

    cleaned = re.sub(r"[\[\]]", " ", cleaned)
    return _normalize_whitespace(cleaned)


def extract_title(content: str) -> str:
    """Extract document title from Typst source content."""
    # Typst common: #set document(title: "...")
    typst_str = re.search(
        r"#set\s+document\s*\(\s*title\s*:\s*\"([^\"]+)\"",
        content,
        re.DOTALL,
    )
    if typst_str:
        return _normalize_whitespace(typst_str.group(1))

    # Typst bracket style: #set document(title: [ ... ])
    typst_block = re.search(r"#set\s+document\s*\(\s*title\s*:\s*\[", content, re.DOTALL)
    if typst_block:
        bracket_idx = typst_block.end() - 1
        text = _extract_balanced_block(content, bracket_idx, "[", "]")
        if text:
            return _strip_typst_markup(text)

    return ""


def extract_abstract(content: str) -> str:
    """Extract abstract text from Typst source content."""
    # Typst: #abstract[...]
    typst_abs = re.search(r"#abstract\[", content, re.DOTALL)
    if typst_abs:
        bracket_idx = typst_abs.end() - 1
        text = _extract_balanced_block(content, bracket_idx, "[", "]")
        if text:
            return _strip_typst_markup(text)

    heading_abs = re.search(
        r"^=\s+摘要\s*\n(.*?)(?=^=\s+|\Z)",
        content,
        re.DOTALL | re.MULTILINE,
    )
    if heading_abs:
        return _strip_typst_markup(heading_abs.group(1))

    return ""
