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
import unicodedata
from collections import Counter
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
_DISSENT_FIELD_NAMES = frozenset({"dimensionid", "rationale"})
_MARKUP_SPAN_RE = re.compile(
    r"<[^>]*>|\]\((?:[^()]|\([^()]*\))*\)|\]\[[^\]]*\]|\[[ xX]?\]"
)
# A block opener, including one behind list or blockquote markers: rendered
# through CommonMark, `- <!--` opens raw HTML just as a bare `<!--` does, and
# needs no closer to swallow the rest of the item. The indentation allowances
# must not add up to four, which would make the whole line indented code: a
# list marker takes one to four following spaces before its content, a block
# quote at most one, and a block start may still be indented up to three
# inside the quote it opens. Erring narrow costs a miss; erring wide aborts a
# valid card. Only an ordered list beginning at 1 may interrupt an open
# paragraph, so `2. <!--` under a paragraph line is text, not a list opening
# a raw-HTML block, and the fields below it stay on the page.
def _container_prefix(ordered: str) -> str:
    """Matched against a tab-expanded line, so spaces are the only gap.

    Every gap is one unambiguous run: letting a single space be claimed by
    either of two adjacent optional groups gave two ways to match each marker
    and doubled the work per nesting level, so a short nested quote stalled
    the checker rather than returning a verdict.
    """
    return rf"(?:(?:[-*+]|{ordered}) {{1,4}}|> {{0,4}})*"


# Lines that end the paragraph above them, so the NEXT line sits at a real
# block start where any ordered marker may open a list. An ATX heading of any
# level, a thematic break, and a lone `-` do that from either state, the last
# because it reads as a setext underline under a paragraph and as an empty
# list item without one. A bare `>` starts a container rather than closing a
# paragraph and is left to #613 with the rest of the container family.
_CLOSES_PARAGRAPH_RE = re.compile(
    r"^ {0,3}(?:"
    r"#{1,6}(?:[ \t].*)?$"
    r"|(?:\*[ \t]*){3,}$|(?:_[ \t]*){3,}$|(?:-[ \t]*){3,}$"
    r"|-[ \t]*$"
    r")"
)
# A `=` run or two-or-more hyphens underlines a paragraph, so it closes one
# only when there is a paragraph to underline; with none, it is ordinary
# paragraph text and OPENS one.
_SETEXT_UNDERLINE_RE = re.compile(r"^ {0,3}(?:=+|-{2,})[ \t]*$")
# An empty list item has a blank first line, so it cannot interrupt an open
# paragraph. It only holds the state down where none is open. Reading every
# lone marker as a closer looked symmetrical and aborted valid cards.
_EMPTY_LIST_ITEM_RE = re.compile(r"^ {0,3}(?:[*+]|\d{1,9}[.)])[ \t]*$")
_ANY_ORDERED_MARKER = r"\d{1,9}[.)]"
_PARAGRAPH_INTERRUPTING_MARKER = r"1[.)]"
_COMMENT_OPENER_RE = re.compile(
    rf"^ {{0,3}}{_container_prefix(_ANY_ORDERED_MARKER)}<!--"
)
_PARAGRAPH_OPENER_RE = re.compile(
    rf"^ {{0,3}}{_container_prefix(_PARAGRAPH_INTERRUPTING_MARKER)}<!--"
)


class ConformanceError(Exception):
    """Reviewer conformance failure -> exit 3."""


@dataclass
class PhaseOnePlan:
    commitments: dict[str, dict[str, str]]
    warnings: list[str]


@dataclass
class DissentSpan:
    """The dissent section as written: every line, plus the commented ones.

    `strip_fences` leaves HTML comments in place, so a canonical field inside
    `<!-- ... -->` otherwise parses as a real dissent and collects the
    trigger-binding exemption while the visible card claims nothing.
    """

    lines: list[str]
    hidden_by_comment: list[str]


@dataclass
class DissentParse:
    dimensions: set[str]
    diagnostics: list[str]


def _normalise(text: str) -> str:
    return " ".join(text.casefold().split())


def _is_dissent_field_shaped(line: str) -> bool:
    """True when a line spells a dissent field, canonically or decorated.

    Decoration-agnostic by construction: a line is field-shaped when the
    letters preceding its first colon spell exactly a field name, whatever
    non-letters surround them. Enumerating Markdown wrappers instead would
    leave the next unenumerated wrapper (task item, table cell, link label)
    reading as prose. Folded first so a fullwidth re-spelling cannot pass.

    Markup spans carrying letters of their own (HTML tags, reference targets,
    task-list markers, and link destinations up to one nesting level deep) are
    dropped BEFORE the colon is located, not after: an absolute link target
    carries its own `https:` and would otherwise win the partition.

    Decoration beyond those — a deeper nested destination, a quoted HTML
    attribute containing `>`, exotic custom syntax — is deliberately out of
    scope, because absorbing it costs one advisory-flagged record while a
    broader rule costs false aborts, which is the failure this tolerance
    exists to remove. `test_a_nested_paren_link_destination_is_a_declared_
    limit` pins that boundary so it cannot move by accident.

    `str.isalpha` keeps every script's letters, so CJK prose that happens to
    name a field stays prose rather than collapsing onto the field name and
    aborting a panel it should tolerate.
    """
    stripped = _MARKUP_SPAN_RE.sub(
        "", unicodedata.normalize("NFKC", line).casefold()
    )
    head, separator, _ = stripped.partition(":")
    label = "".join(char for char in head if char.isalpha())
    return bool(separator) and label in _DISSENT_FIELD_NAMES


def _lines_with_fence_state(text: str):
    """Yield every line with whether it sits inside a fenced block.

    Mirrors the fence bookkeeping of `panel.strip_fences`, which drops those
    lines rather than reporting them. The dissent scan needs both facts: the
    content, so a fenced field cannot hide, and the state, so a fenced heading
    is not mistaken for a section boundary.
    """
    fence_char, fence_len = None, 0
    for line in panel._COMMONMARK_LINE_END_RE.split(text):
        if fence_char is not None:
            if match := panel._FENCE_CLOSE_RE.fullmatch(line):
                token = match.group("fence")
                if token[0] == fence_char and len(token) >= fence_len:
                    fence_char, fence_len = None, 0
                    continue
            yield line, True
            continue
        if match := panel._FENCE_OPEN_RE.fullmatch(line):
            token, info = match.group("fence"), match.group("info")
            if token[0] != "`" or "`" not in info:
                fence_char, fence_len = token[0], len(token)
                continue
        yield line, False


def _opens_comment(line: str, *, paragraph_open: bool) -> bool:
    """Whether the line starts an HTML comment at a block position.

    Tabs are measured to the next four-column stop rather than counted as one
    character, the way CommonMark reads them wherever indentation defines
    block structure. Counting characters put `> \\t<!--` (column four, a live
    comment) and `  - \\t<!--` (column eight, indented code) on the wrong
    sides of the boundary in opposite directions.

    With a paragraph open, an ordered marker other than 1 cannot start a list,
    so it cannot open a comment either.
    """
    pattern = _PARAGRAPH_OPENER_RE if paragraph_open else _COMMENT_OPENER_RE
    return bool(pattern.match(line.expandtabs(4)))


def _comment_state_after(
    line: str, *, commented: bool, paragraph_open: bool = False
) -> bool:
    """Whether the line ends inside an HTML comment.

    Resolved by delimiter ORDER, not by presence: `<!-- a --> <!--` closes
    and reopens on one line, and reading that as closed credited a comment
    carrying canonical fields as a real dissent. Only a block opener starts
    one, list and blockquote markers included, so a marker discussed mid-line
    is still not a comment; once a line has opened one, its later delimiters
    are that same block's raw HTML.

    The closer may reuse the opener's own last two dashes, which is how
    CommonMark closes `<!-->` and `<!--->`. Ordering the scan without that
    overlap would read them as unterminated and abort a card that presence-
    testing for a closer had passed.
    """
    index = 0
    if not commented:
        if not _opens_comment(line, paragraph_open=paragraph_open):
            return False
        # Located in the ORIGINAL line: the prefix carries no `<!--`, so the
        # first occurrence is the opener wherever tab expansion moved it.
        commented, index = True, line.find("<!--") + 2
    while True:
        token = "-->" if commented else "<!--"
        position = line.find(token, index)
        if position < 0:
            return commented
        commented, index = not commented, position + len(token)


def _raw_dissent_span(text: str) -> DissentSpan:
    """Dissent-section lines as written, before any sanitizer runs.

    Comment delimiters are opened up rather than dropped, so a field inside an
    HTML comment is scanned instead of vanishing with the comment. A
    field-shaped H2 immediately inside the span rides along, because a field
    spelled as its own `## dimension_id: D1` heading leaves the section body
    empty and would otherwise be invisible; a field-shaped heading anywhere
    else is an ordinary extra section, which the report grammar permits.

    Only an unfenced heading delimits the span, so a heading written inside a
    fenced block cannot end it early and hide the fields that follow — not
    even one repeating a title that exists structurally elsewhere. A COMMENTED
    heading still delimits, agreeing with `split_sections` rather than second-
    guessing it: disagreeing cost four false aborts across review rounds and
    bought only a miss that credits the seat nothing, while agreeing keeps a
    comment opened above the heading from laundering the fields below it.
    """
    span, hidden_by_comment, inside, commented = [], [], False, False
    paragraph_open = False
    for line, fenced in _lines_with_fence_state(text):
        entered_commented = commented
        opens_comment = not fenced and _opens_comment(
            line, paragraph_open=paragraph_open
        )
        if not fenced:
            # A block opener only, list and blockquote markers included:
            # four columns STARTING a block makes indented code, and a fence
            # makes every marker inert. Not read as an opener: a marker
            # mid-line, one in an inline-code span, or one indented as a lazy
            # paragraph continuation. The first and last of those DO form a
            # comment, so that miss is not free: it grants a trigger-binding
            # exemption for a dissent the page does not show. Refused anyway,
            # because closing it means reading a bare `<!--` inside
            # unrestricted `rationale:` text as an opener, aborting a valid
            # card on an unretryable phase; the deterministic closure belongs
            # in the output grammar (#613), not here. Both are pinned as
            # tests, and #613 also carries the wider hiding channel this
            # visibility model does not cover at all: raw HTML that is not a
            # comment, such as a `<script>` or `<template>` block.
            commented = _comment_state_after(
                line, commented=commented, paragraph_open=paragraph_open
            )
        if not fenced and (match := panel._H2_RE.fullmatch(line)):
            title = match.group(1)
            if inside and _is_dissent_field_shaped(title):
                span.append(title)
            else:
                inside = title == "Scoring Plan Dissent"
            paragraph_open = False
            continue
        # CommonMark counts only spaces and tabs as blank, so a line holding
        # an ideographic space is a paragraph. Calling it blank put the next
        # line at a block start and aborted a valid zh-TW card.
        expanded = line.expandtabs(4)
        state_dependent = (
            _SETEXT_UNDERLINE_RE if paragraph_open else _EMPTY_LIST_ITEM_RE
        )
        closes_paragraph = bool(
            _CLOSES_PARAGRAPH_RE.match(expanded)
            or state_dependent.match(expanded)
        )
        paragraph_open = (
            not fenced
            and bool(line.strip(" \t"))
            and not closes_paragraph
            # A recognized comment block is raw HTML, never a paragraph, so
            # the line after one is at a block start again. Recording its own
            # lines as an open paragraph read the next `2. <!--` with the
            # restricted pattern and credited the fields it hides.
            and not (entered_commented or opens_comment)
        )
        if inside:
            # Opened up only where a comment actually is. Rewriting every line
            # carrying the tokens would break a canonical `rationale:` that
            # merely mentions them (its text is unrestricted) from matching
            # the canonical parse, aborting an unretryable Phase 2 on a
            # valid card.
            if entered_commented or opens_comment:
                span.append(line.replace("<!--", " ").replace("-->", " "))
            else:
                span.append(line)
            if entered_commented:
                hidden_by_comment.append(line)
    return DissentSpan(span, hidden_by_comment)


def _empty_dissent_section_diagnostic(raw_span: list[str]) -> str:
    """Counted on the raw span: fenced prose is archived content too."""
    non_blank = sum(1 for line in raw_span if line.strip())
    return (
        "[DISSENT-EMPTY-SECTION: ## Scoring Plan Dissent spells no dissent "
        "field; read as no dissent, with full Phase 1 trigger binding "
        f"enforced on every dimension; {non_blank} non-blank line(s) present "
        "— read the archived response if any narrate a deviation]"
    )


def _one_field(
    lines: list[str],
    field: str,
    path: str,
    *,
    required: bool,
    dimension_id: str,
) -> str | None:
    hits = [match.group("value") for line in lines
            if (match := _FIELD_PATTERNS[field].fullmatch(line))]
    expected = "exactly one" if required else "at most one"
    if (required and len(hits) != 1) or (not required and len(hits) > 1):
        raise ConformanceError(
            f"[PHASE1-GRAMMAR: {path}: expected {expected} canonical "
            f"{field}: line for dimension {dimension_id}, found {len(hits)}]"
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
            f"[PHASE1-GRAMMAR: {path}: duplicate scoring-plan subsection: "
            f"{', '.join(sorted(subsection_dupes))}]"
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
            field: _one_field(
                sublines,
                field,
                path,
                required=True,
                dimension_id=did,
            )
            for field in (
                "dimension_id", "what_to_look_for",
                "what_triggers_block", "what_triggers_warn",
            )
        }
        mandatory = dimensions[did]["priority"] == "mandatory"
        fields["what_triggers_fatal"] = _one_field(
            sublines,
            "what_triggers_fatal",
            path,
            required=mandatory,
            dimension_id=did,
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


def parse_dissent_dimensions(text: str) -> DissentParse:
    lines = panel.strip_fences(text)
    sections, dupes = panel.split_sections(lines)
    if "Scoring Plan Dissent" in dupes:
        raise ConformanceError(
            "[DISSENT-GRAMMAR: duplicate ## Scoring Plan Dissent]"
        )
    if "Scoring Plan Dissent" not in sections:
        return DissentParse(set(), [])
    body = sections["Scoring Plan Dissent"]
    span = _raw_dissent_span(text)
    raw_span = span.lines
    # A commented-out field is not a claim the seat made, so it is struck from
    # the canonical parse and left to fail below as an unparsed occurrence.
    outstanding = Counter(span.hidden_by_comment)
    visible = []
    for line in body:
        if outstanding.get(line):
            outstanding[line] -= 1
            continue
        visible.append(line)
    parsed = Counter(
        line for line in visible
        if _DISSENT_DIM_RE.fullmatch(line)
        or _DISSENT_RATIONALE_RE.fullmatch(line)
    )
    dims = [match.group("dim") for line in visible
            if (match := _DISSENT_DIM_RE.fullmatch(line))]
    rationales = [
        match.group("text") for line in visible
        if (match := _DISSENT_RATIONALE_RE.fullmatch(line))
    ]
    # Scanned on the RAW span, not the sanitized body: a field the sanitizers
    # delete (fence, comment) or relocate (its own H2) would otherwise reach
    # the tolerance branch as an empty section. A field line the canonical
    # parse never saw is a dissent this seat cannot be credited with, so it
    # fails whether or not it is canonically spelled. Counted rather than
    # matched by value, so a hidden copy of a canonical field is still one
    # unparsed occurrence and cannot ride in on its twin's identity.
    hidden = Counter(
        candidate for candidate in raw_span
        if _is_dissent_field_shaped(candidate)
    )
    if any(count > parsed[value] for value, count in hidden.items()) or any(
        _is_dissent_field_shaped(candidate) and candidate not in parsed
        for candidate in visible
    ):
        raise ConformanceError(
            "[DISSENT-GRAMMAR: dissent fields must be canonical unbulleted "
            "dimension_id: and rationale: lines]"
        )
    if not dims and not rationales:
        # A section that spells no dissent field carries the same information
        # as an absent section, so it is read as no dissent instead of
        # aborting an unretryable Phase 2. The occurrence stays auditable in
        # the run record, and full Phase 1 trigger binding still applies to
        # every dimension.
        return DissentParse(
            set(), [_empty_dissent_section_diagnostic(raw_span)]
        )
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
    if not dims:
        raise ConformanceError(
            "[DISSENT-GRAMMAR: dissent section must name dimension_id]"
        )
    if len(dims) != len(set(dims)):
        raise ConformanceError("[DISSENT-GRAMMAR: duplicate dimension_id]")
    if len(rationales) != len(dims):
        raise ConformanceError(
            "[DISSENT-GRAMMAR: each dissent requires one rationale: line]"
        )
    return DissentParse(set(dims), [])


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
        for diagnostic in dissent.diagnostics:
            print(diagnostic)
        dimensions = {
            dim["id"]: dim for dim in contract["acceptance_dimensions"]
        }
        check_trigger_binding(report, plan, dimensions, dissent.dimensions)
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
