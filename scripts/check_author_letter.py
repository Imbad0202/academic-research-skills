#!/usr/bin/env python3
"""Check the author letter against the manuscript and the decision package (#1078).

The author letter is the review rewritten for the author from the finished
Editorial Decision Package (``academic-paper-reviewer/SKILL.md`` § Author
letter; ``templates/author_letter_template.md``). A rewrite can turn a
paraphrase into a false quotation, carry a machine line into the letter, or
drop a revision item, so this script checks three things:

  quotes     every quotation occurs in the manuscript, by the check that the
             reviewer claim check (#1002) uses for a judge's quotation: the
             quotation marks of ``audit_panel_claims._QUOTED`` (“…”, "…",
             ‘…’, 「…」, 『…』) read in each paragraph or list item made one
             line, with blockquote marks removed, and
             ``dispatch_panel_claim_audit.evidence_ok`` with
             ``contradiction`` evidence. That check applies NFC, folds
             case, makes each whitespace run one space, removes the double
             quotation marks " “ ”, and reads ‘ ’ as '; it keeps 「」, 『』,
             and every other mark. A quotation that differs from the
             manuscript only in what it folds passes. It finds no word boundary
             ("significant" passes inside "insignificant"), reads no other
             quotation marks (« », „ “), and a line break between two CJK
             characters, in the letter or in the manuscript file, becomes a
             space that the other text does not have, so the quotation is
             reported as not found. An unpaired or empty mark
             can pair with the wrong mark (`"" and "invented"` reads
             `" and "`), and the words after it are then not checked.
             Skipped, with a notice, when no manuscript file is given.
  ids        the whole letter, the appendix included, holds no machine line,
             internal id, HTML comment, or fenced code block. Bare transport refs (``R1``, ``S2``) are not
             searched for, because a manuscript location such as "Table S1"
             has the same form.
  item map   the appendix is the letter's last level-2 heading, and the item
             map is its last level-3 subsection. The item map holds one table
             of two columns, and no other line with a pipe: a header row and a delimiter row, then one row
             for each change (an item number from 1, then a ref), and no rows when
             there are no changes. Outer pipes are optional. Each item
             number appears once, and the refs are the rows of the Required
             and Suggested Revisions tables of the package, each once. The
             script does not compare the item numbers with the numbered
             items of the body.

Exit 0 pass / 1 problems found / 2 missing or unreadable input.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from audit_panel_claims import _QUOTED
    from dispatch_panel_claim_audit import evidence_ok
except ImportError:  # pragma: no cover - dual-path import
    from scripts.audit_panel_claims import _QUOTED
    from scripts.dispatch_panel_claim_audit import evidence_ok

# A delimiter row of two or more columns; outer pipes are optional.
_TABLE_RULE = re.compile(r"^\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)+\|?\s*$")
_PARAGRAPH = re.compile(r"\n\s*\n")
# A list item mark at the start of a line.
_LIST_ITEM = re.compile(r"^[ \t]*(?:[-*+]|[0-9]+[.)])[ \t]")
# Every blockquote mark at the start of a line, nested or indented.
_BLOCKQUOTE = re.compile(r"^(?:[ \t]*>[ \t]?)+", re.MULTILINE)
_LEVEL2 = re.compile(r"^[ \t]{0,3}##(?!#)[ \t]+\S", re.MULTILINE)
_LEVEL3 = re.compile(r"^[ \t]{0,3}###(?!#)[ \t]+\S", re.MULTILINE)
_ITEM = re.compile(r"^[1-9][0-9]*$")
_REF = re.compile(r"^[RS][0-9]+$")
_ROADMAP_HEADING = re.compile(r"^[ \t]{0,3}###[ \t]+(?:Required|Suggested) Revisions\b")
_HEADING = re.compile(r"^[ \t]{0,3}#{1,6}[ \t]")
# Machine lines and internal ids of the package that belong only in the audit
# record (#1078 Rule 3 of the template).
# A field name counts wherever it stands, in Markdown emphasis or code too:
# no author letter has a reason to write it.
MACHINE_PATTERNS = (
    re.compile(r"(?<![A-Za-z0-9])(?:dimension_verdicts|fired_conditions"
               r"|editorial_decision|calibration_status)(?![A-Za-z0-9])"),
    # ASCII boundaries: a CJK letter beside an id is not a boundary for \b.
    # An underscore may be Markdown emphasis (_REV-3_), so it is a boundary.
    re.compile(r"(?<![A-Za-z0-9])NOT_CALIBRATED(?![A-Za-z0-9])"),
    re.compile(r"(?<![A-Za-z0-9])(?:must_fix|should_fix)(?![A-Za-z0-9])"),
    re.compile(r"(?<![A-Za-z0-9])REV-[0-9]+"),
    re.compile(r"(?<![A-Za-z0-9])SC-[0-9]+"),
    re.compile(r"(?<![A-Za-z0-9])(?:EIC|R[1-3]|DA)-W[0-9]+"),
    re.compile(r"(?<![A-Za-z0-9])CONSENSUS-[0-9]+"),
    re.compile(r"(?<![A-Za-z0-9])DA-CRITICAL(?![A-Za-z0-9])"),
    re.compile(r"(?<![A-Za-z0-9])SEVERITY-SOURCE(?![A-Za-z0-9])"),
    re.compile(r"(?<![A-Za-z0-9])Transport refs?(?![A-Za-z0-9])", re.IGNORECASE),
    re.compile(r"<!--"),
    re.compile(r"^\s*(?:```|~~~)", re.MULTILINE),
)


def split_letter(letter: str) -> tuple[str, str]:
    """The body and the appendix. The appendix starts at the last level-2
    heading (the template ends with it, in the user's language); a letter with
    fewer than two level-2 headings has no appendix."""
    starts = [m.start() for m in _LEVEL2.finditer(letter)]
    if len(starts) < 2:
        return letter, ""
    return letter[:starts[-1]], letter[starts[-1]:]


def _blocks(text: str) -> list[str]:
    """Paragraphs and list items, with blockquote marks removed, so a
    quotation can wrap onto the next line of its block but no further."""
    blocks = []
    for paragraph in _PARAGRAPH.split(_BLOCKQUOTE.sub("", text)):
        current = []
        for line in paragraph.splitlines():
            if _LIST_ITEM.match(line) and current:
                blocks.append("\n".join(current))
                current = []
            current.append(line)
        blocks.append("\n".join(current))
    return blocks


def quotations(text: str) -> list[str]:
    """Quoted spans, by the reviewer claim check's marks, in each paragraph
    or list item made one line, so a quotation can wrap onto the next line."""
    spans = []
    for block in _blocks(text):
        flat = " ".join(block.split())
        spans += [next(g for g in m.groups() if g is not None) for m in _QUOTED.finditer(flat)]
    return spans


def item_map(appendix: str) -> str:
    """The appendix's last level-3 subsection (the template's Item Map)."""
    starts = [m.start() for m in _LEVEL3.finditer(appendix)]
    return appendix[starts[-1]:] if starts else ""


def _cells(line: str) -> list[str]:
    """The cells of a table row, with at most one outer pipe at each end."""
    body = line.strip()
    body = body[1:] if body.startswith("|") else body
    body = body[:-1] if body.endswith("|") else body
    return [_trim(c) for c in body.split("|")]


def _trim(cell: str) -> str:
    """``cell`` without the whitespace (Unicode spaces included) and the
    `` ` ``, ``*``, and ``_`` marks at its ends, in any order."""
    while True:
        trimmed = cell.strip().strip("`*_")
        if trimmed == cell:
            return cell
        cell = trimmed


def table_rows(text: str) -> list[str] | None:
    """The data rows of the first two-column table in ``text``: a header row
    of two cells, then a delimiter row of two cells, then the rows up to a
    blank line. None when ``text`` has no such table."""
    lines = text.splitlines()
    for i in range(len(lines) - 1):
        if ("|" in lines[i] and len(_cells(lines[i])) == 2
                and _TABLE_RULE.match(lines[i + 1]) and len(_cells(lines[i + 1])) == 2):
            rows = []
            for line in lines[i + 2:]:
                if not line.strip():
                    break
                rows.append(line)
            return rows
    return None


def map_rows(rows: list[str]) -> tuple[list[tuple[str, str]], list[str]]:
    """(item, ref) for each row of the item map, and a problem for each row
    that is not two cells: an item number, then a ref."""
    pairs, problems = [], []
    for line in rows:
        cells = _cells(line)
        if len(cells) != 2 or not _ITEM.match(cells[0]) or not _REF.match(cells[1]):
            problems.append(f"[AUTHOR-LETTER-MAPPING] item map row needs one item number and one ref: {line.strip()[:60]!r}")
            continue
        pairs.append((cells[0], cells[1]))
    return pairs, problems


def roadmap_refs(package: str) -> list[str]:
    """The transport refs of the Required and Suggested Revisions tables."""
    refs, inside = [], False
    for line in package.splitlines():
        if _HEADING.match(line):
            inside = bool(_ROADMAP_HEADING.match(line))
            continue
        if inside and "|" in line:
            first = _cells(line)[0]
            if _REF.match(first):
                refs.append(first)
    return refs


def check(letter: str, package: str, manuscript: str | None) -> list[str]:
    _body, appendix = split_letter(letter)
    problems = []
    if not appendix or not _LEVEL3.search(appendix):
        problems.append("[AUTHOR-LETTER-APPENDIX] no appendix: the letter needs a last level-2 heading "
                        "after its body, with the item map as its last level-3 subsection")
    if manuscript is not None:
        for quote in quotations(letter):
            if not evidence_ok({"quote": quote, "evidence": "contradiction"}, "", manuscript):
                problems.append(f"[AUTHOR-LETTER-QUOTE] not in the manuscript: {quote[:40]!r}")
    # The whole letter, the appendix included (template Rule 3); bare
    # transport refs are not among the patterns, so the item map passes.
    # Blockquote marks removed too, so a fence inside a blockquote counts.
    unquoted = _BLOCKQUOTE.sub("", letter)
    for pattern in MACHINE_PATTERNS:
        if (hit := pattern.search(letter) or pattern.search(unquoted)):
            problems.append(f"[AUTHOR-LETTER-MACHINE-LINE] the letter holds {hit.group(0).strip()!r}")
    table = table_rows(item_map(appendix))
    if appendix and _LEVEL3.search(appendix) and table is None:
        problems.append("[AUTHOR-LETTER-APPENDIX] the item map has no two-column table (a header row and a delimiter row of two cells); "
                        "with no changes it is a table with no rows")
    rows, row_problems = map_rows(table or [])
    problems += row_problems
    # The item map holds one table: a second table or a stray row would go
    # unchecked, so every line with a pipe must belong to the table.
    if table is not None and sum("|" in line for line in item_map(appendix).splitlines()) > len(table) + 2:
        problems.append("[AUTHOR-LETTER-MAPPING] the item map has a table row outside its one table")
    mapped, items = [ref for _, ref in rows], [item for item, _ in rows]
    for item in sorted({i for i in items if items.count(i) > 1}, key=int):
        problems.append(f"[AUTHOR-LETTER-MAPPING] item map item {item} appears more than once")
    expected = roadmap_refs(package)
    for ref in sorted(set(expected) - set(mapped)):
        problems.append(f"[AUTHOR-LETTER-MAPPING] roadmap item {ref} is not in the item map")
    for ref in sorted(set(mapped) - set(expected)):
        problems.append(f"[AUTHOR-LETTER-MAPPING] item map ref {ref} is not a roadmap item")
    for ref in sorted({r for r in mapped if mapped.count(r) > 1}):
        problems.append(f"[AUTHOR-LETTER-MAPPING] item map ref {ref} appears more than once")
    return problems


def _read(path: Path, name: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"[AUTHOR-LETTER-INPUT] cannot read the {name}: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--letter", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--manuscript", type=Path)
    args = parser.parse_args(argv)
    letter = _read(args.letter, "author letter")
    package = _read(args.package, "decision package")
    manuscript = None if args.manuscript is None else _read(args.manuscript, "manuscript")
    problems = check(letter, package, manuscript)
    for problem in problems:
        print(problem)
    if manuscript is None:
        print("[AUTHOR-LETTER-QUOTE-CHECK-NOT-RUN] no manuscript file was given")
    if not problems:
        print("AUTHOR-LETTER: PASS")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
