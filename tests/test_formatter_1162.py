"""Pin the formatter's content-integrity rule: a word-count deviation of 1% or
more starts a section-by-section comparison and is not a failure on its own (#1162)."""

from __future__ import annotations

from tests.test_formatter_1071 import FORMATTER, _rows_with_first_cell

TRIGGER = "a deviation of 1% or more triggers a section-by-section content comparison"
FAIL_RULE = "fails only when that comparison finds lost content"


def test_quality_gate_content_integrity_fails_only_on_lost_content() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    rows = _rows_with_first_cell(text, "Content integrity")
    assert len(rows) == 1, (
        "expected exactly one Markdown row whose first cell is 'Content integrity', "
        f"found {len(rows)}"
    )
    pass_criteria = " ".join(rows[0].split("|")[2].split())
    assert TRIGGER in pass_criteria
    assert FAIL_RULE in pass_criteria
    assert "deviation < 1%" not in rows[0]


def test_final_checklist_content_loss_item_uses_word_count_as_trigger() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    section = text.split("=== Content Integrity ===\n", 1)[1].split("\n===", 1)[0]
    items = [line for line in section.splitlines() if "did not cause content loss" in line]
    assert len(items) == 1, (
        "expected exactly one Content Integrity checklist item about content loss, "
        f"found {len(items)}"
    )
    item = " ".join(items[0].split())
    assert TRIGGER in item
    assert FAIL_RULE in item
    assert "deviation < 1%" not in item
