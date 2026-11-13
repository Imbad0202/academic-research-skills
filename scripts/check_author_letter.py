#!/usr/bin/env python3
"""Check the author letter against the manuscript and the decision package (#1078).

The author letter is the review rewritten for the author from the finished
Editorial Decision Package (``academic-paper-reviewer/SKILL.md`` § Author
letter; ``templates/author_letter_template.md``). A rewrite can turn a
paraphrase into a false quotation, carry a machine line into the body, or drop
a revision item, so this script checks three things:

  quotes     every span in quotation marks (the reviewer claim check's quote
             grammar, read across line breaks) occurs in the manuscript,
             after the same normalization (``dispatch_panel_claim_audit._norm``)
             with whitespace removed, so a quotation wrapped onto a new line
             still matches. Skipped, with a notice, when no manuscript file is
             given.
  body       the body, before the appendix, holds no machine line or internal
             id. The appendix is the letter's last level-2 heading, whatever
             language it is in. Bare transport refs (``R1``, ``S2``) are not
             searched for, because a manuscript location such as "Table S1"
             has the same form.
  item map   each appendix table row that holds a transport ref has one item
             number and one ref; the item numbers are the numbered items of
             the body, each once; the refs are the must-fix and should-fix
             rows of the package's Revision Roadmap, each once.

Exit 0 pass / 1 problems found / 2 missing or unreadable input.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from audit_panel_claims import _QUOTED
    from dispatch_panel_claim_audit import _norm
except ImportError:  # pragma: no cover - dual-path import
    from scripts.audit_panel_claims import _QUOTED
    from scripts.dispatch_panel_claim_audit import _norm

_LEVEL2 = re.compile(r"^\s{0,3}##(?!#)\s+\S", re.MULTILINE)
_NUMBERED = re.compile(r"^\s{0,3}([0-9]+)[.)、．]\s", re.MULTILINE)
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
    re.compile(r"\bNOT_CALIBRATED\b"),
    re.compile(r"\b(?:must_fix|should_fix)\b"),
    re.compile(r"(?<![A-Za-z0-9])REV-[0-9]+"),
    re.compile(r"(?<![A-Za-z0-9])SC-[0-9]+"),
    re.compile(r"(?<![A-Za-z0-9])(?:EIC|R[1-3]|DA)-W[0-9]+"),
    re.compile(r"\[CONSENSUS-[0-9]\]"),
    re.compile(r"\bDA-CRITICAL\b"),
    re.compile(r"\[SEVERITY-SOURCE"),
    re.compile(r"Transport ref", re.IGNORECASE),
    re.compile(r"<!--"),
    re.compile(r"^\s*```", re.MULTILINE),
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
    """Quoted spans, read across line breaks as the reviewer claim check does."""
    flat = " ".join(text.split())
    return [next(g for g in m.groups() if g is not None) for m in _QUOTED.finditer(flat)]


def _squeeze(text: str) -> str:
    return "".join(_norm(text).split())


def _cells(line: str) -> list[str]:
    return [c.strip().strip("`*") for c in line.strip().strip("|").split("|")]


def map_rows(text: str) -> tuple[list[tuple[str, str]], list[str]]:
    """(item, ref) for each table row that holds a transport ref, and a
    problem for each such row that does not have exactly one item number and
    one ref."""
    rows, problems = [], []
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = _cells(line)
        refs = [c for c in cells if _REF.match(c)]
        if not refs:
            continue
        items = [c for c in cells if c.isdigit()]
        if len(refs) != 1 or len(items) != 1:
            problems.append(f"[AUTHOR-LETTER-MAPPING] item map row needs one item number and one ref: {line.strip()[:60]!r}")
            continue
        rows.append((items[0], refs[0]))
    return rows, problems


def roadmap_refs(package: str) -> list[str]:
    """The transport refs of the Required and Suggested Revisions tables."""
    refs, inside = [], False
    for line in package.splitlines():
        if _HEADING.match(line):
            inside = bool(_ROADMAP_HEADING.match(line))
            continue
        if inside and line.lstrip().startswith("|"):
            first = line.strip().strip("|").split("|")[0].strip().strip("`*")
            if _REF.match(first):
                refs.append(first)
    return refs


def check(letter: str, package: str, manuscript: str | None) -> list[str]:
    body, appendix = split_letter(letter)
    problems = []
    if not appendix:
        problems.append("[AUTHOR-LETTER-APPENDIX] no appendix: the letter needs a last level-2 heading after its body")
    if manuscript is not None:
        haystack = _squeeze(manuscript)
        for quote in quotations(letter):
            if _squeeze(quote) and _squeeze(quote) not in haystack:
                problems.append(f"[AUTHOR-LETTER-QUOTE] not in the manuscript: {quote[:40]!r}")
    for pattern in MACHINE_PATTERNS:
        if pattern.search(body):
            problems.append(f"[AUTHOR-LETTER-MACHINE-LINE] the body matches {pattern.pattern!r}")
    rows, row_problems = map_rows(appendix)
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
