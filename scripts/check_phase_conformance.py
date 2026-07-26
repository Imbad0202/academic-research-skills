#!/usr/bin/env python3
"""Fail-closed Phase 1 -> Phase 2 conformance checker for reviewer Schema 13.2.

Usage:
  python scripts/check_phase_conformance.py --contract C.json --role eic \
      --phase1 eic.phase1.md --phase2 eic.phase2.md \
      --manuscript manuscript.md --metadata metadata.json

Exit 0 pass, 2 contract/infra failure, 3 reviewer conformance failure.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_panel_synthesis as panel  # noqa: E402

EXIT_PASS = 0
EXIT_CONTRACT = 2
EXIT_CONFORMANCE = 3
ANCHOR_TYPES = frozenset({
    "text", "table", "figure", "equation", "dataset", "absence"
})

_FIELD_PATTERNS = {
    "dimension_id": re.compile(r"^dimension_id: (?P<value>D\d+)$"),
    "what_to_look_for": re.compile(r"^what_to_look_for: (?P<value>\S.*)$"),
    "what_triggers_block": re.compile(
        r"^what_triggers_block: (?P<value>\S.*)$"
    ),
    "what_triggers_warn": re.compile(
        r"^what_triggers_warn: (?P<value>\S.*)$"
    ),
    "what_triggers_fatal": re.compile(
        r"^what_triggers_fatal: (?P<value>\S.*)$"
    ),
}
_DISSENT_DIM_RE = re.compile(r"^dimension_id: (?P<dim>D\d+)\s*$")
_DISSENT_RATIONALE_RE = re.compile(r"^rationale: (?P<text>\S.*)\s*$")
_SEVERITY_RE = re.compile(
    r"^(?:[-*]\s*)?\*\*Severity\*\*:\s*(?P<severity>Critical|Major|Minor)\b"
)
_ANCHOR_RE = re.compile(
    r"^(?:[-*]\s*)?\*\*Evidence Anchor\*\*:\s*(?P<value>\S.*)$"
)


class ConformanceError(Exception):
    """Reviewer conformance failure -> exit 3."""


@dataclass
class PhaseOnePlan:
    commitments: dict[str, dict[str, str]]
    warnings: list[str]


def _normalise(text: str) -> str:
    return " ".join(text.casefold().split())


def _one_field(
    lines: list[str], field: str, path: str, *, required: bool
) -> str | None:
    hits = [match.group("value") for line in lines
            if (match := _FIELD_PATTERNS[field].fullmatch(line))]
    expected = "exactly one" if required else "at most one"
    if (required and len(hits) != 1) or (not required and len(hits) > 1):
        raise ConformanceError(
            f"[PHASE1-GRAMMAR: {path}: expected {expected} canonical "
            f"{field}: line, found {len(hits)}]"
        )
    return hits[0] if hits else None


def parse_phase1(
    path: str, text: str, contract: dict, role: str
) -> PhaseOnePlan:
    lines = panel.strip_fences(text)
    sections, dupes = panel.split_sections(lines)
    if "Scoring Plan" in dupes or "Scoring Plan" not in sections:
        raise ConformanceError(
            f"[PHASE1-GRAMMAR: {path}: exactly one ## Scoring Plan required]"
        )
    dimensions = {d["id"]: d for d in contract["acceptance_dimensions"]}
    eligible = {
        did for did, dim in dimensions.items()
        if role in dim["eligible_roles"]
    }
    subsections, subsection_dupes = panel.split_subsections(
        sections["Scoring Plan"]
    )
    if subsection_dupes:
        raise ConformanceError(
            f"[PHASE1-GRAMMAR: {path}: duplicate scoring-plan subsection]"
        )
    commitments: dict[str, dict[str, str]] = {}
    warnings: list[str] = []
    for title, sublines in subsections.items():
        match = panel._DIM_H3_RE.fullmatch(title)
        if not match or match.group("dim") not in dimensions:
            raise ConformanceError(
                f"[PHASE1-GRAMMAR: {path}: invalid subsection '### {title}']"
            )
        did = match.group("dim")
        if did not in eligible:
            raise ConformanceError(
                f"[PHASE1-OUT-OF-ROLE: {path}: role {role} planned {did}]"
            )
        if match.group("name") != dimensions[did]["name"]:
            raise ConformanceError(
                f"[PHASE1-GRAMMAR: {path}: {did} name mismatch]"
            )
        fields = {
            field: _one_field(sublines, field, path, required=True)
            for field in (
                "dimension_id", "what_to_look_for",
                "what_triggers_block", "what_triggers_warn",
            )
        }
        mandatory = dimensions[did]["priority"] == "mandatory"
        fields["what_triggers_fatal"] = _one_field(
            sublines, "what_triggers_fatal", path, required=mandatory
        )
        if not mandatory and fields["what_triggers_fatal"] is not None:
            raise ConformanceError(
                f"[PHASE1-GRAMMAR: {path}: what_triggers_fatal is forbidden "
                f"on non-mandatory dimension {did}]"
            )
        if fields["dimension_id"] != did:
            raise ConformanceError(
                f"[PHASE1-GRAMMAR: {path}: heading {did} disagrees with "
                f"dimension_id={fields['dimension_id']}]"
            )
        triggers = [
            fields["what_triggers_block"],
            fields["what_triggers_warn"],
        ]
        if mandatory:
            triggers.append(fields["what_triggers_fatal"])
        if len({_normalise(value) for value in triggers}) != len(triggers):
            raise ConformanceError(
                f"[PHASE1-TRIGGER-COLLISION: {path}: {did} trigger "
                "commitments must be pairwise distinct]"
            )
        for field in (
            "what_triggers_block", "what_triggers_warn",
            "what_triggers_fatal",
        ):
            value = fields[field]
            if value is not None and len(value.split()) < 8:
                warnings.append(
                    f"[PHASE1-TRIGGER-SHORT: {path}: {did} {field} "
                    "has fewer than 8 words]"
                )
        commitments[did] = fields
    if set(commitments) != eligible:
        raise ConformanceError(
            f"[PHASE1-SCOPE: {path}: planned={sorted(commitments)}, "
            f"eligible={sorted(eligible)}]"
        )
    return PhaseOnePlan(commitments, warnings)


def _flatten_metadata_values(value) -> list[str]:
    if isinstance(value, dict):
        return [
            item
            for nested in value.values()
            for item in _flatten_metadata_values(nested)
        ]
    if isinstance(value, list):
        return [
            item
            for nested in value
            for item in _flatten_metadata_values(nested)
        ]
    if isinstance(value, (str, int, float, bool)):
        return [str(value)]
    return []


def check_manuscript_leakage(
    phase1_text: str, manuscript_text: str, metadata: dict, contract: dict
) -> None:
    phase1_norm = _normalise(phase1_text)
    words = _normalise(manuscript_text).split()
    exemption_haystacks = [
        _normalise(value) for value in _flatten_metadata_values(metadata)
    ]
    exemption_haystacks.append(_normalise(json.dumps(
        contract, ensure_ascii=False, sort_keys=True
    )))
    for index in range(max(0, len(words) - 11)):
        shingle = " ".join(words[index:index + 12])
        if shingle not in phase1_norm:
            continue
        if any(shingle in haystack for haystack in exemption_haystacks):
            continue
        raise ConformanceError(
            "[PHASE1-MANUSCRIPT-LEAK: 12-word manuscript shingle appears "
            "in Phase 1 outside metadata/contract exemptions]"
        )


def parse_dissent_dimensions(text: str) -> set[str]:
    lines = panel.strip_fences(text)
    sections, dupes = panel.split_sections(lines)
    if "Scoring Plan Dissent" in dupes:
        raise ConformanceError(
            "[DISSENT-GRAMMAR: duplicate ## Scoring Plan Dissent]"
        )
    if "Scoring Plan Dissent" not in sections:
        return set()
    dims = [match.group("dim") for line in sections["Scoring Plan Dissent"]
            if (match := _DISSENT_DIM_RE.fullmatch(line))]
    if not dims:
        raise ConformanceError(
            "[DISSENT-GRAMMAR: dissent section must name dimension_id]"
        )
    if len(dims) != len(set(dims)):
        raise ConformanceError("[DISSENT-GRAMMAR: duplicate dimension_id]")
    rationales = [
        match.group("text")
        for line in sections["Scoring Plan Dissent"]
        if (match := _DISSENT_RATIONALE_RE.fullmatch(line))
    ]
    if len(rationales) != len(dims):
        raise ConformanceError(
            "[DISSENT-GRAMMAR: each dissent requires one rationale: line]"
        )
    return set(dims)


def check_trigger_binding(
    report: panel.ReviewerReport,
    plan: PhaseOnePlan,
    dimensions: dict[str, dict],
    dissent: set[str],
) -> None:
    if len(dissent) >= 2:
        raise ConformanceError(
            f"[PROTOCOL-VIOLATION: multi_dissent=true, "
            f"dimensions={sorted(dissent)}]"
        )
    unknown = dissent - set(dimensions)
    if unknown:
        raise ConformanceError(
            f"[DISSENT-GRAMMAR: unknown dimensions {sorted(unknown)}]"
        )
    for did, value in report.scores.items():
        if did in dissent:
            if value.block_class == "fatal":
                raise ConformanceError(
                    f"[DISSENT-FATALITY: {did} dissent may not mint fatality]"
                )
            continue
        if not value.trigger:
            continue
        if value.score == "warn":
            field = "what_triggers_warn"
        elif value.block_class == "fatal":
            field = "what_triggers_fatal"
        else:
            field = "what_triggers_block"
        committed = plan.commitments.get(did, {}).get(field)
        if not committed or _normalise(value.trigger) not in _normalise(committed):
            raise ConformanceError(
                f"[TRIGGER-DRIFT: {did} {field} does not contain emitted "
                "trigger text]"
            )
        matching_fields = {
            candidate
            for candidate in (
                "what_triggers_block", "what_triggers_warn",
                "what_triggers_fatal",
            )
            if plan.commitments.get(did, {}).get(candidate)
            and _normalise(value.trigger) in _normalise(
                plan.commitments[did][candidate]
            )
        }
        if matching_fields != {field}:
            raise ConformanceError(
                f"[TRIGGER-AMBIGUOUS: {did} emitted trigger matches "
                f"{sorted(matching_fields)}, expected only {field}]"
            )


def _validate_anchor(anchor: str, context: str) -> None:
    match = re.match(
        r"^(?P<type>text|table|figure|equation|dataset|absence):\s*(?P<tail>\S.*)$",
        anchor,
        re.IGNORECASE,
    )
    if not match:
        raise ConformanceError(
            f"[ANCHOR-INVALID: {context}: expected typed anchor]"
        )
    anchor_type = match.group("type").casefold()
    tail = match.group("tail")
    if anchor_type == "text":
        quote = re.search(r'["“](?P<quote>[^"”]+)["”]', tail)
        if not quote or len(quote.group("quote").split()) > 25:
            raise ConformanceError(
                f"[ANCHOR-INVALID: {context}: text anchor needs a quoted "
                "excerpt of at most 25 words]"
            )
    if anchor_type == "absence" and not tail.strip():
        raise ConformanceError(
            f"[ANCHOR-INVALID: {context}: absence anchor must name checked "
            "surfaces]"
        )


def check_scoring_seat_anchors(report: panel.ReviewerReport) -> None:
    lines = panel.strip_fences(report.text)
    sections, _ = panel.split_sections(lines)
    if "Review Body" not in sections:
        raise ConformanceError(
            f"[REVIEW-BODY-MISSING: {report.path}]"
        )
    review_lines = sections["Review Body"]
    blocks, _ = panel.split_subsections(review_lines)
    current_finding = None
    for line in review_lines:
        if match := panel._H3_RE.fullmatch(line):
            current_finding = match.group(1)
        elif _SEVERITY_RE.match(line) and current_finding is None:
            raise ConformanceError(
                f"[FINDING-GRAMMAR: {report.path}: every finding with "
                "Severity must have its own ### finding heading]"
            )
    for title, block in blocks.items():
        severities = [
            match.group("severity") for line in block
            if (match := _SEVERITY_RE.match(line))
        ]
        if not severities:
            continue
        if len(severities) != 1:
            raise ConformanceError(
                f"[FINDING-GRAMMAR: {report.path}: {title} must contain "
                "exactly one Severity line]"
            )
        if severities[0] not in {"Critical", "Major"}:
            continue
        anchors = [match.group("value") for line in block
                   if (match := _ANCHOR_RE.match(line))]
        if len(anchors) != 1:
            raise ConformanceError(
                f"[ANCHOR-MISSING: {report.path}: {title} "
                f"{severities[0]} finding needs exactly one Evidence Anchor]"
            )
        _validate_anchor(anchors[0], f"{report.path}:{title}")


def check_da_anchors(report: panel.ReviewerReport) -> None:
    lines = panel.strip_fences(report.text)
    sections, _ = panel.split_sections(lines)
    if "Review Body" not in sections:
        raise ConformanceError(
            f"[REVIEW-BODY-MISSING: {report.path}]"
        )
    rows = panel.parse_da_critical_table(report.text, report.path)
    expected = [f"C{index}" for index in range(1, len(rows) + 1)]
    if list(rows) != expected:
        raise ConformanceError(
            f"[DA-CRITICAL-ID: {report.path}: IDs must be dense C1..Cn; "
            f"got={list(rows)}]"
        )
    for finding_id, anchor in rows.items():
        if not anchor:
            raise ConformanceError(
                f"[ANCHOR-MISSING: {report.path}: {finding_id}]"
            )
        _validate_anchor(anchor, f"{report.path}:{finding_id}")

    # MAJOR uses the same table grammar except that IDs are not the DA terminal
    # contract. Parse its Evidence Anchor cells locally while retaining the
    # shared CRITICAL parser as the single DA-ID authority.
    major_starts = [
        i for i, line in enumerate(lines)
        if line.strip() == "#### MAJOR"
    ]
    if len(major_starts) != 1:
        raise ConformanceError(
            f"[DA-MAJOR-PARSE: {report.path}: expected exactly one "
            f"#### MAJOR section, found {len(major_starts)}]"
        )
    start = major_starts[0]
    table_lines = []
    for line in lines[start + 1:]:
        if re.match(r"^#{2,4} ", line):
            break
        table_lines.append(line)
    header_index = next((i for i, line in enumerate(table_lines)
                         if "Evidence Anchor" in panel._markdown_cells(line)), None)
    if header_index is None:
        raise ConformanceError(
            f"[DA-MAJOR-PARSE: {report.path}: missing Evidence Anchor column]"
        )
    header = panel._markdown_cells(table_lines[header_index])
    anchor_col = header.index("Evidence Anchor")
    for line in table_lines[header_index + 2:]:
        cells = panel._markdown_cells(line)
        if not cells:
            continue
        if anchor_col >= len(cells) or not cells[anchor_col]:
            raise ConformanceError(
                f"[ANCHOR-MISSING: {report.path}: DA MAJOR row]"
            )
        _validate_anchor(cells[anchor_col], f"{report.path}:DA MAJOR")


def _parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--role", required=True)
    parser.add_argument("--phase1", required=True, type=Path)
    parser.add_argument("--phase2", required=True, type=Path)
    parser.add_argument("--manuscript", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)
    try:
        contract, _ = panel.load_contract(args.contract)
        if args.role not in panel.ROLE_SETS[contract["mode"]]:
            raise panel.ContractError(
                f"[ROLE-BINDING: --role {args.role} is invalid for "
                f"{contract['mode']}]"
            )
        phase1_text = panel._read_text(args.phase1)
        phase2_text = panel._read_text(args.phase2)
        manuscript_text = panel._read_text(args.manuscript)
        try:
            metadata = json.loads(panel._read_text(args.metadata))
        except json.JSONDecodeError as exc:
            raise panel.ContractError(
                f"[METADATA-INVALID: {args.metadata}: {exc}]"
            ) from exc
        plan = parse_phase1(str(args.phase1), phase1_text, contract, args.role)
        for warning in plan.warnings:
            print(warning)
        report = panel.parse_report(
            str(args.phase2), phase2_text, contract
        )
        if report.role != args.role:
            raise ConformanceError(
                f"[ROLE-BINDING: report declares {report.role}, dispatched "
                f"as {args.role}]"
            )
        check_manuscript_leakage(
            phase1_text, manuscript_text, metadata, contract
        )
        dissent = parse_dissent_dimensions(phase2_text)
        dimensions = {
            dim["id"]: dim for dim in contract["acceptance_dimensions"]
        }
        check_trigger_binding(report, plan, dimensions, dissent)
        if report.role == "da":
            check_da_anchors(report)
        else:
            check_scoring_seat_anchors(report)
    except panel.ContractError as exc:
        print(exc)
        return EXIT_CONTRACT
    except (panel.ReportError, ConformanceError) as exc:
        print(exc)
        return EXIT_CONFORMANCE
    print("PHASE-CONFORMANCE: PASS")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
