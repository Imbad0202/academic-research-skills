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
import html
import json
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_panel_synthesis as panel  # noqa: E402
import recompute_receipts as recompute  # noqa: E402

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
# --- #610 methodology arithmetic-receipt grammar -------------------------
# Receipt machine lines are lowercase snake_case on purpose: they can never
# collide with the finding grammar's bold `**Severity**:` / `**Evidence
# Anchor**:` declarations, so the receipt section cannot trip the
# outside-Review-Body severity gate and a finding cannot satisfy a receipt
# field. Decoration tolerance is bounded to the two shapes the finding
# grammar already accepts (one leading list marker, bold around the key).
# The section is read fence-transparently (#637/#638 display-form
# discipline): a fenced receipt line is still content, so a stylistic fence
# neither hides a receipt nor turns one into a false abort, and any other
# decoration of a field-shaped line is detected and aborts loudly instead of
# silently passing a forbidden-field guard or failing a required count.
_RECEIPT_SECTION = "Arithmetic Receipts"
_RECEIPT_H3_RE = re.compile(r"^AR[1-9]\d*$")
_RECEIPT_PROCEDURES = frozenset(
    {"p_from_test_statistic", "grim", "grimmer", "n_from_df"}
)
_RECEIPT_STATUSES = frozenset(
    {"consistent", "mismatch", "not_computable", "not_applicable"}
)
_NOT_COMPUTABLE_REASONS = frozenset({
    "missing_reported_value",
    "test_family_ambiguous",
    "tail_ambiguous",
    "nonstandard_p_procedure",
    "inequality_unresolvable",
    "rounding_rule_ambiguous",
    "rounding_boundary_ambiguous",
    "scale_granularity_unknown",
    "scale_support_unknown",
    "analytic_n_ambiguous",
    "aggregation_or_weighting_unknown",
    "sd_convention_unknown",
    "mean_grim_inconsistent",
    "df_identity_ambiguous",
    "model_correction_or_pooling",
    "reachability_not_completed",
})
_TAIL_CONVENTIONS = frozenset(
    {"two-tailed", "one-tailed", "upper-tail", "unstated"}
)


def _receipt_field_re(key: str) -> re.Pattern[str]:
    # Bold is balanced-or-absent: a half-bold `**key:` is a decorated line
    # for the shape guard to abort, never a canonical field (#610 round-2).
    return re.compile(
        rf"^(?:[-*] )?(?:{key}|\*\*{key}\*\*): (?P<value>\S.*?)\s*$"
    )


_RECEIPT_FIELD_RES = {
    key: _receipt_field_re(key)
    for key in (
        "procedure_id",
        "evidence_anchor",
        "reported_inputs",
        "assumptions",
        "derivation",
        "derived_value_or_range",
        "comparison_rule",
        "status",
        "not_computable_reason",
        "finding_ref",
        "tail_convention",
        "rounding_interval",
        "nearest_achievable",
        "df_identity",
    )
}
_RECEIPT_ATTESTATION_RE = _receipt_field_re("no_recomputable_statistics")
_RECEIPT_ATTESTATION_ADVISORY = (
    "[RECEIPT-ATTESTATION: declaration-only — applicability not "
    "machine-verified; adjudication judges the attestation]"
)
# Folded field-name alphabets for the decoration-agnostic shape test, the
# same construction as `_is_dissent_field_shaped`: a line is receipt-field-
# shaped when the letters before its first colon spell a field name after
# markup-span strip + NFKC fold. A shaped line that the canonical grammar
# does not parse is a loud abort, never a silently ignored decoration.
_RECEIPT_FIELD_SHAPE_NAMES = frozenset(
    "".join(char for char in key if char.isalpha())
    for key in (*_RECEIPT_FIELD_RES, "no_recomputable_statistics")
)
_FINDING_REF_VALUE_RE = re.compile(r"^W[1-9]\d*$")
# The back-reference value is exact: `AR<n>` up to end-of-line or the next
# table pipe. `AR1, AR2` and trailing prose fail this parse and then abort
# via the lenient declaration count below rather than half-reading `AR1`.
_RECEIPT_BACKREF_RE = re.compile(
    r"(?:^|\|\s*)\s*(?:[-*]\s*)?\*\*Arithmetic Receipt\*\*:\s*"
    r"(?P<value>AR[1-9]\d*)\s*(?=\||$)"
)
# Lenient declaration shape for the back-reference, checked against the
# canonical parse per line (`_is_dissent_field_shaped` construction): a line
# whose letters before the first colon spell exactly `arithmeticreceipt` is
# a declaration the seat made, so a decorated, fenced, or prose-trailed
# back-reference the canonical regex refuses aborts instead of vanishing.
# Prose that merely mentions the section (`the Arithmetic Receipts
# section: ...`) carries extra letters in its head and stays prose.
_RECEIPT_BACKREF_SHAPE_NAME = "arithmeticreceipt"
# Both-tails value rule (#610 rounds 1-2): under an unstated tail, each tail
# label must share its own `;`-delimited segment of `derived_value_or_range`
# with a digit — either side of the label, so `p = .192 (two-tailed)` is a
# shown value while a bare label in a digitless segment is not. Hyphen
# variants (space, ASCII hyphen, U+2010-U+2015) are folded into the label
# match, the value text is NFKC-folded first, and the label needs letter
# boundaries so `notwo-tailed` prose cannot satisfy the rule; a fused
# `twotailed` typo still counts as the label — it carries its value, and
# rejecting it would be a false abort on an unretryable phase.
_TAIL_LABEL_RES = {
    label: re.compile(rf"(?<![a-z]){label}[\s‐-―-]?tailed(?![a-z])")
    for label in ("two", "one")
}
# Conditional-field matrix, spec §4/§5 (2026-08-02 #610 spec): which
# procedure-specific lines each procedure may carry. `tail_convention` is
# required on every p_from_test_statistic receipt (what the paper states is
# always statable — `unstated` exists for exactly that case); the completed-
# procedure fields (`rounding_interval`, `nearest_achievable`, `df_identity`)
# are required only under a verdict status, because `not_computable` may
# legitimately stop before the field can exist, and remain permitted there
# for a partial attempt that stopped late.
_RECEIPT_VERDICT_STATUSES = frozenset({"consistent", "mismatch"})
_PROCEDURE_FIELDS = {
    "p_from_test_statistic": ("tail_convention",),
    "grim": ("rounding_interval", "nearest_achievable"),
    "grimmer": ("rounding_interval", "nearest_achievable"),
    "n_from_df": ("df_identity",),
}
# Inverted view driving the conditional-field loop, so the matrix above is
# the single authority: field -> the procedures that carry it.
_PROCEDURE_FIELD_OWNERS = {
    field: tuple(
        procedure
        for procedure, fields in _PROCEDURE_FIELDS.items()
        if field in fields
    )
    for fields in _PROCEDURE_FIELDS.values()
    for field in fields
}
_ALWAYS_REQUIRED_PROCEDURE_FIELDS = frozenset({"tail_convention"})
# --- end #610 receipt grammar --------------------------------------------
_DISSENT_FIELD_NAMES = frozenset({"dimensionid", "rationale"})
_MARKUP_SPAN_RE = re.compile(
    r"<[^>]*>|\]\((?:[^()]|\([^()]*\))*\)|\]\[[^\]]*\]|\[[ xX]?\]"
)
# Non-comment raw HTML is forbidden only inside the dissent span (#682).
# Match the opening delimiter rather than requiring a complete tag: CommonMark
# raw blocks such as a line ending in ``<script`` can still hide the canonical
# fields below it, and a malformed claimed dissent must abort rather than fall
# through to the empty-section advisory.  Autolinks such as
# ``<https://example.test>`` do not match because ``:`` is not a tag-name
# boundary.  Comment delimiters remain owned by the #613 state machine so its
# more specific ``[DISSENT-HIDDEN]`` diagnostic keeps precedence.
_DISSENT_RAW_HTML_RE = re.compile(
    r"<(?:(?:/?[A-Za-z][A-Za-z0-9-]*)(?=[\s/>]|$)|![A-Za-z]|!\[CDATA\[|\?)",
    re.IGNORECASE,
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
    raw_html: list[str]


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


def _display_fold(line: str) -> str:
    """Unescape HTML entities FIRST, then NFKC-fold and casefold.

    Order matters (#610 round-3 P1): a fullwidth-colon entity `&#xFF1A;`
    decodes to a fullwidth colon that only the SUBSEQUENT NFKC fold maps to
    `:`, so folding before unescaping left the decoded colon unfolded and
    the declaration unseen. A doubly-encoded or fullwidth-ampersand entity
    stays literal, which matches what the renderer shows.
    """
    return unicodedata.normalize("NFKC", html.unescape(line)).casefold()


_ESCAPED_PIPE_RE = re.compile(r"\\\|")
# CommonMark §2.4: a backslash escapes the next punctuation character, so
# `\\` is a literal backslash and ``\` `` a literal backtick that can
# neither open nor close a code span. One left-to-right pass sequences the
# two correctly (`\\` consumes its backslash before a following backtick is
# considered). Ignoring this let an escaped-backtick "span" blank a live
# `<!--` and credit a hidden dissent field (#613 security round 1, P1).
_ESCAPED_BACKTICK_RE = re.compile(r"\\[\\`]")


def _blank_code_spans(line: str) -> str:
    """Blank CommonMark inline code spans, matching runs of EQUAL length.

    A regex accepting unequal delimiter runs (#610 round-4 P1) blanked
    from a single-backtick opener to a double-backtick closer — a stretch
    the renderer does NOT treat as code, re-opening the later-cell attack
    — and conversely swallowed legitimate prose. This scanner pairs an
    opening run only with the next run of exactly its length, as the
    renderer does; an unmatched run stays literal. Backslash-escaped
    backticks are blanked FIRST: they are literal to the renderer and must
    not participate in pairing.
    """
    line = _ESCAPED_BACKTICK_RE.sub("  ", line)
    out: list[str] = []
    index, length = 0, len(line)
    while index < length:
        if line[index] != "`":
            out.append(line[index])
            index += 1
            continue
        run_end = index
        while run_end < length and line[run_end] == "`":
            run_end += 1
        run = run_end - index
        scan, close = run_end, -1
        while scan < length:
            if line[scan] != "`":
                scan += 1
                continue
            candidate_end = scan
            while candidate_end < length and line[candidate_end] == "`":
                candidate_end += 1
            if candidate_end - scan == run:
                close = scan
                break
            scan = candidate_end
        if close >= 0:
            out.append(" " * (close + run - index))
            index = close + run
        else:
            out.append(line[index:run_end])
            index = run_end
    return "".join(out)


def _cell_split_form(line: str) -> str:
    """The line with pipe-bearing non-cell constructs blanked for splitting.

    A naive `split("|")` read the pipe inside a Markdown link destination,
    an escaped `\\|`, or an inline code span as a GFM cell boundary and
    minted a phantom field-shaped cell out of legitimate prose — a false
    abort on an unretryable phase (#610 round-3). Those spans are literal
    or non-tabular to the renderer, so they are blanked before the split;
    the whole-line candidate is always tested unmodified.
    """
    blanked = _MARKUP_SPAN_RE.sub(" ", line)
    blanked = _blank_code_spans(blanked)
    return _ESCAPED_PIPE_RE.sub(" ", blanked)


def _is_receipt_field_shaped(line: str) -> bool:
    """True when a line spells a receipt machine field, however decorated.

    Same construction as `_is_dissent_field_shaped` (#610 round-1 fix 4):
    markup spans are stripped, the line is NFKC-folded and HTML-unescaped
    (an entity colon `&#58;` renders as a colon and must read as one), and
    the letters before the first colon must spell exactly a receipt field
    name. An unenumerated decoration — `**status:** mismatch`, a table
    cell, an indented, ordered, or blockquoted marker — is therefore a
    declaration the seat made, and a shaped line the canonical grammar
    refuses aborts loudly instead of silently passing a forbidden-field
    guard or starving a required-field count.
    """
    stripped = _MARKUP_SPAN_RE.sub("", _display_fold(line))
    head, separator, _ = stripped.partition(":")
    label = "".join(char for char in head if char.isalpha())
    return bool(separator) and label in _RECEIPT_FIELD_SHAPE_NAMES


def _receipt_shape_candidates(line: str) -> list[str]:
    """The line plus, when it carries pipes, each `|`-delimited cell.

    The head-of-line shape test alone lets a machine declaration hide in a
    LATER table cell (`| note | **tail_convention:** two-tailed |`), where
    the head letters of the whole line spell nothing (#610 round-2). Cells
    are scanned only when the line does not canonically parse, so a
    canonical field whose free-text value happens to contain a pipe is
    never re-partitioned against itself.
    """
    if "|" not in line:
        return [line]
    return [line, *_cell_split_form(line).split("|")]


def _tail_value_shown(derived_fold: str, label_re: re.Pattern[str]) -> bool:
    """Whether a tail label shares a `;`-delimited segment with a digit.

    Segments are the `;`-delimited pieces of the (NFKC-folded, casefolded)
    `derived_value_or_range` value: a bare label whose number sits in some
    other segment — or nowhere — is a label, not a shown value, and cannot
    satisfy the both-tails display rule. Digit-adjacency is direction-free
    within the segment (`two-tailed p ≈ .192` and `p = .192 (two-tailed)`
    both show the value); the one-pass any() also keeps the scan linear.
    """
    return any(
        label_re.search(segment)
        and any(char.isdigit() for char in segment)
        for segment in derived_fold.split(";")
    )


def _is_backref_shaped(line: str) -> bool:
    """True when a line spells the `**Arithmetic Receipt**:` field, however
    decorated — the same head shape test as the receipt fields."""
    stripped = _MARKUP_SPAN_RE.sub("", _display_fold(line))
    head, separator, _ = stripped.partition(":")
    label = "".join(char for char in head if char.isalpha())
    return bool(separator) and label == _RECEIPT_BACKREF_SHAPE_NAME


def _strip_inline_comment_spans(
    line: str, open_: bool
) -> tuple[str, list[str], bool]:
    """(rendered remainder, hidden segments, state) for inline spans.

    The block visibility model deliberately refuses to read a mid-paragraph
    `prose <!--` as an opener (see `_raw_dissent_span`), but CommonMark
    treats it as raw inline HTML whose comment hides everything until
    `-->`. The Review Body backref walk therefore strips those spans and
    parses only what the renderer shows (#610 rounds 3-5): content after
    the opener on the SAME line is stripped too, and content after a
    closing `-->` on the same line is kept and parsed — so a hidden
    back-reference is never credited and a rendered one is never dropped.
    The hidden segments are returned as well, because a declaration inside
    a span must abort even when the line also carries visible content —
    silently dropping it re-opened the hidden-declaration channel one
    partial-visibility case at a time (#610 round-5). They stay one entry
    PER SPAN, never joined (#610 round-6): joining let a prose span prefix
    shield a declaration in the next span, and conversely synthesized a
    phantom declaration out of harmless fragments. Callers pass a
    code-span-blanked line, matching the renderer's precedence of code
    spans over raw HTML.
    """
    visible_parts: list[str] = []
    hidden_segments: list[str] = []
    index, state = 0, open_
    while True:
        token = "-->" if state else "<!--"
        position = line.find(token, index)
        if position < 0:
            if state:
                hidden_segments.append(line[index:])
            else:
                visible_parts.append(line[index:])
            return "".join(visible_parts), hidden_segments, state
        if state:
            hidden_segments.append(line[index:position])
        else:
            visible_parts.append(line[index:position])
        state, index = not state, position + len(token)


def _backref_declared_count(line: str) -> int:
    """Back-reference declarations on the line, counted per table cell.

    Counting the whole line once let a malformed second declaration ride
    beside a canonical one (`… AR1 | **Arithmetic Receipt:** see AR2`) —
    the canonical parse found a match, the shape test never ran, and the
    visible second declaration vanished (#610 round-2). Cells are the
    declaration slots the canonical regex itself recognises (its
    start-or-pipe prefix), so declared-vs-parsed equality is exact.
    """
    if "|" not in line:
        return 1 if _is_backref_shaped(line) else 0
    return sum(
        1 for cell in _cell_split_form(line).split("|")
        if _is_backref_shaped(cell)
    )


def _lines_with_fence_state(text: str):
    """Yield every line with whether it sits inside a fenced block.

    Mirrors the fence bookkeeping of `panel.strip_fences`, which drops those
    lines rather than reporting them. The dissent scan needs both facts: the
    content, so a fenced field cannot hide, and the state, so a fenced heading
    is not mistaken for a section boundary.

    Fenced lines are yielded in DISPLAY form: CommonMark strips up to the
    opener's indentation from every content line of an indented fence, so a
    consumer reading fenced content (the receipt gate) sees what the page
    shows rather than false-aborting on the indent (#610 round-2).
    """
    fence_char, fence_len, fence_indent = None, 0, 0
    for line in panel._COMMONMARK_LINE_END_RE.split(text):
        if fence_char is not None:
            if match := panel._FENCE_CLOSE_RE.fullmatch(line):
                token = match.group("fence")
                if token[0] == fence_char and len(token) >= fence_len:
                    fence_char, fence_len, fence_indent = None, 0, 0
                    continue
            leading = len(line) - len(line.lstrip(" "))
            yield line[min(fence_indent, leading):], True
            continue
        if match := panel._FENCE_OPEN_RE.fullmatch(line):
            token, info = match.group("fence"), match.group("info")
            if token[0] != "`" or "`" not in info:
                fence_char, fence_len = token[0], len(token)
                fence_indent = len(line) - len(line.lstrip(" "))
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


def _inline_comment_state_after(line: str, *, commented: bool) -> bool:
    """Delimiter-order comment state with NO block-position requirement.

    Span-scoped (#613): inside the dissent span the output grammar makes a
    bare ``<!--`` out-of-grammar prose — the delivered Phase 2 prompts and
    the protocol now require inline code for any mention — so every
    occurrence is an opener, including the two CommonMark shapes the block
    visibility model deliberately does not read (a marker following text on
    its own line; a marker indented as a lazy paragraph continuation).
    Callers blank code spans first, so the sanctioned inline-code mention
    never opens.
    """
    index = 0
    while True:
        token = "-->" if commented else "<!--"
        position = line.find(token, index)
        if position < 0:
            return commented
        commented = not commented
        # After an opener, resume at +2 rather than +4: the closer may
        # reuse the opener's own last two dashes (`<!-->`, `<!--->`) —
        # the same overlap rule the block scanner applies (codex #650
        # round 1, P2: skipping it left the empty comment "open" and
        # false-aborted the rendered fields below it).
        index = position + (2 if commented else len(token))


def _lines_with_hidden_state(text: str):
    """Yield (line, fenced, hidden): fence plus HTML-comment visibility.

    The comment and paragraph bookkeeping mirror `_raw_dissent_span` line
    for line, so the receipt gate and the dissent gate share one visibility
    model (#610 round-2, both tracks): `hidden` is True when the line sits
    inside — or itself opens — an HTML comment at a block position, i.e.
    when a CommonMark renderer would not display it. `code_indented` is
    True when the line starts an indented code block (four columns at a
    block position, no paragraph open), i.e. when the renderer shows it as
    literal text rather than a field line (#610 round-3). Fence state is
    layered first, exactly as in `_raw_dissent_span`: a comment marker
    inside a fence is literal text and advances no comment state.
    """
    commented = False
    paragraph_open = False
    for line, fenced in _lines_with_fence_state(text):
        entered_commented = commented
        opens_comment = not fenced and _opens_comment(
            line, paragraph_open=paragraph_open
        )
        if not fenced:
            commented = _comment_state_after(
                line, commented=commented, paragraph_open=paragraph_open
            )
        expanded = line.expandtabs(4)
        code_indented = (
            not fenced
            and not paragraph_open
            and bool(line.strip(" \t"))
            and expanded.startswith("    ")
        )
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
            and not (entered_commented or opens_comment)
            # An indented-code line is literal, never a paragraph: letting
            # it open one made the NEXT code line read as a live paragraph
            # continuation and earn credit the renderer does not show
            # (#610 round-4).
            and not code_indented
        )
        yield line, fenced, entered_commented or opens_comment, code_indented


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
    span, hidden_by_comment, raw_html = [], [], []
    inside, commented = False, False
    paragraph_open = False
    # #613: span-scoped inline comment state. Outside the span, only a
    # block-position opener counts (the #612 model, unchanged, because
    # prose there may legitimately mention a bare marker). INSIDE the span
    # the delivered output grammar requires inline code for any mention, so
    # a bare `<!--` is an opener wherever it appears — closing the two
    # residual shapes (#613): a marker following text on its own line, and
    # a marker indented as a lazy paragraph continuation.
    span_inline = False
    # Code spans pair by equal-length runs ACROSS soft line breaks within a
    # paragraph, which a per-line blanker cannot see: a trailing unpaired
    # run on one line can pair into the next line and pull a `<!--` out of
    # (or into) code (#613 security round 1, P1). Once a span line leaves
    # an odd number of backtick runs, local blanking is untrustworthy for
    # the REST of that paragraph: stop blanking and read every `<!--` as an
    # opener — abort-direction, since the sanctioned mention is a
    # same-line inline-code span in a paragraph with balanced runs.
    code_parity_suspect = False
    for line, fenced in _lines_with_fence_state(text):
        entered_commented = commented
        entered_inline = span_inline
        opens_comment = not fenced and _opens_comment(
            line, paragraph_open=paragraph_open
        )
        if not fenced:
            # A block opener only, list and blockquote markers included:
            # four columns STARTING a block makes indented code, and a fence
            # makes every marker inert. Not read as an opener HERE: a marker
            # mid-line, one in an inline-code span, or one indented as a lazy
            # paragraph continuation — inside the dissent span those are the
            # #613 inline state's job, now that the output grammar makes a
            # bare marker out-of-grammar prose. #613 tracks, and leaves
            # OPEN, the wider hiding channel this visibility model does not
            # cover at all: raw HTML that is not a comment, such as a
            # `<script>` or `<template>` block — the shipped closure is the
            # comment channel only.
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
            span_inline = False
            code_parity_suspect = False
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
            if not line.strip(" \t"):
                # A blank line closes the paragraph, and with it any
                # cross-line code-span ambiguity.
                code_parity_suspect = False
            opens_inline = False
            blanked = None
            if (not fenced and not entered_commented and not entered_inline
                    and not opens_comment):
                # #613: only lines the block model does NOT already own can
                # open the inline state; code spans are blanked first so the
                # grammar's sanctioned `` `<!--` `` mention stays prose —
                # unless this paragraph's runs stopped pairing locally, in
                # which case blanking is off and every marker opens.
                escaped = _ESCAPED_BACKTICK_RE.sub("  ", line)
                blanked = (
                    escaped if code_parity_suspect
                    else _blank_code_spans(line)
                )
                opens_inline = "<!--" in blanked
                if len(re.findall(r"`+", escaped)) % 2:
                    code_parity_suspect = True
            # #682: any non-comment raw-HTML tag/delimiter in the dissent
            # span is out of grammar even when it hides no field.  Scan the
            # display form after inline-code blanking; fenced examples retain
            # their previous semantics, and the exact H2 boundaries above
            # keep the rule span-scoped.  Under cross-line code ambiguity we
            # take the same abort-direction as the #613 comment guard rather
            # than letting a malformed tag earn a dissent exemption.
            if not fenced:
                html_scan = (
                    _ESCAPED_BACKTICK_RE.sub("  ", line)
                    if code_parity_suspect
                    else _blank_code_spans(line)
                )
                if _DISSENT_RAW_HTML_RE.search(html_scan):
                    raw_html.append(line)
            # Opened up only where a comment actually is. Rewriting every line
            # carrying the tokens would break a canonical `rationale:` that
            # merely mentions them in inline code from matching the
            # canonical parse, aborting an unretryable Phase 2 on a valid
            # card.
            if (entered_commented or opens_comment or entered_inline
                    or opens_inline):
                span.append(line.replace("<!--", " ").replace("-->", " "))
            else:
                span.append(line)
            if entered_commented or entered_inline:
                hidden_by_comment.append(line)
            if not fenced and (entered_inline or opens_inline):
                span_inline = _inline_comment_state_after(
                    blanked if blanked is not None
                    else _blank_code_spans(line),
                    commented=entered_inline,
                )
    return DissentSpan(span, hidden_by_comment, raw_html)


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
    # §4 names three requirements, not one: the paraphrase section and the
    # terminal acknowledgement are as mandatory as the plan, and a plan
    # alone passing would let the dispatcher retry -- or accept -- a
    # protocol-invalid Phase 1.
    if "Contract Paraphrase" in dupes or "Contract Paraphrase" \
            not in sections:
        raise ConformanceError(
            f"[PHASE1-GRAMMAR: {path}: exactly one ## Contract Paraphrase "
            "required]"
        )
    # BOTH tails must be the marker. The raw tail catches output after
    # the acknowledgement (a trailing fenced block would vanish from the
    # structural view before the tail is computed); the fence-aware tail
    # catches an acknowledgement that exists only as fenced code.
    # Located by nonblankness but compared UNSTRIPPED (bar the line
    # ending): an indented `    [CONTRACT-ACKNOWLEDGED]` renders as a
    # code block, and stripping before comparison let it pass the exact
    # terminal-line requirement.
    raw_tail = next(
        (line for line in reversed(text.splitlines())
         if line.strip()), "")
    fenced_tail = next(
        (line for line in reversed(lines) if line.strip()), "")
    if raw_tail.rstrip() != "[CONTRACT-ACKNOWLEDGED]" or \
            fenced_tail.rstrip() != "[CONTRACT-ACKNOWLEDGED]":
        raise ConformanceError(
            f"[PHASE1-GRAMMAR: {path}: final nonblank line must be "
            "[CONTRACT-ACKNOWLEDGED]]"
        )
    # And in §4's exact order, with nothing else at H2: presence alone
    # would let a reordered or extra-sectioned precommitment pass. All
    # four real dispatch outputs carry exactly this sequence.
    h2_titles = [line[3:].strip() for line in lines
                 if line.startswith("## ")]
    if h2_titles != ["Contract Paraphrase", "Scoring Plan"]:
        raise ConformanceError(
            f"[PHASE1-GRAMMAR: {path}: H2 sections must be exactly "
            "## Contract Paraphrase then ## Scoring Plan, found "
            f"{h2_titles!r}]"
        )
    dimensions = {d["id"]: d for d in contract["acceptance_dimensions"]}
    # §4's paragraph floor: a bare heading over an empty or one-line body
    # is not the paraphrase the contract's `paraphrase_minimum_dimensions`
    # names ("all" = one paragraph per dimension). The count is the
    # machine-checkable lower bound; whether each paragraph is TIED to a
    # distinct dimension stays with the seat's own §4 preflight.
    # A CLOSED list of zero-content lines that separate and never count:
    # ATX headings, thematic breaks, single-line HTML comments -- six
    # bare `### Dn` headings (or six `---` rules) used to count as six
    # paragraphs, satisfying the floor with no paraphrase prose at all.
    # Deliberately NOT a full CommonMark block classifier: a list item
    # still counts, because a bulleted six-point paraphrase is real
    # content and refusing it would abort a panel over formatting (the
    # false-abort channel #609 exists to remove). Blocks are still
    # blank-line separated -- a TIGHT six-item list is one block and
    # does not meet a six-paragraph floor, same as before this list.
    # TERMINATION BOUND: zero-content variants beyond this list
    # (container-prefixed comments like `- <!-- -->`, malformed comments
    # like `<!-->`, entity/whitespace tricks) are out of scope by
    # declared design -- the variant space is unbounded, the observed
    # base rate in committed panels is zero, and §4's substantive
    # judgment sits with the seat's preflight, not this floor.
    separator = re.compile(
        r"#{1,6}(\s|$)"          # ATX heading
        r"|([-*_])(\s*\2){2,}$"  # thematic break
        r"|<!--.*-->$"           # single-line HTML comment
        r"|[-*+]$"               # lone list marker, no item text
    )
    paragraphs, in_paragraph, in_comment = 0, False, False
    for line in sections["Contract Paraphrase"]:
        stripped = line.strip()
        if in_comment:
            # Hidden until the closing `-->`, closer line included: six
            # multi-line comment blocks are as unrendered as six
            # single-line ones.
            if "-->" in stripped:
                in_comment = False
            in_paragraph = False
            continue
        if stripped.startswith("<!--") and "-->" not in stripped:
            # Conservative entry -- a line-LEADING opener with no closer
            # on the same line. Prose that merely mentions `<!--`
            # mid-line stays countable content.
            in_comment = True
            in_paragraph = False
            continue
        if stripped and not separator.match(stripped):
            if not in_paragraph:
                paragraphs += 1
                in_paragraph = True
        else:
            in_paragraph = False
    minimum = contract.get("measurement_procedure", {}).get(
        "paraphrase_minimum_dimensions")
    required = len(dimensions) if minimum == "all" else (
        minimum if isinstance(minimum, int) else 0)
    if paragraphs < required:
        raise ConformanceError(
            f"[PHASE1-GRAMMAR: {path}: Contract Paraphrase has "
            f"{paragraphs} paragraph(s), fewer than the {required} "
            "required]"
        )
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
    # Raw HTML owns its own diagnostic even when stripping the tag leaves a
    # field-shaped line.  Checking it first prevents a ``<span>dimension_id``
    # wrapper from being mislabeled as comment hiding by the older generic
    # raw-span occurrence guard.  Comment-only cards never populate this list
    # and retain the #613 ``[DISSENT-HIDDEN]`` path below.
    if span.raw_html:
        raise ConformanceError(
            "[DISSENT-RAW-HTML: raw HTML tags or delimiters are forbidden "
            "inside ## Scoring Plan Dissent; put markup mentions in inline "
            "code]"
        )
    if any(count > parsed[value] for value, count in hidden.items()):
        # Distinct marker (#613 security round 1, P3): these fields ARE
        # canonical — the failure is that comment markup hides them from
        # the rendered card, and pointing the operator at line grammar
        # misattributes an unretryable abort.
        raise ConformanceError(
            "[DISSENT-HIDDEN: a canonical dissent field is hidden from the "
            "rendered card by comment markup; write dissent fields in the "
            "clear and mention comment syntax only in inline code]"
        )
    if any(
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
        # A finding needs at least one parseable Severity declaration, and
        # every declaration must parse. When a card declares more than one
        # ACROSS lines and the chain strictly ESCALATES (Minor < Major <
        # Critical), the LAST in reading order is operative — the current
        # model generation self-corrects mid-card with explicit supersession
        # prose ("See the Severity line below, which supersedes the line
        # above", #637 ms01_quant r1: Major -> Critical), and Phase 2 permits
        # no retry for this class, so a strict exactly-one rule turns a
        # visible, reader-unambiguous correction into a whole-panel abort.
        # Every other multi-declaration shape keeps the loud abort:
        # de-escalation could waive the Critical/Major Evidence-Anchor
        # requirement by appending one weaker line; a non-monotone or
        # repeated-value chain signals several findings bundled under one W
        # heading (the one-finding-per-heading accounting feeds the severity
        # ladder); and two parseable declarations on ONE line are not a
        # reading-order correction at all. The advisory line below keeps the
        # full declaration trail in the gate log for adjudication.
        parseable_per_line = [
            sum(1 for _ in _SEVERITY_RE.finditer(line)) for line in block
        ]
        if (not severities or len(severities) != severity_declarations
                or any(count > 1 for count in parseable_per_line)):
            raise ConformanceError(
                f"[FINDING-GRAMMAR: {report.path}: {title} must contain "
                "exactly one parseable Severity declaration]"
            )
        severity_rank = {"Minor": 0, "Major": 1, "Critical": 2}
        if any(severity_rank[later] <= severity_rank[earlier]
               for earlier, later in zip(severities, severities[1:])):
            raise ConformanceError(
                f"[FINDING-GRAMMAR: {report.path}: {title}: multiple "
                "Severity declarations must form a strictly escalating "
                "self-correction chain]"
            )
        if len(severities) > 1:
            print(
                f"[SEVERITY-SUPERSEDED: {report.path}: {title}: "
                + " -> ".join(severities) + "]"
            )
        operative_severity = severities[-1]
        anchor_declarations = sum(
            len(_ANCHOR_DECL_RE.findall(line)) for line in block
        )
        anchors = [
            match.group("value") for line in block
            for match in _ANCHOR_RE.finditer(line)
        ]
        if operative_severity not in {"Critical", "Major"}:
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
                f"{operative_severity} finding needs exactly one "
                "Evidence Anchor]"
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


def _one_receipt_field(
    lines: list[str], key: str, path: str, receipt_id: str, *, required: bool
) -> str | None:
    hits = [
        match.group("value")
        for line in lines
        if (match := _RECEIPT_FIELD_RES[key].fullmatch(line))
    ]
    expected = "exactly one" if required else "at most one"
    if (required and len(hits) != 1) or (not required and len(hits) > 1):
        raise ConformanceError(
            f"[RECEIPT-GRAMMAR: {path}: {receipt_id} expected {expected} "
            f"canonical {key}: line, found {len(hits)}]"
        )
    return hits[0] if hits else None


def _review_body_receipt_backrefs(
    report: panel.ReviewerReport,
) -> tuple[set[str], dict[str, list[str]]]:
    """W-finding ids and per-block `**Arithmetic Receipt**:` back-references.

    Back-references are collected across the WHOLE Review Body — preamble and
    non-W subsections included — so a back-reference stranded outside its
    weakness block is a linkage failure, not invisible. The walk is
    fence-aware: only unfenced headings delimit (agreeing with
    `split_sections`), a fenced or decorated back-reference declaration is
    counted by the lenient detector, and a declaration count exceeding the
    canonical parse aborts — a back-reference the seat spelled but the
    grammar refused is a linkage failure, never a silent drop.
    """
    lines = panel.strip_fences(report.text)
    sections, _ = panel.split_sections(lines)
    review_lines = sections.get("Review Body", [])
    blocks, _ = panel.split_subsections(review_lines)
    finding_ids = {
        title.split(":", 1)[0]
        for title in blocks
        if _FINDING_H3_RE.fullmatch(title)
    }
    backrefs: dict[str, list[str]] = {}
    current = "(preamble)"
    inside = False
    inline_commented = False
    for line, fenced, hidden, code_indented in _lines_with_hidden_state(
        report.text
    ):
        if not fenced and (match := panel._H2_RE.fullmatch(line)):
            inside = match.group(1) == "Review Body"
            current = "(preamble)"
            inline_commented = False
            continue
        if not inside:
            continue
        parse_line = line
        if not fenced and not hidden and not code_indented:
            # A paragraph-inline comment span cannot cross a paragraph
            # boundary: a blank line or an interrupting ATX heading (any
            # level) ends the paragraph and with it the raw-HTML span, so
            # the state resets there instead of leaking a false abort into
            # later prose. Code spans are blanked first, matching the
            # renderer's precedence: a literal `<!--` inside inline code
            # opens nothing (#610 round-4).
            if (
                not line.strip(" \t")
                or _ATX_HEADING_RE.match(line)
            ):
                inline_commented = False
            else:
                code_blanked = _blank_code_spans(line)
                visible, hidden_segments, inline_commented = (
                    _strip_inline_comment_spans(
                        code_blanked, inline_commented
                    )
                )
                if visible != code_blanked:
                    # A declaration inside a hidden span aborts whether or
                    # not the line also shows visible content (#610 round
                    # 5): hidden prose is skippable, a hidden machine
                    # declaration never is. Each span is checked on its
                    # own (#610 round-6).
                    if any(
                        _backref_declared_count(segment)
                        for segment in hidden_segments
                    ):
                        raise ConformanceError(
                            f"[RECEIPT-LINKAGE: {report.path}: an "
                            "Arithmetic Receipt back-reference "
                            "declaration sits inside a paragraph-"
                            "inline HTML comment span and does not "
                            "render; it is non-conforming]"
                        )
                    if not visible.strip(" \t"):
                        continue
                    # Only the rendered remainder is parsed: content after
                    # a closing `-->` stays live, content behind an opener
                    # is gone.
                    parse_line = visible
        if fenced or hidden or code_indented:
            # Never credited: a machine declaration the page does not show
            # as a field line — fenced, commented, or rendered as indented
            # code — is a loud failure, not a silent drop or a silent
            # credit (#610 rounds 2-3).
            if _backref_declared_count(line):
                kind = (
                    "fenced" if fenced
                    else "commented-out" if hidden
                    else "indented-code"
                )
                raise ConformanceError(
                    f"[RECEIPT-LINKAGE: {report.path}: a {kind} Arithmetic "
                    "Receipt back-reference declaration does not render as "
                    "a field line and is non-conforming]"
                )
            continue
        if match := panel._H3_RE.fullmatch(line):
            title = match.group(1)
            current = (
                title.split(":", 1)[0]
                if _FINDING_H3_RE.fullmatch(title)
                else f"(non-finding: {title})"
            )
            continue
        # Canonical parsing and the declaration count run on the SAME
        # display form (#610 round-4 P1): parsing the raw line while
        # counting on a blanked one let a code-span declaration be
        # credited over the rendered field beside it.
        display = _cell_split_form(parse_line)
        matches = list(_RECEIPT_BACKREF_RE.finditer(display))
        if _backref_declared_count(display) != len(matches):
            raise ConformanceError(
                f"[RECEIPT-LINKAGE: {report.path}: back-reference "
                f"declaration(s) on {line.strip()!r} do not all parse "
                "canonically — each value must be exactly "
                "**Arithmetic Receipt**: AR<n> with no trailing text]"
            )
        for match in matches:
            backrefs.setdefault(current, []).append(match.group("value"))
    return finding_ids, backrefs


_INDENTED_H2_RE = re.compile(r"^ {1,3}##\s+\S")
# Any ATX heading interrupts a paragraph (CommonMark), so any level ends a
# paragraph-inline comment span — resetting only on H3 false-aborted a
# rendered backref after an interrupting H4 (#610 round-4).
_ATX_HEADING_RE = re.compile(r"^ {0,3}#{1,6}(?:[ \t]|$)")


def _receipt_section_view(
    text: str,
) -> tuple[list[tuple[str, bool]], list[str], bool]:
    """Receipt-section lines with visibility, the unfenced H2 order, and
    whether an indented H2 renders after the section opened.

    The section body is read through `_lines_with_hidden_state` rather than
    `strip_fences` (#610 rounds 1-2, the #637/#609 convergence): a model
    that fences its receipt block still WROTE the receipts, so the fenced
    lines are read as content — no false abort — while a fenced `### AR<n>`
    block sitting beside an unfenced attestation is SEEN and aborts as
    receipts-plus-attestation instead of hiding. Each content line carries
    its hidden flag so a machine line inside an HTML comment — which the
    rendered card does not show — can abort rather than be credited. Only
    an unfenced H2 delimits, agreeing with `split_sections` (a COMMENTED
    heading therefore still delimits, as in `_raw_dissent_span`), so a
    fenced heading can neither open nor close the section. The H2 title is
    matched exactly, case-sensitively, consistent with every other section
    grammar. A 1-3-space-indented `##` line is not a section to this
    grammar but still renders as a heading, so one appearing after the
    receipt section opens is reported for the terminal-section rule.
    """
    h2_titles: list[str] = []
    section: list[tuple[str, bool, bool]] = []
    inside = False
    indented_h2_after = False
    for line, fenced, hidden, _ in _lines_with_hidden_state(text):
        if not fenced and (match := panel._H2_RE.fullmatch(line)):
            h2_titles.append(match.group(1))
            inside = match.group(1) == _RECEIPT_SECTION
            continue
        if inside:
            if not fenced and not hidden and _INDENTED_H2_RE.match(line):
                indented_h2_after = True
            section.append((line, hidden, fenced))
    return section, h2_titles, indented_h2_after


def check_methodology_receipts(report: panel.ReviewerReport) -> None:
    """#610 arithmetic-receipt gate, methodology seat only.

    Auditability, not truth: this gate proves the receipt fields exist, use
    the closed enums, and link mismatches to weaknesses bidirectionally. It
    never attests that the arithmetic is correct — that judgment stays with
    human adjudication (`VERIFIED` / `MISCOMPUTED`), per the spec's invariant
    6 and the receipt block's leading epistemic-status note.
    """
    view, h2_titles, indented_h2_after = _receipt_section_view(report.text)
    occurrences = h2_titles.count(_RECEIPT_SECTION)
    if occurrences > 1:
        raise ConformanceError(
            f"[RECEIPT-GRAMMAR: {report.path}: duplicate "
            f"## {_RECEIPT_SECTION}]"
        )
    if occurrences == 0:
        raise ConformanceError(
            f"[RECEIPT-MISSING: {report.path}: methodology card requires "
            f"exactly one ## {_RECEIPT_SECTION} section]"
        )
    if h2_titles[-1] != _RECEIPT_SECTION or indented_h2_after:
        raise ConformanceError(
            f"[RECEIPT-GRAMMAR: {report.path}: ## {_RECEIPT_SECTION} must "
            "be the final section of the card]"
        )
    in_subsection = False
    for line, hidden, fenced in view:
        if not fenced and ("<!--" in line or "-->" in line):
            # Comment-free zone (#610 round-3 P1): the receipt section is
            # machine lines, so a paragraph-inline `prose <!--` opener —
            # which the block-position visibility model deliberately does
            # not read — could otherwise launder the receipts below it out
            # of the rendered card. Banning the markup outright is
            # deterministic and costs no legitimate content; fenced lines
            # render the markup literally and stay exempt.
            raise ConformanceError(
                f"[RECEIPT-GRAMMAR: {report.path}: HTML comment markup "
                f"{line.strip()!r} is not allowed in the receipt section]"
            )
        if panel._H3_RE.fullmatch(line):
            if hidden:
                raise ConformanceError(
                    f"[RECEIPT-GRAMMAR: {report.path}: receipt heading "
                    f"{line.strip()!r} is inside an HTML comment; the "
                    "rendered card does not show it]"
                )
            in_subsection = True
            continue
        canonical = bool(
            _RECEIPT_ATTESTATION_RE.fullmatch(line)
            or any(
                pattern.fullmatch(line)
                for pattern in _RECEIPT_FIELD_RES.values()
            )
        )
        if canonical:
            if hidden:
                raise ConformanceError(
                    f"[RECEIPT-GRAMMAR: {report.path}: receipt machine "
                    f"line {line.strip()!r} is inside an HTML comment; the "
                    "rendered card does not show it]"
                )
            if (
                not in_subsection
                and not _RECEIPT_ATTESTATION_RE.fullmatch(line)
            ):
                raise ConformanceError(
                    f"[RECEIPT-GRAMMAR: {report.path}: receipt machine "
                    f"line {line.strip()!r} sits outside every ### AR<n> "
                    "subsection; the enum and linkage gates never inspect "
                    "it there]"
                )
            continue
        if any(
            _is_receipt_field_shaped(candidate)
            for candidate in _receipt_shape_candidates(line)
        ):
            # One neutral message for both visibility states: an opener
            # line like `<!-- c --> key: value` is hidden to the model but
            # partially renders, so claiming "commented-out" would misread
            # the page to the seat (#610 round-3 P3).
            raise ConformanceError(
                f"[RECEIPT-GRAMMAR: {report.path}: receipt machine line "
                f"{line.strip()!r} is decorated or non-canonical; write "
                "plain unbulleted key: value text (tolerated: one "
                "leading list marker, balanced bold around the key)]"
            )
    body = [line for line, _, _ in view]
    attestations = [
        line for line in body if _RECEIPT_ATTESTATION_RE.fullmatch(line)
    ]
    subsections, sub_dupes = panel.split_subsections(body)
    if sub_dupes:
        raise ConformanceError(
            f"[RECEIPT-GRAMMAR: {report.path}: duplicate receipt heading(s) "
            f"{sorted(sub_dupes)}]"
        )
    for title in subsections:
        if not _RECEIPT_H3_RE.fullmatch(title):
            raise ConformanceError(
                f"[RECEIPT-GRAMMAR: {report.path}: invalid receipt "
                f"subsection '### {title}'; expected ### AR<n>]"
            )
    if not subsections:
        if len(attestations) != 1:
            raise ConformanceError(
                f"[RECEIPT-GRAMMAR: {report.path}: a receipt section with "
                "no ### AR<n> subsection requires exactly one "
                f"no_recomputable_statistics: line, found {len(attestations)}]"
            )
        # Honest-claim boundary (#610 round-1 fix 2): the gate proved only
        # that the declaration EXISTS. Whether the manuscript really has
        # nothing recomputable is judged at adjudication, so the pass is
        # annotated rather than silent.
        print(_RECEIPT_ATTESTATION_ADVISORY)
        return
    if attestations:
        raise ConformanceError(
            f"[RECEIPT-GRAMMAR: {report.path}: no_recomputable_statistics: "
            "is forbidden when ### AR<n> receipts exist]"
        )
    expected_ids = [f"AR{index}" for index in range(1, len(subsections) + 1)]
    if list(subsections) != expected_ids:
        raise ConformanceError(
            f"[RECEIPT-GRAMMAR: {report.path}: receipt IDs must be dense "
            f"AR1..ARn in order; got={list(subsections)}]"
        )
    finding_ids, backrefs = _review_body_receipt_backrefs(report)
    mismatch_refs: dict[str, str] = {}
    for receipt_id, sublines in subsections.items():
        procedure = _one_receipt_field(
            sublines, "procedure_id", report.path, receipt_id, required=True
        )
        if procedure not in _RECEIPT_PROCEDURES:
            raise ConformanceError(
                f"[RECEIPT-GRAMMAR: {report.path}: {receipt_id} "
                f"procedure_id '{procedure}' is not a bounded procedure]"
            )
        anchor = _one_receipt_field(
            sublines, "evidence_anchor", report.path, receipt_id,
            required=True,
        )
        _validate_anchor(anchor, f"{report.path}:{receipt_id}")
        for key in (
            "reported_inputs", "assumptions", "derivation",
            "comparison_rule",
        ):
            _one_receipt_field(
                sublines, key, report.path, receipt_id, required=True
            )
        derived = _one_receipt_field(
            sublines, "derived_value_or_range", report.path, receipt_id,
            required=True,
        )
        status = _one_receipt_field(
            sublines, "status", report.path, receipt_id, required=True
        )
        if status not in _RECEIPT_STATUSES:
            raise ConformanceError(
                f"[RECEIPT-GRAMMAR: {report.path}: {receipt_id} status "
                f"'{status}' is not in the closed status enum]"
            )
        reason = _one_receipt_field(
            sublines, "not_computable_reason", report.path, receipt_id,
            required=(status == "not_computable"),
        )
        if status != "not_computable" and reason is not None:
            raise ConformanceError(
                f"[RECEIPT-GRAMMAR: {report.path}: {receipt_id} "
                "not_computable_reason is forbidden unless status is "
                "not_computable]"
            )
        if reason is not None and reason not in _NOT_COMPUTABLE_REASONS:
            raise ConformanceError(
                f"[RECEIPT-GRAMMAR: {report.path}: {receipt_id} "
                f"not_computable_reason '{reason}' is not in the closed v1 "
                "enum]"
            )
        tail = None
        for key, procedures in _PROCEDURE_FIELD_OWNERS.items():
            if procedure in procedures:
                required = (
                    key in _ALWAYS_REQUIRED_PROCEDURE_FIELDS
                    or status in _RECEIPT_VERDICT_STATUSES
                )
                value = _one_receipt_field(
                    sublines, key, report.path, receipt_id, required=required
                )
                if key == "tail_convention":
                    tail = value
            else:
                if _one_receipt_field(
                    sublines, key, report.path, receipt_id, required=False
                ) is not None:
                    raise ConformanceError(
                        f"[RECEIPT-GRAMMAR: {report.path}: {receipt_id} "
                        f"{key} is forbidden for procedure {procedure}]"
                    )
        if procedure == "p_from_test_statistic":
            if tail is not None and tail not in _TAIL_CONVENTIONS:
                raise ConformanceError(
                    f"[RECEIPT-GRAMMAR: {report.path}: {receipt_id} "
                    f"tail_convention '{tail}' is not in the closed enum]"
                )
            if tail == "unstated" and status in _RECEIPT_VERDICT_STATUSES:
                derived_fold = unicodedata.normalize(
                    "NFKC", derived
                ).casefold()
                if not all(
                    _tail_value_shown(derived_fold, label_re)
                    for label_re in _TAIL_LABEL_RES.values()
                ):
                    raise ConformanceError(
                        f"[RECEIPT-TAILS: {report.path}: {receipt_id} "
                        "unstated tail requires derived_value_or_range to "
                        "show BOTH labeled VALUES — each of the two-tailed "
                        "and one-tailed labels sharing its own ;-segment "
                        "with its derived number, either order]"
                    )
        finding_ref = _one_receipt_field(
            sublines, "finding_ref", report.path, receipt_id,
            required=(status == "mismatch"),
        )
        if status != "mismatch":
            if finding_ref is not None:
                raise ConformanceError(
                    f"[RECEIPT-LINKAGE: {report.path}: {receipt_id} "
                    "finding_ref is forbidden unless status is mismatch]"
                )
            continue
        if not _FINDING_REF_VALUE_RE.fullmatch(finding_ref):
            raise ConformanceError(
                f"[RECEIPT-LINKAGE: {report.path}: {receipt_id} finding_ref "
                f"'{finding_ref}' must name one W<n> weakness]"
            )
        if finding_ref not in finding_ids:
            raise ConformanceError(
                f"[RECEIPT-LINKAGE: {report.path}: {receipt_id} finding_ref "
                f"{finding_ref} has no matching ### {finding_ref} weakness "
                "in ## Review Body]"
            )
        if finding_ref in mismatch_refs:
            raise ConformanceError(
                f"[RECEIPT-LINKAGE: {report.path}: {finding_ref} is claimed "
                f"by both {mismatch_refs[finding_ref]} and {receipt_id}; "
                "no two receipts share a finding_ref]"
            )
        mismatch_refs[finding_ref] = receipt_id
    for finding_id, receipt_id in mismatch_refs.items():
        if backrefs.get(finding_id) != [receipt_id]:
            raise ConformanceError(
                f"[RECEIPT-LINKAGE: {report.path}: weakness {finding_id} "
                "must carry exactly one **Arithmetic Receipt**: "
                f"{receipt_id} back-reference, found "
                f"{backrefs.get(finding_id, [])}]"
            )
    for location, values in backrefs.items():
        for value in values:
            if mismatch_refs.get(location) != value:
                raise ConformanceError(
                    f"[RECEIPT-LINKAGE: {report.path}: back-reference "
                    f"{value} in {location} does not correspond to a "
                    "mismatch receipt naming that weakness]"
                )


def check_recompute_extraction(path: str, text: str) -> None:
    """#610 step-5 extraction gate, methodology seat only.

    The isolated numeric input surface: the response must be exactly one
    ``## Recompute Extraction`` section of machine lines. The grammar
    authority is the calculator's own parser (`recompute_receipts`), so the
    gate and the consumer can never disagree about what an extraction says;
    this gate adds the response-level structure rules and the anchor-grammar
    check the calculator deliberately does not own.
    """
    lines = panel.strip_fences(text)
    sections, dupes = panel.split_sections(lines)
    if recompute.EXTRACTION_SECTION in dupes:
        raise ConformanceError(
            f"[EXTRACTION-GRAMMAR: {path}: duplicate "
            f"## {recompute.EXTRACTION_SECTION}]"
        )
    if recompute.EXTRACTION_SECTION not in sections:
        raise ConformanceError(
            f"[EXTRACTION-GRAMMAR: {path}: exactly one "
            f"## {recompute.EXTRACTION_SECTION} section is required]"
        )
    extra = [
        title for title in list(sections) + list(dupes)
        if title != recompute.EXTRACTION_SECTION
    ]
    if extra:
        raise ConformanceError(
            f"[EXTRACTION-GRAMMAR: {path}: the response may carry no "
            f"section other than ## {recompute.EXTRACTION_SECTION}; "
            f"found {extra}]"
        )
    preamble = []
    for line in lines:
        if panel._H2_RE.fullmatch(line):
            break
        preamble.append(line)
    if any(line.strip() for line in preamble):
        raise ConformanceError(
            f"[EXTRACTION-GRAMMAR: {path}: no content is allowed before "
            f"## {recompute.EXTRACTION_SECTION}]"
        )
    try:
        extraction = recompute.parse_extraction(text)
    except recompute.ExtractionError as exc:
        raise ConformanceError(
            f"[EXTRACTION-GRAMMAR: {path}: {exc}]"
        ) from exc
    for request in extraction.requests:
        _validate_anchor(
            request["evidence_anchor"], f"{path}:{request.rr_id}"
        )
    if extraction.attestation is not None:
        # Same declaration-only honesty boundary as the receipt attestation.
        print(_RECEIPT_ATTESTATION_ADVISORY)


def check_injected_receipts(
    report: panel.ReviewerReport, injected_text: str
) -> None:
    """#610 step-5 identity gate: the card's receipt section must be the
    dispatcher-injected receipts verbatim, plus only the canonical
    ``finding_ref:`` lines the mismatch receipts require.

    Runs AFTER `check_methodology_receipts`, so grammar, enum, linkage, and
    per-subsection `finding_ref` placement are already proven; this gate
    proves nothing else changed. The comparison ignores blank lines and
    reads the card fence-transparently — the same view the receipt gate
    uses — so a decorated or re-spelled injected line fails identity loudly
    rather than being silently re-read.
    """
    injected_lines = [
        line.rstrip("\r") for line in injected_text.split("\n")
    ]
    heading = f"## {recompute.RECEIPT_SECTION}"
    if not injected_lines or injected_lines[0] != heading:
        raise panel.ContractError(
            f"[INJECTED-RECEIPTS-INVALID: the injected file must begin "
            f"with {heading!r}]"
        )
    expected = [line for line in injected_lines[1:] if line.strip()]
    view, _, _ = _receipt_section_view(report.text)
    # Only the PLAIN spelling is the permitted addition (codex round 1,
    # P2-4): the receipt grammar tolerates a decorated finding_ref, but
    # under injection "add exactly one finding_ref: line" means the
    # undecorated canonical form — a bolded or bulleted spelling stays in
    # the comparison and fails identity loudly.
    plain_finding_ref = re.compile(r"^finding_ref: W[1-9]\d*$")
    actual = [
        line for line, _, _ in view
        if line.strip() and not plain_finding_ref.fullmatch(line)
    ]
    if actual != expected:
        divergence = next(
            (
                f"card={card!r} vs injected={wanted!r}"
                for card, wanted in zip(actual, expected)
                if card != wanted
            ),
            f"card has {len(actual)} content lines, injected has "
            f"{len(expected)}",
        )
        raise ConformanceError(
            f"[RECEIPT-IDENTITY: {report.path}: the ## "
            f"{recompute.RECEIPT_SECTION} section must reproduce the "
            "dispatcher-computed receipts verbatim, adding only "
            f"finding_ref: lines on mismatch receipts; first divergence: "
            f"{divergence}]"
        )


def check_receipt_section_forbidden(report: panel.ReviewerReport) -> None:
    # Declared boundary: this guard sees what `split_sections` sees, so a
    # fenced or indented `## Arithmetic Receipts` on a non-methodology seat
    # is an inert displayed block, not a section — it earns the seat
    # nothing (no consumer reads it) and is deliberately not chased here.
    lines = panel.strip_fences(report.text)
    sections, dupes = panel.split_sections(lines)
    if _RECEIPT_SECTION in sections or _RECEIPT_SECTION in dupes:
        raise ConformanceError(
            f"[RECEIPT-SECTION-FORBIDDEN: {report.path}: role "
            f"{report.role} may not emit ## {_RECEIPT_SECTION}; the #610 "
            "receipt gate is methodology-only]"
        )


def _parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--role", required=True)
    parser.add_argument("--phase1", required=True, type=Path)
    # The retry decision is taken while Phase 2 has not been requested yet, so
    # the gate has to be answerable on Phase 1 alone. Mirrors the
    # --synthesis / --layer1-only split in check_panel_synthesis.py.
    stage = parser.add_mutually_exclusive_group(required=True)
    stage.add_argument("--phase2", type=Path)
    stage.add_argument("--phase1-only", action="store_true")
    # #610 step 5: the methodology extraction call is its own gated stage,
    # answerable between Phase 1 and Phase 2 like --phase1-only is before
    # Phase 2.
    stage.add_argument("--extraction", type=Path)
    parser.add_argument("--injected-receipts", type=Path)
    parser.add_argument("--manuscript", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.injected_receipts is not None and args.phase2 is None:
        parser.error("--injected-receipts requires --phase2")
    return args


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
        phase2_text = (
            panel._read_text(args.phase2) if args.phase2 is not None
            else None
        )
        manuscript_text = panel._read_text(args.manuscript)
        try:
            metadata = json.loads(panel._read_text(args.metadata))
        except json.JSONDecodeError as exc:
            raise panel.ContractError(
                f"[METADATA-INVALID: {args.metadata}: {exc}]"
            ) from exc
        if args.phase1_only:
            # Blindness FIRST, before structural parsing: a response both
            # malformed and leaking would otherwise report only the grammar
            # failure, and the dispatcher would grant the retry a proven
            # leak must never receive. It is the half a retry must not be
            # granted in spite of.
            check_manuscript_leakage(
                phase1_text, manuscript_text, metadata, contract
            )
        plan = parse_phase1(str(args.phase1), phase1_text, contract, args.role)
        for warning in plan.warnings:
            print(warning)
        if args.phase1_only:
            print("PHASE1-CONFORMANCE: PASS")
            return EXIT_PASS
        if args.extraction is not None:
            # #610 step 5. The extraction call is methodology-only by
            # design: no other seat has an extraction stage to gate.
            if args.role != "methodology":
                raise panel.ContractError(
                    f"[ROLE-BINDING: --extraction is methodology-only, "
                    f"dispatched as {args.role}]"
                )
            check_manuscript_leakage(
                phase1_text, manuscript_text, metadata, contract
            )
            check_recompute_extraction(
                str(args.extraction), panel._read_text(args.extraction)
            )
            print("EXTRACTION-CONFORMANCE: PASS")
            return EXIT_PASS
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
        if report.role == "methodology":
            check_methodology_receipts(report)
            if args.injected_receipts is not None:
                check_injected_receipts(
                    report, panel._read_text(args.injected_receipts)
                )
                # A distinct witness line (security round 1, P2-5): the
                # evidence contract names this gate as contract content, so
                # a Phase 2 gated WITHOUT it must be distinguishable in the
                # preserved gate log.
                print("RECEIPT-IDENTITY: PASS")
        else:
            if args.injected_receipts is not None:
                raise panel.ContractError(
                    f"[ROLE-BINDING: --injected-receipts is "
                    f"methodology-only, dispatched as {args.role}]"
                )
            check_receipt_section_forbidden(report)
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
