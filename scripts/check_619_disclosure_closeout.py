#!/usr/bin/env python3
"""Fail-closed focused guard for issue #619 disclosure closeout surfaces."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PROTOCOL_REL = "academic-paper/references/disclosure_mode_protocol.md"
POLICIES_REL = "academic-paper/references/venue_disclosure_policies.md"
AUDIT_REL = "audits/external-contribution-audit-prompt.md"

MATRIX_BEGIN = "<!-- 619-frontiers-action-matrix:BEGIN -->"
MATRIX_END = "<!-- 619-frontiers-action-matrix:END -->"
EXPECTED_MATRIX = {
    "Created written content": ("REQUIRED", "REQUIRED", "—"),
    "Edited written content": ("—", "REQUIRED", "—"),
    "Produced non-data visual content": ("REQUIRED", "REQUIRED", "—"),
    "Edited non-data visual content": ("—", "REQUIRED", "—"),
    "Produced figure representing manuscript data": (
        "REQUIRED",
        "REQUIRED",
        "REQUIRED",
    ),
    "Edited figure representing manuscript data": ("—", "REQUIRED", "REQUIRED"),
}
SCENARIO_LABELS = {
    "Created written content": "created text",
    "Edited written content": "edited text",
    "Produced non-data visual content": "non-data visual",
    "Edited non-data visual content": "edited non-data visual",
    "Produced figure representing manuscript data": "data-representing figure",
    "Edited figure representing manuscript data": "edited data-representing figure",
}


class MissingRequiredFile(RuntimeError):
    pass


def _read(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise MissingRequiredFile(f"required file missing: {rel}") from exc


def _heading_section(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    try:
        start = lines.index(heading)
    except ValueError:
        return None
    level = len(heading) - len(heading.lstrip("#"))
    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if not line.startswith("#"):
            continue
        other_level = len(line) - len(line.lstrip("#"))
        if other_level <= level:
            end = index
            break
    return "\n".join(lines[start:end])


def _venue_section(text: str, venue: str) -> str | None:
    prefix = f"## Venue: {venue}"
    start = next(
        (match.start() for match in re.finditer(r"^## Venue: .+$", text, re.MULTILINE)
         if match.group(0).startswith(prefix)),
        None,
    )
    if start is None:
        return None
    next_heading = text.find("\n## Venue: ", start + 1)
    return text[start:] if next_heading < 0 else text[start:next_heading]


def _field(section: str, name: str) -> str | None:
    prefix = f"| {name} |"
    rows = [line for line in section.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        return None
    return rows[0][len(prefix):].removesuffix("|").strip()


def _frontiers_rows(protocol: str) -> tuple[str | None, str | None]:
    phase2a = _heading_section(
        protocol, "### Phase 2a: Decide whether the venue requires a disclosure (#596 venue path)"
    )
    phase2b = _heading_section(
        protocol, "### Phase 2b: Build the venue-required fact ledger (#596 venue path)"
    )
    def row(section: str | None) -> str | None:
        if section is None:
            return None
        rows = [line for line in section.splitlines() if line.startswith("| Frontiers |")]
        return rows[0] if len(rows) == 1 else None
    return row(phase2a), row(phase2b)


def _parse_matrix(protocol: str, errors: list[str]) -> dict[str, tuple[str, ...]]:
    if protocol.count(MATRIX_BEGIN) != 1 or protocol.count(MATRIX_END) != 1:
        errors.append("Frontiers Phase 5 action matrix markers must occur exactly once")
        return {}
    body = protocol.split(MATRIX_BEGIN, 1)[1].split(MATRIX_END, 1)[0]
    rows: dict[str, tuple[str, ...]] = {}
    for line in body.splitlines():
        if not line.startswith("|") or line.startswith("|---") or "Use record" in line:
            continue
        cells = tuple(cell.strip() for cell in line.strip().strip("|").split("|"))
        if len(cells) != 4:
            errors.append(f"Frontiers action matrix malformed row: {line}")
            continue
        if cells[0] in rows:
            errors.append(f"Frontiers action matrix duplicate scenario: {cells[0]}")
        rows[cells[0]] = cells[1:]
    return rows


def check(root: Path) -> list[str]:
    protocol = _read(root, PROTOCOL_REL)
    policies = _read(root, POLICIES_REL)
    audit = _read(root, AUDIT_REL)
    errors: list[str] = []

    phase2a, phase2b = _frontiers_rows(protocol)
    if phase2a is None or "Phase 5" not in phase2a or "does not halt disclosure rendering" not in phase2a:
        errors.append("Frontiers Phase 2a must route nonblocking quality actions to Phase 5")
    if phase2b is None:
        errors.append("Frontiers Phase 2b ledger row missing or duplicated")
    else:
        forbidden = ("plagiarism-free confirmation before render", "originality/plagiarism-free confirmation", "accurately reflects the data")
        if any(token in phase2b for token in forbidden):
            errors.append("Frontiers Phase 2b regrew a quality-action render gate")
        if "Phase-5 pre-submission actions, not fields required before render" not in phase2b:
            errors.append("Frontiers Phase 2b must identify quality checks as Phase-5 actions")

    matrix = _parse_matrix(protocol, errors)
    if set(matrix) != set(EXPECTED_MATRIX):
        errors.append("Frontiers action matrix scenario inventory drift")
    for scenario, expected in EXPECTED_MATRIX.items():
        if matrix.get(scenario) != expected:
            errors.append(
                "Frontiers action matrix mapping drift for "
                f"{SCENARIO_LABELS[scenario]}"
            )
    normalized_protocol = " ".join(protocol.split())
    for phrase in (
        "UNKNOWN or false action state is OUTSTANDING",
        "it never becomes a disclosure `UNKNOWN` halt",
        "do not halt or withhold the otherwise complete disclosure",
    ):
        if phrase not in normalized_protocol:
            errors.append(f"Frontiers OUTSTANDING semantics missing: {phrase}")

    frontiers = _venue_section(policies, "Frontiers")
    if frontiers is None:
        errors.append("Frontiers evidence row missing")
    else:
        prohibited = _field(frontiers, "Prohibited uses")
        expected_prohibited = (
            "Listing generative AI as author or co-author. Editors/reviewers "
            "uploading manuscript content to external generative AI tools."
        )
        if prohibited != expected_prohibited:
            errors.append("Frontiers Prohibited uses must contain only the two hard prohibitions")
        notes = _field(frontiers, "Notes") or ""
        for phrase in ("Phase-5 pre-submission checklist", "remains outstanding", "not a disclosure `UNKNOWN` halt"):
            if phrase not in notes:
                errors.append(f"Frontiers evidence action semantics missing: {phrase}")

    jama = _venue_section(policies, "JAMA")
    if jama is None:
        errors.append("JAMA evidence row missing")
    else:
        access = _field(jama, "Access date") or ""
        notes = _field(jama, "Notes") or ""
        if "cited exact official-URL snapshot is from 2026-07-01" not in access:
            errors.append("JAMA Access date must identify the cited snapshot date")
        gap = (
            "A Piece of My Mind and Poetry drafting clauses were verified on the live "
            "official page on 2026-08-01 and are absent from the cited 2026-07-01 snapshot."
        )
        if gap not in notes:
            errors.append("JAMA live-versus-snapshot evidence gap is not explicit")
        if "No later exact official-URL snapshot was available" not in notes:
            errors.append("JAMA later-snapshot search outcome is not recorded")

    required_audit_fragments = (
        "PR #599 blind audit head `7bb578d3`",
        "reply/recheck exact head `9e4234ac`",
        "final exact head `559994eb`",
        "codex `gpt-5.6-sol`",
        "| ultra |",
        "Template A: 8 P1 / 6 P2 / 1 P3",
        "first-party re-verification initially confirmed 3 P1",
        "Template B + further recheck: 5 P1 / 7 P2 / 2 P3",
        "docs-only contributor credit over substantive `7bb578d3`",
        "prior findings closed; Frontiers action-carrier reclassified as nonblocking maintainer follow-up",
    )
    for fragment in required_audit_fragments:
        if fragment not in audit:
            errors.append(f"2026-08-01 audit round missing exact receipt: {fragment}")
    old_round = next((line for line in audit.splitlines() if line.startswith("| 2026-07-30 |")), "")
    new_round = next((line for line in audit.splitlines() if line.startswith("| 2026-08-01 |")), "")
    if "`45653587`" not in old_round:
        errors.append("2026-07-30 audit row lost PR #599 head 45653587")
    if "`45653587`" in new_round:
        errors.append("2026-08-01 audit row incorrectly reuses head 45653587")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        errors = check(args.root)
    except MissingRequiredFile as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if errors:
        print("#619 disclosure closeout: FAIL", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print("#619 disclosure closeout: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
