"""Pin the formatter's content-integrity rule (#1162): word counts are compared
before and after conversion, a deviation of 1% or more only triggers a
section-by-section comparison with the Draft, the selected reference list, and the
bilingual abstracts and keywords, and the check fails on lost, duplicated, or added
content, not on the deviation itself."""

from __future__ import annotations

from tests.test_formatter_1071 import FORMATTER, _rows_with_first_cell

COMPARED = "compare word counts before and after conversion"

ROW_PASS_CRITERIA = (
    "Compare word counts before and after conversion. A deviation of 1% or more "
    "triggers a section-by-section comparison with the Draft, the selected "
    "reference list, and the bilingual abstracts and keywords. A word-count "
    "deviation alone does not fail this check; any lost content does, and so does "
    "text the conversion duplicated and text it added that is in none of those "
    "inputs. A section this file tells the formatter to add, such as the Data "
    "Availability Statement or the AI Disclosure Statement, may be added once when "
    "the Draft does not already have it; a second copy still fails. A missing "
    "Abstract or Limitations section is reported, not written (Step 2.4 / 2.6). An "
    "existing AI Disclosure Statement that is incomplete may be completed in place "
    "with the standard text. A word-count change from converting the citation style "
    "(for example author-year to numbered or numbered to author-year), or from "
    "reformatting reference-list entries to the target style (for example "
    "abbreviated journal titles or `et al.`), is neither lost nor added content. "
    "Stripping the `<!--protected-hedges: ...-->` control comment (#548) is "
    "required, not content loss. In the blind-review version only, removing all "
    "author information as directed by the Author Information step is an allowed "
    "difference."
)
ROW_FAILURE_HANDLING = (
    "Restore missing content. In the blind-review version only, leave out all "
    "author information removed as directed by the Author Information step. Remove "
    "text the conversion duplicated and any addition this check does not allow."
)
CHECKLIST_ITEM = (
    "□ Format conversion did not lose, duplicate, or add content (compare word "
    "counts before and after conversion; a deviation of 1% or more triggers a "
    "section-by-section comparison with the Draft, the selected reference list, and "
    "the bilingual abstracts and keywords; a word-count deviation alone does not "
    "fail this item, but any lost content does, and so does text the conversion "
    "duplicated and text it added that is in none of those inputs; a section this "
    "file tells the formatter to add, such as the Data Availability Statement or "
    "the AI Disclosure Statement, may be added once when the Draft does not already "
    "have it, and a second copy still fails; a missing Abstract or Limitations "
    "section is reported, not written (Step 2.4 / 2.6); an existing AI Disclosure "
    "Statement that is incomplete may be completed in place with the standard text; "
    "a word-count change from converting the citation style, for example "
    "author-year to numbered or numbered to author-year, or from reformatting "
    "reference-list entries to the target style, for example abbreviated journal "
    "titles or `et al.`, is neither lost nor added content; stripping the "
    "`<!--protected-hedges: ...-->` control comment (#548) is required, not content "
    "loss, since it is machine transport, consumed upstream by the abstract stage. "
    "In the blind-review version only, removing all author information as directed "
    "by the Author Information step is an allowed difference)"
)
TREE_BRANCH = (
    "├── Content loss, duplication, or addition ->\n"
    "│   1. Compare the Draft, the selected reference list, and the bilingual "
    "abstracts and keywords with the Formatted output section by section\n"
    "│   2. Re-insert missing text. In the blind-review version only, leave out "
    "all author information removed as directed by the Author Information step.\n"
    "│   3. Remove text the conversion duplicated and any addition the Content integrity "
    "check does not allow\n"
    "│   4. Re-run final checklist\n"
)
QUALITY_CHECKLIST_ITEM = (
    "- [ ] No content lost during formatting. In the blind-review version only, "
    "all author information removed as directed by the Author Information step "
    "is an allowed difference."
)
AI_DISCLOSURE_FAILURE_HANDLING = (
    "Insert the standard Disclosure text, or complete an existing statement in place "
    "with it"
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


def test_quality_checklist_content_item() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    section = text.split("### Content Integrity\n", 1)[1].split("\n#", 1)[0]
    items = [line for line in section.splitlines() if line.startswith("- [ ] No content")]
    assert items == [QUALITY_CHECKLIST_ITEM]


def test_ai_disclosure_row_allows_completion_in_place() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    rows = _rows_with_first_cell(text, "AI Disclosure")
    assert len(rows) == 1
    cells = [_collapse(cell) for cell in rows[0].split("|")]
    assert cells[3] == AI_DISCLOSURE_FAILURE_HANDLING
