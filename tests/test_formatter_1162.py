"""Pin the formatter's content-integrity rule (#1162): word counts are compared
before and after conversion, a deviation of 1% or more only triggers a
section-by-section comparison with the Draft and the other inputs, and the check
fails on lost, duplicated, or added content, not on the deviation itself."""

from __future__ import annotations

from tests.test_formatter_1071 import FORMATTER, _rows_with_first_cell

COMPARED = "compare word counts before and after conversion"

ROW_PASS_CRITERIA = (
    "Compare word counts before and after conversion. A deviation of 1% or more "
    "triggers a section-by-section comparison with the Draft and the other inputs in "
    "Input Sources. A word-count deviation alone does not fail this check; any lost "
    "content does, and so does text the conversion duplicated and text it added that "
    "is in none of those inputs. A section the target format requires, or the AI "
    "Disclosure Statement, may be added once when the Draft does not already have it; "
    "a second copy still fails. A word-count change from converting the citation style "
    "(for example author-year to numbered or numbered to author-year), or from "
    "reformatting reference-list entries to the target style (for example abbreviated "
    "journal titles or `et al.`), is neither lost nor added content. Stripping the "
    "`<!--protected-hedges: ...-->` control comment (#548) is required, not content loss"
)
ROW_FAILURE_HANDLING = (
    "Find missing content and restore it; remove duplicated text and any addition "
    "this check does not allow"
)
CHECKLIST_ITEM = (
    "□ Format conversion did not lose, duplicate, or add content (compare word counts "
    "before and after conversion; a deviation of 1% or more triggers a "
    "section-by-section comparison with the Draft and the other inputs in Input "
    "Sources; a word-count deviation alone does not fail this item, but any lost "
    "content does, and so does text the conversion duplicated and text it added that "
    "is in none of those inputs; a section the target format requires, or the AI "
    "Disclosure Statement, may be added once when the Draft does not already have it, "
    "and a second copy still fails; a word-count change from converting the citation "
    "style, for example author-year to numbered or numbered to author-year, or from "
    "reformatting reference-list entries to the target style, for example abbreviated "
    "journal titles or `et al.`, is neither lost nor added content; stripping the "
    "`<!--protected-hedges: ...-->` control comment (#548) is required, not content "
    "loss, since it is machine transport, consumed upstream by the abstract stage)"
)
TREE_BRANCH = (
    "├── Content loss, duplication, or addition ->\n"
    "│   1. Compare the Draft and the other inputs with the Formatted output section by section\n"
    "│   2. Find missing text, re-insert\n"
    "│   3. Remove duplicated text and any addition the Content integrity check does not allow\n"
    "│   4. Re-run final checklist\n"
)


def _collapse(text: str) -> str:
    return " ".join(text.split())


def test_quality_gate_content_integrity_row() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    rows = _rows_with_first_cell(text, "Content integrity")
    assert len(rows) == 1, (
        "expected exactly one Markdown row whose first cell is 'Content integrity', "
        f"found {len(rows)}"
    )
    cells = [_collapse(cell) for cell in rows[0].split("|")]
    assert COMPARED in cells[2].lower()
    assert cells[2] == ROW_PASS_CRITERIA
    assert cells[3] == ROW_FAILURE_HANDLING


def test_final_checklist_content_integrity_item() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    section = text.split("=== Content Integrity ===\n", 1)[1].split("\n===", 1)[0]
    items = [
        _collapse(line)
        for line in section.splitlines()
        if line.startswith("□ Format conversion did not")
    ]
    assert len(items) == 1, (
        "expected exactly one Content Integrity checklist item about format conversion, "
        f"found {len(items)}"
    )
    assert COMPARED in items[0].lower()
    assert items[0] == CHECKLIST_ITEM


def test_failure_strategy_branch() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    assert text.count(TREE_BRANCH) == 1
