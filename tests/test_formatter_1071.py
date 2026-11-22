"""Pin the #1071 formatter quality-gate exceptions and Phase 7 caller row.

Each case reads ``academic-paper/agents/formatter_agent.md`` and selects the
one Markdown table row whose first cell is the case id. The required literal
must occur in that row, so a one-row regression fails only its own case.
"""

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
        "retaining a citation verbatim or preserving a reference-list entry, "
        "that item satisfies this check. Continue formatting",
        id="Format compliance",
    ),
    pytest.param(
        "Journal requirements",
        "In `full` mode, when a reported incoming mismatch requires "
        "retaining a citation verbatim or preserving a reference-list entry, "
        "that item satisfies this check when the Output Package warning names the journal "
        "requirement that could not be applied. Continue formatting",
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
