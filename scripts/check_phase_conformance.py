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
_METADATA_KEYS = frozenset({"title", "field", "word_count"})
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
    r"(?:^|\|\s*)\s*(?:[-*]\s*)?\*\*Severity\*\*:\s*"
    r"(?P<severity>Critical|Major|Minor)\b"
)
_ANCHOR_RE = re.compile(
    r"(?:^|\|\s*)\s*(?:[-*]\s*)?\*\*Evidence Anchor\*\*:\s*"
    r"(?P<value>[^|]+)"
)
_SEVERITY_DECL_RE = re.compile(
    r"\*\*Severity(?:\*\*)?\s*:",
    re.IGNORECASE,
)
_ANCHOR_DECL_RE = re.compile(
    r"\*\*Evidence Anchor(?:\*\*)?\s*:",
    re.IGNORECASE,
)
_FINDING_H3_RE = re.compile(r"^W[1-9]\d*: \S.*$")


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


def validate_metadata_envelope(metadata) -> None:
    if not isinstance(metadata, dict) or set(metadata) != _METADATA_KEYS:
        actual = (
            sorted(metadata)
            if isinstance(metadata, dict)
            else type(metadata).__name__
        )
        raise panel.ContractError(
            "[METADATA-INVALID: expected exact title/field/word_count "
            f"envelope, got {actual}]"
        )
    if (
        not isinstance(metadata["title"], str)
        or not metadata["title"].strip()
        or not isinstance(metadata["field"], str)
        or not metadata["field"].strip()
        or isinstance(metadata["word_count"], bool)
        or not isinstance(metadata["word_count"], int)
        or metadata["word_count"] < 0
    ):
        raise panel.ContractError(
            "[METADATA-INVALID: title and field must be non-empty strings; "
            "word_count must be a non-negative integer]"
        )


def check_manuscript_leakage(
    phase1_text: str, manuscript_text: str, metadata: dict, contract: dict
) -> None:
    validate_metadata_envelope(metadata)
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
    h2_positions = {
        match.group(1): index
        for index, line in enumerate(lines)
        if (match := panel._H2_RE.fullmatch(line))
    }
    if h2_positions["Scoring Plan Dissent"] > h2_positions.get(
        "Dimension Scores", -1
    ):
        raise ConformanceError(
            "[DISSENT-GRAMMAR: ## Scoring Plan Dissent must precede "
            "## Dimension Scores]"
        )
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
    uncommitted = dissent - set(plan.commitments)
    if uncommitted:
        raise ConformanceError(
            f"[DISSENT-GRAMMAR: dissent dimensions were not committed by "
            f"this seat {sorted(uncommitted)}]"
        )
    for did, value in report.scores.items():
        eligible = report.role in dimensions[did]["eligible_roles"]
        needs_trigger = eligible and value.score in {"block", "warn"}
        if needs_trigger != bool(value.trigger):
            raise ConformanceError(
                f"[TRIGGER-GRAMMAR: {report.path}: {did} trigger is required "
                "iff an eligible dimension scores block or warn]"
            )
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
    try:
        panel.validate_evidence_anchor(anchor, context)
    except panel.ReportError as exc:
        raise ConformanceError(str(exc)) from exc


def check_scoring_seat_anchors(report: panel.ReviewerReport) -> None:
    lines = panel.strip_fences(report.text)
    sections, dupes = panel.split_sections(lines)
    if "Review Body" in dupes or "Review Body" not in sections:
        raise ConformanceError(
            f"[REVIEW-BODY-MISSING: {report.path}]"
        )
    current_h2 = None
    for line in lines:
        if match := panel._H2_RE.fullmatch(line):
            current_h2 = match.group(1)
        elif _SEVERITY_DECL_RE.search(line) and current_h2 != "Review Body":
            raise ConformanceError(
                f"[FINDING-GRAMMAR: {report.path}: Severity outside "
                "## Review Body]"
            )
    review_lines = sections["Review Body"]
    blocks, subsection_dupes = panel.split_subsections(review_lines)
    if subsection_dupes:
        raise ConformanceError(
            f"[FINDING-GRAMMAR: {report.path}: duplicate finding heading]"
        )
    preamble = []
    for line in review_lines:
        if panel._H3_RE.fullmatch(line):
            break
        preamble.append(line)
    if any(_SEVERITY_DECL_RE.search(line) for line in preamble):
        raise ConformanceError(
            f"[FINDING-GRAMMAR: {report.path}: every finding with "
            "Severity must have its own ### finding heading]"
        )
    for title, block in blocks.items():
        severity_declarations = sum(
            len(_SEVERITY_DECL_RE.findall(line)) for line in block
        )
        severities = [
            match.group("severity") for line in block
            for match in _SEVERITY_RE.finditer(line)
        ]
        is_finding = _FINDING_H3_RE.fullmatch(title) is not None
        if severity_declarations and not is_finding:
            raise ConformanceError(
                f"[FINDING-GRAMMAR: {report.path}: every finding with "
                "Severity must have its own ### W<n>: <title> heading]"
            )
        if is_finding and any(panel._H4_RE.fullmatch(line) for line in block):
            raise ConformanceError(
                f"[FINDING-GRAMMAR: {report.path}: {title} may not nest "
                "a Severity finding under H4]"
            )
        if not is_finding:
            continue
        if len(severities) != 1 or severity_declarations != 1:
            raise ConformanceError(
                f"[FINDING-GRAMMAR: {report.path}: {title} must contain "
                "exactly one parseable Severity declaration]"
            )
        anchor_declarations = sum(
            len(_ANCHOR_DECL_RE.findall(line)) for line in block
        )
        anchors = [
            match.group("value") for line in block
            for match in _ANCHOR_RE.finditer(line)
        ]
        if severities[0] not in {"Critical", "Major"}:
            if anchor_declarations > 1 or len(anchors) != anchor_declarations:
                raise ConformanceError(
                    f"[FINDING-GRAMMAR: {report.path}: {title} may contain "
                    "at most one parseable Evidence Anchor declaration]"
                )
            if anchors:
                _validate_anchor(anchors[0], f"{report.path}:{title}")
            continue
        if len(anchors) != 1 or anchor_declarations != 1:
            raise ConformanceError(
                f"[ANCHOR-MISSING: {report.path}: {title} "
                f"{severities[0]} finding needs exactly one Evidence Anchor]"
            )
        _validate_anchor(anchors[0], f"{report.path}:{title}")


def check_da_anchors(report: panel.ReviewerReport) -> None:
    try:
        rows, major_anchors = panel.parse_da_tables(report.text, report.path)
    except panel.ReportError as exc:
        raise ConformanceError(str(exc)) from exc
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

    for anchor in major_anchors:
        if not anchor:
            raise ConformanceError(
                f"[ANCHOR-MISSING: {report.path}: DA MAJOR row]"
            )
        _validate_anchor(anchor, f"{report.path}:DA MAJOR")


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
