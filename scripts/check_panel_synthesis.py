#!/usr/bin/env python3
"""Validate Schema 13.2 reviewer cards and recompute panel synthesis.

Schema 13.2 removes per-seat failure-condition decisions. This checker parses
role-scoped dimension scores, evaluates each condition per dimension over only
its assessed eligible seats, verifies the synthesizer audit lines, and enforces
the DA-CRITICAL terminal consistency gate.

Exit codes (precedence 2 > 3 > 1):
  0 pass
  1 synthesis-layer failure
  2 contract/infra failure
  3 reviewer-report failure
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_sprint_contract  # noqa: E402

EXIT_PASS = 0
EXIT_SYNTHESIS = 1
EXIT_CONTRACT = 2
EXIT_REVIEWER = 3

ACTION_ENUM = frozenset({
    "editorial_decision=accept",
    "editorial_decision=minor_revision",
    "editorial_decision=major_revision",
    "editorial_decision=reject",
})
SCORE_ORDER = {"pass": 0, "warn": 1, "block": 2}
ROLE_SETS = check_sprint_contract.ROLE_SETS


class ContractError(Exception):
    """Contract/infra failure -> exit 2."""


class ReportError(Exception):
    """Reviewer-report failure -> exit 3."""


class SynthesisError(Exception):
    """Synthesis-output failure -> exit 1."""


@dataclass(frozen=True)
class DimensionScore:
    score: str
    block_class: str | None = None
    trigger: str | None = None
    abstain_reason: str | None = None


@dataclass
class ReviewerReport:
    path: str
    role: str
    scores: dict[str, DimensionScore]
    text: str


@dataclass(frozen=True)
class ExpressionAtom:
    dimension_ids: tuple[str, ...]
    dimension_quantifier: str
    score: str | None = None
    or_worse: bool = False
    fatal: bool = False


@dataclass
class Synthesis:
    fired: list[str]
    decision: str
    dimension_verdicts: dict[str, str]
    adjudications: dict[str, str]
    rejection_rationales: dict[str, str]
    marker_count: int | None


# --- Markdown helpers shared with check_phase_conformance.py -------------------

_FENCE_OPEN_RE = re.compile(
    r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>[^\n]*)$"
)
_FENCE_CLOSE_RE = re.compile(
    r"^ {0,3}(?P<fence>`{3,}|~{3,})[ \t]*$"
)
_COMMONMARK_LINE_END_RE = re.compile(r"\r\n?|\n")
_H2_RE = re.compile(r"^## (.+?)\s*$")
_H3_RE = re.compile(r"^### (.+?)\s*$")
_H4_RE = re.compile(r"^#### (.+?)\s*$")
_DIM_H3_RE = re.compile(r"^(?P<dim>D\d+): (?P<name>.+)$")
_ROLE_RE = re.compile(r"^contract_role: (?P<role>[a-z_]+)\s*$")
_SCORE_RE = re.compile(r"^score: (?P<value>block|warn|pass|not_assessed)\s*$")
_BLOCK_CLASS_RE = re.compile(r"^block_class: (?P<value>fatal|repairable)\s*$")
_TRIGGER_RE = re.compile(r'^trigger: "(?P<value>[^"\n]+)"\s*$')
_ABSTAIN_RE = re.compile(r"^abstain_reason: (?P<value>\S.*)\s*$")
_DECISION_RE = re.compile(r"^(?P<action>editorial_decision=[a-z_]+)\s*$")
_RETIRED_DECISION_RE = re.compile(
    r"^\s*editorial_decision=\S+\s*$", re.IGNORECASE
)
_DA_SEVERITY_DECL_RE = re.compile(
    r"\*\*Severity(?:\*\*)?\s*:",
    re.IGNORECASE,
)
_DA_ISSUE_ID_RE = re.compile(r"^[CM][1-9]\d*$", re.IGNORECASE)
_DA_TYPED_ANCHOR_RE = re.compile(
    r"^(?:text|table|figure|equation|dataset|absence)\s*:",
    re.IGNORECASE,
)
_RAW_HTML_TABLE_RE = re.compile(
    r"<\s*/?\s*(?:table|thead|tbody|tr|th|td)\b", re.IGNORECASE
)
_HTML_COMMENT_RE = re.compile(r"<!--")
_DA_FENCED_BLOCK_SENTINEL = "\0DA_FENCED_BLOCK\0"
_DEFAULT_IGNORABLE_RANGES = (
    (0x00AD, 0x00AD), (0x034F, 0x034F), (0x061C, 0x061C),
    (0x115F, 0x1160), (0x17B4, 0x17B5), (0x180B, 0x180F),
    (0x200B, 0x200F), (0x202A, 0x202E), (0x2060, 0x206F),
    (0x3164, 0x3164), (0xFE00, 0xFE0F), (0xFEFF, 0xFEFF),
    (0xFFA0, 0xFFA0), (0xFFF0, 0xFFF8), (0x1BCA0, 0x1BCA3),
    (0x1D173, 0x1D17A),
    (0xE0000, 0xE0FFF),
)


def strip_fences(
    text: str, *, preserve_fenced_blocks: bool = False
) -> list[str]:
    """Remove CommonMark fenced blocks; optionally retain an opaque sentinel."""
    out: list[str] = []
    fence_char: str | None = None
    fence_len = 0
    for line in _COMMONMARK_LINE_END_RE.split(text):
        if fence_char is not None:
            match = _FENCE_CLOSE_RE.fullmatch(line)
            if match:
                token = match.group("fence")
                if token[0] == fence_char and len(token) >= fence_len:
                    fence_char, fence_len = None, 0
            continue
        match = _FENCE_OPEN_RE.fullmatch(line)
        if match:
            token = match.group("fence")
            info = match.group("info")
            if token[0] != "`" or "`" not in info:
                fence_char, fence_len = token[0], len(token)
                if preserve_fenced_blocks:
                    out.append(_DA_FENCED_BLOCK_SENTINEL)
                continue
        out.append(line)
    return out


_INLINE_CODE_LINE_RE = re.compile(
    r"^ {0,3}(?P<ticks>`+)(?P<body>[^`]+?)(?P=ticks)[ \t]*$"
)


def audit_candidate_lines(text: str) -> list[str]:
    """Candidate lines for the synthesis mechanical audit-line grammars.

    The four audit lines (``dimension_verdicts`` / ``fired_conditions`` /
    ``da_critical_adjudications`` / bare ``editorial_decision=``) are
    routinely emitted inside a CommonMark code fence, or wrapped whole in an
    inline code span — both render the line verbatim and visibly to a
    reader, so rejecting them is a false abort, not a leak guard (#637:
    every synthesis first attempt of the 2026-08-03 baseline cohort, 6/6,
    fenced the audit block; one retry re-emitted it as inline code spans).
    This walker therefore keeps fenced content (dropping only the
    fence-marker lines themselves, with the same open/close state machine as
    ``strip_fences``) and additionally yields the unwrapped body of any
    non-fenced line that is entirely one inline code span. Candidates are
    normalized to what a CommonMark renderer would DISPLAY, since rendered
    visibility is the acceptance criterion: an inline span whose body has
    both a leading and a trailing space renders with one space stripped
    from each side, and lines inside an indented fence render dedented by
    up to the opener's indent — both normalizations are applied here so
    the start-anchored grammars see the displayed text.

    Declared boundaries (ACCEPTED misses — change deliberately, with
    tests): blockquoted or emphasis-wrapped audit lines never match the
    line-anchored grammars and stay non-candidates; an inline code span
    inside a fence renders its backticks literally and is not unwrapped;
    the rejection-rationale and DA-consistency-marker grammars keep the
    plain-line source in ``parse_synthesis`` because both are quotable
    diagnostics whose fenced or wrapped occurrences read as quotation.
    One asymmetry of that boundary is accepted deliberately: a fenced
    marker in a state where the marker is forbidden stays invisible to
    ``check_da_terminal_gate`` and no longer aborts upstream (pre-#637 the
    whole fenced block aborted at ``fired_conditions``); the editorial
    decision itself is independently recomputed from the reviewer cards by
    the layer-2 check, so the slip is an accounting cosmetic, not a
    decision channel.
    """
    out: list[str] = []
    fence_char: str | None = None
    fence_len = 0
    fence_indent = 0
    for line in _COMMONMARK_LINE_END_RE.split(text):
        if fence_char is not None:
            match = _FENCE_CLOSE_RE.fullmatch(line)
            if (match and match.group("fence")[0] == fence_char
                    and len(match.group("fence")) >= fence_len):
                fence_char, fence_len, fence_indent = None, 0, 0
            else:
                dedent = 0
                while (dedent < fence_indent and dedent < len(line)
                       and line[dedent] == " "):
                    dedent += 1
                out.append(line[dedent:])
            continue
        match = _FENCE_OPEN_RE.fullmatch(line)
        if match:
            token = match.group("fence")
            info = match.group("info")
            if token[0] != "`" or "`" not in info:
                fence_char, fence_len = token[0], len(token)
                fence_indent = match.start("fence")
                continue
        out.append(line)
        if span := _INLINE_CODE_LINE_RE.fullmatch(line):
            body = span.group("body")
            if (len(body) >= 2 and body[0] == " " and body[-1] == " "
                    and body.strip(" ")):
                body = body[1:-1]
            out.append(body)
    return out


def _split_by(lines: list[str], heading_re: re.Pattern[str]):
    sections: dict[str, list[str]] = {}
    dupes: set[str] = set()
    current: list[str] | None = None
    for line in lines:
        match = heading_re.match(line)
        if match:
            title = match.group(1)
            if title in sections:
                dupes.add(title)
            current = sections.setdefault(title, [])
            continue
        if current is not None:
            current.append(line)
    return sections, dupes


def split_sections(lines: list[str]):
    return _split_by(lines, _H2_RE)


def split_subsections(lines: list[str]):
    return _split_by(lines, _H3_RE)


def exactly_one(
    lines: list[str],
    pattern: re.Pattern[str],
    field: str,
    path: str,
    group: str = "value",
    *,
    required: bool = True,
) -> str | None:
    hits = [m.group(group) for line in lines if (m := pattern.fullmatch(line))]
    expected = "exactly one" if required else "at most one"
    if (required and len(hits) != 1) or (not required and len(hits) > 1):
        raise ReportError(
            f"[REPORT-PARSE: {path}: expected {expected} {field} line, "
            f"found {len(hits)}]"
        )
    return hits[0] if hits else None


def _split_gfm_cells(row: str) -> list[str]:
    cells: list[str] = []
    current: list[str] = []
    for char in row:
        if char == "|":
            backslashes = 0
            for previous in reversed(current):
                if previous != "\\":
                    break
                backslashes += 1
            if backslashes % 2 == 0:
                cells.append("".join(current).strip())
                current = []
                continue
        current.append(char)
    cells.append("".join(current).strip())
    return cells


def _markdown_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return _split_gfm_cells(stripped[1:-1])


def _possible_markdown_cells(line: str) -> list[str]:
    """Return cells from either outer-pipe or pipe-less GFM table rows."""
    stripped = line.strip()
    if "|" not in stripped:
        return []
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return _split_gfm_cells(stripped)


class _VisibleTextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _is_default_ignorable(char: str) -> bool:
    codepoint = ord(char)
    return any(start <= codepoint <= end for start, end in _DEFAULT_IGNORABLE_RANGES)


def _rendered_header_cell(cell: str) -> str:
    """Normalize common inline Markdown wrappers to their visible cell text."""
    rendered = re.sub(r"\\([^\w\s])", r"\1", cell)
    rendered = re.sub(
        r"!?\[([^\]]*)\](?:\([^)]+\)|\[[^\]]*\])", r"\1", rendered
    )
    rendered = re.sub(r"\[([^\]]+)\]", r"\1", rendered)
    parser = _VisibleTextHTMLParser()
    parser.feed(rendered)
    rendered = "".join(parser.parts)
    rendered = unicodedata.normalize("NFKC", rendered)
    rendered = "".join(
        char for char in rendered
        if unicodedata.category(char) != "Cf"
        and not _is_default_ignorable(char)
    )
    rendered = re.sub(r"[*_~`]+", "", rendered)
    return re.sub(r"\s+", " ", rendered).strip().casefold()


def _balanced_square_brackets(text: str) -> bool:
    """Return whether square brackets are ordered and balanced in locator text."""
    depth = 0
    for char in text:
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def _quoted_excerpts(text: str) -> list[str] | None:
    """Return every balanced straight/curly excerpt, including nested pairs."""
    stack: list[tuple[str, int]] = []
    excerpts: list[str] = []
    for index, char in enumerate(text):
        if char == "“":
            stack.append(("curly", index + 1))
        elif char == "”":
            if not stack or stack[-1][0] != "curly":
                return None
            _, start = stack.pop()
            excerpts.append(text[start:index])
        elif char == '"':
            if stack and stack[-1][0] == "straight":
                _, start = stack.pop()
                excerpts.append(text[start:index])
            else:
                stack.append(("straight", index + 1))
    return None if stack else excerpts


def _absence_parts(text: str) -> tuple[str, str, str] | None:
    """Parse the two reserved absence separators without regex backtracking."""
    expected_separator = " — expected "
    checked_separator = "; checked "
    if (
        text.count(expected_separator) != 1
        or text.count(checked_separator) != 1
    ):
        return None
    where, found_expected, remainder = text.partition(expected_separator)
    expected, found_checked, surfaces = remainder.partition(checked_separator)
    if not found_expected or not found_checked:
        return None
    parts = (where, expected, surfaces)
    return parts if all(part.strip() for part in parts) else None


def validate_evidence_anchor(anchor: str, context: str) -> None:
    """Validate the shared finding-anchor grammar for either checker."""
    value = anchor.strip()
    if value.startswith("["):
        if not value.endswith("]"):
            raise ReportError(
                f"[ANCHOR-INVALID: {context}: unpaired square wrapper]"
            )
        square_inner = value[1:-1]
        if square_inner != square_inner.strip():
            raise ReportError(
                f"[ANCHOR-INVALID: {context}: padded square wrapper]"
            )
        value = square_inner
    if value.startswith("`"):
        if not value.endswith("`"):
            raise ReportError(
                f"[ANCHOR-INVALID: {context}: unpaired backtick wrapper]"
            )
        backtick_inner = value[1:-1]
        if backtick_inner != backtick_inner.strip():
            raise ReportError(
                f"[ANCHOR-INVALID: {context}: padded backtick wrapper]"
            )
        value = backtick_inner
    match = re.match(
        r"^(?P<type>text|table|figure|equation|dataset|absence):\s*"
        r"(?P<tail>\S.*)$",
        value,
        re.IGNORECASE,
    )
    if not match:
        tag = "ANCHOR-MISSING" if not value else "ANCHOR-INVALID"
        raise ReportError(f"[{tag}: {context}: expected typed anchor]")
    tail = match.group("tail")
    if not _balanced_square_brackets(tail) or tail.count("`") % 2:
        raise ReportError(
            f"[ANCHOR-INVALID: {context}: locator delimiters must be balanced]"
        )
    if match.group("type").casefold() == "text":
        quote_texts = _quoted_excerpts(tail)
        if (
            not quote_texts
            or any(not text.strip() or len(text.split()) > 25
                   for text in quote_texts)
        ):
            raise ReportError(
                f"[ANCHOR-INVALID: {context}: text anchor needs balanced "
                "quoted excerpts of at most 25 words]"
            )
    elif match.group("type").casefold() == "absence":
        if _absence_parts(tail) is None:
            raise ReportError(
                f"[ANCHOR-INVALID: {context}: absence anchor needs "
                "<where> — expected <item>; checked <surfaces>]"
            )


def _require_single_da_table_heading(
    review_lines: list[str], heading: str, path: str
) -> int:
    """Return the sole exact DA issue-table heading position."""
    parse_tag = f"DA-{heading}-PARSE"
    starts = [
        i for i, line in enumerate(review_lines)
        if _H4_RE.fullmatch(line)
        and _H4_RE.fullmatch(line).group(1) == heading
    ]
    if len(starts) != 1:
        raise ReportError(
            f"[{parse_tag}: {path}: expected exactly one "
            f"#### {heading} section, found {len(starts)}]"
        )
    return starts[0]


def _parse_da_table_block(
    review_lines: list[str], heading: str, path: str, start: int, end: int
) -> tuple[list[list[str]], int, int]:
    """Return table data lines plus ``#`` and anchor column positions."""
    parse_tag = f"DA-{heading}-PARSE"
    block = review_lines[start + 1:end]
    nonblank = [i for i, line in enumerate(block) if line.strip()]
    header_index = nonblank[0] if nonblank else None
    if header_index is None:
        raise ReportError(
            f"[{parse_tag}: {path}: missing table header with # and "
            "Evidence Anchor columns]"
        )
    header = _markdown_cells(block[header_index])
    if "#" not in header or "Evidence Anchor" not in header:
        raise ReportError(
            f"[{parse_tag}: {path}: missing table header: first nonblank "
            "line must have # and Evidence Anchor columns]"
        )
    if header.count("#") != 1 or header.count("Evidence Anchor") != 1:
        raise ReportError(
            f"[{parse_tag}: {path}: table header must contain exactly one # "
            "and one Evidence Anchor column]"
        )
    separator_index = header_index + 1
    separator = (
        _markdown_cells(block[separator_index])
        if separator_index < len(block) else []
    )
    if (
        len(separator) != len(header)
        or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator)
    ):
        raise ReportError(
            f"[{parse_tag}: {path}: missing or malformed Markdown table separator]"
        )
    rows: list[list[str]] = []
    table_tail = block[header_index + 2:]
    for index, line in enumerate(table_tail):
        if not line.strip():
            if any(
                trailing.strip() for trailing in table_tail[index + 1:]
            ):
                raise ReportError(
                    f"[{parse_tag}: {path}: the DA issue tables are terminal; "
                    "put Review Body prose before #### CRITICAL and emit no "
                    "nonblank content after a table ends]"
                )
            break
        cells = _markdown_cells(line)
        if len(cells) != len(header):
            raise ReportError(
                f"[{parse_tag}: {path}: every data row must be an "
                "outer-pipe-delimited row with the header column count]"
            )
        rows.append(cells)
    return rows, header.index("#"), header.index("Evidence Anchor")


def _check_da_shadow_issue_surfaces(lines: list[str], path: str) -> None:
    """Reject issue-table surfaces outside the two canonical DA bands."""
    current_h2: str | None = None
    in_canonical_da_band = False
    for candidate in lines:
        if h2_match := _H2_RE.fullmatch(candidate):
            current_h2 = h2_match.group(1)
            in_canonical_da_band = False
            continue
        if _H3_RE.fullmatch(candidate):
            in_canonical_da_band = False
            continue
        if h4_match := _H4_RE.fullmatch(candidate):
            in_canonical_da_band = (
                current_h2 == "Review Body"
                and h4_match.group(1) in {"CRITICAL", "MAJOR"}
            )
            continue
        if _RAW_HTML_TABLE_RE.search(candidate):
            raise ReportError(
                f"[DA-TABLE-PARSE: {path}: unexpected raw HTML issue-table "
                "surface outside the canonical CRITICAL and MAJOR bands]"
            )
        if in_canonical_da_band:
            continue
        raw_cells = _possible_markdown_cells(candidate)
        cells = {_rendered_header_cell(cell) for cell in raw_cells}
        issue_payload = any(
            _DA_ISSUE_ID_RE.fullmatch(cell)
            or _DA_TYPED_ANCHOR_RE.search(cell)
            for cell in cells
        )
        if "#" in cells or "evidence anchor" in cells or issue_payload:
            raise ReportError(
                f"[DA-TABLE-PARSE: {path}: unexpected issue-table band outside "
                "the canonical CRITICAL and MAJOR bands]"
            )


def parse_da_tables(
    text: str, path: str = "<report>"
) -> tuple[dict[str, str], list[str]]:
    """Parse both mandatory DA tables from the report's ``Review Body``.

    Returns ``(critical_id_to_anchor, major_anchors)``. Both exact H4 sections
    and their exact ``#`` / ``Evidence Anchor`` columns are required even when
    their tables are empty. This is the single structural parser used by both
    the phase-conformance and synthesis checkers.
    """
    raw_lines = _COMMONMARK_LINE_END_RE.split(text)
    if any(_HTML_COMMENT_RE.search(line) for line in raw_lines):
        raise ReportError(
            f"[DA-TABLE-PARSE: {path}: HTML comments are forbidden in DA reports]"
        )
    lines = strip_fences(text, preserve_fenced_blocks=True)
    sections, dupes = split_sections(lines)
    if "Review Body" in dupes or "Review Body" not in sections:
        raise ReportError(
            f"[DA-TABLE-PARSE: {path}: expected exactly one ## Review Body]"
        )
    review_lines = sections["Review Body"]
    if any(_DA_SEVERITY_DECL_RE.search(line) for line in lines):
        raise ReportError(
            f"[DA-FINDING-GRAMMAR: {path}: standalone Severity declarations "
            "are forbidden; use the CRITICAL and MAJOR issue tables]"
        )
    critical_start = _require_single_da_table_heading(
        review_lines, "CRITICAL", path
    )
    major_start = _require_single_da_table_heading(
        review_lines, "MAJOR", path
    )
    if critical_start >= major_start:
        raise ReportError(
            f"[DA-TABLE-PARSE: {path}: #### CRITICAL must precede #### MAJOR]"
        )
    _check_da_shadow_issue_surfaces(lines, path)
    critical_lines, critical_id_col, critical_anchor_col = _parse_da_table_block(
        review_lines, "CRITICAL", path, critical_start, major_start
    )
    major_lines, major_id_col, major_anchor_col = _parse_da_table_block(
        review_lines, "MAJOR", path, major_start, len(review_lines)
    )

    rows: dict[str, str] = {}
    for cells in critical_lines:
        finding_id = cells[critical_id_col]
        if not re.fullmatch(r"C[1-9]\d*", finding_id):
            raise ReportError(
                f"[DA-CRITICAL-PARSE: {path}: invalid CRITICAL ID "
                f"'{finding_id}'; expected C1..Cn]"
            )
        if finding_id in rows:
            raise ReportError(
                f"[DA-CRITICAL-PARSE: {path}: duplicate CRITICAL ID {finding_id}]"
            )
        anchor = cells[critical_anchor_col]
        validate_evidence_anchor(anchor, f"{path}:{finding_id}")
        rows[finding_id] = anchor

    major_anchors: list[str] = []
    for cells in major_lines:
        if not cells[major_id_col]:
            raise ReportError(
                f"[DA-MAJOR-PARSE: {path}: empty MAJOR # cell]"
            )
        anchor = cells[major_anchor_col]
        validate_evidence_anchor(anchor, f"{path}:DA MAJOR")
        major_anchors.append(anchor)
    return rows, major_anchors


def parse_da_critical_table(text: str, path: str = "<report>") -> dict[str, str]:
    """Compatibility wrapper over the shared two-table DA parser."""
    return parse_da_tables(text, path)[0]


# --- Contract and report parsing ----------------------------------------------

def _read_text(path: Path | str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ContractError(f"[IO-ERROR: {path}: {exc}]") from exc


def load_contract(path: Path | str):
    try:
        contract = json.loads(_read_text(path))
    except json.JSONDecodeError as exc:
        raise ContractError(f"[CONTRACT-INVALID: {path}: {exc}]") from exc
    problems = check_sprint_contract.validate(contract)
    problems += check_sprint_contract.check_structural_invariants(contract)
    if problems:
        raise ContractError(
            f"[CONTRACT-INVALID: {path}: {'; '.join(problems)}]"
        )
    mode = contract.get("mode")
    if mode not in ROLE_SETS:
        raise ContractError(
            f"[CONTRACT-INELIGIBLE: unsupported reviewer mode {mode}]"
        )
    expected = check_sprint_contract.EXPECTED_PANEL_SIZE[mode]
    if contract.get("panel_size") != expected:
        raise ContractError(
            f"[CONTRACT-INELIGIBLE: panel_size={contract.get('panel_size')} "
            f"inconsistent with mode={mode}; expected {expected}]"
        )
    accept_grade_action(contract["failure_conditions"])
    dimensions = {d["id"]: d for d in contract["acceptance_dimensions"]}
    expressions = {
        condition["condition_id"]: parse_expression(
            condition["expression"], dimensions, condition["condition_id"]
        )
        for condition in contract["failure_conditions"]
    }
    return contract, expressions


def parse_report(path: str, text: str, contract: dict) -> ReviewerReport:
    lines = strip_fences(text)
    sections, dupes = split_sections(lines)
    if "Dimension Scores" in dupes:
        raise ReportError(
            f"[REPORT-PARSE: {path}: duplicated ## Dimension Scores]"
        )
    if "Dimension Scores" not in sections:
        raise ReportError(
            f"[REPORT-PARSE: {path}: missing ## Dimension Scores]"
        )
    for retired in ("Failure Condition Checks", "Editorial Decision"):
        if retired in sections:
            raise ReportError(
                f"[V1-GRAMMAR-RETIRED: {path}: ## {retired} is forbidden "
                "under Schema 13.2]"
            )
    if any(_RETIRED_DECISION_RE.fullmatch(line) for line in lines):
        raise ReportError(
            f"[V1-GRAMMAR-RETIRED: {path}: bare editorial_decision line is "
            "forbidden under Schema 13.2]"
        )
    role = exactly_one(lines, _ROLE_RE, "contract_role", path, "role")
    role_set = ROLE_SETS[contract["mode"]]
    if role not in role_set:
        raise ReportError(
            f"[REPORT-ROLE: {path}: role={role} is not valid for "
            f"{contract['mode']}]"
        )

    dims = {d["id"]: d for d in contract["acceptance_dimensions"]}
    subsections, subsection_dupes = split_subsections(sections["Dimension Scores"])
    if subsection_dupes:
        raise ReportError(
            f"[REPORT-PARSE: {path}: duplicated Dimension Scores subsection(s) "
            f"{sorted(subsection_dupes)}]"
        )
    scores: dict[str, DimensionScore] = {}
    for title, sublines in subsections.items():
        match = _DIM_H3_RE.fullmatch(title)
        if not match or match.group("dim") not in dims:
            raise ReportError(
                f"[REPORT-PARSE: {path}: unknown Dimension Scores subsection "
                f"'### {title}']"
            )
        did = match.group("dim")
        if match.group("name") != dims[did]["name"]:
            raise ReportError(
                f"[REPORT-PARSE: {path}: {did} name mismatch]"
            )
        score = exactly_one(sublines, _SCORE_RE, f"score ({did})", path)
        block_class = exactly_one(
            sublines, _BLOCK_CLASS_RE, f"block_class ({did})", path,
            required=False
        )
        trigger = exactly_one(
            sublines, _TRIGGER_RE, f"trigger ({did})", path, required=False
        )
        abstain_reason = exactly_one(
            sublines, _ABSTAIN_RE, f"abstain_reason ({did})", path,
            required=False
        )
        eligible = role in dims[did]["eligible_roles"]
        if eligible and score == "not_assessed" and not abstain_reason:
            raise ReportError(
                f"[ABSTENTION-INVALID: {path}: eligible role {role} must give "
                f"abstain_reason for {did}]"
            )
        if not eligible and score != "not_assessed":
            raise ReportError(
                f"[OUT-OF-ROLE-SCORE: {path}: role {role} may not score {did}]"
            )
        if not eligible and abstain_reason:
            raise ReportError(
                f"[ABSTENTION-INVALID: {path}: structural abstention on {did} "
                "must not carry abstain_reason]"
            )
        mandatory_block = (
            eligible and score == "block" and dims[did]["priority"] == "mandatory"
        )
        if mandatory_block != bool(block_class):
            raise ReportError(
                f"[BLOCK-CLASS-INVALID: {path}: {did} block_class is required "
                "iff an eligible mandatory dimension scores block]"
            )
        needs_trigger = eligible and score in {"block", "warn"}
        if needs_trigger != bool(trigger):
            raise ReportError(
                f"[TRIGGER-GRAMMAR: {path}: {did} trigger is required iff an "
                "eligible dimension scores block or warn]"
            )
        if score != "not_assessed" and abstain_reason:
            raise ReportError(
                f"[ABSTENTION-INVALID: {path}: {did} scored result may not "
                "carry abstain_reason]"
            )
        scores[did] = DimensionScore(
            score, block_class, trigger, abstain_reason
        )
    missing = [did for did in dims if did not in scores]
    if missing:
        raise ReportError(
            f"[REPORT-PARSE: {path}: missing Dimension Scores for {missing}]"
        )
    return ReviewerReport(path, role, scores, text)


# --- Closed expression grammar and two-stage evaluation -----------------------

_SCORE = r"'(?P<score>block|warn|pass)'"
_EXPRESSION_PATTERNS = (
    ("any_priority", re.compile(
        r"^any (?:(?P<p1>[a-z]+) dimension|dimension with priority="
        r"(?P<p2>[a-z]+)|(?P<p3>[a-z]+)-priority dimension) scores "
        + _SCORE + r"$")),
    ("count_priority", re.compile(
        r"^two or more (?:(?P<p1>[a-z]+) dimensions|dimensions with priority="
        r"(?P<p2>[a-z]+)) score " + _SCORE + r" or worse$")),
    ("every_priority", re.compile(
        r"^every (?P<p1>[a-z]+) dimension scores " + _SCORE + r"$")),
    ("dim_exact", re.compile(r"^(?P<dim>D\d+) scores " + _SCORE + r"$")),
    ("fatal_priority", re.compile(
        r"^any (?P<p1>[a-z]+) dimension has a fatal block$")),
    ("fatal_dim", re.compile(r"^(?P<dim>D\d+) has a fatal block$")),
    ("any_all", re.compile(
        r"^any dimension scores " + _SCORE + r" or worse$")),
    ("dim_threshold", re.compile(
        r"^(?P<dim>D\d+) scores " + _SCORE + r" or worse$")),
    ("every_all", re.compile(
        r"^every dimension scores " + _SCORE + r"$")),
)


def parse_expression(
    expression: str, dimensions: dict[str, dict], condition_id: str
) -> tuple[ExpressionAtom, ...]:
    atoms: list[ExpressionAtom] = []
    for part in expression.split(" AND "):
        for kind, pattern in _EXPRESSION_PATTERNS:
            match = pattern.fullmatch(part)
            if match:
                break
        else:
            raise ContractError(
                f"[EXPRESSION-UNRECOGNISED: condition_id={condition_id}, "
                f"expression={expression}]"
            )
        if kind in {"dim_exact", "fatal_dim", "dim_threshold"}:
            did = match.group("dim")
            if did not in dimensions:
                raise ContractError(
                    f"[EXPRESSION-SEMANTIC: condition_id={condition_id}: "
                    f"unknown dimension {did}]"
                )
            dim_ids = (did,)
        elif kind in {"any_all", "every_all"}:
            dim_ids = tuple(dimensions)
        else:
            priority = match.group("p1") or match.groupdict().get("p2") \
                or match.groupdict().get("p3")
            dim_ids = tuple(
                did for did, dim in dimensions.items()
                if dim["priority"] == priority
            )
            if not dim_ids:
                raise ContractError(
                    f"[EXPRESSION-SEMANTIC: condition_id={condition_id}: "
                    f"priority '{priority}' matches no dimension]"
                )
        fatal = kind in {"fatal_priority", "fatal_dim"}
        if fatal and any(dimensions[did]["priority"] != "mandatory"
                         for did in dim_ids):
            raise ContractError(
                f"[CONTRACT-INVALID: condition_id={condition_id}: fatal atom "
                "may target mandatory dimensions only]"
            )
        dimension_quantifier = (
            "count2" if kind == "count_priority"
            else "every" if kind in {"every_priority", "every_all"}
            else "any"
        )
        atoms.append(ExpressionAtom(
            dimension_ids=dim_ids,
            dimension_quantifier=dimension_quantifier,
            score=None if fatal else match.groupdict().get("score"),
            or_worse=kind in {
                "count_priority", "any_all", "dim_threshold"
            },
            fatal=fatal,
        ))
    return tuple(atoms)


def quantifier_fires(
    quantifier: str, indicators: list[bool], warnings: list[str]
) -> bool:
    n = len(indicators)
    if n == 0:
        raise ContractError("[DIMENSION-UNASSESSED]")
    k = sum(indicators)
    if quantifier == "any":
        return k >= 1
    if quantifier == "all":
        return k == n
    if quantifier == "majority":
        threshold = 1 if n == 1 else (2 if n == 2 else n // 2 + 1)
        return k >= threshold
    raise ContractError(f"unknown cross_reviewer_quantifier '{quantifier}'")


def _seat_indicator(value: DimensionScore, atom: ExpressionAtom) -> bool:
    if atom.fatal:
        return value.score == "block" and value.block_class == "fatal"
    if atom.or_worse:
        return SCORE_ORDER[value.score] >= SCORE_ORDER[atom.score]
    return value.score == atom.score


def evaluate_expression(
    atoms: tuple[ExpressionAtom, ...],
    assessed: dict[str, list[DimensionScore]],
    cross_quantifier: str,
    warnings: list[str],
) -> bool:
    for atom in atoms:
        dimension_results = []
        for did in atom.dimension_ids:
            values = assessed[did]
            dimension_results.append(quantifier_fires(
                cross_quantifier,
                [_seat_indicator(value, atom) for value in values],
                warnings,
            ))
        if atom.dimension_quantifier == "any":
            result = any(dimension_results)
        elif atom.dimension_quantifier == "every":
            result = all(dimension_results)
        else:
            result = sum(dimension_results) >= 2
        if not result:
            return False
    return True


def accept_grade_action(conditions: list[dict]) -> str:
    for condition in conditions:
        if condition["action"] == "editorial_decision=accept":
            return condition["action"]
    raise ContractError(
        "[CONTRACT-INELIGIBLE: no accept-grade failure condition]"
    )


def resolve_decision(conditions: list[dict], fired_ids: set[str]) -> str:
    fired = [(index, condition) for index, condition in enumerate(conditions)
             if condition["condition_id"] in fired_ids]
    if not fired:
        return accept_grade_action(conditions)
    return max(
        fired, key=lambda pair: (pair[1]["severity"], -pair[0])
    )[1]["action"]


def collect_assessed(
    reports: list[ReviewerReport], contract: dict
) -> dict[str, list[DimensionScore]]:
    assessed: dict[str, list[DimensionScore]] = {}
    for dim in contract["acceptance_dimensions"]:
        did = dim["id"]
        values = [
            report.scores[did]
            for report in reports
            if report.role in dim["eligible_roles"]
            and report.scores[did].score != "not_assessed"
        ]
        if not values:
            raise ContractError(f"[DIMENSION-UNASSESSED: {did}]")
        assessed[did] = values
    return assessed


def compute_dimension_verdicts(
    assessed: dict[str, list[DimensionScore]]
) -> dict[str, str]:
    verdicts: dict[str, str] = {}
    for did, values in assessed.items():
        if any(value.score == "block" and value.block_class == "fatal"
               for value in values):
            verdicts[did] = "block(fatal)"
        else:
            verdicts[did] = max(values, key=lambda value:
                                SCORE_ORDER[value.score]).score
    return verdicts


def recompute_panel(
    reports: list[ReviewerReport],
    contract: dict,
    expressions: dict[str, tuple[ExpressionAtom, ...]],
    warnings: list[str],
):
    assessed = collect_assessed(reports, contract)
    fired: list[str] = []
    for condition in contract["failure_conditions"]:
        if evaluate_expression(
            expressions[condition["condition_id"]],
            assessed,
            condition["cross_reviewer_quantifier"],
            warnings,
        ):
            fired.append(condition["condition_id"])
    decision = resolve_decision(contract["failure_conditions"], set(fired))
    return assessed, fired, decision


# --- Synthesis grammar and DA-CRITICAL gate ------------------------------------

_LIST_BODY = r"(?P<body>[^\]]*)"
_FIRED_LIST_RE = re.compile(r"^fired_conditions: \[" + _LIST_BODY + r"\]\s*$")
_VERDICTS_RE = re.compile(r"^dimension_verdicts: \[" + _LIST_BODY + r"\]\s*$")
_ADJUDICATIONS_RE = re.compile(
    r"^da_critical_adjudications: \[" + _LIST_BODY + r"\]\s*$"
)
_RATIONALE_RE = re.compile(
    r"^(?P<id>C[1-9]\d*) rejection rationale: (?P<text>\S.*)\s*$"
)
_MARKER_RE = re.compile(
    r"^\[DA-CRITICAL-VS-ACCEPT: (?P<count>\d+) "
    r"validated/unresolved\]\s*$"
)


def _one_body(
    lines: list[str], pattern: re.Pattern[str], label: str, path: str
) -> str:
    """Exactly one DISTINCT body for an audit-line grammar.

    Re-statements of an audit line that parse to the SAME stripped body (a
    plain line plus its fenced copy, or a padded inline-span variant of it)
    collapse to one value; the collapse is value-level, not byte-level, by
    design — the candidate list already mixes raw lines with their
    rendering-normalized forms. Two candidates that parse to different
    bodies remain a loud abort, so a decoy that disagrees with the
    operative line can never be silently absorbed (#637).
    """
    bodies = [match.group("body").strip() for line in lines
              if (match := pattern.fullmatch(line))]
    distinct = list(dict.fromkeys(bodies))
    if len(distinct) != 1:
        raise SynthesisError(
            f"[SYNTHESIS-PARSE: {path}: expected exactly one {label} line, "
            f"found {len(distinct)}]"
        )
    return distinct[0]


def _comma_tokens(body: str) -> list[str]:
    return [token.strip() for token in body.split(",") if token.strip()]


def parse_synthesis(path: str, text: str, contract: dict) -> Synthesis:
    # The four mechanical audit lines read from the decoration-tolerant
    # candidate source; rationales and the DA marker stay plain-line-only
    # (see audit_candidate_lines for the declared boundary).
    lines = strip_fences(text)
    audit_lines = audit_candidate_lines(text)
    fired = _comma_tokens(_one_body(
        audit_lines, _FIRED_LIST_RE, "fired_conditions", path
    ))
    condition_ids = {c["condition_id"] for c in contract["failure_conditions"]}
    if len(fired) != len(set(fired)) or set(fired) - condition_ids:
        raise SynthesisError(
            f"[SYNTHESIS-PARSE: {path}: invalid fired_conditions {fired}]"
        )

    verdict_tokens = _comma_tokens(_one_body(
        audit_lines, _VERDICTS_RE, "dimension_verdicts", path
    ))
    verdicts: dict[str, str] = {}
    for token in verdict_tokens:
        match = re.fullmatch(
            r"(?P<dim>D\d+)=(?P<value>pass|warn|block|block\(fatal\))", token
        )
        if not match or match.group("dim") in verdicts:
            raise SynthesisError(
                f"[SYNTHESIS-PARSE: {path}: invalid dimension verdict "
                f"'{token}']"
            )
        verdicts[match.group("dim")] = match.group("value")

    adjudication_tokens = _comma_tokens(_one_body(
        audit_lines, _ADJUDICATIONS_RE, "da_critical_adjudications", path
    ))
    adjudications: dict[str, str] = {}
    for token in adjudication_tokens:
        match = re.fullmatch(
            r"(?P<id>C[1-9]\d*)=(?P<value>VALIDATED|REJECTED|UNRESOLVED)",
            token,
        )
        if not match or match.group("id") in adjudications:
            raise SynthesisError(
                f"[SYNTHESIS-PARSE: {path}: invalid DA adjudication "
                f"'{token}']"
            )
        adjudications[match.group("id")] = match.group("value")

    decisions = list(dict.fromkeys(
        match.group("action") for line in audit_lines
        if (match := _DECISION_RE.fullmatch(line))
    ))
    if len(decisions) != 1 or decisions[0] not in ACTION_ENUM:
        raise SynthesisError(
            f"[SYNTHESIS-PARSE: {path}: expected exactly one valid decision]"
        )
    rationales: dict[str, str] = {}
    for line in lines:
        if match := _RATIONALE_RE.fullmatch(line):
            if match.group("id") in rationales:
                raise SynthesisError(
                    f"[SYNTHESIS-PARSE: {path}: duplicate rejection rationale "
                    f"for {match.group('id')}]"
                )
            rationales[match.group("id")] = match.group("text")
    markers = [int(match.group("count")) for line in lines
               if (match := _MARKER_RE.fullmatch(line))]
    if len(markers) > 1:
        raise SynthesisError(
            f"[SYNTHESIS-PARSE: {path}: duplicate DA consistency marker]"
        )
    return Synthesis(
        fired=fired,
        decision=decisions[0],
        dimension_verdicts=verdicts,
        adjudications=adjudications,
        rejection_rationales=rationales,
        marker_count=markers[0] if markers else None,
    )


def check_da_terminal_gate(
    reports: list[ReviewerReport], synthesis: Synthesis
) -> list[str]:
    da = next((report for report in reports if report.role == "da"), None)
    da_ids = set(parse_da_tables(da.text, da.path)[0]) if da is not None else set()
    adjudicated_ids = set(synthesis.adjudications)
    diagnostics: list[str] = []
    if da_ids != adjudicated_ids:
        diagnostics.append(
            f"[DA-CRITICAL-ADJUDICATION-MISMATCH: report={sorted(da_ids)}, "
            f"synthesis={sorted(adjudicated_ids)}]"
        )
    for finding_id, value in synthesis.adjudications.items():
        if value == "REJECTED" and finding_id not in synthesis.rejection_rationales:
            diagnostics.append(
                f"[DA-CRITICAL-RATIONALE-MISSING: {finding_id}]"
            )
    active = sum(value in {"VALIDATED", "UNRESOLVED"}
                 for value in synthesis.adjudications.values())
    needs_marker = (
        synthesis.decision == "editorial_decision=accept" and active > 0
    )
    if needs_marker and synthesis.marker_count != active:
        diagnostics.append(
            f"[DA-CRITICAL-VS-ACCEPT-MARKER: expected={active}, "
            f"stated={synthesis.marker_count}]"
        )
    if not needs_marker and synthesis.marker_count is not None:
        diagnostics.append(
            "[DA-CRITICAL-VS-ACCEPT-MARKER: marker forbidden in this state]"
        )
    return diagnostics


def layer2_check(
    reports: list[ReviewerReport],
    contract: dict,
    expressions: dict[str, tuple[ExpressionAtom, ...]],
    synthesis: Synthesis,
    warnings: list[str],
) -> list[str]:
    assessed, fired, decision = recompute_panel(
        reports, contract, expressions, warnings
    )
    verdicts = compute_dimension_verdicts(assessed)
    diagnostics: list[str] = []
    if (fired != synthesis.fired or decision != synthesis.decision
            or verdicts != synthesis.dimension_verdicts):
        diagnostics.append(
            f"[PANEL-SYNTHESIS-MISMATCH: recomputed_verdicts={verdicts}, "
            f"declared_verdicts={synthesis.dimension_verdicts}, "
            f"recomputed_fired={fired}, declared_fired={synthesis.fired}, "
            f"recomputed={decision}, stated={synthesis.decision}]"
        )
    diagnostics.extend(check_da_terminal_gate(reports, synthesis))
    return diagnostics


# --- CLI -----------------------------------------------------------------------

def _parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--report", required=True, action="append",
                        type=Path, dest="reports")
    parser.add_argument(
        "--roles",
        help="Comma-separated dispatch roles, positionally matched to reports",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--synthesis", type=Path)
    group.add_argument("--layer1-only", action="store_true")
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)
    warnings: list[str] = []
    infra: list[str] = []
    reviewer_diags: list[str] = []
    synthesis_diags: list[str] = []
    try:
        contract, expressions = load_contract(args.contract)
    except ContractError as exc:
        print(exc)
        return EXIT_CONTRACT

    panel_size = contract["panel_size"]
    resolved = [path.resolve() for path in args.reports]
    if len(set(resolved)) != len(resolved):
        infra.append("[PANEL-CARDINALITY: duplicate report paths]")
    if args.layer1_only:
        if not 1 <= len(args.reports) <= panel_size:
            infra.append(
                f"[PANEL-CARDINALITY: layer1-only accepts 1..{panel_size} "
                f"reports, got={len(args.reports)}]"
            )
    elif len(args.reports) != panel_size:
        infra.append(
            f"[PANEL-CARDINALITY: got={len(args.reports)}, "
            f"panel_size={panel_size}]"
        )

    texts: dict[Path, str] = {}
    digests: set[str] = set()
    seen_paths: set[Path] = set()
    for path in args.reports:
        try:
            texts[path] = _read_text(path)
        except ContractError as exc:
            infra.append(str(exc))
            continue
        resolved_path = path.resolve()
        if resolved_path in seen_paths:
            continue
        seen_paths.add(resolved_path)
        digest = hashlib.sha256(texts[path].encode()).hexdigest()
        if digest in digests:
            infra.append(
                f"[PANEL-CARDINALITY: byte-identical report contents ({path})]"
            )
        digests.add(digest)

    reports: list[ReviewerReport] = []
    for path in args.reports:
        if path not in texts:
            continue
        try:
            reports.append(parse_report(str(path), texts[path], contract))
        except ReportError as exc:
            reviewer_diags.append(str(exc))

    if len(reports) == len(args.reports):
        roles = [report.role for report in reports]
        role_set = ROLE_SETS[contract["mode"]]
        if args.layer1_only:
            if len(set(roles)) != len(roles):
                infra.append(f"[PANEL-CARDINALITY: duplicate roles {roles}]")
        elif set(roles) != role_set or len(set(roles)) != len(roles):
            infra.append(
                f"[PANEL-CARDINALITY: roles {sorted(roles)} != "
                f"required {sorted(role_set)}]"
            )
        if args.roles is not None:
            dispatched = [role.strip() for role in args.roles.split(",")]
            if len(dispatched) != len(reports):
                infra.append(
                    f"[ROLE-BINDING: --roles count={len(dispatched)} does not "
                    f"match reports={len(reports)}]"
                )
            else:
                for index, (expected, report) in enumerate(
                    zip(dispatched, reports)
                ):
                    if expected != report.role:
                        reviewer_diags.append(
                            f"[ROLE-BINDING: report[{index}] declares "
                            f"{report.role}, dispatched as {expected}]"
                        )

    if not args.layer1_only and not infra and not reviewer_diags:
        try:
            synthesis = parse_synthesis(
                str(args.synthesis), _read_text(args.synthesis), contract
            )
            synthesis_diags.extend(layer2_check(
                reports, contract, expressions, synthesis, warnings
            ))
        except ContractError as exc:
            infra.append(str(exc))
        except ReportError as exc:
            reviewer_diags.append(str(exc))
        except SynthesisError as exc:
            synthesis_diags.append(str(exc))

    for diagnostic in warnings + infra + reviewer_diags + synthesis_diags:
        print(diagnostic)
    if infra:
        return EXIT_CONTRACT
    if reviewer_diags:
        return EXIT_REVIEWER
    if synthesis_diags:
        return EXIT_SYNTHESIS
    print("LAYER1-ONLY: PASS" if args.layer1_only else "PANEL-SYNTHESIS: PASS")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
