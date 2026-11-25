"""Pin Vancouver in-text parentheses, the blind-review restore exception, and
style-directed reference-list author names (#1172)."""

from __future__ import annotations

from tests.test_formatter_1071 import FORMATTER, _rows_with_first_cell

NUMBERED_CONVERSION_BULLET = (
    "- Replace author-year citations with [Number] for IEEE and (Number) for "
    "Vancouver. In `full` mode, retain verbatim a citation that a reported "
    "incoming mismatch names and that cannot be numbered without changing its "
    "content."
)

CONTENT_INTEGRITY_FAILURE_HANDLING = (
    "Find missing content and restore it. Manuscript author fields removed for "
    "the blind-review version are an allowed difference. Do not restore those "
    "fields in that version. Remove text the conversion duplicated and any "
    "addition this check does not allow."
)

CONTENT_LOSS_STEP = (
    "│   2. Find missing text and re-insert it. Manuscript author fields "
    "removed for the blind-review version are an allowed difference. Do not "
    "re-insert those fields in that version."
)

REFERENCE_LIST_AUTHOR_CHECKBOX = (
    "- [ ] Reference-list author names follow the target style, including an "
    "applicable journal requirement: preserve author order and spelling, list "
    "every required name, and use et al. only where that rule calls for "
    "truncation (Vancouver lists all six authors when there are six, and the "
    "first six followed by et al. for more than six; a style that requires all "
    "seven names retains all seven)."
)

OLD_UNCONDITIONAL_AUTHOR_CHECKBOX = (
    "- [ ] All author names preserved (no names lost or misspelled)"
)

ADJACENT_REFERENCE_CHECKS = (
    "- [ ] Total citation count matches (in-text: input count == output count)",
    "- [ ] Total reference count matches (reference list: input count == output count)",
    "- [ ] All years preserved",
    "- [ ] All titles preserved (case may change per target format rules)",
    "- [ ] All DOIs preserved",
)


def _markdown_cells(line: str) -> list[str]:
    cells = [cell.strip() for cell in line.split("|")]
    if cells and cells[0] == "":
        cells = cells[1:]
    if cells and cells[-1] == "":
        cells = cells[:-1]
    return cells


def test_numbered_conversion_follows_style_table() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    features = text.split("### Format-Specific Features\n", 1)[1].split(
        "\n### ", 1
    )[0]
    table_rows = [line for line in features.splitlines() if line.startswith("|")]
    header = _markdown_cells(table_rows[0])
    in_text_rows = [
        line
        for line in table_rows
        if _markdown_cells(line)[0] == "In-text style"
    ]
    assert len(in_text_rows) == 1
    in_text = dict(zip(header, _markdown_cells(in_text_rows[0]), strict=True))
    assert in_text["IEEE"] == "[Number]"
    assert in_text["Vancouver"] == "(Number)"

    section = text.split(
        "### Handling Numbered References (IEEE / Vancouver)\n", 1
    )[1].split("\n### ", 1)[0]
    to_instructions = section.split(
        "When converting **to** numbered formats:\n", 1
    )[1].split("When converting **from** numbered formats:", 1)[0]
    bullets = [
        line
        for line in to_instructions.splitlines()
        if line.startswith("- Replace author-year citations")
    ]
    assert len(bullets) == 1
    assert bullets[0] == NUMBERED_CONVERSION_BULLET


def test_content_integrity_failure_handling_allows_blind_review_removal() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    rows = _rows_with_first_cell(text, "Content integrity")
    assert len(rows) == 1, (
        "expected exactly one Markdown row whose first cell is "
        "'Content integrity', "
        f"found {len(rows)}"
    )
    gates = text.split("## Quality Gates\n", 1)[1].split("\n## ", 1)[0]
    header_rows = [
        line
        for line in gates.splitlines()
        if line.startswith("|") and _markdown_cells(line)[0] == "Check Item"
    ]
    assert len(header_rows) == 1
    header = _markdown_cells(header_rows[0])
    cells = _markdown_cells(rows[0])
    assert cells[header.index("Failure Handling")] == (
        CONTENT_INTEGRITY_FAILURE_HANDLING
    )


def test_content_loss_recovery_allows_blind_review_removal() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    branch = text.split("├── Content loss, duplication, or addition ->\n", 1)[1].split(
        "├── Journal format non-compliance ->", 1
    )[0]
    steps = [line for line in branch.splitlines() if line.startswith("│   2. ")]
    assert steps == [CONTENT_LOSS_STEP]


def test_verification_checklist_reference_authors_follow_the_target_style() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    section = text.split("### Verification Checklist\n", 1)[1].split("\n---\n", 1)[0]
    author_items = [
        line
        for line in section.splitlines()
        if line.startswith("- [ ]") and "author" in line.lower()
    ]
    assert len(author_items) == 1
    checkbox = author_items[0]
    assert checkbox == REFERENCE_LIST_AUTHOR_CHECKBOX
    assert OLD_UNCONDITIONAL_AUTHOR_CHECKBOX not in section
    for required in (
        "author order",
        "spelling",
        "every required name",
        "et al.",
        "truncation",
        "applicable journal requirement",
        "all six authors when there are six",
        "first six followed by et al. for more than six",
        "requires all seven names retains all seven",
    ):
        assert required in checkbox
    for adjacent in ADJACENT_REFERENCE_CHECKS:
        assert adjacent in section
