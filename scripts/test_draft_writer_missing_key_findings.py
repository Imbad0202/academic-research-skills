"""The draft writer must not infer findings from a source title or method (#993).

Reads the shipped agent prompt directly. No production helper.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT = REPO_ROOT / "academic-paper" / "agents" / "draft_writer_agent.md"

MISSING_ISSUE = "Source annotation missing Key Findings"
GAP = "[MATERIAL GAP: key findings of <source>]"
# The pre-#993 handling cell. Kept inline so the acceptance predicate can
# reject it without a fixture file.
OLD_HANDLING = "Use source's Title + Method to infer likely contribution direction"
INFER_LIKELY = "infer likely contribution"

_STATE_FINDING = re.compile(
    r"(?<!do not )(?<!Do not )\b(?:state|draft|report|write|present)\b"
    r"(?:\s+\w+){0,4}\s+findings?\b",
    re.IGNORECASE,
)
_PROMOTE_FIELD = re.compile(
    r"(?<!do not )(?<!Do not )\b(?:title|method)\b(?:\s+\w+){0,8}\s+"
    r"(?:as|into)\s+(?:a\s+|the\s+)?(?:result|contribution|finding|hypothesis)\b",
    re.IGNORECASE,
)
_INFER_FINDING = re.compile(
    r"(?<!do not )(?<!Do not )\binfer\b(?:\s+\w+){0,8}\s+"
    r"(?:a\s+|the\s+|likely\s+)?(?:result|contribution|finding|hypothesis)\b",
    re.IGNORECASE,
)


def _table_rows(text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != 2:
            continue
        if cells[0] in {"Issue", "Missing Item", "Type"} or set(cells[0]) <= {"-"}:
            continue
        rows.append((cells[0], cells[1]))
    return rows


def _missing_findings_row(text: str) -> tuple[str, str]:
    matches = [row for row in _table_rows(text) if row[0] == MISSING_ISSUE]
    assert len(matches) == 1, matches
    return matches[0]


def gap_required(issue: str) -> bool:
    """The key-findings gap applies only when that field is missing."""
    return issue == MISSING_ISSUE


def tells_writer_to_state_a_finding(cell: str) -> bool:
    return _STATE_FINDING.search(cell) is not None


def turns_title_or_method_into_finding(cell: str) -> bool:
    """True when title or method is used as a result, contribution, finding, or hypothesis."""
    return _PROMOTE_FIELD.search(cell) is not None or _INFER_FINDING.search(cell) is not None


def accepts_handling(cell: str) -> bool:
    """Reject a handling that tells the writer to infer a likely contribution."""
    return INFER_LIKELY not in cell


def test_missing_key_findings_marks_gap_without_stating_a_finding() -> None:
    issue, cell = _missing_findings_row(AGENT.read_text(encoding="utf-8"))
    assert issue == MISSING_ISSUE
    assert GAP in cell
    assert "annotation fields that are actually present" in cell
    assert not tells_writer_to_state_a_finding(cell)


def test_present_key_findings_stay_outside_this_row() -> None:
    text = AGENT.read_text(encoding="utf-8")
    issue, cell = _missing_findings_row(text)
    assert "missing Key Findings" in issue
    assert gap_required(issue)
    assert GAP in cell
    # A present Key Findings field is not this row, so the test does not
    # require the gap tag for it or for any neighboring row.
    assert not gap_required("Source annotation with Key Findings present")
    for other_issue, other_cell in _table_rows(text):
        if gap_required(other_issue):
            continue
        assert GAP not in other_cell


def test_title_and_method_are_cited_as_topic_and_method() -> None:
    _, cell = _missing_findings_row(AGENT.read_text(encoding="utf-8"))
    assert "title as topic" in cell
    assert "method as method" in cell
    assert not turns_title_or_method_into_finding(cell)


def test_infer_likely_contribution_is_rejected() -> None:
    _, cell = _missing_findings_row(AGENT.read_text(encoding="utf-8"))
    assert INFER_LIKELY not in cell
    assert accepts_handling(cell)
    assert not accepts_handling(OLD_HANDLING)
