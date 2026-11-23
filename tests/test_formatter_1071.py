"""Pin the formatter's Step 4 check, quality-gate exceptions, and Phase 7 caller row."""

from __future__ import annotations

from pathlib import Path

import pytest

FORMATTER = (
    Path(__file__).resolve().parents[1]
    / "academic-paper"
    / "agents"
    / "formatter_agent.md"
)

CASES = [
    pytest.param(
        "Format compliance",
        "In `full` mode, when a reported incoming mismatch requires "
        "retaining a citation verbatim, that citation satisfies this check. "
        "When such a mismatch requires preserving a reference-list entry, "
        "the entry still follows the target format; only a rule that would "
        "remove the entry does not apply to it. Continue formatting",
        id="Format compliance",
    ),
    pytest.param(
        "Journal requirements",
        "In `full` mode, when a reported incoming mismatch requires "
        "retaining a citation verbatim, a journal requirement that would "
        "change that citation does not apply to that citation. When such a "
        "mismatch requires preserving a reference-list entry, a journal "
        "requirement that would remove the entry does not apply to that "
        "entry, and every other requirement still does. The Output Package "
        "warning names each requirement not applied this way; all other "
        "citations and entries are checked as usual. Continue formatting",
        id="Journal requirements",
    ),
    pytest.param(
        "Phase 7 caller",
        "(a Round 1 Accept, or early formatting after Phase 5a and before "
        "any revision round), use the initial Phase 5a Corrected Draft",
        id="Phase 7 caller",
    ),
]


def _rows_with_first_cell(text: str, label: str) -> list[str]:
    """Return every Markdown table row whose first cell equals ``label``."""
    rows: list[str] = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = line.split("|")
        if len(cells) < 3:
            continue
        if cells[1].strip() == label:
            rows.append(line)
    return rows


@pytest.mark.parametrize(("row_label", "required_literal"), CASES)
def test_formatter_1071_row_contains_literal(
    row_label: str, required_literal: str
) -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    rows = _rows_with_first_cell(text, row_label)
    assert len(rows) == 1, (
        f"expected exactly one Markdown row whose first cell is {row_label!r}, "
        f"found {len(rows)}"
    )
    assert required_literal in rows[0]


def test_step_4_format_compliance_accepts_required_preservation() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    step_4 = text.split("Step 4: Verification\n", 1)[1].split("\n```", 1)[0]
    assert (
        "- Format compliance check: output matches target format rules. "
        "In `full` mode, when a reported incoming mismatch requires retaining "
        "a citation verbatim, that citation satisfies this check. "
        "When such a mismatch requires preserving a reference-list entry, "
        "the entry still follows the target format; only a rule that would "
        "remove the entry does not apply to it."
    ) in " ".join(step_4.split())
