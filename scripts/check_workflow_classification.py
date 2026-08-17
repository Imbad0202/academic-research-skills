#!/usr/bin/env python3
"""Defrift lint for the CI workflow classification table (#755).

docs/ARCHITECTURE.md §7.1 claims to classify EVERY workflow's enforcement
strength — a completeness claim that silently rots when a workflow is
added, renamed, or removed. This lint pins the mechanical halves and
deliberately nothing else — whether a row's class honestly describes its
workflow's behavior stays owned by code review (degradation-registry
posture):

  WC-1  Inventory sync, both directions: every *.yml / *.yaml under
        .github/workflows/ has exactly one well-formed 5-cell table row,
        and every row names an existing workflow file.
  WC-2  Every row's Class cell begins with one of the closed four-term
        vocabulary — Blocking / Advisory / Administrative / Post-push
        detection — as a whole term (qualifiers may follow after a
        boundary; `Blockingg` does not count).
  WC-3  The bolded count line recomputes from the Class column: total,
        blocking, advisory, administrative, and post-push numbers must
        all match the table.
  WC-4  Every `[bypass-token]` named in a row's Bypass cell appears
        verbatim in that row's workflow file, on a non-comment line (a
        renamed token cannot leave the table stale while CI stays green,
        and a stale token surviving only in a YAML comment does not
        count; one surviving only inside a non-comment echo/log string
        is an accepted edge).

Exit 0 when all hold; exit 1 with one line per violation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _skill_lint import heading_section

DOC_RELPATH = Path("docs/ARCHITECTURE.md")
SECTION_HEADING = "### 7.1 CI workflow enforcement classes (#755)"
WORKFLOWS_DIR = Path(".github/workflows")

CLASS_VOCABULARY = (
    "Blocking",
    "Advisory",
    "Administrative",
    "Post-push detection",
)
# The count line tallies by leading class term (order: total, then one count
# per vocabulary term as worded in the sentence).
_COUNT_LINE_RE = re.compile(
    r"\*\*(\d+) workflows — (\d+) blocking[^,]*,\s+(\d+)\s+advisory,"
    r"\s+(\d+) administrative,\s+(\d+) post-push detection\.\*\*",
    re.DOTALL,
)
_FILENAME_CELL_RE = re.compile(r"`([^`]+\.ya?ml)`")
_BYPASS_TOKEN_RE = re.compile(r"\[[a-z][a-z-]*\]")
# Any bracketed span in a Bypass cell must BE a well-formed token — a typo
# spelling like `[skip_cooldown]` fails loudly instead of silently skipping
# WC-4.
_ANY_BRACKET_RE = re.compile(r"\[[^\]]+\]")
# Markdown cell split on unescaped pipes only (`\|` stays inside a cell).
_CELL_SPLIT_RE = re.compile(r"(?<!\\)\|")


def _table_rows(section: str) -> tuple[list[list[str]], list[str]]:
    """(data rows, malformed-first-cell errors). Every pipe row that is not
    the header or the separator must open with a backticked workflow
    filename — a bogus row cannot silently drop out of WC-1/WC-3."""
    rows: list[list[str]] = []
    errors: list[str] = []
    for line in section.split("\n"):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in _CELL_SPLIT_RE.split(stripped)]
        # Leading/trailing empties from the outer pipes.
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        if not cells:
            continue
        if cells[0] == "Workflow":
            continue  # header row
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            continue  # separator row
        if _FILENAME_CELL_RE.fullmatch(cells[0]):
            rows.append(cells)
        else:
            errors.append(
                f"WC-1: table row opening with {cells[0]!r} does not name a "
                f"backticked workflow file — malformed or misplaced row"
            )
    return rows, errors


def _class_term(class_cell: str) -> str | None:
    """The vocabulary term the cell begins with — as a whole term, followed
    by end-of-cell, whitespace, or an opening parenthesis."""
    for term in sorted(CLASS_VOCABULARY, key=len, reverse=True):
        if class_cell == term or class_cell.startswith(term + " ") or (
            class_cell.startswith(term + "(")
        ):
            return term
    return None


def run_all_checks(root: Path) -> list[str]:
    doc_path = root / DOC_RELPATH
    if not doc_path.exists():
        return [f"WC-1: {DOC_RELPATH} is missing"]
    doc_text = doc_path.read_text(encoding="utf-8")
    section = heading_section(doc_text, SECTION_HEADING)
    if section is None:
        return [
            f"WC-1: section '{SECTION_HEADING}' not found in {DOC_RELPATH}"
        ]
    rows, errors = _table_rows(section)

    on_disk = {
        p.name
        for pattern in ("*.yml", "*.yaml")
        for p in (root / WORKFLOWS_DIR).glob(pattern)
    }
    in_table = [
        _FILENAME_CELL_RE.fullmatch(cells[0]).group(1) for cells in rows
    ]
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
    for name in sorted({n for n in in_table if in_table.count(n) > 1}):
        errors.append(f"WC-1: workflow '{name}' has more than one table row")

    tally: dict[str, int] = {term: 0 for term in CLASS_VOCABULARY}
    for name, cells in zip(in_table, rows):
        # Cells: workflow | trigger | what it checks | class | bypass.
        if len(cells) != 5:
            errors.append(
                f"WC-1: row '{name}' has {len(cells)} cells, expected 5"
            )
            continue
        term = _class_term(cells[3])
        if term is None:
            errors.append(
                f"WC-2: row '{name}' class cell {cells[3]!r} does not begin "
                f"with a whole term from {list(CLASS_VOCABULARY)}"
            )
        else:
            tally[term] += 1
        if name in on_disk:
            # Full-comment lines don't execute: a token surviving only in a
            # comment must not satisfy WC-4.
            workflow_text = "\n".join(
                line
                for line in (root / WORKFLOWS_DIR / name)
                .read_text(encoding="utf-8")
                .split("\n")
                if not line.lstrip().startswith("#")
            )
            for span in _ANY_BRACKET_RE.findall(cells[4]):
                if not _BYPASS_TOKEN_RE.fullmatch(span):
                    errors.append(
                        f"WC-4: bypass cell of '{name}' carries {span!r}, "
                        f"which is not a well-formed [lowercase-hyphen] "
                        f"token — typo or unsupported spelling"
                    )
            for token in _BYPASS_TOKEN_RE.findall(cells[4]):
                if token not in workflow_text:
                    errors.append(
                        f"WC-4: bypass token '{token}' in the '{name}' row "
                        f"does not appear in {WORKFLOWS_DIR / name} — "
                        f"renamed or removed token"
                    )

    count_match = _COUNT_LINE_RE.search(section)
    if not count_match:
        errors.append(
            "WC-3: the bolded count line is missing or no longer matches "
            "the expected sentence shape"
        )
    else:
        stated = [int(g) for g in count_match.groups()]
        actual = [
            len(rows),
            tally["Blocking"],
            tally["Advisory"],
            tally["Administrative"],
            tally["Post-push detection"],
        ]
        if stated != actual:
            errors.append(
                f"WC-3: count line states "
                f"total/blocking/advisory/administrative/post-push = "
                f"{stated}, table has {actual}"
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
    print("check_workflow_classification: OK (WC-1..WC-4)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
