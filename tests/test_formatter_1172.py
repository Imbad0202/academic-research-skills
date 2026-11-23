"""Pin Vancouver in-text parentheses and the blind-review restore exception (#1172)."""

from __future__ import annotations

from tests.test_formatter_1071 import FORMATTER, _rows_with_first_cell

NUMBERED_CONVERSION_BULLET = (
    "- Replace author-year citations with [Number] for IEEE and (Number) for "
    "Vancouver. In `full` mode, retain verbatim a citation that a reported "
    "incoming mismatch names and that cannot be numbered without changing its "
    "content."
)

CONTENT_INTEGRITY_FAILURE_HANDLING = (
    "Find missing content and restore it. Author fields removed for the "
    "blind-review version are an allowed difference. Do not restore those "
    "fields in that version."
)

CONTENT_LOSS_STEP = (
    "│   2. Re-insert missing paragraphs. Author fields removed for the "
    "blind-review version are an allowed difference. Do not re-insert those "
    "fields in that version."
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
    branch = text.split("├── Content loss ->\n", 1)[1].split(
        "├── Journal format non-compliance ->", 1
    )[0]
    steps = [line for line in branch.splitlines() if line.startswith("│   2. ")]
    assert steps == [CONTENT_LOSS_STEP]
