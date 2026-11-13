#!/usr/bin/env python3
"""Check the author letter against the manuscript and the decision package (#1078).

The author letter is the review rewritten for the author from the finished
Editorial Decision Package (``academic-paper-reviewer/SKILL.md`` § Author
letter; ``templates/author_letter_template.md``). A rewrite can turn a
paraphrase into a false quotation, carry a machine line into the body, or drop
a revision item, so this script checks three things:

  quotes     every span in quotation marks (the reviewer claim check's quote
             grammar) occurs in the manuscript, after the same normalization
             (``dispatch_panel_claim_audit._norm``). Skipped, with a notice,
             when no manuscript file is given.
  body       the body, before the ``## Appendix`` / ``## 附錄`` heading, holds
             no machine line or internal id. Bare transport refs (``R1``,
             ``S2``) are not searched for, because a manuscript location such
             as "Table S1" has the same form.
  item map   the transport refs in the appendix tables are the must-fix and
             should-fix rows of the package's Revision Roadmap, each once.

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

_APPENDIX = re.compile(r"^\s{0,3}##\s+(?:Appendix|附錄)\b", re.MULTILINE)
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
    """The body and the appendix; the appendix is empty without its heading."""
    match = _APPENDIX.search(letter)
    if match is None:
        return letter, ""
    return letter[:match.start()], letter[match.start():]


def quotations(text: str) -> list[str]:
    return [next(g for g in m.groups() if g is not None) for m in _QUOTED.finditer(text)]


def table_refs(text: str) -> list[str]:
    """Each table cell that is exactly a transport ref, in order."""
    refs = []
    for line in text.splitlines():
        if line.lstrip().startswith("|"):
            refs += [c.strip().strip("`*") for c in line.strip().strip("|").split("|")
                     if _REF.match(c.strip().strip("`*"))]
    return refs


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
        problems.append("[AUTHOR-LETTER-APPENDIX] no '## Appendix' or '## 附錄' heading")
    if manuscript is not None:
        haystack = _norm(manuscript)
        for quote in quotations(letter):
            if _norm(quote) and _norm(quote) not in haystack:
                problems.append(f"[AUTHOR-LETTER-QUOTE] not in the manuscript: {quote[:40]!r}")
    for pattern in MACHINE_PATTERNS:
        if pattern.search(body):
            problems.append(f"[AUTHOR-LETTER-MACHINE-LINE] the body matches {pattern.pattern!r}")
    expected, mapped = roadmap_refs(package), table_refs(appendix)
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
