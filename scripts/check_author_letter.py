#!/usr/bin/env python3
"""Check the author letter against the manuscript and the decision package (#1078).

The author letter is the review rewritten for the author from the finished
Editorial Decision Package (``academic-paper-reviewer/SKILL.md`` § Author
letter; ``templates/author_letter_template.md``). A rewrite can turn a
paraphrase into a false quotation, carry a machine line into the body, or drop
a revision item, so this script checks three things:

  quotes     every span in “…”, "…", 「…」, or 『…』 occurs in the manuscript. A
             quotation can wrap onto the next line inside a paragraph. ‘…’ is
             allowed only inside another quotation, because its closing mark
             is also the apostrophe (“the patients’ outcomes”); a ‘ outside a
             quotation is a problem. Both sides are compared after NFC, with
             whitespace runs made one space, double quotation marks
             (" “ ” 「 」 『 』) removed, the space between two CJK characters
             removed, and ‘ ’ read as '. Case, other marks, and digits must
             match. A quotation that starts or ends with a letter or digit of
             a script that puts spaces between words must start or end at a
             word boundary of the manuscript, so "significant" does not match
             inside "insignificant" nor "café" inside "caféine". Skipped,
             with a notice, when no manuscript file is given.
  ids        the whole letter, the appendix included, holds no machine line or
             internal id, and only the body has numbered items. The appendix is the letter's last level-2 heading, whatever
             language it is in. Bare transport refs (``R1``, ``S2``) are not
             searched for, because a manuscript location such as "Table S1"
             has the same form.
  item map   the item map is the appendix's last level-3 subsection and holds a
             table: a header row and a delimiter row, then no rows when there
             are no changes. Outer pipes are optional. Each row of the table
             has one item number and one ref; the item numbers are the
             numbered items of the body, each once; the refs are the rows of
             the Required and Suggested Revisions tables of the package, each
             once.

Exit 0 pass / 1 problems found / 2 missing or unreadable input.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

# The reviewer claim check's quotation marks (audit_panel_claims._QUOTED),
# read inside one paragraph. Single quotation marks are left out: ’ is also
# the apostrophe, so a ‘…’ span has no reliable end (template Rule 4).
_QUOTED = re.compile(r'"([^"]+)"|“([^”]+)”|「([^」]+)」|『([^』]+)』')
_QUOTE_MARKS = str.maketrans("", "", "\"“”「」『』")
# A delimiter row of two or more columns; outer pipes are optional.
_TABLE_RULE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")
_CJK_CHAR = "\u3000-\u303f\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff\uff00-\uffef"
_CJK_GAP = re.compile(f"(?<=[{_CJK_CHAR}]) (?=[{_CJK_CHAR}])")
_PARAGRAPH = re.compile(r"\n\s*\n")
_LEVEL3 = re.compile(r"^\s{0,3}###(?!#)\s+\S", re.MULTILINE)

_LEVEL2 = re.compile(r"^\s{0,3}##(?!#)\s+\S", re.MULTILINE)
# "1. " or "1) ", or a full-width "1、" / "1．" with or without a space.
_NUMBERED = re.compile(r"^\s{0,3}([0-9]+)(?:[.)]\s|[、．](?![0-9]))", re.MULTILINE)
_ITEM = re.compile(r"^[0-9]+$")
_REF = re.compile(r"^[RS][0-9]+$")
_ROADMAP_HEADING = re.compile(r"^\s{0,3}###\s+(?:Required|Suggested) Revisions\b")
_HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
# Machine lines and internal ids of the package that belong only in the audit
# record (#1078 Rule 3 of the template).
MACHINE_PATTERNS = (
    re.compile(r"dimension_verdicts\s*:"),
    re.compile(r"fired_conditions\s*:"),
    re.compile(r"editorial_decision\s*="),
    re.compile(r"calibration_status\s*:"),
    # ASCII boundaries: a CJK letter beside an id is not a boundary for \b.
    # An underscore may be Markdown emphasis (_REV-3_), so it is a boundary.
    re.compile(r"(?<![A-Za-z0-9])NOT_CALIBRATED(?![A-Za-z0-9])"),
    re.compile(r"(?<![A-Za-z0-9])(?:must_fix|should_fix)(?![A-Za-z0-9])"),
    re.compile(r"(?<![A-Za-z0-9])REV-[0-9]+"),
    re.compile(r"(?<![A-Za-z0-9])SC-[0-9]+"),
    re.compile(r"(?<![A-Za-z0-9])(?:EIC|R[1-3]|DA)-W[0-9]+"),
    re.compile(r"\[CONSENSUS-[0-9]+\]"),
    re.compile(r"(?<![A-Za-z0-9])DA-CRITICAL(?![A-Za-z0-9])"),
    re.compile(r"\[SEVERITY-SOURCE"),
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


def quotations(text: str) -> list[str]:
    """Quoted spans; a quotation can wrap onto the next line of its paragraph."""
    spans = []
    for paragraph in _PARAGRAPH.split(text):
        flat = " ".join(paragraph.split())
        spans += [next(g for g in m.groups() if g is not None) for m in _QUOTED.finditer(flat)]
    return spans


def stray_single_quotes(text: str) -> int:
    """How many ‘ marks stand outside every other quotation."""
    count = 0
    for paragraph in _PARAGRAPH.split(text):
        count += _QUOTED.sub("", " ".join(paragraph.split())).count("‘")
    return count


def _squeeze(text: str) -> str:
    """NFC, one space for each whitespace run, double quotation marks
    removed, no space between two CJK characters, and ‘ ’ read as '. Case
    stays: "5 mM" is not "5 mm"."""
    text = unicodedata.normalize("NFC", text).replace("‘", "'").replace("’", "'")
    flat = " ".join(text.translate(_QUOTE_MARKS).split())
    return _CJK_GAP.sub("", flat)


def _wordish(ch: str) -> bool:
    """A letter, digit, or combining mark of a script that puts spaces
    between words; a CJK character is not, so a CJK quotation needs no
    word boundary."""
    if not ch or re.match(f"[{_CJK_CHAR}]", ch):
        return False
    return ch.isalnum() or unicodedata.category(ch).startswith("M")


def _found(quote: str, haystack: str) -> bool:
    """``quote`` occurs in ``haystack``, and where it starts or ends with a
    letter or digit of a spaced script, the occurrence starts or ends at a
    word boundary."""
    if not quote:
        return True
    start = 0
    while (at := haystack.find(quote, start)) != -1:
        before = haystack[at - 1] if at else ""
        after = haystack[at + len(quote)] if at + len(quote) < len(haystack) else ""
        head_ok = not (_wordish(quote[0]) and _wordish(before))
        tail_ok = not (_wordish(quote[-1]) and _wordish(after))
        if head_ok and tail_ok:
            return True
        start = at + 1
    return False


def item_map(appendix: str) -> str:
    """The appendix's last level-3 subsection (the template's Item Map)."""
    starts = [m.start() for m in _LEVEL3.finditer(appendix)]
    return appendix[starts[-1]:] if starts else ""


def _cells(line: str) -> list[str]:
    return [c.strip().strip("`*") for c in line.strip().strip("|").split("|")]


def table_rows(text: str) -> list[str] | None:
    """The data rows of the first table in ``text``: a line with a pipe,
    then a delimiter row, then the rows up to a blank line. None when
    ``text`` has no such table."""
    lines = text.splitlines()
    for i in range(len(lines) - 1):
        if "|" in lines[i] and _TABLE_RULE.match(lines[i + 1]):
            rows = []
            for line in lines[i + 2:]:
                if not line.strip():
                    break
                rows.append(line)
            return rows
    return None


def map_rows(rows: list[str]) -> tuple[list[tuple[str, str]], list[str]]:
    """(item, ref) for each row of the item map, and a problem for each row
    that does not have exactly one item number and one ref."""
    pairs, problems = [], []
    for line in rows:
        cells = _cells(line)
        refs = [c for c in cells if _REF.match(c)]
        items = [c for c in cells if _ITEM.match(c)]
        if len(refs) != 1 or len(items) != 1:
            problems.append(f"[AUTHOR-LETTER-MAPPING] item map row needs one item number and one ref: {line.strip()[:60]!r}")
            continue
        pairs.append((items[0], refs[0]))
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
    body, appendix = split_letter(letter)
    problems = []
    if not appendix or not _LEVEL3.search(appendix):
        problems.append("[AUTHOR-LETTER-APPENDIX] no appendix: the letter needs a last level-2 heading "
                        "after its body, with the item map as its last level-3 subsection")
    if manuscript is not None:
        haystack = _squeeze(manuscript)
        for quote in quotations(letter):
            if not _found(_squeeze(quote), haystack):
                problems.append(f"[AUTHOR-LETTER-QUOTE] not in the manuscript: {quote[:40]!r}")
    if stray_single_quotes(letter):
        problems.append("[AUTHOR-LETTER-QUOTE] a ‘…’ quotation outside another quotation: use “…” or 「…」")
    # The whole letter, the appendix included (template Rule 3); bare
    # transport refs are not among the patterns, so the item map passes.
    for pattern in MACHINE_PATTERNS:
        if pattern.search(letter):
            problems.append(f"[AUTHOR-LETTER-MACHINE-LINE] the letter matches {pattern.pattern!r}")
    if _NUMBERED.search(appendix):
        problems.append("[AUTHOR-LETTER-MAPPING] the appendix has a numbered item; only the changes are numbered")
    table = table_rows(item_map(appendix))
    if appendix and _LEVEL3.search(appendix) and table is None:
        problems.append("[AUTHOR-LETTER-APPENDIX] the item map has no table (a header row and a delimiter row); "
                        "with no changes it is a table with no rows")
    rows, row_problems = map_rows(table or [])
    problems += row_problems
    mapped, items = [ref for _, ref in rows], [item for item, _ in rows]
    numbered = _NUMBERED.findall(body)
    for item in sorted(set(numbered) - set(items), key=int):
        problems.append(f"[AUTHOR-LETTER-MAPPING] body item {item} is not in the item map")
    for item in sorted(set(items) - set(numbered), key=int):
        problems.append(f"[AUTHOR-LETTER-MAPPING] item map item {item} is not a numbered item of the body")
    for item in sorted({i for i in items if items.count(i) > 1}, key=int):
        problems.append(f"[AUTHOR-LETTER-MAPPING] item map item {item} appears more than once")
    for item in sorted({i for i in numbered if numbered.count(i) > 1}, key=int):
        problems.append(f"[AUTHOR-LETTER-MAPPING] body item {item} is numbered more than once")
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
