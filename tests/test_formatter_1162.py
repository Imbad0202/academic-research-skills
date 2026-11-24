"""Pin the formatter's content-integrity rule (#1162): word counts are compared
before and after conversion, a deviation of 1% or more only triggers a
section-by-section comparison with the Draft, and the check fails on lost,
duplicated, or added content, not on the deviation itself."""

from __future__ import annotations

from tests.test_formatter_1071 import FORMATTER, _rows_with_first_cell

COMPARED = "compare word counts before and after conversion"

ROW_PASS_CRITERIA = (
    "Compare word counts before and after conversion. A deviation of 1% or more "
    "triggers a section-by-section comparison with the Draft. A word-count deviation "
    "alone does not fail this check; any lost content does, and so does text the "
    "conversion duplicated or added, apart from sections the target format requires "
    "and the AI Disclosure Statement. A word-count change from converting the "
    "citation style (for example author-year to numbered or numbered to author-year) "
    "is neither lost nor added content"
)
ROW_FAILURE_HANDLING = (
    "Find missing content and restore it; remove text the conversion duplicated or added"
)
CHECKLIST_RULE = (
    "(compare word counts before and after conversion; a deviation of 1% or more "
    "triggers a section-by-section comparison with the Draft; a word-count deviation "
    "alone does not fail this item, but any lost content does, and so does text the "
    "conversion duplicated or added, apart from sections the target format requires "
    "and the AI Disclosure Statement; a word-count change from converting the "
    "citation style, for example author-year to numbered or numbered to author-year, "
    "is neither lost nor added content; stripping"
)


def _collapse(text: str) -> str:
    return " ".join(text.split())


def _content_integrity_row() -> list[str]:
    text = FORMATTER.read_text(encoding="utf-8")
    rows = _rows_with_first_cell(text, "Content integrity")
    assert len(rows) == 1, (
        "expected exactly one Markdown row whose first cell is 'Content integrity', "
        f"found {len(rows)}"
    )
    return [_collapse(cell) for cell in rows[0].split("|")]


def _content_loss_item() -> str:
    text = FORMATTER.read_text(encoding="utf-8")
    section = text.split("=== Content Integrity ===\n", 1)[1].split("\n===", 1)[0]
    items = [line for line in section.splitlines() if "did not cause content loss" in line]
    assert len(items) == 1, (
        "expected exactly one Content Integrity checklist item about content loss, "
        f"found {len(items)}"
    )
    return _collapse(items[0])


def test_quality_gate_content_integrity_row() -> None:
    cells = _content_integrity_row()
    assert COMPARED in cells[2].lower()
    assert cells[2] == ROW_PASS_CRITERIA
    assert cells[3] == ROW_FAILURE_HANDLING


def test_final_checklist_content_loss_item() -> None:
    item = _content_loss_item()
    assert COMPARED in item.lower()
    assert CHECKLIST_RULE in item
    assert "deviation < 1%" not in item


def test_failure_strategy_removes_duplicated_or_added_text() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    branch = text.split("├── Content loss, duplication, or addition ->\n", 1)[1]
    branch = branch.split("\n├──", 1)[0]
    assert "Find missing paragraphs, re-insert" in branch
    assert "Remove text the conversion duplicated or added" in branch
