"""
Document Parsers for Chinese Academic Thesis
Support for LaTeX and Typst document parsing.
"""

import re
from abc import ABC, abstractmethod
from typing import Any


class DocumentParser(ABC):
    """Abstract base class for document parsers."""

    @abstractmethod
    def split_sections(self, content: str) -> dict[str, tuple[int, int]]:
        pass

    @abstractmethod
    def extract_visible_text(self, line: str) -> str:
        pass

    @abstractmethod
    def get_comment_prefix(self) -> str:
        pass

    def extract_headings(self, content: str) -> list[dict[str, Any]]:
        """Return heading nodes in document order.

        Parsers that support fine-grained heading inspection should override this.
        """
        return []


class LatexParser(DocumentParser):
    """Parser for Chinese LaTeX Thesis."""

    HEADING_PATTERN = re.compile(
        r"\\(?P<command>chapter|section|subsection|subsubsection|paragraph)\*?"
        r"(?:\[[^\]]*\])?\{(?P<title>[^}]*)\}"
    )

    HEADING_LEVELS = {
        "chapter": 1,
        "section": 2,
        "subsection": 3,
        "subsubsection": 4,
        "paragraph": 5,
    }

    # Chinese Section patterns
    SECTION_PATTERNS = {
        "abstract": r"\\chapter{摘要}|\\section{摘要}",
        "introduction": r"\\chapter{绪论}|\\chapter{引言}|\\section{绪论}|\\section{引言}",
        "contribution": r"\\chapter{(?:创新点|主要贡献)}|\\section{(?:创新点|主要贡献)}",
        "related": r"\\chapter{相关工作}|\\section{相关工作}|\\section{文献综述}",
        "method": r"\\chapter{.*?(?:方法|原理|设计)}",
        "experiment": r"\\chapter{.*?(?:实验|实现|测试)}|\\section{.*?(?:实验|实现)}",
        "result": r"\\chapter{.*?(?:结果|性能)}|\\section{.*?(?:结果|性能)}",
        "discussion": r"\\chapter{.*?(?:讨论|分析)}|\\section{.*?(?:讨论|分析)}",
        "conclusion": r"\\chapter{结论}|\\chapter{总结与展望}|\\section{结论}",
    }

    PRESERVE_PATTERNS = [
        r"\\cite{[^}]+}",  # Citations
        r"\\ref{[^}]+}",  # References
        r"\\label{[^}]+}",  # Labels
        r"\\eqref{[^}]+}",  # Equation references
        r"\\autoref{[^}]+}",  # Auto references
        r"\$\$[^$]*\$\$",  # Display math
        r"\$[^$]*\$",  # Inline math
        r"\\begin{equation}.*?\\end{equation}",  # Equations
        r"\\begin{align}.*?\\end{align}",  # Align environments
        r"\\begin{.*?}.*?\\end{.*?}",  # Generic environments
        r"\\includegraphics(?:\[[^]]*\])?\{[^}]+\}",  # Images
        r"\\caption{[^}]+}",  # Captions
    ]

    def get_comment_prefix(self) -> str:
        return "%"

    def split_sections(self, content: str) -> dict[str, tuple[int, int]]:
        lines = content.split("\n")
        sections = {}
        current_section = "preamble"
        start_line = 0

        for i, line in enumerate(lines, 1):
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
        temp_line = line
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

    def extract_headings(self, content: str) -> list[dict[str, Any]]:
        headings: list[dict[str, Any]] = []
        for line_no, line in enumerate(content.split("\n"), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith(self.get_comment_prefix()):
                continue
            match = self.HEADING_PATTERN.search(stripped)
            if not match:
                continue
            command = match.group("command")
            headings.append(
                {
                    "line": line_no,
                    "level": self.HEADING_LEVELS[command],
                    "command": command,
                    "title": match.group("title").strip(),
                }
            )
        return headings


class TypstParser(DocumentParser):
    """Parser for Chinese Typst Thesis."""

    HEADING_PATTERN = re.compile(r"^(?P<marks>={1,5})\s+(?P<title>.+?)\s*$")

    # Chinese Section patterns for Typst
    # e.g. = 摘要, = 绪论
    SECTION_PATTERNS = {
        "abstract": r"^=\s+摘要",
        "introduction": r"^=\s+(?:绪论|引言)",
        "contribution": r"^=\s+(?:创新点|主要贡献)",
        "related": r"^=\s+(?:相关工作|文献综述)",
        "method": r"^=\s+.*(?:方法|原理|设计)",
        "experiment": r"^=\s+.*(?:实验|实现|测试)",
        "result": r"^=\s+.*(?:结果|性能)",
        "discussion": r"^=\s+.*(?:讨论|分析)",
        "conclusion": r"^=\s+.*(?:结论|总结与展望)",
    }

    PRESERVE_PATTERNS = [
        r"@[a-zA-Z0-9_-]+",  # Citations
        r"#cite\([^)]+\)",
        r"#figure\([^)]+\)",
        r"#table\([^)]+\)",
        r"\$[^$]+\$",
        r"//.*",
        r"/\*.*?\*/",
        r"<[a-zA-Z0-9_-]+>",
        r"#link\([^)]+\)",
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
            if line.startswith("//"):
                continue

            for section_name, pattern in self.SECTION_PATTERNS.items():
                if re.search(pattern, line):
                    if current_section != "preamble":
                        sections[current_section] = (start_line, i - 1)
                    current_section = section_name
                    start_line = i
                    break

        if current_section != "preamble":
            sections[current_section] = (start_line, len(lines))

        return sections

    def extract_visible_text(self, line: str) -> str:
        temp_line = line
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

    def extract_headings(self, content: str) -> list[dict[str, Any]]:
        headings: list[dict[str, Any]] = []
        for line_no, line in enumerate(content.split("\n"), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith(self.get_comment_prefix()):
                continue
            match = self.HEADING_PATTERN.match(stripped)
            if not match:
                continue
            headings.append(
                {
                    "line": line_no,
                    "level": len(match.group("marks")),
                    "command": "heading",
                    "title": match.group("title").strip(),
                }
            )
        return headings


def get_parser(file_path: Any) -> DocumentParser:
    """Factory method to get appropriate parser."""
    path_str = str(file_path).lower()
    if path_str.endswith(".typ"):
        return TypstParser()
    return LatexParser()


def _normalize_whitespace(text: str) -> str:
    """Collapse whitespace to single spaces."""
    return re.sub(r"\s+", " ", text).strip()


def _strip_latex_markup(text: str) -> str:
    """Remove LaTeX commands from text, keeping content."""
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])*\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\[a-zA-Z]+\*?", "", text)
    text = re.sub(r"[{}]", "", text)
    return _normalize_whitespace(text)


def extract_title(content: str) -> str:
    """Extract document title from Chinese LaTeX thesis source.

    Supports \\ctitle, \\title commands commonly used in Chinese thesis templates.
    """
    # Chinese title: \ctitle{...}
    ctitle = re.search(r"\\ctitle\{(.+?)\}", content, re.DOTALL)
    if ctitle:
        return _strip_latex_markup(ctitle.group(1))

    # Standard: \title{...}
    title = re.search(r"\\title(?:\[[^\]]*\])?\{(.+?)\}", content, re.DOTALL)
    if title:
        return _strip_latex_markup(title.group(1))

    return ""


def extract_abstract(content: str) -> str:
    """Extract abstract text from Chinese LaTeX thesis source.

    Supports \\cabstract, \\begin{cabstract}, \\begin{abstract} environments.
    """
    # Chinese abstract environment: \begin{cabstract}...\end{cabstract}
    cab = re.search(r"\\begin{cabstract}(.*?)\\end{cabstract}", content, re.DOTALL)
    if cab:
        return _strip_latex_markup(cab.group(1))

    # Standard abstract environment
    ab = re.search(r"\\begin{abstract}(.*?)\\end{abstract}", content, re.DOTALL)
    if ab:
        return _strip_latex_markup(ab.group(1))

    # Section-based: \chapter{摘要} or \section{摘要}
    sec = re.search(
        r"\\(?:chapter|section)\{摘要\}(.*?)(?=\\(?:chapter|section)\{|\\end\{document\}|\Z)",
        content,
        re.DOTALL,
    )
    if sec:
        return _strip_latex_markup(sec.group(1))

    return ""
