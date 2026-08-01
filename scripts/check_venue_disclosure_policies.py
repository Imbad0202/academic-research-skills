#!/usr/bin/env python3
"""Structural guard for the 15-entry venue disclosure policy database."""

from pathlib import Path
import re
import sys


DEFAULT = Path("academic-paper/references/venue_disclosure_policies.md")
REQUIRED = (
    "Source URL",
    "Access date",
    "Policy summary",
    "Required phrasing elements",
    "Preferred disclosure location",
    "Prohibited uses",
    "Authorship rule",
)
FIELD_ROW = re.compile(
    r"^\|[ \t]*([^|\n]*?)[ \t]*\|[ \t]*((?:\\\||[^|\n])*)\|[ \t]*$"
)


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    text = path.read_text(encoding="utf-8")
    headings = list(re.finditer(r"^## Venue: (.+)$", text, re.MULTILINE))
    labels = [match.group(1).split(" (", 1)[0].strip() for match in headings]
    errors: list[str] = []
    if len(labels) != 15:
        errors.append(f"expected 15 venue headings, found {len(labels)}")
    if len({label.casefold() for label in labels}) != len(labels):
        errors.append("venue headings are not unique (case-insensitive)")
    if labels != sorted(labels, key=str.casefold):
        errors.append("venue headings are not globally case-insensitive alphabetical")
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        entry = text[match.end():end]
        for field in REQUIRED:
            values = []
            for line in entry.splitlines():
                key = re.match(r"^\|[ \t]*([^|\n]*?)[ \t]*\|", line)
                if key and key.group(1).strip() == field:
                    row = FIELD_ROW.fullmatch(line)
                    values.append(row.group(2) if row else None)
            if len(values) != 1:
                errors.append(
                    f"{match.group(1)}: {field!r} occurs {len(values)} times"
                )
            elif values[0] is None:
                errors.append(f"{match.group(1)}: {field!r} is not a two-column row")
            elif not values[0].strip():
                errors.append(f"{match.group(1)}: {field!r} has an empty value")
    if errors:
        print("venue disclosure policy structure: FAIL", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print("venue disclosure policy structure: OK (15 ordered entries, seven fields each)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
