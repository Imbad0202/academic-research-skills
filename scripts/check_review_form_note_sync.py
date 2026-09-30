#!/usr/bin/env python3
"""Review-form note sync lint (#921).

`shared/references/review_form_note.md` holds the canonical review-form note:
the rules for when ARS reminds the author that a literature review can take
several forms, and the fixed note text in English and Traditional Chinese.
This lint keeps each surface's verbatim copy byte-identical to it and checks
that the note offers its options without a default or a ranking.

Checks:
  RF-1  The canonical file holds exactly one begin marker and one end marker,
        each alone on its line, begin before end, around a non-empty block.
  RF-2  Every surface holds exactly one such marker pair, and its block is
        byte-identical to the canonical block, line endings included.
  RF-3  The canonical block holds an English and a Traditional Chinese note
        text. Every non-blank line of each opens with `>`. Each has exactly
        five list items, opening with the five review forms' labels in the
        same order, and its neutrality sentence verbatim;
        no other note line carries a word that ranks, recommends, or
        preselects, or a selection mark.

Usage:
    python scripts/check_review_form_note_sync.py [--root PATH]

Exit codes: 0 all checks pass; 1 a check failed; 2 a required file is missing.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _skill_lint import read_or_exit2  # noqa: E402
from check_routing_core_sync import first_difference  # noqa: E402

CANONICAL = Path("shared/references/review_form_note.md")
SURFACES = (
    Path("deep-research/SKILL.md"),
    Path("academic-paper/SKILL.md"),
)
BEGIN = "<!-- review-form-note:begin -->"
END = "<!-- review-form-note:end -->"

NOTE_HEADINGS = ("**Note text (English):**", "**Note text (Traditional Chinese):**")
# The exact bold label that opens each option line, per note language, in order.
OPTIONS = (
    ("**Systematic review**:", "**系統性回顧（systematic review）**："),
    ("**Scoping review**:", "**範疇回顧（scoping review）**："),
    ("**Narrative or integrative review**:", "**敘事或整合性回顧（narrative / integrative review）**："),
    ("**Rapid review**:", "**快速回顧（rapid review）**："),
    ("**No formal review**:", "**不做正式回顧**："),
)
# The one line per note that says there is no default, recommendation, or
# ranking. It must be present verbatim, and it is the only note line allowed to
# use those words.
NEUTRALITY = (
    "> ARS does not choose this for you. There is no default and no recommendation, "
    "and the order below is not a ranking.",
    "> 這件事由你決定，ARS 不替你選。下列選項沒有預設、沒有推薦，排列順序也不代表高下。",
)
LIST_ITEM = re.compile(r"^>\s*(?:[-*+]|\d+[.)])\s")
RANKING_WORDS = re.compile(
    r"\b(?:recommend\w*|default\w*|best|prefer\w*|suggest\w*|ideal\w*|should|most|least|"
    r"better|optimal\w*|advis\w*)\b|推薦|建議|預設|最|首選|應該|較適合|更好|優先",
    re.IGNORECASE,
)
SELECTION_MARK = re.compile(r"\[[ xX✓✔]\]|[☑☒✅✔✓★⭐←]|\(\*\)")


def extract_block(text: str, label: str) -> tuple[str | None, list[str]]:
    """Return the text between the one marker pair, or None with the errors.
    A marker line may end in CR; the block keeps its CRs for the comparison."""
    lines = text.split("\n")
    begins = [i for i, line in enumerate(lines) if line.rstrip("\r") == BEGIN]
    ends = [i for i, line in enumerate(lines) if line.rstrip("\r") == END]
    errors: list[str] = []
    for marker, whole in ((BEGIN, begins), (END, ends)):
        total = text.count(marker)
        if total != 1 or len(whole) != 1:
            errors.append(f"{label}: expected one {marker} alone on its line, "
                          f"found {total} occurrence(s), {len(whole)} on their own line")
    if errors:
        return None, errors
    if begins[0] > ends[0]:
        return None, [f"{label}: {END} comes before {BEGIN}"]
    block = "\n".join(lines[begins[0] + 1:ends[0]])
    if not block.strip():
        return None, [f"{label}: the review-form note block is empty"]
    return block, []


def note_lines(block: str, heading: str) -> list[str] | None:
    """Return the non-blank lines of the note text under `heading`, up to the
    next note-text heading, or None when the heading is missing. Line
    terminators are dropped here; RF-2 compares the raw bytes."""
    lines = [line.rstrip("\r") for line in block.split("\n")]
    if heading not in lines:
        return None
    note = []
    for line in lines[lines.index(heading) + 1:]:
        if line.startswith("**Note text"):
            break
        if line.strip():
            note.append(line)
    return note


def check_neutrality(block: str) -> list[str]:
    """RF-3: each note lists the five forms under their exact labels, in order,
    keeps its neutrality sentence, and has no ranking word or selection mark."""
    errors: list[str] = []
    for index, heading in enumerate(NOTE_HEADINGS):
        where = f"RF-3 {CANONICAL}: {heading}"
        lines = note_lines(block, heading)
        if lines is None:
            errors.append(f"RF-3 {CANONICAL}: note text heading {heading} is missing")
            continue
        for line in lines:
            if not line.startswith(">"):
                errors.append(f"{where} has a line outside the quoted note text: {line[:60]!r}")
        if NEUTRALITY[index] not in lines:
            errors.append(f"{where} lacks its neutrality sentence verbatim")
        items = [line for line in lines if LIST_ITEM.match(line)]
        labels = [names[index] for names in OPTIONS]
        if len(items) != len(labels):
            errors.append(f"{where} lists {len(items)} options, expected {len(labels)}")
        else:
            for line, label in zip(items, labels):
                if not line.startswith(f"> - {label}"):
                    errors.append(f"{where} option out of order or relabelled: "
                                  f"expected it to open with {label!r}, found {line[:60]!r}")
        for line in lines:
            if line == NEUTRALITY[index]:
                continue
            for pattern, kind in ((RANKING_WORDS, "ranking word"), (SELECTION_MARK, "selection mark")):
                match = pattern.search(line)
                if match:
                    errors.append(f"{where} carries the {kind} {match.group(0)!r} in {line[:60]!r}")
    return errors


def check(root: Path) -> list[str]:
    """Run RF-1 to RF-3 under `root`; a missing file exits 2."""
    canonical, errors = extract_block(read_or_exit2(root, str(CANONICAL), exact=True),
                                      f"RF-1 {CANONICAL}")
    if canonical is not None:
        errors += check_neutrality(canonical)
    for rel in SURFACES:
        block, copy_errors = extract_block(read_or_exit2(root, str(rel), exact=True), f"RF-2 {rel}")
        errors += copy_errors
        if block is not None and canonical is not None and block != canonical:
            errors.append(f"RF-2 {rel}: review-form note block differs from {CANONICAL} "
                          f"({first_difference(block, canonical)})")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    errors = check(args.root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"check_review_form_note_sync: OK ({len(SURFACES)} surfaces match {CANONICAL})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
