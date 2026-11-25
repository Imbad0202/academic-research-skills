"""Pin year placement, IEEE/Vancouver conversion, APA template notes, the
element check, and blind-review section completeness (#1187)."""

from __future__ import annotations

from tests.test_formatter_1071 import FORMATTER, _rows_with_first_cell

YEAR_POSITION_ROW = (
    "| Year position | After author | After author | After publisher or "
    "volume/issue (bibliography) | End of entry | End of journal entry | "
    "After journal title |"
)

IEEE_VANCOUVER_PARAGRAPH = (
    "When converting between IEEE and Vancouver in either direction, keep "
    "the existing reference numbers and list order. Change only the in-text "
    "form ([Number] for IEEE, (Number) for Vancouver) and the reference-list "
    "entry format to match the target style."
)

LATEX_BIBLATEX_LINE = (
    r"\usepackage[style=apa,backend=biber]{biblatex} % APA example. "
    "Set style to the target biblatex style."
)

PANDOC_CSL_EXAMPLE = """\
# APA example. Set --csl to the CSL file for the target style.
pandoc paper.md -o paper.docx \\
  --reference-doc=template.docx \\
  --citeproc \\
  --bibliography=references.bib \\
  --csl=apa-7th.csl
"""

ELEMENT_CHECK = (
    "  - Element check: compare the extracted elements with the intermediate "
    "representation. Preserve every extracted value there, including all "
    "supplied author names when the target style truncates the rendered list."
)

CONTENT_INTEGRITY_SECTIONS = (
    "- [ ] All sections present and complete except, in the blind-review "
    "version only, whole author-information sections removed as directed by "
    "the Author Information step."
)

PREOUTPUT_SECTIONS = (
    "□ All sections exist and are complete (compare with Draft section by "
    "section) except, in the blind-review version only, whole "
    "author-information sections removed as directed by the Author "
    "Information step."
)


def _section(text: str, start: str, end: str) -> str:
    return text.split(start, 1)[1].split(end, 1)[0]


def _paragraphs(text: str) -> list[str]:
    return [block.strip("\n") for block in text.split("\n\n") if block.strip()]


def test_year_position_row() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    features = _section(text, "### Format-Specific Features\n", "\n### ")
    rows = _rows_with_first_cell(features, "Year position")
    assert len(rows) == 1
    assert rows[0] == YEAR_POSITION_ROW


def test_ieee_vancouver_keeps_numbers_and_order() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    section = _section(
        text,
        "### Handling Numbered References (IEEE / Vancouver)\n",
        "\n### ",
    )
    matches = [
        paragraph
        for paragraph in _paragraphs(section)
        if paragraph == IEEE_VANCOUVER_PARAGRAPH
    ]
    assert matches == [IEEE_VANCOUVER_PARAGRAPH]


def test_latex_template_marks_apa_biblatex_example() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    after = text.split("**LaTeX document structure template**:\n", 1)[1]
    block = after.split("```latex\n", 1)[1].split("\n```", 1)[0]
    lines = [
        line
        for line in block.splitlines()
        if line.startswith(r"\usepackage[style=apa,backend=biber]{biblatex}")
    ]
    assert lines == [LATEX_BIBLATEX_LINE]


def test_pandoc_commands_mark_apa_csl_example() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    commands = _section(text, "**Pandoc conversion commands**:\n", "\n**")
    block = commands.split("```bash\n", 1)[1].split("\n```", 1)[0]
    assert PANDOC_CSL_EXAMPLE in block + "\n"
    comment = "# APA example. Set --csl to the CSL file for the target style."
    comment_at = block.index(comment)
    command_at = block.index("pandoc paper.md -o paper.docx \\\n", comment_at)
    between = block[comment_at + len(comment) : command_at]
    assert between == "\n"
    command = block[command_at:].split("\n\n", 1)[0]
    assert "--csl=apa-7th.csl" in command
    assert command.endswith("--csl=apa-7th.csl")


def test_step4_element_check_preserves_extracted_authors() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    step_4 = _section(text, "Step 4: Verification\n", "\n```")
    lines = [line for line in step_4.splitlines() if "- Element check:" in line]
    assert len(lines) == 1
    assert lines[0] == ELEMENT_CHECK


def test_content_integrity_allows_blind_review_section_removal() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    section = _section(text, "### Content Integrity\n", "\n### ")
    lines = [
        line for line in section.splitlines() if line.startswith("- [ ] All sections")
    ]
    assert len(lines) == 1
    assert lines[0] == CONTENT_INTEGRITY_SECTIONS


def test_preoutput_checklist_allows_blind_review_section_removal() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    section = _section(text, "=== Content Integrity ===\n", "\n=== ")
    lines = [
        line for line in section.splitlines() if line.startswith("□ All sections")
    ]
    assert len(lines) == 1
    assert lines[0] == PREOUTPUT_SECTIONS
