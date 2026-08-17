#!/usr/bin/env python3
"""Defrift lint for the CI workflow classification table (#755).

docs/ARCHITECTURE.md §7.1 claims to classify EVERY workflow's enforcement
strength — a completeness claim that silently rots when a workflow is added,
renamed, or removed. This lint pins the two mechanical halves and
deliberately nothing else — whether a row's class honestly describes its
workflow's behavior stays owned by code review (degradation-registry
posture):

  WC-1  Inventory sync, both directions: every *.yml under
        .github/workflows/ has exactly one table row, and every row names
        an existing workflow file.
  WC-2  Every row's Class cell begins with one of the closed four-term
        vocabulary: Blocking / Advisory / Administrative / Post-push
        detection (qualifiers may follow).

Exit 0 when both hold; exit 1 with one line per violation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DOC_RELPATH = Path("docs/ARCHITECTURE.md")
SECTION_HEADING = "### 7.1 CI workflow enforcement classes"
WORKFLOWS_DIR = Path(".github/workflows")

CLASS_VOCABULARY = (
    "Blocking",
    "Advisory",
    "Administrative",
    "Post-push detection",
)

# A table row whose first cell is a backticked workflow filename.
_ROW_RE = re.compile(r"^\|\s*`([^`]+\.yml)`\s*\|")


def _section_body(md_text: str) -> str | None:
    """Body of the §7.1 section, up to the next heading of any level."""
    lines = md_text.split("\n")
    body: list[str] = []
    in_section = False
    for line in lines:
        if line.startswith(SECTION_HEADING):
            in_section = True
            continue
        if in_section and re.match(r"#{2,3} ", line):
            break
        if in_section:
            body.append(line)
    return "\n".join(body) if in_section else None


def _table_rows(section: str) -> list[tuple[str, list[str]]]:
    """(workflow filename, all cells) per data row of the classification
    table."""
    rows: list[tuple[str, list[str]]] = []
    for line in section.split("\n"):
        match = _ROW_RE.match(line)
        if not match:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append((match.group(1), cells))
    return rows


def run_all_checks(root: Path) -> list[str]:
    doc_path = root / DOC_RELPATH
    if not doc_path.exists():
        return [f"WC-1: {DOC_RELPATH} is missing"]
    section = _section_body(doc_path.read_text(encoding="utf-8"))
    if section is None:
        return [
            f"WC-1: section '{SECTION_HEADING}' not found in {DOC_RELPATH}"
        ]
    rows = _table_rows(section)
    errors: list[str] = []

    on_disk = {
        p.name for p in sorted((root / WORKFLOWS_DIR).glob("*.yml"))
    }
    in_table = [name for name, _ in rows]
    for name in sorted(on_disk - set(in_table)):
        errors.append(
            f"WC-1: workflow '{name}' exists on disk but has no row in the "
            f"§7.1 classification table — classify it (new or renamed "
            f"workflow)"
        )
    for name in sorted(set(in_table) - on_disk):
        errors.append(
            f"WC-1: table row '{name}' names no file under {WORKFLOWS_DIR} "
            f"(removed or renamed workflow)"
        )
    duplicates = {n for n in in_table if in_table.count(n) > 1}
    for name in sorted(duplicates):
        errors.append(f"WC-1: workflow '{name}' has more than one table row")

    for name, cells in rows:
        # Cells: workflow | trigger | what it checks | class | bypass.
        if len(cells) < 5:
            errors.append(
                f"WC-2: row '{name}' has {len(cells)} cells, expected 5"
            )
            continue
        class_cell = cells[3]
        if not class_cell.startswith(CLASS_VOCABULARY):
            errors.append(
                f"WC-2: row '{name}' class cell {class_cell!r} does not "
                f"begin with one of {list(CLASS_VOCABULARY)}"
            )
    return errors


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    errors = run_all_checks(root)
    if errors:
        for line in errors:
            print(f"ERROR: {line}", file=sys.stderr)
        print(
            f"check_workflow_classification: {len(errors)} violation(s)",
            file=sys.stderr,
        )
        return 1
    print("check_workflow_classification: OK (WC-1..WC-2)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
