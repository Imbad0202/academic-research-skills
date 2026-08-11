#!/usr/bin/env python3
"""Lint only explicitly named #669 generated output surfaces.

The checker never scans a directory or repository.  A pathway term is allowed
only in the exact candidate-name JSON field and its exact deterministic
``Candidate pathway examined:`` rendering.  The artifact remains a candidate
rule trace, never a determination.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

if __package__:
    from scripts.resolve_human_subjects_authority import ContractError, load_json
else:
    from resolve_human_subjects_authority import ContractError, load_json  # type: ignore[no-redef]


PATHWAY_TERMS: tuple[tuple[str, ...], ...] = (
    ("exempt",),
    ("expedited",),
    ("full", "board"),
    ("convened", "board"),
    ("not", "human", "subjects", "research"),
    ("nhsr",),
)
ALWAYS_BANNED_TERMS: tuple[tuple[str, ...], ...] = (
    ("no", "irb", "needed"),
    ("no", "irb", "required"),
    ("irb", "not", "required"),
    ("no", "ethics", "review", "needed"),
    ("no", "ethics", "review", "required"),
    ("approved",),
    ("approval",),
    ("approve",),
    ("approves",),
    ("approving",),
    ("cleared",),
    ("clearance",),
    ("clear",),
    ("clears",),
    ("low", "risk"),
    ("probability",),
    ("confidence",),
    ("likely",),
    ("unlikely",),
    ("probably",),
    ("chance",),
    ("odds",),
    ("likelihood",),
    ("percent",),
    ("percentage",),
    ("rank",),
    ("ranked",),
    ("ranking",),
    ("preferred",),
    ("recommended",),
    ("most", "studies", "like", "yours"),
    ("timeline",),
)
PERCENT_RE = re.compile(r"(?<![\w.])\d{1,3}(?:[.,]\d+)?\s*%")
TIME_ESTIMATE_RE = re.compile(
    r"\b(?:(?:within|takes?|estimated?)\s+)?(?:\d+|one|two|three|four|five|six|"
    r"seven|eight|nine|ten|eleven|twelve)\s+(?:business\s+)?(?:days?|weeks?|months?)\b"
)
MAX_RENDERED_BYTES = 8 * 1024 * 1024
MAX_SURFACE_NODES = 200_000


def normalize_surface(text: str) -> tuple[str, tuple[str, ...]]:
    """Return NFKC/case/whitespace normalized text and punctuation-free words."""
    normalized = unicodedata.normalize("NFKC", text).casefold()
    normalized = "".join(
        " "
        if unicodedata.category(char) == "Cc"
        else ""
        if unicodedata.category(char) in {"Cf", "Cs"}
        else char
        for char in normalized
    )
    normalized = " ".join(normalized.split())
    normalized = re.sub(r"\s*([:;,!?%])\s*", r"\1", normalized)
    words = tuple(re.findall(r"[^\W_]+", normalized, flags=re.UNICODE))
    return normalized, words


def _contains_sequence(words: tuple[str, ...], sequence: tuple[str, ...]) -> bool:
    width = len(sequence)
    return any(words[index : index + width] == sequence for index in range(len(words) - width + 1))


def _string_violations(text: str, *, permit_pathway_name: bool) -> list[str]:
    normalized, words = normalize_surface(text)
    errors: list[str] = []
    for phrase in ALWAYS_BANNED_TERMS:
        if _contains_sequence(words, phrase):
            errors.append(f"banned determination-adjacent phrase: {' '.join(phrase)}")
    if PERCENT_RE.search(normalized):
        errors.append("banned probability percentage")
    if TIME_ESTIMATE_RE.search(normalized):
        errors.append("banned pathway timeline estimate")
    if not permit_pathway_name:
        for phrase in PATHWAY_TERMS:
            if _contains_sequence(words, phrase):
                errors.append(f"pathway name appears outside candidate grammar: {' '.join(phrase)}")
    return errors


def _candidate_name_violations(text: str) -> list[str]:
    normalized, words = normalize_surface(text)
    errors: list[str] = []
    if len(words) > 12:
        errors.append("candidate pathway name exceeds 12 words")
    if re.search(r"[.!?;:]", normalized):
        errors.append("candidate pathway name must be a name, not sentence punctuation")
    subjects = {"this", "study", "activity", "project", "protocol", "research"}
    assertions = {
        "is",
        "are",
        "falls",
        "qualifies",
        "meets",
        "appears",
        "may",
        "will",
        "should",
    }
    if subjects & set(words) and assertions & set(words):
        errors.append("candidate pathway name is determination-shaped prose")
    return errors


def _walk_strings(value: Any, path: tuple[str | int, ...] = ()) -> list[tuple[tuple[str | int, ...], str]]:
    rows: list[tuple[tuple[str | int, ...], str]] = []
    stack: list[tuple[tuple[str | int, ...], Any]] = [(path, value)]
    visited = 0
    while stack:
        current_path, current = stack.pop()
        visited += 1
        if visited > MAX_SURFACE_NODES:
            raise ContractError(
                f"generated surface exceeds {MAX_SURFACE_NODES} JSON nodes"
            )
        if isinstance(current, dict):
            stack.extend(
                ((*current_path, key), child)
                for key, child in reversed(tuple(current.items()))
            )
        elif isinstance(current, list):
            stack.extend(
                ((*current_path, index), child)
                for index, child in reversed(tuple(enumerate(current)))
            )
        elif isinstance(current, str):
            rows.append((current_path, current))
    return rows


def _read_text_limited(path: Path) -> str:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise ContractError(f"cannot stat rendered artifact {path}: {exc}") from exc
    if size > MAX_RENDERED_BYTES:
        raise ContractError(
            f"rendered artifact exceeds {MAX_RENDERED_BYTES} bytes: {path}"
        )
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ContractError(f"cannot read rendered artifact {path}: {exc}") from exc


def _format_path(path: tuple[str | int, ...]) -> str:
    rendered = "$"
    for token in path:
        rendered += f"[{token}]" if isinstance(token, int) else f".{token}"
    return rendered


def _candidate_name_path(path: tuple[str | int, ...]) -> bool:
    return (
        len(path) == 3
        and path[0] == "candidate_pathways"
        and isinstance(path[1], int)
        and path[2] == "candidate_pathway_name"
    )


def lint_trace_surface(trace: dict[str, Any]) -> list[str]:
    """Inspect string leaves in one explicit generated JSON artifact."""
    errors: list[str] = []
    for path, value in _walk_strings(trace):
        candidate_name = _candidate_name_path(path)
        for message in _string_violations(value, permit_pathway_name=candidate_name):
            errors.append(f"trace {_format_path(path)}: {message}")
        if candidate_name:
            for message in _candidate_name_violations(value):
                errors.append(f"trace {_format_path(path)}: {message}")
    return errors


def _candidate_lines(trace: dict[str, Any]) -> set[str]:
    rows = trace.get("candidate_pathways")
    if not isinstance(rows, list):
        return set()
    result: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        profile = row.get("profile_ref")
        name = row.get("candidate_pathway_name")
        if isinstance(profile, dict) and isinstance(profile.get("profile_id"), str) and isinstance(name, str):
            result.add(f"Candidate pathway examined: {profile['profile_id']} {name}")
    return result


def lint_rendered_surface(trace: dict[str, Any], rendered: str) -> list[str]:
    """Inspect every line in one explicit rendering with exact candidate grammar."""
    allowed_candidate_lines = _candidate_lines(trace)
    errors: list[str] = []
    for line_number, line in enumerate(rendered.splitlines(), start=1):
        permit = line in allowed_candidate_lines
        for message in _string_violations(line, permit_pathway_name=permit):
            errors.append(f"rendered line {line_number}: {message}")
        if line.startswith("Candidate pathway examined:") and line not in allowed_candidate_lines:
            errors.append(f"rendered line {line_number}: candidate grammar does not exactly match trace")
    return errors


def lint_artifacts(trace: dict[str, Any], rendered: str | None = None) -> list[str]:
    errors = lint_trace_surface(trace)
    if rendered is not None:
        try:
            if __package__:
                from scripts.build_review_pathway_rule_trace import render_review_pathway_rule_trace
            else:
                from build_review_pathway_rule_trace import render_review_pathway_rule_trace  # type: ignore[no-redef]
            expected = render_review_pathway_rule_trace(trace)
        except (ContractError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"trace cannot be deterministically rendered: {exc}")
        else:
            if rendered != expected:
                errors.append("rendered artifact does not exactly equal the deterministic renderer")
        errors.extend(lint_rendered_surface(trace, rendered))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-json", type=Path, required=True)
    parser.add_argument("--rendered", type=Path)
    args = parser.parse_args(argv)
    try:
        trace = load_json(args.trace_json)
        rendered = _read_text_limited(args.rendered) if args.rendered else None
        errors = lint_artifacts(trace, rendered)
    except (ContractError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Review-pathway generated output lint passed (#669).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
