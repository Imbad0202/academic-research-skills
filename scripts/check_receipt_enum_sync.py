#!/usr/bin/env python3
"""Defrift lint for the #610 arithmetic-receipt closed enums.

The receipt grammar spells its four closed enums in three places: the
`methodology-receipt` canonical prompt fragment (what the reviewer is told),
the conformance checker's frozensets (what is enforced), and the #610 spec §4
(what was decided). This lint parses the backtick enum lists out of the
fragment and the spec and asserts set equality against the checker constants,
so a value added or renamed on one surface fails CI until every surface moves
in the same commit. The spec does not define a `tail_convention` enum, so that
comparison is fragment-vs-checker only.

Usage: python scripts/check_receipt_enum_sync.py [--root REPO_ROOT]
Exit 0 in sync, 1 drift, 2 missing file or unparseable surface.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_phase_conformance as phase  # noqa: E402
import check_reviewer_sprint_prompt_sync as sync  # noqa: E402

CANONICAL_REL = sync.CANONICAL_REL
SPEC_REL = "docs/design/2026-08-02-610-statistical-recompute-baseline-spec.md"
_BACKTICK_NAME_RE = re.compile(r"`([a-z0-9_]+)`")
_ANGLE_ENUM_RES = {
    "procedure_id": re.compile(r"`procedure_id: <([^>]+)>`"),
    "status": re.compile(r"`status: <([^>]+)>`"),
    "tail_convention": re.compile(r"`tail_convention: <([^>]+)>`"),
}
_FRAGMENT_REASONS_RE = re.compile(
    r"closed v1 enum: (?P<names>.*?)\. Every other status"
)
CHECKER_ENUMS = {
    "procedure_id": frozenset(phase._RECEIPT_PROCEDURES),
    "status": frozenset(phase._RECEIPT_STATUSES),
    "not_computable_reason": frozenset(phase._NOT_COMPUTABLE_REASONS),
    "tail_convention": frozenset(phase._TAIL_CONVENTIONS),
}


def _read(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: required file unreadable: {rel}: {exc}",
              file=sys.stderr)
        raise SystemExit(2)


def _fragment_enums(fragment: str, errors: list[str]) -> dict[str, set[str]]:
    enums: dict[str, set[str]] = {}
    for name, pattern in _ANGLE_ENUM_RES.items():
        matches = pattern.findall(fragment)
        if len(matches) != 1:
            errors.append(
                f"fragment: expected exactly one `{name}: <...>` enum "
                f"spelling, found {len(matches)}"
            )
            continue
        enums[name] = {value.strip() for value in matches[0].split("|")}
    reasons = _FRAGMENT_REASONS_RE.search(fragment)
    if reasons is None:
        errors.append(
            "fragment: the closed v1 not_computable_reason sentence "
            "('closed v1 enum: ... . Every other status') was not found"
        )
    else:
        enums["not_computable_reason"] = set(
            _BACKTICK_NAME_RE.findall(reasons.group("names"))
        )
    return enums


def _spec_section4_lines(
    spec_lines: list[str], errors: list[str]
) -> list[str]:
    """The lines of spec §4 only, so a worked example or historical block
    elsewhere in the document can never satisfy — or mask drift in — the
    normative enum definitions (#610 round-2)."""
    starts = [
        index for index, line in enumerate(spec_lines)
        if line.startswith("## 4. ")
    ]
    if len(starts) != 1:
        errors.append(
            f"spec: expected exactly one '## 4. ' heading, found "
            f"{len(starts)}"
        )
        return []
    end = next(
        (
            index for index in range(starts[0] + 1, len(spec_lines))
            if spec_lines[index].startswith("## ")
        ),
        len(spec_lines),
    )
    return spec_lines[starts[0]:end]


def _spec_table_cell_enum(
    spec_lines: list[str], field: str, errors: list[str]
) -> set[str] | None:
    rows = [
        line for line in spec_lines
        if line.startswith(f"| `{field}` |")
    ]
    if len(rows) != 1:
        errors.append(
            f"spec §4: expected exactly one `| `{field}` |` table row, "
            f"found {len(rows)}"
        )
        return None
    cells = rows[0].split("|")
    return set(_BACKTICK_NAME_RE.findall(cells[2]))


def _spec_reason_enum(spec_lines: list[str], errors: list[str]) -> set[str]:
    starts = [
        index for index, line in enumerate(spec_lines)
        if "closed v1 enum" in line
    ]
    if len(starts) != 1:
        errors.append(
            "spec §4: expected exactly one 'closed v1 enum' sentence in "
            f"§4, found {len(starts)}"
        )
        return set()
    names: set[str] = set()
    for line in spec_lines[starts[0] + 1:]:
        if match := re.fullmatch(r"- `([a-z0-9_]+)`", line.strip()):
            names.add(match.group(1))
        elif line.strip() and names:
            break
    return names


def check(root: Path) -> list[str]:
    errors: list[str] = []
    canonical_text = _read(root, CANONICAL_REL)
    fragments = {
        match.group("name"): match.group("body")
        for match in sync.MARKER_RE.finditer(canonical_text)
    }
    fragment = fragments.get("methodology-receipt")
    if fragment is None:
        print("ERROR: methodology-receipt fragment missing from "
              f"{CANONICAL_REL}", file=sys.stderr)
        raise SystemExit(2)
    spec_lines = _spec_section4_lines(
        _read(root, SPEC_REL).splitlines(), errors
    )

    fragment_enums = _fragment_enums(fragment, errors)
    spec_enums = {
        "procedure_id": _spec_table_cell_enum(
            spec_lines, "procedure_id", errors
        ),
        "status": _spec_table_cell_enum(spec_lines, "status", errors),
        "not_computable_reason": _spec_reason_enum(spec_lines, errors),
    }

    for name, checker_values in CHECKER_ENUMS.items():
        for surface, values in (
            ("fragment", fragment_enums.get(name)),
            ("spec §4", spec_enums.get(name)),
        ):
            if values is None:
                continue  # tail_convention has no spec enum; parse errors
                # for the other absences are already recorded above.
            if values != checker_values:
                missing = sorted(checker_values - values)
                extra = sorted(values - checker_values)
                errors.append(
                    f"{name}: {surface} enum drifted from the checker "
                    f"frozenset (missing={missing}, extra={extra})"
                )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args(argv)
    errors = check(args.root)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print("RECEIPT-ENUM-SYNC: PASS (4 enums, 3 surfaces)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
